//! Repository contract and path map: what belongs where, what may be indexed, who may write it, what must never leave.
use crate::util::{glob_match, read_yaml};
use crate::Result;
use serde_json::{json, Map, Value};
use std::path::{Path, PathBuf};

pub const SECRET_CLASS: &str = "secret";
pub const ALWAYS_EXCLUDED_DIRS: &[&str] = &[
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".governance-runtime",
    ".venv",
    "venv",
    "target",
];

#[derive(Debug, Clone)]
pub struct PathDecision {
    pub path: String,
    pub rule_pattern: Option<String>,
    pub attrs: Map<String, Value>,
}

impl PathDecision {
    pub fn class(&self) -> String {
        self.attrs
            .get("class")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown")
            .to_string()
    }
    pub fn is_secret(&self) -> bool {
        self.class() == SECRET_CLASS
            || self.attrs.get("sensitivity").and_then(|v| v.as_str()) == Some("secret")
    }
    /// Never read/indexed: secret-class or a sensitivity class in SECURITY_POLICY.never_index_classes.
    pub fn is_never_index(&self) -> bool {
        self.is_secret()
            || self
                .attrs
                .get("never_index")
                .and_then(|v| v.as_bool())
                .unwrap_or(false)
    }
    pub fn sensitivity(&self) -> String {
        self.str("sensitivity")
    }
    pub fn export_allowed(&self) -> bool {
        self.attrs.get("export").and_then(|v| v.as_str()) == Some("allowed")
    }
    pub fn flag(&self, key: &str) -> bool {
        if self.is_secret() && key.ends_with("_index") {
            return false;
        }
        self.attrs
            .get(key)
            .and_then(|v| v.as_bool())
            .unwrap_or(false)
    }
    pub fn str(&self, key: &str) -> String {
        self.attrs
            .get(key)
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string()
    }
    pub fn namespace(&self) -> String {
        self.str("namespace")
    }
    pub fn default_retrieval(&self) -> bool {
        self.attrs
            .get("default_retrieval")
            .and_then(|v| v.as_bool())
            .unwrap_or(true)
            && !self.is_secret()
    }
}

fn class_defaults(cls: &str) -> Value {
    match cls {
        "source" => {
            json!({"semantic_index": true, "lexical_index": true, "graph_index": true, "code_index": true})
        }
        "test" => {
            json!({"semantic_index": true, "lexical_index": true, "graph_index": true, "code_index": true})
        }
        "authoritative" => {
            json!({"semantic_index": true, "lexical_index": true, "graph_index": true})
        }
        "evidence" => json!({"semantic_index": true, "lexical_index": true, "graph_index": true}),
        "narrative" => json!({"semantic_index": true, "lexical_index": true}),
        "derived" => json!({"semantic_index": false, "lexical_index": false, "graph_index": false}),
        "generated" => {
            json!({"semantic_index": false, "lexical_index": false, "graph_index": false, "mutation": "generated"})
        }
        "historical" => {
            json!({"semantic_index": false, "lexical_index": true, "default_retrieval": false, "mutation": "restricted"})
        }
        "secret" => {
            json!({"semantic_index": false, "lexical_index": false, "graph_index": false, "code_index": false, "default_retrieval": false,
                           "agent_read": "prohibited", "export": "denied", "sensitivity": "secret", "namespace": "secret"})
        }
        "runtime-data" => {
            json!({"semantic_index": false, "lexical_index": false, "graph_index": false})
        }
        "devops" => json!({"semantic_index": true, "lexical_index": true}),
        "tooling" => json!({"semantic_index": true, "lexical_index": true, "code_index": true}),
        _ => json!({}),
    }
}

fn base_defaults() -> Map<String, Value> {
    json!({"class": "unknown", "semantic_index": false, "lexical_index": false, "graph_index": false, "code_index": false,
           "default_retrieval": true, "mutation": "allowed", "agent_read": "allowed", "export": "denied",
           "sensitivity": "internal", "namespace": "unknown"}).as_object().unwrap().clone()
}

/// Sensitivity enforcement inputs (SECURITY_POLICY + DATA_SENSITIVITY + ARCHIVE_POLICY).
#[derive(Debug, Clone, Default)]
pub struct SensitivityRules {
    pub classifications: Vec<(String, String)>, // (pattern, class)
    pub never_index: Vec<String>,
    pub never_export: Vec<String>,
    pub archive_default_retrieval: Option<bool>,
    pub secret_agent_read: Option<String>,
}

pub fn sensitivity_rank(class: &str) -> u8 {
    match class {
        "secret" => 4,
        "restricted" => 3,
        "confidential" => 2,
        "internal" => 1,
        _ => 0,
    }
}

#[derive(Debug, Clone)]
pub struct RepositoryContract {
    pub data: Value,
    pub roots: Vec<(String, String)>,
    pub rules: Vec<Value>,
    pub sensitivity: SensitivityRules,
}

impl RepositoryContract {
    pub fn new(data: Value) -> Self {
        let mut roots = vec![];
        if let Some(m) = data.get("roots").and_then(|r| r.as_object()) {
            for (k, v) in m {
                let s = v.as_str().unwrap_or("").trim_end_matches('/').to_string() + "/";
                roots.push((k.clone(), s));
            }
        }
        let rules = data
            .get("paths")
            .and_then(|p| p.as_array())
            .cloned()
            .unwrap_or_default();
        RepositoryContract {
            data,
            roots,
            rules,
            sensitivity: SensitivityRules::default(),
        }
    }
    pub fn with_sensitivity(mut self, rules: SensitivityRules) -> Self {
        self.sensitivity = rules;
        self
    }
    pub fn load(p: &Path) -> Result<Self> {
        Ok(Self::new(read_yaml(p)?))
    }
    pub fn root(&self, name: &str) -> String {
        self.roots
            .iter()
            .find(|(k, _)| k == name)
            .map(|(_, v)| v.clone())
            .unwrap_or(format!("{name}/"))
    }
    pub fn namespace_for(&self, path: &str) -> String {
        for (name, root) in &self.roots {
            if path.starts_with(root.as_str()) {
                return name.clone();
            }
        }
        "root".to_string()
    }
    /// Ordered rules; later rules override earlier ones. A `secret` classification can never be downgraded.
    pub fn decide(&self, path: &str) -> PathDecision {
        let path = path.replace('\\', "/");
        let path = path.trim_start_matches("./").to_string();
        let mut attrs = base_defaults();
        let mut matched: Option<String> = None;
        let mut secret_locked = false;
        for rule in &self.rules {
            let pat = rule.get("pattern").and_then(|v| v.as_str()).unwrap_or("");
            if pat.is_empty() || !glob_match(pat, &path) {
                continue;
            }
            let cls = rule
                .get("class")
                .and_then(|v| v.as_str())
                .unwrap_or("unknown");
            if secret_locked && cls != SECRET_CLASS {
                continue;
            }
            let mut merged = base_defaults();
            if let Some(cd) = class_defaults(cls).as_object() {
                for (k, v) in cd {
                    merged.insert(k.clone(), v.clone());
                }
            }
            if let Some(r) = rule.as_object() {
                for (k, v) in r {
                    if k != "pattern" {
                        merged.insert(k.clone(), v.clone());
                    }
                }
            }
            attrs = merged;
            matched = Some(pat.to_string());
            if cls == SECRET_CLASS {
                secret_locked = true;
            }
        }
        let ns = attrs
            .get("namespace")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown")
            .to_string();
        if ns == "unknown" || ns.is_empty() {
            attrs.insert("namespace".into(), Value::String(self.namespace_for(&path)));
        }
        // --- sensitivity: DATA_SENSITIVITY classifications (highest class wins) + SECURITY_POLICY never_index / never_export
        let mut sensitivity = attrs
            .get("sensitivity")
            .and_then(|v| v.as_str())
            .unwrap_or("internal")
            .to_string();
        for (pat, cls) in &self.sensitivity.classifications {
            if glob_match(pat, &path) && sensitivity_rank(cls) > sensitivity_rank(&sensitivity) {
                sensitivity = cls.clone();
            }
        }
        if attrs.get("class").and_then(|v| v.as_str()) == Some(SECRET_CLASS) {
            sensitivity = "secret".into();
        }
        attrs.insert("sensitivity".into(), Value::String(sensitivity.clone()));
        if self
            .sensitivity
            .never_index
            .iter()
            .any(|c| c == &sensitivity)
        {
            for k in [
                "semantic_index",
                "lexical_index",
                "graph_index",
                "code_index",
            ] {
                attrs.insert(k.into(), Value::Bool(false));
            }
            attrs.insert("default_retrieval".into(), Value::Bool(false));
            attrs.insert("export".into(), Value::String("denied".into()));
            let ar = if sensitivity == "secret" {
                self.sensitivity
                    .secret_agent_read
                    .clone()
                    .unwrap_or("prohibited".into())
            } else {
                "restricted".into()
            };
            attrs.insert("agent_read".into(), Value::String(ar));
            attrs.insert("never_index".into(), Value::Bool(true));
        }
        if self
            .sensitivity
            .never_export
            .iter()
            .any(|c| c == &sensitivity)
        {
            attrs.insert("export".into(), Value::String("denied".into()));
        }
        if attrs.get("class").and_then(|v| v.as_str()) == Some("historical") {
            if let Some(dr) = self.sensitivity.archive_default_retrieval {
                if attrs.get("default_retrieval").is_none() || matched.is_none() {
                    attrs.insert("default_retrieval".into(), Value::Bool(dr));
                }
            }
        }
        PathDecision {
            path,
            rule_pattern: matched,
            attrs,
        }
    }
    pub fn to_framework_json(&self, framework: &str, version: &str) -> Value {
        let mut paths = Map::new();
        for r in &self.rules {
            if let (Some(pat), Some(obj)) =
                (r.get("pattern").and_then(|v| v.as_str()), r.as_object())
            {
                let mut o = obj.clone();
                o.shift_remove("pattern");
                paths.insert(pat.to_string(), Value::Object(o));
            }
        }
        let mut roots = Map::new();
        for (k, v) in &self.roots {
            roots.insert(k.clone(), Value::String(v.clone()));
        }
        json!({"framework": framework, "version": version, "generated": true, "source": "governance/project/REPOSITORY_CONTRACT.yaml",
               "governance_dir": "governance", "roots": roots, "paths": paths})
    }
}

/// Deterministically list repository files (sorted), skipping VCS/runtime/cache directories.
pub fn iter_repo_files(root: &Path, include_runtime: bool) -> Vec<(PathBuf, String)> {
    let mut out = vec![];
    let walker = walkdir::WalkDir::new(root)
        .sort_by_file_name()
        .into_iter()
        .filter_entry(|e| {
            if e.depth() == 0 {
                return true;
            }
            let name = e.file_name().to_string_lossy();
            if e.file_type().is_dir() {
                if name == ".governance-runtime" {
                    return include_runtime;
                }
                return !ALWAYS_EXCLUDED_DIRS.contains(&name.as_ref());
            }
            true
        });
    for entry in walker.filter_map(|e| e.ok()) {
        if entry.file_type().is_file() && !entry.path_is_symlink() {
            let rel = entry
                .path()
                .strip_prefix(root)
                .unwrap()
                .to_string_lossy()
                .replace('\\', "/");
            out.push((entry.path().to_path_buf(), rel));
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    fn contract() -> RepositoryContract {
        RepositoryContract::new(
            json!({"roots": {"governance": "governance/", "spec": "spec/", "product": "product/", "archive": "archive/"},
            "paths": [{"pattern": "spec/**", "class": "authoritative"}, {"pattern": "product/**", "class": "source"}, {"pattern": "**/.env*", "class": "secret"}, {"pattern": "product/secrets/**", "class": "secret"}, {"pattern": "product/**", "class": "source", "semantic_index": true}, {"pattern": "archive/**", "class": "historical"}]}),
        )
    }
    #[test]
    fn secret_classification_can_never_be_downgraded() {
        let c = contract();
        let d = c.decide("product/secrets/key.pem");
        assert!(
            d.is_secret()
                && !d.flag("semantic_index")
                && !d.flag("lexical_index")
                && d.str("agent_read") == "prohibited"
        );
        assert!(c.decide("product/.env.prod").is_secret());
        let s = c.decide("product/app.py");
        assert_eq!(s.class(), "source");
        assert!(s.flag("code_index") && s.flag("semantic_index"));
        let a = c.decide("archive/old.md");
        assert!(!a.default_retrieval() && a.class() == "historical" && a.flag("lexical_index"));
        assert_eq!(c.decide("spec/x.yaml").namespace(), "spec");
        assert_eq!(c.decide("README.md").class(), "unknown");
    }
}
