//! Repair iteration 1, round-3 integration (P2-AR-0041): the end states the integration handoff (P2-HO-0040) asks to
//! be proven on the integrated tree — task records sealed on every OS write with `task` a sealed record kind (WS-5 r2
//! IP-R3-1, final step), proven with a close inside another task's claim window; the OS writes other operations make
//! inside a claim window attributed rather than read as the worker's (R3-WS5-8); a CIT invalidating DONE work leaves the
//! graph well typed (IP-R3-WS02-07); and WS-2's G2 readiness duty at close still reached in the union behind WS-5's
//! in-task materiality rule.
//!
//! Integration regression evidence (Contract v3 O3), not acceptance evidence. Black-box through the `gov` JSON
//! contract on the one provisioned-root harness; closes carry consumption receipts (`crate::ws05::receipt`).
use crate::common::*;
use crate::ws05::{receipt, traceable_inputs};
use serde_json::{json, Value};
use std::path::Path;

fn fresh(tag: &str) -> (std::path::PathBuf, Gov) {
    let (root, g) = setup_fixture("greenfield", tag, "S-int3");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        tag,
        "--alias",
        &format!("a-{tag}"),
    ]);
    git_commit_all(&root, "after init");
    (root, g)
}

fn create(g: &Gov, class: &str, objective: &str, allowed: &str, fields: Value) -> String {
    let f = fields.to_string();
    g.ok(&[
        "task",
        "create",
        "--class",
        class,
        "--objective",
        objective,
        "--status",
        "READY",
        "--allowed",
        allowed,
        "--fields",
        &f,
    ])["id"]
        .as_str()
        .unwrap()
        .to_string()
}

fn write_file(root: &Path, rel: &str, text: &str) {
    let p = root.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, text).unwrap();
}

/// The T2 binding of record `rid` as `gov artefact show` reports it: (binding, sealing operation).
fn seal(g: &Gov, rid: &str) -> (String, String) {
    let a = g.ok(&["artefact", "show", rid]);
    (
        a["t2_binding"]["binding"]
            .as_str()
            .unwrap_or("")
            .to_string(),
        a["t2_binding"]["operation"]
            .as_str()
            .unwrap_or("")
            .to_string(),
    )
}

/// Claim `task` from its own session and role, do its work in `file`, and close it with a consumption receipt.
fn do_and_close(g: &Gov, root: &Path, task: &str, file: &str) -> Value {
    write_file(root, file, &format!("// {task}\npub fn f() {{}}\n"));
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        g,
        root,
        task,
        task,
        "work",
        &[file],
        "not_applicable_with_reason",
    );
    g.ok(&["task", "close", task, "--report", &rep])
}

/// Every task record the OS writes is sealed (created, claimed, closed, replanned), and a close inside another task's
/// claim window honours those writes: the other task's claim and close, the report, and generated work are OS writes
/// recognised by their seals, never this worker's mutations.
#[test]
fn task_records_are_sealed_and_os_writes_inside_another_claim_window_are_honoured() {
    let (root, g) = fresh("int3-seal");
    let ia = traceable_inputs(&root, "0801");
    let ib = traceable_inputs(&root, "0802");
    git_commit_all(&root, "inputs");
    g.ok(&["rebuild-memory", "--incremental"]);
    let a = create(&g, "refactor", "work a", "src/a/**", ia);
    let b = create(&g, "refactor", "work b", "src/b/**", ib);
    // created by `gov task create`: sealed as that operation (portable scope on this owner machine)
    assert_eq!(seal(&g, &a), ("VERIFIED".into(), "task create".into()));
    let ra = yaml(&root, &format!("spec/tasks/{a}.yaml"));
    assert_eq!(ra["os_binding"]["alg"], "hmac-sha256/t2-v2", "{ra}");
    assert!(gov_runtime::t2::SEALED_RECORD_TYPES.contains(&"task"));
    // A is claimed first; B is claimed and closed entirely inside A's claim window
    let ga = g.with_session("S-a");
    let gb = g.with_session("S-b");
    ga.ok(&["context", "compile", &a]);
    ga.ok(&["task", "claim", &a]);
    assert_eq!(seal(&g, &a), ("VERIFIED".into(), "task claim".into()));
    gb.ok(&["context", "compile", &b]);
    gb.ok(&["task", "claim", &b]);
    let cb = do_and_close(&gb, &root, &b, "src/b/lib.rs");
    assert_eq!(cb["task_status"], "DONE", "{cb}");
    assert_eq!(seal(&g, &b), ("VERIFIED".into(), "task close".into()));
    // A closes with its own work only: B's task record (and every OS write inside A's window) is recognised by its seal
    let ca = do_and_close(&ga, &root, &a, "src/a/lib.rs");
    assert_eq!(ca["task_status"], "DONE", "{ca}");
    let rpt = yaml(
        &root,
        &format!("spec/reports/{}.yaml", ca["report"].as_str().unwrap()),
    );
    let bound: Vec<String> = rpt["mutation_evidence"]["os_managed_bound"]
        .as_array()
        .unwrap()
        .iter()
        .map(|x| x.as_str().unwrap().to_string())
        .collect();
    assert!(
        bound.iter().any(|p| p == &format!("spec/tasks/{b}.yaml")),
        "B's task record, written inside A's window, is an OS write recognised by its seal: {}",
        rpt["mutation_evidence"]
    );
    // every task record in the project verifies: the suite's T2 family names none of them
    let o = g.run(&["audit", "--no-persist", "--family", "os_binding_integrity"]);
    let text = o.envelope.to_string();
    assert!(
        !text.contains("spec/tasks/TASK-"),
        "a task record the OS wrote does not verify: {text}"
    );
}

/// A task record written outside `gov` inside a claim window is refused at that close as a T2 violation: a sealed
/// record edited by hand (BROKEN), a sealed record whose seal was stripped and its status forged DONE (an unsealed
/// record of a sealed kind — refusable because `task` is a sealed kind), and a task record created by hand.
#[test]
fn a_task_record_written_outside_gov_inside_a_claim_window_is_refused_at_close() {
    let (root, g) = fresh("int3-forge");
    let ia = traceable_inputs(&root, "0811");
    git_commit_all(&root, "inputs");
    g.ok(&["rebuild-memory", "--incremental"]);
    let a = create(&g, "refactor", "work a", "src/a/**", ia);
    let c = create(&g, "documentation", "notes", "docs/**", json!({}));
    let ga = g.with_session("S-a");
    ga.ok(&["context", "compile", &a]);
    ga.ok(&["task", "claim", &a]);
    write_file(&root, "src/a/lib.rs", "pub fn f() {}\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &ga,
        &root,
        &a,
        "a",
        "work",
        &["src/a/lib.rs"],
        "not_applicable_with_reason",
    );
    let c_rel = format!("spec/tasks/{c}.yaml");
    let original = read(&root, &c_rel);
    let refused = |what: &str| {
        let e = ga.err(&["task", "close", &a, "--report", &rep]);
        assert_eq!(
            e.error_code(),
            "MUTATION_SCOPE_VIOLATION",
            "{what}: {}",
            e.envelope
        );
        let v = e.details()["t2_violations"].to_string();
        assert!(v.contains("spec/tasks/"), "{what}: {v}");
        v
    };
    // (a) a hand edit of a sealed task record (forged DONE): BROKEN
    let mut forged = yaml(&root, &c_rel);
    forged["task_status"] = json!("DONE");
    write_yaml(&root, &c_rel, &forged);
    let v = refused("hand edit");
    assert!(v.contains("BROKEN"), "{v}");
    // (b) the same forgery with the seal stripped: an unsealed record of a sealed kind
    forged.as_object_mut().unwrap().remove("os_binding");
    write_yaml(&root, &c_rel, &forged);
    let v = refused("seal stripped");
    assert!(v.contains("carries no seal"), "{v}");
    write(&root, &c_rel, &original);
    // (c) a task record created by hand
    write_yaml(
        &root,
        "spec/tasks/TASK-0999.yaml",
        &json!({"id": "TASK-0999", "type": "task", "title": "forged", "status": "ACTIVE", "task_status": "DONE", "class": "documentation", "objective": "forged"}),
    );
    let v = refused("hand-created");
    assert!(v.contains("TASK-0999"), "{v}");
    std::fs::remove_file(root.join("spec/tasks/TASK-0999.yaml")).unwrap();
    // with the repository as gov left it, the close proceeds (work the refused closes generated — sealed, so an OS
    // write in this window — is indexed first, as before any close)
    g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(
        ga.ok(&["task", "close", &a, "--report", &rep])["task_status"],
        "DONE"
    );
}

/// A task record that carried no seal before the claim (written before the OS sealed task records, e.g. by an older
/// release) and that a gov operation rewrites inside the claim window is reported, not refused — the OS does not seal
/// content it never sealed, and the worker did not write it. The record stays unsealed (never blessed).
#[test]
fn a_legacy_unsealed_task_rewritten_by_gov_inside_a_claim_window_is_reported_not_refused() {
    let (root, g) = fresh("int3-legacy");
    let ia = traceable_inputs(&root, "0821");
    write_yaml(
        &root,
        "spec/tasks/TASK-0500.yaml",
        &json!({"id": "TASK-0500", "type": "task", "title": "legacy notes", "status": "ACTIVE", "task_status": "READY", "class": "documentation", "objective": "legacy notes", "allowed_paths": ["docs/**"]}),
    );
    git_commit_all(&root, "inputs and a legacy task record");
    g.ok(&["rebuild-memory", "--incremental"]);
    let a = create(&g, "refactor", "work a", "src/a/**", ia);
    let ga = g.with_session("S-a");
    ga.ok(&["context", "compile", &a]);
    ga.ok(&["task", "claim", &a]);
    // another operator puts the legacy task on hold through gov, inside A's window
    g.with_session("S-other").ok(&[
        "task",
        "status",
        "TASK-0500",
        "BLOCKED",
        "--note",
        "on hold",
    ]);
    let legacy = yaml(&root, "spec/tasks/TASK-0500.yaml");
    assert_eq!(legacy["task_status"], "BLOCKED");
    assert!(
        legacy.get("os_binding").is_none(),
        "the OS never blesses content it did not write: {legacy}"
    );
    let ca = do_and_close(&ga, &root, &a, "src/a/lib.rs");
    assert_eq!(ca["task_status"], "DONE", "{ca}");
    let rpt = yaml(
        &root,
        &format!("spec/reports/{}.yaml", ca["report"].as_str().unwrap()),
    );
    assert!(
        rpt["mutation_evidence"]["os_managed_unbound"]
            .to_string()
            .contains("TASK-0500"),
        "{}",
        rpt["mutation_evidence"]
    );
}

/// WS-2 IP-R3-WS02-07: a CIT that invalidates DONE work generates one revalidation task (`revalidates` -> `TESTS`,
/// task -> task), and that relationship is well typed — the governance suite's `graph_integrity` family and doctor
/// D015 report no ill-typed relationship for it (before the integration fix every such task was a false medium
/// `ill_typed` finding).
#[test]
fn a_cit_invalidating_done_work_leaves_graph_integrity_and_d015_clean() {
    let (root, g) = fresh("int3-reval");
    let inputs = traceable_inputs(&root, "0831");
    git_commit_all(&root, "inputs");
    g.ok(&["rebuild-memory", "--incremental"]);
    let done = create(&g, "refactor", "totals", "src/**", inputs);
    g.ok(&["context", "compile", &done]);
    g.ok(&["task", "claim", &done]);
    let c = do_and_close(&g, &root, &done, "src/totals.rs");
    assert_eq!(c["task_status"], "DONE", "{c}");
    git_commit_all(&root, "done");
    let mf = root.join(".governance-runtime/mf-reval.json");
    std::fs::write(
        &mf,
        json!([{"op": "set_field", "target": "REQ-0831", "field": "statement", "value": "totals are integer cents"}]).to_string(),
    )
    .unwrap();
    let cit = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "state the unit",
        "--trigger",
        "behaviour_change",
        "--targets",
        "REQ-0831",
        "--manifest",
        mf.to_str().unwrap(),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    let sim = g.ok(&["cit", "simulate", &cit]);
    crate::ws03::human_decide(&g, sim["human_gate"].as_str().unwrap(), "A");
    g.ok(&["cit", "approve", &cit, "--method", "human"]);
    g.ok(&["cit", "execute", &cit]);
    let reval: Vec<Value> = g
        .ok(&["task", "list"])
        .as_array()
        .unwrap()
        .iter()
        .filter(|t| {
            t["revalidates"] == json!(done) || t["generated_from"]["source"] == "cit-effect"
        })
        .cloned()
        .collect();
    assert!(!reval.is_empty(), "a revalidation task is generated");
    let rid = reval[0]["id"].as_str().unwrap().to_string();
    assert_eq!(g.ok(&["task", "show", &rid])["revalidates"], json!(done));
    g.ok(&["rebuild-memory", "--incremental"]);
    let o = g.run(&["audit", "--no-persist", "--family", "graph_integrity"]);
    let text = o.envelope.to_string();
    assert!(
        !(text.contains("ill_typed") || text.contains("does not relate in either direction"))
            || !text.contains(&rid),
        "the revalidation relationship is well typed: {text}"
    );
    let (_, d015) = doctor_check(&g, "D015");
    assert!(
        !d015.contains(&rid),
        "D015 does not report the revalidation task: {d015}"
    );
}

/// WS-2 G2 readiness at close (BC-P2-07, `verification::close_readiness`) × WS-5 in-task materiality (BC-P2-13): in
/// the union a task's own hand edit of its feature's readiness is refused earlier, as a material change outside change
/// control (`MATERIAL_CHANGE_REQUIRES_CIT`, WS-2 probe G2.a). The G2 duty still stands: when the feature's
/// pre-implementation readiness regresses through change control inside the claim window (a CIT the owner approved),
/// materiality accepts the write and the close is refused `TASK_READINESS_REGRESSED`.
#[test]
fn a_readiness_regression_made_through_change_control_is_refused_at_close_by_g2() {
    let (root, g) = fresh("int3-g2");
    let na: &[(&str, &str)] = &[
        (
            "representative_test_data",
            "literal order values inside the acceptance test; no dataset",
        ),
        (
            "independent_acceptance_tests",
            "the unit test is the acceptance evidence for this integration test",
        ),
    ];
    let ready = readiness_all_present_except(&[], na);
    write_yaml(
        &root,
        "spec/features/F-0931.yaml",
        &json!({"id": "F-0931", "type": "feature", "title": "Order totals", "status": "ACTIVE", "capability_category": "backend",
                "requirements": ["REQ-0931"], "scenarios": ["SCN-0931"], "acceptance_tests": ["TST-0931"], "readiness": ready}),
    );
    write_yaml(
        &root,
        "spec/requirements/REQ-0931.yaml",
        &json!({"id": "REQ-0931", "type": "requirement", "title": "totals are exact", "status": "ACTIVE", "feature": "F-0931",
                "kind": "functional", "acceptance_criteria": ["2 x 199 = 398"]}),
    );
    write_yaml(
        &root,
        "spec/scenarios/SCN-0931.yaml",
        &json!({"id": "SCN-0931", "type": "scenario", "title": "append two orders", "status": "ACTIVE", "feature": "F-0931",
                "actor": "clerk", "given": ["an empty ledger"], "when": ["two orders are appended"], "then": ["the total is 398"],
                "success_criteria": ["exact"], "failure_criteria": ["drift"],
                "data_requirements_not_applicable": "literal values inside the test"}),
    );
    write_yaml(
        &root,
        "spec/tasks/TST-0931.yaml",
        &json!({"id": "TST-0931", "type": "test-obligation", "title": "totals unit test", "status": "ACTIVE", "feature": "F-0931",
                "family": "unit", "scenario": "SCN-0931"}),
    );
    git_commit_all(&root, "spec");
    g.ok(&["rebuild-memory", "--incremental"]);
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "implementation",
        "--objective",
        "implement totals",
        "--feature",
        "F-0931",
        "--status",
        "READY",
        "--allowed",
        "src/**",
        "--fields",
        &json!({"requirements": ["REQ-0931"], "scenarios": ["SCN-0931"], "acceptance_tests": ["TST-0931"]}).to_string(),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    git_commit_all(&root, "task");
    g.ok(&["context", "compile", &t]);
    g.ok(&["task", "claim", &t]);
    write_file(&root, "src/totals.rs", "pub fn total() -> i64 { 398 }\n");
    // the regression arrives through change control while the task is claimed
    let regressed = readiness_all_present_except(&["security_privacy"], na);
    let mf = root.join(".governance-runtime/mf-g2.json");
    std::fs::write(
        &mf,
        json!([{"op": "set_field", "target": "F-0931", "field": "readiness", "value": regressed}])
            .to_string(),
    )
    .unwrap();
    let cit = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "security review withdrawn",
        "--trigger",
        "acceptance_criteria_change",
        "--targets",
        "F-0931",
        "--manifest",
        mf.to_str().unwrap(),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    let sim = g.ok(&["cit", "simulate", &cit]);
    if let Some(gate) = sim["human_gate"].as_str() {
        crate::ws03::human_decide(&g, gate, "A");
    }
    g.ok(&["cit", "approve", &cit, "--method", "human"]);
    g.ok(&["cit", "execute", &cit]);
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(&g, &root, &t, "g2", "totals", &["src/totals.rs"], "passed");
    let c = g.run(&["task", "close", &t, "--report", &rep]);
    assert!(!c.ok(), "{}", c.envelope);
    assert_eq!(c.error_code(), "TASK_READINESS_REGRESSED", "{}", c.envelope);
}
