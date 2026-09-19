//! Fixture 7 — failure injection: each fault is detected by doctor/suite and repaired by a recovery primitive.
use crate::common::*;
use serde_json::json;

#[test]
fn injected_failures_are_detected_and_recovered() {
    let (root, g) = setup_fixture("greenfield", "failinj", "S-inj");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "orders-ledger",
        "--alias",
        "fx-inj",
        "--intent",
        "ledger",
    ]);
    assert_ne!(doctor_verdict(&g), "UNHEALTHY");
    // 1. corrupt runtime DB
    std::fs::write(
        root.join(".governance-runtime/state.db"),
        b"this is not a database",
    )
    .unwrap();
    for f in ["state.db-wal", "state.db-shm"] {
        let _ = std::fs::remove_file(root.join(".governance-runtime").join(f));
    }
    let (ok, msg) = doctor_check(&g, "D009");
    assert!(!ok, "{msg}");
    let rec = g.ok(&["recover"]);
    assert!(rec["actions"].to_string().contains("rebuilt_runtime"));
    assert!(doctor_check(&g, "D009").0);
    // 2. interrupted CIT execution (EXECUTING with snapshot, file half-changed)
    let original = read(&root, "spec/now/NOW.md");
    let mf = root.join(".governance-runtime/m.json");
    std::fs::write(&mf, json!([{"op": "write_file", "path": "spec/now/NOW.md", "content": "# NOW\nchanged by CIT\n"}]).to_string()).unwrap();
    let cit = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "editorial update of NOW",
        "--trigger",
        "editorial",
        "--manifest",
        mf.to_str().unwrap(),
    ]);
    let cid = cit["id"].as_str().unwrap().to_string();
    let sim = g.ok(&["cit", "simulate", &cid]);
    assert_eq!(
        sim["impact"]["human_gate_required"], false,
        "editorial R0 change is auto-approvable"
    );
    g.ok(&["cit", "approve", &cid, "--by", "agent", "--method", "auto"]);
    let snap = root
        .join(".governance-runtime/cit")
        .join(&cid)
        .join("snapshot/spec/now");
    std::fs::create_dir_all(&snap).unwrap();
    std::fs::write(snap.join("NOW.md"), &original).unwrap();
    gov_runtime::util::write_json(&root.join(".governance-runtime/cit").join(&cid).join("snapshot.json"), &json!({"cit": cid, "files": ["spec/now/NOW.md"], "created_paths": [], "taken_at": "x", "commit": "x"})).unwrap();
    let mut c = yaml(&root, &format!("spec/decisions/{cid}.yaml"));
    c["cit_status"] = json!("EXECUTING");
    c["execution"] = json!({"started": "x", "session": "dead"});
    write_yaml(&root, &format!("spec/decisions/{cid}.yaml"), &c);
    write(&root, "spec/now/NOW.md", "# NOW\nhalf-applied garbage\n");
    let (ok, msg) = doctor_check(&g, "D016");
    assert!(!ok, "{msg}");
    let rec2 = g.ok(&["recover"]);
    assert!(rec2["actions"].to_string().contains("rolled_back"));
    assert_eq!(
        read(&root, "spec/now/NOW.md"),
        original,
        "interrupted mutation must be rolled back to the snapshot"
    );
    assert_eq!(
        yaml(&root, &format!("spec/decisions/{cid}.yaml"))["cit_status"],
        "ROLLED_BACK"
    );
    assert!(doctor_check(&g, "D016").0);
    // 3. stale index blocks task close
    g.ok(&["rebuild-memory"]);
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "docs",
        "--status",
        "READY",
    ]);
    let tid = t["id"].as_str().unwrap().to_string();
    g.ok(&["task", "claim", &tid]);
    let rep = write_report(
        &root,
        "t",
        "wrote docs",
        &["README.md"],
        "not_applicable_with_reason",
    );
    write(&root, "spec/now/NOW.md", "# NOW\nedited after indexing\n");
    let (ok, _) = doctor_check(&g, "D010");
    assert!(!ok);
    assert_eq!(
        g.err(&["task", "close", &tid, "--report", &rep])
            .error_code(),
        "INDEX_STALE"
    );
    g.ok(&["rebuild-memory", "--incremental"]);
    // BC-P2-20 (P2-AR-0026): the close that succeeds carries the worker's consumption receipt
    let rep = crate::ws05::receipt(
        &g,
        &root,
        &tid,
        "t2",
        "wrote docs",
        &["README.md"],
        "not_applicable_with_reason",
    );
    g.ok(&["task", "close", &tid, "--report", &rep]);
    // 4. expired claim
    {
        let p = gov_runtime::Project::open(&root);
        let cs = gov_runtime::memory::claims::ClaimsStore::open(&p).unwrap();
        cs.insert_raw(
            "TASK-0001",
            "S-dead",
            "x",
            "2020-01-01T00:00:00Z",
            "2020-01-01T01:00:00Z",
        )
        .unwrap();
    }
    let (ok, _) = doctor_check(&g, "D017");
    assert!(!ok);
    assert_eq!(g.ok(&["claims", "sweep"])["swept"], 1);
    // 5. freeze left on: mutations refused with exit code 4
    g.ok(&["freeze-writes", "--reason", "incident"]);
    let e = g.err(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "x",
    ]);
    assert_eq!(e.error_code(), "FROZEN");
    assert_eq!(e.code, 4);
    let (ok, _) = doctor_check(&g, "D018");
    assert!(!ok);
    g.ok(&["resume"]);
    assert!(doctor_check(&g, "D018").0);
    // 6. kernel tampered in place
    let kp = "governance/kernel/policies/BUDGET_POLICY.yaml";
    let orig_k = read(&root, kp);
    write(&root, kp, &(orig_k.clone() + "\ntampered: true\n"));
    let d = g.run(&["doctor"]);
    assert!(!d.ok());
    assert_eq!(d.code, 3);
    assert_eq!(d.details()["verdict"], "UNHEALTHY");
    assert!(d.details()["checks"]
        .as_array()
        .unwrap()
        .iter()
        .any(|c| c["id"] == "D003" && c["ok"] == false));
    let au = g.run(&["audit", "--no-persist"]);
    assert!(!au.ok());
    assert!(au.details()["findings"]
        .as_array()
        .unwrap()
        .iter()
        .any(|f| f["family"] == "mutation_scope" && f["severity"] == "critical"));
    g.ok(&["kernel", "reinstall", "--source", signed_source()]);
    assert_eq!(read(&root, kp), orig_k);
    assert!(doctor_check(&g, "D003").0);
    // 7. invalid policy override
    let mut pp = yaml(&root, "governance/project/PROJECT_POLICY.yaml");
    pp["policy_overrides"] = json!({"NOPE_POLICY.x": 1});
    write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    let (ok, _) = doctor_check(&g, "D007");
    assert!(!ok);
    pp["policy_overrides"] = json!({});
    write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    assert!(doctor_check(&g, "D007").0);
    // 8. secret planted in product source: flagged critical, never indexed
    write(
        &root,
        "src/leak.rs",
        "pub const KEY: &str = \"AKIAIOSFODNN7EXAMPLE\";\n",
    );
    let d = g.run(&["doctor"]);
    assert!(d.details()["checks"]
        .as_array()
        .unwrap()
        .iter()
        .any(|c| c["id"] == "D011" && c["ok"] == false && c["severity"] == "critical"));
    let rb = g.ok(&["rebuild-memory"]);
    assert!(rb["secret_blocked"]
        .as_array()
        .unwrap()
        .iter()
        .any(|x| x["path"] == "src/leak.rs"));
    assert!(!indexed_paths(&root).contains(&"src/leak.rs".to_string()));
    assert!(
        chunk_texts(&root)
            .iter()
            .all(|t| !t.contains("AKIAIOSFODNN7EXAMPLE")),
        "secret must never reach the index (INV-009)"
    );
    std::fs::remove_file(root.join("src/leak.rs")).unwrap();
    g.ok(&["rebuild-memory"]);
    // 9. task depending on a missing task
    g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "orphan",
        "--deps",
        "TASK-9999",
    ]);
    let dag = g.ok(&["task", "dag"]);
    assert!(dag["missing_dependencies"]
        .as_array()
        .unwrap()
        .iter()
        .any(|m| m["dependency"] == "TASK-9999"));
    let au = g.run(&["audit", "--no-persist"]);
    let f = if au.ok() { au.result() } else { au.details() };
    assert!(f["findings"]
        .as_array()
        .unwrap()
        .iter()
        .any(|x| x["family"] == "graph_integrity"
            && x["message"].as_str().unwrap().contains("TASK-9999")));
    // 10. missing overlay file
    std::fs::rename(
        root.join("governance/project/DATA_SENSITIVITY.yaml"),
        root.join("governance/project/DATA_SENSITIVITY.yaml.bak"),
    )
    .unwrap();
    let (ok, _) = doctor_check(&g, "D006");
    assert!(!ok);
    std::fs::rename(
        root.join("governance/project/DATA_SENSITIVITY.yaml.bak"),
        root.join("governance/project/DATA_SENSITIVITY.yaml"),
    )
    .unwrap();
    assert!(doctor_check(&g, "D006").0);
    // 11. a failing embed plugin is a clear error, never a silent fallback; the previous index survives
    write_yaml(
        &root,
        "governance/project/plugins/bad.yaml",
        &json!({"plugin_id": "bad-embed", "capability": "embed", "version": "1", "command": ["/bin/false"]}),
    );
    let mut pp = yaml(&root, "governance/project/PROJECT_POLICY.yaml");
    pp["policy_overrides"] = json!({"MEMORY_POLICY.embedding.provider": "bad-embed"});
    write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    let e = g.err(&["rebuild-memory"]);
    assert!(
        e.error_code().starts_with("PLUGIN_") || e.error_code() == "EMBEDDER_BAD_OUTPUT",
        "{}",
        e.error_code()
    );
    assert!(exists(&root, ".governance-runtime/state.db"));
    let (ok25, _) = doctor_check(&g, "D025");
    assert!(!ok25, "pin (bad-embed) differs from the live index");
    pp["policy_overrides"] = json!({});
    write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    std::fs::remove_file(root.join("governance/project/plugins/bad.yaml")).unwrap();
    assert!(doctor_check(&g, "D025").0);
    // 12. a gate that exists only in a file is not presented (INV-008)
    let gate = g.ok(&[
        "gate",
        "create",
        "--question",
        "Ship it?",
        "--fields",
        &crate::ws03::package(json!({})),
    ]);
    let gid = gate["id"].as_str().unwrap().to_string();
    assert_eq!(
        g.err(&["decide", &gid, "--option", "A"]).error_code(),
        "GATE_NOT_PRESENTED"
    );
    let (ok, _) = doctor_check(&g, "D019");
    assert!(!ok);
    g.ok(&["gate", "present", &gid]);
    crate::ws03::human_decide(&g, &gid, "A");
    // 13. handoff that returns files outside its authority is rejected (mutation scope)
    let t2 = g.ok(&[
        "task",
        "create",
        "--class",
        "implementation",
        "--objective",
        "scoped work",
        "--status",
        "READY",
        "--allowed",
        "src/**",
    ]);
    let h = g.ok(&[
        "handoff",
        "create",
        "--to-role",
        "backend-engineer",
        "--task",
        t2["id"].as_str().unwrap(),
    ]);
    let ret = root.join(".governance-runtime/ret.json");
    std::fs::write(&ret, json!({"task": t2["id"], "status": "success", "work_completed": "x", "files_changed": ["governance/kernel/KERNEL.yaml"], "evidence": [], "tests": {"status": "passed"}, "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": [], "recommended_next_action": "close"}).to_string()).unwrap();
    assert_eq!(
        g.err(&[
            "handoff",
            "return",
            h["id"].as_str().unwrap(),
            "--file",
            ret.to_str().unwrap()
        ])
        .error_code(),
        "MUTATION_SCOPE_VIOLATION"
    );
    assert_eq!(
        g.err(&[
            "handoff",
            "create",
            "--to-role",
            "orchestrator",
            "--task",
            t2["id"].as_str().unwrap()
        ])
        .error_code(),
        "INV_014"
    );
    g.ok(&["rebuild-memory"]);
    assert_ne!(doctor_verdict(&g), "UNHEALTHY");
}
