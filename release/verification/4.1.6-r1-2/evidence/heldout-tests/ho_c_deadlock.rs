//! AR-0029 held-out group C — the repair's `Marking::Unreadable` judgement call.
//!
//! The repair made an unreadable marking record refuse instead of returning `Ok`, and claims in
//! `runtime/src/srr/breakglass.rs`:
//!
//! > "Recovery is unaffected, because every [`PERMITTED_OPERATIONS`] entry is allowed before this is ever
//! > consulted, so the exit path stays open."
//!
//! The restore half of that is true. The *exit* half is what these tests attack: clearing the marking runs
//! through `Degraded::load`, which reads the same file with the opposite disposition.
mod common;
use common::mint;

use gov_runtime::srr::breakglass as bg;
use gov_runtime::srr::state::Floors;

const PRODUCT: &str = mint::PRODUCT;

/// Every shape of "present but not a readable marking record" I could construct.
fn corruptions() -> Vec<(&'static str, Vec<u8>)> {
    vec![
        ("truncated json", b"{\"active\": tr".to_vec()),
        ("empty file", b"".to_vec()),
        ("not json at all", b"\x00\x01\x02binary".to_vec()),
        ("json but not an object", b"[1,2,3]".to_vec()),
        ("object with no `active` member", b"{\"marking\":\"x\"}".to_vec()),
        ("`active` is a string", b"{\"active\":\"true\"}".to_vec()),
        ("`active` is null", b"{\"active\":null}".to_vec()),
    ]
}

#[test]
fn c1_an_unreadable_marking_refuses_everything_outside_the_allow_list() {
    let m = mint::scenario("c1");
    let ms = m.open();
    for (what, bytes) in corruptions() {
        m.corrupt_marking(PRODUCT, &bytes);
        let e = bg::guard(&ms, PRODUCT, "cit approve")
            .unwrap_err_or_panic(&format!("{what}: expected a refusal"));
        assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED", "{what}");
        assert!(
            e.details["break_glass_record"]["unreadable_marking_record"]
                .as_str()
                .unwrap_or_default()
                .ends_with(".json"),
            "{what}: the refusal must name the file an operator has to deal with"
        );
    }
    println!("AR-0029 C1 — all {} corruption shapes refuse", corruptions().len());
}

#[test]
fn c2_the_restore_half_of_the_claim_holds() {
    // The repair's claim that the allow-list is consulted before any state read: verified.
    let m = mint::scenario("c2");
    let ms = m.open();
    m.corrupt_marking(PRODUCT, b"{\"active\": tr");
    for label in ["kernel reinstall", "update --apply", "update --rollback", "checkpoint"] {
        assert!(
            bg::guard(&ms, PRODUCT, label).is_ok(),
            "'{label}' must stay available with an unreadable marking"
        );
    }
    println!("AR-0029 C2 — restoration and backup remain available under an unreadable marking");
}

/// **The exit half does not hold.** After restoring an authenticated release at or above BOTH floors — the
/// `OWNER-DECISION-0006` §7 / `OWNER-DECISION-0007` §2 exit condition — the marking is not cleared, because
/// `try_exit` loads through `Degraded::load`, which treats an unreadable record as "not marked" and returns
/// `Ok(None)` without writing anything. The guard, reading the same file, keeps refusing.
#[test]
fn c3_an_unreadable_marking_cannot_be_cleared_by_meeting_the_exit_condition() {
    let m = mint::scenario("c3");
    let ms = m.open();

    let mut floors = Floors {
        product: PRODUCT.into(),
        ..Default::default()
    };
    floors.raise_minimum_secure("4.1.2", 12, "src");
    floors.raise_release("4.1.5", 15, true);
    // sanity: this release satisfies the owner-decided exit policy
    assert!(bg::exit_satisfied("4.1.6", 16, &floors));

    m.corrupt_marking(PRODUCT, b"{\"active\": tr");
    let before = std::fs::read(ms.degraded_path(PRODUCT)).unwrap();

    // This is exactly what `verifier::record_installed` does after a successful authenticated install.
    let exit = bg::try_exit(&ms, PRODUCT, 16, "4.1.6", true, &floors).unwrap();
    let after = std::fs::read(ms.degraded_path(PRODUCT)).unwrap();
    let still_refused = bg::guard(&ms, PRODUCT, "cit approve");

    println!(
        "AR-0029 C3 — after installing an authenticated release above BOTH floors:\n\
         \x20 try_exit returned {exit:?}\n\
         \x20 marking record rewritten = {}\n\
         \x20 `cit approve` still refused = {}\n\
         \x20 is_degraded() reports = {}   (the guard disagrees)",
        before != after,
        still_refused.is_err(),
        bg::is_degraded(&ms, PRODUCT)
    );

    assert!(
        still_refused.is_ok(),
        "OBSERVED (AR29-C1): the exit condition of OWNER-DECISION-0006 §7 was met — an authenticated release at \
         or above both floors was installed — yet the machine still refuses governed operation as \
         `{}`. `try_exit` returned {exit:?} and did not rewrite the record, because `Degraded::load` treats an \
         unreadable marking as absent while `read_marking` treats it as present. The repair's claim that \
         \"the exit path stays open\" holds for restoration but not for clearing the marking.",
        bg::DEGRADED_TOKEN
    );
}

/// The same divergence seen from the reporting surface: the machine refuses as degraded while telling the
/// operator it is not degraded.
#[test]
fn c4_the_machine_reports_not_degraded_while_refusing_as_degraded() {
    let m = mint::scenario("c4");
    m.activate();
    let v1 = mint::Signer1::seeded(0x61);
    m.provision_with(&mint::root_document(1, &mint::canonical_year(2099), &v1));
    m.corrupt_marking(PRODUCT, b"{\"active\": tr");

    let status = gov_runtime::srr::status().unwrap();
    let bgs = gov_runtime::srr::provision::break_glass_status().unwrap();
    let guard = bg::guard_light(PRODUCT, "cit approve");

    println!(
        "AR-0029 C4 — `gov trust status`.degraded = {}; `gov trust break-glass`.currently_degraded = {}; \
         guard_light(\"cit approve\") = {}",
        status["degraded"],
        bgs["currently_degraded"],
        guard.as_ref().err().map(|e| e.code.clone()).unwrap_or("Ok".into())
    );

    assert!(
        !(guard.is_err() && bgs["currently_degraded"] == false),
        "OBSERVED (AR29-C1): `gov trust break-glass` reports currently_degraded=false and `gov trust status` \
         reports degraded={} while every governed mutation is refused with `{}`. Two readers of the same \
         record disagree about whether the machine is marked.",
        status["degraded"],
        bg::DEGRADED_TOKEN
    );
}

/// Control: with a *readable* marking, the exit condition does clear it and governed operation resumes. This is
/// what C3 measures the absence of, and it must pass or C3 proves nothing.
#[test]
fn c5_a_readable_marking_clears_when_the_exit_condition_is_met() {
    let m = mint::scenario("c5");
    let ms = m.open();
    m.mark_degraded(PRODUCT);

    let mut floors = Floors {
        product: PRODUCT.into(),
        ..Default::default()
    };
    floors.raise_minimum_secure("4.1.2", 12, "src");
    floors.raise_release("4.1.5", 15, true);

    assert!(bg::guard(&ms, PRODUCT, "cit approve").is_err(), "marked: refused");

    // below the high-water: stays marked
    let held = bg::try_exit(&ms, PRODUCT, 13, "4.1.3", true, &floors).unwrap().unwrap();
    assert_eq!(held["cleared"], false);
    assert!(bg::is_degraded(&ms, PRODUCT));

    // unauthenticated at-floor release: stays marked (§1/§7)
    let unauth = bg::try_exit(&ms, PRODUCT, 16, "4.1.6", false, &floors).unwrap().unwrap();
    assert_eq!(unauth["cleared"], false);
    assert!(bg::is_degraded(&ms, PRODUCT));

    // authenticated, above both floors: clears, and governed operation resumes
    let cleared = bg::try_exit(&ms, PRODUCT, 16, "4.1.6", true, &floors).unwrap().unwrap();
    assert_eq!(cleared["cleared"], true);
    assert!(!bg::is_degraded(&ms, PRODUCT));
    assert!(bg::guard(&ms, PRODUCT, "cit approve").is_ok(), "exit must restore governed operation");
    println!("AR-0029 C5 — readable marking: held below floor, held when unauthenticated, cleared at floor");
}

// ---------------------------------------------------------------------------------------------- small helper

trait UnwrapErrOrPanic<T, E> {
    fn unwrap_err_or_panic(self, msg: &str) -> E;
}
impl<T: std::fmt::Debug, E> UnwrapErrOrPanic<T, E> for Result<T, E> {
    fn unwrap_err_or_panic(self, msg: &str) -> E {
        match self {
            Ok(v) => panic!("{msg} (got Ok({v:?}))"),
            Err(e) => e,
        }
    }
}
