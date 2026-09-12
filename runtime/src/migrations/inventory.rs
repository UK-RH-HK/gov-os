//! A1 cold deterministic inventory: existence before interpretation; no semantic memory involved.
use crate::paths::iter_repo_files;
use crate::util::{glob_match, is_text_file, sha256_file};
use serde_json::{json, Value};
use std::collections::HashSet;
use std::path::Path;

pub const PACKAGE_MANIFESTS: &[&str] = &[
    "Cargo.toml",
    "package.json",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "CMakeLists.txt",
    "Makefile",
    "Gemfile",
    "mix.exs",
    "composer.json",
];
pub const ENTRYPOINTS: &[&str] = &[
    "main.py",
    "app.py",
    "__main__.py",
    "manage.py",
    "wsgi.py",
    "asgi.py",
    "src/main.rs",
    "main.rs",
    "main.go",
    "index.js",
    "index.ts",
    "server.js",
    "server.ts",
    "app.js",
    "app.ts",
    "src/index.ts",
    "src/index.js",
    "Main.java",
    "Program.cs",
];
pub const CHAT_STORE_PATTERNS: &[&str] = &[
    "**/chat_history*",
    "**/chat-history*",
    "**/conversations*",
    "**/sessions*.jsonl",
    "**/.chat/**",
    "**/chat*.db",
    "**/chat*.sqlite*",
    "**/memory/*.sqlite*",
    "**/memory/*.db",
    "**/agent_memory*",
    "**/*.chat.json",
];
pub const INDEX_STORE_PATTERNS: &[&str] = &[
    "**/.index/**",
    "**/vectors.json",
    "**/vectors.npy",
    "**/embeddings*",
    "**/*.faiss",
    "**/chroma/**",
    "**/.vectorstore/**",
    "**/index.json",
    "**/*.index",
];
pub const PROVIDER_RULE_PATTERNS: &[&str] = &[
    "**/.cursorrules",
    "**/.cursor/rules/**",
    "**/.windsurfrules",
    "**/.clinerules",
    "**/.aider.conf.yml",
    "**/.aiderrules",
    "**/AGENTS.md",
    "**/AGENT_RULES*.md",
    "**/AGENT.md",
    "**/CLAUDE.md",
    "**/GEMINI.md",
    "**/.github/copilot-instructions.md",
    "**/.copilot/**",
    "**/.continue/**",
    "**/RULES.md",
    "**/*.rules.md",
    "**/.agent/**",
    "**/.ai/**",
    "**/ai-rules*",
    "**/prompts/system*.md",
    "**/.roo/**",
    "**/.roomodes",
];
pub const OLD_GOVERNANCE_PATTERNS: &[&str] = &[
    "**/DECISIONS.md",
    "**/decisions/**",
    "**/adr/**",
    "**/ADR/**",
    "**/docs/governance/**",
    "**/GOVERNANCE.md",
    "**/CONSTITUTION*.md",
    "**/framework*.md",
    "**/LESSONS.md",
    "**/lessons/**",
    "**/*decision*.md",
    "**/*Decision*.md",
    "**/*DECISION*.md",
    "**/*lesson*.md",
    "**/*Lesson*.md",
    "**/*LESSON*.md",
];
pub const GENERATED_PATTERNS: &[&str] = &[
    "**/build/**",
    "**/dist/**",
    "**/*.min.js",
    "**/*.pyc",
    "**/coverage/**",
    "**/.coverage",
    "**/*.egg-info/**",
    "**/out/**",
];
pub const CI_PATTERNS: &[&str] = &[
    "**/.github/workflows/**",
    "**/.gitlab-ci.yml",
    "**/Jenkinsfile",
    "**/Dockerfile",
    "**/docker-compose*.yml",
    "**/.circleci/**",
    "**/deploy/**",
    "**/devops/**",
    "**/infra/**",
    "**/terraform/**",
    "**/k8s/**",
    "**/helm/**",
];

pub fn language(ext: &str) -> Option<&'static str> {
    crate::capabilities::ecosystems::language_for_ext(ext)
}

fn is_test_path(rel: &str) -> bool {
    let name = rel.rsplit('/').next().unwrap_or(rel);
    rel.contains("/tests/")
        || rel.starts_with("tests/")
        || rel.contains("/test/")
        || rel.starts_with("test/")
        || rel.contains("__tests__")
        || rel.contains("/spec/") && (name.ends_with(".rb") || name.ends_with(".js"))
        || name.starts_with("test_")
        || name.ends_with("_test.py")
        || name.ends_with("_test.go")
        || name.ends_with(".test.ts")
        || name.ends_with(".test.js")
        || name.ends_with(".spec.ts")
        || name.ends_with(".spec.js")
        || name.ends_with("Test.java")
        || name.ends_with("_spec.rb")
}

pub const REPO_CONFIG_FILES: &[&str] = &[
    ".gitignore",
    ".gitattributes",
    ".gitmodules",
    ".editorconfig",
    ".dockerignore",
    ".npmrc",
    ".nvmrc",
    ".python-version",
    ".tool-versions",
    ".ruby-version",
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "NOTICE",
    "CODEOWNERS",
    ".prettierrc",
    ".eslintrc",
    ".eslintrc.json",
    ".babelrc",
    "tsconfig.json",
    "rustfmt.toml",
    "clippy.toml",
    ".rustfmt.toml",
    "Cargo.lock",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "uv.lock",
    "go.sum",
    ".pre-commit-config.yaml",
    "tox.ini",
    "mypy.ini",
    "pytest.ini",
    ".flake8",
    ".mailmap",
];

pub fn detect_kinds(rel: &str, abs: &Path) -> Vec<&'static str> {
    let mut kinds = vec![];
    let name = rel.rsplit('/').next().unwrap_or(rel);
    if REPO_CONFIG_FILES.contains(&name) {
        kinds.push("config");
    }
    let ext = Path::new(rel)
        .extension()
        .map(|e| e.to_string_lossy().to_lowercase())
        .unwrap_or_default();
    if PACKAGE_MANIFESTS.contains(&name) {
        kinds.push("package_manifest");
    }
    if ENTRYPOINTS
        .iter()
        .any(|e| rel == *e || rel.ends_with(&format!("/{e}")))
    {
        kinds.push("entrypoint");
    }
    if CHAT_STORE_PATTERNS.iter().any(|p| glob_match(p, rel)) {
        kinds.push("chat_store");
    }
    if INDEX_STORE_PATTERNS.iter().any(|p| glob_match(p, rel)) {
        kinds.push("index_store");
    }
    if PROVIDER_RULE_PATTERNS.iter().any(|p| glob_match(p, rel)) {
        kinds.push("provider_rules");
    }
    if OLD_GOVERNANCE_PATTERNS.iter().any(|p| glob_match(p, rel))
        && !rel.starts_with("spec/")
        && !rel.starts_with("governance/")
    {
        kinds.push("old_governance");
    }
    if GENERATED_PATTERNS.iter().any(|p| glob_match(p, rel)) {
        kinds.push("generated");
    }
    if CI_PATTERNS.iter().any(|p| glob_match(p, rel)) {
        kinds.push("devops");
    }
    if matches!(ext.as_str(), "db" | "sqlite" | "sqlite3") {
        kinds.push("database");
    }
    if is_test_path(rel) && language(&ext).is_some() {
        kinds.push("test");
    }
    if language(&ext).is_some() && !kinds.contains(&"test") {
        kinds.push("source");
    }
    if matches!(ext.as_str(), "md" | "rst" | "txt" | "adoc") {
        kinds.push("doc");
    }
    if matches!(
        ext.as_str(),
        "yaml" | "yml" | "toml" | "ini" | "cfg" | "json" | "env"
    ) && !kinds.contains(&"package_manifest")
    {
        kinds.push("config");
    }
    if matches!(ext.as_str(), "csv" | "parquet" | "jsonl" | "tsv" | "xlsx")
        || rel.starts_with("data/")
        || rel.contains("/data/")
        || rel.contains("/fixtures/")
    {
        kinds.push("data");
    }
    if rel.starts_with("spec/")
        || rel.contains("/spec/") && ext == "md"
        || rel.contains("/specs/")
        || name.to_lowercase().contains("spec") && ext == "md"
        || name.to_lowercase().contains("requirement")
        || name.to_lowercase().contains("architecture")
    {
        kinds.push("spec_doc");
    }
    if rel.contains("research") || rel.contains("experiment") {
        kinds.push("research");
    }
    if rel.contains("report") || rel.contains("audit") {
        kinds.push("report");
    }
    if abs.is_file() && !is_text_file(abs) {
        kinds.push("binary");
    }
    if kinds.is_empty() {
        kinds.push("unknown");
    }
    kinds
}

pub fn git_tracked(root: &Path) -> HashSet<String> {
    let out = std::process::Command::new("git")
        .args(["ls-files", "-z"])
        .current_dir(root)
        .output();
    match out {
        Ok(o) if o.status.success() => String::from_utf8_lossy(&o.stdout)
            .split('\0')
            .filter(|s| !s.is_empty())
            .map(|s| s.to_string())
            .collect(),
        _ => HashSet::new(),
    }
}

/// Deterministic inventory of every file (sorted), with kinds, hash, size and git tracking.
pub fn inventory(root: &Path, scanner: &crate::security::secrets::SecretScanner) -> Vec<Value> {
    let tracked = git_tracked(root);
    let mut out = vec![];
    for (abs, rel) in iter_repo_files(root, false) {
        let mut kinds = detect_kinds(&rel, &abs);
        let size = abs.metadata().map(|m| m.len()).unwrap_or(0);
        let secret_path = scanner.path_is_secret(&rel);
        let secret_hits = if !secret_path && !kinds.contains(&"binary") {
            scanner.scan_file(&abs, &rel)
        } else {
            vec![]
        };
        if secret_path || !secret_hits.is_empty() {
            kinds.push("secret");
        }
        let hash = if kinds.contains(&"secret") {
            "<not-hashed:secret>".to_string()
        } else {
            sha256_file(&abs).unwrap_or_default()
        };
        out.push(json!({"path": rel, "size": size, "hash": hash, "git_tracked": tracked.contains(&rel), "kinds": kinds, "secret_patterns": secret_hits.iter().map(|h| h.pattern_id.clone()).collect::<HashSet<_>>().into_iter().collect::<Vec<_>>(), "ext": Path::new(&rel).extension().map(|e| e.to_string_lossy().to_string()).unwrap_or_default()}));
    }
    out
}

pub fn summary(items: &[Value]) -> Value {
    let mut by_kind: std::collections::BTreeMap<String, usize> = std::collections::BTreeMap::new();
    for i in items {
        for k in i["kinds"].as_array().cloned().unwrap_or_default() {
            *by_kind
                .entry(k.as_str().unwrap_or("").to_string())
                .or_insert(0) += 1;
        }
    }
    json!({"files": items.len(), "tracked": items.iter().filter(|i| i["git_tracked"].as_bool().unwrap_or(false)).count(), "by_kind": by_kind, "bytes": items.iter().map(|i| i["size"].as_u64().unwrap_or(0)).sum::<u64>()})
}
