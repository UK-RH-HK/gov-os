//! AR-0029 held-out group E — `AR27-N2`: is the `ROOT_EXPIRY_PROFILE` reasoning sound, and is the state still
//! reported honestly?
//!
//! The repair removed the false claim rather than implementing the control, and justified that with: barring an
//! expired root from signing its successor would make root rotation permanently impossible, because `provision`
//! refuses to re-anchor a provisioned machine. These tests measure both limbs of that argument on the candidate
//! instead of taking it on trust, and check that what the profile says is enforced, is.
mod common;
use common::mint;

use gov_runtime::srr::metadata as md;
use gov_runtime::srr::verifier;

const PRODUCT: &str = mint::PRODUCT;

/// An anchor that has since expired: provisioned honestly when it was valid, expired against today's clock.
fn expired_anchor_machine(tag: &str) -> (mint::Machine, mint::Signer1) {
    let m = mint::scenario(tag);
    m.activate();
    let k = mint::Signer1::seeded(0x81);
    // 2020 is in the past against any plausible run clock; `provision_with` writes the protected anchor exactly
    // as `set_root_metadata` does, without going through the first-provisioning expiry refusal — which is the
    // point: this models a machine whose anchor expired AFTER it was provisioned, the only way this state arises.
    m.provision_with(&mint::root_document(1, "2020-01-01T00:00:00Z", &k));
    (m, k)
}

#[test]
fn e1_the_profile_is_honest_about_what_an_expired_anchor_does_not_bar() {
    let (m, _k) = expired_anchor_machine("e1");
    let ms = m.open();
    let now = gov_runtime::util::now_iso();

    assert_eq!(verifier::ROOT_EXPIRY_PROFILE, "reported_not_admission_blocking_r1");

    // claim: an expired installed anchor does not bar loading the trust anchor
    let root = verifier::trusted_root(&ms, &now).unwrap().expect("anchor loads");
    assert!(
        root.envelope.is_expired(&now),
        "scenario precondition: the anchor is expired against the local clock"
    );

    // claim: the state is REPORTED
    let status = gov_runtime::srr::status().unwrap();
    assert_eq!(status["trust_anchor"]["expired_against_local_clock"], true);
    assert_eq!(status["trust_anchor"]["version"], 1);
    println!(
        "AR-0029 E1 — expired anchor: trusted_root() loads it, `gov trust status` reports \
         expired_against_local_clock = {} and expires = {}",
        status["trust_anchor"]["expired_against_local_clock"], status["trust_anchor"]["expires"]
    );

    // and nothing in the reporting surface calls it current or fully trusted
    let s = serde_json::to_string(&status).unwrap();
    assert!(
        !s.contains("\"authenticity\":\"AUTHENTIC\"") || status["installed_release"].is_null(),
        "no authenticity claim may be manufactured from an expired anchor with nothing installed"
    );
}

/// Limb 1 of the repair's argument, measured: with the profile as implemented, a machine whose anchor has
/// expired CAN still rotate its root.
#[test]
fn e2_root_rotation_is_possible_under_the_implemented_profile() {
    let (m, k1) = expired_anchor_machine("e2");
    let k2 = mint::Signer1::seeded(0x82);
    let anchor = m.home.join("oob").join("root2.json");
    // the successor itself must be fresh — that check IS enforced
    mint::write(&anchor, &mint::successor_root(2, "2099-01-01T00:00:00Z", &k1, &k2));

    let out = gov_runtime::srr::provision::root_update(&anchor, None)
        .expect("rotation from an expired anchor must be possible");
    assert_eq!(out["from_version"], 1);
    assert_eq!(out["to_version"], 2);
    println!(
        "AR-0029 E2 — rotation from an EXPIRED anchor succeeded: v{} -> v{}, revoked {} key(s)",
        out["from_version"], out["to_version"],
        out["revoked_keyids"].as_array().map(|a| a.len()).unwrap_or(0)
    );

    // and an expired SUCCESSOR is still refused, so freshness is enforced where the profile says it is
    let (m2, j1) = expired_anchor_machine("e2b");
    let j2 = mint::Signer1::seeded(0x83);
    let stale = m2.home.join("oob").join("root2-stale.json");
    mint::write(&stale, &mint::successor_root(2, "2020-06-01T00:00:00Z", &j1, &j2));
    let e = gov_runtime::srr::provision::root_update(&stale, None).unwrap_err();
    assert_eq!(e.code, "SRR_METADATA_EXPIRED");
    println!("AR-0029 E2 — an expired SUCCESSOR root is refused: {}", e.code);
}

/// Limb 2 of the repair's argument, measured: the alternative really would be a dead end, because the only other
/// door — re-provisioning — is closed on a provisioned machine.
#[test]
fn e3_the_alternative_would_make_rotation_permanently_impossible() {
    let (m, _k1) = expired_anchor_machine("e3");
    let fresh = mint::Signer1::seeded(0x84);
    let anchor = m.home.join("oob").join("fresh.json");
    mint::write(&anchor, &mint::root_document(1, "2099-01-01T00:00:00Z", &fresh));

    let e = gov_runtime::srr::provision::provision(&anchor, None).unwrap_err();
    assert_eq!(
        e.code, "SRR_ALREADY_PROVISIONED",
        "re-anchoring must be refused, or the repair's dead-end argument does not hold"
    );
    println!(
        "AR-0029 E3 — re-provisioning a provisioned machine is refused ({}), so if `trusted_root` barred an \
         expired anchor there would be no remaining path to rotate it. The repair's reasoning holds.",
        e.code
    );
}

/// The things the profile says ARE enforced, are.
#[test]
fn e4_the_enforced_half_of_the_profile_is_real() {
    let now = gov_runtime::util::now_iso();
    let k = mint::Signer1::seeded(0x85);

    // first provisioning refuses an expired root
    let m = mint::scenario("e4");
    m.activate();
    let stale = m.home.join("oob").join("stale-root.json");
    mint::write(&stale, &mint::root_document(1, "2020-01-01T00:00:00Z", &k));
    let e = gov_runtime::srr::provision::provision(&stale, None).unwrap_err();
    assert_eq!(e.code, "SRR_METADATA_EXPIRED");

    // parse_self_signed_root refuses it directly too
    let env = md::Envelope::parse(
        mint::root_document(1, "2020-01-01T00:00:00Z", &k).as_bytes(),
        "e4",
    )
    .unwrap();
    assert_eq!(
        md::parse_self_signed_root(env, &now).unwrap_err().code,
        "SRR_METADATA_EXPIRED"
    );
    println!("AR-0029 E4 — first provisioning and self-signed parse both refuse an expired root");
}

/// `trusted_root` must not branch on expiry — a branch whose arms are identical asserts a control that does not
/// exist, which is what `AR27-N2` was. Read off the candidate's source.
#[test]
fn e5_trusted_root_carries_no_vestigial_expiry_branch() {
    let src = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../wt/srr1-r1-verify-2/runtime/src/srr/verifier.rs");
    let text = std::fs::read_to_string(&src).unwrap();
    let body = text.split("pub fn trusted_root").nth(1).unwrap();
    let body = &body[..body.find("\n}").unwrap()];
    assert!(
        !body.contains("if root.envelope.is_expired") && !body.contains("if env.is_expired"),
        "OBSERVED: a branch on anchor expiry is back in `trusted_root`"
    );
    assert!(
        body.contains("ROOT_EXPIRY_PROFILE"),
        "the function must name the profile it implements"
    );
    // and the profile constant states the not-enforced half explicitly rather than implying it
    let doc = text.split("pub const ROOT_EXPIRY_PROFILE").next().unwrap();
    assert!(doc.contains("Not enforced"), "the profile must state what it does not bar");
    println!("AR-0029 E5 — no vestigial branch; the profile names itself at the site and states both halves");
}

/// An expired anchor still admits releases — the profile says so, and it must not silently do the opposite
/// either. Measured at the level the profile speaks about.
#[test]
fn e6_an_expired_anchor_does_not_bar_verifying_release_metadata_against_it() {
    let (m, k) = expired_anchor_machine("e6");
    let ms = m.open();
    let now = gov_runtime::util::now_iso();
    let root = verifier::trusted_root(&ms, &now).unwrap().unwrap();

    // a release-role signature made by a key the expired root delegates still verifies against it
    let signed = format!(
        r#"{{"_type":"release","spec_version":"srr/1","product":"{PRODUCT}","version":1,"expires":"2099-01-01T00:00:00Z"}}"#
    );
    let env = md::Envelope::parse(mint::envelope(&signed, &[&k]).as_bytes(), "e6").unwrap();
    let accepted = root.verify_role("release", &env).unwrap();
    assert_eq!(accepted.len(), 1);
    println!(
        "AR-0029 E6 — an expired anchor still authorises its delegated roles ({} signature accepted), which is \
         exactly what ROOT_EXPIRY_PROFILE = \"{}\" declares. Reported, not admission-blocking.",
        accepted.len(),
        verifier::ROOT_EXPIRY_PROFILE
    );
}
