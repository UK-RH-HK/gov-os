//! Index content coverage (BC-P2-25; Contract v3:239, :249, :274, :325, :356 "deliberately missing index coverage").
//!
//! The invariant: every non-empty line of an indexed code file, every content line of a governed record (all
//! fields, list-valued and nested ones included, and the Markdown body) and every non-empty line of an indexed
//! document is held by at least one chunk of that artefact, so lexical and semantic memory have no silent blind
//! spots. `memory::indexer::rebuild` checks it for every artefact it (re)indexes and reports the result
//! (`IndexReport.coverage`, runtime meta `index_coverage`); [`verify`] checks the whole live index against the tree
//! and is the entry point for a health-scheduler/governance-suite check.
//!
//! **Markdown headings (repair-1 round 3, WS-2 R3-4).** A heading is one definition shared with the chunker
//! ([`crate::memory::chunking::atx_heading`]); the chunker holds every heading as a section title without its `#`
//! markers (chunker version 3), and the comparison reads headings the same way on both sides
//! ([`crate::memory::chunking::uncovered_lines_with`]), so a heading a chunk holds — with or without markers — is
//! never reported as a gap. Every uncovered line of a listed artefact is reported.
use crate::memory::chunking::{atx_heading, uncovered_lines_with, Chunk};
use crate::memory::db::RuntimeDb;
use crate::records::parse_record_text;
use crate::util::{read_text, sha256_hex};
use crate::{Project, Result};
use serde_json::{json, Value};

/// Markdown headings are held as section titles (without their `#` markers); compare body lines the same way.
pub fn without_heading_markers(text: &str) -> String {
    text.lines()
        .map(|l| atx_heading(l).unwrap_or(l).to_string())
        .collect::<Vec<_>>()
        .join("\n")
}

/// True when an artefact's content is compared as Markdown (records — their body is Markdown — and documents).
pub fn is_markdown_content(rel: &str, is_record: bool) -> bool {
    let ext = rel.rsplit('.').next().unwrap_or("").to_lowercase();
    is_record || matches!(ext.as_str(), "md" | "txt" | "rst")
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
    if is_markdown_content(rel, false) {
        without_heading_markers(text)
    } else {
        text.to_string()
    }
}

/// The non-empty lines of `expected` that none of `chunks` holds, compared as Markdown for records and documents.
pub fn uncovered(
    rel: &str,
    expected: &str,
    chunks: &[Chunk],
    max_chars: usize,
    is_record: bool,
) -> Vec<(usize, String)> {
    uncovered_lines_with(
        expected,
        chunks,
        max_chars,
        is_markdown_content(rel, is_record),
    )
}

/// A gap row: the artefact and **every** uncovered line (each line's text truncated for the report).
pub fn gap_row(artifact_id: Option<&str>, rel: &str, miss: &[(usize, String)]) -> Value {
    let mut v = json!({"path": rel, "count": miss.len(),
        "lines": miss.iter().map(|(n, l)| json!({"line": n, "text": l.chars().take(120).collect::<String>()})).collect::<Vec<_>>()});
    if let Some(a) = artifact_id {
        v["artifact_id"] = json!(a);
    }
    v
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
    let mut uncovered_total = 0usize;
    let mut gaps = vec![];
    let mut unlisted_artefacts = 0usize;
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
        let miss = uncovered(&rel, &expected, &chunks, max_chars, is_record);
        if !miss.is_empty() {
            uncovered_total += miss.len();
            if gaps.len() < 50 {
                gaps.push(gap_row(Some(&aid), &rel, &miss));
            } else {
                unlisted_artefacts += 1;
            }
        }
    }
    Ok(
        json!({"check": "index_content_coverage", "checked_artifacts": checked, "stale_skipped": stale,
        "uncovered_lines": uncovered_total, "complete": uncovered_total == 0, "gaps": gaps,
        "unlisted_artefacts": unlisted_artefacts, "comparison": "markdown headings by text on both sides (chunker 3)"}),
    )
}
