//! Ecosystem detection: resolve native build/test/lint/format/metadata tooling for the governed project's languages.
//! Absence of a native tool is a capability gap (recorded), never a crash. The Governance OS imposes no language.
use serde_json::{json, Value};
use std::path::Path;

pub struct EcosystemDef { pub id: &'static str, pub manifests: &'static [&'static str], pub languages: &'static [&'static str],
    pub build: &'static [&'static str], pub test: &'static [&'static str], pub lint: &'static [&'static str], pub format: &'static [&'static str], pub metadata: &'static [&'static str], pub required_binary: &'static str }

pub const ECOSYSTEMS: &[EcosystemDef] = &[
    EcosystemDef { id: "rust-cargo", manifests: &["Cargo.toml"], languages: &["rust"], build: &["cargo", "build"], test: &["cargo", "test"], lint: &["cargo", "clippy"], format: &["cargo", "fmt", "--check"], metadata: &["cargo", "metadata", "--format-version", "1", "--no-deps"], required_binary: "cargo" },
    EcosystemDef { id: "python", manifests: &["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt"], languages: &["python"], build: &[], test: &["python3", "-m", "pytest", "-q"], lint: &["python3", "-m", "pyflakes", "."], format: &[], metadata: &[], required_binary: "python3" },
    EcosystemDef { id: "node-npm", manifests: &["package.json"], languages: &["javascript", "typescript"], build: &["npm", "run", "build"], test: &["npm", "test"], lint: &["npm", "run", "lint"], format: &[], metadata: &[], required_binary: "npm" },
    EcosystemDef { id: "go", manifests: &["go.mod"], languages: &["go"], build: &["go", "build", "./..."], test: &["go", "test", "./..."], lint: &["go", "vet", "./..."], format: &["gofmt", "-l", "."], metadata: &["go", "list", "-m", "-json"], required_binary: "go" },
    EcosystemDef { id: "cmake", manifests: &["CMakeLists.txt"], languages: &["c", "cpp"], build: &["cmake", "--build", "build"], test: &["ctest", "--test-dir", "build"], lint: &[], format: &["clang-format", "--dry-run"], metadata: &[], required_binary: "cmake" },
    EcosystemDef { id: "make", manifests: &["Makefile"], languages: &["c", "cpp", "mixed"], build: &["make"], test: &["make", "test"], lint: &[], format: &[], metadata: &[], required_binary: "make" },
    EcosystemDef { id: "maven", manifests: &["pom.xml"], languages: &["java"], build: &["mvn", "-q", "compile"], test: &["mvn", "-q", "test"], lint: &[], format: &[], metadata: &[], required_binary: "mvn" },
    EcosystemDef { id: "gradle", manifests: &["build.gradle", "build.gradle.kts"], languages: &["java", "kotlin"], build: &["gradle", "build"], test: &["gradle", "test"], lint: &[], format: &[], metadata: &[], required_binary: "gradle" },
    EcosystemDef { id: "dotnet", manifests: &["*.csproj", "*.sln"], languages: &["csharp"], build: &["dotnet", "build"], test: &["dotnet", "test"], lint: &[], format: &["dotnet", "format", "--verify-no-changes"], metadata: &[], required_binary: "dotnet" },
    EcosystemDef { id: "ruby-bundler", manifests: &["Gemfile"], languages: &["ruby"], build: &[], test: &["bundle", "exec", "rake", "test"], lint: &[], format: &[], metadata: &[], required_binary: "bundle" },
    EcosystemDef { id: "elixir-mix", manifests: &["mix.exs"], languages: &["elixir"], build: &["mix", "compile"], test: &["mix", "test"], lint: &[], format: &["mix", "format", "--check-formatted"], metadata: &[], required_binary: "mix" },
];

pub fn binary_available(name: &str) -> bool {
    let Ok(path) = std::env::var("PATH") else { return false };
    std::env::split_paths(&path).any(|d| d.join(name).is_file())
}

fn has_manifest(root: &Path, pattern: &str) -> Option<String> {
    if let Some(ext) = pattern.strip_prefix("*") {
        if let Ok(rd) = std::fs::read_dir(root) {
            let mut names: Vec<String> = rd.filter_map(|e| e.ok()).map(|e| e.file_name().to_string_lossy().to_string()).filter(|n| n.ends_with(ext)).collect();
            names.sort();
            return names.into_iter().next();
        }
        return None;
    }
    if root.join(pattern).is_file() { Some(pattern.to_string()) } else { None }
}

/// Detect ecosystems at `root` and (one level down) in common product roots.
pub fn detect(root: &Path, product_roots: &[String]) -> Value {
    let mut found: Vec<Value> = vec![];
    let mut dirs = vec![("".to_string(), root.to_path_buf())];
    if let Ok(rd) = std::fs::read_dir(root) {
        let mut subs: Vec<_> = rd.filter_map(|e| e.ok()).filter(|e| e.path().is_dir()).map(|e| e.path()).filter(|p| { let n = p.file_name().unwrap().to_string_lossy().to_string(); !n.starts_with('.') && !crate::paths::ALWAYS_EXCLUDED_DIRS.contains(&n.as_str()) && !["governance", "spec", "archive", "docs"].contains(&n.as_str()) }).collect();
        subs.sort();
        for s in subs { dirs.push((format!("{}/", s.file_name().unwrap().to_string_lossy()), s)); }
    }
    for pr in product_roots {
        let p = root.join(pr.trim_end_matches('/'));
        if p.is_dir() && p != root { dirs.push((pr.clone(), p.clone())); }
        if let Ok(rd) = std::fs::read_dir(&p) {
            let mut subs: Vec<_> = rd.filter_map(|e| e.ok()).filter(|e| e.path().is_dir()).map(|e| e.path()).collect();
            subs.sort();
            for s in subs { dirs.push((format!("{}{}/", pr, s.file_name().unwrap().to_string_lossy()), s)); }
        }
    }
    for eco in ECOSYSTEMS {
        for (prefix, dir) in &dirs {
            for m in eco.manifests {
                if let Some(mf) = has_manifest(dir, m) {
                    let avail = binary_available(eco.required_binary);
                    let cmd = |c: &[&str]| -> Value { if c.is_empty() { Value::Null } else { json!({"command": c, "available": avail}) } };
                    if found.iter().any(|f| f["id"] == eco.id && f["manifest"] == format!("{prefix}{mf}")) { break; }
                    found.push(json!({"id": eco.id, "manifest": format!("{prefix}{mf}"), "dir": prefix.trim_end_matches('/'), "languages": eco.languages,
                        "required_binary": eco.required_binary, "available": avail,
                        "build": cmd(eco.build), "test": cmd(eco.test), "lint": cmd(eco.lint), "format": cmd(eco.format), "metadata": cmd(eco.metadata),
                        "gap": if avail { Value::Null } else { json!(format!("native tool '{}' not on PATH: capability gap (raise tooling task or human gate)", eco.required_binary)) }}));
                    break;
                }
            }
        }
    }
    json!({"ecosystems": found, "count": found.len()})
}

pub fn language_for_ext(ext: &str) -> Option<&'static str> {
    Some(match ext {
        "py" => "python", "rs" => "rust", "js" | "mjs" | "cjs" | "jsx" => "javascript", "ts" | "tsx" => "typescript", "go" => "go",
        "c" | "h" => "c", "cc" | "cpp" | "cxx" | "hpp" | "hh" => "cpp", "java" => "java", "kt" | "kts" => "kotlin", "cs" => "csharp",
        "rb" => "ruby", "ex" | "exs" => "elixir", "swift" => "swift", "sh" | "bash" => "shell", "sql" => "sql", "scala" => "scala", "php" => "php",
        _ => return None,
    })
}
