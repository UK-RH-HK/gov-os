//! Governance families that re-check the decision, change-control, continuity and routing records when the evidence
//! they feed goes stale (Contract v3:95-111 "the appropriate re-check"; A0-J1-03: the re-check must exercise the
//! capability). Each family reads records only; the scheduler declares their inputs (`crate::scheduler::catalogue`).
use super::Family;
use crate::records::RecordStore;
use crate::Project;
use serde_json::{json, Value};
use std::collections::BTreeSet;

fn finding(sev: &str, family: &str, msg: String, path: Option<String>) -> Value {
    json!({"severity": sev, "family": family, "message": msg, "path": path})
}

/// L: gate answers are offered options of presented gates; no task listed as blocked by an unanswered gate is DONE;
/// pending gates are presented.
pub fn human_gate_integrity(store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let mut pending = 0;
    let mut answered = 0;
    for g in store.of_type("human-gate") {
        let status = g.get("gate_status");
        let presented = g
            .data
            .get("presented_in_chat")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);
        match status.as_str() {
            "ANSWERED" => {
                answered += 1;
                let opt = g.data["answer"]["option"].as_str().unwrap_or("");
                let offered: Vec<String> = g.data["options"]
                    .as_array()
                    .map(|a| {
                        a.iter()
                            .filter_map(|o| {
                                o["id"]
                                    .as_str()
                                    .or_else(|| o.as_str())
                                    .map(|s| s.to_string())
                            })
                            .collect()
                    })
                    .unwrap_or_default();
                if !offered.is_empty() && !offered.iter().any(|o| o == opt) {
                    f.findings.push(finding("high", &fam, format!("{} was answered '{opt}', which is not one of its offered options {offered:?}", g.id()), Some(g.path.clone())));
                }
                if !presented {
                    f.findings.push(finding(
                        "high",
                        &fam,
                        format!(
                            "{} is ANSWERED but was never presented to the human (INV-008)",
                            g.id()
                        ),
                        Some(g.path.clone()),
                    ));
                }
            }
            "PENDING" | "PRESENTED" => {
                pending += 1;
                for t in g.list("blocks_tasks") {
                    match store.get(&t) {
                        Some(task) if task.get("task_status") == "DONE" => {
                            f.findings.push(finding(
                                "high",
                                &fam,
                                format!(
                                    "{t} is DONE while {} (which blocks it) is still {status}",
                                    g.id()
                                ),
                                Some(task.path.clone()),
                            ))
                        }
                        None => f.findings.push(finding(
                            "medium",
                            &fam,
                            format!("{} blocks unknown task {t}", g.id()),
                            Some(g.path.clone()),
                        )),
                        _ => {}
                    }
                }
                if !presented {
                    // WS-3's rule: rendering (`gov gate present`) is not presentation; a gate is presented only on
                    // the owner's signed receipt or signed answer (integration observation O-2)
                    let rendered = g
                        .data
                        .get("presentation")
                        .map(|x| !x.is_null())
                        .unwrap_or(false);
                    f.findings.push(finding(
                        "low",
                        &fam,
                        if rendered {
                            format!("{} is pending: rendered to the human channel, awaiting the owner's signed receipt or answer (not yet evidenced as presented)", g.id())
                        } else {
                            format!("{} is pending and was never rendered to the human channel: it exists only in files (INV-008)", g.id())
                        },
                        Some(g.path.clone()),
                    ));
                }
            }
            _ => {}
        }
    }
    f.detail = json!({"pending": pending, "answered": answered});
}

/// K: no CIT left EXECUTING; a COMMITTED CIT carries its approval and, where a human gate was required, that gate is
/// answered.
pub fn change_control_integrity(_p: &Project, store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let mut by_status: std::collections::BTreeMap<String, usize> = Default::default();
    for c in store.of_type("cit") {
        let st = c.get("cit_status");
        *by_status.entry(st.clone()).or_insert(0) += 1;
        match st.as_str() {
            "EXECUTING" => f.findings.push(finding(
                "high",
                &fam,
                format!(
                    "{} was left EXECUTING (interrupted change transaction); run `gov recover`",
                    c.id()
                ),
                Some(c.path.clone()),
            )),
            "COMMITTED" => {
                if c.data.get("approval").map(|a| a.is_null()).unwrap_or(true) {
                    f.findings.push(finding(
                        "high",
                        &fam,
                        format!("{} is COMMITTED without a recorded approval", c.id()),
                        Some(c.path.clone()),
                    ));
                }
                let required = c.data["impact"]["human_gate_required"]
                    .as_bool()
                    .unwrap_or(false);
                let gate = c.get("human_gate");
                if required || !gate.is_empty() {
                    let answered = store
                        .get(&gate)
                        .map(|g| g.get("gate_status") == "ANSWERED")
                        .unwrap_or(false);
                    if !answered {
                        f.findings.push(finding(
                            "high",
                            &fam,
                            format!(
                                "{} is COMMITTED but its required human gate '{}' is not answered",
                                c.id(),
                                if gate.is_empty() {
                                    "<none raised>"
                                } else {
                                    &gate
                                }
                            ),
                            Some(c.path.clone()),
                        ));
                    }
                }
            }
            _ => {}
        }
    }
    f.detail = json!({"cits_by_status": by_status});
}

/// N: handoffs and checkpoints reference known tasks; the latest-checkpoint pointer resolves.
pub fn continuity_checkpoint_handoff(p: &Project, store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let tasks: BTreeSet<String> = store.of_type("task").iter().map(|t| t.id()).collect();
    let handoffs = store.of_type("handoff");
    for h in &handoffs {
        let t = h.get("task");
        if !t.is_empty() && !tasks.contains(&t) {
            f.findings.push(finding(
                "medium",
                &fam,
                format!("handoff {} references unknown task {t}", h.id()),
                Some(h.path.clone()),
            ));
        }
    }
    let checkpoints = store.of_type("checkpoint");
    for c in &checkpoints {
        let t = c.get("task");
        if !t.is_empty() && !tasks.contains(&t) {
            f.findings.push(finding(
                "low",
                &fam,
                format!("checkpoint {} references unknown task {t}", c.id()),
                Some(c.path.clone()),
            ));
        }
    }
    let dir = crate::checkpoints::dir(p);
    let latest = dir.join("LATEST.yaml");
    let mut pointer = Value::Null;
    if latest.exists() {
        match crate::util::read_yaml(&latest) {
            Ok(v) => {
                let target = v["path"].as_str().unwrap_or("").to_string();
                if target.is_empty() || !p.root.join(&target).exists() {
                    f.findings.push(finding(
                        "medium",
                        &fam,
                        format!("latest-checkpoint pointer names a missing checkpoint '{target}'"),
                        Some(crate::util::rel_posix(&latest, &p.root)),
                    ));
                }
                pointer = json!(target);
            }
            Err(e) => f.findings.push(finding(
                "medium",
                &fam,
                format!("latest-checkpoint pointer unreadable: {e}"),
                Some(crate::util::rel_posix(&latest, &p.root)),
            )),
        }
    }
    // G3 checkpoint freshness (Contract v3:796, W12 :1189; WS-4 R2-7): the latest checkpoint still describes the
    // material state it captured. A stale latest checkpoint is disclosed; when it is the resume point of work in
    // progress (its task is claimed) a fresh agent resuming from it would reconstruct stale inputs — medium.
    let mut freshness = Value::Null;
    if !checkpoints.is_empty() {
        if let Ok(fr) = crate::checkpoints::freshness(p, None) {
            if fr["state"] == "STALE" {
                let ck = fr["checkpoint"].as_str().unwrap_or("?").to_string();
                let task = store.get(&ck).map(|c| c.get("task")).unwrap_or_default();
                let live = store
                    .get(&task)
                    .map(|t| {
                        matches!(
                            t.get("task_status").as_str(),
                            "CLAIMED" | "IN_PROGRESS" | "REVIEW"
                        )
                    })
                    .unwrap_or(false);
                let mut x = finding(
                    if live { "medium" } else { "low" },
                    &fam,
                    format!(
                        "latest checkpoint {ck} is STALE: the material state it captured changed since ({}){}",
                        fr["reasons"].as_array().map(|a| a.iter().map(|r| r["kind"].as_str().unwrap_or("?").to_string()).collect::<Vec<_>>().join(", ")).unwrap_or_default(),
                        if live { format!("; it is the resume point of {task}, which is in progress — take a new checkpoint (`gov checkpoint create`)") } else { String::new() }
                    ),
                    store.get(&ck).map(|c| c.path.clone()),
                );
                x["subjects"] = json!([ck, task]);
                f.findings.push(x);
            }
            freshness = json!({"checkpoint": fr["checkpoint"], "state": fr["state"], "reasons": fr["reasons"], "stale_checkpoints": fr["stale_checkpoints"]});
        }
    }
    f.detail = json!({"handoffs": handoffs.len(), "checkpoints": checkpoints.len(), "latest": pointer, "latest_freshness": freshness});
}

fn tier_rank(t: &str) -> Option<u8> {
    match t {
        "T0" => Some(0),
        "T1" => Some(1),
        "T2" => Some(2),
        "T3" => Some(3),
        _ => None,
    }
}

/// M: every task class in use resolves to a declared routing tier at or above its policy minimum; routing evidence
/// names known task classes.
pub fn model_routing_integrity(p: &Project, store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let pol = p.policies();
    let declared: BTreeSet<String> = pol
        .get("MODEL_ROUTING_POLICY", "tiers")
        .and_then(|t| t.as_object().map(|m| m.keys().cloned().collect()))
        .unwrap_or_default();
    let classes: BTreeSet<String> = store
        .of_type("task")
        .iter()
        .map(|t| t.get("class"))
        .filter(|c| !c.is_empty())
        .collect();
    let mut resolved = serde_json::Map::new();
    for c in &classes {
        let tier = crate::routing::tier_for_class(p, c);
        let minimum = pol
            .get(
                "MODEL_ROUTING_POLICY",
                &format!("task_class_minimum_tier.{c}"),
            )
            .and_then(|v| v.as_str().map(|s| s.to_string()));
        if !declared.is_empty() && !declared.contains(&tier) {
            f.findings.push(finding(
                "high",
                &fam,
                format!("task class '{c}' routes to tier '{tier}', which MODEL_ROUTING_POLICY.tiers does not declare"),
                None,
            ));
        }
        match (&minimum, tier_rank(&tier)) {
            (Some(m), Some(r)) if tier_rank(m).map(|mr| r < mr).unwrap_or(false) => {
                f.findings.push(finding("high", &fam, format!("task class '{c}' routes to {tier}, below its policy minimum {m} (a kernel floor may be raised, never lowered)"), None))
            }
            (None, _) => f.findings.push(finding(
                "low",
                &fam,
                format!("task class '{c}' has no MODEL_ROUTING_POLICY.task_class_minimum_tier (defaults to T2)"),
                None,
            )),
            _ => {}
        }
        resolved.insert(c.clone(), json!({"tier": tier, "minimum": minimum}));
    }
    let mut unknown_evidence = BTreeSet::new();
    if let Ok(text) = crate::util::read_text(&crate::routing::evidence_path(p)) {
        let known: BTreeSet<String> = pol
            .get("MODEL_ROUTING_POLICY", "task_class_minimum_tier")
            .and_then(|m| m.as_object().map(|o| o.keys().cloned().collect()))
            .unwrap_or_default();
        for line in text.lines() {
            if let Ok(v) = serde_json::from_str::<Value>(line) {
                let c = v["task_class"].as_str().unwrap_or("").to_string();
                if !c.is_empty() && !known.is_empty() && !known.contains(&c) {
                    unknown_evidence.insert(c);
                }
            }
        }
    }
    for c in &unknown_evidence {
        f.findings.push(finding(
            "low",
            &fam,
            format!("routing evidence names task class '{c}', which has no routing floor"),
            None,
        ));
    }
    f.detail = json!({"task_classes": resolved});
}
