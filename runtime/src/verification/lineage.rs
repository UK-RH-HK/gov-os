//! **Orphan / dead-output and unexplained-output detection** (Contract v3 W7, lines 1138-1144; BC-P2-22; the G5
//! "audits end-to-end lineage and orphan states" duty of W12 line 1191).
//!
//! Every W7 class is detected **by name** — the finding names the record or file, never only a count — from the
//! governed records themselves (canonical edges, `crate::graph::lineage`), version control (the governance baseline)
//! and, where available, the code graph of the derived index:
//!
//! | W7 bullet (Contract v3) | kind | orphan when |
//! |---|---|---|
//! | 1139 completed output, expected consumers, no actual consumer | `unconsumed-output` | a current record declares `consumers` and no other record consumes it (or a declared consumer does not exist) |
//! | 1140 requirement/spec without downstream implementation/test path | `spec-without-downstream-path` | a current requirement/scenario that no task, report, change, code, test obligation or test reaches |
//! | 1141 research expected to feed a decision, never consumed | `unconsumed-research` | complete research/experiment output no decision (or change) cites — the declared target decision was decided without it, does not exist, or none was ever named |
//! | 1142 acceptance test without requirement/scenario | `unjustified-acceptance-test` | an acceptance-level test obligation linked to no current requirement or scenario |
//! | 1143 implementation/code without active requirement/decision/spec justification | `unjustified-code` | a source/test file that no governed work produced (traced to an active spec record), no current spec names, no committed change wrote, that no justified code depends on, and that is not part of the governance baseline |
//! | 1144 orphans produce governed investigation/remediation, not silent deletion | — | [`generate_remediation`]: one linked investigation task per orphan, idempotent; nothing is ever deleted |
//!
//! Records the remediation itself creates (investigation tasks, `generated_by: health:lineage_orphans`) never count
//! as a consumer, implementation, test or justification, so generating remediation never hides an orphan: an orphan
//! stays reported until it is actually linked or retired through governed work.
use crate::graph::lineage::{record_edges, NON_CURRENT_STATUSES};
use crate::memory::db::RuntimeDb;
use crate::records::{Record, RecordStore};
use crate::util::{now_iso, sha256_hex};
use crate::{Project, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet, VecDeque};

/// The governance-suite family that owns W7 detection.
pub const FAMILY: &str = "lineage_orphans";
/// `generated_by` of the investigation tasks [`generate_remediation`] creates.
pub const GENERATOR: &str = "health:lineage_orphans";

pub const KIND_UNCONSUMED_OUTPUT: &str = "unconsumed-output";
pub const KIND_SPEC_WITHOUT_PATH: &str = "spec-without-downstream-path";
pub const KIND_UNCONSUMED_RESEARCH: &str = "unconsumed-research";
pub const KIND_UNJUSTIFIED_TEST: &str = "unjustified-acceptance-test";
pub const KIND_UNJUSTIFIED_CODE: &str = "unjustified-code";

/// Every W7 kind with the Contract v3 line that requires it.
pub const KINDS: &[(&str, &str)] = &[
    (KIND_UNCONSUMED_OUTPUT, "Contract v3:1139"),
    (KIND_SPEC_WITHOUT_PATH, "Contract v3:1140"),
    (KIND_UNCONSUMED_RESEARCH, "Contract v3:1141"),
    (KIND_UNJUSTIFIED_TEST, "Contract v3:1142"),
    (KIND_UNJUSTIFIED_CODE, "Contract v3:1143"),
];

/// Record types whose current records justify implementation (an active requirement, decision or specification).
pub const JUSTIFYING_TYPES: &[&str] = &[
    "requirement",
    "decision",
    "feature",
    "scenario",
    "interface",
    "architecture",
    "data",
    "security",
    "performance",
    "workflow",
    "project",
    "cit",
    "research",
    "experiment",
];

/// Record types that are specifications requiring a downstream implementation or test path (W7 line 1140).
pub const SPEC_TYPES: &[&str] = &["requirement", "scenario"];
/// Record types that are research outputs expected to feed decisions (W7 line 1141).
pub const RESEARCH_TYPES: &[&str] = &["research", "experiment"];
/// Record types that are governed execution work (an implementation path).
pub const WORK_TYPES: &[&str] = &["task", "report", "cit"];
/// Test families at acceptance level (the families TEST_POLICY requires an independent author for, plus acceptance).
pub const ACCEPTANCE_FAMILIES: &[&str] = &["acceptance", "scenario", "system"];
/// Repository-contract classes that are implementation/code (W7 line 1143).
pub const CODE_CLASSES: &[&str] = &["source", "test"];

// Edge types by which a node depends on the node it points at (reading upstream), and by which a node affects or
// produces what it points at — the same two sets impact traversal uses (`crate::graph`).
use crate::graph::{IMPACT_IN, IMPACT_OUT};

/// One detected orphan.
#[derive(Debug, Clone)]
pub struct Orphan {
    pub kind: &'static str,
    pub subject: String,
    pub subject_type: String,
    pub path: Option<String>,
    pub severity: &'static str,
    pub message: String,
    pub remediation: String,
    pub detail: Value,
}

impl Orphan {
    /// Stable identity of the orphan: the same kind and subject always yield the same key (remediation idempotency).
    pub fn key(&self) -> String {
        key_of(self.kind, &self.subject)
    }
    /// The governance-suite finding for this orphan.
    pub fn finding(&self, family: &str) -> Value {
        json!({"severity": self.severity, "family": family, "message": self.message, "path": self.path,
            "orphan": {"kind": self.kind, "subject": self.subject, "subject_type": self.subject_type, "key": self.key(),
                       "contract": KINDS.iter().find(|(k, _)| *k == self.kind).map(|(_, c)| *c), "remediation": self.remediation, "detail": self.detail}})
    }
}

pub fn key_of(kind: &str, subject: &str) -> String {
    format!(
        "W7-{}",
        &sha256_hex(format!("{kind}\u{1f}{subject}").as_bytes())[..16]
    )
}

/// The detection result.
#[derive(Debug, Clone)]
pub struct Report {
    pub orphans: Vec<Orphan>,
    /// Source/test files that predate governance and are not (yet) linked to an active requirement/decision/spec.
    pub baseline_unlinked: Vec<String>,
    pub baseline: Value,
    pub detail: Value,
}

fn archived(r: &Record) -> bool {
    r.problems.iter().any(|p| p == "archived")
}

/// A record the remediation of this module generated: never a consumer, implementation, test or justification.
pub fn is_generated(r: &Record) -> bool {
    r.get("generated_by") == GENERATOR
}

/// Current, live governed work or specification: not archived, not superseded/historical/retired, not cancelled.
fn live(r: &Record) -> bool {
    !archived(r)
        && !NON_CURRENT_STATUSES.contains(&r.status().as_str())
        && r.get("task_status") != "CANCELLED"
}

/// Canonical edges between governed records, with the edges declared by (or touching) generated remediation removed.
struct Graph {
    out: BTreeMap<String, Vec<(String, String, String)>>,
    inn: BTreeMap<String, Vec<(String, String, String)>>,
}

impl Graph {
    fn build(store: &RecordStore) -> Graph {
        let generated: BTreeSet<String> = store
            .records
            .iter()
            .filter(|r| is_generated(r))
            .map(|r| r.id())
            .collect();
        let mut out: BTreeMap<String, Vec<(String, String, String)>> = BTreeMap::new();
        let mut inn: BTreeMap<String, Vec<(String, String, String)>> = BTreeMap::new();
        for (s, t, d, by) in record_edges(store) {
            if generated.contains(&by) || generated.contains(&s) || generated.contains(&d) {
                continue;
            }
            out.entry(s.clone())
                .or_default()
                .push((t.clone(), d.clone(), by.clone()));
            inn.entry(d).or_default().push((t, s, by));
        }
        Graph { out, inn }
    }
    fn out_of(&self, n: &str) -> &[(String, String, String)] {
        self.out.get(n).map(|v| v.as_slice()).unwrap_or(&[])
    }
    fn in_of(&self, n: &str) -> &[(String, String, String)] {
        self.inn.get(n).map(|v| v.as_slice()).unwrap_or(&[])
    }
}

// ------------------------------------------------------------------------------------------ governance baseline

/// The governance baseline: the repository state at which the project came under governance (the commit that first
/// recorded `governance/framework.lock`, and the adoption A0 baseline commit when the project was adopted), plus
/// every path the adoption migration moved existing content to. Code in it is adopted as it was, not produced by
/// governed work; it is reported as baseline, never as unexplained output.
#[derive(Debug, Clone, Default)]
pub struct Baseline {
    pub available: bool,
    pub commits: Vec<String>,
    pub paths: BTreeSet<String>,
    pub adoption_moves: BTreeSet<String>,
    pub note: String,
}

impl Baseline {
    pub fn contains(&self, rel: &str) -> bool {
        self.paths.contains(rel) || self.adoption_moves.contains(rel)
    }
    pub fn to_value(&self) -> Value {
        json!({"available": self.available, "commits": self.commits, "paths": self.paths.len(), "adoption_moves": self.adoption_moves.len(), "note": self.note})
    }
}

/// The commits that define the governance baseline (see [`Baseline`]); empty when version control cannot say.
pub fn baseline_commits(p: &Project) -> Vec<String> {
    let mut commits = vec![];
    let (c, out, _) = p.git(&[
        "log",
        "--diff-filter=A",
        "--format=%H",
        "--",
        "governance/framework.lock",
    ]);
    if c == 0 {
        if let Some(first) = out.lines().filter(|l| !l.trim().is_empty()).last() {
            commits.push(first.trim().to_string());
        }
    }
    let a0 = p.root.join(crate::adopt::EVIDENCE).join("00-BASELINE.yaml");
    if let Ok(b) = crate::util::read_yaml(&a0) {
        if let Some(cm) = b["commit"].as_str() {
            let cm = cm.trim();
            if !cm.is_empty() && cm != "unknown" && !commits.iter().any(|x| x == cm) {
                commits.push(cm.to_string());
            }
        }
    }
    if commits.is_empty() && p.git_available() {
        // governance installed but not committed yet: everything committed so far predates it
        let (c, out, _) = p.git(&["rev-parse", "--verify", "HEAD"]);
        if c == 0 && !out.is_empty() {
            commits.push(out.trim().to_string());
        }
    }
    commits
}

pub fn governance_baseline(p: &Project) -> Baseline {
    let commits = baseline_commits(p);
    let mut b = Baseline {
        commits: commits.clone(),
        ..Default::default()
    };
    for cm in &commits {
        let (c, out, _) = p.git(&["ls-tree", "-r", "--name-only", cm]);
        if c == 0 {
            b.available = true;
            for l in out.lines() {
                let l = l.trim();
                if !l.is_empty() {
                    b.paths.insert(l.to_string());
                }
            }
        }
    }
    // content the adoption migration relocated is baseline content at its new path (A6 ledger, applied rows)
    let ledger = p
        .root
        .join(crate::adopt::EVIDENCE)
        .join("migration-ledger.jsonl");
    if let Ok(text) = crate::util::read_text(&ledger) {
        for line in text.lines() {
            let Ok(v) = serde_json::from_str::<Value>(line) else {
                continue;
            };
            if v["status"] != "applied" {
                continue;
            }
            for k in ["to", "original_archived_to"] {
                if let Some(t) = v["result"][k].as_str() {
                    b.adoption_moves
                        .insert(t.trim_start_matches("./").to_string());
                }
            }
        }
    }
    b.note = if b.available {
        format!(
            "governance baseline: {} commit(s), {} path(s), {} adoption move(s)",
            b.commits.len(),
            b.paths.len(),
            b.adoption_moves.len()
        )
    } else {
        "no version-control baseline: the repository is not under version control or governance was never committed; unexplained-code detection cannot tell baseline code from new code".into()
    };
    b
}

// ------------------------------------------------------------------------------------------------- detection

/// Run every W7 detection over the governed records (and the code graph when the index is available).
pub fn detect(p: &Project, store: &RecordStore, db: Option<&RuntimeDb>) -> Report {
    let g = Graph::build(store);
    let mut orphans = vec![];
    let mut counts: BTreeMap<&str, usize> = BTreeMap::new();
    unconsumed_outputs(store, &g, &mut orphans);
    let contract = p.contract();
    specs_without_path(
        &|f: &str| contract.decide(f).class(),
        store,
        &g,
        &mut orphans,
    );
    let research = unconsumed_research(store, &g, &mut orphans);
    let tests = unjustified_tests(store, &g, &mut orphans);
    let baseline = governance_baseline(p);
    let code = unjustified_code(p, store, &g, db, &baseline, &mut orphans);
    for o in &orphans {
        *counts.entry(o.kind).or_insert(0) += 1;
    }
    orphans.sort_by(|a, b| (a.kind, &a.subject).cmp(&(b.kind, &b.subject)));
    let baseline_unlinked: Vec<String> = code["baseline_unlinked"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let detail = json!({
        "orphans": orphans.len(),
        "by_kind": KINDS.iter().map(|(k, c)| (k.to_string(), json!({"count": counts.get(k).cloned().unwrap_or(0), "contract": c}))).collect::<serde_json::Map<String, Value>>(),
        "subjects": orphans.iter().map(|o| json!({"kind": o.kind, "subject": o.subject, "severity": o.severity, "key": o.key()})).collect::<Vec<_>>(),
        "research": research,
        "tests": tests,
        "code": code,
        "baseline": baseline.to_value(),
        "resolved_investigations": resolved_investigations(p, store),
    });
    Report {
        orphans,
        baseline_unlinked,
        baseline: baseline.to_value(),
        detail,
    }
}

/// W7 line 1139: current outputs that declare expected consumers of which none actually consumes them.
fn unconsumed_outputs(store: &RecordStore, g: &Graph, out: &mut Vec<Orphan>) {
    let live_tasks: Vec<String> = store
        .of_type("task")
        .into_iter()
        .filter(|t| live(t) && !is_generated(t))
        .map(|t| t.id())
        .collect();
    for r in &store.records {
        if !live(r) || is_generated(r) {
            continue;
        }
        let expected = r.list("consumers");
        if expected.is_empty() {
            continue;
        }
        let id = r.id();
        let mut actual: BTreeSet<String> = g
            .in_of(&id)
            .iter()
            .filter(|(t, s, by)| t == "CONSUMES" && by != &id && s != &id)
            .filter(|(_, s, _)| {
                store
                    .get(s)
                    .map(|x| live(x) && !is_generated(x))
                    .unwrap_or(false)
            })
            .map(|(_, s, _)| s.clone())
            .collect();
        // every task context packet carries every ACTIVE/PROVISIONAL architecture record (graph::IMPLICIT_CONSUMERS)
        if r.rtype() == "architecture"
            && crate::graph::IMPLICIT_INPUT_STATUSES.contains(&r.status().as_str())
        {
            actual.extend(live_tasks.iter().filter(|t| **t != id).cloned());
        }
        let missing: Vec<String> = expected
            .iter()
            .filter(|c| store.get(c).is_none())
            .cloned()
            .collect();
        let not_consuming: Vec<String> = expected
            .iter()
            .filter(|c| store.get(c).is_some() && !actual.contains(*c))
            .cloned()
            .collect();
        let detail = json!({"expected_consumers": expected, "actual_consumers": actual, "missing_consumers": missing, "declared_but_not_consuming": not_consuming});
        if actual.is_empty() || !missing.is_empty() {
            let mut why = vec![];
            if actual.is_empty() {
                why.push("no record consumes it".to_string());
            }
            if !missing.is_empty() {
                why.push(format!(
                    "declared consumer(s) {} do not exist",
                    missing.join(", ")
                ));
            }
            if !not_consuming.is_empty() {
                why.push(format!(
                    "declared consumer(s) {} do not declare it as an input",
                    not_consuming.join(", ")
                ));
            }
            out.push(Orphan {
                kind: KIND_UNCONSUMED_OUTPUT,
                subject: id.clone(),
                subject_type: r.rtype(),
                path: Some(r.path.clone()),
                severity: if r.status() == "ACTIVE" { "medium" } else { "low" },
                message: format!("orphan output: {id} ({}) declares expected consumers [{}] but {} (W7 unconsumed output)", r.rtype(), expected.join(", "), why.join("; ")),
                remediation: format!("have each expected consumer declare {id} as an input (required_inputs / interfaces / required_data), correct its `consumers`, or retire {id} through a CIT"),
                detail,
            });
        } else if !not_consuming.is_empty() {
            out.push(Orphan {
                kind: KIND_UNCONSUMED_OUTPUT,
                subject: id.clone(),
                subject_type: r.rtype(),
                path: Some(r.path.clone()),
                severity: "low",
                message: format!("{id} ({}) is consumed, but its declared consumer(s) {} do not declare it as an input (W7 expected vs actual consumers)", r.rtype(), not_consuming.join(", ")),
                remediation: format!("have {} declare {id} as an input, or remove them from {id}.consumers", not_consuming.join(", ")),
                detail,
            });
        }
    }
}

/// Nodes downstream of `id`: what depends on it (in-edges of impact-in types) and what it is validated by / affects.
fn downstream(g: &Graph, id: &str) -> Vec<String> {
    let mut v: Vec<String> = downstream_typed(g, id)
        .into_iter()
        .map(|(_, n)| n)
        .collect();
    v.sort();
    v.dedup();
    v
}

/// [`downstream`] with the edge type each node is reached by.
fn downstream_typed(g: &Graph, id: &str) -> Vec<(String, String)> {
    let mut v: Vec<(String, String)> = g
        .in_of(id)
        .iter()
        .filter(|(t, _, _)| IMPACT_IN.contains(&t.as_str()) || t == "VALIDATED_BY" || t == "TESTS")
        .map(|(t, s, _)| (t.clone(), s.clone()))
        .collect();
    v.extend(
        g.out_of(id)
            .iter()
            .filter(|(t, _, _)| t == "VALIDATED_BY" || t == "AFFECTS")
            .map(|(t, d, _)| (t.clone(), d.clone())),
    );
    v.sort();
    v.dedup();
    v
}

/// Report fields that make a closing report a **consumption receipt** (`context::receipt`, W5): the receipt states
/// what the work implemented, separately from what it consumed.
pub const RECEIPT_FIELDS: &[&str] = &[
    "receipt_validation",
    "requirements_implemented",
    "scenarios_implemented",
    "features_implemented",
    "inputs_consumed",
];

/// Was `task` closed under the consumption-receipt contract? Then its receipt — not its declarations — says what it
/// implemented.
pub fn closed_under_receipt(store: &RecordStore, task: &Record) -> bool {
    store
        .get(&task.get("closed_by_report"))
        .map(|r| RECEIPT_FIELDS.iter().any(|k| r.data.get(*k).is_some()))
        .unwrap_or(false)
}

/// Edge types by which planned (open) work declares the specification it will implement or verify.
const PLANNED_PATH_TYPES: &[&str] = &[
    "IMPLEMENTS",
    "GOVERNED_BY",
    "VALIDATED_BY",
    "TESTS",
    "AFFECTS",
];

/// **What counts as a downstream implementation path (W7 line 1140; W5 lines 1115-1119: consumption ≠
/// implementation; IF-1).** A node reached from a spec record through edge `t` is an implementation path when:
/// * a **report** (a closing receipt) `IMPLEMENTS` it — consuming it (`inputs_consumed` → `CONSUMES`) or applying it
///   is not implementing it;
/// * an **open task** plans it (`requirements`/`scenarios` → `GOVERNED_BY`/`VALIDATED_BY`, `implements`, `tests`);
///   a task that only consumes it (`required_inputs`) does not;
/// * a **DONE task** closed under the receipt contract never does by its own declarations (its receipt is the
///   statement of what it implemented); a DONE task closed before that contract (no receipt fields) is judged by its
///   declarations, as before;
/// * a **change transaction** `IMPLEMENTS` it.
fn work_implements(store: &RecordStore, r: &Record, t: &str) -> bool {
    match r.rtype().as_str() {
        "report" => t == "IMPLEMENTS",
        "cit" => t == "IMPLEMENTS",
        "task" => {
            if !PLANNED_PATH_TYPES.contains(&t) {
                return false;
            }
            r.get("task_status") != "DONE" || !closed_under_receipt(store, r)
        }
        _ => false,
    }
}

/// The implementation, test and code paths of one spec record (one hop through the scenarios that validate it).
#[derive(Debug, Clone, Default)]
pub struct SpecPaths {
    pub implementation: bool,
    pub test: bool,
    /// Production code (repository-contract class `source`) produced by the work that implements it, or code that
    /// names it.
    pub code: bool,
    pub via_scenarios: Vec<String>,
    pub implemented_by: Vec<String>,
}

fn spec_paths_of(
    file_class: &dyn Fn(&str) -> String,
    store: &RecordStore,
    g: &Graph,
    id: &str,
) -> SpecPaths {
    let direct = |id: &str| -> SpecPaths {
        let mut sp = SpecPaths::default();
        for (t, n) in downstream_typed(g, id) {
            if let Some(file) = n.strip_prefix("file:") {
                if file_class(file) == "test" {
                    sp.test = true;
                } else {
                    sp.implementation = true;
                    sp.code = true;
                }
                continue;
            }
            let Some(r) = store.get(&n) else { continue };
            if !live(r) || is_generated(r) {
                continue;
            }
            let rt = r.rtype();
            if WORK_TYPES.contains(&rt.as_str()) {
                if work_implements(store, r, &t) {
                    sp.implementation = true;
                    sp.implemented_by.push(n.clone());
                }
            } else if rt == "test-obligation" {
                sp.test = true;
            } else if rt == "scenario" && n != id {
                sp.via_scenarios.push(n.clone());
            }
        }
        sp
    };
    let mut sp = direct(id);
    for s in sp.via_scenarios.clone() {
        let s2 = direct(&s);
        sp.implementation |= s2.implementation;
        sp.test |= s2.test;
        sp.code |= s2.code;
        sp.implemented_by.extend(s2.implemented_by);
    }
    // code: what the implementing work produced (the report, or the task and its closing report)
    if !sp.code {
        for w in &sp.implemented_by {
            let mut producers = vec![w.clone()];
            if let Some(r) = store.get(w) {
                if r.rtype() == "task" {
                    let rep = r.get("closed_by_report");
                    if !rep.is_empty() {
                        producers.push(rep);
                    }
                }
            }
            let produced_code = producers.iter().any(|x| {
                g.out_of(x).iter().any(|(t, d, _)| {
                    t == "PRODUCES"
                        && d.strip_prefix("file:")
                            .map(|f| file_class(f) == "source")
                            .unwrap_or(false)
                })
            });
            if produced_code {
                sp.code = true;
                break;
            }
        }
    }
    sp.implemented_by.sort();
    sp.implemented_by.dedup();
    sp
}

/// W11 requirement→code and requirement→test traceability (Contract v3:1180-1181): every live, ACTIVE requirement with
/// its implementation, code and test paths (same path semantics as W7 detection).
pub fn requirement_paths(p: &Project, store: &RecordStore) -> Vec<Value> {
    let g = Graph::build(store);
    let contract = p.contract();
    let fc = |f: &str| contract.decide(f).class();
    store
        .of_type("requirement")
        .into_iter()
        .filter(|r| live(r) && !is_generated(r) && r.status() == "ACTIVE")
        .map(|r| {
            let sp = spec_paths_of(&fc, store, &g, &r.id());
            json!({"requirement": r.id(), "implementation": sp.implementation, "code": sp.code, "test": sp.test, "implemented_by": sp.implemented_by, "via_scenarios": sp.via_scenarios})
        })
        .collect()
}

/// W7 line 1140: current requirements/scenarios that nothing implements or tests.
fn specs_without_path(
    file_class: &dyn Fn(&str) -> String,
    store: &RecordStore,
    g: &Graph,
    out: &mut Vec<Orphan>,
) {
    for r in &store.records {
        let t = r.rtype();
        if !SPEC_TYPES.contains(&t.as_str()) || !live(r) || is_generated(r) {
            continue;
        }
        let id = r.id();
        let sp = spec_paths_of(file_class, store, g, &id);
        if sp.implementation || sp.test {
            continue;
        }
        let via = sp.via_scenarios.clone();
        // Severity: a current spec of a feature whose implementation work is already DONE was skipped by delivered
        // work — a delivery gap (medium). A spec no work has reached yet is visible, generates its investigation, and
        // does not degrade health on its own (low): an unplanned requirement is backlog, not a defect.
        let delivered: Vec<String> = features_of(store, g, r)
            .into_iter()
            .filter(|f| feature_has_done_work(store, g, f))
            .collect();
        let severity = if r.status() == "ACTIVE" && !delivered.is_empty() {
            "medium"
        } else {
            "low"
        };
        // consumption is not implementation: name the closing receipts that consumed it without implementing it
        let consumed_only: Vec<String> = g
            .in_of(&id)
            .iter()
            .filter(|(et, s, _)| {
                et == "CONSUMES"
                    && store
                        .get(s)
                        .map(|x| x.rtype() == "report" && live(x))
                        .unwrap_or(false)
            })
            .map(|(_, s, _)| s.clone())
            .collect();
        out.push(Orphan {
            kind: KIND_SPEC_WITHOUT_PATH,
            subject: id.clone(),
            subject_type: t.clone(),
            path: Some(r.path.clone()),
            severity,
            message: format!("orphan {t}: {id} ({}) has no downstream implementation or test path — no task, report, change or code implements it and no test obligation or test validates it{}{} (W7 requirement/spec without downstream path)", r.status(), if delivered.is_empty() { String::new() } else { format!(", although implementation work of its feature {} is DONE", delivered.join(", ")) }, if consumed_only.is_empty() { String::new() } else { format!("; closing receipt(s) {} consumed it without implementing it (consumption is not implementation, Contract v3:1115-1119)", consumed_only.join(", ")) }),
            remediation: format!("plan work for {id} (a task declaring it in `requirements`/`scenarios`), link the test that validates it, or retire it through a CIT"),
            detail: json!({"downstream": downstream(g, &id), "via_scenarios": via, "features_with_done_work": delivered, "consumed_without_implementation_by": consumed_only}),
        });
    }
}

/// The features a spec record belongs to: its own `feature`, and every feature that lists it.
fn features_of(store: &RecordStore, g: &Graph, r: &Record) -> Vec<String> {
    let id = r.id();
    let mut v: BTreeSet<String> = BTreeSet::new();
    for (t, d, _) in g.out_of(&id) {
        if t == "REALISES"
            && store
                .get(d)
                .map(|x| x.rtype() == "feature")
                .unwrap_or(false)
        {
            v.insert(d.clone());
        }
    }
    for (_, s, _) in g.in_of(&id) {
        if store
            .get(s)
            .map(|x| x.rtype() == "feature")
            .unwrap_or(false)
        {
            v.insert(s.clone());
        }
    }
    v.into_iter().collect()
}

/// Does a feature have DONE governed work realising it?
fn feature_has_done_work(store: &RecordStore, g: &Graph, feature: &str) -> bool {
    g.in_of(feature).iter().any(|(t, s, _)| {
        t == "REALISES"
            && store
                .get(s)
                .map(|x| {
                    x.rtype() == "task"
                        && x.get("task_status") == "DONE"
                        && live(x)
                        && !is_generated(x)
                })
                .unwrap_or(false)
    })
}

/// Ids a record cites without a relation field: decision evidence references and similar citation-only fields.
fn citations(r: &Record) -> Vec<String> {
    let mut v = vec![];
    for k in ["evidence_refs", "evidence", "research", "sources", "inputs"] {
        v.extend(r.list(k).into_iter().map(|x| {
            x.split('@')
                .next()
                .unwrap_or("")
                .trim()
                .trim_start_matches("file:")
                .to_string()
        }));
    }
    v
}

/// W7 line 1141: complete research/experiment output that no decision consumes.
fn unconsumed_research(store: &RecordStore, g: &Graph, out: &mut Vec<Orphan>) -> Value {
    let mut pending = vec![];
    let mut consumed = vec![];
    let mut incomplete = vec![];
    // decision/CIT → research citations through fields that are not relation fields
    let mut cited_by: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    for d in &store.records {
        if !matches!(d.rtype().as_str(), "decision" | "cit") || archived(d) {
            continue;
        }
        for c in citations(d) {
            cited_by.entry(c).or_default().insert(d.id());
        }
    }
    let decision_prefix = format!("{}-", crate::records::prefix_for("decision"));
    for r in &store.records {
        let t = r.rtype();
        if !RESEARCH_TYPES.contains(&t.as_str()) || !live(r) || is_generated(r) {
            continue;
        }
        let id = r.id();
        let outcome = if t == "experiment" {
            r.get("result")
        } else {
            r.get("conclusion")
        };
        if outcome.trim().is_empty() && r.data.get("result").map(|v| v.is_null()).unwrap_or(true) {
            incomplete.push(id.clone());
            continue;
        }
        // decisions (and change transactions) that consume it: any edge from one of them to it, or a citation
        let mut consumers: BTreeSet<String> = g
            .in_of(&id)
            .iter()
            .filter(|(et, s, _)| {
                et != "SUPERSEDES"
                    && store
                        .get(s)
                        .map(|x| matches!(x.rtype().as_str(), "decision" | "cit") && !archived(x))
                        .unwrap_or(false)
            })
            .map(|(_, s, _)| s.clone())
            .collect();
        if let Some(c) = cited_by.get(&id) {
            consumers.extend(c.iter().cloned());
        }
        // decisions the research declares it feeds (its own influences/affects/decision fields)
        let mut expected: Vec<String> = vec![];
        for k in ["influences", "affects", "decisions", "decision", "feeds"] {
            for x in r.list(k) {
                let x = x.split('@').next().unwrap_or("").trim().to_string();
                let is_decision = match store.get(&x) {
                    Some(d) => d.rtype() == "decision",
                    None => x.starts_with(&decision_prefix),
                };
                if is_decision && !expected.contains(&x) {
                    expected.push(x);
                }
            }
        }
        let mut problems = vec![];
        let mut sev = "low";
        for d in &expected {
            match store.get(d) {
                None => {
                    sev = "medium";
                    problems.push(format!(
                        "the decision it declares it feeds, {d}, does not exist"
                    ));
                }
                Some(dr) if consumers.contains(d) => {
                    let _ = dr;
                }
                Some(dr) if dr.status() == "ACTIVE" => {
                    sev = "medium";
                    problems.push(format!(
                        "{d} was decided without consuming it (it declares that it feeds {d})"
                    ));
                }
                Some(_) => pending.push(json!({"research": id, "decision": d})),
            }
        }
        if expected.is_empty() && consumers.is_empty() {
            problems.push("no decision consumes it and it names no decision it feeds".into());
        }
        if problems.is_empty() {
            if !consumers.is_empty() {
                consumed.push(json!({"research": id, "consumed_by": consumers}));
            }
            continue;
        }
        out.push(Orphan {
            kind: KIND_UNCONSUMED_RESEARCH,
            subject: id.clone(),
            subject_type: t.clone(),
            path: Some(r.path.clone()),
            severity: sev,
            message: format!("orphan {t}: {id} is complete but never consumed by a decision: {} (W7 research expected to feed a decision)", problems.join("; ")),
            remediation: format!("have the decision cite {id} (`derived_from` / `evidence_refs`), or record why it was not needed and retire it through a CIT"),
            detail: json!({"expected_decisions": expected, "consumed_by": consumers}),
        });
    }
    json!({"consumed": consumed, "pending_decisions": pending, "incomplete": incomplete})
}

/// W7 line 1142: acceptance-level test obligations linked to no current requirement or scenario; and test
/// obligations that validate nothing governed at all.
fn unjustified_tests(store: &RecordStore, g: &Graph, out: &mut Vec<Orphan>) -> Value {
    let listed_as_acceptance: BTreeSet<String> = store
        .records
        .iter()
        .filter(|r| !archived(r))
        .flat_map(|r| r.list("acceptance_tests"))
        .collect();
    let spec_kind = |n: &str| -> Option<String> {
        store
            .get(n)
            .filter(|r| live(r) && !is_generated(r))
            .map(|r| r.rtype())
    };
    let mut checked = 0;
    for r in store.of_type("test-obligation") {
        if !live(r) || is_generated(r) {
            continue;
        }
        checked += 1;
        let id = r.id();
        let family = r.get("family");
        let acceptance =
            ACCEPTANCE_FAMILIES.contains(&family.as_str()) || listed_as_acceptance.contains(&id);
        let mut neighbours: Vec<String> = g
            .out_of(&id)
            .iter()
            .filter(|(t, _, _)| t != "SUPERSEDES")
            .map(|(_, d, _)| d.clone())
            .collect();
        neighbours.extend(
            g.in_of(&id)
                .iter()
                .filter(|(t, _, _)| t != "SUPERSEDES")
                .map(|(_, s, _)| s.clone()),
        );
        let mut req_or_scn = false;
        let mut any_spec = false;
        for n in &neighbours {
            match spec_kind(n).as_deref() {
                Some("requirement") | Some("scenario") => {
                    req_or_scn = true;
                    any_spec = true;
                }
                Some("task") => {
                    any_spec = true;
                    // a task that declares this test and a requirement/scenario ties them together
                    let t = store.get(n).unwrap();
                    if t.list("requirements")
                        .iter()
                        .chain(t.list("scenarios").iter())
                        .any(|x| {
                            matches!(
                                spec_kind(x).as_deref(),
                                Some("requirement") | Some("scenario")
                            )
                        })
                    {
                        req_or_scn = true;
                    }
                }
                Some(k) if JUSTIFYING_TYPES.contains(&k) => any_spec = true,
                _ => {}
            }
        }
        if acceptance && !req_or_scn {
            out.push(Orphan {
                kind: KIND_UNJUSTIFIED_TEST,
                subject: id.clone(),
                subject_type: "test-obligation".into(),
                path: Some(r.path.clone()),
                severity: "medium",
                message: format!("orphan acceptance test: {id} (family '{family}') validates no requirement or scenario{} (W7 acceptance test without requirement/scenario)", if any_spec { " — its only links are to features, tasks or other records" } else { " — it is linked to nothing governed" }),
                remediation: format!("link {id} to the requirement or scenario it accepts (`scenario` / `tests` / the requirement's `acceptance_tests`), or retire it through a CIT"),
                detail: json!({"family": family, "linked": neighbours}),
            });
        } else if !acceptance && !any_spec {
            out.push(Orphan {
                kind: KIND_UNJUSTIFIED_TEST,
                subject: id.clone(),
                subject_type: "test-obligation".into(),
                path: Some(r.path.clone()),
                severity: "low",
                message: format!("{id} (family '{family}') validates nothing governed: it is linked to no requirement, scenario, feature, interface, decision or task (W7 unjustified test)"),
                remediation: format!("link {id} to what it validates, or retire it through a CIT"),
                detail: json!({"family": family, "linked": neighbours}),
            });
        }
    }
    json!({"test_obligations_checked": checked})
}

/// Does the live record `start` trace (upstream, through the canonical edges) to a current record of a justifying
/// type? Returns the justifying record's id.
fn traces_to_spec(
    store: &RecordStore,
    g: &Graph,
    start: &str,
    memo: &mut BTreeMap<String, Option<String>>,
) -> Option<String> {
    if let Some(m) = memo.get(start) {
        return m.clone();
    }
    let mut seen: BTreeSet<String> = BTreeSet::new();
    let mut q: VecDeque<(String, usize)> = VecDeque::new();
    q.push_back((start.to_string(), 0));
    let mut found = None;
    while let Some((n, hop)) = q.pop_front() {
        if !seen.insert(n.clone()) {
            continue;
        }
        let Some(r) = store.get(&n) else { continue };
        if !live(r) || is_generated(r) {
            continue;
        }
        let t = r.rtype();
        let current_cit = t != "cit" || r.get("cit_status") == "COMMITTED";
        if JUSTIFYING_TYPES.contains(&t.as_str()) && current_cit {
            found = Some(n.clone());
            break;
        }
        if hop >= 6 {
            continue;
        }
        for (t, d, _) in g.out_of(&n) {
            if IMPACT_IN.contains(&t.as_str()) && !d.starts_with("file:") {
                q.push_back((d.clone(), hop + 1));
            }
        }
        for (t, s, _) in g.in_of(&n) {
            if IMPACT_OUT.contains(&t.as_str()) && !s.starts_with("file:") {
                q.push_back((s.clone(), hop + 1));
            }
        }
    }
    memo.insert(start.to_string(), found.clone());
    found
}

/// W7 line 1143: implementation/code with no active requirement/decision/spec justification.
fn unjustified_code(
    p: &Project,
    store: &RecordStore,
    g: &Graph,
    db: Option<&RuntimeDb>,
    baseline: &Baseline,
    out: &mut Vec<Orphan>,
) -> Value {
    let contract = p.contract();
    let code: Vec<String> = crate::paths::iter_repo_files(&p.root, false)
        .into_iter()
        .map(|(_, rel)| rel)
        .filter(|rel| CODE_CLASSES.contains(&contract.decide(rel).class().as_str()))
        .collect();
    let code_set: BTreeSet<&String> = code.iter().collect();
    // justification per file: (how, by)
    let mut justified: BTreeMap<String, Value> = BTreeMap::new();
    let mut memo: BTreeMap<String, Option<String>> = BTreeMap::new();
    for f in &code {
        let node = format!("file:{f}");
        let mut linked: Vec<(String, String)> = g
            .in_of(&node)
            .iter()
            .map(|(t, s, _)| (t.clone(), s.clone()))
            .collect();
        linked.extend(
            g.out_of(&node)
                .iter()
                .map(|(t, d, _)| (t.clone(), d.clone())),
        );
        for (t, rid) in linked {
            if rid.starts_with("file:") {
                continue;
            }
            if let Some(spec) = traces_to_spec(store, g, &rid, &mut memo) {
                justified.insert(f.clone(), json!({"how": if spec == rid { "named by a current specification" } else { "produced by governed work traced to an active specification" }, "record": rid, "edge": t, "traces_to": spec}));
                break;
            }
        }
    }
    // a committed change transaction wrote it (the CIT is governed by its decision/gate)
    for c in store.of_type("cit") {
        if c.get("cit_status") != "COMMITTED" || !live(c) {
            continue;
        }
        let touched = c.data["execution"]["propagation"]["touched"]
            .as_array()
            .cloned()
            .unwrap_or_default();
        for t in touched {
            if let Some(t) = t.as_str() {
                if code_set.contains(&t.to_string()) && !justified.contains_key(t) {
                    justified.insert(
                        t.to_string(),
                        json!({"how": "written by a committed change transaction", "record": c.id()}),
                    );
                }
            }
        }
    }
    // supporting code: what justified code imports or calls (code graph of the derived index)
    let mut graph_available = false;
    if let Some(db) = db {
        if let Ok(rows) = db.query(
            "SELECT src, dst FROM edges WHERE type IN ('IMPORTS','CALLS') AND src LIKE 'file:%' AND dst LIKE 'file:%'",
            &[],
        ) {
            graph_available = true;
            let mut adj: BTreeMap<String, Vec<String>> = BTreeMap::new();
            for r in rows {
                let (Some(s), Some(d)) = (r["src"].as_str(), r["dst"].as_str()) else {
                    continue;
                };
                adj.entry(s.trim_start_matches("file:").to_string())
                    .or_default()
                    .push(d.trim_start_matches("file:").to_string());
            }
            let mut q: VecDeque<String> = justified.keys().cloned().collect();
            while let Some(f) = q.pop_front() {
                for d in adj.get(&f).cloned().unwrap_or_default() {
                    if !justified.contains_key(&d) && code_set.contains(&d) {
                        justified.insert(
                            d.clone(),
                            json!({"how": "supporting code of justified code", "record": format!("file:{f}")}),
                        );
                        q.push_back(d);
                    }
                }
            }
        }
    }
    let mut baseline_unlinked = vec![];
    let mut unexplained = vec![];
    for f in &code {
        if justified.contains_key(f) {
            continue;
        }
        if baseline.contains(f) {
            baseline_unlinked.push(f.clone());
            continue;
        }
        if !baseline.available {
            continue;
        }
        unexplained.push(f.clone());
        out.push(Orphan {
            kind: KIND_UNJUSTIFIED_CODE,
            subject: format!("file:{f}"),
            subject_type: contract.decide(f).class(),
            path: Some(f.clone()),
            severity: "medium",
            message: format!("unexplained code: {f} has no active requirement/decision/spec justification — no governed work produced it (report/task outputs traced to a current specification), no current specification names it, no committed change transaction wrote it, no justified code depends on it, and it is not part of the governance baseline (W7 unexplained output)"),
            remediation: format!("close the work that produced {f} with a report tracing it to its requirement/decision, have a specification name it, or remove it through a CIT (never silently)"),
            detail: json!({"class": contract.decide(f).class()}),
        });
    }
    json!({"files_checked": code.len(), "justified": justified.len(), "justifications": justified, "baseline_unlinked": baseline_unlinked,
           "unexplained": unexplained, "code_graph_available": graph_available, "baseline_available": baseline.available})
}

// ------------------------------------------------------------------------------------------------ remediation

/// **W7 line 1144 — orphans produce governed investigation/remediation, never silent deletion.** For every orphan
/// that has no investigation yet, create one linked investigation task: `READY`, class `validation`, designated for
/// the change controller (linking or retiring an orphan is a change), scoped to `spec/**`, never allowed to merge into
/// production, `investigates: {kind, subject, key, detected_by}` and an `AFFECTS` relation to the subject (the link that
/// makes it linked work; `AFFECTS` is not a consumption, implementation or test edge, so it never hides the orphan). Idempotent: an orphan whose key already has an investigation task (in any
/// status) gets none. Respects emergency controls (FREEZE_WRITES / PAUSE): when a task write is refused, nothing is
/// created and the reason is returned. Nothing is ever deleted.
///
/// This is the orphan producer of the event-driven work generation BC-P2-24 (WS-5, round 3) will own; the engine can
/// adopt these tasks by their `generated_by` and `investigates.key`.
pub fn generate_remediation(p: &Project, detected_by: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let db = if p.db_path().exists() {
        RuntimeDb::open(&p.db_path()).ok()
    } else {
        None
    };
    let report = detect(p, &store, db.as_ref());
    remediate(p, &store, &report.orphans, detected_by)
}

/// Existing investigation tasks by orphan key.
pub fn investigations(store: &RecordStore) -> BTreeMap<String, (String, String)> {
    let mut m = BTreeMap::new();
    for t in store.of_type("task") {
        if !is_generated(t) {
            continue;
        }
        if let Some(k) = t.data["investigates"]["key"].as_str() {
            m.entry(k.to_string())
                .or_insert((t.id(), t.get("task_status")));
        }
    }
    m
}

/// Does the subject of an investigation still exist (a governed record, or a repository file)?
fn subject_exists(p: &Project, store: &RecordStore, subject: &str) -> bool {
    match subject.strip_prefix("file:") {
        Some(f) => p.root.join(f).exists(),
        None => store.get(subject).is_some(),
    }
}

/// **Investigations whose subject is gone** (integration observation O-1). Deleting or retiring an orphan's subject
/// is how many investigations end; the generated task's `AFFECTS` link to it then names nothing. That link is the
/// record of what was investigated, not a defect of the graph: it is never reported as a dangling edge
/// ([`is_resolved_investigation_edge`]), so it can neither degrade health nor refuse a governance close, and the
/// investigation task stays closable or withdrawable like any task. Returned for reporting.
pub fn resolved_investigations(p: &Project, store: &RecordStore) -> Vec<Value> {
    store
        .of_type("task")
        .into_iter()
        .filter(|t| is_generated(t))
        .filter_map(|t| {
            let subject = t.data["investigates"]["subject"].as_str()?.to_string();
            (!subject_exists(p, store, &subject)).then(|| {
                json!({"task": t.id(), "task_status": t.get("task_status"), "subject": subject, "kind": t.data["investigates"]["kind"],
                       "note": "the orphan's subject no longer exists: the investigation is complete; close it with its receipt or withdraw it (task status CANCELLED)"})
            })
        })
        .collect()
}

/// Is `src -type-> dst` the `AFFECTS` link of a generated investigation to its subject, and is that subject gone?
pub fn is_resolved_investigation_edge(
    p: &Project,
    store: &RecordStore,
    src: &str,
    etype: &str,
    dst: &str,
) -> bool {
    if etype != "AFFECTS" {
        return false;
    }
    let Some(t) = store.get(src) else {
        return false;
    };
    is_generated(t)
        && t.data["investigates"]["subject"].as_str() == Some(dst)
        && !subject_exists(p, store, dst)
}

fn remediate(
    p: &Project,
    store: &RecordStore,
    orphans: &[Orphan],
    detected_by: &str,
) -> Result<Value> {
    let existing = investigations(store);
    let todo: Vec<&Orphan> = orphans
        .iter()
        .filter(|o| !existing.contains_key(&o.key()))
        .collect();
    if todo.is_empty() {
        return Ok(
            json!({"created": [], "existing": existing.len(), "orphans": orphans.len(), "generated": 0}),
        );
    }
    if let Err(e) = crate::orchestration::control::guard_write(p, "task create") {
        return Ok(
            json!({"created": [], "not_generated": todo.len(), "reason": format!("[{}] {}", e.code, e.message), "orphans": orphans.len()}),
        );
    }
    let class = "validation";
    let tier = crate::routing::tier_for_class(p, class);
    let mut ids: Vec<String> = store.records.iter().map(|r| r.id()).collect();
    let mut created = vec![];
    for o in todo {
        let id = crate::util::next_id(crate::records::prefix_for("task"), &ids, 4);
        ids.push(id.clone());
        let title = format!("Investigate orphan {}: {}", o.kind, o.subject);
        let rec = crate::records::new_record(
            "task",
            &id,
            &title,
            json!({
                "class": class, "task_status": "READY",
                "objective": format!("{} Determine whether it is intended. Then either link it through governed work ({}) or retire it through a CIT. Never delete it silently (Contract v3:1144).", o.message, o.remediation),
                "generated_by": GENERATOR,
                "investigates": {"kind": o.kind, "subject": o.subject, "subject_type": o.subject_type, "key": o.key(), "path": o.path, "detected_by": detected_by, "detected_at": now_iso()},
                "relations": [{"type": "AFFECTS", "target": o.subject, "note": format!("orphan under investigation ({})", o.kind)}],
                "role": "change-controller",
                "dependencies": [],
                "allowed_paths": ["spec/**"],
                "forbidden_paths": ["governance/kernel/**"],
                "production_merge_allowed": false,
                "minimum_model_tier": tier, "minimum_reasoning": "medium",
                "state_class": "AUTHORITATIVE",
                "provenance": {"producer": format!("gov health ({FAMILY})"), "session": p.session_id, "role": p.role, "created_at": now_iso()},
            }),
        );
        p.schemas()
            .validate("task", &rec.data, &format!("({id})"))?;
        crate::records::save_record(&p.root, &rec)?;
        created.push(json!({"task": id, "kind": o.kind, "subject": o.subject, "key": o.key()}));
    }
    // the new tasks are governed records: keep the derived index fresh for them, as every record writer does, so the
    // run that follows does not report its own remediation as index staleness
    if p.db_path().exists() {
        let _ = crate::memory::indexer::rebuild(
            p,
            crate::memory::indexer::IndexOptions {
                incremental: true,
                ..Default::default()
            },
        );
    }
    let _ = crate::observability::emit(
        p,
        "health.remediation",
        json!({"family": FAMILY, "created": created.len(), "detected_by": detected_by}),
    );
    Ok(
        json!({"created": created, "existing": existing.len(), "orphans": orphans.len(), "generated": created.len()}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::records::parse_record_text;

    fn store(recs: &[(&str, &str)]) -> RecordStore {
        let records: Vec<Record> = recs
            .iter()
            .map(|(y, p)| parse_record_text(y, p).unwrap())
            .collect();
        let mut by_id = BTreeMap::new();
        for (i, r) in records.iter().enumerate() {
            by_id.insert(r.id(), i);
        }
        RecordStore {
            records,
            by_id,
            duplicates: vec![],
            problems: vec![],
        }
    }

    #[test]
    fn each_record_level_w7_class_is_named_and_linked_records_are_not() {
        let s = store(&[
            ("id: REQ-0001\ntype: requirement\nstatus: ACTIVE\nfeature: F-0001\n", "spec/requirements/REQ-0001.yaml"),
            ("id: REQ-0002\ntype: requirement\nstatus: ACTIVE\n", "spec/requirements/REQ-0002.yaml"),
            ("id: REQ-0003\ntype: requirement\nstatus: ACTIVE\nfeature: F-0001\n", "spec/requirements/REQ-0003.yaml"),
            ("id: REQ-0004\ntype: requirement\nstatus: ACTIVE\nscenarios: [SCN-0001]\n", "spec/requirements/REQ-0004.yaml"),
            ("id: F-0001\ntype: feature\nstatus: ACTIVE\nrequirements: [REQ-0001]\n", "spec/features/F-0001.yaml"),
            ("id: SCN-0001\ntype: scenario\nstatus: ACTIVE\n", "spec/scenarios/SCN-0001.yaml"),
            ("id: TST-0001\ntype: test-obligation\nstatus: ACTIVE\nfamily: unit\nscenario: SCN-0001\n", "spec/tasks/TST-0001.yaml"),
            ("id: TST-0009\ntype: test-obligation\nstatus: ACTIVE\nfamily: acceptance\n", "spec/tasks/TST-0009.yaml"),
            ("id: TST-0010\ntype: test-obligation\nstatus: ACTIVE\nfamily: acceptance\nfeature: F-0001\n", "spec/tasks/TST-0010.yaml"),
            ("id: TASK-0001\ntype: task\nstatus: ACTIVE\ntask_status: READY\nrequirements: [REQ-0001]\n", "spec/tasks/TASK-0001.yaml"),
            ("id: API-0001\ntype: interface\nstatus: ACTIVE\nconsumers: [TASK-0001]\n", "spec/interfaces/API-0001.yaml"),
            ("id: API-0002\ntype: interface\nstatus: ACTIVE\nconsumers: [TASK-0077]\n", "spec/interfaces/API-0002.yaml"),
            ("id: API-0003\ntype: interface\nstatus: ACTIVE\nconsumers: [TASK-0002]\n", "spec/interfaces/API-0003.yaml"),
            ("id: TASK-0002\ntype: task\nstatus: ACTIVE\ntask_status: READY\ninterfaces: [API-0003]\n", "spec/tasks/TASK-0002.yaml"),
            ("id: RES-0001\ntype: research\nstatus: ACTIVE\nconclusion: x\ninfluences: [D-0001]\n", "spec/research/RES-0001.yaml"),
            ("id: RES-0002\ntype: research\nstatus: ACTIVE\nconclusion: y\naffects: [F-0001]\n", "spec/research/RES-0002.yaml"),
            ("id: RES-0003\ntype: research\nstatus: ACTIVE\nconclusion: z\ninfluences: [D-0002]\n", "spec/research/RES-0003.yaml"),
            ("id: RES-0004\ntype: research\nstatus: ACTIVE\nquestion: open\n", "spec/research/RES-0004.yaml"),
            ("id: D-0001\ntype: decision\nstatus: ACTIVE\nchosen_option: A\n", "spec/decisions/D-0001.yaml"),
            ("id: D-0002\ntype: decision\nstatus: ACTIVE\nchosen_option: A\nevidence_refs: [RES-0003]\n", "spec/decisions/D-0002.yaml"),
            // generated remediation never counts as a downstream path or a consumer
            ("id: TASK-0009\ntype: task\nstatus: ACTIVE\ntask_status: READY\ngenerated_by: health:lineage_orphans\nrequirements: [REQ-0002]\nrequired_inputs: [{id: API-0002, reason: r}]\n", "spec/tasks/TASK-0009.yaml"),
        ]);
        let g = Graph::build(&s);
        let mut out = vec![];
        unconsumed_outputs(&s, &g, &mut out);
        specs_without_path(&|_f: &str| "source".to_string(), &s, &g, &mut out);
        let _ = unconsumed_research(&s, &g, &mut out);
        let _ = unjustified_tests(&s, &g, &mut out);
        let names: Vec<(&str, String)> = out.iter().map(|o| (o.kind, o.subject.clone())).collect();
        for want in [
            (KIND_UNCONSUMED_OUTPUT, "API-0001"),
            (KIND_UNCONSUMED_OUTPUT, "API-0002"),
            (KIND_UNCONSUMED_RESEARCH, "RES-0001"),
            (KIND_UNCONSUMED_RESEARCH, "RES-0002"),
            (KIND_UNJUSTIFIED_TEST, "TST-0009"),
            (KIND_UNJUSTIFIED_TEST, "TST-0010"),
            (KIND_SPEC_WITHOUT_PATH, "REQ-0002"),
            (KIND_SPEC_WITHOUT_PATH, "REQ-0003"),
        ] {
            assert!(
                names.iter().any(|(k, s)| *k == want.0 && s == want.1),
                "missing {want:?} in {names:?}"
            );
        }
        for not in [
            "API-0003", "RES-0003", "RES-0004", "TST-0001", "REQ-0001", "REQ-0004", "SCN-0001",
        ] {
            assert!(
                !names.iter().any(|(_, s)| s == not),
                "{not} is linked: {names:?}"
            );
        }
        // IF-1: consumption is not implementation. A closing receipt that consumed REQ-0005 (inputs_consumed) and
        // declares it not implemented leaves it an orphan; the one that implemented REQ-0006 does not; a DONE task
        // closed under a receipt is judged by the receipt, not by its own declaration
        let s2 = store(&[
            ("id: F-0002\ntype: feature\nstatus: ACTIVE\nrequirements: [REQ-0005, REQ-0006]\n", "spec/features/F-0002.yaml"),
            ("id: REQ-0005\ntype: requirement\nstatus: ACTIVE\nfeature: F-0002\n", "spec/requirements/REQ-0005.yaml"),
            ("id: REQ-0006\ntype: requirement\nstatus: ACTIVE\nfeature: F-0002\n", "spec/requirements/REQ-0006.yaml"),
            ("id: TASK-0005\ntype: task\nstatus: ACTIVE\ntask_status: DONE\nclass: implementation\nfeature: F-0002\nrequirements: [REQ-0005, REQ-0006]\nclosed_by_report: RPT-0005\n", "spec/tasks/TASK-0005.yaml"),
            ("id: RPT-0005\ntype: report\nstatus: ACTIVE\ntask: TASK-0005\ninputs_consumed: [REQ-0005, REQ-0006]\nrequirements_implemented: [REQ-0006]\ndeviations: ['REQ-0005: not implemented by this task']\n", "spec/reports/RPT-0005.yaml"),
            ("id: TASK-0006\ntype: task\nstatus: ACTIVE\ntask_status: READY\nrequired_inputs: [{id: REQ-0007, reason: context}]\n", "spec/tasks/TASK-0006.yaml"),
            ("id: REQ-0007\ntype: requirement\nstatus: ACTIVE\n", "spec/requirements/REQ-0007.yaml"),
        ]);
        let g2 = Graph::build(&s2);
        let mut out2 = vec![];
        specs_without_path(&|_f: &str| "source".to_string(), &s2, &g2, &mut out2);
        let orphaned: Vec<&str> = out2.iter().map(|o| o.subject.as_str()).collect();
        assert!(orphaned.contains(&"REQ-0005"), "{orphaned:?}");
        assert!(!orphaned.contains(&"REQ-0006"), "{orphaned:?}");
        // an open task that only consumes a requirement does not plan its implementation
        assert!(orphaned.contains(&"REQ-0007"), "{orphaned:?}");
        let r5 = out2.iter().find(|o| o.subject == "REQ-0005").unwrap();
        assert_eq!(
            r5.severity, "medium",
            "a delivery gap of a feature with DONE work"
        );
        assert!(r5.message.contains("RPT-0005"), "{}", r5.message);
        // every orphan has a stable key and a named finding
        let f = out[0].finding(FAMILY);
        assert_eq!(f["orphan"]["key"], json!(out[0].key()));
        assert!(f["message"].as_str().unwrap().contains(&out[0].subject));
        assert_eq!(key_of("a", "b"), key_of("a", "b"));
        assert_ne!(key_of("a", "b"), key_of("a", "c"));
    }
}
