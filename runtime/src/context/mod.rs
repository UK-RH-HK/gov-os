//! Context compiler (framework §15; Contract v3 W4 lines 1106-1112, W10 lines 1162-1171; BC-P2-19).
//!
//! A packet has three separately hashed parts:
//!
//! * **`deterministic_authority`** (`deterministic_hash`) — the task contract and every mandatory input the task's
//!   manifest resolves ([`manifest`]), each delivered with its **normative content** (the whole record and, for
//!   Markdown records, its body), its exact id, declared `version` and SHA-256 `content_hash`, its authority class,
//!   whether it is required and why. Resolved from the governed records only, so it is identical whether or not
//!   the derived index exists, and it changes whenever any supplied content changes.
//! * **`input_manifest`** (`manifest_hash`) — the resolution itself: what was declared, what each id resolved to,
//!   what is missing or violated, and the packet's `delivery_state` (`COMPLETE` | `BLOCKED`). A missing required
//!   input is never silently dropped: it is named here and the packet is `BLOCKED` (W4 line 1112).
//! * **`retrieved_intelligence`** — supplementary context only: task-declared `supplementary_context` and
//!   semantic/lexical/graph/code retrieval. A retrieval or index failure (absent, corrupt or re-pinned index,
//!   unavailable reranker) **degrades only this block**, explicitly (`supplementary_state: DEGRADED` with the
//!   reasons); the mandatory inputs are still delivered (W10 line 1170, INV-010). Token pressure drops only this
//!   block (W4 line 1109).
//!
//! `packet_hash` covers all of it plus the receipt contract; `input_hashes` lists every supplied input's hash and
//! `provenance` binds the packet to the repository commit it was compiled at. Every packet is kept under
//! `.governance-runtime/context/packets/<task>/<packet_hash>.json`, so a packet hash recorded in a checkpoint,
//! handoff or consumption receipt resolves back to exactly what was supplied ([`load_packet`]).
pub mod contradictions;
pub mod manifest;
pub mod receipt;

use crate::memory::db::RuntimeDb;
use crate::orchestration::control;
use crate::records::{Record, RecordStore};
use crate::retrieval::{retrieve, RetrieveOptions};
use crate::util::{hash_value, now_iso, sorted, write_json};
use crate::{GovError, Project, Result};
use manifest::{Entry, Manifest, Slot};
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

/// One delivered input: its identity, its normative content and its manifest annotation.
fn input_value(r: &Record, e: &Entry) -> Value {
    let mut v = brief(r);
    // the lifecycle state the manifest judged (an archived record is HISTORICAL whatever its field says)
    v["status"] = json!(e.status);
    v["content"] = sorted(&r.data);
    if !r.body.is_empty() {
        v["body"] = json!(r.body);
    }
    v["version"] = json!(e.version);
    v["content_hash"] = json!(e.content_hash);
    v["state_class"] = json!(e.state_class);
    v["required"] = json!(e.required);
    v["reason"] = e.reason();
    v["declared_in"] = json!(e.sources);
    if let Some(f) = &e.authority_flag {
        v["authority_flag"] = json!(f);
    }
    if let Some(s) = &e.superseded_by {
        v["superseded_by"] = json!(s);
    }
    if !e.problems.is_empty() {
        v["problems"] = e.problems_value();
    }
    if !e.duplicate_paths.is_empty() {
        v["duplicate_paths"] = json!(e.duplicate_paths);
    }
    v
}

/// An authority flag that makes a decision conflicting rather than active: superseded, not current, ambiguous,
/// contradicted by another current input (BC-P2-18), or set aside by a contradiction's resolution.
fn currency_flag(f: &str) -> bool {
    f == "UNKNOWN_OR_CONFLICTING"
        || f == "AMBIGUOUS_DUPLICATE_ID"
        || f == "CONTRADICTORY"
        || f == "SET_ASIDE_BY_RESOLUTION"
        || crate::graph::lineage::NON_CURRENT_STATUSES.contains(&f)
}

/// Delivered inputs whose records carry an upstream-change staleness marker, and the task's own markers
/// (`cit::propagation`, BC-P2-04): the worker sees what is stale without any lookup. Deterministic (records only).
fn input_staleness(m: &Manifest, store: &RecordStore, task: &Record) -> Value {
    let stale: Vec<Value> = m
        .entries
        .iter()
        .filter(|e| e.delivered())
        .filter_map(|e| store.get(&e.id).map(|r| (e, r)))
        .filter(|(_, r)| r.data["staleness"]["stale"].as_bool() == Some(true))
        .map(|(e, r)| json!({"id": e.id, "slot": e.slot.name(), "staleness": r.data["staleness"]}))
        .collect();
    json!({"stale_inputs": stale,
        "task_retest_required": task.data.get("retest_required").cloned().unwrap_or(json!(false)),
        "task_staleness": task.data.get("staleness").cloned().unwrap_or(Value::Null),
        "task_revalidation": task.data.get("revalidation").cloned().unwrap_or(Value::Null)})
}

/// Open the runtime index the way every command does (creating an empty store when none exists).
pub fn open_index(p: &Project) -> Result<RuntimeDb> {
    let d = RuntimeDb::open(&p.db_path())?;
    d.init_schema()?;
    Ok(d)
}

/// The derived index as the compiler sees it: open, or unavailable with the reason it could not be opened.
/// Existing callers pass `&RuntimeDb` unchanged (`From<&RuntimeDb>`).
pub enum IndexHandle<'a> {
    Open(&'a RuntimeDb),
    Unavailable(GovError),
}

impl<'a> From<&'a RuntimeDb> for IndexHandle<'a> {
    fn from(d: &'a RuntimeDb) -> Self {
        IndexHandle::Open(d)
    }
}

/// Compile the packet for `task_id`, opening the index itself and **tolerating its absence or damage**: the
/// mandatory inputs never depend on the index (W10 line 1170). Use this at every dispatch boundary.
///
/// Dispatch is also where the product observes what the delivery changes (repair iteration 1, round 2):
/// * every unresolved contradiction among the task's mandatory inputs is **routed** to its Human Decision Gate
///   before the packet is compiled (BC-P2-18; `contradictions::route_for_task`), so the packet names the gate;
/// * when a previous packet of the task delivered different input versions, that packet is **invalidated** (its
///   history copy carries `invalidated` with the inputs that changed) and the new packet records `redelivery`
///   (BC-P2-04 "affected context packets are invalidated");
/// * a task that never started work is **acknowledged** current once the packet delivers every changed input at its
///   current version (`cit::propagation::acknowledge_on_redelivery`).
pub fn compile_tolerant(p: &Project, task_id: &str) -> Result<Value> {
    let previous = crate::util::read_json(
        &p.runtime_dir()
            .join("context")
            .join(format!("{task_id}.json")),
    )
    .ok();
    let routed = contradictions::route_for_task(p, task_id);
    let mut packet = match open_index(p) {
        Ok(db) => compile(p, &db, task_id)?,
        Err(e) => compile(p, IndexHandle::Unavailable(e), task_id)?,
    };
    if routed.as_array().map(|a| !a.is_empty()).unwrap_or(false) {
        packet["contradiction_routing"] = routed;
    }
    if let Some(prev) = previous {
        // compared on normative content when both packets carry it (bookkeeping on an input is not a change)
        let key = if prev.get("input_normative_hashes").is_some() {
            "input_normative_hashes"
        } else {
            "input_hashes"
        };
        let old = prev[key].as_object().cloned().unwrap_or_default();
        let new = packet[key].as_object().cloned().unwrap_or_default();
        let mut changed: Vec<Value> = vec![];
        for (id, h) in &old {
            if new.get(id) != Some(h) {
                changed.push(json!({"id": id, "delivered": h, "current": new.get(id)}));
            }
        }
        for (id, h) in &new {
            if !old.contains_key(id) {
                changed.push(json!({"id": id, "delivered": Value::Null, "current": h}));
            }
        }
        if !changed.is_empty() {
            let prev_hash = prev["packet_hash"].as_str().unwrap_or("").to_string();
            let hist = packets_dir(p, task_id).join(format!("{prev_hash}.json"));
            if let Ok(mut h) = crate::util::read_json(&hist) {
                if h.get("invalidated").map(|v| v.is_null()).unwrap_or(true) {
                    h["invalidated"] = json!({"at": now_iso(), "cause": {"kind": "redelivery", "superseded_by_packet": packet["packet_hash"]}, "inputs": changed,
                        "remediation": "this packet no longer delivers the task's current inputs; work done against it must be revalidated"});
                    let _ = write_json(&hist, &h);
                }
            }
            packet["redelivery"] = json!({"previous_packet": prev_hash, "previous_compiled_at": prev["compiled_at"], "inputs_changed": changed,
                "previous_invalidated": prev.get("invalidated").cloned().unwrap_or(Value::Null)});
            write_json(
                &p.runtime_dir()
                    .join("context")
                    .join(format!("{task_id}.json")),
                &packet,
            )?;
        }
    }
    if let Ok(true) = crate::cit::propagation::acknowledge_on_redelivery(p, task_id, &packet) {
        packet["acknowledged_redelivery"] = json!(true);
    }
    Ok(packet)
}

fn degradation(stage: &str, e: &GovError) -> Value {
    json!({"stage": stage, "code": e.code, "message": e.message})
}

/// The supplementary block: retrieval over the derived index. Never fails; failures are recorded as degradations.
fn retrieved_block(p: &Project, db: IndexHandle, query: &str, k: usize) -> (Value, Vec<Value>) {
    let mut degr = vec![];
    let mut ret = json!({"query": query, "retrieval_strategy": Value::Null, "routes": [], "index_snapshot": {"index_version": Value::Null, "manifest_hash": Value::Null},
        "ranked_evidence": [], "semantic_candidates": [], "lessons_failures": [], "code_references": []});
    let db = match db {
        IndexHandle::Open(d) => d,
        IndexHandle::Unavailable(e) => {
            degr.push(degradation("open_index", &e));
            return (ret, degr);
        }
    };
    match retrieve(
        p,
        db,
        query,
        RetrieveOptions {
            k,
            log: true,
            ..Default::default()
        },
    ) {
        Ok(res) => {
            ret["retrieval_strategy"] = json!(res.strategy);
            ret["routes"] = json!(res.routes);
            ret["index_snapshot"] = json!({"index_version": res.index_version, "manifest_hash": res.index_manifest_hash});
            ret["ranked_evidence"] = json!(res.hits.iter().map(|h| json!({"artifact_id": h.artifact_id, "path": h.path, "section": h.section, "score": h.score, "routes": h.routes, "status": h.status, "state_class": h.state_class, "excerpt": h.excerpt, "parent_excerpt": h.parent_excerpt, "neighbours": h.neighbours, "flags": h.flags})).collect::<Vec<_>>());
            // framework §15.2 "semantic candidates" (CONTEXT_POLICY.retrieved_fields): the admitted candidates the
            // semantic route contributed, as references into ranked_evidence (same order; content is not repeated)
            ret["semantic_candidates"] = json!(res.hits.iter().filter(|h| h.routes.iter().any(|r| r == "semantic")).map(|h| json!({"artifact_id": h.artifact_id, "path": h.path, "section": h.section, "score": h.score})).collect::<Vec<_>>());
        }
        Err(e) => degr.push(degradation("retrieve", &e)),
    }
    match retrieve(
        p,
        db,
        query,
        RetrieveOptions {
            k: 5,
            record_types: vec!["lesson".into(), "report".into()],
            ..Default::default()
        },
    ) {
        Ok(lessons) => {
            ret["lessons_failures"] = json!(lessons
                .hits
                .iter()
                .map(
                    |h| json!({"artifact_id": h.artifact_id, "path": h.path, "excerpt": h.excerpt})
                )
                .collect::<Vec<_>>());
        }
        Err(e) => degr.push(degradation("retrieve_lessons", &e)),
    }
    let mut code_refs = vec![];
    for tok in crate::memory::embeddings::tokenize(query)
        .into_iter()
        .filter(|t| t.len() > 3)
        .take(12)
    {
        match db.query(
            "SELECT path, qualname, kind FROM symbols WHERE name=?1 LIMIT 3",
            &[&tok],
        ) {
            Ok(rows) => code_refs.extend(rows),
            Err(e) => {
                degr.push(degradation("code_references", &e));
                break;
            }
        }
    }
    ret["code_references"] = json!(code_refs);
    (ret, degr)
}

/// Paths among `paths` with changes not committed at `HEAD` (or `None` when git cannot tell).
fn uncommitted(p: &Project, paths: &[String]) -> Option<Vec<String>> {
    if paths.is_empty() {
        return Some(vec![]);
    }
    let mut a: Vec<&str> = vec!["diff", "--name-only", "HEAD", "--"];
    a.extend(paths.iter().map(|s| s.as_str()));
    let (c1, changed, _) = p.git(&a);
    let mut b: Vec<&str> = vec!["ls-files", "--others", "--exclude-standard", "--"];
    b.extend(paths.iter().map(|s| s.as_str()));
    let (c2, untracked, _) = p.git(&b);
    if c1 != 0 || c2 != 0 {
        return None;
    }
    let mut out: Vec<String> = changed
        .lines()
        .chain(untracked.lines())
        .map(|l| l.trim().to_string())
        .filter(|l| !l.is_empty())
        .collect();
    out.sort();
    out.dedup();
    Some(out)
}

fn packets_dir(p: &Project, task_id: &str) -> std::path::PathBuf {
    p.runtime_dir()
        .join("context")
        .join("packets")
        .join(task_id)
}

/// Compile the context packet for `task_id`. `db` is the open index (`&RuntimeDb`) or
/// [`IndexHandle::Unavailable`]; only the supplementary block depends on it.
pub fn compile<'a>(p: &Project, db: impl Into<IndexHandle<'a>>, task_id: &str) -> Result<Value> {
    let db: IndexHandle<'a> = db.into();
    let store = RecordStore::load(&p.root);
    let task = store
        .get(task_id)
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("task {task_id} not found")))?;
    if task.rtype() != "task" {
        return Err(GovError::new("USAGE", format!("{task_id} is not a task")));
    }
    let pol = p.policies();
    let m: Manifest = manifest::resolve(p, &store, task);
    let delivered = |slot: Slot| -> Vec<Value> {
        m.in_slot(slot)
            .into_iter()
            .filter(|e| e.delivered())
            .filter_map(|e| store.get(&e.id).map(|r| input_value(r, e)))
            .collect()
    };
    let feature = m
        .in_slot(Slot::Feature)
        .into_iter()
        .find(|e| e.delivered())
        .and_then(|e| store.get(&e.id).map(|r| input_value(r, e)));
    // authority precedence (framework §2/§21): a superseded, non-current or ambiguous decision is never active
    // authority; it is delivered flagged in conflicting_decisions
    let (mut active_decisions, mut conflicting): (Vec<Value>, Vec<Value>) = (vec![], vec![]);
    for d in delivered(Slot::Decision) {
        if d["authority_flag"]
            .as_str()
            .map(currency_flag)
            .unwrap_or(false)
        {
            conflicting.push(d);
        } else {
            active_decisions.push(d);
        }
    }
    active_decisions.sort_by(|a, b| a["id"].as_str().cmp(&b["id"].as_str()));
    conflicting.sort_by(|a, b| a["id"].as_str().cmp(&b["id"].as_str()));
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
    let scenarios = delivered(Slot::Scenario);
    let mut acceptance: Vec<Value> = vec![];
    for s in &scenarios {
        let sid = s["id"].as_str().unwrap_or("");
        if let Some(r) = store.get(sid) {
            for c in r.list("success_criteria") {
                acceptance.push(json!({"scenario": sid, "criterion": c}));
            }
            for c in r.list("then") {
                acceptance.push(json!({"scenario": sid, "then": c}));
            }
        }
    }
    for t in task.list("acceptance_tests") {
        acceptance.push(json!({"test": t}));
    }
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
        "feature": feature, "governing_requirements": delivered(Slot::Requirement), "active_decisions": active_decisions, "conflicting_decisions": conflicting,
        "architecture": delivered(Slot::Architecture), "interfaces": delivered(Slot::Interface), "scenarios": scenarios,
        "test_designs": delivered(Slot::TestDesign), "datasets": delivered(Slot::Dataset), "evidence_inputs": delivered(Slot::Evidence), "other_inputs": delivered(Slot::Other),
        "acceptance_criteria": acceptance, "allowed_writes": task.list("allowed_paths"), "prohibited_writes": prohibited, "required_skills": skills, "required_tools": task.list("required_tools"),
        "dependency_state": dependency_state, "minimum_model_tier": task.get("minimum_model_tier"), "minimum_reasoning": task.get("minimum_reasoning"),
        // BC-P2-18: contradictions among the inputs and how each stands (members are never active authority while unresolved)
        "contradictions": m.contradictions,
        // BC-P2-04: which delivered inputs, and whether the task itself, carry an upstream-change staleness marker
        "input_staleness": input_staleness(&m, &store, task),
        // WS-5 IP-1: the enforcement state of the task contract (required data/tools/skills, blocked_by, designated
        // role, production-merge permission, mutation scope)
        "task_contract": crate::orchestration::tasks::contract_enforcement(p, &store, task),
    });
    let det = sorted(&det);
    let det_hash = hash_value(&det);
    let manifest_v = sorted(&m.to_value());
    let manifest_hash = hash_value(&manifest_v);
    let contract = sorted(&receipt::contract_for(p, &store, task_id, &m));
    // ---- supplementary block (never authority; failures degrade only this block)
    let query = format!("{} {}", task.title(), task.get("objective"));
    let k = pol.get_i64("CONTEXT_POLICY", "max_retrieved_slices", 12) as usize;
    let (mut ret, degradations) = retrieved_block(p, db, &query, k);
    ret["declared_supplementary"] = json!(m.supplementary);
    if !degradations.is_empty() {
        ret["degraded"] = json!({"state": "DEGRADED", "reasons": degradations,
            "effect": "supplementary retrieval is unavailable or partial; the deterministic authority block and the input manifest are resolved from governed records and are complete (Contract v3 W10 line 1170, INV-010)",
            "remediation": "gov rebuild-memory (or restore the pinned embedder/reranker), then recompile for supplementary context"});
    }
    // CONTEXT_POLICY.max_packet_chars: bound the packet deterministically by dropping supplementary slices from the
    // tail; the mandatory blocks are never displaced (W4 line 1109)
    let max = pol.get_i64("CONTEXT_POLICY", "max_packet_chars", 60000) as usize;
    let mandatory_len = serde_json::to_string(&det)?.len()
        + serde_json::to_string(&manifest_v)?.len()
        + serde_json::to_string(&contract)?.len();
    let mut truncated = 0usize;
    loop {
        let total = mandatory_len + serde_json::to_string(&ret)?.len() + 400;
        if total <= max {
            break;
        }
        let mut dropped = false;
        for key in [
            "semantic_candidates",
            "code_references",
            "lessons_failures",
            "ranked_evidence",
            "declared_supplementary",
        ] {
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
    // the content hashes of the delivered inputs; task dependencies are not content inputs (their record changes
    // with every status transition; `dependency_state` carries what the task needs of them)
    let input_hashes: serde_json::Map<String, Value> = m
        .entries
        .iter()
        .filter(|e| e.delivered() && e.slot != manifest::Slot::Dependency)
        .filter_map(|e| e.content_hash.clone().map(|h| (e.id.clone(), json!(h))))
        .collect();
    // the same inputs' normative hashes (bookkeeping excluded): what upstream-change staleness is judged on
    let input_normative_hashes: serde_json::Map<String, Value> = m
        .entries
        .iter()
        .filter(|e| e.delivered() && e.slot != manifest::Slot::Dependency)
        .filter_map(|e| e.normative_hash.clone().map(|h| (e.id.clone(), json!(h))))
        .collect();
    let input_paths: Vec<String> = m
        .entries
        .iter()
        .filter(|e| e.delivered())
        .map(|e| e.path.clone())
        .collect();
    let mut packet = json!({"packet_id": format!("CTX-{}-{}", task_id, &det_hash[..8]), "task": task_id,
        "delivery_state": m.delivery_state(),
        "supplementary_state": if degradations.is_empty() { "COMPLETE" } else { "DEGRADED" },
        "deterministic_authority": det, "deterministic_hash": det_hash,
        "input_manifest": manifest_v, "manifest_hash": manifest_hash, "input_hashes": input_hashes, "input_normative_hashes": input_normative_hashes,
        "receipt_contract": contract,
        "retrieved_intelligence": ret, "index_version": crate::INDEX_VERSION});
    let ph = hash_value(
        &json!({"d": packet["deterministic_authority"], "m": packet["input_manifest"], "c": packet["receipt_contract"], "r": packet["retrieved_intelligence"]}),
    );
    packet["packet_hash"] = Value::String(ph.clone());
    packet["provenance"] = json!({"repo_commit": p.git_commit(), "inputs_uncommitted": uncommitted(p, &input_paths),
        "compiler": {"runtime_version": crate::RUNTIME_VERSION, "index_version": crate::INDEX_VERSION},
        "index_available": packet["supplementary_state"] == "COMPLETE"});
    packet["compiled_at"] = Value::String(now_iso());
    let chars = serde_json::to_string(&packet)?.len();
    packet["chars"] = json!(chars);
    packet["budget"] = json!({"max_packet_chars": max, "mandatory_chars": mandatory_len, "dropped_supplementary_slices": truncated, "over_budget": chars > max});
    if chars > max {
        packet["warning"] = json!(format!("the mandatory blocks alone (deterministic authority, input manifest, receipt contract: {mandatory_len} chars) exceed CONTEXT_POLICY.max_packet_chars ({chars} > {max}); mandatory inputs are never displaced — split the task"));
    }
    // the packet is held to its own published contract (framework/schemas/context-packet.schema.json)
    if p.schemas().has("context-packet") {
        p.schemas().validate(
            "context-packet",
            &packet,
            &format!("(packet for {task_id})"),
        )?;
    }
    write_json(
        &p.runtime_dir()
            .join("context")
            .join(format!("{task_id}.json")),
        &packet,
    )?;
    write_json(&packets_dir(p, task_id).join(format!("{ph}.json")), &packet)?;
    Ok(packet)
}

/// The packet last compiled for `task_id` (`hash = None`), or the packet with that `packet_hash` (full hash or a
/// prefix of at least 12 characters) from the packet history.
pub fn load_packet(p: &Project, task_id: &str, hash: Option<&str>) -> Result<Value> {
    let not_found = |what: String| {
        GovError::new(
            "PACKET_NOT_FOUND",
            format!("{what}; run `gov context compile {task_id}`"),
        )
    };
    match hash {
        None => crate::util::read_json(
            &p.runtime_dir()
                .join("context")
                .join(format!("{task_id}.json")),
        )
        .map_err(|_| not_found(format!("no packet has been compiled for {task_id}"))),
        Some(h) => {
            let h = h.trim();
            if h.len() < 12 || !h.chars().all(|c| c.is_ascii_hexdigit()) {
                return Err(not_found(format!(
                    "'{h}' is not a packet hash (at least 12 hex characters)"
                )));
            }
            let dir = packets_dir(p, task_id);
            let exact = dir.join(format!("{h}.json"));
            if exact.exists() {
                return crate::util::read_json(&exact);
            }
            let mut hits: Vec<std::path::PathBuf> = std::fs::read_dir(&dir)
                .map(|rd| {
                    rd.filter_map(|e| e.ok())
                        .map(|e| e.path())
                        .filter(|pth| {
                            pth.file_name()
                                .map(|n| n.to_string_lossy().starts_with(h))
                                .unwrap_or(false)
                        })
                        .collect()
                })
                .unwrap_or_default();
            hits.sort();
            match hits.len() {
                1 => crate::util::read_json(&hits[0]),
                0 => Err(not_found(format!(
                    "no packet {h} was compiled for {task_id} on this machine"
                ))),
                n => Err(GovError::new(
                    "PACKET_AMBIGUOUS",
                    format!("{n} packets of {task_id} start with {h}; give more of the hash"),
                )),
            }
        }
    }
}

/// **Delivery verification** (W4 lines 1110-1112, W10 line 1171 "independently testable"): is the packet still a
/// faithful delivery of the task's declared inputs? Re-resolves the manifest now and checks that every required
/// input is delivered with its current content hash, that the deterministic block still hashes to
/// `deterministic_hash`, and that the packet was not compiled blocked. Integration point for the checkpoint/handoff and full-audit
/// context-delivery checks (`verification::run` context family, WS-2).
pub fn verify_delivery(p: &Project, packet: &Value) -> Result<Value> {
    let task_id = packet["task"].as_str().unwrap_or("").to_string();
    let store = RecordStore::load(&p.root);
    let m = manifest::resolve_task(p, &store, &task_id)?;
    let det = &packet["deterministic_authority"];
    let det_ok = hash_value(det) == packet["deterministic_hash"].as_str().unwrap_or("");
    let supplied = packet["input_hashes"]
        .as_object()
        .cloned()
        .unwrap_or_default();
    // staleness is judged on normative content when the packet carries it (bookkeeping on an input is not a change)
    let normative = packet["input_normative_hashes"].as_object().cloned();
    let mut undelivered = vec![];
    let mut stale = vec![];
    for e in m
        .entries
        .iter()
        .filter(|e| e.required && e.slot != manifest::Slot::Dependency)
    {
        match supplied.get(&e.id).and_then(|v| v.as_str()) {
            None => undelivered
                .push(json!({"id": e.id, "slot": e.slot.name(), "resolution_now": e.resolution})),
            Some(h) => {
                let changed = match &normative {
                    Some(n) => n.get(&e.id).and_then(|v| v.as_str()) != e.normative_hash.as_deref(),
                    None => Some(h) != e.content_hash.as_deref(),
                };
                if changed {
                    stale.push(json!({"id": e.id, "supplied": h, "current": e.content_hash, "normative_supplied": normative.as_ref().and_then(|n| n.get(&e.id).cloned()), "normative_current": e.normative_hash}));
                }
            }
        }
    }
    let invalidated = packet.get("invalidated").filter(|v| !v.is_null()).cloned();
    let ok = det_ok
        && undelivered.is_empty()
        && stale.is_empty()
        && invalidated.is_none()
        && packet["delivery_state"] == "COMPLETE"
        && m.satisfied();
    Ok(
        json!({"task": task_id, "ok": ok, "packet_hash": packet["packet_hash"], "deterministic_hash_verified": det_ok,
        "declared_inputs": m.entries.iter().filter(|e| e.required).count(), "delivery_state_at_compile": packet["delivery_state"],
        "delivery_state_now": m.delivery_state(), "undelivered_inputs": undelivered, "stale_inputs": stale,
        "invalidated": invalidated, "contradictions_now": m.contradictions,
        "missing_inputs_now": m.missing(), "input_violations_now": m.violations()}),
    )
}

/// Refuse to dispatch a packet whose mandatory inputs are unsatisfied (W4 line 1112). Integration point for
/// `status::continue_work` and handoff creation (WS-5 / BC-P2-05).
pub fn ensure_dispatchable(packet: &Value) -> Result<()> {
    if let Some(inv) = packet.get("invalidated").filter(|v| !v.is_null()) {
        let task = packet["task"].as_str().unwrap_or("?");
        return Err(GovError::new(
            "PACKET_INVALIDATED",
            format!("the context packet for {task} was invalidated by an upstream change: it no longer delivers the current inputs; recompile it (`gov context compile {task}`) before dispatch"),
        )
        .with_details(json!({"task": task, "invalidated": inv, "packet_hash": packet["packet_hash"]})));
    }
    if packet["delivery_state"] == "COMPLETE" {
        return Ok(());
    }
    let task = packet["task"].as_str().unwrap_or("?");
    Err(GovError::new(
        "INPUT_MANIFEST_UNSATISFIED",
        format!("the context packet for {task} is BLOCKED: its mandatory inputs are not all satisfied; it cannot be dispatched. `gov context manifest {task}` names what is missing"),
    )
    .with_details(json!({"task": task, "missing_inputs": packet["input_manifest"]["missing_inputs"], "input_violations": packet["input_manifest"]["input_violations"], "packet_hash": packet["packet_hash"]})))
}
