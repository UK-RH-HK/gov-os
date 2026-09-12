//! Hierarchical chunking: document -> section -> child (framework section 14.1).
use regex::Regex;
use std::sync::OnceLock;

#[derive(Debug, Clone)]
pub struct Chunk {
    pub level: String,
    pub section: String,
    pub text: String,
    pub ordinal: usize,
    pub parent_ordinal: Option<usize>,
}

fn heading_rx() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"(?m)^(#{1,6})\s+(.*)$").unwrap())
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
    let mut sections: Vec<(String, String)> = vec![];
    let mut pos = 0usize;
    let mut last_title = title.to_string();
    for m in heading_rx().captures_iter(body) {
        let whole = m.get(0).unwrap();
        let seg = body[pos..whole.start()].trim().to_string();
        if !seg.is_empty() {
            sections.push((last_title.clone(), seg));
        }
        last_title = m[2].trim().to_string();
        pos = whole.end();
    }
    let tail = body[pos..].trim().to_string();
    if !tail.is_empty() {
        sections.push((last_title, tail));
    }
    if sections.is_empty() && !body.trim().is_empty() {
        sections.push((title.to_string(), body.trim().to_string()));
    }
    let mut ordinal = 1usize;
    for (sec_title, sec_text) in sections {
        let sec_ord = ordinal;
        let head: String = sec_text.chars().take(max_chars).collect();
        chunks.push(Chunk {
            level: "section".into(),
            section: sec_title.clone(),
            text: format!("{sec_title}\n{head}"),
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
        if text.len() < 40 {
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

/// Structural code chunks: header (imports/docs) + one chunk per top-level unit (qualname, lineno, end_lineno).
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
    if units.is_empty() {
        let mut rest = chunk_plain(path, source, max_chars, overlap);
        rest.remove(0);
        chunks.extend(rest);
        return chunks;
    }
    let mut ordinal = 1usize;
    let first = units.iter().map(|u| u.1).min().unwrap_or(1).max(1);
    let header: String = lines
        .iter()
        .take(first - 1)
        .cloned()
        .collect::<Vec<_>>()
        .join("\n");
    if !header.trim().is_empty() {
        chunks.push(Chunk {
            level: "section".into(),
            section: "__module__".into(),
            text: header.chars().take(max_chars).collect(),
            ordinal,
            parent_ordinal: Some(0),
        });
        ordinal += 1;
    }
    for (q, a, b) in units {
        let a1 = a.saturating_sub(1).min(lines.len());
        let b1 = (*b).min(lines.len()).max(a1);
        let text = lines[a1..b1].join("\n");
        let sec_ord = ordinal;
        chunks.push(Chunk {
            level: "section".into(),
            section: q.clone(),
            text: format!("{q}\n{}", text.chars().take(max_chars).collect::<String>()),
            ordinal: sec_ord,
            parent_ordinal: Some(0),
        });
        ordinal += 1;
        let pieces = split_long(&text, max_chars, overlap);
        if pieces.len() > 1 {
            for piece in pieces {
                chunks.push(Chunk {
                    level: "child".into(),
                    section: q.clone(),
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
}
