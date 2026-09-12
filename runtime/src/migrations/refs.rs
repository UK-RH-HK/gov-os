//! Reference updates after moves: markdown links/citations, Python and JS/TS import paths.
use crate::paths::iter_repo_files;
use crate::util::{is_text_file, read_text, write_text};
use crate::Result;
use std::path::Path;

fn py_module(path: &str) -> Option<String> {
    let p = path.strip_suffix(".py")?;
    let p = p.strip_suffix("/__init__").unwrap_or(p);
    Some(p.replace('/', "."))
}

/// Rewrite references to moved files across text files. Returns changed file paths.
pub fn update_references(root: &Path, moves: &[(String, String)]) -> Result<Vec<String>> { update_references_opts(root, moves, true, &[]) }

/// `relativise_moved`: also re-relativise links inside moved markdown files; `skip`: files not to touch (e.g. restored from a snapshot).
pub fn update_references_opts(root: &Path, moves: &[(String, String)], relativise_moved: bool, skip: &[String]) -> Result<Vec<String>> {
    let mut changed = vec![];
    if moves.is_empty() { return Ok(changed); }
    // links inside moved markdown files are re-relativised from the new location
    let link_rx = regex::Regex::new(r"\]\(([^)#\s]+)((?:#[^)]*)?)\)").unwrap();
    for (from, to) in moves {
        if !relativise_moved || !to.ends_with(".md") || !root.join(to).exists() { continue; }
        let Ok(text) = read_text(&root.join(to)) else { continue };
        let old_dir = Path::new(from).parent().map(|d| d.to_string_lossy().to_string()).unwrap_or_default();
        let new_dir = Path::new(to).parent().map(|d| d.to_string_lossy().to_string()).unwrap_or_default();
        let new_text = link_rx.replace_all(&text, |c: &regex::Captures| {
            let target = &c[1];
            if target.starts_with("http") || target.starts_with('/') || target.starts_with("mailto:") { return c[0].to_string(); }
            let abs = normalize_rel(&format!("{}/{}", old_dir, target));
            // if the target itself moved, point at its new location
            let abs = moves.iter().find(|(f, _)| *f == abs).map(|(_, t)| t.clone()).unwrap_or(abs);
            format!("]({}{})", relative_path(&new_dir, &abs), &c[2])
        }).to_string();
        if new_text != text { write_text(&root.join(to), &new_text)?; changed.push(to.clone()); }
    }
    for (abs, rel) in iter_repo_files(root, false) {
        if !is_text_file(&abs) || rel.starts_with(".git") { continue; }
        if rel.starts_with("spec/audits/GOVERNANCE-ADOPTION/") || rel.starts_with("governance/kernel/") || rel.starts_with("governance/generated/") || skip.contains(&rel) { continue; }
        let Ok(text) = read_text(&abs) else { continue };
        let mut new_text = text.clone();
        for (from, to) in moves {
            if from == to { continue; }
            // 1. exact repo-relative path occurrences (links, citations, config)
            if new_text.contains(from.as_str()) { new_text = new_text.replace(from.as_str(), to); }
            // 2. relative markdown links from this file's directory
            let dir = Path::new(&rel).parent().map(|d| d.to_string_lossy().to_string()).unwrap_or_default();
            if !dir.is_empty() && from.starts_with(&format!("{dir}/")) {
                let rel_from = &from[dir.len() + 1..];
                let rel_to = relative_path(&dir, to);
                for pat in [format!("]({rel_from})"), format!("](./{rel_from})")] { if new_text.contains(&pat) { new_text = new_text.replace(&pat, &format!("]({rel_to})")); } }
            }
            // 3. python module paths
            if let (Some(mf), Some(mt)) = (py_module(from), py_module(to)) {
                for (a, b) in [(format!("import {mf}"), format!("import {mt}")), (format!("from {mf} import"), format!("from {mt} import")), (format!("from {mf}.")
                    , format!("from {mt}."))] { if new_text.contains(&a) { new_text = new_text.replace(&a, &b); } }
            }
            // 4. JS/TS relative imports
            if rel.ends_with(".ts") || rel.ends_with(".js") || rel.ends_with(".tsx") || rel.ends_with(".jsx") {
                let stem_from = from.trim_end_matches(".ts").trim_end_matches(".js").trim_end_matches(".tsx").to_string();
                let rel_import = relative_path(&dir, &stem_from);
                let rel_import = if rel_import.starts_with('.') { rel_import } else { format!("./{rel_import}") };
                if new_text.contains(&format!("'{rel_import}'")) || new_text.contains(&format!("\"{rel_import}\"")) {
                    let stem_to = to.trim_end_matches(".ts").trim_end_matches(".js").trim_end_matches(".tsx").to_string();
                    let new_import = relative_path(&dir, &stem_to);
                    let new_import = if new_import.starts_with('.') { new_import } else { format!("./{new_import}") };
                    new_text = new_text.replace(&format!("'{rel_import}'"), &format!("'{new_import}'")).replace(&format!("\"{rel_import}\""), &format!("\"{new_import}\""));
                }
            }
        }
        if new_text != text { write_text(&abs, &new_text)?; changed.push(rel); }
    }
    Ok(changed)
}

fn normalize_rel(p: &str) -> String {
    let mut out: Vec<&str> = vec![];
    for seg in p.split('/') { match seg { "" | "." => {}, ".." => { out.pop(); }, s => out.push(s) } }
    out.join("/")
}

pub fn relative_path(from_dir: &str, to: &str) -> String {
    let f: Vec<&str> = from_dir.split('/').filter(|s| !s.is_empty()).collect();
    let t: Vec<&str> = to.split('/').filter(|s| !s.is_empty()).collect();
    let mut i = 0;
    while i < f.len() && i < t.len() && f[i] == t[i] { i += 1; }
    let mut parts: Vec<String> = vec!["..".to_string(); f.len() - i];
    parts.extend(t[i..].iter().map(|s| s.to_string()));
    if parts.is_empty() { ".".into() } else { parts.join("/") }
}

/// Find broken markdown links (relative paths that do not resolve) across the tree.
pub fn broken_links(root: &Path) -> Vec<(String, String)> {
    let rx = regex::Regex::new(r"\]\(([^)#\s]+)(?:#[^)]*)?\)").unwrap();
    let mut out = vec![];
    for (abs, rel) in iter_repo_files(root, false) {
        if !rel.ends_with(".md") { continue; }
        let Ok(text) = read_text(&abs) else { continue };
        let dir = Path::new(&rel).parent().unwrap_or(Path::new(""));
        for c in rx.captures_iter(&text) {
            let target = &c[1];
            if target.starts_with("http") || target.starts_with("mailto:") { continue; }
            let candidate = if target.starts_with('/') { root.join(target.trim_start_matches('/')) } else { root.join(dir).join(target) };
            let norm = normalize(&candidate.to_string_lossy());
            if !Path::new(&norm).exists() { out.push((rel.clone(), target.to_string())); }
        }
    }
    out
}

fn normalize(p: &str) -> String {
    let mut out: Vec<&str> = vec![];
    for seg in p.split('/') { match seg { "" | "." => { if out.is_empty() && p.starts_with('/') { out.push(""); } }, ".." => { out.pop(); }, s => out.push(s) } }
    let s = out.join("/");
    if p.starts_with('/') && !s.starts_with('/') { format!("/{s}") } else { s }
}
