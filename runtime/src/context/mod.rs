//! Context compiler (framework §15): deterministic authority block (hash-stable) + retrieved intelligence block.
use crate::memory::db::RuntimeDb;
use crate::orchestration::control;
use crate::records::RecordStore;
use crate::retrieval::{retrieve, RetrieveOptions};
use crate::util::{hash_value, now_iso, sorted, write_json};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

fn brief(r: &crate::records::Record) -> Value {
    let mut v = json!({"id": r.id(), "type": r.rtype(), "title": r.title(), "status": r.status(), "path": r.path});
    for k in ["summary", "objective", "question", "chosen_option", "rationale", "kind", "acceptance_criteria", "given", "when", "then", "success_criteria", "failure_criteria", "contract", "readiness", "class"] {
        if let Some(x) = r.data.get(k) { v[k] = x.clone(); }
    }
    v
}

pub fn compile(p: &Project, db: &RuntimeDb, task_id: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let task = store.get(task_id).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("task {task_id} not found")))?;
    if task.rtype() != "task" { return Err(GovError::new("USAGE", format!("{task_id} is not a task"))); }
    let pol = p.policies();
    let feature_id = task.get("feature");
    let feature = store.get(&feature_id).filter(|r| r.rtype() == "feature");
    let mut req_ids = task.list("requirements");
    if let Some(f) = feature { req_ids.extend(f.list("requirements")); }
    let mut dec_ids = task.list("decisions");
    for d in store.active("decision") {
        if d.list("affects").contains(&feature_id) || d.list("affects").contains(&task_id.to_string()) || (!feature_id.is_empty() && d.list("governed_by").contains(&feature_id)) { dec_ids.push(d.id()); }
    }
    dec_ids.sort(); dec_ids.dedup();
    let mut scn_ids = task.list("scenarios");
    if let Some(f) = feature { scn_ids.extend(f.list("scenarios")); }
    scn_ids.sort(); scn_ids.dedup();
    let mut iface_ids = vec![];
    if let Some(f) = feature { iface_ids.extend(f.list("interfaces")); }
    let mut acceptance: Vec<Value> = vec![];
    for s in &scn_ids { if let Some(r) = store.get(s) { for c in r.list("success_criteria") { acceptance.push(json!({"scenario": s, "criterion": c})); } for c in r.list("then") { acceptance.push(json!({"scenario": s, "then": c})); } } }
    for t in task.list("acceptance_tests") { acceptance.push(json!({"test": t})); }
    let collect = |ids: &[String], want: &str| -> Vec<Value> { ids.iter().filter_map(|i| store.get(i)).filter(|r| want.is_empty() || r.rtype() == want).map(brief).collect() };
    let mut prohibited = task.list("forbidden_paths");
    prohibited.push("governance/kernel/**".into());
    for r in &p.contract().rules { if r.get("mutation").and_then(|m| m.as_str()) == Some("prohibited") { if let Some(pat) = r.get("pattern").and_then(|x| x.as_str()) { prohibited.push(pat.to_string()); } } }
    prohibited.sort(); prohibited.dedup();
    let dependency_state: Vec<Value> = task.list("dependencies").iter().map(|d| json!({"id": d, "task_status": store.get(d).map(|r| r.get("task_status")).unwrap_or("MISSING".into())})).collect();
    let skills: Vec<Value> = task.list("required_skills").iter().map(|s| { let sk = crate::skills::find_skill(p, s); json!({"id": s, "version": sk.as_ref().map(|k| k["version"].clone()).unwrap_or(Value::Null), "resolved": sk.is_some()}) }).collect();
    let ctl = control::state(p);
    let mut status_counts = serde_json::Map::new();
    for t in store.of_type("task") { let s = t.get("task_status"); *status_counts.entry(s).or_insert(json!(0)) = json!(status_counts.get(&t.get("task_status")).and_then(|v| v.as_i64()).unwrap_or(0) + 1); }
    let pending_gates: Vec<String> = store.of_type("human-gate").into_iter().filter(|g| matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED")).map(|g| g.id()).collect();
    let det = json!({
        "task": brief(task), "objective": task.get("objective"),
        "project_state": {"framework_version": p.framework_version(), "task_status_counts": status_counts, "pending_human_gates": pending_gates, "control": ctl.get("mode"), "projects": store.of_type("project").iter().map(|r| brief(r)).collect::<Vec<_>>()},
        "feature": feature.map(brief), "governing_requirements": collect(&req_ids, "requirement"), "active_decisions": collect(&dec_ids, "decision"),
        "architecture": store.active("architecture").iter().map(|r| brief(r)).collect::<Vec<_>>(), "interfaces": collect(&iface_ids, "interface"), "scenarios": collect(&scn_ids, "scenario"),
        "acceptance_criteria": acceptance, "allowed_writes": task.list("allowed_paths"), "prohibited_writes": prohibited, "required_skills": skills, "required_tools": task.list("required_tools"),
        "dependency_state": dependency_state, "minimum_model_tier": task.get("minimum_model_tier"), "minimum_reasoning": task.get("minimum_reasoning"),
    });
    let det = sorted(&det);
    let det_hash = hash_value(&det);
    let query = format!("{} {}", task.title(), task.get("objective"));
    let k = pol.get_i64("CONTEXT_POLICY", "max_retrieved_slices", 12) as usize;
    let res = retrieve(p, db, &query, RetrieveOptions { k, log: true, ..Default::default() })?;
    let lessons = retrieve(p, db, &query, RetrieveOptions { k: 5, record_types: vec!["lesson".into(), "report".into()], ..Default::default() })?;
    let mut code_refs = vec![];
    for tok in crate::memory::embeddings::tokenize(&query).into_iter().filter(|t| t.len() > 3).take(12) {
        for r in db.query("SELECT path, qualname, kind FROM symbols WHERE name=?1 LIMIT 3", &[&tok])? { code_refs.push(r); }
    }
    let ret = json!({"query": query, "retrieval_strategy": res.strategy, "routes": res.routes, "index_snapshot": {"index_version": res.index_version, "manifest_hash": res.index_manifest_hash},
        "ranked_evidence": res.hits.iter().map(|h| json!({"artifact_id": h.artifact_id, "path": h.path, "section": h.section, "score": h.score, "routes": h.routes, "status": h.status, "state_class": h.state_class, "excerpt": h.excerpt, "parent_excerpt": h.parent_excerpt, "neighbours": h.neighbours, "flags": h.flags})).collect::<Vec<_>>(),
        "lessons_failures": lessons.hits.iter().map(|h| json!({"artifact_id": h.artifact_id, "path": h.path, "excerpt": h.excerpt})).collect::<Vec<_>>(), "code_references": code_refs});
    let mut packet = json!({"packet_id": format!("CTX-{}-{}", task_id, &det_hash[..8]), "task": task_id, "deterministic_authority": det, "deterministic_hash": det_hash, "retrieved_intelligence": ret, "index_version": crate::INDEX_VERSION});
    let ph = hash_value(&json!({"d": packet["deterministic_authority"], "r": packet["retrieved_intelligence"]}));
    packet["packet_hash"] = Value::String(ph);
    packet["compiled_at"] = Value::String(now_iso());
    let chars = serde_json::to_string(&packet)?.len();
    packet["chars"] = json!(chars);
    let max = pol.get_i64("CONTEXT_POLICY", "max_packet_chars", 60000) as usize;
    if chars > max { packet["warning"] = json!(format!("packet exceeds CONTEXT_POLICY.max_packet_chars ({chars} > {max})")); }
    write_json(&p.runtime_dir().join("context").join(format!("{task_id}.json")), &packet)?;
    Ok(packet)
}
