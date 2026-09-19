//! `gov status` (fresh-agent reconstruction) and `gov continue` (correct next work with bounded authority).
use crate::checkpoints;
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::orchestration::{claims, control, dag, gates};
use crate::records::RecordStore;
use crate::{Project, Result};
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
    let features: Vec<Value> = store.of_type("feature").into_iter().map(|f| { let r = crate::orchestration::readiness::evaluate(p, f); json!({"id": f.id(), "title": f.title(), "coverage": r.coverage, "pre_implementation_ok": r.pre_implementation_ok, "gaps": r.gaps.len()}) }).collect();
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
        format!("present human gate {} in chat (`gov gate present {}`), continue independent runnable work", pend[0]["id"], pend[0]["id"])
    } else if !fr.manifest_present {
        "gov rebuild-memory".into()
    } else if let Some(t) = &next_task {
        format!("gov continue → claim {t}")
    } else if !pend.is_empty() {
        format!("waiting on human gate {}", pend[0]["id"])
    } else {
        "no runnable tasks: run readiness planning or discovery".into()
    };
    // Signed Release Root v1: report the machine's release-trust posture honestly here too, so state
    // reconstruction never presents a below-floor or unauthenticated installation as simply "installed".
    // `framework.*` describes what the LOCK says; `release_trust.*` describes what was actually VERIFIED. Those
    // are different predicates and are never merged (frozen R0 item 11).
    let release_trust = crate::srr::state::MachineState::open()
        .ok()
        .map(|ms| {
            let installed = crate::srr::state::InstalledRecord::load(&ms, crate::FRAMEWORK_NAME);
            let degraded = crate::srr::breakglass::Degraded::load(&ms, crate::FRAMEWORK_NAME);
            json!({
                "posture": if ms.is_provisioned() { "PROVISIONED" } else { "UNPROVISIONED" },
                "authenticity": installed.as_ref().map(|i| i.authenticity.clone())
                    .unwrap_or_else(|| "UNKNOWN".into()),
                "verified_release": installed.as_ref().map(|i| i.release_version.clone()),
                "verified_payload_hash": installed.as_ref().map(|i| i.payload_hash.clone()),
                "currency": "UNKNOWN_BETWEEN_INGRESSES",
                "revocation_knowledge": "only revocations this machine has received; no claim about unseen or future revocations",
                "marking": degraded.as_ref().map(|d| d.marking.clone()),
                "below_floor": degraded.is_some(),
                "detail": "gov trust status",
            })
        })
        .unwrap_or(Value::Null);
    Ok(json!({
        "framework": {"name": lock["framework"], "version": lock["version"], "release_hash": lock["release_hash"], "cli_version": crate::CLI_VERSION, "installed_at": lock["installed_at"]},
        "release_trust": release_trust,
        "project": {"name": p.project_name(), "alias": p.project_alias(), "root": p.root.display().to_string(), "commit": p.git_commit(), "branch": p.git_branch()},
        "control": ctl, "session": p.session_id, "role": p.role,
        "memory": {"runtime_present": p.db_path().exists(), "index_fresh": fr.fresh, "index_manifest_present": fr.manifest_present, "stale": fr.stale.len(), "added": fr.added.len(), "removed": fr.removed.len()},
        "tasks": {"counts": d.counts, "runnable": d.runnable, "waiting_human": d.waiting_human, "blocked": d.blocked.iter().take(10).cloned().collect::<Vec<_>>(), "longest_chain": d.longest_chain, "cycles": d.cycles},
        "human_gates": pend, "open_transactions": open_cits, "latest_checkpoint": latest.map(|l| json!({"id": l["id"], "next_action": l["next_action"], "task": l["task"], "session": l["session"]})),
        "recent_reports": reports.iter().take(3).map(|r| json!({"id": r.id(), "task": r.get("task"), "outcome": r.get("outcome")})).collect::<Vec<_>>(),
        "features": features, "records": store.records.len(), "next_task": next_task, "next_action": next_action, "fresh_agent_reads": reads,
    }))
}

pub fn continue_work(p: &Project, db: &RuntimeDb, claim: bool) -> Result<Value> {
    p.require_installed()?;
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
    // offer only work this session can take (BC-P2-14/15): not designated for another role, not held by another
    // session, and not overlapping the mutation scope of another session's live claim
    let store = RecordStore::load(&p.root);
    let (candidates, deferred) = partition_for_session(p, &store, candidates)?;
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
            json!({"status": "WAITING_HUMAN", "gate": gate_text, "message": "HUMAN_GATE_POLICY.continue_independent_work=false: work halts while a gate is pending"}),
        );
    }
    let Some(next) = candidates.first().cloned() else {
        return Ok(
            json!({"status": "NO_RUNNABLE_WORK", "gate": gate_text, "waiting_human": d.waiting_human, "blocked": d.blocked, "deferred": deferred, "suggestion": if deferred.is_empty() { "run `gov readiness plan <feature>` or create discovery tasks" } else { "runnable work exists but this session cannot take it now (see `deferred`): act in the designated role, or wait for the overlapping claims to close" }}),
        );
    };
    let task = store
        .get(&next)
        .map(|r| r.data.clone())
        .unwrap_or(json!({}));
    let packet = crate::context::compile(p, db, &next)?;
    let skills = crate::skills::resolve(p, &task)?;
    let routing = crate::routing::route(p, Some(&task), None, None, None)?;
    let mut claimed = Value::Null;
    if claim {
        claimed = crate::orchestration::tasks::claim(p, &next)?;
    }
    Ok(
        json!({"status": "NEXT_WORK", "task": next, "task_contract": task, "context_packet": {"path": format!(".governance-runtime/context/{next}.json"), "deterministic_hash": packet["deterministic_hash"], "packet_hash": packet["packet_hash"], "chars": packet["chars"]},
        "skills": skills, "routing": {"minimum_tier": routing["minimum_tier"], "reasoning": routing["reasoning"], "chosen": routing["chosen"]}, "claimed": claimed, "parallel_runnable": candidates.iter().skip(1).take(5).cloned().collect::<Vec<_>>(), "deferred": deferred, "gate": gate_text, "status_summary": st["next_action"]}),
    )
}

/// Split runnable tasks into those the acting session can claim now and those it cannot, with the reason: designated
/// for another role, held by another session's live claim, or a mutation scope overlapping another session's live
/// claim (the same rules [`crate::orchestration::tasks::claim`] enforces atomically).
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
        ok.push(id);
    }
    Ok((ok, deferred))
}
