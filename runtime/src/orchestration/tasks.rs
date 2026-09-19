//! Task contracts (framework §42), creation, status transitions and evidence-gated close (§13, §64).
//! Every mutating path is authority-checked (AUTHORITY_POLICY.authority_levels_required) and task close enforces the
//! task's contract (Contract v3:560-569):
//!
//! * **runnable is derived** (BC-P2-16) — `task create --status READY`, `task status READY`, `replan`, `claim` and
//!   `gov continue` all ask one question, [`crate::orchestration::dag::evaluate`]: dependencies and `blocks`, required
//!   data/tools/skills, the mandatory task-input manifest, every governing Human Decision Gate, readiness policy,
//!   TEST_POLICY (independence from recorded authorship included), pending re-tests and explicit holds. `DONE`,
//!   `CLAIMED` and `IN_PROGRESS` are reached only through `close` and `claim`;
//! * **claim** (BC-P2-15) — granted atomically to one session with the task's mutation scope and the session's
//!   working tree recorded ([`crate::orchestration::claims`]); the task's designated `role` binds who may claim it;
//!   the claim baseline (the tree snapshot, the CITs already committed, the reports already written and the task
//!   contract as claimed) is sealed with the T2 binding primitive, so a worker cannot rewrite the evidence its close
//!   is checked against;
//! * **close** — only by the session holding the claim, from the working tree it was claimed in, in the designated
//!   role, never while a governing Human Decision Gate withholds authorisation; see [`close`] for the order of its
//!   checks and why;
//! * **path scope** (BC-P2-14) — the mutations observed since the task's claim baseline must be declared and inside
//!   `allowed_paths` / outside `forbidden_paths` (as recorded now and as claimed), unless a Change-Impact Transaction
//!   **executed while the task was claimed** touched that path. A claim baseline is never reset by re-claiming;
//! * **OS-written state** (BC-P2-09, D-0007 T2) — a changed path under an OS-managed location is the OS's own write
//!   only when it can be told apart from a worker's: a record carrying a T2 seal must verify, and a record of a kind
//!   the OS always seals (gates, gate-derived decisions, close reports, and every type `t2::SEALED_RECORD_TYPES`
//!   names) must carry one. Anything else there is observed as the worker's mutation of OS-written state and refused;
//! * **production merge** (BC-P2-14) — a task whose contract forbids production merge (every `experiment` task)
//!   cannot close with mutations in the production tree ([`is_production_path`]); promotion goes through a CIT;
//! * **independence** (BC-P2-34, task-role side) — independence of tests and test data from the implementer is taken
//!   from recorded authorship ([`AuthorshipIndex`]: the sealed close reports), never from what an artefact says about
//!   itself; one session does not both implement a feature and author its independent tests or test data.
//! * **material changes** (BC-P2-13 in-task half) — what a task changed is classified at its close by what changed
//!   (`cit::materiality::classify_paths`), never by the task's label; a material change completes only through
//!   CIT-P/CIT-E (a CIT committed inside the claim window that wrote exactly that content), except the initial
//!   authoring of specification by specification work ([`material_changes`]);
//! * **current inputs** (BC-P2-04 close side) — work done against an input that changed since it was consumed does not
//!   close, and a re-test flag is cleared only by re-test evidence (`cit::propagation::require_current_inputs`); a
//!   claim first propagates changes made outside change control (`detect_and_propagate`), and the DAG shows them;
//! * **work generation** (BC-P2-24) — the events a close records (discoveries, unresolved items, proposed decisions)
//!   generate linked work (`orchestration::generation`); generated work is created by [`create_generated`];
//! * **where claim evidence lives** (BC-P2-31) — claim baselines and carried sets at `paths::store_path(root,
//!   "claim-trees")`, the claims store at `paths::store_path(root, "claims")`, never in the derived runtime directory;
//! * **availability** (round-3 rule) — a hard-block does not refuse creating or claiming the work that remedies it
//!   ([`guard_work`]); every other applicable block refuses, typed, naming the block and its scope.
use crate::authority;
use crate::checkpoints;
use crate::memory::claims::ClaimRequest;
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::orchestration::dag::{self, DagCtx, TaskState, IMPLEMENTATION_CLASSES};
use crate::orchestration::{claims, control, gates};
use crate::records::{new_record, save_record, Record, RecordStore};
use crate::scheduler::{self, catalogue::ops};
use crate::util::{glob_match, now_iso, today};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

pub const STATUSES: &[&str] = &[
    "DRAFT",
    "READY",
    "BLOCKED",
    "CLAIMED",
    "IN_PROGRESS",
    "REVIEW",
    "DONE",
    "CANCELLED",
    "WAITING_HUMAN",
];

/// Statuses a task reaches only through its lifecycle operation, never by `task create` / `task status`: a task is
/// DONE only through an evidence-gated close, and CLAIMED / IN_PROGRESS only through an atomic claim.
pub const OPERATION_ONLY_STATUSES: &[(&str, &str)] = &[
    ("DONE", "gov task close <id> --report <receipt>"),
    ("CLAIMED", "gov task claim <id>"),
    ("IN_PROGRESS", "gov task claim <id>"),
];

fn operation_only(status: &str) -> Option<GovError> {
    OPERATION_ONLY_STATUSES
        .iter()
        .find(|(s, _)| *s == status)
        .map(|(s, route)| {
            GovError::new(
                "TASK_STATUS_REQUIRES_OPERATION",
                format!("task status {s} is reached only through `{route}` (its evidence and claim checks cannot be skipped by setting the status)"),
            )
            .with_details(json!({"status": s, "route": route}))
        })
}

/// The status the DAG derives for a task that is not DONE: READY when runnable, WAITING_HUMAN when a governing gate
/// is pending, BLOCKED otherwise.
fn derived_status(ev: &dag::TaskEval) -> &'static str {
    match ev.state {
        TaskState::Runnable => "READY",
        TaskState::WaitingHuman => "WAITING_HUMAN",
        TaskState::Blocked => "BLOCKED",
        TaskState::Done => "DONE",
    }
}

// ------------------------------------------------------------------------------------------------ availability

/// The health checks a task declares it remedies: its contract field `remedies` (check ids of the health scheduler
/// catalogue — the work generator sets it on the remediation work it generates for a failing check; a creator may
/// declare it on work it opens to repair a block).
pub fn remedies_of(t: &Value) -> Vec<String> {
    t.get("remedies")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.trim().to_string()))
                .filter(|s| !s.is_empty())
                .collect()
        })
        .unwrap_or_default()
}

/// **G0 at a work operation, under the availability rule** (round-3 common protocol, from Contract v3 L4
/// "Independent runnable branches continue. Global stop only when policy or critical-path state requires" and O5
/// "hard-block vs warning semantics are explicit"). The write guard (kernel trust, break-glass, emergency controls)
/// always runs. The health half is the scheduler's G0 guard with the **paths the operation relies on**, so a
/// path-scoped block governs only the work inside its scope; and a hard-block the work **remedies** (its `remedies`
/// names the blocking check) does not refuse it — work that remedies a block stays available. The remedy still
/// cannot commit without clearing its block: its close passes the same guard, which re-evaluates the block and
/// refuses while it stands. Every refusal is the scheduler's typed `HEALTH_HARD_BLOCK`, naming each block, its check
/// and its scope.
pub fn guard_work(
    p: &Project,
    label: &str,
    op: &str,
    paths: &[String],
    remedies: &[String],
) -> Result<Value> {
    if remedies.is_empty() {
        control::guard_write(p, label)?;
        return scheduler::guard(p, op, paths);
    }
    // the same write guard without its generic (whole-operation) health half, which the scoped decision below owns
    control::guard_write(p, &format!("{label} (remedy)"))?;
    match scheduler::guard(p, op, paths) {
        Ok(v) => Ok(v),
        Err(e) if e.code == "HEALTH_HARD_BLOCK" => {
            let blocks = e.details["blocks"].as_array().cloned().unwrap_or_default();
            let (remedied, standing): (Vec<Value>, Vec<Value>) =
                blocks.into_iter().partition(|b| {
                    remedies
                        .iter()
                        .any(|r| Some(r.as_str()) == b["check"].as_str())
                });
            if standing.is_empty() {
                return Ok(json!({"operation": op, "allowed": true, "availability": {
                    "rule": "a hard-block does not refuse the work that remedies it (round-3 availability rule); the remedy commits only if its close finds the block cleared",
                    "remedies": remedies, "remedied_blocks": remedied}}));
            }
            let first = &standing[0];
            Err(GovError::new(
                "HEALTH_HARD_BLOCK",
                format!(
                    "{op} is refused: {} active hard-block(s) this work does not remedy, e.g. check {} ({}, scope {}): {}. The work remedies {remedies:?}; repair the other condition(s), or remedy them in their own work",
                    standing.len(),
                    first["check"].as_str().unwrap_or("?"),
                    first["severity"].as_str().unwrap_or("?"),
                    first["scope"].as_str().unwrap_or("operation"),
                    first["message"].as_str().unwrap_or("")
                ),
            )
            .with_details(json!({"operation": op, "paths": paths, "blocks": standing, "remedied_blocks": remedied, "remedies": remedies})))
        }
        Err(e) => Err(e),
    }
}

pub fn create(p: &Project, fields: Value) -> Result<Value> {
    // G0 (tier contract, BC-P2-06, IP-WS02-02) under the availability rule: an active hard-block governing task
    // creation refuses it — except for work that remedies that block (`remedies`)
    let remedies = remedies_of(&fields);
    let paths: Vec<String> = fields
        .get("allowed_paths")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let availability = guard_work(p, "task create", ops::TASK_CREATE, &paths, &remedies)?;
    authority::require(p, "create_task")?;
    let producer = json!({"producer": "gov task create", "session": p.session_id, "role": p.role, "created_at": now_iso()});
    let mut out = build_and_save(p, fields, producer, "task create", false)?;
    if availability.get("availability").is_some() {
        out["availability"] = availability["availability"].clone();
    }
    Ok(out)
}

/// **Create work the Governance OS generates from an event** (BC-P2-24; `orchestration::generation`): the same
/// record, defaults, schema and DAG-derived status as [`create`], with the generator's provenance and `generation`
/// block. The write guard applies (kernel trust, break-glass, FREEZE_WRITES / PAUSE: nothing is generated while
/// writes are frozen); the acting role's `create_task` authority and the health hard-block do not — generated work is
/// the OS's reaction to an event, not the caller's request, and remediation stays available under the block it
/// remedies (availability rule; it still commits only by clearing it).
pub fn create_generated(p: &Project, fields: Value, trigger: &str) -> Result<Value> {
    control::guard_write(p, "work generation")?;
    let producer = json!({"producer": crate::orchestration::generation::GENERATOR, "trigger": trigger, "session": p.session_id, "role": p.role, "created_at": now_iso()});
    build_and_save(p, fields, producer, "work generation", true)
}

/// Build, validate and persist a task record: defaults, routing and role checks, OS-owned provenance, the status the
/// DAG derives (READY is never asserted), and the influence backlinks of the evidence it relies on.
fn build_and_save(
    p: &Project,
    mut fields: Value,
    producer: Value,
    operation: &str,
    generated: bool,
) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let id = fields
        .get("id")
        .and_then(|v| v.as_str())
        .filter(|_| !generated)
        .map(|s| s.to_string())
        .unwrap_or_else(|| store.next_id("task"));
    if store.get(&id).is_some() {
        return Err(GovError::new(
            "DUPLICATE_ID",
            format!("{id} already exists"),
        ));
    }
    let title = fields
        .get("title")
        .and_then(|v| v.as_str())
        .or(fields.get("objective").and_then(|v| v.as_str()))
        .unwrap_or("untitled task")
        .to_string();
    if !fields.is_object() {
        return Err(GovError::new("USAGE", "task fields must be a JSON object"));
    }
    let obj = fields.as_object_mut().unwrap();
    obj.entry("task_status").or_insert(json!("DRAFT"));
    let requested = obj
        .get("task_status")
        .and_then(|v| v.as_str())
        .unwrap_or("DRAFT")
        .to_string();
    if let Some(e) = operation_only(&requested) {
        return Err(e);
    }
    obj.entry("objective").or_insert(json!(title));
    obj.entry("class").or_insert(json!("implementation"));
    let class = obj
        .get("class")
        .and_then(|c| c.as_str())
        .unwrap_or("implementation")
        .to_string();
    obj.entry("production_merge_allowed")
        .or_insert(json!(class != "experiment"));
    if class == "experiment" {
        obj.insert("production_merge_allowed".into(), json!(false));
    }
    let tier = crate::routing::tier_for_class(p, &class);
    obj.entry("minimum_model_tier").or_insert(json!(tier));
    obj.entry("minimum_reasoning").or_insert(json!("medium"));
    obj.entry("allowed_paths").or_insert(json!([]));
    obj.entry("forbidden_paths")
        .or_insert(json!(["governance/kernel/**"]));
    // MODEL_ROUTING_POLICY.reasoning_levels / tiers are the only valid values
    let pol = p.policies();
    let levels = pol.get_list("MODEL_ROUTING_POLICY", "reasoning_levels");
    if let Some(r) = obj.get("minimum_reasoning").and_then(|v| v.as_str()) {
        if !levels.is_empty() && !levels.iter().any(|l| l == r) {
            return Err(GovError::new("USAGE", format!("minimum_reasoning '{r}' is not one of MODEL_ROUTING_POLICY.reasoning_levels {levels:?}")));
        }
    }
    if let Some(t) = obj.get("minimum_model_tier").and_then(|v| v.as_str()) {
        if pol
            .get("MODEL_ROUTING_POLICY", &format!("tiers.{t}"))
            .is_none()
        {
            return Err(GovError::new(
                "USAGE",
                format!("minimum_model_tier '{t}' is not a MODEL_ROUTING_POLICY tier"),
            ));
        }
    }
    // the designated role binds who may claim and close the task, so it must name a kernel role
    if let Some(r) = obj.get("role").and_then(|v| v.as_str()) {
        if !r.is_empty() && !authority::is_kernel_role(p, r) {
            return Err(GovError::new("UNKNOWN_ROLE", format!("task role '{r}' is not defined in the kernel ROLES.yaml; the designated role binds who may claim and close the task, so it must be a kernel role id (e.g. backend-engineer, independent-test-designer)")));
        }
    }
    // provenance is a fact of the OS operation (D-0007 rule 2), never the caller's (W1 producer attribute)
    if let Some(claimed) = obj.remove("provenance") {
        obj.insert("provenance_requested".into(), claimed);
    }
    obj.insert("provenance".into(), producer);
    // which event generated the work is the work generator's record (BC-P2-24), never the caller's
    if !generated {
        if let Some(claimed) = obj.remove("generation") {
            obj.insert("generation_requested".into(), claimed);
        }
    }
    obj.remove("status_source");
    obj.remove("id");
    obj.remove("title");
    let mut rec = new_record("task", &id, &title, Value::Object(obj.clone()));
    p.schemas()
        .validate("task", &rec.data, &format!("({id})"))?;
    // READY is derived from the DAG, never asserted (BC-P2-16): a task that would not be runnable is stored in the
    // status the DAG derives, with the reasons
    let mut ready_check = Value::Null;
    if requested == "READY" {
        let ctx = DagCtx::new(p, &store);
        let ev = dag::evaluate(&ctx, &rec, Some("READY"));
        let stored = derived_status(&ev);
        if stored != "READY" {
            rec.set("task_status", json!(stored));
            rec.set(
                "status_note",
                json!(format!(
                    "READY was requested; the task DAG does not allow it: {}",
                    ev.reasons.join("; ")
                )),
            );
        }
        ready_check =
            json!({"requested_status": "READY", "stored_status": stored, "dag": ev.to_value()});
    }
    let stored = rec.get("task_status");
    rec.set(
        "status_source",
        json!({"operation": operation, "status": stored, "session": p.session_id, "role": p.role, "at": now_iso()}),
    );
    // a task record is T2 state the OS writes (WS-5 r2 IP-R3-1, round-3 integration): sealed as written by this
    // operation, so a hand edit of it — or a task record written outside gov — is refused at a concurrent close
    crate::t2::seal_record(&mut rec, operation)?;
    save_record(&p.root, &rec)?;
    let mut out = rec.data.clone();
    if !ready_check.is_null() {
        out["ready_check"] = ready_check;
    }
    // J1/J2 influence backlinks (WS-10 IP-WS10-13): research and experiment records this work relies on record it
    let cited = cited_evidence_ids(&rec);
    if !cited.is_empty() {
        match crate::lifecycle::record_influence(p, &cited, &id) {
            Ok(u) if !u.is_empty() => out["influence_recorded"] = json!(u),
            Ok(_) => {}
            Err(e) => out["influence_not_recorded"] = json!({"code": e.code, "message": e.message}),
        }
    }
    Ok(out)
}

/// Evidence ids a task relies on (`derived_from`, `required_inputs`, `optional_inputs`, input relations): what an
/// influence backlink names (IP-WS10-13).
pub fn cited_evidence_ids(t: &Record) -> Vec<String> {
    let mut out: Vec<String> = t.list("derived_from");
    for k in ["required_inputs", "optional_inputs"] {
        for e in t
            .data
            .get(k)
            .and_then(|v| v.as_array())
            .cloned()
            .unwrap_or_default()
        {
            match e {
                Value::String(s) => out.push(s),
                Value::Object(o) => {
                    if let Some(s) = o.get("id").and_then(|v| v.as_str()) {
                        out.push(s.to_string())
                    }
                }
                _ => {}
            }
        }
    }
    for rel in t
        .data
        .get("relations")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default()
    {
        if matches!(
            rel["type"].as_str(),
            Some("DERIVED_FROM") | Some("CONSUMES") | Some("USES")
        ) {
            if let Some(s) = rel["target"].as_str() {
                out.push(s.to_string());
            }
        }
    }
    let mut seen = BTreeSet::new();
    out.retain(|x| !x.is_empty() && seen.insert(x.clone()));
    out
}

/// `gov task status <id> <status>`. DONE / CLAIMED / IN_PROGRESS are refused (their operations are `close` and
/// `claim`); READY is granted only when the task DAG finds the task runnable (BC-P2-16); BLOCKED and WAITING_HUMAN set
/// here are explicit holds the DAG and replan keep until an explicit READY releases them.
pub fn set_status(p: &Project, id: &str, status: &str, note: Option<&str>) -> Result<Value> {
    control::guard_write(p, "task status")?;
    authority::require(p, "mutate_task_status")?;
    if !STATUSES.contains(&status) {
        return Err(GovError::new(
            "USAGE",
            format!("invalid task status {status}"),
        ));
    }
    if let Some(e) = operation_only(status) {
        return Err(e);
    }
    let mut store = RecordStore::load(&p.root);
    {
        let rec = store
            .get(id)
            .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
        if rec.rtype() != "task" {
            return Err(GovError::new("USAGE", format!("{id} is not a task")));
        }
        if status == "READY" {
            let ctx = DagCtx::new(p, &store);
            let ev = dag::evaluate(&ctx, rec, Some("READY"));
            if !ev.runnable() {
                return Err(GovError::new("TASK_NOT_READY", format!("{id} cannot be set READY: the task DAG does not allow it ({}): {}. Resolve the reasons (`gov task dag`); READY is derived, not asserted", ev.state.as_str(), ev.reasons.join("; "))).with_details(ev.to_value()));
            }
        }
    }
    let rec = store.get_mut(id).unwrap();
    let was_verified = crate::t2::verify_record(rec).is_verified();
    rec.set("task_status", json!(status));
    rec.set("updated", json!(today()));
    if let Some(n) = note {
        rec.set("status_note", json!(n));
    }
    rec.set(
        "status_source",
        json!({"operation": "task status", "status": status, "session": p.session_id, "role": p.role, "at": now_iso(), "note": note}),
    );
    save_task(p, rec, was_verified, "task status")?;
    let mut data = rec.data.clone();
    // a status change is a task transition: observed as a mandatory checkpoint trigger now (WS-4 R2-6)
    data["boundaries"] = observe_boundaries(p, "gov continue");
    Ok(data)
}

/// `gov task list`: every task with its status, and — for open work — the inputs that changed since its work
/// consumed them (`cit::propagation::stale_inputs`, WS-4 R2-2), so direct-change staleness is visible where work is
/// picked; generated work names the event it was generated from (BC-P2-24).
pub fn list(p: &Project, status: Option<&str>) -> Vec<Value> {
    let store = RecordStore::load(&p.root);
    store.of_type("task").into_iter().filter(|t| status.map(|s| t.get("task_status") == s).unwrap_or(true))
        .map(|t| {
            let mut v = json!({"id": t.id(), "title": t.title(), "class": t.get("class"), "task_status": t.get("task_status"), "feature": t.get("feature"), "dependencies": t.list("dependencies"), "human_gate": t.get("human_gate"), "retest_required": t.data.get("retest_required").and_then(|v| v.as_bool()).unwrap_or(false), "path": t.path});
            if !matches!(t.get("task_status").as_str(), "DONE" | "CANCELLED") {
                let (_, stale) = crate::cit::propagation::stale_inputs(p, &store, t);
                if !stale.is_empty() {
                    v["stale_inputs"] = json!(stale.iter().map(|(c, prop)| json!({"id": c.id, "consumed": c.from, "current": c.to, "propagated": prop})).collect::<Vec<_>>());
                }
            }
            if let Some(g) = crate::orchestration::generation::source_of(t) {
                v["generated_from"] = g;
            }
            v
        }).collect()
}

/// `gov task show` with what the product derives about the task (integration point for the CLI arm, which today
/// prints the record as stored): the record, its DAG evaluation, its derived staleness
/// (`cit::propagation::task_staleness`, WS-4 R2-2) and the event it was generated from (BC-P2-24).
pub fn show(p: &Project, id: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let t = store
        .get(id)
        .filter(|t| t.rtype() == "task")
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    let mut out = t.data.clone();
    let ctx = DagCtx::new(p, &store);
    out["derived"] = json!({
        "dag": dag::evaluate(&ctx, t, None).to_value(),
        "staleness": crate::cit::propagation::task_staleness(p, &store, id).unwrap_or(Value::Null),
        "generated_from": crate::orchestration::generation::source_of(t),
    });
    Ok(out)
}

/// The task's designated role, if any, refuses every other acting role. `claimed` is the contract recorded in the
/// sealed claim baseline: a role designated there binds too, so rewriting the task record during the claim does
/// not change who may close it.
fn designated_role_refusal(
    p: &Project,
    t: &Record,
    action: &str,
    claimed: Option<&Value>,
) -> Option<GovError> {
    let mut roles: Vec<String> = vec![t.get("role")];
    if let Some(r) = claimed.and_then(|c| c.get("role")).and_then(|v| v.as_str()) {
        roles.push(r.to_string());
    }
    roles.retain(|r| !r.is_empty());
    roles.dedup();
    let designated = roles.iter().find(|r| **r != p.role)?.clone();
    Some(GovError::new("ROLE_NOT_DESIGNATED", format!("{} designates role '{designated}' (task contract `role`); the acting role '{}' may not {action} it — act as '{designated}' or have the task contract amended", t.id(), p.role)).with_details(json!({"task": t.id(), "designated_role": designated, "acting_role": p.role})))
}

// ------------------------------------------------------------------------------------ recorded authorship (BC-P2-34)

/// The author of an artefact's content as the OS recorded it: the session and acting role of the T2-sealed close
/// report that accepted it.
#[derive(Debug, Clone)]
pub struct Author {
    pub report: String,
    pub task: String,
    pub session: String,
    pub role: String,
    pub closed_at: String,
    /// The current content is exactly what that close accepted (false: changed since only by a Change-Impact
    /// Transaction the claim-window rules honour).
    pub exact: bool,
}

impl Author {
    pub fn to_value(&self) -> Value {
        json!({"report": self.report, "task": self.task, "session": self.session, "role": self.role, "closed_at": self.closed_at, "exact": self.exact})
    }
}

/// **Recorded authorship** (BC-P2-34; Contract v3:366, :526, :783-785): who produced a repository path, established
/// from the OS's own record of completed work — the T2-sealed close reports and the content each accepted
/// (`mutation_evidence.observed_hashes`) — never from a field an artefact states about itself (`author_role`,
/// `independent_of_implementer`). A path's recorded author is the latest sealed close that accepted a change to it,
/// provided the content is still what that close accepted or has since been changed only by an honoured,
/// COMMITTED Change-Impact Transaction (e.g. staleness marking by CIT propagation); content changed any other way has
/// no recorded author.
pub struct AuthorshipIndex {
    by_path: BTreeMap<String, Vec<(Option<String>, Author)>>,
    by_task: BTreeMap<String, Vec<Author>>,
    /// path -> epoch seconds at which an honoured COMMITTED CIT finished touching it.
    cit_touches: BTreeMap<String, Vec<i64>>,
}

impl AuthorshipIndex {
    pub fn build(p: &Project, store: &RecordStore) -> Self {
        let _ = p;
        let mut by_path: BTreeMap<String, Vec<(Option<String>, Author)>> = BTreeMap::new();
        let mut by_task: BTreeMap<String, Vec<Author>> = BTreeMap::new();
        for r in store.of_type("report") {
            if !crate::t2::verify_record(r).is_verified() {
                continue;
            }
            let me = &r.data["mutation_evidence"];
            let a = Author {
                report: r.id(),
                task: r.get("task"),
                session: r.get("session"),
                role: r.get("role"),
                closed_at: me["closed_at"].as_str().unwrap_or("").to_string(),
                exact: true,
            };
            by_task.entry(a.task.clone()).or_default().push(a.clone());
            if let Some(h) = me["observed_hashes"].as_object() {
                for (path, hash) in h {
                    by_path
                        .entry(path.clone())
                        .or_default()
                        .push((hash.as_str().map(|s| s.to_string()), a.clone()));
                }
            }
        }
        let mut cit_touches: BTreeMap<String, Vec<i64>> = BTreeMap::new();
        for c in store.of_type("cit") {
            if c.get("cit_status") != "COMMITTED" || !cit_record_honoured(c) {
                continue;
            }
            let ex = &c.data["execution"];
            let Some(at) = ex["finished"]
                .as_str()
                .or(ex["started"].as_str())
                .and_then(epoch_of)
            else {
                continue;
            };
            if let Some(t) = ex["propagation"]["touched"].as_array() {
                for x in t.iter().filter_map(|x| x.as_str()) {
                    cit_touches.entry(x.to_string()).or_default().push(at);
                }
            }
        }
        AuthorshipIndex {
            by_path,
            by_task,
            cit_touches,
        }
    }

    /// The recorded author of the current content of `path`, or `None`.
    pub fn author_of(&self, p: &Project, path: &str) -> Option<Author> {
        let cur = std::fs::read(p.root.join(path))
            .ok()
            .map(|b| crate::util::sha256_hex(&b))?;
        let latest = self.by_path.get(path)?.iter().max_by(|(_, a), (_, b)| {
            (epoch_of(&a.closed_at), &a.report).cmp(&(epoch_of(&b.closed_at), &b.report))
        })?;
        let (hash, a) = latest;
        if hash.as_deref() == Some(cur.as_str()) {
            return Some(a.clone());
        }
        let since = epoch_of(&a.closed_at)?;
        let changed_by_cit = self
            .cit_touches
            .get(path)
            .map(|v| v.iter().any(|t| *t >= since))
            .unwrap_or(false);
        changed_by_cit.then(|| Author {
            exact: false,
            ..a.clone()
        })
    }

    /// The sealed closes of `task`.
    pub fn closes_of(&self, task: &str) -> &[Author] {
        self.by_task.get(task).map(|v| v.as_slice()).unwrap_or(&[])
    }
}

/// Is `t` independent verification work for its feature (tests, test data)?
fn independent_work(t: &Record) -> bool {
    t.get("class") == "test-design"
        || matches!(
            t.get("role").as_str(),
            "independent-test-designer" | "data-author"
        )
        || matches!(
            t.get("readiness_cell").as_str(),
            "independent_acceptance_tests" | "representative_test_data"
        )
}

/// **Independence of the acting session** (BC-P2-34, task-role side): the reasons `session` may not claim or close
/// `t`. An implementation task may not be taken by the session that authored (recorded authorship) the independent
/// tests or test data it relies on, nor by a session holding or having closed independent test/data work of the
/// same feature; and independent test/data work may not be taken by a session holding or having closed
/// implementation work of that feature.
pub fn independence_conflicts(
    ctx: &DagCtx,
    store: &RecordStore,
    t: &Record,
    session: &str,
) -> Vec<String> {
    let mut out = ctx.independence_reasons(t, Some(session));
    let feature = t.get("feature");
    let mine_impl = IMPLEMENTATION_CLASSES.contains(&t.get("class").as_str());
    let mine_indep = independent_work(t);
    if feature.is_empty() || !(mine_impl || mine_indep) {
        return out;
    }
    for other in store.of_type("task") {
        if other.id() == t.id() || other.get("feature") != feature {
            continue;
        }
        let other_impl = IMPLEMENTATION_CLASSES.contains(&other.get("class").as_str());
        let other_indep = independent_work(other);
        let (mine, theirs) = if mine_impl && other_indep {
            ("implementation", "independent test/data work")
        } else if mine_indep && other_impl {
            ("independent test/data work", "implementation")
        } else {
            continue;
        };
        if ctx.claim_session(&other.id()).as_deref() == Some(session) {
            out.push(format!("session {session} holds the claim on {} ({theirs}) of feature {feature}; the same session may not also do its {mine} ({})", other.id(), t.id()));
        }
        if let Some(a) = ctx
            .authorship()
            .closes_of(&other.id())
            .iter()
            .find(|a| a.session == session)
        {
            out.push(format!("session {session} closed {} ({theirs}) of feature {feature} ({}); the same session may not also do its {mine} ({})", other.id(), a.report, t.id()));
        }
    }
    out
}

fn independence_refusal(t: &Record, action: &str, reasons: &[String]) -> GovError {
    GovError::new(
        "INDEPENDENCE_VIOLATION",
        format!("{} may not be {action} by this session: independence is established from recorded authorship (BC-P2-34): {}. Act from an independent session in the designated role", t.id(), reasons.join("; ")),
    )
    .with_details(json!({"task": t.id(), "reasons": reasons}))
}

/// Claim a runnable task for this session (BC-P2-15, BC-P2-16). The task DAG decides whether it may be claimed at all;
/// the grant, the parallel-agent budget (BUDGET_POLICY.defaults.max_parallel_agents) and the mutation-scope overlap
/// check are decided in one claims-store transaction; the designated role and recorded-authorship independence bind
/// who may claim it.
pub fn claim(p: &Project, id: &str) -> Result<Value> {
    // G0 (tier contract, BC-P2-06, IP-WS02-03) under the availability rule: scoped to the paths the claim reserves,
    // and a block the task remedies does not refuse its claim
    let (remedies, scope_paths) = {
        let store = RecordStore::load(&p.root);
        match store.get(id).filter(|t| t.rtype() == "task") {
            Some(t) => (remedies_of(&t.data), t.list("allowed_paths")),
            None => (vec![], vec![]),
        }
    };
    let availability = guard_work(p, "task claim", ops::TASK_CLAIM, &scope_paths, &remedies)?;
    authority::require(p, "claim_task")?;
    // an upstream change made outside change control reaches the work before it is picked (WS-4 R2-3, BC-P2-04):
    // detection is content-based (what each task's work consumed), never index freshness
    let propagation = crate::cit::propagation::detect_and_propagate(p, "task claim", false)
        .map(|v| {
            json!({"changes": v["changes"], "propagated": v["propagated"], "retest_required": v["propagation"]["retest_required"], "revalidation_tasks": v["propagation"]["revalidation_tasks"]})
        })
        .unwrap_or_else(|e| json!({"error": {"code": e.code, "message": e.message}}));
    let store = RecordStore::load(&p.root);
    let t = store
        .get(id)
        .filter(|t| t.rtype() == "task")
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    // the DAG decides (BC-P2-16): dependencies, blocks, required inputs, the mandatory manifest, gates, readiness,
    // TEST_POLICY, stale inputs, re-test, explicit holds, DRAFT/DONE/CANCELLED
    let ctx = DagCtx::new(p, &store);
    let ev = dag::evaluate(&ctx, t, None);
    if !ev.runnable() {
        return Err(ev.refusal("claimed"));
    }
    if let Some(e) = designated_role_refusal(p, t, "claim", None) {
        return Err(e);
    }
    let conflicts = independence_conflicts(&ctx, &store, t, &p.session_id);
    if !conflicts.is_empty() {
        return Err(independence_refusal(t, "claimed", &conflicts));
    }
    let max_agents = p
        .policies()
        .get_i64("BUDGET_POLICY", "defaults.max_parallel_agents", 4) as usize;
    let scope = claims::scope_of_task(t);
    let iso = claims::isolation(p);
    let granted = claims::claim_with(
        p,
        &ClaimRequest {
            task_id: id,
            session: &p.session_id,
            role: &p.role,
            isolation: &iso,
            scope: &scope,
            lease_secs: None,
            max_parallel_sessions: Some(max_agents),
        },
    );
    let mut c = match granted {
        Ok(c) => c,
        Err(e) if e.code == "BUDGET_EXCEEDED" => {
            let active: Vec<String> = e.details["active_sessions"]
                .as_array()
                .map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(|s| s.to_string()))
                        .collect()
                })
                .unwrap_or_default();
            let on = p.policies().get_str(
                "BUDGET_POLICY",
                "on_threshold_exceeded",
                "human_decision_gate",
            );
            let mut gate_id = Value::Null;
            if on == "human_decision_gate" {
                let g = gates::create_system(
                    p,
                    json!({"question": format!("Budget threshold exceeded: {} parallel agent sessions hold claims (BUDGET_POLICY.defaults.max_parallel_agents = {max_agents}). Allow session {} to claim {id}?", active.len(), p.session_id), "why_now": "a task claim would exceed the delegated parallelism budget", "current_state": format!("active sessions: {active:?}"), "options": [{"id": "A", "description": "raise the budget in the project overlay"}, {"id": "B", "description": "wait for a session to finish"}], "impact": "cost and coordination", "reversibility": "reversible", "recommendation": "B", "confidence": 0.7, "trigger": "budget_threshold", "impact_radius": "R1"}),
                )?;
                gate_id = g["id"].clone();
            }
            return Err(GovError::new("BUDGET_EXCEEDED", format!("max_parallel_agents ({max_agents}) reached: {} active session(s); human decision gate {gate_id} raised", active.len())).with_details(json!({"active_sessions": active, "human_gate": gate_id})));
        }
        Err(e) => return Err(e),
    };
    let renewed = c["renewed"].as_bool().unwrap_or(false);
    // the grant is atomic; the task record is not part of that transaction, so re-read it: a concurrent close that
    // finished between the DAG check above and the grant must not be followed by a claim of a closed task
    let store = RecordStore::load(&p.root);
    let st_now = store
        .get(id)
        .map(|r| r.get("task_status"))
        .unwrap_or_default();
    if matches!(st_now.as_str(), "DONE" | "CANCELLED" | "") {
        if !renewed {
            let _ = claims::release(p, id, &p.session_id, false);
        }
        return Err(GovError::new(
            "TASK_NOT_RUNNABLE",
            format!("{id} became {st_now} while it was being claimed; the claim was withdrawn"),
        ));
    }
    set_status_internal(p, id, "IN_PROGRESS", None, "task claim")?;
    let store = RecordStore::load(&p.root);
    c["baseline"] = establish_baseline(p, &store, id, renewed)?;
    if availability.get("availability").is_some() {
        c["availability"] = availability["availability"].clone();
    }
    if propagation["changes"].as_u64().unwrap_or(0) > 0 || propagation.get("error").is_some() {
        c["upstream_changes"] = propagation;
    }
    // the transition is a mandatory checkpoint trigger, observed by the product now (WS-4 R2-6, BC-P2-05)
    c["boundaries"] = observe_boundaries(p, &format!("gov task close {id} --report <receipt>"));
    Ok(c)
}

/// **Observe execution boundaries right after a transition** (WS-4 R2-6; BC-P2-05, Contract v3:729-742): every
/// mandatory checkpoint trigger that occurred since the latest checkpoint (a task transition, a material decision,
/// a significant mutation, a routing switch) becomes a checkpoint now, not only at the next boundary. Never fails
/// the transition it follows: an index that cannot be opened, or a checkpoint that cannot be written, is reported.
pub fn observe_boundaries(p: &Project, next_action: &str) -> Value {
    // a health-check sandbox is a disposable copy of the project, not a working session: its transitions are not
    // the project's continuity (and every file of a fresh copy would read as a significant mutation)
    if crate::scheduler::sandbox::inside_sandbox() {
        return json!({"observed": false, "reason": "inside a health-check sandbox (a copy, not a session)"});
    }
    let db = match RuntimeDb::open(&p.db_path()).and_then(|d| d.init_schema().map(|_| d)) {
        Ok(d) => d,
        Err(e) => {
            return json!({"observed": false, "reason": format!("[{}] {}", e.code, e.message)})
        }
    };
    match checkpoints::observe_boundaries(p, &db, next_action) {
        Ok(v) => json!({"observed": true, "checkpoints": v}),
        Err(e) => json!({"observed": false, "reason": format!("[{}] {}", e.code, e.message)}),
    }
}

fn set_status_internal(
    p: &Project,
    id: &str,
    status: &str,
    note: Option<&str>,
    operation: &str,
) -> Result<Value> {
    let mut store = RecordStore::load(&p.root);
    let rec = store
        .get_mut(id)
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    let was_verified = crate::t2::verify_record(rec).is_verified();
    rec.set("task_status", json!(status));
    rec.set("updated", json!(today()));
    if let Some(n) = note {
        rec.set("status_note", json!(n));
    }
    rec.set(
        "status_source",
        json!({"operation": operation, "status": status, "session": p.session_id, "role": p.role, "at": now_iso()}),
    );
    save_task(p, rec, was_verified, operation)?;
    Ok(rec.data.clone())
}

/// Persist a task record an OS operation rewrote, under the OS re-seal rule (integration O-7; WS-5 r2 IP-R3-1): the
/// record is re-sealed as written by `operation` when its seal verified immediately before this write
/// (`was_verified`), and written unsealed otherwise — the OS never blesses content it did not write (a legacy or
/// hand-edited task record stays unhonoured).
pub fn save_task(p: &Project, rec: &mut Record, was_verified: bool, operation: &str) -> Result<()> {
    crate::t2::seal_if_verified(rec, was_verified, operation)?;
    save_record(&p.root, rec)
}

/// Release a claim. The mutations the claim window produced stay attributed to the task: they are carried into the
/// baseline of the next claim, so a release followed by a re-claim cannot reset the observed-mutation evidence.
/// Releasing is a governed write like every other claim operation: it passes the write guard (kernel trust, the
/// OWNER-DECISION-0006 §6 default-refuse allow-list, FREEZE_WRITES / PAUSE). The task's status afterwards is the one
/// the DAG derives (READY only when it is runnable).
pub fn release(p: &Project, id: &str, force: bool) -> Result<bool> {
    control::guard_write(
        p,
        if force {
            "task release --force"
        } else {
            "task release"
        },
    )?;
    authority::require(
        p,
        if force {
            "force_release_task"
        } else {
            "release_task"
        },
    )?;
    let released = claims::release_row(p, id, &p.session_id, force)?;
    if released.is_some() {
        let store = RecordStore::load(&p.root);
        if let Some(t) = store.get(id) {
            let _ = carry_forward(p, &store, t);
            let st = t.get("task_status");
            // an explicit hold set while the task was claimed stays as it was set
            if !matches!(st.as_str(), "DONE" | "CANCELLED") && dag::explicit_hold(t).is_none() {
                let ctx = DagCtx::new(p, &store);
                let ev = dag::evaluate(&ctx, t, Some("READY"));
                let _ = set_status_internal(
                    p,
                    id,
                    derived_status(&ev),
                    Some("released"),
                    "task release",
                );
            }
        }
        // releasing is a task transition (WS-4 R2-6)
        let _ = observe_boundaries(p, "gov continue");
    }
    Ok(released.is_some())
}

// ------------------------------------------------------------------------------------ OS-written state (BC-P2-09)

/// Locations only the Governance OS writes while a task is open (derived views, evidence records, gate/decision/CIT
/// records, task records, continuity records). A change under one of them is never simply "exempt": it is the OS's own
/// write only when [`classify_os_path`] can tell it apart from a worker's.
const OS_MANAGED_PREFIXES: &[&str] = &[
    "governance/generated/",
    // BC-P2-31 (WS-7 round 3, IP-W7R3-1 / IP-R3-WS03-3): the OS-written plugin registry's home
    // (`paths::PLUGIN_REGISTRY_PATH`); a registration made inside a claim is recognised by its seal at close
    "governance/registry/",
    "spec/reports/",
    "spec/audits/",
    "spec/planning/",
    "spec/decisions/HDG-",
    "spec/decisions/CIT-",
    "spec/decisions/D-",
    "spec/lessons/",
    "framework.json",
    ".gitignore",
    "spec/now/NOW.md",
];

/// Is `path` a location only the OS writes? `spec/tasks/` holds both OS-written task records and authored test
/// obligations (`TST-*`): only task records are OS-managed there, so an authored obligation is observed (and its
/// authorship recorded by the close that accepts it).
fn os_managed(p: &Project, path: &str) -> bool {
    if let Some(rest) = path.strip_prefix("spec/tasks/") {
        let abs = p.root.join(path);
        return match std::fs::read_to_string(&abs) {
            Ok(text) => crate::records::parse_record_text(&text, path)
                .map(|r| r.rtype() == "task")
                .unwrap_or(false),
            Err(_) => rest.starts_with("TASK-"),
        };
    }
    OS_MANAGED_PREFIXES.iter().any(|pre| path.starts_with(pre))
}

/// Paths the repository contract declares as generated/derived outputs are not worker mutations either.
fn contract_generated(p: &Project, path: &str) -> bool {
    let d = p.contract().decide(path);
    matches!(d.class().as_str(), "generated" | "derived")
}

/// How a changed OS-managed path stands at task close.
#[derive(Debug, Clone)]
pub enum OsWrite {
    /// Provably written by a gov operation on this machine: its T2 seal verifies.
    Bound,
    /// No seal, and its kind is not (yet) sealed by every OS writer: accepted as the OS's own write and reported.
    Unbound(String),
    /// A lower-trust write to OS-written state: a seal that no longer verifies, a kind the OS always seals written
    /// without one, or a governed record deleted.
    Violation(String),
}

/// The record kind a changed file is, when every OS write of that kind is sealed: gates, decisions derived from a
/// gate answer (or asserting human approval), close reports (sealed by [`close`], their only writer) and every type
/// `t2::SEALED_RECORD_TYPES` names.
fn sealed_kind(p: &Project, path: &str) -> Option<String> {
    let text = std::fs::read_to_string(p.root.join(path)).ok()?;
    let r = crate::records::parse_record_text(&text, path)?;
    let t = r.rtype();
    if crate::t2::SEALED_RECORD_TYPES.contains(&t.as_str()) {
        return Some(format!("a {t} record"));
    }
    if t == "report" {
        return Some("a task-close report".into());
    }
    if t == "decision"
        && (r
            .data
            .get("human_approved")
            .and_then(|v| v.as_bool())
            .unwrap_or(false)
            || r.list("derived_from").iter().any(|d| d.starts_with("HDG-")))
    {
        return Some("a decision derived from a Human Decision Gate answer".into());
    }
    None
}

/// Record kinds that became sealed kinds after records of them could exist unsealed (task records: WS-5 r2 IP-R3-1;
/// CIT records: IP-R3-2 — both at the round-3 integration). See [`write_baseline`] and [`classify_os_path_in`].
pub const LEGACY_SEALED_KINDS: &[&str] = &["task", "cit"];

/// Classify a changed OS-managed path (BC-P2-09 close side, `t2::classify_path`): the OS's own write is recognised by
/// its seal, never by its location.
pub fn classify_os_path(p: &Project, path: &str) -> OsWrite {
    classify_os_path_in(p, path, &BTreeSet::new())
}

/// [`classify_os_path`] against a claim baseline: `legacy_unsealed` names the records of [`LEGACY_SEALED_KINDS`] that
/// were already unsealed when the claim began (legacy, or appended by a governed change). Such a record, rewritten
/// without a seal inside the window, is the OS's unblessed write of content it never sealed — reported, not the
/// worker's T2 violation. Anything else unsealed of a sealed kind is a violation.
pub fn classify_os_path_in(p: &Project, path: &str, legacy_unsealed: &BTreeSet<String>) -> OsWrite {
    use crate::t2::Binding;
    if !p.root.join(path).exists() {
        return if path.starts_with("spec/") {
            OsWrite::Violation(format!("{path} (an OS-written governed record) was deleted outside a gov operation; OS-written records are superseded, never deleted"))
        } else {
            OsWrite::Unbound(format!("{path}: derived output removed"))
        };
    }
    match crate::t2::classify_path(&p.root, path) {
        Binding::Verified { .. } => OsWrite::Bound,
        Binding::Unsealed => match sealed_kind(p, path) {
            Some(kind) if legacy_unsealed.contains(path) => OsWrite::Unbound(format!("{path} is {kind} that carried no seal when this claim began (written before the OS sealed its kind, or appended by a governed change): rewritten inside the window without a seal, since the OS never seals content it did not write; reported, not this task's T2 violation")),
            Some(kind) => OsWrite::Violation(format!("{path} is {kind}: only a gov operation writes it and every such write is sealed (T2), but this one carries no seal")),
            None => OsWrite::Unbound(format!("{path}: OS-managed location, record kind not yet sealed by every writer")),
        },
        other => OsWrite::Violation(format!(
            "{path}: OS-written state (T2) changed outside a gov operation (binding {}: {})",
            other.code(),
            other.to_value()["reason"].as_str().unwrap_or("")
        )),
    }
}

/// Content listing of the governed repository (tracked + untracked, honouring .gitignore; walk fallback without git).
pub fn tree_listing(p: &Project) -> std::collections::BTreeMap<String, String> {
    let mut out = std::collections::BTreeMap::new();
    let (code, stdout, _) = p.git(&["ls-files", "-co", "--exclude-standard", "-z"]);
    let paths: Vec<String> = if code == 0 {
        stdout
            .split('\0')
            .filter(|s| !s.is_empty())
            .map(|s| s.to_string())
            .collect()
    } else {
        crate::paths::iter_repo_files(&p.root, false)
            .into_iter()
            .map(|(_, rel)| rel)
            .collect()
    };
    for rel in paths {
        if rel.starts_with(".governance-runtime/")
            || rel.starts_with(".git/")
            || rel.starts_with(&format!("{}/", crate::paths::STATE_DIR))
        {
            continue;
        }
        let abs = p.root.join(&rel);
        if let Ok(bytes) = std::fs::read(&abs) {
            out.insert(rel, crate::util::sha256_hex(&bytes));
        }
    }
    out
}

/// **Where claim baselines and carried-mutation sets live (BC-P2-31).** They are the evidence a task close is checked
/// against and cannot be rebuilt, so they are kept where the kernel puts non-rebuildable operational state —
/// `paths::store_path(root, "claim-trees")`, `.governance-state/tasks/` — not in the derived runtime directory an
/// operator may delete (framework §19). A directory an earlier release kept at `.governance-runtime/tasks/` is moved
/// there once (`paths::relocate_legacy`) while nothing is at the new place; afterwards a directory reappearing at the
/// legacy path is not the store and is reported by `paths::misplaced_os_state`, never merged.
pub fn claim_trees_dir(p: &Project) -> std::path::PathBuf {
    let target = crate::paths::store_path(&p.root, "claim-trees")
        .unwrap_or_else(|| p.root.join(crate::paths::STATE_DIR).join("tasks"));
    if !target.exists() && p.runtime_dir().join("tasks").is_dir() {
        let _ = crate::paths::relocate_legacy(&p.root, "claim-trees");
    }
    target
}

fn task_runtime_dir(p: &Project, id: &str) -> std::path::PathBuf {
    claim_trees_dir(p).join(id)
}

/// Create the directory a claim-tree file is written to, inside the self-ignored state directory.
fn ensure_task_state_dir(p: &Project, id: &str) -> Result<std::path::PathBuf> {
    crate::paths::ensure_state_dir(&p.root)?;
    let d = task_runtime_dir(p, id);
    std::fs::create_dir_all(&d)?;
    Ok(d)
}
fn claim_tree_path(p: &Project, id: &str) -> std::path::PathBuf {
    task_runtime_dir(p, id).join("claim-tree.json")
}
/// Mutations of earlier claim windows of the task (path -> hash at the start of that window; null = absent).
fn carried_path(p: &Project, id: &str) -> std::path::PathBuf {
    task_runtime_dir(p, id).join("carried.json")
}

/// Epoch seconds of an RFC 3339 timestamp or a bare `YYYY-MM-DD` date (midnight UTC).
fn epoch_of(s: &str) -> Option<i64> {
    if let Ok(d) = chrono::DateTime::parse_from_rfc3339(s) {
        return Some(d.timestamp());
    }
    chrono::NaiveDate::parse_from_str(s, "%Y-%m-%d")
        .ok()
        .and_then(|d| d.and_hms_opt(0, 0, 0))
        .map(|d| d.and_utc().timestamp())
}

/// The claim baseline of a task as read back.
#[derive(Debug, Clone)]
pub enum Baseline {
    /// Sealed by the claim that wrote it and unmodified since.
    Bound(Value),
    /// Present but not provably written by a claim on this machine (edited, legacy, or another machine's).
    Unbound { binding: Value },
    /// No baseline.
    Absent,
}

/// Read a task's claim baseline and verify its T2 seal (a baseline is machine-local runtime state the worker's
/// account can write; the seal is what makes it the claim's evidence).
pub fn read_baseline(p: &Project, id: &str) -> Baseline {
    let Ok(doc) = crate::util::read_json(&claim_tree_path(p, id)) else {
        return Baseline::Absent;
    };
    let b = crate::t2::verify_value(&doc, "");
    if b.is_verified() {
        Baseline::Bound(doc)
    } else {
        Baseline::Unbound {
            binding: b.to_value(),
        }
    }
}

fn bound_baseline(p: &Project, id: &str) -> Option<Value> {
    match read_baseline(p, id) {
        Baseline::Bound(d) => Some(d),
        _ => None,
    }
}

/// The contract fields a claim reserves: the close is held to them as claimed as well as to the record as it is.
fn contract_snapshot(t: &Record) -> Value {
    json!({"allowed_paths": t.list("allowed_paths"), "forbidden_paths": t.list("forbidden_paths"),
           "production_merge_allowed": production_merge_allowed(t), "class": t.get("class"), "role": t.get("role"),
           "feature": t.get("feature"), "human_gate": t.get("human_gate")})
}

/// Snapshot the working tree now and make it the task's claim baseline (overwriting any previous one).
pub fn snapshot_tree(p: &Project, id: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    write_baseline(p, &store, id, tree_listing(p), &BTreeMap::new())
}

/// The claim window is bound exactly, not by clock: the baseline lists the CITs already COMMITTED and the close
/// reports already written when it was taken, and only CITs committed / closes reported after it count as inside
/// the window. The baseline also records the task contract as claimed, and is sealed (T2) so the worker whose close
/// it governs cannot rewrite it.
fn write_baseline(
    p: &Project,
    store: &RecordStore,
    id: &str,
    mut files: BTreeMap<String, String>,
    carried: &BTreeMap<String, Option<String>>,
) -> Result<Value> {
    let cits_committed: Vec<String> = store
        .of_type("cit")
        .into_iter()
        .filter(|c| c.get("cit_status") == "COMMITTED")
        .map(|c| c.id())
        .collect();
    let reports_present: Vec<String> = store
        .of_type("report")
        .into_iter()
        .map(|r| r.id())
        .collect();
    for (k, orig) in carried {
        match orig {
            Some(h) => {
                files.insert(k.clone(), h.clone());
            }
            None => {
                files.remove(k);
            }
        }
    }
    let contract = store.get(id).map(contract_snapshot).unwrap_or(Value::Null);
    // records of the kinds sealed since round 3 (LEGACY_SEALED_KINDS) that carry no seal at the baseline: written
    // before the OS sealed their kind, or appended by a governed change. An OS write into one inside this window
    // cannot re-seal it (the OS never blesses content it did not write), so at close such a record is reported, not
    // refused as this task's T2 violation; a seal stripped, or such a record created, inside the window is refused.
    let unsealed_os_records: Vec<String> = store
        .records
        .iter()
        .filter(|r| {
            LEGACY_SEALED_KINDS.contains(&r.rtype().as_str())
                && r.data
                    .get(crate::t2::SEAL_FIELD)
                    .map(|v| v.is_null())
                    .unwrap_or(true)
        })
        .map(|r| r.path.clone())
        .collect();
    let mut doc = json!({"task": id, "at": now_iso(), "commit": p.git_commit(), "session": p.session_id, "role": p.role, "worktree": claims::worktree_id(p),
        "files": files, "carried": carried.keys().collect::<Vec<_>>(), "cits_committed": cits_committed, "reports_present": reports_present,
        "contract": contract, "unsealed_os_records": unsealed_os_records,
        "method": "git ls-files -co --exclude-standard + sha256 (walk fallback); mutations of earlier claim windows carried"});
    crate::t2::seal_value(&mut doc, "", "task claim baseline")?;
    let path = claim_tree_path(p, id);
    ensure_task_state_dir(p, id)?;
    crate::util::write_json(&path, &doc)?;
    let _ = std::fs::remove_file(carried_path(p, id));
    Ok(
        json!({"files": doc["files"].as_object().map(|m| m.len()).unwrap_or(0), "commit": doc["commit"], "at": doc["at"], "reused": false, "carried": doc["carried"], "sealed": true}),
    )
}

/// The carried mutations of earlier claim windows. A carried set that does not verify (edited outside gov) is not
/// trusted to *drop* anything: every uncommitted path is carried as if created in the window, so it must still be
/// declared and in scope at close.
fn read_carried(p: &Project, id: &str) -> BTreeMap<String, Option<String>> {
    let Ok(v) = crate::util::read_json(&carried_path(p, id)) else {
        return BTreeMap::new();
    };
    if !crate::t2::verify_value(&v, "").is_verified() {
        return uncommitted_paths(p)
            .into_iter()
            .filter(|f| !os_managed(p, f) && !contract_generated(p, f))
            .map(|f| (f, None))
            .collect();
    }
    v["carried"]
        .as_object()
        .cloned()
        .map(|m| {
            m.into_iter()
                .map(|(k, v)| (k, v.as_str().map(|s| s.to_string())))
                .collect()
        })
        .unwrap_or_default()
}

fn write_carried(p: &Project, id: &str, carried: &BTreeMap<String, Option<String>>) -> Result<()> {
    let mut doc = json!({"task": id, "carried": carried, "at": now_iso()});
    crate::t2::seal_value(&mut doc, "", "task release (carried mutations)")?;
    ensure_task_state_dir(p, id)?;
    crate::util::write_json(&carried_path(p, id), &doc)
}

/// The claim baseline: kept when the same session continues its claim; otherwise a fresh snapshot in which every
/// mutation of an earlier claim window of this task (released, expired or abandoned) keeps its original baseline
/// value, so it is still observed — and must still be declared and in scope — when the task closes.
fn establish_baseline(
    p: &Project,
    store: &RecordStore,
    id: &str,
    continuing: bool,
) -> Result<Value> {
    if continuing {
        if let Some(doc) = bound_baseline(p, id) {
            return Ok(
                json!({"files": doc["files"].as_object().map(|m| m.len()).unwrap_or(0), "commit": doc["commit"], "at": doc["at"], "reused": true, "carried": doc["carried"], "sealed": true}),
            );
        }
    }
    let mut carried = read_carried(p, id);
    if let Some(t) = store.get(id) {
        match read_baseline(p, id) {
            // an earlier claim window ended without a release or a close (lease expired, swept, session gone)
            Baseline::Bound(doc) => {
                let obs = observe_against(p, store, t, Some(&doc));
                for (k, orig) in obs.baseline_of {
                    carried.entry(k).or_insert(orig);
                }
            }
            // a baseline that does not verify is not trusted to hide anything: every uncommitted change is carried
            Baseline::Unbound { .. } => {
                for f in uncommitted_paths(p) {
                    if !os_managed(p, &f) && !contract_generated(p, &f) {
                        carried.entry(f).or_insert(None);
                    }
                }
            }
            Baseline::Absent => {}
        }
    }
    write_baseline(p, store, id, tree_listing(p), &carried)
}

/// At release: fold the claim window's attributable mutations into the task's carried set and retire the baseline.
fn carry_forward(p: &Project, store: &RecordStore, t: &Record) -> Result<()> {
    let id = t.id();
    let path = claim_tree_path(p, &id);
    let mut carried = read_carried(p, &id);
    match read_baseline(p, &id) {
        Baseline::Bound(doc) => {
            let obs = observe_against(p, store, t, Some(&doc));
            for (k, orig) in obs.baseline_of {
                carried.entry(k).or_insert(orig);
            }
        }
        Baseline::Unbound { .. } => {
            for f in uncommitted_paths(p) {
                if !os_managed(p, &f) && !contract_generated(p, &f) {
                    carried.entry(f).or_insert(None);
                }
            }
        }
        Baseline::Absent => return Ok(()),
    }
    write_carried(p, &id, &carried)?;
    let _ = std::fs::remove_file(&path);
    Ok(())
}

/// What a task's claim window shows in the working tree.
#[derive(Debug, Clone, Default)]
pub struct Observation {
    /// Paths changed since the baseline that are this task's (CIT-covered paths and T2 violations included,
    /// attributed ones not).
    pub observed: Vec<String>,
    /// For each observed path not covered by a CIT: its baseline hash (None = the path did not exist).
    pub baseline_of: BTreeMap<String, Option<String>>,
    /// For each observed path not covered by a CIT: its current hash (None = deleted).
    pub current_of: BTreeMap<String, Option<String>>,
    /// Every path a Change-Impact Transaction executed inside the claim window wrote **and whose current content is
    /// what that CIT left** ([`cit_window_writes`], IP-R3-6): what may lie outside the task's scope because a CIT
    /// governing that specific change covers it.
    pub cit_window: BTreeSet<String>,
    /// The observed paths among `cit_window`.
    pub cit_covered: BTreeSet<String>,
    /// Changed paths attributed to another claim or to a task closed inside the window.
    pub attributed: Vec<Value>,
    /// Observed changes to OS-written state that no OS operation provably produced (BC-P2-09): `{path, reason}`.
    /// They are refused whether or not they are declared or in scope.
    pub t2_violations: Vec<Value>,
    /// Changed OS-managed paths accepted as the OS's own writes: sealed and verifying.
    pub os_bound: Vec<String>,
    /// Changed OS-managed paths accepted as the OS's own writes without a seal (kinds not yet sealed by every
    /// writer), reported so nothing is invisible.
    pub os_unbound: Vec<String>,
    /// Start of the claim window (epoch seconds), when there is a baseline.
    pub window_start: Option<i64>,
    pub evidence: Value,
}

/// Is a CIT record honoured by the claim-window rules? A record carrying a T2 seal must verify; an unsealed record
/// is honoured only while CIT state is not declared sealed (`t2::SEALED_RECORD_TYPES` does not contain `cit`) —
/// once it is, an unsealed CIT record governs nothing.
pub fn cit_record_honoured(c: &Record) -> bool {
    use crate::t2::Binding;
    match crate::t2::verify_record(c) {
        Binding::Verified { .. } => true,
        Binding::Unsealed => !crate::t2::SEALED_RECORD_TYPES.contains(&"cit"),
        _ => false,
    }
}

/// Paths touched by a COMMITTED Change-Impact Transaction that finished at or after `since` — the claim window of
/// the task being closed. A CIT committed before the window began governs nothing the task did.
pub fn cit_covered_paths(store: &RecordStore, since: Option<i64>) -> BTreeSet<String> {
    let mut out = BTreeSet::new();
    let Some(since) = since else {
        return out;
    };
    for c in store.of_type("cit") {
        if c.get("cit_status") != "COMMITTED" || !cit_record_honoured(c) {
            continue;
        }
        let ex = &c.data["execution"];
        let at = ex["finished"]
            .as_str()
            .or(ex["started"].as_str())
            .and_then(epoch_of);
        if at.map(|a| a >= since).unwrap_or(false) {
            if let Some(t) = ex["propagation"]["touched"].as_array() {
                out.extend(t.iter().filter_map(|x| x.as_str().map(|s| s.to_string())));
            }
        }
    }
    out
}

/// Paths touched by the CITs committed inside a claim window: those COMMITTED now and not already COMMITTED when
/// the baseline was taken (baselines written before that list existed fall back to [`cit_covered_paths`]). Only CIT
/// records the T2 rules honour count ([`cit_record_honoured`]).
pub fn cit_window_paths(store: &RecordStore, baseline: Option<&Value>) -> BTreeSet<String> {
    let Some(doc) = baseline else {
        return BTreeSet::new();
    };
    let Some(before) = doc["cits_committed"].as_array() else {
        return cit_covered_paths(store, doc["at"].as_str().and_then(epoch_of));
    };
    let before: BTreeSet<&str> = before.iter().filter_map(|x| x.as_str()).collect();
    let mut out = BTreeSet::new();
    for c in store.of_type("cit") {
        if c.get("cit_status") == "COMMITTED"
            && !before.contains(c.id().as_str())
            && cit_record_honoured(c)
        {
            if let Some(t) = c.data["execution"]["propagation"]["touched"].as_array() {
                out.extend(t.iter().filter_map(|x| x.as_str().map(|s| s.to_string())));
            }
        }
    }
    out
}

/// **What the CITs committed inside a claim window wrote, bound to content** (WS-5 IP-R3-6 / WS-4 IP-3, BC-P2-14
/// "a mutation outside a task's allowed paths is accepted only when a CIT governing that specific change covers it"):
/// path -> the SHA-256 each in-window write left (`None` = the CIT removed the path). Only a COMMITTED transaction
/// whose sealed state and recorded writes verify (`cit::binding::verified_writes`) counts; a path is governed by it
/// only while its current content is what the CIT wrote — a later edit of the same path is the worker's again.
/// In-window = committed now and not already committed when the baseline was taken (a baseline written before that
/// list existed: finished at or after the window start).
pub fn cit_window_writes(
    store: &RecordStore,
    baseline: Option<&Value>,
) -> BTreeMap<String, BTreeSet<Option<String>>> {
    let mut out: BTreeMap<String, BTreeSet<Option<String>>> = BTreeMap::new();
    let Some(doc) = baseline else {
        return out;
    };
    let before: Option<BTreeSet<&str>> = doc["cits_committed"]
        .as_array()
        .map(|a| a.iter().filter_map(|x| x.as_str()).collect());
    let since = doc["at"].as_str().and_then(epoch_of);
    for c in store.of_type("cit") {
        if c.get("cit_status") != "COMMITTED" {
            continue;
        }
        let inside = match &before {
            Some(set) => !set.contains(c.id().as_str()),
            None => {
                let ex = &c.data["execution"];
                match (
                    since,
                    ex["finished"]
                        .as_str()
                        .or(ex["started"].as_str())
                        .and_then(epoch_of),
                ) {
                    (Some(s), Some(a)) => a >= s,
                    _ => false,
                }
            }
        };
        if !inside {
            continue;
        }
        if let Ok(writes) = crate::cit::binding::verified_writes(c) {
            for w in writes {
                if !w.path.is_empty() {
                    out.entry(w.path).or_default().insert(w.sha256);
                }
            }
        }
    }
    out
}

/// Content accepted by closes that completed inside the window: report id, task, path -> hash (None = deleted).
/// Only T2-sealed close reports count (a hand-written report accepts nothing).
type ClosedState = (String, String, BTreeMap<String, Option<String>>);
fn closed_states(store: &RecordStore, baseline: &Value, exclude_task: &str) -> Vec<ClosedState> {
    let present: Option<BTreeSet<String>> = baseline["reports_present"].as_array().map(|a| {
        a.iter()
            .filter_map(|x| x.as_str().map(|s| s.to_string()))
            .collect()
    });
    let since = baseline["at"]
        .as_str()
        .and_then(epoch_of)
        .unwrap_or(i64::MAX);
    let mut out = vec![];
    for r in store.of_type("report") {
        let me = &r.data["mutation_evidence"];
        let Some(h) = me["observed_hashes"].as_object() else {
            continue;
        };
        let inside = match &present {
            Some(set) => !set.contains(&r.id()),
            None => me["closed_at"]
                .as_str()
                .and_then(epoch_of)
                .map(|a| a >= since)
                .unwrap_or(false),
        };
        if !inside {
            continue;
        }
        let task = r.get("task");
        if task == exclude_task {
            continue;
        }
        // only the recorded, OS-written close of a DONE task counts
        if !crate::t2::verify_record(r).is_verified() {
            continue;
        }
        let recorded = store
            .get(&task)
            .map(|t| t.get("task_status") == "DONE" && t.get("closed_by_report") == r.id())
            .unwrap_or(false);
        if !recorded {
            continue;
        }
        let m = h
            .iter()
            .map(|(k, v)| (k.clone(), v.as_str().map(|s| s.to_string())))
            .collect();
        out.push((r.id(), task, m));
    }
    out
}

/// Mutations observed for task `t` since its claim baseline, with attribution:
/// 1. contract-generated paths are never the worker's; an OS-managed path is the OS's own write only when
///    [`classify_os_path`] can tell (a verifying seal, or an unsealed kind not yet sealed by every writer) — a
///    T2 violation is the worker's mutation of OS-written state;
/// 2. a path whose current content is exactly what a task closed inside this window accepted belongs to that close;
/// 3. a path outside this task's scope, inside the scope of another live claim made from the same working tree and
///    changed since that claim's own baseline, belongs to that claim (scopes of concurrent claims are disjoint);
/// 4. everything else is this task's. Paths a CIT executed inside the window touched are reported in `cit_covered`.
///
/// Only a sealed (bound) baseline is used; without one this observes git's uncommitted changes instead.
pub fn observe(p: &Project, store: &RecordStore, t: &Record) -> Observation {
    let doc = bound_baseline(p, &t.id());
    observe_against(p, store, t, doc.as_ref())
}

/// Sort a changed path under an OS-managed location into the observation (see [`observe`]).
fn classify_into(
    p: &Project,
    f: &str,
    obs: &mut Observation,
    legacy_unsealed: &BTreeSet<String>,
) -> bool {
    match classify_os_path_in(p, f, legacy_unsealed) {
        OsWrite::Bound => {
            obs.os_bound.push(f.to_string());
            false
        }
        OsWrite::Unbound(_) => {
            obs.os_unbound.push(f.to_string());
            false
        }
        OsWrite::Violation(reason) => {
            obs.t2_violations.push(json!({"path": f, "reason": reason}));
            true
        }
    }
}

fn observe_against(
    p: &Project,
    store: &RecordStore,
    t: &Record,
    doc: Option<&Value>,
) -> Observation {
    let id = t.id();
    let now = tree_listing(p);
    let Some(doc) = doc else {
        // no bound claim baseline (only reachable by an L3+ forced close): fall back to git's view of uncommitted
        // changes
        let mut obs = Observation::default();
        for f in uncommitted_paths(p) {
            if contract_generated(p, &f)
                || (os_managed(p, &f) && !classify_into(p, &f, &mut obs, &BTreeSet::new()))
            {
                continue;
            }
            obs.current_of.insert(f.clone(), now.get(&f).cloned());
            obs.observed.push(f);
        }
        obs.evidence = json!({"baseline": "none (uncommitted changes: git diff HEAD + untracked files)", "observed": obs.observed,
            "t2_violations": obs.t2_violations, "os_managed_bound": obs.os_bound, "os_managed_unbound": obs.os_unbound});
        return obs;
    };
    let baseline: BTreeMap<String, String> = doc["files"]
        .as_object()
        .map(|m| {
            m.iter()
                .filter_map(|(k, v)| v.as_str().map(|s| (k.clone(), s.to_string())))
                .collect()
        })
        .unwrap_or_default();
    let window_start = doc["at"].as_str().and_then(epoch_of);
    let legacy_unsealed: BTreeSet<String> = doc["unsealed_os_records"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    // what the in-window CITs wrote, bound to content (IP-R3-6): a path is the CIT's governed change only while its
    // current content is what the CIT left
    let cit_writes = cit_window_writes(store, Some(doc));
    let cit_covered: BTreeSet<String> = cit_writes
        .iter()
        .filter(|(path, hashes)| hashes.contains(&now.get(*path).cloned()))
        .map(|(path, _)| path.clone())
        .collect();
    let mut changed: BTreeSet<String> = BTreeSet::new();
    for (rel, h) in &now {
        if baseline.get(rel) != Some(h) {
            changed.insert(rel.clone());
        }
    }
    for rel in baseline.keys() {
        if !now.contains_key(rel) {
            changed.insert(rel.clone());
        }
    }
    let closed = closed_states(store, doc, &id);
    let own_scope = reserved_scope(p, t).unwrap_or_else(|| claims::scope_of_task(t));
    let wt = claims::worktree_id(p);
    let others: Vec<(Value, Vec<String>, BTreeMap<String, String>)> = claims::live(p)
        .unwrap_or_default()
        .into_iter()
        .filter(|c| {
            c["task_id"].as_str() != Some(id.as_str())
                && c["worktree"].as_str() == Some(wt.as_str())
        })
        .map(|c| {
            let other = c["task_id"].as_str().unwrap_or("").to_string();
            let theirs: BTreeMap<String, String> = bound_baseline(p, &other)
                .and_then(|d| d["files"].as_object().cloned())
                .map(|m| {
                    m.into_iter()
                        .filter_map(|(k, v)| v.as_str().map(|s| (k, s.to_string())))
                        .collect()
                })
                .unwrap_or_default();
            let scope = claims::scope_of_claim(&c);
            (c, scope, theirs)
        })
        .collect();
    let mut obs = Observation {
        window_start,
        cit_window: cit_covered.clone(),
        ..Default::default()
    };
    for f in changed {
        if contract_generated(p, &f) {
            continue;
        }
        let cur = now.get(&f).cloned();
        let mut t2_violation = false;
        if os_managed(p, &f) {
            // the OS's own writes are recognised by their seal; an in-window CIT may rewrite OS-written records
            // (e.g. propagation marks), which is its governed change, not the worker's
            if !classify_into(p, &f, &mut obs, &legacy_unsealed) {
                continue;
            }
            if cit_covered.contains(&f) {
                obs.t2_violations.pop();
                obs.cit_covered.insert(f);
                continue;
            }
            t2_violation = true;
        } else if cit_covered.contains(&f) {
            obs.cit_covered.insert(f.clone());
            obs.observed.push(f);
            continue;
        }
        if let Some((rid, task, _)) = closed.iter().find(|(_, _, m)| m.get(&f) == Some(&cur)) {
            if t2_violation {
                obs.t2_violations.pop();
            }
            obs.attributed
                .push(json!({"path": f, "to": task, "via": "closed_report", "report": rid}));
            continue;
        }
        if !claims::path_in_scope(&own_scope, &f) {
            if let Some((c, _, _)) = others.iter().find(|(_, scope, theirs)| {
                claims::path_in_scope(scope, &f) && theirs.get(&f) != cur.as_ref()
            }) {
                if t2_violation {
                    obs.t2_violations.pop();
                }
                obs.attributed.push(json!({"path": f, "to": c["task_id"], "via": "live_claim", "session": c["session_id"]}));
                continue;
            }
        }
        obs.baseline_of.insert(f.clone(), baseline.get(&f).cloned());
        obs.current_of.insert(f.clone(), cur);
        obs.observed.push(f);
    }
    // paths an in-window CIT wrote whose content has changed since: no longer the CIT's governed change
    let cit_superseded: Vec<String> = cit_writes
        .keys()
        .filter(|k| !cit_covered.contains(*k) && obs.observed.contains(*k))
        .cloned()
        .collect();
    obs.evidence = json!({"baseline": format!("claim baseline {} (commit {})", doc["at"].as_str().unwrap_or("?"), doc["commit"].as_str().unwrap_or("?")),
        "observed": obs.observed, "carried": doc["carried"], "attributed_elsewhere": obs.attributed, "cit_covered": obs.cit_covered,
        "cit_writes_changed_since": cit_superseded, "cit_coverage": "content-bound (cit::binding::verified_writes)",
        "t2_violations": obs.t2_violations, "os_managed_bound": obs.os_bound, "os_managed_unbound": obs.os_unbound});
    obs
}

/// Every path with uncommitted changes (tracked files differing from HEAD, and untracked files not ignored), one
/// entry per file, from NUL-separated path-only git output (no porcelain status columns to mis-slice).
fn uncommitted_paths(p: &Project) -> Vec<String> {
    let mut out: BTreeSet<String> = BTreeSet::new();
    for args in [
        &["diff", "--name-only", "--no-renames", "-z", "HEAD"][..],
        &["ls-files", "--others", "--exclude-standard", "-z"][..],
    ] {
        let (c, stdout, _) = p.git(args);
        if c == 0 {
            out.extend(
                stdout
                    .split('\0')
                    .map(|s| s.trim_matches('\n'))
                    .filter(|s| !s.is_empty())
                    .filter(|s| !s.starts_with(&format!("{}/", crate::paths::STATE_DIR)))
                    .map(|s| s.to_string()),
            );
        }
    }
    out.into_iter().collect()
}

/// Mutations observed since the claim baseline (added/modified/deleted), excluding the OS's own provable writes and
/// changes attributed to other claims or closes (see [`observe`]).
pub fn observed_mutations(p: &Project, id: &str) -> (Vec<String>, Value) {
    let store = RecordStore::load(&p.root);
    match store.get(id) {
        Some(t) => {
            let o = observe(p, &store, t);
            (o.observed, o.evidence)
        }
        None => (vec![], json!({"baseline": "unknown task"})),
    }
}

/// The mutation scope the task's claim reserved when it was granted (None when there is no claim with a recorded
/// scope, or the reservation is unrestricted). The close is held to it: a task record widened after the claim was
/// granted cannot widen what the claim may close with — the reservation is what other sessions' claims were
/// checked against.
pub fn reserved_scope(p: &Project, t: &Record) -> Option<Vec<String>> {
    let c = claims::get(p, &t.id()).ok().flatten()?;
    if c["scope"].is_null() {
        return None;
    }
    let s = claims::scope_of_claim(&c);
    if s.iter().any(|x| x == claims::UNRESTRICTED) {
        None
    } else {
        Some(s)
    }
}

/// Mutation-scope check for a task: forbidden paths, kernel, contract-prohibited paths, and (when allowed_paths is
/// declared) anything outside it — or outside the scope its claim reserved, or outside the contract recorded in its
/// sealed claim baseline — that is not in `governed`: the paths a CIT executed inside this task's claim window
/// touched ([`cit_window_paths`]). `claimed` is the contract as claimed (`None` when there is no bound baseline).
pub fn scope_violations(
    p: &Project,
    task: &crate::records::Record,
    files: &[String],
    governed: &BTreeSet<String>,
) -> Vec<String> {
    let claimed = bound_baseline(p, &task.id()).map(|d| d["contract"].clone());
    scope_violations_with(p, task, files, governed, claimed.as_ref())
}

fn str_list(v: Option<&Value>) -> Vec<String> {
    v.and_then(|x| x.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default()
}

fn scope_violations_with(
    p: &Project,
    task: &crate::records::Record,
    files: &[String],
    governed: &BTreeSet<String>,
    claimed: Option<&Value>,
) -> Vec<String> {
    let reserved = reserved_scope(p, task);
    let allowed = task.list("allowed_paths");
    let claimed_allowed = str_list(claimed.and_then(|c| c.get("allowed_paths")));
    let mut forbidden = task.list("forbidden_paths");
    for f in str_list(claimed.and_then(|c| c.get("forbidden_paths"))) {
        if !forbidden.contains(&f) {
            forbidden.push(f);
        }
    }
    forbidden.push("governance/kernel/**".into());
    let prohibited: Vec<String> = p
        .contract()
        .rules
        .iter()
        .filter(|r| r.get("mutation").and_then(|m| m.as_str()) == Some("prohibited"))
        .filter_map(|r| {
            r.get("pattern")
                .and_then(|x| x.as_str())
                .map(|s| s.to_string())
        })
        .collect();
    let mut out = vec![];
    for f in files {
        if forbidden.iter().any(|pat| glob_match(pat, f)) {
            out.push(format!("{f}: forbidden path"));
            continue;
        }
        if prohibited.iter().any(|pat| glob_match(pat, f)) {
            out.push(format!(
                "{f}: mutation prohibited by the repository contract"
            ));
            continue;
        }
        if governed.contains(f) {
            continue;
        }
        if !allowed.is_empty() && !allowed.iter().any(|pat| glob_match(pat, f)) {
            out.push(format!(
                "{f}: outside allowed_paths {allowed:?} and not governed by a CIT executed while this task was claimed"
            ));
            continue;
        }
        if !claimed_allowed.is_empty() && !claimed_allowed.iter().any(|pat| glob_match(pat, f)) {
            out.push(format!(
                "{f}: outside the allowed_paths {claimed_allowed:?} the task had when it was claimed (the task record was changed during the claim)"
            ));
            continue;
        }
        if let Some(r) = &reserved {
            if !claims::path_in_scope(r, f) {
                out.push(format!(
                    "{f}: outside the scope {r:?} the task's claim reserved (the task record was widened after the claim was granted; release and claim again to reserve the new scope)"
                ));
            }
        }
    }
    out
}

/// Whether the task contract permits its output to land in the production tree (framework §42: an experiment
/// specifies `production_merge_allowed: false`; an `experiment` task never merges, whatever its record says).
pub fn production_merge_allowed(t: &Record) -> bool {
    t.data
        .get("production_merge_allowed")
        .and_then(|v| v.as_bool())
        .unwrap_or(true)
        && t.get("class") != "experiment"
}

/// Is `path` in the production tree? Everything is, except the governance record space (the repository contract's
/// `spec`, `archive` and `governance` roots) and paths the contract classifies as evidence, narrative, historical,
/// generated, derived or runtime data — so a project gives experiments a sandbox by classifying it (e.g.
/// `{pattern: "experiments/**", class: evidence}`), a governed change to the repository contract.
pub fn is_production_path(p: &Project, path: &str) -> bool {
    let c = p.contract();
    let d = c.decide(path);
    if ["spec", "archive", "governance"]
        .iter()
        .any(|r| path.starts_with(&c.root(r)))
    {
        return false;
    }
    !matches!(
        d.class().as_str(),
        "evidence" | "narrative" | "historical" | "generated" | "derived" | "runtime-data"
    )
}

/// **Close a task with evidence** (framework §13, §64; Contract v3:560-569, W5, O1/O4, L3).
///
/// The worker's structured return *is* the close report (the consumption receipt, BC-P2-20). The checks run in this
/// order, and the order is deliberate — the first refusal is the one reported:
///
/// | # | check | refusal | `--force` (L3+) |
/// |---|---|---|---|
/// | 1 | normalise the worker return (`context::receipt::report_from_worker_return`, lossless) | — | — |
/// | 2 | another session's live claim | `TASK_CLAIMED` | overridden, recorded |
/// | 3 | evidence payload: `tests.status` allowed by TEST_POLICY, `work_completed` present | `EVIDENCE_REQUIRED` | no |
/// | 4 | the claim: held by this session, from its working tree | `CLAIM_REQUIRED`, `CLAIM_WORKTREE_MISMATCH` | overridden, recorded |
/// | 5 | the claim baseline is the sealed one the claim wrote (T2) | `CLAIM_BASELINE_UNBOUND` | overridden (git's uncommitted view), recorded |
/// | 6 | designated role, as recorded now and as claimed | `ROLE_NOT_DESIGNATED` | overridden, recorded |
/// | 7 | independence from recorded authorship (BC-P2-34) | `INDEPENDENCE_VIOLATION` | overridden, recorded |
/// | 8 | every governing Human Decision Gate authorises the work (BC-P2-12) | `GATE_NOT_AUTHORISED` | **no**: a human gate is not an L3 decision |
/// | 9 | observed mutations: declared, in scope (as recorded and as claimed), and no change to OS-written state that no OS operation produced (`t2::classify_path`, BC-P2-09) | `MUTATION_SCOPE_VIOLATION` | no |
/// | 10 | production-merge permission | `PRODUCTION_MERGE_NOT_ALLOWED` | no |
/// | 10a | material changes made inside the task complete only through change control ([`material_changes`], BC-P2-13) | `MATERIAL_CHANGE_REQUIRES_CIT` | no |
/// | 10b | an experiment task is linked to an OS-written experiment with a recorded run (`lifecycle::experiment::task_lifecycle_refusal`, J2) | `EXPERIMENT_LIFECYCLE_REQUIRED` | overridden, recorded |
/// | 11 | index pins and freshness | `INDEX_PIN_MISMATCH`, `INDEX_STALE` | stale only (degraded) |
/// | 12 | the consumption receipt against the manifest and packet (`context::receipt::require_valid`, W5) | `RECEIPT_INVALID` | no |
/// | 12a | the inputs are current and a re-test flag is backed by re-test evidence (`cit::propagation::require_current_inputs`, BC-P2-04) | `INPUTS_STALE`, `RETEST_EVIDENCE_REQUIRED` | no |
/// | 13 | the health close gate (`verification::close_gate`): G0 hard-blocks, G2 re-check, governance-evidence currency (O4), product-test outcome from recorded evidence (O1) | `HEALTH_HARD_BLOCK`, `GOVERNANCE_SUITE_STALE`/`_MISSING`, `PRODUCT_TEST*` | currency only (degraded) |
///
/// Why this order: who may close (2, 4-7) and whether the work may complete at all (8) are decided before any
/// evidence is weighed; the repository's own state (9-10b: scope, merge permission, materiality, experiment
/// lifecycle), observed independently of the worker, is weighed before the worker's account of it (12, 12a), so an
/// incomplete receipt never masks an out-of-scope, forged or material mutation; the
/// evidence payload (3) keeps its long-standing place so a malformed report is refused as such; the health gate
/// (13) runs last because it may execute checks and record a governance-suite result, which nothing before it
/// should cause for a close that is refused anyway. After the task is DONE: its report is sealed, a re-test it
/// evidenced is cleared ([`require_current_inputs`](crate::cit::propagation::require_current_inputs)), a revalidation
/// task resolves the completed work it revalidates, and the work its report calls for is generated (BC-P2-24).
pub fn close(
    p: &Project,
    db: &RuntimeDb,
    id: &str,
    report_in: Value,
    force: bool,
) -> Result<Value> {
    control::guard_write(p, "task close")?;
    authority::require(
        p,
        if force {
            "force_close_task"
        } else {
            "close_task"
        },
    )?;
    let pol = p.policies();
    let store = RecordStore::load(&p.root);
    let t = store
        .get(id)
        .filter(|t| t.rtype() == "task")
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    if t.get("task_status") == "DONE" {
        return Err(GovError::new("USAGE", format!("{id} already DONE")));
    }
    // --- 1. the worker's return is the receipt (one contract; lossless mapping of status -> outcome)
    if !report_in.is_object() {
        return Err(GovError::new(
            "EVIDENCE_REQUIRED",
            "the close report must be a JSON object (the worker return / consumption receipt)",
        ));
    }
    let mut report = crate::context::receipt::report_from_worker_return(&report_in);
    // --- 2. another session's live claim is refused first (as before)
    let live_holder = claims::holder(p, id)?;
    if let Some(h) = &live_holder {
        if h["session_id"].as_str() != Some(p.session_id.as_str()) && !force {
            return Err(GovError::new(
                "TASK_CLAIMED",
                format!("{id} is claimed by another session; --force requires L3+"),
            ));
        }
    }
    // --- 3. the evidence payload keeps its precedence so a malformed report keeps its own refusal
    let tests_status = report
        .get("tests")
        .and_then(|x| x.get("status"))
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let allowed = pol.get_list("TEST_POLICY", "task_close_requires_tests_status");
    if !allowed.contains(&tests_status) {
        return Err(GovError::new(
            "EVIDENCE_REQUIRED",
            format!("report.tests.status must be one of {allowed:?} (got '{tests_status}')"),
        ));
    }
    if report
        .get("work_completed")
        .and_then(|v| v.as_str())
        .map(|s| s.is_empty())
        .unwrap_or(true)
    {
        return Err(GovError::new(
            "EVIDENCE_REQUIRED",
            "report.work_completed is required",
        ));
    }
    // --- 4. the claim (BC-P2-15): work is closed by the session that holds it, from the working tree it was claimed in
    let wt = claims::worktree_id(p);
    let claim = claims::get(p, id)?;
    let mut overrides: Vec<Value> = vec![];
    let mut own_claim = false;
    match &claim {
        Some(c) if c["session_id"].as_str() == Some(p.session_id.as_str()) => {
            own_claim = true;
            let cw = c["worktree"].as_str().unwrap_or("");
            if !cw.is_empty() && cw != wt {
                if !force {
                    return Err(GovError::new("CLAIM_WORKTREE_MISMATCH", format!("{id} was claimed from worktree {cw}; close it there — its mutation baseline belongs to that working tree (this is {wt})")).with_details(json!({"claim": c, "closing_worktree": wt})));
                }
                overrides.push(json!({"override": "claim_worktree", "claim_worktree": cw, "closing_worktree": wt}));
            }
        }
        Some(c) if live_holder.is_some() => {
            if !force {
                return Err(GovError::new(
                    "TASK_CLAIMED",
                    format!("{id} is claimed by another session; --force requires L3+"),
                ));
            }
            overrides.push(json!({"override": "claim_holder", "holder": c["session_id"]}));
        }
        _ => {
            if !force {
                return Err(GovError::new("CLAIM_REQUIRED", format!("{id} is not claimed by session {}; claim it first (`gov task claim {id}`) — the claim records the mutation baseline, scope and working tree the close is checked against", p.session_id)).with_details(json!({"task": id, "session": p.session_id, "claim": claim})));
            }
            overrides.push(json!({"override": "no_claim_held", "claim": claim}));
        }
    }
    // --- 5. the claim baseline must be the sealed one the claim wrote: a rewritten baseline would hide mutations
    let baseline = read_baseline(p, id);
    let bound = match &baseline {
        Baseline::Bound(d) => Some(d.clone()),
        _ => None,
    };
    if own_claim && bound.is_none() {
        let state = match &baseline {
            Baseline::Unbound { binding } => json!({"state": "UNBOUND", "t2": binding}),
            _ => json!({"state": "ABSENT"}),
        };
        if !force {
            return Err(GovError::new("CLAIM_BASELINE_UNBOUND", format!("{id}: the claim baseline this close must be checked against is not the one the claim wrote (it is missing, or it was changed outside gov: T2 binding not verified); the observed mutations cannot be established. An L3+ `--force` close is checked against git's uncommitted changes instead and records the override")).with_details(json!({"task": id, "baseline": state})));
        }
        overrides.push(json!({"override": "claim_baseline_unbound", "baseline": state}));
    }
    let claimed_contract = bound.as_ref().map(|d| d["contract"].clone());
    // --- 6. the designated role (BC-P2-14), as recorded now and as claimed
    if let Some(e) = designated_role_refusal(p, t, "close", claimed_contract.as_ref()) {
        if !force {
            return Err(e);
        }
        overrides.push(json!({"override": "designated_role", "designated_role": e.details["designated_role"], "acting_role": p.role}));
    }
    let ctx = DagCtx::new(p, &store);
    // --- 7. independence from recorded authorship (BC-P2-34)
    let conflicts = independence_conflicts(&ctx, &store, t, &p.session_id);
    if !conflicts.is_empty() {
        if !force {
            return Err(independence_refusal(t, "closed", &conflicts));
        }
        overrides.push(json!({"override": "independence", "reasons": conflicts}));
    }
    // --- 8. Human Decision Gates (BC-P2-12): work cannot complete while a governing gate withholds authorisation
    let mut governing = ctx.governing_gates(t);
    if let Some(g) = claimed_contract
        .as_ref()
        .and_then(|c| c["human_gate"].as_str())
        .filter(|g| !g.is_empty())
    {
        if !governing.iter().any(|x| x == g) {
            governing.push(g.to_string());
        }
    }
    let mut gate_states = vec![];
    let mut unauthorised = vec![];
    for g in &governing {
        let a = gates::task_gate_authorisation_in(p, &store, g);
        let v = json!({"gate": g, "authorisation": a.to_value()});
        if !a.authorises() {
            unauthorised.push(
                json!({"gate": g, "authorisation": a.to_value(), "reason": a.blocking_reason(g)}),
            );
        }
        gate_states.push(v);
    }
    if !unauthorised.is_empty() {
        let why: Vec<String> = unauthorised
            .iter()
            .filter_map(|u| u["reason"].as_str().map(|s| s.to_string()))
            .collect();
        return Err(GovError::new("GATE_NOT_AUTHORISED", format!("{id} cannot be completed: {}. Work blocked by a Human Decision Gate completes only after an answer that authorises it (present the gate; the human answers through the authenticated channel); `--force` does not override a human gate", why.join("; "))).with_details(json!({"task": id, "gates": unauthorised})));
    }
    // --- 9. mutation scope (framework §25/§42; verifier H4): the declared manifest ...
    let mut files_changed: Vec<String> = vec![];
    for k in ["files_changed", "outputs_produced"] {
        for f in report
            .get(k)
            .and_then(|v| v.as_array())
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect::<Vec<_>>()
            })
            .unwrap_or_default()
        {
            if !files_changed.contains(&f) {
                files_changed.push(f);
            }
        }
    }
    let obs = observe_against(p, &store, t, bound.as_ref());
    let governed = &obs.cit_window;
    let violations =
        scope_violations_with(p, t, &files_changed, governed, claimed_contract.as_ref());
    if !violations.is_empty() {
        return Err(GovError::new("MUTATION_SCOPE_VIOLATION", format!("task {id} reports mutations outside its contract: {}; route them through a CIT or amend the task contract", violations.join("; "))).with_details(json!({"violations": violations, "allowed_paths": t.list("allowed_paths")})));
    }
    // ... and the mutations actually observed in the repository since the claim baseline (verifier M-N4): undeclared
    // or out-of-scope changes fail closed unless a CIT executed inside this claim window governs them, and a change
    // to OS-written state that no OS operation produced (T2) fails closed whatever the report says;
    // self-attestation is never sufficient
    let observed = obs.observed.clone();
    let evidence = obs.evidence.clone();
    let undeclared: Vec<String> = observed
        .iter()
        .filter(|f| !files_changed.contains(f) && !governed.contains(*f))
        .cloned()
        .collect();
    let observed_violations =
        scope_violations_with(p, t, &observed, governed, claimed_contract.as_ref());
    if !undeclared.is_empty() || !observed_violations.is_empty() || !obs.t2_violations.is_empty() {
        let t2_paths: Vec<String> = obs
            .t2_violations
            .iter()
            .filter_map(|v| v["path"].as_str().map(|s| s.to_string()))
            .collect();
        return Err(GovError::new("MUTATION_SCOPE_VIOLATION", format!("task {id}: the repository shows mutations the report does not declare or the contract does not allow (undeclared: {undeclared:?}; out of scope: {observed_violations:?}; OS-written state changed outside a gov operation: {t2_paths:?}); declare every change in files_changed, route out-of-scope changes through a CIT, amend the task contract, and restore OS-written records (gates, decisions, reports, CITs) from version control — they are written only by gov operations")).with_details(json!({"undeclared": undeclared, "out_of_scope": observed_violations, "t2_violations": obs.t2_violations, "reported": files_changed, "observed": observed, "evidence": evidence})));
    }
    // --- 10. production-merge permission (BC-P2-14; Contract v3:569, :614), as recorded now and as claimed
    let merge_allowed = production_merge_allowed(t)
        && claimed_contract
            .as_ref()
            .map(|c| {
                c["production_merge_allowed"].as_bool().unwrap_or(true)
                    && c["class"] != "experiment"
            })
            .unwrap_or(true);
    if !merge_allowed {
        let landed: Vec<String> = observed
            .iter()
            .filter(|f| !governed.contains(*f) && is_production_path(p, f))
            .cloned()
            .collect();
        if !landed.is_empty() {
            return Err(GovError::new("PRODUCTION_MERGE_NOT_ALLOWED", format!("task {id} ({}) may not merge into production (production_merge_allowed: false) but its mutations landed in the production tree: {landed:?}; keep experimental output outside the production tree (spec/experiments/** or a path the repository contract classifies as evidence) and promote it through a CIT", t.get("class"))).with_details(json!({"task": id, "class": t.get("class"), "production_paths": landed, "observed": observed, "evidence": evidence})));
        }
    }
    // --- 10a. material changes made inside the task (BC-P2-13 in-task half; WS-4 R2-4): a material change completes
    //          only through CIT-P/CIT-E — observed, classified by what changed (never by a label), and accepted only
    //          when an in-window CIT wrote exactly this content, or when it is the task's contracted authoring
    let task_class = claimed_contract
        .as_ref()
        .and_then(|c| c["class"].as_str())
        .filter(|c| !c.is_empty())
        .map(|c| c.to_string())
        .unwrap_or_else(|| t.get("class"));
    let base_commit = bound
        .as_ref()
        .and_then(|d| d["commit"].as_str())
        .filter(|c| !c.is_empty())
        .map(|c| c.to_string());
    let material = material_changes(p, t, &task_class, &obs, base_commit.as_deref());
    if !material.refused.is_empty() {
        let what: Vec<String> = material
            .refused
            .iter()
            .map(|f| {
                format!(
                    "{} {} ({})",
                    f["class"].as_str().unwrap_or("?"),
                    f["subject"].as_str().unwrap_or("?"),
                    f["path"].as_str().unwrap_or("?")
                )
            })
            .collect();
        return Err(GovError::new("MATERIAL_CHANGE_REQUIRES_CIT", format!("task {id} made material change(s) outside change control: {}. Contract v3:638-647 / framework §47-48: a material change completes only through CIT-P/CIT-E, whatever task it is made in. Restore these paths and propose the change as a Change-Impact Transaction (`gov cit propose --targets … --manifest …`, simulate, approve, execute) while this task is claimed — its recorded writes then cover exactly this content — or narrow the work to non-material changes", what.join("; "))).with_details(json!({"task": id, "class": task_class, "refused": material.refused, "accepted": material.accepted, "rule_source": "cit::materiality (kernel floor) at task close", "remediation": "gov cit propose / simulate / approve / execute inside the claim window"})));
    }
    // --- 10b. experiments are governed through their lifecycle (WS-10 IP-WS10-11, Contract v3 J2): an experiment task
    //          closes only when linked to an OS-written experiment record with a recorded run
    if let Some(e) = crate::lifecycle::experiment::task_lifecycle_refusal(
        &crate::lifecycle::Ctx::new(p, &store),
        t,
    ) {
        if !force {
            return Err(e);
        }
        overrides
            .push(json!({"override": "experiment_lifecycle", "code": e.code, "reason": e.message}));
    }
    let unobserved: Vec<String> = files_changed
        .iter()
        .filter(|f| !observed.contains(f))
        .cloned()
        .collect();
    // --- 11. freshness (content and pins)
    let fr = freshness(p);
    let stale_count = fr.stale.len() + fr.added.len() + fr.removed.len();
    let max_stale = pol.get_i64(
        "MEMORY_POLICY",
        "freshness.max_stale_artifacts_on_task_close",
        0,
    ) as usize;
    let on_stale = pol.get_str("MEMORY_POLICY", "freshness.on_stale_close", "fail");
    let mut degraded: Vec<Value> = vec![];
    if !fr.pin_mismatch.is_empty() {
        return Err(GovError::new("INDEX_PIN_MISMATCH", format!("the index was built with different pins than policy declares ({}); run `gov rebuild-memory` before closing", fr.pin_mismatch.join("; "))));
    }
    if !fr.manifest_present || stale_count > max_stale {
        if on_stale == "fail" && !force {
            return Err(GovError::new("INDEX_STALE", format!("required index is stale ({stale_count} artefacts changed since last build); run `gov rebuild-memory --incremental` before closing")).with_details(json!({"stale": fr.stale, "added": fr.added, "removed": fr.removed})));
        }
        degraded.push(json!(format!("index stale ({stale_count})")));
    }
    // --- 12. the consumption receipt (BC-P2-20, W5): validated against the manifest and the packet it names
    report = require_receipt(p, &store, t, &report)?;
    // --- 12a. current inputs (BC-P2-04 close side; WS-4 R2-1): work done against an input that has changed since it
    //          was consumed cannot close, and a re-test flag is cleared only by evidence of the re-test against the
    //          changed inputs (never by closing, never by an index rebuild)
    let currency = crate::cit::propagation::require_current_inputs(p, &store, id, &report)?;
    // --- 13. the health close gate (G0 hard-block, G2 re-check, O4 currency, O1 product tests from evidence)
    // what this task touched: what it declares and what it was observed to change — not the paths an in-window CIT
    // changed, which are that CIT's governed mutations (its own G4 tier covers them)
    let mut touched: Vec<String> = files_changed.clone();
    for f in &observed {
        if !touched.contains(f) && !obs.cit_covered.contains(f) {
            touched.push(f.clone());
        }
    }
    let mut task_value = t.data.clone();
    task_value["id"] = json!(id);
    let gate = crate::verification::close_gate(p, &task_value, &report, &touched, force)?;
    if let Some(d) = gate["degraded"].as_array() {
        degraded.extend(d.iter().cloned());
    }
    // --- mint the report (sealed: an OS-written T2 record) and complete the task
    let closed_at = now_iso();
    let rpt_id = store.next_id("report");
    let robj = report.as_object_mut().unwrap();
    robj.insert("task".into(), json!(id));
    robj.insert("session".into(), json!(p.session_id));
    robj.insert("role".into(), json!(p.role));
    robj.entry("outcome").or_insert(json!("success"));
    robj.entry("evidence").or_insert(json!([]));
    if !degraded.is_empty() {
        robj.insert("degraded".into(), json!(degraded));
    }
    robj.insert("state_class".into(), json!("EVIDENCE"));
    robj.insert("observed_files_changed".into(), json!(observed));
    robj.insert(
        "close_gate".into(),
        json!({"governance_affecting": gate["governance_affecting"], "reasons": gate["reasons"], "g2": gate["g2"], "human_gates": gate_states}),
    );
    // the content this close accepts, so a later close in the same working tree can tell this task's accepted
    // changes from its own, and so recorded authorship names exactly what was accepted
    robj.insert(
        "mutation_evidence".into(),
        json!({"baseline": evidence["baseline"], "baseline_sealed": bound.is_some(), "reported_but_unchanged": unobserved, "closed_at": closed_at,
            "observed_hashes": obs.current_of, "cit_covered": obs.cit_covered, "attributed_elsewhere": obs.attributed,
            "os_managed_bound": obs.os_bound, "os_managed_unbound": obs.os_unbound,
            "carried": evidence["carried"], "claim": claim.as_ref().map(|c| json!({"session": c["session_id"], "role": c["role"], "worktree": c["worktree"], "branch": c["branch"], "head": c["head"], "scope": c["scope"], "claimed_at": c["claimed_at"]})),
            "claimed_contract": claimed_contract, "closing_worktree": wt, "overrides": overrides,
            "material_changes": {"accepted": material.accepted.clone(), "classified_paths": material.classified, "rule_source": "cit::materiality at task close (BC-P2-13)"}}),
    );
    if currency["clears_retest"].as_bool() == Some(true) {
        robj.insert(
            "revalidated_inputs".into(),
            currency["revalidated_inputs"].clone(),
        );
    }
    let title = format!("Report for {id}: {}", t.title());
    let mut rec = new_record("report", &rpt_id, &title, Value::Object(robj.clone()));
    p.schemas()
        .validate("report", &rec.data, &format!("({rpt_id})"))?;
    crate::t2::seal_record(&mut rec, "task close")?;
    save_record(&p.root, &rec)?;
    let produced: Vec<String> = observed
        .iter()
        .filter(|f| !obs.cit_covered.contains(*f))
        .cloned()
        .collect();
    let mut store2 = RecordStore::load(&p.root);
    let tr = store2.get_mut(id).unwrap();
    let tr_verified = crate::t2::verify_record(tr).is_verified();
    tr.set("task_status", json!("DONE"));
    tr.set("closed_by_report", json!(rpt_id));
    tr.set("updated", json!(today()));
    tr.set("closed_at", json!(closed_at));
    // the task -> output edges (W5 line 1126 / W8): what the task actually produced, as observed
    tr.set("outputs_produced", json!(produced));
    tr.set(
        "status_source",
        json!({"operation": "task close", "status": "DONE", "session": p.session_id, "role": p.role, "at": closed_at, "report": rpt_id}),
    );
    // a re-test flag is cleared only by the evidence `require_current_inputs` accepted (WS-4 R2-1): the re-tested
    // inputs are recorded, and the staleness it resolved says how
    if currency["clears_retest"].as_bool() == Some(true) {
        tr.set("retest_required", json!(false));
        tr.set("revalidated_inputs", currency["revalidated_inputs"].clone());
        let mut s = tr.data.get("staleness").cloned().unwrap_or(json!({}));
        if s.is_object() {
            s["stale"] = json!(false);
            s["resolved"] = json!({"by": "task close with re-test evidence", "report": rpt_id, "inputs": currency["revalidated_inputs"], "at": closed_at});
            tr.set("staleness", s);
        }
    }
    save_task(p, tr, tr_verified, "task close")?;
    // a revalidation task's close revalidates the completed work it names (BC-P2-04 / BC-P2-24: "a revalidation
    // task's close clears the revalidation of the task it names")
    let revalidated = resolve_revalidation(p, t, &rpt_id, &closed_at);
    let _ = claims::release(p, id, &p.session_id, force);
    let _ = std::fs::remove_file(claim_tree_path(p, id));
    let _ = std::fs::remove_file(carried_path(p, id));
    let ck = checkpoints::create(
        p,
        db,
        json!({"task": id, "trigger": "task_transition", "last_completed_step": format!("closed {id}"), "next_action": "gov continue", "tests_status": tests_status, "files_changed": files_changed, "observed_files_changed": observed}),
    )?;
    let _ = crate::memory::indexer::rebuild(
        p,
        crate::memory::indexer::IndexOptions {
            incremental: true,
            ..Default::default()
        },
    );
    // governed work the completed work calls for (its discoveries, unresolved items and proposed decisions) is
    // generated now, linked to the sealed report (BC-P2-24)
    let generated = crate::orchestration::generation::reconcile(
        p,
        &crate::orchestration::generation::Options::triggered_by("task close"),
    )
    .unwrap_or_else(|e| json!({"error": {"code": e.code, "message": e.message}}));
    let mut out = json!({"task": id, "task_status": "DONE", "report": rpt_id, "checkpoint": ck["id"], "degraded": degraded, "overrides": overrides,
               "receipt_validation": robj["receipt_validation"], "close_gate": {"governance_affecting": gate["governance_affecting"], "g2": gate["g2"]}});
    if currency["clears_retest"].as_bool() == Some(true) {
        out["revalidated_inputs"] = currency["revalidated_inputs"].clone();
    }
    if !revalidated.is_null() {
        out["revalidated_task"] = revalidated;
    }
    if !material.accepted.is_empty() {
        out["material_changes_accepted"] = json!(material.accepted);
    }
    out["generated_work"] = crate::orchestration::generation::summary(&generated);
    Ok(out)
}

/// A revalidation task (`revalidates: <task>`, generated by upstream-change propagation or the work generator)
/// revalidates the completed work it names when it closes: that task's `revalidation` becomes resolved, its re-test
/// flag and staleness are cleared, each naming the closing report. Returns what was resolved (`Null` when nothing).
fn resolve_revalidation(p: &Project, t: &Record, report: &str, at: &str) -> Value {
    let target = t.get("revalidates");
    if target.is_empty() {
        return Value::Null;
    }
    let mut store = RecordStore::load(&p.root);
    let Some(r) = store.get_mut(&target).filter(|r| r.rtype() == "task") else {
        return Value::Null;
    };
    let required = r.data["revalidation"]["required"].as_bool() == Some(true)
        || r.data.get("retest_required").and_then(|v| v.as_bool()) == Some(true);
    if !required || r.get("task_status") != "DONE" {
        return Value::Null;
    }
    let was_verified = crate::t2::verify_record(r).is_verified();
    let mut rv = r.data.get("revalidation").cloned().unwrap_or(json!({}));
    if !rv.is_object() {
        rv = json!({});
    }
    rv["required"] = json!(false);
    rv["resolved_by"] = json!({"task": t.id(), "report": report, "at": at});
    r.set("revalidation", rv);
    r.set("retest_required", json!(false));
    let mut s = r.data.get("staleness").cloned().unwrap_or(json!({}));
    if s.is_object() {
        s["stale"] = json!(false);
        s["resolved"] =
            json!({"by": "revalidation task", "task": t.id(), "report": report, "at": at});
        r.set("staleness", s);
    }
    r.set("updated", json!(today()));
    match save_task(p, r, was_verified, "task close (revalidation)") {
        Ok(()) => json!({"task": target, "resolved_by": t.id(), "report": report}),
        Err(e) => json!({"task": target, "error": {"code": e.code, "message": e.message}}),
    }
}

/// Task classes contracted to change the product's behaviour (its source): a behaviour change to product source made
/// by a task of any other class is outside its contract, so it is material for it (BC-P2-13).
pub const SOURCE_CHANGING_CLASSES: &[&str] = &[
    "implementation",
    "integration",
    "refactor",
    "repair",
    "performance",
    "security",
    "experiment",
];

/// Record types whose **initial authoring** is specification work: a new record of one of these types that no
/// earlier record is replaced by is the output a specification-producing task is contracted to make, not a change to
/// existing authority (there is no consumer whose basis it changes).
pub const AUTHORED_SPEC_TYPES: &[&str] = &[
    "requirement",
    "scenario",
    "test-obligation",
    "feature",
    "data",
];

/// Material classes an initially authored specification record may carry.
const AUTHORING_CLASSES: &[&str] = &[
    "behaviour_change",
    "acceptance_criteria_change",
    "data_migration",
];

/// The in-task materiality verdict of a close ([`material_changes`]).
#[derive(Debug, Clone, Default)]
pub struct MaterialCheck {
    /// Findings the close must refuse: `{path, class, subject, rule, evidence}`.
    pub refused: Vec<Value>,
    /// Material findings accepted, each with why (`via`).
    pub accepted: Vec<Value>,
    /// Paths classified.
    pub classified: usize,
}

/// **Material changes made inside a task (BC-P2-13 close side; WS-4 R2-4; Contract v3:446, :638-647; framework
/// §47-48).** Every path the task was observed to change since its claim is classified by what changed
/// (`cit::materiality::classify_paths` against the claim-time commit), never by the task's label. A finding that
/// must pass change control (`requires_cit_in_task`, and a behaviour change to product source made by a task not
/// contracted to change it, [`SOURCE_CHANGING_CLASSES`]) is accepted only when:
///
/// 1. **a CIT governed exactly this change** — a transaction committed inside the claim window wrote the path and its
///    content is still what that CIT left (`cit::binding::verified_writes`, [`cit_window_writes`]); or
/// 2. **it is initial authoring** — a specification record of [`AUTHORED_SPEC_TYPES`] that did not exist when the
///    task was claimed and supersedes nothing, created by a task that produces specification
///    (`dag::produces_feature_specification`), carrying only [`AUTHORING_CLASSES`]; or
/// 3. **it is the task's own readiness cell** — a readiness gap task changing only its cell of its feature's
///    `readiness` map.
///
/// Everything else is refused. Architecture, interface, security, governance, infrastructure and migration changes
/// are never exempt: they are material whatever task makes them and however new the file is.
pub fn material_changes(
    p: &Project,
    t: &Record,
    task_class: &str,
    obs: &Observation,
    base_commit: Option<&str>,
) -> MaterialCheck {
    let mut out = MaterialCheck::default();
    let producer = crate::orchestration::dag::produces_feature_specification(t)
        || crate::orchestration::dag::SPECIFICATION_PRODUCING_CLASSES.contains(&task_class);
    for path in &obs.observed {
        if obs.cit_covered.contains(path) {
            out.accepted.push(json!({"path": path, "via": "a CIT committed inside the claim window wrote exactly this content (verified writes)"}));
            continue;
        }
        out.classified += 1;
        let m = crate::cit::materiality::classify_paths(p, std::slice::from_ref(path), base_commit);
        let created = matches!(obs.baseline_of.get(path), Some(None));
        let current = std::fs::read_to_string(p.root.join(path))
            .ok()
            .and_then(|txt| crate::records::parse_record_text(&txt, path));
        for f in &m.findings {
            let outside_contract = f.class == "behaviour_change"
                && f.rule == "product source"
                && !SOURCE_CHANGING_CLASSES.contains(&task_class);
            if !f.requires_cit_in_task && !outside_contract {
                continue;
            }
            let row = json!({"path": path, "class": f.class, "subject": f.subject, "rule": f.rule, "evidence": f.evidence});
            // 2. initial authoring of specification by specification-producing work
            let authored = producer
                && created
                && AUTHORING_CLASSES.contains(&f.class)
                && match &current {
                    Some(r) => {
                        AUTHORED_SPEC_TYPES.contains(&r.rtype().as_str())
                            && r.list("supersedes").is_empty()
                            && !r.relations().iter().any(|(ty, _)| ty == "SUPERSEDES")
                    }
                    // an executable acceptance criterion (Gherkin) newly written by specification work
                    None => f.rule == "executable acceptance criteria",
                };
            if authored {
                let mut a = row.clone();
                a["via"] = json!("initial authoring by specification-producing work (created in this claim window, supersedes nothing)");
                out.accepted.push(a);
                continue;
            }
            // 3. the readiness gap task's own cell of its feature
            if own_readiness_cell_only(p, t, path, current.as_ref(), base_commit) {
                let mut a = row.clone();
                a["via"] = json!(format!(
                    "the readiness gap task's own cell ({}) of its feature",
                    t.get("readiness_cell")
                ));
                out.accepted.push(a);
                continue;
            }
            out.refused.push(row);
        }
    }
    out
}

/// Did a readiness gap task change nothing of `path` but its own readiness cell of its own feature?
fn own_readiness_cell_only(
    p: &Project,
    t: &Record,
    path: &str,
    current: Option<&Record>,
    base_commit: Option<&str>,
) -> bool {
    let (cell, feature) = (t.get("readiness_cell"), t.get("feature"));
    let Some(cur) = current else {
        return false;
    };
    if cell.is_empty() || feature.is_empty() || cur.id() != feature || cur.rtype() != "feature" {
        return false;
    }
    let base = base_commit.unwrap_or("HEAD");
    let Some(before) =
        crate::cit::materiality::git_output(&p.root, &["show", &format!("{base}:{path}")])
            .and_then(|txt| crate::records::parse_record_text(&txt, path))
    else {
        return false;
    };
    let (b, a) = (&before.data, &cur.data);
    let keys: BTreeSet<String> = b
        .as_object()
        .into_iter()
        .chain(a.as_object())
        .flat_map(|m| m.keys().cloned())
        .collect();
    for k in keys {
        if b.get(&k) == a.get(&k)
            || crate::cit::materiality::BOOKKEEPING_FIELDS.contains(&k.as_str())
        {
            continue;
        }
        if k != "readiness" {
            return false;
        }
        let strip = |v: Option<&Value>| -> Value {
            let mut m = v.and_then(|x| x.as_object()).cloned().unwrap_or_default();
            m.remove(&cell);
            Value::Object(m)
        };
        if strip(b.get("readiness")) != strip(a.get("readiness")) {
            return false;
        }
    }
    true
}

/// **The consumption receipt at close** (BC-P2-20 close side): `context::receipt::validate` against the task's
/// manifest and the packet the receipt names, refused as `RECEIPT_INVALID` with every error — exactly
/// `receipt::require_valid`, with one rule the task DAG applies too ([`dag::produces_feature_specification`]): a task
/// that produces its feature's specification does not complete *on* the inputs it only inherits from the feature,
/// so an unsatisfied inherited-only input is advisory for it rather than `MANIFEST_UNSATISFIED` (what the task
/// declares itself still binds). Returns the report fields to persist: the canonical receipt merged over the report,
/// plus `receipt_validation`.
fn require_receipt(p: &Project, store: &RecordStore, t: &Record, report: &Value) -> Result<Value> {
    let id = t.id();
    let mut chk = crate::context::receipt::validate(p, store, &id, report)?;
    let mut advisory: Vec<Value> = vec![];
    if dag::produces_feature_specification(t) {
        let m = crate::context::manifest::resolve(p, store, t);
        let inherited_only: BTreeSet<String> = m
            .entries
            .iter()
            .filter(|e| e.required && !e.satisfied())
            .filter(|e| e.sources.iter().all(|s| s.starts_with("feature ")))
            .map(|e| e.id.clone())
            .collect();
        chk.errors.retain(|e| {
            let ids: Vec<String> = e["ids"]
                .as_array()
                .map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(|s| s.to_string()))
                        .collect()
                })
                .unwrap_or_default();
            let only_inherited = (e["code"] == "MANIFEST_UNSATISFIED"
                && !ids.is_empty()
                && ids.iter().all(|i| inherited_only.contains(i)))
                || (e["code"] == "PACKET_BLOCKED"
                    && ids.first().is_some_and(|h| {
                        crate::context::load_packet(p, &id, Some(h))
                            .map(|pk| dag::packet_blocked_only_by_inherited(t, &pk))
                            .unwrap_or(false)
                    }));
            if only_inherited {
                advisory.push(json!({"code": "INHERITED_INPUT_UNSATISFIED", "message": format!("{id} produces its feature's specification; the inputs it only inherits from the feature are not yet satisfied ({}: {})", e["code"].as_str().unwrap_or(""), ids.join(", ")), "ids": ids}));
            }
            !only_inherited
        });
    }
    if !chk.ok() {
        let codes: Vec<String> = chk
            .errors
            .iter()
            .filter_map(|e| e["code"].as_str().map(|s| s.to_string()))
            .collect();
        return Err(GovError::new(
            "RECEIPT_INVALID",
            format!(
                "{id}: the consumption receipt does not trace this completion to its inputs ({}). Remediation: return the fields in the packet's receipt_contract — {}",
                codes.join(", "),
                chk.errors.iter().filter_map(|e| e["message"].as_str()).collect::<Vec<_>>().join(" | ")
            ),
        )
        .with_details(chk.to_value()));
    }
    chk.warnings.extend(advisory);
    let mut out = crate::context::receipt::report_from_worker_return(report);
    if let (Some(o), Some(c)) = (out.as_object_mut(), chk.receipt.as_object()) {
        for (k, v) in c {
            if !v.is_null() {
                o.insert(k.clone(), v.clone());
            }
        }
        let mut summary = chk.summary();
        summary["warnings"] = json!(chk
            .warnings
            .iter()
            .map(|w| w["code"].clone())
            .collect::<Vec<_>>());
        o.insert("receipt_validation".into(), summary);
    }
    Ok(out)
}

/// The enforcement state of a task's contract fields, for consumers that present the contract (the context packet,
/// `gov task show`): resolution of `required_data`, `required_tools` and `required_skills`, the tasks that `blocks`
/// it, the designated role, the production-merge permission, the governing gates and the task's DAG state.
/// Read-only.
pub fn contract_enforcement(p: &Project, store: &RecordStore, t: &Record) -> Value {
    let inputs = crate::orchestration::dag::required_inputs(p, store, t);
    let blocked_by: Vec<Value> = store
        .of_type("task")
        .into_iter()
        .filter(|o| o.list("blocks").contains(&t.id()))
        .map(|o| json!({"task": o.id(), "task_status": o.get("task_status")}))
        .collect();
    let ctx = DagCtx::new(p, store);
    let ev = dag::evaluate(&ctx, t, None);
    json!({"required_data": inputs["required_data"], "required_tools": inputs["required_tools"], "required_skills": inputs["required_skills"],
        "blocked_by": blocked_by, "blocks": t.list("blocks"), "designated_role": t.get("role"),
        "production_merge_allowed": production_merge_allowed(t), "mutation_scope": claims::scope_of_task(t),
        "governing_gates": ev.gates, "dag": {"state": ev.state.as_str(), "reasons": ev.reasons}})
}

/// Production-merge violations present in the working tree, for the governance suite (Contract v3:614 "production
/// merge prohibited where experimental"): for every task whose contract forbids production merge, (a) an open task
/// with a claim baseline whose own observed mutations lie in the production tree — including output committed to
/// git outside the Governance OS after its close was refused — and (b) a closed task whose report records observed
/// production paths. Each finding names the task and the paths. Read-only; hashes the tree only when such a task
/// has a baseline.
pub fn production_merge_findings(p: &Project, store: &RecordStore) -> Vec<Value> {
    let mut out = vec![];
    for t in store.of_type("task") {
        if production_merge_allowed(t) {
            continue;
        }
        let id = t.id();
        let st = t.get("task_status");
        if st == "DONE" {
            let rid = t.get("closed_by_report");
            let landed: Vec<String> = store
                .get(&rid)
                .map(|r| r.list("observed_files_changed"))
                .unwrap_or_default()
                .into_iter()
                .filter(|f| is_production_path(p, f))
                .collect();
            if !landed.is_empty() {
                out.push(json!({"task": id, "class": t.get("class"), "task_status": st, "report": rid, "production_paths": landed,
                    "message": format!("{id} ({}) forbids production merge but its close accepted production paths {landed:?}", t.get("class"))}));
            }
            continue;
        }
        if st == "CANCELLED" || !claim_tree_path(p, &id).exists() {
            continue;
        }
        let obs = observe(p, store, t);
        let landed: Vec<String> = obs
            .observed
            .iter()
            .filter(|f| !obs.cit_window.contains(*f) && is_production_path(p, f))
            .cloned()
            .collect();
        if !landed.is_empty() {
            out.push(json!({"task": id, "class": t.get("class"), "task_status": st, "production_paths": landed,
                "message": format!("{id} ({}) forbids production merge but its output is in the production tree: {landed:?}", t.get("class"))}));
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    /// DONE, CLAIMED and IN_PROGRESS are reached only through close / claim: `task create` and `task status` refuse
    /// them with the route to take; every other status is settable.
    #[test]
    fn operation_only_statuses_name_their_route() {
        for s in ["DONE", "CLAIMED", "IN_PROGRESS"] {
            let e = operation_only(s).expect(s);
            assert_eq!(e.code, "TASK_STATUS_REQUIRES_OPERATION");
            assert!(e.details["route"]
                .as_str()
                .unwrap()
                .starts_with("gov task "));
        }
        for s in [
            "DRAFT",
            "READY",
            "BLOCKED",
            "REVIEW",
            "CANCELLED",
            "WAITING_HUMAN",
        ] {
            assert!(operation_only(s).is_none(), "{s}");
        }
    }

    /// The evidence a task relies on — what its influence backlinks name (IP-WS10-13) — and the checks it declares it
    /// remedies (availability rule) are read from its contract fields.
    #[test]
    fn cited_evidence_and_remedies_are_read_from_the_contract() {
        let t = crate::records::new_record(
            "task",
            "TASK-0001",
            "t",
            json!({"derived_from": ["RES-0001", "EXP-0001"], "required_inputs": ["RES-0001", {"id": "D-0001", "reason": "r"}],
                   "optional_inputs": [{"id": "RES-0002"}], "relations": [{"type": "CONSUMES", "target": "RES-0003"}, {"type": "AFFECTS", "target": "F-0001"}],
                   "remedies": ["graph_integrity", " ", "D011"]}),
        );
        assert_eq!(
            cited_evidence_ids(&t),
            vec!["RES-0001", "EXP-0001", "D-0001", "RES-0002", "RES-0003"]
        );
        assert_eq!(remedies_of(&t.data), vec!["graph_integrity", "D011"]);
    }

    #[test]
    fn independent_work_is_recognised_by_class_role_or_readiness_cell() {
        let t = |f: Value| crate::records::new_record("task", "TASK-0001", "t", f);
        assert!(independent_work(&t(json!({"class": "test-design"}))));
        assert!(independent_work(&t(
            json!({"class": "data", "role": "data-author"})
        )));
        assert!(independent_work(&t(
            json!({"class": "specification", "readiness_cell": "independent_acceptance_tests"})
        )));
        assert!(!independent_work(&t(
            json!({"class": "implementation", "role": "backend-engineer"})
        )));
    }
}
