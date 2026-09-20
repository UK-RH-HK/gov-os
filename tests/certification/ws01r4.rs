//! Repair iteration 1, round 4, WS-1 (P2-AR-0042): BC-P2-02 — every capability of the owner source names evidence
//! owners that exist and run, `gov contract verify` enforces it through the CLI, and the product generates the
//! suite-to-contract matrix from its own map (frozen gate contract AC-10, AC-13).
//!
//! Builder regression evidence (Contract v3 O3), not acceptance evidence.
use crate::common::*;
use serde_json::{json, Value};
use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

/// What the certification harness itself lists (`--list`), optionally only its `#[ignore]`d tests.
fn harness_list(ignored: bool) -> BTreeSet<String> {
    let mut args = vec!["--list", "--format", "terse"];
    if ignored {
        args.push("--ignored");
    }
    let o = std::process::Command::new(std::env::current_exe().unwrap())
        .args(&args)
        .output()
        .unwrap();
    String::from_utf8_lossy(&o.stdout)
        .lines()
        .filter_map(|l| l.strip_suffix(": test").map(String::from))
        .collect()
}

/// The owner resolver of `gov contract verify` reads the certification crate's module tree; the harness's own list is
/// the authority it must agree with, both ways (a renamed or removed test stops resolving; an `#[ignore]`d one is
/// never an owner).
#[test]
fn the_owner_resolver_lists_exactly_the_tests_the_certification_harness_runs() {
    let idx = gov_runtime::contracts::test_index(&canonical_root(), "certification")
        .expect("tests/certification/main.rs");
    let found: BTreeSet<String> = idx.keys().cloned().collect();
    let all = harness_list(false);
    assert!(all.len() > 150, "{}", all.len());
    assert_eq!(
        found, all,
        "resolver vs `cargo test --test certification -- --list`"
    );
    let ignored: BTreeSet<String> = idx
        .iter()
        .filter(|(_, s)| s.ignored)
        .map(|(k, _)| k.clone())
        .collect();
    assert_eq!(ignored, harness_list(true));
    assert_eq!(
        idx["ws01r4::the_owner_resolver_lists_exactly_the_tests_the_certification_harness_runs"]
            .file,
        "tests/certification/ws01r4.rs"
    );
}

/// A scratch canonical tree: the contract chain copied, the owners' sources either linked in read-only from this
/// checkout, or (for `copied_tests`) the certification crate copied so a test in it can be changed.
fn chain_copy(tag: &str, sources: bool, copied_tests: bool) -> PathBuf {
    let c = tmp(tag).join("canonical");
    for d in ["framework", "tests/governance", "docs/generated"] {
        copy_dir(&canonical_root().join(d), &c.join(d));
    }
    std::fs::copy(
        canonical_root().join("Governance_OS_Capability_Acceptance_Contract_v3.md"),
        c.join("Governance_OS_Capability_Acceptance_Contract_v3.md"),
    )
    .unwrap();
    if sources {
        for d in ["runtime", "release"] {
            std::os::unix::fs::symlink(canonical_root().join(d), c.join(d)).unwrap();
        }
        if copied_tests {
            copy_dir(
                &canonical_root().join("tests/certification"),
                &c.join("tests/certification"),
            );
        } else {
            std::os::unix::fs::symlink(
                canonical_root().join("tests/certification"),
                c.join("tests/certification"),
            )
            .unwrap();
        }
    }
    c
}

const MAP: &str = "tests/governance/capability-evidence-map.yaml";

fn row(map: &Value, cap: &str) -> usize {
    map["capabilities"]
        .as_array()
        .unwrap()
        .iter()
        .position(|r| r["capability"] == cap)
        .unwrap()
}

fn owner_at(map: &Value, cap: &str, prefix: &str) -> usize {
    map["capabilities"][row(map, cap)]["automated_checks"]
        .as_array()
        .unwrap()
        .iter()
        .position(|o| o["id"].as_str().unwrap().starts_with(prefix))
        .unwrap_or_else(|| panic!("{cap} has no {prefix} owner"))
}

fn edit_map(root: &Path, f: impl FnOnce(&mut Value)) {
    let mut v = yaml(root, MAP);
    f(&mut v);
    write_yaml(root, MAP, &v);
}

/// BC-P2-02 through the product surface: the committed chain binds with every capability owned, and every mutation
/// class the handoff names fails `gov contract verify` with its own typed error.
#[test]
fn gov_contract_verify_enforces_the_evidence_owners() {
    let g = Gov::new(&canonical_root(), "S-owners");
    let r = g.ok(&["contract", "verify"]);
    assert_eq!(r["verdict"], "CONTRACT_SOURCE_BOUND");
    let s = &r["evidence_owners"];
    assert_eq!(s["capabilities"], 101);
    assert_eq!(s["deferred"], json!([]), "{s}");
    assert_eq!(s["not_in_this_tree"], json!([]));
    assert!(s["owners"].as_u64().unwrap() >= 101);

    type Mutation = Box<dyn Fn(&mut Value)>;
    let cases: Vec<(&str, Mutation, &str)> = vec![
        (
            "a capability with zero owners (Gate U)",
            Box::new(|v: &mut Value| {
                let u = row(v, "U");
                v["capabilities"][u]["automated_checks"] = json!([]);
                v["capabilities"][u]["independent_verification"] = json!([]);
                for it in v["capabilities"][u]["checklist"].as_array_mut().unwrap() {
                    it["automated_checks"] = json!([]);
                }
            }),
            "CONTRACT_EVIDENCE_OWNER_MISSING",
        ),
        (
            "an owner naming a test the harness does not run (renamed away)",
            Box::new(|v: &mut Value| {
                let c = row(v, "L3");
                let t = owner_at(v, "L3", "test:certification:");
                let id = v["capabilities"][c]["automated_checks"][t]["id"]
                    .as_str()
                    .unwrap()
                    .to_string();
                v["capabilities"][c]["automated_checks"][t]["id"] = json!(format!("{id}_renamed"));
            }),
            "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
        ),
        (
            "an owner naming a check at a tier the catalogue does not declare",
            Box::new(|v: &mut Value| {
                let c = row(v, "A3");
                let t = owner_at(v, "A3", "check:");
                v["capabilities"][c]["automated_checks"][t]["tiers"] = json!(["G2"]);
            }),
            "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
        ),
        (
            "an out-of-vocabulary evidence class",
            Box::new(|v: &mut Value| {
                let c = row(v, "K2");
                v["capabilities"][c]["evidence_class"] = json!(["builder says so"]);
            }),
            "CONTRACT_EVIDENCE_MAP_DIVERGED",
        ),
        (
            "an out-of-vocabulary health-scheduler tier",
            Box::new(|v: &mut Value| {
                let c = row(v, "K2");
                v["capabilities"][c]["health_scheduler_tiers"] = json!(["G7"]);
            }),
            "CONTRACT_EVIDENCE_MAP_DIVERGED",
        ),
        (
            "a governed field changed without a recompile",
            Box::new(|v: &mut Value| {
                let c = row(v, "O5");
                v["capabilities"][c]["severity"] = json!("critical");
            }),
            "CONTRACT_EVIDENCE_MAP_NOT_RECOMPILED",
        ),
    ];
    for (name, mutate, want) in cases {
        let c = chain_copy("ws01r4-mut", true, false);
        edit_map(&c, |v| mutate(v));
        let e = Gov::new(&c, "S-mut").err(&["contract", "verify"]);
        assert_eq!(e.error_code(), want, "{name}: {}", e.envelope);
        assert!(e.details()["difference_count"].as_u64().unwrap_or(1) >= 1);
    }

    // an owner test that is #[ignore]d is not an owner: the harness does not run it
    let c = chain_copy("ws01r4-ignored", true, true);
    let map = yaml(&c, MAP);
    let id = map["capabilities"][row(&map, "L3")]["automated_checks"]
        [owner_at(&map, "L3", "test:certification:")]["id"]
        .as_str()
        .unwrap()
        .to_string();
    let path = id.trim_start_matches("test:certification:");
    let (module, func) = path.split_once("::").unwrap();
    let rel = format!("tests/certification/{module}.rs");
    let src = read(&c, &rel);
    let marker = format!("#[test]\nfn {func}(");
    assert!(src.contains(&marker), "{rel} declares {func}");
    write(
        &c,
        &rel,
        &src.replacen(&marker, &format!("#[test]\n#[ignore]\nfn {func}("), 1),
    );
    let e = Gov::new(&c, "S-ign").err(&["contract", "verify"]);
    assert_eq!(
        e.error_code(),
        "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
        "{}",
        e.envelope
    );
    assert!(e.envelope.to_string().contains("ignore"), "{}", e.envelope);
}

/// A release-tooling tree carries the contract chain but no test sources, held-out suites or gate contract: the chain
/// still binds, the owners resolved there only at compile time are disclosed as deferred (never passed silently), and
/// `gov contract compile` refuses to bind owners it cannot resolve.
#[test]
fn a_tree_without_the_owners_sources_discloses_deferred_owners_and_refuses_to_compile() {
    let c = chain_copy("ws01r4-bare", false, false);
    let g = Gov::new(&c, "S-bare");
    let r = g.ok(&["contract", "verify"]);
    assert_eq!(r["verdict"], "CONTRACT_SOURCE_BOUND");
    assert!(!r["evidence_owners"]["deferred"]
        .as_array()
        .unwrap()
        .is_empty());
    assert_eq!(
        r["evidence_owners"]["not_in_this_tree"]
            .as_array()
            .unwrap()
            .len(),
        4
    );
    let e = g.err(&["contract", "compile"]);
    assert_eq!(
        e.error_code(),
        "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
        "{}",
        e.envelope
    );
    assert_eq!(
        read(&c, MAP),
        read(&canonical_root(), MAP),
        "compile wrote nothing"
    );
}

/// AC-10's suite-to-contract matrix is generated by the product from its own map: every capability, its owners with
/// their tiers, and last-run evidence read only from the run outputs supplied.
#[test]
fn the_suite_to_contract_matrix_is_generated_from_the_products_own_map() {
    let out = tmp("ws01r4-matrix");
    let results = out.join("lib.out");
    std::fs::write(
        &results,
        "test contracts::tests::the_committed_binding_chain_verifies ... ok\n",
    )
    .unwrap();
    let g = Gov::new(&canonical_root(), "S-matrix");
    let r = g.ok(&[
        "contract",
        "matrix",
        "--lib-results",
        results.to_str().unwrap(),
        "--out",
        out.to_str().unwrap(),
    ]);
    assert_eq!(r["capabilities"], 101);
    let mx: Value =
        serde_json::from_str(&std::fs::read_to_string(out.join("suite-to-contract.json")).unwrap())
            .unwrap();
    assert_eq!(mx["contract"]["verify_verdict"], "CONTRACT_SOURCE_BOUND");
    let md = std::fs::read_to_string(out.join("suite-to-contract.md")).unwrap();
    for c in mx["capabilities"].as_array().unwrap() {
        let owners = c["owners"].as_array().unwrap();
        assert!(!owners.is_empty(), "{}", c["capability"]);
        assert!(md.contains(&format!("#### {} — ", c["capability"].as_str().unwrap())));
        for o in owners {
            assert!(o["resolved"].get("unresolved").is_none(), "{o}");
        }
    }
    let statuses: Vec<String> = mx["capabilities"]
        .as_array()
        .unwrap()
        .iter()
        .flat_map(|c| c["owners"].as_array().unwrap().clone())
        .map(|o| o["last_run"]["status"].as_str().unwrap_or("").to_string())
        .collect();
    assert!(statuses.iter().any(|s| s == "NOT_IN_SUPPLIED_EVIDENCE"));
    // the contract chain is untouched by generating the matrix
    let r2 = g.ok(&["contract", "verify"]);
    assert_eq!(r2["verdict"], "CONTRACT_SOURCE_BOUND");
}
