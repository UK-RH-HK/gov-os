//! Mechanical L0–L5 authority enforcement (framework §23, AUTHORITY_POLICY.authority_levels_required).
//! Every privileged executable path calls `require(project, operation)` before mutating anything.
use crate::util::read_yaml;
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub fn roles_doc(p: &Project) -> Value {
    read_yaml(&p.kernel_dir().join("roles").join("ROLES.yaml")).unwrap_or(json!({}))
}

pub fn parse_level(s: &str) -> Option<u8> {
    s.strip_prefix('L')
        .and_then(|n| n.parse::<u8>().ok())
        .filter(|n| *n <= 5)
}

/// Authority level of a role (ROLES.yaml). Unknown roles are rejected.
pub fn level_of(p: &Project, role: &str) -> Result<u8> {
    let doc = roles_doc(p);
    let r = doc["roles"].as_array().and_then(|a| a.iter().find(|r| r["id"].as_str() == Some(role))).cloned()
        .ok_or_else(|| GovError::new("UNKNOWN_ROLE", format!("role '{role}' is not defined in the kernel ROLES.yaml; use a kernel role id (e.g. orchestrator, backend-engineer, human)")))?;
    parse_level(r["level"].as_str().unwrap_or("")).ok_or_else(|| {
        GovError::new(
            "UNKNOWN_ROLE",
            format!("role '{role}' has no valid authority level"),
        )
    })
}

/// Required level for an operation class; a class missing from policy is treated conservatively as L3.
pub fn required_level(p: &Project, operation: &str) -> u8 {
    p.policies()
        .get(
            "AUTHORITY_POLICY",
            &format!("authority_levels_required.{operation}"),
        )
        .and_then(|v| v.as_str().and_then(parse_level))
        .unwrap_or(3)
}

pub fn require(p: &Project, operation: &str) -> Result<u8> {
    let have = level_of(p, &p.role)?;
    let need = required_level(p, operation);
    if have < need {
        return Err(GovError::new("AUTHORITY_DENIED", format!("role '{}' (L{have}) may not perform '{operation}' (requires L{need}); AUTHORITY_POLICY.authority_levels_required", p.role))
            .with_details(json!({"role": p.role, "level": format!("L{have}"), "required": format!("L{need}"), "operation": operation})));
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
