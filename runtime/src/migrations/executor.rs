//! A6 controlled migration: batch snapshot → actions → reference updates → checks → ledger; rollback on failure.
use super::refs::update_references;
use crate::records::{new_record, save_record};
use crate::util::{copy_dir, now_iso, read_json, read_text, write_json, write_text};
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

pub fn snapshot_dir(root: &Path, batch: i64) -> PathBuf { root.join(crate::RUNTIME_DIR).join("migration").join(format!("batch-{batch}")) }

fn git_mv(root: &Path, from: &str, to: &str) -> Result<()> {
    if let Some(d) = root.join(to).parent() { std::fs::create_dir_all(d)?; }
    let st = std::process::Command::new("git").args(["mv", "-k", from, to]).current_dir(root).output();
    if !(st.map(|o| o.status.success()).unwrap_or(false) && root.join(to).exists()) { std::fs::rename(root.join(from), root.join(to))?; }
    Ok(())
}

fn git_rm(root: &Path, path: &str) -> Result<()> {
    let st = std::process::Command::new("git").args(["rm", "-q", "--cached", path]).current_dir(root).output();
    let _ = st;
    let full = root.join(path);
    if full.is_file() { std::fs::remove_file(full)?; } else if full.is_dir() { std::fs::remove_dir_all(full)?; }
    Ok(())
}

/// Extract a legacy markdown decision/lesson document into governed PROVISIONAL records; archive the original.
fn extract_doc(root: &Path, entry: &Value, next_ids: &mut (u32, u32)) -> Result<(Vec<String>, String)> {
    let path = entry["current_path"].as_str().unwrap_or("");
    let text = read_text(&root.join(path))?;
    let is_decision = entry["target_class"] == "DECISION";
    let target_dir = entry["target_path"].as_str().unwrap_or(if is_decision { "spec/decisions/" } else { "spec/lessons/" }).to_string();
    let mut created = vec![];
    // split on H2/H1 headings; each heading becomes a record; fallback = whole document
    let rx = regex::Regex::new(r"(?m)^#{1,2}\s+(.+)$").unwrap();
    let mut sections: Vec<(String, String)> = vec![];
    let mut last_title = Path::new(path).file_stem().map(|s| s.to_string_lossy().to_string()).unwrap_or("legacy".into());
    let mut pos = 0;
    for m in rx.captures_iter(&text) { let whole = m.get(0).unwrap(); let body = text[pos..whole.start()].trim().to_string(); if !body.is_empty() { sections.push((last_title.clone(), body)); } last_title = m[1].trim().to_string(); pos = whole.end(); }
    let tail = text[pos..].trim().to_string(); if !tail.is_empty() { sections.push((last_title, tail)); }
    if sections.is_empty() { sections.push((Path::new(path).file_stem().map(|s| s.to_string_lossy().to_string()).unwrap_or("legacy".into()), text.clone())); }
    for (title, body) in sections {
        if body.len() < 20 { continue; }
        let low = body.to_lowercase();
        let superseded = low.contains("superseded") || low.contains("deprecated") || low.contains("obsolete");
        let (rtype, id) = if is_decision { next_ids.0 += 1; ("decision", format!("D-L{:04}", next_ids.0)) } else { next_ids.1 += 1; ("lesson", format!("L-L{:04}", next_ids.1)) };
        let mut fields = json!({"status": if superseded { "SUPERSEDED" } else { "PROVISIONAL" }, "state_class": if superseded { "HISTORICAL" } else { "AUTHORITATIVE" }, "legacy_source": path, "provenance": {"extracted_from": path, "extracted_at": now_iso(), "method": "adopt extract (heading split)", "authority_note": "LEGACY material: PROVISIONAL until confirmed by decision (INV-004)"}, "body": body, "tags": ["legacy-extraction"]});
        if is_decision { fields["question"] = json!(title); fields["rationale"] = json!(body.chars().take(500).collect::<String>()); fields["human_approved"] = json!(false); fields["chosen_option"] = json!("as-recorded-in-legacy"); }
        else { fields["scope"] = json!("PROJECT"); fields["lifecycle"] = json!("candidate"); fields["problem_statement"] = json!(title); fields["evidence_strength"] = json!("low"); }
        let mut rec = new_record(rtype, &id, &title, fields);
        rec.path = format!("{}{}.yaml", target_dir.trim_end_matches('/').to_string() + "/", id);
        save_record(root, &rec)?;
        created.push(rec.path.clone());
    }
    let archive_to = format!("archive/spec/legacy-docs/{}", path.replace('/', "__"));
    git_mv(root, path, &archive_to)?;
    Ok((created, archive_to))
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct BatchResult { pub batch: i64, pub applied: Vec<Value>, pub moves: Vec<(String, String)>, pub references_updated: Vec<String>, pub created: Vec<String>, pub snapshot: String, pub skipped: Vec<Value> }

/// Execute one batch of the catalogue. `gate_answers` lists artefact ids whose human gate has been answered YES.
pub fn apply_batch(root: &Path, catalogue: &[Value], batch: i64, gate_answers: &[String], ledger: &Path) -> Result<BatchResult> {
    let entries: Vec<&Value> = catalogue.iter().filter(|e| e["batch"].as_i64() == Some(batch) && e["action"] != "KEEP_IN_PLACE").collect();
    let snap = snapshot_dir(root, batch);
    crate::util::remove_dir_if_exists(&snap)?;
    std::fs::create_dir_all(&snap)?;
    let mut touched: Vec<String> = vec![];
    for e in &entries { for k in ["current_path", "target_path"] { if let Some(p) = e[k].as_str() { if !p.is_empty() && root.join(p).exists() && !touched.contains(&p.to_string()) { touched.push(p.to_string()); } } } }
    for t in &touched { let src = root.join(t); if src.is_file() { let dst = snap.join("files").join(t); if let Some(d) = dst.parent() { std::fs::create_dir_all(d)?; } std::fs::copy(&src, &dst)?; } else if src.is_dir() { copy_dir(&src, &snap.join("files").join(t))?; } }
    let mut result = BatchResult { batch, applied: vec![], moves: vec![], references_updated: vec![], created: vec![], snapshot: snap.to_string_lossy().to_string(), skipped: vec![] };
    let mut next_ids = (0u32, 0u32);
    let mut ledger_lines = vec![];
    for e in entries {
        let action = e["action"].as_str().unwrap_or("");
        let from = e["current_path"].as_str().unwrap_or("").to_string();
        let aid = e["artifact_id"].as_str().unwrap_or("").to_string();
        if e["requires_human_gate"].as_bool().unwrap_or(false) && !gate_answers.contains(&aid) { result.skipped.push(json!({"artifact_id": aid, "path": from, "reason": "requires an answered human gate"})); continue; }
        if action == "EXTRACT" && e["target_path"].as_str().map(|t| t.contains("memory-stores")).unwrap_or(false) { result.skipped.push(json!({"artifact_id": aid, "path": from, "reason": "legacy memory store: extraction and retirement happen in A8 after migration acceptance (protocol §13)"})); continue; }
        if !root.join(&from).exists() { result.skipped.push(json!({"artifact_id": aid, "path": from, "reason": "NOT_FOUND at execution time (not proof of absence)"})); continue; }
        let outcome: Result<Value> = (|| match action {
            "MOVE" | "RENAME" => { let to = e["target_path"].as_str().unwrap_or("").to_string(); if to.is_empty() { return Err(GovError::new("PLAN_INVALID", format!("{aid}: MOVE without target"))); } git_mv(root, &from, &to)?; result.moves.push((from.clone(), to.clone())); Ok(json!({"to": to})) }
            "EXTRACT" => {
                if e["target_class"] == "DECISION" || e["target_class"] == "LESSON" { let (c, archived) = extract_doc(root, e, &mut next_ids)?; result.created.extend(c.clone()); result.moves.push((from.clone(), archived.clone())); Ok(json!({"created": c, "original_archived_to": archived})) }
                else { let to = e["target_path"].as_str().unwrap_or("").to_string(); git_mv(root, &from, &to)?; result.moves.push((from.clone(), to.clone())); Ok(json!({"to": to, "note": "store retired to archive after extraction (see 09 report)"})) }
            }
            "RETIRE" => { let to = format!("archive/code-reference/retired/{}", from.replace('/', "__")); git_mv(root, &from, &to)?; result.moves.push((from.clone(), to.clone())); Ok(json!({"to": to})) }
            "DELETE_FROM_ACTIVE_TREE" => { git_rm(root, &from)?; Ok(json!({"deleted": true})) }
            "SPLIT" | "MERGE" => Err(GovError::new("PLAN_UNSUPPORTED", format!("{aid}: {action} requires a manual CIT"))),
            other => Err(GovError::new("PLAN_INVALID", format!("{aid}: unknown action {other}"))),
        })();
        match outcome {
            Ok(v) => { result.applied.push(json!({"artifact_id": aid, "action": action, "path": from, "result": v})); ledger_lines.push(json!({"at": now_iso(), "batch": batch, "artifact_id": aid, "action": action, "path": from, "result": v, "status": "applied"})); }
            Err(err) => { ledger_lines.push(json!({"at": now_iso(), "batch": batch, "artifact_id": aid, "action": action, "path": from, "status": "failed", "error": err.to_string()})); append_ledger(ledger, &ledger_lines)?; rollback_batch(root, batch)?; return Err(GovError::new("MIGRATION_BATCH_FAILED", format!("batch {batch} failed at {aid} ({err}); batch rolled back"))); }
        }
    }
    result.references_updated = update_references(root, &result.moves)?;
    write_json(&snap.join("batch.json"), &json!({"batch": batch, "touched": touched, "moves": result.moves, "created": result.created, "references_updated": result.references_updated, "at": now_iso()}))?;
    ledger_lines.push(json!({"at": now_iso(), "batch": batch, "status": "batch_complete", "applied": result.applied.len(), "references_updated": result.references_updated.len()}));
    append_ledger(ledger, &ledger_lines)?;
    Ok(result)
}

fn append_ledger(ledger: &Path, lines: &[Value]) -> Result<()> {
    if let Some(d) = ledger.parent() { std::fs::create_dir_all(d)?; }
    let mut text = if ledger.exists() { read_text(ledger)? } else { String::new() };
    for l in lines { text.push_str(&serde_json::to_string(l)?); text.push('\n'); }
    write_text(ledger, &text)
}

/// Restore a batch from its snapshot: reverse moves, remove created files, restore originals.
pub fn rollback_batch(root: &Path, batch: i64) -> Result<Value> {
    let snap = snapshot_dir(root, batch);
    let meta = read_json(&snap.join("batch.json")).unwrap_or(json!({"moves": [], "created": [], "touched": []}));
    let mut restored = vec![]; let mut removed = vec![];
    for m in meta["moves"].as_array().cloned().unwrap_or_default() { let (from, to) = (m[0].as_str().unwrap_or(""), m[1].as_str().unwrap_or("")); if root.join(to).exists() && !root.join(from).exists() { git_mv(root, to, from)?; restored.push(from.to_string()); } }
    for c in meta["created"].as_array().cloned().unwrap_or_default() { let p = c.as_str().unwrap_or(""); if root.join(p).exists() && !meta["touched"].as_array().map(|a| a.iter().any(|t| t.as_str() == Some(p))).unwrap_or(false) { let _ = git_rm(root, p); removed.push(p.to_string()); } }
    let files = snap.join("files");
    if files.exists() {
        for entry in walkdir::WalkDir::new(&files).into_iter().filter_map(|e| e.ok()).filter(|e| e.file_type().is_file()) {
            let rel = entry.path().strip_prefix(&files).unwrap().to_string_lossy().replace('\\', "/");
            let dst = root.join(&rel); if let Some(d) = dst.parent() { std::fs::create_dir_all(d)?; } std::fs::copy(entry.path(), &dst)?; if !restored.contains(&rel) { restored.push(rel); }
        }
    }
    // references: re-run reverse replacement
    let reverse: Vec<(String, String)> = meta["moves"].as_array().cloned().unwrap_or_default().iter().map(|m| (m[1].as_str().unwrap_or("").to_string(), m[0].as_str().unwrap_or("").to_string())).collect();
    let refs = super::refs::update_references_opts(root, &reverse, false, &restored)?;
    Ok(json!({"batch": batch, "restored": restored, "removed": removed, "references_reverted": refs}))
}
