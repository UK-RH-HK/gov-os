//! Phase-2 repair iteration 1, round 2, WS-8 (P2-AR-0029) — builder regression for OWNER-DECISION-P2-0002
//! (Option A: refuse external-source kernel ingress until the machine is provisioned): BC-P2-36 admission, the
//! unprovisioned sub-case of BC-P2-35, IP-WS02-15 (the embedded-kernel cache), IP-WS02-12 (G5 at update), IP-7 (update
//! reads its gate answer through the verified-answer API) and IP-2 / IP-WS02-13 (release build).
//!
//! Builder evidence only (Contract v3 O3). Scenarios that are ABOUT a machine with no trust anchor say so and do not
//! provision it; every other scenario follows the documented first-run path, provision then install.
use crate::common::*;
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

const REFUSED: &str = "SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED";

/// A project on a machine with NO trust anchor (this file's subject). Returns (scratch, project, gov).
fn unprovisioned_project(tag: &str) -> (PathBuf, PathBuf, Gov) {
    let root = tmp(tag);
    let proj = root.join("project");
    std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# ws08 round 2\n");
    git_init_commit(&proj);
    let g = Gov::new(&proj, &format!("S-{tag}"));
    (root, proj, g)
}

/// External-source kernel material: the stored synthetic 4.1.1 payload (a different release).
fn external_release() -> PathBuf {
    canonical_root().join("fixtures/update/previous-release/4.1.1")
}

/// External-source kernel material that claims to be the current release: a copy of this checkout's framework with
/// one policy byte changed. Nothing about its path or its KERNEL.yaml distinguishes it; only its content does.
fn doctored_current(tag: &str) -> PathBuf {
    let dir = tmp(tag).join("framework");
    copy_dir(&canonical_root().join("framework"), &dir);
    copy_dir(
        &canonical_root().join("migrations"),
        &dir.parent().unwrap().join("migrations"),
    );
    copy_dir(
        &canonical_root().join("tools"),
        &dir.parent().unwrap().join("tools"),
    );
    let p = "policies/SECURITY_POLICY.yaml";
    let text = read(&dir, p);
    write(&dir, p, &format!("{text}\n# doctored\n"));
    dir
}

/// External-source kernel material that is a genuinely newer release: the current framework as a hypothetical 9.9.9
/// with a declared, non-breaking migration from the current version (so `gov update` would otherwise proceed).
fn newer_external(tag: &str) -> PathBuf {
    let dir = doctored_current(tag);
    let ky = dir.join("KERNEL.yaml");
    let text = std::fs::read_to_string(&ky).unwrap();
    let text = text
        .replacen(
            &format!("version: {}", gov_runtime::VERSION),
            "version: 9.9.9",
            1,
        )
        .replacen(
            "supported_from_versions: [",
            &format!("supported_from_versions: [\"{}\", ", gov_runtime::VERSION),
            1,
        );
    std::fs::write(&ky, text).unwrap();
    let mig = dir.parent().unwrap().join("migrations");
    // round-2 integration (P2-AR-0032): the canonical tree now also carries a prepared migration from the current
    // version to the next, unreleased one (WS-9/11, `M-4.1.5-4.1.6`); a hypothetical 9.9.9 release declares its own
    // step from the current version, so the copied tree keeps no other step from it (the chain resolver follows the
    // first step from the installed version)
    for e in std::fs::read_dir(&mig).unwrap().filter_map(|e| e.ok()) {
        let n = e.file_name().to_string_lossy().to_string();
        if n.starts_with(&format!("M-{}-", gov_runtime::VERSION)) {
            std::fs::remove_file(e.path()).unwrap();
        }
    }
    std::fs::write(
        mig.join(format!("M-{}-9.9.9.yaml", gov_runtime::VERSION)),
        format!("id: M-{v}-9.9.9\nfrom_version: {v}\nto_version: 9.9.9\ndescription: hypothetical external release\nbreaking: false\nhuman_gate: none\naffected_indexes: []\noverlay_template_changes: []\noperations:\n  - {{op: note, text: \"hypothetical\"}}\nrollback: gov update --rollback\n", v = gov_runtime::VERSION),
    )
    .unwrap();
    dir
}

fn presented(o: &Out) -> String {
    o.envelope["release_trust"]["presented_as"]
        .as_str()
        .unwrap_or("")
        .to_string()
}

fn staging_is_empty(g: &Gov) -> bool {
    std::fs::read_dir(machine_state_dir(&g.root).join("staging"))
        .map(|rd| rd.count() == 0)
        .unwrap_or(true)
}

fn human_gates(proj: &Path) -> usize {
    std::fs::read_dir(proj.join("spec/decisions"))
        .map(|rd| {
            rd.filter_map(|e| e.ok())
                .filter(|e| e.file_name().to_string_lossy().starts_with("HDG-"))
                .count()
        })
        .unwrap_or(0)
}

// ------------------------------------------------------------------------------------ requirement 1: refusal

/// OWNER-DECISION-P2-0002 requirement 1: on a machine with no administrator-provisioned trust anchor, privileged
/// kernel material from an external source is refused at every ingress — typed, observable, remediation
/// "provision" — before it is staged for installation, and a refused ingress leaves the installation as it was.
#[test]
fn an_unprovisioned_machine_refuses_external_source_kernel_ingress_at_every_ingress() {
    let (_root, proj, g) = unprovisioned_project("ws08r2-refuse");
    // init --source: another release, and a doctored copy of the current one
    for src in [external_release(), doctored_current("ws08r2-doctored")] {
        let e = g.err(&[
            "init",
            "--source",
            src.to_str().unwrap(),
            "--name",
            "r",
            "--alias",
            "fx-r",
            "--skip-index",
        ]);
        assert_eq!(e.error_code(), REFUSED, "{}", e.envelope);
        assert_eq!(e.details()["decision"], "OWNER-DECISION-P2-0002");
        assert_eq!(e.details()["staged_for_installation"], false);
        assert!(e.details()["remediation"][0]
            .as_str()
            .unwrap()
            .contains("gov trust provision"));
        assert!(!exists(&proj, "governance/kernel") && !exists(&proj, "governance/framework.lock"));
        assert!(
            staging_is_empty(&g),
            "a refused candidate left staged bytes behind"
        );
    }
    // a release SIGNED under some root is still external material here: without an anchor nothing can verify it
    let signed_old = signed_copy(
        &external_release(),
        "ws08r2-signed-old",
        sequence_of("4.1.1"),
    );
    let e = g.err(&[
        "init",
        "--source",
        signed_old.to_str().unwrap(),
        "--name",
        "r",
    ]);
    assert_eq!(e.error_code(), REFUSED, "{}", e.envelope);
    let ts = g.ok(&["trust", "status"]);
    assert_eq!(ts["posture"], "UNPROVISIONED");
    assert!(ts["installations"].as_array().unwrap().is_empty(), "{ts}");

    // the one admissible payload: the binary's own, as a bootstrap installation
    g.ok(&["init", "--name", "r", "--alias", "fx-r", "--skip-index"]);
    git_commit_all(&proj, "bootstrap");
    let lock_before = read(&proj, "governance/framework.lock");
    let manifest_before = read(&proj, "governance/kernel/KERNEL_MANIFEST.json");
    let unchanged = |what: &str| {
        assert_eq!(
            read(&proj, "governance/framework.lock"),
            lock_before,
            "{what}: lock changed"
        );
        assert_eq!(
            read(&proj, "governance/kernel/KERNEL_MANIFEST.json"),
            manifest_before,
            "{what}: kernel changed"
        );
        assert!(staging_is_empty(&g), "{what}: staged bytes left behind");
    };
    let ext = external_release();
    let ext_s = ext.to_str().unwrap();
    let newer = newer_external("ws08r2-newer");
    let newer_s = newer.to_str().unwrap();
    // update: said by --check, refused by --apply before any Human Decision Gate is raised for it
    let chk = g.ok(&["update", "--check", "--source", newer_s]);
    assert_eq!(chk["available"], "9.9.9", "{chk}");
    assert_eq!(chk["compatible"], true, "{chk}");
    assert_eq!(chk["admission"]["refused_before_staging"], true, "{chk}");
    assert_eq!(chk["admission"]["code"], REFUSED);
    let gates_before = human_gates(&proj);
    let e = g.err(&["update", "--apply", "--source", newer_s]);
    assert_eq!(e.error_code(), REFUSED, "{}", e.envelope);
    assert_eq!(
        human_gates(&proj),
        gates_before,
        "a gate was raised for a refused update"
    );
    unchanged("update --apply");
    // kernel reinstall
    let e = g.err(&["kernel", "reinstall", "--source", ext_s]);
    assert_eq!(e.error_code(), REFUSED, "{}", e.envelope);
    unchanged("kernel reinstall");
    // rollback: an update snapshot is repository-local content; its kernel is external material here
    let snap = proj.join(".governance-runtime/update/9.9.9");
    copy_dir(&ext, &snap.join("kernel"));
    copy_dir(&proj.join("governance/project"), &snap.join("project"));
    std::fs::copy(
        proj.join("governance/framework.lock"),
        snap.join("framework.lock"),
    )
    .unwrap();
    gov_runtime::util::write_json(
        &snap.join("snapshot.json"),
        &json!({"from": "4.1.1", "to": "9.9.9", "at": "2026-01-01T00:00:00Z", "migrations": []}),
    )
    .unwrap();
    let e = g.err(&["update", "--rollback"]);
    assert_eq!(e.error_code(), REFUSED, "{}", e.envelope);
    unchanged("update --rollback");

    // adopt: A6 batch 0 installs through the same ingress
    let (mroot, planner) = setup_fixture_unprovisioned("migration", "ws08r2-adopt", "S-planner");
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
    // round-2 integration (P2-AR-0032): WS-9/11 (BC-P2-34) — the designated reviewer approves with tests of its own
    crate::migration::reviewer_authors_tests(&mroot);
    planner
        .with_session("S-rev")
        .with_role("migration-reviewer")
        .ok(&["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"]);
    let e = planner
        .with_session("S-exec")
        .with_role("migration-executor")
        .err(&[
            "adopt", "migrate", "--batch", "0", "--source", ext_s, "--name", "m", "--alias", "fx-m",
        ]);
    assert_eq!(e.error_code(), REFUSED, "{}", e.envelope);
    assert!(!exists(&mroot, "governance/kernel") && !exists(&mroot, "governance/framework.lock"));
}

// ------------------------------------------------------------------------------------ requirement 2: bootstrap

/// OWNER-DECISION-P2-0002 requirement 2: the verifier binary's own embedded payload may be installed on an
/// unprovisioned machine only as an explicitly marked bootstrap mode tied to the binary's identity, never presented
/// as current, verified or certified, and disclosed. Whether it IS the embedded payload is decided by content: the
/// embedded cache and a byte-identical checkout both qualify.
#[test]
fn the_bootstrap_installation_is_marked_tied_to_the_binary_and_never_presented_as_current() {
    for (tag, via_checkout) in [("ws08r2-boot-emb", false), ("ws08r2-boot-src", true)] {
        let (root, proj, g) = unprovisioned_project(tag);
        let g = if via_checkout {
            g
        } else {
            g.with_env("GOV_CANONICAL_ROOT", "/nonexistent")
                .with_env("GOV_KERNEL_CACHE", root.join("cache").to_str().unwrap())
        };
        let r = g.ok(&["init", "--name", "b", "--alias", "fx-b", "--skip-index"]);
        let ra = &r["release_authenticity"];
        assert_eq!(ra["admission"], "BOOTSTRAP_EMBEDDED_PAYLOAD", "{r}");
        assert_eq!(ra["authenticity"], "UNKNOWN");
        assert_eq!(ra["posture"], "UNPROVISIONED");
        let binary = &ra["bootstrap"]["binary"];
        assert_eq!(binary["embedded_payload_hash"], ra["payload_hash"], "{ra}");
        assert_eq!(binary["gov_version"], gov_runtime::VERSION);
        assert_eq!(
            binary["executable_sha256"].as_str().unwrap().len(),
            64,
            "the bootstrap is tied to the binary that installed it: {binary}"
        );
        assert_eq!(ra["bootstrap"]["decision"], "OWNER-DECISION-P2-0002");
        assert!(ra["notes"].as_array().unwrap().iter().any(|n| n
            .as_str()
            .unwrap()
            .starts_with("BOOTSTRAP_EMBEDDED_PAYLOAD")));
        // the lock records the marking; it never records a verified identity
        let lock = yaml(&proj, "governance/framework.lock");
        assert_eq!(lock["admission"], "BOOTSTRAP_EMBEDDED_PAYLOAD", "{lock}");
        assert_eq!(lock["authenticity"], "UNKNOWN");
        assert!(lock["sequence"].is_null() && lock["release_metadata_sha256"].is_null());
        assert_eq!(lock["release_hash"], binary["embedded_payload_hash"]);
        assert!(lock["identity_basis"]["established_by"]
            .as_str()
            .unwrap()
            .contains("BOOTSTRAP"));
        // never presented as current, and disclosed on every surface
        for args in [
            vec!["status"],
            vec!["doctor"],
            vec!["gate", "list"],
            vec!["version"],
        ] {
            let o = g.run(&args);
            assert_eq!(presented(&o), "UNAUTHENTICATED", "{args:?}: {}", o.envelope);
            assert!(
                o.envelope["release_trust"]["disclosure"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .any(|d| d.as_str().unwrap().contains("BOOTSTRAP installation")),
                "{args:?}: {}",
                o.envelope
            );
        }
        assert!(g.ok(&["status"])["release_trust"]["verified_release"].is_null());
        let chk = g.ok(&["update", "--check"]);
        assert_ne!(chk["recommendation"], "nothing to do", "{chk}");
        // trust status: the posture, the policy, the installation and its marking; no floor was raised
        let ts = g.ok(&["trust", "status"]);
        assert_eq!(ts["posture"], "UNPROVISIONED");
        assert_eq!(
            ts["admission_policy"]["policy"],
            gov_runtime::srr::verifier::UNPROVISIONED_ADMISSION_POLICY
        );
        assert!(ts["installed_release"].is_null(), "{ts}");
        assert!(ts["installations"]
            .as_array()
            .unwrap()
            .iter()
            .any(|i| i["admission"] == "BOOTSTRAP_EMBEDDED_PAYLOAD"
                && i["authenticity"] == "UNKNOWN"));
        assert_eq!(ts["floors"]["release_high_water"]["sequence"], 0, "{ts}");
        // the kernel itself is trusted as the bootstrap baseline: governed work proceeds
        assert_eq!(g.ok(&["kernel", "trust"])["verified"], true);
        g.ok(&[
            "task",
            "create",
            "--class",
            "documentation",
            "--objective",
            "after bootstrap",
        ]);
    }
}

/// Bootstrap is the unprovisioned posture's only door, never a provisioned machine's: a machine with a trust anchor
/// refuses the embedded payload without signed metadata, exactly as before the decision (R1, unchanged).
#[test]
fn a_provisioned_machine_never_installs_in_bootstrap_mode() {
    let (root, proj, g) = unprovisioned_project("ws08r2-prov-noboot");
    provision(&g);
    for gg in [
        g.clone(),
        g.with_env("GOV_CANONICAL_ROOT", "/nonexistent")
            .with_env("GOV_KERNEL_CACHE", root.join("cache").to_str().unwrap()),
    ] {
        let e = gg.err(&["init", "--name", "p", "--alias", "fx-p", "--skip-index"]);
        assert_eq!(e.error_code(), "SRR_RELEASE_UNVERIFIED", "{}", e.envelope);
        assert!(!exists(&proj, "governance/framework.lock"));
    }
    let r = g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "p",
        "--alias",
        "fx-p",
        "--skip-index",
    ]);
    assert_eq!(
        r["release_authenticity"]["admission"],
        "SIGNED_RELEASE_METADATA"
    );
    assert!(r["release_authenticity"]["bootstrap"].is_null());
    assert_eq!(
        yaml(&proj, "governance/framework.lock")["admission"],
        "SIGNED_RELEASE_METADATA"
    );
    assert_eq!(presented(&g.run(&["status"])), "CURRENT");
}

// ------------------------------------------------------------------------------------ BC-P2-35, unprovisioned

/// The unprovisioned sub-case of BC-P2-35, determined by OWNER-DECISION-P2-0002: a mutually consistent rewrite of a
/// bootstrap installation (payload + KERNEL_MANIFEST.json + framework.lock) is external kernel material that never
/// passed an ingress. It is detected against this machine's protected record and fails closed, as on a provisioned
/// machine (round 1 reported it and did not enforce it, pending the owner's answer).
#[test]
fn a_consistent_rewrite_of_a_bootstrap_installation_fails_closed() {
    let (_root, proj, g) = unprovisioned_project("ws08r2-rewrite");
    g.ok(&["init", "--name", "w", "--alias", "fx-w", "--skip-index"]);
    git_commit_all(&proj, "bootstrap");
    let kd = proj.join("governance/kernel");
    let rel = "policies/SECURITY_POLICY.yaml";
    let text = read(&kd, rel);
    let old = "never_index_classes: [secret, restricted]";
    assert!(text.contains(old));
    write(&kd, rel, &text.replace(old, "never_index_classes: []"));
    let m = gov_runtime::kernel::build_manifest(&kd).unwrap();
    gov_runtime::util::write_json(&kd.join("KERNEL_MANIFEST.json"), &m).unwrap();
    let mut lock = yaml(&proj, "governance/framework.lock");
    lock["release_hash"] = m["payload_hash"].clone();
    lock["kernel_manifest_hash"] = json!(gov_runtime::kernel::manifest_hash(&m));
    write_yaml(&proj, "governance/framework.lock", &lock);
    let kv = g.ok(&["kernel", "verify"]);
    assert_eq!(kv["ok"], false, "{kv}");
    assert!(kv["modified"].as_array().unwrap().contains(&json!(rel)));
    assert_eq!(kv["trust"]["protected_record"]["state"], "DIVERGED", "{kv}");
    let e = g.err(&["task", "create", "--objective", "after the rewrite"]);
    assert_eq!(e.error_code(), "KERNEL_TAMPERED", "{}", e.envelope);
    let eff = g.ok(&["policy", "effective", "SECURITY_POLICY"]);
    assert_eq!(
        eff["effective"]["never_index_classes"],
        json!(["secret", "restricted"]),
        "the security floor comes from the embedded baseline"
    );
    let o = g.run(&["status"]);
    assert!(o.envelope["release_trust"]["disclosure"]
        .to_string()
        .contains("NOT ADMITTED"));
    // restoring the committed bootstrap installation restores trust
    git(&proj, &["checkout", "--", "governance"]);
    assert_eq!(g.ok(&["kernel", "trust"])["verified"], true);
    g.ok(&["task", "create", "--objective", "after the restore"]);
}

/// OWNER-DECISION-P2-0002 at use time: kernel material a machine with no trust anchor never admitted — another
/// machine's (verified) install arriving by copy or clone — is not trusted there (`KERNEL_UNANCHORED`, remedy
/// "provision"); the running binary's own payload, which such a machine may bootstrap, is.
#[test]
fn an_unprovisioned_machine_does_not_trust_kernel_material_it_never_admitted() {
    // machine A: provisioned, installs the signed 4.1.1
    let (ra, pa, ga) = unprovisioned_project("ws08r2-useA");
    provision(&ga);
    let k411 = signed_copy(
        &external_release(),
        "ws08r2-use-4.1.1",
        sequence_of("4.1.1"),
    );
    ga.ok(&[
        "init",
        "--source",
        k411.to_str().unwrap(),
        "--name",
        "u",
        "--alias",
        "fx-u",
        "--skip-index",
    ]);
    git_commit_all(&pa, "machine A");
    let _ = ra;
    // machine B: no trust anchor
    let pb = tmp("ws08r2-useB").join("project");
    copy_dir(&pa, &pb);
    let gb = Gov::new(&pb, "S-useB");
    let e = gb.err(&["task", "create", "--objective", "on B"]);
    assert_eq!(e.error_code(), "KERNEL_UNANCHORED", "{}", e.envelope);
    assert_eq!(e.details()["decision"], "OWNER-DECISION-P2-0002");
    assert!(e.details()["remediation"]
        .to_string()
        .contains("gov trust provision"));
    let kt = gb.ok(&["kernel", "trust"]);
    assert_eq!(kt["verified"], false);
    assert_eq!(
        kt["trust"]["protected_record"]["state"], "UNADMITTED",
        "{kt}"
    );
    assert_eq!(presented(&gb.run(&["status"])), "UNAUTHENTICATED");
    // the remedy is the one the refusal names: provision, then verify the pinned release
    provision(&gb);
    gb.ok(&["kernel", "reinstall", "--source", k411.to_str().unwrap()]);
    gb.ok(&[
        "task",
        "create",
        "--objective",
        "on B, provisioned and verified",
    ]);
    assert_eq!(presented(&gb.run(&["status"])), "CURRENT");
    // control: a bootstrap installation of this binary's payload, copied to another unprovisioned machine, is trusted
    let (_rc, pc, gc) = unprovisioned_project("ws08r2-useC");
    gc.ok(&["init", "--name", "c", "--alias", "fx-c", "--skip-index"]);
    let pd = tmp("ws08r2-useD").join("project");
    copy_dir(&pc, &pd);
    let gd = Gov::new(&pd, "S-useD");
    gd.ok(&[
        "task",
        "create",
        "--objective",
        "on D: the embedded payload",
    ]);
}

// ------------------------------------------------------------------------------------ IP-WS02-15

/// IP-WS02-15 — the root cause of the corrupt embedded-kernel cache. A cache directory in the old defect's shape
/// (content-addressed name, `.complete` marker, KERNEL.yaml present, one payload file missing) is never re-used, and
/// concurrent processes materialising one cold cache each end with the exact embedded payload.
#[test]
fn a_corrupt_or_racing_embedded_kernel_cache_is_never_installed() {
    let base = tmp("ws08r2-cache");
    let cache = base.join("cache");
    let mut listing: Vec<(String, String)> = gov_runtime::kernel::embedded::files()
        .iter()
        .map(|(p, b)| (p.to_string(), gov_runtime::util::sha256_hex(b)))
        .collect();
    listing.sort();
    let id = gov_runtime::util::sha256_text(&serde_json::to_string(&listing).unwrap());
    let dir = cache.join("kernels").join(format!(
        "{}-{}",
        gov_runtime::kernel::embedded::version(),
        &id[..12]
    ));
    let dropped = "policies/SECURITY_POLICY.yaml";
    for (rel, bytes) in gov_runtime::kernel::embedded::files() {
        if *rel == dropped {
            continue;
        }
        let p = dir.join(rel);
        std::fs::create_dir_all(p.parent().unwrap()).unwrap();
        std::fs::write(&p, bytes).unwrap();
    }
    std::fs::write(dir.join(".complete"), id.as_bytes()).unwrap();
    assert!(dir.join("KERNEL.yaml").exists() && !dir.join(dropped).exists());
    let (_r, proj, g) = unprovisioned_project("ws08r2-cache-p0");
    let g = g
        .with_env("GOV_CANONICAL_ROOT", "/nonexistent")
        .with_env("GOV_KERNEL_CACHE", cache.to_str().unwrap());
    let r = g.ok(&["init", "--name", "k", "--alias", "fx-k", "--skip-index"]);
    assert_eq!(
        r["release_authenticity"]["admission"],
        "BOOTSTRAP_EMBEDDED_PAYLOAD"
    );
    assert!(exists(&proj, &format!("governance/kernel/{dropped}")));
    assert_eq!(g.ok(&["kernel", "verify"])["ok"], true);
    assert!(
        dir.join(dropped).exists(),
        "the corrupt cache was not replaced"
    );
    // cold cache, concurrent materialisation by several processes
    let cold = base.join("cold");
    let handles: Vec<_> = (0..6)
        .map(|i| {
            let cold = cold.clone();
            std::thread::spawn(move || {
                let (_r, proj, g) = unprovisioned_project(&format!("ws08r2-cache-p{}", i + 1));
                let g = g
                    .with_env("GOV_CANONICAL_ROOT", "/nonexistent")
                    .with_env("GOV_KERNEL_CACHE", cold.to_str().unwrap());
                let o = g.run(&["init", "--name", "k", "--alias", "fx-k", "--skip-index"]);
                (o.ok(), o.envelope.to_string(), proj)
            })
        })
        .collect();
    let embedded = gov_runtime::kernel::embedded_payload_hash();
    for h in handles {
        let (ok, env, proj) = h.join().unwrap();
        assert!(ok, "{env}");
        assert_eq!(
            yaml(&proj, "governance/framework.lock")["release_hash"],
            json!(embedded),
            "a racing materialisation installed something other than the embedded payload"
        );
    }
    let kernels = cold.join("kernels");
    let leftovers: Vec<String> = std::fs::read_dir(&kernels)
        .unwrap()
        .filter_map(|e| e.ok())
        .map(|e| e.file_name().to_string_lossy().to_string())
        .filter(|n| n.starts_with(".staging-") || n.starts_with(".stale-"))
        .collect();
    assert!(leftovers.is_empty(), "staging leftovers: {leftovers:?}");
}

// ------------------------------------------------------------------------------------ IP-7, IP-WS02-12

fn provisioned_at_4_1_1(tag: &str) -> (PathBuf, Gov, PathBuf) {
    let (_r, proj, g) = unprovisioned_project(tag);
    provision(&g);
    let k411 = signed_copy(
        &external_release(),
        &format!("{tag}-4.1.1"),
        sequence_of("4.1.1"),
    );
    g.ok(&[
        "init",
        "--source",
        k411.to_str().unwrap(),
        "--name",
        "u",
        "--alias",
        "fx-u",
    ]);
    git_commit_all(&proj, "4.1.1");
    (proj, g, k411)
}

/// IP-7 (WS-3): `update --apply` honours its gate only through `gates::verified_answer`; a verified answer that
/// declines the update declines it (this outcome was unreachable while the gate record's fields were read directly).
#[test]
fn update_applies_only_on_a_verified_authorising_answer() {
    let (proj, g, _k) = provisioned_at_4_1_1("ws08r2-answer");
    let e = g.err(&["update", "--apply", "--source", signed_source()]);
    assert_eq!(e.error_code(), "HUMAN_GATE_REQUIRED");
    let gid = e.details()["gate"].as_str().unwrap().to_string();
    let r = g.ok(&[
        "update",
        "--apply",
        "--source",
        signed_source(),
        "--approve",
        "--by",
        "owner",
    ]);
    assert_eq!(r["applied"], false);
    assert!(r["reason"]
        .as_str()
        .unwrap()
        .contains("not presented/answered"));
    crate::ws03::human_decide(&g, &gid, "B");
    let r = g.ok(&[
        "update",
        "--apply",
        "--source",
        signed_source(),
        "--approve",
        "--by",
        "owner",
    ]);
    assert_eq!(r["applied"], false, "{r}");
    assert_eq!(r["reason"], "human declined the update");
    assert_eq!(r["answer"]["by_kind"], "human");
    assert_eq!(yaml(&proj, "governance/framework.lock")["version"], "4.1.1");
}

/// IP-WS02-12 (epsilon-r O5-G5-update, A0-O5-09): the post-install verification of an update is the G5 full suite,
/// fresh. An update over a defect only the full suite detects (a task dependency cycle) is refused and rolled back:
/// the installation, the lock and this machine's protected record are as before.
#[test]
fn an_update_over_a_defect_the_full_suite_detects_is_refused_and_rolled_back() {
    let (proj, g, _k) = provisioned_at_4_1_1("ws08r2-g5");
    for (id, dep) in [("TASK-0001", "TASK-0002"), ("TASK-0002", "TASK-0001")] {
        write_yaml(
            &proj,
            &format!("spec/tasks/{id}.yaml"),
            &json!({"id": id, "type": "task", "title": id, "status": "ACTIVE", "task_status": "READY", "class": "documentation", "objective": "o", "dependencies": [dep]}),
        );
    }
    g.ok(&["rebuild-memory"]);
    git_commit_all(&proj, "a dependency cycle");
    let lock_before = read(&proj, "governance/framework.lock");
    let e = g.err(&["update", "--apply", "--source", signed_source()]);
    let gid = e.details()["gate"].as_str().unwrap().to_string();
    crate::ws03::human_decide(&g, &gid, "A");
    let o = g.run(&[
        "update",
        "--apply",
        "--source",
        signed_source(),
        "--approve",
        "--by",
        "owner",
    ]);
    assert!(
        !o.ok(),
        "the update applied over a defect the full suite detects: {}",
        o.envelope
    );
    assert_eq!(o.error_code(), "VERIFICATION_FAILED", "{}", o.envelope);
    assert!(o.envelope["error"]["message"]
        .as_str()
        .unwrap()
        .contains("G5 full governance suite"));
    assert_eq!(read(&proj, "governance/framework.lock"), lock_before);
    assert_eq!(g.ok(&["kernel", "trust"])["verified"], true);
    assert_eq!(yaml(&proj, "governance/framework.lock")["version"], "4.1.1");
}

// ------------------------------------------------------------------------------------ IP-2, IP-WS02-13

/// A canonical tree carrying exactly what a release build and `contracts::verify` read.
fn canonical_copy(tag: &str) -> PathBuf {
    let c = tmp(tag).join("canonical");
    for d in [
        "framework",
        "migrations",
        "tools",
        "tests/governance",
        "docs/generated",
    ] {
        copy_dir(&canonical_root().join(d), &c.join(d));
    }
    std::fs::copy(
        canonical_root().join("Governance_OS_Capability_Acceptance_Contract_v3.md"),
        c.join("Governance_OS_Capability_Acceptance_Contract_v3.md"),
    )
    .unwrap();
    c
}

/// IP-2 (WS-1/12) and IP-WS02-13: a release is built only from a tree whose capability-contract chain is bound to
/// the approved source, the health tier is run or its absence stated (never claimed), and the built release is
/// verified as written; the checks are kept as evidence beside the immutable manifest.
#[test]
fn a_release_is_built_only_from_a_contract_bound_tree_and_verified_as_written() {
    let c = canonical_copy("ws08r2-rel");
    let out = c.parent().unwrap().join("out");
    let g = Gov::new(&c, "S-rel");
    let b = g.ok(&[
        "release",
        "build",
        "--version",
        gov_runtime::VERSION,
        "--canonical",
        c.to_str().unwrap(),
        "--out",
        out.to_str().unwrap(),
        "--certification",
        "READY_FOR_INDEPENDENT_OS_VERIFICATION",
    ]);
    let checks = &b["pre_release_checks"];
    assert_eq!(
        checks["capability_contract"]["verdict"], "CONTRACT_SOURCE_BOUND",
        "{checks}"
    );
    assert_eq!(checks["health"]["tier"], "G5");
    assert_eq!(
        checks["health"]["ran"], false,
        "an uninstalled canonical root has no governed-project suite"
    );
    assert!(checks["health"]["reason"]
        .as_str()
        .unwrap()
        .contains("not a governed installation"));
    assert_eq!(checks["built_release_verified"]["ok"], true);
    // OWNER-DECISION-P2-0002 requirement 4: the build states the posture it ran on (this machine: no trust anchor)
    assert_eq!(checks["machine_posture"], "UNPROVISIONED");
    assert_eq!(checks["release_evidence_eligible"], false);
    let dir = out.join("releases").join(gov_runtime::VERSION);
    assert_eq!(
        json(&dir, "PRE_RELEASE_CHECKS.json")["capability_contract"]["verdict"],
        "CONTRACT_SOURCE_BOUND"
    );
    assert_eq!(
        g.ok(&["release", "verify", dir.to_str().unwrap()])["ok"],
        true
    );
    // a derived contract view that diverges from the approved source: refused before anything is written
    let c2 = canonical_copy("ws08r2-rel-diverged");
    let view = "docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md";
    let text = read(&c2, view);
    write(&c2, view, &format!("{text}\nan unapproved line\n"));
    let out2 = c2.parent().unwrap().join("out");
    let e = Gov::new(&c2, "S-rel2").err(&[
        "release",
        "build",
        "--version",
        gov_runtime::VERSION,
        "--canonical",
        c2.to_str().unwrap(),
        "--out",
        out2.to_str().unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "RELEASE_CONTRACT_NOT_BOUND",
        "{}",
        e.envelope
    );
    assert_eq!(
        e.details()["contract_error"],
        "CONTRACT_GENERATED_VIEW_DIVERGED"
    );
    assert!(!out2.join("releases").exists());
    // a payload-only canonical tree (how release tooling and the root-of-trust probes build releases) carries no
    // contract view to diverge: the build proceeds and records that no binding is claimed
    let c3 = tmp("ws08r2-rel-payload-only").join("canonical");
    for d in ["framework", "migrations", "tools"] {
        copy_dir(&canonical_root().join(d), &c3.join(d));
    }
    let out3 = c3.parent().unwrap().join("out");
    let b3 = Gov::new(&c3, "S-rel3").ok(&[
        "release",
        "build",
        "--version",
        gov_runtime::VERSION,
        "--canonical",
        c3.to_str().unwrap(),
        "--out",
        out3.to_str().unwrap(),
    ]);
    assert_eq!(
        b3["pre_release_checks"]["capability_contract"]["verdict"], "INCOMPLETE_IN_THIS_TREE",
        "{}",
        b3["pre_release_checks"]
    );
    assert_eq!(b3["pre_release_checks"]["release_evidence_eligible"], false);
    let _: Value = Value::Null;
}

// ------------------------------------------------------------------------------------ §5 preserved (R1)

/// The `OWNER-DECISION-0006` §5 restoration route `update --apply` still completes below floor now that the
/// post-install verification is the G5 full suite (IP-WS02-12): a machine in owner-authorised break-glass, on a release
/// below its high-water, restores an authenticated at-floor release that needs no Human Decision Gate (its
/// certification is bound by signed metadata), and the marking clears (§7). The allow-list is unchanged; this measures
/// that the reachable behaviour behind its `update --apply` entry is unchanged too.
#[test]
fn below_floor_restoration_by_update_still_completes_with_the_g5_post_install_suite() {
    use crate::srr_material::*;
    let (proj, g, k411) = provisioned_at_4_1_1("ws08r2-s5");
    let e = g.err(&["update", "--apply", "--source", signed_source()]);
    let gid = e.details()["gate"].as_str().unwrap().to_string();
    crate::ws03::human_decide(&g, &gid, "A");
    let up = g.ok(&[
        "update",
        "--apply",
        "--source",
        signed_source(),
        "--approve",
        "--by",
        "owner",
    ]);
    assert_eq!(up["applied"], true, "{up}");
    break_glass(&g, &k411, "ws08r2-s5-rb");
    g.ok(&[
        "update",
        "--rollback",
        "--break-glass",
        "--reason",
        "restore drill",
    ]);
    let ts = g.ok(&["trust", "status"]);
    assert_eq!(
        ts["degraded"]["marking"], "DEGRADED — RECOVERY ONLY",
        "{ts}"
    );
    assert_eq!(yaml(&proj, "governance/framework.lock")["version"], "4.1.1");
    // the at-floor release, its certification bound by release metadata signed under the suite root
    let dir = tmp("ws08r2-s5-certified");
    gov_runtime::kernel::stage_payload(&canonical_root().join("framework"), &dir.join("kernel"))
        .unwrap();
    let mut rel = release_doc(
        &dir.join("kernel"),
        CURRENT_SEQUENCE + 1,
        CURRENT_SEQUENCE,
        "stable",
        &far_future(),
        "",
        0,
    );
    rel["evidence"] = json!({"certification": {"status": "CERTIFIED"}});
    std::fs::create_dir_all(dir.join("metadata")).unwrap();
    suite_publisher().reseal(
        &dir.join("metadata"),
        &rel,
        CURRENT_SEQUENCE + 1,
        &far_future(),
    );
    let k = dir.join("kernel");
    let chk = g.ok(&["update", "--check", "--source", k.to_str().unwrap()]);
    assert_eq!(chk["human_gate_required"], false, "{chk}");
    let r = g.ok(&["update", "--apply", "--source", k.to_str().unwrap()]);
    assert_eq!(
        r["applied"], true,
        "the §5 restoration route no longer completes: {r}"
    );
    assert_eq!(
        r["details"]["protected_state"]["break_glass_exit"]["cleared"], true,
        "{}",
        r["details"]["protected_state"]
    );
    assert!(g.ok(&["trust", "status"])["degraded"].is_null());
    assert_eq!(
        yaml(&proj, "governance/framework.lock")["version"],
        gov_runtime::VERSION
    );
}
