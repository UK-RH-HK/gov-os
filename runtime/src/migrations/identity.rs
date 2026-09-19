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
    /// `GOV_SESSION`/`GOV_ROLE` when set, otherwise the A0 planner session recorded in the adoption baseline.
    ///
    /// Kept for API compatibility only: adoption stages no longer use it. Every stage now resolves its actor from
    /// what the caller declared to the process ([`resolve_actor`]); a stage with no declared session refuses
    /// instead of borrowing the planner's.
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
    /// The actor of a stage whose caller supplies nothing: session and role are exactly what the caller declared to
    /// this process ([`resolve_actor`]).
    pub fn process() -> Actor {
        Actor {
            session: None,
            role: None,
            source: "process declaration".into(),
        }
    }
    /// A caller-supplied session (and role) that [`resolve_actor`] checks against the process declaration: a
    /// session nobody declared (e.g. a fallback id) is recorded as undeclared, never as a declaration.
    pub fn supplied(session: &str, role: Option<&str>) -> Actor {
        Actor {
            session: Some(session.to_string()).filter(|s| !s.trim().is_empty()),
            role: role.map(|r| r.to_string()).filter(|r| !r.trim().is_empty()),
            source: "caller-supplied".into(),
        }
    }
}

// ------------------------------------------------------------------------ declared authorship (BC-P2-34, BC-P2-08)

/// Where the session of an adoption actor was declared. Only a declared session records authorship: independence
/// between adoption roles is established from recorded authorship (declared role and session of the author versus the
/// planner/executor/builder), so an invocation whose session nobody declared cannot author an adoption stage.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SessionSource {
    /// Installed once for the process by the CLI ([`install_declared_session`]).
    Installed,
    /// The global `--session <id>` flag.
    Flag,
    /// The stage's own session flag (`gov adopt review --reviewer-session <id>`).
    StageFlag,
    /// `GOV_SESSION=<id>`.
    Environment,
    /// Nothing declared (a caller-generated fallback id is not a declaration).
    Undeclared,
}

impl SessionSource {
    pub fn as_str(&self) -> &'static str {
        match self {
            SessionSource::Installed => "installed",
            SessionSource::Flag => "flag",
            SessionSource::StageFlag => "stage-flag",
            SessionSource::Environment => "environment",
            SessionSource::Undeclared => "undeclared",
        }
    }
    pub fn is_declared(&self) -> bool {
        *self != SessionSource::Undeclared
    }
}

static DECLARED_SESSION: std::sync::OnceLock<Option<String>> = std::sync::OnceLock::new();

/// Install the session this process declared (the CLI's `--session`, else `GOV_SESSION`), once, exactly like
/// `authority::install_acting_role` does for the role. Optional: without it [`declared_session`] reads the same
/// declaration from the process arguments and environment. A second, different installation is refused.
pub fn install_declared_session(session: Option<String>) -> crate::Result<()> {
    let s = session.filter(|s| !s.trim().is_empty());
    match DECLARED_SESSION.get() {
        Some(existing) if *existing == s => Ok(()),
        Some(existing) => Err(crate::GovError::new(
            "SESSION_CONFLICT",
            format!(
                "the declared session of this process is already {existing:?}; it cannot be re-declared as {s:?}"
            ),
        )),
        None => {
            let _ = DECLARED_SESSION.set(s);
            Ok(())
        }
    }
}

/// The value the caller gave `flag` on this process's command line (`--flag v` or `--flag=v`), as the CLI parser
/// reads it. Empty values are not declarations.
pub fn cli_flag_value(flag: &str) -> Option<String> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    flag_value_in(&args, flag)
}

fn flag_value_in(args: &[String], flag: &str) -> Option<String> {
    let eq = format!("{flag}=");
    let mut i = 0;
    while i < args.len() {
        let a = &args[i];
        if a == "--" {
            break;
        }
        if a == flag {
            return args.get(i + 1).cloned().filter(|v| !v.trim().is_empty());
        }
        if let Some(v) = a.strip_prefix(&eq) {
            return Some(v.to_string()).filter(|v| !v.trim().is_empty());
        }
        i += 1;
    }
    None
}

/// **The session declared to this process** for an adoption stage: the stage's own session flag when it has one
/// (`stage_flag`, e.g. `--reviewer-session`), else the process declaration (installed, then `--session`, then
/// `GOV_SESSION`). Two different declarations in one invocation are refused (`SESSION_CONFLICT`), as two different
/// role declarations are (`ROLE_CONFLICT`).
pub fn declared_session(
    stage_flag: Option<&str>,
) -> crate::Result<Option<(String, SessionSource)>> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    declared_session_in(
        &args,
        std::env::var("GOV_SESSION").ok(),
        DECLARED_SESSION.get(),
        stage_flag,
    )
}

fn declared_session_in(
    args: &[String],
    env_session: Option<String>,
    installed: Option<&Option<String>>,
    stage_flag: Option<&str>,
) -> crate::Result<Option<(String, SessionSource)>> {
    let process = match installed {
        Some(Some(s)) => Some((s.clone(), SessionSource::Installed)),
        Some(None) => None,
        None => flag_value_in(args, "--session")
            .map(|s| (s, SessionSource::Flag))
            .or_else(|| {
                env_session
                    .map(|s| s.trim().to_string())
                    .filter(|s| !s.is_empty())
                    .map(|s| (s, SessionSource::Environment))
            }),
    };
    let stage = stage_flag
        .and_then(|f| flag_value_in(args, f))
        .map(|s| (s, SessionSource::StageFlag));
    match (stage, process) {
        (Some((s, _)), Some((p, psrc))) if s != p => Err(crate::GovError::new(
            "SESSION_CONFLICT",
            format!(
                "two different sessions were declared for one invocation ('{p}' via {} and '{s}' via {}); an adoption stage is authored by one session — declare one",
                psrc.as_str(),
                stage_flag.unwrap_or("the stage flag")
            ),
        )
        .with_details(json!({"process_session": p, "process_source": psrc.as_str(), "stage_session": s, "stage_flag": stage_flag}))),
        (Some(s), _) => Ok(Some(s)),
        (None, p) => Ok(p),
    }
}

/// An adoption actor as the OS establishes it: the declared role the process evaluates authority against, and the
/// declared session — each with where it came from.
#[derive(Debug, Clone)]
pub struct ResolvedActor {
    pub session: Option<String>,
    pub session_source: SessionSource,
    pub role: Option<String>,
    pub role_source: String,
}

impl ResolvedActor {
    pub fn session_declared(&self) -> bool {
        self.session.is_some() && self.session_source.is_declared()
    }
    pub fn role_declared(&self) -> bool {
        self.role.is_some()
    }
    pub fn role_id(&self) -> String {
        self.role
            .clone()
            .unwrap_or_else(|| crate::authority::UNDECLARED_ROLE.to_string())
    }
    pub fn session_id(&self) -> String {
        self.session.clone().unwrap_or_default()
    }
    /// The [`Actor`] form recorded in W1 `producer` blocks.
    pub fn as_actor(&self) -> Actor {
        Actor {
            session: self.session.clone(),
            role: self.role.clone(),
            source: format!(
                "session: {}; role: {}",
                self.session_source.as_str(),
                self.role_source
            ),
        }
    }
    pub fn to_value(&self) -> Value {
        json!({"session": self.session, "session_source": self.session_source.as_str(), "role": self.role_id(), "role_declared": self.role_declared(), "role_source": self.role_source})
    }
}

/// **Resolve who is acting in an adoption stage (BC-P2-08, BC-P2-34).** The role is the process's acting role
/// (`authority::installed_acting_role`, else `GOV_ROLE`) — one role per invocation, the same one authority is
/// evaluated against; a different role supplied by the caller is refused (`ROLE_CONFLICT`). The session is the one
/// declared to the process ([`declared_session`]); a caller-supplied session that nobody declared is recorded as
/// undeclared, and one that contradicts the declaration is refused (`SESSION_CONFLICT`).
pub fn resolve_actor(actor: &Actor, stage_flag: Option<&str>) -> crate::Result<ResolvedActor> {
    let acting = crate::authority::installed_acting_role()
        .cloned()
        .unwrap_or_else(|| crate::authority::resolve_acting_role(None));
    if let Some(r) = actor
        .role
        .as_deref()
        .map(str::trim)
        .filter(|r| !r.is_empty())
    {
        if r != acting.id() {
            return Err(crate::GovError::new(
                "ROLE_CONFLICT",
                format!(
                    "the stage was asked to record role '{r}', but the acting role of this invocation is '{}' ({}); one role per invocation — declare the role you act under",
                    acting.id(),
                    acting.source.as_str()
                ),
            ));
        }
    }
    let declared = declared_session(stage_flag)?;
    let given = actor
        .session
        .as_deref()
        .map(str::trim)
        .filter(|s| !s.is_empty());
    let (session, session_source) = match (declared, given) {
        (Some((d, _)), Some(g)) if d != g => {
            return Err(crate::GovError::new(
                "SESSION_CONFLICT",
                format!("the stage was asked to record session '{g}', but this invocation declared session '{d}'"),
            ))
        }
        (Some((d, src)), _) => (Some(d), src),
        (None, Some(g)) => (Some(g.to_string()), SessionSource::Undeclared),
        (None, None) => (None, SessionSource::Undeclared),
    };
    Ok(ResolvedActor {
        session,
        session_source,
        role: acting.role.clone(),
        role_source: acting.source.as_str().to_string(),
    })
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
    fn a_session_is_declared_only_by_the_caller_and_never_twice() {
        let a = |v: &[&str]| v.iter().map(|s| s.to_string()).collect::<Vec<_>>();
        // flag, then environment
        let r = declared_session_in(
            &a(&["--session", "S-1", "adopt", "map"]),
            Some("S-env".into()),
            None,
            None,
        )
        .unwrap();
        assert_eq!(r, Some(("S-1".to_string(), SessionSource::Flag)));
        let r =
            declared_session_in(&a(&["adopt", "map", "--session=S-2"]), None, None, None).unwrap();
        assert_eq!(r, Some(("S-2".to_string(), SessionSource::Flag)));
        let r =
            declared_session_in(&a(&["adopt", "map"]), Some("S-env".into()), None, None).unwrap();
        assert_eq!(r, Some(("S-env".to_string(), SessionSource::Environment)));
        // nothing declared: a fallback id the caller generated is not a declaration
        assert_eq!(
            declared_session_in(&a(&["adopt", "map"]), Some("  ".into()), None, None).unwrap(),
            None
        );
        // the stage's own flag declares the session when nothing else does ...
        let r = declared_session_in(
            &a(&["adopt", "review", "--reviewer-session", "S-r"]),
            None,
            None,
            Some("--reviewer-session"),
        )
        .unwrap();
        assert_eq!(r, Some(("S-r".to_string(), SessionSource::StageFlag)));
        // ... and must agree with the process declaration when both are given
        let e = declared_session_in(
            &a(&["adopt", "review", "--reviewer-session", "S-other"]),
            Some("S-plan".into()),
            None,
            Some("--reviewer-session"),
        )
        .unwrap_err();
        assert_eq!(e.code, "SESSION_CONFLICT");
        let r = declared_session_in(
            &a(&[
                "--session",
                "S-r",
                "adopt",
                "review",
                "--reviewer-session",
                "S-r",
            ]),
            None,
            None,
            Some("--reviewer-session"),
        )
        .unwrap();
        assert_eq!(r.map(|x| x.0), Some("S-r".to_string()));
        // an installed declaration wins over the arguments
        let inst = Some("S-inst".to_string());
        let r = declared_session_in(&a(&["--session", "S-1"]), None, Some(&inst), None).unwrap();
        assert_eq!(r, Some(("S-inst".to_string(), SessionSource::Installed)));
        // `--` ends option parsing; an empty value is not a declaration
        assert_eq!(
            flag_value_in(&a(&["--", "--session", "S-x"]), "--session"),
            None
        );
        assert_eq!(flag_value_in(&a(&["--session", ""]), "--session"), None);
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
