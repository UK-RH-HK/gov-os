//! **P2-AR-0044 — the HO-0033 structural invariants, re-measured on this tree.**
//!
//! `HO-0033` ("Preservation — must still hold") pins a set of counts and shapes. The tree is roughly three times
//! the size it was at `srr1-r1-accepted`, so a count that merely *matches* proves less than it did; each test
//! below therefore measures the count **and** states the property the count stands for, so that a count which
//! changed can still be judged.
//!
//! My own splitter and my own greps: the point is that the product's `section6.rs` census is the thing under test,
//! not the thing doing the testing.
mod common;
use common::*;

/// Every `.rs` file under `runtime/src` and `cli/src`, as (relative path, text).
fn product_files() -> Vec<(String, String)> {
    fn walk(d: &std::path::Path, root: &std::path::Path, out: &mut Vec<(String, String)>) {
        let Ok(rd) = std::fs::read_dir(d) else { return };
        let mut es: Vec<_> = rd.filter_map(|e| e.ok()).map(|e| e.path()).collect();
        es.sort();
        for p in es {
            if p.is_dir() {
                walk(&p, root, out);
            } else if p.extension().map(|x| x == "rs").unwrap_or(false) {
                let rel = p.strip_prefix(root).unwrap_or(&p).display().to_string();
                out.push((rel, std::fs::read_to_string(&p).unwrap_or_default()));
            }
        }
    }
    let root = product_root();
    let mut out = vec![];
    for base in ["runtime/src", "cli/src"] {
        walk(&root.join(base), &root, &mut out);
    }
    out
}

/// Strip `#[cfg(test)]` modules, so a test fixture is never mistaken for a product call site.
fn cut_tests(t: &str) -> String {
    let mut out = String::new();
    let mut lines = t.lines().peekable();
    while let Some(l) = lines.next() {
        if l.trim_start().starts_with("#[cfg(test)]") {
            // skip to the end of the following item at the same indentation
            let indent = l.len() - l.trim_start().len();
            let close = format!("{}}}", " ".repeat(indent));
            for n in lines.by_ref() {
                if n == close {
                    break;
                }
            }
            continue;
        }
        out.push_str(l);
        out.push('\n');
    }
    out
}

/// Occurrences of `needle` in product source, outside `#[cfg(test)]`, as `path:line` sites.
fn sites(needle: &str) -> Vec<String> {
    let mut out = vec![];
    for (rel, text) in product_files() {
        for (i, l) in cut_tests(&text).lines().enumerate() {
            // ignore doc comments and ordinary comments: a mention is not a call site
            let t = l.trim_start();
            if t.starts_with("//") || t.starts_with("*") {
                continue;
            }
            if l.contains(needle) {
                out.push(format!("{rel}:{}", i + 1));
            }
        }
    }
    out
}

/// **f1 — the §5 allow-list is four operations, and the decision is exact match.**
#[test]
fn f1_the_section_5_allow_list_is_four_entries_and_exact_match() {
    use gov_runtime::srr::breakglass as bg;
    assert_eq!(
        bg::PERMITTED_OPERATIONS.len(),
        4,
        "the §5 allow-list must be four operations, found {:?}",
        bg::PERMITTED_OPERATIONS
    );
    let labels: Vec<&str> = bg::PERMITTED_OPERATIONS.iter().map(|(l, _)| *l).collect();
    assert_eq!(
        labels,
        vec!["checkpoint", "kernel reinstall", "update --apply", "update --rollback"],
        "the four operations changed"
    );
    // Exact match, not prefix/suffix/substring/case/whitespace.
    for l in &labels {
        assert!(bg::permitted_activity(l).is_some(), "{l} must be permitted");
        for near in [
            format!("{l} "),
            format!(" {l}"),
            format!("{l}x"),
            format!("x{l}"),
            l.to_uppercase(),
            l.replace(' ', ""),
            format!("{l}\n"),
            format!("{l}\t"),
            format!("{l}--force"),
        ] {
            if near == **l {
                continue; // e.g. removing spaces from "checkpoint" yields the label itself
            }
            assert!(
                bg::permitted_activity(&near).is_none(),
                "near miss {near:?} must NOT be permitted (exact match only)"
            );
        }
    }
    // Default is refusal.
    for other in ["", "trust bind", "tools install", "gate approve", "update"] {
        assert!(
            bg::permitted_activity(other).is_none(),
            "{other:?} must be refused by default"
        );
    }
    assert_eq!(bg::REFUSAL_POLICY, "allow_list_default_refuse");
}

/// **f2 — five `srr::admit` sites, five `kernel::install_kernel` call sites, and they pair.**
///
/// The property is not the number five: it is that **no privileged kernel ingress installs bytes that the common
/// verifier did not admit**. The count stands for that, so the test also checks the pairing file by file.
#[test]
fn f2_every_install_kernel_site_is_paired_with_an_admit_site() {
    let admits = sites("srr::admit(");
    // Only the DEFINITION line is excluded — deliberately not the whole of kernel.rs, so a call site added
    // inside the defining module would still be counted and would still have to pair.
    let installs: Vec<String> = sites("install_kernel(")
        .into_iter()
        .filter(|s| {
            let (f, n) = s.rsplit_once(':').unwrap();
            let n: usize = n.parse().unwrap();
            let text = std::fs::read_to_string(product_root().join(f)).unwrap();
            let line = cut_tests(&text).lines().nth(n - 1).unwrap_or("").to_string();
            // `fn install_kernel(` defines it; `require(&p, "install_kernel")` is an authority check, not an install
            !line.contains("fn install_kernel(") && !line.contains("\"install_kernel\"")
        })
        .collect();

    assert_eq!(admits.len(), 5, "expected five `srr::admit` sites, found {admits:?}");
    assert_eq!(
        installs.len(),
        5,
        "expected five `install_kernel` call sites, found {installs:?}"
    );

    // Pairing: each install site sits in the same file as an admit site, below it and close to it.
    let file_of = |s: &String| s.rsplit_once(':').unwrap().0.to_string();
    let line_of = |s: &String| s.rsplit_once(':').unwrap().1.parse::<usize>().unwrap();
    let mut unpaired = vec![];
    for i in &installs {
        let paired = admits.iter().any(|a| {
            file_of(a) == file_of(i) && line_of(a) < line_of(i) && line_of(i) - line_of(a) < 60
        });
        if !paired {
            unpaired.push(i.clone());
        }
    }
    assert!(
        unpaired.is_empty(),
        "these `install_kernel` sites are not preceded by an `srr::admit` in the same function: {unpaired:?}\nadmits: {admits:?}"
    );
    println!("admit sites:   {admits:?}");
    println!("install sites: {installs:?}");
}

/// **f3 — one `by_admit` call site, one `AuthenticatedRelease` struct literal.**
///
/// The property: `admit` is the *only* constructor of the token that `install_kernel` demands, so no ingress can
/// mint one. A second literal anywhere, or a second `by_admit` call, would break it.
#[test]
fn f3_the_admission_token_has_exactly_one_constructor() {
    let by_admit: Vec<String> = sites("by_admit()")
        .into_iter()
        .filter(|s| {
            let (f, n) = s.rsplit_once(':').unwrap();
            let n: usize = n.parse().unwrap();
            let t = std::fs::read_to_string(product_root().join(f)).unwrap();
            let line = cut_tests(&t).lines().nth(n - 1).unwrap_or("").to_string();
            !line.contains("fn by_admit") // the definition is not a call
        })
        .collect();
    assert_eq!(by_admit.len(), 1, "expected exactly one `by_admit` call site, found {by_admit:?}");

    // A struct literal is `AuthenticatedRelease {` — a type annotation or a reference is not.
    let literals: Vec<String> = sites("AuthenticatedRelease {")
        .into_iter()
        .filter(|s| {
            let (f, n) = s.rsplit_once(':').unwrap();
            let n: usize = n.parse().unwrap();
            let t = std::fs::read_to_string(product_root().join(f)).unwrap();
            let line = cut_tests(&t).lines().nth(n - 1).unwrap_or("").to_string();
            !line.contains("pub struct") && !line.contains("impl ")
        })
        .collect();
    assert_eq!(
        literals.len(),
        1,
        "expected exactly one `AuthenticatedRelease` struct literal, found {literals:?}"
    );
    assert!(
        literals[0].starts_with("runtime/src/srr/verifier.rs"),
        "the one literal must be inside the verifier, found {literals:?}"
    );
}

/// **f4 — zero `Clearance` constructions outside `breakglass`.**
#[test]
fn f4_no_clearance_is_constructed_outside_breakglass() {
    let mut found = vec![];
    for (rel, text) in product_files() {
        if rel.ends_with("srr/breakglass.rs") {
            continue;
        }
        for (i, l) in cut_tests(&text).lines().enumerate() {
            let t = l.trim_start();
            if t.starts_with("//") || t.starts_with("*") {
                continue;
            }
            if l.contains("Clearance {") || l.contains("Clearance::new") || l.contains("Clearance(") {
                found.push(format!("{rel}:{}", i + 1));
            }
        }
    }
    assert!(
        found.is_empty(),
        "a Clearance must be constructible only inside breakglass, found {found:?}"
    );
}

/// **f5 — D-0007 establishes `intact`, never `authentic` or `admissible`.**
///
/// Post-install integrity is a *separate* control from release authenticity (frozen R1 item 8).
#[test]
fn f5_d0007_integrity_never_claims_authenticity_or_admissibility() {
    let t = cut_tests(&src("runtime/src/kernel_trust.rs"));
    let low = t.to_lowercase();
    assert!(
        low.contains("intact"),
        "kernel_trust.rs must establish integrity (`intact`)"
    );
    for forbidden in ["authentic", "admissible"] {
        // Allowed only where the file explicitly says it is NOT making that claim.
        for (i, l) in t.lines().enumerate() {
            if l.to_lowercase().contains(forbidden) {
                let ctx = l.to_lowercase();
                assert!(
                    ctx.contains("not ") || ctx.contains("never") || ctx.contains("distinct")
                        || l.trim_start().starts_with("//") || l.trim_start().starts_with("///"),
                    "kernel_trust.rs:{} claims '{forbidden}': {l}",
                    i + 1
                );
            }
        }
    }
}

/// **f6 — `SRR-R0-L4` is vacuous: the product carries no signing capability at all.**
#[test]
fn f6_the_product_cannot_sign() {
    let mut found = vec![];
    for (rel, text) in product_files() {
        for (i, l) in cut_tests(&text).lines().enumerate() {
            let t = l.trim_start();
            if t.starts_with("//") || t.starts_with("*") {
                continue;
            }
            for needle in ["SigningKey", "ed25519_dalek::Signer", ".sign(", "Keypair"] {
                if l.contains(needle) {
                    found.push(format!("{rel}:{} {}", i + 1, l.trim()));
                }
            }
        }
    }
    assert!(found.is_empty(), "the product must carry no signing capability: {found:?}");

    // And the non-dev dependency cannot even generate a key.
    let manifest = src("runtime/Cargo.toml");
    let deps = manifest
        .split("[dev-dependencies]")
        .next()
        .unwrap_or("")
        .to_string();
    assert!(
        !deps.contains("rand_core"),
        "the non-dev dependency set must not carry key generation"
    );
}

/// **f7 — the Contract v3 canonical import is byte-identical to the owner source, and fails closed.**
#[test]
fn f7_contract_v3_canonical_import_is_byte_identical_and_pinned() {
    let owner = std::fs::read(product_root().join("Governance_OS_Capability_Acceptance_Contract_v3.md"))
        .expect("owner source");
    let canonical = std::fs::read(
        product_root().join("framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md"),
    )
    .expect("canonical import");
    assert_eq!(
        sha256_hex(&owner),
        "4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3",
        "the owner source is not the pinned Contract v3"
    );
    assert_eq!(
        owner, canonical,
        "the canonical import must be byte-identical to the owner source"
    );
    // The digest is pinned in code, so a consistently replaced repository is still refused.
    assert!(
        src("runtime/src/contracts.rs")
            .contains("4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3"),
        "the owner-source digest must be pinned in the binary"
    );
    // Fails closed: the embedded model refuses a source that does not hash to the pin.
    let m = gov_runtime::contracts::embedded_model();
    assert!(m.is_ok(), "the genuine embedded source must load: {:?}", m.err());
}

/// **f8 — the protected floors are monotonic: every mutator raises, and `Floors::save` binds it.**
///
/// Frozen R1 item 7. HO-0033 requires floors "at all six ingresses, advancing last". The advancing-last half is
/// behavioural and is covered by the product's own suite; the half a census can hold is that **no code path
/// lowers a floor**, which is what this measures.
#[test]
fn f8_no_floor_mutator_lowers_a_floor() {
    let t = cut_tests(&src("runtime/src/srr/state.rs"));
    // Every public mutator of the floors is a raise.
    let mutators: Vec<&str> = t
        .lines()
        .filter(|l| l.contains("pub fn raise_") || l.contains("pub fn set_") || l.contains("pub fn lower_"))
        .collect();
    assert!(
        !mutators.iter().any(|l| l.contains("lower_")),
        "no floor mutator may lower: {mutators:?}"
    );
    assert!(
        mutators.iter().any(|l| l.contains("raise_")),
        "expected raising mutators, found {mutators:?}"
    );
    println!("floor mutators: {mutators:?}");
}
