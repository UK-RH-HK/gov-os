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

fn fresh(tag: &str) -> (std::path::PathBuf, Gov) {
    let (root, g) = setup_fixture("greenfield", tag, "S-ws5");
    g.ok(&["init", "--name", tag, "--alias", &format!("a-{tag}")]);
    git_commit_all(&root, "after init");
    (root, g)
}

fn create(
    g: &Gov,
    class: &str,
    objective: &str,
    status: &str,
    allowed: &str,
    fields: Value,
) -> Value {
    let f = fields.to_string();
    let mut args = vec![
        "task",
        "create",
        "--class",
        class,
        "--objective",
        objective,
        "--status",
        status,
        "--fields",
        &f,
    ];
    if !allowed.is_empty() {
        args.extend(["--allowed", allowed]);
    }
    g.ok(&args)
}

fn id(v: &Value) -> String {
    v["id"].as_str().unwrap().to_string()
}

fn dag(g: &Gov) -> Value {
    g.ok(&["task", "dag"])
}

fn runnable(g: &Gov, task: &str) -> bool {
    dag(g)["runnable"]
        .as_array()
        .unwrap()
        .iter()
        .any(|x| x == task)
}

fn blocked_reasons(g: &Gov, task: &str) -> String {
    let d = dag(g);
    let mut s = String::new();
    for k in ["blocked", "waiting_human"] {
        for b in d[k].as_array().unwrap() {
            if b["task"] == task {
                s.push_str(&b["reasons"].to_string());
            }
        }
    }
    s
}

/// BC-P2-16: READY, claimable and runnable are one derived fact. A task whose mandatory input is absent is stored in
/// the status the DAG derives, cannot be set READY, claimed or replanned READY; DONE / IN_PROGRESS are reached only
/// through close / claim; an explicit hold is kept until an explicit, DAG-checked READY.
#[test]
fn runnable_ready_and_claimable_are_derived_from_the_task_dag() {
    let (root, g) = fresh("ws5-derive");
    let t = create(
        &g,
        "documentation",
        "needs a requirement that does not exist",
        "READY",
        "docs/**",
        json!({"requirements": ["REQ-0901"]}),
    );
    let tid = id(&t);
    assert_eq!(t["task_status"], "BLOCKED", "{t}");
    assert!(t["ready_check"]["dag"]["reasons"]
        .to_string()
        .contains("REQ-0901"));
    assert_eq!(
        g.err(&["task", "status", &tid, "READY"]).error_code(),
        "TASK_NOT_READY"
    );
    assert_eq!(
        g.err(&["task", "claim", &tid]).error_code(),
        "TASK_NOT_RUNNABLE"
    );
    let rp = g.ok(&["task", "replan"]);
    assert!(
        !rp["changed"].to_string().contains(&tid),
        "replan must not promote it: {rp}"
    );
    assert!(!runnable(&g, &tid));
    // the input appears: the same derivation now allows it
    write_yaml(
        &root,
        "spec/requirements/REQ-0901.yaml",
        &json!({"id": "REQ-0901", "type": "requirement", "title": "docs describe totals", "status": "ACTIVE", "kind": "functional"}),
    );
    let rp = g.ok(&["task", "replan"]);
    assert!(rp["changed"].to_string().contains(&tid), "{rp}");
    assert!(runnable(&g, &tid));
    g.ok(&["task", "claim", &tid]);
    // DONE / CLAIMED / IN_PROGRESS are reached only through their operations
    let d = create(&g, "documentation", "plain", "READY", "notes/**", json!({}));
    for st in ["DONE", "IN_PROGRESS", "CLAIMED"] {
        assert_eq!(
            g.err(&["task", "status", &id(&d), st]).error_code(),
            "TASK_STATUS_REQUIRES_OPERATION",
            "{st}"
        );
    }
    assert_eq!(
        g.err(&[
            "task",
            "create",
            "--class",
            "documentation",
            "--objective",
            "born done",
            "--status",
            "DONE"
        ])
        .error_code(),
        "TASK_STATUS_REQUIRES_OPERATION"
    );
    // an explicit hold is not runnable, not offered, not replanned; only an explicit READY releases it
    g.ok(&[
        "task",
        "status",
        &id(&d),
        "BLOCKED",
        "--note",
        "waiting on vendor",
    ]);
    assert!(!runnable(&g, &id(&d)));
    assert!(blocked_reasons(&g, &id(&d)).contains("explicitly"));
    g.ok(&["task", "replan"]);
    assert_eq!(g.ok(&["task", "show", &id(&d)])["task_status"], "BLOCKED");
    let other = g.with_session("S-other");
    let c = other.ok(&["continue"]);
    assert_ne!(c["task"], json!(id(&d)), "{c}");
    assert!(!c["parallel_runnable"].to_string().contains(&id(&d)), "{c}");
    assert_eq!(
        other.err(&["task", "claim", &id(&d)]).error_code(),
        "TASK_NOT_RUNNABLE"
    );
    g.ok(&["task", "status", &id(&d), "READY"]);
    assert!(runnable(&g, &id(&d)));
}

/// BC-P2-12 (DAG and close side): gated work is runnable only on an answer that authorises it, returns to blocked
/// when the answer declines or the gate is withdrawn, a missing gate blocks, removing the task's `human_gate` field
/// does not release it (the OS-written gate names the task), and gated work cannot be completed — not even with
/// `--force` — while its gate withholds authorisation.
#[test]
fn gates_decide_runnability_and_completion() {
    let (root, g) = fresh("ws5-gates");
    crate::ws03::human_channel(&g);
    let gated = |q: &str, tasks: &[&str]| -> String {
        let r = g.ok(&[
            "gate",
            "create",
            "--question",
            q,
            "--fields",
            &crate::ws03::package(json!({"blocks_tasks": tasks})),
        ]);
        id(&r)
    };
    // pending -> waiting, not claimable
    let t1 = id(&create(
        &g,
        "discovery",
        "t1",
        "READY",
        "notes/a/**",
        json!({}),
    ));
    let g1 = gated("May t1 proceed?", &[&t1]);
    assert!(!runnable(&g, &t1));
    assert!(dag(&g)["waiting_human"].to_string().contains(&t1));
    assert_eq!(
        g.err(&["task", "claim", &t1]).error_code(),
        "TASK_NOT_RUNNABLE"
    );
    // a declining answer blocks
    crate::ws03::human_decide(&g, &g1, "B");
    assert!(!runnable(&g, &t1));
    assert!(blocked_reasons(&g, &t1).contains("does not authorise"));
    // an authorising answer releases; withdrawing it blocks again
    let t2 = id(&create(
        &g,
        "discovery",
        "t2",
        "READY",
        "notes/b/**",
        json!({}),
    ));
    let g2 = gated("May t2 proceed?", &[&t2]);
    crate::ws03::human_decide(&g, &g2, "A");
    assert!(runnable(&g, &t2), "{}", dag(&g));
    g.ok(&["task", "claim", &t2]);
    g.ok(&["gate", "revoke", &g2, "--reason", "withdrawn"]);
    assert!(blocked_reasons(&g, &t2).contains("withdrawn"));
    write(&root, "notes/b/out.txt", "work\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &g,
        &root,
        &t2,
        "t2",
        "work",
        &["notes/b/out.txt"],
        "not_applicable_with_reason",
    );
    let e = g.err(&["task", "close", &t2, "--report", &rep]);
    assert_eq!(e.error_code(), "GATE_NOT_AUTHORISED", "{}", e.envelope);
    assert_eq!(
        g.err(&["task", "close", &t2, "--report", &rep, "--force"])
            .error_code(),
        "GATE_NOT_AUTHORISED",
        "a human gate is not an L3 decision"
    );
    // a gate raised against work already in progress stops its completion (delta-r L3s.1)
    let t3 = id(&create(
        &g,
        "discovery",
        "t3",
        "READY",
        "notes/c/**",
        json!({}),
    ));
    g.ok(&["task", "claim", &t3]);
    let g3 = gated("Is it safe to continue t3?", &[&t3]);
    write(&root, "notes/c/out.txt", "work\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep3 = receipt(
        &g,
        &root,
        &t3,
        "t3",
        "work",
        &["notes/c/out.txt"],
        "not_applicable_with_reason",
    );
    let e = g.err(&["task", "close", &t3, "--report", &rep3]);
    assert_eq!(e.error_code(), "GATE_NOT_AUTHORISED");
    assert!(e.envelope.to_string().contains(&g3));
    crate::ws03::human_decide(&g, &g3, "A");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep3 = receipt(
        &g,
        &root,
        &t3,
        "t3b",
        "work",
        &["notes/c/out.txt"],
        "not_applicable_with_reason",
    );
    g.ok(&["task", "close", &t3, "--report", &rep3]);
    // a reference to a missing gate blocks
    let t4 = id(&create(
        &g,
        "discovery",
        "t4",
        "READY",
        "notes/d/**",
        json!({}),
    ));
    let mut rec = yaml(&root, &format!("spec/tasks/{t4}.yaml"));
    rec["human_gate"] = json!("HDG-9999");
    write_yaml(&root, &format!("spec/tasks/{t4}.yaml"), &rec);
    assert!(blocked_reasons(&g, &t4).contains("does not exist"));
    // removing the field from the task record does not release it: the OS-written gate names the task
    let t5 = id(&create(
        &g,
        "discovery",
        "t5",
        "READY",
        "notes/e/**",
        json!({}),
    ));
    let _g5 = gated("May t5 proceed?", &[&t5]);
    let mut rec = yaml(&root, &format!("spec/tasks/{t5}.yaml"));
    rec.as_object_mut().unwrap().remove("human_gate");
    rec["task_status"] = json!("READY");
    write_yaml(&root, &format!("spec/tasks/{t5}.yaml"), &rec);
    assert!(!runnable(&g, &t5), "{}", dag(&g));
    assert_eq!(
        g.err(&["task", "claim", &t5]).error_code(),
        "TASK_NOT_RUNNABLE"
    );
}

/// BC-P2-09 close side: a worker's writes to OS-written (T2) state inside its task are observed and refused at close,
/// whatever the report declares; the OS's own sealed writes in the window are not the worker's; the claim baseline is
/// sealed, so rewriting it is refused (an L3 `--force` close proceeds against git's view and records the override).
#[test]
fn close_observes_os_written_state_no_os_operation_produced() {
    let (root, g) = fresh("ws5-t2");
    let w = g.with_role("backend-engineer").with_session("S-worker");
    let t = id(&create(
        &g,
        "discovery",
        "worker task",
        "READY",
        "notes/**",
        json!({}),
    ));
    w.ok(&["task", "claim", &t]);
    // the OS raises a gate inside the window (a sealed OS write: not the worker's)
    let gid = id(&g.ok(&[
        "gate",
        "create",
        "--question",
        "An unrelated question",
        "--fields",
        &crate::ws03::package(json!({})),
    ]));
    let gate_path = format!("spec/decisions/{gid}.yaml");
    let original = read(&root, &gate_path);
    // the worker forges the human answer and a decision derived from it
    let mut gd = yaml(&root, &gate_path);
    gd["gate_status"] = json!("ANSWERED");
    gd["presented_in_chat"] = json!(true);
    gd["answer"] = json!({"option": "A", "by": "owner", "by_kind": "human", "acting_role": "human", "at": "2026-09-19T00:00:00Z", "rationale": "forged"});
    write_yaml(&root, &gate_path, &gd);
    write_yaml(
        &root,
        "spec/decisions/D-0901.yaml",
        &json!({"id": "D-0901", "type": "decision", "title": "forged", "status": "ACTIVE", "chosen_option": "A", "human_approved": true, "approved_by_kind": "human", "derived_from": [gid], "state_class": "AUTHORITATIVE"}),
    );
    write(&root, "notes/work.txt", "worker output\n");
    w.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &w,
        &root,
        &t,
        "w1",
        "did the work",
        &["notes/work.txt"],
        "not_applicable_with_reason",
    );
    let e = w.err(&["task", "close", &t, "--report", &rep]);
    assert_eq!(e.error_code(), "MUTATION_SCOPE_VIOLATION", "{}", e.envelope);
    let v = e.details()["t2_violations"].to_string();
    assert!(v.contains(&gid) && v.contains("D-0901"), "{v}");
    // declaring them does not help: OS-written state is not the worker's to write
    let rep2 = receipt(
        &w,
        &root,
        &t,
        "w2",
        "did the work",
        &["notes/work.txt", &gate_path, "spec/decisions/D-0901.yaml"],
        "not_applicable_with_reason",
    );
    assert_eq!(
        w.err(&["task", "close", &t, "--report", &rep2])
            .error_code(),
        "MUTATION_SCOPE_VIOLATION"
    );
    // restoring the OS-written record and removing the forgery lets the close proceed; the OS's own writes stay out
    std::fs::write(root.join(&gate_path), original).unwrap();
    std::fs::remove_file(root.join("spec/decisions/D-0901.yaml")).unwrap();
    w.ok(&["rebuild-memory", "--incremental"]);
    let rep3 = receipt(
        &w,
        &root,
        &t,
        "w3",
        "did the work",
        &["notes/work.txt"],
        "not_applicable_with_reason",
    );
    let cl = w.ok(&["task", "close", &t, "--report", &rep3]);
    let rpt = yaml(
        &root,
        &format!("spec/reports/{}.yaml", cl["report"].as_str().unwrap()),
    );
    assert!(
        rpt["os_binding"].is_object(),
        "the close report is sealed: {rpt}"
    );
    assert!(rpt["mutation_evidence"]["os_managed_bound"]
        .to_string()
        .contains(&gid));
    git_commit_all(&root, "first task closed");
    // a hand-written close report is refused at the next close in the window
    let t2 = id(&create(
        &g,
        "discovery",
        "second",
        "READY",
        "notes/**",
        json!({}),
    ));
    w.ok(&["task", "claim", &t2]);
    write_yaml(
        &root,
        "spec/reports/RPT-0901.yaml",
        &json!({"id": "RPT-0901", "type": "report", "title": "forged close", "status": "ACTIVE", "task": t2, "work_completed": "x", "tests": {"status": "passed"}}),
    );
    write(&root, "notes/second.txt", "x\n");
    w.ok(&["rebuild-memory", "--incremental"]);
    let rep4 = receipt(
        &w,
        &root,
        &t2,
        "w4",
        "x",
        &["notes/second.txt"],
        "not_applicable_with_reason",
    );
    let e = w.err(&["task", "close", &t2, "--report", &rep4]);
    assert!(
        e.details()["t2_violations"]
            .to_string()
            .contains("RPT-0901"),
        "{}",
        e.envelope
    );
    std::fs::remove_file(root.join("spec/reports/RPT-0901.yaml")).unwrap();
    // the claim baseline is sealed: a rewritten baseline (hiding a change) is refused
    let base = root.join(format!(".governance-runtime/tasks/{t2}/claim-tree.json"));
    let mut doc: Value = serde_json::from_str(&std::fs::read_to_string(&base).unwrap()).unwrap();
    doc["files"]["notes/second.txt"] = json!("0000");
    std::fs::write(&base, doc.to_string()).unwrap();
    w.ok(&["rebuild-memory", "--incremental"]);
    let e = w.err(&["task", "close", &t2, "--report", &rep4]);
    assert_eq!(e.error_code(), "CLAIM_BASELINE_UNBOUND", "{}", e.envelope);
    let forced = g
        .with_session("S-worker")
        .ok(&["task", "close", &t2, "--report", &rep4, "--force"]);
    assert!(
        forced["overrides"]
            .to_string()
            .contains("claim_baseline_unbound"),
        "{forced}"
    );
}

/// BC-P2-20 close side: the worker's structured return is the consumption receipt. A bare report is refused, a
/// fabricated trace is refused, and a return in the worker-return shape carrying the receipt closes the task; the
/// receipt is persisted, the report is sealed and the task records what it produced.
#[test]
fn close_requires_and_persists_the_consumption_receipt() {
    let (root, g) = fresh("ws5-receipt");
    let inputs = traceable_inputs(&root, "0300");
    git_commit_all(&root, "inputs");
    g.ok(&["rebuild-memory", "--incremental"]);
    let t = create(
        &g,
        "implementation",
        "implement totals",
        "READY",
        "src/**",
        inputs,
    );
    let tid = id(&t);
    assert_eq!(t["task_status"], "READY", "{t}");
    g.ok(&["task", "claim", &tid]);
    let lib = read(&root, "src/lib.rs");
    write(
        &root,
        "src/lib.rs",
        &format!("{lib}\npub fn ws5_receipt() -> i64 {{ 1 }}\n"),
    );
    g.ok(&["rebuild-memory", "--incremental"]);
    let bare = write_report(
        &root,
        "bare",
        "implemented",
        &["src/lib.rs"],
        "not_applicable_with_reason",
    );
    let e = g.err(&["task", "close", &tid, "--report", &bare]);
    assert_eq!(e.error_code(), "RECEIPT_INVALID", "{}", e.envelope);
    let codes = e.details()["errors"].to_string();
    for c in [
        "RECEIPT_FIELDS_MISSING",
        "INPUT_NOT_ACKNOWLEDGED",
        "TRACEABILITY_MISSING",
        "TEST_EVIDENCE_MISSING",
    ] {
        assert!(codes.contains(c), "{c}: {codes}");
    }
    let forged = receipt_with(
        &g,
        &root,
        &tid,
        "forged",
        "implemented",
        &["src/lib.rs"],
        "not_applicable_with_reason",
        json!({"requirements_implemented": ["REQ-9999"]}),
    );
    let e = g.err(&["task", "close", &tid, "--report", &forged]);
    assert!(
        e.details()["errors"]
            .to_string()
            .contains("UNKNOWN_REFERENCE"),
        "{}",
        e.envelope
    );
    // the worker-return shape (status success, discoveries, risks, ...) is the receipt: one contract
    let full: Value = serde_json::from_str(
        &std::fs::read_to_string(receipt(
            &g,
            &root,
            &tid,
            "full",
            "implemented",
            &["src/lib.rs"],
            "not_applicable_with_reason",
        ))
        .unwrap(),
    )
    .unwrap();
    let mut wr = full.clone();
    let o = wr.as_object_mut().unwrap();
    o.remove("outcome");
    for (k, v) in [
        ("task", json!(tid)),
        ("status", json!("success")),
        ("discoveries", json!([])),
        ("risks", json!([])),
        ("lessons", json!([])),
        ("proposed_decisions", json!([])),
        ("recommended_next_action", json!("close")),
    ] {
        o.insert(k.into(), v);
    }
    let schemas =
        gov_runtime::schemas::SchemaRegistry::new(&canonical_root().join("framework/schemas"));
    schemas
        .validate("worker-return", &wr, "(ws05)")
        .expect("the return is a schema-valid worker return");
    let wf = root.join(".governance-runtime/reports/worker-return.json");
    std::fs::write(&wf, wr.to_string()).unwrap();
    let cl = g.ok(&["task", "close", &tid, "--report", wf.to_str().unwrap()]);
    assert_eq!(cl["receipt_validation"]["ok"], true, "{cl}");
    let rpt = yaml(
        &root,
        &format!("spec/reports/{}.yaml", cl["report"].as_str().unwrap()),
    );
    assert_eq!(rpt["outcome"], "success");
    assert_eq!(rpt["requirements_implemented"], json!(["REQ-0300"]));
    assert!(rpt["os_binding"].is_object());
    let tr = yaml(&root, &format!("spec/tasks/{tid}.yaml"));
    assert_eq!(tr["outputs_produced"], json!(["src/lib.rs"]), "{tr}");
    assert_eq!(tr["provenance"]["producer"], "gov task create");
}

/// BC-P2-34 (task-role side): independence of tests and test data from the implementer is established from recorded
/// authorship — the sealed close report that produced the artefact — not from what the artefact says about itself;
/// the session that authored the independent tests of a feature may not implement it; test data the implementer
/// authored blocks the implementation.
#[test]
fn independence_is_established_from_recorded_authorship() {
    let (root, g) = fresh("ws5-indep");
    write_yaml(
        &root,
        "spec/features/F-0200.yaml",
        &json!({"id": "F-0200", "type": "feature", "title": "Totals", "status": "ACTIVE", "capability_category": "backend", "requirements": ["REQ-0200"], "scenarios": ["SCN-0200"], "acceptance_tests": ["TST-0200"],
                "readiness": readiness_all_present_except(&[], &[("ux_interactions", "library crate, no UI"), ("cost_constraints", "no infrastructure cost")])}),
    );
    write_yaml(
        &root,
        "spec/requirements/REQ-0200.yaml",
        &json!({"id": "REQ-0200", "type": "requirement", "title": "exact totals", "status": "ACTIVE", "feature": "F-0200", "kind": "functional"}),
    );
    write_yaml(
        &root,
        "spec/scenarios/SCN-0200.yaml",
        &json!({"id": "SCN-0200", "type": "scenario", "title": "total two orders", "status": "ACTIVE", "feature": "F-0200", "actor": "clerk", "given": ["a ledger"], "when": ["two orders"], "then": ["399"], "success_criteria": ["exact"], "failure_criteria": ["drift"]}),
    );
    // a hand-written acceptance obligation that declares itself independent
    let tst = json!({"id": "TST-0200", "type": "test-obligation", "title": "acceptance", "status": "ACTIVE", "feature": "F-0200", "scenario": "SCN-0200", "family": "acceptance", "author_role": "independent-test-designer", "independent_of_implementer": true});
    write_yaml(&root, "spec/tasks/TST-0200.yaml", &tst);
    git_commit_all(&root, "feature");
    g.ok(&["rebuild-memory", "--incremental"]);
    let imp = id(&create(
        &g,
        "implementation",
        "implement totals",
        "READY",
        "src/**",
        json!({"feature": "F-0200", "requirements": ["REQ-0200"], "scenarios": ["SCN-0200"], "role": "backend-engineer"}),
    ));
    assert!(!runnable(&g, &imp));
    assert!(
        blocked_reasons(&g, &imp).contains("recorded authorship"),
        "{}",
        blocked_reasons(&g, &imp)
    );
    // produced through a test-design task closed by an independent role and session, it counts
    let td = id(&create(
        &g,
        "test-design",
        "independent acceptance tests",
        "READY",
        "spec/**",
        json!({"feature": "F-0200", "role": "independent-test-designer"}),
    ));
    let designer = g
        .with_role("independent-test-designer")
        .with_session("S-td");
    designer.ok(&["task", "claim", &td]);
    let mut tst2 = tst.clone();
    tst2["test_path"] = json!("tests/ledger_test.rs");
    write_yaml(&root, "spec/tasks/TST-0200.yaml", &tst2);
    designer.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &designer,
        &root,
        &td,
        "td",
        "tests designed",
        &["spec/tasks/TST-0200.yaml"],
        "not_applicable_with_reason",
    );
    designer.ok(&["task", "close", &td, "--report", &rep]);
    g.ok(&["task", "replan"]);
    assert!(runnable(&g, &imp), "{}", blocked_reasons(&g, &imp));
    // the session that authored the tests may not implement the feature, whatever role it declares
    let same = g.with_role("backend-engineer").with_session("S-td");
    let e = same.err(&["task", "claim", &imp]);
    assert_eq!(e.error_code(), "INDEPENDENCE_VIOLATION", "{}", e.envelope);
    let c = same.ok(&["continue"]);
    assert!(c["deferred"].to_string().contains("independence"), "{c}");
    // test data the implementer authored blocks the implementation (Contract v3 H4)
    write_yaml(
        &root,
        "spec/data/TD-0200.yaml",
        &json!({"id": "TD-0200", "type": "data", "title": "test orders", "status": "ACTIVE", "author_role": "backend-engineer"}),
    );
    let mut tst3 = tst2.clone();
    tst3["data_provenance"] = json!("TD-0200 (synthetic)");
    write_yaml(&root, "spec/tasks/TST-0200.yaml", &tst3);
    let r = blocked_reasons(&g, &imp);
    assert!(r.contains("TD-0200"), "{r}");
    // an independent implementer session proceeds once the tests and data are independent again
    write_yaml(&root, "spec/tasks/TST-0200.yaml", &tst2);
    std::fs::remove_file(root.join("spec/data/TD-0200.yaml")).unwrap();
    g.ok(&["rebuild-memory", "--incremental"]);
    g.with_role("backend-engineer")
        .with_session("S-impl")
        .ok(&["task", "claim", &imp]);
}

/// WS-5 IP-4: releasing a claim is a governed write. It passes the write guard (kernel trust, the OWNER-DECISION-0006
/// §6 default-refuse allow-list, FREEZE_WRITES / PAUSE) inside the runtime operation, not only at the CLI's G0: with
/// the installed kernel tampered, every governed write is refused — the claim release included.
#[test]
fn releasing_a_claim_is_a_guarded_write() {
    let (root, g) = fresh("ws5-release");
    let t = id(&create(
        &g,
        "documentation",
        "d",
        "READY",
        "docs/**",
        json!({}),
    ));
    g.ok(&["task", "claim", &t]);
    let pol = "governance/kernel/policies/BUDGET_POLICY.yaml";
    let orig = read(&root, pol);
    write(&root, pol, &format!("{orig}\n# tampered\n"));
    let e = g.err(&["task", "release", &t]);
    assert_eq!(e.error_code(), "KERNEL_TAMPERED", "{}", e.envelope);
    write(&root, pol, &orig);
    assert_eq!(g.ok(&["task", "release", &t])["released"], true);
    g.ok(&["freeze-writes", "--reason", "incident"]);
    assert_eq!(g.err(&["task", "claim", &t]).error_code(), "FROZEN");
}

/// WS-2 IP-WS02-04, WS-8 IP-4, WS-3 IP-3: a fresh agent sees the health state and this project's release trust, and
/// the product never proposes a command that asserts a human identity on the agent's behalf.
#[test]
fn status_shows_health_and_this_projects_release_trust() {
    let (_root, g) = fresh("ws5-status");
    let st = g.ok(&["status"]);
    assert!(st["health"]["state"].is_string(), "{}", st["health"]);
    assert!(st["release_trust"]["scope"]
        .as_str()
        .unwrap()
        .contains("this project"));
    assert!(st["release_trust"]["authenticity"].is_string());
    let gid = id(&g.ok(&[
        "gate",
        "create",
        "--question",
        "approve?",
        "--fields",
        &crate::ws03::package(json!({})),
    ]));
    let it = g.ok(&["intent", "approve it"]);
    assert!(!it["commands"].to_string().contains("--by human"), "{it}");
    assert!(it["commands"].to_string().contains(&gid));
}
