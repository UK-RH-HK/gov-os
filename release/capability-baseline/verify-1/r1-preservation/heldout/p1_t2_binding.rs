//! **P2-AR-0044 — the new cross-machine T2 binding authority.**
//!
//! `runtime/src/srr/binding.rs` and `runtime/src/t2.rs` are new since `srr1-r1-accepted`. They create a *new*
//! authority: a key whose possession makes a repository file an honoured T2 fact on another of the owner's
//! machines. Frozen R1 items 2 ("candidate/source files cannot create their own trusted identity"), 9 ("project,
//! CLI, environment, model and plugin inputs cannot create trust or approval"), 10 (ARCH-0003 provisioning) and
//! 1/3 (the verifier is used correctly; wrong keys, replay, downgrade, expiry fail closed) all reach it.
//!
//! The question each test asks is the frozen one: **can anything other than the owner's provisioned root create
//! this authority, and does `gov` ever sign?**
//!
//! Run single-threaded: the machine helpers set process-wide environment.
mod common;
use common::*;
use gov_runtime::t2::{self, Binding};
use serde_json::json;

/// Mint a root that delegates `t2-binding` to the owner's binding-role key, provision `m` with it, and return the
/// root bytes so a second machine can be provisioned with the same anchor.
fn provisioned_owner_machine(tag: &str) -> (Machine, String, ed25519_dalek::SigningKey) {
    let rootk = signer(1);
    let bindk = signer(2);
    let (rid, bid) = (kid(&rootk), kid(&bindk));
    let doc = root_doc(
        1,
        &rid,
        &[("t2-binding", vec![&bid], 1)],
        &[(&rid, &rootk), (&bid, &bindk)],
    );
    let bytes = envelope(&doc, &[(&rid, &rootk)]);
    let m = Machine::new(tag);
    let (ok, v) = m.provision(&bytes);
    assert!(ok, "the product's own provisioning command failed: {}", text(&v));
    assert!(m.is_provisioned(), "provisioning left no latch");
    (m, bytes, bindk)
}

/// **a1 — repository content cannot create an honoured T2 fact.**
///
/// The whole point of the primitive. A hand-written record carrying a plausible `os_binding` block — including one
/// copied verbatim from a genuinely sealed record — must not verify.
#[test]
fn a1_repository_content_cannot_manufacture_a_verified_t2_fact() {
    let m = Machine::new("a1");
    m.enter();

    // A genuine seal, written by the primitive on this machine.
    let mut genuine = json!({"id": "GATE-1", "type": "human-gate", "status": "ANSWERED", "answer": "yes"});
    t2::seal_value(&mut genuine, "", "gate answer").expect("seal");
    assert!(
        matches!(t2::verify_value(&genuine, ""), Binding::Verified { .. }),
        "a record the OS just sealed must verify: {genuine}"
    );

    // 1. no seal at all — a plain hand-written record.
    let hand = json!({"id": "GATE-2", "type": "human-gate", "status": "ANSWERED", "answer": "yes"});
    assert!(
        matches!(t2::verify_value(&hand, ""), Binding::Unsealed),
        "an unsealed hand-written record must be Unsealed, was {:?}",
        t2::verify_value(&hand, "")
    );

    // 2. an invented seal block of the right shape.
    let mut invented = hand.clone();
    invented[t2::SEAL_FIELD] = json!({
        "alg": t2::SEAL_ALG, "key_id": "0123456789abcdef", "operation": "gate answer",
        "at": "2026-09-20T00:00:00Z", "mac": "0".repeat(64),
    });
    assert!(
        !matches!(t2::verify_value(&invented, ""), Binding::Verified { .. }),
        "an invented seal must never verify"
    );

    // 3. the genuine seal LIFTED onto different content — the interesting forgery.
    let mut lifted = json!({"id": "GATE-3", "type": "human-gate", "status": "ANSWERED", "answer": "yes"});
    lifted[t2::SEAL_FIELD] = genuine[t2::SEAL_FIELD].clone();
    assert!(
        !matches!(t2::verify_value(&lifted, ""), Binding::Verified { .. }),
        "a seal lifted from another record must not verify: {:?}",
        t2::verify_value(&lifted, "")
    );

    // 4. one flipped flag on the genuine record.
    let mut tampered = genuine.clone();
    tampered["answer"] = json!("no");
    assert!(
        matches!(t2::verify_value(&tampered, ""), Binding::Broken { .. }),
        "a modified sealed record must be Broken, was {:?}",
        t2::verify_value(&tampered, "")
    );
}

/// **a2 — a foreign machine's seal is not honoured, and the refusal is typed.**
///
/// Two unprovisioned machines, each with its own machine-scope key. A record sealed on one is `Foreign` on the
/// other: a clone of a machine-scope record does not travel. (P2-ADJ-0002; frozen R1 item 9.)
#[test]
fn a2_a_foreign_machines_seal_is_not_honoured() {
    let one = Machine::new("a2-one");
    let two = Machine::new("a2-two");

    one.enter();
    let mut rec = json!({"id": "D-1", "type": "decision", "status": "ACCEPTED"});
    t2::seal_value(&mut rec, "", "decision accept").expect("seal on machine one");
    assert!(matches!(t2::verify_value(&rec, ""), Binding::Verified { .. }));

    two.enter();
    let b = t2::verify_value(&rec, "");
    assert!(
        matches!(b, Binding::Foreign { .. }),
        "machine one's record must be Foreign on machine two, was {b:?}"
    );
    assert!(
        !matches!(b, Binding::Verified { .. }),
        "a foreign seal must never be honoured"
    );
}

/// **a3 — the authority is delegated from the provisioned root; an unprovisioned machine cannot be bound.**
///
/// Frozen R1 item 10 and OD-P2-02: the binding authority exists only through ARCH-0003 §8 provisioning.
#[test]
fn a3_an_unprovisioned_machine_cannot_be_bound() {
    let m = Machine::new("a3");
    let key = binding_key(7);
    let auth = envelope(
        &authority_doc("owner-a3", 1, &[(&key, "active")], None),
        &[(&kid(&signer(2)), &signer(2))],
    );
    let (ok, v) = m.bind(&auth, &key);
    assert!(!ok, "binding an unprovisioned machine must be refused: {}", text(&v));
    assert_eq!(
        code(&v),
        "T2_BINDING_UNPROVISIONED",
        "the refusal must be typed and name the unprovisioned posture: {}",
        text(&v)
    );
    // The availability rule: the refusal names its remedy.
    assert!(
        text(&v).contains("trust provision"),
        "a refusal must name its listed remedy: {}",
        text(&v)
    );
}

/// **a4 — an authority signed by anything other than the root's delegated `t2-binding` role is refused.**
///
/// Wrong signer, role confusion, an undelegated root, and an unsigned document. This is frozen R1 item 3 applied
/// to the new authority, and item 2: source files cannot create their own trusted identity.
#[test]
fn a4_only_the_root_delegated_role_can_create_a_binding_authority() {
    let (m, _root_bytes, bindk) = provisioned_owner_machine("a4");
    let key = binding_key(9);
    let doc = authority_doc("owner-a4", 1, &[(&key, "active")], None);

    // (i) signed by an attacker's key but PRESENTED under the delegated role's key id — the substitution a
    //     document would have to get away with for repository-side material to create this authority.
    let attacker = signer(99);
    let forged = envelope_raw(&doc, vec![serde_json::json!({"keyid": kid(&bindk), "sig": sign_hex(&attacker, &doc)})]);
    let (ok, v) = m.bind(&forged, &key);
    assert!(!ok, "a forged signature must be refused: {}", text(&v));
    assert_eq!(code(&v), "SRR_THRESHOLD_NOT_MET", "typed refusal expected, got {}", text(&v));

    // (ii) signed by the ROOT key rather than the delegated t2-binding key (role confusion).
    let rolemix = envelope(&doc, &[(&kid(&signer(1)), &signer(1))]);
    let (ok, v) = m.bind(&rolemix, &key);
    assert!(!ok, "role confusion must be refused: {}", text(&v));
    assert_eq!(code(&v), "SRR_THRESHOLD_NOT_MET", "typed refusal expected, got {}", text(&v));

    // (iii) no signatures at all.
    let unsigned = envelope_raw(&doc, vec![]);
    let (ok, v) = m.bind(&unsigned, &key);
    assert!(!ok, "an unsigned authority must be refused: {}", text(&v));
    assert_eq!(code(&v), "SRR_METADATA_UNSIGNED", "typed refusal expected, got {}", text(&v));

    // (iv) the genuine article is accepted — so (i)-(iii) are not vacuous passes (P2-ADJ-0003).
    let good = envelope(&doc, &[(&kid(&bindk), &bindk)]);
    let (ok, v) = m.bind(&good, &key);
    assert!(ok, "the owner's genuine authority must be accepted: {}", text(&v));
}

/// **a5 — a binding authority may not be sourced from the repository, nor supplied through the environment.**
///
/// ARCH-0003 §8 ("never from the repository") and frozen R1 item 9.
#[test]
fn a5_the_authority_cannot_come_from_the_repository_or_the_environment() {
    let (m, _b, bindk) = provisioned_owner_machine("a5");
    let key = binding_key(11);
    let auth = envelope(
        &authority_doc("owner-a5", 1, &[(&key, "active")], None),
        &[(&kid(&bindk), &bindk)],
    );

    // Placed inside the project repository, which is the one place ARCH-0003 §8 forbids.
    let af = m.project.join("governance").join("t2-binding-authority.json");
    let kf = m.project.join("governance").join("binding-key.json");
    write(&af, &auth);
    write(&kf, &(serde_json::to_string_pretty(&key_file_doc(&key)).unwrap() + "\n"));
    let (ok, v) = m.gov_json(&[
        "trust", "bind", "--authority", af.to_str().unwrap(), "--key", kf.to_str().unwrap(),
    ]);
    assert!(!ok, "a repository-sourced authority must be refused: {}", text(&v));
    let c = code(&v);
    assert!(
        c.contains("REPOSITORY") || text(&v).contains("repository"),
        "the refusal must name the repository source, got {c}: {}",
        text(&v)
    );

    // Every refused-authority environment variable is still refused at the verifier, including for `trust bind`.
    for var in [
        "GOV_TRUST_OVERRIDE", "GOV_SKIP_VERIFY", "GOV_ALLOW_UNSIGNED",
        "GOV_RELEASE_AUTHORITY", "GOV_HUMAN_GATE_APPROVED",
    ] {
        let good_af = m.admin.join("a.json");
        let good_kf = m.admin.join("k.json");
        write(&good_af, &auth);
        write(&good_kf, &(serde_json::to_string_pretty(&key_file_doc(&key)).unwrap() + "\n"));
        let out = std::process::Command::new(gov_bin())
            .args(["trust", "bind", "--authority", good_af.to_str().unwrap(),
                   "--key", good_kf.to_str().unwrap(), "--json"])
            .current_dir(&m.project)
            .env_clear()
            .env("PATH", std::env::var("PATH").unwrap_or_default())
            .env("HOME", &m.home)
            .env("XDG_STATE_HOME", m.home.join(".local/state"))
            .env("GOV_MACHINE_STATE_DIR", &m.state)
            .env(var, "1")
            .output()
            .unwrap();
        let so = String::from_utf8_lossy(&out.stdout).to_string();
        assert!(
            !out.status.success() && so.contains("SRR_ENV_CANNOT_CREATE_AUTHORITY"),
            "{var} must be refused as authority by `trust bind`: {so}"
        );
    }
}

/// **a6 — authority version rollback and same-version conflict are refused (replay / downgrade, item 3).**
#[test]
fn a6_authority_rollback_and_conflict_fail_closed() {
    let (m, _b, bindk) = provisioned_owner_machine("a6");
    let k1 = binding_key(21);
    let k2 = binding_key(22);
    let bid = kid(&bindk);

    let v2 = envelope(
        &authority_doc("owner-a6", 2, &[(&k1, "active")], None),
        &[(&bid, &bindk)],
    );
    let (ok, v) = m.bind(&v2, &k1);
    assert!(ok, "version 2 must install: {}", text(&v));

    // Downgrade to version 1 — would re-enable a key the owner revoked.
    let v1 = envelope(
        &authority_doc("owner-a6", 1, &[(&k2, "active")], None),
        &[(&bid, &bindk)],
    );
    let (ok, v) = m.bind(&v1, &k2);
    assert!(!ok, "an older authority version must be refused: {}", text(&v));
    assert_eq!(code(&v), "T2_BINDING_AUTHORITY_ROLLBACK", "typed refusal expected: {}", text(&v));

    // A *different* document at the same accepted version.
    let v2b = envelope(
        &authority_doc("owner-a6", 2, &[(&k2, "active")], None),
        &[(&bid, &bindk)],
    );
    let (ok, v) = m.bind(&v2b, &k2);
    assert!(!ok, "a conflicting same-version authority must be refused: {}", text(&v));
    assert_eq!(code(&v), "T2_BINDING_AUTHORITY_CONFLICT", "typed refusal expected: {}", text(&v));
}

/// **a7 — a key the authority does not authorise by id AND commitment is refused.**
#[test]
fn a7_an_unauthorised_or_mismatched_key_is_refused() {
    let (m, _b, bindk) = provisioned_owner_machine("a7");
    let good = binding_key(31);
    let other = binding_key(32);
    let auth = envelope(
        &authority_doc("owner-a7", 1, &[(&good, "active")], None),
        &[(&kid(&bindk), &bindk)],
    );

    // A key the document does not list at all.
    let (ok, v) = m.bind(&auth, &other);
    assert!(!ok, "an unlisted key must be refused: {}", text(&v));
    assert_eq!(code(&v), "T2_BINDING_KEY_NOT_AUTHORISED", "typed refusal expected: {}", text(&v));

    // A document that publishes the right key id against the WRONG commitment.
    let mut doc = authority_doc("owner-a7b", 1, &[(&good, "active")], None);
    doc["keys"][0]["commitment"] = json!(gov_runtime::srr::binding::commitment_of(&other));
    let auth2 = envelope(&doc, &[(&kid(&bindk), &bindk)]);
    let (ok, v) = m.bind(&auth2, &good);
    assert!(!ok, "a commitment mismatch must be refused: {}", text(&v));
    assert_eq!(code(&v), "T2_BINDING_KEY_MISMATCH", "typed refusal expected: {}", text(&v));
}

/// **a8 — a root that does not delegate `t2-binding` cannot authorise any binding authority.**
///
/// The delegation is the whole chain of custody: without it there is no authority, however well signed.
#[test]
fn a8_a_root_without_the_delegation_authorises_nothing() {
    let rootk = signer(41);
    let rid = kid(&rootk);
    // No `t2-binding` role at all.
    let doc = root_doc(1, &rid, &[], &[(&rid, &rootk)]);
    let m = Machine::new("a8");
    let (ok, v) = m.provision(&envelope(&doc, &[(&rid, &rootk)]));
    assert!(ok, "provisioning must succeed: {}", text(&v));

    let key = binding_key(43);
    let auth = envelope(
        &authority_doc("owner-a8", 1, &[(&key, "active")], None),
        &[(&kid(&signer(2)), &signer(2))],
    );
    let (ok, v) = m.bind(&auth, &key);
    assert!(!ok, "no delegation must mean no authority: {}", text(&v));
    assert_eq!(code(&v), "T2_BINDING_NOT_DELEGATED", "typed refusal expected: {}", text(&v));
    assert!(
        text(&v).contains("root-update"),
        "the refusal must name how the owner adds the delegation: {}",
        text(&v)
    );
}

/// **a9 — an authority that does not list this machine cannot bind it.**
#[test]
fn a9_a_machine_the_authority_does_not_list_is_refused() {
    let (m, _b, bindk) = provisioned_owner_machine("a9");
    let key = binding_key(51);
    let auth = envelope(
        &authority_doc("owner-a9", 1, &[(&key, "active")], Some(vec!["some-other-machine".into()])),
        &[(&kid(&bindk), &bindk)],
    );
    let (ok, v) = m.bind(&auth, &key);
    assert!(!ok, "an unlisted machine must be refused: {}", text(&v));
    assert_eq!(
        code(&v),
        "T2_BINDING_MACHINE_NOT_AUTHORISED",
        "typed refusal expected: {}",
        text(&v)
    );
}

/// **a10 — cross-machine continuity actually works, and only under the owner's authority (P2-ADJ-0002).**
///
/// Two machines of the same owner, both provisioned under the same root and bound to the same authority: a fact
/// sealed on one is honoured on the other. A third machine of a *different* owner is not.
///
/// This is the positive control for a1/a2: without it, "nothing is honoured anywhere" would pass every test above.
#[test]
fn a10_owner_facts_travel_between_bound_machines_and_no_further() {
    let rootk = signer(61);
    let bindk = signer(62);
    let (rid, bid) = (kid(&rootk), kid(&bindk));
    let root_bytes = envelope(
        &root_doc(1, &rid, &[("t2-binding", vec![&bid], 1)], &[(&rid, &rootk), (&bid, &bindk)]),
        &[(&rid, &rootk)],
    );
    let key = binding_key(63);
    let auth = envelope(
        &authority_doc("owner-a10", 1, &[(&key, "active")], None),
        &[(&bid, &bindk)],
    );

    let one = Machine::new("a10-one");
    let two = Machine::new("a10-two");
    for m in [&one, &two] {
        let (ok, v) = m.provision(&root_bytes);
        assert!(ok, "provision {}: {}", m.name, text(&v));
        let (ok, v) = m.bind(&auth, &key);
        assert!(ok, "bind {}: {}", m.name, text(&v));
    }

    one.enter();
    let mut rec = json!({"id": "GATE-X", "type": "human-gate", "status": "ANSWERED"});
    t2::seal_value(&mut rec, "", "gate answer").expect("seal on machine one");
    let b1 = t2::verify_value(&rec, "");
    assert!(matches!(b1, Binding::Verified { .. }), "machine one must honour its own seal: {b1:?}");

    two.enter();
    let b2 = t2::verify_value(&rec, "");
    assert!(
        matches!(b2, Binding::Verified { .. }),
        "P2-ADJ-0002: an owner fact sealed on machine one must be honoured on machine two, was {b2:?}"
    );

    // A different owner: different root, different authority, different key.
    let orootk = signer(71);
    let obindk = signer(72);
    // The other owner's OWN key ids: a key id is SHA-256 of its material, so the first owner's ids cannot be
    // reused for different keys (the product refuses that as SRR_KEYID_MISMATCH).
    let (orid, obid) = (kid(&orootk), kid(&obindk));
    let o_root = envelope(
        &root_doc(1, &orid, &[("t2-binding", vec![&obid], 1)], &[(&orid, &orootk), (&obid, &obindk)]),
        &[(&orid, &orootk)],
    );
    let okey = binding_key(73);
    let oauth = envelope(
        &authority_doc("other-owner", 1, &[(&okey, "active")], None),
        &[(&obid, &obindk)],
    );
    let three = Machine::new("a10-other-owner");
    let (ok, v) = three.provision(&o_root);
    assert!(ok, "provision other owner: {}", text(&v));
    let (ok, v) = three.bind(&oauth, &okey);
    assert!(ok, "bind other owner: {}", text(&v));

    three.enter();
    let b3 = t2::verify_value(&rec, "");
    assert!(
        !matches!(b3, Binding::Verified { .. }),
        "a foreign owner's machine must NOT honour this owner's fact, was {b3:?}"
    );
}

/// **a11 — `gov` verifies and never signs (SRR-R0-L4), including for this new authority.**
///
/// There is no command that emits a `t2-binding-authority`, and no signing capability reachable from the binary.
#[test]
fn a11_gov_has_no_command_that_mints_a_binding_authority() {
    let m = Machine::new("a11");
    // Every `gov trust` subcommand, from the product's own help.
    let (_ok, help, _e) = m.gov(&["trust", "--help"]);
    // Read the Commands: block and check the SUBCOMMAND NAMES, not prose (the help legitimately says
    // "owner-signed" and "Signed Release Root" while offering no signing operation).
    let names: Vec<String> = help
        .lines()
        .skip_while(|l| !l.starts_with("Commands:"))
        .skip(1)
        .take_while(|l| l.starts_with("  ") && !l.trim().is_empty())
        .filter_map(|l| l.split_whitespace().next().map(|s| s.to_string()))
        .collect();
    assert!(!names.is_empty(), "could not read the subcommand list: {help}");
    for n in &names {
        assert!(
            !["sign", "mint", "issue", "keygen", "generate-key", "authorise", "authorize"]
                .contains(&n.as_str()),
            "`gov trust` must expose no minting/signing subcommand, found '{n}' in {names:?}"
        );
    }
    // And the source carries no signing capability at all (the structural half is p6::f6).
    for rel in ["runtime/src/srr/binding.rs", "runtime/src/t2.rs"] {
        let s = src(rel);
        assert!(
            !s.contains("SigningKey") && !s.contains("ed25519_dalek::Signer"),
            "{rel} must carry no ed25519 signing capability"
        );
    }
}

/// **a12 — an expired binding authority is refused, with a typed result.**
///
/// The common-protocol cross-machine attack list names "an expired or rolled-back authority" separately. `a6`
/// covers rollback; this covers expiry, including the three non-canonical `expires` forms the profile treats as
/// expired rather than trying to compare (AR27-N1's fix, which must still bind the NEW document type).
#[test]
fn a12_an_expired_or_non_canonical_authority_is_refused() {
    let (m, _b, bindk) = provisioned_owner_machine("a12");
    let key = binding_key(81);
    let bid = kid(&bindk);

    for (label, expires) in [
        ("plainly in the past", "2001-01-01T00:00:00Z"),
        ("absent", ""),
        ("lowercase t/z, not the emitted form", "2039-01-01t00:00:00z"),
        ("a numeric offset that does not order lexicographically", "2039-01-01T00:00:00+14:00"),
        ("fractional seconds", "2039-01-01T00:00:00.000Z"),
    ] {
        let mut doc = authority_doc("owner-a12", 1, &[(&key, "active")], None);
        doc["expires"] = serde_json::json!(expires);
        let (ok, v) = m.bind(&envelope(&doc, &[(&bid, &bindk)]), &key);
        assert!(!ok, "an authority whose expiry is {label} must be refused: {}", text(&v));
        assert_eq!(
            code(&v),
            "T2_BINDING_AUTHORITY_EXPIRED",
            "expiry refusal must be typed ({label}): {}",
            text(&v)
        );
    }

    // Positive control: the same document with the canonical form this profile emits IS accepted, so the five
    // refusals above are the expiry gate working rather than the document being rejected for some other reason.
    let good = authority_doc("owner-a12", 1, &[(&key, "active")], None);
    let (ok, v) = m.bind(&envelope(&good, &[(&bid, &bindk)]), &key);
    assert!(ok, "the same authority with a canonical future expiry must be accepted: {}", text(&v));
}

/// **a13 — nothing secret is in any repository (ARCH-0003 §8; the common-protocol cross-machine attack).**
///
/// The binding key is the one piece of material whose possession lets a machine write facts the owner's other
/// machines honour. After a full provision-and-bind ceremony, and after the OS has sealed a record, no byte of it
/// may be anywhere under the project tree — and the key file itself must not be world-readable.
#[test]
fn a13_no_binding_secret_is_written_into_the_repository() {
    use std::os::unix::fs::PermissionsExt;
    let (m, _b, bindk) = provisioned_owner_machine("a13");
    let key = binding_key(91);
    let auth = envelope(
        &authority_doc("owner-a13", 1, &[(&key, "active")], None),
        &[(&kid(&bindk), &bindk)],
    );
    let (ok, v) = m.bind(&auth, &key);
    assert!(ok, "bind must succeed: {}", text(&v));

    // Make the OS actually seal something, so any leak path a seal might take is exercised.
    m.enter();
    let mut rec = serde_json::json!({"id": "D-A13", "type": "decision", "status": "ACCEPTED"});
    gov_runtime::t2::seal_value(&mut rec, "", "decision accept").expect("seal");
    assert!(matches!(gov_runtime::t2::verify_value(&rec, ""), Binding::Verified { .. }));

    let key_hex = hex_of(&key);
    let mut leaks = vec![];
    fn walk(d: &std::path::Path, needle: &str, out: &mut Vec<String>) {
        let Ok(rd) = std::fs::read_dir(d) else { return };
        for e in rd.flatten() {
            let p = e.path();
            if p.is_dir() {
                walk(&p, needle, out);
            } else if let Ok(bytes) = std::fs::read(&p) {
                if String::from_utf8_lossy(&bytes).contains(needle) {
                    out.push(p.display().to_string());
                }
            }
        }
    }
    walk(&m.project, &key_hex, &mut leaks);
    assert!(
        leaks.is_empty(),
        "the binding key must appear nowhere in the repository, found in {leaks:?}"
    );

    // It does live in protected machine state, outside every repository, and not world-readable.
    let mut found_key_file = None;
    fn find(d: &std::path::Path, needle: &str, out: &mut Option<std::path::PathBuf>) {
        let Ok(rd) = std::fs::read_dir(d) else { return };
        for e in rd.flatten() {
            let p = e.path();
            if p.is_dir() {
                find(&p, needle, out);
            } else if std::fs::read(&p)
                .map(|b| String::from_utf8_lossy(&b).contains(needle))
                .unwrap_or(false)
            {
                *out = Some(p);
            }
        }
    }
    find(&m.state, &key_hex, &mut found_key_file);
    let kp = found_key_file.expect("the bound key must be held in protected machine state");
    assert!(!kp.starts_with(&m.project), "the key must live outside the repository, found {kp:?}");
    let mode = std::fs::metadata(&kp).unwrap().permissions().mode() & 0o077;
    assert_eq!(mode, 0, "the binding key must not be group/world readable, mode {:o}", mode);
}
