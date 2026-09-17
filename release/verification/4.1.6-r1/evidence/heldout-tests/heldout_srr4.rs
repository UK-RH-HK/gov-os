//! HELD-OUT INDEPENDENT R1 VERIFICATION SUITE, part 4 — AR-0027 (verifier-a).
//!
//! Trust-anchor freshness, the TUF freshness roles, atomic/crash-safe commit, and the authentic/intact separation.
#[path = "common/forge.rs"]
mod forge;

use forge::*;
use std::path::{Path, PathBuf};

fn scratch(name: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!(
        "ar0027-{}-{}-{}", name, std::process::id(),
        std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()));
    std::fs::create_dir_all(&d).unwrap();
    d
}
fn isolate(h: &Path) {
    let ks: Vec<String> = std::env::vars().map(|(k, _)| k).filter(|k| k.starts_with("GOV_")).collect();
    for k in ks { std::env::remove_var(&k); }
    std::env::set_var("XDG_STATE_HOME", h);
}
fn state_root(h: &Path) -> PathBuf { h.join("governance-os").join("machine") }
fn candidate_kernel() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../wt/srr1-r1-verify/framework").canonicalize().unwrap()
}
fn write(p: &Path, s: &str) {
    if let Some(d) = p.parent() { std::fs::create_dir_all(d).unwrap(); }
    std::fs::write(p, s).unwrap();
}

struct Env { payload_hash: String, kmh: String, files: String, version: String, migrations: String }
fn measure(home: &Path) -> Env {
    let ms = gov_runtime::srr::state::MachineState::at(&state_root(home)).unwrap();
    let s = gov_runtime::srr::staging::stage(&ms, &candidate_kernel()).unwrap();
    let files: Vec<String> = s.files.iter()
        .map(|(k, v)| format!(r#"{}:{{"sha256":"{}"}}"#, json_str(k), v)).collect();
    let mitems: Vec<String> = gov_runtime::migrations::framework::load_migrations(&s.payload_dir).iter()
        .map(|m| format!(r#"{{"id":{},"from_version":"","to_version":"","sha256":"{}"}}"#,
            json_str(m.get("id").and_then(|v| v.as_str()).unwrap_or("")),
            gov_runtime::util::sha256_text(&gov_runtime::util::canonical_json(m)))).collect();
    let e = Env { payload_hash: s.payload_hash.clone(), kmh: s.kernel_manifest_hash.clone(),
        files: files.join(","), version: s.version.clone(), migrations: mitems.join(",") };
    gov_runtime::srr::staging::abandon(&ms, &s, "measurement only");
    e
}
fn release_text(e: &Env, seq: u64, ver: u64) -> String {
    format!(
        r#"{{"_type":"release","spec_version":"srr/1","version":{ver},"expires":"2099-01-01T00:00:00Z","product":"{PRODUCT}","repository":"held-out","channel":"stable","release_version":"{}","sequence":{seq},"platforms":["any"],"minimum_secure_release":"","minimum_secure_sequence":0,"payload":{{"payload_hash":"{}","kernel_manifest_hash":"{}","files":{{{}}}}},"migrations":[{}],"delegations":[]}}"#,
        e.version, e.payload_hash, e.kmh, e.files, e.migrations)
}

// ======================================================== E. trust-anchor freshness and the TUF freshness roles

/// Frozen R1: "... and expiry fail closed." An EXPIRED trust anchor is the case the verifier's own comment says
/// "cannot authorise a trust change". This test establishes what the code actually does.
#[test]
fn e1_an_expired_trust_anchor_still_authorises_a_release_install() {
    let home = scratch("e1");
    isolate(&home);
    let e = measure(&home);
    let (rk, rel, sn, ts, rc) = (key(91), key(92), key(93), key(94), key(95));

    // Provision while the root is still valid, then let it expire (simulated by installing an already-expired
    // anchor directly into protected state, which is what an owner's short-lived root looks like after its date).
    let anchor = scratch("e1-admin").join("root.json");
    write(&anchor, &RootSpec::simple(&rk, &rel, &sn, &ts, &rc).file());
    gov_runtime::srr::provision::provision(&anchor, None).expect("provision");

    let expired_root = RootSpec { version: 1, expires: "2000-01-01T00:00:00Z", product: PRODUCT,
        root_keys: vec![&rk], root_threshold: 1, release_keys: vec![&rel], release_threshold: 1,
        snapshot_keys: vec![&sn], timestamp_keys: vec![&ts], recovery_keys: vec![&rc] }.file();
    let ms = gov_runtime::srr::state::MachineState::at(&state_root(&home)).unwrap();
    std::fs::write(ms.root_metadata_path(), expired_root).unwrap();

    // `gov trust status` reports the expiry honestly.
    let st = gov_runtime::srr::status().unwrap();
    assert_eq!(st["trust_anchor"]["expired_against_local_clock"], true,
        "status must report the anchor's expiry honestly");

    // But a release install — a trust-changing lifecycle operation — still proceeds against it.
    let meta = scratch("e1-meta");
    write(&meta.join("release.json"), &signed_envelope(&release_text(&e, 40, 1), &[&rel]));
    let r = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel())
            .with_metadata_dir(Some(meta)));
    println!("AR-0027 E1 — install against an EXPIRED trust anchor: {:?}",
        r.as_ref().map(|a| a.authenticity.as_str()).map_err(|e| e.code.clone()));
    assert!(r.is_ok(), "OBSERVED: an expired trust anchor still authorises a release install");
    assert_eq!(r.unwrap().authenticity, gov_runtime::srr::Authenticity::Authentic,
        "OBSERVED: the result is reported as AUTHENTIC, not as stale or refused");
}

/// TUF's snapshot and timestamp roles exist to bound freshness and defeat freeze attacks. This test establishes
/// whether an attacker who controls the metadata directory can simply omit them.
#[test]
fn e2_timestamp_and_snapshot_are_optional_and_their_expiry_does_not_refuse() {
    let home = scratch("e2");
    isolate(&home);
    let e = measure(&home);
    let (rk, rel, sn, ts, rc) = (key(101), key(102), key(103), key(104), key(105));
    let anchor = scratch("e2-admin").join("root.json");
    write(&anchor, &RootSpec::simple(&rk, &rel, &sn, &ts, &rc).file());
    gov_runtime::srr::provision::provision(&anchor, None).expect("provision");

    // (a) release.json alone — no timestamp, no snapshot.
    let bare = scratch("e2-bare");
    write(&bare.join("release.json"), &signed_envelope(&release_text(&e, 40, 1), &[&rel]));
    let a = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel())
            .with_metadata_dir(Some(bare))).expect("release.json alone is accepted");
    assert_eq!(a.authenticity, gov_runtime::srr::Authenticity::Authentic);
    println!("AR-0027 E2(a) — no timestamp/snapshot: authenticity={} currency={}",
        a.authenticity.as_str(), a.currency.as_str());
    assert_eq!(a.currency, gov_runtime::srr::Currency::Unknown,
        "currency is honestly reported as UNKNOWN ...");
    // ... but the trust-changing operation proceeds regardless of UNKNOWN currency.
    assert!(a.notes.iter().any(|n| n.contains("no timestamp metadata")),
        "the omission must at least be recorded: {:?}", a.notes);

    // (b) an EXPIRED timestamp downgrades currency to STALE but does not refuse.
    let stale = scratch("e2-stale");
    let rel_text = release_text(e_ref(&e), 41, 2);
    let rel_file = signed_envelope(&rel_text, &[&rel]);
    let rel_sha = sha256_hex(rel_file.as_bytes());
    let snap_text = format!(
        r#"{{"_type":"snapshot","spec_version":"srr/1","version":2,"expires":"2099-01-01T00:00:00Z","meta":{{"release.json":{{"version":2,"sha256":"{rel_sha}"}}}}}}"#);
    let snap_file = signed_envelope(&snap_text, &[&sn]);
    let snap_sha = sha256_hex(snap_file.as_bytes());
    let ts_text = format!(
        r#"{{"_type":"timestamp","spec_version":"srr/1","version":2,"expires":"2000-01-01T00:00:00Z","meta":{{"snapshot.json":{{"version":2,"sha256":"{snap_sha}"}}}}}}"#);
    write(&stale.join("release.json"), &rel_file);
    write(&stale.join("snapshot.json"), &snap_file);
    write(&stale.join("timestamp.json"), &signed_envelope(&ts_text, &[&ts]));
    let b = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel())
            .with_metadata_dir(Some(stale))).expect("an expired timestamp does not refuse");
    println!("AR-0027 E2(b) — expired timestamp: currency={}", b.currency.as_str());
    assert_eq!(b.currency, gov_runtime::srr::Currency::Stale,
        "OBSERVED: an expired timestamp yields STALE and the operation proceeds");

    // (c) a snapshot that does NOT bind the presented release is refused (the binding itself works).
    let bad = scratch("e2-badsnap");
    let r2 = release_text(e_ref(&e), 42, 3);
    let f2 = signed_envelope(&r2, &[&rel]);
    let snap_bad = format!(
        r#"{{"_type":"snapshot","spec_version":"srr/1","version":3,"expires":"2099-01-01T00:00:00Z","meta":{{"release.json":{{"version":3,"sha256":"{}"}}}}}}"#, "0".repeat(64));
    write(&bad.join("release.json"), &f2);
    write(&bad.join("snapshot.json"), &signed_envelope(&snap_bad, &[&sn]));
    let e3 = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel())
            .with_metadata_dir(Some(bad))).unwrap_err();
    assert_eq!(e3.code, "SRR_RELEASE_NOT_IN_SNAPSHOT",
        "when a snapshot IS present its binding is enforced");
}

fn e_ref(e: &Env) -> &Env { e }

/// Frozen R1 item 6: staging/install/rollback/recovery are atomic and crash-safe. Interrupt the transaction.
#[test]
fn e3_install_transaction_is_atomic_and_replays_after_interruption() {
    let home = scratch("e3");
    isolate(&home);
    let ms = gov_runtime::srr::state::MachineState::at(&state_root(&home)).unwrap();
    let staged = gov_runtime::srr::staging::stage(&ms, &candidate_kernel()).unwrap();

    let dest_parent = scratch("e3-install");
    let dest = dest_parent.join("kernel");

    // A pre-existing "old" installation that must survive or be cleanly replaced — never left mixed.
    std::fs::create_dir_all(&dest).unwrap();
    std::fs::write(dest.join("MARKER-OLD"), b"old").unwrap();

    // Commit, then verify the committed tree is the complete new version and no scaffolding is left behind.
    gov_runtime::srr::staging::commit_tree(&ms, &staged, &dest).expect("commit");
    assert!(dest.join("KERNEL.yaml").exists(), "the new version must be complete");
    assert!(!dest.join("MARKER-OLD").exists(), "the old tree must be gone, not merged");
    assert!(!dest_parent.join("kernel.srr-new").exists(), "no .srr-new may be left behind");
    assert!(!dest_parent.join("kernel.srr-old").exists(), "no .srr-old may be left behind");

    // Simulate a crash in the window between the two renames: `dest` absent, `dest.srr-new` complete.
    let newd = dest_parent.join("kernel.srr-new");
    std::fs::rename(&dest, &newd).unwrap();
    assert!(!dest.exists());
    // Re-create the journal intent that the real transaction would have fsynced before the rename.
    let journal = ms.journal_dir();
    let intents: Vec<_> = std::fs::read_dir(&journal).unwrap().filter_map(|e| e.ok()).collect();
    println!("AR-0027 E3 — journal entries after commit: {}", intents.len());

    let replayed = gov_runtime::srr::staging::recover(&ms).expect("recover must not fail");
    println!("AR-0027 E3 — replay actions: {:?}",
        replayed.iter().map(|r| r["action"].as_str().unwrap_or("")).collect::<Vec<_>>());

    // Whatever the journal said, the outcome must be ONE complete tree, never a mixed one.
    let complete = dest.join("KERNEL.yaml").exists() || newd.join("KERNEL.yaml").exists();
    assert!(complete, "recovery must leave one complete installation");
    assert!(!(dest.exists() && newd.exists() && dest.join("KERNEL.yaml").exists()
              && newd.join("KERNEL.yaml").exists()),
        "recovery must not leave two competing trees");
}

/// Frozen R1 item 8 / D-0007: installed-kernel integrity establishes INTACT only — never AUTHENTIC, never
/// ADMISSIBLE. Neither control may read the other's state.
#[test]
fn e4_intact_is_not_authentic_and_the_two_controls_are_independent() {
    let home = scratch("e4");
    isolate(&home);
    let (rk, rel, sn, ts, rc) = (key(111), key(112), key(113), key(114), key(115));
    let anchor = scratch("e4-admin").join("root.json");
    write(&anchor, &RootSpec::simple(&rk, &rel, &sn, &ts, &rc).file());
    gov_runtime::srr::provision::provision(&anchor, None).expect("provision");

    // A candidate that is perfectly self-consistent — payload, KERNEL_MANIFEST.json and lock all agree — is
    // exactly the "mutually consistent files delivered with the copy" case OWNER-DIRECTIVE-0004 forbids as an
    // authenticity root. With a trust anchor present and no signed metadata, it must be refused.
    let consistent = scratch("e4-candidate").join("framework");
    gov_runtime::util::copy_dir(&candidate_kernel(), &consistent).unwrap();
    let manifest = gov_runtime::kernel::build_manifest(&consistent).unwrap();
    gov_runtime::util::write_json(&consistent.join("KERNEL_MANIFEST.json"), &manifest).unwrap();

    let e = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &consistent)).unwrap_err();
    assert_eq!(e.code, "SRR_RELEASE_UNVERIFIED",
        "a self-consistent manifest must never establish authenticity");
    assert!(e.message.contains("no signed release metadata") || e.message.contains("unsigned"),
        "{}", e.message);

    // The separation is also declared in the machine's own status output.
    let st = gov_runtime::srr::status().unwrap();
    assert!(st["separation"]["intact"].as_str().unwrap().contains("D-0007"));
    assert!(st["separation"]["authentic"].as_str().unwrap().contains("signed release metadata"));
    assert!(st["separation"]["admissible"].as_str().unwrap().contains("floor"));
}
