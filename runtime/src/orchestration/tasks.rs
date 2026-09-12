//! Task contracts (framework §42), creation, status transitions and evidence-gated close (§13, §64).
//! Every mutating path is authority-checked (AUTHORITY_POLICY.authority_levels_required) and task close enforces the
//! task's mutation scope: files changed outside allowed_paths must have gone through a committed CIT.
use crate::authority;
use crate::checkpoints;
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::orchestration::{claims, control, gates};
use crate::records::{new_record, save_record, RecordStore};
use crate::util::{glob_match, now_iso, today};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub const STATUSES: &[&str] = &["DRAFT", "READY", "BLOCKED", "CLAIMED", "IN_PROGRESS", "REVIEW", "DONE", "CANCELLED", "WAITING_HUMAN"];

pub fn create(p: &Project, mut fields: Value) -> Result<Value> {
    control::guard_write(p, "task create")?;
    authority::require(p, "create_task")?;
    let store = RecordStore::load(&p.root);
    let id = fields.get("id").and_then(|v| v.as_str()).map(|s| s.to_string()).unwrap_or_else(|| store.next_id("task"));
    if store.get(&id).is_some() { return Err(GovError::new("DUPLICATE_ID", format!("{id} already exists"))); }
    let title = fields.get("title").and_then(|v| v.as_str()).or(fields.get("objective").and_then(|v| v.as_str())).unwrap_or("untitled task").to_string();
    let obj = fields.as_object_mut().unwrap();
    obj.entry("task_status").or_insert(json!("DRAFT"));
    obj.entry("objective").or_insert(json!(title));
    obj.entry("class").or_insert(json!("implementation"));
    let class = obj.get("class").and_then(|c| c.as_str()).unwrap_or("implementation").to_string();
    obj.entry("production_merge_allowed").or_insert(json!(class != "experiment"));
    if class == "experiment" { obj.insert("production_merge_allowed".into(), json!(false)); }
    let tier = crate::routing::tier_for_class(p, &class);
    obj.entry("minimum_model_tier").or_insert(json!(tier));
    obj.entry("minimum_reasoning").or_insert(json!("medium"));
    obj.entry("allowed_paths").or_insert(json!([]));
    obj.entry("forbidden_paths").or_insert(json!(["governance/kernel/**"]));
    // MODEL_ROUTING_POLICY.reasoning_levels / tiers are the only valid values
    let pol = p.policies();
    let levels = pol.get_list("MODEL_ROUTING_POLICY", "reasoning_levels");
    if let Some(r) = obj.get("minimum_reasoning").and_then(|v| v.as_str()) { if !levels.is_empty() && !levels.iter().any(|l| l == r) { return Err(GovError::new("USAGE", format!("minimum_reasoning '{r}' is not one of MODEL_ROUTING_POLICY.reasoning_levels {levels:?}"))); } }
    if let Some(t) = obj.get("minimum_model_tier").and_then(|v| v.as_str()) { if pol.get("MODEL_ROUTING_POLICY", &format!("tiers.{t}")).is_none() { return Err(GovError::new("USAGE", format!("minimum_model_tier '{t}' is not a MODEL_ROUTING_POLICY tier"))); } }
    obj.remove("id"); obj.remove("title");
    let rec = new_record("task", &id, &title, Value::Object(obj.clone()));
    p.schemas().validate("task", &rec.data, &format!("({id})"))?;
    save_record(&p.root, &rec)?;
    Ok(rec.data)
}

pub fn set_status(p: &Project, id: &str, status: &str, note: Option<&str>) -> Result<Value> {
    control::guard_write(p, "task status")?;
    authority::require(p, "mutate_task_status")?;
    if !STATUSES.contains(&status) { return Err(GovError::new("USAGE", format!("invalid task status {status}"))); }
    let mut store = RecordStore::load(&p.root);
    let rec = store.get_mut(id).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    if rec.rtype() != "task" { return Err(GovError::new("USAGE", format!("{id} is not a task"))); }
    rec.set("task_status", json!(status)); rec.set("updated", json!(today()));
    if let Some(n) = note { rec.set("status_note", json!(n)); }
    let data = rec.data.clone();
    save_record(&p.root, rec)?;
    Ok(data)
}

pub fn list(p: &Project, status: Option<&str>) -> Vec<Value> {
    let store = RecordStore::load(&p.root);
    store.of_type("task").into_iter().filter(|t| status.map(|s| t.get("task_status") == s).unwrap_or(true))
        .map(|t| json!({"id": t.id(), "title": t.title(), "class": t.get("class"), "task_status": t.get("task_status"), "feature": t.get("feature"), "dependencies": t.list("dependencies"), "human_gate": t.get("human_gate"), "retest_required": t.data.get("retest_required").and_then(|v| v.as_bool()).unwrap_or(false), "path": t.path})).collect()
}

/// Claim a runnable task for this session. BUDGET_POLICY.defaults.max_parallel_agents bounds concurrent sessions.
pub fn claim(p: &Project, id: &str) -> Result<Value> {
    control::guard_write(p, "task claim")?;
    authority::require(p, "claim_task")?;
    let store = RecordStore::load(&p.root);
    let t = store.get(id).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    let st = t.get("task_status");
    if !matches!(st.as_str(), "READY" | "CLAIMED" | "IN_PROGRESS" | "REVIEW") { return Err(GovError::new("TASK_NOT_RUNNABLE", format!("{id} is {st}; only READY tasks can be claimed (run `gov task dag` / replan)"))); }
    let max_agents = p.policies().get_i64("BUDGET_POLICY", "defaults.max_parallel_agents", 4) as usize;
    let active = claims::active_sessions(p)?;
    if !active.iter().any(|s| s == &p.session_id) && active.len() >= max_agents {
        let on = p.policies().get_str("BUDGET_POLICY", "on_threshold_exceeded", "human_decision_gate");
        let mut gate_id = Value::Null;
        if on == "human_decision_gate" {
            let g = gates::create_system(p, json!({"question": format!("Budget threshold exceeded: {} parallel agent sessions hold claims (BUDGET_POLICY.defaults.max_parallel_agents = {max_agents}). Allow session {} to claim {id}?", active.len(), p.session_id), "why_now": "a task claim would exceed the delegated parallelism budget", "current_state": format!("active sessions: {active:?}"), "options": [{"id": "A", "description": "raise the budget in the project overlay"}, {"id": "B", "description": "wait for a session to finish"}], "impact": "cost and coordination", "reversibility": "reversible", "recommendation": "B", "confidence": 0.7, "trigger": "budget_threshold", "impact_radius": "R1"}))?;
            gate_id = g["id"].clone();
        }
        return Err(GovError::new("BUDGET_EXCEEDED", format!("max_parallel_agents ({max_agents}) reached: {} active session(s); human decision gate {gate_id} raised", active.len())).with_details(json!({"active_sessions": active, "human_gate": gate_id})));
    }
    let c = claims::claim(p, id, &p.session_id, &p.role, None)?;
    set_status_internal(p, id, "IN_PROGRESS", None)?;
    Ok(c)
}

fn set_status_internal(p: &Project, id: &str, status: &str, note: Option<&str>) -> Result<Value> {
    let mut store = RecordStore::load(&p.root);
    let rec = store.get_mut(id).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    rec.set("task_status", json!(status)); rec.set("updated", json!(today()));
    if let Some(n) = note { rec.set("status_note", json!(n)); }
    let data = rec.data.clone(); save_record(&p.root, rec)?; Ok(data)
}

pub fn release(p: &Project, id: &str, force: bool) -> Result<bool> {
    authority::require(p, if force { "force_release_task" } else { "release_task" })?;
    let released = claims::release(p, id, &p.session_id, force)?;
    if released { let _ = set_status_internal(p, id, "READY", Some("released")); }
    Ok(released)
}

/// Paths governed by a committed Change-Impact Transaction (mutations outside a task's scope are legitimate only there).
fn cit_governed_paths(store: &RecordStore) -> Vec<String> {
    let mut out = vec![];
    for c in store.of_type("cit") { if c.get("cit_status") == "COMMITTED" { if let Some(t) = c.data["execution"]["propagation"]["touched"].as_array() { out.extend(t.iter().filter_map(|x| x.as_str().map(|s| s.to_string()))); } } }
    out
}

/// Mutation-scope check for a task: forbidden paths, kernel, contract-prohibited paths, and (when allowed_paths is
/// declared) anything outside it that no committed CIT governs.
pub fn scope_violations(p: &Project, task: &crate::records::Record, files: &[String], store: &RecordStore) -> Vec<String> {
    let allowed = task.list("allowed_paths");
    let mut forbidden = task.list("forbidden_paths");
    forbidden.push("governance/kernel/**".into());
    let prohibited: Vec<String> = p.contract().rules.iter().filter(|r| r.get("mutation").and_then(|m| m.as_str()) == Some("prohibited")).filter_map(|r| r.get("pattern").and_then(|x| x.as_str()).map(|s| s.to_string())).collect();
    let governed = cit_governed_paths(store);
    let mut out = vec![];
    for f in files {
        if forbidden.iter().any(|pat| glob_match(pat, f)) { out.push(format!("{f}: forbidden path")); continue; }
        if prohibited.iter().any(|pat| glob_match(pat, f)) { out.push(format!("{f}: mutation prohibited by the repository contract")); continue; }
        if !allowed.is_empty() && !allowed.iter().any(|pat| glob_match(pat, f)) && !governed.contains(f) { out.push(format!("{f}: outside allowed_paths {allowed:?} and not governed by a committed CIT")); }
    }
    out
}

/// Close with evidence (worker return / report). Enforces authority, claim, mutation scope, tests status, index
/// freshness (including embedder pins) and governance currency.
pub fn close(p: &Project, db: &RuntimeDb, id: &str, mut report: Value, force: bool) -> Result<Value> {
    control::guard_write(p, "task close")?;
    authority::require(p, if force { "force_close_task" } else { "close_task" })?;
    let pol = p.policies();
    let store = RecordStore::load(&p.root);
    let t = store.get(id).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    if t.get("task_status") == "DONE" { return Err(GovError::new("USAGE", format!("{id} already DONE"))); }
    if let Some(h) = claims::holder(p, id)? { if h["session_id"].as_str() != Some(&p.session_id) && !force { return Err(GovError::new("TASK_CLAIMED", format!("{id} is claimed by another session; --force requires L3+"))); } }
    let tests_status = report.get("tests").and_then(|x| x.get("status")).and_then(|v| v.as_str()).unwrap_or("").to_string();
    let allowed = pol.get_list("TEST_POLICY", "task_close_requires_tests_status");
    if !allowed.contains(&tests_status) { return Err(GovError::new("EVIDENCE_REQUIRED", format!("report.tests.status must be one of {allowed:?} (got '{tests_status}')"))); }
    if report.get("work_completed").and_then(|v| v.as_str()).map(|s| s.is_empty()).unwrap_or(true) { return Err(GovError::new("EVIDENCE_REQUIRED", "report.work_completed is required")); }
    let files_changed: Vec<String> = report.get("files_changed").and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
    // --- mutation scope (framework §25/§42; verifier H4)
    let violations = scope_violations(p, t, &files_changed, &store);
    if !violations.is_empty() { return Err(GovError::new("MUTATION_SCOPE_VIOLATION", format!("task {id} reports mutations outside its contract: {}; route them through a CIT or amend the task contract", violations.join("; "))).with_details(json!({"violations": violations, "allowed_paths": t.list("allowed_paths")}))); }
    // --- freshness (content and pins)
    let fr = freshness(p);
    let stale_count = fr.stale.len() + fr.added.len() + fr.removed.len();
    let max_stale = pol.get_i64("MEMORY_POLICY", "freshness.max_stale_artifacts_on_task_close", 0) as usize;
    let on_stale = pol.get_str("MEMORY_POLICY", "freshness.on_stale_close", "fail");
    let mut degraded = vec![];
    if !fr.pin_mismatch.is_empty() { return Err(GovError::new("INDEX_PIN_MISMATCH", format!("the index was built with different pins than policy declares ({}); run `gov rebuild-memory` before closing", fr.pin_mismatch.join("; ")))); }
    if !fr.manifest_present || stale_count > max_stale {
        if on_stale == "fail" && !force { return Err(GovError::new("INDEX_STALE", format!("required index is stale ({stale_count} artefacts changed since last build); run `gov rebuild-memory --incremental` before closing")).with_details(json!({"stale": fr.stale, "added": fr.added, "removed": fr.removed}))); }
        degraded.push(format!("index stale ({stale_count})"));
    }
    // --- governance currency
    let touches_gov = files_changed.iter().any(|f| glob_match("governance/**", f) || glob_match("spec/decisions/**", f));
    if touches_gov {
        match crate::verification::latest_green(p) {
            Some(g) if g["inputs_hash"].as_str() == Some(&crate::verification::inputs_hash(p)) => {}
            Some(_) => { if !force { return Err(GovError::new("GOVERNANCE_SUITE_STALE", "task touches governance paths but the last green governance record is obsolete; run `gov audit` first")); } degraded.push("governance suite stale".into()); }
            None => { if !force { return Err(GovError::new("GOVERNANCE_SUITE_MISSING", "task touches governance paths; no green governance record exists; run `gov audit` first")); } degraded.push("no governance record".into()); }
        }
    }
    let rpt_id = store.next_id("report");
    let robj = report.as_object_mut().unwrap();
    robj.insert("task".into(), json!(id)); robj.insert("session".into(), json!(p.session_id)); robj.insert("role".into(), json!(p.role));
    robj.entry("outcome").or_insert(json!("success")); robj.entry("evidence").or_insert(json!([]));
    if !degraded.is_empty() { robj.insert("degraded".into(), json!(degraded)); }
    robj.insert("state_class".into(), json!("EVIDENCE"));
    let title = format!("Report for {id}: {}", t.title());
    let rec = new_record("report", &rpt_id, &title, Value::Object(robj.clone()));
    p.schemas().validate("report", &rec.data, &format!("({rpt_id})"))?;
    save_record(&p.root, &rec)?;
    let mut store2 = RecordStore::load(&p.root);
    let tr = store2.get_mut(id).unwrap();
    tr.set("task_status", json!("DONE")); tr.set("closed_by_report", json!(rpt_id)); tr.set("updated", json!(today())); tr.set("closed_at", json!(now_iso()));
    if tr.data.get("retest_required").is_some() { tr.set("retest_required", json!(false)); }
    save_record(&p.root, tr)?;
    let _ = claims::release(p, id, &p.session_id, true);
    let ck = checkpoints::create(p, db, json!({"task": id, "trigger": "task_transition", "last_completed_step": format!("closed {id}"), "next_action": "gov continue", "tests_status": tests_status, "files_changed": files_changed}))?;
    let _ = crate::memory::indexer::rebuild(p, crate::memory::indexer::IndexOptions { incremental: true, ..Default::default() });
    Ok(json!({"task": id, "task_status": "DONE", "report": rpt_id, "checkpoint": ck["id"], "degraded": degraded}))
}
