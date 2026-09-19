//! Product-test results as governed, freshness-bound evidence (Contract v3:751-761 Gate O1, :980 and :1004 Gate U;
//! BC-P2-43).
//!
//! * **Per family.** Each product test family (TEST_POLICY.product_families) that the project can run is executed and
//!   recorded separately. Families come from `PROJECT_POLICY.tests.families.<family>: {command, cwd?, covers?}`; without
//!   that, the ecosystem conventions are used where they identify families (Cargo: `unit` = library/binary targets,
//!   `integration` = `tests/*.rs`), otherwise the configured or detected command is recorded as one unattributed
//!   family `all`.
//! * **Governed evidence.** Every run is persisted as an `audit` record (`scope: product-tests`, `state_class:
//!   EVIDENCE`) with per-family status, exit code, command, the paths the family covers and the **key** of those
//!   covered inputs, plus provenance (runtime, repository, actor, time).
//! * **Freshness-bound.** A family's evidence is current only while the digest of the files it covers (and its command)
//!   is unchanged.
//! * **Health.** A failing family is a HIGH finding of the `product_test_health` family and of doctor D030, which makes
//!   the repository UNHEALTHY and hard-blocks `task.close` for work under the family's covered paths and
//!   `release.build`/`update.apply` (see `crate::scheduler::catalogue`).
//! * **Close.** [`enforce_close`] verifies a report's test outcome from this evidence instead of the report's own
//!   claim (integration point for `orchestration::tasks::close`, WS-5).
//! * **Command status.** A failed suite is returned as the typed error `PRODUCT_TESTS_FAILED` (non-zero exit), never as a
//!   successful command.
use super::currency::{self, Snapshot};
use crate::records::{new_record, save_record, RecordStore};
use crate::util::{glob_match, hash_value, now_iso};
use crate::{GovError, Project, Result};
use serde_json::{json, Map, Value};
use std::collections::BTreeMap;
use std::path::Path;

pub const SCOPE: &str = "product-tests";
/// Every source-class file (the fallback coverage of an unattributed command).
pub const ALL_SOURCE: &str = "**";

#[derive(Debug, Clone)]
pub struct FamilyPlan {
    pub family: String,
    pub command: Vec<String>,
    /// Working directory relative to the repository root ("" = root).
    pub cwd: String,
    /// Repository-relative globs of the source-class files the family's outcome depends on.
    pub covers: Vec<String>,
    /// Where the plan came from (`PROJECT_POLICY.tests.families`, `PROJECT_POLICY.tests.product_test_command`,
    /// `ecosystem:<id>`).
    pub source: String,
    /// The family is known (false for the unattributed aggregate `all`).
    pub attributed: bool,
}

impl FamilyPlan {
    fn to_value(&self) -> Value {
        json!({"family": self.family, "command": self.command, "cwd": self.cwd, "covers": self.covers, "source": self.source, "attributed": self.attributed})
    }
}

fn str_list(v: &Value) -> Vec<String> {
    v.as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default()
}

fn prefixed(dir: &str, rel: &str) -> String {
    if dir.is_empty() || dir == "." {
        rel.to_string()
    } else {
        format!("{}/{}", dir.trim_end_matches('/'), rel)
    }
}

fn cargo_plans(root: &Path, dir: &str) -> Vec<FamilyPlan> {
    let d = if dir.is_empty() {
        root.to_path_buf()
    } else {
        root.join(dir)
    };
    let manifest = std::fs::read_to_string(d.join("Cargo.toml")).unwrap_or_default();
    let has_lib = d.join("src").join("lib.rs").exists() || manifest.contains("[lib]");
    let has_bins = d.join("src").join("main.rs").exists()
        || d.join("src").join("bin").is_dir()
        || manifest.contains("[[bin]]");
    let has_tests = std::fs::read_dir(d.join("tests"))
        .map(|rd| {
            rd.filter_map(|e| e.ok())
                .any(|e| e.path().extension().map(|x| x == "rs").unwrap_or(false))
        })
        .unwrap_or(false);
    let common: Vec<String> = ["Cargo.toml", "Cargo.lock", "build.rs"]
        .iter()
        .map(|f| prefixed(dir, f))
        .collect();
    let mut out = vec![];
    if has_lib || has_bins {
        let mut cmd: Vec<String> = vec!["cargo".into(), "test".into()];
        if has_lib {
            cmd.push("--lib".into());
        }
        if has_bins {
            cmd.push("--bins".into());
        }
        let mut covers = vec![prefixed(dir, "src/**")];
        covers.extend(common.clone());
        out.push(FamilyPlan {
            family: "unit".into(),
            command: cmd,
            cwd: dir.to_string(),
            covers,
            source: "ecosystem:rust-cargo".into(),
            attributed: true,
        });
    }
    if has_tests {
        let mut covers = vec![prefixed(dir, "src/**"), prefixed(dir, "tests/**")];
        covers.extend(common);
        out.push(FamilyPlan {
            family: "integration".into(),
            command: vec!["cargo".into(), "test".into(), "--test".into(), "*".into()],
            cwd: dir.to_string(),
            covers,
            source: "ecosystem:rust-cargo".into(),
            attributed: true,
        });
    }
    out
}

/// The product test families this project can run, and notes about how they were resolved.
pub fn plan(p: &Project) -> (Vec<FamilyPlan>, Vec<String>) {
    let pp = p.project_policy();
    let tests = &pp["tests"];
    let vocabulary = p.policies().get_list("TEST_POLICY", "product_families");
    let mut notes = vec![];
    if let Some(fams) = tests.get("families").and_then(|f| f.as_object()) {
        let mut out = vec![];
        for (fam, cfg) in fams {
            let command = str_list(&cfg["command"]);
            if command.is_empty() {
                notes.push(format!(
                    "PROJECT_POLICY.tests.families.{fam} declares no command; the family cannot run"
                ));
                continue;
            }
            if !vocabulary.is_empty() && !vocabulary.contains(fam) {
                notes.push(format!(
                    "PROJECT_POLICY.tests.families.{fam} is outside TEST_POLICY.product_families {vocabulary:?}"
                ));
            }
            let mut covers = str_list(&cfg["covers"]);
            if covers.is_empty() {
                covers = vec![ALL_SOURCE.into()];
            }
            out.push(FamilyPlan {
                family: fam.clone(),
                command,
                cwd: cfg["cwd"].as_str().unwrap_or("").to_string(),
                covers,
                source: format!("PROJECT_POLICY.tests.families.{fam}"),
                attributed: true,
            });
        }
        return (out, notes);
    }
    let legacy = str_list(&tests["product_test_command"]);
    if !legacy.is_empty() {
        notes.push("PROJECT_POLICY.tests.product_test_command is one command for every family: its result is recorded as the unattributed family 'all' (declare PROJECT_POLICY.tests.families to attribute results per family)".into());
        return (
            vec![FamilyPlan {
                family: "all".into(),
                command: legacy,
                cwd: String::new(),
                covers: vec![ALL_SOURCE.into()],
                source: "PROJECT_POLICY.tests.product_test_command".into(),
                attributed: false,
            }],
            notes,
        );
    }
    let eco = crate::capabilities::ecosystems::detect(&p.root, &[p.contract().root("product")]);
    let Some(e) = eco["ecosystems"].as_array().and_then(|a| {
        a.iter()
            .find(|e| e["test"].is_object() && e["available"].as_bool().unwrap_or(false))
    }) else {
        notes.push("no product test command configured (PROJECT_POLICY.tests) or detectable with an available toolchain (capability gap)".into());
        return (vec![], notes);
    };
    let id = e["id"].as_str().unwrap_or("").to_string();
    let dir = e["dir"].as_str().unwrap_or("").to_string();
    if id == "rust-cargo" {
        let plans = cargo_plans(&p.root, &dir);
        if !plans.is_empty() {
            return (plans, notes);
        }
    }
    notes.push(format!("ecosystem {id} runs every family with one command: its result is recorded as the unattributed family 'all' (declare PROJECT_POLICY.tests.families to attribute results per family)"));
    (
        vec![FamilyPlan {
            family: "all".into(),
            command: str_list(&e["test"]["command"]),
            cwd: dir,
            covers: vec![ALL_SOURCE.into()],
            source: format!("ecosystem:{id}"),
            attributed: false,
        }],
        notes,
    )
}

fn covered(plan_covers: &[String], rel: &str) -> bool {
    plan_covers
        .iter()
        .any(|c| c == ALL_SOURCE || glob_match(c, rel))
}

/// The freshness key of a family: its command/cwd and the digests of the source-class files it covers.
pub fn family_key(snap: &Snapshot, plan: &FamilyPlan) -> String {
    let files: Vec<(&String, &String)> = snap
        .files
        .iter()
        .filter(|(rel, (class, _))| class == currency::SOURCE && covered(&plan.covers, rel))
        .map(|(rel, (_, d))| (rel, d))
        .collect();
    hash_value(
        &json!({"family": plan.family, "command": plan.command, "cwd": plan.cwd, "covers": plan.covers, "files": files}),
    )
}

fn tail(s: &str, n: usize) -> String {
    let lines: Vec<&str> = s.lines().collect();
    lines[lines.len().saturating_sub(n)..].join("\n")
}

/// Execute the planned families (all, or those named in `only`), record the governed evidence, refresh the product
/// test health state, and return the per-family results. A failing family returns `PRODUCT_TESTS_FAILED`.
pub fn run(p: &Project, only: &[String]) -> Result<Value> {
    let (plans, notes) = plan(p);
    let plans: Vec<FamilyPlan> = plans
        .into_iter()
        .filter(|pl| only.is_empty() || only.contains(&pl.family))
        .collect();
    if plans.is_empty() {
        return Ok(
            json!({"ran": false, "reason": notes.join("; "), "status": "not_applicable_with_reason", "families": {}, "notes": notes}),
        );
    }
    let started_at = now_iso();
    let mut results: Vec<(FamilyPlan, i32, String, String, u128)> = vec![];
    for pl in &plans {
        let cwd = if pl.cwd.is_empty() {
            p.root.clone()
        } else {
            p.root.join(&pl.cwd)
        };
        let t0 = std::time::Instant::now();
        let (code, out, err) = crate::util::run_cmd(&pl.command, &cwd)?;
        results.push((pl.clone(), code, out, err, t0.elapsed().as_millis()));
    }
    // the key is taken after the run: a run that writes a lock file (e.g. Cargo.lock) is bound to the state it left
    let snap = Snapshot::take(p)?;
    let mut fams = Map::new();
    let mut failed = vec![];
    for (pl, code, out, err, ms) in &results {
        let status = if *code == 0 { "passed" } else { "failed" };
        if *code != 0 {
            failed.push(pl.family.clone());
        }
        fams.insert(
            pl.family.clone(),
            json!({"status": status, "exit": code, "command": pl.command, "cwd": pl.cwd, "covers": pl.covers, "source": pl.source,
                   "attributed": pl.attributed, "key": family_key(&snap, pl), "duration_ms": *ms as u64,
                   "stdout_tail": tail(out, 20), "stderr_tail": tail(err, 20)}),
        );
    }
    let verdict = if failed.is_empty() {
        "PASSED"
    } else {
        "FAILED"
    };
    let store = RecordStore::load(&p.root);
    let id = store.next_id("audit");
    let rec = new_record(
        "audit",
        &id,
        &format!("Product test run {id} ({verdict})"),
        json!({
            "scope": SCOPE, "state_class": "EVIDENCE", "verdict": verdict, "green": false, "families": fams,
            "failed_families": failed, "notes": notes, "run_at": now_iso(), "started_at": started_at,
            "auditor_role": p.role, "session": p.session_id,
            "runtime": currency::runtime_identity(), "repository": crate::scheduler::repository_state(p, &snap),
            "actor": {"role": p.role, "session": p.session_id, "pid": std::process::id()},
        }),
    );
    save_record(&p.root, &rec)?;
    let first = &results[0].0;
    let worst_exit = results.iter().map(|r| r.1).find(|c| *c != 0).unwrap_or(0);
    let status = if failed.is_empty() {
        "passed"
    } else {
        "failed"
    };
    let ev = json!({"ran": true, "status": status, "verdict": verdict, "record": id, "families": fams, "failed_families": failed,
                    "command": first.command, "cwd": p.root.join(&first.cwd).to_string_lossy(), "source": first.source,
                    "exit": worst_exit, "notes": notes, "at": now_iso()});
    crate::observability::emit(
        p,
        "product.suite",
        json!({"status": status, "exit": worst_exit, "source": first.source, "command": first.command, "record": id, "families": results.iter().map(|r| json!({"family": r.0.family, "exit": r.1})).collect::<Vec<_>>()}),
    )?;
    // keep the index fresh (the record is evidence) and refresh the health state the guard reads
    if p.db_path().exists() {
        let _ = crate::memory::indexer::rebuild(
            p,
            crate::memory::indexer::IndexOptions {
                incremental: true,
                ..Default::default()
            },
        );
    }
    let mut o = crate::scheduler::RunOptions::new(
        crate::scheduler::Tier::G2,
        crate::scheduler::Trigger::new("product.tests").with_subject(&id),
    );
    o.selection = crate::scheduler::Selection::Explicit(vec!["product_test_health".into()]);
    o.surface = "product-tests".into();
    o.record = crate::scheduler::RecordPolicy::Never;
    let health = crate::scheduler::run_suite(p, &o)
        .map(|h| json!({"health_result": h.result["id"], "state": h.result["state"]}))
        .unwrap_or(Value::Null);
    let mut ev = ev;
    ev["health"] = health;
    if !failed.is_empty() {
        return Err(GovError::new(
            "PRODUCT_TESTS_FAILED",
            format!(
                "product test famil{} {} failed (recorded as {id}); the failure is governed evidence: health is UNHEALTHY and close of covered work is refused until a passing run is recorded",
                if failed.len() == 1 { "y" } else { "ies" },
                failed.join(", ")
            ),
        )
        .with_details(ev));
    }
    Ok(ev)
}

/// Product-test records, newest first.
pub fn latest_records(p: &Project) -> Vec<Value> {
    let store = RecordStore::load(&p.root);
    let mut v: Vec<Value> = store
        .of_type("audit")
        .into_iter()
        .filter(|r| r.get("scope") == SCOPE)
        .map(|r| r.data.clone())
        .collect();
    v.sort_by(|a, b| {
        let ka = (
            a["run_at"].as_str().unwrap_or("").to_string(),
            a["id"].as_str().unwrap_or("").to_string(),
        );
        let kb = (
            b["run_at"].as_str().unwrap_or("").to_string(),
            b["id"].as_str().unwrap_or("").to_string(),
        );
        kb.cmp(&ka)
    });
    v
}

/// The latest recorded entry per family: family → (record id, entry).
pub fn latest_per_family(p: &Project) -> BTreeMap<String, (String, Value)> {
    let mut out = BTreeMap::new();
    for r in latest_records(p) {
        let rid = r["id"].as_str().unwrap_or("").to_string();
        if let Some(fams) = r["families"].as_object() {
            for (fam, e) in fams {
                out.entry(fam.clone())
                    .or_insert_with(|| (rid.clone(), e.clone()));
            }
        }
    }
    out
}

/// Per planned family: latest outcome, whether its evidence is current, and the record that holds it.
pub fn status(p: &Project, snap: Option<&Snapshot>) -> Value {
    let (plans, notes) = plan(p);
    if plans.is_empty() {
        return json!({"applicable": false, "notes": notes, "families": {}});
    }
    let owned;
    let snap = match snap {
        Some(s) => s,
        None => match Snapshot::take(p) {
            Ok(s) => {
                owned = s;
                &owned
            }
            Err(e) => return json!({"applicable": true, "error": e.code}),
        },
    };
    let ev = latest_per_family(p);
    let mut fams = Map::new();
    for pl in &plans {
        let key = family_key(snap, pl);
        let row = match ev.get(&pl.family) {
            None => {
                json!({"status": "missing", "current": false, "covers": pl.covers, "attributed": pl.attributed})
            }
            Some((rid, e)) => {
                json!({"status": e["status"], "current": e["key"].as_str() == Some(key.as_str()), "record": rid, "exit": e["exit"], "covers": pl.covers, "attributed": pl.attributed})
            }
        };
        fams.insert(pl.family.clone(), row);
    }
    json!({"applicable": true, "notes": notes, "families": fams, "plan": plans.iter().map(|p| p.to_value()).collect::<Vec<_>>()})
}

/// Findings and detail for the `product_test_health` family and doctor D030.
pub fn health_findings(p: &Project, snap: Option<&Snapshot>) -> (Vec<Value>, Value) {
    let st = status(p, snap);
    if !st["applicable"].as_bool().unwrap_or(false) {
        return (vec![], st);
    }
    let mut out = vec![];
    let (mut failing, mut stale, mut missing) = (0, 0, 0);
    for (fam, row) in st["families"].as_object().cloned().unwrap_or_default() {
        match row["status"].as_str() {
            Some("failed") => {
                failing += 1;
                out.push(json!({"severity": "high", "family": "product_test_health", "message": format!("product test family '{fam}' FAILED in {} (exit {}){}: work under its covered paths cannot close and releases are refused until a passing run is recorded (`gov verify product`)", row["record"].as_str().unwrap_or("?"), row["exit"], if row["current"].as_bool().unwrap_or(false) { "" } else { "; covered inputs changed since" }), "path": Value::Null, "covers": row["covers"]}));
            }
            Some("passed") if !row["current"].as_bool().unwrap_or(false) => {
                stale += 1;
                out.push(json!({"severity": "low", "family": "product_test_health", "message": format!("product test evidence for family '{fam}' ({}) is stale: its covered inputs changed since it was recorded; run `gov verify product`", row["record"].as_str().unwrap_or("?")), "path": Value::Null}));
            }
            Some("missing") => {
                missing += 1;
                out.push(json!({"severity": "low", "family": "product_test_health", "message": format!("no recorded product-test evidence for family '{fam}'; run `gov verify product`"), "path": Value::Null}));
            }
            _ => {}
        }
    }
    let mut detail = st;
    detail["slo"] = json!({"name": "product-test health", "failing_families": failing, "threshold_failing_families": 0, "breached": failing > 0, "stale": stale, "missing": missing});
    (out, detail)
}

/// **Close verification (integration point for `orchestration::tasks::close`, WS-5).** The test outcome of a close is
/// taken from recorded evidence, never from the report alone:
///
/// 1. a family whose latest recorded run failed refuses the close of any task that touches its covered paths;
/// 2. a report claiming `tests.status: passed` needs current, passing evidence for every family covering the touched
///    paths (every family when none covers them); missing or stale evidence refuses the close.
///
/// Returns notes to record on the report when the close may proceed.
pub fn enforce_close(
    p: &Project,
    task: &Value,
    report: &Value,
    touched: &[String],
) -> Result<Vec<String>> {
    let claimed = report["tests"]["status"].as_str().unwrap_or("").to_string();
    let (plans, notes) = plan(p);
    let task_id = task["id"].as_str().unwrap_or("?");
    if plans.is_empty() {
        if claimed == "passed" {
            return Err(GovError::new("PRODUCT_TEST_EVIDENCE_REQUIRED", format!("{task_id}: the report claims tests passed, but no product test can run in this project ({}); a claim cannot stand in for evidence — report tests.status not_applicable_with_reason", notes.join("; "))));
        }
        return Ok(vec![]);
    }
    let snap = Snapshot::take(p)?;
    let ev = latest_per_family(p);
    let touched_src: Vec<&String> = touched
        .iter()
        .filter(|f| currency::classify_path(f) == currency::SOURCE)
        .collect();
    let covering: Vec<&FamilyPlan> = plans
        .iter()
        .filter(|pl| touched_src.iter().any(|f| covered(&pl.covers, f)))
        .collect();
    for pl in &plans {
        if let Some((rid, e)) = ev.get(&pl.family) {
            if e["status"] == "failed" && covering.iter().any(|c| c.family == pl.family) {
                return Err(GovError::new("PRODUCT_TESTS_FAILED", format!("{task_id} touches paths covered by product test family '{}', whose latest recorded run {rid} FAILED; record a passing run (`gov verify product`) before closing", pl.family)).with_details(json!({"family": pl.family, "record": rid, "touched": touched_src})));
            }
        }
    }
    if claimed == "passed" {
        let relevant: Vec<&FamilyPlan> = if covering.is_empty() {
            plans.iter().collect()
        } else {
            covering
        };
        for pl in relevant {
            let key = family_key(&snap, pl);
            match ev.get(&pl.family) {
                None => return Err(GovError::new("PRODUCT_TEST_EVIDENCE_REQUIRED", format!("{task_id}: the report claims tests passed, but no product test run is recorded for family '{}'; run `gov verify product`", pl.family))),
                Some((rid, e)) if e["status"] != "passed" => return Err(GovError::new("PRODUCT_TESTS_FAILED", format!("{task_id}: the report claims tests passed, but the latest recorded run of family '{}' ({rid}) {}", pl.family, e["status"].as_str().unwrap_or("did not pass")))),
                Some((rid, e)) if e["key"].as_str() != Some(key.as_str()) => return Err(GovError::new("PRODUCT_TEST_EVIDENCE_STALE", format!("{task_id}: the report claims tests passed, but the recorded run of family '{}' ({rid}) predates changes to its covered inputs; run `gov verify product`", pl.family))),
                _ => {}
            }
        }
    }
    Ok(vec![])
}
