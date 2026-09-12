//! Tool/MCP capability registry and permissions (framework §28-32). Exposure is role/task scoped; least authority.
use crate::orchestration::gates;
use crate::util::{now_iso, read_yaml, write_json};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub fn kernel_tools(p: &Project) -> Vec<Value> {
    let path = p
        .kernel_dir()
        .join("tools")
        .join("registry")
        .join("TOOLS.yaml");
    read_yaml(&path)
        .ok()
        .and_then(|v| v["tools"].as_array().cloned())
        .unwrap_or_default()
}
pub fn project_tools(p: &Project) -> Vec<Value> {
    let dir = p.overlay_dir().join("tools");
    let Ok(rd) = std::fs::read_dir(&dir) else {
        return vec![];
    };
    let mut paths: Vec<_> = rd
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|x| x.extension().map(|e| e == "yaml").unwrap_or(false))
        .collect();
    paths.sort();
    paths
        .into_iter()
        .filter_map(|x| read_yaml(&x).ok())
        .collect()
}
pub fn mcp_servers(p: &Project) -> Vec<Value> {
    let mut out = read_yaml(
        &p.kernel_dir()
            .join("tools")
            .join("mcp")
            .join("registry.yaml"),
    )
    .ok()
    .and_then(|v| v["servers"].as_array().cloned())
    .unwrap_or_default();
    if let Ok(v) = read_yaml(&p.overlay_dir().join("mcp").join("registry.yaml")) {
        out.extend(v["servers"].as_array().cloned().unwrap_or_default());
    }
    out
}

pub fn role_permissions(p: &Project, role: &str) -> Vec<String> {
    p.overlay()
        .get("TOOL_PERMISSIONS.yaml")
        .get("roles")
        .and_then(|r| r.get(role))
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default()
}

fn role_allowed(tool: &Value, role: &str, perms: &[String]) -> bool {
    let approved = tool["approved_roles"]
        .as_array()
        .map(|a| {
            a.iter()
                .any(|r| r.as_str() == Some(role) || r.as_str() == Some("all"))
        })
        .unwrap_or(false);
    let required: Vec<String> = tool["required_permission_classes"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    approved && required.iter().all(|r| perms.contains(r))
}

/// Capability plugins as registry entries (type `plugin`), classified for the acting role (verifier H-N2).
pub fn plugin_tools(p: &Project) -> (Vec<Value>, Value) {
    let set = crate::capabilities::governance::plugin_set(p);
    let pol = p.policies();
    let min = pol.get_str("TOOL_POLICY", "plugins.min_authority", "L2");
    let roles_doc = crate::authority::roles_doc(p);
    let default_roles: Vec<String> = roles_doc["roles"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter(|r| {
                    crate::authority::parse_level(r["level"].as_str().unwrap_or("")).unwrap_or(0)
                        >= crate::authority::parse_level(&min).unwrap_or(2)
                })
                .filter_map(|r| r["id"].as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let entry = |d: &crate::capabilities::protocol::PluginDescriptor, status: &str| {
        let registered = d
            .raw
            .get("provenance")
            .and_then(|v| v.get("registered_at"))
            .is_some();
        let approved: Vec<String> = if !d.approved_roles.is_empty() {
            d.approved_roles.clone()
        } else if registered {
            vec!["all".into()]
        } else {
            default_roles.clone()
        };
        json!({"tool_id": d.plugin_id, "name": d.plugin_id, "type": "plugin", "capabilities": [d.capability], "status": status, "version": d.version, "languages": d.languages, "approved_roles": approved, "required_permission_classes": d.required_permission_classes, "health_check": d.raw.get("health_check").cloned().unwrap_or(json!({"kind": "command_exists"})), "version_pin": d.version, "pin": d.raw.get("pin").cloned().unwrap_or(Value::Null), "provenance": d.raw.get("provenance").cloned().unwrap_or(Value::Null), "source": d.source})
    };
    let mut out: Vec<Value> = set.usable.iter().map(|d| entry(d, "active")).collect();
    let (valid, _) = crate::capabilities::host::discover_all(&p.root);
    for d in valid
        .iter()
        .filter(|d| !set.usable.iter().any(|u| u.plugin_id == d.plugin_id))
    {
        let mut e = entry(d, "active");
        e["denied_for_acting_role"] = json!(set
            .denied
            .iter()
            .find(|x| x["plugin_id"] == d.plugin_id)
            .map(|x| x["reason"].clone())
            .unwrap_or(Value::Null));
        out.push(e);
    }
    for r in &set.rejected {
        out.push(json!({"tool_id": r["plugin_id"], "name": r["plugin_id"], "type": "plugin", "capabilities": [], "status": "rejected", "reason": r["reason"], "source": r["source"], "approved_roles": []}));
    }
    (
        out,
        json!({"usable": set.usable.len(), "denied": set.denied, "rejected": set.rejected}),
    )
}

/// Compile governance/generated/tool-registry.json (kernel + project tools, plugins, MCP servers, per-role exposure).
pub fn generate_registry(p: &Project) -> Result<Value> {
    let mut tools = kernel_tools(p);
    tools.extend(project_tools(p));
    let (ptools, plugin_summary) = plugin_tools(p);
    tools.extend(ptools);
    let servers = mcp_servers(p);
    let perms_all = p.overlay().get("TOOL_PERMISSIONS.yaml");
    let mut exposure = serde_json::Map::new();
    if let Some(roles) = perms_all.get("roles").and_then(|r| r.as_object()) {
        for (role, _) in roles {
            let perms = role_permissions(p, role);
            let allow: Vec<String> = perms_all
                .get("tool_allowlist")
                .and_then(|a| a.get(role))
                .and_then(|v| v.as_array())
                .map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(|s| s.to_string()))
                        .collect()
                })
                .unwrap_or_default();
            let mcp_allow: Vec<String> = perms_all
                .get("mcp_servers")
                .and_then(|a| a.get(role))
                .and_then(|v| v.as_array())
                .map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(|s| s.to_string()))
                        .collect()
                })
                .unwrap_or_default();
            let t: Vec<String> = tools
                .iter()
                .filter(|t| {
                    t["status"].as_str() == Some("active")
                        && role_allowed(t, role, &perms)
                        && (allow.is_empty()
                            || allow
                                .iter()
                                .any(|a| Some(a.as_str()) == t["tool_id"].as_str()))
                })
                .filter_map(|t| t["tool_id"].as_str().map(|s| s.to_string()))
                .collect();
            let m: Vec<String> = servers
                .iter()
                .filter(|s| {
                    s["status"].as_str() == Some("active")
                        && role_allowed(s, role, &perms)
                        && (mcp_allow.is_empty()
                            || mcp_allow
                                .iter()
                                .any(|a| Some(a.as_str()) == s["id"].as_str()))
                })
                .filter_map(|s| s["id"].as_str().map(|x| x.to_string()))
                .collect();
            exposure.insert(
                role.clone(),
                json!({"permissions": perms, "tools": t, "mcp_servers": m}),
            );
        }
    }
    let reg = json!({"generated_from": {"kernel": p.lock().map(|l| l["kernel_manifest_hash"].clone()).unwrap_or(Value::Null), "overlay": p.overlay().hash(), "generated_at": now_iso()}, "tools": tools, "plugins": plugin_summary, "mcp_servers": servers, "role_exposure": exposure});
    let path = p.policies().get_str(
        "TOOL_POLICY",
        "mcp.registry_path",
        "governance/generated/tool-registry.json",
    );
    write_json(&p.root.join(path), &reg)?;
    Ok(reg)
}

/// Languages of the governed project's detected ecosystems (used to resolve native tooling, never the OS language).
pub fn project_languages(p: &Project) -> Vec<String> {
    let eco = crate::capabilities::ecosystems::detect(&p.root, &[p.contract().root("product")]);
    let mut v: Vec<String> = eco["ecosystems"]
        .as_array()
        .map(|a| {
            a.iter()
                .flat_map(|e| e["languages"].as_array().cloned().unwrap_or_default())
                .filter_map(|l| l.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    v.sort();
    v.dedup();
    v
}

fn tool_languages(t: &Value) -> Vec<String> {
    t["languages"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default()
}

pub fn resolve(p: &Project, role: &str, capability: &str) -> Result<Value> {
    let perms = role_permissions(p, role);
    let mut tools = kernel_tools(p);
    tools.extend(project_tools(p));
    tools.extend(plugin_tools(p).0);
    let langs = project_languages(p);
    // a tool tagged with `languages` applies only to governed projects of those languages (registry-driven, not OS-driven)
    let lang_ok = |t: &Value| {
        let tl = tool_languages(t);
        tl.is_empty() || tl.iter().any(|l| langs.contains(l))
    };
    let matches: Vec<Value> = tools
        .iter()
        .filter(|t| {
            t["capabilities"]
                .as_array()
                .map(|a| a.iter().any(|c| c.as_str() == Some(capability)))
                .unwrap_or(false)
        })
        .cloned()
        .collect();
    let usable: Vec<Value> = matches.iter().filter(|t| t["status"].as_str() == Some("active") && role_allowed(t, role, &perms) && lang_ok(t)).map(|t| json!({"tool_id": t["tool_id"], "name": t["name"], "type": t["type"], "version": t["version"], "languages": t["languages"], "available": t["health_check"]["command"].as_array().and_then(|c| c.first()).and_then(|c| c.as_str()).map(crate::capabilities::ecosystems::binary_available)})).collect();
    let mcp: Vec<Value> = mcp_servers(p)
        .into_iter()
        .filter(|s| {
            s["capabilities"]
                .as_array()
                .map(|a| a.iter().any(|c| c.as_str() == Some(capability)))
                .unwrap_or(false)
                && s["status"].as_str() == Some("active")
                && role_allowed(s, role, &perms)
        })
        .map(|s| json!({"mcp_id": s["id"], "name": s["name"]}))
        .collect();
    let gap = usable.is_empty() && mcp.is_empty();
    let reason = if gap {
        if matches.is_empty() {
            "no registered tool provides this capability"
        } else if matches.iter().all(|t| !lang_ok(t)) {
            "registered tools for this capability target other languages than the governed project's"
        } else if matches
            .iter()
            .any(|t| t["status"].as_str() != Some("active"))
        {
            "a tool exists but is not active (proposed/deprecated)"
        } else {
            "role lacks approval or permission classes for the available tool"
        }
    } else {
        ""
    };
    Ok(
        json!({"role": role, "capability": capability, "project_languages": langs, "tools": usable, "mcp_servers": mcp, "capability_gap": gap, "reason": reason, "next": if gap { "gov tools install --descriptor <file> (checks TOOL_POLICY auto-install conditions) or raise a tooling task" } else { "" }}),
    )
}

/// Install/register a tool only when every TOOL_POLICY auto-install condition holds; otherwise raise a Human Decision Gate.
pub fn install(p: &Project, descriptor: Value, role: &str, execute: bool) -> Result<Value> {
    crate::orchestration::control::guard_write(p, "tools install")?;
    crate::authority::require(p, "install_tool")?;
    let pol = p.policies();
    if pol.get_bool("TOOL_POLICY", "health_check_required", true)
        && descriptor
            .get("health_check")
            .and_then(|h| h.get("kind"))
            .is_none()
    {
        return Err(GovError::new(
            "USAGE",
            "TOOL_POLICY.health_check_required: the descriptor must declare health_check.kind",
        ));
    }
    let tool_types = pol.get_list("TOOL_POLICY", "tool_types");
    if let Some(t) = descriptor.get("type").and_then(|v| v.as_str()) {
        if !tool_types.is_empty() && !tool_types.iter().any(|x| x == t) {
            return Err(GovError::new(
                "USAGE",
                format!("tool type '{t}' is not in TOOL_POLICY.tool_types {tool_types:?}"),
            ));
        }
    }
    let conditions = pol.get_list("TOOL_POLICY", "auto_install_conditions");
    let install_roles: Vec<String> = p
        .overlay()
        .get("TOOL_PERMISSIONS.yaml")
        .get("install_authority_roles")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let approved_licences = pol.get_list("TOOL_POLICY", "approved_licences");
    let max_cost = pol.get_f64("BUDGET_POLICY", "defaults.max_install_cost_usd", 0.0);
    let tool_id = descriptor["tool_id"].as_str().unwrap_or("").to_string();
    if tool_id.is_empty() {
        return Err(GovError::new("USAGE", "descriptor requires tool_id"));
    }
    let mut checks = vec![];
    let mut push = |name: &str, ok: bool, detail: String| {
        checks.push(json!({"condition": name, "ok": ok, "detail": detail}))
    };
    push(
        "role_has_install_authority",
        install_roles.iter().any(|r| r == role),
        format!("role {role}; install roles {install_roles:?}"),
    );
    push(
        "installation_reversible",
        descriptor["reversible"].as_bool().unwrap_or(false),
        "descriptor.reversible".into(),
    );
    let cost = descriptor["cost_usd"].as_f64().unwrap_or(0.0);
    push(
        "cost_within_budget",
        cost <= max_cost,
        format!("cost {cost} <= {max_cost}"),
    );
    let req: Vec<String> = descriptor["required_permission_classes"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let perms = role_permissions(p, role);
    push(
        "no_privilege_escalation",
        req.iter().all(|r| perms.contains(r))
            && !req
                .iter()
                .any(|r| r == "SYSTEM_INSTALL" || r == "SECRET_READ" || r == "DEPLOY_PRODUCTION"),
        format!("required {req:?} within role permissions {perms:?}"),
    );
    let lic = descriptor["license"].as_str().unwrap_or("").to_string();
    push(
        "licence_and_security_satisfied",
        approved_licences.contains(&lic)
            && descriptor["security_review"]
                .as_str()
                .map(|s| s == "passed")
                .unwrap_or(false),
        format!(
            "license {lic}; security_review {}",
            descriptor["security_review"]
        ),
    );
    push(
        "version_pinned_and_recorded",
        descriptor["version_pin"]
            .as_str()
            .map(|s| !s.is_empty())
            .unwrap_or(false),
        "descriptor.version_pin".into(),
    );
    push(
        "tool_registered",
        true,
        "will be registered under governance/project/tools/".into(),
    );
    push(
        "environment_reproducible",
        descriptor["install_command"]
            .as_array()
            .map(|a| !a.is_empty())
            .unwrap_or(false)
            && descriptor["uninstall_command"]
                .as_array()
                .map(|a| !a.is_empty())
                .unwrap_or(false),
        "install and uninstall commands declared".into(),
    );
    // only the conditions the policy declares are evaluated (all must hold)
    let checks: Vec<Value> = checks
        .into_iter()
        .filter(|c| {
            conditions.is_empty()
                || conditions
                    .iter()
                    .any(|n| n == c["condition"].as_str().unwrap_or(""))
        })
        .collect();
    let all_ok = checks.iter().all(|c| c["ok"].as_bool().unwrap_or(false));
    if !all_ok {
        let failed: Vec<String> = checks
            .iter()
            .filter(|c| !c["ok"].as_bool().unwrap_or(false))
            .map(|c| c["condition"].as_str().unwrap_or("").to_string())
            .collect();
        let gate = gates::create_system(
            p,
            json!({"question": format!("Approve installation of tool {tool_id}? Automatic installation conditions failed: {}", failed.join(", ")), "why_now": "a task requires a capability that is not available", "current_state": "tool not installed", "options": [{"id": "A", "description": "approve installation as described"}, {"id": "B", "description": "reject; find an alternative"}], "impact": "adds an executable capability to the environment", "reversibility": if descriptor["reversible"].as_bool().unwrap_or(false) { "reversible" } else { "irreversible or unknown" }, "recommendation": "B unless the tool is essential", "confidence": 0.6, "trigger": "tool_install", "impact_radius": "R2"}),
        )?;
        return Ok(json!({"installed": false, "human_gate": gate["id"], "checks": checks}));
    }
    let mut desc = descriptor.clone();
    desc["status"] = json!("active");
    desc["installed_by"] = json!(p.session_id);
    desc["installed_at"] = json!(now_iso());
    desc["type"] = desc.get("type").cloned().unwrap_or(json!("library"));
    desc["approved_roles"] = desc.get("approved_roles").cloned().unwrap_or(json!([role]));
    desc["capabilities"] = desc.get("capabilities").cloned().unwrap_or(json!([]));
    desc["name"] = desc.get("name").cloned().unwrap_or(json!(tool_id));
    let mut exec_result = Value::Null;
    if execute {
        let cmd: Vec<String> = desc["install_command"]
            .as_array()
            .unwrap()
            .iter()
            .filter_map(|x| x.as_str().map(|s| s.to_string()))
            .collect();
        let (code, out, err) = crate::util::run_cmd(&cmd, &p.root)?;
        exec_result = json!({"exit": code, "stdout": out.chars().take(2000).collect::<String>(), "stderr": err.chars().take(2000).collect::<String>()});
        if code != 0 {
            return Err(GovError::new(
                "INSTALL_FAILED",
                format!("install command failed ({code})"),
            )
            .with_details(exec_result));
        }
    }
    p.schemas()
        .validate("tool", &desc, &format!("({tool_id})"))?;
    crate::util::write_yaml(
        &p.overlay_dir()
            .join("tools")
            .join(format!("{tool_id}.yaml")),
        &desc,
    )?;
    let health = health_one(p, &desc);
    generate_registry(p)?;
    Ok(
        json!({"installed": true, "tool_id": tool_id, "checks": checks, "executed": execute, "exec_result": exec_result, "health": health, "registered_at": format!("governance/project/tools/{tool_id}.yaml")}),
    )
}

pub fn health_one(p: &Project, tool: &Value) -> Value {
    let hc = &tool["health_check"];
    match hc["kind"].as_str().unwrap_or("none") {
        "builtin" => json!({"tool_id": tool["tool_id"], "ok": true, "kind": "builtin"}),
        "command" => {
            let cmd: Vec<String> = hc["command"]
                .as_array()
                .map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(|s| s.to_string()))
                        .collect()
                })
                .unwrap_or_default();
            let expect = hc["expect_exit"].as_i64().unwrap_or(0) as i32;
            match crate::util::run_cmd(&cmd, &p.root) {
                Ok((code, _, err)) => {
                    json!({"tool_id": tool["tool_id"], "ok": code == expect, "kind": "command", "exit": code, "stderr": err.chars().take(200).collect::<String>()})
                }
                Err(e) => json!({"tool_id": tool["tool_id"], "ok": false, "error": e.to_string()}),
            }
        }
        _ => json!({"tool_id": tool["tool_id"], "ok": Value::Null, "kind": "none"}),
    }
}

pub fn health(p: &Project) -> Vec<Value> {
    let mut tools = kernel_tools(p);
    tools.extend(project_tools(p));
    tools
        .iter()
        .filter(|t| t["status"].as_str() == Some("active"))
        .map(|t| health_one(p, t))
        .collect()
}

pub fn check_permission(p: &Project, role: &str, perm: &str) -> bool {
    role_permissions(p, role).iter().any(|x| x == perm)
}
