//! **Stable artefact identity** (Contract v3 W1, lines 1068-1080; BC-P2-21 records side).
//!
//! Every governed output that may feed downstream work is answered here with the nine W1 attributes, computed
//! from the governed record and version control — never from the derived index, so identity survives an index
//! loss (INV-010):
//!
//! | W1 attribute | source |
//! |---|---|
//! | stable artefact ID | the record's `id` (survives moves; the index re-keys by id on relocation) |
//! | artefact type | `type` |
//! | canonical path | `records::record_dir_for(type)` (+ `CHECKPOINT_POLICY.location` for checkpoints); a record outside it is reported by [`misplaced_records`] |
//! | authoritative status | the effective `state_class` (`AUTHORITY_POLICY.default_state_class_by_type`) |
//! | lifecycle state | `status` |
//! | version / content hash | declared `version` (if any) + SHA-256 of the record's bytes |
//! | producer / provenance | declared provenance fields + the commit that introduced the file and the commit that last changed it |
//! | supersedes / superseded-by | declared `supersedes` + successor derived from every record (`graph::lineage::successor_map`) |
//! | expected downstream consumers | declared `consumers` + actual consumers (`graph::lineage::consumers_of`) |
//!
//! [`stable_content_id`] is the identity scheme for outputs that have no authored id (audit findings, adoption
//! catalogue entries): an id derived from the output's natural key, so re-running the producer yields the same id
//! for the same finding/artefact and a different one for a different finding (integration points for WS-2's audit
//! finding ids and WS-9's catalogue ids).
use crate::records::{record_dir_for, state_class_for, Record, RecordStore};
use crate::util::sha256_hex;
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

/// Declared provenance fields a governed record may carry (the product writes several of them itself:
/// `session`/`role` on reports and checkpoints, `approved_by`/`derived_from` on gate-minted decisions,
/// `provenance` on worker-return lessons, `generated_by` on generated tasks).
pub const PROVENANCE_FIELDS: &[&str] = &[
    "provenance",
    "producer",
    "produced_by",
    "created_by",
    "generated_by",
    "approved_by",
    "approved_by_role",
    "author",
    "author_role",
    "session",
    "role",
    "sources",
    "derived_from",
];

/// Roots whose records are not held to a type's canonical directory: archived records (by definition relocated)
/// and the project overlay (governance/project/, configuration records owned by the overlay).
pub const NON_CANONICAL_ROOTS: &[&str] = &["archive/", "governance/project/"];

/// The canonical directory for a record type in this project, or `None` for a type with no canonical location.
pub fn canonical_dir(p: Option<&Project>, rtype: &str) -> Option<String> {
    if rtype == "checkpoint" {
        if let Some(p) = p {
            return Some(p.policies().get_str(
                "CHECKPOINT_POLICY",
                "location",
                "spec/reports/checkpoints",
            ));
        }
    }
    record_dir_for(rtype).ok().map(|d| d.to_string())
}

/// The canonical directory of one governed record. As [`canonical_dir`], except where a type's canonical location
/// depends on the record: a `failure` record of kind `retrieval-miss` is a memory-quality event, whose canonical
/// location is `spec/reports/memory-quality/` (never indexed; `memory::failures`), not the failures directory.
pub fn canonical_dir_of(p: Option<&Project>, r: &Record) -> Option<String> {
    let t = r.rtype();
    if t == crate::memory::failures::RECORD_TYPE && r.get("failure_kind") == "retrieval-miss" {
        return Some(crate::memory::failures::MEMORY_QUALITY_DIR.to_string());
    }
    canonical_dir(p, &t)
}

/// Is the record `r` stored in its canonical location? `None` when its type has none.
pub fn record_in_canonical_location(p: Option<&Project>, r: &Record) -> Option<bool> {
    if NON_CANONICAL_ROOTS
        .iter()
        .any(|root| r.path.starts_with(root))
    {
        return Some(true);
    }
    canonical_dir_of(p, r).map(|d| within(&r.path, &d))
}

/// Is `path` inside `dir` (the directory itself or any subdirectory of it)?
fn within(path: &str, dir: &str) -> bool {
    let d = dir.trim_end_matches('/');
    path.starts_with(&format!("{d}/"))
}

/// Is a record of type `rtype` stored at `path` in its canonical location? `None` when the type has none.
pub fn in_canonical_location(p: Option<&Project>, rtype: &str, path: &str) -> Option<bool> {
    if NON_CANONICAL_ROOTS
        .iter()
        .any(|root| path.starts_with(root))
    {
        return Some(true);
    }
    canonical_dir(p, rtype).map(|d| within(path, &d))
}

/// **Records outside their type's canonical location** (W1 line 1072 "canonical path"): a record whose `type` has
/// a canonical directory and that is stored elsewhere. Subdirectories of the canonical directory are canonical
/// (a record moved within its type's tree keeps its identity).
pub fn misplaced_records(p: Option<&Project>, store: &RecordStore) -> Vec<Value> {
    let mut out = vec![];
    for r in &store.records {
        let id = r.id();
        let t = r.rtype();
        if id.is_empty() || t.is_empty() {
            continue;
        }
        if NON_CANONICAL_ROOTS
            .iter()
            .any(|root| r.path.starts_with(root))
        {
            continue;
        }
        let Some(dir) = canonical_dir_of(p, r) else {
            continue;
        };
        if !within(&r.path, &dir) {
            out.push(json!({"id": id, "type": t, "path": r.path, "canonical_dir": dir,
                "message": format!("{id} ({t}) is stored at {} outside its canonical location {dir}/", r.path)}));
        }
    }
    out
}

/// A stable id derived from an output's natural key: `PREFIX-<first 12 hex of sha256(parts joined by U+001F)>`.
/// The same key always yields the same id; a different key a different id — independent of how many other
/// outputs precede it (the positional `GF-nnnn` / `ART-nnnnn` defect, A0-W1-01 / S0-W1-01).
pub fn stable_content_id(prefix: &str, parts: &[&str]) -> String {
    let key = parts.join("\u{1f}");
    format!("{prefix}-{}", &sha256_hex(key.as_bytes())[..12])
}

/// SHA-256 of a record's bytes as stored (the same hash the index manifest records as `content_hash`).
pub fn content_hash(root: &std::path::Path, rec: &Record) -> Option<String> {
    crate::util::read_bytes(&root.join(&rec.path))
        .ok()
        .map(|b| sha256_hex(&b))
}

/// Version-control provenance of a path: the commit that introduced it and the commit that last changed it.
pub fn git_provenance(p: &Project, path: &str) -> Value {
    let fmt = "--format=%H%x1f%an%x1f%aI";
    let parse = |s: &str| -> Value {
        let mut it = s.split('\u{1f}');
        match (it.next(), it.next(), it.next()) {
            (Some(c), Some(a), Some(t)) if !c.is_empty() => {
                json!({"commit": c, "author": a, "at": t})
            }
            _ => Value::Null,
        }
    };
    let (c1, created, _) = p.git(&["log", "--diff-filter=A", "--follow", fmt, "--", path]);
    let (c2, last, _) = p.git(&["log", "-1", fmt, "--", path]);
    let (_, dirty, _) = p.git(&["status", "--porcelain", "--", path]);
    if c1 != 0 && c2 != 0 {
        return json!({"available": false});
    }
    json!({
        "available": true,
        "introduced_by": created.lines().last().map(parse).unwrap_or(Value::Null),
        "last_changed_by": last.lines().next().map(parse).unwrap_or(Value::Null),
        "uncommitted_changes": !dirty.trim().is_empty(),
    })
}

/// The nine W1 attributes of the governed artefact `id`.
pub fn identity(p: &Project, store: &RecordStore, id: &str) -> Result<Value> {
    let r = store.get(id).ok_or_else(|| {
        GovError::new(
            "ARTEFACT_NOT_FOUND",
            format!("no governed record with id {id}; run `gov artefact check` to list identity problems"),
        )
    })?;
    let t = r.rtype();
    let authority = p
        .policies()
        .effective
        .get("AUTHORITY_POLICY")
        .cloned()
        .unwrap_or(json!({}));
    let dir = canonical_dir_of(Some(p), r);
    let succ = super::lineage::successor_map(store);
    let declared_prov: serde_json::Map<String, Value> = PROVENANCE_FIELDS
        .iter()
        .filter_map(|k| r.data.get(*k).map(|v| (k.to_string(), v.clone())))
        .collect();
    let duplicates: Vec<String> = store
        .duplicates
        .iter()
        .find(|(d, _)| d == id)
        .map(|(_, paths)| paths.clone())
        .unwrap_or_default();
    Ok(json!({
        "id": r.id(),
        "type": t,
        "path": r.path,
        "canonical_dir": dir,
        "in_canonical_location": dir.as_ref().map(|d| within(&r.path, d) || NON_CANONICAL_ROOTS.iter().any(|x| r.path.starts_with(x))),
        "authoritative_status": state_class_for(r, &authority),
        "lifecycle_state": r.status(),
        "version": r.data.get("version").cloned().unwrap_or(Value::Null),
        "content_hash": content_hash(&p.root, r),
        "provenance": {"declared": declared_prov, "version_control": git_provenance(p, &r.path)},
        "supersedes": r.list("supersedes"),
        "superseded_by": succ.get(id).cloned(),
        "expected_consumers": r.list("consumers"),
        "actual_consumers": super::lineage::consumers_of(store, id),
        "edges": r.edges().into_iter().map(|(s, t, d)| json!({"src": s, "type": t, "dst": d})).collect::<Vec<_>>(),
        "duplicate_paths": duplicates,
        "archived": r.problems.iter().any(|x| x == "archived"),
    }))
}

/// Identity and lineage problems across the governed records: misplaced records, duplicate ids, stale lineage
/// links and outputs whose declared consumers never consume them (`gov artefact check`; the full-audit lineage family's
/// record-level queries).
pub fn check(p: &Project, store: &RecordStore) -> Value {
    let misplaced = misplaced_records(Some(p), store);
    let duplicates: Vec<Value> = store
        .duplicates
        .iter()
        .map(|(id, paths)| json!({"id": id, "paths": paths, "message": format!("duplicate record id {id} at {}", paths.join(", "))}))
        .collect();
    let stale = super::lineage::stale_links(store);
    let unconsumed = super::lineage::unconsumed_outputs(store);
    // contradictions among current authoritative records that precedence cannot resolve (BC-P2-18), with how each
    // stands; an unresolved one is an authority problem
    let contradictions: Vec<Value> = crate::context::contradictions::detect_all(store)
        .iter()
        .map(|c| {
            let res = crate::context::contradictions::resolution(p, store, c);
            let mut v = c.to_value();
            v["resolution"] = res.to_value();
            v["blocks"] = json!(res.blocks());
            v
        })
        .collect();
    let unresolved = contradictions.iter().any(|c| c["blocks"] == true);
    let ok = misplaced.is_empty() && duplicates.is_empty() && stale.is_empty() && !unresolved;
    json!({"ok": ok, "records": store.records.len(), "misplaced": misplaced, "duplicate_ids": duplicates,
           "stale_links": stale, "unconsumed_outputs": unconsumed, "contradictions": contradictions})
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::records::parse_record_text;
    use std::collections::BTreeMap;

    #[test]
    fn misplaced_records_are_reported_and_subdirectories_are_canonical() {
        let recs = vec![
            parse_record_text(
                "id: REQ-0003\ntype: requirement\nstatus: ACTIVE\n",
                "spec/scenarios/REQ-0003.yaml",
            )
            .unwrap(),
            parse_record_text(
                "id: REQ-0002\ntype: requirement\nstatus: ACTIVE\n",
                "spec/requirements/moved/REQ-0002.yaml",
            )
            .unwrap(),
            parse_record_text(
                "id: TST-0001\ntype: test-obligation\nstatus: ACTIVE\n",
                "spec/tasks/TST-0001.yaml",
            )
            .unwrap(),
            parse_record_text(
                "id: X-0001\ntype: something-new\nstatus: ACTIVE\n",
                "spec/x/X-0001.yaml",
            )
            .unwrap(),
        ];
        let mut by_id = BTreeMap::new();
        for (i, r) in recs.iter().enumerate() {
            by_id.insert(r.id(), i);
        }
        let s = RecordStore {
            records: recs,
            by_id,
            duplicates: vec![],
            problems: vec![],
        };
        let m = misplaced_records(None, &s);
        assert_eq!(m.len(), 1, "{m:?}");
        assert_eq!(m[0]["id"], "REQ-0003");
        assert_eq!(m[0]["canonical_dir"], "spec/requirements");
    }

    #[test]
    fn failure_and_plan_records_have_canonical_locations() {
        let miss = parse_record_text(
            "id: FAIL-0001\ntype: failure\nfailure_kind: retrieval-miss\nstatus: ACTIVE\n",
            "spec/reports/memory-quality/FAIL-0001.yaml",
        )
        .unwrap();
        let tool = parse_record_text(
            "id: FAIL-0002\ntype: failure\nfailure_kind: tool-failure\nstatus: ACTIVE\n",
            "spec/reports/failures/FAIL-0002.yaml",
        )
        .unwrap();
        let misfiled = parse_record_text(
            "id: FAIL-0003\ntype: failure\nfailure_kind: tool-failure\nstatus: ACTIVE\n",
            "spec/reports/memory-quality/FAIL-0003.yaml",
        )
        .unwrap();
        let plan = parse_record_text(
            "id: MPLAN-GOVERNANCE-ADOPTION\ntype: migration-plan\nstatus: ACTIVE\n",
            "spec/audits/GOVERNANCE-ADOPTION/05-plan.yaml",
        )
        .unwrap();
        assert_eq!(record_in_canonical_location(None, &miss), Some(true));
        assert_eq!(record_in_canonical_location(None, &tool), Some(true));
        assert_eq!(record_in_canonical_location(None, &misfiled), Some(false));
        assert_eq!(record_in_canonical_location(None, &plan), Some(true));
        assert_eq!(crate::records::prefix_for("failure"), "FAIL");
        assert_eq!(crate::records::prefix_for("migration-plan"), "MPLAN");
    }

    #[test]
    fn content_derived_ids_are_stable_and_distinct() {
        let a = stable_content_id(
            "GF",
            &[
                "schema_invariants",
                "REQ-0001 has status 'X'",
                "spec/requirements/REQ-0001.yaml",
            ],
        );
        let b = stable_content_id(
            "GF",
            &[
                "schema_invariants",
                "REQ-0001 has status 'X'",
                "spec/requirements/REQ-0001.yaml",
            ],
        );
        let c = stable_content_id(
            "GF",
            &[
                "schema_invariants",
                "REQ-0002 has status 'X'",
                "spec/requirements/REQ-0002.yaml",
            ],
        );
        assert_eq!(a, b);
        assert_ne!(a, c);
        assert!(crate::records::id_regex().is_match(&a), "{a}");
    }
}
