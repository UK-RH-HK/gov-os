//! # Experiment lifecycle (Contract v3 J2, lines 607-614; challenge "irreproducible experiment", line 616; BC-P2-48)
//!
//! **Requirement.** Experiments are governed through a lifecycle recording hypothesis/question, method/data,
//! reproducibility, results, interpretation and decision influence; experimental output cannot enter the production
//! tree without a governed promotion.
//!
//! **State machine** (`experiment_state`; every transition is a `gov experiment` operation, T2-sealed):
//!
//! | from | to | operation | requires |
//! |---|---|---|---|
//! | — | DESIGNED | `design` | hypothesis or question; method; data (governed ids), data provenance or file inputs; outputs outside the production tree; `production_merge_allowed` never true |
//! | DESIGNED | RUNNING | `run` | the primary run: its results, and every input bound by SHA-256 at run time |
//! | RUNNING / CONCLUDED / PROMOTED | (same) | `reproduce` | a reproduction run; the OS judges agreement with the primary run under the acceptance rule fixed at design (`exact`, or a numeric `tolerance`) and whether it ran on the same input bytes |
//! | RUNNING | CONCLUDED | `conclude` | interpretation, decision influence, confidence, reproducibility procedure and environment; the results are the primary run's (copied by the OS, never asserted) |
//! | CONCLUDED | PROMOTED | `promote` | governed evidence, an independent (other-session) agreeing reproduction, and an owner-signed human answer approving exactly these output paths (a gate raised by the OS whose subject digest binds experiment, results and paths) |
//! | DESIGNED / RUNNING / CONCLUDED | ABANDONED | `abandon` | a reason |
//!
//! **Reproducibility** (`reproducibility.status`, computed from the recorded runs): `NOT_REPRODUCED` as soon as one
//! reproduction on the same inputs disagrees — a later agreeing run does not erase it; `REPRODUCED` when at least
//! one does and none disagrees; otherwise `UNVERIFIED`. An experiment whose recorded inputs have changed since its
//! primary run is irreproducible from the tree as it stands. Only a CONCLUDED/PROMOTED, OS-written (T2), complete,
//! `REPRODUCED` experiment on unchanged inputs is governed evidence ([`status`]); anything else is refused as a
//! citation ([`super::require_citable`]) and held reference-only.
//!
//! **Production merge.** An experiment's output lives outside the production tree (its declared `outputs`). The
//! production-merge prohibition is detected three ways ([`findings`]): declared outputs inside the production tree,
//! a production file whose bytes equal an experimental output file (a copy), and — through WS-5's
//! `tasks::production_merge_findings` — experiment-class task output that reached production. Each is covered only
//! by a PROMOTED experiment's approved paths. [`promotion_refusal`] is the check a CIT that carries experimental
//! output into production must pass (integration point, `cit/**`), [`task_lifecycle_refusal`] the check an
//! experiment-class task close must pass (integration point, `tasks.rs`).
use super::{
    evidence_status, finding, hash_path, influence_findings, influenced_by, is_current, list,
    location_paths, present, push_history, refuse_os_owned, reliance_findings, safe_rel_path,
    stamp, validate_seal_save, Ctx, EvidenceStatus, Standing,
};
use crate::authority;
use crate::orchestration::control;
use crate::records::{new_record, Record, RecordStore};
use crate::util::{canonical_json, glob_match, now_iso, sha256_hex, sha256_text};
use crate::{GovError, Project, Result};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

pub const STATES: &[&str] = &["DESIGNED", "RUNNING", "CONCLUDED", "PROMOTED", "ABANDONED"];
/// The gate trigger of an experiment promotion.
pub const PROMOTION_TRIGGER: &str = "experiment_promotion";
/// Fields that define what an experiment is; frozen once the primary run is recorded.
pub const DESIGN_FIELDS: &[&str] = &[
    "hypothesis",
    "question",
    "method",
    "data",
    "data_provenance",
    "inputs",
];
/// Record fields that are OS bookkeeping, not content, when a record is bound as an experiment input.
const VOLATILE_FIELDS: &[&str] = &[
    "influences",
    "lifecycle",
    "recorded_by",
    "concluded_by",
    "staleness",
    "updated",
    crate::t2::SEAL_FIELD,
];

/// Is `from → to` a transition of the experiment state machine?
pub fn transition_allowed(from: &str, to: &str) -> bool {
    matches!(
        (from, to),
        ("DESIGNED", "RUNNING")
            | ("RUNNING", "CONCLUDED")
            | ("CONCLUDED", "PROMOTED")
            | ("DESIGNED", "ABANDONED")
            | ("RUNNING", "ABANDONED")
            | ("CONCLUDED", "ABANDONED")
    )
}

fn transition(id: &str, from: &str, to: &str) -> Result<()> {
    if transition_allowed(from, to) {
        Ok(())
    } else {
        Err(GovError::new(
            "EXPERIMENT_TRANSITION_INVALID",
            format!(
                "{id} is {}; {from} → {to} is not a transition of the experiment lifecycle (DESIGNED → RUNNING → CONCLUDED → PROMOTED; any non-final state → ABANDONED)",
                if from.is_empty() { "not in the lifecycle" } else { from }
            ),
        )
        .with_details(json!({"experiment": id, "from": from, "to": to})))
    }
}

/// The J2 design items `data` does not record.
pub fn missing_design(data: &Value) -> Vec<String> {
    let mut out = vec![];
    if !present(data.get("hypothesis")) && !present(data.get("question")) {
        out.push("hypothesis/question".into());
    }
    if !present(data.get("method")) {
        out.push("method".into());
    }
    if !present(data.get("data"))
        && !present(data.get("data_provenance"))
        && !present(data.get("inputs"))
    {
        out.push("data".into());
    }
    out
}

/// The J2 conclusion items `data` does not record.
pub fn missing_conclusion(data: &Value) -> Vec<String> {
    let mut out = vec![];
    if !present(data.get("results")) && !present(data.get("result")) {
        out.push("results".into());
    }
    let rp = data.get("reproducibility").cloned().unwrap_or(Value::Null);
    if !present(rp.get("procedure")) || !present(rp.get("environment")) {
        out.push("reproducibility (procedure and environment)".into());
    }
    if !present(data.get("interpretation")) {
        out.push("interpretation".into());
    }
    if !present(data.get("decision_influence")) {
        out.push("decision_influence".into());
    }
    if !data
        .get("confidence")
        .and_then(|v| v.as_f64())
        .map(|c| (0.0..=1.0).contains(&c))
        .unwrap_or(false)
    {
        out.push("confidence".into());
    }
    out
}

fn runs(r: &Record) -> Vec<Value> {
    r.data
        .get("runs")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default()
}

fn primary_run(r: &Record) -> Option<Value> {
    runs(r).into_iter().find(|x| x["kind"] == "primary")
}

/// The acceptance rule fixed at design: `{mode: exact}` (default) or `{mode: tolerance, relative, absolute}`.
pub fn acceptance(r: &Record) -> Value {
    let a = r.data["reproducibility"]["acceptance"].clone();
    if a.is_object() {
        a
    } else {
        json!({"mode": "exact"})
    }
}

fn flatten(v: &Value, prefix: &str, out: &mut BTreeMap<String, Value>) {
    match v {
        Value::Object(o) => {
            for (k, x) in o {
                flatten(x, &format!("{prefix}/{k}"), out);
            }
        }
        Value::Array(a) => {
            for (i, x) in a.iter().enumerate() {
                flatten(x, &format!("{prefix}/{i}"), out);
            }
        }
        _ => {
            out.insert(prefix.to_string(), v.clone());
        }
    }
}

/// Does `reproduced` agree with `primary` under the acceptance rule? Returns the agreement and the differing leaves.
pub fn compare_results(primary: &Value, reproduced: &Value, rule: &Value) -> (bool, Vec<String>) {
    let mode = rule["mode"].as_str().unwrap_or("exact");
    let mut a = BTreeMap::new();
    let mut b = BTreeMap::new();
    flatten(primary, "", &mut a);
    flatten(reproduced, "", &mut b);
    let mut diffs = vec![];
    let keys: BTreeSet<&String> = a.keys().chain(b.keys()).collect();
    let rel = rule["relative"].as_f64().unwrap_or(0.0).max(0.0);
    let abs = rule["absolute"].as_f64().unwrap_or(0.0).max(0.0);
    for k in keys {
        match (a.get(k), b.get(k)) {
            (Some(x), Some(y)) => {
                let same = match (x.as_f64(), y.as_f64(), mode) {
                    (Some(p), Some(q), "tolerance") => {
                        (p - q).abs() <= abs + rel * p.abs().max(q.abs())
                    }
                    (Some(p), Some(q), _) => p == q,
                    _ => x == y,
                };
                if !same {
                    diffs.push(format!(
                        "{}: {} vs {}",
                        if k.is_empty() { "/" } else { k },
                        x,
                        y
                    ));
                }
            }
            (Some(_), None) => diffs.push(format!("{k}: missing in the reproduction")),
            (None, Some(_)) => diffs.push(format!("{k}: not in the primary run")),
            (None, None) => {}
        }
    }
    (diffs.is_empty(), diffs)
}

/// The reproducibility verdict of the recorded runs, with the reasons.
pub fn judge(runs: &[Value]) -> (String, Vec<String>) {
    let mut reasons = vec![];
    let valid: Vec<&Value> = runs
        .iter()
        .filter(|x| x["kind"] == "reproduction")
        .filter(|x| {
            let same = x["same_inputs"].as_bool().unwrap_or(false);
            if !same {
                reasons.push(format!(
                    "reproduction {} ran on different input bytes: not a reproduction of the primary run",
                    x["run_id"].as_str().unwrap_or("?")
                ));
            }
            same
        })
        .collect();
    let disagreeing: Vec<&str> = valid
        .iter()
        .filter(|x| !x["agrees"].as_bool().unwrap_or(false))
        .map(|x| x["run_id"].as_str().unwrap_or("?"))
        .collect();
    if !disagreeing.is_empty() {
        reasons.push(format!(
            "reproduction(s) {disagreeing:?} disagree with the primary run: the result is not reproducible"
        ));
        return ("NOT_REPRODUCED".into(), reasons);
    }
    if valid.iter().any(|x| x["agrees"].as_bool().unwrap_or(false)) {
        return ("REPRODUCED".into(), reasons);
    }
    reasons.push("no reproduction on the same inputs has been recorded".into());
    ("UNVERIFIED".into(), reasons)
}

/// A digest of a governed record's content for input binding: the record without OS bookkeeping fields, so an
/// influence backlink or a seal does not look like a change to the data.
pub fn record_digest(r: &Record) -> String {
    let mut d = r.data.clone();
    if let Some(m) = d.as_object_mut() {
        for k in VOLATILE_FIELDS {
            m.remove(*k);
        }
    }
    sha256_text(&format!("{}\n{}", canonical_json(&d), r.body))
}

/// Bind every input of the experiment by content: each governed `data` record (content digest, plus the files at its
/// `location`), and each `inputs` entry (a repository file/directory, or a record id). A missing input binds `null`.
pub fn bind_inputs(root: &Path, store: &RecordStore, r: &Record) -> Vec<Value> {
    let mut out: BTreeMap<String, Value> = BTreeMap::new();
    let bind_record = |id: &str, out: &mut BTreeMap<String, Value>| match store.get(id) {
        Some(x) => {
            out.insert(format!("record:{id}"), json!(record_digest(x)));
            for loc in location_paths(x) {
                let h = safe_rel_path(&loc).ok().and_then(|l| hash_path(root, &l));
                out.insert(format!("path:{loc}"), json!(h));
            }
        }
        None => {
            out.insert(format!("record:{id}"), Value::Null);
        }
    };
    for id in list(r, "data") {
        bind_record(&id, &mut out);
    }
    for inp in r.data["inputs"].as_array().cloned().unwrap_or_default() {
        if let Some(pth) = inp.get("path").and_then(|v| v.as_str()) {
            let h = safe_rel_path(pth).ok().and_then(|l| hash_path(root, &l));
            out.insert(format!("path:{pth}"), json!(h));
        } else if let Some(id) = inp.get("id").and_then(|v| v.as_str()) {
            bind_record(id, &mut out);
        } else if let Some(s) = inp.as_str() {
            let h = safe_rel_path(s).ok().and_then(|l| hash_path(root, &l));
            out.insert(format!("path:{s}"), json!(h));
        }
    }
    out.into_iter()
        .map(|(k, v)| json!({"ref": k, "sha256": v}))
        .collect()
}

fn input_drift(root: &Path, store: &RecordStore, r: &Record) -> Vec<String> {
    let Some(pr) = primary_run(r) else {
        return vec![];
    };
    let now: BTreeMap<String, Value> = bind_inputs(root, store, r)
        .into_iter()
        .map(|x| {
            (
                x["ref"].as_str().unwrap_or("").to_string(),
                x["sha256"].clone(),
            )
        })
        .collect();
    let mut out = vec![];
    for x in pr["inputs"].as_array().cloned().unwrap_or_default() {
        let k = x["ref"].as_str().unwrap_or("").to_string();
        match now.get(&k) {
            Some(h) if *h == x["sha256"] => {}
            Some(Value::Null) | None => out.push(format!("input {k} no longer exists")),
            Some(_) => out.push(format!("input {k} changed since the primary run")),
        }
    }
    out
}

fn env_now(extra: &Value) -> Value {
    let mut e = json!({"gov_version": crate::VERSION, "os": std::env::consts::OS, "arch": std::env::consts::ARCH});
    if let Some(o) = extra.as_object() {
        for (k, v) in o {
            e[k] = v.clone();
        }
    } else if let Some(s) = extra.as_str() {
        e["declared"] = json!(s);
    }
    e
}

// ------------------------------------------------------------------------------------------------ standing

/// The evidence standing of an experiment record.
pub fn status(ctx: &Ctx, r: &Record) -> EvidenceStatus {
    let state_class = ctx.state_class(r);
    let state = r.get("experiment_state");
    let mut missing = vec![];
    let mut reasons = vec![];
    let standing = if !is_current(r) {
        reasons.push(format!("lifecycle status {}", r.status()));
        Standing::NotCurrent
    } else if state.is_empty() {
        missing = missing_design(&r.data);
        reasons.push(
            "not governed through the experiment lifecycle (no experiment_state; `gov experiment design`)".into(),
        );
        Standing::Ungoverned
    } else if state == "ABANDONED" {
        reasons.push("abandoned".into());
        Standing::NotCurrent
    } else {
        let b = (ctx.binding)(r);
        missing = missing_design(&r.data);
        if matches!(state.as_str(), "CONCLUDED" | "PROMOTED") {
            missing.extend(missing_conclusion(&r.data));
        }
        if !b.is_verified() {
            reasons.push(format!("its lifecycle facts (state, runs, reproducibility, promotion) are not what a gov operation on this machine wrote (T2 {})", b.code()));
            Standing::Ungoverned
        } else if !missing.is_empty() {
            reasons.push(format!("{state} without every required J2 field"));
            Standing::Incomplete
        } else if matches!(state.as_str(), "DESIGNED" | "RUNNING") {
            reasons.push(format!("{state}: not concluded"));
            Standing::ReferenceOnly
        } else {
            let (verdict, why) = judge(&runs(r));
            let drift = ctx
                .root
                .map(|root| input_drift(root, ctx.store, r))
                .unwrap_or_default();
            if verdict != "REPRODUCED" || !drift.is_empty() {
                reasons.push(format!("reproducibility {verdict}"));
                reasons.extend(why);
                reasons.extend(drift);
                Standing::Irreproducible
            } else {
                Standing::Governed
            }
        }
    };
    EvidenceStatus {
        id: r.id(),
        rtype: r.rtype(),
        path: r.path.clone(),
        state,
        standing,
        state_class,
        missing,
        reasons,
    }
}

// ------------------------------------------------------------------------------------------------ production merge

/// The concrete path a glob's literal prefix names (for classifying an output location).
fn literal_prefix(glob: &str) -> String {
    let cut = glob.find(['*', '?', '[']).unwrap_or(glob.len());
    let pre = &glob[..cut];
    if pre.ends_with('/') || pre.is_empty() {
        format!("{pre}x")
    } else {
        pre.to_string()
    }
}

/// Repository files under an experiment's declared outputs, with their hashes and sizes.
fn output_files(root: &Path, r: &Record) -> Vec<(String, u64, String)> {
    let outs = list(r, "outputs");
    if outs.is_empty() {
        return vec![];
    }
    let mut v = vec![];
    for (abs, rel) in crate::paths::iter_repo_files(root, false) {
        if outs.iter().any(|g| {
            glob_match(g, &rel) || rel.starts_with(&format!("{}/", g.trim_end_matches('/')))
        }) {
            let size = std::fs::metadata(&abs).map(|m| m.len()).unwrap_or(0);
            if size == 0 {
                continue;
            }
            if let Ok(h) = crate::util::sha256_file(&abs) {
                v.push((rel, size, h));
            }
        }
    }
    v
}

/// Why a PROMOTED experiment's promotion is not honoured, or `None` when it is: the lifecycle facts must be OS-written
/// (T2), the promotion APPROVED, and its gate must still carry the owner-signed, authorising human answer bound to the
/// promotion's subject digest (a revoked or re-answered gate withdraws the promotion).
pub fn promotion_problem(ctx: &Ctx, r: &Record) -> Option<String> {
    if r.get("experiment_state") != "PROMOTED" {
        return Some("not promoted".into());
    }
    let b = (ctx.binding)(r);
    if !b.is_verified() {
        return Some(format!(
            "its lifecycle facts are not OS-written (T2 {})",
            b.code()
        ));
    }
    let pr = &r.data["promotion"];
    if pr["state"] != "APPROVED" {
        return Some(format!("promotion state {}", pr["state"]));
    }
    let gate = pr["gate"].as_str().unwrap_or("");
    let subject = pr["subject_sha256"].as_str().unwrap_or("");
    if gate.is_empty() || subject.is_empty() {
        return Some("the promotion names no gate or subject digest".into());
    }
    (ctx.human_approval)(gate, subject).err().map(|e| {
        format!(
            "its approval on {gate} is not honoured: [{}] {}",
            e.code, e.message
        )
    })
}

/// The production paths a PROMOTED experiment's approved, still-honoured promotion covers.
pub fn promoted_paths(ctx: &Ctx, r: &Record) -> BTreeSet<String> {
    if promotion_problem(ctx, r).is_some() {
        return BTreeSet::new();
    }
    r.data["promotion"]["paths"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default()
}

fn covered(paths: &BTreeSet<String>, path: &str) -> bool {
    paths.iter().any(|g| g == path || glob_match(g, path))
}

/// Production-merge findings of the experiment records: declared outputs inside the production tree, and production
/// files whose bytes equal an experimental output file, not covered by an approved promotion.
pub fn production_merge_findings(ctx: &Ctx) -> Vec<Value> {
    let mut out = vec![];
    let Some(root) = ctx.root else { return out };
    let exps: Vec<&Record> = ctx
        .store
        .of_type("experiment")
        .into_iter()
        .filter(|r| r.get("experiment_state") != "ABANDONED")
        .collect();
    let mut by_hash: BTreeMap<String, Vec<(String, String)>> = BTreeMap::new();
    let mut sizes: BTreeSet<u64> = BTreeSet::new();
    for r in &exps {
        let promoted = promoted_paths(ctx, r);
        for o in list(r, "outputs") {
            if (ctx.production)(&literal_prefix(&o)) && !covered(&promoted, &o) {
                out.push(finding("high", "EXPERIMENT_OUTPUT_IN_PRODUCTION", r, format!(
                    "{} declares experimental output '{o}' inside the production tree without an approved promotion (Contract v3 J2 'production merge prohibited where experimental')",
                    r.id()
                )));
            }
        }
        for (rel, size, h) in output_files(root, r) {
            if (ctx.production)(&rel) {
                continue;
            }
            sizes.insert(size);
            by_hash.entry(h).or_default().push((r.id(), rel));
        }
    }
    if by_hash.is_empty() {
        return out;
    }
    for (abs, rel) in crate::paths::iter_repo_files(root, false) {
        if !(ctx.production)(&rel) {
            continue;
        }
        let size = std::fs::metadata(&abs).map(|m| m.len()).unwrap_or(0);
        if !sizes.contains(&size) {
            continue;
        }
        let Ok(h) = crate::util::sha256_file(&abs) else {
            continue;
        };
        let Some(srcs) = by_hash.get(&h) else {
            continue;
        };
        for (eid, src) in srcs {
            let Some(e) = ctx.store.get(eid) else {
                continue;
            };
            if covered(&promoted_paths(ctx, e), &rel) {
                continue;
            }
            out.push(finding("high", "EXPERIMENT_OUTPUT_IN_PRODUCTION", e, format!(
                "production file {rel} is a copy of {eid}'s experimental output {src}, and no approved promotion of {eid} covers it (Contract v3 J2; `gov experiment promote {eid} --paths {rel}`)"
            )));
        }
    }
    out
}

/// The experiment records linked to `task`: runs recorded for it, or ids the task relies on / names.
pub fn experiments_of_task(store: &RecordStore, task: &Record) -> Vec<String> {
    let tid = task.id();
    let mut out: BTreeSet<String> = BTreeSet::new();
    for e in store.of_type("experiment") {
        if runs(e).iter().any(|x| x["task"] == tid.as_str()) || e.list("tasks").contains(&tid) {
            out.insert(e.id());
        }
    }
    for (s, _, d) in task.edges() {
        if s == tid
            && store
                .get(&d)
                .map(|x| x.rtype() == "experiment")
                .unwrap_or(false)
        {
            out.insert(d);
        }
    }
    for id in task
        .list("experiment")
        .into_iter()
        .chain(task.list("experiments"))
    {
        if store
            .get(&id)
            .map(|x| x.rtype() == "experiment")
            .unwrap_or(false)
        {
            out.insert(id);
        }
    }
    out.into_iter().collect()
}

/// **Close-time check for an experiment-class task (integration point: `tasks::close`, WS-5).** An experiment task
/// is governed through an experiment record: it must be linked to one (a run recorded with `--task`, or the task
/// names/relies on it) whose lifecycle is OS-written and has a primary run. `None` when the task may close.
pub fn task_lifecycle_refusal(ctx: &Ctx, task: &Record) -> Option<GovError> {
    if task.get("class") != "experiment" {
        return None;
    }
    let linked = experiments_of_task(ctx.store, task);
    let ok = linked.iter().any(|id| {
        ctx.store
            .get(id)
            .map(|e| {
                (ctx.binding)(e).is_verified()
                    && primary_run(e).is_some()
                    && e.get("experiment_state") != "DESIGNED"
            })
            .unwrap_or(false)
    });
    if ok {
        return None;
    }
    Some(GovError::new("EXPERIMENT_LIFECYCLE_REQUIRED", format!(
        "{} is an experiment task, and experiments are governed through a lifecycle (Contract v3 J2): link it to an experiment record with a recorded run (`gov experiment design`, then `gov experiment run <EXP> --task {}`); linked now: {linked:?}",
        task.id(), task.id()
    )).with_details(json!({"task": task.id(), "linked_experiments": linked})))
}

/// **CIT-time check (integration point: `cit::approve` / `cit::execute`, WS-4).** A CIT that carries experimental
/// output into the production tree — it names an experiment (`experiment`), moves a file out of an experiment's
/// outputs, or writes bytes equal to an experimental output file — must name only production paths an approved
/// promotion of that experiment covers. `None` when the CIT may proceed.
pub fn promotion_refusal(ctx: &Ctx, cit: &Record) -> Option<GovError> {
    let root = ctx.root?;
    // bytes of every experimental output file (outside production) -> the experiments that produced them
    let mut hashes: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    let mut outputs: Vec<(String, Vec<String>)> = vec![];
    for e in ctx.store.of_type("experiment") {
        outputs.push((e.id(), list(e, "outputs")));
        for (rel, _, h) in output_files(root, e) {
            if !(ctx.production)(&rel) {
                hashes.entry(h).or_default().insert(e.id());
            }
        }
    }
    let declared: Vec<String> = cit.list("experiment");
    let mut problems = vec![];
    for op in cit.data["mutation_manifest"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        let kind = op["op"].as_str().unwrap_or("");
        let (target, sources): (Option<String>, BTreeSet<String>) = match kind {
            "write_file" => {
                let t = op["path"].as_str().map(String::from);
                let h = sha256_hex(op["content"].as_str().unwrap_or("").as_bytes());
                (t, hashes.get(&h).cloned().unwrap_or_default())
            }
            "move_file" => {
                let from = op["path"].as_str().unwrap_or("");
                let e: BTreeSet<String> = outputs
                    .iter()
                    .filter(|(_, globs)| {
                        globs.iter().any(|g| {
                            glob_match(g, from)
                                || from.starts_with(&format!("{}/", g.trim_end_matches('/')))
                        })
                    })
                    .map(|(id, _)| id.clone())
                    .collect();
                (op["to"].as_str().map(String::from), e)
            }
            _ => (None, BTreeSet::new()),
        };
        let Some(target) = target else { continue };
        if !(ctx.production)(&target) {
            continue;
        }
        let covers = |eid: &str| {
            ctx.store
                .get(eid)
                .map(|e| covered(&promoted_paths(ctx, e), &target))
                .unwrap_or(false)
        };
        // every experiment the CIT declares must have approved this path; experimental bytes need one approval
        for eid in &declared {
            if !covers(eid) {
                problems.push(json!({"experiment": eid, "path": target, "op": kind}));
            }
        }
        if !sources.is_empty() && !sources.iter().any(|e| covers(e)) {
            problems.push(json!({"experiment": sources, "path": target, "op": kind}));
        }
    }
    if problems.is_empty() {
        return None;
    }
    Some(GovError::new("EXPERIMENT_NOT_PROMOTED", format!(
        "{} carries experimental output into the production tree without an approved promotion covering it (Contract v3 J2): {problems:?}. Promote first: `gov experiment promote <EXP> --paths <path>` (an owner-signed human answer approves the exact paths).",
        cit.id()
    )).with_details(json!({"cit": cit.id(), "unpromoted": problems})))
}

/// The experiment family of [`super::suite_findings`].
pub fn findings(ctx: &Ctx) -> Vec<Value> {
    let mut out = vec![];
    for r in ctx.store.of_type("experiment") {
        if r.id().is_empty() {
            continue;
        }
        let st = status(ctx, r);
        let state = r.get("experiment_state");
        if r.data
            .get("production_merge_allowed")
            .and_then(|v| v.as_bool())
            == Some(true)
        {
            out.push(finding("high", "EXPERIMENT_MERGE_PERMITTED", r, format!(
                "{} declares production_merge_allowed: true; experimental output merges only through a promotion (Contract v3 J2)",
                r.id()
            )));
        }
        if !is_current(r) {
            continue;
        }
        match st.standing {
            Standing::Ungoverned if state.is_empty() => {
                if st.presented_as_evidence() {
                    out.push(finding("medium", "EXPERIMENT_NOT_GOVERNED", r, format!(
                        "{} is presented as {} but is not governed through the experiment lifecycle{} (`gov experiment design`)",
                        r.id(), st.state_class,
                        if st.missing.is_empty() { String::new() } else { format!("; it does not record {}", st.missing.join(", ")) }
                    )));
                } else {
                    out.push(finding("low", "EXPERIMENT_REFERENCE_NOTE", r, format!(
                        "{} is an experiment note held reference-only ({}); it is not governed evidence",
                        r.id(), st.state_class
                    )));
                }
            }
            Standing::Ungoverned => out.push(finding(
                "high",
                "EXPERIMENT_LIFECYCLE_NOT_OS_WRITTEN",
                r,
                format!(
                    "{}: {} — its state, runs, reproducibility and promotion are not honoured",
                    r.id(),
                    st.reasons.join("; ")
                ),
            )),
            Standing::Incomplete => out.push(finding(
                "medium",
                "EXPERIMENT_INCOMPLETE",
                r,
                format!(
                    "{} ({state}) does not record {} (Contract v3 J2)",
                    r.id(),
                    st.missing.join(", ")
                ),
            )),
            Standing::Irreproducible => {
                let verdict = r.data["reproducibility"]["status"].as_str().unwrap_or("");
                let (code, sev) =
                    if verdict == "UNVERIFIED" && !st.reasons.iter().any(|x| x.contains("input")) {
                        ("EXPERIMENT_REPRODUCTION_PENDING", "low")
                    } else {
                        (
                            "EXPERIMENT_IRREPRODUCIBLE",
                            if state == "PROMOTED" {
                                "high"
                            } else {
                                "medium"
                            },
                        )
                    };
                out.push(finding(
                    sev,
                    code,
                    r,
                    format!(
                        "{} ({state}) is not governed evidence: {}",
                        r.id(),
                        st.reasons.join("; ")
                    ),
                ));
            }
            _ => {}
        }
        if st.standing != Standing::Governed && st.state_class == "EVIDENCE" && !state.is_empty() {
            out.push(finding(
                "medium",
                "EXPERIMENT_PRESENTED_AS_EVIDENCE",
                r,
                format!(
                    "{} is presented as EVIDENCE while its standing is {}",
                    r.id(),
                    st.standing.as_str()
                ),
            ));
        }
        if state == "PROMOTED" && (ctx.binding)(r).is_verified() {
            if let Some(why) = promotion_problem(ctx, r) {
                out.push(finding(
                    "high",
                    "EXPERIMENT_PROMOTION_NOT_HONOURED",
                    r,
                    format!(
                        "{} is PROMOTED but its promotion is not honoured: {why} — the promoted paths are no longer covered",
                        r.id()
                    ),
                ));
            }
        }
    }
    // experiment-class tasks closed without an experiment lifecycle
    for t in ctx.store.of_type("task") {
        if t.get("class") == "experiment" && t.get("task_status") == "DONE" {
            if let Some(e) = task_lifecycle_refusal(ctx, t) {
                out.push(finding(
                    "medium",
                    "EXPERIMENT_TASK_WITHOUT_LIFECYCLE",
                    t,
                    e.message,
                ));
            }
        }
    }
    out.extend(production_merge_findings(ctx));
    out.extend(reliance_findings(ctx, "experiment"));
    out.extend(influence_findings(ctx, "experiment"));
    out
}

// ------------------------------------------------------------------------------------------------ commands

fn obj(fields: Value) -> Result<Map<String, Value>> {
    match fields {
        Value::Object(m) => Ok(m),
        Value::Null => Ok(Map::new()),
        _ => Err(GovError::new(
            "USAGE",
            "--fields must be a JSON/YAML object",
        )),
    }
}

fn load_experiment(store: &RecordStore, id: &str) -> Result<Record> {
    let r = store
        .get(id)
        .ok_or_else(|| GovError::new("EXPERIMENT_NOT_FOUND", format!("{id} not found")))?;
    if r.rtype() != "experiment" {
        return Err(GovError::new(
            "USAGE",
            format!("{id} is a {} record, not an experiment", r.rtype()),
        ));
    }
    Ok(r.clone())
}

/// The lifecycle facts of `r` must be what gov wrote before gov builds on them.
fn require_bound(r: &Record) -> Result<()> {
    crate::t2::require_verified(
        r,
        "an experiment's lifecycle facts (state, runs, reproducibility)",
    )
}

fn check_design_refs(p: &Project, store: &RecordStore, o: &Map<String, Value>) -> Result<()> {
    let v = Value::Object(o.clone());
    let mut unknown = vec![];
    for id in crate::util::str_list(&v, "data") {
        if store.get(&id).is_none() {
            unknown.push(id);
        }
    }
    for inp in v["inputs"].as_array().cloned().unwrap_or_default() {
        if let Some(pth) = inp.get("path").and_then(|x| x.as_str()).or(inp.as_str()) {
            safe_rel_path(pth)?;
        } else if let Some(id) = inp.get("id").and_then(|x| x.as_str()) {
            if store.get(id).is_none() {
                unknown.push(id.to_string());
            }
        } else {
            return Err(GovError::new(
                "USAGE",
                "each inputs entry is {path: <repository path>} or {id: <record id>}",
            ));
        }
    }
    if !unknown.is_empty() {
        return Err(GovError::new(
            "EXPERIMENT_REFERENCE_UNKNOWN",
            format!("experiment data/inputs that are not governed records: {unknown:?}"),
        ));
    }
    for o in crate::util::str_list(&v, "outputs") {
        let rel = safe_rel_path(&o)?;
        if crate::orchestration::tasks::is_production_path(p, &literal_prefix(&rel)) {
            return Err(GovError::new("EXPERIMENT_OUTPUT_IN_PRODUCTION", format!(
                "experimental output '{o}' would live in the production tree; keep it under spec/experiments/** or a path the repository contract classifies as evidence, and promote it later (`gov experiment promote`)"
            )));
        }
    }
    if let Some(m) = v["reproducibility"]["acceptance"]["mode"].as_str() {
        if !matches!(m, "exact" | "tolerance") {
            return Err(GovError::new(
                "USAGE",
                format!("reproducibility.acceptance.mode '{m}' is not exact|tolerance"),
            ));
        }
    }
    if v["reproducibility"].get("status").is_some() {
        return Err(GovError::new(
            "OS_OWNED_FIELD",
            "reproducibility.status is computed by the OS from the recorded runs",
        ));
    }
    Ok(())
}

fn standing_value(p: &Project, id: &str) -> Value {
    let store = RecordStore::load(&p.root);
    let ctx = Ctx::new(p, &store);
    store
        .get(id)
        .and_then(|r| evidence_status(&ctx, r))
        .map(|s| s.to_value())
        .unwrap_or(Value::Null)
}

/// `gov experiment design`: record a new experiment in DESIGNED — or take an existing experiment record that is not
/// in the lifecycle (written by hand, or before this lifecycle existed) into it under its own id, the given fields
/// completing its design. Adoption corrects `production_merge_allowed` to `false` and holds the record reference-only.
pub fn design(p: &Project, fields: Value) -> Result<Value> {
    control::guard_write(p, "experiment design")?;
    authority::require(p, super::RECORD_AUTHORITY)?;
    refuse_os_owned(&fields, &[])?;
    let store = RecordStore::load(&p.root);
    let mut o = obj(fields)?;
    if let Some(t) = o.remove("type") {
        if t != "experiment" {
            return Err(GovError::new(
                "USAGE",
                "gov experiment design writes experiment records",
            ));
        }
    }
    if let Some(v) = o.get("production_merge_allowed") {
        if v != &json!(false) {
            return Err(GovError::new("PRODUCTION_MERGE_NOT_ALLOWED", "an experiment never merges into production by its own flag (Contract v3 J2); its output is promoted through `gov experiment promote`"));
        }
    }
    if let Some(sc) = o.get("state_class").and_then(|v| v.as_str()) {
        if sc != "NARRATIVE" {
            return Err(GovError::new("USAGE", format!("a designed experiment is held reference-only until it is concluded and reproduced; state_class '{sc}' is not allowed")));
        }
    }
    let status = o
        .get("status")
        .and_then(|v| v.as_str())
        .unwrap_or("ACTIVE")
        .to_string();
    if !super::CURRENT_STATUSES.contains(&status.as_str()) {
        return Err(GovError::new(
            "USAGE",
            format!("an experiment is designed ACTIVE or PROVISIONAL, not {status}"),
        ));
    }
    let id = o
        .remove("id")
        .and_then(|v| v.as_str().map(String::from))
        .unwrap_or_else(|| store.next_id("experiment"));
    if !crate::records::id_regex().is_match(&id) {
        return Err(GovError::new("USAGE", format!("'{id}' is not a record id")));
    }
    let mut adopted: Option<Record> = None;
    if let Some(e) = store.get(&id) {
        if e.rtype() != "experiment" || !e.get("experiment_state").is_empty() {
            return Err(GovError::new(
                "DUPLICATE_ID",
                format!(
                    "{id} already exists{}",
                    if e.rtype() == "experiment" {
                        format!(
                            " in the experiment lifecycle ({})",
                            e.get("experiment_state")
                        )
                    } else {
                        String::new()
                    }
                ),
            ));
        }
        let mut base = e.data.as_object().cloned().unwrap_or_default();
        for k in super::OS_OWNED_FIELDS {
            base.remove(*k);
        }
        for k in ["id", "type", "state_class", "production_merge_allowed"] {
            base.remove(k);
        }
        for (k, v) in std::mem::take(&mut o) {
            base.insert(k, v);
        }
        o = base;
        adopted = Some(e.clone());
    }
    check_design_refs(p, &store, &o)?;
    let missing = missing_design(&Value::Object(o.clone()));
    if !missing.is_empty() {
        return Err(GovError::new("EXPERIMENT_DESIGN_INCOMPLETE", format!("{id} cannot be designed without {} (Contract v3 J2: hypothesis/question, method/data)", missing.join(", "))).with_details(json!({"experiment": id, "missing": missing})));
    }
    let title = o
        .remove("title")
        .and_then(|v| v.as_str().map(String::from))
        .or_else(|| {
            o.get("hypothesis")
                .or(o.get("question"))
                .and_then(|v| v.as_str().map(String::from))
        })
        .unwrap_or_else(|| "experiment".into());
    let mut rec = new_record("experiment", &id, &title, Value::Object(o));
    if let Some(e) = &adopted {
        // keep the record where it is (its identity and path), and its format
        rec.path = e.path.clone();
        rec.format = e.format.clone();
        rec.body = e.body.clone();
        if let Some(c) = e.data.get("created") {
            rec.set("created", c.clone());
        }
        rec.set(
            "adopted_into_lifecycle",
            json!({"at": now_iso(), "production_merge_allowed_was": e.data.get("production_merge_allowed"), "state_class_was": e.data.get("state_class")}),
        );
    }
    rec.set("production_merge_allowed", json!(false));
    rec.set("experiment_state", json!("DESIGNED"));
    rec.set("state_class", json!("NARRATIVE"));
    let mut rp = rec.data["reproducibility"].clone();
    if !rp.is_object() {
        rp = json!({});
    }
    if rp.get("acceptance").is_none() {
        rp["acceptance"] = json!({"mode": "exact"});
    }
    rp["status"] = json!("UNVERIFIED");
    rec.set("reproducibility", rp);
    rec.set("runs", json!([]));
    if rec.data.get("influences").is_none() {
        rec.set("influences", json!([]));
    }
    rec.set("recorded_by", stamp(p, "experiment design"));
    push_history(&mut rec, p, "DESIGNED", "experiment design");
    validate_seal_save(p, &mut rec, "experiment design")?;
    Ok(json!({"experiment": rec.data, "standing": standing_value(p, &id)}))
}

/// `gov experiment update`: amend an experiment. Its design is editable only while DESIGNED (the recorded runs were
/// made under the recorded design); afterwards only descriptive fields change.
pub fn update(p: &Project, id: &str, fields: Value) -> Result<Value> {
    control::guard_write(p, "experiment update")?;
    authority::require(p, super::RECORD_AUTHORITY)?;
    refuse_os_owned(&fields, &[])?;
    let store = RecordStore::load(&p.root);
    let mut rec = load_experiment(&store, id)?;
    let state = rec.get("experiment_state");
    if state.is_empty() {
        return Err(GovError::new(
            "EXPERIMENT_TRANSITION_INVALID",
            format!(
                "{id} is not in the experiment lifecycle; record it with `gov experiment design`"
            ),
        ));
    }
    if state != "DESIGNED" || !runs(&rec).is_empty() {
        require_bound(&rec)?;
    }
    let o = obj(fields)?;
    for k in [
        "id",
        "type",
        "state_class",
        "production_merge_allowed",
        "results",
    ] {
        if o.contains_key(k) {
            return Err(GovError::new(
                "USAGE",
                format!("'{k}' is not changed by update"),
            ));
        }
    }
    if state != "DESIGNED" {
        let frozen: Vec<&str> = DESIGN_FIELDS
            .iter()
            .copied()
            .chain(["reproducibility"])
            .filter(|k| o.contains_key(*k))
            .collect();
        if !frozen.is_empty() {
            return Err(GovError::new("EXPERIMENT_DESIGN_FROZEN", format!("{id} is {state}: its runs were made under the recorded design, so {frozen:?} cannot change; design a new experiment (`supersedes: [{id}]`)")));
        }
    }
    check_design_refs(p, &store, &o)?;
    for (k, v) in o {
        if k == "reproducibility" {
            let mut rp = rec.data["reproducibility"].clone();
            if let Some(m) = v.as_object() {
                for (a, b) in m {
                    rp[a] = b.clone();
                }
            }
            rec.set("reproducibility", rp);
        } else {
            rec.set(&k, v);
        }
    }
    let missing = missing_design(&rec.data);
    if !missing.is_empty() {
        return Err(GovError::new(
            "EXPERIMENT_DESIGN_INCOMPLETE",
            format!("{id} would no longer record {}", missing.join(", ")),
        ));
    }
    push_history(&mut rec, p, &state, "experiment update");
    validate_seal_save(p, &mut rec, "experiment update")?;
    Ok(json!({"experiment": rec.data, "standing": standing_value(p, id)}))
}

/// `gov experiment run`: record the primary run (DESIGNED → RUNNING): its results and every input bound by content.
pub fn run(
    p: &Project,
    id: &str,
    results: Value,
    environment: Value,
    task: Option<&str>,
) -> Result<Value> {
    control::guard_write(p, "experiment run")?;
    authority::require(p, super::RECORD_AUTHORITY)?;
    let store = RecordStore::load(&p.root);
    let mut rec = load_experiment(&store, id)?;
    let state = rec.get("experiment_state");
    if state == "RUNNING" && primary_run(&rec).is_some() {
        return Err(GovError::new("EXPERIMENT_ALREADY_RUN", format!("{id} already has its primary run; record another run with `gov experiment reproduce {id}`")));
    }
    transition(id, &state, "RUNNING")?;
    if !runs(&rec).is_empty() {
        require_bound(&rec)?;
    }
    let missing = missing_design(&rec.data);
    if !missing.is_empty() {
        return Err(GovError::new(
            "EXPERIMENT_DESIGN_INCOMPLETE",
            format!("{id} does not record {}", missing.join(", ")),
        ));
    }
    if !present(Some(&results)) {
        return Err(GovError::new(
            "USAGE",
            "a run records its --results (a non-empty JSON/YAML value)",
        ));
    }
    if let Some(t) = task {
        if store.get(t).map(|x| x.rtype() != "task").unwrap_or(true) {
            return Err(GovError::new(
                "TASK_NOT_FOUND",
                format!("--task {t} is not a task"),
            ));
        }
    }
    let inputs = bind_inputs(&p.root, &store, &rec);
    let absent: Vec<String> = inputs
        .iter()
        .filter(|x| x["sha256"].is_null())
        .map(|x| x["ref"].as_str().unwrap_or("").to_string())
        .collect();
    if !absent.is_empty() {
        return Err(GovError::new("EXPERIMENT_INPUT_MISSING", format!("{id} cannot run: inputs {absent:?} do not exist, so the run could not be reproduced from what it recorded")));
    }
    let run = json!({"run_id": "R1", "kind": "primary", "at": now_iso(), "role": p.role, "session": p.session_id, "task": task,
        "results": results, "results_sha256": sha256_text(&canonical_json(&results)), "inputs": inputs, "environment": env_now(&environment)});
    rec.set("runs", json!([run]));
    rec.set("experiment_state", json!("RUNNING"));
    rec.set("state_class", json!("NARRATIVE"));
    let mut rp = rec.data["reproducibility"].clone();
    rp["status"] = json!("UNVERIFIED");
    rec.set("reproducibility", rp);
    push_history(&mut rec, p, "RUNNING", "experiment run");
    validate_seal_save(p, &mut rec, "experiment run")?;
    Ok(
        json!({"experiment": id, "experiment_state": "RUNNING", "run": run, "standing": standing_value(p, id)}),
    )
}

/// `gov experiment reproduce`: record a reproduction run; the OS judges agreement with the primary run and whether
/// it ran on the same input bytes, and recomputes the reproducibility verdict.
pub fn reproduce(p: &Project, id: &str, results: Value, environment: Value) -> Result<Value> {
    control::guard_write(p, "experiment reproduce")?;
    authority::require(p, super::RECORD_AUTHORITY)?;
    let store = RecordStore::load(&p.root);
    let mut rec = load_experiment(&store, id)?;
    let state = rec.get("experiment_state");
    if !matches!(state.as_str(), "RUNNING" | "CONCLUDED" | "PROMOTED") {
        return Err(GovError::new(
            "EXPERIMENT_TRANSITION_INVALID",
            format!("{id} is {state}; a reproduction follows the primary run"),
        ));
    }
    require_bound(&rec)?;
    let primary = primary_run(&rec).ok_or_else(|| {
        GovError::new(
            "EXPERIMENT_TRANSITION_INVALID",
            format!("{id} has no primary run"),
        )
    })?;
    if !present(Some(&results)) {
        return Err(GovError::new(
            "USAGE",
            "a reproduction records its --results",
        ));
    }
    let inputs = bind_inputs(&p.root, &store, &rec);
    let same_inputs = json!(inputs) == primary["inputs"];
    let (agrees, diffs) = compare_results(&primary["results"], &results, &acceptance(&rec));
    let independent = primary["session"].as_str() != Some(p.session_id.as_str());
    let mut all = runs(&rec);
    let run = json!({"run_id": format!("R{}", all.len() + 1), "kind": "reproduction", "at": now_iso(), "role": p.role, "session": p.session_id,
        "results": results, "results_sha256": sha256_text(&canonical_json(&results)), "inputs": inputs, "environment": env_now(&environment),
        "same_inputs": same_inputs, "agrees": agrees, "independent": independent, "differences": diffs.iter().take(20).collect::<Vec<_>>()});
    all.push(run.clone());
    let (verdict, reasons) = judge(&all);
    rec.set("runs", json!(all));
    let mut rp = rec.data["reproducibility"].clone();
    rp["status"] = json!(verdict);
    rec.set("reproducibility", rp);
    if matches!(state.as_str(), "CONCLUDED" | "PROMOTED") {
        rec.set(
            "state_class",
            json!(if verdict == "REPRODUCED" {
                "EVIDENCE"
            } else {
                "NARRATIVE"
            }),
        );
    }
    push_history(&mut rec, p, &state, "experiment reproduce");
    validate_seal_save(p, &mut rec, "experiment reproduce")?;
    Ok(
        json!({"experiment": id, "run": run, "reproducibility": {"status": verdict, "reasons": reasons}, "standing": standing_value(p, id)}),
    )
}

/// `gov experiment conclude`: RUNNING → CONCLUDED. The results are the primary run's (copied, never asserted); the
/// caller records interpretation, decision influence, confidence and the reproducibility procedure/environment. The
/// experiment is EVIDENCE only once reproduced.
pub fn conclude(p: &Project, id: &str, fields: Value) -> Result<Value> {
    control::guard_write(p, "experiment conclude")?;
    authority::require(p, super::RECORD_AUTHORITY)?;
    refuse_os_owned(&fields, &[])?;
    let store = RecordStore::load(&p.root);
    let mut rec = load_experiment(&store, id)?;
    let state = rec.get("experiment_state");
    transition(id, &state, "CONCLUDED")?;
    require_bound(&rec)?;
    let primary = primary_run(&rec).ok_or_else(|| {
        GovError::new(
            "EXPERIMENT_TRANSITION_INVALID",
            format!("{id} has no primary run"),
        )
    })?;
    let o = obj(fields)?;
    let frozen: Vec<&str> = DESIGN_FIELDS
        .iter()
        .copied()
        .chain([
            "id",
            "type",
            "state_class",
            "production_merge_allowed",
            "results",
            "result",
        ])
        .filter(|k| o.contains_key(*k))
        .collect();
    if !frozen.is_empty() {
        return Err(GovError::new("EXPERIMENT_DESIGN_FROZEN", format!("{frozen:?} are not set at conclusion: the design is fixed and the results are the primary run's recorded results")));
    }
    for (k, v) in o {
        if k == "reproducibility" {
            let mut rp = rec.data["reproducibility"].clone();
            for (a, b) in v.as_object().cloned().unwrap_or_default() {
                if a == "status" {
                    return Err(GovError::new(
                        "OS_OWNED_FIELD",
                        "reproducibility.status is computed by the OS",
                    ));
                }
                if a == "acceptance" && b != rp["acceptance"] {
                    return Err(GovError::new("EXPERIMENT_DESIGN_FROZEN", "the acceptance rule was fixed before the runs; changing it after seeing them would re-judge the evidence"));
                }
                rp[a] = b;
            }
            rec.set("reproducibility", rp);
        } else {
            rec.set(&k, v);
        }
    }
    rec.set("results", primary["results"].clone());
    let mut missing = missing_design(&rec.data);
    missing.extend(missing_conclusion(&rec.data));
    if !missing.is_empty() {
        return Err(GovError::new(
            "EXPERIMENT_CONCLUSION_INCOMPLETE",
            format!(
                "{id} cannot be concluded without {} (Contract v3 J2)",
                missing.join(", ")
            ),
        )
        .with_details(json!({"experiment": id, "missing": missing})));
    }
    let (verdict, _) = judge(&runs(&rec));
    let mut rp = rec.data["reproducibility"].clone();
    rp["status"] = json!(verdict);
    rec.set("reproducibility", rp);
    rec.set("experiment_state", json!("CONCLUDED"));
    rec.set(
        "state_class",
        json!(if verdict == "REPRODUCED" {
            "EVIDENCE"
        } else {
            "NARRATIVE"
        }),
    );
    rec.set("concluded_by", stamp(p, "experiment conclude"));
    push_history(&mut rec, p, "CONCLUDED", "experiment conclude");
    validate_seal_save(p, &mut rec, "experiment conclude")?;
    Ok(json!({"experiment": rec.data, "standing": standing_value(p, id)}))
}

/// The promotion subject: what an owner-signed approval of a promotion binds (experiment, primary results, the agreeing
/// reproductions and the exact production paths).
pub fn promotion_subject(r: &Record, paths: &[String]) -> (Value, String) {
    let mut ps = paths.to_vec();
    ps.sort();
    ps.dedup();
    let reproductions: Vec<Value> = runs(r)
        .into_iter()
        .filter(|x| x["kind"] == "reproduction" && x["agrees"] == true && x["same_inputs"] == true)
        .map(|x| x["run_id"].clone())
        .collect();
    let subject = json!({"kind": "experiment-promotion", "experiment": r.id(),
        "results_sha256": primary_run(r).map(|x| x["results_sha256"].clone()).unwrap_or(Value::Null),
        "reproductions": reproductions, "paths": ps});
    let sha = sha256_text(&canonical_json(&subject));
    (subject, sha)
}

/// `gov experiment promote`: CONCLUDED → PROMOTED through a governed promotion. Without `gate`, the OS raises a Human
/// Decision Gate whose subject digest binds the experiment, its results, its reproductions and the exact paths, and
/// records the promotion as PENDING. With `gate`, the gate must carry an owner-signed, authorising human answer for
/// exactly that subject ([`crate::orchestration::gates::human_approval_for`]).
pub fn promote(
    p: &Project,
    id: &str,
    paths: &[String],
    gate: Option<&str>,
    cit: Option<&str>,
) -> Result<Value> {
    control::guard_write(p, "experiment promote")?;
    authority::require(p, super::PROMOTE_AUTHORITY)?;
    let store = RecordStore::load(&p.root);
    let mut rec = load_experiment(&store, id)?;
    let state = rec.get("experiment_state");
    transition(id, &state, "PROMOTED")?;
    require_bound(&rec)?;
    let ctx = Ctx::new(p, &store);
    let st = status(&ctx, &rec);
    if !st.citable() {
        return Err(GovError::new("EXPERIMENT_NOT_PROMOTABLE", format!("{id} is {}: only governed evidence (concluded, reproduced on unchanged inputs) is promoted: {}", st.standing.as_str(), st.reasons.join("; "))).with_details(st.to_value()));
    }
    if !runs(&rec).iter().any(|x| {
        x["kind"] == "reproduction"
            && x["agrees"] == true
            && x["same_inputs"] == true
            && x["independent"] == true
    }) {
        return Err(GovError::new("EXPERIMENT_NOT_PROMOTABLE", format!("{id} has no independent reproduction: promotion into production needs an agreeing reproduction recorded by a session other than the primary run's (`gov experiment reproduce {id}` from another session)")));
    }
    if paths.is_empty() {
        return Err(GovError::new(
            "USAGE",
            "name the production paths the promotion approves (--paths)",
        ));
    }
    let mut ps = vec![];
    for x in paths {
        let rel = safe_rel_path(x)?;
        if !crate::orchestration::tasks::is_production_path(p, &literal_prefix(&rel)) {
            return Err(GovError::new("USAGE", format!("'{rel}' is not in the production tree; a promotion approves production paths only")));
        }
        ps.push(rel);
    }
    if let Some(c) = cit {
        if store.get(c).map(|x| x.rtype() != "cit").unwrap_or(true) {
            return Err(GovError::new(
                "CIT_NOT_FOUND",
                format!("--cit {c} is not a change-impact transaction"),
            ));
        }
    }
    let (subject, sha) = promotion_subject(&rec, &ps);
    let Some(gate_id) = gate else {
        let conf = rec.data["confidence"].as_f64().unwrap_or(0.5);
        let g = crate::orchestration::gates::create_system(
            p,
            json!({
                "question": format!("Promote the output of experiment {id} into production at {}?", ps.join(", ")),
                "why_now": format!("{id} is concluded, reproduced independently on unchanged inputs, and its output is proposed for the production tree; experimental output enters production only through a governed promotion (Contract v3 J2)"),
                "current_state": format!("{id}: hypothesis/question '{}'; results digest {}; reproductions {}; interpretation: {}", rec.data.get("hypothesis").or(rec.data.get("question")).and_then(|v| v.as_str()).unwrap_or(""), subject["results_sha256"], subject["reproductions"], rec.get("interpretation")),
                "options": [
                    {"id": "A", "description": format!("approve the promotion of exactly {} (the change itself is then carried by a CIT)", ps.join(", ")), "authorises_blocked_work": true},
                    {"id": "B", "description": "decline: the experimental output stays out of the production tree", "authorises_blocked_work": false}
                ],
                "impact": format!("the production tree gains experimental output at {}", ps.join(", ")),
                "reversibility": "reversible: the promoting CIT can be rolled back and the promotion revoked",
                "cost_rework": "one CIT and its retest if the promotion is reverted",
                "recommendation": format!("decide on the evidence: interpretation '{}', decision influence '{}'", rec.get("interpretation"), rec.data["decision_influence"].as_str().unwrap_or("")),
                "confidence": conf,
                "impact_radius": "R3",
                "trigger": PROMOTION_TRIGGER,
                "subject": {"kind": "experiment-promotion", "id": id, "sha256": sha, "digest_of": subject},
            }),
        )?;
        let gid = g["id"].as_str().unwrap_or("").to_string();
        rec.set("promotion", json!({"state": "PENDING", "gate": gid, "subject_sha256": sha, "paths": ps, "cit": cit, "requested_by": stamp(p, "experiment promote")}));
        push_history(&mut rec, p, "CONCLUDED", "experiment promote (gate raised)");
        validate_seal_save(p, &mut rec, "experiment promote")?;
        return Ok(
            json!({"experiment": id, "experiment_state": "CONCLUDED", "promotion": rec.data["promotion"], "gate": gid,
            "next_actions": [format!("gov gate present {gid}"), format!("the product owner signs an answer for {gid}; `gov decide {gid} --option A --answer-file <signed>`"), format!("gov experiment promote {id} --paths {} --gate {gid}", ps.join(","))]}),
        );
    };
    let a = crate::orchestration::gates::human_approval_for(p, gate_id, &sha)?;
    rec.set("promotion", json!({"state": "APPROVED", "gate": gate_id, "decision": a.decision, "subject_sha256": sha, "paths": ps, "cit": cit,
        "approved_by": a.answered_by, "approved_by_kind": a.by_kind, "approved_at": now_iso(), "promoted_by": stamp(p, "experiment promote")}));
    rec.set("experiment_state", json!("PROMOTED"));
    push_history(&mut rec, p, "PROMOTED", "experiment promote");
    validate_seal_save(p, &mut rec, "experiment promote")?;
    Ok(
        json!({"experiment": id, "experiment_state": "PROMOTED", "promotion": rec.data["promotion"], "standing": standing_value(p, id)}),
    )
}

/// `gov experiment abandon`: any non-final state → ABANDONED (status RETIRED, HISTORICAL). Allowed on a record whose
/// seal does not verify: abandoning is the fail-safe direction.
pub fn abandon(p: &Project, id: &str, reason: &str) -> Result<Value> {
    control::guard_write(p, "experiment abandon")?;
    authority::require(p, super::RECORD_AUTHORITY)?;
    if reason.trim().is_empty() {
        return Err(GovError::new("USAGE", "abandoning records its --reason"));
    }
    let store = RecordStore::load(&p.root);
    let mut rec = load_experiment(&store, id)?;
    let state = rec.get("experiment_state");
    transition(id, &state, "ABANDONED")?;
    rec.set("experiment_state", json!("ABANDONED"));
    rec.set("abandon_reason", json!(reason));
    rec.set("status", json!("RETIRED"));
    rec.set("state_class", json!("HISTORICAL"));
    push_history(&mut rec, p, "ABANDONED", "experiment abandon");
    validate_seal_save(p, &mut rec, "experiment abandon")?;
    Ok(json!({"experiment": rec.data, "standing": standing_value(p, id)}))
}

/// `gov experiment show`.
pub fn show(p: &Project, id: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let rec = load_experiment(&store, id)?;
    let ctx = Ctx::new(p, &store);
    let st = status(&ctx, &rec);
    let (verdict, reasons) = judge(&runs(&rec));
    let derived = influenced_by(&store, id);
    let recorded = rec.list("influences");
    let not_recorded: Vec<&String> = derived.iter().filter(|x| !recorded.contains(x)).collect();
    Ok(json!({"experiment": rec.data, "standing": st.to_value(),
        "reproducibility": {"status": verdict, "reasons": reasons, "input_drift": input_drift(&p.root, &store, &rec)},
        "influences": {"recorded": recorded, "derived": derived, "not_recorded": not_recorded},
        "t2": crate::t2::verify_record(&rec).to_value(),
        "identity": crate::graph::identity::identity(p, &store, id).unwrap_or(Value::Null)}))
}

/// `gov experiment check`: standings and findings, including WS-5's experiment-task production-merge findings.
pub fn check(p: &Project) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let ctx = Ctx::new(p, &store);
    let mut f = findings(&ctx);
    f.extend(task_merge_findings(p, &store));
    Ok(
        json!({"family": super::FAMILY, "experiments": super::standings(&ctx, "experiment"), "findings": f, "ok": f.is_empty()}),
    )
}

/// WS-5's production-merge findings for experiment-class tasks, in this family's shape.
pub fn task_merge_findings(p: &Project, store: &RecordStore) -> Vec<Value> {
    crate::orchestration::tasks::production_merge_findings(p, store)
        .into_iter()
        .filter(|f| f["class"] == "experiment")
        .map(|f| {
            json!({"severity": "high", "family": super::FAMILY, "code": "EXPERIMENTAL_TASK_OUTPUT_IN_PRODUCTION",
                "record": f["task"], "path": store.get(f["task"].as_str().unwrap_or("")).map(|t| t.path.clone()),
                "message": f["message"], "production_paths": f["production_paths"]})
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::super::testkit::*;
    use super::*;

    fn designed(id: &str) -> Value {
        json!({"id": id, "type": "experiment", "status": "ACTIVE", "experiment_state": "DESIGNED", "state_class": "NARRATIVE",
            "hypothesis": "async halves p95", "method": "A/B on staging", "data": ["DATA-0001"], "production_merge_allowed": false,
            "reproducibility": {"acceptance": {"mode": "tolerance", "relative": 0.05}, "status": "UNVERIFIED"}, "runs": [],
            "os_binding": {"test": "verified"}})
    }

    #[test]
    fn the_state_machine_admits_only_its_transitions() {
        assert!(transition_allowed("DESIGNED", "RUNNING"));
        assert!(transition_allowed("CONCLUDED", "PROMOTED"));
        assert!(!transition_allowed("DESIGNED", "CONCLUDED"));
        assert!(!transition_allowed("RUNNING", "PROMOTED"));
        assert!(!transition_allowed("PROMOTED", "ABANDONED"));
        assert!(!transition_allowed("", "RUNNING"));
        assert_eq!(
            transition("EXP-1", "DESIGNED", "PROMOTED")
                .unwrap_err()
                .code,
            "EXPERIMENT_TRANSITION_INVALID"
        );
    }

    #[test]
    fn reproductions_are_judged_by_the_os_under_the_fixed_rule() {
        let rule = json!({"mode": "tolerance", "relative": 0.05});
        assert!(compare_results(&json!({"p95": 100.0}), &json!({"p95": 103.0}), &rule).0);
        let (ok, d) = compare_results(&json!({"p95": 100.0}), &json!({"p95": 120.0}), &rule);
        assert!(!ok && d[0].contains("/p95"));
        assert!(
            !compare_results(
                &json!({"p95": 100.0}),
                &json!({"p95": 100.1}),
                &json!({"mode": "exact"})
            )
            .0
        );
        assert!(
            !compare_results(&json!({"a": 1}), &json!({"a": 1, "b": 2}), &rule).0,
            "a different shape never agrees"
        );
        let r1 = json!({"run_id": "R1", "kind": "primary"});
        let agree =
            json!({"run_id": "R2", "kind": "reproduction", "same_inputs": true, "agrees": true});
        let disagree =
            json!({"run_id": "R3", "kind": "reproduction", "same_inputs": true, "agrees": false});
        let other_inputs =
            json!({"run_id": "R4", "kind": "reproduction", "same_inputs": false, "agrees": true});
        assert_eq!(judge(&[r1.clone()]).0, "UNVERIFIED");
        assert_eq!(judge(&[r1.clone(), other_inputs.clone()]).0, "UNVERIFIED");
        assert_eq!(judge(&[r1.clone(), agree.clone()]).0, "REPRODUCED");
        assert_eq!(
            judge(&[r1, disagree, agree]).0,
            "NOT_REPRODUCED",
            "a later agreeing run does not erase a disagreement"
        );
    }

    #[test]
    fn standing_requires_os_written_concluded_reproduced_experiments_on_unchanged_inputs() {
        let fx = Fx::new("exp");
        fx.put("spec/data/DATA-0001.yaml", json!({"id": "DATA-0001", "type": "data", "status": "ACTIVE", "data_kind": "test-dataset", "location": "fixtures/traffic.csv"}));
        fx.file("fixtures/traffic.csv", "t,ms\n1,40\n");
        let s0 = fx.store();
        let mut base = designed("EXP-0001");
        let inputs = bind_inputs(
            &fx.dir,
            &s0,
            &crate::records::parse_record_text(
                &crate::util::to_yaml(&base).unwrap(),
                "spec/experiments/EXP-0001.yaml",
            )
            .unwrap(),
        );
        assert!(inputs.iter().all(|x| !x["sha256"].is_null()), "{inputs:?}");
        let primary = json!({"run_id": "R1", "kind": "primary", "session": "S-1", "results": {"p95": 18.0}, "inputs": inputs});
        let repro = json!({"run_id": "R2", "kind": "reproduction", "session": "S-2", "results": {"p95": 18.5}, "inputs": inputs, "same_inputs": true, "agrees": true, "independent": true});
        let concluded = |runs: Value| {
            let mut v = base.clone();
            v["experiment_state"] = json!("CONCLUDED");
            v["state_class"] = json!("EVIDENCE");
            v["runs"] = runs;
            v["results"] = json!({"p95": 18.0});
            v["reproducibility"]["procedure"] = json!("replay the day");
            v["reproducibility"]["environment"] = json!("staging");
            v["interpretation"] = json!("async helps");
            v["decision_influence"] = json!("supports D-0003");
            v["confidence"] = json!(0.8);
            v
        };
        fx.put(
            "spec/experiments/EXP-0001.yaml",
            concluded(json!([primary, repro])),
        );
        fx.put("spec/experiments/EXP-0002.yaml", {
            let mut v = concluded(json!([primary]));
            v["id"] = json!("EXP-0002");
            v
        });
        fx.put("spec/experiments/EXP-0003.yaml", {
            let mut v = concluded(json!([primary, repro]));
            v["id"] = json!("EXP-0003");
            v.as_object_mut().unwrap().remove("os_binding");
            v
        });
        base["id"] = json!("EXP-0004");
        fx.put("spec/experiments/EXP-0004.yaml", base.clone());
        fx.put("spec/experiments/EXP-0005.yaml", json!({"id": "EXP-0005", "type": "experiment", "status": "ACTIVE", "title": "Try an async gateway client"}));
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &[]);
        let st = |id: &str| status(&c, s.get(id).unwrap());
        assert_eq!(
            st("EXP-0001").standing,
            Standing::Governed,
            "{:?}",
            st("EXP-0001")
        );
        assert_eq!(
            st("EXP-0002").standing,
            Standing::Irreproducible,
            "never reproduced"
        );
        assert_eq!(
            st("EXP-0003").standing,
            Standing::Ungoverned,
            "hand-written lifecycle facts are not honoured"
        );
        assert_eq!(st("EXP-0004").standing, Standing::ReferenceOnly);
        let e5 = st("EXP-0005");
        assert_eq!(e5.standing, Standing::Ungoverned);
        assert_eq!(e5.missing, vec!["hypothesis/question", "method", "data"]);
        // the data it ran on changes: irreproducible from the tree as it stands
        fx.file("fixtures/traffic.csv", "t,ms\n1,41\n");
        let s2 = fx.store();
        let c2 = ctx(&s2, &fx.dir, &[]);
        let st2 = status(&c2, s2.get("EXP-0001").unwrap());
        assert_eq!(st2.standing, Standing::Irreproducible);
        assert!(
            st2.reasons
                .iter()
                .any(|r| r.contains("path:fixtures/traffic.csv changed")),
            "{:?}",
            st2.reasons
        );
        // an OS-bookkeeping change to an input record (influence backlink, seal) is not a data change
        let d = s2.get("DATA-0001").unwrap().clone();
        let mut d2 = d.clone();
        d2.set("influences", json!(["D-0009"]));
        assert_eq!(record_digest(&d), record_digest(&d2));
    }

    #[test]
    fn experimental_output_copied_into_production_is_found_unless_promoted() {
        let fx = Fx::new("expm");
        fx.file(
            "spec/experiments/EXP-0001/gateway_async.py",
            "async def charge():\n    pass\n",
        );
        fx.file(
            "product/gateway_async.py",
            "async def charge():\n    pass\n",
        );
        let mut e = designed("EXP-0001");
        e["outputs"] = json!(["spec/experiments/EXP-0001/**"]);
        fx.put("spec/experiments/EXP-0001.yaml", e.clone());
        let mut bad = designed("EXP-0002");
        bad["outputs"] = json!(["product/**"]);
        fx.put("spec/experiments/EXP-0002.yaml", bad);
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &[]);
        let f = production_merge_findings(&c);
        assert!(
            f.iter().any(|x| x["record"] == "EXP-0001"
                && x["message"]
                    .as_str()
                    .unwrap()
                    .contains("product/gateway_async.py")),
            "{f:?}"
        );
        assert!(f
            .iter()
            .any(|x| x["record"] == "EXP-0002" && x["code"] == "EXPERIMENT_OUTPUT_IN_PRODUCTION"));
        // a CIT that writes the same bytes into production is refused until a promotion covers the path
        let cit = crate::records::new_record(
            "cit",
            "CIT-0001",
            "t",
            json!({"mutation_manifest": [{"op": "write_file", "path": "product/gateway_async.py", "content": "async def charge():\n    pass\n"}]}),
        );
        assert_eq!(
            promotion_refusal(&c, &cit).unwrap().code,
            "EXPERIMENT_NOT_PROMOTED"
        );
        e["experiment_state"] = json!("PROMOTED");
        e["promotion"] = json!({"state": "APPROVED", "gate": "HDG-0001", "paths": ["product/gateway_async.py"], "subject_sha256": "x"});
        fx.put("spec/experiments/EXP-0001.yaml", e.clone());
        let s2 = fx.store();
        let c2 = ctx(&s2, &fx.dir, &[]);
        assert!(promotion_refusal(&c2, &cit).is_none());
        assert!(!production_merge_findings(&c2)
            .iter()
            .any(|x| x["record"] == "EXP-0001"));
        // a revoked promotion gate withdraws the promotion: the copy is reported again and the CIT refused
        e["promotion"]["gate"] = json!("HDG-REVOKED");
        fx.put("spec/experiments/EXP-0001.yaml", e);
        let s3 = fx.store();
        let c3 = ctx(&s3, &fx.dir, &[]);
        assert!(promotion_problem(&c3, s3.get("EXP-0001").unwrap()).is_some());
        assert!(promotion_refusal(&c3, &cit).is_some());
        assert!(production_merge_findings(&c3)
            .iter()
            .any(|x| x["record"] == "EXP-0001"));
    }
}
