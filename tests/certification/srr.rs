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
    // the release this machine verified is the current framework payload (P2-AR-0039: its version follows
    // framework/KERNEL.yaml, 4.1.6, rather than a literal)
    assert_eq!(
        st["installed_release"]["release_version"],
        gov_runtime::VERSION
    );
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

// ------------------------------------------------ 11. OWNER-DECISION-0006 §6 coverage: is the guard on the path?

/// Read a product source file, by path relative to the repository root.
fn src(rel: &str) -> String {
    std::fs::read_to_string(canonical_root().join(rel))
        .unwrap_or_else(|e| panic!("read {rel}: {e}"))
}

/// Every `.rs` file the product ships (runtime + cli), as (path, text).
fn product_sources() -> Vec<(String, String)> {
    fn walk(dir: &Path, out: &mut Vec<(String, String)>) {
        let Ok(rd) = std::fs::read_dir(dir) else { return };
        for e in rd.filter_map(|e| e.ok()) {
            let p = e.path();
            if p.is_dir() {
                walk(&p, out);
            } else if p.extension().map(|x| x == "rs").unwrap_or(false) {
                out.push((
                    p.display().to_string(),
                    std::fs::read_to_string(&p).unwrap_or_default(),
                ));
            }
        }
    }
    let mut v = vec![];
    walk(&canonical_root().join("runtime/src"), &mut v);
    walk(&canonical_root().join("cli/src"), &mut v);
    v.sort();
    v
}

/// The body of `fn <name>` in `text`, from the signature to the first column-0 `}`.
fn fn_body<'a>(text: &'a str, name: &str) -> &'a str {
    let at = text
        .find(&format!("fn {name}("))
        .unwrap_or_else(|| panic!("fn {name}( not found — the §6 sink census must be re-derived"));
    let rest = &text[at..];
    let end = rest.find("\n}").unwrap_or(rest.len());
    &rest[..end]
}

/// **The `OWNER-DECISION-0006` §6 coverage test.**
///
/// `AR29-B1` and `AR29-B2` were not defects in a decision procedure — repair 1's allow-list decides correctly, and
/// AR-0029 confirmed it could not be broken. They were two operations that never reached a decision procedure at
/// all. A test that swept operation *labels* through the guard could not see that, and did not: AR-0027's `d3`
/// printed `trust root-update` in its REFUSED column while the operation succeeded.
///
/// So this test asks the prior question, in two halves, and would have failed on candidate 2 in both:
///
/// * **structurally** — for every §6 bullet, the single primitive that can realise it
///   ([`breakglass::SECTION_6_SINKS`]) carries the enforcement point *inside* it, the witness type is sealed, and
///   no second implementation of a §6 primitive exists anywhere in the tree. This is what fails when someone adds
///   a new way to raise a Human Gate or write a trust anchor.
/// * **dynamically** — every §6-named operation the product actually exposes is driven end to end, through the
///   real `gov` binary, on a machine in genuine owner-authorised break-glass, and must refuse. This is
///   `AR29-B1`'s and `AR29-B2`'s counterexamples, kept as regressions.
#[test]
fn section_6_effects_are_enforced_inside_their_sinks() {
    use gov_runtime::srr::breakglass as bg;

    // ---------------------------------------------------------------- A. the mechanism, read off the source

    // A1. Every §6 activity the decision names has a declared sink, and no sink names an activity §6 does not.
    assert_eq!(bg::SECTION_6_SINKS.len(), bg::REFUSED_ACTIVITIES.len());
    for (activity, _sink) in bg::SECTION_6_SINKS {
        assert!(
            bg::REFUSED_ACTIVITIES.contains(activity),
            "'{activity}' is not an OWNER-DECISION-0006 §6 activity"
        );
    }
    for a in bg::REFUSED_ACTIVITIES {
        assert!(
            bg::SECTION_6_SINKS.iter().any(|(x, _)| x == a),
            "§6 activity '{a}' has no declared enforcement sink"
        );
    }

    // A2. Each sink that names a function contains the enforcement call for its own effect, in its own body.
    let state_rs = src("runtime/src/srr/state.rs");
    let gates_rs = src("runtime/src/orchestration/gates.rs");
    let release_rs = src("runtime/src/release.rs");
    let plugins_rs = src("runtime/src/srr/plugins.rs");
    let control_rs = src("runtime/src/orchestration/control.rs");
    for (sink_body, needle, what) in [
        (
            fn_body(&state_rs, "set_root_metadata"),
            "Effect::TrustPolicyMutation",
            "§6 bullet 4 sink `MachineState::set_root_metadata`",
        ),
        (
            fn_body(&gates_rs, "answer"),
            "Effect::HumanGateApprove",
            "§6 bullet 2 (approval) sink `gates::answer`",
        ),
        (
            fn_body(&release_rs, "build"),
            "Effect::ReleaseCertification",
            "§6 bullet 3 sink `release::build`",
        ),
        (
            fn_body(&plugins_rs, "guard_acquisition"),
            "Effect::PrivilegedPluginAcquisition",
            "§6 bullet 5 sink `plugins::guard_acquisition`",
        ),
        (
            fn_body(&control_rs, "guard_write"),
            "breakglass::guard_light",
            "§6 bullet 1 chokepoint `control::guard_write`",
        ),
    ] {
        assert!(
            sink_body.contains(needle),
            "{what} no longer contains `{needle}`: the enforcement point has left the effect"
        );
    }

    // A3. The §6 bullet 2 (creation) sink is enforced by the TYPE SYSTEM, not by a call this test can only grep
    // for: `gates::build` takes a `&Clearance`, which has no constructor outside `breakglass`.
    assert!(
        gates_rs.contains("_clearance: &crate::srr::breakglass::Clearance"),
        "`gates::build` no longer requires a §6 clearance; a new gate-raising path would compile unguarded"
    );
    for wrapper in ["create", "create_system"] {
        assert!(
            fn_body(&gates_rs, wrapper).contains("Effect::HumanGateCreate"),
            "`gates::{wrapper}` no longer asks §6 before building a gate"
        );
    }

    // A4. The witness is sealed: private fields, one private constructor, and no construction site outside
    // `breakglass`. If any of this is relaxed, A3's compile-time guarantee silently becomes decorative.
    let bg_rs = src("runtime/src/srr/breakglass.rs");
    let clearance_struct = bg_rs
        .split("pub struct Clearance {")
        .nth(1)
        .expect("Clearance struct")
        .split("\n}")
        .next()
        .unwrap();
    assert!(
        !clearance_struct.contains("pub "),
        "`Clearance` gained a public field: a struct literal outside `breakglass` would then compile"
    );
    assert!(
        bg_rs.contains("    fn issue(effect: Effect, operation: &str) -> Clearance {"),
        "`Clearance::issue` is no longer the private sole constructor"
    );
    for deriv in ["Clone, Debug", "Debug, Clone", "Default"] {
        assert!(
            !bg_rs.contains(&format!("#[derive({deriv})]\npub struct Clearance")),
            "`Clearance` must not derive `{deriv}`"
        );
    }
    let outside: Vec<String> = product_sources()
        .into_iter()
        .filter(|(p, t)| !p.ends_with("srr/breakglass.rs") && t.contains("Clearance {"))
        .map(|(p, _)| p)
        .collect();
    assert!(
        outside.is_empty(),
        "a `Clearance` value is constructed outside `breakglass`: {outside:?}"
    );

    // A5. `AR29-N1` — the no-bypass claim is now a type property: `AuthenticatedRelease` holds a private seal, so
    // no struct literal outside `srr::verifier` compiles, and the seal has exactly one construction site.
    let verifier_rs = src("runtime/src/srr/verifier.rs");
    assert!(
        verifier_rs.contains("    admitted: sealed::Admitted,"),
        "`AuthenticatedRelease` lost its private seal; 'constructible only by admit' would be an enumeration again"
    );
    assert!(
        !verifier_rs.contains("pub admitted"),
        "the seal field must not be public"
    );
    let by_admit: usize = product_sources()
        .iter()
        .map(|(_, t)| t.matches("Admitted::by_admit()").count())
        .sum();
    assert_eq!(
        by_admit, 1,
        "the seal constructor must have exactly one call site (the tail of `admit_inner`)"
    );
    let literals: Vec<String> = product_sources()
        .into_iter()
        .flat_map(|(path, t)| {
            t.lines()
                .enumerate()
                .filter(|(_, l)| {
                    l.contains("AuthenticatedRelease {")
                        && !l.contains("struct ")
                        && !l.contains("impl ")
                })
                .map(|(n, l)| format!("{path}:{} {}", n + 1, l.trim()))
                .collect::<Vec<_>>()
        })
        .collect();
    assert_eq!(
        literals.len(),
        1,
        "`AuthenticatedRelease` is constructed in more than one place: {literals:?}"
    );

    // A6. **No second implementation of a §6 primitive.** This is the assertion that fails when a future change
    // adds a new way to perform a forbidden effect rather than a new caller of an existing one.
    let human_gate_records: Vec<String> = product_sources()
        .into_iter()
        .filter(|(_, t)| t.contains(r#"new_record("human-gate""#))
        .map(|(p, _)| p)
        .collect();
    assert_eq!(
        human_gate_records.len(),
        1,
        "a `human-gate` record is minted outside `gates::build`: {human_gate_records:?}"
    );
    assert!(human_gate_records[0].ends_with("orchestration/gates.rs"));

    let anchor_writers: Vec<String> = product_sources()
        .into_iter()
        .filter(|(_, t)| t.contains("root_metadata_path()"))
        .map(|(p, _)| p)
        .collect();
    assert_eq!(
        anchor_writers.len(),
        2,
        "the trust anchor path is reached from somewhere new: {anchor_writers:?} (expected `state.rs` to write \
         it and `verifier.rs` to read it)"
    );

    // §6 bullet 6 has no sink because it has no primitive: the only mutators of a floor are monotonic.
    let floors = state_rs
        .split("impl Floors {")
        .nth(1)
        .unwrap()
        .split("\n}")
        .next()
        .unwrap();
    let mutators: Vec<&str> = floors
        .match_indices("pub fn ")
        .map(|(i, _)| floors[i + 7..].split('(').next().unwrap())
        .filter(|n| {
            !matches!(
                *n,
                "load"
                    | "to_value"
                    | "save"
                    | "metadata_floor"
                    | "observed_only"
                    | "effective_floor_sequence"
                    | "effective_floor_version"
            )
        })
        .collect();
    assert_eq!(
        mutators,
        vec!["raise_metadata", "raise_release", "raise_minimum_secure"],
        "`Floors` gained a mutator that is not a monotonic raise: {mutators:?}"
    );

    // ---------------------------------------------------------------- B. the reachability half, measured

    let (root, proj, g) = project("srr-s6-coverage");
    let p = Publisher::new();
    let admin = root.join("admin-domain");
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

    // Genuine break-glass: an owner-signed authorisation, out of band, through the real `admit` path.
    let bg_status = g.ok(&["trust", "break-glass"]);
    let inbox = PathBuf::from(bg_status["inbox"].as_str().unwrap());
    let (_, payload_hash, kmh, ver) = measure(&lo.join("kernel"));
    let tok = break_glass_doc(
        &machine_id(&g),
        "nonce-s6-1",
        "restore after a bad release",
        &far_future(),
        &ver,
        &payload_hash,
        &kmh,
    );
    std::fs::write(inbox.join("auth.json"), envelope(&tok, &[&p.recovery])).unwrap();
    g.ok(&[
        "kernel",
        "reinstall",
        "--source",
        lo.join("kernel").to_str().unwrap(),
        "--break-glass",
    ]);
    let ms = gov_runtime::srr::state::MachineState::at(&machine_state_dir(&proj)).unwrap();
    assert!(bg::is_degraded(&ms, gov_runtime::FRAMEWORK_NAME));
    let anchor_before = g.ok(&["trust", "status"])["trust_anchor"]["version"].clone();
    let root_floor_before =
        gov_runtime::srr::state::Floors::load(&ms, gov_runtime::FRAMEWORK_NAME).metadata_floor("root");

    // B1 — §6 bullet 4. `AR29-B1`'s counterexample, verbatim: a successor root signed by BOTH quorums, i.e. a
    // succession that would be accepted on a healthy machine, offered to a machine marked DEGRADED.
    let n1 = key(0xB1);
    let n2 = key(0xB2);
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
    let successor = admin.join("root-2-s6.json");
    std::fs::write(
        &successor,
        envelope(&doc, &[&p.root_a, &p.root_b, &n1, &n2]),
    )
    .unwrap();
    let e = g.err(&["trust", "root-update", "--anchor", successor.to_str().unwrap()]);
    assert_eq!(
        e.error_code(),
        "SRR_BELOW_FLOOR_REFUSED",
        "§6 bullet 4: a trust-policy mutation must not complete below floor"
    );
    assert_eq!(e.details()["refused_class"], "trust_policy_mutation");
    assert_eq!(e.details()["section_6_bullet"], 4);
    // and nothing moved
    assert_eq!(
        g.ok(&["trust", "status"])["trust_anchor"]["version"],
        anchor_before
    );
    assert_eq!(
        gov_runtime::srr::state::Floors::load(&ms, gov_runtime::FRAMEWORK_NAME).metadata_floor("root"),
        root_floor_before
    );

    // B2 — the same bullet through the other door. A machine cannot carry the marking without already holding a
    // trust anchor, so `gov trust provision` is shut here by the already-provisioned latch — which is the
    // accurate diagnosis, and why the §6 guard on this path sits after that check rather than before it. What
    // matters for §6 is that the *effect* cannot happen, which B2b measures at the sink itself.
    let fresh = p.write_root(&admin, 1, &far_future());
    let e = g.err(&["trust", "provision", "--anchor", fresh.to_str().unwrap()]);
    assert_eq!(e.error_code(), "SRR_ALREADY_PROVISIONED");

    // B2b — the sink. Every trust anchor write in the product goes through `set_root_metadata`, including one
    // written by code that does not exist yet, and below floor it refuses.
    let anchor_bytes = std::fs::read(&fresh).unwrap();
    let e = ms
        .set_root_metadata(&anchor_bytes, 1, gov_runtime::FRAMEWORK_NAME)
        .unwrap_err();
    assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED");
    assert_eq!(e.details["refused_class"], "trust_policy_mutation");
    assert_eq!(e.details["section_6_bullet"], 4);

    // B3 — §6 bullet 2 (creation), through the operator surface.
    let e = g.err(&["gate", "create", "--question", "approve something?"]);
    assert_eq!(e.error_code(), "SRR_BELOW_FLOOR_REFUSED");
    assert_eq!(e.details()["refused_class"], "human_gate_create");

    // B4 — §6 bullet 2 reached from INSIDE an allow-listed §5 operation is measured separately, in
    // `an_allow_listed_operation_cannot_create_a_human_gate_below_floor`, because it needs a machine whose
    // installed version is genuinely behind the candidate. Structurally, here: the enforcement point sits between
    // the allow-list entry and the gate creation, which is precisely the span `AR29-B2` measured as empty.
    let update_rs = src("runtime/src/update.rs");
    let apply = update_rs.split("pub fn apply_update_opts").nth(1).unwrap();
    let head = &apply[..apply.find("let auth = crate::srr::admit").unwrap()];
    let marker = r#"guard_write(p, "update --apply")"#;
    let between =
        &head[head.find(marker).unwrap() + marker.len()..head.find("gates::create_system").unwrap()];
    assert!(
        between.contains("breakglass::guard_effect")
            && between.contains("Effect::HumanGateCreate"),
        "nothing enforces §6 between the allow-list entry and the gate creation in `update --apply`"
    );
    assert!(
        bg::permitted_activity("update --apply").is_some(),
        "the allow-list still permits the operation; what §6 forbids is the gate inside it"
    );

    // B5 — §6 bullet 2 (creation) reached from `gov kernel override`, the second caller `AR29-B2` named and the
    // one it could not drive end to end. The kernel is tampered first so the override is actually attempted.
    let victim = proj.join("governance/kernel/policies/AUTHORITY_POLICY.yaml");
    let original = std::fs::read(&victim).unwrap();
    std::fs::write(&victim, [&original[..], b"\n# tampered\n"].concat()).unwrap();
    let e = g.err(&["kernel", "override", "--reason", "coverage probe"]);
    assert_eq!(
        e.error_code(),
        "SRR_BELOW_FLOOR_REFUSED",
        "§6 bullet 2: `gov kernel override` must not raise a kernel-integrity gate below floor"
    );
    assert_eq!(e.details()["refused_class"], "human_gate_create");
    std::fs::write(&victim, &original).unwrap();

    // B6 — §6 bullet 3. `release::build` takes no `Project` and structurally cannot reach `control::guard_write`;
    // the effect-level point is the only thing standing between a degraded machine and a certified release.
    let e = g.err(&[
        "release",
        "build",
        "--version",
        "9.9.9",
        "--certification",
        "CERTIFIED",
        "--out",
        root.join("rel-out").to_str().unwrap(),
        "--canonical",
        canonical_root().to_str().unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "SRR_BELOW_FLOOR_REFUSED",
        "§6 bullet 3: release certification must not complete below floor"
    );
    assert_eq!(e.details()["refused_class"], "release_certification");
    assert!(
        !root.join("rel-out/releases/9.9.9").exists(),
        "the refusal must happen before anything is written"
    );

    // B7 — §5, §7 and §10 are not collateral damage: the gate-free restoration route still works, still needs no
    // network, and still clears the marking.
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

    // B8 — and once the machine is out of break-glass, every one of them is available again. A guard that never
    // lifts is indistinguishable from a broken product.
    let r = g.ok(&["trust", "root-update", "--anchor", successor.to_str().unwrap()]);
    assert_eq!(r["to_version"], 2);
    // (WS-3 / BC-P2-49: a gate is raised only with a complete decision package, so the positive case supplies one)
    assert!(g
        .run(&[
            "gate",
            "create",
            "--question",
            "approve something?",
            "--fields",
            &crate::ws03::package(serde_json::json!({}))
        ])
        .ok());
}

/// `AR29-B2` second limb and `AR29-N4`, measured end to end: `update --apply` is on the `OWNER-DECISION-0006` §5
/// allow-list and is still refused below floor at the Human Gate it would have to create, before any protected
/// write, with the gate-free restoration routes named — and one of those routes then works.
///
/// This is the case the allow-list and the reachable behaviour used to disagree about. They now agree, and the
/// agreement is written down in `breakglass::BELOW_FLOOR_LIMITS` as well as enforced here.
#[test]
fn an_allow_listed_operation_cannot_create_a_human_gate_below_floor() {
    use gov_runtime::srr::breakglass as bg;

    let (root, proj, g) = project("srr-s6-update");
    let p = Publisher::new();
    provision(&root, &g, &p, 1, &far_future());

    // A machine installed on a genuinely older release, so `update --check` has somewhere to go.
    let prev = canonical_root().join("fixtures/update/previous-release/4.1.1");
    let old = root.join("rel-old");
    copy_dir(&prev, &old.join("kernel"));
    p.publish(&old, 20, 100, "stable", &far_future(), "4.0.0", 50);
    let r = g.ok(&[
        "init",
        "--source",
        old.join("kernel").to_str().unwrap(),
        "--name",
        "u",
        "--alias",
        "fx-u",
    ]);
    assert_eq!(r["version"], "4.1.1");

    // Genuine owner-authorised break-glass onto the same payload published below the floor.
    let below = root.join("rel-below");
    copy_dir(&prev, &below.join("kernel"));
    p.publish(&below, 21, 60, "stable", &far_future(), "4.0.0", 50);
    let bg_status = g.ok(&["trust", "break-glass"]);
    let inbox = PathBuf::from(bg_status["inbox"].as_str().unwrap());
    let (_, payload_hash, kmh, ver) = measure(&below.join("kernel"));
    let tok = break_glass_doc(
        &machine_id(&g),
        "nonce-s6-update",
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
        below.join("kernel").to_str().unwrap(),
        "--break-glass",
    ]);
    assert_eq!(r["release_authenticity"]["below_floor"], true);
    let ms = gov_runtime::srr::state::MachineState::at(&machine_state_dir(&proj)).unwrap();
    assert!(bg::is_degraded(&ms, gov_runtime::FRAMEWORK_NAME));

    // The candidate the operator would update to. Uncertified, so `human_gate_required` is true — the ordinary
    // break-glass case, and the reason this is not a corner.
    let hi = root.join("rel-hi");
    make_release(&hi);
    p.publish(&hi, 22, 200, "stable", &far_future(), "4.0.0", 50);
    let chk = g.ok(&["update", "--check", "--source", hi.join("kernel").to_str().unwrap()]);
    assert_eq!(chk["current"], "4.1.1");
    assert_eq!(chk["human_gate_required"], true, "scenario precondition: {chk}");

    // The allow-list permits the operation ...
    assert!(bg::permitted_activity("update --apply").is_some());
    // ... and §6 bullet 2 refuses the gate inside it.
    let e = g.err(&[
        "update",
        "--apply",
        "--source",
        hi.join("kernel").to_str().unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "SRR_BELOW_FLOOR_REFUSED",
        "an allow-listed operation does not suspend §6 inside itself"
    );
    assert_eq!(e.details()["refused_class"], "human_gate_create");
    assert_eq!(e.details()["section_6_bullet"], 2);
    assert_eq!(e.details()["operation"], "gate create (update --apply)");
    let routes = e.details()["gate_free_restoration_routes"].clone();
    assert!(
        routes
            .as_array()
            .unwrap()
            .contains(&json!("kernel reinstall")),
        "a refusal that strands the operator is not a refusal we can ship: {routes}"
    );
    assert!(
        e.details()["below_floor_limits"]
            .to_string()
            .contains("update --apply"),
        "the refusal must state the allow-list limit it is enforcing"
    );

    // Nothing was created, and nothing was written.
    let gates = g.ok(&["gate", "list"]);
    assert!(
        gates.as_array().map(|a| a.is_empty()).unwrap_or(true),
        "a Human Gate was created below floor: {gates}"
    );
    assert_eq!(
        yaml(&proj, "governance/framework.lock")["version"],
        "4.1.1",
        "the refused update must not have installed anything"
    );

    // And the route the refusal names actually works: §7 exit, offline, no gate.
    let back = root.join("rel-back");
    copy_dir(&prev, &back.join("kernel"));
    p.publish(&back, 23, 100, "stable", &far_future(), "4.0.0", 50);
    let r = g.ok(&[
        "kernel",
        "reinstall",
        "--source",
        back.join("kernel").to_str().unwrap(),
    ]);
    assert_eq!(r["protected_state"]["break_glass_exit"]["cleared"], true);
    assert!(g.ok(&["trust", "status"])["degraded"].is_null());
    // once out, the gate the operator needs can be created again: the refusal was §6, not a permanent brake
    let e = g.err(&[
        "update",
        "--apply",
        "--source",
        hi.join("kernel").to_str().unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "HUMAN_GATE_REQUIRED",
        "above floor the ordinary Human Gate flow resumes"
    );
    assert!(
        e.details()["gate"].as_str().is_some(),
        "the gate that §6 forbade below floor is created normally above it: {}",
        e.details()
    );
}

/// `AR29-C1` — the marking record has exactly one reader, so the machine cannot refuse as marked while reporting
/// itself unmarked, and a satisfied `OWNER-DECISION-0006` §7 exit clears it even when it is unreadable.
///
/// This does not touch the exit **policy**: `exit_satisfied` and `EXIT_POLICY` are owner-decided
/// (`OWNER-DECISION-0007` §2) and are the single exit-floor comparison, unchanged.
#[test]
fn an_unreadable_marking_is_read_the_same_way_by_every_consumer_and_still_exits() {
    use gov_runtime::srr::breakglass as bg;
    use gov_runtime::srr::state::{Floors, MachineState};

    let dir = tmp("srr-c1-one-reader");
    let ms = MachineState::at(&dir.join("machine")).unwrap();
    let product = gov_runtime::FRAMEWORK_NAME;

    let mut floors = Floors {
        product: product.to_string(),
        ..Default::default()
    };
    floors.raise_minimum_secure("4.1.2", 12, "src");
    floors.raise_release("4.1.5", 15, true);

    for shape in [
        &b"{\"active\": tr"[..],
        &b""[..],
        &b"\x00\x01\x02binary"[..],
        &b"[1,2,3]"[..],
        &b"{\"marking\":\"x\"}"[..],
        &b"{\"active\":\"true\"}"[..],
        &b"{\"active\":null}"[..],
    ] {
        std::fs::write(ms.degraded_path(product), shape).unwrap();

        // the guard refuses ...
        let e = bg::guard(&ms, product, "cit approve").unwrap_err();
        assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED");
        // ... and every other reader agrees that the machine is marked
        assert!(
            bg::is_degraded(&ms, product),
            "two readers of one record disagree (AR29-C1)"
        );
        assert!(bg::Degraded::load(&ms, product).is_some());

        // restoration stays open ...
        for l in ["kernel reinstall", "update --apply", "update --rollback", "checkpoint"] {
            assert!(bg::guard(&ms, product, l).is_ok(), "§5 '{l}' must stay open");
        }
        // ... and so does the exit: the §7 condition clears the record rather than being silently ignored
        let exit = bg::try_exit(&ms, product, 16, "4.1.6", true, &floors)
            .unwrap()
            .expect("an unreadable marking is still a marking");
        assert_eq!(exit["cleared"], true);
        assert!(!bg::is_degraded(&ms, product));
        assert!(
            bg::guard(&ms, product, "cit approve").is_ok(),
            "governed operation must resume once the §7 exit condition is met"
        );
    }

    // The exit policy itself is untouched and still refuses below the stricter floor.
    std::fs::write(ms.degraded_path(product), b"{\"active\": tr").unwrap();
    assert_eq!(bg::EXIT_POLICY, "b_stricter_both_floors");
    let held = bg::try_exit(&ms, product, 13, "4.1.3", true, &floors)
        .unwrap()
        .unwrap();
    assert_eq!(held["cleared"], false);
    let unauth = bg::try_exit(&ms, product, 16, "4.1.6", false, &floors)
        .unwrap()
        .unwrap();
    assert_eq!(unauth["cleared"], false);
    assert!(bg::is_degraded(&ms, product));
}

/// `AR29-N5` — the refusal-class tables are partitioned by what the product actually enforces, and the partition
/// is checked against the product's own enforcement-point call sites rather than asserted.
///
/// This is the mechanism behind AR-0027's false negative, closed: a table naming operations that do not exist
/// made a label sweep look like coverage. A label that is enforced belongs in `REFUSAL_CLASSES`; a label that is
/// not belongs in `RESERVED_REFUSAL_CLASSES`, which is a statement that the operation is absent.
#[test]
fn section_6_refusal_class_tables_are_partitioned_by_what_the_product_actually_enforces() {
    use gov_runtime::srr::breakglass as bg;

    // Every string literal this product passes to an enforcement point, read off the call sites.
    let mut enforced: Vec<String> = vec![];
    for (path, text) in product_sources() {
        if path.ends_with("srr/breakglass.rs") {
            continue; // the tables themselves, and the guards' own definitions
        }
        for call in [
            "guard_write(p, \"",
            "guard_write(&p, \"",
            "guard_write(&p0, \"",
            "guard_write(&self.project, \"",
        ] {
            for part in text.split(call).skip(1) {
                if let Some(q) = part.find('"') {
                    enforced.push(part[..q].to_string());
                }
            }
        }
        // `breakglass::guard(...)` and `guard_effect(...)` take the label as the last argument.
        for part in text.split("Effect::").skip(1) {
            if let Some(a) = part.find(",\n") {
                let tail = &part[a..];
                if let Some(q0) = tail.find('"') {
                    if let Some(q1) = tail[q0 + 1..].find('"') {
                        enforced.push(tail[q0 + 1..q0 + 1 + q1].to_string());
                    }
                }
            }
        }
        for part in text.split("breakglass::guard(&ms, crate::FRAMEWORK_NAME, \"").skip(1) {
            if let Some(q) = part.find('"') {
                enforced.push(part[..q].to_string());
            }
        }
    }
    enforced.sort();
    enforced.dedup();
    println!("§6 enforcement-point labels in the product ({}): {enforced:?}", enforced.len());

    for (label, class) in bg::REFUSAL_CLASSES {
        assert!(
            bg::REFUSED_ACTIVITIES.contains(class),
            "'{class}' is not an OWNER-DECISION-0006 §6 activity"
        );
        assert!(
            enforced.iter().any(|e| e == label),
            "REFUSAL_CLASSES names '{label}', which this product passes to no enforcement point. A table of \
             operations that do not exist is what made AR-0027's label sweep read as coverage (AR29-N5); move \
             it to RESERVED_REFUSAL_CLASSES or give it a call site."
        );
        assert!(bg::permitted_activity(label).is_none());
    }
    for (label, class) in bg::RESERVED_REFUSAL_CLASSES {
        assert!(bg::REFUSED_ACTIVITIES.contains(class));
        assert!(
            !enforced.iter().any(|e| e == label),
            "'{label}' is reserved as a name no operation carries, but the product now enforces it: promote it \
             to REFUSAL_CLASSES"
        );
    }
    // Neither table decides anything: an unnamed label is refused exactly as a named one is.
    assert_eq!(bg::REFUSAL_POLICY, "allow_list_default_refuse");
    assert_eq!(
        bg::refusal_class("an operation invented after AR-0030"),
        "normal_privileged_operation"
    );
}

/// The preservation census, in the product's own suite.
///
/// `AR29-N1` asked for `AuthenticatedRelease` to become genuinely unconstructible outside `admit`. Sealing it has
/// one unavoidable consequence: AR-0029's `ho_f_preservation` binary no longer compiles, because its `f4` **is** a
/// struct literal of that type from an external crate — the compile error is the finding closing. That binary also
/// carried six preservation checks unrelated to `f4`, so they are restored here, in the same shape, rather than
/// quietly lost. Nothing here is new policy; it is evidence that was external and is now internal.
#[test]
fn the_no_bypass_and_no_signing_preservation_census_still_holds() {
    // f1 — the permissive ed25519 verifier is out of scope crate-wide, not merely unused.
    let mut importers: Vec<String> = vec![];
    let mut permissive: Vec<String> = vec![];
    for (path, text) in product_sources() {
        for (n, line) in text.lines().enumerate() {
            let code = line.split("//").next().unwrap_or("");
            if code.contains("use ed25519_dalek") && code.contains("Verifier") {
                importers.push(format!("{path}:{}", n + 1));
            }
            if code.contains(".verify(") && !code.contains("verify_strict") {
                permissive.push(format!("{path}:{} {}", n + 1, code.trim()));
            }
        }
    }
    assert!(
        importers.is_empty(),
        "the permissive `Verifier` trait is in scope at {importers:?}"
    );
    assert!(permissive.is_empty(), "a bare `.verify(` call exists: {permissive:?}");

    // f2 — `gov` verifies and never signs (`SRR-R0-L4` stays vacuous).
    let mut signing: Vec<String> = vec![];
    for (path, text) in product_sources() {
        for (n, line) in text.lines().enumerate() {
            let code = line.split("//").next().unwrap_or("");
            for needle in ["SigningKey", "ed25519_dalek::Signer", "PRIVATE KEY", "from_keypair_bytes"] {
                if !code.contains(needle) {
                    continue;
                }
                // `security/secrets.rs` carries a secret *detector* regex naming the PEM header it looks for.
                if needle == "PRIVATE KEY" && path.ends_with("security/secrets.rs") && code.contains("-----BEGIN")
                {
                    continue;
                }
                signing.push(format!("{path}:{} {}", n + 1, code.trim()));
            }
        }
    }
    assert!(signing.is_empty(), "product source can sign: {signing:?}");

    // f3 — exactly five `admit` sites, exactly five `install_kernel` call sites, no path-taking variant.
    let mut admits: Vec<String> = vec![];
    let mut installs: Vec<String> = vec![];
    for (path, text) in product_sources() {
        for (n, line) in text.lines().enumerate() {
            let code = line.split("//").next().unwrap_or("");
            if code.contains("srr::admit(") {
                admits.push(format!("{path}:{}", n + 1));
            }
            if (code.contains("install_kernel(&") || code.contains("install_kernel(a,"))
                && !code.contains("fn install_kernel")
            {
                installs.push(format!("{path}:{}", n + 1));
            }
        }
    }
    assert_eq!(admits.len(), 5, "admit call sites: {admits:?}");
    assert_eq!(installs.len(), 5, "install_kernel call sites: {installs:?}");
    let kernel = src("runtime/src/kernel.rs");
    assert!(kernel.contains("pub fn install_kernel(\n    auth: &crate::srr::AuthenticatedRelease,"));
    assert!(!kernel.contains("pub fn install_kernel_from_path"));

    // f5 — D-0007 stays a separate control that establishes *intact*, never *authentic* or *admissible*.
    let kt = src("runtime/src/kernel_trust.rs");
    for forbidden in [
        "srr::admit",
        "AuthenticatedRelease",
        "Authenticity",
        "breakglass",
        "below_floor",
        "Floors",
    ] {
        assert!(
            !kt.contains(forbidden),
            "D-0007 (`kernel_trust`) reads `{forbidden}` from the SRR verdicts"
        );
    }
    let verifier_rs = src("runtime/src/srr/verifier.rs");
    let admit_body = verifier_rs.split("fn admit_inner").nth(1).unwrap();
    assert!(
        !admit_body.contains("kernel_trust"),
        "the verifier consults the D-0007 integrity control when deciding admissibility"
    );

    // f7 — floors are monotonic and rise only from an authenticated observation.
    let mut f = gov_runtime::srr::state::Floors {
        product: gov_runtime::FRAMEWORK_NAME.into(),
        ..Default::default()
    };
    f.raise_release("4.1.5", 15, true);
    f.raise_minimum_secure("4.1.2", 12, "src");
    f.raise_metadata("release", 7);
    f.raise_release("4.0.0", 1, true);
    f.raise_minimum_secure("4.0.0", 1, "src");
    f.raise_metadata("release", 1);
    assert_eq!(f.release_high_water_sequence, 15);
    assert_eq!(f.release_high_water_version, "4.1.5");
    assert_eq!(f.minimum_secure_sequence, 12);
    assert_eq!(f.metadata_floor("release"), 7);
    let before = f.release_high_water_sequence;
    f.raise_release("9.9.9", 999, false);
    assert_eq!(before, f.release_high_water_sequence, "an unverified install raised a floor");

    // and the SRR2-R1-C1 exit policy point is untouched and still single.
    assert_eq!(gov_runtime::srr::breakglass::EXIT_POLICY, "b_stricter_both_floors");
    let exit_sites: usize = product_sources()
        .iter()
        .map(|(_, t)| t.matches("effective_floor_sequence()").count())
        .sum();
    assert!(
        exit_sites <= 4,
        "the exit-floor comparison has spread beyond `exit_satisfied` and its reporting"
    );
}
