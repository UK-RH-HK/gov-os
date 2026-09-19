//! Dynamic task DAG (framework §41-44): runnable/blocked sets, longest chain, cycles, human-gate dependencies, replan.
//!
//! Task-contract fields that order or gate work (Contract v3:563-566, BC-P2-14):
//! * `dependencies` and `blocks` are both ordering edges — `A.blocks = [B]` means B waits for A exactly as if
//!   `B.dependencies` contained A (cycles and the longest chain see both);
//! * `required_data`, `required_tools` and `required_skills` gate readiness: a task whose required input does not
//!   resolve ([`InputResolver`]) is blocked, with the reason, until it does.
use crate::orchestration::readiness;
use crate::records::{save_record, Record, RecordStore};
use crate::util::today;
use crate::{Project, Result};
use serde_json::{json, Value};
use std::cell::OnceCell;
use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Clone, serde::Serialize)]
pub struct DagView {
    pub runnable: Vec<String>,
    pub blocked: Vec<Value>,
    pub waiting_human: Vec<Value>,
    pub done: Vec<String>,
    pub longest_chain: Vec<String>,
    pub cycles: Vec<Vec<String>>,
    pub per_feature: Value,
    pub human_gate_dependencies: Vec<Value>,
    pub counts: Value,
    pub missing_dependencies: Vec<Value>,
    /// `blocks` entries naming a task that does not exist.
    pub dangling_blocks: Vec<Value>,
}

/// Lifecycle statuses that make a governed record unavailable as a current input (AUTHORITY_POLICY
/// `retrieval_default_excludes_statuses`).
fn excluded_statuses(p: &Project) -> Vec<String> {
    let v = p
        .policies()
        .get_list("AUTHORITY_POLICY", "retrieval_default_excludes_statuses");
    if v.is_empty() {
        ["SUPERSEDED", "HISTORICAL", "REJECTED", "RETIRED", "LEGACY"]
            .iter()
            .map(|s| s.to_string())
            .collect()
    } else {
        v
    }
}

/// Resolves a task's required inputs (Contract v3:564 "scenarios/data", :566 "required skills/tools"). Registries
/// are read once per resolver and only when a task needs them.
pub struct InputResolver<'a> {
    p: &'a Project,
    store: &'a RecordStore,
    excluded: Vec<String>,
    registry: OnceCell<BTreeMap<String, String>>,
    plugins: OnceCell<BTreeMap<String, String>>,
    skills: OnceCell<Vec<Value>>,
    files: OnceCell<Vec<String>>,
}

impl<'a> InputResolver<'a> {
    pub fn new(p: &'a Project, store: &'a RecordStore) -> Self {
        InputResolver {
            p,
            store,
            excluded: excluded_statuses(p),
            registry: OnceCell::new(),
            plugins: OnceCell::new(),
            skills: OnceCell::new(),
            files: OnceCell::new(),
        }
    }
    /// A governed record (any type; typically `data`) in a current lifecycle status, or a repository path / glob
    /// that exists. `Err` carries the reason it is unavailable.
    pub fn data(&self, d: &str) -> std::result::Result<Value, String> {
        if crate::records::id_regex().is_match(d) {
            if let Some(r) = self.store.get(d) {
                let st = r.status();
                if self.excluded.contains(&st) {
                    return Err(format!("required data {d} is {st} (not a current input)"));
                }
                return Ok(json!({"id": d, "resolved": "record", "path": r.path, "status": st}));
            }
        }
        if std::path::Path::new(d).components().any(|c| {
            !matches!(
                c,
                std::path::Component::Normal(_) | std::path::Component::CurDir
            )
        }) {
            return Err(format!(
                "required data {d} is neither a governed record nor a path inside the repository"
            ));
        }
        if d.contains('*') || d.contains('?') {
            let files = self.files.get_or_init(|| {
                crate::paths::iter_repo_files(&self.p.root, false)
                    .into_iter()
                    .map(|(_, rel)| rel)
                    .collect()
            });
            if let Some(f) = files.iter().find(|f| crate::util::glob_match(d, f)) {
                return Ok(json!({"id": d, "resolved": "path", "path": f}));
            }
        } else if self.p.root.join(d).exists() {
            return Ok(json!({"id": d, "resolved": "path", "path": d}));
        }
        Err(format!(
            "required data {d} is not available (no governed record or repository path)"
        ))
    }
    /// A tool registered in the kernel/project tool registry, the MCP registry or as a capability plugin, and active.
    pub fn tool(&self, t: &str) -> std::result::Result<Value, String> {
        let reg = self.registry.get_or_init(|| {
            let mut m = BTreeMap::new();
            let mut tools = crate::tools::kernel_tools(self.p);
            tools.extend(crate::tools::project_tools(self.p));
            for x in tools {
                if let Some(id) = x["tool_id"].as_str() {
                    m.insert(
                        id.to_string(),
                        x["status"].as_str().unwrap_or("").to_string(),
                    );
                }
            }
            for s in crate::tools::mcp_servers(self.p) {
                if let Some(id) = s["id"].as_str() {
                    m.entry(id.to_string())
                        .or_insert(s["status"].as_str().unwrap_or("").to_string());
                }
            }
            m
        });
        let status = match reg.get(t) {
            Some(s) => Some(s.clone()),
            None => self
                .plugins
                .get_or_init(|| {
                    crate::tools::plugin_tools(self.p)
                        .0
                        .into_iter()
                        .filter_map(|x| {
                            x["tool_id"].as_str().map(|id| {
                                (
                                    id.to_string(),
                                    x["status"].as_str().unwrap_or("").to_string(),
                                )
                            })
                        })
                        .collect()
                })
                .get(t)
                .cloned(),
        };
        match status {
            Some(s) if s == "active" => Ok(json!({"id": t, "status": s})),
            Some(s) => Err(format!("required tool {t} is registered but {s}, not active")),
            None => Err(format!("required tool {t} is not registered (tool registry, MCP registry or capability plugins); raise a tooling task or register it (`gov tools install`)")),
        }
    }
    /// A kernel or project skill, not in a retired lifecycle status.
    pub fn skill(&self, s: &str) -> std::result::Result<Value, String> {
        let skills = self
            .skills
            .get_or_init(|| crate::skills::list_skills(self.p));
        match skills.iter().find(|k| k["id"].as_str() == Some(s)) {
            Some(k) => {
                let st = k["status"].as_str().unwrap_or("ACTIVE").to_uppercase();
                if self.excluded.contains(&st) {
                    Err(format!("required skill {s} is {st}"))
                } else {
                    Ok(json!({"id": s, "version": k["version"], "source": k["_source"]}))
                }
            }
            None => Err(format!("required skill {s} is not registered (capability gap: `gov skills resolve <task>`)")),
        }
    }
    /// Every unavailable required input of `t`, as blocking reasons.
    pub fn gaps(&self, t: &Record) -> Vec<String> {
        let mut out = vec![];
        for d in t.list("required_data") {
            if let Err(e) = self.data(&d) {
                out.push(e);
            }
        }
        for x in t.list("required_tools") {
            if let Err(e) = self.tool(&x) {
                out.push(e);
            }
        }
        for x in t.list("required_skills") {
            if let Err(e) = self.skill(&x) {
                out.push(e);
            }
        }
        out
    }
}

/// Resolution state of each required input of `t` (for presentation, e.g. the context packet).
pub fn required_inputs(p: &Project, store: &RecordStore, t: &Record) -> Value {
    let r = InputResolver::new(p, store);
    let row = |id: &str, res: std::result::Result<Value, String>| match res {
        Ok(v) => json!({"id": id, "available": true, "resolution": v}),
        Err(e) => json!({"id": id, "available": false, "reason": e}),
    };
    json!({
        "required_data": t.list("required_data").iter().map(|d| row(d, r.data(d))).collect::<Vec<_>>(),
        "required_tools": t.list("required_tools").iter().map(|d| row(d, r.tool(d))).collect::<Vec<_>>(),
        "required_skills": t.list("required_skills").iter().map(|d| row(d, r.skill(d))).collect::<Vec<_>>(),
    })
}

pub fn compute(p: &Project) -> Result<DagView> {
    let store = RecordStore::load(&p.root);
    let tasks: Vec<&crate::records::Record> = store.of_type("task");
    let ids: BTreeSet<String> = tasks.iter().map(|t| t.id()).collect();
    let enforce = p
        .project_policy()
        .get("readiness")
        .and_then(|r| r.get("enforce_pre_implementation_cells"))
        .and_then(|v| v.as_bool())
        .unwrap_or(true);
    let gates: BTreeMap<String, String> = store
        .of_type("human-gate")
        .into_iter()
        .map(|g| (g.id(), g.get("gate_status")))
        .collect();
    let status_of: BTreeMap<String, String> = tasks
        .iter()
        .map(|t| (t.id(), t.get("task_status")))
        .collect();
    // `A.blocks = [B]` is the edge B -> A: B waits for A
    let mut blocked_by: BTreeMap<String, Vec<String>> = BTreeMap::new();
    let mut dangling_blocks = vec![];
    for t in &tasks {
        for b in t.list("blocks") {
            if ids.contains(&b) {
                blocked_by.entry(b).or_default().push(t.id());
            } else {
                dangling_blocks.push(json!({"task": t.id(), "blocks": b}));
            }
        }
    }
    let inputs = InputResolver::new(p, &store);
    let mut runnable = vec![];
    let mut blocked = vec![];
    let mut waiting = vec![];
    let mut done = vec![];
    let mut missing = vec![];
    let mut gate_deps = vec![];
    let mut per_feature: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for t in &tasks {
        let id = t.id();
        let st = t.get("task_status");
        per_feature
            .entry(t.get("feature"))
            .or_default()
            .push(id.clone());
        if st == "DONE" || st == "CANCELLED" {
            done.push(id);
            continue;
        }
        let mut reasons = vec![];
        for d in t.list("dependencies") {
            match status_of.get(&d) {
                Some(s) if s == "DONE" => {}
                Some(s) => reasons.push(format!("dependency {d} is {s}")),
                None => {
                    if ids.contains(&d) {
                        reasons.push(format!("dependency {d} unknown status"));
                    } else {
                        missing.push(json!({"task": id, "dependency": d}));
                        reasons.push(format!("dependency {d} missing"));
                    }
                }
            }
        }
        for b in blocked_by.get(&id).cloned().unwrap_or_default() {
            let s = status_of.get(&b).cloned().unwrap_or_default();
            if s != "DONE" {
                reasons.push(format!(
                    "blocked by {b} (its `blocks` lists {id}); {b} is {s}"
                ));
            }
        }
        reasons.extend(inputs.gaps(t));
        let gate = t.get("human_gate");
        if !gate.is_empty() {
            let gs = gates.get(&gate).cloned().unwrap_or("MISSING".into());
            gate_deps.push(json!({"task": id, "gate": gate, "gate_status": gs}));
            if gs == "PENDING" || gs == "PRESENTED" {
                waiting.push(json!({"task": id, "gate": gate}));
                continue;
            }
        }
        if enforce && t.get("class") == "implementation" && !t.get("feature").is_empty() {
            if let Some(f) = store.get(&t.get("feature")) {
                let r = readiness::evaluate(p, f);
                if !r.pre_implementation_ok {
                    reasons.push(format!(
                        "feature {} pre-implementation readiness cells missing: {}",
                        f.id(),
                        r.pre_implementation_gaps.join(", ")
                    ));
                }
            }
        }
        if t.get("class") == "implementation" {
            // TEST_POLICY.implementation_task_requires: scenarios and acceptance tests must be declared (task or feature)
            let feature = store
                .get(&t.get("feature"))
                .filter(|f| f.rtype() == "feature");
            let has_scn = !t.list("scenarios").is_empty()
                || feature
                    .map(|f| !f.list("scenarios").is_empty())
                    .unwrap_or(false);
            let declared_tests: Vec<String> = {
                let mut v = t.list("acceptance_tests");
                if let Some(f) = feature {
                    v.extend(f.list("acceptance_tests"));
                }
                if let Some(f) = feature {
                    v.extend(
                        store
                            .of_type("test-obligation")
                            .iter()
                            .filter(|o| o.get("feature") == f.id())
                            .map(|o| o.id()),
                    );
                }
                v
            };
            for req in p
                .policies()
                .get_list("TEST_POLICY", "implementation_task_requires")
            {
                match req.as_str() {
                    "scenarios_present" => {
                        if !has_scn {
                            reasons.push("TEST_POLICY.implementation_task_requires: no scenarios declared on the task or its feature".into());
                        }
                    }
                    "acceptance_tests_declared" if declared_tests.is_empty() => {
                        reasons.push("TEST_POLICY.implementation_task_requires: no acceptance tests declared on the task or its feature".into());
                    }
                    _ => {}
                }
            }
            // TEST_POLICY.independent_test_author_required_for: declared obligations of those families must be independent
            let indep = p
                .policies()
                .get_list("TEST_POLICY", "independent_test_author_required_for");
            for tid in &declared_tests {
                if let Some(o) = store.get(tid) {
                    if o.rtype() == "test-obligation"
                        && indep.contains(&o.get("family"))
                        && !o
                            .data
                            .get("independent_of_implementer")
                            .and_then(|v| v.as_bool())
                            .unwrap_or(false)
                    {
                        reasons.push(format!("{tid} ({}) must be authored independently of the implementer (TEST_POLICY.independent_test_author_required_for)", o.get("family")));
                    }
                }
            }
        }
        if t.data
            .get("retest_required")
            .and_then(|v| v.as_bool())
            .unwrap_or(false)
        {
            reasons.push("retest required after CIT propagation".into());
        }
        if reasons.is_empty() {
            if st == "DRAFT" {
                blocked.push(json!({"task": id, "reasons": ["DRAFT: promote with `gov task status <id> READY`"]}));
            } else {
                runnable.push(id);
            }
        } else {
            blocked.push(json!({"task": id, "reasons": reasons}));
        }
    }
    // cycles + longest chain over open tasks
    let open: BTreeSet<String> = tasks
        .iter()
        .filter(|t| !matches!(t.get("task_status").as_str(), "DONE" | "CANCELLED"))
        .map(|t| t.id())
        .collect();
    let deps: BTreeMap<String, Vec<String>> = tasks
        .iter()
        .map(|t| {
            let mut d: Vec<String> = t
                .list("dependencies")
                .into_iter()
                .chain(blocked_by.get(&t.id()).cloned().unwrap_or_default())
                .filter(|d| open.contains(d))
                .collect();
            d.sort();
            d.dedup();
            (t.id(), d)
        })
        .collect();
    let mut cycles = vec![];
    let mut color: BTreeMap<String, u8> = BTreeMap::new();
    fn dfs(
        n: &str,
        deps: &BTreeMap<String, Vec<String>>,
        color: &mut BTreeMap<String, u8>,
        stack: &mut Vec<String>,
        cycles: &mut Vec<Vec<String>>,
    ) {
        color.insert(n.to_string(), 1);
        stack.push(n.to_string());
        for d in deps.get(n).cloned().unwrap_or_default() {
            match color.get(&d).copied().unwrap_or(0) {
                0 => dfs(&d, deps, color, stack, cycles),
                1 => {
                    let pos = stack.iter().position(|x| x == &d).unwrap_or(0);
                    cycles.push(stack[pos..].to_vec());
                }
                _ => {}
            }
        }
        stack.pop();
        color.insert(n.to_string(), 2);
    }
    for n in &open {
        if color.get(n).copied().unwrap_or(0) == 0 {
            let mut st = vec![];
            dfs(n, &deps, &mut color, &mut st, &mut cycles);
        }
    }
    let mut memo: BTreeMap<String, Vec<String>> = BTreeMap::new();
    fn longest(
        n: &str,
        deps: &BTreeMap<String, Vec<String>>,
        memo: &mut BTreeMap<String, Vec<String>>,
        depth: usize,
    ) -> Vec<String> {
        if let Some(v) = memo.get(n) {
            return v.clone();
        }
        if depth > 500 {
            return vec![n.to_string()];
        }
        let mut best: Vec<String> = vec![];
        for d in deps.get(n).cloned().unwrap_or_default() {
            let c = longest(&d, deps, memo, depth + 1);
            if c.len() > best.len() {
                best = c;
            }
        }
        let mut out = best;
        out.push(n.to_string());
        memo.insert(n.to_string(), out.clone());
        out
    }
    let mut longest_chain: Vec<String> = vec![];
    if cycles.is_empty() {
        for n in &open {
            let c = longest(n, &deps, &mut memo, 0);
            if c.len() > longest_chain.len() {
                longest_chain = c;
            }
        }
    }
    let counts = json!({"total": tasks.len(), "runnable": runnable.len(), "blocked": blocked.len(), "waiting_human": waiting.len(), "done": done.len(), "open": open.len()});
    let pf: Value = json!(per_feature);
    Ok(DagView {
        runnable,
        blocked,
        waiting_human: waiting,
        done,
        longest_chain,
        cycles,
        per_feature: pf,
        human_gate_dependencies: gate_deps,
        counts,
        missing_dependencies: missing,
        dangling_blocks,
    })
}

/// Recompute and persist READY/BLOCKED/WAITING_HUMAN for open non-DRAFT tasks.
pub fn replan(p: &Project) -> Result<Value> {
    crate::orchestration::control::guard_write(p, "replan")?;
    let view = compute(p)?;
    let mut store = RecordStore::load(&p.root);
    let mut changed = vec![];
    let blocked_ids: BTreeSet<String> = view
        .blocked
        .iter()
        .filter_map(|b| b["task"].as_str().map(|s| s.to_string()))
        .collect();
    let waiting_ids: BTreeSet<String> = view
        .waiting_human
        .iter()
        .filter_map(|b| b["task"].as_str().map(|s| s.to_string()))
        .collect();
    let ids: Vec<String> = store.of_type("task").iter().map(|t| t.id()).collect();
    for id in ids {
        let rec = store.get_mut(&id).unwrap();
        let st = rec.get("task_status");
        let target = if view.runnable.contains(&id) {
            "READY"
        } else if waiting_ids.contains(&id) {
            "WAITING_HUMAN"
        } else if blocked_ids.contains(&id) && st != "DRAFT" {
            "BLOCKED"
        } else {
            continue;
        };
        if matches!(
            st.as_str(),
            "DONE" | "CANCELLED" | "IN_PROGRESS" | "CLAIMED" | "REVIEW"
        ) {
            continue;
        }
        if st != target {
            rec.set("task_status", json!(target));
            rec.set("updated", json!(today()));
            save_record(&p.root, rec)?;
            changed.push(json!({"task": id, "from": st, "to": target}));
        }
    }
    Ok(
        json!({"changed": changed, "runnable": view.runnable, "blocked": view.blocked.len(), "waiting_human": view.waiting_human.len(), "cycles": view.cycles}),
    )
}
