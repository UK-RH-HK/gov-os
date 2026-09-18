//! AR-0031 held-out group B — **the fail-open in `guard_effect` / `guard_light`**.
//!
//! Both enforcement points resolve the protected state root themselves and, when that resolution returns `Err`,
//! return `Ok` — permitting the effect. The repair calls this "the ungoverned/unprovisioned case, not a degraded
//! one", inherited from repair 1, and says closing it would require changing machine-state root resolution, which
//! `OWNER-DECISION-0007` §1 puts out of scope.
//!
//! This group tests all three of those characterisations:
//!
//! * b1 — **when does `resolve_state_root()` actually return `Err`?** If the unprovisioned case returns `Ok`, the
//!   stated justification does not describe the branch it justifies.
//! * b2/b3 — is the fail-open reachable on a machine that IS marked, without any code change?
//! * b4 — what does it let through: which §6 bullets lose their enforcement point entirely?
//! * b5 — does the state-carrying form (`guard_effect_on`) share the defect?
//! * b6 — would closing it require touching `resolve_state_root`?
//!
//! `OBSERVED:` assertions pin a weakness and are expected to FAIL.
mod common;
use common::bench::{self, PRODUCT};

use gov_runtime::srr::breakglass as bg;
use gov_runtime::srr::state::{self, MachineState};

/// b1 — enumerate every input to `resolve_state_root()` and record which ones return `Err`.
///
/// The fail-open branch is justified in the source as "no protected machine state resolves here ... the
/// ungoverned/unprovisioned case". Measure whether that is what the `Err` branch means.
#[test]
fn b1_resolve_state_root_errors_only_on_the_hostile_case_never_on_the_unprovisioned_one() {
    // 1. Unprovisioned, no override: Ok.
    let (_x1, root1) = bench::isolated_default_root("b1-unprov");
    assert!(
        state::resolve_state_root().is_ok(),
        "unprovisioned machine with no override should resolve"
    );
    assert!(!root1.join("trust").join("provisioned.json").exists());

    // 2. Unprovisioned, override set: Ok (this is the documented CI-runner mechanism).
    let alt = bench::scratch("b1-alt");
    std::env::set_var("GOV_MACHINE_STATE_DIR", &alt);
    assert!(
        state::resolve_state_root().is_ok(),
        "unprovisioned machine with an override should resolve to the override"
    );

    // 3. Provisioned, no override: Ok.
    bench::strip_env();
    let (_x2, root2) = bench::isolated_default_root("b1-prov");
    bench::set_provisioned(&root2);
    assert!(
        state::resolve_state_root().is_ok(),
        "provisioned machine with no override should resolve"
    );

    // 4. Provisioned, override set to a DIFFERENT path: Err.
    let alt2 = bench::scratch("b1-alt2");
    std::env::set_var("GOV_MACHINE_STATE_DIR", &alt2);
    let e = state::resolve_state_root()
        .expect_err("a provisioned machine must refuse an override that relocates it");
    assert_eq!(e.code, "SRR_PROTECTED_STATE_OVERRIDE_REFUSED");

    bench::strip_env();

    // So: the ONLY input that produces `Err` is case 4 — an environment variable attempting to relocate an
    // already-provisioned machine's protected floors. That is the adversarial case the product names and
    // refuses, not an ungoverned machine.
    let bg_rs = bench::src("runtime/src/srr/breakglass.rs");
    let justification_is_accurate = !bg_rs.contains("the ungoverned/unprovisioned case, not a degraded one");
    assert!(
        justification_is_accurate,
        "OBSERVED: `guard_light` and `guard_effect` justify returning `Ok` on a `resolve_state_root()` error as \
         \"the ungoverned/unprovisioned case, not a degraded one\". Measured above: the unprovisioned case \
         returns `Ok(default)` and never reaches that branch. The ONLY input that reaches it is \
         `SRR_PROTECTED_STATE_OVERRIDE_REFUSED` — GOV_MACHINE_STATE_DIR set so as to relocate a PROVISIONED \
         machine. The guards therefore fail open on precisely the input the product has already classified as \
         hostile."
    );
}

/// b2 — with a genuinely marked machine, set the override and watch every effect-level §6 check return `Ok`.
#[test]
fn b2_an_environment_variable_suppresses_every_effect_level_section_6_check() {
    let (_x, root) = bench::isolated_default_root("b2");
    bench::set_provisioned(&root);
    bench::mark_degraded(&root, PRODUCT);

    // The machine is marked, and while the override is unset every effect is refused.
    let ms = MachineState::at(&root).unwrap();
    assert!(bg::is_degraded(&ms, PRODUCT), "harness failed to mark the machine");
    for (effect, activity) in bench::all_effects() {
        assert!(
            bg::guard_effect(effect, "held-out-probe").is_err(),
            "baseline: '{activity}' should be refused on a marked machine"
        );
    }

    // Now set GOV_MACHINE_STATE_DIR to any other path. Nothing about the machine changes: the marking record is
    // still there, `Degraded::load` still reports it through a `MachineState`, the floors are untouched.
    let alt = bench::scratch("b2-alt");
    std::env::set_var("GOV_MACHINE_STATE_DIR", &alt);
    assert!(
        bg::is_degraded(&ms, PRODUCT),
        "the machine is still marked; only the ambient environment changed"
    );

    let mut permitted: Vec<&str> = vec![];
    for (effect, activity) in bench::all_effects() {
        if bg::guard_effect(effect, "held-out-probe").is_ok() {
            permitted.push(activity);
        }
    }
    bench::strip_env();

    assert!(
        permitted.is_empty(),
        "OBSERVED: with `GOV_MACHINE_STATE_DIR` set on a provisioned, MARKED machine, `guard_effect` returns \
         `Ok` for these §6 effects instead of refusing them: {permitted:?}. `resolve_state_root()` returns \
         `SRR_PROTECTED_STATE_OVERRIDE_REFUSED`, and the guard converts that refusal into a clearance. No code \
         change, no signing key, no owner authorisation — one environment variable that `REFUSED_AUTHORITY_ENV` \
         does not list."
    );
}

/// b3 — the operation-level guard shares the defect, so the two enforcement points fail open together.
#[test]
fn b3_the_operation_level_guard_fails_open_on_the_same_input() {
    let (_x, root) = bench::isolated_default_root("b3");
    bench::set_provisioned(&root);
    bench::mark_degraded(&root, PRODUCT);

    // Baseline: a non-allow-listed operation is refused.
    assert!(
        bg::guard_light(PRODUCT, "gate answer").is_err(),
        "baseline: `gate answer` should be refused on a marked machine"
    );

    let alt = bench::scratch("b3-alt");
    std::env::set_var("GOV_MACHINE_STATE_DIR", &alt);
    let now_permitted: Vec<&str> = [
        "gate create",
        "gate answer",
        "plugins register",
        "tools install",
        "cit execute",
        "task create",
        "trust provision",
    ]
    .into_iter()
    .filter(|op| bg::guard_light(PRODUCT, op).is_ok())
    .collect();
    bench::strip_env();

    assert!(
        now_permitted.is_empty(),
        "OBSERVED: `guard_light` — the §6 bullet 1 chokepoint every mutating governed operation reaches through \
         `control::guard_write` — also returns `Ok` for {now_permitted:?} under the same environment variable. \
         Both of the candidate's two enforcement points fail open on the same input, so an operation that \
         carries a §6 bullet 2-7 effect loses BOTH checks at once."
    );
}

/// b4 — what this actually costs, bullet by bullet. `gates::create_system` is the sharpest case: the repair
/// deliberately left it with no operation-level guard, because the sink was supposed to be sufficient.
#[test]
fn b4_gate_creation_loses_its_only_enforcement_point() {
    let gates_rs = bench::src("runtime/src/orchestration/gates.rs");
    let create_system = bench::fn_body(&gates_rs, "create_system");
    assert!(
        !create_system.is_empty(),
        "`gates::create_system` not found; re-derive this scenario"
    );
    // The repair's design: no operation guard here, the sink carries §6.
    assert!(
        !create_system.contains("guard_write"),
        "`create_system` gained an operation-level guard; re-derive this scenario"
    );
    assert!(
        create_system.contains("Effect::HumanGateCreate"),
        "`create_system` no longer asks §6"
    );

    // So on this path `guard_effect` is the ONLY §6 control. Measure it under the override.
    let (_x, root) = bench::isolated_default_root("b4");
    bench::set_provisioned(&root);
    bench::mark_degraded(&root, PRODUCT);
    assert!(
        bg::guard_effect(bg::Effect::HumanGateCreate, "gate create (system)").is_err(),
        "baseline: system gate creation should be refused on a marked machine"
    );

    let alt = bench::scratch("b4-alt");
    std::env::set_var("GOV_MACHINE_STATE_DIR", &alt);
    let cleared = bg::guard_effect(bg::Effect::HumanGateCreate, "gate create (system)").is_ok();
    // A clearance is exactly what `gates::build` demands, and `build` performs no further §6 check.
    let build = bench::fn_body(&gates_rs, "build");
    let build_rechecks = build.contains("guard_effect") || build.contains("is_degraded");
    bench::strip_env();

    assert!(
        !cleared || build_rechecks,
        "OBSERVED: `gates::create_system` has no operation-level guard by design, so `guard_effect` is its only \
         §6 control. Under `GOV_MACHINE_STATE_DIR` that guard issues a `Clearance` on a marked machine, and \
         `gates::build` — which takes the `&Clearance` as proof the question was asked — performs no further \
         check. A Human Gate is therefore created below floor, which is `OWNER-DECISION-0006` §6 bullet 2, and \
         `gates::answer` loses its check on the same input, so the gate can then be approved below floor too. \
         An environment variable has created an approval."
    );
}

/// b5 — the state-carrying form does NOT share the defect, which is the proof that the defect is in the
/// resolution, not in the decision.
#[test]
fn b5_the_state_carrying_guard_is_immune_because_it_resolves_nothing() {
    let (_x, root) = bench::isolated_default_root("b5");
    bench::set_provisioned(&root);
    let ms = MachineState::at(&root).unwrap();
    bench::mark_via_product_path(&ms, PRODUCT);

    let alt = bench::scratch("b5-alt");
    std::env::set_var("GOV_MACHINE_STATE_DIR", &alt);

    // `guard_effect_on` takes the `MachineState`, so there is nothing to resolve and nothing to fail open on.
    let e = bg::guard_effect_on(&ms, PRODUCT, bg::Effect::TrustPolicyMutation, "trust anchor write")
        .expect_err("guard_effect_on must still refuse under the override");
    assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED");

    // And therefore §6 bullet 4 — the one sink that uses the state-carrying form — holds under the same input
    // that opens bullets 2, 3 and 5.
    let e = ms
        .set_root_metadata(b"{\"signed\":{}}", 9, PRODUCT)
        .expect_err("set_root_metadata must still refuse under the override");
    assert_eq!(e.details["refused_class"], "trust_policy_mutation");
    bench::strip_env();
}

/// b6 — would closing the fail-open require the change `OWNER-DECISION-0007` §1 put out of scope?
///
/// `AR27-OD1` is about how the machine-state root is *derived* (`XDG_STATE_HOME`/`HOME`). The fail-open is in how
/// the two guards *handle an error from* that derivation. Verify the owner-closed functions are untouched, and
/// that the fail-open lives entirely in `breakglass.rs`.
#[test]
fn b6_closing_the_fail_open_does_not_touch_the_owner_closed_resolution() {
    let state_rs = bench::src("runtime/src/srr/state.rs");
    let bg_rs = bench::src("runtime/src/srr/breakglass.rs");

    // The owner-closed derivation is exactly where it was: `default_state_root` reads XDG_STATE_HOME then HOME.
    let dsr = bench::fn_body(&state_rs, "default_state_root");
    assert!(
        dsr.contains("XDG_STATE_HOME") && dsr.contains("HOME"),
        "`default_state_root` no longer derives from XDG_STATE_HOME/HOME (AR27-OD1 is owner-closed)"
    );
    // `resolve_state_root` still has exactly one error return, and it is the override refusal.
    let rsr = bench::fn_body(&state_rs, "resolve_state_root");
    assert_eq!(
        rsr.matches("Err(").count(),
        1,
        "`resolve_state_root` gained or lost an error path; re-derive this scenario"
    );
    assert!(rsr.contains("SRR_PROTECTED_STATE_OVERRIDE_REFUSED"));

    // The fail-open is two `let ... else { return Ok(...) }` blocks in breakglass.rs and nowhere else.
    let fail_open_sites = bg_rs.matches("let Ok(root) = crate::srr::state::resolve_state_root() else {").count();
    assert_eq!(
        fail_open_sites, 2,
        "expected the fail-open in exactly `guard_light` and `guard_effect`; found {fail_open_sites}"
    );
    let elsewhere: Vec<String> = bench::product_sources()
        .into_iter()
        .filter(|(p, t)| {
            !p.ends_with("srr/breakglass.rs")
                && t.contains("let Ok(root) = crate::srr::state::resolve_state_root() else {")
        })
        .map(|(p, _)| p)
        .collect();
    assert!(elsewhere.is_empty(), "the fail-open pattern appears elsewhere: {elsewhere:?}");

    // Therefore the repair statement under test — that closing this would mean changing machine-state root
    // resolution — is a statement about two lines in `breakglass.rs`, not about `state.rs`.
    assert!(
        bg_rs.contains("AR27-OD1 is out of scope"),
        "the repair's out-of-scope justification is no longer in the source; re-derive this scenario"
    );
}
