//! Fixture 1 — greenfield Rust project: ideation → readiness gaps → DAG → independent tests → CIT → checkpoints →
//! routing → product verification → fresh-agent continuation.
use crate::common::*;
use serde_json::json;

#[test]
fn greenfield_end_to_end() {
    let (root, g) = setup_fixture("greenfield", "greenfield", "S-alpha");
    let r = g.ok(&[
        "init",
        "--name",
        "orders-ledger",
        "--alias",
        "fx-green",
        "--intent",
        "Append-only order ledger with totals",
    ]);
    assert_eq!(r["version"], gov_runtime::VERSION);
    for f in [
        "governance/framework.lock",
        "governance/kernel/KERNEL_MANIFEST.json",
        "governance/kernel/constitution/CONSTITUTION.md",
        "governance/project/REPOSITORY_CONTRACT.yaml",
        "governance/generated/index-manifest.json",
        "governance/generated/adapter-manifest.json",
        "governance/generated/tool-registry.json",
        "governance/generated/adapters/generic/SYSTEM_INSTRUCTION.md",
        "framework.json",
        "spec/product/PRJ-0001.yaml",
        ".gitignore",
    ] {
        assert!(exists(&root, f), "{f} missing after init");
    }
    assert!(read(&root, ".gitignore").contains(".governance-runtime/"));
    assert_eq!(r["adapters"], 5);
    assert!(
        r["index"]["ecosystems"].as_u64().unwrap() >= 1,
        "Cargo ecosystem must be detected"
    );
    assert_eq!(
        r["conformance"]["verdict"], "HEALTHY",
        "{}",
        r["conformance"]
    );
    let m = json(&root, "governance/generated/index-manifest.json");
    assert_eq!(m["embedder"]["id"], "hashed-ngram");
    assert!(m["artifacts"]
        .as_object()
        .unwrap()
        .contains_key("src/lib.rs"));
    // --- specification: feature with readiness gaps, scenario, requirement ---
    write_yaml(
        &root,
        "spec/features/F-0001.yaml",
        &json!({"id": "F-0001", "type": "feature", "title": "Order totals", "status": "ACTIVE", "capability_category": "backend", "requirements": ["REQ-0001"], "scenarios": ["SCN-0001"],
        "readiness": readiness_all_present_except(&["representative_test_data", "performance_capacity", "independent_acceptance_tests"], &[("ux_interactions", "library crate, no UI"), ("cost_constraints", "no infrastructure cost")])}),
    );
    write_yaml(
        &root,
        "spec/requirements/REQ-0001.yaml",
        &json!({"id": "REQ-0001", "type": "requirement", "title": "Ledger totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001", "kind": "functional", "acceptance_criteria": ["total_cents sums quantity*unit_cents"]}),
    );
    write_yaml(
        &root,
        "spec/scenarios/SCN-0001.yaml",
        &json!({"id": "SCN-0001", "type": "scenario", "title": "Append two orders and total", "status": "ACTIVE", "feature": "F-0001", "actor": "clerk", "given": ["an empty ledger"], "when": ["two orders are appended"], "then": ["total_cents is 399"], "success_criteria": ["exact total"], "failure_criteria": ["duplicate ids accepted"]}),
    );
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "implementation",
        "--objective",
        "Implement Ledger totals",
        "--feature",
        "F-0001",
        "--status",
        "READY",
        "--allowed",
        "src/**,tests/**",
        "--fields",
        r#"{"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "role": "backend-engineer"}"#,
    ]);
    let impl_id = t["id"].as_str().unwrap().to_string();
    let dag = g.ok(&["task", "dag"]);
    assert!(
        dag["blocked"]
            .as_array()
            .unwrap()
            .iter()
            .any(|b| b["task"] == impl_id && b["reasons"].to_string().contains("readiness")),
        "implementation must be blocked by missing pre-implementation cells: {dag}"
    );
    // --- readiness generates work in the same DAG ---
    let plan = g.ok(&["readiness", "plan", "F-0001"]);
    let created: Vec<String> = plan["created_tasks"]
        .as_array()
        .unwrap()
        .iter()
        .map(|x| x.as_str().unwrap().to_string())
        .collect();
    assert_eq!(created.len(), 3, "{plan}");
    assert!(plan["implementation_tasks_blocked"]
        .as_array()
        .unwrap()
        .iter()
        .any(|x| x == &impl_id));
    let classes: Vec<String> = created
        .iter()
        .map(|id| {
            g.ok(&["task", "show", id])["class"]
                .as_str()
                .unwrap()
                .to_string()
        })
        .collect();
    assert!(
        classes.contains(&"data".into())
            && classes.contains(&"test-design".into())
            && classes.contains(&"performance".into()),
        "{classes:?}"
    );
    // simulate doing the gap work: claim + close each with evidence; then mark cells PRESENT
    for id in &created {
        g.ok(&["task", "claim", id]);
        let rep = write_report(
            &root,
            id,
            "provided readiness cell",
            &[],
            "not_applicable_with_reason",
        );
        g.ok(&["rebuild-memory", "--incremental"]);
        g.ok(&["task", "close", id, "--report", &rep]);
    }
    let mut f = yaml(&root, "spec/features/F-0001.yaml");
    f["readiness"] = readiness_all_present_except(
        &[],
        &[
            ("ux_interactions", "library crate, no UI"),
            ("cost_constraints", "no infrastructure cost"),
        ],
    );
    f["acceptance_tests"] = json!(["TST-0001"]);
    write_yaml(&root, "spec/features/F-0001.yaml", &f);
    // independent test author records the obligation
    write_yaml(
        &root,
        "spec/tasks/TST-0001.yaml",
        &json!({"id": "TST-0001", "type": "test-obligation", "title": "Ledger acceptance tests", "status": "ACTIVE", "feature": "F-0001", "scenario": "SCN-0001", "family": "acceptance", "test_path": "tests/ledger_test.rs", "author_role": "independent-test-designer", "independent_of_implementer": true, "data_provenance": "synthetic"}),
    );
    let rp = g.ok(&["task", "replan"]);
    assert!(
        rp["runnable"]
            .as_array()
            .unwrap()
            .iter()
            .any(|x| x == &impl_id),
        "impl task must become READY after readiness satisfied: {rp}"
    );
    // --- continue: context packet is deterministic ---
    // the task contract designates backend-engineer, and the designated role binds who may claim and close it
    // (BC-P2-14): the orchestrator is refused, the designated role continues the work
    assert_eq!(
        g.err(&["task", "claim", &impl_id]).error_code(),
        "ROLE_NOT_DESIGNATED"
    );
    let be = g.with_role("backend-engineer");
    let c1 = be.ok(&["continue", "--claim"]);
    assert_eq!(c1["status"], "NEXT_WORK");
    assert_eq!(c1["task"], impl_id);
    assert_eq!(c1["routing"]["minimum_tier"], "T2");
    let c2 = g.ok(&["context", "compile", &impl_id]);
    let c3 = g.ok(&["context", "compile", &impl_id]);
    assert_eq!(
        c2["deterministic_hash"], c3["deterministic_hash"],
        "deterministic authority block must be reproducible"
    );
    assert_ne!(
        c1["context_packet"]["deterministic_hash"],
        serde_json::Value::Null
    );
    assert!(c2["deterministic_authority"]["prohibited_writes"]
        .as_array()
        .unwrap()
        .iter()
        .any(|x| x == "governance/kernel/**"));
    assert!(c2["deterministic_authority"]["governing_requirements"]
        .as_array()
        .unwrap()
        .iter()
        .any(|x| x["id"] == "REQ-0001"));
    // --- CIT: interface/behaviour change requires a human gate; gate must be presented before approval ---
    let mf = root.join(".governance-runtime/cit-manifest.json");
    std::fs::write(&mf, json!([{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["total_cents sums quantity*unit_cents", "totals never overflow u64 (checked arithmetic)"]}]).to_string()).unwrap();
    let cit = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "Use checked arithmetic for totals and document overflow behaviour",
        "--trigger",
        "behaviour_change",
        "--targets",
        "REQ-0001",
        "--manifest",
        mf.to_str().unwrap(),
    ]);
    let cit_id = cit["id"].as_str().unwrap().to_string();
    let sim = g.ok(&["cit", "simulate", &cit_id]);
    assert_eq!(sim["impact"]["radius"], "R2");
    assert_eq!(sim["impact"]["human_gate_required"], true);
    assert!(
        sim["impact"]["affected_tasks"]
            .as_array()
            .unwrap()
            .iter()
            .any(|x| x == &impl_id),
        "task governed by REQ-0001 must be in the impact set: {}",
        sim["impact"]
    );
    let gate = sim["human_gate"].as_str().unwrap().to_string();
    let e = g.err(&[
        "cit", "approve", &cit_id, "--by", "owner", "--method", "human",
    ]);
    assert_eq!(e.error_code(), "GATE_NOT_PRESENTED");
    let e2 = g.err(&["decide", &gate, "--option", "A", "--by", "owner"]);
    assert_eq!(e2.error_code(), "GATE_NOT_PRESENTED");
    let pres = g.ok(&["gate", "present", &gate]);
    assert!(pres["chat_text"]
        .as_str()
        .unwrap()
        .contains("HUMAN DECISION GATE"));
    let dec = crate::ws03::human_decide(&g, &gate, "A");
    let decision = dec["decision"].as_str().unwrap().to_string();
    let ap = g.ok(&[
        "cit", "approve", &cit_id, "--by", "owner", "--method", "human",
    ]);
    assert_eq!(
        ap["decision"], decision,
        "approval must reuse the gate's decision"
    );
    let ex = g.ok(&["cit", "execute", &cit_id]);
    assert_eq!(ex["cit_status"], "COMMITTED");
    assert!(g.ok(&["task", "show", &impl_id])["retest_required"] == true);
    assert!(
        yaml(&root, "spec/requirements/REQ-0001.yaml")["acceptance_criteria"]
            .as_array()
            .unwrap()
            .len()
            == 2
    );
    // --- product verification runs the native toolchain (cargo test) ---
    let pv = g.ok(&["verify", "product"]);
    assert_eq!(pv["status"], "passed", "{pv}");
    assert!(pv["source"].as_str().unwrap().contains("rust-cargo"));
    // --- routing evidence + telemetry ---
    let rec = root.join(".governance-runtime/route-ev.json");
    std::fs::write(&rec, json!({"model": "model-alias-large", "provider": "provider-alias", "task_class": "implementation", "reasoning_effort": "medium", "cost": 0.12, "latency_ms": 900, "pass": true, "repair_count": 0, "reviewer_findings": 1}).to_string()).unwrap();
    g.ok(&["route", "--record", rec.to_str().unwrap()]);
    let rr = g.ok(&["route", "--report"]);
    assert_eq!(rr["rows"][0]["task_class"], "implementation");
    let tel = g.ok(&["telemetry", "summary"]);
    assert!(tel["events"].as_u64().unwrap() > 5);
    // --- close implementation task with evidence; checkpoint written ---
    let rep = write_report(
        &root,
        "impl",
        "Implemented totals with checked arithmetic",
        &["src/lib.rs"],
        "passed",
    );
    g.ok(&["rebuild-memory", "--incremental"]);
    let cl = be.ok(&["task", "close", &impl_id, "--report", &rep]);
    assert!(cl["checkpoint"].as_str().unwrap().starts_with("CKPT-"));
    let wd = g.ok(&[
        "checkpoint",
        "watchdog",
        "--utilisation",
        "0.9",
        "--next-action",
        "gov continue",
    ]);
    assert_eq!(wd["fired"], true);
    // --- fresh agent, new session: reconstruct state without prior conversation ---
    let fresh = g.with_session("S-fresh");
    let st = fresh.ok(&["status"]);
    assert_eq!(st["tasks"]["counts"]["done"], 4);
    assert!(st["latest_checkpoint"]["id"]
        .as_str()
        .unwrap()
        .starts_with("CKPT-"));
    assert!(st["fresh_agent_reads"].as_array().unwrap().len() <= 25);
    let cont = fresh.ok(&["continue"]);
    assert!(cont["status"] == "NO_RUNNABLE_WORK" || cont["status"] == "NEXT_WORK");
    let sk = g.ok(&["skills", "resolve", &impl_id]);
    assert!(sk["candidates_by_class_role"]
        .as_array()
        .unwrap()
        .iter()
        .any(|s| s["id"] == "SKL-BACKEND-IMPL"));
    g.ok(&["adapters", "verify"]);
    let au = g.ok(&["audit"]);
    assert_ne!(au["verdict"], "UNHEALTHY", "{}", au["findings"]);
    assert_eq!(au["counts"]["critical"], 0);
    assert_ne!(doctor_verdict(&g), "UNHEALTHY");
    git_commit_all(&root, "greenfield certified state");
}
