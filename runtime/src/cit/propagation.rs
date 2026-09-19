//! **Upstream-change propagation** (BC-P2-04; Contract v3:632 "staleness/retest/rework propagation", :1129-1136 W6
//! "When an authoritative upstream artefact changes: dependent task evidence becomes stale; implementation/release/test
//! evidence is invalidated according to impact; affected context packets are invalidated; graph/CIT computes impacted
//! downstream nodes; revalidation/rework tasks are generated; COMPLETE does not imply permanently valid; stale
//! evidence cannot remain green merely because the original task closed successfully", :788-789 O4, :1187 G1;
//! framework §47.2).
//!
//! One engine serves both ways an authoritative input can change:
//!
//! * **through CIT-E** — `cit::execute` calls [`plan`] before it applies the manifest (so the snapshot covers every
//!   record propagation will touch) and [`apply`] after, inside the transaction (a rollback undoes the markers and
//!   removes the generated tasks);
//! * **directly** (an edit that never passed change control) — [`detect`] derives the change from what each piece of
//!   dependent work recorded it consumed, and [`detect_and_propagate`] runs the same [`plan`]/[`apply`]. Detection is
//!   content-based: it compares the SHA-256 each consumer recorded (the task's delivered context packet, the inputs a
//!   checkpoint recorded, the consumption receipt of a closing report) with the input's bytes now. It never reads the
//!   derived index, so an index rebuild cannot substitute for dependency staleness (W6 line 1132, AC-16 W6×D1).
//!
//! ## What a change reaches (the dependency closure, independent of the CIT radius)
//!
//! | dependent | how it is found | what happens |
//! |---|---|---|
//! | every task whose input manifest includes a changed input (open **and** `DONE`), plus every task the CIT-P impact lists | `context::manifest::resolve` per task; `impact.affected_tasks` | `retest_required: true`, `retest_reason`, `staleness.inputs_changed` |
//! | a `DONE` dependent task | as above | also `revalidation.required: true` and a generated **revalidation task** (`class: validation`, `revalidates: <task>`, same inputs), unless an open one exists |
//! | the closing report(s) of a dependent task | `task.closed_by_report`, `report.task` | `staleness` (implementation evidence is no longer green) |
//! | validation evidence | scenarios/test obligations that reference a changed input, the feature's scenarios and acceptance tests when one of its requirements changed, the acceptance tests/scenarios a dependent task declares, and the CIT-P `tests_required` | `staleness` |
//! | checkpoints | those of a dependent task, and any checkpoint whose recorded `inputs` include a changed input at another hash | `staleness` |
//! | open handoffs of a dependent task | `handoff.task` | `staleness` (the handed-off packet predates the change) |
//! | compiled context packets of a dependent task | `.governance-runtime/context/<task>.json` (+ its history copy) | `invalidated` marker naming the inputs, their delivered and current hashes |
//!
//! Markers accumulate (`staleness.inputs_changed` keeps every `{id, from, to, cause}`), and re-running propagation for
//! a change already recorded writes nothing. Nothing is cleared here: close must not clear staleness without retest
//! evidence ([`require_current_inputs`], the task-close integration point for WS-5), and a revalidation task's close
//! clears the revalidation of the task it names (WS-5, BC-P2-24). The one exception is a task that never started work:
//! re-delivering its packet at the current inputs acknowledges the change ([`acknowledge_on_redelivery`]).
use crate::context::manifest;
use crate::records::{save_record, Record, RecordStore};
use crate::util::{now_iso, read_json, sha256_hex, write_json};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

/// One changed authoritative input: its id and the SHA-256 of its bytes before and after (`None` = absent).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct InputChange {
    pub id: String,
    pub from: Option<String>,
    pub to: Option<String>,
}

impl InputChange {
    pub fn to_value(&self, cause: &Cause) -> Value {
        json!({"id": self.id, "from": self.from, "to": self.to, "cause": cause.label()})
    }
}

/// What made the inputs change.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Cause {
    /// A committed Change-Impact Transaction.
    Cit(String),
    /// A change that did not pass change control, detected by the named operation.
    Direct { detected_by: String },
}

impl Cause {
    pub fn label(&self) -> String {
        match self {
            Cause::Cit(id) => format!("CIT {id}"),
            Cause::Direct { .. } => "direct change (not through a CIT)".into(),
        }
    }
    pub fn to_value(&self) -> Value {
        match self {
            Cause::Cit(id) => json!({"kind": "cit", "cit": id}),
            Cause::Direct { detected_by } => {
                json!({"kind": "direct", "detected_by": detected_by, "note": "an authoritative input changed outside change control; the same propagation CIT-E performs was applied when it was detected"})
            }
        }
    }
}

/// The dependents a set of changes reaches, each with why.
#[derive(Debug, Clone, Default)]
pub struct Plan {
    pub changed: Vec<String>,
    pub open_tasks: BTreeMap<String, BTreeSet<String>>,
    pub done_tasks: BTreeMap<String, BTreeSet<String>>,
    pub reports: BTreeMap<String, BTreeSet<String>>,
    pub tests: BTreeMap<String, BTreeSet<String>>,
    pub checkpoints: BTreeMap<String, BTreeSet<String>>,
    pub handoffs: BTreeMap<String, BTreeSet<String>>,
    pub packets: BTreeMap<String, BTreeSet<String>>,
}

fn add(m: &mut BTreeMap<String, BTreeSet<String>>, k: &str, why: String) {
    m.entry(k.to_string()).or_default().insert(why);
}

impl Plan {
    /// Repository paths of every governed record the plan will write, and the packet files (so a CIT snapshot can
    /// cover them).
    pub fn paths(&self, p: &Project, store: &RecordStore) -> Vec<String> {
        let mut v = vec![];
        for m in [
            &self.open_tasks,
            &self.done_tasks,
            &self.reports,
            &self.tests,
            &self.checkpoints,
            &self.handoffs,
        ] {
            for id in m.keys() {
                if let Some(r) = store.get(id) {
                    v.push(r.path.clone());
                }
            }
        }
        for t in self.packets.keys() {
            for f in packet_files(p, t) {
                v.push(f);
            }
        }
        v.sort();
        v.dedup();
        v
    }
    pub fn to_value(&self) -> Value {
        let m = |x: &BTreeMap<String, BTreeSet<String>>| -> Value {
            json!(x
                .iter()
                .map(|(k, w)| json!({"id": k, "why": w.iter().cloned().collect::<Vec<_>>()}))
                .collect::<Vec<_>>())
        };
        json!({"changed": self.changed, "open_tasks": m(&self.open_tasks), "completed_tasks": m(&self.done_tasks),
            "reports": m(&self.reports), "tests": m(&self.tests), "checkpoints": m(&self.checkpoints),
            "handoffs": m(&self.handoffs), "packets": m(&self.packets)})
    }
}

/// Current SHA-256 of a governed record's bytes, or of a repository file named `file:<path>` (`None` when it does
/// not exist).
pub fn record_hash(root: &std::path::Path, store: &RecordStore, id: &str) -> Option<String> {
    let rel = match id.strip_prefix("file:") {
        Some(path) => path.to_string(),
        None => store.get(id)?.path.clone(),
    };
    crate::util::read_bytes(&root.join(rel))
        .ok()
        .map(|b| sha256_hex(&b))
}

fn packet_path(p: &Project, task: &str) -> std::path::PathBuf {
    p.runtime_dir().join("context").join(format!("{task}.json"))
}

/// The packet files of `task` (the current packet and its history copy), as repository-relative paths.
fn packet_files(p: &Project, task: &str) -> Vec<String> {
    let mut v = vec![];
    let cur = packet_path(p, task);
    if cur.exists() {
        v.push(crate::util::rel_posix(&cur, &p.root));
        if let Ok(pk) = read_json(&cur) {
            if let Some(h) = pk["packet_hash"].as_str() {
                let hist = p
                    .runtime_dir()
                    .join("context")
                    .join("packets")
                    .join(task)
                    .join(format!("{h}.json"));
                if hist.exists() {
                    v.push(crate::util::rel_posix(&hist, &p.root));
                }
            }
        }
    }
    v
}

const FINISHED: &[&str] = &["DONE"];
const INERT: &[&str] = &["CANCELLED"];

/// Ids a record references through any of the given fields (lists, scalars, `relations[].target`).
fn refs(r: &Record, fields: &[&str]) -> BTreeSet<String> {
    let mut out = BTreeSet::new();
    for f in fields {
        match r.data.get(*f) {
            Some(Value::String(s)) if !s.is_empty() => {
                out.insert(s.split('@').next().unwrap_or("").to_string());
            }
            Some(Value::Array(a)) => {
                for x in a {
                    if let Some(id) = crate::records::relation_target(x) {
                        out.insert(id);
                    }
                }
            }
            _ => {}
        }
    }
    if let Some(rels) = r.data.get("relations").and_then(|v| v.as_array()) {
        for x in rels {
            if let Some(t) = x.get("target").and_then(|v| v.as_str()) {
                out.insert(t.to_string());
            }
        }
    }
    out
}

/// Fields of scenarios/test obligations that name what they validate.
const VALIDATES_FIELDS: &[&str] = &[
    "requirements",
    "requirement",
    "tests",
    "validates",
    "validated_by",
    "scenario",
    "scenarios",
    "interfaces",
    "decisions",
    "derived_from",
];

/// **The dependents of a change set** (read-only). `impact` is the CIT-P impact when the change is a CIT (its
/// `affected_tasks` and `tests_required` are included as the impact analysis dictates); the dependency closure below
/// is computed from the governed records and does not depend on the CIT radius. `only_tasks` restricts the task
/// dependents to the given set: a change detected after the fact reaches only the tasks whose work consumed the
/// previous version (a task already delivered the current version is not stale).
pub fn plan(
    p: &Project,
    store: &RecordStore,
    changed: &[String],
    impact: Option<&Value>,
    only_tasks: Option<&BTreeSet<String>>,
) -> Plan {
    let mut pl = Plan {
        changed: changed.to_vec(),
        ..Default::default()
    };
    let changed_set: BTreeSet<&str> = changed.iter().map(|s| s.as_str()).collect();
    // 1. consumers: every task whose input manifest declares a changed input (open and completed)
    let mut affected: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    for t in store.of_type("task") {
        if INERT.contains(&t.get("task_status").as_str()) {
            continue;
        }
        if only_tasks.map(|o| !o.contains(&t.id())).unwrap_or(false) {
            continue;
        }
        let m = manifest::resolve(p, store, t);
        for e in &m.entries {
            if changed_set.contains(e.id.as_str()) {
                affected.entry(t.id()).or_default().insert(format!(
                    "consumes {} ({}, declared in {})",
                    e.id,
                    e.slot.name(),
                    e.sources.join(", ")
                ));
            }
        }
    }
    // 2. what the CIT-P impact analysis lists
    if let Some(imp) = impact {
        for t in imp["affected_tasks"]
            .as_array()
            .cloned()
            .unwrap_or_default()
        {
            if let Some(id) = t.as_str() {
                if store
                    .get(id)
                    .map(|r| !INERT.contains(&r.get("task_status").as_str()))
                    .unwrap_or(false)
                {
                    affected.entry(id.to_string()).or_default().insert(format!(
                        "in the CIT-P impact set (radius {})",
                        imp["radius"].as_str().unwrap_or("?")
                    ));
                }
            }
        }
        for t in imp["tests_required"]
            .as_array()
            .cloned()
            .unwrap_or_default()
        {
            if let Some(id) = t.as_str() {
                if store.get(id).is_some() {
                    add(&mut pl.tests, id, "CIT-P tests_required".into());
                }
            }
        }
    }
    for (tid, why) in &affected {
        let Some(t) = store.get(tid) else { continue };
        let done = FINISHED.contains(&t.get("task_status").as_str());
        let target = if done {
            &mut pl.done_tasks
        } else {
            &mut pl.open_tasks
        };
        target.insert(tid.clone(), why.clone());
        // the task's closing evidence
        let mut reports: BTreeSet<String> = BTreeSet::new();
        let cbr = t.get("closed_by_report");
        if !cbr.is_empty() {
            reports.insert(cbr);
        }
        for r in store.of_type("report") {
            if r.get("task") == *tid {
                reports.insert(r.id());
            }
        }
        for r in reports {
            if store.get(&r).is_some() {
                add(
                    &mut pl.reports,
                    &r,
                    format!("evidence of {tid}, which depends on the change"),
                );
            }
        }
        // the validation evidence the task declares
        for v in t
            .list("acceptance_tests")
            .into_iter()
            .chain(t.list("scenarios"))
        {
            if store.get(&v).is_some() {
                add(
                    &mut pl.tests,
                    &v,
                    format!("validates {tid}, which depends on the change"),
                );
            }
        }
        for c in store.of_type("checkpoint") {
            if c.get("task") == *tid {
                add(
                    &mut pl.checkpoints,
                    &c.id(),
                    format!("captured the state of {tid}"),
                );
            }
        }
        for h in store.of_type("handoff") {
            if h.get("task") == *tid && h.get("handoff_status") == "OPEN" {
                add(
                    &mut pl.handoffs,
                    &h.id(),
                    format!("hands off {tid} with a packet that predates the change"),
                );
            }
        }
        if packet_path(p, tid).exists() {
            add(
                &mut pl.packets,
                tid,
                "compiled before the change".to_string(),
            );
        }
    }
    // 3. validation evidence of the changed inputs themselves (independent of any task and of the radius)
    let mut features: BTreeSet<String> = BTreeSet::new();
    for id in &changed_set {
        if let Some(r) = store.get(id) {
            if r.rtype() == "feature" {
                features.insert(r.id());
            }
            let f = r.get("feature");
            if !f.is_empty() && r.rtype() == "requirement" {
                features.insert(f);
            }
        }
    }
    for f in store.of_type("feature") {
        if f.list("requirements")
            .iter()
            .chain(f.list("interfaces").iter())
            .any(|x| changed_set.contains(x.as_str()))
        {
            features.insert(f.id());
        }
    }
    for r in store
        .records
        .iter()
        .filter(|r| matches!(r.rtype().as_str(), "scenario" | "test-obligation"))
    {
        if r.problems.iter().any(|x| x == "archived") {
            continue;
        }
        let rid = r.id();
        if changed_set.contains(rid.as_str()) {
            continue;
        }
        let named: Vec<String> = refs(r, VALIDATES_FIELDS)
            .into_iter()
            .filter(|x| changed_set.contains(x.as_str()))
            .collect();
        if !named.is_empty() {
            add(
                &mut pl.tests,
                &rid,
                format!("validates changed input(s) {}", named.join(", ")),
            );
        }
        let f = r.get("feature");
        if !f.is_empty() && features.contains(&f) {
            add(
                &mut pl.tests,
                &rid,
                format!("validates feature {f}, whose requirements changed"),
            );
        }
    }
    for fid in &features {
        if let Some(f) = store.get(fid) {
            for v in f
                .list("scenarios")
                .into_iter()
                .chain(f.list("acceptance_tests"))
            {
                if store.get(&v).is_some() && !changed_set.contains(v.as_str()) {
                    add(
                        &mut pl.tests,
                        &v,
                        format!("acceptance evidence of feature {fid}, whose requirements changed"),
                    );
                }
            }
        }
    }
    // 4. checkpoints that recorded a changed input (whatever their task)
    for c in store.of_type("checkpoint") {
        let rec: Vec<String> = c.data["inputs"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|x| x["id"].as_str().map(String::from))
                    .collect()
            })
            .unwrap_or_default();
        let hit: Vec<&String> = rec
            .iter()
            .filter(|x| changed_set.contains(x.as_str()))
            .collect();
        if !hit.is_empty() {
            add(
                &mut pl.checkpoints,
                &c.id(),
                format!(
                    "recorded input(s) {}",
                    hit.iter()
                        .map(|s| s.as_str())
                        .collect::<Vec<_>>()
                        .join(", ")
                ),
            );
        }
    }
    pl
}

/// Merge `changes` into a record's `staleness` block. Returns `None` when every change is already recorded.
fn merged_staleness(
    existing: Option<&Value>,
    changes: &[InputChange],
    cause: &Cause,
    why: &BTreeSet<String>,
    extra: Value,
) -> Option<Value> {
    let mut list: Vec<Value> = existing
        .and_then(|s| s.get("inputs_changed"))
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default();
    let already = |c: &InputChange, list: &Vec<Value>| {
        list.iter()
            .any(|x| x["id"].as_str() == Some(c.id.as_str()) && x["to"].as_str() == c.to.as_deref())
    };
    let fresh: Vec<&InputChange> = changes.iter().filter(|c| !already(c, &list)).collect();
    let was_stale = existing
        .and_then(|s| s.get("stale"))
        .and_then(|v| v.as_bool())
        .unwrap_or(false);
    if fresh.is_empty() && was_stale {
        return None;
    }
    for c in &fresh {
        list.push(c.to_value(cause));
    }
    let mut causes: Vec<Value> = existing
        .and_then(|s| s.get("causes"))
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default();
    let cv = cause.to_value();
    if !causes.contains(&cv) {
        causes.push(cv);
    }
    let mut v = json!({"stale": true, "reason": cause.label(), "at": now_iso(), "causes": causes,
        "inputs_changed": list, "why": why.iter().cloned().collect::<Vec<_>>()});
    if let (Some(o), Some(e)) = (v.as_object_mut(), extra.as_object()) {
        for (k, x) in e {
            o.insert(k.clone(), x.clone());
        }
    }
    Some(v)
}

/// The changes relevant to one dependent (all of them: a dependent reached by the plan depends on the set).
fn relevant<'a>(changes: &'a [InputChange]) -> &'a [InputChange] {
    changes
}

/// Options for [`apply`].
#[derive(Debug, Clone)]
pub struct ApplyOptions {
    /// Generate revalidation tasks for completed dependents (requires the acting role's `create_task` authority;
    /// when it is missing the completed task is still marked and the result says the task is pending).
    pub generate_rework: bool,
}

impl Default for ApplyOptions {
    fn default() -> Self {
        ApplyOptions {
            generate_rework: true,
        }
    }
}

fn save_set(
    p: &Project,
    id: &str,
    f: impl FnOnce(&mut Record) -> bool,
    touched: &mut Vec<String>,
) -> Result<bool> {
    let mut st = RecordStore::load(&p.root);
    let Some(r) = st.get_mut(id) else {
        return Ok(false);
    };
    if !f(r) {
        return Ok(false);
    }
    touched.push(r.path.clone());
    save_record(&p.root, r)?;
    Ok(true)
}

/// An open revalidation task already generated for `task`, if any.
fn open_revalidation(store: &RecordStore, task: &str) -> Option<String> {
    store
        .of_type("task")
        .into_iter()
        .find(|t| {
            t.get("revalidates") == task
                && !matches!(t.get("task_status").as_str(), "DONE" | "CANCELLED")
        })
        .map(|t| t.id())
}

/// Generate the revalidation task for completed task `t` (framework §47.2 "rework propagation"; W6 line 1134).
fn generate_revalidation(
    p: &Project,
    store: &RecordStore,
    t: &Record,
    changes: &[InputChange],
    cause: &Cause,
) -> Result<Value> {
    let tid = t.id();
    let ids: Vec<String> = changes.iter().map(|c| c.id.clone()).collect();
    let m = manifest::resolve(p, store, t);
    let status = if m.satisfied() { "READY" } else { "BLOCKED" };
    let mut f = json!({
        "title": format!("Revalidate {tid} after {}", cause.label()),
        "objective": format!("Revalidate the completed work of {tid} ({}) against its changed inputs {}: re-run its acceptance evidence at the current input versions, rework what no longer holds, and close with a consumption receipt at the current hashes", t.title(), ids.join(", ")),
        "class": "validation",
        "task_status": status,
        "revalidates": tid,
        "revalidation_of": {"task": tid, "report": t.get("closed_by_report"), "cause": cause.to_value(),
            "inputs_changed": changes.iter().map(|c| c.to_value(cause)).collect::<Vec<_>>()},
        "generated_by": "cit::propagation (upstream change)",
        "provenance": {"producer": "gov upstream-change propagation", "cause": cause.to_value(), "session": p.session_id, "role": p.role, "at": now_iso()},
    });
    for k in [
        "feature",
        "requirements",
        "decisions",
        "scenarios",
        "acceptance_tests",
        "interfaces",
        "architecture",
        "required_data",
        "required_inputs",
        "optional_inputs",
        "allowed_paths",
        "forbidden_paths",
        "derived_from",
    ] {
        if let Some(v) = t.data.get(k) {
            if !v.is_null() {
                f[k] = v.clone();
            }
        }
    }
    if status == "BLOCKED" {
        f["status_note"] = json!(m.blocking_reason().unwrap_or_default());
    }
    crate::orchestration::tasks::create(p, f)
}

/// **Persist a plan** for `changes` caused by `cause`. Returns the propagation summary (`retest_required` and
/// `stale_tests` keep the keys CIT-E always reported) and appends every repository path written to `touched`.
/// `created` receives the paths of generated tasks (a CIT adds them to its snapshot so a rollback removes them).
pub fn apply(
    p: &Project,
    plan: &Plan,
    changes: &[InputChange],
    cause: &Cause,
    opts: &ApplyOptions,
    touched: &mut Vec<String>,
    created: &mut Vec<String>,
) -> Result<Value> {
    let pol = p.policies();
    let on = |k: &str| pol.get_bool("CHANGE_POLICY", &format!("propagation.{k}"), true);
    let ch = relevant(changes);
    let mut retest = vec![];
    let mut revalidate = vec![];
    let mut rework = vec![];
    let mut rework_pending = vec![];
    let mut stale_reports = vec![];
    let mut stale_tests = vec![];
    let mut stale_checkpoints = vec![];
    let mut stale_handoffs = vec![];
    let mut invalidated_packets = vec![];
    let reason = cause.label();
    if on("mark_affected_tasks_retest") {
        for (tid, why) in &plan.open_tasks {
            let wrote = save_set(
                p,
                tid,
                |r| {
                    let ms = merged_staleness(r.data.get("staleness"), ch, cause, why, json!({}));
                    let retest_set =
                        r.data.get("retest_required").and_then(|v| v.as_bool()) == Some(true);
                    if ms.is_none() && retest_set {
                        return false;
                    }
                    r.set("retest_required", json!(true));
                    r.set("retest_reason", json!(reason.clone()));
                    if let Some(s) = ms {
                        r.set("staleness", s);
                    }
                    true
                },
                touched,
            )?;
            if wrote {
                retest.push(tid.clone());
            }
        }
    }
    if on("revalidate_completed_tasks") {
        for (tid, why) in &plan.done_tasks {
            let store = RecordStore::load(&p.root);
            let existing = open_revalidation(&store, tid);
            let mut task_ref: Option<String> = existing.clone();
            let t = store.get(tid).cloned();
            let needs = t
                .as_ref()
                .map(|t| {
                    merged_staleness(t.data.get("staleness"), ch, cause, why, json!({})).is_some()
                })
                .unwrap_or(false);
            if !needs {
                continue;
            }
            if task_ref.is_none() && on("generate_revalidation_tasks") {
                if opts.generate_rework {
                    if let Some(t) = &t {
                        match generate_revalidation(p, &store, t, ch, cause) {
                            Ok(v) => {
                                let id = v["id"].as_str().unwrap_or("").to_string();
                                if let Some(r) = RecordStore::load(&p.root).get(&id) {
                                    created.push(r.path.clone());
                                    touched.push(r.path.clone());
                                }
                                rework.push(json!({"task": id, "revalidates": tid}));
                                task_ref = Some(id);
                            }
                            Err(e) => rework_pending.push(
                                json!({"revalidates": tid, "code": e.code, "reason": e.message}),
                            ),
                        }
                    }
                } else {
                    rework_pending.push(json!({"revalidates": tid, "reason": "the acting role may not create tasks (create_task); the completed task is marked and a later propagation by an authorised role generates its revalidation task"}));
                }
            }
            save_set(
                p,
                tid,
                |r| {
                    let Some(s) = merged_staleness(
                        r.data.get("staleness"),
                        ch,
                        cause,
                        why,
                        json!({"requires": "revalidation"}),
                    ) else {
                        return false;
                    };
                    r.set("retest_required", json!(true));
                    r.set("retest_reason", json!(reason.clone()));
                    r.set("staleness", s);
                    r.set("revalidation", json!({"required": true, "cause": cause.to_value(), "task": task_ref, "at": now_iso(),
                        "note": "COMPLETE does not imply permanently valid (Contract v3 W6): this task's evidence depends on inputs that changed after it closed"}));
                    true
                },
                touched,
            )?;
            revalidate.push(tid.clone());
        }
    }
    let mark = |ids: &BTreeMap<String, BTreeSet<String>>,
                out: &mut Vec<String>,
                touched: &mut Vec<String>|
     -> Result<()> {
        for (id, why) in ids {
            let wrote = save_set(
                p,
                id,
                |r| match merged_staleness(r.data.get("staleness"), ch, cause, why, json!({})) {
                    Some(s) => {
                        r.set("staleness", s);
                        true
                    }
                    None => false,
                },
                touched,
            )?;
            if wrote {
                out.push(id.clone());
            }
        }
        Ok(())
    };
    if on("mark_evidence_stale") {
        mark(&plan.reports, &mut stale_reports, touched)?;
    }
    if on("mark_affected_tests_stale") {
        mark(&plan.tests, &mut stale_tests, touched)?;
    }
    if on("mark_checkpoints_stale") {
        mark(&plan.checkpoints, &mut stale_checkpoints, touched)?;
        mark(&plan.handoffs, &mut stale_handoffs, touched)?;
    }
    if on("invalidate_context_packets") {
        let store = RecordStore::load(&p.root);
        for tid in plan.packets.keys() {
            for rel in packet_files(p, tid) {
                let abs = p.root.join(&rel);
                let Ok(mut pk) = read_json(&abs) else {
                    continue;
                };
                let supplied = pk["input_hashes"].as_object().cloned().unwrap_or_default();
                let stale: Vec<Value> = ch
                    .iter()
                    .filter(|c| supplied.get(&c.id).and_then(|v| v.as_str()) != c.to.as_deref())
                    .map(|c| json!({"id": c.id, "delivered": supplied.get(&c.id), "current": c.to, "cause": reason}))
                    .collect();
                if stale.is_empty() {
                    continue;
                }
                let mut prev: Vec<Value> = pk["invalidated"]["inputs"]
                    .as_array()
                    .cloned()
                    .unwrap_or_default();
                let before = prev.len();
                for s in stale {
                    if !prev
                        .iter()
                        .any(|x| x["id"] == s["id"] && x["current"] == s["current"])
                    {
                        prev.push(s);
                    }
                }
                if prev.len() == before && pk.get("invalidated").is_some() {
                    continue;
                }
                pk["invalidated"] = json!({"at": now_iso(), "cause": cause.to_value(), "inputs": prev,
                    "remediation": format!("recompile before use: `gov context compile {tid}` delivers the current inputs; work done against this packet must be revalidated"),
                    "task_status_now": store.get(tid).map(|r| r.get("task_status"))});
                write_json(&abs, &pk)?;
                touched.push(rel.clone());
                if !invalidated_packets.contains(tid) {
                    invalidated_packets.push(tid.clone());
                }
            }
        }
    }
    Ok(json!({
        "cause": cause.to_value(),
        "inputs_changed": ch.iter().map(|c| c.to_value(cause)).collect::<Vec<_>>(),
        "retest_required": retest,
        "revalidation_required": revalidate,
        "revalidation_tasks": rework,
        "revalidation_pending": rework_pending,
        "stale_reports": stale_reports,
        "stale_tests": stale_tests,
        "stale_checkpoints": stale_checkpoints,
        "stale_handoffs": stale_handoffs,
        "invalidated_packets": invalidated_packets,
        "plan": plan.to_value(),
    }))
}

// ------------------------------------------------------------------------------------------------ detection

/// What a task's work consumed: the input hashes one consumer recorded, where and when.
#[derive(Debug, Clone)]
pub struct Baseline {
    pub source: String,
    pub reference: String,
    pub at: String,
    pub hashes: BTreeMap<String, String>,
}

impl Baseline {
    pub fn to_value(&self) -> Value {
        json!({"source": self.source, "reference": self.reference, "at": self.at, "inputs": self.hashes})
    }
}

fn receipt_hashes(r: &Record) -> BTreeMap<String, String> {
    let mut out = BTreeMap::new();
    for x in r.data["inputs_consumed"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        match &x {
            Value::String(s) => {
                if let Some((id, h)) = s.split_once('@') {
                    out.insert(id.trim().to_string(), h.trim().to_string());
                }
            }
            Value::Object(o) => {
                if let (Some(id), Some(h)) = (
                    o.get("id").and_then(|v| v.as_str()),
                    o.get("content_hash").and_then(|v| v.as_str()),
                ) {
                    out.insert(id.to_string(), h.to_string());
                }
            }
            _ => {}
        }
    }
    out
}

/// **What task `t`'s work consumed.** For a completed task: the consumption receipt of its closing report, else the
/// inputs its closing checkpoint recorded (as delivered), else the last packet compiled before it closed. For open
/// work: the latest of its delivered packet and its latest checkpoint's recorded inputs. `None` when nothing was
/// ever delivered (no work consumed anything).
pub fn baseline_of(p: &Project, store: &RecordStore, t: &Record) -> Option<Baseline> {
    let tid = t.id();
    let done = FINISHED.contains(&t.get("task_status").as_str());
    let closed_at = t.get("closed_at");
    let mut cands: Vec<Baseline> = vec![];
    if done {
        let rid = t.get("closed_by_report");
        if let Some(r) = store.get(&rid) {
            let h = receipt_hashes(r);
            if !h.is_empty() {
                return Some(Baseline {
                    source: "closing report consumption receipt".into(),
                    reference: rid,
                    at: closed_at,
                    hashes: h,
                });
            }
        }
    }
    for c in store.of_type("checkpoint") {
        if c.get("task") != tid {
            continue;
        }
        let at = c.get("created_at");
        if done
            && !closed_at.is_empty()
            && at.as_str() > closed_at.as_str()
            && c.get("trigger") != "task_transition"
        {
            continue;
        }
        let Some(arr) = c.data["inputs"].as_array() else {
            continue;
        };
        let mut h = BTreeMap::new();
        for x in arr {
            let id = x["id"].as_str().unwrap_or("");
            let hash = x["delivered_hash"]
                .as_str()
                .or(x["content_hash"].as_str())
                .unwrap_or("");
            if !id.is_empty() && !hash.is_empty() {
                h.insert(id.to_string(), hash.to_string());
            }
        }
        if !h.is_empty() {
            cands.push(Baseline {
                source: format!("checkpoint {} ({})", c.id(), c.get("trigger")),
                reference: c.id(),
                at,
                hashes: h,
            });
        }
    }
    if let Ok(pk) = read_json(&packet_path(p, &tid)) {
        let at = pk["compiled_at"].as_str().unwrap_or("").to_string();
        let h: BTreeMap<String, String> = pk["input_hashes"]
            .as_object()
            .map(|o| {
                o.iter()
                    .filter_map(|(k, v)| v.as_str().map(|s| (k.clone(), s.to_string())))
                    .collect()
            })
            .unwrap_or_default();
        let before_close = !done || closed_at.is_empty() || at.as_str() <= closed_at.as_str();
        if !h.is_empty() && before_close {
            cands.push(Baseline {
                source: "delivered context packet".into(),
                reference: pk["packet_hash"].as_str().unwrap_or("").to_string(),
                at,
                hashes: h,
            });
        }
    }
    // a completed task's closing checkpoint is authoritative for what the closed work was checked against
    if done {
        if let Some(b) = cands
            .iter()
            .filter(|b| b.source.contains("task_transition"))
            .max_by(|a, b| a.at.cmp(&b.at))
        {
            return Some(b.clone());
        }
    }
    cands.into_iter().max_by(|a, b| a.at.cmp(&b.at))
}

/// Inputs of task `t` whose bytes changed since its baseline, and whether each change is already propagated to it.
pub fn stale_inputs(
    p: &Project,
    store: &RecordStore,
    t: &Record,
) -> (Option<Baseline>, Vec<(InputChange, bool)>) {
    let Some(b) = baseline_of(p, store, t) else {
        return (None, vec![]);
    };
    let m = manifest::resolve(p, store, t);
    let recorded: Vec<Value> = t.data["staleness"]["inputs_changed"]
        .as_array()
        .cloned()
        .unwrap_or_default();
    let mut out = vec![];
    for e in &m.entries {
        let Some(then) = b.hashes.get(&e.id) else {
            continue;
        };
        let now = e.content_hash.clone();
        if now.as_deref() == Some(then.as_str()) {
            continue;
        }
        let c = InputChange {
            id: e.id.clone(),
            from: Some(then.clone()),
            to: now,
        };
        let propagated = recorded.iter().any(|x| {
            x["id"].as_str() == Some(c.id.as_str()) && x["to"].as_str() == c.to.as_deref()
        });
        out.push((c, propagated));
    }
    (Some(b), out)
}

/// **The derived staleness of task `task_id`** (read-only; integration point for the DAG, `task list`/`show` and
/// `status`, WS-5): the baseline its work consumed, every input changed since, whether that change was propagated,
/// and the markers on the record.
pub fn task_staleness(p: &Project, store: &RecordStore, task_id: &str) -> Result<Value> {
    let t = store
        .get(task_id)
        .filter(|t| t.rtype() == "task")
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("task {task_id} not found")))?;
    let (b, st) = stale_inputs(p, store, t);
    Ok(json!({
        "task": task_id,
        "task_status": t.get("task_status"),
        "stale": !st.is_empty() || t.data.get("retest_required").and_then(|v| v.as_bool()).unwrap_or(false),
        "baseline": b.map(|b| b.to_value()),
        "stale_inputs": st.iter().map(|(c, prop)| json!({"id": c.id, "consumed": c.from, "current": c.to, "propagated": prop})).collect::<Vec<_>>(),
        "retest_required": t.data.get("retest_required").cloned().unwrap_or(json!(false)),
        "staleness": t.data.get("staleness").cloned().unwrap_or(Value::Null),
        "revalidation": t.data.get("revalidation").cloned().unwrap_or(Value::Null),
    }))
}

/// **Unpropagated upstream changes** across the project: for every task, the inputs whose bytes differ from what its
/// work consumed and that its record does not yet carry as stale.
pub fn detect(p: &Project, store: &RecordStore) -> Vec<(String, Vec<InputChange>)> {
    let mut out = vec![];
    for t in store.of_type("task") {
        if INERT.contains(&t.get("task_status").as_str()) {
            continue;
        }
        let (_, st) = stale_inputs(p, store, t);
        let fresh: Vec<InputChange> = st
            .into_iter()
            .filter(|(_, prop)| !prop)
            .map(|(c, _)| c)
            .collect();
        if !fresh.is_empty() {
            out.push((t.id(), fresh));
        }
    }
    out
}

/// **Detect every unpropagated upstream change and propagate it** exactly as CIT-E does (the direct-change path:
/// Contract v3:1129-1136 "however made"). `detected_by` names the operation (recorded in every marker).
pub fn detect_and_propagate(p: &Project, detected_by: &str, dry_run: bool) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let found = detect(p, &store);
    // one change per input: the earliest consumed hash is the `from`, the current bytes the `to`
    let mut changes: BTreeMap<String, InputChange> = BTreeMap::new();
    for (_, cs) in &found {
        for c in cs {
            changes.entry(c.id.clone()).or_insert_with(|| c.clone());
        }
    }
    let changes: Vec<InputChange> = changes.into_values().collect();
    let ids: Vec<String> = changes.iter().map(|c| c.id.clone()).collect();
    let tasks: BTreeSet<String> = found.iter().map(|(t, _)| t.clone()).collect();
    let pl = plan(p, &store, &ids, None, Some(&tasks));
    let detected = json!(found.iter().map(|(t, cs)| json!({"task": t, "inputs": cs.iter().map(|c| json!({"id": c.id, "consumed": c.from, "current": c.to})).collect::<Vec<_>>()})).collect::<Vec<_>>());
    if dry_run || changes.is_empty() {
        return Ok(
            json!({"detected": detected, "changes": changes.len(), "dry_run": dry_run, "plan": pl.to_value(), "propagated": false}),
        );
    }
    let cause = Cause::Direct {
        detected_by: detected_by.to_string(),
    };
    let opts = ApplyOptions {
        generate_rework: crate::authority::require(p, "create_task").is_ok(),
    };
    let mut touched = vec![];
    let mut created = vec![];
    let r = apply(p, &pl, &changes, &cause, &opts, &mut touched, &mut created)?;
    Ok(
        json!({"detected": detected, "changes": changes.len(), "dry_run": false, "propagated": true, "propagation": r, "touched": touched}),
    )
}

/// **Close-side check** (integration point for `orchestration::tasks::close`, WS-5; Contract v3:1135-1136 "stale
/// evidence cannot remain green merely because the original task closed successfully", W6 "close cannot clear
/// staleness without retest evidence", AC-16 W6×D1 "an index rebuild never substitutes for dependency staleness").
///
/// Refuses the close of `task_id` with `report` (the worker return / report, receipt fields included) when:
/// * `INPUTS_STALE` — an input the task consumed changed since (content hash, not index freshness) and the report
///   does not acknowledge the current version (`inputs_consumed` at the current hash): the work was done against the
///   old input;
/// * `RETEST_EVIDENCE_REQUIRED` — the task is `retest_required` and the report carries no passing test evidence
///   produced against the current inputs (`inputs_consumed` at the current hashes and `tests.status: passed`, or an
///   explicit `retest` block naming the re-validated inputs).
///
/// On success returns what the close should persist: `{"revalidated_inputs": [...], "clears_retest": bool}`.
pub fn require_current_inputs(
    p: &Project,
    store: &RecordStore,
    task_id: &str,
    report: &Value,
) -> Result<Value> {
    let t = store
        .get(task_id)
        .filter(|t| t.rtype() == "task")
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("task {task_id} not found")))?;
    let m = manifest::resolve(p, store, t);
    let current: BTreeMap<String, Option<String>> = m
        .entries
        .iter()
        .map(|e| (e.id.clone(), e.content_hash.clone()))
        .collect();
    let receipt: BTreeMap<String, String> = {
        let mut out = BTreeMap::new();
        for x in report["inputs_consumed"]
            .as_array()
            .cloned()
            .unwrap_or_default()
        {
            match &x {
                Value::String(s) => {
                    if let Some((id, h)) = s.split_once('@') {
                        out.insert(id.trim().to_string(), h.trim().to_string());
                    }
                }
                Value::Object(o) => {
                    if let (Some(id), Some(h)) = (
                        o.get("id").and_then(|v| v.as_str()),
                        o.get("content_hash").and_then(|v| v.as_str()),
                    ) {
                        out.insert(id.to_string(), h.to_string());
                    }
                }
                _ => {}
            }
        }
        out
    };
    let acknowledged = |id: &str| -> bool {
        match (receipt.get(id), current.get(id).cloned().flatten()) {
            (Some(h), Some(c)) => c.starts_with(h.as_str()) && h.len() >= 12,
            _ => false,
        }
    };
    let (_, st) = stale_inputs(p, store, t);
    let unacknowledged: Vec<Value> = st
        .iter()
        .filter(|(c, _)| !acknowledged(&c.id))
        .map(|(c, _)| json!({"id": c.id, "consumed": c.from, "current": c.to}))
        .collect();
    if !unacknowledged.is_empty() {
        return Err(GovError::new(
            "INPUTS_STALE",
            format!("{task_id} cannot close: its work consumed input(s) that have changed since ({}). An index rebuild does not make stale work current. Recompile its context (`gov context compile {task_id}`), revalidate the work against the current inputs, and close with `inputs_consumed` at the current hashes", unacknowledged.iter().map(|x| x["id"].as_str().unwrap_or("").to_string()).collect::<Vec<_>>().join(", ")),
        )
        .with_details(json!({"task": task_id, "stale_inputs": unacknowledged})));
    }
    let retest = t
        .data
        .get("retest_required")
        .and_then(|v| v.as_bool())
        .unwrap_or(false);
    let changed_ids: Vec<String> = t.data["staleness"]["inputs_changed"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x["id"].as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    let tests_passed = report["tests"]["status"].as_str() == Some("passed");
    let explicit: Vec<String> = report["retest"]["inputs"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| {
                    x.as_str()
                        .map(|s| s.split('@').next().unwrap_or("").to_string())
                })
                .collect()
        })
        .unwrap_or_default();
    if retest {
        let covered = changed_ids
            .iter()
            .all(|id| acknowledged(id) || explicit.contains(id));
        let passed = tests_passed || report["retest"]["status"].as_str() == Some("passed");
        if !(covered && passed) {
            return Err(GovError::new(
                "RETEST_EVIDENCE_REQUIRED",
                format!("{task_id} is retest_required ({}); closing does not clear it without evidence that the work was re-tested against the changed inputs {changed_ids:?}: include `inputs_consumed` at their current hashes (or `retest.inputs`) and passing test evidence", t.get("retest_reason")),
            )
            .with_details(json!({"task": task_id, "changed_inputs": changed_ids, "acknowledged": changed_ids.iter().filter(|i| acknowledged(i) || explicit.contains(i)).collect::<Vec<_>>(), "tests_passed": passed})));
        }
    }
    Ok(json!({"task": task_id, "clears_retest": retest, "revalidated_inputs": changed_ids}))
}

/// **Re-delivery acknowledges a change for work that never started** (`context::compile_tolerant`): when task `t` is
/// not claimed and never was (no claim row), its only stale artefact was the packet, and a packet compiled at the
/// current inputs delivers them. Clears `retest_required` and records how (`staleness.resolved`). Returns whether it
/// wrote.
pub fn acknowledge_on_redelivery(p: &Project, task_id: &str, packet: &Value) -> Result<bool> {
    let store = RecordStore::load(&p.root);
    let Some(t) = store.get(task_id) else {
        return Ok(false);
    };
    if t.data.get("retest_required").and_then(|v| v.as_bool()) != Some(true) {
        return Ok(false);
    }
    if !matches!(
        t.get("task_status").as_str(),
        "READY" | "BLOCKED" | "DRAFT" | "WAITING_HUMAN"
    ) {
        return Ok(false);
    }
    if crate::orchestration::claims::get(p, task_id)
        .ok()
        .flatten()
        .is_some()
    {
        return Ok(false);
    }
    let supplied = packet["input_hashes"]
        .as_object()
        .cloned()
        .unwrap_or_default();
    let all_current = t.data["staleness"]["inputs_changed"]
        .as_array()
        .map(|a| {
            a.iter().all(|x| {
                let id = x["id"].as_str().unwrap_or("");
                match x["to"].as_str() {
                    Some(to) => supplied.get(id).and_then(|v| v.as_str()) == Some(to),
                    None => !supplied.contains_key(id),
                }
            })
        })
        .unwrap_or(false);
    if !all_current || packet["delivery_state"] != "COMPLETE" {
        return Ok(false);
    }
    let mut touched = vec![];
    save_set(
        p,
        task_id,
        |r| {
            r.set("retest_required", json!(false));
            let mut s = r.data.get("staleness").cloned().unwrap_or(json!({}));
            s["stale"] = json!(false);
            s["resolved"] = json!({"by": "re-delivery", "packet_hash": packet["packet_hash"], "at": now_iso(),
                "note": "the task had not started work; its context packet now delivers every changed input at its current version"});
            r.set("staleness", s);
            true
        },
        &mut touched,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn staleness_accumulates_changes_and_is_idempotent() {
        let c1 = InputChange {
            id: "REQ-0001".into(),
            from: Some("a".into()),
            to: Some("b".into()),
        };
        let cause = Cause::Cit("CIT-0001".into());
        let why: BTreeSet<String> = ["consumes REQ-0001".to_string()].into_iter().collect();
        let s1 =
            merged_staleness(None, std::slice::from_ref(&c1), &cause, &why, json!({})).unwrap();
        assert_eq!(s1["stale"], true);
        assert_eq!(s1["reason"], "CIT CIT-0001");
        assert!(
            merged_staleness(
                Some(&s1),
                std::slice::from_ref(&c1),
                &cause,
                &why,
                json!({})
            )
            .is_none(),
            "an already recorded change writes nothing"
        );
        let c2 = InputChange {
            id: "REQ-0001".into(),
            from: Some("b".into()),
            to: Some("c".into()),
        };
        let direct = Cause::Direct {
            detected_by: "gov cit propagate".into(),
        };
        let s2 = merged_staleness(Some(&s1), &[c2], &direct, &why, json!({})).unwrap();
        assert_eq!(s2["inputs_changed"].as_array().unwrap().len(), 2);
        assert_eq!(s2["causes"].as_array().unwrap().len(), 2);
    }

    #[test]
    fn receipts_name_consumed_hashes() {
        let r = crate::records::parse_record_text(
            "id: RPT-0001\ntype: report\ninputs_consumed: ['REQ-0001@abc123abc123', {id: D-0001, content_hash: def456def456}]\n",
            "spec/reports/RPT-0001.yaml",
        )
        .unwrap();
        let h = receipt_hashes(&r);
        assert_eq!(h.get("REQ-0001").map(|s| s.as_str()), Some("abc123abc123"));
        assert_eq!(h.get("D-0001").map(|s| s.as_str()), Some("def456def456"));
    }
}
