//! Stable identity for adoption artefacts (BC-P2-21 catalogue/plan side; Contract v3:1069-1080 "stable artefact ID
//! ... artefact type ... producer/provenance ... supersedes/superseded-by lineage", :1080 "Applies to ... migration
//! plans, audit findings ...").
//!
//! Every id minted here is a pure function of what the artefact *is*, never of the order in which a stage happened
//! to meet it, so re-running a stage (or the whole adoption) reproduces the same id for the same subject and a
//! ledger line written by an earlier pass keeps naming the artefact it recorded:
//!
//! * a catalogue / classification artefact is identified by its repository path (`ART-<12 hex>`); an artefact that a
//!   migration moved is a new catalogue subject at its new path and carries `lineage.migrated_from` back to the id
//!   the ledger recorded for it;
//! * an adoption finding is identified by family, message and path (`GF-<10 hex>`), so inserting another finding
//!   ahead of it does not renumber it;
//! * a record extracted from a legacy store is identified by its source and normalised content.
use crate::util::{now_iso, sha256_text};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

/// Catalogue and classification id of the artefact at `path` (repository-relative, `/`-separated).
pub fn artefact_id(path: &str) -> String {
    let h = sha256_text(&format!(
        "governance-os/adoption-artefact\n{}",
        path.trim_start_matches("./")
    ));
    format!("ART-{}", &h[..12])
}

/// Stable id of a finding: the same family, message and path always yield the same id.
pub fn finding_id(finding: &Value) -> String {
    let h = sha256_text(&format!(
        "governance-os/finding\n{}\n{}\n{}",
        finding["family"].as_str().unwrap_or(""),
        finding["message"].as_str().unwrap_or(""),
        finding["path"].as_str().unwrap_or("")
    ));
    format!("GF-{}", &h[..10])
}

/// Assign [`finding_id`] to every finding; identical findings in one list get `-2`, `-3`, ... in list order.
///
/// **Integration point (WS-2, `runtime/src/verification/mod.rs::audit`)**: the governance suite numbers its findings
/// positionally (`GF-{n:04}`), so an unrelated earlier finding renumbers every later one (zeta-r
/// `W1-b1-audit-finding-id-stable`). Replacing that loop's id assignment with a call to this function gives audit
/// findings the same stable identity adoption findings have here.
pub fn assign_finding_ids(findings: &mut [Value]) {
    let mut seen: HashMap<String, usize> = HashMap::new();
    for f in findings.iter_mut() {
        let base = finding_id(f);
        let n = seen.entry(base.clone()).or_insert(0);
        *n += 1;
        f["id"] = json!(if *n == 1 { base } else { format!("{base}-{n}") });
    }
}

/// Normalised text used for extracted-record identity (case, whitespace and punctuation insensitive).
pub fn normalise_text(s: &str) -> String {
    s.to_lowercase()
        .chars()
        .filter(|c| c.is_alphanumeric())
        .collect()
}

/// Id of a record extracted from a legacy memory store (A8): `<prefix>-C<10 hex>` over the source store and the
/// normalised text.
pub fn extracted_record_id(prefix: &str, source: &str, text: &str) -> String {
    let h = sha256_text(&format!(
        "governance-os/legacy-extraction\n{source}\n{}",
        normalise_text(text)
    ));
    format!("{prefix}-C{}", &h[..10])
}

/// Id of a record extracted from a legacy decision/lesson document (A6 EXTRACT): `<prefix>-L<10 hex>` over the
/// source document, the section title and the normalised section text. Independent of processing order, so a
/// batch that re-runs, or runs a subset of documents, reproduces the same ids.
pub fn extracted_doc_record_id(prefix: &str, source: &str, title: &str, text: &str) -> String {
    let h = sha256_text(&format!(
        "governance-os/legacy-document-extraction\n{source}\n{}\n{}",
        normalise_text(title),
        normalise_text(text)
    ));
    format!("{prefix}-L{}", &h[..10])
}

/// Stable id of a knowledge unit listed in a residual-knowledge register.
pub fn knowledge_unit_id(source: &str, text: &str) -> String {
    let h = sha256_text(&format!(
        "governance-os/legacy-knowledge-unit\n{source}\n{}",
        normalise_text(text)
    ));
    format!("KU-{}", &h[..10])
}

/// Content hash of the material fields of a JSON value (key order independent).
pub fn content_hash(v: &Value) -> String {
    crate::util::hash_value(v)
}

/// Who produced an adoption artefact. `session`/`role` are what the stage was invoked with when the caller supplied
/// them; `session_source` says where they came from so a reader can tell a declared caller from a fallback.
#[derive(Debug, Clone, Default)]
pub struct Actor {
    pub session: Option<String>,
    pub role: Option<String>,
    pub source: String,
}

impl Actor {
    /// The actor a stage records when its caller passed none: `GOV_SESSION`/`GOV_ROLE` when set, otherwise the A0
    /// planner session recorded in the adoption baseline (Role A performs A1-A4 by protocol §3).
    ///
    /// **Integration point (round 2, BC-P2-08 adopt call sites):** `cli/src/main.rs` calls `a3_map`/`a4_plan`
    /// without the declared session/role; once WS-3's role resolution lands, those arms call
    /// `adopt::a3_map_by` / `adopt::a4_plan_by` with `Actor { session, role, source: "declared" }`.
    pub fn from_env_or_baseline(baseline: &Value) -> Actor {
        let env = |k: &str| std::env::var(k).ok().filter(|s| !s.is_empty());
        match env("GOV_SESSION") {
            Some(s) => Actor {
                session: Some(s),
                role: env("GOV_ROLE"),
                source: "environment".into(),
            },
            None => Actor {
                session: baseline["planner_session"].as_str().map(|s| s.to_string()),
                role: env("GOV_ROLE"),
                source: "adoption-baseline planner session (A0)".into(),
            },
        }
    }
    pub fn declared(session: &str, role: Option<&str>) -> Actor {
        Actor {
            session: Some(session.to_string()),
            role: role.map(|r| r.to_string()),
            source: "declared".into(),
        }
    }
}

/// W1 producer block for an artefact written by adoption stage `stage` through `command`.
pub fn producer(stage: &str, command: &str, actor: &Actor) -> Value {
    json!({"stage": stage, "command": command, "session": actor.session, "role": actor.role, "session_source": actor.source,
        "runtime": {"framework": crate::FRAMEWORK_NAME, "version": crate::VERSION, "runtime_version": crate::RUNTIME_VERSION}, "at": now_iso()})
}

/// Directory holding every version of a versioned adoption artefact (`<stem>.versions/`).
///
/// Versions are stored as JSON so that superseded plan versions are never loaded as governed records (the current
/// version is the only record carrying the artefact id; history must not read as a duplicate id).
pub fn versions_dir(evidence: &Path, stem: &str) -> PathBuf {
    evidence.join(format!("{stem}.versions"))
}

pub fn version_file(evidence: &Path, stem: &str, version: u64, ext: &str) -> PathBuf {
    versions_dir(evidence, stem).join(format!("v{version:04}.{ext}"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn artefact_ids_depend_only_on_the_path() {
        assert_eq!(artefact_id(".env"), artefact_id(".env"));
        assert_eq!(artefact_id("./a/b.py"), artefact_id("a/b.py"));
        assert_ne!(artefact_id(".env"), artefact_id(".cursorrules"));
        assert!(artefact_id("x").starts_with("ART-") && artefact_id("x").len() == 16);
    }

    #[test]
    fn finding_ids_survive_an_inserted_finding() {
        let a = json!({"family": "f", "message": "m1"});
        let b = json!({"family": "f", "message": "m2"});
        let x = json!({"family": "f", "message": "inserted first"});
        let mut one = vec![a.clone(), b.clone()];
        let mut two = vec![x, a, b];
        assign_finding_ids(&mut one);
        assign_finding_ids(&mut two);
        assert_eq!(one[0]["id"], two[1]["id"]);
        assert_eq!(one[1]["id"], two[2]["id"]);
    }

    #[test]
    fn identical_findings_are_disambiguated() {
        let a = json!({"family": "f", "message": "same"});
        let mut v = vec![a.clone(), a];
        assign_finding_ids(&mut v);
        assert_ne!(v[0]["id"], v[1]["id"]);
        assert!(v[1]["id"].as_str().unwrap().ends_with("-2"));
    }

    #[test]
    fn extracted_ids_ignore_whitespace_and_case() {
        assert_eq!(
            extracted_record_id("D", "s", "We decided X."),
            extracted_record_id("D", "s", "we  decided x")
        );
        assert_ne!(
            extracted_record_id("D", "s", "a b"),
            extracted_record_id("D", "t", "a b")
        );
    }
}
