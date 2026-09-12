//! Canonical policy layer: kernel policies + overlay overrides + unexpired accepted exceptions.
use crate::schemas::SchemaRegistry;
use crate::util::{deep_get, deep_set, read_yaml, today};
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::Path;

pub const POLICY_NAMES: &[&str] = &[
    "AUTHORITY_POLICY",
    "MEMORY_POLICY",
    "CHANGE_POLICY",
    "SECURITY_POLICY",
    "TOOL_POLICY",
    "MODEL_ROUTING_POLICY",
    "CONTEXT_POLICY",
    "HUMAN_GATE_POLICY",
    "BUDGET_POLICY",
    "CHECKPOINT_POLICY",
    "TEST_POLICY",
    "LEARNING_POLICY",
    "ARCHIVE_POLICY",
];
/// Kernel policies that older kernels may lack; loaded when present (the precedence rules also have an embedded fallback).
pub const OPTIONAL_POLICY_NAMES: &[&str] = &["POLICY_PRECEDENCE"];
pub const OVERLAY_FILES: &[(&str, &str)] = &[
    ("PROJECT_POLICY.yaml", "project-policy"),
    ("REPOSITORY_CONTRACT.yaml", "repository-contract"),
    ("CAPABILITY_PROFILE.yaml", "capability-profile"),
    ("TOOL_PERMISSIONS.yaml", "tool-permissions"),
    ("MODEL_ROUTING_OVERRIDES.yaml", "model-routing-overrides"),
    ("DATA_SENSITIVITY.yaml", "data-sensitivity"),
    ("PROJECT_EXCEPTIONS.yaml", "project-exceptions"),
];

#[derive(Debug, Clone, Default)]
pub struct Overlay {
    pub files: BTreeMap<String, Value>,
    pub problems: Vec<String>,
}

impl Overlay {
    pub fn get(&self, file: &str) -> Value {
        self.files.get(file).cloned().unwrap_or(json!({}))
    }
    pub fn hash(&self) -> String {
        crate::util::hash_value(&serde_json::to_value(&self.files).unwrap_or(Value::Null))
    }
}

pub fn load_overlay(overlay_dir: &Path, schemas: Option<&SchemaRegistry>) -> Overlay {
    let mut ov = Overlay::default();
    for (fname, schema) in OVERLAY_FILES {
        let p = overlay_dir.join(fname);
        if !p.exists() {
            ov.problems.push(format!("overlay file missing: {fname}"));
            continue;
        }
        match read_yaml(&p) {
            Ok(d) => {
                if let Some(s) = schemas {
                    if s.has(schema) {
                        match s.errors(schema, &d) {
                            Ok(errs) if !errs.is_empty() => ov.problems.push(format!(
                                "{fname}: {}",
                                errs.iter().take(3).cloned().collect::<Vec<_>>().join("; ")
                            )),
                            Err(e) => ov.problems.push(format!("{fname}: {e}")),
                            _ => {}
                        }
                    }
                }
                ov.files.insert(fname.to_string(), d);
            }
            Err(e) => ov.problems.push(format!("{fname}: unreadable ({e})")),
        }
    }
    ov
}

#[derive(Debug, Clone, Default)]
pub struct PolicySet {
    pub raw: BTreeMap<String, Value>,
    pub effective: BTreeMap<String, Value>,
    pub applied_overrides: Vec<Value>,
    /// Overrides/exceptions refused by the constitutional precedence rules (verifier H-N1): recorded, never applied.
    pub refused_overrides: Vec<Value>,
    pub precedence: Option<Value>,
    pub problems: Vec<String>,
}

impl PolicySet {
    pub fn load(kernel_dir: &Path, overlay: &Overlay, schemas: &SchemaRegistry) -> Self {
        let mut ps = PolicySet::default();
        let names: Vec<&str> = POLICY_NAMES
            .iter()
            .copied()
            .chain(OPTIONAL_POLICY_NAMES.iter().copied())
            .collect();
        for name in names {
            let p = kernel_dir.join("policies").join(format!("{name}.yaml"));
            if !p.exists() {
                if !OPTIONAL_POLICY_NAMES.contains(&name) {
                    ps.problems.push(format!("kernel policy missing: {name}"));
                }
                continue;
            }
            match read_yaml(&p) {
                Ok(d) => {
                    let sname = format!("policy-{name}");
                    if schemas.has(&sname) {
                        if let Ok(errs) = schemas.errors(&sname, &d) {
                            if !errs.is_empty() {
                                ps.problems.push(format!(
                                    "{name}: {}",
                                    errs.iter().take(3).cloned().collect::<Vec<_>>().join("; ")
                                ));
                            }
                        }
                    }
                    ps.raw.insert(name.to_string(), d.clone());
                    ps.effective.insert(name.to_string(), d);
                }
                Err(e) => ps.problems.push(format!("{name}: unreadable ({e})")),
            }
        }
        // ---- constitutional precedence (framework §21, verifier H-N1): evaluate every override/exception against the
        // kernel rules before it touches the effective policy; refusals are recorded and leave the policy unchanged.
        let prec = crate::policy_precedence::load(kernel_dir);
        ps.precedence = prec.as_ref().map(crate::policy_precedence::describe);
        if prec.is_none() {
            ps.problems.push("POLICY_PRECEDENCE rules unavailable (installed kernel and embedded payload): every override is refused (fail closed)".into());
        }
        let pp = overlay.get("PROJECT_POLICY.yaml");
        if let Some(over) = pp.get("policy_overrides").and_then(|v| v.as_object()) {
            for (key, value) in over {
                let (pol, dotted) = key.split_once('.').unwrap_or((key.as_str(), ""));
                if dotted.is_empty() || !ps.effective.contains_key(pol) {
                    ps.problems
                        .push(format!("policy override targets unknown policy/key: {key}"));
                    continue;
                }
                let kernel_value = ps.raw.get(pol).and_then(|k| deep_get(k, dotted).cloned());
                let verdict = match &prec {
                    Some(pr) => crate::policy_precedence::evaluate(
                        pr,
                        pol,
                        dotted,
                        kernel_value.as_ref(),
                        value,
                        false,
                    ),
                    None => Err(format!("{key}: precedence rules unavailable")),
                };
                match verdict {
                    Ok(mode) => {
                        deep_set(ps.effective.get_mut(pol).unwrap(), dotted, value.clone());
                        ps.applied_overrides.push(json!({"policy": pol, "key": dotted, "value": value, "source": "PROJECT_POLICY.policy_overrides", "mode": mode}));
                    }
                    Err(reason) => ps.refused_overrides.push(json!({"policy": pol, "key": dotted, "value": value, "source": "PROJECT_POLICY.policy_overrides", "kernel_value": kernel_value, "reason": reason})),
                }
            }
        }
        let exc = overlay.get("PROJECT_EXCEPTIONS.yaml");
        for e in exc
            .get("exceptions")
            .and_then(|v| v.as_array())
            .cloned()
            .unwrap_or_default()
        {
            let expires = e
                .get("expires")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let id = e
                .get("id")
                .and_then(|v| v.as_str())
                .unwrap_or("?")
                .to_string();
            if expires.as_str() < today().as_str() {
                ps.problems
                    .push(format!("expired exception {id} still listed"));
                continue;
            }
            let pol = e
                .get("policy")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let key = e
                .get("key")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let value = e.get("value").cloned().unwrap_or(Value::Null);
            if !ps.effective.contains_key(&pol) {
                ps.problems
                    .push(format!("exception {id} targets unknown policy {pol}"));
                continue;
            }
            if e.get("decision")
                .and_then(|v| v.as_str())
                .map(|d| d.is_empty())
                .unwrap_or(true)
            {
                ps.refused_overrides.push(json!({"policy": pol, "key": key, "value": value, "source": id, "reason": format!("exception {id} has no decision record (an exception is a governed decision with an expiry)")}));
                continue;
            }
            let kernel_value = ps.raw.get(&pol).and_then(|k| deep_get(k, &key).cloned());
            let verdict = match &prec {
                Some(pr) => crate::policy_precedence::evaluate(
                    pr,
                    &pol,
                    &key,
                    kernel_value.as_ref(),
                    &value,
                    true,
                ),
                None => Err(format!("{id}: precedence rules unavailable")),
            };
            match verdict {
                Ok(mode) => {
                    if let Some(target) = ps.effective.get_mut(&pol) { deep_set(target, &key, value.clone()); }
                    ps.applied_overrides.push(json!({"policy": pol, "key": key, "value": value, "source": id, "decision": e.get("decision"), "mode": mode}));
                }
                Err(reason) => ps.refused_overrides.push(json!({"policy": pol, "key": key, "value": value, "source": id, "decision": e.get("decision"), "kernel_value": kernel_value, "reason": reason})),
            }
        }
        ps
    }
    pub fn policy(&self, name: &str) -> Result<&Value> {
        self.effective
            .get(name)
            .ok_or_else(|| GovError::new("POLICY_MISSING", format!("policy not loaded: {name}")))
    }
    pub fn get(&self, name: &str, dotted: &str) -> Option<Value> {
        self.effective
            .get(name)
            .and_then(|p| deep_get(p, dotted).cloned())
    }
    pub fn get_str(&self, name: &str, dotted: &str, default: &str) -> String {
        self.get(name, dotted)
            .and_then(|v| v.as_str().map(|s| s.to_string()))
            .unwrap_or(default.to_string())
    }
    pub fn get_i64(&self, name: &str, dotted: &str, default: i64) -> i64 {
        self.get(name, dotted)
            .and_then(|v| v.as_i64())
            .unwrap_or(default)
    }
    pub fn get_f64(&self, name: &str, dotted: &str, default: f64) -> f64 {
        self.get(name, dotted)
            .and_then(|v| v.as_f64())
            .unwrap_or(default)
    }
    pub fn get_bool(&self, name: &str, dotted: &str, default: bool) -> bool {
        self.get(name, dotted)
            .and_then(|v| v.as_bool())
            .unwrap_or(default)
    }
    pub fn get_list(&self, name: &str, dotted: &str) -> Vec<String> {
        self.get(name, dotted)
            .and_then(|v| {
                v.as_array().map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(|s| s.to_string()))
                        .collect()
                })
            })
            .unwrap_or_default()
    }
}
