//! Human Decision Gates (framework §50-54, HUMAN_GATE_POLICY). INV-008: a gate that exists only in a file is not
//! presented; answers are recorded only for presented gates, by a human or (within `agent_resolvable_when`) by an
//! L3+ agent.
use crate::authority;
use crate::orchestration::control;
use crate::records::{new_record, save_record, RecordStore};
use crate::util::{now_iso, today};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

fn radius_rank(r: &str) -> u8 { r.strip_prefix('R').and_then(|n| n.parse().ok()).unwrap_or(5) }

fn build(p: &Project, mut fields: Value) -> Result<crate::records::Record> {
    let pol = p.policies();
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
    // HUMAN_GATE_POLICY.decision_package_fields: every field must be present (explicit "not assessed" beats silence)
    for f in pol.get_list("HUMAN_GATE_POLICY", "decision_package_fields") {
        if !o.contains_key(&f) { let v = match f.as_str() { "options" | "permitted_next_actions" => json!([]), "confidence" => json!(0.5), _ => json!("not assessed") }; o.insert(f, v); }
    }
    // HUMAN_GATE_POLICY.prioritisation: ordered criteria weighted by position
    let crit = pol.get_list("HUMAN_GATE_POLICY", "prioritisation");
    let weight = |name: &str| crit.iter().position(|c| c == name).map(|i| (crit.len() - i) as f64).unwrap_or(1.0);
    let blocked = o.get("blocks_tasks").and_then(|v| v.as_array()).map(|a| a.len()).unwrap_or(0) as f64;
    let radius = radius_rank(o.get("impact_radius").and_then(|v| v.as_str()).unwrap_or("R1")) as f64;
    let irreversible = if o.get("reversibility").and_then(|v| v.as_str()).map(|s| s.to_lowercase().contains("irrevers") || s == "low").unwrap_or(false) { 1.0 } else { 0.0 };
    let time_sensitive = if o.get("time_sensitive").and_then(|v| v.as_bool()).unwrap_or(false) { 1.0 } else { 0.0 };
    o.insert("priority_score".into(), json!(blocked * weight("tasks_blocked") + blocked * weight("critical_path_effect") * 0.5 + radius * weight("impact_radius") + irreversible * weight("irreversibility") * 2.0 + time_sensitive * weight("time_sensitivity")));
    o.remove("id");
    let title = o.get("title").and_then(|v| v.as_str()).unwrap_or(&question).to_string();
    o.remove("title");
    let rec = new_record("human-gate", &id, &title, Value::Object(o.clone()));
    p.schemas().validate("human-gate", &rec.data, &format!("({id})"))?;
    Ok(rec)
}

fn block_tasks(p: &Project, rec: &crate::records::Record) -> Result<()> {
    let mut store2 = RecordStore::load(&p.root);
    for t in rec.data["blocks_tasks"].as_array().cloned().unwrap_or_default() {
        if let Some(tr) = t.as_str().and_then(|s| store2.get_mut(s)) { tr.set("human_gate", json!(rec.id())); if tr.get("task_status") != "DONE" { tr.set("task_status", json!("WAITING_HUMAN")); } save_record(&p.root, tr)?; }
    }
    Ok(())
}

/// Create a gate on behalf of an acting role (authority-checked).
pub fn create(p: &Project, fields: Value) -> Result<Value> {
    control::guard_write(p, "gate create")?;
    authority::require(p, "create_gate")?;
    let rec = build(p, fields)?;
    save_record(&p.root, &rec)?;
    block_tasks(p, &rec)?;
    Ok(rec.data)
}

/// Create a gate raised by the system itself (budget/threshold/update/migration triggers) — not subject to the
/// acting role's authority, because the gate is the mechanism that stops the acting role.
pub fn create_system(p: &Project, fields: Value) -> Result<Value> {
    let rec = build(p, fields)?;
    save_record(&p.root, &rec)?;
    block_tasks(p, &rec)?;
    Ok(rec.data)
}

/// Render the decision package for the active chat and mark it presented.
pub fn present(p: &Project, id: &str) -> Result<(Value, String)> {
    authority::require(p, "present_gate")?;
    let mut store = RecordStore::load(&p.root);
    let g = store.get_mut(id).ok_or_else(|| GovError::new("GATE_NOT_FOUND", format!("{id} not found")))?;
    if g.rtype() != "human-gate" { return Err(GovError::new("USAGE", format!("{id} is not a human gate"))); }
    if g.get("gate_status") == "PENDING" { g.set("gate_status", json!("PRESENTED")); }
    g.set("presented_in_chat", json!(true)); g.set("presented_at", json!(now_iso()));
    save_record(&p.root, g)?;
    let d = &g.data;
    let mut text = format!("HUMAN DECISION GATE {id}\nQuestion: {}\nWhy now: {}\nCurrent state: {}\n", d["question"].as_str().unwrap_or(""), d["why_now"].as_str().unwrap_or("-"), d["current_state"].as_str().unwrap_or("-"));
    if let Some(opts) = d["options"].as_array() { text.push_str("Options:\n"); for o in opts { text.push_str(&format!("  [{}] {} {}\n", o["id"].as_str().unwrap_or("?"), o["description"].as_str().unwrap_or(""), o.get("impact").and_then(|v| v.as_str()).map(|s| format!("(impact: {s})")).unwrap_or_default())); } }
    text.push_str(&format!("Impact: {}\nReversibility: {}\nCost/rework: {}\nRecommendation: {}\nConfidence: {}\nPermitted next actions: {}\n", d["impact"].as_str().unwrap_or("-"), d["reversibility"].as_str().unwrap_or("-"), d["cost_rework"].as_str().unwrap_or("-"), d["recommendation"].as_str().unwrap_or("-"), d["confidence"], d["permitted_next_actions"]));
    Ok((d.clone(), text))
}

pub fn pending(p: &Project) -> Vec<Value> {
    let store = RecordStore::load(&p.root);
    let batch_low = p.policies().get_bool("HUMAN_GATE_POLICY", "batch_low_priority", true);
    let mut v: Vec<Value> = store.of_type("human-gate").into_iter().filter(|g| matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED"))
        .map(|g| { let score = g.data.get("priority_score").and_then(|v| v.as_f64()).unwrap_or(0.0); json!({"id": g.id(), "question": g.get("question"), "gate_status": g.get("gate_status"), "presented_in_chat": g.data.get("presented_in_chat").and_then(|v| v.as_bool()).unwrap_or(false), "priority_score": score, "batchable": batch_low && score < 3.0, "blocks_tasks": g.list("blocks_tasks"), "cit": g.get("cit"), "trigger": g.get("trigger")}) }).collect();
    v.sort_by(|a, b| b["priority_score"].as_f64().partial_cmp(&a["priority_score"].as_f64()).unwrap_or(std::cmp::Ordering::Equal));
    v
}

/// The recorded answer of a presented gate (`Some(option)`), or `None` while it is pending / never presented.
pub fn answered_option(p: &Project, gate_id: &str) -> Option<String> {
    let store = RecordStore::load(&p.root);
    store.get(gate_id).filter(|g| g.get("gate_status") == "ANSWERED" && g.data.get("presented_in_chat").and_then(|v| v.as_bool()).unwrap_or(false)).and_then(|g| g.data["answer"]["option"].as_str().map(|s| s.to_string()))
}

pub fn is_answered_yes(p: &Project, gate_id: &str) -> bool {
    let store = RecordStore::load(&p.root);
    store.get(gate_id).map(|g| g.get("gate_status") == "ANSWERED" && g.data["answer"]["option"].as_str() == Some("A") && g.data.get("presented_in_chat").and_then(|v| v.as_bool()).unwrap_or(false)).unwrap_or(false)
}

/// Answer a gate. `by` is the answerer: a human identity (relayed by an L3+ role or given by the `human` role) or a
/// kernel role id (agent resolution, allowed only within HUMAN_GATE_POLICY.agent_resolvable_when for L3+ roles).
pub fn answer(p: &Project, id: &str, option: &str, by: &str, rationale: Option<&str>) -> Result<Value> {
    control::guard_write(p, "gate answer")?;
    let pol = p.policies();
    let mut store = RecordStore::load(&p.root);
    let g = store.get_mut(id).ok_or_else(|| GovError::new("GATE_NOT_FOUND", format!("{id} not found")))?;
    if !matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED") { return Err(GovError::new("USAGE", format!("{id} is {}", g.get("gate_status")))); }
    let presented = g.data.get("presented_in_chat").and_then(|v| v.as_bool()).unwrap_or(false);
    if pol.get_bool("HUMAN_GATE_POLICY", "must_be_presented_in_chat", true) && !presented { return Err(GovError::new("GATE_NOT_PRESENTED", format!("{id} has not been presented in chat (INV-008); run `gov gate present {id}` and show it to the human first"))); }
    let acting = authority::level_of(p, &p.role)?;
    let by_is_agent = authority::is_kernel_role(p, by) && by != "human";
    let kind = if by_is_agent {
        // agent-resolvable contradictions only (framework §50): low impact, high confidence, reversible; L3+ acting role
        let max_r = pol.get_str("HUMAN_GATE_POLICY", "agent_resolvable_when.max_radius", "R1");
        let min_c = pol.get_f64("HUMAN_GATE_POLICY", "agent_resolvable_when.min_confidence", 0.8);
        let need_rev = pol.get_bool("HUMAN_GATE_POLICY", "agent_resolvable_when.reversible", true);
        let radius = g.get("impact_radius"); let radius = if radius.is_empty() { "R5".to_string() } else { radius };
        let conf = g.data.get("confidence").and_then(|v| v.as_f64()).unwrap_or(0.0);
        let rev = g.get("reversibility").to_lowercase(); let reversible = !(rev.contains("irrevers") || rev == "low") && !rev.is_empty();
        let ok = radius_rank(&radius) <= radius_rank(&max_r) && conf >= min_c && (!need_rev || reversible) && acting >= 3;
        if !ok { return Err(GovError::new("AUTHORITY_DENIED", format!("agent '{by}' (acting role {} L{acting}) may not answer {id}: agent_resolvable_when requires radius <= {max_r} (gate {radius}), confidence >= {min_c} (gate {conf}), reversible ({reversible}) and an L3+ acting role", p.role)).with_details(json!({"operation": "answer_gate_as_agent", "role": p.role, "level": format!("L{acting}")}))); }
        "agent"
    } else {
        let need = authority::required_level(p, "answer_gate");
        if acting < need { return Err(GovError::new("AUTHORITY_DENIED", format!("role '{}' (L{acting}) may not record a human answer for {id} (requires L{need}: a change controller/orchestrator relaying the human, or --role human)", p.role)).with_details(json!({"operation": "answer_gate", "role": p.role, "level": format!("L{acting}"), "required": format!("L{need}")}))); }
        "human"
    };
    g.set("gate_status", json!("ANSWERED"));
    g.set("answer", json!({"option": option, "by": by, "by_kind": kind, "acting_role": p.role, "at": now_iso(), "rationale": rationale}));
    let gdata = g.data.clone();
    save_record(&p.root, g)?;
    let did = store.next_id("decision");
    let mut dec = new_record("decision", &did, &format!("Decision for {id}: option {option}"), json!({"question": gdata["question"], "options": gdata["options"], "chosen_option": option, "rationale": rationale.unwrap_or(""), "approved_by": by, "approved_at": now_iso(), "human_approved": kind == "human", "impact_radius": gdata.get("impact_radius").cloned().unwrap_or(json!("R1")), "reversibility": gdata.get("reversibility").cloned().unwrap_or(json!("unknown")), "confidence": if kind == "human" { 1.0 } else { gdata.get("confidence").and_then(|v| v.as_f64()).unwrap_or(0.8) }, "derived_from": [id], "cit": gdata.get("cit").cloned().unwrap_or(Value::Null), "state_class": "AUTHORITATIVE"}));
    if dec.data["cit"].is_null() { dec.data.as_object_mut().unwrap().remove("cit"); }
    save_record(&p.root, &dec)?;
    if let Some(cit_id) = gdata.get("cit").and_then(|v| v.as_str()).filter(|c| !c.is_empty()) { let mut sc = RecordStore::load(&p.root); if let Some(c) = sc.get_mut(cit_id) { if c.get("decision").is_empty() { c.set("decision", json!(did)); save_record(&p.root, c)?; } } }
    let mut unblocked = vec![];
    let mut store2 = RecordStore::load(&p.root);
    for t in gdata["blocks_tasks"].as_array().cloned().unwrap_or_default() { if let Some(tr) = t.as_str().and_then(|s| store2.get_mut(s)) { if tr.get("task_status") == "WAITING_HUMAN" { tr.set("task_status", json!("READY")); tr.set("updated", json!(today())); save_record(&p.root, tr)?; unblocked.push(tr.id()); } } }
    Ok(json!({"gate": id, "decision": did, "option": option, "answered_by_kind": kind, "unblocked_tasks": unblocked, "cit": gdata.get("cit")}))
}
