//! Built-in, dependency-free multi-language code-structural extraction (the fallback adapter when no `code_intel`
//! plugin is registered for a language; plugins are resolved through the capability registry, API-0001).
//!
//! Fidelity (BC-P2-27, Contract v3:252): every file is first lexed into *code* and *non-code* — comment and string
//! literal contents are blanked byte-for-byte (line and byte positions preserved) by [`blank_non_code`] — and
//! symbols, spans, calls, inheritance/implementation relations, route registrations and database models are read
//! from the code only. A `class`/`def`/`fn` inside a docstring, a comment or a string is never a symbol, and a brace
//! inside a string never moves a unit's end. String *values* (route paths, table names, import targets) are read from
//! the original text at positions the lexer classified as code. This is lexer-level, not a type-checked AST: names are
//! resolved by the index (same file, then imports, then repository), and relation kinds a language only decides at
//! type-check time (Go interface satisfaction) are not claimed.
use super::{CodeFacts, Model, Relation, Route, Symbol};
use regex::Regex;
use std::collections::HashMap;
use std::sync::OnceLock;

/// Identity of this extractor. Part of the per-artefact derivation key (`memory::indexer`), so a change to the
/// extractor re-derives the facts of files it produced even when their content did not change.
pub const EXTRACTOR_VERSION: &str = "builtin-generic/2";

struct LangRules {
    symbol: Vec<(&'static str, &'static str)>,
    import: Vec<&'static str>,
    block_scoped: bool,
}

fn rules(language: &str) -> LangRules {
    match language {
        "python" => LangRules {
            symbol: vec![
                (r"^\s*class\s+([A-Za-z_]\w*)", "class"),
                (r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(", "function"),
            ],
            import: vec![r"^\s*import\s+([\w\.]+)", r"^\s*from\s+([\w\.]+)\s+import"],
            block_scoped: false,
        },
        "rust" => LangRules {
            symbol: vec![
                (
                    r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:const\s+)?(?:async\s+)?(?:unsafe\s+)?(?:extern\s+(?:\x22[^\x22]*\x22\s+)?)?fn\s+([A-Za-z_]\w*)",
                    "function",
                ),
                (
                    r"^\s*(?:pub(?:\([^)]*\))?\s+)?struct\s+([A-Za-z_]\w*)",
                    "struct",
                ),
                (
                    r"^\s*(?:pub(?:\([^)]*\))?\s+)?enum\s+([A-Za-z_]\w*)",
                    "enum",
                ),
                (
                    r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:unsafe\s+)?trait\s+([A-Za-z_]\w*)",
                    "trait",
                ),
                (
                    r"^\s*(?:unsafe\s+)?impl(?:<[^>]*>)?\s+(?:[\w:]+(?:<[^>]*>)?\s+for\s+)?([A-Za-z_]\w*)",
                    "impl",
                ),
                (
                    r"^\s*(?:pub(?:\([^)]*\))?\s+)?mod\s+([A-Za-z_]\w*)",
                    "module",
                ),
            ],
            import: vec![
                r"^\s*(?:pub(?:\([^)]*\))?\s+)?use\s+([\w:]+)",
                r"^\s*(?:pub\s+)?mod\s+([A-Za-z_]\w*)\s*;",
            ],
            block_scoped: true,
        },
        "javascript" | "typescript" => LangRules {
            symbol: vec![
                (
                    r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)\s*[(<]",
                    "function",
                ),
                (
                    r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)",
                    "class",
                ),
                (
                    r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*(?::[^=]+)?=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*(?::[^=]+)?=>",
                    "function",
                ),
                (
                    r"^\s*(?:export\s+)?(?:declare\s+)?interface\s+([A-Za-z_$][\w$]*)",
                    "interface",
                ),
                (
                    r"^\s*(?:export\s+)?type\s+([A-Za-z_$][\w$]*)\s*(?:<[^>]*>)?\s*=",
                    "type",
                ),
                (
                    r"^\s+(?:(?:public|private|protected|static|readonly|async|override|abstract|get|set)\s+)*([A-Za-z_$][\w$]*)\s*(?:<[^>]*>)?\s*\([^;]*\)\s*(?::\s*[^{;]+)?\{\s*$",
                    "method",
                ),
            ],
            import: vec![
                r#"^\s*import\s+.*?from\s+['"]([^'"]+)['"]"#,
                r#"require\(\s*['"]([^'"]+)['"]\s*\)"#,
                r#"^\s*import\s+['"]([^'"]+)['"]"#,
                r#"^\s*export\s+.*?from\s+['"]([^'"]+)['"]"#,
            ],
            block_scoped: true,
        },
        "go" => LangRules {
            symbol: vec![
                (
                    r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*\(",
                    "function",
                ),
                (r"^\s*type\s+([A-Za-z_]\w*)\s+(?:struct|interface)", "type"),
            ],
            import: vec![
                r#"^\s*(?:[A-Za-z_]\w*\s+)?"([\w\./-]+)"\s*$"#,
                r#"^\s*import\s+(?:[A-Za-z_]\w*\s+)?"([\w\./-]+)""#,
            ],
            block_scoped: true,
        },
        "c" | "cpp" => LangRules {
            symbol: vec![
                (
                    r"^\s*(?:class|struct)\s+([A-Za-z_]\w*)\s*(?:final\s*)?(?::[^;]*)?\{?\s*$",
                    "class",
                ),
                (
                    r"^[A-Za-z_][\w:<>\*&\s]*?\s\*?([A-Za-z_]\w*)\s*\([^;]*\)\s*(?:const)?\s*\{?\s*$",
                    "function",
                ),
            ],
            import: vec![r#"^\s*#\s*include\s*[<"]([^>"]+)[>"]"#],
            block_scoped: true,
        },
        "java" | "kotlin" | "csharp" | "scala" => LangRules {
            symbol: vec![
                (
                    r"^\s*(?:public|private|protected|internal|static|final|abstract|sealed|data|open|partial|case|\s)*\s*(?:class|interface|enum|object|record|trait|struct)\s+([A-Za-z_]\w*)",
                    "class",
                ),
                (
                    r"^\s*(?:(?:public|private|protected|internal|override|open|abstract|suspend|inline|operator|infix|tailrec|final)\s+)*fun\s+(?:<[^>]*>\s*)?(?:[\w.]+\.)?([A-Za-z_]\w*)\s*\(",
                    "method",
                ),
                (
                    r"^\s*(?:(?:private|protected|override|final|implicit|lazy)\s+)*def\s+([A-Za-z_]\w*)",
                    "method",
                ),
                (
                    r"^\s*(?:public|private|protected|internal|static|final|override|async|virtual|abstract|synchronized|\s)*\s*[\w<>\[\],\s\?]+\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{?\s*$",
                    "method",
                ),
            ],
            import: vec![r"^\s*(?:import|using)\s+(?:static\s+)?([\w\.]+)"],
            block_scoped: true,
        },
        "ruby" => LangRules {
            symbol: vec![
                (r"^\s*class\s+([A-Za-z_]\w*)", "class"),
                (r"^\s*module\s+([A-Za-z_]\w*)", "module"),
                (r"^\s*def\s+(?:self\.)?([A-Za-z_]\w*[?!=]?)", "function"),
            ],
            import: vec![r#"^\s*require(?:_relative)?\s+['"]([^'"]+)['"]"#],
            block_scoped: false,
        },
        "shell" => LangRules {
            symbol: vec![(
                r"^\s*(?:function\s+)?([A-Za-z_]\w*)\s*\(\)\s*\{?",
                "function",
            )],
            import: vec![r#"^\s*(?:source|\.)\s+([^\s]+)"#],
            block_scoped: true,
        },
        _ => LangRules {
            symbol: vec![
                (r"^\s*(?:function|def|fn|func)\s+([A-Za-z_]\w*)", "function"),
                (
                    r"^\s*(?:class|struct|trait|interface)\s+([A-Za-z_]\w*)",
                    "class",
                ),
            ],
            import: vec![],
            block_scoped: true,
        },
    }
}

type LangPatterns = (Vec<(Regex, &'static str)>, Vec<Regex>, bool);

fn compiled(language: &str) -> LangPatterns {
    static CACHE: OnceLock<std::sync::Mutex<HashMap<String, LangPatterns>>> = OnceLock::new();
    let cache = CACHE.get_or_init(|| std::sync::Mutex::new(HashMap::new()));
    if let Some(c) = cache.lock().unwrap().get(language) {
        return c.clone();
    }
    let r = rules(language);
    let sy: Vec<(Regex, &'static str)> = r
        .symbol
        .iter()
        .filter_map(|(rx, k)| Regex::new(rx).ok().map(|c| (c, *k)))
        .collect();
    let im: Vec<Regex> = r
        .import
        .iter()
        .filter_map(|rx| Regex::new(rx).ok())
        .collect();
    let out = (sy, im, r.block_scoped);
    cache
        .lock()
        .unwrap()
        .insert(language.to_string(), out.clone());
    out
}

// ------------------------------------------------------------------------------------------------ lexical layer

#[derive(Clone, Copy, PartialEq)]
enum Family {
    /// `#` comments; `'`/`"` strings with escapes; Python triple quotes; Ruby `=begin/=end`.
    Hash { triple: bool, ruby: bool },
    /// Shell: `#` comments only at a word start; `'...'` without escapes, `"..."` with escapes.
    Shell,
    /// `//` and `/* */` comments; `"` strings; `'` char literal or string; backtick templates/raw strings.
    CLike {
        char_literals: bool,
        backtick: bool,
        rust: bool,
        triple: bool,
        verbatim: bool,
        hash_comments: bool,
    },
    /// SQL: `--` and `/* */` comments, `'...'` strings.
    Sql,
}

fn family(language: &str) -> Family {
    let c = |char_literals, backtick, rust, triple, verbatim, hash_comments| Family::CLike {
        char_literals,
        backtick,
        rust,
        triple,
        verbatim,
        hash_comments,
    };
    match language {
        "python" => Family::Hash {
            triple: true,
            ruby: false,
        },
        "ruby" | "elixir" => Family::Hash {
            triple: language == "elixir",
            ruby: language == "ruby",
        },
        "shell" => Family::Shell,
        "sql" => Family::Sql,
        "rust" => c(true, false, true, false, false, false),
        "javascript" | "typescript" => c(false, true, false, false, false, false),
        "go" => c(true, true, false, false, false, false),
        "kotlin" | "scala" => c(true, false, false, true, false, false),
        "csharp" => c(true, false, false, true, true, false),
        "swift" => c(false, false, false, true, false, false),
        "php" => c(false, false, false, false, false, true),
        _ => c(true, false, false, false, false, false),
    }
}

/// Replace the contents of comments and string literals with spaces, byte for byte (newlines and `\r` kept), so
/// every byte offset and line number of the result equals the source's. String delimiters are kept, so a literal
/// still reads as a literal; comment markers are blanked with the comment.
pub fn blank_non_code(language: &str, source: &str) -> String {
    let b = source.as_bytes();
    let n = b.len();
    let mut out: Vec<u8> = Vec::with_capacity(n);
    let fam = family(language);
    let blank =
        |out: &mut Vec<u8>, x: u8| out.push(if x == b'\n' || x == b'\r' { x } else { b' ' });
    let at_line_start = |i: usize| i == 0 || b[i - 1] == b'\n';
    let starts = |i: usize, s: &[u8]| i + s.len() <= n && &b[i..i + s.len()] == s;
    let mut i = 0usize;
    while i < n {
        let c = b[i];
        // ---- comments
        let line_comment = match fam {
            Family::Hash { .. } => c == b'#',
            Family::Shell => {
                c == b'#' && (i == 0 || b[i - 1].is_ascii_whitespace() || b[i - 1] == b';')
            }
            Family::CLike { hash_comments, .. } => starts(i, b"//") || (hash_comments && c == b'#'),
            Family::Sql => starts(i, b"--"),
        };
        if line_comment {
            while i < n && b[i] != b'\n' {
                blank(&mut out, b[i]);
                i += 1;
            }
            continue;
        }
        if matches!(fam, Family::Hash { ruby: true, .. })
            && at_line_start(i)
            && starts(i, b"=begin")
        {
            // Ruby block comment: through the end of the `=end` line
            loop {
                let line_start = i;
                while i < n && b[i] != b'\n' {
                    blank(&mut out, b[i]);
                    i += 1;
                }
                if i < n {
                    out.push(b'\n');
                    i += 1;
                }
                if starts(line_start, b"=end") || i >= n {
                    break;
                }
            }
            continue;
        }
        if matches!(fam, Family::CLike { .. } | Family::Sql) && starts(i, b"/*") {
            let nested = matches!(fam, Family::CLike { rust: true, .. })
                || matches!(
                    fam,
                    Family::CLike {
                        triple: true,
                        verbatim: false,
                        char_literals: false,
                        ..
                    }
                );
            let mut depth = 0usize;
            while i < n {
                if starts(i, b"/*") && (depth == 0 || nested) {
                    depth += 1;
                    blank(&mut out, b[i]);
                    blank(&mut out, b[i + 1]);
                    i += 2;
                    continue;
                }
                if starts(i, b"*/") {
                    depth -= 1;
                    blank(&mut out, b[i]);
                    blank(&mut out, b[i + 1]);
                    i += 2;
                    if depth == 0 {
                        break;
                    }
                    continue;
                }
                blank(&mut out, b[i]);
                i += 1;
            }
            continue;
        }
        // ---- strings. The closing delimiter of a literal that spans lines is blanked too, so a continuation line
        // never reads as code (its indentation is that of the first code after the literal, or it is empty).
        let close = |out: &mut Vec<u8>, delim: &[u8], spanned: bool| {
            for &x in delim {
                out.push(if spanned { b' ' } else { x });
            }
        };
        let triple_ok = matches!(
            fam,
            Family::Hash { triple: true, .. } | Family::CLike { triple: true, .. }
        );
        if triple_ok
            && (starts(i, b"\"\"\"") || (matches!(fam, Family::Hash { .. }) && starts(i, b"'''")))
        {
            let delim = [c, c, c];
            out.extend_from_slice(&delim);
            i += 3;
            let escapes = matches!(fam, Family::Hash { .. });
            let mut spanned = false;
            while i < n && !starts(i, &delim) {
                if escapes && b[i] == b'\\' && i + 1 < n {
                    blank(&mut out, b[i]);
                    blank(&mut out, b[i + 1]);
                    spanned |= b[i + 1] == b'\n';
                    i += 2;
                    continue;
                }
                spanned |= b[i] == b'\n';
                blank(&mut out, b[i]);
                i += 1;
            }
            if i < n {
                close(&mut out, &delim, spanned);
                i += 3;
            }
            continue;
        }
        if c == b'"' {
            // Rust raw strings r"..." / r#"..."#; C# verbatim @"..."
            let mut hashes = 0usize;
            let mut k = i;
            while k > 0 && b[k - 1] == b'#' {
                hashes += 1;
                k -= 1;
            }
            let rust_raw = matches!(fam, Family::CLike { rust: true, .. })
                && k > 0
                && b[k - 1] == b'r'
                && (k < 2
                    || !(b[k - 2].is_ascii_alphanumeric() || b[k - 2] == b'_')
                    || b[k - 2] == b'b');
            let verbatim =
                matches!(fam, Family::CLike { verbatim: true, .. }) && i > 0 && b[i - 1] == b'@';
            out.push(b'"');
            i += 1;
            let mut spanned = false;
            if rust_raw {
                let mut closing = vec![b'"'];
                closing.extend(std::iter::repeat(b'#').take(hashes));
                while i < n && !starts(i, &closing) {
                    spanned |= b[i] == b'\n';
                    blank(&mut out, b[i]);
                    i += 1;
                }
                if i < n {
                    close(&mut out, b"\"", spanned);
                    i += 1;
                }
                continue;
            }
            let multiline = !matches!(fam, Family::Hash { .. });
            while i < n {
                if verbatim && starts(i, b"\"\"") {
                    blank(&mut out, b'"');
                    blank(&mut out, b'"');
                    i += 2;
                    continue;
                }
                if !verbatim && b[i] == b'\\' && i + 1 < n {
                    spanned |= b[i + 1] == b'\n';
                    blank(&mut out, b[i]);
                    blank(&mut out, b[i + 1]);
                    i += 2;
                    continue;
                }
                if b[i] == b'"' || (b[i] == b'\n' && !multiline) {
                    break;
                }
                spanned |= b[i] == b'\n';
                blank(&mut out, b[i]);
                i += 1;
            }
            if i < n && b[i] == b'"' {
                close(&mut out, b"\"", spanned);
                i += 1;
            }
            continue;
        }
        if c == b'\'' {
            let string_quote = match fam {
                Family::Hash { .. } | Family::Shell | Family::Sql => true,
                Family::CLike { char_literals, .. } => !char_literals,
            };
            if string_quote {
                let escapes = !matches!(fam, Family::Shell | Family::Sql);
                out.push(b'\'');
                i += 1;
                while i < n {
                    if escapes && b[i] == b'\\' && i + 1 < n {
                        blank(&mut out, b[i]);
                        blank(&mut out, b[i + 1]);
                        i += 2;
                        continue;
                    }
                    if b[i] == b'\'' || (b[i] == b'\n' && escapes) {
                        break;
                    }
                    blank(&mut out, b[i]);
                    i += 1;
                }
                if i < n && b[i] == b'\'' {
                    out.push(b'\'');
                    i += 1;
                }
                continue;
            }
            // char literal ('x', '\n', '\u{..}', a multi-byte char) — otherwise a lifetime/label: code
            let end = if i + 1 < n && b[i + 1] == b'\\' {
                (i + 3..(i + 14).min(n)).find(|&j| b[j] == b'\'')
            } else if i + 1 < n {
                let w = utf8_width(b[i + 1]);
                let j = i + 1 + w;
                (j < n && b[j] == b'\'').then_some(j)
            } else {
                None
            };
            if let Some(j) = end {
                out.push(b'\'');
                for &x in &b[i + 1..j] {
                    blank(&mut out, x);
                }
                out.push(b'\'');
                i = j + 1;
                continue;
            }
            out.push(c);
            i += 1;
            continue;
        }
        if c == b'`' && matches!(fam, Family::CLike { backtick: true, .. }) {
            out.push(b'`');
            i += 1;
            let escapes = language != "go";
            let mut spanned = false;
            while i < n && b[i] != b'`' {
                if escapes && b[i] == b'\\' && i + 1 < n {
                    spanned |= b[i + 1] == b'\n';
                    blank(&mut out, b[i]);
                    blank(&mut out, b[i + 1]);
                    i += 2;
                    continue;
                }
                spanned |= b[i] == b'\n';
                blank(&mut out, b[i]);
                i += 1;
            }
            if i < n {
                close(&mut out, b"`", spanned);
                i += 1;
            }
            continue;
        }
        out.push(c);
        i += 1;
    }
    // Only ASCII bytes were substituted for whole UTF-8 sequences inside literals/comments, and code bytes were
    // copied unchanged, so the result is valid UTF-8; fall back defensively all the same.
    String::from_utf8(out).unwrap_or_else(|e| String::from_utf8_lossy(e.as_bytes()).into_owned())
}

fn utf8_width(first: u8) -> usize {
    match first {
        0x00..=0x7F => 1,
        0xC0..=0xDF => 2,
        0xE0..=0xEF => 3,
        _ => 4,
    }
}

/// The first string literal (single, double or backtick quoted) starting at or after byte `from` of `orig`, read at a
/// position the lexer classified as code (the delimiter survives blanking). Returns (value, end offset).
fn string_literal_at(orig: &str, blank: &str, from: usize) -> Option<(String, usize)> {
    let ob = orig.as_bytes();
    let bb = blank.as_bytes();
    let mut i = from;
    while i < ob.len() && i < bb.len() {
        let q = ob[i];
        if (q == b'"' || q == b'\'' || q == b'`') && bb[i] == q {
            let mut j = i + 1;
            while j < ob.len() {
                if ob[j] == b'\\' {
                    j += 2;
                    continue;
                }
                if ob[j] == q {
                    return Some((orig.get(i + 1..j)?.to_string(), j + 1));
                }
                j += 1;
            }
            return None;
        }
        if q == b')' && bb[i] == b')' {
            return None;
        }
        i += 1;
    }
    None
}

/// True when byte `pos` of the line is code (not inside a comment or string).
fn is_code_at(orig: &str, blank: &str, pos: usize) -> bool {
    orig.as_bytes().get(pos) == blank.as_bytes().get(pos) && orig.as_bytes().get(pos) != Some(&b' ')
}

fn indent_of(line: &str) -> usize {
    line.chars().take_while(|c| c.is_whitespace()).count()
}

/// End line of a unit: next non-empty code line with indentation <= the unit's start (indentation-scoped languages)
/// or the line closing the brace opened by the unit (block-scoped). Reads blanked lines: braces and indentation in
/// strings and comments do not count.
fn unit_end(lines: &[&str], start_idx: usize, block_scoped: bool) -> usize {
    if block_scoped {
        let mut depth = 0i32;
        let mut seen_open = false;
        for (i, line) in lines.iter().enumerate().skip(start_idx) {
            for ch in line.chars() {
                if ch == '{' {
                    depth += 1;
                    seen_open = true;
                }
                if ch == '}' {
                    depth -= 1;
                }
            }
            if seen_open && depth <= 0 {
                return i + 1;
            }
            if !seen_open && line.trim_end().ends_with(';') {
                return i + 1;
            }
            if i - start_idx > 4000 {
                break;
            }
        }
        if !seen_open {
            return start_idx + 1;
        }
        lines.len()
    } else {
        let base = indent_of(lines[start_idx]);
        let mut last = start_idx + 1;
        for (i, line) in lines.iter().enumerate().skip(start_idx + 1) {
            if line.trim().is_empty() {
                continue;
            }
            if indent_of(line) <= base {
                // a block terminator at the opening indentation (`end`) closes the unit and belongs to it
                return if line.trim() == "end" { i + 1 } else { last };
            }
            last = i + 1;
        }
        last
    }
}

// ------------------------------------------------------------------------------------------------ structure

fn simple_name(expr: &str) -> String {
    let e = expr.trim();
    let e = e.split(['<', '[', '(']).next().unwrap_or(e).trim();
    let e = e.trim_start_matches('*').trim_start_matches('&').trim();
    e.rsplit(['.', ':']).next().unwrap_or(e).trim().to_string()
}

fn is_ident(s: &str) -> bool {
    let mut ch = s.chars();
    matches!(ch.next(), Some(c) if c.is_alphabetic() || c == '_' || c == '$')
        && s.chars()
            .all(|c| c.is_alphanumeric() || c == '_' || c == '$')
}

/// Split a supertype list on top-level commas (generic arguments and call parentheses kept together).
fn split_top(list: &str, sep: char) -> Vec<String> {
    let mut out = vec![];
    let mut depth = 0i32;
    let mut cur = String::new();
    for ch in list.chars() {
        match ch {
            '<' | '(' | '[' => depth += 1,
            '>' | ')' | ']' => depth -= 1,
            _ => {}
        }
        if ch == sep && depth <= 0 {
            out.push(cur.trim().to_string());
            cur.clear();
        } else {
            cur.push(ch);
        }
    }
    if !cur.trim().is_empty() {
        out.push(cur.trim().to_string());
    }
    out
}

/// Remove a primary-constructor parameter list (`class X(val a: Int) : Y`) so its `:` is not read as the
/// supertype separator.
fn strip_ctor_params(header: &str, name: &str) -> String {
    let Some(pos) = header.find(name) else {
        return header.to_string();
    };
    let after = pos + name.len();
    let rest = &header[after..];
    let lead = rest.len() - rest.trim_start().len();
    let rest_t = rest.trim_start();
    let rest_t = if rest_t.starts_with('<') {
        // generic parameters come before the constructor
        let mut depth = 0i32;
        let mut end = 0;
        for (k, ch) in rest_t.char_indices() {
            match ch {
                '<' => depth += 1,
                '>' => {
                    depth -= 1;
                    if depth == 0 {
                        end = k + 1;
                        break;
                    }
                }
                _ => {}
            }
        }
        &rest_t[end..]
    } else {
        rest_t
    };
    let t = rest_t.trim_start();
    if !t.starts_with('(') {
        return header.to_string();
    }
    let mut depth = 0i32;
    for (k, ch) in t.char_indices() {
        match ch {
            '(' => depth += 1,
            ')' => {
                depth -= 1;
                if depth == 0 {
                    return format!("{} {}", &header[..after + lead], &t[k + 1..]);
                }
            }
            _ => {}
        }
    }
    header.to_string()
}

fn rx(pat: &str) -> Regex {
    Regex::new(pat).unwrap()
}

struct StructureRx {
    py_class: Regex,
    js_class: Regex,
    js_interface: Regex,
    java_decl: Regex,
    colon_decl: Regex,
    scala_decl: Regex,
    cpp_decl: Regex,
    rust_impl: Regex,
    rust_trait: Regex,
    ruby_class: Regex,
    ruby_include: Regex,
    go_struct: Regex,
    route_decorator: Regex,
    route_annotation: Regex,
    route_rust_attr: Regex,
    route_cs_attr: Regex,
    route_call: Regex,
    route_django: Regex,
    route_ruby: Regex,
    methods_kw: Regex,
    model_body: Regex,
    model_attr: Regex,
    model_call: Regex,
    tablename: Regex,
    go_tag: Regex,
    ident_arg: Regex,
}

fn srx() -> &'static StructureRx {
    static R: OnceLock<StructureRx> = OnceLock::new();
    R.get_or_init(|| StructureRx {
        py_class: rx(r"^\s*class\s+([A-Za-z_]\w*)\s*\(([^)]*)\)"),
        js_class: rx(r"\bclass\s+([A-Za-z_$][\w$]*)(?:\s*<[^{]*?>)?(?:\s+extends\s+([\w$.]+)(?:\s*<[^{]*?>)?(?:\([^)]*\))?)?(?:\s+implements\s+([^{]+))?\s*\{"),
        js_interface: rx(r"\binterface\s+([A-Za-z_$][\w$]*)(?:\s*<[^{]*?>)?\s+extends\s+([^{]+)\{"),
        java_decl: rx(r"\b(class|interface|enum|record)\s+([A-Za-z_]\w*)(?:\s*<[^{]*?>)?(?:\s*\([^)]*\))?(?:\s+extends\s+([^{]+?))?(?:\s+implements\s+([^{]+?))?\s*\{"),
        colon_decl: rx(r"\b(?:class|struct|interface|record|object)\s+([A-Za-z_]\w*)[^:{=]*?:\s*([^{]+?)\s*(?:\{|$)"),
        scala_decl: rx(r"\b(?:class|object|trait)\s+([A-Za-z_]\w*)[^{]*?\bextends\s+([\w.]+)((?:\s+with\s+[\w.]+)*)"),
        cpp_decl: rx(r"^\s*(?:class|struct)\s+([A-Za-z_]\w*)\s*(?:final\s*)?:\s*([^{;]+)"),
        rust_impl: rx(r"^\s*(?:unsafe\s+)?impl(?:<[^>]*>)?\s+([\w:]+)(?:<[^>]*>)?\s+for\s+([\w:]+)"),
        rust_trait: rx(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:unsafe\s+)?trait\s+([A-Za-z_]\w*)(?:<[^>]*>)?\s*:\s*([^{]+)"),
        ruby_class: rx(r"^\s*class\s+([A-Za-z_]\w*)\s*<\s*([\w:]+)"),
        ruby_include: rx(r"^\s*(?:include|extend|prepend)\s+([A-Z][\w:]*)"),
        go_struct: rx(r"^\s*type\s+([A-Za-z_]\w*)\s+(struct|interface)\s*\{"),
        route_decorator: rx(r"^\s*@\s*[\w.]*?\.?(route|get|post|put|delete|patch|head|options|api_route|websocket)\s*\("),
        route_annotation: rx(r"^\s*@\s*(?:(Get|Post|Put|Delete|Patch|Head|Options|Request)Mapping|(Get|Post|Put|Delete|Patch|Head|Options|All)|(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)|Path)\b\s*(\(|$)"),
        route_rust_attr: rx(r"^\s*#\[\s*(get|post|put|delete|patch|head|options|route)\s*\("),
        route_cs_attr: rx(r"^\s*\[\s*(?:Http(Get|Post|Put|Delete|Patch|Head|Options)|Route)\s*(?:\(|\])"),
        route_call: rx(r"(?:^|[^\w$])([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s*\.\s*(get|post|put|delete|patch|all|head|options|use|route|HandleFunc|Handle|GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|Any|Get|Post|Put|Delete|Patch|MapGet|MapPost|MapPut|MapDelete|MapPatch|Map)\s*\("),
        route_django: rx(r"(?:^|[^\w.])(path|re_path|url)\s*\("),
        route_ruby: rx(r"^\s*(get|post|put|patch|delete|match)\s+(?:\(\s*)?['\x22]"),
        methods_kw: rx(r#"methods\s*=\s*\[([^\]]*)\]"#),
        model_body: rx(r"^\s*(?:__tablename__|__table__|__table_args__)\s*=|\b(?:Column|mapped_column|relationship)\s*\(|\bmodels\.\w*Field\s*\(|\bmodels\.ForeignKey\s*\("),
        model_attr: rx(r"^\s*(?:@\s*(?:Entity|Table|Document)\b|\[\s*Table\s*\(|#\[\s*(?:diesel|sea_orm|table_name)\b|#\[\s*derive\s*\([^)]*\b(?:Queryable|Insertable|Selectable|FromRow|DeriveEntityModel|Identifiable|AsChangeset|Model)\b)"),
        model_call: rx(r"\b(?:mongoose\.model|sequelize\.define|\bmodel)\s*\(\s*['\x22]"),
        tablename: rx(r#"(?:__tablename__\s*=\s*['"]|table_name\s*=\s*['"]?|\bname\s*=\s*['"]|db_table\s*=\s*['"]|Table\s*\(\s*['"]|Entity\s*\(\s*['"])([\w.]+)"#),
        go_tag: rx(r#"`[^`]*\b(?:gorm|db|bun|pg|sql):"[^`]*`"#),
        ident_arg: rx(r"^\s*,\s*(?:async\s+)?(?:[\w$]+\s*\(\s*)?([A-Za-z_$][\w$.]*)"),
    })
}

const HTTP_CLIENT_RECEIVERS: &[&str] = &[
    "requests",
    "axios",
    "httpx",
    "http_client",
    "client",
    "session",
    "fetch",
    "superagent",
    "got",
    "ky",
    "request",
    "this.http",
    "http.client",
    "urllib",
    "aiohttp",
    "req",
    "res",
    "response",
    "api",
    "self.client",
];

fn route_method(verb: &str) -> String {
    match verb.to_ascii_lowercase().as_str() {
        "route" | "api_route" | "use" | "all" | "any" | "handle" | "handlefunc" | "map"
        | "request" | "path" | "match" | "" => "ANY".into(),
        v => v.trim_start_matches("map").to_ascii_uppercase(),
    }
}

/// Extract relations, routes and database models from (blanked, original) lines and the unit table.
fn structure(
    language: &str,
    lines: &[&str],
    blank: &[&str],
    symbols: &[Symbol],
) -> (Vec<Relation>, Vec<Route>, Vec<Model>) {
    let r = srx();
    let mut relations: Vec<Relation> = vec![];
    let mut routes: Vec<Route> = vec![];
    let mut models: Vec<Model> = vec![];
    let is_type = |k: &str| {
        matches!(
            k,
            "class" | "struct" | "interface" | "trait" | "type" | "enum" | "impl"
        )
    };
    // a type declaration header: from the definition line through the line that opens its body, or through the
    // first line that does not continue the declaration (a trailing `,` `:` `(` `<` `&` `+` or keyword continues it)
    let header = |i: usize| -> String {
        let mut h = String::new();
        for l in blank.iter().skip(i).take(8) {
            h.push_str(l);
            h.push(' ');
            let t = l.trim_end();
            if t.contains('{') {
                break;
            }
            let continues = [
                ",",
                ":",
                "(",
                "<",
                "&",
                "+",
                "|",
                "extends",
                "implements",
                "with",
                "where",
            ]
            .iter()
            .any(|c| t.ends_with(c));
            if !continues {
                break;
            }
        }
        h
    };
    let mut push_rel = |kind: &str, from: &str, name: &str, line: usize| {
        let n = simple_name(name);
        if n.is_empty()
            || !is_ident(&n)
            || n == from
            || matches!(n.as_str(), "object" | "Object" | "self")
        {
            return;
        }
        relations.push(Relation {
            kind: kind.into(),
            from: from.into(),
            name: n,
            lineno: line,
        });
    };
    // ---- inheritance / implementation, from each type definition
    for s in symbols
        .iter()
        .filter(|s| is_type(&s.kind) && s.lineno >= 1 && s.lineno <= blank.len())
    {
        let i = s.lineno - 1;
        let h = header(i);
        let line = s.lineno;
        match language {
            "python" => {
                let src = blank[i..(i + 6).min(blank.len())].join(" ");
                if let Some(c) = r.py_class.captures(&src) {
                    for base in split_top(&c[2], ',') {
                        if base.contains('=') {
                            continue; // metaclass=..., keyword arguments
                        }
                        push_rel("inherits", &s.qualname, &base, line);
                    }
                }
            }
            "javascript" | "typescript" => {
                if let Some(c) = r.js_class.captures(&h) {
                    if let Some(e) = c.get(2) {
                        push_rel("inherits", &s.qualname, e.as_str(), line);
                    }
                    if let Some(im) = c.get(3) {
                        for x in split_top(im.as_str(), ',') {
                            push_rel("implements", &s.qualname, &x, line);
                        }
                    }
                } else if let Some(c) = r.js_interface.captures(&h) {
                    for x in split_top(&c[2], ',') {
                        push_rel("inherits", &s.qualname, &x, line);
                    }
                }
            }
            "java" => {
                if let Some(c) = r.java_decl.captures(&h) {
                    let is_iface = &c[1] == "interface";
                    if let Some(e) = c.get(3) {
                        for x in split_top(e.as_str(), ',') {
                            push_rel("inherits", &s.qualname, &x, line);
                        }
                    }
                    if let Some(im) = c.get(4) {
                        for x in split_top(im.as_str(), ',') {
                            push_rel(
                                if is_iface { "inherits" } else { "implements" },
                                &s.qualname,
                                &x,
                                line,
                            );
                        }
                    }
                }
            }
            "kotlin" | "csharp" | "swift" => {
                let h = strip_ctor_params(&h, &s.name);
                if let Some(c) = r.colon_decl.captures(&h) {
                    let list = c[2].split(" where ").next().unwrap_or("").to_string();
                    for (k, x) in split_top(&list, ',').into_iter().enumerate() {
                        let n = simple_name(&x);
                        let iface_like = n.len() > 1
                            && n.starts_with('I')
                            && n.chars()
                                .nth(1)
                                .map(|ch| ch.is_uppercase())
                                .unwrap_or(false);
                        let kind = match language {
                            "kotlin" => {
                                if x.contains('(') {
                                    "inherits"
                                } else {
                                    "implements"
                                }
                            }
                            "csharp" => {
                                if iface_like {
                                    "implements"
                                } else {
                                    "inherits"
                                }
                            }
                            _ => {
                                if k == 0 {
                                    "inherits"
                                } else {
                                    "implements"
                                }
                            }
                        };
                        push_rel(kind, &s.qualname, &x, line);
                    }
                }
            }
            "scala" => {
                if let Some(c) = r.scala_decl.captures(&h) {
                    push_rel("inherits", &s.qualname, &c[2], line);
                    for w in c[3].split_whitespace().filter(|w| *w != "with") {
                        push_rel("implements", &s.qualname, w, line);
                    }
                }
            }
            "c" | "cpp" => {
                if let Some(c) = r.cpp_decl.captures(&h) {
                    for x in split_top(&c[2], ',') {
                        let x = x
                            .replace("public", "")
                            .replace("private", "")
                            .replace("protected", "")
                            .replace("virtual", "");
                        push_rel("inherits", &s.qualname, &x, line);
                    }
                }
            }
            "rust" => {
                if s.kind == "impl" {
                    if let Some(c) = r.rust_impl.captures(blank[i]) {
                        push_rel("implements", &simple_name(&c[2]), &c[1], line);
                    }
                } else if s.kind == "trait" {
                    if let Some(c) = r.rust_trait.captures(&h) {
                        for x in c[2].split('+') {
                            let x = x.trim();
                            if !x.starts_with('\'') && !x.is_empty() {
                                push_rel("inherits", &s.qualname, x, line);
                            }
                        }
                    }
                }
            }
            "ruby" => {
                if let Some(c) = r.ruby_class.captures(blank[i]) {
                    push_rel("inherits", &s.qualname, &c[2], line);
                }
                let end = s.end_lineno.min(blank.len());
                for (j, l) in blank.iter().enumerate().take(end).skip(i + 1) {
                    if let Some(c) = r.ruby_include.captures(l) {
                        push_rel("implements", &s.qualname, &c[1], j + 1);
                    }
                }
            }
            "go" => {
                if let Some(c) = r.go_struct.captures(blank[i]) {
                    // embedded fields / embedded interfaces: a member line that is only a type name
                    let end = s.end_lineno.min(blank.len());
                    for (j, l) in blank
                        .iter()
                        .enumerate()
                        .take(end.saturating_sub(1))
                        .skip(i + 1)
                    {
                        let t = l.trim();
                        let first = t.split_whitespace().next().unwrap_or("");
                        let rest = t[first.len()..].trim();
                        let only_type = !first.is_empty()
                            && (rest.is_empty() || rest.starts_with('`'))
                            && first.trim_start_matches('*').split('.').all(is_ident);
                        if only_type {
                            push_rel("inherits", &c[1], first, j + 1);
                        }
                    }
                }
            }
            _ => {}
        }
    }
    // ---- route registrations
    let next_function = |after: usize| -> Option<String> {
        symbols
            .iter()
            .filter(|s| s.lineno > after && matches!(s.kind.as_str(), "function" | "method"))
            .min_by_key(|s| s.lineno)
            .filter(|s| s.lineno <= after + 12)
            .map(|s| s.qualname.clone())
    };
    let enclosing = |line: usize| -> Option<String> {
        symbols
            .iter()
            .filter(|s| s.kind != "module" && s.lineno <= line && line <= s.end_lineno)
            .max_by_key(|s| s.lineno)
            .map(|s| s.qualname.clone())
    };
    for (i, (orig, bl)) in lines.iter().zip(blank.iter()).enumerate() {
        let lineno = i + 1;
        let mut found: Vec<(String, String, Option<String>)> = vec![]; // (method, path, handler)
        if let Some(c) = r.route_decorator.captures(bl) {
            let verb = c[1].to_string();
            if let Some((path, _)) = string_literal_at(orig, bl, c.get(0).unwrap().end()) {
                if path.starts_with('/') || path.is_empty() {
                    let mut method = route_method(&verb);
                    if method == "ANY" {
                        if let Some(m) = r.methods_kw.captures(orig) {
                            let ms: Vec<String> = m[1]
                                .split(',')
                                .map(|x| {
                                    x.trim()
                                        .trim_matches(|ch| ch == '"' || ch == '\'')
                                        .to_ascii_uppercase()
                                })
                                .filter(|x| !x.is_empty())
                                .collect();
                            if !ms.is_empty() {
                                method = ms.join("|");
                            }
                        } else if verb == "route" {
                            method = "GET".into();
                        }
                    }
                    found.push((method, path, next_function(lineno)));
                }
            }
        } else if let Some(c) = r.route_annotation.captures(bl) {
            let verb = c
                .get(1)
                .or(c.get(2))
                .or(c.get(3))
                .map(|m| m.as_str())
                .unwrap_or("path");
            let path = string_literal_at(orig, bl, c.get(0).unwrap().end().saturating_sub(1))
                .map(|(p, _)| p)
                .unwrap_or_default();
            found.push((
                route_method(verb),
                if path.is_empty() { "/".into() } else { path },
                next_function(lineno),
            ));
        } else if let Some(c) = r.route_rust_attr.captures(bl) {
            if let Some((path, _)) = string_literal_at(orig, bl, c.get(0).unwrap().end()) {
                found.push((route_method(&c[1]), path, next_function(lineno)));
            }
        } else if let Some(c) = r.route_cs_attr.captures(bl) {
            let path = string_literal_at(orig, bl, c.get(0).unwrap().end().saturating_sub(1))
                .map(|(p, _)| p)
                .unwrap_or_default();
            let verb = c.get(1).map(|m| m.as_str()).unwrap_or("route");
            found.push((route_method(verb), path, next_function(lineno)));
        } else {
            for c in r.route_call.captures_iter(bl) {
                let recv = c[1].to_string();
                let verb = c[2].to_string();
                let lower = verb
                    .chars()
                    .next()
                    .map(|ch| ch.is_lowercase())
                    .unwrap_or(false);
                if lower
                    && HTTP_CLIENT_RECEIVERS
                        .iter()
                        .any(|h| recv == *h || recv.ends_with(&format!(".{h}")))
                {
                    continue;
                }
                let Some((path, end)) = string_literal_at(orig, bl, c.get(0).unwrap().end()) else {
                    continue;
                };
                if !path.starts_with('/') {
                    continue;
                }
                let rest = orig.get(end..).unwrap_or("");
                let handler = r.ident_arg.captures(rest).map(|h| h[1].to_string());
                let inline = rest.trim_start().starts_with(',') && handler.is_none()
                    || rest.contains("=>")
                    || rest.contains("function")
                    || rest.contains("func(");
                if handler.is_none() && !inline {
                    continue; // a registration names or defines its handler; a bare `x.get("/path")` is a lookup/call
                }
                let handler = match handler {
                    Some(h)
                        if !matches!(
                            h.as_str(),
                            "async" | "function" | "func" | "req" | "ctx" | "c"
                        ) =>
                    {
                        Some(simple_name(&h))
                    }
                    _ => enclosing(lineno),
                };
                found.push((route_method(&verb), path, handler));
            }
            if found.is_empty() && language == "python" {
                if let Some(c) = r.route_django.captures(bl) {
                    if let Some((path, end)) = string_literal_at(orig, bl, c.get(0).unwrap().end())
                    {
                        let rest = orig.get(end..).unwrap_or("");
                        if let Some(h) = r.ident_arg.captures(rest) {
                            found.push(("ANY".into(), path, Some(simple_name(&h[1]))));
                        }
                    }
                }
            }
            if found.is_empty() && language == "ruby" {
                if let Some(c) = r.route_ruby.captures(bl) {
                    if let Some((path, _)) =
                        string_literal_at(orig, bl, c.get(0).unwrap().end() - 1)
                    {
                        found.push((route_method(&c[1]), path, enclosing(lineno)));
                    }
                }
            }
        }
        for (method, path, handler) in found {
            routes.push(Route {
                method,
                path,
                handler,
                lineno,
            });
        }
    }
    // ---- database models
    let attachments_above = |start: usize| -> Vec<&str> {
        let mut out = vec![];
        let mut k = start;
        while k > 1 {
            let l = lines[k - 2].trim();
            if l.starts_with('@') || l.starts_with("#[") || (l.starts_with('[') && l.ends_with(']'))
            {
                out.push(lines[k - 2]);
                k -= 1;
            } else {
                break;
            }
        }
        out
    };
    let orm_bases = |q: &str| -> Option<String> {
        relations
            .iter()
            .filter(|rel| rel.from == q && rel.kind == "inherits")
            .map(|rel| rel.name.clone())
            .find(|n| {
                matches!(
                    n.as_str(),
                    "ApplicationRecord" | "DeclarativeBase" | "Model" | "SQLModel"
                )
            })
    };
    for s in symbols
        .iter()
        .filter(|s| matches!(s.kind.as_str(), "class" | "struct" | "type"))
    {
        if s.lineno == 0 || s.lineno > lines.len() {
            continue;
        }
        let (a, b) = (s.lineno - 1, s.end_lineno.min(lines.len()).max(s.lineno));
        let mut evidence: Option<String> = None;
        let mut table: Option<String> = None;
        for att in attachments_above(s.lineno) {
            if r.model_attr.is_match(att) {
                evidence = Some(att.trim().chars().take(80).collect());
                table = r
                    .tablename
                    .captures(att)
                    .map(|c| c[1].to_string())
                    .or(table);
            }
        }
        // only the unit's own lines (not its nested units) carry model evidence
        let kids: Vec<(usize, usize)> = symbols
            .iter()
            .filter(|o| o.parent.as_deref() == Some(s.qualname.as_str()) && o.lineno != s.lineno)
            .map(|o| (o.lineno, o.end_lineno))
            .collect();
        for j in a..b {
            let bl = blank[j];
            if kids.iter().any(|(ka, kb)| *ka <= j + 1 && j + 1 <= *kb) {
                continue;
            }
            if r.model_body.is_match(bl)
                || (language == "go" && r.go_tag.is_match(lines[j]))
                || (language == "go" && bl.trim() == "gorm.Model")
            {
                evidence.get_or_insert_with(|| lines[j].trim().chars().take(80).collect());
                if table.is_none()
                    && (lines[j].contains("__tablename__") || lines[j].contains("db_table"))
                {
                    table = r.tablename.captures(lines[j]).map(|c| c[1].to_string());
                }
            }
        }
        if evidence.is_none() {
            if let Some(base) = orm_bases(&s.qualname) {
                let hdr = lines[a];
                let qualified = hdr.contains(&format!("models.{base}"))
                    || hdr.contains(&format!("db.{base}"))
                    || matches!(base.as_str(), "ApplicationRecord" | "DeclarativeBase")
                    || (base == "SQLModel" && hdr.contains("table=True"))
                    || (base == "Model"
                        && matches!(language, "javascript" | "typescript")
                        && lines
                            .iter()
                            .any(|l| l.contains(&format!("{}.init(", s.name))));
                if qualified {
                    evidence = Some(format!("base {base}"));
                }
            }
        }
        if let Some(ev) = evidence {
            models.push(Model {
                name: s.name.clone(),
                qualname: s.qualname.clone(),
                table,
                lineno: s.lineno,
                evidence: ev,
            });
        }
    }
    for (i, (orig, bl)) in lines.iter().zip(blank.iter()).enumerate() {
        if let Some(c) = r.model_call.find(bl) {
            if let Some((name, _)) = string_literal_at(orig, bl, c.end() - 1) {
                if is_ident(&name) && !models.iter().any(|m| m.name == name) {
                    models.push(Model {
                        name: name.clone(),
                        qualname: name,
                        table: None,
                        lineno: i + 1,
                        evidence: orig.trim().chars().take(80).collect(),
                    });
                }
            }
        }
    }
    (relations, routes, models)
}

const NOT_A_METHOD: &[&str] = &[
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "return",
    "new",
    "else",
    "when",
    "using",
    "lock",
    "foreach",
    "synchronized",
    "function",
    "with",
    "until",
    "unless",
    "do",
    "try",
    "finally",
    "throw",
    "await",
    "yield",
];

pub fn analyze(path: &str, language: &str, source: &str) -> CodeFacts {
    let (sy, im, block_scoped) = compiled(language);
    let blanked = blank_non_code(language, source);
    let lines: Vec<&str> = source.lines().collect();
    let blank: Vec<&str> = blanked.lines().collect();
    let module = path
        .rsplit('/')
        .next()
        .unwrap_or(path)
        .rsplit_once('.')
        .map(|(a, _)| a.to_string())
        .unwrap_or(path.to_string());
    let mut symbols = vec![Symbol {
        name: module.clone(),
        qualname: module.clone(),
        kind: "module".into(),
        lineno: 1,
        end_lineno: lines.len().max(1),
        parent: None,
        signature: String::new(),
    }];
    let mut imports = vec![];
    let mut units = vec![];
    let mut stack: Vec<(usize, String, usize)> = vec![]; // (indent, qualname, end_line)
    for (i, bl) in blank.iter().enumerate() {
        let orig = lines.get(i).copied().unwrap_or("");
        for r in &im {
            if let Some(c) = r.captures(orig) {
                // an import is read from the original line only where the lexer saw code at the match
                let at = c
                    .get(0)
                    .map(|m| m.start() + (m.as_str().len() - m.as_str().trim_start().len()))
                    .unwrap_or(0);
                if is_code_at(orig, bl, at) {
                    imports.push(c[1].to_string());
                }
            }
        }
        for (r, kind) in &sy {
            if let Some(c) = r.captures(bl) {
                let name = c[1].to_string();
                if *kind == "method" && NOT_A_METHOD.contains(&name.as_str()) {
                    continue; // control-flow statements shaped like a method header
                }
                let ind = indent_of(bl);
                while let Some(top) = stack.last() {
                    if top.0 >= ind || top.2 <= i {
                        stack.pop();
                    } else {
                        break;
                    }
                }
                let parent = stack.last().map(|t| t.1.clone());
                let qual = match &parent {
                    Some(p) => format!("{p}.{name}"),
                    None => name.clone(),
                };
                let end = unit_end(&blank, i, block_scoped);
                let kind_final = if *kind == "function" && parent.is_some() {
                    "method"
                } else if *kind == "method" && parent.is_none() {
                    "function"
                } else {
                    kind
                };
                symbols.push(Symbol {
                    name: name.clone(),
                    qualname: qual.clone(),
                    kind: kind_final.into(),
                    lineno: i + 1,
                    end_lineno: end,
                    parent: parent.clone(),
                    signature: orig.trim().chars().take(120).collect(),
                });
                if parent.is_none() {
                    units.push((qual.clone(), i + 1, end));
                }
                stack.push((ind, qual, end));
                break;
            }
        }
    }
    imports.sort();
    imports.dedup();
    // calls: identifiers followed by '(' in the code of each top-level unit, excluding keywords and the unit itself
    static CALL_RX: OnceLock<Regex> = OnceLock::new();
    let call_rx = CALL_RX.get_or_init(|| Regex::new(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(").unwrap());
    const KEYWORDS: &[&str] = &[
        "if",
        "for",
        "while",
        "switch",
        "return",
        "fn",
        "def",
        "class",
        "func",
        "function",
        "match",
        "catch",
        "print",
        "println",
        "printf",
        "assert",
        "elif",
        "except",
        "with",
        "sizeof",
        "new",
        "super",
        "self",
        "this",
        "impl",
        "struct",
        "enum",
        "trait",
        "type",
        "let",
        "var",
        "const",
        "import",
        "from",
        "async",
        "await",
        "lambda",
        "not",
        "and",
        "or",
        "in",
        "is",
        "as",
        "yield",
        "raise",
        "throw",
        "try",
        "typeof",
        "instanceof",
        "case",
        "defer",
        "go",
        "range",
        "make",
        "len",
        "cap",
        "append",
        "Some",
        "Ok",
        "Err",
        "None",
        "vec",
        "format",
        "panic",
        "unwrap",
        "expect",
        "json",
        "require",
        "export",
        "static",
        "extern",
        "unsafe",
        "loop",
        "where",
        "pub",
        "mod",
        "use",
        "test",
        "it",
        "describe",
    ];
    let defined: std::collections::HashSet<String> =
        symbols.iter().map(|s| s.name.clone()).collect();
    let mut calls: Vec<(String, String)> = vec![];
    for (qual, a, b) in &units {
        let a1 = a.saturating_sub(1).min(blank.len());
        let b1 = (*b).min(blank.len()).max(a1);
        let text = blank[a1..b1].join("\n");
        let mut seen = std::collections::HashSet::new();
        for c in call_rx.captures_iter(&text) {
            let name = c[1].to_string();
            if KEYWORDS.contains(&name.as_str()) || name == *qual || name.len() < 3 {
                continue;
            }
            if !defined.contains(&name) && !text.lines().any(|l| l.contains(&format!("{name}("))) {
                continue;
            }
            if seen.insert(name.clone()) {
                calls.push((qual.clone(), name));
            }
        }
    }
    let (relations, routes, models) = structure(language, &lines, &blank, &symbols);
    CodeFacts {
        language: language.into(),
        provider: "builtin-generic".into(),
        symbols,
        imports,
        calls,
        units,
        relations,
        routes,
        models,
        degraded: None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn no_symbols_from_comments_or_strings() {
        let py = "\"\"\"Doc.\n\nclass NotReal:\n    pass\ndef not_real():\n    pass\n\"\"\"\n# class AlsoNot:\nx = \"def fake(): pass\"\n\n\ndef real(x):\n    return x + 1\n";
        let f = analyze("m.py", "python", py);
        let names: Vec<&str> = f.symbols.iter().map(|s| s.name.as_str()).collect();
        assert!(names.contains(&"real"), "{names:?}");
        assert!(
            !names
                .iter()
                .any(|n| ["NotReal", "not_real", "AlsoNot", "fake"].contains(n)),
            "{names:?}"
        );
        let ts = "// class Ghost {}\nconst s = `function phantom() {`;\n/* interface Hidden {} */\nexport function real(a: string) {\n  return \"}\";\n}\nexport function after() {}\n";
        let f = analyze("a.ts", "typescript", ts);
        let names: Vec<&str> = f.symbols.iter().map(|s| s.name.as_str()).collect();
        assert!(
            names.contains(&"real") && names.contains(&"after"),
            "{names:?}"
        );
        assert!(
            !names
                .iter()
                .any(|n| ["Ghost", "phantom", "Hidden"].contains(n)),
            "{names:?}"
        );
        let real = f.symbols.iter().find(|s| s.name == "real").unwrap();
        assert_eq!(
            (real.lineno, real.end_lineno),
            (4, 6),
            "a brace inside a string must not move the unit end"
        );
        let rs = "fn f<'a>(x: &'a str) -> char { let c = '{'; let s = r#\"fn fake() {\"#; c }\n// fn commented() {}\npub fn g() {}\n";
        let f = analyze("l.rs", "rust", rs);
        let names: Vec<&str> = f.symbols.iter().map(|s| s.name.as_str()).collect();
        assert_eq!(names, vec!["l", "f", "g"], "{names:?}");
    }

    #[test]
    fn blanking_preserves_positions_and_lines() {
        for (lang, src) in [
            ("python", "a = 'x#y' # c\ns = \"\"\"multi\nline\"\"\"\n"),
            (
                "rust",
                "let s = \"é\\\"\"; // é\n/* a /* nested */ b */ let t = 1;\n",
            ),
            ("go", "x := `raw\n{string}`\ny := 'a'\n"),
            ("csharp", "var p = @\"C:\\dir\"\"q\"; // c\n"),
            ("shell", "echo \"$# not a comment\" # comment\n"),
        ] {
            let b = blank_non_code(lang, src);
            assert_eq!(b.len(), src.len(), "{lang}");
            assert_eq!(b.lines().count(), src.lines().count(), "{lang}");
        }
        let b = blank_non_code("rust", "/* a /* nested */ b */ let t = 1;\n");
        assert!(b.contains("let t = 1;") && !b.contains('a') && !b.contains('b'));
        let b = blank_non_code("shell", "echo $# x # comment\n");
        assert!(b.contains("$#") && !b.contains("comment"));
    }

    #[test]
    fn inheritance_routes_and_models_across_languages() {
        let py = "from flask import Flask\nfrom sqlalchemy import Column, Integer\napp = Flask(__name__)\n\nclass Order(Base, AuditedEntity, metaclass=Meta):\n    __tablename__ = \"orders\"\n    id = Column(Integer)\n\n@app.route(\"/orders/<int:oid>\", methods=[\"GET\", \"POST\"])\ndef get_order(oid):\n    return oid\n\n@app.post(\"/orders\")\ndef create():\n    return requests.get(\"/elsewhere\")\n";
        let f = analyze("api.py", "python", py);
        let inh: Vec<(&str, &str, &str)> = f
            .relations
            .iter()
            .map(|r| (r.kind.as_str(), r.from.as_str(), r.name.as_str()))
            .collect();
        assert!(
            inh.contains(&("inherits", "Order", "Base"))
                && inh.contains(&("inherits", "Order", "AuditedEntity")),
            "{inh:?}"
        );
        assert!(!inh.iter().any(|x| x.2 == "Meta"), "{inh:?}");
        let routes: Vec<(&str, &str, Option<&str>)> = f
            .routes
            .iter()
            .map(|r| (r.method.as_str(), r.path.as_str(), r.handler.as_deref()))
            .collect();
        assert!(
            routes.contains(&("GET|POST", "/orders/<int:oid>", Some("get_order"))),
            "{routes:?}"
        );
        assert!(
            routes.contains(&("POST", "/orders", Some("create"))),
            "{routes:?}"
        );
        assert!(
            !routes.iter().any(|r| r.1 == "/elsewhere"),
            "an HTTP client call is not a route: {routes:?}"
        );
        assert!(
            f.models
                .iter()
                .any(|m| m.name == "Order" && m.table.as_deref() == Some("orders")),
            "{:?}",
            f.models
        );
        let ts = "import { Router } from \"express\";\nexport interface Repo { find(id: number): void; }\nexport class Sql implements Repo, Other {\n  find(id: number) {}\n}\nexport class Cached extends Sql {}\nconst router = Router();\nrouter.get(\"/api/orders/:id\", async (req, res) => {\n  res.json({});\n});\nconst v = cache.get(\"/not-a-route\");\nrouter.post(\"/api/orders\", createOrder);\n";
        let f = analyze("api.ts", "typescript", ts);
        let inh: Vec<(&str, &str, &str)> = f
            .relations
            .iter()
            .map(|r| (r.kind.as_str(), r.from.as_str(), r.name.as_str()))
            .collect();
        assert!(
            inh.contains(&("implements", "Sql", "Repo"))
                && inh.contains(&("implements", "Sql", "Other"))
                && inh.contains(&("inherits", "Cached", "Sql")),
            "{inh:?}"
        );
        let paths: Vec<(&str, &str)> = f
            .routes
            .iter()
            .map(|r| (r.method.as_str(), r.path.as_str()))
            .collect();
        assert!(
            paths.contains(&("GET", "/api/orders/:id")) && paths.contains(&("POST", "/api/orders")),
            "{paths:?}"
        );
        assert!(!paths.iter().any(|p| p.1 == "/not-a-route"), "{paths:?}");
        let rs = "pub trait Ledger: Send + Sync { fn total(&self) -> i64; }\npub struct Mem { e: Vec<i64> }\nimpl Ledger for Mem {\n    fn total(&self) -> i64 { 0 }\n}\n#[derive(Queryable, Debug)]\npub struct Row { id: i32 }\n#[get(\"/ping\")]\nasync fn ping() -> &'static str { \"pong\" }\n";
        let f = analyze("l.rs", "rust", rs);
        let inh: Vec<(&str, &str, &str)> = f
            .relations
            .iter()
            .map(|r| (r.kind.as_str(), r.from.as_str(), r.name.as_str()))
            .collect();
        assert!(
            inh.contains(&("implements", "Mem", "Ledger"))
                && inh.contains(&("inherits", "Ledger", "Send")),
            "{inh:?}"
        );
        assert!(f.models.iter().any(|m| m.name == "Row"), "{:?}", f.models);
        assert!(
            f.routes
                .iter()
                .any(|r| r.path == "/ping" && r.handler.as_deref() == Some("ping")),
            "{:?}",
            f.routes
        );
        let go = "package server\n\nimport \"net/http\"\n\ntype Order struct {\n\tgorm.Model\n\tSku string `gorm:\"size:64\"`\n}\n\nfunc Ping(w http.ResponseWriter, r *http.Request) {}\n\nfunc Register() {\n\thttp.HandleFunc(\"/ping\", Ping)\n}\n";
        let f = analyze("s.go", "go", go);
        assert!(
            f.routes
                .iter()
                .any(|r| r.path == "/ping" && r.handler.as_deref() == Some("Ping")),
            "{:?}",
            f.routes
        );
        assert!(f.models.iter().any(|m| m.name == "Order"), "{:?}", f.models);
        assert!(
            f.relations
                .iter()
                .any(|r| r.from == "Order" && r.name == "Model"),
            "{:?}",
            f.relations
        );
        let java = "@Entity\n@Table(name = \"orders\")\npublic class Order extends BaseEntity implements Serializable {\n  @GetMapping(\"/orders/{id}\")\n  public Order get(Long id) { return null; }\n}\n";
        let f = analyze("Order.java", "java", java);
        assert!(
            f.models
                .iter()
                .any(|m| m.name == "Order" && m.table.as_deref() == Some("orders")),
            "{:?}",
            f.models
        );
        assert!(
            f.relations
                .iter()
                .any(|r| r.kind == "inherits" && r.name == "BaseEntity"),
            "{:?}",
            f.relations
        );
        assert!(
            f.relations
                .iter()
                .any(|r| r.kind == "implements" && r.name == "Serializable"),
            "{:?}",
            f.relations
        );
        assert!(
            f.routes
                .iter()
                .any(|r| r.method == "GET" && r.path == "/orders/{id}"),
            "{:?}",
            f.routes
        );
    }

    #[test]
    fn trait_method_declarations_are_single_line_units() {
        let rs = "pub trait Ledger {\n    fn append(&mut self, c: i64);\n    fn total(&self) -> i64;\n}\n";
        let f = analyze("l.rs", "rust", rs);
        let append = f.symbols.iter().find(|s| s.name == "append").unwrap();
        assert_eq!((append.lineno, append.end_lineno), (2, 2));
        assert_eq!(append.parent.as_deref(), Some("Ledger"));
    }
}
