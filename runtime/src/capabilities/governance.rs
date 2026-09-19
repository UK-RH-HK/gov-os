//! Capability/plugin supply-chain boundary (framework §28–32, TOOL_POLICY.plugins; verifier H-N2; Phase-2 repair
//! iteration 1, WS-7: BC-P2-39, BC-P2-40, BC-P2-11 plugin side, BC-P2-09 registry side).
//!
//! No executable capability runs merely because a descriptor exists. Before a plugin is used by any path
//! (`capabilities invoke`, the indexer, retrieval, benchmarks, code intelligence, `plugins health --ping`) it must be:
//! a schema-valid descriptor with a stable identity and version; healthy (program resolvable); authorised for the
//! acting role (authority floor, approved roles, permission classes); bound — every byte it executes is the
//! registered implementation ([`super::binding`]); and, **because the OS cannot confine what a spawned process does,
//! registered and approved whatever it declares** ([`super::binding::ExecutionClass`]):
//!
//! * an **executable** plugin (a script, an interpreter with a module or inline code, a binary) runs only with a
//!   registry entry `gov plugins register` wrote and sealed on this machine (T2) and a presented, owner-answered gate
//!   raised for exactly that registration subject — identity, version, descriptor, implementation, permission set —
//!   re-verified at every execution ([`crate::orchestration::gates::human_approval_for`]); a revoked gate, a declined
//!   answer, an answer to another question, a forged or foreign registry entry, or a changed byte stops it;
//! * an **OS-provided** capability server (this `gov` binary's own `capabilities serve-embed`) is non-elevated by
//!   construction and keeps D-0005's hand-declared allowance.
//!
//! A descriptor's own `permissions` / `required_permission_classes` can only narrow (the role must hold the classes)
//! and are shown to the approver; they never decide whether approval is needed (Contract v3 F4:426, :430; ARCH-0003
//! §9). Every refusal is a typed, auditable error and the plugin is listed as `denied`/`rejected`, never silently
//! skipped; doctor D028 and the `plugin_governance` suite family report integrity failures whatever the acting role.
use super::binding::{self, ExecutionClass, Implementation};
use super::host::discover_all;
use super::protocol::PluginDescriptor;
use super::registry::{self, Standing};
use crate::orchestration::gates;
use crate::records::RecordStore;
use crate::util::now_iso;
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::Path;

#[derive(Debug, Clone, Default, serde::Serialize)]
pub struct PluginSet {
    /// Descriptors the acting role may execute (validated, registered and approved or OS-provided, healthy, bound,
    /// authorised).
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

/// Where a plugin's own code lives (module package, script, or program), for the `SRR-R0-L6` acquisition class.
/// `None` means no local implementation resolved, which `SRR-R0-L6` treats as remotely acquired.
pub fn resolve_implementation(desc: &PluginDescriptor, root: &Path) -> Option<std::path::PathBuf> {
    binding::resolve(desc, root).ok().and_then(|i| i.primary)
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
    let cwd = binding::working_dir(desc, root);
    let ok = if first.contains('/') {
        binding::resolve_program(&first, &cwd).is_some() || {
            let p = if Path::new(&first).is_absolute() {
                std::path::PathBuf::from(&first)
            } else {
                root.join(&first)
            };
            p.is_file()
        }
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
        let looks_like_file = !a.contains(char::is_whitespace)
            && (a.contains('/')
                || a.ends_with(".py")
                || a.ends_with(".sh")
                || a.ends_with(".js")
                || a.ends_with(".rb")
                || a.ends_with(".pl"));
        if looks_like_file {
            let in_cwd = if Path::new(&a).is_absolute() {
                std::path::PathBuf::from(&a)
            } else {
                cwd.join(&a)
            };
            let in_root = root.join(&a);
            if !in_cwd.exists() && !in_root.exists() {
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

/// What a descriptor DECLARES about elevation (elevated permission classes from verified kernel policy, `network`,
/// `filesystem_write`). Shown to the approver and recorded; it never decides whether approval is needed (BC-P2-39).
fn declared_elevation(v: &Value, required: &[String], elevated: &[String]) -> Vec<String> {
    let mut out: Vec<String> = required
        .iter()
        .filter(|r| elevated.contains(r))
        .cloned()
        .collect();
    for k in ["network", "filesystem_write"] {
        if v.get("permissions")
            .and_then(|x| x.get(k))
            .and_then(|b| b.as_bool())
            .unwrap_or(false)
        {
            out.push(format!("permissions.{k}"));
        }
    }
    out
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

// ------------------------------------------------------------------------------------------ approvals by subject

/// Where the approval of one subject (a plugin registration, a tool installation) stands.
#[derive(Debug, Clone)]
pub enum SubjectApproval {
    /// A presented, owner-signed, authorising answer on a gate raised for exactly this subject.
    Approved(gates::VerifiedAnswer),
    /// The human declined this exact subject: the request ends here (a changed subject is a new request; the gate
    /// can be withdrawn with `gov gate revoke`).
    Declined { gate: String, option: String },
    /// A gate for this subject is raised and not answered yet.
    Pending { gate: String },
    /// No gate for this subject is usable; `not_honoured` lists every candidate and why it was not honoured.
    None { not_honoured: Vec<Value> },
}

/// **The approval of one subject, read only through WS-3's gate API.** Candidates are the gates whose OS-written
/// (T2-verified) record carries `subject: {kind: <kind>, sha256: <sha>}` — the subject the OS raised them for — plus
/// any gate id the caller cites; a cited gate raised for anything else is reported and never honoured (a gate
/// approves only what it was raised for: Contract v3:430, :678). Each candidate is evaluated with
/// [`gates::human_approval_for`]: T2-bound, presented, answered by an owner-signed human answer that re-verifies
/// against the current anchor, authorising, and bound to exactly this subject digest.
pub fn approval_for_subject(
    p: &Project,
    kind: &str,
    sha: &str,
    cited: &[String],
) -> SubjectApproval {
    let store = RecordStore::load(&p.root);
    let mut not_honoured: Vec<Value> = vec![];
    let mut candidates: Vec<String> = vec![];
    let for_subject = |r: &crate::records::Record| {
        r.data["subject"]["kind"].as_str() == Some(kind)
            && r.data["subject"]["sha256"].as_str() == Some(sha)
    };
    for c in cited.iter().filter(|c| !c.is_empty()) {
        match store.get(c).filter(|r| r.rtype() == "human-gate") {
            None => not_honoured.push(json!({"gate": c, "code": "GATE_NOT_FOUND", "reason": "cited gate does not exist"})),
            Some(r) if !for_subject(r) => not_honoured.push(json!({"gate": c, "code": "GATE_MISMATCH",
                "reason": format!("gate {c} was raised for {}, not for this {kind} ({sha}); a gate answer approves exactly what it was raised for",
                    if r.data["subject"].is_object() { r.data["subject"].to_string() } else { format!("'{}'", r.get("question")) })})),
            Some(_) => candidates.push(c.clone()),
        }
    }
    let mut found: Vec<&crate::records::Record> = store
        .of_type("human-gate")
        .into_iter()
        .filter(|r| for_subject(r))
        .collect();
    found.sort_by_key(|r| std::cmp::Reverse(r.id()));
    for r in found {
        if !candidates.contains(&r.id()) {
            candidates.push(r.id());
        }
    }
    let mut declined = None;
    let mut pending = None;
    for gid in candidates {
        let rec = store.get(&gid);
        if let Some(r) = rec {
            let b = crate::t2::verify_record(r);
            if !b.is_verified() {
                not_honoured.push(json!({"gate": gid, "code": "T2_UNBOUND", "t2": b.to_value()}));
                continue;
            }
        }
        match gates::human_approval_for(p, &gid, sha) {
            Ok(a) => return SubjectApproval::Approved(a),
            Err(e) => match e.code.as_str() {
                "GATE_DECLINED" => {
                    if declined.is_none() {
                        declined = Some((
                            gid.clone(),
                            gates::answered_option(p, &gid).unwrap_or_default(),
                        ));
                    }
                }
                "GATE_NOT_ANSWERED" => {
                    if pending.is_none() {
                        pending = Some(gid.clone());
                    }
                }
                _ => not_honoured.push(json!({"gate": gid, "code": e.code, "reason": e.message})),
            },
        }
    }
    if let Some((gate, option)) = declined {
        return SubjectApproval::Declined { gate, option };
    }
    if let Some(gate) = pending {
        return SubjectApproval::Pending { gate };
    }
    SubjectApproval::None { not_honoured }
}

// ------------------------------------------------------------------------------------------ authorisation

fn refuse(
    code: &str,
    msg: String,
    desc: &PluginDescriptor,
    checks: &[Value],
    extra: Value,
) -> GovError {
    let mut d = json!({"plugin_id": desc.plugin_id, "checks": checks});
    if let (Some(o), Some(x)) = (d.as_object_mut(), extra.as_object()) {
        for (k, v) in x {
            o.insert(k.clone(), v.clone());
        }
    }
    GovError::new(code, msg).with_details(d)
}

fn impl_diff(entry: &Value, imp: &Implementation) -> Value {
    let reg: Vec<(String, String)> = entry["implementation"]
        .as_array()
        .map(|a| {
            a.iter()
                .map(|f| {
                    (
                        f["path"].as_str().unwrap_or("").to_string(),
                        f["sha256"].as_str().unwrap_or("").to_string(),
                    )
                })
                .collect()
        })
        .unwrap_or_default();
    let now: Vec<(String, String)> = imp
        .files
        .iter()
        .map(|f| (f.path.clone(), f.sha256.clone()))
        .collect();
    let changed: Vec<&String> = now
        .iter()
        .filter(|(p, h)| reg.iter().any(|(rp, rh)| rp == p && rh != h))
        .map(|(p, _)| p)
        .collect();
    let added: Vec<&String> = now
        .iter()
        .filter(|(p, _)| !reg.iter().any(|(rp, _)| rp == p))
        .map(|(p, _)| p)
        .collect();
    let removed: Vec<&String> = reg
        .iter()
        .filter(|(p, _)| !now.iter().any(|(np, _)| np == p))
        .map(|(p, _)| p)
        .collect();
    json!({"changed": changed, "added": added, "removed": removed})
}

/// Authorise `desc` for the acting role. Ok(grant) or a typed refusal.
///
/// Trust sources: the authority floor and permission classes come from verified kernel policy
/// (`kernel_trust`-backed `PolicySet`); registration, approved roles and the approving gate come from the OS-written,
/// T2-verified plugin registry; whether approval is needed comes from what the command executes
/// ([`binding::resolve`]); the approval itself is a verified gate answer bound to the registration subject. Only the
/// command, capability and version come from the descriptor — and they are bound by the registration.
pub fn authorize(p: &Project, desc: &PluginDescriptor) -> Result<Value> {
    let pol = p.policies();
    let mut checks = vec![];
    let level = role_level(p)?;
    let min = parse_level(&pol.get_str("TOOL_POLICY", "plugins.min_authority", "L2"));
    let claims = self_authorising_claims(desc);

    // 0. standing: a forged/foreign registry entry is never honoured; an edited, re-versioned or re-purposed
    //    descriptor never matches its registration -> fail closed
    let standing = registry::standing(p, desc);
    match &standing {
        Standing::Mismatched(why) => {
            checks.push(json!({"check": "registry_binding", "ok": false, "detail": why}));
            return Err(refuse(
                "PLUGIN_REGISTRY_MISMATCH",
                why.clone(),
                desc,
                &checks,
                json!({"registry": registry::shown_path(p)}),
            ));
        }
        Standing::Unbound { binding } => {
            checks.push(
                json!({"check": "registry_binding", "ok": false, "detail": binding.to_value()}),
            );
            return Err(refuse("PLUGIN_REGISTRATION_UNBOUND", format!(
                "plugin '{}' has a registry entry in {} that no `gov plugins register` on this machine produced as it stands (T2 binding {}): a hand-written, edited, legacy or foreign registration is a request, recorded and ignored (D-0007 rule 2). Re-register it with `gov plugins register`.",
                desc.plugin_id, registry::shown_path(p), binding.code()), desc, &checks, json!({"t2": binding.to_value(), "registry": registry::shown_path(p)})));
        }
        _ => {}
    }
    let reg: Option<Value> = match &standing {
        Standing::Registered(e) => Some((**e).clone()),
        _ => None,
    };
    let registered = reg.is_some();
    checks.push(json!({"check": "registry_binding", "ok": true, "detail": if registered { format!("registered in {} (T2-verified; identity, version and descriptor content bound)", registry::shown_path(p)) } else { "hand-declared descriptor (no registration record)".to_string() }, "descriptor_claims_ignored": claims}));

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

    // 3. permission classes: the role must hold every class either side declares (a declaration may only add needs)
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
        return Err(refuse("PLUGIN_NOT_AUTHORIZED", format!("plugin '{}' requires permission classes {missing:?} that role '{}' does not hold (TOOL_PERMISSIONS)", desc.plugin_id, p.role), desc, &checks, json!({})));
    }

    // 4. health: the program must resolve
    let (healthy, hmsg) = health_static(desc, &p.root);
    checks.push(json!({"check": "health", "ok": healthy, "detail": hmsg}));
    if !healthy {
        return Err(refuse(
            "PLUGIN_UNHEALTHY",
            format!(
                "plugin '{}' failed its health check: {hmsg}",
                desc.plugin_id
            ),
            desc,
            &checks,
            json!({}),
        ));
    }

    // 5. what the command executes, derived by the OS (BC-P2-39 class, BC-P2-40 bytes)
    let imp = match binding::resolve(desc, &p.root) {
        Ok(i) => i,
        Err(e) => {
            checks
                .push(json!({"check": "implementation_binding", "ok": false, "detail": e.message}));
            return Err(refuse(&e.code, e.message.clone(), desc, &checks, json!({})));
        }
    };
    let elevated = pol.get_list("TOOL_POLICY", "plugins.elevated_permission_classes");
    let declared_elevated = declared_elevation(&desc.raw, &required, &elevated);
    checks.push(json!({"check": "execution_class", "ok": true, "detail": format!("{} ({})", imp.class.as_str(), if imp.class == ExecutionClass::OsProvided { "this gov binary serving an OS capability endpoint: non-elevated by construction" } else { "an unsandboxed process: its declared permissions are not enforced, so it can exceed the non-elevated floor whatever it declares" }), "declared_elevation": declared_elevated, "declared_elevation_decides_nothing": true}));

    // 6. an executable plugin runs only as a registered one (the registry is the only proof)
    if imp.class == ExecutionClass::Executable && !registered {
        checks.push(json!({"check": "registration", "ok": false, "detail": "an executable plugin needs an OS-written registration and an answered gate raised for it"}));
        return Err(refuse("PLUGIN_NOT_APPROVED", format!(
            "plugin '{}' is an executable plugin (it runs `{}` as an unsandboxed process with the invoking account's authority). The OS cannot enforce what its descriptor declares (permissions {} / classes {:?}), so whether it may run is never decided by those declarations (Contract v3 F4:426, :430; ARCH-0003 §9): it runs only when registered with `gov plugins register`, which raises a Human Decision Gate for exactly this plugin identity, version, implementation and permission set, and the human answers it A{}",
            desc.plugin_id, imp.program, desc.raw.get("permissions").cloned().unwrap_or(json!({})), desc.required_permission_classes,
            if claims.is_empty() { String::new() } else { format!("; ignored descriptor claims: {claims:?}") }),
            desc, &checks, json!({"cause": "UNREGISTERED_EXECUTABLE", "execution_class": imp.class.as_str(), "implementation": imp.to_value(), "remediation": "gov plugins register --descriptor <file> (as an install-authority role); present the gate it raises; the product owner answers it through the human channel; register again"})));
    }

    // 7. bytes: the declared pin, and the registered implementation, must equal what the command executes now.
    //    Contract v3 F4:429 makes drift fail closed whatever the policy says; a kernel whose
    //    TOOL_POLICY.plugins.refuse_on_pin_drift is false is reported beside the refusal, never obeyed.
    let drift_policy = pol.get_bool("TOOL_POLICY", "plugins.refuse_on_pin_drift", true);
    checks.push(json!({"check": "pin_drift_policy", "ok": true, "detail": if drift_policy { "TOOL_POLICY.plugins.refuse_on_pin_drift: true (drift fails closed)" } else { "TOOL_POLICY.plugins.refuse_on_pin_drift is false, but drift fails closed regardless (Contract v3 F4:429)" }}));
    if let Some(declared) = &desc.pin_sha256 {
        let ok = declared == &imp.sha256;
        checks.push(json!({"check": "pin_sha256", "ok": ok, "detail": format!("declared {declared}, observed {}", imp.sha256)}));
        if !ok {
            return Err(refuse("PLUGIN_PIN_MISMATCH", format!("plugin '{}' implementation does not match its declared pin (sha256 {declared}); re-register after review", desc.plugin_id), desc, &checks, json!({"implementation": imp.to_value()})));
        }
    }
    if let Some(e) = &reg {
        let reg_impl = e
            .get("implementation_sha256")
            .and_then(|v| v.as_str())
            .unwrap_or("");
        let ok = !reg_impl.is_empty() && reg_impl == imp.sha256;
        checks.push(json!({"check": "registered_implementation", "ok": ok, "detail": format!("registered {reg_impl:?}, observed {}", imp.sha256)}));
        if !ok {
            return Err(refuse("PLUGIN_PIN_MISMATCH", format!(
                "plugin '{}' implementation does not match the registered content hash (registered {}, observed {}); a changed byte never runs under an old approval — re-register after review",
                desc.plugin_id, if reg_impl.is_empty() { "(none: a registration that predates implementation binding)" } else { reg_impl }, imp.sha256),
                desc, &checks, json!({"difference": impl_diff(e, &imp), "implementation": imp.to_value()})));
        }
    }

    // 8. approval: an executable registration is honoured only through a verified answer bound to its subject
    let mut gate_used = Value::Null;
    if imp.class == ExecutionClass::Executable {
        let e = reg.as_ref().expect("registered checked above");
        let subject = e
            .get("registration_subject_sha256")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        let (_, now_subject) = binding::registration_subject(&desc.raw, &imp);
        let gate = e
            .get("registration_gate")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        let verdict = if subject.is_empty() || gate.is_empty() {
            Err(GovError::new("GATE_NOT_FOUND", "the registration records no approving gate or subject (a registration that predates BC-P2-39 binding)"))
        } else if subject != now_subject {
            Err(GovError::new("APPROVAL_STALE", format!("the registration subject is {subject} but the descriptor and implementation now describe {now_subject}")))
        } else {
            gates::human_approval_for(p, &gate, &subject)
        };
        match verdict {
            Ok(a) => {
                checks.push(json!({"check": "registration_approved", "ok": true, "detail": format!("gate {gate} answered {} by {} ({}), bound to subject {subject}", a.option, a.answered_by, a.by_kind)}));
                gate_used = json!(gate);
            }
            Err(x) => {
                checks.push(json!({"check": "registration_approved", "ok": false, "detail": format!("{}: {}", x.code, x.message)}));
                return Err(refuse("PLUGIN_NOT_APPROVED", format!(
                    "plugin '{}' is registered but its registration is not approved now: {} ({}). An executable plugin runs only while the presented, owner-answered gate raised for exactly its registration subject authorises it; re-register to raise a new gate",
                    desc.plugin_id, x.message, x.code), desc, &checks, json!({"cause": x.code, "gate": gate, "registration_subject_sha256": subject})));
            }
        }
    }
    Ok(
        json!({"plugin_id": desc.plugin_id, "capability": desc.capability, "version": desc.version, "role": p.role, "level": format!("L{level}"), "registered": registered, "execution_class": imp.class.as_str(), "implementation_sha256": imp.sha256, "pin_sha256": imp.sha256, "registration_gate": gate_used, "ignored_descriptor_claims": claims, "checks": checks}),
    )
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

fn gate_package(
    id: &str,
    desc: &PluginDescriptor,
    imp: &Implementation,
    subject: &str,
    required: &[String],
    previous: Option<&Value>,
    change: Option<&Value>,
) -> Value {
    let files: Vec<String> = imp
        .files
        .iter()
        .map(|f| format!("{} ({}) sha256 {}", f.path, f.role, f.sha256))
        .collect();
    let declared_of = |role: &str| -> Vec<String> {
        imp.files
            .iter()
            .filter(|f| f.role == role)
            .map(|f| f.path.clone())
            .collect()
    };
    let (model, runtime) = (declared_of("model"), declared_of("runtime"));
    let components = if model.is_empty() && runtime.is_empty() {
        String::new()
    } else {
        format!(" It loads the declared model artefacts {model:?} and runtime artefacts {runtime:?} (bound above: a changed model or runtime byte stops the plugin until a new approval).")
    };
    let prior = previous
        .and_then(|e| e.get("implementation_sha256").and_then(|v| v.as_str()))
        .map(|h| {
            if h == imp.sha256 {
                format!("The tracked registry already records this implementation ({h}).")
            } else {
                format!("The tracked registry records a DIFFERENT implementation for this plugin id (registered {h}, now {}): approving re-baselines the plugin onto the bytes listed here.", imp.sha256)
            }
        })
        .unwrap_or_else(|| "No earlier registration of this plugin id is recorded.".to_string());
    // INT3-O1 (Contract v3 K3, F4): the registration is also a material governance/security change, carried out by
    // its own change transaction; this gate approves the plugin's execution, that transaction's own gate approves
    // the change. Each names the other; neither answer stands in for the other.
    let change_text = change
        .map(|c| {
            format!(
                " The registration is written only by change transaction {} (CIT-P simulated automatically: impact radius {}, effective triggers {}; {}), whose own gate {} approves the change itself: answering this gate approves the plugin's execution, not the change.",
                c["cit"].as_str().unwrap_or("?"),
                c["radius"].as_str().unwrap_or("?"),
                c["effective_triggers"],
                c["consequences"]
                    .as_array()
                    .map(|a| a.iter().filter_map(|x| x.as_str()).collect::<Vec<_>>().join("; "))
                    .unwrap_or_default(),
                c["human_gate"].as_str().unwrap_or("(none required)"),
            )
        })
        .unwrap_or_default();
    let mut subject_v = json!({"kind": "plugin-registration", "id": id, "version": desc.version, "sha256": subject, "implementation_sha256": imp.sha256});
    if let Some(c) = change {
        subject_v["change_transaction"] = json!({"cit": c["cit"], "human_gate": c["human_gate"], "binding_sha256": c["binding_sha256"]});
    }
    json!({
        "question": format!("Approve plugin {id} v{} ({}) to execute: it runs {:?} (working directory {}) as an unsandboxed process with the invoking account's authority?", desc.version, desc.capability, desc.command, desc.cwd.clone().unwrap_or_else(|| ".".into())),
        "why_now": "a capability plugin was submitted for registration; the OS cannot enforce the permissions a plugin declares, so every executable plugin runs only after this specific approval (BC-P2-39)",
        "current_state": format!("plugin {id} is not registered and does not run. {prior}"),
        "options": [
            {"id": "A", "description": format!("approve execution of exactly this implementation (subject {subject})")},
            {"id": "B", "description": "refuse: the plugin stays unregistered and never runs"}
        ],
        "impact": format!("implementation sha256 {} = {}; declared permissions {} and permission classes {:?} are shown for review and are NOT enforced at run time; roles allowed to trigger it: {:?}.{components}",
            imp.sha256, files.join("; "), desc.raw.get("permissions").cloned().unwrap_or(json!({})), required,
            if desc.approved_roles.is_empty() { vec!["all (subject to TOOL_POLICY.plugins.min_authority)".to_string()] } else { desc.approved_roles.clone() }) + &change_text,
        "reversibility": "reversible: gov plugins unregister, or gov gate revoke on this gate, stops the plugin at its next execution",
        "recommendation": "A only after reviewing the command, every bound file and the declared permissions; B otherwise",
        "confidence": 0.5,
        "trigger": "privilege_elevation",
        "impact_radius": "R3",
        "plugin_id": id,
        "subject": subject_v,
    })
}

/// A registration request as the OS derives it **before any approval is asked or any byte is written**: the
/// schema-valid descriptor, a healthy program, the implementation binding, the acquisition verdict (SRR-R0-L6 and
/// `OWNER-DECISION-0006` §6 bullet 5, asked unconditionally by [`prepare`]) and the registration subject a gate
/// approves. Only [`prepare`] constructs one, so the one registration writer ([`write_registration`]) can only run
/// after the acquisition sink was asked for exactly this request.
struct Prepared {
    id: String,
    dest: std::path::PathBuf,
    tmp: PluginDescriptor,
    imp: Implementation,
    acquisition_verdict: Value,
    required: Vec<String>,
    declared_elevated: Vec<String>,
    normalized: Value,
    subject_doc: Value,
    subject: String,
    previous: Option<Value>,
    cited: Vec<String>,
}

impl Prepared {
    fn dest_rel(&self) -> String {
        format!("governance/project/plugins/{}.yaml", self.id)
    }
}

fn prepare(p: &Project, mut descriptor: Value) -> Result<Prepared> {
    let id = descriptor["plugin_id"].as_str().unwrap_or("").to_string();
    if id.is_empty() {
        return Err(GovError::new("USAGE", "descriptor requires plugin_id"));
    }
    let Some(o) = descriptor.as_object_mut() else {
        return Err(GovError::new("USAGE", "descriptor must be an object"));
    };
    o.remove("provenance");
    o.remove(crate::t2::SEAL_FIELD);
    // a gate id in the descriptor is a request naming a candidate approval, never the approval itself
    let cited: Vec<String> = descriptor
        .get("registration_gate")
        .and_then(|v| v.as_str())
        .map(|s| vec![s.to_string()])
        .unwrap_or_default();
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
    let imp = binding::resolve(&tmp, &p.root)?;
    // `SRR-R0-L6` — built-in/local capabilities versus remotely acquired privileged plugins, tools and profiles.
    // The class is derived from where the implementation bytes actually are (the module package, script or program
    // the OS just resolved), never from what the descriptor says about itself. A privileged capability whose bytes
    // came from outside the verified release payload and outside the governed project must be authorised by a
    // delegated signed target in the verified release metadata.
    let acquisition = crate::srr::plugins::classify(
        &p.root,
        &crate::kernel_trust::trusted_root(p),
        imp.primary.as_deref(),
    );
    let channel = crate::srr::state::MachineState::open()
        .ok()
        .and_then(|ms| crate::srr::state::InstalledRecord::load(&ms, crate::FRAMEWORK_NAME))
        .map(|r| r.channel)
        .unwrap_or_default();
    // Delegated targets are carried by the verified release metadata of the installed release. Until a signed
    // delegation exists for a capability, a privileged remotely-acquired one is refused rather than admitted.
    let acquisition_verdict =
        crate::srr::plugins::guard_acquisition(&id, &descriptor, acquisition, &[], &channel)?;
    let required: Vec<String> = tmp.required_permission_classes.clone();
    // declared elevation only raises the stated impact of the gate; every executable plugin needs the gate anyway
    let elevated = p
        .policies()
        .get_list("TOOL_POLICY", "plugins.elevated_permission_classes");
    let declared_elevated = declared_elevation(&descriptor, &required, &elevated);
    let normalized = binding::normalized_descriptor(&descriptor);
    let (subject_doc, subject) = binding::registration_subject(&descriptor, &imp);
    let previous = registry::entry(p, &id);
    Ok(Prepared {
        id,
        dest,
        tmp,
        imp,
        acquisition_verdict,
        required,
        declared_elevated,
        normalized,
        subject_doc,
        subject,
        previous,
        cited,
    })
}

/// **The one writer of a registration** (the descriptor the OS normalises and the sealed registry entry). It takes
/// a [`Prepared`] — proof that the acquisition sink was asked for exactly this request — and is reached only from the
/// execution of the registration's own change transaction ([`apply_registration`], CIT-E), after the execution
/// approval was re-verified there.
fn write_registration(
    p: &Project,
    prep: &Prepared,
    gate_id: &Value,
    change_transaction: &str,
) -> Result<(Value, Value)> {
    let mut descriptor = prep.normalized.clone();
    descriptor["pin"] = json!({"sha256": prep.imp.sha256, "files": prep.imp.paths()});
    descriptor["provenance"] = json!({"registered_by_session": p.session_id, "registered_by_role": p.role, "registered_at": now_iso(), "gate": gate_id, "method": "gov plugins register", "change_transaction": change_transaction});
    descriptor["status"] = json!("active");
    if let Some(d) = prep.dest.parent() {
        std::fs::create_dir_all(d)?;
    }
    crate::util::write_yaml(&prep.dest, &descriptor)?;
    // The authoritative record lives OUTSIDE the descriptor (verifier V-H1): identity, version, descriptor content
    // hash, implementation, subject, approved roles, permission classes and the approving gate are written — and
    // sealed (T2) — by the OS.
    let written = PluginDescriptor::from_value(&descriptor, &prep.dest.to_string_lossy())
        .ok_or_else(|| GovError::new("USAGE", "descriptor is not a plugin descriptor"))?;
    let dsha = registry::descriptor_hash(&written).ok_or_else(|| {
        GovError::new(
            "IO_ERROR",
            format!(
                "cannot read the registered descriptor at {}",
                prep.dest.display()
            ),
        )
    })?;
    let approved_roles: Vec<String> = strings(&descriptor, "approved_roles");
    let entry = registry::record(
        p,
        registry::Registration {
            desc: &written,
            descriptor_sha256: &dsha,
            implementation: &prep.imp,
            subject_sha256: &prep.subject,
            approved_roles: &approved_roles,
            required_permission_classes: &prep.required,
            permissions: descriptor.get("permissions").cloned().unwrap_or(json!({})),
            gate: gate_id.clone(),
        },
    )?;
    let _ = crate::tools::generate_registry(p);
    Ok((descriptor, entry))
}

/// The manifest operation of a registration's change transaction: what CIT-P simulates and CIT-E applies
/// (`cit::apply_op` → [`apply_registration`]). The approval of the transaction binds it (its content digest).
fn registration_op(prep: &Prepared) -> Value {
    json!({"op": "register_plugin", "plugin_id": prep.id, "path": prep.dest_rel(), "registry": registry::REGISTRY_PATH,
        "descriptor": prep.normalized, "subject_sha256": prep.subject, "implementation_sha256": prep.imp.sha256,
        "execution_class": prep.imp.class.as_str()})
}

fn registration_proposal(prep: &Prepared) -> String {
    let approval = if prep.imp.class == ExecutionClass::Executable {
        "Its execution is approved separately, by the Human Decision Gate raised for exactly this registration subject (Contract v3 F4); this transaction is the registration's change control (Contract v3 K3) and does not approve execution."
    } else {
        "It is an OS-provided capability server (non-elevated by construction, D-0005), so no execution approval is asked; this transaction is the registration's change control (Contract v3 K3)."
    };
    format!(
        "Register capability plugin {} v{} ({}): write its OS-normalised descriptor to {} and its sealed entry to {} (registration subject sha256 {}, implementation sha256 {}). {approval}",
        prep.id,
        prep.tmp.version,
        prep.tmp.capability,
        prep.dest_rel(),
        registry::REGISTRY_PATH,
        prep.subject,
        prep.imp.sha256
    )
}

/// **CIT-E side of a registration** (the `register_plugin` manifest operation; INT3-O1). The request is derived
/// again from the bytes as they are now ([`prepare`]: schema, health, binding, the acquisition sink) and must be
/// exactly the subject the transaction's approval binds; an executable plugin's execution approval (Contract v3 F4:
/// a presented, owner-answered gate raised for exactly this subject) is re-verified here, so no route into CIT-E —
/// `gov plugins register`, `gov cit execute` or a hand-proposed transaction carrying this operation — writes a
/// registration the owner did not approve. Returns the paths it wrote.
pub fn apply_registration(p: &Project, op: &Value, change_transaction: &str) -> Result<Value> {
    let prep = prepare(p, op["descriptor"].clone())?;
    let want = op["subject_sha256"].as_str().unwrap_or("");
    if prep.subject != want || op["plugin_id"].as_str() != Some(prep.id.as_str()) {
        return Err(GovError::new("PLUGIN_REGISTRATION_STALE", format!("change transaction {change_transaction} registers plugin {:?} with subject {want}, but its descriptor and the implementation bytes now give plugin '{}' subject {}: the plugin changed after the transaction was proposed and approved; nothing is written — register it again (`gov plugins register`) for a new request", op["plugin_id"], prep.id, prep.subject)).with_details(json!({"cit": change_transaction, "approved_subject": want, "current_subject": prep.subject, "implementation": prep.imp.to_value()})));
    }
    let mut gate_id = Value::Null;
    if prep.imp.class == ExecutionClass::Executable {
        match approval_for_subject(p, "plugin-registration", &prep.subject, &prep.cited) {
            SubjectApproval::Approved(a) => gate_id = json!(a.gate),
            other => {
                let (gate, state) = match &other {
                    SubjectApproval::Declined { gate, .. } => (json!(gate), "DECLINED"),
                    SubjectApproval::Pending { gate } => (json!(gate), "PENDING"),
                    _ => (Value::Null, "NONE"),
                };
                return Err(GovError::new("PLUGIN_NOT_APPROVED", format!("change transaction {change_transaction} would register executable plugin '{}', but no presented, owner-answered gate raised for exactly this registration subject authorises its execution (gate {gate}, {state}); an approved change is not an execution approval (Contract v3 F4) — nothing is written", prep.id)).with_details(json!({"cit": change_transaction, "plugin_id": prep.id, "registration_subject_sha256": prep.subject, "execution_gate": gate, "execution_gate_state": state})));
            }
        }
    }
    let legacy_before = p.root.join(registry::LEGACY_REGISTRY_PATH).exists();
    let (descriptor, entry) = write_registration(p, &prep, &gate_id, change_transaction)?;
    let mut touched = vec![prep.dest_rel(), registry::REGISTRY_PATH.to_string()];
    if legacy_before && !p.root.join(registry::LEGACY_REGISTRY_PATH).exists() {
        touched.push(registry::LEGACY_REGISTRY_PATH.to_string());
    }
    Ok(
        json!({"plugin_id": prep.id, "touched": touched, "registry_entry": entry, "pin": descriptor["pin"], "provenance": descriptor["provenance"], "execution_gate": gate_id}),
    )
}

/// What `gov plugins register` reports about the registration's change transaction.
fn change_view(p: &Project, cit: &str) -> Value {
    let store = RecordStore::load(&p.root);
    match store.get(cit) {
        Some(c) => {
            json!({"cit": cit, "cit_status": c.get("cit_status"), "human_gate": Some(c.get("human_gate")).filter(|g| !g.is_empty()),
            "radius": c.data["impact"]["radius"], "effective_triggers": c.data["impact"]["effective_triggers"],
            "binding_sha256": c.data["impact"]["binding_sha256"], "consequences": c.data["impact"]["consequences"],
            "decision": Some(c.get("decision")).filter(|d| !d.is_empty())})
        }
        None => Value::Null,
    }
}

/// Register (or re-register) a plugin descriptor as a governed act: authority, schema, acquisition class, health,
/// the implementation binding, and — for every executable plugin, whatever it declares — a presented, owner-answered
/// Human Decision Gate raised for exactly this registration subject.
///
/// **A registration is also a material governance and security change** (INT3-O1; Contract v3 K3 "auto-trigger for
/// material security, governance/policy"; F4 "elevated permissions reference authoritative gate/decision"; framework
/// §47-48 "the human should not need to type /impact"). So the OS itself proposes the registration's change
/// transaction (`cit::propose_registration`: CIT-P, simulated automatically, its own gate raised under
/// CHANGE_POLICY), and the descriptor and registry entry are written **only by that transaction's execution** (CIT-E,
/// [`apply_registration`]: snapshot, verification, index refresh, commit or rollback, per-path writes recorded and
/// sealed). Two approvals, each for what it approves, each naming the other: the execution approval (this module's
/// gate, subject `plugin-registration`, which names the transaction and its gate) and the change approval (the
/// transaction's gate, whose sealed content names the registration subject). Neither answer stands in for the other,
/// and the worker never hand-files a transaction: repeating `gov plugins register` once both are answered approves
/// and executes it. A registration made inside a claimed task therefore closes on the transaction's recorded writes
/// (task close step 10a), like any other governed change.
pub fn register(p: &Project, descriptor: Value) -> Result<Value> {
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
    let prep = prepare(p, descriptor)?;
    let id = prep.id.clone();
    let subject = prep.subject.clone();
    let common = |mut v: Value| -> Value {
        v["registration_subject_sha256"] = json!(subject);
        v["execution_class"] = json!(prep.imp.class.as_str());
        v["implementation"] = prep.imp.to_value();
        v["acquisition"] = prep.acquisition_verdict.clone();
        v
    };
    let mut gate_id = Value::Null;
    let mut approved_by = Value::Null;
    if prep.imp.class == ExecutionClass::Executable {
        match approval_for_subject(p, "plugin-registration", &subject, &prep.cited) {
            SubjectApproval::Approved(a) => {
                gate_id = json!(a.gate);
                approved_by = json!({"gate": a.gate, "option": a.option, "by_kind": a.by_kind, "answered_by": a.answered_by, "decision": a.decision});
            }
            SubjectApproval::Declined { gate, option } => {
                // the request ends here, and so does its change transaction
                let closed = crate::cit::close_registration_requests(
                    p,
                    &id,
                    Some(&subject),
                    &format!("the execution approval of this registration was declined (gate {gate}, answer '{option}')"),
                );
                return Ok(common(
                    json!({"registered": false, "declined": true, "human_gate": gate, "answer": option,
                    "reason": format!("the human declined gate {gate} for exactly this registration; the request ends here. A changed descriptor or implementation is a new request; `gov gate revoke {gate}` withdraws the refusal"),
                    "change_transactions_closed": closed}),
                ));
            }
            SubjectApproval::Pending { gate } => {
                let open = crate::cit::registration_transactions(p, &subject)
                    .into_iter()
                    .find(|(_, st)| crate::cit::is_open_status(st))
                    .map(|(c, _)| change_view(p, &c))
                    .unwrap_or(Value::Null);
                return Ok(common(
                    json!({"registered": false, "human_gate": gate, "state": "PENDING", "change_transaction": open,
                    "reason": format!("gate {gate} for exactly this registration is raised and not answered yet: `gov gate present {gate}`, then the product owner answers it through the human channel{}, then register again", open["human_gate"].as_str().map(|g| format!(" (and gate {g} of the registration's change transaction {})", open["cit"].as_str().unwrap_or("?"))).unwrap_or_default())}),
                ));
            }
            SubjectApproval::None { not_honoured } => {
                // a new request: first its change transaction (CIT-P, simulated automatically), then the execution
                // approval gate, which names the transaction and its gate
                let c = crate::cit::propose_registration(
                    p,
                    registration_op(&prep),
                    &registration_proposal(&prep),
                    &id,
                    &subject,
                )?;
                let cit = c["id"].as_str().unwrap_or("").to_string();
                let change = change_view(p, &cit);
                let mut pkg = gate_package(
                    &id,
                    &prep.tmp,
                    &prep.imp,
                    &subject,
                    &prep.required,
                    prep.previous.as_ref(),
                    Some(&change),
                );
                if !prep.declared_elevated.is_empty() {
                    pkg["impact_radius"] = json!("R4");
                    pkg["impact"] = json!(format!(
                        "{} It also DECLARES elevated access {:?}.",
                        pkg["impact"].as_str().unwrap_or(""),
                        prep.declared_elevated
                    ));
                }
                let g = gates::create_system(p, pkg)?;
                let gid = g["id"].as_str().unwrap_or("").to_string();
                crate::cit::note_registration_gate(p, &cit, &gid);
                return Ok(common(
                    json!({"registered": false, "human_gate": gid, "state": "RAISED", "gates_not_honoured": not_honoured, "change_transaction": change,
                    "reason": format!("an executable plugin runs only after a presented, owner-answered gate raised for exactly its identity, version, implementation and permission set; and a registration is a material governance and security change, carried out by change transaction {cit} (proposed and simulated by the OS) with its own gate {}. Present both gates, have the product owner answer them through the human channel, then register again (the gate is found by its subject; citing it as registration_gate is optional)", change["human_gate"].as_str().unwrap_or("(none required)"))}),
                ));
            }
        }
    }
    // --- change control: the registration is written only by its change transaction's execution
    // a registration of exactly this subject, approved by this gate, already in force: nothing changes
    if let Some(e) = prep.previous.as_ref() {
        let in_force = registry::binding_of(&id, e).is_verified()
            && e["registration_subject_sha256"].as_str() == Some(subject.as_str())
            && e["registration_gate"] == gate_id
            && std::fs::read(&prep.dest)
                .ok()
                .map(|b| crate::util::sha256_hex(&b))
                .as_deref()
                == e["descriptor_sha256"].as_str();
        if in_force {
            let d = crate::util::read_yaml(&prep.dest).unwrap_or(Value::Null);
            return Ok(common(
                json!({"registered": true, "unchanged": true, "plugin_id": id, "path": prep.dest_rel(), "pin": d["pin"], "provenance": d["provenance"], "approved_roles": d["approved_roles"], "registry": registry::REGISTRY_PATH, "registry_entry": e, "approval": approved_by, "registration_subject": prep.subject_doc,
                "change_transaction": d["provenance"]["change_transaction"].as_str().map(|c| change_view(p, c)).unwrap_or(Value::Null),
                "reason": "this registration is already in force as written by its change transaction: nothing to change"}),
            ));
        }
    }
    let linked = crate::cit::registration_transactions(p, &subject);
    let cit = match linked.iter().find(|(_, st)| crate::cit::is_open_status(st)) {
        Some((c, _)) => c.clone(),
        None => {
            if let Some((c, st)) = linked.first().filter(|(_, st)| st == "REJECTED") {
                let v = change_view(p, c);
                return Ok(common(
                    json!({"registered": false, "declined": true, "human_gate": v["human_gate"], "change_transaction": v, "approval": approved_by,
                    "reason": format!("the change transaction {c} of exactly this registration is {st} (declined through its gate, or withdrawn with the execution approval): the request ends here. A changed descriptor or implementation is a new request; withdrawing the execution approval (`gov gate revoke <gate>`) and registering again raises a new one")}),
                ));
            }
            let c = crate::cit::propose_registration(
                p,
                registration_op(&prep),
                &registration_proposal(&prep),
                &id,
                &subject,
            )?;
            c["id"].as_str().unwrap_or("").to_string()
        }
    };
    let change = change_view(p, &cit);
    match crate::cit::registration_gate_state(p, &cit) {
        crate::cit::GateState::Pending(g) => Ok(common(
            json!({"registered": false, "human_gate": g, "state": if linked.iter().any(|(c, _)| c == &cit) { "PENDING" } else { "RAISED" }, "change_transaction": change, "approval": approved_by,
            "reason": format!("the registration's change transaction {cit} (proposed and simulated by the OS: Contract v3 K3) waits on its own gate {g}; present it, have the product owner answer it through the human channel, then register again")}),
        )),
        crate::cit::GateState::Declined(g) => Ok(common(
            json!({"registered": false, "declined": true, "human_gate": g, "change_transaction": change_view(p, &cit), "approval": approved_by,
            "reason": format!("gate {g} of the registration's change transaction {cit} was declined: the change is refused and the request ends here")}),
        )),
        crate::cit::GateState::Ready => {
            let executed = crate::cit::execute_registration(p, &cit)?;
            let e = registry::entry(p, &id).unwrap_or(Value::Null);
            let d = crate::util::read_yaml(&prep.dest).unwrap_or(Value::Null);
            Ok(common(
                json!({"registered": true, "plugin_id": id, "path": prep.dest_rel(), "pin": d["pin"], "provenance": d["provenance"], "approved_roles": d["approved_roles"], "registry": registry::REGISTRY_PATH, "registry_entry": e, "approval": approved_by, "registration_subject": prep.subject_doc,
                "change_transaction": change_view(p, &cit), "execution": executed}),
            ))
        }
    }
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

/// **Role-independent integrity of one declared plugin** (for doctor D028, the suite family, `plugins health`):
/// registry binding (T2), descriptor match, implementation bytes, and the live approval of an executable
/// registration. `None` when nothing is wrong. `(code, severity, message)`.
pub fn integrity(p: &Project, desc: &PluginDescriptor) -> Option<(String, String, String)> {
    let id = &desc.plugin_id;
    let standing = registry::standing(p, desc);
    let entry = match &standing {
        Standing::Unbound { binding } => {
            return Some(("PLUGIN_REGISTRATION_UNBOUND".into(), "high".into(), format!(
                "plugin {id}: its entry in {} is not what `gov plugins register` wrote on this machine (T2 binding {}: {}); a forged, edited, legacy or foreign registration is never honoured — re-register it",
                registry::shown_path(p), binding.code(), binding.to_value()["reason"].as_str().unwrap_or(""))));
        }
        Standing::Mismatched(why) => {
            return Some((
                "PLUGIN_REGISTRY_MISMATCH".into(),
                "high".into(),
                format!("plugin {id} does not match its registration: {why}"),
            ))
        }
        Standing::Registered(e) => Some((**e).clone()),
        Standing::Unregistered => None,
    };
    let imp = match binding::resolve(desc, &p.root) {
        Ok(i) => i,
        Err(e) => {
            return Some((
                e.code.clone(),
                if entry.is_some() { "high" } else { "medium" }.into(),
                format!("plugin {id}: {}", e.message),
            ))
        }
    };
    match (&entry, imp.class) {
        (None, ExecutionClass::Executable) => Some(("PLUGIN_NOT_APPROVED".into(), "medium".into(), format!(
            "plugin {id} is an executable plugin with no registration: it never runs (whatever it declares) until `gov plugins register` and an answered gate raised for it"))),
        (None, ExecutionClass::OsProvided) => None,
        (Some(e), class) => {
            let reg_impl = e["implementation_sha256"].as_str().unwrap_or("");
            if reg_impl != imp.sha256 {
                return Some(("PLUGIN_PIN_MISMATCH".into(), "high".into(), format!(
                    "plugin {id}: the implementation it would execute ({}) is not the registered one ({}); changed: {}. It is refused at execution; re-register after review",
                    imp.sha256, if reg_impl.is_empty() { "none recorded" } else { reg_impl }, impl_diff(e, &imp))));
            }
            if class == ExecutionClass::Executable {
                let subject = e["registration_subject_sha256"].as_str().unwrap_or("");
                let gate = e["registration_gate"].as_str().unwrap_or("");
                if subject.is_empty() || gate.is_empty() {
                    return Some(("PLUGIN_NOT_APPROVED".into(), "high".into(), format!("plugin {id}: its registration records no approving gate/subject; re-register")));
                }
                if let Err(x) = gates::human_approval_for(p, gate, subject) {
                    let sev = if matches!(x.code.as_str(), "GATE_REVOKED" | "GATE_DECLINED") { "medium" } else { "high" };
                    return Some(("PLUGIN_NOT_APPROVED".into(), sev.into(), format!(
                        "plugin {id}: its registration gate {gate} does not approve it now ({}: {}); it is refused at execution", x.code, x.message)));
                }
            }
            None
        }
    }
}

fn record_health_failure(
    p: &Project,
    d: &PluginDescriptor,
    code: &str,
    message: &str,
    operation: &str,
) -> Value {
    // WS-6 IP-3: a plugin health failure is a tool failure in failure memory (idempotent per plugin/version/code;
    // a governed write that reports `not_recorded` under FREEZE_WRITES/PAUSE rather than failing the check)
    crate::memory::failures::record_tool_failure(
        p,
        &crate::memory::failures::ToolFailure {
            tool_kind: d.capability.clone(),
            tool_id: d.plugin_id.clone(),
            version: d.version.clone(),
            code: code.to_string(),
            message: message.to_string(),
            operation: operation.to_string(),
            affected: vec![d.source.clone()],
        },
        true,
    )
    .to_value()
}

/// Health report for every declared plugin (static resolution, implementation integrity, and an optional protocol
/// ping — **only** for plugins the acting role may execute: a health check never runs an unregistered or unapproved
/// plugin). Each failure is recorded in failure memory (WS-6 IP-3).
pub fn health(p: &Project, ping: bool) -> Vec<Value> {
    let (valid, rejected) = discover_all(&p.root);
    let mut out: Vec<Value> = rejected
        .into_iter()
        .map(|r| json!({"plugin_id": r["plugin_id"], "status": "rejected", "detail": r["reason"]}))
        .collect();
    for d in valid {
        let (ok, msg) = health_static(&d, &p.root);
        let grant = authorize(p, &d);
        let integ = integrity(p, &d);
        let mut row = json!({"plugin_id": d.plugin_id, "capability": d.capability, "version": d.version, "status": if ok { "healthy" } else { "unhealthy" }, "detail": msg, "authorised_for_acting_role": grant.is_ok(),
            "execution_class": grant.as_ref().ok().and_then(|g| g["execution_class"].as_str().map(String::from)),
            "integrity": integ.as_ref().map(|(c, s, m)| json!({"ok": false, "code": c, "severity": s, "message": m})).unwrap_or(json!({"ok": true}))});
        if !ok {
            row["failure_memory"] =
                record_health_failure(p, &d, "PLUGIN_UNHEALTHY", &msg, "plugins health");
        }
        if ok
            && ping
            && d.raw.get("health_check").and_then(|h| h["kind"].as_str()) == Some("protocol_ping")
        {
            if let Err(e) = &grant {
                row["ping"] = json!({"ok": false, "skipped": true, "error": e.code, "reason": "not executed: the plugin is not usable by the acting role (a health check never runs an unregistered or unapproved plugin)"});
            } else {
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
                        row["failure_memory"] = record_health_failure(
                            p,
                            &d,
                            &e.code,
                            &e.message,
                            "plugins health --ping",
                        );
                    }
                }
            }
        }
        out.push(row);
    }
    out
}

/// Findings for doctor/suite: invalid descriptors, self-authorising claims, forged/foreign registry entries,
/// registry mismatches, implementation drift, unapproved executable registrations, unregistered executables and
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
        if matches!(standing, Standing::Unregistered) && !claims.is_empty() {
            out.push(json!({"severity": "high", "plugin_id": d.plugin_id,
                "message": format!("plugin descriptor {} declares its own authorisation ({}) but no record exists in {}; the claims are ignored by the executable paths and the descriptor must be registered with `gov plugins register` or the fields removed", d.plugin_id, claims.join(", "), registry::shown_path(p)),
                "path": d.source}));
            continue;
        }
        if let Some((code, sev, msg)) = integrity(p, d) {
            let sev = if (d.plugin_id == pinned_embed || d.plugin_id == pinned_rerank)
                && sev == "medium"
            {
                "high".to_string()
            } else {
                sev
            };
            out.push(json!({"severity": sev, "plugin_id": d.plugin_id, "code": code, "message": msg, "path": d.source}));
        }
    }
    let declared: Vec<String> = valid.iter().map(|d| d.plugin_id.clone()).collect();
    for (id, b) in registry::unbound_entries(p) {
        if declared.contains(&id) {
            continue; // reported above with its descriptor
        }
        out.push(json!({"severity": "high", "plugin_id": id, "code": "PLUGIN_REGISTRATION_UNBOUND", "message": format!("plugin registry records '{id}' but no gov operation on this machine produced that entry as it stands (T2 binding {}); it is never honoured", b.code()), "path": registry::shown_path(p)}));
    }
    // BC-P2-31: a second, differing registry at the legacy location (never read; reported)
    out.extend(registry::location_findings(p));
    for id in registry::orphans(p, &declared) {
        if out
            .iter()
            .any(|f| f["plugin_id"].as_str() == Some(id.as_str()))
        {
            continue;
        }
        out.push(json!({"severity": "medium", "plugin_id": id, "message": format!("plugin registry records '{id}' but no descriptor declares it (stale registration; run `gov plugins unregister {id}`)"), "path": registry::shown_path(p)}));
    }
    for d in &set.denied {
        let id = d["plugin_id"].as_str().unwrap_or("");
        if out.iter().any(|f| f["plugin_id"].as_str() == Some(id)) {
            continue;
        }
        let sev = if d["code"] == "PLUGIN_PIN_MISMATCH"
            || d["code"] == "PLUGIN_REGISTRY_MISMATCH"
            || d["code"] == "PLUGIN_REGISTRATION_UNBOUND"
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
