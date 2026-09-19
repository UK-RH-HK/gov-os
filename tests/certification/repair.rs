//! Builder regression tests for every root cause repaired after the independent verification of 4.1.2
//! (release/verification/4.1.2/INDEPENDENT_VERIFICATION_REPORT.md §11). Each test names the finding it covers.
use crate::common::*;
use serde_json::json;
use std::path::Path;

fn serve_embed_plugin(root: &Path, id: &str, reverse: bool) {
    let mut cmd = vec![
        gov_bin().to_string_lossy().to_string(),
        "capabilities".into(),
        "serve-embed".into(),
        "--id".into(),
        id.into(),
    ];
    if reverse {
        cmd.push("--reverse".into());
    }
    write_yaml(
        root,
        &format!("governance/project/plugins/{id}.yaml"),
        &json!({"plugin_id": id, "capability": "embed", "version": "1", "command": cmd, "languages": []}),
    );
}
fn set_overrides(root: &Path, over: serde_json::Value) {
    let mut pp = yaml(root, "governance/project/PROJECT_POLICY.yaml");
    pp["policy_overrides"] = over;
    write_yaml(root, "governance/project/PROJECT_POLICY.yaml", &pp);
}
fn vector_groups(root: &Path) -> Vec<(String, i64)> {
    let d = db(root);
    let mut s = d
        .conn
        .prepare("SELECT embedder, dim FROM vectors GROUP BY embedder, dim")
        .unwrap();
    s.query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, i64>(1)?)))
        .unwrap()
        .map(|x| x.unwrap())
        .collect()
}

/// C1 / HV-01: the query is embedded with the pinned implementation; no silent fallback when it is unavailable.
#[test]
fn embedder_replaceable_end_to_end_and_no_silent_fallback() {
    let (root, g) = setup_fixture("greenfield", "rep-embed", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "e",
        "--alias",
        "e-alias",
        "--skip-index",
    ]);
    serve_embed_plugin(&root, "reversed-builtin", true);
    set_overrides(
        &root,
        json!({"MEMORY_POLICY.embedding.provider": "reversed-builtin", "MEMORY_POLICY.embedding.dimensions": 8}),
    );
    let titles = [
        "Order totals are exact integer cents",
        "Ledger rejects duplicate order identifiers",
        "Clerk appends two orders and reads the total",
        "Gateway retries are capped at five attempts",
    ];
    for (i, t) in titles.iter().enumerate() {
        write_yaml(
            &root,
            &format!("spec/requirements/REQ-{:04}.yaml", i + 1),
            &json!({"id": format!("REQ-{:04}", i + 1), "type": "requirement", "title": t, "status": "ACTIVE", "kind": "functional", "acceptance_criteria": [format!("{t} and nothing else")]}),
        );
    }
    let r = g.ok(&["rebuild-memory"]);
    assert_eq!(r["embedder"]["id"], "reversed-builtin");
    assert_eq!(r["embedder"]["source"], "plugin");
    assert_eq!(r["embedder"]["dimensions"], 8);
    assert_eq!(
        vector_groups(&root),
        vec![("reversed-builtin".to_string(), 8)]
    );
    assert_eq!(
        json(&root, "governance/generated/index-manifest.json")["embedder"]["id"],
        "reversed-builtin"
    );
    for (i, t) in titles.iter().enumerate() {
        let q = g.ok(&["memory", "query", t, "--route", "semantic", "--k", "4"]);
        assert_eq!(
            q["embedder"]["id"], "reversed-builtin",
            "query must be embedded with the pinned plugin"
        );
        assert_eq!(
            q["hits"][0]["artifact_id"],
            format!("REQ-{:04}", i + 1),
            "exact-title query must rank its own record first: {}",
            q["hits"]
        );
    }
    // remove the plugin: declared but unavailable => errors, never a fallback to the built-in embedder
    std::fs::remove_file(root.join("governance/project/plugins/reversed-builtin.yaml")).unwrap();
    assert_eq!(
        g.err(&["memory", "query", titles[0], "--route", "semantic"])
            .error_code(),
        "EMBEDDER_UNAVAILABLE"
    );
    let manifest_before =
        json(&root, "governance/generated/index-manifest.json")["manifest_hash"].clone();
    assert_eq!(
        g.err(&["rebuild-memory"]).error_code(),
        "EMBEDDER_UNAVAILABLE"
    );
    assert!(
        exists(&root, ".governance-runtime/state.db"),
        "a failed build must not destroy the previous index"
    );
    assert_eq!(
        json(&root, "governance/generated/index-manifest.json")["manifest_hash"],
        manifest_before
    );
    // policy pin differs from the live index => semantic route refuses with EMBEDDER_MISMATCH
    set_overrides(&root, json!({}));
    assert_eq!(
        g.err(&["memory", "query", titles[0], "--route", "semantic"])
            .error_code(),
        "EMBEDDER_MISMATCH"
    );
    let (ok, _) = doctor_check(&g, "D025");
    assert!(!ok);
}

/// H1 / HV-07: a pin change invalidates the index, blocks task close, and incremental builds escalate to full.
#[test]
fn embedder_pin_change_escalates_to_full_rebuild_without_mixed_index() {
    let (root, g) = setup_fixture("greenfield", "rep-pin", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "p",
        "--alias",
        "p-alias",
    ]);
    assert_eq!(
        vector_groups(&root),
        vec![("hashed-ngram".to_string(), 512)]
    );
    set_overrides(
        &root,
        json!({"MEMORY_POLICY.embedding.dimensions": 64, "MEMORY_POLICY.embedding.version": "2"}),
    );
    let fr = g.ok(&["memory", "freshness"]);
    assert_eq!(fr["fresh"], false);
    assert!(!fr["pin_mismatch"].as_array().unwrap().is_empty(), "{fr}");
    let (ok10, _) = doctor_check(&g, "D010");
    assert!(!ok10);
    let (ok25, msg) = doctor_check(&g, "D025");
    assert!(!ok25, "{msg}");
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "x",
        "--status",
        "READY",
    ]);
    g.ok(&["task", "claim", t["id"].as_str().unwrap()]);
    let rep = write_report(&root, "pin", "w", &[], "not_applicable_with_reason");
    assert_eq!(
        g.err(&["task", "close", t["id"].as_str().unwrap(), "--report", &rep])
            .error_code(),
        "INDEX_PIN_MISMATCH"
    );
    let r = g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(r["mode"], "full");
    assert!(
        r["escalated_to_full"]
            .as_str()
            .unwrap()
            .contains("pin change"),
        "{r}"
    );
    assert_eq!(
        vector_groups(&root),
        vec![("hashed-ngram".to_string(), 64)],
        "no heterogeneous index"
    );
    assert_eq!(
        json(&root, "governance/generated/index-manifest.json")["embedder"]["dimensions"],
        64
    );
    assert!(doctor_check(&g, "D025").0 && doctor_check(&g, "D010").0);
    assert!(g.ok(&["memory", "freshness"])["fresh"] == true);
}

/// H7 / HV-02: a pinned reranker is invoked between fusion and filtering; absence of a pinned plugin is an error.
#[test]
fn reranker_hook_invoked_and_never_silently_skipped() {
    let (root, g) = setup_fixture("greenfield", "rep-rerank", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "r",
        "--alias",
        "r-alias",
        "--skip-index",
    ]);
    let marker = root.join(".governance-runtime/RERANK_INVOKED");
    std::fs::create_dir_all(marker.parent().unwrap()).unwrap();
    write(&root, "rerank.sh", &format!("#!/usr/bin/env bash\nREQ=$(cat)\ntouch '{}'\nfirst=$(printf '%s' \"$REQ\" | sed -n 's/.*\"id\":\"\\([^\"]*\\)\".*/\\1/p' | head -n1)\nprintf '{{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{{\"id\":\"marker-reranker\",\"version\":\"1\"}},\"outputs\":{{\"scores\":[{{\"id\":\"%s\",\"score\":9.0}}]}}}}' \"$first\"\n", marker.display()));
    use std::os::unix::fs::PermissionsExt;
    std::fs::set_permissions(
        root.join("rerank.sh"),
        std::fs::Permissions::from_mode(0o755),
    )
    .unwrap();
    write_yaml(
        &root,
        "governance/project/plugins/rerank.yaml",
        &json!({"plugin_id": "marker-reranker", "capability": "rerank", "version": "1", "command": [root.join("rerank.sh").to_string_lossy()], "languages": []}),
    );
    // BC-P2-39 (repair iteration 1, WS-7): an executable plugin runs only when registered against a gate raised for it
    crate::ws07::register_approved(&g, &root.join("governance/project/plugins/rerank.yaml"));
    // the registration is written under the plugin id; the hand-written copy would be a second, unregistered
    // declaration of the same id
    std::fs::remove_file(root.join("governance/project/plugins/rerank.yaml")).unwrap();
    set_overrides(
        &root,
        json!({"MEMORY_POLICY.reranker.provider": "marker-reranker"}),
    );
    let r = g.ok(&["rebuild-memory"]);
    assert_eq!(r["reranker"]["provider"], "marker-reranker");
    let q = g.ok(&[
        "memory",
        "query",
        "why was the ledger designed with integer cents",
        "--k",
        "5",
    ]);
    assert!(
        marker.exists(),
        "reranker plugin must be invoked during retrieval"
    );
    assert_eq!(q["reranker"]["provider"], "marker-reranker");
    assert!(q["hits"]
        .as_array()
        .unwrap()
        .iter()
        .any(|h| h["rerank_score"].as_f64() == Some(9.0)));
    std::fs::remove_file(root.join("governance/project/plugins/marker-reranker.yaml")).unwrap();
    assert_eq!(
        g.err(&["memory", "query", "integer cents", "--k", "3"])
            .error_code(),
        "RERANKER_UNAVAILABLE"
    );
}

/// H7 / HV-20: a benchmark compares candidates with metrics and records a research record; selection is a decision.
#[test]
fn benchmark_records_evidence_and_selection_pins_through_decision() {
    let (root, g) = setup_fixture("greenfield", "rep-bench", "S-rep");
    let r = g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "b",
        "--alias",
        "b-alias",
    ]);
    assert!(
        r["heldout_generated"].as_u64().unwrap() >= 5,
        "starter held-out set must be generated at init: {r}"
    );
    let v = g.ok(&["memory", "verify"]);
    assert_eq!(v["measured"], true);
    assert_eq!(v["status"], "PASS", "{v}");
    serve_embed_plugin(&root, "gov-builtin-embed", false);
    let b = g.ok(&[
        "memory",
        "benchmark",
        "--candidate",
        "current",
        "--candidate",
        "builtin:64",
        "--candidate",
        "plugin:gov-builtin-embed:32",
        "--record",
    ]);
    let rows = b["rows"].as_array().unwrap();
    assert_eq!(rows.len(), 3);
    for row in rows {
        assert_eq!(row["usable"], true, "{row}");
        for m in [
            "recall_at_k",
            "mrr",
            "precision_at_k",
            "avg_query_latency_ms",
            "index_ms",
            "vectors",
        ] {
            assert!(row.get(m).is_some(), "metric {m} missing");
        }
    }
    let res_id = b["research_record"].as_str().unwrap().to_string();
    assert!(exists(&root, &format!("spec/research/{res_id}.yaml")));
    // BC-P2-30 (A0-D5-02, WS-6 round 2): a profile change pins governance/project/** (radius R5), so the first call
    // raises the change-control gate and applies nothing; it is applied only on the owner-signed answer to that gate.
    let pending = g.ok(&[
        "memory",
        "select",
        "builtin:64",
        "--research",
        &res_id,
        "--by",
        "owner",
    ]);
    assert_eq!(pending["applied"], false, "{pending}");
    let gid = pending["human_gate"].as_str().unwrap().to_string();
    crate::ws03::human_decide(&g, &gid, "A");
    let sel = g.ok(&[
        "memory",
        "select",
        "builtin:64",
        "--research",
        &res_id,
        "--gate",
        &gid,
    ]);
    assert_eq!(sel["applied"], true, "{sel}");
    let did = sel["decision"].as_str().unwrap();
    assert!(exists(&root, &format!("spec/decisions/{did}.yaml")));
    assert_eq!(
        yaml(&root, "governance/project/PROJECT_POLICY.yaml")["policy_overrides"]
            ["MEMORY_POLICY.embedding.dimensions"],
        64
    );
    assert_eq!(vector_groups(&root), vec![("hashed-ngram".to_string(), 64)]);
    assert!(g.ok(&["memory", "freshness"])["fresh"] == true);
    // the live index still answers queries after re-pinning
    g.ok(&["memory", "query", "orders ledger", "--k", "3"]);
}

/// H7 / HV-20: zero held-out queries is UNMEASURED, never green.
#[test]
fn unmeasured_memory_recall_is_not_green() {
    let (root, g) = setup_fixture("greenfield", "rep-unmeasured", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "u",
        "--alias",
        "u-alias",
        "--skip-index",
    ]);
    g.ok(&["rebuild-memory"]);
    assert_eq!(
        yaml(&root, "governance/tests/memory/heldout.yaml")["queries"]
            .as_array()
            .unwrap()
            .len(),
        0
    );
    let v = g.ok(&["memory", "verify"]);
    assert_eq!(v["measured"], false);
    assert_eq!(v["pass"], false);
    assert_eq!(v["status"], "UNMEASURED");
    let au = g.run(&["audit", "--no-persist"]);
    let f = if au.ok() { au.result() } else { au.details() };
    assert_eq!(
        f["families"]["memory_retrieval_regression"]["ok"], false,
        "{}",
        f["families"]["memory_retrieval_regression"]
    );
    let s = g.ok(&["memory", "heldout-starter"]);
    assert!(s["queries"].as_u64().unwrap() >= 5);
    g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(g.ok(&["memory", "verify"])["measured"], true);
}

/// H3 / HV-03: L0/L1 roles are refused privileged operations; unknown roles are rejected; human/L4 allowed.
#[test]
fn authority_levels_are_enforced_on_executable_paths() {
    let (root, g) = setup_fixture("greenfield", "rep-auth", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "a",
        "--alias",
        "a-alias",
    ]);
    let aud = g.with_role("independent-auditor"); // L0
    assert_eq!(
        aud.err(&[
            "task",
            "create",
            "--class",
            "documentation",
            "--objective",
            "x",
            "--status",
            "READY"
        ])
        .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        aud.err(&[
            "cit",
            "propose",
            "--proposal",
            "x",
            "--trigger",
            "editorial"
        ])
        .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        aud.err(&["gate", "create", "--question", "q"]).error_code(),
        "AUTHORITY_DENIED"
    );
    let worker = g.with_role("research-agent"); // L1
    assert_eq!(
        worker.err(&["freeze-writes", "--reason", "x"]).error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        worker.err(&["kernel", "reinstall"]).error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        worker
            .err(&[
                "cit",
                "propose",
                "--proposal",
                "x",
                "--trigger",
                "editorial"
            ])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        g.with_role("nobody-role")
            .err(&[
                "task",
                "create",
                "--class",
                "documentation",
                "--objective",
                "x"
            ])
            .error_code(),
        "UNKNOWN_ROLE"
    );
    // orchestrator (L4) creates a gate; an L1 agent cannot answer it; a relayed human answer by L4 can.
    // (WS-3 / BC-P2-49 + BC-P2-10: gates carry a complete package, and the human answer is owner-signed — a
    // `--role human` claim is no longer an identity and carries no authority.)
    let gate = g.ok(&[
        "gate",
        "create",
        "--question",
        "Ship?",
        "--fields",
        &crate::ws03::package(
            json!({"impact_radius": "R3", "reversibility": "irreversible", "confidence": 0.5}),
        ),
    ]);
    let gid = gate["id"].as_str().unwrap().to_string();
    g.ok(&["gate", "present", &gid]);
    assert_eq!(
        worker
            .err(&["decide", &gid, "--option", "A", "--by", "research-agent"])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        worker
            .err(&["decide", &gid, "--option", "A", "--by", "owner"])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        g.err(&[
            "decide",
            &gid,
            "--option",
            "A",
            "--by",
            "orchestrator",
            "--rationale",
            "x"
        ])
        .error_code(),
        "AUTHORITY_DENIED",
        "agent resolution outside agent_resolvable_when (R3, irreversible) is refused even for L4"
    );
    assert_eq!(
        g.with_role("human")
            .err(&["decide", &gid, "--option", "A", "--by", "owner"])
            .error_code(),
        "AUTHORITY_DENIED",
        "a declared `human` role is a claim, not the human"
    );
    let d = crate::ws03::human_decide(&g, &gid, "A");
    assert_eq!(d["answered_by_kind"], "human");
    // agent-resolvable gate (R1, high confidence, reversible) raised by one session can be answered by an L3+
    // agent in another (BC-P2-18: the assessment must not rest solely on the resolver's own declaration)
    let g2 = g.ok(&[
        "gate",
        "create",
        "--question",
        "trivial?",
        "--fields",
        &crate::ws03::package(
            json!({"impact_radius": "R1", "reversibility": "reversible", "confidence": 0.95}),
        ),
    ]);
    let gid2 = g2["id"].as_str().unwrap().to_string();
    g.ok(&["gate", "present", &gid2]);
    assert_eq!(
        g.with_role("change-controller").with_session("S-cc").ok(&[
            "decide",
            &gid2,
            "--option",
            "A",
            "--by",
            "change-controller",
            "--rationale",
            "trivial and reversible"
        ])["answered_by_kind"],
        "agent"
    );
    // L1 worker can claim and close its own task (claim_task/close_task are L1)
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
    let be = g.with_role("backend-engineer");
    be.ok(&["task", "claim", t["id"].as_str().unwrap()]);
    // BC-P2-20 (P2-AR-0026): the close report is the worker's consumption receipt
    let rep = crate::ws05::receipt(
        &be,
        &root,
        t["id"].as_str().unwrap(),
        "w",
        "wrote docs",
        &["README.md"],
        "not_applicable_with_reason",
    );
    be.ok(&["rebuild-memory", "--incremental"]);
    be.ok(&["task", "close", t["id"].as_str().unwrap(), "--report", &rep]);
    assert_eq!(
        be.err(&[
            "task",
            "create",
            "--class",
            "documentation",
            "--objective",
            "x"
        ])
        .error_code(),
        "AUTHORITY_DENIED"
    );
    // cit approval paths: L0 refused; L3 auto-approval only within CHANGE_POLICY; L4 human relay ok
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "edit NOW",
        "--trigger",
        "editorial",
    ]);
    let cid = c["id"].as_str().unwrap().to_string();
    g.ok(&["cit", "simulate", &cid]);
    assert_eq!(
        aud.err(&["cit", "approve", &cid, "--by", "auditor", "--method", "auto"])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    g.with_role("change-controller")
        .ok(&["cit", "approve", &cid, "--by", "agent", "--method", "auto"]);
}

/// H4 / HV-04: task close enforces the task's mutation scope unless a committed CIT governs the change.
#[test]
fn task_close_enforces_mutation_scope() {
    let (root, g) = setup_fixture("greenfield", "rep-scope", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "s",
        "--alias",
        "s-alias",
    ]);
    // P2-AR-0026 (BC-P2-16): a claim is granted only to a task the DAG finds runnable, and an implementation task
    // needs its scenarios and acceptance tests declared (TEST_POLICY.implementation_task_requires); the receipt then
    // traces the work to them (BC-P2-20)
    let inputs = crate::ws05::traceable_inputs(&root, "0100");
    git_commit_all(&root, "traceable inputs");
    g.ok(&["rebuild-memory", "--incremental"]);
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "implementation",
        "--objective",
        "scoped",
        "--status",
        "READY",
        "--allowed",
        "src/**",
        "--fields",
        &inputs.to_string(),
    ]);
    let tid = t["id"].as_str().unwrap().to_string();
    assert_eq!(t["task_status"], "READY", "{t}");
    g.ok(&["task", "claim", &tid]);
    // a change governed by a committed CIT is legitimate even outside allowed_paths (within the claim window).
    // Round-2 integration (P2-AR-0032): the CIT executes before the out-of-scope write below, not while it is on
    // disk. With WS-4's G4 tier after CIT-E and WS-2's W7 remediation, a CIT executed while the stray SCN-0099 exists
    // raises a governed investigation task for it; removing SCN-0099 (the remedy this test asserts) then leaves that
    // task's AFFECTS edge dangling, the suite DEGRADED and WS-5's governance-affecting close refused (routed as an
    // observation in the round-2 integration report). Every assertion below is unchanged.
    let mf = root.join(".governance-runtime/m.json");
    std::fs::write(
        &mf,
        json!([{"op": "write_file", "path": "spec/now/NOW.md", "content": "# NOW\ngoverned\n"}])
            .to_string(),
    )
    .unwrap();
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "governed edit",
        "--trigger",
        "editorial",
        "--manifest",
        mf.to_str().unwrap(),
    ]);
    let cid = c["id"].as_str().unwrap().to_string();
    g.ok(&["cit", "simulate", &cid]);
    g.ok(&["cit", "approve", &cid, "--by", "agent", "--method", "auto"]);
    g.ok(&["cit", "execute", &cid]);
    write(
        &root,
        "spec/scenarios/SCN-0099.yaml",
        "id: SCN-0099\ntype: scenario\ntitle: outside\nstatus: ACTIVE\n",
    );
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = write_report(
        &root,
        "bad",
        "out of scope",
        &["spec/scenarios/SCN-0099.yaml", "README.md"],
        "passed",
    );
    let e = g.err(&["task", "close", &tid, "--report", &rep]);
    assert_eq!(e.error_code(), "MUTATION_SCOPE_VIOLATION");
    assert_eq!(e.details()["violations"].as_array().unwrap().len(), 2);
    assert_eq!(g.ok(&["task", "show", &tid])["task_status"], "IN_PROGRESS");
    let kernel = write_report(
        &root,
        "kernel",
        "touched kernel",
        &["governance/kernel/KERNEL.yaml"],
        "passed",
    );
    assert_eq!(
        g.err(&["task", "close", &tid, "--report", &kernel])
            .error_code(),
        "MUTATION_SCOPE_VIOLATION"
    );
    // the out-of-scope file is still on disk: observed mutations (not the report) decide, so close is refused ...
    let good = crate::ws05::receipt(
        &g,
        &root,
        &tid,
        "good",
        "in scope + governed",
        &["src/lib.rs", "spec/now/NOW.md"],
        "not_applicable_with_reason",
    );
    g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(
        g.err(&["task", "close", &tid, "--report", &good])
            .error_code(),
        "MUTATION_SCOPE_VIOLATION"
    );
    // ... until it is removed from the repository
    std::fs::remove_file(root.join("spec/scenarios/SCN-0099.yaml")).unwrap();
    g.ok(&["rebuild-memory", "--incremental"]);
    g.ok(&["task", "close", &tid, "--report", &good]);
}

/// H2 / HV-05: claims survive full rebuilds and recovery; a second session cannot steal a claimed task.
#[test]
fn claims_survive_full_memory_rebuild() {
    let (root, g) = setup_fixture("greenfield", "rep-claims", "S-alpha");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "c",
        "--alias",
        "c-alias",
    ]);
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "claimed",
        "--status",
        "READY",
    ]);
    let tid = t["id"].as_str().unwrap().to_string();
    g.ok(&["task", "claim", &tid]);
    let b = g.with_session("S-beta");
    assert_eq!(b.err(&["task", "claim", &tid]).error_code(), "TASK_CLAIMED");
    g.ok(&["rebuild-memory"]);
    assert_eq!(g.ok(&["claims", "list"]).as_array().unwrap().len(), 1);
    assert_eq!(b.err(&["task", "claim", &tid]).error_code(), "TASK_CLAIMED");
    g.ok(&["recover"]);
    assert_eq!(g.ok(&["claims", "list"]).as_array().unwrap().len(), 1);
    assert!(exists(&root, ".governance-runtime/claims.db") && doctor_check(&g, "D026").0);
    // deleting the derived index alone never touches claims
    std::fs::remove_file(root.join(".governance-runtime/state.db")).unwrap();
    g.ok(&["rebuild-memory"]);
    assert_eq!(b.err(&["task", "claim", &tid]).error_code(), "TASK_CLAIMED");
}

/// BUDGET_POLICY.defaults.max_parallel_agents bounds concurrent sessions and raises a gate.
#[test]
fn budget_parallel_agents_threshold_raises_gate() {
    let (root, g) = setup_fixture("greenfield", "rep-budget", "S-one");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "b",
        "--alias",
        "b-alias",
    ]);
    set_overrides(
        &root,
        json!({"BUDGET_POLICY.defaults.max_parallel_agents": 1}),
    );
    let t1 = g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "a",
        "--status",
        "READY",
    ]);
    let t2 = g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "b",
        "--status",
        "READY",
    ]);
    g.ok(&["task", "claim", t1["id"].as_str().unwrap()]);
    let e = g
        .with_session("S-two")
        .err(&["task", "claim", t2["id"].as_str().unwrap()]);
    assert_eq!(e.error_code(), "BUDGET_EXCEEDED");
    assert!(e.details()["human_gate"]
        .as_str()
        .unwrap()
        .starts_with("HDG-"));
    // routing evidence above max_task_cost_usd raises a gate too
    let rec = root.join(".governance-runtime/ev.json");
    std::fs::write(&rec, json!({"model": "m", "provider": "p", "task_class": "implementation", "reasoning_effort": "high", "cost": 999.0, "latency_ms": 1, "pass": true, "repair_count": 0, "reviewer_findings": 0}).to_string()).unwrap();
    let r = g.ok(&["route", "--record", rec.to_str().unwrap()]);
    assert!(r["threshold_exceeded"]
        .as_str()
        .unwrap()
        .contains("max_task_cost_usd"));
    assert!(r["human_gate"].as_str().unwrap().starts_with("HDG-"));
}

/// H6 / HV-29: destructive migration entries execute only after a presented, answered gate record.
#[test]
fn destructive_migration_requires_answered_gate_record() {
    let (root, planner, executor) = run_brownfield_to_a6("rep-destructive");
    let cat: Vec<serde_json::Value> = read(
        &root,
        "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl",
    )
    .lines()
    .map(|l| serde_json::from_str(l).unwrap())
    .collect();
    let dead = cat
        .iter()
        .find(|e| e["current_path"] == "src/app/old_export.py")
        .unwrap();
    let gid = dead["human_gate"]
        .as_str()
        .expect("A6 batch 0 must create a gate record for each destructive entry")
        .to_string();
    let r = executor.ok(&[
        "adopt",
        "migrate",
        "--batch",
        "7",
        "--gate-answer",
        dead["artifact_id"].as_str().unwrap(),
    ]);
    assert!(
        exists(&root, "src/app/old_export.py"),
        "flag-only answers must not delete anything"
    );
    assert!(
        r["batches"][0]["skipped"].to_string().contains("gate"),
        "{}",
        r["batches"][0]
    );
    assert!(r["batches"].as_array().unwrap().iter().any(|b| b
        .get("note")
        .map(|n| n.to_string().contains("ignored"))
        .unwrap_or(false)));
    let gate = yaml(&root, &format!("spec/decisions/{gid}.yaml"));
    assert_eq!(gate["trigger"], "destructive_migration");
    assert_eq!(gate["gate_status"], "PENDING");
    assert_eq!(
        executor
            .err(&["decide", &gid, "--option", "A", "--by", "owner"])
            .error_code(),
        "GATE_NOT_PRESENTED"
    );
    executor.ok(&["gate", "present", &gid]);
    crate::ws03::human_decide(&executor, &gid, "A");
    executor.ok(&["adopt", "migrate", "--batch", "7"]);
    assert!(
        !exists(&root, "src/app/old_export.py"),
        "answered gate => destructive action executes"
    );
    let _ = planner;
}

/// H5 / HV-09 / HV-21: restricted/confidential classes are never read or indexed; namespaces filter by role.
#[test]
fn sensitivity_classes_and_namespaces_are_enforced() {
    let (root, g) = setup_fixture("greenfield", "rep-sens", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "s",
        "--alias",
        "s-alias",
        "--skip-index",
    ]);
    let mut ds = yaml(&root, "governance/project/DATA_SENSITIVITY.yaml");
    ds["classifications"] = json!([{"pattern": "product/data/customers/**", "class": "restricted", "reason": "customer data"}, {"pattern": "docs/private/**", "class": "confidential", "reason": "legal"}]);
    write_yaml(&root, "governance/project/DATA_SENSITIVITY.yaml", &ds);
    let mut rc = yaml(&root, "governance/project/REPOSITORY_CONTRACT.yaml");
    rc["paths"].as_array_mut().unwrap().push(json!({"pattern": "product/legal/**", "class": "authoritative", "sensitivity": "restricted", "semantic_index": true, "lexical_index": true, "namespace": "product"}));
    rc["paths"].as_array_mut().unwrap().push(json!({"pattern": "docs/**", "class": "narrative", "semantic_index": true, "lexical_index": true, "namespace": "spec"}));
    write_yaml(&root, "governance/project/REPOSITORY_CONTRACT.yaml", &rc);
    write(
        &root,
        "product/data/customers/list.csv",
        "customer,email\nAcme Freight Ltd,ops@acme.example\n",
    );
    write(
        &root,
        "product/legal/settlement.md",
        "# Restricted settlement\nConfidential terms with Acme Freight Ltd.\n",
    );
    write(
        &root,
        "docs/private/memo.md",
        "# confidential memo\nlegal privilege\n",
    );
    let r = g.ok(&["rebuild-memory"]);
    let excluded = r["excluded"].to_string();
    assert!(
        excluded.contains("product/data/customers/list.csv")
            && excluded.contains("product/legal/settlement.md")
            && excluded.contains("sensitivity:restricted"),
        "{excluded}"
    );
    let paths = indexed_paths(&root);
    assert!(!paths
        .iter()
        .any(|p| p.starts_with("product/data") || p.starts_with("product/legal")));
    for t in chunk_texts(&root) {
        assert!(!t.contains("Acme Freight"));
    }
    let q = g.ok(&[
        "memory",
        "query",
        "Acme Freight settlement terms",
        "--k",
        "5",
    ]);
    assert!(q["hits"]
        .as_array()
        .unwrap()
        .iter()
        .all(|h| !h["path"].as_str().unwrap().starts_with("product/legal")));
    let au = g.run(&["audit", "--no-persist"]);
    let f = if au.ok() { au.result() } else { au.details() };
    assert!(
        f["findings"]
            .as_array()
            .unwrap()
            .iter()
            .all(|x| x["family"] != "secrets_sensitivity_indexing"),
        "{}",
        f["findings"]
    );
    // confidential is indexed (not in never_index_classes) but export-denied; never_export blocks fixture files
    assert!(paths.contains(&"docs/private/memo.md".to_string()));
    let d = db(&root);
    let sens: String = d
        .conn
        .query_row(
            "SELECT sensitivity FROM artifacts WHERE path='docs/private/memo.md'",
            [],
            |r| r.get(0),
        )
        .unwrap();
    assert_eq!(sens, "confidential");
    let mut l = gov_runtime::util::read_yaml(
        &canonical_root().join("fixtures/upstream-learning/lessons/L-0001.yaml"),
    )
    .unwrap();
    l["synthetic_reproducer"]["files"] = json!({"docs/private/x.md": "synthetic"});
    write_yaml(&root, "spec/lessons/L-0001.yaml", &l);
    let b = g.err(&["upstream", "prepare", "L-0001"]);
    assert_eq!(b.error_code(), "UPSTREAM_BLOCKED");
    assert!(b.details()["reasons"]
        .to_string()
        .contains("never_export_classes"));
    // namespace/role filter: research-agent is not in the product namespace's roles
    let qr = g.with_role("research-agent").ok(&[
        "memory",
        "query",
        "Ledger append order total_cents",
        "--k",
        "5",
    ]);
    assert!(
        qr["hits"]
            .as_array()
            .unwrap()
            .iter()
            .all(|h| !h["path"].as_str().unwrap().starts_with("src/")),
        "{}",
        qr["hits"]
    );
    assert!(qr["excluded_by_namespace"].as_u64().unwrap() > 0);
    let qe = g.with_role("backend-engineer").ok(&[
        "memory",
        "query",
        "Ledger append order total_cents",
        "--k",
        "5",
    ]);
    assert!(qe["hits"]
        .as_array()
        .unwrap()
        .iter()
        .any(|h| h["path"].as_str().unwrap().starts_with("src/")));
}

/// M2 / HV-10 and M9 / HV-34 / HV-17: automatic CIT-P on policy triggers; secrets redacted at propose and execution refused.
#[test]
fn cit_auto_simulation_and_secret_redaction() {
    let (root, g) = setup_fixture("greenfield", "rep-cit", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "c",
        "--alias",
        "c-alias",
    ]);
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "replace the ledger storage engine",
        "--trigger",
        "architecture_change",
    ]);
    assert_eq!(c["cit_status"], "SIMULATED");
    assert_eq!(c["auto_simulated"], true);
    assert!(c["simulation"]["human_gate"]
        .as_str()
        .unwrap()
        .starts_with("HDG-"));
    let mf = root.join(".governance-runtime/m.json");
    std::fs::write(&mf, json!([{"op": "write_file", "path": "src/keys.rs", "content": "pub const K: &str = \"AKIAIOSFODNN7EXAMPLE\";\n"}]).to_string()).unwrap();
    let c2 = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "add key",
        "--trigger",
        "editorial",
        "--manifest",
        mf.to_str().unwrap(),
    ]);
    let cid = c2["id"].as_str().unwrap().to_string();
    assert_eq!(c2["secret_flagged"], true);
    assert!(
        !read(&root, &format!("spec/decisions/{cid}.yaml")).contains("AKIAIOSFODNN7EXAMPLE"),
        "secret must not be persisted"
    );
    assert!(
        doctor_check(&g, "D011").0,
        "no secret outside secret class after redaction"
    );
    // WS-4 round 2 (BC-P2-13): writing product source is a behaviour change whatever the declared label, so this
    // `editorial` CIT is human-gated; the approval goes through the owner channel, and execution is still refused
    let sim = g.ok(&["cit", "simulate", &cid]);
    assert_eq!(sim["impact"]["human_gate_required"], true, "{sim}");
    let gate = sim["human_gate"].as_str().unwrap().to_string();
    g.ok(&["gate", "present", &gate]);
    crate::ws03::human_decide(&g, &gate, "A");
    g.ok(&["cit", "approve", &cid, "--by", "owner", "--method", "human"]);
    assert_eq!(
        g.err(&["cit", "execute", &cid]).error_code(),
        "SECRET_IN_MANIFEST"
    );
    assert!(!exists(&root, "src/keys.rs"));
}

/// M3 / HV-11: `update --apply --approve` is not a substitute for a presented, answered gate.
#[test]
fn update_approval_requires_presented_answered_gate() {
    let root = tmp("rep-update");
    let proj = root.join("project");
    std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# u\n");
    git_init_commit(&proj);
    let g = Gov::new(&proj, "S-rep");
    // provision, then install (OWNER-DECISION-P2-0002): both releases are signed under the suite's throw-away root
    provision(&g);
    let prev = signed_copy(
        &canonical_root().join("fixtures/update/previous-release/4.1.1"),
        "rep-update-4.1.1",
        sequence_of("4.1.1"),
    );
    g.ok(&[
        "init",
        "--source",
        prev.to_str().unwrap(),
        "--name",
        "u",
        "--alias",
        "u-alias",
        "--skip-index",
    ]);
    assert_eq!(
        g.err(&["update", "--apply", "--source", signed_source()])
            .error_code(),
        "HUMAN_GATE_REQUIRED"
    );
    let ap = g.ok(&[
        "update",
        "--apply",
        "--source",
        signed_source(),
        "--approve",
        "--by",
        "owner",
    ]);
    assert_eq!(ap["applied"], false);
    let gid = ap["human_gate"].as_str().unwrap().to_string();
    assert_eq!(yaml(&proj, "governance/framework.lock")["version"], "4.1.1");
    g.ok(&["gate", "present", &gid]);
    crate::ws03::human_decide(&g, &gid, "A");
    let ap2 = g.ok(&[
        "update",
        "--apply",
        "--source",
        signed_source(),
        "--approve",
        "--by",
        "owner",
    ]);
    assert_eq!(ap2["applied"], true);
    assert_eq!(
        yaml(&proj, "governance/framework.lock")["version"],
        gov_runtime::VERSION
    );
    assert!(g
        .ok(&["gate", "list"])
        .as_array()
        .unwrap()
        .iter()
        .all(|x| x["presented_in_chat"] == true));
}

/// M5 / HV-16: FREEZE_WRITES stops migration batches and upstream submission.
#[test]
fn freeze_writes_is_honoured_by_adopt_and_upstream() {
    let (root, planner) = setup_fixture("migration", "rep-freeze", "S-planner");
    for s in [
        "baseline",
        "inventory",
        "classify",
        "map",
        "plan",
        "test-design",
    ] {
        planner.ok(&["adopt", s]);
    }
    crate::migration::reviewer_authors_tests(&root); // BC-P2-34: the reviewer approves with tests of its own
    planner
        .with_session("S-rev")
        .with_role("migration-reviewer")
        .ok(&["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"]);
    let ex = planner
        .with_session("S-exec")
        .with_role("migration-executor");
    ex.ok(&[
        "adopt",
        "migrate",
        "--batch",
        "0",
        "--source",
        signed_source(),
        "--name",
        "libcore",
        "--alias",
        "fx-mig",
    ]);
    ex.ok(&["freeze-writes", "--reason", "incident"]);
    assert_eq!(
        ex.err(&["adopt", "migrate", "--batch", "1"]).error_code(),
        "FROZEN"
    );
    assert_eq!(
        ex.err(&["adopt", "migrate", "--batch", "2"]).error_code(),
        "FROZEN"
    );
    assert!(exists(&root, "notes/api-spec.md"));
    planner
        .with_session("S-exec")
        .with_role("orchestrator")
        .ok(&["resume"]);
    let (root2, g2) = setup_fixture("greenfield", "rep-freeze-up", "S-rep");
    g2.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "f",
        "--alias",
        "f-alias",
    ]);
    std::fs::copy(
        canonical_root().join("fixtures/upstream-learning/lessons/L-0001.yaml"),
        root2.join("spec/lessons/L-0001.yaml"),
    )
    .unwrap();
    let inbox = root2.join("_inbox").join("lessons").join("inbox");
    std::fs::create_dir_all(&inbox).unwrap();
    g2.ok(&["upstream", "prepare", "L-0001"]);
    g2.ok(&["freeze-writes", "--reason", "incident"]);
    assert_eq!(
        g2.err(&[
            "upstream",
            "submit",
            "PKT-0001",
            "--destination",
            inbox.to_str().unwrap(),
            "--approved-by",
            "owner"
        ])
        .error_code(),
        "FROZEN"
    );
}

/// M4 / HV-15: the packet carries the authority layers and flags superseded-but-ACTIVE decisions.
#[test]
fn context_packet_layers_and_contradiction_flags() {
    let (root, g) = setup_fixture("greenfield", "rep-ctx", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "x",
        "--alias",
        "x-alias",
    ]);
    write_yaml(
        &root,
        "spec/decisions/D-0001.yaml",
        &json!({"id": "D-0001", "type": "decision", "title": "Retry limit is 3", "status": "ACTIVE", "question": "retries?", "chosen_option": "A", "rationale": "old", "human_approved": true}),
    );
    write_yaml(
        &root,
        "spec/decisions/D-0002.yaml",
        &json!({"id": "D-0002", "type": "decision", "title": "Retry limit is 5", "status": "ACTIVE", "supersedes": ["D-0001"], "question": "retries?", "chosen_option": "B", "rationale": "new", "human_approved": true}),
    );
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "implementation",
        "--objective",
        "align retries",
        "--status",
        "READY",
        "--fields",
        r#"{"decisions": ["D-0001", "D-0002"]}"#,
    ]);
    g.ok(&["rebuild-memory"]);
    let c = g.ok(&["context", "compile", t["id"].as_str().unwrap()]);
    let det = &c["deterministic_authority"];
    let act: Vec<&str> = det["active_decisions"]
        .as_array()
        .unwrap()
        .iter()
        .map(|d| d["id"].as_str().unwrap())
        .collect();
    assert_eq!(act, vec!["D-0002"]);
    assert_eq!(det["conflicting_decisions"][0]["id"], "D-0001");
    assert_eq!(
        det["conflicting_decisions"][0]["authority_flag"],
        "UNKNOWN_OR_CONFLICTING"
    );
    assert_eq!(
        det["authority_layers"][0]["name"],
        "constitution_hard_invariants"
    );
    assert!(det["authority_layers"][0]["items"]
        .as_array()
        .unwrap()
        .iter()
        .any(|i| i["id"] == "INV-001"));
    assert!(det["hard_invariants"].as_array().unwrap().len() >= 15);
    assert!(det["authority_layers"]
        .as_array()
        .unwrap()
        .iter()
        .any(|l| l["name"] == "project_policy"));
    let c2 = g.ok(&["context", "compile", t["id"].as_str().unwrap()]);
    assert_eq!(c["deterministic_hash"], c2["deterministic_hash"]);
    // CONTEXT_POLICY.max_packet_chars bounds the packet deterministically
    set_overrides(&root, json!({"CONTEXT_POLICY.max_packet_chars": 9000}));
    let c3 = g.ok(&["context", "compile", t["id"].as_str().unwrap()]);
    assert!(
        c3["retrieved_intelligence"]["truncated_slices"]
            .as_u64()
            .unwrap_or(0)
            > 0
            || c3["chars"].as_u64().unwrap() <= 9000,
        "{}",
        c3["chars"]
    );
}

/// M10 / HV-39 and M8 / HV-33: implementation prerequisites and bare-identifier symbol queries.
#[test]
fn implementation_prerequisites_and_symbol_route() {
    let (_root, g) = setup_fixture("greenfield", "rep-impl", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "i",
        "--alias",
        "i-alias",
    ]);
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "implementation",
        "--objective",
        "ship without tests",
        "--status",
        "READY",
        "--allowed",
        "src/**",
    ]);
    let rp = g.ok(&["task", "replan"]);
    assert!(rp["runnable"].as_array().unwrap().is_empty(), "{rp}");
    assert_eq!(
        g.ok(&["task", "show", t["id"].as_str().unwrap()])["task_status"],
        "BLOCKED"
    );
    let dag = g.ok(&["task", "dag"]);
    assert!(dag["blocked"]
        .to_string()
        .contains("implementation_task_requires"));
    let c = g.ok(&["continue"]);
    assert_ne!(c["task"], t["id"]);
    let (root2, g2) = setup_fixture("brownfield", "rep-sym", "S-rep");
    g2.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "b",
        "--alias",
        "b-alias",
    ]);
    let a = g2.ok(&[
        "memory",
        "query",
        "with_retry",
        "--route",
        "symbol",
        "--k",
        "5",
    ]);
    assert!(
        a["hits"]
            .as_array()
            .unwrap()
            .iter()
            .any(|h| h["artifact_id"] == "file:src/app/retry.py"),
        "{}",
        a["hits"]
    );
    let b = g2.ok(&["memory", "query", "with_retry", "--k", "5"]);
    assert!(b["routes"]
        .as_array()
        .unwrap()
        .iter()
        .any(|r| r == "symbol"));
    let d = db(&root2);
    let calls: i64 = d
        .conn
        .query_row("SELECT COUNT(*) FROM edges WHERE type='CALLS'", [], |r| {
            r.get(0)
        })
        .unwrap();
    assert!(
        calls > 0,
        "CALLS edges must be materialised from code intelligence"
    );
}

/// M7 / HV-26, L1 / HV-19, L4 / HV-28, L6 / HV-32, L7 / HV-14, L8 / HV-27.
#[test]
fn smaller_findings_regressions() {
    let (root, g) = setup_fixture("greenfield", "rep-small", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "shipping-quotes",
        "--alias",
        "proj-z",
    ]);
    // L8: timestamps are quoted strings in YAML output
    assert!(
        read(&root, "governance/framework.lock").contains("installed_at: '"),
        "{}",
        read(&root, "governance/framework.lock")
    );
    // M7: category/title/tags sanitised
    let mut ds = yaml(&root, "governance/project/DATA_SENSITIVITY.yaml");
    ds["identifiers_to_strip"] = json!(["Acme Freight Ltd"]);
    write_yaml(&root, "governance/project/DATA_SENSITIVITY.yaml", &ds);
    let mut l = gov_runtime::util::read_yaml(
        &canonical_root().join("fixtures/upstream-learning/lessons/L-0001.yaml"),
    )
    .unwrap();
    l["id"] = json!("L-0010");
    l["title"] = json!("Acme Freight Ltd lost data");
    l["category"] = json!("acme-freight-ltd-outage");
    l["tags"] = json!(["Acme Freight Ltd"]);
    write_yaml(&root, "spec/lessons/L-0010.yaml", &l);
    let pk = g.ok(&["upstream", "prepare", "L-0010"]);
    assert!(!read(
        &root,
        &pk["path"]
            .as_str()
            .unwrap()
            .replace(&format!("{}/", root.display()), "")
    )
    .to_lowercase()
    .contains("acme"));
    // L1: checkpoint before handoff; L6: worker lessons promoted; L7: rollback marks the decision REJECTED
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "implementation",
        "--objective",
        "impl",
        "--status",
        "READY",
        "--allowed",
        "src/**",
    ]);
    let before = g.ok(&["checkpoint", "latest"]);
    let h = g.ok(&[
        "handoff",
        "create",
        "--to-role",
        "backend-engineer",
        "--task",
        t["id"].as_str().unwrap(),
    ]);
    let after = g.ok(&["checkpoint", "latest"]);
    assert_ne!(before["id"], after["id"]);
    assert_eq!(after["trigger"], "before_handoff");
    let ret = root.join(".governance-runtime/ret.json");
    std::fs::write(&ret, json!({"task": t["id"], "status": "success", "work_completed": "did", "files_changed": ["src/lib.rs"], "evidence": [], "tests": {"status": "passed"}, "discoveries": [], "risks": [], "lessons": ["always pin the embedder"], "proposed_decisions": [], "unresolved": [], "recommended_next_action": "close"}).to_string()).unwrap();
    let r = g.ok(&[
        "handoff",
        "return",
        h["id"].as_str().unwrap(),
        "--file",
        ret.to_str().unwrap(),
    ]);
    let lid = r["lessons_created"][0].as_str().unwrap();
    assert_eq!(
        yaml(&root, &format!("spec/lessons/{lid}.yaml"))["status"],
        "PROVISIONAL"
    );
    write_yaml(
        &root,
        "spec/requirements/REQ-0001.yaml",
        &json!({"id": "REQ-0001", "type": "requirement", "title": "Exact cents", "status": "ACTIVE", "kind": "functional", "acceptance_criteria": ["a"]}),
    );
    g.ok(&["rebuild-memory"]);
    let mf = root.join(".governance-runtime/m.json");
    std::fs::write(&mf, json!([{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["a", "b"]}]).to_string()).unwrap();
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "tighten",
        "--trigger",
        "behaviour_change",
        "--targets",
        "REQ-0001",
        "--manifest",
        mf.to_str().unwrap(),
    ]);
    let cid = c["id"].as_str().unwrap().to_string();
    let gate = c["simulation"]["human_gate"].as_str().unwrap().to_string();
    g.ok(&["gate", "present", &gate]);
    crate::ws03::human_decide(&g, &gate, "A");
    let ap = g.ok(&["cit", "approve", &cid, "--by", "owner", "--method", "human"]);
    g.ok(&["cit", "execute", &cid]);
    g.ok(&["cit", "rollback", &cid, "--reason", "test"]);
    let dec = yaml(
        &root,
        &format!("spec/decisions/{}.yaml", ap["decision"].as_str().unwrap()),
    );
    assert_eq!(dec["status"], "REJECTED");
    assert_eq!(dec["rollback_of"], cid);
    // L4: audit leaves the index fresh
    g.ok(&["audit"]);
    assert!(doctor_check(&g, "D010").0);
}

/// M6 / HV-24: the kernel is embedded; init works without any canonical checkout; the lock source is logical.
#[test]
fn embedded_kernel_installs_without_canonical_root() {
    let root = tmp("rep-embedded");
    write(&root, "README.md", "x\n");
    git_init_commit(&root);
    // UNPROVISIONED on purpose: this scenario is the binary's own embedded payload, which OWNER-DECISION-P2-0002
    // admits on a machine with no trust anchor only as a marked bootstrap installation.
    let g = Gov::new(&root, "S-rep")
        .with_env("GOV_CANONICAL_ROOT", "/nonexistent/path")
        .with_env("GOV_KERNEL_CACHE", root.join("_cache").to_str().unwrap());
    let r = g.ok(&["init", "--name", "p", "--alias", "p-alias", "--skip-index"]);
    assert_eq!(r["version"], gov_runtime::VERSION);
    assert_eq!(
        r["release_authenticity"]["admission"], "BOOTSTRAP_EMBEDDED_PAYLOAD",
        "{r}"
    );
    assert_eq!(r["release_authenticity"]["authenticity"], "UNKNOWN");
    let lock = yaml(&root, "governance/framework.lock");
    assert!(
        lock["source"]
            .as_str()
            .unwrap()
            .starts_with("embedded:agentic-engineering-os@"),
        "{}",
        lock["source"]
    );
    assert!(!lock["source"].as_str().unwrap().contains('/'));
    assert_eq!(g.ok(&["kernel", "verify"])["ok"], true);
    assert!(
        exists(&root, "governance/kernel/policies/ENFORCEMENT_MAP.yaml")
            && exists(&root, "governance/kernel/tools/registry/TOOLS.yaml")
            && exists(&root, "governance/kernel/migrations/M-4.1.2-4.1.3.yaml")
    );
}

/// M12: every declared policy key is enforced or classified; enforced_by functions exist and keys are read in source.
#[test]
fn policy_enforcement_coverage_is_complete_and_honest() {
    let (_root, g) = setup_fixture("greenfield", "rep-coverage", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "p",
        "--alias",
        "p-alias",
    ]);
    let au = g.run(&["audit", "--no-persist"]);
    let f = if au.ok() { au.result() } else { au.details() };
    let fam = &f["families"]["policy_enforcement_coverage"];
    assert_eq!(fam["ok"], true, "{fam}");
    assert_eq!(
        fam["detail"]["uncovered"].as_array().unwrap().len(),
        0,
        "{}",
        fam["detail"]["uncovered"]
    );
    assert!(
        fam["detail"]["enforced"].as_u64().unwrap() >= 80,
        "{}",
        fam["detail"]
    );
    // static: every enforced_by function exists in the Rust source and every enforced key's last segment is read
    let map = gov_runtime::util::read_yaml(
        &canonical_root().join("framework/policies/ENFORCEMENT_MAP.yaml"),
    )
    .unwrap();
    let mut src = String::new();
    for (abs, _) in
        gov_runtime::paths::iter_repo_files(&canonical_root().join("runtime/src"), false)
    {
        src.push_str(&std::fs::read_to_string(&abs).unwrap());
    }
    for f in gov_runtime::policy_coverage::enforced_functions(&map) {
        let name = f.rsplit("::").next().unwrap();
        assert!(
            src.contains(&format!("fn {name}")),
            "enforced_by function {f} does not exist"
        );
    }
    for (key, entry) in map["keys"].as_object().unwrap() {
        if entry.get("enforced_by").is_none() {
            continue;
        }
        let (_pol, dotted) = key.split_once('.').unwrap();
        let leaf = dotted
            .trim_end_matches(".*")
            .rsplit('.')
            .next()
            .unwrap()
            .to_string();
        assert!(
            src.contains(&format!("\"{leaf}\""))
                || src.contains(&format!(".{leaf}\""))
                || src.contains(&format!("{leaf}."))
                || src.contains(&format!("\"{}", dotted.trim_end_matches(".*"))),
            "policy key {key} is declared enforced but never referenced in runtime/src"
        );
    }
}

/// C2 / HV-36 at the CLI boundary: a plugin answering with hundreds of kilobytes completes quickly.
#[test]
fn plugin_host_large_response_through_cli() {
    let (root, g) = setup_fixture("greenfield", "rep-big", "S-rep");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "b",
        "--alias",
        "b-alias",
        "--skip-index",
    ]);
    write(&root, "big.sh", "#!/usr/bin/env bash\nREQ=$(cat)\nn=$(printf '%s' \"$REQ\" | sed -n 's/.*\"n\"[[:space:]]*:[[:space:]]*\\([0-9]*\\).*/\\1/p'); n=${n:-1}\nprintf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{\"id\":\"big\",\"version\":\"1\"},\"outputs\":{\"vectors\":['\nrow=$(yes 0.123456 | head -n 512 | paste -sd, -)\nfor ((i=0;i<n;i++)); do if [ $i -gt 0 ]; then printf ','; fi; printf '[%s]' \"$row\"; done\nprintf '],\"dim\":512}}'\n");
    use std::os::unix::fs::PermissionsExt;
    std::fs::set_permissions(root.join("big.sh"), std::fs::Permissions::from_mode(0o755)).unwrap();
    write_yaml(
        &root,
        "governance/project/plugins/big.yaml",
        &json!({"plugin_id": "big", "capability": "embed", "version": "1", "command": [root.join("big.sh").to_string_lossy()], "languages": []}),
    );
    // BC-P2-39 (repair iteration 1, WS-7): an executable plugin runs only when registered against a gate raised for it
    crate::ws07::register_approved(&g, &root.join("governance/project/plugins/big.yaml"));
    let t0 = std::time::Instant::now();
    let r = g.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "big",
        "--inputs",
        r#"{"n": 256}"#,
    ]);
    assert!(
        r["stdout_bytes"].as_u64().unwrap() > 1_000_000,
        "{}",
        r["stdout_bytes"]
    );
    assert!(t0.elapsed() < std::time::Duration::from_secs(30));
}
