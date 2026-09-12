//! Kernel payload: build from the canonical repo, install into a consumer, verify immutability.
use crate::util::{
    copy_dir, hash_tree, hash_value, now_iso, read_json, read_yaml, remove_dir_if_exists,
    write_json,
};
use crate::{GovError, Result, FRAMEWORK_NAME, VERSION};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

pub const KERNEL_MANIFEST: &str = "KERNEL_MANIFEST.json";

/// The kernel payload compiled into the binary (build.rs embeds framework/, migrations/ and tools/), so a single
/// `gov` executable can install a kernel on any machine without the source checkout (D-0002, verifier M6).
pub mod embedded {
    include!(concat!(env!("OUT_DIR"), "/embedded_kernel.rs"));
    pub fn version() -> &'static str {
        EMBEDDED_VERSION
    }
    /// The framework commit this payload was built from (release manifest commit when the build tree carries the
    /// release, else the git HEAD at build time; "unknown" outside a checkout).
    pub fn commit() -> &'static str {
        EMBEDDED_COMMIT
    }
    pub fn files() -> &'static [(&'static str, &'static [u8])] {
        EMBEDDED_FILES
    }
}

/// Materialise the embedded payload into a per-user cache directory (idempotent, content-addressed).
pub fn embedded_kernel_dir() -> Result<PathBuf> {
    let files = embedded::files();
    let mut listing: Vec<(String, String)> = files
        .iter()
        .map(|(p, b)| (p.to_string(), crate::util::sha256_hex(b)))
        .collect();
    listing.sort();
    let id = crate::util::sha256_text(&serde_json::to_string(&listing)?);
    let base = std::env::var("GOV_KERNEL_CACHE")
        .ok()
        .map(PathBuf::from)
        .or_else(|| {
            std::env::var("XDG_CACHE_HOME")
                .ok()
                .map(|c| PathBuf::from(c).join("gov"))
        })
        .or_else(|| {
            std::env::var("HOME")
                .ok()
                .map(|h| PathBuf::from(h).join(".cache").join("gov"))
        })
        .unwrap_or(std::env::temp_dir().join("gov-cache"));
    let dir = base
        .join("kernels")
        .join(format!("{}-{}", embedded::version(), &id[..12]));
    if dir.join("KERNEL.yaml").exists() && dir.join(".complete").exists() {
        return Ok(dir);
    }
    let staging = base
        .join("kernels")
        .join(format!(".staging-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&staging);
    for (rel, bytes) in files {
        let p = staging.join(rel);
        if let Some(d) = p.parent() {
            std::fs::create_dir_all(d)?;
        }
        std::fs::write(&p, bytes)?;
    }
    std::fs::write(staging.join(".complete"), id.as_bytes())?;
    if dir.exists() {
        let _ = std::fs::remove_dir_all(&staging);
    } else if let Err(e) = std::fs::rename(&staging, &dir) {
        let _ = std::fs::remove_dir_all(&staging);
        if !dir.join(".complete").exists() {
            return Err(GovError::io("materialise embedded kernel", e));
        }
    }
    Ok(dir)
}

/// The canonical repository root, only when explicitly provided (GOV_CANONICAL_ROOT); no build path is baked in.
pub fn canonical_root() -> Option<PathBuf> {
    let c = std::env::var("GOV_CANONICAL_ROOT")
        .ok()
        .map(PathBuf::from)?;
    if c.join("framework").join("KERNEL.yaml").exists() {
        Some(c.canonicalize().unwrap_or(c))
    } else {
        None
    }
}

/// Kernel source precedence: explicit --source > GOV_CANONICAL_ROOT (developer checkout) > embedded payload.
pub fn resolve_kernel_source(source: Option<&Path>) -> Result<PathBuf> {
    let src = match source {
        Some(s) => s.to_path_buf(),
        None => match canonical_root() {
            Some(r) => r.join("framework"),
            None => embedded_kernel_dir()?,
        },
    };
    for cand in [src.clone(), src.join("kernel"), src.join("framework")] {
        if cand.join("KERNEL.yaml").exists() {
            return Ok(cand);
        }
    }
    Err(GovError::new(
        "KERNEL_SOURCE_NOT_FOUND",
        format!("no kernel payload found at {}", src.display()),
    ))
}

/// Whether `src` is the materialised embedded payload (per-user cache).
pub fn is_embedded_dir(src: &Path) -> bool {
    let s = src.to_string_lossy();
    (s.contains("/kernels/") && s.contains(".cache"))
        || s.contains("gov-cache")
        || std::env::var("GOV_KERNEL_CACHE")
            .map(|c| !c.is_empty() && s.starts_with(&c))
            .unwrap_or(false)
}

/// The framework release commit for a kernel source (verifier M-N1): the release manifest next to `kernel/`, the
/// commit embedded in this binary for the embedded payload, or the HEAD of the checkout containing a framework/ dir.
/// Never the consumer repository's HEAD.
pub fn release_commit_for_source(src: &Path) -> String {
    if let Some(parent) = src.parent() {
        let m = parent.join("manifest.json");
        if m.exists() {
            if let Ok(v) = crate::util::read_json(&m) {
                if let Some(c) = v["release_commit"].as_str().filter(|c| !c.is_empty()) {
                    return c.to_string();
                }
            }
        }
    }
    if is_embedded_dir(src) {
        return embedded::commit().to_string();
    }
    let out = std::process::Command::new("git")
        .args(["rev-parse", "HEAD"])
        .current_dir(src)
        .output();
    if let Ok(o) = out {
        if o.status.success() {
            let c = String::from_utf8_lossy(&o.stdout).trim().to_string();
            if !c.is_empty() {
                return c;
            }
        }
    }
    "unknown".into()
}

/// Logical, machine-independent source label recorded in framework.lock.
pub fn source_label(src: &Path) -> String {
    let meta = kernel_meta(src).unwrap_or(serde_json::json!({}));
    let ver = meta
        .get("version")
        .map(|v| match v {
            Value::String(s) => s.clone(),
            o => o.to_string(),
        })
        .unwrap_or("unknown".into());
    let s = src.to_string_lossy();
    if s.contains("/kernels/") && s.contains(".cache")
        || s.contains("gov-cache")
        || std::env::var("GOV_KERNEL_CACHE")
            .map(|c| s.starts_with(&c))
            .unwrap_or(false)
    {
        return format!("embedded:{}@{}", FRAMEWORK_NAME, ver);
    }
    if s.contains("/release/releases/") {
        return format!("release:{}@{}", FRAMEWORK_NAME, ver);
    }
    format!("source:{}@{}", FRAMEWORK_NAME, ver)
}

pub fn kernel_meta(kernel_dir: &Path) -> Result<Value> {
    read_yaml(&kernel_dir.join("KERNEL.yaml"))
}

pub fn payload_files(kernel_dir: &Path) -> Result<BTreeMap<String, String>> {
    Ok(hash_tree(kernel_dir, &[KERNEL_MANIFEST])?.1)
}

pub fn build_manifest(kernel_dir: &Path) -> Result<Value> {
    let meta = kernel_meta(kernel_dir)?;
    let files = payload_files(kernel_dir)?;
    let files_v = serde_json::to_value(&files)?;
    let s = |k: &str, d: &str| {
        meta.get(k)
            .map(|v| match v {
                Value::String(x) => x.clone(),
                other => other.to_string(),
            })
            .unwrap_or(d.to_string())
    };
    Ok(json!({
        "framework": s("framework", FRAMEWORK_NAME),
        "version": s("version", VERSION),
        "files": files_v.clone(),
        "payload_hash": hash_value(&files_v),
        "schema_versions": meta.get("schema_versions").cloned().unwrap_or(json!({})),
        "cli_version": s("cli_version", VERSION),
        "runtime_version": s("runtime_version", VERSION),
        "adapter_versions": meta.get("adapter_versions").cloned().unwrap_or(json!({})),
        "supported_from_versions": meta.get("supported_from_versions").cloned().unwrap_or(json!([])),
    }))
}

/// Copy the payload dirs listed in KERNEL.yaml into `dest` (fresh). `migrations` may live next to framework/.
pub fn stage_payload(source_dir: &Path, dest: &Path) -> Result<()> {
    remove_dir_if_exists(dest)?;
    std::fs::create_dir_all(dest)?;
    let meta = kernel_meta(source_dir)?;
    for d in meta
        .get("payload_dirs")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default()
    {
        let d = d.as_str().unwrap_or("").to_string();
        let mut src = source_dir.join(&d);
        if !src.exists() && (d == "migrations" || d == "tools") {
            let cand = source_dir.parent().map(|p| p.join(&d)).unwrap_or_default();
            if cand.exists() {
                src = cand;
            }
        }
        if src.exists() {
            copy_dir(&src, &dest.join(&d))?;
        }
    }
    std::fs::copy(source_dir.join("KERNEL.yaml"), dest.join("KERNEL.yaml"))?;
    Ok(())
}

pub fn install_kernel(source: Option<&Path>, governance_dir: &Path) -> Result<Value> {
    let src = resolve_kernel_source(source)?;
    let dest = governance_dir.join("kernel");
    stage_payload(&src, &dest)?;
    let mut manifest = build_manifest(&dest)?;
    manifest["built_at"] = Value::String(now_iso());
    write_json(&dest.join(KERNEL_MANIFEST), &manifest)?;
    Ok(manifest)
}

pub fn read_manifest(kernel_dir: &Path) -> Result<Value> {
    let p = kernel_dir.join(KERNEL_MANIFEST);
    if !p.exists() {
        return Err(GovError::new(
            "KERNEL_MANIFEST_MISSING",
            format!("kernel manifest missing at {}", p.display()),
        ));
    }
    read_json(&p)
}

pub fn manifest_hash(manifest: &Value) -> String {
    let mut m = serde_json::Map::new();
    for k in ["framework", "version", "files", "payload_hash"] {
        if let Some(v) = manifest.get(k) {
            m.insert(k.to_string(), v.clone());
        }
    }
    hash_value(&Value::Object(m))
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct KernelVerification {
    pub ok: bool,
    pub modified: Vec<String>,
    pub missing: Vec<String>,
    pub added: Vec<String>,
    pub payload_hash: String,
    pub version: String,
}

pub fn verify_kernel(kernel_dir: &Path) -> Result<KernelVerification> {
    let manifest = read_manifest(kernel_dir)?;
    let actual = payload_files(kernel_dir)?;
    let expected: BTreeMap<String, String> = manifest
        .get("files")
        .and_then(|f| serde_json::from_value(f.clone()).ok())
        .unwrap_or_default();
    let modified: Vec<String> = expected
        .iter()
        .filter(|(p, h)| actual.get(*p).map(|a| a != *h).unwrap_or(false))
        .map(|(p, _)| p.clone())
        .collect();
    let missing: Vec<String> = expected
        .keys()
        .filter(|p| !actual.contains_key(*p))
        .cloned()
        .collect();
    let added: Vec<String> = actual
        .keys()
        .filter(|p| !expected.contains_key(*p))
        .cloned()
        .collect();
    Ok(KernelVerification {
        ok: modified.is_empty() && missing.is_empty() && added.is_empty(),
        modified,
        missing,
        added,
        payload_hash: manifest
            .get("payload_hash")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string(),
        version: manifest
            .get("version")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string(),
    })
}
