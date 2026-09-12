//! Declarative framework-version migrations executed by `gov update` (only overlay/lock/generated/runtime are touched).
use crate::util::{deep_delete, deep_get, deep_set, read_yaml, write_yaml};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::Path;

pub fn load_migrations(kernel_dir: &Path) -> Vec<Value> {
    let dir = if kernel_dir.join("migrations").is_dir() { kernel_dir.join("migrations") } else if kernel_dir.file_name().map(|n| n == "migrations").unwrap_or(false) { kernel_dir.to_path_buf() } else { kernel_dir.join("migrations") };
    let Ok(rd) = std::fs::read_dir(&dir) else { return vec![] };
    let mut paths: Vec<_> = rd.filter_map(|e| e.ok()).map(|e| e.path()).filter(|p| p.extension().map(|e| e == "yaml").unwrap_or(false)).collect();
    paths.sort();
    paths.into_iter().filter_map(|p| read_yaml(&p).ok()).filter(|m| m.get("id").is_some()).collect()
}

/// Migrations forming a path from `from` to `to` (chained by from_version/to_version).
pub fn path(migrations: &[Value], from: &str, to: &str) -> Vec<Value> {
    let mut chain = vec![]; let mut cur = from.to_string();
    for _ in 0..50 {
        if cur == to { break; }
        match migrations.iter().find(|m| m["from_version"].as_str() == Some(&cur)) { Some(m) => { cur = m["to_version"].as_str().unwrap_or("").to_string(); chain.push(m.clone()); } None => break }
    }
    if cur != to { return vec![]; }
    chain
}

#[derive(Debug, Clone, serde::Serialize, Default)]
pub struct MigrationOutcome { pub applied: Vec<Value>, pub index_rebuild: bool, pub regenerate_adapters: bool, pub overlay_keys_changed: Vec<String>, pub notes: Vec<String> }

pub fn apply(p: &Project, migration: &Value, new_kernel_dir: &Path, dry_run: bool, out: &mut MigrationOutcome) -> Result<()> {
    let overlay = p.overlay_dir();
    for op in migration["operations"].as_array().cloned().unwrap_or_default() {
        let kind = op["op"].as_str().unwrap_or("");
        let file = op["file"].as_str().unwrap_or("").to_string();
        let if_missing = op["if_missing"].as_bool().unwrap_or(false);
        let mut rec = json!({"op": kind, "file": file, "dry_run": dry_run});
        match kind {
            "note" => { out.notes.push(op["text"].as_str().unwrap_or("").to_string()); }
            "add_overlay_file_from_template" => {
                let dest = overlay.join(&file);
                if dest.exists() && if_missing { rec["skipped"] = json!("exists"); }
                else if !dry_run { let tpl = new_kernel_dir.join("overlay-templates").join(op["template"].as_str().unwrap_or(&file)); std::fs::copy(&tpl, &dest).map_err(|e| GovError::new("MIGRATION_FAILED", format!("copy template {}: {e}", tpl.display())))?; out.overlay_keys_changed.push(format!("{file}:*")); }
            }
            "rename_overlay_file" => { let (from, to) = (overlay.join(op["from"].as_str().unwrap_or("")), overlay.join(op["to"].as_str().unwrap_or(""))); if from.exists() && !dry_run { std::fs::rename(&from, &to)?; out.overlay_keys_changed.push(format!("{}:*", op["to"].as_str().unwrap_or(""))); } else if !from.exists() && !if_missing { return Err(GovError::new("MIGRATION_FAILED", format!("{} missing", from.display()))); } }
            "set_overlay_key" | "rename_overlay_key" | "delete_overlay_key" => {
                let path = overlay.join(&file);
                let mut data = read_yaml(&path).unwrap_or(json!({}));
                match kind {
                    "set_overlay_key" => { let key = op["key"].as_str().unwrap_or(""); if deep_get(&data, key).is_some() && if_missing { rec["skipped"] = json!("exists"); } else { deep_set(&mut data, key, op["value"].clone()); out.overlay_keys_changed.push(format!("{file}:{key}")); } }
                    "rename_overlay_key" => { let (from, to) = (op["from"].as_str().unwrap_or(""), op["to"].as_str().unwrap_or("")); match deep_get(&data, from).cloned() { Some(v) => { deep_delete(&mut data, from); deep_set(&mut data, to, v); out.overlay_keys_changed.push(format!("{file}:{from}->{to}")); } None => { if !if_missing { return Err(GovError::new("MIGRATION_FAILED", format!("{file}: key {from} missing"))); } rec["skipped"] = json!("missing"); } } }
                    _ => { let key = op["key"].as_str().unwrap_or(""); if deep_delete(&mut data, key) { out.overlay_keys_changed.push(format!("{file}:-{key}")); } }
                }
                if !dry_run { write_yaml(&path, &data)?; }
            }
            "set_lock_field" => { if !dry_run { let mut lock = read_yaml(&p.lock_path())?; lock[op["key"].as_str().unwrap_or("x")] = op["value"].clone(); write_yaml(&p.lock_path(), &lock)?; } }
            "require_index_rebuild" => { out.index_rebuild = true; }
            "regenerate_adapters" => { out.regenerate_adapters = true; }
            other => return Err(GovError::new("MIGRATION_FAILED", format!("unknown migration op {other}"))),
        }
        out.applied.push(rec);
    }
    Ok(())
}
