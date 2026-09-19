//! Dynamic task DAG (framework §41-44): runnable/blocked sets, longest chain, cycles, human-gate dependencies, replan.
//!
//! Task-contract fields that order or gate work (Contract v3:563-566, BC-P2-14):
//! * `dependencies` and `blocks` are both ordering edges — `A.blocks = [B]` means B waits for A exactly as if
//!   `B.dependencies` contained A (cycles and the longest chain see both);
//! * `required_data`, `required_tools` and `required_skills` gate readiness: a task whose required input does not
//!   resolve ([`InputResolver`]) is blocked, with the reason, until it does.
//!
//! ## Runnable is derived from the DAG, never asserted (BC-P2-16, BC-P2-12; Contract v3:392, :522, :587, :1101)
//!
//! A task is **runnable** — offered by `gov continue`, claimable (`tasks::claim`), stored READY (`task create`,
//! `task status READY`, `task replan`) — only when [`evaluate`] finds no blocking reason. One evaluation serves every
//! route, so the routes cannot disagree:
//!
//! 1. **ordering** — every `dependencies` entry is DONE and every task whose `blocks` names it is DONE;
//! 2. **required data / tools / skills** resolve ([`InputResolver`]);
//! 3. **mandatory inputs** — the task-input manifest (`context::manifest`, Contract v3 W3) is satisfied: an absent,
//!    superseded, conflicting, non-current or constraint-violating mandatory input blocks. A task that produces its
//!    feature's specification ([`produces_feature_specification`]) is not blocked by inputs it only inherits from the
//!    feature — those are what it is writing;
//! 4. **Human Decision Gates** — every gate governing the task authorises the work
//!    (`gates::task_gate_authorisation_in`, the single gate decision): the gate the task record names in
//!    `human_gate`, and the latest OS-written (T2-verified) gate whose `blocks_tasks` names the task, so removing the
//!    field from a task record does not release the task. PENDING waits (WAITING_HUMAN); DECLINED, WITHDRAWN,
//!    MISSING and UNVERIFIED block;
//! 5. **readiness policy** — pre-implementation cells, read through the precedence-enforced project policy;
//! 6. **TEST_POLICY** — scenarios and acceptance tests declared; a test of an independence family
//!    (`independent_test_author_required_for`) counts as independent only when its authorship is **recorded**
//!    (the sealed close report that produced its current content, `tasks::AuthorshipIndex`) and the recorded author
//!    is neither the implementer's designated role nor the session holding the implementation claim — never because
//!    the artefact says so (`independent_of_implementer` is a claim, BC-P2-34); test data a test relies on must not be
//!    authored by the implementer (recorded, or declared by the data record itself);
//! 7. no re-test pending after CIT propagation;
//! 8. not DRAFT, and not held in BLOCKED / WAITING_HUMAN by an explicit `gov task status` (an explicit hold is
//!    released only by an explicit `gov task status <id> READY`, which is itself checked against this evaluation).
use crate::orchestration::gates::{self, GateAuthorisation};
use crate::orchestration::{claims, readiness, tasks};
use crate::records::{save_record, Record, RecordStore};
use crate::util::{now_iso, today};
use crate::{Project, Result};
use serde_json::{json, Value};
use std::cell::{OnceCell, RefCell};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Clone, serde::Serialize)]
pub struct DagView {
    pub runnable: Vec<String>,
    pub blocked: Vec<Value>,
    pub waiting_human: Vec<Value>,
    pub done: Vec<String>,
    pub longest_chain: Vec<String>,
    pub cycles: Vec<Vec<String>>,
    pub per_feature: Value,
    pub human_gate_dependencies: Vec<Value>,
    pub counts: Value,
    pub missing_dependencies: Vec<Value>,
    /// `blocks` entries naming a task that does not exist.
    pub dangling_blocks: Vec<Value>,
}

/// Lifecycle statuses that make a governed record unavailable as a current input (AUTHORITY_POLICY
/// `retrieval_default_excludes_statuses`).
fn excluded_statuses(p: &Project) -> Vec<String> {
    let v = p
        .policies()
        .get_list("AUTHORITY_POLICY", "retrieval_default_excludes_statuses");
    if v.is_empty() {
        ["SUPERSEDED", "HISTORICAL", "REJECTED", "RETIRED", "LEGACY"]
            .iter()
            .map(|s| s.to_string())
            .collect()
    } else {
        v
    }
}

/// Resolves a task's required inputs (Contract v3:564 "scenarios/data", :566 "required skills/tools"). Registries
/// are read once per resolver and only when a task needs them.
pub struct InputResolver<'a> {
    p: &'a Project,
    store: &'a RecordStore,
    excluded: Vec<String>,
    registry: OnceCell<BTreeMap<String, String>>,
    plugins: OnceCell<BTreeMap<String, String>>,
    skills: OnceCell<Vec<Value>>,
    files: OnceCell<Vec<String>>,
}

impl<'a> InputResolver<'a> {
    pub fn new(p: &'a Project, store: &'a RecordStore) -> Self {
        InputResolver {
            p,
            store,
            excluded: excluded_statuses(p),
            registry: OnceCell::new(),
            plugins: OnceCell::new(),
            skills: OnceCell::new(),
            files: OnceCell::new(),
        }
    }
    /// A governed record (any type; typically `data`) in a current lifecycle status, or a repository path / glob
    /// that exists. `Err` carries the reason it is unavailable.
    pub fn data(&self, d: &str) -> std::result::Result<Value, String> {
        if crate::records::id_regex().is_match(d) {
            if let Some(r) = self.store.get(d) {
                let st = r.status();
                if self.excluded.contains(&st) {
                    return Err(format!("required data {d} is {st} (not a current input)"));
                }
                return Ok(json!({"id": d, "resolved": "record", "path": r.path, "status": st}));
            }
        }
        if std::path::Path::new(d).components().any(|c| {
            !matches!(
                c,
                std::path::Component::Normal(_) | std::path::Component::CurDir
            )
        }) {
            return Err(format!(
                "required data {d} is neither a governed record nor a path inside the repository"
            ));
        }
        if d.contains('*') || d.contains('?') {
            let files = self.files.get_or_init(|| {
                crate::paths::iter_repo_files(&self.p.root, false)
                    .into_iter()
                    .map(|(_, rel)| rel)
                    .collect()
            });
            if let Some(f) = files.iter().find(|f| crate::util::glob_match(d, f)) {
                return Ok(json!({"id": d, "resolved": "path", "path": f}));
            }
        } else if self.p.root.join(d).exists() {
            return Ok(json!({"id": d, "resolved": "path", "path": d}));
        }
        Err(format!(
            "required data {d} is not available (no governed record or repository path)"
        ))
    }
    /// A tool registered in the kernel/project tool registry, the MCP registry or as a capability plugin, and active.
    pub fn tool(&self, t: &str) -> std::result::Result<Value, String> {
        let reg = self.registry.get_or_init(|| {
            let mut m = BTreeMap::new();
            let mut tools = crate::tools::kernel_tools(self.p);
            tools.extend(crate::tools::project_tools(self.p));
            for x in tools {
                if let Some(id) = x["tool_id"].as_str() {
                    m.insert(
                        id.to_string(),
                        x["status"].as_str().unwrap_or("").to_string(),
                    );
                }
            }
            for s in crate::tools::mcp_servers(self.p) {
                if let Some(id) = s["id"].as_str() {
                    m.entry(id.to_string())
                        .or_insert(s["status"].as_str().unwrap_or("").to_string());
                }
            }
            m
        });
        let status = match reg.get(t) {
            Some(s) => Some(s.clone()),
            None => self
                .plugins
                .get_or_init(|| {
                    crate::tools::plugin_tools(self.p)
                        .0
                        .into_iter()
                        .filter_map(|x| {
                            x["tool_id"].as_str().map(|id| {
                                (
                                    id.to_string(),
                                    x["status"].as_str().unwrap_or("").to_string(),
                                )
                            })
                        })
                        .collect()
                })
                .get(t)
                .cloned(),
        };
        match status {
            Some(s) if s == "active" => Ok(json!({"id": t, "status": s})),
            Some(s) => Err(format!("required tool {t} is registered but {s}, not active")),
            None => Err(format!("required tool {t} is not registered (tool registry, MCP registry or capability plugins); raise a tooling task or register it (`gov tools install`)")),
        }
    }
    /// A kernel or project skill, not in a retired lifecycle status.
    pub fn skill(&self, s: &str) -> std::result::Result<Value, String> {
        let skills = self
            .skills
            .get_or_init(|| crate::skills::list_skills(self.p));
        match skills.iter().find(|k| k["id"].as_str() == Some(s)) {
            Some(k) => {
                let st = k["status"].as_str().unwrap_or("ACTIVE").to_uppercase();
                if self.excluded.contains(&st) {
                    Err(format!("required skill {s} is {st}"))
                } else {
                    Ok(json!({"id": s, "version": k["version"], "source": k["_source"]}))
                }
            }
            None => Err(format!("required skill {s} is not registered (capability gap: `gov skills resolve <task>`)")),
        }
    }
    /// Every unavailable required input of `t`, as blocking reasons.
    pub fn gaps(&self, t: &Record) -> Vec<String> {
        let mut out = vec![];
        for d in t.list("required_data") {
            if let Err(e) = self.data(&d) {
                out.push(e);
            }
        }
        for x in t.list("required_tools") {
            if let Err(e) = self.tool(&x) {
                out.push(e);
            }
        }
        for x in t.list("required_skills") {
            if let Err(e) = self.skill(&x) {
                out.push(e);
            }
        }
        out
    }
}

/// Resolution state of each required input of `t` (for presentation, e.g. the context packet).
pub fn required_inputs(p: &Project, store: &RecordStore, t: &Record) -> Value {
    let r = InputResolver::new(p, store);
    let row = |id: &str, res: std::result::Result<Value, String>| match res {
        Ok(v) => json!({"id": id, "available": true, "resolution": v}),
        Err(e) => json!({"id": id, "available": false, "reason": e}),
    };
    json!({
        "required_data": t.list("required_data").iter().map(|d| row(d, r.data(d))).collect::<Vec<_>>(),
        "required_tools": t.list("required_tools").iter().map(|d| row(d, r.tool(d))).collect::<Vec<_>>(),
        "required_skills": t.list("required_skills").iter().map(|d| row(d, r.skill(d))).collect::<Vec<_>>(),
    })
}

/// The DAG state of one task ([`evaluate`]).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TaskState {
    /// DONE or CANCELLED.
    Done,
    /// Nothing blocks it: it may be claimed, stored READY and offered.
    Runnable,
    /// A governing Human Decision Gate is still pending (other reasons may also block it).
    WaitingHuman,
    /// At least one blocking reason.
    Blocked,
}

impl TaskState {
    pub fn as_str(&self) -> &'static str {
        match self {
            TaskState::Done => "DONE",
            TaskState::Runnable => "RUNNABLE",
            TaskState::WaitingHuman => "WAITING_HUMAN",
            TaskState::Blocked => "BLOCKED",
        }
    }
}

/// How one task stands against the DAG: the single decision behind the runnable set, claim, READY and replan.
#[derive(Debug, Clone)]
pub struct TaskEval {
    pub task: String,
    pub state: TaskState,
    /// Every reason the task is not runnable (empty when it is).
    pub reasons: Vec<String>,
    /// Each governing gate with its authorisation (`gates::task_gate_authorisation_in`).
    pub gates: Vec<Value>,
    /// Governing gates still pending (the task waits on them).
    pub pending_gates: Vec<String>,
    /// The mandatory-input manifest verdict, when it blocks.
    pub manifest: Option<Value>,
    /// `dependencies` entries naming no task.
    pub missing_dependencies: Vec<Value>,
}

impl TaskEval {
    pub fn runnable(&self) -> bool {
        self.state == TaskState::Runnable
    }
    pub fn to_value(&self) -> Value {
        json!({"task": self.task, "state": self.state.as_str(), "reasons": self.reasons, "gates": self.gates,
               "pending_gates": self.pending_gates, "manifest": self.manifest})
    }
    /// The typed refusal for a route that requires a runnable task (`TASK_NOT_RUNNABLE`), naming every reason.
    pub fn refusal(&self, action: &str) -> crate::GovError {
        crate::GovError::new(
            "TASK_NOT_RUNNABLE",
            format!(
                "{} cannot be {action}: the task DAG does not allow it ({}): {}. `gov task dag` lists every blocking reason; resolve them (complete dependencies, provide the mandatory inputs, obtain an authorising gate answer, satisfy readiness/TEST_POLICY), then `gov task replan`",
                self.task,
                self.state.as_str(),
                self.reasons.join("; ")
            ),
        )
        .with_details(self.to_value())
    }
}

/// An explicit hold: `gov task status <id> BLOCKED|WAITING_HUMAN` records its source on the task
/// (`status_source`); while the stored status is still the one it set, the task stays held. Derived statuses (replan,
/// create, the readiness planner, gate transitions) carry no such source and are recomputed from the DAG.
pub fn explicit_hold(t: &Record) -> Option<String> {
    let st = t.get("task_status");
    if !matches!(st.as_str(), "BLOCKED" | "WAITING_HUMAN") {
        return None;
    }
    let src = t.data.get("status_source")?;
    if src.get("operation").and_then(|v| v.as_str()) != Some("task status")
        || src.get("status").and_then(|v| v.as_str()) != Some(st.as_str())
    {
        return None;
    }
    let note = t.get("status_note");
    Some(format!(
        "held {st} explicitly by `gov task status` ({} as {}{}); only an explicit `gov task status {} READY` releases it",
        src.get("session").and_then(|v| v.as_str()).unwrap_or("?"),
        src.get("role").and_then(|v| v.as_str()).unwrap_or("?"),
        if note.is_empty() {
            String::new()
        } else {
            format!(": {note}")
        },
        t.id()
    ))
}

/// Task classes whose work is implementation for the independence rules (the implementer side of BC-P2-34).
pub const IMPLEMENTATION_CLASSES: &[&str] =
    &["implementation", "integration", "refactor", "repair"];

/// Task classes that produce a feature's specification (the readiness planner's gap classes and discovery): they do
/// not consume the inputs a feature still lacks.
pub const SPECIFICATION_PRODUCING_CLASSES: &[&str] = &[
    "discovery",
    "research",
    "specification",
    "decision-preparation",
    "data",
    "architecture",
    "test-design",
    "security",
    "performance",
];

/// Does `t` produce its feature's specification (a readiness gap task, or a specification-producing class)? For such a
/// task the inputs it only inherits from its feature are not mandatory inputs (see [`evaluate`], step 3); what it
/// declares itself still binds.
pub fn produces_feature_specification(t: &Record) -> bool {
    !t.get("readiness_cell").is_empty()
        || SPECIFICATION_PRODUCING_CLASSES.contains(&t.get("class").as_str())
}

/// Is `packet` (a compiled context packet of task `t`) BLOCKED **only** by inputs `t` inherits from its feature, while
/// `t` produces that feature's specification ([`produces_feature_specification`])? Then the packet is dispatchable
/// and completable for `t` (the same rule as [`evaluate`] step 3); anything the task declares itself still blocks.
pub fn packet_blocked_only_by_inherited(t: &Record, packet: &Value) -> bool {
    if packet["delivery_state"] == "COMPLETE" || !produces_feature_specification(t) {
        return false;
    }
    let im = &packet["input_manifest"];
    let blocking: Vec<&Value> = ["missing_inputs", "input_violations"]
        .iter()
        .flat_map(|k| im[*k].as_array().into_iter().flatten())
        .collect();
    !blocking.is_empty()
        && blocking.iter().all(|e| {
            e["declared_in"].as_array().map_or(false, |a| {
                !a.is_empty()
                    && a.iter()
                        .all(|s| s.as_str().is_some_and(|s| s.starts_with("feature ")))
            })
        })
}

/// One gate's authorisation, cached per computation.
#[derive(Clone)]
struct GateView {
    auth: GateAuthorisation,
    value: Value,
}

/// Records, gate authorisations, recorded authorship and live claims, read once per DAG computation.
pub struct DagCtx<'a> {
    p: &'a Project,
    store: &'a RecordStore,
    ids: BTreeSet<String>,
    status_of: BTreeMap<String, String>,
    blocked_by: BTreeMap<String, Vec<String>>,
    dangling_blocks: Vec<Value>,
    inputs: InputResolver<'a>,
    enforce_readiness: bool,
    implementation_requires: Vec<String>,
    independent_families: Vec<String>,
    /// task -> the latest OS-written (T2-verified) gate whose `blocks_tasks` names it.
    gate_listing: BTreeMap<String, String>,
    gate_views: RefCell<BTreeMap<String, GateView>>,
    authorship: OnceCell<tasks::AuthorshipIndex>,
    live_claims: OnceCell<Vec<Value>>,
    /// The research/experiment/test-data lifecycle context (WS-10), built once per computation.
    lifecycle: OnceCell<crate::lifecycle::Ctx<'a>>,
}

impl<'a> DagCtx<'a> {
    pub fn new(p: &'a Project, store: &'a RecordStore) -> Self {
        let tasks: Vec<&Record> = store.of_type("task");
        let ids: BTreeSet<String> = tasks.iter().map(|t| t.id()).collect();
        let status_of = tasks
            .iter()
            .map(|t| (t.id(), t.get("task_status")))
            .collect();
        // `A.blocks = [B]` is the edge B -> A: B waits for A
        let mut blocked_by: BTreeMap<String, Vec<String>> = BTreeMap::new();
        let mut dangling_blocks = vec![];
        for t in &tasks {
            for b in t.list("blocks") {
                if ids.contains(&b) {
                    blocked_by.entry(b).or_default().push(t.id());
                } else {
                    dangling_blocks.push(json!({"task": t.id(), "blocks": b}));
                }
            }
        }
        // gates bind the tasks they block by their own OS-written record, not only by the task's `human_gate` field
        let mut listing: BTreeMap<String, (String, String)> = BTreeMap::new();
        for g in store.of_type("human-gate") {
            let listed = g.list("blocks_tasks");
            if listed.is_empty() || !crate::t2::verify_record(g).is_verified() {
                continue;
            }
            let at = g.data["raised_by"]["at"].as_str().unwrap_or("").to_string();
            for t in listed {
                let key = (at.clone(), g.id());
                match listing.get(&t) {
                    Some(cur) if *cur >= key => {}
                    _ => {
                        listing.insert(t, key);
                    }
                }
            }
        }
        let enforce_readiness = p
            .project_policy()
            .get("readiness")
            .and_then(|r| r.get("enforce_pre_implementation_cells"))
            .and_then(|v| v.as_bool())
            .unwrap_or(true);
        let pol = p.policies();
        DagCtx {
            p,
            store,
            ids,
            status_of,
            blocked_by,
            dangling_blocks,
            inputs: InputResolver::new(p, store),
            enforce_readiness,
            implementation_requires: pol.get_list("TEST_POLICY", "implementation_task_requires"),
            independent_families: pol
                .get_list("TEST_POLICY", "independent_test_author_required_for"),
            gate_listing: listing.into_iter().map(|(t, (_, g))| (t, g)).collect(),
            gate_views: RefCell::new(BTreeMap::new()),
            authorship: OnceCell::new(),
            live_claims: OnceCell::new(),
            lifecycle: OnceCell::new(),
        }
    }

    /// The lifecycle context of the scenario → data → test-data chain (`lifecycle::scenario`).
    pub fn lifecycle(&self) -> &crate::lifecycle::Ctx<'a> {
        self.lifecycle
            .get_or_init(|| crate::lifecycle::Ctx::new(self.p, self.store))
    }

    /// Why implementation task `t` may not start on its feature's scenario chain (WS-10 IP-WS10-12; Contract v3 H3
    /// "Production implementation does not become READY before required prerequisite cells satisfy policy", H4
    /// FEATURE → SCENARIOS → DATA → TEST DATA → SUCCESS/FAILURE → INDEPENDENT TESTS): each pre-implementation gap of
    /// the chain (`lifecycle::scenario::implementation_blockers`), except gaps of a readiness cell the feature states
    /// not applicable with a reason (`N/A_WITH_REASON` is explicit, never silent).
    pub fn chain_blockers(&self, t: &Record) -> Vec<String> {
        if !IMPLEMENTATION_CLASSES.contains(&t.get("class").as_str()) || t.get("feature").is_empty()
        {
            return vec![];
        }
        let not_applicable: Vec<String> = self
            .store
            .get(&t.get("feature"))
            .filter(|f| f.rtype() == "feature")
            .map(|f| readiness::not_applicable_cells(f))
            .unwrap_or_default();
        crate::lifecycle::scenario::implementation_blockers(self.lifecycle(), t)
            .into_iter()
            .filter(|g| {
                let code = g.split(':').next().unwrap_or("");
                !readiness::chain_cell_of(code)
                    .map(|c| not_applicable.iter().any(|n| n == c))
                    .unwrap_or(false)
            })
            .collect()
    }

    fn gate_view(&self, gate: &str) -> GateView {
        if let Some(v) = self.gate_views.borrow().get(gate) {
            return v.clone();
        }
        let auth = gates::task_gate_authorisation_in(self.p, self.store, gate);
        let status = self
            .store
            .get(gate)
            .map(|g| g.get("gate_status"))
            .unwrap_or_else(|| "MISSING".into());
        let value = json!({"gate": gate, "gate_status": status, "authorisation": auth.to_value()});
        let v = GateView { auth, value };
        self.gate_views
            .borrow_mut()
            .insert(gate.to_string(), v.clone());
        v
    }

    /// The gates governing `t`: the gate its record names in `human_gate`, and the latest T2-verified gate whose
    /// `blocks_tasks` names it.
    pub fn governing_gates(&self, t: &Record) -> Vec<String> {
        let mut out = vec![];
        let named = t.get("human_gate");
        if !named.is_empty() {
            out.push(named);
        }
        if let Some(g) = self.gate_listing.get(&t.id()) {
            if !out.contains(g) {
                out.push(g.clone());
            }
        }
        out
    }

    pub fn authorship(&self) -> &tasks::AuthorshipIndex {
        self.authorship
            .get_or_init(|| tasks::AuthorshipIndex::build(self.p, self.store))
    }

    fn live_claims(&self) -> &Vec<Value> {
        self.live_claims
            .get_or_init(|| claims::live(self.p).unwrap_or_default())
    }

    /// The session holding a live claim on `task`, if any.
    pub fn claim_session(&self, task: &str) -> Option<String> {
        self.live_claims()
            .iter()
            .find(|c| c["task_id"].as_str() == Some(task))
            .and_then(|c| c["session_id"].as_str().map(|s| s.to_string()))
    }

    /// The acceptance tests a task relies on: its own and its feature's declared tests, and every test obligation
    /// recorded against the feature.
    pub fn declared_tests(&self, t: &Record) -> Vec<String> {
        let feature = self
            .store
            .get(&t.get("feature"))
            .filter(|f| f.rtype() == "feature");
        let mut v = t.list("acceptance_tests");
        if let Some(f) = feature {
            v.extend(f.list("acceptance_tests"));
            v.extend(
                self.store
                    .of_type("test-obligation")
                    .iter()
                    .filter(|o| o.get("feature") == f.id())
                    .map(|o| o.id()),
            );
        }
        let mut seen = BTreeSet::new();
        v.retain(|x| seen.insert(x.clone()));
        v
    }

    /// Why obligation `o` is not independent of the implementer of `t` (BC-P2-34), or `None` when it is. Independence
    /// is taken from the **recorded** author of the obligation's current content — the sealed close report that
    /// produced it — compared with the implementer's designated role, the session holding the implementation claim
    /// (`session`, or the live claim) and the implementation task itself.
    pub fn obligation_dependence(
        &self,
        o: &Record,
        t: &Record,
        session: Option<&str>,
    ) -> Option<String> {
        let Some(a) = self.authorship().author_of(self.p, &o.path) else {
            return Some(format!("{} ({}) must be authored independently of the implementer (TEST_POLICY.independent_test_author_required_for), and its independence is not established from recorded authorship: no sealed close report produced its current content. `independent_of_implementer` / `author_role` are the artefact's own claims, not evidence; produce it through a test-design task closed by an independent role and session", o.id(), o.get("family")));
        };
        let designated = t.get("role");
        let claim = self.claim_session(&t.id());
        let sessions: Vec<String> = session
            .map(|s| s.to_string())
            .into_iter()
            .chain(claim)
            .collect();
        if a.task == t.id() {
            return Some(format!(
                "{} was produced by {} itself ({}), not independently of it",
                o.id(),
                t.id(),
                a.report
            ));
        }
        if !designated.is_empty() && a.role == designated {
            return Some(format!("{} was authored in role '{}' ({} closing {}), the implementer's designated role: tests of the independence families must come from another role", o.id(), a.role, a.report, a.task));
        }
        if sessions.contains(&a.session) {
            return Some(format!("{} was authored by session {} ({} closing {}), the session implementing {}: independence requires a different author session", o.id(), a.session, a.report, a.task, t.id()));
        }
        None
    }

    /// Why a test dataset `d` that obligation `o` relies on is not independent of the implementer of `t`, or `None`.
    /// Dependence is established by the recorded author (sealed close report) or declared by the data record itself
    /// (`author_role`, `author_session`): a record that states it was authored by the implementer is believed.
    pub fn data_dependence(
        &self,
        d: &Record,
        o: &Record,
        t: &Record,
        session: Option<&str>,
    ) -> Option<String> {
        let designated = t.get("role");
        let mut sessions: Vec<String> = session.map(|s| s.to_string()).into_iter().collect();
        sessions.extend(self.claim_session(&t.id()));
        if let Some(a) = self.authorship().author_of(self.p, &d.path) {
            if (!designated.is_empty() && a.role == designated) || sessions.contains(&a.session) {
                return Some(format!("test data {} (used by {}) was authored by the implementer ({} as '{}', {}): test-data authorship must be independent of the implementation (Contract v3 H4)", d.id(), o.id(), a.session, a.role, a.report));
            }
        }
        let declared_role = d.get("author_role");
        let declared_session = d.get("author_session");
        if (!designated.is_empty() && declared_role == designated)
            || (!declared_session.is_empty() && sessions.contains(&declared_session))
        {
            return Some(format!("test data {} (used by {}) declares itself authored by the implementer (author_role '{}'{}): test-data authorship must be independent of the implementation (Contract v3 H4)", d.id(), o.id(), declared_role, if declared_session.is_empty() { String::new() } else { format!(", session {declared_session}") }));
        }
        None
    }

    /// The test datasets obligation `o` relies on: ids named in `test_data` / `datasets` / `data_provenance` that
    /// resolve to `data` records.
    pub fn test_data_of(&self, o: &Record) -> Vec<&'a Record> {
        let mut texts: Vec<String> = vec![];
        for k in ["test_data", "datasets", "data_provenance", "dataset"] {
            match o.data.get(k) {
                Some(Value::String(s)) => texts.push(s.clone()),
                Some(Value::Array(a)) => {
                    texts.extend(a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())))
                }
                _ => {}
            }
        }
        let rx = crate::records::id_regex();
        let mut out: Vec<&Record> = vec![];
        for text in texts {
            for tok in text.split(|c: char| !(c.is_ascii_alphanumeric() || "._-".contains(c))) {
                let tok = tok.trim_end_matches(['.', '-', '_']);
                if !rx.is_match(tok) {
                    continue;
                }
                if let Some(d) = self.store.get(tok).filter(|d| d.rtype() == "data") {
                    if !out.iter().any(|x| x.id() == d.id()) {
                        out.push(d);
                    }
                }
            }
        }
        out
    }

    /// The independence reasons for implementation task `t` acted on by `session` (claim/close) — or, with `None`,
    /// by whoever holds its claim (the DAG view).
    pub fn independence_reasons(&self, t: &Record, session: Option<&str>) -> Vec<String> {
        let mut out = vec![];
        if !IMPLEMENTATION_CLASSES.contains(&t.get("class").as_str()) {
            return out;
        }
        for tid in self.declared_tests(t) {
            let Some(o) = self
                .store
                .get(&tid)
                .filter(|o| o.rtype() == "test-obligation")
            else {
                continue;
            };
            if !self.independent_families.contains(&o.get("family")) {
                continue;
            }
            if let Some(r) = self.obligation_dependence(o, t, session) {
                out.push(r);
            }
            for d in self.test_data_of(o) {
                if let Some(r) = self.data_dependence(d, o, t, session) {
                    out.push(r);
                }
            }
        }
        out
    }
}

/// Evaluate task `t` against the DAG. `as_status` evaluates it as if its stored status were that value (the READY
/// routes ask "would it be runnable if READY?", so DRAFT and an explicit hold are not reasons there).
pub fn evaluate(ctx: &DagCtx, t: &Record, as_status: Option<&str>) -> TaskEval {
    let id = t.id();
    let st = as_status
        .map(|s| s.to_string())
        .unwrap_or_else(|| t.get("task_status"));
    let mut ev = TaskEval {
        task: id.clone(),
        state: TaskState::Runnable,
        reasons: vec![],
        gates: vec![],
        pending_gates: vec![],
        manifest: None,
        missing_dependencies: vec![],
    };
    if st == "DONE" || st == "CANCELLED" {
        ev.state = TaskState::Done;
        return ev;
    }
    let reasons = &mut ev.reasons;
    // 1. ordering
    for d in t.list("dependencies") {
        match ctx.status_of.get(&d) {
            Some(s) if s == "DONE" => {}
            Some(s) => reasons.push(format!("dependency {d} is {s}")),
            None => {
                if ctx.ids.contains(&d) {
                    reasons.push(format!("dependency {d} unknown status"));
                } else {
                    ev.missing_dependencies
                        .push(json!({"task": id, "dependency": d}));
                    reasons.push(format!("dependency {d} missing"));
                }
            }
        }
    }
    for b in ctx.blocked_by.get(&id).cloned().unwrap_or_default() {
        let s = ctx.status_of.get(&b).cloned().unwrap_or_default();
        if s != "DONE" {
            reasons.push(format!(
                "blocked by {b} (its `blocks` lists {id}); {b} is {s}"
            ));
        }
    }
    // 2. required data / tools / skills
    reasons.extend(ctx.inputs.gaps(t));
    // 3. mandatory task-input manifest (W3). A task that produces its feature's specification does not consume the
    //    parts of it the feature still lacks: inputs it only inherits from the feature bind consumers of that
    //    specification (implementation work), not the work that writes it — otherwise readiness planning would
    //    generate work that can never start
    let m = crate::context::manifest::resolve(ctx.p, ctx.store, t);
    let producer = produces_feature_specification(t);
    let unsatisfied: Vec<&crate::context::manifest::Entry> = m
        .entries
        .iter()
        .filter(|e| e.required && !e.satisfied())
        .filter(|e| !(producer && e.sources.iter().all(|s| s.starts_with("feature "))))
        .collect();
    if !unsatisfied.is_empty() {
        let items: Vec<String> = unsatisfied
            .iter()
            .map(|e| {
                let codes: Vec<&str> = if e.delivered() {
                    e.problems
                        .iter()
                        .filter(|p| p.blocking)
                        .map(|p| p.code)
                        .collect()
                } else {
                    vec![e.resolution]
                };
                format!("{} ({}: {})", e.id, e.slot.name(), codes.join(","))
            })
            .collect();
        reasons.push(format!(
            "mandatory inputs unsatisfied: {}",
            items.join("; ")
        ));
        ev.manifest = Some(
            json!({"delivery_state": m.delivery_state(), "missing_inputs": m.missing(), "input_violations": m.violations(),
                   "blocking": unsatisfied.iter().map(|e| e.id.clone()).collect::<Vec<_>>()}),
        );
    }
    // 4. Human Decision Gates (BC-P2-12)
    for g in ctx.governing_gates(t) {
        let v = ctx.gate_view(&g);
        match &v.auth {
            GateAuthorisation::Authorised { .. } => {}
            GateAuthorisation::Pending { .. } => ev.pending_gates.push(g.clone()),
            other => {
                if let Some(r) = other.blocking_reason(&g) {
                    reasons.push(r);
                }
            }
        }
        ev.gates.push(v.value);
    }
    // 5. readiness policy: the pre-implementation cells — those the scenario chain determines computed from it, not
    //    asserted (IP-WS10-12) — and the chain's own pre-implementation gaps for the scenarios this work implements
    if ctx.enforce_readiness && t.get("class") == "implementation" && !t.get("feature").is_empty() {
        if let Some(f) = ctx.store.get(&t.get("feature")) {
            let r = readiness::evaluate_in(ctx.p, ctx.lifecycle(), f);
            if !r.pre_implementation_ok {
                reasons.push(format!(
                    "feature {} pre-implementation readiness cells missing: {}",
                    f.id(),
                    r.pre_implementation_gaps.join(", ")
                ));
            }
        }
    }
    if ctx.enforce_readiness {
        let chain = ctx.chain_blockers(t);
        if !chain.is_empty() {
            reasons.push(format!(
                "scenario chain not ready for implementation (Contract v3 H3/H4; `gov scenario trace`): {}",
                chain.join("; ")
            ));
        }
    }
    // 6. TEST_POLICY
    if t.get("class") == "implementation" {
        let feature = ctx
            .store
            .get(&t.get("feature"))
            .filter(|f| f.rtype() == "feature");
        let has_scn = !t.list("scenarios").is_empty()
            || feature
                .map(|f| !f.list("scenarios").is_empty())
                .unwrap_or(false);
        let declared_tests = ctx.declared_tests(t);
        for req in &ctx.implementation_requires {
            match req.as_str() {
                "scenarios_present" if !has_scn => {
                    reasons.push("TEST_POLICY.implementation_task_requires: no scenarios declared on the task or its feature".into());
                }
                "acceptance_tests_declared" if declared_tests.is_empty() => {
                    reasons.push("TEST_POLICY.implementation_task_requires: no acceptance tests declared on the task or its feature".into());
                }
                _ => {}
            }
        }
    }
    reasons.extend(ctx.independence_reasons(t, None));
    // 7. re-test after an upstream change (CIT propagation, or a direct change propagated when detected)
    if t.data
        .get("retest_required")
        .and_then(|v| v.as_bool())
        .unwrap_or(false)
    {
        let why = t.get("retest_reason");
        reasons.push(format!(
            "retest required after upstream change propagation{}: work that has not started re-delivers its context at the current inputs (`gov context compile {id}`); started work closes only with re-test evidence against the changed inputs",
            if why.is_empty() { String::new() } else { format!(" ({why})") }
        ));
    }
    // 7a. inputs changed since this task's work consumed them and not yet propagated (BC-P2-04; WS-4 R2-2): content
    //     against what the delivered packet / checkpoint recorded — never index freshness
    if !matches!(st.as_str(), "DONE" | "CANCELLED") {
        let (baseline, stale) = crate::cit::propagation::stale_inputs(ctx.p, ctx.store, t);
        let fresh: Vec<String> = stale
            .iter()
            .filter(|(_, propagated)| !propagated)
            .map(|(c, _)| c.id.clone())
            .collect();
        if !fresh.is_empty() {
            reasons.push(format!(
                "input(s) {} changed since this task's work consumed them ({}), outside change control: an upstream change reaches its dependents (`gov cit propagate`), and a context compiled now (`gov context compile {id}`) delivers the current versions",
                fresh.join(", "),
                baseline.map(|b| b.source).unwrap_or_default()
            ));
        }
    }
    // 8. DRAFT and explicit holds (not when asked "as READY")
    if as_status.is_none() {
        if let Some(h) = explicit_hold(t) {
            reasons.push(h);
        } else if st == "DRAFT" && reasons.is_empty() {
            reasons.push(format!("DRAFT: promote with `gov task status {id} READY`"));
        }
    }
    ev.state = if !ev.pending_gates.is_empty() {
        TaskState::WaitingHuman
    } else if ev.reasons.is_empty() {
        TaskState::Runnable
    } else {
        TaskState::Blocked
    };
    if !ev.pending_gates.is_empty() {
        let pending = ev.pending_gates.join(", ");
        ev.reasons
            .insert(0, format!("waiting on human gate {pending}"));
    }
    ev
}

/// Evaluate one task by id (the claim / READY routes). `None` when `id` is not a task.
pub fn task_eval(
    p: &Project,
    store: &RecordStore,
    id: &str,
    as_status: Option<&str>,
) -> Option<TaskEval> {
    let t = store.get(id).filter(|t| t.rtype() == "task")?;
    let ctx = DagCtx::new(p, store);
    Some(evaluate(&ctx, t, as_status))
}

pub fn compute(p: &Project) -> Result<DagView> {
    let store = RecordStore::load(&p.root);
    let ctx = DagCtx::new(p, &store);
    let tasks: Vec<&crate::records::Record> = store.of_type("task");
    let mut runnable = vec![];
    let mut blocked = vec![];
    let mut waiting = vec![];
    let mut done = vec![];
    let mut missing = vec![];
    let mut gate_deps = vec![];
    let mut per_feature: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for t in &tasks {
        let id = t.id();
        per_feature
            .entry(t.get("feature"))
            .or_default()
            .push(id.clone());
        let ev = evaluate(&ctx, t, None);
        missing.extend(ev.missing_dependencies.iter().cloned());
        for g in &ev.gates {
            gate_deps.push(json!({"task": id, "gate": g["gate"], "gate_status": g["gate_status"], "authorisation": g["authorisation"]}));
        }
        match ev.state {
            TaskState::Done => done.push(id),
            TaskState::Runnable => runnable.push(id),
            TaskState::WaitingHuman => waiting.push(json!({"task": id, "gate": ev.pending_gates.first(), "gates": ev.pending_gates, "reasons": ev.reasons})),
            TaskState::Blocked => blocked.push(json!({"task": id, "reasons": ev.reasons})),
        }
    }
    // cycles + longest chain over open tasks
    let open: BTreeSet<String> = tasks
        .iter()
        .filter(|t| !matches!(t.get("task_status").as_str(), "DONE" | "CANCELLED"))
        .map(|t| t.id())
        .collect();
    let deps: BTreeMap<String, Vec<String>> = tasks
        .iter()
        .map(|t| {
            let mut d: Vec<String> = t
                .list("dependencies")
                .into_iter()
                .chain(ctx.blocked_by.get(&t.id()).cloned().unwrap_or_default())
                .filter(|d| open.contains(d))
                .collect();
            d.sort();
            d.dedup();
            (t.id(), d)
        })
        .collect();
    let mut cycles = vec![];
    let mut color: BTreeMap<String, u8> = BTreeMap::new();
    fn dfs(
        n: &str,
        deps: &BTreeMap<String, Vec<String>>,
        color: &mut BTreeMap<String, u8>,
        stack: &mut Vec<String>,
        cycles: &mut Vec<Vec<String>>,
    ) {
        color.insert(n.to_string(), 1);
        stack.push(n.to_string());
        for d in deps.get(n).cloned().unwrap_or_default() {
            match color.get(&d).copied().unwrap_or(0) {
                0 => dfs(&d, deps, color, stack, cycles),
                1 => {
                    let pos = stack.iter().position(|x| x == &d).unwrap_or(0);
                    cycles.push(stack[pos..].to_vec());
                }
                _ => {}
            }
        }
        stack.pop();
        color.insert(n.to_string(), 2);
    }
    for n in &open {
        if color.get(n).copied().unwrap_or(0) == 0 {
            let mut st = vec![];
            dfs(n, &deps, &mut color, &mut st, &mut cycles);
        }
    }
    let mut memo: BTreeMap<String, Vec<String>> = BTreeMap::new();
    fn longest(
        n: &str,
        deps: &BTreeMap<String, Vec<String>>,
        memo: &mut BTreeMap<String, Vec<String>>,
        depth: usize,
    ) -> Vec<String> {
        if let Some(v) = memo.get(n) {
            return v.clone();
        }
        if depth > 500 {
            return vec![n.to_string()];
        }
        let mut best: Vec<String> = vec![];
        for d in deps.get(n).cloned().unwrap_or_default() {
            let c = longest(&d, deps, memo, depth + 1);
            if c.len() > best.len() {
                best = c;
            }
        }
        let mut out = best;
        out.push(n.to_string());
        memo.insert(n.to_string(), out.clone());
        out
    }
    let mut longest_chain: Vec<String> = vec![];
    if cycles.is_empty() {
        for n in &open {
            let c = longest(n, &deps, &mut memo, 0);
            if c.len() > longest_chain.len() {
                longest_chain = c;
            }
        }
    }
    let counts = json!({"total": tasks.len(), "runnable": runnable.len(), "blocked": blocked.len(), "waiting_human": waiting.len(), "done": done.len(), "open": open.len()});
    let pf: Value = json!(per_feature);
    Ok(DagView {
        runnable,
        blocked,
        waiting_human: waiting,
        done,
        longest_chain,
        cycles,
        per_feature: pf,
        human_gate_dependencies: gate_deps,
        counts,
        missing_dependencies: missing,
        dangling_blocks: ctx.dangling_blocks.clone(),
    })
}

/// Recompute and persist READY/BLOCKED/WAITING_HUMAN for open tasks whose status is derived: DRAFT, claimed or
/// in-flight work (CLAIMED/IN_PROGRESS/REVIEW) and explicit holds are left as they are. A task becomes READY here only
/// when [`evaluate`] finds it runnable (mandatory inputs, gates and every other reason included).
pub fn replan(p: &Project) -> Result<Value> {
    crate::orchestration::control::guard_write(p, "replan")?;
    // work the recorded events call for joins the DAG before it is replanned (BC-P2-24)
    let generated = crate::orchestration::generation::reconcile(
        p,
        &crate::orchestration::generation::Options::triggered_by("replan"),
    )
    .map(|r| crate::orchestration::generation::summary(&r))
    .unwrap_or_else(|e| json!({"error": {"code": e.code, "message": e.message}}));
    let view = compute(p)?;
    let mut store = RecordStore::load(&p.root);
    let mut changed = vec![];
    let blocked_ids: BTreeSet<String> = view
        .blocked
        .iter()
        .filter_map(|b| b["task"].as_str().map(|s| s.to_string()))
        .collect();
    let waiting_ids: BTreeSet<String> = view
        .waiting_human
        .iter()
        .filter_map(|b| b["task"].as_str().map(|s| s.to_string()))
        .collect();
    let ids: Vec<String> = store.of_type("task").iter().map(|t| t.id()).collect();
    for id in ids {
        let rec = store.get_mut(&id).unwrap();
        let st = rec.get("task_status");
        let target = if view.runnable.contains(&id) {
            "READY"
        } else if waiting_ids.contains(&id) {
            "WAITING_HUMAN"
        } else if blocked_ids.contains(&id) && st != "DRAFT" {
            "BLOCKED"
        } else {
            continue;
        };
        if matches!(
            st.as_str(),
            "DONE" | "CANCELLED" | "IN_PROGRESS" | "CLAIMED" | "REVIEW"
        ) || explicit_hold(rec).is_some()
        {
            continue;
        }
        if st != target {
            rec.set("task_status", json!(target));
            rec.set("updated", json!(today()));
            rec.set(
                "status_source",
                json!({"operation": "replan", "status": target, "session": p.session_id, "role": p.role, "at": now_iso()}),
            );
            save_record(&p.root, rec)?;
            changed.push(json!({"task": id, "from": st, "to": target}));
        }
    }
    Ok(
        json!({"changed": changed, "runnable": view.runnable, "blocked": view.blocked.len(), "waiting_human": view.waiting_human.len(), "cycles": view.cycles, "generated_work": generated}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::records::new_record;

    fn task(status: &str, source: Value) -> Record {
        let mut f = json!({"class": "documentation", "task_status": status, "objective": "o"});
        if !source.is_null() {
            f["status_source"] = source;
        }
        new_record("task", "TASK-0001", "t", f)
    }

    /// Only a BLOCKED / WAITING_HUMAN set by `gov task status` — and still the stored status — is an explicit hold;
    /// derived statuses (replan, create, the planner, gate transitions) are recomputed from the DAG.
    #[test]
    fn explicit_hold_is_only_a_status_set_by_task_status_and_still_in_force() {
        let by_status =
            |s: &str| json!({"operation": "task status", "status": s, "session": "S", "role": "r"});
        assert!(explicit_hold(&task("BLOCKED", by_status("BLOCKED"))).is_some());
        assert!(explicit_hold(&task("WAITING_HUMAN", by_status("WAITING_HUMAN"))).is_some());
        // derived by replan or create: recomputed
        assert!(explicit_hold(&task(
            "BLOCKED",
            json!({"operation": "replan", "status": "BLOCKED"})
        ))
        .is_none());
        assert!(explicit_hold(&task("BLOCKED", Value::Null)).is_none());
        // the status moved on since the hold (e.g. a gate transition rewrote it): no longer a hold
        assert!(explicit_hold(&task("BLOCKED", by_status("READY"))).is_none());
        // READY / DRAFT set by `task status` are not holds
        assert!(explicit_hold(&task("READY", by_status("READY"))).is_none());
        assert!(explicit_hold(&task("DRAFT", by_status("DRAFT"))).is_none());
    }

    #[test]
    fn task_state_names_are_stable() {
        for (s, n) in [
            (TaskState::Done, "DONE"),
            (TaskState::Runnable, "RUNNABLE"),
            (TaskState::WaitingHuman, "WAITING_HUMAN"),
            (TaskState::Blocked, "BLOCKED"),
        ] {
            assert_eq!(s.as_str(), n);
        }
        let ev = TaskEval {
            task: "TASK-0001".into(),
            state: TaskState::Blocked,
            reasons: vec!["dependency TASK-0002 is READY".into()],
            gates: vec![],
            pending_gates: vec![],
            manifest: None,
            missing_dependencies: vec![],
        };
        let e = ev.refusal("claimed");
        assert_eq!(e.code, "TASK_NOT_RUNNABLE");
        assert!(e.message.contains("TASK-0002"));
        assert_eq!(e.details["state"], "BLOCKED");
    }
}
