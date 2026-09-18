//! Context compiler (framework §15): deterministic authority block (hash-stable) + retrieved intelligence block.
use crate::memory::db::RuntimeDb;
use crate::orchestration::control;
use crate::records::RecordStore;
use crate::retrieval::{retrieve, RetrieveOptions};
use crate::util::{hash_value, now_iso, sorted, write_json};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

fn brief(r: &crate::records::Record) -> Value {
    let mut v = json!({"id": r.id(), "type": r.rtype(), "title": r.title(), "status": r.status(), "path": r.path});
    for k in [
        "summary",
        "objective",
        "question",
        "chosen_option",
        "rationale",
        "kind",
        "acceptance_criteria",
        "given",
        "when",
        "then",
        "success_criteria",
        "failure_criteria",
        "contract",
        "readiness",
        "class",
    ] {
        if let Some(x) = r.data.get(k) {
            v[k] = x.clone();
        }
    }
    v
}

pub fn compile(p: &Project, db: &RuntimeDb, task_id: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let task = store
        .get(task_id)
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("task {task_id} not found")))?;
    if task.rtype() != "task" {
        return Err(GovError::new("USAGE", format!("{task_id} is not a task")));
    }
    let pol = p.policies();
    let feature_id = task.get("feature");
    let feature = store.get(&feature_id).filter(|r| r.rtype() == "feature");
    let mut req_ids = task.list("requirements");
    if let Some(f) = feature {
        req_ids.extend(f.list("requirements"));
    }
    let mut dec_ids = task.list("decisions");
    for d in store.active("decision") {
        if d.list("affects").contains(&feature_id)
            || d.list("affects").contains(&task_id.to_string())
            || (!feature_id.is_empty() && d.list("governed_by").contains(&feature_id))
        {
            dec_ids.push(d.id());
        }
    }
    dec_ids.sort();
    dec_ids.dedup();
    // authority precedence (framework §2/§21): a superseded-but-ACTIVE decision is UNKNOWN_OR_CONFLICTING, never authority
    let superseded_by_map: std::collections::BTreeMap<String, String> = store
        .records
        .iter()
        .flat_map(|r| r.list("supersedes").into_iter().map(move |s| (s, r.id())))
        .collect();
    let mut active_decisions: Vec<Value> = vec![];
    let mut conflicting: Vec<Value> = vec![];
    for id in &dec_ids {
        let Some(r) = store.get(id) else { continue };
        if r.rtype() != "decision" {
            continue;
        }
        let mut b = brief(r);
        let sup = superseded_by_map.get(id).cloned().or_else(|| {
            let s = r.get("superseded_by");
            if s.is_empty() {
                None
            } else {
                Some(s)
            }
        });
        if let Some(by) = sup {
            b["authority_flag"] = json!("UNKNOWN_OR_CONFLICTING");
            b["superseded_by"] = json!(by);
            b["reason"] = json!("superseded by a later decision but still marked ACTIVE; resolve via CIT before relying on it");
            conflicting.push(b);
        } else if r.status() == "ACTIVE" || r.status() == "PROVISIONAL" {
            active_decisions.push(b);
        }
    }
    let invariants = crate::util::read_yaml(
        &p.kernel_dir()
            .join("constitution")
            .join("HARD_INVARIANTS.yaml"),
    )
    .ok()
    .and_then(|v| v["invariants"].as_array().cloned())
    .unwrap_or_default();
    let pp = p.project_policy();
    let authority_layers = json!([
        {"layer": 1, "name": "constitution_hard_invariants", "items": invariants.iter().map(|i| json!({"id": i["id"], "statement": i["statement"]})).collect::<Vec<_>>()},
        {"layer": 2, "name": "security_authority", "kernel_trust": pol.kernel_trust.clone(), "precedence": pol.get_list("AUTHORITY_POLICY", "precedence"), "never_index_classes": pol.get_list("SECURITY_POLICY", "never_index_classes"), "never_export_classes": pol.get_list("SECURITY_POLICY", "never_export_classes"), "acting_role": p.role, "authority_level": crate::authority::level_of(p, &p.role).map(|l| format!("L{l}")).unwrap_or("unknown".into())},
        {"layer": 3, "name": "project_policy", "project": pp.get("project"), "policy_overrides": pol.applied_overrides.len(), "policy_overrides_applied": pol.applied_overrides.iter().map(|o| json!({"policy": o["policy"], "key": o["key"], "mode": o["mode"], "source": o["source"]})).collect::<Vec<_>>(), "policy_overrides_refused": pol.refused_overrides.iter().map(|o| json!({"policy": o["policy"], "key": o["key"], "reason": o["reason"]})).collect::<Vec<_>>(), "precedence": pol.precedence.clone(), "readiness_enforced": pp["readiness"]["enforce_pre_implementation_cells"], "staleness": pp.get("staleness")},
        {"layer": 4, "name": "active_decisions_and_spec"}, {"layer": 5, "name": "task_contract_and_mutation_manifest"}, {"layer": 6, "name": "role_and_skill"}, {"layer": 7, "name": "retrieved_context"}, {"layer": 8, "name": "model_inference"}
    ]);
    let mut scn_ids = task.list("scenarios");
    if let Some(f) = feature {
        scn_ids.extend(f.list("scenarios"));
    }
    scn_ids.sort();
    scn_ids.dedup();
    let mut iface_ids = vec![];
    if let Some(f) = feature {
        iface_ids.extend(f.list("interfaces"));
    }
    let mut acceptance: Vec<Value> = vec![];
    for s in &scn_ids {
        if let Some(r) = store.get(s) {
            for c in r.list("success_criteria") {
                acceptance.push(json!({"scenario": s, "criterion": c}));
            }
            for c in r.list("then") {
                acceptance.push(json!({"scenario": s, "then": c}));
            }
        }
    }
    for t in task.list("acceptance_tests") {
        acceptance.push(json!({"test": t}));
    }
    let collect = |ids: &[String], want: &str| -> Vec<Value> {
        ids.iter()
            .filter_map(|i| store.get(i))
            .filter(|r| want.is_empty() || r.rtype() == want)
            .map(brief)
            .collect()
    };
    let mut prohibited = task.list("forbidden_paths");
    prohibited.push("governance/kernel/**".into());
    for r in &p.contract().rules {
        if r.get("mutation").and_then(|m| m.as_str()) == Some("prohibited") {
            if let Some(pat) = r.get("pattern").and_then(|x| x.as_str()) {
                prohibited.push(pat.to_string());
            }
        }
    }
    prohibited.sort();
    prohibited.dedup();
    let dependency_state: Vec<Value> = task.list("dependencies").iter().map(|d| json!({"id": d, "task_status": store.get(d).map(|r| r.get("task_status")).unwrap_or("MISSING".into())})).collect();
    let skills: Vec<Value> = task.list("required_skills").iter().map(|s| { let sk = crate::skills::find_skill(p, s); json!({"id": s, "version": sk.as_ref().map(|k| k["version"].clone()).unwrap_or(Value::Null), "resolved": sk.is_some()}) }).collect();
    let ctl = control::state(p);
    let mut status_counts = serde_json::Map::new();
    for t in store.of_type("task") {
        let s = t.get("task_status");
        *status_counts.entry(s).or_insert(json!(0)) = json!(
            status_counts
                .get(&t.get("task_status"))
                .and_then(|v| v.as_i64())
                .unwrap_or(0)
                + 1
        );
    }
    let pending_gates: Vec<String> = store
        .of_type("human-gate")
        .into_iter()
        .filter(|g| matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED"))
        .map(|g| g.id())
        .collect();
    let det = json!({
        "task": brief(task), "objective": task.get("objective"),
        // `OWNER-DECISION-0006` §6 bullet 7 (`AR31-B1`): `framework_version` is what the LOCK says is installed;
        // `release_trust.below_floor` is whether this machine is marked `DEGRADED — RECOVERY ONLY` and is
        // therefore running beneath its signed security floor. This packet is the deterministic authority block
        // every kernel role reads, and it used to carry the version with no marking, so every agent consuming it
        // treated the below-floor release as the current one. The two are different predicates and are never
        // merged (frozen R0 item 11). The block is read at the one §6 bullet 7 sink, `crate::srr::present`, which
        // asks `breakglass::guard_effect` and reports the refusal rather than swallowing it.
        "project_state": {"framework_version": p.framework_version(), "release_trust": crate::srr::present::presentation("context packet"), "task_status_counts": status_counts, "pending_human_gates": pending_gates, "control": ctl.get("mode"), "projects": store.of_type("project").iter().map(|r| brief(r)).collect::<Vec<_>>()},
        "authority_layers": authority_layers, "hard_invariants": invariants.iter().map(|i| i["id"].clone()).collect::<Vec<_>>(),
        "feature": feature.map(brief), "governing_requirements": collect(&req_ids, "requirement"), "active_decisions": active_decisions, "conflicting_decisions": conflicting,
        "architecture": store.active("architecture").iter().map(|r| brief(r)).collect::<Vec<_>>(), "interfaces": collect(&iface_ids, "interface"), "scenarios": collect(&scn_ids, "scenario"),
        "acceptance_criteria": acceptance, "allowed_writes": task.list("allowed_paths"), "prohibited_writes": prohibited, "required_skills": skills, "required_tools": task.list("required_tools"),
        "dependency_state": dependency_state, "minimum_model_tier": task.get("minimum_model_tier"), "minimum_reasoning": task.get("minimum_reasoning"),
    });
    let det = sorted(&det);
    let det_hash = hash_value(&det);
    let query = format!("{} {}", task.title(), task.get("objective"));
    let k = pol.get_i64("CONTEXT_POLICY", "max_retrieved_slices", 12) as usize;
    let res = retrieve(
        p,
        db,
        &query,
        RetrieveOptions {
            k,
            log: true,
            ..Default::default()
        },
    )?;
    let lessons = retrieve(
        p,
        db,
        &query,
        RetrieveOptions {
            k: 5,
            record_types: vec!["lesson".into(), "report".into()],
            ..Default::default()
        },
    )?;
    let mut code_refs = vec![];
    for tok in crate::memory::embeddings::tokenize(&query)
        .into_iter()
        .filter(|t| t.len() > 3)
        .take(12)
    {
        for r in db.query(
            "SELECT path, qualname, kind FROM symbols WHERE name=?1 LIMIT 3",
            &[&tok],
        )? {
            code_refs.push(r);
        }
    }
    let ret = json!({"query": query, "retrieval_strategy": res.strategy, "routes": res.routes, "index_snapshot": {"index_version": res.index_version, "manifest_hash": res.index_manifest_hash},
        "ranked_evidence": res.hits.iter().map(|h| json!({"artifact_id": h.artifact_id, "path": h.path, "section": h.section, "score": h.score, "routes": h.routes, "status": h.status, "state_class": h.state_class, "excerpt": h.excerpt, "parent_excerpt": h.parent_excerpt, "neighbours": h.neighbours, "flags": h.flags})).collect::<Vec<_>>(),
        "lessons_failures": lessons.hits.iter().map(|h| json!({"artifact_id": h.artifact_id, "path": h.path, "excerpt": h.excerpt})).collect::<Vec<_>>(), "code_references": code_refs});
    let mut ret = ret;
    // CONTEXT_POLICY.max_packet_chars: bound the packet deterministically by dropping retrieved slices from the tail
    let max = pol.get_i64("CONTEXT_POLICY", "max_packet_chars", 60000) as usize;
    let det_len = serde_json::to_string(&det)?.len();
    let mut truncated = 0usize;
    loop {
        let total = det_len + serde_json::to_string(&ret)?.len() + 400;
        if total <= max {
            break;
        }
        let mut dropped = false;
        for key in ["code_references", "lessons_failures", "ranked_evidence"] {
            if let Some(a) = ret[key].as_array_mut() {
                if !a.is_empty() {
                    a.pop();
                    dropped = true;
                    truncated += 1;
                    break;
                }
            }
        }
        if !dropped {
            break;
        }
    }
    if truncated > 0 {
        ret["truncated_slices"] = json!(truncated);
    }
    let mut packet = json!({"packet_id": format!("CTX-{}-{}", task_id, &det_hash[..8]), "task": task_id, "deterministic_authority": det, "deterministic_hash": det_hash, "retrieved_intelligence": ret, "index_version": crate::INDEX_VERSION});
    let ph = hash_value(
        &json!({"d": packet["deterministic_authority"], "r": packet["retrieved_intelligence"]}),
    );
    packet["packet_hash"] = Value::String(ph);
    packet["compiled_at"] = Value::String(now_iso());
    let chars = serde_json::to_string(&packet)?.len();
    packet["chars"] = json!(chars);
    if chars > max {
        packet["warning"] = json!(format!("deterministic authority block alone exceeds CONTEXT_POLICY.max_packet_chars ({chars} > {max}); split the task"));
    }
    write_json(
        &p.runtime_dir()
            .join("context")
            .join(format!("{task_id}.json")),
        &packet,
    )?;
    Ok(packet)
}
