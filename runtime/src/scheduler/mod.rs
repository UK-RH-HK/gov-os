//! Governance Health Scheduler (Contract v3:791-808, Gate O5; frozen AC-5; BC-P2-06).
//!
//! **Tier contract.** Hosts call the scheduler at their trigger events through [`tier_run`] (or [`guard`] for G0);
//! the scheduler decides *which* checks run from the dependency relation between the changed inputs and each check's
//! declared inputs ([`catalogue`]), runs the independent ones **concurrently** on a worker pool, runs the ones that
//! write state in **disposable sandboxes** ([`sandbox`]), serves unchanged ones from a **cache keyed by the digests of
//! exactly the inputs they declare** ([`store`]), records every result with its provenance, and maintains the
//! **hard-blocks** that the G0 guard enforces.
//!
//! | Tier | Duty (Contract v3:793-799) | Host trigger (owner) | Default selection / cache |
//! |---|---|---|---|
//! | G0 | guard every privileged/mutating command | every governed operation (`control::guard_write`, WS-3; task/CIT/update hosts) | [`admit`] / [`guard`]: active hard-blocks within their scope, remedies admitted, targeted re-evaluation |
//! | G1 | changed paths / schema / secrets / index and dependency/lineage invalidation | **every material mutation, however made**: [`observe`] compares the tree with the last observed state before any operation commits a change the repository relies on (close, CIT-E, release, update, migration) and at `gov status`/`continue`/`gov health status`, and runs G1 on what changed | G1 checks the changed inputs impact, cache |
//! | G2 | mutation scope / readiness / tests / references / memory freshness / input consumption | task close (`tasks::close` → `verification::close_gate`, WS-5) | tier checks (all for governance-affecting work), cache |
//! | G3 | claims / decisions / gates / checkpoint freshness / mandatory-input continuity | checkpoint & handoff (WS-4) | tier checks, cache |
//! | G4 | wider staleness/impact propagation after CIT-E / migration / memory / architecture | CIT execute (WS-4), migration (WS-9), and [`observe`] when an architecture, migration or memory-profile input changed however made | tier checks, cache; a governance-suite record is written |
//! | G5 | full suite | adopt (WS-9), update/release (WS-8), `gov audit` | all checks, fresh (hosts) / cache (`gov audit`) |
//! | G6 | qualification (synthetic repos, chaos, soak, hidden tests) | `gov health qualify` (Phase 4 harness), provisioned machines only | all checks, fresh, qualification subject and machine posture recorded |
//!
//! **Availability rule (P2-HO-0031; Contract v3 L4, O5 :807).** A hard-block refuses the operations whose reliance
//! it protects, **scoped** to what the failing check governs ([`catalogue::BlockScope`]); work that remedies a block
//! and independent work outside its scope stay available; a remedy that does not clear its block does not commit; every
//! refusal is typed (`HEALTH_HARD_BLOCK`, `HEALTH_REMEDY_INCOMPLETE`) and names each block, its check, its scope and
//! its subjects. Hosts use one API: [`admit`] a [`Request`] naming the operation and its subjects; when the
//! [`Admission`] is a remedy of a committing operation, call [`confirm_remedy`] after applying the change and before
//! committing (roll back on error). [`guard`] is the same decision for hosts that pass paths and cannot carry an
//! obligation: it refuses a committing operation that would only be admitted as a remedy.
use crate::records::RecordStore;
use crate::util::{glob_match, hash_value, now_iso};
use crate::verification::currency::{self, Snapshot};
use crate::verification::Family;
use crate::{GovError, Project, Result};
use catalogue::{Cache, CheckDef, Extra, Isolation, Repro, Surface};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, VecDeque};
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::Mutex;

pub mod catalogue;
pub mod sandbox;
pub mod store;

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Tier {
    G0,
    G1,
    G2,
    G3,
    G4,
    G5,
    G6,
}

impl Tier {
    pub fn as_str(&self) -> &'static str {
        match self {
            Tier::G0 => "G0",
            Tier::G1 => "G1",
            Tier::G2 => "G2",
            Tier::G3 => "G3",
            Tier::G4 => "G4",
            Tier::G5 => "G5",
            Tier::G6 => "G6",
        }
    }
    pub fn parse(s: &str) -> Result<Tier> {
        Ok(match s.trim().to_ascii_uppercase().as_str() {
            "G0" => Tier::G0,
            "G1" => Tier::G1,
            "G2" => Tier::G2,
            "G3" => Tier::G3,
            "G4" => Tier::G4,
            "G5" => Tier::G5,
            "G6" => Tier::G6,
            other => {
                return Err(GovError::new(
                    "USAGE",
                    format!("unknown health tier '{other}' (expected G0..G6)"),
                ))
            }
        })
    }
    pub fn duty(&self) -> &'static str {
        match self {
            Tier::G0 => "Guard — every privileged/mutating command",
            Tier::G1 => "Mutation — changed paths/schema/secrets/index invalidation",
            Tier::G2 => "Task Close — mutation scope/readiness/tests/references/memory freshness",
            Tier::G3 => "Checkpoint/Handoff — claims/decisions/gates/checkpoint freshness",
            Tier::G4 => "Milestone — CIT-E/migration/memory/architecture changes",
            Tier::G5 => "Full Suite — adopt/update/release/full audit",
            Tier::G6 => "Qualification — synthetic repos/chaos/soak/hidden tests",
        }
    }
    pub fn all() -> [Tier; 7] {
        [
            Tier::G0,
            Tier::G1,
            Tier::G2,
            Tier::G3,
            Tier::G4,
            Tier::G5,
            Tier::G6,
        ]
    }
}

/// What caused a run: the host event, its subject and the paths it changed (all recorded as provenance).
#[derive(Debug, Clone, Default)]
pub struct Trigger {
    pub event: String,
    pub subject: Option<String>,
    pub paths: Vec<String>,
}

impl Trigger {
    pub fn new(event: &str) -> Self {
        Trigger {
            event: event.into(),
            ..Default::default()
        }
    }
    pub fn with_subject(mut self, subject: &str) -> Self {
        self.subject = Some(subject.into());
        self
    }
    pub fn with_paths(mut self, paths: &[String]) -> Self {
        self.paths = paths.to_vec();
        self
    }
    /// Host helpers (the integration points name these).
    pub fn task_close(task: &str, paths: &[String]) -> Self {
        Trigger::new(catalogue::ops::TASK_CLOSE)
            .with_subject(task)
            .with_paths(paths)
    }
    pub fn cit_execute(cit: &str, paths: &[String]) -> Self {
        Trigger::new(catalogue::ops::CIT_EXECUTE)
            .with_subject(cit)
            .with_paths(paths)
    }
    /// A G6 qualification run (synthetic repository, chaos, soak or hidden-test run) identified by `run_id`.
    pub fn qualification(kind: &str, run_id: &str) -> Self {
        Trigger::new(&format!("qualification.{kind}")).with_subject(run_id)
    }
    pub fn to_value(&self) -> Value {
        json!({"event": self.event, "subject": self.subject, "paths": self.paths})
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CacheMode {
    /// Reuse a check's cached result when its key is unchanged.
    Use,
    /// Execute every wanted check; compare with the cached result under an identical key (reproducibility).
    Refresh,
    /// Neither read nor write the cache.
    Off,
}

impl CacheMode {
    pub fn as_str(&self) -> &'static str {
        match self {
            CacheMode::Use => "use",
            CacheMode::Refresh => "refresh",
            CacheMode::Off => "off",
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Selection {
    /// Every suite check (executed when stale, reused when current under [`CacheMode::Use`]).
    All,
    /// The checks of one tier; checks outside it are reused when current and reported not evaluated otherwise.
    Tier(Tier),
    /// Named checks only.
    Explicit(Vec<String>),
}

#[derive(Debug, Clone)]
pub struct RunOptions {
    pub tier: Tier,
    pub trigger: Trigger,
    pub selection: Selection,
    pub cache: CacheMode,
    pub deep: bool,
    /// Which surface asked (`audit`, `health-run`, `tier`, `guard`, `suite`): recorded as provenance.
    pub surface: String,
    /// Persist a governance-suite `audit` record: `Always` (gov audit), `WhenCompleteAndStale` (tier runs: only
    /// when the run re-establishes currency), `Never`.
    pub record: RecordPolicy,
    /// Upper bound on worker threads (default: available parallelism, between 2 and 4).
    pub workers: Option<usize>,
    /// Write the ledger result and state (false only for the compatibility `verification::run`).
    pub ledger: bool,
    /// G6 only: the validated qualification run this health result observes ([`qualification_run`]), recorded with
    /// the result and the governance-suite record.
    pub qualification: Option<Value>,
    /// Execute every check once (no concurrent double run): mutation observation ([`observe`]) re-evaluates impacted
    /// checks cheaply; reproducibility is established by the G4-G6 runs.
    pub single_run: bool,
    /// The input snapshot the run evaluates, when the caller already took it (`None`: taken by the run).
    pub snapshot: Option<Snapshot>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RecordPolicy {
    Always,
    WhenCompleteAndStale,
    Never,
}

impl RunOptions {
    pub fn new(tier: Tier, trigger: Trigger) -> Self {
        let (selection, cache) = match tier {
            Tier::G5 | Tier::G6 => (Selection::All, CacheMode::Refresh),
            Tier::G0 => (Selection::Explicit(vec![]), CacheMode::Use),
            t => (Selection::Tier(t), CacheMode::Use),
        };
        RunOptions {
            tier,
            trigger,
            selection,
            cache,
            deep: false,
            surface: "tier".into(),
            record: RecordPolicy::WhenCompleteAndStale,
            workers: None,
            ledger: true,
            qualification: None,
            single_run: false,
            snapshot: None,
        }
    }
}

/// How a check was evaluated in a run.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Status {
    Executed,
    Reused,
    NotEvaluated,
}

impl Status {
    fn as_str(&self) -> &'static str {
        match self {
            Status::Executed => "executed",
            Status::Reused => "reused",
            Status::NotEvaluated => "not-evaluated",
        }
    }
}

#[derive(Debug, Clone)]
pub struct CheckRun {
    pub id: String,
    pub status: Status,
    pub family: Option<Family>,
    pub key: String,
    pub key_parts: Value,
    pub duration_ms: u128,
    pub threads: Vec<String>,
    pub reproducible: Option<bool>,
    pub cached_from: Option<String>,
    pub isolation: String,
    pub wanted: bool,
}

/// The outcome of a suite run: per-check runs in suite order plus the persisted health result.
pub struct SuiteOutcome {
    pub runs: Vec<CheckRun>,
    pub snapshot: Snapshot,
    pub result: Value,
}

impl SuiteOutcome {
    /// Families evaluated (executed or reused) — the order of the effective TEST_POLICY list.
    pub fn families(&self) -> Vec<Family> {
        self.runs.iter().filter_map(|r| r.family.clone()).collect()
    }
    /// Families the caller asked for (their findings form the selected verdict).
    pub fn wanted_families(&self) -> Vec<Family> {
        self.runs
            .iter()
            .filter(|r| r.wanted)
            .filter_map(|r| r.family.clone())
            .collect()
    }
    pub fn complete(&self) -> bool {
        self.runs.iter().all(|r| r.status != Status::NotEvaluated)
    }
}

/// Canonical hash of a check result (id, ok, findings) — details such as durations are excluded.
pub fn result_hash_of(result: &Value) -> String {
    hash_value(&json!({"id": result["id"], "ok": result["ok"], "findings": result["findings"]}))
}

fn family_to_value(f: &Family) -> Value {
    json!({"id": f.id, "ok": f.ok, "findings": f.findings, "detail": f.detail})
}

fn family_from_value(v: &Value) -> Family {
    Family {
        id: v["id"].as_str().unwrap_or("").to_string(),
        ok: v["ok"].as_bool().unwrap_or(false),
        findings: v["findings"].as_array().cloned().unwrap_or_default(),
        detail: v["detail"].clone(),
    }
}

/// A check the catalogue does not declare (a project-added family name): conservative defaults.
const UNDECLARED: CheckDef = CheckDef {
    id: "undeclared",
    surface: Surface::Family,
    duty: "family named by TEST_POLICY but not declared in the catalogue",
    deps: &["@files"],
    extras: &[],
    isolation: Isolation::InProcess,
    repro: Repro::SelfChecked,
    cache: Cache::Never,
    tiers: &[Tier::G5, Tier::G6],
    blocks: &[],
};

fn def_for(id: &str) -> &'static CheckDef {
    catalogue::get(id).unwrap_or(&UNDECLARED)
}

// ------------------------------------------------------------------------------------------------ key extras

fn sha_of_files(paths: &[std::path::PathBuf]) -> String {
    let mut parts = vec![];
    for p in paths {
        parts.push(json!({"f": p.file_name().map(|n| n.to_string_lossy().to_string()), "sha": std::fs::read(p).map(|b| crate::util::sha256_hex(&b)).ok()}));
    }
    hash_value(&json!(parts))
}

/// Content digest of the derived index: what checks read (artefacts, chunk text, vectors, edges, exclusions, meta),
/// excluding the retrieval log that ordinary queries append to.
pub fn live_index_digest(p: &Project) -> String {
    let path = p.db_path();
    if !path.exists() {
        return "absent".into();
    }
    let conn = match rusqlite::Connection::open_with_flags(
        &path,
        rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY | rusqlite::OpenFlags::SQLITE_OPEN_NO_MUTEX,
    ) {
        Ok(c) => c,
        Err(e) => return format!("unreadable:{e}"),
    };
    let mut h = sha2::Sha256::new();
    use sha2::Digest;
    let queries = [
        "SELECT path, content_hash, status, state_class, record_type, namespace, sensitivity, path_class, superseded_by, default_retrieval FROM artifacts ORDER BY path",
        "SELECT chunk_id, artifact_id, content_hash, text FROM chunks ORDER BY chunk_id",
        "SELECT chunk_id, artifact_id, embedder, dim FROM vectors ORDER BY chunk_id",
        "SELECT src, type, dst, source_artifact FROM edges ORDER BY src, type, dst, source_artifact",
        "SELECT path, reason FROM excluded ORDER BY path",
        "SELECT key, value FROM meta ORDER BY key",
    ];
    for q in queries {
        h.update(q.as_bytes());
        let Ok(mut st) = conn.prepare(q) else {
            h.update(b"<missing>");
            continue;
        };
        let n = st.column_count();
        let rows = st.query_map([], |r| {
            let mut s = String::new();
            for i in 0..n {
                let v: rusqlite::types::Value = r.get(i)?;
                s.push_str(&format!("{v:?}\u{1f}"));
            }
            Ok(s)
        });
        if let Ok(rows) = rows {
            for row in rows.flatten() {
                h.update(row.as_bytes());
                h.update(b"\x1e");
            }
        }
    }
    format!("{:x}", h.finalize())
}

fn product_evidence_digest(p: &Project) -> String {
    match crate::verification::product::latest_records(p) {
        v if v.is_empty() => "none".into(),
        v => hash_value(&json!(v
            .iter()
            .map(|r| json!({"id": r["id"], "families": r["families"], "at": r["run_at"]}))
            .collect::<Vec<_>>())),
    }
}

struct Extras<'a> {
    p: &'a Project,
    deep: bool,
    memo: BTreeMap<String, String>,
}

impl<'a> Extras<'a> {
    fn get(&mut self, e: Extra) -> String {
        let name = format!("{e:?}");
        if let Some(v) = self.memo.get(&name) {
            return v.clone();
        }
        let v = match e {
            Extra::LiveIndex => live_index_digest(self.p),
            // the store actually in use (a linked worktree shares its main worktree's; WS-6 IP-R2-12: wherever its
            // writer keeps it)
            Extra::Claims => {
                let db = crate::memory::claims::ClaimsStore::path_for(self.p);
                let wal = db.with_file_name(format!(
                    "{}-wal",
                    db.file_name()
                        .map(|n| n.to_string_lossy().to_string())
                        .unwrap_or_else(|| "claims.db".into())
                ));
                sha_of_files(&[db, wal])
            }
            Extra::Telemetry => sha_of_files(&[
                crate::observability::path(self.p),
                crate::routing::evidence_path(self.p),
            ]),
            Extra::Qualifications => hash_value(&json!(store::history(self.p, store::RETAIN)
                .into_iter()
                .filter(|h| h["tier"] == "G6")
                .map(|h| h["id"].clone())
                .collect::<Vec<_>>())),
            Extra::ClockHour => chrono::Utc::now().format("%Y-%m-%dT%H").to_string(),
            Extra::ContextPackets => {
                let mut files: Vec<std::path::PathBuf> =
                    std::fs::read_dir(self.p.runtime_dir().join("context"))
                        .map(|rd| {
                            rd.flatten()
                                .map(|e| e.path())
                                .filter(|x| x.extension().map(|e| e == "json").unwrap_or(false))
                                .collect()
                        })
                        .unwrap_or_default();
                files.sort();
                sha_of_files(&files)
            }
            Extra::ProductEvidence => product_evidence_digest(self.p),
            Extra::SkillObservations => sha_of_files(&[crate::skills::observations_path(self.p)]),
            Extra::PluginObservations => {
                sha_of_files(&[self.p.runtime_dir().join("plugins").join("observed.json")])
            }
            Extra::DeepMode => self.deep.to_string(),
            Extra::ContractSource => match crate::verification::reporting::contract_root(self.p) {
                Some(root) => sha_of_files(
                    &crate::verification::reporting::contract_files()
                        .iter()
                        .map(|f| root.join(f))
                        .collect::<Vec<_>>(),
                ),
                None => "not-applicable".into(),
            },
            Extra::GovernanceBaseline => hash_value(&json!(
                crate::verification::lineage::baseline_commits(self.p)
            )),
        };
        self.memo.insert(name, v.clone());
        v
    }
}

/// The cache key of a check: its id plus the digests of exactly the classes and extras it declares.
fn check_key(snap: &Snapshot, def: &CheckDef, id: &str, extras: &mut Extras) -> (String, Value) {
    let deps = catalogue::expand_deps(def);
    let classes: Map<String, Value> = deps
        .iter()
        .map(|d| {
            (
                d.to_string(),
                json!(snap.classes.get(*d).cloned().unwrap_or_default()),
            )
        })
        .collect();
    let ex: Map<String, Value> = def
        .extras
        .iter()
        .map(|e| (format!("{e:?}"), json!(extras.get(*e))))
        .collect();
    let parts = json!({"classes": classes, "extras": ex});
    (hash_value(&json!({"check": id, "parts": parts})), parts)
}

// ------------------------------------------------------------------------------------------------ execution

struct Task {
    idx: usize,
    replica: u8,
}

struct Done {
    idx: usize,
    replica: u8,
    family: Family,
    ms: u128,
    thread: String,
}

#[allow(clippy::too_many_arguments)]
fn execute_one(
    root: &std::path::Path,
    session: &str,
    role: &str,
    store: &RecordStore,
    def: &CheckDef,
    id: &str,
    deep: bool,
    snap: &Snapshot,
) -> Family {
    let live = Project::open(root).with_session(Some(session.into()), Some(role.into()));
    let run = |p: &Project, st: &RecordStore| -> Result<Family> {
        let db = if p.db_path().exists() {
            Some(crate::memory::db::RuntimeDb::open(&p.db_path())?)
        } else {
            None
        };
        crate::verification::run_family(
            &crate::verification::FamilyCtx {
                p,
                db: db.as_ref(),
                store: st,
                deep,
                snapshot: Some(snap),
            },
            id,
        )
    };
    let out = match def.isolation {
        Isolation::Sandbox if !sandbox::inside_sandbox() => {
            match sandbox::Sandbox::create(
                &live,
                id,
                sandbox::SandboxOptions {
                    runtime: true,
                    git: false,
                },
            ) {
                Ok(sb) => {
                    let sp = sb.project(&live);
                    let sstore = RecordStore::load(&sb.root);
                    run(&sp, &sstore).map(|f| {
                        let v = sb.relocate(&family_to_value(&f));
                        let mut f2 = family_from_value(&v);
                        if let Some(o) = f2.detail.as_object_mut() {
                            o.insert("isolated_in_sandbox".into(), json!(true));
                        } else if f2.detail.is_null() {
                            f2.detail = json!({"isolated_in_sandbox": true});
                        }
                        f2
                    })
                }
                Err(e) => Err(e),
            }
        }
        _ => run(&live, store),
    };
    match out {
        Ok(f) => f,
        Err(e) => Family {
            id: id.to_string(),
            ok: false,
            findings: vec![
                json!({"severity": "high", "family": id, "message": format!("check could not execute: [{}] {}", e.code, e.message), "path": Value::Null}),
            ],
            detail: json!({"execution_error": e.code}),
        },
    }
}

fn max_severity(findings: &[Value]) -> &'static str {
    let mut best = "none";
    for f in findings {
        let s = f["severity"].as_str().unwrap_or("low");
        if catalogue::rank(s) > catalogue::rank(best) {
            best = match s {
                "critical" => "critical",
                "high" => "high",
                "medium" => "medium",
                "low" => "low",
                _ => "info",
            };
        }
    }
    best
}

fn verdict_of(findings: &[&Value]) -> &'static str {
    let has = |sev: &str| findings.iter().any(|x| x["severity"].as_str() == Some(sev));
    if has("critical") || has("high") {
        "UNHEALTHY"
    } else if has("medium") {
        "DEGRADED"
    } else {
        "HEALTHY"
    }
}

/// The suite: the effective `TEST_POLICY.governance_families` (projects may add families; POLICY_PRECEDENCE makes
/// the list additive).
pub fn suite_families(p: &Project) -> Vec<String> {
    p.policies().get_list("TEST_POLICY", "governance_families")
}

/// Run the governance suite under the scheduler. The caller receives every check run; the ledger result (with
/// provenance) is persisted and the hard-block state updated unless `opts.ledger` is false.
pub fn run_suite(p: &Project, opts: &RunOptions) -> Result<SuiteOutcome> {
    let _depth = SuiteDepth::enter();
    let started = std::time::Instant::now();
    let started_at = now_iso();
    let run_id = store::new_result_id();
    let snap = match &opts.snapshot {
        Some(s) => s.clone(),
        None => Snapshot::take(p)?,
    };
    let families = suite_families(p);
    let mut extras = Extras {
        p,
        deep: opts.deep,
        memo: BTreeMap::new(),
    };
    let wanted_of = |id: &str| -> bool {
        match &opts.selection {
            Selection::All => true,
            Selection::Tier(t) => def_for(id).tiers.contains(t) || def_for(id).id == "undeclared",
            Selection::Explicit(ids) => ids.iter().any(|x| x == id),
        }
    };
    let mut runs: Vec<CheckRun> = vec![];
    let mut to_execute: Vec<usize> = vec![];
    for id in &families {
        let def = def_for(id);
        let (key, parts) = check_key(&snap, def, id, &mut extras);
        // checks that are never cached (time- or session-dependent, all cheap) run whenever the suite does, so a tier
        // run can still leave a complete result
        let wanted = wanted_of(id)
            || (def.cache == Cache::Never && !matches!(opts.selection, Selection::Explicit(_)));
        let cacheable = def.cache == Cache::Cacheable && opts.cache != CacheMode::Off;
        let cached = if cacheable {
            store::cache_get(p, id, &key)
        } else {
            None
        };
        let virtual_check = id == "audit_reproducibility";
        let status = if virtual_check
            || (wanted && (opts.cache == CacheMode::Refresh || cached.is_none()))
        {
            Status::Executed
        } else if cached.is_some() {
            Status::Reused
        } else {
            Status::NotEvaluated
        };
        let mut r = CheckRun {
            id: id.clone(),
            status,
            family: None,
            key,
            key_parts: parts,
            duration_ms: 0,
            threads: vec![],
            reproducible: None,
            cached_from: None,
            isolation: format!("{:?}", def.isolation),
            wanted,
        };
        if status == Status::Reused {
            let c = cached.unwrap();
            let mut f = family_from_value(&c["result"]);
            if let Some(o) = f.detail.as_object_mut() {
                o.insert("served_from_cache".into(), json!(c["produced_by"]));
            }
            r.family = Some(f);
            r.cached_from = c["produced_by"].as_str().map(|s| s.to_string());
        }
        if status == Status::Executed && !virtual_check {
            to_execute.push(runs.len());
        }
        runs.push(r);
    }
    // ---- worker pool: independent checks concurrently, DoubleRun checks twice
    let mut queue: VecDeque<Task> = VecDeque::new();
    for &i in &to_execute {
        queue.push_back(Task { idx: i, replica: 0 });
        if def_for(&runs[i].id).repro == Repro::DoubleRun && !opts.single_run {
            queue.push_back(Task { idx: i, replica: 1 });
        }
    }
    let n_tasks = queue.len();
    let max_workers = opts.workers.unwrap_or_else(|| {
        std::thread::available_parallelism()
            .map(|n| n.get())
            .unwrap_or(2)
            .clamp(2, 4)
    });
    let workers = max_workers
        .min(n_tasks)
        .max(if n_tasks > 0 { 1 } else { 0 });
    // Resolve kernel trust once, on this thread, before any worker starts. Workers then read the cached verdict, and
    // an untrusted kernel's embedded-baseline substitution is materialised exactly once: `kernel::embedded_kernel_dir`
    // stages into a per-process directory, so concurrent first materialisations from threads of one process would
    // interleave and leave a corrupt cache marked complete (integration point for WS-8, see the repair report).
    let _ = crate::kernel_trust::trust(&p.root);
    let queue = Mutex::new(queue);
    let done: Mutex<Vec<Done>> = Mutex::new(vec![]);
    let store_live = RecordStore::load(&p.root);
    let ids: Vec<String> = runs.iter().map(|r| r.id.clone()).collect();
    let root = p.root.clone();
    let (session, role, deep) = (p.session_id.clone(), p.role.clone(), opts.deep);
    std::thread::scope(|s| {
        for w in 0..workers {
            let (queue, done, store_live, ids, root, session, role, snap) = (
                &queue,
                &done,
                &store_live,
                &ids,
                &root,
                &session,
                &role,
                &snap,
            );
            let _ = std::thread::Builder::new()
                .name(format!("gov-health-{w}"))
                .spawn_scoped(s, move || loop {
                    let task = { queue.lock().ok().and_then(|mut q| q.pop_front()) };
                    let Some(task) = task else { break };
                    let id = &ids[task.idx];
                    let t0 = std::time::Instant::now();
                    let fam =
                        execute_one(root, session, role, store_live, def_for(id), id, deep, snap);
                    let thread = std::thread::current().name().unwrap_or("?").to_string();
                    if let Ok(mut d) = done.lock() {
                        d.push(Done {
                            idx: task.idx,
                            replica: task.replica,
                            family: fam,
                            ms: t0.elapsed().as_millis(),
                            thread,
                        });
                    }
                });
        }
    });
    // a worker that could not be spawned leaves its tasks queued: run them here rather than drop them
    let mut leftover: Vec<Task> = queue
        .into_inner()
        .map(|q| q.into_iter().collect())
        .unwrap_or_default();
    let mut done = done.into_inner().unwrap_or_default();
    for task in leftover.drain(..) {
        let id = &ids[task.idx];
        let t0 = std::time::Instant::now();
        let fam = execute_one(
            &root,
            &session,
            &role,
            &store_live,
            def_for(id),
            id,
            deep,
            &snap,
        );
        done.push(Done {
            idx: task.idx,
            replica: task.replica,
            family: fam,
            ms: t0.elapsed().as_millis(),
            thread: "main".into(),
        });
    }
    done.sort_by_key(|d| (d.idx, d.replica));
    let mut threads_used: Vec<String> = done.iter().map(|d| d.thread.clone()).collect();
    threads_used.sort();
    threads_used.dedup();
    let mut mismatches: Vec<Value> = vec![];
    let mut compared: Vec<Value> = vec![];
    for d in done {
        let r = &mut runs[d.idx];
        r.duration_ms = r.duration_ms.max(d.ms);
        r.threads.push(d.thread.clone());
        if d.replica == 0 {
            r.family = Some(d.family);
        } else if let Some(first) = &r.family {
            let a = result_hash_of(&family_to_value(first));
            let b = result_hash_of(&family_to_value(&d.family));
            r.reproducible = Some(a == b);
            compared.push(json!({"check": r.id, "method": "double-run", "equal": a == b}));
            if a != b {
                mismatches
                    .push(json!({"check": r.id, "method": "double-run", "first": a, "second": b}));
            }
        }
    }
    // reproducibility against a cached result computed under an identical key (Refresh mode)
    for r in runs.iter_mut() {
        if r.status != Status::Executed || r.id == "audit_reproducibility" {
            continue;
        }
        if let (Some(prev), Some(f)) = (store::cache_peek(p, &r.id), &r.family) {
            if prev["key"].as_str() == Some(r.key.as_str()) {
                let a = result_hash_of(&family_to_value(f));
                let equal = prev["result_hash"].as_str() == Some(a.as_str());
                compared.push(json!({"check": r.id, "method": "cached-identical-key", "cached_from": prev["produced_by"], "equal": equal}));
                if !equal {
                    mismatches.push(json!({"check": r.id, "method": "cached-identical-key", "cached_from": prev["produced_by"]}));
                    r.reproducible = Some(false);
                }
            }
        }
    }
    // the virtual reproducibility family
    for r in runs.iter_mut() {
        if r.id != "audit_reproducibility" {
            continue;
        }
        let findings: Vec<Value> = mismatches.iter().map(|m| json!({"severity": "high", "family": "audit_reproducibility", "message": format!("check {} produced a different result on identical inputs ({})", m["check"].as_str().unwrap_or("?"), m["method"].as_str().unwrap_or("?")), "path": Value::Null})).collect();
        r.family = Some(Family {
            id: r.id.clone(),
            ok: findings.is_empty(),
            findings,
            detail: json!({"compared": compared, "mismatches": mismatches.len(), "note": "every executed DoubleRun check runs twice concurrently; every refreshed check is compared with its cached result under an identical key"}),
        });
    }
    // ---- cache writes (executed, cacheable, valid)
    if opts.cache != CacheMode::Off {
        for r in &runs {
            if r.status != Status::Executed || def_for(&r.id).cache != Cache::Cacheable {
                continue;
            }
            if let Some(f) = &r.family {
                let _ =
                    store::cache_put(p, &r.id, &r.key, &r.key_parts, &family_to_value(f), &run_id);
            }
        }
    }
    let result = assemble_result(
        p,
        opts,
        &run_id,
        &started_at,
        started.elapsed().as_millis(),
        &snap,
        &runs,
        &threads_used,
        workers,
    );
    let mut out = SuiteOutcome {
        runs,
        snapshot: snap,
        result,
    };
    if opts.ledger {
        update_state_from_suite(p, &out, &run_id)?;
        out.result["blocks"] = store::load_state(p)["blocks"].clone();
        out.result["state"] = json!(health_state(&store::load_state(p)));
        store::save_result(p, &out.result)?;
        // every G1 duty evaluated against this snapshot: the mutations up to it are observed (see `observe`)
        let g1_done = out
            .runs
            .iter()
            .all(|r| !def_for(&r.id).tiers.contains(&Tier::G1) || r.status != Status::NotEvaluated);
        if g1_done {
            let _ = save_observed(p, &out.snapshot, &run_id);
        }
        let _ = crate::observability::emit(
            p,
            "health.run",
            json!({"id": run_id, "tier": opts.tier.as_str(), "surface": opts.surface, "executed": out.result["summary"]["executed"], "reused": out.result["summary"]["reused"], "workers": workers, "verdict": out.result["verdict"], "duration_ms": out.result["duration_ms"]}),
        );
    }
    Ok(out)
}

#[allow(clippy::too_many_arguments)]
fn assemble_result(
    p: &Project,
    opts: &RunOptions,
    run_id: &str,
    started_at: &str,
    ms: u128,
    snap: &Snapshot,
    runs: &[CheckRun],
    threads_used: &[String],
    workers: usize,
) -> Value {
    let all_findings: Vec<&Value> = runs
        .iter()
        .filter_map(|r| r.family.as_ref())
        .flat_map(|f| f.findings.iter())
        .collect();
    let wanted_findings: Vec<&Value> = runs
        .iter()
        .filter(|r| r.wanted)
        .filter_map(|r| r.family.as_ref())
        .flat_map(|f| f.findings.iter())
        .collect();
    let count = |s: Status| runs.iter().filter(|r| r.status == s).count();
    let complete = runs.iter().all(|r| r.status != Status::NotEvaluated);
    let checks: Vec<Value> = runs
        .iter()
        .map(|r| {
            let def = def_for(&r.id);
            json!({
                "id": r.id, "status": r.status.as_str(), "wanted": r.wanted,
                "ok": r.family.as_ref().map(|f| f.ok), "max_severity": r.family.as_ref().map(|f| max_severity(&f.findings)),
                "findings": r.family.as_ref().map(|f| f.findings.len()), "key": r.key, "duration_ms": r.duration_ms as u64,
                "threads": r.threads, "isolation": r.isolation, "reproducible": r.reproducible, "cached_from": r.cached_from,
                "enforcement": catalogue::enforcement(def),
            })
        })
        .collect();
    json!({
        "id": run_id,
        "schema": "gov.health-result/1",
        "surface": opts.surface,
        "tier": opts.tier.as_str(),
        "tier_duty": opts.tier.duty(),
        "trigger": opts.trigger.to_value(),
        "selection": match &opts.selection { Selection::All => json!("all"), Selection::Tier(t) => json!(format!("tier:{}", t.as_str())), Selection::Explicit(v) => json!({"explicit": v}) },
        "cache_mode": opts.cache.as_str(),
        "deep": opts.deep,
        "checks": checks,
        "summary": {"executed": count(Status::Executed), "reused": count(Status::Reused), "not_evaluated": count(Status::NotEvaluated), "complete": complete,
                     "executed_checks": runs.iter().filter(|r| r.status == Status::Executed).map(|r| r.id.clone()).collect::<Vec<_>>(),
                     "reused_checks": runs.iter().filter(|r| r.status == Status::Reused).map(|r| r.id.clone()).collect::<Vec<_>>(),
                     "not_evaluated_checks": runs.iter().filter(|r| r.status == Status::NotEvaluated).map(|r| r.id.clone()).collect::<Vec<_>>()},
        "parallelism": {"workers": workers, "threads_used": threads_used, "process_id": std::process::id()},
        "inputs": snap.classes_value(),
        "inputs_hash": snap.key(),
        "excluded_health_outputs": snap.excluded.len(),
        "runtime": snap.runtime,
        "machine_trust": snap.machine_trust,
        "repository": repository_state(p, snap),
        "actor": {"role": p.role, "session": p.session_id, "pid": std::process::id()},
        "started_at": started_at,
        "finished_at": now_iso(),
        "duration_ms": ms as u64,
        "verdict": verdict_of(&wanted_findings),
        "suite_verdict": if complete { json!(verdict_of(&all_findings)) } else { json!("INCOMPLETE") },
        "record": Value::Null,
        "qualification": opts.qualification,
    })
}

/// Repository state for provenance: commit, dirty file count and the content key of the tree.
pub fn repository_state(p: &Project, snap: &Snapshot) -> Value {
    let dirty = p.git_dirty_files();
    json!({"git_commit": p.git_commit(), "git_dirty_files": dirty.len(), "content_key": snap.key(), "root_name": p.root.file_name().map(|n| n.to_string_lossy().to_string())})
}

// ------------------------------------------------------------------------------------------------ state & blocks

/// The subjects a finding names: its explicit `subjects`, else the records and paths it carries (`path`, `record`,
/// `records`, an orphan's subject). Empty when it names none.
fn finding_subjects(f: &Value) -> Vec<String> {
    let mut v: Vec<String> = vec![];
    let mut push = |x: &Value| {
        if let Some(s) = x.as_str() {
            if !s.is_empty() {
                v.push(s.to_string());
            }
        }
    };
    for x in f["subjects"].as_array().cloned().unwrap_or_default() {
        push(&x);
    }
    push(&f["path"]);
    push(&f["record"]);
    for x in f["records"].as_array().cloned().unwrap_or_default() {
        push(&x);
    }
    push(&f["orphan"]["subject"]);
    v.sort();
    v.dedup();
    v
}

fn blocking_findings(def: &CheckDef, findings: &[Value]) -> Vec<Value> {
    let lowest = def
        .blocks
        .iter()
        .map(|b| catalogue::rank(b.min_severity))
        .min();
    let Some(lowest) = lowest else {
        return vec![];
    };
    findings
        .iter()
        .filter(|f| catalogue::rank(f["severity"].as_str().unwrap_or("low")) >= lowest)
        .map(|f| {
            let named = finding_subjects(f);
            let (subjects, implicit) = if named.is_empty() {
                (catalogue::governed_paths(def), true)
            } else {
                (named, false)
            };
            json!({"severity": f["severity"], "message": f["message"], "covers": f.get("covers").cloned().unwrap_or(Value::Null),
                   "path": f.get("path").cloned().unwrap_or(Value::Null), "subjects": subjects, "subjects_implicit": implicit})
        })
        .collect()
}

/// Recompute the active blocks from the latest outcome of every check.
fn derive_blocks(checks: &Map<String, Value>) -> Vec<Value> {
    let mut out = vec![];
    for (id, e) in checks {
        let def = def_for(id);
        for f in e["blocking_findings"]
            .as_array()
            .cloned()
            .unwrap_or_default()
        {
            let sev = f["severity"].as_str().unwrap_or("low");
            for rule in def.blocks {
                if !catalogue::triggers(rule, sev) {
                    continue;
                }
                out.push(json!({
                    "check": id, "surface": e["surface"], "severity": sev, "operations": rule.operations,
                    "scope": rule.scope.as_str(), "remedies": rule.remedies,
                    "subjects": f.get("subjects").cloned().unwrap_or(json!([])), "subjects_implicit": f["subjects_implicit"],
                    "covers": f["covers"], "message": f["message"], "result": e["result"], "at": e["at"], "key": e["key"],
                }));
            }
        }
    }
    out
}

fn update_state(p: &Project, entries: Vec<(String, Value)>, run_id: &str) -> Result<()> {
    let mut st = store::load_state(p);
    let mut checks = st["checks"].as_object().cloned().unwrap_or_default();
    for (id, e) in entries {
        checks.insert(id, e);
    }
    let blocks = derive_blocks(&checks);
    st["checks"] = Value::Object(checks);
    st["blocks"] = json!(blocks);
    st["updated_at"] = json!(now_iso());
    st["last_result"] = json!(run_id);
    store::save_state(p, &st)
}

fn update_state_from_suite(p: &Project, out: &SuiteOutcome, run_id: &str) -> Result<()> {
    let at = now_iso();
    let entries = out
        .runs
        .iter()
        .filter_map(|r| {
            let f = r.family.as_ref()?;
            let def = def_for(&r.id);
            Some((
                r.id.clone(),
                json!({"surface": "family", "ok": f.ok, "max_severity": max_severity(&f.findings), "result": run_id, "at": at, "key": r.key,
                       "status": r.status.as_str(), "blocking_findings": blocking_findings(def, &f.findings)}),
            ))
        })
        .collect();
    update_state(p, entries, run_id)
}

/// Record a `gov doctor` report as a health result (tier G1 diagnostics) and refresh the blocks its checks declare.
pub fn record_doctor(p: &Project, report: &Value, snap: Option<&Snapshot>) -> Result<Value> {
    let run_id = store::new_result_id();
    let owned;
    let snap = match snap {
        Some(s) => s,
        None => {
            owned = Snapshot::take(p)?;
            &owned
        }
    };
    let at = now_iso();
    let checks = report["checks"].as_array().cloned().unwrap_or_default();
    let mut entries = vec![];
    let mut rows = vec![];
    for c in &checks {
        let id = c["id"].as_str().unwrap_or("").to_string();
        let def = def_for(&id);
        let key = snap.key_for(&catalogue::expand_deps(def));
        let ok = c["ok"].as_bool().unwrap_or(true);
        let sev = if ok {
            "none"
        } else {
            c["severity"].as_str().unwrap_or("low")
        };
        let findings: Vec<Value> = if ok {
            vec![]
        } else {
            vec![
                json!({"severity": sev, "message": c["message"], "covers": c.get("covers").cloned().unwrap_or(Value::Null), "subjects": c.get("subjects").cloned().unwrap_or(json!([]))}),
            ]
        };
        entries.push((
            id.clone(),
            json!({"surface": "doctor", "ok": ok, "max_severity": sev, "result": run_id, "at": at, "key": key, "status": "executed", "blocking_findings": blocking_findings(def, &findings)}),
        ));
        rows.push(json!({"id": id, "status": "executed", "ok": ok, "max_severity": sev, "key": key, "enforcement": catalogue::enforcement(def)}));
    }
    update_state(p, entries, &run_id)?;
    let st = store::load_state(p);
    let result = json!({
        "id": run_id, "schema": "gov.health-result/1", "surface": "doctor", "tier": "G1", "tier_duty": Tier::G1.duty(),
        "trigger": {"event": "gov doctor", "subject": null, "paths": []}, "checks": rows,
        "summary": {"executed": checks.len(), "reused": 0, "not_evaluated": 0, "complete": true},
        "inputs": snap.classes_value(), "inputs_hash": snap.key(), "runtime": snap.runtime, "machine_trust": snap.machine_trust,
        "repository": repository_state(p, snap), "actor": {"role": p.role, "session": p.session_id, "pid": std::process::id()},
        "started_at": at, "finished_at": now_iso(), "verdict": report["verdict"], "state": health_state(&st), "blocks": st["blocks"], "record": null,
    });
    store::save_result(p, &result)?;
    let _ = crate::observability::emit(
        p,
        "health.run",
        json!({"id": run_id, "tier": "G1", "surface": "doctor", "executed": checks.len(), "reused": 0, "verdict": report["verdict"], "state": result["state"]}),
    );
    Ok(
        json!({"id": run_id, "state": result["state"], "blocks": st["blocks"].as_array().map(|a| a.len()).unwrap_or(0)}),
    )
}

/// RED when a hard-block is active, YELLOW when any check's latest outcome failed as a warning, GREEN otherwise.
pub fn health_state(st: &Value) -> &'static str {
    if st["blocks"]
        .as_array()
        .map(|a| !a.is_empty())
        .unwrap_or(false)
    {
        return "RED";
    }
    let warn = st["checks"]
        .as_object()
        .map(|m| {
            m.values().any(|e| {
                !e["ok"].as_bool().unwrap_or(true)
                    && catalogue::rank(e["max_severity"].as_str().unwrap_or("none")) >= 2
            })
        })
        .unwrap_or(false);
    if warn {
        "YELLOW"
    } else {
        "GREEN"
    }
}

// -------------------------------------------------------------------------- G0: one host API (availability rule)

/// A governed operation presented to the G0 guard: the operation ([`catalogue::ops`]) and its **subjects** — the
/// record ids and repository paths (globs allowed) it starts, hands off, completes or changes. Examples: a task close
/// names the task, its declared inputs and every touched path (`verification::close_gate`); a change transaction names
/// its targets and manifest paths; `update --apply` names [`catalogue::ops::UPDATE_SUBJECTS`]. An empty subject list
/// means "the operation as a whole": only blocks that are not subject-scoped can be decided for it.
#[derive(Debug, Clone, Default)]
pub struct Request {
    pub operation: String,
    pub subjects: Vec<String>,
}

impl Request {
    pub fn new(operation: &str) -> Self {
        Request {
            operation: operation.to_string(),
            subjects: vec![],
        }
    }
    pub fn with_subjects<S: AsRef<str>>(mut self, subjects: &[S]) -> Self {
        self.subjects
            .extend(subjects.iter().map(|s| s.as_ref().to_string()));
        self
    }
    pub fn to_value(&self) -> Value {
        json!({"operation": self.operation, "subjects": self.subjects})
    }
}

/// The G0 decision for a [`Request`] that is not refused.
#[derive(Debug, Clone)]
pub struct Admission {
    pub operation: String,
    pub subjects: Vec<String>,
    /// Active blocks this operation is admitted under **as their remedy** (empty: no block governs it). When the
    /// operation commits ([`Admission::obligation`]), it may commit only after [`confirm_remedy`] shows every one of
    /// them cleared.
    pub remedy_for: Vec<Value>,
    /// Checks re-evaluated because their inputs changed since the block was recorded.
    pub reevaluated: Vec<String>,
    /// The mutation observation (G1) this decision was taken after.
    pub observed: Value,
}

impl Admission {
    pub fn is_remedy(&self) -> bool {
        !self.remedy_for.is_empty()
    }
    /// Does the host owe a [`confirm_remedy`] before committing?
    pub fn obligation(&self) -> bool {
        self.is_remedy() && catalogue::ops::COMMITTING.contains(&self.operation.as_str())
    }
    pub fn to_value(&self) -> Value {
        json!({"operation": self.operation, "allowed": true, "subjects": self.subjects, "remedy_for": self.remedy_for,
               "remedy": self.is_remedy(), "obligation": if self.obligation() { json!("confirm_remedy before commit: the blocks listed in remedy_for must be cleared by this change, else roll back") } else { Value::Null },
               "blocks": [], "reevaluated": self.reevaluated, "observed": self.observed})
    }
}

fn subject_matches(a: &str, b: &str) -> bool {
    a == b || glob_match(a, b) || glob_match(b, a)
}

/// Does any requested subject reach any block subject?
pub fn subjects_reach(block_subjects: &[String], request: &[String]) -> bool {
    request
        .iter()
        .any(|r| block_subjects.iter().any(|b| subject_matches(b, r)))
}

/// Add each named record's path and each record path's id, so ids and paths match either way.
fn with_record_aliases(store: &RecordStore, subjects: &[String]) -> Vec<String> {
    let mut out: Vec<String> = subjects.to_vec();
    for s in subjects {
        if let Some(r) = store.get(s) {
            out.push(r.path.clone());
        } else if let Some(r) = store.records.iter().find(|r| &r.path == s) {
            out.push(r.id());
        }
    }
    out.sort();
    out.dedup();
    out
}

fn block_subjects(b: &Value, store: &RecordStore) -> Vec<String> {
    let v: Vec<String> = b["subjects"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    with_record_aliases(store, &v)
}

/// How an active block bears on a request: it does not apply, it refuses the request, or it admits the request as
/// its remedy.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Bearing {
    None,
    Refuses,
    Remedy,
}

fn bearing(b: &Value, req: &Request, req_subjects: &[String], store: &RecordStore) -> Bearing {
    let op = req.operation.as_str();
    let listed = |k: &str| {
        b[k].as_array()
            .map(|a| a.iter().any(|o| o.as_str() == Some(op)))
            .unwrap_or(false)
    };
    let refused_op = listed("operations");
    let remedy_op = listed("remedies");
    if !refused_op && !remedy_op {
        return Bearing::None;
    }
    let bsub = block_subjects(b, store);
    let reaches = !req_subjects.is_empty() && subjects_reach(&bsub, req_subjects);
    if remedy_op && reaches {
        return Bearing::Remedy;
    }
    if !refused_op {
        return Bearing::None;
    }
    let applies = match b["scope"].as_str() {
        Some("covered-paths") => {
            let covers: Vec<String> = b["covers"]
                .as_array()
                .map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(|s| s.to_string()))
                        .collect()
                })
                .unwrap_or_default();
            covers.is_empty()
                || req
                    .subjects
                    .iter()
                    .any(|pth| covers.iter().any(|c| glob_match(c, pth)))
        }
        Some("subjects") => reaches,
        _ => true,
    };
    if applies {
        Bearing::Refuses
    } else {
        Bearing::None
    }
}

/// Split the active blocks of `st` by their bearing on `req`: (refusing, remedial).
fn classify_blocks(st: &Value, req: &Request, store: &RecordStore) -> (Vec<Value>, Vec<Value>) {
    let req_subjects = with_record_aliases(store, &req.subjects);
    let (mut refusing, mut remedial) = (vec![], vec![]);
    for b in st["blocks"].as_array().cloned().unwrap_or_default() {
        match bearing(&b, req, &req_subjects, store) {
            Bearing::Refuses => refusing.push(b),
            Bearing::Remedy => remedial.push(b),
            Bearing::None => {}
        }
    }
    (refusing, remedial)
}

/// Re-evaluate the checks behind `blocks` whose declared inputs changed since the block was recorded (or that are
/// never cached), so a repaired condition never keeps refusing work and an unrepaired one never stops refusing it.
fn reevaluate(
    p: &Project,
    blocks: &[Value],
    operation: &str,
    subjects: &[String],
    force: bool,
) -> Result<Vec<String>> {
    if blocks.is_empty() {
        return Ok(vec![]);
    }
    let snap = Snapshot::take(p)?;
    let mut extras = Extras {
        p,
        deep: false,
        memo: BTreeMap::new(),
    };
    let mut fam_rerun: Vec<String> = vec![];
    let mut doctor_rerun = false;
    for b in blocks {
        let id = b["check"].as_str().unwrap_or("");
        let def = def_for(id);
        let now_key = match def.surface {
            Surface::Family => check_key(&snap, def, id, &mut extras).0,
            Surface::Doctor => snap.key_for(&catalogue::expand_deps(def)),
        };
        if force || b["key"].as_str() != Some(now_key.as_str()) || def.cache == Cache::Never {
            match def.surface {
                Surface::Family => fam_rerun.push(id.to_string()),
                Surface::Doctor => doctor_rerun = true,
            }
        }
    }
    fam_rerun.sort();
    fam_rerun.dedup();
    let mut reevaluated = vec![];
    if !fam_rerun.is_empty() {
        let mut o = RunOptions::new(Tier::G0, Trigger::new(operation).with_paths(subjects));
        o.selection = Selection::Explicit(fam_rerun.clone());
        o.surface = "guard".into();
        o.record = RecordPolicy::Never;
        o.cache = if force {
            CacheMode::Refresh
        } else {
            CacheMode::Use
        };
        o.snapshot = Some(snap);
        run_suite(p, &o)?;
        reevaluated.extend(fam_rerun);
    }
    if doctor_rerun {
        crate::doctor::run(p)?;
        reevaluated.push("doctor".into());
    }
    Ok(reevaluated)
}

fn describe_block(b: &Value) -> String {
    let subj: Vec<String> = b["subjects"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .take(4)
                .collect()
        })
        .unwrap_or_default();
    format!(
        "check {} ({}, scope {}{}): {}",
        b["check"].as_str().unwrap_or("?"),
        b["severity"].as_str().unwrap_or("?"),
        b["scope"].as_str().unwrap_or("global"),
        if subj.is_empty() || b["scope"] == "global" {
            String::new()
        } else {
            format!(" [{}]", subj.join(", "))
        },
        b["message"].as_str().unwrap_or("")
    )
}

fn hard_block_error(req: &Request, refusing: &[Value], reevaluated: &[String]) -> GovError {
    GovError::new(
        "HEALTH_HARD_BLOCK",
        format!(
            "{} is refused: {} active hard-block(s) govern it, e.g. {}. Repair the condition (or run the work that remedies it: an operation listed as a block's remedy that names the blocked subjects stays available), then re-run `gov health run` (or `gov doctor` for doctor checks) to clear it",
            req.operation,
            refusing.len(),
            describe_block(&refusing[0])
        ),
    )
    .with_details(json!({"operation": req.operation, "subjects": req.subjects, "paths": req.subjects, "blocks": refusing, "reevaluated": reevaluated,
        "remediation": "repair the failing condition; `gov health status` lists every active block with its check, scope and subjects; `gov health run` re-evaluates"}))
}

/// **G0 (tier contract; the one host API).** Decide `req` against the active hard-blocks after observing the
/// mutations made since the last observation (G1, [`observe`]):
///
/// * a block **refuses** the request when the operation is one it protects and its scope applies (global;
///   covered paths; or subjects the request reaches) — unless the request is that block's remedy;
/// * a block **admits** the request as its **remedy** when the operation is listed among the block's remedies and the
///   request's subjects reach the block's subjects — the work that repairs the condition stays available;
/// * every other block does not bear on the request: independent work stays available.
///
/// Blocks whose check inputs changed since they were recorded are re-evaluated first. The refusal is
/// `HEALTH_HARD_BLOCK` (exit 4) naming every refusing block, its check, scope and subjects. On admission the host
/// that commits a change must honour [`Admission::obligation`] with [`confirm_remedy`].
pub fn admit(p: &Project, req: &Request) -> Result<Admission> {
    // an operation that commits a change the repository then relies on first observes every mutation made since the
    // last observation (G1 before reliance); operations that only start, hand off or propose work are decided on the
    // recorded state
    let observed = if catalogue::ops::COMMITTING.contains(&req.operation.as_str()) {
        observe(p).unwrap_or_else(|e| json!({"error": e.code, "message": e.message}))
    } else {
        Value::Null
    };
    let store = RecordStore::load(&p.root);
    let (refusing, remedial) = classify_blocks(&store::load_state(p), req, &store);
    let mut all: Vec<Value> = refusing.clone();
    all.extend(remedial.iter().cloned());
    if all.is_empty() {
        return Ok(Admission {
            operation: req.operation.clone(),
            subjects: req.subjects.clone(),
            remedy_for: vec![],
            reevaluated: vec![],
            observed,
        });
    }
    let reevaluated = reevaluate(p, &all, &req.operation, &req.subjects, false)?;
    let store = RecordStore::load(&p.root);
    let (refusing, remedial) = classify_blocks(&store::load_state(p), req, &store);
    if !refusing.is_empty() {
        return Err(hard_block_error(req, &refusing, &reevaluated));
    }
    Ok(Admission {
        operation: req.operation.clone(),
        subjects: req.subjects.clone(),
        remedy_for: remedial,
        reevaluated,
        observed,
    })
}

/// **The remedy obligation.** After a host admitted as a remedy ([`Admission::obligation`]) has applied its change
/// and before it commits: re-evaluate every block the admission was granted under, fresh, against the changed state.
/// `Ok` when none remains (the change repaired what it was admitted for); `HEALTH_REMEDY_INCOMPLETE` (exit 4) naming
/// every block left otherwise — the host rolls back: nothing commits under a block it does not clear. A block that
/// still admits or refuses the operation counts as left.
pub fn confirm_remedy(p: &Project, adm: &Admission) -> Result<Value> {
    if !adm.is_remedy() {
        return Ok(json!({"remedy": false, "cleared": []}));
    }
    let reevaluated = reevaluate(p, &adm.remedy_for, &adm.operation, &adm.subjects, true)?;
    let req = Request {
        operation: adm.operation.clone(),
        subjects: adm.subjects.clone(),
    };
    let store = RecordStore::load(&p.root);
    let (refusing, remedial) = classify_blocks(&store::load_state(p), &req, &store);
    let checks: Vec<&str> = adm
        .remedy_for
        .iter()
        .filter_map(|b| b["check"].as_str())
        .collect();
    let left: Vec<Value> = refusing
        .into_iter()
        .chain(remedial)
        .filter(|b| checks.contains(&b["check"].as_str().unwrap_or("")))
        .collect();
    if !left.is_empty() {
        return Err(GovError::new(
            "HEALTH_REMEDY_INCOMPLETE",
            format!(
                "{} was admitted under {} hard-block(s) as their remedy, but after its change {} still hold(s), e.g. {} — a remedy that does not clear its block does not commit; roll the change back",
                adm.operation,
                adm.remedy_for.len(),
                left.len(),
                describe_block(&left[0])
            ),
        )
        .with_details(json!({"operation": adm.operation, "subjects": adm.subjects, "admitted_under": adm.remedy_for, "left": left, "reevaluated": reevaluated})));
    }
    Ok(json!({"remedy": true, "cleared": adm.remedy_for, "reevaluated": reevaluated}))
}

/// **G0 guard for hosts that pass the paths they touch** (`control::guard_write`, WS-3; task, CIT, handoff, release
/// and adopt hosts). The same decision as [`admit`] with the paths as subjects. It cannot hand back a remedy
/// obligation, so a **committing** operation (`ops::COMMITTING`) that would be admitted only as a remedy is refused
/// here (`HEALTH_HARD_BLOCK`, `details.remedy_admissible: true`): its host either applies-then-verifies (e.g. CIT-E's
/// repair mode re-guards the committed state and rolls back) or uses [`admit`] + [`confirm_remedy`]. A non-committing
/// operation admitted as a remedy (proposing or approving the change that repairs a block, creating, claiming or
/// handing off the task that repairs it) is allowed.
pub fn guard(p: &Project, operation: &str, paths: &[String]) -> Result<Value> {
    let req = Request::new(operation).with_subjects(paths);
    let adm = admit(p, &req)?;
    if adm.obligation() {
        return Err(GovError::new(
            "HEALTH_HARD_BLOCK",
            format!(
                "{operation} is refused here: {} active hard-block(s) govern it and it is admissible only as their remedy, e.g. {} — a remedy commits only once it has cleared them (apply, then confirm: `scheduler::admit` + `scheduler::confirm_remedy`; CIT-E re-guards the applied state)",
                adm.remedy_for.len(),
                describe_block(&adm.remedy_for[0])
            ),
        )
        .with_details(json!({"operation": operation, "subjects": paths, "paths": paths, "blocks": adm.remedy_for, "remedy_admissible": true, "reevaluated": adm.reevaluated,
            "remediation": "apply the change and confirm that it clears the listed blocks before committing"})));
    }
    Ok(adm.to_value())
}

// ------------------------------------------------------------------------------------ G1: mutation observation

fn observed_path(p: &Project) -> std::path::PathBuf {
    store::dir(p).join("observed.json")
}

/// Input classes whose change is a **milestone** (Contract v3:797 "CIT-E/migration/memory/architecture changes"):
/// architecture and interface specifications, kernel migrations and the lock, the model/retrieval profile. A
/// mutation of one of them, however made, is observed at G4 (wider staleness/impact propagation) instead of G1.
pub const MILESTONE_CLASSES: &[&str] = &[
    "spec_architecture",
    "kernel_migration",
    "framework_lock",
    "model_profile",
];

fn save_observed(p: &Project, snap: &Snapshot, by: &str) -> Result<()> {
    let files: Map<String, Value> = snap
        .files
        .iter()
        .map(|(k, (c, d))| (k.clone(), json!([c, d])))
        .collect();
    let path = observed_path(p);
    if let Some(d) = path.parent() {
        std::fs::create_dir_all(d)?;
    }
    let tmp = path.with_extension(format!("tmp-{}", crate::util::short_uuid()));
    crate::util::write_json(
        &tmp,
        &json!({"key": snap.key(), "by": by, "at": now_iso(), "memory_profile": memory_profile_digest(p), "files": files}),
    )?;
    std::fs::rename(&tmp, &path)?;
    Ok(())
}

/// The digest of the memory profile: the index manifest's core (what the index was built from and with, not its
/// per-artefact entries) and the pins the effective policy asks for (embedder, reranker, chunking, lexical, index
/// format). A change of either is a memory change (a pin changed in the policy overlay, or the index rebuilt under
/// another profile).
fn memory_profile_digest(p: &Project) -> String {
    let core = match crate::memory::manifest::read_index_manifest(p) {
        Some(mut m) => {
            if let Some(o) = m.as_object_mut() {
                for k in [
                    "artifacts",
                    "excluded",
                    "built_at",
                    "repo_commit",
                    "counts",
                    "manifest_hash",
                ] {
                    o.remove(k);
                }
            }
            m
        }
        None => json!("absent"),
    };
    // the pins as the effective policy states them (not the plugin set a role may use: the digest must not depend on
    // who observes)
    let mem = p
        .policies()
        .effective
        .get("MEMORY_POLICY")
        .cloned()
        .unwrap_or(Value::Null);
    let pins = json!({"embedding": mem["embedding"], "reranker": mem["reranker"], "chunking": mem["chunking"],
                      "lexical": mem["lexical"], "index_version": crate::INDEX_VERSION});
    hash_value(&json!({"index": core, "pins": pins}))
}

/// **G1 at every material mutation, however made** (Contract v3:794, W12 :1187; BC-P2-07). The product is not a
/// daemon: a mutation made by an editor, a worker, a script or a gov command is observed at the next gov invocation
/// that commits a change the repository then relies on ([`admit`] of a committing operation: task close, CIT-E,
/// release, update, migration) or that reports state (`gov status`, `gov continue`, `gov health status`) — so no
/// mutation is relied on before G1 has checked it. The
/// tree is compared with the state the last observation (or any run that evaluated every G1 check) saw; when paths
/// changed, the G1 tier runs on them — the checks whose declared inputs the change impacts are re-executed, the others
/// are served from the cache — and the result is recorded with trigger `mutation.observed` and the changed paths. A
/// change to a milestone input ([`MILESTONE_CLASSES`], or the memory profile of the index manifest) is observed at
/// G4. Nothing governed is written: no governance-suite record, no remediation (the hard-blocks it derives take effect
/// at once for the admission that observed it). Skipped inside health sandboxes and before installation.
pub fn observe(p: &Project) -> Result<Value> {
    if sandbox::inside_sandbox()
        || !p.lock_path().exists()
        || SUITE_DEPTH.load(Ordering::SeqCst) > 0
    {
        return Ok(Value::Null);
    }
    // one observation at a time per process: a check that reports state (fresh-agent reconstruction reads
    // `gov status`) must not observe again from inside the observation's own run
    if OBSERVING
        .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
        .is_err()
    {
        return Ok(json!({"skipped": "an observation is already running in this process"}));
    }
    let r = observe_inner(p);
    OBSERVING.store(false, Ordering::SeqCst);
    r
}

static OBSERVING: AtomicBool = AtomicBool::new(false);
/// Suite runs in progress in this process (a check that reports state must not start a run of its own).
pub(crate) static SUITE_DEPTH: AtomicUsize = AtomicUsize::new(0);

struct SuiteDepth;
impl SuiteDepth {
    fn enter() -> Self {
        SUITE_DEPTH.fetch_add(1, Ordering::SeqCst);
        SuiteDepth
    }
}
impl Drop for SuiteDepth {
    fn drop(&mut self) {
        SUITE_DEPTH.fetch_sub(1, Ordering::SeqCst);
    }
}

fn observe_inner(p: &Project) -> Result<Value> {
    let prev = crate::util::read_json(&observed_path(p)).unwrap_or(json!({}));
    let snap = Snapshot::take(p)?;
    if prev["key"].as_str() == Some(snap.key().as_str()) {
        return Ok(json!({"changed": 0}));
    }
    let prev_files: BTreeMap<String, (String, String)> = prev["files"]
        .as_object()
        .map(|m| {
            m.iter()
                .map(|(k, v)| {
                    (
                        k.clone(),
                        (
                            v[0].as_str().unwrap_or("").to_string(),
                            v[1].as_str().unwrap_or("").to_string(),
                        ),
                    )
                })
                .collect()
        })
        .unwrap_or_default();
    let changed = snap.changed_paths(&prev_files);
    let mut classes: Vec<String> = changed
        .iter()
        .map(|c| {
            snap.files
                .get(c)
                .map(|(k, _)| k.clone())
                .or_else(|| prev_files.get(c).map(|(k, _)| k.clone()))
                .unwrap_or_else(|| currency::classify_path(c).to_string())
        })
        .collect();
    classes.sort();
    classes.dedup();
    let profile = memory_profile_digest(p);
    let memory_change = prev["memory_profile"]
        .as_str()
        .map(|d| d != profile)
        .unwrap_or(false);
    let milestone = memory_change
        || classes
            .iter()
            .any(|c| MILESTONE_CLASSES.contains(&c.as_str()));
    if changed.is_empty() && !milestone {
        // only non-file classes changed (runtime, machine trust, T2 state): the next run re-keys; nothing to observe
        let _ = save_observed(p, &snap, "observe");
        return Ok(json!({"changed": 0, "non_file_classes_changed": true}));
    }
    let tier = if milestone { Tier::G4 } else { Tier::G1 };
    let shown: Vec<String> = changed.iter().take(200).cloned().collect();
    let mut o = RunOptions::new(tier, Trigger::new("mutation.observed").with_paths(&shown));
    o.surface = format!("observe:{}", tier.as_str());
    // exactly the tier's checks (the cache serves those whose declared inputs the change did not touch)
    o.selection = Selection::Explicit(
        suite_families(p)
            .into_iter()
            .filter(|id| def_for(id).tiers.contains(&tier))
            .collect(),
    );
    o.record = RecordPolicy::Never;
    o.single_run = true;
    o.snapshot = Some(snap.clone());
    let out = run_suite(p, &o)?;
    let _ = save_observed(p, &snap, out.result["id"].as_str().unwrap_or("observe"));
    Ok(json!({
        "tier": tier.as_str(), "changed": changed.len(), "changed_paths": shown, "changed_classes": classes,
        "milestone": milestone, "memory_profile_changed": memory_change,
        "health_result": out.result["id"], "verdict": out.result["verdict"], "state": out.result["state"],
        "executed": out.result["summary"]["executed_checks"],
    }))
}

/// Blocks recorded by governance-suite checks, split into those whose check inputs are unchanged since the blocking
/// result (current) and those whose inputs changed (stale: the next guard or health run re-evaluates them).
pub fn suite_blocks(p: &Project, snap: &Snapshot) -> (Vec<Value>, Vec<Value>) {
    let st = store::load_state(p);
    let mut extras = Extras {
        p,
        deep: false,
        memo: BTreeMap::new(),
    };
    let (mut current, mut stale) = (vec![], vec![]);
    for b in st["blocks"].as_array().cloned().unwrap_or_default() {
        if b["surface"] == "doctor" {
            continue;
        }
        let id = b["check"].as_str().unwrap_or("");
        let def = def_for(id);
        let now_key = check_key(snap, def, id, &mut extras).0;
        if b["key"].as_str() == Some(now_key.as_str()) && def.cache != Cache::Never {
            current.push(b);
        } else {
            stale.push(b);
        }
    }
    (current, stale)
}

/// The repository health state: RED/YELLOW/GREEN, active blocks, latest check outcomes, stale checks and currency;
/// the **repository verdict** (the thirteen HEALTHY conditions, `verification::slo`), every Gate U SLO and the W11
/// artifact-flow metrics of the latest suite result. Mutations made since the last observation are observed first
/// (G1, [`observe`]), so the state reflects every material mutation however made.
pub fn status(p: &Project) -> Result<Value> {
    let observed = if SUITE_DEPTH.load(Ordering::SeqCst) > 0 {
        Value::Null
    } else {
        observe(p).unwrap_or_else(|e| json!({"error": e.code, "message": e.message}))
    };
    let st = store::load_state(p);
    let snap = Snapshot::take(p)?;
    let cur = currency::Currency::evaluate(p, &snap);
    let mut extras = Extras {
        p,
        deep: false,
        memo: BTreeMap::new(),
    };
    let mut stale = vec![];
    if let Some(m) = st["checks"].as_object() {
        for (id, e) in m {
            let def = def_for(id);
            let now_key = match def.surface {
                Surface::Family => check_key(&snap, def, id, &mut extras).0,
                Surface::Doctor => snap.key_for(&catalogue::expand_deps(def)),
            };
            if e["key"].as_str() != Some(now_key.as_str()) {
                stale.push(id.clone());
            }
        }
    }
    let failing: Vec<Value> = st["checks"]
        .as_object()
        .map(|m| {
            m.iter()
                .filter(|(_, e)| !e["ok"].as_bool().unwrap_or(true))
                .map(|(id, e)| json!({"check": id, "max_severity": e["max_severity"], "result": e["result"], "at": e["at"], "enforcement": catalogue::enforcement(def_for(id))["mode"]}))
                .collect()
        })
        .unwrap_or_default();
    // the repository verdict and the SLOs (skipped when asked from inside a suite run: a check reading `gov status`
    // must not evaluate the checks that are running)
    let repository = if SUITE_DEPTH.load(Ordering::SeqCst) > 0 {
        json!({"verdict": "NOT_EVALUATED", "reason": "requested from inside a health run"})
    } else {
        let store = RecordStore::load(&p.root);
        let db = if p.db_path().exists() {
            crate::memory::db::RuntimeDb::open(&p.db_path()).ok()
        } else {
            None
        };
        let slos = crate::verification::slo::evaluate(&crate::verification::slo::SloCtx {
            p,
            store: &store,
            db: db.as_ref(),
            snapshot: Some(&snap),
            state: &st,
        });
        let conds = crate::verification::slo::conditions(&st, None, Some(cur.current));
        crate::verification::slo::repository_verdict(&conds, &slos)
    };
    let w11 = store::cache_peek(p, crate::verification::flow::FAMILY)
        .map(|c| json!({"metrics": c["result"]["detail"]["w11_metrics"], "computed_by": c["produced_by"], "at": c["produced_at"], "current": st["checks"][crate::verification::flow::FAMILY]["key"] == c["key"]}))
        .unwrap_or(json!({"metrics": null, "reason": "no artifact_flow_health result recorded yet (G4-G6: gov health run --tier G4, gov audit)"}));
    Ok(json!({
        "state": health_state(&st),
        "repository": repository,
        "blocks": st["blocks"],
        "failing_checks": failing,
        "stale_checks": stale,
        "governance_suite_currency": cur.to_value(),
        "last_result": st["last_result"],
        "updated_at": st["updated_at"],
        "observed": observed,
        "product_tests": crate::verification::product::status(p, Some(&snap)),
        "failure_memory": failure_memory_summary(p),
        "artifact_flow": w11,
    }))
}

/// Open failure-memory records (retrieval misses, tool failures) awaiting follow-up, by kind (ws06 IP-2).
pub fn failure_memory_summary(p: &Project) -> Value {
    let open = crate::memory::failures::open_failures(p);
    let mut by_kind: BTreeMap<String, usize> = BTreeMap::new();
    for f in &open {
        *by_kind
            .entry(f["failure_kind"].as_str().unwrap_or("?").to_string())
            .or_insert(0) += 1;
    }
    json!({"open": open.len(), "by_kind": by_kind, "records": open.iter().take(20).map(|f| json!({"id": f["id"], "failure_kind": f["failure_kind"], "title": f["title"]})).collect::<Vec<_>>()})
}

/// **Tier contract entry point for hosts.** Runs tier `tier` for `trigger` with the tier's defaults (see the module
/// table) and returns the health result. G0 delegates to [`guard`]. A tier run that leaves the governance suite
/// complete and green while the latest green record is stale persists a new governance-suite record, so work that
/// relies on currency can proceed without an operator-run full audit.
pub fn tier_run(p: &Project, tier: Tier, trigger: Trigger) -> Result<Value> {
    if tier == Tier::G0 {
        return guard(p, &trigger.event, &trigger.paths);
    }
    let mut o = RunOptions::new(tier, trigger);
    o.surface = format!("tier:{}", tier.as_str());
    // a milestone, full-suite or qualification result is governed evidence whatever its verdict (W12 :1190-1192;
    // WS-4 R2-7): it is recorded as a governance-suite record; G1-G3 results persist a record only when they
    // re-establish green currency
    if matches!(tier, Tier::G4 | Tier::G5 | Tier::G6) {
        o.record = RecordPolicy::Always;
    }
    crate::verification::audit_with(p, &o)
}

/// A G6 qualification run to observe: the verifier-owned hidden oracle, the score report of the candidate run, and
/// the directories the oracle must be kept out of.
#[derive(Debug, Clone, Default)]
pub struct QualificationRun {
    /// `synthetic-repository`, `chaos`, `soak` or `hidden-test` (Contract v3:799).
    pub kind: String,
    pub run_id: Option<String>,
    pub oracle: std::path::PathBuf,
    pub score_report: std::path::PathBuf,
    pub public_suites: Vec<std::path::PathBuf>,
    pub repositories: Vec<std::path::PathBuf>,
}

/// Qualification run kinds G6 observes (Contract v3:799 "synthetic repos/chaos/soak/hidden tests").
pub const QUALIFICATION_KINDS: &[&str] = &["synthetic-repository", "chaos", "soak", "hidden-test"];

/// **G6 entry point (tier contract; Contract v3:799; ws01-12 IP-4).** Accepts a qualification run and records its
/// health — only when the run's evidence is sound:
///
/// 1. the hidden oracle conforms to the Qualification Oracle format and is **separate** from the public suite, the
///    given qualification repositories **and this governed repository** (`ORACLE_RECORD_INVALID`,
///    `ORACLE_SEPARATION_VIOLATED`);
/// 2. the score report conforms and is **bound** to that oracle — identity, digest, every injected fault scored,
///    arithmetic (`ORACLE_SCORE_BINDING_MISMATCH`).
///
/// Then the G6 tier runs every check fresh (compared with the cache) and the health result and governance-suite
/// record carry the qualification: kind, run id, oracle id/digest/purpose, the report's binding and metrics. A
/// `FORMAT_SAMPLE` oracle is recorded with `counts_as_qualification: false`.
pub fn qualification_run(p: &Project, q: &QualificationRun) -> Result<Value> {
    use crate::qualification_oracle as qo;
    if !QUALIFICATION_KINDS.contains(&q.kind.as_str()) {
        return Err(GovError::new(
            "USAGE",
            format!(
                "unknown qualification run kind '{}' (expected one of {:?})",
                q.kind, QUALIFICATION_KINDS
            ),
        ));
    }
    let mut repos = q.repositories.clone();
    repos.push(p.root.clone());
    let oracle = qo::validate_file(
        &q.oracle,
        &qo::ValidateOptions {
            oracle: None,
            public_suites: q.public_suites.clone(),
            repositories: repos,
        },
    )?;
    if oracle["kind"] != qo::KIND_ORACLE {
        return Err(GovError::new(
            "QUALIFICATION_ORACLE_REQUIRED",
            format!(
                "{} is a {} document, not a qualification-oracle; G6 records a run only against the hidden oracle it was scored against",
                q.oracle.display(),
                oracle["kind"].as_str().unwrap_or("?")
            ),
        ));
    }
    let report = qo::validate_file(
        &q.score_report,
        &qo::ValidateOptions {
            oracle: Some(q.oracle.clone()),
            ..Default::default()
        },
    )?;
    if report["kind"] != qo::KIND_SCORE_REPORT {
        return Err(GovError::new(
            "QUALIFICATION_REPORT_REQUIRED",
            format!(
                "{} is a {} document, not a qualification-score-report",
                q.score_report.display(),
                report["kind"].as_str().unwrap_or("?")
            ),
        ));
    }
    let report_doc: Value = crate::util::read_text(&q.score_report)
        .ok()
        .and_then(|t| serde_yaml::from_str(&t).ok())
        .unwrap_or(Value::Null);
    let oracle_doc: Value = crate::util::read_text(&q.oracle)
        .ok()
        .and_then(|t| serde_yaml::from_str(&t).ok())
        .unwrap_or(Value::Null);
    let run_id = q
        .run_id
        .clone()
        .or_else(|| {
            report_doc["binding"]["run_id"]
                .as_str()
                .map(|s| s.to_string())
        })
        .unwrap_or_else(|| format!("QR-{}", crate::util::short_uuid()));
    let purpose = oracle["purpose"].as_str().unwrap_or("").to_string();
    // OWNER-DECISION-P2-0002 requirement 4 (WS-8 IP-R2-WS08-8): Phase-4 qualification evidence runs on provisioned
    // machines. A qualification run on a machine with no trust anchor is refused; a format-sample run is recorded
    // with the posture and never counts as qualification.
    let trust = currency::machine_trust_state();
    let provisioned = trust["posture"] == "PROVISIONED";
    if !provisioned && purpose == "QUALIFICATION" {
        return Err(GovError::new(
            "QUALIFICATION_MACHINE_UNPROVISIONED",
            format!(
                "a {} qualification run cannot be recorded on this machine: it has no provisioned Signed Release Root trust anchor (posture {}), and Phase-4 qualification evidence runs only on provisioned machines (OWNER-DECISION-P2-0002 requirement 4). Provision the machine (`gov trust provision --anchor <administrator root>`) and re-run",
                q.kind,
                trust["posture"].as_str().unwrap_or("?")
            ),
        )
        .with_details(json!({"machine_posture": trust["posture"], "remediation": "gov trust provision --anchor <root metadata from the administrator domain>"})));
    }
    // What is recorded lives in the qualification repository, so it must not carry the hidden oracle: no oracle id,
    // no oracle digest, no fault identities or truths (Contract v3:1062; the separation scan would — rightly — find
    // them). The oracle is referred to by a one-way commitment its custodian can recompute from the oracle digest;
    // the score report is recorded by its own digest and the numeric V4 metrics only.
    let commitment = |d: &Value| {
        crate::util::sha256_hex(
            format!(
                "governance-os/g6-oracle-commitment\n{}",
                d.as_str().unwrap_or("")
            )
            .as_bytes(),
        )
    };
    let _ = &oracle_doc;
    let metrics: Map<String, Value> = report_doc["metrics"]
        .as_object()
        .map(|m| {
            m.iter()
                .map(|(k, v)| {
                    let shown = if v.get("applicable") == Some(&json!(false)) {
                        json!({"applicable": false})
                    } else if let Some(x) = v.get("value") {
                        json!({"value": x})
                    } else if let Some(x) = v.get("count") {
                        json!({"count": x})
                    } else if v.is_number() {
                        v.clone()
                    } else {
                        json!({"recorded": true})
                    };
                    (k.clone(), shown)
                })
                .collect()
        })
        .unwrap_or_default();
    let qualification = json!({
        "kind": q.kind, "run_id": run_id,
        "oracle": {"commitment_sha256": commitment(&oracle["canonical_sha256"]), "purpose": purpose, "format_sha256": oracle["format_sha256"], "separation_checked": oracle["separation"]["scanned"]},
        "score_report": {"canonical_sha256": report["canonical_sha256"], "binding_verified": report["binding_verified"].is_object(), "metrics": metrics},
        "counts_as_qualification": purpose == "QUALIFICATION" && provisioned,
        "machine_posture": trust["posture"],
        "machine_trust_anchor_sha256": trust["trust_anchor_sha256"],
    });
    let mut o = RunOptions::new(Tier::G6, Trigger::qualification(&q.kind, &run_id));
    o.surface = "qualification".into();
    o.record = RecordPolicy::Always;
    o.qualification = Some(qualification.clone());
    let r = crate::verification::audit_with(p, &o)?;
    Ok(json!({"qualification": qualification, "health": r}))
}

/// Every declared check, the tiers and the operation vocabulary (`gov health checks`).
pub fn describe_catalogue() -> Value {
    json!({
        "tiers": Tier::all().iter().map(|t| json!({"tier": t.as_str(), "duty": t.duty(), "checks": catalogue::CHECKS.iter().filter(|c| c.tiers.contains(t)).map(|c| c.id).collect::<Vec<_>>()})).collect::<Vec<_>>(),
        "operations": catalogue::ops::ALL,
        "checks": catalogue::CHECKS.iter().map(catalogue::describe).collect::<Vec<_>>(),
        "input_classes": currency::all_class_ids().iter().map(|c| json!({"class": c, "contract_class": currency::contract_class_of(c)})).collect::<Vec<_>>(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tiers_parse_and_default_selection() {
        assert_eq!(Tier::parse("g2").unwrap(), Tier::G2);
        assert!(Tier::parse("G9").is_err());
        let o = RunOptions::new(Tier::G5, Trigger::new("update.apply"));
        assert_eq!(o.selection, Selection::All);
        assert_eq!(o.cache, CacheMode::Refresh);
        let o = RunOptions::new(Tier::G2, Trigger::task_close("TASK-1", &[]));
        assert_eq!(o.selection, Selection::Tier(Tier::G2));
        assert_eq!(o.cache, CacheMode::Use);
    }

    fn st_with(checks: &Map<String, Value>) -> Value {
        json!({"checks": checks, "blocks": derive_blocks(checks)})
    }

    fn empty_store() -> RecordStore {
        RecordStore {
            records: vec![],
            by_id: Default::default(),
            duplicates: vec![],
            problems: vec![],
        }
    }

    #[test]
    fn blocks_are_derived_from_declared_rules_and_scoped() {
        let mut checks = Map::new();
        checks.insert("D011".into(), json!({"surface": "doctor", "blocking_findings": blocking_findings(catalogue::get("D011").unwrap(), &[json!({"severity": "critical", "message": "secret", "subjects": ["src/creds.rs"]})]), "result": "HR-1", "at": "t", "key": "k"}));
        checks.insert("product_test_health".into(), json!({"surface": "family", "blocking_findings": [{"severity": "high", "message": "unit failed", "covers": ["src/**"], "subjects": ["**"]}], "result": "HR-2", "at": "t", "key": "k2"}));
        checks.insert("index_freshness".into(), json!({"surface": "family", "blocking_findings": [], "result": "HR-2", "at": "t", "key": "k3"}));
        let st = st_with(&checks);
        let store = empty_store();
        let refuses = |op: &str, subj: &[&str]| {
            let r = Request::new(op).with_subjects(subj);
            classify_blocks(&st, &r, &store)
        };
        // a critical global block refuses every governed operation...
        assert_eq!(refuses("task.create", &[]).0.len(), 1);
        assert_eq!(refuses("cit.propose", &["docs/n.md"]).0.len(), 1);
        // ...except the work that repairs exactly what it names (non-committing: allowed; committing: obligation)
        let (refusing, remedial) = refuses("cit.propose", &["src/creds.rs"]);
        assert!(refusing.is_empty() && remedial.len() == 1);
        // covered paths: only a close touching the covered code
        assert!(refuses("task.close", &["src/lib.rs"])
            .0
            .iter()
            .any(|b| b["check"] == "product_test_health"));
        assert!(!refuses("task.close", &["docs/x.md"])
            .0
            .iter()
            .any(|b| b["check"] == "product_test_health"));
        // a kernel update does not rely on product behaviour
        assert!(!refuses("update.apply", &["governance/kernel/**"])
            .0
            .iter()
            .any(|b| b["check"] == "product_test_health"));
        assert!(!st["blocks"]
            .as_array()
            .unwrap()
            .iter()
            .any(|b| b["check"] == "index_freshness"));
        assert_eq!(health_state(&st), "RED");
    }

    #[test]
    fn subject_scoped_blocks_leave_independent_work_available() {
        let mut checks = Map::new();
        let gi = catalogue::get("graph_integrity").unwrap();
        checks.insert("graph_integrity".into(), json!({"surface": "family", "blocking_findings": blocking_findings(gi, &[json!({"severity": "high", "message": "task TASK-0001 depends on missing TASK-0099", "subjects": ["TASK-0001", "TASK-0099"]})]), "result": "HR-1", "at": "t", "key": "k"}));
        let st = st_with(&checks);
        let store = empty_store();
        let r = |op: &str, subj: &[&str]| {
            classify_blocks(&st, &Request::new(op).with_subjects(subj), &store)
        };
        // the task it names cannot be claimed or closed ...
        assert_eq!(r("task.claim", &["TASK-0001"]).0.len(), 1);
        assert_eq!(r("task.close", &["TASK-0001", "src/lib.rs"]).0.len(), 1);
        // ... every other task stays available (O-R2-2), and so does an operation judged as a whole
        assert!(r("task.claim", &["TASK-0002"]).0.is_empty());
        assert!(r("task.close", &["TASK-0002", "docs/a.md"]).0.is_empty());
        assert!(r("task.claim", &[]).0.is_empty());
        // a release relies on the whole graph
        assert_eq!(r("release.build", &[]).0.len(), 1);
        // creating work is not refused by it; a change transaction on it is not refused either
        assert!(r("task.create", &["TASK-0099"]).0.is_empty());
        assert!(r("cit.execute", &["spec/tasks/TASK-0001.yaml"])
            .0
            .is_empty());
    }

    #[test]
    fn an_update_is_the_remedy_of_an_overlay_block_but_not_of_a_record_block() {
        let mut checks = Map::new();
        let d006 = catalogue::get("D006").unwrap();
        // D006 names no file of its own: its subjects are the paths it governs (the overlay)
        checks.insert("D006".into(), json!({"surface": "doctor", "blocking_findings": blocking_findings(d006, &[json!({"severity": "high", "message": "overlay file missing: PROJECT_EXCEPTIONS.yaml"})]), "result": "HR-1", "at": "t", "key": "k"}));
        let st = st_with(&checks);
        let store = empty_store();
        let upd = Request::new(catalogue::ops::UPDATE_APPLY)
            .with_subjects(catalogue::ops::UPDATE_SUBJECTS);
        let (refusing, remedial) = classify_blocks(&st, &upd, &store);
        assert!(refusing.is_empty(), "{refusing:?}");
        assert_eq!(remedial.len(), 1);
        let si = catalogue::get("schema_invariants").unwrap();
        let mut checks = Map::new();
        checks.insert("schema_invariants".into(), json!({"surface": "family", "blocking_findings": blocking_findings(si, &[json!({"severity": "high", "message": "REQ-0102 invalid", "path": "spec/requirements/REQ-0102.yaml"})]), "result": "HR-1", "at": "t", "key": "k"}));
        let st = st_with(&checks);
        let (refusing, _) = classify_blocks(&st, &upd, &store);
        assert_eq!(refusing.len(), 1, "an update does not repair a record");
        // a close elsewhere is not refused; a close that relies on the record is
        let (r1, _) = classify_blocks(
            &st,
            &Request::new("task.close").with_subjects(&["TASK-0001", "src/lib.rs"]),
            &store,
        );
        assert!(r1.is_empty());
        let (r2, _) = classify_blocks(
            &st,
            &Request::new("task.close")
                .with_subjects(&["TASK-0001", "spec/requirements/REQ-0102.yaml"]),
            &store,
        );
        assert_eq!(r2.len(), 1);
    }
}
