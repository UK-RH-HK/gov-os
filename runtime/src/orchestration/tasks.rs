//! Task contracts (framework §42), creation, status transitions and evidence-gated close (§13, §64).
use crate::checkpoints;
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::orchestration::{claims, control};
use crate::records::{new_record, save_record, RecordStore};
use crate::util::{glob_match, now_iso, today};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub const STATUSES: &[&str] = &["DRAFT", "READY", "BLOCKED", "CLAIMED", "IN_PROGRESS", "REVIEW", "DONE", "CANCELLED", "WAITING_HUMAN"];

pub fn create(p: &Project, mut fields: Value) -> Result<Value> {
    control::guard_write(p, "task create")?;
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
    obj.remove("id"); obj.remove("title");
    let rec = new_record("task", &id, &title, Value::Object(obj.clone()));
    p.schemas().validate("task", &rec.data, &format!("({id})"))?;
    save_record(&p.root, &rec)?;
    Ok(rec.data)
}

pub fn set_status(p: &Project, id: &str, status: &str, note: Option<&str>) -> Result<Value> {
    control::guard_write(p, "task status")?;
    if !STATUSES.contains(&status) { return Err(GovError::new("USAGE", format!("invalid task status {status}"))); }
    let mut store = RecordStore::load(&p.root);
    let rec = store.get_mut(id).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    if rec.rtype() != "task" { return Err(GovError::new("USAGE", format!("{id} is not a task"))); }
    rec.set("task_status", json!(status));
    rec.set("updated", json!(today()));
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

pub fn claim(p: &Project, db: &RuntimeDb, id: &str) -> Result<Value> {
    control::guard_write(p, "task claim")?;
    let store = RecordStore::load(&p.root);
    let t = store.get(id).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    let st = t.get("task_status");
    if !matches!(st.as_str(), "READY" | "CLAIMED" | "IN_PROGRESS" | "REVIEW") { return Err(GovError::new("TASK_NOT_RUNNABLE", format!("{id} is {st}; only READY tasks can be claimed (run `gov task dag` / replan)"))); }
    let c = claims::claim(db, id, &p.session_id, &p.role, None)?;
    set_status(p, id, "IN_PROGRESS", None)?;
    Ok(c)
}

pub fn release(p: &Project, db: &RuntimeDb, id: &str, force: bool) -> Result<bool> {
    let released = claims::release(db, id, &p.session_id, force)?;
    if released { let _ = set_status(p, id, "READY", Some("released")); }
    Ok(released)
}

/// Close with evidence (worker return / report). Enforces claim, tests status, index freshness and governance currency.
pub fn close(p: &Project, db: &RuntimeDb, id: &str, mut report: Value, force: bool) -> Result<Value> {
    control::guard_write(p, "task close")?;
    let pol = p.policies();
    let store = RecordStore::load(&p.root);
    let t = store.get(id).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found")))?;
    if t.get("task_status") == "DONE" { return Err(GovError::new("USAGE", format!("{id} already DONE"))); }
    if let Some(h) = claims::holder(db, id)? {
        if h["session_id"].as_str() != Some(&p.session_id) && !force { return Err(GovError::new("TASK_CLAIMED", format!("{id} is claimed by another session; --force requires L3+"))); }
    }
    let tests_status = report.get("tests").and_then(|x| x.get("status")).and_then(|v| v.as_str()).unwrap_or("").to_string();
    let allowed = pol.get_list("TEST_POLICY", "task_close_requires_tests_status");
    if !allowed.contains(&tests_status) { return Err(GovError::new("EVIDENCE_REQUIRED", format!("report.tests.status must be one of {allowed:?} (got '{tests_status}')"))); }
    if report.get("work_completed").and_then(|v| v.as_str()).map(|s| s.is_empty()).unwrap_or(true) { return Err(GovError::new("EVIDENCE_REQUIRED", "report.work_completed is required")); }
    // freshness
    let fr = freshness(p);
    let stale_count = fr.stale.len() + fr.added.len() + fr.removed.len();
    let max_stale = pol.get_i64("MEMORY_POLICY", "freshness.max_stale_artifacts_on_task_close", 0) as usize;
    let on_stale = pol.get_str("MEMORY_POLICY", "freshness.on_stale_close", "fail");
    let mut degraded = vec![];
    if !fr.manifest_present || stale_count > max_stale {
        if on_stale == "fail" && !force { return Err(GovError::new("INDEX_STALE", format!("required index is stale ({stale_count} artefacts changed since last build); run `gov rebuild-memory --incremental` before closing")).with_details(json!({"stale": fr.stale, "added": fr.added, "removed": fr.removed}))); }
        degraded.push(format!("index stale ({stale_count})"));
    }
    // governance currency
    let files_changed: Vec<String> = report.get("files_changed").and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
    let touches_gov = files_changed.iter().any(|f| glob_match("governance/**", f) || glob_match("spec/decisions/**", f));
    if touches_gov {
        match crate::verification::latest_green(p) {
            Some(g) if g["inputs_hash"].as_str() == Some(&crate::verification::inputs_hash(p)) => {}
            Some(_) => { if !force { return Err(GovError::new("GOVERNANCE_SUITE_STALE", "task touches governance paths but the last green governance record is obsolete; run `gov audit` first")); } degraded.push("governance suite stale".into()); }
            None => { if !force { return Err(GovError::new("GOVERNANCE_SUITE_MISSING", "task touches governance paths; no green governance record exists; run `gov audit` first")); } degraded.push("no governance record".into()); }
        }
    }
    // write report record
    let rpt_id = store.next_id("report");
    let robj = report.as_object_mut().unwrap();
    robj.insert("task".into(), json!(id)); robj.insert("session".into(), json!(p.session_id)); robj.insert("role".into(), json!(p.role));
    robj.entry("outcome").or_insert(json!("success"));
    robj.entry("evidence").or_insert(json!([]));
    if !degraded.is_empty() { robj.insert("degraded".into(), json!(degraded)); }
    robj.insert("state_class".into(), json!("EVIDENCE"));
    let title = format!("Report for {id}: {}", t.title());
    let rec = new_record("report", &rpt_id, &title, Value::Object(robj.clone()));
    p.schemas().validate("report", &rec.data, &format!("({rpt_id})"))?;
    save_record(&p.root, &rec)?;
    // close
    let mut store2 = RecordStore::load(&p.root);
    let tr = store2.get_mut(id).unwrap();
    tr.set("task_status", json!("DONE")); tr.set("closed_by_report", json!(rpt_id)); tr.set("updated", json!(today())); tr.set("closed_at", json!(now_iso()));
    if tr.data.get("retest_required").is_some() { tr.set("retest_required", json!(false)); }
    save_record(&p.root, tr)?;
    let _ = claims::release(db, id, &p.session_id, true);
    let ck = checkpoints::create(p, db, json!({"task": id, "trigger": "task_transition", "last_completed_step": format!("closed {id}"), "next_action": "gov continue", "tests_status": tests_status, "files_changed": files_changed}))?;
    // keep derived memory fresh after writing the report/task/checkpoint records
    let _ = crate::memory::indexer::rebuild(p, crate::memory::indexer::IndexOptions { incremental: true });
    Ok(json!({"task": id, "task_status": "DONE", "report": rpt_id, "checkpoint": ck["id"], "degraded": degraded}))
}
