//! # Research, experiment and test-data lifecycles (WS-10; BC-P2-46, BC-P2-47, BC-P2-48)
//!
//! Contract v3 Gate J (lines 594-616) and Gate H4 (lines 524-527); framework Part XII §45-46 and §39.
//!
//! | Module | What it governs | Contract |
//! |---|---|---|
//! | [`research`] | a research output becomes governed EVIDENCE only when it records question, reason, method, sources/data, measurements, uncertainty, conclusion and confidence; unfinished research is held reference-only (NARRATIVE); the decisions/tasks it influenced are recorded as OS-maintained backlinks | J1 (596-605), §45 |
//! | [`experiment`] | a state machine DESIGNED → RUNNING → CONCLUDED → PROMOTED (→ ABANDONED) recording hypothesis/question, method/data, OS-recorded runs with inputs bound by hash, reproducibility judged by the OS from a reproduction run, results, interpretation and decision influence; experimental output enters the production tree only through a promotion approved by an owner-signed human answer | J2 (607-614), challenge "irreproducible experiment" (616) |
//! | [`scenario`] | the FEATURE → SCENARIOS → DATA → TEST DATA → SUCCESS/FAILURE → INDEPENDENT TESTS chain traced through the product's own fields with every missing link reported; test-data provenance required and read; test-data authorship recorded by the OS and its independence from the implementer and the end-to-end test author checked | H4 (524-527), §39 |
//!
//! ## What "governed" means here, and which facts are T2
//!
//! A research or experiment record's **standing** ([`Standing`]) is computed from the record store every time it is
//! asked for; nothing trusts a stored verdict. Completeness is a property of the record's content, so a complete
//! hand-written research record is evidence. The facts the OS itself establishes — an experiment's lifecycle state,
//! its runs (who ran, on which input bytes, with which results), the reproducibility verdict, a promotion, and
//! test-data authorship — are written by `gov` operations and sealed with the T2 binding primitive
//! ([`crate::t2`]); a consumer honours them only while the seal verifies. A hand-edited experiment that claims
//! `REPRODUCED` or `PROMOTED`, or a hand-written `authorship` block, is reported and not honoured.
//!
//! ## Where each check runs (evidence owners)
//!
//! * **Schemas** (`framework/schemas/{research,experiment,scenario}.schema.json`, kernel payload): the J1/J2
//!   completeness rules are in the schemas, so every product path that validates a record — CIT execution
//!   (`append_record`, post-execution `schema_validation`) and the governance suite's `schema_invariants` family —
//!   refuses or reports an incomplete record that claims evidence.
//! * **Lifecycle commands** (`gov research|experiment|data|scenario ...`): typed refusals at every transition.
//! * **Suite findings** ([`suite_findings`]): the full check set, for the governance-suite family WS-2 wires
//!   (integration point; `verification/**` is WS-2's).
//! * **Consumer APIs** for the call sites other workstreams own: [`require_citable`] (a decision/gate/task may not
//!   rely on research or an experiment that is not governed evidence), [`record_influence`] (the backlink when one
//!   does), [`indexed_state_class`] (retrieval holds non-governed evidence reference-only),
//!   [`experiment::task_lifecycle_refusal`], [`experiment::promotion_refusal`],
//!   [`scenario::implementation_blockers`], [`scenario::readiness_cells`].
use crate::records::{save_record, state_class_for, Record, RecordStore};
use crate::t2::Binding;
use crate::util::{now_iso, sha256_file, str_list};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

pub mod experiment;
pub mod research;
pub mod scenario;

/// Name of the governance-suite family these checks are written for (the family itself is WS-2's to register).
pub const FAMILY: &str = "research_experiment_data_lifecycle";
/// The `AUTHORITY_POLICY` class every lifecycle write requires: `record_research_evidence` (L1), the class of
/// recording research, experiments and test data, so the L1 roles that author this material — `research-agent`,
/// `data-author` — can (IP-WS10-01; declared at the round-3 integration, IP-R3-WS03-4). The matching
/// `COMMAND_GUARDS` entries are kept equal by a unit test.
pub const RECORD_AUTHORITY: &str = "record_research_evidence";
/// The `AUTHORITY_POLICY` class of an experiment promotion (applying a human-answered gate to a production change).
pub const PROMOTE_AUTHORITY: &str = "approve_cit_human";
/// Record types whose outputs are evidence with a lifecycle here.
pub const EVIDENCE_TYPES: &[&str] = &["research", "experiment"];
/// Lifecycle statuses that are current.
pub const CURRENT_STATUSES: &[&str] = &["ACTIVE", "PROVISIONAL"];
/// State classes under which a record is *presented as* governed evidence or authority.
pub const EVIDENCE_CLAIM_CLASSES: &[&str] = &["EVIDENCE", "AUTHORITATIVE", "DERIVED"];
/// Record types that are not "influenced decisions/tasks" when they cite evidence: other evidence, execution
/// records and history. Everything else that derives from research or an experiment (decisions, gates, CITs,
/// tasks, requirements, architecture, …) was influenced by it.
pub const NOT_INFLUENCED_TYPES: &[&str] = &[
    "research",
    "experiment",
    "report",
    "checkpoint",
    "handoff",
    "audit",
    "lesson",
    "legacy",
    "data",
];
/// Canonical edge types by which a record relies on (derives from, consumes, is governed by) another record.
pub const RELIANCE_EDGE_TYPES: &[&str] = &[
    "DERIVED_FROM",
    "CONSUMES",
    "GOVERNED_BY",
    "USES",
    "VALIDATED_BY",
    "IMPLEMENTS",
    "GENERATED_FROM",
    "LEARNED_FROM",
    "DEPENDS_ON",
];
/// Fields only the OS writes on lifecycle records; a caller supplying them is refused.
pub const OS_OWNED_FIELDS: &[&str] = &[
    "research_state",
    "experiment_state",
    "recorded_by",
    "concluded_by",
    "lifecycle",
    "runs",
    "promotion",
    "authorship",
    crate::t2::SEAL_FIELD,
];

// ------------------------------------------------------------------------------------------------ context

/// A lookup of a decision the OS honours.
pub type DecisionLookup<'a> = Box<dyn Fn(&str) -> Result<Record> + 'a>;
/// A check that a gate still carries an owner-signed, authorising human answer bound to a subject digest.
pub type ApprovalCheck<'a> = Box<dyn Fn(&str, &str) -> Result<()> + 'a>;

/// What the lifecycle checks read besides the record store. Production code builds it with [`Ctx::new`]; unit tests
/// supply their own closures.
pub struct Ctx<'a> {
    pub store: &'a RecordStore,
    /// Effective `AUTHORITY_POLICY` (default state class per record type).
    pub authority: Value,
    /// Repository root for input/location hashing; `None` skips every check that reads repository files.
    pub root: Option<&'a Path>,
    /// T2 binding of a record ([`crate::t2::verify_record`]).
    pub binding: Box<dyn Fn(&Record) -> Binding + 'a>,
    /// Whether a path is in the production tree ([`crate::orchestration::tasks::is_production_path`]).
    pub production: Box<dyn Fn(&str) -> bool + 'a>,
    /// A decision the OS honours ([`crate::orchestration::gates::verified_decision`]).
    pub verified_decision: DecisionLookup<'a>,
    /// Whether gate `.0` still carries an owner-signed, authorising human answer bound to subject digest `.1`
    /// ([`crate::orchestration::gates::human_approval_for`]) — what keeps an experiment promotion honoured.
    pub human_approval: ApprovalCheck<'a>,
    /// `TEST_POLICY.independent_test_author_required_for`: test families whose author — and whose test data's
    /// author — must be independent of the implementer.
    pub independent_families: Vec<String>,
}

impl<'a> Ctx<'a> {
    pub fn new(p: &'a Project, store: &'a RecordStore) -> Self {
        let mut fams = p
            .policies()
            .get_list("TEST_POLICY", "independent_test_author_required_for");
        if fams.is_empty() {
            fams = ["acceptance", "scenario", "system"]
                .iter()
                .map(|s| s.to_string())
                .collect();
        }
        Ctx {
            store,
            authority: authority_policy(p),
            root: Some(p.root.as_path()),
            binding: Box::new(crate::t2::verify_record),
            production: Box::new(move |path: &str| {
                crate::orchestration::tasks::is_production_path(p, path)
            }),
            verified_decision: Box::new(move |id: &str| {
                crate::orchestration::gates::verified_decision(p, id)
            }),
            human_approval: Box::new(move |gate: &str, subject: &str| {
                crate::orchestration::gates::human_approval_for(p, gate, subject).map(|_| ())
            }),
            independent_families: fams,
        }
    }
    pub fn state_class(&self, r: &Record) -> String {
        state_class_for(r, &self.authority)
    }
}

/// The effective `AUTHORITY_POLICY`, falling back to this binary's embedded kernel copy.
pub fn authority_policy(p: &Project) -> Value {
    if let Ok(v) = p.policies().policy("AUTHORITY_POLICY") {
        return v.clone();
    }
    crate::kernel::embedded::files()
        .iter()
        .find(|(r, _)| *r == "policies/AUTHORITY_POLICY.yaml")
        .and_then(|(_, b)| serde_yaml::from_slice(b).ok())
        .unwrap_or_else(|| {
            json!({"default_state_class_by_type": {"research": "EVIDENCE", "experiment": "EVIDENCE"}})
        })
}

pub fn archived(r: &Record) -> bool {
    r.problems.iter().any(|p| p == "archived")
}

/// A current record: not archived and in a current lifecycle status.
pub fn is_current(r: &Record) -> bool {
    !archived(r) && CURRENT_STATUSES.contains(&r.status().as_str())
}

/// A field carries content: a non-blank string, a non-empty list/object, a number or a boolean.
pub fn present(v: Option<&Value>) -> bool {
    match v {
        None | Some(Value::Null) => false,
        Some(Value::String(s)) => !s.trim().is_empty(),
        Some(Value::Array(a)) => !a.is_empty(),
        Some(Value::Object(o)) => !o.is_empty(),
        Some(_) => true,
    }
}

// ------------------------------------------------------------------------------------------------ standing

/// Where a research or experiment record stands as evidence.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Standing {
    /// Complete, concluded, current (and for an experiment: OS-recorded and reproduced on unchanged inputs).
    Governed,
    /// Deliberately held reference-only (NARRATIVE/HISTORICAL, or not concluded yet).
    ReferenceOnly,
    /// Presented as evidence but missing required fields: a violation.
    Incomplete,
    /// An experiment whose reproducibility is not established or is refuted.
    Irreproducible,
    /// Not governed through the lifecycle (no lifecycle state, or lifecycle facts not OS-written).
    Ungoverned,
    /// Superseded, retired, rejected, …
    NotCurrent,
}

impl Standing {
    pub fn as_str(&self) -> &'static str {
        match self {
            Standing::Governed => "GOVERNED_EVIDENCE",
            Standing::ReferenceOnly => "REFERENCE_ONLY",
            Standing::Incomplete => "INCOMPLETE",
            Standing::Irreproducible => "IRREPRODUCIBLE",
            Standing::Ungoverned => "UNGOVERNED",
            Standing::NotCurrent => "NOT_CURRENT",
        }
    }
}

/// The evidence standing of one research/experiment record, with every reason.
#[derive(Debug, Clone)]
pub struct EvidenceStatus {
    pub id: String,
    pub rtype: String,
    pub path: String,
    /// The lifecycle state (declared, or derived from content where the lifecycle allows it).
    pub state: String,
    pub standing: Standing,
    /// The effective state class the record is presented under.
    pub state_class: String,
    pub missing: Vec<String>,
    pub reasons: Vec<String>,
}

impl EvidenceStatus {
    /// May a decision, gate or task rely on it?
    pub fn citable(&self) -> bool {
        self.standing == Standing::Governed
    }
    /// Is it presented as evidence (state class) while not being governed evidence?
    pub fn presented_as_evidence(&self) -> bool {
        EVIDENCE_CLAIM_CLASSES.contains(&self.state_class.as_str())
    }
    pub fn to_value(&self) -> Value {
        json!({"id": self.id, "type": self.rtype, "path": self.path, "state": self.state,
            "standing": self.standing.as_str(), "citable": self.citable(), "state_class": self.state_class,
            "missing": self.missing, "reasons": self.reasons})
    }
}

/// The standing of `r` if it is a research or experiment record.
pub fn evidence_status(ctx: &Ctx, r: &Record) -> Option<EvidenceStatus> {
    match r.rtype().as_str() {
        "research" => Some(research::status(ctx, r)),
        "experiment" => Some(experiment::status(ctx, r)),
        _ => None,
    }
}

/// **Consumer API (BC-P2-47/48): refuse to rely on evidence that is not governed.** For every id in `cited` that
/// names a research or experiment record, the record must be governed evidence; otherwise `EVIDENCE_NOT_CITABLE`
/// naming each one with its standing and reasons. Ids that are not research/experiment records are ignored (the
/// caller resolves its own references). Returns the standings of the evidence it checked.
///
/// Call sites (integration points): gate creation and answer (`derived_from`, `--evidence`), `memory select
/// --research`, task creation (`derived_from`, `required_inputs`), CIT proposal.
pub fn require_citable(p: &Project, store: &RecordStore, cited: &[String]) -> Result<Vec<Value>> {
    let ctx = Ctx::new(p, store);
    require_citable_in(&ctx, cited)
}

pub fn require_citable_in(ctx: &Ctx, cited: &[String]) -> Result<Vec<Value>> {
    let mut checked = vec![];
    let mut refused = vec![];
    for id in cited {
        let Some(r) = ctx.store.get(id) else { continue };
        let Some(st) = evidence_status(ctx, r) else {
            continue;
        };
        if !st.citable() {
            refused.push(st.to_value());
        }
        checked.push(st.to_value());
    }
    if refused.is_empty() {
        return Ok(checked);
    }
    let names: Vec<String> = refused
        .iter()
        .map(|s| {
            format!(
                "{} ({})",
                s["id"].as_str().unwrap_or(""),
                s["standing"].as_str().unwrap_or("")
            )
        })
        .collect();
    Err(GovError::new(
        "EVIDENCE_NOT_CITABLE",
        format!("cannot rely on {}: only governed evidence may be cited by a decision, gate or task (Contract v3 J1/J2; framework §45 'unstructured research notes remain reference only'). Complete the research (`gov research conclude <id>`), or conclude and reproduce the experiment (`gov experiment conclude|reproduce <id>`), then cite it.", names.join(", ")),
    )
    .with_details(json!({"not_citable": refused, "checked": checked})))
}

/// **Retrieval standing (integration point for the indexer, WS-6).** The state class under which a record should be
/// indexed: a research or experiment record presented as evidence that is not governed evidence is held
/// reference-only (`NARRATIVE`), so an unsupported conclusion is never retrieved as current EVIDENCE. Every other
/// record keeps [`state_class_for`].
pub fn indexed_state_class(ctx: &Ctx, r: &Record) -> String {
    let sc = ctx.state_class(r);
    match evidence_status(ctx, r) {
        Some(st) if !st.citable() && EVIDENCE_CLAIM_CLASSES.contains(&sc.as_str()) => {
            "NARRATIVE".into()
        }
        _ => sc,
    }
}

// ------------------------------------------------------------------------------------------------ influence

/// The evidence records (research/experiment ids) `r` relies on: its canonical outgoing reliance edges
/// ([`Record::edges`]) and its `evidence_refs`; for a decision derived from a gate, also what that gate relies on.
pub fn cited_evidence(store: &RecordStore, r: &Record) -> Vec<String> {
    let mut out: BTreeSet<String> = BTreeSet::new();
    let visit = |rec: &Record, out: &mut BTreeSet<String>| {
        let me = rec.id();
        for (s, t, d) in rec.edges() {
            if s == me && RELIANCE_EDGE_TYPES.contains(&t.as_str()) {
                if let Some(x) = store.get(&d) {
                    if EVIDENCE_TYPES.contains(&x.rtype().as_str()) {
                        out.insert(d);
                    }
                }
            }
        }
        for e in rec.list("evidence_refs") {
            if let Some(x) = store.get(&e) {
                if EVIDENCE_TYPES.contains(&x.rtype().as_str()) {
                    out.insert(e);
                }
            }
        }
    };
    visit(r, &mut out);
    if r.rtype() == "decision" {
        for g in r.list("derived_from") {
            if let Some(gate) = store.get(&g).filter(|x| x.rtype() == "human-gate") {
                visit(gate, &mut out);
            }
        }
    }
    out.remove(&r.id());
    out.into_iter().collect()
}

/// The decisions, gates, tasks and other governed records that were influenced by evidence `id` (they rely on it
/// directly, or are decisions derived from a gate that relies on it).
pub fn influenced_by(store: &RecordStore, id: &str) -> Vec<String> {
    let mut out: BTreeSet<String> = BTreeSet::new();
    for r in &store.records {
        if archived(r) || r.id().is_empty() || r.id() == id {
            continue;
        }
        if NOT_INFLUENCED_TYPES.contains(&r.rtype().as_str()) {
            continue;
        }
        if cited_evidence(store, r).iter().any(|c| c == id) {
            out.insert(r.id());
        }
    }
    out.into_iter().collect()
}

/// **Record the influence backlink (J1 "influenced decisions/tasks"; J2 "decision influence").** For each id in
/// `cited` that is a research or experiment record, add `influenced` to its `influences`. A record whose T2 seal
/// verified before the write is re-sealed (the OS wrote the change); an unsealed or broken record is written
/// unsealed — the OS never blesses content it did not write. Returns the ids updated.
///
/// Call it right after persisting a decision, gate, task or CIT that relies on evidence (integration points in
/// `gates::answer`/`create`, `memory::benchmark::select`, `tasks::create`, `cit::propose`); [`sync_influences`]
/// reconciles anything written before those call sites existed.
pub fn record_influence(p: &Project, cited: &[String], influenced: &str) -> Result<Vec<String>> {
    let mut store = RecordStore::load(&p.root);
    let mut updated = vec![];
    for id in cited {
        let Some(r) = store.get_mut(id) else { continue };
        if !EVIDENCE_TYPES.contains(&r.rtype().as_str()) || r.id() == influenced {
            continue;
        }
        let mut infl = r.list("influences");
        if infl.iter().any(|x| x == influenced) {
            continue;
        }
        let was_sealed = crate::t2::verify_record(r).is_verified();
        infl.push(influenced.to_string());
        r.set("influences", json!(infl));
        if was_sealed {
            crate::t2::seal_record(r, "lifecycle record influence")?;
        }
        save_record(&p.root, r)?;
        updated.push(id.clone());
    }
    Ok(updated)
}

/// Reconcile every influence backlink from the record store (`gov research sync`): each research or experiment
/// record gains the ids of the governed records that rely on it and are not yet recorded. Backlinks are never
/// removed (an influence that happened stays recorded when the decision is later superseded).
pub fn sync_influences(p: &Project) -> Result<Value> {
    crate::orchestration::control::guard_write(p, "research sync")?;
    crate::authority::require(p, RECORD_AUTHORITY)?;
    let store = RecordStore::load(&p.root);
    let mut plan: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for r in &store.records {
        if archived(r) || !EVIDENCE_TYPES.contains(&r.rtype().as_str()) {
            continue;
        }
        let have = r.list("influences");
        let missing: Vec<String> = influenced_by(&store, &r.id())
            .into_iter()
            .filter(|x| !have.contains(x))
            .collect();
        if !missing.is_empty() {
            plan.insert(r.id(), missing);
        }
    }
    let mut done = vec![];
    for (id, adds) in &plan {
        for a in adds {
            record_influence(p, std::slice::from_ref(id), a)?;
        }
        done.push(json!({"id": id, "added": adds}));
    }
    Ok(json!({"updated": done, "count": done.len()}))
}

// ------------------------------------------------------------------------------------------------ authorship

/// Who authored a governed record, and how the product knows.
#[derive(Debug, Clone)]
pub struct Authorship {
    pub role: Option<String>,
    pub session: Option<String>,
    /// `os-recorded` (a T2-sealed `authorship` stamp written by a gov operation), `task-close` (the OS-observed
    /// output of a closed task: the report's role and session), `declared` (fields the author wrote), `none`.
    pub source: String,
    /// Whether the product itself recorded it (independence can only be *established* from such authorship).
    pub established: bool,
    pub detail: Value,
}

impl Authorship {
    pub fn to_value(&self) -> Value {
        json!({"role": self.role, "session": self.session, "source": self.source, "established": self.established, "detail": self.detail})
    }
}

fn non_empty(s: String) -> Option<String> {
    if s.trim().is_empty() {
        None
    } else {
        Some(s)
    }
}

/// The authorship of `r`, strongest source first: the OS stamp (only while its T2 seal verifies), then the closing
/// report of the task that produced the file (OS-observed paths only), then declared fields.
pub fn authorship_of(ctx: &Ctx, r: &Record) -> Authorship {
    if let Some(a) = r.data.get("authorship").filter(|v| v.is_object()) {
        let b = (ctx.binding)(r);
        let role = a["role"].as_str().map(String::from);
        let session = a["session"].as_str().map(String::from);
        if b.is_verified() {
            return Authorship {
                role,
                session,
                source: "os-recorded".into(),
                established: true,
                detail: json!({"stamp": a, "t2": b.to_value()}),
            };
        }
        return Authorship {
            role,
            session,
            source: "declared".into(),
            established: false,
            detail: json!({"note": "an `authorship` block is present but no gov operation on this machine wrote this record as it stands", "t2": b.to_value()}),
        };
    }
    // the OS-observed output of a closed task: the latest report whose observed paths include this record
    let mut reports: Vec<&Record> = ctx
        .store
        .of_type("report")
        .into_iter()
        .filter(|rep| rep.list("observed_files_changed").contains(&r.path))
        .collect();
    reports.sort_by_key(|rep| rep.id());
    if let Some(rep) = reports.last() {
        return Authorship {
            role: non_empty(rep.get("role")),
            session: non_empty(rep.get("session")),
            source: "task-close".into(),
            established: true,
            detail: json!({"report": rep.id(), "task": rep.get("task"), "t2": (ctx.binding)(rep).code(),
                "note": "OS-observed output of the closing session (report records are not T2-sealed until the task-close T2 adoption, WS-5 IP-5)"}),
        };
    }
    let role = non_empty(r.get("author_role")).or_else(|| non_empty(r.get("author")));
    let session = non_empty(r.get("author_session"));
    if role.is_some() || session.is_some() {
        return Authorship {
            role,
            session,
            source: "declared".into(),
            established: false,
            detail: json!({"note": "author fields written by the author; the product did not record this authorship"}),
        };
    }
    Authorship {
        role: None,
        session: None,
        source: "none".into(),
        established: false,
        detail: Value::Null,
    }
}

/// The OS authorship stamp for a record written by `operation` in this invocation.
pub fn stamp(p: &Project, operation: &str) -> Value {
    json!({"role": p.role, "session": p.session_id, "at": now_iso(), "operation": operation})
}

/// Append one lifecycle transition to the record's OS-written history.
pub fn push_history(r: &mut Record, p: &Project, state: &str, operation: &str) {
    let mut h = r
        .data
        .get("lifecycle")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default();
    h.push(json!({"state": state, "at": now_iso(), "role": p.role, "session": p.session_id, "operation": operation}));
    r.set("lifecycle", json!(h));
}

/// Validate against the kernel schema for the record's type (the generic `record` schema for a type without one, as
/// CIT execution does), T2-seal as written by `operation`, persist.
pub fn validate_seal_save(p: &Project, r: &mut Record, operation: &str) -> Result<()> {
    let t = r.rtype();
    let schema = if p.schemas().has(&t) {
        t
    } else {
        "record".to_string()
    };
    if p.schemas().has(&schema) {
        p.schemas()
            .validate(&schema, &r.data, &format!("({})", r.id()))?;
    }
    crate::t2::seal_record(r, operation)?;
    save_record(&p.root, r)
}

/// Refuse caller-supplied OS-owned lifecycle fields (typed, with the list).
pub fn refuse_os_owned(fields: &Value, allowed: &[&str]) -> Result<()> {
    let Some(o) = fields.as_object() else {
        return Err(GovError::new(
            "USAGE",
            "--fields must be a JSON/YAML object",
        ));
    };
    let bad: Vec<&str> = OS_OWNED_FIELDS
        .iter()
        .copied()
        .filter(|k| o.contains_key(*k) && !allowed.contains(k))
        .collect();
    if bad.is_empty() {
        Ok(())
    } else {
        Err(GovError::new("OS_OWNED_FIELD", format!("fields {bad:?} are written only by the OS as lifecycle facts (T2); remove them from --fields")).with_details(json!({"fields": bad})))
    }
}

/// A repository-relative path that stays inside the repository (no absolute paths, no `..`).
pub fn safe_rel_path(s: &str) -> Result<String> {
    let t = s.trim().trim_start_matches("./").replace('\\', "/");
    if t.is_empty() || t.starts_with('/') || t.split('/').any(|seg| seg == "..") {
        return Err(GovError::new(
            "USAGE",
            format!("'{s}' is not a repository-relative path inside the repository"),
        ));
    }
    Ok(t)
}

/// SHA-256 of a repository file, or the deterministic tree hash of a directory; `None` when it does not exist.
pub fn hash_path(root: &Path, rel: &str) -> Option<String> {
    let abs = root.join(rel);
    if abs.is_file() {
        sha256_file(&abs).ok()
    } else if abs.is_dir() {
        crate::util::hash_tree(&abs, &[]).ok().map(|(h, _)| h)
    } else {
        None
    }
}

/// The repository paths a data record's content lives at (`location`, or `provenance.location`).
pub fn location_paths(r: &Record) -> Vec<String> {
    let mut out = vec![];
    for v in [r.data.get("location"), r.data["provenance"].get("location")]
        .into_iter()
        .flatten()
    {
        match v {
            Value::String(s) if !s.trim().is_empty() => out.push(s.clone()),
            Value::Array(a) => out.extend(a.iter().filter_map(|x| x.as_str().map(String::from))),
            _ => {}
        }
    }
    out
}

/// Every id-shaped string in `v` (a string, a list of strings, or free text naming ids).
pub fn ids_in(v: Option<&Value>) -> Vec<String> {
    let mut out = vec![];
    let mut take = |s: &str| {
        for tok in
            s.split(|c: char| !(c.is_ascii_alphanumeric() || c == '-' || c == '.' || c == '_'))
        {
            let tok = tok.trim_end_matches('.');
            if !tok.is_empty() && crate::records::id_regex().is_match(tok) {
                out.push(tok.to_string());
            }
        }
    };
    match v {
        Some(Value::String(s)) => take(s),
        Some(Value::Array(a)) => {
            for x in a {
                if let Some(s) = x.as_str() {
                    take(s);
                } else if let Some(s) = x.get("id").and_then(|y| y.as_str()) {
                    take(s);
                }
            }
        }
        _ => {}
    }
    out.sort();
    out.dedup();
    out
}

// ------------------------------------------------------------------------------------------------ findings

/// One finding in the governance-suite shape, with a stable code and the record it concerns.
pub fn finding(severity: &str, code: &str, record: &Record, message: String) -> Value {
    json!({"severity": severity, "family": FAMILY, "code": code, "record": record.id(), "path": record.path, "message": message})
}

/// **The suite family's check set** (integration point: WS-2 registers the family `research_experiment_data_lifecycle`
/// in `verification::run_family`, `TEST_POLICY.governance_families` and the scheduler catalogue, and maps each entry
/// to its `finding(severity, family, message, path)`). Research (J1), experiments (J2) and the H4 chain.
pub fn suite_findings(p: &Project, store: &RecordStore) -> Vec<Value> {
    let ctx = Ctx::new(p, store);
    findings_in(&ctx)
}

pub fn findings_in(ctx: &Ctx) -> Vec<Value> {
    let mut out = research::findings(ctx);
    out.extend(experiment::findings(ctx));
    out.extend(scenario::findings(ctx));
    out
}

/// The standing of every research and experiment record (for `gov research check` / `gov experiment check`).
pub fn standings(ctx: &Ctx, rtype: &str) -> Vec<Value> {
    ctx.store
        .of_type(rtype)
        .into_iter()
        .filter_map(|r| evidence_status(ctx, r).map(|s| s.to_value()))
        .collect()
}

/// Findings about records that rely on evidence which is not governed (decision taken on an unsupported research
/// conclusion or an irreproducible experiment — Gate J challenges "unsupported research conclusion", "irreproducible
/// experiment", "decision taken before required evidence").
pub fn reliance_findings(ctx: &Ctx, rtype: &str) -> Vec<Value> {
    let mut out = vec![];
    for r in &ctx.store.records {
        if archived(r) || NOT_INFLUENCED_TYPES.contains(&r.rtype().as_str()) {
            continue;
        }
        if !CURRENT_STATUSES.contains(&r.status().as_str()) {
            continue;
        }
        for c in cited_evidence(ctx.store, r) {
            let Some(e) = ctx.store.get(&c).filter(|e| e.rtype() == rtype) else {
                continue;
            };
            let Some(st) = evidence_status(ctx, e) else {
                continue;
            };
            if st.citable() {
                continue;
            }
            let sev = match r.rtype().as_str() {
                "decision" | "human-gate" | "cit" => "high",
                _ => "medium",
            };
            out.push(finding(
                sev,
                "RELIES_ON_UNGOVERNED_EVIDENCE",
                r,
                format!(
                    "{} ({}) relies on {c}, which is not governed evidence ({}: {})",
                    r.id(),
                    r.rtype(),
                    st.standing.as_str(),
                    st.missing
                        .iter()
                        .map(|m| format!("missing {m}"))
                        .chain(st.reasons.iter().cloned())
                        .collect::<Vec<_>>()
                        .join("; ")
                ),
            ));
        }
    }
    out
}

/// Findings about influence backlinks of `rtype` records: an influenced record not recorded, or a recorded
/// influence that names nothing.
pub fn influence_findings(ctx: &Ctx, rtype: &str) -> Vec<Value> {
    let mut out = vec![];
    for r in ctx.store.of_type(rtype) {
        let have = r.list("influences");
        let missing: Vec<String> = influenced_by(ctx.store, &r.id())
            .into_iter()
            .filter(|x| !have.contains(x))
            .collect();
        if !missing.is_empty() {
            out.push(finding("medium", "INFLUENCE_NOT_RECORDED", r, format!(
                "{} influenced {missing:?} (they rely on it) but does not record them in `influences` (Contract v3 J1 'influenced decisions/tasks'); run `gov research sync`",
                r.id()
            )));
        }
        let dangling: Vec<String> = have
            .iter()
            .filter(|x| ctx.store.get(x).is_none())
            .cloned()
            .collect();
        if !dangling.is_empty() {
            out.push(finding(
                "low",
                "INFLUENCE_UNKNOWN",
                r,
                format!(
                    "{} records influences {dangling:?} that are not governed records",
                    r.id()
                ),
            ));
        }
    }
    out
}

/// `str_list` over a record field (convenience re-export for submodules).
pub(crate) fn list(r: &Record, key: &str) -> Vec<String> {
    str_list(&r.data, key)
}

#[cfg(test)]
pub(crate) mod testkit {
    //! Pure fixtures: a record store written to a temporary directory and a [`Ctx`] whose T2 verdicts, production
    //! tree and verified decisions the test chooses.
    use super::*;
    use std::path::PathBuf;

    pub struct Fx {
        pub dir: PathBuf,
    }
    impl Fx {
        pub fn new(tag: &str) -> Self {
            let dir = std::env::temp_dir()
                .join(format!("gov-lifecycle-{tag}-{}", crate::util::short_uuid()));
            std::fs::create_dir_all(&dir).unwrap();
            Fx { dir }
        }
        pub fn put(&self, rel: &str, data: Value) {
            crate::util::write_yaml(&self.dir.join(rel), &data).unwrap();
        }
        pub fn file(&self, rel: &str, text: &str) {
            crate::util::write_text(&self.dir.join(rel), text).unwrap();
        }
        pub fn store(&self) -> RecordStore {
            RecordStore::load(&self.dir)
        }
    }
    impl Drop for Fx {
        fn drop(&mut self) {
            let _ = std::fs::remove_dir_all(&self.dir);
        }
    }

    /// A context in which every record whose `os_binding` is `{"test": "verified"}` verifies, production is
    /// everything under `product/` or `src/`, decisions listed in `verified` are honoured, and every promotion gate
    /// is approved except `HDG-REVOKED`.
    pub fn ctx<'a>(store: &'a RecordStore, root: &'a Path, verified: &'a [&'a str]) -> Ctx<'a> {
        Ctx {
            store,
            authority: json!({"default_state_class_by_type": {"research": "EVIDENCE", "experiment": "EVIDENCE", "data": "AUTHORITATIVE"}}),
            root: Some(root),
            binding: Box::new(|r: &Record| {
                if r.data[crate::t2::SEAL_FIELD]["test"] == "verified" {
                    Binding::Verified {
                        key_id: "t".into(),
                        operation: "test".into(),
                        at: "t".into(),
                    }
                } else if r.data.get(crate::t2::SEAL_FIELD).is_some() {
                    Binding::Broken {
                        reason: "test".into(),
                    }
                } else {
                    Binding::Unsealed
                }
            }),
            production: Box::new(|p: &str| p.starts_with("product/") || p.starts_with("src/")),
            verified_decision: Box::new(move |id: &str| {
                if verified.contains(&id) {
                    Ok(crate::records::new_record(
                        "decision",
                        id,
                        "t",
                        json!({"human_approved": true}),
                    ))
                } else {
                    Err(GovError::new("DECISION_NOT_FOUND", id.to_string()))
                }
            }),
            human_approval: Box::new(|gate: &str, _subject: &str| {
                if gate == "HDG-REVOKED" {
                    Err(GovError::new("GATE_REVOKED", "revoked"))
                } else {
                    Ok(())
                }
            }),
            independent_families: vec!["acceptance".into(), "scenario".into(), "system".into()],
        }
    }
}

#[cfg(test)]
mod tests {
    use super::testkit::*;
    use super::*;

    #[test]
    fn every_lifecycle_command_is_g0_classified_with_the_class_its_runtime_requires() {
        use crate::orchestration::control::{command_guard, Effect};
        let writes = [
            "research record",
            "research update",
            "research conclude",
            "research withdraw",
            "research sync",
            "experiment design",
            "experiment update",
            "experiment run",
            "experiment reproduce",
            "experiment conclude",
            "experiment abandon",
            "data register",
        ];
        for l in writes {
            let g = command_guard(l).unwrap_or_else(|| panic!("{l} not classified"));
            assert_eq!(g.effect, Effect::Write, "{l}");
            assert_eq!(g.authority, Some(RECORD_AUTHORITY), "{l}");
        }
        let p = command_guard("experiment promote").unwrap();
        assert_eq!(
            (p.effect, p.authority),
            (Effect::Write, Some(PROMOTE_AUTHORITY))
        );
        for l in [
            "research show",
            "research check",
            "experiment show",
            "experiment check",
            "data show",
            "scenario trace",
            "scenario check",
        ] {
            let g = command_guard(l).unwrap_or_else(|| panic!("{l} not classified"));
            assert_eq!((g.effect, g.authority), (Effect::Read, Some("read")), "{l}");
        }
    }

    #[test]
    fn ids_are_read_from_lists_objects_and_free_text() {
        assert_eq!(
            ids_in(Some(&json!("TD-0001 (synthetic, generated)"))),
            vec!["TD-0001"]
        );
        assert_eq!(
            ids_in(Some(&json!(["DATA-0001", {"id": "TD-0002"}, "free text"]))),
            vec!["DATA-0001", "TD-0002"]
        );
        assert!(ids_in(Some(&json!("synthetic"))).is_empty());
        assert!(safe_rel_path("../x").is_err() && safe_rel_path("/etc").is_err());
        assert_eq!(safe_rel_path("./a/b").unwrap(), "a/b");
    }

    #[test]
    fn influence_is_derived_through_edges_evidence_refs_and_gates() {
        let fx = Fx::new("infl");
        fx.put(
            "spec/research/RES-0001.yaml",
            json!({"id": "RES-0001", "type": "research", "status": "ACTIVE", "question": "q"}),
        );
        fx.put(
            "spec/research/RES-0002.yaml",
            json!({"id": "RES-0002", "type": "research", "status": "ACTIVE", "question": "q"}),
        );
        fx.put("spec/decisions/HDG-0001.yaml", json!({"id": "HDG-0001", "type": "human-gate", "status": "ACTIVE", "gate_status": "ANSWERED", "question": "q", "derived_from": ["RES-0001"]}));
        fx.put("spec/decisions/D-0001.yaml", json!({"id": "D-0001", "type": "decision", "status": "ACTIVE", "derived_from": ["HDG-0001"], "evidence_refs": ["RES-0002"]}));
        fx.put("spec/tasks/TASK-0001.yaml", json!({"id": "TASK-0001", "type": "task", "status": "ACTIVE", "class": "implementation", "task_status": "READY", "objective": "o", "required_inputs": [{"id": "RES-0002", "reason": "r"}]}));
        fx.put("spec/reports/RPT-0001.yaml", json!({"id": "RPT-0001", "type": "report", "status": "ACTIVE", "derived_from": ["RES-0001"]}));
        let s = fx.store();
        assert_eq!(
            influenced_by(&s, "RES-0001"),
            vec!["D-0001", "HDG-0001"],
            "a decision derived from a gate that relies on the research was influenced by it; a report is not"
        );
        assert_eq!(influenced_by(&s, "RES-0002"), vec!["D-0001", "TASK-0001"]);
        assert_eq!(
            cited_evidence(&s, s.get("D-0001").unwrap()),
            vec!["RES-0001", "RES-0002"]
        );
    }

    #[test]
    fn authorship_prefers_the_os_stamp_then_the_closing_report_then_declarations() {
        let fx = Fx::new("auth");
        fx.put("spec/data/TD-0001.yaml", json!({"id": "TD-0001", "type": "data", "status": "ACTIVE", "authorship": {"role": "data-author", "session": "S-da"}, "os_binding": {"test": "verified"}}));
        fx.put("spec/data/TD-0002.yaml", json!({"id": "TD-0002", "type": "data", "status": "ACTIVE", "authorship": {"role": "data-author", "session": "S-da"}}));
        fx.put("spec/data/TD-0003.yaml", json!({"id": "TD-0003", "type": "data", "status": "ACTIVE", "author_role": "backend-engineer"}));
        fx.put("spec/data/TD-0004.yaml", json!({"id": "TD-0004", "type": "data", "status": "ACTIVE", "author_role": "data-author"}));
        fx.put("spec/reports/RPT-0001.yaml", json!({"id": "RPT-0001", "type": "report", "status": "ACTIVE", "task": "TASK-0009", "role": "backend-engineer", "session": "S-impl", "observed_files_changed": ["spec/data/TD-0004.yaml"]}));
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &[]);
        let a1 = authorship_of(&c, s.get("TD-0001").unwrap());
        assert!(a1.established && a1.source == "os-recorded");
        let a2 = authorship_of(&c, s.get("TD-0002").unwrap());
        assert!(
            !a2.established && a2.source == "declared",
            "a hand-written authorship block is a claim"
        );
        let a3 = authorship_of(&c, s.get("TD-0003").unwrap());
        assert!(!a3.established && a3.role.as_deref() == Some("backend-engineer"));
        let a4 = authorship_of(&c, s.get("TD-0004").unwrap());
        assert!(
            a4.established
                && a4.source == "task-close"
                && a4.role.as_deref() == Some("backend-engineer"),
            "the OS-observed closing session outranks the declared author"
        );
    }
}
