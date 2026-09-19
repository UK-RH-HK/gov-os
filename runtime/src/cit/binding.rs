//! **CIT state binding** (BC-P2-09 CIT state, BC-P2-11 CIT side; Contract v3:678 "Declined/revoked/stale/other-CIT
//! gates cannot authorise execution", framework §47.2 "decision finalised → mutation manifest → …").
//!
//! A Change-Impact Transaction is T2 state (D-0007): its status, the impact the OS simulated, the approval derived
//! from a gate answer and what its execution wrote are facts only a `gov cit` operation may establish. The CIT record
//! is a plain repository file, so this module binds those facts the same way the T2 primitive binds gates
//! ([`crate::t2`]): every `gov cit` operation that changes CIT state writes an **`os_state`** block into the record
//! and seals it with the machine binding key ([`crate::t2::seal_value`]). The block carries digests, not copies:
//!
//! | field | what it binds |
//! |---|---|
//! | `content_sha256` | the transaction content: id, proposal, declared trigger, targets, mutation manifest ([`content_digest`]) |
//! | `impact_sha256` | the simulated impact the approval answered: radius, gate requirement, seeds, affected nodes, affected tasks, tests, features, material classes ([`impact_digest`]) |
//! | `binding_sha256` | `sha256(cit ‖ content ‖ impact)` — what a Human Decision Gate raised for this CIT carries as `subject.sha256`, so the owner signs exactly this transaction and impact ([`binding_digest`]) |
//! | `approval_sha256` | the approval record the OS derived from the verified gate answer (or the automatic path) |
//! | `writes_sha256` | per-path SHA-256 of every file the execution wrote (IP-3 of WS-5: in-window CIT coverage binds content) |
//! | `cit_status`, `human_gate`, `decision`, `op`, `at` | the state the operation left |
//!
//! Consumers never trust the record's top-level fields for an authority decision: approve and execute recompute the
//! digests from the record as it stands and compare them with the sealed block ([`verified_state`]); a hand-edited
//! manifest, impact, approval, gate reference or status is therefore refused, typed, at approve and at execute.
//!
//! **Why a sealed block rather than a whole-record seal.** Other OS operations legitimately write a CIT record they do
//! not own: `gates::answer` records the decision id and marks a declined transaction `REJECTED`, `gates::revoke`
//! returns an approved transaction to `SIMULATED` and removes its approval. Those writes only *reduce* authority, and
//! they do not re-seal the record, so a whole-record seal would turn every answered or revoked CIT into an unbound
//! record. The sealed block keeps the OS facts verifiable across those writes; the top-level status is honoured only
//! in the restrictive direction (execution needs *both* the top-level status and the sealed status to be `APPROVED`).
use crate::records::Record;
use crate::t2::{self, Binding};
use crate::util::{canonical_json, now_iso, sha256_hex};
use crate::{GovError, Result};
use serde_json::{json, Value};

/// The record field that carries the sealed CIT state.
pub const STATE_FIELD: &str = "os_state";

/// Values as the product's YAML writer stores them and reads them back, so a digest computed before `save_record`
/// equals the digest computed from the loaded record (the same normalisation the T2 seal applies).
fn normalised(v: &Value) -> Value {
    crate::util::to_yaml(v)
        .ok()
        .and_then(|t| serde_yaml::from_str::<Value>(&t).ok())
        .unwrap_or_else(|| v.clone())
}

fn digest(v: &Value) -> String {
    sha256_hex(canonical_json(&normalised(v)).as_bytes())
}

/// The transaction content an approval binds (Contract v3:678, framework §47.2): identity, proposal, the proposer's
/// declared trigger, targets and the mutation manifest.
pub fn content_of(cit: &Value) -> Value {
    json!({
        "cit": cit.get("id").cloned().unwrap_or(Value::Null),
        "proposal": cit.get("proposal").cloned().unwrap_or(Value::Null),
        "trigger": cit.get("trigger").cloned().unwrap_or(Value::Null),
        "targets": cit.get("targets").cloned().unwrap_or(json!([])),
        "mutation_manifest": cit.get("mutation_manifest").cloned().unwrap_or(json!([])),
    })
}

pub fn content_digest(cit: &Value) -> String {
    digest(&content_of(cit))
}

/// The simulated impact an approval binds: everything that decides who must approve and what the change reaches.
/// Timestamps, index snapshot references, semantic candidates and prose consequences are left out: they describe the
/// simulation run, not the impact.
pub fn impact_of(impact: &Value) -> Value {
    let affected: Vec<Value> = impact["affected"]
        .as_array()
        .map(|a| {
            a.iter()
                .map(|x| json!({"node": x["node"], "hop": x["hop"]}))
                .collect()
        })
        .unwrap_or_default();
    json!({
        "radius": impact.get("radius").cloned().unwrap_or(Value::Null),
        "human_gate_required": impact.get("human_gate_required").cloned().unwrap_or(Value::Null),
        "seeds": impact.get("seeds").cloned().unwrap_or(json!([])),
        "affected": affected,
        "affected_tasks": impact.get("affected_tasks").cloned().unwrap_or(json!([])),
        "tests_required": impact.get("tests_required").cloned().unwrap_or(json!([])),
        "features": impact.get("features").cloned().unwrap_or(json!([])),
        "material_classes": impact.get("material_classes").cloned().unwrap_or(json!([])),
        "effective_triggers": impact.get("effective_triggers").cloned().unwrap_or(json!([])),
    })
}

pub fn impact_digest(impact: &Value) -> String {
    digest(&impact_of(impact))
}

/// What a gate raised for CIT `cit` carries as `subject.sha256`: the transaction and the impact the human answers.
pub fn binding_digest(cit: &str, content_sha256: &str, impact_sha256: &str) -> String {
    sha256_hex(
        canonical_json(
            &json!({"cit": cit, "content_sha256": content_sha256, "impact_sha256": impact_sha256}),
        )
        .as_bytes(),
    )
}

pub fn approval_digest(approval: &Value) -> String {
    digest(approval)
}

pub fn writes_digest(writes: &Value) -> String {
    digest(writes)
}

/// The sealed CIT state as the OS last wrote it.
#[derive(Debug, Clone, Default)]
pub struct CitState {
    pub cit: String,
    pub cit_status: String,
    pub op: String,
    pub at: String,
    pub content_sha256: String,
    pub impact_sha256: Option<String>,
    pub binding_sha256: Option<String>,
    pub human_gate: Option<String>,
    pub approval_sha256: Option<String>,
    pub decision: Option<String>,
    pub writes_sha256: Option<String>,
}

fn opt(v: &Value, k: &str) -> Option<String> {
    v.get(k)
        .and_then(|x| x.as_str())
        .filter(|s| !s.is_empty())
        .map(String::from)
}

impl CitState {
    fn from_value(v: &Value) -> Self {
        CitState {
            cit: opt(v, "cit").unwrap_or_default(),
            cit_status: opt(v, "cit_status").unwrap_or_default(),
            op: opt(v, "op").unwrap_or_default(),
            at: opt(v, "at").unwrap_or_default(),
            content_sha256: opt(v, "content_sha256").unwrap_or_default(),
            impact_sha256: opt(v, "impact_sha256"),
            binding_sha256: opt(v, "binding_sha256"),
            human_gate: opt(v, "human_gate"),
            approval_sha256: opt(v, "approval_sha256"),
            decision: opt(v, "decision"),
            writes_sha256: opt(v, "writes_sha256"),
        }
    }
    fn to_value(&self) -> Value {
        json!({
            "cit": self.cit, "cit_status": self.cit_status, "op": self.op, "at": self.at,
            "content_sha256": self.content_sha256, "impact_sha256": self.impact_sha256,
            "binding_sha256": self.binding_sha256, "human_gate": self.human_gate,
            "approval_sha256": self.approval_sha256, "decision": self.decision, "writes_sha256": self.writes_sha256,
        })
    }
}

/// Seal `state` into the CIT record as written by the OS operation `op` (call immediately before `save_record`).
pub fn seal(rec: &mut Record, mut state: CitState, op: &str) -> Result<()> {
    state.cit = rec.id();
    state.op = op.to_string();
    state.at = now_iso();
    let mut v = state.to_value();
    t2::seal_value(&mut v, "", op)?;
    rec.set(STATE_FIELD, v);
    Ok(())
}

/// The sealed state of a CIT record, or the typed refusal: `T2_UNBOUND` when the block is absent, not sealed by this
/// machine or modified since, `CIT_STATE_MISMATCH` when a sealed block of another transaction was copied in.
pub fn verified_state(rec: &Record) -> Result<CitState> {
    let v = rec.data.get(STATE_FIELD).cloned().unwrap_or(Value::Null);
    let b = if v.is_object() {
        t2::verify_value(&v, "")
    } else {
        Binding::Unsealed
    };
    if !b.is_verified() {
        return Err(t2::unbound(
            &rec.id(),
            &rec.path,
            "Change-Impact Transaction state (status, simulated impact, approval, execution)",
            &b,
        )
        .with_details(json!({"record": rec.id(), "path": rec.path, "t2": b.to_value(), "field": STATE_FIELD,
            "remediation": "a CIT's state is established only by `gov cit propose|simulate|approve|execute`; re-propose the change through gov (a record written or edited outside gov is a request, not a transaction)"})));
    }
    let st = CitState::from_value(&v);
    if st.cit != rec.id() {
        return Err(GovError::new(
            "CIT_STATE_MISMATCH",
            format!(
                "{} carries the sealed state of {}: a transaction's state cannot be copied into another record",
                rec.id(),
                st.cit
            ),
        ));
    }
    Ok(st)
}

/// Whether the record's sealed state verifies (for reporting; consumers use [`verified_state`]).
pub fn binding_of(rec: &Record) -> Value {
    match verified_state(rec) {
        Ok(s) => json!({"binding": "VERIFIED", "cit_status": s.cit_status, "op": s.op, "at": s.at}),
        Err(e) => json!({"binding": "UNBOUND", "code": e.code, "message": e.message}),
    }
}

/// One file a CIT execution wrote, with the content it left (`sha256: None` = the execution deleted it).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PathWrite {
    pub path: String,
    pub sha256: Option<String>,
}

impl PathWrite {
    pub fn to_value(&self) -> Value {
        json!({"path": self.path, "sha256": self.sha256})
    }
}

/// The per-path content an execution left, for `touched` paths under `root`.
pub fn capture_writes(root: &std::path::Path, touched: &[String]) -> Vec<PathWrite> {
    let mut paths: Vec<String> = touched.iter().filter(|t| !t.is_empty()).cloned().collect();
    paths.sort();
    paths.dedup();
    paths
        .into_iter()
        .map(|p| {
            let abs = root.join(&p);
            let sha = if abs.is_file() {
                crate::util::read_bytes(&abs).ok().map(|b| sha256_hex(&b))
            } else {
                None
            };
            PathWrite {
                path: p,
                sha256: sha,
            }
        })
        .collect()
}

/// **What a committed CIT wrote, verified** (integration point IP-3 for WS-5's task-close scope check): the per-path
/// content hashes recorded in `execution.writes`, honoured only when the record's sealed state is `COMMITTED` and its
/// `writes_sha256` matches. A CIT covers an out-of-scope path for a task only when the path's current content hash
/// equals the hash the CIT wrote (the change the CIT governed), not merely because the path was in its window.
pub fn verified_writes(rec: &Record) -> Result<Vec<PathWrite>> {
    let st = verified_state(rec)?;
    if st.cit_status != "COMMITTED" {
        return Err(GovError::new(
            "CIT_NOT_COMMITTED",
            format!(
                "{} is {} (sealed state); only a committed transaction governs what it wrote",
                rec.id(),
                st.cit_status
            ),
        ));
    }
    let writes = rec.data["execution"]["writes"].clone();
    if st.writes_sha256.as_deref() != Some(writes_digest(&writes).as_str()) {
        return Err(GovError::new(
            "CIT_STATE_MISMATCH",
            format!(
                "{}: the recorded execution writes are not the ones the execution sealed",
                rec.id()
            ),
        ));
    }
    Ok(writes
        .as_array()
        .map(|a| {
            a.iter()
                .map(|w| PathWrite {
                    path: w["path"].as_str().unwrap_or("").to_string(),
                    sha256: w["sha256"].as_str().map(String::from),
                })
                .collect()
        })
        .unwrap_or_default())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn digests_are_stable_across_the_record_writer_and_sensitive_to_content() {
        let cit = json!({"id": "CIT-0001", "proposal": "p", "trigger": "editorial", "targets": ["REQ-0001"],
            "mutation_manifest": [{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "1.0"}]});
        let a = content_digest(&cit);
        let round: Value = serde_yaml::from_str(&crate::util::to_yaml(&cit).unwrap()).unwrap();
        assert_eq!(a, content_digest(&round));
        let mut changed = cit.clone();
        changed["mutation_manifest"]
            .as_array_mut()
            .unwrap()
            .push(json!({"op": "write_file", "path": "governance/project/x.md", "content": "x"}));
        assert_ne!(a, content_digest(&changed));
        let imp = json!({"radius": "R2", "human_gate_required": true, "seeds": ["REQ-0001"], "affected": [{"node": "TASK-0001", "hop": 1, "via": "x"}], "simulated_at": "t1"});
        let mut later = imp.clone();
        later["simulated_at"] = json!("t2");
        assert_eq!(
            impact_digest(&imp),
            impact_digest(&later),
            "run metadata is not impact"
        );
        later["radius"] = json!("R5");
        assert_ne!(impact_digest(&imp), impact_digest(&later));
        assert_ne!(
            binding_digest("CIT-0001", &a, &impact_digest(&imp)),
            binding_digest("CIT-0002", &a, &impact_digest(&imp)),
            "the binding names the transaction"
        );
    }
}
