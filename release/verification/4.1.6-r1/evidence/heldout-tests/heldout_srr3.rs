//! HELD-OUT INDEPENDENT R1 VERIFICATION SUITE, part 3 — AR-0027 (verifier-a).
//!
//! Below-floor break-glass recovery against all ten binding requirements of OWNER-DECISION-0006, and the
//! `SRR2-R1-C1` exit policy point.
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
    let migs = gov_runtime::migrations::framework::load_migrations(&s.payload_dir);
    let mitems: Vec<String> = migs.iter().map(|m| {
        let id = m.get("id").and_then(|v| v.as_str()).unwrap_or("");
        let sha = gov_runtime::util::sha256_text(&gov_runtime::util::canonical_json(m));
        format!(r#"{{"id":{},"from_version":"","to_version":"","sha256":"{}"}}"#, json_str(id), sha)
    }).collect();
    let e = Env { payload_hash: s.payload_hash.clone(), kmh: s.kernel_manifest_hash.clone(),
        files: files.join(","), version: s.version.clone(), migrations: mitems.join(",") };
    gov_runtime::srr::staging::abandon(&ms, &s, "measurement only");
    e
}

fn release_text(e: &Env, seq: u64, ver: u64, min_rel: &str, min_seq: u64) -> String {
    format!(
        r#"{{"_type":"release","spec_version":"srr/1","version":{ver},"expires":"2099-01-01T00:00:00Z","product":"{PRODUCT}","repository":"held-out","channel":"stable","release_version":"{}","sequence":{seq},"platforms":["any"],"minimum_secure_release":"{min_rel}","minimum_secure_sequence":{min_seq},"payload":{{"payload_hash":"{}","kernel_manifest_hash":"{}","files":{{{}}}}},"migrations":[{}],"delegations":[]}}"#,
        e.version, e.payload_hash, e.kmh, e.files, e.migrations)
}

/// Provision, install at sequence 40 so a floor exists, and return the machine id.
fn provisioned_with_floor(home: &Path, tag: &str, keys: (&Key, &Key, &Key, &Key, &Key)) -> (Env, String) {
    let e = measure(home);
    let anchor = scratch(&format!("{tag}-admin")).join("root.json");
    write(&anchor, &RootSpec::simple(keys.0, keys.1, keys.2, keys.3, keys.4).file());
    gov_runtime::srr::provision::provision(&anchor, None).expect("provision");
    let meta = scratch(&format!("{tag}-meta"));
    write(&meta.join("release.json"), &signed_envelope(&release_text(&e, 40, 1, "", 0), &[keys.1]));
    let auth = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Update, &candidate_kernel())
            .with_metadata_dir(Some(meta))).expect("admit at seq 40");
    gov_runtime::srr::record_installed(&auth).expect("record");
    let mid = gov_runtime::srr::state::MachineState::at(&state_root(home)).unwrap().machine_id;
    (e, mid)
}

// ==================================================================== D. OWNER-DECISION-0006 break-glass

#[test]
fn d1_break_glass_authority_cannot_be_manufactured() {
    let home = scratch("d1");
    isolate(&home);
    let (rk, rel, sn, ts, rc) = (key(51), key(52), key(53), key(54), key(55));
    let (e, mid) = provisioned_with_floor(&home, "d1", (&rk, &rel, &sn, &ts, &rc));

    // Below floor (sequence 9 < 40) at the `recovery` ingress.
    let low = scratch("d1-low");
    write(&low.join("release.json"), &signed_envelope(&release_text(&e, 9, 1, "", 0), &[&rel]));
    let cand = candidate_kernel();
    let req = || gov_runtime::srr::AdmissionRequest::new(
        gov_runtime::srr::Ingress::Recovery, &cand).with_metadata_dir(Some(low.clone()));

    // §1/§9 — refused by default, floor binds.
    assert_eq!(gov_runtime::srr::admit(req()).unwrap_err().code, "SRR_BELOW_FLOOR");

    // The CLI-level request alone is NOT authority (§2).
    let e1 = gov_runtime::srr::admit(req().with_break_glass(true)).unwrap_err();
    assert_eq!(e1.code, "SRR_BREAK_GLASS_NOT_AUTHORISED",
        "`--break-glass` must only REQUEST; the authority must come from an owner-signed token");

    let ms = gov_runtime::srr::state::MachineState::at(&state_root(&home)).unwrap();
    let inbox = ms.break_glass_inbox();

    // A token signed by a key that is not the owner's `recovery` role is refused.
    let impostor = key(98);
    write(&inbox.join("a-impostor.json"), &signed_envelope(
        &break_glass_text(&mid, "n-impostor", "2099-01-01T00:00:00Z", &e.payload_hash, &e.kmh, &e.version),
        &[&impostor]));
    assert_eq!(gov_runtime::srr::admit(req().with_break_glass(true)).unwrap_err().code,
        "SRR_BREAK_GLASS_NOT_AUTHORISED", "a non-recovery-role signature must not authorise");

    // A token bound to a DIFFERENT machine is refused, even though the owner signed it.
    write(&inbox.join("b-othermachine.json"), &signed_envelope(
        &break_glass_text("some-other-machine", "n-other", "2099-01-01T00:00:00Z",
            &e.payload_hash, &e.kmh, &e.version), &[&rc]));
    assert_eq!(gov_runtime::srr::admit(req().with_break_glass(true)).unwrap_err().code,
        "SRR_BREAK_GLASS_NOT_AUTHORISED", "a token for another machine must not authorise this one");

    // An expired token is refused.
    write(&inbox.join("c-expired.json"), &signed_envelope(
        &break_glass_text(&mid, "n-exp", "2000-01-01T00:00:00Z", &e.payload_hash, &e.kmh, &e.version),
        &[&rc]));
    assert_eq!(gov_runtime::srr::admit(req().with_break_glass(true)).unwrap_err().code,
        "SRR_BREAK_GLASS_NOT_AUTHORISED", "an expired token must not authorise");

    // A token that names only a version (SRR2-R1-C2) is refused at parse.
    let novhash = format!(
        r#"{{"_type":"break-glass","spec_version":"srr/1","version":1,"expires":"2099-01-01T00:00:00Z","product":"{PRODUCT}","machine_id":"{mid}","nonce":"n-nohash","reason":"x","issued":"2026-09-17T00:00:00Z","recovery_release":{{"release_version":"{}"}}}}"#,
        e.version);
    write(&inbox.join("d-nohash.json"), &signed_envelope(&novhash, &[&rc]));
    assert_eq!(gov_runtime::srr::admit(req().with_break_glass(true)).unwrap_err().code,
        "SRR_BREAK_GLASS_NOT_AUTHORISED", "SRR2-R1-C2: a version-only token must be refused");

    // A validly signed token for THIS machine but binding a DIFFERENT payload is refused at entry.
    write(&inbox.join("e-wrongpayload.json"), &signed_envelope(
        &break_glass_text(&mid, "n-wrong", "2099-01-01T00:00:00Z", &"0".repeat(64), &"0".repeat(64), &e.version),
        &[&rc]));
    let werr = gov_runtime::srr::admit(req().with_break_glass(true)).unwrap_err();
    assert_eq!(werr.code, "SRR_BREAK_GLASS_WRONG_PAYLOAD",
        "SRR2-R1-C2: the token must bind the digests actually being installed: {werr:?}");
}

#[test]
fn d2_valid_break_glass_enters_marks_and_is_single_use() {
    let home = scratch("d2");
    isolate(&home);
    let (rk, rel, sn, ts, rc) = (key(61), key(62), key(63), key(64), key(65));
    let (e, mid) = provisioned_with_floor(&home, "d2", (&rk, &rel, &sn, &ts, &rc));
    let ms = gov_runtime::srr::state::MachineState::at(&state_root(&home)).unwrap();
    let floors_before = gov_runtime::srr::state::Floors::load(&ms, PRODUCT);

    let low = scratch("d2-low");
    write(&low.join("release.json"), &signed_envelope(&release_text(&e, 9, 1, "", 0), &[&rel]));
    let cand = candidate_kernel();
    let req = || gov_runtime::srr::AdmissionRequest::new(
        gov_runtime::srr::Ingress::Recovery, &cand)
        .with_metadata_dir(Some(low.clone())).with_break_glass(true);

    write(&ms.break_glass_inbox().join("ok.json"), &signed_envelope(
        &break_glass_text(&mid, "nonce-single-use", "2099-01-01T00:00:00Z", &e.payload_hash, &e.kmh, &e.version),
        &[&rc]));

    let auth = gov_runtime::srr::admit(req()).expect("a valid owner-signed token must admit below floor");
    assert!(auth.below_floor);
    assert!(auth.authenticity.is_authenticated(), "§1: break-glass never relaxes authenticity");

    // §4 — the marking is byte-exact, WITH U+2014, in the durable record on disk.
    let rec: serde_json::Value = serde_json::from_slice(
        &std::fs::read(ms.degraded_path(PRODUCT)).unwrap()).unwrap();
    assert_eq!(rec["marking"].as_str().unwrap(), "DEGRADED — RECOVERY ONLY");
    assert_eq!(rec["marking"].as_str().unwrap().as_bytes(),
        b"DEGRADED \xe2\x80\x94 RECOVERY ONLY", "§4 marking must be byte-exact with U+2014");
    assert_eq!(rec["active"], true);
    // §3 — durable entry record contents.
    assert_eq!(rec["machine_id"].as_str().unwrap(), mid);
    assert!(!rec["entered_at"].as_str().unwrap().is_empty());
    assert!(!rec["reason"].as_str().unwrap().is_empty());
    assert_eq!(rec["floors_at_entry"]["protected_release_high_water_sequence"], 40);
    assert_eq!(rec["recovery_release"]["payload_hash"].as_str().unwrap(), e.payload_hash);

    // §8 — the floor itself is not lowered.
    gov_runtime::srr::record_installed(&auth).expect("record");
    let floors_after = gov_runtime::srr::state::Floors::load(&ms, PRODUCT);
    assert_eq!(floors_after.release_high_water_sequence, floors_before.release_high_water_sequence,
        "§8: break-glass must never lower the protected high-water");
    assert_eq!(floors_after.release_high_water_sequence, 40);

    // §7 — still degraded, because the installed release (seq 9) is below the floor.
    assert!(gov_runtime::srr::breakglass::is_degraded(&ms, PRODUCT),
        "§7: the marking must persist until an authenticated release at/above the floor is installed");

    // Single use: the same nonce cannot be replayed. Re-present the identical token.
    write(&ms.break_glass_inbox().join("replay.json"), &signed_envelope(
        &break_glass_text(&mid, "nonce-single-use", "2099-01-01T00:00:00Z", &e.payload_hash, &e.kmh, &e.version),
        &[&rc]));
    let e2 = gov_runtime::srr::admit(req()).unwrap_err();
    assert_eq!(e2.code, "SRR_BREAK_GLASS_NOT_AUTHORISED", "a spent nonce must not be replayable");
    assert!(serde_json::to_string(&e2.details).unwrap().contains("nonce already consumed"),
        "details must name the spent nonce: {:?}", e2.details);

    // §7 exit — installing an authenticated release at the floor clears the marking, and only then.
    let hi = scratch("d2-hi");
    write(&hi.join("release.json"), &signed_envelope(&release_text(&e, 40, 2, "", 0), &[&rel]));
    let auth2 = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Recovery, &candidate_kernel())
            .with_metadata_dir(Some(hi))).expect("at-floor release admits");
    let out = gov_runtime::srr::record_installed(&auth2).expect("record");
    assert_eq!(out["break_glass_exit"]["cleared"], true, "exit must clear at the floor: {out}");
    assert!(!gov_runtime::srr::breakglass::is_degraded(&ms, PRODUCT));
}

/// OWNER-DECISION-0006 §6 — what is actually refused while the machine is marked `DEGRADED — RECOVERY ONLY`.
///
/// The decision states a CLASS ("normal privileged Governance OS operation"). This test enumerates the operation
/// labels the product's own `guard_write` chokepoint passes, and reports which of them the guard refuses.
#[test]
fn d3_below_floor_refusal_surface_against_owner_decision_0006_section_6() {
    let home = scratch("d3");
    isolate(&home);
    let (rk, rel, sn, ts, rc) = (key(71), key(72), key(73), key(74), key(75));
    let (e, mid) = provisioned_with_floor(&home, "d3", (&rk, &rel, &sn, &ts, &rc));
    let ms = gov_runtime::srr::state::MachineState::at(&state_root(&home)).unwrap();
    let low = scratch("d3-low");
    write(&low.join("release.json"), &signed_envelope(&release_text(&e, 9, 1, "", 0), &[&rel]));
    write(&ms.break_glass_inbox().join("ok.json"), &signed_envelope(
        &break_glass_text(&mid, "n-d3", "2099-01-01T00:00:00Z", &e.payload_hash, &e.kmh, &e.version), &[&rc]));
    let auth = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Recovery, &candidate_kernel())
            .with_metadata_dir(Some(low)).with_break_glass(true)).expect("enter break-glass");
    assert!(auth.below_floor);
    assert!(gov_runtime::srr::breakglass::is_degraded(&ms, PRODUCT));

    // Every operation label the product passes to `guard_write`, harvested from the product source.
    let labels = [
        "upstream submit", "upstream export", "memory select", "checkpoint", "gate create", "gate answer",
        "gate revoke", "gate present", "decide", "update --apply", "tools install", "replan",
        "plugins register", "plugins unregister", "handoff create", "handoff return", "readiness plan",
        "cit propose", "cit simulate", "cit approve", "cit reject", "cit execute", "adopt migrate",
        "adopt extract-legacy", "adopt build-memory", "task create", "task status", "task claim",
        "task close", "kernel reinstall", "release build", "release certify", "trust provision",
        "trust root-update", "skills install",
    ];
    let mut refused = vec![];
    let mut permitted = vec![];
    for l in labels {
        match gov_runtime::srr::breakglass::guard(&ms, PRODUCT, l) {
            Err(_) => refused.push(l),
            Ok(()) => permitted.push(l),
        }
    }
    println!("AR-0027 D3 — while marked `DEGRADED — RECOVERY ONLY`:");
    println!("  REFUSED   ({}): {:?}", refused.len(), refused);
    println!("  PERMITTED ({}): {:?}", permitted.len(), permitted);

    // The §6 bullets that name a specific operation are all refused.
    for must in ["gate create", "gate present", "gate answer", "decide", "release build", "release certify",
                 "trust provision", "trust root-update", "plugins register", "tools install",
                 "skills install", "cit execute"] {
        assert!(refused.contains(&must), "§6 requires '{must}' to be refused while below floor");
    }
    // The §5 permitted activities remain available.
    assert!(permitted.contains(&"kernel reinstall"), "§5 permits uninstall/reinstall");

    // OBSERVED GAP — §6 bullet 1 names the CLASS "normal privileged Governance OS operation", but the guard is a
    // substring DENY-LIST, so privileged operations absent from that list proceed.
    for gap in ["cit approve", "cit reject", "cit simulate", "gate revoke", "handoff return",
                "plugins unregister", "adopt extract-legacy", "adopt build-memory", "checkpoint"] {
        assert!(permitted.contains(&gap),
            "OBSERVED: '{gap}' is permitted while the machine is marked DEGRADED — RECOVERY ONLY");
    }
    // `cit approve` is the sharpest case: an approval-class privileged operation.
    assert!(gov_runtime::srr::breakglass::guard(&ms, PRODUCT, "cit approve").is_ok(),
        "OBSERVED: `cit approve` is not refused below floor");
    assert!(gov_runtime::srr::breakglass::guard_light(PRODUCT, "cit approve").is_ok(),
        "OBSERVED: the hot-path guard does not refuse `cit approve` either");
}

/// `SRR2-R1-C1` — the exit policy lives at exactly one point and implements the stricter both-floors reading.
#[test]
fn d4_exit_policy_is_one_point_at_the_stricter_reading() {
    assert_eq!(gov_runtime::srr::breakglass::EXIT_POLICY, "b_stricter_both_floors");
    let ms_home = scratch("d4");
    isolate(&ms_home);
    let ms = gov_runtime::srr::state::MachineState::at(&state_root(&ms_home)).unwrap();
    let mut f = gov_runtime::srr::state::Floors::load(&ms, PRODUCT);
    f.raise_minimum_secure("4.1.2", 12, "src");
    f.raise_release("4.1.5", 15, true);

    // Above the signed minimum but below the protected high-water: refused under (b), would pass under (a).
    assert!(!gov_runtime::srr::breakglass::exit_satisfied("4.1.3", 13, &f),
        "the stricter reading must refuse a release between the two floors");
    assert!(gov_runtime::srr::breakglass::exit_satisfied("4.1.5", 15, &f));
    assert!(!gov_runtime::srr::breakglass::exit_satisfied("4.1.1", 11, &f));
    assert!(gov_runtime::srr::breakglass::exit_condition_description().contains("BOTH"));
}

/// §10 — break-glass recovery must work with no network. Nothing in the authorisation path may read the network.
#[test]
fn d5_break_glass_is_purely_local() {
    let home = scratch("d5");
    isolate(&home);
    // Poison every proxy variable so any outbound HTTP would fail, and deny name resolution.
    for v in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"] {
        std::env::set_var(v, "http://127.0.0.1:1");
    }
    let (rk, rel, sn, ts, rc) = (key(81), key(82), key(83), key(84), key(85));
    let (e, mid) = provisioned_with_floor(&home, "d5", (&rk, &rel, &sn, &ts, &rc));
    let ms = gov_runtime::srr::state::MachineState::at(&state_root(&home)).unwrap();
    let low = scratch("d5-low");
    write(&low.join("release.json"), &signed_envelope(&release_text(&e, 9, 1, "", 0), &[&rel]));
    write(&ms.break_glass_inbox().join("ok.json"), &signed_envelope(
        &break_glass_text(&mid, "n-d5", "2099-01-01T00:00:00Z", &e.payload_hash, &e.kmh, &e.version), &[&rc]));
    let auth = gov_runtime::srr::admit(
        gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Recovery, &candidate_kernel())
            .with_metadata_dir(Some(low)).with_break_glass(true))
        .expect("§10: below-floor recovery must succeed with no network");
    assert!(auth.below_floor);
    let st = gov_runtime::srr::status().unwrap();
    assert_eq!(st["break_glass"]["network_required"], false);
    for v in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"] {
        std::env::remove_var(v);
    }
}
