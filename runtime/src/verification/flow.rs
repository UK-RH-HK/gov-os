//! **W11 — artifact-flow quantitative health** (Contract v3:1173-1183; BC-P2-23). The nine metrics, computed from the
//! governed repository's own state by the governance-suite family `artifact_flow_health` (G4-G6), each with its
//! numerator and denominator, the items that pull it down and a declared target:
//!
//! | metric | measured over | a fault that moves it |
//! |---|---|---|
//! | `required_input_delivery_accuracy` | the mandatory inputs of every live task whose context packet was delivered (stored packet), delivered at the version the manifest requires | a required input removed, changed or never delivered |
//! | `current_version_selection_accuracy` | the inputs those packets delivered | a delivered input superseded or changed since |
//! | `superseded_input_leakage_rate` | the governing inputs of live and DONE tasks (declared, delivered or consumed per receipt) | a task working from a SUPERSEDED/retired input not flagged stale |
//! | `missing_required_input_detection` | live tasks whose manifest lacks a mandatory input | such a task stored or offered as runnable |
//! | `staleness_propagation_accuracy` | (task, input) pairs whose input changed since the work consumed it | a direct upstream edit not yet propagated |
//! | `requirement_to_code_traceability_coverage` | ACTIVE requirements | a requirement no work implemented with production code |
//! | `requirement_to_test_traceability_coverage` | ACTIVE requirements | a requirement no test obligation/test validates |
//! | `orphan_detection` (recall / false positives) | W7 detection and the outcome of its investigations | an injected orphan (detected count), an investigation closed as not an orphan (false positive) |
//! | `fresh_agent_reconstruction_correctness` | reconstruction probes from records alone | a stale checkpoint, a claim on a missing task, an undeliverable packet |
//!
//! The metrics are reported (family detail, `gov health status`); a metric below its target is disclosed as a `low`
//! finding — the underlying defects are raised at their own severities by their owning checks (delivery:
//! `context_reproducibility`; leakage and stale links: `graph_integrity`; staleness: `upstream_change_propagation`;
//! W7: `lineage_orphans`), so W11 never double-counts a defect into the verdict.
use super::Family;
use crate::context::manifest;
use crate::records::{Record, RecordStore};
use crate::Project;
use serde_json::{json, Value};
use std::collections::BTreeSet;

pub const FAMILY: &str = "artifact_flow_health";

/// Declared targets (the metrics are tracked; a metric below its target is disclosed).
pub const TARGETS: &[(&str, f64)] = &[
    ("required_input_delivery_accuracy", 1.0),
    ("current_version_selection_accuracy", 1.0),
    ("missing_required_input_detection", 1.0),
    ("staleness_propagation_accuracy", 1.0),
    ("requirement_to_code_traceability_coverage", 1.0),
    ("requirement_to_test_traceability_coverage", 1.0),
    ("orphan_detection_precision", 1.0),
    ("fresh_agent_reconstruction_correctness", 1.0),
];
/// The one rate whose target is a maximum.
pub const MAX_SUPERSEDED_LEAKAGE_RATE: f64 = 0.0;

fn ratio(num: usize, den: usize) -> Value {
    if den == 0 {
        Value::Null
    } else {
        json!((num as f64) / (den as f64))
    }
}

fn metric(id: &str, contract: &str, num: usize, den: usize, detail: Value) -> Value {
    json!({"metric": id, "contract": contract, "value": ratio(num, den), "numerator": num, "denominator": den,
           "applicable": den > 0, "detail": detail})
}

const LIVE_STATUSES: &[&str] = &["READY", "CLAIMED", "IN_PROGRESS", "REVIEW", "BLOCKED"];

fn is_live_task(t: &Record) -> bool {
    LIVE_STATUSES.contains(&t.get("task_status").as_str())
        && !t.problems.iter().any(|x| x == "archived")
}

fn stored_packet(p: &Project, task: &str) -> Option<Value> {
    if task.contains('/') || task.contains("..") {
        return None;
    }
    crate::util::read_json(&p.runtime_dir().join("context").join(format!("{task}.json"))).ok()
}

/// Every W11 metric (see the module table).
pub fn metrics(p: &Project, store: &RecordStore) -> Value {
    let tasks: Vec<&Record> = store.of_type("task");
    let live: Vec<&&Record> = tasks
        .iter()
        .filter(|t| is_live_task(t) && !super::lineage::is_generated(t))
        .collect();
    // ---- m1 / m2: what the delivered packets carry against what the manifests require now
    let (mut declared, mut delivered_ok) = (0usize, 0usize);
    let (mut supplied_total, mut supplied_current) = (0usize, 0usize);
    let mut delivery_misses = vec![];
    let mut version_misses = vec![];
    for t in &live {
        let Some(pk) = stored_packet(p, &t.id()) else {
            continue;
        };
        let m = manifest::resolve(p, store, t);
        let supplied = pk["input_hashes"].as_object().cloned().unwrap_or_default();
        let normative = pk["input_normative_hashes"].as_object().cloned();
        for e in m
            .entries
            .iter()
            .filter(|e| e.required && e.slot != manifest::Slot::Dependency)
        {
            declared += 1;
            let got = supplied.get(&e.id).and_then(|v| v.as_str());
            let at_current = match (got, &normative) {
                (None, _) => false,
                (Some(_), Some(n)) => {
                    n.get(&e.id).and_then(|v| v.as_str()) == e.normative_hash.as_deref()
                }
                (Some(h), None) => Some(h) == e.content_hash.as_deref(),
            };
            if got.is_some() && at_current && e.satisfied() {
                delivered_ok += 1;
            } else {
                delivery_misses.push(json!({"task": t.id(), "input": e.id, "delivered": got.is_some(), "at_current_version": at_current, "satisfies_manifest": e.satisfied()}));
            }
        }
        for (id, h) in &supplied {
            supplied_total += 1;
            let cur = store.get(id);
            let current_record = cur
                .map(|r| {
                    !crate::graph::lineage::NON_CURRENT_STATUSES.contains(&r.status().as_str())
                        && r.get("superseded_by").is_empty()
                })
                .unwrap_or(false);
            let entry = m.entries.iter().find(|e| &e.id == id);
            let same_version = match (&normative, entry) {
                (Some(n), Some(e)) => {
                    n.get(id).and_then(|v| v.as_str()) == e.normative_hash.as_deref()
                }
                (None, Some(e)) => h.as_str() == e.content_hash.as_deref(),
                _ => cur.is_some(),
            };
            if current_record && same_version {
                supplied_current += 1;
            } else {
                version_misses.push(json!({"task": t.id(), "input": id, "current_record": current_record, "same_version": same_version}));
            }
        }
    }
    let m1 = metric(
        "required_input_delivery_accuracy",
        "Contract v3:1175",
        delivered_ok,
        declared,
        json!({"misses": delivery_misses.iter().take(20).collect::<Vec<_>>(), "over": "mandatory inputs of live tasks whose context packet was delivered"}),
    );
    let m2 = metric(
        "current_version_selection_accuracy",
        "Contract v3:1176",
        supplied_current,
        supplied_total,
        json!({"misses": version_misses.iter().take(20).collect::<Vec<_>>(), "over": "inputs delivered in stored context packets"}),
    );
    // ---- m3: superseded-input leakage (governing inputs of live and DONE work that are no longer current, unflagged)
    let mut pairs = 0usize;
    let mut leaks = vec![];
    for t in tasks.iter().filter(|t| {
        (is_live_task(t) || t.get("task_status") == "DONE") && !super::lineage::is_generated(t)
    }) {
        let mut inputs: BTreeSet<String> = BTreeSet::new();
        for f in [
            "requirements",
            "decisions",
            "scenarios",
            "interfaces",
            "architecture",
            "required_inputs",
        ] {
            for x in t.list(f) {
                inputs.insert(x.split('@').next().unwrap_or("").trim().to_string());
            }
        }
        if let Some(r) = store.get(&t.get("closed_by_report")) {
            for x in r.list("inputs_consumed") {
                inputs.insert(x.split('@').next().unwrap_or("").trim().to_string());
            }
        }
        let flagged = t
            .data
            .get("staleness")
            .map(|v| !v.is_null())
            .unwrap_or(false)
            || t.data["retest_required"] == true
            || t.data["revalidation_required"] == true;
        for id in inputs.iter().filter(|x| !x.is_empty()) {
            let Some(r) = store.get(id) else { continue };
            pairs += 1;
            let non_current = crate::graph::lineage::NON_CURRENT_STATUSES
                .contains(&r.status().as_str())
                || !r.get("superseded_by").is_empty();
            if non_current && !flagged {
                leaks.push(json!({"task": t.id(), "task_status": t.get("task_status"), "input": id, "input_status": r.status(), "superseded_by": r.get("superseded_by")}));
            }
        }
    }
    let m3 = json!({"metric": "superseded_input_leakage_rate", "contract": "Contract v3:1177", "value": ratio(leaks.len(), pairs),
                    "numerator": leaks.len(), "denominator": pairs, "applicable": pairs > 0,
                    "detail": {"leaks": leaks.iter().take(20).collect::<Vec<_>>(), "over": "governing inputs (declared, delivered or consumed per receipt) of live and DONE tasks; a flagged (stale/retest) task is not a leak"}});
    // ---- m4: missing required inputs, and whether the product detects them (not offered as runnable)
    let dag = crate::orchestration::dag::compute(p).ok();
    let runnable: BTreeSet<String> = dag
        .as_ref()
        .map(|d| d.runnable.iter().cloned().collect())
        .unwrap_or_default();
    let mut missing_tasks = 0usize;
    let mut detected = 0usize;
    let mut missing_rows = vec![];
    let mut missing_inputs = 0usize;
    for t in &live {
        let m = manifest::resolve(p, store, t);
        let miss = m.missing();
        if miss.is_empty() {
            continue;
        }
        missing_tasks += 1;
        missing_inputs += miss.len();
        let is_detected = !runnable.contains(&t.id())
            && (t.get("task_status") == "BLOCKED" || !runnable.contains(&t.id()));
        if is_detected {
            detected += 1;
        }
        missing_rows.push(json!({"task": t.id(), "task_status": t.get("task_status"), "missing_inputs": miss, "offered_as_runnable": runnable.contains(&t.id())}));
    }
    let m4 = json!({"metric": "missing_required_input_detection", "contract": "Contract v3:1178", "value": ratio(detected, missing_tasks),
                    "numerator": detected, "denominator": missing_tasks, "applicable": missing_tasks > 0,
                    "missing_required_inputs": missing_inputs, "detail": {"tasks": missing_rows}});
    // ---- m5: staleness propagation accuracy (changed inputs already propagated to the work that consumed them)
    let (mut changed_pairs, mut propagated) = (0usize, 0usize);
    let mut unpropagated = vec![];
    for t in &tasks {
        if matches!(t.get("task_status").as_str(), "CANCELLED") {
            continue;
        }
        let (_, st) = crate::cit::propagation::stale_inputs(p, store, t);
        for (c, prop) in st {
            changed_pairs += 1;
            if prop {
                propagated += 1;
            } else {
                unpropagated.push(
                    json!({"task": t.id(), "input": c.id, "consumed": c.from, "current": c.to}),
                );
            }
        }
    }
    let m5 = metric(
        "staleness_propagation_accuracy",
        "Contract v3:1179",
        propagated,
        changed_pairs,
        json!({"unpropagated": unpropagated.iter().take(20).collect::<Vec<_>>(), "over": "(task, input) pairs whose input changed since the work consumed it"}),
    );
    // ---- m6 / m7: requirement → code and requirement → test traceability
    let reqs = super::lineage::requirement_paths(p, store);
    let code = reqs.iter().filter(|r| r["code"] == true).count();
    let test = reqs.iter().filter(|r| r["test"] == true).count();
    let m6 = metric(
        "requirement_to_code_traceability_coverage",
        "Contract v3:1180",
        code,
        reqs.len(),
        json!({"uncovered": reqs.iter().filter(|r| r["code"] != true).map(|r| r["requirement"].clone()).collect::<Vec<_>>()}),
    );
    let m7 = metric(
        "requirement_to_test_traceability_coverage",
        "Contract v3:1181",
        test,
        reqs.len(),
        json!({"uncovered": reqs.iter().filter(|r| r["test"] != true).map(|r| r["requirement"].clone()).collect::<Vec<_>>()}),
    );
    // ---- m8: orphan-output detection recall / false positives
    let m8 = orphan_detection(p, store);
    // ---- m9: fresh-agent reconstruction correctness
    let m9 = reconstruction(p, store, &live);
    json!({
        "required_input_delivery_accuracy": m1, "current_version_selection_accuracy": m2,
        "superseded_input_leakage_rate": m3, "missing_required_input_detection": m4,
        "staleness_propagation_accuracy": m5, "requirement_to_code_traceability_coverage": m6,
        "requirement_to_test_traceability_coverage": m7, "orphan_detection": m8,
        "fresh_agent_reconstruction_correctness": m9,
    })
}

/// Recall and false positives of W7 orphan detection. In the governed repository the false-positive side is measured
/// from how investigations end: an investigation closed or withdrawn with a resolution stating the subject was not an
/// orphan (`resolution`/`outcome` naming `false_positive`, `not_an_orphan` or `intended`) is a false positive; one
/// whose subject was linked (no longer detected) or retired (gone) is a true positive. Recall needs the true orphan
/// set, which only the hidden oracle of a qualification run knows: the latest G6 qualification's recorded
/// `orphan_detection_recall` metric is reported when one exists.
fn orphan_detection(p: &Project, store: &RecordStore) -> Value {
    let db = if p.db_path().exists() {
        crate::memory::db::RuntimeDb::open(&p.db_path()).ok()
    } else {
        None
    };
    let report = super::lineage::detect(p, store, db.as_ref());
    let detected: BTreeSet<String> = report.orphans.iter().map(|o| o.key()).collect();
    let (mut tp, mut fp, mut open) = (0usize, 0usize, 0usize);
    let mut fps = vec![];
    for t in store.of_type("task") {
        if !super::lineage::is_generated(t) {
            continue;
        }
        let key = t.data["investigates"]["key"]
            .as_str()
            .unwrap_or("")
            .to_string();
        let st = t.get("task_status");
        if !matches!(st.as_str(), "DONE" | "CANCELLED") {
            open += 1;
            continue;
        }
        let rep = store.get(&t.get("closed_by_report"));
        let said = |k: &str| {
            let v = |x: &Value| {
                x.as_str()
                    .map(|s| s.to_ascii_lowercase())
                    .unwrap_or_default()
            };
            [
                v(&t.data[k]),
                rep.map(|r| v(&r.data[k])).unwrap_or_default(),
            ]
            .iter()
            .any(|s| {
                s.contains("false_positive")
                    || s.contains("not_an_orphan")
                    || s.contains("intended")
            })
        };
        if said("resolution") || said("outcome_reason") || said("cancel_reason") {
            fp += 1;
            fps.push(t.id());
        } else if !detected.contains(&key) {
            tp += 1;
        } else {
            open += 1;
        }
    }
    let recall = crate::scheduler::store::history(p, 300)
        .into_iter()
        .find(|h| h["tier"] == "G6")
        .and_then(|h| crate::scheduler::store::load_result(p, h["id"].as_str().unwrap_or("")))
        .and_then(|r| {
            r["qualification"]["score_report"]["metrics"]
                .as_object()
                .and_then(|m| {
                    m.iter()
                        .find(|(k, _)| k.contains("orphan") && k.contains("recall"))
                        .map(|(_, v)| v.clone())
                })
        });
    json!({"metric": "orphan_detection", "contract": "Contract v3:1182",
           "orphans_detected": report.orphans.len(), "by_kind": report.detail["by_kind"],
           "orphan_detection_precision": ratio(tp, tp + fp), "orphan_detection_false_positive_rate": ratio(fp, tp + fp),
           "orphan_detection_recall": recall.clone().unwrap_or(Value::Null),
           "recall_source": if recall.is_some() { json!("latest G6 qualification run (hidden oracle)") } else { json!("not measurable in the governed repository: the true orphan set is known only to a qualification oracle (G6)") },
           "investigations": {"resolved_true_positive": tp, "resolved_false_positive": fp, "open": open, "false_positives": fps},
           "applicable": true})
}

/// Can a fresh agent reconstruct the current state from records alone? Each probe either reconstructs correctly or
/// names what a fresh agent would get wrong.
fn reconstruction(p: &Project, store: &RecordStore, live: &[&&Record]) -> Value {
    let mut probes: Vec<Value> = vec![];
    // the status packet builds from records alone and stays within the read budget
    match crate::status::status(p) {
        Ok(st) => {
            let budget = p
                .policies()
                .get_i64("CONTEXT_POLICY", "fresh_agent_read_budget_files", 25)
                as usize;
            let reads = st["fresh_agent_reads"]
                .as_array()
                .map(|a| a.len())
                .unwrap_or(0);
            probes.push(json!({"probe": "status packet within the read budget", "ok": reads <= budget, "reads": reads, "budget": budget}));
        }
        Err(e) => {
            probes.push(json!({"probe": "status packet builds", "ok": false, "error": e.code}))
        }
    }
    // the latest checkpoint still describes the material state it captured
    if let Ok(f) = crate::checkpoints::freshness(p, None) {
        probes.push(json!({"probe": "latest checkpoint current", "ok": f["state"] == "CURRENT", "checkpoint": f["checkpoint"], "reasons": f["reasons"]}));
    }
    // every claim names a task that exists and is held
    if let Ok(cl) = crate::orchestration::claims::list(p) {
        for c in cl
            .iter()
            .filter(|c| !c["expired"].as_bool().unwrap_or(false))
        {
            let id = c["task_id"].as_str().unwrap_or("");
            let ok = store
                .get(id)
                .map(|t| {
                    matches!(
                        t.get("task_status").as_str(),
                        "CLAIMED" | "IN_PROGRESS" | "REVIEW" | "READY"
                    )
                })
                .unwrap_or(false);
            probes.push(json!({"probe": "claim names a held task", "ok": ok, "task": id}));
        }
    }
    // the mandatory inputs of work in progress resolve from records alone, and its delivered packet still verifies
    for t in live.iter().filter(|t| {
        matches!(
            t.get("task_status").as_str(),
            "CLAIMED" | "IN_PROGRESS" | "REVIEW"
        )
    }) {
        let m = manifest::resolve(p, store, t);
        probes.push(json!({"probe": "mandatory inputs resolve from records", "ok": m.satisfied(), "task": t.id(), "missing": m.missing()}));
        if let Some(pk) = stored_packet(p, &t.id()) {
            let ok = crate::context::verify_delivery(p, &pk)
                .map(|v| v["ok"] == true)
                .unwrap_or(false);
            probes.push(json!({"probe": "delivered packet reconstructs the current inputs", "ok": ok, "task": t.id()}));
        }
    }
    let ok = probes.iter().filter(|x| x["ok"] == true).count();
    json!({"metric": "fresh_agent_reconstruction_correctness", "contract": "Contract v3:1183", "value": ratio(ok, probes.len()),
           "numerator": ok, "denominator": probes.len(), "applicable": !probes.is_empty(), "probes": probes})
}

/// The `artifact_flow_health` family: the nine metrics in the detail; a `low` disclosure for each below target.
pub fn family(p: &Project, store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let m = metrics(p, store);
    for (id, target) in TARGETS {
        let v = if *id == "orphan_detection_precision" {
            m["orphan_detection"]["orphan_detection_precision"].as_f64()
        } else {
            m[*id]["value"].as_f64()
        };
        if let Some(v) = v {
            if v + 1e-9 < *target {
                f.findings.push(json!({"severity": "low", "family": fam, "metric": id,
                    "message": format!("W11 {id} is {v:.3}, below its target {target:.3} (Contract v3:1173-1183; the defects behind it are reported by their owning checks)"), "path": Value::Null}));
            }
        }
    }
    if let Some(v) = m["superseded_input_leakage_rate"]["value"].as_f64() {
        if v > MAX_SUPERSEDED_LEAKAGE_RATE + 1e-9 {
            f.findings.push(json!({"severity": "low", "family": fam, "metric": "superseded_input_leakage_rate",
                "message": format!("W11 superseded_input_leakage_rate is {v:.3}: work is governed by an input that is no longer current and is not flagged stale (Contract v3:1177)"), "path": Value::Null}));
        }
    }
    f.detail = json!({"w11_metrics": m, "targets": TARGETS.iter().map(|(k, v)| json!({"metric": k, "min": v})).collect::<Vec<_>>(), "max_superseded_input_leakage_rate": MAX_SUPERSEDED_LEAKAGE_RATE});
}
