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
//! | G0 | guard every privileged/mutating command | every governed operation (`control::guard_write`, WS-3; task/CIT hosts) | [`guard`]: active hard-blocks, targeted re-evaluation |
//! | G1 | changed paths / schema / secrets / index invalidation | any material mutation (WS-4/WS-5/WS-6) | tier checks, cache |
//! | G2 | mutation scope / tests / references / memory freshness | task close (`tasks::close`, WS-5) | tier checks, cache |
//! | G3 | claims / decisions / gates / checkpoint freshness | checkpoint & handoff (WS-4) | tier checks, cache |
//! | G4 | wider staleness after CIT-E / migration / memory / architecture | CIT execute (WS-4), migration (WS-9) | tier checks, cache |
//! | G5 | full suite | adopt (WS-9), update/release (WS-8), `gov audit` | all checks, fresh (hosts) / cache (`gov audit`) |
//! | G6 | qualification (synthetic repos, chaos, soak, hidden tests) | qualification harness (Phase 4) | all checks, fresh, qualification subject recorded |
use crate::records::RecordStore;
use crate::util::{glob_match, hash_value, now_iso};
use crate::verification::currency::{self, Snapshot};
use crate::verification::Family;
use crate::{GovError, Project, Result};
use catalogue::{BlockScope, Cache, CheckDef, Extra, Isolation, Repro, Surface};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, VecDeque};
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
            Extra::Claims => {
                let rt = self.p.runtime_dir();
                sha_of_files(&[rt.join("claims.db"), rt.join("claims.db-wal")])
            }
            Extra::ProductEvidence => product_evidence_digest(self.p),
            Extra::SkillObservations => sha_of_files(&[crate::skills::observations_path(self.p)]),
            Extra::PluginObservations => {
                sha_of_files(&[self.p.runtime_dir().join("plugins").join("observed.json")])
            }
            Extra::DeepMode => self.deep.to_string(),
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
    let started = std::time::Instant::now();
    let started_at = now_iso();
    let run_id = store::new_result_id();
    let snap = Snapshot::take(p)?;
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
        if def_for(&runs[i].id).repro == Repro::DoubleRun {
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
    })
}

/// Repository state for provenance: commit, dirty file count and the content key of the tree.
pub fn repository_state(p: &Project, snap: &Snapshot) -> Value {
    let dirty = p.git_dirty_files();
    json!({"git_commit": p.git_commit(), "git_dirty_files": dirty.len(), "content_key": snap.key(), "root_name": p.root.file_name().map(|n| n.to_string_lossy().to_string())})
}

// ------------------------------------------------------------------------------------------------ state & blocks

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
        .map(|f| json!({"severity": f["severity"], "message": f["message"], "covers": f.get("covers").cloned().unwrap_or(Value::Null), "path": f.get("path").cloned().unwrap_or(Value::Null)}))
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
                    "scope": match rule.scope { BlockScope::Global => "global", BlockScope::CoveredPaths => "covered-paths" },
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
                json!({"severity": sev, "message": c["message"], "covers": c.get("covers").cloned().unwrap_or(Value::Null)}),
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

fn block_applies(b: &Value, operation: &str, paths: &[String]) -> bool {
    let ops_ok = b["operations"]
        .as_array()
        .map(|a| a.iter().any(|o| o.as_str() == Some(operation)))
        .unwrap_or(false);
    if !ops_ok {
        return false;
    }
    if b["scope"].as_str() != Some("covered-paths") {
        return true;
    }
    let covers: Vec<String> = b["covers"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    if covers.is_empty() {
        return true;
    }
    paths
        .iter()
        .any(|pth| covers.iter().any(|c| glob_match(c, pth)))
}

/// **G0 guard (tier contract).** Refuses `operation` (see [`catalogue::ops`]) while an active hard-block governs it.
/// A block whose check's declared inputs have changed since it was recorded is re-evaluated first (only that check),
/// so a repaired condition never keeps refusing work and an unrepaired one never stops refusing it.
///
/// Integration points: `orchestration::control::guard_write` (WS-3) for every governed operation; `tasks::create`,
/// `tasks::claim`, `status::continue_work(claim)`, `tasks::close` (WS-5); `cit::propose`/`approve`/`execute`,
/// `handoffs::create` (WS-4); `release::build`, `update::apply_update_opts` (WS-8); `adopt::a6_migrate` (WS-9).
pub fn guard(p: &Project, operation: &str, paths: &[String]) -> Result<Value> {
    let st = store::load_state(p);
    let active: Vec<Value> = st["blocks"]
        .as_array()
        .cloned()
        .unwrap_or_default()
        .into_iter()
        .filter(|b| block_applies(b, operation, paths))
        .collect();
    if active.is_empty() {
        return Ok(json!({"operation": operation, "allowed": true, "blocks": []}));
    }
    // targeted re-evaluation of blocking checks whose inputs changed
    let snap = Snapshot::take(p)?;
    let mut extras = Extras {
        p,
        deep: false,
        memo: BTreeMap::new(),
    };
    let mut fam_rerun: Vec<String> = vec![];
    let mut doctor_rerun = false;
    for b in &active {
        let id = b["check"].as_str().unwrap_or("");
        let def = def_for(id);
        let now_key = match def.surface {
            Surface::Family => check_key(&snap, def, id, &mut extras).0,
            Surface::Doctor => snap.key_for(&catalogue::expand_deps(def)),
        };
        if b["key"].as_str() != Some(now_key.as_str()) || def.cache == Cache::Never {
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
        let mut o = RunOptions::new(Tier::G0, Trigger::new(operation).with_paths(paths));
        o.selection = Selection::Explicit(fam_rerun.clone());
        o.surface = "guard".into();
        o.record = RecordPolicy::Never;
        run_suite(p, &o)?;
        reevaluated.extend(fam_rerun);
    }
    if doctor_rerun {
        crate::doctor::run(p)?;
        reevaluated.push("doctor".into());
    }
    let st = store::load_state(p);
    let still: Vec<Value> = st["blocks"]
        .as_array()
        .cloned()
        .unwrap_or_default()
        .into_iter()
        .filter(|b| block_applies(b, operation, paths))
        .collect();
    if still.is_empty() {
        return Ok(
            json!({"operation": operation, "allowed": true, "blocks": [], "reevaluated": reevaluated}),
        );
    }
    let first = &still[0];
    Err(GovError::new(
        "HEALTH_HARD_BLOCK",
        format!(
            "{operation} is refused: {} active hard-block(s), e.g. check {} ({}): {}. Repair the condition, then re-run `gov health run` (or `gov doctor` for doctor checks) to clear it",
            still.len(),
            first["check"].as_str().unwrap_or("?"),
            first["severity"].as_str().unwrap_or("?"),
            first["message"].as_str().unwrap_or("")
        ),
    )
    .with_details(json!({"operation": operation, "paths": paths, "blocks": still, "reevaluated": reevaluated, "remediation": "repair the failing condition; `gov health status` lists every active block and its check; `gov health run` re-evaluates"})))
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

/// The repository health state: RED/YELLOW/GREEN, active blocks, latest check outcomes, stale checks and currency.
pub fn status(p: &Project) -> Result<Value> {
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
    Ok(json!({
        "state": health_state(&st),
        "blocks": st["blocks"],
        "failing_checks": failing,
        "stale_checks": stale,
        "governance_suite_currency": cur.to_value(),
        "last_result": st["last_result"],
        "updated_at": st["updated_at"],
        "product_tests": crate::verification::product::status(p, Some(&snap)),
    }))
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
    crate::verification::audit_with(p, &o)
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

    #[test]
    fn blocks_are_derived_from_declared_rules_and_scoped() {
        let mut checks = Map::new();
        checks.insert("D011".into(), json!({"surface": "doctor", "blocking_findings": [{"severity": "critical", "message": "secret"}], "result": "HR-1", "at": "t", "key": "k"}));
        checks.insert("product_test_health".into(), json!({"surface": "family", "blocking_findings": [{"severity": "high", "message": "unit failed", "covers": ["src/**"]}], "result": "HR-2", "at": "t", "key": "k2"}));
        checks.insert("index_freshness".into(), json!({"surface": "family", "blocking_findings": [], "result": "HR-2", "at": "t", "key": "k3"}));
        let blocks = derive_blocks(&checks);
        assert!(blocks
            .iter()
            .any(|b| b["check"] == "D011" && block_applies(b, "task.create", &[])));
        let close_block = blocks
            .iter()
            .find(|b| b["check"] == "product_test_health" && b["scope"] == "covered-paths")
            .unwrap();
        assert!(block_applies(
            close_block,
            "task.close",
            &["src/lib.rs".into()]
        ));
        assert!(!block_applies(
            close_block,
            "task.close",
            &["docs/x.md".into()]
        ));
        assert!(!blocks.iter().any(|b| b["check"] == "index_freshness"));
        let st = json!({"checks": checks, "blocks": blocks});
        assert_eq!(health_state(&st), "RED");
    }
}
