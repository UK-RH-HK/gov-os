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
//!
//! ## Repair iteration 1, round 3 (WS-4)
//!
//! * **Every CIT write is sealed** (WS-5 IP-R3-2): each operation seals the sealed-state block *and* the whole record
//!   ([`binding::seal`]); the secret-material flag is bound into the block. Another OS writer of a CIT record re-seals
//!   it only when its seal verified before the write (IP for WS-3's gate writers).
//! * **Every OS write into a sealed record either re-seals a previously verified record or is recorded in the CIT's
//!   touched list, and a hand edit still breaks the seal** (integration O-7): manifest ops re-seal a record they
//!   modify when its seal verified before and the write is one the OS is entitled to seal
//!   ([`binding::content_write_entitled`]), and always record the path; rollback re-seals the approval decision it
//!   marks REJECTED (WS-2 R3-1); propagation re-seals the markers it writes; **a change propagated outside CIT-E**
//!   (detected direct change, handoff re-delivery) is recorded as a sealed system transaction whose touched list and
//!   per-path writes cover what it marked ([`propagate_as_transaction`], WS-5 IP-R3-3).
//! * **CIT-E verification judges graph integrity** with `memory::integrity::check` before and after the manifest: a
//!   new reversed, ill-typed or stale relationship declared by a record the transaction wrote, or a new supersession
//!   cycle, fails the verification and rolls back (WS-6 IP-R2-2).
//! * **Experimental output reaches production only through a promotion** the approved CIT names
//!   (`lifecycle::experiment::promotion_refusal` at approve and at execute; WS-10 IP-WS10-09).
//! * **Rollback snapshots are non-rebuildable state** kept where `paths::store_path(root, "cit-snapshots")` says
//!   (BC-P2-31, WS-6 IP-R2-10), relocated once from the legacy runtime directory.
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
    // the transaction's targets: a record by its path (the guard aliases ids and paths), and a file target as the
    // path it is (WS-2 IP-R3-WS02-04, round-3 integration: a CIT repairing a file-level block — a secret in `src/…` —
    // reaches that block's subjects and is admitted as its remedy)
    for t in cit["targets"].as_array().cloned().unwrap_or_default() {
        if let Some(x) = t.as_str().filter(|x| !x.is_empty()) {
            match store.get(x) {
                Some(r) => v.push(r.path.clone()),
                None => v.push(x.to_string()),
            }
        }
    }
    v.sort();
    v.dedup();
    v
}

pub fn propose(p: &Project, fields: Value) -> Result<Value> {
    propose_inner(p, fields, None, "propose_cit", false)
}

/// [`propose`] with the fields only the OS writes (`origin`, `system`) supplied by an OS host, the authority class the
/// host operation carries, and simulation forced (Contract v3 K3: a material change is simulated whether or not the
/// derived index exists yet — an empty index simulates against the records and paths alone).
fn propose_inner(
    p: &Project,
    mut fields: Value,
    os_fields: Option<Value>,
    authority: &str,
    always_simulate: bool,
) -> Result<Value> {
    control::guard_write(p, "cit propose")?;
    crate::authority::require(p, authority)?;
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
        // OS-owned: a transaction the OS itself proposed or recorded (schema `origin`/`system`)
        "origin",
        "system",
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
    if let Some(Value::Object(os)) = &os_fields {
        for (k, v) in os {
            o.insert(k.clone(), v.clone());
        }
    }
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
            secret_flagged: !secret_hits.is_empty(),
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
    if (wants_sim || always_simulate) && (always_simulate || p.db_path().exists()) {
        if always_simulate && !freshness(p).fresh {
            // CIT-P's impact analysis (graph reach, semantic candidates) runs on the index as the repository stands
            // now, as CIT-E's verification does: bring the derived index current first. Best effort: the change may be
            // the very thing the build needs (re-registering the pinned embedder), so a failed build leaves the
            // simulation on the index as it stands — unless there is none, which is refused with the build's cause.
            if let Err(e) = crate::memory::indexer::rebuild(
                p,
                crate::memory::indexer::IndexOptions {
                    incremental: true,
                    ..Default::default()
                },
            ) {
                if !p.db_path().exists() {
                    return Err(e);
                }
            }
        }
        let db = RuntimeDb::open(&p.db_path())?;
        if always_simulate {
            db.init_schema()?;
        }
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
        // a registration writes the registry too (and moves a registry still at its legacy location)
        if op["op"] == "register_plugin" {
            v.push(
                op["registry"]
                    .as_str()
                    .unwrap_or(crate::paths::PLUGIN_REGISTRY_PATH)
                    .to_string(),
            );
            v.push(crate::capabilities::registry::LEGACY_REGISTRY_PATH.to_string());
        }
        // R4-O1: an installation rewrites the generated tool registry as well
        if op["op"] == "install_tool" {
            if let Some(r) = op["registry"].as_str() {
                v.push(r.to_string());
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
    // Semantic candidates are advisory (excluded from the impact an approval binds: `binding::impact_of`). A query
    // that cannot run because of the retrieval profile itself — the pinned embedder unusable or not the one the live
    // index was built with — must not make change control impossible, least of all for the change that repairs the
    // profile (re-registering the pinned embedder; availability rule, P2-HO-0031): the simulation records why the
    // candidates are unavailable and the graph reach stands. No index at all is still refused (nothing to simulate on).
    let mut candidates_unavailable = Value::Null;
    let candidates = if k > 0 {
        match retrieve(p, db, rec.get("proposal").as_str(), RetrieveOptions { k, ..Default::default() }) {
            Ok(r) => r.hits.into_iter().map(|h| json!({"artifact_id": h.artifact_id, "path": h.path, "score": h.score, "routes": h.routes})).collect::<Vec<_>>(),
            Err(e) if e.code == "INDEX_MISSING" => return Err(e),
            Err(e) => {
                candidates_unavailable = json!({"code": e.code, "message": e.message});
                vec![]
            }
        }
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
    let mut consequences = consequences;
    if !candidates_unavailable.is_null() {
        consequences.push(format!(
            "semantic candidates unavailable ({}): the retrieval profile cannot answer the query now; the graph reach above stands",
            candidates_unavailable["code"].as_str().unwrap_or("?")
        ));
    }
    let routing = crate::routing::route(p, None, Some("governance"), None, Some(&radius))?;
    let mut impact = json!({"radius": radius, "seeds": seeds, "affected": affected.iter().map(|a| json!({"node": a.node, "hop": a.hop, "via": a.via})).collect::<Vec<_>>(), "affected_tasks": tasks, "tests_required": tests, "features": features, "other": other,
        "completed_tasks_to_revalidate": pre.done_tasks.keys().cloned().collect::<Vec<_>>(),
        "material_classes": mat.classes(), "effective_triggers": effective,
        "semantic_candidates": candidates, "semantic_candidates_unavailable": candidates_unavailable, "consequences": consequences, "human_gate_required": human_gate_required, "minimum_model_tier": routing["minimum_tier"], "simulated_at": now_iso(), "index_snapshot": db.get_meta("index_manifest_hash")});
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
    // the decision an earlier gate's answer recorded belongs to that gate: it does not survive a change of gate
    if existing.as_deref() != gate_id.as_deref() {
        if let Some(o) = r.data.as_object_mut() {
            o.remove("decision");
        }
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
            secret_flagged: st.secret_flagged,
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
                secret_flagged: prev.as_ref().map(|s| s.secret_flagged).unwrap_or(false),
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

/// **Experimental output enters production only through a governed promotion** (Contract v3:607-614 J2; WS-10
/// IP-WS10-09): a transaction that names an experiment, moves a file out of an experiment's outputs or writes bytes
/// equal to an experimental output into the production tree is refused (`EXPERIMENT_NOT_PROMOTED`) unless an
/// approved, still-honoured promotion of that experiment covers each such path. Asked at approve and again at
/// execute (a promotion revoked in between stops the execution).
fn promotion_check(p: &Project, store: &RecordStore, cit: &Record) -> Result<()> {
    let ctx = crate::lifecycle::Ctx::new(p, store);
    match crate::lifecycle::experiment::promotion_refusal(&ctx, cit) {
        Some(e) => Err(e),
        None => Ok(()),
    }
}

/// Approve a simulated transaction. Human approval is never supplied by the caller: it is DERIVED from the gate's
/// verified answer (`gates::verified_answer`: T2-bound, owner-signed for a human answer) for exactly this transaction
/// and simulated impact. Without a gate only the automatic path within CHANGE_POLICY.auto_approve_max_radius exists,
/// and it is recorded as an agent decision (human_approved: false).
pub fn approve(p: &Project, id: &str, by: &str, method: &str) -> Result<Value> {
    approve_with(p, id, by, method, None)
}

/// [`approve`] under the authority of an OS host operation (`authority`) instead of the CIT approval classes: used
/// only for a transaction the host itself proposed and whose content it checked ([`execute_registration`]). Every
/// other check — the guards, the sealed state, the content and impact binding, the gate answer read through
/// `gates::verified_answer` — is the same.
fn approve_with(
    p: &Project,
    id: &str,
    by: &str,
    method: &str,
    authority: Option<&str>,
) -> Result<Value> {
    control::guard_write(p, "cit approve")?;
    crate::authority::require(
        p,
        authority.unwrap_or(if method == "human" {
            "approve_cit_human"
        } else {
            "approve_cit_auto"
        }),
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
    // J2 (WS-10 IP-WS10-09): a transaction that carries experimental output into production is approvable only for
    // paths an approved promotion of that experiment covers
    promotion_check(p, &store, &r)?;
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
            secret_flagged: st.secret_flagged,
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
            "register_plugin" | "install_tool" => {
                if let Some(path) = op["path"].as_str().filter(|x| !x.is_empty()) {
                    v.push(format!("file:{path}"));
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

/// **Where rollback snapshots live** (BC-P2-31; Contract v3 B3:202 "deleting derived state cannot delete project
/// truth"; WS-6 IP-R2-10): the non-rebuildable OS store `paths::store_path(root, "cit-snapshots")`, never the derived
/// runtime directory a rebuild may delete. A snapshot tree an earlier release kept in the runtime directory is moved
/// here first ([`relocate_snapshots`]).
fn snapshot_base(p: &Project) -> PathBuf {
    relocate_snapshots(p);
    crate::paths::store_path(&p.root, "cit-snapshots")
        .unwrap_or_else(|| p.runtime_dir().join("cit"))
}

fn snapshot_dir(p: &Project, id: &str) -> PathBuf {
    snapshot_base(p).join(id)
}

/// Move the legacy snapshot tree (`paths::relocate_legacy`); when both locations hold snapshots (an older binary
/// wrote after the move), move each transaction's snapshot that is not already at the store location, keep the
/// others where they are, and report both. Never overwrites a snapshot.
fn relocate_snapshots(p: &Project) -> Vec<Value> {
    match crate::paths::relocate_legacy(&p.root, "cit-snapshots") {
        Ok(v) => v,
        Err(e) if e.code == "STATE_LOCATION_CONFLICT" => {
            let Some(store) = crate::paths::os_store("cit-snapshots") else {
                return vec![];
            };
            let Some((from, to)) = store.moves.first() else {
                return vec![];
            };
            let (legacy, dest) = (p.root.join(from), p.root.join(to));
            let mut out = vec![];
            for e in std::fs::read_dir(&legacy)
                .map(|rd| rd.filter_map(|e| e.ok()).collect::<Vec<_>>())
                .unwrap_or_default()
            {
                let name = e.file_name();
                let target = dest.join(&name);
                if target.exists() {
                    out.push(json!({"store": "cit-snapshots", "kept": crate::util::rel_posix(&e.path(), &p.root), "reason": "a snapshot of the same transaction exists at the store location"}));
                } else if std::fs::rename(e.path(), &target).is_ok() {
                    out.push(json!({"store": "cit-snapshots", "from": crate::util::rel_posix(&e.path(), &p.root), "to": crate::util::rel_posix(&target, &p.root), "action": "moved"}));
                }
            }
            let _ = std::fs::remove_dir(&legacy);
            out
        }
        Err(_) => vec![],
    }
}

fn take_snapshot(
    p: &Project,
    id: &str,
    cit: &Value,
    store: &RecordStore,
    extra: &[String],
) -> Result<Value> {
    // the store location is self-ignored by Git, so a snapshot is never observed as a worker's mutation
    crate::paths::ensure_state_dir(&p.root)?;
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
        if op["op"]
            .as_str()
            .map(|o| HOST_PROPOSED_OPS.contains(&o))
            .unwrap_or(false)
        {
            for k in ["path", "registry"] {
                if let Some(pth) = op[k].as_str() {
                    if !p.root.join(pth).exists() {
                        created_paths.push(pth.to_string());
                    }
                }
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

/// What the manifest ops of one execution did to OS-sealed records (integration O-7): the records re-sealed after a
/// write the OS verified and was entitled to seal, and the sealed records written but left unsealed (a content
/// rewrite of operation-owned facts, or a record whose seal did not verify before the write). Every one of them is
/// also in the execution's touched list.
#[derive(Debug, Default)]
struct SealLog {
    cit: String,
    resealed: Vec<String>,
    left_unsealed: Vec<Value>,
}

impl SealLog {
    fn op_name(&self, kind: &str) -> String {
        format!("cit execute {}: {kind}", self.cit)
    }
    fn record(&mut self, path: &str, was_verified: bool, sealed: bool, why: &str) {
        if sealed {
            self.resealed.push(path.to_string());
        } else if was_verified {
            self.left_unsealed
                .push(json!({"path": path, "reason": why}));
        }
    }
    fn to_value(&self) -> Value {
        json!({"resealed": self.resealed, "left_unsealed": self.left_unsealed,
            "rule": "a record whose T2 seal verified before the write is re-sealed when the write is one the OS may seal as its own (bookkeeping, or a governed content change outside operation-owned facts); otherwise it stays unsealed and the path is in the touched list (cit::binding::reseal_if_verified)"})
    }
}

/// After a `write_file` op replaced a record wholesale: re-seal it as the transaction's write when the record at that
/// path was sealed and verified before, and a whole-record rewrite of its type is one the OS may seal
/// ([`binding::content_write_entitled`]). Returns whether it sealed.
fn reseal_rewritten_file(p: &Project, path: &str, was_verified: bool, op: &str) -> Result<bool> {
    if !was_verified {
        return Ok(false);
    }
    let Some(mut r) = std::fs::read_to_string(p.root.join(path))
        .ok()
        .and_then(|t| parse_record_text(&t, path))
        .filter(|r| r.problems.is_empty() && !r.id().is_empty())
    else {
        return Ok(false);
    };
    if !binding::content_write_entitled(&r.rtype(), None) {
        return Ok(false);
    }
    binding::reseal_if_verified(&mut r, was_verified, true, op)?;
    save_record(&p.root, &r)?;
    Ok(true)
}

fn apply_op(p: &Project, op: &Value, touched: &mut Vec<String>, seals: &mut SealLog) -> Result<()> {
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
            // O-7: was this record OS state the OS can vouch for before the transaction wrote into it?
            let was_verified = binding::verified_before(r);
            let entitled = match kind {
                "mark_stale" => true,
                "set_status" => binding::content_write_entitled(&r.rtype(), Some("status")),
                _ => binding::content_write_entitled(&r.rtype(), op["field"].as_str()),
            };
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
            let sealed =
                binding::reseal_if_verified(r, was_verified, entitled, &seals.op_name(kind))?;
            seals.record(&r.path, was_verified, sealed, if entitled { "" } else { "a governed content change of facts only the record's own operation establishes is not sealed as the OS's own" });
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
            // O-7: a sealed record the transaction replaces wholesale
            let was_verified =
                p.root.join(path).is_file() && crate::t2::verify_file(&p.root, path).is_verified();
            let old_type = std::fs::read_to_string(p.root.join(path))
                .ok()
                .and_then(|t| parse_record_text(&t, path))
                .map(|r| r.rtype())
                .unwrap_or_default();
            write_text(&p.root.join(path), content)?;
            let sealed = reseal_rewritten_file(
                p,
                path,
                was_verified && binding::content_write_entitled(&old_type, None),
                &seals.op_name(kind),
            )?;
            seals.record(
                path,
                was_verified,
                sealed,
                "a wholesale rewrite of a record whose facts only its own operation establishes is not sealed as the OS's own",
            );
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
            // an appended record is the transaction's content, never replayed OS state: a seal or sealed CIT state
            // carried in the manifest (copied from another record) is not written
            if let Some(o) = r.data.as_object_mut() {
                o.remove(crate::t2::SEAL_FIELD);
                o.remove(binding::STATE_FIELD);
            }
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
        // INT3-O1: a plugin registration is written only here, by its change transaction's execution; the
        // registration re-derives the request from the bytes as they are now, requires exactly the subject this
        // transaction's approval binds, and re-verifies the execution approval (Contract v3 F4)
        "register_plugin" => {
            let r = crate::capabilities::governance::apply_registration(p, op, &seals.cit)?;
            for t in r["touched"].as_array().cloned().unwrap_or_default() {
                if let Some(t) = t.as_str() {
                    touched.push(t.to_string());
                }
            }
        }
        // R4-O1: a tool installation is written only here, by its change transaction's execution; the installation
        // re-derives the request from the bytes as they are now, requires exactly the subject this transaction's
        // approval binds, and re-verifies the installation's own approval where one was needed (Contract v3 F4)
        "install_tool" => {
            let r = crate::tools::apply_installation(p, op, &seals.cit)?;
            for t in r["touched"].as_array().cloned().unwrap_or_default() {
                if let Some(t) = t.as_str() {
                    touched.push(t.to_string());
                }
            }
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

/// Refusals of the retrieval profile itself, as the indexer raises them: the pinned embedder or reranker cannot run
/// as pinned (not registered or approved as declared, not usable by the acting role, another revision or identity
/// than the pin, unavailable). A declared plugin that is not usable is refused naming it (`PluginSet::refusal`).
fn is_retrieval_profile_refusal(e: &GovError) -> bool {
    e.code.starts_with("EMBEDDER_")
        || e.code.starts_with("RERANKER_")
        || e.code.starts_with("PLUGIN_")
        || e.details
            .get("plugin_id")
            .and_then(|v| v.as_str())
            .is_some()
}

/// CIT-E: snapshot -> apply -> propagate -> regenerate -> refresh index -> verify -> commit or rollback.
pub fn execute(p: &Project, db: &RuntimeDb, id: &str) -> Result<Value> {
    execute_with(p, db, id, None)
}

/// [`execute`] under the authority of an OS host operation (see [`approve_with`]).
fn execute_with(p: &Project, db: &RuntimeDb, id: &str, authority: Option<&str>) -> Result<Value> {
    control::guard_write(p, "cit execute")?;
    crate::authority::require(p, authority.unwrap_or("execute_cit"))?;
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
    if st.secret_flagged {
        return Err(GovError::new("SECRET_IN_MANIFEST", format!("{id} was flagged at proposal time because its proposal/manifest contained secret material (redacted); gov sealed that flag, so it cannot be executed whatever the record now says. Re-propose without secrets (store them in a secret-class path).")).with_details(json!({"sealed_state": "secret_flagged"})));
    }
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
    // J2 (WS-10 IP-WS10-09): a promotion revoked, or experimental bytes produced, after approval stop execution
    promotion_check(p, &store, &rec)?;
    // ---- propagation is planned before anything is applied, so the snapshot covers every record it will touch
    let changed = changed_record_ids(p, &store, &rec.data);
    let before_hashes: Vec<(String, Option<String>)> = changed
        .iter()
        .map(|c| (c.clone(), propagation::record_hash(&p.root, &store, c)))
        .collect();
    let plan = propagation::plan(p, &store, &changed, Some(&rec.data["impact"]), None);
    let snapshot = take_snapshot(p, id, &rec.data, &store, &plan.paths(p, &store))?;
    // verification compares against a FRESH pre-execution baseline (A0-K2-03): damage already in the working tree but
    // not yet indexed is not attributed to this transaction. A baseline the retrieval profile refused to build is
    // remembered: the same refusal after the manifest is not this transaction's damage either (below)
    let mut pre_refresh: Option<GovError> = None;
    if pol.get_bool("CHANGE_POLICY", "propagation.refresh_index", true) {
        if let Err(e) = crate::memory::indexer::rebuild(
            p,
            crate::memory::indexer::IndexOptions {
                incremental: true,
                ..Default::default()
            },
        ) {
            pre_refresh = Some(e);
        }
    }
    let dangling_before: std::collections::BTreeSet<String> = graph::dangling_edges(db)?
        .iter()
        .map(|e| e.to_string())
        .collect();
    // relationship integrity before the manifest (WS-6 IP-R2-2): what the transaction may not make worse
    let integrity_before = integrity_keys(p);
    let mut s = RecordStore::load(&p.root);
    {
        let r = s.get_mut(id).unwrap();
        r.set("cit_status", json!("EXECUTING"));
        r.set("execution", json!({"started": now_iso(), "snapshot": snapshot, "session": p.session_id, "role": p.role, "gate": approval["gate"], "decision": approval["decision"], "approval_method": approval["method"]}));
        journal(
            r,
            json!({"at": now_iso(), "event": "executing", "gate": approval["gate"], "decision": approval["decision"], "session": p.session_id}),
        );
        binding::seal(r, st.carried("EXECUTING"), "cit execute")?;
        save_record(&p.root, r)?;
    }
    let mut touched = vec![];
    let mut created: Vec<String> = vec![];
    let mut seals = SealLog {
        cit: id.to_string(),
        ..Default::default()
    };
    let result: Result<Value> = (|| {
        // paths the manifest's content ops wrote (not its staleness marks or deletions): the records whose declared
        // relationships the transaction answers for
        let mut content_written: Vec<String> = vec![];
        let mut integrity_report = Value::Null;
        for op in rec.data["mutation_manifest"]
            .as_array()
            .cloned()
            .unwrap_or_default()
        {
            let from = touched.len();
            apply_op(p, &op, &mut touched, &mut seals)?;
            if !matches!(op["op"].as_str(), Some("mark_stale") | Some("delete_file")) {
                content_written.extend(touched[from..].iter().cloned());
            }
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
        // K2 memory/index refresh. A0-K2-03 for the index itself: when the retrieval profile refused to build the index
        // before the manifest was applied as well (the pinned embedder or reranker cannot run as pinned — e.g. a
        // registration of its next revision, which the profile's pin then refuses), the refusal is not attributed to
        // this transaction: it is recorded, the index stays as it was (index_freshness keeps reporting it), and the
        // freshness verification, which could not pass before either, is not what decides this commit. Any other
        // refresh failure, or a refusal this transaction introduced, fails the verification as before.
        let mut index_refresh = json!({"refreshed": true});
        if pol.get_bool("CHANGE_POLICY", "propagation.refresh_index", true) {
            match crate::memory::indexer::rebuild(
                p,
                crate::memory::indexer::IndexOptions {
                    incremental: true,
                    ..Default::default()
                },
            ) {
                Ok(_) => {}
                Err(e)
                    if is_retrieval_profile_refusal(&e)
                        && pre_refresh
                            .as_ref()
                            .map(is_retrieval_profile_refusal)
                            .unwrap_or(false) =>
                {
                    let b = pre_refresh.as_ref().unwrap();
                    index_refresh = json!({"refreshed": false, "code": e.code, "message": e.message,
                        "before": {"code": b.code, "message": b.message},
                        "rule": "A0-K2-03: the retrieval profile refused to build the index before this transaction was applied as well; the refusal is not attributed to it, the index stays as it was and index_freshness reports it"});
                }
                Err(e) => return Err(e),
            }
        } else {
            index_refresh = json!({"refreshed": false, "reason": "CHANGE_POLICY.propagation.refresh_index is false"});
        }
        let refusal_pre_existing = index_refresh.get("before").is_some();
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
            // WS-6 IP-R2-2: relationships the transaction itself declared must be well-typed, in the direction of
            // their meaning and not point at non-current records; it must not create a supersession cycle
            let (introduced, consequences) =
                integrity_introduced(p, &integrity_before, &content_written, &changed);
            integrity_report = json!({"introduced": introduced, "consequences": consequences,
                "rule": "memory::integrity::check before and after the manifest: a new reversed, ill-typed or stale relationship declared by a record this transaction's content ops wrote (stale: to a target it did not itself change), or a new supersession cycle, fails the verification; new stale relationships of other records to a target this transaction retired are its propagation's consequences"});
            if !introduced.is_empty() {
                problems.push(format!(
                    "{} relationship integrity finding(s) introduced by records this transaction wrote: {}",
                    introduced.len(),
                    introduced
                        .iter()
                        .map(|f| f["message"].as_str().unwrap_or("").to_string())
                        .collect::<Vec<_>>()
                        .join(" | ")
                ));
            }
        }
        if required.iter().any(|r| r == "index_freshness") && !refusal_pre_existing {
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
        v["index_refresh"] = index_refresh;
        v["relationship_integrity"] = integrity_report;
        v["t2_seals"] = seals.to_value();
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
                    writes_sha256: Some(binding::writes_digest(&writes_v)),
                    ..st.carried("COMMITTED")
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
            // whole-record seal is renewed only when the committed record still verifies (O-7: a hand edit made after
            // the commit stays broken). The index is refreshed again so the committed transaction leaves it current.
            let mut s3 = RecordStore::load(&p.root);
            if let Some(r) = s3.get_mut(id) {
                let was_verified = binding::verified_before(r);
                let mut ex = r.data["execution"].clone();
                ex["health"] = health.clone();
                r.set("execution", ex);
                binding::reseal_if_verified(r, was_verified, true, "cit execute (G4 health)")?;
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
                binding::seal(r, st.carried("ROLLED_BACK"), "cit execute")?;
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

/// Relationship-integrity findings (`memory::integrity::check`, WS-6 BC-P2-28) that are not `low`, keyed for a
/// before/after comparison by kind, declaring record and edge. Dangling edges are left to the index-based check CIT-E
/// already runs beside it.
fn integrity_keys(p: &Project) -> std::collections::BTreeMap<String, Value> {
    let store = RecordStore::load(&p.root);
    match crate::memory::integrity::check(p, &store, None) {
        Ok(i) => i
            .findings
            .into_iter()
            .filter(|f| f["severity"] != "low" && f["kind"] != "dangling")
            .map(|f| {
                let key = format!(
                    "{}|{}|{}|{}",
                    f["kind"], f["record"], f["edge"], f["records"]
                );
                (key, f)
            })
            .collect(),
        Err(_) => Default::default(),
    }
}

/// The relationship-integrity findings a transaction introduced and answers for (WS-6 IP-R2-2), and the new findings
/// that are consequences of it:
/// * **introduced** — a new `reversed` or `ill_typed` relationship declared by a record the manifest's content ops
///   wrote; a new `stale` relationship declared by such a record to a target the transaction did not itself change
///   (it pointed new content at a record that was already not current); a new `supersession_cycle`;
/// * **consequences** — every other new finding, e.g. current records still pointing at a record this transaction
///   superseded: propagation marks their work for retest, and the suite reports the links.
fn integrity_introduced(
    p: &Project,
    before: &std::collections::BTreeMap<String, Value>,
    content_written: &[String],
    changed: &[String],
) -> (Vec<Value>, Vec<Value>) {
    let after = integrity_keys(p);
    let store = RecordStore::load(&p.root);
    let written: std::collections::BTreeSet<String> = content_written
        .iter()
        .filter_map(|pth| {
            store
                .records
                .iter()
                .find(|r| r.path == *pth)
                .map(|r| r.id())
        })
        .collect();
    let (mut introduced, mut consequences) = (vec![], vec![]);
    for (k, f) in after {
        if before.contains_key(&k) {
            continue;
        }
        let kind = f["kind"].as_str().unwrap_or("");
        let declarer = f["record"].as_str().unwrap_or("");
        let own = written.contains(declarer);
        let target = {
            let (s, d) = (
                f["edge"]["src"].as_str().unwrap_or(""),
                f["edge"]["dst"].as_str().unwrap_or(""),
            );
            if s == declarer {
                d.to_string()
            } else {
                s.to_string()
            }
        };
        let answerable = match kind {
            "supersession_cycle" => true,
            "reversed" | "ill_typed" => own,
            "stale" => own && !changed.iter().any(|c| *c == target),
            _ => false,
        };
        if answerable {
            introduced.push(f);
        } else {
            consequences.push(f);
        }
    }
    (introduced, consequences)
}

/// **Propagate a change made outside CIT-E as a sealed system transaction** (BC-P2-04 direct path; WS-5 IP-R3-3;
/// integration O-7). Propagation writes OS markers into records it does not own — close reports, authored test
/// obligations, scenarios, tasks, checkpoints, handoffs — and a concurrent task close must be able to tell those
/// writes apart from a worker's (a changed authored obligation would otherwise be an undeclared mutation; an unsealed
/// or legacy report a T2 violation) and recorded authorship must survive them. Re-sealing covers records whose seal
/// verified; for the rest, the OS records the paths in a transaction's touched list: this function writes a
/// `COMMITTED` CIT record of `origin: system`, `trigger: propagation`, with no mutation manifest (it changes no
/// authoritative content), whose `execution.propagation.touched` and sealed per-path `execution.writes` are exactly
/// what the propagation wrote. It is taken with a rollback snapshot and journalled like CIT-E (an interruption is
/// recovered by `gov recover`); when the propagation writes nothing, no record is kept. Returns the propagation
/// summary with `cit` naming the transaction (or `null`).
pub fn propagate_as_transaction(
    p: &Project,
    plan: &propagation::Plan,
    changes: &[propagation::InputChange],
    detected_by: &str,
    opts: &propagation::ApplyOptions,
) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let id = store.next_id("cit");
    let cause = propagation::Cause::Direct {
        detected_by: detected_by.to_string(),
    };
    let ids: Vec<String> = changes.iter().map(|c| c.id.clone()).collect();
    let targets: Vec<String> = ids
        .iter()
        .filter(|i| store.get(i).is_some())
        .cloned()
        .collect();
    let approval = json!({"method": "policy", "policy": "CHANGE_POLICY.propagation", "human_approved": false, "answered_by_kind": "system",
        "basis": "propagation of a detected upstream change writes OS bookkeeping only (staleness, retest and revalidation marks, packet invalidation); it changes no authoritative content, so CHANGE_POLICY.propagation authorises it without a gate",
        "recorded_by_session": p.session_id, "recorded_by_role": p.role, "at": now_iso()});
    let impact = json!({"radius": "R0", "human_gate_required": false, "seeds": ids, "affected": [], "affected_tasks": plan.open_tasks.keys().chain(plan.done_tasks.keys()).cloned().collect::<Vec<_>>(),
        "tests_required": plan.tests.keys().cloned().collect::<Vec<_>>(), "features": [], "material_classes": [], "effective_triggers": [],
        "consequences": ["bookkeeping only: dependents of the changed input(s) are marked stale / for retest or revalidation"]});
    let mut rec = new_record(
        "cit",
        &id,
        &format!("Propagation of a direct change to {}", ids.join(", ")),
        json!({"cit_status": "EXECUTING", "origin": "system", "trigger": "propagation", "proposed_by": p.role,
            "proposal": format!("propagate upstream change(s) to {} detected by {detected_by} (made outside change control) to the work that consumed the previous content", ids.join(", ")),
            "targets": targets, "mutation_manifest": [], "impact": impact, "approval": approval, "state_class": "AUTHORITATIVE",
            "system": {"kind": "direct-change propagation", "detected_by": detected_by, "cause": cause.to_value(),
                "inputs_changed": changes.iter().map(|c| c.to_value(&cause)).collect::<Vec<_>>()},
            "journal": [{"at": now_iso(), "event": "system_propagation", "detected_by": detected_by, "session": p.session_id}]}),
    );
    p.schemas().validate("cit", &rec.data, &format!("({id})"))?;
    let snapshot = take_snapshot(p, &id, &rec.data, &store, &plan.paths(p, &store))?;
    rec.set("execution", json!({"started": now_iso(), "snapshot": snapshot, "session": p.session_id, "role": p.role, "cause": cause.to_value()}));
    let content = binding::content_digest(&rec.data);
    let state = CitState {
        content_sha256: content,
        impact_sha256: Some(binding::impact_digest(&rec.data["impact"])),
        approval_sha256: Some(binding::approval_digest(&rec.data["approval"])),
        ..Default::default()
    };
    binding::seal(
        &mut rec,
        state.carried("EXECUTING"),
        "cit propagate (system)",
    )?;
    save_record(&p.root, &rec)?;
    let mut touched = vec![];
    let mut created = vec![];
    let applied = propagation::apply(p, plan, changes, &cause, opts, &mut touched, &mut created);
    let _ = register_created(p, &id, &created);
    let mut s2 = RecordStore::load(&p.root);
    let Some(r) = s2.get_mut(&id) else {
        return Err(GovError::new(
            "CIT_NOT_FOUND",
            format!("the propagation transaction {id} vanished while it executed"),
        ));
    };
    match applied {
        Ok(mut v) if touched.is_empty() && created.is_empty() => {
            // nothing was written (every change was already recorded): no transaction to keep
            let _ = std::fs::remove_file(p.root.join(&r.path));
            let _ = crate::util::remove_dir_if_exists(&snapshot_dir(p, &id));
            v["cit"] = Value::Null;
            v["touched"] = json!([]);
            Ok(v)
        }
        Ok(mut v) => {
            v["touched"] = json!(touched.clone());
            let mut all = touched.clone();
            all.extend(created.iter().cloned());
            let writes_v = json!(binding::capture_writes(&p.root, &all)
                .iter()
                .map(|w| w.to_value())
                .collect::<Vec<_>>());
            let mut ex = r.data["execution"].clone();
            ex["finished"] = json!(now_iso());
            ex["result"] = json!("committed");
            ex["verification"] =
                json!({"ok": true, "note": "bookkeeping only: no authoritative content changed"});
            ex["propagation"] = v.clone();
            ex["writes"] = writes_v.clone();
            r.set("execution", ex);
            r.set("cit_status", json!("COMMITTED"));
            journal(r, json!({"at": now_iso(), "event": "committed"}));
            binding::seal(
                r,
                CitState {
                    writes_sha256: Some(binding::writes_digest(&writes_v)),
                    ..state.carried("COMMITTED")
                },
                "cit propagate (system)",
            )?;
            save_record(&p.root, r)?;
            v["cit"] = json!(id);
            Ok(v)
        }
        Err(e) => {
            let rb = restore_snapshot(p, &id)?;
            let mut ex = r.data["execution"].clone();
            ex["finished"] = json!(now_iso());
            ex["result"] = json!("rolled_back");
            ex["error"] = json!(e.to_string());
            r.set("execution", ex);
            r.set("cit_status", json!("ROLLED_BACK"));
            journal(
                r,
                json!({"at": now_iso(), "event": "rolled_back", "error": e.to_string()}),
            );
            binding::seal(r, state.carried("ROLLED_BACK"), "cit propagate (system)")?;
            save_record(&p.root, r)?;
            Err(GovError::new(
                &e.code,
                format!(
                    "{} — the propagation transaction {id} was rolled back",
                    e.message
                ),
            )
            .with_details(json!({"cit": id, "rollback": rb, "details": e.details})))
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
        .map(|c| json!({"id": c.id(), "cit_status": c.get("cit_status"), "state": binding::binding_of(c), "record_seal": crate::t2::verify_record(c).code()}))
        .collect()
}

/// CHANGE_POLICY.rollback.keep_snapshots: keep only the newest N CIT snapshot directories (older transactions cannot be
/// rolled back automatically afterwards; git history remains).
pub fn prune_snapshots(p: &Project, keep: usize) {
    let base = snapshot_base(p);
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
        // rolling back is the fail-safe direction: sealed whatever the record's prior binding was (a ROLLED_BACK
        // transaction covers nothing and authorises nothing)
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
                secret_flagged: prev.as_ref().map(|s| s.secret_flagged).unwrap_or(false),
                ..Default::default()
            },
            "cit rollback",
        )?;
        save_record(&p.root, r)?;
    }
    // the approval decision no longer describes the project (verifier L7): mark it REJECTED with provenance. The
    // rollback is the decision's own lifecycle operation, so a decision whose seal verified before is re-sealed as
    // written by it (WS-2 R3-1): the OS's rollback never makes its own decision look tampered with, and a decision
    // edited by hand before the rollback stays unsealed
    let mut decision_resealed = Value::Null;
    if !decision_id.is_empty() {
        let mut s3 = RecordStore::load(&p.root);
        if let Some(d) = s3.get_mut(&decision_id) {
            let was_verified = binding::verified_before(d);
            d.set("status", json!("REJECTED"));
            d.set("state_class", json!("HISTORICAL"));
            d.set("rollback_of", json!(id));
            d.set("updated", json!(crate::util::today()));
            let sealed = binding::reseal_if_verified(d, was_verified, true, "cit rollback")?;
            decision_resealed =
                json!({"decision": decision_id, "resealed": sealed, "sealed_before": was_verified});
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
    Ok(
        json!({"cit": id, "cit_status": "ROLLED_BACK", "rollback": rb, "approval_decision": decision_resealed}),
    )
}

pub fn interrupted(p: &Project) -> Vec<Value> {
    RecordStore::load(&p.root).of_type("cit").into_iter().filter(|c| c.get("cit_status") == "EXECUTING").map(|c| json!({"id": c.id(), "started": c.data["execution"]["started"], "session": c.data["execution"]["session"], "snapshot_present": snapshot_dir(p, &c.id()).join("snapshot.json").exists()})).collect()
}

// ------------------------------------------------------------------ a plugin registration as a change transaction

/// **A plugin registration is carried out by a change transaction the OS proposes** (INT3-O1, WS-5 × WS-7; Contract
/// v3 K3 "auto-trigger for material: … security, governance/policy"; F4 "elevated permissions reference
/// authoritative gate/decision"; framework §47-48 "the human should not need to type /impact"). A registration writes
/// the plugin's descriptor under `governance/project/plugins/` and its sealed registry entry: a material governance
/// and security change (`materiality`). `gov plugins register` therefore proposes this transaction itself (no worker
/// hand-files it), with one manifest operation, `register_plugin`, whose content — the normalised descriptor and the
/// registration subject — the transaction's approval binds. CIT-P is simulated automatically and raises the
/// transaction's own gate under CHANGE_POLICY. The plugin's **execution** approval stays what it was (the gate raised
/// for exactly the registration subject, `capabilities::governance`), and it names this transaction and its gate; this
/// transaction's gate approves the **change**. Neither answer stands in for the other. CIT-E writes the registration
/// ([`crate::capabilities::governance::apply_registration`]), so a registration made inside a claimed task closes on
/// the transaction's recorded writes (task close step 10a) like any other governed change.
///
/// `origin: system`, `system.kind: plugin-registration` (OS-owned fields: [`propose`] strips them from proposer input).
pub fn propose_registration(
    p: &Project,
    op: Value,
    proposal: &str,
    plugin_id: &str,
    subject: &str,
) -> Result<Value> {
    let targets: Vec<Value> = ["path", "registry"]
        .iter()
        .filter_map(|k| op[*k].as_str().map(|s| json!(s)))
        .collect();
    let fields = json!({"proposal": proposal, "title": format!("Register capability plugin {plugin_id}"),
        "trigger": "security_change", "targets": targets, "mutation_manifest": [op]});
    let os = json!({"origin": "system", "system": {"kind": "plugin-registration", "operation": "plugins register",
        "plugin_id": plugin_id, "registration_subject_sha256": subject,
        "note": "proposed by the OS for a `gov plugins register` request (Contract v3 K3): the registration is written only by this transaction's execution; the plugin's execution approval is the gate raised for exactly the registration subject"}});
    propose_inner(p, fields, Some(os), "register_plugin", true)
}

/// **A tool installation is carried out by a change transaction the OS proposes** (R4-O1, the adjacent path
/// P2-AR-0043 left open beside INT3-O1; Contract v3 K3 "auto-trigger for material: … security, governance/policy";
/// F4 "elevated permissions reference authoritative gate/decision"; framework §47-48 "the human should not need to
/// type /impact"). `gov tools install` writes the tool's descriptor under `governance/project/tools/` — a governed
/// path the kernel-floor materiality classifies exactly as it classifies a plugin descriptor, and which a task close
/// refuses as a material change made outside change control. So the installation proposes this transaction itself
/// (no worker hand-files it), with one manifest operation, `install_tool`, whose content — the descriptor as given,
/// the installation subject, the installing role and whether the install command runs — the transaction's approval
/// binds. CIT-P is simulated automatically and raises the transaction's own gate under CHANGE_POLICY. The
/// installation's **own** approval stays what it was (the gate raised for exactly the installation subject when an
/// auto-install condition failed, `tools::install`), and it names this transaction and its gate; this transaction's
/// gate approves the **change**. Neither answer stands in for the other. CIT-E writes the descriptor
/// ([`crate::tools::apply_installation`]), so an installation made inside a claimed task closes on the transaction's
/// recorded writes (task close step 10a) like any other governed change.
///
/// `origin: system`, `system.kind: tool-installation` (OS-owned fields: [`propose`] strips them from proposer input).
pub fn propose_installation(
    p: &Project,
    op: Value,
    proposal: &str,
    tool_id: &str,
    subject: &str,
) -> Result<Value> {
    let targets: Vec<Value> = ["path", "registry"]
        .iter()
        .filter_map(|k| op[*k].as_str().map(|s| json!(s)))
        .collect();
    let fields = json!({"proposal": proposal, "title": format!("Install tool {tool_id}"),
        "trigger": "security_change", "targets": targets, "mutation_manifest": [op]});
    let os = json!({"origin": "system", "system": {"kind": "tool-installation", "operation": "tools install",
        "tool_id": tool_id, "installation_subject_sha256": subject,
        "note": "proposed by the OS for a `gov tools install` request (Contract v3 K3): the tool descriptor is written only by this transaction's execution; the installation's own approval, when an auto-install condition failed, is the gate raised for exactly the installation subject"}});
    propose_inner(p, fields, Some(os), "install_tool", true)
}

/// Statuses of a transaction that is still a request (not finished).
pub fn is_open_status(s: &str) -> bool {
    matches!(s, "PROPOSED" | "SIMULATED" | "APPROVED")
}

/// **The manifest operations the OS itself proposes for a host operation**, each the whole manifest of its own
/// transaction: a capability plugin's registration (INT3-O1) and a tool installation (R4-O1). Both write governed
/// files under the OS-managed/project-plugin prefixes, so both are material governance changes that complete only
/// through change control, and for both the host — not the worker — files the transaction.
pub const HOST_PROPOSED_OPS: &[&str] = &["register_plugin", "install_tool"];

/// The one `op` operation of a host-proposed transaction that is exactly that operation (`None` for anything else).
fn host_op_of(c: &Record, op: &str) -> Option<Value> {
    let m = c.data["mutation_manifest"].as_array()?;
    (m.len() == 1 && m[0]["op"] == op).then(|| m[0].clone())
}

/// The host-proposed `op` transactions of exactly this subject whose state gov sealed, newest first:
/// `(id, cit_status)`.
pub fn host_transactions(p: &Project, op: &str, subject: &str) -> Vec<(String, String)> {
    let store = RecordStore::load(&p.root);
    let mut v: Vec<(String, String)> = store
        .of_type("cit")
        .into_iter()
        .filter(|c| {
            host_op_of(c, op)
                .map(|o| o["subject_sha256"].as_str() == Some(subject))
                .unwrap_or(false)
                && binding::verified_state(c)
                    .map(|st| st.cit_status == c.get("cit_status"))
                    .unwrap_or(false)
        })
        .map(|c| (c.id(), c.get("cit_status")))
        .collect();
    v.sort_by(|a, b| b.0.cmp(&a.0));
    v
}

/// End the open host-proposed `op` transactions whose `id_field` is `id` (and, when given, of exactly `subject`):
/// the request they carry ended (its own approval was declined). Each is marked REJECTED with a sealed state.
/// Returns their ids.
pub fn close_host_requests(
    p: &Project,
    op: &str,
    id_field: &str,
    id: &str,
    subject: Option<&str>,
    why: &str,
) -> Vec<String> {
    let store = RecordStore::load(&p.root);
    let ids: Vec<String> = store
        .of_type("cit")
        .into_iter()
        .filter(|c| is_open_status(&c.get("cit_status")))
        .filter(|c| {
            host_op_of(c, op)
                .map(|o| {
                    o[id_field].as_str() == Some(id)
                        && subject
                            .map(|s| o["subject_sha256"].as_str() == Some(s))
                            .unwrap_or(true)
                })
                .unwrap_or(false)
        })
        .map(|c| c.id())
        .collect();
    ids.into_iter()
        .filter(|id| reject_sealed(p, id, why).is_ok())
        .collect()
}

/// Journal, on a host-proposed transaction, the subject approval gate raised for what it carries (the transaction's
/// side of the cross-reference; the gate's package names the transaction and its gate). `note` says which approval
/// that gate is. The journal is not part of the content an approval binds; the record is re-sealed only when it
/// verified before.
pub fn note_host_gate(p: &Project, cit: &str, gate: &str, note: &str, operation: &str) {
    let mut s = RecordStore::load(&p.root);
    if let Some(c) = s.get_mut(cit) {
        let was = crate::t2::verify_record(c).is_verified();
        journal(
            c,
            json!({"at": now_iso(), "event": "subject_approval_gate_raised", "gate": gate, "note": note}),
        );
        if crate::t2::seal_if_verified(c, was, &format!("{operation} (cit note)")).is_ok() {
            let _ = save_record(&p.root, c);
        }
    }
}

/// Where the approval of a host-proposed transaction stands.
#[derive(Debug, Clone, PartialEq)]
pub enum GateState {
    /// Its gate waits on an answer (a withdrawn gate is raised again by re-simulating: the request was repeated).
    Pending(String),
    /// Its gate was answered with a non-authorising option: the change is refused.
    Declined(String),
    /// Approved already, or answered and ready to approve; approve/execute decide the rest, typed.
    Ready,
}

pub fn host_gate_state(p: &Project, cit: &str) -> GateState {
    let store = RecordStore::load(&p.root);
    let Some(c) = store.get(cit) else {
        return GateState::Ready;
    };
    if c.get("cit_status") != "SIMULATED" {
        return GateState::Ready;
    }
    let g = c.get("human_gate");
    if g.is_empty() {
        return GateState::Ready;
    }
    match gates::verified_answer(p, &g) {
        Ok(a) if a.authorises_blocked_work => GateState::Ready,
        Ok(_) => GateState::Declined(g),
        Err(e) if e.code == "GATE_NOT_ANSWERED" => GateState::Pending(g),
        Err(e) if e.code == "GATE_REVOKED" => {
            // the owner withdrew the question and the request is repeated: simulate again, which raises a fresh gate
            // for the transaction as it stands (a withdrawn gate is never reused)
            let fresh = RuntimeDb::open(&p.db_path())
                .and_then(|db| db.init_schema().map(|_| db))
                .and_then(|db| simulate_inner(p, &db, cit));
            match fresh
                .ok()
                .and_then(|v| v["human_gate"].as_str().map(String::from))
            {
                Some(ng) => GateState::Pending(ng),
                None => GateState::Ready,
            }
        }
        Err(_) => GateState::Ready,
    }
}

/// Approve (from its gate's verified answer) and execute a host-proposed transaction, under the authority of the
/// host operation (`authority`) that proposed it and whose content it is. Refused for any transaction that is not
/// exactly one `op` operation, so this path executes nothing but that host operation, and CIT-E re-verifies the
/// subject's own approval (Contract v3 F4) before it writes.
pub fn execute_host_op(p: &Project, id: &str, op: &str, authority: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let c = load_cit(&store, id)?;
    if host_op_of(&c, op).is_none() {
        return Err(GovError::new(
            "USAGE",
            format!("{id} is not a host-proposed {op} transaction (exactly one {op} operation)"),
        ));
    }
    if c.get("cit_status") == "SIMULATED" {
        let gate = c.get("human_gate");
        let method = if !gate.is_empty()
            && gates::verified_answer(p, &gate)
                .map(|a| a.by_kind == "human")
                .unwrap_or(false)
        {
            "human"
        } else {
            "auto"
        };
        approve_with(p, id, &p.role.clone(), method, Some(authority))?;
    }
    let db = RuntimeDb::open(&p.db_path())?;
    db.init_schema()?;
    execute_with(p, &db, id, Some(authority))
}

pub fn list(p: &Project) -> Vec<Value> {
    RecordStore::load(&p.root).of_type("cit").into_iter().map(|c| json!({"id": c.id(), "title": c.title(), "cit_status": c.get("cit_status"), "trigger": c.get("trigger"), "effective_trigger": c.data["materiality"]["effective_trigger"], "radius": c.data["impact"]["radius"], "human_gate": c.get("human_gate"), "decision": c.get("decision"), "state": binding::binding_of(c), "origin": c.data.get("origin").cloned().unwrap_or(json!("proposer")), "record_seal": crate::t2::verify_record(c).code()})).collect()
}

pub fn read_text_opt(p: &Path) -> Option<String> {
    read_text(p).ok()
}
