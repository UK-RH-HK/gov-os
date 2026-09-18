//! AR-0031 held-out group C — **the three prior-evidence changes**, verified rather than taken on trust.
//!
//! 1. `ho_f_preservation` no longer compiles; its six unrelated checks were reproduced in the product suite as
//!    `the_no_bypass_and_no_signing_preservation_census_still_holds`. c1–c3 check the migration **assertion by
//!    assertion** and reproduce anything that was dropped.
//! 2. `ho_b::b3` and `::b6` flipped from passing to failing. c4 re-derives b3's §6 census for candidate 3 rather
//!    than reading b3's stale printed one; c5 checks b6's new statement.
//! 3. `ho_b::b4` was briefly broken and the cause reverted. c6 verifies **both halves**.
//!
//! `OBSERVED:` assertions pin a weakness and are expected to FAIL.
mod common;
use common::bench::{self, PRODUCT};

use gov_runtime::srr::breakglass as bg;

// --------------------------------------------------------- 1. was the ho_f census weakened in the move?

/// c1 — the migration, assertion by assertion. `ho_f` is committed evidence and must not be edited, so its text
/// is read and its assertions are enumerated against the product-suite test that replaced it.
#[test]
fn c1_the_migrated_preservation_census_is_compared_assertion_by_assertion() {
    let ho_f = bench::src("release/verification/4.1.6-r1-2/evidence/heldout-tests/ho_f_preservation.rs");
    let suite = bench::src("tests/certification/srr.rs");
    let migrated = bench::fn_body(&suite, "the_no_bypass_and_no_signing_preservation_census_still_holds");
    assert!(
        !migrated.is_empty(),
        "`the_no_bypass_and_no_signing_preservation_census_still_holds` not found in the product suite"
    );

    // f4 is the one that is SUPPOSED to be gone: it is the literal `AR29-N1` asked to be made impossible.
    assert!(
        ho_f.contains("fn f4_authenticated_release_is_not_type_constructor_enforced"),
        "ho_f::f4 is missing from the committed evidence"
    );
    assert!(
        !migrated.contains("AuthenticatedRelease {"),
        "the migrated census reintroduced the f4 struct literal"
    );

    // f3 — reproduced in full: five/five, typed `install_kernel`, no path-taking variant.
    for needle in [
        r#"srr::admit("#,
        "install_kernel(&",
        "admit call sites",
        "install_kernel call sites",
        "pub fn install_kernel_from_path",
    ] {
        assert!(
            migrated.contains(needle),
            "f3 lost `{needle}` in the move"
        );
    }

    // f5 — reproduced in full: the same six forbidden tokens, both directions.
    for forbidden in ["srr::admit", "AuthenticatedRelease", "Authenticity", "breakglass", "below_floor", "Floors"] {
        assert!(
            migrated.contains(&format!("\"{forbidden}\"")),
            "f5 lost the `{forbidden}` D-0007 independence token in the move"
        );
    }
    assert!(migrated.contains("fn admit_inner"), "f5 lost the reverse-direction check");

    // f7 — reproduced in full, including the unauthenticated-observation case.
    assert!(
        migrated.contains("raise_release(\"9.9.9\", 999, false)"),
        "f7 lost the unauthenticated-observation case in the move"
    );

    // f1 — STRENGTHENED on its static half: `ho_f` only printed the bare `.verify(` census, the migrated test
    // asserts it empty. Record that explicitly so the move is not scored as a pure loss.
    let f1 = &ho_f[ho_f.find("fn f1_the_permissive").unwrap()..ho_f.find("fn f2_no_signing").unwrap()];
    assert!(
        !f1.contains("assert!(callers.is_empty()"),
        "ho_f::f1 did assert the bare-verify census after all; re-derive this comparison"
    );
    assert!(
        migrated.contains("permissive.is_empty()"),
        "the migrated census dropped the bare-`.verify(` assertion"
    );
}

/// c2 — `ho_f::f1`'s **behavioural** half was not reproduced: the product suite cannot sign, so the malleated
/// S+L signature case disappeared from the running evidence when `ho_f` stopped compiling.
///
/// This verifier reproduces it, so the assurance survives the migration.
#[test]
fn c2_the_dropped_malleability_check_is_reproduced_and_still_holds() {
    let suite = bench::src("tests/certification/srr.rs");
    let migrated = bench::fn_body(&suite, "the_no_bypass_and_no_signing_preservation_census_still_holds");
    let reproduced = migrated.contains("verify_strict(") && migrated.contains("malleat");
    assert!(
        reproduced,
        "OBSERVED: `ho_f::f1`'s behavioural half — a malleated S+L signature must be refused by BOTH \
         `crypto::verify` and `crypto::verify_strict`, with the same error code — was not reproduced when the \
         census moved into the product suite. `ho_f` no longer compiles, so that check runs nowhere in the \
         candidate's evidence. It is reproduced below by this verifier; the underlying property still holds, so \
         this is a loss of assurance coverage, not a live defect."
    );
}

/// The property itself, measured here because nothing else measures it any more.
#[test]
fn c2b_verify_and_verify_strict_are_one_behaviour_on_a_non_canonical_scalar() {
    use ed25519_dalek::{Signer, SigningKey};

    let sk = SigningKey::from_bytes(&[0x5au8; 32]);
    let public = hex::encode(sk.verifying_key().to_bytes());
    let msg = b"AR-0031 c2b";
    let sig = hex::encode(sk.sign(msg).to_bytes());

    gov_runtime::srr::crypto::verify(&public, &sig, msg).expect("a good signature must verify");
    gov_runtime::srr::crypto::verify_strict(&public, &sig, msg).expect("and must verify strictly");

    // S + L: the classic non-canonical scalar the permissive ed25519 verifier accepts and the strict one refuses.
    let mut raw = hex::decode(&sig).unwrap();
    let l: [u8; 32] = [
        0xed, 0xd3, 0xf5, 0x5c, 0x1a, 0x63, 0x12, 0x58, 0xd6, 0x9c, 0xf7, 0xa2, 0xde, 0xf9, 0xde,
        0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x10,
    ];
    let mut carry = 0u16;
    for i in 0..32 {
        let s = raw[32 + i] as u16 + l[i] as u16 + carry;
        raw[32 + i] = (s & 0xff) as u8;
        carry = s >> 8;
    }
    let malleated = hex::encode(&raw);
    let a = gov_runtime::srr::crypto::verify(&public, &malleated, msg);
    let b = gov_runtime::srr::crypto::verify_strict(&public, &malleated, msg);
    assert!(
        a.is_err() && b.is_err(),
        "a malleated S+L signature was accepted: verify={a:?} verify_strict={b:?}"
    );
    assert_eq!(
        a.unwrap_err().code,
        b.unwrap_err().code,
        "the two entry points disagree on a malleated signature"
    );
}

/// c3 — `ho_f::f2`'s second half (no relaxation switch anywhere in product source) was also not reproduced.
/// Reproduced here, and the property still holds.
#[test]
fn c3_the_dropped_relaxation_switch_census_is_reproduced_and_still_holds() {
    let suite = bench::src("tests/certification/srr.rs");
    let migrated = bench::fn_body(&suite, "the_no_bypass_and_no_signing_preservation_census_still_holds");
    let reproduced = migrated.contains("skip_verify") || migrated.contains("allow_unsigned");
    assert!(
        reproduced,
        "OBSERVED: `ho_f::f2`'s second half — no `skip_verify` / `allow_unsigned` / `force_unsigned` relaxation \
         switch appears anywhere in product source outside `REFUSED_AUTHORITY_ENV` — was not reproduced in the \
         move. `grep -rn 'skip_verify|allow_unsigned|force_unsigned' tests/` finds nothing, so this check runs \
         nowhere in the candidate's evidence. Reproduced below; the property still holds."
    );
}

#[test]
fn c3b_no_relaxation_switch_exists_in_product_source() {
    for (path, text) in bench::product_sources() {
        for needle in ["skip_verify", "skip-verify", "allow_unsigned", "allow-unsigned", "force_unsigned"] {
            let Some(i) = text.find(needle) else { continue };
            let ctx = &text[i.saturating_sub(160)..(i + 80).min(text.len())];
            assert!(
                ctx.contains("REFUSED_AUTHORITY_ENV")
                    || ctx.contains("GOV_SKIP_VERIFY")
                    || ctx.contains("GOV_ALLOW_UNSIGNED"),
                "'{needle}' appears at {path} outside the refused-authority list"
            );
        }
    }
}

// ------------------------------------------------- 2. re-derive b3's census; check b6's new statement

/// c4 — `ho_b::b3` prints a §6 enforcement-point census taken on **candidate 2**. It is stale. Re-derive it.
#[test]
fn c4_the_section_6_enforcement_point_census_re_derived_on_candidate_3() {
    let provision_rs = bench::src("runtime/src/srr/provision.rs");
    let gates_rs = bench::src("runtime/src/orchestration/gates.rs");
    let release_rs = bench::src("runtime/src/release.rs");
    let state_rs = bench::src("runtime/src/srr/state.rs");
    let tools_rs = bench::src("runtime/src/tools.rs");

    // bullet 2 (creation): `create` AND `create_system` now both ask §6, and `build` demands the witness.
    for w in ["create", "create_system"] {
        assert!(
            bench::fn_body(&gates_rs, w).contains("Effect::HumanGateCreate"),
            "gates::{w} does not ask §6 (b3 recorded create_system as UNGUARDED on candidate 2)"
        );
    }
    assert!(bench::fn_body(&gates_rs, "build").contains("_clearance: &crate::srr::breakglass::Clearance"));

    // bullet 2 (approval): `answer` asks §6 at the effect as well as at the operation.
    let answer = bench::fn_body(&gates_rs, "answer");
    assert!(answer.contains("Effect::HumanGateApprove"));
    assert!(answer.contains(r#"guard_write(p, "gate answer")"#));

    // bullet 3: `release::build` still takes no `Project` — b3's reason it could not be guarded — and now guards
    // itself at the effect instead.
    assert!(
        release_rs.contains("pub fn build(\n    canonical_root: &Path,"),
        "release::build signature changed; re-derive this census"
    );
    assert!(
        bench::fn_body(&release_rs, "build").contains("Effect::ReleaseCertification"),
        "release::build is still unguarded (b3's candidate-2 finding)"
    );

    // bullet 4: `root_update` now guards (this is the assertion that flips b3), and the sink guards underneath.
    let root_update = bench::fn_body(&provision_rs, "root_update");
    assert!(
        root_update.contains("breakglass::guard") || root_update.contains("guard_write"),
        "root_update still reaches no guard"
    );
    assert!(bench::fn_body(&state_rs, "set_root_metadata").contains("Effect::TrustPolicyMutation"));

    // bullet 5: `plugins register` reaches the sink; `tools install` reaches only the operation guard.
    assert!(bench::fn_body(&tools_rs, "install").contains(r#"guard_write(p, "tools install")"#));

    // bullets 6 and 7: no primitive claimed. Bullet 6 verified in hx_a::a7; bullet 7 falsified in hx_a::a8.
    println!(
        "AR-0031 C4 — §6 enforcement-point census RE-DERIVED on candidate 3 (supersedes ho_b::b3's \
         candidate-2 print):\n\
         \x20 bullet 1 (normal privileged operation): `control::guard_write` -> `guard_light`, allow-list \
         default-refuse, 28 call sites / 23 labels. FAILS OPEN on `resolve_state_root()` error (hx_b::b3).\n\
         \x20 bullet 2 (gate creation): `gates::build` sink, compiler-enforced `&Clearance`; `create` and \
         `create_system` both ask. `create_system` has NO operation guard, so the sink is its only control \
         (hx_b::b4).\n\
         \x20 bullet 2 (gate approval): `gates::answer` — operation guard AND effect guard. Both fail open on \
         the same input.\n\
         \x20 bullet 3 (release certification): `release::build` — effect guard only (takes no Project). Fails \
         open.\n\
         \x20 bullet 4 (trust-policy mutation): `MachineState::set_root_metadata` via `guard_effect_on`, under \
         BOTH the framework key and the anchor's product key. DOES NOT fail open (hx_b::b5). `root_update` and \
         `provision` now also guard at the operation.\n\
         \x20 bullet 5 (privileged acquisition): `plugins::guard_acquisition` sink, reached from \
         `capabilities::governance::register_plugin` only, and only when the DESCRIPTOR declares a privileged \
         permission class. `tools::install` reaches the effect through the operation guard alone (hx_d).\n\
         \x20 bullet 6 (floor lowering): no primitive — `Floors` exposes only monotonic `raise_*`. HOLDS.\n\
         \x20 bullet 7 (present below floor as current): no primitive CLAIMED; falsified — `gov doctor`, \
         `gov update --check`, `gov version` and the agent context packet all report the below-floor release \
         with no marking (hx_a::a8)."
    );
}

/// c5 — `ho_b::b6`'s new statement, "a guard now sits between the allow-list entry and the gate creation".
#[test]
fn c5_a_guard_now_sits_between_the_allow_list_entry_and_the_gate_creation() {
    let update_rs = bench::src("runtime/src/update.rs");
    let apply = update_rs.split("pub fn apply_update_opts").nth(1).expect("apply_update_opts");
    let head = &apply[..apply.find("let auth = crate::srr::admit").expect("admit in apply")];
    assert!(head.contains(r#"guard_write(p, "update --apply")"#));
    assert!(head.contains("gates::create_system"), "apply no longer creates a system gate");

    let marker = r#"guard_write(p, "update --apply")"#;
    let between = &head[head.find(marker).unwrap() + marker.len()..head.find("gates::create_system").unwrap()];
    let guarded = between.contains("breakglass::guard") || between.contains("guard_write");
    assert!(
        guarded,
        "no guard sits between the §5 allow-list entry and the gate creation; b6's flip is not the repair working"
    );

    // And the decision half, measured: the allow-listed entry passes bullet 1 while the gate effects refuse.
    let (_x, root) = bench::isolated_default_root("c5");
    bench::mark_degraded(&root, PRODUCT);
    let ms = gov_runtime::srr::state::MachineState::at(&root).unwrap();
    assert!(bg::guard(&ms, PRODUCT, "update --apply").is_ok(), "§5 entry must stay open");
    assert_eq!(
        bg::guard(&ms, PRODUCT, "gate create").unwrap_err().details["refused_class"],
        "human_gate_create"
    );
    assert_eq!(
        bg::guard_effect(bg::Effect::HumanGateCreate, "gate create (update --apply)")
            .unwrap_err()
            .details["refused_class"],
        "human_gate_create"
    );
}

/// c6 — `ho_b::b4`'s two halves: the already-provisioned diagnosis is preserved, AND §6 at that door is proved
/// at the sink.
#[test]
fn c6_provision_keeps_its_diagnosis_and_section_6_is_proved_at_the_sink() {
    let provision_rs = bench::src("runtime/src/srr/provision.rs");
    let provision = bench::fn_body(&provision_rs, "provision");
    assert!(!provision.is_empty(), "`provision` not found");

    // half 1 — the §6 guard sits AFTER the already-provisioned latch, so the accurate error survives.
    let latch = provision
        .find("SRR_ALREADY_PROVISIONED")
        .expect("the already-provisioned latch is gone");
    let guard = provision
        .find("breakglass::guard")
        .expect("`provision` reaches no break-glass guard at all");
    assert!(
        latch < guard,
        "the §6 guard was put back BEFORE the already-provisioned check: `SRR_ALREADY_PROVISIONED` would become \
         `SRR_BELOW_FLOOR_REFUSED`, the property AR-0029's b4 verified"
    );

    // half 2 — and the door is genuinely closed underneath, at the sink, whatever the operation-level ordering.
    let (_x, root) = bench::isolated_default_root("c6");
    let ms = gov_runtime::srr::state::MachineState::at(&root).unwrap();
    bench::mark_via_product_path(&ms, PRODUCT);
    let e = ms
        .set_root_metadata(b"{\"signed\":{}}", 1, PRODUCT)
        .expect_err("the sink must refuse below floor regardless of the operation-level ordering");
    assert_eq!(e.details["refused_class"], "trust_policy_mutation");
    assert_eq!(e.details["section_6_bullet"], 4);
}
