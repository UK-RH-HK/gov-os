//! AR-0031 held-out group A — **the `SECTION_6_SINKS` census itself**.
//!
//! Repair 2's whole class control rests on one claim: *exactly one primitive realises each `OWNER-DECISION-0006`
//! §6 effect, and the check is inside it.* This group attacks that claim from three directions:
//!
//! * a1–a3: does each named sink actually refuse at the instant of the effect, on a marked machine?
//! * a4–a6: is the census **complete** — is there a second path to a named effect that the census does not name?
//! * a7–a8: bullets 6 and 7 claim *no primitive exists*. Is that an audited fact or an unfalsifiable assertion?
//!
//! Assertions whose message begins `OBSERVED:` pin a weakness this verifier found rather than a behaviour the
//! candidate should have. They are expected to FAIL; a failing `OBSERVED:` assertion is a finding, not a broken
//! test.
mod common;
use common::bench::{self, PRODUCT};

use gov_runtime::srr::breakglass as bg;
use gov_runtime::srr::state::MachineState;
use serde_json::json;

// ---------------------------------------------------------------------------------- a1: the sinks that exist

/// Every §6 activity has exactly one declared sink and no sink names an activity §6 does not.
#[test]
fn a1_the_census_is_a_total_function_over_the_section_6_activities() {
    assert_eq!(
        bg::SECTION_6_SINKS.len(),
        bg::REFUSED_ACTIVITIES.len(),
        "census and activity list differ in length"
    );
    for a in bg::REFUSED_ACTIVITIES {
        let n = bg::SECTION_6_SINKS.iter().filter(|(x, _)| x == a).count();
        assert_eq!(n, 1, "§6 activity '{a}' has {n} declared sinks, expected 1");
    }
    // Two of the eight declare that no primitive exists. Those are assertions about the product, not code.
    let no_primitive: Vec<&str> = bg::SECTION_6_SINKS
        .iter()
        .filter(|(_, s)| s.starts_with("no primitive"))
        .map(|(a, _)| *a)
        .collect();
    assert_eq!(
        no_primitive,
        vec![
            "floor_lower_or_reset",
            "present_below_floor_release_as_current"
        ],
        "the set of bullets claiming no primitive changed"
    );
}

/// On a marked machine every effect-level guard refuses, and the refusal quotes the right §6 bullet.
#[test]
fn a2_every_effect_guard_refuses_at_the_instant_of_the_effect() {
    let (_x, root) = bench::isolated_default_root("a2");
    bench::mark_degraded(&root, PRODUCT);
    let ms = MachineState::at(&root).unwrap();
    assert!(bg::is_degraded(&ms, PRODUCT), "harness failed to mark the machine");

    for (effect, activity) in bench::all_effects() {
        // `NormalPrivilegedOperation` is the one variant that consults the §5 allow-list; drive it with a label
        // that is not allow-listed so the comparison is like for like.
        let op = "held-out-probe";
        let r = bg::guard_effect(effect, op);
        let e = r.expect_err(&format!(
            "§6 effect '{activity}' was NOT refused below floor by guard_effect"
        ));
        assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED", "wrong refusal code for {activity}");
        assert_eq!(
            e.details["refused_class"], activity,
            "refusal for {activity} reported the wrong class"
        );
    }
}

/// The §5 allow-list is an exception to bullet 1 only. It must not open bullets 2-7.
#[test]
fn a3_an_allow_listed_operation_does_not_suspend_bullets_2_to_7() {
    let (_x, root) = bench::isolated_default_root("a3");
    bench::mark_degraded(&root, PRODUCT);

    for op in ["checkpoint", "kernel reinstall", "update --apply", "update --rollback"] {
        // bullet 1 at an allow-listed label: permitted.
        assert!(
            bg::guard_effect(bg::Effect::NormalPrivilegedOperation, op).is_ok(),
            "§5 allow-list entry '{op}' was refused at bullet 1"
        );
        // the same label carrying a bullet-2 effect: refused.
        let e = bg::guard_effect(bg::Effect::HumanGateCreate, op)
            .expect_err(&format!("'{op}' created a Human Gate below floor"));
        assert_eq!(e.details["refused_class"], "human_gate_create");
        let e = bg::guard_effect(bg::Effect::ReleaseCertification, op)
            .expect_err(&format!("'{op}' certified a release below floor"));
        assert_eq!(e.details["refused_class"], "release_certification");
    }
}

// ------------------------------------------------------------------- a4-a6: is the census COMPLETE?

/// Bullet 4's sink claims to be *the only writer of `trust/root.json`*. Verify that at the sink, and verify the
/// claim's basis: no other code in the product reaches the trust anchor path.
#[test]
fn a4_the_trust_anchor_sink_refuses_and_is_the_only_writer() {
    let (_x, root) = bench::isolated_default_root("a4");
    let ms = MachineState::at(&root).unwrap();
    bench::mark_via_product_path(&ms, PRODUCT);

    let e = ms
        .set_root_metadata(b"{\"signed\":{}}", 2, PRODUCT)
        .expect_err("a trust anchor was written below floor");
    assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED");
    assert_eq!(e.details["refused_class"], "trust_policy_mutation");
    assert!(
        !ms.root_metadata_path().exists(),
        "root.json was written despite the refusal"
    );

    // A successor anchor naming a DIFFERENT product must not step around this machine's marking.
    let e = ms
        .set_root_metadata(b"{\"signed\":{}}", 2, "some-other-product")
        .expect_err("an anchor for another product was written below floor");
    assert_eq!(e.details["refused_class"], "trust_policy_mutation");

    // The census basis: only `state.rs` (write) and `verifier.rs` (read) reach the anchor path, and nothing in
    // the product composes that path by hand.
    let reachers: Vec<String> = bench::product_sources()
        .into_iter()
        .filter(|(_, t)| t.contains("root_metadata_path()"))
        .map(|(p, _)| p)
        .collect();
    assert_eq!(
        reachers.len(),
        2,
        "the trust anchor path is reached from somewhere new: {reachers:?}"
    );
    let hand_rolled: Vec<String> = bench::product_sources()
        .into_iter()
        .filter(|(p, t)| {
            !p.ends_with("srr/state.rs") && (t.contains(r#"join("root.json")"#) || t.contains(r#""trust/root.json""#))
        })
        .map(|(p, _)| p)
        .collect();
    assert!(
        hand_rolled.is_empty(),
        "the trust anchor path is composed by hand outside `state.rs`: {hand_rolled:?}"
    );
}

/// Bullet 2 (creation)'s sink claims to be *the only constructor of a `human-gate` record*, enforced by the
/// compiler through a sealed `&Clearance`.
///
/// The compile-time guarantee is real but **scoped to the `gates` module**: `build` is private, so nothing
/// outside `gates.rs` can call it — and nothing outside `gates.rs` NEEDS to, because `new_record` + `save_record`
/// are both `pub`, `Record`'s fields are `pub`, and `Record::set` is `pub`. A gate record can therefore be minted
/// and persisted below floor without a `Clearance` ever existing.
///
/// This test does not claim such a path exists in the product today — a5 measures that separately. It measures
/// whether the *type system* prevents one, which is the claim the repair makes.
#[test]
fn a5_the_clearance_seal_does_not_cover_gate_creation_outside_the_gates_module() {
    // The seal itself is real: `Clearance` cannot be constructed here.
    let bg_rs = bench::src("runtime/src/srr/breakglass.rs");
    let clearance = bg_rs
        .split("pub struct Clearance {")
        .nth(1)
        .expect("Clearance struct")
        .split("\n}")
        .next()
        .unwrap();
    assert!(
        !clearance.contains("pub "),
        "`Clearance` gained a public field"
    );

    // And `build` really is private, so the compiler does bind every gate-raising function INSIDE `gates.rs`.
    let gates_rs = bench::src("runtime/src/orchestration/gates.rs");
    assert!(
        gates_rs.contains("\nfn build(\n"),
        "`gates::build` is no longer module-private; the seal's scope has changed"
    );
    assert!(
        gates_rs.contains("_clearance: &crate::srr::breakglass::Clearance"),
        "`gates::build` no longer requires a §6 clearance"
    );

    // But the record API that `build` itself uses is fully public, and takes no clearance. A caller outside the
    // module reaches the same durable artefact without one. Demonstrated by construction, not by assertion:
    let rec = gov_runtime::records::new_record(
        "human-gate",
        "HDG-9001",
        "minted without a Clearance",
        json!({"question": "may a gate be created below floor?", "gate_status": "PENDING"}),
    );
    assert_eq!(
        rec.rtype(),
        "human-gate",
        "a `human-gate` record was constructed outside `gates::build`, with no `Clearance` in existence"
    );
    // ... and the same is reachable by retyping any record, because `Record::set` is public.
    let mut other = gov_runtime::records::new_record("task", "T-9001", "t", json!({}));
    other.set("type", json!("human-gate"));
    assert_eq!(
        other.rtype(),
        "human-gate",
        "an existing record was retyped to `human-gate` with no `Clearance`"
    );

    // The certification test that polices this census clause greps for ONE literal. Show the literal is not the
    // property: a construction that does not spell it is invisible to that check.
    let census_test = bench::src("tests/certification/srr.rs");
    assert!(
        census_test.contains(r#"t.contains(r#"new_record("human-gate""#),
        "the census test no longer greps for the `new_record(\"human-gate\"` literal; re-derive this scenario"
    );
    let gate_type: &str = "human-gate";
    let evasive = gov_runtime::records::new_record(gate_type, "HDG-9002", "t", json!({}));
    assert_eq!(evasive.rtype(), "human-gate");

    // The census clause is therefore a source-literal property, not an effect property. Stating it as the
    // candidate would have to state it to be a class control:
    let is_effect_property = census_test.contains("record_dir_for(\"human-gate\")")
        || census_test.contains("save_record")
        || census_test.contains("Record::set");
    assert!(
        is_effect_property,
        "OBSERVED: `section_6_effects_are_enforced_inside_their_sinks` A6 polices the bullet-2 census with one \
         source grep for the literal `new_record(\"human-gate\"`. Three constructions demonstrated above reach \
         the same durable artefact without spelling it: `new_record` through a non-literal type argument, \
         `Record::set(\"type\", ...)` on any existing record, and a `Record` struct literal (all fields `pub`). \
         None needs a `Clearance`, because the compile-time guarantee binds only functions inside `gates.rs` \
         where `build` is private. No such path exists in the product today (measured: the literal occurs once), \
         so this is the census clause being weaker than its stated form, not a live bypass."
    );
}

/// a6 — the census as a whole: for each named sink, is that function the *only* product code that realises the
/// effect? Measured, per bullet, against the product's own sources.
#[test]
fn a6_no_second_primitive_realises_a_named_section_6_effect() {
    let srcs = bench::product_sources();

    // bullet 3 — release certification. `release::build` is the sink, and it is the only code that can put a
    // caller-chosen certification status into a release manifest. `update.rs` also spells
    // `"certification": {"status": ...}`, but only as the hard-coded `UNCERTIFIED` default it synthesises when
    // reading an unreleased framework source tree, which certifies nothing — so the test is written against the
    // settable status, not against the JSON key.
    let settable: Vec<String> = srcs
        .iter()
        .filter(|(_, t)| t.contains(r#""certification": {"status": certification_status"#))
        .map(|(p, _)| p.clone())
        .collect();
    assert_eq!(
        settable,
        vec!["runtime/src/release.rs".to_string()],
        "a caller-chosen release certification status is written outside `release::build`: {settable:?}"
    );
    // and nothing outside `release::build` can emit a CERTIFIED verdict at all
    let certifiers: Vec<String> = srcs
        .iter()
        .filter(|(p, t)| {
            !p.ends_with("runtime/src/update.rs") && t.contains(r#""CERTIFIED""#)
        })
        .map(|(p, _)| p.clone())
        .collect();
    assert!(
        certifiers.is_empty(),
        "a CERTIFIED literal is written outside the sink: {certifiers:?} (update.rs only compares)"
    );
    // the sink itself guards, and has exactly one caller
    assert!(bench::fn_body(&bench::src("runtime/src/release.rs"), "build")
        .contains("Effect::ReleaseCertification"));
    let build_callers: usize = srcs.iter().map(|(_, t)| t.matches("release::build(").count()).sum();
    assert_eq!(build_callers, 1, "`release::build` gained callers");

    // bullet 4 — the sole-writer claim is measured in a4.
    // bullet 5 — the census's sole-sink claim for this bullet is falsified in `hx_d::d3`; the sink has exactly
    // one caller, which is the fact that claim rests on.
    let sink_callers: Vec<String> = srcs
        .iter()
        .filter(|(p, t)| !p.ends_with("srr/plugins.rs") && t.contains("guard_acquisition("))
        .map(|(p, _)| p.clone())
        .collect();
    assert_eq!(
        sink_callers,
        vec!["runtime/src/capabilities/governance.rs".to_string()],
        "the bullet-5 sink's caller set changed: {sink_callers:?}"
    );
}

// --------------------------------------------------- a7-a8: the two bullets that claim NO primitive exists

/// Bullet 6 — "lowering or resetting the signed security floor / high-water". The claim is that `Floors` exposes
/// only monotonic raises, so no primitive can realise the effect. Test the claim, not the prose.
#[test]
fn a7_bullet_6_has_no_primitive_because_every_floor_mutator_is_a_monotonic_raise() {
    let state_rs = bench::src("runtime/src/srr/state.rs");
    let floors = state_rs
        .split("impl Floors {")
        .nth(1)
        .expect("impl Floors")
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
    // And the bullet-6 effect variant is never used outside `breakglass.rs` itself, consistent with "no
    // primitive exists": inside `breakglass.rs` it appears in `activity()` and in two of its own unit tests.
    let outside: Vec<String> = bench::product_sources()
        .into_iter()
        .filter(|(p, t)| !p.ends_with("srr/breakglass.rs") && t.contains("Effect::FloorLowerOrReset"))
        .map(|(p, _)| p)
        .collect();
    assert!(outside.is_empty(), "bullet 6 gained a call site outside breakglass.rs: {outside:?}");
}

/// Bullet 7 — "treating the below-floor release as current or fully trusted". The census asserts no primitive
/// exists **because "every reporting surface carries the marking"**. That is an empirical claim about the whole
/// product, and the repair states it did not exhaustively audit `gov status`, `gov doctor` or telemetry.
///
/// This audits them.
#[test]
fn a8_bullet_7_claims_every_reporting_surface_carries_the_marking() {
    // The claim, read off the census so this test fails if the claim is reworded.
    let claim = bg::SECTION_6_SINKS
        .iter()
        .find(|(a, _)| *a == "present_below_floor_release_as_current")
        .map(|(_, s)| *s)
        .unwrap();
    assert_eq!(claim, "no primitive: every reporting surface carries the marking");

    // The three surfaces the repair says it checked really do carry it.
    for (rel, func) in [
        ("runtime/src/status.rs", "status"),
        ("runtime/src/srr/mod.rs", "status"),
        ("runtime/src/recovery.rs", "recover"),
    ] {
        let body = bench::fn_body(&bench::src(rel), func);
        assert!(
            body.contains("Degraded::load") || body.contains("is_degraded") || body.contains("degraded"),
            "{rel}::{func} was supposed to carry the marking and does not"
        );
    }

    // The surfaces it did NOT audit. `gov doctor` reports a whole-machine health verdict beside the installed
    // framework version.
    let doctor_rs = bench::src("runtime/src/doctor.rs");
    let doctor_aware = doctor_rs.contains("breakglass")
        || doctor_rs.contains("is_degraded")
        || doctor_rs.contains("below_floor")
        || doctor_rs.contains("Degraded");
    assert!(
        doctor_aware,
        "OBSERVED: `gov doctor` (runtime/src/doctor.rs) contains no reference to the break-glass marking at all. \
         It emits `verdict` alongside `framework_version`, so on a machine marked `DEGRADED — RECOVERY ONLY` it \
         reports the below-floor release with a HEALTHY verdict and no marking beside it. §6 bullet 7's \
         `no primitive: every reporting surface carries the marking` is false."
    );

    // `gov update --check` labels the installed release `current` and can recommend doing nothing.
    let update_rs = bench::src("runtime/src/update.rs");
    let check = bench::fn_body(&update_rs, "check");
    assert!(
        !check.is_empty(),
        "`update::check` not found; re-derive this scenario"
    );
    let check_aware = check.contains("breakglass") || check.contains("is_degraded") || check.contains("degraded");
    assert!(
        check_aware,
        "OBSERVED: `update::check` (`gov update --check`) emits `\"current\": <installed version>`, \
         `\"up_to_date\"` and `\"recommendation\": \"nothing to do\"` with no reference to the marking. On a \
         marked machine this presents the below-floor release as current and tells the operator there is nothing \
         to do, which is §6 bullet 7 verbatim. It is read-only, so it never reaches `control::guard_write` and \
         nothing refuses it."
    );

    // The agent context packet — the machine-readable surface every kernel role reads.
    let ctx_rs = bench::src("runtime/src/context/mod.rs");
    let ctx_aware = ctx_rs.contains("breakglass") || ctx_rs.contains("is_degraded") || ctx_rs.contains("below_floor");
    assert!(
        ctx_aware,
        "OBSERVED: the agent context packet (`runtime/src/context/mod.rs`) carries `framework_version` with no \
         marking, so every agent reading it treats the below-floor release as the current one."
    );

    // And the effect variant that exists for this bullet is never used anywhere in the product, so nothing is
    // ever refused under bullet 7.
    let outside: Vec<String> = bench::product_sources()
        .into_iter()
        .filter(|(p, t)| {
            !p.ends_with("srr/breakglass.rs") && t.contains("Effect::PresentBelowFloorReleaseAsCurrent")
        })
        .map(|(p, _)| p)
        .collect();
    assert!(
        !outside.is_empty(),
        "OBSERVED: `Effect::PresentBelowFloorReleaseAsCurrent` has no call site anywhere in the product outside \
         `breakglass.rs` itself, where it appears only in the enum, in `activity()` and in two unit tests. \
         Bullet 7 is declared, named, and reportable, and is enforced nowhere — so the census's \
         `no primitive: every reporting surface carries the marking` is the only thing standing behind it, and \
         the surfaces measured above falsify it."
    );
}
