//! Phase-2 repair iteration 1, WS-8 (P2-AR-0020) — builder regression for the root-of-trust and lifecycle-ingress
//! repairs BC-P2-35, BC-P2-36 (presentation part), BC-P2-37 and BC-P2-38.
//!
//! Black-box through the `gov` JSON contract, like the rest of this harness. Builder evidence only (Contract v3 O3):
//! acceptance is decided by fresh independent verifiers with their own held-out tests. The harness keys protected
//! machine state by repository root, so a project copied to another path is another machine.
use crate::common::*;
use crate::srr_material::*;
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

fn project(tag: &str) -> (PathBuf, PathBuf, Gov) {
    let root = tmp(tag);
    let proj = root.join("project");
    std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# ws08 project\n");
    git_init_commit(&proj);
    let g = Gov::new(&proj, &format!("S-{tag}"));
    (root, proj, g)
}

fn provision(root: &Path, g: &Gov, p: &Publisher) {
    let rf = p.write_root(&root.join("admin-domain"), 1, &far_future());
    g.ok(&["trust", "provision", "--anchor", rf.to_str().unwrap()]);
}

/// As [`provision`], with the root also delegating the `human-gate` role to the test owner's key
/// (`crate::ws03::owner`): on a provisioned machine the authenticated human channel is that delegation
/// (BC-P2-10, integration P2-AR-0022), so a test that answers a gate provisions a root that delegates it.
fn provision_with_human_gate(root: &Path, g: &Gov, p: &Publisher) {
    let mut doc = root_doc(
        1,
        &far_future(),
        &[&p.root_a, &p.root_b, &p.root_c],
        2,
        &[&p.release],
        &p.snapshot,
        &p.timestamp,
        Some(&p.recovery),
    );
    let owner = crate::ws03::owner();
    let (kid, entry) = key_entry(&owner);
    doc["keys"][kid.as_str()] = entry;
    doc["roles"]["human-gate"] = json!({"keyids": [owner.keyid.clone()], "threshold": 1});
    let dir = root.join("admin-domain");
    std::fs::create_dir_all(&dir).unwrap();
    let rf = dir.join("root-1.json");
    std::fs::write(&rf, envelope(&doc, &[&p.root_a, &p.root_b])).unwrap();
    g.ok(&["trust", "provision", "--anchor", rf.to_str().unwrap()]);
}

/// A release of the current framework: `<dir>/kernel` + signed metadata.
fn current_release(p: &Publisher, dir: &Path, metadata_version: u64, sequence: u64) -> PathBuf {
    std::fs::create_dir_all(dir).unwrap();
    gov_runtime::kernel::stage_payload(&canonical_root().join("framework"), &dir.join("kernel"))
        .unwrap();
    p.publish(
        dir,
        metadata_version,
        sequence,
        "stable",
        &far_future(),
        "4.0.0",
        1,
    );
    dir.join("kernel")
}

/// A release of the synthetic previous release 4.1.1 (fixtures/update/previous-release/4.1.1).
fn previous_release(p: &Publisher, dir: &Path, metadata_version: u64, sequence: u64) -> PathBuf {
    copy_dir(
        &canonical_root().join("fixtures/update/previous-release/4.1.1"),
        &dir.join("kernel"),
    );
    p.publish(
        dir,
        metadata_version,
        sequence,
        "stable",
        &far_future(),
        "4.0.0",
        1,
    );
    dir.join("kernel")
}

fn init(g: &Gov, source: &Path) -> Value {
    g.ok(&[
        "init",
        "--source",
        source.to_str().unwrap(),
        "--name",
        "w",
        "--alias",
        "fx-w",
        "--skip-index",
    ])
}

/// Rewrite one installed kernel file AND regenerate KERNEL_MANIFEST.json AND framework.lock to agree.
fn consistent_rewrite(proj: &Path, rel_file: &str, old: &str, new: &str) {
    let kd = proj.join("governance/kernel");
    let text = read(&kd, rel_file);
    assert!(text.contains(old), "{rel_file} lacks {old}");
    write(&kd, rel_file, &text.replace(old, new));
    let m = gov_runtime::kernel::build_manifest(&kd).unwrap();
    gov_runtime::util::write_json(&kd.join("KERNEL_MANIFEST.json"), &m).unwrap();
    let mut lock = yaml(proj, "governance/framework.lock");
    lock["release_hash"] = m["payload_hash"].clone();
    lock["kernel_manifest_hash"] = json!(gov_runtime::kernel::manifest_hash(&m));
    write_yaml(proj, "governance/framework.lock", &lock);
}

fn presented(o: &Out) -> String {
    o.envelope["release_trust"]["presented_as"]
        .as_str()
        .unwrap_or("")
        .to_string()
}

fn update_through_gate(g: &Gov, source: &Path) -> Out {
    let s = source.to_str().unwrap();
    let first = g.run(&["update", "--apply", "--source", s]);
    if first.ok() {
        return first;
    }
    let gid = first.details()["gate"].as_str().unwrap_or("").to_string();
    assert!(!gid.is_empty(), "no gate raised: {}", first.envelope);
    // BC-P2-10 (WS-3): the human answers through the owner-signed channel (renders the package, then decides)
    crate::ws03::human_decide(g, &gid, "A");
    g.run(&[
        "update",
        "--apply",
        "--source",
        s,
        "--approve",
        "--by",
        "owner",
    ])
}

/// BC-P2-35: a mutually consistent payload + KERNEL_MANIFEST.json + framework.lock rewrite is detected against this
/// machine's protected installation record and fails closed; the rewritten pin is named; restoring it and
/// reinstalling the signed release restores a trusted kernel.
#[test]
fn a_consistent_post_install_rewrite_is_detected_against_the_protected_record() {
    let (root, proj, g) = project("ws08-rewrite");
    let p = Publisher::new();
    provision(&root, &g, &p);
    let rel = current_release(&p, &root.join("rel"), 1, 20);
    init(&g, &rel);
    consistent_rewrite(
        &proj,
        "policies/SECURITY_POLICY.yaml",
        "never_index_classes: [secret, restricted]",
        "never_index_classes: []",
    );
    let kv = g.ok(&["kernel", "verify"]);
    assert_eq!(kv["ok"], false, "{kv}");
    assert!(kv["modified"]
        .as_array()
        .unwrap()
        .contains(&json!("policies/SECURITY_POLICY.yaml")));
    assert_eq!(kv["trust"]["verified"], false);
    let e = g.err(&["task", "create", "--objective", "after the rewrite"]);
    assert_eq!(e.error_code(), "KERNEL_TAMPERED");
    let eff = g.ok(&["policy", "effective", "SECURITY_POLICY"]);
    assert_eq!(
        eff["effective"]["never_index_classes"],
        json!(["secret", "restricted"]),
        "the security floor must come from the embedded baseline"
    );
    let (d003, msg) = doctor_check(&g, "D003");
    assert!(!d003 && msg.contains("SECURITY_POLICY"), "{msg}");
    // the remedy: the rewritten pin is named before anything moves
    let lock_before = read(&proj, "governance/framework.lock");
    let e = g.err(&["kernel", "reinstall", "--source", rel.to_str().unwrap()]);
    assert_eq!(e.error_code(), "KERNEL_PIN_REWRITTEN", "{}", e.envelope);
    assert_eq!(read(&proj, "governance/framework.lock"), lock_before);
    let rec = e.details()["this_machine_committed"].clone();
    let mut lock = yaml(&proj, "governance/framework.lock");
    lock["release_hash"] = rec["release_hash"].clone();
    lock["kernel_manifest_hash"] = rec["kernel_manifest_hash"].clone();
    write_yaml(&proj, "governance/framework.lock", &lock);
    g.ok(&["kernel", "reinstall", "--source", rel.to_str().unwrap()]);
    assert_eq!(g.ok(&["kernel", "trust"])["verified"], true);
    g.ok(&["task", "create", "--objective", "after the remedy"]);
}

/// BC-P2-35 / ARCH-0003 §8: a provisioned machine that did not install the project (another root = another machine
/// in this harness) refuses privileged work until it has verified the pinned signed release.
#[test]
fn a_machine_that_did_not_install_the_project_verifies_the_pinned_release_first() {
    let (root, proj, g) = project("ws08-clone-a");
    let p = Publisher::new();
    provision(&root, &g, &p);
    let rel = current_release(&p, &root.join("rel"), 1, 20);
    init(&g, &rel);
    let other = tmp("ws08-clone-b").join("project");
    copy_dir(&proj, &other);
    let gb = Gov::new(&other, "S-ws08-clone-b");
    provision(&other.parent().unwrap().to_path_buf(), &gb, &p);
    let e = gb.err(&["task", "create", "--objective", "on machine B"]);
    assert_eq!(e.error_code(), "KERNEL_UNANCHORED", "{}", e.envelope);
    assert_eq!(presented(&gb.run(&["status"])), "UNAUTHENTICATED");
    gb.ok(&["kernel", "reinstall", "--source", rel.to_str().unwrap()]);
    gb.ok(&["task", "create", "--objective", "on machine B, verified"]);
    assert_eq!(presented(&gb.run(&["status"])), "CURRENT");
}

/// BC-P2-36 (presentation): on a machine with no trust anchor, nothing installed is presented as current or verified,
/// and the surfaces disclose it; an authentic install on a provisioned machine is presented as current.
#[test]
fn an_unauthenticated_installation_is_never_presented_as_current() {
    let (_root, proj, g) = project("ws08-unprov");
    g.ok(&["init", "--name", "u", "--alias", "fx-u", "--skip-index"]);
    for args in [
        vec!["status"],
        vec!["doctor"],
        vec!["gate", "list"],
        vec!["kernel", "trust"],
    ] {
        let o = g.run(&args);
        assert_eq!(presented(&o), "UNAUTHENTICATED", "{args:?}: {}", o.envelope);
        assert!(
            o.envelope["release_trust"]["disclosure"]
                .as_array()
                .map(|a| !a.is_empty())
                .unwrap_or(false),
            "{args:?} carries no disclosure"
        );
    }
    let st = g.ok(&["status"]);
    assert!(st["release_trust"]["verified_release"].is_null(), "{st}");
    let d = g.run(&["doctor"]);
    let r = if d.ok() { d.result() } else { d.details() };
    assert_eq!(r["release_trust"]["presented_as"], "UNAUTHENTICATED");
    let ts = g.ok(&["trust", "status"]);
    assert!(ts["installed_release"].is_null(), "{ts}");
    assert!(ts["installations"]
        .as_array()
        .unwrap()
        .iter()
        .any(|i| i["authenticity"] == "UNKNOWN"));
    assert!(yaml(&proj, "governance/framework.lock")["authenticity"] == "UNKNOWN");
    // control: provisioned, authentic
    let (root2, _proj2, g2) = project("ws08-prov");
    let p = Publisher::new();
    provision(&root2, &g2, &p);
    let rel = current_release(&p, &root2.join("rel"), 1, 20);
    init(&g2, &rel);
    assert_eq!(presented(&g2.run(&["status"])), "CURRENT");
}

/// BC-P2-37: certification is believed only from signed release metadata; an unsigned claim never waives the Human
/// Decision Gate; `gov` cannot mint a certification claim.
#[test]
fn certification_is_taken_only_from_the_trust_root() {
    let (root, proj, g) = project("ws08-cert");
    let p = Publisher::new();
    provision(&root, &g, &p);
    let prev = previous_release(&p, &root.join("prev"), 1, 10);
    init(&g, &prev);
    let hi_dir = root.join("hi");
    let hi = current_release(&p, &hi_dir, 2, 20);
    write(
        &hi_dir,
        "manifest.json",
        &json!({"version": gov_runtime::VERSION, "certification": {"status": "CERTIFIED"}})
            .to_string(),
    );
    let chk = g.ok(&["update", "--check", "--source", hi.to_str().unwrap()]);
    assert_eq!(chk["human_gate_required"], true, "{chk}");
    assert_ne!(chk["certification"], "CERTIFIED");
    assert_eq!(chk["certification_basis"]["unsigned_claim"], "CERTIFIED");
    assert_eq!(chk["certification_basis"]["authenticated"], false);
    // the trust-root-authenticated carrier: evidence.certification in signed release metadata
    let mut rel = release_doc(&hi, 3, 21, "stable", &far_future(), "4.0.0", 1);
    rel["evidence"] = json!({"certification": {"status": "CERTIFIED"}});
    p.reseal(&hi_dir.join("metadata"), &rel, 3, &far_future());
    let chk = g.ok(&["update", "--check", "--source", hi.to_str().unwrap()]);
    assert_eq!(chk["certification"], "CERTIFIED", "{chk}");
    assert_eq!(chk["certification_basis"]["authenticated"], true);
    // minting is refused for every role, before anything is written
    for role in ["orchestrator", "research-agent"] {
        let out = root.join(format!("mint-{role}"));
        let e = g.with_role(role).err(&[
            "release",
            "build",
            "--version",
            gov_runtime::VERSION,
            "--canonical",
            canonical_root().to_str().unwrap(),
            "--out",
            out.to_str().unwrap(),
            "--certification",
            "CERTIFIED",
        ]);
        assert_eq!(
            e.error_code(),
            "RELEASE_CERTIFICATION_REQUIRES_SIGNED_METADATA"
        );
        assert!(!out.join("releases").exists());
    }
    let _ = proj;
}

/// BC-P2-37: framework.lock records the verified identity and its basis; a signed release commit is recorded.
#[test]
fn framework_lock_records_the_verified_identity_and_its_basis() {
    let (root, proj, g) = project("ws08-lock");
    let p = Publisher::new();
    provision(&root, &g, &p);
    let dir = root.join("rel");
    let k = current_release(&p, &dir, 1, 20);
    let mut rel = release_doc(&k, 2, 20, "stable", &far_future(), "4.0.0", 1);
    rel["evidence"] =
        json!({"provenance": {"release_commit": "0123456789abcdef0123456789abcdef01234567"}});
    p.reseal(&dir.join("metadata"), &rel, 2, &far_future());
    init(&g, &k);
    let lock = yaml(&proj, "governance/framework.lock");
    assert_eq!(lock["authenticity"], "AUTHENTIC", "{lock}");
    assert_eq!(lock["sequence"], 20);
    assert_eq!(lock["channel"], "stable");
    assert!(lock["release_metadata_sha256"].as_str().unwrap().len() == 64);
    assert_eq!(
        lock["release_commit"],
        "0123456789abcdef0123456789abcdef01234567"
    );
    assert!(lock["identity_basis"]["release_commit"]
        .as_str()
        .unwrap()
        .contains("signed release metadata"));
    assert!(lock["source"].as_str().unwrap().starts_with("release:"));
}

/// BC-P2-38: on a provisioned machine the rollback ingress restores a release this machine verified — refused below
/// floor without the owner's break-glass authorisation, admitted with it; no floor moves.
#[test]
fn a_provisioned_machine_rolls_back_to_a_release_it_verified() {
    let (root, proj, g) = project("ws08-rollback");
    let p = Publisher::new();
    provision_with_human_gate(&root, &g, &p);
    let prev = previous_release(&p, &root.join("prev"), 1, 10);
    init(&g, &prev);
    let hi = current_release(&p, &root.join("hi"), 2, 20);
    let up = update_through_gate(&g, &hi);
    assert!(up.ok(), "{}", up.envelope);
    assert_eq!(
        yaml(&proj, "governance/framework.lock")["version"],
        gov_runtime::VERSION
    );
    let floors = g.ok(&["trust", "status"])["floors"]["release_high_water"].clone();
    let e = g.err(&["update", "--rollback"]);
    assert_eq!(e.error_code(), "SRR_BELOW_FLOOR", "{}", e.envelope);
    assert_eq!(
        yaml(&proj, "governance/framework.lock")["version"],
        gov_runtime::VERSION
    );
    let inbox = PathBuf::from(g.ok(&["trust", "break-glass"])["inbox"].as_str().unwrap());
    let mid = g.ok(&["trust", "status"])["machine_id"]
        .as_str()
        .unwrap()
        .to_string();
    let (_, payload_hash, kmh, ver) = measure(&prev);
    let tok = break_glass_doc(
        &mid,
        "ws08-rb",
        "roll back a bad update",
        &far_future(),
        &ver,
        &payload_hash,
        &kmh,
    );
    std::fs::write(inbox.join("auth.json"), envelope(&tok, &[&p.recovery])).unwrap();
    let r = g.ok(&["update", "--rollback", "--break-glass", "--reason", "ws08"]);
    assert_eq!(
        r["release_authenticity"]["authenticity"], "PREVIOUSLY_VERIFIED_BY_THIS_MACHINE",
        "{r}"
    );
    assert_eq!(yaml(&proj, "governance/framework.lock")["version"], "4.1.1");
    assert_eq!(g.ok(&["kernel", "trust"])["verified"], true);
    let ts = g.ok(&["trust", "status"]);
    assert_eq!(ts["degraded"]["marking"], "DEGRADED — RECOVERY ONLY");
    assert_eq!(ts["floors"]["release_high_water"], floors, "a floor moved");
}

/// BC-P2-38: refused privileged lifecycle commands leave the installation as they found it.
#[test]
fn refused_lifecycle_commands_leave_the_installation_as_they_found_it() {
    let (root, proj, g) = project("ws08-atomic");
    let p = Publisher::new();
    provision_with_human_gate(&root, &g, &p);
    let prev = previous_release(&p, &root.join("prev"), 1, 10);
    init(&g, &prev);
    let manifest_before = read(&proj, "governance/kernel/KERNEL_MANIFEST.json");
    let lock_before = read(&proj, "governance/framework.lock");
    // a reinstall of a different (authentic, above-floor) release is a version change: refused before the swap
    let hi = current_release(&p, &root.join("hi"), 2, 20);
    let e = g.err(&["kernel", "reinstall", "--source", hi.to_str().unwrap()]);
    assert_eq!(e.error_code(), "KERNEL_MISMATCH");
    assert_eq!(e.details()["installation_changed"], false);
    assert_eq!(
        read(&proj, "governance/kernel/KERNEL_MANIFEST.json"),
        manifest_before
    );
    assert_eq!(read(&proj, "governance/framework.lock"), lock_before);
    assert_eq!(g.ok(&["kernel", "trust"])["verified"], true);
    // an update refused by the single verifier leaves no snapshot to "roll back"
    let unsigned = root.join("unsigned");
    std::fs::create_dir_all(&unsigned).unwrap();
    gov_runtime::kernel::stage_payload(
        &canonical_root().join("framework"),
        &unsigned.join("kernel"),
    )
    .unwrap();
    let up = update_through_gate(&g, &unsigned.join("kernel"));
    assert_eq!(up.error_code(), "SRR_RELEASE_UNVERIFIED", "{}", up.envelope);
    let snaps = proj.join(".governance-runtime/update");
    assert!(
        !snaps.exists() || std::fs::read_dir(&snaps).unwrap().next().is_none(),
        "a refused update left a snapshot behind"
    );
    assert_eq!(
        g.err(&["update", "--rollback"]).error_code(),
        "SNAPSHOT_MISSING"
    );
    assert_eq!(read(&proj, "governance/framework.lock"), lock_before);
}
