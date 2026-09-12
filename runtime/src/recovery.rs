//! Interrupted-session recovery (protocol §4): classify partial mutations, finish or roll back, checkpoint, freeze on UNKNOWN.
use crate::memory::db::RuntimeDb;
use crate::orchestration::{claims, control};
use crate::records::{new_record, save_record, RecordStore};
use crate::util::now_iso;
use crate::{Project, Result};
use serde_json::{json, Value};

pub fn recover(p: &Project, dry_run: bool) -> Result<Value> {
    p.require_installed()?;
    let mut items = vec![]; let mut actions = vec![]; let mut unknown = 0;
    // 1. interrupted CITs
    for c in crate::cit::interrupted(p) {
        let id = c["id"].as_str().unwrap_or("").to_string();
        let cls = if c["snapshot_present"].as_bool().unwrap_or(false) { "PARTIAL_SHOULD_ROLL_BACK" } else { "UNKNOWN" };
        items.push(json!({"kind": "cit", "id": id, "classification": cls}));
        if cls == "PARTIAL_SHOULD_ROLL_BACK" && !dry_run { let r = crate::cit::rollback(p, &id, Some("recovery: interrupted execution"))?; actions.push(json!({"rolled_back": id, "restored": r["rollback"]["restored"]})); } else if cls == "UNKNOWN" { unknown += 1; }
    }
    // 2. interrupted migration batches (ledger without batch_complete)
    let ledger = p.root.join("spec/audits/GOVERNANCE-ADOPTION/migration-ledger.jsonl");
    if ledger.exists() {
        let lines: Vec<Value> = crate::util::read_text(&ledger)?.lines().filter_map(|l| serde_json::from_str(l).ok()).collect();
        let mut open: std::collections::BTreeMap<i64, bool> = std::collections::BTreeMap::new();
        for l in &lines { if let Some(b) = l["batch"].as_i64() { let e = open.entry(b).or_insert(false); if l["status"] == "batch_complete" { *e = true; } } }
        for (b, done) in open { if !done { items.push(json!({"kind": "migration_batch", "batch": b, "classification": "PARTIAL_SHOULD_ROLL_BACK"})); if !dry_run { let r = crate::migrations::executor::rollback_batch(&p.root, b)?; actions.push(json!({"rolled_back_batch": b, "restored": r["restored"]})); } } }
    }
    // 3. runtime DB health
    let db_ok = p.db_path().exists() && RuntimeDb::open(&p.db_path()).map(|d| d.has_schema() && d.integrity_ok()).unwrap_or(false);
    if p.db_path().exists() && !db_ok { items.push(json!({"kind": "runtime_db", "classification": "PARTIAL_SAFE_TO_FINISH"})); if !dry_run { let r = crate::memory::indexer::rebuild(p, crate::memory::indexer::IndexOptions { incremental: false })?; actions.push(json!({"rebuilt_runtime": true, "manifest_hash": r.manifest_hash})); } }
    // 4. expired claims
    if let Ok(db) = RuntimeDb::open(&p.db_path()) { if db.has_schema() { let n = if dry_run { claims::list(&db)?.iter().filter(|c| c["expired"].as_bool().unwrap_or(false)).count() } else { claims::sweep_expired(&db)? }; if n > 0 { items.push(json!({"kind": "claims", "expired": n, "classification": "COMPLETE_UNVERIFIED"})); actions.push(json!({"claims_swept": n})); } } }
    // 5. dirty governance files (uncommitted) → COMPLETE_UNVERIFIED
    let dirty: Vec<String> = p.git_dirty_files().into_iter().filter(|f| f.starts_with("governance/") || f.starts_with("spec/")).collect();
    if !dirty.is_empty() { items.push(json!({"kind": "uncommitted_governance_changes", "files": dirty, "classification": "COMPLETE_UNVERIFIED"})); }
    // 6. adoption in progress
    let base = p.root.join("spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml");
    if base.exists() { if let Ok(b) = crate::util::read_yaml(&base) { if let Some(st) = b["stage_status"].as_object() { for (k, v) in st { if v == "in_progress" { items.push(json!({"kind": "adoption_stage", "stage": k, "classification": "UNKNOWN"})); unknown += 1; } } } } }
    let mut frozen = false;
    if unknown > 0 && !dry_run { control::set(p, "FREEZE_WRITES", Some("recovery found UNKNOWN partial mutations; broad governance/memory work frozen until reviewed"))?; frozen = true; }
    let mut checkpoint = Value::Null;
    if !dry_run {
        let db = RuntimeDb::open(&p.db_path())?; db.init_schema()?;
        if !frozen { checkpoint = crate::checkpoints::create(p, &db, json!({"trigger": "manual", "next_action": "gov status; review recovery report", "last_completed_step": "recovery", "open_questions": items.iter().filter(|i| i["classification"] == "UNKNOWN").map(|i| i.to_string()).collect::<Vec<_>>()}))?; }
        let store = RecordStore::load(&p.root);
        let id = store.next_id("report");
        let rec = new_record("report", &id, &format!("Recovery report {id}"), json!({"task": "recovery", "role": p.role, "outcome": if unknown > 0 { "blocked" } else { "success" }, "work_completed": format!("classified {} interrupted item(s); {} action(s) applied", items.len(), actions.len()), "files_changed": [], "evidence": items.clone(), "tests": {"status": "not_applicable_with_reason", "reason": "recovery"}, "discoveries": actions.clone(), "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": items.iter().filter(|i| i["classification"] == "UNKNOWN").cloned().collect::<Vec<_>>(), "recommended_next_action": if frozen { "review UNKNOWN items, then gov resume" } else { "gov status" }, "state_class": "EVIDENCE", "recovered_at": now_iso()}));
        save_record(&p.root, &rec)?;
    }
    Ok(json!({"items": items, "actions": actions, "unknown": unknown, "writes_frozen": frozen, "checkpoint": checkpoint["id"], "dry_run": dry_run}))
}
