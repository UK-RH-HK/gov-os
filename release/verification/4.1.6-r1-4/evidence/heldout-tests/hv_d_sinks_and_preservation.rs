//! **AR-0033 held-out verification — the sinks the derivation found, the residual dispositions, and the frozen
//! R1 preservation obligations.**
//!
//! Run single-threaded: several tests set process-wide environment.
mod common;
use common::*;
use gov_runtime::srr::breakglass as bg;
use serde_json::json;

fn set_env(m: &Machine) {
    std::env::set_var("HOME", &m.home);
    std::env::set_var("XDG_STATE_HOME", &m.home);
    std::env::remove_var("GOV_MACHINE_STATE_DIR");
}

/// **d1 — `AR31-N3`: bullet 2 is an EFFECT property. All three of AR-0031's constructions are refused.**
#[test]
fn d1_a_human_gate_record_cannot_be_persisted_below_floor_however_it_was_minted() {
    let m = machine("d1-record");
    set_env(&m);
    let proj = scratch("d1-proj");

    // the dispatch is a runtime type lookup, not a source grep — that is the whole point of AR31-N3
    assert_eq!(bg::guarded_record_effect("human-gate"), Some(bg::Effect::HumanGateCreate));
    assert!(bg::guarded_record_effect("task").is_none());
    assert!(bg::guarded_record_effect("decision").is_none());

    let literal = gov_runtime::records::new_record("human-gate", "HDG-9001", "t", json!({"question": "q"}));
    let computed_ty: &str = &String::from("human-gate");
    let computed = gov_runtime::records::new_record(computed_ty, "HDG-9002", "t", json!({"question": "q"}));
    let mut retyped = gov_runtime::records::new_record("task", "TASK-9003", "t", json!({}));
    retyped.set("type", json!("human-gate"));

    // above floor all three persist
    for r in [&literal, &computed, &retyped] {
        gov_runtime::records::save_record(&proj, r)
            .unwrap_or_else(|e| panic!("an unmarked machine refused a gate write: [{}] {}", e.code, e.message));
    }

    // below floor all three are refused at the record-write sink, whoever minted them
    m.mark();
    for (what, r) in [("literal", &literal), ("computed type", &computed), ("retyped", &retyped)] {
        let e = gov_runtime::records::save_record(&proj, r)
            .err()
            .unwrap_or_else(|| panic!("a `human-gate` record minted by {what} was PERSISTED below floor"));
        assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED", "{what}");
        assert_eq!(e.details["refused_class"], "human_gate_create", "{what}");
        assert_eq!(e.details["section_6_bullet"], 2, "{what}");
    }
    // and an unguarded record type is unaffected, so this is a §6 control and not a freeze
    let task = gov_runtime::records::new_record("task", "TASK-9004", "t", json!({}));
    gov_runtime::records::save_record(&proj, &task).expect("an unrelated record type was refused below floor");

    // the compiler-enforced `&Clearance` on `gates::build` is KEPT alongside it
    assert!(
        src("runtime/src/orchestration/gates.rs").contains("_clearance: &crate::srr::breakglass::Clearance"),
        "`gates::build` no longer requires a §6 clearance"
    );
    std::env::remove_var("GOV_MACHINE_STATE_DIR");
}

/// **d2 — the CIT closure: `write_file` and `move_file` ask §6 by the record type the bytes declare.**
#[test]
fn d2_the_cit_mutation_ops_reach_the_bullet_2_control() {
    let f = product_functions(true)
        .into_iter()
        .find(|f| f.file.ends_with("cit/mod.rs") && f.name == "apply_op")
        .expect("cit::apply_op not found");
    // both branches present, both asking
    for op in ["\"write_file\"", "\"move_file\""] {
        assert!(f.body.contains(op), "`apply_op` lost its {op} branch");
    }
    assert_eq!(
        f.body.matches("guarded_record_effect(").count(),
        2,
        "expected the §6 record-type question in exactly the two CIT ops that bypass `save_record`"
    );
    assert_eq!(
        f.body.matches("crate::srr::breakglass::guard_effect(effect,").count(),
        2,
        "a CIT mutation op parses the record type and then does not ask §6"
    );
    for op in ["cit write_file", "cit move_file"] {
        assert!(f.body.contains(op), "the CIT §6 refusal does not name the operation `{op}`");
    }
    // `append_record` still goes through the record-write sink rather than growing a second control
    assert!(f.body.contains("save_record(&p.root, r)"), "`append_record` no longer persists through the sink");
}

/// **d3 — `gov gate present` is refused below floor at the record-write sink.**
///
/// The repair reports this as a real behaviour change: `gate present` calls `authority::require` and
/// `save_record` and NOT `control::guard_write`, so before this repair it mutated a governed Human Gate record
/// below floor.
#[test]
fn d3_gate_present_reaches_no_operation_guard_and_is_now_refused_at_the_sink() {
    let gates = src("runtime/src/orchestration/gates.rs");
    let present = split("gates.rs", &cut_tests(&gates))
        .into_iter()
        .find(|f| f.name == "present")
        .expect("gates::present not found");
    assert!(
        !present.body.contains("guard_write("),
        "`gates::present` now has an operation-level guard; re-derive this scenario"
    );
    assert!(
        present.body.contains("save_record(&p.root, g)"),
        "`gates::present` no longer persists through the record-write sink, so nothing refuses it below floor"
    );
    // The record it saves is guaranteed to be a `human-gate` — the function refuses any other type before the
    // write — so `save_record`'s type-keyed §6 dispatch necessarily fires. That closes the chain from the
    // command to the refusal without needing the CLI to reach it.
    assert!(
        present.body.contains(r#"if g.rtype() != "human-gate""#),
        "`gates::present` no longer guarantees the record type it writes; re-derive this scenario"
    );
    assert!(bg::guarded_record_effect("human-gate").is_some());
    // and the mutation really is a mutation, so this is a governed record write and not a read
    assert!(present.body.contains(r#"g.set("presented_at""#));
    // and the label is NOT on the §5 allow-list, so the refusal is not an accident of the operation table
    assert!(bg::permitted_activity("gate present").is_none());

    // behavioural: through the binary, on a marked machine
    let m = machine("d3-present");
    let proj = m.home.join("proj");
    std::fs::create_dir_all(&proj).unwrap();
    m.mark();
    let r = gov(&m, &proj, &[], &["--json", "gate", "present", "HDG-0001"]);
    let v = r.json();
    let code = v["error"]["code"].as_str().unwrap_or("");
    println!("gov gate present on a marked machine: {code}");
    assert!(
        v["ok"] == json!(false),
        "`gov gate present` succeeded on a marked machine: {v}"
    );
    assert_eq!(v["release_trust"]["below_floor"], true, "the refusal envelope lost the marking");
}

/// **d4 — `AR31-N1` / `AR31-N2`: both acquisition primitives ask, and the descriptor no longer decides.**
#[test]
fn d4_both_acquisition_primitives_ask_section_6_unconditionally() {
    let m = machine("d4-acq");
    set_env(&m);
    m.mark();

    // AR31-N2: a capability that declares itself UNPRIVILEGED is still refused below floor.
    let unprivileged = json!({
        "plugin_id": "p1", "capability": "embed", "version": "1", "source": "remote",
        "required_permission_classes": ["READ_ONLY"],
    });
    let e = gov_runtime::srr::plugins::guard_acquisition(
        "embed",
        &unprivileged,
        gov_runtime::srr::plugins::Acquisition::RemotelyAcquired,
        &[],
        "stable",
    )
    .err()
    .expect("an unprivileged remote capability was acquired below floor: the descriptor still decides");
    assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED");
    assert_eq!(e.details["refused_class"], "privileged_plugin_acquisition");

    // a descriptor that declares NOTHING at all is also refused
    let silent = json!({"plugin_id": "p2", "capability": "embed", "version": "1"});
    assert!(
        gov_runtime::srr::plugins::guard_acquisition("embed", &silent, gov_runtime::srr::plugins::Acquisition::RemotelyAcquired, &[], "stable").is_err(),
        "a descriptor that declares no permission classes is not asked the §6 question"
    );

    // AR31-N1: the second primitive has its own named door and it asks the same question
    let e = gov_runtime::srr::plugins::guard_acquisition_below_floor("tools install")
        .err()
        .expect("`tools install` is not refused below floor");
    assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED");
    assert_eq!(e.details["refused_class"], "privileged_plugin_acquisition");

    // the question is asked BEFORE the descriptor is consulted, structurally
    let acq = product_functions(true)
        .into_iter()
        .find(|f| f.file.ends_with("srr/plugins.rs") && f.name == "guard_acquisition")
        .unwrap();
    // Comments are stripped: the question is what the CODE does before the guard, not what it says about the
    // arrangement it replaced.
    let code_only: String = acq
        .body
        .lines()
        .filter(|l| !l.trim_start().starts_with("//"))
        .collect::<Vec<_>>()
        .join("\n");
    let before = code_only.split("Effect::PrivilegedPluginAcquisition").next().unwrap().to_string();
    assert!(
        !before.contains("is_privileged(") && !before.contains("if privileged"),
        "the §6 question is still gated on data the descriptor supplies about itself (ARCH-0003 §9): {before}"
    );
    // and it really is asked first, before the descriptor is read at all
    assert!(
        code_only.contains("let privileged = is_privileged(descriptor);"),
        "`guard_acquisition` no longer reads the descriptor after the guard; re-derive this scenario"
    );

    // above floor nothing changes
    let clean = machine("d4-clean");
    set_env(&clean);
    gov_runtime::srr::plugins::guard_acquisition("embed", &unprivileged, gov_runtime::srr::plugins::Acquisition::RemotelyAcquired, &[], "stable")
        .expect("an unmarked machine refused a capability acquisition");
    std::env::remove_var("GOV_MACHINE_STATE_DIR");
}

/// **d5 — `AR31-N4`: the two dropped sub-checks, reproduced HERE rather than trusted where they were moved.**
///
/// AR-0031's point was that the malleability check cannot live in the product's own suite under `SRR-R0-L4`,
/// because `gov` cannot sign. The repair moved it into `tests/certification/section6.rs`, the implementer's own
/// suite. Whether that is the right home is a judgement; whether the PROPERTY holds is measurable, and it is
/// measured here, in held-out material, from an independent malleation.
#[test]
fn d5_the_malleability_and_relaxation_properties_hold_in_held_out_material() {
    use ed25519_dalek::{Signer, SigningKey};
    let sk = SigningKey::from_bytes(&[0xa3u8; 32]);
    let public = hex::encode(sk.verifying_key().to_bytes());
    let msg = b"AR-0033 independent malleability probe";
    let sig = hex::encode(sk.sign(msg).to_bytes());
    gov_runtime::srr::crypto::verify(&public, &sig, msg).expect("a good signature must verify");
    gov_runtime::srr::crypto::verify_strict(&public, &sig, msg).expect("and must verify strictly");

    // S + L, the classic non-canonical scalar. L = 2^252 + 27742317777372353535851937790883648493.
    let l: [u8; 32] = [
        0xed, 0xd3, 0xf5, 0x5c, 0x1a, 0x63, 0x12, 0x58, 0xd6, 0x9c, 0xf7, 0xa2, 0xde, 0xf9, 0xde, 0x14,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10,
    ];
    let mut raw = hex::decode(&sig).unwrap();
    let mut carry = 0u16;
    for i in 0..32 {
        let s = raw[32 + i] as u16 + l[i] as u16 + carry;
        raw[32 + i] = (s & 0xff) as u8;
        carry = s >> 8;
    }
    let malleated = hex::encode(&raw);
    assert_ne!(malleated, sig, "the malleation produced the original signature");
    let a = gov_runtime::srr::crypto::verify(&public, &malleated, msg);
    let b = gov_runtime::srr::crypto::verify_strict(&public, &malleated, msg);
    assert!(a.is_err() && b.is_err(), "a malleated S+L signature was ACCEPTED: verify={a:?} strict={b:?}");
    assert_eq!(
        a.unwrap_err().code,
        b.unwrap_err().code,
        "the two entry points disagree on a malleated signature"
    );

    // a flipped byte must fail too, so the above is not passing for an unrelated reason
    let mut flipped = hex::decode(&sig).unwrap();
    flipped[3] ^= 0x01;
    assert!(gov_runtime::srr::crypto::verify(&public, &hex::encode(&flipped), msg).is_err());

    // the relaxation-switch census, re-derived over product source
    for (path, text) in product_files() {
        for needle in ["skip_verify", "skip-verify", "allow_unsigned", "allow-unsigned", "force_unsigned", "insecure_skip"] {
            for (n, line) in text.lines().enumerate() {
                assert!(
                    !(line.contains(needle) && !line.contains("REFUSED_AUTHORITY_ENV")),
                    "{path}:{} declares a verification relaxation switch: {line}", n + 1
                );
            }
        }
    }

    // and the check IS durably present in the candidate's own suite, so this verifier is not the only home
    let s6 = src("tests/certification/section6.rs");
    assert!(
        s6.contains("verify_strict(") && s6.contains("malleated") && s6.contains("skip_verify"),
        "the restored sub-checks are not in `tests/certification/section6.rs` after all"
    );
}

/// **d6 — `SRR-R0-L4` is vacuous: `gov` verifies and never signs.**
#[test]
fn d6_the_product_cannot_sign() {
    for (path, text) in product_files() {
        if path.contains("security/") {
            continue; // the secret DETECTOR's regexes, not a signing capability
        }
        for needle in ["SigningKey", "ed25519_dalek::Signer", "PRIVATE KEY", ".sign(", "SecretKey"] {
            assert!(
                !text.contains(needle),
                "{path} carries a signing capability ({needle}); SRR-R0-L4 requires `gov` to verify and never sign"
            );
        }
    }
    // and the excluded directory really is only a detector
    for (path, text) in product_files() {
        if !path.contains("security/") {
            continue;
        }
        for needle in ["SigningKey", "ed25519_dalek::Signer", "PRIVATE KEY"] {
            if text.contains(needle) {
                println!("security/ hit for {needle:?} in {path} — inspected: detector regex only");
                assert!(
                    !text.contains("use ed25519_dalek::Signer"),
                    "{path} imports a real signer, not a detector pattern"
                );
            }
        }
    }
}

/// **d7 — the frozen R1 preservation obligations, re-measured.**
#[test]
fn d7_frozen_r1_preservation_still_holds() {
    // the sealed witness is constructible nowhere outside `breakglass`
    let clearance: Vec<String> = product_files()
        .into_iter()
        .filter(|(p, _)| !p.ends_with("srr/breakglass.rs"))
        .filter(|(_, t)| t.contains("Clearance {") || t.contains("Clearance::issue"))
        .map(|(p, _)| p)
        .collect();
    assert!(clearance.is_empty(), "a `Clearance` is constructed outside `breakglass`: {clearance:?}");

    // The sealed authenticated-release witness: exactly one CONSTRUCTION site. The type declaration and its
    // `impl` block spell the same two words, so they are excluded by hand rather than by a looser needle.
    let mut constructions = vec![];
    for (p, t) in product_files() {
        for (n, line) in t.lines().enumerate() {
            let s = line.trim_start();
            if !s.contains("AuthenticatedRelease {") {
                continue;
            }
            if s.starts_with("pub struct ") || s.starts_with("struct ") || s.starts_with("impl ") {
                continue;
            }
            constructions.push(format!("{p}:{}: {s}", n + 1));
        }
    }
    println!("`AuthenticatedRelease` construction sites: {constructions:#?}");
    assert_eq!(
        constructions.len(),
        1,
        "expected exactly one `AuthenticatedRelease` construction, found {}: {constructions:?}",
        constructions.len()
    );
    assert!(constructions[0].contains("srr/verifier.rs"), "the one construction moved: {constructions:?}");
    let by_admit: usize = product_files().into_iter().map(|(_, t)| t.matches("fn by_admit").count()).sum();
    assert_eq!(by_admit, 1, "expected exactly one `by_admit` constructor, found {by_admit}");

    // five `admit` sites paired with five `install_kernel` sites
    let funcs = product_functions(true);
    let admit: Vec<String> = funcs.iter().filter(|f| f.body.contains("srr::admit(")).map(|f| f.site()).collect();
    let install: Vec<String> = funcs.iter().filter(|f| f.body.contains("install_kernel(")).filter(|f| f.name != "install_kernel").map(|f| f.site()).collect();
    println!("admit sites: {admit:#?}\ninstall_kernel sites: {install:#?}");
    assert_eq!(admit.len(), 5, "the admit-site census moved: {admit:?}");
    assert_eq!(install.len(), 5, "the install_kernel-site census moved: {install:?}");

    // D-0007 establishes INTACT and never AUTHENTIC or ADMISSIBLE
    let kt = src("runtime/src/kernel_trust.rs");
    assert!(
        !kt.contains("AUTHENTIC") && !kt.contains("admissible"),
        "the D-0007 post-install integrity control now speaks of authenticity or admissibility"
    );

    // the §6 refusal vocabulary is the decision's, exactly
    assert_eq!(bg::REFUSED_ACTIVITIES.len(), 8);
    assert_eq!(bg::DEGRADED_TOKEN.as_bytes(), bg::DEGRADED_TOKEN_BYTES);
    for (class, bullet) in [
        ("normal_privileged_operation", 1u8), ("human_gate_create", 2), ("human_gate_approve", 2),
        ("release_certification", 3), ("trust_policy_mutation", 4), ("privileged_plugin_acquisition", 5),
        ("floor_lower_or_reset", 6), ("present_below_floor_release_as_current", 7),
    ] {
        assert_eq!(bg::refusal_bullet(class), bullet, "{class} is reported under the wrong §6 bullet");
    }

    // the contract v3 canonical import is byte-identical and fails closed
    let contract = std::fs::read(product_root().join("Governance_OS_Capability_Acceptance_Contract_v3.md")).unwrap();
    use sha2::{Digest, Sha256};
    let d = hex::encode(Sha256::digest(&contract));
    println!("Contract v3 canonical import SHA-256: {d}");
    assert!(
        d.starts_with("4c2df291"),
        "the contract v3 canonical import is not byte-identical: {d}"
    );
}

/// **d8 — `SRR-R0-L7`: break-glass works with no network, and no first install was added.**
#[test]
fn d8_break_glass_consults_no_network() {
    let bgs = src("runtime/src/srr/breakglass.rs");
    for needle in ["reqwest", "http://", "https://", "TcpStream", "ureq", "curl"] {
        assert!(
            !bgs.contains(needle),
            "the break-glass module reaches the network via {needle}; OWNER-DECISION-0006 §10 requires it to work offline"
        );
    }
    // authorisation reads local files only
    let auth = split("bg", &cut_tests(&bgs)).into_iter().find(|f| f.name == "authorise").unwrap();
    assert!(auth.body.contains("inbox") || auth.body.contains("read_json") || auth.body.contains("read_dir"));
    assert!(!auth.body.contains("network"), "the authorisation path mentions a network");
}
