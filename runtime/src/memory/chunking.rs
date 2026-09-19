//! Hierarchical chunking: document -> section -> child (framework section 14.1).
//!
//! Coverage invariant (BC-P2-25, Contract v3:249, :325): every non-empty line of an indexed code file and every
//! content section of a governed record is held by at least one chunk. Code is chunked down to its structural units
//! (module → class/impl → function/method), each unit's chunk carries the unit's qualified name as its section, and
//! whatever no unit covers (module-level statements, decorators without a unit, trailing blocks) is emitted as
//! `__module__` sections — nothing is silently left out of the lexical and semantic stores.
use regex::Regex;
use std::sync::OnceLock;

/// Identity of the chunking algorithm. It is part of the chunking pin (`indexer::chunking_config`), so an index
/// built by a different chunker is reported incompatible and is fully rebuilt rather than mixed.
///
/// Version 3 (repair-1 round 3, WS-2 R3-4): a Markdown heading is one line (an ATX heading, [`atx_heading`]) and
/// every heading is held by a chunk without its `#` markers — including a heading with no content of its own (a
/// title directly followed by a sub-heading, or a trailing heading), which version 2 dropped.
pub const CHUNKER_VERSION: &str = "3";
/// Name of the section holding code that belongs to no structural unit.
pub const MODULE_SECTION: &str = "__module__";

#[derive(Debug, Clone)]
pub struct Chunk {
    pub level: String,
    pub section: String,
    pub text: String,
    pub ordinal: usize,
    pub parent_ordinal: Option<usize>,
}

/// **The one definition of a Markdown heading** used by the chunker and by the coverage check
/// (`memory::coverage`): an ATX heading — one to six `#` at the start of the line followed by a space or tab (or
/// nothing: an empty heading). Returns the heading's text without its markers (trimmed), `None` for any other line.
/// A heading never spans lines.
pub fn atx_heading(line: &str) -> Option<&str> {
    static RX: OnceLock<Regex> = OnceLock::new();
    let rx = RX.get_or_init(|| Regex::new(r"^#{1,6}(?:[ \t]+(.*))?$").unwrap());
    let line = line.strip_suffix('\r').unwrap_or(line);
    rx.captures(line)
        .map(|c| c.get(1).map(|m| m.as_str().trim()).unwrap_or(""))
}

fn split_long(text: &str, max_chars: usize, overlap: usize) -> Vec<String> {
    let chars: Vec<char> = text.chars().collect();
    if chars.len() <= max_chars {
        return vec![text.to_string()];
    }
    let mut out = vec![];
    let mut start = 0usize;
    while start < chars.len() {
        let end = (start + max_chars).min(chars.len());
        let mut cut = end;
        if end < chars.len() {
            let lo = start + max_chars / 2;
            if let Some(pos) = (lo..end).rev().find(|&i| chars[i] == '\n') {
                cut = pos;
            }
        }
        if cut <= start {
            cut = end;
        }
        let piece: String = chars[start..cut].iter().collect();
        if !piece.trim().is_empty() {
            out.push(piece.trim().to_string());
        }
        if cut >= chars.len() {
            break;
        }
        start = cut.saturating_sub(overlap).max(start + 1);
    }
    out
}

pub fn chunk_markdown(title: &str, body: &str, max_chars: usize, overlap: usize) -> Vec<Chunk> {
    let mut chunks = vec![];
    let mut doc_text = title.trim().to_string();
    let first_para = body.trim().split("\n\n").next().unwrap_or("").to_string();
    if !first_para.is_empty() && !first_para.starts_with('#') {
        doc_text.push('\n');
        doc_text.push_str(&first_para.chars().take(400).collect::<String>());
    }
    chunks.push(Chunk {
        level: "document".into(),
        section: title.into(),
        text: doc_text,
        ordinal: 0,
        parent_ordinal: None,
    });
    // (section title, headings with no content of their own directly before it, section text)
    let mut sections: Vec<(String, Vec<String>, String)> = vec![];
    let mut pending: Vec<String> = vec![];
    let mut cur_title = title.to_string();
    let mut cur: Vec<&str> = vec![];
    let mut flush = |t: &str, lines: &mut Vec<&str>, pending: &mut Vec<String>| {
        let seg = lines.join("\n").trim().to_string();
        lines.clear();
        if seg.is_empty() {
            return false;
        }
        sections.push((t.to_string(), std::mem::take(pending), seg));
        true
    };
    let mut first = true;
    for line in body.lines() {
        match atx_heading(line) {
            Some(h) => {
                let had_content = flush(&cur_title, &mut cur, &mut pending);
                // a heading whose section is empty is still content: it is carried into the next section's chunk
                if !had_content && !first && !cur_title.is_empty() {
                    pending.push(cur_title.clone());
                }
                cur_title = h.to_string();
                first = false;
            }
            None => cur.push(line),
        }
    }
    let had_content = flush(&cur_title, &mut cur, &mut pending);
    if !had_content && !first && !cur_title.is_empty() {
        pending.push(cur_title.clone());
    }
    if !pending.is_empty() {
        // headings with no content after them (a document of headings only, or trailing headings)
        let last = pending.last().cloned().unwrap_or_default();
        let held = pending.join("\n");
        sections.push((last, vec![], held));
    }
    let mut ordinal = 1usize;
    for (sec_title, context, sec_text) in sections {
        let sec_ord = ordinal;
        let head: String = sec_text.chars().take(max_chars).collect();
        let lead = if context.is_empty() {
            String::new()
        } else {
            format!("{}\n", context.join("\n"))
        };
        chunks.push(Chunk {
            level: "section".into(),
            section: sec_title.clone(),
            text: format!("{lead}{sec_title}\n{head}"),
            ordinal: sec_ord,
            parent_ordinal: Some(0),
        });
        ordinal += 1;
        let pieces = split_long(&sec_text, max_chars, overlap);
        if pieces.len() > 1 {
            for piece in pieces {
                chunks.push(Chunk {
                    level: "child".into(),
                    section: sec_title.clone(),
                    text: piece,
                    ordinal,
                    parent_ordinal: Some(sec_ord),
                });
                ordinal += 1;
            }
        }
    }
    chunks
}

/// Record chunks: the document chunk and Markdown body sections, then one section per content section of the
/// record (`Record::text_sections`: every field, list-valued and nested ones included), split into children when
/// longer than `max_chars`. No section is dropped for being short.
pub fn chunk_record(
    title: &str,
    fields: &[(String, String)],
    body: &str,
    max_chars: usize,
    overlap: usize,
) -> Vec<Chunk> {
    let mut chunks = chunk_markdown(title, body, max_chars, overlap);
    let mut ordinal = chunks.iter().map(|c| c.ordinal).max().unwrap_or(0) + 1;
    for (name, text) in fields {
        if text.trim().is_empty() {
            continue;
        }
        let sec_ord = ordinal;
        let head: String = text.chars().take(max_chars).collect();
        chunks.push(Chunk {
            level: "section".into(),
            section: name.clone(),
            text: format!("{name}\n{head}"),
            ordinal: sec_ord,
            parent_ordinal: Some(0),
        });
        ordinal += 1;
        let pieces = split_long(text, max_chars, overlap);
        if pieces.len() > 1 {
            for piece in pieces {
                chunks.push(Chunk {
                    level: "child".into(),
                    section: name.clone(),
                    text: piece,
                    ordinal,
                    parent_ordinal: Some(sec_ord),
                });
                ordinal += 1;
            }
        }
    }
    chunks
}

pub fn chunk_plain(title: &str, text: &str, max_chars: usize, _overlap: usize) -> Vec<Chunk> {
    let mut chunks = vec![Chunk {
        level: "document".into(),
        section: title.into(),
        text: format!("{title}\n{}", text.chars().take(300).collect::<String>()),
        ordinal: 0,
        parent_ordinal: None,
    }];
    let mut buf = String::new();
    let mut ordinal = 1usize;
    for p in text.split("\n\n").filter(|p| !p.trim().is_empty()) {
        if buf.len() + p.len() > max_chars && !buf.is_empty() {
            chunks.push(Chunk {
                level: "section".into(),
                section: format!("part {ordinal}"),
                text: buf.trim().to_string(),
                ordinal,
                parent_ordinal: Some(0),
            });
            ordinal += 1;
            buf.clear();
        }
        buf.push_str(p);
        buf.push_str("\n\n");
    }
    if !buf.trim().is_empty() {
        chunks.push(Chunk {
            level: "section".into(),
            section: format!("part {ordinal}"),
            text: buf.trim().to_string(),
            ordinal,
            parent_ordinal: Some(0),
        });
    }
    chunks
}

/// A structural unit of a code file after normalisation: 1-based inclusive line span, nesting parent index.
#[derive(Debug, Clone)]
struct Unit {
    qualname: String,
    start: usize,
    end: usize,
    parent: Option<usize>,
}

/// True for a line that attaches to the unit below it: decorators and annotations (`@...`), attributes (`#[...]`,
/// `[Attribute(...)]`) and item doc comments (`///`).
fn is_attachment(line: &str) -> bool {
    static ATTR: OnceLock<Regex> = OnceLock::new();
    let attr = ATTR.get_or_init(|| Regex::new(r"^\[[A-Z][\w.]*(\(.*\))?\]$").unwrap());
    let t = line.trim();
    t.starts_with('@') || t.starts_with("#[") || t.starts_with("///") || attr.is_match(t)
}

/// Normalise the units reported by code intelligence: clamp to the file, extend each unit upward over the
/// decorator/attribute lines that belong to it, drop duplicates, and derive nesting from span containment (a unit
/// strictly inside another is its child; equal spans nest in reporting order).
fn normalise_units(lines: &[&str], units: &[(String, usize, usize)]) -> Vec<Unit> {
    let n = lines.len();
    let mut out: Vec<Unit> = vec![];
    let mut seen = std::collections::HashSet::new();
    for (q, a, b) in units {
        if q.is_empty() || q == MODULE_SECTION || *a == 0 || *a > n {
            continue;
        }
        let end = (*b).max(*a).min(n);
        let mut start = *a;
        while start > 1 && is_attachment(lines[start - 2]) {
            start -= 1;
        }
        if seen.insert((q.clone(), start, end)) {
            out.push(Unit {
                qualname: q.clone(),
                start,
                end,
                parent: None,
            });
        }
    }
    out.sort_by(|x, y| {
        x.start
            .cmp(&y.start)
            .then(y.end.cmp(&x.end))
            .then(x.qualname.cmp(&y.qualname))
    });
    let mut stack: Vec<usize> = vec![];
    for i in 0..out.len() {
        while let Some(&top) = stack.last() {
            if out[top].end >= out[i].end && out[top].start <= out[i].start {
                break;
            }
            stack.pop();
        }
        out[i].parent = stack.last().copied();
        stack.push(i);
    }
    out
}

/// Structural code chunks (framework §14.1: "prefer structural units such as module/class/function/symbol"):
///
/// * `document` — the path and the first 15 lines;
/// * `section` — each top-level unit (qualified name + its text, decorators included), and `__module__` sections
///   for code outside every unit (the header before the first unit first, then every later gap);
/// * `child` — each nested unit (a method inside its class, an item inside an `impl`), parented to the chunk of its
///   enclosing unit, so a symbol lookup returns the unit's own slice; and, for a unit longer than `max_chars`, the
///   parts of it no nested unit holds (size-split), so nothing inside a long unit is lost either.
///
/// `units` are `(qualname, lineno, end_lineno)`, 1-based inclusive, nested ones included. Every non-empty line of
/// `source` is held by at least one chunk (lines longer than `max_chars` are held split).
pub fn chunk_code(
    path: &str,
    source: &str,
    units: &[(String, usize, usize)],
    max_chars: usize,
    overlap: usize,
) -> Vec<Chunk> {
    let lines: Vec<&str> = source.lines().collect();
    let mut chunks = vec![Chunk {
        level: "document".into(),
        section: path.into(),
        text: format!(
            "{path}\n{}",
            lines
                .iter()
                .take(15)
                .cloned()
                .collect::<Vec<_>>()
                .join("\n")
        ),
        ordinal: 0,
        parent_ordinal: None,
    }];
    let units = normalise_units(&lines, units);
    let mut covered = vec![false; lines.len()];
    let mut ordinal = 1usize;
    // header: module-level lines before the first top-level unit
    let first = units
        .iter()
        .filter(|u| u.parent.is_none())
        .map(|u| u.start)
        .min()
        .unwrap_or(lines.len() + 1);
    emit_gaps(
        &lines,
        &mut covered,
        0,
        first.saturating_sub(1).min(lines.len()),
        None,
        MODULE_SECTION,
        "section",
        &mut chunks,
        &mut ordinal,
        max_chars,
        overlap,
    );
    for i in 0..units.len() {
        if units[i].parent.is_none() {
            emit_unit(
                &lines,
                &units,
                i,
                0,
                "section",
                &mut covered,
                &mut chunks,
                &mut ordinal,
                max_chars,
                overlap,
            );
        }
    }
    // module-level code after or between units (constants, registrations, `if __name__ == ...` blocks, exports)
    emit_gaps(
        &lines,
        &mut covered,
        0,
        lines.len(),
        None,
        MODULE_SECTION,
        "section",
        &mut chunks,
        &mut ordinal,
        max_chars,
        overlap,
    );
    chunks
}

#[allow(clippy::too_many_arguments)]
fn emit_unit(
    lines: &[&str],
    units: &[Unit],
    i: usize,
    parent_ord: usize,
    level: &str,
    covered: &mut [bool],
    chunks: &mut Vec<Chunk>,
    ordinal: &mut usize,
    max_chars: usize,
    overlap: usize,
) {
    let u = &units[i];
    let (a, b) = (u.start - 1, u.end.min(lines.len()));
    let text = lines[a..b].join("\n");
    let own_ord = *ordinal;
    chunks.push(Chunk {
        level: level.into(),
        section: u.qualname.clone(),
        text: format!(
            "{}\n{}",
            u.qualname,
            text.chars().take(max_chars).collect::<String>()
        ),
        ordinal: own_ord,
        parent_ordinal: Some(parent_ord),
    });
    *ordinal += 1;
    let fits = text.chars().count() <= max_chars;
    if fits {
        for c in covered.iter_mut().take(b).skip(a) {
            *c = true;
        }
    }
    let children: Vec<usize> = (0..units.len())
        .filter(|&j| units[j].parent == Some(i))
        .collect();
    for &j in &children {
        emit_unit(
            lines, units, j, own_ord, "child", covered, chunks, ordinal, max_chars, overlap,
        );
    }
    if !fits {
        // the unit's own chunk is truncated: hold the rest through size-split children of its uncovered lines
        emit_gaps(
            lines,
            covered,
            a,
            b,
            Some(own_ord),
            &u.qualname,
            "child",
            chunks,
            ordinal,
            max_chars,
            overlap,
        );
    }
}

/// Emit chunks for every maximal run of not-yet-covered lines in `[from, to)` (0-based) that holds a non-empty line.
/// With `parent = None` each run becomes a `section` under the document (split into children when long); with a
/// parent each run's pieces become children of it.
#[allow(clippy::too_many_arguments)]
fn emit_gaps(
    lines: &[&str],
    covered: &mut [bool],
    from: usize,
    to: usize,
    parent: Option<usize>,
    section: &str,
    level: &str,
    chunks: &mut Vec<Chunk>,
    ordinal: &mut usize,
    max_chars: usize,
    overlap: usize,
) {
    let mut i = from;
    while i < to {
        if covered[i] || lines[i].trim().is_empty() {
            i += 1;
            continue;
        }
        let mut j = i;
        while j < to && !covered[j] {
            j += 1;
        }
        let run = lines[i..j].join("\n");
        let run = run.trim_end();
        match parent {
            None => {
                let sec_ord = *ordinal;
                chunks.push(Chunk {
                    level: level.into(),
                    section: section.into(),
                    text: format!(
                        "{section}\n{}",
                        run.chars().take(max_chars).collect::<String>()
                    ),
                    ordinal: sec_ord,
                    parent_ordinal: Some(0),
                });
                *ordinal += 1;
                if run.chars().count() > max_chars {
                    for piece in split_long(run, max_chars, overlap) {
                        chunks.push(Chunk {
                            level: "child".into(),
                            section: section.into(),
                            text: piece,
                            ordinal: *ordinal,
                            parent_ordinal: Some(sec_ord),
                        });
                        *ordinal += 1;
                    }
                }
            }
            Some(po) => {
                for piece in split_long(run, max_chars, overlap) {
                    chunks.push(Chunk {
                        level: level.into(),
                        section: section.into(),
                        text: piece,
                        ordinal: *ordinal,
                        parent_ordinal: Some(po),
                    });
                    *ordinal += 1;
                }
            }
        }
        for c in covered.iter_mut().take(j).skip(i) {
            *c = true;
        }
        i = j;
    }
}

/// Non-empty lines of `source` that no chunk holds (each line compared trimmed against the trimmed lines of the
/// chunk texts; a line longer than `max_chars / 2` may legitimately be held split and is only checked as a
/// substring). Used by the coverage check (`memory::coverage`) and by the unit tests of the chunker. Code and
/// plain text are compared as they are; Markdown content through [`uncovered_lines_with`].
pub fn uncovered_lines(source: &str, chunks: &[Chunk], max_chars: usize) -> Vec<(usize, String)> {
    uncovered_lines_with(source, chunks, max_chars, false)
}

/// [`uncovered_lines`], and with `markdown` both sides are read as Markdown: a heading line ([`atx_heading`]) is
/// compared by its text, whether the source or a chunk holds it with or without its `#` markers (the chunker holds
/// headings as section titles, without markers; a document's lead paragraph may hold one with them). Every
/// uncovered line is returned (WS-2 R3-4).
pub fn uncovered_lines_with(
    source: &str,
    chunks: &[Chunk],
    max_chars: usize,
    markdown: bool,
) -> Vec<(usize, String)> {
    let norm = |l: &str| -> String {
        let t = l.trim();
        if markdown {
            if let Some(h) = atx_heading(t) {
                return h.to_string();
            }
        }
        t.to_string()
    };
    let mut held: std::collections::HashSet<String> = std::collections::HashSet::new();
    for c in chunks {
        for l in c.text.lines() {
            held.insert(norm(l));
        }
    }
    let mut out = vec![];
    for (i, l) in source.lines().enumerate() {
        let t = norm(l);
        if t.is_empty() || held.contains(&t) {
            continue;
        }
        if t.chars().count() > max_chars / 2 {
            let head: String = t.chars().take(max_chars / 4).collect();
            if chunks.iter().any(|c| c.text.contains(&head)) {
                continue;
            }
        }
        out.push((i + 1, l.trim().to_string()));
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn hierarchical_chunks() {
        let body = "intro para\n\n## Section A\n".to_string()
            + &"a".repeat(300)
            + "\n\n## Section B\n"
            + &"line\n".repeat(400);
        let ch = chunk_markdown("Doc", &body, 500, 50);
        assert_eq!(ch[0].level, "document");
        let sections: Vec<&Chunk> = ch.iter().filter(|c| c.level == "section").collect();
        assert!(sections.len() >= 3);
        let children: Vec<&Chunk> = ch.iter().filter(|c| c.level == "child").collect();
        assert!(!children.is_empty() && children.iter().all(|c| c.parent_ordinal.is_some()));
        let code = chunk_code(
            "a.rs",
            "use x;\nfn a() {\n1\n}\nfn b() {\n2\n}\n",
            &[("a".into(), 2, 4), ("b".into(), 5, 7)],
            100,
            10,
        );
        assert!(code.iter().any(|c| c.section == "a") && code.iter().any(|c| c.section == "b"));
    }

    /// BC-P2-25: module-level code between and after units, decorators and trailing blocks are chunked.
    #[test]
    fn every_non_empty_code_line_is_held_by_a_chunk() {
        let mut src = String::from(
            "\"\"\"Refund routes.\"\"\"\nfrom flask import Flask\n\napp = Flask(__name__)\n",
        );
        let mut units = vec![];
        for i in 1..=6 {
            let dec = src.lines().count() + 3;
            src.push_str(&format!(
                "\n\n@app.route(\"/refunds/v{i}/<rid>\", methods=[\"POST\"])\ndef refund_v{i}(rid):\n    return {{\"rid\": rid, \"version\": {i}}}\n"
            ));
            units.push((format!("refund_v{i}"), dec + 1, dec + 2));
        }
        src.push_str("\n\nREFUND_WINDOW_DAYS_SENTINEL = 45\n\nif __name__ == \"__main__\":\n    app.run(port=8088)\n");
        let chunks = chunk_code("src/app/refunds.py", &src, &units, 1200, 120);
        assert!(
            uncovered_lines(&src, &chunks, 1200).is_empty(),
            "{:?}",
            uncovered_lines(&src, &chunks, 1200)
        );
        let f3 = chunks.iter().find(|c| c.section == "refund_v3").unwrap();
        assert!(
            f3.text.contains("@app.route(\"/refunds/v3/<rid>\""),
            "a decorator belongs to its unit: {}",
            f3.text
        );
        assert!(chunks
            .iter()
            .any(|c| c.section == MODULE_SECTION && c.text.contains("app.run(port=8088)")));
        assert!(chunks
            .iter()
            .any(|c| c.section == MODULE_SECTION && c.text.contains("SENTINEL")));
    }

    /// BC-P2-25 / D3: methods are their own chunks under their class, and a long unit keeps every line.
    #[test]
    fn methods_are_child_units_and_long_units_keep_every_line() {
        let mut src = String::from("class Pipeline:\n    \"\"\"Runs steps.\"\"\"\n    LIMIT = 5\n");
        let mut units = vec![];
        for i in 1..=15 {
            let start = src.lines().count() + 2;
            src.push_str(&format!(
                "\n    def step_{i}(self, rows):\n        return [r for r in rows if r.get('k{i}') is not None]\n"
            ));
            units.push((format!("Pipeline.step_{i}"), start, start + 1));
        }
        src.push_str("\n    MIDDLE_CONSTANT = 'kept'\n");
        let start = src.lines().count() + 2;
        src.push_str("\n    def reconcile_quarantine(self, rows):\n        return [r for r in rows if r.get('quarantined')]\n");
        units.push(("Pipeline.reconcile_quarantine".into(), start, start + 1));
        let n = src.lines().count();
        units.push(("Pipeline".into(), 1, n));
        let chunks = chunk_code("p.py", &src, &units, 400, 40);
        assert!(
            uncovered_lines(&src, &chunks, 400).is_empty(),
            "{:?}",
            uncovered_lines(&src, &chunks, 400)
        );
        let class_chunk = chunks.iter().find(|c| c.section == "Pipeline").unwrap();
        let m = chunks
            .iter()
            .find(|c| c.section == "Pipeline.reconcile_quarantine")
            .unwrap();
        assert_eq!(m.level, "child");
        assert_eq!(m.parent_ordinal, Some(class_chunk.ordinal));
        assert!(m.text.contains("def reconcile_quarantine"));
        assert!(chunks.iter().any(|c| c.text.contains("MIDDLE_CONSTANT")));
    }

    /// WS-2 R3-4 / BC-P2-25: every Markdown heading is held — a title followed directly by a sub-heading, runs of
    /// headings, a trailing heading, a document of headings only — and the coverage comparison reads headings the
    /// same way on both sides, so a held heading is never reported as a gap while a missing body line still is.
    #[test]
    fn every_heading_is_held_and_headings_compare_the_same_way_on_both_sides() {
        assert_eq!(atx_heading("## Scope"), Some("Scope"));
        assert_eq!(atx_heading("#\tTabbed  "), Some("Tabbed"));
        assert_eq!(atx_heading("#"), Some(""));
        assert_eq!(atx_heading("#hashtag"), None);
        assert_eq!(atx_heading("####### seven"), None);
        assert_eq!(atx_heading("  # indented"), None);
        let docs = [
            "# Title\n\n## Sub\nbody line one\n",
            "# no input change\n# second heading\n",
            "intro paragraph\n# A\n## B\n### C\ntext under C\n## D\n",
            "# Only\n## Headings\n### Here\n",
            "#\nplain after an empty heading\n",
            "lead\n## X\n\n\n## Y\n  \n## Z\ntail\n",
        ];
        for body in docs {
            let chunks = chunk_markdown("doc.md", body, 1200, 120);
            let expected = body
                .lines()
                .map(|l| atx_heading(l).unwrap_or(l).to_string())
                .collect::<Vec<_>>()
                .join("\n");
            let miss = uncovered_lines_with(&expected, &chunks, 1200, true);
            assert!(miss.is_empty(), "{body:?}: {miss:?} {chunks:?}");
            // the raw source (markers kept) is held too when compared as Markdown
            assert!(uncovered_lines_with(body, &chunks, 1200, true).is_empty());
        }
        let c = chunk_markdown("doc.md", "# Title\n\n## Sub\nbody\n", 1200, 120);
        let sub = c.iter().find(|x| x.section == "Sub").unwrap();
        assert!(sub.text.starts_with("Title\nSub\n"), "{}", sub.text);
        // a body line no chunk holds is still a gap, and every uncovered line is listed
        let partial = vec![Chunk {
            level: "section".into(),
            section: "x".into(),
            text: "# held heading".into(),
            ordinal: 1,
            parent_ordinal: Some(0),
        }];
        let miss = uncovered_lines_with(
            "held heading\nmissing one\nmissing two\n",
            &partial,
            1200,
            true,
        );
        assert_eq!(
            miss,
            vec![
                (2, "missing one".to_string()),
                (3, "missing two".to_string())
            ]
        );
        // code keeps its `#` lines literally (a Python comment is not a heading)
        assert_eq!(
            uncovered_lines("# a comment\nx = 1\n", &partial, 1200).len(),
            2
        );
    }

    /// BC-P2-25: list-valued and nested record fields (scenario steps, acceptance criteria, a worker's nested
    /// return) are record sections and reach the chunks.
    #[test]
    fn record_sections_hold_list_and_nested_content() {
        let scn = crate::records::parse_record_text(
            "id: SCN-0001\ntype: scenario\ntitle: Two orders totalled\nstatus: ACTIVE\nfeature: F-0001\ngiven: [an empty ledger]\nwhen: [two orders are appended]\nthen: [the total is 750 cents]\n",
            "spec/scenarios/SCN-0001.yaml",
        )
        .unwrap();
        let req = crate::records::parse_record_text(
            "id: REQ-0001\ntype: requirement\ntitle: Totals\nstatus: ACTIVE\nacceptance_criteria:\n  - total_cents equals quantity times unit_cents\noptions:\n  - {id: A, description: integer cents}\n",
            "spec/requirements/REQ-0001.yaml",
        )
        .unwrap();
        let hnd = crate::records::parse_record_text(
            "id: HND-0001\ntype: handoff\ntitle: h\nstatus: ACTIVE\nreturn:\n  status: failed\n  tests: {status: failed, failed: 2}\n  discoveries: [refund rows are negative cents; sign convention undocumented]\n  risks: [float arithmetic reintroduces drift]\n",
            "spec/planning/HND-0001.yaml",
        )
        .unwrap();
        for (r, needles) in [
            (
                &scn,
                vec![
                    "two orders are appended",
                    "the total is 750 cents",
                    "an empty ledger",
                ],
            ),
            (
                &req,
                vec![
                    "total_cents equals quantity times unit_cents",
                    "integer cents",
                ],
            ),
            (
                &hnd,
                vec![
                    "sign convention undocumented",
                    "reintroduces drift",
                    "failed: 2",
                ],
            ),
        ] {
            let sections = r.text_sections();
            let chunks = chunk_record(&r.title(), &sections, "", 1200, 120);
            for n in needles {
                assert!(
                    chunks.iter().any(|c| c.text.contains(n)),
                    "{n} not chunked for {}: {chunks:?}",
                    r.id()
                );
            }
            let all: String = sections
                .iter()
                .map(|(_, t)| t.clone())
                .collect::<Vec<_>>()
                .join("\n");
            assert!(uncovered_lines(&all, &chunks, 1200).is_empty());
            assert!(!sections.iter().any(|(k, _)| k == "id" || k == "type"));
        }
        let text = hnd.text();
        assert!(
            text.contains("sign convention undocumented") && text.contains("reintroduces drift")
        );
    }
}
