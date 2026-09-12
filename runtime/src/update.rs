//! `gov update` (framework §82, protocol §12): versioned, impact-checked kernel replacement with migrations,
//! overlay preservation, adapter regeneration, index rebuild, verification and CIT-E commit or rollback.
use crate::kernel::{install_kernel, resolve_kernel_source, KERNEL_MANIFEST};
use crate::lock::{compare_versions, write_lock};
use crate::memory::db::RuntimeDb;
use crate::migrations::framework::{apply, load_migrations, path as migration_path, MigrationOutcome};
use crate::orchestration::{control, gates};
use crate::util::{copy_dir, hash_tree, now_iso, read_json, read_yaml, remove_dir_if_exists, write_json};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::Path;

fn migrations_for_source(src: &Path) -> Vec<Value> {
    let m = load_migrations(src);
    if !m.is_empty() { return m; }
    src.parent().map(|p| load_migrations(&p.join("migrations").parent().unwrap_or(p))).unwrap_or_default()
}

fn source_manifest(src: &Path) -> Result<Value> {
    // A built release dir has manifest.json next to kernel/; a raw framework/ dir has KERNEL.yaml only.
    if let Some(parent) = src.parent() { let m = parent.join("manifest.json"); if m.exists() { return read_json(&m); } }
    let meta = read_yaml(&src.join("KERNEL.yaml"))?;
    let migs = migrations_for_source(src);
    let ver = meta["version"].as_str().unwrap_or("0").to_string();
    Ok(json!({"version": ver, "supported_from_versions": meta["supported_from_versions"], "migration_ids": migs.iter().filter(|m| m["to_version"].as_str() == Some(&ver)).map(|m| m["id"].clone()).collect::<Vec<_>>(), "breaking_changes": migs.iter().filter(|m| m["breaking"].as_bool().unwrap_or(false)).map(|m| m["description"].clone()).collect::<Vec<_>>(), "human_gates": migs.iter().filter_map(|m| m["human_gate"].as_str().filter(|g| *g != "none").map(|s| json!(s))).collect::<Vec<_>>(), "required_index_rebuilds": [], "release_notes": "(unreleased framework source)", "certification": {"status": "UNCERTIFIED"}}))
}

/// CIT-P for a framework update against this project.
pub fn check(p: &Project, source: Option<&str>) -> Result<Value> {
    p.require_installed()?;
    let src = resolve_kernel_source(source.map(Path::new))?;
    let avail = source_manifest(&src)?;
    let current = p.framework_version();
    let target = avail["version"].as_str().unwrap_or("0").to_string();
    let ord = compare_versions(&current, &target);
    let supported: Vec<String> = avail["supported_from_versions"].as_array().map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
    let migs = migrations_for_source(&src);
    let chain = migration_path(&migs, &current, &target);
    let compatible = supported.iter().any(|s| s == &current) || current == target;
    let mut dry = MigrationOutcome::default();
    for m in &chain { let _ = apply(p, m, &src, true, &mut dry); }
    let breaking: Vec<Value> = chain.iter().filter(|m| m["breaking"].as_bool().unwrap_or(false)).map(|m| m["description"].clone()).collect();
    let human_gates: Vec<Value> = chain.iter().filter_map(|m| m["human_gate"].as_str().filter(|g| *g != "none").map(|s| json!(s))).collect();
    let cert = avail["certification"]["status"].as_str().unwrap_or("UNCERTIFIED").to_string();
    let radius = if !breaking.is_empty() { "R5" } else if !dry.overlay_keys_changed.is_empty() { "R4" } else { "R3" };
    let human_gate_required = !breaking.is_empty() || !human_gates.is_empty() || cert != "CERTIFIED";
    let impact = json!({"radius": radius, "overlay_changes": dry.overlay_keys_changed, "index_rebuild": dry.index_rebuild, "regenerate_adapters": dry.regenerate_adapters, "notes": dry.notes, "breaking_changes": breaking, "human_gates": human_gates, "consequences": [
        format!("kernel {current} → {target} ({} migration step(s))", chain.len()), "spec/ and product/ are not touched (INV-013)", if dry.index_rebuild { "all derived indexes are rebuilt after install" } else { "no index rebuild required" },
        if cert == "CERTIFIED" { "target release is certified" } else { "target release is NOT certified: human approval required" }]});
    Ok(json!({"current": current, "available": target, "source": src.display().to_string(), "up_to_date": ord != std::cmp::Ordering::Less, "downgrade": ord == std::cmp::Ordering::Greater, "compatible": compatible, "migration_path": chain.iter().map(|m| m["id"].clone()).collect::<Vec<_>>(), "migration_path_complete": !chain.is_empty() || current == target,
        "certification": cert, "impact": impact, "human_gate_required": human_gate_required, "recommendation": if ord != std::cmp::Ordering::Less { "nothing to do" } else if !compatible { "unsupported upgrade path: adopt an intermediate release" } else if human_gate_required { "review impact; approve with `gov update --apply --approve --by <human>`" } else { "safe: `gov update --apply`" }}))
}

fn snapshot_dir(p: &Project, target: &str) -> std::path::PathBuf { p.runtime_dir().join("update").join(target) }

pub fn apply_update(p: &mut Project, source: Option<&str>, approve: bool, by: &str) -> Result<Value> {
    control::guard_write(p, "update --apply")?;
    let chk = check(p, source)?;
    if chk["up_to_date"].as_bool().unwrap_or(false) { return Ok(json!({"applied": false, "reason": "already up to date", "check": chk})); }
    if !chk["compatible"].as_bool().unwrap_or(false) || !chk["migration_path_complete"].as_bool().unwrap_or(false) { return Err(GovError::new("UPDATE_UNSUPPORTED", "no supported migration path from the installed version").with_details(chk)); }
    if chk["human_gate_required"].as_bool().unwrap_or(true) && !approve {
        let g = gates::create(p, json!({"question": format!("Approve framework update {} → {}?", chk["current"], chk["available"]), "why_now": "gov update --apply requested", "current_state": format!("installed {}", chk["current"]), "options": [{"id": "A", "description": "approve update"}, {"id": "B", "description": "stay on current release"}], "impact": chk["impact"]["consequences"].to_string(), "reversibility": "gov update --rollback restores kernel/overlay/lock", "recommendation": "A after reviewing release notes", "confidence": 0.7, "trigger": "governance_change", "impact_radius": chk["impact"]["radius"]}))?;
        return Err(GovError::new("HUMAN_GATE_REQUIRED", format!("update requires human approval: gate {} created; re-run with --approve --by <human> after presenting it", g["id"])).with_details(json!({"gate": g["id"], "check": chk})));
    }
    let target = chk["available"].as_str().unwrap_or("").to_string();
    let src = Path::new(chk["source"].as_str().unwrap_or(""));
    let db = RuntimeDb::open(&p.db_path())?; db.init_schema()?;
    let ck = crate::checkpoints::create(p, &db, json!({"trigger": "before_model_switch", "next_action": format!("gov update --apply to {target}"), "last_completed_step": "pre-update checkpoint"})).ok();
    // snapshot kernel + overlay + lock + generated
    let snap = snapshot_dir(p, &target);
    remove_dir_if_exists(&snap)?;
    for sub in ["kernel", "project", "generated"] { let s = p.governance_dir().join(sub); if s.exists() { copy_dir(&s, &snap.join(sub))?; } }
    std::fs::copy(p.lock_path(), snap.join("framework.lock"))?;
    write_json(&snap.join("snapshot.json"), &json!({"from": chk["current"], "to": target, "at": now_iso(), "checkpoint": ck.as_ref().map(|c| c["id"].clone())}))?;
    let (overlay_before, _) = hash_tree(&p.overlay_dir(), &[])?;
    let result: Result<Value> = (|| {
        let manifest = install_kernel(Some(src), &p.governance_dir())?;
        let migs = load_migrations(&p.kernel_dir());
        let chain = migration_path(&migs, chk["current"].as_str().unwrap_or(""), &target);
        let mut out = MigrationOutcome::default();
        for m in &chain { p.schemas().validate("migration", m, "(migration)")?; apply(p, m, &p.kernel_dir(), false, &mut out)?; }
        let commit = p.git_commit();
        write_lock(&p.lock_path(), &manifest, &src.to_string_lossy(), Some(&commit))?;
        for m in &chain { for op in m["operations"].as_array().cloned().unwrap_or_default() { if op["op"] == "set_lock_field" { let mut lock = read_yaml(&p.lock_path())?; lock[op["key"].as_str().unwrap_or("x")] = op["value"].clone(); crate::util::write_yaml(&p.lock_path(), &lock)?; } } }
        p.invalidate();
        // overlay preservation: only migration-declared changes may differ
        let (overlay_after, _) = hash_tree(&p.overlay_dir(), &[])?;
        if overlay_after != overlay_before && out.overlay_keys_changed.is_empty() { return Err(GovError::new("OVERLAY_CLOBBERED", "project overlay changed without a declaring migration (INV-013)")); }
        if !p.overlay().problems.is_empty() { return Err(GovError::new("OVERLAY_INVALID", format!("overlay invalid after migration: {}", p.overlay().problems.join("; ")))); }
        crate::tools::generate_registry(p)?;
        crate::adapters::generate(p)?;
        let rebuilt = if out.index_rebuild || !chk["impact"]["index_rebuild"].is_null() { Some(crate::memory::indexer::rebuild(p, crate::memory::indexer::IndexOptions { incremental: !out.index_rebuild })?.manifest_hash) } else { None };
        let doc = crate::doctor::run(p)?;
        let critical: Vec<Value> = doc.checks.iter().filter(|c| !c["ok"].as_bool().unwrap_or(true) && c["severity"] == "critical").cloned().collect();
        if !critical.is_empty() { return Err(GovError::new("VERIFICATION_FAILED", format!("doctor reports critical findings after update: {}", critical.iter().map(|c| c["id"].as_str().unwrap_or("").to_string()).collect::<Vec<_>>().join(", "))).with_details(json!(critical))); }
        let audit = crate::verification::audit(p, &crate::verification::SuiteOptions { deep: false, families: vec!["schema_invariants".into(), "mutation_scope".into(), "adapter_portability".into(), "secrets_sensitivity_indexing".into()] }, false)?;
        if audit["counts"]["critical"].as_u64().unwrap_or(0) > 0 { return Err(GovError::new("VERIFICATION_FAILED", "governance suite reports critical findings after update").with_details(audit)); }
        Ok(json!({"migrations": chain.iter().map(|m| m["id"].clone()).collect::<Vec<_>>(), "operations": out.applied, "overlay_keys_changed": out.overlay_keys_changed, "index_manifest": rebuilt, "doctor": doc.verdict, "audit": audit["verdict"]}))
    })();
    match result {
        Ok(v) => {
            let ledger = p.root.join("spec/reports/framework-updates.jsonl");
            let mut text = crate::util::read_text(&ledger).unwrap_or_default();
            text.push_str(&serde_json::to_string(&json!({"at": now_iso(), "from": chk["current"], "to": target, "by": by, "session": p.session_id, "result": "committed", "details": v}))?); text.push('\n');
            crate::util::write_text(&ledger, &text)?;
            let db2 = RuntimeDb::open(&p.db_path())?;
            let _ = crate::checkpoints::create(p, &db2, json!({"trigger": "accepted_cit", "next_action": "gov status", "last_completed_step": format!("framework updated to {target}")}));
            Ok(json!({"applied": true, "from": chk["current"], "to": target, "details": v, "rollback": "gov update --rollback"}))
        }
        Err(e) => { let rb = rollback(p, Some(&target))?; Err(GovError::new(&e.code, format!("{} — update rolled back", e.message)).with_details(json!({"rollback": rb, "details": e.details}))) }
    }
}

/// Restore kernel, overlay, generated and lock from the update snapshot; rebuild indexes.
pub fn rollback(p: &mut Project, target: Option<&str>) -> Result<Value> {
    let base = p.runtime_dir().join("update");
    let dir = match target { Some(t) => base.join(t), None => { let mut dirs: Vec<_> = std::fs::read_dir(&base).map(|rd| rd.filter_map(|e| e.ok()).map(|e| e.path()).filter(|x| x.join("snapshot.json").exists()).collect()).unwrap_or_default(); dirs.sort_by_key(|d| std::fs::metadata(d.join("snapshot.json")).and_then(|m| m.modified()).ok()); dirs.pop().ok_or_else(|| GovError::new("SNAPSHOT_MISSING", "no update snapshot found"))? } };
    let meta = read_json(&dir.join("snapshot.json"))?;
    for sub in ["kernel", "project", "generated"] { let s = dir.join(sub); let d = p.governance_dir().join(sub); if s.exists() { remove_dir_if_exists(&d)?; copy_dir(&s, &d)?; } }
    std::fs::copy(dir.join("framework.lock"), p.lock_path())?;
    p.invalidate();
    let ok = p.kernel_dir().join(KERNEL_MANIFEST).exists() && crate::kernel::verify_kernel(&p.kernel_dir()).map(|v| v.ok).unwrap_or(false);
    let r = crate::memory::indexer::rebuild(p, crate::memory::indexer::IndexOptions { incremental: false })?;
    Ok(json!({"rolled_back_to": meta["from"], "kernel_ok": ok, "index_manifest": r.manifest_hash}))
}
