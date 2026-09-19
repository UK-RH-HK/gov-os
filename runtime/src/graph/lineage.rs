//! Record-level lineage over the governed records themselves (no index required): canonical edges, declared vs
//! actual consumers, and stale lineage links (Contract v3 W1 line 1078, W7 lines 1139-1144, W8 lines 1147-1152).
//!
//! These are pure functions of the record store, so they hold even when the derived index is absent or damaged
//! (INV-010). They are the queries a full-audit lineage/orphan family runs (integration point: `verification::run`,
//! owned by WS-2) and what `gov artefact check` reports.
use crate::records::{Record, RecordStore};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

/// Lifecycle statuses that are not current: a link from current work to such a record is stale.
pub const NON_CURRENT_STATUSES: &[&str] = &[
    "SUPERSEDED",
    "HISTORICAL",
    "DEPRECATED",
    "RETIRED",
    "REJECTED",
    "LEGACY",
];

fn archived(r: &Record) -> bool {
    r.problems.iter().any(|p| p == "archived")
}

/// `superseded id -> successor id`, from every record's `supersedes` list and every record's own `superseded_by`.
pub fn successor_map(store: &RecordStore) -> BTreeMap<String, String> {
    let mut m = BTreeMap::new();
    for r in &store.records {
        if archived(r) {
            continue;
        }
        for s in r.list("supersedes") {
            m.entry(s).or_insert_with(|| r.id());
        }
    }
    for r in &store.records {
        if archived(r) {
            continue;
        }
        let sb = r.get("superseded_by");
        if !sb.is_empty() {
            m.entry(r.id()).or_insert(sb);
        }
    }
    m
}

/// Every canonical edge declared by the (non-archived) governed records: `(source, type, destination, declared_by)`.
pub fn record_edges(store: &RecordStore) -> Vec<(String, String, String, String)> {
    let mut out = vec![];
    for r in &store.records {
        if archived(r) || r.id().is_empty() {
            continue;
        }
        for (s, t, d) in r.edges() {
            out.push((s, t, d, r.id()));
        }
    }
    out.sort();
    out.dedup();
    out
}

/// Records that consume `id` (declared manifest inputs, receipts, `consumers` fields), by canonical `CONSUMES`
/// edges: the **actual** consumers of an output (W7 line 1139).
pub fn consumers_of(store: &RecordStore, id: &str) -> Vec<String> {
    let mut out: BTreeSet<String> = BTreeSet::new();
    for (s, t, d, _) in record_edges(store) {
        if t == "CONSUMES" && d == id {
            out.insert(s);
        }
    }
    out.into_iter().collect()
}

/// Is `r` itself current work whose links matter? Superseded/historical records and cancelled tasks are not.
fn is_current(r: &Record) -> bool {
    !archived(r)
        && !NON_CURRENT_STATUSES.contains(&r.status().as_str())
        && r.get("task_status") != "CANCELLED"
}

/// Change-Impact Transaction states in which the transaction is finished: its links (the records it changed or
/// superseded, the gate and decision that approved or declined it) record what it did, not what anything relies on
/// now.
pub const FINISHED_CIT_STATES: &[&str] = &["COMMITTED", "ROLLED_BACK", "REJECTED"];

/// Is `r` a finished Change-Impact Transaction (see [`FINISHED_CIT_STATES`])?
pub fn finished_transaction(r: &Record) -> bool {
    r.rtype() == "cit" && FINISHED_CIT_STATES.contains(&r.get("cit_status").as_str())
}

/// **Stale lineage links** (W8 line 1151): a current record whose relation points at a record that is not current
/// — superseded (by status or by a successor), historical, deprecated, retired, rejected or legacy. Supersession
/// edges themselves are not stale links (they are how currency is expressed), and neither are the links of a
/// finished Change-Impact Transaction ([`finished_transaction`]; WS-2 R3-2): a committed CIT that superseded a
/// requirement, or a rolled-back one whose approval decision is now REJECTED, links to those records as history.
pub fn stale_links(store: &RecordStore) -> Vec<Value> {
    let succ = successor_map(store);
    let mut out = vec![];
    for r in &store.records {
        if !is_current(r) || r.id().is_empty() || finished_transaction(r) {
            continue;
        }
        let me = r.id();
        for (s, t, d) in r.edges() {
            if t == "SUPERSEDES" {
                continue;
            }
            // the record at the other end of the edge from this record
            let other = if s == me { d.clone() } else { s.clone() };
            if other.starts_with("file:") {
                continue;
            }
            let Some(o) = store.get(&other) else { continue };
            let status = o.status();
            let successor = succ.get(&other).cloned();
            if NON_CURRENT_STATUSES.contains(&status.as_str()) || successor.is_some() {
                out.push(json!({"record": me, "record_type": r.rtype(), "edge": {"src": s, "type": t, "dst": d},
                    "stale_target": other, "target_status": status, "superseded_by": successor, "path": r.path,
                    "message": format!("{me} is linked ({t}) to {other}, which is {}{}", status, successor.as_ref().map(|x| format!(" and superseded by {x}")).unwrap_or_default())}));
            }
        }
    }
    out
}

/// Outputs that declare expected consumers (`consumers:`) of which none actually consumes them (W7 line 1139);
/// and declared consumers that do not exist.
pub fn unconsumed_outputs(store: &RecordStore) -> Vec<Value> {
    let edges = record_edges(store);
    let mut out = vec![];
    for r in &store.records {
        if !is_current(r) {
            continue;
        }
        let expected = r.list("consumers");
        if expected.is_empty() {
            continue;
        }
        let id = r.id();
        let actual: BTreeSet<String> = edges
            .iter()
            .filter(|(s, t, d, by)| t == "CONSUMES" && d == &id && by != &id && s != &id)
            .map(|(s, _, _, _)| s.clone())
            .collect();
        let missing: Vec<&String> = expected.iter().filter(|c| store.get(c).is_none()).collect();
        if actual.is_empty() || !missing.is_empty() {
            out.push(json!({"record": id, "expected_consumers": expected, "actual_consumers": actual, "missing_consumers": missing, "path": r.path}));
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::records::parse_record_text;

    fn rec(yaml: &str, path: &str) -> Record {
        parse_record_text(yaml, path).unwrap()
    }

    fn store(recs: Vec<Record>) -> RecordStore {
        let mut by_id = BTreeMap::new();
        for (i, r) in recs.iter().enumerate() {
            by_id.insert(r.id(), i);
        }
        RecordStore {
            records: recs,
            by_id,
            duplicates: vec![],
            problems: vec![],
        }
    }

    #[test]
    fn every_relation_field_reads_in_the_direction_of_its_meaning() {
        let api = rec("id: API-0001\ntype: interface\nstatus: ACTIVE\nconsumers: [TASK-0001]\nproducers: [TASK-0000]\n", "spec/interfaces/API-0001.yaml");
        let e = api.edges();
        assert!(
            e.contains(&("TASK-0001".into(), "CONSUMES".into(), "API-0001".into())),
            "{e:?}"
        );
        assert!(
            e.contains(&("TASK-0000".into(), "PRODUCES".into(), "API-0001".into())),
            "{e:?}"
        );
        assert!(api
            .relations()
            .contains(&("CONSUMED_BY".into(), "TASK-0001".into())));
        let rpt = rec("id: RPT-0001\ntype: report\nstatus: ACTIVE\ntask: TASK-0001\nfiles_changed: [src/lib.rs]\nrequirements_implemented: [REQ-0001]\ninputs_consumed: ['REQ-0001@0123456789ab']\nacceptance_evidence: [{test: TST-0001, result: passed}]\n", "spec/reports/RPT-0001.yaml");
        let e = rpt.edges();
        for want in [
            ("TASK-0001", "PRODUCES", "RPT-0001"),
            ("RPT-0001", "PRODUCES", "file:src/lib.rs"),
            ("RPT-0001", "IMPLEMENTS", "REQ-0001"),
            ("RPT-0001", "CONSUMES", "REQ-0001"),
            ("RPT-0001", "VALIDATED_BY", "TST-0001"),
        ] {
            assert!(
                e.contains(&(want.0.into(), want.1.into(), want.2.into())),
                "missing {want:?} in {e:?}"
            );
        }
        // a checkpoint's working-tree snapshot is not an output of the checkpoint
        let ck = rec("id: CKPT-00001\ntype: checkpoint\nstatus: ACTIVE\ntask: TASK-0001\nfiles_changed: [src/lib.rs]\n", "spec/reports/checkpoints/CKPT-00001.yaml");
        assert!(!ck.edges().iter().any(|(_, _, d)| d.starts_with("file:")));
        let t = rec("id: TASK-0001\ntype: task\nstatus: ACTIVE\nhuman_gate: HDG-0001\nrequired_data: [DATA-0001]\nacceptance_tests: [TST-0002]\nrelations: [{type: GOVERNED_BY, target: REQ-0009, note: why}]\nrequired_inputs: [{id: REQ-0005, reason: r}]\n", "spec/tasks/TASK-0001.yaml");
        let e = t.edges();
        for want in [
            ("HDG-0001", "BLOCKS", "TASK-0001"),
            ("TASK-0001", "CONSUMES", "DATA-0001"),
            ("TASK-0001", "CONSUMES", "TST-0002"),
            ("TASK-0001", "VALIDATED_BY", "TST-0002"),
            ("TASK-0001", "CONSUMES", "REQ-0009"),
            ("TASK-0001", "CONSUMES", "REQ-0005"),
        ] {
            assert!(
                e.contains(&(want.0.into(), want.1.into(), want.2.into())),
                "missing {want:?} in {e:?}"
            );
        }
        let res = rec(
            "id: RES-0001\ntype: research\nstatus: ACTIVE\ninfluences: [D-0001]\n",
            "spec/research/RES-0001.yaml",
        );
        assert!(res
            .edges()
            .contains(&("RES-0001".into(), "AFFECTS".into(), "D-0001".into())));
        let old = rec(
            "id: REQ-0001\ntype: requirement\nstatus: SUPERSEDED\nsuperseded_by: REQ-0002\n",
            "spec/requirements/REQ-0001.yaml",
        );
        assert!(old
            .edges()
            .contains(&("REQ-0002".into(), "SUPERSEDES".into(), "REQ-0001".into())));
    }

    #[test]
    fn stale_links_and_unconsumed_outputs_are_named() {
        let s = store(vec![
            rec("id: REQ-0009\ntype: requirement\nstatus: SUPERSEDED\nsuperseded_by: REQ-0001\n", "spec/requirements/REQ-0009.yaml"),
            rec("id: REQ-0001\ntype: requirement\nstatus: ACTIVE\nsupersedes: [REQ-0009]\n", "spec/requirements/REQ-0001.yaml"),
            rec("id: TASK-0003\ntype: task\nstatus: ACTIVE\ntask_status: READY\nrequirements: [REQ-0009]\n", "spec/tasks/TASK-0003.yaml"),
            rec("id: DATA-0001\ntype: data\nstatus: ACTIVE\nconsumers: [TASK-0404]\n", "spec/data/DATA-0001.yaml"),
        ]);
        let st = stale_links(&s);
        assert!(
            st.iter()
                .any(|x| x["record"] == "TASK-0003" && x["stale_target"] == "REQ-0009"),
            "{st:?}"
        );
        assert!(
            !st.iter().any(|x| x["record"] == "REQ-0001"),
            "a supersession edge is not a stale link: {st:?}"
        );
        let un = unconsumed_outputs(&s);
        assert!(un.iter().any(|x| x["record"] == "DATA-0001"), "{un:?}");
        assert_eq!(consumers_of(&s, "REQ-0009"), vec!["TASK-0003".to_string()]);
    }

    #[test]
    fn a_finished_transactions_links_are_history_not_stale_links() {
        let s = store(vec![
            rec("id: REQ-0009\ntype: requirement\nstatus: SUPERSEDED\nsuperseded_by: REQ-0001\n", "spec/requirements/REQ-0009.yaml"),
            rec("id: REQ-0001\ntype: requirement\nstatus: ACTIVE\nsupersedes: [REQ-0009]\n", "spec/requirements/REQ-0001.yaml"),
            rec("id: D-0007\ntype: decision\nstatus: REJECTED\nrollback_of: CIT-0002\n", "spec/decisions/D-0007.yaml"),
            // the transaction that superseded REQ-0009 and the rolled-back one whose approval is now REJECTED
            rec("id: CIT-0001\ntype: cit\nstatus: ACTIVE\ncit_status: COMMITTED\ntargets: [REQ-0009]\n", "spec/decisions/CIT-0001.yaml"),
            rec("id: CIT-0002\ntype: cit\nstatus: ACTIVE\ncit_status: ROLLED_BACK\ntargets: [REQ-0009]\ndecision: D-0007\n", "spec/decisions/CIT-0002.yaml"),
            // an open transaction still relies on what it targets
            rec("id: CIT-0003\ntype: cit\nstatus: ACTIVE\ncit_status: SIMULATED\ntargets: [REQ-0009]\n", "spec/decisions/CIT-0003.yaml"),
        ]);
        let st = stale_links(&s);
        let from: Vec<&str> = st.iter().filter_map(|x| x["record"].as_str()).collect();
        assert!(
            !from.contains(&"CIT-0001") && !from.contains(&"CIT-0002"),
            "{st:?}"
        );
        assert!(from.contains(&"CIT-0003"), "{st:?}");
    }
}
