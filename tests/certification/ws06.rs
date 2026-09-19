//! Repair iteration 1, round 2, WS-6 (P2-AR-0027): graph integrity (BC-P2-28), retrieval-profile component identity
//! and change governance (BC-P2-30), classification of non-rebuildable OS state (BC-P2-31).
//!
//! Builder regression evidence (Contract v3 O3), not acceptance evidence. Human answers go through WS-3's
//! owner-signed channel helper (`crate::ws03::human_decide`); every invocation declares its role.
use crate::common::*;
use serde_json::{json, Value};
use std::path::Path;

fn set_overrides(root: &Path, over: Value) {
    let mut pp = yaml(root, "governance/project/PROJECT_POLICY.yaml");
    let mut cur = pp
        .get("policy_overrides")
        .cloned()
        .filter(|v| v.is_object())
        .unwrap_or(json!({}));
    for (k, v) in over.as_object().unwrap() {
        cur[k] = v.clone();
    }
    pp["policy_overrides"] = cur;
    write_yaml(root, "governance/project/PROJECT_POLICY.yaml", &pp);
}

fn kinds(r: &Value) -> Vec<String> {
    r["findings"]
        .as_array()
        .unwrap()
        .iter()
        .map(|f| f["kind"].as_str().unwrap().to_string())
        .collect()
}

fn findings_of<'a>(r: &'a Value, kind: &str) -> Vec<&'a Value> {
    r["findings"]
        .as_array()
        .unwrap()
        .iter()
        .filter(|f| f["kind"] == kind)
        .collect()
}

/// BC-P2-30 (A0-D4-01, A0-D5-01): the embedder's adapter, model artefact and inference runtime are separately
/// identified and content-bound; a model artefact changed behind an unchanged plugin id and revision fails closed at
/// query time, makes the index stale and forces a full re-embed; a descriptor revision other than the pinned one
/// never executes.
#[test]
fn embedder_components_are_identified_bound_and_fail_closed_on_change() {
    let (root, g) = setup_fixture("greenfield", "ws06-components", "S-ws06");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "c",
        "--alias",
        "c-alias",
        "--skip-index",
    ]);
    write(
        &root,
        "tools/emb/echo_embedder.sh",
        &read(&canonical_root(), "capabilities/shell/echo_embedder.sh"),
    );
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(
            root.join("tools/emb/echo_embedder.sh"),
            std::fs::Permissions::from_mode(0o755),
        )
        .unwrap();
    }
    write(&root, "tools/emb/model.bin", "weights v1\n");
    let desc = json!({"plugin_id": "echo-local", "capability": "embed", "version": "1", "command": ["tools/emb/echo_embedder.sh"], "languages": []});
    write_yaml(&root, "governance/project/plugins/echo-local.yaml", &desc);
    // round-2 integration (P2-AR-0032): WS-7 (BC-P2-39) — an executable plugin runs only registered, against a gate
    // raised for exactly it and answered by the owner
    crate::ws07::register_approved(&g, &root.join("governance/project/plugins/echo-local.yaml"));
    set_overrides(
        &root,
        json!({"MEMORY_POLICY.embedding.provider": "echo-local", "MEMORY_POLICY.embedding.dimensions": 8}),
    );
    write_yaml(
        &root,
        "spec/requirements/REQ-0001.yaml",
        &json!({"id": "REQ-0001", "type": "requirement", "title": "Order totals are exact integer cents", "status": "ACTIVE", "kind": "functional"}),
    );
    git_commit_all(&root, "local embedder with a model artefact");
    let r = g.ok(&["rebuild-memory"]);
    let e = &r["embedder"];
    assert_eq!(e["id"], "echo-local", "{e}");
    assert_eq!(e["adapter"]["kind"], "plugin");
    assert_eq!(e["adapter"]["plugin_id"], "echo-local");
    assert_eq!(e["adapter"]["version"], "1");
    assert_eq!(
        e["model"]["artefacts"], 1,
        "the model artefact beside the adapter is bound: {e}"
    );
    assert_eq!(e["runtime"]["id"], "bash", "{e}");
    assert_eq!(e["runtime"]["kind"], "interpreter");
    assert_eq!(e["identity"].as_str().unwrap().len(), 64);
    let m = json(&root, "governance/generated/index-manifest.json");
    assert_eq!(
        m["embedder"], r["embedder"],
        "the manifest pins the identity"
    );
    let comp = &m["components"]["embedder"];
    assert_eq!(comp["model"]["artefacts"][0]["path"], "tools/emb/model.bin");
    assert_eq!(comp["runtime"]["sha256"].as_str().unwrap().len(), 64);
    assert_eq!(
        comp["adapter"]["implementation"][0]["path"],
        "tools/emb/echo_embedder.sh"
    );
    g.ok(&[
        "memory",
        "query",
        "integer cents",
        "--route",
        "semantic",
        "--k",
        "3",
    ]);
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);

    // the model artefact changes behind the same plugin id, revision and adapter bytes
    write(&root, "tools/emb/model.bin", "weights v2\n");
    git_commit_all(&root, "weights changed");
    let fr = g.ok(&["memory", "freshness"]);
    assert_eq!(fr["fresh"], false, "{fr}");
    assert!(!fr["pin_mismatch"].as_array().unwrap().is_empty(), "{fr}");
    let q = g.err(&["memory", "query", "integer cents", "--route", "semantic"]);
    assert_eq!(q.error_code(), "EMBEDDER_MISMATCH", "{}", q.envelope);
    assert!(
        q.envelope["error"]["message"]
            .as_str()
            .unwrap()
            .contains("model artefact"),
        "{}",
        q.envelope
    );
    let rb = g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(rb["mode"], "full", "{rb}");
    assert!(rb["escalated_to_full"]
        .as_str()
        .unwrap()
        .contains("embedder"));
    g.ok(&[
        "memory",
        "query",
        "integer cents",
        "--route",
        "semantic",
        "--k",
        "3",
    ]);

    // the declared revision moves away from the pinned one: nothing executes under the old pin
    let mut d2 = desc.clone();
    d2["version"] = json!("2");
    write_yaml(&root, "governance/project/plugins/echo-local.yaml", &d2);
    // round-2 integration (P2-AR-0032): under WS-7 (BC-P2-39/40) the edited descriptor is not the registered one, so it
    // never executes at all; the owner approves the revision-2 registration, and what still refuses it is the index's
    // revision-1 pin (this test's property)
    assert!(
        !g.run(&["memory", "query", "integer cents", "--route", "semantic"])
            .ok(),
        "an unregistered descriptor revision executed"
    );
    crate::ws07::register_approved(&g, &root.join("governance/project/plugins/echo-local.yaml"));
    git_commit_all(&root, "descriptor revision 2 under a revision-1 pin");
    let q = g.err(&["memory", "query", "integer cents", "--route", "semantic"]);
    assert_eq!(
        q.error_code(),
        "EMBEDDER_REVISION_MISMATCH",
        "{}",
        q.envelope
    );
    assert_eq!(
        g.err(&["rebuild-memory"]).error_code(),
        "EMBEDDER_REVISION_MISMATCH"
    );
    assert!(!g.ok(&["memory", "freshness"])["pin_mismatch"]
        .as_array()
        .unwrap()
        .is_empty());
}

/// BC-P2-30 (A0-D5-02) and WS-3 IP-8: a profile change needs T2-bound benchmark evidence of the chosen candidate,
/// the change-control gate for its radius answered by the human through the owner-signed channel, a full re-index
/// and a recorded held-out regression; the decision asserts only that; a pin edited outside it is detected.
#[test]
fn a_profile_change_needs_evidence_the_radius_gate_and_a_recorded_regression() {
    let (root, g) = setup_fixture("greenfield", "ws06-select", "S-ws06");
    let r = g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "s",
        "--alias",
        "s-alias",
    ]);
    assert!(r["heldout_generated"].as_u64().unwrap() >= 5, "{r}");
    assert_eq!(
        g.err(&["memory", "select", "builtin:64"]).error_code(),
        "PROFILE_EVIDENCE_REQUIRED"
    );
    let b = g.ok(&[
        "memory",
        "benchmark",
        "--candidate",
        "current",
        "--candidate",
        "builtin:64",
        "--record",
    ]);
    let res = b["research_record"].as_str().unwrap().to_string();
    let rec = yaml(&root, &format!("spec/research/{res}.yaml"));
    assert_eq!(rec["version"], "1");
    assert_eq!(rec["content_hash"].as_str().unwrap().len(), 64, "IP-13");
    assert!(
        rec["os_binding"].is_object(),
        "the evidence is sealed (T2): {rec}"
    );
    for row in rec["measurements"]["rows"].as_array().unwrap() {
        assert_eq!(row["profile"]["digest"].as_str().unwrap().len(), 64);
    }
    // a hand-written copy of the evidence is not evidence
    let mut forged = rec.clone();
    forged["id"] = json!("RES-0900");
    forged.as_object_mut().unwrap().remove("os_binding");
    write_yaml(&root, "spec/research/RES-0900.yaml", &forged);
    assert_eq!(
        g.err(&["memory", "select", "builtin:64", "--research", "RES-0900"])
            .error_code(),
        "PROFILE_EVIDENCE_UNBOUND"
    );
    std::fs::remove_file(root.join("spec/research/RES-0900.yaml")).unwrap();
    // evidence that never measured the candidate
    assert_eq!(
        g.err(&["memory", "select", "builtin:32", "--research", &res])
            .error_code(),
        "PROFILE_EVIDENCE_STALE"
    );
    // the first call raises the change-control gate and applies nothing
    let before = read(&root, "governance/project/PROJECT_POLICY.yaml");
    let pending = g.ok(&["memory", "select", "builtin:64", "--research", &res]);
    assert_eq!(pending["applied"], false, "{pending}");
    assert_eq!(pending["impact_radius"], "R5");
    assert_eq!(pending["human_answer_required"], true);
    let gid = pending["human_gate"].as_str().unwrap().to_string();
    assert_eq!(
        read(&root, "governance/project/PROJECT_POLICY.yaml"),
        before
    );
    let gate = yaml(&root, &format!("spec/decisions/{gid}.yaml"));
    assert_eq!(gate["trigger"], "retrieval_profile_change");
    assert_eq!(
        gate["subject"]["sha256"], pending["subject_sha256"],
        "the gate binds this exact change"
    );
    // asking again re-reports the same gate
    assert_eq!(
        g.ok(&["memory", "select", "builtin:64", "--research", &res])["human_gate"],
        json!(gid)
    );
    assert_eq!(
        g.err(&[
            "memory",
            "select",
            "builtin:64",
            "--research",
            &res,
            "--gate",
            &gid
        ])
        .error_code(),
        "GATE_NOT_ANSWERED"
    );
    // a declared human role cannot select (IP-8: human approval never comes from a role claim)
    assert_eq!(
        g.with_role("human")
            .err(&[
                "memory",
                "select",
                "builtin:64",
                "--research",
                &res,
                "--gate",
                &gid
            ])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    // an agent cannot resolve a radius-R5 change
    assert!(!g
        .run(&["decide", &gid, "--option", "A", "--by", "orchestrator"])
        .ok());
    crate::ws03::human_decide(&g, &gid, "A");
    let sel = g.ok(&[
        "memory",
        "select",
        "builtin:64",
        "--research",
        &res,
        "--gate",
        &gid,
    ]);
    assert_eq!(sel["applied"], true, "{sel}");
    assert_eq!(sel["human_approved"], true);
    let did = sel["decision"].as_str().unwrap().to_string();
    let aid = sel["audit"].as_str().unwrap().to_string();
    let dec = yaml(&root, &format!("spec/decisions/{did}.yaml"));
    assert_eq!(dec["human_approved"], true);
    assert_eq!(dec["approved_by_kind"], "human");
    assert_eq!(dec["chosen_option"], "A");
    let derived: Vec<String> = dec["derived_from"]
        .as_array()
        .unwrap()
        .iter()
        .map(|x| x.as_str().unwrap().to_string())
        .collect();
    assert_eq!(derived, vec![gid.clone(), res.clone(), aid.clone()]);
    assert!(dec["rationale"].as_str().unwrap().contains(&res));
    assert!(dec["rationale"].as_str().unwrap().contains(&aid));
    assert_eq!(dec["retrieval_profile"]["digest"], sel["profile"]);
    let aud = yaml(&root, &format!("spec/audits/{aid}.yaml"));
    assert_eq!(aud["scope"], "retrieval-profile-regression");
    assert_eq!(aud["verdict"], "PASS");
    assert_eq!(aud["result"]["measured"], true);
    assert_eq!(
        yaml(&root, "governance/project/PROJECT_POLICY.yaml")["policy_overrides"]
            ["MEMORY_POLICY.embedding.dimensions"],
        64
    );
    let prof = g.ok(&["memory", "profile"]);
    assert_eq!(prof["state"], "GOVERNED", "{prof}");
    assert_eq!(prof["decision"], json!(did));
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);
    // an applied gate authorises nothing more, and an answer binds exactly the change it approved
    let bench = |cand: &str| -> String {
        g.ok(&[
            "memory",
            "benchmark",
            "--candidate",
            "current",
            "--candidate",
            cand,
            "--record",
        ])["research_record"]
            .as_str()
            .unwrap()
            .to_string()
    };
    let res2 = bench("builtin:32");
    assert_eq!(
        g.err(&[
            "memory",
            "select",
            "builtin:32",
            "--research",
            &res2,
            "--gate",
            &gid
        ])
        .error_code(),
        "GATE_ALREADY_APPLIED"
    );
    let gid2 = g.ok(&["memory", "select", "builtin:32", "--research", &res2])["human_gate"]
        .as_str()
        .unwrap()
        .to_string();
    crate::ws03::human_decide(&g, &gid2, "A");
    let res3 = bench("builtin:32");
    assert_eq!(
        g.err(&[
            "memory",
            "select",
            "builtin:32",
            "--research",
            &res3,
            "--gate",
            &gid2
        ])
        .error_code(),
        "APPROVAL_STALE"
    );
    // a pin edited directly in the overlay is not governed, and the product says so
    set_overrides(&root, json!({"MEMORY_POLICY.embedding.dimensions": 16}));
    git_commit_all(&root, "direct pin edit");
    let rb = g.ok(&["rebuild-memory"]);
    assert_eq!(
        rb["retrieval_profile"]["state"], "UNGOVERNED_CHANGE",
        "{}",
        rb["retrieval_profile"]
    );
    let prof = g.ok(&["memory", "profile"]);
    assert_eq!(prof["state"], "UNGOVERNED_CHANGE");
    assert!(prof["message"].as_str().unwrap().contains(&did));
}

/// BC-P2-28: graph integrity raises orphan, dangling, stale, reversed and ill-typed relationships and supersession
/// cycles as findings, on every build and on demand; a well-formed chain raises nothing.
#[test]
fn graph_integrity_raises_orphan_stale_reversed_ill_typed_and_cycles() {
    let (root, g) = setup_fixture("greenfield", "ws06-integrity", "S-ws06");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "i",
        "--alias",
        "i-alias",
        "--skip-index",
    ]);
    let rec = |rel: &str, v: Value| write_yaml(&root, rel, &v);
    // a well-formed chain
    rec(
        "spec/features/F-0001.yaml",
        json!({"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE"}),
    );
    rec(
        "spec/requirements/REQ-0001.yaml",
        json!({"id": "REQ-0001", "type": "requirement", "title": "Integer cents", "status": "ACTIVE", "kind": "functional", "feature": "F-0001", "validated_by": ["TST-0001"]}),
    );
    rec(
        "spec/tasks/TST-0001.yaml",
        json!({"id": "TST-0001", "type": "test-obligation", "title": "Cents test", "status": "ACTIVE", "tests": ["REQ-0001"]}),
    );
    rec(
        "spec/architecture/ARCH-0001.yaml",
        json!({"id": "ARCH-0001", "type": "architecture", "title": "Ledger", "status": "ACTIVE", "implements": ["REQ-0001"]}),
    );
    rec(
        "spec/decisions/D-0001.yaml",
        json!({"id": "D-0001", "type": "decision", "title": "Old", "status": "SUPERSEDED", "question": "q?"}),
    );
    rec(
        "spec/decisions/D-0002.yaml",
        json!({"id": "D-0002", "type": "decision", "title": "New", "status": "ACTIVE", "question": "q?", "supersedes": ["D-0001"]}),
    );
    // faults
    rec(
        "spec/features/F-0002.yaml",
        json!({"id": "F-0002", "type": "feature", "title": "Governed by an old decision", "status": "ACTIVE", "decisions": ["D-0001"]}),
    );
    rec(
        "spec/requirements/REQ-0002.yaml",
        json!({"id": "REQ-0002", "type": "requirement", "title": "Reversed", "status": "ACTIVE", "feature": "F-0001", "relations": [{"type": "IMPLEMENTS", "target": "ARCH-0001"}, {"type": "TESTS", "target": "TST-0001"}]}),
    );
    rec(
        "spec/requirements/REQ-0003.yaml",
        json!({"id": "REQ-0003", "type": "requirement", "title": "Orphan", "status": "ACTIVE", "kind": "functional"}),
    );
    rec(
        "spec/architecture/ARCH-0002.yaml",
        json!({"id": "ARCH-0002", "type": "architecture", "title": "Ill-typed", "status": "ACTIVE", "relations": [{"type": "CALLS", "target": "REQ-0001"}]}),
    );
    rec(
        "spec/decisions/D-0003.yaml",
        json!({"id": "D-0003", "type": "decision", "title": "Cycle a", "status": "ACTIVE", "question": "q?", "supersedes": ["D-0004"]}),
    );
    rec(
        "spec/decisions/D-0004.yaml",
        json!({"id": "D-0004", "type": "decision", "title": "Cycle b", "status": "ACTIVE", "question": "q?", "supersedes": ["D-0003"]}),
    );
    rec(
        "spec/requirements/REQ-0004.yaml",
        json!({"id": "REQ-0004", "type": "requirement", "title": "Dangling", "status": "ACTIVE", "feature": "F-0001", "depends_on": ["REQ-9999"]}),
    );
    git_commit_all(&root, "graph");
    let built = g.ok(&["rebuild-memory"]);
    assert_eq!(
        built["graph_integrity"]["ok"], false,
        "{}",
        built["graph_integrity"]
    );
    let r = g.ok(&["memory", "integrity"]);
    let k = kinds(&r);
    for want in [
        "orphan",
        "dangling",
        "stale",
        "reversed",
        "ill_typed",
        "supersession_cycle",
    ] {
        assert!(k.iter().any(|x| x == want), "{want} not raised: {r}");
    }
    let msgs = |kind: &str| -> String {
        findings_of(&r, kind)
            .iter()
            .map(|f| f["message"].as_str().unwrap().to_string())
            .collect::<Vec<_>>()
            .join(" | ")
    };
    assert!(msgs("orphan").contains("REQ-0003"), "{}", msgs("orphan"));
    assert!(msgs("stale").contains("F-0002") && msgs("stale").contains("D-0001"));
    assert_eq!(findings_of(&r, "reversed").len(), 2, "{}", msgs("reversed"));
    assert!(msgs("reversed").contains("REQ-0002"));
    assert!(msgs("ill_typed").contains("ARCH-0002") && msgs("ill_typed").contains("CALLS"));
    assert!(msgs("dangling").contains("REQ-9999"));
    assert!(msgs("supersession_cycle").contains("D-0003"));
    // the well-formed chain raises nothing
    for f in r["findings"].as_array().unwrap() {
        let rec = f["record"].as_str().unwrap_or("");
        assert!(
            !["F-0001", "REQ-0001", "TST-0001", "ARCH-0001", "D-0002"].contains(&rec),
            "{f}"
        );
    }
    // repaired, the graph is clean again
    for f in ["F-0002", "REQ-0002", "ARCH-0002"] {
        let dir = if f.starts_with('F') {
            "features"
        } else if f.starts_with("REQ") {
            "requirements"
        } else {
            "architecture"
        };
        std::fs::remove_file(root.join(format!("spec/{dir}/{f}.yaml"))).unwrap();
    }
    for f in ["D-0003", "D-0004"] {
        std::fs::remove_file(root.join(format!("spec/decisions/{f}.yaml"))).unwrap();
    }
    rec(
        "spec/requirements/REQ-0003.yaml",
        json!({"id": "REQ-0003", "type": "requirement", "title": "Now related", "status": "ACTIVE", "feature": "F-0001"}),
    );
    rec(
        "spec/requirements/REQ-0004.yaml",
        json!({"id": "REQ-0004", "type": "requirement", "title": "Resolved", "status": "ACTIVE", "feature": "F-0001", "depends_on": ["REQ-0001"]}),
    );
    git_commit_all(&root, "repaired");
    let built = g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(
        built["graph_integrity"]["ok"], true,
        "{}",
        built["graph_integrity"]
    );
    assert!(g.ok(&["memory", "integrity"])["findings"]
        .as_array()
        .unwrap()
        .is_empty());
}

/// BC-P2-31: the product never classifies claims, emergency-control state or the OS plugin registry as derived or
/// generated, wherever their writers keep them; deleting every file it does classify derived or generated keeps them
/// (and a full rebuild restores everything else). Until the writers relocate (integration points), the stores still
/// found in the derived runtime directory are reported.
#[test]
fn deleting_everything_classified_derived_keeps_claims_control_and_registration() {
    let (root, g) = setup_fixture("greenfield", "ws06-state", "S-ws06");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "st",
        "--alias",
        "st-alias",
    ]);
    // round-2 integration (P2-AR-0032): WS-5 (BC-P2-16) — an implementation task is claimable only when the DAG finds
    // it runnable, which needs its scenarios and acceptance tests declared
    let inputs = crate::ws05::traceable_inputs(&root, "0600");
    git_commit_all(&root, "traceable inputs");
    g.ok(&["rebuild-memory", "--incremental"]);
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "implementation",
        "--objective",
        "Totals",
        "--status",
        "READY",
        "--allowed",
        "src/**",
        "--fields",
        &inputs.to_string(),
    ]);
    let tid = t["id"].as_str().unwrap().to_string();
    g.ok(&["task", "claim", &tid]);
    write(&root, "tools/rr/rerank.sh", "#!/usr/bin/env bash\ncat >/dev/null; printf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"outputs\":{\"scores\":[]}}'\n");
    let df = root.parent().unwrap().join("ws06-state-rerank.yaml");
    std::fs::write(&df, "plugin_id: shell-rerank\ncapability: rerank\nversion: \"1\"\ncommand: [\"bash\", \"tools/rr/rerank.sh\"]\nlanguages: []\n").unwrap();
    // round-2 integration (P2-AR-0032): WS-7 (BC-P2-11 plugin side) — the registration is approved by the owner's
    // answer to the gate raised for exactly it
    let reg = crate::ws07::register_approved(&g, &df);
    assert_eq!(reg["registered"], true, "{reg}");
    git_commit_all(&root, "live state");
    g.ok(&["rebuild-memory"]);
    g.ok(&[
        "freeze-writes",
        "--reason",
        "ws06: emergency state must survive derived-state deletion",
    ]);

    let p = gov_runtime::Project::open(&root);
    let contract = p.contract();
    for s in gov_runtime::paths::OS_STORES {
        for (legacy, target) in s.moves {
            for rel in [legacy, target] {
                let probe = if root.join(rel).is_dir() {
                    format!("{rel}/x.json")
                } else {
                    rel.to_string()
                };
                let class = contract.decide(&probe).class();
                assert!(
                    class == "operational" || class == "authoritative",
                    "{} at {probe}: {class}",
                    s.id
                );
            }
        }
    }
    let del = gov_runtime::paths::derived_deletion_set(&root, contract);
    assert!(
        del.iter().any(|f| f == ".governance-runtime/state.db"),
        "{del:?}"
    );
    assert!(
        del.iter()
            .any(|f| f == "governance/generated/index-manifest.json"),
        "{del:?}"
    );
    for f in &del {
        assert!(
            !f.contains("claims.db")
                && !f.ends_with("control.json")
                && !f.ends_with("plugin-registry.json"),
            "{f} would be deleted as derived"
        );
    }
    let misplaced: Vec<String> = gov_runtime::paths::misplaced_os_state(&root)
        .iter()
        .map(|m| m["store"].as_str().unwrap().to_string())
        .collect();
    // round 3 (WS-3, BC-P2-31 / WS-6 IP-R2-8): the emergency-control writer now keeps its state where it belongs
    // (`paths::store_path(root, "emergency-control")`), so it is no longer misplaced; a store whose writer still keeps
    // it in the legacy location is reported, and exactly then
    assert!(
        exists(&root, ".governance-state/control.json")
            && !exists(&root, ".governance-runtime/control.json"),
        "the freeze is recorded in the operational store"
    );
    for s in gov_runtime::paths::OS_STORES {
        let legacy_present = s.moves.iter().any(|(from, _)| root.join(from).exists());
        assert_eq!(
            misplaced.iter().any(|m| m == s.id),
            legacy_present,
            "{} is reported exactly while its writer keeps it in the legacy location: {misplaced:?}",
            s.id
        );
    }
    // round 3 (P2-AR-0036, BC-P2-31): the claims store's writer (WS-5) keeps it where it belongs,
    // `paths::store_path(root, "claims")`, so it is no longer misplaced — and it lives outside every directory the
    // product classifies derived or generated
    assert!(
        !misplaced.iter().any(|m| m == "claims"),
        "the claims store is at its BC-P2-31 location: {misplaced:?}"
    );
    assert!(exists(&root, ".governance-state/claims.db"));
    for f in &del {
        std::fs::remove_file(root.join(f)).unwrap();
    }
    // what the product classifies derived is gone; claims, the freeze and the registration are not
    let st = g.ok(&["status"]);
    assert_eq!(st["control"]["writes_frozen"], true, "{}", st["control"]);
    let claims = g.ok(&["claims", "list"]);
    assert!(
        claims
            .as_array()
            .unwrap()
            .iter()
            .any(|c| c["task_id"] == json!(tid)),
        "{claims}"
    );
    assert!(
        json(&root, "governance/generated/plugin-registry.json")["plugins"]["shell-rerank"]
            .is_object()
    );
    g.ok(&["resume"]);
    // the claim still binds: another session cannot take the task
    assert!(!g.with_session("S-other").run(&["task", "claim", &tid]).ok());
    let rb = g.ok(&["rebuild-memory"]);
    assert_eq!(rb["mode"], "full");
    assert!(exists(&root, "governance/generated/index-manifest.json"));
    assert!(g
        .ok(&["claims", "list"])
        .as_array()
        .unwrap()
        .iter()
        .any(|c| c["task_id"] == json!(tid)));
}
