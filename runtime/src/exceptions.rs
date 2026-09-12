//! Governed policy exceptions (verifier V-M1).
//!
//! `PROJECT_EXCEPTIONS.yaml` is project-controlled configuration: the `decision` field is a *claim*, not a fact. An
//! exception is applied only when that claim resolves to an authoritative governed decision record which exists, is a
//! decision, is current (ACTIVE, not superseded, not revoked, not expired), was approved at or above the authority
//! required to grant an exception, and whose own scope explicitly covers this exception or this policy key — for this
//! project. Anything else is refused, recorded in `refused_overrides` and reported by doctor D027.
use crate::util::{glob_match, today};
use serde_json::Value;
use std::path::Path;

pub struct Verdict {
    pub ok: bool,
    pub reason: String,
    pub decision_path: Option<String>,
}

impl Verdict {
    fn deny(reason: impl Into<String>) -> Self {
        Verdict {
            ok: false,
            reason: reason.into(),
            decision_path: None,
        }
    }
}

fn parse_front_matter(text: &str) -> Option<Value> {
    let rest = text.strip_prefix("---\n")?;
    let end = rest.find("\n---")?;
    serde_yaml::from_str(&rest[..end]).ok()
}

/// Resolve a record id to its governed record without loading the whole store (policy loading must not recurse).
pub fn resolve_record(root: &Path, id: &str) -> Option<(Value, String)> {
    if id.is_empty() || id.contains('/') || id.contains("..") {
        return None;
    }
    let spec = root.join("spec");
    for dir in [
        "decisions",
        "planning",
        "product",
        "architecture",
        "interfaces",
    ] {
        for ext in ["yaml", "yml", "md"] {
            let p = spec.join(dir).join(format!("{id}.{ext}"));
            if p.exists() {
                let text = std::fs::read_to_string(&p).ok()?;
                let v = if ext == "md" {
                    parse_front_matter(&text)?
                } else {
                    serde_yaml::from_str(&text).ok()?
                };
                return Some((v, format!("spec/{dir}/{id}.{ext}")));
            }
        }
    }
    // fall back to a bounded scan of spec/ for a record file whose stem is the id
    let mut stack = vec![spec];
    let mut seen = 0usize;
    while let Some(d) = stack.pop() {
        let Ok(rd) = std::fs::read_dir(&d) else {
            continue;
        };
        for e in rd.flatten() {
            let p = e.path();
            seen += 1;
            if seen > 5000 {
                return None;
            }
            if p.is_dir() {
                stack.push(p);
                continue;
            }
            let stem = p.file_stem().map(|s| s.to_string_lossy().to_string());
            if stem.as_deref() != Some(id) {
                continue;
            }
            let ext = p
                .extension()
                .map(|s| s.to_string_lossy().to_string())
                .unwrap_or_default();
            let Ok(text) = std::fs::read_to_string(&p) else {
                continue;
            };
            let v = if ext == "md" {
                parse_front_matter(&text)
            } else if ext == "yaml" || ext == "yml" {
                serde_yaml::from_str(&text).ok()
            } else {
                None
            };
            if let Some(v) = v {
                let rel = p
                    .strip_prefix(root)
                    .map(|r| r.to_string_lossy().to_string())
                    .unwrap_or_else(|_| p.to_string_lossy().to_string());
                return Some((v, rel));
            }
        }
    }
    None
}

fn str_field(v: &Value, key: &str) -> String {
    v.get(key)
        .and_then(|x| x.as_str())
        .unwrap_or("")
        .to_string()
}

fn list_field(v: &Value, key: &str) -> Vec<String> {
    v.get(key)
        .and_then(|x| x.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|s| s.as_str().map(|t| t.to_string()))
                .collect()
        })
        .unwrap_or_default()
}

/// Does the decision's own scope explicitly authorise this exception / policy key?
fn scope_covers(decision: &Value, exception_id: &str, full_key: &str, policy: &str) -> bool {
    let mut refs: Vec<String> = vec![];
    for k in [
        "authorises_exceptions",
        "authorizes_exceptions",
        "permits_policy_keys",
        "affects",
        "tags",
        "scope",
    ] {
        refs.extend(list_field(decision, k));
    }
    if let Some(s) = decision.get("scope").and_then(|v| v.as_str()) {
        refs.push(s.to_string());
    }
    refs.iter().any(|r| {
        r == exception_id
            || r == full_key
            || r == policy
            || (r.contains('*') && (glob_match(r, full_key) || glob_match(r, policy)))
    })
}

/// Validate one `PROJECT_EXCEPTIONS` entry against authoritative project state.
///
/// `role_level` resolves a kernel role id to its authority level (trusted ROLES.yaml); `required_level` is
/// `AUTHORITY_POLICY.authority_levels_required.grant_policy_exception`.
pub fn validate(
    root: &Path,
    exception: &Value,
    project_name: &str,
    required_level: u8,
    role_level: &dyn Fn(&str) -> Option<u8>,
) -> Verdict {
    let id = str_field(exception, "id");
    let id = if id.is_empty() { "?".to_string() } else { id };
    let policy = str_field(exception, "policy");
    let key = str_field(exception, "key");
    let full_key = format!("{policy}.{key}");
    let decision_id = str_field(exception, "decision");
    if decision_id.is_empty() {
        return Verdict::deny(format!(
            "exception {id} has no decision record (an exception is a governed decision with an expiry, not a self-declared waiver)"
        ));
    }
    let Some((d, path)) = resolve_record(root, &decision_id) else {
        return Verdict::deny(format!(
            "exception {id} references decision {decision_id}, which does not exist in this repository (unresolved governance reference: fail closed)"
        ));
    };
    let rtype = str_field(&d, "type");
    if rtype != "decision" {
        return Verdict::deny(format!(
            "exception {id} references {decision_id} ({path}), which is a '{rtype}' record, not a decision"
        ));
    }
    let status = str_field(&d, "status");
    if status != "ACTIVE" {
        return Verdict::deny(format!(
            "exception {id} references decision {decision_id} whose status is {status} (only an ACTIVE decision authorises an exception)"
        ));
    }
    if !str_field(&d, "superseded_by").is_empty() {
        return Verdict::deny(format!(
            "exception {id} references decision {decision_id}, superseded by {}",
            str_field(&d, "superseded_by")
        ));
    }
    if d.get("revoked").and_then(|v| v.as_bool()).unwrap_or(false)
        || !str_field(&d, "revoked_gate").is_empty()
        || !str_field(&d, "rollback_of").is_empty()
    {
        return Verdict::deny(format!(
            "exception {id} references decision {decision_id}, which has been revoked or rolled back"
        ));
    }
    let d_expires = str_field(&d, "expires");
    if !d_expires.is_empty() && d_expires.as_str() < today().as_str() {
        return Verdict::deny(format!(
            "exception {id} references decision {decision_id}, which expired on {d_expires}"
        ));
    }
    // authority: the decision must have been approved at or above the level required to grant an exception
    let human = d
        .get("human_approved")
        .and_then(|v| v.as_bool())
        .unwrap_or(false);
    let approver_level = ["approved_by_role", "owner_role", "role"]
        .iter()
        .filter_map(|k| {
            let r = str_field(&d, k);
            if r.is_empty() {
                None
            } else {
                role_level(&r)
            }
        })
        .max();
    let authorised = human || approver_level.map(|l| l >= required_level).unwrap_or(false);
    if !authorised {
        return Verdict::deny(format!(
            "exception {id}: decision {decision_id} was not approved at the authority required to grant a policy exception (needs human approval or an approver at L{required_level}; found {})",
            approver_level.map(|l| format!("L{l}")).unwrap_or_else(|| "no resolvable approver role".into())
        ));
    }
    // scope: the decision must explicitly cover this exception or this policy key
    if !scope_covers(&d, &id, &full_key, &policy) {
        return Verdict::deny(format!(
            "exception {id}: decision {decision_id} does not name it or {full_key} in authorises_exceptions / permits_policy_keys / affects (a decision about something else cannot authorise this exception)"
        ));
    }
    // project scope
    let d_project = ["applies_to_project", "project"]
        .iter()
        .map(|k| str_field(&d, k))
        .find(|s| !s.is_empty())
        .unwrap_or_default();
    if !d_project.is_empty() && !project_name.is_empty() && d_project != project_name {
        return Verdict::deny(format!(
            "exception {id}: decision {decision_id} applies to project '{d_project}', not '{project_name}'"
        ));
    }
    Verdict {
        ok: true,
        reason: format!("authorised by {decision_id} ({path})"),
        decision_path: Some(path),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn setup(decision: Option<Value>) -> std::path::PathBuf {
        let root = std::env::temp_dir().join(format!("gov-exc-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(root.join("spec/decisions")).unwrap();
        if let Some(d) = decision {
            crate::util::write_yaml(&root.join("spec/decisions/D-0001.yaml"), &d).unwrap();
        }
        root
    }
    fn exc() -> Value {
        json!({"id": "EXC-1", "policy": "BUDGET_POLICY", "key": "defaults.max_tool_calls", "value": 9, "decision": "D-0001", "expires": "2099-01-01"})
    }
    fn lvl(_r: &str) -> Option<u8> {
        Some(4)
    }

    #[test]
    fn a_fabricated_decision_reference_is_refused() {
        let root = setup(None);
        let v = validate(&root, &exc(), "p", 4, &lvl);
        assert!(!v.ok && v.reason.contains("does not exist"), "{}", v.reason);
        let _ = std::fs::remove_dir_all(&root);
    }

    #[test]
    fn lifecycle_scope_and_authority_are_all_required() {
        let base = json!({"id": "D-0001", "type": "decision", "title": "t", "status": "ACTIVE",
            "question": "?", "chosen_option": "A", "rationale": "r", "human_approved": true,
            "authorises_exceptions": ["EXC-1"]});
        let root = setup(Some(base.clone()));
        assert!(validate(&root, &exc(), "p", 4, &lvl).ok);
        // superseded
        let mut d = base.clone();
        d["superseded_by"] = json!("D-0002");
        crate::util::write_yaml(&root.join("spec/decisions/D-0001.yaml"), &d).unwrap();
        assert!(!validate(&root, &exc(), "p", 4, &lvl).ok);
        // not ACTIVE
        let mut d = base.clone();
        d["status"] = json!("REJECTED");
        crate::util::write_yaml(&root.join("spec/decisions/D-0001.yaml"), &d).unwrap();
        assert!(!validate(&root, &exc(), "p", 4, &lvl).ok);
        // scope names another policy key
        let mut d = base.clone();
        d["authorises_exceptions"] = json!(["EXC-OTHER"]);
        crate::util::write_yaml(&root.join("spec/decisions/D-0001.yaml"), &d).unwrap();
        assert!(!validate(&root, &exc(), "p", 4, &lvl).ok);
        // insufficient authority
        let mut d = base.clone();
        d["human_approved"] = json!(false);
        d["approved_by_role"] = json!("research-agent");
        crate::util::write_yaml(&root.join("spec/decisions/D-0001.yaml"), &d).unwrap();
        assert!(
            !validate(&root, &exc(), "p", 4, &|r: &str| if r == "research-agent" {
                Some(1)
            } else {
                None
            })
            .ok
        );
        // wrong project
        let mut d = base.clone();
        d["applies_to_project"] = json!("other");
        crate::util::write_yaml(&root.join("spec/decisions/D-0001.yaml"), &d).unwrap();
        assert!(!validate(&root, &exc(), "p", 4, &lvl).ok);
        // a glob over the policy key is accepted
        let mut d = base.clone();
        d["authorises_exceptions"] = json!([]);
        d["permits_policy_keys"] = json!(["BUDGET_POLICY.defaults.*"]);
        crate::util::write_yaml(&root.join("spec/decisions/D-0001.yaml"), &d).unwrap();
        assert!(validate(&root, &exc(), "p", 4, &lvl).ok);
        let _ = std::fs::remove_dir_all(&root);
    }
}
