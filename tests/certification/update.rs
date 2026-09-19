//! Fixture 4 — framework update from a synthetic previous release 4.1.1 to the 4.1.2 candidate, then rollback.
use crate::common::*;
use serde_json::{json, Value};

/// The synthetic previous release is stored immutably under fixtures/update/previous-release/4.1.1 (see README).
fn previous_release() -> std::path::PathBuf {
    canonical_root().join("fixtures/update/previous-release/4.1.1")
}

#[test]
fn update_from_previous_release_preserves_project_and_rolls_back() {
    let root = tmp("update");
    let prev = previous_release();
    let proj = root.join("project");
    std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# upd project\n");
    git_init_commit(&proj);
    let g = Gov::new(&proj, "S-upd");
    let r = g.ok(&[
        "init",
        "--source",
        prev.to_str().unwrap(),
        "--name",
        "upd-project",
        "--alias",
        "fx-upd",
    ]);
    assert_eq!(r["version"], "4.1.1");
    assert!(!exists(&proj, "governance/project/PROJECT_EXCEPTIONS.yaml"));
    assert!(read(&proj, "governance/project/PROJECT_POLICY.yaml").contains("human_gates:"));
    // project state that must survive
    let mut pp = yaml(&proj, "governance/project/PROJECT_POLICY.yaml");
    pp["policy_overrides"] = json!({"MEMORY_POLICY.retrieval.default_k": 5});
    write_yaml(&proj, "governance/project/PROJECT_POLICY.yaml", &pp);
    write_yaml(
        &proj,
        "spec/decisions/D-0001.yaml",
        &json!({"id": "D-0001", "type": "decision", "title": "Keep it simple", "status": "ACTIVE", "question": "?", "chosen_option": "A", "rationale": "r", "human_approved": true}),
    );
    g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "Write docs",
        "--status",
        "READY",
    ]);
    g.ok(&["rebuild-memory"]);
    git_commit_all(&proj, "4.1.1 state");
    let overlay_before = tree_hash(&proj.join("governance/project"), &[]);
    // --- check (CIT-P) ---
    let chk = g.ok(&["update", "--check"]);
    assert_eq!(chk["current"], "4.1.1");
    assert_eq!(chk["available"], gov_runtime::VERSION);
    assert_eq!(chk["migration_path"][0], "M-4.1.1-4.1.2");
    assert_eq!(chk["migration_path"][1], "M-4.1.2-4.1.3");
    assert_eq!(chk["compatible"], true);
    assert_eq!(
        chk["human_gate_required"], true,
        "uncertified target must require a human gate: {chk}"
    );
    assert!(chk["impact"]["consequences"]
        .to_string()
        .contains("not touched"));
    // --- apply without approval → gate; --approve without an answered gate does nothing (INV-008) ---
    let e = g.err(&["update", "--apply"]);
    assert_eq!(e.error_code(), "HUMAN_GATE_REQUIRED");
    let gid = e.details()["gate"].as_str().unwrap().to_string();
    assert_eq!(
        g.ok(&["update", "--apply", "--approve", "--by", "owner"])["applied"],
        false
    );
    g.ok(&["gate", "present", &gid]);
    crate::ws03::human_decide(&g, &gid, "A");
    // --- apply with approval (spec/ measured from here: the gate record above is legitimate governance state) ---
    let spec_before = tree_hash(&proj.join("spec"), &["audits/**", "reports/**"]);
    let ap = g.ok(&["update", "--apply", "--approve", "--by", "owner"]);
    assert_eq!(ap["applied"], true);
    assert_eq!(ap["to"], gov_runtime::VERSION);
    assert_eq!(
        yaml(&proj, "governance/framework.lock")["version"],
        gov_runtime::VERSION
    );
    assert_eq!(
        yaml(&proj, "governance/framework.lock")["lock_schema_version"],
        "1.1.0"
    );
    let pp2 = yaml(&proj, "governance/project/PROJECT_POLICY.yaml");
    assert_eq!(pp2["gates"]["presentation_channel"], "chat");
    assert!(pp2.get("human_gates").is_none());
    assert_eq!(pp2["schema_version"], "1.0.0");
    assert_eq!(
        pp2["policy_overrides"]["MEMORY_POLICY.retrieval.default_k"], 5,
        "project overlay values must be preserved"
    );
    assert_eq!(pp2["project"]["name"], "upd-project");
    assert!(exists(&proj, "governance/project/PROJECT_EXCEPTIONS.yaml"));
    assert!(
        exists(&proj, "governance/kernel/policies/LEARNING_POLICY.yaml")
            && exists(&proj, "governance/kernel/policies/ARCHIVE_POLICY.yaml")
    );
    assert_eq!(
        tree_hash(&proj.join("spec"), &["audits/**", "reports/**"]),
        spec_before,
        "spec/ must not change on framework update (INV-013)"
    );
    assert!(read(&proj, "spec/reports/framework-updates.jsonl")
        .contains(&format!("\"to\":\"{}\"", gov_runtime::VERSION)));
    let d = g.run(&["doctor"]);
    let checks = if d.ok() { d.result() } else { d.details() };
    assert!(
        checks["checks"]
            .as_array()
            .unwrap()
            .iter()
            .all(|c| c["ok"] == true || c["severity"] != "critical"),
        "no critical doctor finding after update: {}",
        checks["checks"]
    );
    assert_eq!(
        json(&proj, "governance/generated/adapter-manifest.json")["kernel_hash"],
        yaml(&proj, "governance/framework.lock")["kernel_manifest_hash"]
    );
    assert_eq!(
        g.ok(&["status"])["framework"]["version"],
        gov_runtime::VERSION
    );
    // --- rollback ---
    let rb = g.ok(&["update", "--rollback"]);
    assert_eq!(rb["rolled_back_to"], "4.1.1");
    assert_eq!(rb["kernel_ok"], true);
    assert_eq!(yaml(&proj, "governance/framework.lock")["version"], "4.1.1");
    assert_eq!(
        tree_hash(&proj.join("governance/project"), &[]),
        overlay_before,
        "overlay restored byte-for-byte"
    );
    assert!(!exists(
        &proj,
        "governance/kernel/policies/LEARNING_POLICY.yaml"
    ));
    let _: Value = g.ok(&["status"]);
}
