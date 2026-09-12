//! Embeds the kernel payload (framework/, migrations/, tools/) into the binary so `gov init` works without the
//! source checkout. Only file contents are embedded; no build-machine paths reach the binary.
use std::path::{Path, PathBuf};

fn walk(dir: &Path, prefix: &str, out: &mut Vec<(String, PathBuf)>) {
    let mut entries: Vec<_> = std::fs::read_dir(dir)
        .map(|rd| rd.filter_map(|e| e.ok()).collect())
        .unwrap_or_default();
    entries.sort_by_key(|e| e.file_name());
    for e in entries {
        let p = e.path();
        let name = e.file_name().to_string_lossy().to_string();
        let rel = if prefix.is_empty() {
            name.clone()
        } else {
            format!("{prefix}/{name}")
        };
        if p.is_dir() {
            walk(&p, &rel, out);
        } else if p.is_file() {
            out.push((rel, p));
        }
    }
}

/// Minimal extraction of `"release_commit": "<hex>"` without a JSON dependency in the build script.
fn serde_json_lite_commit(text: &str) -> Option<String> {
    let idx = text.find("\"release_commit\"")?;
    let rest = &text[idx + "\"release_commit\"".len()..];
    let start = rest.find('"')? + 1;
    let end = rest[start..].find('"')? + start;
    let c = rest[start..end].trim().to_string();
    if c.is_empty() {
        None
    } else {
        Some(c)
    }
}

fn main() {
    let manifest_dir = PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").unwrap());
    let root = manifest_dir.join("..");
    let mut files: Vec<(String, PathBuf)> = vec![];
    walk(&root.join("framework"), "", &mut files);
    walk(&root.join("migrations"), "migrations", &mut files);
    walk(&root.join("tools"), "tools", &mut files);
    files.retain(|(rel, _)| {
        !rel.ends_with("README.md") || rel.starts_with("migrations") || rel.starts_with("tools")
    });
    let version = std::fs::read_to_string(root.join("framework").join("KERNEL.yaml"))
        .ok()
        .and_then(|t| {
            t.lines().find(|l| l.starts_with("version:")).map(|l| {
                l.trim_start_matches("version:")
                    .trim()
                    .trim_matches('"')
                    .to_string()
            })
        })
        .unwrap_or("0.0.0".into());
    // release provenance: the release manifest's commit when this tree carries the release for this version,
    // otherwise the git HEAD of the checkout (never a build-machine path)
    let manifest = root
        .join("release")
        .join("releases")
        .join(&version)
        .join("manifest.json");
    let commit = std::fs::read_to_string(&manifest)
        .ok()
        .and_then(|t| serde_json_lite_commit(&t))
        .or_else(|| {
            std::process::Command::new("git")
                .args(["rev-parse", "HEAD"])
                .current_dir(&root)
                .output()
                .ok()
                .filter(|o| o.status.success())
                .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
                .filter(|c| !c.is_empty())
        })
        .unwrap_or_else(|| "unknown".into());
    let mut src = String::new();
    src.push_str(&format!(
        "pub const EMBEDDED_VERSION: &str = {:?};\n",
        version
    ));
    src.push_str(&format!(
        "pub const EMBEDDED_COMMIT: &str = {:?};\n",
        commit
    ));
    src.push_str("pub static EMBEDDED_FILES: &[(&str, &[u8])] = &[\n");
    for (rel, path) in &files {
        src.push_str(&format!(
            "    ({:?}, include_bytes!({:?})),\n",
            rel,
            path.canonicalize().unwrap().to_string_lossy()
        ));
    }
    src.push_str("];\n");
    let out = PathBuf::from(std::env::var("OUT_DIR").unwrap()).join("embedded_kernel.rs");
    std::fs::write(&out, src).unwrap();
    for d in ["framework", "migrations", "tools"] {
        println!("cargo:rerun-if-changed={}", root.join(d).display());
    }
    println!(
        "cargo:rerun-if-changed={}",
        root.join(".git").join("HEAD").display()
    );
    println!(
        "cargo:rerun-if-changed={}",
        root.join(".git").join("refs").join("heads").display()
    );
    println!("cargo:rerun-if-changed={}", manifest.display());
    for (_, path) in &files {
        println!("cargo:rerun-if-changed={}", path.display());
    }
}
