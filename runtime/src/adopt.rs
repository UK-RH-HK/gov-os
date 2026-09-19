//! `gov adopt`: staged, path-first, memory-safe brownfield adoption (framework §79, protocol A0-A11) with an
//! immutable evidence tree and independence enforced by session/role separation and verdict gates.
use crate::kernel::{install_kernel, resolve_kernel_source};
use crate::lock::write_lock;
use crate::memory::db::RuntimeDb;
use crate::migrations::{
    classify, executor, extraction, identity, inventory, ownership, planner, references, verify,
};
use crate::records::{new_record, save_record};
use crate::util::{
    glob_match, now_iso, read_json, read_text, read_yaml, write_json, write_text, write_yaml,
};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

pub const EVIDENCE: &str = "spec/audits/GOVERNANCE-ADOPTION";
pub const STAGES: &[&str] = &[
    "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11",
];

fn ev(root: &Path) -> PathBuf {
    root.join(EVIDENCE)
}
fn baseline_path(root: &Path) -> PathBuf {
    ev(root).join("00-BASELINE.yaml")
}
fn load_baseline(root: &Path) -> Result<Value> {
    read_yaml(&baseline_path(root)).map_err(|_| {
        GovError::new(
            "ADOPTION_NOT_STARTED",
            "run `gov adopt baseline` (A0) first",
        )
    })
}
fn save_baseline(root: &Path, b: &Value) -> Result<()> {
    write_yaml(&baseline_path(root), b)
}
fn set_stage(
    root: &Path,
    stage: &str,
    status: &str,
    extra: Option<(&str, Value)>,
) -> Result<Value> {
    let mut b = load_baseline(root)?;
    b["stage_status"][stage] = json!(status);
    b["stage_times"][stage] = json!(now_iso());
    if let Some((k, v)) = extra {
        b[k] = v;
    }
    save_baseline(root, &b)?;
    Ok(b)
}
fn require_stage(b: &Value, stage: &str) -> Result<()> {
    if b["stage_status"][stage].as_str() != Some("done") {
        return Err(GovError::new(
            "STAGE_ORDER",
            format!("stage {stage} must be complete first (protocol order A0→A11)"),
        ));
    }
    Ok(())
}
fn require_verdict(b: &Value, key: &str, accepted: &[&str]) -> Result<()> {
    let v = b["verdicts"][key]["verdict"].as_str().unwrap_or("");
    if !accepted.contains(&v) {
        return Err(GovError::new(
            "VERDICT_REQUIRED",
            format!("independent verdict '{key}' must be one of {accepted:?} (current: '{v}')"),
        ));
    }
    Ok(())
}
fn write_md(root: &Path, name: &str, text: &str) -> Result<String> {
    let p = ev(root).join(name);
    write_text(&p, text)?;
    Ok(format!("{EVIDENCE}/{name}"))
}
fn scanner_for(root: &Path) -> crate::security::secrets::SecretScanner {
    let p = Project::open(root);
    if p.is_installed() {
        return p.secret_scanner().clone();
    }
    match crate::kernel::canonical_root()
        .or_else(|| std::env::var("GOV_KERNEL_SOURCE").ok().map(PathBuf::from))
    {
        Some(r) => {
            let pol = read_yaml(
                &r.join("framework")
                    .join("policies")
                    .join("SECURITY_POLICY.yaml"),
            )
            .or_else(|_| read_yaml(&r.join("policies").join("SECURITY_POLICY.yaml")))
            .unwrap_or(json!({}));
            crate::security::secrets::SecretScanner::from_policies(&pol, &json!({}))
        }
        None => crate::security::secrets::SecretScanner::default_scanner(),
    }
}

// ---------------------------------------------------------------- A0
pub fn a0_baseline(root: &Path, session: &str) -> Result<Value> {
    std::fs::create_dir_all(ev(root))?;
    let p = Project::open(root);
    let git = p.git_available();
    let dirty = if git { p.git_dirty_files() } else { vec![] };
    let mut interrupted = json!({"detected": false, "items": []});
    let partial_gov =
        root.join("governance").exists() && !root.join("governance/framework.lock").exists();
    if partial_gov {
        interrupted["detected"] = json!(true);
        interrupted["items"].as_array_mut().unwrap().push(json!({"kind": "partial_governance_dir", "classification": "PARTIAL_SHOULD_ROLL_BACK", "note": "governance/ exists without framework.lock"}));
    }
    if p.is_installed() {
        if let Ok(r) = crate::recovery::recover(&p, true) {
            if !r["items"].as_array().map(|a| a.is_empty()).unwrap_or(true) {
                interrupted["detected"] = json!(true);
                interrupted["items"] = r["items"].clone();
            }
        }
    }
    if baseline_path(root).exists() {
        if let Ok(prev) = read_yaml(&baseline_path(root)) {
            if let Some(st) = prev["stage_status"].as_object() {
                for (k, v) in st {
                    if v == "in_progress" {
                        interrupted["detected"] = json!(true);
                        interrupted["items"].as_array_mut().unwrap().push(json!({"kind": "adoption_stage", "stage": k, "classification": "UNKNOWN"}));
                    }
                }
            }
        }
    }
    // baseline tests via ecosystem detection (record, never fail)
    let eco = crate::capabilities::ecosystems::detect(root, &["product/".into()]);
    let mut baseline_tests =
        json!({"ran": false, "reason": "no runnable native test command detected"});
    if let Some(e) = eco["ecosystems"].as_array().and_then(|a| {
        a.iter()
            .find(|e| e["test"].is_object() && e["available"].as_bool().unwrap_or(false))
    }) {
        let cmd: Vec<String> = e["test"]["command"]
            .as_array()
            .unwrap()
            .iter()
            .filter_map(|x| x.as_str().map(|s| s.to_string()))
            .collect();
        let cwd = root.join(e["dir"].as_str().unwrap_or(""));
        if let Ok((code, out, err)) = crate::util::run_cmd(&cmd, &cwd) {
            baseline_tests = json!({"ran": true, "ecosystem": e["id"], "command": cmd, "exit": code, "status": if code == 0 { "passed" } else { "failed" }, "stdout_tail": out.lines().rev().take(5).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join("\n"), "stderr_tail": err.lines().rev().take(5).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join("\n")});
        }
    }
    let b = json!({"adoption_id": format!("ADOPT-{}", crate::util::today()), "started_at": now_iso(), "session": session, "planner_session": session, "commit": if git { p.git_commit() } else { "no-git".into() }, "branch": if git { p.git_branch() } else { "no-git".into() },
        "dirty_files": dirty, "untracked_files": [], "baseline_tests": baseline_tests, "interrupted_work": interrupted, "ecosystems": eco, "stage_status": {"A0": "done"}, "stage_times": {"A0": now_iso()}, "verdicts": {}});
    save_baseline(root, &b)?;
    Ok(
        json!({"stage": "A0", "evidence": format!("{EVIDENCE}/00-BASELINE.yaml"), "commit": b["commit"], "dirty_files": b["dirty_files"].as_array().map(|a| a.len()).unwrap_or(0), "interrupted": b["interrupted_work"]["detected"], "baseline_tests": b["baseline_tests"]["status"], "freeze_advice": if b["interrupted_work"]["detected"].as_bool().unwrap_or(false) { "interrupted work detected: review items before A1; broad edits are frozen by protocol" } else { "clean baseline" }}),
    )
}

// ---------------------------------------------------------------- A1
pub fn a1_inventory(root: &Path) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A0")?;
    set_stage(root, "A1", "in_progress", None)?;
    let items = inventory::inventory(root, &scanner_for(root));
    let summary = inventory::summary(&items);
    let mut jl = String::new();
    for i in &items {
        jl.push_str(&serde_json::to_string(i)?);
        jl.push('\n');
    }
    write_text(&ev(root).join("01-COLD-INVENTORY.jsonl"), &jl)?;
    let mut md = format!("# 01 — Cold deterministic inventory\n\nFiles: {} · tracked: {} · bytes: {}\n\nNo semantic memory was consulted (protocol §6).\n\n## By kind\n\n| Kind | Count |\n|---|---|\n", summary["files"], summary["tracked"], summary["bytes"]);
    for (k, v) in summary["by_kind"].as_object().unwrap() {
        md.push_str(&format!("| {k} | {v} |\n"));
    }
    md.push_str("\n## Notable\n\n");
    for kind in [
        "package_manifest",
        "entrypoint",
        "provider_rules",
        "chat_store",
        "index_store",
        "old_governance",
        "database",
        "secret",
        "devops",
    ] {
        let ps: Vec<String> = items
            .iter()
            .filter(|i| {
                i["kinds"]
                    .as_array()
                    .map(|a| a.iter().any(|k| k == kind))
                    .unwrap_or(false)
            })
            .map(|i| i["path"].as_str().unwrap_or("").to_string())
            .collect();
        if !ps.is_empty() {
            md.push_str(&format!("- **{kind}**: {}\n", ps.join(", ")));
        }
    }
    write_md(root, "01-COLD-INVENTORY.md", &md)?;
    set_stage(
        root,
        "A1",
        "done",
        Some(("inventory_summary", summary.clone())),
    )?;
    Ok(
        json!({"stage": "A1", "summary": summary, "evidence": [format!("{EVIDENCE}/01-COLD-INVENTORY.md"), format!("{EVIDENCE}/01-COLD-INVENTORY.jsonl")]}),
    )
}

fn read_jsonl(p: &Path) -> Result<Vec<Value>> {
    Ok(read_text(p)?
        .lines()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect())
}

// ---------------------------------------------------------------- A2
pub fn a2_classify(root: &Path) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A1")?;
    set_stage(root, "A2", "in_progress", None)?;
    let items = read_jsonl(&ev(root).join("01-COLD-INVENTORY.jsonl"))?;
    let classified = classify::classify_all(root, &items);
    let mut jl = String::new();
    for c in &classified {
        jl.push_str(&serde_json::to_string(c)?);
        jl.push('\n');
    }
    write_text(&ev(root).join("02-CLASSIFICATION.jsonl"), &jl)?;
    write_md(
        root,
        "03-LEGACY-GOVERNANCE-MAP.md",
        &classify::legacy_map_markdown(&classified),
    )?;
    let mut by_class: std::collections::BTreeMap<String, usize> = std::collections::BTreeMap::new();
    let mut by_auth: std::collections::BTreeMap<String, usize> = std::collections::BTreeMap::new();
    for c in &classified {
        *by_class
            .entry(c["class"].as_str().unwrap_or("").into())
            .or_insert(0) += 1;
        *by_auth
            .entry(c["authority"].as_str().unwrap_or("").into())
            .or_insert(0) += 1;
    }
    let unknown = by_class.get("UNKNOWN").copied().unwrap_or(0);
    let conflicting = by_auth.get("UNKNOWN_OR_CONFLICTING").copied().unwrap_or(0);
    set_stage(
        root,
        "A2",
        "done",
        Some((
            "classification_summary",
            json!({"by_class": by_class, "by_authority": by_auth, "unknown": unknown, "conflicting": conflicting}),
        )),
    )?;
    Ok(
        json!({"stage": "A2", "classified": classified.len(), "by_class": by_class, "by_authority": by_auth, "unknown": unknown, "conflicting": conflicting, "evidence": [format!("{EVIDENCE}/02-CLASSIFICATION.jsonl"), format!("{EVIDENCE}/03-LEGACY-GOVERNANCE-MAP.md")]}),
    )
}

fn native_test_dir(root: &Path) -> Option<String> {
    for d in ["tests", "test", "product/tests", "src/tests", "spec"] {
        if root.join(d).is_dir() && d != "spec" {
            return Some(d.into());
        }
    }
    None
}

// ---------------------------------------------------------------- A3
/// The archive root migrations retire material into.
pub const ARCHIVE_ROOT: &str = "archive";
/// Stable ids of the two versioned adoption planning artefacts (BC-P2-21, Contract v3:1080 "migration plans").
pub const CATALOGUE_ID: &str = "PMAP-GOVERNANCE-ADOPTION";
pub const PLAN_ID: &str = "MPLAN-GOVERNANCE-ADOPTION";
const CATALOGUE_STEM: &str = "04-TARGET-PATH-MAP";
const PLAN_STEM: &str = "05-plan";

fn catalogue_meta_path(root: &Path) -> PathBuf {
    ev(root).join(format!("{CATALOGUE_STEM}.meta.json"))
}

fn write_catalogue(root: &Path, catalogue: &[Value]) -> Result<()> {
    let mut jl = String::new();
    for e in catalogue {
        jl.push_str(&serde_json::to_string(e)?);
        jl.push('\n');
    }
    write_text(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl")), &jl)
}

pub fn a3_map(root: &Path) -> Result<Value> {
    let b = load_baseline(root)?;
    a3_map_by(root, &identity::Actor::from_env_or_baseline(&b))
}

/// A3 with the producing actor recorded in every catalogue entry (W1 producer/provenance).
pub fn a3_map_by(root: &Path, actor: &identity::Actor) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A2")?;
    set_stage(root, "A3", "in_progress", None)?;
    let classified = read_jsonl(&ev(root).join("02-CLASSIFICATION.jsonl"))?;
    // ARCHIVE_POLICY.unused_code_action of the kernel being adopted decides how dead code is treated
    let unused_action = {
        let p0 = Project::open(root);
        if p0.is_installed() {
            p0.policies().get_str(
                "ARCHIVE_POLICY",
                "unused_code_action",
                "remove_from_active_tree",
            )
        } else {
            crate::kernel::resolve_kernel_source(None)
                .ok()
                .and_then(|k| read_yaml(&k.join("policies").join("ARCHIVE_POLICY.yaml")).ok())
                .and_then(|v| v["unused_code_action"].as_str().map(|s| s.to_string()))
                .unwrap_or("remove_from_active_tree".into())
        }
    };
    let mut catalogue = planner::plan(
        root,
        &classified,
        native_test_dir(root).as_deref(),
        &unused_action,
    );
    // Dependency proof for every retirement, from a fresh scan of the tree as it is now (BC-P2-33).
    let index = references::build_fresh(root);
    let os = ownership::OsState::load(root);
    planner::apply_dependency_proofs(&mut catalogue, &index, root, &os, ARCHIVE_ROOT);
    // Stable identity, versions, producer and lineage (BC-P2-21).
    let previous =
        read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl"))).unwrap_or_default();
    let prev_meta = read_json(&catalogue_meta_path(root)).unwrap_or(Value::Null);
    let prev_version = prev_meta["version"].as_u64().unwrap_or(0);
    let ledger = read_jsonl(&ev(root).join("migration-ledger.jsonl")).unwrap_or_default();
    let producer = identity::producer("A3", "gov adopt map", actor);
    let adoption = json!({"adoption_id": b["adoption_id"], "started_at": b["started_at"]});
    planner::finalise_identity(
        &mut catalogue,
        &previous,
        prev_version,
        &ledger,
        &producer,
        prev_version + 1,
        prev_meta["adoption"] == adoption,
    );
    let mut hashes: Vec<(String, String)> = catalogue
        .iter()
        .map(|e| {
            (
                e["artifact_id"].as_str().unwrap_or("").to_string(),
                e["entry_hash"].as_str().unwrap_or("").to_string(),
            )
        })
        .collect();
    hashes.sort();
    let content_hash = identity::content_hash(&json!(hashes));
    let unchanged = prev_meta["content_hash"].as_str() == Some(content_hash.as_str());
    let version = if unchanged {
        prev_version
    } else {
        prev_version + 1
    };
    for e in catalogue.iter_mut() {
        e["catalogue_version"] = json!(version);
    }
    let schemas = Project::open(root).schemas().schema_dir.clone();
    let reg = crate::schemas::SchemaRegistry::new(&schemas);
    let mut problems = vec![];
    for e in &catalogue {
        if reg.has("migration-catalogue-entry") {
            if let Ok(errs) = reg.errors("migration-catalogue-entry", e) {
                for x in errs {
                    problems.push(format!("{}: {x}", e["artifact_id"]));
                }
            }
        }
    }
    write_catalogue(root, &catalogue)?;
    let meta = if unchanged {
        let mut m = prev_meta.clone();
        m["last_regenerated_at"] = json!(now_iso());
        m["adoption"] = adoption.clone();
        m
    } else {
        let history = identity::version_file(&ev(root), CATALOGUE_STEM, version, "jsonl");
        if let Some(d) = history.parent() {
            std::fs::create_dir_all(d)?;
        }
        std::fs::copy(ev(root).join(format!("{CATALOGUE_STEM}.jsonl")), &history)?;
        json!({"id": CATALOGUE_ID, "type": "migration-catalogue", "title": "Adoption target path map (migration catalogue)", "version": version, "content_hash": content_hash,
            "entries": catalogue.len(), "producer": producer, "adoption": adoption,
            "supersedes": if prev_version > 0 { json!([{"version": prev_version, "content_hash": prev_meta["content_hash"], "snapshot": format!("{EVIDENCE}/{CATALOGUE_STEM}.versions/v{prev_version:04}.jsonl")}]) } else { json!([]) },
            "history": format!("{EVIDENCE}/{CATALOGUE_STEM}.versions/"), "created_at": now_iso()})
    };
    write_json(&catalogue_meta_path(root), &meta)?;
    let actions: std::collections::BTreeMap<String, usize> =
        catalogue
            .iter()
            .fold(std::collections::BTreeMap::new(), |mut m, e| {
                *m.entry(e["action"].as_str().unwrap_or("").into())
                    .or_insert(0) += 1;
                m
            });
    let unknown = catalogue
        .iter()
        .filter(|e| e["finding_state"] == "UNKNOWN")
        .count();
    let gated_retirements: Vec<Value> = catalogue
        .iter()
        .filter(|e| {
            e["dependency_proof"]["result"] == "ACTIVE_REFERENCES"
        })
        .map(|e| json!({"artifact_id": e["artifact_id"], "path": e["current_path"], "action": e["action"], "active_references": e["dependency_proof"]["active_references"]}))
        .collect();
    let citations: usize = catalogue
        .iter()
        .map(|e| e["citations"].as_array().map(|a| a.len()).unwrap_or(0))
        .sum();
    set_stage(
        root,
        "A3",
        "done",
        Some((
            "path_map_summary",
            json!({"actions": actions, "unknown": unknown, "catalogue_version": version, "gated_retirements": gated_retirements.len()}),
        )),
    )?;
    Ok(
        json!({"stage": "A3", "entries": catalogue.len(), "actions": actions, "unknown_blocking_destructive": unknown, "schema_problems": problems, "catalogue": {"id": CATALOGUE_ID, "version": version, "content_hash": content_hash, "regenerated_unchanged": unchanged},
            "citations_represented": citations, "retirements_with_active_references": gated_retirements, "evidence": format!("{EVIDENCE}/{CATALOGUE_STEM}.jsonl")}),
    )
}

/// Destructive catalogue entries (RETIRE / DELETE_FROM_ACTIVE_TREE / gated moves) get a Human Decision Gate record
/// each; the executor accepts only ANSWERED (option A), presented gates — never a CLI flag (INV-008, verifier H6).
pub fn ensure_destructive_gates(root: &Path, catalogue: &mut [Value]) -> Result<Vec<String>> {
    let p = Project::open(root);
    if !p.is_installed() {
        return Ok(vec![]);
    }
    let mut created = vec![];
    for e in catalogue.iter_mut() {
        if !e["requires_human_gate"].as_bool().unwrap_or(false) {
            continue;
        }
        if e.get("human_gate")
            .and_then(|v| v.as_str())
            .map(|g| !g.is_empty())
            .unwrap_or(false)
        {
            continue;
        }
        let aid = e["artifact_id"].as_str().unwrap_or("").to_string();
        let action = e["action"].as_str().unwrap_or("").to_string();
        let path = e["current_path"].as_str().unwrap_or("").to_string();
        let reasons: Vec<String> = e["gate_reasons"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default();
        let dependants: Vec<String> = e["dependency_proof"]["active_references"]
            .as_array()
            .map(|a| {
                a.iter()
                    .map(|r| {
                        format!(
                            "{}:{} ({} {})",
                            r["from"].as_str().unwrap_or(""),
                            r["line"],
                            r["role"].as_str().unwrap_or(""),
                            r["kind"].as_str().unwrap_or("")
                        )
                    })
                    .collect()
            })
            .unwrap_or_default();
        let refs_gate = reasons.iter().any(|r| r == "active_references");
        let question = if refs_gate {
            format!("Adoption migration: {action} {path} ({aid}) although active files still refer to it: {}? {}", dependants.join(", "), e["reason"].as_str().unwrap_or(""))
        } else {
            format!(
                "Adoption migration: {action} {path} ({aid})? {}",
                e["reason"].as_str().unwrap_or("")
            )
        };
        let option_a = if refs_gate {
            format!("approve {action} anyway: the references listed are left exactly as they are (never re-pointed at the archived copy) and reported as dangling until fixed")
        } else {
            format!("approve {action}")
        };
        let option_b = if refs_gate {
            "keep in place: registered LEGACY; remove the references through governed work, then re-run gov adopt map/plan".to_string()
        } else {
            "keep in place (skip this entry)".to_string()
        };
        let g = crate::orchestration::gates::create_system(
            &p,
            json!({"question": question, "why_now": format!("migration action needing a human decision ({})", if reasons.is_empty() { "destructive or structural".to_string() } else { reasons.join(", ") }), "current_state": format!("present at {path}"),
                "options": [{"id": "A", "description": option_a}, {"id": "B", "description": option_b}], "impact": format!("target: {}; dependency proof: {} (dependants digest {})", e["target_path"].as_str().unwrap_or("removed from active tree"), e["dependency_proof"]["result"].as_str().unwrap_or("n/a"), e["dependency_proof"]["dependants_digest"].as_str().unwrap_or("-")),
                "reversibility": "batch snapshot + git history", "recommendation": if refs_gate { "B until the references are removed" } else { "A if no reference or unique data exists" }, "confidence": e["confidence"].as_f64().unwrap_or(0.5), "trigger": "destructive_migration", "impact_radius": "R2", "artifact_id": aid}),
        )?;
        let gid = g["id"].as_str().unwrap_or("").to_string();
        e["human_gate"] = json!(gid);
        created.push(gid);
    }
    if !created.is_empty() {
        write_catalogue(root, catalogue)?;
    }
    Ok(created)
}

/// Artefact ids whose destructive gate has been presented and answered with option A.
pub fn answered_destructive(root: &Path, catalogue: &[Value]) -> Vec<String> {
    let p = Project::open(root);
    if !p.is_installed() {
        return vec![];
    }
    catalogue
        .iter()
        .filter(|e| e["requires_human_gate"].as_bool().unwrap_or(false))
        .filter(|e| {
            e.get("human_gate")
                .and_then(|g| g.as_str())
                .map(|g| crate::orchestration::gates::is_answered_yes(&p, g))
                .unwrap_or(false)
        })
        .filter_map(|e| e["artifact_id"].as_str().map(|s| s.to_string()))
        .collect()
}

// ---------------------------------------------------------------- A4
pub fn a4_plan(root: &Path) -> Result<Value> {
    let b = load_baseline(root)?;
    a4_plan_by(root, &identity::Actor::from_env_or_baseline(&b))
}

/// The downstream consumers the migration plan declares (W1 "expected consumers", Contract v3:1076-1078). They are
/// stage artefacts (a stage, the role acting in it and the evidence file it reads the plan into), not governed records,
/// so the plan declares them under `expected_consumers`: `consumers` is the record relation field whose every entry is
/// the id of a record that consumes this one (`<id> CONSUMES <plan>`, `record.schema.json`; BC-P2-21 edge semantics).
fn plan_consumers() -> Value {
    json!([
        {"stage": "A5", "role": "independent migration reviewer / test author", "artefact": format!("{EVIDENCE}/06-migration-tests.yaml")},
        {"stage": "A6", "role": "migration executor", "artefact": format!("{EVIDENCE}/07-MIGRATION-EXECUTION-REPORT.md")},
        {"stage": "A6", "role": "migration executor", "artefact": format!("{EVIDENCE}/migration-ledger.jsonl")},
        {"stage": "A7", "role": "independent migration verifier", "artefact": format!("{EVIDENCE}/08-INDEPENDENT-MIGRATION-VERIFICATION.md")}
    ])
}

/// A4 with W1 identity: the plan is one artefact (`MPLAN-GOVERNANCE-ADOPTION`) with a type, status, content hash,
/// version, producer, declared consumers and supersession lineage; every version is kept in `05-plan.versions/`, so
/// re-planning never overwrites the plan a reviewer approved (BC-P2-21; Contract v3:1069-1080).
pub fn a4_plan_by(root: &Path, actor: &identity::Actor) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A3")?;
    set_stage(root, "A4", "in_progress", None)?;
    let mut catalogue = read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl")))?;
    let gates_created = ensure_destructive_gates(root, &mut catalogue)?;
    let batches = planner::batches(&catalogue);
    let unknown = catalogue
        .iter()
        .filter(|e| e["finding_state"] == "UNKNOWN")
        .count();
    let cat_meta = read_json(&catalogue_meta_path(root)).unwrap_or(Value::Null);
    let gated: Vec<Value> = catalogue
        .iter()
        .filter(|e| e["requires_human_gate"].as_bool().unwrap_or(false))
        .map(|e| json!({"artifact_id": e["artifact_id"], "path": e["current_path"], "action": e["action"], "gate_reasons": e["gate_reasons"], "dependants_digest": e["dependency_proof"]["dependants_digest"]}))
        .collect();
    let catalogue_ref = json!({"id": CATALOGUE_ID, "version": cat_meta["version"], "content_hash": cat_meta["content_hash"], "path": format!("{EVIDENCE}/{CATALOGUE_STEM}.jsonl")});
    let content = json!({"batches": batches, "unknown_blocking": unknown, "catalogue": catalogue_ref, "gated_entries": gated});
    let content_hash = identity::content_hash(&content);
    let plan_path = ev(root).join(format!("{PLAN_STEM}.yaml"));
    let prev = read_yaml(&plan_path).ok().filter(|v| v["id"] == PLAN_ID);
    let prev_version = prev
        .as_ref()
        .and_then(|p| p["version"].as_u64())
        .unwrap_or(0);
    let unchanged = prev
        .as_ref()
        .map(|p| p["content_hash"].as_str() == Some(content_hash.as_str()))
        .unwrap_or(false);
    let plan = if unchanged {
        let mut p = prev.clone().unwrap();
        p["last_regenerated_at"] = json!(now_iso());
        p["last_regenerated_by"] = identity::producer("A4", "gov adopt plan", actor);
        p
    } else {
        let version = prev_version + 1;
        // the previous version stays retrievable, marked superseded by this one
        if prev_version > 0 {
            let snap = identity::version_file(&ev(root), PLAN_STEM, prev_version, "json");
            let mut old = read_json(&snap).unwrap_or_else(|_| prev.clone().unwrap_or(Value::Null));
            old["status"] = json!("SUPERSEDED");
            old["superseded_by"] = json!(format!("{PLAN_ID}@v{version}"));
            old["superseded_by_detail"] = json!({"version": version, "content_hash": content_hash});
            write_json(&snap, &old)?;
        }
        let mut p = json!({"id": PLAN_ID, "type": "migration-plan", "title": "Adoption/migration plan", "status": "ACTIVE", "state_class": "DERIVED",
            "version": version, "content_hash": content_hash, "producer": identity::producer("A4", "gov adopt plan", actor), "expected_consumers": plan_consumers(),
            "supersedes": if prev_version > 0 { json!([format!("{PLAN_ID}@v{prev_version}")]) } else { json!([]) },
            "supersedes_detail": if prev_version > 0 { json!([{"version": prev_version, "content_hash": prev.as_ref().map(|p| p["content_hash"].clone()).unwrap_or(Value::Null), "snapshot": format!("{EVIDENCE}/{PLAN_STEM}.versions/v{prev_version:04}.json")}]) } else { json!([]) },
            "history": format!("{EVIDENCE}/{PLAN_STEM}.versions/"), "created_at": now_iso()});
        for (k, v) in content.as_object().unwrap() {
            p[k] = v.clone();
        }
        p
    };
    let version = plan["version"].as_u64().unwrap_or(1);
    let snap = identity::version_file(&ev(root), PLAN_STEM, version, "json");
    if let Some(d) = snap.parent() {
        std::fs::create_dir_all(d)?;
    }
    if !unchanged || !snap.exists() {
        write_json(&snap, &plan)?;
    }
    write_yaml(&plan_path, &plan)?;
    write_md(
        root,
        "05-ADOPTION-MIGRATION-PLAN.md",
        &format!(
            "{}\n## Identity\n\n- id: `{PLAN_ID}` (type migration-plan), version {version}, content hash `{}`\n- catalogue: `{CATALOGUE_ID}` version {}\n- history: `{EVIDENCE}/{PLAN_STEM}.versions/`\n",
            planner::plan_markdown(&catalogue, &batches, unknown),
            &content_hash[..16],
            cat_meta["version"]
        ),
    )?;
    set_stage(root, "A4", "done", None)?;
    Ok(
        json!({"stage": "A4", "plan": {"id": PLAN_ID, "version": version, "content_hash": content_hash, "regenerated_unchanged": unchanged}, "batches": batches.iter().map(|b| json!({"batch": b["batch"], "entries": b["entries"], "human_gate": b["requires_human_gate"]})).collect::<Vec<_>>(), "human_gates_created": gates_created, "evidence": [format!("{EVIDENCE}/05-ADOPTION-MIGRATION-PLAN.md"), format!("{EVIDENCE}/{PLAN_STEM}.yaml")]}),
    )
}

// ---------------------------------------------------------------- A5
pub fn a5_test_design(root: &Path) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A4")?;
    let catalogue = read_jsonl(&ev(root).join("04-TARGET-PATH-MAP.jsonl"))?;
    let legacy: Vec<String> = classify::legacy_mechanisms(root)
        .into_iter()
        .map(|l| l.path)
        .collect();
    let cmd = b["baseline_tests"]["command"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect::<Vec<_>>()
        })
        .filter(|c| !c.is_empty() && b["baseline_tests"]["status"] == "passed");
    let tests = verify::scaffold_tests(&catalogue, &legacy, cmd);
    let path = ev(root).join("06-migration-tests.yaml");
    if !path.exists() {
        write_yaml(&path, &tests)?;
    }
    // the plan and the independent tests must agree on every artefact's disposition (Contract v3:928-929)
    let current = read_yaml(&path).unwrap_or(tests.clone());
    let conflicts = verify::plan_test_agreement(&catalogue, &current);
    let md = format!("# 06 — Independent migration test design\n\nAuthored by a fresh independent session (Role B). Scaffold generated by the planner; the reviewer must review classification, target map, destructive moves, unknown items, references/imports, authority changes, archive/delete decisions and old memory stores, then extend `06-migration-tests.yaml` and record a verdict with `gov adopt review`.\n\nTest families: path integrity · code integrity · governance integrity · behaviour preservation · rollback/recovery.\n\nScaffolded tests: {}\n\n## Verdicts\n\n", tests["tests"].as_array().map(|a| a.len()).unwrap_or(0));
    let p = ev(root).join("06-INDEPENDENT-MIGRATION-TEST-DESIGN.md");
    if !p.exists() {
        write_text(&p, &md)?;
    }
    Ok(
        json!({"stage": "A5", "tests_file": format!("{EVIDENCE}/06-migration-tests.yaml"), "scaffolded_tests": tests["tests"].as_array().map(|a| a.len()).unwrap_or(0), "plan_test_disagreements": conflicts, "next": "independent reviewer extends tests and runs `gov adopt review --verdict MIGRATION_PLAN_APPROVED --session <fresh-session>`"}),
    )
}

pub fn a5_review(
    root: &Path,
    verdict: &str,
    reviewer_session: &str,
    reviewer_role: &str,
    notes: Option<&str>,
) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A4")?;
    if ![
        "MIGRATION_PLAN_APPROVED",
        "MIGRATION_PLAN_APPROVED_WITH_AMENDMENTS",
        "MIGRATION_PLAN_REJECTED",
    ]
    .contains(&verdict)
    {
        return Err(GovError::new("USAGE", "verdict must be MIGRATION_PLAN_APPROVED | MIGRATION_PLAN_APPROVED_WITH_AMENDMENTS | MIGRATION_PLAN_REJECTED"));
    }
    if b["planner_session"].as_str() == Some(reviewer_session) {
        return Err(GovError::new("INDEPENDENCE", "reviewer session must differ from the planner session (fresh independent context, protocol Role B)"));
    }
    if !ev(root).join("06-migration-tests.yaml").exists() {
        return Err(GovError::new("VERDICT_REQUIRED", "independent tests file 06-migration-tests.yaml missing; run `gov adopt test-design` and author tests before a verdict"));
    }
    let tests = read_yaml(&ev(root).join("06-migration-tests.yaml"))?;
    let n = tests["tests"].as_array().map(|a| a.len()).unwrap_or(0);
    if verdict.starts_with("MIGRATION_PLAN_APPROVED") {
        let catalogue = read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl")))?;
        let conflicts = verify::plan_test_agreement(&catalogue, &tests);
        if !conflicts.is_empty() {
            return Err(GovError::new(
                "PLAN_TEST_DISAGREEMENT",
                format!("{} independent test(s) contradict the plan's disposition of an artefact; a plan cannot be approved against tests that contradict it — amend the plan (gov adopt map/plan) or the tests, or record MIGRATION_PLAN_REJECTED", conflicts.len()),
            )
            .with_details(json!({"conflicts": conflicts})));
        }
    }
    let entry = json!({"verdict": verdict, "session": reviewer_session, "role": reviewer_role, "at": now_iso(), "tests": n, "notes": notes});
    let mut md =
        read_text(&ev(root).join("06-INDEPENDENT-MIGRATION-TEST-DESIGN.md")).unwrap_or_default();
    md.push_str(&format!("- {} — **{verdict}** by {reviewer_role} (session {reviewer_session}), {n} held-out tests. {}\n", now_iso(), notes.unwrap_or("")));
    write_text(
        &ev(root).join("06-INDEPENDENT-MIGRATION-TEST-DESIGN.md"),
        &md,
    )?;
    let mut b2 = b.clone();
    b2["verdicts"]["A5"] = entry.clone();
    b2["stage_status"]["A5"] = json!(if verdict == "MIGRATION_PLAN_REJECTED" {
        "rejected"
    } else {
        "done"
    });
    b2["stage_times"]["A5"] = json!(now_iso());
    save_baseline(root, &b2)?;
    Ok(json!({"stage": "A5", "verdict": entry}))
}

// ---------------------------------------------------------------- A6
fn brownfield_contract(
    root: &Path,
    kernel_dir: &Path,
    classified: &[Value],
    catalogue: &[Value],
) -> Result<Value> {
    let mut c = read_yaml(
        &kernel_dir
            .join("overlay-templates")
            .join("REPOSITORY_CONTRACT.yaml"),
    )?;
    let mut extra = vec![];
    let mut src_dirs: std::collections::BTreeSet<String> = std::collections::BTreeSet::new();
    let mut test_dirs: std::collections::BTreeSet<String> = std::collections::BTreeSet::new();
    let mut secret_paths: Vec<String> = vec![];
    for e in classified {
        let path = e["path"].as_str().unwrap_or("");
        let top = path.split('/').next().unwrap_or("").to_string();
        if top.is_empty() || !path.contains('/') {
            continue;
        }
        match e["class"].as_str().unwrap_or("") {
            "PRODUCT_SOURCE" | "DEAD_OR_UNUSED" => {
                if !["spec", "governance", "archive", "product", "docs"].contains(&top.as_str()) {
                    src_dirs.insert(top);
                }
            }
            "PRODUCT_TEST" => {
                if !["spec", "governance", "archive", "product", "docs"].contains(&top.as_str()) {
                    test_dirs.insert(top);
                }
            }
            _ => {}
        }
    }
    // Everything carrying secret material is classified secret wherever it is now and wherever the plan retires it
    // to (a secret-bearing legacy store keeps its protection in the archive).
    for e in classified {
        let path = e["path"].as_str().unwrap_or("");
        if !path.is_empty()
            && (e["class"] == "SECRET" || e["sensitivity"] == "secret")
            && !secret_paths.contains(&path.to_string())
        {
            secret_paths.push(path.to_string());
        }
    }
    for e in catalogue.iter().filter(|e| e["sensitivity"] == "secret") {
        for k in ["current_path", "target_path"] {
            if let Some(t) = e[k].as_str().filter(|t| !t.is_empty() && !t.ends_with('/')) {
                if !secret_paths.contains(&t.to_string()) {
                    secret_paths.push(t.to_string());
                }
            }
        }
    }
    for d in &test_dirs {
        extra.push(json!({"pattern": format!("{d}/**"), "class": "test", "owner_role": "independent-test-designer", "semantic_index": true, "lexical_index": true, "graph_index": true, "code_index": true, "namespace": "product"}));
    }
    for d in &src_dirs {
        if test_dirs.contains(d) {
            continue;
        }
        extra.push(json!({"pattern": format!("{d}/**"), "class": "source", "owner_role": "backend-engineer", "semantic_index": true, "lexical_index": true, "graph_index": true, "code_index": true, "namespace": "product"}));
    }
    for s in &secret_paths {
        extra.push(json!({"pattern": s, "class": "secret", "semantic_index": false, "lexical_index": false, "graph_index": false, "code_index": false, "agent_read": "prohibited", "export": "denied", "namespace": "secret"}));
    }
    if let Some(arr) = c["paths"].as_array_mut() {
        let secrets_at_end: Vec<Value> = extra
            .iter()
            .filter(|r| r["class"] == "secret")
            .cloned()
            .collect();
        let others: Vec<Value> = extra
            .iter()
            .filter(|r| r["class"] != "secret")
            .cloned()
            .collect();
        let mut merged = others;
        merged.extend(arr.clone());
        merged.extend(secrets_at_end);
        *arr = merged;
    }
    c["capability_roots"] = json!({"native_source": src_dirs, "native_tests": test_dirs});
    let _ = root;
    Ok(c)
}

pub fn a6_migrate(
    root: &Path,
    batch: Option<i64>,
    source: Option<&str>,
    gate_answers: &[String],
    project_name: &str,
    alias: &str,
    session: &str,
) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A4")?;
    require_verdict(
        &b,
        "A5",
        &[
            "MIGRATION_PLAN_APPROVED",
            "MIGRATION_PLAN_APPROVED_WITH_AMENDMENTS",
        ],
    )?;
    {
        let p0 = Project::open(root);
        if p0.is_installed() {
            crate::orchestration::control::guard_write(&p0, "adopt migrate")?;
            crate::authority::require(&p0, "migrate_execute")?;
        }
    }
    // the approved plan and its independent tests must agree before anything executes (Contract v3:928-929)
    if let Ok(t) = read_yaml(&ev(root).join("06-migration-tests.yaml")) {
        let cat0 = read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl")))?;
        let conflicts = verify::plan_test_agreement(&cat0, &t);
        if !conflicts.is_empty() {
            return Err(GovError::new(
                "PLAN_TEST_DISAGREEMENT",
                format!("{} independent test(s) contradict the plan; nothing executed (a batch run against contradicting tests can only fail and roll back) — amend and re-review", conflicts.len()),
            )
            .with_details(json!({"conflicts": conflicts})));
        }
    }
    let deprecated_flag_note = if gate_answers.is_empty() {
        Value::Null
    } else {
        json!(format!("--gate-answer {:?} ignored: a destructive entry executes only when its Human Decision Gate record is presented and answered (gov gate present / gov decide)", gate_answers))
    };
    let mut catalogue = read_jsonl(&ev(root).join("04-TARGET-PATH-MAP.jsonl"))?;
    let classified = read_jsonl(&ev(root).join("02-CLASSIFICATION.jsonl"))?;
    let plan = read_yaml(&ev(root).join("05-plan.yaml"))?;
    let batches: Vec<i64> = match batch {
        Some(n) => vec![n],
        None => plan["batches"]
            .as_array()
            .map(|a| a.iter().filter_map(|x| x["batch"].as_i64()).collect())
            .unwrap_or_default(),
    };
    let ledger = ev(root).join("migration-ledger.jsonl");
    let tests_file = ev(root).join("06-migration-tests.yaml");
    let mut report = read_text(&ev(root).join("07-MIGRATION-EXECUTION-REPORT.md")).unwrap_or_else(|_| "# 07 — Migration execution report\n\nExecutor: Role C. Each batch: checkpoint → execute → update references → independent-authored tests + affected product tests → evidence → ledger.\n\n".into());
    let mut results = vec![];
    let mut b2 = b.clone();
    b2["executor_session"] = json!(session);
    b2["stage_status"]["A6"] = json!("in_progress");
    save_baseline(root, &b2)?;
    let unknown = catalogue
        .iter()
        .filter(|e| e["finding_state"] == "UNKNOWN")
        .count();
    for n in batches {
        let mut entry = json!({"batch": n, "at": now_iso()});
        if n == 0 {
            let src = resolve_kernel_source(source.map(Path::new))?;
            let gov = root.join("governance");
            std::fs::create_dir_all(&gov)?;
            // Privileged lifecycle ingress `adopt`: the one verification policy. Brownfield adoption installs a
            // kernel exactly like `init` does, so it is admitted through the same verifier and bound by the same
            // floors (ARCH-0003 §3.6; OWNER-DECISION-0006 §9).
            let mut adopt_auth: Option<crate::srr::AuthenticatedRelease> = None;
            let manifest = if root.join("governance/framework.lock").exists() {
                crate::kernel::read_manifest(&gov.join("kernel"))?
            } else {
                let a = crate::srr::admit(
                    crate::srr::AdmissionRequest::new(crate::srr::Ingress::Adopt, &src)
                        .with_reason(Some("gov adopt migrate (batch 0)".into())),
                )?;
                let m = install_kernel(&a, &gov)?;
                adopt_auth = Some(a);
                m
            };
            if !root.join("governance/framework.lock").exists() {
                let consumer_commit = Project::open(root).git_commit();
                let release_commit = crate::kernel::release_commit_for_source(&src);
                write_lock(
                    &gov.join("framework.lock"),
                    &manifest,
                    &crate::kernel::source_label(&src),
                    Some(&release_commit),
                    Some(&consumer_commit),
                )?;
            }
            let contract = brownfield_contract(root, &gov.join("kernel"), &classified, &catalogue)?;
            let opts = crate::init::InitOptions {
                source: None,
                project_name: project_name.into(),
                alias: alias.into(),
                mode: "adopt".into(),
                force: false,
                intent: None,
                skip_index: true,
                channel: None,
                break_glass: false,
            };
            let written =
                crate::init::write_overlay(root, &gov.join("kernel"), &opts, Some(contract))?;
            crate::init::ensure_roots(root)?;
            let mut p = Project::open(root);
            p.invalidate();
            crate::tools::generate_registry(&p)?;
            crate::adapters::generate(&p)?;
            let gates_created = ensure_destructive_gates(root, &mut catalogue)?;
            // Transaction step (9): floors advance only after the install is committed and verified (SRR-R0-L5).
            let protected = match adopt_auth.as_ref() {
                Some(a) => crate::srr::record_installed(a)?,
                None => Value::Null,
            };
            entry["installed"] = json!({"version": manifest["version"], "overlay_written": written, "destructive_gates_created": gates_created, "release_authenticity": adopt_auth.as_ref().map(|a| a.to_value()), "protected_state": protected});
        } else {
            if n >= 6 && unknown > 0 {
                return Err(GovError::new(
                    "UNKNOWN_BLOCKS_DESTRUCTIVE",
                    format!(
                        "{unknown} UNKNOWN artefact(s) block destructive batch {n} (protocol §8)"
                    ),
                ));
            }
            let p = Project::open(root);
            if p.is_installed() {
                crate::orchestration::control::guard_write(&p, "adopt migrate")?;
                let db = RuntimeDb::open(&p.db_path())?;
                db.init_schema()?;
                let _ = crate::checkpoints::create(
                    &p,
                    &db,
                    json!({"trigger": "significant_mutation", "next_action": format!("execute migration batch {n}"), "last_completed_step": format!("pre-batch {n} checkpoint")}),
                );
            }
            let _ = ensure_destructive_gates(root, &mut catalogue)?;
            let answered = answered_destructive(root, &catalogue);
            let ctx = executor::BatchContext {
                archive_root: ARCHIVE_ROOT.into(),
                catalogue_version: read_json(&catalogue_meta_path(root))
                    .map(|m| m["version"].clone())
                    .unwrap_or(Value::Null),
                plan_version: plan["version"].clone(),
                scanner: scanner_for(root),
            };
            let mut r = executor::apply_batch(root, &catalogue, n, &answered, &ledger, &ctx)?;
            {
                let pj = Project::open(root);
                for sk in r.skipped.iter_mut() {
                    let aid = sk["artifact_id"].as_str().unwrap_or("").to_string();
                    if let Some(e) = catalogue
                        .iter()
                        .find(|e| e["artifact_id"].as_str() == Some(&aid))
                    {
                        if let Some(g) = e["human_gate"].as_str() {
                            match crate::orchestration::gates::answered_option(&pj, g).as_deref() {
                                Some("A") => {}
                                Some(o) => {
                                    sk["reason"] = json!(format!(
                                        "human gate {g} answered {o}: kept in place by decision"
                                    ));
                                    sk["gate"] = json!(g);
                                }
                                None => {
                                    sk["reason"] = json!(format!("human gate {g} pending (present it in chat and decide; a CLI flag is not an answer)"));
                                    sk["gate"] = json!(g);
                                }
                            }
                        }
                    }
                }
            }
            entry["applied"] = json!(r.applied.len());
            entry["moves"] = json!(r.moves);
            entry["created"] = json!(r.created);
            entry["references_updated"] = json!(r.references_updated);
            entry["skipped"] = json!(r.skipped);
            entry["blocked"] = json!(r.blocked);
            entry["retired_with_active_references"] = json!(r.retired_with_active_references);
        }
        // post-batch tests
        let mut tests = json!({"ran": false});
        if tests_file.exists() {
            let t = verify::run_tests_file_upto(root, &tests_file, Some(n))?;
            tests = t.clone();
            if !t["ok"].as_bool().unwrap_or(false) && n > 0 {
                let rb = executor::rollback_batch(root, n)?;
                entry["rolled_back"] = json!(rb);
                b2["stage_status"]["A6"] = json!("failed");
                save_baseline(root, &b2)?;
                report.push_str(&format!(
                    "## Batch {n} — FAILED tests, rolled back\n\n```json\n{}\n```\n\n",
                    serde_json::to_string_pretty(&t)?
                ));
                write_text(&ev(root).join("07-MIGRATION-EXECUTION-REPORT.md"), &report)?;
                return Err(GovError::new("MIGRATION_BATCH_FAILED", format!("batch {n}: {} independent test(s) failed; batch rolled back; downstream batches not executed", t["fail"])).with_details(t));
            }
        }
        entry["tests"] = tests;
        report.push_str(&format!(
            "## Batch {n}\n\n```json\n{}\n```\n\n",
            serde_json::to_string_pretty(&entry)?
        ));
        results.push(entry);
    }
    write_text(&ev(root).join("07-MIGRATION-EXECUTION-REPORT.md"), &report)?;
    if !deprecated_flag_note.is_null() {
        results.push(json!({"note": deprecated_flag_note}));
    }
    let all_done = batch.is_none()
        || plan["batches"]
            .as_array()
            .map(|a| {
                a.iter().all(|x| {
                    x["batch"].as_i64() == batch
                        || read_text(&ledger)
                            .map(|t| {
                                t.contains(&format!(
                                    "\"batch\":{},\"status\":\"batch_complete\"",
                                    x["batch"]
                                ))
                            })
                            .unwrap_or(false)
                        || x["entries"].as_u64() == Some(0)
                })
            })
            .unwrap_or(true);
    b2["stage_status"]["A6"] = json!(if all_done { "done" } else { "in_progress" });
    b2["stage_times"]["A6"] = json!(now_iso());
    save_baseline(root, &b2)?;
    Ok(
        json!({"stage": "A6", "batches": results, "complete": all_done, "evidence": format!("{EVIDENCE}/07-MIGRATION-EXECUTION-REPORT.md")}),
    )
}

pub fn rollback_batch(root: &Path, batch: i64) -> Result<Value> {
    executor::rollback_batch(root, batch)
}

// ---------------------------------------------------------------- A7
pub fn a7_verify_migration(
    root: &Path,
    verdict: Option<&str>,
    session: &str,
    role: &str,
) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A6")?;
    if b["executor_session"].as_str() == Some(session) {
        return Err(GovError::new(
            "INDEPENDENCE",
            "migration verifier session must differ from the executor session (Role D)",
        ));
    }
    let catalogue = read_jsonl(&ev(root).join("04-TARGET-PATH-MAP.jsonl"))?;
    let vc = verify::verify_catalogue(root, &catalogue);
    let tests_file = ev(root).join("06-migration-tests.yaml");
    let tests = if tests_file.exists() {
        verify::run_tests_file(root, &tests_file)?
    } else {
        json!({"ok": false, "reason": "no independent tests"})
    };
    let p = Project::open(root);
    let secrets_ok = p.is_installed() && {
        let sc = p.secret_scanner();
        let contract = p.contract();
        crate::paths::iter_repo_files(root, false)
            .into_iter()
            .all(|(abs, rel)| {
                contract.decide(&rel).is_secret()
                    || sc.path_is_secret(&rel)
                    || sc.scan_file(&abs, &rel).is_empty()
            })
    };
    let kernel_ok = p.is_installed()
        && crate::kernel::verify_kernel(&p.kernel_dir())
            .map(|v| v.ok)
            .unwrap_or(false);
    let computed = if vc["ok"].as_bool().unwrap_or(false)
        && tests["ok"].as_bool().unwrap_or(false)
        && secrets_ok
        && kernel_ok
    {
        "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD"
    } else {
        "MIGRATION_REJECTED_NEEDS_REPAIR"
    };
    let final_verdict = verdict.unwrap_or(computed);
    if verdict.is_some()
        && verdict != Some(computed)
        && final_verdict == "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD"
    {
        return Err(GovError::new(
            "VERDICT_CONFLICT",
            format!("verifier claims acceptance but evidence computes {computed}; repair first"),
        )
        .with_details(json!({"catalogue": vc, "tests": tests})));
    }
    let n_of = |k: &str| vc[k].as_array().map(|a| a.len()).unwrap_or(0);
    let md = format!("# 08 — Independent migration verification\n\nVerifier: {role} (session {session}) at {}. Executor confidence statements ignored; actual paths inspected; dependency references re-derived from a fresh scan.\n\n- Catalogue vs reality: {} problem(s), {} broken link(s), {} legacy mechanism(s) still active\n- Legacy retirements awaiting a Human Decision Gate: {} · kept by decision: {}\n- Retired with active references accepted at a gate: {} · active citations of archived material: {}\n- Independent tests: {} pass / {} fail\n- Secrets isolated: {secrets_ok}\n- Kernel intact: {kernel_ok}\n\n**Verdict: {final_verdict}**\n\n```json\n{}\n```\n", now_iso(), n_of("problems"), n_of("broken_links"), n_of("legacy_in_active_tree"), n_of("legacy_retirement_pending_gate"), n_of("legacy_kept_by_decision"), n_of("retired_with_accepted_active_references"), n_of("active_citations_of_archived_material"), tests["pass"], tests["fail"], serde_json::to_string_pretty(&json!({"catalogue": vc, "tests": tests}))?);
    write_md(root, "08-INDEPENDENT-MIGRATION-VERIFICATION.md", &md)?;
    let mut b2 = b.clone();
    b2["verdicts"]["A7"] =
        json!({"verdict": final_verdict, "session": session, "role": role, "at": now_iso()});
    b2["stage_status"]["A7"] = json!(if final_verdict.starts_with("MIGRATION_ACCEPTED") {
        "done"
    } else {
        "rejected"
    });
    b2["stage_times"]["A7"] = json!(now_iso());
    save_baseline(root, &b2)?;
    Ok(
        json!({"stage": "A7", "verdict": final_verdict, "catalogue_problems": vc["problems"], "broken_links": vc["broken_links"], "legacy_in_active_tree": vc["legacy_in_active_tree"],
            "legacy_retirement_pending_gate": vc["legacy_retirement_pending_gate"], "legacy_kept_by_decision": vc["legacy_kept_by_decision"], "retired_with_accepted_active_references": vc["retired_with_accepted_active_references"],
            "active_citations_of_archived_material": vc["active_citations_of_archived_material"], "tests": {"pass": tests["pass"], "fail": tests["fail"]}, "secrets_isolated": secrets_ok, "kernel_intact": kernel_ok}),
    )
}

// ---------------------------------------------------------------- A8
/// A8: extract every unit of unique durable knowledge from each legacy store (decisions, lessons, skill candidates,
/// research notes, evidence claims; everything else into a review register), then retire each store only after a
/// fresh dependency proof shows no active code, configuration or document depends on it — or under a Human Decision
/// Gate answered A for exactly the dependants found, leaving them as they are (framework §69-70; BC-P2-33).
pub fn a8_extract_legacy(root: &Path) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A7")?;
    require_verdict(&b, "A7", &["MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD"])?;
    {
        let p0 = Project::open(root);
        crate::orchestration::control::guard_write(&p0, "adopt extract-legacy")?;
        crate::authority::require(&p0, "migrate_execute")?;
    }
    set_stage(root, "A8", "in_progress", None)?;
    let catalogue = read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl")))?;
    let scanner = scanner_for(root);
    let answered = answered_destructive(root, &catalogue);
    let mut stores = vec![];
    let mut created = vec![];
    let mut registers = vec![];
    let mut retired = vec![];
    let mut retained = vec![];
    let mut seen: std::collections::HashSet<String> = std::collections::HashSet::new();
    let mut ledger_rows: Vec<Value> = vec![];
    // stores = legacy memory stores (EXTRACT → memory-stores) + legacy rule/governance files (wherever they are now)
    let mut sources: Vec<(&Value, bool)> = catalogue
        .iter()
        .filter(|e| {
            e["action"] == "EXTRACT"
                && e["target_path"]
                    .as_str()
                    .map(|t| t.contains("memory-stores"))
                    .unwrap_or(false)
        })
        .map(|e| (e, true))
        .collect();
    for e in catalogue
        .iter()
        .filter(|e| e["current_class"] == "GOVERNANCE_LEGACY" && e["action"] == "MOVE")
    {
        sources.push((e, false));
    }
    let needs_proof = sources
        .iter()
        .any(|(e, store)| *store && root.join(e["current_path"].as_str().unwrap_or("")).exists());
    let index = if needs_proof {
        references::build_fresh(root)
    } else {
        references::ReferenceIndex::default()
    };
    let os = ownership::OsState::load(root);
    let active = references::ActiveSet {
        root,
        os: &os,
        archive_root: ARCHIVE_ROOT.into(),
        leaving: planner::non_active_paths(&catalogue, ARCHIVE_ROOT, &answered),
    };
    for (e, is_store) in sources {
        let path = e["current_path"].as_str().unwrap_or("").to_string();
        let target = e["target_path"].as_str().unwrap_or("").to_string();
        let aid = e["artifact_id"].as_str().unwrap_or("").to_string();
        let at_source = root.join(&path).exists();
        let read_from = if at_source {
            path.clone()
        } else if !target.is_empty() && root.join(&target).exists() {
            target.clone()
        } else {
            path.clone()
        };
        let (kind, x) = extraction::extract_store(root, &path, &read_from, &scanner, &mut seen)?;
        created.extend(x.records.clone());
        if let Some(r) = &x.register {
            registers.push(r.clone());
            created.push(r.clone());
        }
        let mut proof = Value::Null;
        let disposition = if kind == "NOT_FOUND" {
            "NOT_FOUND".to_string()
        } else if !at_source {
            retired.push(read_from.clone());
            "RETIRE".to_string()
        } else if !is_store {
            // a legacy rule file its migration batch did not retire (gated or blocked): registered, not moved here
            let why = match e["human_gate"]
                .as_str()
                .and_then(|g| crate::orchestration::gates::answered_option(&Project::open(root), g))
            {
                Some(o) if o != "A" => "KEPT_BY_DECISION",
                _ => "RETIREMENT_PENDING_GATE",
            };
            retained.push(json!({"path": path, "artifact_id": aid, "disposition": why, "gate": e["human_gate"]}));
            why.to_string()
        } else {
            let p = references::dependency_proof(&index, &path, Some(target.as_str()), &active);
            let clean = references::proof_is_clean(&p);
            let gated = e["requires_human_gate"].as_bool().unwrap_or(false);
            let authorised = answered.contains(&aid);
            let gate_for_refs = e["gate_reasons"]
                .as_array()
                .map(|a| a.iter().any(|r| r == "active_references"))
                .unwrap_or(false);
            proof = p.clone();
            let outcome = if !clean
                && !(authorised
                    && gate_for_refs
                    && executor::proof_covered_by(&p, &e["dependency_proof"]))
            {
                "RETIREMENT_BLOCKED_ACTIVE_REFERENCES"
            } else if gated && !authorised {
                match e["human_gate"].as_str().and_then(|g| {
                    crate::orchestration::gates::answered_option(&Project::open(root), g)
                }) {
                    Some(_) => "KEPT_BY_DECISION",
                    None => "RETIREMENT_PENDING_GATE",
                }
            } else {
                "RETIRE"
            };
            if outcome == "RETIRE" {
                if let Some(d) = root.join(&target).parent() {
                    std::fs::create_dir_all(d)?;
                }
                let _ = std::process::Command::new("git")
                    .args(["mv", "-k", &path, &target])
                    .current_dir(root)
                    .output();
                if root.join(&path).exists() {
                    std::fs::rename(root.join(&path), root.join(&target))?;
                }
                retired.push(target.clone());
                // the ledger records store retirements too, so every later pass can re-check what depended on them
                let dangling = if clean {
                    Value::Null
                } else {
                    p["active_references"].clone()
                };
                ledger_rows.push(json!({"at": now_iso(), "stage": "A8", "artifact_id": aid, "action": "EXTRACT", "path": path, "status": "applied", "entry_hash": e["entry_hash"],
                    "result": {"to": target, "retired_with_active_references": dangling, "authorised_by_gate": if clean { Value::Null } else { e["human_gate"].clone() }},
                    "dependency_proof": {"result": p["result"], "dependants_digest": p["dependants_digest"], "active_references": p["active_references"]}}));
            } else {
                retained.push(json!({"path": path, "artifact_id": aid, "disposition": outcome, "gate": e["human_gate"], "dependency_proof": p}));
            }
            outcome.to_string()
        };
        stores.push(json!({"path": path, "artifact_id": aid, "kind": kind, "strings": x.units, "extracted": x.distilled, "registered_for_review": x.registered_for_review,
            "skipped_secret_strings": x.withheld_secret, "duplicates": x.duplicates, "by_kind": x.by_kind, "records": x.records, "register": x.register,
            "disposition": disposition, "archived_to": if disposition == "RETIRE" { json!(if at_source { target.clone() } else { read_from.clone() }) } else { Value::Null },
            "dependency_proof": proof, "retired_with_active_references": if disposition == "RETIRE" && !proof.is_null() && !references::proof_is_clean(&proof) { proof["active_references"].clone() } else { Value::Null }}));
    }
    if !ledger_rows.is_empty() {
        let lp = ev(root).join("migration-ledger.jsonl");
        let mut text = read_text(&lp).unwrap_or_default();
        for r in &ledger_rows {
            text.push_str(&serde_json::to_string(r)?);
            text.push('\n');
        }
        write_text(&lp, &text)?;
    }
    // LEGACY registration record: every legacy mechanism, where it went, and why any is still in the tree. A mechanism
    // still present after migration acceptance is held behind a gate (pending, or kept by the human's decision): it is
    // registered here whatever authority label classification gave it (a superseded decision log included).
    let mut legacy_paths: Vec<String> = catalogue
        .iter()
        .filter(|e| e["authority"] == "LEGACY")
        .map(|e| e["current_path"].as_str().unwrap_or("").to_string())
        .collect();
    for l in classify::legacy_mechanisms(root) {
        if !legacy_paths.contains(&l.path) {
            if !retained.iter().any(|r| r["path"] == l.path.as_str()) {
                let entry = catalogue
                    .iter()
                    .find(|e| e["current_path"].as_str() == Some(l.path.as_str()));
                retained.push(json!({"path": l.path, "artifact_id": entry.map(|e| e["artifact_id"].clone()), "disposition": "RETAINED_UNDER_GATE", "gate": entry.map(|e| e["human_gate"].clone()), "kind": l.kind}));
            }
            legacy_paths.push(l.path);
        }
    }
    let mut rec = new_record(
        "legacy",
        "LEG-0001",
        "Retired legacy governance and memory mechanisms",
        json!({"status": "LEGACY", "state_class": "HISTORICAL", "paths": legacy_paths, "archived": retired, "retained": retained, "body": "Legacy mechanisms inventoried in A2, retired in A6/A8 after a dependency proof. They carry no authority (INV-004). Unique durable knowledge was extracted into PROVISIONAL records with provenance; units not distilled into a typed record are listed in review registers. A mechanism still in the tree is listed under `retained` with its gate or blocking proof.", "extracted_records": created, "review_registers": registers}),
    );
    rec.path = "archive/governance/LEG-0001.yaml".into();
    save_record(root, &rec)?;
    let md = format!("# 09 — Legacy memory extraction\n\n| Store | Kind | Units | Distilled | For review | Secret withheld | Disposition |\n|---|---|---|---|---|---|---|\n{}\n\nCreated {} record(s): {}\n\nReview registers (units not distilled into a typed record — nothing unique is dropped): {}\n\nRetained in the active tree: {}\n\nRaw chat/session content was not imported into active semantic memory (§70, protocol §13). Each retirement was preceded by a fresh dependency proof over code, configuration and docs.\n",
        stores.iter().map(|s| format!("| {} | {} | {} | {} | {} | {} | {} |", s["path"].as_str().unwrap_or(""), s["kind"].as_str().unwrap_or(""), s["strings"], s["extracted"], s["registered_for_review"], s["skipped_secret_strings"], s["disposition"].as_str().unwrap_or(""))).collect::<Vec<_>>().join("\n"),
        created.len(), created.join(", "), if registers.is_empty() { "none".to_string() } else { registers.join(", ") },
        if retained.is_empty() { "none".to_string() } else { retained.iter().map(|r| format!("{} ({})", r["path"].as_str().unwrap_or(""), r["disposition"].as_str().unwrap_or(""))).collect::<Vec<_>>().join(", ") });
    write_md(root, "09-LEGACY-MEMORY-EXTRACTION.md", &md)?;
    set_stage(root, "A8", "done", None)?;
    Ok(
        json!({"stage": "A8", "stores": stores, "created_records": created, "review_registers": registers, "retired": retired, "retained": retained, "legacy_record": "archive/governance/LEG-0001.yaml"}),
    )
}

// ---------------------------------------------------------------- A9
pub fn a9_build_memory(root: &Path, session: &str) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A8")?;
    require_verdict(&b, "A7", &["MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD"])?;
    {
        let p0 = Project::open(root);
        crate::orchestration::control::guard_write(&p0, "adopt build-memory")?;
        crate::authority::require(&p0, "build_memory")?;
    }
    let mut b2 = b.clone();
    b2["memory_builder_session"] = json!(session);
    b2["stage_status"]["A9"] = json!("in_progress");
    save_baseline(root, &b2)?;
    let mut p = Project::open(root);
    p.invalidate();
    p.require_installed()?;
    let r = crate::memory::indexer::rebuild(
        &p,
        crate::memory::indexer::IndexOptions {
            incremental: false,
            ..Default::default()
        },
    )?;
    // held-out template from governed records (only when none exist yet)
    let held_path = root.join(p.policies().get_str(
        "MEMORY_POLICY",
        "regression.heldout_file",
        "governance/tests/memory/heldout.yaml",
    ));
    let existing = read_yaml(&held_path)
        .ok()
        .and_then(|h| h["queries"].as_array().map(|a| a.len()))
        .unwrap_or(0);
    let mut generated = 0;
    if existing == 0 {
        let db = RuntimeDb::open(&p.db_path())?;
        let set = crate::memory::heldout::generate_starter(&p, &db, "gov adopt build-memory")?;
        generated = set["queries"].as_array().map(|a| a.len()).unwrap_or(0);
        drop(db);
        write_yaml(&held_path, &set)?;
        let _ = crate::memory::indexer::rebuild(
            &p,
            crate::memory::indexer::IndexOptions {
                incremental: true,
                ..Default::default()
            },
        );
    }
    let md = format!("# 10 — Memory implementation report\n\nBuilt after path stabilisation (A7 accepted) on canonical paths.\n\n- artefacts: {} · chunks: {} · vectors: {} · edges: {} · symbols: {}\n- excluded (secret/binary/large): {}\n- secret-content blocked: {}\n- embedder: {}\n- manifest hash: {}\n- degradations: {:?}\n- held-out queries generated: {generated}\n", r.counts["artifacts"], r.counts["chunks"], r.counts["vectors"], r.counts["edges"], r.counts["symbols"], r.excluded.len(), r.secret_blocked.len(), r.embedder, r.manifest_hash, r.degradations);
    write_md(root, "10-MEMORY-IMPLEMENTATION-REPORT.md", &md)?;
    set_stage(root, "A9", "done", None)?;
    Ok(
        json!({"stage": "A9", "counts": r.counts, "manifest_hash": r.manifest_hash, "excluded": r.excluded.len(), "secret_blocked": r.secret_blocked, "heldout_generated": generated}),
    )
}

// ---------------------------------------------------------------- A10
pub fn a10_verify_memory(
    root: &Path,
    verdict: Option<&str>,
    session: &str,
    role: &str,
) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A9")?;
    if b["memory_builder_session"].as_str() == Some(session) {
        return Err(GovError::new(
            "INDEPENDENCE",
            "memory verifier session must differ from the memory builder session (Role F)",
        ));
    }
    let mut p = Project::open(root);
    p.invalidate();
    // delete/rebuild guarantee (§19): two full rebuilds from Git + records at the same tree state must be identical
    let first = crate::memory::indexer::rebuild(
        &p,
        crate::memory::indexer::IndexOptions {
            incremental: false,
            ..Default::default()
        },
    )?;
    let before = Some(first.manifest_hash.clone());
    let rebuilt = crate::memory::indexer::rebuild(
        &p,
        crate::memory::indexer::IndexOptions {
            incremental: false,
            ..Default::default()
        },
    )?;
    let reproducible = before.as_deref() == Some(rebuilt.manifest_hash.as_str());
    // held-out retrieval regression on the fresh index
    let db = RuntimeDb::open(&p.db_path())?;
    let held = read_yaml(&root.join(p.policies().get_str(
        "MEMORY_POLICY",
        "regression.heldout_file",
        "governance/tests/memory/heldout.yaml",
    )))?;
    let h = crate::retrieval::run_heldout(&p, &db, &held)?;
    let secret_leak = db.count_where("artifacts", "path_class='secret'") > 0
        || db.query("SELECT text FROM chunks", &[])?.iter().any(|r| {
            !p.secret_scanner()
                .scan_text(r["text"].as_str().unwrap_or(""), "c")
                .is_empty()
        });
    let status = crate::status::status(&p)?;
    let computed = if h["pass"].as_bool().unwrap_or(false) && reproducible && !secret_leak {
        "MEMORY_ACCEPTED_FOR_V4_AUDIT"
    } else {
        "MEMORY_REJECTED_NEEDS_REPAIR"
    };
    let final_verdict = verdict.unwrap_or(computed);
    if final_verdict == "MEMORY_ACCEPTED_FOR_V4_AUDIT" && computed != final_verdict {
        return Err(
            GovError::new("VERDICT_CONFLICT", format!("evidence computes {computed}"))
                .with_details(
                    json!({"heldout": h, "reproducible": reproducible, "secret_leak": secret_leak}),
                ),
        );
    }
    let md = format!("# 11 — Independent memory verification\n\nVerifier: {role} (session {session}) at {}.\n\n- held-out: recall@k {:.2}, MRR {:.2}, stale-hit {:.2}, superseded-hit {:.2}, forbidden {} → pass={}\n- delete/rebuild reproducibility: {reproducible} (before {:?}, after {})\n- secret exclusion: leak={secret_leak}\n- fresh-agent reconstruction: status packet ok, next action: {}\n\n**Verdict: {final_verdict}**\n", now_iso(), h["recall_at_k"].as_f64().unwrap_or(0.0), h["mrr"].as_f64().unwrap_or(0.0), h["stale_hit_rate"].as_f64().unwrap_or(0.0), h["superseded_hit_rate"].as_f64().unwrap_or(0.0), h["forbidden_violations"], h["pass"], before, rebuilt.manifest_hash, status["next_action"]);
    write_md(root, "11-INDEPENDENT-MEMORY-VERIFICATION.md", &md)?;
    let mut b2 = b.clone();
    b2["verdicts"]["A10"] = json!({"verdict": final_verdict, "session": session, "role": role, "at": now_iso(), "reproducible": reproducible});
    b2["stage_status"]["A10"] = json!(if final_verdict.starts_with("MEMORY_ACCEPTED") {
        "done"
    } else {
        "rejected"
    });
    b2["stage_times"]["A10"] = json!(now_iso());
    save_baseline(root, &b2)?;
    let failed: Vec<Value> = h["results"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter(|x| !x["pass"].as_bool().unwrap_or(false))
                .cloned()
                .collect()
        })
        .unwrap_or_default();
    Ok(
        json!({"stage": "A10", "verdict": final_verdict, "heldout": {"recall_at_k": h["recall_at_k"], "mrr": h["mrr"], "pass": h["pass"], "queries": h["queries"], "stale_hit_rate": h["stale_hit_rate"], "superseded_hit_rate": h["superseded_hit_rate"], "forbidden_violations": h["forbidden_violations"], "failed": failed}, "reproducible": reproducible, "secret_leak": secret_leak}),
    )
}

// ---------------------------------------------------------------- A11
pub fn a11_audit(root: &Path, accept_exceptions: bool) -> Result<Value> {
    let b = load_baseline(root)?;
    require_stage(&b, "A10")?;
    require_verdict(&b, "A10", &["MEMORY_ACCEPTED_FOR_V4_AUDIT"])?;
    let mut p = Project::open(root);
    p.invalidate();
    let _ = crate::memory::indexer::rebuild(
        &p,
        crate::memory::indexer::IndexOptions {
            incremental: true,
            ..Default::default()
        },
    )?; // audit a fresh index
    let audit = crate::verification::audit(
        &p,
        &crate::verification::SuiteOptions {
            deep: true,
            families: vec![],
        },
        true,
    )?;
    let _ = crate::memory::indexer::rebuild(
        &p,
        crate::memory::indexer::IndexOptions {
            incremental: true,
            ..Default::default()
        },
    )?; // the audit record is evidence; keep the index fresh
    let doctor = crate::doctor::run(&p)?;
    // adoption's own findings, re-derived now (not taken from A7): legacy mechanisms still active, retirements that
    // left active references, and extracted knowledge awaiting review — each with a stable id (BC-P2-21)
    let catalogue =
        read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl"))).unwrap_or_default();
    let vc = verify::verify_catalogue(root, &catalogue);
    let mut adoption_findings: Vec<Value> = vec![];
    for l in vc["legacy_in_active_tree"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        adoption_findings.push(json!({"severity": "high", "family": "adoption_legacy", "path": l, "message": format!("legacy mechanism {} is still active and unregistered (INV-004)", l.as_str().unwrap_or(""))}));
    }
    for g in vc["legacy_retirement_pending_gate"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        let deps: Vec<String> = g["dependency_proof"]
            .as_array()
            .map(|a| {
                a.iter()
                    .map(|r| format!("{}:{}", r["from"].as_str().unwrap_or(""), r["line"]))
                    .collect()
            })
            .unwrap_or_default();
        adoption_findings.push(json!({"severity": "high", "family": "adoption_legacy", "path": g["path"], "message": format!("legacy mechanism {} is still active: its retirement awaits Human Decision Gate {} ({}){}", g["path"].as_str().unwrap_or(""), g["gate"].as_str().unwrap_or("-"), g["gate_reasons"], if deps.is_empty() { String::new() } else { format!("; active references: {}", deps.join(", ")) })}));
    }
    for k in vc["legacy_kept_by_decision"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        adoption_findings.push(json!({"severity": "medium", "family": "adoption_legacy", "path": k["path"], "message": format!("legacy mechanism {} kept in the active tree by decision on {} (option {}); registered LEGACY, no authority", k["path"].as_str().unwrap_or(""), k["gate"].as_str().unwrap_or("-"), k["option"].as_str().unwrap_or(""))}));
    }
    for a in vc["retired_with_accepted_active_references"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        let r = &a["reference"];
        let live = r["role"] != "docs";
        adoption_findings.push(json!({"severity": if live { "high" } else { "medium" }, "family": "adoption_dependency", "path": r["from"],
            "message": format!("{} {}:{} still refers to retired {} ({} {}); retirement {}; the reference was not re-pointed at the archive — fix or remove it",
                r["role"].as_str().unwrap_or(""), r["from"].as_str().unwrap_or(""), r["line"], r["to"].as_str().unwrap_or(""), r["kind"].as_str().unwrap_or(""), r["resolution"].as_str().unwrap_or(""),
                a["gate"].as_str().map(|g| format!("authorised by gate {g}")).unwrap_or_else(|| "not gated".into()))}));
    }
    // path states after migration may legitimately change through governed work (A7 judged them at migration time);
    // what A11 re-derives is that nothing active depends on retired material
    for m in vc["dependency_problems"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        adoption_findings
            .push(json!({"severity": "high", "family": "adoption_dependency", "message": m}));
    }
    let store = crate::records::RecordStore::load(root);
    for r in store.records.iter().filter(|r| {
        r.rtype() == "report"
            && r.data["review_required"].as_bool().unwrap_or(false)
            && r.status() == "PROVISIONAL"
    }) {
        let n = r.data["units"].as_array().map(|a| a.len()).unwrap_or(0);
        adoption_findings.push(json!({"severity": "low", "family": "adoption_knowledge", "path": r.path, "message": format!("{n} legacy knowledge unit(s) extracted from {} await review in {}", r.get("legacy_source"), r.id())}));
    }
    identity::assign_finding_ids(&mut adoption_findings);
    let adoption_high = adoption_findings
        .iter()
        .filter(|f| f["severity"] == "high" || f["severity"] == "critical")
        .count();
    let legacy_retired = vc["legacy_kept_by_decision"]
        .as_array()
        .map(|a| a.is_empty())
        .unwrap_or(true)
        && vc["legacy_retirement_pending_gate"]
            .as_array()
            .map(|a| a.is_empty())
            .unwrap_or(true)
        && vc["legacy_in_active_tree"]
            .as_array()
            .map(|a| a.is_empty())
            .unwrap_or(true)
        && !vc["retired_with_accepted_active_references"]
            .as_array()
            .map(|a| a.iter().any(|x| x["reference"]["role"] != "docs"))
            .unwrap_or(false);
    let legacy_active = vc["legacy_in_active_tree"]
        .as_array()
        .map(|a| a.len())
        .unwrap_or(0)
        + vc["legacy_retirement_pending_gate"]
            .as_array()
            .map(|a| a.len())
            .unwrap_or(0);
    let inv_count = b["inventory_summary"]["files"].as_u64().unwrap_or(0);
    let class_count = read_jsonl(&ev(root).join("02-CLASSIFICATION.jsonl"))
        .map(|v| v.len() as u64)
        .unwrap_or(0);
    let checks = vec![
        (
            "migration baseline pinned",
            !b["commit"].as_str().unwrap_or("").is_empty(),
        ),
        (
            "every material artefact classified",
            class_count >= inv_count && inv_count > 0,
        ),
        (
            "target path map explicit",
            ev(root).join("04-TARGET-PATH-MAP.jsonl").exists(),
        ),
        (
            "migration plan independently reviewed",
            b["verdicts"]["A5"]["verdict"]
                .as_str()
                .map(|v| v.starts_with("MIGRATION_PLAN_APPROVED"))
                .unwrap_or(false)
                && b["verdicts"]["A5"]["session"] != b["planner_session"],
        ),
        (
            "independent migration tests exist",
            ev(root).join("06-migration-tests.yaml").exists(),
        ),
        (
            "migrated paths/imports/links pass",
            b["verdicts"]["A7"]["verdict"] == "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD",
        ),
        (
            "behaviour baseline preserved or changed by decision",
            b["baseline_tests"]["status"] != "failed"
                || b["verdicts"]["A7"]["verdict"] == "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD",
        ),
        (
            "legacy governance has no accidental authority",
            legacy_active == 0,
        ),
        (
            "unique knowledge extracted from retired stores",
            ev(root).join("09-LEGACY-MEMORY-EXTRACTION.md").exists(),
        ),
        (
            "memory built on stable canonical paths",
            ev(root).join("10-MEMORY-IMPLEMENTATION-REPORT.md").exists(),
        ),
        (
            "independent memory verifier passed",
            b["verdicts"]["A10"]["verdict"] == "MEMORY_ACCEPTED_FOR_V4_AUDIT",
        ),
        (
            "comprehensive v4 audit completed",
            !audit["audit"].as_str().unwrap_or("").is_empty(),
        ),
        (
            "installed release pinned in framework.lock",
            p.lock_path().exists(),
        ),
        (
            "project overlay separate from kernel",
            p.overlay_dir().exists()
                && crate::kernel::verify_kernel(&p.kernel_dir())
                    .map(|v| v.ok)
                    .unwrap_or(false),
        ),
        (
            "clean machine can reconstruct derived runtime",
            b["verdicts"]["A10"]["reproducible"]
                .as_bool()
                .unwrap_or(false),
        ),
    ];
    let all = checks.iter().all(|(_, ok)| *ok) && adoption_high == 0;
    let exceptions = p.overlay().get("PROJECT_EXCEPTIONS.yaml")["exceptions"]
        .as_array()
        .map(|a| a.len())
        .unwrap_or(0);
    // a legacy mechanism kept by an answered gate is an exception a human decided, not an unresolved finding
    let verdict = if all && audit["verdict"] == "HEALTHY" && doctor.verdict == "HEALTHY" {
        if legacy_retired {
            "ADOPTED_HEALTHY"
        } else {
            "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
        }
    } else if all
        && (accept_exceptions || exceptions > 0)
        && audit["counts"]["critical"].as_u64().unwrap_or(0) == 0
    {
        "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
    } else {
        "NOT_ADOPTED_HEALTHY"
    };
    let md = format!("# 12 — Adoption final report\n\nAudit: {} (verdict {}), doctor: {}\n\n| Acceptance criterion | OK |\n|---|---|\n{}\n\nOpen findings: critical {} · high {} · medium {} · low {}\n\n## Adoption findings (stable ids)\n\n| Id | Severity | Finding |\n|---|---|---|\n{}\n\n**Final verdict: {verdict}**\n", audit["audit"], audit["verdict"], doctor.verdict, checks.iter().map(|(n, ok)| format!("| {n} | {} |", if *ok { "✅" } else { "❌" })).collect::<Vec<_>>().join("\n"), audit["counts"]["critical"], audit["counts"]["high"], audit["counts"]["medium"], audit["counts"]["low"],
        adoption_findings.iter().map(|f| format!("| {} | {} | {} |", f["id"].as_str().unwrap_or(""), f["severity"].as_str().unwrap_or(""), f["message"].as_str().unwrap_or("").replace('|', "/"))).collect::<Vec<_>>().join("\n"));
    write_md(root, "12-ADOPTION-FINAL-REPORT.md", &md)?;
    let mut b2 = b.clone();
    b2["verdicts"]["A11"] = json!({"verdict": verdict, "audit": audit["audit"], "at": now_iso()});
    b2["stage_status"]["A11"] = json!("done");
    b2["stage_times"]["A11"] = json!(now_iso());
    b2["final_verdict"] = json!(verdict);
    save_baseline(root, &b2)?;
    let mut messages: Vec<Value> = adoption_findings
        .iter()
        .map(|f| json!({"id": f["id"], "severity": f["severity"], "family": f["family"], "message": f["message"]}))
        .collect();
    messages.extend(audit["findings"].as_array().map(|a| a.iter().take(12).map(|f| json!({"severity": f["severity"], "family": f["family"], "message": f["message"]})).collect::<Vec<_>>()).unwrap_or_default());
    let doctor_failed: Vec<Value> = doctor
        .checks
        .iter()
        .filter(|c| !c["ok"].as_bool().unwrap_or(true))
        .map(|c| json!({"id": c["id"], "message": c["message"]}))
        .collect();
    Ok(
        json!({"stage": "A11", "verdict": verdict, "audit": audit["audit"], "audit_verdict": audit["verdict"], "doctor": doctor.verdict, "checks": checks.iter().map(|(n, ok)| json!({"criterion": n, "ok": ok})).collect::<Vec<_>>(), "findings": audit["counts"], "adoption_findings": adoption_findings, "legacy_authority_retired": legacy_retired, "finding_messages": messages, "doctor_failed": doctor_failed, "evidence": format!("{EVIDENCE}/12-ADOPTION-FINAL-REPORT.md")}),
    )
}

pub fn status(root: &Path) -> Result<Value> {
    let b = load_baseline(root)?;
    let mut stages = vec![];
    for s in STAGES {
        stages.push(json!({"stage": s, "status": b["stage_status"][s].as_str().unwrap_or("pending"), "verdict": b["verdicts"][s]["verdict"]}));
    }
    let next = STAGES
        .iter()
        .find(|s| b["stage_status"][s].as_str().unwrap_or("pending") != "done")
        .map(|s| s.to_string());
    Ok(
        json!({"adoption_id": b["adoption_id"], "commit": b["commit"], "stages": stages, "next_stage": next, "final_verdict": b["final_verdict"], "evidence_dir": EVIDENCE}),
    )
}

pub fn glob_helper(pat: &str, path: &str) -> bool {
    glob_match(pat, path)
}
pub fn read_json_helper(p: &Path) -> Result<Value> {
    read_json(p)
}
