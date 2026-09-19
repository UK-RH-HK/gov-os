//! **Gate U — framework-health SLOs and the HEALTHY conjunction** (Contract v3:976-1008; framework §75-76;
//! BC-P2-44).
//!
//! * [`evaluate`] computes **every** Gate U SLO against the threshold declared for it in
//!   `framework/health/HEALTH_SLOS.yaml` (or the kernel policy key it names). Each SLO names its **owner**: the check
//!   whose finding changes the health state when the threshold is crossed. Where no existing check raises the crossing,
//!   the owner is the governance-suite family `health_slos` ([`family`]), which runs at G1/G3-G6, so the health
//!   scheduler observes every SLO.
//! * [`conditions`] evaluates the thirteen conditions of a HEALTHY repository from the latest outcome of every check
//!   that owns one (the latest suite results in the health state, the latest — or current — doctor run) and the
//!   currency of the green governance evidence. [`repository_verdict`] is the **one** repository verdict: `HEALTHY`
//!   only when all thirteen hold (`gov health status`, `gov status` → `health.repository`, doctor D035).
use super::currency::{Currency, Snapshot};
use super::Family;
use crate::memory::db::RuntimeDb;
use crate::records::RecordStore;
use crate::scheduler::catalogue;
use crate::Project;
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::sync::OnceLock;

/// The SLO and condition declarations (compiled in: `framework/health/` is not a kernel payload directory).
pub const DECLARATIONS: &str = include_str!("../../../framework/health/HEALTH_SLOS.yaml");
/// The family that owns SLO crossings no other check raises.
pub const FAMILY: &str = "health_slos";

pub fn declarations() -> &'static Value {
    static D: OnceLock<Value> = OnceLock::new();
    D.get_or_init(|| {
        serde_yaml::from_str(DECLARATIONS).unwrap_or(json!({"slos": [], "conditions": []}))
    })
}

fn decl(id: &str) -> Value {
    declarations()["slos"]
        .as_array()
        .and_then(|a| a.iter().find(|s| s["id"] == id).cloned())
        .unwrap_or(Value::Null)
}

/// A threshold value: a literal number, or `{policy: "POLICY.dotted.key"}` read from the effective policy.
fn number(p: &Project, v: &Value, default: f64) -> (f64, Value) {
    if let Some(n) = v.as_f64() {
        return (
            n,
            json!({"value": n, "source": "framework/health/HEALTH_SLOS.yaml"}),
        );
    }
    if let Some(key) = v["policy"].as_str() {
        if let Some((pol, dotted)) = key.split_once('.') {
            let n = p.policies().get_f64(pol, dotted, default);
            return (n, json!({"value": n, "source": key}));
        }
    }
    (default, json!({"value": default, "source": "default"}))
}

/// Record types counted by the orphan-graph SLO (see [`evaluate`], SLO 5). Tasks are not among them: whether work
/// traces to the authority it serves is what the task-traceability SLO (SLO 8) measures, under its own population rule;
/// counting an untraced task here as well would judge the same fact twice and bypass that rule.
pub const ORPHAN_SLO_TYPES: &[&str] = &[
    "feature",
    "requirement",
    "scenario",
    "test-obligation",
    "interface",
    "research",
    "experiment",
];

/// Task classes that produce the evidence decisions rest on (outside the task-traceability population, SLO 8).
pub const EVIDENCE_TASK_CLASSES: &[&str] = &["discovery", "research", "experiment"];

/// Whether a task class is outside the task-traceability population (SLO 8): work that creates or maintains the
/// authority (`currency::GOVERNANCE_AFFECTING_TASK_CLASSES`) or produces the evidence decisions rest on
/// ([`EVIDENCE_TASK_CLASSES`]). Their own grounding is judged elsewhere (governance-affecting closes by the currency
/// gate; research and experiment by their lifecycle).
pub fn authority_upstream_class(class: &str) -> bool {
    super::currency::GOVERNANCE_AFFECTING_TASK_CLASSES.contains(&class)
        || EVIDENCE_TASK_CLASSES.contains(&class)
}

/// What an SLO evaluation needs.
pub struct SloCtx<'a> {
    pub p: &'a Project,
    pub store: &'a RecordStore,
    pub db: Option<&'a RuntimeDb>,
    pub snapshot: Option<&'a Snapshot>,
    /// The health state (`scheduler::store::load_state`): latest outcome of every check.
    pub state: &'a Value,
}

fn row(id: &str, value: Value, threshold: Value, crossed: Option<bool>, detail: Value) -> Value {
    let d = decl(id);
    let applicable = crossed.is_some();
    json!({"id": id, "title": d["title"], "contract": d["contract"], "measure": d["measure"], "owner": d["owner"],
           "severity": d["severity"], "value": value, "threshold": threshold, "applicable": applicable,
           "crossed": crossed.unwrap_or(false), "detail": detail})
}

fn state_outcome<'a>(st: &'a Value, check: &str) -> Option<&'a Value> {
    st["checks"].get(check).filter(|e| e.is_object())
}

fn cached_detail(p: &Project, check: &str) -> Value {
    crate::scheduler::store::cache_peek(p, check)
        .map(|c| c["result"]["detail"].clone())
        .unwrap_or(Value::Null)
}

/// Tokens recorded in a cost/usage object under any of the usual names.
fn tokens_of(v: &Value) -> Option<f64> {
    if !v.is_object() {
        return None;
    }
    let mut total = 0.0;
    let mut any = false;
    for k in [
        "tokens_input",
        "tokens_in",
        "input_tokens",
        "tokens_output",
        "tokens_out",
        "output_tokens",
    ] {
        if let Some(n) = v[k].as_f64() {
            total += n;
            any = true;
        }
    }
    if !any {
        for k in ["tokens", "tokens_total", "total_tokens"] {
            if let Some(n) = v[k].as_f64() {
                return Some(n);
            }
        }
        return None;
    }
    Some(total)
}

/// **Every Gate U SLO, computed against its declared threshold.**
pub fn evaluate(c: &SloCtx) -> Vec<Value> {
    let p = c.p;
    let store = c.store;
    let mut out = vec![];
    // 1 governance-suite freshness (owner D021)
    let cur = match c.snapshot {
        Some(s) => Some(Currency::evaluate(p, s)),
        None => Snapshot::take(p).ok().map(|s| Currency::evaluate(p, &s)),
    };
    match &cur {
        Some(cur) => out.push(row(
            "governance_suite_freshness",
            json!({"current": cur.current, "green": cur.green, "changed_classes": cur.changed_classes}),
            json!({"rule": "the latest honoured green record is current (TEST_POLICY.green_record_currency: inputs_hash)"}),
            Some(!cur.current),
            json!({"message": cur.message()}),
        )),
        None => out.push(row(
            "governance_suite_freshness",
            Value::Null,
            Value::Null,
            None,
            json!({"reason": "the input snapshot could not be taken"}),
        )),
    }
    // 2 product-test health (owner product_test_health / D030)
    {
        let st = super::product::status(p, c.snapshot);
        if st["applicable"].as_bool().unwrap_or(false) {
            let fams = st["families"].as_object().cloned().unwrap_or_default();
            let failing: Vec<String> = fams
                .iter()
                .filter(|(_, v)| {
                    v["status"].as_str().map(|s| s != "passed").unwrap_or(false)
                        && v["status"] != "missing"
                })
                .map(|(k, _)| k.clone())
                .collect();
            let missing: Vec<String> = fams
                .iter()
                .filter(|(_, v)| v["status"] == "missing")
                .map(|(k, _)| k.clone())
                .collect();
            out.push(row(
                "product_test_health",
                json!({"failing_families": failing.len(), "families": fams.len(), "never_recorded": missing}),
                json!({"max_failing_families": 0}),
                Some(!failing.is_empty()),
                json!({"failing": failing}),
            ));
        } else {
            out.push(row(
                "product_test_health",
                Value::Null,
                json!({"max_failing_families": 0}),
                None,
                json!({"reason": "no product test command configured or detectable"}),
            ));
        }
    }
    // 3 retrieval Recall@K (owner memory_retrieval_regression)
    {
        let (min, th) = number(
            p,
            &decl("retrieval_recall_at_k")["threshold"],
            p.policies()
                .get_f64("MEMORY_POLICY", "regression.min_recall_at_k", 0.8),
        );
        let d = cached_detail(p, "memory_retrieval_regression");
        let recall = d["recall_at_k"].as_f64();
        let outcome = state_outcome(c.state, "memory_retrieval_regression");
        let failing = outcome.map(|e| !e["ok"].as_bool().unwrap_or(true));
        let crossed = match (recall, failing) {
            (Some(r), f) => Some(r + 1e-9 < min || f.unwrap_or(false)),
            (None, Some(f)) => Some(f),
            (None, None) => None,
        };
        out.push(row(
            "retrieval_recall_at_k",
            json!({"recall_at_k": recall, "mrr": d["mrr"], "queries": d["queries"], "latest_outcome_ok": outcome.map(|e| e["ok"].clone())}),
            th,
            crossed,
            json!({"unmeasured_when": "no memory_retrieval_regression result has been recorded on this machine"}),
        ));
    }
    // 4 stale-index count (owner index_freshness)
    {
        let fr = crate::memory::manifest::freshness(p);
        let n = fr.stale.len() + fr.added.len() + fr.removed.len();
        let (max, th) = number(
            p,
            &decl("stale_index_count")["threshold"],
            p.policies().get_f64(
                "MEMORY_POLICY",
                "freshness.max_stale_artifacts_on_task_close",
                0.0,
            ),
        );
        out.push(row(
            "stale_index_count",
            json!({"stale_index_count": n, "manifest_present": fr.manifest_present, "age_hours": fr.age_hours}),
            th,
            Some(!fr.manifest_present || n as f64 > max),
            json!({"stale": fr.stale.iter().take(10).collect::<Vec<_>>(), "added": fr.added.iter().take(10).collect::<Vec<_>>(), "removed": fr.removed.iter().take(10).collect::<Vec<_>>()}),
        ));
    }
    // 5 orphan-graph count (owner health_slos)
    {
        let (max, th) = number(p, &decl("orphan_graph_count")["threshold"]["max"], 0.0);
        match c.db {
            Some(db) => {
                // a node counts when it is current (ACTIVE) and of a type whose purpose is to be implemented,
                // validated or consumed (ORPHAN_SLO_TYPES): a requirement, scenario, test obligation, interface or
                // feature no relationship reaches, or research/experiment evidence no decision consumes (untraced
                // work is SLO 8's). Decisions and architecture records govern the project as a whole and may stand alone; the
                // project record is the chain's root; audits are evidence; PROVISIONAL candidates awaiting review
                // (e.g. decisions extracted from retired legacy stores) are not orphan authority.
                let orphans: Vec<String> = crate::graph::orphan_nodes(db)
                    .unwrap_or_default()
                    .into_iter()
                    .filter(|id| {
                        store
                            .get(id)
                            .map(|r| {
                                ORPHAN_SLO_TYPES.contains(&r.rtype().as_str())
                                    && r.status() == "ACTIVE"
                                    && !super::lineage::is_generated(r)
                                    && !r.problems.iter().any(|x| x == "archived")
                            })
                            .unwrap_or(false)
                    })
                    .collect();
                out.push(row(
                    "orphan_graph_count",
                    json!({"orphan_graph_nodes": orphans.len()}),
                    th,
                    Some(orphans.len() as f64 > max),
                    json!({"orphans": orphans}),
                ));
            }
            None => out.push(row(
                "orphan_graph_count",
                Value::Null,
                th,
                None,
                json!({"reason": "no derived index (gov rebuild-memory)"}),
            )),
        }
    }
    // 6 unresolved contradictions (owner authority_unambiguous; supersession conflicts / duplicates: D014)
    {
        let cs = crate::context::contradictions::detect_all(store);
        let unresolved: Vec<Value> = cs
            .iter()
            .filter(|x| crate::context::contradictions::resolution(p, store, x).blocks())
            .map(|x| x.to_value())
            .collect();
        let conflicts =
            c.db.and_then(|d| d.get_meta("supersession_conflicts"))
                .and_then(|v| v.as_array().map(|a| a.len()))
                .unwrap_or(0);
        let n = unresolved.len() + conflicts + store.duplicates.len();
        out.push(row(
            "unresolved_contradictions",
            json!({"unresolved_contradictions": n, "contradictions": unresolved.len(), "supersession_conflicts": conflicts, "duplicate_ids": store.duplicates.len()}),
            json!({"max": 0}),
            Some(n > 0),
            json!({"contradictions": unresolved.iter().take(10).collect::<Vec<_>>()}),
        ));
    }
    // 7 unresolved human gates (owner health_slos)
    {
        let t = &decl("unresolved_human_gates")["threshold"];
        let (max_open, th_open) = number(
            p,
            &t["max_open"],
            p.policies()
                .get_f64("BUDGET_POLICY", "defaults.max_parallel_agents", 4.0),
        );
        let (max_age, _) = number(p, &t["max_age_hours"], 72.0);
        let open: Vec<&crate::records::Record> = store
            .of_type("human-gate")
            .into_iter()
            .filter(|g| matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED"))
            .collect();
        let now = chrono::Utc::now();
        let age_of = |g: &crate::records::Record| -> Option<f64> {
            let at = g.get("created");
            chrono::DateTime::parse_from_rfc3339(&at)
                .ok()
                .map(|t| (now - t.with_timezone(&chrono::Utc)).num_minutes() as f64 / 60.0)
        };
        let oldest = open.iter().filter_map(|g| age_of(g)).fold(0.0f64, f64::max);
        let crossed = open.len() as f64 > max_open || oldest > max_age;
        out.push(row(
            "unresolved_human_gates",
            json!({"open_gates": open.len(), "oldest_open_hours": (oldest * 10.0).round() / 10.0}),
            json!({"max_open": th_open, "max_age_hours": max_age}),
            Some(crossed),
            json!({"open": open.iter().map(|g| json!({"id": g.id(), "gate_status": g.get("gate_status"), "age_hours": age_of(g)})).collect::<Vec<_>>()}),
        ));
    }
    // 8 task traceability % (owner health_slos). The population is the work that realises authority: a task of a
    // class whose work creates or maintains the authority itself (the governance-affecting classes: governance,
    // specification, decision preparation, architecture, release, memory, migration) or produces the evidence a
    // decision is taken on (discovery, research, experiment) is upstream of what it would trace to.
    {
        let t = &decl("task_traceability")["threshold"];
        let (min, _) = number(p, &t["min"], 0.8);
        let (pop, _) = number(p, &t["min_population"], 3.0);
        let untraced_closed: Vec<String> =
            crate::context::receipt::untraceable_closed_tasks(p, store)
                .iter()
                .filter_map(|u| u["task"].as_str().map(|s| s.to_string()))
                .collect();
        let mut total = 0usize;
        let mut traced = 0usize;
        let mut untraced = vec![];
        for tk in store.of_type("task") {
            if tk.problems.iter().any(|x| x == "archived")
                || tk.get("task_status") == "CANCELLED"
                || super::lineage::is_generated(tk)
                || !tk.get("generated_by").is_empty()
                || authority_upstream_class(&tk.get("class"))
            {
                continue;
            }
            total += 1;
            let declares = !tk.get("feature").is_empty()
                || crate::records::TASK_INPUT_FIELDS
                    .iter()
                    .any(|f| !tk.list(f).is_empty())
                || tk.data["relations"]
                    .as_array()
                    .map(|a| {
                        a.iter().any(|r| {
                            crate::records::INPUT_RELATION_TYPES
                                .contains(&r["type"].as_str().unwrap_or(""))
                        })
                    })
                    .unwrap_or(false);
            if declares && !untraced_closed.contains(&tk.id()) {
                traced += 1;
            } else {
                untraced.push(tk.id());
            }
        }
        let pct = if total == 0 {
            1.0
        } else {
            traced as f64 / total as f64
        };
        let judged = total as f64 >= pop;
        out.push(row(
            "task_traceability",
            json!({"task_traceability": pct, "traced": traced, "tasks": total}),
            json!({"min": min, "min_population": pop}),
            if judged {
                Some(pct + 1e-9 < min)
            } else {
                Some(false)
            },
            json!({"untraced": untraced.iter().take(20).collect::<Vec<_>>(), "judged": judged}),
        ));
    }
    // 9 feature readiness coverage (owner health_slos; explicit readiness: feature_readiness)
    {
        let t = &decl("feature_readiness_coverage")["threshold"];
        let (min, _) = number(p, &t["min_mean"], 0.5);
        let (pop, _) = number(p, &t["min_population"], 1.0);
        let mut covs = vec![];
        for f in store.of_type("feature") {
            if f.status() != "ACTIVE" || f.problems.iter().any(|x| x == "archived") {
                continue;
            }
            let v = crate::orchestration::readiness::evaluate(p, f);
            covs.push((f.id(), v.coverage));
        }
        let mean = if covs.is_empty() {
            1.0
        } else {
            covs.iter().map(|(_, c)| c).sum::<f64>() / covs.len() as f64
        };
        let judged = covs.len() as f64 >= pop;
        out.push(row(
            "feature_readiness_coverage",
            json!({"feature_readiness_coverage": mean, "active_features": covs.len()}),
            json!({"min_mean": min, "min_population": pop}),
            if judged { Some(mean + 1e-9 < min) } else { Some(false) },
            json!({"per_feature": covs.iter().map(|(f, c)| json!({"feature": f, "coverage": c})).collect::<Vec<_>>()}),
        ));
    }
    // 10 context packet size (owner health_slos)
    {
        let (max, th) = number(
            p,
            &decl("context_packet_size")["threshold"],
            p.policies()
                .get_f64("CONTEXT_POLICY", "max_packet_chars", 60000.0),
        );
        let live: std::collections::BTreeSet<String> = store
            .of_type("task")
            .into_iter()
            .filter(|t| !matches!(t.get("task_status").as_str(), "DONE" | "CANCELLED"))
            .map(|t| t.id())
            .collect();
        let mut sizes: Vec<(String, u64)> = vec![];
        if let Ok(rd) = std::fs::read_dir(p.runtime_dir().join("context")) {
            for e in rd.flatten() {
                let path = e.path();
                let Some(stem) = path.file_stem().map(|s| s.to_string_lossy().to_string()) else {
                    continue;
                };
                if path.extension().map(|x| x != "json").unwrap_or(true) || !live.contains(&stem) {
                    continue;
                }
                if let Ok(v) = crate::util::read_json(&path) {
                    let chars = v["chars"].as_u64().unwrap_or_else(|| {
                        serde_json::to_string(&v)
                            .map(|s| s.len() as u64)
                            .unwrap_or(0)
                    });
                    sizes.push((stem, chars));
                }
            }
        }
        sizes.sort_by(|a, b| b.1.cmp(&a.1));
        let largest = sizes.first().map(|x| x.1).unwrap_or(0);
        out.push(row(
            "context_packet_size",
            json!({"largest_packet_chars": largest, "packets": sizes.len()}),
            th,
            Some(largest as f64 > max),
            json!({"largest": sizes.iter().take(5).map(|(t, c)| json!({"task": t, "chars": c})).collect::<Vec<_>>()}),
        ));
    }
    // 11 tokens / completed task (owner health_slos)
    {
        let (max, th) = number(
            p,
            &decl("tokens_per_completed_task")["threshold"]["max"],
            2_000_000.0,
        );
        let mut by_task: BTreeMap<String, f64> = BTreeMap::new();
        let done: Vec<&crate::records::Record> = store
            .of_type("task")
            .into_iter()
            .filter(|t| t.get("task_status") == "DONE")
            .collect();
        for t in &done {
            if let Some(r) = store.get(&t.get("closed_by_report")) {
                if let Some(n) = tokens_of(&r.data["cost"]).or_else(|| tokens_of(&r.data["usage"]))
                {
                    *by_task.entry(t.id()).or_insert(0.0) += n;
                }
            }
        }
        let done_ids: std::collections::BTreeSet<String> = done.iter().map(|t| t.id()).collect();
        let mut tally = |task: &str, v: &Value| {
            if done_ids.contains(task) {
                if let Some(n) = tokens_of(v) {
                    *by_task.entry(task.to_string()).or_insert(0.0) += n;
                }
            }
        };
        if let Ok(text) = crate::util::read_text(&crate::routing::evidence_path(p)) {
            for l in text.lines() {
                if let Ok(v) = serde_json::from_str::<Value>(l) {
                    if let Some(t) = v["task"].as_str() {
                        tally(t, &v);
                    }
                }
            }
        }
        for e in crate::observability::events(p) {
            if e["name"] == "routing.evidence" {
                continue; // mirrored from the routing evidence above
            }
            if let Some(t) = e["attributes"]["task"].as_str() {
                tally(t, &e["attributes"]);
            }
        }
        let measured = by_task.len();
        let per = if measured == 0 {
            None
        } else {
            Some(by_task.values().sum::<f64>() / measured as f64)
        };
        out.push(row(
            "tokens_per_completed_task",
            json!({"tokens_per_completed_task": per, "done_tasks": done.len(), "done_tasks_with_token_accounting": measured}),
            th,
            match (done.is_empty(), per) {
                (true, _) => Some(false),
                (false, Some(v)) => Some(v > max),
                (false, None) => None,
            },
            json!({"unmeasured": !done.is_empty() && per.is_none(), "note": "tokens are read from the closing report's cost/usage, routing evidence and telemetry attributes (tokens_input/tokens_output or tokens)"}),
        ));
    }
    // 12 first-pass completion (owner health_slos)
    {
        let t = &decl("first_pass_completion")["threshold"];
        let (min, _) = number(p, &t["min"], 0.5);
        let (pop, _) = number(p, &t["min_population"], 1.0);
        let closing: Vec<&crate::records::Record> = store
            .of_type("report")
            .into_iter()
            .filter(|r| !r.get("task").is_empty() && !r.problems.iter().any(|x| x == "archived"))
            .collect();
        let first = closing
            .iter()
            .filter(|r| {
                r.get("outcome") == "success"
                    && r.data
                        .get("repair_count")
                        .and_then(|v| v.as_u64())
                        .unwrap_or(0)
                        == 0
            })
            .count();
        let rate = if closing.is_empty() {
            1.0
        } else {
            first as f64 / closing.len() as f64
        };
        let judged = closing.len() as f64 >= pop;
        out.push(row(
            "first_pass_completion",
            json!({"first_pass_completion_rate": rate, "reports": closing.len(), "first_pass": first}),
            json!({"min": min, "min_population": pop}),
            if judged { Some(rate + 1e-9 < min) } else { Some(false) },
            json!({"judged": judged}),
        ));
    }
    // 13 handoff failure (owner health_slos)
    {
        let t = &decl("handoff_failure")["threshold"];
        let (max, _) = number(p, &t["max_rate"], 0.5);
        let (pop, _) = number(p, &t["min_population"], 1.0);
        let returned: Vec<&crate::records::Record> = store
            .of_type("handoff")
            .into_iter()
            .filter(|h| h.get("handoff_status") == "RETURNED")
            .collect();
        let failed: Vec<String> = returned
            .iter()
            .filter(|h| {
                matches!(
                    h.data["return"]["status"].as_str(),
                    Some("failed") | Some("blocked")
                ) || h.data.get("authority_violations").is_some()
                    || h.data["receipt_validation"]["ok"] == false
            })
            .map(|h| h.id())
            .collect();
        let rate = if returned.is_empty() {
            0.0
        } else {
            failed.len() as f64 / returned.len() as f64
        };
        let judged = returned.len() as f64 >= pop;
        out.push(row(
            "handoff_failure",
            json!({"handoff_failure_rate": rate, "returned": returned.len(), "failed": failed.len()}),
            json!({"max_rate": max, "min_population": pop}),
            if judged { Some(rate > max + 1e-9) } else { Some(false) },
            json!({"failed_handoffs": failed}),
        ));
    }
    // 14 memory rebuild success (owner recovery_rebuild) and 15 fresh-agent reconstruction (owner fresh_agent_reconstruction)
    for (id, check) in [
        ("memory_rebuild_success", "recovery_rebuild"),
        (
            "fresh_agent_reconstruction_success",
            "fresh_agent_reconstruction",
        ),
    ] {
        let o = state_outcome(c.state, check);
        let d = cached_detail(p, check);
        out.push(row(
            id,
            json!({"latest_outcome_ok": o.map(|e| e["ok"].clone()), "latest_result": o.map(|e| e["result"].clone()), "detail": d}),
            decl(id)["threshold"].clone(),
            o.map(|e| !e["ok"].as_bool().unwrap_or(true)),
            json!({"owner_check": check}),
        ));
    }
    out
}

/// The `health_slos` family: every SLO in the detail; a finding for each crossed SLO this family owns (the others
/// are raised by their owning checks), and a low disclosure for each SLO that applies but is unmeasured.
pub fn family(c: &SloCtx, f: &mut Family) {
    let fam = f.id.clone();
    let slos = evaluate(c);
    let mut crossed = vec![];
    for s in &slos {
        let own = s["owner"] == FAMILY;
        if s["crossed"] == true {
            crossed.push(s["id"].clone());
            if own {
                f.findings.push(json!({"severity": s["severity"], "family": fam, "slo": s["id"],
                    "message": format!("Gate U SLO '{}' crossed its threshold: {} vs threshold {} ({})", s["title"].as_str().unwrap_or(""), s["value"], s["threshold"], s["contract"].as_str().unwrap_or("")),
                    "path": Value::Null, "subjects": slo_subjects(s)}));
            }
        } else if own && s["applicable"] == false && s["detail"]["unmeasured"] == true {
            let sev = decl(s["id"].as_str().unwrap_or(""))["unmeasured"]
                .as_str()
                .unwrap_or("low")
                .to_string();
            f.findings.push(json!({"severity": sev, "family": fam, "slo": s["id"],
                "message": format!("Gate U SLO '{}' is not measurable: nothing has been recorded to measure it ({})", s["title"].as_str().unwrap_or(""), s["detail"]["note"].as_str().unwrap_or("")),
                "path": Value::Null}));
        }
    }
    // compact: the measures and titles are declarations (`framework/health/HEALTH_SLOS.yaml`, `gov health status`);
    // each SLO carries its value, threshold, owner and verdict, and the detail that names what crosses it
    let compact: Vec<Value> = slos
        .iter()
        .map(|s| {
            let mut c = json!({"id": s["id"], "value": s["value"], "threshold": s["threshold"], "owner": s["owner"],
                               "applicable": s["applicable"], "crossed": s["crossed"]});
            if s["crossed"] == true && s["owner"] == FAMILY {
                c["detail"] = s["detail"].clone();
            }
            c
        })
        .collect();
    f.detail = json!({"slos": compact, "crossed": crossed, "declarations": "framework/health/HEALTH_SLOS.yaml"});
}

fn slo_subjects(s: &Value) -> Vec<String> {
    let mut v = vec![];
    for k in ["orphans", "untraced", "failed_handoffs"] {
        for x in s["detail"][k].as_array().cloned().unwrap_or_default() {
            if let Some(id) = x.as_str() {
                v.push(id.to_string());
            }
        }
    }
    for x in s["detail"]["open"].as_array().cloned().unwrap_or_default() {
        if let Some(id) = x["id"].as_str() {
            v.push(id.to_string());
        }
    }
    v
}

/// **The thirteen HEALTHY conditions** (Contract v3:995-1008): each with its owning checks, its status (`HOLDS`,
/// `FAILS`, `UNKNOWN`) and the failing owners. `doctor_now` are the checks of a doctor run in progress (doctor D035),
/// read instead of the recorded doctor outcomes.
pub fn conditions(
    st: &Value,
    doctor_now: Option<&[Value]>,
    currency_current: Option<bool>,
) -> Vec<Value> {
    let outcome = |id: &str| -> Option<(bool, String, bool)> {
        if id.starts_with('D') && id.len() == 4 {
            if let Some(chk) = doctor_now {
                return chk.iter().find(|c| c["id"] == id).map(|c| {
                    let ok = c["ok"].as_bool().unwrap_or(true);
                    (
                        ok,
                        if ok {
                            "none".into()
                        } else {
                            c["severity"].as_str().unwrap_or("low").to_string()
                        },
                        true,
                    )
                });
            }
        }
        state_outcome(st, id).map(|e| {
            (
                e["ok"].as_bool().unwrap_or(true),
                e["max_severity"].as_str().unwrap_or("none").to_string(),
                true,
            )
        })
    };
    let mut out = vec![];
    for c in declarations()["conditions"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        let id = c["id"].as_str().unwrap_or("").to_string();
        let owners: Vec<String> = c["owners"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default();
        let mut failing: Vec<Value> = vec![];
        let mut evaluated = 0usize;
        for o in &owners {
            if o == "D021" {
                if let Some(cur) = currency_current {
                    evaluated += 1;
                    if !cur {
                        failing.push(json!({"check": "D021", "severity": "medium", "why": "the green governance evidence is not current"}));
                    }
                    continue;
                }
            }
            if let Some((ok, sev, _)) = outcome(o) {
                evaluated += 1;
                if !ok {
                    failing.push(json!({"check": o, "severity": sev}));
                }
            }
        }
        if id == "H11" {
            // an unresolved critical finding of any evaluated check is an unresolved critical audit finding
            if let Some(m) = st["checks"].as_object() {
                for (cid, e) in m {
                    if e["max_severity"] == "critical"
                        && !failing.iter().any(|f| f["check"] == *cid)
                    {
                        failing.push(json!({"check": cid, "severity": "critical", "why": "its latest outcome carries an unresolved critical finding"}));
                    }
                }
            }
            if let Some(chk) = doctor_now {
                for d in chk {
                    if d["ok"] == false
                        && d["severity"] == "critical"
                        && !failing.iter().any(|f| f["check"] == d["id"])
                    {
                        failing.push(json!({"check": d["id"], "severity": "critical", "why": "critical doctor finding"}));
                    }
                }
            }
        }
        let status = if !failing.is_empty() {
            "FAILS"
        } else if evaluated == 0 {
            "UNKNOWN"
        } else {
            "HOLDS"
        };
        let worst = failing
            .iter()
            .map(|f| f["severity"].as_str().unwrap_or("low").to_string())
            .max_by_key(|s| catalogue::rank(s))
            .unwrap_or_else(|| "none".into());
        out.push(json!({"id": id, "title": c["title"], "contract": c["contract"], "owners": owners, "status": status,
                        "failing": failing, "severity": worst, "evaluated_owners": evaluated}));
    }
    out
}

/// **The one repository verdict** (Contract v3:995 "A repository is HEALTHY only when"): `HEALTHY` only when all
/// thirteen conditions hold; `UNHEALTHY` when a failing condition is high or critical; `DEGRADED` otherwise (a medium
/// or low failure, or a condition not yet evaluated on this machine). The SLOs are carried beside it; a crossed SLO
/// changes the verdict through its owning check's condition, and every crossed SLO is listed.
pub fn repository_verdict(conds: &[Value], slos: &[Value]) -> Value {
    let failing: Vec<&Value> = conds.iter().filter(|c| c["status"] == "FAILS").collect();
    let unknown: Vec<&Value> = conds.iter().filter(|c| c["status"] == "UNKNOWN").collect();
    let crossed: Vec<Value> = slos
        .iter()
        .filter(|s| s["crossed"] == true)
        .map(|s| json!({"slo": s["id"], "owner": s["owner"], "severity": s["severity"], "value": s["value"], "threshold": s["threshold"]}))
        .collect();
    // an SLO another check owns changes the verdict through that check's condition, at the severity the owner judged;
    // an SLO `health_slos` owns changes it directly
    let worst = failing
        .iter()
        .map(|c| c["severity"].as_str().unwrap_or("low"))
        .chain(
            crossed
                .iter()
                .filter(|s| s["owner"] == FAMILY)
                .map(|s| s["severity"].as_str().unwrap_or("medium")),
        )
        .max_by_key(|s| catalogue::rank(s))
        .unwrap_or("none");
    let verdict = if failing.is_empty() && unknown.is_empty() && crossed.is_empty() {
        "HEALTHY"
    } else if catalogue::rank(worst) >= 3 {
        "UNHEALTHY"
    } else {
        "DEGRADED"
    };
    json!({"verdict": verdict, "healthy_only_when": "all thirteen conditions of Contract v3:995-1008 hold",
           "conditions": conds, "failing_conditions": failing.iter().map(|c| c["id"].clone()).collect::<Vec<_>>(),
           "unknown_conditions": unknown.iter().map(|c| c["id"].clone()).collect::<Vec<_>>(),
           "crossed_slos": crossed, "slos": slos})
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_gate_u_slo_and_condition_is_declared_with_an_owner_and_threshold() {
        let d = declarations();
        let slos = d["slos"].as_array().unwrap();
        assert_eq!(slos.len(), 15, "Contract v3:980-993 lists fifteen SLOs");
        for s in slos {
            assert!(s["threshold"].is_object(), "{s}");
            let owner = s["owner"].as_str().unwrap();
            assert!(
                catalogue::get(owner).is_some(),
                "{}: owner {owner} is not a declared check",
                s["id"]
            );
            assert!(
                matches!(s["severity"].as_str(), Some("medium") | Some("high")),
                "{s}"
            );
        }
        let conds = d["conditions"].as_array().unwrap();
        assert_eq!(
            conds.len(),
            13,
            "Contract v3:996-1008 lists thirteen conditions"
        );
        for c in conds {
            for o in c["owners"].as_array().unwrap() {
                assert!(
                    catalogue::get(o.as_str().unwrap()).is_some(),
                    "{}: owner {o} is not a declared check",
                    c["id"]
                );
            }
        }
    }

    #[test]
    fn healthy_only_when_every_condition_holds() {
        let st = json!({"checks": {"graph_integrity": {"ok": true, "max_severity": "low"}, "memory_retrieval_regression": {"ok": false, "max_severity": "high"}}});
        let conds = conditions(&st, Some(&[]), Some(true));
        let h5 = conds.iter().find(|c| c["id"] == "H5").unwrap();
        assert_eq!(h5["status"], "FAILS");
        let v = repository_verdict(&conds, &[]);
        assert_eq!(v["verdict"], "UNHEALTHY");
        // an unevaluated condition is not "holds": the verdict is not HEALTHY
        let st2 = json!({"checks": {}});
        let v2 = repository_verdict(&conditions(&st2, Some(&[]), Some(true)), &[]);
        assert_eq!(v2["verdict"], "DEGRADED");
        // a critical outcome anywhere fails H11
        let st3 =
            json!({"checks": {"path_map_compliance": {"ok": false, "max_severity": "critical"}}});
        let c3 = conditions(&st3, Some(&[]), Some(true));
        assert_eq!(
            c3.iter().find(|c| c["id"] == "H11").unwrap()["status"],
            "FAILS"
        );
        // a crossed SLO keeps the verdict from HEALTHY
        let all_ok: serde_json::Map<String, Value> = catalogue::CHECKS
            .iter()
            .map(|c| {
                (
                    c.id.to_string(),
                    json!({"ok": true, "max_severity": "none"}),
                )
            })
            .collect();
        let st4 = json!({"checks": all_ok});
        let c4 = conditions(&st4, None, Some(true));
        assert_eq!(repository_verdict(&c4, &[])["verdict"], "HEALTHY");
        let slo = json!({"id": "orphan_graph_count", "crossed": true, "severity": "medium", "owner": "health_slos"});
        assert_eq!(repository_verdict(&c4, &[slo])["verdict"], "DEGRADED");
    }
}
