//! Authoritative plugin registry (verifier V-H1).
//!
//! A capability descriptor is *discovery*, never *authorisation*. Everything a descriptor says about its own
//! standing — `approved_roles`, `provenance`, `status`, `registration_gate` — is attacker-controllable content in a
//! file that any writer of the repository can create. Registration therefore lives outside the descriptor, in
//! `governance/generated/plugin-registry.json`, which only `gov plugins register` writes after checking authority,
//! health, permissions and (for elevated permissions) an answered Human Decision Gate.
//!
//! A registry entry binds, for one `plugin_id`:
//!   * the exact `version` it was registered at;
//!   * `descriptor_sha256` — the bytes of the descriptor file as registered, so a later edit fails closed;
//!   * `implementation_sha256` — the observed content hash of the command files;
//!   * the authoritative `approved_roles`, `required_permission_classes` and `permissions`;
//!   * the gate/decision that approved elevated permissions, and who registered it when.
//!
//! Registration never lowers the authority floor: `TOOL_POLICY.plugins.min_authority` comes from verified kernel
//! policy and applies to every execution, so even a forged registry file cannot hand an L0 role execution.
use super::protocol::PluginDescriptor;
use crate::util::{now_iso, read_json, sha256_hex, write_json};
use crate::{Project, Result};
use serde_json::{json, Value};
use std::path::PathBuf;

pub const REGISTRY_PATH: &str = "governance/generated/plugin-registry.json";
pub const SCHEMA_VERSION: &str = "1.0.0";

pub fn path(p: &Project) -> PathBuf {
    p.root.join(REGISTRY_PATH)
}

pub fn load(p: &Project) -> Value {
    read_json(&path(p)).unwrap_or(json!({"schema_version": SCHEMA_VERSION, "plugins": {}}))
}

/// The registered entry for `plugin_id`, if the OS ever registered one.
pub fn entry(p: &Project, plugin_id: &str) -> Option<Value> {
    load(p)
        .get("plugins")
        .and_then(|m| m.get(plugin_id))
        .cloned()
        .filter(|v| v.is_object())
}

/// sha256 of the descriptor file exactly as it sits on disk (identity binding for the registry entry).
pub fn descriptor_hash(desc: &PluginDescriptor) -> Option<String> {
    std::fs::read(&desc.source).ok().map(|b| sha256_hex(&b))
}

/// How a descriptor relates to the authoritative registry.
#[derive(Debug, Clone, PartialEq)]
pub enum Standing {
    /// No registry record: a hand-declared descriptor. Executable only at/above the authority floor, never with
    /// elevated permissions.
    Unregistered,
    /// A registry record matches this descriptor's identity, version and content.
    Registered(Box<Value>),
    /// A registry record exists but the descriptor no longer matches it (edited, version drift, id reuse).
    Mismatched(String),
}

pub fn standing(p: &Project, desc: &PluginDescriptor) -> Standing {
    let Some(e) = entry(p, &desc.plugin_id) else {
        return Standing::Unregistered;
    };
    let reg_version = e
        .get("version")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    if reg_version != desc.version {
        return Standing::Mismatched(format!(
            "plugin '{}' is registered at version {reg_version} but the descriptor declares {}; re-register after review",
            desc.plugin_id, desc.version
        ));
    }
    let reg_hash = e
        .get("descriptor_sha256")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let actual = descriptor_hash(desc).unwrap_or_default();
    if reg_hash.is_empty() || actual.is_empty() || reg_hash != actual {
        return Standing::Mismatched(format!(
            "plugin '{}' descriptor does not match the registered content (registered sha256 {}, observed {}); an edited descriptor is never authorised",
            desc.plugin_id,
            if reg_hash.is_empty() { "(absent)" } else { &reg_hash[..reg_hash.len().min(12)] },
            if actual.is_empty() { "(unreadable)" } else { &actual[..actual.len().min(12)] }
        ));
    }
    let reg_cap = e.get("capability").and_then(|v| v.as_str()).unwrap_or("");
    if reg_cap != desc.capability {
        return Standing::Mismatched(format!(
            "plugin '{}' is registered for capability '{reg_cap}' but the descriptor declares '{}'",
            desc.plugin_id, desc.capability
        ));
    }
    Standing::Registered(Box::new(e))
}

/// Record a registration. Written only by `capabilities::governance::register` after its governance checks.
#[allow(clippy::too_many_arguments)]
pub fn record(
    p: &Project,
    desc: &PluginDescriptor,
    descriptor_sha256: &str,
    implementation_sha256: Option<&str>,
    implementation_files: &[String],
    approved_roles: &[String],
    required_permission_classes: &[String],
    permissions: Value,
    gate: Value,
) -> Result<Value> {
    let mut doc = load(p);
    if !doc.is_object() {
        doc = json!({"schema_version": SCHEMA_VERSION, "plugins": {}});
    }
    doc["schema_version"] = json!(SCHEMA_VERSION);
    if !doc["plugins"].is_object() {
        doc["plugins"] = json!({});
    }
    let e = json!({
        "plugin_id": desc.plugin_id, "capability": desc.capability, "version": desc.version,
        "descriptor_path": desc.source.rsplit('/').take(2).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join("/"),
        "descriptor_sha256": descriptor_sha256,
        "implementation_sha256": implementation_sha256, "implementation_files": implementation_files,
        "approved_roles": approved_roles, "required_permission_classes": required_permission_classes,
        "permissions": permissions, "registration_gate": gate,
        "registered_by_session": p.session_id, "registered_by_role": p.role, "registered_at": now_iso(),
        "method": "gov plugins register",
    });
    doc["plugins"][&desc.plugin_id] = e.clone();
    write_json(&path(p), &doc)?;
    Ok(e)
}

/// Remove a registration (the descriptor keeps existing; it simply stops being registered).
pub fn remove(p: &Project, plugin_id: &str) -> Result<bool> {
    let mut doc = load(p);
    let existed = doc.get("plugins").and_then(|m| m.get(plugin_id)).is_some();
    if existed {
        if let Some(m) = doc["plugins"].as_object_mut() {
            m.remove(plugin_id);
        }
        write_json(&path(p), &doc)?;
    }
    Ok(existed)
}

/// Registry records with no descriptor on disk (stale registrations), for doctor/audit.
pub fn orphans(p: &Project, declared: &[String]) -> Vec<String> {
    load(p)
        .get("plugins")
        .and_then(|m| m.as_object())
        .map(|m| {
            m.keys()
                .filter(|k| !declared.contains(k))
                .cloned()
                .collect()
        })
        .unwrap_or_default()
}
