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
    /// Verified-kernel verdict for the source these policies were read from (verifier V-H2).
    pub kernel_trust: Value,
    pub problems: Vec<String>,
    /// Project overlay documents as the product must read them (BC-P2-45): every key evaluated against
    /// POLICY_PRECEDENCE, refused weakenings replaced by the kernel value and reported in `refused_overrides`.
    /// Keys: `PROJECT_POLICY.yaml`, `MODEL_ROUTING_OVERRIDES.yaml`.
    pub effective_overlays: BTreeMap<String, Value>,
}

impl PolicySet {
    /// Load the effective policy for a repository. Constitutional content is read only from a kernel that has been
    /// authenticated against the installed release identity (`kernel_trust`); when verification fails the immutable
    /// payload embedded in this binary is substituted explicitly and the substitution is recorded (verifier V-H2).
    pub fn load(root: &Path, overlay: &Overlay, schemas: &SchemaRegistry) -> Self {
        let trust = crate::kernel_trust::trust(root);
        let kernel_dir = trust.policy_root.clone();
        let kernel_dir = kernel_dir.as_path();
        let mut ps = PolicySet {
            kernel_trust: trust.to_value(),
            ..Default::default()
        };
        if trust.substituted {
            ps.problems.push(format!(
                "installed kernel failed verification: {}. Constitutional policy is read from the embedded baseline {} and mutating operations are refused (KERNEL_TAMPERED) until `gov kernel reinstall`.",
                trust.problems.join("; "),
                trust.trusted_version
            ));
        } else if trust.installed && !trust.verified {
            ps.problems.push(format!(
                "installed kernel failed verification and no trusted baseline is available: {}",
                trust.problems.join("; ")
            ));
        }
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
        ps.precedence = prec.as_ref().map(|pr| {
            let mut d = crate::policy_precedence::describe(pr);
            d["source"] = json!(trust.source.clone());
            d["kernel_verified"] = json!(trust.verified);
            d
        });
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
            // V-M1: the `decision` field is a claim. It is applied only when it resolves to an existing, current,
            // sufficiently approved decision whose own scope covers this exception for this project.
            let roles_doc = crate::util::read_yaml(&kernel_dir.join("roles").join("ROLES.yaml"))
                .unwrap_or(json!({}));
            let required_level = ps
                .effective
                .get("AUTHORITY_POLICY")
                .and_then(|a| {
                    deep_get(a, "authority_levels_required.grant_policy_exception").cloned()
                })
                .and_then(|v| v.as_str().and_then(crate::authority::parse_level))
                .unwrap_or(4);
            let project_name = pp
                .get("project")
                .and_then(|x| x.get("name"))
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let level_of = |role: &str| -> Option<u8> {
                roles_doc["roles"]
                    .as_array()
                    .and_then(|a| a.iter().find(|r| r["id"].as_str() == Some(role)))
                    .and_then(|r| r["level"].as_str().and_then(crate::authority::parse_level))
            };
            let verdict_exc =
                crate::exceptions::validate(root, &e, &project_name, required_level, &level_of);
            if !verdict_exc.ok {
                ps.refused_overrides.push(json!({"policy": pol, "key": key, "value": value, "source": id, "decision": e.get("decision"), "reason": verdict_exc.reason}));
                continue;
            }
            // BC-P2-09: the governing decision is T2 state. Its approval fields count only when a gov operation
            // (a Human Decision Gate answer) wrote the record as it stands; a hand-written or edited decision is a
            // request, recorded and ignored (D-0007 rule 2).
            if let Some(dp) = verdict_exc.decision_path.as_deref() {
                let b = crate::t2::verify_file(root, dp);
                if !b.is_verified() {
                    ps.refused_overrides.push(json!({"policy": pol, "key": key, "value": value, "source": id, "decision": e.get("decision"),
                        "reason": format!("decision {} ({dp}) is not a record a gov operation wrote as it stands (T2 binding {}); only a decision recorded by an answered Human Decision Gate can authorise a policy exception (D-0007 rule 2)", e.get("decision").and_then(|v| v.as_str()).unwrap_or("?"), b.code()),
                        "t2": b.to_value()}));
                    continue;
                }
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
                    ps.applied_overrides.push(json!({"policy": pol, "key": key, "value": value, "source": id, "decision": e.get("decision"), "mode": mode, "authorised_by": verdict_exc.reason}));
                }
                Err(reason) => ps.refused_overrides.push(json!({"policy": pol, "key": key, "value": value, "source": id, "decision": e.get("decision"), "kernel_value": kernel_value, "reason": reason})),
            }
        }
        // ---- BC-P2-45: every project overlay input is subject to POLICY_PRECEDENCE, not only policy_overrides.
        // Kernel values come from the verified kernel: the overlay templates it ships (PROJECT_POLICY), the
        // routing policy's task-class floors and the roles' tier/reasoning defaults (MODEL_ROUTING_OVERRIDES).
        let template_pp = read_yaml(
            &kernel_dir
                .join("overlay-templates")
                .join("PROJECT_POLICY.yaml"),
        )
        .unwrap_or(json!({}));
        let pp_kernel = |dotted: &str| deep_get(&template_pp, dotted).cloned();
        let v = crate::policy_precedence::evaluate_overlay(
            prec.as_ref(),
            "PROJECT_POLICY",
            "PROJECT_POLICY.yaml",
            &pp,
            &pp_kernel,
            &["policy_overrides"],
        );
        ps.applied_overrides.extend(v.applied);
        ps.refused_overrides.extend(v.refused);
        ps.effective_overlays
            .insert("PROJECT_POLICY.yaml".into(), v.effective);
        let roles = read_yaml(&kernel_dir.join("roles").join("ROLES.yaml")).unwrap_or(json!({}));
        let routing_kernel = ps
            .raw
            .get("MODEL_ROUTING_POLICY")
            .cloned()
            .unwrap_or(json!({}));
        let mro_kernel = |dotted: &str| -> Option<Value> {
            let parts: Vec<&str> = dotted.split('.').collect();
            match parts.as_slice() {
                ["task_class_overrides", class] => Some(
                    deep_get(&routing_kernel, &format!("task_class_minimum_tier.{class}"))
                        .cloned()
                        .unwrap_or(json!(crate::routing::DEFAULT_CLASS_TIER)),
                ),
                ["role_overrides", role, field] => {
                    let r = roles["roles"]
                        .as_array()
                        .and_then(|a| a.iter().find(|x| x["id"].as_str() == Some(role)))?;
                    match *field {
                        "minimum_tier" => Some(json!(r["minimum_tier"]
                            .as_str()
                            .filter(|t| t.starts_with('T'))
                            .unwrap_or("T0"))),
                        "default_reasoning" => Some(json!(r["default_reasoning"]
                            .as_str()
                            .filter(|x| ["low", "medium", "high", "extra_high"].contains(x))
                            .unwrap_or("low"))),
                        _ => None,
                    }
                }
                _ => None,
            }
        };
        let v = crate::policy_precedence::evaluate_overlay(
            prec.as_ref(),
            "MODEL_ROUTING_OVERRIDES",
            "MODEL_ROUTING_OVERRIDES.yaml",
            &overlay.get("MODEL_ROUTING_OVERRIDES.yaml"),
            &mro_kernel,
            &[],
        );
        ps.applied_overrides.extend(v.applied);
        ps.refused_overrides.extend(v.refused);
        ps.effective_overlays
            .insert("MODEL_ROUTING_OVERRIDES.yaml".into(), v.effective);
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
