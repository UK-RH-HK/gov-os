//! Model routing (framework §55-58): tiers and reasoning are canonical; model/provider names live only in the overlay.
use crate::util::{now_iso, read_json};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub fn tier_for_class(p: &Project, class: &str) -> String {
    let pol = p.policies();
    let over = p.overlay().get("MODEL_ROUTING_OVERRIDES.yaml");
    if let Some(t) = over
        .get("task_class_overrides")
        .and_then(|m| m.get(class))
        .and_then(|v| v.as_str())
    {
        return t.to_string();
    }
    pol.get(
        "MODEL_ROUTING_POLICY",
        &format!("task_class_minimum_tier.{class}"),
    )
    .and_then(|v| v.as_str().map(|s| s.to_string()))
    .unwrap_or("T2".into())
}

fn tier_rank(t: &str) -> u8 {
    match t {
        "T0" => 0,
        "T1" => 1,
        "T2" => 2,
        "T3" => 3,
        _ => 2,
    }
}
fn reason_rank(r: &str) -> u8 {
    match r {
        "low" => 0,
        "medium" => 1,
        "high" => 2,
        "extra_high" => 3,
        _ => 1,
    }
}

pub fn route(
    p: &Project,
    task: Option<&Value>,
    class: Option<&str>,
    role: Option<&str>,
    radius: Option<&str>,
) -> Result<Value> {
    let pol = p.policies();
    let over = p.overlay().get("MODEL_ROUTING_OVERRIDES.yaml");
    let class = task
        .and_then(|t| t["class"].as_str())
        .or(class)
        .unwrap_or("implementation")
        .to_string();
    let role = task
        .and_then(|t| t["role"].as_str())
        .or(role)
        .unwrap_or(&p.role)
        .to_string();
    let mut tier = tier_for_class(p, &class);
    let mut reasoning = "medium".to_string();
    if let Some(t) = task {
        if let Some(x) = t["minimum_model_tier"].as_str() {
            if tier_rank(x) > tier_rank(&tier) {
                tier = x.into();
            }
        }
        if let Some(r) = t["minimum_reasoning"].as_str() {
            reasoning = r.into();
        }
    }
    let roles = crate::util::read_yaml(
        &crate::kernel_trust::trusted_root(p)
            .join("roles")
            .join("ROLES.yaml"),
    )
    .unwrap_or(json!({}));
    if let Some(r) = roles["roles"]
        .as_array()
        .and_then(|a| a.iter().find(|r| r["id"].as_str() == Some(&role)))
    {
        if let Some(t) = r["minimum_tier"].as_str() {
            if t.starts_with('T') && tier_rank(t) > tier_rank(&tier) {
                tier = t.into();
            }
        }
        if let Some(rr) = r["default_reasoning"].as_str() {
            if reason_rank(rr) > reason_rank(&reasoning) {
                reasoning = rr.into();
            }
        }
    }
    if let Some(ro) = over.get("role_overrides").and_then(|m| m.get(&role)) {
        if let Some(t) = ro["minimum_tier"].as_str() {
            if tier_rank(t) > tier_rank(&tier) {
                tier = t.into();
            }
        }
        if let Some(rr) = ro["default_reasoning"].as_str() {
            reasoning = rr.into();
        }
    }
    if let Some(rd) = radius {
        if let Some(t) = pol
            .get("MODEL_ROUTING_POLICY", &format!("radius_minimum_tier.{rd}"))
            .and_then(|v| v.as_str().map(|s| s.to_string()))
        {
            if tier_rank(&t) > tier_rank(&tier) {
                tier = t;
            }
        }
    }
    let mut candidates = vec![];
    for prov in over
        .get("providers")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default()
    {
        for m in prov["models"].as_array().cloned().unwrap_or_default() {
            let mt = m["tier"].as_str().unwrap_or("T0");
            let mr = m["max_reasoning"].as_str().unwrap_or("low");
            if tier_rank(mt) >= tier_rank(&tier) && reason_rank(mr) >= reason_rank(&reasoning) {
                candidates.push(json!({"provider": prov["name"], "model": m["id"], "tier": mt, "max_reasoning": mr, "cost_per_1k_in": m.get("cost_per_1k_in").and_then(|v| v.as_f64()).unwrap_or(0.0), "cost_per_1k_out": m.get("cost_per_1k_out").and_then(|v| v.as_f64()).unwrap_or(0.0)}));
            }
        }
    }
    let prefer_cheap = over
        .get("preferences")
        .and_then(|x| x.get("prefer_lowest_cost_meeting_tier"))
        .and_then(|v| v.as_bool())
        .unwrap_or(true);
    if prefer_cheap {
        candidates.sort_by(|a, b| {
            let ca = a["cost_per_1k_in"].as_f64().unwrap_or(0.0)
                + a["cost_per_1k_out"].as_f64().unwrap_or(0.0);
            let cb = b["cost_per_1k_in"].as_f64().unwrap_or(0.0)
                + b["cost_per_1k_out"].as_f64().unwrap_or(0.0);
            ca.partial_cmp(&cb)
                .unwrap_or(std::cmp::Ordering::Equal)
                .then(
                    tier_rank(a["tier"].as_str().unwrap_or("T0"))
                        .cmp(&tier_rank(b["tier"].as_str().unwrap_or("T0"))),
                )
        });
    }
    let chosen = candidates.first().cloned();
    Ok(
        json!({"task": task.and_then(|t| t["id"].as_str()), "task_class": class, "role": role, "minimum_tier": tier, "reasoning": reasoning, "candidates": candidates, "chosen": chosen,
              "note": if over.get("providers").and_then(|v| v.as_array()).map(|a| a.is_empty()).unwrap_or(true) { "no provider models configured in MODEL_ROUTING_OVERRIDES.yaml; tier requirement returned for the harness to satisfy" } else { "" }}),
    )
}

pub fn evidence_path(p: &Project) -> std::path::PathBuf {
    p.runtime_dir().join("routing").join("evidence.jsonl")
}

/// Record empirical routing evidence (§58) and mirror it into telemetry.
pub fn record(p: &Project, mut ev: Value) -> Result<Value> {
    crate::authority::require(p, "record_routing_evidence")?;
    let pol = p.policies();
    // MODEL_ROUTING_POLICY.record_evidence: every declared evidence field must be present (explicit null allowed)
    let required = pol.get_list("MODEL_ROUTING_POLICY", "record_evidence");
    fn alias(f: &str) -> String {
        match f {
            "pass_fail" => "pass".into(),
            "latency" => "latency_ms".into(),
            other => other.to_string(),
        }
    }
    let missing: Vec<String> = required
        .iter()
        .filter(|f| ev.get(alias(f)).is_none() && ev.get(f.as_str()).is_none())
        .cloned()
        .collect();
    if !missing.is_empty() {
        return Err(GovError::new("USAGE", format!("routing evidence must carry MODEL_ROUTING_POLICY.record_evidence fields; missing: {missing:?}")));
    }
    // BUDGET_POLICY thresholds: per-task cost and daily spend
    let cost = ev.get("cost").and_then(|v| v.as_f64()).unwrap_or(0.0);
    let max_task = pol.get_f64("BUDGET_POLICY", "defaults.max_task_cost_usd", 25.0);
    let max_daily = pol.get_f64("BUDGET_POLICY", "defaults.max_daily_spend_usd", 200.0);
    let today = crate::util::today();
    let mut spent_today = 0.0;
    if evidence_path(p).exists() {
        for line in crate::util::read_text(&evidence_path(p))?.lines() {
            if let Ok(v) = serde_json::from_str::<Value>(line) {
                if v["ts"]
                    .as_str()
                    .map(|t| t.starts_with(&today))
                    .unwrap_or(false)
                {
                    spent_today += v["cost"].as_f64().unwrap_or(0.0);
                }
            }
        }
    }
    let task_label = ev
        .get("task")
        .and_then(|v| v.as_str())
        .unwrap_or("this workstream")
        .to_string();
    let mut threshold: Option<String> = None;
    if cost > max_task {
        threshold = Some(format!(
            "task cost {cost} > BUDGET_POLICY.defaults.max_task_cost_usd {max_task}"
        ));
    } else if spent_today + cost > max_daily {
        threshold = Some(format!(
            "daily spend {:.2} > BUDGET_POLICY.defaults.max_daily_spend_usd {max_daily}",
            spent_today + cost
        ));
    }
    let o = ev.as_object_mut().unwrap();
    o.insert("ts".into(), json!(now_iso()));
    o.insert("session".into(), json!(p.session_id));
    if let Some(t) = &threshold {
        if pol.get_str(
            "BUDGET_POLICY",
            "on_threshold_exceeded",
            "human_decision_gate",
        ) == "human_decision_gate"
        {
            let g = crate::orchestration::gates::create_system(
                p,
                json!({"question": format!("Budget threshold exceeded: {t}. Continue spending on {task_label}?"), "why_now": "delegated budget exhausted", "current_state": format!("spent today {:.2}", spent_today + cost), "options": [{"id": "A", "description": "raise the budget"}, {"id": "B", "description": "stop this workstream"}], "impact": "cost", "reversibility": "reversible", "recommendation": "B", "confidence": 0.7, "trigger": "budget_threshold", "impact_radius": "R1"}),
            )?;
            o.insert("threshold_exceeded".into(), json!(t));
            o.insert("human_gate".into(), g["id"].clone());
        }
    }
    let path = evidence_path(p);
    if let Some(d) = path.parent() {
        std::fs::create_dir_all(d)?;
    }
    use std::io::Write;
    let mut f = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&path)?;
    writeln!(f, "{}", serde_json::to_string(&ev)?)?;
    crate::observability::emit(p, "routing.evidence", ev.clone())?;
    Ok(ev)
}

pub fn report(p: &Project) -> Result<Value> {
    let path = evidence_path(p);
    let mut by: std::collections::BTreeMap<String, (usize, usize, f64, f64, usize)> =
        std::collections::BTreeMap::new();
    if path.exists() {
        for line in crate::util::read_text(&path)?.lines() {
            let Ok(v) = serde_json::from_str::<Value>(line) else {
                continue;
            };
            let key = format!(
                "{}|{}|{}",
                v["provider"].as_str().unwrap_or("?"),
                v["model"].as_str().unwrap_or("?"),
                v["task_class"].as_str().unwrap_or("?")
            );
            let e = by.entry(key).or_insert((0, 0, 0.0, 0.0, 0));
            e.0 += 1;
            if v["pass"].as_bool().unwrap_or(false) {
                e.1 += 1;
            }
            e.2 += v["cost"].as_f64().unwrap_or(0.0);
            e.3 += v["latency_ms"].as_f64().unwrap_or(0.0);
            e.4 += v["repair_count"].as_u64().unwrap_or(0) as usize;
        }
    }
    let rows: Vec<Value> = by.into_iter().map(|(k, (n, pass, cost, lat, rep))| { let parts: Vec<&str> = k.split('|').collect(); json!({"provider": parts[0], "model": parts[1], "task_class": parts[2], "runs": n, "pass_rate": pass as f64 / n as f64, "avg_cost": cost / n as f64, "avg_latency_ms": lat / n as f64, "avg_repairs": rep as f64 / n as f64}) }).collect();
    let _ = read_json;
    Ok(json!({"rows": rows}))
}
