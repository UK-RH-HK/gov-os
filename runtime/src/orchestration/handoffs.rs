//! Typed A2A handoffs (framework §25) and the spawned-agent return contract (§61). INV-014.
use crate::orchestration::control;
use crate::records::{new_record, save_record, RecordStore};
use crate::util::{now_iso, read_yaml};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub fn create(p: &Project, mut fields: Value) -> Result<Value> {
    control::guard_write(p, "handoff create")?;
    let store = RecordStore::load(&p.root);
    let id = store.next_id("handoff");
    let o = fields.as_object_mut().ok_or_else(|| GovError::new("USAGE", "handoff fields must be an object"))?;
    let to_role = o.get("to_role").and_then(|v| v.as_str()).unwrap_or("").to_string();
    let roles = read_yaml(&p.kernel_dir().join("roles").join("ROLES.yaml")).unwrap_or(json!({}));
    let known: Vec<String> = roles["roles"].as_array().map(|a| a.iter().filter_map(|r| r["id"].as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
    if !known.contains(&to_role) { return Err(GovError::new("UNKNOWN_ROLE", format!("to_role '{to_role}' is not a kernel role"))); }
    if to_role == "orchestrator" && !o.get("explicit_orchestrator_assignment").and_then(|v| v.as_bool()).unwrap_or(false) {
        return Err(GovError::new("INV_014", "a spawned worker must not be handed the orchestrator role unless explicitly assigned (explicit_orchestrator_assignment: true)"));
    }
    let task = o.get("task").and_then(|v| v.as_str()).unwrap_or("").to_string();
    let t = store.get(&task).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("task {task} not found")))?;
    let auth = o.entry("authority").or_insert(json!({}));
    if auth.get("allowed").is_none() { auth["allowed"] = json!(t.list("allowed_paths")); }
    if auth.get("prohibited").is_none() { let mut f = t.list("forbidden_paths"); if !f.iter().any(|x| x == "governance/kernel/**") { f.push("governance/kernel/**".into()); } auth["prohibited"] = json!(f); }
    o.entry("from_role").or_insert(json!(p.role));
    o.entry("inputs").or_insert(json!({"task": task, "context_packet": format!(".governance-runtime/context/{task}.json")}));
    o.entry("expected_outputs").or_insert(json!(["implementation", "evidence"]));
    o.entry("required_return").or_insert(json!(["changed_files", "tests", "discoveries", "unresolved"]));
    o.insert("handoff_status".into(), json!("OPEN"));
    o.insert("state_class".into(), json!("DERIVED"));
    let rec = new_record("handoff", &id, &format!("Handoff {} → {} for {task}", o["from_role"].as_str().unwrap_or(""), to_role), Value::Object(o.clone()));
    p.schemas().validate("handoff", &rec.data, &format!("({id})"))?;
    save_record(&p.root, &rec)?;
    Ok(rec.data)
}

pub fn return_result(p: &Project, id: &str, ret: Value) -> Result<Value> {
    control::guard_write(p, "handoff return")?;
    p.schemas().validate("worker-return", &ret, "(worker return contract)")?;
    let mut store = RecordStore::load(&p.root);
    let h = store.get_mut(id).ok_or_else(|| GovError::new("HANDOFF_NOT_FOUND", format!("{id} not found")))?;
    let allowed = h.data["authority"]["allowed"].as_array().cloned().unwrap_or_default();
    let prohibited = h.data["authority"]["prohibited"].as_array().cloned().unwrap_or_default();
    let mut violations = vec![];
    for f in ret["files_changed"].as_array().cloned().unwrap_or_default() {
        let f = f.as_str().unwrap_or("").to_string();
        if prohibited.iter().any(|pat| crate::util::glob_match(pat.as_str().unwrap_or(""), &f)) { violations.push(format!("{f}: prohibited path")); }
        else if !allowed.is_empty() && !allowed.iter().any(|pat| crate::util::glob_match(pat.as_str().unwrap_or(""), &f)) { violations.push(format!("{f}: outside allowed paths")); }
    }
    h.set("return", ret.clone());
    h.set("returned_at", json!(now_iso()));
    h.set("handoff_status", json!("RETURNED"));
    if !violations.is_empty() { h.set("authority_violations", json!(violations)); }
    save_record(&p.root, h)?;
    if !violations.is_empty() { return Err(GovError::new("MUTATION_SCOPE_VIOLATION", format!("worker changed files outside its authority: {}", violations.join("; "))).with_details(json!({"violations": violations}))); }
    Ok(json!({"handoff": id, "status": "RETURNED", "files_changed": ret["files_changed"], "unresolved": ret["unresolved"]}))
}
