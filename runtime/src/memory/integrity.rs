//! Graph integrity (BC-P2-28; Contract v3 C2:231 "Graph integrity checks detect orphan/stale/reversed/invalid
//! relationships"; :356 "graph edges stale").
//!
//! [`check`] **raises** — as findings with a kind, a severity, the edge and a remediation, not as a count —
//!
//! * `orphan`: a governed traceability record (feature, requirement, scenario, test obligation, interface,
//!   architecture, decision, task) that no relationship reaches or leaves;
//! * `dangling`: an edge whose target does not exist (index edges, code included; record edges without an index);
//! * `stale`: a *current* record whose in-force relationship (depends on, implements, realises, governed by,
//!   constrains, validated by, tests, uses, consumes, blocks, owns, calls, imports) points at a target that is no
//!   longer current — superseded (by status or by a successor), retired, deprecated, rejected, legacy, historical, or
//!   archived / under a path the repository contract classifies `historical`. Provenance relationships
//!   (derived from, learned from, failed because, generated from, produces, affects, supersedes) record history and
//!   are never stale;
//! * `reversed`: a relationship whose endpoint types fit the relation type only the other way round (a requirement
//!   that IMPLEMENTS an architecture record, a requirement that TESTS a test obligation), per [`SIGNATURES`];
//! * `ill_typed`: a relationship whose endpoint types fit the relation type in neither direction (an architecture
//!   record that CALLS a requirement), or a relation type that is not one of the framework's typed relationships;
//! * `supersession_cycle`: records that supersede each other (authority cannot be resolved).
//!
//! Record edges are read canonically through `crate::records::Record::edges` (`graph::canonical_of`, WS-4 IP-12), so
//! a field declared on the target side (`consumers`, `producers`, `task`, `human_gate`, `superseded_by`) is judged
//! in the direction of its meaning. Endpoint types come from the governed records themselves; an endpoint whose type
//! the kernel does not know (a custom record type, a `module:`/`external:` node) is never judged.
//!
//! Runs on every index build (G1-equivalent: `indexer::rebuild` records the result in runtime meta
//! `graph_integrity` and in its report) and on demand (`gov memory integrity`); the full-audit `graph_integrity`
//! family, doctor D015 and CIT-E's `graph_integrity` verification are its other callers (integration points).
use crate::graph::lineage::NON_CURRENT_STATUSES;
use crate::graph::EDGE_TYPES;
use crate::memory::db::RuntimeDb;
use crate::records::{Record, RecordStore};
use crate::{Project, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

/// Where a record type sits in the traceability chain; relation signatures are stated over these kinds.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Kind {
    Project,
    Feature,
    Requirement,
    /// Normative design and constraints: architecture, interface, decision, data, security, performance, workflow.
    Design,
    /// Verification definitions: scenario, test obligation.
    Verify,
    /// Work and its control: task, handoff, CIT, human gate, checkpoint, migration plan.
    Work,
    /// Repository files (code, tests, documents indexed as files).
    Code,
    /// Evidence and history: report, audit, research, experiment, lesson, failure, legacy.
    Evidence,
}

pub fn kind_of(rtype: &str) -> Option<Kind> {
    Some(match rtype {
        "project" => Kind::Project,
        "feature" => Kind::Feature,
        "requirement" => Kind::Requirement,
        "architecture" | "interface" | "decision" | "data" | "security" | "performance"
        | "workflow" => Kind::Design,
        "scenario" | "test-obligation" => Kind::Verify,
        "task" | "handoff" | "cit" | "human-gate" | "checkpoint" | "migration-plan" => Kind::Work,
        "file" => Kind::Code,
        "report" | "audit" | "research" | "experiment" | "lesson" | "failure" | "legacy" => {
            Kind::Evidence
        }
        _ => return None,
    })
}

use Kind::*;
const ALL: &[Kind] = &[
    Project,
    Feature,
    Requirement,
    Design,
    Verify,
    Work,
    Code,
    Evidence,
];
const NORMATIVE: &[Kind] = &[Project, Feature, Requirement, Design];

/// A relation type's endpoint signature: which kinds may be its source and which its destination.
pub struct Signature {
    pub rel: &'static str,
    pub src: &'static [Kind],
    pub dst: &'static [Kind],
    pub meaning: &'static str,
}

/// Endpoint signatures per relation type (framework §11.2 relationship memory; the traceability chain project →
/// feature → requirement → design/constraint → verification → work → code/evidence). Types absent here
/// (`DEPENDS_ON`, `BLOCKS`, `DERIVED_FROM`, `USES`, `CONSUMES`, `AFFECTS`, `GENERATED_FROM`, `OWNS`) relate any kinds.
pub const SIGNATURES: &[Signature] = &[
    Signature {
        rel: "IMPLEMENTS",
        src: &[Design, Work, Code, Evidence],
        dst: &[Project, Feature, Requirement, Design, Verify],
        meaning: "the source realises the target specification (work, code or design implements a requirement, feature, interface or scenario)",
    },
    Signature {
        rel: "REALISES",
        src: &[Feature, Requirement, Design, Verify, Work, Code, Evidence],
        dst: &[Project, Feature, Requirement],
        meaning: "the source realises a more general product intent (a requirement realises its feature, a feature its project)",
    },
    Signature {
        rel: "TESTS",
        src: &[Verify, Work, Code, Evidence],
        dst: &[Project, Feature, Requirement, Design, Verify, Code],
        meaning: "a test obligation, scenario, test task or test file tests the target",
    },
    Signature {
        rel: "VALIDATED_BY",
        src: ALL,
        dst: &[Verify, Work, Code, Evidence],
        meaning: "the source is validated by a test obligation, scenario, test or evidence",
    },
    Signature {
        rel: "GOVERNED_BY",
        src: ALL,
        dst: NORMATIVE,
        meaning: "the source is governed by a normative record (requirement, decision, architecture, interface, feature, project)",
    },
    Signature {
        rel: "CONSTRAINS",
        src: NORMATIVE,
        dst: ALL,
        meaning: "a normative record constrains the target",
    },
    Signature {
        rel: "PRODUCES",
        src: &[Work, Evidence],
        dst: ALL,
        meaning: "work (or an experiment/research activity) produces the target",
    },
    Signature {
        rel: "CALLS",
        src: &[Code],
        dst: &[Code],
        meaning: "code calls code",
    },
    Signature {
        rel: "IMPORTS",
        src: &[Code],
        dst: &[Code],
        meaning: "code imports code",
    },
    Signature {
        rel: "LEARNED_FROM",
        src: ALL,
        dst: &[Evidence, Work, Verify],
        meaning: "the source learned from a lesson, report, failure, experiment or completed work",
    },
    Signature {
        rel: "FAILED_BECAUSE",
        src: &[Work, Evidence, Verify, Code],
        dst: ALL,
        meaning: "a task, run, test or failure record failed because of the target",
    },
];

/// Relation types that assert the target is in force now; a current record's such edge to a non-current target is
/// stale. The others record provenance/history.
pub const IN_FORCE: &[&str] = &[
    "DEPENDS_ON",
    "IMPLEMENTS",
    "REALISES",
    "GOVERNED_BY",
    "CONSTRAINS",
    "VALIDATED_BY",
    "TESTS",
    "USES",
    "CONSUMES",
    "BLOCKS",
    "OWNS",
    "CALLS",
    "IMPORTS",
];

/// Record types an orphan check applies to (the traceability chain; evidence and control records may stand alone).
pub const CONNECTED_TYPES: &[&str] = &[
    "feature",
    "requirement",
    "scenario",
    "test-obligation",
    "interface",
    "architecture",
    "decision",
    "task",
];

fn signature(rel: &str) -> Option<&'static Signature> {
    SIGNATURES.iter().find(|s| s.rel == rel)
}

/// Does `src -rel-> dst` fit the relation's signature?
pub fn fits(rel: &str, src: Kind, dst: Kind) -> bool {
    let Some(s) = signature(rel) else {
        return true;
    };
    if !(s.src.contains(&src) && s.dst.contains(&dst)) {
        // code implementing code (a class implementing an interface in another file) is code-level structure
        return rel == "IMPLEMENTS" && src == Code && dst == Code;
    }
    // within the product-intent chain, realisation points from the more specific to the more general
    if rel == "REALISES" && NORMATIVE[..3].contains(&src) && NORMATIVE[..3].contains(&dst) {
        return src > dst;
    }
    true
}

fn archived(r: &Record) -> bool {
    r.problems.iter().any(|p| p == "archived")
}

fn successor_of(store: &RecordStore) -> BTreeMap<String, String> {
    crate::graph::lineage::successor_map(store)
}

fn is_current(r: &Record, succ: &BTreeMap<String, String>) -> bool {
    !archived(r)
        && !NON_CURRENT_STATUSES.contains(&r.status().as_str())
        && r.get("task_status") != "CANCELLED"
        && !succ.contains_key(&r.id())
}

/// Does `r` still assert its relationships now? Evidence is a record of what was; closed work (a DONE task, a
/// committed or rolled-back CIT, an answered or withdrawn gate, a checkpoint, a handoff) is history too.
fn asserts_now(r: &Record, succ: &BTreeMap<String, String>) -> bool {
    if !is_current(r, succ) || kind_of(&r.rtype()) == Some(Kind::Evidence) {
        return false;
    }
    let closed = matches!(
        r.get("task_status").as_str(),
        "DONE" | "CANCELLED" | "CLOSED"
    ) || matches!(
        r.get("cit_status").as_str(),
        "COMMITTED" | "ROLLED_BACK" | "REJECTED" | "ABANDONED"
    ) || matches!(
        r.get("gate_status").as_str(),
        "ANSWERED" | "REVOKED" | "WITHDRAWN"
    ) || matches!(r.rtype().as_str(), "checkpoint" | "handoff");
    !closed
}

/// Why `r` is not current, if it is not.
fn not_current_reason(
    r: &Record,
    succ: &BTreeMap<String, String>,
    historical_path: bool,
) -> Option<String> {
    if archived(r) || historical_path {
        return Some(format!("historical (archived at {})", r.path));
    }
    let st = r.status();
    if let Some(s) = succ.get(&r.id()) {
        return Some(format!("{st} and superseded by {s}"));
    }
    if NON_CURRENT_STATUSES.contains(&st.as_str()) {
        return Some(st);
    }
    if r.get("task_status") == "CANCELLED" {
        return Some("CANCELLED".into());
    }
    None
}

fn finding(kind: &str, severity: &str, message: String, extra: Value) -> Value {
    let mut f = json!({"kind": kind, "severity": severity, "message": message});
    if let (Some(o), Some(x)) = (f.as_object_mut(), extra.as_object()) {
        for (k, v) in x {
            o.insert(k.clone(), v.clone());
        }
    }
    f
}

/// The integrity report: every finding plus counts by kind.
#[derive(Debug, Clone, serde::Serialize)]
pub struct Integrity {
    pub ok: bool,
    pub checked_records: usize,
    pub checked_edges: usize,
    pub counts: BTreeMap<String, usize>,
    pub findings: Vec<Value>,
}

impl Integrity {
    /// Summary with at most `max` findings (meta / rebuild report).
    pub fn summary(&self, max: usize) -> Value {
        json!({"ok": self.ok, "checked_records": self.checked_records, "checked_edges": self.checked_edges,
               "counts": self.counts, "findings": self.findings.iter().take(max).cloned().collect::<Vec<_>>(),
               "truncated": self.findings.len() > max})
    }
}

/// **The graph integrity check.** `db` (the live index) adds code edges to the dangling check; without it dangling
/// record edges are judged against the record store.
pub fn check(p: &Project, store: &RecordStore, db: Option<&RuntimeDb>) -> Result<Integrity> {
    let succ = successor_of(store);
    let contract = p.contract();
    let historical_path = |path: &str| contract.decide(path).class() == "historical";
    let mut findings: Vec<Value> = vec![];
    let mut checked_edges = 0usize;
    let mut touched: BTreeSet<String> = BTreeSet::new();
    let known = |id: &str| store.get(id).is_some();
    let mut dangling_seen: BTreeSet<(String, String, String)> = BTreeSet::new();
    let known_types: BTreeSet<&str> = EDGE_TYPES.iter().copied().collect();
    let records: Vec<&Record> = store
        .records
        .iter()
        .filter(|r| !archived(r) && !r.id().is_empty())
        .collect();
    for r in &records {
        let me = r.id();
        let edges = r.edges();
        for (s, t, d) in &edges {
            checked_edges += 1;
            touched.insert(s.clone());
            touched.insert(d.clone());
            let edge = json!({"src": s, "type": t, "dst": d});
            // --- relation type
            if !known_types.contains(t.as_str()) {
                findings.push(finding("ill_typed", "medium", format!("{me} declares a relationship of unknown type {t} ({s} -{t}-> {d}); the typed relationships are {}", EDGE_TYPES.join("/")),
                    json!({"record": me, "edge": edge, "path": r.path, "remediation": "use one of the framework's typed relationships (framework §11.2)"})));
                continue;
            }
            // --- endpoint types, per relation type
            let kind = |id: &str| -> Option<Kind> {
                if id.starts_with("file:") {
                    return Some(Kind::Code);
                }
                store.get(id).and_then(|x| kind_of(&x.rtype()))
            };
            if let (Some(ks), Some(kd)) = (kind(s), kind(d)) {
                if !fits(t, ks, kd) {
                    let sig = signature(t).map(|x| x.meaning).unwrap_or("");
                    let rtype = |id: &str| {
                        if id.starts_with("file:") {
                            "file".to_string()
                        } else {
                            store.get(id).map(|x| x.rtype()).unwrap_or_default()
                        }
                    };
                    if fits(t, kd, ks) {
                        findings.push(finding("reversed", "medium", format!("{me}: {s} ({}) -{t}-> {d} ({}) is recorded in the wrong direction: {t} means {sig}; the relationship reads {d} -{t}-> {s}", rtype(s), rtype(d)),
                            json!({"record": me, "edge": edge, "path": r.path, "remediation": format!("declare it on the other end ({d} -{t}-> {s}) or use the inverse relation (e.g. validated_by for tests)")})));
                    } else {
                        findings.push(finding("ill_typed", "medium", format!("{me}: {s} ({}) -{t}-> {d} ({}) relates types that {t} does not relate in either direction: {t} means {sig}", rtype(s), rtype(d)),
                            json!({"record": me, "edge": edge, "path": r.path, "remediation": "use the relation type that states what the relationship means"})));
                    }
                }
            }
            // --- stale: a current source's in-force relationship to a target that is no longer current
            if IN_FORCE.contains(&t.as_str()) {
                let src_current = if s.starts_with("file:") {
                    !historical_path(s.trim_start_matches("file:"))
                } else {
                    store.get(s).map(|x| asserts_now(x, &succ)).unwrap_or(false)
                };
                if src_current {
                    let why = if let Some(path) = d.strip_prefix("file:") {
                        historical_path(path)
                            .then(|| format!("a historical file ({path} is classified historical)"))
                    } else {
                        store
                            .get(d)
                            .and_then(|x| not_current_reason(x, &succ, historical_path(&x.path)))
                    };
                    if let Some(why) = why {
                        findings.push(finding("stale", "medium", format!("{s} -{t}-> {d}: {s} is current but {d} is {why}; the relationship still asserts {d} is in force (declared by {me})"),
                            json!({"record": me, "edge": edge, "path": r.path, "target_state": why, "remediation": format!("point {s} at the current successor of {d}, or retire the relationship")})));
                    }
                }
            }
            // --- dangling record targets (index edges are checked below when an index is available)
            if db.is_none() && !d.starts_with("file:") && !known(d) && !d.contains(':') {
                if dangling_seen.insert((s.clone(), t.clone(), d.clone())) {
                    findings.push(finding("dangling", "medium", format!("{s} -{t}-> {d}: {d} does not exist (declared by {me})"),
                        json!({"record": me, "edge": edge, "path": r.path, "remediation": "fix the reference or add the missing record"})));
                }
            }
        }
    }
    if let Some(db) = db {
        for e in crate::graph::dangling_edges(db)? {
            let (s, t, d) = (
                e["src"].as_str().unwrap_or("").to_string(),
                e["type"].as_str().unwrap_or("").to_string(),
                e["dst"].as_str().unwrap_or("").to_string(),
            );
            if dangling_seen.insert((s.clone(), t.clone(), d.clone())) {
                findings.push(finding("dangling", "medium", format!("dangling edge {s} -{t}-> {d}: {d} is not an artefact of the index (renamed, deleted or never existed)"),
                    json!({"edge": {"src": s, "type": t, "dst": d}, "path": e["source_artifact"], "remediation": "fix the reference (or the import) or add the missing artefact"})));
            }
        }
    }
    // --- supersession cycles (authority cannot be resolved)
    let mut sup: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    for r in &records {
        for (s, t, d) in r.edges() {
            if t == "SUPERSEDES" {
                sup.entry(s).or_default().insert(d);
            }
        }
    }
    let mut reported: BTreeSet<Vec<String>> = BTreeSet::new();
    for start in sup.keys() {
        let mut stack = vec![(start.clone(), vec![start.clone()])];
        while let Some((n, path)) = stack.pop() {
            for next in sup.get(&n).cloned().unwrap_or_default() {
                if next == *start {
                    let mut cyc = path.clone();
                    cyc.sort();
                    if reported.insert(cyc) {
                        findings.push(finding("supersession_cycle", "high", format!("supersession cycle {} -> {start}: each record is superseded by another in the cycle, so no current authority exists", path.join(" -> ")),
                            json!({"records": path, "remediation": "keep one direction of supersession; mark the superseded records SUPERSEDED through a CIT"})));
                    }
                } else if !path.contains(&next) && path.len() < 32 {
                    let mut p2 = path.clone();
                    p2.push(next.clone());
                    stack.push((next, p2));
                }
            }
        }
    }
    // --- orphans: traceability records no relationship reaches or leaves
    for r in &records {
        if !CONNECTED_TYPES.contains(&r.rtype().as_str()) || !is_current(r, &succ) {
            continue;
        }
        if !touched.contains(&r.id()) {
            findings.push(finding("orphan", "low", format!("orphan {} {}: no relationship reaches or leaves it (it traces to no feature, requirement, decision, test or work)", r.rtype(), r.id()),
                json!({"record": r.id(), "path": r.path, "remediation": "relate it to what it realises, implements, tests or governs, or retire it"})));
        }
    }
    let mut counts: BTreeMap<String, usize> = BTreeMap::new();
    for f in &findings {
        *counts
            .entry(f["kind"].as_str().unwrap_or("").to_string())
            .or_default() += 1;
    }
    let ok = findings.iter().all(|f| f["severity"] == "low");
    Ok(Integrity {
        ok,
        checked_records: records.len(),
        checked_edges,
        counts,
        findings,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn signatures_judge_direction_and_type() {
        // the probe's reversed cases and their correct forms
        assert!(
            !fits("IMPLEMENTS", Requirement, Design) && fits("IMPLEMENTS", Design, Requirement)
        );
        assert!(!fits("TESTS", Requirement, Verify) && fits("TESTS", Verify, Requirement));
        assert!(
            !fits("VALIDATED_BY", Verify, Requirement) && fits("VALIDATED_BY", Requirement, Verify)
        );
        assert!(!fits("REALISES", Feature, Requirement) && fits("REALISES", Requirement, Feature));
        // ill-typed both ways
        assert!(!fits("CALLS", Design, Requirement) && !fits("CALLS", Requirement, Design));
        // product-emitted field edges fit
        for (rel, s, d) in [
            ("GOVERNED_BY", Work, Requirement),
            ("GOVERNED_BY", Work, Design),
            ("VALIDATED_BY", Work, Verify),
            ("REALISES", Work, Feature),
            ("REALISES", Requirement, Feature),
            ("PRODUCES", Work, Evidence),
            ("PRODUCES", Work, Code),
            ("IMPLEMENTS", Evidence, Requirement),
            ("IMPLEMENTS", Work, Verify),
            ("IMPLEMENTS", Code, Code),
            ("TESTS", Code, Code),
            ("TESTS", Verify, Verify),
            ("LEARNED_FROM", Work, Evidence),
            ("CALLS", Code, Code),
            ("DEPENDS_ON", Evidence, Project),
        ] {
            assert!(fits(rel, s, d), "{rel} {s:?} -> {d:?}");
        }
    }
}
