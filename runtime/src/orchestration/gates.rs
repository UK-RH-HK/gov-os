//! Human Decision Gates (framework §50-54). INV-008: a gate that exists only in a file is not presented.
use crate::orchestration::control;
use crate::records::{new_record, save_record, RecordStore};
use crate::util::{now_iso, today};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub fn create(p: &Project, mut fields: Value) -> Result<Value> {
    control::guard_write(p, "gate create")?;
    let store = RecordStore::load(&p.root);
    let id = fields.get("id").and_then(|v| v.as_str()).map(|s| s.to_string()).unwrap_or_else(|| store.next_id("human-gate"));
    let question = fields.get("question").and_then(|v| v.as_str()).unwrap_or("").to_string();
    if question.is_empty() { return Err(GovError::new("USAGE", "a human gate needs a question")); }
    let o = fields.as_object_mut().unwrap();
    o.insert("gate_status".into(), json!("PENDING"));
    o.insert("presented_in_chat".into(), json!(false));
    o.entry("options").or_insert(json!([]));
    o.entry("permitted_next_actions").or_insert(json!(["gov decide <gate> --option <id>", "continue independent runnable work"]));
    o.entry("blocks_tasks").or_insert(json!([]));
    let blocked = o.get("blocks_tasks").and_then(|v| v.as_array()).map(|a| a.len()).unwrap_or(0);
    let radius_w = match o.get("impact_radius").and_then(|v| v.as_str()).unwrap_or("R1") { "R5" => 5.0, "R4" => 4.0, "R3" => 3.0, "R2" => 2.0, _ => 1.0 };
    let irreversible = if o.get("reversibility").and_then(|v| v.as_str()).map(|s| s.to_lowercase().contains("irrevers") || s == "low").unwrap_or(false) { 2.0 } else { 0.0 };
    o.insert("priority_score".into(), json!(blocked as f64 * 2.0 + radius_w + irreversible));
    o.remove("id");
    let title = o.get("title").and_then(|v| v.as_str()).unwrap_or(&question).to_string();
    o.remove("title");
    let rec = new_record("human-gate", &id, &title, Value::Object(o.clone()));
    p.schemas().validate("human-gate", &rec.data, &format!("({id})"))?;
    save_record(&p.root, &rec)?;
    // block the tasks
    let mut store2 = RecordStore::load(&p.root);
    for t in rec.data["blocks_tasks"].as_array().cloned().unwrap_or_default() {
        if let Some(tr) = t.as_str().and_then(|s| store2.get_mut(s)) { tr.set("human_gate", json!(id)); if tr.get("task_status") != "DONE" { tr.set("task_status", json!("WAITING_HUMAN")); } save_record(&p.root, tr)?; }
    }
    Ok(rec.data)
}

/// Render the decision package for the active chat and mark it presented.
pub fn present(p: &Project, id: &str) -> Result<(Value, String)> {
    let mut store = RecordStore::load(&p.root);
    let g = store.get_mut(id).ok_or_else(|| GovError::new("GATE_NOT_FOUND", format!("{id} not found")))?;
    if g.rtype() != "human-gate" { return Err(GovError::new("USAGE", format!("{id} is not a human gate"))); }
    if g.get("gate_status") == "PENDING" { g.set("gate_status", json!("PRESENTED")); }
    g.set("presented_in_chat", json!(true));
    g.set("presented_at", json!(now_iso()));
    save_record(&p.root, g)?;
    let d = &g.data;
    let mut text = format!("HUMAN DECISION GATE {id}\nQuestion: {}\nWhy now: {}\nCurrent state: {}\n", d["question"].as_str().unwrap_or(""), d["why_now"].as_str().unwrap_or("-"), d["current_state"].as_str().unwrap_or("-"));
    if let Some(opts) = d["options"].as_array() { text.push_str("Options:\n"); for o in opts { text.push_str(&format!("  [{}] {} {}\n", o["id"].as_str().unwrap_or("?"), o["description"].as_str().unwrap_or(""), o.get("impact").and_then(|v| v.as_str()).map(|s| format!("(impact: {s})")).unwrap_or_default())); } }
    text.push_str(&format!("Impact: {}\nReversibility: {}\nCost/rework: {}\nRecommendation: {}\nConfidence: {}\nPermitted next actions: {}\n",
        d["impact"].as_str().unwrap_or("-"), d["reversibility"].as_str().unwrap_or("-"), d["cost_rework"].as_str().unwrap_or("-"), d["recommendation"].as_str().unwrap_or("-"), d["confidence"], d["permitted_next_actions"]));
    Ok((d.clone(), text))
}

pub fn pending(p: &Project) -> Vec<Value> {
    let store = RecordStore::load(&p.root);
    let mut v: Vec<Value> = store.of_type("human-gate").into_iter().filter(|g| matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED"))
        .map(|g| json!({"id": g.id(), "question": g.get("question"), "gate_status": g.get("gate_status"), "presented_in_chat": g.data.get("presented_in_chat").and_then(|v| v.as_bool()).unwrap_or(false), "priority_score": g.data.get("priority_score").and_then(|v| v.as_f64()).unwrap_or(0.0), "blocks_tasks": g.list("blocks_tasks"), "cit": g.get("cit")})).collect();
    v.sort_by(|a, b| b["priority_score"].as_f64().partial_cmp(&a["priority_score"].as_f64()).unwrap_or(std::cmp::Ordering::Equal));
    v
}

/// Answer a gate: records the decision, unblocks tasks, links to a CIT if any.
pub fn answer(p: &Project, id: &str, option: &str, by: &str, rationale: Option<&str>) -> Result<Value> {
    control::guard_write(p, "gate answer")?;
    let mut store = RecordStore::load(&p.root);
    let g = store.get_mut(id).ok_or_else(|| GovError::new("GATE_NOT_FOUND", format!("{id} not found")))?;
    if !matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED") { return Err(GovError::new("USAGE", format!("{id} is {}", g.get("gate_status")))); }
    let presented = g.data.get("presented_in_chat").and_then(|v| v.as_bool()).unwrap_or(false);
    if !presented { return Err(GovError::new("GATE_NOT_PRESENTED", format!("{id} has not been presented in chat (INV-008); run `gov gate present {id}` and show it to the human first"))); }
    g.set("gate_status", json!("ANSWERED"));
    g.set("answer", json!({"option": option, "by": by, "at": now_iso(), "rationale": rationale}));
    let gdata = g.data.clone();
    save_record(&p.root, g)?;
    let did = store.next_id("decision");
    let dec = new_record("decision", &did, &format!("Decision for {id}: option {option}"), json!({"question": gdata["question"], "options": gdata["options"], "chosen_option": option, "rationale": rationale.unwrap_or(""), "approved_by": by, "approved_at": now_iso(), "human_approved": true, "impact_radius": gdata.get("impact_radius").cloned().unwrap_or(json!("R1")), "reversibility": gdata.get("reversibility").cloned().unwrap_or(json!("unknown")), "confidence": 1.0, "governed_by": [], "derived_from": [id], "cit": gdata.get("cit").cloned().unwrap_or(Value::Null), "state_class": "AUTHORITATIVE"}));
    let mut dec = dec; if dec.data["cit"].is_null() { dec.data.as_object_mut().unwrap().remove("cit"); }
    save_record(&p.root, &dec)?;
    // link the decision to the CIT that raised the gate (so approval reuses it instead of minting another)
    if let Some(cit_id) = gdata.get("cit").and_then(|v| v.as_str()).filter(|c| !c.is_empty()) {
        let mut sc = RecordStore::load(&p.root);
        if let Some(c) = sc.get_mut(cit_id) { if c.get("decision").is_empty() { c.set("decision", json!(did)); save_record(&p.root, c)?; } }
    }
    let mut unblocked = vec![];
    let mut store2 = RecordStore::load(&p.root);
    for t in gdata["blocks_tasks"].as_array().cloned().unwrap_or_default() {
        if let Some(tr) = t.as_str().and_then(|s| store2.get_mut(s)) { if tr.get("task_status") == "WAITING_HUMAN" { tr.set("task_status", json!("READY")); tr.set("updated", json!(today())); save_record(&p.root, tr)?; unblocked.push(tr.id()); } }
    }
    Ok(json!({"gate": id, "decision": did, "option": option, "unblocked_tasks": unblocked, "cit": gdata.get("cit")}))
}
