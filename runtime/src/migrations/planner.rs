//! A3/A4 target path map + batched plan. No file moves. Unknown items block destructive batches.
//!
//! Every retirement (an action that takes an artefact out of the active tree: archive moves, EXTRACT of a legacy
//! store or document, RETIRE, DELETE_FROM_ACTIVE_TREE) carries a **dependency proof** computed over code,
//! configuration and docs (BC-P2-33; Contract v3:879, :884). A retirement with active references is not planned as an
//! automatic action: it requires an answered Human Decision Gate bound to that proof and runs in the gated batch, and
//! no migration step ever re-points an active reference at archived legacy material.
use super::identity;
use super::ownership::OsState;
use super::references::{dependency_proof, proof_is_clean, ActiveSet, ReferenceIndex};
use serde_json::{json, Value};
use std::collections::BTreeSet;
use std::path::Path;

/// The batch that holds every retirement or destructive action needing an answered Human Decision Gate.
pub const GATED_BATCH: i64 = 7;
/// The batch whose legacy memory stores are extracted and retired in A8 (after migration acceptance).
pub const MEMORY_STORE_BATCH: i64 = 6;

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

/// Where the original of an EXTRACTed legacy document is archived (see `executor::extract_doc`).
pub fn legacy_doc_archive_path(path: &str) -> String {
    format!("archive/spec/legacy-docs/{}", path.replace('/', "__"))
}

/// Where a RETIREd artefact is archived (see `executor::apply_batch`).
pub fn retired_code_archive_path(path: &str) -> String {
    format!("archive/code-reference/retired/{}", path.replace('/', "__"))
}

fn is_memory_store_extract(e: &Value) -> bool {
    e["action"] == "EXTRACT"
        && e["target_path"]
            .as_str()
            .map(|t| t.contains("memory-stores"))
            .unwrap_or(false)
}

/// The location an entry's artefact is archived to when it is retired (`Some("")` for a deletion), or `None` when
/// the entry's action keeps the artefact in the active tree.
pub fn retirement_target(e: &Value, archive_root: &str) -> Option<String> {
    let path = e["current_path"].as_str().unwrap_or("");
    let target = e["target_path"].as_str().unwrap_or("");
    let ar = format!("{}/", archive_root.trim_end_matches('/'));
    match e["action"].as_str().unwrap_or("") {
        "DELETE_FROM_ACTIVE_TREE" => Some(String::new()),
        "RETIRE" => Some(retired_code_archive_path(path)),
        "MOVE" | "RENAME" if target.starts_with(&ar) => Some(target.to_string()),
        "EXTRACT" if is_memory_store_extract(e) => Some(target.to_string()),
        "EXTRACT" => Some(legacy_doc_archive_path(path)),
        _ => None,
    }
}

fn gate_reasons(e: &Value) -> Vec<String> {
    e["gate_reasons"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default()
}

fn add_gate_reason(e: &mut Value, reason: &str) {
    let mut r = gate_reasons(e);
    if !r.iter().any(|x| x == reason) {
        r.push(reason.to_string());
    }
    e["gate_reasons"] = json!(r);
    e["requires_human_gate"] = json!(true);
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
        let secret = c["sensitivity"] == "secret"
            || c["kinds"]
                .as_array()
                .map(|a| a.iter().any(|k| k == "secret"))
                .unwrap_or(false);
        let low = if secret {
            String::new()
        } else {
            crate::util::read_text(&root.join(&path))
                .map(|t| t.chars().take(2000).collect::<String>().to_lowercase())
                .unwrap_or_default()
        };
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
        let os_owned = c["os_owned"].is_string();
        let chat_store = c["kinds"]
            .as_array()
            .map(|a| a.iter().any(|k| k == "chat_store"))
            .unwrap_or(false);
        let secret_index = json!({"semantic_index": false, "lexical_index": false, "default_retrieval": false, "export": "denied"});
        let (action, target, target_class, reason, batch, gate, index_policy, verification): (&str, Option<String>, &str, String, i64, bool, Value, Vec<&str>) = match class {
            _ if os_owned => ("KEEP_IN_PLACE", None, class, format!("Governance OS {} state: never classified, planned or retired as legacy", c["os_owned"].as_str().unwrap_or("")), 0, false, json!({}), vec!["path_present"]),
            // A legacy memory store that also carries secrets is still a legacy store: it is extracted (secret strings
            // withheld) and retired in A8 like any other, but moving secret material needs an answered Human Decision
            // Gate and its archive location is classified secret in the repository contract (plan and tests agree).
            "HISTORICAL" if chat_store && secret && !path.starts_with("archive/") => ("EXTRACT", Some(format!("archive/governance/memory-stores/{}", name)), "HISTORICAL", "secret-bearing chat/session store: extract unique durable knowledge in A8 (secret strings withheld), then retire to archive under an answered Human Decision Gate; source and archive location classified secret, never indexed or exported (§70, SECURITY_POLICY)".into(), MEMORY_STORE_BATCH, true, secret_index.clone(), vec!["knowledge_extracted", "path_absent_at_source", "not_indexed", "not_exported"]),
            "SECRET" => ("KEEP_IN_PLACE", None, "SECRET", "secrets are never moved by automation; classified secret in the repository contract, excluded from index/export, must be gitignored".into(), 0, false, secret_index.clone(), vec!["not_indexed", "not_exported", "gitignored_or_human_gate"]),
            "GOVERNANCE_CURRENT" => ("KEEP_IN_PLACE", None, "GOVERNANCE_CURRENT", "installed kernel/overlay".into(), 0, false, json!({}), vec!["path_present"]),
            "HISTORICAL" if path.starts_with("archive/") => ("KEEP_IN_PLACE", None, "HISTORICAL", "already archived".into(), 0, false, if secret { secret_index.clone() } else { json!({"default_retrieval": false}) }, vec![]),
            "GOVERNANCE_LEGACY" if secret => ("MOVE", Some(format!("archive/governance/legacy-rules/{}", path.replace('/', "__"))), "HISTORICAL", "secret-bearing legacy provider/governance rule: retired to archive under an answered Human Decision Gate; archive location classified secret (INV-004, SECURITY_POLICY)".into(), GATED_BATCH, true, secret_index.clone(), vec!["path_absent_at_source", "path_present_at_target", "not_authoritative", "not_indexed"]),
            "GOVERNANCE_LEGACY" => ("MOVE", Some(format!("archive/governance/legacy-rules/{}", path.replace('/', "__"))), "HISTORICAL", "legacy provider/governance rule retired to archive (INV-004); no active authority".into(), 1, false, json!({"default_retrieval": false, "semantic_index": false}), vec!["path_absent_at_source", "path_present_at_target", "not_authoritative"]),
            "HISTORICAL" if chat_store => ("EXTRACT", Some(format!("archive/governance/memory-stores/{}", name)), "HISTORICAL", "chat/session store: extract unique durable knowledge (A8) then retire to archive; never imported raw into active memory (§70)".into(), MEMORY_STORE_BATCH, false, json!({"semantic_index": false, "lexical_index": false, "default_retrieval": false}), vec!["knowledge_extracted", "path_absent_at_source", "not_indexed"]),
            "GENERATED" if authority == "LEGACY" => ("DELETE_FROM_ACTIVE_TREE", None, "GENERATED", "stale derived index; rebuilt by gov rebuild-memory after path stabilisation (git history preserves it)".into(), MEMORY_STORE_BATCH, false, json!({"semantic_index": false, "lexical_index": false}), vec!["path_absent_at_source"]),
            "GENERATED" => ("KEEP_IN_PLACE", None, "GENERATED", "build output; excluded from index; should be gitignored".into(), 0, false, json!({"semantic_index": false, "lexical_index": false}), vec![]),
            "DECISION" | "LESSON" if is_record && !path.starts_with("spec/") => ("MOVE", Some(format!("spec/{}/{}", spec_subdir(class, &path, &low), name)), class, "governed record located outside spec/; relocated into the canonical spec tree (duplicate ids are surfaced by doctor)".into(), 2, false, json!({"semantic_index": true, "graph_index": true}), vec!["path_absent_at_source", "path_present_at_target"]),
            "DECISION" | "LESSON" if !path.starts_with("spec/") => ("EXTRACT", Some(format!("spec/{}/", spec_subdir(class, &path, &low))), if class == "DECISION" { "DECISION" } else { "LESSON" }, "legacy decision/lesson document: extract into governed PROVISIONAL records with provenance; original archived".into(), 2, secret, json!({"semantic_index": true, "graph_index": true}), vec!["records_created_with_provenance", "original_archived", "links_updated"]),
            "SPEC_AUTHORITATIVE" | "SPEC_DERIVED" | "RESEARCH_EVIDENCE" | "REPORT_EVIDENCE" | "TASK" if misplaced || (!path.starts_with("spec/") && class != "SPEC_DERIVED") => ("MOVE", Some(format!("spec/{}/{}", spec_subdir(class, &path, &low), name)), class, "spec/evidence material normalised into the canonical spec tree; links/citations updated".into(), 2, false, json!({"semantic_index": true, "graph_index": true}), vec!["path_absent_at_source", "path_present_at_target", "links_updated"]),
            "SPEC_AUTHORITATIVE" | "SPEC_DERIVED" | "RESEARCH_EVIDENCE" | "REPORT_EVIDENCE" | "TASK" | "DECISION" | "LESSON" => ("KEEP_IN_PLACE", None, class, "already in canonical location".into(), 0, false, json!({"semantic_index": true}), vec!["path_present"]),
            "PRODUCT_TEST" if misplaced => ("MOVE", Some(format!("{}/{}", product_test_dir.unwrap_or("tests"), name)), "PRODUCT_TEST", "test file relocated into the native test directory; imports updated".into(), 4, false, json!({"code_index": true}), vec!["path_present_at_target", "imports_resolve", "tests_run"]),
            "PRODUCT_TEST" => ("KEEP_IN_PLACE", None, "PRODUCT_TEST", "native test layout preserved (mapped via repository contract)".into(), 0, false, json!({"code_index": true}), vec!["tests_run"]),
            "PRODUCT_SOURCE" if misplaced => ("MOVE", Some(format!("product/{}", name)), "PRODUCT_SOURCE", "source located outside the product tree; relocated with imports rewritten (reversible: batch snapshot + independent tests; no human gate for a non-destructive move)".into(), 3, false, json!({"code_index": true}), vec!["path_present_at_target", "imports_resolve", "build_or_tests_run"]),
            "PRODUCT_SOURCE" | "TOOLING" | "DEVOPS" | "DATA_TEST" | "DATA_RUNTIME" => ("KEEP_IN_PLACE", None, class, "native product/devops/data layout preserved and described by the repository contract (§8.1, §79.3)".into(), 0, false, json!({"code_index": class == "PRODUCT_SOURCE"}), vec!["path_present"]),
            "DEAD_OR_UNUSED" => (dead_action, None, "DEAD_OR_UNUSED", format!("no references found; ARCHIVE_POLICY.unused_code_action={unused_code_action} — destructive, requires an answered Human Decision Gate (§71)"), GATED_BATCH, true, json!({"semantic_index": false}), vec!["human_gate_answered", "path_absent_at_source", "build_or_tests_run"]),
            _ => ("KEEP_IN_PLACE", None, "UNKNOWN", "unknown artefact: blocks destructive batches until classified (protocol §8)".into(), 0, false, json!({}), vec!["classified_before_destructive_batches"]),
        };
        let finding_state = if class == "UNKNOWN" {
            "UNKNOWN"
        } else {
            "PRESENT"
        };
        let mut gate_reasons: Vec<&str> = vec![];
        if gate {
            gate_reasons.push(if class == "DEAD_OR_UNUSED" {
                "destructive_cleanup"
            } else {
                "secret_material_move"
            });
        }
        let mut e = json!({"artifact_id": c["artifact_id"], "type": "migration-catalogue-entry", "current_path": path, "current_class": class, "authority": authority, "target_path": target, "target_class": target_class, "action": action, "reason": reason,
            "references": c.get("references").cloned().unwrap_or(json!([])), "imports": c.get("imports").cloned().unwrap_or(json!([])), "citations": c.get("citations").cloned().unwrap_or(json!([])),
            "path_references": c.get("path_references").cloned().unwrap_or(json!([])), "consumers": c.get("consumers").cloned().unwrap_or(json!([])), "cited_by": c.get("cited_by").cloned().unwrap_or(json!([])),
            "reference_edges": c.get("reference_edges").cloned().unwrap_or(json!([])),
            "index_policy": index_policy, "sensitivity": if secret { "secret" } else { "internal" },
            "rollback": "batch snapshot under .governance-runtime/migration/batch-<n>/ restored by `gov adopt rollback --batch <n>`; git history preserves deletions", "verification": verification, "batch": batch, "requires_human_gate": gate, "gate_reasons": gate_reasons, "confidence": c["confidence"], "finding_state": finding_state});
        if c["os_owned"].is_string() {
            e["os_owned"] = c["os_owned"].clone();
        }
        if gate && action == "EXTRACT" && !is_memory_store_extract(&e) && batch != GATED_BATCH {
            // knowledge is extracted in its own batch; only the retirement of the original waits for the gate
            e["extract_batch"] = json!(batch);
            e["batch"] = json!(GATED_BATCH);
        }
        out.push(e);
    }
    out
}

/// Paths whose references are not *active* dependencies: artefacts leaving the active tree (retirements that need no
/// gate, or whose gate has been answered A), and artefacts without authority (legacy, historical, superseded,
/// rejected) whose citations bind nothing. A gated retirement not yet authorised is *staying*: what it references
/// counts as active.
pub fn non_active_paths(
    catalogue: &[Value],
    archive_root: &str,
    answered: &[String],
) -> BTreeSet<String> {
    catalogue
        .iter()
        .filter(|e| {
            let aid = e["artifact_id"].as_str().unwrap_or("").to_string();
            let leaving = retirement_target(e, archive_root).is_some()
                && (!e["requires_human_gate"].as_bool().unwrap_or(false)
                    || answered.contains(&aid));
            leaving
                || matches!(
                    e["authority"].as_str().unwrap_or(""),
                    "LEGACY" | "HISTORICAL" | "SUPERSEDED" | "REJECTED"
                )
        })
        .filter_map(|e| e["current_path"].as_str().map(|s| s.to_string()))
        .collect()
}

/// Attach a dependency proof to every retirement entry. A retirement with active references (code, configuration or
/// docs) becomes a gated retirement: it runs only in [`GATED_BATCH`] after its Human Decision Gate is answered A, and
/// executing it never rewrites the references. An EXTRACT of a legacy document still extracts its knowledge in its
/// own batch (`extract_batch`); only the retirement of the original waits for the gate.
///
/// Gating an entry keeps it in the active tree for now, which can make its own references active; the proofs are
/// therefore recomputed until no further entry becomes gated (the set of leaving artefacts only shrinks).
pub fn apply_dependency_proofs(
    catalogue: &mut [Value],
    index: &ReferenceIndex,
    root: &Path,
    os: &OsState,
    archive_root: &str,
) {
    for _round in 0..64 {
        let active = ActiveSet {
            root,
            os,
            archive_root: archive_root.to_string(),
            leaving: non_active_paths(catalogue, archive_root, &[]),
        };
        let mut changed = false;
        for e in catalogue.iter_mut() {
            let Some(target) = retirement_target(e, archive_root) else {
                continue;
            };
            let path = e["current_path"].as_str().unwrap_or("").to_string();
            let proof = dependency_proof(index, &path, Some(target.as_str()), &active);
            let clean = proof_is_clean(&proof);
            e["dependency_proof"] = proof;
            let already = gate_reasons(e).iter().any(|r| r == "active_references");
            if !clean && !already {
                changed = true;
                add_gate_reason(e, "active_references");
                if e["action"] == "EXTRACT"
                    && !is_memory_store_extract(e)
                    && e["extract_batch"].is_null()
                {
                    e["extract_batch"] = e["batch"].clone();
                }
                if !is_memory_store_extract(e) {
                    e["batch"] = json!(GATED_BATCH);
                }
                let mut v: Vec<Value> = e["verification"].as_array().cloned().unwrap_or_default();
                for x in [
                    "dependency_proof_bound_to_answered_gate",
                    "active_references_not_rewritten",
                ] {
                    if !v.iter().any(|y| y == x) {
                        v.push(json!(x));
                    }
                }
                e["verification"] = json!(v);
            }
        }
        if !changed {
            break;
        }
    }
}

/// Fields that define an entry's content for identity/versioning (everything except bookkeeping, including the
/// `human_gate` id the OS assigns when it raises the entry's gate).
pub fn material(e: &Value) -> Value {
    let mut m = e.clone();
    if let Some(o) = m.as_object_mut() {
        for k in [
            "producer",
            "entry_hash",
            "entry_version",
            "supersedes",
            "human_gate",
            "lineage",
            "catalogue_version",
        ] {
            o.remove(k);
        }
        if let Some(p) = o
            .get_mut("dependency_proof")
            .and_then(|p| p.as_object_mut())
        {
            p.remove("computed_at");
            p.remove("scanned_files");
        }
    }
    m
}

fn gate_subject(e: &Value) -> Value {
    json!([
        e["current_path"],
        e["action"],
        e["target_path"],
        e["gate_reasons"],
        e["dependency_proof"]["dependants_digest"]
    ])
}

/// Digest of what a Human Decision Gate raised for catalogue entry `e` decides: the artefact's path, action, target,
/// gate reasons and the dependants its dependency proof found. The gate records it as `subject.sha256`, and an
/// answer is honoured for an entry only while the entry still asks exactly that question (BC-P2-11 for adoption).
pub fn gate_subject_sha256(e: &Value) -> String {
    identity::content_hash(&json!({"artifact_id": e["artifact_id"], "subject": gate_subject(e)}))
}

/// Digest of the catalogue **as reviewed**: every entry's material content (recomputed here, never read from a
/// stored `entry_hash`), keyed by artefact id and order-independent. The OS's own bookkeeping (entry versions,
/// producers, the gate id it assigns) is excluded, so executing the approved plan never changes it; any change to
/// what an entry says will happen to an artefact does (BC-P2-34: execution bound to the approved artefacts).
pub fn catalogue_digest(catalogue: &[Value]) -> String {
    let mut rows: Vec<(String, String)> = catalogue
        .iter()
        .map(|e| {
            (
                e["artifact_id"].as_str().unwrap_or("").to_string(),
                identity::content_hash(&material(e)),
            )
        })
        .collect();
    rows.sort();
    identity::content_hash(&json!(rows))
}

/// W1 identity for catalogue entries (BC-P2-21): type, content hash, version, producer, supersession lineage, lineage
/// to the ledger entry that moved the artefact here, and carry-over of a Human Decision Gate whose subject is unchanged.
///
/// `carry_gates`: a Human Decision Gate is carried to the re-generated entry only within the same adoption (A3 re-run
/// without a new A0) and only when its subject is unchanged; a new adoption pass asks its own questions.
pub fn finalise_identity(
    catalogue: &mut [Value],
    previous: &[Value],
    previous_version: u64,
    ledger: &[Value],
    producer: &Value,
    version: u64,
    carry_gates: bool,
) {
    for e in catalogue.iter_mut() {
        let aid = e["artifact_id"].as_str().unwrap_or("").to_string();
        let hash = identity::content_hash(&material(e));
        let prev = previous
            .iter()
            .find(|p| p["artifact_id"].as_str() == Some(aid.as_str()));
        match prev {
            Some(p)
                if p["entry_hash"].as_str() == Some(hash.as_str())
                    && p["entry_version"].is_u64() =>
            {
                e["entry_version"] = p["entry_version"].clone();
                e["supersedes"] = p.get("supersedes").cloned().unwrap_or(json!([]));
                e["producer"] = p.get("producer").cloned().unwrap_or(producer.clone());
            }
            Some(p) => {
                let pv = p["entry_version"].as_u64().unwrap_or(1);
                e["entry_version"] = json!(pv + 1);
                e["supersedes"] = json!([{"entry_hash": p["entry_hash"].clone(), "entry_version": pv, "catalogue_version": previous_version}]);
                e["producer"] = producer.clone();
            }
            None => {
                e["entry_version"] = json!(1);
                e["supersedes"] = json!([]);
                e["producer"] = producer.clone();
            }
        }
        e["entry_hash"] = json!(hash);
        e["catalogue_version"] = json!(version);
        if let Some(p) = prev.filter(|_| carry_gates) {
            if p["human_gate"]
                .as_str()
                .map(|g| !g.is_empty())
                .unwrap_or(false)
                && gate_subject(p) == gate_subject(e)
                && e["requires_human_gate"].as_bool().unwrap_or(false)
            {
                e["human_gate"] = p["human_gate"].clone();
            }
        }
        // An artefact that a migration put here is a new catalogue subject; its lineage names the ledger entry (and
        // the id the ledger recorded) so every ledger line stays resolvable to the artefact it recorded.
        let path = e["current_path"].as_str().unwrap_or("");
        if let Some(l) = ledger.iter().rev().find(|l| {
            l["status"] == "applied"
                && (l["result"]["to"].as_str() == Some(path)
                    || l["result"]["original_archived_to"].as_str() == Some(path))
        }) {
            e["lineage"] = json!({"migrated_from": {"artifact_id": l["artifact_id"], "path": l["path"], "action": l["action"], "batch": l["batch"], "at": l["at"]}});
        }
    }
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
        (
            7,
            "Gated retirements and destructive cleanup (human gate): dead/unused code, and retirements whose dependency proof found active references",
        ),
    ];
    defs.iter().map(|(n, d)| {
        let entries: Vec<&Value> = catalogue.iter().filter(|e| (e["batch"].as_i64() == Some(*n) || e["extract_batch"].as_i64() == Some(*n)) && e["action"] != "KEEP_IN_PLACE").collect();
        json!({"batch": n, "description": d, "entries": entries.len(), "actions": entries.iter().map(|e| e["artifact_id"].clone()).collect::<Vec<_>>(), "requires_human_gate": entries.iter().any(|e| e["requires_human_gate"].as_bool().unwrap_or(false) && e["batch"].as_i64() == Some(*n)), "rollback_point": format!("snapshot batch-{n}"), "pre_tests": ["independent path/link/import tests", "affected product tests"], "post_tests": ["independent path/link/import tests", "affected product tests", "checkpoint"]})
    }).collect()
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
    s.push_str("\n## Retirements and their dependency proofs\n\nEvery retirement is preceded by a proof over code, configuration and docs. A retirement with active references runs only after its Human Decision Gate is answered A; the references are reported and never re-pointed at archived material.\n\n| Artefact | Path | Proof | Active references |\n|---|---|---|---|\n");
    for e in catalogue
        .iter()
        .filter(|e| e["dependency_proof"].is_object())
    {
        let refs: Vec<String> = e["dependency_proof"]["active_references"]
            .as_array()
            .map(|a| {
                a.iter()
                    .map(|r| {
                        format!(
                            "{}:{} ({})",
                            r["from"].as_str().unwrap_or(""),
                            r["line"],
                            r["kind"].as_str().unwrap_or("")
                        )
                    })
                    .collect()
            })
            .unwrap_or_default();
        s.push_str(&format!(
            "| {} | {} | {} | {} |\n",
            e["artifact_id"].as_str().unwrap_or(""),
            e["current_path"].as_str().unwrap_or(""),
            e["dependency_proof"]["result"].as_str().unwrap_or(""),
            if refs.is_empty() {
                "-".to_string()
            } else {
                refs.join(", ")
            }
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
