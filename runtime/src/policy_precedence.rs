//! Constitutional policy precedence (framework §21; verifier H-N1). A lower-precedence layer (PROJECT_POLICY overrides,
//! PROJECT_EXCEPTIONS) may specialise or strengthen a higher layer but never weaken hard invariants, security floors,
//! authority floors, sensitivity floors or human-gate requirements. The rules are kernel data
//! (`policies/POLICY_PRECEDENCE.yaml`); an override that violates them is refused, recorded, and leaves the effective
//! policy unchanged (fail closed). Keys without a rule are not overridable (deny by default).
use crate::util::read_yaml;
use serde_json::{json, Value};
use std::path::Path;

#[derive(Debug, Clone)]
pub struct Rule {
    pub key: String,
    pub mode: String,
    pub kind: String,
    pub order: Vec<String>,
    pub strict_value: Option<Value>,
    pub exception_relaxable: bool,
}

#[derive(Debug, Clone)]
pub struct Precedence {
    pub rules: Vec<Rule>,
    pub default_mode: String,
    pub layers: Vec<String>,
    pub source: String,
}

fn parse_rules(doc: &Value, source: &str) -> Precedence {
    let rules = doc["rules"]
        .as_array()
        .cloned()
        .unwrap_or_default()
        .into_iter()
        .filter_map(|r| {
            Some(Rule {
                key: r["key"].as_str()?.to_string(),
                mode: r["mode"].as_str().unwrap_or("immutable").to_string(),
                kind: r["kind"].as_str().unwrap_or("").to_string(),
                order: r["order"]
                    .as_array()
                    .map(|a| {
                        a.iter()
                            .filter_map(|x| x.as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_default(),
                strict_value: r.get("strict_value").cloned(),
                exception_relaxable: r["exception_relaxable"].as_bool().unwrap_or(false),
            })
        })
        .collect();
    Precedence {
        rules,
        default_mode: doc["default_mode"]
            .as_str()
            .unwrap_or("immutable")
            .to_string(),
        layers: doc["layers"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default(),
        source: source.to_string(),
    }
}

/// Load the precedence rules from the installed kernel; fall back to the payload embedded in this binary so a
/// project installed from an older kernel is still governed by the constitutional floor.
pub fn load(kernel_dir: &Path) -> Option<Precedence> {
    let p = kernel_dir.join("policies").join("POLICY_PRECEDENCE.yaml");
    if p.exists() {
        if let Ok(doc) = read_yaml(&p) {
            return Some(parse_rules(&doc, "installed kernel"));
        }
    }
    let bytes = crate::kernel::embedded::files()
        .iter()
        .find(|(rel, _)| *rel == "policies/POLICY_PRECEDENCE.yaml")
        .map(|(_, b)| *b)?;
    let text = String::from_utf8_lossy(bytes);
    let doc: Value = serde_yaml::from_str(&text).ok()?;
    Some(parse_rules(
        &doc,
        "embedded kernel (installed kernel has no POLICY_PRECEDENCE.yaml)",
    ))
}

/// Dotted-key pattern match: `*` matches exactly one segment; a trailing `*` matches one or more segments.
pub fn key_matches(pattern: &str, key: &str) -> bool {
    let ps: Vec<&str> = pattern.split('.').collect();
    let ks: Vec<&str> = key.split('.').collect();
    if ps.last() == Some(&"*") && ps.len() <= ks.len() {
        let head = &ps[..ps.len() - 1];
        if head.iter().zip(ks.iter()).all(|(p, k)| *p == "*" || p == k) && ks.len() > head.len() {
            return true;
        }
    }
    ps.len() == ks.len() && ps.iter().zip(ks.iter()).all(|(p, k)| *p == "*" || p == k)
}

impl Precedence {
    pub fn rule_for(&self, full_key: &str) -> Option<&Rule> {
        self.rules.iter().find(|r| key_matches(&r.key, full_key))
    }
}

fn rank(kind: &str, order: &[String], v: &Value) -> Option<f64> {
    match kind {
        "level" | "radius" | "tier" => v
            .as_str()
            .and_then(|s| s.get(1..))
            .and_then(|n| n.parse::<f64>().ok()),
        "number" => v.as_f64(),
        "bool" => v.as_bool().map(|b| if b { 1.0 } else { 0.0 }),
        "ordered" => v
            .as_str()
            .and_then(|s| order.iter().position(|o| o == s))
            .map(|i| i as f64),
        _ => v.as_f64().or_else(|| {
            v.as_str()
                .and_then(|s| s.get(1..))
                .and_then(|n| n.parse::<f64>().ok())
        }),
    }
}

fn flatten(prefix: &str, v: &Value, out: &mut Vec<(String, Value)>) {
    match v.as_object() {
        Some(m) if !m.is_empty() => {
            for (k, x) in m {
                flatten(&format!("{prefix}.{k}"), x, out);
            }
        }
        _ => out.push((prefix.to_string(), v.clone())),
    }
}

fn set_of(v: &Value) -> Option<Vec<String>> {
    v.as_array().map(|a| {
        a.iter()
            .map(|x| match x {
                Value::String(s) => s.clone(),
                o => o.to_string(),
            })
            .collect()
    })
}

/// Decide whether `new_value` may replace `kernel_value` at `policy.key`. Returns the applied mode on success or
/// the reason on refusal.
pub fn evaluate(
    prec: &Precedence,
    policy: &str,
    key: &str,
    kernel_value: Option<&Value>,
    new_value: &Value,
    via_exception: bool,
) -> std::result::Result<String, String> {
    let full = format!("{policy}.{key}");
    if new_value
        .as_object()
        .map(|m| !m.is_empty())
        .unwrap_or(false)
    {
        let mut leaves = vec![];
        flatten(&full, new_value, &mut leaves);
        let mut modes = vec![];
        for (leaf, v) in leaves {
            let sub = leaf.trim_start_matches(&format!("{policy}.")).to_string();
            let kv = kernel_value.and_then(|k| {
                crate::util::deep_get(k, sub.trim_start_matches(key).trim_start_matches('.'))
            });
            modes.push(evaluate(prec, policy, &sub, kv, &v, via_exception)?);
        }
        return Ok(format!("composite[{}]", modes.join(",")));
    }
    let rule = prec.rule_for(&full);
    let (mode, kind, order, strict, relaxable) = match rule {
        Some(r) => (
            r.mode.as_str(),
            r.kind.as_str(),
            r.order.clone(),
            r.strict_value.clone(),
            r.exception_relaxable,
        ),
        None => (prec.default_mode.as_str(), "", vec![], None, false),
    };
    if via_exception && relaxable {
        return Ok("exception_relaxed".into());
    }
    let refuse = |why: String| {
        Err(format!(
            "{full}: {why} (POLICY_PRECEDENCE mode '{mode}', rule {})",
            rule.map(|r| r.key.clone())
                .unwrap_or_else(|| "<default>".into())
        ))
    };
    match mode {
        "overridable" => Ok(mode.into()),
        "immutable" => refuse(if rule.is_none() {
            "key is not declared overridable by the kernel precedence rules (deny by default)"
                .into()
        } else {
            "constitutional/security key cannot be overridden by a lower-precedence layer".into()
        }),
        "floor" | "ceiling" => {
            let Some(k) = kernel_value else {
                return Ok(mode.into());
            };
            let (Some(kr), Some(nr)) = (rank(kind, &order, k), rank(kind, &order, new_value))
            else {
                return refuse(format!(
                    "value {new_value} is not comparable with the kernel value {k}"
                ));
            };
            let ok = if mode == "floor" { nr >= kr } else { nr <= kr };
            if ok {
                Ok(mode.into())
            } else {
                refuse(format!(
                    "{new_value} would weaken the kernel {} {k}",
                    if mode == "floor" {
                        "minimum"
                    } else {
                        "maximum"
                    }
                ))
            }
        }
        "additive" => {
            let (Some(ks), Some(ns)) = (
                kernel_value.and_then(set_of).or(Some(vec![])),
                set_of(new_value),
            ) else {
                return refuse("additive keys must stay lists".into());
            };
            let missing: Vec<&String> = ks.iter().filter(|k| !ns.contains(k)).collect();
            if missing.is_empty() {
                Ok(mode.into())
            } else {
                refuse(format!("kernel entries {missing:?} may not be removed (additive key: a lower layer may only add)"))
            }
        }
        "shrink_only" => {
            let (Some(ks), Some(ns)) = (kernel_value.and_then(set_of), set_of(new_value)) else {
                return refuse("shrink_only keys must stay lists".into());
            };
            let extra: Vec<&String> = ns.iter().filter(|n| !ks.contains(n)).collect();
            if extra.is_empty() {
                Ok(mode.into())
            } else {
                refuse(format!("entries {extra:?} are not in the kernel list (shrink_only key: a lower layer may only remove)"))
            }
        }
        "strengthen_only_bool" => {
            let strict = strict.unwrap_or(json!(true));
            if new_value == &strict || kernel_value == Some(new_value) {
                Ok(mode.into())
            } else {
                refuse(format!("only the strict value {strict} is allowed"))
            }
        }
        other => refuse(format!("unknown precedence mode '{other}'")),
    }
}

/// Deterministic summary for doctor/audit/context packets.
pub fn describe(prec: &Precedence) -> Value {
    json!({"source": prec.source, "rules": prec.rules.len(), "default_mode": prec.default_mode, "layers": prec.layers})
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn pattern_matching() {
        assert!(key_matches(
            "AUTHORITY_POLICY.authority_levels_required.*",
            "AUTHORITY_POLICY.authority_levels_required.create_task"
        ));
        assert!(key_matches(
            "AUTHORITY_POLICY.*",
            "AUTHORITY_POLICY.authority_levels_required.create_task"
        ));
        assert!(key_matches(
            "MEMORY_POLICY.namespaces.*.export",
            "MEMORY_POLICY.namespaces.product.export"
        ));
        assert!(!key_matches(
            "MEMORY_POLICY.namespaces.*.export",
            "MEMORY_POLICY.namespaces.export"
        ));
        assert!(!key_matches(
            "SECURITY_POLICY.never_index_classes",
            "SECURITY_POLICY.never_export_classes"
        ));
    }
    #[test]
    fn floors_and_additive_sets() {
        let prec = Precedence {
            rules: vec![
                Rule {
                    key: "A.levels.*".into(),
                    mode: "floor".into(),
                    kind: "level".into(),
                    order: vec![],
                    strict_value: None,
                    exception_relaxable: false,
                },
                Rule {
                    key: "S.never_index".into(),
                    mode: "additive".into(),
                    kind: String::new(),
                    order: vec![],
                    strict_value: None,
                    exception_relaxable: false,
                },
                Rule {
                    key: "M.k".into(),
                    mode: "overridable".into(),
                    kind: String::new(),
                    order: vec![],
                    strict_value: None,
                    exception_relaxable: false,
                },
            ],
            default_mode: "immutable".into(),
            layers: vec![],
            source: "test".into(),
        };
        assert!(evaluate(
            &prec,
            "A",
            "levels.create",
            Some(&json!("L2")),
            &json!("L0"),
            false
        )
        .is_err());
        assert!(evaluate(
            &prec,
            "A",
            "levels.create",
            Some(&json!("L2")),
            &json!("L4"),
            false
        )
        .is_ok());
        assert!(evaluate(
            &prec,
            "S",
            "never_index",
            Some(&json!(["secret", "restricted"])),
            &json!([]),
            false
        )
        .is_err());
        assert!(evaluate(
            &prec,
            "S",
            "never_index",
            Some(&json!(["secret", "restricted"])),
            &json!(["secret", "restricted", "confidential"]),
            false
        )
        .is_ok());
        assert!(evaluate(&prec, "M", "k", Some(&json!(1)), &json!(99), false).is_ok());
        assert!(
            evaluate(&prec, "X", "y", None, &json!(1), false).is_err(),
            "deny by default"
        );
    }
}
