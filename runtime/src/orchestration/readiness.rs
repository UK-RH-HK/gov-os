//! Feature/Capability Readiness Contract (framework §37-38): every cell explicit; gaps generate tasks in the same DAG.
//!
//! A generated gap task carries the designated role its dimension declares (`gap_task_role` in the kernel taxonomy
//! `READINESS_DIMENSIONS.yaml`): independent acceptance tests go to the independent test designer and representative
//! test data to the data author, so the designated role binds who may claim and close them (BC-P2-34, task-role
//! side). Its stored status is the one the task DAG derives (READY only when runnable, BC-P2-16).
use crate::orchestration::control;
use crate::records::{new_record, save_record, Record, RecordStore};
use crate::util::{now_iso, read_yaml};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Clone, serde::Serialize)]
pub struct ReadinessView {
    pub feature: String,
    pub cells: Vec<Value>,
    pub gaps: Vec<String>,
    pub pre_implementation_gaps: Vec<String>,
    pub pre_implementation_ok: bool,
    pub invalid: Vec<String>,
    pub coverage: f64,
}

pub fn dimensions(p: &Project) -> Vec<Value> {
    read_yaml(
        &p.kernel_dir()
            .join("taxonomy")
            .join("READINESS_DIMENSIONS.yaml"),
    )
    .ok()
    .and_then(|v| v.get("dimensions").and_then(|d| d.as_array()).cloned())
    .unwrap_or_default()
}

/// Readiness cells the scenario chain determines (`lifecycle::scenario::readiness_cells`, WS-10 IP-WS10-12): their
/// state is computed from the product's own records, not taken from what the feature asserts.
pub const CHAIN_CELLS: &[&str] = &[
    "success_criteria",
    "failure_criteria",
    "representative_test_data",
    "independent_acceptance_tests",
];

/// The readiness cell a scenario-chain gap code belongs to (the same mapping `lifecycle::scenario::readiness_cells`
/// applies), if any.
pub fn chain_cell_of(code: &str) -> Option<&'static str> {
    match code {
        "SCENARIO_WITHOUT_SUCCESS_CRITERIA" => Some("success_criteria"),
        "SCENARIO_WITHOUT_FAILURE_CRITERIA" => Some("failure_criteria"),
        "SCENARIO_WITHOUT_TEST" | "SCENARIO_WITHOUT_INDEPENDENT_TEST" => {
            Some("independent_acceptance_tests")
        }
        "SCENARIO_DATA_UNDECLARED"
        | "DATA_REQUIREMENT_NOT_GOVERNED"
        | "DATA_REQUIREMENT_UNRESOLVED"
        | "DATA_REQUIREMENT_WRONG_TYPE"
        | "DATA_REQUIREMENT_WITHOUT_TEST_DATA"
        | "TEST_DATA_WITHOUT_PROVENANCE"
        | "TEST_DATA_PROVENANCE_INVALID"
        | "TEST_DATA_PROVENANCE_UNSTRUCTURED"
        | "TEST_DATA_REAL_DATA_UNAPPROVED"
        | "TEST_DATA_LOCATION_MISSING"
        | "TEST_DATA_CHANGED"
        | "TEST_DATA_UNDECLARED"
        | "DATA_AUTHOR_NOT_INDEPENDENT"
        | "DATA_AUTHOR_IS_TEST_AUTHOR" => Some("representative_test_data"),
        _ => None,
    }
}

/// Cells `feature` states not applicable with a reason (`{status: N/A_WITH_REASON, reason}`): explicit, reviewable
/// statements the product honours (a silent N/A is invalid).
pub fn not_applicable_cells(feature: &Record) -> Vec<String> {
    feature
        .data
        .get("readiness")
        .and_then(|r| r.as_object())
        .map(|m| {
            m.iter()
                .filter(|(_, v)| {
                    v.get("status").and_then(|s| s.as_str()) == Some("N/A_WITH_REASON")
                        && v.get("reason")
                            .and_then(|r| r.as_str())
                            .map(|r| r.trim().len() >= 3)
                            .unwrap_or(false)
                })
                .map(|(k, _)| k.clone())
                .collect()
        })
        .unwrap_or_default()
}

/// `(state, reason)` of a readiness cell value as authored.
fn cell_state(cell: &Value) -> (String, Option<String>) {
    match cell {
        Value::String(s) => (s.clone(), None),
        Value::Object(o) => (
            o.get("status")
                .and_then(|v| v.as_str())
                .unwrap_or("INVALID")
                .to_string(),
            o.get("reason")
                .and_then(|v| v.as_str())
                .map(|s| s.to_string()),
        ),
        _ => ("INVALID".into(), None),
    }
}

/// A silent N/A (no reason) or a malformed cell value: never honoured, and reported as invalid.
fn silent_or_invalid(cell: &Value) -> bool {
    let (state, reason) = cell_state(cell);
    state == "N/A" || (state == "N/A_WITH_REASON" && reason.is_none()) || state == "INVALID"
}

pub fn evaluate(p: &Project, feature: &Record) -> ReadinessView {
    let store = RecordStore::load(&p.root);
    let lctx = crate::lifecycle::Ctx::new(p, &store);
    evaluate_in(p, &lctx, feature)
}

/// Evaluate `feature`'s readiness against the kernel dimensions. The cells the scenario chain determines
/// ([`CHAIN_CELLS`]) are **computed** from the feature's scenarios, data, test data and tests
/// (`lifecycle::scenario::readiness_cells`) rather than taken on the feature's word: an assertion the chain
/// contradicts (e.g. `PRESENT` while a scenario lacks failure criteria or its test data has no provenance) is
/// `MISSING` with the chain's reasons; where the chain holds, the author's own statement stands (the chain never
/// upgrades a cell the author keeps open). A cell the feature states `N/A_WITH_REASON` keeps that explicit
/// statement. Each chain cell records what was asserted, what the chain found and where it came from.
pub fn evaluate_in(p: &Project, lctx: &crate::lifecycle::Ctx, feature: &Record) -> ReadinessView {
    let dims = dimensions(p);
    let mut readiness = feature.data.get("readiness").cloned().unwrap_or(json!({}));
    if !readiness.is_object() {
        readiness = json!({});
    }
    let computed = crate::lifecycle::scenario::readiness_cells(lctx, feature);
    let mut provenance: BTreeMap<String, Value> = BTreeMap::new();
    // an authored silent N/A or malformed value stays invalid when the chain computes the cell's state
    let mut asserted_invalid: BTreeSet<String> = BTreeSet::new();
    for cell in CHAIN_CELLS {
        let asserted = readiness.get(*cell).cloned().unwrap_or(json!("MISSING"));
        if silent_or_invalid(&asserted) {
            asserted_invalid.insert(cell.to_string());
        }
        let na = asserted.get("status").and_then(|s| s.as_str()) == Some("N/A_WITH_REASON");
        let Some(c) = computed.get(*cell) else {
            continue;
        };
        if na {
            provenance.insert(cell.to_string(), json!({"asserted": asserted, "computed": c, "honoured": "the feature's explicit N/A_WITH_REASON"}));
            continue;
        }
        let computed_state = c["state"].as_str().unwrap_or("MISSING").to_string();
        // the chain refutes an assertion it contradicts; it never upgrades a cell the author keeps open
        let state = if computed_state == "PRESENT" {
            match &asserted {
                Value::String(s) => s.clone(),
                other => other
                    .get("status")
                    .and_then(|x| x.as_str())
                    .unwrap_or("MISSING")
                    .to_string(),
            }
        } else {
            computed_state.clone()
        };
        if state != "PRESENT" || asserted.as_str() != Some("PRESENT") {
            readiness[*cell] = json!(state);
        }
        provenance.insert(cell.to_string(), json!({"asserted": asserted, "state": state, "chain_state": computed_state, "computed_from": c["computed_from"], "reasons": c["reasons"]}));
    }
    let readiness = readiness;
    let mut cells = vec![];
    let mut gaps = vec![];
    let mut pre_gaps = vec![];
    let mut invalid = vec![];
    let mut present = 0usize;
    for d in &dims {
        let id = d["id"].as_str().unwrap_or("").to_string();
        let pre = d["pre_implementation"].as_bool().unwrap_or(false);
        let cell = readiness.get(&id).cloned().unwrap_or(json!("MISSING"));
        let (state, reason) = cell_state(&cell);
        let ok = state == "PRESENT"
            || (state == "N/A_WITH_REASON"
                && reason.as_ref().map(|r| r.len() >= 3).unwrap_or(false));
        if silent_or_invalid(&cell) || asserted_invalid.contains(&id) {
            invalid.push(format!(
                "{id}: silent N/A or invalid cell value is not allowed"
            ));
        }
        if ok {
            present += 1;
        } else {
            gaps.push(id.clone());
            if pre {
                pre_gaps.push(id.clone());
            }
        }
        let mut row = json!({"dimension": id, "state": state, "reason": reason, "pre_implementation": pre, "gap_task_class": d["gap_task_class"], "gap_task_role": d["gap_task_role"], "ok": ok});
        if let Some(pv) = provenance.get(&id) {
            row["computed"] = pv.clone();
        }
        cells.push(row);
    }
    let coverage = if dims.is_empty() {
        1.0
    } else {
        present as f64 / dims.len() as f64
    };
    ReadinessView {
        feature: feature.id(),
        cells,
        gaps,
        pre_implementation_gaps: pre_gaps.clone(),
        pre_implementation_ok: pre_gaps.is_empty() && invalid.is_empty(),
        invalid,
        coverage,
    }
}

pub fn check(p: &Project, feature_id: &str) -> Result<ReadinessView> {
    let store = RecordStore::load(&p.root);
    let f = store
        .get(feature_id)
        .filter(|r| r.rtype() == "feature")
        .ok_or_else(|| GovError::new("FEATURE_NOT_FOUND", format!("{feature_id} not found")))?;
    Ok(evaluate(p, f))
}

/// Generate gap tasks for MISSING cells and make implementation tasks of the feature depend on pre-implementation gap tasks.
pub fn plan(p: &Project, feature_id: &str) -> Result<Value> {
    control::guard_write(p, "readiness plan")?;
    let view = check(p, feature_id)?;
    let store = RecordStore::load(&p.root);
    let existing: Vec<&Record> = store
        .of_type("task")
        .into_iter()
        .filter(|t| t.get("feature") == feature_id)
        .collect();
    let mut created = vec![];
    let mut pre_task_ids = vec![];
    let mut ids: Vec<String> = store.records.iter().map(|r| r.id()).collect();
    for c in &view.cells {
        if c["ok"].as_bool().unwrap_or(false) {
            continue;
        }
        let dim = c["dimension"].as_str().unwrap_or("").to_string();
        if let Some(t) = existing
            .iter()
            .find(|t| t.get("readiness_cell") == dim && t.get("task_status") != "CANCELLED")
        {
            if c["pre_implementation"].as_bool().unwrap_or(false) {
                pre_task_ids.push(t.id());
            }
            continue;
        }
        let id = crate::util::next_id("TASK", &ids, 4);
        ids.push(id.clone());
        let class = c["gap_task_class"]
            .as_str()
            .unwrap_or("specification")
            .to_string();
        let mut fields = json!({"class": class, "task_status": "READY", "feature": feature_id, "objective": format!("Fill readiness dimension '{dim}' for {feature_id} (currently {})", c["state"]), "readiness_cell": dim, "generated_by": "readiness-planner", "dependencies": [], "minimum_model_tier": crate::routing::tier_for_class(p, &class), "minimum_reasoning": "medium", "allowed_paths": ["spec/**"], "forbidden_paths": ["governance/kernel/**", "product/**"], "production_merge_allowed": false, "state_class": "AUTHORITATIVE",
            "provenance": {"producer": "gov readiness plan", "session": p.session_id, "role": p.role, "created_at": now_iso()}});
        // the dimension's designated role binds who may claim and close the gap task (independent tests, test data)
        if let Some(role) = c["gap_task_role"]
            .as_str()
            .filter(|r| !r.is_empty() && crate::authority::is_kernel_role(p, r))
        {
            fields["role"] = json!(role);
        }
        let mut rec = new_record(
            "task",
            &id,
            &format!("{feature_id}: provide readiness cell '{dim}'"),
            fields,
        );
        p.schemas()
            .validate("task", &rec.data, &format!("({id})"))?;
        // READY is derived from the DAG (BC-P2-16)
        let ctx = crate::orchestration::dag::DagCtx::new(p, &store);
        let ev = crate::orchestration::dag::evaluate(&ctx, &rec, Some("READY"));
        if !ev.runnable() {
            let st = if ev.state == crate::orchestration::dag::TaskState::WaitingHuman {
                "WAITING_HUMAN"
            } else {
                "BLOCKED"
            };
            rec.set("task_status", json!(st));
            rec.set(
                "status_note",
                json!(format!(
                    "the task DAG does not allow READY: {}",
                    ev.reasons.join("; ")
                )),
            );
        }
        let stored = rec.get("task_status");
        rec.set("status_source", json!({"operation": "readiness plan", "status": stored, "session": p.session_id, "role": p.role, "at": now_iso()}));
        // a task record is T2 state the OS writes (round-3 integration): sealed as written by this operation
        crate::t2::seal_record(&mut rec, "readiness plan")?;
        save_record(&p.root, &rec)?;
        created.push(id.clone());
        if c["pre_implementation"].as_bool().unwrap_or(false) {
            pre_task_ids.push(id);
        }
    }
    let mut linked = vec![];
    let mut store2 = RecordStore::load(&p.root);
    let impl_ids: Vec<String> = store2
        .of_type("task")
        .into_iter()
        .filter(|t| t.get("feature") == feature_id && t.get("class") == "implementation")
        .map(|t| t.id())
        .collect();
    for tid in impl_ids {
        let t = store2.get_mut(&tid).unwrap();
        let mut deps = t.list("dependencies");
        let before = deps.len();
        for g in &pre_task_ids {
            if !deps.contains(g) && *g != tid {
                deps.push(g.clone());
            }
        }
        if deps.len() != before {
            let was_verified = crate::t2::verify_record(t).is_verified();
            t.set("dependencies", json!(deps));
            if t.get("task_status") == "READY" {
                t.set("task_status", json!("BLOCKED"));
            }
            crate::t2::seal_if_verified(t, was_verified, "readiness plan")?;
            save_record(&p.root, t)?;
            linked.push(tid);
        }
    }
    Ok(
        json!({"feature": feature_id, "created_tasks": created, "pre_implementation_gap_tasks": pre_task_ids, "implementation_tasks_blocked": linked, "gaps": view.gaps, "coverage": view.coverage}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::records::new_record;

    /// Every pre-implementation gap of the scenario chain (`lifecycle::scenario`) belongs to a chain readiness cell,
    /// and every chain cell is a pre-implementation dimension of the kernel taxonomy: the DAG's chain gating and the
    /// computed readiness cells cannot disagree.
    #[test]
    fn every_pre_implementation_chain_gap_belongs_to_a_chain_cell() {
        for code in crate::lifecycle::scenario::PRE_IMPLEMENTATION_CODES {
            let cell =
                chain_cell_of(code).unwrap_or_else(|| panic!("{code} maps to no readiness cell"));
            assert!(CHAIN_CELLS.contains(&cell), "{code} -> {cell}");
        }
        let taxonomy: Value = serde_yaml::from_str(include_str!(
            "../../../framework/taxonomy/READINESS_DIMENSIONS.yaml"
        ))
        .unwrap();
        for cell in CHAIN_CELLS {
            let d = taxonomy["dimensions"]
                .as_array()
                .unwrap()
                .iter()
                .find(|d| d["id"].as_str() == Some(cell))
                .unwrap_or_else(|| panic!("{cell} is not a kernel readiness dimension"));
            assert_eq!(d["pre_implementation"], true, "{cell}");
        }
    }

    /// A not-applicable cell is honoured only as an explicit statement with a reason (a silent N/A is invalid).
    #[test]
    fn not_applicable_cells_need_a_reason() {
        let f = new_record(
            "feature",
            "F-0001",
            "f",
            json!({"readiness": {
                "representative_test_data": {"status": "N/A_WITH_REASON", "reason": "pure arithmetic, literal inputs"},
                "success_criteria": {"status": "N/A_WITH_REASON"},
                "failure_criteria": "N/A",
                "independent_acceptance_tests": "PRESENT"}}),
        );
        assert_eq!(
            not_applicable_cells(&f),
            vec!["representative_test_data".to_string()]
        );
        // a silent N/A stays invalid whether or not the chain computes the cell
        let r = &f.data["readiness"];
        assert!(!silent_or_invalid(&r["representative_test_data"]));
        assert!(silent_or_invalid(&r["success_criteria"]));
        assert!(silent_or_invalid(&r["failure_criteria"]));
        assert!(!silent_or_invalid(&r["independent_acceptance_tests"]));
        assert!(silent_or_invalid(&json!(3)));
    }
}
