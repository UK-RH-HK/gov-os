//! Failure memory (framework §11.8 "structured records of … retrieval misses; … tool failures", §18 "A retrieval
//! failure creates an explicit memory-quality event"; Contract v3 C8, :276-283; BC-P2-32).
//!
//! A failure the product observes becomes a **durable, structured, kind-distinguishable governed record** of record
//! type `failure` with `failure_kind` one of [`KINDS`], in the tracked tree (never in the derived runtime store), so
//! it survives every memory rebuild, and with a `follow_up` block that the work generator (BC-P2-24) links to the task
//! it creates ([`link_follow_up`]). Tool failures and the other kinds live in `spec/reports/failures/` and are indexed
//! like any evidence record, so a later session recalls them through the fabric. Retrieval misses are memory-quality
//! events: they live in `spec/reports/memory-quality/` and, like the held-out set, are never indexed (a record of a
//! missed query must not answer that query, and recording a miss must not move the index a context packet was just
//! compiled against). One record exists per failure *signature* (kind + what failed), so a repeated failure is
//! reported against its existing record instead of flooding the tree.
//!
//! Writers in this workstream: ad-hoc retrieval misses (`retrieval::retrieve` for logged agent queries), code
//! intelligence adapter failures and embedder/reranker failures (`memory::indexer::rebuild`, `retrieval`).
//! Other producers call [`record`] (tool health checks, held-out regression runs — see the integration points in
//! the WS-6 repair report). Recording never fails the operation that observed the failure: the outcome says whether
//! a record was written, found, or not written and why (e.g. FREEZE_WRITES).
use crate::records::{Record, RecordFormat};
use crate::util::{now_iso, read_text, sha256_hex, today};
use crate::{Project, Result};
use serde_json::{json, Value};

/// Canonical directory of failure records (under the OS-written evidence tree `spec/reports/`). Indexed like any
/// evidence record, so a later session recalls a tool failure through the fabric.
pub const FAILURE_DIR: &str = "spec/reports/failures";
/// Canonical directory of memory-quality events (retrieval misses). Durable and governed like every failure record,
/// but — like the held-out retrieval set (framework §17) — **never indexed**: a record of a missed query would
/// otherwise answer that query itself, and recording a miss must not change the index a caller (a context packet)
/// has just been compiled against. `memory::indexer` and `manifest::freshness` skip this directory.
pub const MEMORY_QUALITY_DIR: &str = "spec/reports/memory-quality";

/// True for a path under [`MEMORY_QUALITY_DIR`] (never indexed).
pub fn is_memory_quality_path(rel: &str) -> bool {
    rel.starts_with(&format!("{MEMORY_QUALITY_DIR}/"))
}

fn dir_for(kind: &str) -> &'static str {
    if kind == "retrieval-miss" {
        MEMORY_QUALITY_DIR
    } else {
        FAILURE_DIR
    }
}
/// Record type and id prefix of failure records.
pub const RECORD_TYPE: &str = "failure";
pub const ID_PREFIX: &str = "FAIL";
/// The failure kinds of framework §11.8, as recorded in `failure_kind`.
pub const KINDS: &[&str] = &[
    "bug",
    "failed-approach",
    "incorrect-assumption",
    "retrieval-miss",
    "regression",
    "migration-failure",
    "tool-failure",
];

/// A failure observed by a product operation.
#[derive(Debug, Clone)]
pub struct FailureEvent {
    /// One of [`KINDS`].
    pub kind: String,
    /// What identifies "the same failure" (hashed into the signature together with the kind).
    pub signature_basis: Value,
    pub title: String,
    /// One or two sentences a later reader (and the semantic index) can match.
    pub summary: String,
    /// Structured detail (query, routes, coverage; tool kind/id/version/code/message, …).
    pub subject: Value,
    pub root_cause_candidates: Vec<String>,
    /// Actions the follow-up must take (framework §18: root cause, repair, held-out test).
    pub required_actions: Vec<String>,
    /// The product operation that observed the failure (`memory query`, `rebuild-memory`, …).
    pub operation: String,
    /// `automatic` (detected by the product) or `reported` (declared by an agent).
    pub detection: String,
}

#[derive(Debug, Clone, serde::Serialize, PartialEq, Eq)]
pub struct FailureOutcome {
    /// `recorded` (a new record), `existing` (same signature already recorded) or `not_recorded`.
    pub status: String,
    pub id: Option<String>,
    pub path: Option<String>,
    pub kind: String,
    pub signature: String,
    pub reason: Option<String>,
}

impl FailureOutcome {
    pub fn to_value(&self) -> Value {
        serde_json::to_value(self).unwrap_or(Value::Null)
    }
}

pub fn signature(kind: &str, basis: &Value) -> String {
    sha256_hex(format!("{kind}\n{}", crate::util::hash_value(basis)).as_bytes())[..24].to_string()
}

fn failure_files(p: &Project) -> Vec<(String, Value)> {
    let mut out = vec![];
    for d in [FAILURE_DIR, MEMORY_QUALITY_DIR] {
        let Ok(rd) = std::fs::read_dir(p.root.join(d)) else {
            continue;
        };
        let mut names: Vec<String> = rd
            .filter_map(|e| e.ok())
            .map(|e| e.file_name().to_string_lossy().to_string())
            .filter(|n| n.ends_with(".yaml"))
            .collect();
        names.sort();
        for n in names {
            let rel = format!("{d}/{n}");
            if let Ok(t) = read_text(&p.root.join(&rel)) {
                if let Ok(v) = serde_yaml::from_str::<Value>(&t) {
                    out.push((rel, v));
                }
            }
        }
    }
    out.sort_by(|a, b| {
        a.1.get("id")
            .and_then(|x| x.as_str())
            .cmp(&b.1.get("id").and_then(|x| x.as_str()))
    });
    out
}

/// Existing failure records, oldest first: `(path, record data)`.
pub fn list(p: &Project) -> Vec<(String, Value)> {
    failure_files(p)
}

/// The record already holding this signature, if any.
pub fn find_by_signature(p: &Project, sig: &str) -> Option<(String, Value)> {
    failure_files(p)
        .into_iter()
        .find(|(_, v)| v.get("signature").and_then(|s| s.as_str()) == Some(sig))
}

fn next_id(existing: &[(String, Value)]) -> String {
    let ids: Vec<String> = existing
        .iter()
        .filter_map(|(_, v)| v.get("id").and_then(|x| x.as_str()).map(|s| s.to_string()))
        .collect();
    crate::util::next_id(ID_PREFIX, &ids, 4)
}

/// Remove machine-specific absolute paths and secret-pattern matches from free text before it is persisted in the
/// tracked tree (failure records are indexed and may be exported for review; they must be path-independent and
/// never carry a secret the scanner recognises).
fn sanitise(p: &Project, v: &Value) -> Value {
    let root = p.root.to_string_lossy().to_string();
    let scanner = p.secret_scanner();
    match v {
        Value::String(s) => {
            let mut t = if root.len() > 1 {
                s.replace(&format!("{root}/"), "")
                    .replace(&root, "<project-root>")
            } else {
                s.clone()
            };
            let hits = scanner.scan_text(&t, "failure-memory");
            if !hits.is_empty() {
                let mut ids: Vec<String> = hits.iter().map(|h| h.pattern_id.clone()).collect();
                ids.sort();
                ids.dedup();
                t = format!("[redacted: matched secret pattern(s) {}]", ids.join(","));
            }
            Value::String(t)
        }
        Value::Array(a) => Value::Array(a.iter().map(|x| sanitise(p, x)).collect()),
        Value::Object(o) => {
            Value::Object(o.iter().map(|(k, x)| (k.clone(), sanitise(p, x))).collect())
        }
        other => other.clone(),
    }
}

/// Record a failure durably (idempotent per signature). With `reindex`, a freshly written *indexed* record (not a
/// memory-quality event) is indexed right away when the index was fresh before the write, so recording a failure
/// never turns a fresh index stale and the record is recallable immediately; an already-stale index is left for
/// the next refresh.
pub fn record(p: &Project, ev: FailureEvent, reindex: bool) -> FailureOutcome {
    let sig = signature(&ev.kind, &ev.signature_basis);
    let mut outcome = FailureOutcome {
        status: "not_recorded".into(),
        id: None,
        path: None,
        kind: ev.kind.clone(),
        signature: sig.clone(),
        reason: None,
    };
    if !KINDS.contains(&ev.kind.as_str()) {
        outcome.reason = Some(format!("unknown failure kind '{}'", ev.kind));
        return outcome;
    }
    if !p.is_installed() {
        outcome.reason = Some("no Governance OS installation at this root".into());
        return outcome;
    }
    let existing = failure_files(p);
    if let Some((path, v)) = existing
        .iter()
        .find(|(_, v)| v.get("signature").and_then(|s| s.as_str()) == Some(sig.as_str()))
    {
        outcome.status = "existing".into();
        outcome.id = v.get("id").and_then(|x| x.as_str()).map(|s| s.to_string());
        outcome.path = Some(path.clone());
        return outcome;
    }
    // an OS observation is still a governed write: FREEZE_WRITES / PAUSE / recovery-only / kernel trust apply
    if let Err(e) = crate::orchestration::control::guard_write(p, "record failure memory") {
        outcome.reason = Some(format!("{}: {}", e.code, e.message));
        return outcome;
    }
    let dir = dir_for(&ev.kind);
    let was_fresh = reindex && dir == FAILURE_DIR && crate::memory::manifest::freshness(p).fresh;
    let id = next_id(&existing);
    let path = format!("{dir}/{id}.yaml");
    let data = json!({
        "id": id,
        "type": RECORD_TYPE,
        "title": sanitise(p, &json!(ev.title.chars().take(160).collect::<String>())),
        "status": "ACTIVE",
        "state_class": "EVIDENCE",
        "failure_kind": ev.kind,
        "signature": sig,
        "created": today(),
        "occurred_at": now_iso(),
        "summary": sanitise(p, &json!(ev.summary)),
        "detected_by": {"operation": ev.operation, "detection": ev.detection, "session": p.session_id, "role": p.role},
        "subject": sanitise(p, &ev.subject),
        "root_cause_candidates": ev.root_cause_candidates,
        "follow_up": {"status": "open", "required_actions": ev.required_actions, "task": Value::Null, "heldout_query": Value::Null},
    });
    let rec = Record {
        path: path.clone(),
        data,
        body: String::new(),
        format: RecordFormat::Yaml,
        problems: vec![],
    };
    if let Err(e) = crate::records::save_record(&p.root, &rec) {
        outcome.reason = Some(format!("{}: {}", e.code, e.message));
        return outcome;
    }
    outcome.status = "recorded".into();
    outcome.id = Some(id.clone());
    outcome.path = Some(path);
    let _ = crate::observability::emit(
        p,
        "failure_memory",
        json!({"id": id, "kind": ev.kind, "signature": sig, "operation": ev.operation}),
    );
    if was_fresh {
        let _ = crate::memory::indexer::rebuild(
            p,
            crate::memory::indexer::IndexOptions {
                incremental: true,
                record_failures: Some(false),
                ..Default::default()
            },
        );
    }
    outcome
}

/// Link a failure record to the governed work that follows it up (BC-P2-24 work generation; §18 repair and
/// held-out test). `task` and/or `heldout_query` are set; the follow-up becomes `linked`.
pub fn link_follow_up(
    p: &Project,
    failure_id: &str,
    task: Option<&str>,
    heldout_query: Option<&str>,
) -> Result<Value> {
    crate::orchestration::control::guard_write(p, "link failure follow-up")?;
    let (path, mut v) = failure_files(p)
        .into_iter()
        .find(|(_, v)| v.get("id").and_then(|x| x.as_str()) == Some(failure_id))
        .ok_or_else(|| {
            crate::GovError::new(
                "NOT_FOUND",
                format!("no failure record {failure_id} under {FAILURE_DIR}/ or {MEMORY_QUALITY_DIR}/"),
            )
            .with_details(json!({"remediation": "failure producers create failure records; list them under spec/reports/failures/ and spec/reports/memory-quality/"}))
        })?;
    if let Some(t) = task {
        v["follow_up"]["task"] = json!(t);
    }
    if let Some(h) = heldout_query {
        v["follow_up"]["heldout_query"] = json!(h);
    }
    v["follow_up"]["status"] = json!("linked");
    v["updated"] = json!(today());
    let rec = Record {
        path: path.clone(),
        data: v.clone(),
        body: String::new(),
        format: RecordFormat::Yaml,
        problems: vec![],
    };
    crate::records::save_record(&p.root, &rec)?;
    Ok(json!({"id": failure_id, "path": path, "follow_up": v["follow_up"]}))
}

/// Failure records whose follow-up has not been linked to governed work yet (input to BC-P2-24 work generation).
pub fn open_failures(p: &Project) -> Vec<Value> {
    failure_files(p)
        .into_iter()
        .filter(|(_, v)| {
            v.get("status").and_then(|s| s.as_str()) == Some("ACTIVE")
                && v.pointer("/follow_up/status").and_then(|s| s.as_str()) == Some("open")
        })
        .map(|(path, v)| json!({"id": v["id"], "path": path, "failure_kind": v["failure_kind"], "title": v["title"], "required_actions": v.pointer("/follow_up/required_actions")}))
        .collect()
}

/// A tool failure (framework §11.8): a code-intelligence adapter, embedder, reranker or registered tool that failed
/// or was unavailable while the product needed it.
#[derive(Debug, Clone)]
pub struct ToolFailure {
    /// `code_intel`, `embed`, `rerank`, `tool` (registered tool health) …
    pub tool_kind: String,
    pub tool_id: String,
    pub version: String,
    /// The typed error code the product observed (`PLUGIN_FAILED`, `EMBEDDER_BAD_OUTPUT`, …).
    pub code: String,
    pub message: String,
    pub operation: String,
    /// Paths or items affected (first few), for the reader.
    pub affected: Vec<String>,
}

pub fn tool_failure_event(t: &ToolFailure) -> FailureEvent {
    FailureEvent {
        kind: "tool-failure".into(),
        signature_basis: json!({"tool_kind": t.tool_kind, "tool_id": t.tool_id, "version": t.version, "code": t.code}),
        title: format!("Tool failure: {} {} ({})", t.tool_kind, t.tool_id, t.code),
        summary: format!(
            "The {} tool '{}' (version {}) failed with {} during `{}`: {}",
            t.tool_kind,
            t.tool_id,
            t.version,
            t.code,
            t.operation,
            t.message.chars().take(300).collect::<String>()
        ),
        subject: json!({"tool_kind": t.tool_kind, "tool_id": t.tool_id, "version": t.version, "code": t.code,
            "message": t.message.chars().take(600).collect::<String>(), "affected": t.affected.iter().take(10).collect::<Vec<_>>()}),
        root_cause_candidates: vec![
            "tool implementation or runtime missing/broken".into(),
            "tool configuration or pin mismatch".into(),
        ],
        required_actions: vec![
            "diagnose the tool failure (gov capabilities plugins / gov tools health)".into(),
            "repair or replace the tool, or record an accepted degradation".into(),
        ],
        operation: t.operation.clone(),
        detection: "automatic".into(),
    }
}

/// Record a tool failure (idempotent per tool kind/id/version/error code), unless
/// `MEMORY_POLICY.failure_memory.tool_failures` is false.
pub fn record_tool_failure(p: &Project, t: &ToolFailure, reindex: bool) -> FailureOutcome {
    let ev = tool_failure_event(t);
    if !p
        .policies()
        .get_bool("MEMORY_POLICY", "failure_memory.tool_failures", true)
    {
        return FailureOutcome {
            status: "not_recorded".into(),
            id: None,
            path: None,
            kind: ev.kind.clone(),
            signature: signature(&ev.kind, &ev.signature_basis),
            reason: Some("MEMORY_POLICY.failure_memory.tool_failures is false".into()),
        };
    }
    record(p, ev, reindex)
}

/// A retrieval miss declared or detected for a query (framework §18). `expected_refs` are the artefacts that
/// should have been returned when known (an agent-reported or held-out miss); `detail` carries the measurements.
pub fn retrieval_miss_event(
    query: &str,
    expected_refs: &[String],
    detail: Value,
    root_causes: Vec<String>,
    operation: &str,
    detection: &str,
) -> FailureEvent {
    let normalised: String = query
        .to_lowercase()
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ");
    let mut subject = json!({"query": query, "expected_refs": expected_refs});
    if let (Some(s), Some(d)) = (subject.as_object_mut(), detail.as_object()) {
        for (k, v) in d {
            s.insert(k.clone(), v.clone());
        }
    }
    FailureEvent {
        kind: "retrieval-miss".into(),
        signature_basis: json!({"query": normalised, "expected": expected_refs}),
        title: format!(
            "Retrieval miss: {}",
            query.chars().take(120).collect::<String>()
        ),
        summary: format!(
            "Memory-quality event: the query \"{}\" was not answered by the knowledge fabric ({}).",
            query.chars().take(200).collect::<String>(),
            if expected_refs.is_empty() {
                "no returned evidence covered the question".to_string()
            } else {
                format!("expected {}", expected_refs.join(", "))
            }
        ),
        subject,
        root_cause_candidates: root_causes,
        required_actions: vec![
            "root-cause the miss: chunking / metadata / routing / graph / lexical / stale index / knowledge gap".into(),
            "repair the cause or record the knowledge gap".into(),
            "add a held-out retrieval query for it (governance/tests/memory/heldout.yaml)".into(),
        ],
        operation: operation.into(),
        detection: detection.into(),
    }
}

/// Record one retrieval-miss failure per failed query of a held-out regression result (`retrieval::run_heldout`
/// output), for producers that persist regression results (audit, adoption A10). Returns the outcomes.
pub fn record_heldout_misses(
    p: &Project,
    regression: &Value,
    operation: &str,
) -> Vec<FailureOutcome> {
    let mut out = vec![];
    for r in regression
        .get("results")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default()
    {
        if r.get("pass").and_then(|v| v.as_bool()).unwrap_or(true) {
            continue;
        }
        let expected: Vec<String> = r
            .get("expected")
            .and_then(|v| v.as_array())
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default();
        let ev = retrieval_miss_event(
            r.get("query").and_then(|v| v.as_str()).unwrap_or(""),
            &expected,
            json!({"heldout_id": r.get("id"), "got": r.get("got"), "recall": r.get("recall"), "routes": r.get("routes"), "forbidden_hits": r.get("forbidden_hits")}),
            vec!["regression against a held-out expectation".into()],
            operation,
            "automatic",
        );
        out.push(record(p, ev, false));
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn failure_kinds_signatures_and_locations() {
        let a = retrieval_miss_event(
            "Blue-green  ROLLBACK procedure",
            &[],
            json!({}),
            vec![],
            "memory query",
            "automatic",
        );
        let b = retrieval_miss_event(
            "blue-green rollback   procedure",
            &[],
            json!({"k": 5}),
            vec![],
            "memory query",
            "automatic",
        );
        assert_eq!(a.kind, "retrieval-miss");
        assert_eq!(
            signature(&a.kind, &a.signature_basis),
            signature(&b.kind, &b.signature_basis),
            "the same question (case/spacing aside) is one memory-quality event"
        );
        let t = tool_failure_event(&ToolFailure {
            tool_kind: "code_intel".into(),
            tool_id: "python-ast".into(),
            version: "1.0.0".into(),
            code: "PLUGIN_BAD_RESPONSE".into(),
            message: "exit 3".into(),
            operation: "rebuild-memory".into(),
            affected: vec!["src/a.py".into()],
        });
        assert_eq!(t.kind, "tool-failure");
        assert_ne!(
            signature(&t.kind, &t.signature_basis),
            signature(&a.kind, &a.signature_basis)
        );
        assert!(KINDS.contains(&a.kind.as_str()) && KINDS.contains(&t.kind.as_str()));
        assert_eq!(dir_for(&a.kind), MEMORY_QUALITY_DIR);
        assert_eq!(dir_for(&t.kind), FAILURE_DIR);
        assert!(is_memory_quality_path(
            "spec/reports/memory-quality/FAIL-0001.yaml"
        ));
        assert!(!is_memory_quality_path(
            "spec/reports/failures/FAIL-0002.yaml"
        ));
        assert!(t.required_actions.iter().any(|x| x.contains("repair")));
        assert!(a.required_actions.iter().any(|x| x.contains("held-out")));
    }
}
