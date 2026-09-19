//! **Contradictions among authoritative inputs: detection and routing** (BC-P2-18, detection side; Contract v3:657-660
//! L1 "deterministic precedence first; low-impact/reversible/high-confidence agent resolution where allowed; human
//! escalation for consequential uncertainty", :1103 W3 "Conflicting mandatory inputs trigger contradiction handling";
//! framework §50).
//!
//! Framework §50: *conflict → deterministic precedence resolves? yes → fix + record; no → low impact + high
//! confidence + reversible? yes → agent resolves + records rationale; no → Human Decision Gate.*
//!
//! * **Precedence first.** Records linked by supersession (directly or transitively) never contradict: the successor
//!   governs and `context::manifest` already refuses the superseded one as a current input (`SUPERSEDED`,
//!   `UNKNOWN_OR_CONFLICTING`). A superseded record still marked current is reported with its fix (a CIT recording the
//!   supersession) but needs no decision.
//! * **Undecidable contradictions are detected** ([`detect_among`]) between current, authoritative records:
//!   `DECLARED_CONFLICT` (a record names another in `conflicts_with`/`contradicts`), `SUPERSESSION_FORK` (two current
//!   records both supersede the same record, neither supersedes the other), and `DECISION_CONFLICT` (two current
//!   decisions answer the same question differently — the same declared `decision_key`/`topic`/`subject`, the same
//!   `question`, or the same subject once each title is stripped of its own choice — with different chosen options).
//! * **They are never delivered together as authority.** In a task's input manifest every member of an unresolved
//!   contradiction is flagged `CONTRADICTORY` with a blocking `CONTRADICTION` problem, so the packet delivers them as
//!   conflicting (not active) decisions, the manifest is `BLOCKED` and the task cannot be READY (`require_ready`).
//! * **They are routed** ([`route`]) to a system-raised Human Decision Gate (`trigger: contradiction`) whose package
//!   carries the OS's own assessment: impact radius from what the records govern, detection confidence, and
//!   reversibility. The existing answer rules then decide who may resolve it: an L3+ agent within
//!   `HUMAN_GATE_POLICY.agent_resolvable_when` on this OS-sourced assessment, otherwise the human.
//! * **The answer resolves them** ([`resolution`]), read only through `gates::verified_answer`: one member governs and
//!   the others are set aside as authority (`SET_ASIDE_BY_RESOLUTION`; blocking where a task explicitly declared a
//!   set-aside record), or the records are compatible, or neither governs until revised (still blocking). The
//!   option→outcome table is part of the gate's `subject`, inside the package the answer binds.
use crate::orchestration::gates;
use crate::records::{Record, RecordStore};
use crate::util::{canonical_json, now_iso, sha256_hex};
use crate::{Project, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

/// Lifecycle states of a current record (a contradiction is only between current records).
const CURRENT: &[&str] = &["ACTIVE", "PROVISIONAL"];
/// The gate trigger contradictions are routed under.
pub const TRIGGER: &str = "contradiction";

/// One detected contradiction.
#[derive(Debug, Clone, PartialEq)]
pub struct Contradiction {
    pub kind: &'static str,
    pub members: Vec<String>,
    pub subject: String,
    pub evidence: Vec<String>,
    /// How confident the detection is (explicit declarations and forks: 0.9; same question: 0.85; derived subject: 0.6).
    pub confidence: f64,
    pub key: String,
}

impl Contradiction {
    fn new(
        kind: &'static str,
        mut members: Vec<String>,
        subject: String,
        evidence: Vec<String>,
        confidence: f64,
    ) -> Self {
        members.sort();
        members.dedup();
        let key = sha256_hex(canonical_json(&json!({"kind": kind, "members": members})).as_bytes());
        Contradiction {
            kind,
            members,
            subject,
            evidence,
            confidence,
            key,
        }
    }
    pub fn to_value(&self) -> Value {
        json!({"kind": self.kind, "members": self.members, "subject": self.subject, "evidence": self.evidence,
               "detection_confidence": self.confidence, "key": self.key})
    }
}

fn current(r: &Record) -> bool {
    CURRENT.contains(&r.status().as_str()) && !r.problems.iter().any(|p| p == "archived")
}

fn norm(s: &str) -> String {
    s.to_lowercase()
        .split(|c: char| !c.is_alphanumeric())
        .filter(|t| !t.is_empty())
        .collect::<Vec<_>>()
        .join(" ")
}

const STOPWORDS: &[&str] = &[
    "a", "an", "the", "is", "are", "be", "in", "on", "of", "for", "to", "use", "uses", "using",
    "with", "as", "by", "and", "or", "we", "will", "shall", "should", "must", "at", "via", "into",
];

/// The text a decision chose: the chosen option's description when the record lists its options, else the
/// chosen option itself.
fn choice_text(d: &Record) -> String {
    let chosen = d.get("chosen_option");
    if let Some(opts) = d.data.get("options").and_then(|v| v.as_array()) {
        if let Some(o) = opts
            .iter()
            .find(|o| o["id"].as_str() == Some(chosen.as_str()))
        {
            if let Some(desc) = o["description"].as_str().filter(|s| !s.trim().is_empty()) {
                return desc.to_string();
            }
        }
    }
    chosen
}

/// A decision's subject once its own choice is removed from its title (or question): "Persist payments in
/// Postgres" choosing "postgres" → "persist payments". `None` when fewer than two content words remain.
fn derived_subject(d: &Record) -> Option<String> {
    let choice: BTreeSet<String> = norm(&choice_text(d))
        .split(' ')
        .filter(|t| !t.is_empty())
        .map(String::from)
        .collect();
    let base = if !d.get("question").is_empty() {
        d.get("question")
    } else {
        d.title()
    };
    let words: Vec<String> = norm(&base)
        .split(' ')
        .filter(|t| !t.is_empty() && !choice.contains(*t) && !STOPWORDS.contains(t))
        .map(String::from)
        .collect();
    if words.len() >= 2 {
        Some(words.join(" "))
    } else {
        None
    }
}

fn explicit_key(d: &Record) -> Option<String> {
    for k in ["decision_key", "topic", "subject"] {
        if let Some(s) = d.data.get(k).and_then(|v| v.as_str()) {
            let n = norm(s);
            if !n.is_empty() {
                return Some(n);
            }
        }
    }
    None
}

/// `id -> every record id it supersedes (transitively)`, over all non-archived records.
fn supersession_closure(store: &RecordStore) -> BTreeMap<String, BTreeSet<String>> {
    let mut direct: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    for r in &store.records {
        if r.problems.iter().any(|p| p == "archived") || r.id().is_empty() {
            continue;
        }
        for s in r.list("supersedes") {
            direct.entry(r.id()).or_default().insert(s);
        }
        let sb = r.get("superseded_by");
        if !sb.is_empty() {
            direct.entry(sb).or_default().insert(r.id());
        }
    }
    let mut out: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    for k in direct.keys() {
        let mut seen = BTreeSet::new();
        let mut stack: Vec<String> = direct[k].iter().cloned().collect();
        while let Some(x) = stack.pop() {
            if seen.insert(x.clone()) {
                if let Some(n) = direct.get(&x) {
                    stack.extend(n.iter().cloned());
                }
            }
        }
        out.insert(k.clone(), seen);
    }
    out
}

fn linked(clo: &BTreeMap<String, BTreeSet<String>>, a: &str, b: &str) -> bool {
    clo.get(a).map(|s| s.contains(b)).unwrap_or(false)
        || clo.get(b).map(|s| s.contains(a)).unwrap_or(false)
}

/// **Contradictions among the current records named by `ids`** (pure; precedence-linked pairs are never
/// contradictions).
pub fn detect_among(store: &RecordStore, ids: &[String]) -> Vec<Contradiction> {
    let clo = supersession_closure(store);
    let recs: Vec<&Record> = {
        let mut seen = BTreeSet::new();
        ids.iter()
            .filter(|i| seen.insert((*i).clone()))
            .filter_map(|i| store.get(i))
            .filter(|r| current(r))
            .collect()
    };
    let mut out: Vec<Contradiction> = vec![];
    let push = |out: &mut Vec<Contradiction>, c: Contradiction| {
        if !out.iter().any(|x| x.key == c.key) {
            out.push(c);
        }
    };
    for (i, a) in recs.iter().enumerate() {
        for b in recs.iter().skip(i + 1) {
            let (ai, bi) = (a.id(), b.id());
            if ai == bi || linked(&clo, &ai, &bi) {
                continue;
            }
            let declared = ["conflicts_with", "contradicts"]
                .iter()
                .any(|f| a.list(f).contains(&bi) || b.list(f).contains(&ai));
            if declared {
                push(
                    &mut out,
                    Contradiction::new(
                        "DECLARED_CONFLICT",
                        vec![ai.clone(), bi.clone()],
                        format!("{} / {}", a.title(), b.title()),
                        vec![format!(
                            "{ai} and {bi} are declared to conflict (conflicts_with/contradicts)"
                        )],
                        0.9,
                    ),
                );
                continue;
            }
            if a.rtype() != "decision" || b.rtype() != "decision" {
                continue;
            }
            let (ca, cb) = (norm(&choice_text(a)), norm(&choice_text(b)));
            if ca.is_empty() || cb.is_empty() || ca == cb {
                continue;
            }
            let same = if let (Some(ka), Some(kb)) = (explicit_key(a), explicit_key(b)) {
                (ka == kb).then(|| (format!("decision key '{ka}'"), 0.9))
            } else if !a.get("question").is_empty()
                && norm(&a.get("question")) == norm(&b.get("question"))
            {
                Some((format!("question '{}'", a.get("question")), 0.85))
            } else {
                match (derived_subject(a), derived_subject(b)) {
                    (Some(sa), Some(sb)) if sa == sb => Some((format!("subject '{sa}'"), 0.6)),
                    _ => None,
                }
            };
            if let Some((subject, conf)) = same {
                push(
                    &mut out,
                    Contradiction::new(
                        "DECISION_CONFLICT",
                        vec![ai.clone(), bi.clone()],
                        subject.clone(),
                        vec![format!("{ai} chooses '{}' and {bi} chooses '{}' for the same {subject}, and neither supersedes the other", choice_text(a), choice_text(b))],
                        conf,
                    ),
                );
            }
        }
    }
    // two current successors of one record: which governs is undecidable by precedence
    let mut succ: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for r in &recs {
        for s in r.list("supersedes") {
            succ.entry(s).or_default().push(r.id());
        }
    }
    for (old, heirs) in succ {
        if heirs.len() < 2 {
            continue;
        }
        for (i, a) in heirs.iter().enumerate() {
            for b in heirs.iter().skip(i + 1) {
                if linked(&clo, a, b) {
                    continue;
                }
                push(
                    &mut out,
                    Contradiction::new(
                        "SUPERSESSION_FORK",
                        vec![a.clone(), b.clone()],
                        format!("successor of {old}"),
                        vec![format!(
                            "{a} and {b} both supersede {old}; neither supersedes the other"
                        )],
                        0.9,
                    ),
                );
            }
        }
    }
    out
}

/// **Every contradiction among current records of the project** (for `gov artefact check`, and the audit/doctor
/// families — integration point for WS-2). Decisions are compared when their scopes overlap (a shared
/// `affects`/`governed_by`/`feature` target, or neither scoped); declared conflicts and forks always count.
pub fn detect_all(store: &RecordStore) -> Vec<Contradiction> {
    let ids: Vec<String> = store
        .records
        .iter()
        .filter(|r| current(r) && !r.id().is_empty())
        .map(|r| r.id())
        .collect();
    let scope = |r: &Record| -> BTreeSet<String> {
        let mut s: BTreeSet<String> = r
            .list("affects")
            .into_iter()
            .chain(r.list("governed_by"))
            .collect();
        let f = r.get("feature");
        if !f.is_empty() {
            s.insert(f);
        }
        s
    };
    detect_among(store, &ids)
        .into_iter()
        .filter(|c| {
            if c.kind != "DECISION_CONFLICT" {
                return true;
            }
            let sets: Vec<BTreeSet<String>> = c
                .members
                .iter()
                .filter_map(|m| store.get(m))
                .map(scope)
                .collect();
            sets.iter().all(|s| s.is_empty())
                || sets
                    .windows(2)
                    .all(|w| !w[0].is_disjoint(&w[1]) || w[0].is_empty() || w[1].is_empty())
        })
        .collect()
}

/// How a contradiction stands.
#[derive(Debug, Clone, PartialEq)]
pub enum Resolution {
    /// No honoured answer: `gate` is the open gate it was routed to, if any.
    Unresolved { gate: Option<String> },
    /// One member governs; the others are set aside as authority.
    Prevails {
        gate: String,
        decision: Option<String>,
        prevailing: Vec<String>,
        set_aside: Vec<String>,
        by_kind: String,
    },
    /// The records do not contradict; all stand.
    Compatible {
        gate: String,
        decision: Option<String>,
        by_kind: String,
    },
    /// The answer holds the dependent work until the records are revised.
    Held { gate: String, option: String },
}

impl Resolution {
    pub fn blocks(&self) -> bool {
        matches!(
            self,
            Resolution::Unresolved { .. } | Resolution::Held { .. }
        )
    }
    pub fn to_value(&self) -> Value {
        match self {
            Resolution::Unresolved { gate } => json!({"state": "UNRESOLVED", "gate": gate}),
            Resolution::Prevails {
                gate,
                decision,
                prevailing,
                set_aside,
                by_kind,
            } => {
                json!({"state": "RESOLVED", "outcome": "prevails", "gate": gate, "decision": decision, "prevailing": prevailing, "set_aside": set_aside, "resolved_by_kind": by_kind})
            }
            Resolution::Compatible {
                gate,
                decision,
                by_kind,
            } => {
                json!({"state": "RESOLVED", "outcome": "compatible", "gate": gate, "decision": decision, "resolved_by_kind": by_kind})
            }
            Resolution::Held { gate, option } => {
                json!({"state": "HELD", "gate": gate, "option": option, "note": "the answer holds the dependent work until the records are revised through change control"})
            }
        }
    }
}

/// Gates raised for contradiction `key`, oldest first.
fn gates_for(store: &RecordStore, key: &str) -> Vec<Record> {
    let mut v: Vec<Record> = store
        .of_type("human-gate")
        .into_iter()
        .filter(|g| {
            g.get("trigger") == TRIGGER && g.data["subject"]["sha256"].as_str() == Some(key)
        })
        .cloned()
        .collect();
    v.sort_by_key(|g| g.id());
    v
}

/// **How contradiction `c` stands**: the newest gate with an honoured answer decides (read through
/// `gates::verified_answer`); otherwise the open gate it was routed to, if any.
pub fn resolution(p: &Project, store: &RecordStore, c: &Contradiction) -> Resolution {
    let gs = gates_for(store, &c.key);
    for g in gs.iter().rev() {
        if g.get("gate_status") != "ANSWERED" {
            continue;
        }
        let Ok(a) = gates::verified_answer_in(p, store, &g.id()) else {
            continue;
        };
        let outcome = &a.record.data["subject"]["outcomes"][&a.option];
        if !a.authorises_blocked_work || outcome["hold"].as_bool() == Some(true) {
            return Resolution::Held {
                gate: g.id(),
                option: a.option,
            };
        }
        if outcome["compatible"].as_bool() == Some(true) {
            return Resolution::Compatible {
                gate: g.id(),
                decision: a.decision,
                by_kind: a.by_kind,
            };
        }
        let list = |k: &str| -> Vec<String> {
            outcome[k]
                .as_array()
                .map(|x| {
                    x.iter()
                        .filter_map(|v| v.as_str().map(String::from))
                        .collect()
                })
                .unwrap_or_default()
        };
        let prevailing = list("prevails");
        if !prevailing.is_empty() {
            return Resolution::Prevails {
                gate: g.id(),
                decision: a.decision,
                prevailing,
                set_aside: list("set_aside"),
                by_kind: a.by_kind,
            };
        }
    }
    let open = gs
        .iter()
        .rev()
        .find(|g| matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED"))
        .map(|g| g.id());
    Resolution::Unresolved { gate: open }
}

/// The OS's assessment of a contradiction: radius from what the records govern.
fn assessed_radius(store: &RecordStore, c: &Contradiction) -> &'static str {
    let recs: Vec<&Record> = c.members.iter().filter_map(|m| store.get(m)).collect();
    let tagged = |r: &Record, w: &str| {
        r.list("tags").iter().any(|t| t.to_lowercase().contains(w)) || r.rtype() == w
    };
    if recs
        .iter()
        .any(|r| tagged(r, "architect") || tagged(r, "security") || tagged(r, "governance"))
    {
        "R3"
    } else if !recs.is_empty() && recs.iter().all(|r| r.status() == "PROVISIONAL") {
        "R1"
    } else {
        "R2"
    }
}

/// **Route contradiction `c` to its decision point**: the open (or answered) gate for it when one exists, otherwise
/// a new system-raised gate (`trigger: contradiction`) carrying the OS's assessment and the option→outcome table.
/// `tasks` are the tasks whose mandatory inputs include the members (named in the package, blocked by their
/// manifests). Returns `{"gate", "raised": bool}`.
pub fn route(
    p: &Project,
    store: &RecordStore,
    c: &Contradiction,
    tasks: &[String],
) -> Result<Value> {
    match resolution(p, store, c) {
        Resolution::Unresolved { gate: Some(g) } => {
            return Ok(json!({"gate": g, "raised": false, "state": "UNRESOLVED"}))
        }
        Resolution::Unresolved { gate: None } => {}
        other => {
            return Ok(
                json!({"gate": other.to_value()["gate"], "raised": false, "state": other.to_value()["state"]}),
            )
        }
    }
    let letters = ["A", "B", "C", "D", "E", "F", "G", "H"];
    let mut options = vec![];
    let mut outcomes = serde_json::Map::new();
    for (i, m) in c.members.iter().enumerate().take(letters.len() - 2) {
        let others: Vec<String> = c.members.iter().filter(|x| *x != m).cloned().collect();
        let title = store.get(m).map(|r| r.title()).unwrap_or_default();
        options.push(json!({"id": letters[i], "description": format!("{m} ({title}) governs; {} is set aside as authority until it is revised or superseded through change control", others.join(", ")), "authorises_blocked_work": true}));
        outcomes.insert(
            letters[i].into(),
            json!({"prevails": [m], "set_aside": others}),
        );
    }
    let n = options.len();
    options.push(json!({"id": letters[n], "description": format!("{} do not contradict each other: all stand (record why in the rationale)", c.members.join(" and ")), "authorises_blocked_work": true}));
    outcomes.insert(letters[n].into(), json!({"compatible": true}));
    options.push(json!({"id": letters[n + 1], "description": "neither governs until the records are revised through change control; the dependent work stays blocked", "authorises_blocked_work": false}));
    outcomes.insert(letters[n + 1].into(), json!({"hold": true}));
    let radius = assessed_radius(store, c);
    let g = gates::create_system(
        p,
        json!({
            "question": format!("Contradictory authoritative inputs: {} disagree on the same {} — which governs?", c.members.join(" and "), c.subject),
            "why_now": format!("deterministic precedence cannot resolve it ({}); the dependent work {} cannot proceed on contradictory authority", c.kind, if tasks.is_empty() { "(none yet)".to_string() } else { tasks.join(", ") }),
            "current_state": format!("{}; the members are delivered to workers only as conflicting, not as active authority, and the tasks' input manifests are BLOCKED", c.evidence.join("; ")),
            "options": options,
            "impact": format!("tasks {} stay blocked until this is resolved; the resolution sets the other record(s) aside as authority", if tasks.is_empty() { "(none yet)".to_string() } else { tasks.join(", ") }),
            "reversibility": "reversible: the resolution is a recorded decision; a later change-impact transaction can supersede either record",
            "cost_rework": format!("{} dependent task(s) may need rework if the wrong record governs", tasks.len()),
            "recommendation": "choose the record that reflects the current product direction; if both genuinely stand, choose the compatibility option and say why",
            "confidence": c.confidence,
            "impact_radius": radius,
            "trigger": TRIGGER,
            "blocks_tasks": [],
            "subject": {"kind": "contradiction", "sha256": c.key, "contradiction_kind": c.kind, "members": c.members, "subject": c.subject, "outcomes": Value::Object(outcomes), "tasks": tasks, "detected_at": now_iso()},
            "title": format!("Contradiction: {}", c.members.join(" vs ")),
        }),
    )?;
    Ok(
        json!({"gate": g["id"], "raised": true, "state": "UNRESOLVED", "radius": radius, "confidence": c.confidence}),
    )
}

/// Route every unresolved contradiction among `task_id`'s mandatory inputs (the dispatch-time trigger:
/// `context::compile_tolerant`). Failures are reported, never raised: a refused gate creation (for example below
/// the security floor) leaves the manifest BLOCKED, which is the safe state.
pub fn route_for_task(p: &Project, task_id: &str) -> Value {
    let store = RecordStore::load(&p.root);
    let Some(t) = store.get(task_id) else {
        return json!([]);
    };
    let m = crate::context::manifest::resolve(p, &store, t);
    let mut out = vec![];
    for c in m.contradictions.iter() {
        let unresolved =
            c["resolution"]["state"] == "UNRESOLVED" && c["resolution"]["gate"].is_null();
        if !unresolved {
            continue;
        }
        let members: Vec<String> = c["members"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(String::from))
                    .collect()
            })
            .unwrap_or_default();
        let found = detect_among(&store, &members);
        let Some(con) = found
            .into_iter()
            .find(|x| Some(x.key.as_str()) == c["key"].as_str())
        else {
            continue;
        };
        let tasks: Vec<String> = store
            .of_type("task")
            .into_iter()
            .filter(|x| !matches!(x.get("task_status").as_str(), "DONE" | "CANCELLED"))
            .filter(|x| {
                let mm = crate::context::manifest::resolve_with(&p.root, &json!({}), &store, x);
                con.members
                    .iter()
                    .all(|id| mm.entries.iter().any(|e| &e.id == id))
            })
            .map(|x| x.id())
            .collect();
        match route(p, &store, &con, &tasks) {
            Ok(v) => out.push(json!({"contradiction": con.to_value(), "routed": v})),
            Err(e) => out.push(json!({"contradiction": con.to_value(), "routed": null, "error": {"code": e.code, "message": e.message}})),
        }
    }
    json!(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::records::parse_record_text;

    fn store(recs: &[(&str, &str)]) -> RecordStore {
        let records: Vec<Record> = recs
            .iter()
            .map(|(path, text)| parse_record_text(text, path).unwrap())
            .collect();
        let mut by_id = std::collections::BTreeMap::new();
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
    fn precedence_resolves_first_and_undecidable_pairs_are_detected() {
        let s = store(&[
            ("spec/decisions/D-0101.yaml", "id: D-0101\ntype: decision\ntitle: Retry limit is 3\nstatus: ACTIVE\nchosen_option: '3'\naffects: [F-0001]\n"),
            ("spec/decisions/D-0102.yaml", "id: D-0102\ntype: decision\ntitle: Retry limit is 5\nstatus: ACTIVE\nchosen_option: '5'\nsupersedes: [D-0101]\naffects: [F-0001]\n"),
            ("spec/decisions/D-0103.yaml", "id: D-0103\ntype: decision\ntitle: Persist payments in Postgres\nstatus: ACTIVE\nchosen_option: postgres\naffects: [F-0001]\n"),
            ("spec/decisions/D-0104.yaml", "id: D-0104\ntype: decision\ntitle: Persist payments in MySQL\nstatus: ACTIVE\nchosen_option: mysql\naffects: [F-0001]\n"),
        ]);
        let ids: Vec<String> = ["D-0101", "D-0102", "D-0103", "D-0104"]
            .iter()
            .map(|s| s.to_string())
            .collect();
        let found = detect_among(&s, &ids);
        assert_eq!(found.len(), 1, "{found:?}");
        assert_eq!(found[0].kind, "DECISION_CONFLICT");
        assert_eq!(
            found[0].members,
            vec!["D-0103".to_string(), "D-0104".to_string()]
        );
        assert!(
            found[0].confidence < 0.8,
            "a subject derived from titles is not high-confidence"
        );
        assert_eq!(detect_all(&s).len(), 1);
    }

    #[test]
    fn explicit_keys_questions_forks_and_declared_conflicts() {
        let s = store(&[
            ("spec/decisions/D-1.yaml", "id: D-1\ntype: decision\ntitle: Queue\nstatus: ACTIVE\ndecision_key: message-broker\nchosen_option: A\noptions: [{id: A, description: kafka}]\n"),
            ("spec/decisions/D-2.yaml", "id: D-2\ntype: decision\ntitle: Broker\nstatus: PROVISIONAL\ndecision_key: Message broker\nchosen_option: A\noptions: [{id: A, description: rabbitmq}]\n"),
            ("spec/decisions/D-3.yaml", "id: D-3\ntype: decision\ntitle: t3\nstatus: ACTIVE\nsupersedes: [D-0]\nchosen_option: x\n"),
            ("spec/decisions/D-4.yaml", "id: D-4\ntype: decision\ntitle: t4\nstatus: ACTIVE\nsupersedes: [D-0]\nchosen_option: y\n"),
            ("spec/requirements/REQ-1.yaml", "id: REQ-1\ntype: requirement\ntitle: r1\nstatus: ACTIVE\nconflicts_with: [REQ-2]\n"),
            ("spec/requirements/REQ-2.yaml", "id: REQ-2\ntype: requirement\ntitle: r2\nstatus: ACTIVE\n"),
            ("spec/decisions/D-5.yaml", "id: D-5\ntype: decision\ntitle: Same choice\nstatus: ACTIVE\ndecision_key: message-broker\nchosen_option: A\noptions: [{id: A, description: kafka}]\n"),
        ]);
        let ids: Vec<String> = s.records.iter().map(|r| r.id()).collect();
        let found = detect_among(&s, &ids);
        let kinds: Vec<(&str, Vec<String>)> =
            found.iter().map(|c| (c.kind, c.members.clone())).collect();
        assert!(
            kinds.contains(&("DECISION_CONFLICT", vec!["D-1".into(), "D-2".into()])),
            "{kinds:?}"
        );
        assert!(
            kinds.contains(&("DECISION_CONFLICT", vec!["D-2".into(), "D-5".into()])),
            "{kinds:?}"
        );
        assert!(
            !kinds
                .iter()
                .any(|(_, m)| m == &vec!["D-1".to_string(), "D-5".to_string()]),
            "the same choice is not a contradiction"
        );
        assert!(
            kinds.contains(&("SUPERSESSION_FORK", vec!["D-3".into(), "D-4".into()])),
            "{kinds:?}"
        );
        assert!(
            kinds.contains(&("DECLARED_CONFLICT", vec!["REQ-1".into(), "REQ-2".into()])),
            "{kinds:?}"
        );
    }
}
