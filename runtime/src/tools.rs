//! Tool/MCP capability registry and permissions (framework §28-32). Exposure is role/task scoped; least authority.
use crate::orchestration::gates;
use crate::util::{now_iso, read_yaml, write_json};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub fn kernel_tools(p: &Project) -> Vec<Value> {
    let path = p.kernel_dir().join("tools").join("registry").join("TOOLS.yaml");
    read_yaml(&path).ok().and_then(|v| v["tools"].as_array().cloned()).unwrap_or_default()
}
pub fn project_tools(p: &Project) -> Vec<Value> {
    let dir = p.overlay_dir().join("tools");
    let Ok(rd) = std::fs::read_dir(&dir) else { return vec![] };
    let mut paths: Vec<_> = rd.filter_map(|e| e.ok()).map(|e| e.path()).filter(|x| x.extension().map(|e| e == "yaml").unwrap_or(false)).collect();
    paths.sort();
    paths.into_iter().filter_map(|x| read_yaml(&x).ok()).collect()
}
pub fn mcp_servers(p: &Project) -> Vec<Value> {
    let mut out = read_yaml(&p.kernel_dir().join("tools").join("mcp").join("registry.yaml")).ok().and_then(|v| v["servers"].as_array().cloned()).unwrap_or_default();
    if let Ok(v) = read_yaml(&p.overlay_dir().join("mcp").join("registry.yaml")) { out.extend(v["servers"].as_array().cloned().unwrap_or_default()); }
    out
}

pub fn role_permissions(p: &Project, role: &str) -> Vec<String> {
    p.overlay().get("TOOL_PERMISSIONS.yaml").get("roles").and_then(|r| r.get(role)).and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default()
}

fn role_allowed(tool: &Value, role: &str, perms: &[String]) -> bool {
    let approved = tool["approved_roles"].as_array().map(|a| a.iter().any(|r| r.as_str() == Some(role) || r.as_str() == Some("all"))).unwrap_or(false);
    let required: Vec<String> = tool["required_permission_classes"].as_array().map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
    approved && required.iter().all(|r| perms.contains(r))
}

/// Compile governance/generated/tool-registry.json (kernel + project tools, MCP servers, per-role exposure).
pub fn generate_registry(p: &Project) -> Result<Value> {
    let mut tools = kernel_tools(p); tools.extend(project_tools(p));
    let servers = mcp_servers(p);
    let perms_all = p.overlay().get("TOOL_PERMISSIONS.yaml");
    let mut exposure = serde_json::Map::new();
    if let Some(roles) = perms_all.get("roles").and_then(|r| r.as_object()) {
        for (role, _) in roles {
            let perms = role_permissions(p, role);
            let allow: Vec<String> = perms_all.get("tool_allowlist").and_then(|a| a.get(role)).and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
            let mcp_allow: Vec<String> = perms_all.get("mcp_servers").and_then(|a| a.get(role)).and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
            let t: Vec<String> = tools.iter().filter(|t| t["status"].as_str() == Some("active") && role_allowed(t, role, &perms) && (allow.is_empty() || allow.iter().any(|a| Some(a.as_str()) == t["tool_id"].as_str()))).filter_map(|t| t["tool_id"].as_str().map(|s| s.to_string())).collect();
            let m: Vec<String> = servers.iter().filter(|s| s["status"].as_str() == Some("active") && role_allowed(s, role, &perms) && (mcp_allow.is_empty() || mcp_allow.iter().any(|a| Some(a.as_str()) == s["id"].as_str()))).filter_map(|s| s["id"].as_str().map(|x| x.to_string())).collect();
            exposure.insert(role.clone(), json!({"permissions": perms, "tools": t, "mcp_servers": m}));
        }
    }
    let reg = json!({"generated_from": {"kernel": p.lock().map(|l| l["kernel_manifest_hash"].clone()).unwrap_or(Value::Null), "overlay": p.overlay().hash(), "generated_at": now_iso()}, "tools": tools, "mcp_servers": servers, "role_exposure": exposure});
    write_json(&p.generated_dir().join("tool-registry.json"), &reg)?;
    Ok(reg)
}

pub fn resolve(p: &Project, role: &str, capability: &str) -> Result<Value> {
    let perms = role_permissions(p, role);
    let mut tools = kernel_tools(p); tools.extend(project_tools(p));
    let matches: Vec<Value> = tools.iter().filter(|t| t["capabilities"].as_array().map(|a| a.iter().any(|c| c.as_str() == Some(capability))).unwrap_or(false)).cloned().collect();
    let usable: Vec<Value> = matches.iter().filter(|t| t["status"].as_str() == Some("active") && role_allowed(t, role, &perms)).map(|t| json!({"tool_id": t["tool_id"], "name": t["name"], "type": t["type"], "version": t["version"]})).collect();
    let mcp: Vec<Value> = mcp_servers(p).into_iter().filter(|s| s["capabilities"].as_array().map(|a| a.iter().any(|c| c.as_str() == Some(capability))).unwrap_or(false) && s["status"].as_str() == Some("active") && role_allowed(s, role, &perms)).map(|s| json!({"mcp_id": s["id"], "name": s["name"]})).collect();
    let gap = usable.is_empty() && mcp.is_empty();
    let reason = if gap { if matches.is_empty() { "no registered tool provides this capability" } else if matches.iter().any(|t| t["status"].as_str() != Some("active")) { "a tool exists but is not active (proposed/deprecated)" } else { "role lacks approval or permission classes for the available tool" } } else { "" };
    Ok(json!({"role": role, "capability": capability, "tools": usable, "mcp_servers": mcp, "capability_gap": gap, "reason": reason, "next": if gap { "gov tools install --descriptor <file> (checks TOOL_POLICY auto-install conditions) or raise a tooling task" } else { "" }}))
}

/// Install/register a tool only when every TOOL_POLICY auto-install condition holds; otherwise raise a Human Decision Gate.
pub fn install(p: &Project, descriptor: Value, role: &str, execute: bool) -> Result<Value> {
    crate::orchestration::control::guard_write(p, "tools install")?;
    let pol = p.policies();
    let install_roles: Vec<String> = p.overlay().get("TOOL_PERMISSIONS.yaml").get("install_authority_roles").and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
    let approved_licences = pol.get_list("TOOL_POLICY", "approved_licences");
    let max_cost = pol.get_f64("BUDGET_POLICY", "defaults.max_install_cost_usd", 0.0);
    let tool_id = descriptor["tool_id"].as_str().unwrap_or("").to_string();
    if tool_id.is_empty() { return Err(GovError::new("USAGE", "descriptor requires tool_id")); }
    let mut checks = vec![];
    let mut push = |name: &str, ok: bool, detail: String| checks.push(json!({"condition": name, "ok": ok, "detail": detail}));
    push("role_has_install_authority", install_roles.iter().any(|r| r == role), format!("role {role}; install roles {install_roles:?}"));
    push("installation_reversible", descriptor["reversible"].as_bool().unwrap_or(false), "descriptor.reversible".into());
    let cost = descriptor["cost_usd"].as_f64().unwrap_or(0.0);
    push("cost_within_budget", cost <= max_cost, format!("cost {cost} <= {max_cost}"));
    let req: Vec<String> = descriptor["required_permission_classes"].as_array().map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
    let perms = role_permissions(p, role);
    push("no_privilege_escalation", req.iter().all(|r| perms.contains(r)) && !req.iter().any(|r| r == "SYSTEM_INSTALL" || r == "SECRET_READ" || r == "DEPLOY_PRODUCTION"), format!("required {req:?} within role permissions {perms:?}"));
    let lic = descriptor["license"].as_str().unwrap_or("").to_string();
    push("licence_and_security_satisfied", approved_licences.contains(&lic) && descriptor["security_review"].as_str().map(|s| s == "passed").unwrap_or(false), format!("license {lic}; security_review {}", descriptor["security_review"]));
    push("version_pinned_and_recorded", descriptor["version_pin"].as_str().map(|s| !s.is_empty()).unwrap_or(false), "descriptor.version_pin".into());
    push("tool_registered", true, "will be registered under governance/project/tools/".into());
    push("environment_reproducible", descriptor["install_command"].as_array().map(|a| !a.is_empty()).unwrap_or(false) && descriptor["uninstall_command"].as_array().map(|a| !a.is_empty()).unwrap_or(false), "install and uninstall commands declared".into());
    let all_ok = checks.iter().all(|c| c["ok"].as_bool().unwrap_or(false));
    if !all_ok {
        let failed: Vec<String> = checks.iter().filter(|c| !c["ok"].as_bool().unwrap_or(false)).map(|c| c["condition"].as_str().unwrap_or("").to_string()).collect();
        let gate = gates::create(p, json!({"question": format!("Approve installation of tool {tool_id}? Automatic installation conditions failed: {}", failed.join(", ")), "why_now": "a task requires a capability that is not available", "current_state": "tool not installed", "options": [{"id": "A", "description": "approve installation as described"}, {"id": "B", "description": "reject; find an alternative"}], "impact": "adds an executable capability to the environment", "reversibility": if descriptor["reversible"].as_bool().unwrap_or(false) { "reversible" } else { "irreversible or unknown" }, "recommendation": "B unless the tool is essential", "confidence": 0.6, "trigger": "tool_install", "impact_radius": "R2"}))?;
        return Ok(json!({"installed": false, "human_gate": gate["id"], "checks": checks}));
    }
    let mut desc = descriptor.clone();
    desc["status"] = json!("active"); desc["installed_by"] = json!(p.session_id); desc["installed_at"] = json!(now_iso());
    desc["type"] = desc.get("type").cloned().unwrap_or(json!("library"));
    desc["approved_roles"] = desc.get("approved_roles").cloned().unwrap_or(json!([role]));
    desc["capabilities"] = desc.get("capabilities").cloned().unwrap_or(json!([]));
    desc["name"] = desc.get("name").cloned().unwrap_or(json!(tool_id));
    let mut exec_result = Value::Null;
    if execute {
        let cmd: Vec<String> = desc["install_command"].as_array().unwrap().iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect();
        let (code, out, err) = crate::util::run_cmd(&cmd, &p.root)?;
        exec_result = json!({"exit": code, "stdout": out.chars().take(2000).collect::<String>(), "stderr": err.chars().take(2000).collect::<String>()});
        if code != 0 { return Err(GovError::new("INSTALL_FAILED", format!("install command failed ({code})")).with_details(exec_result)); }
    }
    p.schemas().validate("tool", &desc, &format!("({tool_id})"))?;
    crate::util::write_yaml(&p.overlay_dir().join("tools").join(format!("{tool_id}.yaml")), &desc)?;
    let health = health_one(p, &desc);
    generate_registry(p)?;
    Ok(json!({"installed": true, "tool_id": tool_id, "checks": checks, "executed": execute, "exec_result": exec_result, "health": health, "registered_at": format!("governance/project/tools/{tool_id}.yaml")}))
}

pub fn health_one(p: &Project, tool: &Value) -> Value {
    let hc = &tool["health_check"];
    match hc["kind"].as_str().unwrap_or("none") {
        "builtin" => json!({"tool_id": tool["tool_id"], "ok": true, "kind": "builtin"}),
        "command" => {
            let cmd: Vec<String> = hc["command"].as_array().map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
            let expect = hc["expect_exit"].as_i64().unwrap_or(0) as i32;
            match crate::util::run_cmd(&cmd, &p.root) { Ok((code, _, err)) => json!({"tool_id": tool["tool_id"], "ok": code == expect, "kind": "command", "exit": code, "stderr": err.chars().take(200).collect::<String>()}), Err(e) => json!({"tool_id": tool["tool_id"], "ok": false, "error": e.to_string()}) }
        }
        _ => json!({"tool_id": tool["tool_id"], "ok": Value::Null, "kind": "none"}),
    }
}

pub fn health(p: &Project) -> Vec<Value> {
    let mut tools = kernel_tools(p); tools.extend(project_tools(p));
    tools.iter().filter(|t| t["status"].as_str() == Some("active")).map(|t| health_one(p, t)).collect()
}

pub fn check_permission(p: &Project, role: &str, perm: &str) -> bool { role_permissions(p, role).iter().any(|x| x == perm) }
