//! **AR-0033 held-out verification — `AR31-B2` fail-closed, and that §5 restoration still works.**
//!
//! A control that fails closed on an undetermined subject is only correct if the recovery mode it guards can
//! still be exited. A break-glass you cannot leave is a worse defect than the one being fixed, so both halves
//! are measured here.
//!
//! Run single-threaded: these tests set process-wide environment.
mod common;
use common::*;
use gov_runtime::srr::breakglass as bg;
use gov_runtime::srr::state::{Floors, MachineState};

const ALL_EFFECTS: &[(bg::Effect, &str)] = &[
    (bg::Effect::NormalPrivilegedOperation, "normal_privileged_operation"),
    (bg::Effect::HumanGateCreate, "human_gate_create"),
    (bg::Effect::HumanGateApprove, "human_gate_approve"),
    (bg::Effect::ReleaseCertification, "release_certification"),
    (bg::Effect::TrustPolicyMutation, "trust_policy_mutation"),
    (bg::Effect::PrivilegedPluginAcquisition, "privileged_plugin_acquisition"),
    (bg::Effect::FloorLowerOrReset, "floor_lower_or_reset"),
    (bg::Effect::PresentBelowFloorReleaseAsCurrent, "present_below_floor_release_as_current"),
];

fn set_env(m: &Machine, override_dir: Option<&std::path::Path>) {
    std::env::set_var("HOME", &m.home);
    std::env::set_var("XDG_STATE_HOME", &m.home);
    match override_dir {
        Some(d) => std::env::set_var("GOV_MACHINE_STATE_DIR", d),
        None => std::env::remove_var("GOV_MACHINE_STATE_DIR"),
    }
}

fn clear_env() {
    std::env::remove_var("GOV_MACHINE_STATE_DIR");
}

/// **c1 — both enforcement points fail CLOSED when the subject cannot be determined.**
#[test]
fn c1_both_enforcement_points_fail_closed_on_an_undetermined_subject() {
    let m = machine("c1-hostile");
    m.provision();
    m.mark();
    let elsewhere = scratch("c1-elsewhere");
    set_env(&m, Some(&elsewhere));

    // the input really is the hostile one, and resolution really does refuse it
    let e = gov_runtime::srr::state::resolve_state_root().unwrap_err();
    assert_eq!(e.code, "SRR_PROTECTED_STATE_OVERRIDE_REFUSED");

    // effect level — every effect, including the one AR-0031 showed cleared all eight
    for (effect, name) in ALL_EFFECTS {
        let r = bg::guard_effect(*effect, "held-out probe");
        let err = r.err().unwrap_or_else(|| panic!("§6 {name} CLEARED under an undetermined subject"));
        assert_eq!(err.code, "SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED", "{name}: {}", err.code);
        assert_eq!(err.details["subject"], "UNDETERMINED", "{name}");
        assert_eq!(err.details["fail"], "closed", "{name}");
        assert_eq!(err.details["refused_class"], *name, "{name}: the class is not reported");
        assert!(
            err.message.contains("GOV_MACHINE_STATE_DIR"),
            "{name}: the refusal does not name the variable to unset"
        );
    }

    // operation level — every label AR-0031 drove, plus labels nobody has written
    for label in [
        "gate create", "gate answer", "plugins register", "tools install", "cit execute",
        "task create", "trust provision", "an operation invented after this verification", "",
    ] {
        let err = bg::guard_light(PRODUCT, label)
            .err()
            .unwrap_or_else(|| panic!("operation {label:?} CLEARED under an undetermined subject"));
        assert_eq!(err.code, "SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED", "{label:?}");
        assert_eq!(err.details["fail"], "closed");
    }

    // bullet 7 fails closed the same way: unknown is not "no"
    let v = gov_runtime::srr::present::presentation("held-out");
    assert_eq!(v["below_floor"], true, "an undetermined subject was presented as current");
    assert_eq!(v["presented_as"], gov_runtime::srr::present::PRESENTED_UNDETERMINED);
    assert_eq!(v["refusal_code"], "SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED");
    clear_env();
}

/// **c2 — §5 restoration is NOT blocked by the fail-closed change.**
///
/// The allow-list is consulted before any state read, in both functions, so no recovery route can be blocked by
/// a failure to resolve state. If this were not so, the fix for `AR31-B2` would have created an unexitable
/// recovery mode, which is exactly the defect the handoff asks about.
#[test]
fn c2_the_section_5_allow_list_is_consulted_before_the_state_read() {
    let m = machine("c2-allow");
    m.provision();
    m.mark();
    let elsewhere = scratch("c2-elsewhere");
    set_env(&m, Some(&elsewhere));

    // Under the SAME hostile input that refuses everything else, all four §5 routes stay open.
    for (op, activity) in bg::PERMITTED_OPERATIONS {
        bg::guard_light(PRODUCT, op)
            .unwrap_or_else(|e| panic!("§5 recovery route `{op}` ({activity}) is BLOCKED: [{}] {}", e.code, e.message));
        bg::guard_effect(bg::Effect::NormalPrivilegedOperation, op)
            .unwrap_or_else(|e| panic!("§5 route `{op}` blocked at the effect point: [{}] {}", e.code, e.message));
    }
    clear_env();

    // and with no override at all, on a genuinely marked machine, the same four are permitted and everything
    // else is refused — the allow-list is a class control, not a state-read artefact
    set_env(&m, None);
    for (op, _) in bg::PERMITTED_OPERATIONS {
        bg::guard_light(PRODUCT, op).unwrap_or_else(|e| panic!("`{op}` refused below floor: {}", e.code));
    }
    for label in ["gate create", "release build", "trust root-update", "kernel reinstall --force", "checkpoint --all"] {
        let e = bg::guard_light(PRODUCT, label).err().unwrap_or_else(|| panic!("`{label}` permitted below floor"));
        assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED", "{label}");
    }
    // exact match, never substring: a near miss of a permitted label is refused
    for near in ["checkpoint ", " checkpoint", "Checkpoint", "checkpoints", "update --apply --force", "update"] {
        assert!(bg::permitted_activity(near).is_none(), "`{near}` is permitted by a non-exact match");
    }
    assert_eq!(bg::PERMITTED_OPERATIONS.len(), 4, "the §5 allow-list changed size");
    assert_eq!(bg::REFUSAL_POLICY, "allow_list_default_refuse");
    clear_env();
}

/// **c3 — the recovery mode can still be EXITED.**
///
/// `try_exit` is the only place the marking may be cleared. It must clear when the `OWNER-DECISION-0006` §7
/// condition is met and refuse when it is not, and neither the new record-write sink nor the new floors sink may
/// stand in its way. This is the "a recovery mode you cannot exit would be a new defect" check.
#[test]
fn c3_break_glass_can_still_be_exited_and_the_exit_policy_is_unchanged() {
    let m = machine("c3-exit");
    set_env(&m, None);
    let ms: MachineState = m.ms();
    let mut floors = Floors { product: PRODUCT.into(), ..Default::default() };
    floors.raise_release("4.1.5", 15, true);
    floors.raise_minimum_secure("4.1.2", 12, "sha");
    floors.save(&ms).unwrap();
    m.mark();
    assert!(m.is_marked());

    // 1. an UNauthenticated release never clears, whatever its version
    let r = bg::try_exit(&ms, PRODUCT, 99, "9.9.9", false, &floors).unwrap().unwrap();
    assert_eq!(r["cleared"], false, "an unauthenticated release cleared break-glass");
    assert!(m.is_marked());

    // 2. an authenticated release BELOW the floor does not clear, and says why
    let r = bg::try_exit(&ms, PRODUCT, 14, "4.1.4", true, &floors).unwrap().unwrap();
    assert_eq!(r["cleared"], false, "a below-floor release cleared break-glass");
    assert_eq!(r["exit_policy"], bg::EXIT_POLICY);
    assert!(m.is_marked());

    // 3. an authenticated release at or above BOTH floors clears it — recovery is exitable
    let r = bg::try_exit(&ms, PRODUCT, 15, "4.1.5", true, &floors).unwrap().unwrap();
    assert_eq!(r["cleared"], true, "a satisfied OWNER-DECISION-0006 §7 exit did NOT clear the marking");
    assert!(!m.is_marked(), "the marking survived a satisfied exit: break-glass is unexitable");

    // 4. and the surfaces agree immediately
    assert_eq!(gov_runtime::srr::present::presentation("exit")["below_floor"], false);

    // 5. the owner-decided policy point is untouched (SRR2-R1-C1)
    assert_eq!(bg::EXIT_POLICY, "b_stricter_both_floors");
    assert!(bg::exit_satisfied("4.1.5", 15, &floors));
    assert!(!bg::exit_satisfied("4.1.5", 14, &floors));
    assert!(!bg::exit_satisfied("4.1.1", 15, &floors));
    clear_env();
}

/// **c4 — an UNREADABLE marking record is still exitable (`AR29-C1` preserved).**
#[test]
fn c4_an_unreadable_marking_is_treated_as_marked_and_can_still_be_cleared() {
    let m = machine("c4-unreadable");
    set_env(&m, None);
    let ms = m.ms();
    std::fs::create_dir_all(ms.degraded_path(PRODUCT).parent().unwrap()).unwrap();
    std::fs::write(ms.degraded_path(PRODUCT), b"this is not a record").unwrap();
    assert!(bg::is_degraded(&ms, PRODUCT), "an unreadable marking record is silently 'not marked'");
    assert_eq!(gov_runtime::srr::present::presentation("x")["below_floor"], true);
    let e = bg::guard_light(PRODUCT, "gate create").err().unwrap();
    assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED");
    // and a §5 route is still open, and the exit still clears it
    bg::guard_light(PRODUCT, "kernel reinstall").unwrap();
    let mut floors = Floors { product: PRODUCT.into(), ..Default::default() };
    floors.raise_release("4.1.0", 10, true);
    let r = bg::try_exit(&ms, PRODUCT, 10, "4.1.0", true, &floors).unwrap().unwrap();
    assert_eq!(r["cleared"], true, "an unreadable marking cannot be cleared: break-glass is unexitable");
    assert!(!bg::is_degraded(&ms, PRODUCT));
    clear_env();
}

/// **c5 — the state-carrying form was never affected and still is not.**
#[test]
fn c5_the_state_carrying_guard_resolves_nothing_and_holds_under_the_same_input() {
    let m = machine("c5-on");
    m.provision();
    m.mark();
    let elsewhere = scratch("c5-elsewhere");
    set_env(&m, Some(&elsewhere));
    let ms = m.ms(); // opened directly, not via resolution
    for (effect, name) in ALL_EFFECTS {
        if *effect == bg::Effect::NormalPrivilegedOperation {
            continue;
        }
        let e = bg::guard_effect_on(&ms, PRODUCT, *effect, "held-out")
            .err()
            .unwrap_or_else(|| panic!("guard_effect_on cleared {name}"));
        assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED", "{name}");
    }
    clear_env();
}

/// **c6 — the fail-open pattern is gone from the whole tree, and the owner-closed resolution is untouched.**
#[test]
fn c6_the_fail_open_is_gone_and_resolution_is_byte_identical() {
    let hits = census("= crate::srr::state::resolve_state_root() else", &[]);
    assert!(hits.is_empty(), "the `let ... else` fail-open pattern is back: {hits:?}");
    let hits2 = census("resolve_state_root() else", &[]);
    assert!(hits2.is_empty(), "a fail-open on state resolution is back: {hits2:?}");

    // `OWNER-DECISION-0007` §1 / `AR27-OD1`: verified but NOT graded. Compared against the base commit export.
    if let Ok(base) = std::env::var("AR0033_BASE_SRC") {
        let now = src("runtime/src/srr/state.rs");
        let then = std::fs::read_to_string(std::path::PathBuf::from(&base).join("runtime/src/srr/state.rs")).unwrap();
        for f in ["resolve_state_root", "default_state_root"] {
            let a = split("state.rs", &cut_tests(&now)).into_iter().find(|x| x.name == f).unwrap().body;
            let b = split("state.rs", &cut_tests(&then)).into_iter().find(|x| x.name == f).unwrap().body;
            assert_eq!(a, b, "`{f}` is NOT byte-identical across the repair (OWNER-DECISION-0007 §1)");
        }
        let bgn = src("runtime/src/srr/breakglass.rs");
        let bgt = std::fs::read_to_string(std::path::PathBuf::from(&base).join("runtime/src/srr/breakglass.rs")).unwrap();
        let a = split("bg", &cut_tests(&bgn)).into_iter().find(|x| x.name == "exit_satisfied").unwrap().body;
        let b = split("bg", &cut_tests(&bgt)).into_iter().find(|x| x.name == "exit_satisfied").unwrap().body;
        assert_eq!(a, b, "`exit_satisfied` is NOT byte-identical across the repair (SRR2-R1-C1)");
        println!("resolve_state_root / default_state_root / exit_satisfied: BYTE-IDENTICAL across the repair");
    }
    // the CI-runner route still works on an UNprovisioned machine (ARCH-0003 §8)
    let un = machine("c6-unprov");
    let target = scratch("c6-target");
    set_env(&un, Some(&target));
    assert_eq!(gov_runtime::srr::state::resolve_state_root().unwrap(), target);
    clear_env();
}
