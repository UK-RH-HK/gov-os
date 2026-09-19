//! A6 controlled migration: batch snapshot → actions → reference updates → checks → ledger; rollback on failure.
//!
//! **Rollback material is non-rebuildable operational state (BC-P2-31; Contract v3 B1:188, B3:202, D6:352).** A batch
//! snapshot is the only copy of what a batch replaced, so it lives in the OS store `migration-snapshots`
//! ([`crate::paths::OS_STORES`]): `.governance-state/migration/batch-<n>/` — machine-local, self-ignored by Git, never
//! walked, indexed or deleted by a rebuild — and not in the derived runtime directory, whose deletion (framework §19)
//! must not take a rollback with it. A snapshot an earlier version kept at `.governance-runtime/migration/` is moved
//! there once ([`crate::paths::relocate_legacy`]) before a batch runs or rolls back; while it cannot be moved it is
//! still read where it is, so a rollback stays available.
//!
//! **A rollback restores only what its batch could have changed.** The snapshot is content on disk, and content never
//! establishes what it may overwrite: a restore, a reversed move and a removal of created records are each confined
//! to the paths the batch recorded as touched or created, and never reach an OS-owned location (the installed kernel,
//! `framework.lock`, trust material, OS state, `.git`). Anything else in a snapshot is reported and left alone.
use super::{identity, planner, references};
use crate::records::{new_record, save_record};
use crate::util::{copy_dir, now_iso, read_json, read_text, write_json, write_text};
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

/// The OS store (BC-P2-31) that holds migration batch snapshots.
pub const SNAPSHOT_STORE: &str = "migration-snapshots";

/// Where batch snapshots are kept: the `migration-snapshots` store location (`.governance-state/migration`).
pub fn snapshots_root(root: &Path) -> PathBuf {
    crate::paths::store_path(root, SNAPSHOT_STORE)
        .unwrap_or_else(|| root.join(crate::paths::STATE_DIR).join("migration"))
}

/// The snapshot directory of batch `batch` where it belongs (`.governance-state/migration/batch-<n>`).
pub fn snapshot_dir(root: &Path, batch: i64) -> PathBuf {
    snapshots_root(root).join(format!("batch-{batch}"))
}

/// Where an earlier version kept batch snapshots (inside the derived runtime directory).
fn legacy_snapshot_dir(root: &Path, batch: i64) -> PathBuf {
    root.join(crate::RUNTIME_DIR)
        .join("migration")
        .join(format!("batch-{batch}"))
}

/// Prepare the snapshot store before a batch writes to it: move a legacy snapshot directory once (typed
/// `STATE_LOCATION_CONFLICT` if both places hold different material; nothing is overwritten) and make sure the state
/// directory ignores itself in Git.
fn prepare_store(root: &Path) -> Result<Vec<Value>> {
    let moved = crate::paths::relocate_legacy(root, SNAPSHOT_STORE)?;
    crate::paths::ensure_state_dir(root)?;
    Ok(moved)
}

/// The snapshot of `batch` to roll back from: where it belongs, after an attempt to move a legacy store there; a
/// legacy snapshot that could not be moved is read where it is, so the rollback stays available.
fn locate_snapshot(root: &Path, batch: i64) -> (PathBuf, Value) {
    let relocation = match prepare_store(root) {
        Ok(m) => json!({"moved": m}),
        Err(e) => json!({"error": {"code": e.code, "message": e.message}}),
    };
    let here = snapshot_dir(root, batch);
    let legacy = legacy_snapshot_dir(root, batch);
    if !here.join("batch.json").exists() && legacy.join("batch.json").exists() {
        return (legacy, relocation);
    }
    (here, relocation)
}

/// Repository-relative locations a migration batch never writes, so a rollback never restores, moves or removes
/// anything there, whatever a snapshot claims: the installed kernel, the lock, trust material, the OS's own state
/// and the VCS.
const PROTECTED_PREFIXES: &[&str] = &[
    ".git/",
    "governance/kernel/",
    "governance/trust/",
    ".governance-state/",
];
const PROTECTED_FILES: &[&str] = &["governance/framework.lock", ".git", ".governance-state"];

/// Whether a rollback may write `rel`: a plain repository-relative path (not absolute, no `..`, no backslash) outside
/// every protected location and outside the derived runtime directory.
fn rollback_may_write(rel: &str) -> bool {
    if rel.is_empty()
        || rel.starts_with('/')
        || rel.contains('\\')
        || rel.split('/').any(|c| c == "..")
    {
        return false;
    }
    let n = super::references::normalize_rel(rel);
    !(n.is_empty()
        || PROTECTED_FILES.contains(&n.as_str())
        || PROTECTED_PREFIXES.iter().any(|p| n.starts_with(p))
        || n == crate::RUNTIME_DIR
        || n.starts_with(&format!("{}/", crate::RUNTIME_DIR)))
}

/// Whether `rel` is one of `roots` or lies under one of them.
fn within(rel: &str, roots: &[String]) -> bool {
    roots
        .iter()
        .any(|r| rel == r || rel.starts_with(&format!("{}/", r.trim_end_matches('/'))))
}

fn git_mv(root: &Path, from: &str, to: &str) -> Result<()> {
    if let Some(d) = root.join(to).parent() {
        std::fs::create_dir_all(d)?;
    }
    let st = std::process::Command::new("git")
        .args(["mv", "-k", from, to])
        .current_dir(root)
        .output();
    if !(st.map(|o| o.status.success()).unwrap_or(false) && root.join(to).exists()) {
        std::fs::rename(root.join(from), root.join(to))?;
    }
    Ok(())
}

fn git_rm(root: &Path, path: &str) -> Result<()> {
    let st = std::process::Command::new("git")
        .args(["rm", "-q", "--cached", path])
        .current_dir(root)
        .output();
    let _ = st;
    let full = root.join(path);
    if full.is_file() {
        std::fs::remove_file(full)?;
    } else if full.is_dir() {
        std::fs::remove_dir_all(full)?;
    }
    Ok(())
}

/// Extract a legacy markdown decision/lesson document into governed PROVISIONAL records (one per H1/H2 section).
///
/// Record ids are derived from the source document and the section content ([`identity::extracted_doc_record_id`]),
/// so re-running a batch, or running the retirement phase in a later batch, reproduces the same records instead of
/// renumbering them. A section carrying secret material is withheld (counted, never copied into a record). Records
/// that already exist with identical content are not rewritten and not reported as created, so a later batch's
/// rollback never removes what an earlier batch extracted. The original is **not** moved here: its retirement is a
/// separate, dependency-proofed step.
fn extract_doc_records(
    root: &Path,
    entry: &Value,
    scanner: &crate::security::secrets::SecretScanner,
) -> Result<(Vec<String>, Vec<String>, usize)> {
    let path = entry["current_path"].as_str().unwrap_or("");
    let text = read_text(&root.join(path))?;
    let is_decision = entry["target_class"] == "DECISION";
    let target_dir = entry["target_path"]
        .as_str()
        .unwrap_or(if is_decision {
            "spec/decisions/"
        } else {
            "spec/lessons/"
        })
        .to_string();
    let mut created = vec![];
    let mut all = vec![];
    let mut withheld = 0usize;
    // split on H2/H1 headings; each heading becomes a record; fallback = whole document
    let rx = regex::Regex::new(r"(?m)^#{1,2}\s+(.+)$").unwrap();
    let mut sections: Vec<(String, String)> = vec![];
    let mut last_title = Path::new(path)
        .file_stem()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or("legacy".into());
    let mut pos = 0;
    for m in rx.captures_iter(&text) {
        let whole = m.get(0).unwrap();
        let body = text[pos..whole.start()].trim().to_string();
        if !body.is_empty() {
            sections.push((last_title.clone(), body));
        }
        last_title = m[1].trim().to_string();
        pos = whole.end();
    }
    let tail = text[pos..].trim().to_string();
    if !tail.is_empty() {
        sections.push((last_title, tail));
    }
    if sections.is_empty() {
        sections.push((
            Path::new(path)
                .file_stem()
                .map(|s| s.to_string_lossy().to_string())
                .unwrap_or("legacy".into()),
            text.clone(),
        ));
    }
    for (title, body) in sections {
        if body.len() < 20 {
            continue;
        }
        if !scanner.scan_text(&body, path).is_empty() || !scanner.scan_text(&title, path).is_empty()
        {
            withheld += 1;
            continue;
        }
        let low = body.to_lowercase();
        let superseded =
            low.contains("superseded") || low.contains("deprecated") || low.contains("obsolete");
        let (rtype, prefix) = if is_decision {
            ("decision", "D")
        } else {
            ("lesson", "L")
        };
        let id = identity::extracted_doc_record_id(prefix, path, &title, &body);
        let mut fields = json!({"status": if superseded { "SUPERSEDED" } else { "PROVISIONAL" }, "state_class": if superseded { "HISTORICAL" } else { "AUTHORITATIVE" }, "legacy_source": path, "provenance": {"extracted_from": path, "method": "adopt extract (heading split)", "authority_note": "LEGACY material: PROVISIONAL until confirmed by decision (INV-004)"}, "body": body, "tags": ["legacy-extraction"]});
        if is_decision {
            fields["question"] = json!(title);
            fields["rationale"] = json!(body.chars().take(500).collect::<String>());
            fields["human_approved"] = json!(false);
            fields["chosen_option"] = json!("as-recorded-in-legacy");
        } else {
            fields["scope"] = json!("PROJECT");
            fields["lifecycle"] = json!("candidate");
            fields["problem_statement"] = json!(title);
            fields["evidence_strength"] = json!("low");
        }
        let mut rec = new_record(rtype, &id, &title, fields);
        rec.path = format!(
            "{}{}.yaml",
            target_dir.trim_end_matches('/').to_string() + "/",
            id
        );
        all.push(rec.path.clone());
        if root.join(&rec.path).exists() {
            continue;
        }
        save_record(root, &rec)?;
        created.push(rec.path.clone());
    }
    Ok((created, all, withheld))
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct BatchResult {
    pub batch: i64,
    pub applied: Vec<Value>,
    pub moves: Vec<(String, String)>,
    pub references_updated: Vec<String>,
    pub created: Vec<String>,
    pub snapshot: String,
    pub skipped: Vec<Value>,
    /// retirements refused because a fresh dependency proof found active references no answered gate covers
    pub blocked: Vec<Value>,
    /// retirements executed under an answered gate while active references existed (references left as they were)
    pub retired_with_active_references: Vec<Value>,
    /// legacy snapshot material moved into the `migration-snapshots` store before this batch (BC-P2-31)
    pub snapshot_relocated: Vec<Value>,
}

/// What one batch run binds its ledger lines to, and how it proves and extracts.
pub struct BatchContext {
    pub archive_root: String,
    pub catalogue_version: Value,
    pub plan_version: Value,
    pub scanner: crate::security::secrets::SecretScanner,
}

/// Dependants (file, kind) of a proof.
fn dependants(proof: &Value) -> std::collections::BTreeSet<(String, String)> {
    proof["active_references"]
        .as_array()
        .map(|a| {
            a.iter()
                .map(|r| {
                    (
                        r["from"].as_str().unwrap_or("").to_string(),
                        r["kind"].as_str().unwrap_or("").to_string(),
                    )
                })
                .collect()
        })
        .unwrap_or_default()
}

/// A fresh proof is covered by the proof a gate was raised with when it names no dependant the gate did not show.
pub fn proof_covered_by(fresh: &Value, planned: &Value) -> bool {
    dependants(fresh).is_subset(&dependants(planned))
}

/// Execute one batch of the catalogue. `gate_answers` lists artefact ids whose human gate has been answered YES.
///
/// Every retirement re-proves, from a fresh scan of the working tree, that no active code, configuration or document
/// depends on the artefact. With active references the retirement proceeds only under an answered gate raised for
/// exactly those dependants, and never rewrites them: references are re-pointed only for moves whose target stays in
/// the active tree (BC-P2-33: migration never rewrites active references into archived legacy material).
pub fn apply_batch(
    root: &Path,
    catalogue: &[Value],
    batch: i64,
    gate_answers: &[String],
    ledger: &Path,
    ctx: &BatchContext,
) -> Result<BatchResult> {
    let entries: Vec<&Value> = catalogue
        .iter()
        .filter(|e| {
            e["action"] != "KEEP_IN_PLACE"
                && (e["batch"].as_i64() == Some(batch)
                    || e["extract_batch"].as_i64() == Some(batch))
        })
        .collect();
    // BC-P2-31: rollback material lives in its OS store, moved there once from the derived runtime directory
    let relocated = prepare_store(root)?;
    let snap = snapshot_dir(root, batch);
    crate::util::remove_dir_if_exists(&snap)?;
    std::fs::create_dir_all(&snap)?;
    let mut touched: Vec<String> = vec![];
    for e in &entries {
        for k in ["current_path", "target_path"] {
            if let Some(p) = e[k].as_str() {
                if !p.is_empty() && root.join(p).exists() && !touched.contains(&p.to_string()) {
                    touched.push(p.to_string());
                }
            }
        }
    }
    for t in &touched {
        let src = root.join(t);
        if src.is_file() {
            let dst = snap.join("files").join(t);
            if let Some(d) = dst.parent() {
                std::fs::create_dir_all(d)?;
            }
            std::fs::copy(&src, &dst)?;
        } else if src.is_dir() {
            copy_dir(&src, &snap.join("files").join(t))?;
        }
    }
    let mut result = BatchResult {
        batch,
        applied: vec![],
        moves: vec![],
        references_updated: vec![],
        created: vec![],
        snapshot: snap.to_string_lossy().to_string(),
        skipped: vec![],
        blocked: vec![],
        retired_with_active_references: vec![],
        snapshot_relocated: relocated,
    };
    let ar = ctx.archive_root.trim_end_matches('/').to_string();
    // One fresh scan per batch, taken before any retirement of this batch relies on it.
    let needs_proof = entries.iter().any(|e| {
        e["batch"].as_i64() == Some(batch) && planner::retirement_target(e, &ar).is_some()
    });
    let index = if needs_proof {
        references::build_fresh(root)
    } else {
        references::ReferenceIndex::default()
    };
    let os = super::ownership::OsState::load(root);
    let active = references::ActiveSet {
        root,
        os: &os,
        archive_root: ar.clone(),
        leaving: planner::non_active_paths(catalogue, &ar, gate_answers),
    };
    let mut ledger_lines = vec![];
    let row = |e: &Value, status: &str, extra: Value| -> Value {
        let mut r = json!({"at": now_iso(), "batch": batch, "artifact_id": e["artifact_id"], "action": e["action"], "path": e["current_path"], "status": status,
            "entry_hash": e["entry_hash"], "catalogue_version": ctx.catalogue_version, "plan_version": ctx.plan_version});
        if let (Some(o), Some(x)) = (r.as_object_mut(), extra.as_object()) {
            for (k, v) in x {
                o.insert(k.clone(), v.clone());
            }
        }
        r
    };
    for e in entries {
        let action = e["action"].as_str().unwrap_or("");
        let from = e["current_path"].as_str().unwrap_or("").to_string();
        let aid = e["artifact_id"].as_str().unwrap_or("").to_string();
        // phase 1 of a gated EXTRACT: knowledge is extracted now; the original is retired only in its gated batch
        if action == "EXTRACT"
            && e["extract_batch"].as_i64() == Some(batch)
            && e["batch"].as_i64() != Some(batch)
        {
            if !root.join(&from).exists() {
                result.skipped.push(json!({"artifact_id": aid, "path": from, "reason": "NOT_FOUND at execution time (not proof of absence)"}));
                continue;
            }
            match extract_doc_records(root, e, &ctx.scanner) {
                Ok((c, all, withheld)) => {
                    result.created.extend(c.clone());
                    let v = json!({"created": c, "records": all, "withheld_secret_sections": withheld, "original_retained": true, "retirement": format!("gated: the original is retired in batch {} only after its Human Decision Gate is answered A", e["batch"])});
                    result.applied.push(
                        json!({"artifact_id": aid, "action": "EXTRACT", "path": from, "result": v}),
                    );
                    ledger_lines.push(row(e, "applied", json!({"phase": "extract", "result": v})));
                }
                Err(err) => {
                    ledger_lines.push(row(
                        e,
                        "failed",
                        json!({"phase": "extract", "error": err.to_string()}),
                    ));
                    append_ledger(ledger, &ledger_lines)?;
                    rollback_batch(root, batch)?;
                    return Err(GovError::new(
                        "MIGRATION_BATCH_FAILED",
                        format!("batch {batch} failed at {aid} ({err}); batch rolled back"),
                    ));
                }
            }
            continue;
        }
        let answered = gate_answers.contains(&aid);
        if e["requires_human_gate"].as_bool().unwrap_or(false) && !answered {
            result.skipped.push(json!({"artifact_id": aid, "path": from, "reason": "requires an answered human gate"}));
            ledger_lines.push(row(
                e,
                "skipped",
                json!({"reason": "requires an answered human gate"}),
            ));
            continue;
        }
        if action == "EXTRACT"
            && e["target_path"]
                .as_str()
                .map(|t| t.contains("memory-stores"))
                .unwrap_or(false)
        {
            result.skipped.push(json!({"artifact_id": aid, "path": from, "reason": "legacy memory store: extraction and retirement happen in A8 after migration acceptance (protocol §13)"}));
            continue;
        }
        if !root.join(&from).exists() {
            result.skipped.push(json!({"artifact_id": aid, "path": from, "reason": "NOT_FOUND at execution time (not proof of absence)"}));
            continue;
        }
        let mut dangling: Option<Value> = None;
        let mut proof_summary = Value::Null;
        if let Some(target) = planner::retirement_target(e, &ar) {
            let proof = references::dependency_proof(&index, &from, Some(target.as_str()), &active);
            proof_summary = json!({"result": proof["result"], "dependants_digest": proof["dependants_digest"], "active_references": proof["active_references"], "scanned_files": proof["scanned_files"]});
            if !references::proof_is_clean(&proof) {
                let gated_for_refs = e["gate_reasons"]
                    .as_array()
                    .map(|a| a.iter().any(|r| r == "active_references"))
                    .unwrap_or(false);
                let covered = proof_covered_by(&proof, &e["dependency_proof"]);
                if !(answered && gated_for_refs && covered) {
                    let why = if !gated_for_refs || !answered {
                        "no answered Human Decision Gate authorises retiring it while they exist (re-run `gov adopt map` and `gov adopt plan` to raise one)"
                    } else {
                        "the gate was answered for a different set of dependants; re-plan so the gate shows the current ones"
                    };
                    let b = json!({"artifact_id": aid, "path": from, "reason": format!("RETIREMENT_BLOCKED_ACTIVE_REFERENCES: a fresh dependency proof found active references and {why}"), "dependency_proof": proof});
                    result.blocked.push(b.clone());
                    result.skipped.push(b);
                    ledger_lines.push(row(
                        e,
                        "blocked",
                        json!({"dependency_proof": proof_summary}),
                    ));
                    continue;
                }
                dangling = Some(proof["active_references"].clone());
            }
        }
        let scanner = &ctx.scanner;
        let outcome: Result<Value> = (|| match action {
            "MOVE" | "RENAME" => {
                let to = e["target_path"].as_str().unwrap_or("").to_string();
                if to.is_empty() {
                    return Err(GovError::new(
                        "PLAN_INVALID",
                        format!("{aid}: MOVE without target"),
                    ));
                }
                git_mv(root, &from, &to)?;
                result.moves.push((from.clone(), to.clone()));
                Ok(json!({"to": to}))
            }
            "EXTRACT" => {
                if e["target_class"] == "DECISION" || e["target_class"] == "LESSON" {
                    let (c, all, withheld) = extract_doc_records(root, e, scanner)?;
                    result.created.extend(c.clone());
                    let archived = planner::legacy_doc_archive_path(&from);
                    git_mv(root, &from, &archived)?;
                    result.moves.push((from.clone(), archived.clone()));
                    Ok(
                        json!({"created": c, "records": all, "withheld_secret_sections": withheld, "original_archived_to": archived}),
                    )
                } else {
                    let to = e["target_path"].as_str().unwrap_or("").to_string();
                    git_mv(root, &from, &to)?;
                    result.moves.push((from.clone(), to.clone()));
                    Ok(
                        json!({"to": to, "note": "store retired to archive after extraction (see 09 report)"}),
                    )
                }
            }
            "RETIRE" => {
                let to = planner::retired_code_archive_path(&from);
                git_mv(root, &from, &to)?;
                result.moves.push((from.clone(), to.clone()));
                Ok(json!({"to": to}))
            }
            "DELETE_FROM_ACTIVE_TREE" => {
                git_rm(root, &from)?;
                Ok(json!({"deleted": true}))
            }
            "SPLIT" | "MERGE" => Err(GovError::new(
                "PLAN_UNSUPPORTED",
                format!("{aid}: {action} requires a manual CIT"),
            )),
            other => Err(GovError::new(
                "PLAN_INVALID",
                format!("{aid}: unknown action {other}"),
            )),
        })();
        match outcome {
            Ok(mut v) => {
                if let Some(d) = &dangling {
                    v["retired_with_active_references"] = d.clone();
                    v["authorised_by_gate"] = e["human_gate"].clone();
                    result.retired_with_active_references.push(json!({"artifact_id": aid, "path": from, "gate": e["human_gate"], "active_references": d}));
                }
                result
                    .applied
                    .push(json!({"artifact_id": aid, "action": action, "path": from, "result": v}));
                ledger_lines.push(row(
                    e,
                    "applied",
                    json!({"result": v, "dependency_proof": proof_summary}),
                ));
            }
            Err(err) => {
                ledger_lines.push(row(e, "failed", json!({"error": err.to_string()})));
                append_ledger(ledger, &ledger_lines)?;
                rollback_batch(root, batch)?;
                return Err(GovError::new(
                    "MIGRATION_BATCH_FAILED",
                    format!("batch {batch} failed at {aid} ({err}); batch rolled back"),
                ));
            }
        }
    }
    // References are re-pointed only for moves whose target stays in the active tree. For a retirement (target in the
    // archive) only links inside the archived file itself and references from other archived material are
    // re-relativised: an active reference is never re-pointed at archived legacy material.
    let archive_prefix = format!("{ar}/");
    let (retire_moves, active_moves): (Vec<(String, String)>, Vec<(String, String)>) = result
        .moves
        .iter()
        .cloned()
        .partition(|(_, to)| to.starts_with(&archive_prefix));
    let mut updated = super::refs::update_references_in(root, &active_moves, true, &[], &|_| true)?;
    for f in super::refs::update_references_in(root, &retire_moves, true, &[], &|rel: &str| {
        rel.starts_with(&archive_prefix)
    })? {
        if !updated.contains(&f) {
            updated.push(f);
        }
    }
    result.references_updated = updated;
    write_json(
        &snap.join("batch.json"),
        &json!({"batch": batch, "touched": touched, "moves": result.moves, "retirement_moves": retire_moves, "created": result.created, "references_updated": result.references_updated, "snapshot_relocated": result.snapshot_relocated, "at": now_iso()}),
    )?;
    ledger_lines.push(json!({"at": now_iso(), "batch": batch, "status": "batch_complete", "applied": result.applied.len(), "blocked": result.blocked.len(), "references_updated": result.references_updated.len(), "catalogue_version": ctx.catalogue_version, "plan_version": ctx.plan_version}));
    append_ledger(ledger, &ledger_lines)?;
    Ok(result)
}

fn append_ledger(ledger: &Path, lines: &[Value]) -> Result<()> {
    if let Some(d) = ledger.parent() {
        std::fs::create_dir_all(d)?;
    }
    let mut text = if ledger.exists() {
        read_text(ledger)?
    } else {
        String::new()
    };
    for l in lines {
        text.push_str(&serde_json::to_string(l)?);
        text.push('\n');
    }
    write_text(ledger, &text)
}

/// Restore a batch from its snapshot: reverse moves, remove created files, restore originals.
///
/// The snapshot is read from the `migration-snapshots` store (a legacy snapshot is moved there first, or read where
/// it is if it cannot be). Every write is confined to what the batch recorded — a reversed move must start from a
/// path the batch snapshotted, a restored file must lie under one, a removed file must be one the batch created — and
/// never reaches a protected location ([`rollback_may_write`]); whatever else the snapshot names is reported under
/// `refused` and left alone.
pub fn rollback_batch(root: &Path, batch: i64) -> Result<Value> {
    let (snap, relocation) = locate_snapshot(root, batch);
    let meta = read_json(&snap.join("batch.json"))
        .unwrap_or(json!({"moves": [], "created": [], "touched": []}));
    let touched: Vec<String> = meta["touched"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    let mut restored = vec![];
    let mut removed = vec![];
    let mut refused: Vec<Value> = vec![];
    let mut reversed: Vec<(String, String)> = vec![];
    for m in meta["moves"].as_array().cloned().unwrap_or_default() {
        let (from, to) = (m[0].as_str().unwrap_or(""), m[1].as_str().unwrap_or(""));
        if !(rollback_may_write(from) && rollback_may_write(to) && within(from, &touched)) {
            refused.push(json!({"kind": "move", "from": to, "to": from, "reason": "not a move of a path this batch snapshotted, or it reaches a protected location"}));
            continue;
        }
        if root.join(to).exists() && !root.join(from).exists() {
            git_mv(root, to, from)?;
            restored.push(from.to_string());
        }
        reversed.push((to.to_string(), from.to_string()));
    }
    for c in meta["created"].as_array().cloned().unwrap_or_default() {
        let p = c.as_str().unwrap_or("");
        if !rollback_may_write(p) {
            refused.push(json!({"kind": "remove", "path": p, "reason": "protected location"}));
            continue;
        }
        if root.join(p).exists() && !touched.iter().any(|t| t == p) {
            let _ = git_rm(root, p);
            removed.push(p.to_string());
        }
    }
    let files = snap.join("files");
    if files.exists() {
        for entry in walkdir::WalkDir::new(&files)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_type().is_file())
        {
            let rel = entry
                .path()
                .strip_prefix(&files)
                .unwrap()
                .to_string_lossy()
                .replace('\\', "/");
            if !(rollback_may_write(&rel) && within(&rel, &touched)) {
                refused.push(json!({"kind": "restore", "path": rel, "reason": "not under a path this batch snapshotted, or a protected location"}));
                continue;
            }
            let dst = root.join(&rel);
            if let Some(d) = dst.parent() {
                std::fs::create_dir_all(d)?;
            }
            std::fs::copy(entry.path(), &dst)?;
            if !restored.contains(&rel) {
                restored.push(rel);
            }
        }
    }
    // references: re-run reverse replacement for the moves reversed
    let refs = super::refs::update_references_opts(root, &reversed, false, &restored)?;
    Ok(
        json!({"batch": batch, "restored": restored, "removed": removed, "references_reverted": refs, "refused": refused,
               "snapshot": snap.to_string_lossy(), "snapshot_store": relocation}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    fn project(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("gov-exec-{tag}-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    fn ctx() -> BatchContext {
        BatchContext {
            archive_root: "archive".into(),
            catalogue_version: json!(1),
            plan_version: json!(1),
            scanner: crate::security::secrets::SecretScanner::default_scanner(),
        }
    }

    /// BC-P2-31 (WS-6 IP-R2-10): a batch snapshot is written to the `migration-snapshots` OS store, whose directory
    /// ignores itself in Git, and survives deleting the whole derived runtime directory — the rollback still restores.
    #[test]
    fn batch_snapshots_live_in_the_os_store_and_survive_deleting_the_runtime_directory() {
        let root = project("store");
        write_text(&root.join("notes/api.md"), "# API\n\nthe api\n").unwrap();
        std::fs::create_dir_all(root.join(crate::RUNTIME_DIR)).unwrap();
        write_text(&root.join(crate::RUNTIME_DIR).join("state.db"), "derived").unwrap();
        let cat = vec![
            json!({"artifact_id": "ART-1", "current_path": "notes/api.md", "target_path": "spec/api.md", "action": "MOVE", "batch": 1}),
        ];
        let ledger = root.join("ledger.jsonl");
        let r = apply_batch(&root, &cat, 1, &[], &ledger, &ctx()).unwrap();
        assert_eq!(
            PathBuf::from(&r.snapshot),
            root.join(".governance-state/migration/batch-1")
        );
        assert!(root
            .join(".governance-state/migration/batch-1/batch.json")
            .exists());
        assert!(root.join(".governance-state/.gitignore").exists());
        assert!(root.join("spec/api.md").exists() && !root.join("notes/api.md").exists());
        // the product never classifies the snapshot derived, and deleting what it does classify keeps it
        let contract = crate::paths::RepositoryContract::load(
            &Path::new(env!("CARGO_MANIFEST_DIR"))
                .join("../framework/overlay-templates/REPOSITORY_CONTRACT.yaml"),
        )
        .unwrap();
        let rel = ".governance-state/migration/batch-1/batch.json";
        assert_eq!(
            contract.decide(rel).class(),
            crate::paths::OPERATIONAL_CLASS
        );
        std::fs::remove_dir_all(root.join(crate::RUNTIME_DIR)).unwrap();
        let rb = rollback_batch(&root, 1).unwrap();
        assert!(
            root.join("notes/api.md").exists() && !root.join("spec/api.md").exists(),
            "{rb}"
        );
        assert_eq!(rb["refused"], json!([]));
        let _ = std::fs::remove_dir_all(&root);
    }

    /// A snapshot an earlier version kept in the derived runtime directory is moved into the store once, and the
    /// rollback it holds still works.
    #[test]
    fn a_legacy_snapshot_is_moved_into_the_store_and_still_rolls_back() {
        let root = project("legacy");
        let legacy = root.join(".governance-runtime/migration/batch-2");
        write_text(
            &legacy.join("files/lib/util.py"),
            "def f():\n    return 1\n",
        )
        .unwrap();
        write_json(
            &legacy.join("batch.json"),
            &json!({"batch": 2, "touched": ["lib/util.py"], "moves": [], "created": []}),
        )
        .unwrap();
        let rb = rollback_batch(&root, 2).unwrap();
        assert_eq!(
            read_text(&root.join("lib/util.py")).unwrap(),
            "def f():\n    return 1\n"
        );
        assert!(!root.join(".governance-runtime/migration").exists());
        assert!(root
            .join(".governance-state/migration/batch-2/batch.json")
            .exists());
        assert_eq!(rb["snapshot_store"]["moved"][0]["action"], "moved", "{rb}");
        let _ = std::fs::remove_dir_all(&root);
    }

    /// A rollback writes only what its batch recorded, and never an OS-owned location, whatever the snapshot on disk
    /// says (a snapshot is content, not authority): a planted kernel file, lock, trust file, an unrecorded file, a
    /// move of the kernel and the removal of the lock are refused and reported; the recorded file is restored.
    #[test]
    fn a_rollback_restores_only_what_its_batch_recorded() {
        let root = project("confine");
        write_text(
            &root.join("governance/kernel/KERNEL.yaml"),
            "version: 9.9.9\n",
        )
        .unwrap();
        write_text(&root.join("governance/framework.lock"), "lock: installed\n").unwrap();
        let snap = snapshot_dir(&root, 3);
        for (rel, text) in [
            ("product/app.py", "print('original')\n"),
            ("governance/kernel/KERNEL.yaml", "version: 0.0.1\n"),
            ("governance/framework.lock", "lock: planted\n"),
            ("governance/trust/root.json", "{}\n"),
            ("notes/unrecorded.md", "planted\n"),
        ] {
            write_text(&snap.join("files").join(rel), text).unwrap();
        }
        write_json(
            &snap.join("batch.json"),
            &json!({"batch": 3, "touched": ["product/app.py", "governance/kernel", "../outside"],
                "moves": [["governance/kernel/KERNEL.yaml", "archive/K.yaml"], ["/etc/hosts", "archive/hosts"]],
                "created": ["governance/framework.lock"]}),
        )
        .unwrap();
        let rb = rollback_batch(&root, 3).unwrap();
        assert_eq!(
            read_text(&root.join("product/app.py")).unwrap(),
            "print('original')\n"
        );
        assert_eq!(
            read_text(&root.join("governance/kernel/KERNEL.yaml")).unwrap(),
            "version: 9.9.9\n"
        );
        assert_eq!(
            read_text(&root.join("governance/framework.lock")).unwrap(),
            "lock: installed\n"
        );
        assert!(
            !root.join("governance/trust").exists() && !root.join("notes/unrecorded.md").exists()
        );
        let refused = rb["refused"].as_array().unwrap();
        assert_eq!(refused.len(), 7, "{rb}");
        assert_eq!(rb["restored"], json!(["product/app.py"]));
        let _ = std::fs::remove_dir_all(&root);
    }
}
