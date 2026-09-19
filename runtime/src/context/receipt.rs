//! **Consumption receipt and implementation traceability** (Contract v3 W5, lines 1114-1126; BC-P2-20 contract and
//! lineage side).
//!
//! The worker's structured return **is** the consumption receipt. One contract serves the handoff return, the task
//! close report and the persisted report record:
//!
//! | receipt field | W5 bullet | aliases accepted |
//! |---|---|---|
//! | `context_packet_hash` — the packet the worker was supplied | exact inputs supplied | `packet_hash` |
//! | `inputs_consumed` — `ID@<content_hash>` or `{id, content_hash}` for every required input | exact inputs consumed | `consumed_inputs` |
//! | `outputs_produced` — paths/ids | outputs produced | `files_changed` |
//! | `requirements_implemented`, `scenarios_implemented`, `features_implemented` | requirements/features/scenarios implemented | — |
//! | `decisions_applied`, `constraints_applied` (architecture/interface/decision ids) | decisions/architecture constraints applied | — |
//! | `acceptance_evidence` — `{test, result, evidence}` per declared acceptance test | tests/acceptance evidence produced | `tests_evidence` |
//! | `deviations`, `unresolved` — lists, empty when there are none | deviations/unknowns | `unknowns` for `unresolved` |
//!
//! The worker-return schema's `status` (`success|partial|failed|blocked`) is the report's `outcome`; the report
//! record's `status` is its lifecycle state. [`report_from_worker_return`] and [`worker_return_from_report`] are
//! the lossless mapping between the two shapes (S0-W5-01).
//!
//! [`validate`] checks a receipt against the task's resolved manifest ([`super::manifest`]) and the packet it names:
//! fabricated references, claims outside the manifest, unacknowledged or stale consumption, missing traceability
//! where it is required, and declared acceptance tests without evidence. The persisted receipt fields become
//! lineage edges (`records::RELATION_FIELDS`: report `IMPLEMENTS` requirement, `GOVERNED_BY` decision, `CONSUMES`
//! input, `VALIDATED_BY` test, `PRODUCES` output; task `PRODUCES` report), so code, tests and evidence are
//! followable back to the authoritative inputs in both directions (`graph::impact_set` / `graph::upstream_set`).
//!
//! **Integration point (WS-5, `orchestration::tasks::close`)**: map a worker return with
//! [`report_from_worker_return`], then `let report = require_valid(p, &store, id, &report)?;` before the report
//! record is minted, and persist `outputs_produced` on the task record (the task → code edge).
use super::manifest::{self, Manifest, Slot};
use crate::records::RecordStore;
use crate::{GovError, Project, Result};
use serde_json::{json, Map, Value};

/// Task classes whose completion must trace to the requirements/scenarios/decisions it realises. Any task whose
/// outputs include production source (repository contract class `source`) is held to the same rule.
pub const TRACEABILITY_REQUIRED_CLASSES: &[&str] = &[
    "implementation",
    "integration",
    "refactor",
    "repair",
    "performance",
];

/// The worker-return `status` vocabulary (framework §61), which is the report `outcome`.
pub const WORKER_STATUSES: &[&str] = &["success", "partial", "failed", "blocked"];

/// Report-record fields the OS adds at close; they are not part of the worker's return.
pub const OS_REPORT_FIELDS: &[&str] = &[
    "id",
    "type",
    "title",
    "status",
    "created",
    "updated",
    "session",
    "role",
    "state_class",
    "observed_files_changed",
    "mutation_evidence",
    "degraded",
    "receipt_validation",
    "outcome",
];

/// Test results that count as acceptance evidence.
pub const PASSING_RESULTS: &[&str] = &["passed", "not_applicable_with_reason"];

/// Lossless mapping: a worker return (worker-return schema) → the fields of a task-close report. The worker's
/// `status` becomes `outcome`; every other field is kept verbatim.
pub fn report_from_worker_return(ret: &Value) -> Value {
    let mut m = ret.as_object().cloned().unwrap_or_default();
    if let Some(s) = m
        .get("status")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string())
    {
        if WORKER_STATUSES.contains(&s.as_str()) {
            m.remove("status");
            m.entry("outcome".to_string()).or_insert(json!(s));
        }
    }
    Value::Object(m)
}

/// Lossless inverse of [`report_from_worker_return`]: a persisted report → the worker return it came from
/// (`outcome` → `status`; OS-added record fields dropped).
pub fn worker_return_from_report(report: &Value) -> Value {
    let mut m = report.as_object().cloned().unwrap_or_default();
    let outcome = m.get("outcome").cloned();
    for k in OS_REPORT_FIELDS {
        m.remove(*k);
    }
    if let Some(o) = outcome {
        m.insert("status".into(), o);
    }
    Value::Object(m)
}

fn list_of(m: &Map<String, Value>, keys: &[&str]) -> Option<Vec<Value>> {
    keys.iter().find_map(|k| m.get(*k)).map(|v| match v {
        Value::Array(a) => a.clone(),
        Value::Null => vec![],
        other => vec![other.clone()],
    })
}

fn ids_of(v: &[Value]) -> Vec<String> {
    v.iter()
        .filter_map(|x| crate::records::relation_target(x))
        .collect()
}

/// A consumed-input entry as `(id, hash-or-version)`.
fn consumed_entry(v: &Value) -> Option<(String, Option<String>)> {
    match v {
        Value::String(s) => {
            let mut it = s.splitn(2, '@');
            let id = it.next()?.trim().to_string();
            let h = it
                .next()
                .map(|x| x.trim().to_string())
                .filter(|x| !x.is_empty());
            (!id.is_empty()).then_some((id, h))
        }
        Value::Object(o) => {
            let id = o.get("id").and_then(|x| x.as_str())?.trim().to_string();
            let h = ["content_hash", "hash", "version"]
                .iter()
                .find_map(|k| o.get(*k).and_then(|x| x.as_str()))
                .map(|x| x.trim().to_string())
                .filter(|x| !x.is_empty());
            Some((id, h))
        }
        _ => None,
    }
}

/// The receipt contract a packet hands the worker: exactly what the return must contain for this task.
pub fn contract_for(p: &Project, store: &RecordStore, task_id: &str, m: &Manifest) -> Value {
    let class = store
        .get(task_id)
        .map(|t| t.get("class"))
        .unwrap_or_default();
    let trace = |s: Slot| -> Vec<String> {
        m.in_slot(s)
            .into_iter()
            .filter(|e| e.required && e.satisfied())
            .map(|e| e.id.clone())
            .collect()
    };
    let _ = p;
    json!({
        "required_fields": ["context_packet_hash", "inputs_consumed", "outputs_produced", "requirements_implemented", "scenarios_implemented", "decisions_applied", "acceptance_evidence", "deviations", "unresolved"],
        "acknowledge_inputs": m.required_satisfied().iter().map(|e| json!({"id": e.id, "content_hash": e.content_hash, "version": e.version})).collect::<Vec<_>>(),
        "trace": {"requirements": trace(Slot::Requirement), "scenarios": trace(Slot::Scenario), "features": trace(Slot::Feature), "decisions": trace(Slot::Decision), "constraints": trace(Slot::Architecture).into_iter().chain(trace(Slot::Interface)).collect::<Vec<_>>()},
        "tests_requiring_evidence": trace(Slot::TestDesign),
        "traceability_required": TRACEABILITY_REQUIRED_CLASSES.contains(&class.as_str()),
        "format": "inputs_consumed: ['ID@<content_hash>' | {id, content_hash}]; acceptance_evidence: [{test, result: passed|failed|not_applicable_with_reason, evidence}]; every trace id must be implemented/applied or named in a deviation",
    })
}

/// The outcome of validating one receipt.
#[derive(Clone, Debug)]
pub struct ReceiptCheck {
    pub task: String,
    pub errors: Vec<Value>,
    pub warnings: Vec<Value>,
    /// The receipt in canonical field names.
    pub receipt: Value,
    pub manifest_hash: String,
    pub packet_hash: Option<String>,
    pub traceability_required: bool,
}

impl ReceiptCheck {
    pub fn ok(&self) -> bool {
        self.errors.is_empty()
    }
    pub fn to_value(&self) -> Value {
        json!({"task": self.task, "ok": self.ok(), "errors": self.errors, "warnings": self.warnings,
               "manifest_hash": self.manifest_hash, "packet_hash": self.packet_hash,
               "traceability_required": self.traceability_required, "receipt": self.receipt})
    }
    /// What is persisted beside the receipt: the verdict and what it was checked against.
    pub fn summary(&self) -> Value {
        json!({"ok": self.ok(), "errors": self.errors.iter().map(|e| e["code"].clone()).collect::<Vec<_>>(),
               "error_count": self.errors.len(), "warning_count": self.warnings.len(),
               "manifest_hash": self.manifest_hash, "packet_hash": self.packet_hash,
               "traceability_required": self.traceability_required})
    }
}

fn err(code: &str, message: String, ids: Vec<String>) -> Value {
    json!({"code": code, "message": message, "ids": ids})
}

/// Validate `receipt` (a worker return or a close report, either shape) for task `task_id` against its manifest
/// and the packet it names.
pub fn validate(
    p: &Project,
    store: &RecordStore,
    task_id: &str,
    receipt: &Value,
) -> Result<ReceiptCheck> {
    let task = store
        .get(task_id)
        .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("task {task_id} not found")))?;
    let m = manifest::resolve(p, store, task);
    let r = report_from_worker_return(receipt);
    let o = r.as_object().cloned().unwrap_or_default();
    let mut errors: Vec<Value> = vec![];
    let mut warnings: Vec<Value> = vec![];

    // --- presence of the receipt fields (empty lists are an explicit "none")
    let packet_hash = ["context_packet_hash", "packet_hash"]
        .iter()
        .find_map(|k| o.get(*k).and_then(|v| v.as_str()))
        .map(|s| s.trim().to_string())
        .filter(|s| !s.is_empty());
    let consumed = list_of(&o, &["inputs_consumed", "consumed_inputs"]);
    let outputs = list_of(&o, &["outputs_produced", "files_changed"]);
    let deviations = list_of(&o, &["deviations"]);
    let unresolved = list_of(&o, &["unresolved", "unknowns"]);
    let req_impl = ids_of(&list_of(&o, &["requirements_implemented"]).unwrap_or_default());
    let scn_impl = ids_of(&list_of(&o, &["scenarios_implemented"]).unwrap_or_default());
    let feat_impl = ids_of(&list_of(&o, &["features_implemented"]).unwrap_or_default());
    let dec_applied = ids_of(&list_of(&o, &["decisions_applied"]).unwrap_or_default());
    let con_applied = ids_of(&list_of(&o, &["constraints_applied"]).unwrap_or_default());
    let evidence = list_of(&o, &["acceptance_evidence", "tests_evidence"]).unwrap_or_default();
    let mut missing_fields = vec![];
    for (name, present) in [
        ("context_packet_hash", packet_hash.is_some()),
        ("inputs_consumed", consumed.is_some()),
        ("outputs_produced (or files_changed)", outputs.is_some()),
        ("deviations", deviations.is_some()),
        ("unresolved (or unknowns)", unresolved.is_some()),
    ] {
        if !present {
            missing_fields.push(name.to_string());
        }
    }
    if !missing_fields.is_empty() {
        errors.push(err("RECEIPT_FIELDS_MISSING", format!("the consumption receipt lacks {}; every field is required (an empty list states 'none')", missing_fields.join(", ")), missing_fields));
    }

    // --- the manifest must still be satisfied: completion cannot rest on absent or superseded inputs
    if !m.satisfied() {
        errors.push(err(
            "MANIFEST_UNSATISFIED",
            format!("{task_id}: {}", m.blocking_reason().unwrap_or_default()),
            m.entries
                .iter()
                .filter(|e| e.required && !e.satisfied())
                .map(|e| e.id.clone())
                .collect(),
        ));
    }

    // --- the packet the worker was supplied
    let packet = packet_hash
        .as_ref()
        .and_then(|h| super::load_packet(p, task_id, Some(h)).ok());
    if let Some(h) = &packet_hash {
        match &packet {
            // packet history is machine-local runtime state: an unknown hash (e.g. compiled on another machine) is
            // reported, and consumption is then proven by the content hashes in inputs_consumed alone
            None => warnings.push(err("PACKET_UNKNOWN", format!("context_packet_hash {h} is not a packet compiled for {task_id} on this machine; consumption is checked against the content hashes in inputs_consumed only"), vec![h.clone()])),
            Some(pk) if pk["delivery_state"] == "BLOCKED" => errors.push(err("PACKET_BLOCKED", format!("packet {h} was compiled with mandatory inputs unsatisfied; work on a blocked packet cannot complete"), vec![h.clone()])),
            _ => {}
        }
    }
    let supplied = |id: &str| -> Option<String> {
        packet
            .as_ref()
            .and_then(|pk| pk["input_hashes"][id].as_str().map(|s| s.to_string()))
    };

    // --- every reference must exist and be of the right type (fabricated trace is refused)
    let mut unknown = vec![];
    let mut wrong = vec![];
    let check_ref = |id: &str,
                     types: &[&str],
                     unknown: &mut Vec<String>,
                     wrong: &mut Vec<String>| match store.get(id) {
        None => unknown.push(id.to_string()),
        Some(rec) if !types.is_empty() && !types.contains(&rec.rtype().as_str()) => wrong.push(
            format!("{id} is a {}, not {}", rec.rtype(), types.join("/")),
        ),
        _ => {}
    };
    for id in &req_impl {
        check_ref(id, &["requirement"], &mut unknown, &mut wrong);
    }
    for id in &scn_impl {
        check_ref(id, &["scenario"], &mut unknown, &mut wrong);
    }
    for id in &feat_impl {
        check_ref(id, &["feature"], &mut unknown, &mut wrong);
    }
    for id in &dec_applied {
        check_ref(id, &["decision"], &mut unknown, &mut wrong);
    }
    for id in &con_applied {
        check_ref(
            id,
            &["architecture", "interface", "decision"],
            &mut unknown,
            &mut wrong,
        );
    }
    let consumed_entries: Vec<(String, Option<String>)> = consumed
        .clone()
        .unwrap_or_default()
        .iter()
        .filter_map(consumed_entry)
        .collect();
    for (id, _) in &consumed_entries {
        check_ref(id, &[], &mut unknown, &mut wrong);
    }
    let mut evidence_by_test: std::collections::BTreeMap<String, Value> = Default::default();
    for e in &evidence {
        if let Some(t) = crate::records::relation_target(e) {
            check_ref(&t, &["test-obligation"], &mut unknown, &mut wrong);
            evidence_by_test.insert(t, e.clone());
        }
    }
    if !unknown.is_empty() {
        unknown.sort();
        unknown.dedup();
        errors.push(err(
            "UNKNOWN_REFERENCE",
            format!(
                "the receipt names ids that do not exist: {}; traceability cannot be fabricated",
                unknown.join(", ")
            ),
            unknown,
        ));
    }
    if !wrong.is_empty() {
        errors.push(err(
            "WRONG_REFERENCE_TYPE",
            format!(
                "the receipt names records of the wrong type: {}",
                wrong.join("; ")
            ),
            vec![],
        ));
    }

    // --- claims must stay inside the task's manifest (undocumented implementation is untraceable)
    let in_slot = |id: &str, slots: &[Slot]| {
        m.entries
            .iter()
            .any(|e| e.id == id && slots.contains(&e.slot) && e.delivered())
    };
    let outside: Vec<String> = req_impl
        .iter()
        .filter(|i| store.get(i).is_some() && !in_slot(i, &[Slot::Requirement]))
        .chain(
            scn_impl
                .iter()
                .filter(|i| store.get(i).is_some() && !in_slot(i, &[Slot::Scenario])),
        )
        .chain(
            feat_impl
                .iter()
                .filter(|i| store.get(i).is_some() && !in_slot(i, &[Slot::Feature])),
        )
        .chain(
            dec_applied
                .iter()
                .filter(|i| store.get(i).is_some() && !in_slot(i, &[Slot::Decision])),
        )
        .chain(con_applied.iter().filter(|i| {
            store.get(i).is_some()
                && !in_slot(i, &[Slot::Architecture, Slot::Interface, Slot::Decision])
        }))
        .cloned()
        .collect();
    if !outside.is_empty() {
        errors.push(err("CLAIM_OUTSIDE_MANIFEST", format!("the receipt claims to implement/apply {} which {task_id} does not declare as inputs; declare them in the task's manifest or remove the claim", outside.join(", ")), outside));
    }

    // --- consumption: every required input acknowledged, at the version that is current
    let mut unacknowledged = vec![];
    let mut stale = vec![];
    for e in m.required_satisfied() {
        let Some((_, declared)) = consumed_entries.iter().find(|(id, _)| *id == e.id) else {
            unacknowledged.push(e.id.clone());
            continue;
        };
        let current = e.content_hash.clone().unwrap_or_default();
        let claimed = declared.clone().or_else(|| supplied(&e.id));
        match claimed {
            None => unacknowledged.push(format!(
                "{} (no content hash, and no supplied packet names it)",
                e.id
            )),
            Some(h) => {
                let hn = h.trim().trim_start_matches("sha256:").to_ascii_lowercase();
                let matches = (hn.len() >= 12 && current.starts_with(&hn))
                    || e.version.as_deref() == Some(h.trim());
                if !matches {
                    stale.push(format!(
                        "{}@{h} (current {})",
                        e.id,
                        &current[..current.len().min(16)]
                    ));
                }
            }
        }
    }
    if !unacknowledged.is_empty() {
        errors.push(err(
            "INPUT_NOT_ACKNOWLEDGED",
            format!(
                "required inputs not recorded as consumed: {}; list each as 'ID@<content_hash>'",
                unacknowledged.join(", ")
            ),
            unacknowledged,
        ));
    }
    if !stale.is_empty() {
        errors.push(err("STALE_CONSUMPTION", format!("inputs consumed at a version that is no longer the governed content: {}; recompile the packet and re-verify the work against the current inputs", stale.join(", ")), stale));
    }
    for (id, h) in &consumed_entries {
        if m.entries.iter().any(|e| e.id == *id) || store.get(id).is_none() {
            continue;
        }
        warnings.push(json!({"code": "CONSUMED_UNDECLARED_INPUT", "message": format!("{id}{} was consumed but is not in {task_id}'s manifest", h.as_ref().map(|x| format!("@{x}")).unwrap_or_default()), "ids": [id]}));
    }

    // --- traceability where it is required
    let class = task.get("class");
    let source_outputs: Vec<String> = outputs
        .clone()
        .unwrap_or_default()
        .iter()
        .filter_map(|x| x.as_str())
        .filter(|path| p.contract().decide(path).class() == "source")
        .map(|s| s.to_string())
        .collect();
    let trace_required =
        TRACEABILITY_REQUIRED_CLASSES.contains(&class.as_str()) || !source_outputs.is_empty();
    let deviation_text =
        serde_json::to_string(&deviations.clone().unwrap_or_default()).unwrap_or_default();
    if trace_required {
        let upstream: Vec<&manifest::Entry> = m
            .entries
            .iter()
            .filter(|e| {
                e.required
                    && matches!(
                        e.slot,
                        Slot::Requirement | Slot::Scenario | Slot::Decision | Slot::Feature
                    )
            })
            .collect();
        if upstream.is_empty() {
            errors.push(err("UNTRACEABLE_IMPLEMENTATION", format!("{task_id} ({class}) produces implementation{} but declares no feature, requirement, scenario or decision it realises; implementation needs an authoritative justification", if source_outputs.is_empty() { String::new() } else { format!(" ({})", source_outputs.join(", ")) }), source_outputs.clone()));
        } else if req_impl.is_empty() && scn_impl.is_empty() && feat_impl.is_empty() {
            errors.push(err("TRACEABILITY_MISSING", format!("{task_id} ({class}) closes without naming the requirements/scenarios/features it implemented (requirements_implemented / scenarios_implemented / features_implemented)"), vec![]));
        }
        let mut unaccounted = vec![];
        for e in &upstream {
            if !e.satisfied() {
                continue;
            }
            let done = match e.slot {
                Slot::Requirement => req_impl.contains(&e.id),
                Slot::Scenario => scn_impl.contains(&e.id),
                Slot::Feature => true,
                Slot::Decision => dec_applied.contains(&e.id),
                _ => true,
            };
            if !done && !deviation_text.contains(&e.id) {
                unaccounted.push(format!("{} ({})", e.id, e.slot.name()));
            }
        }
        if !unaccounted.is_empty() {
            errors.push(err(
                "TRACE_INCOMPLETE",
                format!(
                    "mandatory inputs neither implemented/applied nor explained in a deviation: {}",
                    unaccounted.join(", ")
                ),
                unaccounted,
            ));
        }
    }

    // --- acceptance evidence against the declared tests
    let mut no_evidence = vec![];
    let mut failing = vec![];
    for e in m.in_slot(Slot::TestDesign) {
        if !e.required || !e.satisfied() {
            continue;
        }
        match evidence_by_test.get(&e.id) {
            None => no_evidence.push(e.id.clone()),
            Some(ev) => {
                let result = ev
                    .get("result")
                    .or_else(|| ev.get("status"))
                    .and_then(|v| v.as_str())
                    .unwrap_or("");
                let reason = ev.get("reason").and_then(|v| v.as_str()).unwrap_or("");
                if !PASSING_RESULTS.contains(&result)
                    || (result == "not_applicable_with_reason" && reason.trim().is_empty())
                {
                    failing.push(format!(
                        "{} ({})",
                        e.id,
                        if result.is_empty() {
                            "no result"
                        } else {
                            result
                        }
                    ));
                }
            }
        }
    }
    if !no_evidence.is_empty() {
        errors.push(err(
            "TEST_EVIDENCE_MISSING",
            format!(
                "declared acceptance tests without evidence in acceptance_evidence: {}",
                no_evidence.join(", ")
            ),
            no_evidence,
        ));
    }
    if !failing.is_empty() {
        errors.push(err(
            "TEST_EVIDENCE_NOT_PASSING",
            format!(
                "declared acceptance tests whose evidence does not pass: {}",
                failing.join(", ")
            ),
            failing,
        ));
    }

    // --- canonical receipt
    let mut canon = json!({
        "context_packet_hash": packet_hash,
        "inputs_consumed": consumed_entries.iter().map(|(id, h)| { let h = h.clone().or_else(|| supplied(id)); json!({"id": id, "content_hash": h}) }).collect::<Vec<_>>(),
        "outputs_produced": outputs.clone().unwrap_or_default(),
        "requirements_implemented": req_impl, "scenarios_implemented": scn_impl, "features_implemented": feat_impl,
        "decisions_applied": dec_applied, "constraints_applied": con_applied,
        "acceptance_evidence": evidence,
        "deviations": deviations.unwrap_or_default(), "unresolved": unresolved.unwrap_or_default(),
    });
    if let Some(oc) = o.get("outcome") {
        canon["outcome"] = oc.clone();
    }
    Ok(ReceiptCheck {
        task: task_id.to_string(),
        errors,
        warnings,
        receipt: canon,
        manifest_hash: m.hash(),
        packet_hash,
        traceability_required: trace_required,
    })
}

/// Validate, and return the report fields to persist: the receipt in canonical field names merged over the
/// original report, plus `receipt_validation`. Refuses with `RECEIPT_INVALID` (details: every error) when the
/// receipt does not account for the task's inputs, outputs and traceability.
pub fn require_valid(
    p: &Project,
    store: &RecordStore,
    task_id: &str,
    report: &Value,
) -> Result<Value> {
    let chk = validate(p, store, task_id, report)?;
    if !chk.ok() {
        let codes: Vec<String> = chk
            .errors
            .iter()
            .filter_map(|e| e["code"].as_str().map(|s| s.to_string()))
            .collect();
        return Err(GovError::new(
            "RECEIPT_INVALID",
            format!(
                "{task_id}: the consumption receipt does not trace this completion to its inputs ({}). Remediation: return the fields in the packet's receipt_contract — {}",
                codes.join(", "),
                chk.errors.iter().filter_map(|e| e["message"].as_str()).collect::<Vec<_>>().join(" | ")
            ),
        )
        .with_details(chk.to_value()));
    }
    let mut out = report_from_worker_return(report);
    if let (Some(o), Some(c)) = (out.as_object_mut(), chk.receipt.as_object()) {
        for (k, v) in c {
            if !v.is_null() {
                o.insert(k.clone(), v.clone());
            }
        }
        o.insert("receipt_validation".into(), chk.summary());
    }
    Ok(out)
}

/// Closed tasks whose completion does not trace to upstream authority: a DONE task that is held to traceability
/// (by class, or because its closing report records production-source outputs) whose closing report names no
/// implemented requirement/scenario/feature, or whose manifest declares none (W5 line 1125, W7 line 1143).
/// Integration point for the full-audit `product_traceability` family (WS-2).
pub fn untraceable_closed_tasks(p: &Project, store: &RecordStore) -> Vec<Value> {
    let mut out = vec![];
    for t in store.of_type("task") {
        if t.get("task_status") != "DONE" {
            continue;
        }
        let rpt = store.get(&t.get("closed_by_report"));
        let outputs: Vec<String> = rpt
            .map(|r| {
                let mut v = r.list("outputs_produced");
                v.extend(r.list("files_changed"));
                v
            })
            .unwrap_or_default();
        let source: Vec<&String> = outputs
            .iter()
            .filter(|path| p.contract().decide(path).class() == "source")
            .collect();
        let class = t.get("class");
        if !(TRACEABILITY_REQUIRED_CLASSES.contains(&class.as_str()) || !source.is_empty()) {
            continue;
        }
        let m = manifest::resolve(p, store, t);
        let declared = m.entries.iter().any(|e| {
            e.required
                && matches!(
                    e.slot,
                    Slot::Requirement | Slot::Scenario | Slot::Decision | Slot::Feature
                )
        });
        let traced = rpt
            .map(|r| {
                !r.list("requirements_implemented").is_empty()
                    || !r.list("scenarios_implemented").is_empty()
                    || !r.list("features_implemented").is_empty()
            })
            .unwrap_or(false);
        if !declared || !traced {
            out.push(json!({"task": t.id(), "class": class, "closed_by_report": t.get("closed_by_report"),
                "declares_upstream": declared, "report_traces_implementation": traced, "source_outputs": source,
                "message": format!("{} ({class}) is DONE but its implementation {}", t.id(), if !declared { "has no declared feature/requirement/scenario/decision" } else { "is not traced to the requirements/scenarios it implemented" })}));
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn worker_return_and_report_are_one_contract() {
        let w = json!({"task": "TASK-0001", "status": "success", "work_completed": "x", "files_changed": ["src/lib.rs"],
                       "evidence": [], "tests": {"status": "passed"}, "discoveries": [], "risks": [], "lessons": [],
                       "proposed_decisions": [], "unresolved": [], "recommended_next_action": "none",
                       "inputs_consumed": ["REQ-0001@0123456789abcdef"], "deviations": []});
        let r = report_from_worker_return(&w);
        assert!(
            r.get("status").is_none(),
            "the worker status must not collide with the record lifecycle status"
        );
        assert_eq!(r["outcome"], "success");
        // the OS adds its record fields at close; the inverse mapping recovers the worker return exactly
        let mut persisted = r.clone();
        for (k, v) in [
            ("id", json!("RPT-0001")),
            ("type", json!("report")),
            ("status", json!("ACTIVE")),
            ("session", json!("S")),
            ("role", json!("r")),
            ("state_class", json!("EVIDENCE")),
            ("observed_files_changed", json!(["src/lib.rs"])),
        ] {
            persisted[k] = v;
        }
        assert_eq!(worker_return_from_report(&persisted), w);
        // a lifecycle status that is not a worker status is left alone
        let r2 = report_from_worker_return(&json!({"status": "ACTIVE"}));
        assert_eq!(r2["status"], "ACTIVE");
    }

    #[test]
    fn worker_return_maps_to_a_schema_valid_report() {
        let schemas = crate::schemas::SchemaRegistry::new(
            &std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../framework/schemas"),
        );
        let w = json!({"task": "TASK-0001", "status": "partial", "work_completed": "x", "files_changed": [],
                       "evidence": [], "tests": {"status": "passed"}, "discoveries": [], "risks": [], "lessons": [],
                       "proposed_decisions": [], "unresolved": ["u"], "recommended_next_action": "none"});
        assert!(schemas.errors("worker-return", &w).unwrap().is_empty());
        let mut rec =
            crate::records::new_record("report", "RPT-0001", "t", report_from_worker_return(&w));
        rec.set("state_class", json!("EVIDENCE"));
        let errs = schemas.errors("report", &rec.data).unwrap();
        assert!(errs.is_empty(), "{errs:?}");
        // without the mapping the collision S0-W5-01 describes is real
        let bad = crate::records::new_record("report", "RPT-0002", "t", w.clone());
        assert!(!schemas.errors("report", &bad.data).unwrap().is_empty());
    }
}
