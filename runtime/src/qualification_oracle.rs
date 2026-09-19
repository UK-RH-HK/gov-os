//! Qualification Oracle format — Contract v3 Gate V (V1-V4), a machine-checkable definition and its validator.
//!
//! Contract v3:1012-1062 requires every sophisticated qualification repository to have a **verifier-owned hidden
//! oracle** — a fault manifest (V1), a hidden path-map oracle for the brownfield repository (V2), a hidden memory
//! oracle (V3) — and quantitative qualification scoring against it (V4); and "the permanent public qualification suite
//! and fresh verifier hidden oracle must remain separate". Contract v3:1206 then requires the oracle **format** to be
//! accepted before any hidden fault is generated.
//!
//! This module is that format's validator. It generates nothing: no fault, no oracle, no repository. The format
//! definition lives at [`DEFINITION_PATH`] — outside the public qualification suite and outside the kernel payload
//! directories installed into consumer projects — and is compiled into the binary so validation needs no checkout.
//!
//! * [`check_document`] applies the JSON Schema and the format's semantic rules to one document and returns every
//!   violation, each tagged with the Contract v3 element it concerns (e.g. `V1.6` "expected severity", line 1023).
//! * [`crosswalk`] proves the format covers **every** V1-V4 checklist item of the owner source (read from the approved
//!   bytes, not from memory), together with Gate V's custody and separation sentences, W12's G6 duty and the Gate W
//!   challenge's "the hidden oracle defines the correct required input/version and expected downstream propagation".
//! * [`validate_file`] adds what a single document cannot show: a score report's binding to the sealed oracle it was
//!   scored against, and the physical separation of a hidden oracle from the public suite and the qualification
//!   repository (the oracle may not be stored inside either, and no trace of it may be found in either).
//!
//! Refusals are typed: `ORACLE_RECORD_INVALID`, `ORACLE_SCORE_BINDING_MISMATCH`, `ORACLE_SEPARATION_VIOLATED`,
//! `ORACLE_RECORD_UNREADABLE`, `ORACLE_FORMAT_INCOMPLETE`.
use crate::util::{hash_value, sha256_text};
use crate::{GovError, Result};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

pub const FORMAT: &str = "governance-os.qualification-oracle";
pub const FORMAT_VERSION: u64 = 1;
/// The format definition: a JSON Schema (2020-12) plus the `x-contract-crosswalk` to the owner source.
pub const DEFINITION_PATH: &str = "framework/qualification-oracle/qualification-oracle.schema.json";
pub const DEFINITION: &str =
    include_str!("../../framework/qualification-oracle/qualification-oracle.schema.json");
pub const KIND_ORACLE: &str = "qualification-oracle";
pub const KIND_SCORE_REPORT: &str = "qualification-score-report";
/// Record types a governed repository might use for hidden-oracle material (for [`is_hidden_oracle_material`]).
pub const HIDDEN_ORACLE_RECORD_TYPES: &[&str] = &[
    "qualification-oracle",
    "fault-manifest",
    "path-map-oracle",
    "hidden-path-map-oracle",
    "memory-oracle",
    "hidden-memory-oracle",
];
/// Files larger than this are not scanned for leaked oracle material.
const MAX_SCAN_BYTES: u64 = 8 * 1024 * 1024;
/// A hidden authoritative truth statement at least this long found verbatim outside custody is a leak.
const MIN_TRUTH_SCAN_CHARS: usize = 32;
const RATIO_TOLERANCE: f64 = 1e-9;

/// SHA-256 of the format definition's bytes: the identity a reviewer accepts and every document names.
pub fn format_sha256() -> String {
    sha256_text(DEFINITION)
}

fn definition() -> Result<Value> {
    serde_json::from_str(DEFINITION).map_err(|e| {
        GovError::new(
            "ORACLE_FORMAT_INVALID",
            format!("{DEFINITION_PATH} is not JSON: {e}"),
        )
    })
}

/// One entry of the format's crosswalk to the owner source.
#[derive(Debug, Clone)]
pub struct CrosswalkEntry {
    /// A checklist item id (`V1.6`), a challenge id (`AQC-W12`) or `L<line>` for a non-checklist source line.
    pub element: String,
    pub kind: String,
    pub text: String,
    pub fields: Vec<String>,
    pub source_line: usize,
}

/// The crosswalk from the owner source to the format, **checked against the approved bytes**: every element's text
/// must be the source's text at that element, and every checklist item and every statement of V1-V4 and Gate V must
/// be mapped to a field. A format that misses one is refused (`ORACLE_FORMAT_INCOMPLETE`).
pub fn crosswalk() -> Result<Vec<CrosswalkEntry>> {
    let def = definition()?;
    let model = crate::contracts::embedded_model()?;
    let src: Vec<&str> = crate::contracts::EMBEDDED_SOURCE.lines().collect();
    let entries = def
        .get("x-contract-crosswalk")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default();
    let mut out = vec![];
    let mut problems: Vec<String> = vec![];
    for e in &entries {
        let element = e["element"].as_str().unwrap_or("").to_string();
        let kind = e["kind"].as_str().unwrap_or("").to_string();
        let text = e["text"].as_str().unwrap_or("").to_string();
        let fields: Vec<String> = e["fields"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default();
        if kind != KIND_ORACLE && kind != KIND_SCORE_REPORT {
            problems.push(format!("{element}: unknown document kind {kind:?}"));
        }
        if fields.is_empty() {
            problems.push(format!("{element}: maps to no field"));
        }
        let line_no = element
            .strip_prefix('L')
            .filter(|n| !n.is_empty() && n.chars().all(|c| c.is_ascii_digit()))
            .and_then(|n| n.parse::<usize>().ok());
        let source_line = if let Some(n) = line_no {
            if src.get(n.wrapping_sub(1)).copied() != Some(text.as_str()) {
                problems.push(format!(
                    "{element}: the owner source line {n} is not {text:?}"
                ));
            }
            n
        } else if let Some(it) = model.any_item(&element) {
            if it.text != text {
                problems.push(format!(
                    "{element}: the owner source item reads {:?}, not {text:?}",
                    it.text
                ));
            }
            it.line
        } else if let Some(ch) = model.challenges.iter().find(|c| c.id == element) {
            if !ch.text.contains(&text) {
                problems.push(format!("{element}: the challenge does not state {text:?}"));
            }
            ch.line
        } else {
            problems.push(format!("{element}: not an element of the owner source"));
            0
        };
        out.push(CrosswalkEntry {
            element,
            kind,
            text,
            fields,
            source_line,
        });
    }
    let mut required: Vec<(String, usize)> = vec![];
    for cap in ["V1", "V2", "V3", "V4"] {
        let Some(c) = model.capability(cap) else {
            problems.push(format!("the owner source has no {cap}"));
            continue;
        };
        required.extend(c.items.iter().map(|i| (i.id.clone(), i.line)));
        required.extend(
            c.statements
                .iter()
                .map(|s| (format!("L{}", s.line), s.line)),
        );
    }
    if let Some(g) = model.gates.iter().find(|g| g.id == "V") {
        required.extend(
            g.statements
                .iter()
                .map(|s| (format!("L{}", s.line), s.line)),
        );
    }
    for (id, line) in &required {
        if !out.iter().any(|e| &e.element == id) {
            problems.push(format!(
                "Contract v3:{line} ({id}) is not mapped to any field of the format"
            ));
        }
    }
    if !problems.is_empty() {
        return Err(GovError::new(
            "ORACLE_FORMAT_INCOMPLETE",
            format!(
                "the Qualification Oracle format does not cover the owner source's Gate V: {}",
                problems.join("; ")
            ),
        )
        .with_details(json!({"problems": problems, "definition": DEFINITION_PATH})));
    }
    Ok(out)
}

fn element_for<'a>(cw: &'a [CrosswalkEntry], kind: &str, path: &str) -> Option<&'a CrosswalkEntry> {
    let segs: Vec<&str> = path.split('/').filter(|s| !s.is_empty()).collect();
    let mut best: Option<(&CrosswalkEntry, usize)> = None;
    let known = kind == KIND_ORACLE || kind == KIND_SCORE_REPORT;
    for e in cw.iter().filter(|e| e.kind == kind || !known) {
        for f in &e.fields {
            let ps: Vec<&str> = f.split('/').filter(|s| !s.is_empty()).collect();
            if !ps.is_empty()
                && ps.len() <= segs.len()
                && ps.iter().zip(segs.iter()).all(|(p, s)| *p == "*" || p == s)
                && best.map(|b| ps.len() > b.1).unwrap_or(true)
            {
                best = Some((e, ps.len()));
            }
        }
    }
    best.map(|b| b.0)
}

struct Violations<'a> {
    kind: String,
    cw: &'a [CrosswalkEntry],
    list: Vec<Value>,
}

impl Violations<'_> {
    fn push(&mut self, at: &str, problem: impl Into<String>) {
        let mut o = Map::new();
        o.insert("at".into(), json!(if at.is_empty() { "/" } else { at }));
        o.insert("problem".into(), json!(problem.into()));
        if let Some(e) = element_for(self.cw, &self.kind, at) {
            o.insert("element".into(), json!(e.element));
            o.insert(
                "contract".into(),
                json!(format!("Contract v3:{} “{}”", e.source_line, e.text)),
            );
        }
        self.list.push(Value::Object(o));
    }
}

fn arr<'a>(v: &'a Value, ptr: &str) -> Vec<&'a Value> {
    v.pointer(ptr)
        .and_then(|x| x.as_array())
        .map(|a| a.iter().collect())
        .unwrap_or_default()
}

fn s<'a>(v: &'a Value, key: &str) -> Option<&'a str> {
    v.get(key).and_then(|x| x.as_str())
}

/// Validate one document against the format: the JSON Schema, the format digest it names, and the semantic rules of
/// its kind. Returns the kind and every violation (empty when the document conforms).
pub fn check_document(doc: &Value) -> Result<(String, Vec<Value>)> {
    let def = definition()?;
    let cw = crosswalk()?;
    let model = crate::contracts::embedded_model()?;
    let kind = s(doc, "kind").unwrap_or("").to_string();
    let mut v = Violations {
        kind: kind.clone(),
        cw: &cw,
        list: vec![],
    };
    let compiled = jsonschema::JSONSchema::options()
        .with_draft(jsonschema::Draft::Draft202012)
        .compile(&def)
        .map_err(|e| {
            GovError::new(
                "ORACLE_FORMAT_INVALID",
                format!("{DEFINITION_PATH} does not compile as JSON Schema 2020-12: {e}"),
            )
        })?;
    if let Err(errs) = compiled.validate(doc) {
        for e in errs {
            let base = e.instance_path.to_string();
            match &e.kind {
                jsonschema::error::ValidationErrorKind::Required { property } => {
                    let p = property.as_str().unwrap_or("");
                    v.push(
                        &format!("{base}/{p}"),
                        format!("required field '{p}' is missing"),
                    );
                }
                _ => v.push(&base, e.to_string()),
            }
        }
    }
    if let Some(d) = s(doc, "format_sha256") {
        if d != format_sha256() {
            v.push(
                "/format_sha256",
                format!("the document was written against format definition {d}; this is {} — a document is valid only against the exact (reviewed) format version it names", format_sha256()),
            );
        }
    }
    if kind == KIND_ORACLE {
        oracle_semantics(doc, &model, &mut v);
    } else if kind == KIND_SCORE_REPORT {
        report_semantics(doc, &mut v);
    } else {
        let v1: Vec<String> = cw
            .iter()
            .filter(|e| e.element.starts_with("V1."))
            .flat_map(|e| {
                e.fields
                    .iter()
                    .map(|f| f.rsplit('/').next().unwrap_or("").to_string())
            })
            .collect();
        v.push(
            "/kind",
            format!(
                "not a document of the Qualification Oracle format{}: the format has two kinds — '{KIND_ORACLE}' (V1 fault manifest, V2 hidden path-map oracle, V3 hidden memory oracle) and '{KIND_SCORE_REPORT}' (V4); every injected defect of a fault manifest records {}",
                s(doc, "type").map(|t| format!(" (a record of type {t:?})")).unwrap_or_default(),
                v1.join(", ")
            ),
        );
    }
    Ok((kind, v.list))
}

fn is_gate_w(cap: &str) -> bool {
    cap.len() > 1 && cap.starts_with('W') && cap[1..].chars().all(|c| c.is_ascii_digit())
}

fn norm_location(x: &str) -> String {
    let t = x.trim();
    let t = t.strip_prefix("./").unwrap_or(t);
    t.trim_end_matches('/').to_string()
}

fn nested(a: &str, b: &str) -> bool {
    let (a, b) = (norm_location(a), norm_location(b));
    !a.is_empty()
        && !b.is_empty()
        && (a == b || a.starts_with(&format!("{b}/")) || b.starts_with(&format!("{a}/")))
}

fn oracle_semantics(doc: &Value, model: &crate::contracts::ContractModel, v: &mut Violations) {
    let universe: BTreeSet<String> = model.capability_ids().into_iter().collect();
    let challenges: BTreeSet<String> = model.challenge_ids().into_iter().collect();
    let tiers: BTreeSet<String> = model.tier_ids().into_iter().collect();

    // V1 — fault manifest
    let mut fault_ids = BTreeSet::new();
    for (i, f) in arr(doc, "/fault_manifest/faults").iter().enumerate() {
        let at = format!("/fault_manifest/faults/{i}");
        if let Some(id) = s(f, "fault_id") {
            if !fault_ids.insert(id.to_string()) {
                v.push(
                    &format!("{at}/fault_id"),
                    format!("fault_id {id:?} is not unique"),
                );
            }
        }
        let caps: Vec<&str> = arr(f, "/class/capabilities")
            .iter()
            .filter_map(|c| c.as_str())
            .collect();
        for (j, c) in caps.iter().enumerate() {
            if !universe.contains(*c) {
                v.push(
                    &format!("{at}/class/capabilities/{j}"),
                    format!("{c:?} is not a capability of the owner source (Contract v3)"),
                );
            }
        }
        for (j, c) in arr(f, "/class/challenge_ids").iter().enumerate() {
            if let Some(c) = c.as_str() {
                if !challenges.contains(c) {
                    v.push(
                        &format!("{at}/class/challenge_ids/{j}"),
                        format!(
                            "{c:?} is not an advanced-qualification challenge of the owner source"
                        ),
                    );
                }
            }
        }
        for (j, t) in arr(f, "/expected_detection/tiers").iter().enumerate() {
            if let Some(t) = t.as_str() {
                if !tiers.contains(t) {
                    v.push(
                        &format!("{at}/expected_detection/tiers/{j}"),
                        format!(
                            "{t:?} is not a Governance Health Scheduler tier of O5 ({})",
                            tiers.iter().cloned().collect::<Vec<_>>().join(", ")
                        ),
                    );
                }
            }
        }
        if caps.iter().any(|c| is_gate_w(c)) && f.get("artifact_flow").is_none() {
            v.push(
                &format!("{at}/artifact_flow"),
                "a fault that challenges a Gate W capability must state the correct required input/version and the expected downstream propagation",
            );
        }
    }

    // V2 — hidden path-map oracle
    let mut current_paths: BTreeMap<String, usize> = BTreeMap::new();
    let entries = arr(doc, "/path_map_oracle/entries");
    for (i, e) in entries.iter().enumerate() {
        let at = format!("/path_map_oracle/entries/{i}");
        let cur = e
            .pointer("/current_artefact/path")
            .and_then(|x| x.as_str())
            .unwrap_or("");
        if !cur.is_empty() && current_paths.insert(cur.to_string(), i).is_some() {
            v.push(
                &format!("{at}/current_artefact/path"),
                format!("current artefact {cur:?} appears in more than one path-map entry"),
            );
        }
        let targets: Vec<&str> = arr(e, "/expected_target_paths")
            .iter()
            .filter_map(|x| x.as_str())
            .collect();
        let unique: BTreeSet<&str> = targets.iter().copied().collect();
        if unique.len() != targets.len() {
            v.push(
                &format!("{at}/expected_target_paths"),
                "target paths are not unique",
            );
        }
        let n = targets.len();
        let problem = match s(e, "action") {
            Some("KEEP") if !(n == 1 && targets[0] == cur) => {
                Some("KEEP: expected_target_paths must be exactly [the current path]")
            }
            Some("MOVE") | Some("RENAME") if !(n == 1 && targets[0] != cur) => {
                Some("MOVE/RENAME: exactly one target path, different from the current path")
            }
            Some("SPLIT") if n < 2 => Some("SPLIT: two or more target paths"),
            Some("MERGE") if n != 1 => Some("MERGE: exactly one target path"),
            Some("EXTRACT") if n < 1 => Some("EXTRACT: one or more target paths"),
            Some("RETIRE") if n > 1 => Some("RETIRE: no target path, or one archive location"),
            Some("DELETE_FROM_ACTIVE_TREE") if n != 0 => {
                Some("DELETE_FROM_ACTIVE_TREE: no target path")
            }
            _ => None,
        };
        if let Some(p) = problem {
            v.push(&format!("{at}/expected_target_paths"), p);
        }
    }

    // V3 — hidden memory oracle
    let refs = |ptr: &str| -> Vec<(usize, String)> {
        arr(doc, ptr)
            .iter()
            .enumerate()
            .filter_map(|(i, x)| s(x, "ref").map(|r| (i, r.to_string())))
            .collect()
    };
    let must = refs("/memory_oracle/must_be_indexed");
    let never: BTreeSet<String> = refs("/memory_oracle/must_never_be_indexed")
        .into_iter()
        .map(|x| x.1)
        .collect();
    let must_set: BTreeSet<String> = must.iter().map(|x| x.1.clone()).collect();
    for (i, r) in &must {
        if never.contains(r) {
            v.push(
                &format!("/memory_oracle/must_be_indexed/{i}/ref"),
                format!("{r:?} is also listed in must_never_be_indexed"),
            );
        }
    }
    for (ptr, what) in [
        ("/memory_oracle/must_be_indexed", "must_be_indexed"),
        (
            "/memory_oracle/must_never_be_indexed",
            "must_never_be_indexed",
        ),
        (
            "/memory_oracle/expected_authority_namespaces",
            "expected_authority_namespaces",
        ),
        ("/memory_oracle/expected_status", "expected_status"),
    ] {
        let mut seen = BTreeSet::new();
        for (i, r) in refs(ptr) {
            if !seen.insert(r.clone()) {
                v.push(
                    &format!("{ptr}/{i}/ref"),
                    format!("{r:?} appears twice in {what}"),
                );
            }
        }
    }
    for (i, st) in arr(doc, "/memory_oracle/expected_status")
        .iter()
        .enumerate()
    {
        if s(st, "status") == Some("SUPERSEDED") && s(st, "superseded_by") == s(st, "ref") {
            v.push(
                &format!("/memory_oracle/expected_status/{i}/superseded_by"),
                "an artefact cannot be superseded by itself",
            );
        }
    }
    let mut qids = BTreeSet::new();
    for (i, q) in arr(doc, "/memory_oracle/expected_retrieval_results")
        .iter()
        .enumerate()
    {
        let at = format!("/memory_oracle/expected_retrieval_results/{i}");
        if let Some(id) = s(q, "query_id") {
            if !qids.insert(id.to_string()) {
                v.push(
                    &format!("{at}/query_id"),
                    format!("query_id {id:?} is not unique"),
                );
            }
        }
        let inc: BTreeSet<&str> = arr(q, "/must_include")
            .iter()
            .filter_map(|x| x.as_str())
            .collect();
        let exc: BTreeSet<&str> = arr(q, "/must_not_include")
            .iter()
            .filter_map(|x| x.as_str())
            .collect();
        if let Some(r) = inc.intersection(&exc).next() {
            v.push(
                &format!("{at}/must_not_include"),
                format!("{r:?} is both required and forbidden in the results"),
            );
        }
        for r in &inc {
            if never.contains(*r) {
                v.push(
                    &format!("{at}/must_include"),
                    format!("{r:?} must never be indexed, so no retrieval may return it"),
                );
            }
        }
    }

    // V2 ↔ V3 consistency
    for (i, e) in entries.iter().enumerate() {
        let cur = e
            .pointer("/current_artefact/path")
            .and_then(|x| x.as_str())
            .unwrap_or("");
        match s(e, "indexing_expectation") {
            Some("NEVER_INDEX") if must_set.contains(cur) => v.push(
                &format!("/path_map_oracle/entries/{i}/indexing_expectation"),
                format!("NEVER_INDEX contradicts memory_oracle.must_be_indexed for {cur:?}"),
            ),
            Some("INDEX_CURRENT") | Some("INDEX_HISTORICAL") if never.contains(cur) => v.push(
                &format!("/path_map_oracle/entries/{i}/indexing_expectation"),
                format!("indexing {cur:?} contradicts memory_oracle.must_never_be_indexed"),
            ),
            _ => {}
        }
    }

    // separation (Contract v3:1062)
    if let Some(sep) = doc.get("separation") {
        let store = s(sep, "oracle_storage").unwrap_or("");
        for (key, what) in [
            (
                "public_qualification_suite",
                "the permanent public qualification suite",
            ),
            ("qualification_repository", "the qualification repository"),
        ] {
            if let Some(other) = s(sep, key) {
                if nested(store, other) {
                    v.push(
                        "/separation/oracle_storage",
                        format!("the hidden oracle's storage location {store:?} is not separate from {what} ({other:?})"),
                    );
                }
            }
        }
    }
}

fn ratio_parts(m: &Value) -> Option<(u64, u64, f64)> {
    Some((
        m.get("numerator")?.as_u64()?,
        m.get("denominator")?.as_u64()?,
        m.get("value")?.as_f64()?,
    ))
}

fn is_na(m: &Value) -> bool {
    m.get("applicable") == Some(&json!(false))
}

/// Check a ratio's arithmetic and, where the report itself determines them, its numerator and denominator.
fn check_ratio(
    v: &mut Violations,
    at: &str,
    m: Option<&Value>,
    expect: Option<(u64, u64)>,
    na_when: Option<bool>,
) {
    let Some(m) = m else { return };
    match na_when {
        Some(true) if !is_na(m) => {
            v.push(at, "must be an explicit N/A here (nothing to measure)");
            return;
        }
        Some(false) if is_na(m) => {
            v.push(at, "cannot be N/A: the report has outcomes to measure");
            return;
        }
        _ => {}
    }
    if is_na(m) {
        return;
    }
    let Some((num, den, value)) = ratio_parts(m) else {
        return;
    };
    if num > den {
        v.push(at, format!("numerator {num} exceeds denominator {den}"));
    }
    if den > 0 && (value - num as f64 / den as f64).abs() > RATIO_TOLERANCE {
        v.push(
            &format!("{at}/value"),
            format!("value {value} is not {num}/{den}"),
        );
    }
    if let Some((en, ed)) = expect {
        if (num, den) != (en, ed) {
            v.push(
                at,
                format!("is {num}/{den}; the per-fault outcomes give {en}/{ed}"),
            );
        }
    }
}

fn report_semantics(doc: &Value, v: &mut Violations) {
    let outcomes = arr(doc, "/per_fault_outcomes");
    let mut ids = BTreeSet::new();
    let mut detected = 0u64;
    let mut severity_ok = 0u64;
    let mut imp_expected = 0u64;
    let mut imp_found = 0u64;
    for (i, o) in outcomes.iter().enumerate() {
        let at = format!("/per_fault_outcomes/{i}");
        if let Some(id) = s(o, "fault_id") {
            if !ids.insert(id.to_string()) {
                v.push(
                    &format!("{at}/fault_id"),
                    format!("fault {id:?} has more than one outcome"),
                );
            }
        }
        let det = o.get("detected").and_then(|x| x.as_bool()).unwrap_or(false);
        let sev_ok = o
            .get("severity_correct")
            .and_then(|x| x.as_bool())
            .unwrap_or(false);
        let e = o
            .get("impacted_expected")
            .and_then(|x| x.as_u64())
            .unwrap_or(0);
        let f = o
            .get("impacted_found")
            .and_then(|x| x.as_u64())
            .unwrap_or(0);
        if f > e {
            v.push(
                &format!("{at}/impacted_found"),
                format!("found {f} of {e} expected impacted artefacts"),
            );
        }
        imp_expected += e;
        if det {
            detected += 1;
            imp_found += f;
            if sev_ok {
                severity_ok += 1;
            }
            for k in ["detected_at_tier", "observed_severity", "detection_signal"] {
                if o.get(k).map(|x| x.is_null()).unwrap_or(true) {
                    v.push(
                        &format!("{at}/{k}"),
                        "a detected fault records where, how and at what severity it was detected",
                    );
                }
            }
        } else {
            for k in ["detected_at_tier", "observed_severity", "detection_signal"] {
                if o.get(k).map(|x| !x.is_null()).unwrap_or(false) {
                    v.push(
                        &format!("{at}/{k}"),
                        "an undetected fault has no detection record",
                    );
                }
            }
            if sev_ok {
                v.push(
                    &format!("{at}/severity_correct"),
                    "an undetected fault cannot have a correct severity",
                );
            }
            if f > 0 {
                v.push(
                    &format!("{at}/impacted_found"),
                    "an undetected fault earns no impact-map credit",
                );
            }
        }
    }
    let total = outcomes.len() as u64;
    let m = doc.get("metrics");
    let metric = |k: &str| m.and_then(|m| m.get(k));
    check_ratio(
        v,
        "/metrics/injected_defect_detection_recall",
        metric("injected_defect_detection_recall"),
        Some((detected, total)),
        Some(false),
    );
    check_ratio(
        v,
        "/metrics/severity_accuracy",
        metric("severity_accuracy"),
        (detected > 0).then_some((severity_ok, detected)),
        Some(detected == 0),
    );
    check_ratio(
        v,
        "/metrics/impact_map_accuracy",
        metric("impact_map_accuracy"),
        (imp_expected > 0).then_some((imp_found, imp_expected)),
        Some(imp_expected == 0),
    );
    for k in [
        "path_map_accuracy",
        "recovery_chaos_pass_rate",
        "human_gate_correctness",
        "task_readiness_correctness",
    ] {
        check_ratio(v, &format!("/metrics/{k}"), metric(k), None, None);
    }
    if let Some(fp) = metric("false_positives") {
        let n = fp
            .get("findings")
            .and_then(|x| x.as_array())
            .map(|a| a.len() as u64);
        if n.is_some() && fp.get("count").and_then(|x| x.as_u64()) != n {
            v.push(
                "/metrics/false_positives/count",
                "count differs from the number of findings listed",
            );
        }
    }
    for k in [
        "missed_authoritative_artefacts",
        "wrong_indexing_count",
        "stale_index_count",
    ] {
        if let Some(c) = metric(k) {
            let n = c
                .get("refs")
                .and_then(|x| x.as_array())
                .map(|a| a.len() as u64);
            if n.is_some() && c.get("count").and_then(|x| x.as_u64()) != n {
                v.push(
                    &format!("/metrics/{k}/count"),
                    "count differs from the number of artefacts listed",
                );
            }
        }
    }
}

/// A score report against the sealed oracle it names: identity, digest, repository, fault coverage and the parts of
/// every metric the oracle determines. Returns violations located in the report.
pub fn cross_check(report: &Value, oracle: &Value) -> Vec<Value> {
    let cw = crosswalk().unwrap_or_default();
    let mut v = Violations {
        kind: KIND_SCORE_REPORT.into(),
        cw: &cw,
        list: vec![],
    };
    let digest = hash_value(oracle);
    if report.pointer("/binding/oracle_id") != oracle.get("oracle_id") {
        v.push(
            "/binding/oracle_id",
            format!(
                "the report names oracle {:?}; the oracle supplied is {:?}",
                report.pointer("/binding/oracle_id"),
                oracle.get("oracle_id")
            ),
        );
    }
    if report
        .pointer("/binding/oracle_sha256")
        .and_then(|x| x.as_str())
        != Some(digest.as_str())
    {
        v.push("/binding/oracle_sha256", format!("the report was scored against oracle digest {:?}; the oracle supplied has digest {digest} — the oracle changed after it was sealed, or the report was scored against another oracle", report.pointer("/binding/oracle_sha256")));
    }
    for k in ["id", "commit"] {
        if report.pointer(&format!("/binding/repository/{k}"))
            != oracle.pointer(&format!("/repository/{k}"))
        {
            v.push(
                &format!("/binding/repository/{k}"),
                "differs from the oracle's qualification repository",
            );
        }
    }
    if report.get("purpose") != oracle.get("purpose") {
        v.push("/purpose", "a report and its oracle must have the same purpose (a FORMAT_SAMPLE is never scored as QUALIFICATION)");
    }
    let faults: BTreeMap<String, &Value> = arr(oracle, "/fault_manifest/faults")
        .into_iter()
        .filter_map(|f| s(f, "fault_id").map(|id| (id.to_string(), f)))
        .collect();
    let mut covered = BTreeSet::new();
    for (i, o) in arr(report, "/per_fault_outcomes").iter().enumerate() {
        let at = format!("/per_fault_outcomes/{i}");
        let Some(id) = s(o, "fault_id") else { continue };
        covered.insert(id.to_string());
        let Some(f) = faults.get(id) else {
            v.push(
                &format!("{at}/fault_id"),
                format!("fault {id:?} is not in the oracle's fault manifest"),
            );
            continue;
        };
        let expected_impacted = arr(f, "/expected_impacted").len() as u64;
        if o.get("impacted_expected").and_then(|x| x.as_u64()) != Some(expected_impacted) {
            v.push(
                &format!("{at}/impacted_expected"),
                format!(
                    "the oracle expects {expected_impacted} impacted artefacts/nodes for {id:?}"
                ),
            );
        }
        if let Some(obs) = s(o, "observed_severity") {
            let correct = Some(obs) == s(f, "expected_severity");
            if o.get("severity_correct").and_then(|x| x.as_bool()) != Some(correct) {
                v.push(
                    &format!("{at}/severity_correct"),
                    format!(
                        "observed {obs}, expected {:?}: severity_correct must be {correct}",
                        s(f, "expected_severity")
                    ),
                );
            }
        }
    }
    for id in faults.keys() {
        if !covered.contains(id) {
            v.push(
                "/per_fault_outcomes",
                format!(
                    "the oracle's fault {id:?} has no outcome — every injected defect is scored"
                ),
            );
        }
    }
    let entries = arr(oracle, "/path_map_oracle/entries").len() as u64;
    match report.pointer("/metrics/path_map_accuracy") {
        Some(m) if entries == 0 && !is_na(m) => v.push(
            "/metrics/path_map_accuracy",
            "the oracle has no path-map oracle, so path-map accuracy is an explicit N/A",
        ),
        Some(m) if entries > 0 && is_na(m) => v.push(
            "/metrics/path_map_accuracy",
            "the oracle has a path-map oracle, so path-map accuracy is measured",
        ),
        Some(m) if entries > 0 => {
            if m.get("denominator").and_then(|x| x.as_u64()) != Some(entries) {
                v.push(
                    "/metrics/path_map_accuracy/denominator",
                    format!("the oracle has {entries} path-map entries"),
                );
            }
        }
        _ => {}
    }
    let queries = arr(oracle, "/memory_oracle/expected_retrieval_results").len() as u64;
    if report
        .pointer("/metrics/retrieval_metrics/queries")
        .and_then(|x| x.as_u64())
        != Some(queries)
    {
        v.push(
            "/metrics/retrieval_metrics/queries",
            format!("the oracle defines {queries} expected retrieval results"),
        );
    }
    v.list
}

/// True when a value is hidden-oracle material: a document of this format's oracle kind, or a governed record whose
/// type is one of [`HIDDEN_ORACLE_RECORD_TYPES`]. A governed repository under qualification must hold none
/// (Contract v3:1014, :1062) — see the integration point for the governance suite in the repair report.
pub fn is_hidden_oracle_material(v: &Value) -> bool {
    (s(v, "format") == Some(FORMAT) && s(v, "kind") == Some(KIND_ORACLE))
        || s(v, "type")
            .map(|t| HIDDEN_ORACLE_RECORD_TYPES.contains(&t))
            .unwrap_or(false)
}

/// Files under `root` that hold hidden-oracle material (see [`is_hidden_oracle_material`]).
pub fn scan_for_hidden_oracle_material(root: &Path) -> Vec<Value> {
    let mut out = vec![];
    for e in walkdir::WalkDir::new(root)
        .sort_by_file_name()
        .into_iter()
        .filter_entry(|e| e.file_name() != ".git")
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
    {
        if e.metadata()
            .map(|m| m.len() > MAX_SCAN_BYTES)
            .unwrap_or(true)
        {
            continue;
        }
        let Ok(bytes) = std::fs::read(e.path()) else {
            continue;
        };
        let text = String::from_utf8_lossy(&bytes);
        if !(text.contains(FORMAT) || HIDDEN_ORACLE_RECORD_TYPES.iter().any(|t| text.contains(t))) {
            continue;
        }
        if let Ok(v) = serde_yaml::from_str::<Value>(&text) {
            if is_hidden_oracle_material(&v) {
                out.push(json!({"path": e.path().display().to_string(), "problem": "hidden-oracle material"}));
            }
        }
    }
    out
}

fn separation_scan(
    oracle_path: &Path,
    doc: &Value,
    dirs: &[(PathBuf, &'static str)],
) -> Vec<Value> {
    let canon = |p: &Path| std::fs::canonicalize(p).unwrap_or_else(|_| p.to_path_buf());
    let op = canon(oracle_path);
    let oracle_id = s(doc, "oracle_id").unwrap_or("").to_string();
    let digest = hash_value(doc);
    let truths: Vec<(String, String)> = arr(doc, "/fault_manifest/faults")
        .iter()
        .filter_map(|f| {
            let t = f
                .pointer("/hidden_authoritative_truth/statement")?
                .as_str()?;
            (t.chars().count() >= MIN_TRUTH_SCAN_CHARS)
                .then(|| (s(f, "fault_id").unwrap_or("?").to_string(), t.to_string()))
        })
        .collect();
    let mut out = vec![];
    for (dir, role) in dirs {
        let d = canon(dir);
        if op.starts_with(&d) {
            out.push(json!({"at": d.display().to_string(), "problem": format!("the hidden oracle is stored inside the {role}")}));
        }
        for e in walkdir::WalkDir::new(&d)
            .sort_by_file_name()
            .into_iter()
            .filter_entry(|e| e.file_name() != ".git")
            .filter_map(|e| e.ok())
            .filter(|e| e.file_type().is_file())
        {
            let p = canon(e.path());
            if p == op
                || e.metadata()
                    .map(|m| m.len() > MAX_SCAN_BYTES)
                    .unwrap_or(true)
            {
                continue;
            }
            let Ok(bytes) = std::fs::read(e.path()) else {
                continue;
            };
            let text = String::from_utf8_lossy(&bytes);
            let shown = p.display().to_string();
            if text.contains(FORMAT) {
                if let Ok(v) = serde_yaml::from_str::<Value>(&text) {
                    if is_hidden_oracle_material(&v) {
                        out.push(json!({"at": shown, "problem": format!("a hidden-oracle document lies inside the {role}")}));
                        continue;
                    }
                }
            }
            if !oracle_id.is_empty() && text.contains(&oracle_id) {
                out.push(json!({"at": shown, "problem": format!("the oracle id {oracle_id:?} appears inside the {role}")}));
            }
            if text.contains(&digest) {
                out.push(json!({"at": shown, "problem": format!("the oracle's digest appears inside the {role}")}));
            }
            for (fid, t) in &truths {
                if text.contains(t.as_str()) {
                    out.push(json!({"at": shown, "problem": format!("the hidden authoritative truth of fault {fid:?} appears verbatim inside the {role}")}));
                }
            }
        }
    }
    out
}

/// Options for [`validate_file`].
#[derive(Debug, Clone, Default)]
pub struct ValidateOptions {
    /// For a score report: the sealed oracle it was scored against.
    pub oracle: Option<PathBuf>,
    /// Public qualification suite roots the oracle must be kept out of.
    pub public_suites: Vec<PathBuf>,
    /// Qualification repository roots the oracle must be kept out of.
    pub repositories: Vec<PathBuf>,
}

fn load(path: &Path) -> Result<Value> {
    let text = crate::util::read_text(path).map_err(|e| {
        GovError::new(
            "ORACLE_RECORD_UNREADABLE",
            format!("{} cannot be read: {}", path.display(), e.message),
        )
    })?;
    serde_yaml::from_str::<Value>(&text).map_err(|e| {
        GovError::new(
            "ORACLE_RECORD_UNREADABLE",
            format!("{} is neither JSON nor YAML: {e}", path.display()),
        )
    })
}

fn invalid(what: &str, kind: &str, violations: Vec<Value>) -> GovError {
    let n = violations.len();
    let head: Vec<String> = violations
        .iter()
        .take(4)
        .map(|x| {
            format!(
                "{} {}{}",
                x["at"].as_str().unwrap_or(""),
                x["problem"].as_str().unwrap_or(""),
                x.get("element")
                    .and_then(|e| e.as_str())
                    .map(|e| format!(" [{e}]"))
                    .unwrap_or_default()
            )
        })
        .collect();
    GovError::new(
        "ORACLE_RECORD_INVALID",
        format!(
            "{what} is not a valid {} document: {n} violation(s) — {}{}. Remedy: supply every field the format requires (`gov oracle format` lists each Contract v3 V1-V4 element and its field) and correct the listed violations; the validator never fills a field in.",
            if kind.is_empty() { "Qualification Oracle" } else { kind },
            head.join("; "),
            if n > 4 { "; …" } else { "" }
        ),
    )
    .with_details(json!({"violation_count": n, "violations": violations, "format_sha256": format_sha256(), "definition": DEFINITION_PATH}))
}

fn summary(doc: &Value, kind: &str) -> Value {
    let count = |p: &str| arr(doc, p).len();
    let counts = if kind == KIND_ORACLE {
        json!({
            "faults": count("/fault_manifest/faults"),
            "path_map_entries": count("/path_map_oracle/entries"),
            "must_be_indexed": count("/memory_oracle/must_be_indexed"),
            "must_never_be_indexed": count("/memory_oracle/must_never_be_indexed"),
            "expected_retrieval_results": count("/memory_oracle/expected_retrieval_results"),
        })
    } else {
        json!({"per_fault_outcomes": count("/per_fault_outcomes")})
    };
    json!({
        "verdict": "RECORD_CONFORMS_TO_FORMAT",
        "kind": kind,
        "purpose": doc.get("purpose"),
        "format": FORMAT,
        "format_version": FORMAT_VERSION,
        "format_sha256": format_sha256(),
        "canonical_sha256": hash_value(doc),
        "counts": counts,
    })
}

/// Validate an in-memory document (no filesystem checks). Used by in-process callers such as a G6 qualification entry
/// point.
pub fn validate_value(doc: &Value) -> Result<Value> {
    let (kind, violations) = check_document(doc)?;
    if !violations.is_empty() {
        return Err(invalid("the document", &kind, violations));
    }
    Ok(summary(doc, &kind))
}

/// `gov oracle validate`: validate a document on disk; for a score report optionally cross-check it against its
/// sealed oracle; for an oracle, check its physical separation from the public suite and the qualification repository
/// (the directories given, plus the locations the oracle declares when they exist on this machine).
pub fn validate_file(path: &Path, opts: &ValidateOptions) -> Result<Value> {
    let doc = load(path)?;
    let (kind, violations) = check_document(&doc)?;
    let shown = path.display().to_string();
    if !violations.is_empty() {
        return Err(invalid(&shown, &kind, violations));
    }
    let mut out = summary(&doc, &kind);
    out["path"] = json!(shown);
    if kind == KIND_ORACLE {
        if opts.oracle.is_some() {
            return Err(GovError::new(
                "USAGE",
                "--oracle applies to a qualification-score-report, not to an oracle",
            ));
        }
        let mut dirs: Vec<(PathBuf, &'static str)> = vec![];
        for d in &opts.public_suites {
            dirs.push((d.clone(), "public qualification suite"));
        }
        for d in &opts.repositories {
            dirs.push((d.clone(), "qualification repository"));
        }
        for (key, role) in [
            ("public_qualification_suite", "public qualification suite"),
            ("qualification_repository", "qualification repository"),
        ] {
            if let Some(loc) = doc
                .pointer(&format!("/separation/{key}"))
                .and_then(|x| x.as_str())
            {
                let p = PathBuf::from(loc);
                if p.is_dir() {
                    dirs.push((p, role));
                }
            }
        }
        for (d, role) in &dirs {
            if !d.is_dir() {
                return Err(GovError::new(
                    "USAGE",
                    format!("the {role} {} is not a directory", d.display()),
                ));
            }
        }
        let found = separation_scan(path, &doc, &dirs);
        if !found.is_empty() {
            return Err(GovError::new(
                "ORACLE_SEPARATION_VIOLATED",
                format!(
                    "the hidden oracle {shown} is not separate from the public qualification suite / qualification repository: {} finding(s), first: {} — {}. Contract v3:1062: \"The permanent public qualification suite and fresh verifier hidden oracle must remain separate.\" Remedy: keep the oracle in verifier custody outside both, remove every trace of it from them, and re-seal it.",
                    found.len(),
                    found[0]["at"].as_str().unwrap_or(""),
                    found[0]["problem"].as_str().unwrap_or("")
                ),
            )
            .with_details(json!({"findings": found})));
        }
        out["separation"] = json!({
            "scanned": dirs.iter().map(|(d, r)| json!({"role": r, "path": d.display().to_string()})).collect::<Vec<_>>(),
            "findings": 0,
        });
    } else {
        if !opts.public_suites.is_empty() || !opts.repositories.is_empty() {
            return Err(GovError::new(
                "USAGE",
                "--public-suite / --repository apply to a qualification-oracle document",
            ));
        }
        if let Some(op) = &opts.oracle {
            let oracle = load(op)?;
            let (okind, ov) = check_document(&oracle)?;
            if okind != KIND_ORACLE {
                return Err(GovError::new(
                    "USAGE",
                    format!(
                        "--oracle must name a qualification-oracle document; {} is {okind:?}",
                        op.display()
                    ),
                ));
            }
            if !ov.is_empty() {
                return Err(invalid(&op.display().to_string(), &okind, ov));
            }
            let x = cross_check(&doc, &oracle);
            if !x.is_empty() {
                return Err(GovError::new(
                    "ORACLE_SCORE_BINDING_MISMATCH",
                    format!(
                        "the score report {shown} does not match the oracle {}: {} violation(s), first: {} {}. Remedy: score against the sealed oracle the report names, and every injected fault of it.",
                        op.display(),
                        x.len(),
                        x[0]["at"].as_str().unwrap_or(""),
                        x[0]["problem"].as_str().unwrap_or("")
                    ),
                )
                .with_details(json!({"violations": x})));
            }
            out["binding_verified"] =
                json!({"oracle": op.display().to_string(), "oracle_sha256": hash_value(&oracle)});
        }
    }
    Ok(out)
}

/// `gov oracle format`: the format definition, its digest, and the crosswalk from every Contract v3 V1-V4 element to
/// the field that carries it.
pub fn format_definition() -> Result<Value> {
    let def = definition()?;
    let cw = crosswalk()?;
    Ok(json!({
        "format": FORMAT,
        "format_version": FORMAT_VERSION,
        "format_sha256": format_sha256(),
        "definition": DEFINITION_PATH,
        "status": def.get("x-format-status"),
        "kinds": [KIND_ORACLE, KIND_SCORE_REPORT],
        "owner_source_sha256": crate::contracts::OWNER_SOURCE_SHA256,
        "crosswalk": cw.iter().map(|e| json!({"element": e.element, "source_line": e.source_line, "text": e.text, "kind": e.kind, "fields": e.fields})).collect::<Vec<_>>(),
        "separation": "An oracle document is stored by the fresh verifier outside the public qualification suite and outside the qualification repository; `gov oracle validate` refuses one stored inside either, and any copy, id, digest or verbatim hidden truth of it found in either.",
        "schema": def,
    }))
}

#[cfg(test)]
mod tests {
    use super::*;

    const REPO_COMMIT: &str = "0123456789abcdef0123456789abcdef01234567";

    /// A synthetic FORMAT_SAMPLE oracle. It exercises every field of the format and describes no qualification
    /// repository: every path is a placeholder under `example/`.
    fn sample_oracle() -> Value {
        json!({
            "format": FORMAT,
            "format_version": FORMAT_VERSION,
            "format_sha256": format_sha256(),
            "kind": KIND_ORACLE,
            "purpose": "FORMAT_SAMPLE",
            "oracle_id": "SAMPLE-ORACLE-0001",
            "custody": {"owner_role": "FRESH_INDEPENDENT_VERIFIER", "owner_run_id": "SAMPLE-RUN", "authored_independently_of_implementation": true, "created_at": "2026-09-19T00:00:00Z"},
            "visibility": "HIDDEN",
            "repository": {"id": "sample-repo", "adoption_mode": "BROWNFIELD", "commit": REPO_COMMIT, "label": "format sample"},
            "separation": {"public_qualification_suite": "example/public-suite", "qualification_repository": "example/repository", "oracle_storage": "example/verifier-custody/oracle.json"},
            "fault_manifest": {"faults": [
                {
                    "fault_id": "SAMPLE-F1",
                    "class": {"id": "SAMPLE_SUPERSEDED_INPUT", "capabilities": ["W3", "W10"], "challenge_ids": ["AQC-W12"]},
                    "hidden_authoritative_truth": {"statement": "example/spec-b.md is the current required input; example/spec-a.md is superseded", "authoritative_refs": ["example/spec-b.md"]},
                    "injected_repository_state": {"description": "a superseded spec made semantically closer to the task than the current one", "changes": [{"path": "example/spec-a.md", "change": "MODIFIED"}, {"path": "example/spec-c.md", "change": "MOVED", "from_path": "example/old/spec-c.md"}]},
                    "expected_detection": {"tiers": ["G0", "G2"], "signals": ["SAMPLE_SIGNAL"], "must_detect_before": "task close"},
                    "expected_severity": "HIGH",
                    "expected_impacted": [{"ref": "example/task-1", "ref_kind": "TASK", "relation": "DIRECT"}, {"ref": "example/src/a.rs", "ref_kind": "PATH", "relation": "TRANSITIVE"}],
                    "expected_governed_action": [{"action": "BLOCK_CLOSE", "target": "example/task-1", "description": "close refused until the current input is consumed"}],
                    "forbidden_outcomes": [{"outcome": "the superseded spec satisfies the required input", "observable": "the context packet lists example/spec-a.md as the mandatory input"}],
                    "artifact_flow": {"required_inputs": [{"artefact_id": "example/spec-b.md", "version": "2"}], "expected_propagation": [{"ref": "example/task-1", "expected_state": "STALE"}]}
                },
                {
                    "fault_id": "SAMPLE-F2",
                    "class": {"id": "SAMPLE_SEEDED_SECRET", "capabilities": ["A3"]},
                    "hidden_authoritative_truth": {"statement": "example/.env is a secret and must never be indexed or exported", "authoritative_refs": []},
                    "injected_repository_state": {"description": "a credential file added", "changes": [{"path": "example/.env", "change": "ADDED"}]},
                    "expected_detection": {"tiers": ["G1"], "signals": ["SAMPLE_SECRET_SIGNAL"], "must_detect_before": "the next index build"},
                    "expected_severity": "CRITICAL",
                    "expected_impacted": [{"ref": "example/.env", "ref_kind": "PATH", "relation": "DIRECT"}],
                    "expected_governed_action": [{"action": "QUARANTINE", "description": "excluded from every index"}],
                    "forbidden_outcomes": [{"outcome": "the secret is retrievable", "observable": "a retrieval result cites example/.env"}]
                }
            ]},
            "path_map_oracle": {"entries": [
                {"current_artefact": {"path": "example/spec-b.md"}, "correct_classification": "specification", "authority": "AUTHORITATIVE", "expected_target_paths": ["example/spec-b.md"], "action": "KEEP", "expected_references": ["example/src/a.rs"], "expected_consumers": ["example/task-1"], "sensitivity": "internal", "indexing_expectation": "INDEX_CURRENT"},
                {"current_artefact": {"path": "example/spec-a.md"}, "correct_classification": "specification", "authority": "SUPERSEDED", "expected_target_paths": ["example/archive/spec-a.md"], "action": "MOVE", "expected_references": [], "expected_consumers": [], "sensitivity": "internal", "indexing_expectation": "INDEX_HISTORICAL"}
            ]},
            "memory_oracle": {
                "must_be_indexed": [{"ref": "example/spec-b.md", "routes": ["STRUCTURED", "SEMANTIC"]}],
                "must_never_be_indexed": [{"ref": "example/.env", "reason": "secret"}],
                "expected_authority_namespaces": [{"ref": "example/spec-b.md", "namespace": "authoritative/spec"}],
                "expected_status": [{"ref": "example/spec-b.md", "status": "CURRENT"}, {"ref": "example/spec-a.md", "status": "SUPERSEDED", "superseded_by": "example/spec-b.md"}],
                "expected_graph_relationships": [{"from": "example/src/a.rs", "relation": "IMPLEMENTS", "to": "example/spec-b.md"}],
                "expected_code_symbols": [{"path": "example/src/a.rs", "symbol": "handle", "symbol_kind": "function", "language": "rust"}],
                "expected_retrieval_results": [{"query_id": "Q1", "query": "current spec for the example feature", "route": "FUSED", "top_k": 5, "must_include": ["example/spec-b.md"], "must_not_include": ["example/spec-a.md"]}]
            }
        })
    }

    fn sample_report(oracle: &Value) -> Value {
        json!({
            "format": FORMAT,
            "format_version": FORMAT_VERSION,
            "format_sha256": format_sha256(),
            "kind": KIND_SCORE_REPORT,
            "purpose": "FORMAT_SAMPLE",
            "report_id": "SAMPLE-REPORT-0001",
            "custody": {"owner_role": "FRESH_INDEPENDENT_VERIFIER", "owner_run_id": "SAMPLE-RUN", "authored_independently_of_implementation": true, "created_at": "2026-09-19T01:00:00Z"},
            "binding": {"oracle_id": "SAMPLE-ORACLE-0001", "oracle_sha256": hash_value(oracle), "repository": {"id": "sample-repo", "commit": REPO_COMMIT}, "candidate": {"commit": "89abcdef0123456789abcdef0123456789abcdef", "product_code_digest": "0".repeat(64)}, "run_id": "SAMPLE-RUN-1", "scored_at": "2026-09-19T02:00:00Z"},
            "metrics": {
                "injected_defect_detection_recall": {"numerator": 1, "denominator": 2, "value": 0.5},
                "false_positives": {"count": 1, "findings": ["SAMPLE-FINDING-9"]},
                "severity_accuracy": {"numerator": 1, "denominator": 1, "value": 1.0},
                "impact_map_accuracy": {"numerator": 1, "denominator": 3, "value": 1.0 / 3.0},
                "path_map_accuracy": {"numerator": 1, "denominator": 2, "value": 0.5},
                "missed_authoritative_artefacts": {"count": 0, "refs": []},
                "wrong_indexing_count": {"count": 1, "refs": ["example/.env"]},
                "stale_index_count": {"count": 0, "refs": []},
                "retrieval_metrics": {"k": 5, "queries": 1, "recall_at_k": 1.0, "mrr": 1.0, "precision_at_k": 0.2, "stale_hit_rate": 0.0},
                "recovery_chaos_pass_rate": {"applicable": false, "reason": "no chaos scenario in the format sample"},
                "human_gate_correctness": {"numerator": 1, "denominator": 1, "value": 1.0},
                "task_readiness_correctness": {"numerator": 2, "denominator": 2, "value": 1.0}
            },
            "per_fault_outcomes": [
                {"fault_id": "SAMPLE-F1", "detected": true, "detected_at_tier": "G2", "detection_signal": "SAMPLE_SIGNAL", "observed_severity": "HIGH", "severity_correct": true, "impacted_expected": 2, "impacted_found": 1, "governed_action_correct": true, "forbidden_outcomes_observed": []},
                {"fault_id": "SAMPLE-F2", "detected": false, "detected_at_tier": null, "detection_signal": null, "observed_severity": null, "severity_correct": false, "impacted_expected": 1, "impacted_found": 0, "governed_action_correct": false, "forbidden_outcomes_observed": ["the secret is retrievable"]}
            ]
        })
    }

    fn problems(doc: &Value) -> Vec<Value> {
        check_document(doc).expect("format loads").1
    }

    /// Remove the value at a JSON pointer (`*` = index 0).
    fn remove(doc: &mut Value, field: &str) -> bool {
        let ptr = field.replace('*', "0");
        let (parent, key) = ptr.rsplit_once('/').unwrap();
        match doc.pointer_mut(parent) {
            Some(Value::Object(o)) => o.remove(key).is_some(),
            _ => false,
        }
    }

    #[test]
    fn the_format_covers_every_v1_v4_element_of_the_owner_source() {
        let cw = crosswalk().expect("complete crosswalk");
        let model = crate::contracts::embedded_model().unwrap();
        for cap in ["V1", "V2", "V3", "V4"] {
            for it in &model.capability(cap).unwrap().items {
                assert!(
                    cw.iter().any(|e| e.element == it.id && e.text == it.text),
                    "{} unmapped",
                    it.id
                );
            }
        }
        assert_eq!(cw.iter().filter(|e| e.element.starts_with('V')).count(), 35);
        let f = format_definition().unwrap();
        assert_eq!(f["format_sha256"], format_sha256());
    }

    #[test]
    fn well_formed_samples_validate() {
        let o = sample_oracle();
        assert_eq!(problems(&o), Vec::<Value>::new());
        let r = sample_report(&o);
        assert_eq!(problems(&r), Vec::<Value>::new());
        assert_eq!(cross_check(&r, &o), Vec::<Value>::new());
        assert_eq!(
            validate_value(&o).unwrap()["verdict"],
            "RECORD_CONFORMS_TO_FORMAT"
        );
    }

    #[test]
    fn a_record_missing_any_v1_v4_field_is_rejected() {
        let cw = crosswalk().unwrap();
        let o = sample_oracle();
        let r = sample_report(&o);
        let mut checked = 0;
        for e in &cw {
            for f in &e.fields {
                let mut doc = if e.kind == KIND_ORACLE {
                    o.clone()
                } else {
                    r.clone()
                };
                assert!(remove(&mut doc, f), "the sample carries {f}");
                let p = problems(&doc);
                let ptr = f.replace('*', "0");
                assert!(
                    p.iter().any(|x| x["at"] == ptr && x["element"] == e.element.as_str()),
                    "removing {f} ({}) was not reported at {ptr} as that Contract v3 element: {p:#?}",
                    e.element
                );
                checked += 1;
            }
        }
        assert!(checked >= 45, "{checked}");
    }

    #[test]
    fn the_record_the_audit_used_is_rejected() {
        // epsilon-r V probe: a "fault manifest" record lacking every V1 field
        for doc in [
            json!({"id": "FM-0001", "type": "fault-manifest", "title": "empty fault manifest", "status": "ACTIVE"}),
            json!({"id": "FM-0002", "type": "fault-manifest", "title": "nonsense", "status": "ACTIVE", "class": 42, "expected_severity": "purple"}),
        ] {
            let e = validate_value(&doc).unwrap_err();
            assert_eq!(e.code, "ORACLE_RECORD_INVALID");
        }
        let mut o = sample_oracle();
        o["fault_manifest"]["faults"][0] = json!({"fault_id": "X1"});
        let p = problems(&o);
        for k in [
            "class",
            "hidden_authoritative_truth",
            "injected_repository_state",
            "expected_detection",
            "expected_severity",
            "expected_impacted",
            "expected_governed_action",
            "forbidden_outcomes",
        ] {
            assert!(
                p.iter()
                    .any(|x| x["at"] == format!("/fault_manifest/faults/0/{k}")),
                "{k}: {p:#?}"
            );
        }
    }

    #[test]
    fn semantic_rules_reject_contradictory_or_unanchored_records() {
        let cases: Vec<(&str, Box<dyn Fn(&mut Value)>, &str)> = vec![
            (
                "duplicate fault id",
                Box::new(|o| o["fault_manifest"]["faults"][1]["fault_id"] = json!("SAMPLE-F1")),
                "/fault_manifest/faults/1/fault_id",
            ),
            (
                "unknown capability",
                Box::new(|o| {
                    o["fault_manifest"]["faults"][1]["class"]["capabilities"] = json!(["Z9"])
                }),
                "/fault_manifest/faults/1/class/capabilities/0",
            ),
            (
                "unknown challenge",
                Box::new(|o| {
                    o["fault_manifest"]["faults"][0]["class"]["challenge_ids"] = json!(["AQC-Z9"])
                }),
                "/fault_manifest/faults/0/class/challenge_ids/0",
            ),
            (
                "unknown tier",
                Box::new(|o| {
                    o["fault_manifest"]["faults"][1]["expected_detection"]["tiers"] = json!(["G9"])
                }),
                "/fault_manifest/faults/1/expected_detection/tiers/0",
            ),
            (
                "gate W fault without artifact flow",
                Box::new(|o| {
                    o["fault_manifest"]["faults"][0]
                        .as_object_mut()
                        .unwrap()
                        .remove("artifact_flow");
                }),
                "/fault_manifest/faults/0/artifact_flow",
            ),
            (
                "KEEP to another path",
                Box::new(|o| {
                    o["path_map_oracle"]["entries"][0]["expected_target_paths"] =
                        json!(["example/elsewhere.md"])
                }),
                "/path_map_oracle/entries/0/expected_target_paths",
            ),
            (
                "MOVE to itself",
                Box::new(|o| {
                    o["path_map_oracle"]["entries"][1]["expected_target_paths"] =
                        json!(["example/spec-a.md"])
                }),
                "/path_map_oracle/entries/1/expected_target_paths",
            ),
            (
                "indexed and never indexed",
                Box::new(|o| {
                    o["memory_oracle"]["must_never_be_indexed"][0]["ref"] =
                        json!("example/spec-b.md")
                }),
                "/memory_oracle/must_be_indexed/0/ref",
            ),
            (
                "retrieval returns never-indexed material",
                Box::new(|o| {
                    o["memory_oracle"]["expected_retrieval_results"][0]["must_include"] =
                        json!(["example/.env"])
                }),
                "/memory_oracle/expected_retrieval_results/0/must_include",
            ),
            (
                "superseded without successor",
                Box::new(|o| {
                    o["memory_oracle"]["expected_status"][1]
                        .as_object_mut()
                        .unwrap()
                        .remove("superseded_by");
                }),
                "/memory_oracle/expected_status/1/superseded_by",
            ),
            (
                "path map contradicts memory oracle",
                Box::new(|o| {
                    o["path_map_oracle"]["entries"][0]["indexing_expectation"] =
                        json!("NEVER_INDEX")
                }),
                "/path_map_oracle/entries/0/indexing_expectation",
            ),
            (
                "oracle stored in the public suite",
                Box::new(|o| {
                    o["separation"]["oracle_storage"] =
                        json!("example/public-suite/hidden/oracle.json")
                }),
                "/separation/oracle_storage",
            ),
            (
                "brownfield without path map",
                Box::new(|o| {
                    o.as_object_mut().unwrap().remove("path_map_oracle");
                }),
                "/path_map_oracle",
            ),
            (
                "visible oracle",
                Box::new(|o| o["visibility"] = json!("PUBLIC")),
                "/visibility",
            ),
            (
                "builder-authored oracle",
                Box::new(|o| o["custody"]["owner_role"] = json!("BUILDER")),
                "/custody/owner_role",
            ),
            (
                "another format version",
                Box::new(|o| o["format_sha256"] = json!("1".repeat(64))),
                "/format_sha256",
            ),
        ];
        for (name, mutate, at) in cases {
            let mut o = sample_oracle();
            mutate(&mut o);
            let p = problems(&o);
            assert!(
                p.iter().any(|x| x["at"] == at),
                "{name}: expected a violation at {at}: {p:#?}"
            );
        }
    }

    #[test]
    fn score_arithmetic_is_checked() {
        let o = sample_oracle();
        let cases: Vec<(&str, Box<dyn Fn(&mut Value)>, &str)> = vec![
            (
                "value is not the quotient",
                Box::new(|r| {
                    r["metrics"]["injected_defect_detection_recall"]["value"] = json!(0.9)
                }),
                "/metrics/injected_defect_detection_recall/value",
            ),
            (
                "recall disagrees with outcomes",
                Box::new(|r| {
                    r["metrics"]["injected_defect_detection_recall"] =
                        json!({"numerator": 2, "denominator": 2, "value": 1.0})
                }),
                "/metrics/injected_defect_detection_recall",
            ),
            (
                "severity accuracy disagrees",
                Box::new(|r| {
                    r["metrics"]["severity_accuracy"] =
                        json!({"numerator": 0, "denominator": 1, "value": 0.0})
                }),
                "/metrics/severity_accuracy",
            ),
            (
                "undetected fault credited",
                Box::new(|r| r["per_fault_outcomes"][1]["severity_correct"] = json!(true)),
                "/per_fault_outcomes/1/severity_correct",
            ),
            (
                "false-positive count",
                Box::new(|r| r["metrics"]["false_positives"]["count"] = json!(3)),
                "/metrics/false_positives/count",
            ),
            (
                "missing metric",
                Box::new(|r| {
                    r["metrics"]
                        .as_object_mut()
                        .unwrap()
                        .remove("human_gate_correctness");
                }),
                "/metrics/human_gate_correctness",
            ),
        ];
        for (name, mutate, at) in cases {
            let mut r = sample_report(&o);
            mutate(&mut r);
            let p = problems(&r);
            assert!(
                p.iter().any(|x| x["at"] == at),
                "{name}: expected a violation at {at}: {p:#?}"
            );
        }
    }

    #[test]
    fn a_score_report_is_bound_to_its_sealed_oracle() {
        let o = sample_oracle();
        let r = sample_report(&o);
        // the oracle changes after sealing
        let mut o2 = o.clone();
        o2["fault_manifest"]["faults"][1]["expected_severity"] = json!("LOW");
        let x = cross_check(&r, &o2);
        assert!(
            x.iter().any(|v| v["at"] == "/binding/oracle_sha256"),
            "{x:#?}"
        );
        // a fault goes unscored
        let mut r2 = r.clone();
        r2["per_fault_outcomes"].as_array_mut().unwrap().pop();
        let x = cross_check(&r2, &o);
        assert!(x.iter().any(|v| v["at"] == "/per_fault_outcomes"), "{x:#?}");
        // a severity judged correct that the oracle says is wrong
        let mut r3 = r.clone();
        r3["per_fault_outcomes"][0]["observed_severity"] = json!("LOW");
        let x = cross_check(&r3, &o);
        assert!(
            x.iter()
                .any(|v| v["at"] == "/per_fault_outcomes/0/severity_correct"),
            "{x:#?}"
        );
    }

    #[test]
    fn the_hidden_oracle_is_kept_out_of_the_public_suite_and_the_repository() {
        let base =
            std::env::temp_dir().join(format!("gov-oracle-sep-{}", crate::util::short_uuid()));
        let public = base.join("public");
        let repo = base.join("repo");
        let custody = base.join("custody");
        for d in [&public, &repo, &custody] {
            std::fs::create_dir_all(d).unwrap();
        }
        std::fs::write(public.join("README.md"), "public qualification suite\n").unwrap();
        let o = sample_oracle();
        let text = serde_json::to_string_pretty(&o).unwrap();
        let held = custody.join("oracle.json");
        std::fs::write(&held, &text).unwrap();
        let opts = ValidateOptions {
            oracle: None,
            public_suites: vec![public.clone()],
            repositories: vec![repo.clone()],
        };
        let ok = validate_file(&held, &opts).expect("an oracle in verifier custody is separate");
        assert_eq!(ok["separation"]["findings"], 0);
        // stored inside the repository
        let inside = repo.join("oracle.json");
        std::fs::write(&inside, &text).unwrap();
        assert_eq!(
            validate_file(&inside, &opts).unwrap_err().code,
            "ORACLE_SEPARATION_VIOLATED"
        );
        std::fs::remove_file(&inside).unwrap();
        // a copy leaked into the public suite
        std::fs::write(public.join("copy.yaml"), crate::util::to_yaml(&o).unwrap()).unwrap();
        assert_eq!(
            validate_file(&held, &opts).unwrap_err().code,
            "ORACLE_SEPARATION_VIOLATED"
        );
        std::fs::remove_file(public.join("copy.yaml")).unwrap();
        // a hidden truth quoted verbatim inside the repository
        std::fs::write(
            repo.join("notes.md"),
            "example/spec-b.md is the current required input; example/spec-a.md is superseded\n",
        )
        .unwrap();
        assert_eq!(
            validate_file(&held, &opts).unwrap_err().code,
            "ORACLE_SEPARATION_VIOLATED"
        );
        assert!(scan_for_hidden_oracle_material(&repo).is_empty());
        std::fs::write(
            repo.join("FM-0001.yaml"),
            "id: FM-0001\ntype: fault-manifest\ntitle: t\nstatus: ACTIVE\n",
        )
        .unwrap();
        assert_eq!(scan_for_hidden_oracle_material(&repo).len(), 1);
        let _ = std::fs::remove_dir_all(&base);
    }

    #[test]
    fn a_report_is_validated_against_the_oracle_file_it_names() {
        let base =
            std::env::temp_dir().join(format!("gov-oracle-bind-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&base).unwrap();
        let o = sample_oracle();
        let r = sample_report(&o);
        std::fs::write(base.join("oracle.yaml"), crate::util::to_yaml(&o).unwrap()).unwrap();
        std::fs::write(base.join("report.json"), serde_json::to_string(&r).unwrap()).unwrap();
        let opts = ValidateOptions {
            oracle: Some(base.join("oracle.yaml")),
            ..Default::default()
        };
        let v = validate_file(&base.join("report.json"), &opts).expect("bound");
        assert_eq!(v["binding_verified"]["oracle_sha256"], hash_value(&o));
        let mut o2 = o.clone();
        o2["memory_oracle"]["expected_retrieval_results"][0]["top_k"] = json!(10);
        std::fs::write(base.join("oracle.yaml"), crate::util::to_yaml(&o2).unwrap()).unwrap();
        assert_eq!(
            validate_file(&base.join("report.json"), &opts)
                .unwrap_err()
                .code,
            "ORACLE_SCORE_BINDING_MISMATCH"
        );
        let _ = std::fs::remove_dir_all(&base);
    }
}
