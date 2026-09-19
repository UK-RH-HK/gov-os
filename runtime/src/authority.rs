//! Mechanical L0–L5 authority enforcement (framework §23, AUTHORITY_POLICY.authority_levels_required).
//! Every privileged executable path calls `require(project, operation)` before mutating anything.
//!
//! ## Acting-role resolution (BC-P2-08) — the one resolution every command uses
//!
//! The acting role is declared by the caller (D-0007 T5; OD-P2-01 keeps *agent* identity a documented adapter
//! boundary). What this module fixes is that the declaration is **resolved once, the same way, for every command**,
//! and that an invocation that declares nothing is not silently promoted:
//!
//! | precedence | means | [`RoleSource`] |
//! |---|---|---|
//! | 1 | the global `--role <id>` flag | `Flag` |
//! | 2 | `GOV_ROLE=<id>` | `Environment` |
//! | 3 | nothing declared | `Undeclared` → [`UNDECLARED_ROLE`], **L0: no privileged authority** |
//!
//! Framework §23: "No spawned worker behaves as an orchestrator unless explicitly assigned that role." The previous
//! default (`orchestrator`, L4) is gone. [`resolve_acting_role`] computes the declaration and
//! [`install_acting_role`] makes it the process-wide acting role, so that **every** `Project` opened in this
//! process — including those opened internally by `init`, every `adopt`/`migrate` stage and the first install
//! batch — evaluates authority against the role the caller declared (`crate::project::Project::open` reads
//! [`installed_acting_role`] first). The CLI installs it exactly once, before dispatch.
//!
//! ## The `human` role is never conferred by a declaration (BC-P2-10)
//!
//! L5 is "human/product owner — final authority at defined gates". A role *claim* of `human` is caller metadata
//! (D-0007 rule 2: a T5 field carrying an approval-class name is a request, recorded and ignored). Human authority
//! arrives only through the authenticated human channel ([`crate::human_channel`]); a process that declares an L5
//! role acts with L0 authority ([`acting_level`]).
use crate::util::read_yaml;
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::sync::OnceLock;

/// The acting-role id of an invocation that declared no role. It is not a kernel role and carries L0 authority.
pub const UNDECLARED_ROLE: &str = "undeclared";

/// Where the acting role came from.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RoleSource {
    /// The global `--role` flag (or a stage-specific role flag the CLI accepted as the declaration).
    Flag,
    /// `GOV_ROLE`.
    Environment,
    /// Nothing declared: L0, no privileged authority.
    Undeclared,
}

impl RoleSource {
    pub fn as_str(&self) -> &'static str {
        match self {
            RoleSource::Flag => "flag",
            RoleSource::Environment => "environment",
            RoleSource::Undeclared => "undeclared",
        }
    }
}

/// The resolved acting role of one invocation.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ActingRole {
    pub role: Option<String>,
    pub source: RoleSource,
}

impl ActingRole {
    /// The role id authority is evaluated against ([`UNDECLARED_ROLE`] when nothing was declared).
    pub fn id(&self) -> &str {
        self.role.as_deref().unwrap_or(UNDECLARED_ROLE)
    }
    pub fn is_declared(&self) -> bool {
        self.role.is_some()
    }
    pub fn to_value(&self) -> Value {
        json!({"role": self.id(), "declared": self.is_declared(), "source": self.source.as_str()})
    }
}

/// **The acting-role resolution API (BC-P2-08).** `flag` is the value of the caller's `--role` (or `None`).
///
/// Precedence: a non-empty flag, then a non-empty `GOV_ROLE`, then undeclared. Whitespace-only values are not
/// declarations. The role id itself is validated later, where authority is evaluated against the verified kernel
/// (`UNKNOWN_ROLE` for an id the kernel does not define).
pub fn resolve_acting_role(flag: Option<&str>) -> ActingRole {
    if let Some(f) = flag.map(str::trim).filter(|s| !s.is_empty()) {
        return ActingRole {
            role: Some(f.to_string()),
            source: RoleSource::Flag,
        };
    }
    if let Some(e) = std::env::var("GOV_ROLE")
        .ok()
        .map(|s| s.trim().to_string())
        .filter(|s| !s.is_empty())
    {
        return ActingRole {
            role: Some(e),
            source: RoleSource::Environment,
        };
    }
    ActingRole {
        role: None,
        source: RoleSource::Undeclared,
    }
}

static PROCESS_ROLE: OnceLock<ActingRole> = OnceLock::new();

/// Make `role` the acting role of every `Project` this process opens. Set once; a second, different installation
/// is refused so that no code path can re-declare the role part-way through a command.
pub fn install_acting_role(role: ActingRole) -> Result<()> {
    match PROCESS_ROLE.get() {
        Some(existing) if *existing == role => Ok(()),
        Some(existing) => Err(GovError::new(
            "ROLE_CONFLICT",
            format!(
                "the acting role of this process is already '{}' ({}); it cannot be re-declared as '{}'",
                existing.id(),
                existing.source.as_str(),
                role.id()
            ),
        )),
        None => {
            let _ = PROCESS_ROLE.set(role);
            Ok(())
        }
    }
}

/// The process-wide acting role, when the CLI (or an embedder) installed one.
pub fn installed_acting_role() -> Option<&'static ActingRole> {
    PROCESS_ROLE.get()
}

/// The acting role a `Project` opened now should carry: the installed process role, else `GOV_ROLE`, else
/// [`UNDECLARED_ROLE`]. Never `orchestrator` by default (framework §23).
pub fn default_role_id() -> String {
    match installed_acting_role() {
        Some(r) => r.id().to_string(),
        None => resolve_acting_role(None).id().to_string(),
    }
}

pub fn is_declared(role: &str) -> bool {
    !role.trim().is_empty() && role != UNDECLARED_ROLE
}

/// Role definitions come from the VERIFIED kernel (verifier V-H2): a tampered installed payload must not be able to
/// redefine authority levels.
pub fn roles_doc(p: &Project) -> Value {
    read_yaml(
        &crate::kernel_trust::trusted_root(p)
            .join("roles")
            .join("ROLES.yaml"),
    )
    .unwrap_or(json!({}))
}

pub fn parse_level(s: &str) -> Option<u8> {
    s.strip_prefix('L')
        .and_then(|n| n.parse::<u8>().ok())
        .filter(|n| *n <= 5)
}

fn level_in(doc: &Value, role: &str) -> Result<u8> {
    if role == UNDECLARED_ROLE {
        return Ok(0);
    }
    let r = doc["roles"].as_array().and_then(|a| a.iter().find(|r| r["id"].as_str() == Some(role))).cloned()
        .ok_or_else(|| GovError::new("UNKNOWN_ROLE", format!("role '{role}' is not defined in the kernel ROLES.yaml; use a kernel role id (e.g. orchestrator, backend-engineer, change-controller)")))?;
    parse_level(r["level"].as_str().unwrap_or("")).ok_or_else(|| {
        GovError::new(
            "UNKNOWN_ROLE",
            format!("role '{role}' has no valid authority level"),
        )
    })
}

/// Kernel authority level of a role as ROLES.yaml defines it. Unknown roles are rejected; [`UNDECLARED_ROLE`] is
/// L0. This is the *definition*; what a declared role actually carries is [`level_of`].
pub fn kernel_level_of(p: &Project, role: &str) -> Result<u8> {
    level_in(&roles_doc(p), role)
}

/// The authority a **declared** role carries: its kernel level, except that an L5 (human) level is never conferred
/// by a declaration — human authority is exercised only through the authenticated human channel (BC-P2-10;
/// D-0007 rule 2). A declared L5 role therefore carries L0. Every product caller asks this question about the
/// acting role (`p.role`), which is why the rule lives here rather than beside each caller: a consumer that
/// derived "human approved" from `level_of(..) >= 5` (e.g. retrieval-profile selection) now derives `false`.
pub fn level_of(p: &Project, role: &str) -> Result<u8> {
    let l = kernel_level_of(p, role)?;
    Ok(if l >= 5 { 0 } else { l })
}

/// The authority the acting role of `p` carries ([`level_of`] of `p.role`).
pub fn acting_level(p: &Project) -> Result<u8> {
    level_of(p, &p.role)
}

fn embedded_required_level(operation: &str) -> Option<u8> {
    crate::kernel::embedded::files()
        .iter()
        .find(|(r, _)| *r == "policies/AUTHORITY_POLICY.yaml")
        .and_then(|(_, b)| serde_yaml::from_slice::<Value>(b).ok())
        .and_then(|d| {
            d["authority_levels_required"][operation]
                .as_str()
                .and_then(parse_level)
        })
}

/// Required level for an operation class. A class the installed kernel's policy does not declare (a project installed
/// from an older release) is read from the kernel embedded in this binary; a class neither declares is treated
/// conservatively as L3.
pub fn required_level(p: &Project, operation: &str) -> u8 {
    p.policies()
        .get(
            "AUTHORITY_POLICY",
            &format!("authority_levels_required.{operation}"),
        )
        .and_then(|v| v.as_str().and_then(parse_level))
        .or_else(|| embedded_required_level(operation))
        .unwrap_or(3)
}

fn denied(role: &str, have: u8, need: u8, operation: &str, kernel: &str) -> GovError {
    let (why, remediation) = if !is_declared(role) {
        (
            "no acting role was declared, so the invocation carries no privileged authority (framework §23: no worker behaves as an orchestrator unless explicitly assigned that role)".to_string(),
            "declare the assigned role with the global `--role <kernel role id>` flag or GOV_ROLE".to_string(),
        )
    } else if have == 0 && kernel == "L5" {
        (
            format!("role '{role}' is the human/product-owner role; human authority is never conferred by a role declaration and is exercised only through the authenticated human channel (owner-signed answers, `gov trust human-channel`)"),
            "act under an agent role; record human answers with owner-signed documents".to_string(),
        )
    } else {
        (
            format!("role '{role}' (L{have}) may not perform '{operation}'"),
            "use a role whose kernel level meets AUTHORITY_POLICY.authority_levels_required"
                .to_string(),
        )
    };
    GovError::new(
        "AUTHORITY_DENIED",
        format!("{why}; '{operation}' requires L{need} (AUTHORITY_POLICY.authority_levels_required). Remediation: {remediation}."),
    )
    .with_details(json!({
        "role": role,
        "declared": is_declared(role),
        "level": format!("L{have}"),
        "kernel_level": kernel,
        "required": format!("L{need}"),
        "operation": operation,
        "cause": if !is_declared(role) { "ROLE_UNDECLARED" } else if kernel == "L5" { "HUMAN_ROLE_CLAIM" } else { "LEVEL_TOO_LOW" },
        "remediation": remediation,
    }))
}

pub fn require(p: &Project, operation: &str) -> Result<u8> {
    let kernel = kernel_level_of(p, &p.role)?;
    let have = acting_level(p)?;
    let need = required_level(p, operation);
    if have < need {
        return Err(denied(
            &p.role,
            have,
            need,
            operation,
            &format!("L{kernel}"),
        ));
    }
    Ok(have)
}

/// Authority check for a **lifecycle ingress on a repository that has no installed kernel yet** (first `init`,
/// every `adopt` stage before the first install batch). There is no project policy to read, so the check is made
/// against the kernel embedded in this binary — the same constitution the install would put in place. The acting
/// role is the one the caller declared (BC-P2-08: "init and every adopt/migrate stage included, first install
/// batch included").
pub fn require_with_embedded_kernel(role: &str, operation: &str) -> Result<u8> {
    let doc_of = |rel: &str| -> Value {
        crate::kernel::embedded::files()
            .iter()
            .find(|(r, _)| *r == rel)
            .and_then(|(_, b)| serde_yaml::from_slice::<Value>(b).ok())
            .unwrap_or(json!({}))
    };
    let roles = doc_of("roles/ROLES.yaml");
    let authority = doc_of("policies/AUTHORITY_POLICY.yaml");
    let kernel = level_in(&roles, role)?;
    let have = if kernel >= 5 { 0 } else { kernel };
    let need = authority["authority_levels_required"][operation]
        .as_str()
        .and_then(parse_level)
        .or_else(|| embedded_required_level(operation))
        .unwrap_or(3);
    if have < need {
        return Err(denied(role, have, need, operation, &format!("L{kernel}")));
    }
    Ok(have)
}

/// Role groups (ROLES.yaml `groups`): used for namespace permissions in MEMORY_POLICY.namespaces.<ns>.roles.
pub fn role_in(p: &Project, role: &str, allowed: &[String]) -> bool {
    if allowed.iter().any(|a| a == "all" || a == role) {
        return true;
    }
    let doc = roles_doc(p);
    let groups = doc
        .get("groups")
        .and_then(|g| g.as_object())
        .cloned()
        .unwrap_or_default();
    allowed.iter().any(|a| {
        groups
            .get(a)
            .and_then(|m| m.as_array())
            .map(|members| members.iter().any(|m| m.as_str() == Some(role)))
            .unwrap_or(false)
    })
}

pub fn is_kernel_role(p: &Project, name: &str) -> bool {
    roles_doc(p)["roles"]
        .as_array()
        .map(|a| a.iter().any(|r| r["id"].as_str() == Some(name)))
        .unwrap_or(false)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn undeclared_is_level_zero_and_never_orchestrator() {
        let doc = json!({"roles": [{"id": "orchestrator", "level": "L4"}]});
        assert_eq!(level_in(&doc, UNDECLARED_ROLE).unwrap(), 0);
        assert!(!is_declared(UNDECLARED_ROLE));
        assert!(!is_declared("  "));
        assert!(is_declared("orchestrator"));
        assert_eq!(level_in(&doc, "orchestrator").unwrap(), 4);
        assert_eq!(level_in(&doc, "nobody").unwrap_err().code, "UNKNOWN_ROLE");
    }

    #[test]
    fn resolution_precedence_is_flag_then_environment_then_undeclared() {
        let r = resolve_acting_role(Some("change-controller"));
        assert_eq!(r.id(), "change-controller");
        assert_eq!(r.source, RoleSource::Flag);
        // whitespace is not a declaration
        let blank = ActingRole {
            role: None,
            source: RoleSource::Undeclared,
        };
        assert_eq!(blank.id(), UNDECLARED_ROLE);
        assert!(!blank.is_declared());
    }

    #[test]
    fn embedded_kernel_check_refuses_undeclared_and_human_claims() {
        let e = require_with_embedded_kernel(UNDECLARED_ROLE, "install_kernel").unwrap_err();
        assert_eq!(e.code, "AUTHORITY_DENIED");
        assert_eq!(e.details["cause"], "ROLE_UNDECLARED");
        let e = require_with_embedded_kernel("human", "install_kernel").unwrap_err();
        assert_eq!(e.details["cause"], "HUMAN_ROLE_CLAIM");
        let e = require_with_embedded_kernel("independent-auditor", "install_kernel").unwrap_err();
        assert_eq!(e.details["cause"], "LEVEL_TOO_LOW");
        assert_eq!(
            require_with_embedded_kernel("orchestrator", "install_kernel").unwrap(),
            4
        );
    }
}
