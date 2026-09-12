//! Capability/plugin supply-chain boundary (framework §28–32, TOOL_POLICY.plugins; verifier H-N2).
//! No executable capability runs merely because a descriptor exists. Before a plugin is used by any path
//! (`capabilities invoke`, the indexer, retrieval, benchmarks, code intelligence) it must be: a schema-valid descriptor
//! with a stable identity and version pin; registered in the generated Tool/Capability Registry; healthy (executable
//! resolvable); authorised for the acting role (authority floor, approved_roles, permission classes, elevated
//! permissions only through a registration gate); and pinned by content hash when a pin is declared or observed.
//! Every refusal is a typed, auditable error and the plugin is listed as `denied`/`rejected`, never silently skipped.
use super::host::discover_all;
use super::protocol::PluginDescriptor;
use crate::util::{now_iso, read_json, sha256_hex, write_json};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Default, serde::Serialize)]
pub struct PluginSet {
    /// Descriptors the acting role may execute (validated, registered, healthy, pinned, authorised).
    pub usable: Vec<PluginDescriptor>,
    /// Valid descriptors the acting role may not execute (reason recorded).
    pub denied: Vec<Value>,
    /// Descriptors that failed schema validation (never executable).
    pub rejected: Vec<Value>,
}

impl PluginSet {
    pub fn find(
        &self,
        capability: &str,
        language: Option<&str>,
        plugin_id: Option<&str>,
    ) -> Option<PluginDescriptor> {
        super::host::find(&self.usable, capability, language, plugin_id)
    }
    /// Why a declared plugin id is not usable (denied/rejected), for typed errors.
    pub fn refusal(&self, plugin_id: &str) -> Option<GovError> {
        if let Some(d) = self
            .denied
            .iter()
            .find(|d| d["plugin_id"].as_str() == Some(plugin_id))
        {
            return Some(
                GovError::new(
                    d["code"].as_str().unwrap_or("PLUGIN_NOT_AUTHORIZED"),
                    format!(
                        "plugin '{plugin_id}' is declared but not usable: {}",
                        d["reason"].as_str().unwrap_or("")
                    ),
                )
                .with_details(d.clone()),
            );
        }
        if let Some(r) = self
            .rejected
            .iter()
            .find(|d| d["plugin_id"].as_str() == Some(plugin_id))
        {
            return Some(
                GovError::new(
                    "PLUGIN_DESCRIPTOR_INVALID",
                    format!(
                        "plugin '{plugin_id}' descriptor is invalid and can never execute: {}",
                        r["reason"].as_str().unwrap_or("")
                    ),
                )
                .with_details(r.clone()),
            );
        }
        None
    }
}

fn observed_path(p: &Project) -> PathBuf {
    p.runtime_dir().join("plugins").join("observed.json")
}

/// Files the command resolves to inside the governed project (interpreter scripts, local executables); hashed for the
/// content pin. Binaries resolved from PATH (e.g. `python3`) are identified by name only.
pub fn command_files(desc: &PluginDescriptor, root: &Path) -> Vec<(String, PathBuf)> {
    let mut out = vec![];
    let plugin_dir = Path::new(&desc.source)
        .parent()
        .map(|p| p.to_path_buf())
        .unwrap_or_default();
    for (i, c) in desc.command.iter().enumerate() {
        let c = c
            .replace("{project_root}", &root.to_string_lossy())
            .replace("{plugin_dir}", &plugin_dir.to_string_lossy());
        if i > 0 && c.starts_with('-') {
            continue;
        }
        let cand = if Path::new(&c).is_absolute() {
            PathBuf::from(&c)
        } else {
            root.join(&c)
        };
        if cand.is_file() {
            out.push((c.clone(), cand));
        }
    }
    out
}

/// Content hash over the resolvable command files (sorted), or None when nothing local is hashable.
pub fn pin_hash(desc: &PluginDescriptor, root: &Path) -> Option<String> {
    let mut files = command_files(desc, root);
    if files.is_empty() {
        return None;
    }
    files.sort();
    let mut acc = String::new();
    for (name, path) in files {
        let bytes = std::fs::read(&path).ok()?;
        acc.push_str(&format!("{name}:{}\n", sha256_hex(&bytes)));
    }
    Some(sha256_hex(acc.as_bytes()))
}

fn binary_on_path(name: &str) -> bool {
    super::ecosystems::binary_available(name)
}

/// Executable resolvable? (health kind `command_exists`, the default; `protocol_ping` is run by `gov plugins health`).
pub fn health_static(desc: &PluginDescriptor, root: &Path) -> (bool, String) {
    let first = desc.command.first().cloned().unwrap_or_default();
    let plugin_dir = Path::new(&desc.source)
        .parent()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_default();
    let first = first
        .replace("{project_root}", &root.to_string_lossy())
        .replace("{plugin_dir}", &plugin_dir);
    let ok = if first.contains('/') {
        let p = if Path::new(&first).is_absolute() {
            PathBuf::from(&first)
        } else {
            root.join(&first)
        };
        p.is_file()
    } else {
        binary_on_path(&first)
    };
    if !ok {
        return (false, format!("command '{first}' is not resolvable"));
    }
    // every non-flag argument that names an existing-looking script must exist
    for a in desc.command.iter().skip(1) {
        let a = a
            .replace("{project_root}", &root.to_string_lossy())
            .replace("{plugin_dir}", &plugin_dir);
        if a.starts_with('-') {
            continue;
        }
        let looks_like_file = a.contains('/')
            || a.ends_with(".py")
            || a.ends_with(".sh")
            || a.ends_with(".js")
            || a.ends_with(".rb")
            || a.ends_with(".pl");
        if looks_like_file {
            let p = if Path::new(&a).is_absolute() {
                PathBuf::from(&a)
            } else {
                root.join(&a)
            };
            if !p.exists() {
                return (false, format!("argument '{a}' names a missing file"));
            }
        }
    }
    (true, "executable resolvable".into())
}

fn role_level(p: &Project) -> Result<u8> {
    crate::authority::level_of(p, &p.role)
}

fn parse_level(s: &str) -> u8 {
    crate::authority::parse_level(s).unwrap_or(2)
}

/// Authorise `desc` for the acting role. Ok(grant) or a typed refusal.
pub fn authorize(p: &Project, desc: &PluginDescriptor) -> Result<Value> {
    let pol = p.policies();
    let mut checks = vec![];
    let level = role_level(p)?;
    let min = parse_level(&pol.get_str("TOOL_POLICY", "plugins.min_authority", "L2"));
    let registered = desc
        .raw
        .get("provenance")
        .and_then(|v| v.get("registered_at"))
        .and_then(|v| v.as_str())
        .map(|s| !s.is_empty())
        .unwrap_or(false);
    // 1. authority floor: an unregistered (hand-declared) descriptor executes only for roles at/above the floor; a
    //    registered one (governed act, gate when elevated) executes for its approved_roles
    let approved: Vec<String> = desc.approved_roles.clone();
    let role_ok = if !approved.is_empty() {
        approved.iter().any(|r| r == "all" || r == &p.role)
    } else if registered {
        true
    } else {
        level >= min
    };
    checks.push(json!({"check": "role_authorised", "ok": role_ok, "detail": format!("role {} L{level}; approved_roles {:?}; registered {registered}; min_authority L{min}", p.role, approved)}));
    if !role_ok {
        return Err(GovError::new("AUTHORITY_DENIED", format!("role '{}' (L{level}) may not execute plugin '{}': {}", p.role, desc.plugin_id, if !approved.is_empty() { format!("not in approved_roles {approved:?}") } else { format!("unregistered descriptors execute only for roles at/above TOOL_POLICY.plugins.min_authority (L{min}); register it with `gov plugins register`") })).with_details(json!({"operation": "execute_plugin", "plugin_id": desc.plugin_id, "role": p.role, "level": format!("L{level}"), "checks": checks})));
    }
    // 2. permission classes: required classes must be held by the role; elevated classes need a registration gate
    let perms = crate::tools::role_permissions(p, &p.role);
    let required = desc.required_permission_classes.clone();
    let missing: Vec<&String> = required.iter().filter(|r| !perms.contains(r)).collect();
    checks.push(json!({"check": "permission_classes", "ok": missing.is_empty(), "detail": format!("required {required:?}; role holds {perms:?}")}));
    if !missing.is_empty() {
        return Err(GovError::new("PLUGIN_NOT_AUTHORIZED", format!("plugin '{}' requires permission classes {missing:?} that role '{}' does not hold (TOOL_PERMISSIONS)", desc.plugin_id, p.role)).with_details(json!({"plugin_id": desc.plugin_id, "checks": checks})));
    }
    let elevated = pol.get_list("TOOL_POLICY", "plugins.elevated_permission_classes");
    let needs_gate = required.iter().any(|r| elevated.contains(r))
        || desc
            .raw
            .get("permissions")
            .map(|x| {
                x["network"].as_bool().unwrap_or(false)
                    || x["filesystem_write"].as_bool().unwrap_or(false)
            })
            .unwrap_or(false);
    if needs_gate {
        let gate = desc
            .raw
            .get("provenance")
            .and_then(|v| v.get("gate"))
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        let gate_ok = !gate.is_empty() && crate::orchestration::gates::is_answered_yes(p, &gate);
        checks.push(json!({"check": "elevated_permissions_approved", "ok": gate_ok, "detail": format!("gate {gate:?}")}));
        if !gate_ok {
            return Err(GovError::new("PLUGIN_NOT_APPROVED", format!("plugin '{}' declares elevated permissions ({required:?}/network/filesystem_write) but no presented, answered-A registration gate is recorded in provenance.gate", desc.plugin_id)).with_details(json!({"plugin_id": desc.plugin_id, "checks": checks})));
        }
    }
    // 3. health: the executable must resolve
    let (healthy, hmsg) = health_static(desc, &p.root);
    checks.push(json!({"check": "health", "ok": healthy, "detail": hmsg}));
    if !healthy {
        return Err(GovError::new(
            "PLUGIN_UNHEALTHY",
            format!(
                "plugin '{}' failed its health check: {hmsg}",
                desc.plugin_id
            ),
        )
        .with_details(json!({"plugin_id": desc.plugin_id, "checks": checks})));
    }
    // 4. pin: declared sha256 must match; an observed implementation change without a version change is drift
    let observed = pin_hash(desc, &p.root);
    if let Some(declared) = &desc.pin_sha256 {
        let ok = observed.as_deref() == Some(declared.as_str());
        checks.push(json!({"check": "pin_sha256", "ok": ok, "detail": format!("declared {declared}, observed {observed:?}")}));
        if !ok {
            return Err(GovError::new("PLUGIN_PIN_MISMATCH", format!("plugin '{}' implementation does not match its declared pin (sha256 {declared}); re-register after review", desc.plugin_id)).with_details(json!({"plugin_id": desc.plugin_id, "checks": checks})));
        }
    }
    let drift = record_observed(p, desc, observed.as_deref());
    if let Some(d) = drift {
        checks.push(json!({"check": "pin_drift", "ok": false, "detail": d.clone()}));
        if pol.get_bool("TOOL_POLICY", "plugins.refuse_on_pin_drift", true) {
            return Err(GovError::new(
                "PLUGIN_PIN_MISMATCH",
                format!("plugin '{}': {d}", desc.plugin_id),
            )
            .with_details(json!({"plugin_id": desc.plugin_id, "checks": checks})));
        }
    } else {
        checks.push(json!({"check": "pin_drift", "ok": true, "detail": observed.clone().unwrap_or_else(|| "no local files to pin (interpreter-only command)".into())}));
    }
    Ok(
        json!({"plugin_id": desc.plugin_id, "capability": desc.capability, "version": desc.version, "role": p.role, "level": format!("L{level}"), "registered": registered, "pin_sha256": observed, "checks": checks}),
    )
}

/// Remember the first observed content hash per (plugin_id, version) on this machine; report drift.
fn record_observed(p: &Project, desc: &PluginDescriptor, observed: Option<&str>) -> Option<String> {
    let h = observed?;
    let path = observed_path(p);
    let mut doc = read_json(&path).unwrap_or(json!({}));
    let key = desc.plugin_id.clone();
    let prev = doc.get(&key).cloned();
    if let Some(prev) = prev {
        if prev["version"].as_str() == Some(desc.version.as_str()) {
            if prev["sha256"].as_str() != Some(h) {
                return Some(format!("implementation changed since first governed use on this machine (version {} unchanged; sha256 {} → {h}); bump the version or re-register", desc.version, prev["sha256"].as_str().unwrap_or("?")));
            }
            return None;
        }
    }
    doc[&key] = json!({"version": desc.version, "sha256": h, "first_seen": now_iso(), "source": desc.source});
    let _ = std::fs::create_dir_all(path.parent().unwrap());
    let _ = write_json(&path, &doc);
    None
}

/// Invocation timeout for governed plugins (TOOL_POLICY.plugins.timeout_seconds).
pub fn invoke_timeout(p: &Project) -> std::time::Duration {
    std::time::Duration::from_secs(
        p.policies()
            .get_i64("TOOL_POLICY", "plugins.timeout_seconds", 60)
            .max(1) as u64,
    )
}

/// Every declared plugin classified for the acting role.
pub fn plugin_set(p: &Project) -> PluginSet {
    let (valid, rejected) = discover_all(&p.root);
    let mut set = PluginSet {
        usable: vec![],
        denied: vec![],
        rejected,
    };
    for d in valid {
        match authorize(p, &d) {
            Ok(_) => set.usable.push(d),
            Err(e) => set.denied.push(json!({"plugin_id": d.plugin_id, "capability": d.capability, "version": d.version, "source": d.source, "code": e.code, "reason": e.message, "details": e.details})),
        }
    }
    set
}

/// Register (or re-register) a plugin descriptor as a governed act: authority, schema, pin hash, provenance, and a
/// Human Decision Gate when the descriptor asks for elevated permissions (TOOL_POLICY auto-install conditions).
pub fn register(p: &Project, mut descriptor: Value) -> Result<Value> {
    crate::orchestration::control::guard_write(p, "plugins register")?;
    crate::authority::require(p, "register_plugin")?;
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
    if !install_roles.is_empty() && !install_roles.iter().any(|r| r == &p.role) {
        return Err(GovError::new(
            "AUTHORITY_DENIED",
            format!(
                "role '{}' is not in TOOL_PERMISSIONS.install_authority_roles {install_roles:?}",
                p.role
            ),
        )
        .with_details(json!({"operation": "register_plugin", "role": p.role})));
    }
    let id = descriptor["plugin_id"].as_str().unwrap_or("").to_string();
    if id.is_empty() {
        return Err(GovError::new("USAGE", "descriptor requires plugin_id"));
    }
    descriptor.as_object_mut().unwrap().remove("provenance");
    p.schemas()
        .validate("plugin-descriptor", &descriptor, &format!("(plugin {id})"))?;
    let dest = p.overlay_dir().join("plugins").join(format!("{id}.yaml"));
    let tmp = PluginDescriptor::from_value(&descriptor, &dest.to_string_lossy())
        .ok_or_else(|| GovError::new("USAGE", "descriptor is not a plugin descriptor"))?;
    let (healthy, hmsg) = health_static(&tmp, &p.root);
    if !healthy {
        return Err(GovError::new(
            "PLUGIN_UNHEALTHY",
            format!("plugin '{id}' cannot be registered: {hmsg}"),
        ));
    }
    let pin = pin_hash(&tmp, &p.root);
    let pol = p.policies();
    let elevated = pol.get_list("TOOL_POLICY", "plugins.elevated_permission_classes");
    let required: Vec<String> = tmp.required_permission_classes.clone();
    let perms = crate::tools::role_permissions(p, &p.role);
    let needs_gate = required.iter().any(|r| elevated.contains(r))
        || descriptor
            .get("permissions")
            .map(|x| {
                x["network"].as_bool().unwrap_or(false)
                    || x["filesystem_write"].as_bool().unwrap_or(false)
            })
            .unwrap_or(false);
    let escalates = required.iter().any(|r| !perms.contains(r));
    let mut gate_id = Value::Null;
    if needs_gate || escalates {
        let existing = descriptor
            .get("registration_gate")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string())
            .unwrap_or_default();
        if !existing.is_empty() && crate::orchestration::gates::is_answered_yes(p, &existing) {
            gate_id = json!(existing);
        } else {
            let g = crate::orchestration::gates::create_system(
                p,
                json!({"question": format!("Approve registration of plugin {id} ({}) with elevated permissions {required:?}?", tmp.capability), "why_now": "a capability descriptor asks for permissions beyond the sandboxed stdin/stdout boundary", "current_state": "plugin not registered", "options": [{"id": "A", "description": "approve registration"}, {"id": "B", "description": "refuse"}], "impact": format!("command {:?}", tmp.command), "reversibility": "delete the descriptor", "recommendation": "A only after reviewing the command and its provenance", "confidence": 0.5, "trigger": "privilege_elevation", "impact_radius": "R3", "plugin_id": id}),
            )?;
            return Ok(
                json!({"registered": false, "human_gate": g["id"], "reason": "elevated permissions or privilege escalation require a presented, answered registration gate; re-run with the descriptor field registration_gate: <HDG> after the human answers A"}),
            );
        }
    }
    descriptor["pin"] = json!({"sha256": pin, "files": command_files(&tmp, &p.root).iter().map(|(n, _)| n.clone()).collect::<Vec<_>>()});
    descriptor["provenance"] = json!({"registered_by_session": p.session_id, "registered_by_role": p.role, "registered_at": now_iso(), "gate": gate_id, "method": "gov plugins register"});
    descriptor["status"] = json!("active");
    if descriptor.get("approved_roles").is_none() {
        descriptor["approved_roles"] = json!(["all"]);
    }
    if descriptor.get("health_check").is_none() {
        descriptor["health_check"] = json!({"kind": "command_exists"});
    }
    std::fs::create_dir_all(dest.parent().unwrap())?;
    crate::util::write_yaml(&dest, &descriptor)?;
    // reset the observed hash for this id (a registration is the governed act that pins the implementation)
    let path = observed_path(p);
    let mut doc = read_json(&path).unwrap_or(json!({}));
    doc[&id] = json!({"version": tmp.version, "sha256": pin, "first_seen": now_iso(), "source": dest.to_string_lossy()});
    let _ = std::fs::create_dir_all(path.parent().unwrap());
    let _ = write_json(&path, &doc);
    let _ = crate::tools::generate_registry(p);
    Ok(
        json!({"registered": true, "plugin_id": id, "path": format!("governance/project/plugins/{id}.yaml"), "pin": descriptor["pin"], "provenance": descriptor["provenance"], "approved_roles": descriptor["approved_roles"]}),
    )
}

/// Health report for every declared plugin (static resolution + optional protocol ping).
pub fn health(p: &Project, ping: bool) -> Vec<Value> {
    let (valid, rejected) = discover_all(&p.root);
    let mut out: Vec<Value> = rejected
        .into_iter()
        .map(|r| json!({"plugin_id": r["plugin_id"], "status": "rejected", "detail": r["reason"]}))
        .collect();
    for d in valid {
        let (ok, msg) = health_static(&d, &p.root);
        let mut row = json!({"plugin_id": d.plugin_id, "capability": d.capability, "version": d.version, "status": if ok { "healthy" } else { "unhealthy" }, "detail": msg, "authorised_for_acting_role": authorize(p, &d).is_ok()});
        if ok
            && ping
            && d.raw.get("health_check").and_then(|h| h["kind"].as_str()) == Some("protocol_ping")
        {
            let inputs = match d.capability.as_str() {
                "embed" => json!({"texts": []}),
                "rerank" => json!({"query": "", "candidates": []}),
                _ => json!({}),
            };
            match super::host::invoke(&d, &p.root, inputs, std::time::Duration::from_secs(20)) {
                Ok(o) => {
                    row["ping"] = json!({"ok": true, "provider": o.provider});
                }
                Err(e) => {
                    row["ping"] = json!({"ok": false, "error": e.code});
                    row["status"] = json!("unhealthy");
                }
            }
        }
        out.push(row);
    }
    out
}

/// Findings for doctor/suite: rejected descriptors, drift, unauthorised pinned implementations.
pub fn findings(p: &Project) -> Vec<Value> {
    let set = plugin_set(p);
    let mut out = vec![];
    for r in &set.rejected {
        out.push(json!({"severity": "high", "plugin_id": r["plugin_id"], "message": format!("plugin descriptor {} is invalid and cannot execute: {}", r["source"].as_str().unwrap_or("?"), r["reason"].as_str().unwrap_or("")), "path": r["source"]}));
    }
    let pol = p.policies();
    let pinned_embed = pol.get_str("MEMORY_POLICY", "embedding.provider", "hashed-ngram");
    let pinned_rerank = pol.get_str("MEMORY_POLICY", "reranker.provider", "none");
    for d in &set.denied {
        let id = d["plugin_id"].as_str().unwrap_or("");
        let sev = if d["code"] == "PLUGIN_PIN_MISMATCH"
            || d["code"] == "PLUGIN_NOT_APPROVED"
            || id == pinned_embed
            || id == pinned_rerank
        {
            "high"
        } else {
            "medium"
        };
        out.push(json!({"severity": sev, "plugin_id": id, "message": format!("plugin {id} not usable by role {}: {} ({})", p.role, d["reason"].as_str().unwrap_or(""), d["code"].as_str().unwrap_or("")), "path": d["source"]}));
    }
    out
}
