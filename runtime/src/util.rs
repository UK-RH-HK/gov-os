//! Deterministic utilities: IO, hashing, glob matching, ids, time, JSON path helpers.
use crate::{GovError, Result};
use regex::Regex;
use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::{Mutex, OnceLock};

pub fn read_text(p: &Path) -> Result<String> {
    fs::read_to_string(p).map_err(|e| GovError::io(&format!("read {}", p.display()), e))
}
pub fn read_bytes(p: &Path) -> Result<Vec<u8>> {
    fs::read(p).map_err(|e| GovError::io(&format!("read {}", p.display()), e))
}
pub fn write_text(p: &Path, s: &str) -> Result<()> {
    if let Some(parent) = p.parent() {
        fs::create_dir_all(parent).map_err(|e| GovError::io(&format!("mkdir {}", parent.display()), e))?;
    }
    fs::write(p, s).map_err(|e| GovError::io(&format!("write {}", p.display()), e))
}
pub fn read_yaml(p: &Path) -> Result<Value> {
    let text = read_text(p)?;
    let v: Value = serde_yaml::from_str(&text).map_err(|e| GovError::new("YAML_ERROR", format!("{}: {e}", p.display())))?;
    Ok(if v.is_null() { json!({}) } else { v })
}
pub fn write_yaml(p: &Path, v: &Value) -> Result<()> {
    let s = to_yaml(v)?;
    write_text(p, &s)
}
pub fn to_yaml(v: &Value) -> Result<String> {
    let raw = serde_yaml::to_string(v)?;
    // YAML 1.1 loaders would read unquoted dates/timestamps as datetime objects; our schemas declare strings.
    static TS: OnceLock<Regex> = OnceLock::new();
    let rx = TS.get_or_init(|| Regex::new(r"^(\s*(?:- )?(?:[A-Za-z_][\w.-]*: )?)(\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2})?)?)\s*$").unwrap());
    let out: Vec<String> = raw.lines().map(|l| match rx.captures(l) { Some(c) => format!("{}'{}'", &c[1], &c[2]), None => l.to_string() }).collect();
    Ok(out.join("\n") + "\n")
}
pub fn read_json(p: &Path) -> Result<Value> {
    let text = read_text(p)?;
    serde_json::from_str(&text).map_err(|e| GovError::new("JSON_ERROR", format!("{}: {e}", p.display())))
}
pub fn write_json(p: &Path, v: &Value) -> Result<()> {
    let s = serde_json::to_string_pretty(&sorted(v))?;
    write_text(p, &(s + "\n"))
}

/// Recursively sort object keys (deterministic serialisation for hashing and tracked manifests).
pub fn sorted(v: &Value) -> Value {
    match v {
        Value::Object(m) => {
            let mut b: BTreeMap<String, Value> = BTreeMap::new();
            for (k, val) in m {
                b.insert(k.clone(), sorted(val));
            }
            let mut out = Map::new();
            for (k, val) in b {
                out.insert(k, val);
            }
            Value::Object(out)
        }
        Value::Array(a) => Value::Array(a.iter().map(sorted).collect()),
        other => other.clone(),
    }
}
pub fn canonical_json(v: &Value) -> String {
    serde_json::to_string(&sorted(v)).unwrap_or_default()
}
pub fn sha256_hex(b: &[u8]) -> String {
    format!("{:x}", Sha256::digest(b))
}
pub fn sha256_text(s: &str) -> String {
    sha256_hex(s.as_bytes())
}
pub fn hash_value(v: &Value) -> String {
    sha256_text(&canonical_json(v))
}
pub fn sha256_file(p: &Path) -> Result<String> {
    Ok(sha256_hex(&read_bytes(p)?))
}

/// Deterministic tree hash: (tree_hash, {relpath: filehash}) skipping excluded globs.
pub fn hash_tree(root: &Path, exclude: &[&str]) -> Result<(String, BTreeMap<String, String>)> {
    let mut files = BTreeMap::new();
    for entry in walkdir::WalkDir::new(root).sort_by_file_name().into_iter().filter_map(|e| e.ok()) {
        if !entry.file_type().is_file() {
            continue;
        }
        let rel = entry.path().strip_prefix(root).unwrap_or(entry.path()).to_string_lossy().replace('\\', "/");
        if exclude.iter().any(|pat| glob_match(pat, &rel)) {
            continue;
        }
        files.insert(rel, sha256_file(entry.path())?);
    }
    let v = serde_json::to_value(&files)?;
    Ok((hash_value(&v), files))
}

pub fn now_iso() -> String {
    chrono::Utc::now().format("%Y-%m-%dT%H:%M:%SZ").to_string()
}
pub fn today() -> String {
    chrono::Utc::now().format("%Y-%m-%d").to_string()
}
pub fn new_session_id() -> String {
    format!("S-{}", &uuid::Uuid::new_v4().simple().to_string()[..12])
}
pub fn short_uuid() -> String {
    uuid::Uuid::new_v4().simple().to_string()[..8].to_string()
}

static GLOB_CACHE: OnceLock<Mutex<BTreeMap<String, Regex>>> = OnceLock::new();

/// gitignore-like glob → regex (supports **, *, ?). Patterns without '/' also match basenames anywhere.
pub fn glob_to_regex(pattern: &str) -> Regex {
    let cache = GLOB_CACHE.get_or_init(|| Mutex::new(BTreeMap::new()));
    if let Some(rx) = cache.lock().unwrap().get(pattern) {
        return rx.clone();
    }
    let mut pat = pattern.trim().to_string();
    if pat.ends_with('/') {
        pat.push_str("**");
    }
    let chars: Vec<char> = pat.chars().collect();
    let mut out = String::from("^");
    let mut i = 0;
    while i < chars.len() {
        let c = chars[i];
        if c == '*' {
            if i + 2 < chars.len() && chars[i + 1] == '*' && chars[i + 2] == '/' {
                out.push_str("(?:.*/)?");
                i += 3;
                continue;
            }
            if i + 1 < chars.len() && chars[i + 1] == '*' {
                out.push_str(".*");
                i += 2;
                continue;
            }
            out.push_str("[^/]*");
        } else if c == '?' {
            out.push_str("[^/]");
        } else if ".+()[]{}^$|\\".contains(c) {
            out.push('\\');
            out.push(c);
        } else {
            out.push(c);
        }
        i += 1;
    }
    out.push('$');
    let rx = Regex::new(&out).unwrap_or_else(|_| Regex::new("^$").unwrap());
    cache.lock().unwrap().insert(pattern.to_string(), rx.clone());
    rx
}

pub fn glob_match(pattern: &str, path: &str) -> bool {
    let path = path.replace('\\', "/");
    let path = path.trim_start_matches("./");
    let pattern = pattern.strip_prefix("./").unwrap_or(pattern);
    if glob_to_regex(pattern).is_match(path) {
        return true;
    }
    let core = pattern.trim_end_matches('/');
    if !core.contains('/') && glob_to_regex(&format!("**/{pattern}")).is_match(path) {
        return true;
    }
    false
}

pub fn deep_get<'a>(v: &'a Value, dotted: &str) -> Option<&'a Value> {
    let mut cur = v;
    for part in dotted.split('.') {
        cur = cur.get(part)?;
    }
    Some(cur)
}
pub fn deep_set(v: &mut Value, dotted: &str, value: Value) {
    let parts: Vec<&str> = dotted.split('.').collect();
    let mut cur = v;
    for part in &parts[..parts.len() - 1] {
        if !cur.is_object() {
            *cur = json!({});
        }
        let m = cur.as_object_mut().unwrap();
        if !m.get(*part).map(|x| x.is_object()).unwrap_or(false) {
            m.insert(part.to_string(), json!({}));
        }
        cur = m.get_mut(*part).unwrap();
    }
    if !cur.is_object() {
        *cur = json!({});
    }
    cur.as_object_mut().unwrap().insert(parts[parts.len() - 1].to_string(), value);
}
pub fn deep_delete(v: &mut Value, dotted: &str) -> bool {
    let parts: Vec<&str> = dotted.split('.').collect();
    let mut cur = v;
    for part in &parts[..parts.len() - 1] {
        match cur.get_mut(*part) {
            Some(x) => cur = x,
            None => return false,
        }
    }
    cur.as_object_mut().map(|m| m.shift_remove(parts[parts.len() - 1]).is_some()).unwrap_or(false)
}
pub fn str_of(v: &Value, key: &str) -> String {
    match v.get(key) {
        Some(Value::String(s)) => s.clone(),
        Some(Value::Number(n)) => n.to_string(),
        Some(Value::Bool(b)) => b.to_string(),
        _ => String::new(),
    }
}
pub fn str_list(v: &Value, key: &str) -> Vec<String> {
    match v.get(key) {
        Some(Value::Array(a)) => a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect(),
        Some(Value::String(s)) => vec![s.clone()],
        _ => vec![],
    }
}
pub fn bool_of(v: &Value, key: &str, default: bool) -> bool {
    v.get(key).and_then(|x| x.as_bool()).unwrap_or(default)
}

/// Next sequential id for a prefix given existing ids (e.g. TASK-0007).
pub fn next_id(prefix: &str, existing: &[String], width: usize) -> String {
    let rx = Regex::new(&format!("^{}-(\\d+)$", regex::escape(prefix))).unwrap();
    let mut mx = 0u64;
    for e in existing {
        if let Some(c) = rx.captures(e) {
            mx = mx.max(c[1].parse::<u64>().unwrap_or(0));
        }
    }
    format!("{}-{:0width$}", prefix, mx + 1, width = width)
}

pub fn is_text_file(p: &Path) -> bool {
    match fs::File::open(p) {
        Ok(mut f) => {
            use std::io::Read;
            let mut buf = [0u8; 2048];
            let n = f.read(&mut buf).unwrap_or(0);
            !buf[..n].contains(&0u8)
        }
        Err(_) => false,
    }
}

pub fn rel_posix(p: &Path, root: &Path) -> String {
    p.strip_prefix(root).unwrap_or(p).to_string_lossy().replace('\\', "/")
}

pub fn copy_dir(src: &Path, dst: &Path) -> Result<()> {
    for entry in walkdir::WalkDir::new(src).into_iter().filter_map(|e| e.ok()) {
        let rel = entry.path().strip_prefix(src).unwrap();
        let target = dst.join(rel);
        if entry.file_type().is_dir() {
            fs::create_dir_all(&target)?;
        } else if entry.file_type().is_file() {
            if let Some(par) = target.parent() {
                fs::create_dir_all(par)?;
            }
            fs::copy(entry.path(), &target)?;
        }
    }
    Ok(())
}

pub fn remove_dir_if_exists(p: &Path) -> Result<()> {
    if p.exists() {
        fs::remove_dir_all(p)?;
    }
    Ok(())
}

pub fn path_join(root: &Path, rel: &str) -> PathBuf {
    root.join(rel.trim_start_matches('/'))
}

pub fn run_cmd(cmd: &[String], cwd: &Path) -> Result<(i32, String, String)> {
    if cmd.is_empty() {
        return Err(GovError::new("USAGE", "empty command"));
    }
    let out = std::process::Command::new(&cmd[0]).args(&cmd[1..]).current_dir(cwd).output();
    match out {
        Ok(o) => Ok((o.status.code().unwrap_or(-1), String::from_utf8_lossy(&o.stdout).to_string(), String::from_utf8_lossy(&o.stderr).to_string())),
        Err(e) => Ok((-1, String::new(), e.to_string())),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn glob_semantics() {
        assert!(glob_match("spec/decisions/**", "spec/decisions/D-1.yaml"));
        assert!(glob_match("**/.env*", "product/.env.local"));
        assert!(glob_match("**/.env*", ".env"));
        assert!(glob_match("*.md", "docs/a/b.md"));
        assert!(!glob_match("spec/**", "product/x.py"));
        assert!(glob_match("archive/", "archive/x/y"));
        assert!(glob_match("governance/kernel/**", "governance/kernel/x"));
        assert!(!glob_match("governance/kernel/**", "governance/kernels/x"));
    }
    #[test]
    fn hashing_is_canonical() {
        let a = json!({"b": 1, "a": [3, {"z": 1, "y": 2}]});
        let b = json!({"a": [3, {"y": 2, "z": 1}], "b": 1});
        assert_eq!(hash_value(&a), hash_value(&b));
        assert_eq!(sha256_text("abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    }
    #[test]
    fn deep_helpers() {
        let mut v = json!({});
        deep_set(&mut v, "a.b.c", json!(1));
        assert_eq!(deep_get(&v, "a.b.c"), Some(&json!(1)));
        assert!(deep_delete(&mut v, "a.b.c"));
        assert_eq!(deep_get(&v, "a.b.c"), None);
        assert_eq!(next_id("TASK", &["TASK-0003".into(), "TASK-0010".into(), "D-0099".into()], 4), "TASK-0011");
    }
}
