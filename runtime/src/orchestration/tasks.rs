//! Task contracts (framework §42), creation, status transitions and evidence-gated close (§13, §64).
//! Every mutating path is authority-checked (AUTHORITY_POLICY.authority_levels_required) and task close enforces the
//! task's contract (Contract v3:560-569):
//!
//! * **claim** (BC-P2-15) — granted atomically to one session with the task's mutation scope and the session's
//!   working tree recorded ([`crate::orchestration::claims`]); the task's designated `role` binds who may claim it;
//! * **close** — only by the session holding the claim, from the working tree it was claimed in, in the designated
//!   role (an L3+ `--force` records each override it uses);
//! * **path scope** (BC-P2-14) — the mutations observed since the task's claim baseline must be declared and inside
//!   `allowed_paths` / outside `forbidden_paths`, unless a Change-Impact Transaction **executed while the task was
//!   claimed** touched that path (a CIT committed before the claim covers nothing for this task). A claim baseline is
//!   never reset by re-claiming: a renewal keeps it, and the mutations of an earlier, released claim window are
//!   carried into the next baseline, so releasing and re-claiming cannot launder a change;
//! * **production merge** (BC-P2-14) — a task whose contract forbids production merge (every `experiment` task)
//!   cannot close with mutations in the production tree ([`is_production_path`]); promotion into production goes
//!   through a CIT.
//!
//! `blocks`, `required_data`, `required_tools` and `required_skills` gate readiness in the DAG
//! ([`crate::orchestration::dag`]).
use crate::authority;
use crate::checkpoints;
use crate::memory::claims::ClaimRequest;
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::orchestration::{claims, control, gates};
use crate::records::{new_record, save_record, Record, RecordStore};
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
/// Stored statuses from which a task may be claimed.
const CLAIMABLE: &[&str] = &["READY", "CLAIMED", "IN_PROGRESS", "REVIEW"];

pub fn create(p: &Project, mut fields: Value) -> Result<Value> {
    control::guard_write(p, "task create")?;
    authority::require(p, "create_task")?;
    let store = RecordStore::load(&p.root);
    let id = fields
        .get("id")
        .and_then(|v| v.as_str())
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
    let obj = fields.as_object_mut().unwrap();
    obj.entry("task_status").or_insert(json!("DRAFT"));
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
    obj.remove("id");
    obj.remove("title");
    let rec = new_record("task", &id, &title, Value::Object(obj.clone()));
    p.schemas()
        .validate("task", &rec.data, &format!("({id})"))?;
    save_record(&p.root, &rec)?;
    Ok(rec.data)
}

pub fn set_status(p: &Project, id: &str, status: &str, note: Option<&str>) -> Result<Value> {
    control::guard_write(p, "task status")?;
    authority::require(p, "mutate_task_status")?;
    if !STATUSES.contains(&status) {
        return Err(GovError::new(
            "USAGE",
            format!("invalid task status {status}"),
        ));
    }
    let mut store = RecordStore::load(&p.root);
    let rec = store
        .get_mut(id)
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    if rec.rtype() != "task" {
        return Err(GovError::new("USAGE", format!("{id} is not a task")));
    }
    rec.set("task_status", json!(status));
    rec.set("updated", json!(today()));
    if let Some(n) = note {
        rec.set("status_note", json!(n));
    }
    let data = rec.data.clone();
    save_record(&p.root, rec)?;
    Ok(data)
}

pub fn list(p: &Project, status: Option<&str>) -> Vec<Value> {
    let store = RecordStore::load(&p.root);
    store.of_type("task").into_iter().filter(|t| status.map(|s| t.get("task_status") == s).unwrap_or(true))
        .map(|t| json!({"id": t.id(), "title": t.title(), "class": t.get("class"), "task_status": t.get("task_status"), "feature": t.get("feature"), "dependencies": t.list("dependencies"), "human_gate": t.get("human_gate"), "retest_required": t.data.get("retest_required").and_then(|v| v.as_bool()).unwrap_or(false), "path": t.path})).collect()
}

/// The task's designated role, if any, refuses every other acting role.
fn designated_role_refusal(p: &Project, t: &Record, action: &str) -> Option<GovError> {
    let designated = t.get("role");
    if designated.is_empty() || designated == p.role {
        return None;
    }
    Some(GovError::new("ROLE_NOT_DESIGNATED", format!("{} designates role '{designated}' (task contract `role`); the acting role '{}' may not {action} it — act as '{designated}' or have the task contract amended", t.id(), p.role)).with_details(json!({"task": t.id(), "designated_role": designated, "acting_role": p.role})))
}

/// Claim a runnable task for this session (BC-P2-15). The grant, the parallel-agent budget
/// (BUDGET_POLICY.defaults.max_parallel_agents) and the mutation-scope overlap check are decided in one claims-store
/// transaction; the task's designated role binds who may claim it.
pub fn claim(p: &Project, id: &str) -> Result<Value> {
    control::guard_write(p, "task claim")?;
    authority::require(p, "claim_task")?;
    let store = RecordStore::load(&p.root);
    let t = store
        .get(id)
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    let st = t.get("task_status");
    if !CLAIMABLE.contains(&st.as_str()) {
        return Err(GovError::new(
            "TASK_NOT_RUNNABLE",
            format!("{id} is {st}; only READY tasks can be claimed (run `gov task dag` / replan)"),
        ));
    }
    if let Some(e) = designated_role_refusal(p, t, "claim") {
        return Err(e);
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
    // finished between the status check above and the grant must not be followed by a claim of a closed task
    let store = RecordStore::load(&p.root);
    let st_now = store
        .get(id)
        .map(|r| r.get("task_status"))
        .unwrap_or_default();
    if !CLAIMABLE.contains(&st_now.as_str()) {
        if !renewed {
            let _ = claims::release(p, id, &p.session_id, false);
        }
        return Err(GovError::new(
            "TASK_NOT_RUNNABLE",
            format!("{id} became {st_now} while it was being claimed; the claim was withdrawn"),
        ));
    }
    set_status_internal(p, id, "IN_PROGRESS", None)?;
    c["baseline"] = establish_baseline(p, &store, id, renewed)?;
    Ok(c)
}

fn set_status_internal(p: &Project, id: &str, status: &str, note: Option<&str>) -> Result<Value> {
    let mut store = RecordStore::load(&p.root);
    let rec = store
        .get_mut(id)
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    rec.set("task_status", json!(status));
    rec.set("updated", json!(today()));
    if let Some(n) = note {
        rec.set("status_note", json!(n));
    }
    let data = rec.data.clone();
    save_record(&p.root, rec)?;
    Ok(data)
}

/// Release a claim. The mutations the claim window produced stay attributed to the task: they are carried into the
/// baseline of the next claim, so a release followed by a re-claim cannot reset the observed-mutation evidence.
pub fn release(p: &Project, id: &str, force: bool) -> Result<bool> {
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
        }
        let _ = set_status_internal(p, id, "READY", Some("released"));
    }
    Ok(released.is_some())
}

/// Paths the Governance OS itself writes while a task is open (derived views, evidence records, gate/CIT records,
/// task records). They are never attributed to the worker's mutation manifest.
const OS_MANAGED_PREFIXES: &[&str] = &[
    "governance/generated/",
    "spec/reports/",
    "spec/audits/",
    "spec/tasks/",
    "spec/planning/",
    "spec/decisions/HDG-",
    "spec/decisions/CIT-",
    "spec/decisions/D-",
    "spec/lessons/",
    "framework.json",
    ".gitignore",
    "spec/now/NOW.md",
];

fn os_managed(path: &str) -> bool {
    OS_MANAGED_PREFIXES.iter().any(|pre| path.starts_with(pre))
}

/// Paths the repository contract declares as generated/derived outputs are not worker mutations either.
fn contract_generated(p: &Project, path: &str) -> bool {
    let d = p.contract().decide(path);
    matches!(d.class().as_str(), "generated" | "derived")
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
        if rel.starts_with(".governance-runtime/") || rel.starts_with(".git/") {
            continue;
        }
        let abs = p.root.join(&rel);
        if let Ok(bytes) = std::fs::read(&abs) {
            out.insert(rel, crate::util::sha256_hex(&bytes));
        }
    }
    out
}

fn task_runtime_dir(p: &Project, id: &str) -> std::path::PathBuf {
    p.runtime_dir().join("tasks").join(id)
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

/// Snapshot the working tree now and make it the task's claim baseline (overwriting any previous one).
pub fn snapshot_tree(p: &Project, id: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    write_baseline(p, &store, id, tree_listing(p), &BTreeMap::new())
}

/// The claim window is bound exactly, not by clock: the baseline lists the CITs already COMMITTED and the close
/// reports already written when it was taken, and only CITs committed / closes reported after it count as inside
/// the window.
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
    let doc = json!({"task": id, "at": now_iso(), "commit": p.git_commit(), "session": p.session_id, "worktree": claims::worktree_id(p),
        "files": files, "carried": carried.keys().collect::<Vec<_>>(), "cits_committed": cits_committed, "reports_present": reports_present,
        "method": "git ls-files -co --exclude-standard + sha256 (walk fallback); mutations of earlier claim windows carried"});
    let path = claim_tree_path(p, id);
    std::fs::create_dir_all(path.parent().unwrap())?;
    crate::util::write_json(&path, &doc)?;
    let _ = std::fs::remove_file(carried_path(p, id));
    Ok(
        json!({"files": doc["files"].as_object().map(|m| m.len()).unwrap_or(0), "commit": doc["commit"], "at": doc["at"], "reused": false, "carried": doc["carried"]}),
    )
}

fn read_carried(p: &Project, id: &str) -> BTreeMap<String, Option<String>> {
    crate::util::read_json(&carried_path(p, id))
        .ok()
        .and_then(|v| v.as_object().cloned())
        .map(|m| {
            m.into_iter()
                .map(|(k, v)| (k, v.as_str().map(|s| s.to_string())))
                .collect()
        })
        .unwrap_or_default()
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
    let path = claim_tree_path(p, id);
    if continuing {
        if let Ok(doc) = crate::util::read_json(&path) {
            return Ok(
                json!({"files": doc["files"].as_object().map(|m| m.len()).unwrap_or(0), "commit": doc["commit"], "at": doc["at"], "reused": true, "carried": doc["carried"]}),
            );
        }
    }
    let mut carried = read_carried(p, id);
    if let (Ok(doc), Some(t)) = (crate::util::read_json(&path), store.get(id)) {
        // an earlier claim window ended without a release or a close (lease expired, swept, session gone)
        let obs = observe_against(p, store, t, Some(&doc));
        for (k, orig) in obs.baseline_of {
            carried.entry(k).or_insert(orig);
        }
    }
    write_baseline(p, store, id, tree_listing(p), &carried)
}

/// At release: fold the claim window's attributable mutations into the task's carried set and retire the baseline.
fn carry_forward(p: &Project, store: &RecordStore, t: &Record) -> Result<()> {
    let id = t.id();
    let path = claim_tree_path(p, &id);
    let Ok(doc) = crate::util::read_json(&path) else {
        return Ok(());
    };
    let obs = observe_against(p, store, t, Some(&doc));
    let mut carried = read_carried(p, &id);
    for (k, orig) in obs.baseline_of {
        carried.entry(k).or_insert(orig);
    }
    std::fs::create_dir_all(task_runtime_dir(p, &id))?;
    crate::util::write_json(&carried_path(p, &id), &json!(carried))?;
    let _ = std::fs::remove_file(&path);
    Ok(())
}

/// What a task's claim window shows in the working tree.
#[derive(Debug, Clone, Default)]
pub struct Observation {
    /// Paths changed since the baseline that are this task's (CIT-covered paths included, attributed ones not).
    pub observed: Vec<String>,
    /// For each observed path not covered by a CIT: its baseline hash (None = the path did not exist).
    pub baseline_of: BTreeMap<String, Option<String>>,
    /// For each observed path not covered by a CIT: its current hash (None = deleted).
    pub current_of: BTreeMap<String, Option<String>>,
    /// Every path a Change-Impact Transaction executed inside the claim window touched (what may lie outside the
    /// task's scope because a CIT governing that change covers it).
    pub cit_window: BTreeSet<String>,
    /// The observed paths among `cit_window`.
    pub cit_covered: BTreeSet<String>,
    /// Changed paths attributed to another claim or to a task closed inside the window.
    pub attributed: Vec<Value>,
    /// Start of the claim window (epoch seconds), when there is a baseline.
    pub window_start: Option<i64>,
    pub evidence: Value,
}

/// Paths touched by a COMMITTED Change-Impact Transaction that finished at or after `since` — the claim window of
/// the task being closed. A CIT committed before the window began governs nothing the task did.
pub fn cit_covered_paths(store: &RecordStore, since: Option<i64>) -> BTreeSet<String> {
    let mut out = BTreeSet::new();
    let Some(since) = since else {
        return out;
    };
    for c in store.of_type("cit") {
        if c.get("cit_status") != "COMMITTED" {
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
/// the baseline was taken (baselines written before that list existed fall back to [`cit_covered_paths`]).
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
        if c.get("cit_status") == "COMMITTED" && !before.contains(c.id().as_str()) {
            if let Some(t) = c.data["execution"]["propagation"]["touched"].as_array() {
                out.extend(t.iter().filter_map(|x| x.as_str().map(|s| s.to_string())));
            }
        }
    }
    out
}

/// Content accepted by closes that completed inside the window: report id, task, path -> hash (None = deleted).
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
        // only the recorded close of a DONE task counts
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
/// 1. OS-managed and contract-generated paths are never the worker's;
/// 2. a path whose current content is exactly what a task closed inside this window accepted belongs to that close;
/// 3. a path outside this task's scope, inside the scope of another live claim made from the same working tree and
///    changed since that claim's own baseline, belongs to that claim (scopes of concurrent claims are disjoint);
/// 4. everything else is this task's. Paths a CIT executed inside the window touched are reported in `cit_covered`.
pub fn observe(p: &Project, store: &RecordStore, t: &Record) -> Observation {
    let doc = crate::util::read_json(&claim_tree_path(p, &t.id())).ok();
    observe_against(p, store, t, doc.as_ref())
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
        // no claim baseline (only reachable by an L3+ forced close): fall back to git's view of uncommitted changes
        let observed: Vec<String> = uncommitted_paths(p)
            .into_iter()
            .filter(|f| !os_managed(f) && !contract_generated(p, f))
            .collect();
        return Observation {
            current_of: observed
                .iter()
                .map(|f| (f.clone(), now.get(f).cloned()))
                .collect(),
            observed: observed.clone(),
            evidence: json!({"baseline": "none (uncommitted changes: git diff HEAD + untracked files)", "observed": observed}),
            ..Default::default()
        };
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
    let cit_covered = cit_window_paths(store, Some(doc));
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
    changed.retain(|f| !os_managed(f) && !contract_generated(p, f));
    let closed = closed_states(store, doc, &id);
    let own_scope = claims::scope_of_task(t);
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
            let theirs: BTreeMap<String, String> =
                crate::util::read_json(&claim_tree_path(p, &other))
                    .ok()
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
        let cur = now.get(&f).cloned();
        if cit_covered.contains(&f) {
            obs.cit_covered.insert(f.clone());
            obs.observed.push(f);
            continue;
        }
        if let Some((rid, task, _)) = closed.iter().find(|(_, _, m)| m.get(&f) == Some(&cur)) {
            obs.attributed
                .push(json!({"path": f, "to": task, "via": "closed_report", "report": rid}));
            continue;
        }
        if !claims::path_in_scope(&own_scope, &f) {
            if let Some((c, _, _)) = others.iter().find(|(_, scope, theirs)| {
                claims::path_in_scope(scope, &f) && theirs.get(&f) != cur.as_ref()
            }) {
                obs.attributed.push(json!({"path": f, "to": c["task_id"], "via": "live_claim", "session": c["session_id"]}));
                continue;
            }
        }
        obs.baseline_of.insert(f.clone(), baseline.get(&f).cloned());
        obs.current_of.insert(f.clone(), cur);
        obs.observed.push(f);
    }
    obs.evidence = json!({"baseline": format!("claim baseline {} (commit {})", doc["at"].as_str().unwrap_or("?"), doc["commit"].as_str().unwrap_or("?")),
        "observed": obs.observed, "carried": doc["carried"], "attributed_elsewhere": obs.attributed, "cit_covered": obs.cit_covered});
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
                    .map(|s| s.to_string()),
            );
        }
    }
    out.into_iter().collect()
}

/// Mutations observed since the claim baseline (added/modified/deleted), excluding OS-managed paths and changes
/// attributed to other claims or closes (see [`observe`]).
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

/// Mutation-scope check for a task: forbidden paths, kernel, contract-prohibited paths, and (when allowed_paths is
/// declared) anything outside it that is not in `governed` — the paths a CIT executed inside this task's claim
/// window touched ([`cit_window_paths`]).
pub fn scope_violations(
    p: &Project,
    task: &crate::records::Record,
    files: &[String],
    governed: &BTreeSet<String>,
) -> Vec<String> {
    let allowed = task.list("allowed_paths");
    let mut forbidden = task.list("forbidden_paths");
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
        if !allowed.is_empty()
            && !allowed.iter().any(|pat| glob_match(pat, f))
            && !governed.contains(f)
        {
            out.push(format!(
                "{f}: outside allowed_paths {allowed:?} and not governed by a CIT executed while this task was claimed"
            ));
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

/// Close with evidence (worker return / report). Enforces authority, the claim (holder, worktree), the designated
/// role, mutation scope, production-merge permission, tests status, index freshness (including embedder pins) and
/// governance currency.
pub fn close(
    p: &Project,
    db: &RuntimeDb,
    id: &str,
    mut report: Value,
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
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    if t.get("task_status") == "DONE" {
        return Err(GovError::new("USAGE", format!("{id} already DONE")));
    }
    // another session's live claim is refused first (as before); the rest of the claim binding follows the
    // evidence checks so a malformed report keeps its own refusal
    let live_holder = claims::holder(p, id)?;
    if let Some(h) = &live_holder {
        if h["session_id"].as_str() != Some(p.session_id.as_str()) && !force {
            return Err(GovError::new(
                "TASK_CLAIMED",
                format!("{id} is claimed by another session; --force requires L3+"),
            ));
        }
    }
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
    // --- the claim (BC-P2-15): work is closed by the session that holds it, from the working tree it was claimed in
    let wt = claims::worktree_id(p);
    let claim = claims::get(p, id)?;
    let mut overrides: Vec<Value> = vec![];
    match &claim {
        Some(c) if c["session_id"].as_str() == Some(p.session_id.as_str()) => {
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
    // --- the designated role (BC-P2-14)
    if let Some(e) = designated_role_refusal(p, t, "close") {
        if !force {
            return Err(e);
        }
        overrides.push(json!({"override": "designated_role", "designated_role": t.get("role"), "acting_role": p.role}));
    }
    let files_changed: Vec<String> = report
        .get("files_changed")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    // --- mutation scope (framework §25/§42; verifier H4): the declared manifest ...
    let obs = observe(p, &store, t);
    let governed = &obs.cit_window;
    let violations = scope_violations(p, t, &files_changed, governed);
    if !violations.is_empty() {
        return Err(GovError::new("MUTATION_SCOPE_VIOLATION", format!("task {id} reports mutations outside its contract: {}; route them through a CIT or amend the task contract", violations.join("; "))).with_details(json!({"violations": violations, "allowed_paths": t.list("allowed_paths")})));
    }
    // ... and the mutations actually observed in the repository since the claim baseline (verifier M-N4): undeclared
    // or out-of-scope changes fail closed unless a CIT executed inside this claim window governs them;
    // self-attestation is never sufficient
    let observed = obs.observed.clone();
    let evidence = obs.evidence.clone();
    let undeclared: Vec<String> = observed
        .iter()
        .filter(|f| !files_changed.contains(f) && !governed.contains(*f))
        .cloned()
        .collect();
    let observed_violations = scope_violations(p, t, &observed, governed);
    if !undeclared.is_empty() || !observed_violations.is_empty() {
        return Err(GovError::new("MUTATION_SCOPE_VIOLATION", format!("task {id}: the repository shows mutations the report does not declare or the contract does not allow (undeclared: {undeclared:?}; out of scope: {observed_violations:?}); declare every change in files_changed, route out-of-scope changes through a CIT, or amend the task contract")).with_details(json!({"undeclared": undeclared, "out_of_scope": observed_violations, "reported": files_changed, "observed": observed, "evidence": evidence})));
    }
    // --- production-merge permission (BC-P2-14; Contract v3:569, :614)
    if !production_merge_allowed(t) {
        let landed: Vec<String> = observed
            .iter()
            .filter(|f| !governed.contains(*f) && is_production_path(p, f))
            .cloned()
            .collect();
        if !landed.is_empty() {
            return Err(GovError::new("PRODUCTION_MERGE_NOT_ALLOWED", format!("task {id} ({}) may not merge into production (production_merge_allowed: false) but its mutations landed in the production tree: {landed:?}; keep experimental output outside the production tree (spec/experiments/** or a path the repository contract classifies as evidence) and promote it through a CIT", t.get("class"))).with_details(json!({"task": id, "class": t.get("class"), "production_paths": landed, "observed": observed, "evidence": evidence})));
        }
    }
    let unobserved: Vec<String> = files_changed
        .iter()
        .filter(|f| !observed.contains(f))
        .cloned()
        .collect();
    // --- freshness (content and pins)
    let fr = freshness(p);
    let stale_count = fr.stale.len() + fr.added.len() + fr.removed.len();
    let max_stale = pol.get_i64(
        "MEMORY_POLICY",
        "freshness.max_stale_artifacts_on_task_close",
        0,
    ) as usize;
    let on_stale = pol.get_str("MEMORY_POLICY", "freshness.on_stale_close", "fail");
    let mut degraded = vec![];
    if !fr.pin_mismatch.is_empty() {
        return Err(GovError::new("INDEX_PIN_MISMATCH", format!("the index was built with different pins than policy declares ({}); run `gov rebuild-memory` before closing", fr.pin_mismatch.join("; "))));
    }
    if !fr.manifest_present || stale_count > max_stale {
        if on_stale == "fail" && !force {
            return Err(GovError::new("INDEX_STALE", format!("required index is stale ({stale_count} artefacts changed since last build); run `gov rebuild-memory --incremental` before closing")).with_details(json!({"stale": fr.stale, "added": fr.added, "removed": fr.removed})));
        }
        degraded.push(format!("index stale ({stale_count})"));
    }
    // --- governance currency
    let touches_gov = files_changed
        .iter()
        .any(|f| glob_match("governance/**", f) || glob_match("spec/decisions/**", f));
    if touches_gov {
        match crate::verification::latest_green(p) {
            Some(g) if g["inputs_hash"].as_str() == Some(&crate::verification::inputs_hash(p)) => {}
            Some(_) => {
                if !force {
                    return Err(GovError::new("GOVERNANCE_SUITE_STALE", "task touches governance paths but the last green governance record is obsolete; run `gov audit` first"));
                }
                degraded.push("governance suite stale".into());
            }
            None => {
                if !force {
                    return Err(GovError::new("GOVERNANCE_SUITE_MISSING", "task touches governance paths; no green governance record exists; run `gov audit` first"));
                }
                degraded.push("no governance record".into());
            }
        }
    }
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
    // the content this close accepts, so a later close in the same working tree can tell this task's accepted
    // changes from its own (and so the evidence names exactly what was accepted)
    robj.insert(
        "mutation_evidence".into(),
        json!({"baseline": evidence["baseline"], "reported_but_unchanged": unobserved, "closed_at": closed_at,
            "observed_hashes": obs.current_of, "cit_covered": obs.cit_covered, "attributed_elsewhere": obs.attributed,
            "carried": evidence["carried"], "claim": claim.as_ref().map(|c| json!({"session": c["session_id"], "role": c["role"], "worktree": c["worktree"], "branch": c["branch"], "head": c["head"], "scope": c["scope"], "claimed_at": c["claimed_at"]})),
            "closing_worktree": wt, "overrides": overrides}),
    );
    let title = format!("Report for {id}: {}", t.title());
    let rec = new_record("report", &rpt_id, &title, Value::Object(robj.clone()));
    p.schemas()
        .validate("report", &rec.data, &format!("({rpt_id})"))?;
    save_record(&p.root, &rec)?;
    let mut store2 = RecordStore::load(&p.root);
    let tr = store2.get_mut(id).unwrap();
    tr.set("task_status", json!("DONE"));
    tr.set("closed_by_report", json!(rpt_id));
    tr.set("updated", json!(today()));
    tr.set("closed_at", json!(closed_at));
    if tr.data.get("retest_required").is_some() {
        tr.set("retest_required", json!(false));
    }
    save_record(&p.root, tr)?;
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
    Ok(
        json!({"task": id, "task_status": "DONE", "report": rpt_id, "checkpoint": ck["id"], "degraded": degraded, "overrides": overrides}),
    )
}

/// The enforcement state of a task's contract fields, for consumers that present the contract (the context packet,
/// `gov task show`): resolution of `required_data`, `required_tools` and `required_skills`, the tasks that `blocks`
/// it, the designated role and the production-merge permission. Read-only.
pub fn contract_enforcement(p: &Project, store: &RecordStore, t: &Record) -> Value {
    let inputs = crate::orchestration::dag::required_inputs(p, store, t);
    let blocked_by: Vec<Value> = store
        .of_type("task")
        .into_iter()
        .filter(|o| o.list("blocks").contains(&t.id()))
        .map(|o| json!({"task": o.id(), "task_status": o.get("task_status")}))
        .collect();
    json!({"required_data": inputs["required_data"], "required_tools": inputs["required_tools"], "required_skills": inputs["required_skills"],
        "blocked_by": blocked_by, "blocks": t.list("blocks"), "designated_role": t.get("role"),
        "production_merge_allowed": production_merge_allowed(t), "mutation_scope": claims::scope_of_task(t)})
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
