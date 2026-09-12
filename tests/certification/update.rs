//! Fixture 4 — framework update from a synthetic previous release 4.1.1 to the 4.1.2 candidate, then rollback.
use crate::common::*;
use serde_json::{json, Value};
use std::path::Path;

/// Derive the synthetic 4.1.1 kernel payload from the current framework (differences documented in fixtures/update/README.md).
fn make_previous_release(dst: &Path) {
    let src = canonical_root().join("framework");
    copy_dir(&src, dst);
    copy_dir(&canonical_root().join("tools"), &dst.join("tools"));
    let mut k = gov_runtime::util::read_yaml(&dst.join("KERNEL.yaml")).unwrap();
    k["version"] = json!("4.1.1"); k["cli_version"] = json!("4.1.1"); k["runtime_version"] = json!("4.1.1"); k["supported_from_versions"] = json!([]);
    k["payload_dirs"] = json!(["constitution", "policies", "schemas", "skills", "adapters", "roles", "taxonomy", "commands", "overlay-templates", "tools"]);
    gov_runtime::util::write_yaml(&dst.join("KERNEL.yaml"), &k).unwrap();
    std::fs::remove_file(dst.join("policies/LEARNING_POLICY.yaml")).unwrap();
    std::fs::remove_file(dst.join("policies/ARCHIVE_POLICY.yaml")).unwrap();
    std::fs::remove_file(dst.join("overlay-templates/PROJECT_EXCEPTIONS.yaml")).unwrap();
    std::fs::remove_file(dst.join("schemas/project-exceptions.schema.json")).unwrap();
    let pp = std::fs::read_to_string(dst.join("overlay-templates/PROJECT_POLICY.yaml")).unwrap().replace("schema_version: 1.0.0", "schema_version: 0.9.0").replace("gates:\n  presentation_channel: chat\n", "human_gates:\n  channel: chat\n");
    std::fs::write(dst.join("overlay-templates/PROJECT_POLICY.yaml"), pp).unwrap();
}

#[test]
fn update_from_previous_release_preserves_project_and_rolls_back() {
    let root = tmp("update");
    let prev = root.join("_prev-4.1.1"); std::fs::create_dir_all(&prev).unwrap();
    make_previous_release(&prev);
    let proj = root.join("project"); std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# upd project\n");
    git_init_commit(&proj);
    let g = Gov::new(&proj, "S-upd");
    let r = g.ok(&["init", "--source", prev.to_str().unwrap(), "--name", "upd-project", "--alias", "fx-upd"]);
    assert_eq!(r["version"], "4.1.1");
    assert!(!exists(&proj, "governance/project/PROJECT_EXCEPTIONS.yaml"));
    assert!(read(&proj, "governance/project/PROJECT_POLICY.yaml").contains("human_gates:"));
    // project state that must survive
    let mut pp = yaml(&proj, "governance/project/PROJECT_POLICY.yaml");
    pp["policy_overrides"] = json!({"MEMORY_POLICY.retrieval.default_k": 5});
    write_yaml(&proj, "governance/project/PROJECT_POLICY.yaml", &pp);
    write_yaml(&proj, "spec/decisions/D-0001.yaml", &json!({"id": "D-0001", "type": "decision", "title": "Keep it simple", "status": "ACTIVE", "question": "?", "chosen_option": "A", "rationale": "r", "human_approved": true}));
    g.ok(&["task", "create", "--class", "documentation", "--objective", "Write docs", "--status", "READY"]);
    g.ok(&["rebuild-memory"]);
    git_commit_all(&proj, "4.1.1 state");
    let overlay_before = tree_hash(&proj.join("governance/project"), &[]);
    // --- check (CIT-P) ---
    let chk = g.ok(&["update", "--check"]);
    assert_eq!(chk["current"], "4.1.1"); assert_eq!(chk["available"], "4.1.2");
    assert_eq!(chk["migration_path"][0], "M-4.1.1-4.1.2"); assert_eq!(chk["compatible"], true);
    assert_eq!(chk["human_gate_required"], true, "uncertified target must require a human gate: {chk}");
    assert!(chk["impact"]["consequences"].to_string().contains("not touched"));
    // --- apply without approval → gate ---
    let e = g.err(&["update", "--apply"]);
    assert_eq!(e.error_code(), "HUMAN_GATE_REQUIRED");
    assert!(g.ok(&["gate", "list"]).as_array().unwrap().len() >= 1);
    // --- apply with approval (spec/ measured from here: the gate record above is legitimate governance state) ---
    let spec_before = tree_hash(&proj.join("spec"), &["audits/**", "reports/**"]);
    let ap = g.ok(&["update", "--apply", "--approve", "--by", "owner"]);
    assert_eq!(ap["applied"], true); assert_eq!(ap["to"], "4.1.2");
    assert_eq!(yaml(&proj, "governance/framework.lock")["version"], "4.1.2");
    assert_eq!(yaml(&proj, "governance/framework.lock")["lock_schema_version"], "1.0.0");
    let pp2 = yaml(&proj, "governance/project/PROJECT_POLICY.yaml");
    assert_eq!(pp2["gates"]["presentation_channel"], "chat"); assert!(pp2.get("human_gates").is_none());
    assert_eq!(pp2["schema_version"], "1.0.0");
    assert_eq!(pp2["policy_overrides"]["MEMORY_POLICY.retrieval.default_k"], 5, "project overlay values must be preserved");
    assert_eq!(pp2["project"]["name"], "upd-project");
    assert!(exists(&proj, "governance/project/PROJECT_EXCEPTIONS.yaml"));
    assert!(exists(&proj, "governance/kernel/policies/LEARNING_POLICY.yaml") && exists(&proj, "governance/kernel/policies/ARCHIVE_POLICY.yaml"));
    assert_eq!(tree_hash(&proj.join("spec"), &["audits/**", "reports/**"]), spec_before, "spec/ must not change on framework update (INV-013)");
    assert!(read(&proj, "spec/reports/framework-updates.jsonl").contains("\"to\":\"4.1.2\""));
    let d = g.run(&["doctor"]);
    let checks = if d.ok() { d.result() } else { d.details() };
    assert!(checks["checks"].as_array().unwrap().iter().all(|c| c["ok"] == true || c["severity"] != "critical"), "no critical doctor finding after update: {}", checks["checks"]);
    assert_eq!(json(&proj, "governance/generated/adapter-manifest.json")["kernel_hash"], yaml(&proj, "governance/framework.lock")["kernel_manifest_hash"]);
    assert_eq!(g.ok(&["status"])["framework"]["version"], "4.1.2");
    // --- rollback ---
    let rb = g.ok(&["update", "--rollback"]);
    assert_eq!(rb["rolled_back_to"], "4.1.1"); assert_eq!(rb["kernel_ok"], true);
    assert_eq!(yaml(&proj, "governance/framework.lock")["version"], "4.1.1");
    assert_eq!(tree_hash(&proj.join("governance/project"), &[]), overlay_before, "overlay restored byte-for-byte");
    assert!(!exists(&proj, "governance/kernel/policies/LEARNING_POLICY.yaml"));
    let _: Value = g.ok(&["status"]);
}
