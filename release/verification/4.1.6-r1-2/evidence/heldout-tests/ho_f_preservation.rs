//! AR-0029 held-out group F — `AR27-N4` and the preservation obligations, re-measured on candidate 2.
mod common;
use common::mint;

fn wt() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../wt/srr1-r1-verify-2")
        .canonicalize()
        .unwrap()
}

fn rs_files(dir: &std::path::Path, out: &mut Vec<std::path::PathBuf>) {
    let Ok(rd) = std::fs::read_dir(dir) else { return };
    for e in rd.filter_map(|e| e.ok()) {
        let p = e.path();
        if p.is_dir() {
            rs_files(&p, out);
        } else if p.extension().map(|x| x == "rs").unwrap_or(false) {
            out.push(p);
        }
    }
}

fn product_sources() -> Vec<std::path::PathBuf> {
    let mut v = vec![];
    rs_files(&wt().join("runtime/src"), &mut v);
    rs_files(&wt().join("cli/src"), &mut v);
    v.sort();
    v
}

/// `AR27-N4` — the permissive verifier must be out of scope crate-wide, not merely unused.
#[test]
fn f1_the_permissive_ed25519_verifier_is_out_of_scope_crate_wide() {
    let mut importers: Vec<String> = vec![];
    let mut callers: Vec<String> = vec![];
    for p in product_sources() {
        let text = std::fs::read_to_string(&p).unwrap();
        for (n, line) in text.lines().enumerate() {
            let code = line.split("//").next().unwrap_or("");
            if code.contains("use ed25519_dalek") && code.contains("Verifier") {
                importers.push(format!("{}:{}", p.display(), n + 1));
            }
            if code.contains(".verify(") && !code.contains("verify_strict") {
                callers.push(format!("{}:{} {}", p.display(), n + 1, code.trim()));
            }
        }
    }
    println!(
        "AR-0029 F1 — across {} product source files: `Verifier` trait imports = {:?}; bare `.verify(` calls = {:?}",
        product_sources().len(),
        importers,
        callers
    );
    assert!(importers.is_empty(), "the permissive `Verifier` trait is in scope at {importers:?}");

    // behavioural: `verify` and `verify_strict` are one behaviour, including on a malleated signature
    let k = mint::Signer1::seeded(0x91);
    let msg = b"AR-0029 f1";
    let sig = k.sign_hex(msg);
    gov_runtime::srr::crypto::verify(&k.public, &sig, msg).expect("a good signature must verify");
    gov_runtime::srr::crypto::verify_strict(&k.public, &sig, msg).unwrap();

    // S + L is the classic non-canonical scalar the permissive verifier accepts and the strict one refuses.
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
    let a = gov_runtime::srr::crypto::verify(&k.public, &malleated, msg);
    let b = gov_runtime::srr::crypto::verify_strict(&k.public, &malleated, msg);
    assert!(a.is_err() && b.is_err(), "a malleated signature must be refused by both entry points");
    assert_eq!(a.unwrap_err().code, b.unwrap_err().code);
    println!("AR-0029 F1 — `verify` and `verify_strict` are one behaviour, including on a malleated S+L signature");
}

/// `gov` verifies and never signs (`SRR-R0-L4` vacuous).
#[test]
fn f2_no_signing_capability_exists_in_product_source() {
    let mut hits: Vec<String> = vec![];
    for p in product_sources() {
        let text = std::fs::read_to_string(&p).unwrap();
        for (n, line) in text.lines().enumerate() {
            let code = line.split("//").next().unwrap_or("");
            for needle in ["SigningKey", "ed25519_dalek::Signer", "PRIVATE KEY", "from_keypair_bytes"] {
                if !code.contains(needle) {
                    continue;
                }
                // `security/secrets.rs` carries a secret *detector* regex that names the PEM header it looks
                // for. Matching a pattern is the opposite of holding a key, so it is excluded by name.
                if needle == "PRIVATE KEY"
                    && p.ends_with("security/secrets.rs")
                    && code.contains("-----BEGIN")
                {
                    continue;
                }
                hits.push(format!("{}:{} {}", p.display(), n + 1, code.trim()));
            }
        }
    }
    println!("AR-0029 F2 — signing-capability hits in product source: {hits:?}");
    assert!(hits.is_empty(), "product source can sign: {hits:?}");

    // and no relaxation switch of any kind
    for p in product_sources() {
        let text = std::fs::read_to_string(&p).unwrap();
        for needle in ["skip_verify", "skip-verify", "allow_unsigned", "allow-unsigned", "force_unsigned"] {
            if let Some(i) = text.find(needle) {
                // the refused-authority env list names two of these as things to REFUSE; that is the only
                // legitimate appearance.
                let ctx = &text[i.saturating_sub(120)..(i + 60).min(text.len())];
                assert!(
                    ctx.contains("REFUSED_AUTHORITY_ENV") || ctx.contains("GOV_SKIP_VERIFY") || ctx.contains("GOV_ALLOW_UNSIGNED"),
                    "'{needle}' appears at {} outside the refused-authority list",
                    p.display()
                );
            }
        }
    }
}

/// Exactly five `admit` sites, exactly five `install_kernel` call sites, and `install_kernel` has no
/// path-taking variant.
#[test]
fn f3_the_ingress_invariant_still_counts_five_and_five() {
    let mut admits: Vec<String> = vec![];
    let mut installs: Vec<String> = vec![];
    for p in product_sources() {
        let text = std::fs::read_to_string(&p).unwrap();
        for (n, line) in text.lines().enumerate() {
            let code = line.split("//").next().unwrap_or("");
            if code.contains("srr::admit(") {
                admits.push(format!("{}:{}", p.display(), n + 1));
            }
            if (code.contains("install_kernel(&") || code.contains("install_kernel(a,"))
                && !code.contains("fn install_kernel")
            {
                installs.push(format!("{}:{}", p.display(), n + 1));
            }
        }
    }
    println!("AR-0029 F3 — admit sites {}: {admits:?}", admits.len());
    println!("AR-0029 F3 — install_kernel call sites {}: {installs:?}", installs.len());
    assert_eq!(admits.len(), 5, "admit call sites: {admits:?}");
    assert_eq!(installs.len(), 5, "install_kernel call sites: {installs:?}");

    let kernel = std::fs::read_to_string(wt().join("runtime/src/kernel.rs")).unwrap();
    assert!(
        kernel.contains("pub fn install_kernel(\n    auth: &crate::srr::AuthenticatedRelease,"),
        "install_kernel must take a typed authenticated-release value"
    );
    assert!(
        !kernel.contains("pub fn install_kernel_from_path"),
        "a path-taking variant exists"
    );
}

/// The "no-bypass" property, probed rather than assumed: is `AuthenticatedRelease` genuinely constructible only
/// by `admit`?
///
/// It is not *type*-enforced — every field of `AuthenticatedRelease`, `Staged`, `MachineState` and `Floors` is
/// `pub`, so a struct literal compiles from outside the crate (this test is that struct literal, and it
/// compiles). The property that does hold is the enumerated one in `f3`: `install_kernel` takes no path, so no
/// ingress can install from a source directory by mistake, and the five/five census makes a hand-built value
/// visible. Recorded as an observation about the claim's wording, not as a reachable bypass: building one
/// requires writing new product or caller source, which is the thing the census inspects.
#[test]
fn f4_authenticated_release_is_not_type_constructor_enforced() {
    let m = mint::scenario("f4");
    let ms = m.open();
    let forged = gov_runtime::srr::AuthenticatedRelease {
        ingress: gov_runtime::srr::Ingress::Update,
        product: mint::PRODUCT.into(),
        release_version: "9.9.9".into(),
        sequence: 9999,
        channel: "stable".into(),
        repository: String::new(),
        authenticity: gov_runtime::srr::Authenticity::Authentic,
        currency: gov_runtime::srr::Currency::Current,
        posture: gov_runtime::srr::Posture::Provisioned,
        payload_hash: "00".repeat(32),
        kernel_manifest_hash: "00".repeat(32),
        below_floor: false,
        break_glass: None,
        floors: gov_runtime::srr::state::Floors {
            product: mint::PRODUCT.into(),
            ..Default::default()
        },
        staged: gov_runtime::srr::staging::Staged {
            id: "forged".into(),
            payload_dir: m.home.join("not-staged"),
            files: Default::default(),
            payload_hash: "00".repeat(32),
            kernel_manifest_hash: "00".repeat(32),
            version: "9.9.9".into(),
            manifest: serde_json::Value::Null,
        },
        machine: ms,
        release_metadata_sha256: String::new(),
        migrations: vec![],
        delegations: vec![],
        notes: vec![],
    };
    println!(
        "AR-0029 F4 — OBSERVATION: an `AuthenticatedRelease` claiming authenticity={:?} at sequence {} was \
         constructed outside `admit`, from a crate that only depends on gov-runtime. All fields are `pub`, so \
         \"constructible only by admit\" is an enumeration property (5 admit / 5 install_kernel sites), not a \
         type-system property. Non-blocking: reaching it requires new product or caller source.",
        forged.authenticity, forged.sequence
    );
    assert_eq!(forged.verified_payload(), m.home.join("not-staged"));
}

/// D-0007 stays a separate control that establishes *intact*, never *authentic* or *admissible*.
#[test]
fn f5_d0007_remains_independent_of_the_srr_verdicts() {
    let kt = std::fs::read_to_string(wt().join("runtime/src/kernel_trust.rs")).unwrap();
    for forbidden in [
        "srr::admit",
        "AuthenticatedRelease",
        "Authenticity",
        "breakglass",
        "below_floor",
        "Floors",
    ] {
        assert!(
            !kt.contains(forbidden),
            "D-0007 (`kernel_trust`) reads `{forbidden}` from the SRR verdicts"
        );
    }
    // and the SRR side reads no D-0007 record when deciding
    let verifier = std::fs::read_to_string(wt().join("runtime/src/srr/verifier.rs")).unwrap();
    let admit_body = verifier.split("fn admit_inner").nth(1).unwrap();
    assert!(
        !admit_body.contains("kernel_trust"),
        "the verifier consults the D-0007 integrity control when deciding admissibility"
    );
    println!("AR-0029 F5 — the three predicates stay separate: no reference in either direction at decision time");
}

/// Contract v3 canonical import is byte-identical to the owner source and is hash-pinned in code.
#[test]
fn f6_contract_v3_canonical_import_is_byte_identical() {
    let owner = wt().join("Governance_OS_Capability_Acceptance_Contract_v3.md");
    let imported = wt().join("framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md");
    let a = std::fs::read(&owner).unwrap();
    let b = std::fs::read(&imported).unwrap();
    let da = mint::digest(&a);
    println!("AR-0029 F6 — owner source {da}, canonical import {}", mint::digest(&b));
    assert_eq!(a, b, "the canonical import is not byte-identical to the owner source");
    assert_eq!(da, "4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3");
    let contracts = std::fs::read_to_string(wt().join("runtime/src/contracts.rs")).unwrap();
    assert!(
        contracts.contains(&da),
        "the owner-source digest is not pinned in `contracts.rs`"
    );
    assert!(contracts.contains("CONTRACT_SOURCE_DIVERGED"), "the divergence refusal is gone");
}

/// Floors are monotonic and advance only from an authenticated observation.
#[test]
fn f7_floors_are_monotonic_and_only_rise_from_verified_facts() {
    let mut f = gov_runtime::srr::state::Floors {
        product: mint::PRODUCT.into(),
        ..Default::default()
    };
    f.raise_release("4.1.5", 15, true);
    f.raise_minimum_secure("4.1.2", 12, "src");
    f.raise_metadata("release", 7);

    f.raise_release("4.0.0", 1, true);
    f.raise_minimum_secure("4.0.0", 1, "src");
    f.raise_metadata("release", 1);
    assert_eq!(f.release_high_water_sequence, 15);
    assert_eq!(f.release_high_water_version, "4.1.5");
    assert_eq!(f.minimum_secure_sequence, 12);
    assert_eq!(f.metadata_floor("release"), 7);

    // an unauthenticated observation raises nothing
    let before = f.release_high_water_sequence;
    f.raise_release("9.9.9", 999, false);
    assert_eq!(f.release_high_water_sequence, before, "an unverified install raised a floor");
    println!("AR-0029 F7 — floors monotonic; an unauthenticated observation raises nothing");
}
