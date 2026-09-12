//! Builder regression tests for the third independent re-verification
//! (release/verification/4.1.4/INDEPENDENT_REVERIFICATION_REPORT.md §11–§13). Each test names the finding it covers
//! and attacks the whole trust class, not only the verifier's exact input.
use crate::common::*;
use serde_json::{json, Value};
use std::path::Path;

fn write_exec(root: &Path, rel: &str, text: &str) -> String {
    write(root, rel, text);
    use std::os::unix::fs::PermissionsExt;
    std::fs::set_permissions(root.join(rel), std::fs::Permissions::from_mode(0o755)).unwrap();
    rel.to_string()
}

/// A plugin that records every invocation, so "was it executed?" is observable rather than inferred.
fn probe(root: &Path, marker: &Path) -> String {
    write_exec(
        root,
        "tools/probe.sh",
        &format!(
            "#!/bin/sh\ncat >/dev/null\necho EXECUTED >> '{}'\nprintf '{{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{{\"id\":\"probe\",\"version\":\"1\"}},\"outputs\":{{\"symbols\":[],\"imports\":[],\"calls\":[],\"chunks\":[]}}}}'\n",
            marker.display()
        ),
    )
}

fn descriptor(root: &Path, id: &str, extra: &str) {
    write(
        root,
        &format!("governance/project/plugins/{id}.yaml"),
        &format!("plugin_id: {id}\ncapability: code_intel\ncommand: [\"tools/probe.sh\"]\nversion: \"1\"\nlanguages: [\"python\"]\n{extra}"),
    );
}

fn clear_plugins(root: &Path, marker: &Path) {
    let d = root.join("governance/project/plugins");
    if let Ok(rd) = std::fs::read_dir(&d) {
        for e in rd.flatten() {
            std::fs::remove_file(e.path()).unwrap();
        }
    }
    let _ = std::fs::remove_file(marker);
}

fn executed(marker: &Path) -> bool {
    std::fs::read_to_string(marker)
        .map(|s| s.contains("EXECUTED"))
        .unwrap_or(false)
}

fn usable(g: &Gov) -> Vec<String> {
    g.ok(&["plugins", "list"])["usable"]
        .as_array()
        .unwrap()
        .iter()
        .map(|u| u["plugin_id"].as_str().unwrap().to_string())
        .collect()
}

fn denial(g: &Gov, id: &str) -> String {
    g.ok(&["plugins", "list"])["denied"]
        .as_array()
        .unwrap()
        .iter()
        .find(|d| d["plugin_id"] == id)
        .map(|d| d["code"].as_str().unwrap_or("").to_string())
        .unwrap_or_default()
}

/// V-H1 / VV-04: a descriptor describes, it never authorises. Every field an attacker can write into
/// `governance/project/plugins/*.yaml` is inert; authorisation comes from verified kernel policy and the OS-written
/// registry. The L0 independence roles can never obtain command execution.
#[test]
fn plugin_descriptors_can_never_authorise_themselves() {
    let (root, g) = setup_fixture("greenfield", "rep3-plug", "S-rep3");
    g.ok(&["init", "--name", "p", "--alias", "p-alias", "--skip-index"]);
    let marker = root.join("v3-marker.txt");
    probe(&root, &marker);
    write(&root, "src/probe.py", "def f():\n    return 1\n");
    std::fs::create_dir_all(root.join("governance/project/plugins")).unwrap();
    let l0 = g.with_role("independent-auditor"); // L0: an independence role the protocol depends on
    let l1 = g.with_role("backend-engineer"); // L1
    let l4 = g.with_role("orchestrator"); // L4

    // 1. self-declared approved_roles: ["all"] — the verifier's exact attack
    clear_plugins(&root, &marker);
    descriptor(&root, "p-allroles", "approved_roles: [\"all\"]\n");
    assert!(
        usable(&l0).is_empty(),
        "L0 must not gain a usable plugin from a descriptor claim"
    );
    assert_eq!(denial(&l0, "p-allroles"), "AUTHORITY_DENIED");
    l0.ok(&["rebuild-memory"]);
    assert!(
        !executed(&marker),
        "ARBITRARY EXECUTION as L0 through approved_roles"
    );
    assert!(usable(&l1).is_empty(), "L1 is below the floor too");
    l1.ok(&["rebuild-memory"]);
    assert!(!executed(&marker));
    // doctor reports the claim itself, whatever the acting role: it is the claim that is wrong
    let (ok28, msg28) = doctor_check(&l4, "D028");
    assert!(
        !ok28 && msg28.contains("p-allroles"),
        "D028 must report the self-authorising descriptor: {msg28}"
    );
    let au = l4.run(&["audit", "--no-persist", "--family", "plugin_governance"]);
    let f = if au.ok() { au.result() } else { au.details() };
    assert!(
        f["findings"].to_string().contains("p-allroles"),
        "{}",
        f["findings"]
    );

    // 2. fabricated provenance (claims to have been registered)
    clear_plugins(&root, &marker);
    descriptor(&root, "p-fakeprov", "provenance:\n  registered_at: \"2026-01-01T00:00:00Z\"\n  registered_by_role: human\n  method: manual\n  gate: HDG-0001\n");
    assert!(usable(&l0).is_empty());
    assert_eq!(denial(&l0, "p-fakeprov"), "AUTHORITY_DENIED");
    l0.ok(&["rebuild-memory"]);
    assert!(
        !executed(&marker),
        "ARBITRARY EXECUTION as L0 through forged provenance"
    );
    assert!(!doctor_check(&l4, "D028").0);

    // 3. fabricated provenance + approved_roles + status: active + a self-declared pin (everything at once)
    clear_plugins(&root, &marker);
    let real_pin = {
        clear_plugins(&root, &marker);
        descriptor(&root, "p-pinprobe", "");
        let list = l4.ok(&["plugins", "list"]);
        let _ = list;
        // the pin the OS would compute is not exposed for an unregistered descriptor; use a deliberately wrong one
        "0".repeat(64)
    };
    descriptor(
        &root,
        "p-everything",
        &format!("approved_roles: [\"all\"]\nstatus: active\nprovenance:\n  registered_at: \"2026-01-01T00:00:00Z\"\n  registered_by_role: human\npin:\n  sha256: \"{real_pin}\"\n"),
    );
    assert!(usable(&l0).is_empty());
    l0.ok(&["rebuild-memory"]);
    assert!(!executed(&marker));

    // 4. the governed path: registration by an authorised role creates the OS-side record
    clear_plugins(&root, &marker);
    descriptor(&root, "p-reg", "");
    let df = root.join("governance/project/plugins/p-reg.yaml");
    assert_eq!(
        l1.err(&["plugins", "register", "--descriptor", df.to_str().unwrap()])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    let r = l4.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    assert_eq!(r["registered"], true, "{r}");
    let reg = json(&root, "governance/generated/plugin-registry.json");
    let e = &reg["plugins"]["p-reg"];
    assert_eq!(e["version"], "1");
    assert!(e["descriptor_sha256"].as_str().unwrap().len() == 64);
    assert!(e["implementation_sha256"].as_str().unwrap().len() == 64);
    assert_eq!(e["registered_by_role"], "orchestrator");
    assert!(usable(&l4).contains(&"p-reg".to_string()));
    // registration does NOT lower the authority floor: L0/L1 still cannot execute a registered plugin
    assert!(
        usable(&l0).is_empty(),
        "registration must not lower TOOL_POLICY.plugins.min_authority"
    );
    l0.ok(&["rebuild-memory"]);
    assert!(!executed(&marker));
    assert_eq!(
        l0.err(&[
            "capabilities",
            "invoke",
            "--plugin",
            "p-reg",
            "--inputs",
            "{}"
        ])
        .error_code(),
        "AUTHORITY_DENIED"
    );
    assert!(
        doctor_check(&l4, "D028").0,
        "a properly registered plugin is clean"
    );

    // 5. descriptor edited after registration -> fails closed for everyone
    let mut d = yaml(&root, "governance/project/plugins/p-reg.yaml");
    d["languages"] = json!(["python", "rust"]);
    write_yaml(&root, "governance/project/plugins/p-reg.yaml", &d);
    assert_eq!(denial(&l4, "p-reg"), "PLUGIN_REGISTRY_MISMATCH");
    assert!(usable(&l4).is_empty());
    assert!(!doctor_check(&l4, "D028").0);

    // 6. version drift against the registration
    let mut d = yaml(&root, "governance/project/plugins/p-reg.yaml");
    d["languages"] = json!(["python"]);
    d["version"] = json!("2");
    write_yaml(&root, "governance/project/plugins/p-reg.yaml", &d);
    assert_eq!(denial(&l4, "p-reg"), "PLUGIN_REGISTRY_MISMATCH");

    // 7. identity spoofing: a different descriptor claiming a registered plugin's id
    clear_plugins(&root, &marker);
    descriptor(&root, "p-reg", "approved_roles: [\"all\"]\n");
    assert_eq!(denial(&l4, "p-reg"), "PLUGIN_REGISTRY_MISMATCH");
    assert!(usable(&l0).is_empty());
    l0.ok(&["rebuild-memory"]);
    assert!(!executed(&marker));

    // 8. a registry record with no descriptor is stale, and reported
    clear_plugins(&root, &marker);
    assert!(
        !doctor_check(&l4, "D028").0,
        "orphan registration must be reported"
    );
    l4.ok(&["plugins", "unregister", "p-reg"]);
    assert!(doctor_check(&l4, "D028").0);

    // 9. elevated permissions are never granted by the descriptor, registered or not
    clear_plugins(&root, &marker);
    descriptor(
        &root,
        "p-elev",
        "permissions:\n  network: true\n  filesystem_write: true\napproved_roles: [\"all\"]\n",
    );
    assert_eq!(denial(&l4, "p-elev"), "PLUGIN_NOT_APPROVED");
    assert!(usable(&l0).is_empty());
    let df = root.join("governance/project/plugins/p-elev.yaml");
    let r = l4.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    assert_eq!(r["registered"], false);
    let gate = r["human_gate"].as_str().unwrap().to_string();
    assert!(
        !exists(&root, "governance/generated/plugin-registry.json")
            || json(&root, "governance/generated/plugin-registry.json")["plugins"]["p-elev"]
                .is_null()
    );
    l4.ok(&["gate", "present", &gate]);
    l4.ok(&["decide", &gate, "--option", "A", "--by", "owner"]);
    let mut d = yaml(&root, "governance/project/plugins/p-elev.yaml");
    d["registration_gate"] = json!(gate);
    write_yaml(&root, "governance/project/plugins/p-elev.yaml", &d);
    let df2 = root.join("governance/project/plugins/p-elev.yaml");
    let r2 = l4.ok(&["plugins", "register", "--descriptor", df2.to_str().unwrap()]);
    assert_eq!(r2["registered"], true, "{r2}");
    assert_eq!(
        json(&root, "governance/generated/plugin-registry.json")["plugins"]["p-elev"]
            ["registration_gate"],
        gate
    );
    assert!(usable(&l4).contains(&"p-elev".to_string()));
    assert!(
        usable(&l0).is_empty(),
        "an approved elevated plugin still respects the authority floor"
    );
}

/// V-H2 / VV-03(b,c) / VV-14: constitutional enforcement consumes only a kernel authenticated against the installed
/// release identity. Tampering with any kernel policy fails closed; the embedded baseline is substituted explicitly;
/// mutating operations refuse with KERNEL_TAMPERED until the payload is restored or an L4+ gate is answered.
#[test]
fn constitutional_floors_require_a_verified_kernel() {
    let (root, g) = setup_fixture("greenfield", "rep3-kernel", "S-rep3");
    g.ok(&["init", "--name", "k", "--alias", "k-alias"]);
    let l0 = g.with_role("independent-auditor");
    // healthy baseline
    assert!(doctor_check(&g, "D029").0);
    assert_eq!(g.ok(&["kernel", "trust"])["verified"], true);
    let restricted = |root: &Path| {
        let mut ds = yaml(root, "governance/project/DATA_SENSITIVITY.yaml");
        ds["classifications"] =
            json!([{"pattern": "customer/**", "class": "restricted", "reason": "probe"}]);
        write_yaml(root, "governance/project/DATA_SENSITIVITY.yaml", &ds);
        write(root, "customer/secret.md", "REP3RESTRICTED private terms\n");
    };
    restricted(&root);
    let rb = g.ok(&["rebuild-memory"]);
    assert!(
        rb["excluded"].to_string().contains("customer/secret.md"),
        "{}",
        rb["excluded"]
    );

    {
        let (file, mutation) = (
            "policies/POLICY_PRECEDENCE.yaml",
            "policy: POLICY_PRECEDENCE\nversion: 1.0.0\nlayers: [a]\ndefault_mode: overridable\nrules:\n  - {key: AUTHORITY_POLICY.*, mode: overridable}\n  - {key: SECURITY_POLICY.*, mode: overridable}\n",
        );
        let original = read(&root, &format!("governance/kernel/{file}"));
        write(&root, &format!("governance/kernel/{file}"), mutation);
        let mut pp = yaml(&root, "governance/project/PROJECT_POLICY.yaml");
        pp["policy_overrides"] = json!({"AUTHORITY_POLICY.authority_levels_required.create_task": "L0", "SECURITY_POLICY.never_index_classes": []});
        write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
        // the weakening is NOT applied: precedence comes from the embedded baseline
        let ov = g.ok(&["policy", "overrides"]);
        assert_eq!(
            ov["kernel_trust"]["verified"], false,
            "{}",
            ov["kernel_trust"]
        );
        assert_eq!(ov["kernel_trust"]["substituted_embedded_baseline"], true);
        assert!(
            ov["applied"].as_array().unwrap().is_empty(),
            "{}",
            ov["applied"]
        );
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
        assert!(
            refused.contains(&"AUTHORITY_POLICY.authority_levels_required.create_task".to_string()),
            "{refused:?}"
        );
        assert!(refused.contains(&"SECURITY_POLICY.never_index_classes".to_string()));
        // every mutating path refuses, whatever the role
        assert_eq!(
            l0.err(&[
                "task",
                "create",
                "--class",
                "implementation",
                "--objective",
                "probe",
                "--status",
                "READY"
            ])
            .error_code(),
            "KERNEL_TAMPERED"
        );
        assert_eq!(
            g.err(&[
                "task",
                "create",
                "--class",
                "documentation",
                "--objective",
                "probe",
                "--status",
                "READY"
            ])
            .error_code(),
            "KERNEL_TAMPERED"
        );
        assert_eq!(g.err(&["rebuild-memory"]).error_code(), "KERNEL_TAMPERED");
        assert_eq!(
            g.err(&[
                "cit",
                "propose",
                "--proposal",
                "x",
                "--trigger",
                "editorial"
            ])
            .error_code(),
            "KERNEL_TAMPERED"
        );
        assert_eq!(
            g.err(&["gate", "create", "--question", "q"]).error_code(),
            "KERNEL_TAMPERED"
        );
        // diagnostics still work and name the exact problem
        let (ok3, msg3) = doctor_check(&g, "D003");
        assert!(!ok3 && msg3.contains(file), "{msg3}");
        let (ok29, msg29) = doctor_check(&g, "D029");
        assert!(!ok29 && msg29.contains("FAILED verification"), "{msg29}");
        assert_eq!(g.ok(&["kernel", "verify"])["ok"], false);
        let au = g.run(&["audit", "--no-persist", "--family", "policy_precedence"]);
        let f = if au.ok() { au.result() } else { au.details() };
        assert!(
            f["findings"].to_string().contains("verified kernel"),
            "{}",
            f["findings"]
        );
        // restoring the payload restores enforcement
        write(&root, &format!("governance/kernel/{file}"), &original);
        assert!(doctor_check(&g, "D029").0);
        g.ok(&["rebuild-memory"]);
        pp["policy_overrides"] = json!({});
        write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    }

    // tampering with the SECURITY floor cannot remove a never-index class at index time (VV-14)
    let sec_path = "governance/kernel/policies/SECURITY_POLICY.yaml";
    let original = read(&root, sec_path);
    let mut sec = yaml(&root, sec_path);
    sec["never_index_classes"] = json!([]);
    write_yaml(&root, sec_path, &sec);
    assert_eq!(g.err(&["rebuild-memory"]).error_code(), "KERNEL_TAMPERED");
    let q = g.ok(&["memory", "query", "REP3RESTRICTED", "--k", "5"]);
    assert!(
        q["hits"]
            .as_array()
            .unwrap()
            .iter()
            .all(|h| h["path"] != "customer/secret.md"),
        "{}",
        q["hits"]
    );
    // rewriting KERNEL_MANIFEST.json to match the tampered file does not help: the lock still disagrees
    let payload = gov_runtime::kernel::build_manifest(&root.join("governance/kernel")).unwrap();
    gov_runtime::util::write_json(
        &root.join("governance/kernel/KERNEL_MANIFEST.json"),
        &payload,
    )
    .unwrap();
    assert_eq!(g.err(&["rebuild-memory"]).error_code(), "KERNEL_TAMPERED");
    let (ok4, msg4) = doctor_check(&g, "D004");
    assert!(!ok4, "D004 must catch the rewritten manifest: {msg4}");
    // the L4+ override is a governed act bound to this exact kernel state
    assert_eq!(
        g.with_role("change-controller")
            .err(&["kernel", "override", "--reason", "x"])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    let o = g.ok(&["kernel", "override", "--reason", "reviewed local change"]);
    let gate = o["human_gate"].as_str().unwrap().to_string();
    assert_eq!(o["override_active"], false);
    assert_eq!(
        g.err(&["rebuild-memory"]).error_code(),
        "KERNEL_TAMPERED",
        "an unanswered gate is not an override"
    );
    g.ok(&["gate", "present", &gate]);
    g.ok(&["decide", &gate, "--option", "A", "--by", "owner"]);
    g.ok(&["rebuild-memory"]);
    // ... and it does not survive a different tampering
    let mut sec2 = yaml(&root, sec_path);
    sec2["secret_content_patterns"] = json!([]);
    write_yaml(&root, sec_path, &sec2);
    assert_eq!(
        g.err(&["rebuild-memory"]).error_code(),
        "KERNEL_TAMPERED",
        "the override is bound to one kernel state"
    );
    write(&root, sec_path, &original);
    let payload = gov_runtime::kernel::build_manifest(&root.join("governance/kernel")).unwrap();
    gov_runtime::util::write_json(
        &root.join("governance/kernel/KERNEL_MANIFEST.json"),
        &payload,
    )
    .unwrap();
    assert!(doctor_check(&g, "D029").0);
    assert!(doctor_check(&g, "D003").0);
    g.ok(&["rebuild-memory"]);
}

/// V-M1 / VV-03(a): a `PROJECT_EXCEPTIONS` entry is applied only when its `decision` resolves to an existing,
/// current, sufficiently approved decision whose own scope covers that exception for this project.
#[test]
fn policy_exceptions_require_a_real_governing_decision() {
    let (root, g) = setup_fixture("greenfield", "rep3-exc", "S-rep3");
    g.ok(&["init", "--name", "e", "--alias", "e-alias", "--skip-index"]);
    let key = "defaults.max_tool_calls";
    let set_exceptions = |items: Value| {
        let mut ex = yaml(&root, "governance/project/PROJECT_EXCEPTIONS.yaml");
        ex["exceptions"] = items;
        write_yaml(&root, "governance/project/PROJECT_EXCEPTIONS.yaml", &ex);
    };
    let refused_reason = |g: &Gov, id: &str| -> String {
        g.ok(&["policy", "overrides"])["refused"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["source"] == id)
            .map(|r| r["reason"].as_str().unwrap_or("").to_string())
            .unwrap_or_default()
    };
    let applied = |g: &Gov, id: &str| -> bool {
        g.ok(&["policy", "overrides"])["applied"]
            .as_array()
            .unwrap()
            .iter()
            .any(|r| r["source"] == id)
    };
    let exc = |decision: &str| json!([{"id": "EXC-0001", "policy": "BUDGET_POLICY", "key": key, "value": 999999, "decision": decision, "expires": "2099-01-01", "rationale": "probe"}]);

    // 1. a decision id that does not exist — the verifier's exact attack
    set_exceptions(exc("D-DOES-NOT-EXIST"));
    assert!(!applied(&g, "EXC-0001"));
    assert!(
        refused_reason(&g, "EXC-0001").contains("does not exist"),
        "{}",
        refused_reason(&g, "EXC-0001")
    );
    let (ok27, msg27) = doctor_check(&g, "D027");
    assert!(
        !ok27 && msg27.contains("EXC-0001"),
        "D027 must report the dangling reference: {msg27}"
    );

    // 2. no decision at all
    set_exceptions(
        json!([{"id": "EXC-0001", "policy": "BUDGET_POLICY", "key": key, "value": 999999, "expires": "2099-01-01"}]),
    );
    assert!(!applied(&g, "EXC-0001"));

    // 3. a real record that is not a decision
    write_yaml(
        &root,
        "spec/requirements/REQ-0009.yaml",
        &json!({"id": "REQ-0009", "type": "requirement", "title": "not a decision", "status": "ACTIVE", "kind": "functional", "acceptance_criteria": ["a"]}),
    );
    set_exceptions(exc("REQ-0009"));
    assert!(refused_reason(&g, "EXC-0001").contains("not a decision"));

    // 4. a decision that exists, is ACTIVE and human-approved, but says nothing about this exception
    let base = json!({"id": "D-0001", "type": "decision", "title": "Unrelated", "status": "ACTIVE", "question": "?",
        "chosen_option": "A", "rationale": "r", "human_approved": true});
    write_yaml(&root, "spec/decisions/D-0001.yaml", &base);
    set_exceptions(exc("D-0001"));
    assert!(
        refused_reason(&g, "EXC-0001").contains("does not name it"),
        "{}",
        refused_reason(&g, "EXC-0001")
    );

    // 5. in scope, approved, active -> applied
    let mut d = base.clone();
    d["authorises_exceptions"] = json!(["EXC-0001"]);
    write_yaml(&root, "spec/decisions/D-0001.yaml", &d);
    assert!(
        applied(&g, "EXC-0001"),
        "{}",
        g.ok(&["policy", "overrides"])["refused"]
    );
    assert_eq!(
        g.ok(&["policy", "effective", "BUDGET_POLICY"])["effective"]["defaults"]["max_tool_calls"],
        999999
    );
    assert!(doctor_check(&g, "D027").0);

    // 6. superseded / rejected / revoked / expired decisions all invalidate it
    for (field, value) in [
        ("superseded_by", json!("D-0002")),
        ("status", json!("REJECTED")),
        ("revoked", json!(true)),
        ("expires", json!("2000-01-01")),
    ] {
        let mut bad = d.clone();
        bad[field] = value.clone();
        write_yaml(&root, "spec/decisions/D-0001.yaml", &bad);
        assert!(
            !applied(&g, "EXC-0001"),
            "a decision with {field}={value} must not authorise an exception"
        );
        assert_eq!(
            g.ok(&["policy", "effective", "BUDGET_POLICY"])["effective"]["defaults"]
                ["max_tool_calls"],
            g.ok(&["policy", "effective", "BUDGET_POLICY"])["kernel"]["defaults"]["max_tool_calls"]
        );
    }

    // 7. insufficient authority: an agent-approved decision by a low-authority role
    let mut weak = d.clone();
    weak["human_approved"] = json!(false);
    weak["approved_by_role"] = json!("research-agent");
    weak["owner_role"] = json!("research-agent");
    write_yaml(&root, "spec/decisions/D-0001.yaml", &weak);
    assert!(!applied(&g, "EXC-0001"));
    assert!(
        refused_reason(&g, "EXC-0001").contains("authority"),
        "{}",
        refused_reason(&g, "EXC-0001")
    );
    // an L4 approver is sufficient without a human
    let mut strong = weak.clone();
    strong["approved_by_role"] = json!("orchestrator");
    strong["owner_role"] = json!("orchestrator");
    write_yaml(&root, "spec/decisions/D-0001.yaml", &strong);
    assert!(applied(&g, "EXC-0001"));

    // 8. a decision scoped to another project
    let mut other = d.clone();
    other["applies_to_project"] = json!("some-other-project");
    write_yaml(&root, "spec/decisions/D-0001.yaml", &other);
    assert!(!applied(&g, "EXC-0001"));

    // 9. an exception can never reach a constitutional floor, however well governed
    write_yaml(&root, "spec/decisions/D-0001.yaml", &d);
    set_exceptions(json!([
        {"id": "EXC-SEC", "policy": "AUTHORITY_POLICY", "key": "authority_levels_required.execute_cit", "value": "L0", "decision": "D-0001", "expires": "2099-01-01"},
        {"id": "EXC-IDX", "policy": "SECURITY_POLICY", "key": "never_index_classes", "value": [], "decision": "D-0001", "expires": "2099-01-01"},
    ]));
    let mut d2 = d.clone();
    d2["authorises_exceptions"] = json!(["EXC-SEC", "EXC-IDX"]);
    write_yaml(&root, "spec/decisions/D-0001.yaml", &d2);
    assert!(!applied(&g, "EXC-SEC") && !applied(&g, "EXC-IDX"));
    assert_eq!(
        g.ok(&["policy", "effective", "AUTHORITY_POLICY"])["effective"]
            ["authority_levels_required"]["execute_cit"],
        "L3"
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
}

/// Trust-boundary audit (directive §5): a caller- or descriptor-supplied field never manufactures a higher-trust
/// fact. This test asserts the invariant across the whole surface, so a future field cannot quietly reintroduce it.
#[test]
fn lower_trust_inputs_cannot_manufacture_higher_trust_facts() {
    let (root, g) = setup_fixture("greenfield", "rep3-trust", "S-rep3");
    g.ok(&["init", "--name", "t", "--alias", "t-alias"]);
    // 1. a tool descriptor cannot self-certify its security review: the condition fails and a gate is raised
    let td = root.join("tool.json");
    std::fs::write(&td, json!({"tool_id": "selfcert", "name": "selfcert", "type": "CLI", "capabilities": ["run_tests"],
        "version": "1", "version_pin": "1.0.0", "license": "MIT", "security_review": "passed", "reversible": true,
        "cost_usd": 0.0, "install_command": ["true"], "uninstall_command": ["true"], "required_permission_classes": ["RUN_TESTS"],
        "health_check": {"kind": "command_exists", "command": ["true"]}}).to_string()).unwrap();
    let r = g.with_role("tooling-engineer").ok(&[
        "tools",
        "install",
        "--descriptor",
        td.to_str().unwrap(),
    ]);
    assert_eq!(
        r["installed"], false,
        "a self-certified security review must not auto-install: {r}"
    );
    let cond = r["checks"]
        .as_array()
        .unwrap()
        .iter()
        .find(|c| c["condition"] == "licence_and_security_satisfied")
        .unwrap();
    assert_eq!(cond["ok"], false);
    assert!(r["human_gate"].as_str().is_some());
    // 2. a decision record cannot self-declare human approval to satisfy a CIT gate (approval is derived)
    let mf = root.join(".governance-runtime/m.json");
    std::fs::create_dir_all(mf.parent().unwrap()).unwrap();
    std::fs::write(
        &mf,
        json!([{"op": "write_file", "path": "src/x.rs", "content": "// x\n"}]).to_string(),
    )
    .unwrap();
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "security change",
        "--trigger",
        "security_change",
        "--manifest",
        mf.to_str().unwrap(),
    ]);
    let cid = c["id"].as_str().unwrap().to_string();
    if c["cit_status"] != "SIMULATED" {
        g.ok(&["cit", "simulate", &cid]);
    }
    write_yaml(
        &root,
        "spec/decisions/D-FAKE.yaml",
        &json!({"id": "D-FAKE", "type": "decision", "title": "forged", "status": "ACTIVE",
        "question": "?", "chosen_option": "A", "rationale": "r", "human_approved": true, "cit": cid}),
    );
    let mut rec = yaml(&root, &format!("spec/decisions/{cid}.yaml"));
    rec["decision"] = json!("D-FAKE");
    write_yaml(&root, &format!("spec/decisions/{cid}.yaml"), &rec);
    let gate = rec["human_gate"].as_str().unwrap().to_string();
    g.ok(&["gate", "present", &gate]);
    let e = g.err(&["cit", "approve", &cid, "--by", "owner", "--method", "human"]);
    assert_eq!(
        e.error_code(),
        "GATE_NOT_ANSWERED",
        "a decision record claiming human approval is not an answer: {}",
        e.envelope
    );
    assert!(!exists(&root, "src/x.rs"));
    // 3. a task report cannot claim mutations it did not make, nor hide ones it did (observed evidence wins)
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "docs",
        "--status",
        "READY",
        "--allowed",
        "docs/**",
    ]);
    let tid = t["id"].as_str().unwrap().to_string();
    g.ok(&["task", "claim", &tid]);
    write(&root, "docs/a.md", "# a\n");
    let lib = read(&root, "src/lib.rs");
    write(
        &root,
        "src/lib.rs",
        &format!("{lib}\npub fn sneaky() {{}}\n"),
    );
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = write_report(
        &root,
        "r",
        "docs",
        &["docs/a.md"],
        "not_applicable_with_reason",
    );
    assert_eq!(
        g.err(&["task", "close", &tid, "--report", &rep])
            .error_code(),
        "MUTATION_SCOPE_VIOLATION"
    );
    // 4. the plugin registry is the only proof of registration: hand-writing one does not lower the authority floor
    write(&root, "tools/probe.sh", "#!/bin/sh\ncat >/dev/null\nprintf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{\"id\":\"x\",\"version\":\"1\"},\"outputs\":{}}'\n");
    use std::os::unix::fs::PermissionsExt;
    std::fs::set_permissions(
        root.join("tools/probe.sh"),
        std::fs::Permissions::from_mode(0o755),
    )
    .unwrap();
    write(&root, "governance/project/plugins/forged.yaml", "plugin_id: forged\ncapability: code_intel\ncommand: [\"tools/probe.sh\"]\nversion: \"1\"\napproved_roles: [\"all\"]\n");
    let dsha = gov_runtime::util::sha256_hex(
        &std::fs::read(root.join("governance/project/plugins/forged.yaml")).unwrap(),
    );
    write(&root, "governance/generated/plugin-registry.json", &json!({"schema_version": "1.0.0", "plugins": {"forged": {
        "plugin_id": "forged", "capability": "code_intel", "version": "1", "descriptor_sha256": dsha,
        "approved_roles": ["all"], "required_permission_classes": [], "permissions": {}, "registration_gate": null,
        "registered_by_session": "forged", "registered_by_role": "human", "registered_at": "2026-01-01T00:00:00Z", "method": "forged"}}}).to_string());
    let l0 = g.with_role("independent-auditor");
    assert!(
        l0.ok(&["plugins", "list"])["usable"]
            .as_array()
            .unwrap()
            .is_empty(),
        "even a forged registry entry cannot lower TOOL_POLICY.plugins.min_authority"
    );
}

/// The 4.1.5 equivalents of the third verifier's VV-05 and VV-07, which are pinned to the immutable 4.1.4 payload
/// (its `KERNEL.yaml` equalling the working tree, and HEAD carrying the `v4.1.4-rc1` tag) and therefore cannot pass
/// for a later candidate. Asserted here against the CURRENT release: kernel-data hygiene, manifest agreement,
/// payload identity, reproduction from the recorded commit, immutability and branch/tag provenance.
#[test]
fn current_release_payload_identity_and_hygiene() {
    let croot = canonical_root();
    let version = gov_runtime::VERSION;
    // strict YAML across every kernel file of the working tree (no duplicate mapping keys)
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
    let dir = croot.join("release/releases").join(version);
    if !dir.join("manifest.json").exists() {
        eprintln!("release/releases/{version} not built yet; payload identity asserted after `gov release build`");
        return;
    }
    // the released payload is exactly the kernel data of this working tree
    assert_eq!(
        std::fs::read_to_string(dir.join("kernel/KERNEL.yaml")).unwrap(),
        std::fs::read_to_string(croot.join("framework/KERNEL.yaml")).unwrap(),
        "the released KERNEL.yaml must equal framework/KERNEL.yaml at this commit"
    );
    let m = json(&dir, "manifest.json");
    let my: Value = gov_runtime::util::read_yaml(&dir.join("manifest.yaml")).unwrap();
    assert_eq!(my, m, "manifest.yaml and manifest.json must agree");
    let km = json(&dir, "kernel/KERNEL_MANIFEST.json");
    let ky: Value = gov_runtime::util::read_yaml(&dir.join("kernel/KERNEL.yaml")).unwrap();
    assert_eq!(ky["schema_versions"], km["schema_versions"]);
    assert_eq!(km["schema_versions"], m["schema_versions"]);
    assert_eq!(m["version"], version);
    assert_eq!(m["provenance"]["release_tag"], format!("v{version}-rc1"));
    assert_eq!(
        m["provenance"]["release_branch"].as_str().unwrap(),
        git(&croot, &["rev-parse", "--abbrev-ref", "HEAD"]).1.trim()
    );
    assert!(m["provenance"]["migration_substance_problems"]
        .as_array()
        .unwrap()
        .is_empty());
    // the payload verifies and reproduces from its recorded commit
    let g = Gov::new(&croot, "S-rel3");
    assert_eq!(
        g.ok(&["release", "verify", dir.to_str().unwrap()])["ok"],
        true
    );
    let rc = m["release_commit"].as_str().unwrap();
    assert_eq!(
        git(&croot, &["merge-base", "--is-ancestor", rc, "HEAD"]).0,
        0,
        "release_commit must be an ancestor of HEAD"
    );
    let out = tmp("rep3-release-out");
    let b = g.ok(&[
        "release",
        "build",
        "--version",
        version,
        "--canonical",
        croot.to_str().unwrap(),
        "--out",
        out.to_str().unwrap(),
        "--certification",
        "READY_FOR_INDEPENDENT_REVERIFICATION",
    ]);
    assert_eq!(b["release_hash"], m["release_hash"]);
    assert_eq!(b["file_hashes"], m["file_hashes"]);
    assert_eq!(
        b["provenance"]["reproduced_from_commit"],
        m["release_commit"]
    );
    assert_eq!(
        g.err(&[
            "release",
            "build",
            "--version",
            version,
            "--canonical",
            croot.to_str().unwrap(),
            "--out",
            croot.join("release").to_str().unwrap()
        ])
        .error_code(),
        "RELEASE_IMMUTABLE"
    );
}
