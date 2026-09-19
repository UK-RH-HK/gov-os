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
//! **Why a sealed block as well as a whole-record seal.** Other OS operations legitimately write a CIT record they do
//! not own: `gates::answer` records the decision id and marks a declined transaction `REJECTED`, `gates::revoke`
//! returns an approved transaction to `SIMULATED` and removes its approval. Those writes only *reduce* authority. The
//! sealed block keeps the OS facts an approval or execution relies on verifiable across them; the top-level status is
//! honoured only in the restrictive direction (execution needs *both* the top-level status and the sealed status to
//! be `APPROVED`).
//!
//! ## The whole record is sealed too (repair iteration 1, round 3; WS-5 IP-R3-2, integration O-7)
//!
//! Consumers outside `gov cit` read more of a CIT record than the block binds: task close and recorded authorship
//! (WS-5) honour a `COMMITTED` transaction's `execution.propagation.touched` list, and the governance suite reads its
//! status and approval. So [`seal`] also T2-seals the **whole record** (`t2::seal_record`), as the last step of every
//! CIT operation, after that operation has verified or re-derived everything the record asserts (the block's
//! digests; the gate, decision and approval against it). A hand edit of any field breaks the whole-record seal, and
//! no CIT operation blesses it: `approve` and `execute` refuse an edit to anything the block binds before they seal,
//! and a `COMMITTED` record is never re-sealed by a CIT operation except by rolling it back. Another OS writer of a
//! CIT record re-seals it only when its seal verified before the write ([`reseal_if_verified`]; the gate writers in
//! `gates.rs` are an integration point for WS-3, recorded in the round-3 WS-4 report), which is what lets
//! `t2::SEALED_RECORD_TYPES` name `cit`: an unsealed or broken CIT record then governs nothing.
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
    /// The transaction was flagged at proposal because its proposal/manifest carried secret material (redacted):
    /// it can never execute. Bound here so removing the top-level `secret_flagged` by hand does not release it.
    pub secret_flagged: bool,
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
            secret_flagged: v
                .get("secret_flagged")
                .and_then(|x| x.as_bool())
                .unwrap_or(false),
        }
    }
    fn to_value(&self) -> Value {
        let mut v = json!({
            "cit": self.cit, "cit_status": self.cit_status, "op": self.op, "at": self.at,
            "content_sha256": self.content_sha256, "impact_sha256": self.impact_sha256,
            "binding_sha256": self.binding_sha256, "human_gate": self.human_gate,
            "approval_sha256": self.approval_sha256, "decision": self.decision, "writes_sha256": self.writes_sha256,
        });
        // only when set, so the digest of every block sealed before the field existed is unchanged
        if self.secret_flagged {
            v["secret_flagged"] = json!(true);
        }
        v
    }
    /// The state carried over to the next operation's seal: everything the previous operation bound, with the new
    /// status (the caller overrides what the operation re-derives).
    pub fn carried(&self, cit_status: &str) -> CitState {
        CitState {
            cit_status: cit_status.to_string(),
            op: String::new(),
            at: String::new(),
            ..self.clone()
        }
    }
}

/// Seal `state` into the CIT record as written by the OS operation `op`, then T2-seal the whole record (call
/// immediately before `save_record`, after every other field of the record has been set).
pub fn seal(rec: &mut Record, mut state: CitState, op: &str) -> Result<()> {
    state.cit = rec.id();
    state.op = op.to_string();
    state.at = now_iso();
    let mut v = state.to_value();
    t2::seal_value(&mut v, "", op)?;
    rec.set(STATE_FIELD, v);
    t2::seal_record(rec, op)
}

// ------------------------------------------------------------------------------------ the OS re-seal rule (O-7)

/// Record types whose sealed content only their own operation establishes: a gate (its presentation and answer), a
/// transaction (its state), a close report (the evidence a close accepted and the authorship it records), research
/// and experiment lifecycle records and datasets (the lifecycle facts, WS-10), and health, product-test and
/// retrieval-regression evidence (`audit`). A **content** rewrite of one of these by another OS operation (a CIT
/// `set_field`, for example) is not an operation entitled to that content ([`content_write_entitled`]), so it is
/// never re-sealed: the record stays unhonoured and the write is recorded where it happened (the CIT's touched
/// list). Bookkeeping markers (staleness, retest and revalidation marks, journals) are re-sealed on every type.
pub const OPERATION_OWNED_TYPES: &[&str] = &[
    "human-gate",
    "cit",
    "report",
    "research",
    "experiment",
    "data",
    "audit",
];

/// Fields of a decision that record how it was derived — from which gate, with which answer, approved by whom and
/// whether a human approved it. They are established by the operation that minted the decision (a gate answer, an
/// automatic CIT approval, a retrieval-profile selection); a CIT rewriting one of them is not re-sealed, so a
/// governed change cannot launder an approval (`gates::verified_decision` then refuses the decision).
pub const DECISION_DERIVATION_FIELDS: &[&str] = &[
    "chosen_option",
    "human_approved",
    "derived_from",
    "approved_by",
    "approved_by_kind",
    "approved_by_role",
    "approved_at",
    "cit",
    "binding_sha256",
    "subject_sha256",
    "approval",
    "retrieval_profile",
    crate::t2::SEAL_FIELD,
    STATE_FIELD,
];

/// Fields of a task record its lifecycle operations establish — a claim, a close, a status transition, the
/// planner's provenance (WS-5). A governed change may revise the task's contract (objective, inputs, scope), and that
/// is re-sealed; a CIT writing one of these is not, so a transaction cannot pass for a close or a claim.
pub const TASK_OPERATION_FIELDS: &[&str] = &[
    "task_status",
    "status_source",
    "closed_by_report",
    "closed_at",
    "outputs_produced",
    "claimed_by",
    "claim",
    "provenance",
    "revalidation",
    "retest_required",
    crate::t2::SEAL_FIELD,
];

/// Is a content write of `field` (`None`: a whole-record rewrite) into a record of type `rtype`, made by a governed
/// change (a CIT manifest op), one the OS may seal as its own? Not for [`OPERATION_OWNED_TYPES`], not for a
/// decision's [`DECISION_DERIVATION_FIELDS`] or a task's [`TASK_OPERATION_FIELDS`] (nor a whole-record rewrite of
/// either); yes otherwise.
pub fn content_write_entitled(rtype: &str, field: Option<&str>) -> bool {
    if OPERATION_OWNED_TYPES.contains(&rtype) {
        return false;
    }
    let protected: &[&str] = match rtype {
        "decision" => DECISION_DERIVATION_FIELDS,
        "task" => TASK_OPERATION_FIELDS,
        _ => return true,
    };
    match field {
        Some(f) => {
            let top = f.split('.').next().unwrap_or(f);
            !protected.contains(&top)
        }
        None => false,
    }
}

/// Does `rec` carry a T2 seal that verifies on this machine? Call it **before** modifying the record, and pass the
/// answer to [`reseal_if_verified`] after.
pub fn verified_before(rec: &Record) -> bool {
    t2::verify_record(rec).is_verified()
}

/// The pure decision behind [`reseal_if_verified`].
pub fn should_reseal(was_verified: bool, entitled: bool) -> bool {
    was_verified && entitled
}

/// **The OS re-seal rule** for a write into an existing record (integration O-7; `bcf0139` generalised): a record
/// whose seal verified before the OS wrote into it (`was_verified`, from [`verified_before`]) is re-sealed as written
/// by `op`, so the OS's own write never makes OS state look tampered with; a record whose seal did not verify
/// (unsealed, edited by hand, foreign) is written but never sealed — the OS does not bless content it did not write,
/// and a hand edit still breaks the seal. `entitled` says whether the writing operation may establish what it wrote
/// in this record: bookkeeping markers and a record's own lifecycle operations are; a governed content rewrite of
/// operation-owned facts is not ([`content_write_entitled`]). Returns whether it sealed.
pub fn reseal_if_verified(
    rec: &mut Record,
    was_verified: bool,
    entitled: bool,
    op: &str,
) -> Result<bool> {
    if !should_reseal(was_verified, entitled) {
        return Ok(false);
    }
    t2::seal_record(rec, op)?;
    Ok(true)
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

/// One content-bound CIT write of a path: the committed transaction that wrote it and the SHA-256 it left.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CoveringWrite {
    pub cit: String,
    pub sha256: Option<String>,
}

/// **CIT coverage bound to content** (IP-R3-6; Contract v3:614 "a CIT governing that specific change"): for every
/// committed transaction that `include` admits (the caller's claim window), the paths its execution wrote with the
/// content each write left — honoured only through [`verified_writes`] (sealed `COMMITTED` state, writes digest
/// intact) and only for a record whose whole-record T2 seal verifies (a hand-edited CIT record covers nothing).
/// Task close accepts an out-of-scope path only when [`covers`] finds its current content among them.
pub fn writes_by_path(
    store: &crate::records::RecordStore,
    include: impl Fn(&Record) -> bool,
) -> std::collections::BTreeMap<String, Vec<CoveringWrite>> {
    let mut out: std::collections::BTreeMap<String, Vec<CoveringWrite>> = Default::default();
    for c in store.of_type("cit") {
        if !include(c) || !verified_before(c) {
            continue;
        }
        let Ok(writes) = verified_writes(c) else {
            continue;
        };
        for w in writes {
            out.entry(w.path.clone()).or_default().push(CoveringWrite {
                cit: c.id(),
                sha256: w.sha256.clone(),
            });
        }
    }
    out
}

/// Does a committed CIT write in `by_path` ([`writes_by_path`]) account for `path` holding `current` (its SHA-256
/// now; `None` = deleted)? Returns the covering transaction.
pub fn covers(
    by_path: &std::collections::BTreeMap<String, Vec<CoveringWrite>>,
    path: &str,
    current: Option<&str>,
) -> Option<String> {
    by_path.get(path).and_then(|v| {
        v.iter()
            .find(|w| w.sha256.as_deref() == current)
            .map(|w| w.cit.clone())
    })
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

    #[test]
    fn the_os_reseals_only_what_it_verified_and_is_entitled_to_write() {
        // a hand-edited (or never sealed) record is never sealed by an OS write, whatever the write
        assert!(!should_reseal(false, true));
        assert!(should_reseal(true, true));
        assert!(!should_reseal(true, false));
        // governed content rewrites: specification and task records yes, operation-owned facts no
        for t in ["requirement", "task", "checkpoint", "handoff", "scenario"] {
            assert!(content_write_entitled(t, Some("statement")), "{t}");
        }
        for t in OPERATION_OWNED_TYPES {
            assert!(!content_write_entitled(t, Some("title")), "{t}");
        }
        // a decision's lifecycle and wording may be revised through change control; how it was derived may not
        assert!(content_write_entitled("decision", Some("status")));
        assert!(content_write_entitled("decision", Some("rationale")));
        for f in [
            "chosen_option",
            "human_approved",
            "derived_from",
            "approval.gate",
        ] {
            assert!(!content_write_entitled("decision", Some(f)), "{f}");
        }
        assert!(!content_write_entitled("decision", None));
        // a task's contract may be revised through change control; its claim, close and status may not
        assert!(content_write_entitled("task", Some("objective")));
        assert!(content_write_entitled("task", Some("allowed_paths")));
        for f in ["task_status", "closed_by_report", "outputs_produced"] {
            assert!(!content_write_entitled("task", Some(f)), "{f}");
        }
        assert!(!content_write_entitled("task", None));
    }

    #[test]
    fn a_secret_flag_is_bound_into_the_block_only_when_set() {
        let plain = CitState {
            cit: "CIT-0001".into(),
            cit_status: "PROPOSED".into(),
            content_sha256: "c".into(),
            ..Default::default()
        };
        assert!(plain.to_value().get("secret_flagged").is_none());
        let flagged = CitState {
            secret_flagged: true,
            ..plain.clone()
        };
        assert_eq!(flagged.to_value()["secret_flagged"], true);
        assert!(CitState::from_value(&flagged.to_value()).secret_flagged);
        let next = flagged.carried("SIMULATED");
        assert!(next.secret_flagged && next.cit_status == "SIMULATED");
    }

    #[test]
    fn coverage_is_bound_to_the_content_a_committed_cit_wrote() {
        let mut m: std::collections::BTreeMap<String, Vec<CoveringWrite>> = Default::default();
        m.insert(
            "spec/tasks/TST-0001.yaml".into(),
            vec![CoveringWrite {
                cit: "CIT-0002".into(),
                sha256: Some("aa".into()),
            }],
        );
        m.insert(
            "src/gone.rs".into(),
            vec![CoveringWrite {
                cit: "CIT-0003".into(),
                sha256: None,
            }],
        );
        assert_eq!(
            covers(&m, "spec/tasks/TST-0001.yaml", Some("aa")).as_deref(),
            Some("CIT-0002")
        );
        assert_eq!(
            covers(&m, "spec/tasks/TST-0001.yaml", Some("bb")),
            None,
            "the path changed again after the CIT wrote it"
        );
        assert_eq!(covers(&m, "src/gone.rs", None).as_deref(), Some("CIT-0003"));
        assert_eq!(covers(&m, "src/other.rs", Some("aa")), None);
    }
}
