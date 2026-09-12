//! Model/provider adapters (framework §22, §4): generated projections of kernel + overlay. Conformance = every hard
//! invariant statement reproduced verbatim; manifest ties outputs to kernel/overlay hashes.
use crate::util::{hash_value, now_iso, read_json, read_text, read_yaml, sha256_file, write_json, write_text};
use crate::{Project, Result, FRAMEWORK_NAME};
use serde_json::{json, Value};

fn invariants(p: &Project) -> Vec<Value> {
    read_yaml(&p.kernel_dir().join("constitution").join("HARD_INVARIANTS.yaml")).ok().and_then(|v| v["invariants"].as_array().cloned()).unwrap_or_default()
}

pub fn generate(p: &Project) -> Result<Value> {
    let inv = invariants(p);
    let pol = p.policies();
    let precedence = pol.get_list("AUTHORITY_POLICY", "precedence");
    let triggers = pol.get_list("CHECKPOINT_POLICY", "mandatory_triggers");
    let secret_patterns = pol.get_list("SECURITY_POLICY", "secret_path_patterns");
    let roles = read_yaml(&p.kernel_dir().join("roles").join("ROLES.yaml")).unwrap_or(json!({}));
    let commands = read_yaml(&p.kernel_dir().join("commands").join("COMMAND_CONTRACT.yaml")).unwrap_or(json!({}));
    let registry = read_json(&p.generated_dir().join("tool-registry.json")).unwrap_or(json!({"mcp_servers": [], "role_exposure": {}}));
    let inv_md: String = inv.iter().map(|i| format!("- {}: {}", i["id"].as_str().unwrap_or(""), i["statement"].as_str().unwrap_or(""))).collect::<Vec<_>>().join("\n");
    let prec_md: String = precedence.iter().enumerate().map(|(i, x)| format!("{}. {}", i + 1, x.replace('_', " "))).collect::<Vec<_>>().join("\n");
    let roles_md: String = roles["roles"].as_array().map(|a| a.iter().map(|r| format!("- {} ({}, {}, min tier {})", r["id"].as_str().unwrap_or(""), r["name"].as_str().unwrap_or(""), r["level"].as_str().unwrap_or(""), r["minimum_tier"].as_str().unwrap_or(""))).collect::<Vec<_>>().join("\n")).unwrap_or_default();
    let cmds_md: String = commands["human_surface"].as_array().map(|a| a.iter().map(|c| format!("- gov {}: {}", c["command"].as_str().unwrap_or(""), c["description"].as_str().unwrap_or(""))).collect::<Vec<_>>().join("\n")).unwrap_or_default();
    let subs: Vec<(&str, String)> = vec![
        ("{{framework}}", FRAMEWORK_NAME.into()), ("{{version}}", p.framework_version()), ("{{project_name}}", p.project_name()),
        ("{{invariants}}", inv_md), ("{{invariants_json}}", serde_json::to_string(&inv)?), ("{{precedence}}", prec_md), ("{{precedence_json}}", serde_json::to_string(&precedence)?),
        ("{{checkpoint_triggers}}", triggers.join(", ")), ("{{secret_patterns}}", secret_patterns.join(", ")), ("{{secret_patterns_json}}", serde_json::to_string(&secret_patterns)?),
        ("{{roles}}", roles_md), ("{{roles_json}}", serde_json::to_string(&roles["roles"])?), ("{{commands}}", cmds_md), ("{{commands_json}}", serde_json::to_string(&commands["human_surface"])?),
        ("{{mcp_servers_json}}", serde_json::to_string(&registry["mcp_servers"])?), ("{{mcp_role_exposure_json}}", serde_json::to_string(&registry["role_exposure"])?),
    ];
    let adir = p.kernel_dir().join("adapters");
    let mut outputs = serde_json::Map::new();
    let mut names: Vec<_> = std::fs::read_dir(&adir).map(|rd| rd.filter_map(|e| e.ok()).map(|e| e.path()).filter(|x| x.is_dir()).collect()).unwrap_or_default();
    names.sort();
    for dir in names {
        let Ok(meta) = read_yaml(&dir.join("adapter.yaml")) else { continue };
        let id = meta["id"].as_str().unwrap_or("").to_string();
        let tpl = read_text(&dir.join(meta["template"].as_str().unwrap_or("template.md")))?;
        let mut out = tpl;
        for (k, v) in &subs { out = out.replace(k, v); }
        let rel = meta["output"].as_str().unwrap_or("").to_string();
        write_text(&p.root.join(&rel), &out)?;
        if meta["format"].as_str() == Some("json") { serde_json::from_str::<Value>(&out).map_err(|e| crate::GovError::new("ADAPTER_INVALID_JSON", format!("{id}: {e}")))?; }
        outputs.insert(id, json!({"version": meta["version"].as_str().unwrap_or("0"), "output": rel, "hash": crate::util::sha256_text(&out)}));
    }
    let manifest = json!({"kernel_hash": p.lock()?["kernel_manifest_hash"], "overlay_hash": p.overlay().hash(), "adapters": outputs, "invariants_hash": hash_value(&json!(inv)), "generated_at": now_iso()});
    write_json(&p.generated_dir().join("adapter-manifest.json"), &manifest)?;
    // framework.json (derived path-map projection at the repo root)
    write_json(&p.root.join("framework.json"), &p.contract().to_framework_json(FRAMEWORK_NAME, &p.framework_version()))?;
    Ok(manifest)
}

/// Conformance: outputs exist, hashes match, every invariant statement appears verbatim, manifest not stale.
pub fn verify(p: &Project) -> Result<Value> {
    let mut problems = vec![];
    let inv = invariants(p);
    let Ok(m) = read_json(&p.generated_dir().join("adapter-manifest.json")) else { return Ok(json!({"ok": false, "problems": ["adapter-manifest.json missing; run gov adapters generate"]})) };
    if m["kernel_hash"] != p.lock()?["kernel_manifest_hash"] { problems.push("adapter manifest kernel_hash differs from framework.lock (stale adapters)".to_string()); }
    if m["overlay_hash"].as_str() != Some(&p.overlay().hash()) { problems.push("adapter manifest overlay_hash differs from current overlay (stale adapters)".to_string()); }
    if m["invariants_hash"] != hash_value(&json!(inv)) { problems.push("adapter manifest invariants_hash differs from kernel invariants".to_string()); }
    let mut checked = 0;
    for (id, a) in m["adapters"].as_object().cloned().unwrap_or_default() {
        let rel = a["output"].as_str().unwrap_or("");
        let path = p.root.join(rel);
        if !path.exists() { problems.push(format!("{id}: output {rel} missing")); continue; }
        if sha256_file(&path)? != a["hash"].as_str().unwrap_or("") { problems.push(format!("{id}: output {rel} modified since generation")); }
        let text = read_text(&path)?;
        for i in &inv { let st = i["statement"].as_str().unwrap_or(""); if !text.contains(st) { problems.push(format!("{id}: missing invariant {} verbatim", i["id"].as_str().unwrap_or(""))); } }
        checked += 1;
    }
    let fj = p.root.join("framework.json");
    if !fj.exists() { problems.push("framework.json missing".into()); } else if read_json(&fj)? != p.contract().to_framework_json(FRAMEWORK_NAME, &p.framework_version()) { problems.push("framework.json out of sync with REPOSITORY_CONTRACT.yaml".into()); }
    Ok(json!({"ok": problems.is_empty(), "adapters_checked": checked, "invariants": inv.len(), "problems": problems}))
}
