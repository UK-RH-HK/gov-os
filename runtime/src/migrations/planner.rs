//! A3/A4 target path map + batched plan. No file moves. Unknown items block destructive batches.
use serde_json::{json, Value};
use std::path::Path;

fn spec_subdir(class: &str, path: &str, low: &str) -> &'static str {
    let p = path.to_lowercase();
    match class {
        "DECISION" => "decisions",
        "LESSON" => "lessons",
        "RESEARCH_EVIDENCE" => "research",
        "REPORT_EVIDENCE" => "reports",
        "TASK" => "tasks",
        _ => {
            if p.contains("requirement") || low.contains("shall") {
                "requirements"
            } else if p.contains("architect") {
                "architecture"
            } else if p.contains("scenario") || p.contains("journey") {
                "scenarios"
            } else if p.contains("interface") || p.contains("api") {
                "interfaces"
            } else if p.contains("feature") {
                "features"
            } else if p.contains("product") || p.contains("vision") || p.contains("mission") {
                "product"
            } else if p.contains("security") {
                "security"
            } else if p.contains("perf") {
                "performance"
            } else {
                "requirements"
            }
        }
    }
}

/// Build the migration catalogue (one entry per classified artefact) with actions, batches and verification.
pub fn plan(
    root: &Path,
    classified: &[Value],
    product_test_dir: Option<&str>,
    unused_code_action: &str,
) -> Vec<Value> {
    // ARCHIVE_POLICY.unused_code_action: `remove_from_active_tree` (git preserves history) or `archive_reference`
    let dead_action = if unused_code_action == "archive_reference" {
        "RETIRE"
    } else {
        "DELETE_FROM_ACTIVE_TREE"
    };
    let mut out = vec![];
    for c in classified {
        let path = c["path"].as_str().unwrap_or("").to_string();
        let class = c["class"].as_str().unwrap_or("UNKNOWN");
        let authority = c["authority"].as_str().unwrap_or("UNKNOWN_OR_CONFLICTING");
        let name = path.rsplit('/').next().unwrap_or(&path).to_string();
        let low = crate::util::read_text(&root.join(&path))
            .map(|t| t.chars().take(2000).collect::<String>().to_lowercase())
            .unwrap_or_default();
        let misplaced = c["reasons"]
            .as_array()
            .map(|a| {
                a.iter()
                    .any(|r| r.as_str().unwrap_or("").contains("misplaced"))
            })
            .unwrap_or(false);
        let is_record = c["reasons"]
            .as_array()
            .map(|a| a.iter().any(|r| r.as_str() == Some("record")))
            .unwrap_or(false);
        let (action, target, target_class, reason, batch, gate, index_policy, verification): (&str, Option<String>, &str, String, i64, bool, Value, Vec<&str>) = match class {
            "SECRET" => ("KEEP_IN_PLACE", None, "SECRET", "secrets are never moved by automation; classified secret in the repository contract, excluded from index/export, must be gitignored".into(), 0, false, json!({"semantic_index": false, "lexical_index": false, "export": "denied"}), vec!["not_indexed", "not_exported", "gitignored_or_human_gate"]),
            "GOVERNANCE_CURRENT" => ("KEEP_IN_PLACE", None, "GOVERNANCE_CURRENT", "installed kernel/overlay".into(), 0, false, json!({}), vec!["path_present"]),
            "HISTORICAL" if path.starts_with("archive/") => ("KEEP_IN_PLACE", None, "HISTORICAL", "already archived".into(), 0, false, json!({"default_retrieval": false}), vec![]),
            "GOVERNANCE_LEGACY" => ("MOVE", Some(format!("archive/governance/legacy-rules/{}", path.replace('/', "__"))), "HISTORICAL", "legacy provider/governance rule retired to archive (INV-004); no active authority".into(), 1, false, json!({"default_retrieval": false, "semantic_index": false}), vec!["path_absent_at_source", "path_present_at_target", "not_authoritative"]),
            "HISTORICAL" if c["kinds"].as_array().map(|a| a.iter().any(|k| k == "chat_store")).unwrap_or(false) => ("EXTRACT", Some(format!("archive/governance/memory-stores/{}", name)), "HISTORICAL", "chat/session store: extract unique durable knowledge (A8) then retire to archive; never imported raw into active memory (§70)".into(), 6, false, json!({"semantic_index": false, "lexical_index": false, "default_retrieval": false}), vec!["knowledge_extracted", "path_absent_at_source", "not_indexed"]),
            "GENERATED" if authority == "LEGACY" => ("DELETE_FROM_ACTIVE_TREE", None, "GENERATED", "stale derived index; rebuilt by gov rebuild-memory after path stabilisation (git history preserves it)".into(), 6, false, json!({"semantic_index": false, "lexical_index": false}), vec!["path_absent_at_source"]),
            "GENERATED" => ("KEEP_IN_PLACE", None, "GENERATED", "build output; excluded from index; should be gitignored".into(), 0, false, json!({"semantic_index": false, "lexical_index": false}), vec![]),
            "DECISION" | "LESSON" if is_record && !path.starts_with("spec/") => ("MOVE", Some(format!("spec/{}/{}", spec_subdir(class, &path, &low), name)), class, "governed record located outside spec/; relocated into the canonical spec tree (duplicate ids are surfaced by doctor)".into(), 2, false, json!({"semantic_index": true, "graph_index": true}), vec!["path_absent_at_source", "path_present_at_target"]),
            "DECISION" | "LESSON" if !path.starts_with("spec/") => ("EXTRACT", Some(format!("spec/{}/", spec_subdir(class, &path, &low))), if class == "DECISION" { "DECISION" } else { "LESSON" }, "legacy decision/lesson document: extract into governed PROVISIONAL records with provenance; original archived".into(), 2, false, json!({"semantic_index": true, "graph_index": true}), vec!["records_created_with_provenance", "original_archived", "links_updated"]),
            "SPEC_AUTHORITATIVE" | "SPEC_DERIVED" | "RESEARCH_EVIDENCE" | "REPORT_EVIDENCE" | "TASK" if misplaced || (!path.starts_with("spec/") && class != "SPEC_DERIVED") => ("MOVE", Some(format!("spec/{}/{}", spec_subdir(class, &path, &low), name)), class, "spec/evidence material normalised into the canonical spec tree; links/citations updated".into(), 2, false, json!({"semantic_index": true, "graph_index": true}), vec!["path_absent_at_source", "path_present_at_target", "links_updated"]),
            "SPEC_AUTHORITATIVE" | "SPEC_DERIVED" | "RESEARCH_EVIDENCE" | "REPORT_EVIDENCE" | "TASK" | "DECISION" | "LESSON" => ("KEEP_IN_PLACE", None, class, "already in canonical location".into(), 0, false, json!({"semantic_index": true}), vec!["path_present"]),
            "PRODUCT_TEST" if misplaced => ("MOVE", Some(format!("{}/{}", product_test_dir.unwrap_or("tests"), name)), "PRODUCT_TEST", "test file relocated into the native test directory; imports updated".into(), 4, false, json!({"code_index": true}), vec!["path_present_at_target", "imports_resolve", "tests_run"]),
            "PRODUCT_TEST" => ("KEEP_IN_PLACE", None, "PRODUCT_TEST", "native test layout preserved (mapped via repository contract)".into(), 0, false, json!({"code_index": true}), vec!["tests_run"]),
            "PRODUCT_SOURCE" if misplaced => ("MOVE", Some(format!("product/{}", name)), "PRODUCT_SOURCE", "source located outside the product tree; relocated with imports rewritten (reversible: batch snapshot + independent tests; no human gate for a non-destructive move)".into(), 3, false, json!({"code_index": true}), vec!["path_present_at_target", "imports_resolve", "build_or_tests_run"]),
            "PRODUCT_SOURCE" | "TOOLING" | "DEVOPS" | "DATA_TEST" | "DATA_RUNTIME" => ("KEEP_IN_PLACE", None, class, "native product/devops/data layout preserved and described by the repository contract (§8.1, §79.3)".into(), 0, false, json!({"code_index": class == "PRODUCT_SOURCE"}), vec!["path_present"]),
            "DEAD_OR_UNUSED" => (dead_action, None, "DEAD_OR_UNUSED", format!("no references found; ARCHIVE_POLICY.unused_code_action={unused_code_action} — destructive, requires an answered Human Decision Gate (§71)"), 7, true, json!({"semantic_index": false}), vec!["human_gate_answered", "path_absent_at_source", "build_or_tests_run"]),
            _ => ("KEEP_IN_PLACE", None, "UNKNOWN", "unknown artefact: blocks destructive batches until classified (protocol §8)".into(), 0, false, json!({}), vec!["classified_before_destructive_batches"]),
        };
        let finding_state = if class == "UNKNOWN" {
            "UNKNOWN"
        } else {
            "PRESENT"
        };
        out.push(json!({"artifact_id": c["artifact_id"], "current_path": path, "current_class": class, "authority": authority, "target_path": target, "target_class": target_class, "action": action, "reason": reason,
            "references": c.get("references").cloned().unwrap_or(json!([])), "imports": c.get("imports").cloned().unwrap_or(json!([])), "consumers": c.get("references").cloned().unwrap_or(json!([])), "index_policy": index_policy, "sensitivity": if class == "SECRET" { "secret" } else { "internal" },
            "rollback": "batch snapshot under .governance-runtime/migration/batch-<n>/ restored by `gov adopt rollback --batch <n>`; git history preserves deletions", "verification": verification, "batch": batch, "requires_human_gate": gate, "confidence": c["confidence"], "finding_state": finding_state}));
    }
    out
}

pub fn batches(catalogue: &[Value]) -> Vec<Value> {
    let defs = [
        (
            0,
            "Install/pin kernel + establish overlay (no destructive migration)",
        ),
        (
            1,
            "Governance authority: retire legacy provider rules and governance docs to archive",
        ),
        (
            2,
            "Spec normalisation: move/extract non-code records into spec/; update citations",
        ),
        (
            3,
            "Product source relocation (only where justified; human gate)",
        ),
        (4, "Tests/devops relocation and import updates"),
        (5, "Citation/link verification"),
        (
            6,
            "Legacy memory stores: extract unique knowledge, retire stores, delete stale indexes",
        ),
        (7, "Destructive cleanup of dead/unused code (human gate)"),
    ];
    defs.iter().map(|(n, d)| { let entries: Vec<&Value> = catalogue.iter().filter(|e| e["batch"].as_i64() == Some(*n) && e["action"] != "KEEP_IN_PLACE").collect();
        json!({"batch": n, "description": d, "entries": entries.len(), "actions": entries.iter().map(|e| e["artifact_id"].clone()).collect::<Vec<_>>(), "requires_human_gate": entries.iter().any(|e| e["requires_human_gate"].as_bool().unwrap_or(false)), "rollback_point": format!("snapshot batch-{n}"), "pre_tests": ["independent path/link/import tests", "affected product tests"], "post_tests": ["independent path/link/import tests", "affected product tests", "checkpoint"]}) }).collect()
}

pub fn plan_markdown(catalogue: &[Value], batches: &[Value], unknown: usize) -> String {
    let mut s = String::from("# 05 — Adoption/migration plan\n\nOrder follows protocol §9: kernel first, governance authority, spec normalisation, links, product source only where justified, tests/devops, legacy retirement, memory rebuild only after path stability.\n\n");
    s.push_str(&format!("Unknown artefacts blocking destructive batches: **{unknown}**\n\n## Batches\n\n| # | Description | Entries | Human gate |\n|---|---|---|---|\n"));
    for b in batches {
        s.push_str(&format!(
            "| {} | {} | {} | {} |\n",
            b["batch"],
            b["description"].as_str().unwrap_or(""),
            b["entries"],
            b["requires_human_gate"]
        ));
    }
    s.push_str("\n## Actions (non KEEP_IN_PLACE)\n\n| Artefact | Action | From | To | Batch | Gate |\n|---|---|---|---|---|---|\n");
    for e in catalogue.iter().filter(|e| e["action"] != "KEEP_IN_PLACE") {
        s.push_str(&format!(
            "| {} | {} | {} | {} | {} | {} |\n",
            e["artifact_id"].as_str().unwrap_or(""),
            e["action"].as_str().unwrap_or(""),
            e["current_path"].as_str().unwrap_or(""),
            e["target_path"].as_str().unwrap_or("-"),
            e["batch"],
            e["requires_human_gate"]
        ));
    }
    s.push_str("\n## Memory stores to inspect before retirement\n\n");
    for e in catalogue.iter().filter(|e| e["action"] == "EXTRACT") {
        s.push_str(&format!(
            "- {} → {}\n",
            e["current_path"].as_str().unwrap_or(""),
            e["target_path"].as_str().unwrap_or("")
        ));
    }
    s.push_str("\n## Post-migration indexing plan\n\n1. Independent migration verification (A7) must return MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD.\n2. `gov adopt build-memory` (A9) rebuilds the Development Knowledge Fabric on stable canonical paths.\n3. Independent memory verification (A10) with held-out queries.\n");
    s
}
