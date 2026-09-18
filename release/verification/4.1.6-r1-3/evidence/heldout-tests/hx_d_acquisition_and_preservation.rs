//! AR-0031 held-out group D — **§6 bullet 5's weaker sink, the `Clearance` trade, and the R1 preservation set.**
//!
//! d1–d4 judge the repair's disclosed weakness 3 (bullet 5's sink is the acquisition *decision*, not a
//! byte-installing primitive) and weakness 4 (`Clearance` is a witness, not a lifetime-scoped capability).
//! d5–d12 are the frozen R1 preservation items that must still hold.
//!
//! `OBSERVED:` assertions pin a weakness and are expected to FAIL.
mod common;
use common::bench::{self, PRODUCT};

use gov_runtime::srr::breakglass as bg;
use gov_runtime::srr::plugins::{self, Acquisition};
use serde_json::json;

// ------------------------------------------------------------------------ d1-d4: §6 bullet 5 and `Clearance`

/// d1 — the sink refuses below floor for a privileged capability, in every acquisition class.
#[test]
fn d1_the_acquisition_sink_refuses_a_privileged_capability_below_floor() {
    let (_x, root) = bench::isolated_default_root("d1");
    bench::mark_degraded(&root, PRODUCT);

    let privileged = json!({"required_permission_classes": ["SYSTEM_INSTALL"]});
    for class in [Acquisition::BuiltIn, Acquisition::LocalProject, Acquisition::RemotelyAcquired] {
        let e = plugins::guard_acquisition("acme/x", &privileged, class, &[], "stable")
            .expect_err("a privileged acquisition completed below floor");
        assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED", "class {class:?}");
        assert_eq!(e.details["refused_class"], "privileged_plugin_acquisition");
    }
}

/// d2 — but whether the sink asks §6 at all is decided **by the descriptor**.
///
/// `guard_acquisition` calls `guard_effect` only `if is_privileged(descriptor)`, and `is_privileged` reads
/// `required_permission_classes` straight out of the descriptor. The module's own stated principle is that a
/// descriptor cannot move a capability into a weaker class — true of the `Acquisition` class, which is derived
/// from where the bytes are, and **not** true of the privileged/unprivileged split that gates the §6 check.
#[test]
fn d2_the_descriptor_decides_whether_section_6_is_consulted_at_all() {
    let (_x, root) = bench::isolated_default_root("d2");
    bench::mark_degraded(&root, PRODUCT);

    // A descriptor that declares no privileged class never reaches the §6 check, even below floor, even when the
    // bytes came from outside this machine.
    let quiet = json!({"required_permission_classes": ["READ_ONLY"]});
    let r = plugins::guard_acquisition("acme/quiet", &quiet, Acquisition::RemotelyAcquired, &[], "stable");
    assert!(
        r.is_ok(),
        "baseline: an unprivileged remote capability is not a §6 bullet 5 effect"
    );

    // ... and one that declares nothing at all is likewise unprivileged.
    let silent = json!({});
    assert!(
        plugins::guard_acquisition("acme/silent", &silent, Acquisition::RemotelyAcquired, &[], "stable").is_ok()
    );

    // This is defensible — §6 bullet 5 names *privileged* acquisition — but it means the §6 decision for this
    // bullet is taken on self-asserted data, unlike bullets 2, 3 and 4 whose sinks ask unconditionally.
    let plugins_rs = bench::src("runtime/src/srr/plugins.rs");
    let body = bench::fn_body(&plugins_rs, "guard_acquisition");
    assert!(
        body.contains("if privileged {"),
        "guard_acquisition no longer gates the §6 call on the descriptor; re-derive this scenario"
    );
    let is_priv = bench::fn_body(&plugins_rs, "is_privileged");
    assert!(
        is_priv.contains("required_permission_classes"),
        "is_privileged no longer reads the descriptor; re-derive this scenario"
    );
}

/// d3 — the census names ONE sink for bullet 5. `tools::install` is a second primitive that reaches the same
/// effect and never touches it. Below floor it is refused, but only by the operation-level guard — the control
/// repair 2 argued was insufficient as a class control.
#[test]
fn d3_tools_install_reaches_the_bullet_5_effect_without_the_sink() {
    let tools_rs = bench::src("runtime/src/tools.rs");
    let install = bench::fn_body(&tools_rs, "install");
    assert!(!install.is_empty(), "`tools::install` not found");

    // it IS covered at the operation level ...
    assert!(
        install.contains(r#"guard_write(p, "tools install")"#),
        "`tools install` lost its operation-level guard"
    );
    // ... and below floor that guard refuses, so there is no live bypass today.
    let (_x, root) = bench::isolated_default_root("d3");
    bench::mark_degraded(&root, PRODUCT);
    let e = bg::guard_light(PRODUCT, "tools install").expect_err("`tools install` must be refused below floor");
    assert_eq!(e.details["refused_class"], "privileged_plugin_acquisition");

    // ... but it never reaches the census's claimed sole sink.
    assert!(
        install.contains("guard_acquisition"),
        "OBSERVED: `tools::install` installs a capability and never calls `plugins::guard_acquisition`, the \
         census's claimed SOLE sink for §6 bullet 5. `SECTION_6_SINKS` therefore names one primitive for a \
         bullet the product realises in two places. No live bypass follows today, because the operation-level \
         guard refuses `tools install` below floor — but that is exactly the operation-level coverage the repair \
         argued was insufficient as a class control, so for this bullet the class control the repair claims does \
         not exist."
    );
}

/// d4 — the `Clearance` trade, stated so it can be disagreed with explicitly.
///
/// The repair's position: a caller-supplied token is a decision taken earlier, so `set_root_metadata`,
/// `release::build` and `guard_acquisition` ask at the instant of the effect instead. This verifier's position:
/// the two are not alternatives, and the sink that uses the witness is the only one the compiler protects.
#[test]
fn d4_the_clearance_witness_is_not_a_capability_and_its_guarantee_stops_at_the_module_boundary() {
    let bg_rs = bench::src("runtime/src/srr/breakglass.rs");

    // The witness carries no lifetime, no machine identity and no expiry: it records only the effect and label.
    let s = bg_rs
        .split("pub struct Clearance {")
        .nth(1)
        .expect("Clearance")
        .split("\n}")
        .next()
        .unwrap();
    assert!(s.contains("effect: Effect"), "Clearance shape changed");
    assert!(s.contains("operation: String"), "Clearance shape changed");
    assert!(
        !s.contains("issued_at") && !s.contains("machine") && !s.contains("expires"),
        "Clearance gained state that would make this scenario stale; re-derive it"
    );

    // Only one sink takes it, so only one sink is compiler-protected. The other three ask by convention.
    let takers: Vec<String> = bench::product_sources()
        .into_iter()
        .filter(|(p, t)| !p.ends_with("srr/breakglass.rs") && t.contains("&crate::srr::breakglass::Clearance"))
        .map(|(p, _)| p)
        .collect();
    assert_eq!(
        takers.len(),
        1,
        "expected exactly one compiler-protected sink; found {takers:?}"
    );
    assert!(takers[0].ends_with("orchestration/gates.rs"));

    // And even there the guarantee is scoped to the module: `build` is private, so it binds new functions inside
    // `gates.rs` and nothing outside it. hx_a::a5 measures the outside.
    let gates_rs = bench::src("runtime/src/orchestration/gates.rs");
    assert!(gates_rs.contains("\nfn build(\n"), "`gates::build` is no longer module-private");
}

// -------------------------------------------------------------------- d5-d12: the R1 preservation set

/// d5 — the four-operation §5 allow-list and its exact-match semantics.
#[test]
fn d5_the_allow_list_is_four_entries_and_matches_exactly() {
    assert_eq!(bg::PERMITTED_OPERATIONS.len(), 4);
    assert_eq!(bg::REFUSAL_POLICY, "allow_list_default_refuse");
    let labels: Vec<&str> = bg::PERMITTED_OPERATIONS.iter().map(|(l, _)| *l).collect();
    assert_eq!(
        labels,
        vec!["checkpoint", "kernel reinstall", "update --apply", "update --rollback"]
    );
    // every entry maps to a real §5 activity
    for (_, act) in bg::PERMITTED_OPERATIONS {
        assert!(bg::PERMITTED_ACTIVITIES.contains(act), "'{act}' is not a §5 activity");
    }

    // exact match: near-miss forms of every entry are refused.
    for (label, _) in bg::PERMITTED_OPERATIONS {
        for near in [
            format!(" {label}"),
            format!("{label} "),
            format!("{label}x"),
            format!("x{label}"),
            format!("{}", label.to_uppercase()),
            format!("{label}\n"),
            format!("{label}\t"),
            format!("{label}--"),
            label.replace(' ', ""),
            label.replace(' ', "  "),
            label.replace("--", "-"),
            format!("{label}/../{label}"),
        ] {
            if near == *label {
                continue;
            }
            assert!(
                bg::permitted_activity(&near).is_none(),
                "near-miss form '{near}' of '{label}' was admitted by the allow-list"
            );
        }
    }
    // and the empty label, which a defaulted argument would produce
    assert!(bg::permitted_activity("").is_none());
}

/// d6 — five `admit` sites paired with five `install_kernel` sites, and no path-taking installer.
#[test]
fn d6_five_admit_sites_and_five_install_kernel_sites() {
    let mut admits: Vec<String> = vec![];
    let mut installs: Vec<String> = vec![];
    for (path, text) in bench::product_sources() {
        for (n, line) in text.lines().enumerate() {
            let code = line.split("//").next().unwrap_or("");
            if code.contains("srr::admit(") {
                admits.push(format!("{path}:{}", n + 1));
            }
            if (code.contains("install_kernel(&") || code.contains("install_kernel(a,"))
                && !code.contains("fn install_kernel")
            {
                installs.push(format!("{path}:{}", n + 1));
            }
        }
    }
    assert_eq!(admits.len(), 5, "admit call sites: {admits:?}");
    assert_eq!(installs.len(), 5, "install_kernel call sites: {installs:?}");
    let kernel = bench::src("runtime/src/kernel.rs");
    assert!(kernel.contains("pub fn install_kernel(\n    auth: &crate::srr::AuthenticatedRelease,"));
    assert!(!kernel.contains("pub fn install_kernel_from_path"));
}

/// d7 — `gov` verifies and never signs (`SRR-R0-L4` vacuous).
#[test]
fn d7_no_signing_capability_in_product_source() {
    let mut hits: Vec<String> = vec![];
    for (path, text) in bench::product_sources() {
        for (n, line) in text.lines().enumerate() {
            let code = line.split("//").next().unwrap_or("");
            for needle in ["SigningKey", "ed25519_dalek::Signer", "PRIVATE KEY", "from_keypair_bytes"] {
                if !code.contains(needle) {
                    continue;
                }
                if needle == "PRIVATE KEY" && path.ends_with("security/secrets.rs") && code.contains("-----BEGIN") {
                    continue;
                }
                hits.push(format!("{path}:{} {}", n + 1, code.trim()));
            }
        }
    }
    assert!(hits.is_empty(), "product source can sign: {hits:?}");
}

/// d8 — D-0007 remains a separate control establishing *intact*, never *authentic* or *admissible*.
#[test]
fn d8_d0007_stays_independent_of_the_srr_verdicts() {
    let kt = bench::src("runtime/src/kernel_trust.rs");
    for forbidden in ["srr::admit", "AuthenticatedRelease", "Authenticity", "breakglass", "below_floor", "Floors"] {
        assert!(!kt.contains(forbidden), "`kernel_trust` reads `{forbidden}`");
    }
    let verifier = bench::src("runtime/src/srr/verifier.rs");
    let admit_body = verifier.split("fn admit_inner").nth(1).expect("admit_inner");
    assert!(!admit_body.contains("kernel_trust"));
}

/// d9 — Contract v3 canonical import byte-identical and failing closed.
#[test]
fn d9_contract_v3_canonical_import_is_byte_identical_and_fails_closed() {
    use sha2::{Digest, Sha256};
    let owner = std::fs::read(bench::wt().join("Governance_OS_Capability_Acceptance_Contract_v3.md")).unwrap();
    let imported = std::fs::read(
        bench::wt().join("framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md"),
    )
    .unwrap();
    assert_eq!(owner, imported, "the canonical import is not byte-identical");
    let d = hex::encode(Sha256::digest(&owner));
    assert_eq!(d, "4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3");
    let contracts = bench::src("runtime/src/contracts.rs");
    assert!(contracts.contains(&d), "the digest is not pinned in contracts.rs");
    assert!(contracts.contains("CONTRACT_SOURCE_DIVERGED"), "the divergence refusal is gone");
}

/// d10 — the `SRR2-R1-C1` exit policy point is owner-closed: verify it is unchanged and still a single
/// comparison. **Not graded.**
#[test]
fn d10_the_exit_policy_point_is_single_and_unchanged() {
    assert_eq!(bg::EXIT_POLICY, "b_stricter_both_floors");
    let bg_rs = bench::src("runtime/src/srr/breakglass.rs");
    let exit = bench::fn_body(&bg_rs, "exit_satisfied");
    assert!(exit.contains("effective_floor_sequence()") && exit.contains("effective_floor_version()"));
    let sites: usize = bench::product_sources()
        .iter()
        .map(|(_, t)| t.matches("effective_floor_sequence()").count())
        .sum();
    assert!(sites <= 4, "the exit-floor comparison has spread beyond `exit_satisfied` and its reporting");
}

/// d11 — floors are monotonic and advance only from an authenticated observation.
#[test]
fn d11_floors_are_monotonic_and_advance_only_from_verified_facts() {
    let mut f = gov_runtime::srr::state::Floors {
        product: PRODUCT.into(),
        ..Default::default()
    };
    f.raise_release("4.1.5", 15, true);
    f.raise_minimum_secure("4.1.2", 12, "src");
    f.raise_metadata("release", 7);
    f.raise_release("4.0.0", 1, true);
    f.raise_minimum_secure("4.0.0", 1, "src");
    f.raise_metadata("release", 1);
    assert_eq!(f.release_high_water_sequence, 15);
    assert_eq!(f.minimum_secure_sequence, 12);
    assert_eq!(f.metadata_floor("release"), 7);
    let before = f.release_high_water_sequence;
    f.raise_release("9.9.9", 999, false);
    assert_eq!(f.release_high_water_sequence, before, "an unverified install raised a floor");
}

/// d12 — `SRR-R0-L7`: break-glass reads only local files, so recovery works with no network.
#[test]
fn d12_break_glass_is_purely_local() {
    let bg_rs = bench::src("runtime/src/srr/breakglass.rs");
    for needle in ["reqwest", "http://", "https://", "TcpStream", "ureq", "curl"] {
        assert!(
            !bg_rs.contains(needle),
            "the break-glass module reaches the network via `{needle}`"
        );
    }
    // and the refused-authority env list is unchanged, so no variable can supply break-glass authority.
    assert_eq!(gov_runtime::srr::state::REFUSED_AUTHORITY_ENV.len(), 9);
    assert!(gov_runtime::srr::state::REFUSED_AUTHORITY_ENV.contains(&"GOV_BREAK_GLASS"));
    // NOTE: `GOV_MACHINE_STATE_DIR` is deliberately NOT in this list — see hx_b.
    assert!(
        !gov_runtime::srr::state::REFUSED_AUTHORITY_ENV.contains(&"GOV_MACHINE_STATE_DIR"),
        "GOV_MACHINE_STATE_DIR joined the refused list; re-derive hx_b"
    );
}
