//! `OWNER-DECISION-0006` §6 bullet 7 — **how this product presents the installed release**.
//!
//! > While marked `DEGRADED — RECOVERY ONLY`, the product MUST NOT treat the below-floor release as current or
//! > fully trusted.
//!
//! ## Why this module exists
//!
//! Repair 2's census recorded bullet 7 as `no primitive: every reporting surface carries the marking`, and
//! AR-0031 falsified both halves: [`crate::srr::breakglass::Effect::PresentBelowFloorReleaseAsCurrent`] had no
//! call site anywhere in the product, so nothing was ever refused under bullet 7; and the excusing claim was
//! untrue — `runtime/src/doctor.rs` held **zero** references to the marking, `gov update --check` emitted
//! `{"current": <below-floor version>, "up_to_date": …, "recommendation": "nothing to do"}`, and `gov version`
//! and the agent context packet carried no marking either. On a machine in genuine owner-authorised break-glass,
//! the two questions an operator reaches for first — "is this machine healthy?" and "am I up to date?" — both
//! answered as though the machine were not in break-glass.
//!
//! ## The primitive, and why the enforcement point is *inside* it
//!
//! [`presentation`] is the one place this product decides what it is entitled to say about the installed release.
//! It **asks** [`crate::srr::breakglass::guard_effect`] for
//! [`Effect::PresentBelowFloorReleaseAsCurrent`](crate::srr::breakglass::Effect::PresentBelowFloorReleaseAsCurrent),
//! and the answer *is* the presentation:
//!
//! * cleared — the release may be presented as current;
//! * refused — the refusal is not swallowed. It becomes the marking, the entry time and the exit condition in the
//!   returned block, and [`attach`] rewrites any affirmative currency claim the surface was about to make.
//!
//! The refusal therefore changes what the product says, which is exactly what §6 bullet 7 forbids it from saying.
//! This function is deliberately **infallible**: `OWNER-DECISION-0006` §5 requires inspection and diagnosis to
//! stay available below floor, so bullet 7 cannot be enforced by refusing to answer. It is enforced by refusing
//! to answer *as though the machine were current*.
//!
//! ## Why the coverage is universal rather than a list of audited surfaces
//!
//! "Every reporting surface carries the marking" was a list, and it went short — which is the failure this whole
//! repair exists to end. It is not a list here. `gov` emits a command result in exactly one place: the
//! `match result` in `cli/src/main.rs`, which wraps whatever `run()` returned in the response envelope. That
//! envelope calls [`attach`]. **Every command carries the marking, including commands that do not exist yet and
//! commands that have never heard of break-glass** — which the certification suite measures by driving a command
//! with no relationship to release identity at all and asserting the marking is there.
//!
//! Three surfaces additionally carry it in their own payload, because the envelope is not enough for them:
//! `gov doctor` (its report is consumed as a typed value by `update` and the audit suite, and its own `DEGRADED`
//! verdict already means something else), `gov update --check` (an affirmative `up_to_date` is a false claim that
//! a sibling block does not repair), and the agent context packet (it is hashed and consumed as a unit by every
//! kernel role).
//!
//! `gov trust status`, `gov status` and `gov recover` already carried the marking in their own payloads before
//! this repair and are unchanged.
//!
//! ## What this does not cover
//!
//! An in-process embedder of `gov_runtime` that calls a reporting function directly, rather than through the
//! `gov` binary, gets the marking only from the surfaces that carry it in their own payload. The envelope is a
//! property of the CLI boundary. Two other `println!` sites exist in `cli/src/main.rs` — the human rendering of a
//! Human Gate (whose machine-readable form is returned through the envelope) and the `gov-capability/1` provider
//! response (which reports a provider protocol version, not the installed release). Neither is a command result;
//! both are named in the derived census so a third one cannot appear unnoticed.
use crate::srr::breakglass::{self, Effect};
use serde_json::{json, Value};

/// The key every presentation is carried under, in the CLI response envelope and in every report that carries one
/// in its own payload. One spelling, so a consumer never has to know which surface it is reading.
pub const PRESENTATION_KEY: &str = "release_trust";

/// `presented_as` when the machine is at or above its floors: the installed release may be called current.
pub const PRESENTED_CURRENT: &str = "CURRENT";
/// `presented_as` while the machine is marked: the installed release is below floor and is not current.
pub const PRESENTED_BELOW_FLOOR: &str = "BELOW_FLOOR_RECOVERY_ONLY";
/// `presented_as` when the §6 check could not determine its subject (`AR31-B2`). Not current, because unknown is
/// not "no".
pub const PRESENTED_UNDETERMINED: &str = "UNDETERMINED";

/// **The `OWNER-DECISION-0006` §6 bullet 7 sink.**
///
/// `surface` names the caller for the refusal record — the command name at the CLI boundary, or the report name
/// for a surface that carries the presentation in its own payload.
pub fn presentation(surface: &str) -> Value {
    match breakglass::guard_effect(Effect::PresentBelowFloorReleaseAsCurrent, surface) {
        Ok(_) => json!({
            "surface": surface,
            "below_floor": false,
            "marking": Value::Null,
            "presented_as": PRESENTED_CURRENT,
            "section_6_bullet": 7,
            "basis": "OWNER-DECISION-0006 §6 bullet 7 was asked at crate::srr::present::presentation and cleared: this machine carries no `DEGRADED — RECOVERY ONLY` marking. This states the machine's break-glass posture only; it is not a currency claim about the wider release channel, which `gov trust status` reports as UNKNOWN between ingresses.",
        }),
        Err(e) => {
            let undetermined = e.code == "SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED";
            json!({
                "surface": surface,
                "below_floor": true,
                "marking": breakglass::DEGRADED_TOKEN,
                "presented_as": if undetermined { PRESENTED_UNDETERMINED } else { PRESENTED_BELOW_FLOOR },
                "section_6_bullet": 7,
                "refused_class": "present_below_floor_release_as_current",
                "refusal_code": e.code,
                "entered_at": e.details.get("entered_at").cloned().unwrap_or(Value::Null),
                "exit_condition": breakglass::exit_condition_description(),
                "operator_note": if undetermined {
                    "This machine's protected state root could not be resolved, so whether it is marked `DEGRADED — RECOVERY ONLY` could not be determined. OWNER-DECISION-0006 §6 bullet 7 is a MUST NOT, so the installed release is not presented as current. Resolve the protected state root and re-run."
                } else {
                    "This machine is marked `DEGRADED — RECOVERY ONLY` (OWNER-DECISION-0006 §4). The installed release is below its signed security floor: it is NOT current and NOT fully trusted, whatever version number appears beside it. Only the §5 recovery activities are available until an authenticated release at or above both floors is installed."
                },
                "permitted_while_below_floor": breakglass::PERMITTED_ACTIVITIES,
                "gate_free_restoration_routes": breakglass::GATE_FREE_RESTORATION_ROUTES,
            })
        }
    }
}

/// Attach the presentation to a report object, and **demote any affirmative currency claim it carries**.
///
/// Putting the marking beside `"up_to_date": true` would not satisfy §6 bullet 7: the claim itself is the
/// forbidden presentation, and an operator who reads `"recommendation": "nothing to do"` has been told the
/// opposite of what is true — restoring an authenticated at-floor release is the only way out of break-glass.
///
/// A non-object report is left unchanged; the CLI envelope that wraps it is always an object and always carries
/// the presentation, so nothing loses the marking by being an array.
pub fn attach(surface: &str, report: &mut Value) {
    let pres = presentation(surface);
    let below = pres["below_floor"].as_bool().unwrap_or(true);
    let Some(o) = report.as_object_mut() else {
        return;
    };
    if below {
        if o.contains_key("up_to_date") {
            o.insert("up_to_date".into(), json!(false));
        }
        if o.contains_key("recommendation") {
            o.insert(
                "recommendation".into(),
                json!(format!(
                    "this machine is marked `{}`: the installed release is below its signed security floor and is neither current nor fully trusted (OWNER-DECISION-0006 §6 bullet 7). {}",
                    breakglass::DEGRADED_TOKEN,
                    breakglass::exit_condition_description()
                )),
            );
        }
    }
    o.insert(PRESENTATION_KEY.to_string(), pres);
}

/// Is this machine entitled to present its installed release as current right now?
pub fn may_present_as_current(surface: &str) -> bool {
    !presentation(surface)["below_floor"]
        .as_bool()
        .unwrap_or(true)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_presentation_always_states_which_way_it_went() {
        let v = presentation("unit-test");
        assert_eq!(v["section_6_bullet"], 7);
        assert!(v["below_floor"].is_boolean());
        assert!(matches!(
            v["presented_as"].as_str().unwrap(),
            PRESENTED_CURRENT | PRESENTED_BELOW_FLOOR | PRESENTED_UNDETERMINED
        ));
        assert_eq!(v["surface"], "unit-test");
    }

    /// The demotion is driven by the block, not by the caller: a report that claims currency has the claim
    /// rewritten whenever the guard refused, and is left alone when it cleared.
    #[test]
    fn attach_demotes_a_currency_claim_exactly_when_the_guard_refused() {
        let mut r = json!({"current": "4.1.5", "up_to_date": true, "recommendation": "nothing to do"});
        attach("unit-test", &mut r);
        assert!(r.get(PRESENTATION_KEY).is_some());
        let below = r[PRESENTATION_KEY]["below_floor"].as_bool().unwrap();
        if below {
            assert_eq!(r["up_to_date"], false);
            assert!(r["recommendation"]
                .as_str()
                .unwrap()
                .contains("OWNER-DECISION-0006 §6 bullet 7"));
        } else {
            assert_eq!(r["up_to_date"], true);
            assert_eq!(r["recommendation"], "nothing to do");
        }
        // an array report keeps its shape and loses nothing: the envelope carries the marking for it
        let mut arr = json!([1, 2, 3]);
        attach("unit-test", &mut arr);
        assert_eq!(arr, json!([1, 2, 3]));
    }
}
