//! `gov status` (fresh-agent reconstruction) and `gov continue` (correct next work with bounded authority).
use crate::checkpoints;
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::orchestration::{control, dag, gates};
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
    Ok(json!({
        "framework": {"name": lock["framework"], "version": lock["version"], "release_hash": lock["release_hash"], "cli_version": crate::CLI_VERSION, "installed_at": lock["installed_at"]},
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
            json!({"status": "NO_RUNNABLE_WORK", "gate": gate_text, "waiting_human": d.waiting_human, "blocked": d.blocked, "suggestion": "run `gov readiness plan <feature>` or create discovery tasks"}),
        );
    };
    let store = RecordStore::load(&p.root);
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
        "skills": skills, "routing": {"minimum_tier": routing["minimum_tier"], "reasoning": routing["reasoning"], "chosen": routing["chosen"]}, "claimed": claimed, "parallel_runnable": candidates.iter().skip(1).take(5).cloned().collect::<Vec<_>>(), "gate": gate_text, "status_summary": st["next_action"]}),
    )
}
