//! # Scenarios drive data and tests (Contract v3 H4, lines 524-527; framework §39; BC-P2-46 and the data-authorship
//! part of BC-P2-34)
//!
//! ```text
//! FEATURE → SCENARIOS → DATA REQUIREMENTS → TEST DATA DESIGN → SUCCESS/FAILURE CRITERIA → INDEPENDENT TEST DESIGN
//! ```
//!
//! **The chain, in the product's own fields** (the records carry it; nothing here needs the derived index):
//!
//! | link | field(s) |
//! |---|---|
//! | FEATURE → SCENARIO | `feature.scenarios`, or `scenario.feature` |
//! | SCENARIO → DATA | `scenario.data_requirements`: ids of `data` records (`data_kind: requirement`); or `scenario.data_requirements_not_applicable` with the reason |
//! | DATA → TEST DATA | a `data` record (`data_kind: test-dataset`) naming the requirement(s) it realises in `implements` (also accepted: `derived_from`, `realises`, `relations[]` IMPLEMENTS/DERIVED_FROM/REALISES), or the requirement's `test_data` |
//! | SUCCESS/FAILURE | `scenario.success_criteria`, `scenario.failure_criteria` |
//! | INDEPENDENT TESTS | `test-obligation.scenario` (a family in `TEST_POLICY.independent_test_author_required_for`, `independent_of_implementer: true`), with the test data it uses in `test_data` (also accepted: `required_data`, ids named in `data_provenance`) |
//!
//! Every missing link is a typed gap ([`scenario_chain`], [`findings`]). **Provenance** is required and read: a test
//! dataset records `provenance: {source_kind, origin, …}` — `source_kind` one of framework §39's kinds
//! ([`SOURCE_KINDS`]); `approved-real` data names the human-approved decision that approved it (honoured only
//! through [`crate::orchestration::gates::verified_decision`]); a `location` is bound by SHA-256 at registration and
//! re-checked. **Authorship** is recorded by the OS (`gov data register` stamps role and session, T2-sealed; a
//! dataset produced by a task is attributed to the closing session through the OS-observed paths of its report), and
//! the data author's **independence** from the implementer (designated role and closing session of every
//! implementation task of the feature/scenario) and from the end-to-end test author is checked — "the data author
//! should normally be independent": an exception is an owner-approved `independence_waiver` decision.
//!
//! The graph edges for `data_requirements` and `test_data` are WS-4's (`records.rs` relation fields; integration
//! point): `implements`, `derived_from` and `required_data` already yield edges.
use super::{
    authorship_of, hash_path, ids_in, is_current, list, location_paths, present, refuse_os_owned,
    safe_rel_path, stamp, validate_seal_save, Authorship, Ctx,
};
use crate::authority;
use crate::orchestration::control;
use crate::records::{new_record, Record, RecordStore};
use crate::{GovError, Project, Result};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet};

/// Framework §39: data may be approved real data, open/public datasets, repository/GitHub test corpora, generated
/// synthetic data, simulator output, or fixtures.
pub const SOURCE_KINDS: &[&str] = &[
    "approved-real",
    "public",
    "repository-corpus",
    "synthetic",
    "simulator",
    "fixture",
];
pub const DATA_KINDS: &[&str] = &["requirement", "test-dataset"];
/// Task classes whose author is "the implementation author" for data-author independence.
pub const IMPLEMENTATION_CLASSES: &[&str] = &[
    "implementation",
    "integration",
    "refactor",
    "repair",
    "performance",
    "security",
    "devops",
    "migration",
];
/// Fields by which a test dataset names the data requirements it realises.
pub const REALISES_FIELDS: &[&str] = &["implements", "derived_from", "realises"];
const REALISES_RELATIONS: &[&str] = &["IMPLEMENTS", "DERIVED_FROM", "REALISES"];

/// One missing or broken link of the chain.
#[derive(Debug, Clone)]
pub struct Gap {
    pub severity: &'static str,
    pub code: &'static str,
    pub record: String,
    pub path: String,
    pub message: String,
}

impl Gap {
    fn on(r: &Record, severity: &'static str, code: &'static str, message: String) -> Gap {
        Gap {
            severity,
            code,
            record: r.id(),
            path: r.path.clone(),
            message,
        }
    }
    pub fn to_value(&self) -> Value {
        json!({"severity": self.severity, "family": super::FAMILY, "code": self.code, "record": self.record, "path": self.path, "message": self.message})
    }
}

// ------------------------------------------------------------------------------------------------ resolution

/// The data requirements a test dataset realises.
pub fn realised_requirements(r: &Record) -> Vec<String> {
    let mut out: BTreeSet<String> = BTreeSet::new();
    for f in REALISES_FIELDS {
        out.extend(list(r, f));
    }
    for rel in r.data["relations"].as_array().cloned().unwrap_or_default() {
        if REALISES_RELATIONS.contains(&rel["type"].as_str().unwrap_or("")) {
            if let Some(t) = rel["target"].as_str() {
                out.insert(t.to_string());
            }
        }
    }
    out.into_iter().collect()
}

/// Is `id` named as a data requirement by any scenario?
fn required_by_a_scenario(store: &RecordStore, id: &str) -> bool {
    store
        .of_type("scenario")
        .iter()
        .any(|s| list(s, "data_requirements").iter().any(|x| x == id))
}

/// The kind of a `data` record: declared `data_kind`, else inferred from where the chain uses it.
pub fn data_kind(store: &RecordStore, r: &Record) -> String {
    let k = r.get("data_kind");
    if !k.is_empty() {
        return k;
    }
    if required_by_a_scenario(store, &r.id()) {
        return "requirement".into();
    }
    if realised_requirements(r)
        .iter()
        .any(|x| store.get(x).map(|y| y.rtype() == "data").unwrap_or(false))
    {
        return "test-dataset".into();
    }
    if store
        .of_type("test-obligation")
        .iter()
        .any(|t| test_data_of(store, t).0.contains(&r.id()))
    {
        return "test-dataset".into();
    }
    "unknown".into()
}

/// The test datasets that realise data requirement `req`.
pub fn test_datasets_for(store: &RecordStore, req: &str) -> Vec<String> {
    let mut out: BTreeSet<String> = BTreeSet::new();
    for d in store.of_type("data") {
        if d.id() != req
            && d.get("data_kind") != "requirement"
            && realised_requirements(d).iter().any(|x| x == req)
        {
            out.insert(d.id());
        }
    }
    if let Some(r) = store.get(req) {
        for t in list(r, "test_data") {
            if store.get(&t).map(|x| x.rtype() == "data").unwrap_or(false) {
                out.insert(t);
            }
        }
    }
    out.into_iter().collect()
}

pub fn scenarios_of_feature(store: &RecordStore, f: &Record) -> Vec<String> {
    let mut out: BTreeSet<String> = list(f, "scenarios").into_iter().collect();
    for s in store.of_type("scenario") {
        if s.get("feature") == f.id() {
            out.insert(s.id());
        }
    }
    out.into_iter().collect()
}

pub fn feature_of_scenario(store: &RecordStore, s: &Record) -> Option<String> {
    let f = s.get("feature");
    if !f.is_empty() {
        return Some(f);
    }
    store
        .of_type("feature")
        .into_iter()
        .find(|f| list(f, "scenarios").contains(&s.id()))
        .map(|f| f.id())
}

/// Test obligations that test scenario `scn`.
pub fn tests_of_scenario<'s>(store: &'s RecordStore, scn: &str) -> Vec<&'s Record> {
    store
        .of_type("test-obligation")
        .into_iter()
        .filter(|t| t.get("scenario") == scn || list(t, "scenarios").iter().any(|x| x == scn))
        .collect()
}

/// The governed test data a test obligation uses (ids of `data` records from `test_data`, `required_data` and ids
/// named in `data_provenance`), and its free-text provenance if any.
pub fn test_data_of(store: &RecordStore, t: &Record) -> (Vec<String>, Option<String>) {
    let mut ids: BTreeSet<String> = BTreeSet::new();
    for f in ["test_data", "required_data"] {
        for id in ids_in(t.data.get(f)) {
            ids.insert(id);
        }
    }
    let prov = t.data.get("data_provenance");
    for id in ids_in(prov) {
        ids.insert(id);
    }
    let governed: Vec<String> = ids
        .into_iter()
        .filter(|id| store.get(id).map(|x| x.rtype() == "data").unwrap_or(false))
        .collect();
    let text = match prov {
        Some(Value::String(s)) if !s.trim().is_empty() => Some(s.clone()),
        Some(v @ Value::Array(_)) if present(Some(v)) => Some(v.to_string()),
        Some(v @ Value::Object(_)) if present(Some(v)) => Some(v.to_string()),
        _ => None,
    };
    (governed, text)
}

fn independent_test(ctx: &Ctx, t: &Record) -> bool {
    ctx.independent_families.contains(&t.get("family"))
        && t.data
            .get("independent_of_implementer")
            .and_then(|v| v.as_bool())
            .unwrap_or(false)
}

/// Someone who authored or executed part of the chain.
#[derive(Debug, Clone)]
pub struct Actor {
    pub role: Option<String>,
    pub session: Option<String>,
    pub via: String,
}

impl Actor {
    pub fn to_value(&self) -> Value {
        json!({"role": self.role, "session": self.session, "via": self.via})
    }
}

/// The implementers of a feature/scenario: the designated role of every implementation-class task of it, and the
/// role and session that closed it.
pub fn implementers(ctx: &Ctx, feature: &str, scenario: &str) -> Vec<Actor> {
    let mut out = vec![];
    for t in ctx.store.of_type("task") {
        if !IMPLEMENTATION_CLASSES.contains(&t.get("class").as_str())
            || t.get("task_status") == "CANCELLED"
        {
            continue;
        }
        let linked = (!feature.is_empty() && t.get("feature") == feature)
            || (!scenario.is_empty() && list(t, "scenarios").iter().any(|x| x == scenario));
        if !linked {
            continue;
        }
        let role = t.get("role");
        if !role.is_empty() {
            out.push(Actor {
                role: Some(role),
                session: None,
                via: format!("designated role of {}", t.id()),
            });
        }
        let rep = t.get("closed_by_report");
        if let Some(r) = ctx.store.get(&rep) {
            out.push(Actor {
                role: Some(r.get("role")).filter(|x| !x.is_empty()),
                session: Some(r.get("session")).filter(|x| !x.is_empty()),
                via: format!("closing session of {} ({})", t.id(), r.id()),
            });
        }
    }
    out
}

/// The authors of the end-to-end (independent-family) tests of a scenario.
pub fn e2e_authors(ctx: &Ctx, scenario: &str) -> Vec<(String, Authorship)> {
    tests_of_scenario(ctx.store, scenario)
        .into_iter()
        .filter(|t| ctx.independent_families.contains(&t.get("family")))
        .map(|t| (t.id(), authorship_of(ctx, t)))
        .filter(|(_, a)| a.role.is_some() || a.session.is_some())
        .collect()
}

/// Drop repeated gaps (the same code on the same record with the same message, reached through two links).
fn dedup_gaps(gaps: Vec<Gap>) -> Vec<Gap> {
    let mut seen = BTreeSet::new();
    gaps.into_iter()
        .filter(|g| seen.insert((g.code, g.record.clone(), g.message.clone())))
        .collect()
}

// ------------------------------------------------------------------------------------------------ dataset checks

/// Provenance of a test dataset: present, structured, a known source kind with an origin, approved when real, and
/// its content still what was bound.
pub fn provenance_gaps(ctx: &Ctx, d: &Record) -> Vec<Gap> {
    let id = d.id();
    let mut g = vec![];
    match d.data.get("provenance") {
        None | Some(Value::Null) => g.push(Gap::on(d, "medium", "TEST_DATA_WITHOUT_PROVENANCE", format!(
            "test data {id} records no provenance (Contract v3 H4 'Data provenance is recorded'; framework §39 'Provenance must be recorded'): record provenance {{source_kind: one of {SOURCE_KINDS:?}, origin}} (`gov data register`)"
        ))),
        Some(Value::Object(o)) => {
            let sk = o.get("source_kind").and_then(|v| v.as_str()).unwrap_or("");
            if !SOURCE_KINDS.contains(&sk) {
                g.push(Gap::on(d, "medium", "TEST_DATA_PROVENANCE_INVALID", format!(
                    "test data {id}: provenance.source_kind '{sk}' is not one of {SOURCE_KINDS:?} (framework §39)"
                )));
            }
            if !present(o.get("origin")) {
                g.push(Gap::on(d, "medium", "TEST_DATA_PROVENANCE_INVALID", format!(
                    "test data {id}: provenance.origin (where the data came from / how it was generated) is not recorded"
                )));
            }
            if sk == "approved-real" {
                let approval = o.get("approval").and_then(|v| v.as_str()).unwrap_or("");
                let ok = !approval.is_empty()
                    && (ctx.verified_decision)(approval)
                        .map(|dec| dec.data.get("human_approved").and_then(|v| v.as_bool()).unwrap_or(false))
                        .unwrap_or(false);
                if !ok {
                    g.push(Gap::on(d, "high", "TEST_DATA_REAL_DATA_UNAPPROVED", format!(
                        "test data {id} is real data, and provenance.approval ('{approval}') is not a verified, human-approved decision"
                    )));
                }
            }
        }
        Some(_) => g.push(Gap::on(d, "medium", "TEST_DATA_PROVENANCE_UNSTRUCTURED", format!(
            "test data {id}: provenance is free text; record {{source_kind, origin}} so it can be read and checked"
        ))),
    }
    if let Some(root) = ctx.root {
        let recorded = d.data["provenance"]["content_sha256"].clone();
        for loc in location_paths(d) {
            let h = safe_rel_path(&loc).ok().and_then(|l| hash_path(root, &l));
            let want = match &recorded {
                Value::String(s) => Some(s.clone()),
                Value::Object(m) => m.get(&loc).and_then(|v| v.as_str()).map(String::from),
                _ => None,
            };
            match (h, want) {
                (None, _) => g.push(Gap::on(d, "medium", "TEST_DATA_LOCATION_MISSING", format!("test data {id}: its location '{loc}' does not exist"))),
                (Some(h), Some(w)) if h != w => g.push(Gap::on(d, "medium", "TEST_DATA_CHANGED", format!(
                    "test data {id}: '{loc}' changed since its provenance was recorded (sha256 {w} → {h}); re-register it"
                ))),
                (Some(_), None) => g.push(Gap::on(d, "low", "TEST_DATA_UNBOUND", format!(
                    "test data {id}: '{loc}' carries no recorded content hash, so a change to it cannot be detected (`gov data register` binds it)"
                ))),
                _ => {}
            }
        }
    }
    g
}

/// The honoured independence waiver of a dataset (an owner-approved decision), if any.
fn waiver(ctx: &Ctx, d: &Record) -> Option<String> {
    let w = &d.data["independence_waiver"];
    let dec = w
        .get("decision")
        .and_then(|v| v.as_str())
        .or(w.as_str())
        .unwrap_or("");
    if dec.is_empty() {
        return None;
    }
    (ctx.verified_decision)(dec)
        .ok()
        .filter(|r| {
            r.data
                .get("human_approved")
                .and_then(|v| v.as_bool())
                .unwrap_or(false)
        })
        .map(|_| dec.to_string())
}

/// Framework §39 / Contract v3:526: the data author against the implementers and the end-to-end test authors.
pub fn independence_gaps(
    ctx: &Ctx,
    d: &Record,
    implementers: &[Actor],
    e2e: &[(String, Authorship)],
) -> Vec<Gap> {
    let id = d.id();
    let mut g = vec![];
    if waiver(ctx, d).is_some() {
        return g;
    }
    let a = authorship_of(ctx, d);
    if !a.established {
        g.push(Gap::on(d, "medium", "DATA_AUTHORSHIP_NOT_ESTABLISHED", format!(
            "the author of test data {id} was not recorded by the product (authorship: {}{}), so its independence from the implementer and the end-to-end test author cannot be established: register it as its author (`gov data register`) or produce it in a task closed by the data author",
            a.source, a.role.as_ref().map(|r| format!(", declared role {r}")).unwrap_or_default()
        )));
    }
    for x in implementers {
        let same_role = a.role.is_some() && a.role == x.role;
        let same_session = a.session.is_some() && a.session == x.session;
        if same_role || same_session {
            g.push(Gap::on(d, "medium", "DATA_AUTHOR_NOT_INDEPENDENT", format!(
                "test data {id} was authored by {} ({}), the same {} as the implementer ({}): the data author must be independent of the implementation author (framework §39; Contract v3:526), or the owner waives it (`independence_waiver`)",
                a.role.clone().or(a.session.clone()).unwrap_or_default(), a.source,
                if same_session { "session" } else { "role" }, x.via
            )));
        }
    }
    for (tid, ta) in e2e {
        let same_role = a.role.is_some() && a.role == ta.role;
        let same_session = a.session.is_some() && a.session == ta.session;
        if same_role || same_session {
            g.push(Gap::on(d, "medium", "DATA_AUTHOR_IS_TEST_AUTHOR", format!(
                "test data {id} was authored by the same {} as the end-to-end test {tid} ({}): the data author must be independent of the end-to-end test author (framework §39)",
                if same_session { "session" } else { "role" },
                ta.role.clone().or(ta.session.clone()).unwrap_or_default()
            )));
        }
    }
    g
}

/// The scenarios a dataset serves: those whose data requirements it realises, and those whose tests use it; plus the
/// features of tests that use it without naming a scenario.
fn dataset_contexts(store: &RecordStore, d: &Record) -> (BTreeSet<String>, BTreeSet<String>) {
    let reqs = realised_requirements(d);
    let mut scns: BTreeSet<String> = BTreeSet::new();
    let mut feats: BTreeSet<String> = BTreeSet::new();
    for s in store.of_type("scenario") {
        if list(s, "data_requirements")
            .iter()
            .any(|x| reqs.contains(x))
        {
            scns.insert(s.id());
        }
    }
    for t in store.of_type("test-obligation") {
        if test_data_of(store, t).0.contains(&d.id()) {
            let s = t.get("scenario");
            if !s.is_empty() {
                scns.insert(s);
            }
            let f = t.get("feature");
            if !f.is_empty() {
                feats.insert(f);
            }
        }
    }
    (scns, feats)
}

/// Every check of one test dataset in the chain: provenance and author independence.
pub fn dataset_gaps(ctx: &Ctx, d: &Record) -> Vec<Gap> {
    let mut g = provenance_gaps(ctx, d);
    let (scns, feats) = dataset_contexts(ctx.store, d);
    if scns.is_empty() && feats.is_empty() {
        return g;
    }
    let mut imps = vec![];
    let mut e2e = vec![];
    for s in &scns {
        let f = ctx
            .store
            .get(s)
            .and_then(|r| feature_of_scenario(ctx.store, r))
            .unwrap_or_default();
        imps.extend(implementers(ctx, &f, s));
        e2e.extend(e2e_authors(ctx, s));
    }
    for f in &feats {
        imps.extend(implementers(ctx, f, ""));
    }
    g.extend(independence_gaps(ctx, d, &imps, &e2e));
    dedup_gaps(g)
}

// ------------------------------------------------------------------------------------------------ the chain

/// The chain of one scenario, with every gap on it (scenario-level, requirement-level and dataset-level).
pub fn scenario_chain(ctx: &Ctx, s: &Record) -> (Value, Vec<Gap>) {
    let store = ctx.store;
    let sid = s.id();
    let mut gaps = vec![];
    let feature = feature_of_scenario(store, s);
    if feature.is_none() {
        gaps.push(Gap::on(s, "low", "SCENARIO_WITHOUT_FEATURE", format!("scenario {sid} realises no feature (neither `feature` nor any feature's `scenarios`)")));
    }
    if !present(s.data.get("success_criteria")) {
        gaps.push(Gap::on(s, "medium", "SCENARIO_WITHOUT_SUCCESS_CRITERIA", format!("scenario {sid} records no success criteria (Contract v3 H4 FEATURE → SCENARIOS → DATA → TEST DATA → SUCCESS/FAILURE)")));
    }
    if !present(s.data.get("failure_criteria")) {
        gaps.push(Gap::on(
            s,
            "medium",
            "SCENARIO_WITHOUT_FAILURE_CRITERIA",
            format!("scenario {sid} records no failure criteria (Contract v3 H4)"),
        ));
    }
    let na = s.get("data_requirements_not_applicable");
    let reqs = list(s, "data_requirements");
    if reqs.is_empty() && na.trim().is_empty() {
        gaps.push(Gap::on(s, "medium", "SCENARIO_DATA_UNDECLARED", format!("scenario {sid} declares no data requirements and no reasoned `data_requirements_not_applicable` (a silent N/A is a gap)")));
    }
    let mut req_view = vec![];
    let mut datasets: BTreeSet<String> = BTreeSet::new();
    for e in &reqs {
        if !crate::records::id_regex().is_match(e) {
            gaps.push(Gap::on(s, "medium", "DATA_REQUIREMENT_NOT_GOVERNED", format!("scenario {sid}: data requirement '{e}' is free text, not a governed data record, so no test data can be traced to it")));
            req_view.push(json!({"entry": e, "resolved": false}));
            continue;
        }
        match store.get(e) {
            None => {
                gaps.push(Gap::on(
                    s,
                    "medium",
                    "DATA_REQUIREMENT_UNRESOLVED",
                    format!("scenario {sid}: data requirement {e} does not exist"),
                ));
                req_view.push(json!({"entry": e, "resolved": false}));
            }
            Some(r) if r.rtype() != "data" => {
                gaps.push(Gap::on(
                    s,
                    "medium",
                    "DATA_REQUIREMENT_WRONG_TYPE",
                    format!(
                        "scenario {sid}: data requirement {e} is a {} record, not data",
                        r.rtype()
                    ),
                ));
                req_view.push(json!({"entry": e, "resolved": false, "type": r.rtype()}));
            }
            Some(r) => {
                let tds = test_datasets_for(store, e);
                if tds.is_empty() {
                    gaps.push(Gap::on(r, "medium", "DATA_REQUIREMENT_WITHOUT_TEST_DATA", format!("data requirement {e} (of scenario {sid}) has no test dataset designed for it: no data record realises it (`implements: [{e}]`)")));
                }
                datasets.extend(tds.iter().cloned());
                req_view.push(json!({"entry": e, "resolved": true, "kind": data_kind(store, r), "test_datasets": tds}));
            }
        }
    }
    let tests = tests_of_scenario(store, &sid);
    let mut tests_view = vec![];
    if tests.is_empty() {
        gaps.push(Gap::on(
            s,
            "medium",
            "SCENARIO_WITHOUT_TEST",
            format!("scenario {sid} has no test obligation (`scenario: {sid}`)"),
        ));
    } else if !tests.iter().any(|t| independent_test(ctx, t)) {
        gaps.push(Gap::on(s, "medium", "SCENARIO_WITHOUT_INDEPENDENT_TEST", format!(
            "scenario {sid} has no independent test (a test obligation of a family in {:?} with independent_of_implementer: true)", ctx.independent_families
        )));
    }
    for t in &tests {
        let (ids, text) = test_data_of(store, t);
        gaps.extend(test_gaps(ctx, t, Some(s)));
        datasets.extend(ids.iter().cloned());
        tests_view.push(json!({"id": t.id(), "family": t.get("family"), "independent": independent_test(ctx, t), "test_data": ids, "data_provenance_text": text, "author": authorship_of(ctx, t).to_value()}));
    }
    let mut ds_view = vec![];
    for id in &datasets {
        if let Some(d) = store.get(id) {
            let g = dataset_gaps(ctx, d);
            ds_view.push(json!({"id": id, "kind": data_kind(store, d), "realises": realised_requirements(d), "provenance": d.data.get("provenance"),
                "authorship": authorship_of(ctx, d).to_value(), "gaps": g.iter().map(|x| x.to_value()).collect::<Vec<_>>()}));
            gaps.extend(g);
        }
    }
    let gaps = dedup_gaps(gaps);
    let imps = implementers(ctx, feature.as_deref().unwrap_or(""), &sid);
    let view = json!({"scenario": sid, "feature": feature, "success_criteria": s.data.get("success_criteria"), "failure_criteria": s.data.get("failure_criteria"),
        "data_requirements": req_view, "data_requirements_not_applicable": if na.is_empty() { Value::Null } else { json!(na) },
        "test_datasets": ds_view, "tests": tests_view, "implementers": imps.iter().map(|a| a.to_value()).collect::<Vec<_>>(),
        "gaps": gaps.iter().map(|g| g.to_value()).collect::<Vec<_>>(), "complete": gaps.iter().all(|g| g.severity == "low")});
    (view, gaps)
}

/// Test-level gaps: an independent-family test must say which test data it uses, and that data should realise its
/// scenario's data requirements.
pub fn test_gaps(ctx: &Ctx, t: &Record, scenario: Option<&Record>) -> Vec<Gap> {
    let mut g = vec![];
    if !ctx.independent_families.contains(&t.get("family")) {
        return g;
    }
    let tid = t.id();
    let (ids, text) = test_data_of(ctx.store, t);
    let na = scenario
        .map(|s| !s.get("data_requirements_not_applicable").trim().is_empty())
        .unwrap_or(false);
    if ids.is_empty() {
        match text {
            Some(tx) => g.push(Gap::on(t, "low", "TEST_DATA_NOT_GOVERNED", format!(
                "test {tid} ({}) describes its data provenance ('{tx}') but names no governed test dataset, so that provenance and its author's independence cannot be checked (`test_data: [<id>]`)",
                t.get("family")
            ))),
            None if !na => g.push(Gap::on(t, "medium", "TEST_DATA_UNDECLARED", format!(
                "test {tid} ({}) declares no test data and no data provenance (Contract v3 H4 'Data provenance is recorded')",
                t.get("family")
            ))),
            None => {}
        }
    }
    if let Some(s) = scenario {
        let reqs = list(s, "data_requirements");
        if !reqs.is_empty() {
            for id in &ids {
                if let Some(d) = ctx.store.get(id) {
                    if !realised_requirements(d).iter().any(|x| reqs.contains(x)) {
                        g.push(Gap::on(t, "low", "TEST_DATA_NOT_FOR_SCENARIO", format!(
                            "test {tid} uses {id}, which realises none of scenario {}'s data requirements {reqs:?}",
                            s.id()
                        )));
                    }
                }
            }
        }
    }
    g
}

/// `gov scenario trace <feature|scenario>`: the chain as the records carry it, with every gap.
pub fn trace(ctx: &Ctx, id: &str) -> Result<Value> {
    let r = ctx
        .store
        .get(id)
        .ok_or_else(|| GovError::new("NOT_FOUND", format!("{id} not found")))?;
    match r.rtype().as_str() {
        "scenario" => Ok(scenario_chain(ctx, r).0),
        "feature" => {
            let scns = scenarios_of_feature(ctx.store, r);
            let mut out = vec![];
            let mut gaps: Vec<Value> = vec![];
            if scns.is_empty() {
                gaps.push(
                    Gap::on(
                        r,
                        "low",
                        "FEATURE_WITHOUT_SCENARIOS",
                        format!("feature {id} has no scenarios"),
                    )
                    .to_value(),
                );
            }
            for s in &scns {
                match ctx.store.get(s) {
                    Some(sr) if sr.rtype() == "scenario" => {
                        let (v, _) = scenario_chain(ctx, sr);
                        gaps.extend(v["gaps"].as_array().cloned().unwrap_or_default());
                        out.push(v);
                    }
                    _ => gaps.push(
                        Gap::on(
                            r,
                            "medium",
                            "SCENARIO_UNRESOLVED",
                            format!("feature {id} names scenario {s}, which does not exist"),
                        )
                        .to_value(),
                    ),
                }
            }
            let complete = gaps.iter().all(|g| g["severity"] == "low");
            Ok(json!({"feature": id, "scenarios": out, "gaps": gaps, "complete": complete}))
        }
        other => Err(GovError::new(
            "USAGE",
            format!("{id} is a {other} record; trace a feature or a scenario"),
        )),
    }
}

/// The H4 family of [`super::suite_findings`]: every current scenario's chain, every independent-family test's data,
/// and every test dataset's provenance and author independence.
pub fn findings(ctx: &Ctx) -> Vec<Value> {
    let mut gaps: Vec<Gap> = vec![];
    for f in ctx.store.of_type("feature") {
        if is_current(f) && scenarios_of_feature(ctx.store, f).is_empty() {
            gaps.push(Gap::on(
                f,
                "low",
                "FEATURE_WITHOUT_SCENARIOS",
                format!("feature {} has no scenarios", f.id()),
            ));
        }
    }
    for s in ctx.store.of_type("scenario") {
        if is_current(s) {
            gaps.extend(scenario_chain(ctx, s).1);
        }
    }
    for t in ctx.store.of_type("test-obligation") {
        if is_current(t) && t.get("scenario").is_empty() && list(t, "scenarios").is_empty() {
            gaps.extend(test_gaps(ctx, t, None));
            for id in test_data_of(ctx.store, t).0 {
                if let Some(d) = ctx.store.get(&id) {
                    gaps.extend(dataset_gaps(ctx, d));
                }
            }
        }
    }
    dedup_gaps(gaps).into_iter().map(|g| g.to_value()).collect()
}

/// Gap codes that stand in the way of implementing a scenario (for READY gating; integration point `dag.rs`, WS-5).
pub const PRE_IMPLEMENTATION_CODES: &[&str] = &[
    "SCENARIO_WITHOUT_SUCCESS_CRITERIA",
    "SCENARIO_WITHOUT_FAILURE_CRITERIA",
    "SCENARIO_DATA_UNDECLARED",
    "DATA_REQUIREMENT_NOT_GOVERNED",
    "DATA_REQUIREMENT_UNRESOLVED",
    "DATA_REQUIREMENT_WRONG_TYPE",
    "DATA_REQUIREMENT_WITHOUT_TEST_DATA",
    "TEST_DATA_WITHOUT_PROVENANCE",
    "TEST_DATA_PROVENANCE_INVALID",
    "TEST_DATA_PROVENANCE_UNSTRUCTURED",
    "TEST_DATA_REAL_DATA_UNAPPROVED",
    "TEST_DATA_UNDECLARED",
    "DATA_AUTHOR_NOT_INDEPENDENT",
    "DATA_AUTHOR_IS_TEST_AUTHOR",
];

/// **READY gating input (integration point: `orchestration::dag::compute`, WS-5).** Why an implementation-class
/// task's scenario chain is not ready: each gap of [`PRE_IMPLEMENTATION_CODES`] on the scenarios it implements (its
/// `scenarios`, else its feature's).
pub fn implementation_blockers(ctx: &Ctx, task: &Record) -> Vec<String> {
    if !IMPLEMENTATION_CLASSES.contains(&task.get("class").as_str()) {
        return vec![];
    }
    let mut scns: BTreeSet<String> = list(task, "scenarios").into_iter().collect();
    if scns.is_empty() {
        if let Some(f) = ctx.store.get(&task.get("feature")) {
            scns.extend(scenarios_of_feature(ctx.store, f));
        }
    }
    let mut out = vec![];
    for s in scns {
        if let Some(sr) = ctx.store.get(&s).filter(|x| x.rtype() == "scenario") {
            for g in scenario_chain(ctx, sr).1 {
                if PRE_IMPLEMENTATION_CODES.contains(&g.code) {
                    out.push(format!("{}: {}", g.code, g.message));
                }
            }
        }
    }
    out.sort();
    out.dedup();
    out
}

/// **Readiness cells computed from the chain (integration point: `orchestration::readiness::evaluate`, WS-5)** for
/// `success_criteria`, `failure_criteria`, `representative_test_data` and `independent_acceptance_tests`, instead of
/// the author-asserted cell values.
pub fn readiness_cells(ctx: &Ctx, feature: &Record) -> Value {
    let scns: Vec<&Record> = scenarios_of_feature(ctx.store, feature)
        .iter()
        .filter_map(|s| ctx.store.get(s))
        .filter(|s| s.rtype() == "scenario")
        .collect();
    let mut cells: BTreeMap<&str, Vec<String>> = BTreeMap::new();
    for k in [
        "success_criteria",
        "failure_criteria",
        "representative_test_data",
        "independent_acceptance_tests",
    ] {
        cells.insert(k, vec![]);
    }
    for s in &scns {
        for g in scenario_chain(ctx, s).1 {
            let cell = match g.code {
                "SCENARIO_WITHOUT_SUCCESS_CRITERIA" => "success_criteria",
                "SCENARIO_WITHOUT_FAILURE_CRITERIA" => "failure_criteria",
                "SCENARIO_WITHOUT_TEST" | "SCENARIO_WITHOUT_INDEPENDENT_TEST" => {
                    "independent_acceptance_tests"
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
                | "TEST_DATA_CHANGED" => "representative_test_data",
                _ => continue,
            };
            cells
                .get_mut(cell)
                .unwrap()
                .push(format!("{}: {}", g.code, g.message));
        }
    }
    let mut out = Map::new();
    for (k, why) in cells {
        let state = if scns.is_empty() {
            "MISSING"
        } else if why.is_empty() {
            "PRESENT"
        } else {
            "MISSING"
        };
        out.insert(k.to_string(), json!({"state": state, "computed_from": "scenario chain (runtime/src/lifecycle/scenario.rs)", "reasons": if scns.is_empty() { vec![format!("feature {} has no scenarios", feature.id())] } else { why }}));
    }
    Value::Object(out)
}

// ------------------------------------------------------------------------------------------------ commands

/// `gov data register`: record a data requirement or a test dataset. A test dataset names the requirement(s) it
/// realises (`implements`), records structured provenance (and, for real data, the approving human decision), may
/// bind its `location` by SHA-256, and carries the OS authorship stamp of the registering role and session
/// (T2-sealed). A registering session or role that implements one of the scenarios the dataset serves — or authors
/// their end-to-end tests — is refused unless the owner waived independence.
pub fn register(p: &Project, fields: Value) -> Result<Value> {
    control::guard_write(p, "data register")?;
    authority::require(p, super::RECORD_AUTHORITY)?;
    refuse_os_owned(&fields, &[])?;
    let store = RecordStore::load(&p.root);
    let mut o: Map<String, Value> = match fields {
        Value::Object(m) => m,
        _ => {
            return Err(GovError::new(
                "USAGE",
                "--fields must be a JSON/YAML object",
            ))
        }
    };
    if let Some(t) = o.remove("type") {
        if t != "data" {
            return Err(GovError::new(
                "USAGE",
                "gov data register writes data records (type: data)",
            ));
        }
    }
    let kind = o
        .get("data_kind")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    if !DATA_KINDS.contains(&kind.as_str()) {
        return Err(GovError::new(
            "USAGE",
            format!("data_kind must be one of {DATA_KINDS:?}"),
        ));
    }
    let id = o
        .remove("id")
        .and_then(|v| v.as_str().map(String::from))
        .unwrap_or_else(|| {
            let ids: Vec<String> = store.records.iter().map(|r| r.id()).collect();
            crate::util::next_id(if kind == "requirement" { "DATA" } else { "TD" }, &ids, 4)
        });
    if !crate::records::id_regex().is_match(&id) {
        return Err(GovError::new("USAGE", format!("'{id}' is not a record id")));
    }
    if store.get(&id).is_some() {
        return Err(GovError::new(
            "DUPLICATE_ID",
            format!("{id} already exists"),
        ));
    }
    let title = o
        .remove("title")
        .and_then(|v| v.as_str().map(String::from))
        .unwrap_or_else(|| format!("{kind} {id}"));
    let mut rec = new_record("data", &id, &title, json!({}));
    if kind == "requirement" {
        if !present(o.get("description")) {
            return Err(GovError::new(
                "DATA_REQUIREMENT_INCOMPLETE",
                format!("data requirement {id} records what data is needed (`description`)"),
            ));
        }
    } else {
        let reqs: Vec<String> = ids_in(o.get("implements"));
        if reqs.is_empty() {
            return Err(GovError::new("DATA_CHAIN_INCOMPLETE", format!("test dataset {id} names the data requirement(s) it realises (`implements: [DATA-…]`, Contract v3 H4 DATA → TEST DATA)")));
        }
        for r in &reqs {
            match store.get(r) {
                None => return Err(GovError::new("DATA_REFERENCE_UNKNOWN", format!("{r} is not a governed record"))),
                Some(x) if x.rtype() != "data" || data_kind(&store, x) == "test-dataset" => {
                    return Err(GovError::new("DATA_NOT_A_REQUIREMENT", format!("{r} is not a data requirement (a `data` record of data_kind requirement, or one a scenario names in `data_requirements`)")))
                }
                _ => {}
            }
        }
        let prov = o.get("provenance").cloned().unwrap_or(Value::Null);
        let sk = prov["source_kind"].as_str().unwrap_or("");
        if !prov.is_object() || !SOURCE_KINDS.contains(&sk) || !present(prov.get("origin")) {
            return Err(GovError::new("DATA_PROVENANCE_REQUIRED", format!(
                "test dataset {id} records provenance {{source_kind: one of {SOURCE_KINDS:?}, origin: where it came from / how it was generated}} (Contract v3 H4; framework §39 'Provenance must be recorded')"
            )));
        }
        if sk == "approved-real" {
            let approval = prov["approval"].as_str().unwrap_or("");
            let dec = crate::orchestration::gates::verified_decision(p, approval).map_err(|e| {
                GovError::new(
                    "DATA_REAL_DATA_UNAPPROVED",
                    format!(
                        "real data needs an approving human decision (provenance.approval): {}",
                        e.message
                    ),
                )
            })?;
            if !dec
                .data
                .get("human_approved")
                .and_then(|v| v.as_bool())
                .unwrap_or(false)
            {
                return Err(GovError::new(
                    "DATA_REAL_DATA_UNAPPROVED",
                    format!("decision {approval} is not a human approval"),
                ));
            }
        }
        if let Some(w) = o.get("independence_waiver") {
            let dec = w
                .get("decision")
                .and_then(|v| v.as_str())
                .or(w.as_str())
                .unwrap_or("");
            let d = crate::orchestration::gates::verified_decision(p, dec)?;
            if !d
                .data
                .get("human_approved")
                .and_then(|v| v.as_bool())
                .unwrap_or(false)
            {
                return Err(GovError::new(
                    "DATA_WAIVER_UNAPPROVED",
                    format!("independence_waiver {dec} is not an owner-approved decision"),
                ));
            }
        }
        // bind the content where the dataset lives
        let locs: Vec<String> = match o.get("location") {
            Some(Value::String(s)) => vec![s.clone()],
            Some(Value::Array(a)) => a
                .iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect(),
            _ => vec![],
        };
        let mut hashes = Map::new();
        for l in &locs {
            let rel = safe_rel_path(l)?;
            let h = hash_path(&p.root, &rel).ok_or_else(|| {
                GovError::new(
                    "DATA_LOCATION_MISSING",
                    format!("location '{l}' does not exist in the repository"),
                )
            })?;
            hashes.insert(l.clone(), json!(h));
        }
        let mut prov = prov;
        if !hashes.is_empty() {
            prov["content_sha256"] = if hashes.len() == 1 {
                hashes.values().next().cloned().unwrap()
            } else {
                Value::Object(hashes)
            };
            prov["bound_at"] = json!(crate::util::now_iso());
        }
        o.insert("provenance".into(), prov);
        o.insert("implements".into(), json!(reqs));
    }
    for (k, v) in o {
        rec.set(&k, v);
    }
    rec.set("authorship", stamp(p, "data register"));
    // the registering author against the implementers and end-to-end test authors of the scenarios served
    if kind == "test-dataset" {
        let ctx = Ctx::new(p, &store);
        let reqs = realised_requirements(&rec);
        let mut imps = vec![];
        let mut e2e = vec![];
        for s in store.of_type("scenario") {
            if list(s, "data_requirements")
                .iter()
                .any(|x| reqs.contains(x))
            {
                let f = feature_of_scenario(&store, s).unwrap_or_default();
                imps.extend(implementers(&ctx, &f, &s.id()));
                e2e.extend(e2e_authors(&ctx, &s.id()));
            }
        }
        let me_role = Some(p.role.clone());
        let me_session = Some(p.session_id.clone());
        let clash: Vec<String> = imps
            .iter()
            .filter(|a| {
                (a.role.is_some() && a.role == me_role)
                    || (a.session.is_some() && a.session == me_session)
            })
            .map(|a| format!("implementer: {}", a.via))
            .chain(
                e2e.iter()
                    .filter(|(_, a)| {
                        (a.role.is_some() && a.role == me_role)
                            || (a.session.is_some() && a.session == me_session)
                    })
                    .map(|(t, _)| format!("end-to-end test author of {t}")),
            )
            .collect();
        let waived = waiver(&ctx, &rec).is_some();
        if !clash.is_empty() && !waived {
            return Err(GovError::new("DATA_AUTHOR_NOT_INDEPENDENT", format!(
                "{} (session {}) may not author test dataset {id}: it is {clash:?} of the scenario(s) this data serves; the data author must be independent of the implementation author and the end-to-end test author (framework §39; Contract v3:526). Register it as an independent role/session (e.g. data-author), or attach an owner-approved `independence_waiver: {{decision: D-…}}`.",
                p.role, p.session_id
            )).with_details(json!({"dataset": id, "role": p.role, "session": p.session_id, "conflicts": clash})));
        }
    }
    validate_seal_save(p, &mut rec, "data register")?;
    let store2 = RecordStore::load(&p.root);
    let ctx2 = Ctx::new(p, &store2);
    let gaps: Vec<Value> = store2
        .get(&id)
        .map(|r| {
            if kind == "test-dataset" {
                dataset_gaps(&ctx2, r)
                    .iter()
                    .map(|g| g.to_value())
                    .collect()
            } else {
                vec![]
            }
        })
        .unwrap_or_default();
    Ok(json!({"data": rec.data, "gaps": gaps}))
}

/// `gov data show <id>`: kind, provenance, authorship, what it realises and which tests use it, and its gaps.
pub fn show(p: &Project, id: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let ctx = Ctx::new(p, &store);
    let d = store
        .get(id)
        .ok_or_else(|| GovError::new("NOT_FOUND", format!("{id} not found")))?;
    if d.rtype() != "data" {
        return Err(GovError::new(
            "USAGE",
            format!("{id} is a {} record, not data", d.rtype()),
        ));
    }
    let used_by: Vec<String> = store
        .of_type("test-obligation")
        .into_iter()
        .filter(|t| test_data_of(&store, t).0.contains(&d.id()))
        .map(|t| t.id())
        .collect();
    let (scns, _) = dataset_contexts(&store, d);
    let kind = data_kind(&store, d);
    let gaps: Vec<Value> = if kind == "requirement" {
        if test_datasets_for(&store, id).is_empty() {
            vec![Gap::on(
                d,
                "medium",
                "DATA_REQUIREMENT_WITHOUT_TEST_DATA",
                format!("data requirement {id} has no test dataset designed for it"),
            )
            .to_value()]
        } else {
            vec![]
        }
    } else {
        dataset_gaps(&ctx, d).iter().map(|g| g.to_value()).collect()
    };
    Ok(
        json!({"data": d.data, "kind": kind, "realises": realised_requirements(d), "test_datasets": if kind == "requirement" { json!(test_datasets_for(&store, id)) } else { Value::Null },
        "used_by_tests": used_by, "scenarios": scns, "authorship": authorship_of(&ctx, d).to_value(),
        "t2": crate::t2::verify_record(d).to_value(), "gaps": gaps}),
    )
}

/// `gov scenario trace <id>`.
pub fn trace_cmd(p: &Project, id: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let ctx = Ctx::new(p, &store);
    trace(&ctx, id)
}

/// `gov scenario check`: every chain gap in the project.
pub fn check(p: &Project) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let ctx = Ctx::new(p, &store);
    let f = findings(&ctx);
    let blocking = f.iter().filter(|x| x["severity"] != "low").count();
    Ok(json!({"family": super::FAMILY, "findings": f, "ok": blocking == 0}))
}

#[cfg(test)]
mod tests {
    use super::super::testkit::*;
    use super::*;

    /// gamma-r H4's fixture shape: a complete chain in the product's own fields except where each test breaks it.
    fn chain(fx: &Fx) {
        fx.put("spec/features/F-0001.yaml", json!({"id": "F-0001", "type": "feature", "status": "ACTIVE", "scenarios": ["SCN-0001"], "readiness": {}}));
        fx.put("spec/scenarios/SCN-0001.yaml", json!({"id": "SCN-0001", "type": "scenario", "status": "ACTIVE", "feature": "F-0001",
            "data_requirements": ["DATA-0001"], "success_criteria": ["exact integer total"], "failure_criteria": ["duplicate ids accepted"]}));
        fx.put("spec/data/DATA-0001.yaml", json!({"id": "DATA-0001", "type": "data", "status": "ACTIVE", "data_kind": "requirement", "description": "order lines"}));
        fx.file("tests/data/orders.csv", "id,cents\n1,199\n2,200\n");
        let h = crate::util::sha256_file(&fx.dir.join("tests/data/orders.csv")).unwrap();
        fx.put("spec/data/TD-0001.yaml", json!({"id": "TD-0001", "type": "data", "status": "ACTIVE", "data_kind": "test-dataset", "implements": ["DATA-0001"],
            "location": "tests/data/orders.csv", "provenance": {"source_kind": "synthetic", "origin": "generated by gen_orders.py seed 7", "content_sha256": h},
            "authorship": {"role": "data-author", "session": "S-da"}, "os_binding": {"test": "verified"}}));
        fx.put("spec/tasks/TST-0001.yaml", json!({"id": "TST-0001", "type": "test-obligation", "status": "ACTIVE", "feature": "F-0001", "scenario": "SCN-0001", "family": "acceptance",
            "independent_of_implementer": true, "author_role": "independent-test-designer", "test_data": ["TD-0001"]}));
        fx.put("spec/tasks/TASK-0001.yaml", json!({"id": "TASK-0001", "type": "task", "status": "ACTIVE", "class": "implementation", "task_status": "READY", "objective": "o", "feature": "F-0001", "role": "backend-engineer"}));
    }

    fn codes(gaps: &[Gap]) -> Vec<&'static str> {
        let mut v: Vec<&'static str> = gaps.iter().map(|g| g.code).collect();
        v.sort();
        v.dedup();
        v
    }

    #[test]
    fn a_complete_chain_has_no_gaps_and_computes_present_cells() {
        let fx = Fx::new("h4ok");
        chain(&fx);
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &[]);
        let (v, gaps) = scenario_chain(&c, s.get("SCN-0001").unwrap());
        assert!(gaps.is_empty(), "{gaps:?}");
        assert_eq!(v["complete"], true);
        assert_eq!(
            v["data_requirements"][0]["test_datasets"],
            json!(["TD-0001"])
        );
        let cells = readiness_cells(&c, s.get("F-0001").unwrap());
        for k in [
            "success_criteria",
            "failure_criteria",
            "representative_test_data",
            "independent_acceptance_tests",
        ] {
            assert_eq!(cells[k]["state"], "PRESENT", "{k}: {cells}");
        }
        assert!(implementation_blockers(&c, s.get("TASK-0001").unwrap()).is_empty());
    }

    #[test]
    fn every_missing_link_is_a_typed_gap() {
        let fx = Fx::new("h4gap");
        chain(&fx);
        // the gamma-r H4 fixture: requirement and dataset unlinked, dataset authored by the implementer role and
        // without provenance, the test naming it only in free text; and a second scenario missing everything
        fx.put("spec/data/TD-0001.yaml", json!({"id": "TD-0001", "type": "data", "status": "ACTIVE", "author_role": "backend-engineer"}));
        fx.put("spec/tasks/TST-0001.yaml", json!({"id": "TST-0001", "type": "test-obligation", "status": "ACTIVE", "feature": "F-0001", "scenario": "SCN-0001", "family": "acceptance",
            "independent_of_implementer": true, "data_provenance": "TD-0001 (synthetic, generated)"}));
        fx.put("spec/tasks/TST-0002.yaml", json!({"id": "TST-0002", "type": "test-obligation", "status": "ACTIVE", "feature": "F-0001", "scenario": "SCN-0001", "family": "acceptance", "independent_of_implementer": true}));
        fx.put("spec/scenarios/SCN-0002.yaml", json!({"id": "SCN-0002", "type": "scenario", "status": "ACTIVE", "feature": "F-0001", "data_requirements": ["order history", "DATA-0404"]}));
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &[]);
        let (_, g1) = scenario_chain(&c, s.get("SCN-0001").unwrap());
        assert_eq!(
            codes(&g1),
            vec![
                "DATA_AUTHORSHIP_NOT_ESTABLISHED",
                "DATA_AUTHOR_NOT_INDEPENDENT",
                "DATA_REQUIREMENT_WITHOUT_TEST_DATA",
                "TEST_DATA_NOT_FOR_SCENARIO",
                "TEST_DATA_UNDECLARED",
                "TEST_DATA_WITHOUT_PROVENANCE"
            ]
        );
        let (_, g2) = scenario_chain(&c, s.get("SCN-0002").unwrap());
        assert_eq!(
            codes(&g2),
            vec![
                "DATA_REQUIREMENT_NOT_GOVERNED",
                "DATA_REQUIREMENT_UNRESOLVED",
                "SCENARIO_WITHOUT_FAILURE_CRITERIA",
                "SCENARIO_WITHOUT_SUCCESS_CRITERIA",
                "SCENARIO_WITHOUT_TEST"
            ]
        );
        let cells = readiness_cells(&c, s.get("F-0001").unwrap());
        assert_eq!(cells["success_criteria"]["state"], "MISSING");
        assert_eq!(cells["representative_test_data"]["state"], "MISSING");
        let b = implementation_blockers(&c, s.get("TASK-0001").unwrap());
        assert!(
            b.iter()
                .any(|x| x.starts_with("DATA_AUTHOR_NOT_INDEPENDENT")),
            "{b:?}"
        );
        // the suite view names each record
        let f = findings(&c);
        assert!(f
            .iter()
            .any(|x| x["record"] == "TST-0002" && x["code"] == "TEST_DATA_UNDECLARED"));
        assert!(f
            .iter()
            .any(|x| x["record"] == "TD-0001" && x["code"] == "TEST_DATA_WITHOUT_PROVENANCE"));
    }

    #[test]
    fn provenance_is_read_real_data_needs_approval_and_changes_are_detected() {
        let fx = Fx::new("h4prov");
        chain(&fx);
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &["D-0007"]);
        assert!(provenance_gaps(&c, s.get("TD-0001").unwrap()).is_empty());
        let mut real = s.get("TD-0001").unwrap().clone();
        real.data["provenance"]["source_kind"] = json!("approved-real");
        real.data["provenance"]["approval"] = json!("D-0404");
        assert_eq!(
            codes(&provenance_gaps(&c, &real)),
            vec!["TEST_DATA_REAL_DATA_UNAPPROVED"]
        );
        real.data["provenance"]["approval"] = json!("D-0007");
        assert!(provenance_gaps(&c, &real).is_empty());
        real.data["provenance"]["source_kind"] = json!("scraped");
        assert_eq!(
            codes(&provenance_gaps(&c, &real)),
            vec!["TEST_DATA_PROVENANCE_INVALID"]
        );
        fx.file("tests/data/orders.csv", "id,cents\n1,199\n2,201\n");
        let s2 = fx.store();
        let c2 = ctx(&s2, &fx.dir, &[]);
        assert_eq!(
            codes(&provenance_gaps(&c2, s2.get("TD-0001").unwrap())),
            vec!["TEST_DATA_CHANGED"]
        );
    }

    #[test]
    fn data_author_independence_uses_recorded_authorship_and_honours_only_an_approved_waiver() {
        let fx = Fx::new("h4ind");
        chain(&fx);
        // closed implementation task: its closing session authored the dataset
        fx.put("spec/reports/RPT-0001.yaml", json!({"id": "RPT-0001", "type": "report", "status": "ACTIVE", "task": "TASK-0001", "role": "backend-engineer", "session": "S-impl", "observed_files_changed": ["src/lib.rs"]}));
        fx.put("spec/tasks/TASK-0001.yaml", json!({"id": "TASK-0001", "type": "task", "status": "ACTIVE", "class": "implementation", "task_status": "DONE", "objective": "o", "feature": "F-0001", "role": "backend-engineer", "closed_by_report": "RPT-0001"}));
        let td = |auth: Value, waiver: Value| {
            let mut v = json!({"id": "TD-0001", "type": "data", "status": "ACTIVE", "data_kind": "test-dataset", "implements": ["DATA-0001"],
                "provenance": {"source_kind": "synthetic", "origin": "generated"}, "authorship": auth, "os_binding": {"test": "verified"}});
            if !waiver.is_null() {
                v["independence_waiver"] = waiver;
            }
            v
        };
        fx.put(
            "spec/data/TD-0001.yaml",
            td(
                json!({"role": "data-author", "session": "S-impl"}),
                Value::Null,
            ),
        );
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &["D-0009"]);
        let g = dataset_gaps(&c, s.get("TD-0001").unwrap());
        assert!(
            g.iter()
                .any(|x| x.code == "DATA_AUTHOR_NOT_INDEPENDENT"
                    && x.message.contains("same session")),
            "{g:?}"
        );
        fx.put(
            "spec/data/TD-0001.yaml",
            td(
                json!({"role": "independent-test-designer", "session": "S-da"}),
                Value::Null,
            ),
        );
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &["D-0009"]);
        assert_eq!(
            codes(&dataset_gaps(&c, s.get("TD-0001").unwrap())),
            vec!["DATA_AUTHOR_IS_TEST_AUTHOR"]
        );
        fx.put(
            "spec/data/TD-0001.yaml",
            td(
                json!({"role": "backend-engineer", "session": "S-x"}),
                json!({"decision": "D-0404"}),
            ),
        );
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &["D-0009"]);
        assert_eq!(
            codes(&dataset_gaps(&c, s.get("TD-0001").unwrap())),
            vec!["DATA_AUTHOR_NOT_INDEPENDENT"],
            "an unverified waiver is not a waiver"
        );
        fx.put(
            "spec/data/TD-0001.yaml",
            td(
                json!({"role": "backend-engineer", "session": "S-x"}),
                json!({"decision": "D-0009"}),
            ),
        );
        let s = fx.store();
        let c = ctx(&s, &fx.dir, &["D-0009"]);
        assert!(dataset_gaps(&c, s.get("TD-0001").unwrap()).is_empty());
    }
}
