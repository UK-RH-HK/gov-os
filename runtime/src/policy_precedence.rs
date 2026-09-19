//! Constitutional policy precedence (framework §21; verifier H-N1). A lower-precedence layer (PROJECT_POLICY overrides,
//! PROJECT_EXCEPTIONS) may specialise or strengthen a higher layer but never weaken hard invariants, security floors,
//! authority floors, sensitivity floors or human-gate requirements. The rules are kernel data
//! (`policies/POLICY_PRECEDENCE.yaml`); an override that violates them is refused, recorded, and leaves the effective
//! policy unchanged (fail closed). Keys without a rule are not overridable (deny by default).
//!
//! ## Which rules govern (round-2 integration observation O-1; Contract v3 S5 and A1)
//!
//! Two rule sets can speak about a key: the precedence rules of the **installed, verified kernel** and the
//! **constitutional floor compiled into this binary** (the embedded kernel payload). [`Governing`] evaluates a key
//! against every set that *declares* the key's policy or overlay label (has at least one rule for it), and accepts
//! the key only when **every** declaring set accepts it — so a newer binary never lowers a floor an installed kernel
//! declares, and an older installed kernel never lowers a floor this binary enforces.
//!
//! A set that declares **no rule at all** for a label predates that label's evaluation. The kernels shipped as 4.1.4
//! and 4.1.5 are the case in point: their rules cover `policy_overrides` targets only, because those kernels did
//! not evaluate the project overlay documents (`PROJECT_POLICY`, `MODEL_ROUTING_OVERRIDES`) key by key. Reading their
//! silence as "deny every key" refused purely descriptive keys (`project.name`, `providers`, …), made doctor D027
//! CRITICAL and rolled back an update to shipped 4.1.5. Such a set does not govern the label; the declaring set does
//! (this binary's floor), so descriptive keys are recognised as descriptive while every floor it declares
//! (readiness, tier, reasoning, the catch-all `immutable`) is still enforced. When no set declares a label, the
//! installed kernel's default (deny) applies.
use crate::util::read_yaml;
use serde_json::{json, Value};
use std::path::Path;

#[derive(Debug, Clone, PartialEq)]
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
    embedded_with_source("embedded kernel (installed kernel has no POLICY_PRECEDENCE.yaml)")
}

/// The constitutional precedence rules compiled into this binary (its embedded kernel payload).
pub fn embedded() -> Option<Precedence> {
    embedded_with_source("constitutional floor of this binary (embedded kernel)")
}

fn embedded_with_source(source: &str) -> Option<Precedence> {
    let bytes = crate::kernel::embedded::files()
        .iter()
        .find(|(rel, _)| *rel == "policies/POLICY_PRECEDENCE.yaml")
        .map(|(_, b)| *b)?;
    let text = String::from_utf8_lossy(bytes);
    let doc: Value = serde_yaml::from_str(&text).ok()?;
    Some(parse_rules(&doc, source))
}

/// **Every rule set that governs precedence for a repository** (see the module documentation): the installed,
/// verified kernel's rules (or the embedded fallback when it has none) and the constitutional floor compiled into
/// this binary, the latter only when it differs from the former.
#[derive(Debug, Clone)]
pub struct Governing {
    pub sets: Vec<Precedence>,
}

impl Governing {
    /// The governing rule sets for a kernel directory (`None` when no rules exist anywhere: fail closed).
    pub fn load(kernel_dir: &Path) -> Option<Governing> {
        Self::from_sets(load(kernel_dir), embedded())
    }

    /// Compose an installed rule set with this binary's floor (exposed for tests and embedders).
    pub fn from_sets(
        installed: Option<Precedence>,
        floor: Option<Precedence>,
    ) -> Option<Governing> {
        let mut sets: Vec<Precedence> = installed.into_iter().collect();
        if let Some(f) = floor {
            if !sets.iter().any(|s| s.same_rules(&f)) {
                sets.push(f);
            }
        }
        if sets.is_empty() {
            None
        } else {
            Some(Governing { sets })
        }
    }

    /// One rule set governing alone.
    pub fn single(prec: Precedence) -> Governing {
        Governing { sets: vec![prec] }
    }

    /// The sets that govern `label` (a kernel policy name or an overlay document label): those declaring at least
    /// one rule for it; when none does, the first (installed) set with its default mode.
    pub fn governing(&self, label: &str) -> Vec<&Precedence> {
        let v: Vec<&Precedence> = self.sets.iter().filter(|s| s.declares(label)).collect();
        if v.is_empty() {
            self.sets.iter().take(1).collect()
        } else {
            v
        }
    }

    /// [`evaluate`] against every governing set: accepted only when each accepts. The reported mode is the most
    /// constraining one (a non-`overridable` mode wins); a refusal names the rule set that refused.
    pub fn evaluate(
        &self,
        policy: &str,
        key: &str,
        kernel_value: Option<&Value>,
        new_value: &Value,
        via_exception: bool,
    ) -> std::result::Result<String, String> {
        let sets = self.governing(policy);
        let several = self.sets.len() > 1;
        let mut mode: Option<String> = None;
        for s in sets {
            match evaluate(s, policy, key, kernel_value, new_value, via_exception) {
                Ok(m) => {
                    if mode.as_deref().map(|x| x == "overridable").unwrap_or(true) {
                        mode = Some(m);
                    }
                }
                Err(reason) => {
                    return Err(if several {
                        format!("{reason} [rules: {}]", s.source)
                    } else {
                        reason
                    })
                }
            }
        }
        Ok(mode.unwrap_or_else(|| "overridable".into()))
    }

    /// Deterministic summary: the first set as before, plus every governing set.
    pub fn describe(&self) -> Value {
        let mut d = describe(&self.sets[0]);
        d["governing_sets"] = json!(self
            .sets
            .iter()
            .map(|s| json!({"source": s.source, "rules": s.rules.len(), "default_mode": s.default_mode}))
            .collect::<Vec<_>>());
        d
    }
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

    /// Whether this set declares any rule for `label` (its first key segment is the label, or `*`).
    pub fn declares(&self, label: &str) -> bool {
        self.rules.iter().any(|r| {
            let first = r.key.split('.').next().unwrap_or("");
            first == label || first == "*"
        })
    }

    /// Same rules and default (the source label aside).
    pub fn same_rules(&self, other: &Precedence) -> bool {
        self.rules == other.rules && self.default_mode == other.default_mode
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

/// Outcome of evaluating one project **overlay document** (not a kernel policy) against the precedence rules.
#[derive(Debug, Clone, Default)]
pub struct OverlayVerdict {
    /// The document as the product must read it: every refused leaf replaced by its kernel value (or removed when
    /// the kernel defines none).
    pub effective: Value,
    /// Leaves that differ from the kernel value and were accepted under a non-free mode (floor raised, etc.).
    pub applied: Vec<Value>,
    /// Leaves refused by the rules: recorded, reported, never applied.
    pub refused: Vec<Value>,
}

fn overlay_leaves(prefix: &str, v: &Value, out: &mut Vec<(String, Value)>) {
    match v.as_object() {
        // an empty mapping declares nothing, so there is nothing to evaluate
        Some(m) if m.is_empty() => {}
        Some(m) => {
            for (k, x) in m {
                let key = if prefix.is_empty() {
                    k.clone()
                } else {
                    format!("{prefix}.{k}")
                };
                overlay_leaves(&key, x, out);
            }
        }
        None => out.push((prefix.to_string(), v.clone())),
    }
}

/// **BC-P2-45 — every project overlay key is subject to POLICY_PRECEDENCE.** Evaluate every leaf of the overlay
/// document `doc` (file label `label`, e.g. `PROJECT_POLICY`, `MODEL_ROUTING_OVERRIDES`) against the rules keyed
/// `<label>.<dotted>`; `kernel_value_of(dotted)` supplies the kernel (or kernel-default) value the leaf may not
/// weaken. Subtrees named in `skip` are evaluated elsewhere (e.g. `policy_overrides`). A leaf equal to its kernel
/// value changes nothing and is accepted as is; every other leaf must satisfy its rule in every rule set that
/// governs `label` ([`Governing::evaluate`]; deny by default).
pub fn evaluate_overlay(
    prec: Option<&Governing>,
    label: &str,
    source: &str,
    doc: &Value,
    kernel_value_of: &dyn Fn(&str) -> Option<Value>,
    skip: &[&str],
) -> OverlayVerdict {
    let mut out = OverlayVerdict {
        effective: doc.clone(),
        ..Default::default()
    };
    let mut leaves = vec![];
    overlay_leaves("", doc, &mut leaves);
    for (dotted, value) in leaves {
        if skip
            .iter()
            .any(|s| dotted == *s || dotted.starts_with(&format!("{s}.")))
        {
            continue;
        }
        let kernel = kernel_value_of(&dotted);
        if kernel.as_ref() == Some(&value) {
            continue;
        }
        let verdict = match prec {
            Some(pr) => pr.evaluate(label, &dotted, kernel.as_ref(), &value, false),
            None => Err(format!(
                "{label}.{dotted}: precedence rules unavailable (fail closed)"
            )),
        };
        match verdict {
            Ok(mode) => {
                if mode != "overridable" {
                    out.applied.push(json!({"policy": label, "key": dotted, "value": value, "source": source, "mode": mode, "kernel_value": kernel}));
                }
            }
            Err(reason) => {
                match &kernel {
                    Some(k) => crate::util::deep_set(&mut out.effective, &dotted, k.clone()),
                    None => {
                        crate::util::deep_delete(&mut out.effective, &dotted);
                    }
                }
                out.refused.push(json!({"policy": label, "key": dotted, "value": value, "source": source, "kernel_value": kernel, "reason": reason}));
            }
        }
    }
    out
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

    #[test]
    fn overlay_documents_may_raise_floors_but_never_lower_them() {
        let rule = |key: &str, mode: &str, kind: &str, order: &[&str]| Rule {
            key: key.into(),
            mode: mode.into(),
            kind: kind.into(),
            order: order.iter().map(|s| s.to_string()).collect(),
            strict_value: if mode == "strengthen_only_bool" {
                Some(json!(true))
            } else {
                None
            },
            exception_relaxable: false,
        };
        let prec = Precedence {
            rules: vec![
                rule("MRO.task_class_overrides.*", "floor", "tier", &[]),
                rule(
                    "MRO.role_overrides.*.default_reasoning",
                    "floor",
                    "ordered",
                    &["low", "medium", "high", "extra_high"],
                ),
                rule("MRO.providers", "overridable", "", &[]),
                rule("PP.readiness.enforce", "strengthen_only_bool", "", &[]),
                rule("MRO.*", "immutable", "", &[]),
                rule("PP.*", "immutable", "", &[]),
            ],
            default_mode: "immutable".into(),
            layers: vec![],
            source: "test".into(),
        };
        let kernel = |k: &str| -> Option<Value> {
            match k {
                "task_class_overrides.security" => Some(json!("T3")),
                "task_class_overrides.docs" => Some(json!("T1")),
                "role_overrides.orchestrator.default_reasoning" => Some(json!("high")),
                "readiness.enforce" => Some(json!(true)),
                _ => None,
            }
        };
        let doc = json!({"providers": [{"name": "x"}], "task_class_overrides": {"security": "T1", "docs": "T2"},
                         "role_overrides": {"orchestrator": {"default_reasoning": "low"}}, "unknown": 1, "empty": {}});
        let gov = Governing::single(prec);
        let v = evaluate_overlay(Some(&gov), "MRO", "MRO.yaml", &doc, &kernel, &[]);
        let refused: Vec<&str> = v
            .refused
            .iter()
            .map(|r| r["key"].as_str().unwrap())
            .collect();
        assert!(
            refused.contains(&"task_class_overrides.security"),
            "{refused:?}"
        );
        assert!(refused.contains(&"role_overrides.orchestrator.default_reasoning"));
        assert!(
            refused.contains(&"unknown"),
            "deny by default for undeclared overlay keys"
        );
        assert_eq!(
            v.effective["task_class_overrides"]["security"], "T3",
            "the refused weakening is replaced by the floor"
        );
        assert_eq!(
            v.effective["task_class_overrides"]["docs"], "T2",
            "raising a floor is applied"
        );
        assert_eq!(
            v.effective["role_overrides"]["orchestrator"]["default_reasoning"],
            "high"
        );
        assert!(v.effective.get("unknown").is_none());
        assert!(v
            .applied
            .iter()
            .any(|a| a["key"] == "task_class_overrides.docs"));
        let pp = json!({"readiness": {"enforce": false}, "policy_overrides": {"X.y": 1}});
        let v = evaluate_overlay(
            Some(&gov),
            "PP",
            "PP.yaml",
            &pp,
            &kernel,
            &["policy_overrides"],
        );
        assert_eq!(v.refused.len(), 1, "{:?}", v.refused);
        assert_eq!(v.effective["readiness"]["enforce"], true);
        // no rules at all: fail closed
        let v = evaluate_overlay(None, "PP", "PP.yaml", &pp, &kernel, &["policy_overrides"]);
        assert_eq!(v.effective["readiness"]["enforce"], true);
    }

    /// O-1: a kernel whose rules predate overlay-document evaluation (no rule for the label) does not govern it;
    /// the floor that declares the label does. Where both declare a key, the stricter verdict holds either way.
    #[test]
    fn a_rule_set_silent_on_a_label_does_not_govern_it_and_the_stricter_set_wins() {
        let rule = |key: &str, mode: &str, kind: &str| Rule {
            key: key.into(),
            mode: mode.into(),
            kind: kind.into(),
            order: vec![],
            strict_value: if mode == "strengthen_only_bool" {
                Some(json!(true))
            } else {
                None
            },
            exception_relaxable: false,
        };
        let set = |source: &str, rules: Vec<Rule>| Precedence {
            rules,
            default_mode: "immutable".into(),
            layers: vec![],
            source: source.into(),
        };
        // like the shipped 4.1.4/4.1.5 rules: kernel policies only, nothing for the overlay documents
        let old = set(
            "installed kernel",
            vec![
                rule("A.levels.*", "floor", "level"),
                rule("A.*", "immutable", ""),
                rule("M.*", "overridable", ""),
            ],
        );
        let floor = set(
            "floor",
            vec![
                rule("A.levels.*", "floor", "level"),
                rule("A.*", "immutable", ""),
                rule("M.guard", "strengthen_only_bool", ""),
                rule("M.*", "overridable", ""),
                rule("PP.readiness.*", "strengthen_only_bool", ""),
                rule("PP.project.*", "overridable", ""),
                rule("PP.*", "immutable", ""),
            ],
        );
        let gov = Governing::from_sets(Some(old.clone()), Some(floor.clone())).unwrap();
        assert_eq!(gov.sets.len(), 2);
        let kernel = |k: &str| -> Option<Value> {
            match k {
                "readiness.enforce" => Some(json!(true)),
                "project.name" => Some(json!("{{project_name}}")),
                _ => None,
            }
        };
        let doc = json!({"project": {"name": "shop"}, "readiness": {"enforce": false}, "governance": {"x": 1}});
        let v = evaluate_overlay(Some(&gov), "PP", "PP.yaml", &doc, &kernel, &[]);
        let refused: Vec<&str> = v
            .refused
            .iter()
            .map(|r| r["key"].as_str().unwrap())
            .collect();
        assert!(
            !refused.contains(&"project.name"),
            "descriptive key recognised: {refused:?}"
        );
        assert!(
            refused.contains(&"readiness.enforce"),
            "floor still enforced: {refused:?}"
        );
        assert!(
            refused.contains(&"governance.x"),
            "catch-all still immutable: {refused:?}"
        );
        assert_eq!(v.effective["project"]["name"], "shop");
        assert_eq!(v.effective["readiness"]["enforce"], true);
        // the installed set alone (as before): deny by default for every overlay key
        let alone = Governing::single(old.clone());
        let v = evaluate_overlay(Some(&alone), "PP", "PP.yaml", &doc, &kernel, &[]);
        assert_eq!(v.refused.len(), 3);
        // a floor the binary adds is enforced even though the older installed set would allow the override
        assert!(gov
            .evaluate("M", "guard", Some(&json!(true)), &json!(false), false)
            .is_err());
        assert!(gov
            .evaluate("M", "guard", Some(&json!(true)), &json!(true), false)
            .is_ok());
        assert!(gov
            .evaluate("M", "other", Some(&json!(1)), &json!(2), false)
            .is_ok());
        // an installed set stricter than the floor is not overridden by it
        let strict = set(
            "installed kernel",
            vec![
                rule("PP.project.name", "immutable", ""),
                rule("PP.*", "immutable", ""),
            ],
        );
        let gov2 = Governing::from_sets(Some(strict), Some(floor.clone())).unwrap();
        assert!(gov2
            .evaluate("PP", "project.name", None, &json!("shop"), false)
            .is_err());
        // an installed set weaker than the floor does not lower it
        let weak = set("installed kernel", vec![rule("PP.*", "overridable", "")]);
        let gov3 = Governing::from_sets(Some(weak), Some(floor.clone())).unwrap();
        let e = gov3
            .evaluate(
                "PP",
                "readiness.enforce",
                Some(&json!(true)),
                &json!(false),
                false,
            )
            .unwrap_err();
        assert!(e.contains("[rules: floor]"), "{e}");
        // identical sets are evaluated once
        assert_eq!(
            Governing::from_sets(Some(floor.clone()), Some(floor))
                .unwrap()
                .sets
                .len(),
            1
        );
    }
}
