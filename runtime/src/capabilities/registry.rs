//! Authoritative plugin registry (verifier V-H1; BC-P2-09 registry side, BC-P2-40, BC-P2-31).
//!
//! A capability descriptor is *discovery*, never *authorisation*. Everything a descriptor says about its own
//! standing — `approved_roles`, `provenance`, `status`, `registration_gate` — is attacker-controllable content in a
//! file that any writer of the repository can create. Registration therefore lives outside the descriptor, in
//! `governance/registry/plugin-registry.json` ([`REGISTRY_PATH`]), which only `gov plugins register` writes after
//! checking authority, health, the implementation binding and (for every executable plugin) an answered Human
//! Decision Gate raised for exactly that registration.
//!
//! **Where it lives (BC-P2-31; Contract v3 B1:188, B3:202, D6:352; D-0007 T2).** The registry is tracked,
//! OS-written T2 state that nothing can rebuild, so it does not belong among the regenerable views of
//! `governance/generated/` (T3), where deleting the directory — framework §19's rebuild procedure — would silently
//! drop every registration. Its location is the kernel's declaration in [`crate::paths::OS_STORES`], resolved through
//! [`crate::paths::store_path`]. A project whose registry is still at the legacy location
//! ([`LEGACY_REGISTRY_PATH`]) keeps its registrations — the legacy file is read, under exactly the same per-entry seal
//! rule, only while no registry exists at the location — and the next registry write moves it
//! ([`relocate`], [`crate::paths::relocate_legacy`]: a tracked move of the bytes as they are). Moving never seals
//! anything: an entry that was not honoured before the move is not honoured after it, and a registry copied or
//! cloned into the location is honoured entry by entry only where its seal verifies on this machine. Once a
//! registry exists at the location, a file at the legacy location is never read; if it differs it is reported.
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
//!
//! **T2 coverage (WS-2 R3-11).** [`t2_audit`] lists every registry entry — and the registry document — that no gov
//! operation on this machine produced as it stands, in the row shape of [`crate::t2::audit`], so the T2 audit (and
//! through it the `os_binding_integrity` family, doctor D033 and the `t2_bindings` currency class) covers the
//! registry as it covers gates and decisions.
use super::protocol::PluginDescriptor;
use crate::t2::Binding;
use crate::util::{now_iso, read_json, sha256_hex, write_json};
use crate::{Project, Result};
use serde_json::{json, Value};
use std::path::PathBuf;

/// The id of the plugin registry among the OS's non-rebuildable stores ([`crate::paths::OS_STORES`]).
pub const STORE_ID: &str = "plugin-registry";
/// Where the registry belongs (repository-relative): tracked OS-written T2 state, outside the regenerable views.
pub const REGISTRY_PATH: &str = crate::paths::PLUGIN_REGISTRY_PATH;
/// Where `gov plugins register` kept the registry before BC-P2-31 (inside `governance/generated/`, regenerable T3
/// views). Read only while no registry exists at [`REGISTRY_PATH`]; moved by the next registry write.
pub const LEGACY_REGISTRY_PATH: &str = "governance/generated/plugin-registry.json";
pub const SCHEMA_VERSION: &str = "1.1.0";
/// The operation name bound into every registry entry's seal.
pub const SEAL_OPERATION: &str = "plugins register";

/// The absolute location of the registry (where it belongs, whether or not it exists yet).
pub fn path(p: &Project) -> PathBuf {
    crate::paths::store_path(&p.root, STORE_ID).unwrap_or_else(|| p.root.join(REGISTRY_PATH))
}

/// The absolute legacy location (see [`LEGACY_REGISTRY_PATH`]).
pub fn legacy_path(p: &Project) -> PathBuf {
    p.root.join(LEGACY_REGISTRY_PATH)
}

/// The repository-relative file the registry is read from: [`REGISTRY_PATH`] when it exists; otherwise the legacy
/// location when a registry is still kept there (a project whose registry has not been written since BC-P2-31);
/// `None` when there is no registry. Reading never moves anything: only a registry write does ([`relocate`]).
pub fn source(p: &Project) -> Option<&'static str> {
    if path(p).exists() {
        Some(REGISTRY_PATH)
    } else if legacy_path(p).exists() {
        Some(LEGACY_REGISTRY_PATH)
    } else {
        None
    }
}

/// The registry file a message should name: the one it is read from, else where it belongs.
pub fn shown_path(p: &Project) -> &'static str {
    source(p).unwrap_or(REGISTRY_PATH)
}

fn empty() -> Value {
    json!({"schema_version": SCHEMA_VERSION, "plugins": {}})
}

/// The registry document, read from [`source`]. An unreadable registry is an empty one: nothing in it is honoured,
/// so every executable plugin fails closed until it is restored or re-registered.
pub fn load(p: &Project) -> Value {
    match source(p) {
        Some(rel) => read_json(&p.root.join(rel)).unwrap_or_else(|_| empty()),
        None => empty(),
    }
}

/// **Move a registry kept at the legacy location to where it belongs** — the bytes as they are, every entry's seal
/// and the document seal included, so nothing becomes honoured by moving and nothing is re-sealed. Called by every
/// registry write before it reads the registry, and available to the upgrade/migration path. Idempotent.
///
/// When a registry already exists at the location and the legacy file differs from it, the location is
/// authoritative: the legacy file is left in place (never read, never overwritten, never deleted by this call) and
/// reported by [`location_findings`] — deleting or restoring a tracked file is the operator's decision.
pub fn relocate(p: &Project) -> Result<Vec<Value>> {
    match crate::paths::relocate_legacy(&p.root, STORE_ID) {
        Ok(moved) => Ok(moved),
        Err(e) if e.code == "STATE_LOCATION_CONFLICT" => Ok(vec![json!({
            "store": STORE_ID, "from": LEGACY_REGISTRY_PATH, "to": REGISTRY_PATH, "action": "left in place",
            "reason": "a registry already exists where it belongs and the legacy file differs from it; the registry at the location is authoritative and the legacy file is never read"})]),
        Err(e) => Err(e),
    }
}

/// Location anomalies for doctor D028 and the `plugin_governance` family: a second registry at the legacy location
/// that differs from the authoritative one. It is never read, so no authorisation relies on it: it is disclosed at
/// `low` severity (the availability rule of P2-HO-0031 — a finding that governs no reliance must not degrade the suite
/// and refuse unrelated work). A registry that simply has not been moved yet is not a plugin finding — it is still
/// honoured — and is reported by [`crate::paths::misplaced_os_state`].
pub fn location_findings(p: &Project) -> Vec<Value> {
    let (at, legacy) = (path(p), legacy_path(p));
    if !(at.exists() && legacy.exists()) {
        return vec![];
    }
    if std::fs::read(&at).ok() == std::fs::read(&legacy).ok() {
        return vec![];
    }
    vec![
        json!({"severity": "low", "plugin_id": "", "code": "PLUGIN_REGISTRY_LOCATION_CONFLICT", "path": LEGACY_REGISTRY_PATH,
        "message": format!("a second plugin registry exists at the legacy location {LEGACY_REGISTRY_PATH} and differs from the registry at {REGISTRY_PATH}; it is never read (the registry at {REGISTRY_PATH} is authoritative). Remove it, or — if it is the one the OS last wrote — restore it over {REGISTRY_PATH} from version control and re-register what differs")}),
    ]
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
/// `capabilities::governance::register` after its governance checks. A registry still at the legacy location is
/// moved first ([`relocate`]), so the registration is written where it survives deletion of the generated views.
pub fn record(p: &Project, r: Registration) -> Result<Value> {
    relocate(p)?;
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

/// Seal the registry document as a whole as well (in addition to each entry), so that a changed registry file is
/// provably an OS write for the G2 task-close mutation scope ([`crate::t2::classify_path`]) exactly when the file is
/// what a gov operation wrote. **Only when every entry in it is one a gov operation on this machine wrote**: the OS
/// does not bless content it did not write, so a document that still carries a hand-written, edited, legacy or
/// foreign entry is left without a document seal (the entry itself is never honoured and is reported).
fn seal_document(doc: &mut Value, operation: &str) -> Result<()> {
    if let Some(o) = doc.as_object_mut() {
        o.remove(crate::t2::SEAL_FIELD);
    }
    let all_bound = doc
        .get("plugins")
        .and_then(|m| m.as_object())
        .map(|m| m.iter().all(|(k, e)| binding_of(k, e).is_verified()))
        .unwrap_or(true);
    if !all_bound {
        return Ok(());
    }
    crate::t2::seal_value(doc, "", operation)
}

/// Remove a registration (the descriptor keeps existing; it simply stops being registered). A registry still at the
/// legacy location is moved first ([`relocate`]).
pub fn remove(p: &Project, plugin_id: &str) -> Result<bool> {
    relocate(p)?;
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

/// The T2 binding of the registry document as a whole (what `t2::classify_path` sees for the file it is read from).
pub fn document_binding(p: &Project) -> Binding {
    match source(p) {
        Some(rel) => crate::t2::verify_file(&p.root, rel),
        None => Binding::Unsealed,
    }
}

/// **The registry's rows for the T2 audit (WS-2 R3-11; consumed by [`crate::t2::audit`], WS-3).** One row per
/// registry entry that no gov operation on this machine produced as it stands (hand-written, edited, legacy
/// unsealed, sealed by another machine), plus one row for the document when its own seal is present but does not
/// verify (edited after the OS wrote it) while every entry verifies. Row shape as `t2::audit`'s: `id`, `type`,
/// `path`, `t2`. An entry that verifies is not listed; an absent registry lists nothing.
pub fn t2_audit(p: &Project) -> Vec<Value> {
    let Some(rel) = source(p) else {
        return vec![];
    };
    let doc = load(p);
    let mut rows: Vec<Value> = doc
        .get("plugins")
        .and_then(|m| m.as_object())
        .map(|m| {
            m.iter()
                .map(|(k, e)| (k, binding_of(k, e)))
                .filter(|(_, b)| !b.is_verified())
                .map(|(k, b)| json!({"id": format!("{STORE_ID}:{k}"), "type": "plugin-registration", "plugin_id": k, "path": rel, "t2": b.to_value()}))
                .collect()
        })
        .unwrap_or_default();
    if rows.is_empty() && doc.get(crate::t2::SEAL_FIELD).is_some() {
        let b = crate::t2::verify_value(&doc, "");
        if !b.is_verified() {
            rows.push(
                json!({"id": STORE_ID, "type": "plugin-registry", "path": rel, "t2": b.to_value()}),
            );
        }
    }
    rows
}

/// The registry as `gov plugins registry` shows it: every entry with its T2 binding stated beside it, the file it
/// was read from and any location anomaly.
pub fn report(p: &Project) -> Value {
    let whole = document_binding(p);
    let mut doc = load(p);
    doc["document_t2"] = whole.to_value();
    doc["read_from"] = json!(source(p));
    doc["location"] = json!(REGISTRY_PATH);
    doc["location_findings"] = json!(location_findings(p));
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

#[cfg(test)]
mod tests {
    use super::*;

    fn project() -> Project {
        let d = std::env::temp_dir().join(format!("gov-registry-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&d).unwrap();
        Project::open(&d)
    }

    fn put(p: &Project, rel: &str, v: &Value) {
        write_json(&p.root.join(rel), v).unwrap();
    }

    #[test]
    fn the_location_and_the_legacy_location_are_the_kernel_store_declaration() {
        let s = crate::paths::os_store(STORE_ID).expect("the registry is a declared OS store");
        assert_eq!(s.moves, &[(LEGACY_REGISTRY_PATH, REGISTRY_PATH)]);
        assert!(s.tracked && s.class == "authoritative");
        assert!(!REGISTRY_PATH.starts_with("governance/generated/"));
    }

    /// Reading never moves anything; the legacy file is read only while no registry exists where it belongs.
    #[test]
    fn the_legacy_registry_is_read_only_until_one_exists_where_it_belongs() {
        let p = project();
        assert_eq!(source(&p), None);
        assert_eq!(load(&p)["plugins"], json!({}));
        put(
            &p,
            LEGACY_REGISTRY_PATH,
            &json!({"schema_version": "1.1.0", "plugins": {"old": {"plugin_id": "old"}}}),
        );
        assert_eq!(source(&p), Some(LEGACY_REGISTRY_PATH));
        assert!(load(&p)["plugins"]["old"].is_object());
        assert!(
            legacy_path(&p).exists() && !path(&p).exists(),
            "a read moved the registry"
        );
        put(
            &p,
            REGISTRY_PATH,
            &json!({"schema_version": "1.1.0", "plugins": {"new": {"plugin_id": "new"}}}),
        );
        assert_eq!(source(&p), Some(REGISTRY_PATH));
        assert!(
            load(&p)["plugins"]["old"].is_null(),
            "the legacy file was read although a registry exists where it belongs"
        );
        assert_eq!(location_findings(&p).len(), 1);
        let _ = std::fs::remove_dir_all(&p.root);
    }

    /// The move carries the bytes as they are (seals included, nothing re-sealed); a differing legacy file never
    /// overwrites the registry and is left in place; an identical one is removed.
    #[test]
    fn relocation_moves_the_bytes_unchanged_and_never_overwrites() {
        let p = project();
        put(
            &p,
            LEGACY_REGISTRY_PATH,
            &json!({"plugins": {"a": {"plugin_id": "a", "os_binding": {"mac": "x"}}}}),
        );
        let bytes = std::fs::read(legacy_path(&p)).unwrap();
        let moved = relocate(&p).unwrap();
        assert_eq!(moved[0]["action"], "moved");
        assert_eq!(std::fs::read(path(&p)).unwrap(), bytes);
        assert!(!legacy_path(&p).exists());
        assert!(relocate(&p).unwrap().is_empty(), "idempotent");
        // a differing legacy file: the registry where it belongs is authoritative
        put(
            &p,
            LEGACY_REGISTRY_PATH,
            &json!({"plugins": {"forged": {"plugin_id": "forged"}}}),
        );
        let legacy_bytes = std::fs::read(legacy_path(&p)).unwrap();
        let r = relocate(&p).unwrap();
        assert_eq!(r[0]["action"], "left in place");
        assert_eq!(std::fs::read(path(&p)).unwrap(), bytes);
        assert_eq!(std::fs::read(legacy_path(&p)).unwrap(), legacy_bytes);
        assert_eq!(
            location_findings(&p)[0]["code"],
            "PLUGIN_REGISTRY_LOCATION_CONFLICT"
        );
        assert_eq!(location_findings(&p)[0]["severity"], "low");
        // an identical copy is simply removed
        std::fs::write(legacy_path(&p), &bytes).unwrap();
        assert_eq!(
            relocate(&p).unwrap()[0]["action"],
            "removed identical legacy copy"
        );
        assert!(!legacy_path(&p).exists() && location_findings(&p).is_empty());
        let _ = std::fs::remove_dir_all(&p.root);
    }

    /// WS-2 R3-11: every entry no gov operation produced as it stands is a T2 audit row (the cases below need no
    /// machine key: an unsealed entry, and an entry recorded under another plugin's id).
    #[test]
    fn t2_audit_rows_name_every_entry_the_os_did_not_write() {
        let p = project();
        assert!(t2_audit(&p).is_empty());
        put(
            &p,
            REGISTRY_PATH,
            &json!({"plugins": {
            "hand": {"plugin_id": "hand", "capability": "embed", "version": "1"},
            "renamed": {"plugin_id": "other", "os_binding": {"alg": crate::t2::SEAL_ALG, "key_id": "k", "operation": SEAL_OPERATION, "at": "t", "mac": "00"}}}}),
        );
        let rows = t2_audit(&p);
        assert_eq!(rows.len(), 2, "{rows:?}");
        for r in &rows {
            assert_eq!(r["type"], "plugin-registration");
            assert_eq!(r["path"], REGISTRY_PATH);
            assert_ne!(r["t2"]["binding"], "VERIFIED");
        }
        let hand = rows.iter().find(|r| r["plugin_id"] == "hand").unwrap();
        assert_eq!(hand["t2"]["binding"], "UNSEALED");
        assert_eq!(hand["id"], "plugin-registry:hand");
        let renamed = rows.iter().find(|r| r["plugin_id"] == "renamed").unwrap();
        assert_eq!(renamed["t2"]["binding"], "BROKEN");
        let _ = std::fs::remove_dir_all(&p.root);
    }
}
