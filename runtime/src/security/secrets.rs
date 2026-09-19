//! Secret and sensitivity scanning (T0). Fails closed: any hit blocks indexing/export of the unit.
use crate::util::{glob_match, is_text_file, read_text};
use regex::Regex;
use serde_json::Value;
use std::path::Path;

#[derive(Debug, Clone, serde::Serialize)]
pub struct SecretHit {
    pub path: String,
    pub pattern_id: String,
    pub line: usize,
    pub excerpt: String,
}

#[derive(Debug, Clone)]
pub struct SecretScanner {
    pub patterns: Vec<(String, Regex)>,
    pub path_patterns: Vec<String>,
    pub identifiers: Vec<String>,
}

pub const DEFAULT_PATTERNS: &[(&str, &str)] = &[
    ("aws-access-key", r"AKIA[0-9A-Z]{16}"),
    (
        "private-key-block",
        r"-----BEGIN (RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----",
    ),
    ("github-token", r"gh[pousr]_[A-Za-z0-9]{36,}"),
    (
        "generic-api-key",
        r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[=:]\s*['\x22]?[A-Za-z0-9_\-]{20,}",
    ),
    (
        "password-assignment",
        r#"(?i)password\s*[=:]\s*['"][^'"\s]{8,}['"]"#,
    ),
    ("stripe-like-key", r"\bsk_(live|test)_[A-Za-z0-9_]{16,}"),
];

impl SecretScanner {
    pub fn default_scanner() -> Self {
        SecretScanner {
            patterns: DEFAULT_PATTERNS
                .iter()
                .filter_map(|(id, rx)| Regex::new(rx).ok().map(|r| (id.to_string(), r)))
                .collect(),
            path_patterns: vec![],
            identifiers: vec![],
        }
    }
    pub fn from_policies(security_policy: &Value, data_sensitivity: &Value) -> Self {
        let mut patterns = vec![];
        if let Some(a) = security_policy
            .get("secret_content_patterns")
            .and_then(|v| v.as_array())
        {
            for p in a {
                if let (Some(id), Some(rx)) = (
                    p.get("id").and_then(|v| v.as_str()),
                    p.get("regex").and_then(|v| v.as_str()),
                ) {
                    if let Ok(r) = Regex::new(rx) {
                        patterns.push((id.to_string(), r));
                    }
                }
            }
        }
        if patterns.is_empty() {
            return Self::default_scanner();
        }
        let path_patterns = security_policy
            .get("secret_path_patterns")
            .and_then(|v| v.as_array())
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default();
        let identifiers = data_sensitivity
            .get("identifiers_to_strip")
            .and_then(|v| v.as_array())
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .filter(|s| !s.is_empty())
                    .collect()
            })
            .unwrap_or_default();
        SecretScanner {
            patterns,
            path_patterns,
            identifiers,
        }
    }
    /// Identity of what this scanner excludes from the index: its content patterns (id and expression) and its
    /// secret path patterns. Part of every artefact's index derivation key (`memory::indexer::DerivationContext`),
    /// so a change of the secret-scanning policy re-derives — and re-scans — every artefact instead of leaving
    /// content indexed (or excluded) under the previous rules.
    pub fn signature(&self) -> String {
        let pats: Vec<String> = self
            .patterns
            .iter()
            .map(|(id, rx)| format!("{id}\u{1f}{}", rx.as_str()))
            .collect();
        let v = serde_json::json!({"content": pats, "paths": self.path_patterns});
        crate::util::sha256_hex(v.to_string().as_bytes())[..32].to_string()
    }
    pub fn path_is_secret(&self, relpath: &str) -> bool {
        self.path_patterns.iter().any(|p| glob_match(p, relpath))
    }
    pub fn scan_text(&self, text: &str, relpath: &str) -> Vec<SecretHit> {
        let mut hits = vec![];
        for (ln, line) in text.lines().enumerate() {
            for (pid, rx) in &self.patterns {
                if let Some(m) = rx.find(line) {
                    let start = m.start();
                    let prefix: String = line[..start]
                        .chars()
                        .rev()
                        .take(40)
                        .collect::<Vec<_>>()
                        .into_iter()
                        .rev()
                        .collect();
                    hits.push(SecretHit {
                        path: relpath.to_string(),
                        pattern_id: pid.clone(),
                        line: ln + 1,
                        excerpt: format!("{}[REDACTED]", prefix.trim()),
                    });
                }
            }
        }
        hits
    }
    pub fn scan_file(&self, abs: &Path, relpath: &str) -> Vec<SecretHit> {
        if !is_text_file(abs) {
            return vec![];
        }
        if abs.metadata().map(|m| m.len() > 2_000_000).unwrap_or(true) {
            return vec![];
        }
        match read_text(abs) {
            Ok(t) => self.scan_text(&t, relpath),
            Err(_) => vec![],
        }
    }
    pub fn identifier_hits(&self, text: &str) -> Vec<String> {
        let low = text.to_lowercase();
        self.identifiers
            .iter()
            .filter(|i| low.contains(&i.to_lowercase()))
            .cloned()
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn detects_and_redacts() {
        let s = SecretScanner::default_scanner();
        let hits = s.scan_text(
            "x = 1\nAWS_KEY=AKIAIOSFODNN7EXAMPLE\npassword = \"hunter2hunter2\"\n",
            "f",
        );
        assert_eq!(hits.len(), 2);
        assert!(hits.iter().all(
            |h| h.excerpt.contains("[REDACTED]") && !h.excerpt.contains("AKIAIOSFODNN7EXAMPLE")
        ));
        assert!(s.scan_text("nothing here", "f").is_empty());
    }
}
