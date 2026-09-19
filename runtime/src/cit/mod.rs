//! Change-Impact Transactions (framework §47-49): CIT-P simulation before approval, CIT-E atomic execution with
//! snapshot, propagation, derived-view regeneration, index refresh, verification and commit-or-rollback.
//!
//! ## Repair iteration 1, round 2 (WS-4)
//!
//! * **Materiality is derived, not labelled (BC-P2-13, CIT-P side).** [`materiality`] classifies what a manifest
//!   changes into the eight Contract v3:640-647 classes; propose and simulate use the union of the proposer's label and
//!   the derived classes for automatic simulation, radius and human-gate requirement. A material change labelled
//!   `editorial` is simulated at its class's radius and gated as its class requires.
//! * **An approval binds the transaction, its impact and the CIT (BC-P2-11, CIT side).** Every CIT operation seals
//!   the transaction's state ([`binding`]); the gate the OS raises carries `subject.sha256` = the digest of this CIT's
//!   content and simulated impact, which is inside the package the owner signs. Approve and execute read the answer
//!   only through `gates::verified_answer` and refuse, typed, when the content, the impact, the gate reference, the
//!   approval or the sealed status no longer match (`APPROVAL_STALE`, `GATE_MISMATCH`, `T2_UNBOUND`). A re-simulation
//!   that changes the content or impact needs a new gate.
//! * **CIT gates are system gates** (`gates::create_system`): the OS computed the assessment they carry.
//! * **Propagation reaches completed work (BC-P2-04).** CIT-E propagates through [`propagation`]: open and completed
//!   dependents, their evidence, validation evidence, checkpoints, handoffs and packets, with revalidation tasks for
//!   completed work — inside the transaction (the snapshot covers it; a rollback undoes it).
//! * **Tier contract.** Propose/approve/execute pass `scheduler::guard` (G0); execute runs `scheduler::tier_run(G4)`
//!   after commit and records the result.
//! * **What an execution wrote is recorded per path** (`execution.writes`, sealed): [`binding::verified_writes`] is the
//!   API task close uses to accept an out-of-scope path only when its content is what an in-window CIT wrote.
pub mod binding;
pub mod materiality;
pub mod propagation;

use crate::graph;
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::orchestration::{control, gates};
use crate::records::{new_record, parse_record_text, save_record, Record, RecordStore};
use crate::retrieval::{retrieve, RetrieveOptions};
use crate::scheduler::{catalogue::ops, Tier, Trigger};
use crate::util::{
    copy_dir, glob_match, now_iso, read_json, read_text, today, write_json, write_text,
};
use crate::{GovError, Project, Result};
use binding::CitState;
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

const RADII: &[&str] = &["R0", "R1", "R2", "R3", "R4", "R5"];
fn radius_rank(r: &str) -> usize {
    RADII.iter().position(|x| *x == r).unwrap_or(1)
}

/// Redact secret patterns inside every string of a JSON value; returns the number of redactions.
fn redact_value(p: &Project, v: &mut Value, field: &str, hits: &mut Vec<String>) {
    match v {
        Value::String(s) => {
            let found = p.secret_scanner().scan_text(s, field);
            if !found.is_empty() {
                for h in &found {
                    hits.push(format!("{}: {}", field, h.pattern_id));
                }
                let mut out = s.clone();
                for (_, rx) in &p.secret_scanner().patterns {
                    out = rx.replace_all(&out, "[REDACTED]").to_string();
                }
                *s = out;
            }
        }
        Value::Array(a) => {
            for (i, x) in a.iter_mut().enumerate() {
                redact_value(p, x, &format!("{field}[{i}]"), hits);
            }
        }
        Value::Object(o) => {
            for (k, x) in o.iter_mut() {
                redact_value(p, x, &format!("{field}.{k}"), hits);
            }
        }
        _ => {}
    }
}

/// Repository paths a transaction names (for the G0 guard's path-scoped hard-blocks): manifest paths and the files
/// of the records it targets.
fn guard_paths(store: &RecordStore, cit: &Value) -> Vec<String> {
    let mut v: Vec<String> = vec![];
    for x in manifest_paths(cit) {
        match store.get(&x) {
            Some(r) => v.push(r.path.clone()),
            None => v.push(x),
        }
    }
    for t in cit["targets"].as_array().cloned().unwrap_or_default() {
        if let Some(r) = t.as_str().and_then(|id| store.get(id)) {
            v.push(r.path.clone());
        }
    }
    v.sort();
    v.dedup();
    v
}

pub fn propose(p: &Project, mut fields: Value) -> Result<Value> {
    control::guard_write(p, "cit propose")?;
    crate::authority::require(p, "propose_cit")?;
    let store = RecordStore::load(&p.root);
    let id = store.next_id("cit");
    let o = fields
        .as_object_mut()
        .ok_or_else(|| GovError::new("USAGE", "cit fields must be an object"))?;
    if o.get("proposal")
        .and_then(|v| v.as_str())
        .map(|s| s.is_empty())
        .unwrap_or(true)
    {
        return Err(GovError::new("USAGE", "proposal text required"));
    }
    // fields only the OS writes (BC-P2-09/-11): a proposer cannot pre-load an impact, approval, gate or sealed state
    for k in [
        "impact",
        "approval",
        "execution",
        "human_gate",
        "decision",
        "materiality",
        binding::STATE_FIELD,
        crate::t2::SEAL_FIELD,
        "auto_simulated",
        "cit_status",
    ] {
        o.remove(k);
    }
    // SECURITY: a proposal/manifest is a governed record; secret material is redacted before it is persisted and the
    // transaction is flagged so that it can never be executed with that content (verifier M9 / HV-34, HV-17).
    let mut secret_hits: Vec<String> = vec![];
    {
        let mut tmp = Value::Object(o.clone());
        redact_value(p, &mut tmp, "cit", &mut secret_hits);
        if let Value::Object(m) = tmp {
            *o = m;
        }
    }
    if !secret_hits.is_empty() {
        o.insert("secret_flagged".into(), json!(true));
        o.insert(
            "blocked_reasons".into(),
            json!(secret_hits
                .iter()
                .map(|h| format!("secret pattern redacted from {h}"))
                .collect::<Vec<_>>()),
        );
    }
    o.insert("cit_status".into(), json!("PROPOSED"));
    o.entry("proposed_by").or_insert(json!(p.role));
    o.entry("trigger").or_insert(json!("behaviour_change"));
    o.entry("targets").or_insert(json!([]));
    o.entry("mutation_manifest").or_insert(json!([]));
    o.insert(
        "journal".into(),
        json!([{"at": now_iso(), "event": "proposed", "session": p.session_id}]),
    );
    o.insert("state_class".into(), json!("AUTHORITATIVE"));
    let title = o
        .get("title")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string())
        .unwrap_or_else(|| {
            o["proposal"]
                .as_str()
                .unwrap_or("")
                .chars()
                .take(80)
                .collect()
        });
    o.remove("title");
    let mut rec = new_record("cit", &id, &title, Value::Object(o.clone()));
    // an appended record that violates its schema can never execute: refuse it now (as the op enum is), not after
    // a human has been asked to approve it
    for (i, op) in rec.data["mutation_manifest"]
        .as_array()
        .cloned()
        .unwrap_or_default()
        .iter()
        .enumerate()
    {
        if op["op"] != "append_record" {
            continue;
        }
        let r = &op["record"];
        let t = r["type"].as_str().unwrap_or("");
        if t.is_empty() || r["id"].as_str().unwrap_or("").is_empty() {
            return Err(GovError::new(
                "USAGE",
                format!("mutation_manifest[{i}]: append_record requires record.id and record.type"),
            ));
        }
        let schema = if p.schemas().has(t) { t } else { "record" };
        p.schemas().validate(
            schema,
            r,
            &format!("(mutation_manifest[{i}] of {id}: appended {t})"),
        )?;
    }
    // G0 (tier contract, IP-WS02-05): an active hard-block governing these paths refuses the proposal
    crate::scheduler::guard(p, ops::CIT_PROPOSE, &guard_paths(&store, &rec.data))?;
    // BC-P2-13: materiality from what the manifest changes, not only from the declared label
    let declared = rec.get("trigger");
    let mat = materiality::classify_manifest(p, &store, &rec.data);
    rec.set("materiality", mat.to_value(&declared));
    p.schemas().validate("cit", &rec.data, &format!("({id})"))?;
    let content = binding::content_digest(&rec.data);
    binding::seal(
        &mut rec,
        CitState {
            cit_status: "PROPOSED".into(),
            content_sha256: content,
            ..Default::default()
        },
        "cit propose",
    )?;
    save_record(&p.root, &rec)?;
    // CHANGE_POLICY.auto_simulate_triggers: CIT-P is automatic above the impact threshold (framework §48) — judged on
    // the effective triggers (declared ∪ derived), so a material change cannot skip simulation by its label
    let auto = p
        .policies()
        .get_list("CHANGE_POLICY", "auto_simulate_triggers");
    let effective = mat.effective_triggers(&declared);
    let wants_sim = auto.contains(&declared) || effective.iter().any(|t| auto.contains(t));
    if wants_sim && p.db_path().exists() {
        let db = RuntimeDb::open(&p.db_path())?;
        if db.has_schema() {
            let sim = simulate_inner(p, &db, &id)?;
            let mut data = RecordStore::load(&p.root)
                .get(&id)
                .map(|r| r.data.clone())
                .unwrap_or(rec.data.clone());
            data["auto_simulated"] = json!(true);
            data["simulation"] = sim;
            return Ok(data);
        }
    }
    Ok(rec.data)
}

fn manifest_paths(cit: &Value) -> Vec<String> {
    let mut v = vec![];
    for op in cit["mutation_manifest"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        for k in ["path", "to"] {
            if let Some(s) = op[k].as_str() {
                v.push(s.to_string());
            }
        }
        if let Some(t) = op["target"].as_str() {
            v.push(t.to_string());
        }
        if let Some(r) = op["record"].as_object() {
            if let Some(id) = r.get("id").and_then(|x| x.as_str()) {
                v.push(id.to_string());
            }
        }
    }
    v
}

fn seeds_for(p: &Project, db: &RuntimeDb, cit: &Value) -> Result<Vec<String>> {
    let mut seeds: Vec<String> = cit["targets"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    for pth in manifest_paths(cit) {
        if let Some(a) = db.artifact_by_path(&pth)? {
            seeds.push(a["artifact_id"].as_str().unwrap_or("").to_string());
        } else if db.artifact(&pth)?.is_some() {
            seeds.push(pth);
        } else if p.root.join(&pth).exists() {
            seeds.push(format!("file:{pth}"));
        }
    }
    seeds.sort();
    seeds.dedup();
    Ok(seeds)
}

/// Impact radius (framework §49) from the **effective** triggers (declared ∪ derived material classes), governance
/// paths, and the reach of the affected set (cross-feature / cross-module escalation).
fn estimate_radius(
    p: &Project,
    cit: &Value,
    effective: &[String],
    affected: &[graph::Reach],
    db: &RuntimeDb,
) -> Result<String> {
    let pol = p.policies();
    let trigger = cit["trigger"].as_str().unwrap_or("");
    let paths = manifest_paths(cit);
    let mut r = if paths.iter().any(|x| glob_match("governance/**", x)) {
        pol.get_str(
            "CHANGE_POLICY",
            "radius_rules.governance_paths_radius",
            "R5",
        )
    } else if !effective.is_empty() {
        effective
            .iter()
            .map(|c| materiality::radius_floor(p, c))
            .max_by_key(|r| radius_rank(r))
            .unwrap_or_else(|| "R1".into())
    } else if trigger == "editorial" {
        pol.get_str("CHANGE_POLICY", "radius_rules.editorial_radius", "R0")
    } else {
        pol.get_str("CHANGE_POLICY", "radius_rules.single_artifact_radius", "R1")
    };
    let mut features = std::collections::BTreeSet::new();
    let mut modules = std::collections::BTreeSet::new();
    for a in affected {
        if let Some(art) = db.artifact(&a.node)? {
            let rt = art["record_type"].as_str().unwrap_or("");
            if rt == "feature" {
                features.insert(a.node.clone());
            }
            if rt == "file" {
                let path = art["path"].as_str().unwrap_or("");
                if let Some(m) = Path::new(path).parent() {
                    modules.insert(m.to_string_lossy().to_string());
                }
            }
            if let Ok(d) = serde_json::from_str::<Value>(art["data_json"].as_str().unwrap_or("{}"))
            {
                if let Some(f) = d.get("feature").and_then(|v| v.as_str()) {
                    features.insert(f.to_string());
                }
            }
        }
    }
    let cf = pol.get_i64("CHANGE_POLICY", "radius_rules.cross_feature_threshold", 3) as usize;
    let cm = pol.get_i64("CHANGE_POLICY", "radius_rules.cross_module_threshold", 2) as usize;
    if features.len() >= cf && radius_rank(&r) < 4 {
        r = "R4".into();
    } else if modules.len() >= cm && radius_rank(&r) < 3 {
        r = "R3".into();
    }
    Ok(r)
}

/// CIT-P: deterministic graph traversal + bounded retrieval -> impact radius and human-readable consequences.
pub fn simulate(p: &Project, db: &RuntimeDb, id: &str) -> Result<Value> {
    control::guard_write(p, "cit simulate")?;
    crate::authority::require(p, "simulate_cit")?;
    simulate_inner(p, db, id)
}

fn load_cit(store: &RecordStore, id: &str) -> Result<Record> {
    store
        .get(id)
        .filter(|r| r.rtype() == "cit")
        .cloned()
        .ok_or_else(|| GovError::new("CIT_NOT_FOUND", format!("{id} not found")))
}

fn journal(r: &mut Record, ev: Value) {
    if let Some(j) = r.data["journal"].as_array_mut() {
        j.push(ev);
    } else {
        r.set("journal", json!([ev]));
    }
}

/// Gates the OS raised for CIT `id`, newest last.
fn gates_of(store: &RecordStore, id: &str) -> Vec<Record> {
    let mut v: Vec<Record> = store
        .of_type("human-gate")
        .into_iter()
        .filter(|g| g.get("cit") == id)
        .cloned()
        .collect();
    v.sort_by_key(|g| g.id());
    v
}

fn simulate_inner(p: &Project, db: &RuntimeDb, id: &str) -> Result<Value> {
    let pol = p.policies();
    let store = RecordStore::load(&p.root);
    let rec = load_cit(&store, id)?;
    if !matches!(rec.get("cit_status").as_str(), "PROPOSED" | "SIMULATED") {
        return Err(GovError::new(
            "USAGE",
            format!(
                "{id} is {}; only PROPOSED/SIMULATED transactions can be simulated",
                rec.get("cit_status")
            ),
        ));
    }
    // the transaction's state must be what gov wrote (BC-P2-09): a record written or edited outside gov is a request
    let st = binding::verified_state(&rec)?;
    if !matches!(
        st.cit_status.as_str(),
        "PROPOSED" | "SIMULATED" | "APPROVED"
    ) {
        return Err(GovError::new("CIT_STATE_MISMATCH", format!("{id} reads {} but gov last sealed it {}; a transaction gov finalised cannot be re-simulated — propose a new one", rec.get("cit_status"), st.cit_status)).with_details(json!({"sealed_status": st.cit_status, "record_status": rec.get("cit_status")})));
    }
    let content = binding::content_digest(&rec.data);
    let content_changed = content != st.content_sha256;
    // BC-P2-13: materiality recomputed from what the manifest changes now
    let declared = rec.get("trigger");
    let mat = materiality::classify_manifest(p, &store, &rec.data);
    let effective = mat.effective_triggers(&declared);
    let seeds = seeds_for(p, db, &rec.data)?;
    let mut radius = estimate_radius(p, &rec.data, &effective, &[], db)?;
    let mut affected = vec![];
    for _ in 0..2 {
        let depth = pol.get_i64(
            "CHANGE_POLICY",
            &format!("graph_traversal_depth_by_radius.{radius}"),
            2,
        ) as usize;
        affected = graph::impact_set(db, &seeds, depth.max(1))?;
        let r2 = estimate_radius(p, &rec.data, &effective, &affected, db)?;
        if radius_rank(&r2) <= radius_rank(&radius) {
            break;
        }
        radius = r2;
    }
    let k = pol.get_i64(
        "CHANGE_POLICY",
        &format!("semantic_candidates_by_radius.{radius}"),
        8,
    ) as usize;
    let candidates = if k > 0 {
        retrieve(p, db, rec.get("proposal").as_str(), RetrieveOptions { k, ..Default::default() })?.hits.into_iter().map(|h| json!({"artifact_id": h.artifact_id, "path": h.path, "score": h.score, "routes": h.routes})).collect::<Vec<_>>()
    } else {
        vec![]
    };
    let mut tasks = vec![];
    let mut tests = vec![];
    let mut features = vec![];
    let mut other = vec![];
    for a in &affected {
        let rt = db
            .artifact(&a.node)?
            .map(|x| x["record_type"].as_str().unwrap_or("").to_string())
            .unwrap_or_default();
        match rt.as_str() {
            "task" => tasks.push(a.node.clone()),
            "test-obligation" | "scenario" => tests.push(a.node.clone()),
            "feature" => features.push(a.node.clone()),
            "file" => {
                if db
                    .artifact(&a.node)?
                    .map(|x| x["path_class"].as_str() == Some("test"))
                    .unwrap_or(false)
                {
                    tests.push(a.node.clone());
                } else {
                    other.push(a.node.clone());
                }
            }
            _ => other.push(a.node.clone()),
        }
    }
    // completed work the change reaches (W6: COMPLETE does not imply permanently valid)
    let changed = changed_record_ids(p, &store, &rec.data);
    let pre = propagation::plan(p, &store, &changed, None, None);
    let human_triggers = pol.get_list("CHANGE_POLICY", "human_gate_triggers");
    let auto_max = pol.get_str("CHANGE_POLICY", "auto_approve_max_radius", "R1");
    let human_gate_required = radius_rank(&radius) > radius_rank(&auto_max)
        || human_triggers.contains(&declared)
        || effective.iter().any(|t| human_triggers.contains(t));
    let consequences = vec![
        format!("{} artefacts affected within radius {radius} (graph depth {})", affected.len(), pol.get_i64("CHANGE_POLICY", &format!("graph_traversal_depth_by_radius.{radius}"), 2)),
        format!("{} open task(s) will be marked retest-required", tasks.len().max(pre.open_tasks.len())),
        format!("{} completed task(s) will be marked for revalidation, with revalidation tasks generated", pre.done_tasks.len()),
        format!("{} test/scenario artefact(s) become stale and must be re-validated", tests.len().max(pre.tests.len())),
        format!("{} feature(s) readiness potentially impacted", features.len()),
        format!("material classes derived from what the manifest changes: {:?} (declared trigger '{declared}')", mat.classes()),
        if human_gate_required { "human approval required before execution".into() } else { "eligible for automatic approval under CHANGE_POLICY".into() },
        "rollback: snapshot of every touched file is taken before execution; `gov cit rollback` restores it".into(),
    ];
    let routing = crate::routing::route(p, None, Some("governance"), None, Some(&radius))?;
    let mut impact = json!({"radius": radius, "seeds": seeds, "affected": affected.iter().map(|a| json!({"node": a.node, "hop": a.hop, "via": a.via})).collect::<Vec<_>>(), "affected_tasks": tasks, "tests_required": tests, "features": features, "other": other,
        "completed_tasks_to_revalidate": pre.done_tasks.keys().cloned().collect::<Vec<_>>(),
        "material_classes": mat.classes(), "effective_triggers": effective,
        "semantic_candidates": candidates, "consequences": consequences, "human_gate_required": human_gate_required, "minimum_model_tier": routing["minimum_tier"], "simulated_at": now_iso(), "index_snapshot": db.get_meta("index_manifest_hash")});
    let impact_sha = binding::impact_digest(&impact);
    let bind = binding::binding_digest(id, &content, &impact_sha);
    impact["content_sha256"] = json!(content);
    impact["impact_sha256"] = json!(impact_sha);
    impact["binding_sha256"] = json!(bind);
    // a decline is final for this exact transaction and impact (verifier C-N1), whatever the record's status says
    for g in gates_of(&store, id) {
        if g.data["subject"]["sha256"].as_str() != Some(bind.as_str()) {
            continue;
        }
        if let Ok(a) = gates::verified_answer(p, &g.id()) {
            if !a.authorises_blocked_work {
                reject_sealed(p, id, &format!("gate {} declined this transaction", g.id()))?;
                return Err(GovError::new("GATE_DECLINED", format!("gate {} was answered '{}' for exactly this transaction and impact; a decline can never become approval", g.id(), a.option)).with_details(json!({"gate": g.id(), "answer": a.to_value()})));
            }
        }
    }
    // the gate the answer must come from: reused only when it was raised for exactly this content and impact
    let existing = st
        .human_gate
        .clone()
        .or_else(|| Some(rec.get("human_gate")).filter(|g| !g.is_empty()));
    let mut gate_id: Option<String> = None;
    let mut gate_note: Option<Value> = None;
    if human_gate_required {
        let reusable = existing.as_ref().and_then(|g| store.get(g)).filter(|g| {
            g.get("cit") == id
                && g.data["subject"]["sha256"].as_str() == Some(bind.as_str())
                && !matches!(g.get("gate_status").as_str(), "WITHDRAWN" | "EXPIRED")
        });
        if let Some(g) = reusable {
            gate_id = Some(g.id());
        } else {
            let g = gates::create_system(
                p,
                json!({"question": format!("Approve change {id}: {}", rec.get("proposal")),
                    "why_now": format!("CIT-P simulated impact radius {radius}; effective trigger(s) {effective:?} (declared '{declared}'); CHANGE_POLICY requires a human decision before execution"),
                    "current_state": "proposal simulated, not executed: nothing has been applied",
                    "options": [{"id": "A", "description": "approve and execute exactly this transaction (CIT-E)", "authorises_blocked_work": true}, {"id": "B", "description": "reject the transaction", "authorises_blocked_work": false}],
                    "impact": consequences.join("; "),
                    "reversibility": "reversible: a snapshot of every touched file is taken before execution and `gov cit rollback` restores it",
                    "cost_rework": format!("{} open task(s) retest, {} completed task(s) revalidated", tasks.len().max(pre.open_tasks.len()), pre.done_tasks.len()),
                    "recommendation": "A if the proposal matches product direction and the simulated impact is acceptable; B otherwise",
                    "confidence": 0.7,
                    "trigger": effective.first().cloned().unwrap_or_else(|| declared.clone()), "cit": id, "impact_radius": radius, "blocks_tasks": [],
                    "subject": {"kind": "cit-transaction", "cit": id, "sha256": bind, "content_sha256": content, "impact_sha256": impact_sha, "radius": radius, "effective_triggers": effective},
                    "title": format!("Approve {id} ({radius})")}),
            )?;
            gate_id = g["id"].as_str().map(String::from);
            if let Some(old) = &existing {
                gate_note = Some(
                    json!({"at": now_iso(), "event": "gate_superseded", "stale_gate": old, "gate": gate_id, "reason": "the stale gate was raised for another content or impact of this transaction; its answer cannot approve this one"}),
                );
            }
        }
    } else if let Some(old) = &existing {
        gate_note = Some(
            json!({"at": now_iso(), "event": "gate_detached", "stale_gate": old, "reason": "the re-simulated transaction does not require a human gate under CHANGE_POLICY"}),
        );
    }
    let mut store2 = RecordStore::load(&p.root);
    let r = store2
        .get_mut(id)
        .ok_or_else(|| GovError::new("CIT_NOT_FOUND", format!("{id} not found")))?;
    if content_changed {
        journal(
            r,
            json!({"at": now_iso(), "event": "content_changed_outside_gov", "sealed_content_sha256": st.content_sha256, "content_sha256": content,
            "note": "the transaction content differs from what gov last sealed; this simulation is of the content as it stands, and any earlier answer or approval does not bind it"}),
        );
    }
    r.set("impact", impact.clone());
    r.set("materiality", mat.to_value(&declared));
    r.set("cit_status", json!("SIMULATED"));
    r.set("updated", json!(today()));
    if r.data.get("approval").is_some() {
        r.data.as_object_mut().unwrap().remove("approval");
    }
    match &gate_id {
        Some(g) => r.set("human_gate", json!(g)),
        None => {
            r.data.as_object_mut().unwrap().remove("human_gate");
        }
    }
    if let Some(n) = gate_note {
        journal(r, n);
    }
    journal(
        r,
        json!({"at": now_iso(), "event": "simulated", "radius": impact["radius"], "binding_sha256": bind}),
    );
    binding::seal(
        r,
        CitState {
            cit_status: "SIMULATED".into(),
            content_sha256: content,
            impact_sha256: Some(impact_sha),
            binding_sha256: Some(bind),
            human_gate: gate_id.clone(),
            ..Default::default()
        },
        "cit simulate",
    )?;
    save_record(&p.root, r)?;
    Ok(
        json!({"cit": id, "impact": impact, "human_gate": gate_id.map(Value::String).unwrap_or(Value::Null), "materiality": mat.to_value(&declared)}),
    )
}

/// Mark `id` REJECTED with a sealed state (a decline is final for the transaction).
fn reject_sealed(p: &Project, id: &str, why: &str) -> Result<()> {
    let mut s = RecordStore::load(&p.root);
    if let Some(c) = s.get_mut(id) {
        let prev = binding::verified_state(c).ok();
        c.set("cit_status", json!("REJECTED"));
        if c.data.get("approval").is_some() {
            c.data.as_object_mut().unwrap().remove("approval");
        }
        journal(
            c,
            json!({"at": now_iso(), "event": "rejected", "reason": why}),
        );
        let content = binding::content_digest(&c.data);
        binding::seal(
            c,
            CitState {
                cit_status: "REJECTED".into(),
                content_sha256: content,
                impact_sha256: prev.as_ref().and_then(|s| s.impact_sha256.clone()),
                binding_sha256: prev.as_ref().and_then(|s| s.binding_sha256.clone()),
                human_gate: prev.as_ref().and_then(|s| s.human_gate.clone()),
                ..Default::default()
            },
            "cit reject",
        )?;
        save_record(&p.root, c)?;
    }
    Ok(())
}

/// The honoured answer of the gate that governs CIT `id` (read only through `gates::verified_answer`), checked
/// against the transaction and impact the sealed state binds. Every refusal is typed.
fn gate_answer_for(
    p: &Project,
    store: &RecordStore,
    id: &str,
    gate_id: &str,
    binding_sha256: Option<&str>,
) -> Result<gates::VerifiedAnswer> {
    let g = store.get(gate_id).ok_or_else(|| {
        GovError::new(
            "GATE_NOT_FOUND",
            format!("human gate {gate_id} referenced by {id} does not exist"),
        )
    })?;
    if g.rtype() != "human-gate" {
        return Err(GovError::new(
            "GATE_MISMATCH",
            format!("{gate_id} is not a human gate"),
        ));
    }
    if g.get("cit") != id {
        return Err(GovError::new("GATE_MISMATCH", format!("gate {gate_id} belongs to '{}' not {id}; a gate answer approves exactly the transaction it was raised for", g.get("cit"))));
    }
    let presented = g
        .data
        .get("presented_in_chat")
        .and_then(|v| v.as_bool())
        .unwrap_or(false);
    let a = match gates::verified_answer(p, gate_id) {
        Ok(a) => a,
        Err(e) if e.code == "GATE_NOT_ANSWERED" && !presented => {
            return Err(GovError::new("GATE_NOT_PRESENTED", format!("human gate {gate_id} was never presented to the human (INV-008); run `gov gate present {gate_id}` and obtain the owner's answer")));
        }
        Err(e) if e.code == "GATE_NOT_ANSWERED" => {
            return Err(GovError::new("GATE_NOT_ANSWERED", format!("human gate {gate_id} is PRESENTED but has no recorded answer: presentation is not approval (INV-008)")));
        }
        Err(e) => return Err(e),
    };
    if a.record.get("cit") != id {
        return Err(GovError::new(
            "GATE_MISMATCH",
            format!("gate {gate_id} does not belong to {id}"),
        ));
    }
    let bound = a.record.data["subject"]["sha256"]
        .as_str()
        .unwrap_or("")
        .to_string();
    if let Some(want) = binding_sha256 {
        if bound != want {
            return Err(GovError::new("APPROVAL_STALE", format!("gate {gate_id} was answered for another content or impact of {id} (subject {}), not the transaction as it stands (subject {want}); the answer does not bind it — re-simulate and obtain an answer for this transaction", if bound.is_empty() { "none".to_string() } else { bound.clone() })).with_details(json!({"gate": gate_id, "answered_subject": bound, "current_subject": want})));
        }
    }
    Ok(a)
}

/// Approve a simulated transaction. Human approval is never supplied by the caller: it is DERIVED from the gate's
/// verified answer (`gates::verified_answer`: T2-bound, owner-signed for a human answer) for exactly this transaction
/// and simulated impact. Without a gate only the automatic path within CHANGE_POLICY.auto_approve_max_radius exists,
/// and it is recorded as an agent decision (human_approved: false).
pub fn approve(p: &Project, id: &str, by: &str, method: &str) -> Result<Value> {
    control::guard_write(p, "cit approve")?;
    crate::authority::require(
        p,
        if method == "human" {
            "approve_cit_human"
        } else {
            "approve_cit_auto"
        },
    )?;
    let pol = p.policies();
    let store = RecordStore::load(&p.root);
    let r = load_cit(&store, id)?;
    crate::scheduler::guard(p, ops::CIT_APPROVE, &guard_paths(&store, &r.data))?;
    if r.get("cit_status") != "SIMULATED" {
        return Err(GovError::new(
            "USAGE",
            format!(
                "{id} must be SIMULATED before approval (is {})",
                r.get("cit_status")
            ),
        ));
    }
    let st = binding::verified_state(&r)?;
    if !matches!(st.cit_status.as_str(), "SIMULATED" | "APPROVED") {
        return Err(GovError::new(
            "CIT_STATE_MISMATCH",
            format!(
                "{id} reads SIMULATED but gov last sealed it {}; simulate it through gov",
                st.cit_status
            ),
        ));
    }
    let content = binding::content_digest(&r.data);
    if content != st.content_sha256 {
        return Err(GovError::new("APPROVAL_STALE", format!("{id}: the transaction content (proposal/trigger/targets/mutation manifest) changed after it was simulated; approval binds the exact content — run `gov cit simulate {id}` and obtain a decision for the transaction as it stands")).with_details(json!({"sealed_content_sha256": st.content_sha256, "content_sha256": content})));
    }
    let impact_sha = binding::impact_digest(&r.data["impact"]);
    if st.impact_sha256.as_deref() != Some(impact_sha.as_str()) {
        return Err(GovError::new("APPROVAL_STALE", format!("{id}: the recorded impact is not the impact gov simulated; approval binds the simulated impact — re-simulate {id}")).with_details(json!({"sealed_impact_sha256": st.impact_sha256, "impact_sha256": impact_sha})));
    }
    let record_gate = Some(r.get("human_gate")).filter(|g| !g.is_empty());
    if record_gate != st.human_gate {
        return Err(GovError::new("GATE_MISMATCH", format!("{id} names gate {:?} but gov raised {:?} for it; a gate answer approves exactly the transaction it was raised for", record_gate, st.human_gate)));
    }
    let hg_required = r.data["impact"]["human_gate_required"]
        .as_bool()
        .unwrap_or(true);
    let radius = r.data["impact"]["radius"].clone();
    let trigger = r.get("trigger");
    let proposal = r.get("proposal");
    let mut decision_id = r.get("decision");
    let approval: Value = if let Some(gate_id) = st.human_gate.clone() {
        let a = match gate_answer_for(p, &store, id, &gate_id, st.binding_sha256.as_deref()) {
            Ok(a) => a,
            Err(e) => return Err(e),
        };
        if !a.authorises_blocked_work {
            reject_sealed(p, id, &format!("gate {gate_id} answered '{}'", a.option))?;
            return Err(GovError::new("GATE_DECLINED", format!("human gate {gate_id} was answered '{}' by {} ({}): the human declined {id}; a decline can never become approval", a.option, a.answered_by, a.by_kind)).with_details(json!({"gate": gate_id, "answer": a.to_value()})));
        }
        if method == "human" && a.by_kind != "human" {
            return Err(GovError::new("APPROVAL_METHOD_MISMATCH", format!("gate {gate_id} was answered by an agent within HUMAN_GATE_POLICY.agent_resolvable_when, not by a human; `--method human` cannot manufacture human approval (use --method auto, or obtain a human answer)")).with_details(json!({"gate": gate_id, "answer": a.to_value()})));
        }
        let did = a.decision.clone().ok_or_else(|| {
            GovError::new("GATE_STATE_INVALID", format!("gate {gate_id} is ANSWERED but no OS-written decision record derives from it; the answer trail is incomplete"))
        })?;
        if let Some(d) = store.get(&did) {
            let dc = d.get("cit");
            if !dc.is_empty() && dc != id {
                return Err(GovError::new(
                    "GATE_MISMATCH",
                    format!("decision {did} was made for {dc}, not {id}"),
                ));
            }
        }
        if decision_id.is_empty() {
            decision_id = did.clone();
        } else if decision_id != did {
            return Err(GovError::new(
                "GATE_STATE_INVALID",
                format!("{id} references decision {decision_id} but gate {gate_id} produced {did}"),
            ));
        }
        let g = &a.record;
        json!({"gate": gate_id, "decision": did, "method": if a.by_kind == "human" { "human" } else { "agent_within_policy" }, "human_approved": a.by_kind == "human",
            "answered_by": a.answered_by, "answered_by_kind": a.by_kind, "answered_at": g.data["answer"]["at"], "answer_option": a.option, "answer_rationale": g.data["answer"]["rationale"],
            "presented_at": g.data.get("presented_at").cloned().unwrap_or(Value::Null), "presented_by": g.data.get("presented_by").cloned().unwrap_or(Value::Null),
            "human_evidence": a.to_value()["human_evidence"],
            "binding": {"subject_sha256": st.binding_sha256, "content_sha256": content, "impact_sha256": impact_sha, "verified": true},
            "recorded_by": by, "recorded_by_session": p.session_id, "recorded_by_role": p.role, "at": now_iso()})
    } else {
        if hg_required {
            return Err(GovError::new("HUMAN_GATE_REQUIRED", format!("{id} requires a human decision gate but none is recorded; run `gov cit simulate {id}`")));
        }
        let auto_max = pol.get_str("CHANGE_POLICY", "auto_approve_max_radius", "R1");
        if radius_rank(radius.as_str().unwrap_or("R5")) > radius_rank(&auto_max) {
            return Err(GovError::new("HUMAN_GATE_REQUIRED", format!("radius {radius} exceeds CHANGE_POLICY.auto_approve_max_radius {auto_max}; re-simulate to raise a gate")));
        }
        if decision_id.is_empty() {
            let did = store.next_id("decision");
            let mut d = new_record(
                "decision",
                &did,
                &format!("Auto-approve {id}"),
                json!({"question": format!("Execute change {id}?"), "options": [{"id": "A", "description": proposal}], "chosen_option": "A", "rationale": format!("automatic approval within CHANGE_POLICY.auto_approve_max_radius (radius {radius}); no human gate was required"), "approved_by": by, "approved_at": now_iso(), "human_approved": false, "approved_by_kind": "agent", "impact_radius": radius, "reversibility": "snapshot rollback", "confidence": 0.9, "cit": id, "state_class": "AUTHORITATIVE", "tags": [trigger], "binding_sha256": st.binding_sha256}),
            );
            crate::t2::seal_record(&mut d, "cit approve (auto)")?;
            save_record(&p.root, &d)?;
            decision_id = did;
        }
        json!({"gate": Value::Null, "decision": decision_id, "method": "auto", "human_approved": false, "answered_by_kind": "agent",
            "binding": {"subject_sha256": st.binding_sha256, "content_sha256": content, "impact_sha256": impact_sha, "verified": true},
            "recorded_by": by, "recorded_by_session": p.session_id, "recorded_by_role": p.role, "at": now_iso()})
    };
    let mut s2 = RecordStore::load(&p.root);
    let r2 = s2.get_mut(id).unwrap();
    r2.set("cit_status", json!("APPROVED"));
    r2.set("approval", approval.clone());
    r2.set("decision", json!(decision_id));
    journal(
        r2,
        json!({"at": now_iso(), "event": "approved", "by": by, "method": approval["method"], "gate": approval["gate"], "decision": decision_id, "answered_by": approval["answered_by"], "answered_at": approval["answered_at"]}),
    );
    binding::seal(
        r2,
        CitState {
            cit_status: "APPROVED".into(),
            content_sha256: content,
            impact_sha256: Some(impact_sha),
            binding_sha256: st.binding_sha256.clone(),
            human_gate: st.human_gate.clone(),
            approval_sha256: Some(binding::approval_digest(&approval)),
            decision: Some(decision_id.clone()),
            ..Default::default()
        },
        "cit approve",
    )?;
    save_record(&p.root, r2)?;
    Ok(
        json!({"cit": id, "cit_status": "APPROVED", "decision": decision_id, "human_gate": approval["gate"], "method": approval["method"], "human_approved": approval["human_approved"]}),
    )
}

pub fn reject(p: &Project, id: &str, by: &str, reason: Option<&str>) -> Result<Value> {
    control::guard_write(p, "cit reject")?;
    crate::authority::require(p, "reject_cit")?;
    let store = RecordStore::load(&p.root);
    let r = load_cit(&store, id)?;
    if matches!(r.get("cit_status").as_str(), "COMMITTED" | "EXECUTING") {
        return Err(GovError::new(
            "USAGE",
            format!("{id} is {}; cannot reject", r.get("cit_status")),
        ));
    }
    // rejecting is the fail-safe direction: allowed on a record gov cannot vouch for, and sealed from here on
    reject_sealed(
        p,
        id,
        &format!(
            "rejected by {by}{}",
            reason.map(|r| format!(": {r}")).unwrap_or_default()
        ),
    )?;
    Ok(json!({"cit": id, "cit_status": "REJECTED"}))
}

/// Ids of the governed records a manifest changes (not the ones it only marks stale), as they are named now.
fn changed_record_ids(p: &Project, store: &RecordStore, cit: &Value) -> Vec<String> {
    let mut v = vec![];
    for op in cit["mutation_manifest"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        match op["op"].as_str().unwrap_or("") {
            "set_field" | "set_status" => {
                if let Some(t) = op["target"].as_str() {
                    v.push(t.to_string());
                }
            }
            "append_record" => {
                if let Some(t) = op["record"]["id"].as_str() {
                    v.push(t.to_string());
                }
            }
            "write_file" | "delete_file" | "move_file" => {
                let path = op["path"].as_str().unwrap_or("");
                if let Some(r) = store.records.iter().find(|r| r.path == path) {
                    v.push(r.id());
                } else if let Some(r) = op["content"]
                    .as_str()
                    .and_then(|c| parse_record_text(c, path))
                    .filter(|r| !r.id().is_empty())
                {
                    v.push(r.id());
                } else if !path.is_empty() {
                    // a plain repository file: its dependents are what the CIT-P impact analysis reached
                    v.push(format!("file:{path}"));
                }
                if let Some(to) = op["to"].as_str().filter(|t| !t.is_empty()) {
                    if store.records.iter().all(|r| r.path != path) {
                        v.push(format!("file:{to}"));
                    }
                }
            }
            _ => {}
        }
    }
    let _ = p;
    v.retain(|x| !x.is_empty());
    v.sort();
    v.dedup();
    v
}

fn snapshot_dir(p: &Project, id: &str) -> PathBuf {
    p.runtime_dir().join("cit").join(id)
}

fn take_snapshot(
    p: &Project,
    id: &str,
    cit: &Value,
    store: &RecordStore,
    extra: &[String],
) -> Result<Value> {
    let dir = snapshot_dir(p, id);
    let snap = dir.join("snapshot");
    crate::util::remove_dir_if_exists(&dir)?;
    std::fs::create_dir_all(&snap)?;
    let mut files = vec![];
    let mut created_paths = vec![];
    let mut want: Vec<String> = manifest_paths(cit)
        .into_iter()
        .filter_map(|x| {
            if p.root.join(&x).exists() {
                Some(x)
            } else {
                store.get(&x).map(|r| r.path.clone())
            }
        })
        .collect();
    for a in cit["impact"]["affected"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        if let Some(r) = a["node"].as_str().and_then(|n| store.get(n)) {
            want.push(r.path.clone());
        }
    }
    // every record and packet propagation will write (BC-P2-04): a rollback must undo the propagation too
    want.extend(extra.iter().cloned());
    for op in cit["mutation_manifest"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        if op["op"] == "write_file" || op["op"] == "append_record" {
            let path = op["path"].as_str().map(|s| s.to_string()).or_else(|| {
                op["record"]
                    .as_object()
                    .and_then(|r| r.get("id"))
                    .and_then(|i| i.as_str())
                    .and_then(|i| {
                        op["record"]["type"]
                            .as_str()
                            .and_then(|t| crate::records::record_path_for(t, i).ok())
                    })
            });
            if let Some(pth) = path {
                if !p.root.join(&pth).exists() {
                    created_paths.push(pth);
                }
            }
        }
        if op["op"] == "move_file" {
            if let Some(to) = op["to"].as_str() {
                created_paths.push(to.to_string());
            }
        }
    }
    want.sort();
    want.dedup();
    for rel in want {
        let src = p.root.join(&rel);
        if src.is_file() {
            let dst = snap.join(&rel);
            if let Some(d) = dst.parent() {
                std::fs::create_dir_all(d)?;
            }
            std::fs::copy(&src, &dst)?;
            files.push(rel);
        } else if src.is_dir() {
            copy_dir(&src, &snap.join(&rel))?;
            files.push(rel);
        }
    }
    let manifest = json!({"cit": id, "taken_at": now_iso(), "files": files, "created_paths": created_paths, "commit": p.git_commit()});
    write_json(&dir.join("snapshot.json"), &manifest)?;
    Ok(manifest)
}

/// Register paths the execution created after the snapshot was taken (generated revalidation tasks), so a rollback
/// removes them.
fn register_created(p: &Project, id: &str, created: &[String]) -> Result<()> {
    if created.is_empty() {
        return Ok(());
    }
    let path = snapshot_dir(p, id).join("snapshot.json");
    let mut m = read_json(&path)?;
    let mut list: Vec<Value> = m["created_paths"].as_array().cloned().unwrap_or_default();
    for c in created {
        if !list.iter().any(|x| x.as_str() == Some(c.as_str())) {
            list.push(json!(c));
        }
    }
    m["created_paths"] = json!(list);
    write_json(&path, &m)
}

fn apply_op(p: &Project, op: &Value, touched: &mut Vec<String>) -> Result<()> {
    let kind = op["op"].as_str().unwrap_or("");
    match kind {
        "set_status" | "set_field" | "mark_stale" => {
            let target = op["target"]
                .as_str()
                .ok_or_else(|| GovError::new("USAGE", format!("{kind} requires target")))?;
            let mut store = RecordStore::load(&p.root);
            let r = store
                .get_mut(target)
                .ok_or_else(|| GovError::new("RECORD_NOT_FOUND", format!("{target} not found")))?;
            match kind {
                "set_status" => {
                    r.set("status", op["value"].clone());
                    if op["value"] == "SUPERSEDED" {
                        if let Some(by) = op["by"].as_str() {
                            r.set("superseded_by", json!(by));
                        }
                    }
                }
                "set_field" => {
                    let f = op["field"]
                        .as_str()
                        .ok_or_else(|| GovError::new("USAGE", "set_field requires field"))?;
                    if f.contains('.') {
                        crate::util::deep_set(&mut r.data, f, op["value"].clone());
                    } else {
                        r.set(f, op["value"].clone());
                    }
                }
                _ => {
                    r.set("staleness", json!({"stale": true, "reason": op["reason"].as_str().unwrap_or("CIT propagation"), "at": now_iso()}));
                }
            }
            r.set("updated", json!(today()));
            touched.push(r.path.clone());
            save_record(&p.root, r)?;
        }
        "write_file" => {
            let path = op["path"]
                .as_str()
                .ok_or_else(|| GovError::new("USAGE", "write_file requires path"))?;
            if glob_match("governance/kernel/**", path) {
                return Err(GovError::new(
                    "INV_007",
                    "CIT may not write into governance/kernel/",
                ));
            }
            // **`OWNER-DECISION-0006` §6 bullet 2, at the one mutation op that does not pass `save_record`.**
            //
            // `append_record` below persists through `save_record`, which is the §6 record-write sink. A
            // `write_file` op reaches the same durable artefact by writing the bytes directly, so the effect is
            // asked here by the record type the bytes themselves declare. Below floor `cit execute` is refused at
            // the operation level too; this is the effect-level control, which is the one that survives a caller
            // that reaches this op by some other route. Nothing changes above floor.
            let content = op["content"].as_str().unwrap_or("");
            if let Some(r) = parse_record_text(content, path) {
                if let Some(effect) = crate::srr::breakglass::guarded_record_effect(&r.rtype()) {
                    crate::srr::breakglass::guard_effect(effect, "cit write_file")?;
                }
            }
            write_text(&p.root.join(path), content)?;
            touched.push(path.to_string());
        }
        "move_file" => {
            let (from, to) = (
                op["path"].as_str().unwrap_or(""),
                op["to"].as_str().unwrap_or(""),
            );
            if from.is_empty() || to.is_empty() {
                return Err(GovError::new("USAGE", "move_file requires path and to"));
            }
            // §6 bullet 2, as for `write_file`: relocating a file that parses as a guarded record type reaches
            // the same durable artefact without passing `save_record`.
            if let Some(r) = std::fs::read_to_string(p.root.join(from))
                .ok()
                .and_then(|t| parse_record_text(&t, to))
            {
                if let Some(effect) = crate::srr::breakglass::guarded_record_effect(&r.rtype()) {
                    crate::srr::breakglass::guard_effect(effect, "cit move_file")?;
                }
            }
            if let Some(d) = p.root.join(to).parent() {
                std::fs::create_dir_all(d)?;
            }
            let (code, _, _) = p.git(&["mv", "-k", from, to]);
            if code != 0 || !p.root.join(to).exists() {
                std::fs::rename(p.root.join(from), p.root.join(to))?;
            }
            touched.push(from.to_string());
            touched.push(to.to_string());
        }
        "delete_file" => {
            let path = op["path"].as_str().unwrap_or("");
            let full = p.root.join(path);
            if full.is_file() {
                std::fs::remove_file(&full)?;
            } else if full.is_dir() {
                std::fs::remove_dir_all(&full)?;
            }
            touched.push(path.to_string());
        }
        "append_record" => {
            let rec = op["record"].clone();
            let (id, t) = (
                rec["id"].as_str().unwrap_or("").to_string(),
                rec["type"].as_str().unwrap_or("").to_string(),
            );
            if id.is_empty() || t.is_empty() {
                return Err(GovError::new(
                    "USAGE",
                    "append_record requires record.id and record.type",
                ));
            }
            let path = op["path"]
                .as_str()
                .map(|s| s.to_string())
                .unwrap_or(crate::records::record_path_for(&t, &id)?);
            let mut r = parse_record_text(&crate::util::to_yaml(&rec)?, &path)
                .ok_or_else(|| GovError::new("USAGE", "invalid record"))?;
            r.path = path.clone();
            if p.schemas().has(&t) {
                p.schemas().validate(&t, &r.data, &format!("({id})"))?;
            } else {
                p.schemas()
                    .validate("record", &r.data, &format!("({id})"))?;
            }
            save_record(&p.root, &r)?;
            touched.push(path);
        }
        "regenerate_views" => {
            crate::tools::generate_registry(p)?;
            crate::adapters::generate(p)?;
        }
        "set_lock_field" => {
            return Err(GovError::new(
                "USAGE",
                "set_lock_field is reserved for framework migrations (gov update)",
            ));
        }
        other => {
            return Err(GovError::new(
                "USAGE",
                format!("unknown mutation op {other}"),
            ))
        }
    }
    Ok(())
}

/// CIT-E: snapshot -> apply -> propagate -> regenerate -> refresh index -> verify -> commit or rollback.
pub fn execute(p: &Project, db: &RuntimeDb, id: &str) -> Result<Value> {
    control::guard_write(p, "cit execute")?;
    crate::authority::require(p, "execute_cit")?;
    let pol = p.policies();
    let store = RecordStore::load(&p.root);
    let rec = load_cit(&store, id)?;
    // G0 (tier contract, IP-WS02-05). A hard-block refuses reliant work; change control is also how a blocked
    // repository is repaired through governance, so a transaction may execute under an active hard-block only if it
    // REPAIRS the blocking condition: the guard's own targeted re-evaluation runs inside the transaction after the
    // manifest is applied, and a transaction that leaves any block in place is refused and rolled back (the block
    // state is then re-established). Nothing commits under a hard-block it does not clear.
    let gpaths = guard_paths(&store, &rec.data);
    let entry_blocks: Option<Value> = match crate::scheduler::guard(p, ops::CIT_EXECUTE, &gpaths) {
        Ok(_) => None,
        Err(e) if e.code == "HEALTH_HARD_BLOCK" => Some(e.details.clone()),
        Err(e) => return Err(e),
    };
    if rec.get("cit_status") != "APPROVED" {
        return Err(GovError::new(
            "USAGE",
            format!(
                "{id} must be APPROVED to execute (is {})",
                rec.get("cit_status")
            ),
        ));
    }
    if rec
        .data
        .get("secret_flagged")
        .and_then(|v| v.as_bool())
        .unwrap_or(false)
    {
        return Err(GovError::new("SECRET_IN_MANIFEST", format!("{id} was flagged at proposal time because its proposal/manifest contained secret material (redacted); it cannot be executed. Re-propose without secrets (store them in a secret-class path).")).with_details(rec.data.get("blocked_reasons").cloned().unwrap_or(Value::Null)));
    }
    if !pol.get_bool("CHANGE_POLICY", "rollback.snapshot_before_execute", true) {
        return Err(GovError::new("POLICY_UNSAFE", "CHANGE_POLICY.rollback.snapshot_before_execute is false; execution without a snapshot is refused by this release"));
    }
    // ---- the approval is re-derived at execution time and must still bind exactly this transaction (BC-P2-11)
    let st = binding::verified_state(&rec)?;
    let content = binding::content_digest(&rec.data);
    if content != st.content_sha256 {
        return Err(GovError::new("APPROVAL_STALE", format!("{id}: the transaction content (mutation manifest, targets, proposal or trigger) changed after it was approved; the approval binds the exact content that was answered — nothing was executed. Re-simulate {id} and obtain a decision for the transaction as it stands")).with_details(json!({"approved_content_sha256": st.content_sha256, "content_sha256": content})));
    }
    let impact_sha = binding::impact_digest(&rec.data["impact"]);
    if st.impact_sha256.as_deref() != Some(impact_sha.as_str()) {
        return Err(GovError::new("APPROVAL_STALE", format!("{id}: the recorded impact is not the impact that was approved; nothing was executed — re-simulate {id}")).with_details(json!({"approved_impact_sha256": st.impact_sha256, "impact_sha256": impact_sha})));
    }
    let approval = rec.data.get("approval").cloned().unwrap_or(Value::Null);
    if approval.is_null() {
        return Err(GovError::new(
            "USAGE",
            format!("{id} is APPROVED without an approval record; re-simulate and approve"),
        ));
    }
    let record_gate = Some(rec.get("human_gate")).filter(|g| !g.is_empty());
    if record_gate != st.human_gate {
        return Err(GovError::new("GATE_MISMATCH", format!("{id} names gate {:?} but gov raised {:?} for it; a gate answer approves exactly the transaction it was raised for", record_gate, st.human_gate)));
    }
    let hg_required = rec.data["impact"]["human_gate_required"]
        .as_bool()
        .unwrap_or(true);
    if let Some(gate) = st.human_gate.clone() {
        // the decision the approval recorded must still be ACTIVE (a withdrawn/rejected decision revokes it)
        let adec = approval["decision"].as_str().unwrap_or("").to_string();
        if let Some(d) = store.get(&adec) {
            if d.status() != "ACTIVE" {
                return Err(GovError::new(
                    "GATE_REVOKED",
                    format!(
                        "decision {adec} for gate {gate} is {}; it no longer authorises {id}",
                        d.status()
                    ),
                ));
            }
        }
        let a = gate_answer_for(p, &store, id, &gate, st.binding_sha256.as_deref())?;
        if !a.authorises_blocked_work {
            return Err(GovError::new(
                "GATE_DECLINED",
                format!(
                    "human gate {gate} was answered '{}': {id} was declined",
                    a.option
                ),
            )
            .with_details(json!({"gate": gate, "answer": a.to_value()})));
        }
        if approval["gate"].as_str() != Some(gate.as_str()) {
            return Err(GovError::new(
                "APPROVAL_STALE",
                format!(
                    "{id} was approved against gate {} but now references {gate}; approve again",
                    approval["gate"]
                ),
            )
            .with_details(json!({"approval": approval})));
        }
        if a.decision.as_deref() != Some(adec.as_str()) || rec.get("decision") != adec {
            return Err(GovError::new(
                "APPROVAL_STALE",
                format!(
                    "approval decision {} does not match the gate's verified decision {:?}",
                    approval["decision"], a.decision
                ),
            ));
        }
        if approval["answered_at"] != a.record.data["answer"]["at"]
            || approval["answered_by"].as_str() != Some(a.answered_by.as_str())
        {
            return Err(GovError::new(
                "APPROVAL_STALE",
                format!(
                    "gate {gate} was re-answered after approval ({} → {}); approve again",
                    approval["answered_at"], a.record.data["answer"]["at"]
                ),
            ));
        }
    } else if hg_required
        || approval["method"].as_str() == Some("human")
        || approval["human_approved"].as_bool().unwrap_or(false)
    {
        return Err(GovError::new("APPROVAL_STALE", format!("{id} claims human approval without a gate record; human approval derives only from a recorded gate answer")));
    }
    // the approval must be the one gov derived and sealed (checked after the gate, so the authoritative cause of a
    // refusal — an unanswered, declined or revoked gate — is the one reported)
    if st.cit_status != "APPROVED" {
        return Err(GovError::new("APPROVAL_STALE", format!("{id} reads APPROVED but gov last sealed it {}; only an approval gov derived from a verified answer (or the automatic path) executes — approve it through gov", st.cit_status)).with_details(json!({"sealed_status": st.cit_status})));
    }
    if st.approval_sha256.as_deref() != Some(binding::approval_digest(&approval).as_str()) {
        return Err(GovError::new("APPROVAL_STALE", format!("{id}: the approval record is not the one gov derived when it approved; nothing was executed — approve again through gov")));
    }
    // ---- propagation is planned before anything is applied, so the snapshot covers every record it will touch
    let changed = changed_record_ids(p, &store, &rec.data);
    let before_hashes: Vec<(String, Option<String>)> = changed
        .iter()
        .map(|c| (c.clone(), propagation::record_hash(&p.root, &store, c)))
        .collect();
    let plan = propagation::plan(p, &store, &changed, Some(&rec.data["impact"]), None);
    let snapshot = take_snapshot(p, id, &rec.data, &store, &plan.paths(p, &store))?;
    // verification compares against a FRESH pre-execution baseline (A0-K2-03): damage already in the working tree but
    // not yet indexed is not attributed to this transaction
    if pol.get_bool("CHANGE_POLICY", "propagation.refresh_index", true) {
        let _ = crate::memory::indexer::rebuild(
            p,
            crate::memory::indexer::IndexOptions {
                incremental: true,
                ..Default::default()
            },
        );
    }
    let dangling_before: std::collections::BTreeSet<String> = graph::dangling_edges(db)?
        .iter()
        .map(|e| e.to_string())
        .collect();
    let mut s = RecordStore::load(&p.root);
    {
        let r = s.get_mut(id).unwrap();
        r.set("cit_status", json!("EXECUTING"));
        r.set("execution", json!({"started": now_iso(), "snapshot": snapshot, "session": p.session_id, "role": p.role, "gate": approval["gate"], "decision": approval["decision"], "approval_method": approval["method"]}));
        journal(
            r,
            json!({"at": now_iso(), "event": "executing", "gate": approval["gate"], "decision": approval["decision"], "session": p.session_id}),
        );
        binding::seal(
            r,
            CitState {
                cit_status: "EXECUTING".into(),
                content_sha256: content.clone(),
                impact_sha256: Some(impact_sha.clone()),
                binding_sha256: st.binding_sha256.clone(),
                human_gate: st.human_gate.clone(),
                approval_sha256: st.approval_sha256.clone(),
                decision: st.decision.clone(),
                ..Default::default()
            },
            "cit execute",
        )?;
        save_record(&p.root, r)?;
    }
    let mut touched = vec![];
    let mut created: Vec<String> = vec![];
    let result: Result<Value> = (|| {
        for op in rec.data["mutation_manifest"]
            .as_array()
            .cloned()
            .unwrap_or_default()
        {
            apply_op(p, &op, &mut touched)?;
        }
        // propagation (framework §47.2; BC-P2-04): open AND completed dependents, their evidence, validation evidence,
        // checkpoints, handoffs and packets; revalidation tasks for completed work
        let after_store = RecordStore::load(&p.root);
        let changes: Vec<propagation::InputChange> = before_hashes
            .iter()
            .map(|(cid, from)| propagation::InputChange {
                id: cid.clone(),
                from: from.clone(),
                to: propagation::record_hash(&p.root, &after_store, cid),
            })
            .filter(|c| c.from != c.to)
            .collect();
        let prop = propagation::apply(
            p,
            &plan,
            &changes,
            &propagation::Cause::Cit(id.to_string()),
            &propagation::ApplyOptions::default(),
            &mut touched,
            &mut created,
        );
        register_created(p, id, &created)?;
        let prop = prop?;
        if pol.get_bool(
            "CHANGE_POLICY",
            "propagation.regenerate_derived_views",
            true,
        ) {
            crate::tools::generate_registry(p)?;
            crate::adapters::generate(p)?;
        }
        if pol.get_bool("CHANGE_POLICY", "propagation.refresh_index", true) {
            crate::memory::indexer::rebuild(
                p,
                crate::memory::indexer::IndexOptions {
                    incremental: true,
                    ..Default::default()
                },
            )?;
        }
        // verification
        let mut problems = vec![];
        let required = pol.get_list("CHANGE_POLICY", "verification_required");
        if required.iter().any(|r| r == "schema_validation") {
            let st = RecordStore::load(&p.root);
            for pth in &touched {
                if let Some(r) = st.records.iter().find(|r| r.path == *pth) {
                    let t = r.rtype();
                    let schema = if p.schemas().has(&t) {
                        t
                    } else {
                        "record".into()
                    };
                    if let Ok(errs) = p.schemas().errors(&schema, &r.data) {
                        for e in errs {
                            problems.push(format!("{pth}: {e}"));
                        }
                    }
                }
            }
        }
        if required.iter().any(|r| r == "graph_integrity") {
            let db2 = RuntimeDb::open(&p.db_path())?;
            let d = graph::dangling_edges(&db2)?;
            let new_dangling: Vec<&Value> = d
                .iter()
                .filter(|e| !dangling_before.contains(&e.to_string()))
                .collect();
            if !new_dangling.is_empty() {
                problems.push(format!(
                    "{} new dangling edge(s) introduced: {}",
                    new_dangling.len(),
                    new_dangling
                        .iter()
                        .map(|e| format!("{} {} {}", e["src"], e["type"], e["dst"]))
                        .collect::<Vec<_>>()
                        .join(", ")
                ));
            }
        }
        if required.iter().any(|r| r == "index_freshness") {
            let f = freshness(p);
            if !f.fresh {
                problems.push(format!(
                    "index not fresh after refresh: {} stale/{} added/{} removed",
                    f.stale.len(),
                    f.added.len(),
                    f.removed.len()
                ));
            }
        }
        if !problems.is_empty() {
            return Err(GovError::new(
                "VERIFICATION_FAILED",
                format!("CIT-E verification failed: {}", problems.join("; ")),
            )
            .with_details(json!({"problems": problems})));
        }
        let mut v = prop;
        v["touched"] = json!(touched.clone());
        Ok(v)
    })();
    match result {
        Ok(v) => {
            // what the execution wrote, per path (IP-3: in-window CIT coverage binds content)
            let mut all = touched.clone();
            all.extend(created.iter().cloned());
            let writes: Vec<Value> = binding::capture_writes(&p.root, &all)
                .iter()
                .map(|w| w.to_value())
                .collect();
            let writes_v = json!(writes);
            let mut s2 = RecordStore::load(&p.root);
            let r = s2.get_mut(id).unwrap();
            let mut ex = r.data["execution"].clone();
            ex["finished"] = json!(now_iso());
            ex["result"] = json!("committed");
            ex["verification"] = json!({"ok": true});
            ex["propagation"] = v.clone();
            ex["writes"] = writes_v.clone();
            r.set("execution", ex);
            r.set("cit_status", json!("COMMITTED"));
            journal(r, json!({"at": now_iso(), "event": "committed"}));
            binding::seal(
                r,
                CitState {
                    cit_status: "COMMITTED".into(),
                    content_sha256: content.clone(),
                    impact_sha256: Some(impact_sha.clone()),
                    binding_sha256: st.binding_sha256.clone(),
                    human_gate: st.human_gate.clone(),
                    approval_sha256: st.approval_sha256.clone(),
                    decision: st.decision.clone(),
                    writes_sha256: Some(binding::writes_digest(&writes_v)),
                    ..Default::default()
                },
                "cit execute",
            )?;
            save_record(&p.root, r)?;
            let _ = crate::memory::indexer::rebuild(
                p,
                crate::memory::indexer::IndexOptions {
                    incremental: true,
                    ..Default::default()
                },
            );
            // under a hard-block the transaction stands only if it repaired the blocking condition: the guard
            // re-evaluates the blocks against the committed state; any block left means the commit is rolled back
            let mut v = v;
            if let Some(b) = &entry_blocks {
                match crate::scheduler::guard(p, ops::CIT_EXECUTE, &gpaths) {
                    Ok(g) => {
                        v["hard_block_repair"] = json!({"blocks_before": b["blocks"], "cleared": true, "reevaluated": g["reevaluated"],
                            "note": "the repository was under a hard-block that this transaction repairs; the guard's re-evaluation of the committed state found no block left"});
                    }
                    Err(e) => {
                        let why = format!("the repository is under hard-block(s) this transaction does not repair ({}); under a hard-block a transaction stands only when it repairs the blocking condition", e.message);
                        let rb = rollback(p, id, Some(&why))?;
                        reestablish_blocks(p, &b["blocks"]);
                        return Err(GovError::new(
                            "HEALTH_HARD_BLOCK",
                            format!("{why} — rolled back"),
                        )
                        .with_details(json!({"blocks": e.details, "rollback": rb})));
                    }
                }
            }
            let db2 = RuntimeDb::open(&p.db_path())?;
            let ck = crate::checkpoints::create(
                p,
                &db2,
                json!({"trigger": "accepted_cit", "next_action": "gov continue", "last_completed_step": format!("executed {id}"), "open_transactions": [],
                    "propagation": {"cit": id, "retest_required": v["retest_required"], "revalidation_required": v["revalidation_required"], "revalidation_tasks": v["revalidation_tasks"], "stale_tests": v["stale_tests"], "stale_checkpoints": v["stale_checkpoints"], "invalidated_packets": v["invalidated_packets"]}}),
            )?;
            prune_snapshots(
                p,
                pol.get_i64("CHANGE_POLICY", "rollback.keep_snapshots", 20)
                    .max(1) as usize,
            );
            // G4 (tier contract, IP-WS02-06): the wider staleness check a milestone triggers, recorded with the CIT
            let paths: Vec<String> = writes
                .iter()
                .filter_map(|w| w["path"].as_str().map(String::from))
                .collect();
            let health = match crate::scheduler::tier_run(
                p,
                Tier::G4,
                Trigger::cit_execute(id, &paths),
            ) {
                Ok(h) => {
                    json!({"tier": "G4", "verdict": h["verdict"], "health_result": h["health_result"], "audit": h["audit"], "state": h["state"], "counts": h["counts"]})
                }
                Err(e) => {
                    json!({"tier": "G4", "error": {"code": e.code, "message": e.message}})
                }
            };
            // recorded with the execution (outside the sealed state, which binds status, digests and writes only); the
            // index is refreshed again so the committed transaction leaves it current
            let mut s3 = RecordStore::load(&p.root);
            if let Some(r) = s3.get_mut(id) {
                let mut ex = r.data["execution"].clone();
                ex["health"] = health.clone();
                r.set("execution", ex);
                save_record(&p.root, r)?;
            }
            let _ = crate::memory::indexer::rebuild(
                p,
                crate::memory::indexer::IndexOptions {
                    incremental: true,
                    ..Default::default()
                },
            );
            Ok(
                json!({"cit": id, "cit_status": "COMMITTED", "propagation": v, "checkpoint": ck["id"], "health": health}),
            )
        }
        Err(e) => {
            let rb = restore_snapshot(p, id)?;
            // derived views regenerated during the failed execution are regenerated from the restored state
            // (A0-K2-02: rollback leaves derived views consistent with the restored authoritative state)
            let _ = crate::tools::generate_registry(p);
            let _ = crate::adapters::generate(p);
            let mut s2 = RecordStore::load(&p.root);
            if let Some(r) = s2.get_mut(id) {
                let mut ex = r.data["execution"].clone();
                ex["finished"] = json!(now_iso());
                ex["result"] = json!("rolled_back");
                ex["error"] = json!(e.to_string());
                ex["verification"] = json!({"ok": false, "details": e.details});
                r.set("execution", ex);
                r.set("cit_status", json!("ROLLED_BACK"));
                journal(
                    r,
                    json!({"at": now_iso(), "event": "rolled_back", "error": e.to_string()}),
                );
                binding::seal(
                    r,
                    CitState {
                        cit_status: "ROLLED_BACK".into(),
                        content_sha256: content.clone(),
                        impact_sha256: Some(impact_sha.clone()),
                        binding_sha256: st.binding_sha256.clone(),
                        human_gate: st.human_gate.clone(),
                        approval_sha256: st.approval_sha256.clone(),
                        decision: st.decision.clone(),
                        ..Default::default()
                    },
                    "cit execute",
                )?;
                save_record(&p.root, r)?;
            }
            let _ = crate::memory::indexer::rebuild(
                p,
                crate::memory::indexer::IndexOptions {
                    incremental: true,
                    ..Default::default()
                },
            );
            if let Some(b) = &entry_blocks {
                reestablish_blocks(p, &b["blocks"]);
            }
            Err(GovError::new(
                &e.code,
                format!(
                    "{} — rolled back ({} files restored)",
                    e.message,
                    rb["restored"].as_array().map(|a| a.len()).unwrap_or(0)
                ),
            )
            .with_details(json!({"rollback": rb, "details": e.details})))
        }
    }
}

/// Re-run the checks behind `blocks` on the restored tree, so a rolled-back repair attempt cannot leave a block
/// cleared by the re-evaluation it ran on the transaction's (now undone) changes.
fn reestablish_blocks(p: &Project, blocks: &Value) {
    let mut fams: Vec<String> = vec![];
    let mut doctor = false;
    for b in blocks.as_array().cloned().unwrap_or_default() {
        if b["surface"] == "doctor" {
            doctor = true;
        } else if let Some(c) = b["check"].as_str() {
            if !fams.iter().any(|x| x == c) {
                fams.push(c.to_string());
            }
        }
    }
    if !fams.is_empty() {
        let mut o = crate::scheduler::RunOptions::new(Tier::G0, Trigger::new(ops::CIT_EXECUTE));
        o.selection = crate::scheduler::Selection::Explicit(fams);
        o.surface = "cit-rollback".into();
        o.record = crate::scheduler::RecordPolicy::Never;
        let _ = crate::scheduler::run_suite(p, &o);
    }
    if doctor {
        let _ = crate::doctor::run(p);
    }
}

/// **Propagate upstream changes made outside change control** (`gov cit propagate`; BC-P2-04 direct path): detect
/// every input whose bytes differ from what dependent work consumed and propagate it exactly as CIT-E would.
pub fn propagate_detected(p: &Project, dry_run: bool) -> Result<Value> {
    if !dry_run {
        control::guard_write(p, "cit propagate")?;
        crate::authority::require(p, "simulate_cit")?;
    }
    propagation::detect_and_propagate(p, "gov cit propagate", dry_run)
}

/// **Materiality of a proposed manifest or of changes already made** (`gov cit classify`; read-only).
pub fn classify(
    p: &Project,
    id: Option<&str>,
    paths: &[String],
    base: Option<&str>,
) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    if let Some(id) = id {
        let r = load_cit(&store, id)?;
        let m = materiality::classify_manifest(p, &store, &r.data);
        return Ok(json!({"cit": id, "materiality": m.to_value(&r.get("trigger"))}));
    }
    let m = materiality::classify_paths(p, paths, base);
    Ok(json!({"paths": paths, "base": base.unwrap_or("HEAD"), "materiality": m.to_value("")}))
}

/// The honoured state of every CIT (for doctor/suite reporting and `gov cit list`).
pub fn bindings(p: &Project) -> Vec<Value> {
    RecordStore::load(&p.root)
        .of_type("cit")
        .into_iter()
        .map(|c| json!({"id": c.id(), "cit_status": c.get("cit_status"), "state": binding::binding_of(c)}))
        .collect()
}

/// CHANGE_POLICY.rollback.keep_snapshots: keep only the newest N CIT snapshot directories (older transactions cannot be
/// rolled back automatically afterwards; git history remains).
pub fn prune_snapshots(p: &Project, keep: usize) {
    let base = p.runtime_dir().join("cit");
    let Ok(rd) = std::fs::read_dir(&base) else {
        return;
    };
    let mut dirs: Vec<(std::time::SystemTime, PathBuf)> = rd
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|d| d.join("snapshot.json").exists())
        .map(|d| {
            (
                std::fs::metadata(d.join("snapshot.json"))
                    .and_then(|m| m.modified())
                    .unwrap_or(std::time::UNIX_EPOCH),
                d,
            )
        })
        .collect();
    dirs.sort_by_key(|d| std::cmp::Reverse(d.0));
    for (_, d) in dirs.into_iter().skip(keep) {
        let _ = std::fs::remove_dir_all(d);
    }
}

/// Restore the snapshot taken before execution; remove files created by the transaction.
pub fn restore_snapshot(p: &Project, id: &str) -> Result<Value> {
    let dir = snapshot_dir(p, id);
    let manifest = read_json(&dir.join("snapshot.json")).map_err(|_| {
        GovError::new(
            "SNAPSHOT_MISSING",
            format!("no snapshot for {id} under {}", dir.display()),
        )
    })?;
    let mut restored = vec![];
    let mut removed = vec![];
    for created in manifest["created_paths"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        let rel = created.as_str().unwrap_or("");
        let full = p.root.join(rel);
        if manifest["files"]
            .as_array()
            .map(|a| a.iter().any(|f| f.as_str() == Some(rel)))
            .unwrap_or(false)
        {
            continue;
        }
        if full.is_file() {
            std::fs::remove_file(&full)?;
            removed.push(rel.to_string());
        }
    }
    for f in manifest["files"].as_array().cloned().unwrap_or_default() {
        let rel = f.as_str().unwrap_or("");
        let src = dir.join("snapshot").join(rel);
        let dst = p.root.join(rel);
        if src.is_file() {
            if let Some(d) = dst.parent() {
                std::fs::create_dir_all(d)?;
            }
            std::fs::copy(&src, &dst)?;
            restored.push(rel.to_string());
        } else if src.is_dir() {
            crate::util::remove_dir_if_exists(&dst)?;
            copy_dir(&src, &dst)?;
            restored.push(rel.to_string());
        }
    }
    // moved files: if a move op moved A->B and A restored, remove B
    for op in RecordStore::load(&p.root)
        .get(id)
        .map(|r| r.data["mutation_manifest"].clone())
        .unwrap_or(json!([]))
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        if op["op"] == "move_file" {
            if let (Some(from), Some(to)) = (op["path"].as_str(), op["to"].as_str()) {
                if p.root.join(from).exists() && p.root.join(to).exists() && from != to {
                    let _ = std::fs::remove_file(p.root.join(to));
                    removed.push(to.to_string());
                }
            }
        }
    }
    Ok(json!({"cit": id, "restored": restored, "removed": removed}))
}

/// Explicit rollback of a COMMITTED or EXECUTING (interrupted) transaction.
pub fn rollback(p: &Project, id: &str, reason: Option<&str>) -> Result<Value> {
    crate::authority::require(p, "rollback_cit")?; // rollback is an emergency control: allowed while frozen
    let store = RecordStore::load(&p.root);
    let rec = store
        .get(id)
        .ok_or_else(|| GovError::new("CIT_NOT_FOUND", format!("{id} not found")))?;
    if !matches!(
        rec.get("cit_status").as_str(),
        "COMMITTED" | "EXECUTING" | "ROLLED_BACK"
    ) {
        return Err(GovError::new(
            "USAGE",
            format!("{id} is {}; nothing to roll back", rec.get("cit_status")),
        ));
    }
    let rb = restore_snapshot(p, id)?;
    let mut s2 = RecordStore::load(&p.root);
    let mut decision_id = String::new();
    if let Some(r) = s2.get_mut(id) {
        decision_id = r.get("decision");
        let prev = binding::verified_state(r).ok();
        r.set("cit_status", json!("ROLLED_BACK"));
        journal(
            r,
            json!({"at": now_iso(), "event": "rolled_back", "reason": reason, "by": p.session_id}),
        );
        // rolling back is the fail-safe direction: sealed whatever the record's prior binding was
        let content = binding::content_digest(&r.data);
        binding::seal(
            r,
            CitState {
                cit_status: "ROLLED_BACK".into(),
                content_sha256: content,
                impact_sha256: prev.as_ref().and_then(|s| s.impact_sha256.clone()),
                binding_sha256: prev.as_ref().and_then(|s| s.binding_sha256.clone()),
                human_gate: prev.as_ref().and_then(|s| s.human_gate.clone()),
                approval_sha256: prev.as_ref().and_then(|s| s.approval_sha256.clone()),
                decision: prev.as_ref().and_then(|s| s.decision.clone()),
                writes_sha256: prev.as_ref().and_then(|s| s.writes_sha256.clone()),
                ..Default::default()
            },
            "cit rollback",
        )?;
        save_record(&p.root, r)?;
    }
    // the approval decision no longer describes the project (verifier L7): mark it REJECTED with provenance
    if !decision_id.is_empty() {
        let mut s3 = RecordStore::load(&p.root);
        if let Some(d) = s3.get_mut(&decision_id) {
            d.set("status", json!("REJECTED"));
            d.set("state_class", json!("HISTORICAL"));
            d.set("rollback_of", json!(id));
            d.set("updated", json!(crate::util::today()));
            save_record(&p.root, d)?;
        }
    }
    let _ = crate::tools::generate_registry(p);
    let _ = crate::adapters::generate(p);
    let _ = crate::memory::indexer::rebuild(
        p,
        crate::memory::indexer::IndexOptions {
            incremental: true,
            ..Default::default()
        },
    );
    Ok(json!({"cit": id, "cit_status": "ROLLED_BACK", "rollback": rb}))
}

pub fn interrupted(p: &Project) -> Vec<Value> {
    RecordStore::load(&p.root).of_type("cit").into_iter().filter(|c| c.get("cit_status") == "EXECUTING").map(|c| json!({"id": c.id(), "started": c.data["execution"]["started"], "session": c.data["execution"]["session"], "snapshot_present": snapshot_dir(p, &c.id()).join("snapshot.json").exists()})).collect()
}

pub fn list(p: &Project) -> Vec<Value> {
    RecordStore::load(&p.root).of_type("cit").into_iter().map(|c| json!({"id": c.id(), "title": c.title(), "cit_status": c.get("cit_status"), "trigger": c.get("trigger"), "effective_trigger": c.data["materiality"]["effective_trigger"], "radius": c.data["impact"]["radius"], "human_gate": c.get("human_gate"), "decision": c.get("decision"), "state": binding::binding_of(c)})).collect()
}

pub fn read_text_opt(p: &Path) -> Option<String> {
    read_text(p).ok()
}
