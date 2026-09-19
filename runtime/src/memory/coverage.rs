//! Index content coverage (BC-P2-25; Contract v3:239, :249, :274, :325, :356 "deliberately missing index coverage").
//!
//! The invariant: every non-empty line of an indexed code file, every content line of a governed record (all
//! fields, list-valued and nested ones included, and the Markdown body) and every non-empty line of an indexed
//! document is held by at least one chunk of that artefact, so lexical and semantic memory have no silent blind
//! spots. `memory::indexer::rebuild` checks it for every artefact it (re)indexes and reports the result
//! (`IndexReport.coverage`, runtime meta `index_coverage`); [`verify`] checks the whole live index against the tree
//! and is the entry point for a health-scheduler/governance-suite check.
use crate::memory::chunking::{uncovered_lines, Chunk};
use crate::memory::db::RuntimeDb;
use crate::records::parse_record_text;
use crate::util::{read_text, sha256_hex};
use crate::{Project, Result};
use regex::Regex;
use serde_json::{json, Value};
use std::sync::OnceLock;

/// Markdown headings are held as section titles (without their `#` markers); compare body lines the same way.
pub fn without_heading_markers(text: &str) -> String {
    static RX: OnceLock<Regex> = OnceLock::new();
    let rx = RX.get_or_init(|| Regex::new(r"^#{1,6}\s+(.*)$").unwrap());
    text.lines()
        .map(|l| match rx.captures(l) {
            Some(c) => c[1].trim().to_string(),
            None => l.to_string(),
        })
        .collect::<Vec<_>>()
        .join("\n")
}

/// The content an artefact's chunks must hold: for a record, its content sections and body; for a document,
/// its text with heading markers removed; for code and plain text, the text itself.
pub fn expected_content(rel: &str, text: &str, is_record: bool) -> String {
    if is_record {
        if let Some(r) = parse_record_text(text, rel) {
            let body = if r.body.is_empty() {
                r.get("body")
            } else {
                r.body.clone()
            };
            return r
                .text_sections()
                .into_iter()
                .map(|(_, t)| t)
                .chain(std::iter::once(without_heading_markers(&body)))
                .collect::<Vec<_>>()
                .join("\n");
        }
    }
    let ext = rel.rsplit('.').next().unwrap_or("").to_lowercase();
    if matches!(ext.as_str(), "md" | "txt" | "rst") {
        without_heading_markers(text)
    } else {
        text.to_string()
    }
}

/// Check the live index: for each artefact whose file is unchanged since indexing, the non-empty lines of its
/// expected content that no chunk holds. Artefacts whose file changed are counted as `stale_skipped` (freshness,
/// not coverage, owns them). `complete` is true only when nothing checked has a gap.
pub fn verify(p: &Project, db: &RuntimeDb) -> Result<Value> {
    let max_chars = db
        .get_meta("chunking")
        .and_then(|c| c.get("max_chars").and_then(|m| m.as_u64()))
        .unwrap_or(1200) as usize;
    let mut checked = 0usize;
    let mut stale = 0usize;
    let mut uncovered = 0usize;
    let mut gaps = vec![];
    for a in db.query(
        "SELECT artifact_id, path, record_type, content_hash, lexical, semantic FROM artifacts ORDER BY path",
        &[],
    )? {
        let rel = a["path"].as_str().unwrap_or("").to_string();
        let aid = a["artifact_id"].as_str().unwrap_or("").to_string();
        let Ok(text) = read_text(&p.root.join(&rel)) else {
            stale += 1;
            continue;
        };
        if a["content_hash"].as_str() != Some(sha256_hex(text.as_bytes()).as_str()) {
            stale += 1;
            continue;
        }
        let is_record = a["record_type"].as_str() != Some("file");
        let expected = expected_content(&rel, &text, is_record);
        let chunks: Vec<Chunk> = db
            .query(
                "SELECT level, section, text, ordinal FROM chunks WHERE artifact_id=?1 ORDER BY ordinal",
                &[&aid],
            )?
            .into_iter()
            .map(|c| Chunk {
                level: c["level"].as_str().unwrap_or("").to_string(),
                section: c["section"].as_str().unwrap_or("").to_string(),
                text: c["text"].as_str().unwrap_or("").to_string(),
                ordinal: c["ordinal"].as_u64().unwrap_or(0) as usize,
                parent_ordinal: None,
            })
            .collect();
        checked += 1;
        let miss = uncovered_lines(&expected, &chunks, max_chars);
        if !miss.is_empty() {
            uncovered += miss.len();
            if gaps.len() < 50 {
                gaps.push(json!({"artifact_id": aid, "path": rel, "count": miss.len(),
                    "lines": miss.iter().take(5).map(|(n, l)| json!({"line": n, "text": l.chars().take(120).collect::<String>()})).collect::<Vec<_>>()}));
            }
        }
    }
    Ok(
        json!({"check": "index_content_coverage", "checked_artifacts": checked, "stale_skipped": stale,
        "uncovered_lines": uncovered, "complete": uncovered == 0, "gaps": gaps}),
    )
}
