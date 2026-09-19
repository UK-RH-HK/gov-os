//! `gov status` (fresh-agent reconstruction) and `gov continue` (correct next work with bounded authority).
//!
//! * `status` reports the task DAG (runnable is derived: `orchestration::dag::evaluate`), pending gates, controls,
//!   memory freshness, the **health state** (`scheduler::status`: RED/YELLOW/GREEN, active hard-blocks, governance
//!   currency, product tests) and the **release trust of this project's installation**
//!   (`srr::installation::posture_of`), never the machine-wide record of some other project.
//! * `continue` offers only runnable work this session may take (designated role, live claims, overlapping scopes,
//!   independence from recorded authorship), and dispatches a task only with a context packet whose mandatory inputs
//!   are all satisfied (`context::ensure_dispatchable`); the packet compiles whether or not the derived index can be
//!   opened (`context::IndexHandle::Unavailable` degrades only the supplementary block), and every degradation is
//!   reported. With `--claim` the G0 hard-block guard runs before any side effect.
use crate::checkpoints;
use crate::context::IndexHandle;
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::orchestration::{claims, control, dag, gates};
use crate::records::RecordStore;
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub fn status(p: &Project) -> Result<Value> {
    p.require_installed()?;
    let lock = p.lock()?.clone();
    let store = RecordStore::load(&p.root);
    let d = dag::compute(p)?;
    let pend = gates::pending(p);
    let ctl = control::state(p);
    let fr = freshness(p);
    let latest = checkpoints::latest(p);
    let mut reports: Vec<&crate::records::Record> = store.of_type("report");
    reports.sort_by_key(|r| std::cmp::Reverse(r.id()));
    let open_cits: Vec<Value> = store
        .of_type("cit")
        .into_iter()
        .filter(|c| {
            matches!(
                c.get("cit_status").as_str(),
                "PROPOSED" | "SIMULATED" | "APPROVED" | "EXECUTING"
            )
        })
        .map(|c| json!({"id": c.id(), "cit_status": c.get("cit_status"), "title": c.title()}))
        .collect();
    let lctx = crate::lifecycle::Ctx::new(p, &store);
    let features: Vec<Value> = store.of_type("feature").into_iter().map(|f| { let r = crate::orchestration::readiness::evaluate_in(p, &lctx, f); json!({"id": f.id(), "title": f.title(), "coverage": r.coverage, "pre_implementation_ok": r.pre_implementation_ok, "gaps": r.gaps.len()}) }).collect();
    let next_task = d.runnable.first().cloned();
    let mut reads = vec![
        "governance/framework.lock".to_string(),
        "governance/kernel/constitution/CONSTITUTION.md".to_string(),
        "governance/project/PROJECT_POLICY.yaml".to_string(),
        "governance/project/REPOSITORY_CONTRACT.yaml".to_string(),
    ];
    if let Some(l) = &latest {
        if let Some(pth) = store
            .of_type("checkpoint")
            .iter()
            .find(|c| c.id() == l["id"].as_str().unwrap_or(""))
            .map(|c| c.path.clone())
        {
            reads.push(pth);
        }
    }
    if let Some(t) = &next_task {
        if let Some(r) = store.get(t) {
            reads.push(r.path.clone());
        }
        reads.push(format!(".governance-runtime/context/{t}.json"));
    }
    for g in pend.iter().take(3) {
        if let Some(r) = store.get(g["id"].as_str().unwrap_or("")) {
            reads.push(r.path.clone());
        }
    }
    let next_action = if ctl["mode"].as_str() == Some("PAUSED") {
        "paused: resolve the pause reason, then `gov resume`".to_string()
    } else if !pend.is_empty()
        && pend
            .iter()
            .any(|g| !g["presented_in_chat"].as_bool().unwrap_or(false))
    {
        // the human answers through the authenticated human channel (`gov trust human-channel`); no command asserts a
        // human identity on the agent's behalf (BC-P2-10)
        format!("render human gate {id} for the human (`gov gate present {id}`); the human answers through the authenticated human channel (`gov trust human-channel`), then `gov decide {id} --option <id>` relays the owner-signed answer; continue independent runnable work", id = pend[0]["id"].as_str().unwrap_or("?"))
    } else if !fr.manifest_present {
        "gov rebuild-memory".into()
    } else if let Some(t) = &next_task {
        format!("gov continue → claim {t}")
    } else if !pend.is_empty() {
        format!("waiting on human gate {}", pend[0]["id"])
    } else {
        "no runnable tasks: run readiness planning or discovery".into()
    };
    // Signed Release Root v1: report the release-trust posture honestly here too, so state reconstruction never
    // presents a below-floor or unauthenticated installation as simply "installed". `framework.*` describes what the
    // LOCK says; `release_trust.*` describes what was actually VERIFIED — for THIS project's installation, from the
    // machine's protected per-project record (`srr::installation::posture_of`, BC-P2-36), not the machine-wide record
    // of whichever project installed last. Those are different predicates and are never merged (frozen R0 item 11).
    let posture = crate::srr::installation::posture_of(&p.root);
    let degraded = crate::srr::state::MachineState::open()
        .ok()
        .and_then(|ms| crate::srr::breakglass::Degraded::load(&ms, crate::FRAMEWORK_NAME));
    let established = posture["authenticity_established"]
        .as_bool()
        .unwrap_or(false);
    let bound = &posture["bound_release"];
    let release_trust = json!({
        "posture": posture.get("machine_posture").cloned().unwrap_or(json!("UNDETERMINED")),
        "authenticity": posture.get("authenticity").cloned().unwrap_or(json!("UNKNOWN")),
        "authenticity_established": established,
        "verified_release": if established { bound["release_version"].clone() } else { Value::Null },
        "verified_payload_hash": if established { bound["payload_hash"].clone() } else { Value::Null },
        "bound_release": bound,
        "integrity": posture["integrity"],
        "disclosure": posture["disclosure"],
        "scope": "this project's installation (machine-protected per-project record)",
        "currency": "UNKNOWN_BETWEEN_INGRESSES",
        "revocation_knowledge": "only revocations this machine has received; no claim about unseen or future revocations",
        "marking": degraded.as_ref().map(|d| d.marking.clone()),
        "below_floor": degraded.is_some(),
        "detail": "gov trust status",
    });
    // the health state a fresh agent must see before relying on anything (BC-P2-06/43/44 reporting side)
    let health = crate::scheduler::status(p).unwrap_or_else(
        |e| json!({"state": "UNKNOWN", "error": {"code": e.code, "message": e.message}}),
    );
    Ok(json!({
        "framework": {"name": lock["framework"], "version": lock["version"], "release_hash": lock["release_hash"], "cli_version": crate::CLI_VERSION, "installed_at": lock["installed_at"]},
        "release_trust": release_trust,
        "health": health,
        "project": {"name": p.project_name(), "alias": p.project_alias(), "root": p.root.display().to_string(), "commit": p.git_commit(), "branch": p.git_branch()},
        "control": ctl, "session": p.session_id, "role": p.role,
        "memory": {"runtime_present": p.db_path().exists(), "index_fresh": fr.fresh, "index_manifest_present": fr.manifest_present, "stale": fr.stale.len(), "added": fr.added.len(), "removed": fr.removed.len()},
        "tasks": {"counts": d.counts, "runnable": d.runnable, "waiting_human": d.waiting_human, "blocked": d.blocked.iter().take(10).cloned().collect::<Vec<_>>(), "longest_chain": d.longest_chain, "cycles": d.cycles},
        "human_gates": pend, "open_transactions": open_cits, "latest_checkpoint": latest.map(|l| json!({"id": l["id"], "next_action": l["next_action"], "task": l["task"], "session": l["session"]})),
        "recent_reports": reports.iter().take(3).map(|r| json!({"id": r.id(), "task": r.get("task"), "outcome": r.get("outcome")})).collect::<Vec<_>>(),
        "features": features, "records": store.records.len(), "next_task": next_task, "next_action": next_action, "fresh_agent_reads": reads,
    }))
}

/// `gov continue`: the next work this session can take, with its context packet. `db` is the derived index as the
/// caller could open it (`&RuntimeDb`, or `IndexHandle::Unavailable` when it cannot be opened): only the
/// supplementary block of the packet depends on it (Contract v3 W10).
pub fn continue_work<'a>(
    p: &Project,
    db: impl Into<IndexHandle<'a>>,
    claim: bool,
) -> Result<Value> {
    p.require_installed()?;
    if claim {
        // G0 (tier contract, IP-WS02-03): a hard-block governing claims refuses before any side effect
        crate::scheduler::guard(p, crate::scheduler::catalogue::ops::TASK_CLAIM, &[])?;
    }
    let (db_open, db_unavailable): (Option<&RuntimeDb>, Option<GovError>) = match db.into() {
        IndexHandle::Open(d) => (Some(d), None),
        IndexHandle::Unavailable(e) => (None, Some(e)),
    };
    let handle = || -> IndexHandle<'a> {
        match (db_open, &db_unavailable) {
            (Some(d), _) => IndexHandle::Open(d),
            (None, Some(e)) => IndexHandle::Unavailable(e.clone()),
            (None, None) => {
                IndexHandle::Unavailable(GovError::new("INDEX_UNAVAILABLE", "no index handle"))
            }
        }
    };
    // the work the events since the last governed operation call for is in the DAG before the next work is chosen
    // (BC-P2-24): failed tests, findings, discoveries, decisions, lessons, capability gaps, failures
    let generated = crate::orchestration::generation::reconcile(
        p,
        &crate::orchestration::generation::Options::triggered_by("continue"),
    )
    .map(|r| crate::orchestration::generation::summary(&r))
    .unwrap_or_else(|e| json!({"error": {"code": e.code, "message": e.message}}));
    let st = status(p)?;
    let ctl = control::state(p);
    let mut gate_text = None;
    let pend = gates::pending(p);
    if let Some(g) = pend.first() {
        let (_, text) = gates::present(p, g["id"].as_str().unwrap_or(""))?;
        gate_text = Some(text);
    }
    let d = dag::compute(p)?;
    // prefer tasks on the longest open dependency chain, then lowest id
    let mut candidates: Vec<String> = d.runnable.clone();
    candidates.sort_by_key(|t| (if d.longest_chain.contains(t) { 0 } else { 1 }, t.clone()));
    // offer only work this session can take (BC-P2-14/15/34): not designated for another role, not held by another
    // session, not overlapping the mutation scope of another session's live claim, not work whose independence this
    // session would break
    let store = RecordStore::load(&p.root);
    let (candidates, mut deferred) = partition_for_session(p, &store, candidates)?;
    if ctl["mode"].as_str() == Some("PAUSED") {
        return Ok(
            json!({"status": "PAUSED", "gate": gate_text, "message": "execution paused; gov resume after the reason is resolved"}),
        );
    }
    if !pend.is_empty()
        && !p
            .policies()
            .get_bool("HUMAN_GATE_POLICY", "continue_independent_work", true)
    {
        return Ok(
            json!({"status": "WAITING_HUMAN", "gate": gate_text, "message": "HUMAN_GATE_POLICY.continue_independent_work=false: work halts while a gate is pending", "generated_work": generated}),
        );
    }
    // dispatch (W4 line 1112): a packet whose mandatory inputs are not all satisfied is never dispatched; the next
    // candidate is tried and the refused one is reported
    let mut chosen: Option<(String, Value)> = None;
    let mut producer_note: Option<Value> = None;
    for next in &candidates {
        match crate::context::compile(p, handle(), next) {
            Ok(pk) => match crate::context::ensure_dispatchable(&pk) {
                Ok(()) => {
                    chosen = Some((next.clone(), pk));
                    break;
                }
                // a task producing its feature's specification is not blocked by what the feature still lacks
                // (the same rule the DAG and close apply: orchestration::dag::packet_blocked_only_by_inherited)
                Err(_)
                    if store
                        .get(next)
                        .is_some_and(|t| dag::packet_blocked_only_by_inherited(t, &pk)) =>
                {
                    producer_note = Some(json!({"kind": "inherited_inputs_absent", "missing_inputs": pk["input_manifest"]["missing_inputs"], "input_violations": pk["input_manifest"]["input_violations"],
                        "effect": "the packet lacks inputs the task's feature declares but does not have yet; this task produces the feature's specification, so it is dispatched"}));
                    chosen = Some((next.clone(), pk));
                    break;
                }
                Err(e) => deferred.push(json!({"task": next, "reason": e.message, "code": e.code, "details": e.details})),
            },
            Err(e) => deferred.push(json!({"task": next, "reason": format!("its context packet could not be compiled: {}", e.message), "code": e.code})),
        }
    }
    let Some((next, packet)) = chosen else {
        return Ok(
            json!({"status": "NO_RUNNABLE_WORK", "gate": gate_text, "waiting_human": d.waiting_human, "blocked": d.blocked, "deferred": deferred, "generated_work": generated, "suggestion": if deferred.is_empty() { "run `gov readiness plan <feature>` or create discovery tasks" } else { "runnable work exists but this session cannot take it now (see `deferred`): act in the designated role from an independent session, wait for the overlapping claims to close, or satisfy the mandatory inputs the packet names" }}),
        );
    };
    // governed degradations of the dispatch, reported rather than silent
    let mut degraded: Vec<Value> = producer_note.into_iter().collect();
    if let Some(e) = &db_unavailable {
        degraded.push(json!({"kind": "index_unavailable", "code": e.code, "message": e.message, "effect": "the supplementary (retrieved) block of the packet is empty; the mandatory inputs are delivered in full"}));
    }
    if packet["budget"]["over_budget"].as_bool().unwrap_or(false) {
        degraded.push(json!({"kind": "context_packet_over_budget", "budget": packet["budget"], "effect": "supplementary slices were dropped; the mandatory inputs were not displaced"}));
    }
    if let Some(r) = packet["retrieved_intelligence"]["degraded"]
        .as_array()
        .filter(|a| !a.is_empty())
    {
        degraded.push(json!({"kind": "supplementary_retrieval_degraded", "stages": r}));
    }
    let task = store
        .get(&next)
        .map(|r| r.data.clone())
        .unwrap_or(json!({}));
    let skills = crate::skills::resolve(p, &task)?;
    let routing = crate::routing::route(p, Some(&task), None, None, None)?;
    let mut claimed = Value::Null;
    if claim {
        claimed = crate::orchestration::tasks::claim(p, &next)?;
    }
    Ok(
        json!({"status": "NEXT_WORK", "task": next, "task_contract": task, "context_packet": {"path": format!(".governance-runtime/context/{next}.json"), "deterministic_hash": packet["deterministic_hash"], "packet_hash": packet["packet_hash"], "chars": packet["chars"], "delivery_state": packet["delivery_state"], "receipt_contract": packet["receipt_contract"]},
        "skills": skills, "routing": {"minimum_tier": routing["minimum_tier"], "reasoning": routing["reasoning"], "chosen": routing["chosen"]}, "claimed": claimed, "parallel_runnable": candidates.iter().filter(|t| **t != next).take(5).cloned().collect::<Vec<_>>(), "deferred": deferred, "degraded": degraded, "gate": gate_text, "status_summary": st["next_action"], "generated_work": generated}),
    )
}

/// Split runnable tasks into those the acting session can claim now and those it cannot, with the reason: designated
/// for another role, held by another session's live claim, a mutation scope overlapping another session's live
/// claim, or independence this session would break (the same rules [`crate::orchestration::tasks::claim`] enforces).
pub fn partition_for_session(
    p: &Project,
    store: &RecordStore,
    runnable: Vec<String>,
) -> Result<(Vec<String>, Vec<Value>)> {
    let live = claims::live(p)?;
    let others: Vec<&Value> = live
        .iter()
        .filter(|c| c["session_id"].as_str() != Some(p.session_id.as_str()))
        .collect();
    let ctx = dag::DagCtx::new(p, store);
    let mut ok = vec![];
    let mut deferred = vec![];
    for id in runnable {
        let Some(t) = store.get(&id) else {
            continue;
        };
        let role = t.get("role");
        if !role.is_empty() && role != p.role {
            deferred.push(json!({"task": id, "reason": format!("designated for role '{role}' (acting role '{}')", p.role), "designated_role": role}));
            continue;
        }
        if let Some(h) = others
            .iter()
            .find(|c| c["task_id"].as_str() == Some(id.as_str()))
        {
            deferred.push(json!({"task": id, "reason": format!("claimed by session {}", h["session_id"].as_str().unwrap_or("?")), "holder": h["session_id"]}));
            continue;
        }
        let scope = claims::scope_of_task(t);
        let conflicts: Vec<Value> = others
            .iter()
            .filter(|c| claims::scopes_overlap(&scope, &claims::scope_of_claim(c)))
            .map(|c| c["task_id"].clone())
            .collect();
        if !conflicts.is_empty() {
            deferred.push(json!({"task": id, "reason": format!("mutation scope {} overlaps live claim(s) {conflicts:?} of other sessions", claims::describe_scope(&scope)), "conflicts": conflicts}));
            continue;
        }
        let indep =
            crate::orchestration::tasks::independence_conflicts(&ctx, store, t, &p.session_id);
        if !indep.is_empty() {
            deferred.push(json!({"task": id, "reason": format!("independence (recorded authorship): {}", indep.join("; ")), "independence": indep}));
            continue;
        }
        ok.push(id);
    }
    Ok((ok, deferred))
}
