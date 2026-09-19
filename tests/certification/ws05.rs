//! Repair iteration 1, round 2, WS-5 (P2-AR-0026): the task DAG, claims, close and status as the convergence point of
//! the round-1 APIs — runnable derived from the DAG (BC-P2-16), gate semantics on the DAG and close side (BC-P2-12),
//! close-side receipt validation (BC-P2-20), independence from recorded authorship on the task side (BC-P2-34), and
//! OS-written (T2) state observed at close (BC-P2-09 close side).
//!
//! Builder regression evidence (Contract v3 O3), not acceptance evidence. The helpers at the top are the certified
//! way for a builder test to close a task: the close report is the worker's consumption receipt, built from the
//! packet the worker was supplied (`receipt_contract`), never a bare `{work_completed, files_changed, tests}`.
#![allow(dead_code)]
use crate::common::*;
use serde_json::{json, Value};
use std::path::Path;

/// A close report that is the full consumption receipt (Contract v3 W5): the packet compiled for the task now (its
/// hash), every required input acknowledged at its current content hash, the trace the packet's `receipt_contract`
/// names, passing evidence for the declared tests, and explicit (empty) deviations and unknowns. Returns its path.
pub fn receipt(
    g: &Gov,
    root: &Path,
    task: &str,
    name: &str,
    work: &str,
    files: &[&str],
    tests_status: &str,
) -> String {
    receipt_with(g, root, task, name, work, files, tests_status, json!({}))
}

/// [`receipt`] with extra fields merged over it (e.g. a deviation, or a deliberately wrong trace).
#[allow(clippy::too_many_arguments)]
pub fn receipt_with(
    g: &Gov,
    root: &Path,
    task: &str,
    name: &str,
    work: &str,
    files: &[&str],
    tests_status: &str,
    extra: Value,
) -> String {
    let pk = g.ok(&["context", "compile", task]);
    let rc = &pk["receipt_contract"];
    let inputs: Vec<Value> = rc["acknowledge_inputs"]
        .as_array()
        .cloned()
        .unwrap_or_default()
        .iter()
        .map(|e| {
            json!(format!(
                "{}@{}",
                e["id"].as_str().unwrap_or(""),
                e["content_hash"].as_str().unwrap_or("")
            ))
        })
        .collect();
    let tests: Vec<Value> = rc["tests_requiring_evidence"]
        .as_array()
        .cloned()
        .unwrap_or_default()
        .iter()
        .map(|t| json!({"test": t, "result": "passed", "evidence": "certification run"}))
        .collect();
    let mut v = json!({"work_completed": work, "files_changed": files, "tests": {"status": tests_status, "reason": "certification"},
        "outcome": "success", "evidence": [], "context_packet_hash": pk["packet_hash"], "inputs_consumed": inputs,
        "outputs_produced": files, "requirements_implemented": rc["trace"]["requirements"],
        "scenarios_implemented": rc["trace"]["scenarios"], "features_implemented": rc["trace"]["features"],
        "decisions_applied": rc["trace"]["decisions"], "constraints_applied": rc["trace"]["constraints"],
        "acceptance_evidence": tests, "deviations": [], "unresolved": []});
    if let (Some(o), Some(x)) = (v.as_object_mut(), extra.as_object()) {
        for (k, val) in x {
            o.insert(k.clone(), val.clone());
        }
    }
    let p = root.join(".governance-runtime").join("reports");
    std::fs::create_dir_all(&p).unwrap();
    let f = p.join(format!("{name}.json"));
    std::fs::write(&f, serde_json::to_string(&v).unwrap()).unwrap();
    f.to_string_lossy().to_string()
}

/// Governed inputs that make an implementation task runnable and traceable without a feature: an ACTIVE requirement,
/// scenario and a `unit`-family test obligation (not an independence family), written as fixture records. Returns the
/// task `--fields` that declare them.
pub fn traceable_inputs(root: &Path, tag: &str) -> Value {
    let (req, scn, tst) = (
        format!("REQ-{tag}"),
        format!("SCN-{tag}"),
        format!("TST-{tag}"),
    );
    write_yaml(
        root,
        &format!("spec/requirements/{req}.yaml"),
        &json!({"id": req, "type": "requirement", "title": format!("requirement {tag}"), "status": "ACTIVE", "kind": "functional"}),
    );
    write_yaml(
        root,
        &format!("spec/scenarios/{scn}.yaml"),
        &json!({"id": scn, "type": "scenario", "title": format!("scenario {tag}"), "status": "ACTIVE", "actor": "clerk",
                "given": ["a ledger"], "when": ["an order is appended"], "then": ["the total moves"], "success_criteria": ["exact"], "failure_criteria": ["drift"]}),
    );
    write_yaml(
        root,
        &format!("spec/tasks/{tst}.yaml"),
        &json!({"id": tst, "type": "test-obligation", "title": format!("unit tests {tag}"), "status": "ACTIVE", "family": "unit", "scenario": scn}),
    );
    json!({"requirements": [req], "scenarios": [scn], "acceptance_tests": [tst]})
}
