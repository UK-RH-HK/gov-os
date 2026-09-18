//! AR-0029 held-out group D — `AR27-N1`: the canonical-form gate on the expiry comparison, and whether
//! fail-closed bricks legitimate operation.
mod common;
use common::mint;

use gov_runtime::srr::metadata as md;

const NOW: &str = "2026-09-18T12:00:00Z";

#[test]
fn d1_the_canonical_form_gate_accepts_exactly_the_form_the_profile_emits() {
    // What `util::now_iso` emits must pass the gate, or every comparison fails closed forever.
    let emitted = gov_runtime::util::now_iso();
    assert!(
        md::is_canonical_utc_timestamp(&emitted),
        "the profile's own clock reading '{emitted}' is rejected by its own canonical-form gate"
    );
    assert_eq!(emitted.len(), 20);

    // Everything RFC-3339 permits that this profile does not emit must be rejected.
    for bad in [
        "2099-01-01T00:00:00+00:00",
        "2099-01-01T00:00:00+14:00",
        "2099-01-01T00:00:00-11:00",
        "2099-01-01t00:00:00z",
        "2099-01-01T00:00:00z",
        "2099-01-01t00:00:00Z",
        "2099-01-01T00:00:00.000Z",
        "2099-01-01T00:00:00.5Z",
        "2099-01-01 00:00:00Z",
        "2099-01-01T00:00Z",
        "2099-01-01T00:00:00",
        "2099-01-01",
        "99-01-01T00:00:00Z",
        "+2099-01-01T00:00:00Z",
        " 2099-01-01T00:00:00Z",
        "2099-01-01T00:00:00Z ",
        "2099-01-01T00:00:00Z\n",
        "2099-01-01T00:00:00Z\0",
        "2099/01/01T00:00:00Z",
        "",
    ] {
        assert!(
            !md::is_canonical_utc_timestamp(bad),
            "OBSERVED: '{bad}' passes the canonical-form gate"
        );
        assert!(
            md::expiry_fault(bad, NOW).is_some(),
            "OBSERVED: expiry '{bad}' is not treated as expired"
        );
    }
    println!("AR-0029 D1 — canonical gate rejects every non-emitted RFC-3339 form probed");
}

#[test]
fn d2_expiry_is_fail_closed_in_all_four_directions() {
    // 1. absent
    assert!(md::expiry_fault("", NOW).is_some());
    // 2. non-canonical expires
    assert!(md::expiry_fault("2099-01-01T00:00:00+14:00", NOW).is_some());
    // 3. non-canonical clock reading
    assert!(md::expiry_fault("2099-01-01T00:00:00Z", "not-a-clock").is_some());
    assert!(md::expiry_fault("2099-01-01T00:00:00Z", "").is_some());
    // 4. canonical and at or before the clock — including the exact boundary
    assert!(md::expiry_fault(NOW, NOW).is_some(), "expires == now must be expired");
    assert!(md::expiry_fault("2026-09-18T11:59:59Z", NOW).is_some());
    // and the one case that must NOT be expired
    assert!(md::expiry_fault("2026-09-18T12:00:01Z", NOW).is_none());
    assert!(md::expiry_fault("2099-01-01T00:00:00Z", NOW).is_none());
    println!("AR-0029 D2 — fail-closed on absent, non-canonical expires, non-canonical clock and expires <= now");
}

/// Does fail-closed brick legitimate operation? A real root document signed with an ordinary future canonical
/// expiry must still verify, and the identical document with each unusual-but-valid form must not.
#[test]
fn d3_fail_closed_does_not_brick_an_ordinary_document() {
    let k = mint::Signer1::seeded(0x71);
    let now = gov_runtime::util::now_iso();

    let good = mint::root_document(1, "2099-01-01T00:00:00Z", &k);
    let env = md::Envelope::parse(good.as_bytes(), "d3-good").unwrap();
    let root = md::parse_self_signed_root(env, &now).expect("an ordinary future expiry must verify");
    assert_eq!(root.version, 1);
    assert!(!root.envelope.is_expired(&now));

    for (what, expires) in [
        ("+00:00 offset", "2099-01-01T00:00:00+00:00"),
        ("lowercase z", "2099-01-01t00:00:00z"),
        ("fractional seconds", "2099-01-01T00:00:00.000Z"),
    ] {
        let doc = mint::root_document(1, expires, &k);
        let env = md::Envelope::parse(doc.as_bytes(), "d3").unwrap();
        let e = md::parse_self_signed_root(env, &now).unwrap_err();
        assert_eq!(e.code, "SRR_METADATA_EXPIRED", "{what}");
        assert!(
            e.message.contains("canonical UTC form"),
            "{what}: the refusal must say WHY, not print a non-date as a date: {}",
            e.message
        );
    }
    println!("AR-0029 D3 — an ordinary canonical future expiry verifies; three near-forms fail closed with a reason");
}

/// The gate is syntactic, not semantic: it checks digit positions, not calendar ranges. A publisher typo can
/// therefore mint a syntactically canonical but impossible instant. Recorded as an observation, not a defect:
/// the comparison stays lexicographically sound, `expires` is inside the signed byte-string, and every failure
/// direction of a malformed value is *later*, never earlier, only for values a publisher chose.
#[test]
fn d4_the_canonical_gate_is_syntactic_only() {
    assert!(md::is_canonical_utc_timestamp("9999-99-99T99:99:99Z"));
    assert!(md::expiry_fault("9999-99-99T99:99:99Z", NOW).is_none());
    assert!(md::is_canonical_utc_timestamp("0000-00-00T00:00:00Z"));
    assert!(md::expiry_fault("0000-00-00T00:00:00Z", NOW).is_some());
    println!(
        "AR-0029 D4 — OBSERVATION (non-blocking, R2): the canonical gate validates shape, not calendar range; \
         '9999-99-99T99:99:99Z' is accepted as a future expiry. Unreachable by an adversary (the value is inside \
         the signed bytes) and orders correctly; a publisher-side lint would close it."
    );
}

/// Every product call site inherits the gate, because `Envelope::is_expired` delegates to `expiry_fault`.
#[test]
fn d5_every_expiry_consumer_inherits_the_gate() {
    let k = mint::Signer1::seeded(0x72);
    let now = gov_runtime::util::now_iso();

    // root succession candidate (metadata.rs step 5)
    let cur_text = mint::root_document(1, "2099-01-01T00:00:00Z", &k);
    let cur = md::Root::parse(md::Envelope::parse(cur_text.as_bytes(), "cur").unwrap()).unwrap();
    let k2 = mint::Signer1::seeded(0x73);
    let succ = mint::successor_root(2, "2099-01-01T00:00:00+00:00", &k, &k2);
    let e = md::accept_root_succession(
        &cur,
        md::Envelope::parse(succ.as_bytes(), "succ").unwrap(),
        &now,
    )
    .unwrap_err();
    assert_eq!(e.code, "SRR_METADATA_EXPIRED");

    // a successor with a canonical future expiry is accepted, so the gate is not simply refusing everything
    let ok = mint::successor_root(2, "2099-01-01T00:00:00Z", &k, &k2);
    let next = md::accept_root_succession(
        &cur,
        md::Envelope::parse(ok.as_bytes(), "succ-ok").unwrap(),
        &now,
    )
    .expect("a canonical successor must be accepted");
    assert_eq!(next.version, 2);
    println!("AR-0029 D5 — succession inherits the gate and still accepts a well-formed successor");
}
