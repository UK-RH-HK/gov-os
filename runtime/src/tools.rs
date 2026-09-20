//! Tool/MCP capability registry and permissions (framework §28-32). Exposure is role/task scoped; least authority.
//!
//! **Tool acquisition (Phase-2 repair iteration 1, WS-7: BC-P2-41; Contract v3 F3:416-423, F4:431; D-0007
//! consequence 4).** `gov tools install` installs autonomously only when every `TOOL_POLICY.auto_install_conditions`
//! entry holds, and the security part of `licence_and_security_satisfied` holds only on a **governed security review
//! of that tool identity and version** ([`security_review_evidence`]): an OS-written (T2-verified) report closing a
//! `security`-class task, whose `security_review` block names this tool id and version with verdict `passed`, written
//! by a session and role other than the installer's. `gov task close` writes and T2-seals that report
//! (`orchestration::tasks::close`), so a review closed by another role is available as evidence with no owner gate
//! (IP-W7-1, confirmed in round 3). Anything else — the descriptor's own `security_review: passed`, an unrelated
//! record, a hand-written report — is a request, not evidence. When a condition fails, the approval is a
//! Human Decision Gate raised for **exactly this installation** (`subject.kind: tool-installation`, the digest of the
//! installation descriptor): a presented, owner-answered A on that gate lets the governed install proceed, a decline
//! ends the request, a pending gate is returned instead of raising another, and a gate raised for anything else
//! never authorises it ([`crate::capabilities::governance::approval_for_subject`]).
use crate::capabilities::governance::{approval_for_subject, SubjectApproval};
use crate::orchestration::gates;
use crate::records::{Record, RecordStore};
use crate::util::{canonical_json, now_iso, read_yaml, sha256_hex, write_json};
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
///
/// Registration, approval and provenance come **only** from the OS-written, T2-verified plugin registry
/// (D-0007 rule 2; gamma-r A0-F2-02): a hand-declared descriptor's own `provenance`, `status` or `approved_roles`
/// never makes it appear registered, active or approved. `status` is `active` only for a plugin that can run at all
/// (an intact, approved registration, or an OS-provided capability server); an unregistered executable plugin is
/// `unregistered`, a plugin failing its integrity check is `blocked`.
pub fn plugin_tools(p: &Project) -> (Vec<Value>, Value) {
    let set = crate::capabilities::governance::plugin_set(p);
    let pol = p.policies();
    let min = pol.get_str("TOOL_POLICY", "plugins.min_authority", "L2");
    let roles_doc = crate::authority::roles_doc(p);
    let floor_roles: Vec<String> = roles_doc["roles"]
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
    let entry = |d: &crate::capabilities::protocol::PluginDescriptor| {
        let standing = crate::capabilities::registry::standing(p, d);
        let reg = match &standing {
            crate::capabilities::registry::Standing::Registered(e) => Some((**e).clone()),
            _ => None,
        };
        let integrity = crate::capabilities::governance::integrity(p, d);
        let class = crate::capabilities::binding::resolve(d, &p.root)
            .map(|i| i.class.as_str())
            .unwrap_or("UNRESOLVED");
        let status = match (&integrity, &reg) {
            (Some((code, _, _)), _) if code == "PLUGIN_NOT_APPROVED" && reg.is_none() => {
                "unregistered"
            }
            (Some(_), _) => "blocked",
            (None, _) => "active",
        };
        let approved: Vec<String> = match (&reg, status) {
            // the registry's approved roles, cut to the kernel floor execution applies (an L0/L1 role is never
            // offered a plugin that execution would refuse)
            (Some(e), "active") => {
                let listed: Vec<String> = e["approved_roles"]
                    .as_array()
                    .map(|a| {
                        a.iter()
                            .filter_map(|x| x.as_str().map(String::from))
                            .collect()
                    })
                    .unwrap_or_default();
                if listed.is_empty() || listed.iter().any(|r| r == "all") {
                    floor_roles.clone()
                } else {
                    listed
                        .into_iter()
                        .filter(|r| floor_roles.contains(r))
                        .collect()
                }
            }
            // an OS-provided capability server: the kernel floor, narrowed (never widened) by the descriptor
            (None, "active") => {
                let narrowing: Vec<&String> = d
                    .approved_roles
                    .iter()
                    .filter(|r| r.as_str() != "all")
                    .collect();
                floor_roles
                    .iter()
                    .filter(|r| narrowing.is_empty() || narrowing.contains(r))
                    .cloned()
                    .collect()
            }
            _ => vec![],
        };
        let provenance = reg
            .as_ref()
            .map(|e| json!({"registered_by_role": e["registered_by_role"], "registered_by_session": e["registered_by_session"], "registered_at": e["registered_at"], "gate": e["registration_gate"], "method": e["method"], "source": crate::capabilities::registry::REGISTRY_PATH}))
            .unwrap_or(Value::Null);
        json!({"tool_id": d.plugin_id, "name": d.plugin_id, "type": "plugin", "capabilities": [d.capability], "status": status, "version": d.version, "languages": d.languages, "approved_roles": approved, "required_permission_classes": d.required_permission_classes, "health_check": d.raw.get("health_check").cloned().unwrap_or(json!({"kind": "command_exists"})), "version_pin": d.version, "execution_class": class, "pin": reg.as_ref().map(|e| json!({"implementation_sha256": e["implementation_sha256"], "descriptor_sha256": e["descriptor_sha256"]})).unwrap_or(Value::Null), "registered": reg.is_some(), "provenance": provenance, "integrity": integrity.as_ref().map(|(c, s, m)| json!({"code": c, "severity": s, "message": m})), "source": d.source})
    };
    let mut out: Vec<Value> = set.usable.iter().map(&entry).collect();
    let (valid, _) = crate::capabilities::host::discover_all(&p.root);
    for d in valid
        .iter()
        .filter(|d| !set.usable.iter().any(|u| u.plugin_id == d.plugin_id))
    {
        let mut e = entry(d);
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

/// Descriptor fields that are requests or OS-written results, never part of the installation a gate approves.
const INSTALLATION_NON_SUBJECT: &[&str] = &[
    "human_gate",
    "registration_gate",
    "approval_gate",
    "status",
    "installed_by",
    "installed_at",
    "approval",
    "installation_sha256",
    "security_review_evidence",
    crate::t2::SEAL_FIELD,
];

/// The version a tool installation pins: `version_pin` when declared, else `version`.
fn installed_version(descriptor: &Value) -> String {
    descriptor["version_pin"]
        .as_str()
        .filter(|s| !s.is_empty())
        .map(String::from)
        .or_else(|| {
            descriptor.get("version").map(|v| match v {
                Value::String(s) => s.clone(),
                Value::Null => String::new(),
                other => other.to_string(),
            })
        })
        .unwrap_or_default()
}

/// **The installation subject** a tool-install gate approves: tool identity, pinned version and the installation
/// descriptor (commands, permissions, licence, cost, …) minus request/result fields. `(subject, sha256)`.
pub fn installation_subject(descriptor: &Value) -> (Value, String) {
    let mut d = descriptor.clone();
    if let Some(o) = d.as_object_mut() {
        for k in INSTALLATION_NON_SUBJECT {
            o.remove(*k);
        }
    }
    let doc = json!({"kind": "tool-installation", "tool_id": descriptor["tool_id"], "version": installed_version(descriptor), "descriptor": d});
    let sha = sha256_hex(canonical_json(&doc).as_bytes());
    (doc, sha)
}

/// **Is `rec` a governed security review of tool `tool_id` at `version`, not attested by the installer?**
/// (Contract v3 F4:431 "Security review cannot be self-attested"; D-0007 consequence 4 and rule 2.) Pure: the caller
/// supplies the record's T2 binding and the task it closes.
///
/// * the record is a `report` that an OS operation wrote as it stands (T2 `Verified` — a report is T2 state, and a
///   hand-written or edited one is a request, not evidence), ACTIVE, with outcome `success`;
/// * it closes a `security`-class task (`task` names it, and the task's `closed_by_report` names this report);
/// * its `security_review` block names exactly this tool id and version with `verdict: passed`;
/// * its author (recorded `session` and `role`) is neither the installing session nor the installing role.
pub fn review_verdict(
    rec: &Record,
    binding: &crate::t2::Binding,
    task: Option<&Record>,
    tool_id: &str,
    version: &str,
    installer_session: &str,
    installer_role: &str,
) -> std::result::Result<Value, String> {
    let id = rec.id();
    if rec.rtype() != "report" {
        return Err(format!(
            "{id} is a {} record, not a security review report",
            rec.rtype()
        ));
    }
    if !binding.is_verified() {
        return Err(format!("{id} is not a report a gov operation wrote as it stands (T2 binding {}); a hand-written or edited report is a request, not evidence", binding.code()));
    }
    if rec.status() != "ACTIVE" {
        return Err(format!("{id} is {}, not ACTIVE", rec.status()));
    }
    if rec.get("outcome") != "success" {
        return Err(format!(
            "{id} records outcome '{}', not a completed review",
            rec.get("outcome")
        ));
    }
    let t = task.ok_or_else(|| format!("{id} closes no task (task '{}')", rec.get("task")))?;
    if t.rtype() != "task" || t.get("class") != "security" {
        return Err(format!(
            "{id} closes {} of class '{}', not a security review task (class 'security')",
            t.id(),
            t.get("class")
        ));
    }
    if t.get("closed_by_report") != id {
        return Err(format!(
            "task {} is not closed by {id} (closed_by_report '{}')",
            t.id(),
            t.get("closed_by_report")
        ));
    }
    let sr = rec
        .data
        .get("security_review")
        .filter(|v| v.is_object())
        .ok_or_else(|| {
            format!("{id} carries no security_review block (tool_id, version, verdict)")
        })?;
    let (rt, rv, verdict) = (
        sr["tool_id"].as_str().unwrap_or(""),
        sr["version"]
            .as_str()
            .map(String::from)
            .unwrap_or_else(|| sr["version"].to_string()),
        sr["verdict"].as_str().unwrap_or(""),
    );
    if rt != tool_id || rv != version {
        return Err(format!(
            "{id} reviews tool '{rt}' version '{rv}', not '{tool_id}' version '{version}'"
        ));
    }
    if verdict != "passed" {
        return Err(format!("{id} records verdict '{verdict}', not 'passed'"));
    }
    let (rs, rr) = (rec.get("session"), rec.get("role"));
    if rs.is_empty() || rr.is_empty() {
        return Err(format!("{id} records no reviewing session/role"));
    }
    if rs == installer_session {
        return Err(format!("{id} was written by the installing session {rs}: a security review cannot be self-attested"));
    }
    if rr == installer_role {
        return Err(format!("{id} was written by the installing role {rr}: a security review cannot be self-attested"));
    }
    Ok(
        json!({"record": id, "path": rec.path, "task": t.id(), "reviewer_session": rs, "reviewer_role": rr, "tool_id": tool_id, "version": version}),
    )
}

/// The security-review evidence for installing `descriptor` as `installer_role` (see [`review_verdict`]).
pub fn security_review_evidence(
    p: &Project,
    descriptor: &Value,
    installer_role: &str,
) -> std::result::Result<Value, String> {
    let rid = descriptor["security_review_record"]
        .as_str()
        .filter(|s| !s.is_empty())
        .ok_or_else(|| "the descriptor names no security_review_record (its own `security_review: passed` is a claim, not evidence)".to_string())?;
    let store = RecordStore::load(&p.root);
    let rec = store
        .get(rid)
        .ok_or_else(|| format!("{rid} does not resolve to a governed record"))?;
    let binding = crate::t2::verify_record(rec);
    let task = store.get(&rec.get("task"));
    review_verdict(
        rec,
        &binding,
        task,
        descriptor["tool_id"].as_str().unwrap_or(""),
        &installed_version(descriptor),
        &p.session_id,
        installer_role,
    )
}

/// The registry view a tool installation regenerates (TOOL_POLICY `mcp.registry_path`).
fn registry_path(p: &Project) -> String {
    p.policies().get_str(
        "TOOL_POLICY",
        "mcp.registry_path",
        "governance/generated/tool-registry.json",
    )
}

/// The roles TOOL_PERMISSIONS gives installation authority (empty: the policy names none, and the operation's own
/// authority class decides alone).
fn install_authority_roles(p: &Project) -> Vec<String> {
    p.overlay()
        .get("TOOL_PERMISSIONS.yaml")
        .get("install_authority_roles")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default()
}

/// **A tool installation request as the OS derives it, before any approval is asked or any byte is written**: the
/// `TOOL_POLICY.auto_install_conditions` evaluated for the acting role, the governed security-review evidence, and
/// the installation subject a gate approves. Only [`prepare_installation`] constructs one, and the one installation
/// writer ([`install_write`]) asks the §6 acquisition sink at the instant of its write.
struct PreparedInstall {
    tool_id: String,
    version: String,
    /// the descriptor exactly as given: the bytes the request is derived from, and what the manifest operation
    /// carries, so CIT-E can derive the same request again
    descriptor: Value,
    /// the role the conditions were evaluated for (D-0007 rule 2: the acting role, never a caller-supplied one)
    role: String,
    checks: Vec<Value>,
    all_ok: bool,
    failed: Vec<String>,
    review: std::result::Result<Value, String>,
    license: String,
    required: Vec<String>,
    subject_doc: Value,
    subject: String,
    cited: Vec<String>,
}

impl PreparedInstall {
    fn dest_rel(&self) -> String {
        format!("governance/project/tools/{}.yaml", self.tool_id)
    }
}

/// Derive the installation request from `descriptor` for `role`: schema-level policy checks, the auto-install
/// conditions, the security-review evidence and the installation subject. Writes nothing and asks no approval.
fn prepare_installation(p: &Project, descriptor: Value, role: &str) -> Result<PreparedInstall> {
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
    let install_roles = install_authority_roles(p);
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
    // A descriptor's own "security_review: passed" is a claim, not evidence (trust-boundary audit, D-0007), and so is
    // naming any record: the security part holds only on a governed security review OF THIS TOOL IDENTITY AND
    // VERSION that the installer did not write (BC-P2-41; Contract v3 F4:431). Otherwise the condition fails and the
    // installation needs the human's approval, exactly as for any other unmet auto-install condition.
    let review = security_review_evidence(p, &descriptor, role);
    push(
        "licence_and_security_satisfied",
        approved_licences.contains(&lic) && review.is_ok(),
        format!(
            "license {lic}{}; security review: {}",
            if approved_licences.contains(&lic) {
                " (approved)"
            } else {
                " (not in TOOL_POLICY.approved_licences)"
            },
            match &review {
                Ok(v) => format!(
                    "governed review {} of {tool_id} {} by {} ({})",
                    v["record"].as_str().unwrap_or(""),
                    v["version"].as_str().unwrap_or(""),
                    v["reviewer_role"].as_str().unwrap_or(""),
                    v["path"].as_str().unwrap_or("")
                ),
                Err(why) => format!("not evidenced: {why}"),
            }
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
    let failed: Vec<String> = checks
        .iter()
        .filter(|c| !c["ok"].as_bool().unwrap_or(false))
        .map(|c| c["condition"].as_str().unwrap_or("").to_string())
        .collect();
    let (subject_doc, subject) = installation_subject(&descriptor);
    // a gate id written into the descriptor is a request naming a candidate; the gate is found by its subject
    let cited: Vec<String> = ["approval_gate", "human_gate", "registration_gate"]
        .iter()
        .filter_map(|k| {
            descriptor
                .get(*k)
                .and_then(|v| v.as_str())
                .map(String::from)
        })
        .collect();
    Ok(PreparedInstall {
        version: installed_version(&descriptor),
        tool_id,
        descriptor,
        role: role.to_string(),
        checks,
        all_ok,
        failed,
        review,
        license: lic,
        required: req,
        subject_doc,
        subject,
        cited,
    })
}

// =============================================================================================================
// OD-P2-03: does this installation stay inside the project's already-authorised permission and trust envelope?
// =============================================================================================================

/// The trusted OS state the **authorised** side of the envelope is read from (OD-P2-03 requirement 2; governed
/// record `D-0011`). A descriptor is never one of them: Contract v3 F4 ("a descriptor cannot authorise itself") and
/// BC-P2-39, whose defect was a declaration deciding whether approval was needed. What a descriptor declares is a
/// *request*: it can only ever **add** to what the installation is taken to demand, never enlarge this envelope and
/// never shrink what the OS derives for itself.
const ENVELOPE_SOURCES: &[&str] = &[
    "TOOL_PERMISSIONS.yaml roles.<acting role>: the permission classes the project has already authorised for it",
    "TOOL_PERMISSIONS.yaml install_authority_roles",
    "AUTHORITY_POLICY.authority_levels_required.install_tool",
    "REPOSITORY_CONTRACT.yaml: the path map (which paths may be mutated, and their class)",
    "DATA_SENSITIVITY.yaml + SECURITY_POLICY: sensitivity classes and secret path patterns",
    "TOOL_POLICY.installation_envelope: host-authority/credential/network classes and the command-token floor",
    "tools/registry/TOOLS.yaml network_allowlist: the approved registries and allowlisted services (ecosystem knowledge lives in the kernel tool registry, never in kernel policy - INV-005)",
];

/// One entry of `TOOL_POLICY.installation_envelope`.
fn envelope_list(p: &Project, key: &str) -> Vec<String> {
    p.policies()
        .get_list("TOOL_POLICY", &format!("installation_envelope.{key}"))
}

/// **The network allowlist an installation's trust boundary is compared against**: the approved registries and
/// allowlisted services the kernel's **tool registry** carries (`tools/registry/TOOLS.yaml`, key
/// `network_allowlist`). They are not in `TOOL_POLICY` because registry hostnames are ecosystem knowledge, which
/// `INV-005` keeps out of kernel policy — the same reason the language-native tools live in that registry. The
/// registry is part of the verified kernel payload, so a project can no more alter it than the policy.
fn network_allowlist(p: &Project) -> Vec<String> {
    let doc = read_yaml(
        &p.kernel_dir()
            .join("tools")
            .join("registry")
            .join("TOOLS.yaml"),
    )
    .unwrap_or(Value::Null);
    ["approved_registries", "allowlisted_services"]
        .iter()
        .flat_map(|k| {
            doc["network_allowlist"][*k]
                .as_array()
                .cloned()
                .unwrap_or_default()
        })
        .filter_map(|v| v.as_str().map(|s| s.to_ascii_lowercase()))
        .collect()
}

/// Every command the installation carries, as `(where, argv)`. The install command is what the OS runs when the
/// transaction executes; the uninstall and health commands are what the installed tool is.
fn installation_commands(d: &Value) -> Vec<(String, Vec<String>)> {
    let strs = |v: &Value| -> Vec<String> {
        v.as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default()
    };
    let mut out = vec![];
    for k in ["install_command", "uninstall_command"] {
        let v = strs(&d[k]);
        if !v.is_empty() {
            out.push((k.to_string(), v));
        }
    }
    let h = strs(&d["health_check"]["command"]);
    if !h.is_empty() {
        out.push(("health_check.command".to_string(), h));
    }
    out
}

/// The strings a token may hide: the token itself and the value of a `--flag=value`.
fn token_values(tok: &str) -> Vec<String> {
    let mut v = vec![tok.to_string()];
    if let Some((_, rhs)) = tok.split_once('=') {
        if !rhs.is_empty() {
            v.push(rhs.to_string());
        }
    }
    v
}

/// A candidate the OS reads as a filesystem path that leaves the project: absolute, home-relative,
/// drive-qualified, or escaping with a `..` segment.
fn leaves_project(c: &str) -> bool {
    if c.starts_with('/') || c.starts_with('~') || c.starts_with('\\') {
        return true;
    }
    if c.len() > 2 && c.as_bytes()[1] == b':' && matches!(c.as_bytes()[2], b'/' | b'\\') {
        return true;
    }
    c.replace('\\', "/").split('/').any(|seg| seg == "..")
}

/// The host of a URL-ish candidate (`scheme://[user@]host[:port]/…`), if any.
fn endpoint_host(c: &str) -> Option<String> {
    let rest = c.split_once("://").map(|(_, r)| r)?;
    let hostport = rest.split(['/', '?', '#']).next().unwrap_or("");
    let host = hostport.rsplit('@').next().unwrap_or(hostport);
    let host = host.split(':').next().unwrap_or(host);
    (!host.is_empty()).then(|| host.to_ascii_lowercase())
}

/// Case-insensitive glob match of a name against `TOOL_POLICY.installation_envelope.credential_patterns`.
fn matches_any_pattern(name: &str, patterns: &[String]) -> bool {
    let up = name.to_ascii_uppercase();
    patterns
        .iter()
        .any(|p| crate::util::glob_match(&p.to_ascii_uppercase(), &up))
}

/// Names a candidate carries that the OS reads as naming a credential: `NAME=value`, `${NAME}`, `$NAME`.
fn credential_names(tok: &str) -> Vec<String> {
    let mut out = vec![];
    if let Some((lhs, _)) = tok.split_once('=') {
        out.push(lhs.trim_start_matches('-').to_string());
    }
    let mut rest = tok;
    while let Some(i) = rest.find('$') {
        let after = &rest[i + 1..];
        let after = after.strip_prefix('{').unwrap_or(after);
        let name: String = after
            .chars()
            .take_while(|c| c.is_ascii_alphanumeric() || *c == '_')
            .collect();
        if !name.is_empty() {
            out.push(name);
        }
        rest = &rest[i + 1..];
    }
    out
}

/// One authority-expansion finding: what the installation would hold, where the OS read it, and what the project
/// has already authorised.
fn finding(trigger: &str, demanded: String, from: String, authorised: String) -> Value {
    json!({"trigger": trigger, "demanded": demanded, "derived_from": from, "authorised": authorised})
}

/// **Would this installation expand authority?** (OD-P2-03 requirement 2, and requirement 3's fail-closed rule.)
///
/// The comparison is: what the tool **would hold** — permissions, filesystem/project scope, secret access, host
/// authority, policy-mutation capability and network trust boundary — against what the project **has already
/// authorised** ([`ENVELOPE_SOURCES`]). The authorised side is trusted OS state only. The demanded side is the
/// union of what the descriptor asks for (a request: it can only add) and what the OS derives for itself from the
/// installation's own commands, so a descriptor that declares nothing elevated and installs with `sudo` is an
/// expansion all the same (Contract v3 F4; BC-P2-39's defect).
///
/// The token and pattern lists in `TOOL_POLICY.installation_envelope` are a **kernel floor, never a safety proof**:
/// the OS cannot confine a spawned process, so what it cannot observe is carried by the independent governed
/// security review the non-gated branch also requires. Anything that cannot be evaluated — no envelope in policy,
/// no role permissions, a command the OS cannot read — is an expansion and gates.
///
/// `op`, when given, is the installation's manifest operation: its declared paths are checked against the two an
/// installation writes, so a transaction carrying an `install_tool` operation aimed anywhere else is a policy
/// mutation.
pub fn installation_authority(
    p: &Project,
    descriptor: &Value,
    role: &str,
    dest_rel: &str,
    op: Option<&Value>,
) -> Value {
    let triggers = p.policies().get_list(
        "CHANGE_POLICY",
        "change_classes.tool_installation.authority_expansion_triggers",
    );
    let mut findings: Vec<Value> = vec![];
    let mut undetermined: Vec<String> = vec![];
    let env = p.policies().get("TOOL_POLICY", "installation_envelope");
    if env.as_ref().and_then(|v| v.as_object()).is_none() {
        undetermined.push("TOOL_POLICY.installation_envelope is absent: the authorised envelope cannot be determined, so the installation is treated as an expansion (fail closed)".into());
    }
    let role_classes = role_permissions(p, role);
    if role_classes.is_empty() {
        undetermined.push(format!("TOOL_PERMISSIONS.yaml authorises no permission class for role '{role}': nothing the installation asks for is inside the envelope"));
    }
    let host_classes = envelope_list(p, "host_authority_classes");
    let cred_classes = envelope_list(p, "credential_classes");
    let net_classes = envelope_list(p, "network_classes");
    let priv_tokens = envelope_list(p, "privilege_tokens");
    let host_tokens = envelope_list(p, "host_authority_tokens");
    let scope_flags = envelope_list(p, "host_scope_flags");
    let cred_patterns = envelope_list(p, "credential_patterns");
    let policy_paths = envelope_list(p, "policy_paths");
    let secret_paths = p
        .policies()
        .get_list("SECURITY_POLICY", "secret_path_patterns");

    // --- what the request declares (a request only ever ADDS to the demand)
    let required: Vec<String> = descriptor["required_permission_classes"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let perm_flag = |k: &str| descriptor["permissions"][k].as_bool().unwrap_or(false);

    // --- 1. privilege escalation: a class the acting role does not already hold, or a privilege-raising command
    for c in &required {
        if host_classes.contains(c) || cred_classes.contains(c) {
            continue; // their own triggers below say why they are outside any project authorisation
        }
        if !role_classes.contains(c) {
            findings.push(finding(
                "privilege_escalation",
                format!("permission class {c}"),
                "descriptor.required_permission_classes".into(),
                format!("TOOL_PERMISSIONS.roles.{role} = {role_classes:?}"),
            ));
        }
    }
    if perm_flag("repo_write") && !role_classes.iter().any(|c| c == "WRITE_REPO_SCOPED") {
        findings.push(finding(
            "privilege_escalation",
            "repository writes".into(),
            "descriptor.permissions.repo_write".into(),
            format!("TOOL_PERMISSIONS.roles.{role} = {role_classes:?}"),
        ));
    }

    // --- the installation's own commands, read by the OS itself
    let commands = installation_commands(descriptor);
    if commands.is_empty() {
        undetermined.push("the descriptor carries no command the OS can read (install_command, uninstall_command, health_check.command): what the installation would do outside the project cannot be determined".into());
    }
    // exactly what an installation writes, and nothing else: its own descriptor and the generated tool registry it
    // regenerates. The plugin registry is deliberately NOT here — an installation never writes it, so a command
    // that names it is reaching into trusted OS state that decides which programs the OS executes.
    let own_paths = [dest_rel.to_string(), registry_path(p)];
    let mut endpoints: Vec<(String, String)> = vec![];
    for (whence, argv) in &commands {
        for (i, tok) in argv.iter().enumerate() {
            let at = format!("{whence}[{i}] '{tok}'");
            let bare = tok.rsplit('/').next().unwrap_or(tok).to_ascii_lowercase();
            if priv_tokens.iter().any(|t| t == &bare) {
                findings.push(finding(
                    "privilege_escalation",
                    format!("the installation runs '{bare}'"),
                    at.clone(),
                    "nothing the project has authorised raises privilege for an installed tool"
                        .into(),
                ));
            }
            if host_tokens.iter().any(|t| t == &bare) {
                findings.push(finding(
                    "host_level_authority",
                    format!("the installation runs '{bare}', which acts on the host rather than in the project"),
                    at.clone(),
                    "TOOL_POLICY.installation_envelope.host_authority_tokens (kernel floor): no project authorisation covers host-level authority".into(),
                ));
            }
            if i > 0
                && scope_flags
                    .iter()
                    .any(|f| f == tok || tok.starts_with(&format!("{f}=")))
            {
                findings.push(finding(
                    "host_level_authority",
                    format!("the installation installs with '{tok}' (outside the project)"),
                    at.clone(),
                    "TOOL_POLICY.installation_envelope.host_scope_flags".into(),
                ));
            }
            for name in credential_names(tok) {
                if matches_any_pattern(&name, &cred_patterns) {
                    findings.push(finding(
                        "new_secret_or_credential_access",
                        format!("the installation reads the credential '{name}'"),
                        at.clone(),
                        "TOOL_POLICY.installation_envelope.credential_patterns: the project authorises no new credential access to an installed tool".into(),
                    ));
                }
            }
            for c in token_values(tok) {
                if let Some(h) = endpoint_host(&c) {
                    endpoints.push((h, at.clone()));
                    continue;
                }
                if !c.contains('/') && !c.starts_with('~') {
                    continue; // not a path the OS can read as one
                }
                if leaves_project(&c) {
                    findings.push(finding(
                        "broader_filesystem_or_project_access",
                        format!("the installation reaches '{c}', outside the project"),
                        at.clone(),
                        "the project root, as the path map (REPOSITORY_CONTRACT.yaml) scopes it"
                            .into(),
                    ));
                    continue;
                }
                if secret_paths.iter().any(|g| crate::util::glob_match(g, &c)) {
                    findings.push(finding(
                        "new_secret_or_credential_access",
                        format!("the installation reaches '{c}', a secret path"),
                        at.clone(),
                        "SECURITY_POLICY.secret_path_patterns".into(),
                    ));
                    continue;
                }
                if own_paths.iter().any(|o| o == &c) {
                    continue; // exactly what an installation writes
                }
                if policy_paths.iter().any(|g| crate::util::glob_match(g, &c)) {
                    findings.push(finding(
                        "governance_or_security_policy_mutation",
                        format!("the installation reaches '{c}', governance or security policy"),
                        at.clone(),
                        "TOOL_POLICY.installation_envelope.policy_paths; an installation writes only its own descriptor and the generated tool registry".into(),
                    ));
                    continue;
                }
                let d = p.contract().decide(&c);
                let sens = d.sensitivity();
                if sens == "restricted" || sens == "secret" {
                    findings.push(finding(
                        "new_secret_or_credential_access",
                        format!("the installation reaches '{c}', classified {sens}"),
                        at.clone(),
                        "DATA_SENSITIVITY.yaml + SECURITY_POLICY, through the path map".into(),
                    ));
                } else if !matches!(d.str("mutation").as_str(), "allowed" | "") {
                    findings.push(finding(
                        "broader_filesystem_or_project_access",
                        format!("the installation reaches '{c}', whose mutation the path map records as '{}'", d.str("mutation")),
                        at.clone(),
                        "REPOSITORY_CONTRACT.yaml (the path map)".into(),
                    ));
                }
            }
        }
    }

    // --- 2. host-level authority and 3. credential access, as permission classes
    for c in &required {
        if host_classes.contains(c) {
            findings.push(finding(
                "host_level_authority",
                format!("permission class {c}"),
                "descriptor.required_permission_classes".into(),
                format!("TOOL_POLICY.installation_envelope.host_authority_classes {host_classes:?}: outside any role's authorisation"),
            ));
        }
        if cred_classes.contains(c) {
            findings.push(finding(
                "new_secret_or_credential_access",
                format!("permission class {c}"),
                "descriptor.required_permission_classes".into(),
                format!("TOOL_POLICY.installation_envelope.credential_classes {cred_classes:?}: outside any role's authorisation"),
            ));
        }
    }
    if perm_flag("secrets")
        || !descriptor["credential_scope"]
            .as_str()
            .unwrap_or("")
            .is_empty()
    {
        findings.push(finding(
            "new_secret_or_credential_access",
            format!(
                "declared credential access (credential_scope '{}')",
                descriptor["credential_scope"].as_str().unwrap_or("")
            ),
            "descriptor.permissions.secrets / descriptor.credential_scope".into(),
            "the project authorises no new credential access to an installed tool".into(),
        ));
    }

    // --- 5. governance or security policy mutation: the transaction's own declared paths
    if let Some(op) = op {
        for k in ["path", "registry"] {
            if let Some(v) = op[k].as_str() {
                if !own_paths.iter().any(|o| o == v) {
                    findings.push(finding(
                        "governance_or_security_policy_mutation",
                        format!("the change transaction declares {k} '{v}'"),
                        format!("mutation_manifest[0].{k}"),
                        format!("an installation writes exactly {own_paths:?}"),
                    ));
                }
            }
        }
    }
    for k in ["policy_overrides", "governance_writes", "exceptions"] {
        if descriptor.get(k).map(|v| !v.is_null()).unwrap_or(false) {
            findings.push(finding(
                "governance_or_security_policy_mutation",
                format!("the descriptor declares {k}"),
                format!("descriptor.{k}"),
                "an installed tool mutates no policy".into(),
            ));
        }
    }

    // --- 6. network trust boundary. Ordinary use of an approved registry or an allowlisted service, by a role that
    // already holds a network class, is not by itself elevated (OD-P2-03). A network class demanded with no
    // endpoint the OS can derive is an unrestricted boundary.
    let declared_net: Vec<&String> = required
        .iter()
        .filter(|c| net_classes.contains(c))
        .collect();
    let wants_network = !declared_net.is_empty() || perm_flag("network") || !endpoints.is_empty();
    let authorised_hosts: Vec<String> = network_allowlist(p);
    if wants_network {
        let role_net: Vec<&String> = role_classes
            .iter()
            .filter(|c| net_classes.contains(c))
            .collect();
        if role_net.is_empty() {
            findings.push(finding(
                "new_or_unrestricted_network_trust_boundary",
                "network access".into(),
                if declared_net.is_empty() {
                    "the installation's own commands".into()
                } else {
                    "descriptor.required_permission_classes".to_string()
                },
                format!("TOOL_PERMISSIONS.roles.{role} holds no network class ({net_classes:?})"),
            ));
        }
        if endpoints.is_empty() {
            findings.push(finding(
                "new_or_unrestricted_network_trust_boundary",
                "network access to an endpoint the OS cannot determine".into(),
                "descriptor.required_permission_classes / descriptor.permissions.network".into(),
                format!("the kernel tool registry's approved registries and allowlisted services {authorised_hosts:?}: an unbounded boundary is not one of them"),
            ));
        }
        for (h, at) in &endpoints {
            if !authorised_hosts.iter().any(|a| a.eq_ignore_ascii_case(h)) {
                findings.push(finding(
                    "new_or_unrestricted_network_trust_boundary",
                    format!("network access to '{h}'"),
                    at.clone(),
                    format!("the kernel tool registry's approved registries and allowlisted services {authorised_hosts:?}"),
                ));
            }
        }
    }

    // a finding under a trigger the governed rule does not declare is still an expansion, but it is named as such
    let mut fired: Vec<String> = findings
        .iter()
        .filter_map(|f| f["trigger"].as_str().map(|s| s.to_string()))
        .collect();
    fired.sort();
    fired.dedup();
    let undeclared: Vec<String> = fired
        .iter()
        .filter(|t| !triggers.is_empty() && !triggers.contains(t))
        .cloned()
        .collect();
    let expands = !findings.is_empty() || !undetermined.is_empty();
    json!({
        "expands_authority": expands,
        "triggers_fired": fired,
        "triggers_declared": triggers,
        "triggers_not_declared_by_policy": undeclared,
        "findings": findings,
        "undetermined": undetermined,
        "authorised_sources": ENVELOPE_SOURCES,
        "role": role,
        "role_permission_classes": role_classes,
        "network_endpoints": endpoints.iter().map(|(h, _)| h.clone()).collect::<Vec<_>>(),
        "authorised_network_hosts": authorised_hosts,
    })
}

/// **Which branch of `CHANGE_POLICY.change_classes.tool_installation` applies to this installation, and why**
/// (OD-P2-03 requirements 1, 3 and 5). The governed rule names the non-gated conditions — each mapped to the
/// `TOOL_POLICY.auto_install_conditions` entry that decides it — and the authority-expansion triggers; this
/// function evaluates them and returns the verdict `cit::simulate_inner` records in the transaction's bound impact.
///
/// Fail closed and fail gated: no rule in policy, a condition the policy does not declare (so it was never
/// evaluated), a condition that did not hold, or any authority expansion, all require the human gate.
fn change_decision(p: &Project, prep: &PreparedInstall, op: Option<&Value>) -> Value {
    let pol = p.policies();
    let rule = pol.get("CHANGE_POLICY", "change_classes.tool_installation");
    let envelope = installation_authority(p, &prep.descriptor, &prep.role, &prep.dest_rel(), op);
    let Some(rule) = rule.as_ref().filter(|r| r.is_object()) else {
        return json!({"class": "tool_installation", "rule": "CHANGE_POLICY.change_classes.tool_installation",
            "branch": "gated", "gate_required": true,
            "why": "CHANGE_POLICY declares no governed rule for the tool-installation change class, so no installation is pre-authorised: the transaction is gated by the ordinary radius and trigger rules (fail closed)",
            "conditions": [], "authority_envelope": envelope});
    };
    let declared = pol.get_list("TOOL_POLICY", "auto_install_conditions");
    let mut conditions = vec![];
    let map = rule["non_gated_conditions"]
        .as_object()
        .cloned()
        .unwrap_or_default();
    for (owner_condition, policy_condition) in &map {
        let pc = policy_condition.as_str().unwrap_or("");
        if pc == "authority_envelope" {
            let ok = !envelope["expands_authority"].as_bool().unwrap_or(true);
            conditions.push(json!({"condition": owner_condition, "decided_by": pc, "ok": ok,
                "detail": if ok { "the installation stays inside the project's already-authorised permission and trust envelope".to_string() }
                          else { format!("authority expansion: {:?}{}", envelope["triggers_fired"], if envelope["undetermined"].as_array().map(|a| a.is_empty()).unwrap_or(true) { String::new() } else { format!("; undetermined: {}", envelope["undetermined"]) }) }}));
            continue;
        }
        if !declared.iter().any(|d| d == pc) {
            conditions.push(json!({"condition": owner_condition, "decided_by": pc, "ok": false,
                "detail": format!("TOOL_POLICY.auto_install_conditions does not declare '{pc}', so this condition was never evaluated and cannot hold (fail closed)")}));
            continue;
        }
        match prep
            .checks
            .iter()
            .find(|c| c["condition"].as_str() == Some(pc))
        {
            Some(c) => conditions.push(json!({"condition": owner_condition, "decided_by": pc,
                "ok": c["ok"].as_bool().unwrap_or(false), "detail": c["detail"]})),
            None => conditions.push(
                json!({"condition": owner_condition, "decided_by": pc, "ok": false,
                "detail": format!("'{pc}' was not evaluated for this installation (fail closed)")}),
            ),
        }
    }
    if map.is_empty() {
        conditions.push(json!({"condition": "non_gated_conditions", "decided_by": "CHANGE_POLICY", "ok": false,
            "detail": "the governed rule names no non-gated condition, so nothing is pre-authorised (fail closed)"}));
    }
    let unmet: Vec<String> = conditions
        .iter()
        .filter(|c| !c["ok"].as_bool().unwrap_or(false))
        .filter_map(|c| c["condition"].as_str().map(|s| s.to_string()))
        .collect();
    let gate_required = !unmet.is_empty();
    let why = if !gate_required {
        format!("not gated: every non-gated condition of CHANGE_POLICY.change_classes.tool_installation held ({}), and the installation stays inside the project's already-authorised permission and trust envelope, so under owner decision {} (governed record {}) this installation's change transaction needs no Human Gate",
            conditions.iter().filter_map(|c| c["condition"].as_str()).collect::<Vec<_>>().join(", "),
            rule["owner_decision"].as_str().unwrap_or("OD-P2-03"),
            rule["decision_record"].as_str().unwrap_or("D-0011"))
    } else if envelope["expands_authority"].as_bool().unwrap_or(true) {
        format!("gated: this installation expands authority ({:?}); under owner decision {} a Human Gate is required{}",
            envelope["triggers_fired"],
            rule["owner_decision"].as_str().unwrap_or("OD-P2-03"),
            if unmet.len() > 1 { format!("; unmet conditions {unmet:?}") } else { String::new() })
    } else {
        format!("gated: the non-gated conditions {unmet:?} of CHANGE_POLICY.change_classes.tool_installation did not hold, so this installation is not pre-authorised by owner decision {}",
            rule["owner_decision"].as_str().unwrap_or("OD-P2-03"))
    };
    json!({
        "class": "tool_installation",
        "rule": "CHANGE_POLICY.change_classes.tool_installation",
        "owner_decision": rule["owner_decision"],
        "decision_record": rule["decision_record"],
        "tool_id": prep.tool_id,
        "version": prep.version,
        "installation_sha256": prep.subject,
        "branch": if gate_required { "gated" } else { "not_gated" },
        "gate_required": gate_required,
        "why": why,
        "conditions": conditions,
        "unmet_conditions": unmet,
        "security_review": match &prep.review { Ok(v) => v.clone(), Err(e) => json!({"evidenced": false, "why": e}) },
        "authority_envelope": envelope,
    })
}

/// **What allowed this installation** (OD-P2-03 requirement 4), written into the installed descriptor's `approval`
/// so an auditor traces any installed tool back to it: the owner decision and the governed record that carry the
/// rule, the rule itself, which branch applied and why, the bound independent security review the non-gated branch
/// stands on, and the change transaction that wrote it. An elevated installation is exactly the gated class, so its
/// `approval` also names the gate that authorised it.
fn authorised_by(decision: &Value, change_transaction: &str) -> Value {
    json!({
        "owner_decision": decision["owner_decision"],
        "decision_record": decision["decision_record"],
        "rule": decision["rule"],
        "branch": decision["branch"],
        "why": decision["why"],
        "security_review": decision["security_review"],
        "authority_envelope": {"expands_authority": decision["authority_envelope"]["expands_authority"],
            "triggers_fired": decision["authority_envelope"]["triggers_fired"],
            "authorised_sources": decision["authority_envelope"]["authorised_sources"]},
        "change_transaction": change_transaction,
    })
}

/// [`change_decision`] for an `install_tool` manifest operation: the request is derived again from the descriptor
/// the transaction carries, so `cit::simulate_inner` and CIT-E judge the bytes as they are, never a verdict handed
/// to them. A request that cannot be derived is gated (fail closed).
pub fn installation_change_decision(p: &Project, op: &Value) -> Value {
    let role = op["role"].as_str().unwrap_or("").to_string();
    match prepare_installation(p, op["descriptor"].clone(), &role) {
        Ok(prep) => change_decision(p, &prep, Some(op)),
        Err(e) => {
            json!({"class": "tool_installation", "rule": "CHANGE_POLICY.change_classes.tool_installation",
            "branch": "gated", "gate_required": true,
            "why": format!("gated: the installation request cannot be derived from the descriptor this transaction carries ({}: {}), so no condition can be evaluated (fail closed)", e.code, e.message),
            "conditions": [], "authority_envelope": json!({"expands_authority": true, "undetermined": [e.message]})})
        }
    }
}

/// The manifest operation of an installation's change transaction: what CIT-P simulates and CIT-E applies
/// (`cit::apply_op` → [`apply_installation`]). The approval of the transaction binds it (its content digest), so the
/// descriptor as given, the installing role and whether the install command runs are all part of what is approved.
fn installation_op(p: &Project, prep: &PreparedInstall, execute: bool) -> Value {
    json!({"op": "install_tool", "tool_id": prep.tool_id, "path": prep.dest_rel(), "registry": registry_path(p),
        "descriptor": prep.descriptor, "subject_sha256": prep.subject, "role": prep.role, "execute": execute})
}

fn installation_proposal(p: &Project, prep: &PreparedInstall, execute: bool) -> String {
    let approval = if prep.all_ok {
        "Every TOOL_POLICY.auto_install_conditions entry holds, so no separate installation gate is asked; this transaction is the installation's change control (Contract v3 K3). Under CHANGE_POLICY.change_classes.tool_installation (owner decision OD-P2-03, governed record D-0011) it needs a Human Gate only if the installation expands authority; the simulated impact records which branch applied and why (impact.change_class)."
    } else {
        "Its installation is approved separately, by the Human Decision Gate raised for exactly this installation subject (BC-P2-41, Contract v3 F4); this transaction is the installation's change control (Contract v3 K3) and does not approve the installation. Under CHANGE_POLICY.change_classes.tool_installation (owner decision OD-P2-03, governed record D-0011) this transaction needs its own Human Gate unless every non-gated condition holds and the installation stays inside the project's already-authorised envelope; the simulated impact records which branch applied and why (impact.change_class)."
    };
    format!(
        "Install tool {} {} for role {}: write its installation descriptor to {} and regenerate {} (installation subject sha256 {}; install command {}). {approval}",
        prep.tool_id,
        prep.version,
        prep.role,
        prep.dest_rel(),
        registry_path(p),
        prep.subject,
        if execute {
            format!("RUN at execution: {}", prep.descriptor["install_command"])
        } else {
            "not run (--execute was not given)".to_string()
        }
    )
}

/// The Human Decision Gate package for an installation whose auto-install conditions did not all hold. It names the
/// installation's change transaction and that transaction's own gate: each approval names the other, and neither
/// answer stands in for the other (R4-O1, as INT3-O1 for a registration).
fn installation_gate_package(prep: &PreparedInstall, change: &Value, execute: bool) -> Value {
    let change_text = format!(
        " The descriptor is written only by change transaction {} (CIT-P simulated automatically: impact radius {}, effective triggers {}), whose own gate {} approves the change itself: answering this gate approves the installation, not the change.",
        change["cit"].as_str().unwrap_or("?"),
        change["radius"].as_str().unwrap_or("?"),
        change["effective_triggers"],
        change["human_gate"].as_str().unwrap_or("(none required)"),
    );
    let mut subject_v = json!({"kind": "tool-installation", "id": prep.tool_id, "version": prep.version, "sha256": prep.subject});
    subject_v["change_transaction"] = json!({"cit": change["cit"], "human_gate": change["human_gate"], "binding_sha256": change["binding_sha256"]});
    json!({
        "question": format!("Approve installation of tool {} {}? Automatic installation conditions failed: {}", prep.tool_id, prep.version, prep.failed.join(", ")),
        "why_now": "a task requires a capability that is not available",
        "current_state": "tool not installed",
        "options": [
            {"id": "A", "description": format!("approve installation of exactly this descriptor (installation {})", prep.subject)},
            {"id": "B", "description": "reject; find an alternative"}
        ],
        "impact": format!("adds an executable capability to the environment: install {} / uninstall {}; licence {}; permission classes {:?}{}",
            prep.descriptor["install_command"], prep.descriptor["uninstall_command"], prep.license, prep.required,
            if execute { " (the install command runs when the change executes)" } else { "" }) + &change_text,
        "reversibility": if prep.descriptor["reversible"].as_bool().unwrap_or(false) { "reversible" } else { "irreversible or unknown" },
        "recommendation": "B unless the tool is essential",
        "confidence": 0.6,
        "trigger": "tool_install",
        "impact_radius": "R2",
        "subject": subject_v,
    })
}

/// **The one writer of a tool installation** (R4-O1), reached only from [`apply_installation`], i.e. only from the
/// execution of the installation's change transaction. It composes the tools directory itself and asks the §6
/// acquisition sink immediately before writing (`OWNER-DECISION-0006` §6 bullet 5, `AR31-N1`: the derived census
/// finds every writer of a capability registry and requires this call in each). Returns the descriptor as written,
/// the health result, the failure-memory record and the install command's result.
fn install_write(
    p: &Project,
    prep: &PreparedInstall,
    approval: &Value,
    execute: bool,
    change_transaction: &str,
) -> Result<(Value, Value, Value, Value)> {
    crate::srr::plugins::guard_acquisition_below_floor("tools install")?;
    let mut desc = prep.descriptor.clone();
    if let Some(o) = desc.as_object_mut() {
        for k in ["human_gate", "registration_gate", "approval_gate"] {
            o.remove(k);
        }
    }
    let mut approval = approval.clone();
    approval["change_transaction"] = json!(change_transaction);
    desc["status"] = json!("active");
    desc["installed_by"] = json!(p.session_id);
    desc["installed_at"] = json!(now_iso());
    desc["installation_sha256"] = json!(prep.subject);
    desc["approval"] = approval;
    if let Ok(v) = &prep.review {
        desc["security_review_evidence"] = v.clone();
    }
    desc["type"] = desc.get("type").cloned().unwrap_or(json!("library"));
    desc["approved_roles"] = desc
        .get("approved_roles")
        .cloned()
        .unwrap_or(json!([prep.role]));
    desc["capabilities"] = desc.get("capabilities").cloned().unwrap_or(json!([]));
    desc["name"] = desc.get("name").cloned().unwrap_or(json!(prep.tool_id));
    let mut exec_result = Value::Null;
    if execute {
        let cmd: Vec<String> = desc["install_command"]
            .as_array()
            .cloned()
            .unwrap_or_default()
            .iter()
            .filter_map(|x| x.as_str().map(|s| s.to_string()))
            .collect();
        if cmd.is_empty() {
            return Err(GovError::new(
                "USAGE",
                "--execute needs a non-empty install_command",
            ));
        }
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
        .validate("tool", &desc, &format!("({})", prep.tool_id))?;
    crate::util::write_yaml(
        &p.overlay_dir()
            .join("tools")
            .join(format!("{}.yaml", prep.tool_id)),
        &desc,
    )?;
    let health = health_one(p, &desc);
    let failure = record_health_failure(p, &desc, &health, "tools install");
    generate_registry(p)?;
    Ok((desc, health, failure, exec_result))
}

/// **CIT-E side of a tool installation** (the `install_tool` manifest operation; R4-O1). The request is derived
/// again from the descriptor as the transaction carries it ([`prepare_installation`]: policy checks, conditions,
/// the governed security review) and must be exactly the subject the transaction's approval binds; where an
/// auto-install condition did not hold, the installation's own approval (a presented, owner-answered gate raised for
/// exactly this subject) is re-verified here, so no route into CIT-E — `gov tools install`, `gov cit execute` or a
/// hand-proposed transaction carrying this operation — writes an installation the owner did not approve. Returns the
/// paths it wrote.
pub fn apply_installation(p: &Project, op: &Value, change_transaction: &str) -> Result<Value> {
    let role = op["role"].as_str().unwrap_or("").to_string();
    let prep = prepare_installation(p, op["descriptor"].clone(), &role)?;
    let want = op["subject_sha256"].as_str().unwrap_or("");
    if prep.subject != want || op["tool_id"].as_str() != Some(prep.tool_id.as_str()) {
        return Err(GovError::new("TOOL_INSTALLATION_STALE", format!("change transaction {change_transaction} installs tool {:?} with subject {want}, but the descriptor it carries now gives tool '{}' subject {}: the installation changed after the transaction was proposed and approved; nothing is written — install it again (`gov tools install`) for a new request", op["tool_id"], prep.tool_id, prep.subject)).with_details(json!({"cit": change_transaction, "approved_subject": want, "current_subject": prep.subject})));
    }
    // the acting role must itself hold installation authority: `gov cit execute` is not a way around
    // TOOL_PERMISSIONS.install_authority_roles (D-0007 rule 2)
    let install_roles = install_authority_roles(p);
    if !install_roles.is_empty() && !install_roles.iter().any(|r| r == &p.role) {
        return Err(GovError::new(
            "AUTHORITY_DENIED",
            format!(
                "role '{}' is not in TOOL_PERMISSIONS.install_authority_roles {install_roles:?}",
                p.role
            ),
        )
        .with_details(
            json!({"operation": "install_tool", "role": p.role, "cit": change_transaction}),
        ));
    }
    // **OD-P2-03 at the instant of the write.** The branch is derived again here, from the descriptor as the
    // transaction carries it and trusted OS state as it stands now, and an installation that expands authority is
    // written only by a transaction a human gate approved. So a transaction pre-authorised when it was simulated,
    // whose envelope has since changed (a role's permission classes narrowed, a path reclassified, the envelope
    // policy tightened), does not slip through, and neither does a hand-proposed `install_tool` transaction.
    let decision = change_decision(p, &prep, Some(op));
    if decision["gate_required"].as_bool().unwrap_or(true) {
        let gated = RecordStore::load(&p.root)
            .get(change_transaction)
            .map(|c| c.data["approval"]["gate"].is_string())
            .unwrap_or(false);
        if !gated {
            return Err(GovError::new("TOOL_INSTALL_ELEVATED", format!("change transaction {change_transaction} would install tool '{}', which under {} ({}) needs a Human Gate — {} — but no gate approved this transaction; nothing is written. Re-simulate the transaction (`gov cit simulate {change_transaction}`) to raise the gate, or install again for a new request", prep.tool_id, decision["rule"].as_str().unwrap_or("CHANGE_POLICY.change_classes.tool_installation"), decision["owner_decision"].as_str().unwrap_or("OD-P2-03"), decision["why"].as_str().unwrap_or("")))
                .with_details(json!({"cit": change_transaction, "tool_id": prep.tool_id, "change_class": decision})));
        }
    }
    let mut approval = json!({"mode": "autonomous", "conditions": "every TOOL_POLICY.auto_install_conditions entry held",
        "authorised_by": authorised_by(&decision, change_transaction)});
    if !prep.all_ok {
        match approval_for_subject(p, "tool-installation", &prep.subject, &prep.cited) {
            SubjectApproval::Approved(a) => {
                approval = json!({"mode": "human_gate", "gate": a.gate, "option": a.option, "by_kind": a.by_kind, "answered_by": a.answered_by, "decision": a.decision, "installation_sha256": prep.subject, "failed_conditions": prep.failed,
                    "authorised_by": authorised_by(&decision, change_transaction)});
            }
            other => {
                let (gate, state) = match &other {
                    SubjectApproval::Declined { gate, .. } => (json!(gate), "DECLINED"),
                    SubjectApproval::Pending { gate } => (json!(gate), "PENDING"),
                    _ => (Value::Null, "NONE"),
                };
                return Err(GovError::new("TOOL_NOT_APPROVED", format!("change transaction {change_transaction} would install tool '{}', whose automatic installation conditions do not all hold ({}), but no presented, owner-answered gate raised for exactly this installation authorises it (gate {gate}, {state}); an approved change is not an installation approval (BC-P2-41, Contract v3 F4) — nothing is written", prep.tool_id, prep.failed.join(", "))).with_details(json!({"cit": change_transaction, "tool_id": prep.tool_id, "installation_sha256": prep.subject, "installation_gate": gate, "installation_gate_state": state, "failed_conditions": prep.failed})));
            }
        }
    }
    let execute = op["execute"].as_bool().unwrap_or(false);
    let (desc, health, failure, exec_result) =
        install_write(p, &prep, &approval, execute, change_transaction)?;
    Ok(
        json!({"tool_id": prep.tool_id, "touched": [prep.dest_rel(), registry_path(p)], "approval": approval,
        "descriptor": desc, "health": health, "failure_memory": failure, "executed": execute, "exec_result": exec_result}),
    )
}

/// Install/register a tool only when every TOOL_POLICY auto-install condition holds, or when a presented,
/// owner-answered gate raised for exactly this installation approves it; otherwise raise that gate (a decline ends
/// the request; a pending gate is returned, never duplicated).
///
/// **An installation is also a material governance and security change** (R4-O1, the path adjacent to INT3-O1;
/// Contract v3 K3 "auto-trigger for material security, governance/policy"; F4 "elevated permissions reference
/// authoritative gate/decision"; framework §47-48 "the human should not need to type /impact"). The descriptor lives
/// under `governance/project/tools/`, which the kernel-floor materiality classifies exactly as it classifies a plugin
/// descriptor, so the OS itself proposes the installation's change transaction (`cit::propose_installation`: CIT-P,
/// simulated automatically) and the descriptor is written **only by that transaction's execution** (CIT-E,
/// [`apply_installation`]: snapshot, verification, index refresh, commit or rollback, per-path writes recorded and
/// sealed).
///
/// **Whether that transaction needs the owner's gate is `OD-P2-03`** (product owner, 2026-09-20; governed record
/// `D-0011`; the rule in policy is `CHANGE_POLICY.change_classes.tool_installation` with
/// `TOOL_POLICY.installation_envelope`). It does **not** when the tool is authenticated and pinned, independently
/// governed-reviewed, registered, reversible **and** stays entirely inside the project's already-authorised
/// permission and trust envelope ([`installation_authority`]); it **does** when the installation expands authority —
/// privilege escalation, broader filesystem or project access, new secret or credential access, host-level
/// authority, governance or security-policy mutation, or a new or unrestricted network trust boundary. Ordinary
/// network use already authorised by project or tool policy is not by itself elevated. Anything that cannot be
/// evaluated is gated (fail closed). Every installation is recorded either way, and the transaction states which
/// branch applied and why ([`change_decision`], recorded as `impact.change_class`).
///
/// Where an auto-install condition failed there are two approvals, each for what it approves and each naming the
/// other; neither answer stands in for the other, and the worker never hand-files a transaction: repeating
/// `gov tools install` once they are answered approves and executes it. An installation made inside a claimed task
/// therefore closes on the transaction's recorded writes (task close step 10a), like any other governed change.
pub fn install(p: &Project, descriptor: Value, role: &str, execute: bool) -> Result<Value> {
    crate::orchestration::control::guard_write(p, "tools install")?;
    // **`OWNER-DECISION-0006` §6 bullet 5, at the second acquisition primitive** (`AR31-N1`).
    //
    // This function installs a capability — writing a descriptor into `governance/project/tools/` and optionally
    // running its install command — and never reached `plugins::guard_acquisition`, which the census named as the
    // sole sink for bullet 5. Below floor the operation-level guard above already refuses it, so there was no
    // live bypass; what was missing was the effect-level control, which is the one that survives a future
    // acquisition path taking no `Project`. The derived census (`breakglass::SECTION_6_SIGNATURES`) now finds
    // every writer of a capability registry and requires this call in each; the write itself is in
    // [`install_write`], which asks the sink again at the instant of its write.
    crate::srr::plugins::guard_acquisition_below_floor("tools install")?;
    crate::authority::require(p, "install_tool")?;
    // the conditions are evaluated for the ACTING role: a role named on the command line is caller input (T5) and
    // cannot lend another role's install authority or permission classes (D-0007 rule 2)
    if role != p.role {
        return Err(GovError::new(
            "ROLE_CONFLICT",
            format!("`tools install --role {role}` names a role other than the acting role '{}'; installation authority and permission classes are those of the acting role (a caller-supplied role is a request, not authority)", p.role),
        )
        .with_details(json!({"acting_role": p.role, "requested_role": role})));
    }
    let prep = prepare_installation(p, descriptor, role)?;
    let subject = prep.subject.clone();
    let tool_id = prep.tool_id.clone();
    // OD-P2-03: which branch this installation is on, and why, reported with every answer the command gives — the
    // same verdict CIT-P records in the transaction's bound impact and CIT-E re-derives at the write.
    let decision = change_decision(p, &prep, Some(&installation_op(p, &prep, execute)));
    let common = |mut v: Value| -> Value {
        v["installation_sha256"] = json!(subject);
        v["checks"] = json!(prep.checks);
        v["change_class"] = decision.clone();
        v
    };
    // --- 1. the installation's own approval (BC-P2-41; Contract v3 F4), asked only when a condition failed
    let mut approval = json!({"mode": "autonomous", "conditions": "every TOOL_POLICY.auto_install_conditions entry held"});
    if !prep.all_ok {
        match approval_for_subject(p, "tool-installation", &subject, &prep.cited) {
            SubjectApproval::Approved(a) => {
                approval = json!({"mode": "human_gate", "gate": a.gate, "option": a.option, "by_kind": a.by_kind, "answered_by": a.answered_by, "decision": a.decision, "installation_sha256": subject, "failed_conditions": prep.failed});
            }
            SubjectApproval::Declined { gate, option } => {
                // the request ends here, and so does its change transaction
                let closed = crate::cit::close_host_requests(
                    p,
                    "install_tool",
                    "tool_id",
                    &tool_id,
                    Some(&subject),
                    &format!("the installation approval of this request was declined (gate {gate}, answer '{option}')"),
                );
                return Ok(common(
                    json!({"installed": false, "declined": true, "human_gate": gate, "answer": option, "change_transactions_closed": closed,
                    "reason": format!("the human declined gate {gate} for exactly this installation; the request ends here (a changed installation is a new request; `gov gate revoke {gate}` withdraws the refusal)")}),
                ));
            }
            SubjectApproval::Pending { gate } => {
                let open = crate::cit::host_transactions(p, "install_tool", &subject)
                    .into_iter()
                    .find(|(_, st)| crate::cit::is_open_status(st))
                    .map(|(c, _)| crate::capabilities::governance::change_view(p, &c))
                    .unwrap_or(Value::Null);
                return Ok(common(
                    json!({"installed": false, "human_gate": gate, "state": "PENDING", "change_transaction": open,
                    "reason": format!("gate {gate} for exactly this installation is raised and not answered yet: `gov gate present {gate}`, the product owner answers it through the human channel{}, then run the same install again", open["human_gate"].as_str().map(|g| format!(" (and gate {g} of the installation's change transaction {})", open["cit"].as_str().unwrap_or("?"))).unwrap_or_default())}),
                ));
            }
            SubjectApproval::None { not_honoured } => {
                // a new request: first its change transaction (CIT-P, simulated automatically), then the
                // installation gate, which names the transaction and its gate
                let c = crate::cit::propose_installation(
                    p,
                    installation_op(p, &prep, execute),
                    &installation_proposal(p, &prep, execute),
                    &tool_id,
                    &subject,
                )?;
                let cit = c["id"].as_str().unwrap_or("").to_string();
                let change = crate::capabilities::governance::change_view(p, &cit);
                let g =
                    gates::create_system(p, installation_gate_package(&prep, &change, execute))?;
                let gid = g["id"].as_str().unwrap_or("").to_string();
                crate::cit::note_host_gate(
                    p,
                    &cit,
                    &gid,
                    "the installation's own approval (BC-P2-41, Contract v3 F4) is this gate, raised for exactly the installation subject this transaction carries; this transaction's own gate approves the change",
                    "tools install",
                );
                return Ok(common(
                    json!({"installed": false, "human_gate": gid, "state": "RAISED", "gates_not_honoured": not_honoured, "change_transaction": change,
                    "reason": format!("an automatic installation condition failed ({}), so the installation needs a presented, owner-answered gate raised for exactly it; and an installation is a material governance and security change, carried out by change transaction {cit} (proposed and simulated by the OS){}. Present the gate(s) returned here, have the product owner answer them through the human channel, then run the same install again", prep.failed.join(", "),
                        match change["human_gate"].as_str() {
                            Some(g) => format!(" whose own gate {g} approves the change ({})", decision["why"].as_str().unwrap_or("")),
                            None => format!(" which needs no gate of its own ({})", decision["why"].as_str().unwrap_or("")),
                        })}),
                ));
            }
        }
    }
    // --- 2. change control: the descriptor is written only by its change transaction's execution
    // an installation of exactly this subject, approved the same way, already in force: nothing changes
    let dest = p
        .overlay_dir()
        .join("tools")
        .join(format!("{tool_id}.yaml"));
    if let Ok(cur) = read_yaml(&dest) {
        if cur["installation_sha256"].as_str() == Some(subject.as_str())
            && cur["approval"]["mode"] == approval["mode"]
            && cur["approval"]["gate"] == approval["gate"]
            && cur["approval"]["change_transaction"].is_string()
        {
            return Ok(common(
                json!({"installed": true, "unchanged": true, "tool_id": tool_id, "path": prep.dest_rel(), "approval": cur["approval"], "installation_subject": prep.subject_doc,
                "change_transaction": cur["approval"]["change_transaction"].as_str().map(|c| crate::capabilities::governance::change_view(p, c)).unwrap_or(Value::Null),
                "reason": "this installation is already in force as written by its change transaction: nothing to change"}),
            ));
        }
    }
    let linked = crate::cit::host_transactions(p, "install_tool", &subject);
    let cit = match linked.iter().find(|(_, st)| crate::cit::is_open_status(st)) {
        Some((c, _)) => {
            // the install command is part of what the transaction's approval binds, so a request that changes it is
            // a different request: it cannot borrow this transaction's approval
            let store = RecordStore::load(&p.root);
            let recorded = store
                .get(c)
                .map(|r| {
                    r.data["mutation_manifest"][0]["execute"]
                        .as_bool()
                        .unwrap_or(false)
                })
                .unwrap_or(execute);
            if recorded != execute {
                return Ok(common(
                    json!({"installed": false, "change_transaction": crate::capabilities::governance::change_view(p, c),
                    "reason": format!("the open change transaction {c} of exactly this installation was proposed {} and its approval binds that; run `gov tools install` {} again, or `gov cit reject {c}` and start a new request", if recorded { "with --execute" } else { "without --execute" }, if recorded { "with --execute" } else { "without --execute" })}),
                ));
            }
            c.clone()
        }
        None => {
            if let Some((c, st)) = linked.first().filter(|(_, st)| st == "REJECTED") {
                let v = crate::capabilities::governance::change_view(p, c);
                return Ok(common(
                    json!({"installed": false, "declined": true, "human_gate": v["human_gate"], "change_transaction": v, "approval": approval,
                    "reason": format!("the change transaction {c} of exactly this installation is {st} (declined through its gate, or withdrawn with the installation approval): the request ends here. A changed descriptor is a new request; withdrawing the installation approval (`gov gate revoke <gate>`) and installing again raises a new one")}),
                ));
            }
            let c = crate::cit::propose_installation(
                p,
                installation_op(p, &prep, execute),
                &installation_proposal(p, &prep, execute),
                &tool_id,
                &subject,
            )?;
            c["id"].as_str().unwrap_or("").to_string()
        }
    };
    let change = crate::capabilities::governance::change_view(p, &cit);
    match crate::cit::host_gate_state(p, &cit) {
        crate::cit::GateState::Pending(g) => Ok(common(
            json!({"installed": false, "human_gate": g, "state": if linked.iter().any(|(c, _)| c == &cit) { "PENDING" } else { "RAISED" }, "change_transaction": change, "approval": approval,
            "reason": format!("the installation's change transaction {cit} (proposed and simulated by the OS: Contract v3 K3) waits on its own gate {g}; present it, have the product owner answer it through the human channel, then run the same install again")}),
        )),
        crate::cit::GateState::Declined(g) => Ok(common(
            json!({"installed": false, "declined": true, "human_gate": g, "change_transaction": crate::capabilities::governance::change_view(p, &cit), "approval": approval,
            "reason": format!("gate {g} of the installation's change transaction {cit} was declined: the change is refused and the request ends here")}),
        )),
        crate::cit::GateState::Ready => {
            let executed = crate::cit::execute_host_op(p, &cit, "install_tool", "install_tool")?;
            let d = read_yaml(&dest).unwrap_or(Value::Null);
            Ok(common(
                json!({"installed": true, "tool_id": tool_id, "path": prep.dest_rel(), "approval": d["approval"], "installation_subject": prep.subject_doc,
                "executed": execute, "health": health_one(p, &d), "registered_at": prep.dest_rel(),
                "change_transaction": crate::capabilities::governance::change_view(p, &cit), "execution": executed}),
            ))
        }
    }
}

/// WS-6 IP-3: a failing tool health check leaves a durable tool-failure record in failure memory (idempotent per
/// tool/version/code; a governed write that is reported `not_recorded` under FREEZE_WRITES/PAUSE). `Null` when the
/// check did not fail.
fn record_health_failure(p: &Project, tool: &Value, health: &Value, operation: &str) -> Value {
    if health["ok"].as_bool() != Some(false) {
        return Value::Null;
    }
    let version = tool
        .get("version_pin")
        .and_then(|v| v.as_str())
        .filter(|s| !s.is_empty())
        .or_else(|| tool.get("version").and_then(|v| v.as_str()))
        .unwrap_or("")
        .to_string();
    let message = health
        .get("error")
        .and_then(|v| v.as_str())
        .map(String::from)
        .unwrap_or_else(|| {
            format!(
                "health check {} exited {} (expected {}): {}",
                tool["health_check"]["command"],
                health["exit"],
                tool["health_check"]["expect_exit"].as_i64().unwrap_or(0),
                health["stderr"].as_str().unwrap_or("")
            )
        });
    crate::memory::failures::record_tool_failure(
        p,
        &crate::memory::failures::ToolFailure {
            tool_kind: "tool".into(),
            tool_id: tool["tool_id"].as_str().unwrap_or("").to_string(),
            version,
            code: "TOOL_HEALTH_FAILED".into(),
            message,
            operation: operation.to_string(),
            affected: vec![],
        },
        true,
    )
    .to_value()
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

/// Run the health check of every active tool; each failing check is recorded in failure memory (WS-6 IP-3).
pub fn health(p: &Project) -> Vec<Value> {
    let mut tools = kernel_tools(p);
    tools.extend(project_tools(p));
    tools
        .iter()
        .filter(|t| t["status"].as_str() == Some("active"))
        .map(|t| {
            let mut h = health_one(p, t);
            let f = record_health_failure(p, t, &h, "tools health");
            if !f.is_null() {
                h["failure_memory"] = f;
            }
            h
        })
        .collect()
}

pub fn check_permission(p: &Project, role: &str, perm: &str) -> bool {
    role_permissions(p, role).iter().any(|x| x == perm)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::records::new_record;
    use crate::t2::Binding;

    fn verified() -> Binding {
        Binding::Verified {
            key_id: "k".into(),
            operation: "task close".into(),
            at: "2026-09-19T00:00:00Z".into(),
        }
    }

    fn review(extra: Value) -> Record {
        let mut f = json!({"task": "TASK-0007", "session": "S-sec", "role": "security-engineer", "outcome": "success",
            "security_review": {"tool_id": "TOOL-X", "version": "1.2.3", "verdict": "passed"}});
        for (k, v) in extra.as_object().cloned().unwrap_or_default() {
            f[k] = v;
        }
        new_record("report", "RPT-0007", "security review of TOOL-X", f)
    }

    fn task(class: &str, closed_by: &str) -> Record {
        new_record(
            "task",
            "TASK-0007",
            "review TOOL-X",
            json!({"class": class, "task_status": "DONE", "closed_by_report": closed_by}),
        )
    }

    #[test]
    fn a_governed_review_of_this_tool_and_version_by_another_author_is_evidence() {
        let t = task("security", "RPT-0007");
        let ok = review_verdict(
            &review(json!({})),
            &verified(),
            Some(&t),
            "TOOL-X",
            "1.2.3",
            "S-installer",
            "tooling-engineer",
        );
        assert_eq!(ok.unwrap()["reviewer_role"], "security-engineer");
    }

    #[test]
    fn anything_short_of_that_is_not_evidence() {
        let t = task("security", "RPT-0007");
        let v =
            |r: &Record,
             b: &Binding,
             t: Option<&Record>,
             id: &str,
             ver: &str,
             s: &str,
             role: &str| { review_verdict(r, b, t, id, ver, s, role).unwrap_err() };
        let rec = review(json!({}));
        // not OS-written as it stands
        assert!(v(
            &rec,
            &Binding::Unsealed,
            Some(&t),
            "TOOL-X",
            "1.2.3",
            "S-i",
            "tooling-engineer"
        )
        .contains("T2"));
        // another tool, another version
        assert!(v(
            &rec,
            &verified(),
            Some(&t),
            "TOOL-Y",
            "1.2.3",
            "S-i",
            "tooling-engineer"
        )
        .contains("reviews tool"));
        assert!(v(
            &rec,
            &verified(),
            Some(&t),
            "TOOL-X",
            "1.2.4",
            "S-i",
            "tooling-engineer"
        )
        .contains("reviews tool"));
        // self-attested: the installing session or role wrote it
        assert!(v(
            &rec,
            &verified(),
            Some(&t),
            "TOOL-X",
            "1.2.3",
            "S-sec",
            "tooling-engineer"
        )
        .contains("self-attested"));
        assert!(v(
            &rec,
            &verified(),
            Some(&t),
            "TOOL-X",
            "1.2.3",
            "S-i",
            "security-engineer"
        )
        .contains("self-attested"));
        // not a security task, not the report that closed it, no verdict, a failing verdict, another record type
        let doc = task("documentation", "RPT-0007");
        assert!(v(
            &rec,
            &verified(),
            Some(&doc),
            "TOOL-X",
            "1.2.3",
            "S-i",
            "tooling-engineer"
        )
        .contains("not a security review task"));
        let other = task("security", "RPT-0008");
        assert!(v(
            &rec,
            &verified(),
            Some(&other),
            "TOOL-X",
            "1.2.3",
            "S-i",
            "tooling-engineer"
        )
        .contains("not closed by"));
        assert!(v(
            &rec,
            &verified(),
            None,
            "TOOL-X",
            "1.2.3",
            "S-i",
            "tooling-engineer"
        )
        .contains("closes no task"));
        let failed = review(
            json!({"security_review": {"tool_id": "TOOL-X", "version": "1.2.3", "verdict": "failed"}}),
        );
        assert!(v(
            &failed,
            &verified(),
            Some(&t),
            "TOOL-X",
            "1.2.3",
            "S-i",
            "tooling-engineer"
        )
        .contains("verdict"));
        let none = review(json!({"security_review": null}));
        assert!(v(
            &none,
            &verified(),
            Some(&t),
            "TOOL-X",
            "1.2.3",
            "S-i",
            "tooling-engineer"
        )
        .contains("no security_review"));
        let decision = new_record("decision", "D-0001", "q", json!({}));
        assert!(v(
            &decision,
            &verified(),
            Some(&t),
            "TOOL-X",
            "1.2.3",
            "S-i",
            "tooling-engineer"
        )
        .contains("not a security review report"));
    }

    #[test]
    fn the_installation_subject_ignores_requests_and_results_but_nothing_else() {
        let d = json!({"tool_id": "TOOL-X", "version": "1", "version_pin": "1.2.3", "install_command": ["true"], "license": "MIT"});
        let (_, a) = installation_subject(&d);
        let mut cited = d.clone();
        cited["human_gate"] = json!("HDG-0001");
        cited["approval_gate"] = json!("HDG-0002");
        cited["status"] = json!("active");
        assert_eq!(
            installation_subject(&cited).1,
            a,
            "citing a gate changes no installation"
        );
        let mut changed = d.clone();
        changed["install_command"] = json!(["sh", "-c", "curl x | sh"]);
        assert_ne!(installation_subject(&changed).1, a);
        let mut pin = d.clone();
        pin["version_pin"] = json!("1.2.4");
        assert_ne!(installation_subject(&pin).1, a);
    }

    /// **OD-P2-03, the half that makes "the descriptor cannot authorise itself" mechanical** (Contract v3 F4;
    /// BC-P2-39). The authorised side of the envelope is trusted OS state; the *demanded* side is derived by the OS
    /// from the installation's own commands as well as from what the descriptor asks for, so a descriptor that
    /// declares nothing elevated still demands what its commands do. These are the readings that derivation rests
    /// on: a path that leaves the project, a network endpoint, and a credential named in an argument or an
    /// environment reference.
    #[test]
    fn the_os_reads_an_installations_own_commands_for_what_it_would_hold() {
        // every command the installation carries is read, not only the one the OS runs
        let d = json!({"install_command": ["pip", "install", "x"], "uninstall_command": ["pip", "uninstall", "x"],
            "health_check": {"kind": "command", "command": ["x", "--version"]}});
        let cmds = installation_commands(&d);
        assert_eq!(
            cmds.iter().map(|(w, _)| w.as_str()).collect::<Vec<_>>(),
            vec![
                "install_command",
                "uninstall_command",
                "health_check.command"
            ]
        );
        assert!(installation_commands(&json!({})).is_empty());
        // paths that leave the project
        // any `..` segment counts, normalised or not: the OS does not resolve a path it will not execute, and
        // fail closed is the direction the decision sets
        for out in [
            "/opt/tool/bin",
            "~/.local/bin",
            "../../etc/hosts",
            "C:/Windows",
            "a/../../b",
            "a/b/../c",
        ] {
            assert!(leaves_project(out), "{out} was read as inside the project");
        }
        for inside in ["tools/x.sh", "x", "./a/b", "a/b/c"] {
            assert!(
                !leaves_project(inside),
                "{inside} was read as outside the project"
            );
        }
        // a flag hides its value, and the value is read too
        assert_eq!(
            token_values("--prefix=/opt/x"),
            vec!["--prefix=/opt/x", "/opt/x"]
        );
        // network endpoints, with user and port stripped
        assert_eq!(
            endpoint_host("https://me@pypi.org:443/simple/x"),
            Some("pypi.org".into())
        );
        assert_eq!(
            endpoint_host("HTTP://Example.INVALID/x"),
            Some("example.invalid".into())
        );
        assert_eq!(endpoint_host("tools/x.sh"), None);
        // credentials named in an argument or an environment reference
        let names = credential_names("--token=${GITHUB_TOKEN}");
        assert!(names.contains(&"token".to_string()), "{names:?}");
        assert!(names.contains(&"GITHUB_TOKEN".to_string()), "{names:?}");
        let pats = vec!["*TOKEN*".to_string(), "*PASSWORD*".to_string()];
        assert!(matches_any_pattern("GITHUB_TOKEN", &pats));
        assert!(matches_any_pattern("token", &pats));
        assert!(!matches_any_pattern("count", &pats));
    }
}
