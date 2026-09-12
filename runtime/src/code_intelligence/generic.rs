//! Built-in, dependency-free multi-language symbol/import extraction (line-oriented heuristics).
//! Fidelity is lower than a language server or AST plugin; degradations are recorded in capability memory.
use super::{CodeFacts, Symbol};
use regex::Regex;
use std::sync::OnceLock;

struct LangRules { symbol: Vec<(&'static str, &'static str)>, import: Vec<&'static str>, block_scoped: bool }

fn rules(language: &str) -> LangRules {
    match language {
        "python" => LangRules { symbol: vec![(r"^\s*class\s+([A-Za-z_]\w*)", "class"), (r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(", "function")], import: vec![r"^\s*import\s+([\w\.]+)", r"^\s*from\s+([\w\.]+)\s+import"], block_scoped: false },
        "rust" => LangRules { symbol: vec![(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+([A-Za-z_]\w*)", "function"), (r"^\s*(?:pub(?:\([^)]*\))?\s+)?struct\s+([A-Za-z_]\w*)", "struct"), (r"^\s*(?:pub(?:\([^)]*\))?\s+)?enum\s+([A-Za-z_]\w*)", "enum"), (r"^\s*(?:pub(?:\([^)]*\))?\s+)?trait\s+([A-Za-z_]\w*)", "trait"), (r"^\s*impl(?:<[^>]*>)?\s+(?:[\w:]+\s+for\s+)?([A-Za-z_]\w*)", "impl"), (r"^\s*(?:pub(?:\([^)]*\))?\s+)?mod\s+([A-Za-z_]\w*)", "module")], import: vec![r"^\s*use\s+([\w:]+)", r"^\s*(?:pub\s+)?mod\s+([A-Za-z_]\w*)\s*;"], block_scoped: true },
        "javascript" | "typescript" => LangRules { symbol: vec![(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)\s*\(", "function"), (r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)", "class"), (r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*(?::[^=]+)?=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*(?::[^=]+)?=>", "function"), (r"^\s*(?:export\s+)?interface\s+([A-Za-z_$][\w$]*)", "interface"), (r"^\s*(?:export\s+)?type\s+([A-Za-z_$][\w$]*)\s*=", "type")], import: vec![r#"^\s*import\s+.*?from\s+['"]([^'"]+)['"]"#, r#"require\(\s*['"]([^'"]+)['"]\s*\)"#, r#"^\s*import\s+['"]([^'"]+)['"]"#, r#"^\s*export\s+.*?from\s+['"]([^'"]+)['"]"#], block_scoped: true },
        "go" => LangRules { symbol: vec![(r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\(", "function"), (r"^\s*type\s+([A-Za-z_]\w*)\s+(?:struct|interface)", "type")], import: vec![r#"^\s*"([\w\./-]+)"\s*$"#, r#"^\s*import\s+"([\w\./-]+)""#], block_scoped: true },
        "c" | "cpp" => LangRules { symbol: vec![(r"^\s*(?:class|struct)\s+([A-Za-z_]\w*)", "class"), (r"^[A-Za-z_][\w:<>\*&\s]*?\s\*?([A-Za-z_]\w*)\s*\([^;]*\)\s*(?:const)?\s*\{?\s*$", "function")], import: vec![r#"^\s*#include\s*[<"]([^>"]+)[>"]"#], block_scoped: true },
        "java" | "kotlin" | "csharp" | "scala" => LangRules { symbol: vec![(r"^\s*(?:public|private|protected|internal|static|final|abstract|sealed|data|open|\s)*\s*(?:class|interface|enum|object|record)\s+([A-Za-z_]\w*)", "class"), (r"^\s*(?:public|private|protected|internal|static|final|override|async|virtual|abstract|\s)*\s*(?:fun\s+)?[\w<>\[\],\s\?]+\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{?\s*$", "method")], import: vec![r"^\s*(?:import|using)\s+([\w\.]+)"], block_scoped: true },
        "ruby" => LangRules { symbol: vec![(r"^\s*class\s+([A-Za-z_]\w*)", "class"), (r"^\s*module\s+([A-Za-z_]\w*)", "module"), (r"^\s*def\s+(?:self\.)?([A-Za-z_]\w*[?!=]?)", "function")], import: vec![r#"^\s*require(?:_relative)?\s+['"]([^'"]+)['"]"#], block_scoped: false },
        "shell" => LangRules { symbol: vec![(r"^\s*(?:function\s+)?([A-Za-z_]\w*)\s*\(\)\s*\{?", "function")], import: vec![r#"^\s*(?:source|\.)\s+([^\s]+)"#], block_scoped: true },
        _ => LangRules { symbol: vec![(r"^\s*(?:function|def|fn|func)\s+([A-Za-z_]\w*)", "function"), (r"^\s*(?:class|struct|trait|interface)\s+([A-Za-z_]\w*)", "class")], import: vec![], block_scoped: true },
    }
}

fn compiled(language: &str) -> (Vec<(Regex, &'static str)>, Vec<Regex>, bool) {
    static CACHE: OnceLock<std::sync::Mutex<std::collections::HashMap<String, (Vec<(Regex, &'static str)>, Vec<Regex>, bool)>>> = OnceLock::new();
    let cache = CACHE.get_or_init(|| std::sync::Mutex::new(std::collections::HashMap::new()));
    if let Some(c) = cache.lock().unwrap().get(language) { return c.clone(); }
    let r = rules(language);
    let sy: Vec<(Regex, &'static str)> = r.symbol.iter().filter_map(|(rx, k)| Regex::new(rx).ok().map(|c| (c, *k))).collect();
    let im: Vec<Regex> = r.import.iter().filter_map(|rx| Regex::new(rx).ok()).collect();
    let out = (sy, im, r.block_scoped);
    cache.lock().unwrap().insert(language.to_string(), out.clone());
    out
}

fn indent_of(line: &str) -> usize { line.chars().take_while(|c| c.is_whitespace()).count() }

/// End line of a unit: next non-empty line with indentation <= the unit's start (python) or matching brace depth (block-scoped).
fn unit_end(lines: &[&str], start_idx: usize, block_scoped: bool) -> usize {
    if block_scoped {
        let mut depth = 0i32;
        let mut seen_open = false;
        for (i, line) in lines.iter().enumerate().skip(start_idx) {
            for ch in line.chars() {
                if ch == '{' { depth += 1; seen_open = true; }
                if ch == '}' { depth -= 1; }
            }
            if seen_open && depth <= 0 { return i + 1; }
            if !seen_open && line.trim_end().ends_with(';') && i > start_idx { return i + 1; }
            if i - start_idx > 2000 { break; }
        }
        if !seen_open { return start_idx + 1; }
        lines.len()
    } else {
        let base = indent_of(lines[start_idx]);
        for (i, line) in lines.iter().enumerate().skip(start_idx + 1) {
            if line.trim().is_empty() { continue; }
            if indent_of(line) <= base { return i; }
        }
        lines.len()
    }
}

pub fn analyze(path: &str, language: &str, source: &str) -> CodeFacts {
    let (sy, im, block_scoped) = compiled(language);
    let lines: Vec<&str> = source.lines().collect();
    let module = path.rsplit('/').next().unwrap_or(path).rsplit_once('.').map(|(a, _)| a.to_string()).unwrap_or(path.to_string());
    let mut symbols = vec![Symbol { name: module.clone(), qualname: module.clone(), kind: "module".into(), lineno: 1, end_lineno: lines.len().max(1), parent: None, signature: String::new() }];
    let mut imports = vec![];
    let mut units = vec![];
    let mut stack: Vec<(usize, String, usize)> = vec![]; // (indent, qualname, end_line)
    for (i, line) in lines.iter().enumerate() {
        for rx in &im {
            if let Some(c) = rx.captures(line) { imports.push(c[1].to_string()); }
        }
        for (rx, kind) in &sy {
            if let Some(c) = rx.captures(line) {
                let name = c[1].to_string();
                let ind = indent_of(line);
                while let Some(top) = stack.last() { if top.0 >= ind || top.2 <= i { stack.pop(); } else { break; } }
                let parent = stack.last().map(|t| t.1.clone());
                let qual = match &parent { Some(p) => format!("{p}.{name}"), None => name.clone() };
                let end = unit_end(&lines, i, block_scoped);
                let kind_final = if *kind == "function" && parent.is_some() { "method" } else { kind };
                symbols.push(Symbol { name: name.clone(), qualname: qual.clone(), kind: kind_final.into(), lineno: i + 1, end_lineno: end, parent: parent.clone(), signature: line.trim().chars().take(120).collect() });
                if parent.is_none() { units.push((qual.clone(), i + 1, end)); }
                stack.push((ind, qual, end));
                break;
            }
        }
    }
    imports.sort();
    imports.dedup();
    CodeFacts { language: language.into(), provider: "builtin-generic".into(), symbols, imports, calls: vec![], units, degraded: None }
}
