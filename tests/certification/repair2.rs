//! Builder regression tests for every root cause repaired after the independent re-verification of 4.1.3
//! (release/verification/4.1.3/INDEPENDENT_REVERIFICATION_REPORT.md §11–§12). Each test names the finding it covers and
//! exercises the adjacent bypass routes, not only the verifier's exact input.
use crate::common::*;
use serde_json::{json, Value};
use std::path::Path;

fn set_overrides(root: &Path, over: Value) {
    let mut pp = yaml(root, "governance/project/PROJECT_POLICY.yaml");
    pp["policy_overrides"] = over;
    write_yaml(root, "governance/project/PROJECT_POLICY.yaml", &pp);
}
fn manifest_file(root: &Path, name: &str, path: &str) -> String {
    let mf = root
        .join(".governance-runtime")
        .join(format!("{name}.json"));
    std::fs::create_dir_all(mf.parent().unwrap()).unwrap();
    std::fs::write(
        &mf,
        json!([{"op": "write_file", "path": path, "content": format!("// {name}\n")}]).to_string(),
    )
    .unwrap();
    mf.to_string_lossy().to_string()
}
fn security_cit(g: &Gov, root: &Path, name: &str) -> (String, String) {
    let mf = manifest_file(root, name, &format!("src/{name}.rs"));
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        &format!("security change {name}"),
        "--trigger",
        "security_change",
        "--manifest",
        &mf,
    ]);
    let cid = c["id"].as_str().unwrap().to_string();
    if c["cit_status"] != "SIMULATED" {
        g.ok(&["cit", "simulate", &cid]);
    }
    let gate = g.ok(&["cit", "show", &cid])["human_gate"]
        .as_str()
        .unwrap()
        .to_string();
    (cid, gate)
}
fn write_exec(root: &Path, rel: &str, text: &str) -> String {
    write(root, rel, text);
    use std::os::unix::fs::PermissionsExt;
    std::fs::set_permissions(root.join(rel), std::fs::Permissions::from_mode(0o755)).unwrap();
    root.join(rel).to_string_lossy().to_string()
}
fn plugin_script(root: &Path, rel: &str, marker: &Path) -> String {
    write_exec(root, rel, &format!("#!/bin/sh\ncat >/dev/null\necho ran >> '{}'\nprintf '{{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{{\"id\":\"p\",\"version\":\"1\"}},\"outputs\":{{\"vectors\":[],\"dim\":8}}}}'\n", marker.display()))
}

/// C-N1 / NV-01: CIT approval and execution derive from the authoritative gate answer; presentation, a decline, a
/// forged approval object, a revoked gate and an insufficient role never become approval.
#[test]
fn cit_approval_derives_only_from_an_answered_gate() {
    let (root, g) = setup_fixture("greenfield", "rep2-cit", "S-rep2");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "c",
        "--alias",
        "c-alias",
    ]);
    // (a) presented but unanswered
    let (cid, gate) = security_cit(&g, &root, "hdr1");
    assert_eq!(
        g.err(&["cit", "approve", &cid, "--by", "owner", "--method", "human"])
            .error_code(),
        "GATE_NOT_PRESENTED"
    );
    // (WS-3 / BC-P2-10: a gate counts as presented to the human only on the owner's signed receipt)
    crate::ws03::human_receipt(&g, &gate);
    let e = g.err(&["cit", "approve", &cid, "--by", "owner", "--method", "human"]);
    assert_eq!(e.error_code(), "GATE_NOT_ANSWERED", "{}", e.envelope);
    assert_eq!(
        yaml(&root, &format!("spec/decisions/{cid}.yaml"))["cit_status"],
        "SIMULATED"
    );
    assert!(
        !exists(&root, "spec/decisions/D-0001.yaml"),
        "approve must not fabricate a decision record"
    );
    // (c) an L3 agent role with a presented, unanswered gate
    assert_eq!(
        g.with_role("change-controller")
            .err(&["cit", "approve", &cid, "--by", "someone", "--method", "human"])
            .error_code(),
        "GATE_NOT_ANSWERED"
    );
    assert_eq!(
        g.with_role("backend-engineer")
            .err(&["cit", "approve", &cid, "--by", "someone", "--method", "human"])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    // forged approval object written straight into the record: execution revalidates the gate and refuses
    let mut c = yaml(&root, &format!("spec/decisions/{cid}.yaml"));
    c["cit_status"] = json!("APPROVED");
    c["approval"] = json!({"gate": gate, "decision": "D-9999", "method": "human", "human_approved": true, "answered_by": "forged", "answered_at": "2026-01-01T00:00:00Z"});
    write_yaml(&root, &format!("spec/decisions/{cid}.yaml"), &c);
    let e = g.err(&["cit", "execute", &cid]);
    assert_eq!(e.error_code(), "GATE_NOT_ANSWERED", "{}", e.envelope);
    assert!(!exists(&root, "src/hdr1.rs"));
    c["cit_status"] = json!("SIMULATED");
    c.as_object_mut().unwrap().remove("approval");
    write_yaml(&root, &format!("spec/decisions/{cid}.yaml"), &c);
    // (b) the human declines: the transaction is REJECTED, durably, and nothing can execute it
    let d = crate::ws03::human_decide(&g, &gate, "B");
    assert_eq!(d["option"], "B");
    let rec = yaml(&root, &format!("spec/decisions/{cid}.yaml"));
    assert_eq!(rec["cit_status"], "REJECTED", "{rec}");
    assert!(rec["journal"].to_string().contains("rejected_by_gate"));
    assert!(!g
        .run(&["cit", "approve", &cid, "--by", "owner", "--method", "human"])
        .ok());
    assert!(!g.run(&["cit", "execute", &cid]).ok());
    assert!(
        !exists(&root, "src/hdr1.rs"),
        "a declined CIT must never write its manifest"
    );
    let dec = yaml(
        &root,
        &format!("spec/decisions/{}.yaml", d["decision"].as_str().unwrap()),
    );
    assert_eq!(dec["chosen_option"], "B");
    assert_eq!(dec["declined"], true);
    // a forged decision cannot resurrect it: status is REJECTED so approve is refused before any gate check
    // (d) the correct path: presented + answered A -> approval carries the full trail; execute revalidates
    let (cid2, gate2) = security_cit(&g, &root, "hdr2");
    g.ok(&["gate", "present", &gate2]);
    let d2 = crate::ws03::human_decide(&g, &gate2, "A");
    let ap = g.ok(&["cit", "approve", &cid2, "--by", "owner", "--method", "auto"]);
    assert_eq!(
        ap["method"], "human",
        "approval method is derived from the answer kind, not the caller flag"
    );
    assert_eq!(ap["decision"], d2["decision"]);
    assert_eq!(ap["human_approved"], true);
    let rec2 = yaml(&root, &format!("spec/decisions/{cid2}.yaml"));
    for k in [
        "gate",
        "decision",
        "answered_by",
        "answered_by_kind",
        "answered_at",
        "presented_at",
        "presented_by",
        "recorded_by_session",
        "recorded_by_role",
    ] {
        assert!(
            !rec2["approval"][k].is_null(),
            "approval trail lacks {k}: {}",
            rec2["approval"]
        );
    }
    assert_eq!(rec2["approval"]["answered_by_kind"], "human");
    assert_eq!(
        yaml(
            &root,
            &format!("spec/decisions/{}.yaml", d2["decision"].as_str().unwrap())
        )["human_approved"],
        true
    );
    // (e) revoked before execution: approval evaporates; execution refuses; approval again refuses (GATE_REVOKED)
    let rv =
        g.with_role("orchestrator")
            .ok(&["gate", "revoke", &gate2, "--reason", "changed my mind"]);
    assert_eq!(rv["gate_status"], "WITHDRAWN");
    assert_eq!(
        yaml(&root, &format!("spec/decisions/{cid2}.yaml"))["cit_status"],
        "SIMULATED"
    );
    assert!(!g.run(&["cit", "execute", &cid2]).ok());
    assert_eq!(
        g.err(&["cit", "approve", &cid2, "--by", "owner", "--method", "human"])
            .error_code(),
        "GATE_REVOKED"
    );
    assert!(!exists(&root, "src/hdr2.rs"));
    assert_eq!(
        g.err(&["gate", "revoke", &gate2, "--reason", "x"])
            .error_code(),
        "USAGE",
        "already withdrawn"
    );
    assert_eq!(
        g.with_role("backend-engineer")
            .err(&["gate", "revoke", &gate, "--reason", "x"])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    // (f) stale approval: approved, then the gate is re-answered by editing the record -> execution refuses
    let (cid3, gate3) = security_cit(&g, &root, "hdr3");
    g.ok(&["gate", "present", &gate3]);
    crate::ws03::human_decide(&g, &gate3, "A");
    g.ok(&[
        "cit", "approve", &cid3, "--by", "owner", "--method", "human",
    ]);
    // WS-3 / BC-P2-09: a gate answer can no longer be changed by editing the record at all — the edited record is
    // not what gov wrote (T2), so execution refuses it before reading any answer field (previously APPROVAL_STALE /
    // GATE_DECLINED, derived from the edited fields themselves).
    let mut gr = yaml(&root, &format!("spec/decisions/{gate3}.yaml"));
    gr["answer"]["at"] = json!("2030-01-01T00:00:00Z");
    write_yaml(&root, &format!("spec/decisions/{gate3}.yaml"), &gr);
    assert_eq!(g.err(&["cit", "execute", &cid3]).error_code(), "T2_UNBOUND");
    gr["answer"]["option"] = json!("B");
    write_yaml(&root, &format!("spec/decisions/{gate3}.yaml"), &gr);
    assert_eq!(g.err(&["cit", "execute", &cid3]).error_code(), "T2_UNBOUND");
    assert!(!exists(&root, "src/hdr3.rs"));
    // (g) the automatic path never claims human approval
    let mf = root.join(".governance-runtime/ed.json");
    std::fs::write(
        &mf,
        json!([{"op": "write_file", "path": "spec/now/NOW.md", "content": "# NOW\nedit\n"}])
            .to_string(),
    )
    .unwrap();
    let c4 = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "editorial",
        "--trigger",
        "editorial",
        "--manifest",
        mf.to_str().unwrap(),
    ]);
    let cid4 = c4["id"].as_str().unwrap().to_string();
    if c4["cit_status"] != "SIMULATED" {
        g.ok(&["cit", "simulate", &cid4]);
    }
    let ap4 = g.ok(&[
        "cit", "approve", &cid4, "--by", "owner", "--method", "human",
    ]);
    assert_eq!(ap4["method"], "auto");
    assert_eq!(ap4["human_approved"], false);
    assert_eq!(
        yaml(
            &root,
            &format!("spec/decisions/{}.yaml", ap4["decision"].as_str().unwrap())
        )["human_approved"],
        false
    );
    let ex4 = g.ok(&["cit", "execute", &cid4]);
    assert_eq!(ex4["cit_status"], "COMMITTED");
}

/// H-N1 / NV-02: PROJECT_POLICY overrides and PROJECT_EXCEPTIONS may only specialise or strengthen; every weakening of
/// authority, sensitivity, human-gate, change-control or export floors is refused, reported and auditable.
#[test]
fn project_policy_cannot_weaken_constitutional_floors() {
    let (root, g) = setup_fixture("greenfield", "rep2-prec", "S-rep2");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "p",
        "--alias",
        "p-alias",
        "--skip-index",
    ]);
    set_overrides(
        &root,
        json!({
            "AUTHORITY_POLICY.authority_levels_required.create_task": "L0", "AUTHORITY_POLICY.authority_levels_required.execute_cit": "L0", "AUTHORITY_POLICY.authority_levels_required.install_kernel": "L0",
            "SECURITY_POLICY.never_index_classes": [], "SECURITY_POLICY.never_export_classes": [], "SECURITY_POLICY.secret_content_patterns": [],
            "HUMAN_GATE_POLICY.must_be_presented_in_chat": false, "HUMAN_GATE_POLICY.agent_resolvable_when.max_radius": "R5",
            "CHANGE_POLICY.auto_approve_max_radius": "R5", "CHANGE_POLICY.human_gate_triggers": [], "CHANGE_POLICY.rollback.snapshot_before_execute": false,
            "LEARNING_POLICY.upstream.approval": "agent", "ARCHIVE_POLICY.archive_mutation": "free", "TEST_POLICY.task_close_requires_tests_status": ["passed", "skipped", "anything"],
            "MEMORY_POLICY.retrieval.default_k": 5, "AUTHORITY_POLICY.authority_levels_required.claim_task": "L2", "SECURITY_POLICY.never_index_classes": ["secret", "restricted", "confidential"], "CHANGE_POLICY.auto_approve_max_radius": "R0"
        }),
    );
    // NB: duplicate JSON keys above resolve to the last value: never_index_classes strengthened, auto_approve_max_radius R0
    let mut ds = yaml(&root, "governance/project/DATA_SENSITIVITY.yaml");
    ds["classifications"] =
        json!([{"pattern": "product/data/**", "class": "restricted", "reason": "customer data"}]);
    write_yaml(&root, "governance/project/DATA_SENSITIVITY.yaml", &ds);
    write(
        &root,
        "product/data/customers.md",
        "# customers\nZULUQUARTZ7 must never be retrievable.\n",
    );
    git_commit_all(&root, "override attempt");
    let ov = g.ok(&["policy", "overrides"]);
    let refused: Vec<String> = ov["refused"]
        .as_array()
        .unwrap()
        .iter()
        .map(|r| {
            format!(
                "{}.{}",
                r["policy"].as_str().unwrap(),
                r["key"].as_str().unwrap()
            )
        })
        .collect();
    for k in [
        "AUTHORITY_POLICY.authority_levels_required.create_task",
        "AUTHORITY_POLICY.authority_levels_required.execute_cit",
        "AUTHORITY_POLICY.authority_levels_required.install_kernel",
        "SECURITY_POLICY.never_export_classes",
        "SECURITY_POLICY.secret_content_patterns",
        "HUMAN_GATE_POLICY.must_be_presented_in_chat",
        "HUMAN_GATE_POLICY.agent_resolvable_when.max_radius",
        "CHANGE_POLICY.human_gate_triggers",
        "CHANGE_POLICY.rollback.snapshot_before_execute",
        "LEARNING_POLICY.upstream.approval",
        "ARCHIVE_POLICY.archive_mutation",
        "TEST_POLICY.task_close_requires_tests_status",
    ] {
        assert!(
            refused.contains(&k.to_string()),
            "{k} must be refused; refused = {refused:?}"
        );
    }
    let applied: Vec<String> = ov["applied"]
        .as_array()
        .unwrap()
        .iter()
        .map(|r| {
            format!(
                "{}.{}",
                r["policy"].as_str().unwrap(),
                r["key"].as_str().unwrap()
            )
        })
        .collect();
    for k in [
        "MEMORY_POLICY.retrieval.default_k",
        "AUTHORITY_POLICY.authority_levels_required.claim_task",
        "SECURITY_POLICY.never_index_classes",
        "CHANGE_POLICY.auto_approve_max_radius",
    ] {
        assert!(
            applied.contains(&k.to_string()),
            "{k} strengthens/specialises and must apply; applied = {applied:?}"
        );
    }
    let eff = g.ok(&["policy", "effective", "AUTHORITY_POLICY"]);
    assert_eq!(
        eff["effective"]["authority_levels_required"]["create_task"], "L2",
        "effective policy unchanged by the refused override"
    );
    assert_eq!(
        eff["effective"]["authority_levels_required"]["claim_task"], "L2",
        "strengthening override applied"
    );
    // executable consequences
    assert_eq!(
        g.with_role("independent-auditor")
            .err(&[
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
        g.with_role("backend-engineer")
            .err(&["task", "claim", "TASK-0001"])
            .error_code(),
        "AUTHORITY_DENIED",
        "raised floor L2 applies to L1 worker (task may not exist, but authority is checked first)"
    );
    let r = g.ok(&["rebuild-memory"]);
    assert!(
        r["excluded"]
            .to_string()
            .contains("product/data/customers.md"),
        "{}",
        r["excluded"]
    );
    let q = g.ok(&["memory", "query", "ZULUQUARTZ7", "--k", "5"]);
    assert!(q["hits"]
        .as_array()
        .unwrap()
        .iter()
        .all(|h| h["path"] != "product/data/customers.md"));
    // visible in doctor, the governance suite and the context packet. P2-AR-0026: the task is created (and its
    // packet compiled) before doctor records the CRITICAL D027 result, because task creation is guarded by the G0
    // hard-block tier contract (IP-WS02-02) and D027 critical hard-blocks every governed operation.
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "ctx",
        "--status",
        "READY",
    ]);
    let ctx = g.ok(&["context", "compile", t["id"].as_str().unwrap()]);
    let (ok27, msg27) = doctor_check(&g, "D027");
    assert!(!ok27, "{msg27}");
    // ... and the refused weakening now refuses new governed work until it is repaired (G0 hard-block)
    let hb = g.err(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "while weakened",
        "--status",
        "READY",
    ]);
    assert_eq!(hb.error_code(), "HEALTH_HARD_BLOCK", "{}", hb.envelope);
    assert!(hb.envelope.to_string().contains("D027"), "{}", hb.envelope);
    let au = g.run(&["audit", "--no-persist"]);
    let f = if au.ok() { au.result() } else { au.details() };
    let crit: Vec<&Value> = f["findings"]
        .as_array()
        .unwrap()
        .iter()
        .filter(|x| x["family"] == "policy_precedence" && x["severity"] == "critical")
        .collect();
    assert!(crit.len() >= 10, "{}", f["findings"]);
    let layer3 = ctx["deterministic_authority"]["authority_layers"]
        .as_array()
        .unwrap()
        .iter()
        .find(|l| l["layer"] == 3)
        .unwrap()
        .clone();
    assert!(
        layer3["policy_overrides_refused"].as_array().unwrap().len() >= 10,
        "{layer3}"
    );
    // exceptions follow the same rules and need a real governing decision (verifier V-M1). WS-3 / BC-P2-09: that
    // decision must be one a gov operation wrote — the human's owner-signed answer to a gate that asked for exactly
    // this scope — because a hand-written decision claiming human approval is a request, recorded and ignored.
    let eg = g.ok(&[
        "gate",
        "create",
        "--question",
        "Budget headroom for the migration window: may parallel agents exceed the default?",
        "--fields",
        &crate::ws03::package(
            json!({"decision_scope": {"authorises_exceptions": ["EXC-0001", "EXC-0003"]}}),
        ),
    ]);
    let dec_id = crate::ws03::human_decide(&g, eg["id"].as_str().unwrap(), "A")["decision"]
        .as_str()
        .unwrap()
        .to_string();
    let mut ex = yaml(&root, "governance/project/PROJECT_EXCEPTIONS.yaml");
    ex["exceptions"] = json!([
        {"id": "EXC-0001", "policy": "AUTHORITY_POLICY", "key": "authority_levels_required.create_task", "value": "L0", "decision": dec_id, "expires": "2999-01-01", "reason": "attempt"},
        {"id": "EXC-0002", "policy": "BUDGET_POLICY", "key": "defaults.max_parallel_agents", "value": 9, "expires": "2999-01-01", "reason": "no decision"},
        {"id": "EXC-0003", "policy": "BUDGET_POLICY", "key": "defaults.max_parallel_agents", "value": 9, "decision": dec_id, "expires": "2999-01-01", "reason": "relaxable with a decision"}
    ]);
    write_yaml(&root, "governance/project/PROJECT_EXCEPTIONS.yaml", &ex);
    let ov2 = g.ok(&["policy", "overrides"]);
    let src = |v: &Value, s: &str| v.as_array().unwrap().iter().any(|r| r["source"] == s);
    assert!(
        src(&ov2["refused"], "EXC-0001")
            && src(&ov2["refused"], "EXC-0002")
            && src(&ov2["applied"], "EXC-0003"),
        "{ov2}"
    );
    assert_eq!(
        g.with_role("independent-auditor")
            .err(&[
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
    // a clean overlay is HEALTHY on D027
    set_overrides(&root, json!({}));
    ex["exceptions"] = json!([]);
    write_yaml(&root, "governance/project/PROJECT_EXCEPTIONS.yaml", &ex);
    assert!(doctor_check(&g, "D027").0);
}

/// H-N2 / NV-04: plugin descriptors are governed executables — schema, registration, identity/version pin, content
/// pin, health, authority floor, approved roles, permission classes, elevated-permission gate; L0/L1 cannot execute.
#[test]
fn plugins_are_governed_capabilities_not_arbitrary_commands() {
    let (root, g) = setup_fixture("greenfield", "rep2-plug", "S-rep2");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "g",
        "--alias",
        "g-alias",
        "--skip-index",
    ]);
    let marker = root.join(".governance-runtime/ran.txt");
    let script = plugin_script(&root, ".governance-runtime/rogue.sh", &marker);
    let ran = || {
        std::fs::read_to_string(&marker)
            .map(|s| s.lines().count())
            .unwrap_or(0)
    };
    // malformed (no version): rejected by the schema, never executable by anyone
    write_yaml(
        &root,
        "governance/project/plugins/rogue.yaml",
        &json!({"plugin_id": "rogue", "capability": "embed", "command": [script]}),
    );
    let pl = g.ok(&["capabilities", "plugins"]);
    assert!(
        pl.as_array()
            .unwrap()
            .iter()
            .any(|x| x["plugin_id"] == "rogue" && x["status"] == "rejected")
            && !pl
                .as_array()
                .unwrap()
                .iter()
                .any(|x| x["status"] == "usable"),
        "{pl}"
    );
    assert_eq!(
        g.with_role("independent-auditor")
            .err(&[
                "capabilities",
                "invoke",
                "--plugin",
                "rogue",
                "--inputs",
                "{}"
            ])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        g.err(&[
            "capabilities",
            "invoke",
            "--plugin",
            "rogue",
            "--inputs",
            "{}"
        ])
        .error_code(),
        "PLUGIN_DESCRIPTOR_INVALID"
    );
    assert_eq!(ran(), 0, "a rejected descriptor must never execute");
    let (ok28, msg28) = doctor_check(&g, "D028");
    assert!(!ok28, "{msg28}");
    // valid but hand-declared (unregistered): only roles at/above TOOL_POLICY.plugins.min_authority (L2)
    write_yaml(
        &root,
        "governance/project/plugins/rogue.yaml",
        &json!({"plugin_id": "rogue", "capability": "embed", "version": "1", "command": [script]}),
    );
    assert_eq!(
        g.with_role("independent-auditor")
            .err(&[
                "capabilities",
                "invoke",
                "--plugin",
                "rogue",
                "--inputs",
                "{}"
            ])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        g.with_role("backend-engineer")
            .err(&[
                "capabilities",
                "invoke",
                "--plugin",
                "rogue",
                "--inputs",
                "{}"
            ])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(ran(), 0);
    // BC-P2-39 (repair iteration 1, WS-7): not even an L4 role executes a hand-declared EXECUTABLE plugin. Its
    // descriptor declares nothing elevated, but the OS cannot enforce what a spawned process does, so it runs only
    // once registered against a gate raised for exactly it. (Before WS-7: "an L4 role may execute a valid
    // hand-declared plugin" — the self-declared elevation A0-F4-03 found.)
    assert_eq!(
        g.err(&[
            "capabilities",
            "invoke",
            "--plugin",
            "rogue",
            "--inputs",
            "{}"
        ])
        .error_code(),
        "PLUGIN_NOT_APPROVED"
    );
    assert_eq!(ran(), 0);
    let rogue_desc = root.join("governance/project/plugins/rogue.yaml");
    crate::ws07::register_approved(&g, &rogue_desc);
    g.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "rogue",
        "--inputs",
        "{\"texts\": []}",
    ]);
    assert_eq!(
        ran(),
        1,
        "an L4 role may execute a registered, approved plugin"
    );
    // pinned as the embedder: an L0 rebuild must not trigger execution
    set_overrides(
        &root,
        json!({"MEMORY_POLICY.embedding.provider": "rogue", "MEMORY_POLICY.embedding.dimensions": 8}),
    );
    let e = g.with_role("independent-auditor").err(&["rebuild-memory"]);
    assert_eq!(e.error_code(), "AUTHORITY_DENIED", "{}", e.envelope);
    assert_eq!(ran(), 1, "pinned use by an L0 role executed the plugin");
    // the registry knows the plugin, the auditor's resolution shows the gap, tools list carries it
    let res = g.ok(&[
        "tools",
        "resolve",
        "--capability",
        "embed",
        "--role",
        "independent-auditor",
    ]);
    assert_eq!(res["capability_gap"], true);
    let res2 = g.ok(&[
        "tools",
        "resolve",
        "--capability",
        "embed",
        "--role",
        "orchestrator",
    ]);
    assert!(res2["tools"].to_string().contains("rogue"), "{res2}");
    // content pin drift: the implementation changes without a version change -> PLUGIN_PIN_MISMATCH
    write_exec(&root, ".governance-runtime/rogue.sh", &format!("#!/bin/sh\ncat >/dev/null\necho changed >> '{}'\nprintf '{{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{{\"id\":\"p\",\"version\":\"1\"}},\"outputs\":{{\"vectors\":[],\"dim\":8}}}}'\n", marker.display()));
    let e = g.err(&[
        "capabilities",
        "invoke",
        "--plugin",
        "rogue",
        "--inputs",
        "{\"texts\": []}",
    ]);
    assert_eq!(e.error_code(), "PLUGIN_PIN_MISMATCH", "{}", e.envelope);
    assert_eq!(ran(), 1);
    // BC-P2-40 (WS-7): a version bump no longer re-pins the implementation by itself (that was the machine-local
    // trust-on-first-use re-baseline A0-F4-04 found); the edited descriptor no longer matches its registration, and
    // only a new registration, approved through its own gate, binds the new implementation
    write_yaml(
        &root,
        "governance/project/plugins/rogue.yaml",
        &json!({"plugin_id": "rogue", "capability": "embed", "version": "2", "command": [script]}),
    );
    assert_eq!(
        g.err(&[
            "capabilities",
            "invoke",
            "--plugin",
            "rogue",
            "--inputs",
            "{}"
        ])
        .error_code(),
        "PLUGIN_REGISTRY_MISMATCH"
    );
    assert_eq!(ran(), 1);
    crate::ws07::register_approved(&g, &rogue_desc);
    g.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "rogue",
        "--inputs",
        "{\"texts\": []}",
    ]);
    assert_eq!(
        ran(),
        2,
        "an approved re-registration binds the new implementation"
    );
    // a pin written into a registered descriptor is an edit: it no longer matches its registration (the declared-pin
    // check itself is exercised on a hand-declared OS capability server in ws07)
    write_yaml(
        &root,
        "governance/project/plugins/rogue.yaml",
        &json!({"plugin_id": "rogue", "capability": "embed", "version": "2", "command": [script], "pin": {"sha256": "0000"}}),
    );
    assert_eq!(
        g.err(&[
            "capabilities",
            "invoke",
            "--plugin",
            "rogue",
            "--inputs",
            "{}"
        ])
        .error_code(),
        "PLUGIN_REGISTRY_MISMATCH"
    );
    // approved_roles restricts even high-authority roles
    write_yaml(
        &root,
        "governance/project/plugins/rogue.yaml",
        &json!({"plugin_id": "rogue", "capability": "embed", "version": "2", "command": [script], "approved_roles": ["tooling-engineer"]}),
    );
    crate::ws07::register_approved(&g, &rogue_desc);
    assert_eq!(
        g.err(&[
            "capabilities",
            "invoke",
            "--plugin",
            "rogue",
            "--inputs",
            "{}"
        ])
        .error_code(),
        "AUTHORITY_DENIED"
    );
    g.with_role("tooling-engineer").ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "rogue",
        "--inputs",
        "{\"texts\": []}",
    ]);
    // elevated permissions: hand-declared -> not approved; registration raises a gate; answered A -> registered and usable
    let net = json!({"plugin_id": "netembed", "capability": "embed", "version": "1", "command": [script], "required_permission_classes": ["NETWORK_READ"]});
    write_yaml(&root, "governance/project/plugins/netembed.yaml", &net);
    assert_eq!(
        g.err(&[
            "capabilities",
            "invoke",
            "--plugin",
            "netembed",
            "--inputs",
            "{}"
        ])
        .error_code(),
        "PLUGIN_NOT_APPROVED"
    );
    std::fs::remove_file(root.join("governance/project/plugins/netembed.yaml")).unwrap();
    let df = root.join(".governance-runtime/net.json");
    std::fs::write(&df, net.to_string()).unwrap();
    assert_eq!(
        g.with_role("backend-engineer")
            .err(&["plugins", "register", "--descriptor", df.to_str().unwrap()])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    let r = g.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    assert_eq!(r["registered"], false);
    let gate = r["human_gate"].as_str().unwrap().to_string();
    assert!(!exists(&root, "governance/project/plugins/netembed.yaml"));
    g.ok(&["gate", "present", &gate]);
    crate::ws03::human_decide(&g, &gate, "A");
    let mut net2 = net.clone();
    net2["registration_gate"] = json!(gate);
    std::fs::write(&df, net2.to_string()).unwrap();
    let r2 = g.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    assert_eq!(r2["registered"], true);
    assert!(
        r2["pin"]["sha256"]
            .as_str()
            .map(|s| s.len() == 64)
            .unwrap_or(false),
        "{r2}"
    );
    let reg = yaml(&root, "governance/project/plugins/netembed.yaml");
    assert_eq!(reg["provenance"]["gate"], gate);
    assert_eq!(reg["status"], "active");
    g.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "netembed",
        "--inputs",
        "{\"texts\": []}",
    ]);
    // registered with approved_roles: all, but a role lacking NETWORK_READ still may not trigger it
    assert_eq!(
        g.with_role("backend-engineer")
            .err(&[
                "capabilities",
                "invoke",
                "--plugin",
                "netembed",
                "--inputs",
                "{}"
            ])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        g.with_role("change-controller")
            .err(&[
                "capabilities",
                "invoke",
                "--plugin",
                "netembed",
                "--inputs",
                "{}"
            ])
            .error_code(),
        "PLUGIN_NOT_AUTHORIZED"
    );
    // health + registry listing
    let h = g.ok(&["plugins", "health"]);
    assert!(
        h.as_array()
            .unwrap()
            .iter()
            .any(|x| x["plugin_id"] == "netembed" && x["status"] == "healthy"),
        "{h}"
    );
    let reg_json = g.ok(&["tools", "registry"]);
    assert!(reg_json["tools"]
        .as_array()
        .unwrap()
        .iter()
        .any(|t| t["tool_id"] == "netembed" && t["type"] == "plugin"));
    let au = g.run(&["audit", "--no-persist", "--family", "plugin_governance"]);
    let f = if au.ok() { au.result() } else { au.details() };
    assert!(
        f["findings"]
            .as_array()
            .unwrap()
            .iter()
            .all(|x| x["family"] == "plugin_governance"),
        "{}",
        f["findings"]
    );
}

/// M-N1 / M-N2 / NV-08: framework.lock identifies the installed release (release commit, logical source) on every
/// install path and is identical across clones/paths apart from the consumer commit and timestamp.
#[test]
fn framework_lock_is_release_identifying_and_portable() {
    let rel = canonical_root().join("release/releases/4.1.3");
    let m = json(&rel, "manifest.json");
    // OWNER-DECISION-P2-0002: on a machine with no trust anchor the shipped 4.1.3 payload is external-source kernel
    // material and is refused before it is staged for installation; it gets no identity at all.
    let (root0, g0) = setup_fixture_unprovisioned("greenfield", "rep2-lock-unprov", "S-rep2");
    let e = g0.err(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "l0",
        "--alias",
        "l0-alias",
        "--skip-index",
    ]);
    assert_eq!(
        e.error_code(),
        "SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED",
        "{}",
        e.envelope
    );
    assert!(!exists(&root0, "governance/framework.lock") && !exists(&root0, "governance/kernel"));
    // provision, then install: the same payload, signed under the suite's throw-away root
    let (root, g) = setup_fixture("greenfield", "rep2-lock-rel", "S-rep2");
    let signed413 = signed_copy(&rel.join("kernel"), "rep2-lock-4.1.3", sequence_of("4.1.3"));
    g.ok(&[
        "init",
        "--source",
        signed413.to_str().unwrap(),
        "--name",
        "l",
        "--alias",
        "l-alias",
        "--skip-index",
    ]);
    let lock = yaml(&root, "governance/framework.lock");
    // BC-P2-37 (P2-AR-0020): the release's manifest.json is unsigned, so its release_commit is never recorded as
    // identity (Contract v3:149 "recorded, not invented"; D-0007 rule 2); the signed metadata binds none either. What
    // verification did establish — an authenticated release — is recorded, with its basis.
    assert_ne!(lock["release_commit"], m["release_commit"], "{lock}");
    assert_eq!(lock["release_commit"], "unverified", "{lock}");
    assert_eq!(lock["source"], "release:agentic-engineering-os@4.1.3");
    assert_eq!(lock["authenticity"], "AUTHENTIC", "{lock}");
    assert_eq!(lock["sequence"], sequence_of("4.1.3"), "{lock}");
    assert!(lock["identity_basis"]["release_commit"]
        .as_str()
        .unwrap()
        .contains("not recorded as identity"));
    assert_eq!(
        lock["installed_at_commit"].as_str().unwrap(),
        git(&root, &["rev-parse", "HEAD"]).1.trim()
    );
    assert_eq!(lock["lock_schema_version"], "1.1.0");
    assert!(!lock["source"].as_str().unwrap().starts_with('/'));
    // canonical checkout source: the framework tree's own commit, not the consumer's. UNPROVISIONED on purpose (this
    // and the next install are about the payload embedded in the binary, which OWNER-DECISION-P2-0002 admits on a
    // machine with no trust anchor as a marked bootstrap installation, whichever path delivers the same bytes).
    let (root2, g2) = setup_fixture_unprovisioned("greenfield", "rep2-lock-src", "S-rep2");
    g2.ok(&[
        "init",
        "--name",
        "l2",
        "--alias",
        "l2-alias",
        "--skip-index",
    ]);
    let lock2 = yaml(&root2, "governance/framework.lock");
    // BC-P2-37 (P2-AR-0020): identity is decided by content, never by where the bytes came from. The checkout's
    // payload is byte-identical to the payload embedded in this binary, so it records the embedded identity (equal to
    // lock3 below), not the checkout's unauthenticated Git HEAD — and still never the consumer's commit.
    assert_ne!(lock2["release_commit"], lock2["installed_at_commit"]);
    assert!(lock2["source"]
        .as_str()
        .unwrap()
        .starts_with("embedded:agentic-engineering-os@"));
    // embedded payload: the commit baked into the binary; still never the consumer's HEAD
    let (root3, g3) = setup_fixture_unprovisioned("greenfield", "rep2-lock-emb", "S-rep2");
    g3.with_env("GOV_CANONICAL_ROOT", "/nonexistent").ok(&[
        "init",
        "--name",
        "l3",
        "--alias",
        "l3-alias",
        "--skip-index",
    ]);
    let lock3 = yaml(&root3, "governance/framework.lock");
    for k in ["release_commit", "release_hash", "source", "version"] {
        assert_eq!(
            lock2[k], lock3[k],
            "same bytes, same recorded identity: {k}"
        );
    }
    assert!(lock3["source"]
        .as_str()
        .unwrap()
        .starts_with("embedded:agentic-engineering-os@"));
    assert_ne!(lock3["release_commit"], lock3["installed_at_commit"]);
    assert!(lock3["release_commit"].as_str().unwrap().len() >= 7);
    // two machines/paths: identical release identity
    let clone = tmp("rep2-lock-clone");
    copy_dir(&root, &clone);
    let lc = yaml(&clone, "governance/framework.lock");
    for k in [
        "release_commit",
        "release_hash",
        "source",
        "version",
        "kernel_manifest_hash",
    ] {
        assert_eq!(lc[k], lock[k]);
    }
    // the other path is another machine: it is provisioned and verifies the release the lock pins before it
    // relies on the installed kernel (ARCH-0003 §8); that verification writes nothing into the repository
    let gb = Gov::new(&clone, "S-b");
    provision(&gb);
    gb.ok(&[
        "kernel",
        "reinstall",
        "--source",
        signed413.to_str().unwrap(),
    ]);
    for k in [
        "release_commit",
        "release_hash",
        "source",
        "version",
        "kernel_manifest_hash",
    ] {
        assert_eq!(yaml(&clone, "governance/framework.lock")[k], lock[k]);
    }
    let d = gb.ok(&["doctor"]);
    assert!(
        d["checks"]
            .as_array()
            .unwrap()
            .iter()
            .any(|c| c["id"] == "D003" && c["ok"] == true),
        "{d}"
    );
}

/// M-N3 / M-N8 / NV-03 / NV-19 / L-N2: a consumer created from the immutable 4.1.2 payload updates through 4.1.3 to
/// 4.1.4 over the declared chain, reaching the correct final state (contract rule tightened, held-out file not
/// indexed, lock provenance right, overlay customisations preserved), and every rollback is ledgered and consumed.
#[test]
fn genuine_412_consumer_updates_through_413_to_414_and_rolls_back_with_ledger() {
    let rel412 = canonical_root().join("release/releases/4.1.2");
    let rel413 = canonical_root().join("release/releases/4.1.3");
    let (root, g) = setup_fixture("greenfield", "rep2-chain", "S-rep2");
    // provision, then install (OWNER-DECISION-P2-0002): the immutable shipped payloads, signed under the suite's
    // throw-away root in version order, then the current release
    let k412 = signed_copy(
        &rel412.join("kernel"),
        "rep2-chain-4.1.2",
        sequence_of("4.1.2"),
    );
    let k413 = signed_copy(
        &rel413.join("kernel"),
        "rep2-chain-4.1.3",
        sequence_of("4.1.3"),
    );
    let r = g.ok(&[
        "init",
        "--source",
        k412.to_str().unwrap(),
        "--name",
        "chain",
        "--alias",
        "fx-chain",
        "--intent",
        "orders ledger",
    ]);
    assert_eq!(r["version"], "4.1.2");
    set_overrides(&root, json!({"MEMORY_POLICY.retrieval.default_k": 5}));
    write_yaml(
        &root,
        "spec/decisions/D-0001.yaml",
        &json!({"id": "D-0001", "type": "decision", "title": "Use integer cents", "status": "ACTIVE", "question": "money type?", "chosen_option": "A", "rationale": "no floating point", "human_approved": true}),
    );
    write_yaml(
        &root,
        "governance/tests/memory/heldout.yaml",
        &json!({"version": "1", "queries": [{"id": "HQ-001", "query": "Use integer cents", "expected_refs": ["D-0001"], "forbidden": [], "k": 3}, {"id": "HQ-002", "query": "XYLOPHONE-HELDOUT-MARKER only in the held-out file", "expected_refs": ["D-0001"], "forbidden": [], "k": 3}]}),
    );
    g.ok(&["rebuild-memory"]);
    let rule_before = yaml(&root, "governance/project/REPOSITORY_CONTRACT.yaml")["paths"]
        .as_array()
        .unwrap()
        .iter()
        .find(|p| p["pattern"] == "governance/tests/**")
        .cloned()
        .unwrap();
    assert_eq!(
        rule_before["lexical_index"], true,
        "4.1.2 template indexed the held-out file"
    );
    git_commit_all(&root, "4.1.2 state");
    // gate records (HDG-*, their D-* decisions) are legitimate governance state written by the update gate flow;
    // decisions are compared explicitly below
    let spec_excl: &[&str] = &["audits/**", "reports/**", "decisions/**"];
    let spec_before = tree_hash(&root.join("spec"), spec_excl);
    let apply = |src: &Path| -> Value {
        let s = src.to_str().unwrap();
        let e = g.err(&["update", "--apply", "--source", s]);
        assert_eq!(e.error_code(), "HUMAN_GATE_REQUIRED");
        let gate = e.details()["gate"].as_str().unwrap().to_string();
        assert_eq!(
            g.ok(&[
                "update",
                "--apply",
                "--source",
                s,
                "--approve",
                "--by",
                "owner"
            ])["applied"],
            false
        );
        g.ok(&["gate", "present", &gate]);
        crate::ws03::human_decide(&g, &gate, "A");
        g.ok(&[
            "update",
            "--apply",
            "--source",
            s,
            "--approve",
            "--by",
            "owner",
        ])
    };
    // 4.1.2 -> 4.1.3 with the immutable 4.1.3 payload (its migration has no overlay op: reconciliation delivers it)
    let chk = g.ok(&["update", "--check", "--source", k413.to_str().unwrap()]);
    assert_eq!(chk["migration_path"], json!(["M-4.1.2-4.1.3"]));
    let a1 = apply(&k413);
    assert_eq!(a1["applied"], true);
    assert_eq!(a1["to"], "4.1.3");
    assert!(
        a1["details"]["overlay_reconciled"]
            .to_string()
            .contains("governance/tests/**"),
        "{}",
        a1["details"]
    );
    let lock = yaml(&root, "governance/framework.lock");
    assert_eq!(lock["version"], "4.1.3");
    // BC-P2-37 (P2-AR-0020): the 4.1.3 manifest.json is unsigned; its release_commit is not recorded as identity
    // (the signed metadata binds none). The release itself was verified against the trust anchor: `release:`.
    assert_ne!(
        lock["release_commit"],
        json(&rel413, "manifest.json")["release_commit"]
    );
    assert_eq!(lock["release_commit"], "unverified", "{lock}");
    assert_eq!(
        lock["source"], "release:agentic-engineering-os@4.1.3",
        "{lock}"
    );
    assert_eq!(lock["authenticity"], "AUTHENTIC");
    let rule = yaml(&root, "governance/project/REPOSITORY_CONTRACT.yaml")["paths"]
        .as_array()
        .unwrap()
        .iter()
        .find(|p| p["pattern"] == "governance/tests/**")
        .cloned()
        .unwrap();
    assert_eq!(rule["lexical_index"], false, "{rule}");
    assert!(!indexed_paths(&root).contains(&"governance/tests/memory/heldout.yaml".to_string()));
    assert!(
        g.ok(&["memory", "query", "XYLOPHONE-HELDOUT-MARKER", "--k", "3"])["hits"]
            .as_array()
            .unwrap()
            .is_empty()
    );
    assert_eq!(
        yaml(&root, "governance/project/PROJECT_POLICY.yaml")["policy_overrides"]
            ["MEMORY_POLICY.retrieval.default_k"],
        5
    );
    git_commit_all(&root, "4.1.3");
    // 4.1.3 -> current release with the canonical kernel (M-4.1.3-4.1.4 carries the explicit set_overlay_rule)
    let chk2 = g.ok(&["update", "--check", "--source", signed_source()]);
    let chain2: Vec<String> = chk2["migration_path"]
        .as_array()
        .unwrap()
        .iter()
        .map(|m| m.as_str().unwrap().to_string())
        .collect();
    assert_eq!(
        chain2.first().map(|s| s.as_str()),
        Some("M-4.1.3-4.1.4"),
        "{chk2}"
    );
    assert_eq!(
        chain2.last().map(|s| s.as_str()),
        Some(
            format!("M-{}", {
                let v = gov_runtime::VERSION.rsplit_once('.').unwrap();
                format!(
                    "{}.{}-{}",
                    v.0,
                    v.1.parse::<u32>().unwrap() - 1,
                    gov_runtime::VERSION
                )
            })
            .as_str()
        ),
        "the chain must end at the current release: {chain2:?}"
    );
    let a2 = apply(Path::new(signed_source()));
    assert_eq!(a2["to"], gov_runtime::VERSION);
    let lock2 = yaml(&root, "governance/framework.lock");
    assert_eq!(lock2["version"], gov_runtime::VERSION);
    assert_eq!(lock2["lock_schema_version"], "1.1.0");
    // BC-P2-37 (P2-AR-0020): the current payload is byte-identical to this binary's embedded payload, so the
    // recorded release commit is the binary's own (decided by content), not the checkout's unauthenticated Git HEAD;
    // the release was verified against the trust anchor, so it is recorded as a verified `release:`.
    assert_eq!(
        lock2["release_commit"].as_str().unwrap(),
        gov_runtime::kernel::embedded::commit()
    );
    // round 2 (P2-AR-0024): admitted through signed release metadata on this provisioned machine, the basis the lock
    // names is the verified release
    assert_eq!(
        lock2["source"].as_str().unwrap(),
        format!("release:agentic-engineering-os@{}", gov_runtime::VERSION),
        "{lock2}"
    );
    assert_eq!(
        yaml(&root, "governance/project/REPOSITORY_CONTRACT.yaml")["paths"]
            .as_array()
            .unwrap()
            .iter()
            .find(|p| p["pattern"] == "governance/tests/**")
            .unwrap()["lexical_index"],
        false
    );
    assert!(exists(
        &root,
        "governance/kernel/policies/POLICY_PRECEDENCE.yaml"
    ));
    assert_eq!(
        tree_hash(&root.join("spec"), spec_excl),
        spec_before,
        "spec/ untouched by updates (INV-013)"
    );
    assert_eq!(
        yaml(&root, "spec/decisions/D-0001.yaml")["title"],
        "Use integer cents"
    );
    let decisions: Vec<String> = std::fs::read_dir(root.join("spec/decisions"))
        .unwrap()
        .filter_map(|e| e.ok())
        .map(|e| e.file_name().to_string_lossy().to_string())
        .collect();
    assert!(
        decisions.iter().all(|f| f == "D-0001.yaml"
            || f == ".gitkeep"
            || f.starts_with("HDG-")
            || f == "D-0002.yaml"
            || f == "D-0003.yaml"),
        "only the two update gates and their decisions may appear: {decisions:?}"
    );
    assert_eq!(
        yaml(&root, "governance/project/PROJECT_POLICY.yaml")["policy_overrides"]
            ["MEMORY_POLICY.retrieval.default_k"],
        5
    );
    // every structural check is healthy after the chain; only the "run gov audit" currency prompt (D021) may remain.
    // Round-2 integration (P2-AR-0032): this machine is provisioned (WS-8 harness), so D032 (installation release
    // authenticity, P2-AR-0023) must pass here like every other structural check — its temporary unprovisioned-machine
    // allowance is removed
    // BC-P2-44 (P2-AR-0033): D035 is not a structural check — it carries the repository verdict (the thirteen HEALTHY
    // conditions from the governance-suite outcomes, and the Gate U SLOs). After the chain the only conditions it may
    // name are H10 (the same currency prompt as D021) and H5 (retrieval: this fixture's held-out set has too few
    // queries to measure recall, which the suite reports as UNMEASURED); every structural check must pass.
    let doc = g.ok(&["doctor"]);
    let failed: Vec<String> = doc["checks"]
        .as_array()
        .unwrap()
        .iter()
        .filter(|c| c["ok"] == false && c["id"] != "D035")
        .map(|c| c["id"].as_str().unwrap().to_string())
        .collect();
    assert!(
        failed.iter().all(|c| c == "D021"),
        "unexpected doctor failures after the 4.1.2 -> 4.1.3 -> 4.1.4 chain: {failed:?}"
    );
    let d35 = doc["checks"]
        .as_array()
        .unwrap()
        .iter()
        .find(|c| c["id"] == "D035")
        .unwrap();
    if d35["ok"] == false {
        let conds: Vec<&str> = d35["repository"]["failing_conditions"]
            .as_array()
            .unwrap()
            .iter()
            .filter_map(|c| c.as_str())
            .collect();
        assert!(
            conds.iter().all(|c| *c == "H5" || *c == "H10")
                && d35["repository"]["crossed_slos"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .all(|x| x["owner"] != "health_slos"),
            "D035 after the chain: {d35}"
        );
    }
    // rollback 4.1.4 -> 4.1.3 leaves a ledger entry and consumes its snapshot; then 4.1.3 -> 4.1.2; then nothing left.
    // On a provisioned machine each rollback is below the protected release high-water, so it is refused without,
    // and admitted with, an owner-signed break-glass authorisation (ARCH-0003 §7; OWNER-DECISION-0006).
    assert_eq!(
        g.err(&["update", "--rollback", "--reason", "no authority"])
            .error_code(),
        "SRR_BELOW_FLOOR"
    );
    break_glass(&g, &k413, "rep2-chain-rb1");
    let rb = g.with_role("orchestrator").ok(&[
        "update",
        "--rollback",
        "--break-glass",
        "--reason",
        "verifier requested downgrade",
    ]);
    assert_eq!(rb["rolled_back_to"], "4.1.3");
    assert_eq!(rb["snapshot_consumed"], true);
    let ledger: Vec<Value> = read(&root, "spec/reports/framework-updates.jsonl")
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect();
    let rbe = ledger
        .iter()
        .rev()
        .find(|e| e["event"] == "rollback")
        .unwrap();
    for k in [
        "from",
        "to",
        "by",
        "role",
        "authority_level",
        "reason",
        "migrations_reverted",
        "resulting_lock",
        "verification",
        "at",
    ] {
        assert!(!rbe[k].is_null(), "rollback ledger lacks {k}: {rbe}");
    }
    assert_eq!(rbe["from"], gov_runtime::VERSION);
    assert_eq!(rbe["to"], "4.1.3");
    assert_eq!(rbe["reason"], "verifier requested downgrade");
    assert_eq!(rbe["resulting_lock"]["version"], "4.1.3");
    assert_eq!(yaml(&root, "governance/framework.lock")["version"], "4.1.3");
    break_glass(&g, &k412, "rep2-chain-rb2");
    let rb2 = g.ok(&["update", "--rollback", "--break-glass", "--reason", "again"]);
    assert_eq!(rb2["rolled_back_to"], "4.1.2");
    assert_eq!(yaml(&root, "governance/framework.lock")["version"], "4.1.2");
    let e = g.err(&["update", "--rollback"]);
    assert_eq!(e.error_code(), "SNAPSHOT_MISSING", "{}", e.envelope);
    assert_eq!(
        read(&root, "spec/reports/framework-updates.jsonl")
            .lines()
            .filter(|l| l.contains("\"rollback\""))
            .count(),
        2
    );
}

/// M-N4 / NV-05: mutation scope at close is decided from independently observed repository changes since the claim
/// baseline, not from the worker's list; undeclared or out-of-scope changes fail closed.
#[test]
fn task_close_uses_observed_mutations_not_self_attestation() {
    let (root, g) = setup_fixture("greenfield", "rep2-scope", "S-rep2");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "s",
        "--alias",
        "s-alias",
    ]);
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "docs only",
        "--status",
        "READY",
        "--allowed",
        "docs/**",
    ]);
    let tid = t["id"].as_str().unwrap().to_string();
    let c = g.ok(&["task", "claim", &tid]);
    assert!(c["baseline"]["files"].as_u64().unwrap() > 5, "{c}");
    write(&root, "docs/notes.md", "# notes\n");
    let lib = read(&root, "src/lib.rs");
    write(
        &root,
        "src/lib.rs",
        &format!("{lib}\npub fn injected_out_of_scope() -> u8 {{ 7 }}\n"),
    );
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = write_report(
        &root,
        "r1",
        "docs written",
        &["docs/notes.md"],
        "not_applicable_with_reason",
    );
    let e = g.err(&["task", "close", &tid, "--report", &rep]);
    assert_eq!(e.error_code(), "MUTATION_SCOPE_VIOLATION", "{}", e.envelope);
    assert!(
        e.details()["undeclared"].to_string().contains("src/lib.rs"),
        "{}",
        e.details()
    );
    assert!(e.details()["out_of_scope"]
        .to_string()
        .contains("src/lib.rs"));
    // declaring it does not help: it is outside allowed_paths
    let rep2 = write_report(
        &root,
        "r2",
        "docs + lib",
        &["docs/notes.md", "src/lib.rs"],
        "not_applicable_with_reason",
    );
    assert_eq!(
        g.err(&["task", "close", &tid, "--report", &rep2])
            .error_code(),
        "MUTATION_SCOPE_VIOLATION"
    );
    // reverting the out-of-scope change, an in-scope but undeclared change still fails closed
    write(&root, "src/lib.rs", &lib);
    write(&root, "docs/extra.md", "undeclared\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let e3 = g.err(&["task", "close", &tid, "--report", &rep]);
    assert_eq!(e3.error_code(), "MUTATION_SCOPE_VIOLATION");
    assert_eq!(e3.details()["undeclared"], json!(["docs/extra.md"]));
    // BC-P2-20 (P2-AR-0026): the successful close carries the full consumption receipt (the worker's return)
    let rep3 = crate::ws05::receipt(
        &g,
        &root,
        &tid,
        "r3",
        "docs",
        &["docs/notes.md", "docs/extra.md"],
        "not_applicable_with_reason",
    );
    let cl = g.ok(&["task", "close", &tid, "--report", &rep3]);
    let ck = yaml(
        &root,
        &format!(
            "spec/reports/checkpoints/{}.yaml",
            cl["checkpoint"].as_str().unwrap()
        ),
    );
    assert_eq!(
        ck["observed_files_changed"],
        json!(["docs/extra.md", "docs/notes.md"]),
        "{ck}"
    );
    let report = yaml(
        &root,
        &format!("spec/reports/{}.yaml", cl["report"].as_str().unwrap()),
    );
    assert_eq!(
        report["observed_files_changed"],
        json!(["docs/extra.md", "docs/notes.md"])
    );
    assert!(report["mutation_evidence"]["baseline"]
        .as_str()
        .unwrap()
        .contains("claim baseline"));
}

/// M-N5 / NV-07: a governed record relocated with git mv survives the first incremental rebuild with its identity;
/// a genuine duplicate id is still reported.
#[test]
fn incremental_rebuild_follows_record_relocation() {
    let (root, g) = setup_fixture("greenfield", "rep2-move", "S-rep2");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "m",
        "--alias",
        "m-alias",
    ]);
    write_yaml(
        &root,
        "spec/decisions/D-0001.yaml",
        &json!({"id": "D-0001", "type": "decision", "title": "Use integer cents", "status": "ACTIVE", "question": "money type?", "chosen_option": "A", "rationale": "r", "human_approved": true}),
    );
    git_commit_all(&root, "decision");
    g.ok(&["rebuild-memory"]);
    std::fs::create_dir_all(root.join("spec/decisions/2026")).unwrap();
    git(
        &root,
        &[
            "mv",
            "spec/decisions/D-0001.yaml",
            "spec/decisions/2026/D-0001.yaml",
        ],
    );
    git_commit_all(&root, "moved");
    let r = g.ok(&["rebuild-memory", "--incremental"]);
    assert!(
        r["moved"]
            .to_string()
            .contains("spec/decisions/2026/D-0001.yaml"),
        "{r}"
    );
    assert!(
        r["problems"]
            .as_array()
            .map(|a| a.is_empty())
            .unwrap_or(true),
        "{}",
        r["problems"]
    );
    let d = db(&root);
    let path: String = d
        .conn
        .query_row(
            "SELECT path FROM artifacts WHERE artifact_id='D-0001'",
            [],
            |x| x.get(0),
        )
        .unwrap();
    assert_eq!(path, "spec/decisions/2026/D-0001.yaml");
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);
    assert!(g.ok(&["memory", "query", "D-0001", "--k", "3"])["hits"]
        .as_array()
        .unwrap()
        .iter()
        .any(|h| h["artifact_id"] == "D-0001"));
    let n: i64 = d
        .conn
        .query_row(
            "SELECT count(*) FROM artifacts WHERE artifact_id='D-0001'",
            [],
            |x| x.get(0),
        )
        .unwrap();
    assert_eq!(n, 1);
    // pure rename within the same directory and a delete+add with changed content
    git(
        &root,
        &[
            "mv",
            "spec/decisions/2026/D-0001.yaml",
            "spec/decisions/2026/decision-0001.yaml",
        ],
    );
    git_commit_all(&root, "renamed");
    g.ok(&["rebuild-memory", "--incremental"]);
    let path2: String = d
        .conn
        .query_row(
            "SELECT path FROM artifacts WHERE artifact_id='D-0001'",
            [],
            |x| x.get(0),
        )
        .unwrap();
    assert_eq!(path2, "spec/decisions/2026/decision-0001.yaml");
    // genuine duplicate: same id at two live paths -> problem, first occurrence kept
    std::fs::copy(
        root.join("spec/decisions/2026/decision-0001.yaml"),
        root.join("spec/decisions/D-0001-copy.yaml"),
    )
    .unwrap();
    let r3 = g.ok(&["rebuild-memory", "--incremental"]);
    assert!(
        r3["problems"]
            .to_string()
            .contains("duplicate record id D-0001"),
        "{r3}"
    );
}

/// M-N6 / L-N1 / NV-09 / NV-19: interface records and docs state the fail-closed embed semantics; kernel YAML has
/// no duplicate keys; migrations into the current version deliver or declare every overlay-template change.
#[test]
fn interface_contract_kernel_yaml_and_migration_substance_are_consistent() {
    let croot = canonical_root();
    let api = read(&croot, "spec/interfaces/API-0001.yaml");
    assert!(
        !api.contains("degrades to the built-in fallback (embed"),
        "API-0001 must not promise a silent embed fallback"
    );
    assert!(
        api.contains("EMBEDDER_UNAVAILABLE") && api.contains("fail closed"),
        "API-0001 must state the fail-closed embed/rerank semantics"
    );
    assert!(exists(&croot, "spec/decisions/D-0005.yaml"));
    let proto = read(&croot, "capabilities/PROTOCOL.md");
    assert!(
        !proto.contains("it degrades to the fallback"),
        "PROTOCOL.md stale"
    );
    let fr = read(&croot, "fixtures/failure-injection/README.md");
    assert!(
        !fr.contains("rebuild degrades to builtin"),
        "failure-injection README stale"
    );
    // strict YAML: no duplicate mapping keys anywhere in the kernel payload
    fn dup_keys(text: &str) -> Vec<String> {
        let mut stack: Vec<(usize, std::collections::HashSet<String>)> =
            vec![(0, Default::default())];
        let mut dups = vec![];
        let key_of = |t: &str| -> Option<String> {
            let (k, _) = t.split_once(':')?;
            if k.is_empty()
                || k.contains(' ')
                || k.contains('"')
                || k.contains('{')
                || k.contains('[')
            {
                None
            } else {
                Some(k.to_string())
            }
        };
        for line in text.lines() {
            let t = line.trim_start();
            if t.is_empty() || t.starts_with('#') {
                continue;
            }
            let indent = line.len() - t.len();
            if let Some(inner) = t.strip_prefix("- ") {
                // a list item starts a fresh mapping scope for its own keys (indent + 2)
                let ki = indent + 2;
                while stack.len() > 1 && stack.last().unwrap().0 >= ki {
                    stack.pop();
                }
                let mut set: std::collections::HashSet<String> = Default::default();
                if let Some(k) = key_of(inner) {
                    set.insert(k);
                }
                stack.push((ki, set));
                continue;
            }
            let Some(k) = key_of(t) else { continue };
            while stack.len() > 1 && stack.last().unwrap().0 > indent {
                stack.pop();
            }
            if stack.last().unwrap().0 < indent {
                stack.push((indent, Default::default()));
            }
            if !stack.last_mut().unwrap().1.insert(k.clone()) {
                dups.push(k);
            }
        }
        dups
    }
    for (abs, rel) in gov_runtime::paths::iter_repo_files(&croot.join("framework"), false)
        .into_iter()
        .filter(|(_, r)| r.ends_with(".yaml"))
    {
        let d = dup_keys(&std::fs::read_to_string(&abs).unwrap());
        assert!(d.is_empty(), "duplicate keys {d:?} in framework/{rel}");
    }
    // migration substance: every migration into the current version accounts for the template changes it spans
    let migs = gov_runtime::migrations::framework::load_migrations(&croot.join("migrations"));
    let cur = gov_runtime::VERSION;
    let into: Vec<&Value> = migs.iter().filter(|m| m["to_version"] == cur).collect();
    assert!(!into.is_empty(), "no migration into {cur}");
    for m in into {
        let from = m["from_version"].as_str().unwrap();
        let old = croot
            .join("release/releases")
            .join(from)
            .join("kernel/overlay-templates");
        assert!(old.is_dir(), "previous release {from} payload missing");
        let problems = gov_runtime::migrations::framework::check_substance(
            m,
            &old,
            &croot.join("framework/overlay-templates"),
        );
        assert!(problems.is_empty(), "{problems:?}");
    }
    let bad = json!({"id": "M-x", "from_version": "4.1.3", "to_version": cur, "description": "tightens the contract", "operations": [{"op": "note", "text": "nothing"}]});
    let problems = gov_runtime::migrations::framework::check_substance(
        &bad,
        &croot.join("release/releases/4.1.3/kernel/overlay-templates"),
        &croot.join("framework/overlay-templates"),
    );
    assert!(
        !problems.is_empty(),
        "a migration that claims a contract change without an overlay op must be flagged"
    );
    let hist = migs.iter().find(|m| m["id"] == "M-4.1.2-4.1.3").unwrap();
    assert_eq!(
        hist["operations"].as_array().unwrap().len(),
        4,
        "historical migration operations must stay exactly as shipped"
    );
    assert!(hist["amendments"]
        .as_array()
        .map(|a| !a.is_empty())
        .unwrap_or(false));
}

/// NV-16 class: rebuilding an already-released version reproduces it from its recorded commit, not the working tree;
/// building into the canonical release directory stays refused.
#[test]
fn release_build_reproduces_released_versions_from_their_commit() {
    let croot = canonical_root();
    let out = tmp("rep2-release-out");
    let g = Gov::new(&croot, "S-rel");
    let status_before = git(&croot, &["status", "--porcelain", "--", "release/releases"]).1;
    let b = g.ok(&[
        "release",
        "build",
        "--version",
        "4.1.3",
        "--canonical",
        croot.to_str().unwrap(),
        "--out",
        out.to_str().unwrap(),
        "--certification",
        "READY_FOR_INDEPENDENT_REVERIFICATION",
    ]);
    let m = json(&croot.join("release/releases/4.1.3"), "manifest.json");
    assert_eq!(b["release_hash"], m["release_hash"]);
    assert_eq!(b["file_hashes"], m["file_hashes"]);
    assert_eq!(b["release_commit"], m["release_commit"]);
    assert_eq!(
        b["provenance"]["reproduced_from_commit"],
        m["release_commit"]
    );
    let e = g.err(&[
        "release",
        "build",
        "--version",
        "4.1.3",
        "--canonical",
        croot.to_str().unwrap(),
        "--out",
        croot.join("release").to_str().unwrap(),
    ]);
    assert_eq!(e.error_code(), "RELEASE_IMMUTABLE");
    assert_eq!(
        git(&croot, &["status", "--porcelain", "--", "release/releases"]).1,
        status_before,
        "a release build must not touch the canonical release directory"
    );
}
