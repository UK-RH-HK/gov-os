//! HELD-OUT INDEPENDENT R1 VERIFICATION SUITE — AR-0027 (verifier-a).
//!
//! Independently authored attack tests against the Signed Release Root v1 candidate `srr1-r1-candidate-1`
//! (work commit 949c4d343a6d5f203534afa6e3363992fee12488). The builder has not seen these.
//!
//! Run single-threaded: several scenarios manipulate process environment (`XDG_STATE_HOME`, `GOV_*`), which is
//! process-global.
//!
//!   cargo test -- --test-threads=1 --nocapture
#[path = "common/forge.rs"]
mod forge;

use forge::*;
use gov_runtime::srr::metadata::{Envelope, Release, Root};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

// ------------------------------------------------------------------------------------------------ scaffolding

fn scratch(name: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!(
        "ar0027-{}-{}-{}",
        name,
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    ));
    std::fs::create_dir_all(&d).unwrap();
    d
}

/// Strip every `GOV_*` variable and point the protected state root at a private directory, so each scenario runs
/// on its own simulated machine and nothing leaks in from the developer's environment.
fn isolate(state_home: &Path) {
    for (k, _) in std::env::vars() {
        if k.starts_with("GOV_") {
            std::env::remove_var(&k);
        }
    }
    std::env::set_var("XDG_STATE_HOME", state_home);
}

fn candidate_kernel() -> PathBuf {
    // The candidate under test: the repository's own framework payload.
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../wt/srr1-r1-verify/framework")
        .canonicalize()
        .expect("candidate framework/ must exist")
}

/// Measure the candidate exactly as the verifier will, using the product's own staging code.
fn measure(state_root: &Path) -> (String, String, BTreeMap<String, String>, String) {
    let ms = gov_runtime::srr::state::MachineState::at(state_root).unwrap();
    let staged = gov_runtime::srr::staging::stage(&ms, &candidate_kernel()).unwrap();
    (
        staged.payload_hash.clone(),
        staged.kernel_manifest_hash.clone(),
        staged.files.clone(),
        staged.version.clone(),
    )
}

fn write(p: &Path, s: &str) {
    if let Some(d) = p.parent() {
        std::fs::create_dir_all(d).unwrap();
    }
    std::fs::write(p, s).unwrap();
}

fn parse_root(file: &str) -> Result<Root, gov_runtime::GovError> {
    Root::parse(Envelope::parse(file.as_bytes(), "held-out")?)
}

// ============================================================================== A. cryptographic adapter attacks
// Frozen R1: "a mature reviewed TUF/cryptographic implementation is used correctly".

#[test]
fn a1_signature_lifted_from_a_different_document_is_refused() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    let spec = RootSpec::simple(&rk, &rel, &sn, &ts, &rc);
    let root = parse_root(&spec.file()).expect("root parses");

    let files = BTreeMap::from([("a".to_string(), "f".repeat(64))]);
    let doc_a = ReleaseSpec {
        version: 1, expires: "2099-01-01T00:00:00Z", release_version: "4.1.5", sequence: 5,
        channel: "stable", repository: "r", payload_hash: &"a".repeat(64),
        kernel_manifest_hash: &"b".repeat(64), files: &files,
        minimum_secure_release: "4.1.0", minimum_secure_sequence: 1,
    }.signed_text();
    let doc_b = ReleaseSpec {
        version: 1, expires: "2099-01-01T00:00:00Z", release_version: "9.9.9", sequence: 99,
        channel: "stable", repository: "r", payload_hash: &"c".repeat(64),
        kernel_manifest_hash: &"d".repeat(64), files: &files,
        minimum_secure_release: "4.1.0", minimum_secure_sequence: 1,
    }.signed_text();

    // A genuine signature over doc A, presented on doc B.
    let sigs_a = sign_text(&doc_a, &[&rel]);
    let forged = envelope_from_text(&doc_b, &sigs_a);
    let env = Envelope::parse(forged.as_bytes(), "forged").unwrap();
    let e = root.verify_role("release", &env).unwrap_err();
    assert_eq!(e.code, "SRR_THRESHOLD_NOT_MET", "{e:?}");

    // control: the same signature on its own document verifies, so the test is testing the right thing
    let honest = envelope_from_text(&doc_a, &sigs_a);
    let env_ok = Envelope::parse(honest.as_bytes(), "honest").unwrap();
    root.verify_role("release", &env_ok).expect("control must verify");
}

#[test]
fn a2_keyid_cannot_be_pointed_at_another_keys_material() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    let spec = RootSpec::simple(&rk, &rel, &sn, &ts, &rc);
    // Rename the release key id onto the root key's public bytes.
    let tampered = spec.signed_text().replace(&rel.public_hex, &rk.public_hex);
    let file = signed_envelope(&tampered, &[&rk]);
    let e = parse_root(&file).unwrap_err();
    assert_eq!(e.code, "SRR_KEYID_MISMATCH", "{e:?}");
}

#[test]
fn a3_role_confusion_a_timestamp_key_cannot_authorise_a_release() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    let root = parse_root(&RootSpec::simple(&rk, &rel, &sn, &ts, &rc).file()).unwrap();
    let files = BTreeMap::from([("a".to_string(), "f".repeat(64))]);
    let doc = ReleaseSpec {
        version: 1, expires: "2099-01-01T00:00:00Z", release_version: "4.1.5", sequence: 5,
        channel: "stable", repository: "r", payload_hash: &"a".repeat(64),
        kernel_manifest_hash: &"b".repeat(64), files: &files,
        minimum_secure_release: "", minimum_secure_sequence: 0,
    }.signed_text();
    // Signed, validly, by the timestamp role's key — which root does not list for `release`.
    let env = Envelope::parse(signed_envelope(&doc, &[&ts]).as_bytes(), "x").unwrap();
    let e = root.verify_role("release", &env).unwrap_err();
    assert_eq!(e.code, "SRR_THRESHOLD_NOT_MET", "{e:?}");
    // and the snapshot key cannot authorise a release either
    let env2 = Envelope::parse(signed_envelope(&doc, &[&sn]).as_bytes(), "x").unwrap();
    assert_eq!(root.verify_role("release", &env2).unwrap_err().code, "SRR_THRESHOLD_NOT_MET");
}

#[test]
fn a4_threshold_cannot_be_reached_by_repeating_one_key() {
    let (rk, r1, r2, sn, ts, rc) = (key(1), key(2), key(6), key(3), key(4), key(5));
    let mut spec = RootSpec::simple(&rk, &r1, &sn, &ts, &rc);
    spec.release_keys = vec![&r1, &r2];
    spec.release_threshold = 2; // 2-of-2
    let root = parse_root(&spec.file()).unwrap();

    let files = BTreeMap::from([("a".to_string(), "f".repeat(64))]);
    let doc = ReleaseSpec {
        version: 1, expires: "2099-01-01T00:00:00Z", release_version: "4.1.5", sequence: 5,
        channel: "stable", repository: "r", payload_hash: &"a".repeat(64),
        kernel_manifest_hash: &"b".repeat(64), files: &files,
        minimum_secure_release: "", minimum_secure_sequence: 0,
    }.signed_text();

    // One valid signature, presented four times under its own key id.
    let one = sign_text(&doc, &[&r1]);
    let repeated: Vec<(String, String)> = (0..4).map(|_| one[0].clone()).collect();
    let env = Envelope::parse(envelope_from_text(&doc, &repeated).as_bytes(), "x").unwrap();
    let e = root.verify_role("release", &env).unwrap_err();
    assert_eq!(e.code, "SRR_THRESHOLD_NOT_MET", "{e:?}");
    assert_eq!(e.details["accepted_keyids"].as_array().unwrap().len(), 1,
        "one key must count once, not four times");

    // control: two distinct authorised keys do meet the threshold
    let both = sign_text(&doc, &[&r1, &r2]);
    let env_ok = Envelope::parse(envelope_from_text(&doc, &both).as_bytes(), "x").unwrap();
    root.verify_role("release", &env_ok).expect("2-of-2 must verify");
}

#[test]
fn a5_unsatisfiable_threshold_is_refused_at_parse_time() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    let spec = RootSpec::simple(&rk, &rel, &sn, &ts, &rc);
    // release role claims threshold 3 but lists 1 key
    let t = spec.signed_text().replace(
        &format!(r#""release":{{"keyids":["{}"],"threshold":1}}"#, rel.keyid),
        &format!(r#""release":{{"keyids":["{}"],"threshold":3}}"#, rel.keyid));
    assert!(t.contains("\"threshold\":3"), "rewrite must have applied");
    let e = parse_root(&signed_envelope(&t, &[&rk])).unwrap_err();
    assert_eq!(e.code, "SRR_UNSATISFIABLE_THRESHOLD", "{e:?}");
}

#[test]
fn a6_zero_threshold_is_refused() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    let spec = RootSpec::simple(&rk, &rel, &sn, &ts, &rc);
    let t = spec.signed_text().replace(
        &format!(r#""release":{{"keyids":["{}"],"threshold":1}}"#, rel.keyid),
        &format!(r#""release":{{"keyids":["{}"],"threshold":0}}"#, rel.keyid));
    let e = parse_root(&signed_envelope(&t, &[&rk])).unwrap_err();
    assert_eq!(e.code, "SRR_METADATA_MALFORMED", "{e:?}");
    assert!(e.message.contains("threshold 0"), "{}", e.message);
}

#[test]
fn a7_trailing_bytes_after_the_envelope_are_refused() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    let file = RootSpec::simple(&rk, &rel, &sn, &ts, &rc).file();
    for suffix in ["{\"extra\":1}", "\n{}", "garbage", "\0"] {
        let mut b = file.clone().into_bytes();
        b.extend_from_slice(suffix.as_bytes());
        let e = Envelope::parse(&b, "trailing").unwrap_err();
        assert_eq!(e.code, "SRR_METADATA_MALFORMED", "suffix {suffix:?} must be refused");
    }
}

#[test]
fn a8_a_duplicate_signed_member_is_refused_rather_than_last_wins() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    let spec = RootSpec::simple(&rk, &rel, &sn, &ts, &rc);
    let good = spec.signed_text();
    let evil = good.replace("\"version\":1", "\"version\":7");
    let sigs = sign_text(&good, &[&rk]);
    // {"signed": <signed by us>, "signed": <attacker's>, "signatures": [...]}
    let two = format!(
        r#"{{"signed":{good},"signed":{evil},"signatures":[{{"keyid":"{}","sig":"{}"}}]}}"#,
        sigs[0].0, sigs[0].1
    );
    let e = Envelope::parse(two.as_bytes(), "dup").unwrap_err();
    assert_eq!(e.code, "SRR_METADATA_MALFORMED", "{e:?}");
}

#[test]
fn a9_unsigned_and_empty_signature_lists_are_refused() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    let t = RootSpec::simple(&rk, &rel, &sn, &ts, &rc).signed_text();
    let e = Envelope::parse(envelope_from_text(&t, &[]).as_bytes(), "unsigned").unwrap_err();
    assert_eq!(e.code, "SRR_METADATA_UNSIGNED", "{e:?}");
}

#[test]
fn a10_malleable_and_small_order_signatures_are_refused_by_verify_strict() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    let root = parse_root(&RootSpec::simple(&rk, &rel, &sn, &ts, &rc).file()).unwrap();
    let files = BTreeMap::from([("a".to_string(), "f".repeat(64))]);
    let doc = ReleaseSpec {
        version: 1, expires: "2099-01-01T00:00:00Z", release_version: "4.1.5", sequence: 5,
        channel: "stable", repository: "r", payload_hash: &"a".repeat(64),
        kernel_manifest_hash: &"b".repeat(64), files: &files,
        minimum_secure_release: "", minimum_secure_sequence: 0,
    }.signed_text();
    let sigs = sign_text(&doc, &[&rel]);
    let raw = hex::decode(&sigs[0].1).unwrap();

    // Malleate S by adding the group order L to the scalar half (classic ed25519 malleability).
    // verify_strict must reject the non-canonical S.
    let l: [u8; 32] = [
        0xed, 0xd3, 0xf5, 0x5c, 0x1a, 0x63, 0x12, 0x58, 0xd6, 0x9c, 0xf7, 0xa2, 0xde, 0xf9, 0xde, 0x14,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10,
    ];
    let mut s = [0u8; 32];
    s.copy_from_slice(&raw[32..]);
    let mut carry = 0u16;
    for i in 0..32 {
        let v = s[i] as u16 + l[i] as u16 + carry;
        s[i] = (v & 0xff) as u8;
        carry = v >> 8;
    }
    let mut mal = raw.clone();
    mal[32..].copy_from_slice(&s);
    let env = Envelope::parse(
        envelope_from_text(&doc, &[(sigs[0].0.clone(), hex::encode(&mal))]).as_bytes(), "mal").unwrap();
    assert_eq!(root.verify_role("release", &env).unwrap_err().code, "SRR_THRESHOLD_NOT_MET",
        "a malleated (non-canonical S) signature must not verify");

    // A malformed-length signature is refused as malformed key material rather than silently ignored.
    let short = envelope_from_text(&doc, &[(sigs[0].0.clone(), "aabb".into())]);
    let env2 = Envelope::parse(short.as_bytes(), "short").unwrap();
    assert!(root.verify_role("release", &env2).is_err());
}

#[test]
fn a11_unsupported_key_scheme_is_refused() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    let t = RootSpec::simple(&rk, &rel, &sn, &ts, &rc)
        .signed_text()
        .replacen(r#""keytype":"ed25519""#, r#""keytype":"rsa""#, 1);
    let e = parse_root(&signed_envelope(&t, &[&rk])).unwrap_err();
    assert_eq!(e.code, "SRR_UNSUPPORTED_KEY_SCHEME", "{e:?}");
}

#[test]
fn a12_spec_version_and_role_type_confusion_are_refused() {
    let (rk, rel, sn, ts, rc) = (key(1), key(2), key(3), key(4), key(5));
    // wrong spec_version
    let t = RootSpec::simple(&rk, &rel, &sn, &ts, &rc)
        .signed_text().replace(r#""spec_version":"srr/1""#, r#""spec_version":"srr/2""#);
    assert_eq!(parse_root(&signed_envelope(&t, &[&rk])).unwrap_err().code,
        "SRR_UNSUPPORTED_SPEC_VERSION");
    // a release document presented where a root is expected
    let t2 = RootSpec::simple(&rk, &rel, &sn, &ts, &rc)
        .signed_text().replace(r#""_type":"root""#, r#""_type":"release""#);
    assert_eq!(parse_root(&signed_envelope(&t2, &[&rk])).unwrap_err().code,
        "SRR_METADATA_WRONG_ROLE");
}
