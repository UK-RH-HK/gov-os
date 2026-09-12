//! Declarative framework-version migrations executed by `gov update` (only overlay/lock/generated/runtime are touched).
use crate::util::{deep_delete, deep_get, deep_set, read_yaml, write_yaml};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::Path;

pub fn load_migrations(kernel_dir: &Path) -> Vec<Value> {
    let dir = if kernel_dir.join("migrations").is_dir() {
        kernel_dir.join("migrations")
    } else if kernel_dir
        .file_name()
        .map(|n| n == "migrations")
        .unwrap_or(false)
    {
        kernel_dir.to_path_buf()
    } else {
        kernel_dir.join("migrations")
    };
    let Ok(rd) = std::fs::read_dir(&dir) else {
        return vec![];
    };
    let mut paths: Vec<_> = rd
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().map(|e| e == "yaml").unwrap_or(false))
        .collect();
    paths.sort();
    paths
        .into_iter()
        .filter_map(|p| read_yaml(&p).ok())
        .filter(|m| m.get("id").is_some())
        .collect()
}

/// Migrations forming a path from `from` to `to` (chained by from_version/to_version).
pub fn path(migrations: &[Value], from: &str, to: &str) -> Vec<Value> {
    let mut chain = vec![];
    let mut cur = from.to_string();
    for _ in 0..50 {
        if cur == to {
            break;
        }
        match migrations
            .iter()
            .find(|m| m["from_version"].as_str() == Some(&cur))
        {
            Some(m) => {
                cur = m["to_version"].as_str().unwrap_or("").to_string();
                chain.push(m.clone());
            }
            None => break,
        }
    }
    if cur != to {
        return vec![];
    }
    chain
}

#[derive(Debug, Clone, serde::Serialize, Default)]
pub struct MigrationOutcome {
    pub applied: Vec<Value>,
    pub index_rebuild: bool,
    pub regenerate_adapters: bool,
    pub overlay_keys_changed: Vec<String>,
    pub notes: Vec<String>,
}

pub fn apply(
    p: &Project,
    migration: &Value,
    new_kernel_dir: &Path,
    dry_run: bool,
    out: &mut MigrationOutcome,
) -> Result<()> {
    let overlay = p.overlay_dir();
    for op in migration["operations"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        let kind = op["op"].as_str().unwrap_or("");
        let file = op["file"].as_str().unwrap_or("").to_string();
        let if_missing = op["if_missing"].as_bool().unwrap_or(false);
        let mut rec = json!({"op": kind, "file": file, "dry_run": dry_run});
        match kind {
            "note" => {
                out.notes
                    .push(op["text"].as_str().unwrap_or("").to_string());
            }
            "add_overlay_file_from_template" => {
                let dest = overlay.join(&file);
                if dest.exists() && if_missing {
                    rec["skipped"] = json!("exists");
                } else if !dry_run {
                    let tpl = new_kernel_dir
                        .join("overlay-templates")
                        .join(op["template"].as_str().unwrap_or(&file));
                    std::fs::copy(&tpl, &dest).map_err(|e| {
                        GovError::new(
                            "MIGRATION_FAILED",
                            format!("copy template {}: {e}", tpl.display()),
                        )
                    })?;
                    out.overlay_keys_changed.push(format!("{file}:*"));
                }
            }
            "rename_overlay_file" => {
                let (from, to) = (
                    overlay.join(op["from"].as_str().unwrap_or("")),
                    overlay.join(op["to"].as_str().unwrap_or("")),
                );
                if from.exists() && !dry_run {
                    std::fs::rename(&from, &to)?;
                    out.overlay_keys_changed
                        .push(format!("{}:*", op["to"].as_str().unwrap_or("")));
                } else if !from.exists() && !if_missing {
                    return Err(GovError::new(
                        "MIGRATION_FAILED",
                        format!("{} missing", from.display()),
                    ));
                }
            }
            "set_overlay_key" | "rename_overlay_key" | "delete_overlay_key" => {
                let path = overlay.join(&file);
                let mut data = read_yaml(&path).unwrap_or(json!({}));
                match kind {
                    "set_overlay_key" => {
                        let key = op["key"].as_str().unwrap_or("");
                        if deep_get(&data, key).is_some() && if_missing {
                            rec["skipped"] = json!("exists");
                        } else {
                            deep_set(&mut data, key, op["value"].clone());
                            out.overlay_keys_changed.push(format!("{file}:{key}"));
                        }
                    }
                    "rename_overlay_key" => {
                        let (from, to) = (
                            op["from"].as_str().unwrap_or(""),
                            op["to"].as_str().unwrap_or(""),
                        );
                        match deep_get(&data, from).cloned() {
                            Some(v) => {
                                deep_delete(&mut data, from);
                                deep_set(&mut data, to, v);
                                out.overlay_keys_changed
                                    .push(format!("{file}:{from}->{to}"));
                            }
                            None => {
                                if !if_missing {
                                    return Err(GovError::new(
                                        "MIGRATION_FAILED",
                                        format!("{file}: key {from} missing"),
                                    ));
                                }
                                rec["skipped"] = json!("missing");
                            }
                        }
                    }
                    _ => {
                        let key = op["key"].as_str().unwrap_or("");
                        if deep_delete(&mut data, key) {
                            out.overlay_keys_changed.push(format!("{file}:-{key}"));
                        }
                    }
                }
                if !dry_run {
                    write_yaml(&path, &data)?;
                }
            }
            "set_overlay_rule" => {
                // update fields of one element of a rule list (e.g. REPOSITORY_CONTRACT.paths[pattern=...]) — the
                // mechanism by which a tightened template default reaches already-adopted projects (verifier M-N3)
                let path = overlay.join(&file);
                let mut data = read_yaml(&path).unwrap_or(json!({}));
                let list_key = op["list_key"].as_str().unwrap_or("paths");
                let m = op["match"].as_object().cloned().unwrap_or_default();
                let set = op["set"].as_object().cloned().unwrap_or_default();
                let mut changed = vec![];
                let mut found = false;
                if let Some(arr) = data.get_mut(list_key).and_then(|v| v.as_array_mut()) {
                    for el in arr.iter_mut() {
                        if m.iter().all(|(k, v)| el.get(k) == Some(v)) {
                            found = true;
                            for (k, v) in &set {
                                if el.get(k) != Some(v) {
                                    el[k] = v.clone();
                                    changed.push(format!(
                                        "{file}:{list_key}[{}].{k}",
                                        m.iter()
                                            .map(|(a, b)| format!("{a}={b}"))
                                            .collect::<Vec<_>>()
                                            .join(",")
                                    ));
                                }
                            }
                        }
                    }
                    if !found && op["add_if_missing"].as_bool().unwrap_or(false) {
                        let mut el = json!({});
                        for (k, v) in &m {
                            el[k] = v.clone();
                        }
                        for (k, v) in &set {
                            el[k] = v.clone();
                        }
                        if let Some(extra) = op["template_rule"].as_object() {
                            for (k, v) in extra {
                                if el.get(k).is_none() {
                                    el[k] = v.clone();
                                }
                            }
                        }
                        arr.push(el);
                        changed.push(format!("{file}:{list_key}[+]"));
                    }
                }
                if !found
                    && changed.is_empty()
                    && !if_missing
                    && !op["add_if_missing"].as_bool().unwrap_or(false)
                {
                    return Err(GovError::new(
                        "MIGRATION_FAILED",
                        format!("{file}: no {list_key} element matches {m:?}"),
                    ));
                }
                if changed.is_empty() {
                    rec["skipped"] = json!(if found { "already_set" } else { "missing" });
                }
                out.overlay_keys_changed.extend(changed);
                if !dry_run {
                    write_yaml(&path, &data)?;
                }
            }
            "set_lock_field" => {
                if !dry_run {
                    let mut lock = read_yaml(&p.lock_path())?;
                    lock[op["key"].as_str().unwrap_or("x")] = op["value"].clone();
                    write_yaml(&p.lock_path(), &lock)?;
                }
            }
            "require_index_rebuild" => {
                out.index_rebuild = true;
            }
            "regenerate_adapters" => {
                out.regenerate_adapters = true;
            }
            other => {
                return Err(GovError::new(
                    "MIGRATION_FAILED",
                    format!("unknown migration op {other}"),
                ))
            }
        }
        out.applied.push(rec);
    }
    Ok(())
}

const OVERLAY_OPS: &[&str] = &[
    "add_overlay_file_from_template",
    "rename_overlay_file",
    "set_overlay_key",
    "rename_overlay_key",
    "delete_overlay_key",
    "set_overlay_rule",
];

fn rule_key(el: &Value) -> Option<String> {
    ["pattern", "id", "name"].iter().find_map(|k| {
        el.get(k)
            .and_then(|v| v.as_str())
            .map(|s| format!("{k}={s}"))
    })
}

fn reconcile_value(
    old: &Value,
    new: &Value,
    proj: &mut Value,
    path: &str,
    changed: &mut Vec<String>,
) {
    match (old, new) {
        (Value::Object(o), Value::Object(n)) => {
            let Some(pm) = proj.as_object_mut() else {
                return;
            };
            for (k, nv) in n {
                let ov = o.get(k).cloned().unwrap_or(Value::Null);
                match pm.get_mut(k) {
                    Some(pv) => reconcile_value(&ov, nv, pv, &format!("{path}.{k}"), changed),
                    None => {
                        if o.get(k).is_none() && !nv.is_object() && !nv.is_array() {
                            /* new scalar default: the project never had it */
                            pm.insert(k.clone(), nv.clone());
                            changed.push(format!("{path}.{k}"));
                        }
                    }
                }
            }
        }
        (Value::Array(o), Value::Array(n))
            if n.iter().all(|e| rule_key(e).is_some())
                && o.iter().all(|e| rule_key(e).is_some()) =>
        {
            let Some(pa) = proj.as_array_mut() else {
                return;
            };
            for ne in n {
                let Some(k) = rule_key(ne) else { continue };
                let Some(oe) = o
                    .iter()
                    .find(|e| rule_key(e).as_deref() == Some(k.as_str()))
                else {
                    continue;
                };
                if let Some(pe) = pa
                    .iter_mut()
                    .find(|e| rule_key(e).as_deref() == Some(k.as_str()))
                {
                    reconcile_value(oe, ne, pe, &format!("{path}[{k}]"), changed);
                }
            }
        }
        _ => {
            if old != new && proj == old {
                *proj = new.clone();
                changed.push(path.to_string());
            }
        }
    }
}

/// Template-default reconciliation (verifier M-N3): after a kernel update, every overlay leaf that still carries the
/// OLD template default inherits the NEW default; values the project customised are preserved. Deterministic, keyed by
/// rule identity (`pattern`/`id`/`name`) for rule lists, recorded per key, snapshotted with the overlay (rollback-safe).
pub fn reconcile_overlay_defaults(
    overlay_dir: &Path,
    old_templates: &Path,
    new_templates: &Path,
    dry_run: bool,
) -> Result<Vec<String>> {
    let mut changed = vec![];
    let Ok(rd) = std::fs::read_dir(new_templates) else {
        return Ok(changed);
    };
    let mut files: Vec<_> = rd
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().map(|e| e == "yaml").unwrap_or(false))
        .collect();
    files.sort();
    for nf in files {
        let name = nf
            .file_name()
            .map(|n| n.to_string_lossy().to_string())
            .unwrap_or_default();
        let of = old_templates.join(&name);
        let pf = overlay_dir.join(&name);
        if !of.exists() || !pf.exists() {
            continue;
        }
        let (Ok(old), Ok(new), Ok(mut proj)) = (read_yaml(&of), read_yaml(&nf), read_yaml(&pf))
        else {
            continue;
        };
        if old == new {
            continue;
        }
        let mut local = vec![];
        reconcile_value(&old, &new, &mut proj, &name, &mut local);
        if !local.is_empty() {
            if !dry_run {
                write_yaml(&pf, &proj)?;
            }
            changed.extend(local.into_iter().map(|c| format!("reconciled:{c}")));
        }
    }
    Ok(changed)
}

/// Migration record integrity (verifier NV-19 / M-N3): when overlay templates differ between the migration's source
/// and target payloads, the migration must either carry an overlay operation for each changed template file or declare
/// the change under `overlay_template_changes` with how it is delivered (an op or `template_reconciliation`).
pub fn check_substance(
    migration: &Value,
    old_templates: &Path,
    new_templates: &Path,
) -> Vec<String> {
    let mut problems = vec![];
    let ops: Vec<&Value> = migration["operations"]
        .as_array()
        .map(|a| a.iter().collect())
        .unwrap_or_default();
    let overlay_files_in_ops: Vec<String> = ops
        .iter()
        .filter(|o| OVERLAY_OPS.contains(&o["op"].as_str().unwrap_or("")))
        .filter_map(|o| {
            o["file"]
                .as_str()
                .or(o["to"].as_str())
                .map(|s| s.to_string())
        })
        .collect();
    let declared: Vec<&Value> = migration["overlay_template_changes"]
        .as_array()
        .map(|a| a.iter().collect())
        .unwrap_or_default();
    let Ok(rd) = std::fs::read_dir(new_templates) else {
        return problems;
    };
    for nf in rd
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().map(|e| e == "yaml").unwrap_or(false))
    {
        let name = nf
            .file_name()
            .map(|n| n.to_string_lossy().to_string())
            .unwrap_or_default();
        let of = old_templates.join(&name);
        let differs = !of.exists() || std::fs::read(&of).ok() != std::fs::read(&nf).ok();
        if !differs {
            continue;
        }
        let covered_by_op = overlay_files_in_ops.iter().any(|f| f == &name);
        let decl = declared.iter().find(|d| d["file"].as_str() == Some(&name));
        match (covered_by_op, decl) {
            (true, _) => {}
            (false, Some(d)) => { let how = d["handled_by"].as_str().unwrap_or(""); if !(how == "template_reconciliation" || how.starts_with("op:") || how == "not_applicable") || d["reason"].as_str().unwrap_or("").is_empty() { problems.push(format!("{}: overlay template {name} changed; overlay_template_changes entry must state handled_by (template_reconciliation | op:<name> | not_applicable) and a reason", migration["id"])); } }
            (false, None) => problems.push(format!("{}: overlay template {name} changed between {} and {} but the migration has no overlay operation for it and does not declare it under overlay_template_changes", migration["id"], migration["from_version"], migration["to_version"])),
        }
    }
    let desc = migration["description"]
        .as_str()
        .unwrap_or("")
        .to_lowercase();
    if (desc.contains("tighten")
        || desc.contains("overlay is updated")
        || desc.contains("contract rule"))
        && overlay_files_in_ops.is_empty()
        && declared.is_empty()
    {
        problems.push(format!("{}: description claims an overlay/contract change but operations contain none and overlay_template_changes is absent", migration["id"]));
    }
    problems
}
