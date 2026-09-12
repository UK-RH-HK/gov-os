//! Dynamic task DAG (framework §41-44): runnable/blocked sets, longest chain, cycles, human-gate dependencies, replan.
use crate::orchestration::readiness;
use crate::records::{save_record, RecordStore};
use crate::util::today;
use crate::{Project, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Clone, serde::Serialize)]
pub struct DagView { pub runnable: Vec<String>, pub blocked: Vec<Value>, pub waiting_human: Vec<Value>, pub done: Vec<String>, pub longest_chain: Vec<String>, pub cycles: Vec<Vec<String>>, pub per_feature: Value, pub human_gate_dependencies: Vec<Value>, pub counts: Value, pub missing_dependencies: Vec<Value> }

pub fn compute(p: &Project) -> Result<DagView> {
    let store = RecordStore::load(&p.root);
    let tasks: Vec<&crate::records::Record> = store.of_type("task");
    let ids: BTreeSet<String> = tasks.iter().map(|t| t.id()).collect();
    let enforce = p.project_policy().get("readiness").and_then(|r| r.get("enforce_pre_implementation_cells")).and_then(|v| v.as_bool()).unwrap_or(true);
    let gates: BTreeMap<String, String> = store.of_type("human-gate").into_iter().map(|g| (g.id(), g.get("gate_status"))).collect();
    let status_of: BTreeMap<String, String> = tasks.iter().map(|t| (t.id(), t.get("task_status"))).collect();
    let mut runnable = vec![]; let mut blocked = vec![]; let mut waiting = vec![]; let mut done = vec![]; let mut missing = vec![]; let mut gate_deps = vec![];
    let mut per_feature: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for t in &tasks {
        let id = t.id();
        let st = t.get("task_status");
        per_feature.entry(t.get("feature")).or_default().push(id.clone());
        if st == "DONE" || st == "CANCELLED" { done.push(id); continue; }
        let mut reasons = vec![];
        for d in t.list("dependencies") {
            match status_of.get(&d) {
                Some(s) if s == "DONE" => {}
                Some(s) => reasons.push(format!("dependency {d} is {s}")),
                None => { if ids.contains(&d) { reasons.push(format!("dependency {d} unknown status")); } else { missing.push(json!({"task": id, "dependency": d})); reasons.push(format!("dependency {d} missing")); } }
            }
        }
        let gate = t.get("human_gate");
        if !gate.is_empty() {
            let gs = gates.get(&gate).cloned().unwrap_or("MISSING".into());
            gate_deps.push(json!({"task": id, "gate": gate, "gate_status": gs}));
            if gs == "PENDING" || gs == "PRESENTED" { waiting.push(json!({"task": id, "gate": gate})); continue; }
        }
        if enforce && t.get("class") == "implementation" && !t.get("feature").is_empty() {
            if let Some(f) = store.get(&t.get("feature")) {
                let r = readiness::evaluate(p, f);
                if !r.pre_implementation_ok { reasons.push(format!("feature {} pre-implementation readiness cells missing: {}", f.id(), r.pre_implementation_gaps.join(", "))); }
            }
        }
        if t.data.get("retest_required").and_then(|v| v.as_bool()).unwrap_or(false) { reasons.push("retest required after CIT propagation".into()); }
        if reasons.is_empty() {
            if st == "DRAFT" { blocked.push(json!({"task": id, "reasons": ["DRAFT: promote with `gov task status <id> READY`"]})); } else { runnable.push(id); }
        } else { blocked.push(json!({"task": id, "reasons": reasons})); }
    }
    // cycles + longest chain over open tasks
    let open: BTreeSet<String> = tasks.iter().filter(|t| !matches!(t.get("task_status").as_str(), "DONE" | "CANCELLED")).map(|t| t.id()).collect();
    let deps: BTreeMap<String, Vec<String>> = tasks.iter().map(|t| (t.id(), t.list("dependencies").into_iter().filter(|d| open.contains(d)).collect())).collect();
    let mut cycles = vec![];
    let mut color: BTreeMap<String, u8> = BTreeMap::new();
    fn dfs(n: &str, deps: &BTreeMap<String, Vec<String>>, color: &mut BTreeMap<String, u8>, stack: &mut Vec<String>, cycles: &mut Vec<Vec<String>>) {
        color.insert(n.to_string(), 1); stack.push(n.to_string());
        for d in deps.get(n).cloned().unwrap_or_default() {
            match color.get(&d).copied().unwrap_or(0) { 0 => dfs(&d, deps, color, stack, cycles), 1 => { let pos = stack.iter().position(|x| x == &d).unwrap_or(0); cycles.push(stack[pos..].to_vec()); } _ => {} }
        }
        stack.pop(); color.insert(n.to_string(), 2);
    }
    for n in &open { if color.get(n).copied().unwrap_or(0) == 0 { let mut st = vec![]; dfs(n, &deps, &mut color, &mut st, &mut cycles); } }
    let mut memo: BTreeMap<String, Vec<String>> = BTreeMap::new();
    fn longest(n: &str, deps: &BTreeMap<String, Vec<String>>, memo: &mut BTreeMap<String, Vec<String>>, depth: usize) -> Vec<String> {
        if let Some(v) = memo.get(n) { return v.clone(); }
        if depth > 500 { return vec![n.to_string()]; }
        let mut best: Vec<String> = vec![];
        for d in deps.get(n).cloned().unwrap_or_default() { let c = longest(&d, deps, memo, depth + 1); if c.len() > best.len() { best = c; } }
        let mut out = best; out.push(n.to_string());
        memo.insert(n.to_string(), out.clone()); out
    }
    let mut longest_chain: Vec<String> = vec![];
    if cycles.is_empty() { for n in &open { let c = longest(n, &deps, &mut memo, 0); if c.len() > longest_chain.len() { longest_chain = c; } } }
    let counts = json!({"total": tasks.len(), "runnable": runnable.len(), "blocked": blocked.len(), "waiting_human": waiting.len(), "done": done.len(), "open": open.len()});
    let pf: Value = json!(per_feature);
    Ok(DagView { runnable, blocked, waiting_human: waiting, done, longest_chain, cycles, per_feature: pf, human_gate_dependencies: gate_deps, counts, missing_dependencies: missing })
}

/// Recompute and persist READY/BLOCKED/WAITING_HUMAN for open non-DRAFT tasks.
pub fn replan(p: &Project) -> Result<Value> {
    crate::orchestration::control::guard_write(p, "replan")?;
    let view = compute(p)?;
    let mut store = RecordStore::load(&p.root);
    let mut changed = vec![];
    let blocked_ids: BTreeSet<String> = view.blocked.iter().filter_map(|b| b["task"].as_str().map(|s| s.to_string())).collect();
    let waiting_ids: BTreeSet<String> = view.waiting_human.iter().filter_map(|b| b["task"].as_str().map(|s| s.to_string())).collect();
    let ids: Vec<String> = store.of_type("task").iter().map(|t| t.id()).collect();
    for id in ids {
        let rec = store.get_mut(&id).unwrap();
        let st = rec.get("task_status");
        let target = if view.runnable.contains(&id) { "READY" } else if waiting_ids.contains(&id) { "WAITING_HUMAN" } else if blocked_ids.contains(&id) && st != "DRAFT" { "BLOCKED" } else { continue };
        if matches!(st.as_str(), "DONE" | "CANCELLED" | "IN_PROGRESS" | "CLAIMED" | "REVIEW") { continue; }
        if st != target { rec.set("task_status", json!(target)); rec.set("updated", json!(today())); save_record(&p.root, rec)?; changed.push(json!({"task": id, "from": st, "to": target})); }
    }
    Ok(json!({"changed": changed, "runnable": view.runnable, "blocked": view.blocked.len(), "waiting_human": view.waiting_human.len(), "cycles": view.cycles}))
}
