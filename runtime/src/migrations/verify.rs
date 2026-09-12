//! A7/A5 independent verification helpers: compare the catalogue with reality, run held-out migration tests.
use super::refs::broken_links;
use crate::util::{glob_match, read_text, read_yaml};
use crate::Result;
use serde_json::{json, Value};
use std::path::Path;

/// Compare the migration map against the actual tree (executor report is ignored).
pub fn verify_catalogue(root: &Path, catalogue: &[Value]) -> Value {
    let mut entries = vec![]; let mut problems = vec![];
    for e in catalogue {
        let action = e["action"].as_str().unwrap_or(""); let from = e["current_path"].as_str().unwrap_or(""); let to = e["target_path"].as_str().unwrap_or("");
        let src = root.join(from).exists(); let dst = !to.is_empty() && root.join(to).exists();
        let state = match action {
            "KEEP_IN_PLACE" => if src { "PRESENT" } else { "NOT_FOUND" },
            "MOVE" | "RENAME" => if !src && dst { "MIGRATED" } else if src && dst { "CONFLICTING" } else if src { "PRESENT" } else { "NOT_FOUND" },
            "EXTRACT" if to.contains("memory-stores") => if src { "PRESENT" } else { "RETIRED" },
            "EXTRACT" => if !src { "MIGRATED" } else { "PRESENT" },
            "RETIRE" | "DELETE_FROM_ACTIVE_TREE" => if !src { "RETIRED" } else if e["requires_human_gate"].as_bool().unwrap_or(false) { "PRESENT" } else { "PRESENT" },
            _ => "UNKNOWN",
        };
        let deferred_store = action == "EXTRACT" && to.contains("memory-stores");
        let expected_done = matches!(action, "MOVE" | "RENAME" | "EXTRACT" | "RETIRE" | "DELETE_FROM_ACTIVE_TREE") && !e["requires_human_gate"].as_bool().unwrap_or(false) && !deferred_store;
        if expected_done && !matches!(state, "MIGRATED" | "RETIRED") { problems.push(format!("{} expected {} but state is {state} ({from})", e["artifact_id"], action)); }
        if state == "CONFLICTING" { problems.push(format!("{} exists at both source and target", e["artifact_id"])); }
        entries.push(json!({"artifact_id": e["artifact_id"], "action": action, "current_path": from, "target_path": to, "finding_state": state}));
    }
    let links = broken_links(root);
    let deferred: Vec<String> = catalogue.iter().filter(|e| e["action"] == "EXTRACT" && e["target_path"].as_str().map(|t| t.contains("memory-stores")).unwrap_or(false)).map(|e| e["current_path"].as_str().unwrap_or("").to_string()).collect();
    let legacy: Vec<String> = super::classify::legacy_mechanisms(root).into_iter().map(|l| l.path).filter(|p| !deferred.contains(p)).collect();
    json!({"entries": entries, "problems": problems, "broken_links": links.iter().map(|(f, t)| json!({"file": f, "target": t})).collect::<Vec<_>>(), "legacy_in_active_tree": legacy, "deferred_memory_stores": deferred, "ok": problems.is_empty() && legacy.is_empty()})
}

/// Execute independent-authored migration tests (YAML). Kinds: path_present, path_absent, link_resolves, text_absent,
/// text_present, command (exit 0), legacy_not_active, no_secret_in_index.
pub fn run_tests_file(root: &Path, tests_path: &Path) -> Result<Value> { run_tests_file_upto(root, tests_path, None) }

/// Run tests whose `after_batch` is <= `upto_batch` (tests without `after_batch` always run).
pub fn run_tests_file_upto(root: &Path, tests_path: &Path, upto_batch: Option<i64>) -> Result<Value> {
    let tests = read_yaml(tests_path)?;
    let mut results = vec![]; let mut pass = 0; let mut fail = 0; let mut deferred = 0;
    for t in tests["tests"].as_array().cloned().unwrap_or_default() {
        if let (Some(ub), Some(ab)) = (upto_batch, t["after_batch"].as_i64()) { if ab > ub { deferred += 1; continue; } }
        let kind = t["kind"].as_str().unwrap_or(""); let target = t["path"].as_str().unwrap_or("").to_string();
        let ok = match kind {
            "path_present" => root.join(&target).exists(),
            "path_absent" => !root.join(&target).exists(),
            "text_present" => read_text(&root.join(&target)).map(|s| s.contains(t["text"].as_str().unwrap_or("\u{0}"))).unwrap_or(false),
            "text_absent" => read_text(&root.join(&target)).map(|s| !s.contains(t["text"].as_str().unwrap_or("\u{0}"))).unwrap_or(true),
            "link_resolves" => { let dir = Path::new(&target).parent().unwrap_or(Path::new("")); root.join(dir).join(t["link"].as_str().unwrap_or("")).exists() }
            "legacy_not_active" => !super::classify::legacy_mechanisms(root).iter().any(|l| glob_match(t["pattern"].as_str().unwrap_or(&target), &l.path)),
            "command" => { let cmd: Vec<String> = t["command"].as_array().map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default(); let cwd = root.join(t["cwd"].as_str().unwrap_or("")); crate::util::run_cmd(&cmd, &cwd).map(|(c, _, _)| c == t["expect_exit"].as_i64().unwrap_or(0) as i32).unwrap_or(false) }
            "no_secret_in_index" => {
                let db = root.join(crate::RUNTIME_DIR).join("state.db");
                if !db.exists() { true } else {
                    let d = crate::memory::db::RuntimeDb::open(&db)?;
                    if !d.has_schema() { true } else {
                        let scanner = crate::security::secrets::SecretScanner::from_policies(&crate::util::read_yaml(&root.join("governance/kernel/policies/SECURITY_POLICY.yaml")).unwrap_or(json!({})), &json!({}));
                        let literal = t["text"].as_str().filter(|x| !x.is_empty());
                        d.count_where("artifacts", "path_class='secret'") == 0 && d.query("SELECT text FROM chunks", &[])?.iter().all(|r| { let txt = r["text"].as_str().unwrap_or(""); scanner.scan_text(txt, "chunk").is_empty() && literal.map(|l| !txt.contains(l)).unwrap_or(true) })
                    }
                }
            }
            _ => false,
        };
        if ok { pass += 1; } else { fail += 1; }
        results.push(json!({"id": t["id"], "kind": kind, "ok": ok, "path": target, "description": t["description"]}));
    }
    Ok(json!({"tests": results.len(), "pass": pass, "fail": fail, "deferred": deferred, "ok": fail == 0, "results": results}))
}

/// Scaffold held-out migration tests from the catalogue for the independent reviewer to extend.
pub fn scaffold_tests(catalogue: &[Value], legacy_paths: &[String], product_test_cmd: Option<Vec<String>>) -> Value {
    let mut tests = vec![]; let mut n = 0;
    let mut push = |kind: &str, path: &str, extra: Value, desc: String| { n += 1; let mut t = json!({"id": format!("MT-{n:03}"), "kind": kind, "path": path, "description": desc}); if let Some(o) = extra.as_object() { for (k, v) in o { t[k] = v.clone(); } } tests.push(t); };
    push("path_present", "governance/framework.lock", json!({"after_batch": 0}), "kernel pinned".into());
    push("path_present", "governance/kernel/KERNEL_MANIFEST.json", json!({"after_batch": 0}), "kernel installed".into());
    push("path_present", "governance/project/REPOSITORY_CONTRACT.yaml", json!({"after_batch": 0}), "overlay separate from kernel".into());
    for e in catalogue.iter().filter(|e| matches!(e["action"].as_str(), Some("MOVE") | Some("RENAME")) && !e["requires_human_gate"].as_bool().unwrap_or(false)) {
        let b = e["batch"].as_i64().unwrap_or(0);
        push("path_absent", e["current_path"].as_str().unwrap_or(""), json!({"after_batch": b}), format!("{} moved away", e["artifact_id"]));
        push("path_present", e["target_path"].as_str().unwrap_or(""), json!({"after_batch": b}), format!("{} present at target", e["artifact_id"]));
    }
    for e in catalogue.iter().filter(|e| e["action"] == "DELETE_FROM_ACTIVE_TREE") { push("path_absent", e["current_path"].as_str().unwrap_or(""), json!({"after_batch": e["batch"].as_i64().unwrap_or(6)}), format!("{} deleted from active tree", e["artifact_id"])); }
    for l in legacy_paths {
        let entry = catalogue.iter().find(|e| e["current_path"].as_str() == Some(l.as_str()));
        if entry.map(|e| e["action"] == "EXTRACT" && e["target_path"].as_str().map(|t| t.contains("memory-stores")).unwrap_or(false)).unwrap_or(false) { continue; } // extracted/retired in A8, registered in LEG record
        let b = entry.and_then(|e| e["batch"].as_i64()).unwrap_or(6);
        push("legacy_not_active", l, json!({"pattern": l, "after_batch": b}), format!("legacy mechanism {l} not active (INV-004)"));
    }
    if let Some(cmd) = product_test_cmd { push("command", ".", json!({"command": cmd, "expect_exit": 0}), "behaviour baseline: product tests pass".into()); }
    push("no_secret_in_index", ".", json!({}), "no secret material in the derived index (secret scanner over every indexed chunk)".into());
    json!({"version": "1", "authored_by": "scaffold (independent reviewer must review, extend and sign)", "tests": tests})
}
