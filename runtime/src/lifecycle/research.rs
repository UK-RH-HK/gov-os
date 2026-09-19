//! # Research lifecycle — research becomes evidence (Contract v3 J1, lines 596-605; framework §45; BC-P2-47)
//!
//! **Requirement.** Each governed research output records question/reason, method, sources/data, measurements,
//! uncertainty, conclusion, confidence and the decisions/tasks it influenced. "Unstructured research notes remain
//! reference only until transformed into a governed finding or decision."
//!
//! **State machine** (`research_state`, OS-written, T2-sealed):
//!
//! ```text
//! FRAMED (question [+ reason])  --update: method-->  IN_PROGRESS  --conclude: every J1 field-->  CONCLUDED
//!    \______________________________ withdraw _____________/
//!                                                                  WITHDRAWN (status RETIRED, HISTORICAL)
//! ```
//!
//! FRAMED and IN_PROGRESS research is held **reference-only** (`state_class: NARRATIVE`); only CONCLUDED research is
//! `EVIDENCE`. A research record written by hand is judged by the same rules: presented as evidence (its state class,
//! or the policy default `EVIDENCE`) it must be complete, or it is `INCOMPLETE` — reported by the schema
//! (`schema_invariants`, CIT execution) and by [`findings`], refused as a citation by [`super::require_citable`],
//! and held `NARRATIVE` for retrieval by [`super::indexed_state_class`].
//!
//! **Influence.** `influences` lists the decisions, gates, tasks and other governed records that rely on the research.
//! The OS maintains it ([`super::record_influence`], [`super::sync_influences`]); [`findings`] reports every
//! influenced record that is not recorded.
use super::{
    evidence_status, finding, influence_findings, influenced_by, is_current, present, push_history,
    refuse_os_owned, reliance_findings, stamp, validate_seal_save, Ctx, EvidenceStatus, Standing,
    EVIDENCE_CLAIM_CLASSES,
};
use crate::authority;
use crate::orchestration::control;
use crate::records::{new_record, Record, RecordStore};
use crate::{GovError, Project, Result};
use serde_json::{json, Map, Value};

/// The research lifecycle states.
pub const STATES: &[&str] = &["FRAMED", "IN_PROGRESS", "CONCLUDED", "WITHDRAWN"];

/// Contract v3 J1 fields as `(item, accepted fields)`; the item is present when any of its fields carries content.
/// "influenced decisions/tasks" is not here: it is an OS-maintained backlink, checked by [`findings`].
pub const J1_FIELDS: &[(&str, &[&str])] = &[
    ("question", &["question"]),
    ("reason", &["reason"]),
    ("method", &["method"]),
    ("sources/data", &["sources", "data"]),
    ("measurements", &["measurements"]),
    ("uncertainty", &["uncertainty"]),
    ("conclusion", &["conclusion"]),
    ("confidence", &["confidence"]),
];

/// The J1 items `r` does not record (a confidence must be a number in [0, 1]).
pub fn missing_fields(data: &Value) -> Vec<String> {
    let mut out = vec![];
    for (item, fields) in J1_FIELDS {
        let ok = if *item == "confidence" {
            data.get("confidence")
                .and_then(|v| v.as_f64())
                .map(|c| (0.0..=1.0).contains(&c))
                .unwrap_or(false)
        } else {
            fields.iter().any(|f| present(data.get(*f)))
        };
        if !ok {
            out.push(item.to_string());
        }
    }
    out
}

/// The lifecycle state: the OS-written `research_state`, or — for a record no gov operation wrote — CONCLUDED when
/// it is complete and IN_PROGRESS otherwise.
pub fn effective_state(r: &Record) -> String {
    let s = r.get("research_state");
    if !s.is_empty() {
        return s;
    }
    if missing_fields(&r.data).is_empty() {
        "CONCLUDED".into()
    } else {
        "IN_PROGRESS".into()
    }
}

/// The evidence standing of a research record.
pub fn status(ctx: &Ctx, r: &Record) -> EvidenceStatus {
    let state_class = ctx.state_class(r);
    let missing = missing_fields(&r.data);
    let state = effective_state(r);
    let mut reasons = vec![];
    let standing = if !is_current(r) {
        reasons.push(format!("lifecycle status {}", r.status()));
        Standing::NotCurrent
    } else if state == "WITHDRAWN" {
        reasons.push("withdrawn".into());
        Standing::NotCurrent
    } else if !EVIDENCE_CLAIM_CLASSES.contains(&state_class.as_str()) {
        reasons.push(format!(
            "held reference-only (state_class {state_class}, research_state {state})"
        ));
        Standing::ReferenceOnly
    } else if !missing.is_empty() {
        reasons.push(format!(
            "presented as {state_class} without every J1 field (Contract v3 J1; framework §45)"
        ));
        Standing::Incomplete
    } else if state != "CONCLUDED" {
        reasons.push(format!(
            "research_state {state}: unfinished research presented as {state_class}"
        ));
        Standing::Incomplete
    } else {
        Standing::Governed
    };
    EvidenceStatus {
        id: r.id(),
        rtype: r.rtype(),
        path: r.path.clone(),
        state,
        standing,
        state_class,
        missing,
        reasons,
    }
}

/// The research family of [`super::suite_findings`].
pub fn findings(ctx: &Ctx) -> Vec<Value> {
    let mut out = vec![];
    for r in ctx.store.of_type("research") {
        if r.id().is_empty() {
            continue;
        }
        let st = status(ctx, r);
        if st.standing == Standing::Incomplete {
            out.push(finding("medium", "RESEARCH_INCOMPLETE_EVIDENCE", r, format!(
                "{} is presented as {} but is not governed evidence: {}{} — complete it (`gov research conclude {}`) or hold it reference-only (state_class NARRATIVE)",
                r.id(), st.state_class,
                if st.missing.is_empty() { String::new() } else { format!("missing {} ", st.missing.join(", ")) },
                st.reasons.join("; "), r.id()
            )));
        }
        if is_current(r) && st.state_class == "AUTHORITATIVE" {
            out.push(finding("medium", "RESEARCH_PRESENTED_AS_AUTHORITY", r, format!(
                "{} is research presented as AUTHORITATIVE: research is evidence; a decision that adopts its conclusion is the authority (framework §45, Contract v3 W2)",
                r.id()
            )));
        }
        for s in r.list("sources").into_iter().chain(r.list("data")) {
            if crate::records::id_regex().is_match(&s) && ctx.store.get(&s).is_none() {
                out.push(finding(
                    "low",
                    "RESEARCH_SOURCE_UNKNOWN",
                    r,
                    format!(
                        "{} cites {s} as a source, which is not a governed record",
                        r.id()
                    ),
                ));
            }
        }
    }
    out.extend(reliance_findings(ctx, "research"));
    out.extend(influence_findings(ctx, "research"));
    out
}

// ------------------------------------------------------------------------------------------------ commands

fn obj(fields: Value) -> Result<Map<String, Value>> {
    match fields {
        Value::Object(m) => Ok(m),
        Value::Null => Ok(Map::new()),
        _ => Err(GovError::new(
            "USAGE",
            "--fields must be a JSON/YAML object",
        )),
    }
}

/// Every id-shaped reference a research record makes must name a governed record.
fn check_references(store: &RecordStore, o: &Map<String, Value>) -> Result<()> {
    let mut unknown = vec![];
    for k in ["data", "influences"] {
        for s in crate::util::str_list(&Value::Object(o.clone()), k) {
            if store.get(&s).is_none() {
                unknown.push(format!("{k}: {s}"));
            }
        }
    }
    for s in crate::util::str_list(&Value::Object(o.clone()), "sources") {
        if crate::records::id_regex().is_match(&s) && store.get(&s).is_none() {
            unknown.push(format!("sources: {s}"));
        }
    }
    if unknown.is_empty() {
        Ok(())
    } else {
        Err(GovError::new(
            "RESEARCH_REFERENCE_UNKNOWN",
            format!("research references that are not governed records: {unknown:?}"),
        )
        .with_details(json!({"unknown": unknown})))
    }
}

fn incomplete(id: &str, missing: &[String]) -> GovError {
    GovError::new(
        "RESEARCH_INCOMPLETE",
        format!("{id} cannot be concluded as governed evidence: it does not record {} (Contract v3 J1: question/reason, method, sources/data, measurements, uncertainty, conclusion, confidence). Supply them, or record it with --draft to hold it reference-only (NARRATIVE) until it is concluded.", missing.join(", ")),
    )
    .with_details(json!({"research": id, "missing": missing}))
}

fn load_research(store: &RecordStore, id: &str) -> Result<Record> {
    let r = store
        .get(id)
        .ok_or_else(|| GovError::new("RESEARCH_NOT_FOUND", format!("{id} not found")))?;
    if r.rtype() != "research" {
        return Err(GovError::new(
            "USAGE",
            format!("{id} is a {} record, not research", r.rtype()),
        ));
    }
    Ok(r.clone())
}

fn standing_of(p: &Project, id: &str) -> Value {
    let store = RecordStore::load(&p.root);
    let ctx = Ctx::new(p, &store);
    store
        .get(id)
        .and_then(|r| evidence_status(&ctx, r))
        .map(|s| s.to_value())
        .unwrap_or(Value::Null)
}

/// `gov research record`: record a research output. Complete research is recorded CONCLUDED as `EVIDENCE`; with
/// `draft` it is recorded FRAMED/IN_PROGRESS and held reference-only (`NARRATIVE`). Incomplete research without
/// `draft` is refused (`RESEARCH_INCOMPLETE`). `task` names the task the research was done for, recorded as influenced.
pub fn record(p: &Project, fields: Value, draft: bool, task: Option<&str>) -> Result<Value> {
    control::guard_write(p, "research record")?;
    authority::require(p, super::RECORD_AUTHORITY)?;
    refuse_os_owned(&fields, &[])?;
    let store = RecordStore::load(&p.root);
    let mut o = obj(fields)?;
    if let Some(t) = o.remove("type") {
        if t != "research" {
            return Err(GovError::new(
                "USAGE",
                "gov research record writes research records (type: research)",
            ));
        }
    }
    let id = o
        .remove("id")
        .and_then(|v| v.as_str().map(String::from))
        .unwrap_or_else(|| store.next_id("research"));
    if !crate::records::id_regex().is_match(&id) {
        return Err(GovError::new("USAGE", format!("'{id}' is not a record id")));
    }
    if store.get(&id).is_some() {
        return Err(GovError::new(
            "DUPLICATE_ID",
            format!("{id} already exists"),
        ));
    }
    let status = o
        .get("status")
        .and_then(|v| v.as_str())
        .unwrap_or("ACTIVE")
        .to_string();
    if !super::CURRENT_STATUSES.contains(&status.as_str()) {
        return Err(GovError::new(
            "USAGE",
            format!("new research is recorded ACTIVE or PROVISIONAL, not {status}"),
        ));
    }
    let sc = o
        .get("state_class")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    if draft && !sc.is_empty() && sc != "NARRATIVE" {
        return Err(GovError::new("RESEARCH_DRAFT_NOT_EVIDENCE", format!("a draft (FRAMED/IN_PROGRESS) research record is held reference-only; state_class '{sc}' is not allowed (framework §45)")));
    }
    if !draft && !sc.is_empty() && sc != "EVIDENCE" {
        return Err(GovError::new("USAGE", format!("a concluded research record is EVIDENCE (state_class '{sc}' is not allowed); record it with --draft to hold it reference-only")));
    }
    if let Some(t) = task {
        match store.get(t) {
            Some(tr) if tr.rtype() == "task" => {
                let mut infl = crate::util::str_list(&Value::Object(o.clone()), "influences");
                if !infl.iter().any(|x| x == t) {
                    infl.push(t.to_string());
                }
                o.insert("influences".into(), json!(infl));
            }
            _ => {
                return Err(GovError::new(
                    "TASK_NOT_FOUND",
                    format!("--task {t} is not a task"),
                ))
            }
        }
    }
    check_references(&store, &o)?;
    if !present(o.get("question")) {
        return Err(incomplete(&id, &["question".into()]));
    }
    let missing = missing_fields(&Value::Object(o.clone()));
    if !draft && !missing.is_empty() {
        return Err(incomplete(&id, &missing));
    }
    let title = o
        .remove("title")
        .and_then(|v| v.as_str().map(String::from))
        .unwrap_or_else(|| o["question"].as_str().unwrap_or("research").to_string());
    o.entry("influences").or_insert(json!([]));
    let mut rec = new_record("research", &id, &title, Value::Object(o));
    let state = if !draft {
        "CONCLUDED"
    } else if present(rec.data.get("method")) {
        "IN_PROGRESS"
    } else {
        "FRAMED"
    };
    rec.set("research_state", json!(state));
    rec.set(
        "state_class",
        json!(if draft { "NARRATIVE" } else { "EVIDENCE" }),
    );
    rec.set("recorded_by", stamp(p, "research record"));
    if !draft {
        rec.set("concluded_by", stamp(p, "research record"));
    }
    push_history(&mut rec, p, state, "research record");
    validate_seal_save(p, &mut rec, "research record")?;
    Ok(json!({"research": rec.data, "standing": standing_of(p, &id)}))
}

/// Mutable while unfinished: `gov research update` merges fields into a FRAMED/IN_PROGRESS record (FRAMED becomes
/// IN_PROGRESS once a method is recorded). A record no gov operation wrote and that is not complete is taken into
/// the lifecycle here as reference-only. Concluded research is never edited in place: new research supersedes it.
pub fn update(p: &Project, id: &str, fields: Value) -> Result<Value> {
    control::guard_write(p, "research update")?;
    authority::require(p, super::RECORD_AUTHORITY)?;
    refuse_os_owned(&fields, &[])?;
    let store = RecordStore::load(&p.root);
    let mut rec = load_research(&store, id)?;
    let state = effective_state(&rec);
    if !matches!(state.as_str(), "FRAMED" | "IN_PROGRESS") {
        return Err(GovError::new("RESEARCH_TRANSITION_INVALID", format!("{id} is {state}; only FRAMED/IN_PROGRESS research is updated in place (concluded research is superseded by new research: `supersedes: [{id}]`)")));
    }
    let o = obj(fields)?;
    for k in ["id", "type"] {
        if o.contains_key(k) {
            return Err(GovError::new(
                "USAGE",
                format!("'{k}' of an existing record cannot change"),
            ));
        }
    }
    if let Some(sc) = o.get("state_class").and_then(|v| v.as_str()) {
        if sc != "NARRATIVE" {
            return Err(GovError::new("RESEARCH_DRAFT_NOT_EVIDENCE", format!("unfinished research is held reference-only; state_class '{sc}' is reached only by `gov research conclude {id}`")));
        }
    }
    check_references(&store, &o)?;
    for (k, v) in o {
        rec.set(&k, v);
    }
    let next = if present(rec.data.get("method")) {
        "IN_PROGRESS"
    } else {
        "FRAMED"
    };
    rec.set("research_state", json!(next));
    rec.set("state_class", json!("NARRATIVE"));
    if rec.data.get("recorded_by").is_none() {
        rec.set("recorded_by", stamp(p, "research update"));
    }
    push_history(&mut rec, p, next, "research update");
    validate_seal_save(p, &mut rec, "research update")?;
    Ok(json!({"research": rec.data, "standing": standing_of(p, id)}))
}

/// `gov research conclude`: FRAMED/IN_PROGRESS → CONCLUDED. Every J1 field must be recorded; the research becomes
/// `EVIDENCE`.
pub fn conclude(p: &Project, id: &str, fields: Value) -> Result<Value> {
    control::guard_write(p, "research conclude")?;
    authority::require(p, super::RECORD_AUTHORITY)?;
    refuse_os_owned(&fields, &[])?;
    let store = RecordStore::load(&p.root);
    let mut rec = load_research(&store, id)?;
    let state = effective_state(&rec);
    if !matches!(state.as_str(), "FRAMED" | "IN_PROGRESS") {
        return Err(GovError::new(
            "RESEARCH_TRANSITION_INVALID",
            format!("{id} is {state}; only FRAMED/IN_PROGRESS research is concluded"),
        ));
    }
    let o = obj(fields)?;
    for k in ["id", "type", "state_class"] {
        if o.contains_key(k) {
            return Err(GovError::new(
                "USAGE",
                format!("'{k}' is not set by conclude"),
            ));
        }
    }
    check_references(&store, &o)?;
    for (k, v) in o {
        rec.set(&k, v);
    }
    let missing = missing_fields(&rec.data);
    if !missing.is_empty() {
        return Err(incomplete(id, &missing));
    }
    rec.set("research_state", json!("CONCLUDED"));
    rec.set("state_class", json!("EVIDENCE"));
    if !super::CURRENT_STATUSES.contains(&rec.status().as_str()) {
        rec.set("status", json!("ACTIVE"));
    }
    if rec.data.get("influences").is_none() {
        rec.set("influences", json!([]));
    }
    rec.set("concluded_by", stamp(p, "research conclude"));
    push_history(&mut rec, p, "CONCLUDED", "research conclude");
    validate_seal_save(p, &mut rec, "research conclude")?;
    Ok(json!({"research": rec.data, "standing": standing_of(p, id)}))
}

/// `gov research withdraw`: FRAMED/IN_PROGRESS → WITHDRAWN (status RETIRED, state_class HISTORICAL).
pub fn withdraw(p: &Project, id: &str, reason: &str) -> Result<Value> {
    control::guard_write(p, "research withdraw")?;
    authority::require(p, super::RECORD_AUTHORITY)?;
    if reason.trim().is_empty() {
        return Err(GovError::new("USAGE", "a withdrawal records its --reason"));
    }
    let store = RecordStore::load(&p.root);
    let mut rec = load_research(&store, id)?;
    let state = effective_state(&rec);
    if !matches!(state.as_str(), "FRAMED" | "IN_PROGRESS") {
        return Err(GovError::new("RESEARCH_TRANSITION_INVALID", format!("{id} is {state}; only unfinished research is withdrawn (concluded research is superseded)")));
    }
    rec.set("research_state", json!("WITHDRAWN"));
    rec.set("state_class", json!("HISTORICAL"));
    rec.set("status", json!("RETIRED"));
    rec.set("withdrawn_reason", json!(reason));
    push_history(&mut rec, p, "WITHDRAWN", "research withdraw");
    validate_seal_save(p, &mut rec, "research withdraw")?;
    Ok(json!({"research": rec.data, "standing": standing_of(p, id)}))
}

/// `gov research show`: the record, its standing, its recorded and derived influences, its T2 binding and identity.
pub fn show(p: &Project, id: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let rec = load_research(&store, id)?;
    let ctx = Ctx::new(p, &store);
    let st = status(&ctx, &rec);
    let derived = influenced_by(&store, id);
    let recorded = rec.list("influences");
    let not_recorded: Vec<&String> = derived.iter().filter(|x| !recorded.contains(x)).collect();
    Ok(json!({"research": rec.data, "standing": st.to_value(),
        "influences": {"recorded": recorded, "derived": derived, "not_recorded": not_recorded},
        "t2": crate::t2::verify_record(&rec).to_value(),
        "identity": crate::graph::identity::identity(p, &store, id).unwrap_or(Value::Null)}))
}

/// `gov research check`: the standing of every research record and the research findings.
pub fn check(p: &Project) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let ctx = Ctx::new(p, &store);
    let f = findings(&ctx);
    Ok(
        json!({"family": super::FAMILY, "research": super::standings(&ctx, "research"), "findings": f, "ok": f.is_empty()}),
    )
}

#[cfg(test)]
mod tests {
    use super::super::testkit::*;
    use super::*;

    fn complete() -> Value {
        json!({"id": "RES-0001", "type": "research", "status": "ACTIVE", "question": "Is X faster?", "reason": "choose a gateway",
            "method": "A/B on staging", "sources": ["staging traffic 2026-09"], "measurements": {"p95_ms": [40, 18]},
            "uncertainty": "one day of traffic", "conclusion": "X is faster", "confidence": 0.7})
    }

    #[test]
    fn j1_completeness_decides_evidence_standing() {
        let fx = Fx::new("res");
        fx.put("spec/research/RES-0001.yaml", complete());
        fx.put("spec/research/RES-0100.yaml", json!({"id": "RES-0100", "type": "research", "status": "ACTIVE", "question": "Is X faster?", "conclusion": "Yes", "state_class": "EVIDENCE"}));
        fx.put(
            "spec/research/RES-0102.yaml",
            json!({"id": "RES-0102", "type": "research", "status": "ACTIVE", "question": "Shard?"}),
        );
        fx.put("spec/research/RES-0103.yaml", json!({"id": "RES-0103", "type": "research", "status": "ACTIVE", "question": "Shard?", "state_class": "NARRATIVE"}));
        fx.put("spec/research/RES-0104.yaml", {
            let mut v = complete();
            v["id"] = json!("RES-0104");
            v["confidence"] = json!(7);
            v
        });
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &[]);
        let st = |id: &str| status(&c, s.get(id).unwrap());
        assert_eq!(st("RES-0001").standing, Standing::Governed);
        let inc = st("RES-0100");
        assert_eq!(inc.standing, Standing::Incomplete);
        assert_eq!(
            inc.missing,
            vec![
                "reason",
                "method",
                "sources/data",
                "measurements",
                "uncertainty",
                "confidence"
            ]
        );
        assert_eq!(
            st("RES-0102").standing,
            Standing::Incomplete,
            "no state_class = the policy default EVIDENCE: presented as evidence"
        );
        assert_eq!(st("RES-0103").standing, Standing::ReferenceOnly);
        assert_eq!(
            st("RES-0104").missing,
            vec!["confidence"],
            "a confidence outside [0, 1] is not a confidence"
        );
        // retrieval standing: incomplete evidence is held reference-only, governed evidence keeps EVIDENCE
        assert_eq!(
            super::super::indexed_state_class(&c, s.get("RES-0100").unwrap()),
            "NARRATIVE"
        );
        assert_eq!(
            super::super::indexed_state_class(&c, s.get("RES-0001").unwrap()),
            "EVIDENCE"
        );
        // citation: governed evidence may be cited, incomplete may not
        assert!(super::super::require_citable_in(&c, &["RES-0001".into()]).is_ok());
        let e = super::super::require_citable_in(&c, &["RES-0001".into(), "RES-0102".into()])
            .unwrap_err();
        assert_eq!(e.code, "EVIDENCE_NOT_CITABLE");
        assert!(e.message.contains("RES-0102"));
    }

    #[test]
    fn findings_name_incomplete_evidence_unsupported_decisions_and_missing_backlinks() {
        let fx = Fx::new("resf");
        fx.put("spec/research/RES-0001.yaml", complete());
        fx.put("spec/research/RES-0101.yaml", json!({"id": "RES-0101", "type": "research", "status": "ACTIVE", "question": "Does caching help?", "conclusion": "Caching halves latency.", "state_class": "EVIDENCE"}));
        fx.put("spec/decisions/HDG-0002.yaml", json!({"id": "HDG-0002", "type": "human-gate", "status": "ACTIVE", "gate_status": "ANSWERED", "question": "Adopt caching?", "derived_from": ["RES-0101"]}));
        fx.put("spec/decisions/D-0003.yaml", json!({"id": "D-0003", "type": "decision", "status": "ACTIVE", "derived_from": ["HDG-0002"]}));
        fx.put("spec/decisions/D-0004.yaml", json!({"id": "D-0004", "type": "decision", "status": "ACTIVE", "derived_from": ["RES-0001"]}));
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &[]);
        let f = findings(&c);
        let codes = |id: &str| -> Vec<String> {
            f.iter()
                .filter(|x| x["record"] == id)
                .map(|x| x["code"].as_str().unwrap().to_string())
                .collect()
        };
        assert!(codes("RES-0101").contains(&"RESEARCH_INCOMPLETE_EVIDENCE".to_string()));
        assert!(codes("D-0003").contains(&"RELIES_ON_UNGOVERNED_EVIDENCE".to_string()));
        assert!(codes("HDG-0002").contains(&"RELIES_ON_UNGOVERNED_EVIDENCE".to_string()));
        assert!(
            codes("D-0004").is_empty(),
            "a decision on governed research is not a finding"
        );
        assert!(codes("RES-0001").contains(&"INFLUENCE_NOT_RECORDED".to_string()));
        let sev = f.iter().find(|x| x["record"] == "D-0003").unwrap()["severity"].clone();
        assert_eq!(sev, "high");
    }
}
