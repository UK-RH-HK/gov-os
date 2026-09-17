//! HELD-OUT INDEPENDENT R1 VERIFICATION SUITE, part 2 — AR-0027 (verifier-a).
//!
//! Expiry / freshness attacks (disclosed residual 3), end-to-end ingress + floor behaviour (frozen R1 items 3,4,7,9),
//! posture attacks (disclosed residuals 1 and 2) and break-glass conformance to OWNER-DECISION-0006.
//!
//! Run single-threaded: these scenarios manipulate process-global environment.
#[path = "common/forge.rs"]
mod forge;

use forge::*;
use gov_runtime::srr::metadata::Envelope;
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

fn scratch(name: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!(
        "ar0027-{}-{}-{}", name, std::process::id(),
        std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()));
    std::fs::create_dir_all(&d).unwrap();
    d
}

fn isolate(state_home: &Path) {
    let keys: Vec<String> = std::env::vars().map(|(k, _)| k).filter(|k| k.starts_with("GOV_")).collect();
    for k in keys { std::env::remove_var(&k); }
    std::env::set_var("XDG_STATE_HOME", state_home);
}

fn state_root(home: &Path) -> PathBuf {
    home.join("governance-os").join("machine")
}

fn candidate_kernel() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../wt/srr1-r1-verify/framework").canonicalize().unwrap()
}

struct Measured {
    payload_hash: String,
    kernel_manifest_hash: String,
    files: BTreeMap<String, String>,
    version: String,
    migrations: String,
}

fn measure(home: &Path) -> Measured {
    let ms = gov_runtime::srr::state::MachineState::at(&state_root(home)).unwrap();
    let s = gov_runtime::srr::staging::stage(&ms, &candidate_kernel()).unwrap();
    let m = Measured {
        payload_hash: s.payload_hash.clone(),
        kernel_manifest_hash: s.kernel_manifest_hash.clone(),
        files: s.files.clone(),
        version: s.version.clone(),
        migrations: migration_bindings_from(&s.payload_dir),
    };
    gov_runtime::srr::staging::abandon(&ms, &s, "measurement only (held-out harness)");
    m
}

fn write(p: &Path, s: &str) {
    if let Some(d) = p.parent() { std::fs::create_dir_all(d).unwrap(); }
    std::fs::write(p, s).unwrap();
}

/// The migration identities the STAGED payload actually carries, bound by digest exactly as the verifier
/// recomputes them. Binding these is mandatory: the verifier refuses a payload carrying a migration the signed
/// metadata does not name, which `c7` proves separately.
fn migration_bindings_from(payload_dir: &Path) -> String {
    let migs = gov_runtime::migrations::framework::load_migrations(payload_dir);
    let items: Vec<String> = migs.iter().map(|m| {
        let id = m.get("id").and_then(|v| v.as_str()).unwrap_or("");
        let sha = gov_runtime::util::sha256_text(&gov_runtime::util::canonical_json(m));
        format!(r#"{{"id":{},"from_version":"","to_version":"","sha256":"{}"}}"#, json_str(id), sha)
    }).collect();
    items.join(",")
}

// ================================================================= B. expiry / freshness (disclosed residual 3)

/// The residual the builder disclosed: expiry is a lexicographic comparison of RFC-3339 UTC strings at second
/// precision. This test establishes what the comparison actually does with inputs that are valid RFC-3339 but not
/// in the format the emitter produces.
#[test]
fn b1_expiry_comparison_against_valid_but_non_emitted_rfc3339_forms() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    let now = "2026-09-17T12:00:00Z";

    let with_expiry = |e: &str| {
        let t = RootSpec { version: 1, expires: e, product: PRODUCT,
            root_keys: vec![&rk], root_threshold: 1, release_keys: vec![&rel], release_threshold: 1,
            snapshot_keys: vec![&sn], timestamp_keys: vec![&ts], recovery_keys: vec![&rc] }.signed_text();
        let f = signed_envelope(&t, &[&rk]);
        Envelope::parse(f.as_bytes(), "x").unwrap().is_expired(now)
    };

    // Controls: the emitted format behaves correctly.
    assert!(with_expiry("2026-09-17T11:59:59Z"), "past UTC must be expired");
    assert!(!with_expiry("2026-09-17T12:00:01Z"), "future UTC must not be expired");

    // ATTACK 1 — a UTC offset. `2026-09-17T13:00:00+14:00` is 2026-09-16T23:00:00Z: thirteen hours in the PAST.
    let offset_past = with_expiry("2026-09-17T13:00:00+14:00");
    // ATTACK 2 — `2026-09-18T00:00:00-12:00` is 2026-09-18T12:00:00Z: genuinely in the future. Same family.
    // ATTACK 3 — RFC-3339 permits lowercase 't'/'z'.
    let lowercase_past = with_expiry("2026-09-17t11:59:59z");
    // ATTACK 4 — no `expires` member at all.
    let t = RootSpec { version: 1, expires: "2099-01-01T00:00:00Z", product: PRODUCT,
        root_keys: vec![&rk], root_threshold: 1, release_keys: vec![&rel], release_threshold: 1,
        snapshot_keys: vec![&sn], timestamp_keys: vec![&ts], recovery_keys: vec![&rc] }
        .signed_text().replace(r#""expires":"2099-01-01T00:00:00Z","#, "");
    assert!(!t.contains("expires"), "the expires member must actually be gone");
    let missing = Envelope::parse(signed_envelope(&t, &[&rk]).as_bytes(), "x").unwrap().is_expired(now);

    println!("AR-0027 B1 expiry findings:");
    println!("  offset form  '2026-09-17T13:00:00+14:00' (13h in the past) -> expired = {offset_past}");
    println!("  lowercase    '2026-09-17t11:59:59z'      (1s in the past)  -> expired = {lowercase_past}");
    println!("  absent `expires` member                                    -> expired = {missing}");

    // Record the observed behaviour as the finding, rather than asserting the behaviour we would prefer.
    assert!(!offset_past,
        "OBSERVED: a non-UTC RFC-3339 expiry that is genuinely in the past is NOT treated as expired");
    assert!(!lowercase_past,
        "OBSERVED: a lowercase-'z' RFC-3339 expiry that is genuinely in the past is NOT treated as expired");
    assert!(!missing,
        "OBSERVED: metadata carrying no `expires` member never expires (fail-open default)");
}

/// Is there any canonical-format gate on `expires` anywhere, i.e. is the lexicographic comparison's precondition
/// (both sides in the emitted UTC second-precision form) actually enforced on the untrusted side?
#[test]
fn b2_no_canonical_form_check_guards_the_lexicographic_expiry_comparison() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    // A root whose expiry is in a form the emitter never produces still parses and provisions cleanly.
    let t = RootSpec { version: 1, expires: "2099-01-01T00:00:00+00:00", product: PRODUCT,
        root_keys: vec![&rk], root_threshold: 1, release_keys: vec![&rel], release_threshold: 1,
        snapshot_keys: vec![&sn], timestamp_keys: vec![&ts], recovery_keys: vec![&rc] }.signed_text();
    let env = Envelope::parse(signed_envelope(&t, &[&rk]).as_bytes(), "x").unwrap();
    let root = gov_runtime::srr::metadata::parse_self_signed_root(env, "2026-09-17T12:00:00Z");
    assert!(root.is_ok(), "a non-emitted-format expiry is accepted without complaint: {root:?}");
}

// ============================================== C. end-to-end ingress, floors, posture (residuals 1 and 2)

/// Provision a machine, admit a correctly signed release, and confirm the protected floor is then enforced at a
/// NON-`rollback` ingress. Frozen R1 items 3, 4, 7 and 9.
#[test]
fn c1_floor_binds_a_non_rollback_ingress_after_a_verified_install() {
    let home = scratch("c1");
    isolate(&home);
    let m = measure(&home);

    let (rk, rel, sn, ts, rc) = (key(11), key(12), key(13), key(14), key(15));
    let spec = RootSpec::simple(&rk, &rel, &sn, &ts, &rc);
    let anchor = scratch("c1-admin").join("root.json");
    write(&anchor, &spec.file());
    let p = gov_runtime::srr::provision::provision(&anchor, None).expect("provision");
    assert_eq!(p["provisioned"], true);

    // A correctly signed release for the exact measured bytes, with a signed minimum secure release.
    let meta = scratch("c1-meta");
    let files: Vec<String> = m.files.iter()
        .map(|(k, v)| format!(r#"{}:{{"sha256":"{}"}}"#, json_str(k), v)).collect();
    let mk = |seq: u64, min_seq: u64, min_rel: &str, ver: u64| format!(
        r#"{{"_type":"release","spec_version":"srr/1","version":{ver},"expires":"2099-01-01T00:00:00Z","product":"{PRODUCT}","repository":"held-out","channel":"stable","release_version":"{}","sequence":{seq},"platforms":["any"],"minimum_secure_release":"{min_rel}","minimum_secure_sequence":{min_seq},"payload":{{"payload_hash":"{}","kernel_manifest_hash":"{}","files":{{{}}}}},"migrations":[{}],"delegations":[]}}"#,
        m.version, m.payload_hash, m.kernel_manifest_hash, files.join(","), m.migrations);

    write(&meta.join("release.json"), &signed_envelope(&mk(40, 0, "", 1), &[&rel]));

    let auth = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel())
            .with_metadata_dir(Some(meta.clone()))
            .with_channel(Some("stable".into()))).expect("a correctly signed release must be admitted");
    assert_eq!(auth.authenticity, gov_runtime::srr::Authenticity::Authentic);
    assert_eq!(auth.sequence, 40);
    assert!(!auth.below_floor);
    gov_runtime::srr::record_installed(&auth).expect("record");

    // Now present an OLDER release at the `update` ingress — not `rollback`. The floor must still bind.
    let meta2 = scratch("c1-meta-old");
    write(&meta2.join("release.json"), &signed_envelope(&mk(9, 0, "", 2), &[&rel]));
    let e = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel())
            .with_metadata_dir(Some(meta2.clone()))
            .with_channel(Some("stable".into()))).unwrap_err();
    assert_eq!(e.code, "SRR_BELOW_FLOOR", "the floor must bind `update`, not only `rollback`: {e:?}");

    // ... and at `init`, `adopt`, `reinstall`, `recovery` too.
    for ing in [gov_runtime::srr::Ingress::Init, gov_runtime::srr::Ingress::Adopt,
                gov_runtime::srr::Ingress::Reinstall, gov_runtime::srr::Ingress::Recovery,
                gov_runtime::srr::Ingress::Rollback] {
        let e = gov_runtime::srr::admit(
            gov_runtime::srr::AdmissionRequest::new(ing, &candidate_kernel())
                .with_metadata_dir(Some(meta2.clone()))
                .with_channel(Some("stable".into()))).unwrap_err();
        assert_eq!(e.code, "SRR_BELOW_FLOOR", "ingress {:?} must be bound by the floor", ing.as_str());
    }

    // Replaying the older METADATA version is independently refused by the metadata high-water.
    let meta3 = scratch("c1-meta-replay");
    write(&meta3.join("release.json"), &signed_envelope(&mk(40, 0, "", 1), &[&rel]));
    let e3 = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel())
            .with_metadata_dir(Some(meta3)).with_channel(Some("stable".into())));
    // version 1 < high-water 2 (raised by the refused-but-parsed meta2) OR admitted at equal sequence.
    println!("AR-0027 C1 metadata replay outcome: {:?}", e3.as_ref().err().map(|x| x.code.clone()));
}

/// Wrong product / wrong channel / modified payload / unauthorised extra file must all fail closed.
#[test]
fn c2_identity_and_payload_binding_fail_closed() {
    let home = scratch("c2");
    isolate(&home);
    let m = measure(&home);
    let (rk, rel, sn, ts, rc) = (key(21), key(22), key(23), key(24), key(25));
    let anchor = scratch("c2-admin").join("root.json");
    write(&anchor, &RootSpec::simple(&rk, &rel, &sn, &ts, &rc).file());
    gov_runtime::srr::provision::provision(&anchor, None).expect("provision");

    let files: Vec<String> = m.files.iter()
        .map(|(k, v)| format!(r#"{}:{{"sha256":"{}"}}"#, json_str(k), v)).collect();
    let base = format!(
        r#"{{"_type":"release","spec_version":"srr/1","version":1,"expires":"2099-01-01T00:00:00Z","product":"{PRODUCT}","repository":"held-out","channel":"stable","release_version":"{}","sequence":40,"platforms":["any"],"minimum_secure_release":"","minimum_secure_sequence":0,"payload":{{"payload_hash":"{}","kernel_manifest_hash":"{}","files":{{{}}}}},"migrations":[{}],"delegations":[]}}"#,
        m.version, m.payload_hash, m.kernel_manifest_hash, files.join(","), m.migrations);

    let run = |text: &str, chan: Option<&str>| {
        let d = scratch("c2-m");
        write(&d.join("release.json"), &signed_envelope(text, &[&rel]));
        gov_runtime::srr::admit(
            gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel())
                .with_metadata_dir(Some(d)).with_channel(chan.map(|c| c.to_string())))
    };

    // wrong product
    let wrong_product = base.replace(&format!(r#""product":"{PRODUCT}""#), r#""product":"some-other-product""#);
    assert_eq!(run(&wrong_product, None).unwrap_err().code, "SRR_WRONG_PRODUCT");

    // wrong channel (SRR-R0-L2)
    assert_eq!(run(&base, Some("beta")).unwrap_err().code, "SRR_WRONG_CHANNEL");

    // modified payload digest
    let bad_payload = base.replace(&m.payload_hash, &"0".repeat(64));
    assert_eq!(run(&bad_payload, None).unwrap_err().code, "SRR_PAYLOAD_DIGEST_MISMATCH");

    // a signed file the payload does not contain
    let extra = base.replace(r#""migrations":[]"#, r#""migrations":[]"#);
    let extra = extra.replacen(r#""files":{"#, r#""files":{"ghost/file.txt":{"sha256":"aa"},"#, 1);
    assert_eq!(run(&extra, None).unwrap_err().code, "SRR_PAYLOAD_FILE_MISSING");

    // unsupported platform
    let plat = base.replace(r#""platforms":["any"]"#, r#""platforms":["plan9-vax"]"#);
    assert_eq!(run(&plat, None).unwrap_err().code, "SRR_UNSUPPORTED_PLATFORM");

    // expired release metadata
    let exp = base.replace(r#""expires":"2099-01-01T00:00:00Z""#, r#""expires":"2000-01-01T00:00:00Z""#);
    assert_eq!(run(&exp, None).unwrap_err().code, "SRR_METADATA_EXPIRED");

    // signed by a key the root does not authorise for `release`
    let evil = key(99);
    let d = scratch("c2-evil");
    write(&d.join("release.json"), &signed_envelope(&base, &[&evil]));
    let e = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel())
            .with_metadata_dir(Some(d))).unwrap_err();
    assert_eq!(e.code, "SRR_THRESHOLD_NOT_MET");
}

/// A provisioned machine must refuse an unsigned candidate at every ingress that may not fall back to its own
/// protected record, and must fail closed — not silently unprovision — when the anchor file is removed.
#[test]
fn c3_provisioned_machine_refuses_unsigned_input_and_anchor_removal_fails_closed() {
    let home = scratch("c3");
    isolate(&home);
    let (rk, rel, sn, ts, rc) = (key(31), key(32), key(33), key(34), key(35));
    let anchor = scratch("c3-admin").join("root.json");
    write(&anchor, &RootSpec::simple(&rk, &rel, &sn, &ts, &rc).file());
    gov_runtime::srr::provision::provision(&anchor, None).expect("provision");

    // No metadata at all, at an ingress that may not use the protected record.
    for ing in [gov_runtime::srr::Ingress::Init, gov_runtime::srr::Ingress::Adopt,
                gov_runtime::srr::Ingress::Update] {
        let e = gov_runtime::srr::admit(
            gov_runtime::srr::AdmissionRequest::new(ing, &candidate_kernel())).unwrap_err();
        assert_eq!(e.code, "SRR_RELEASE_UNVERIFIED", "ingress {} must refuse unsigned input", ing.as_str());
    }

    // Recovery may consult the protected record — but there is none, so it also refuses.
    let e = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Recovery, &candidate_kernel())).unwrap_err();
    assert_eq!(e.code, "SRR_RELEASE_UNVERIFIED");

    // Deleting the anchor does NOT return the machine to the unprovisioned posture.
    std::fs::remove_file(state_root(&home).join("trust").join("root.json")).unwrap();
    let e = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel())).unwrap_err();
    assert_eq!(e.code, "SRR_TRUST_ANCHOR_MISSING",
        "removing root.json must fail closed, never silently unprovision the machine");
}

/// Disclosed residual 1+2 combined: can an adversary RETURN a provisioned machine to the unprovisioned posture and
/// thereby evade the floor? This test establishes exactly which mechanisms do and do not achieve that.
#[test]
fn c4_returning_a_machine_to_the_unprovisioned_posture() {
    let home = scratch("c4");
    isolate(&home);
    let (rk, rel, sn, ts, rc) = (key(41), key(42), key(43), key(44), key(45));
    let anchor = scratch("c4-admin").join("root.json");
    write(&anchor, &RootSpec::simple(&rk, &rel, &sn, &ts, &rc).file());
    gov_runtime::srr::provision::provision(&anchor, None).expect("provision");
    assert_eq!(gov_runtime::srr::status().unwrap()["posture"], "PROVISIONED");

    // (a) GOV_MACHINE_STATE_DIR on a provisioned machine — must be REFUSED.
    let elsewhere = scratch("c4-elsewhere");
    std::env::set_var("GOV_MACHINE_STATE_DIR", &elsewhere);
    let refused = gov_runtime::srr::state::resolve_state_root();
    assert!(refused.is_err(), "GOV_MACHINE_STATE_DIR must be refused on a provisioned machine");
    assert_eq!(refused.unwrap_err().code, "SRR_PROTECTED_STATE_OVERRIDE_REFUSED");
    std::env::remove_var("GOV_MACHINE_STATE_DIR");

    // (b) Relocating XDG_STATE_HOME — the SAME outcome the named override refuses.
    let relocated = scratch("c4-relocated");
    std::env::set_var("XDG_STATE_HOME", &relocated);
    let st = gov_runtime::srr::status().unwrap();
    println!("AR-0027 C4: after relocating XDG_STATE_HOME, posture = {}", st["posture"]);
    assert_eq!(st["posture"], "UNPROVISIONED",
        "OBSERVED: relocating XDG_STATE_HOME returns the machine to the unprovisioned posture, achieving \
         exactly what GOV_MACHINE_STATE_DIR is refused for");

    // In that posture, entirely unsigned bytes are ADMITTED, with an honest UNKNOWN authenticity claim.
    let auth = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel()))
        .expect("unprovisioned posture admits unsigned bytes");
    assert_eq!(auth.authenticity, gov_runtime::srr::Authenticity::Unknown);
    assert_eq!(auth.posture, gov_runtime::srr::Posture::Unprovisioned);
    assert!(!auth.below_floor, "no floor is established on the relocated state root");

    // The honesty claim: it never says AUTHENTIC, and status reports the posture plainly.
    assert_eq!(auth.to_value()["authenticity"], "UNKNOWN");
    assert!(auth.notes.iter().any(|n| n.contains("no provisioned Signed Release Root trust anchor")),
        "the verifier must say plainly that no anchor exists: {:?}", auth.notes);

    // And no floor is manufactured from the unauthenticated install.
    gov_runtime::srr::record_installed(&auth).expect("record");
    let f = gov_runtime::srr::state::Floors::load(
        &gov_runtime::srr::state::MachineState::at(&state_root(&relocated)).unwrap(), PRODUCT);
    assert!(f.release_high_water_version.is_empty() && f.release_high_water_sequence == 0,
        "an UNKNOWN-authenticity install must never advance a protected floor");

    std::env::set_var("XDG_STATE_HOME", &home);
    assert_eq!(gov_runtime::srr::status().unwrap()["posture"], "PROVISIONED",
        "the real machine's protected state is untouched by the relocation");
}

/// Frozen R1: "project, CLI, environment, model and plugin inputs cannot create trust or approval."
#[test]
fn c5_environment_cannot_carry_authority() {
    let home = scratch("c5");
    isolate(&home);
    for v in gov_runtime::srr::state::REFUSED_AUTHORITY_ENV {
        std::env::set_var(v, "1");
        let e = gov_runtime::srr::admit(
            gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel()))
            .unwrap_err();
        assert_eq!(e.code, "SRR_ENV_CANNOT_CREATE_AUTHORITY", "{v} must be refused outright");
        std::env::remove_var(v);
    }
    // Setting one to the empty string must not slip past `var_os(..).is_some()`.
    std::env::set_var("GOV_SKIP_VERIFY", "");
    let e = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel()));
    assert!(e.is_err() && e.unwrap_err().code == "SRR_ENV_CANNOT_CREATE_AUTHORITY",
        "an empty-valued authority variable must still be refused");
    std::env::remove_var("GOV_SKIP_VERIFY");
}

/// `SRR2-R1-C3`: the floors are a property of the machine and survive destruction of the whole project.
#[test]
fn c6_floors_survive_project_deletion() {
    let home = scratch("c6");
    isolate(&home);
    let ms = gov_runtime::srr::state::MachineState::at(&state_root(&home)).unwrap();
    let mut f = gov_runtime::srr::state::Floors::load(&ms, PRODUCT);
    f.raise_release("4.1.5", 55, true);
    f.raise_minimum_secure("4.1.4", 44, "src");
    f.save(&ms).unwrap();

    let project = scratch("c6-project");
    std::fs::create_dir_all(project.join("governance")).unwrap();
    std::fs::remove_dir_all(&project).unwrap();

    let f2 = gov_runtime::srr::state::Floors::load(&ms, PRODUCT);
    assert_eq!(f2.release_high_water_sequence, 55);
    assert_eq!(f2.minimum_secure_sequence, 44);
    assert!(!state_root(&home).starts_with(&project), "protected state must live outside every repository");

    // Monotonic: a lower value is never written.
    let mut f3 = f2.clone();
    f3.raise_release("1.0.0", 1, true);
    f3.raise_minimum_secure("1.0.0", 1, "x");
    assert_eq!(f3.release_high_water_sequence, 55);
    assert_eq!(f3.minimum_secure_sequence, 44);
    // ... and an unauthenticated observation never raises it at all.
    let mut f4 = f2.clone();
    f4.raise_release("9.9.9", 999, false);
    assert_eq!(f4.release_high_water_sequence, 55);
}
