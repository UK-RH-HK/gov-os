//! **Mandatory task-input manifest** (Contract v3 W3, lines 1092-1104; W2 lines 1084-1089; BC-P2-17).
//!
//! A governed task declares its upstream inputs, and this module resolves the declaration deterministically — from
//! the governed records only, never from retrieval ranking or the derived index (W3 line 1104, W10 line 1164).
//!
//! ## Declaring inputs
//!
//! | declaration on the task record | slot | required |
//! |---|---|---|
//! | `feature` | feature | yes |
//! | `requirements`, feature's `requirements` | requirement | yes |
//! | `decisions`; ACTIVE/PROVISIONAL decisions whose `affects` names the task or its feature, or whose `governed_by` names the feature | decision | yes |
//! | `scenarios`, feature's `scenarios` | scenario | yes |
//! | `acceptance_tests`, feature's `acceptance_tests` | test design | yes |
//! | `interfaces`, feature's `interfaces` | interface | yes |
//! | `architecture` | architecture | yes |
//! | every ACTIVE/PROVISIONAL architecture record (`graph::IMPLICIT_CONSUMERS`) | architecture | no (implicit) |
//! | `required_data` | dataset | yes |
//! | `derived_from` | evidence (experiments, research, …) | yes |
//! | `dependencies` | task dependency | yes (existence; completion is the DAG's) |
//! | `required_inputs: [{id, reason, type?, required_status?, required_state_class?, version?, content_hash?}]` | by `type`, else by the record's type | yes (unless `required: false`) |
//! | `optional_inputs: [...]` (same entry shape) | as above | no |
//! | `relations: [{type, target, note}]` with an input relation type (`records::INPUT_RELATION_TYPES`) | by the record's type | yes (unless `required: false`); `note` is the reason |
//! | `supplementary_context: [id or {id, reason}]` | — (supplementary block only, never authority) | no |
//!
//! Every entry carries the **reason** for the dependency (declared, or the rule that implied it) and where it was
//! declared.
//!
//! ## Resolution
//!
//! An entry is **satisfied** only when its id resolves to exactly one governed record, of the slot's type, whose
//! lifecycle state is current (`ACTIVE`/`PROVISIONAL`, or what the entry's `required_status` names), which no
//! later record supersedes, whose authority class suits the slot (authority slots require `AUTHORITATIVE` unless
//! `required_state_class` says otherwise; historical/conflicting classes never satisfy an evidence slot), and which
//! meets the entry's `version` / `content_hash` constraint. A superseded or historical record therefore **never
//! silently satisfies a current requirement** (W3 line 1102): it is delivered flagged and the manifest is
//! `BLOCKED`. A missing required input makes the manifest `BLOCKED` with the missing ids named (W4 line 1112).
//!
//! ## Integration points (not wired here; see the WS-4 repair report)
//!
//! * READY derivation (`orchestration::{dag,tasks}`, WS-5): a task is not READY/claimable while
//!   [`require_ready`] refuses (`INPUT_MANIFEST_UNSATISFIED`).
//! * Dispatch (`status::continue_work`, WS-5): `context::ensure_dispatchable(&packet)`.
use crate::graph::lineage::{successor_map, NON_CURRENT_STATUSES};
use crate::records::{state_class_for, Record, RecordStore, INPUT_RELATION_TYPES};
use crate::util::{hash_value, sha256_hex};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::Path;

/// Lifecycle states that satisfy an input by default.
pub const CURRENT_STATUSES: &[&str] = &["ACTIVE", "PROVISIONAL"];
/// Authority classes that can never satisfy an input unless the entry names them explicitly.
pub const NON_CURRENT_CLASSES: &[&str] = &["HISTORICAL", "UNKNOWN_OR_CONFLICTING"];

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Slot {
    Feature,
    Requirement,
    Decision,
    Scenario,
    TestDesign,
    Interface,
    Architecture,
    Dataset,
    Evidence,
    Dependency,
    Other,
}

impl Slot {
    pub const ALL: [Slot; 11] = [
        Slot::Feature,
        Slot::Requirement,
        Slot::Decision,
        Slot::Scenario,
        Slot::TestDesign,
        Slot::Interface,
        Slot::Architecture,
        Slot::Dataset,
        Slot::Evidence,
        Slot::Dependency,
        Slot::Other,
    ];
    pub fn name(self) -> &'static str {
        match self {
            Slot::Feature => "feature",
            Slot::Requirement => "requirement",
            Slot::Decision => "decision",
            Slot::Scenario => "scenario",
            Slot::TestDesign => "test_design",
            Slot::Interface => "interface",
            Slot::Architecture => "architecture",
            Slot::Dataset => "dataset",
            Slot::Evidence => "evidence",
            Slot::Dependency => "task_dependency",
            Slot::Other => "other",
        }
    }
    /// Record types that satisfy the slot (empty = any type).
    pub fn expected_types(self) -> &'static [&'static str] {
        match self {
            Slot::Feature => &["feature"],
            Slot::Requirement => &["requirement"],
            Slot::Decision => &["decision"],
            Slot::Scenario => &["scenario"],
            Slot::TestDesign => &["test-obligation"],
            Slot::Interface => &["interface"],
            Slot::Architecture => &["architecture"],
            Slot::Dataset => &["data"],
            Slot::Dependency => &["task"],
            Slot::Evidence | Slot::Other => &[],
        }
    }
    /// Is the slot delivered as governing authority (and therefore held to the AUTHORITATIVE class)?
    pub fn authoritative(self) -> bool {
        matches!(
            self,
            Slot::Feature
                | Slot::Requirement
                | Slot::Decision
                | Slot::Scenario
                | Slot::TestDesign
                | Slot::Interface
                | Slot::Architecture
        )
    }
    fn from_field(f: &str) -> Option<Slot> {
        Some(match f {
            "feature" => Slot::Feature,
            "requirements" => Slot::Requirement,
            "decisions" => Slot::Decision,
            "scenarios" => Slot::Scenario,
            "acceptance_tests" => Slot::TestDesign,
            "interfaces" => Slot::Interface,
            "architecture" => Slot::Architecture,
            "required_data" => Slot::Dataset,
            "derived_from" => Slot::Evidence,
            "dependencies" => Slot::Dependency,
            _ => return None,
        })
    }
    /// The slot a record of type `t` fills when it is declared without a slot.
    pub fn for_type(t: &str) -> Slot {
        match t {
            "feature" => Slot::Feature,
            "requirement" => Slot::Requirement,
            "decision" => Slot::Decision,
            "scenario" => Slot::Scenario,
            "test-obligation" => Slot::TestDesign,
            "interface" => Slot::Interface,
            "architecture" => Slot::Architecture,
            "data" => Slot::Dataset,
            "experiment" | "research" => Slot::Evidence,
            "task" => Slot::Dependency,
            _ => Slot::Other,
        }
    }
    /// A declared `type`/`kind`/`slot` value on a manifest entry: a slot name, a list field name or a record type.
    fn parse(s: &str) -> Option<Slot> {
        let s = s.trim();
        if s.is_empty() {
            return None;
        }
        Slot::ALL
            .iter()
            .copied()
            .find(|x| x.name() == s)
            .or_else(|| Slot::from_field(s))
            .or_else(|| {
                Slot::ALL
                    .iter()
                    .copied()
                    .find(|x| x.expected_types().contains(&s))
            })
            .or_else(|| match s {
                "experiment" | "research" => Some(Slot::Evidence),
                _ => None,
            })
    }
}

/// Constraints a manifest entry declares on its input.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Constraints {
    pub statuses: Vec<String>,
    pub state_classes: Vec<String>,
    pub version: Option<String>,
    pub content_hash: Option<String>,
}

impl Constraints {
    fn is_empty(&self) -> bool {
        *self == Constraints::default()
    }
    fn to_value(&self) -> Value {
        let mut v = json!({});
        if !self.statuses.is_empty() {
            v["required_status"] = json!(self.statuses);
        }
        if !self.state_classes.is_empty() {
            v["required_state_class"] = json!(self.state_classes);
        }
        if let Some(x) = &self.version {
            v["version"] = json!(x);
        }
        if let Some(x) = &self.content_hash {
            v["content_hash"] = json!(x);
        }
        v
    }
}

fn str_or_list(v: Option<&Value>) -> Vec<String> {
    match v {
        Some(Value::String(s)) if !s.trim().is_empty() => vec![s.trim().to_string()],
        Some(Value::Array(a)) => a
            .iter()
            .filter_map(|x| x.as_str().map(|s| s.trim().to_string()))
            .filter(|s| !s.is_empty())
            .collect(),
        _ => vec![],
    }
}

fn first_str(o: &serde_json::Map<String, Value>, keys: &[&str]) -> Option<String> {
    keys.iter().find_map(|k| {
        o.get(*k)
            .and_then(|v| v.as_str())
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
    })
}

fn parse_constraints(o: &serde_json::Map<String, Value>) -> Constraints {
    let mut statuses = vec![];
    for k in ["required_status", "required_state", "required_lifecycle"] {
        statuses.extend(str_or_list(o.get(k)));
    }
    let mut classes = vec![];
    for k in ["required_state_class", "required_authority"] {
        classes.extend(str_or_list(o.get(k)));
    }
    Constraints {
        statuses: statuses.into_iter().map(|s| s.to_uppercase()).collect(),
        state_classes: classes.into_iter().map(|s| s.to_uppercase()).collect(),
        version: first_str(o, &["version", "version_constraint", "required_version"]),
        content_hash: first_str(o, &["content_hash", "required_hash", "hash", "sha256"]),
    }
}

/// One problem found while resolving an entry.
#[derive(Clone, Debug)]
pub struct Problem {
    pub code: &'static str,
    pub message: String,
    pub blocking: bool,
}

/// One declared input of a task, merged over every place it was declared, and its resolution.
#[derive(Clone, Debug)]
pub struct Entry {
    pub id: String,
    pub slot: Slot,
    pub required: bool,
    pub reasons: Vec<String>,
    pub sources: Vec<String>,
    pub constraints: Constraints,
    /// `RESOLVED`, `ABSENT` (no record with the id) or `TYPE_MISMATCH` (a record, of another type).
    pub resolution: &'static str,
    pub record_type: String,
    pub path: String,
    pub status: String,
    pub state_class: String,
    pub version: Option<String>,
    pub content_hash: Option<String>,
    pub superseded_by: Option<String>,
    pub duplicate_paths: Vec<String>,
    pub authority_flag: Option<String>,
    pub problems: Vec<Problem>,
}

impl Entry {
    fn new(id: &str, slot: Slot) -> Self {
        Entry {
            id: id.to_string(),
            slot,
            required: false,
            reasons: vec![],
            sources: vec![],
            constraints: Constraints::default(),
            resolution: "ABSENT",
            record_type: String::new(),
            path: String::new(),
            status: String::new(),
            state_class: String::new(),
            version: None,
            content_hash: None,
            superseded_by: None,
            duplicate_paths: vec![],
            authority_flag: None,
            problems: vec![],
        }
    }
    /// Delivered into the packet's slot (the record exists and is of the slot's type), flagged or not.
    pub fn delivered(&self) -> bool {
        self.resolution == "RESOLVED"
    }
    /// Satisfies the manifest: delivered with no blocking problem.
    pub fn satisfied(&self) -> bool {
        self.delivered() && !self.problems.iter().any(|p| p.blocking)
    }
    pub fn reason(&self) -> Value {
        if self.reasons.is_empty() {
            Value::Null
        } else {
            json!(self.reasons.join("; "))
        }
    }
    pub fn problems_value(&self) -> Value {
        json!(self
            .problems
            .iter()
            .map(|p| json!({"code": p.code, "message": p.message, "blocking": p.blocking}))
            .collect::<Vec<_>>())
    }
    pub fn to_value(&self) -> Value {
        let mut v = json!({
            "id": self.id, "slot": self.slot.name(), "required": self.required, "reason": self.reason(),
            "declared_in": self.sources, "resolution": self.resolution, "delivered": self.delivered(),
            "satisfied": self.satisfied(), "type": self.record_type, "path": self.path, "status": self.status,
            "state_class": self.state_class, "version": self.version, "content_hash": self.content_hash,
            "superseded_by": self.superseded_by, "authority_flag": self.authority_flag,
            "problems": self.problems_value(),
        });
        if !self.constraints.is_empty() {
            v["constraints"] = self.constraints.to_value();
        }
        if !self.duplicate_paths.is_empty() {
            v["duplicate_paths"] = json!(self.duplicate_paths);
        }
        v
    }
    fn problem_summary(&self) -> Value {
        json!({"id": self.id, "slot": self.slot.name(), "required": self.required, "declared_in": self.sources,
               "reason": self.reason(), "resolution": self.resolution, "type": self.record_type,
               "problems": self.problems_value()})
    }
}

/// The resolved manifest of one task.
#[derive(Clone, Debug)]
pub struct Manifest {
    pub task: String,
    pub entries: Vec<Entry>,
    /// Declared supplementary context: `{id, reason, resolution, type, status, path}` — never authority.
    pub supplementary: Vec<Value>,
}

impl Manifest {
    pub fn satisfied(&self) -> bool {
        self.entries.iter().all(|e| !e.required || e.satisfied())
    }
    /// `COMPLETE` when every required input is satisfied, else `BLOCKED`.
    pub fn delivery_state(&self) -> &'static str {
        if self.satisfied() {
            "COMPLETE"
        } else {
            "BLOCKED"
        }
    }
    pub fn in_slot(&self, slot: Slot) -> Vec<&Entry> {
        self.entries.iter().filter(|e| e.slot == slot).collect()
    }
    /// Required inputs that could not be supplied at all: absent, or of the wrong type for the slot declared.
    pub fn missing(&self) -> Vec<Value> {
        self.entries
            .iter()
            .filter(|e| e.required && !e.delivered())
            .map(|e| e.problem_summary())
            .collect()
    }
    /// Required inputs that were supplied but do not satisfy the manifest (superseded, not current, not
    /// authoritative, ambiguous, or violating a declared version/hash/state constraint).
    pub fn violations(&self) -> Vec<Value> {
        self.entries
            .iter()
            .filter(|e| e.required && e.delivered() && !e.satisfied())
            .map(|e| e.problem_summary())
            .collect()
    }
    /// Problems on optional or implicit inputs (reported, never blocking).
    pub fn advisories(&self) -> Vec<Value> {
        self.entries
            .iter()
            .filter(|e| !e.problems.is_empty() && (!e.required || e.satisfied()))
            .map(|e| e.problem_summary())
            .collect()
    }
    /// Required inputs that are satisfied: exactly what a consumption receipt must acknowledge.
    pub fn required_satisfied(&self) -> Vec<&Entry> {
        self.entries
            .iter()
            .filter(|e| e.required && e.satisfied() && e.slot != Slot::Dependency)
            .collect()
    }
    pub fn to_value(&self) -> Value {
        json!({
            "task": self.task,
            "delivery_state": self.delivery_state(),
            "inputs": self.entries.iter().map(|e| e.to_value()).collect::<Vec<_>>(),
            "missing_inputs": self.missing(),
            "input_violations": self.violations(),
            "advisories": self.advisories(),
            "supplementary_context": self.supplementary,
            "counts": {"declared": self.entries.len(), "required": self.entries.iter().filter(|e| e.required).count(),
                       "satisfied": self.entries.iter().filter(|e| e.required && e.satisfied()).count()},
        })
    }
    /// Deterministic hash of the resolution (what was required, what each id resolved to, at which hash).
    pub fn hash(&self) -> String {
        hash_value(&self.to_value())
    }
    /// One line naming what blocks the manifest, for DAG/readiness reporting, or `None` when satisfied.
    pub fn blocking_reason(&self) -> Option<String> {
        if self.satisfied() {
            return None;
        }
        let items: Vec<String> = self
            .entries
            .iter()
            .filter(|e| e.required && !e.satisfied())
            .map(|e| {
                let codes: Vec<&str> = if e.delivered() {
                    e.problems
                        .iter()
                        .filter(|p| p.blocking)
                        .map(|p| p.code)
                        .collect()
                } else {
                    vec![e.resolution]
                };
                format!("{} ({}: {})", e.id, e.slot.name(), codes.join(","))
            })
            .collect();
        Some(format!(
            "mandatory inputs unsatisfied: {}",
            items.join("; ")
        ))
    }
}

#[derive(Default)]
struct Builder {
    entries: BTreeMap<(Slot, String), Entry>,
}

impl Builder {
    fn add(
        &mut self,
        id: &str,
        slot: Slot,
        required: bool,
        reason: Option<String>,
        source: String,
        c: Constraints,
    ) {
        let e = self
            .entries
            .entry((slot, id.to_string()))
            .or_insert_with(|| Entry::new(id, slot));
        e.required |= required;
        if let Some(r) = reason.filter(|r| !r.trim().is_empty()) {
            if !e.reasons.contains(&r) {
                e.reasons.push(r);
            }
        }
        if !e.sources.contains(&source) {
            e.sources.push(source);
        }
        merge_constraints(e, c);
    }
}

fn merge_constraints(e: &mut Entry, c: Constraints) {
    let cur = &mut e.constraints;
    let mut conflict = vec![];
    if !c.statuses.is_empty() {
        if cur.statuses.is_empty() {
            cur.statuses = c.statuses;
        } else {
            let inter: Vec<String> = cur
                .statuses
                .iter()
                .filter(|s| c.statuses.contains(s))
                .cloned()
                .collect();
            if inter.is_empty() {
                conflict.push(format!(
                    "required_status {:?} vs {:?}",
                    cur.statuses, c.statuses
                ));
            } else {
                cur.statuses = inter;
            }
        }
    }
    if !c.state_classes.is_empty() {
        if cur.state_classes.is_empty() {
            cur.state_classes = c.state_classes;
        } else {
            let inter: Vec<String> = cur
                .state_classes
                .iter()
                .filter(|s| c.state_classes.contains(s))
                .cloned()
                .collect();
            if inter.is_empty() {
                conflict.push(format!(
                    "required_state_class {:?} vs {:?}",
                    cur.state_classes, c.state_classes
                ));
            } else {
                cur.state_classes = inter;
            }
        }
    }
    for (mine, theirs, what) in [
        (&mut cur.version, c.version, "version"),
        (&mut cur.content_hash, c.content_hash, "content_hash"),
    ] {
        if let Some(t) = theirs {
            match mine {
                Some(m) if *m != t => conflict.push(format!("{what} {m} vs {t}")),
                _ => *mine = Some(t),
            }
        }
    }
    for c in conflict {
        e.problems.push(Problem {
            code: "CONFLICTING_CONSTRAINTS",
            message: format!(
                "{} is declared more than once with incompatible constraints ({c}); declare one constraint",
                e.id
            ),
            blocking: true,
        });
    }
}

fn entry_ids(v: Option<&Value>) -> Vec<(String, Option<serde_json::Map<String, Value>>)> {
    let mut out = vec![];
    let push = |x: &Value, out: &mut Vec<(String, Option<serde_json::Map<String, Value>>)>| match x
    {
        Value::String(s) => {
            let s = s.split('@').next().unwrap_or("").trim().to_string();
            if !s.is_empty() {
                out.push((s, None));
            }
        }
        Value::Object(o) => {
            if let Some(id) = first_str(o, &["id", "target"]) {
                out.push((id, Some(o.clone())));
            }
        }
        _ => {}
    };
    match v {
        Some(Value::Array(a)) => {
            for x in a {
                push(x, &mut out);
            }
        }
        Some(x @ Value::String(_)) => push(x, &mut out),
        Some(x @ Value::Object(_)) => push(x, &mut out),
        _ => {}
    }
    out
}

/// Parse a version string into numeric components (`v2.3.1-rc1` -> [2, 3, 1]).
fn parse_ver(s: &str) -> Option<Vec<u64>> {
    let s = s.trim().trim_start_matches(['v', 'V', '=']);
    let core = s.split(['-', '+']).next().unwrap_or("");
    let parts: Option<Vec<u64>> = core.split('.').map(|p| p.parse::<u64>().ok()).collect();
    let mut v = parts.filter(|v| !v.is_empty())?;
    while v.len() < 3 {
        v.push(0);
    }
    Some(v)
}

/// Does `actual` satisfy `constraint`? Exact string, `*`, or space/comma-separated comparators over dotted numeric
/// versions (`=X`, `>=X`, `>X`, `<=X`, `<X`, `^X` compatible, `~X` same minor).
pub fn version_satisfies(actual: &str, constraint: &str) -> bool {
    let c = constraint.trim();
    if c == "*" || c == actual.trim() {
        return true;
    }
    let Some(a) = parse_ver(actual) else {
        return false;
    };
    c.split([' ', ',']).filter(|t| !t.is_empty()).all(|tok| {
        let (op, rest) = ["^", "~", ">=", "<=", ">", "<", "="]
            .iter()
            .find(|op| tok.starts_with(**op))
            .map(|op| (*op, &tok[op.len()..]))
            .unwrap_or(("=", tok));
        let Some(b) = parse_ver(rest) else {
            return false;
        };
        match op {
            ">=" => a >= b,
            "<=" => a <= b,
            ">" => a > b,
            "<" => a < b,
            "^" => {
                let upper = if b[0] > 0 {
                    vec![b[0] + 1, 0, 0]
                } else {
                    vec![0, b[1] + 1, 0]
                };
                a >= b && a < upper
            }
            "~" => a >= b && a < vec![b[0], b[1] + 1, 0],
            _ => a == b,
        }
    })
}

/// Normalise a declared content hash (`sha256:` prefix allowed; at least 12 hex characters, prefix match).
fn hash_matches(actual: &str, declared: &str) -> std::result::Result<bool, String> {
    let d = declared
        .trim()
        .trim_start_matches("sha256:")
        .to_ascii_lowercase();
    if d.len() < 12 || d.len() > 64 || !d.chars().all(|c| c.is_ascii_hexdigit()) {
        return Err(format!(
            "content_hash '{declared}' is not a SHA-256 (or a prefix of at least 12 hex characters)"
        ));
    }
    Ok(actual.starts_with(&d))
}

fn resolve_entry(
    e: &mut Entry,
    store: &RecordStore,
    root: &Path,
    authority: &Value,
    succ: &BTreeMap<String, String>,
) {
    let Some(r) = store.get(&e.id) else {
        e.resolution = "ABSENT";
        e.problems.push(Problem {
            code: "ABSENT",
            message: format!(
                "{} is declared as a {} input but no governed record with that id exists; create it, correct the id, or remove the declaration",
                e.id,
                e.slot.name()
            ),
            blocking: e.required,
        });
        return;
    };
    e.record_type = r.rtype();
    e.path = r.path.clone();
    let archived = r.problems.iter().any(|p| p == "archived");
    e.status = if archived {
        "HISTORICAL".into()
    } else {
        r.status()
    };
    e.state_class = state_class_for(r, authority);
    e.version = r
        .data
        .get("version")
        .map(|v| v.as_str().map(|s| s.to_string()).unwrap_or(v.to_string()));
    e.content_hash = crate::util::read_bytes(&root.join(&r.path))
        .ok()
        .map(|b| sha256_hex(&b));
    e.superseded_by = succ.get(&e.id).cloned();
    let expected = e.slot.expected_types();
    if !expected.is_empty() && !expected.contains(&e.record_type.as_str()) {
        e.resolution = "TYPE_MISMATCH";
        e.problems.push(Problem {
            code: "TYPE_MISMATCH",
            message: format!(
                "{} is declared as a {} input but is a {} record ({}); a {} can never satisfy it — declare it in the matching field or correct the id",
                e.id, e.slot.name(), e.record_type, e.path, e.record_type
            ),
            blocking: e.required,
        });
        return;
    }
    e.resolution = "RESOLVED";
    let req = e.required;
    let mut flag: Option<String> = None;
    let mut probs: Vec<Problem> = vec![];
    if crate::graph::identity::in_canonical_location(None, &e.record_type, &e.path) == Some(false) {
        probs.push(Problem {
            code: "NON_CANONICAL_LOCATION",
            message: format!(
                "{} ({}) is stored at {} outside its type's canonical location; it is delivered by id, but move it (identity is kept) so every surface finds it",
                e.id, e.record_type, e.path
            ),
            blocking: false,
        });
    }
    if let Some((_, paths)) = store.duplicates.iter().find(|(d, _)| *d == e.id) {
        e.duplicate_paths = paths.clone();
        flag.get_or_insert("AMBIGUOUS_DUPLICATE_ID".into());
        probs.push(Problem { code: "AMBIGUOUS_ID", message: format!("{} resolves to {} records ({}); the input is ambiguous until the duplicate is removed or re-identified", e.id, paths.len(), paths.join(", ")), blocking: req });
    }
    let allowed_status: Vec<String> = if e.constraints.statuses.is_empty() {
        CURRENT_STATUSES.iter().map(|s| s.to_string()).collect()
    } else {
        e.constraints.statuses.clone()
    };
    if e.slot != Slot::Dependency {
        if let Some(by) = &e.superseded_by {
            if CURRENT_STATUSES.contains(&e.status.as_str()) {
                flag.get_or_insert("UNKNOWN_OR_CONFLICTING".into());
            } else {
                flag.get_or_insert(e.status.clone());
            }
            if !allowed_status.iter().any(|s| s == "SUPERSEDED") {
                probs.push(Problem { code: "SUPERSEDED", message: format!("{} is superseded by {by}; a superseded input cannot satisfy a current requirement — depend on {by} (or resolve the supersession via CIT)", e.id), blocking: req });
            }
        }
        if !allowed_status.contains(&e.status) {
            if NON_CURRENT_STATUSES.contains(&e.status.as_str()) {
                flag.get_or_insert(e.status.clone());
            }
            probs.push(Problem { code: "LIFECYCLE_STATE", message: format!("{} is {} but the input requires {}; historical or non-current material cannot replace a current authoritative input", e.id, e.status, allowed_status.join("|")), blocking: req });
        } else if NON_CURRENT_STATUSES.contains(&e.status.as_str()) {
            // explicitly permitted non-current material: delivered, never as current authority
            flag.get_or_insert(e.status.clone());
        }
        if e.status == "PROVISIONAL" {
            probs.push(Problem {
                code: "PROVISIONAL",
                message: format!(
                    "{} is PROVISIONAL: usable, but may change before it is ratified",
                    e.id
                ),
                blocking: false,
            });
        }
        let class_ok = if !e.constraints.state_classes.is_empty() {
            e.constraints.state_classes.contains(&e.state_class)
        } else if e.slot.authoritative() {
            e.state_class == "AUTHORITATIVE"
        } else {
            !NON_CURRENT_CLASSES.contains(&e.state_class.as_str())
        };
        if !class_ok {
            flag.get_or_insert("NOT_AUTHORITATIVE".into());
            let want = if !e.constraints.state_classes.is_empty() {
                e.constraints.state_classes.join("|")
            } else if e.slot.authoritative() {
                "AUTHORITATIVE".into()
            } else {
                "a current class".into()
            };
            probs.push(Problem { code: "AUTHORITY_CLASS", message: format!("{} has authority class {} but the {} input requires {want}; authority semantics are preserved across stages, so it is delivered flagged and does not satisfy the input", e.id, e.state_class, e.slot.name()), blocking: req });
        }
        if let Some(c) = &e.constraints.version {
            match &e.version {
                Some(v) if version_satisfies(v, c) => {}
                Some(v) => {
                    flag.get_or_insert("CONSTRAINT_VIOLATION".into());
                    probs.push(Problem {
                        code: "VERSION_MISMATCH",
                        message: format!("{} is at version {v}; the input requires {c}", e.id),
                        blocking: req,
                    });
                }
                None => {
                    flag.get_or_insert("CONSTRAINT_VIOLATION".into());
                    probs.push(Problem { code: "VERSION_UNAVAILABLE", message: format!("{} declares no version, so the version constraint {c} cannot be met; pin its content_hash instead", e.id), blocking: req });
                }
            }
        }
        if let Some(h) = &e.constraints.content_hash {
            let actual = e.content_hash.clone().unwrap_or_default();
            match hash_matches(&actual, h) {
                Ok(true) => {}
                Ok(false) => {
                    flag.get_or_insert("CONSTRAINT_VIOLATION".into());
                    probs.push(Problem { code: "HASH_MISMATCH", message: format!("{} content hash is {actual}; the input is pinned to {h} — the pinned version is no longer the governed content", e.id), blocking: req });
                }
                Err(m) => probs.push(Problem {
                    code: "HASH_CONSTRAINT_INVALID",
                    message: m,
                    blocking: req,
                }),
            }
        }
    }
    e.authority_flag = flag;
    e.problems.extend(probs);
}

/// Resolve the manifest of `task` against `store`. `root` locates record bytes (content hashes); `authority` is
/// the effective AUTHORITY_POLICY (default state classes).
pub fn resolve_with(
    root: &Path,
    authority: &Value,
    store: &RecordStore,
    task: &Record,
) -> Manifest {
    let mut b = Builder::default();
    let tid = task.id();
    let feature_id = task.get("feature");
    let feature = store
        .get(&feature_id)
        .filter(|r| r.rtype() == "feature" && !feature_id.is_empty());
    let none = Constraints::default;
    if !feature_id.is_empty() {
        b.add(
            &feature_id,
            Slot::Feature,
            true,
            Some("the task realises this feature".into()),
            "task.feature".into(),
            none(),
        );
    }
    // typed list fields on the task, then the feature's inherited inputs
    for field in [
        "requirements",
        "decisions",
        "scenarios",
        "acceptance_tests",
        "interfaces",
        "architecture",
        "required_data",
        "derived_from",
        "dependencies",
    ] {
        let slot = Slot::from_field(field).unwrap();
        for (id, obj) in entry_ids(task.data.get(field)) {
            let (reason, c, req) = match &obj {
                Some(o) => (
                    first_str(o, &["reason", "note", "why"]),
                    parse_constraints(o),
                    o.get("required").and_then(|v| v.as_bool()).unwrap_or(true),
                ),
                None => (None, none(), true),
            };
            b.add(&id, slot, req, reason, format!("task.{field}"), c);
        }
        if let Some(f) = feature {
            if matches!(
                field,
                "requirements" | "scenarios" | "acceptance_tests" | "interfaces"
            ) {
                for (id, _) in entry_ids(f.data.get(field)) {
                    b.add(
                        &id,
                        slot,
                        true,
                        Some(format!("inherited from feature {feature_id}")),
                        format!("feature {feature_id}.{field}"),
                        none(),
                    );
                }
            }
        }
    }
    // decisions that apply by relation (framework §2/§21: they bind the task whether or not it lists them)
    for d in store.active("decision") {
        let via = if d.list("affects").contains(&tid) {
            Some(format!("{}.affects {tid}", d.id()))
        } else if !feature_id.is_empty() && d.list("affects").contains(&feature_id) {
            Some(format!("{}.affects {feature_id}", d.id()))
        } else if !feature_id.is_empty() && d.list("governed_by").contains(&feature_id) {
            Some(format!("{}.governed_by {feature_id}", d.id()))
        } else {
            None
        };
        if let Some(v) = via {
            b.add(
                &d.id(),
                Slot::Decision,
                true,
                Some("decision applies to this task or its feature".into()),
                format!("applies: {v}"),
                none(),
            );
        }
    }
    // implicit inputs every packet carries (graph::IMPLICIT_CONSUMERS)
    for (input_type, consumer_type, why) in crate::graph::IMPLICIT_CONSUMERS {
        if *consumer_type != "task" {
            continue;
        }
        for r in store.of_type(input_type) {
            if crate::graph::IMPLICIT_INPUT_STATUSES.contains(&r.status().as_str()) {
                b.add(
                    &r.id(),
                    Slot::for_type(input_type),
                    false,
                    Some(format!("implicit input: {why}")),
                    "implicit".into(),
                    none(),
                );
            }
        }
    }
    // explicit manifest entries
    for (field, default_required) in [("required_inputs", true), ("optional_inputs", false)] {
        for (id, obj) in entry_ids(task.data.get(field)) {
            let o = obj.unwrap_or_default();
            let declared_slot =
                first_str(&o, &["slot", "type", "kind"]).and_then(|s| Slot::parse(&s));
            let slot = declared_slot.unwrap_or_else(|| {
                store
                    .get(&id)
                    .map(|r| Slot::for_type(&r.rtype()))
                    .unwrap_or(Slot::Other)
            });
            let req = o
                .get("required")
                .and_then(|v| v.as_bool())
                .unwrap_or(default_required);
            b.add(
                &id,
                slot,
                req,
                first_str(&o, &["reason", "note", "why"]),
                format!("task.{field}"),
                parse_constraints(&o),
            );
        }
    }
    // inputs declared through the generic relations[] list
    if let Some(rels) = task.data.get("relations").and_then(|v| v.as_array()) {
        for r in rels {
            let (Some(t), Some(target)) = (
                r.get("type").and_then(|v| v.as_str()),
                r.get("target").and_then(|v| v.as_str()),
            ) else {
                continue;
            };
            if !INPUT_RELATION_TYPES.contains(&t) {
                continue;
            }
            let o = r.as_object().cloned().unwrap_or_default();
            let slot = store
                .get(target)
                .map(|x| Slot::for_type(&x.rtype()))
                .unwrap_or(Slot::Other);
            let req = o.get("required").and_then(|v| v.as_bool()).unwrap_or(true);
            b.add(
                target,
                slot,
                req,
                first_str(&o, &["note", "reason", "why"]),
                format!("task.relations[{t}]"),
                parse_constraints(&o),
            );
        }
    }
    let succ = successor_map(store);
    let mut entries: Vec<Entry> = b.entries.into_values().collect();
    for e in entries.iter_mut() {
        resolve_entry(e, store, root, authority, &succ);
    }
    // supplementary context: declared separately, never authority, never blocking
    let mut supplementary = vec![];
    for (id, obj) in entry_ids(task.data.get("supplementary_context")) {
        let reason = obj
            .as_ref()
            .and_then(|o| first_str(o, &["reason", "note", "why"]));
        let v = match store.get(&id) {
            Some(r) => {
                json!({"id": id, "reason": reason, "resolution": "RESOLVED", "type": r.rtype(), "status": r.status(), "state_class": state_class_for(r, authority), "path": r.path, "title": r.title(), "superseded_by": succ.get(&id)})
            }
            None => {
                json!({"id": id, "reason": reason, "resolution": "ABSENT", "note": "declared supplementary context does not exist; supplementary context never blocks"})
            }
        };
        supplementary.push(v);
    }
    Manifest {
        task: tid,
        entries,
        supplementary,
    }
}

/// Resolve the manifest of `task` in project `p`.
pub fn resolve(p: &Project, store: &RecordStore, task: &Record) -> Manifest {
    let authority = p
        .policies()
        .effective
        .get("AUTHORITY_POLICY")
        .cloned()
        .unwrap_or(json!({}));
    resolve_with(&p.root, &authority, store, task)
}

/// Resolve the manifest of task `task_id` (typed refusal when it is not a task).
pub fn resolve_task(p: &Project, store: &RecordStore, task_id: &str) -> Result<Manifest> {
    let t = store
        .get(task_id)
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("task {task_id} not found")))?;
    if t.rtype() != "task" {
        return Err(GovError::new("USAGE", format!("{task_id} is not a task")));
    }
    Ok(resolve(p, store, t))
}

/// **The READY check** (W3 lines 1101-1102): refuse with `INPUT_MANIFEST_UNSATISFIED` while any mandatory input of
/// `task_id` is absent, of the wrong type, superseded, not current, not authoritative, ambiguous or outside its
/// declared version/hash/state constraint. Integration point for every route that sets or relies on READY
/// (`task create --status READY`, `task status READY`, `task replan`, `task claim`, `continue`; WS-5).
pub fn require_ready(p: &Project, store: &RecordStore, task_id: &str) -> Result<Manifest> {
    let m = resolve_task(p, store, task_id)?;
    if m.satisfied() {
        return Ok(m);
    }
    Err(GovError::new(
        "INPUT_MANIFEST_UNSATISFIED",
        format!(
            "{task_id} cannot be READY: {}. Remediation: create or correct the missing inputs, depend on the current (superseding) versions, or amend the task's manifest; `gov context manifest {task_id}` shows the full resolution",
            m.blocking_reason().unwrap_or_default()
        ),
    )
    .with_details(json!({"task": task_id, "delivery_state": m.delivery_state(), "missing_inputs": m.missing(), "input_violations": m.violations(), "manifest_hash": m.hash()})))
}

#[cfg(test)]
mod tests {
    use super::*;

    struct Fx {
        root: std::path::PathBuf,
    }
    impl Fx {
        fn new() -> Self {
            let root = std::env::temp_dir().join(format!(
                "gov-manifest-{}-{}",
                std::process::id(),
                crate::util::short_uuid()
            ));
            std::fs::create_dir_all(&root).unwrap();
            Fx { root }
        }
        fn put(&self, rel: &str, text: &str) {
            let p = self.root.join(rel);
            std::fs::create_dir_all(p.parent().unwrap()).unwrap();
            std::fs::write(p, text).unwrap();
        }
        fn manifest(&self, task: &str) -> Manifest {
            let store = RecordStore::load(&self.root);
            let auth = json!({"default_state_class_by_type": {"requirement": "AUTHORITATIVE", "decision": "AUTHORITATIVE", "scenario": "AUTHORITATIVE", "feature": "AUTHORITATIVE", "interface": "AUTHORITATIVE", "architecture": "AUTHORITATIVE", "test-obligation": "AUTHORITATIVE", "task": "AUTHORITATIVE", "research": "EVIDENCE", "experiment": "EVIDENCE", "lesson": "EVIDENCE"}});
            resolve_with(&self.root, &auth, &store, store.get(task).unwrap())
        }
    }
    impl Drop for Fx {
        fn drop(&mut self) {
            let _ = std::fs::remove_dir_all(&self.root);
        }
    }

    fn base() -> Fx {
        let fx = Fx::new();
        fx.put("spec/features/F-0001.yaml", "id: F-0001\ntype: feature\nstatus: ACTIVE\nrequirements: [REQ-0002]\nscenarios: [SCN-0001]\nreadiness: {}\n");
        fx.put(
            "spec/scenarios/SCN-0001.yaml",
            "id: SCN-0001\ntype: scenario\nstatus: ACTIVE\n",
        );
        fx.put(
            "spec/requirements/REQ-0001.yaml",
            "id: REQ-0001\ntype: requirement\nstatus: SUPERSEDED\nsuperseded_by: REQ-0002\n",
        );
        fx.put(
            "spec/requirements/REQ-0002.yaml",
            "id: REQ-0002\ntype: requirement\nstatus: ACTIVE\nsupersedes: [REQ-0001]\n",
        );
        fx.put(
            "spec/requirements/REQ-0003.yaml",
            "id: REQ-0003\ntype: requirement\nstatus: ACTIVE\nstate_class: NARRATIVE\n",
        );
        fx.put(
            "spec/research/RES-0001.yaml",
            "id: RES-0001\ntype: research\nstatus: ACTIVE\n",
        );
        fx.put(
            "spec/data/DATA-0001.yaml",
            "id: DATA-0001\ntype: data\nstatus: ACTIVE\n",
        );
        fx.put(
            "spec/architecture/ARCH-0001.yaml",
            "id: ARCH-0001\ntype: architecture\nstatus: ACTIVE\n",
        );
        fx.put(
            "spec/interfaces/API-0001.yaml",
            "id: API-0001\ntype: interface\nstatus: ACTIVE\nversion: 2.3.1\n",
        );
        fx
    }

    #[test]
    fn a_complete_manifest_is_satisfied_and_names_every_input() {
        let fx = base();
        fx.put("spec/tasks/TASK-0001.yaml", "id: TASK-0001\ntype: task\nstatus: ACTIVE\nfeature: F-0001\nrequired_data: [DATA-0001]\nderived_from: [RES-0001]\ninterfaces: [API-0001]\nrequired_inputs: [{id: API-0001, reason: the exported contract, version: '^2.3', content_hash: ''}]\n");
        let m = fx.manifest("TASK-0001");
        assert!(m.satisfied(), "{}", m.to_value());
        let ids: Vec<(&str, &str)> = m
            .entries
            .iter()
            .map(|e| (e.id.as_str(), e.slot.name()))
            .collect();
        for want in [
            ("F-0001", "feature"),
            ("REQ-0002", "requirement"),
            ("SCN-0001", "scenario"),
            ("DATA-0001", "dataset"),
            ("RES-0001", "evidence"),
            ("API-0001", "interface"),
            ("ARCH-0001", "architecture"),
        ] {
            assert!(ids.contains(&want), "{want:?} not in {ids:?}");
        }
        let api = m.entries.iter().find(|e| e.id == "API-0001").unwrap();
        assert_eq!(api.reason(), json!("the exported contract"));
        assert!(api.content_hash.as_ref().unwrap().len() == 64);
        let arch = m.entries.iter().find(|e| e.id == "ARCH-0001").unwrap();
        assert!(
            !arch.required,
            "implicit architecture is delivered but not declared"
        );
    }

    #[test]
    fn absent_wrong_type_superseded_and_non_authoritative_inputs_block() {
        let fx = base();
        fx.put("spec/tasks/TASK-0002.yaml", "id: TASK-0002\ntype: task\nstatus: ACTIVE\nrequirements: [REQ-0001, REQ-0003, REQ-9999, RES-0001]\n");
        let m = fx.manifest("TASK-0002");
        assert_eq!(m.delivery_state(), "BLOCKED");
        let code = |id: &str| -> Vec<&str> {
            let e = m
                .entries
                .iter()
                .find(|e| e.id == id && e.slot == Slot::Requirement)
                .unwrap();
            if e.delivered() {
                e.problems
                    .iter()
                    .filter(|p| p.blocking)
                    .map(|p| p.code)
                    .collect()
            } else {
                vec![e.resolution]
            }
        };
        assert!(code("REQ-0001").contains(&"SUPERSEDED"));
        assert!(code("REQ-0003").contains(&"AUTHORITY_CLASS"));
        assert_eq!(code("REQ-9999"), vec!["ABSENT"]);
        assert_eq!(code("RES-0001"), vec!["TYPE_MISMATCH"]);
        let sup = m.entries.iter().find(|e| e.id == "REQ-0001").unwrap();
        assert_eq!(sup.authority_flag.as_deref(), Some("SUPERSEDED"));
        assert_eq!(sup.superseded_by.as_deref(), Some("REQ-0002"));
        assert_eq!(m.missing().len(), 2);
        assert_eq!(m.violations().len(), 2);
        assert!(m.blocking_reason().unwrap().contains("REQ-9999"));
    }

    #[test]
    fn state_version_and_hash_constraints_are_enforced() {
        let fx = base();
        fx.put("spec/tasks/TASK-0003.yaml", "id: TASK-0003\ntype: task\nstatus: ACTIVE\nrequired_inputs:\n  - {id: API-0001, version: '>=3.0.0', reason: needs v3}\n  - {id: REQ-0002, content_hash: '000000000000000000000000', reason: pinned}\n  - {id: DATA-0001, required_status: PROVISIONAL, reason: draft data}\n");
        let m = fx.manifest("TASK-0003");
        let codes: Vec<&str> = m
            .entries
            .iter()
            .flat_map(|e| e.problems.iter().filter(|p| p.blocking).map(|p| p.code))
            .collect();
        assert!(
            codes.contains(&"VERSION_MISMATCH")
                && codes.contains(&"HASH_MISMATCH")
                && codes.contains(&"LIFECYCLE_STATE"),
            "{codes:?}"
        );
        // a superseded input explicitly required for archaeology is delivered, flagged, and not blocking
        fx.put("spec/tasks/TASK-0004.yaml", "id: TASK-0004\ntype: task\nstatus: ACTIVE\nrequired_inputs: [{id: REQ-0001, required_status: [SUPERSEDED], reason: compare old rule}]\n");
        let m = fx.manifest("TASK-0004");
        let e = m.entries.iter().find(|e| e.id == "REQ-0001").unwrap();
        assert!(e.satisfied(), "{}", e.to_value());
        assert_eq!(e.authority_flag.as_deref(), Some("SUPERSEDED"));
    }

    #[test]
    fn relations_notes_and_supplementary_context_are_declarations() {
        let fx = base();
        fx.put("spec/tasks/TASK-0005.yaml", "id: TASK-0005\ntype: task\nstatus: ACTIVE\nrelations: [{type: GOVERNED_BY, target: REQ-0002, note: rounding rule this task implements}]\nsupplementary_context: [RES-9999, {id: RES-0001, reason: background}]\n");
        let m = fx.manifest("TASK-0005");
        let e = m.entries.iter().find(|e| e.id == "REQ-0002").unwrap();
        assert_eq!(e.reason(), json!("rounding rule this task implements"));
        assert!(e.required && e.satisfied());
        assert_eq!(m.supplementary.len(), 2);
        assert_eq!(m.supplementary[0]["resolution"], "ABSENT");
        assert!(m.satisfied(), "supplementary context never blocks");
    }

    #[test]
    fn output_contracts_in_the_schema_are_the_enforced_table() {
        let schema: Value = serde_json::from_str(
            &std::fs::read_to_string(
                std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
                    .join("../framework/schemas/context-packet.schema.json"),
            )
            .unwrap(),
        )
        .unwrap();
        let contracts = schema["x-output-contracts"]["output_contracts"]
            .as_object()
            .unwrap();
        for slot in Slot::ALL {
            let declared: Vec<&str> = contracts
                .iter()
                .filter(|(t, c)| {
                    *t != "*"
                        && c["consumable_as"]
                            .as_array()
                            .unwrap()
                            .iter()
                            .any(|s| s == slot.name())
                })
                .map(|(t, _)| t.as_str())
                .collect();
            let any = contracts["*"]["consumable_as"]
                .as_array()
                .unwrap()
                .iter()
                .any(|s| s == slot.name());
            if slot.expected_types().is_empty() {
                assert!(
                    any,
                    "slot {} accepts any type but the schema does not say so",
                    slot.name()
                );
            } else {
                assert!(
                    !any,
                    "slot {} is typed but the schema lets any type in",
                    slot.name()
                );
                let mut want: Vec<&str> = slot.expected_types().to_vec();
                let mut got = declared.clone();
                want.sort();
                got.sort();
                assert_eq!(
                    got,
                    want,
                    "slot {}: schema output contracts vs enforced types",
                    slot.name()
                );
            }
            for t in declared {
                assert_eq!(
                    Slot::for_type(t),
                    slot,
                    "{t} is consumable as {} but defaults elsewhere",
                    slot.name()
                );
            }
        }
    }

    #[test]
    fn version_constraints() {
        assert!(version_satisfies("2.3.1", "2.3.1"));
        assert!(version_satisfies("2.3.1", "^2.3"));
        assert!(!version_satisfies("3.0.0", "^2.3"));
        assert!(version_satisfies("2.4.0", ">=2.3.1 <3"));
        assert!(!version_satisfies("2.3.0", ">=2.3.1"));
        assert!(version_satisfies("2.3.9", "~2.3"));
        assert!(!version_satisfies("2.4.0", "~2.3"));
        assert!(version_satisfies("anything", "*"));
    }
}
