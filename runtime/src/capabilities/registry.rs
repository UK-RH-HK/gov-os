//! Authoritative plugin registry (verifier V-H1; BC-P2-09 registry side, BC-P2-40).
//!
//! A capability descriptor is *discovery*, never *authorisation*. Everything a descriptor says about its own
//! standing — `approved_roles`, `provenance`, `status`, `registration_gate` — is attacker-controllable content in a
//! file that any writer of the repository can create. Registration therefore lives outside the descriptor, in
//! `governance/generated/plugin-registry.json`, which only `gov plugins register` writes after checking authority,
//! health, the implementation binding and (for every executable plugin) an answered Human Decision Gate raised for
//! exactly that registration.
//!
//! A registry entry binds, for one `plugin_id`:
//!   * the exact `version` it was registered at, and its `capability`;
//!   * `descriptor_sha256` — the bytes of the descriptor file as registered, so a later edit fails closed;
//!   * `implementation` / `implementation_sha256` — every file the command executes, as the OS derived it
//!     ([`super::binding::resolve`]: program, script arguments, module-form packages, declared paths), never null;
//!   * `execution_class`, and `registration_subject_sha256` — the digest the registration gate's answer is bound to;
//!   * the authoritative `approved_roles`, `required_permission_classes` and `permissions`;
//!   * the gate that approved it, and who registered it when.
//!
//! **T2 binding (BC-P2-09, D-0007 T2: "the plugin registry" is OS-written state).** Every entry is sealed with the
//! machine's T2 binding key by the registering operation ([`crate::t2::seal_value`]). An entry is honoured only when
//! its seal verifies ([`Standing::Registered`]); an entry a worker wrote or edited by hand, one sealed on another
//! machine (a clone), or a legacy unsealed entry is [`Standing::Unbound`] — refused at execution, reported by doctor
//! D028 and the `plugin_governance` suite family, and it changes the governance-suite inputs (the registry file is a
//! currency input), so prior green evidence goes stale. The tracked entry still carries the registered hashes, so a
//! fresh clone or a reset of machine state cannot re-baseline tampered bytes: re-registration is a new governed act
//! with a new gate whose package shows the implementation being approved.
//!
//! Registration never lowers the authority floor: `TOOL_POLICY.plugins.min_authority` comes from verified kernel
//! policy and applies to every execution.
use super::protocol::PluginDescriptor;
use crate::t2::Binding;
use crate::util::{now_iso, read_json, sha256_hex, write_json};
use crate::{Project, Result};
use serde_json::{json, Value};
use std::path::PathBuf;

pub const REGISTRY_PATH: &str = "governance/generated/plugin-registry.json";
pub const SCHEMA_VERSION: &str = "1.1.0";
/// The operation name bound into every registry entry's seal.
pub const SEAL_OPERATION: &str = "plugins register";

pub fn path(p: &Project) -> PathBuf {
    p.root.join(REGISTRY_PATH)
}

pub fn load(p: &Project) -> Value {
    read_json(&path(p)).unwrap_or(json!({"schema_version": SCHEMA_VERSION, "plugins": {}}))
}

/// The recorded entry for `plugin_id`, whatever its binding (callers that honour it must use [`standing`]).
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

/// The T2 binding of one registry entry (`plugin_id` is the key it is recorded under).
pub fn binding_of(plugin_id: &str, e: &Value) -> Binding {
    if e.get("plugin_id").and_then(|v| v.as_str()) != Some(plugin_id) {
        return Binding::Broken {
            reason: format!(
                "the entry recorded under '{plugin_id}' names plugin '{}'",
                e.get("plugin_id").and_then(|v| v.as_str()).unwrap_or("")
            ),
        };
    }
    crate::t2::verify_value(e, "")
}

/// How a descriptor relates to the authoritative registry.
#[derive(Debug, Clone, PartialEq)]
pub enum Standing {
    /// No registry record: a hand-declared descriptor. Only an OS-provided capability server may run in this
    /// standing ([`super::binding::ExecutionClass::OsProvided`]); an executable plugin is refused.
    Unregistered,
    /// A registry record `gov plugins register` wrote on this machine (T2-verified) matches this descriptor's
    /// identity, version and content.
    Registered(Box<Value>),
    /// A registry record exists but no gov operation on this machine produced it as it stands (hand-written, edited,
    /// legacy unsealed, or sealed elsewhere). Never honoured.
    Unbound { binding: Binding },
    /// A verified registry record exists but the descriptor no longer matches it (edited, version drift, id reuse).
    Mismatched(String),
}

pub fn standing(p: &Project, desc: &PluginDescriptor) -> Standing {
    let Some(e) = entry(p, &desc.plugin_id) else {
        return Standing::Unregistered;
    };
    let b = binding_of(&desc.plugin_id, &e);
    if !b.is_verified() {
        return Standing::Unbound { binding: b };
    }
    let reg_version = e
        .get("version")
        .map(|v| match v {
            Value::String(s) => s.clone(),
            other => other.to_string(),
        })
        .unwrap_or_default();
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

/// What a registration records. Built by `capabilities::governance::register` after its governance checks.
pub struct Registration<'a> {
    pub desc: &'a PluginDescriptor,
    pub descriptor_sha256: &'a str,
    pub implementation: &'a super::binding::Implementation,
    pub subject_sha256: &'a str,
    pub approved_roles: &'a [String],
    pub required_permission_classes: &'a [String],
    pub permissions: Value,
    pub gate: Value,
}

/// Record a registration and **seal the entry** as written by `gov plugins register` (T2). Written only by
/// `capabilities::governance::register` after its governance checks.
pub fn record(p: &Project, r: Registration) -> Result<Value> {
    let mut doc = load(p);
    if !doc.is_object() {
        doc = json!({"schema_version": SCHEMA_VERSION, "plugins": {}});
    }
    doc["schema_version"] = json!(SCHEMA_VERSION);
    if !doc["plugins"].is_object() {
        doc["plugins"] = json!({});
    }
    let desc = r.desc;
    let mut e = json!({
        "plugin_id": desc.plugin_id, "capability": desc.capability, "version": desc.version,
        "descriptor_path": desc.source.rsplit('/').take(2).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join("/"),
        "descriptor_sha256": r.descriptor_sha256,
        "execution_class": r.implementation.class.as_str(),
        "command": desc.command, "cwd": desc.cwd,
        "program": r.implementation.program,
        "implementation_sha256": r.implementation.sha256,
        "implementation_files": r.implementation.paths(),
        "implementation": r.implementation.files,
        "registration_subject_sha256": r.subject_sha256,
        "approved_roles": r.approved_roles, "required_permission_classes": r.required_permission_classes,
        "permissions": r.permissions, "registration_gate": r.gate,
        "registered_by_session": p.session_id, "registered_by_role": p.role, "registered_at": now_iso(),
        "method": SEAL_OPERATION,
    });
    crate::t2::seal_value(&mut e, "", SEAL_OPERATION)?;
    doc["plugins"][&desc.plugin_id] = e.clone();
    seal_document(&mut doc, SEAL_OPERATION)?;
    write_json(&path(p), &doc)?;
    Ok(e)
}

/// Seal the registry document as a whole as well (in addition to each entry), so that a changed
/// `governance/generated/plugin-registry.json` is provably an OS write for the G2 task-close mutation scope
/// ([`crate::t2::classify_path`]) exactly when the file is what a gov operation wrote.
fn seal_document(doc: &mut Value, operation: &str) -> Result<()> {
    if let Some(o) = doc.as_object_mut() {
        o.remove(crate::t2::SEAL_FIELD);
    }
    crate::t2::seal_value(doc, "", operation)
}

/// Remove a registration (the descriptor keeps existing; it simply stops being registered).
pub fn remove(p: &Project, plugin_id: &str) -> Result<bool> {
    let mut doc = load(p);
    let existed = doc.get("plugins").and_then(|m| m.get(plugin_id)).is_some();
    if existed {
        if let Some(m) = doc["plugins"].as_object_mut() {
            m.remove(plugin_id);
        }
        seal_document(&mut doc, "plugins unregister")?;
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

/// Every registry entry no gov operation on this machine produced as it stands (for doctor D028, the
/// `plugin_governance` suite family and `gov plugins registry`): `(plugin_id, binding)`.
pub fn unbound_entries(p: &Project) -> Vec<(String, Binding)> {
    load(p)
        .get("plugins")
        .and_then(|m| m.as_object())
        .map(|m| {
            m.iter()
                .map(|(k, e)| (k.clone(), binding_of(k, e)))
                .filter(|(_, b)| !b.is_verified())
                .collect()
        })
        .unwrap_or_default()
}

/// The T2 binding of the registry document as a whole (what `t2::classify_path` sees for the file).
pub fn document_binding(p: &Project) -> Binding {
    if !path(p).exists() {
        return Binding::Unsealed;
    }
    crate::t2::verify_file(&p.root, REGISTRY_PATH)
}

/// The registry as `gov plugins registry` shows it: every entry with its T2 binding stated beside it.
pub fn report(p: &Project) -> Value {
    let whole = document_binding(p);
    let mut doc = load(p);
    doc["document_t2"] = whole.to_value();
    if let Some(m) = doc.get_mut("plugins").and_then(|m| m.as_object_mut()) {
        for (k, e) in m.iter_mut() {
            let b = binding_of(k, e);
            if let Some(o) = e.as_object_mut() {
                o.insert("t2".into(), b.to_value());
                o.insert("honoured".into(), json!(b.is_verified()));
            }
        }
    }
    doc
}
