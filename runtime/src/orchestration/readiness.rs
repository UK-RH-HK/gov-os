//! Feature/Capability Readiness Contract (framework §37-38): every cell explicit; gaps generate tasks in the same DAG.
use crate::orchestration::control;
use crate::records::{new_record, save_record, Record, RecordStore};
use crate::util::read_yaml;
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

#[derive(Debug, Clone, serde::Serialize)]
pub struct ReadinessView { pub feature: String, pub cells: Vec<Value>, pub gaps: Vec<String>, pub pre_implementation_gaps: Vec<String>, pub pre_implementation_ok: bool, pub invalid: Vec<String>, pub coverage: f64 }

pub fn dimensions(p: &Project) -> Vec<Value> {
    read_yaml(&p.kernel_dir().join("taxonomy").join("READINESS_DIMENSIONS.yaml")).ok().and_then(|v| v.get("dimensions").and_then(|d| d.as_array()).cloned()).unwrap_or_default()
}

pub fn evaluate(p: &Project, feature: &Record) -> ReadinessView {
    let dims = dimensions(p);
    let readiness = feature.data.get("readiness").cloned().unwrap_or(json!({}));
    let mut cells = vec![]; let mut gaps = vec![]; let mut pre_gaps = vec![]; let mut invalid = vec![]; let mut present = 0usize;
    for d in &dims {
        let id = d["id"].as_str().unwrap_or("").to_string();
        let pre = d["pre_implementation"].as_bool().unwrap_or(false);
        let cell = readiness.get(&id).cloned().unwrap_or(json!("MISSING"));
        let (state, reason) = match &cell { Value::String(s) => (s.clone(), None), Value::Object(o) => (o.get("status").and_then(|v| v.as_str()).unwrap_or("INVALID").to_string(), o.get("reason").and_then(|v| v.as_str()).map(|s| s.to_string())), _ => ("INVALID".into(), None) };
        let ok = state == "PRESENT" || (state == "N/A_WITH_REASON" && reason.as_ref().map(|r| r.len() >= 3).unwrap_or(false));
        if state == "N/A" || (state == "N/A_WITH_REASON" && reason.is_none()) || state == "INVALID" { invalid.push(format!("{id}: silent N/A or invalid cell value is not allowed")); }
        if ok { present += 1; } else { gaps.push(id.clone()); if pre { pre_gaps.push(id.clone()); } }
        cells.push(json!({"dimension": id, "state": state, "reason": reason, "pre_implementation": pre, "gap_task_class": d["gap_task_class"], "ok": ok}));
    }
    let coverage = if dims.is_empty() { 1.0 } else { present as f64 / dims.len() as f64 };
    ReadinessView { feature: feature.id(), cells, gaps, pre_implementation_gaps: pre_gaps.clone(), pre_implementation_ok: pre_gaps.is_empty() && invalid.is_empty(), invalid, coverage }
}

pub fn check(p: &Project, feature_id: &str) -> Result<ReadinessView> {
    let store = RecordStore::load(&p.root);
    let f = store.get(feature_id).filter(|r| r.rtype() == "feature").ok_or_else(|| GovError::new("FEATURE_NOT_FOUND", format!("{feature_id} not found")))?;
    Ok(evaluate(p, f))
}

/// Generate gap tasks for MISSING cells and make implementation tasks of the feature depend on pre-implementation gap tasks.
pub fn plan(p: &Project, feature_id: &str) -> Result<Value> {
    control::guard_write(p, "readiness plan")?;
    let view = check(p, feature_id)?;
    let store = RecordStore::load(&p.root);
    let existing: Vec<&Record> = store.of_type("task").into_iter().filter(|t| t.get("feature") == feature_id).collect();
    let mut created = vec![]; let mut pre_task_ids = vec![];
    let mut ids: Vec<String> = store.records.iter().map(|r| r.id()).collect();
    for c in &view.cells {
        if c["ok"].as_bool().unwrap_or(false) { continue; }
        let dim = c["dimension"].as_str().unwrap_or("").to_string();
        if let Some(t) = existing.iter().find(|t| t.get("readiness_cell") == dim && t.get("task_status") != "CANCELLED") { if c["pre_implementation"].as_bool().unwrap_or(false) { pre_task_ids.push(t.id()); } continue; }
        let id = crate::util::next_id("TASK", &ids, 4); ids.push(id.clone());
        let class = c["gap_task_class"].as_str().unwrap_or("specification").to_string();
        let rec = new_record("task", &id, &format!("{feature_id}: provide readiness cell '{dim}'"), json!({"class": class, "task_status": "READY", "feature": feature_id, "objective": format!("Fill readiness dimension '{dim}' for {feature_id} (currently {})", c["state"]), "readiness_cell": dim, "generated_by": "readiness-planner", "dependencies": [], "minimum_model_tier": crate::routing::tier_for_class(p, &class), "minimum_reasoning": "medium", "allowed_paths": ["spec/**"], "forbidden_paths": ["governance/kernel/**", "product/**"], "production_merge_allowed": false, "state_class": "AUTHORITATIVE"}));
        p.schemas().validate("task", &rec.data, &format!("({id})"))?;
        save_record(&p.root, &rec)?;
        created.push(id.clone());
        if c["pre_implementation"].as_bool().unwrap_or(false) { pre_task_ids.push(id); }
    }
    let mut linked = vec![];
    let mut store2 = RecordStore::load(&p.root);
    let impl_ids: Vec<String> = store2.of_type("task").into_iter().filter(|t| t.get("feature") == feature_id && t.get("class") == "implementation").map(|t| t.id()).collect();
    for tid in impl_ids {
        let t = store2.get_mut(&tid).unwrap();
        let mut deps = t.list("dependencies");
        let before = deps.len();
        for g in &pre_task_ids { if !deps.contains(g) && *g != tid { deps.push(g.clone()); } }
        if deps.len() != before { t.set("dependencies", json!(deps)); if t.get("task_status") == "READY" { t.set("task_status", json!("BLOCKED")); } save_record(&p.root, t)?; linked.push(tid); }
    }
    Ok(json!({"feature": feature_id, "created_tasks": created, "pre_implementation_gap_tasks": pre_task_ids, "implementation_tasks_blocked": linked, "gaps": view.gaps, "coverage": view.coverage}))
}
