//! Fixture 6 — clone into a clean environment: doctor + rebuild-memory reconstruct identical derived state.
use crate::common::*;
use serde_json::json;

#[test]
fn clone_rebuilds_identical_derived_state() {
    let (a, ga) = setup_fixture("greenfield", "mm-a", "S-machineA");
    ga.ok(&[
        "init",
        "--name",
        "orders-ledger",
        "--alias",
        "fx-mm",
        "--intent",
        "ledger",
    ]);
    write_yaml(
        &a,
        "spec/features/F-0001.yaml",
        &json!({"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE", "readiness": readiness_all_present_except(&[], &[])}),
    );
    write_yaml(
        &a,
        "spec/decisions/D-0001.yaml",
        &json!({"id": "D-0001", "type": "decision", "title": "Use integer cents", "status": "ACTIVE", "question": "money type?", "chosen_option": "A", "rationale": "no floating point", "human_approved": true, "affects": ["F-0001"]}),
    );
    ga.ok(&[
        "task",
        "create",
        "--class",
        "implementation",
        "--objective",
        "Implement totals",
        "--feature",
        "F-0001",
        "--status",
        "READY",
        "--allowed",
        "src/**",
    ]);
    ga.ok(&["rebuild-memory"]);
    let ca = ga.ok(&["context", "compile", "TASK-0001"]);
    git_commit_all(&a, "state on machine A");
    let sa = ga.ok(&["status"]);
    let manifest_a = json(&a, "governance/generated/index-manifest.json")["manifest_hash"].clone();
    // machine B: clone; no runtime
    let b = tmp("mm-b");
    let (code, out) = git(
        &a,
        &[
            "clone",
            "-q",
            a.to_str().unwrap(),
            b.join("repo").to_str().unwrap(),
        ],
    );
    assert_eq!(code, 0, "{out}");
    let broot = b.join("repo");
    assert!(!exists(&broot, ".governance-runtime"));
    let gb = Gov::new(&broot, "S-machineB");
    let (ok, msg) = doctor_check(&gb, "D009");
    assert!(
        !ok && msg.contains("absent"),
        "doctor must report the missing runtime: {msg}"
    );
    let rb = gb.ok(&["rebuild-memory"]);
    assert_eq!(
        rb["manifest_hash"], manifest_a,
        "rebuilt manifest must equal the tracked manifest from machine A"
    );
    assert_eq!(
        json(&broot, "governance/generated/index-manifest.json")["manifest_hash"],
        manifest_a
    );
    let sb = gb.ok(&["status"]);
    assert_eq!(sa["tasks"]["counts"], sb["tasks"]["counts"]);
    assert_eq!(sa["next_task"], sb["next_task"]);
    let cb = gb.ok(&["context", "compile", "TASK-0001"]);
    assert_eq!(ca["deterministic_hash"], cb["deterministic_hash"]);
    let (ok2, _) = doctor_check(&gb, "D009");
    assert!(ok2);
    // no opaque binaries were synchronised
    let (_, tracked) = git(&broot, &["ls-files"]);
    assert!(!tracked.contains(".governance-runtime"));
}
