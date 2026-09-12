//! Policy enforcement coverage: every declared kernel policy key must be either enforced by a named executable path
//! or explicitly classified as informational in ENFORCEMENT_MAP.yaml. "Declared but does nothing" is a finding.
use crate::util::read_yaml;
use crate::{Project, Result};
use serde_json::{json, Value};
use std::collections::BTreeSet;

fn flatten(prefix: &str, v: &Value, out: &mut BTreeSet<String>) {
    match v {
        Value::Object(m) => { for (k, x) in m { let key = if prefix.is_empty() { k.clone() } else { format!("{prefix}.{k}") }; if x.is_object() && !x.as_object().unwrap().is_empty() { flatten(&key, x, out); } else { out.insert(key); } } }
        _ => { if !prefix.is_empty() { out.insert(prefix.to_string()); } }
    }
}

fn covered(key: &str, entries: &[(String, Value)]) -> Option<Value> {
    for (k, v) in entries {
        if k == key { return Some(v.clone()); }
        if let Some(pre) = k.strip_suffix(".*") { if key.starts_with(&format!("{pre}.")) { return Some(v.clone()); } }
    }
    None
}

pub fn report(p: &Project) -> Result<Value> {
    let map = read_yaml(&p.kernel_dir().join("policies").join("ENFORCEMENT_MAP.yaml"))?;
    let entries: Vec<(String, Value)> = map.get("keys").and_then(|k| k.as_object()).map(|o| o.iter().map(|(k, v)| (k.clone(), v.clone())).collect()).unwrap_or_default();
    let mut uncovered = vec![]; let mut enforced = 0; let mut informational = 0; let mut total = 0;
    let mut unknown_entries: Vec<String> = entries.iter().map(|(k, _)| k.clone()).collect();
    for name in crate::policy::POLICY_NAMES {
        let Ok(pol) = read_yaml(&p.kernel_dir().join("policies").join(format!("{name}.yaml"))) else { continue };
        let mut keys = BTreeSet::new();
        flatten("", &pol, &mut keys);
        for k in keys {
            if k == "policy" || k == "version" { continue; }
            total += 1;
            let full = format!("{name}.{k}");
            match covered(&full, &entries) {
                Some(e) => { if e.get("enforced_by").is_some() { enforced += 1; } else { informational += 1; } unknown_entries.retain(|x| x != &full && !(x.ends_with(".*") && full.starts_with(&x[..x.len() - 1]))); }
                None => uncovered.push(full),
            }
        }
    }
    Ok(json!({"total_keys": total, "enforced": enforced, "informational": informational, "uncovered": uncovered, "map_entries_without_policy_key": unknown_entries, "ok": uncovered.is_empty()}))
}

/// Every `enforced_by` function name in the map (for the builder test that greps the source tree).
pub fn enforced_functions(map: &Value) -> Vec<String> {
    let mut v: Vec<String> = map.get("keys").and_then(|k| k.as_object()).map(|o| o.values().flat_map(|e| e.get("enforced_by").and_then(|x| x.as_array()).cloned().unwrap_or_default()).filter_map(|f| f.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
    v.sort(); v.dedup(); v
}
