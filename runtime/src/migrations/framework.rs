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
    /// Places where a project customised what the new template also changed: the project's value is kept and the
    /// template's is reported here (`sync_overlay_template`), never silently dropped or applied.
    pub template_conflicts: Vec<Value>,
}

pub fn apply(
    p: &Project,
    migration: &Value,
    new_kernel_dir: &Path,
    dry_run: bool,
    out: &mut MigrationOutcome,
) -> Result<()> {
    let overlay = p.overlay_dir();
    let templates = new_kernel_dir.join("overlay-templates");
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
                    let tpl = templates.join(op["template"].as_str().unwrap_or(&file));
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
            k if EDIT_OPS.contains(&k) => {
                let path = overlay.join(&file);
                if k == "sync_overlay_template" && !path.exists() {
                    // nothing installed to converge; a missing overlay file is `add_overlay_file_from_template`'s
                    rec["skipped"] = json!("overlay file missing");
                } else {
                    let before = read_yaml(&path).unwrap_or(json!({}));
                    let mut data = before.clone();
                    let edit = edit_overlay(k, &op, &file, &mut data, &templates)?;
                    for (key, v) in edit.record.as_object().cloned().unwrap_or_default() {
                        rec[key] = v;
                    }
                    out.template_conflicts.extend(edit.conflicts);
                    out.overlay_keys_changed.extend(edit.changed);
                    if !dry_run && data != before {
                        // an overlay that converged exactly to the new template gets the template's own bytes (its
                        // comments and layout), so it is byte-identical to a new installation's
                        let tpl = templates.join(op["template"].as_str().unwrap_or(&file));
                        match read_yaml(&tpl) {
                            Ok(t) if k == "sync_overlay_template" && t == data => {
                                std::fs::copy(&tpl, &path).map_err(|e| {
                                    GovError::new(
                                        "MIGRATION_FAILED",
                                        format!("copy template {}: {e}", tpl.display()),
                                    )
                                })?;
                            }
                            _ => write_yaml(&path, &data)?,
                        }
                    }
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
            // WS-7 IP-W7R3-5 / WS-6 IP-R3-WS06-7 (round 4): the tracked OS-written stores an earlier release kept in
            // the regenerable views (`governance/generated/`) move to where they belong at upgrade — the plugin
            // registry and the skill content bindings — so a brownfield project's registrations and bindings survive
            // deleting the generated views from the moment it is upgraded, not only after its next registry write.
            // The bytes move as they are (every seal included: nothing becomes honoured by moving, nothing is
            // re-sealed); a store already at its location with a differing legacy copy keeps the location and the
            // legacy copy is left and reported (`paths::misplaced_os_state`). Only tracked stores: machine-local
            // operational stores move on first use by their own writers, under their own locks.
            "relocate_os_stores" => {
                let wanted: Vec<String> = match op["stores"].as_array() {
                    Some(a) => a
                        .iter()
                        .filter_map(|x| x.as_str().map(String::from))
                        .collect(),
                    None => crate::paths::OS_STORES
                        .iter()
                        .filter(|s| s.tracked)
                        .map(|s| s.id.to_string())
                        .collect(),
                };
                let mut moved = vec![];
                for id in wanted {
                    let store = crate::paths::os_store(&id).filter(|s| s.tracked).ok_or_else(|| {
                        GovError::new(
                            "MIGRATION_FAILED",
                            format!("relocate_os_stores: '{id}' is not a tracked OS store (paths::OS_STORES); machine-local stores move on first use by their writers"),
                        )
                    })?;
                    if dry_run {
                        for (from, to) in store.moves {
                            if p.root.join(from).exists() {
                                moved.push(json!({"store": id, "from": from, "to": to, "action": "would move"}));
                            }
                        }
                        continue;
                    }
                    moved.extend(match id.as_str() {
                        "plugin-registry" => crate::capabilities::registry::relocate(p)?,
                        "skill-bindings" => crate::skills::relocate_bindings(p)?,
                        other => crate::paths::relocate_legacy(&p.root, other)?,
                    });
                }
                rec["moved"] = json!(moved);
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

/// The operations that edit one overlay file in place (the in-memory part [`edit_overlay`] performs).
const EDIT_OPS: &[&str] = &[
    "set_overlay_key",
    "rename_overlay_key",
    "delete_overlay_key",
    "set_overlay_rule",
    "sync_overlay_template",
];

/// What one in-place overlay edit changed.
#[derive(Debug, Default)]
struct Edit {
    changed: Vec<String>,
    conflicts: Vec<Value>,
    /// fields merged into the operation's record (`skipped`, `changed`, `conflicts`, ...)
    record: Value,
}

/// Apply one in-place overlay operation to `data` (the parsed overlay file `file`). `templates` is the installing
/// kernel's `overlay-templates/` directory. Shared by [`apply`] (on the project's file) and the substance check's
/// simulation of an update (on the previous release's template), so both run the same operation.
fn edit_overlay(
    kind: &str,
    op: &Value,
    file: &str,
    data: &mut Value,
    templates: &Path,
) -> Result<Edit> {
    let if_missing = op["if_missing"].as_bool().unwrap_or(false);
    let mut e = Edit {
        record: json!({}),
        ..Default::default()
    };
    match kind {
        "set_overlay_key" => {
            let key = op["key"].as_str().unwrap_or("");
            if deep_get(data, key).is_some() && if_missing {
                e.record["skipped"] = json!("exists");
            } else {
                deep_set(data, key, op["value"].clone());
                e.changed.push(format!("{file}:{key}"));
            }
        }
        "rename_overlay_key" => {
            let (from, to) = (
                op["from"].as_str().unwrap_or(""),
                op["to"].as_str().unwrap_or(""),
            );
            match deep_get(data, from).cloned() {
                Some(v) => {
                    deep_delete(data, from);
                    deep_set(data, to, v);
                    e.changed.push(format!("{file}:{from}->{to}"));
                }
                None => {
                    if !if_missing {
                        return Err(GovError::new(
                            "MIGRATION_FAILED",
                            format!("{file}: key {from} missing"),
                        ));
                    }
                    e.record["skipped"] = json!("missing");
                }
            }
        }
        "delete_overlay_key" => {
            let key = op["key"].as_str().unwrap_or("");
            if deep_delete(data, key) {
                e.changed.push(format!("{file}:-{key}"));
            }
        }
        "set_overlay_rule" => {
            // update fields of one element of a rule list (e.g. REPOSITORY_CONTRACT.paths[pattern=...]) — the
            // mechanism by which a tightened template default reaches already-adopted projects (verifier M-N3)
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
                e.record["skipped"] = json!(if found { "already_set" } else { "missing" });
            }
            e.changed = changed;
        }
        "sync_overlay_template" => {
            let base = op.get("base").filter(|b| b.is_object()).ok_or_else(|| {
                GovError::new(
                    "MIGRATION_FAILED",
                    format!("{file}: sync_overlay_template carries no `base` (the previous release's template, parsed)"),
                )
            })?;
            let tpl = templates.join(op["template"].as_str().unwrap_or(file));
            let target = read_yaml(&tpl).map_err(|err| {
                GovError::new(
                    "MIGRATION_FAILED",
                    format!(
                        "{file}: the installing kernel's template {} cannot be read: {err}",
                        tpl.display()
                    ),
                )
            })?;
            let mut sync = Sync::default();
            let merged =
                merge3(Some(base), Some(data), Some(&target), file, &mut sync).unwrap_or(json!({}));
            *data = merged;
            e.changed = sync.changed.iter().map(|c| format!("sync:{c}")).collect();
            e.record["changed"] = json!(sync.changed);
            e.record["base_release"] = op["base_release"].clone();
            if !sync.conflicts.is_empty() {
                e.record["conflicts"] = json!(sync.conflicts);
            }
            if sync.changed.is_empty() {
                e.record["skipped"] = json!("already_converged");
            }
            e.conflicts = sync
                .conflicts
                .into_iter()
                .map(|mut c| {
                    c["file"] = json!(file);
                    c
                })
                .collect();
        }
        other => {
            return Err(GovError::new(
                "MIGRATION_FAILED",
                format!("unknown overlay edit {other}"),
            ))
        }
    }
    Ok(e)
}

// ------------------------------------------------------------------ template convergence (`sync_overlay_template`)
//
// **Overlay-template changes reach installed projects through a migration operation (repair-1 r3, IP-R2-11).** A new
// installation takes the kernel's overlay templates as they are; an installed project got the previous release's
// templates and may have customised them. `sync_overlay_template` carries the previous release's template (`base`)
// and converges the project's file to the installing kernel's template by a three-way merge: what the project never
// changed follows the new template (values, rules added, rules removed, rule order); what the project customised is
// kept (a rule it added stays before the rule it preceded; one it appended stays last), and where the template changed
// the same thing too, the project's value is kept and the difference reported (`template_conflicts`), never silently
// dropped. An overlay that is still the base template becomes exactly the new template, so installed and new projects
// agree; [`check_substance`] verifies that for every release it builds. Template changes are delivered by this
// operation, declared in the migration record and shown by `gov update --check` before anything is applied.

#[derive(Debug, Default)]
struct Sync {
    changed: Vec<String>,
    conflicts: Vec<Value>,
}

/// A rule list's elements keyed by identity (`pattern`/`id`/`name`), or None when an element has no identity or two
/// share one (such a list is merged as a whole).
fn keyed(list: &[Value]) -> Option<Vec<(String, Value)>> {
    let mut out: Vec<(String, Value)> = vec![];
    for el in list {
        let k = rule_key(el)?;
        if out.iter().any(|(x, _)| x == &k) {
            return None;
        }
        out.push((k, el.clone()));
    }
    Some(out)
}

/// Three-way merge of one value: `b` the previous template, `p` the project's, `t` the new template (None = absent).
fn merge3(
    b: Option<&Value>,
    p: Option<&Value>,
    t: Option<&Value>,
    path: &str,
    s: &mut Sync,
) -> Option<Value> {
    // maps merge key by key
    if let (Some(Value::Object(pm)), Some(Value::Object(tm))) = (p, t) {
        if b.map(|x| x.is_object()).unwrap_or(true) {
            let bm = b.and_then(|x| x.as_object());
            let mut keys: Vec<String> = tm.keys().cloned().collect();
            for k in pm.keys().chain(bm.map(|m| m.keys()).into_iter().flatten()) {
                if !keys.contains(k) {
                    keys.push(k.clone());
                }
            }
            let mut out = serde_json::Map::new();
            for k in keys {
                if let Some(v) = merge3(
                    bm.and_then(|m| m.get(&k)),
                    pm.get(&k),
                    tm.get(&k),
                    &format!("{path}.{k}"),
                    s,
                ) {
                    out.insert(k, v);
                }
            }
            return Some(Value::Object(out));
        }
    }
    // rule lists merge rule by rule
    if let (Some(Value::Array(pa)), Some(Value::Array(ta))) = (p, t) {
        let bl = match b {
            Some(Value::Array(ba)) => keyed(ba),
            None => Some(vec![]),
            _ => None,
        };
        if let (Some(bl), Some(pl), Some(tl)) = (bl, keyed(pa), keyed(ta)) {
            return Some(Value::Array(merge_rules(&bl, &pl, &tl, path, s)));
        }
    }
    if p == b {
        if t != p {
            s.changed.push(path.to_string());
        }
        return t.cloned();
    }
    if t == b || p == t {
        return p.cloned();
    }
    s.conflicts.push(json!({"path": path, "kept": "project", "project": p, "previous_template": b, "new_template": t,
        "reason": "the project customised a value the new template also changed; the project's value is kept"}));
    p.cloned()
}

/// Three-way merge of a keyed rule list, including its order (rules are last-match, so order is meaning).
fn merge_rules(
    b: &[(String, Value)],
    p: &[(String, Value)],
    t: &[(String, Value)],
    path: &str,
    s: &mut Sync,
) -> Vec<Value> {
    fn get<'a>(l: &'a [(String, Value)], k: &str) -> Option<&'a Value> {
        l.iter().find(|(x, _)| x == k).map(|(_, v)| v)
    }
    let mut keys: Vec<String> = vec![];
    for (k, _) in t.iter().chain(p.iter()).chain(b.iter()) {
        if !keys.contains(k) {
            keys.push(k.clone());
        }
    }
    let mut res: Vec<(String, Value)> = vec![];
    for k in &keys {
        if let Some(v) = merge3(get(b, k), get(p, k), get(t, k), &format!("{path}[{k}]"), s) {
            res.push((k.clone(), v));
        }
    }
    let in_res = |k: &str| res.iter().any(|(x, _)| x == k);
    let base_order: Vec<&String> = b
        .iter()
        .map(|(k, _)| k)
        .filter(|k| get(p, k).is_some())
        .collect();
    let proj_order: Vec<&String> = p
        .iter()
        .map(|(k, _)| k)
        .filter(|k| get(b, k).is_some())
        .collect();
    let mut order: Vec<String>;
    if base_order == proj_order {
        // the project kept the template's order: the new template's order, with each rule the project added kept
        // right before the rule it preceded — a rule it appended stays last, so a project override still overrides
        order = t
            .iter()
            .map(|(k, _)| k.clone())
            .filter(|k| in_res(k))
            .collect();
        let mut anchor: Option<String> = None;
        for (k, _) in p.iter().rev() {
            if !in_res(k) {
                continue;
            }
            if !order.contains(k) {
                let pos = anchor
                    .as_ref()
                    .and_then(|a| order.iter().position(|x| x == a))
                    .unwrap_or(order.len());
                order.insert(pos, k.clone());
            }
            anchor = Some(k.clone());
        }
    } else {
        // the project reordered template rules: its order is kept; a rule new in the template goes right after the
        // rule it follows in the template
        order = p
            .iter()
            .map(|(k, _)| k.clone())
            .filter(|k| in_res(k))
            .collect();
        let mut prev: Option<String> = None;
        for (k, _) in t {
            if !in_res(k) {
                continue;
            }
            if !order.contains(k) {
                let pos = prev
                    .as_ref()
                    .and_then(|a| order.iter().position(|x| x == a))
                    .map(|i| i + 1)
                    .unwrap_or(0);
                order.insert(pos, k.clone());
            }
            prev = Some(k.clone());
        }
        if t.iter()
            .map(|(k, _)| k)
            .filter(|k| in_res(k))
            .ne(order.iter().filter(|k| get(t, k).is_some()))
        {
            s.conflicts.push(json!({"path": path, "kept": "project", "reason": "the project reordered the template's rules; its order is kept, so the new template's rule order is not applied"}));
        }
    }
    for (k, _) in &res {
        if !order.contains(k) {
            order.push(k.clone());
        }
    }
    let before: Vec<&String> = p.iter().map(|(k, _)| k).filter(|k| in_res(k)).collect();
    let after: Vec<&String> = order.iter().filter(|k| get(p, k).is_some()).collect();
    if before != after {
        s.changed.push(format!("{path}(order)"));
    }
    order
        .iter()
        .filter_map(|k| res.iter().find(|(x, _)| x == k).map(|(_, v)| v.clone()))
        .collect()
}

const OVERLAY_OPS: &[&str] = &[
    "add_overlay_file_from_template",
    "rename_overlay_file",
    "set_overlay_key",
    "rename_overlay_key",
    "delete_overlay_key",
    "set_overlay_rule",
    "sync_overlay_template",
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
///
/// **Delivery, not only declaration (repair-1 r3, IP-R2-11).** For every template file the migration delivers (an
/// overlay operation, or a `template_reconciliation` declaration), the check simulates `gov update` on a project whose
/// file is still the previous release's template — the migration's operations in order, then the template-default
/// reconciliation `gov update` performs — and requires the result to be exactly the new template: otherwise installed
/// projects and new installations would disagree about the same release. A `sync_overlay_template` operation must
/// carry, as its `base`, exactly the previous release's template. A declaration `not_applicable`, or one that names a
/// later migration (`op:<name> in M-…`, for a record whose operations are frozen as shipped), is not simulated here.
pub fn check_substance(
    migration: &Value,
    old_templates: &Path,
    new_templates: &Path,
) -> Vec<String> {
    let mut problems = vec![];
    let id = migration["id"].as_str().unwrap_or("?").to_string();
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
    let mut names: Vec<String> = rd
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().map(|e| e == "yaml").unwrap_or(false))
        .map(|nf| {
            nf.file_name()
                .map(|n| n.to_string_lossy().to_string())
                .unwrap_or_default()
        })
        .collect();
    names.sort();
    for name in &names {
        let nf = new_templates.join(name);
        let of = old_templates.join(name);
        let differs = !of.exists() || std::fs::read(&of).ok() != std::fs::read(&nf).ok();
        let covered_by_op = overlay_files_in_ops.iter().any(|f| f == name);
        let decl = declared.iter().find(|d| d["file"].as_str() == Some(name));
        if differs {
            match (covered_by_op, decl) {
                (true, _) => {}
                (false, Some(d)) => { let how = d["handled_by"].as_str().unwrap_or(""); if !(how == "template_reconciliation" || how.starts_with("op:") || how == "not_applicable") || d["reason"].as_str().unwrap_or("").is_empty() { problems.push(format!("{id}: overlay template {name} changed; overlay_template_changes entry must state handled_by (template_reconciliation | op:<name> | not_applicable) and a reason")); } }
                (false, None) => problems.push(format!("{id}: overlay template {name} changed between {} and {} but the migration has no overlay operation for it and does not declare it under overlay_template_changes", migration["from_version"], migration["to_version"])),
            }
        }
        // delivery: simulate `gov update` on an overlay that is still the previous release's template
        let how = decl.and_then(|d| d["handled_by"].as_str()).unwrap_or("");
        let delegated = how == "not_applicable" || how.contains(" in M-");
        let reconciled_only = !covered_by_op && how == "template_reconciliation";
        if !of.exists() || delegated || !(covered_by_op || (differs && reconciled_only)) {
            continue;
        }
        let (Ok(old), Ok(new)) = (read_yaml(&of), read_yaml(&nf)) else {
            problems.push(format!(
                "{id}: overlay template {name} cannot be parsed in the previous or the new payload"
            ));
            continue;
        };
        for o in ops.iter().filter(|o| {
            o["op"] == "sync_overlay_template" && o["file"].as_str() == Some(name.as_str())
        }) {
            if o["base"] != old {
                problems.push(format!("{id}: sync_overlay_template for {name} carries a base that is not the {} template (it must be the previous release's template exactly, parsed)", migration["from_version"]));
            }
        }
        match simulate_update(migration, name, &old, new_templates) {
            Ok(got) => {
                let diffs = differences(&got, &new, name);
                if !diffs.is_empty() {
                    problems.push(format!("{id}: an installed project whose {name} is the {} template does not converge to the {} template through this migration (installed and new projects would disagree): {}", migration["from_version"], migration["to_version"], diffs.into_iter().take(6).collect::<Vec<_>>().join("; ")));
                }
            }
            Err(e) => problems.push(format!(
                "{id}: simulating the migration on the {} template {name} fails: {}",
                migration["from_version"], e.message
            )),
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
        problems.push(format!("{id}: description claims an overlay/contract change but operations contain none and overlay_template_changes is absent"));
    }
    problems
}

/// What `gov update` does to overlay file `name` of a project whose copy is still `old` (the previous release's
/// template): the migration's operations on that file, in order, then the template-default reconciliation.
pub fn simulate_update(
    migration: &Value,
    name: &str,
    old: &Value,
    new_templates: &Path,
) -> Result<Value> {
    let mut doc = old.clone();
    for op in migration["operations"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        let kind = op["op"].as_str().unwrap_or("");
        if op["file"].as_str() != Some(name) {
            continue;
        }
        if kind == "add_overlay_file_from_template" {
            if !op["if_missing"].as_bool().unwrap_or(false) {
                doc = read_yaml(&new_templates.join(op["template"].as_str().unwrap_or(name)))?;
            }
            continue;
        }
        if EDIT_OPS.contains(&kind) {
            edit_overlay(kind, &op, name, &mut doc, new_templates)?;
        }
    }
    let new = read_yaml(&new_templates.join(name))?;
    let mut changed = vec![];
    reconcile_value(old, &new, &mut doc, name, &mut changed);
    Ok(doc)
}

/// Where two overlay documents differ (keyed rules by identity, then rule order), for a readable refusal.
fn differences(got: &Value, want: &Value, path: &str) -> Vec<String> {
    match (got, want) {
        (Value::Object(g), Value::Object(w)) => {
            let mut out = vec![];
            for (k, wv) in w {
                match g.get(k) {
                    Some(gv) => out.extend(differences(gv, wv, &format!("{path}.{k}"))),
                    None => out.push(format!("{path}.{k} missing")),
                }
            }
            for k in g.keys().filter(|k| !w.contains_key(*k)) {
                out.push(format!("{path}.{k} not in the template"));
            }
            out
        }
        (Value::Array(g), Value::Array(w)) => match (keyed(g), keyed(w)) {
            (Some(gk), Some(wk)) => {
                let mut out = vec![];
                for (k, wv) in &wk {
                    match gk.iter().find(|(x, _)| x == k) {
                        Some((_, gv)) => out.extend(differences(gv, wv, &format!("{path}[{k}]"))),
                        None => out.push(format!("{path}[{k}] missing")),
                    }
                }
                for (k, _) in gk.iter().filter(|(k, _)| !wk.iter().any(|(x, _)| x == k)) {
                    out.push(format!("{path}[{k}] not in the template"));
                }
                if out.is_empty() && gk.iter().map(|(k, _)| k).ne(wk.iter().map(|(k, _)| k)) {
                    out.push(format!("{path} rule order differs from the template's"));
                }
                out
            }
            _ if g != w => vec![format!("{path} differs")],
            _ => vec![],
        },
        _ if got != want => vec![format!("{path}: {got} (template: {want})")],
        _ => vec![],
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn canonical() -> std::path::PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR")).join("..")
    }

    fn scratch(tag: &str) -> std::path::PathBuf {
        let d = std::env::temp_dir().join(format!("gov-mig-{tag}-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    fn next_migration() -> Value {
        load_migrations(&canonical().join("migrations"))
            .into_iter()
            .find(|m| m["id"] == "M-4.1.5-4.1.6")
            .expect("M-4.1.5-4.1.6")
    }

    fn rule(pattern: &str, class: &str, extra: Value) -> Value {
        let mut r = json!({"pattern": pattern, "class": class});
        for (k, v) in extra.as_object().cloned().unwrap_or_default() {
            r[k] = v;
        }
        r
    }

    fn patterns(doc: &Value) -> Vec<String> {
        doc["paths"]
            .as_array()
            .unwrap()
            .iter()
            .map(|r| r["pattern"].as_str().unwrap().to_string())
            .collect()
    }

    /// A repository-contract template of the shape IP-R2-11 asks the next release to ship (WS-6 owns the real one):
    /// the specific `spec/` rules after `spec/**` so they decide their paths, the memory-quality evidence rule, the
    /// OS state directory and the registry location, and runtime-directory rules instead of a blanket `**`.
    fn next_contract(base: &Value) -> Value {
        let mut t = base.clone();
        let mut rules: Vec<Value> = base["paths"].as_array().unwrap().clone();
        let spec_all = rules
            .iter()
            .position(|r| r["pattern"] == "spec/**")
            .unwrap();
        let spec_rule = rules.remove(spec_all);
        let first_spec = rules
            .iter()
            .position(|r| r["pattern"].as_str().unwrap().starts_with("spec/"))
            .unwrap();
        rules.insert(first_spec, spec_rule);
        let reports = rules
            .iter()
            .position(|r| r["pattern"] == "spec/reports/**")
            .unwrap();
        rules.insert(reports + 1, rule("spec/reports/memory-quality/**", "evidence", json!({"semantic_index": false, "lexical_index": false, "graph_index": false, "code_index": false, "namespace": "spec"})));
        rules.retain(|r| r["pattern"] != ".governance-runtime/**");
        for p in [
            ".governance-runtime/state.db*",
            ".governance-runtime/context/**",
        ] {
            rules.push(rule(p, "derived", json!({"semantic_index": false, "lexical_index": false, "graph_index": false, "namespace": "runtime"})));
        }
        rules.push(rule(
            ".governance-state/**",
            "operational",
            json!({"namespace": "runtime"}),
        ));
        rules.push(rule(
            "governance/registry/**",
            "authoritative",
            json!({"mutation": "os-only", "namespace": "governance"}),
        ));
        let tests = rules
            .iter_mut()
            .find(|r| r["pattern"] == "governance/tests/**")
            .unwrap();
        tests["owner_role"] = json!("memory-verifier");
        t["paths"] = json!(rules);
        t
    }

    /// Repair-1 r3 (IP-R2-11; coordination with WS-8): the 4.1.5 → 4.1.6 migration is a valid record that converges
    /// **every** overlay file with the installing kernel's template from the exact 4.1.5 templates, so an installed
    /// project that never customised its overlay ends byte-identical to a new installation — whatever template changes
    /// the release carries — and the release substance check accepts it.
    #[test]
    fn the_next_migration_converges_every_overlay_template_from_the_4_1_5_templates() {
        let root = canonical();
        let m = next_migration();
        let reg = crate::schemas::SchemaRegistry::new(&root.join("framework/schemas"));
        assert!(reg.errors("migration", &m).unwrap().is_empty());
        assert_eq!(
            path(&load_migrations(&root.join("migrations")), "4.1.4", "4.1.6").len(),
            2
        );
        let old = root.join("release/releases/4.1.5/kernel/overlay-templates");
        let new = root.join("framework/overlay-templates");
        let mut names: Vec<String> = std::fs::read_dir(&new)
            .unwrap()
            .filter_map(|e| e.ok())
            .map(|e| e.file_name().to_string_lossy().to_string())
            .filter(|n| n.ends_with(".yaml"))
            .collect();
        names.sort();
        for n in &names {
            let op = m["operations"]
                .as_array()
                .unwrap()
                .iter()
                .find(|o| o["op"] == "sync_overlay_template" && o["file"] == n.as_str())
                .unwrap_or_else(|| panic!("no sync_overlay_template for {n}"));
            assert_eq!(
                op["base"],
                read_yaml(&old.join(n)).unwrap(),
                "{n}: base is the 4.1.5 template"
            );
        }
        assert_eq!(check_substance(&m, &old, &new), Vec::<String>::new());
        // a project whose overlay is still the 4.1.5 templates
        let dir = scratch("conv");
        let overlay = dir.join("governance/project");
        std::fs::create_dir_all(&overlay).unwrap();
        for n in &names {
            std::fs::copy(old.join(n), overlay.join(n)).unwrap();
        }
        let p = Project::open(&dir);
        let mut out = MigrationOutcome::default();
        apply(&p, &m, &root.join("framework"), false, &mut out).unwrap();
        assert!(out.index_rebuild && out.regenerate_adapters && out.notes.len() == 3);
        assert!(
            out.template_conflicts.is_empty(),
            "{:?}",
            out.template_conflicts
        );
        for n in &names {
            assert_eq!(
                read_yaml(&overlay.join(n)).unwrap(),
                read_yaml(&new.join(n)).unwrap(),
                "{n} converged"
            );
            if std::fs::read(old.join(n)).unwrap() != std::fs::read(new.join(n)).unwrap() {
                assert_eq!(
                    std::fs::read(overlay.join(n)).unwrap(),
                    std::fs::read(new.join(n)).unwrap(),
                    "{n}: byte-identical to a new installation"
                );
            }
        }
        let mut again = MigrationOutcome::default();
        apply(&p, &m, &root.join("framework"), false, &mut again).unwrap();
        assert!(
            again.overlay_keys_changed.is_empty(),
            "{:?}",
            again.overlay_keys_changed
        );
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// The convergence is a three-way merge: an untouched overlay becomes exactly the new template (rules added,
    /// removed and re-ordered — last-match order is meaning); a customised one keeps every customisation, keeps the
    /// rules the project added next to the rule they followed, and reports (never drops) a customisation the template
    /// also changed. The repository contract that results decides paths as each side intended.
    #[test]
    fn template_convergence_is_a_three_way_merge_that_keeps_customisations() {
        let base = read_yaml(
            &canonical()
                .join("release/releases/4.1.5/kernel/overlay-templates/REPOSITORY_CONTRACT.yaml"),
        )
        .unwrap();
        let target = next_contract(&base);
        let tdir = scratch("tpl");
        write_yaml(&tdir.join("REPOSITORY_CONTRACT.yaml"), &target).unwrap();
        let op = json!({"op": "sync_overlay_template", "file": "REPOSITORY_CONTRACT.yaml", "base_release": "4.1.5", "base": base});
        // untouched: exactly the new template, order included
        let mut untouched = base.clone();
        let e = edit_overlay(
            "sync_overlay_template",
            &op,
            "REPOSITORY_CONTRACT.yaml",
            &mut untouched,
            &tdir,
        )
        .unwrap();
        assert_eq!(untouched, target);
        assert!(e.conflicts.is_empty());
        assert!(
            e.changed.iter().any(|c| c.contains("(order)")),
            "{:?}",
            e.changed
        );
        // customised the way `adopt` and a project do
        let mut proj = base.clone();
        {
            let rules = proj["paths"].as_array_mut().unwrap();
            rules.insert(0, rule("src/**", "source", json!({"code_index": true})));
            rules.push(rule("config/secrets.yaml", "secret", json!({})));
            rules.retain(|r| r["pattern"] != "spec/experiments/**");
            for r in rules.iter_mut() {
                if r["pattern"] == "archive/**" {
                    r["default_retrieval"] = json!(true);
                }
                if r["pattern"] == "governance/tests/**" {
                    r["owner_role"] = json!("test-execution-agent");
                }
            }
        }
        let e = edit_overlay(
            "sync_overlay_template",
            &op,
            "REPOSITORY_CONTRACT.yaml",
            &mut proj,
            &tdir,
        )
        .unwrap();
        let got = patterns(&proj);
        assert_eq!(got[0], "src/**", "a rule the project put first stays first");
        assert_eq!(got.last().unwrap(), "config/secrets.yaml", "{got:?}");
        assert!(
            !got.contains(&"spec/experiments/**".to_string()),
            "a rule the project deleted stays deleted"
        );
        assert!(
            !got.contains(&".governance-runtime/**".to_string()),
            "the untouched blanket rule the template removed is removed"
        );
        for p in [
            "spec/reports/memory-quality/**",
            ".governance-state/**",
            "governance/registry/**",
            ".governance-runtime/state.db*",
        ] {
            assert!(got.contains(&p.to_string()), "{p} delivered: {got:?}");
        }
        let pos = |p: &str| got.iter().position(|x| x == p).unwrap();
        assert!(
            pos("spec/**") < pos("spec/reports/**")
                && pos("spec/reports/**") < pos("spec/reports/memory-quality/**")
        );
        let archive = proj["paths"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["pattern"] == "archive/**")
            .unwrap();
        assert_eq!(archive["default_retrieval"], true, "customisation kept");
        let tests = proj["paths"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["pattern"] == "governance/tests/**")
            .unwrap();
        assert_eq!(
            tests["owner_role"], "test-execution-agent",
            "both changed: the project's value is kept"
        );
        assert_eq!(e.conflicts.len(), 1, "{:?}", e.conflicts);
        assert_eq!(
            e.conflicts[0]["path"],
            "REPOSITORY_CONTRACT.yaml.paths[pattern=governance/tests/**].owner_role"
        );
        assert_eq!(e.conflicts[0]["new_template"], "memory-verifier");
        let c = crate::paths::RepositoryContract::new(proj.clone());
        let d = c.decide("spec/reports/memory-quality/FAIL-0001.yaml");
        assert_eq!(d.class(), "evidence");
        assert!(!d.flag("semantic_index") && !d.flag("lexical_index"));
        assert_eq!(
            c.decide("spec/reports/weekly.md").class(),
            "evidence",
            "specific spec rules decide their paths"
        );
        assert_eq!(c.decide("src/app.py").class(), "source");
        assert!(c.decide("config/secrets.yaml").is_secret());
        assert_eq!(c.decide(".governance-runtime/state.db").class(), "derived");
        // a project that reordered template rules keeps its order; the new rules still arrive
        let mut reordered = base.clone();
        reordered["paths"].as_array_mut().unwrap().swap(0, 1);
        let e = edit_overlay(
            "sync_overlay_template",
            &op,
            "REPOSITORY_CONTRACT.yaml",
            &mut reordered,
            &tdir,
        )
        .unwrap();
        let got = patterns(&reordered);
        assert_eq!(
            &got[..2],
            &[
                "governance/project/**".to_string(),
                "governance/kernel/**".to_string()
            ]
        );
        assert!(got.contains(&"spec/reports/memory-quality/**".to_string()));
        assert!(e
            .conflicts
            .iter()
            .any(|c| c["reason"].as_str().unwrap().contains("reordered")));
        let _ = std::fs::remove_dir_all(&tdir);
    }

    /// The substance check requires delivery, not only a declaration: a declared reconciliation that cannot add a rule,
    /// or an appended rule the template placed elsewhere (last-match order is meaning), is refused; the three-way
    /// convergence from the exact previous template is accepted, and a wrong base is refused.
    #[test]
    fn the_substance_check_simulates_the_update_an_installed_project_receives() {
        let base = read_yaml(
            &canonical()
                .join("release/releases/4.1.5/kernel/overlay-templates/REPOSITORY_CONTRACT.yaml"),
        )
        .unwrap();
        let (old, new) = (scratch("old"), scratch("new"));
        write_yaml(&old.join("REPOSITORY_CONTRACT.yaml"), &base).unwrap();
        write_yaml(&new.join("REPOSITORY_CONTRACT.yaml"), &next_contract(&base)).unwrap();
        let mig = |ops: Value, decl: Value| json!({"id": "M-x", "from_version": "4.1.5", "to_version": "4.1.6", "description": "d", "operations": ops, "overlay_template_changes": decl});
        let declared_only = mig(
            json!([]),
            json!([{"file": "REPOSITORY_CONTRACT.yaml", "handled_by": "template_reconciliation", "reason": "defaults follow"}]),
        );
        let p = check_substance(&declared_only, &old, &new);
        assert!(p.iter().any(|x| x.contains("does not converge")), "{p:?}");
        let appended = mig(
            json!([{"op": "set_overlay_rule", "file": "REPOSITORY_CONTRACT.yaml", "list_key": "paths", "match": {"pattern": "spec/reports/memory-quality/**"}, "set": {"class": "evidence"}, "add_if_missing": true}]),
            json!([]),
        );
        assert!(check_substance(&appended, &old, &new)
            .iter()
            .any(|x| x.contains("does not converge")));
        let sync = mig(
            json!([{"op": "sync_overlay_template", "file": "REPOSITORY_CONTRACT.yaml", "base_release": "4.1.5", "base": base}]),
            json!([]),
        );
        assert_eq!(check_substance(&sync, &old, &new), Vec::<String>::new());
        let mut wrong = base.clone();
        wrong["paths"].as_array_mut().unwrap().pop();
        let bad_base = mig(
            json!([{"op": "sync_overlay_template", "file": "REPOSITORY_CONTRACT.yaml", "base": wrong}]),
            json!([]),
        );
        assert!(check_substance(&bad_base, &old, &new)
            .iter()
            .any(|x| x.contains("carries a base")));
        let _ = (std::fs::remove_dir_all(&old), std::fs::remove_dir_all(&new));
    }

    /// Dry runs (`gov update --check`) report what the convergence would change without writing; a project without
    /// the overlay file is left to `add_overlay_file_from_template`.
    /// WS-7 IP-W7R3-5 / WS-6 IP-R3-WS06-7 (round 4, P2-AR-0043): `relocate_os_stores` moves the tracked OS stores an
    /// earlier release kept in the generated views, bytes unchanged; a dry run reports and writes nothing; a second
    /// run moves nothing; a machine-local store is refused (its writer moves it under its own lock).
    #[test]
    fn relocate_os_stores_moves_tracked_stores_bytes_unchanged_and_only_them() {
        let dir = scratch("relocate");
        let kdir = scratch("relocate-kernel");
        let (reg, bind) = (
            "governance/generated/plugin-registry.json",
            "governance/generated/skill-bindings.json",
        );
        std::fs::create_dir_all(dir.join("governance/generated")).unwrap();
        std::fs::write(
            dir.join(reg),
            "{\"plugins\": {\"x\": {\"os_binding\": \"kept as is\"}}}",
        )
        .unwrap();
        std::fs::write(dir.join(bind), "{\"versions\": {}}").unwrap();
        let (rb, bb) = (
            std::fs::read(dir.join(reg)).unwrap(),
            std::fs::read(dir.join(bind)).unwrap(),
        );
        let p = Project::open(&dir);
        let m = json!({"id": "M-x", "operations": [{"op": "relocate_os_stores"}]});
        let mut out = MigrationOutcome::default();
        apply(&p, &m, &kdir, true, &mut out).unwrap();
        assert_eq!(
            out.applied[0]["moved"].as_array().unwrap().len(),
            2,
            "{:?}",
            out.applied
        );
        assert!(
            dir.join(reg).exists() && dir.join(bind).exists(),
            "a dry run moves nothing"
        );
        let mut out = MigrationOutcome::default();
        apply(&p, &m, &kdir, false, &mut out).unwrap();
        assert!(!dir.join(reg).exists() && !dir.join(bind).exists());
        assert_eq!(
            std::fs::read(dir.join(crate::paths::PLUGIN_REGISTRY_PATH)).unwrap(),
            rb
        );
        assert_eq!(
            std::fs::read(dir.join(crate::paths::SKILL_BINDINGS_PATH)).unwrap(),
            bb
        );
        let mut out = MigrationOutcome::default();
        apply(&p, &m, &kdir, false, &mut out).unwrap();
        assert_eq!(out.applied[0]["moved"], json!([]), "idempotent");
        let local = json!({"id": "M-y", "operations": [{"op": "relocate_os_stores", "stores": ["claims"]}]});
        let e = apply(&p, &local, &kdir, false, &mut MigrationOutcome::default()).unwrap_err();
        assert_eq!(e.code, "MIGRATION_FAILED");
        let _ = (
            std::fs::remove_dir_all(&dir),
            std::fs::remove_dir_all(&kdir),
        );
    }

    #[test]
    fn template_convergence_dry_run_writes_nothing() {
        let base = read_yaml(
            &canonical()
                .join("release/releases/4.1.5/kernel/overlay-templates/REPOSITORY_CONTRACT.yaml"),
        )
        .unwrap();
        let kdir = scratch("kernel");
        std::fs::create_dir_all(kdir.join("overlay-templates")).unwrap();
        write_yaml(
            &kdir.join("overlay-templates/REPOSITORY_CONTRACT.yaml"),
            &next_contract(&base),
        )
        .unwrap();
        let dir = scratch("dry");
        std::fs::create_dir_all(dir.join("governance/project")).unwrap();
        write_yaml(
            &dir.join("governance/project/REPOSITORY_CONTRACT.yaml"),
            &base,
        )
        .unwrap();
        let bytes = std::fs::read(dir.join("governance/project/REPOSITORY_CONTRACT.yaml")).unwrap();
        let m = json!({"id": "M-x", "operations": [
            {"op": "sync_overlay_template", "file": "REPOSITORY_CONTRACT.yaml", "base": base},
            {"op": "sync_overlay_template", "file": "DATA_SENSITIVITY.yaml", "base": {"schema_version": "1.0.0"}}]});
        let p = Project::open(&dir);
        let mut out = MigrationOutcome::default();
        apply(&p, &m, &kdir, true, &mut out).unwrap();
        assert!(!out.overlay_keys_changed.is_empty());
        assert_eq!(
            std::fs::read(dir.join("governance/project/REPOSITORY_CONTRACT.yaml")).unwrap(),
            bytes
        );
        assert_eq!(out.applied[1]["skipped"], "overlay file missing");
        let _ = (
            std::fs::remove_dir_all(&kdir),
            std::fs::remove_dir_all(&dir),
        );
    }
}
