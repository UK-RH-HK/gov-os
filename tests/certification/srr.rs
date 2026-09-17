//! Signed Release Root v1 (`ARCH-0003`) — builder regression evidence.
//!
//! Black-box through the `gov` JSON contract, like the rest of this harness. These are the builder's own tests;
//! the independent R1 verifier authors its own held-out evidence separately.
use crate::common::*;
use crate::srr_material::*;
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

/// A self-contained release directory: `<dir>/kernel` is a complete payload, `<dir>/metadata` holds signed metadata.
fn make_release(dir: &Path) -> PathBuf {
    std::fs::create_dir_all(dir).unwrap();
    gov_runtime::kernel::stage_payload(&canonical_root().join("framework"), &dir.join("kernel"))
        .unwrap();
    dir.join("kernel")
}

fn project(tag: &str) -> (PathBuf, PathBuf, Gov) {
    let root = tmp(tag);
    let proj = root.join("project");
    std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# srr project\n");
    git_init_commit(&proj);
    let g = Gov::new(&proj, &format!("S-{tag}"));
    (root, proj, g)
}

/// Provision the machine's trust anchor from the administrator domain (outside the project).
fn provision(root: &Path, g: &Gov, pubr: &Publisher, version: u64, expires: &str) -> Value {
    let admin = root.join("admin-domain");
    let rf = pubr.write_root(&admin, version, expires);
    g.ok(&["trust", "provision", "--anchor", rf.to_str().unwrap()])
}

fn machine_id(g: &Gov) -> String {
    g.ok(&["trust", "status"])["machine_id"]
        .as_str()
        .unwrap()
        .to_string()
}

/// Rewrite the `signed` member of an envelope in place, keeping the old signatures — the "modified metadata" attack.
fn tamper_signed(path: &Path, mutate: impl FnOnce(&mut Value)) {
    let v: Value = serde_json::from_slice(&std::fs::read(path).unwrap()).unwrap();
    let mut signed = v["signed"].clone();
    mutate(&mut signed);
    let out = format!(
        "{{\"signed\":{},\"signatures\":{}}}",
        serde_json::to_string(&signed).unwrap(),
        serde_json::to_string(&v["signatures"]).unwrap()
    );
    std::fs::write(path, out).unwrap();
}

// ------------------------------------------------------------------ 1. the happy path and the identity bindings

#[test]
fn a_signed_release_is_verified_end_to_end_and_the_floors_advance() {
    let (root, proj, g) = project("srr-happy");
    let p = Publisher::new();
    let rel = root.join("rel");
    make_release(&rel);
    provision(&root, &g, &p, 1, &far_future());
    p.publish(&rel, 10, 100, "stable", &far_future(), "4.0.0", 50);

    let st = g.ok(&["trust", "status"]);
    assert_eq!(st["posture"], "PROVISIONED");
    assert_eq!(
        st["trust_anchor"]["roles"]["root"]["threshold"], 2,
        "ARCH-0003 §4: 2-of-3 offline root keys"
    );

    let r = g.ok(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "srr",
        "--alias",
        "fx-srr",
    ]);
    let auth = &r["release_authenticity"];
    assert_eq!(auth["authenticity"], "AUTHENTIC");
    assert_eq!(auth["currency"], "CURRENT");
    assert_eq!(auth["channel"], "stable");
    assert_eq!(auth["sequence"], 100);
    assert_eq!(auth["below_floor"], false);

    // the installed bytes are the verified bytes
    let installed = json(&proj, "governance/kernel/KERNEL_MANIFEST.json");
    assert_eq!(installed["payload_hash"], auth["payload_hash"]);

    // the protected floors advanced, and they live outside the repository
    let st = g.ok(&["trust", "status"]);
    assert_eq!(st["floors"]["release_high_water"]["sequence"], 100);
    assert_eq!(st["floors"]["minimum_secure"]["sequence"], 50);
    assert_eq!(st["installed_release"]["authenticity"], "AUTHENTIC");
    let sr = st["state_root"].as_str().unwrap();
    assert!(
        !sr.starts_with(proj.to_str().unwrap()),
        "protected state must not live inside the project: {sr}"
    );
}

#[test]
fn an_unsigned_source_is_refused_once_a_trust_anchor_exists() {
    let (root, _proj, g) = project("srr-unsigned");
    let p = Publisher::new();
    let rel = root.join("rel");
    make_release(&rel); // no metadata published
    provision(&root, &g, &p, 1, &far_future());
    let e = g.err(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    assert_eq!(e.error_code(), "SRR_RELEASE_UNVERIFIED");
}

#[test]
fn wrong_key_wrong_product_and_wrong_channel_all_fail_closed() {
    let (root, _proj, g) = project("srr-wrong");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());

    // (a) wrong key: signed by a key that holds no `release` delegation
    let rel = root.join("rel-a");
    make_release(&rel);
    let md = p.publish(&rel, 10, 100, "stable", &far_future(), "4.0.0", 50);
    let doc = release_doc(
        &rel.join("kernel"),
        10,
        100,
        "stable",
        &far_future(),
        "4.0.0",
        50,
    );
    let impostor = key(0x99);
    std::fs::write(md.join("release.json"), envelope(&doc, &[&impostor])).unwrap();
    let e = g.err(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    assert_eq!(e.error_code(), "SRR_THRESHOLD_NOT_MET");

    // (b) wrong product
    let rel = root.join("rel-b");
    make_release(&rel);
    let md = p.publish(&rel, 10, 100, "stable", &far_future(), "4.0.0", 50);
    let mut doc = release_doc(
        &rel.join("kernel"),
        10,
        100,
        "stable",
        &far_future(),
        "4.0.0",
        50,
    );
    doc["product"] = json!("some-other-product");
    // Re-sign the whole chain so the snapshot/timestamp bindings are consistent and the product check is what runs.
    p.reseal(&md, &doc, 10, &far_future());
    let e = g.err(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    assert_eq!(e.error_code(), "SRR_WRONG_PRODUCT");

    // (c) wrong channel — SRR-R0-L2: the channel is a bound field, so a request for another channel fails closed
    let rel = root.join("rel-c");
    make_release(&rel);
    p.publish(&rel, 10, 100, "beta", &far_future(), "4.0.0", 50);
    let e = g.err(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--channel",
        "stable",
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    assert_eq!(e.error_code(), "SRR_WRONG_CHANNEL");
}

// ------------------------------------------------------------------ 2. tampering fails closed

#[test]
fn modified_metadata_payload_and_migration_all_fail_closed() {
    let (root, _proj, g) = project("srr-tamper");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());

    // (a) modified metadata: the signed member is rewritten, the signatures are kept
    let rel = root.join("rel-a");
    make_release(&rel);
    let md = p.publish(&rel, 10, 100, "stable", &far_future(), "4.0.0", 50);
    tamper_signed(&md.join("release.json"), |s| s["sequence"] = json!(9999));
    let e = g.err(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    assert_eq!(e.error_code(), "SRR_THRESHOLD_NOT_MET");

    // (b) a signature made over a *different* document must not admit this one
    let rel = root.join("rel-sig");
    make_release(&rel);
    let md = p.publish(&rel, 10, 100, "stable", &far_future(), "4.0.0", 50);
    let good = release_doc(
        &rel.join("kernel"),
        10,
        100,
        "stable",
        &far_future(),
        "4.0.0",
        50,
    );
    let mut evil = good.clone();
    evil["sequence"] = json!(1);
    std::fs::write(
        md.join("release.json"),
        envelope_with_foreign_signature(&evil, &good, &[&p.release]),
    )
    .unwrap();
    let e = g.err(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    assert_eq!(e.error_code(), "SRR_THRESHOLD_NOT_MET");

    // (c) modified payload after publication
    let rel = root.join("rel-b");
    make_release(&rel);
    p.publish(&rel, 10, 100, "stable", &far_future(), "4.0.0", 50);
    let victim = rel.join("kernel").join("KERNEL.yaml");
    let mut text = std::fs::read_to_string(&victim).unwrap();
    text.push_str("\n# injected\n");
    std::fs::write(&victim, text).unwrap();
    let e = g.err(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    assert_eq!(e.error_code(), "SRR_PAYLOAD_DIGEST_MISMATCH");

    // (d) an extra file that the metadata does not authorise
    let rel = root.join("rel-c");
    make_release(&rel);
    p.publish(&rel, 10, 100, "stable", &far_future(), "4.0.0", 50);
    std::fs::write(
        rel.join("kernel").join("policies").join("SMUGGLED.yaml"),
        "x: 1\n",
    )
    .unwrap();
    let e = g.err(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    assert_eq!(e.error_code(), "SRR_PAYLOAD_FILE_UNAUTHORISED");

    // (e) modified migration — the migration identities are bound by the release metadata
    let rel = root.join("rel-d");
    make_release(&rel);
    let migdir = rel.join("kernel").join("migrations");
    let mut migs: Vec<PathBuf> = std::fs::read_dir(&migdir)
        .unwrap()
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|x| x.extension().map(|e| e == "yaml").unwrap_or(false))
        .collect();
    migs.sort();
    assert!(
        !migs.is_empty(),
        "the kernel must ship migrations for this test to mean anything"
    );
    p.publish(&rel, 10, 100, "stable", &far_future(), "4.0.0", 50);
    let mut m = gov_runtime::util::read_yaml(&migs[0]).unwrap();
    m["description"] = json!("tampered migration description");
    gov_runtime::util::write_yaml(&migs[0], &m).unwrap();
    let e = g.err(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    // either the file digest or the migration identity catches it; both are fail-closed refusals
    assert!(
        ["SRR_PAYLOAD_DIGEST_MISMATCH", "SRR_MIGRATION_MODIFIED"]
            .contains(&e.error_code().as_str()),
        "unexpected code {}",
        e.error_code()
    );
}

#[test]
fn expired_metadata_fails_closed_against_the_declared_local_clock() {
    let (root, _proj, g) = project("srr-expiry");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());
    let rel = root.join("rel");
    make_release(&rel);
    p.publish(&rel, 10, 100, "stable", &past(), "4.0.0", 50);
    let e = g.err(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    assert_eq!(e.error_code(), "SRR_METADATA_EXPIRED");
}

#[test]
fn replaying_older_metadata_is_refused_by_the_protected_high_water() {
    let (root, proj, g) = project("srr-replay");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());
    let rel = root.join("rel");
    make_release(&rel);
    p.publish(&rel, 20, 100, "stable", &far_future(), "4.0.0", 50);
    g.ok(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    assert_eq!(
        g.ok(&["trust", "status"])["floors"]["metadata_high_water"]["release"],
        20
    );

    // republish the same release with an older metadata version: replay must be refused
    p.publish(&rel, 5, 100, "stable", &far_future(), "4.0.0", 50);
    let e = g.err(&[
        "kernel",
        "reinstall",
        "--source",
        rel.join("kernel").to_str().unwrap(),
    ]);
    assert_eq!(e.error_code(), "SRR_METADATA_ROLLBACK");
    assert!(
        exists(&proj, "governance/kernel/KERNEL.yaml"),
        "the refusal must not disturb the installation"
    );
}

// ------------------------------------------------------------------ 3. floors bind every ingress; break-glass

#[test]
fn the_floor_binds_every_ingress_and_only_owner_signed_break_glass_admits_a_below_floor_release() {
    let (root, proj, g) = project("srr-floor");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());

    // install a release at sequence 100
    let hi = root.join("rel-hi");
    make_release(&hi);
    p.publish(&hi, 20, 100, "stable", &far_future(), "4.0.0", 50);
    g.ok(&[
        "init",
        "--source",
        hi.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);

    // a signed but OLDER release (sequence 60) is below the protected high-water
    let lo = root.join("rel-lo");
    make_release(&lo);
    p.publish(&lo, 21, 60, "stable", &far_future(), "4.0.0", 50);

    // the floor refuses it at `reinstall`, not only at `rollback` (OWNER-DECISION-0006 §9)
    let e = g.err(&[
        "kernel",
        "reinstall",
        "--source",
        lo.join("kernel").to_str().unwrap(),
    ]);
    assert_eq!(e.error_code(), "SRR_BELOW_FLOOR");
    assert_eq!(e.details()["ingress"], "reinstall");
    assert_eq!(e.details()["effective_floor_sequence"], 100);

    // requesting break-glass without an owner authorisation is still refused: a CLI flag is not authority
    let e = g.err(&[
        "kernel",
        "reinstall",
        "--source",
        lo.join("kernel").to_str().unwrap(),
        "--break-glass",
    ]);
    assert_eq!(e.error_code(), "SRR_BREAK_GLASS_NOT_AUTHORISED");

    // the owner drops a signed authorisation into the protected inbox, out of band
    let bg = g.ok(&["trust", "break-glass"]);
    let inbox = PathBuf::from(bg["inbox"].as_str().unwrap());
    assert_eq!(bg["requirements"]["network_required"], false);
    let (_, payload_hash, kmh, ver) = measure(&lo.join("kernel"));
    let tok = break_glass_doc(
        &machine_id(&g),
        "nonce-1",
        "restore after a bad release",
        &far_future(),
        &ver,
        &payload_hash,
        &kmh,
    );
    std::fs::write(inbox.join("auth.json"), envelope(&tok, &[&p.recovery])).unwrap();

    // now the below-floor release is admitted, and the machine is marked
    let r = g.ok(&[
        "kernel",
        "reinstall",
        "--source",
        lo.join("kernel").to_str().unwrap(),
        "--break-glass",
    ]);
    assert_eq!(r["release_authenticity"]["below_floor"], true);
    let st = g.ok(&["trust", "status"]);
    assert_eq!(st["degraded"]["marking"], "DEGRADED — RECOVERY ONLY");
    assert_eq!(
        st["degraded"]["marking"].as_str().unwrap().as_bytes(),
        "DEGRADED \u{2014} RECOVERY ONLY".as_bytes()
    );

    // §8: the floors were NOT lowered by break-glass
    assert_eq!(st["floors"]["release_high_water"]["sequence"], 100);
    assert_eq!(st["floors"]["minimum_secure"]["sequence"], 50);

    // §6: refused while below floor — normal privileged operation and Human Gate creation
    for args in [
        vec![
            "task",
            "create",
            "--class",
            "documentation",
            "--objective",
            "o",
            "--status",
            "READY",
        ],
        vec!["gate", "create", "--question", "q"],
    ] {
        let e = g.err(&args);
        assert_eq!(
            e.error_code(),
            "SRR_BELOW_FLOOR_REFUSED",
            "{args:?} must be refused while below floor"
        );
        assert_eq!(e.details()["marking"], "DEGRADED — RECOVERY ONLY");
    }

    // §5: permitted while below floor — inspection and diagnosis keep working
    assert!(g.run(&["trust", "status"]).ok());
    assert!(!g.run(&["doctor"]).stdout.is_empty());
    let rec = g.ok(&["recover", "--dry-run"]);
    assert_eq!(rec["release_trust"]["below_floor"], true);

    // the authorisation is single use: the spent nonce cannot be replayed
    std::fs::write(inbox.join("auth.json"), envelope(&tok, &[&p.recovery])).unwrap();
    let e = g.err(&[
        "kernel",
        "reinstall",
        "--source",
        lo.join("kernel").to_str().unwrap(),
        "--break-glass",
    ]);
    assert_eq!(e.error_code(), "SRR_BREAK_GLASS_NOT_AUTHORISED");
    let _ = std::fs::remove_file(inbox.join("auth.json"));

    // §7 exit: restoring a release at or above BOTH floors clears the marking (SRR2-R1-C1, policy (b)).
    // The publisher re-issues current metadata for the good release: the metadata high-water advanced to 21 while
    // below floor, and replaying version 20 is (correctly) still refused.
    p.publish(&hi, 30, 100, "stable", &far_future(), "4.0.0", 50);
    let r = g.ok(&[
        "kernel",
        "reinstall",
        "--source",
        hi.join("kernel").to_str().unwrap(),
    ]);
    assert_eq!(r["protected_state"]["break_glass_exit"]["cleared"], true);
    let st = g.ok(&["trust", "status"]);
    assert!(
        st["degraded"].is_null(),
        "the marking must be cleared: {}",
        st["degraded"]
    );
    assert!(exists(&proj, "governance/kernel/KERNEL.yaml"));
}

#[test]
fn break_glass_never_admits_an_inauthentic_release_and_needs_no_network() {
    let (root, _proj, g) = project("srr-bg-authentic");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());
    let hi = root.join("rel-hi");
    make_release(&hi);
    p.publish(&hi, 20, 100, "stable", &far_future(), "4.0.0", 50);
    g.ok(&[
        "init",
        "--source",
        hi.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);

    // an UNSIGNED payload this machine has never verified, with a valid owner break-glass authorisation naming
    // its digests. Its bytes differ from the installed release, so the protected installed record cannot vouch.
    let lo = root.join("rel-lo");
    make_release(&lo);
    std::fs::write(
        lo.join("kernel").join("policies").join("UNVERIFIED.yaml"),
        "injected: true\n",
    )
    .unwrap();
    let bg = g.ok(&["trust", "break-glass"]);
    let inbox = PathBuf::from(bg["inbox"].as_str().unwrap());
    let (_, payload_hash, kmh, ver) = measure(&lo.join("kernel"));
    let tok = break_glass_doc(
        &machine_id(&g),
        "n2",
        "r",
        &far_future(),
        &ver,
        &payload_hash,
        &kmh,
    );
    std::fs::write(inbox.join("auth.json"), envelope(&tok, &[&p.recovery])).unwrap();
    // OWNER-DECISION-0006 §1: break-glass relaxes the floor check only. Unsigned code is still refused.
    let e = g.err(&[
        "kernel",
        "reinstall",
        "--source",
        lo.join("kernel").to_str().unwrap(),
        "--break-glass",
    ]);
    assert_eq!(e.error_code(), "SRR_RELEASE_UNVERIFIED");

    // a token signed by a key that holds no `recovery` delegation is not authority either
    let lo2 = root.join("rel-lo2");
    make_release(&lo2);
    p.publish(&lo2, 21, 60, "stable", &far_future(), "4.0.0", 50);
    let impostor = key(0x77);
    let (_, ph2, kmh2, v2) = measure(&lo2.join("kernel"));
    let tok2 = break_glass_doc(&machine_id(&g), "n3", "r", &far_future(), &v2, &ph2, &kmh2);
    std::fs::write(inbox.join("auth.json"), envelope(&tok2, &[&impostor])).unwrap();
    let e = g.err(&[
        "kernel",
        "reinstall",
        "--source",
        lo2.join("kernel").to_str().unwrap(),
        "--break-glass",
    ]);
    assert_eq!(e.error_code(), "SRR_BREAK_GLASS_NOT_AUTHORISED");

    // SRR2-R1-C2: a valid token that binds DIFFERENT payload digests does not authorise these bytes
    let tok3 = break_glass_doc(
        &machine_id(&g),
        "n4",
        "r",
        &far_future(),
        &v2,
        &"0".repeat(64),
        &"1".repeat(64),
    );
    std::fs::write(inbox.join("auth.json"), envelope(&tok3, &[&p.recovery])).unwrap();
    let e = g.err(&[
        "kernel",
        "reinstall",
        "--source",
        lo2.join("kernel").to_str().unwrap(),
        "--break-glass",
    ]);
    assert_eq!(e.error_code(), "SRR_BREAK_GLASS_WRONG_PAYLOAD");

    // a token bound to a different machine is refused
    let tok4 = break_glass_doc(
        "not-this-machine",
        "n5",
        "r",
        &far_future(),
        &v2,
        &ph2,
        &kmh2,
    );
    std::fs::write(inbox.join("auth.json"), envelope(&tok4, &[&p.recovery])).unwrap();
    let e = g.err(&[
        "kernel",
        "reinstall",
        "--source",
        lo2.join("kernel").to_str().unwrap(),
        "--break-glass",
    ]);
    assert_eq!(e.error_code(), "SRR_BREAK_GLASS_NOT_AUTHORISED");
}

// ------------------------------------------------------------------ 4. inputs that must never create authority

#[test]
fn environment_repository_and_caller_inputs_cannot_create_trust_or_approval() {
    let (root, proj, g) = project("srr-inputs");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());
    let rel = root.join("rel");
    make_release(&rel);
    p.publish(&rel, 10, 100, "stable", &far_future(), "4.0.0", 50);
    g.ok(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);

    // (a) authority-bearing environment variables are refused outright
    for v in [
        "GOV_BREAK_GLASS",
        "GOV_SKIP_VERIFY",
        "GOV_ALLOW_UNSIGNED",
        "GOV_FLOOR_OVERRIDE",
        "GOV_MINIMUM_SECURE_RELEASE",
    ] {
        let e = g.with_env(v, "1").err(&["kernel", "reinstall"]);
        assert_eq!(
            e.error_code(),
            "SRR_ENV_CANNOT_CREATE_AUTHORITY",
            "{v} must be refused"
        );
    }

    // (b) an env var cannot relocate a provisioned machine onto attacker-chosen floors
    let elsewhere = root.join("attacker-state");
    std::fs::create_dir_all(&elsewhere).unwrap();
    // The attacker puts their own trust anchor in a directory they control and points the override at it.
    std::fs::write(elsewhere.join("root.json"), p.root_json(1, &far_future())).unwrap();
    std::fs::create_dir_all(elsewhere.join("trust")).unwrap();
    std::fs::write(
        elsewhere.join("trust").join("provisioned.json"),
        "{\"provisioned\": true}",
    )
    .unwrap();
    let out = g
        .with_env("GOV_MACHINE_STATE_DIR", elsewhere.to_str().unwrap())
        .run(&["trust", "status"]);
    assert!(
        !out.ok(),
        "the override must be refused on a provisioned machine: {}",
        out.envelope
    );
    assert_eq!(out.error_code(), "SRR_PROTECTED_STATE_OVERRIDE_REFUSED");
    // and it cannot be used to slip a below-floor release past the floors either
    let e = g
        .with_env("GOV_MACHINE_STATE_DIR", elsewhere.to_str().unwrap())
        .err(&["kernel", "reinstall"]);
    assert_eq!(e.error_code(), "SRR_PROTECTED_STATE_OVERRIDE_REFUSED");

    // (c) a trust anchor may not be taken from inside the governed repository
    let inside = proj.join("governance").join("root.json");
    std::fs::write(&inside, p.root_json(1, &far_future())).unwrap();
    let e = g.err(&["trust", "provision", "--anchor", inside.to_str().unwrap()]);
    assert!(
        [
            "SRR_ANCHOR_FROM_REPOSITORY_REFUSED",
            "SRR_ALREADY_PROVISIONED"
        ]
        .contains(&e.error_code().as_str()),
        "unexpected {}",
        e.error_code()
    );

    // (d) rewriting framework.lock cannot change the release identity the machine believes it verified
    let mut lock = yaml(&proj, "governance/framework.lock");
    lock["release_hash"] = json!("0".repeat(64));
    lock["version"] = json!("9.9.9");
    write_yaml(&proj, "governance/framework.lock", &lock);
    let st = g.ok(&["trust", "status"]);
    assert_eq!(st["installed_release"]["release_version"], "4.1.5");
    assert_ne!(
        st["installed_release"]["payload_hash"],
        json!("0".repeat(64))
    );
}

// ------------------------------------------------------------------ 5. root succession (SRR-R0-L1)

#[test]
fn root_succession_requires_both_quorums_no_gaps_and_revokes_by_omission() {
    let (root, _proj, g) = project("srr-succession");
    let p = Publisher::new();
    let admin = root.join("admin-domain");
    provision(&root, &g, &p, 1, &far_future());

    // (a) a version gap is refused: an intermediate root's revocations must not be skipped
    let v3 = p.write_root(&admin, 3, &far_future());
    let e = g.err(&["trust", "root-update", "--anchor", v3.to_str().unwrap()]);
    assert_eq!(e.error_code(), "SRR_ROOT_VERSION_NOT_SUCCESSOR");

    // (b) a successor not signed by the OUTGOING quorum is refused
    let n1 = key(0xA1);
    let n2 = key(0xA2);
    let doc = root_doc(
        2,
        &far_future(),
        &[&n1, &n2],
        2,
        &[&p.release],
        &p.snapshot,
        &p.timestamp,
        Some(&p.recovery),
    );
    let bad = admin.join("root-2-selfonly.json");
    std::fs::write(&bad, envelope(&doc, &[&n1, &n2])).unwrap();
    let e = g.err(&["trust", "root-update", "--anchor", bad.to_str().unwrap()]);
    assert_eq!(e.error_code(), "SRR_ROOT_SUCCESSION_UNAUTHORISED");

    // (c) a successor not self-signed by the INCOMING quorum is refused
    let bad2 = admin.join("root-2-outgoingonly.json");
    std::fs::write(&bad2, envelope(&doc, &[&p.root_a, &p.root_b])).unwrap();
    let e = g.err(&["trust", "root-update", "--anchor", bad2.to_str().unwrap()]);
    assert_eq!(e.error_code(), "SRR_ROOT_SUCCESSION_UNAUTHORISED");

    // (d) both quorums: accepted, and the dropped keys are revoked by omission
    let good = admin.join("root-2.json");
    std::fs::write(&good, envelope(&doc, &[&p.root_a, &p.root_b, &n1, &n2])).unwrap();
    let r = g.ok(&["trust", "root-update", "--anchor", good.to_str().unwrap()]);
    assert_eq!(r["to_version"], 2);
    let revoked = r["revoked_keyids"].as_array().unwrap();
    assert!(
        revoked.contains(&json!(p.root_c.keyid)),
        "keys absent from the successor are revoked: {revoked:?}"
    );

    // (e) the same version cannot be replayed
    let e = g.err(&["trust", "root-update", "--anchor", good.to_str().unwrap()]);
    assert_eq!(e.error_code(), "SRR_ROOT_VERSION_NOT_SUCCESSOR");
}

// ------------------------------------------------------------------ 6. SRR2-R1-C3 and D-0007 separation

#[test]
fn protected_floors_survive_uninstall_and_project_removal() {
    let (root, proj, g) = project("srr-c3");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());
    let rel = root.join("rel");
    make_release(&rel);
    p.publish(&rel, 20, 100, "stable", &far_future(), "4.0.0", 50);
    g.ok(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    let before = g.ok(&["trust", "status"])["floors"].clone();
    assert_eq!(before["release_high_water"]["sequence"], 100);

    // uninstall: remove governance/ entirely
    std::fs::remove_dir_all(proj.join("governance")).unwrap();
    assert_eq!(
        g.ok(&["trust", "status"])["floors"],
        before,
        "floors must survive uninstall"
    );

    // project removal: delete the whole repository
    std::fs::remove_dir_all(&proj).unwrap();
    std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# re-created\n");
    git_init_commit(&proj);
    let after = g.ok(&["trust", "status"])["floors"].clone();
    assert_eq!(
        after, before,
        "floors must survive project removal (SRR2-R1-C3)"
    );

    // and they are still enforced: an older signed release is refused into the fresh project
    let lo = root.join("rel-lo");
    make_release(&lo);
    p.publish(&lo, 21, 60, "stable", &far_future(), "4.0.0", 50);
    let e = g.err(&[
        "init",
        "--source",
        lo.join("kernel").to_str().unwrap(),
        "--name",
        "y",
        "--alias",
        "fx-y",
    ]);
    assert_eq!(e.error_code(), "SRR_BELOW_FLOOR");
}

#[test]
fn installed_integrity_authenticity_and_admissibility_stay_three_separate_predicates() {
    let (root, proj, g) = project("srr-d0007");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());
    let rel = root.join("rel");
    make_release(&rel);
    p.publish(&rel, 20, 100, "stable", &far_future(), "4.0.0", 50);
    g.ok(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);

    let st = g.ok(&["trust", "status"]);
    assert!(st["separation"]["intact"]
        .as_str()
        .unwrap()
        .contains("D-0007"));
    assert_eq!(g.ok(&["kernel", "trust"])["verified"], true);

    // Tamper the INSTALLED payload. D-0007 must detect it; the release-authenticity record must not be touched by
    // it, and must not be used to excuse it.
    let victim = proj.join("governance/kernel/policies");
    let f = std::fs::read_dir(&victim)
        .unwrap()
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .find(|x| x.extension().map(|e| e == "yaml").unwrap_or(false))
        .unwrap();
    let mut t = std::fs::read_to_string(&f).unwrap();
    t.push_str("\n# local tamper\n");
    std::fs::write(&f, t).unwrap();

    let kt = g.ok(&["kernel", "trust"]);
    assert_eq!(
        kt["verified"], false,
        "D-0007 must still detect installed-payload tampering"
    );
    // the machine's protected record still says what it VERIFIED, which is a different predicate
    let st = g.ok(&["trust", "status"]);
    assert_eq!(st["installed_release"]["authenticity"], "AUTHENTIC");
    // and a mutating governed operation is still refused by D-0007, unchanged by anything in this module
    let e = g.err(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "o",
        "--status",
        "READY",
    ]);
    assert_eq!(e.error_code(), "KERNEL_TAMPERED");
}

// ------------------------------------------------------------------ 7. crash-safety of the transaction

#[test]
fn an_interrupted_install_leaves_one_complete_version_and_never_advances_a_floor() {
    let (root, proj, g) = project("srr-crash");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());
    let rel = root.join("rel");
    make_release(&rel);
    p.publish(&rel, 20, 100, "stable", &far_future(), "4.0.0", 50);
    g.ok(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);
    let good_hash = json(&proj, "governance/kernel/KERNEL_MANIFEST.json")["payload_hash"].clone();
    let floors_before = g.ok(&["trust", "status"])["floors"].clone();

    // Simulate a crash inside the two-rename window: the destination is gone and `<dest>.srr-new` is complete.
    let ms = machine_state_dir(&proj);
    let kernel = proj.join("governance").join("kernel");
    let newp = proj.join("governance").join("kernel.srr-new");
    std::fs::rename(&kernel, &newp).unwrap();
    gov_runtime::util::write_json(
        &ms.join("journal").join("crashed.json"),
        &json!({"id": "crashed", "phase": "swap", "dest": kernel.to_str().unwrap(),
                "new_path": newp.to_str().unwrap(),
                "old_path": proj.join("governance").join("kernel.srr-old").to_str().unwrap()}),
    )
    .unwrap();
    assert!(!kernel.exists());

    // Recovery completes the interrupted swap to one complete valid version.
    let r = g.ok(&["trust", "recover-transactions"]);
    assert_eq!(r["replayed"][0]["action"], "completed_interrupted_swap");
    assert_eq!(
        r["replayed"][0]["floors_advanced"], false,
        "a replay must never advance a protected floor"
    );
    assert!(kernel.join("KERNEL.yaml").exists());
    assert!(!newp.exists());
    assert_eq!(
        json(&proj, "governance/kernel/KERNEL_MANIFEST.json")["payload_hash"],
        good_hash
    );
    assert_eq!(g.ok(&["trust", "status"])["floors"], floors_before);
    assert_eq!(g.ok(&["kernel", "trust"])["verified"], true);
}

// ------------------------------------------------------------------ 8. Capability Contract v3 hash binding

#[test]
fn the_capability_contract_source_chain_is_hash_bound_and_fails_closed() {
    // The canonical import must be byte-identical to the owner's approved source, and the compiled representation
    // must be a fresh compilation of it. Any divergence is a hard failure, not a warning.
    let canonical = canonical_root();
    let g = Gov::new(&canonical, "S-contract");
    let r = g.ok(&["contract", "verify"]);
    assert_eq!(r["verdict"], "CONTRACT_SOURCE_BOUND");
    assert_eq!(
        r["owner_source_sha256"],
        "4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3"
    );
    assert_eq!(r["canonical_import_byte_identical"], true);
    assert!(r["capability_count"].as_u64().unwrap() > 50);

    // Divergence is detected: copy the tree, edit one byte of the import, and verify must refuse.
    let scratch = tmp("contract-diverge");
    for f in [
        "framework",
        "Governance_OS_Capability_Acceptance_Contract_v3.md",
        "tests",
    ] {
        let src = canonical.join(f);
        let dst = scratch.join(f);
        if src.is_dir() {
            copy_dir(&src, &dst);
        } else {
            std::fs::copy(&src, &dst).unwrap();
        }
    }
    let import =
        scratch.join("framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md");
    let mut text = std::fs::read_to_string(&import).unwrap();
    text.push_str("\nan unauthorised addition\n");
    std::fs::write(&import, text).unwrap();
    let e = Gov::new(&scratch, "S-contract2").err(&["contract", "verify"]);
    assert_eq!(e.error_code(), "CONTRACT_SOURCE_DIVERGED");

    // A hand-edited compiled representation is refused too.
    let scratch2 = tmp("contract-compiled");
    for f in [
        "framework",
        "Governance_OS_Capability_Acceptance_Contract_v3.md",
        "tests",
    ] {
        let src = canonical.join(f);
        let dst = scratch2.join(f);
        if src.is_dir() {
            copy_dir(&src, &dst);
        } else {
            std::fs::copy(&src, &dst).unwrap();
        }
    }
    let compiled = scratch2.join("framework/contracts/governance-capability-acceptance.yaml");
    let mut c = gov_runtime::util::read_yaml(&compiled).unwrap();
    c["capabilities"][0]["requirement_class"] = json!("EXECUTION_REFINEMENT");
    gov_runtime::util::write_yaml(&compiled, &c).unwrap();
    let e = Gov::new(&scratch2, "S-contract3").err(&["contract", "verify"]);
    assert_eq!(e.error_code(), "CONTRACT_COMPILED_DIVERGED");
}

// ------------------------------------------------------------------ 9. SRR-R0-L6 acquisition classes

#[test]
fn a_privileged_capability_acquired_from_outside_needs_a_delegated_signed_target() {
    let (root, proj, g) = project("srr-l6");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());
    let rel = root.join("rel");
    make_release(&rel);
    p.publish(&rel, 10, 100, "stable", &far_future(), "4.0.0", 50);
    g.ok(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);

    // A plugin whose implementation lives inside the governed project is LOCAL_PROJECT: the existing kernel-owned
    // controls govern it and no delegation is required.
    let bin = proj.join("tools").join("local-plugin.sh");
    std::fs::create_dir_all(bin.parent().unwrap()).unwrap();
    std::fs::write(&bin, "#!/bin/sh\necho '{}'\n").unwrap();
    write(&proj, "governance/project/plugins/local-scanner.yaml",
        "plugin_id: local-scanner\ncapability: code_intel\ncommand: [\"tools/local-plugin.sh\"]\nversion: \"1\"\nlanguages: [\"python\"]\napproved_roles: [\"all\"]\n");
    let lf = proj.join("governance/project/plugins/local-scanner.yaml");
    let l4 = g.with_role("tooling-engineer");
    let r = l4.ok(&["plugins", "register", "--descriptor", lf.to_str().unwrap()]);
    assert_eq!(r["acquisition"]["acquisition_class"], "LOCAL_PROJECT");
    assert_eq!(r["acquisition"]["privileged"], false);

    // A PRIVILEGED plugin whose implementation resolves nowhere on this machine is REMOTELY_ACQUIRED, and with no
    // delegated signed target in the verified release metadata it is refused (SRR-R0-L6).
    write(&proj, "governance/project/plugins/acme-remote.yaml",
        "plugin_id: acme-remote\ncapability: secret_scan\ncommand: [\"/bin/sh\"]\nversion: \"1\"\nlanguages: [\"python\"]\napproved_roles: [\"all\"]\nrequired_permission_classes: [\"SYSTEM_INSTALL\"]\n");
    let rf = proj.join("governance/project/plugins/acme-remote.yaml");
    let e = l4.err(&["plugins", "register", "--descriptor", rf.to_str().unwrap()]);
    assert_eq!(
        e.error_code(), "SRR_PLUGIN_NOT_DELEGATED",
        "a privileged remotely-acquired capability must be refused without a delegated signed target"
    );
    assert_eq!(e.details()["acquisition_class"], "REMOTELY_ACQUIRED");
}

/// `AR27-B1` — while a machine is marked `DEGRADED — RECOVERY ONLY`, refusal is the **structural default**.
///
/// `OWNER-DECISION-0006` §6 bullet 1 names a class — "normal privileged Governance OS operation" — and a class
/// cannot be enforced by a list of operation names: whatever nobody listed proceeds. This test enters genuine
/// break-glass and then checks the *whole* refusal surface rather than a sample. Every operation label the product
/// passes to `guard_write`, plus labels that do not exist at all, must be refused unless a §5 activity covers it.
#[test]
fn below_floor_refusal_is_default_refuse_across_the_whole_operation_surface() {
    let (root, proj, g) = project("srr-belowfloor-class");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());

    let hi = root.join("rel-hi");
    make_release(&hi);
    p.publish(&hi, 20, 100, "stable", &far_future(), "4.0.0", 50);
    g.ok(&[
        "init",
        "--source",
        hi.join("kernel").to_str().unwrap(),
        "--name",
        "x",
        "--alias",
        "fx-x",
    ]);

    let lo = root.join("rel-lo");
    make_release(&lo);
    p.publish(&lo, 21, 60, "stable", &far_future(), "4.0.0", 50);

    // Genuine break-glass entry: an owner-signed authorisation, out of band, through the real `admit` path.
    let bg = g.ok(&["trust", "break-glass"]);
    let inbox = PathBuf::from(bg["inbox"].as_str().unwrap());
    let (_, payload_hash, kmh, ver) = measure(&lo.join("kernel"));
    let tok = break_glass_doc(
        &machine_id(&g),
        "nonce-class-1",
        "restore after a bad release",
        &far_future(),
        &ver,
        &payload_hash,
        &kmh,
    );
    std::fs::write(inbox.join("auth.json"), envelope(&tok, &[&p.recovery])).unwrap();
    let r = g.ok(&[
        "kernel",
        "reinstall",
        "--source",
        lo.join("kernel").to_str().unwrap(),
        "--break-glass",
    ]);
    assert_eq!(r["release_authenticity"]["below_floor"], true);

    let ms = gov_runtime::srr::state::MachineState::at(&machine_state_dir(&proj))
        .expect("the simulated machine's protected state");
    assert!(gov_runtime::srr::breakglass::is_degraded(
        &ms,
        gov_runtime::FRAMEWORK_NAME
    ));

    // Every operation label the product passes to a below-floor guard, plus labels that do not exist.
    let labels = [
        "upstream submit",
        "upstream export",
        "memory select",
        "checkpoint",
        "gate create",
        "gate answer",
        "gate revoke",
        "gate present",
        "decide",
        "update --apply",
        "update --rollback",
        "tools install",
        "replan",
        "plugins register",
        "plugins unregister",
        "handoff create",
        "handoff return",
        "readiness plan",
        "cit propose",
        "cit simulate",
        "cit approve",
        "cit reject",
        "cit execute",
        "adopt migrate",
        "adopt extract-legacy",
        "adopt build-memory",
        "task create",
        "task status",
        "task claim",
        "task close",
        "kernel reinstall",
        "release build",
        "release certify",
        "trust provision",
        "trust root-update",
        "skills install",
        // labels that did not exist when the guard was written: the class test
        "an operation invented after this repair",
        "quorum override",
        "cit approve --force",
        "KERNEL REINSTALL",
    ];
    let mut permitted: Vec<&str> = vec![];
    let mut refused: Vec<&str> = vec![];
    for l in labels {
        match gov_runtime::srr::breakglass::guard(&ms, gov_runtime::FRAMEWORK_NAME, l) {
            Ok(()) => permitted.push(l),
            Err(e) => {
                assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED", "'{l}' refused for the wrong reason");
                refused.push(l);
            }
        }
    }
    permitted.sort_unstable();
    assert_eq!(
        permitted,
        vec![
            "checkpoint",
            "kernel reinstall",
            "update --apply",
            "update --rollback"
        ],
        "only the OWNER-DECISION-0006 §5 recovery activities may proceed below floor; everything else is §6"
    );
    assert_eq!(refused.len(), labels.len() - 4);

    // The seven AR-0027 measured as permitted with no §5 cover are each refused now.
    for must in [
        "cit approve",
        "cit reject",
        "gate revoke",
        "handoff return",
        "plugins unregister",
        "adopt extract-legacy",
        "adopt build-memory",
    ] {
        assert!(refused.contains(&must), "§6 bullet 1 must refuse '{must}'");
    }
    // And every permitted label carries the §5 activity that justifies it.
    for l in &permitted {
        assert!(
            gov_runtime::srr::breakglass::permitted_activity(l).is_some(),
            "'{l}' proceeds below floor without naming a §5 activity"
        );
    }

    // The hot-path guard inside `guard_write` agrees, end to end through the real binary. `cit approve` is the
    // sharpest case: an approval-class decision on a change-intent transaction.
    for args in [
        vec!["cit", "approve", "CIT-0001"],
        vec!["cit", "reject", "CIT-0001"],
        vec!["gate", "revoke", "G-0001"],
    ] {
        let e = g.err(&args);
        assert_eq!(
            e.error_code(),
            "SRR_BELOW_FLOOR_REFUSED",
            "{args:?} must be refused while the machine is marked DEGRADED — RECOVERY ONLY"
        );
        assert_eq!(e.details()["marking"], "DEGRADED — RECOVERY ONLY");
        assert_eq!(e.details()["refusal_policy"], "allow_list_default_refuse");
    }

    // §5/§7/§10 are not collateral damage: inspection still works and the recovery exit still clears the marking.
    assert!(g.run(&["trust", "status"]).ok());
    p.publish(&hi, 30, 100, "stable", &far_future(), "4.0.0", 50);
    let r = g.ok(&[
        "kernel",
        "reinstall",
        "--source",
        hi.join("kernel").to_str().unwrap(),
    ]);
    assert_eq!(r["protected_state"]["break_glass_exit"]["cleared"], true);
    assert!(g.ok(&["trust", "status"])["degraded"].is_null());
}
