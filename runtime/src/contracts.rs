//! Governance Capability Acceptance Contract v3 — hash-bound source, compiled form and evidence map.
//!
//! The contract itself says how this must work (repo-root contract, "Contract authority model"):
//!
//! * `framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md` is the **human-approved
//!   normative source**, and the agent "must **not** invent or rewrite its semantics from memory";
//! * `framework/contracts/governance-capability-acceptance.yaml` is the **machine-executable compiled form**;
//! * the runtime consumes the YAML, "but it is valid only when `contract-source.lock` proves that it was
//!   compiled/validated from the exact approved source hash";
//! * "Any semantic difference between source and compiled representation is a hard failure."
//!
//! ## Provenance of the canonical import (logged precedence conflict)
//!
//! `GATE-OWNER-CAC-UPLOAD` was written expecting the owner to copy the approved file into
//! `framework/contracts/source/` once builder scaffolding existed. The owner instead supplied the normative source
//! at the repository root (`Governance_OS_Capability_Acceptance_Contract_v3.md`) and directed that that exact file
//! be used and hash-bound. An active owner directive outranks a frozen gate convention, so:
//!
//! * the **repository-root file is the authoritative owner source**;
//! * `framework/contracts/source/…` is a **builder-produced canonical import**, required to be byte-identical to it;
//! * divergence between the two is a hard failure, not a warning — see [`verify`].
//!
//! Nothing here paraphrases, summarises or "improves" the contract text. The compiler below is purely mechanical:
//! it reads capability headings out of the approved bytes and emits identifiers. It invents no semantics, and it
//! is re-run on every [`verify`] so a hand-edited YAML cannot drift from the source.
use crate::util::{read_text, sha256_text};
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::path::Path;

/// The owner-approved normative source at the repository root.
pub const OWNER_SOURCE: &str = "Governance_OS_Capability_Acceptance_Contract_v3.md";
/// The canonical import inside the kernel payload; must be byte-identical to [`OWNER_SOURCE`].
pub const CANONICAL_IMPORT: &str =
    "framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md";
pub const COMPILED: &str = "framework/contracts/governance-capability-acceptance.yaml";
pub const SOURCE_LOCK: &str = "framework/contracts/contract-source.lock";
pub const SCHEMA: &str = "framework/schemas/governance-capability-acceptance.schema.json";
pub const EVIDENCE_MAP: &str = "tests/governance/capability-evidence-map.yaml";
pub const GENERATED_VIEW: &str = "docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md";

/// The digest the product owner supplied for the approved source, recorded in `GATE-OWNER-CAC-UPLOAD` and in the
/// AR-0026 handoff. Pinning it here means a substituted "approved source" is refused even if every file in the
/// repository were replaced consistently.
pub const OWNER_SOURCE_SHA256: &str =
    "4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3";

const CONTRACT_VERSION: &str = "v3";

/// One capability item, read mechanically out of the approved source.
#[derive(Debug, Clone)]
pub struct Capability {
    pub id: String,
    pub title: String,
    pub requirement_class: String,
    pub source_line: usize,
}

fn classify(heading: &str) -> String {
    // The source marks hardening items inline; everything else is an original requirement of the governing
    // documents. These are the source's own words, not a judgement made here.
    if heading.contains("[POST-VERIFICATION HARDENING]") {
        "POST_VERIFICATION_HARDENING".into()
    } else if heading.contains("[EXECUTION REFINEMENT]") {
        "EXECUTION_REFINEMENT".into()
    } else {
        "ORIGINAL".into()
    }
}

/// Extract the capability items. A capability heading is `## <ID>. <title>` where `<ID>` is a letter-group plus a
/// number, exactly as the approved source writes them.
pub fn parse_capabilities(source: &str) -> Vec<Capability> {
    let mut out = vec![];
    for (i, line) in source.lines().enumerate() {
        let Some(rest) = line.strip_prefix("## ") else {
            continue;
        };
        let Some((id, title)) = rest.split_once(". ") else {
            continue;
        };
        let id = id.trim();
        let ok = !id.is_empty()
            && id
                .chars()
                .next()
                .map(|c| c.is_ascii_uppercase())
                .unwrap_or(false)
            && id.chars().any(|c| c.is_ascii_digit())
            && id.chars().all(|c| c.is_ascii_alphanumeric());
        if !ok {
            continue;
        }
        let title_clean = title
            .replace("**[POST-VERIFICATION HARDENING]**", "")
            .replace("**[EXECUTION REFINEMENT]**", "")
            .trim()
            .to_string();
        out.push(Capability {
            id: id.to_string(),
            title: title_clean,
            requirement_class: classify(rest),
            source_line: i + 1,
        });
    }
    out
}

/// Compile the executable representation. Deterministic and byte-stable for a given source.
pub fn compile(source: &str) -> Value {
    let caps = parse_capabilities(source);
    let items: Vec<Value> = caps
        .iter()
        .map(|c| {
            json!({
                "id": c.id,
                "title": c.title,
                "requirement_class": c.requirement_class,
                "source_reference": format!("{CANONICAL_IMPORT}:{}", c.source_line),
                "family": c.id.chars().take_while(|x| x.is_ascii_alphabetic()).collect::<String>(),
                "status": "DECLARED",
            })
        })
        .collect();
    json!({
        "schema": "governance-os.capability-acceptance-contract",
        "schema_version": 1,
        "contract_version": CONTRACT_VERSION,
        "compiled_from": {
            "owner_source": OWNER_SOURCE,
            "canonical_import": CANONICAL_IMPORT,
            "source_sha256": sha256_text(source),
        },
        "compiler": {
            "note": "Mechanically derived from the approved source headings. No contract semantics are authored here; the normative text is the source, and this file is valid only while contract-source.lock proves it was compiled from that exact source hash.",
        },
        "capability_count": items.len(),
        "capabilities": items,
    })
}

/// The source-lock: binds the compiled representation to the exact approved source hash.
pub fn source_lock(source: &str, compiled: &Value) -> Value {
    json!({
        "schema": "governance-os.contract-source-lock",
        "schema_version": 1,
        "contract_version": CONTRACT_VERSION,
        "owner_source": OWNER_SOURCE,
        "owner_source_sha256": OWNER_SOURCE_SHA256,
        "canonical_import": CANONICAL_IMPORT,
        "canonical_import_sha256": sha256_text(source),
        "compiled": COMPILED,
        "compiled_sha256": crate::util::hash_value(compiled),
        "binding": "The compiled representation is valid only while canonical_import_sha256 equals owner_source_sha256 AND the compiled file matches a fresh compilation of that source. Any difference is a hard failure (Contract v3, 'Contract authority model').",
        "gate": "GATE-OWNER-CAC-UPLOAD",
        "logged_precedence_conflict": "The owner supplied the normative source at the repository root rather than at the destination path; an active owner directive outranks the frozen gate convention, so the root file is authoritative and the destination copy is a hash-bound canonical import.",
    })
}

/// Verify the whole chain, failing closed on any divergence.
///
/// Checks, in order:
/// 1. the canonical import exists and matches the owner-supplied digest pinned in [`OWNER_SOURCE_SHA256`];
/// 2. when the owner source is present in this tree, the import is **byte-identical** to it;
/// 3. the source lock records that same digest;
/// 4. the compiled YAML equals a fresh compilation of the verified source.
pub fn verify(repo_root: &Path) -> Result<Value> {
    let import_path = repo_root.join(CANONICAL_IMPORT);
    let import = read_text(&import_path).map_err(|e| {
        GovError::new(
            "CONTRACT_SOURCE_MISSING",
            format!("the canonical Capability Acceptance Contract import is missing at {CANONICAL_IMPORT}: {}", e.message),
        )
    })?;
    let import_sha = sha256_text(&import);
    if import_sha != OWNER_SOURCE_SHA256 {
        return Err(GovError::new(
            "CONTRACT_SOURCE_DIVERGED",
            format!("{CANONICAL_IMPORT} has digest {import_sha}, the owner-approved source digest is {OWNER_SOURCE_SHA256}. The contract text may not be paraphrased, summarised or edited; restore the owner's exact bytes."),
        )
        .with_details(json!({"path": CANONICAL_IMPORT, "found_sha256": import_sha, "expected_sha256": OWNER_SOURCE_SHA256})));
    }
    let owner_path = repo_root.join(OWNER_SOURCE);
    let owner_present = owner_path.exists();
    if owner_present {
        let owner = read_text(&owner_path)?;
        if owner.as_bytes() != import.as_bytes() {
            return Err(GovError::new(
                "CONTRACT_SOURCE_DIVERGED",
                format!(
                    "{CANONICAL_IMPORT} is not byte-identical to the owner source {OWNER_SOURCE}"
                ),
            ));
        }
    }
    let lock: Value = crate::util::read_yaml(&repo_root.join(SOURCE_LOCK)).map_err(|e| {
        GovError::new(
            "CONTRACT_LOCK_MISSING",
            format!("{SOURCE_LOCK} is missing or unreadable: {}", e.message),
        )
    })?;
    if lock["canonical_import_sha256"].as_str() != Some(import_sha.as_str())
        || lock["owner_source_sha256"].as_str() != Some(OWNER_SOURCE_SHA256)
    {
        return Err(GovError::new(
            "CONTRACT_LOCK_DIVERGED",
            format!("{SOURCE_LOCK} does not bind the approved source digest {OWNER_SOURCE_SHA256}"),
        )
        .with_details(lock.clone()));
    }
    let fresh = compile(&import);
    let on_disk: Value = crate::util::read_yaml(&repo_root.join(COMPILED)).map_err(|e| {
        GovError::new(
            "CONTRACT_COMPILED_MISSING",
            format!("{COMPILED} is missing or unreadable: {}", e.message),
        )
    })?;
    if crate::util::hash_value(&on_disk) != crate::util::hash_value(&fresh) {
        return Err(GovError::new(
            "CONTRACT_COMPILED_DIVERGED",
            format!("{COMPILED} does not match a fresh compilation of the approved source. Any semantic difference between source and compiled representation is a hard failure (Contract v3, 'Contract authority model')."),
        )
        .with_details(json!({
            "compiled_sha256": crate::util::hash_value(&on_disk),
            "expected_sha256": crate::util::hash_value(&fresh),
            "remedy": "regenerate the compiled representation from the approved source; never hand-edit it",
        })));
    }
    Ok(json!({
        "contract_version": CONTRACT_VERSION,
        "owner_source": OWNER_SOURCE,
        "owner_source_present_in_tree": owner_present,
        "owner_source_sha256": OWNER_SOURCE_SHA256,
        "canonical_import": CANONICAL_IMPORT,
        "canonical_import_byte_identical": true,
        "compiled": COMPILED,
        "capability_count": fresh["capability_count"],
        "source_lock": SOURCE_LOCK,
        "schema": SCHEMA,
        "evidence_map": EVIDENCE_MAP,
        "generated_view": GENERATED_VIEW,
        "verdict": "CONTRACT_SOURCE_BOUND",
    }))
}

/// Regenerate every derived artifact from the approved source. Used by the builder and by `gov contract compile`;
/// it never rewrites the source itself.
pub fn generate(repo_root: &Path) -> Result<Value> {
    let import = read_text(&repo_root.join(CANONICAL_IMPORT))?;
    let import_sha = sha256_text(&import);
    if import_sha != OWNER_SOURCE_SHA256 {
        return Err(GovError::new(
            "CONTRACT_SOURCE_DIVERGED",
            format!("refusing to compile: {CANONICAL_IMPORT} has digest {import_sha}, expected {OWNER_SOURCE_SHA256}"),
        ));
    }
    let compiled = compile(&import);
    crate::util::write_yaml(&repo_root.join(COMPILED), &compiled)?;
    crate::util::write_yaml(
        &repo_root.join(SOURCE_LOCK),
        &source_lock(&import, &compiled),
    )?;
    let caps = parse_capabilities(&import);
    // Evidence map: one row per capability, with the executable families that already evidence it left for the
    // owner/verifier to fill. Nothing is asserted as evidenced here that is not.
    let rows: Vec<Value> = caps
        .iter()
        .map(|c| {
            json!({"capability": c.id, "title": c.title, "requirement_class": c.requirement_class,
                   "automated_checks": [], "evidence_class": "NOT_YET_MAPPED",
                   "independent_verification_obligation": "R1/R2 per the frozen acceptance boundary"})
        })
        .collect();
    crate::util::write_yaml(
        &repo_root.join(EVIDENCE_MAP),
        &json!({"schema": "governance-os.capability-evidence-map", "schema_version": 1,
                "contract_version": CONTRACT_VERSION, "source_sha256": import_sha,
                "note": "capability → test/check/evidence mapping. Rows are DECLARED, never asserted as satisfied; populating them is governed work, not a builder claim.",
                "capabilities": rows}),
    )?;
    let mut view = String::new();
    view.push_str("# Governance Capability Acceptance — generated runtime view\n\n");
    view.push_str(
        "**Derived and non-authoritative.** The normative source is the owner-approved\n",
    );
    view.push_str(&format!("`{OWNER_SOURCE}` (SHA-256 `{OWNER_SOURCE_SHA256}`), imported byte-identically to\n`{CANONICAL_IMPORT}`.\n\n"));
    view.push_str("This file is generated by `gov contract compile`. Do not edit it; edit nothing but the owner source.\n\n");
    view.push_str("| Capability | Title | Requirement class |\n|---|---|---|\n");
    for c in &caps {
        view.push_str(&format!(
            "| `{}` | {} | `{}` |\n",
            c.id, c.title, c.requirement_class
        ));
    }
    view.push_str(&format!("\n{} capabilities.\n", caps.len()));
    crate::util::write_text(&repo_root.join(GENERATED_VIEW), &view)?;
    Ok(
        json!({"compiled": COMPILED, "source_lock": SOURCE_LOCK, "evidence_map": EVIDENCE_MAP,
              "generated_view": GENERATED_VIEW, "capability_count": caps.len(),
              "source_sha256": import_sha}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_compiler_invents_nothing_and_is_deterministic() {
        let src = "# X\n\n## A1. First capability\ntext\n\n## A2. Second **[POST-VERIFICATION HARDENING]**\ntext\n\n## Not a capability\n";
        let caps = parse_capabilities(src);
        assert_eq!(caps.len(), 2);
        assert_eq!(caps[0].id, "A1");
        assert_eq!(caps[0].requirement_class, "ORIGINAL");
        assert_eq!(caps[1].id, "A2");
        assert_eq!(caps[1].requirement_class, "POST_VERIFICATION_HARDENING");
        assert_eq!(caps[1].title, "Second");
        assert_eq!(
            crate::util::hash_value(&compile(src)),
            crate::util::hash_value(&compile(src)),
            "compilation must be deterministic"
        );
    }

    #[test]
    fn a_single_changed_byte_in_the_source_changes_the_binding() {
        let a = compile("## A1. X\n");
        let b = compile("## A1. Y\n");
        assert_ne!(
            a["compiled_from"]["source_sha256"],
            b["compiled_from"]["source_sha256"]
        );
    }
}
