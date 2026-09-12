//! Organisational telemetry (framework §65-66): OpenTelemetry-compatible span/event records as JSONL.
use crate::records::RecordStore;
use crate::util::{now_iso, read_text};
use crate::{Project, Result};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::io::Write;

pub fn path(p: &Project) -> std::path::PathBuf { p.runtime_dir().join("telemetry").join("events.jsonl") }

pub fn emit(p: &Project, name: &str, attributes: Value) -> Result<Value> {
    let ev = json!({"resource": {"service.name": "gov", "service.version": crate::VERSION, "project": p.project_alias()}, "name": name, "timestamp": now_iso(),
        "trace_id": std::env::var("GOV_TRACE_ID").unwrap_or_else(|_| p.session_id.clone()), "span_id": crate::util::short_uuid(), "attributes": attributes, "session": p.session_id, "role": p.role});
    let path = path(p);
    if let Some(d) = path.parent() { std::fs::create_dir_all(d)?; }
    let mut f = std::fs::OpenOptions::new().create(true).append(true).open(&path)?;
    writeln!(f, "{}", serde_json::to_string(&ev)?)?;
    Ok(ev)
}

pub struct Span { pub name: String, pub started: std::time::Instant, pub attrs: Value }
impl Span {
    pub fn start(name: &str, attrs: Value) -> Self { Span { name: name.into(), started: std::time::Instant::now(), attrs } }
    pub fn end(mut self, p: &Project, ok: bool, extra: Value) -> Value {
        let ms = self.started.elapsed().as_millis();
        if let (Some(a), Some(e)) = (self.attrs.as_object_mut(), extra.as_object()) { for (k, v) in e { a.insert(k.clone(), v.clone()); } }
        self.attrs["duration_ms"] = json!(ms); self.attrs["ok"] = json!(ok);
        emit(p, &self.name, self.attrs.clone()).unwrap_or(Value::Null)
    }
}

pub fn events(p: &Project) -> Vec<Value> {
    let path = path(p);
    if !path.exists() { return vec![]; }
    read_text(&path).map(|t| t.lines().filter_map(|l| serde_json::from_str(l).ok()).collect()).unwrap_or_default()
}

/// Answers to framework §66 questions from telemetry, reports and routing evidence.
pub fn summary(p: &Project) -> Result<Value> {
    let evs = events(p);
    let mut by_cmd: BTreeMap<String, (usize, usize, u128)> = BTreeMap::new();
    let mut retrieval: (usize, u128, usize) = (0, 0, 0);
    for e in &evs {
        let name = e["name"].as_str().unwrap_or("").to_string();
        let a = &e["attributes"];
        let ent = by_cmd.entry(name.clone()).or_insert((0, 0, 0));
        ent.0 += 1; if a["ok"].as_bool().unwrap_or(true) { ent.1 += 1; } ent.2 += a["duration_ms"].as_u64().unwrap_or(0) as u128;
        if name == "retrieval" { retrieval.0 += 1; retrieval.1 += a["latency_ms"].as_u64().unwrap_or(0) as u128; retrieval.2 += a["hits"].as_u64().unwrap_or(0) as usize; }
    }
    let store = RecordStore::load(&p.root);
    let reports = store.of_type("report");
    let mut rework_by_role: BTreeMap<String, (usize, usize)> = BTreeMap::new();
    let mut first_pass = (0usize, 0usize);
    let mut cost_by_class: BTreeMap<String, f64> = BTreeMap::new();
    for r in &reports {
        let role = r.get("role"); let rep = r.data.get("repair_count").and_then(|v| v.as_u64()).unwrap_or(0) as usize;
        let e = rework_by_role.entry(role).or_insert((0, 0)); e.0 += 1; e.1 += rep;
        first_pass.0 += 1; if rep == 0 && r.get("outcome") == "success" { first_pass.1 += 1; }
        let class = store.get(&r.get("task")).map(|t| t.get("class")).unwrap_or("unknown".into());
        *cost_by_class.entry(class).or_insert(0.0) += r.data.get("cost").and_then(|c| c.get("usd")).and_then(|v| v.as_f64()).unwrap_or(0.0);
    }
    let gates_by_feature: BTreeMap<String, usize> = store.of_type("human-gate").iter().fold(BTreeMap::new(), |mut m, g| { for t in g.list("blocks_tasks") { let f = store.get(&t).map(|x| x.get("feature")).unwrap_or_default(); *m.entry(f).or_insert(0) += 1; } m });
    // BUDGET_POLICY.defaults.max_network_calls_per_task: network.call events per task vs budget
    let max_net = p.policies().get_i64("BUDGET_POLICY", "defaults.max_network_calls_per_task", 200);
    let mut net_by_task: BTreeMap<String, i64> = BTreeMap::new();
    for e in &evs { if e["name"] == "network.call" { *net_by_task.entry(e["attributes"]["task"].as_str().unwrap_or("unassigned").to_string()).or_insert(0) += 1; } }
    let net_over: Vec<Value> = net_by_task.iter().filter(|(_, n)| **n > max_net).map(|(t, n)| json!({"task": t, "network_calls": n, "budget": max_net})).collect();
    Ok(json!({
        "budget": {"max_network_calls_per_task": max_net, "network_calls_by_task": net_by_task, "over_budget": net_over, "max_parallel_agents": p.policies().get_i64("BUDGET_POLICY", "defaults.max_parallel_agents", 4), "active_sessions": crate::orchestration::claims::active_sessions(p).unwrap_or_default()},
        "events": evs.len(),
        "commands": by_cmd.iter().map(|(k, (n, ok, ms))| json!({"name": k, "count": n, "ok": ok, "avg_ms": if *n > 0 { *ms as f64 / *n as f64 } else { 0.0 }})).collect::<Vec<_>>(),
        "retrieval": {"queries": retrieval.0, "avg_latency_ms": if retrieval.0 > 0 { retrieval.1 as f64 / retrieval.0 as f64 } else { 0.0 }, "avg_hits": if retrieval.0 > 0 { retrieval.2 as f64 / retrieval.0 as f64 } else { 0.0 }},
        "rework_by_role": rework_by_role.iter().map(|(r, (n, rep))| json!({"role": r, "reports": n, "repairs": rep, "repairs_per_report": *rep as f64 / (*n).max(1) as f64})).collect::<Vec<_>>(),
        "first_pass_completion_rate": if first_pass.0 > 0 { first_pass.1 as f64 / first_pass.0 as f64 } else { Value::Null.as_f64().unwrap_or(1.0) },
        "cost_by_task_class": cost_by_class, "human_gates_by_feature": gates_by_feature,
        "model_routing": crate::routing::report(p)?["rows"],
    }))
}
