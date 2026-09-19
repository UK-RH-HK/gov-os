//! A7/A5 independent verification helpers: compare the catalogue with reality, run held-out migration tests.
use super::refs::broken_links;
use crate::util::{glob_match, read_text, read_yaml};
use crate::Result;
use serde_json::{json, Value};
use std::path::Path;

/// The verified answer of the Human Decision Gate raised for catalogue entry `e` — only while the gate's recorded
/// subject is still this entry's question (see `adopt::entry_gate_answer`).
fn gate_answer(project: &crate::project::Project, e: &Value) -> Option<String> {
    crate::adopt::entry_gate_answer(project, e)
}

/// The test kinds [`run_tests_file`] executes. An independent test of any other kind cannot pass.
pub const TEST_KINDS: &[&str] = &[
    "path_present",
    "path_absent",
    "link_resolves",
    "text_present",
    "text_absent",
    "command",
    "legacy_not_active",
    "retirement_references",
    "no_secret_in_index",
];

/// What a migration test checks, independent of its label: the test without `id`, `description` and `note`. Two
/// tests with the same identity are the same test whoever renamed it (BC-P2-34: a planner-scaffolded test relabelled
/// is still the planner's).
pub fn test_identity(t: &Value) -> String {
    let mut m = t.clone();
    if let Some(o) = m.as_object_mut() {
        for k in ["id", "description", "note", "author", "authored_by"] {
            o.remove(k);
        }
    }
    crate::util::hash_value(&m)
}

/// Digest of a migration test file exactly as it stands (every test and field).
pub fn tests_digest(tests: &Value) -> String {
    crate::util::hash_value(tests)
}

fn read_ledger(root: &Path) -> Vec<Value> {
    read_text(
        &root
            .join(crate::adopt::EVIDENCE)
            .join("migration-ledger.jsonl"),
    )
    .map(|t| {
        t.lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
            .collect()
    })
    .unwrap_or_default()
}

/// Paths without authority in the catalogue (legacy, historical, superseded, rejected): their references bind nothing.
fn non_authority_paths(catalogue: &[Value]) -> std::collections::BTreeSet<String> {
    catalogue
        .iter()
        .filter(|e| {
            matches!(
                e["authority"].as_str().unwrap_or(""),
                "LEGACY" | "HISTORICAL" | "SUPERSEDED" | "REJECTED"
            )
        })
        .filter_map(|e| e["current_path"].as_str().map(|s| s.to_string()))
        .collect()
}

/// Compare the migration map against the actual tree (executor report is ignored).
///
/// Beyond path states, the verifier re-derives from a fresh scan that **no active code or configuration refers to
/// retired legacy material** (neither to where it was nor to where it was archived) unless a Human Decision Gate
/// answered A for exactly that dependant, and that no legacy mechanism remains active outside a recorded gate
/// (pending, or kept by the human's decision).
pub fn verify_catalogue(root: &Path, catalogue: &[Value]) -> Value {
    let project = crate::project::Project::open(root);
    let ledger = read_ledger(root);
    let ar = "archive";
    let mut entries = vec![];
    let mut problems = vec![];
    for e in catalogue {
        let action = e["action"].as_str().unwrap_or("");
        let from = e["current_path"].as_str().unwrap_or("");
        let to = e["target_path"].as_str().unwrap_or("");
        let src = root.join(from).exists();
        let dst = !to.is_empty() && root.join(to).exists();
        let gated = e["requires_human_gate"].as_bool().unwrap_or(false);
        let state = match action {
            "KEEP_IN_PLACE" => {
                if src {
                    "PRESENT"
                } else {
                    "NOT_FOUND"
                }
            }
            "MOVE" | "RENAME" => {
                if !src && dst {
                    "MIGRATED"
                } else if src && dst {
                    "CONFLICTING"
                } else if src && gated {
                    "PRESENT_GATED"
                } else if src {
                    "PRESENT"
                } else {
                    "NOT_FOUND"
                }
            }
            "EXTRACT" if to.contains("memory-stores") => {
                if src {
                    "PRESENT"
                } else {
                    "RETIRED"
                }
            }
            "EXTRACT" => {
                if !src {
                    "MIGRATED"
                } else if gated {
                    "PRESENT_GATED"
                } else {
                    "PRESENT"
                }
            }
            "RETIRE" | "DELETE_FROM_ACTIVE_TREE" => {
                if !src {
                    "RETIRED"
                } else if gated {
                    "PRESENT_GATED"
                } else {
                    "PRESENT"
                }
            }
            _ => "UNKNOWN",
        };
        let deferred_store = action == "EXTRACT" && to.contains("memory-stores");
        let expected_done = matches!(
            action,
            "MOVE" | "RENAME" | "EXTRACT" | "RETIRE" | "DELETE_FROM_ACTIVE_TREE"
        ) && !gated
            && !deferred_store;
        if expected_done && !matches!(state, "MIGRATED" | "RETIRED") {
            problems.push(format!(
                "{} expected {} but state is {state} ({from})",
                e["artifact_id"], action
            ));
        }
        if state == "CONFLICTING" {
            problems.push(format!(
                "{} exists at both source and target",
                e["artifact_id"]
            ));
        }
        entries.push(json!({"artifact_id": e["artifact_id"], "action": action, "current_path": from, "target_path": to, "finding_state": state}));
    }
    let links = broken_links(root);
    let deferred: Vec<String> = catalogue
        .iter()
        .filter(|e| {
            e["action"] == "EXTRACT"
                && e["target_path"]
                    .as_str()
                    .map(|t| t.contains("memory-stores"))
                    .unwrap_or(false)
        })
        .map(|e| e["current_path"].as_str().unwrap_or("").to_string())
        .collect();
    // legacy mechanisms still in the active tree: acceptable only under a recorded Human Decision Gate
    let mut legacy = vec![];
    let mut pending_gate = vec![];
    let mut kept_by_decision = vec![];
    for l in super::classify::legacy_mechanisms(root) {
        if deferred.contains(&l.path) {
            continue;
        }
        let entry = catalogue
            .iter()
            .find(|e| e["current_path"].as_str() == Some(l.path.as_str()));
        match entry {
            Some(e) if e["requires_human_gate"].as_bool().unwrap_or(false) => {
                match gate_answer(&project, e).as_deref() {
                    Some("A") => {
                        let blocked = ledger.iter().rev().find(|r| r["artifact_id"] == e["artifact_id"] && r["status"] != "skipped")
                            .map(|r| r["status"] == "blocked").unwrap_or(false);
                        problems.push(format!(
                            "{} ({}) : its gate {} was answered A but the retirement {}; re-run `gov adopt migrate --batch {}`{}",
                            e["artifact_id"].as_str().unwrap_or(""), l.path, e["human_gate"].as_str().unwrap_or(""),
                            if blocked { "was blocked by a changed dependency proof" } else { "has not been executed" },
                            e["batch"], if blocked { " after re-planning (gov adopt map, gov adopt plan)" } else { "" }
                        ));
                    }
                    Some(o) => kept_by_decision.push(json!({"path": l.path, "artifact_id": e["artifact_id"], "gate": e["human_gate"], "option": o, "gate_reasons": e["gate_reasons"]})),
                    None => pending_gate.push(json!({"path": l.path, "artifact_id": e["artifact_id"], "gate": e["human_gate"], "gate_reasons": e["gate_reasons"], "dependency_proof": e["dependency_proof"]["active_references"]})),
                }
            }
            _ => legacy.push(l.path),
        }
    }
    // no active reference to retired material, and none re-pointed at the archive
    let os = super::ownership::OsState::load(root);
    let active = super::references::ActiveSet {
        root,
        os: &os,
        archive_root: ar.into(),
        leaving: non_authority_paths(catalogue),
    };
    let mut accepted_dangling = vec![];
    let mut unaccepted = vec![];
    let mut historical_citations: Vec<Value> = vec![];
    // every artefact retired by any adoption pass (the ledger, including A8 store retirements) or by this plan
    let mut retired: Vec<(String, String, String, Option<Value>)> = vec![]; // (artifact id, path, archive target, row)
    for r in ledger
        .iter()
        .rev()
        .filter(|r| r["status"] == "applied" && r["phase"] != "extract")
    {
        let path = r["path"].as_str().unwrap_or("").to_string();
        if path.is_empty() || root.join(&path).exists() || retired.iter().any(|x| x.1 == path) {
            continue;
        }
        let to = r["result"]["to"]
            .as_str()
            .or(r["result"]["original_archived_to"].as_str())
            .unwrap_or("")
            .to_string();
        let is_retirement = r["result"]["deleted"] == true || to.starts_with(&format!("{ar}/"));
        if is_retirement {
            retired.push((
                r["artifact_id"].as_str().unwrap_or("").to_string(),
                path,
                to,
                Some(r.clone()),
            ));
        }
    }
    for e in catalogue {
        let from = e["current_path"].as_str().unwrap_or("");
        let Some(target) = super::planner::retirement_target(e, ar) else {
            continue;
        };
        if root.join(from).exists() || retired.iter().any(|x| x.1 == from) {
            continue; // not retired, or already known from the ledger
        }
        retired.push((
            e["artifact_id"].as_str().unwrap_or("").to_string(),
            from.to_string(),
            target,
            None,
        ));
    }
    let ghosts: Vec<String> = retired.iter().map(|x| x.1.clone()).collect();
    let index = super::references::build_fresh_with_ghosts(root, &ghosts);
    for (aid, from, target, row) in &retired {
        let (aid, from, target) = (aid.as_str(), from.as_str(), target.clone());
        let applied = row.as_ref();
        let allowed: Vec<String> = applied
            .and_then(|r| {
                r["result"]["retired_with_active_references"]
                    .as_array()
                    .cloned()
            })
            .unwrap_or_default()
            .iter()
            .filter_map(|x| x["from"].as_str().map(|s| s.to_string()))
            .collect();
        let explicit: Vec<String> = if target.is_empty() {
            vec![]
        } else {
            vec![target.clone()]
        };
        for r in index.active_references(&[from.to_string()], &explicit, &active) {
            let v = r.to_value();
            if r.to == from && allowed.contains(&r.from) {
                accepted_dangling.push(json!({"artifact_id": aid, "reference": v, "gate": applied.map(|a| a["result"]["authorised_by_gate"].clone())}));
            } else if r.role == "docs" {
                // documentation naming retired material (provenance of extracted records, history notes, or a
                // citation of the archived copy): informational — it binds no functionality and was not re-pointed
                // by the migration, which never rewrites active files into the archive
                historical_citations.push(json!({"artifact_id": aid, "reference": v}));
            } else {
                unaccepted.push(json!({"artifact_id": aid, "reference": v}));
            }
        }
    }
    // any active code/configuration resolving into the legacy archive, whatever put it there
    let mut into_archive = vec![];
    let mut citations_of_archive = vec![];
    for r in index.edges.iter().filter(|r| {
        r.to.starts_with(&format!("{ar}/")) && active.is_active(&r.from) && r.role != "provenance"
    }) {
        if r.role == "docs" {
            citations_of_archive.push(r.to_value());
        } else if !unaccepted.iter().any(|u| {
            u["reference"]["from"] == r.from.as_str() && u["reference"]["to"] == r.to.as_str()
        }) {
            into_archive.push(r.to_value());
        }
    }
    let problems_before_dependencies = problems.len();
    for u in &unaccepted {
        problems.push(format!(
            "active {} reference to retired material {} from {}:{} (retirement not authorised for this dependant)",
            u["reference"]["kind"].as_str().unwrap_or(""),
            u["reference"]["to"].as_str().unwrap_or(""),
            u["reference"]["from"].as_str().unwrap_or(""),
            u["reference"]["line"]
        ));
    }
    for r in &into_archive {
        problems.push(format!(
            "active {} {} refers into the archive: {} (active code/configuration must not depend on archived material)",
            r["role"].as_str().unwrap_or(""),
            r["from"].as_str().unwrap_or(""),
            r["to"].as_str().unwrap_or("")
        ));
    }
    let accepted_link_files: Vec<(String, String)> = accepted_dangling
        .iter()
        .map(|a| {
            (
                a["reference"]["from"].as_str().unwrap_or("").to_string(),
                a["reference"]["to"].as_str().unwrap_or("").to_string(),
            )
        })
        .collect();
    let (accepted_links, broken): (Vec<(String, String)>, Vec<(String, String)>) =
        links.into_iter().partition(|(f, t)| {
            accepted_link_files.iter().any(|(af, at)| {
                af == f && {
                    let d = Path::new(f)
                        .parent()
                        .map(|p| p.to_string_lossy().to_string())
                        .unwrap_or_default();
                    let resolved = super::references::normalize_rel(&if d.is_empty() {
                        t.clone()
                    } else {
                        format!("{d}/{t}")
                    });
                    &resolved == at
                }
            })
        });
    let dependency_problems: Vec<String> = problems[problems_before_dependencies..].to_vec();
    json!({"entries": entries, "problems": problems, "dependency_problems": dependency_problems, "broken_links": broken.iter().map(|(f, t)| json!({"file": f, "target": t})).collect::<Vec<_>>(),
        "accepted_broken_links": accepted_links.iter().map(|(f, t)| json!({"file": f, "target": t})).collect::<Vec<_>>(),
        "legacy_in_active_tree": legacy, "legacy_retirement_pending_gate": pending_gate, "legacy_kept_by_decision": kept_by_decision,
        "retired_with_accepted_active_references": accepted_dangling, "active_citations_of_archived_material": citations_of_archive, "documentation_naming_retired_material": historical_citations,
        "deferred_memory_stores": deferred, "ok": problems.is_empty() && legacy.is_empty()})
}

/// Execute independent-authored migration tests (YAML). Kinds: path_present, path_absent, link_resolves, text_absent,
/// text_present, command (exit 0), legacy_not_active, no_secret_in_index.
pub fn run_tests_file(root: &Path, tests_path: &Path) -> Result<Value> {
    run_tests_file_upto(root, tests_path, None)
}

/// Run tests whose `after_batch` is <= `upto_batch` (tests without `after_batch` always run).
pub fn run_tests_file_upto(
    root: &Path,
    tests_path: &Path,
    upto_batch: Option<i64>,
) -> Result<Value> {
    let tests = read_yaml(tests_path)?;
    let mut results = vec![];
    let mut pass = 0;
    let mut fail = 0;
    let mut deferred = 0;
    let mut deferred_reasons = vec![];
    let catalogue_path = root
        .join(crate::adopt::EVIDENCE)
        .join("04-TARGET-PATH-MAP.jsonl");
    let catalogue: Vec<Value> = if catalogue_path.exists() {
        read_text(&catalogue_path)?
            .lines()
            .filter(|l| !l.trim().is_empty())
            .filter_map(|l| serde_json::from_str(l).ok())
            .collect()
    } else {
        vec![]
    };
    let project = crate::project::Project::open(root);
    // one fresh reference scan for every `retirement_references` test of this run
    let needs_refs = tests["tests"]
        .as_array()
        .map(|a| a.iter().any(|t| t["kind"] == "retirement_references"))
        .unwrap_or(false);
    let ref_index = if needs_refs {
        let ghosts: Vec<String> = tests["tests"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter(|t| t["kind"] == "retirement_references")
                    .filter_map(|t| t["path"].as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default();
        super::references::build_fresh_with_ghosts(root, &ghosts)
    } else {
        super::references::ReferenceIndex::default()
    };
    let os = super::ownership::OsState::load(root);
    let active = super::references::ActiveSet {
        root,
        os: &os,
        archive_root: "archive".into(),
        leaving: non_authority_paths(&catalogue),
    };
    for t in tests["tests"].as_array().cloned().unwrap_or_default() {
        if let (Some(ub), Some(ab)) = (upto_batch, t["after_batch"].as_i64()) {
            if ab > ub {
                deferred += 1;
                continue;
            }
        }
        // Tests for entries behind a Human Decision Gate follow the recorded decision: pending → deferred (the batch
        // must not act), answered A → the test runs, any other option → the human kept the entry in place and the
        // planned removal is no longer part of the plan (recorded, not counted as a failure).
        if let Some(aid) = t["gate_artifact"].as_str() {
            let entry = catalogue
                .iter()
                .find(|e| e["artifact_id"].as_str() == Some(aid));
            let gate = entry.and_then(|e| e["human_gate"].as_str()).unwrap_or("");
            match entry
                .and_then(|e| crate::adopt::entry_gate_answer(&project, e))
                .as_deref()
            {
                Some("A") => {}
                Some(other) => {
                    deferred += 1;
                    deferred_reasons.push(json!({"id": t["id"], "artifact_id": aid, "gate": gate, "reason": format!("human gate answered {other}: entry kept in place by decision; planned action withdrawn")}));
                    continue;
                }
                None => {
                    deferred += 1;
                    deferred_reasons.push(json!({"id": t["id"], "artifact_id": aid, "gate": gate, "reason": if gate.is_empty() { "no gate record for a gated entry (A4 creates one)".to_string() } else { "human gate pending: destructive action not executed".to_string() }}));
                    continue;
                }
            }
        }
        let kind = t["kind"].as_str().unwrap_or("");
        let target = t["path"].as_str().unwrap_or("").to_string();
        let ok = match kind {
            "path_present" => root.join(&target).exists(),
            "path_absent" => !root.join(&target).exists(),
            "text_present" => read_text(&root.join(&target))
                .map(|s| s.contains(t["text"].as_str().unwrap_or("\u{0}")))
                .unwrap_or(false),
            "text_absent" => read_text(&root.join(&target))
                .map(|s| !s.contains(t["text"].as_str().unwrap_or("\u{0}")))
                .unwrap_or(true),
            "link_resolves" => {
                let dir = Path::new(&target).parent().unwrap_or(Path::new(""));
                root.join(dir)
                    .join(t["link"].as_str().unwrap_or(""))
                    .exists()
            }
            "legacy_not_active" => !super::classify::legacy_mechanisms(root)
                .iter()
                .any(|l| glob_match(t["pattern"].as_str().unwrap_or(&target), &l.path)),
            "command" => {
                let cmd: Vec<String> = t["command"]
                    .as_array()
                    .map(|a| {
                        a.iter()
                            .filter_map(|x| x.as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_default();
                let cwd = root.join(t["cwd"].as_str().unwrap_or(""));
                crate::util::run_cmd(&cmd, &cwd)
                    .map(|(c, _, _)| c == t["expect_exit"].as_i64().unwrap_or(0) as i32)
                    .unwrap_or(false)
            }
            // after a retirement: nothing active refers to the archived copy (no re-pointing into the archive), and
            // nothing active refers to the retired path except the dependants the retirement's gate accepted
            "retirement_references" => {
                let archive_target = t["archive_target"].as_str().unwrap_or("").to_string();
                let allowed: Vec<String> = t["allowed_from"]
                    .as_array()
                    .map(|a| {
                        a.iter()
                            .filter_map(|x| x.as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_default();
                let explicit: Vec<String> = if archive_target.is_empty() {
                    vec![]
                } else {
                    vec![archive_target.clone()]
                };
                let refs = ref_index.active_references(&[target.clone()], &explicit, &active);
                // re-pointing at the archive fails whoever did it; a remaining reference to the retired path fails
                // when it is live (code/configuration) and not a dependant the retirement's gate accepted
                refs.iter().all(|r| {
                    r.to == target
                        && (allowed.contains(&r.from)
                            || r.role == "docs"
                            || root.join(&target).exists())
                })
            }
            "no_secret_in_index" => {
                let db = root.join(crate::RUNTIME_DIR).join("state.db");
                if !db.exists() {
                    true
                } else {
                    let d = crate::memory::db::RuntimeDb::open(&db)?;
                    if !d.has_schema() {
                        true
                    } else {
                        let scanner = crate::security::secrets::SecretScanner::from_policies(
                            &crate::util::read_yaml(
                                &crate::kernel_trust::trusted_root_of(root)
                                    .join("policies")
                                    .join("SECURITY_POLICY.yaml"),
                            )
                            .unwrap_or(json!({})),
                            &json!({}),
                        );
                        let literal = t["text"].as_str().filter(|x| !x.is_empty());
                        d.count_where("artifacts", "path_class='secret'") == 0
                            && d.query("SELECT text FROM chunks", &[])?.iter().all(|r| {
                                let txt = r["text"].as_str().unwrap_or("");
                                scanner.scan_text(txt, "chunk").is_empty()
                                    && literal.map(|l| !txt.contains(l)).unwrap_or(true)
                            })
                    }
                }
            }
            _ => false,
        };
        if ok {
            pass += 1;
        } else {
            fail += 1;
        }
        results.push(json!({"id": t["id"], "kind": kind, "ok": ok, "path": target, "description": t["description"]}));
    }
    Ok(
        json!({"tests": results.len(), "pass": pass, "fail": fail, "deferred": deferred, "deferred_reasons": deferred_reasons, "ok": fail == 0, "results": results}),
    )
}

/// Scaffold held-out migration tests from the catalogue for the independent reviewer to extend.
///
/// Every expectation is derived from the disposition the plan gives the artefact, so the plan and the scaffolded
/// tests agree on every artefact (BC-P2-33; Contract v3:928-929) — including a legacy store that also carries
/// secrets, a retirement held behind a Human Decision Gate, and a legacy memory store retired only in A8. A legacy
/// mechanism found in the tree but absent from the catalogue gets a `legacy_not_active` test: the plan missed it.
pub fn scaffold_tests(
    catalogue: &[Value],
    legacy_paths: &[String],
    product_test_cmd: Option<Vec<String>>,
) -> Value {
    let mut tests = vec![];
    let mut n = 0;
    let mut push = |kind: &str, path: &str, extra: Value, desc: String| {
        n += 1;
        let mut t =
            json!({"id": format!("MT-{n:03}"), "kind": kind, "path": path, "description": desc});
        if let Some(o) = extra.as_object() {
            for (k, v) in o {
                t[k] = v.clone();
            }
        }
        tests.push(t);
    };
    push(
        "path_present",
        "governance/framework.lock",
        json!({"after_batch": 0}),
        "kernel pinned".into(),
    );
    push(
        "path_present",
        "governance/kernel/KERNEL_MANIFEST.json",
        json!({"after_batch": 0}),
        "kernel installed".into(),
    );
    push(
        "path_present",
        "governance/project/REPOSITORY_CONTRACT.yaml",
        json!({"after_batch": 0}),
        "overlay separate from kernel".into(),
    );
    let gated = |e: &Value| e["requires_human_gate"].as_bool().unwrap_or(false);
    let gate_extra = |e: &Value, b: i64| {
        let mut x = json!({"after_batch": b});
        if gated(e) {
            x["gate_artifact"] = e["artifact_id"].clone();
        }
        x
    };
    let suffix = |e: &Value| {
        if gated(e) {
            " (after its human gate is answered A)"
        } else {
            ""
        }
    };
    for e in catalogue
        .iter()
        .filter(|e| matches!(e["action"].as_str(), Some("MOVE") | Some("RENAME")))
    {
        let b = e["batch"].as_i64().unwrap_or(0);
        push(
            "path_absent",
            e["current_path"].as_str().unwrap_or(""),
            gate_extra(e, b),
            format!("{} moved away{}", e["artifact_id"], suffix(e)),
        );
        push(
            "path_present",
            e["target_path"].as_str().unwrap_or(""),
            gate_extra(e, b),
            format!("{} present at target{}", e["artifact_id"], suffix(e)),
        );
    }
    for e in catalogue.iter().filter(|e| {
        e["action"] == "DELETE_FROM_ACTIVE_TREE"
            || e["action"] == "RETIRE"
            || (e["action"] == "EXTRACT"
                && !e["target_path"]
                    .as_str()
                    .map(|t| t.contains("memory-stores"))
                    .unwrap_or(false))
    }) {
        let what = match e["action"].as_str().unwrap_or("") {
            "RETIRE" => "retired to archive/code-reference",
            "EXTRACT" => "extracted into governed records and archived",
            _ => "deleted from active tree",
        };
        push(
            "path_absent",
            e["current_path"].as_str().unwrap_or(""),
            gate_extra(e, e["batch"].as_i64().unwrap_or(6)),
            format!("{} {what}{}", e["artifact_id"], suffix(e)),
        );
    }
    // every executed retirement leaves no active reference re-pointed at the archive, and no dependant beyond those
    // its gate accepted
    for e in catalogue.iter().filter(|e| {
        e["dependency_proof"].is_object()
            && !e["target_path"]
                .as_str()
                .map(|t| t.contains("memory-stores"))
                .unwrap_or(false)
    }) {
        let allowed: Vec<Value> = e["dependency_proof"]["active_references"]
            .as_array()
            .map(|a| a.iter().map(|r| r["from"].clone()).collect())
            .unwrap_or_default();
        let mut x = gate_extra(e, e["batch"].as_i64().unwrap_or(0));
        x["archive_target"] = e["dependency_proof"]["archive_target"].clone();
        x["allowed_from"] = json!(allowed);
        push(
            "retirement_references",
            e["current_path"].as_str().unwrap_or(""),
            x,
            format!(
                "{}: no active reference re-pointed at archived material; no dependant beyond the proof {}",
                e["artifact_id"],
                if gated(e) { "its gate accepted" } else { "(none)" }
            ),
        );
    }
    for l in legacy_paths {
        let entry = catalogue
            .iter()
            .find(|e| e["current_path"].as_str() == Some(l.as_str()));
        let Some(e) = entry else {
            push(
                "legacy_not_active",
                l,
                json!({"pattern": l, "after_batch": 6}),
                format!("legacy mechanism {l} not active (INV-004) — not in the catalogue: re-run A1-A3"),
            );
            continue;
        };
        if e["action"] == "KEEP_IN_PLACE"
            || (e["action"] == "EXTRACT"
                && e["target_path"]
                    .as_str()
                    .map(|t| t.contains("memory-stores"))
                    .unwrap_or(false))
        {
            continue; // kept by the plan (surfaced by A7), or extracted/retired in A8 and registered in the LEG record
        }
        let b = e["batch"].as_i64().unwrap_or(6);
        let mut x = gate_extra(e, b);
        x["pattern"] = json!(l);
        push(
            "legacy_not_active",
            l,
            x,
            format!("legacy mechanism {l} not active (INV-004){}", suffix(e)),
        );
    }
    if let Some(cmd) = product_test_cmd {
        push(
            "command",
            ".",
            json!({"command": cmd, "expect_exit": 0}),
            "behaviour baseline: product tests pass".into(),
        );
    }
    push(
        "no_secret_in_index",
        ".",
        json!({}),
        "no secret material in the derived index (secret scanner over every indexed chunk)".into(),
    );
    json!({"version": "1", "authored_by": "scaffold (independent reviewer must review, extend and sign)", "tests": tests})
}

/// Contradictions between the plan and the independent migration tests: a test expecting an artefact's removal
/// where the plan keeps it (or holds it behind a human gate the test ignores), its presence where the plan removes
/// it, or a legacy store gone before A8 retires it. An approved plan and its tests must agree on every artefact's
/// disposition (Contract v3:928-929); executing a plan its own tests contradict can only fail and roll back.
pub fn plan_test_agreement(catalogue: &[Value], tests: &Value) -> Vec<Value> {
    let mut out = vec![];
    let deferred = |e: &Value| {
        e["action"] == "EXTRACT"
            && e["target_path"]
                .as_str()
                .map(|t| t.contains("memory-stores"))
                .unwrap_or(false)
    };
    for t in tests["tests"].as_array().cloned().unwrap_or_default() {
        let kind = t["kind"].as_str().unwrap_or("");
        let path = t["path"].as_str().unwrap_or("");
        let gated_test = t["gate_artifact"].as_str();
        let mut conflict = |e: &Value, why: String| {
            out.push(json!({"test": t["id"], "kind": kind, "path": path, "artifact_id": e["artifact_id"], "plan": {"action": e["action"], "batch": e["batch"], "requires_human_gate": e["requires_human_gate"]}, "conflict": why}));
        };
        if let Some(e) = catalogue
            .iter()
            .find(|e| e["current_path"].as_str() == Some(path))
        {
            let gated = e["requires_human_gate"].as_bool().unwrap_or(false);
            let aid = e["artifact_id"].as_str();
            let removes = e["action"] != "KEEP_IN_PLACE";
            match kind {
                "path_absent" | "legacy_not_active" => {
                    if !removes {
                        conflict(
                            e,
                            format!("the plan keeps {path} in place; the test expects it gone"),
                        );
                    } else if gated && gated_test != aid {
                        conflict(e, format!("{path} leaves the active tree only if its Human Decision Gate is answered A; the test expects it gone regardless of the decision (add gate_artifact)"));
                    } else if deferred(e) && t["after_batch"].is_i64() {
                        conflict(e, format!("{path} is a legacy memory store retired in A8 after migration acceptance; the test expects it gone after an A6 batch"));
                    }
                }
                "path_present" => {
                    let ab = t["after_batch"].as_i64();
                    let eb = e["batch"].as_i64().unwrap_or(0);
                    if removes && !gated && !deferred(e) && ab.map(|b| b >= eb).unwrap_or(true) {
                        conflict(e, format!("the plan moves/retires {path} in batch {eb}; the test expects it still present"));
                    }
                }
                _ => {}
            }
        }
        if kind == "path_present" {
            if let Some(e) = catalogue
                .iter()
                .find(|e| e["target_path"].as_str() == Some(path) && !path.is_empty())
            {
                let gated = e["requires_human_gate"].as_bool().unwrap_or(false);
                if gated && gated_test != e["artifact_id"].as_str() {
                    let mut c = |why: String| {
                        out.push(json!({"test": t["id"], "kind": kind, "path": path, "artifact_id": e["artifact_id"], "plan": {"action": e["action"], "batch": e["batch"], "requires_human_gate": true}, "conflict": why}));
                    };
                    c(format!("{path} exists only after a Human Decision Gate is answered A; the test expects it regardless (add gate_artifact)"));
                }
            }
        }
    }
    out
}
