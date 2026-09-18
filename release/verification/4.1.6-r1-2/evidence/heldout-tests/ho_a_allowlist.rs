//! AR-0029 held-out group A — is `AR27-B1` structurally closed?
//!
//! The repair claims `guard`/`guard_light` decide through an exact-match allow-list whose default is refusal, and
//! that `REFUSAL_CLASSES` decides nothing. These tests attack that claim directly, at the decision function and
//! through the real guard on a machine that carries the marking.
//!
//! A passing test means "the asserted behaviour is what candidate 2 does". Assertions that pin an observed
//! WEAKNESS rather than a desired behaviour are labelled `OBSERVED:` in the message.
mod common;
use common::mint;

use gov_runtime::srr::breakglass as bg;

const PRODUCT: &str = mint::PRODUCT;

/// The complete set of operation labels that reach a break-glass guard anywhere in the product, read off the
/// call sites rather than invented: 27 `control::guard_write` labels plus `update --rollback`, which reaches
/// `breakglass::guard` directly from `update.rs:410`.
const REAL_GUARDED_LABELS: &[&str] = &[
    "upstream submit",
    "checkpoint",
    "replan",
    "tools install",
    "gate create",
    "gate answer",
    "gate revoke",
    "adopt migrate",
    "adopt extract-legacy",
    "adopt build-memory",
    "memory select",
    "update --apply",
    "plugins register",
    "plugins unregister",
    "handoff create",
    "handoff return",
    "task create",
    "task status",
    "task claim",
    "task close",
    "readiness plan",
    "kernel reinstall",
    "cit propose",
    "cit simulate",
    "cit approve",
    "cit reject",
    "cit execute",
    "update --rollback",
];

#[test]
fn a1_the_decision_function_is_exact_match_under_every_near_miss_i_could_construct() {
    // The four labels the repair permits, verbatim.
    for (label, activity) in [
        ("checkpoint", "backup_export"),
        ("kernel reinstall", "uninstall_reinstall"),
        ("update --apply", "restore_authenticated_release"),
        ("update --rollback", "restore_authenticated_release"),
    ] {
        assert_eq!(
            bg::permitted_activity(label),
            Some(activity),
            "'{label}' must be permitted and must name its §5 activity"
        );
        assert!(
            bg::PERMITTED_ACTIVITIES.contains(&activity),
            "'{activity}' is not an OWNER-DECISION-0006 §5 activity"
        );
    }

    // Near misses. Every one of these must be refused for the allow-list to be exact-match rather than fuzzy.
    let near_misses: Vec<String> = {
        let mut v: Vec<String> = vec![];
        for base in [
            "checkpoint",
            "kernel reinstall",
            "update --apply",
            "update --rollback",
        ] {
            v.push(base.to_uppercase());
            v.push(base.to_lowercase() + " ");
            v.push(" ".to_string() + base);
            v.push("\t".to_string() + base);
            v.push(base.to_string() + "\n");
            v.push(base.to_string() + "\0");
            v.push(base.to_string() + " --force");
            v.push(base.to_string() + "-unverified");
            v.push(base.to_string() + "; gate answer");
            v.push(format!("gov {base}"));
            v.push(base.replace(' ', "  "));
            v.push(base.replace(' ', "\u{00a0}")); // NBSP for SPACE
            v.push(base.replace("--", "\u{2014}")); // EM DASH for the double hyphen
            v.push(base.replace('e', "\u{0435}")); // Cyrillic small ie homoglyph
            // one-character truncations, at both ends
            v.push(base[..base.len() - 1].to_string());
            v.push(base[1..].to_string());
        }
        // argument-bearing forms the handoff names specifically
        v.push("kernel reinstall --force".into());
        v.push("update --apply-unverified".into());
        v.push("update --apply --break-glass".into());
        v.push("checkpoint delete".into());
        v.push("checkpoint watchdog".into());
        // Several transforms above are the identity on a label that lacks the character they rewrite (there is
        // no space in `checkpoint`, no `--` in `kernel reinstall`). Those are not near misses, they ARE the
        // label, so drop them rather than assert the allow-list refuses its own entries.
        v.retain(|s| bg::PERMITTED_OPERATIONS.iter().all(|(l, _)| l != s));
        v.sort();
        v.dedup();
        v
    };
    let mut permitted_near_misses: Vec<&str> = vec![];
    for m in &near_misses {
        if bg::permitted_activity(m).is_some() {
            permitted_near_misses.push(m);
        }
    }
    println!(
        "AR-0029 A1 — {} near-miss forms probed, {} permitted",
        near_misses.len(),
        permitted_near_misses.len()
    );
    assert!(
        permitted_near_misses.is_empty(),
        "OBSERVED: exact-match semantics do not hold; these near misses were permitted: {permitted_near_misses:?}"
    );
}

#[test]
fn a2_refusal_is_the_default_for_labels_that_exist_in_neither_table() {
    // Labels drawn from nowhere: not on the allow-list, not in REFUSAL_CLASSES, not in the product.
    let unknown = [
        "",
        " ",
        "\n",
        "\u{2014}",
        "quorum override",
        "an operation invented after AR-0029",
        "ZZZZ",
        "update",           // a proper prefix of two permitted labels
        "kernel",           // a proper prefix of one
        "apply",            // a proper substring
        "reinstall",        // a proper substring
        "--apply",          // the argument alone
        "checkpointing",    // a proper superstring
        "\u{0000}",
        "🔥",
    ];
    for label in unknown {
        assert!(
            bg::permitted_activity(label).is_none(),
            "OBSERVED: '{label}' is permitted below floor although it appears in neither table"
        );
        // and it is reported under §6 bullet 1, the class the decision names for privileged governed work
        if !bg::REFUSAL_CLASSES.iter().any(|(n, _)| label.contains(n)) {
            assert_eq!(
                bg::refusal_class(label),
                "normal_privileged_operation",
                "'{label}' should default to §6 bullet 1"
            );
        }
    }
    assert_eq!(bg::REFUSAL_POLICY, "allow_list_default_refuse");
}

#[test]
fn a3_the_real_guard_on_a_marked_machine_permits_exactly_the_four() {
    let m = mint::scenario("a3");
    m.mark_degraded(PRODUCT);
    let ms = m.open();

    let mut permitted: Vec<&str> = vec![];
    let mut refused: Vec<&str> = vec![];
    for label in REAL_GUARDED_LABELS {
        match bg::guard(&ms, PRODUCT, label) {
            Ok(()) => permitted.push(label),
            Err(e) => {
                assert_eq!(
                    e.code, "SRR_BELOW_FLOOR_REFUSED",
                    "'{label}' refused with the wrong code"
                );
                assert_eq!(e.details["refusal_policy"], "allow_list_default_refuse");
                assert_eq!(e.details["marking"], bg::DEGRADED_TOKEN);
                refused.push(label);
            }
        }
    }
    println!(
        "AR-0029 A3 — of {} real guarded labels: PERMITTED {permitted:?}; REFUSED {} others",
        REAL_GUARDED_LABELS.len(),
        refused.len()
    );
    let mut got = permitted.clone();
    got.sort_unstable();
    assert_eq!(
        got,
        vec![
            "checkpoint",
            "kernel reinstall",
            "update --apply",
            "update --rollback"
        ],
        "the below-floor permitted set must be exactly the four §5 entries; it was {permitted:?}"
    );
    // AR27-B1's seven, each now refused through the real guard
    for gap in [
        "cit approve",
        "cit reject",
        "gate revoke",
        "handoff return",
        "plugins unregister",
        "adopt extract-legacy",
        "adopt build-memory",
    ] {
        assert!(
            refused.contains(&gap),
            "AR27-B1 residual: '{gap}' is still permitted below floor"
        );
    }
}

#[test]
fn a4_refusal_classes_are_reporting_only_and_never_load_bearing() {
    let m = mint::scenario("a4");
    m.mark_degraded(PRODUCT);
    let ms = m.open();

    // A label named in REFUSAL_CLASSES and a label named nowhere are refused identically, differing only in the
    // bullet quoted back. If membership were load-bearing the second would behave differently.
    let named = bg::guard(&ms, PRODUCT, "gate create").unwrap_err();
    let unnamed = bg::guard(&ms, PRODUCT, "an operation invented after AR-0029").unwrap_err();
    assert_eq!(named.code, unnamed.code);
    assert_eq!(named.details["refused_class"], "human_gate_create");
    assert_eq!(unnamed.details["refused_class"], "normal_privileged_operation");
    assert_eq!(
        named.details["refusal_policy"],
        unnamed.details["refusal_policy"]
    );

    // Every class REFUSAL_CLASSES can report is an OWNER-DECISION-0006 §6 activity, and no entry is permitted.
    for (label, class) in bg::REFUSAL_CLASSES {
        assert!(
            bg::REFUSED_ACTIVITIES.contains(class),
            "'{class}' is not a §6 activity"
        );
        assert!(
            bg::permitted_activity(label).is_none(),
            "OBSERVED: '{label}' is both refusal-classified and permitted"
        );
    }
}

#[test]
fn a5_an_unmarked_machine_is_not_refused_anything() {
    // The guard must not become a general-purpose brake: with no marking, everything proceeds.
    let m = mint::scenario("a5");
    let ms = m.open();
    for label in REAL_GUARDED_LABELS {
        assert!(
            bg::guard(&ms, PRODUCT, label).is_ok(),
            "'{label}' refused on a machine that carries no marking"
        );
    }
    // and after an explicit cleared exit (`active: false`) likewise
    let rec = serde_json::json!({"active": false, "marking": bg::DEGRADED_TOKEN});
    gov_runtime::srr::state::write_durable(&ms.degraded_path(PRODUCT), &rec).unwrap();
    for label in REAL_GUARDED_LABELS {
        assert!(
            bg::guard(&ms, PRODUCT, label).is_ok(),
            "'{label}' refused after a cleared exit"
        );
    }
}

#[test]
fn a6_the_exit_policy_point_is_single_and_still_the_stricter_reading() {
    // OWNER-DECISION-0007 §2 closed SRR2-R1-C1 as owner policy. Not graded here; verified as still implemented
    // at the one named point.
    assert_eq!(bg::EXIT_POLICY, "b_stricter_both_floors");
    let mut f = gov_runtime::srr::state::Floors {
        product: PRODUCT.into(),
        ..Default::default()
    };
    f.raise_minimum_secure("4.1.2", 12, "src");
    f.raise_release("4.1.5", 15, true);
    assert!(!bg::exit_satisfied("4.1.3", 13, &f), "between the floors must not exit");
    assert!(!bg::exit_satisfied("4.1.5", 14, &f), "sequence below high-water must not exit");
    assert!(!bg::exit_satisfied("4.1.4", 15, &f), "version below high-water must not exit");
    assert!(bg::exit_satisfied("4.1.5", 15, &f));
    assert!(bg::exit_satisfied("4.2.0", 99, &f));
}
