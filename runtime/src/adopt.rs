//! `gov adopt`: staged, path-first, memory-safe brownfield adoption (framework §79, protocol A0-A11) with an
//! immutable evidence tree and independence enforced by session/role separation and verdict gates.
use crate::kernel::{install_kernel, resolve_kernel_source};
use crate::lock::write_lock;
use crate::memory::db::RuntimeDb;
use crate::migrations::{classify, executor, inventory, planner, verify};
use crate::records::{new_record, save_record};
use crate::util::{glob_match, now_iso, read_json, read_text, read_yaml, write_text, write_yaml};
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
pub fn a3_map(root: &Path) -> Result<Value> {
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
    let catalogue = planner::plan(
        root,
        &classified,
        native_test_dir(root).as_deref(),
        &unused_action,
    );
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
    let mut jl = String::new();
    for e in &catalogue {
        jl.push_str(&serde_json::to_string(e)?);
        jl.push('\n');
    }
    write_text(&ev(root).join("04-TARGET-PATH-MAP.jsonl"), &jl)?;
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
    set_stage(
        root,
        "A3",
        "done",
        Some((
            "path_map_summary",
            json!({"actions": actions, "unknown": unknown}),
        )),
    )?;
    Ok(
        json!({"stage": "A3", "entries": catalogue.len(), "actions": actions, "unknown_blocking_destructive": unknown, "schema_problems": problems, "evidence": format!("{EVIDENCE}/04-TARGET-PATH-MAP.jsonl")}),
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
        let g = crate::orchestration::gates::create_system(
            &p,
            json!({"question": format!("Adoption migration: {} {} ({})? {}", e["action"].as_str().unwrap_or(""), e["current_path"].as_str().unwrap_or(""), aid, e["reason"].as_str().unwrap_or("")), "why_now": "destructive or structural migration action in the approved plan", "current_state": format!("present at {}", e["current_path"].as_str().unwrap_or("")), "options": [{"id": "A", "description": format!("approve {}", e["action"].as_str().unwrap_or(""))}, {"id": "B", "description": "keep in place (skip this entry)"}], "impact": format!("target: {}", e["target_path"].as_str().unwrap_or("removed from active tree")), "reversibility": "batch snapshot + git history", "recommendation": "A if no reference or unique data exists", "confidence": e["confidence"].as_f64().unwrap_or(0.5), "trigger": "destructive_migration", "impact_radius": "R2", "artifact_id": aid}),
        )?;
        let gid = g["id"].as_str().unwrap_or("").to_string();
        e["human_gate"] = json!(gid);
        created.push(gid);
    }
    if !created.is_empty() {
        let mut jl = String::new();
        for e in catalogue.iter() {
            jl.push_str(&serde_json::to_string(e)?);
            jl.push('\n');
        }
        write_text(&ev(root).join("04-TARGET-PATH-MAP.jsonl"), &jl)?;
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
    require_stage(&b, "A3")?;
    set_stage(root, "A4", "in_progress", None)?;
    let mut catalogue = read_jsonl(&ev(root).join("04-TARGET-PATH-MAP.jsonl"))?;
    let gates_created = ensure_destructive_gates(root, &mut catalogue)?;
    let batches = planner::batches(&catalogue);
    let unknown = catalogue
        .iter()
        .filter(|e| e["finding_state"] == "UNKNOWN")
        .count();
    write_yaml(
        &ev(root).join("05-plan.yaml"),
        &json!({"batches": batches, "unknown_blocking": unknown, "created_at": now_iso()}),
    )?;
    write_md(
        root,
        "05-ADOPTION-MIGRATION-PLAN.md",
        &planner::plan_markdown(&catalogue, &batches, unknown),
    )?;
    set_stage(root, "A4", "done", None)?;
    Ok(
        json!({"stage": "A4", "batches": batches.iter().map(|b| json!({"batch": b["batch"], "entries": b["entries"], "human_gate": b["requires_human_gate"]})).collect::<Vec<_>>(), "human_gates_created": gates_created, "evidence": [format!("{EVIDENCE}/05-ADOPTION-MIGRATION-PLAN.md"), format!("{EVIDENCE}/05-plan.yaml")]}),
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
    let md = format!("# 06 — Independent migration test design\n\nAuthored by a fresh independent session (Role B). Scaffold generated by the planner; the reviewer must review classification, target map, destructive moves, unknown items, references/imports, authority changes, archive/delete decisions and old memory stores, then extend `06-migration-tests.yaml` and record a verdict with `gov adopt review`.\n\nTest families: path integrity · code integrity · governance integrity · behaviour preservation · rollback/recovery.\n\nScaffolded tests: {}\n\n## Verdicts\n\n", tests["tests"].as_array().map(|a| a.len()).unwrap_or(0));
    let p = ev(root).join("06-INDEPENDENT-MIGRATION-TEST-DESIGN.md");
    if !p.exists() {
        write_text(&p, &md)?;
    }
    Ok(
        json!({"stage": "A5", "tests_file": format!("{EVIDENCE}/06-migration-tests.yaml"), "scaffolded_tests": tests["tests"].as_array().map(|a| a.len()).unwrap_or(0), "next": "independent reviewer extends tests and runs `gov adopt review --verdict MIGRATION_PLAN_APPROVED --session <fresh-session>`"}),
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
fn brownfield_contract(root: &Path, kernel_dir: &Path, classified: &[Value]) -> Result<Value> {
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
            "SECRET" => secret_paths.push(path.to_string()),
            _ => {}
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
            let manifest = if root.join("governance/framework.lock").exists() {
                crate::kernel::read_manifest(&gov.join("kernel"))?
            } else {
                install_kernel(Some(&src), &gov)?
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
            let contract = brownfield_contract(root, &gov.join("kernel"), &classified)?;
            let opts = crate::init::InitOptions {
                source: None,
                project_name: project_name.into(),
                alias: alias.into(),
                mode: "adopt".into(),
                force: false,
                intent: None,
                skip_index: true,
            };
            let written =
                crate::init::write_overlay(root, &gov.join("kernel"), &opts, Some(contract))?;
            crate::init::ensure_roots(root)?;
            let mut p = Project::open(root);
            p.invalidate();
            crate::tools::generate_registry(&p)?;
            crate::adapters::generate(&p)?;
            let gates_created = ensure_destructive_gates(root, &mut catalogue)?;
            entry["installed"] = json!({"version": manifest["version"], "overlay_written": written, "destructive_gates_created": gates_created});
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
            let mut r = executor::apply_batch(root, &catalogue, n, &answered, &ledger)?;
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
    let md = format!("# 08 — Independent migration verification\n\nVerifier: {role} (session {session}) at {}. Executor confidence statements ignored; actual paths inspected.\n\n- Catalogue vs reality: {} problem(s), {} broken link(s), {} legacy mechanism(s) still active\n- Independent tests: {} pass / {} fail\n- Secrets isolated: {secrets_ok}\n- Kernel intact: {kernel_ok}\n\n**Verdict: {final_verdict}**\n\n```json\n{}\n```\n", now_iso(), vc["problems"].as_array().map(|a| a.len()).unwrap_or(0), vc["broken_links"].as_array().map(|a| a.len()).unwrap_or(0), vc["legacy_in_active_tree"].as_array().map(|a| a.len()).unwrap_or(0), tests["pass"], tests["fail"], serde_json::to_string_pretty(&json!({"catalogue": vc, "tests": tests}))?);
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
        json!({"stage": "A7", "verdict": final_verdict, "catalogue_problems": vc["problems"], "broken_links": vc["broken_links"], "legacy_in_active_tree": vc["legacy_in_active_tree"], "tests": {"pass": tests["pass"], "fail": tests["fail"]}, "secrets_isolated": secrets_ok, "kernel_intact": kernel_ok}),
    )
}

// ---------------------------------------------------------------- A8
fn extract_strings_from_sqlite(path: &Path) -> Vec<String> {
    let mut out = vec![];
    let Ok(conn) =
        rusqlite::Connection::open_with_flags(path, rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY)
    else {
        return out;
    };
    let tables: Vec<String> = conn
        .prepare("SELECT name FROM sqlite_master WHERE type='table'")
        .ok()
        .and_then(|mut s| {
            s.query_map([], |r| r.get::<_, String>(0))
                .ok()
                .map(|it| it.filter_map(|x| x.ok()).collect())
        })
        .unwrap_or_default();
    for t in tables {
        let Ok(mut stmt) = conn.prepare(&format!(
            "SELECT * FROM \"{}\" LIMIT 2000",
            t.replace('"', "")
        )) else {
            continue;
        };
        let n = stmt.column_count();
        let Ok(rows) = stmt.query_map([], |r| {
            let mut v = vec![];
            for i in 0..n {
                if let Ok(s) = r.get::<_, String>(i) {
                    v.push(s);
                }
            }
            Ok(v)
        }) else {
            continue;
        };
        for r in rows.flatten() {
            for s in r {
                if s.len() > 20 {
                    out.push(s);
                }
            }
        }
    }
    out
}

fn extract_strings_from_jsonl(path: &Path) -> Vec<String> {
    let Ok(text) = read_text(path) else {
        return vec![];
    };
    let mut out = vec![];
    let mut push_val = |v: &Value| {
        for k in ["content", "text", "message", "body", "summary"] {
            if let Some(s) = v.get(k).and_then(|x| x.as_str()) {
                if s.len() > 20 {
                    out.push(s.to_string());
                }
            }
        }
    };
    if let Ok(Value::Array(a)) = serde_json::from_str::<Value>(&text) {
        for v in a {
            push_val(&v);
            if let Some(msgs) = v.get("messages").and_then(|m| m.as_array()) {
                for m in msgs {
                    push_val(m);
                }
            }
        }
    } else {
        for l in text.lines() {
            if let Ok(v) = serde_json::from_str::<Value>(l) {
                push_val(&v);
                if let Some(msgs) = v.get("messages").and_then(|m| m.as_array()) {
                    for m in msgs {
                        push_val(m);
                    }
                }
            }
        }
    }
    out
}

const DECISION_CUES: &[&str] = &[
    "decision:",
    "decided",
    "we will ",
    "we chose",
    "agreed to",
    "must use",
    "policy:",
];
const LESSON_CUES: &[&str] = &[
    "lesson:",
    "learned",
    "lesson learned",
    "in future",
    "root cause",
    "never again",
    "mistake",
    "retrospective",
];

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
    let catalogue = read_jsonl(&ev(root).join("04-TARGET-PATH-MAP.jsonl"))?;
    let scanner = scanner_for(root);
    let mut stores = vec![];
    let mut created = vec![];
    let mut retired = vec![];
    let mut seen: std::collections::HashSet<String> = std::collections::HashSet::new();
    let mut n_d = 0;
    let mut n_l = 0;
    // stores = catalogue EXTRACT entries pointing to memory-stores + archived legacy rule files
    let mut sources: Vec<(String, String)> = catalogue
        .iter()
        .filter(|e| {
            e["action"] == "EXTRACT"
                && e["target_path"]
                    .as_str()
                    .map(|t| t.contains("memory-stores"))
                    .unwrap_or(false)
        })
        .map(|e| {
            (
                e["current_path"].as_str().unwrap_or("").to_string(),
                e["target_path"].as_str().unwrap_or("").to_string(),
            )
        })
        .collect();
    for e in catalogue
        .iter()
        .filter(|e| e["current_class"] == "GOVERNANCE_LEGACY" && e["action"] == "MOVE")
    {
        if let Some(t) = e["target_path"].as_str() {
            sources.push((t.to_string(), String::new()));
        }
    }
    for (path, target) in sources {
        let already_archived =
            !root.join(&path).exists() && !target.is_empty() && root.join(&target).exists();
        let read_path = if already_archived {
            target.clone()
        } else {
            path.clone()
        };
        let full = root.join(&read_path);
        let (kind, strings) = if !full.exists() {
            ("NOT_FOUND", vec![])
        } else if path.ends_with(".db") || path.ends_with(".sqlite") || path.ends_with(".sqlite3") {
            ("sqlite", extract_strings_from_sqlite(&full))
        } else if path.ends_with(".jsonl") || path.ends_with(".json") {
            ("jsonl", extract_strings_from_jsonl(&full))
        } else {
            (
                "text",
                read_text(&full)
                    .map(|t| {
                        t.split("\n\n")
                            .map(|s| s.trim().to_string())
                            .filter(|s| s.len() > 20)
                            .collect()
                    })
                    .unwrap_or_default(),
            )
        };
        let mut extracted = 0;
        let mut skipped_secret = 0;
        for s in &strings {
            let low = s.to_lowercase();
            if !scanner.scan_text(s, &path).is_empty() {
                skipped_secret += 1;
                continue;
            }
            let is_dec = DECISION_CUES.iter().any(|c| low.contains(c));
            let is_les = LESSON_CUES.iter().any(|c| low.contains(c));
            if !is_dec && !is_les {
                continue;
            }
            let key: String = low
                .chars()
                .filter(|c| c.is_alphanumeric())
                .take(120)
                .collect();
            if !seen.insert(key) {
                continue;
            }
            let title: String = s.lines().next().unwrap_or("").chars().take(90).collect();
            let rec = if is_dec {
                n_d += 1;
                let id = format!("D-C{n_d:04}");
                new_record(
                    "decision",
                    &id,
                    &title,
                    json!({"status": "PROVISIONAL", "state_class": "AUTHORITATIVE", "question": title, "chosen_option": "as-recorded-in-legacy-store", "rationale": s.chars().take(1500).collect::<String>(), "human_approved": false, "legacy_source": path, "provenance": {"extracted_from": path, "store_kind": kind, "extracted_at": now_iso(), "authority_note": "extracted from a retired legacy memory store; PROVISIONAL until confirmed (INV-004, §70)"}, "tags": ["legacy-extraction", "chat-derived"]}),
                )
            } else {
                n_l += 1;
                let id = format!("L-C{n_l:04}");
                new_record(
                    "lesson",
                    &id,
                    &title,
                    json!({"status": "PROVISIONAL", "state_class": "EVIDENCE", "scope": "PROJECT", "lifecycle": "candidate", "problem_statement": title, "body": s.chars().take(1500).collect::<String>(), "evidence_strength": "low", "legacy_source": path, "provenance": {"extracted_from": path, "store_kind": kind, "extracted_at": now_iso()}, "tags": ["legacy-extraction", "chat-derived"]}),
                )
            };
            save_record(root, &rec)?;
            created.push(rec.path.clone());
            extracted += 1;
        }
        let disposition = if kind == "NOT_FOUND" {
            "NOT_FOUND"
        } else if already_archived {
            retired.push(target.clone());
            "RETIRE"
        } else if !target.is_empty() {
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
            "RETIRE"
        } else {
            "KEEP_AS_TEMPORARY_EVIDENCE"
        };
        stores.push(json!({"path": path, "kind": kind, "strings": strings.len(), "extracted": extracted, "skipped_secret_strings": skipped_secret, "disposition": disposition, "archived_to": target}));
    }
    // LEGACY registration record
    let legacy_paths: Vec<String> = catalogue
        .iter()
        .filter(|e| e["authority"] == "LEGACY")
        .map(|e| e["current_path"].as_str().unwrap_or("").to_string())
        .collect();
    let mut rec = new_record(
        "legacy",
        "LEG-0001",
        "Retired legacy governance and memory mechanisms",
        json!({"status": "LEGACY", "state_class": "HISTORICAL", "paths": legacy_paths, "archived": retired, "body": "Legacy mechanisms inventoried in A2, retired in A6/A8. They carry no authority (INV-004). Unique durable knowledge was extracted into PROVISIONAL records with provenance.", "extracted_records": created}),
    );
    rec.path = "archive/governance/LEG-0001.yaml".into();
    save_record(root, &rec)?;
    let md = format!("# 09 — Legacy memory extraction\n\n| Store | Kind | Strings | Extracted | Disposition |\n|---|---|---|---|---|\n{}\n\nCreated {} PROVISIONAL record(s): {}\n\nRaw chat/session content was not imported into active semantic memory (§70, protocol §13).\n", stores.iter().map(|s| format!("| {} | {} | {} | {} | {} |", s["path"].as_str().unwrap_or(""), s["kind"].as_str().unwrap_or(""), s["strings"], s["extracted"], s["disposition"].as_str().unwrap_or(""))).collect::<Vec<_>>().join("\n"), created.len(), created.join(", "));
    write_md(root, "09-LEGACY-MEMORY-EXTRACTION.md", &md)?;
    set_stage(root, "A8", "done", None)?;
    Ok(
        json!({"stage": "A8", "stores": stores, "created_records": created, "retired": retired, "legacy_record": "archive/governance/LEG-0001.yaml"}),
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
    let legacy_active = classify::legacy_mechanisms(root).len();
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
    let all = checks.iter().all(|(_, ok)| *ok);
    let exceptions = p.overlay().get("PROJECT_EXCEPTIONS.yaml")["exceptions"]
        .as_array()
        .map(|a| a.len())
        .unwrap_or(0);
    let verdict = if all && audit["verdict"] == "HEALTHY" && doctor.verdict == "HEALTHY" {
        "ADOPTED_HEALTHY"
    } else if all
        && (accept_exceptions || exceptions > 0)
        && audit["counts"]["critical"].as_u64().unwrap_or(0) == 0
    {
        "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
    } else {
        "NOT_ADOPTED_HEALTHY"
    };
    let md = format!("# 12 — Adoption final report\n\nAudit: {} (verdict {}), doctor: {}\n\n| Acceptance criterion | OK |\n|---|---|\n{}\n\nOpen findings: critical {} · high {} · medium {} · low {}\n\n**Final verdict: {verdict}**\n", audit["audit"], audit["verdict"], doctor.verdict, checks.iter().map(|(n, ok)| format!("| {n} | {} |", if *ok { "✅" } else { "❌" })).collect::<Vec<_>>().join("\n"), audit["counts"]["critical"], audit["counts"]["high"], audit["counts"]["medium"], audit["counts"]["low"]);
    write_md(root, "12-ADOPTION-FINAL-REPORT.md", &md)?;
    let mut b2 = b.clone();
    b2["verdicts"]["A11"] = json!({"verdict": verdict, "audit": audit["audit"], "at": now_iso()});
    b2["stage_status"]["A11"] = json!("done");
    b2["stage_times"]["A11"] = json!(now_iso());
    b2["final_verdict"] = json!(verdict);
    save_baseline(root, &b2)?;
    let messages: Vec<Value> = audit["findings"].as_array().map(|a| a.iter().take(12).map(|f| json!({"severity": f["severity"], "family": f["family"], "message": f["message"]})).collect()).unwrap_or_default();
    let doctor_failed: Vec<Value> = doctor
        .checks
        .iter()
        .filter(|c| !c["ok"].as_bool().unwrap_or(true))
        .map(|c| json!({"id": c["id"], "message": c["message"]}))
        .collect();
    Ok(
        json!({"stage": "A11", "verdict": verdict, "audit": audit["audit"], "audit_verdict": audit["verdict"], "doctor": doctor.verdict, "checks": checks.iter().map(|(n, ok)| json!({"criterion": n, "ok": ok})).collect::<Vec<_>>(), "findings": audit["counts"], "finding_messages": messages, "doctor_failed": doctor_failed, "evidence": format!("{EVIDENCE}/12-ADOPTION-FINAL-REPORT.md")}),
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
