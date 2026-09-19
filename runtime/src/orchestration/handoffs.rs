//! Typed A2A handoffs (framework §25) and the spawned-agent return contract (§61). INV-014.
//!
//! ## Handoff continuity (repair iteration 1, round 2; BC-P2-05, Contract v3:742, :1160)
//!
//! A handoff carries the task's mandatory inputs to another worker, so it is where input continuity is enforced
//! (`checkpoints::FRESHNESS_POLICY`):
//! * **missing or violated mandatory inputs → refused** (`HANDOFF_INPUTS_UNSATISFIED`): the receiving worker would
//!   start without its inputs, or with contradictory ones;
//! * **a stale or invalidated packet → re-delivered**: the packet is recompiled at the current inputs and the handoff
//!   names the new packet hash and the inputs that were stale; when work was already in progress on the stale inputs
//!   the handoff is **explicitly degraded** and the change is propagated to the task (retest required);
//! * the result and the record state the freshness the handoff was created under (`freshness`), and the
//!   `before_handoff` checkpoint records it and the checkpoint it supersedes.
//! The G0 guard (`scheduler::guard(handoff.create)`) and the G3 tier (IP-WS02-05/07) run at creation.
//!
//! ## Round 3 (WS-4)
//!
//! * **The G0 guard is scoped to what the handoff relies on** (availability rule, P2-HO-0031): it is asked for the
//!   task record and every input the task's manifest delivers, so a path-scoped hard-block refuses the handoff only
//!   when it governs something the receiving worker would rely on.
//! * **Handoff records are T2-sealed** as written by `handoff create`, and re-sealed by `handoff return` only when the
//!   seal verified before (O-7): a later hand edit is observable.
//! * **The targeted propagation of a stale packet** is recorded as a sealed system transaction
//!   (`cit::propagate_as_transaction`), like every propagation outside CIT-E.
use crate::orchestration::control;
use crate::records::{new_record, save_record, RecordStore};
use crate::util::{now_iso, read_json, read_yaml};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

/// The freshness of `task`'s delivered inputs at handoff time, re-delivering a stale packet. Returns the
/// `freshness` block and the degradations. Refuses when the mandatory inputs are unsatisfied.
fn handoff_freshness(p: &Project, task: &str) -> Result<(Value, Vec<String>)> {
    let store = RecordStore::load(&p.root);
    let t = store
        .get(task)
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("task {task} not found")))?;
    let m = crate::context::manifest::resolve(p, &store, t);
    if !m.satisfied() {
        return Err(GovError::new(
            "HANDOFF_INPUTS_UNSATISFIED",
            format!("{task} cannot be handed off: {}. A worker must not receive a task whose mandatory inputs are missing, superseded, contradictory or outside their declared constraints (Contract v3 W9 line 1160); `gov context manifest {task}` shows the resolution", m.blocking_reason().unwrap_or_default()),
        )
        .with_details(json!({"task": task, "missing_inputs": m.missing(), "input_violations": m.violations(), "contradictions": m.contradictions, "policy": crate::checkpoints::FRESHNESS_POLICY})));
    }
    let packet_file = p.runtime_dir().join("context").join(format!("{task}.json"));
    let previous = read_json(&packet_file).ok();
    // compared on normative content (bookkeeping on an input is not a change); a packet from before normative
    // hashes existed is compared on bytes
    let normative = previous
        .as_ref()
        .map(|k| k.get("input_normative_hashes").is_some())
        .unwrap_or(false);
    let now: std::collections::BTreeMap<String, Option<String>> = m
        .entries
        .iter()
        .filter(|e| e.delivered() && e.slot != crate::context::manifest::Slot::Dependency)
        .map(|e| {
            (
                e.id.clone(),
                if normative {
                    e.normative_hash.clone()
                } else {
                    e.content_hash.clone()
                },
            )
        })
        .collect();
    let mut stale: Vec<crate::cit::propagation::InputChange> = vec![];
    let mut invalidated = false;
    if let Some(prev) = &previous {
        invalidated = prev
            .get("invalidated")
            .map(|v| !v.is_null())
            .unwrap_or(false);
        let key = if normative {
            "input_normative_hashes"
        } else {
            "input_hashes"
        };
        let delivered = prev[key].as_object().cloned().unwrap_or_default();
        for (id, cur) in &now {
            let d = delivered.get(id).and_then(|v| v.as_str()).map(String::from);
            if d.as_deref() != cur.as_deref() {
                stale.push(crate::cit::propagation::InputChange {
                    id: id.clone(),
                    from: d,
                    to: m
                        .entries
                        .iter()
                        .find(|e| &e.id == id)
                        .and_then(|e| e.normative_hash.clone()),
                });
            }
        }
    }
    let state = match (&previous, stale.is_empty() && !invalidated) {
        (None, _) => "DELIVERED",
        (Some(_), true) => "CURRENT",
        (Some(_), false) => "REFRESHED",
    };
    let packet = if state == "CURRENT" {
        previous.clone().unwrap_or(Value::Null)
    } else {
        crate::context::compile_tolerant(p, task)?
    };
    crate::context::ensure_dispatchable(&packet)?;
    let started = crate::orchestration::claims::get(p, task)
        .ok()
        .flatten()
        .is_some()
        || matches!(
            t.get("task_status").as_str(),
            "CLAIMED" | "IN_PROGRESS" | "REVIEW"
        );
    let mut degraded = vec![];
    let mut propagated = Value::Null;
    if !stale.is_empty() && started {
        degraded.push(format!("work on {task} was in progress against stale inputs ({}); the receiving worker gets the current packet and must revalidate that work (the task is marked retest_required)", stale.iter().map(|c| c.id.clone()).collect::<Vec<_>>().join(", ")));
        let store = RecordStore::load(&p.root);
        let ids: Vec<String> = stale.iter().map(|c| c.id.clone()).collect();
        let only: std::collections::BTreeSet<String> = [task.to_string()].into_iter().collect();
        let pl = crate::cit::propagation::plan(p, &store, &ids, None, Some(&only));
        // recorded as a sealed system transaction, like every propagation outside CIT-E (WS-5 IP-R3-3)
        propagated = crate::cit::propagate_as_transaction(
            p,
            &pl,
            &stale,
            "gov handoff create",
            &crate::cit::propagation::ApplyOptions {
                generate_rework: false,
            },
        )
        .unwrap_or_else(|e| json!({"error": {"code": e.code, "message": e.message}}));
    }
    let fresh = json!({
        "state": state,
        "stale_inputs": stale.iter().map(|c| json!({"id": c.id, "delivered": c.from, "current": c.to})).collect::<Vec<_>>(),
        "previous_packet_invalidated": invalidated,
        "previous_packet_hash": previous.as_ref().map(|k| k["packet_hash"].clone()).unwrap_or(Value::Null),
        "packet_hash": packet["packet_hash"],
        "delivery_state": packet["delivery_state"],
        "work_in_progress": started,
        "propagation": propagated,
        "policy": crate::checkpoints::FRESHNESS_POLICY,
    });
    Ok((fresh, degraded))
}

/// What a handoff of `task` relies on, as repository paths: the task record and every input its manifest delivers.
/// The G0 guard is asked for exactly these (availability rule, P2-HO-0031): a hard-block scoped to paths refuses the
/// handoff only when it governs something the receiving worker would rely on; work outside the block stays available.
fn reliance_paths(p: &Project, store: &RecordStore, task: &str) -> Vec<String> {
    let Some(t) = store.get(task) else {
        return vec![];
    };
    let mut v = vec![t.path.clone()];
    for e in crate::context::manifest::resolve(p, store, t).entries {
        if e.delivered() && !e.path.is_empty() {
            v.push(e.path.clone());
        }
    }
    v.sort();
    v.dedup();
    v
}

pub fn create(p: &Project, mut fields: Value) -> Result<Value> {
    // the write guard (kernel trust, break-glass, FREEZE_WRITES / PAUSE); the health half is decided below, on the one
    // availability host API, with the handoff's subjects and the task's declared remedies in hand (round 4, WS-4
    // IP-R3-WS04-11: the generic whole-operation guard refused the handoff of the very work that repairs a block)
    control::guard_write_host(p, "handoff create")?;
    crate::authority::require(p, "create_handoff")?;
    let store = RecordStore::load(&p.root);
    // G0 (tier contract, IP-WS02-05/07) under the availability rule: an active hard-block governing what the handoff
    // relies on refuses it — except the handoff of work that remedies that block (the task declares the block's check
    // among its `remedies` and its subjects reach the block's), which stays available like creating and claiming it
    let task_named = fields["task"].as_str().unwrap_or("").to_string();
    let (subjects, remedies) = match store.get(&task_named) {
        Some(t) => {
            let mut s = reliance_paths(p, &store, &task_named);
            s.extend(crate::verification::close_subjects(
                &t.data,
                &t.list("allowed_paths"),
            ));
            s.sort();
            s.dedup();
            (s, crate::orchestration::tasks::remedies_of(&t.data))
        }
        None => (vec![], vec![]),
    };
    let admission = crate::scheduler::admit(
        p,
        &crate::scheduler::Request::new(crate::scheduler::catalogue::ops::HANDOFF_CREATE)
            .with_subjects(&subjects)
            .with_remedies(&remedies),
    )?;
    let id = store.next_id("handoff");
    let o = fields
        .as_object_mut()
        .ok_or_else(|| GovError::new("USAGE", "handoff fields must be an object"))?;
    let to_role = o
        .get("to_role")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let roles = read_yaml(
        &crate::kernel_trust::trusted_root(p)
            .join("roles")
            .join("ROLES.yaml"),
    )
    .unwrap_or(json!({}));
    let known: Vec<String> = roles["roles"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|r| r["id"].as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    if !known.contains(&to_role) {
        return Err(GovError::new(
            "UNKNOWN_ROLE",
            format!("to_role '{to_role}' is not a kernel role"),
        ));
    }
    if to_role == "orchestrator"
        && !o
            .get("explicit_orchestrator_assignment")
            .and_then(|v| v.as_bool())
            .unwrap_or(false)
    {
        return Err(GovError::new("INV_014", "a spawned worker must not be handed the orchestrator role unless explicitly assigned (explicit_orchestrator_assignment: true)"));
    }
    let task = o
        .get("task")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let t = store
        .get(&task)
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("task {task} not found")))?;
    // BC-P2-05 / W9: input continuity is enforced before anything is handed off
    let (freshness, degraded) = handoff_freshness(p, &task)?;
    let auth = o.entry("authority").or_insert(json!({}));
    if auth.get("allowed").is_none() {
        auth["allowed"] = json!(t.list("allowed_paths"));
    }
    if auth.get("prohibited").is_none() {
        let mut f = t.list("forbidden_paths");
        if !f.iter().any(|x| x == "governance/kernel/**") {
            f.push("governance/kernel/**".into());
        }
        auth["prohibited"] = json!(f);
    }
    o.entry("from_role").or_insert(json!(p.role));
    o.entry("inputs").or_insert(
        json!({"task": task, "context_packet": format!(".governance-runtime/context/{task}.json")}),
    );
    if let Some(i) = o.get_mut("inputs").and_then(|v| v.as_object_mut()) {
        i.insert(
            "context_packet_hash".into(),
            freshness["packet_hash"].clone(),
        );
    }
    o.insert("freshness".into(), freshness.clone());
    o.insert("degraded".into(), json!(degraded));
    // G3 (tier contract): continuity checks at the handoff boundary, recorded (the G0 guard above is what refuses)
    let health = match crate::scheduler::tier_run(
        p,
        crate::scheduler::Tier::G3,
        crate::scheduler::Trigger::new(crate::scheduler::catalogue::ops::HANDOFF_CREATE)
            .with_subject(&task),
    ) {
        Ok(h) => {
            json!({"tier": "G3", "verdict": h["verdict"], "health_result": h["health_result"], "counts": h["counts"]})
        }
        Err(e) => json!({"tier": "G3", "error": {"code": e.code, "message": e.message}}),
    };
    o.insert("health".into(), health);
    o.entry("expected_outputs")
        .or_insert(json!(["implementation", "evidence"]));
    o.entry("required_return").or_insert(json!([
        "changed_files",
        "tests",
        "discoveries",
        "unresolved"
    ]));
    o.insert("handoff_status".into(), json!("OPEN"));
    o.insert("state_class".into(), json!("DERIVED"));
    let mut rec = new_record(
        "handoff",
        &id,
        &format!(
            "Handoff {} → {} for {task}",
            o["from_role"].as_str().unwrap_or(""),
            to_role
        ),
        Value::Object(o.clone()),
    );
    p.schemas()
        .validate("handoff", &rec.data, &format!("({id})"))?;
    // CHECKPOINT_POLICY mandatory trigger `before_handoff`
    if p.policies()
        .get_list("CHECKPOINT_POLICY", "mandatory_triggers")
        .iter()
        .any(|t| t == "before_handoff")
    {
        let db = crate::memory::db::RuntimeDb::open(&p.db_path())?;
        db.init_schema()?;
        crate::checkpoints::create(
            p,
            &db,
            json!({"trigger": "before_handoff", "task": task, "next_action": format!("worker {} executes {task} via {id}", to_role), "last_completed_step": format!("handoff {id} prepared"),
                "handoff_freshness": {"handoff": id, "state": freshness["state"], "stale_inputs_redelivered": freshness["stale_inputs"], "previous_packet_hash": freshness["previous_packet_hash"], "packet_hash": freshness["packet_hash"], "degraded": degraded}}),
        )?;
    }
    // T2 (round 3, O-7): the handoff record is OS-written continuity state (what was handed over, under which
    // freshness and authority); it is sealed as written by this operation, so a later edit is observable
    let binding = match crate::t2::seal_record(&mut rec, "handoff create") {
        Ok(()) => json!({"sealed": true}),
        Err(e) => {
            json!({"sealed": false, "code": e.code, "message": e.message, "consequence": "written unsealed: its edits cannot be told apart from the OS's writes on this machine"})
        }
    };
    save_record(&p.root, &rec)?;
    let mut out = rec.data.clone();
    out["stale_inputs"] = freshness["stale_inputs"].clone();
    out["record_binding"] = binding;
    if admission.is_remedy() {
        out["availability"] = json!({
            "rule": "a hard-block does not refuse the handoff of work that remedies it (availability rule, P2-HO-0031): the task declares the blocking check among its remedies and its subjects reach the block's; its close commits only once the block is cleared",
            "remedies": remedies, "remedied_blocks": admission.remedy_for});
    }
    Ok(out)
}

pub fn return_result(p: &Project, id: &str, ret: Value) -> Result<Value> {
    control::guard_write(p, "handoff return")?;
    crate::authority::require(p, "return_handoff")?;
    p.schemas()
        .validate("worker-return", &ret, "(worker return contract)")?;
    let mut store = RecordStore::load(&p.root);
    // The worker's return is the consumption receipt (Contract v3 W5; `context::receipt`). It is validated against
    // the task's manifest here and the verdict is recorded on the handoff, so the orchestrator sees missing or
    // fabricated traceability when the work comes back; refusal is task close's (WS-5 integration point).
    let receipt_validation = store
        .get(id)
        .map(|h| h.get("task"))
        .filter(|t| !t.is_empty())
        .and_then(|t| crate::context::receipt::validate(p, &store, &t, &ret).ok())
        .map(|c| {
            let mut s = c.summary();
            s["errors_detail"] = json!(c.errors);
            s
        });
    let h = store
        .get_mut(id)
        .ok_or_else(|| GovError::new("HANDOFF_NOT_FOUND", format!("{id} not found")))?;
    if h.rtype() != "handoff" {
        return Err(GovError::new(
            "HANDOFF_NOT_FOUND",
            format!("{id} is not a handoff"),
        ));
    }
    // O-7: the return is the handoff's own operation; it re-seals the record only when the seal verified before
    let was_verified = crate::cit::binding::verified_before(h);
    let allowed = h.data["authority"]["allowed"]
        .as_array()
        .cloned()
        .unwrap_or_default();
    let prohibited = h.data["authority"]["prohibited"]
        .as_array()
        .cloned()
        .unwrap_or_default();
    let mut violations = vec![];
    for f in ret["files_changed"].as_array().cloned().unwrap_or_default() {
        let f = f.as_str().unwrap_or("").to_string();
        if prohibited
            .iter()
            .any(|pat| crate::util::glob_match(pat.as_str().unwrap_or(""), &f))
        {
            violations.push(format!("{f}: prohibited path"));
        } else if !allowed.is_empty()
            && !allowed
                .iter()
                .any(|pat| crate::util::glob_match(pat.as_str().unwrap_or(""), &f))
        {
            violations.push(format!("{f}: outside allowed paths"));
        }
    }
    h.set("return", ret.clone());
    h.set("returned_at", json!(now_iso()));
    h.set("handoff_status", json!("RETURNED"));
    if let Some(rv) = &receipt_validation {
        h.set("receipt_validation", rv.clone());
    }
    if !violations.is_empty() {
        h.set("authority_violations", json!(violations));
    }
    let task_id = h.get("task");
    crate::cit::binding::reseal_if_verified(h, was_verified, true, "handoff return")?;
    save_record(&p.root, h)?;
    if !violations.is_empty() {
        return Err(GovError::new(
            "MUTATION_SCOPE_VIOLATION",
            format!(
                "worker changed files outside its authority: {}",
                violations.join("; ")
            ),
        )
        .with_details(json!({"violations": violations})));
    }
    // lessons in the return contract become PROVISIONAL lesson candidates (framework §67); never authority
    let mut created = vec![];
    let mut s2 = RecordStore::load(&p.root);
    for l in ret["lessons"].as_array().cloned().unwrap_or_default() {
        let text = l
            .as_str()
            .map(|s| s.to_string())
            .or_else(|| {
                l.get("text")
                    .and_then(|t| t.as_str())
                    .map(|s| s.to_string())
            })
            .unwrap_or_default();
        if text.trim().is_empty() {
            continue;
        }
        let lid = s2.next_id("lesson");
        let rec = new_record(
            "lesson",
            &lid,
            &text.chars().take(90).collect::<String>(),
            json!({"status": "PROVISIONAL", "state_class": "EVIDENCE", "scope": "PROJECT", "lifecycle": "candidate", "category": "worker-return", "problem_statement": text, "evidence_strength": "low", "sources": [id, task_id], "provenance": {"from_handoff": id, "task": task_id, "at": now_iso()}}),
        );
        save_record(&p.root, &rec)?;
        s2.records.push(rec.clone());
        created.push(lid);
    }
    Ok(
        json!({"handoff": id, "status": "RETURNED", "files_changed": ret["files_changed"], "unresolved": ret["unresolved"], "lessons_created": created, "receipt_validation": receipt_validation}),
    )
}
