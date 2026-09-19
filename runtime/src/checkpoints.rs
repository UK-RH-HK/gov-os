//! Checkpoints (framework §59-60): structured resumable state, never a prose summary. Provider-independent watchdog.
//!
//! ## Repair iteration 1, round 2 (WS-4, BC-P2-05; Contract v3:717-742, :1154-1160)
//!
//! * **Mandatory-input continuity.** A checkpoint of a task records the task's mandatory inputs — id, slot, version,
//!   the SHA-256 of the input now and the hash the task's packet delivered (`inputs`) — and the delivery state
//!   (`input_state`: manifest state, packet hash, stale/missing inputs, contradictions). Every checkpoint records a
//!   **state reference current at checkpoint time** (`state_reference`: commit, governed-record digest, and the index
//!   reference taken *after* bringing the index current).
//! * **Staleness.** [`freshness`] derives whether the material state a checkpoint captured still holds (its inputs,
//!   its task's status, the pending decisions, the open transactions); upstream-change propagation also marks affected
//!   checkpoints `staleness` (`cit::propagation`). `gov checkpoint latest` and `gov checkpoint freshness` report it.
//! * **Triggers observed by the product, not the agent.** Every checkpoint records `observed_state` (task statuses,
//!   material decisions, the model-routing map, a mutation mark) and the mandatory triggers that occurred since the
//!   previous checkpoint (`triggers_observed`). [`observe_boundaries`] turns triggers nobody checkpointed into
//!   checkpoints (task transition, material decision, significant mutation, model/provider switch); the watchdog and
//!   session close call it, and hosts call it at their own boundaries (integration points in the WS-4 round-2 report).
//! * **The watchdog counts execution boundaries itself** ([`watchdog`]): gov commands executed since the last
//!   checkpoint (the product's own telemetry) and repository files changed since it; caller-supplied counters can only
//!   make it fire earlier.
//! * **Session close** ([`session_close`], `gov session close`) writes the `before_session_close` checkpoint and is
//!   explicitly degraded when the session's work has stale, missing or contradictory mandatory inputs.
//! * **Tier contract.** A checkpoint runs the G3 tier (`scheduler::tier_run`, IP-WS02-07) and records the result; a
//!   checkpoint is a remedy and is never refused for health.
use crate::memory::db::RuntimeDb;
use crate::orchestration::{claims, control};
use crate::records::{new_record, save_record, Record, RecordStore};
use crate::util::{canonical_json, now_iso, read_json, read_yaml, sha256_hex, write_yaml};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

pub fn dir(p: &Project) -> std::path::PathBuf {
    p.root.join(
        p.policies()
            .get_str("CHECKPOINT_POLICY", "location", "spec/reports/checkpoints"),
    )
}

/// Session-close / handoff freshness policy (kernel floor, stated here and reported in every result that applies
/// it): a handoff whose mandatory inputs are unsatisfied is **refused**; a handoff whose delivered packet is stale is
/// **re-delivered** at the current inputs and, when work was already in progress on the stale inputs, **explicitly
/// degraded**; a session close is never refused (the session ends) but is **explicitly degraded** when the session's
/// work has stale, missing or contradictory mandatory inputs.
pub const FRESHNESS_POLICY: &str = "handoff: unsatisfied mandatory inputs -> refused (HANDOFF_INPUTS_UNSATISFIED); stale packet -> re-delivered at current inputs, degraded when work was in progress on the stale inputs; session close: never refused, degraded when the session's work has stale/missing/contradictory mandatory inputs (checkpoints::FRESHNESS_POLICY)";

/// Top-level gov commands that only inspect: they are not operations the watchdog counts.
const INSPECTION_COMMANDS: &[&str] = &[
    "cli.status",
    "cli.version",
    "cli.doctor",
    "cli.telemetry",
    "cli.checkpoint",
    "cli.session",
];

/// Repository files changed (tracked modified/added/deleted and untracked), from `git status --porcelain -z`.
pub fn working_tree_changes(p: &Project) -> Vec<String> {
    let Some(out) = crate::cit::materiality::git_output(
        &p.root,
        &["status", "--porcelain=v1", "-z", "--untracked-files=all"],
    ) else {
        return vec![];
    };
    let mut v = vec![];
    let mut it = out.split('\0').filter(|e| !e.is_empty());
    while let Some(e) = it.next() {
        if e.len() < 4 {
            continue;
        }
        let (st, path) = (&e[..2], &e[3..]);
        v.push(path.to_string());
        if st.starts_with('R') || st.starts_with('C') {
            it.next();
        }
    }
    v.retain(|x| !x.starts_with(".governance-runtime/"));
    v.sort();
    v.dedup();
    v
}

fn rank(r: &str) -> u8 {
    r.trim_start_matches('R').parse().unwrap_or(0)
}

/// Decisions that are **material** (framework §60 "material decision"): a decision derived from a gate, a
/// human-approved decision, or one assessed at impact radius R2 or wider.
fn material_decisions(store: &RecordStore) -> Vec<String> {
    let mut v: Vec<String> = store
        .of_type("decision")
        .into_iter()
        .filter(|d| {
            d.list("derived_from").iter().any(|x| x.starts_with("HDG-"))
                || d.data.get("human_approved").and_then(|v| v.as_bool()) == Some(true)
                || rank(
                    d.data
                        .get("impact_radius")
                        .and_then(|v| v.as_str())
                        .unwrap_or("R0"),
                ) >= 2
        })
        .map(|d| d.id())
        .collect();
    v.sort();
    v
}

/// Digest of the model/provider routing the project would use (framework §60 "before model/provider switch"): the
/// effective MODEL_ROUTING_POLICY and the project's MODEL_ROUTING_OVERRIDES overlay.
fn routing_digest(p: &Project) -> String {
    let pol = p
        .policies()
        .effective
        .get("MODEL_ROUTING_POLICY")
        .cloned()
        .unwrap_or(Value::Null);
    let overlay = std::fs::read(
        p.root
            .join("governance")
            .join("project")
            .join("MODEL_ROUTING_OVERRIDES.yaml"),
    )
    .unwrap_or_default();
    sha256_hex(format!("{}\n{}", canonical_json(&pol), sha256_hex(&overlay)).as_bytes())
}

/// Digest of every governed record's bytes (spec/, governance/project/), checkpoints excluded: a state reference that
/// needs no index.
fn governed_state_digest(p: &Project, store: &RecordStore) -> String {
    let ck = p
        .policies()
        .get_str("CHECKPOINT_POLICY", "location", "spec/reports/checkpoints");
    let mut parts: Vec<String> = store
        .records
        .iter()
        .filter(|r| !r.path.starts_with(&ck))
        .map(|r| {
            let h = crate::util::read_bytes(&p.root.join(&r.path))
                .map(|b| sha256_hex(&b))
                .unwrap_or_default();
            format!("{}\u{1f}{h}", r.path)
        })
        .collect();
    parts.sort();
    sha256_hex(parts.join("\n").as_bytes())
}

/// What the product observes at a boundary (compared with the previous checkpoint's to find the mandatory triggers
/// that occurred in between).
pub fn observe_state(p: &Project, store: &RecordStore) -> Value {
    let tasks: BTreeMap<String, String> = store
        .of_type("task")
        .into_iter()
        .map(|t| (t.id(), t.get("task_status")))
        .collect();
    json!({
        "at": now_iso(),
        "task_states": tasks,
        "material_decisions": material_decisions(store),
        "routing_digest": routing_digest(p),
        "telemetry_events": crate::observability::events(p).len(),
    })
}

/// Files under the repository (runtime and `.git` excluded) modified after `since` (RFC 3339, UTC).
fn files_changed_since(p: &Project, since: &str) -> usize {
    let Ok(t) = chrono::DateTime::parse_from_rfc3339(since) else {
        return 0;
    };
    let since =
        std::time::UNIX_EPOCH + std::time::Duration::from_secs(t.timestamp().max(0) as u64 + 1);
    crate::paths::iter_repo_files(&p.root, false)
        .into_iter()
        .filter(|(_, rel)| !rel.starts_with(".git/") && !rel.starts_with(".governance-runtime/"))
        .filter(|(abs, _)| {
            std::fs::metadata(abs)
                .and_then(|m| m.modified())
                .map(|m| m >= since)
                .unwrap_or(false)
        })
        .count()
}

/// gov commands (excluding pure inspection) executed after `since`, from the product's own telemetry.
fn commands_since(p: &Project, since: &str) -> usize {
    crate::observability::events(p)
        .iter()
        .filter(|e| {
            let n = e["name"].as_str().unwrap_or("");
            n.starts_with("cli.")
                && !INSPECTION_COMMANDS.contains(&n)
                && e["timestamp"].as_str().unwrap_or("") > since
        })
        .count()
}

/// The mandatory triggers that occurred between the previous checkpoint's observed state and `now`.
fn triggers_between(p: &Project, prev: Option<&Value>, now: &Value) -> Vec<Value> {
    let Some(prev) = prev.filter(|v| v.is_object()) else {
        return vec![];
    };
    let mut out = state_triggers(prev, now);
    let since = prev["at"].as_str().unwrap_or("");
    let changed = files_changed_since(p, since);
    let threshold = p.policies().get_i64(
        "CHECKPOINT_POLICY",
        "watchdog.max_operations_between_checkpoints",
        25,
    ) as usize;
    if !since.is_empty() && changed >= threshold {
        out.push(json!({"trigger": "significant_mutation", "detail": format!("{changed} repository file(s) changed since the previous checkpoint (threshold {threshold}: CHECKPOINT_POLICY.watchdog.max_operations_between_checkpoints)")}));
    }
    out
}

/// The triggers visible in the observed state alone: task transitions, new material decisions, a routing change.
fn state_triggers(prev: &Value, now: &Value) -> Vec<Value> {
    let mut out = vec![];
    let empty = serde_json::Map::new();
    let old = prev["task_states"].as_object().unwrap_or(&empty);
    let transitions: Vec<Value> = now["task_states"]
        .as_object()
        .unwrap_or(&empty)
        .iter()
        .filter_map(|(id, st)| match old.get(id) {
            Some(was) if was != st => Some(json!({"task": id, "from": was, "to": st})),
            _ => None,
        })
        .collect();
    if !transitions.is_empty() {
        out.push(json!({"trigger": "task_transition", "detail": transitions}));
    }
    let was: BTreeSet<String> = prev["material_decisions"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    let new_decisions: Vec<String> = now["material_decisions"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect::<Vec<_>>()
        })
        .unwrap_or_default()
        .into_iter()
        .filter(|d| !was.contains(d))
        .collect();
    if !new_decisions.is_empty() {
        out.push(json!({"trigger": "material_decision", "detail": new_decisions}));
    }
    if prev["routing_digest"].is_string() && prev["routing_digest"] != now["routing_digest"] {
        out.push(json!({"trigger": "before_model_switch", "detail": "the effective model/provider routing changed since the previous checkpoint"}));
    }
    out
}

/// The mandatory-input state of `task_id` as the checkpoint records it: every declared input with the hash now and
/// the hash its packet delivered, and the delivery state.
pub fn task_inputs(p: &Project, store: &RecordStore, task_id: &str) -> Option<(Vec<Value>, Value)> {
    let t = store.get(task_id).filter(|t| t.rtype() == "task")?;
    let m = crate::context::manifest::resolve(p, store, t);
    let pk = read_json(
        &p.runtime_dir()
            .join("context")
            .join(format!("{task_id}.json")),
    )
    .ok();
    let delivered = pk
        .as_ref()
        .and_then(|k| k["input_hashes"].as_object().cloned())
        .unwrap_or_default();
    // staleness on normative content when the packet carries it (bookkeeping on an input is not a change)
    let delivered_norm = pk
        .as_ref()
        .and_then(|k| k["input_normative_hashes"].as_object().cloned());
    let mut stale = vec![];
    let inputs: Vec<Value> = m
        .entries
        .iter()
        .filter(|e| (e.delivered() || e.required) && e.slot != crate::context::manifest::Slot::Dependency)
        .map(|e| {
            let d = delivered.get(&e.id).and_then(|v| v.as_str()).map(String::from);
            let dn = delivered_norm
                .as_ref()
                .and_then(|n| n.get(&e.id))
                .and_then(|v| v.as_str())
                .map(String::from);
            let is_stale = pk.is_some()
                && match &delivered_norm {
                    Some(_) => dn.as_deref() != e.normative_hash.as_deref(),
                    None => d.as_deref() != e.content_hash.as_deref(),
                };
            if is_stale {
                stale.push(json!({"id": e.id, "delivered": d, "current": e.content_hash, "delivered_normative": dn, "current_normative": e.normative_hash}));
            }
            json!({"id": e.id, "slot": e.slot.name(), "required": e.required, "resolution": e.resolution, "version": e.version,
                   "content_hash": e.content_hash, "normative_hash": e.normative_hash, "delivered_hash": d,
                   "delivered_normative_hash": dn, "stale": is_stale})
        })
        .collect();
    let invalidated = pk
        .as_ref()
        .map(|k| k.get("invalidated").map(|v| !v.is_null()).unwrap_or(false))
        .unwrap_or(false);
    let state = json!({
        "task": task_id,
        "task_status": t.get("task_status"),
        "delivery_state": m.delivery_state(),
        "packet_hash": pk.as_ref().map(|k| k["packet_hash"].clone()).unwrap_or(Value::Null),
        "packet_compiled_at": pk.as_ref().map(|k| k["compiled_at"].clone()).unwrap_or(Value::Null),
        "packet_invalidated": invalidated,
        "packet_current": pk.is_some() && stale.is_empty() && !invalidated,
        "stale_inputs": stale,
        "missing_inputs": m.missing(),
        "input_violations": m.violations(),
        "contradictions": m.contradictions,
    });
    Some((inputs, state))
}

pub fn create(p: &Project, db: &RuntimeDb, mut fields: Value) -> Result<Value> {
    control::guard_write(p, "checkpoint")?;
    crate::authority::require(p, "checkpoint")?;
    let pol = p.policies();
    let triggers = pol.get_list("CHECKPOINT_POLICY", "mandatory_triggers");
    let trigger = fields
        .get("trigger")
        .and_then(|v| v.as_str())
        .unwrap_or("manual")
        .to_string();
    if trigger != "manual" && trigger != "watchdog" && !triggers.contains(&trigger) {
        return Err(GovError::new(
            "USAGE",
            format!("unknown checkpoint trigger '{trigger}' (policy triggers: {triggers:?})"),
        ));
    }
    let o = fields
        .as_object_mut()
        .ok_or_else(|| GovError::new("USAGE", "checkpoint fields must be an object"))?;
    o.retain(|_, v| !v.is_null());
    if o.get("next_action")
        .and_then(|v| v.as_str())
        .map(|s| s.is_empty())
        .unwrap_or(true)
    {
        return Err(GovError::new("USAGE", "checkpoint requires next_action"));
    }
    if pol.get_str(
        "CHECKPOINT_POLICY",
        "prose_summary_as_checkpoint",
        "prohibited",
    ) == "prohibited"
        && o.get("summary")
            .and_then(|v| v.as_str())
            .map(|s| s.len() > 2000)
            .unwrap_or(false)
    {
        return Err(GovError::new("CHECKPOINT_POLICY", "prose summaries are prohibited as checkpoints (CHECKPOINT_POLICY.prose_summary_as_checkpoint); use structured fields"));
    }
    // a state reference current at checkpoint time (W9 line 1156): the index is brought current first, so the
    // recorded index reference reflects a change made just before the checkpoint
    let mut index_ref = json!({"index_manifest_hash": Value::Null, "index_version": crate::INDEX_VERSION, "fresh": Value::Null});
    if p.db_path().exists() {
        let fr = crate::memory::manifest::freshness(p);
        let mut fresh = fr.fresh;
        if !fresh {
            fresh = crate::memory::indexer::rebuild(
                p,
                crate::memory::indexer::IndexOptions {
                    incremental: true,
                    ..Default::default()
                },
            )
            .is_ok();
        }
        index_ref = json!({"index_manifest_hash": db.get_meta("index_manifest_hash").unwrap_or(Value::Null), "index_version": crate::INDEX_VERSION, "fresh": fresh,
            "stale_before_checkpoint": fr.stale.len() + fr.added.len() + fr.removed.len()});
    }
    let store = RecordStore::load(&p.root);
    let seq = store.of_type("checkpoint").len() as i64 + 1;
    let id = format!("CKPT-{seq:05}");
    let prev = latest_record(p, &store);
    o.insert("session".into(), json!(p.session_id));
    o.insert("role".into(), json!(p.role));
    o.insert("sequence".into(), json!(seq));
    o.insert("trigger".into(), json!(trigger));
    o.entry("mode").or_insert(json!(control::state(p)["mode"]));
    let task = o
        .get("task")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string());
    if let Some(t) = &task {
        if let Ok(Some(c)) = claims::holder(p, t) {
            o.insert("claim".into(), c);
        }
    }
    let pending = crate::orchestration::gates::pending(p);
    o.entry("pending_decisions").or_insert(json!(pending
        .iter()
        .map(|g| g["id"].clone())
        .collect::<Vec<_>>()));
    o.entry("open_transactions").or_insert(json!(store
        .of_type("cit")
        .into_iter()
        .filter(|c| matches!(
            c.get("cit_status").as_str(),
            "PROPOSED" | "SIMULATED" | "APPROVED" | "EXECUTING"
        ))
        .map(|c| c.id())
        .collect::<Vec<_>>()));
    // open questions the OS knows of: pending gate questions and unresolved contradictions (framework §59)
    if !o.contains_key("open_questions") {
        let mut q: Vec<Value> = pending
            .iter()
            .map(|g| {
                json!(format!(
                    "{}: {}",
                    g["id"].as_str().unwrap_or("?"),
                    g["question"].as_str().unwrap_or("")
                ))
            })
            .collect();
        if let Some(t) = &task {
            if let Some((_, st)) = task_inputs(p, &store, t) {
                for c in st["contradictions"].as_array().cloned().unwrap_or_default() {
                    if c["blocks"].as_bool() == Some(true) {
                        q.push(json!(format!(
                            "contradiction {} ({}){}",
                            c["members"]
                                .as_array()
                                .map(|a| a
                                    .iter()
                                    .filter_map(|x| x.as_str())
                                    .collect::<Vec<_>>()
                                    .join(" vs "))
                                .unwrap_or_default(),
                            c["subject"].as_str().unwrap_or(""),
                            c["resolution"]["gate"]
                                .as_str()
                                .map(|g| format!(": gate {g}"))
                                .unwrap_or_default()
                        )));
                    }
                }
            }
        }
        o.insert("open_questions".into(), json!(q));
    }
    o.entry("files_changed")
        .or_insert(json!(working_tree_changes(p)));
    o.entry("tests_status").or_insert(json!("unknown"));
    if let Some(t) = &task {
        if let Some((inputs, st)) = task_inputs(p, &store, t) {
            o.entry("context_packet_hash")
                .or_insert(st["packet_hash"].clone());
            o.insert("task_status".into(), st["task_status"].clone());
            o.insert("inputs".into(), json!(inputs));
            o.insert("input_state".into(), st);
        }
    }
    let cph = o
        .get("context_packet_hash")
        .cloned()
        .filter(|v| !v.is_null())
        .unwrap_or(json!(""));
    o.insert("context_packet_hash".into(), cph);
    o.entry("memory_snapshot").or_insert(index_ref.clone());
    let observed = observe_state(p, &store);
    let prev_observed = prev.as_ref().map(|r| r.data["observed_state"].clone());
    let occurred = triggers_between(p, prev_observed.as_ref(), &observed);
    o.insert(
        "state_reference".into(),
        json!({"repo_commit": p.git_commit(), "governed_state_digest": governed_state_digest(p, &store), "index": index_ref, "taken_at": now_iso()}),
    );
    o.insert("observed_state".into(), observed);
    o.insert("triggers_observed".into(), json!(occurred));
    if let Some(pr) = &prev {
        let f = freshness_of(p, &store, pr);
        if f["state"] == "STALE" {
            o.insert(
                "supersedes_stale_checkpoint".into(),
                json!({"id": pr.id(), "reasons": f["reasons"]}),
            );
        }
    }
    // G3 (tier contract, IP-WS02-07): checkpoint continuity checks; a checkpoint is a remedy and is never refused
    if !crate::scheduler::sandbox::inside_sandbox() {
        let tr = crate::scheduler::Trigger::new("checkpoint.create");
        let tr = match &task {
            Some(t) => tr.with_subject(t),
            None => tr,
        };
        let h = match crate::scheduler::tier_run(p, crate::scheduler::Tier::G3, tr) {
            Ok(h) => {
                json!({"tier": "G3", "verdict": h["verdict"], "health_result": h["health_result"], "counts": h["counts"]})
            }
            Err(e) => json!({"tier": "G3", "error": {"code": e.code, "message": e.message}}),
        };
        o.insert("health".into(), h);
    }
    o.insert("state_class".into(), json!("EVIDENCE"));
    o.insert("created_at".into(), json!(now_iso()));
    let rec = new_record(
        "checkpoint",
        &id,
        &format!("Checkpoint {seq} ({trigger})"),
        Value::Object(o.clone()),
    );
    p.schemas()
        .validate("checkpoint", &rec.data, &format!("({id})"))?;
    let mut rec = rec;
    rec.path = format!(
        "{}/{id}.yaml",
        pol.get_str("CHECKPOINT_POLICY", "location", "spec/reports/checkpoints")
    );
    save_record(&p.root, &rec)?;
    write_yaml(
        &dir(p).join("LATEST.yaml"),
        &json!({"latest": id, "sequence": seq, "path": rec.path, "written_at": now_iso()}),
    )?;
    if p.db_path().exists() {
        let _ = crate::memory::indexer::rebuild(
            p,
            crate::memory::indexer::IndexOptions {
                incremental: true,
                ..Default::default()
            },
        );
    }
    Ok(rec.data)
}

fn latest_record(p: &Project, store: &RecordStore) -> Option<Record> {
    let ptr = read_yaml(&dir(p).join("LATEST.yaml")).ok()?;
    let id = ptr["latest"].as_str()?;
    store.get(id).cloned()
}

/// The latest checkpoint, with its derived [`freshness`] attached (not persisted).
pub fn latest(p: &Project) -> Option<Value> {
    let ptr = read_yaml(&dir(p).join("LATEST.yaml")).ok()?;
    let path = ptr["path"].as_str()?;
    let mut v = read_yaml(&p.root.join(path)).ok()?;
    let store = RecordStore::load(&p.root);
    if let Some(r) = ptr["latest"].as_str().and_then(|id| store.get(id)) {
        v["freshness"] = freshness_of(p, &store, r);
    }
    Some(v)
}

fn ids_of(v: &Value) -> BTreeSet<String> {
    v.as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| {
                    x.as_str()
                        .map(String::from)
                        .or_else(|| x["id"].as_str().map(String::from))
                })
                .collect()
        })
        .unwrap_or_default()
}

fn freshness_of(p: &Project, store: &RecordStore, ck: &Record) -> Value {
    let mut reasons: Vec<Value> = vec![];
    if ck.data["staleness"]["stale"].as_bool() == Some(true) {
        reasons.push(json!({"kind": "upstream_change", "detail": ck.data["staleness"]["inputs_changed"], "cause": ck.data["staleness"]["reason"]}));
    }
    let task = ck.get("task");
    if !task.is_empty() {
        if let Some(t) = store.get(&task) {
            let was = ck.get("task_status");
            if !was.is_empty() && was != t.get("task_status") {
                reasons.push(json!({"kind": "task_transition", "detail": format!("{task} was {was} and is {} now", t.get("task_status"))}));
            }
            let m = crate::context::manifest::resolve(p, store, t);
            let now: BTreeMap<String, Option<String>> = m
                .entries
                .iter()
                .map(|e| (e.id.clone(), e.content_hash.clone()))
                .collect();
            let now_norm: BTreeMap<String, Option<String>> = m
                .entries
                .iter()
                .map(|e| (e.id.clone(), e.normative_hash.clone()))
                .collect();
            for x in ck.data["inputs"].as_array().cloned().unwrap_or_default() {
                let id = x["id"].as_str().unwrap_or("");
                // compared on normative content when the checkpoint recorded it
                let (then, cur) = match x["normative_hash"].as_str() {
                    Some(h) => (Some(h.to_string()), now_norm.get(id).cloned().flatten()),
                    None => (
                        x["content_hash"].as_str().map(String::from),
                        now.get(id).cloned().flatten(),
                    ),
                };
                if !now.contains_key(id) {
                    reasons.push(json!({"kind": "input_no_longer_declared", "id": id}));
                } else if cur != then {
                    reasons.push(json!({"kind": "input_changed", "id": id, "recorded": then, "current": cur}));
                }
            }
        } else {
            reasons.push(
                json!({"kind": "task_missing", "detail": format!("{task} no longer exists")}),
            );
        }
    }
    let pending_now: BTreeSet<String> = crate::orchestration::gates::pending(p)
        .iter()
        .filter_map(|g| g["id"].as_str().map(String::from))
        .collect();
    let pending_then = ids_of(&ck.data["pending_decisions"]);
    if ck.data.get("pending_decisions").is_some() && pending_now != pending_then {
        reasons.push(json!({"kind": "pending_decisions_changed", "raised": pending_now.difference(&pending_then).collect::<Vec<_>>(), "no_longer_pending": pending_then.difference(&pending_now).collect::<Vec<_>>()}));
    }
    let open_now: BTreeSet<String> = store
        .of_type("cit")
        .into_iter()
        .filter(|c| {
            matches!(
                c.get("cit_status").as_str(),
                "PROPOSED" | "SIMULATED" | "APPROVED" | "EXECUTING"
            )
        })
        .map(|c| c.id())
        .collect();
    let open_then = ids_of(&ck.data["open_transactions"]);
    if ck.data.get("open_transactions").is_some() && open_now != open_then {
        reasons.push(json!({"kind": "open_transactions_changed", "opened": open_now.difference(&open_then).collect::<Vec<_>>(), "closed": open_then.difference(&open_now).collect::<Vec<_>>()}));
    }
    json!({"checkpoint": ck.id(), "state": if reasons.is_empty() { "CURRENT" } else { "STALE" }, "reasons": reasons,
        "note": "a checkpoint is stale when the material state it captured (its task's inputs and status, the pending decisions, the open transactions) has changed since"})
}

/// **Whether checkpoint `id` (default: the latest) still describes the material state it captured** (N3 "can mark
/// checkpoint stale when material state changed"; `gov checkpoint freshness`).
pub fn freshness(p: &Project, id: Option<&str>) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let ck = match id {
        Some(i) => store
            .get(i)
            .filter(|r| r.rtype() == "checkpoint")
            .cloned()
            .ok_or_else(|| {
                GovError::new("CHECKPOINT_NOT_FOUND", format!("{i} is not a checkpoint"))
            })?,
        None => latest_record(p, &store).ok_or_else(|| {
            GovError::new("CHECKPOINT_NOT_FOUND", "no checkpoint has been written")
        })?,
    };
    let mut v = freshness_of(p, &store, &ck);
    v["latest"] = json!(latest_record(p, &store).map(|r| r.id()));
    v["stale_checkpoints"] = json!(store
        .of_type("checkpoint")
        .into_iter()
        .filter(|c| c.data["staleness"]["stale"].as_bool() == Some(true))
        .map(|c| c.id())
        .collect::<Vec<_>>());
    Ok(v)
}

/// **Turn every mandatory trigger that occurred since the last checkpoint into a checkpoint** (framework §60; the
/// product-observed boundary: task transition, material decision, significant mutation, model/provider switch).
/// Returns the checkpoints written (one per trigger kind observed). Hosts call this at their boundaries.
pub fn observe_boundaries(p: &Project, db: &RuntimeDb, next_action: &str) -> Result<Vec<Value>> {
    let store = RecordStore::load(&p.root);
    let Some(prev) = latest_record(p, &store) else {
        return Ok(vec![]);
    };
    let now = observe_state(p, &store);
    let occurred = triggers_between(p, Some(&prev.data["observed_state"]), &now);
    let mut out = vec![];
    for t in occurred {
        let trig = t["trigger"].as_str().unwrap_or("manual").to_string();
        let c = create(
            p,
            db,
            json!({"trigger": trig, "next_action": next_action, "last_completed_step": format!("observed boundary: {trig}"), "observed_boundary": t}),
        )?;
        out.push(json!({"checkpoint": c["id"], "trigger": trig, "detail": t["detail"]}));
    }
    Ok(out)
}

/// Provider-independent watchdog: checkpoint when context utilisation or operations since the last checkpoint exceed
/// policy. **The operations are observed by the product itself** — gov commands executed since the last checkpoint
/// (telemetry) and repository files changed since it — and the caller's counters can only make it fire earlier
/// (Contract v3:739 "does not depend solely on proprietary hooks"). Mandatory triggers nobody checkpointed are
/// checkpointed first ([`observe_boundaries`]).
pub fn watchdog(
    p: &Project,
    db: &RuntimeDb,
    context_utilisation: f64,
    ops_since: i64,
    task: Option<&str>,
    next_action: &str,
) -> Result<Value> {
    let pol = p.policies();
    let th = pol.get_f64(
        "CHECKPOINT_POLICY",
        "watchdog.context_utilisation_threshold",
        0.75,
    );
    let max_ops = pol.get_i64(
        "CHECKPOINT_POLICY",
        "watchdog.max_operations_between_checkpoints",
        25,
    );
    let store = RecordStore::load(&p.root);
    let since = latest_record(p, &store)
        .map(|r| r.get("created_at"))
        .unwrap_or_default();
    let commands = commands_since(p, &since) as i64;
    let files = if since.is_empty() {
        0
    } else {
        files_changed_since(p, &since) as i64
    };
    let observed = commands.max(files);
    let ops = ops_since.max(observed);
    let boundaries = observe_boundaries(p, db, next_action)?;
    if context_utilisation >= th || ops >= max_ops {
        let reason = if context_utilisation >= th {
            "context_utilisation"
        } else {
            "operations"
        };
        let c = create(
            p,
            db,
            json!({"trigger": "watchdog", "task": task, "next_action": next_action, "last_completed_step": format!("watchdog fired (utilisation {context_utilisation:.2}, operations {ops}: {commands} gov command(s) and {files} changed file(s) observed since the last checkpoint)")}),
        )?;
        return Ok(
            json!({"fired": true, "checkpoint": c["id"], "reason": reason, "observed": {"commands": commands, "files_changed": files, "caller_ops": ops_since}, "boundaries": boundaries}),
        );
    }
    Ok(
        json!({"fired": !boundaries.is_empty(), "threshold": th, "max_operations": max_ops, "observed": {"commands": commands, "files_changed": files, "caller_ops": ops_since}, "boundaries": boundaries}),
    )
}

/// **Session close** (Contract v3:735 "before session close", :742 "handoff/session close can be blocked or degraded
/// when checkpoint freshness violates policy"; `gov session close`). Checkpoints every unobserved trigger, then writes
/// the `before_session_close` checkpoint for the session's work, and states the freshness it closed under: never
/// refused, **explicitly degraded** when a task the session holds (or names) has stale, missing or contradictory
/// mandatory inputs, or when the latest checkpoint was stale.
pub fn session_close(
    p: &Project,
    db: &RuntimeDb,
    next_action: &str,
    task: Option<&str>,
) -> Result<Value> {
    control::guard_write(p, "session close")?;
    crate::authority::require(p, "checkpoint")?;
    let boundaries = observe_boundaries(p, db, next_action)?;
    let store = RecordStore::load(&p.root);
    let mut tasks: Vec<String> = task.map(|t| vec![t.to_string()]).unwrap_or_default();
    if tasks.is_empty() {
        tasks = claims::live(p)
            .unwrap_or_default()
            .into_iter()
            .filter(|c| c["session_id"].as_str() == Some(p.session_id.as_str()))
            .filter_map(|c| c["task_id"].as_str().map(String::from))
            .collect();
    }
    let mut degraded = vec![];
    let mut per_task = vec![];
    for t in &tasks {
        match task_inputs(p, &store, t) {
            Some((_, st)) => {
                if st["delivery_state"] != "COMPLETE" {
                    degraded.push(format!(
                        "{t}: mandatory inputs unsatisfied ({} missing, {} violated)",
                        st["missing_inputs"]
                            .as_array()
                            .map(|a| a.len())
                            .unwrap_or(0),
                        st["input_violations"]
                            .as_array()
                            .map(|a| a.len())
                            .unwrap_or(0)
                    ));
                }
                if !st["stale_inputs"]
                    .as_array()
                    .map(|a| a.is_empty())
                    .unwrap_or(true)
                    || st["packet_invalidated"] == true
                {
                    degraded.push(format!("{t}: the delivered context packet is stale (inputs changed since it was compiled); the next session must recompile and revalidate"));
                }
                if st["contradictions"]
                    .as_array()
                    .map(|a| a.iter().any(|c| c["blocks"] == true))
                    .unwrap_or(false)
                {
                    degraded.push(format!(
                        "{t}: its mandatory inputs contain an unresolved contradiction"
                    ));
                }
                per_task.push(st);
            }
            None => degraded.push(format!("{t}: not a task")),
        }
    }
    let prev_fresh = latest_record(p, &store).map(|r| freshness_of(p, &store, &r));
    if let Some(f) = &prev_fresh {
        if f["state"] == "STALE" {
            degraded.push(format!(
                "the latest checkpoint {} was stale; this checkpoint supersedes it",
                f["checkpoint"].as_str().unwrap_or("?")
            ));
        }
    }
    let ck = create(
        p,
        db,
        json!({"trigger": "before_session_close", "task": tasks.first(), "next_action": next_action,
            "last_completed_step": format!("session {} closing", p.session_id),
            "session_close": {"tasks": tasks, "degraded": degraded, "policy": FRESHNESS_POLICY}}),
    )?;
    Ok(
        json!({"session": p.session_id, "checkpoint": ck["id"], "blocked": false, "degraded": degraded, "resumable": degraded.is_empty(),
        "tasks": per_task, "previous_checkpoint_freshness": prev_fresh, "boundaries_checkpointed": boundaries, "policy": FRESHNESS_POLICY}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn transitions_decisions_and_routing_changes_are_triggers() {
        let prev = json!({"at": "t", "task_states": {"TASK-1": "READY", "TASK-2": "READY"}, "material_decisions": ["D-1"], "routing_digest": "a"});
        let now = json!({"at": "u", "task_states": {"TASK-1": "IN_PROGRESS", "TASK-2": "READY", "TASK-3": "READY"}, "material_decisions": ["D-1", "D-2"], "routing_digest": "b"});
        let t = state_triggers(&prev, &now);
        let kinds: Vec<&str> = t.iter().map(|x| x["trigger"].as_str().unwrap()).collect();
        assert_eq!(
            kinds,
            vec![
                "task_transition",
                "material_decision",
                "before_model_switch"
            ]
        );
        assert_eq!(
            t[0]["detail"][0]["task"], "TASK-1",
            "a new task is not a transition"
        );
        assert_eq!(t[1]["detail"], json!(["D-2"]));
        assert!(state_triggers(&now, &now).is_empty());
    }

    #[test]
    fn material_decisions_are_gate_derived_human_or_wide() {
        let recs = [
            "id: D-1\ntype: decision\nstatus: ACTIVE\nderived_from: [HDG-0001]\n",
            "id: D-2\ntype: decision\nstatus: ACTIVE\nimpact_radius: R3\n",
            "id: D-3\ntype: decision\nstatus: ACTIVE\nimpact_radius: R1\n",
            "id: D-4\ntype: decision\nstatus: ACTIVE\nhuman_approved: true\n",
        ];
        let records: Vec<Record> = recs
            .iter()
            .enumerate()
            .map(|(i, t)| {
                crate::records::parse_record_text(t, &format!("spec/decisions/D-{i}.yaml")).unwrap()
            })
            .collect();
        let mut by_id = std::collections::BTreeMap::new();
        for (i, r) in records.iter().enumerate() {
            by_id.insert(r.id(), i);
        }
        let s = RecordStore {
            records,
            by_id,
            duplicates: vec![],
            problems: vec![],
        };
        assert_eq!(material_decisions(&s), vec!["D-1", "D-2", "D-4"]);
    }
}
