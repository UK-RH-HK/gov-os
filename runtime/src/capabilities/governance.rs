//! Capability/plugin supply-chain boundary (framework §28–32, TOOL_POLICY.plugins; verifier H-N2).
//! No executable capability runs merely because a descriptor exists. Before a plugin is used by any path
//! (`capabilities invoke`, the indexer, retrieval, benchmarks, code intelligence) it must be: a schema-valid descriptor
//! with a stable identity and version pin; registered in the generated Tool/Capability Registry; healthy (executable
//! resolvable); authorised for the acting role (authority floor, approved_roles, permission classes, elevated
//! permissions only through a registration gate); and pinned by content hash when a pin is declared or observed.
//! Every refusal is a typed, auditable error and the plugin is listed as `denied`/`rejected`, never silently skipped.
use super::host::discover_all;
use super::protocol::PluginDescriptor;
use super::registry::{self, Standing};
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

/// Claims a descriptor makes about its own standing. They are inert — recorded only so that doctor D028 and the
/// `plugin_governance` suite family can report a descriptor that tries to authorise itself (verifier V-H1).
pub fn self_authorising_claims(desc: &PluginDescriptor) -> Vec<String> {
    let mut v = vec![];
    if desc.approved_roles.iter().any(|r| r == "all") {
        v.push(
            "approved_roles: [\"all\"] (a descriptor cannot widen role authorisation)".to_string(),
        );
    }
    if desc.raw.get("provenance").is_some() {
        v.push("provenance (registration is proven by the OS-written plugin registry, not by the descriptor)".to_string());
    }
    if desc.raw.get("status").and_then(|s| s.as_str()) == Some("active") {
        v.push("status: active".to_string());
    }
    v
}

fn strings(v: &Value, key: &str) -> Vec<String> {
    v.get(key)
        .and_then(|x| x.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|s| s.as_str().map(|t| t.to_string()))
                .collect()
        })
        .unwrap_or_default()
}

fn declares_elevated(v: &Value, required: &[String], elevated: &[String]) -> bool {
    required.iter().any(|r| elevated.contains(r))
        || v.get("permissions")
            .map(|x| {
                x["network"].as_bool().unwrap_or(false)
                    || x["filesystem_write"].as_bool().unwrap_or(false)
            })
            .unwrap_or(false)
}

/// Authorise `desc` for the acting role. Ok(grant) or a typed refusal.
///
/// Trust sources: the authority floor and permission classes come from verified kernel policy
/// (`kernel_trust`-backed `PolicySet`); registration, approved roles and the elevated-permission gate come from the
/// OS-written plugin registry; only the command, capability and declared pin come from the descriptor — and the pin
/// is checked against observed bytes. Nothing a descriptor says about its own standing grants anything.
pub fn authorize(p: &Project, desc: &PluginDescriptor) -> Result<Value> {
    let pol = p.policies();
    let mut checks = vec![];
    let level = role_level(p)?;
    let min = parse_level(&pol.get_str("TOOL_POLICY", "plugins.min_authority", "L2"));
    let claims = self_authorising_claims(desc);

    // 0. standing: an edited, re-versioned or re-purposed descriptor never matches its registration -> fail closed
    let standing = registry::standing(p, desc);
    if let Standing::Mismatched(why) = &standing {
        checks.push(json!({"check": "registry_binding", "ok": false, "detail": why}));
        return Err(GovError::new("PLUGIN_REGISTRY_MISMATCH", why.clone()).with_details(
            json!({"plugin_id": desc.plugin_id, "checks": checks, "registry": registry::REGISTRY_PATH}),
        ));
    }
    let reg: Option<Value> = match &standing {
        Standing::Registered(e) => Some((**e).clone()),
        _ => None,
    };
    let registered = reg.is_some();
    checks.push(json!({"check": "registry_binding", "ok": true, "detail": if registered { format!("registered in {} (identity, version and descriptor content bound)", registry::REGISTRY_PATH) } else { "hand-declared descriptor (no registration record)".to_string() }, "descriptor_claims_ignored": claims}));

    // 1. authority floor from verified kernel policy: applies to every execution, registered or not, and cannot be
    //    widened by anything inside the descriptor (verifier V-H1)
    let floor_ok = level >= min;
    checks.push(json!({"check": "authority_floor", "ok": floor_ok, "detail": format!("role {} L{level} vs TOOL_POLICY.plugins.min_authority L{min}", p.role)}));
    if !floor_ok {
        return Err(GovError::new("AUTHORITY_DENIED", format!(
            "role '{}' (L{level}) may not execute plugin '{}': TOOL_POLICY.plugins.min_authority is L{min} and a descriptor cannot grant itself authority (approved_roles and provenance inside a descriptor are ignored){}",
            p.role, desc.plugin_id,
            if claims.is_empty() { String::new() } else { format!("; ignored descriptor claims: {claims:?}") }))
        .with_details(json!({"operation": "execute_plugin", "plugin_id": desc.plugin_id, "role": p.role, "level": format!("L{level}"), "required": format!("L{min}"), "registered": registered, "ignored_descriptor_claims": claims, "checks": checks})));
    }

    // 2. approved_roles may only NARROW; the authoritative list is the registry's when the plugin is registered
    let approved: Vec<String> = match &reg {
        Some(e) => strings(e, "approved_roles"),
        None => desc.approved_roles.clone(),
    };
    let role_ok = approved.is_empty() || approved.iter().any(|r| r == "all" || r == &p.role);
    checks.push(json!({"check": "approved_roles", "ok": role_ok, "detail": format!("{approved:?} (source: {})", if registered { "registry" } else { "descriptor, narrowing only" })}));
    if !role_ok {
        return Err(GovError::new("AUTHORITY_DENIED", format!(
            "role '{}' is not in the approved roles {approved:?} for plugin '{}'", p.role, desc.plugin_id))
        .with_details(json!({"operation": "execute_plugin", "plugin_id": desc.plugin_id, "role": p.role, "checks": checks})));
    }

    // 3. permission classes: the role must hold every class either side declares (a descriptor may only add needs)
    let perms = crate::tools::role_permissions(p, &p.role);
    let mut required: Vec<String> = desc.required_permission_classes.clone();
    if let Some(e) = &reg {
        for r in strings(e, "required_permission_classes") {
            if !required.contains(&r) {
                required.push(r);
            }
        }
    }
    let missing: Vec<&String> = required.iter().filter(|r| !perms.contains(r)).collect();
    checks.push(json!({"check": "permission_classes", "ok": missing.is_empty(), "detail": format!("required {required:?}; role holds {perms:?}")}));
    if !missing.is_empty() {
        return Err(GovError::new("PLUGIN_NOT_AUTHORIZED", format!("plugin '{}' requires permission classes {missing:?} that role '{}' does not hold (TOOL_PERMISSIONS)", desc.plugin_id, p.role)).with_details(json!({"plugin_id": desc.plugin_id, "checks": checks})));
    }

    // 4. elevated permissions: approval is the gate recorded in the REGISTRY, never a field in the descriptor
    let elevated = pol.get_list("TOOL_POLICY", "plugins.elevated_permission_classes");
    let needs_gate = declares_elevated(&desc.raw, &required, &elevated)
        || reg
            .as_ref()
            .map(|e| declares_elevated(e, &required, &elevated))
            .unwrap_or(false);
    if needs_gate {
        let gate = reg
            .as_ref()
            .and_then(|e| {
                e.get("registration_gate")
                    .and_then(|v| v.as_str())
                    .map(|s| s.to_string())
            })
            .unwrap_or_default();
        let gate_ok = !gate.is_empty() && crate::orchestration::gates::is_answered_yes(p, &gate);
        checks.push(json!({"check": "elevated_permissions_approved", "ok": gate_ok, "detail": format!("registry gate {gate:?}; registered {registered}")}));
        if !gate_ok {
            return Err(GovError::new("PLUGIN_NOT_APPROVED", format!(
                "plugin '{}' declares elevated permissions ({required:?}/network/filesystem_write); it must be registered with `gov plugins register` against a presented, answered-A gate recorded in {} (a gate id written into the descriptor proves nothing)",
                desc.plugin_id, registry::REGISTRY_PATH))
            .with_details(json!({"plugin_id": desc.plugin_id, "checks": checks})));
        }
    }

    // 5. health: the executable must resolve
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

    // 6. pin: declared sha256, the registered implementation hash, and observed drift must all agree
    let observed = pin_hash(desc, &p.root);
    if let Some(declared) = &desc.pin_sha256 {
        let ok = observed.as_deref() == Some(declared.as_str());
        checks.push(json!({"check": "pin_sha256", "ok": ok, "detail": format!("declared {declared}, observed {observed:?}")}));
        if !ok {
            return Err(GovError::new("PLUGIN_PIN_MISMATCH", format!("plugin '{}' implementation does not match its declared pin (sha256 {declared}); re-register after review", desc.plugin_id)).with_details(json!({"plugin_id": desc.plugin_id, "checks": checks})));
        }
    }
    if let Some(e) = &reg {
        if let Some(reg_impl) = e.get("implementation_sha256").and_then(|v| v.as_str()) {
            let ok = observed.as_deref() == Some(reg_impl);
            checks.push(json!({"check": "registered_implementation", "ok": ok, "detail": format!("registered {reg_impl}, observed {observed:?}")}));
            if !ok {
                return Err(GovError::new("PLUGIN_PIN_MISMATCH", format!("plugin '{}' implementation does not match the registered content hash; re-register after review", desc.plugin_id)).with_details(json!({"plugin_id": desc.plugin_id, "checks": checks})));
            }
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
        json!({"plugin_id": desc.plugin_id, "capability": desc.capability, "version": desc.version, "role": p.role, "level": format!("L{level}"), "registered": registered, "pin_sha256": observed, "ignored_descriptor_claims": claims, "checks": checks}),
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
    // The authoritative record lives OUTSIDE the descriptor (verifier V-H1): identity, version, descriptor content
    // hash, implementation hash, approved roles, permission classes and the approving gate are written by the OS.
    let written = PluginDescriptor::from_value(&descriptor, &dest.to_string_lossy())
        .ok_or_else(|| GovError::new("USAGE", "descriptor is not a plugin descriptor"))?;
    let dsha = registry::descriptor_hash(&written).ok_or_else(|| {
        GovError::new(
            "IO_ERROR",
            format!(
                "cannot read the registered descriptor at {}",
                dest.display()
            ),
        )
    })?;
    let approved_roles: Vec<String> = descriptor
        .get("approved_roles")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let files: Vec<String> = command_files(&written, &p.root)
        .iter()
        .map(|(n, _)| n.clone())
        .collect();
    let entry = registry::record(
        p,
        &written,
        &dsha,
        pin.as_deref(),
        &files,
        &approved_roles,
        &required,
        descriptor.get("permissions").cloned().unwrap_or(json!({})),
        gate_id.clone(),
    )?;
    // reset the observed hash for this id (a registration is the governed act that pins the implementation)
    let path = observed_path(p);
    let mut doc = read_json(&path).unwrap_or(json!({}));
    doc[&id] = json!({"version": tmp.version, "sha256": pin, "first_seen": now_iso(), "source": dest.to_string_lossy()});
    let _ = std::fs::create_dir_all(path.parent().unwrap());
    let _ = write_json(&path, &doc);
    let _ = crate::tools::generate_registry(p);
    Ok(
        json!({"registered": true, "plugin_id": id, "path": format!("governance/project/plugins/{id}.yaml"), "pin": descriptor["pin"], "provenance": descriptor["provenance"], "approved_roles": descriptor["approved_roles"], "registry": registry::REGISTRY_PATH, "registry_entry": entry}),
    )
}

/// Remove a plugin's registration (a governed act with the same authority as registering it). The descriptor stays
/// on disk and simply reverts to hand-declared standing.
pub fn unregister(p: &Project, plugin_id: &str) -> Result<Value> {
    crate::orchestration::control::guard_write(p, "plugins unregister")?;
    crate::authority::require(p, "register_plugin")?;
    let removed = registry::remove(p, plugin_id)?;
    let _ = crate::tools::generate_registry(p);
    Ok(
        json!({"unregistered": removed, "plugin_id": plugin_id, "registry": registry::REGISTRY_PATH}),
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

/// Findings for doctor/suite: invalid descriptors, self-authorising claims, registry mismatches, drift and
/// unusable pinned implementations (verifier V-H1: a descriptor that tries to authorise itself is always reported,
/// whatever the acting role, because the claim is what is wrong — not the outcome for one session).
pub fn findings(p: &Project) -> Vec<Value> {
    let (valid, rejected) = discover_all(&p.root);
    let set = plugin_set(p);
    let pol = p.policies();
    let min = parse_level(&pol.get_str("TOOL_POLICY", "plugins.min_authority", "L2"));
    let pinned_embed = pol.get_str("MEMORY_POLICY", "embedding.provider", "hashed-ngram");
    let pinned_rerank = pol.get_str("MEMORY_POLICY", "reranker.provider", "none");
    let mut out = vec![];
    for r in &rejected {
        out.push(json!({"severity": "high", "plugin_id": r["plugin_id"], "message": format!("plugin descriptor {} is invalid and cannot execute: {}", r["source"].as_str().unwrap_or("?"), r["reason"].as_str().unwrap_or("")), "path": r["source"]}));
    }
    for d in &valid {
        let claims = self_authorising_claims(d);
        let standing = registry::standing(p, d);
        match &standing {
            Standing::Mismatched(why) => out.push(json!({"severity": "high", "plugin_id": d.plugin_id, "message": format!("plugin {} does not match its registration: {why}", d.plugin_id), "path": d.source})),
            Standing::Unregistered if !claims.is_empty() => out.push(json!({"severity": "high", "plugin_id": d.plugin_id,
                "message": format!("plugin descriptor {} declares its own authorisation ({}) but no record exists in {}; the claims are ignored by the executable paths and the descriptor must be registered with `gov plugins register` or the fields removed", d.plugin_id, claims.join(", "), registry::REGISTRY_PATH),
                "path": d.source})),
            _ => {}
        }
    }
    for id in registry::orphans(
        p,
        &valid
            .iter()
            .map(|d| d.plugin_id.clone())
            .collect::<Vec<_>>(),
    ) {
        out.push(json!({"severity": "medium", "plugin_id": id, "message": format!("plugin registry records '{id}' but no descriptor declares it (stale registration; run `gov plugins unregister {id}`)"), "path": registry::REGISTRY_PATH}));
    }
    for d in &set.denied {
        let id = d["plugin_id"].as_str().unwrap_or("");
        if out.iter().any(|f| f["plugin_id"].as_str() == Some(id)) {
            continue;
        }
        let sev = if d["code"] == "PLUGIN_PIN_MISMATCH"
            || d["code"] == "PLUGIN_NOT_APPROVED"
            || d["code"] == "PLUGIN_REGISTRY_MISMATCH"
            || id == pinned_embed
            || id == pinned_rerank
        {
            "high"
        } else {
            "medium"
        };
        // an under-authority denial for the acting role is the floor working as designed, not a defect
        let expected_floor_denial = d["code"] == "AUTHORITY_DENIED"
            && crate::authority::level_of(p, &p.role)
                .map(|l| l < min)
                .unwrap_or(false);
        if expected_floor_denial {
            continue;
        }
        out.push(json!({"severity": sev, "plugin_id": id, "message": format!("plugin {id} not usable by role {}: {} ({})", p.role, d["reason"].as_str().unwrap_or(""), d["code"].as_str().unwrap_or("")), "path": d["source"]}));
    }
    out
}
