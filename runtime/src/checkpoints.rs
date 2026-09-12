//! Checkpoints (framework §59-60): structured resumable state, never a prose summary. Provider-independent watchdog.
use crate::memory::db::RuntimeDb;
use crate::orchestration::{claims, control};
use crate::records::{new_record, save_record, RecordStore};
use crate::util::{now_iso, read_yaml, write_yaml};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub fn dir(p: &Project) -> std::path::PathBuf { p.root.join(p.policies().get_str("CHECKPOINT_POLICY", "location", "spec/reports/checkpoints")) }

pub fn create(p: &Project, db: &RuntimeDb, mut fields: Value) -> Result<Value> {
    control::guard_write(p, "checkpoint")?;
    crate::authority::require(p, "checkpoint")?;
    let pol = p.policies();
    let triggers = pol.get_list("CHECKPOINT_POLICY", "mandatory_triggers");
    let trigger = fields.get("trigger").and_then(|v| v.as_str()).unwrap_or("manual").to_string();
    if trigger != "manual" && trigger != "watchdog" && !triggers.contains(&trigger) { return Err(GovError::new("USAGE", format!("unknown checkpoint trigger '{trigger}' (policy triggers: {triggers:?})"))); }
    let store = RecordStore::load(&p.root);
    let seq = store.of_type("checkpoint").len() as i64 + 1;
    let id = format!("CKPT-{seq:05}");
    let o = fields.as_object_mut().unwrap();
    o.retain(|_, v| !v.is_null());
    if o.get("next_action").and_then(|v| v.as_str()).map(|s| s.is_empty()).unwrap_or(true) { return Err(GovError::new("USAGE", "checkpoint requires next_action")); }
    if pol.get_str("CHECKPOINT_POLICY", "prose_summary_as_checkpoint", "prohibited") == "prohibited" && o.get("summary").and_then(|v| v.as_str()).map(|s| s.len() > 2000).unwrap_or(false) { return Err(GovError::new("CHECKPOINT_POLICY", "prose summaries are prohibited as checkpoints (CHECKPOINT_POLICY.prose_summary_as_checkpoint); use structured fields")); }
    o.insert("session".into(), json!(p.session_id)); o.insert("role".into(), json!(p.role)); o.insert("sequence".into(), json!(seq));
    o.insert("trigger".into(), json!(trigger));
    o.entry("mode").or_insert(json!(control::state(p)["mode"]));
    if let Some(t) = o.get("task").and_then(|v| v.as_str()).map(|s| s.to_string()) { if let Ok(Some(c)) = claims::holder(p, &t) { o.insert("claim".into(), c); } }
    o.entry("pending_decisions").or_insert(json!(crate::orchestration::gates::pending(p).iter().map(|g| g["id"].clone()).collect::<Vec<_>>()));
    o.entry("open_transactions").or_insert(json!(store.of_type("cit").into_iter().filter(|c| matches!(c.get("cit_status").as_str(), "PROPOSED" | "SIMULATED" | "APPROVED" | "EXECUTING")).map(|c| c.id()).collect::<Vec<_>>()));
    o.entry("open_questions").or_insert(json!([]));
    o.entry("files_changed").or_insert(json!(p.git_dirty_files()));
    o.entry("tests_status").or_insert(json!("unknown"));
    let cph = o.get("task").and_then(|t| t.as_str()).and_then(|t| crate::util::read_json(&p.runtime_dir().join("context").join(format!("{t}.json"))).ok()).and_then(|c| c["packet_hash"].as_str().map(|s| s.to_string())).unwrap_or_default();
    o.entry("context_packet_hash").or_insert(json!(cph));
    o.entry("memory_snapshot").or_insert(json!({"index_manifest_hash": db.get_meta("index_manifest_hash").unwrap_or(Value::Null), "index_version": crate::INDEX_VERSION}));
    o.insert("state_class".into(), json!("EVIDENCE"));
    o.insert("created_at".into(), json!(now_iso()));
    let rec = new_record("checkpoint", &id, &format!("Checkpoint {seq} ({trigger})"), Value::Object(o.clone()));
    p.schemas().validate("checkpoint", &rec.data, &format!("({id})"))?;
    let mut rec = rec; rec.path = format!("{}/{id}.yaml", pol.get_str("CHECKPOINT_POLICY", "location", "spec/reports/checkpoints"));
    save_record(&p.root, &rec)?;
    write_yaml(&dir(p).join("LATEST.yaml"), &json!({"latest": id, "sequence": seq, "path": rec.path, "written_at": now_iso()}))?;
    if p.db_path().exists() { let _ = crate::memory::indexer::rebuild(p, crate::memory::indexer::IndexOptions { incremental: true, ..Default::default() }); }
    Ok(rec.data)
}

pub fn latest(p: &Project) -> Option<Value> {
    let ptr = read_yaml(&dir(p).join("LATEST.yaml")).ok()?;
    let path = ptr["path"].as_str()?;
    read_yaml(&p.root.join(path)).ok()
}

/// Provider-independent watchdog: checkpoint when context utilisation or operations-since-last exceed policy.
pub fn watchdog(p: &Project, db: &RuntimeDb, context_utilisation: f64, ops_since: i64, task: Option<&str>, next_action: &str) -> Result<Value> {
    let pol = p.policies();
    let th = pol.get_f64("CHECKPOINT_POLICY", "watchdog.context_utilisation_threshold", 0.75);
    let max_ops = pol.get_i64("CHECKPOINT_POLICY", "watchdog.max_operations_between_checkpoints", 25);
    if context_utilisation >= th || ops_since >= max_ops {
        let c = create(p, db, json!({"trigger": "watchdog", "task": task, "next_action": next_action, "last_completed_step": format!("watchdog fired (utilisation {context_utilisation:.2}, ops {ops_since})")}))?;
        return Ok(json!({"fired": true, "checkpoint": c["id"], "reason": if context_utilisation >= th { "context_utilisation" } else { "operations" }}));
    }
    Ok(json!({"fired": false, "threshold": th, "max_operations": max_ops}))
}
