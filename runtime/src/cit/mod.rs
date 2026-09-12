//! Change-Impact Transactions (framework §47-49): CIT-P simulation before approval, CIT-E atomic execution with
//! snapshot, propagation, derived-view regeneration, index refresh, verification and commit-or-rollback.
use crate::graph;
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::orchestration::{control, gates};
use crate::records::{new_record, parse_record_text, save_record, RecordStore};
use crate::retrieval::{retrieve, RetrieveOptions};
use crate::util::{copy_dir, glob_match, now_iso, read_json, read_text, today, write_json, write_text};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

const RADII: &[&str] = &["R0", "R1", "R2", "R3", "R4", "R5"];
fn radius_rank(r: &str) -> usize { RADII.iter().position(|x| *x == r).unwrap_or(1) }

/// Redact secret patterns inside every string of a JSON value; returns the number of redactions.
fn redact_value(p: &Project, v: &mut Value, field: &str, hits: &mut Vec<String>) {
    match v {
        Value::String(s) => { let found = p.secret_scanner().scan_text(s, field); if !found.is_empty() { for h in &found { hits.push(format!("{}: {}", field, h.pattern_id)); } let mut out = s.clone(); for (_, rx) in &p.secret_scanner().patterns { out = rx.replace_all(&out, "[REDACTED]").to_string(); } *s = out; } }
        Value::Array(a) => { for (i, x) in a.iter_mut().enumerate() { redact_value(p, x, &format!("{field}[{i}]"), hits); } }
        Value::Object(o) => { for (k, x) in o.iter_mut() { redact_value(p, x, &format!("{field}.{k}"), hits); } }
        _ => {}
    }
}

pub fn propose(p: &Project, mut fields: Value) -> Result<Value> {
    control::guard_write(p, "cit propose")?;
    crate::authority::require(p, "propose_cit")?;
    let store = RecordStore::load(&p.root);
    let id = store.next_id("cit");
    let o = fields.as_object_mut().ok_or_else(|| GovError::new("USAGE", "cit fields must be an object"))?;
    if o.get("proposal").and_then(|v| v.as_str()).map(|s| s.is_empty()).unwrap_or(true) { return Err(GovError::new("USAGE", "proposal text required")); }
    // SECURITY: a proposal/manifest is a governed record; secret material is redacted before it is persisted and the
    // transaction is flagged so that it can never be executed with that content (verifier M9 / HV-34, HV-17).
    let mut secret_hits: Vec<String> = vec![];
    { let mut tmp = Value::Object(o.clone()); redact_value(p, &mut tmp, "cit", &mut secret_hits); if let Value::Object(m) = tmp { *o = m; } }
    if !secret_hits.is_empty() { o.insert("secret_flagged".into(), json!(true)); o.insert("blocked_reasons".into(), json!(secret_hits.iter().map(|h| format!("secret pattern redacted from {h}")).collect::<Vec<_>>())); }
    o.insert("cit_status".into(), json!("PROPOSED"));
    o.entry("proposed_by").or_insert(json!(p.role));
    o.entry("trigger").or_insert(json!("behaviour_change"));
    o.entry("targets").or_insert(json!([]));
    o.entry("mutation_manifest").or_insert(json!([]));
    o.insert("journal".into(), json!([{"at": now_iso(), "event": "proposed", "session": p.session_id}]));
    o.insert("state_class".into(), json!("AUTHORITATIVE"));
    let title = o.get("title").and_then(|v| v.as_str()).map(|s| s.to_string()).unwrap_or_else(|| o["proposal"].as_str().unwrap_or("").chars().take(80).collect());
    o.remove("title");
    let rec = new_record("cit", &id, &title, Value::Object(o.clone()));
    p.schemas().validate("cit", &rec.data, &format!("({id})"))?;
    save_record(&p.root, &rec)?;
    // CHANGE_POLICY.auto_simulate_triggers: CIT-P is automatic above the impact threshold (framework §48)
    let trigger = rec.get("trigger");
    if p.policies().get_list("CHANGE_POLICY", "auto_simulate_triggers").contains(&trigger) && p.db_path().exists() {
        let db = RuntimeDb::open(&p.db_path())?;
        if db.has_schema() { let sim = simulate_inner(p, &db, &id)?; let mut data = RecordStore::load(&p.root).get(&id).map(|r| r.data.clone()).unwrap_or(rec.data.clone()); data["auto_simulated"] = json!(true); data["simulation"] = sim; return Ok(data); }
    }
    Ok(rec.data)
}

fn manifest_paths(cit: &Value) -> Vec<String> {
    let mut v = vec![];
    for op in cit["mutation_manifest"].as_array().cloned().unwrap_or_default() {
        for k in ["path", "to"] { if let Some(s) = op[k].as_str() { v.push(s.to_string()); } }
        if let Some(t) = op["target"].as_str() { v.push(t.to_string()); }
        if let Some(r) = op["record"].as_object() { if let Some(id) = r.get("id").and_then(|x| x.as_str()) { v.push(id.to_string()); } }
    }
    v
}

fn seeds_for(p: &Project, db: &RuntimeDb, cit: &Value) -> Result<Vec<String>> {
    let mut seeds: Vec<String> = cit["targets"].as_array().map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
    for pth in manifest_paths(cit) {
        if let Some(a) = db.artifact_by_path(&pth)? { seeds.push(a["artifact_id"].as_str().unwrap_or("").to_string()); }
        else if db.artifact(&pth)?.is_some() { seeds.push(pth); }
        else if p.root.join(&pth).exists() { seeds.push(format!("file:{pth}")); }
    }
    seeds.sort(); seeds.dedup();
    Ok(seeds)
}

fn estimate_radius(p: &Project, cit: &Value, affected: &[graph::Reach], db: &RuntimeDb) -> Result<String> {
    let pol = p.policies();
    let trigger = cit["trigger"].as_str().unwrap_or("");
    let paths = manifest_paths(cit);
    let mut r = if paths.iter().any(|x| glob_match("governance/**", x)) || trigger == "governance_change" { pol.get_str("CHANGE_POLICY", "radius_rules.governance_paths_radius", "R5") } else if matches!(trigger, "interface_change" | "behaviour_change" | "security_change" | "architecture_change") { pol.get_str("CHANGE_POLICY", "radius_rules.interface_or_behaviour_radius", "R2") } else if trigger == "editorial" { pol.get_str("CHANGE_POLICY", "radius_rules.editorial_radius", "R0") } else { pol.get_str("CHANGE_POLICY", "radius_rules.single_artifact_radius", "R1") };
    let mut features = std::collections::BTreeSet::new();
    let mut modules = std::collections::BTreeSet::new();
    for a in affected {
        if let Some(art) = db.artifact(&a.node)? {
            let rt = art["record_type"].as_str().unwrap_or("");
            if rt == "feature" { features.insert(a.node.clone()); }
            if rt == "file" { let path = art["path"].as_str().unwrap_or(""); if let Some(m) = Path::new(path).parent() { modules.insert(m.to_string_lossy().to_string()); } }
            if let Ok(d) = serde_json::from_str::<Value>(art["data_json"].as_str().unwrap_or("{}")) { if let Some(f) = d.get("feature").and_then(|v| v.as_str()) { features.insert(f.to_string()); } }
        }
    }
    let cf = pol.get_i64("CHANGE_POLICY", "radius_rules.cross_feature_threshold", 3) as usize;
    let cm = pol.get_i64("CHANGE_POLICY", "radius_rules.cross_module_threshold", 2) as usize;
    if features.len() >= cf && radius_rank(&r) < 4 { r = "R4".into(); }
    else if modules.len() >= cm && radius_rank(&r) < 3 { r = "R3".into(); }
    if trigger == "architecture_change" && radius_rank(&r) < 3 { r = "R3".into(); }
    Ok(r)
}

/// CIT-P: deterministic graph traversal + bounded retrieval -> impact radius and human-readable consequences.
pub fn simulate(p: &Project, db: &RuntimeDb, id: &str) -> Result<Value> {
    control::guard_write(p, "cit simulate")?;
    crate::authority::require(p, "simulate_cit")?;
    simulate_inner(p, db, id)
}

fn simulate_inner(p: &Project, db: &RuntimeDb, id: &str) -> Result<Value> {
    let pol = p.policies();
    let mut store = RecordStore::load(&p.root);
    let rec = store.get(id).ok_or_else(|| GovError::new("CIT_NOT_FOUND", format!("{id} not found")))?.clone();
    if !matches!(rec.get("cit_status").as_str(), "PROPOSED" | "SIMULATED") { return Err(GovError::new("USAGE", format!("{id} is {}; only PROPOSED/SIMULATED transactions can be simulated", rec.get("cit_status")))); }
    let seeds = seeds_for(p, db, &rec.data)?;
    let mut radius = estimate_radius(p, &rec.data, &[], db)?;
    let mut affected = vec![];
    for _ in 0..2 {
        let depth = pol.get_i64("CHANGE_POLICY", &format!("graph_traversal_depth_by_radius.{radius}"), 2) as usize;
        affected = graph::impact_set(db, &seeds, depth.max(1))?;
        let r2 = estimate_radius(p, &rec.data, &affected, db)?;
        if radius_rank(&r2) <= radius_rank(&radius) { break; }
        radius = r2;
    }
    let k = pol.get_i64("CHANGE_POLICY", &format!("semantic_candidates_by_radius.{radius}"), 8) as usize;
    let candidates = if k > 0 { retrieve(p, db, rec.get("proposal").as_str(), RetrieveOptions { k, ..Default::default() })?.hits.into_iter().map(|h| json!({"artifact_id": h.artifact_id, "path": h.path, "score": h.score, "routes": h.routes})).collect::<Vec<_>>() } else { vec![] };
    let mut tasks = vec![]; let mut tests = vec![]; let mut features = vec![]; let mut other = vec![];
    for a in &affected {
        let rt = db.artifact(&a.node)?.map(|x| x["record_type"].as_str().unwrap_or("").to_string()).unwrap_or_default();
        match rt.as_str() { "task" => tasks.push(a.node.clone()), "test-obligation" | "scenario" => tests.push(a.node.clone()), "feature" => features.push(a.node.clone()),
            "file" => { if db.artifact(&a.node)?.map(|x| x["path_class"].as_str() == Some("test")).unwrap_or(false) { tests.push(a.node.clone()); } else { other.push(a.node.clone()); } }
            _ => other.push(a.node.clone()) }
    }
    let human_triggers = pol.get_list("CHANGE_POLICY", "human_gate_triggers");
    let auto_max = pol.get_str("CHANGE_POLICY", "auto_approve_max_radius", "R1");
    let trigger = rec.get("trigger");
    let human_gate_required = radius_rank(&radius) > radius_rank(&auto_max) || human_triggers.contains(&trigger);
    let consequences = vec![
        format!("{} artefacts affected within radius {radius} (graph depth {})", affected.len(), pol.get_i64("CHANGE_POLICY", &format!("graph_traversal_depth_by_radius.{radius}"), 2)),
        format!("{} open task(s) will be marked retest-required", tasks.len()),
        format!("{} test/scenario artefact(s) become stale and must be re-validated", tests.len()),
        format!("{} feature(s) readiness potentially impacted", features.len()),
        if human_gate_required { "human approval required before execution".into() } else { "eligible for automatic approval under CHANGE_POLICY".into() },
        "rollback: snapshot of every touched file is taken before execution; `gov cit rollback` restores it".into(),
    ];
    let routing = crate::routing::route(p, None, Some("governance"), None, Some(&radius))?;
    let impact = json!({"radius": radius, "seeds": seeds, "affected": affected.iter().map(|a| json!({"node": a.node, "hop": a.hop, "via": a.via})).collect::<Vec<_>>(), "affected_tasks": tasks, "tests_required": tests, "features": features, "other": other,
        "semantic_candidates": candidates, "consequences": consequences, "human_gate_required": human_gate_required, "minimum_model_tier": routing["minimum_tier"], "simulated_at": now_iso(), "index_snapshot": db.get_meta("index_manifest_hash")});
    let r = store.get_mut(id).unwrap();
    r.set("impact", impact.clone());
    r.set("cit_status", json!("SIMULATED"));
    r.set("updated", json!(today()));
    if let Some(j) = r.data["journal"].as_array_mut() { j.push(json!({"at": now_iso(), "event": "simulated", "radius": impact["radius"]})); }
    let mut gate_id = r.get("human_gate");
    let proposal = r.get("proposal");
    let rec_data = r.data.clone();
    save_record(&p.root, r)?;
    if human_gate_required && gate_id.is_empty() {
        let g = gates::create(p, json!({"question": format!("Approve change {id}: {}", proposal), "why_now": format!("impact radius {} / trigger {}", impact["radius"], trigger), "current_state": "proposal simulated, not executed",
            "options": [{"id": "A", "description": "approve and execute (CIT-E)"}, {"id": "B", "description": "reject"}], "impact": impact["consequences"].as_array().map(|a| a.iter().map(|c| c.as_str().unwrap_or("").to_string()).collect::<Vec<_>>().join("; ")).unwrap_or_default(),
            "reversibility": "snapshot rollback available", "cost_rework": format!("{} tasks retest", impact["affected_tasks"].as_array().map(|a| a.len()).unwrap_or(0)), "recommendation": "A if the proposal matches product direction", "confidence": 0.7,
            "trigger": trigger, "cit": id, "impact_radius": impact["radius"], "blocks_tasks": []}))?;
        gate_id = g["id"].as_str().unwrap_or("").to_string();
        let mut store2 = RecordStore::load(&p.root);
        let r2 = store2.get_mut(id).unwrap(); r2.set("human_gate", json!(gate_id)); save_record(&p.root, r2)?;
    }
    let _ = rec_data;
    Ok(json!({"cit": id, "impact": impact, "human_gate": if gate_id.is_empty() { Value::Null } else { json!(gate_id) }}))
}

pub fn approve(p: &Project, id: &str, by: &str, method: &str) -> Result<Value> {
    control::guard_write(p, "cit approve")?;
    crate::authority::require(p, if method == "human" { "approve_cit_human" } else { "approve_cit_auto" })?;
    let pol = p.policies();
    let mut store = RecordStore::load(&p.root);
    let r = store.get_mut(id).ok_or_else(|| GovError::new("CIT_NOT_FOUND", format!("{id} not found")))?;
    if r.get("cit_status") != "SIMULATED" { return Err(GovError::new("USAGE", format!("{id} must be SIMULATED before approval (is {})", r.get("cit_status")))); }
    let hg_required = r.data["impact"]["human_gate_required"].as_bool().unwrap_or(true);
    if hg_required && method != "human" { return Err(GovError::new("HUMAN_GATE_REQUIRED", format!("{id} requires human approval (radius {} or trigger); present gate {} in chat and use --method human", r.data["impact"]["radius"], r.get("human_gate")))); }
    if !hg_required { let auto_max = pol.get_str("CHANGE_POLICY", "auto_approve_max_radius", "R1"); if radius_rank(r.data["impact"]["radius"].as_str().unwrap_or("R5")) > radius_rank(&auto_max) && method != "human" { return Err(GovError::new("HUMAN_GATE_REQUIRED", "radius exceeds auto-approve maximum")); } }
    let gate = r.get("human_gate");
    if !gate.is_empty() && method == "human" {
        if let Some(g) = store.get(&gate) { if !matches!(g.get("gate_status").as_str(), "ANSWERED") && !g.data.get("presented_in_chat").and_then(|v| v.as_bool()).unwrap_or(false) { return Err(GovError::new("GATE_NOT_PRESENTED", format!("human gate {gate} was never presented in chat (INV-008); run `gov gate present {gate}`"))); } }
    }
    let r = store.get_mut(id).unwrap();
    r.set("cit_status", json!("APPROVED"));
    r.set("approval", json!({"by": by, "at": now_iso(), "method": method}));
    if let Some(j) = r.data["journal"].as_array_mut() { j.push(json!({"at": now_iso(), "event": "approved", "by": by, "method": method})); }
    let proposal = r.get("proposal"); let radius = r.data["impact"]["radius"].clone(); let trigger = r.get("trigger");
    let decision_existing = r.get("decision");
    save_record(&p.root, r)?;
    let mut decision = decision_existing;
    if decision.is_empty() {
        let did = store.next_id("decision");
        let d = new_record("decision", &did, &format!("Approve {id}"), json!({"question": format!("Execute change {id}?"), "options": [{"id": "A", "description": proposal}], "chosen_option": "A", "rationale": format!("approved via CIT {id} ({method})"), "approved_by": by, "approved_at": now_iso(), "human_approved": method == "human", "impact_radius": radius, "reversibility": "snapshot rollback", "confidence": 0.9, "cit": id, "state_class": "AUTHORITATIVE", "tags": [trigger]}));
        save_record(&p.root, &d)?;
        let mut s2 = RecordStore::load(&p.root); let r2 = s2.get_mut(id).unwrap(); r2.set("decision", json!(did)); save_record(&p.root, r2)?;
        decision = did;
    }
    Ok(json!({"cit": id, "cit_status": "APPROVED", "decision": decision}))
}

pub fn reject(p: &Project, id: &str, by: &str, reason: Option<&str>) -> Result<Value> {
    control::guard_write(p, "cit reject")?;
    crate::authority::require(p, "reject_cit")?;
    let mut store = RecordStore::load(&p.root);
    let r = store.get_mut(id).ok_or_else(|| GovError::new("CIT_NOT_FOUND", format!("{id} not found")))?;
    if matches!(r.get("cit_status").as_str(), "COMMITTED" | "EXECUTING") { return Err(GovError::new("USAGE", format!("{id} is {}; cannot reject", r.get("cit_status")))); }
    r.set("cit_status", json!("REJECTED"));
    if let Some(j) = r.data["journal"].as_array_mut() { j.push(json!({"at": now_iso(), "event": "rejected", "by": by, "reason": reason})); }
    save_record(&p.root, r)?;
    Ok(json!({"cit": id, "cit_status": "REJECTED"}))
}

fn snapshot_dir(p: &Project, id: &str) -> PathBuf { p.runtime_dir().join("cit").join(id) }

fn take_snapshot(p: &Project, id: &str, cit: &Value, store: &RecordStore) -> Result<Value> {
    let dir = snapshot_dir(p, id);
    let snap = dir.join("snapshot");
    crate::util::remove_dir_if_exists(&dir)?;
    std::fs::create_dir_all(&snap)?;
    let mut files = vec![]; let mut created_paths = vec![];
    let mut want: Vec<String> = manifest_paths(cit).into_iter().filter_map(|x| if p.root.join(&x).exists() { Some(x) } else { store.get(&x).map(|r| r.path.clone()) }).collect();
    for a in cit["impact"]["affected"].as_array().cloned().unwrap_or_default() { if let Some(r) = a["node"].as_str().and_then(|n| store.get(n)) { want.push(r.path.clone()); } }
    for op in cit["mutation_manifest"].as_array().cloned().unwrap_or_default() {
        if op["op"] == "write_file" || op["op"] == "append_record" { let path = op["path"].as_str().map(|s| s.to_string()).or_else(|| op["record"].as_object().and_then(|r| r.get("id")).and_then(|i| i.as_str()).and_then(|i| op["record"]["type"].as_str().and_then(|t| crate::records::record_path_for(t, i).ok()))); if let Some(pth) = path { if !p.root.join(&pth).exists() { created_paths.push(pth); } } }
        if op["op"] == "move_file" { if let Some(to) = op["to"].as_str() { created_paths.push(to.to_string()); } }
    }
    want.sort(); want.dedup();
    for rel in want {
        let src = p.root.join(&rel);
        if src.is_file() { let dst = snap.join(&rel); if let Some(d) = dst.parent() { std::fs::create_dir_all(d)?; } std::fs::copy(&src, &dst)?; files.push(rel); }
        else if src.is_dir() { copy_dir(&src, &snap.join(&rel))?; files.push(rel); }
    }
    let manifest = json!({"cit": id, "taken_at": now_iso(), "files": files, "created_paths": created_paths, "commit": p.git_commit()});
    write_json(&dir.join("snapshot.json"), &manifest)?;
    Ok(manifest)
}

fn apply_op(p: &Project, op: &Value, touched: &mut Vec<String>) -> Result<()> {
    let kind = op["op"].as_str().unwrap_or("");
    match kind {
        "set_status" | "set_field" | "mark_stale" => {
            let target = op["target"].as_str().ok_or_else(|| GovError::new("USAGE", format!("{kind} requires target")))?;
            let mut store = RecordStore::load(&p.root);
            let r = store.get_mut(target).ok_or_else(|| GovError::new("RECORD_NOT_FOUND", format!("{target} not found")))?;
            match kind {
                "set_status" => { r.set("status", op["value"].clone()); if op["value"] == "SUPERSEDED" { if let Some(by) = op["by"].as_str() { r.set("superseded_by", json!(by)); } } }
                "set_field" => { let f = op["field"].as_str().ok_or_else(|| GovError::new("USAGE", "set_field requires field"))?; if f.contains('.') { crate::util::deep_set(&mut r.data, f, op["value"].clone()); } else { r.set(f, op["value"].clone()); } }
                _ => { r.set("staleness", json!({"stale": true, "reason": op["reason"].as_str().unwrap_or("CIT propagation"), "at": now_iso()})); }
            }
            r.set("updated", json!(today()));
            touched.push(r.path.clone());
            save_record(&p.root, r)?;
        }
        "write_file" => { let path = op["path"].as_str().ok_or_else(|| GovError::new("USAGE", "write_file requires path"))?; if glob_match("governance/kernel/**", path) { return Err(GovError::new("INV_007", "CIT may not write into governance/kernel/")); } write_text(&p.root.join(path), op["content"].as_str().unwrap_or(""))?; touched.push(path.to_string()); }
        "move_file" => {
            let (from, to) = (op["path"].as_str().unwrap_or(""), op["to"].as_str().unwrap_or(""));
            if from.is_empty() || to.is_empty() { return Err(GovError::new("USAGE", "move_file requires path and to")); }
            if let Some(d) = p.root.join(to).parent() { std::fs::create_dir_all(d)?; }
            let (code, _, _) = p.git(&["mv", "-k", from, to]);
            if code != 0 || !p.root.join(to).exists() { std::fs::rename(p.root.join(from), p.root.join(to))?; }
            touched.push(from.to_string()); touched.push(to.to_string());
        }
        "delete_file" => { let path = op["path"].as_str().unwrap_or(""); let full = p.root.join(path); if full.is_file() { std::fs::remove_file(&full)?; } else if full.is_dir() { std::fs::remove_dir_all(&full)?; } touched.push(path.to_string()); }
        "append_record" => {
            let rec = op["record"].clone();
            let (id, t) = (rec["id"].as_str().unwrap_or("").to_string(), rec["type"].as_str().unwrap_or("").to_string());
            if id.is_empty() || t.is_empty() { return Err(GovError::new("USAGE", "append_record requires record.id and record.type")); }
            let path = op["path"].as_str().map(|s| s.to_string()).unwrap_or(crate::records::record_path_for(&t, &id)?);
            let mut r = parse_record_text(&crate::util::to_yaml(&rec)?, &path).ok_or_else(|| GovError::new("USAGE", "invalid record"))?;
            r.path = path.clone();
            if p.schemas().has(&t) { p.schemas().validate(&t, &r.data, &format!("({id})"))?; } else { p.schemas().validate("record", &r.data, &format!("({id})"))?; }
            save_record(&p.root, &r)?; touched.push(path);
        }
        "regenerate_views" => { crate::tools::generate_registry(p)?; crate::adapters::generate(p)?; }
        "set_lock_field" => { return Err(GovError::new("USAGE", "set_lock_field is reserved for framework migrations (gov update)")); }
        other => return Err(GovError::new("USAGE", format!("unknown mutation op {other}"))),
    }
    Ok(())
}

/// CIT-E: snapshot -> apply -> propagate -> regenerate -> refresh index -> verify -> commit or rollback.
pub fn execute(p: &Project, db: &RuntimeDb, id: &str) -> Result<Value> {
    control::guard_write(p, "cit execute")?;
    crate::authority::require(p, "execute_cit")?;
    let pol = p.policies();
    let store = RecordStore::load(&p.root);
    let rec = store.get(id).ok_or_else(|| GovError::new("CIT_NOT_FOUND", format!("{id} not found")))?.clone();
    if rec.get("cit_status") != "APPROVED" { return Err(GovError::new("USAGE", format!("{id} must be APPROVED to execute (is {})", rec.get("cit_status")))); }
    if rec.data.get("secret_flagged").and_then(|v| v.as_bool()).unwrap_or(false) { return Err(GovError::new("SECRET_IN_MANIFEST", format!("{id} was flagged at proposal time because its proposal/manifest contained secret material (redacted); it cannot be executed. Re-propose without secrets (store them in a secret-class path).")).with_details(rec.data.get("blocked_reasons").cloned().unwrap_or(Value::Null))); }
    if !pol.get_bool("CHANGE_POLICY", "rollback.snapshot_before_execute", true) { return Err(GovError::new("POLICY_UNSAFE", "CHANGE_POLICY.rollback.snapshot_before_execute is false; execution without a snapshot is refused by this release")); }
    if let Some(gate) = Some(rec.get("human_gate")).filter(|g| !g.is_empty()) { if let Some(g) = store.get(&gate) { if g.get("gate_status") != "ANSWERED" { return Err(GovError::new("HUMAN_GATE_REQUIRED", format!("gate {gate} not answered"))); } } }
    let snapshot = take_snapshot(p, id, &rec.data, &store)?;
    let dangling_before: std::collections::BTreeSet<String> = graph::dangling_edges(db)?.iter().map(|e| e.to_string()).collect();
    let mut s = RecordStore::load(&p.root);
    { let r = s.get_mut(id).unwrap(); r.set("cit_status", json!("EXECUTING")); r.set("execution", json!({"started": now_iso(), "snapshot": snapshot, "session": p.session_id})); if let Some(j) = r.data["journal"].as_array_mut() { j.push(json!({"at": now_iso(), "event": "executing"})); } save_record(&p.root, r)?; }
    let mut touched = vec![];
    let result: Result<Value> = (|| {
        for op in rec.data["mutation_manifest"].as_array().cloned().unwrap_or_default() { apply_op(p, &op, &mut touched)?; }
        // propagation
        let mut retest = vec![]; let mut stale = vec![];
        if pol.get_bool("CHANGE_POLICY", "propagation.mark_affected_tasks_retest", true) {
            let mut st = RecordStore::load(&p.root);
            for t in rec.data["impact"]["affected_tasks"].as_array().cloned().unwrap_or_default() { if let Some(tr) = t.as_str().and_then(|x| st.get_mut(x)) { if !matches!(tr.get("task_status").as_str(), "DONE" | "CANCELLED") { tr.set("retest_required", json!(true)); tr.set("retest_reason", json!(format!("CIT {id}"))); save_record(&p.root, tr)?; retest.push(tr.id()); } } }
        }
        if pol.get_bool("CHANGE_POLICY", "propagation.mark_affected_tests_stale", true) {
            let mut st = RecordStore::load(&p.root);
            for t in rec.data["impact"]["tests_required"].as_array().cloned().unwrap_or_default() { if let Some(tr) = t.as_str().and_then(|x| st.get_mut(x)) { tr.set("staleness", json!({"stale": true, "reason": format!("CIT {id}"), "at": now_iso()})); save_record(&p.root, tr)?; stale.push(tr.id()); } }
        }
        if pol.get_bool("CHANGE_POLICY", "propagation.regenerate_derived_views", true) { crate::tools::generate_registry(p)?; crate::adapters::generate(p)?; }
        if pol.get_bool("CHANGE_POLICY", "propagation.refresh_index", true) { crate::memory::indexer::rebuild(p, crate::memory::indexer::IndexOptions { incremental: true, ..Default::default() })?; }
        // verification
        let mut problems = vec![];
        let required = pol.get_list("CHANGE_POLICY", "verification_required");
        if required.iter().any(|r| r == "schema_validation") {
            let st = RecordStore::load(&p.root);
            for pth in &touched { if let Some(r) = st.records.iter().find(|r| r.path == *pth) { let t = r.rtype(); let schema = if p.schemas().has(&t) { t } else { "record".into() }; if let Ok(errs) = p.schemas().errors(&schema, &r.data) { for e in errs { problems.push(format!("{pth}: {e}")); } } } }
        }
        if required.iter().any(|r| r == "graph_integrity") { let db2 = RuntimeDb::open(&p.db_path())?; let d = graph::dangling_edges(&db2)?; let new_dangling: Vec<&Value> = d.iter().filter(|e| !dangling_before.contains(&e.to_string())).collect(); if !new_dangling.is_empty() { problems.push(format!("{} new dangling edge(s) introduced: {}", new_dangling.len(), new_dangling.iter().map(|e| format!("{} {} {}", e["src"], e["type"], e["dst"])).collect::<Vec<_>>().join(", "))); } }
        if required.iter().any(|r| r == "index_freshness") { let f = freshness(p); if !f.fresh { problems.push(format!("index not fresh after refresh: {} stale/{} added/{} removed", f.stale.len(), f.added.len(), f.removed.len())); } }
        if !problems.is_empty() { return Err(GovError::new("VERIFICATION_FAILED", format!("CIT-E verification failed: {}", problems.join("; "))).with_details(json!({"problems": problems}))); }
        Ok(json!({"retest_required": retest, "stale_tests": stale, "touched": touched.clone()}))
    })();
    match result {
        Ok(v) => {
            let mut s2 = RecordStore::load(&p.root);
            let r = s2.get_mut(id).unwrap();
            let mut ex = r.data["execution"].clone(); ex["finished"] = json!(now_iso()); ex["result"] = json!("committed"); ex["verification"] = json!({"ok": true}); ex["propagation"] = v.clone();
            r.set("execution", ex); r.set("cit_status", json!("COMMITTED")); if let Some(j) = r.data["journal"].as_array_mut() { j.push(json!({"at": now_iso(), "event": "committed"})); }
            save_record(&p.root, r)?;
            let _ = crate::memory::indexer::rebuild(p, crate::memory::indexer::IndexOptions { incremental: true, ..Default::default() });
            let db2 = RuntimeDb::open(&p.db_path())?;
            let ck = crate::checkpoints::create(p, &db2, json!({"trigger": "accepted_cit", "next_action": "gov continue", "last_completed_step": format!("executed {id}"), "open_transactions": []}))?;
            prune_snapshots(p, pol.get_i64("CHANGE_POLICY", "rollback.keep_snapshots", 20).max(1) as usize);
            Ok(json!({"cit": id, "cit_status": "COMMITTED", "propagation": v, "checkpoint": ck["id"]}))
        }
        Err(e) => {
            let rb = restore_snapshot(p, id)?;
            let mut s2 = RecordStore::load(&p.root);
            if let Some(r) = s2.get_mut(id) { let mut ex = r.data["execution"].clone(); ex["finished"] = json!(now_iso()); ex["result"] = json!("rolled_back"); ex["error"] = json!(e.to_string()); ex["verification"] = json!({"ok": false, "details": e.details}); r.set("execution", ex); r.set("cit_status", json!("ROLLED_BACK")); if let Some(j) = r.data["journal"].as_array_mut() { j.push(json!({"at": now_iso(), "event": "rolled_back", "error": e.to_string()})); } save_record(&p.root, r)?; }
            let _ = crate::memory::indexer::rebuild(p, crate::memory::indexer::IndexOptions { incremental: true, ..Default::default() });
            Err(GovError::new(&e.code, format!("{} — rolled back ({} files restored)", e.message, rb["restored"].as_array().map(|a| a.len()).unwrap_or(0))).with_details(json!({"rollback": rb, "details": e.details})))
        }
    }
}

/// CHANGE_POLICY.rollback.keep_snapshots: keep only the newest N CIT snapshot directories (older transactions cannot be
/// rolled back automatically afterwards; git history remains).
pub fn prune_snapshots(p: &Project, keep: usize) {
    let base = p.runtime_dir().join("cit");
    let Ok(rd) = std::fs::read_dir(&base) else { return };
    let mut dirs: Vec<(std::time::SystemTime, PathBuf)> = rd.filter_map(|e| e.ok()).map(|e| e.path()).filter(|d| d.join("snapshot.json").exists()).map(|d| (std::fs::metadata(d.join("snapshot.json")).and_then(|m| m.modified()).unwrap_or(std::time::UNIX_EPOCH), d)).collect();
    dirs.sort_by(|a, b| b.0.cmp(&a.0));
    for (_, d) in dirs.into_iter().skip(keep) { let _ = std::fs::remove_dir_all(d); }
}

/// Restore the snapshot taken before execution; remove files created by the transaction.
pub fn restore_snapshot(p: &Project, id: &str) -> Result<Value> {
    let dir = snapshot_dir(p, id);
    let manifest = read_json(&dir.join("snapshot.json")).map_err(|_| GovError::new("SNAPSHOT_MISSING", format!("no snapshot for {id} under {}", dir.display())))?;
    let mut restored = vec![]; let mut removed = vec![];
    for created in manifest["created_paths"].as_array().cloned().unwrap_or_default() {
        let rel = created.as_str().unwrap_or(""); let full = p.root.join(rel);
        if manifest["files"].as_array().map(|a| a.iter().any(|f| f.as_str() == Some(rel))).unwrap_or(false) { continue; }
        if full.is_file() { std::fs::remove_file(&full)?; removed.push(rel.to_string()); }
    }
    for f in manifest["files"].as_array().cloned().unwrap_or_default() {
        let rel = f.as_str().unwrap_or(""); let src = dir.join("snapshot").join(rel); let dst = p.root.join(rel);
        if src.is_file() { if let Some(d) = dst.parent() { std::fs::create_dir_all(d)?; } std::fs::copy(&src, &dst)?; restored.push(rel.to_string()); }
        else if src.is_dir() { crate::util::remove_dir_if_exists(&dst)?; copy_dir(&src, &dst)?; restored.push(rel.to_string()); }
    }
    // moved files: if a move op moved A->B and A restored, remove B
    for op in RecordStore::load(&p.root).get(id).map(|r| r.data["mutation_manifest"].clone()).unwrap_or(json!([])).as_array().cloned().unwrap_or_default() {
        if op["op"] == "move_file" { if let (Some(from), Some(to)) = (op["path"].as_str(), op["to"].as_str()) { if p.root.join(from).exists() && p.root.join(to).exists() && from != to { let _ = std::fs::remove_file(p.root.join(to)); removed.push(to.to_string()); } } }
    }
    Ok(json!({"cit": id, "restored": restored, "removed": removed}))
}

/// Explicit rollback of a COMMITTED or EXECUTING (interrupted) transaction.
pub fn rollback(p: &Project, id: &str, reason: Option<&str>) -> Result<Value> {
    crate::authority::require(p, "rollback_cit")?; // rollback is an emergency control: allowed while frozen
    let store = RecordStore::load(&p.root);
    let rec = store.get(id).ok_or_else(|| GovError::new("CIT_NOT_FOUND", format!("{id} not found")))?;
    if !matches!(rec.get("cit_status").as_str(), "COMMITTED" | "EXECUTING" | "ROLLED_BACK") { return Err(GovError::new("USAGE", format!("{id} is {}; nothing to roll back", rec.get("cit_status")))); }
    let rb = restore_snapshot(p, id)?;
    let mut s2 = RecordStore::load(&p.root);
    let mut decision_id = String::new();
    if let Some(r) = s2.get_mut(id) { decision_id = r.get("decision"); r.set("cit_status", json!("ROLLED_BACK")); if let Some(j) = r.data["journal"].as_array_mut() { j.push(json!({"at": now_iso(), "event": "rolled_back", "reason": reason, "by": p.session_id})); } save_record(&p.root, r)?; }
    // the approval decision no longer describes the project (verifier L7): mark it REJECTED with provenance
    if !decision_id.is_empty() { let mut s3 = RecordStore::load(&p.root); if let Some(d) = s3.get_mut(&decision_id) { d.set("status", json!("REJECTED")); d.set("state_class", json!("HISTORICAL")); d.set("rollback_of", json!(id)); d.set("updated", json!(crate::util::today())); save_record(&p.root, d)?; } }
    let _ = crate::tools::generate_registry(p); let _ = crate::adapters::generate(p);
    let _ = crate::memory::indexer::rebuild(p, crate::memory::indexer::IndexOptions { incremental: true, ..Default::default() });
    Ok(json!({"cit": id, "cit_status": "ROLLED_BACK", "rollback": rb}))
}

pub fn interrupted(p: &Project) -> Vec<Value> {
    RecordStore::load(&p.root).of_type("cit").into_iter().filter(|c| c.get("cit_status") == "EXECUTING").map(|c| json!({"id": c.id(), "started": c.data["execution"]["started"], "session": c.data["execution"]["session"], "snapshot_present": snapshot_dir(p, &c.id()).join("snapshot.json").exists()})).collect()
}

pub fn list(p: &Project) -> Vec<Value> {
    RecordStore::load(&p.root).of_type("cit").into_iter().map(|c| json!({"id": c.id(), "title": c.title(), "cit_status": c.get("cit_status"), "trigger": c.get("trigger"), "radius": c.data["impact"]["radius"], "human_gate": c.get("human_gate"), "decision": c.get("decision")})).collect()
}

pub fn read_text_opt(p: &Path) -> Option<String> { read_text(p).ok() }
