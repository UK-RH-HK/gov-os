//! Kernel payload: build from the canonical repo, install into a consumer, verify immutability.
use crate::util::{copy_dir, hash_tree, hash_value, now_iso, read_json, read_yaml, remove_dir_if_exists, write_json};
use crate::{GovError, Result, FRAMEWORK_NAME, VERSION};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

pub const KERNEL_MANIFEST: &str = "KERNEL_MANIFEST.json";

/// The canonical repository root when running from a source checkout (CARGO_MANIFEST_DIR/..).
pub fn canonical_root() -> Option<PathBuf> {
    let candidates = [
        std::env::var("GOV_CANONICAL_ROOT").ok().map(PathBuf::from),
        Some(PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("..")),
        std::env::current_exe().ok().and_then(|p| p.parent().map(|d| d.join("../.."))),
    ];
    for c in candidates.into_iter().flatten() {
        if c.join("framework").join("KERNEL.yaml").exists() {
            return Some(c.canonicalize().unwrap_or(c));
        }
    }
    None
}

/// Accepts: None (bundled canonical framework/), a canonical repo root, a framework/ dir, a built release dir, or a kernel dir.
pub fn resolve_kernel_source(source: Option<&Path>) -> Result<PathBuf> {
    let src = match source {
        Some(s) => s.to_path_buf(),
        None => canonical_root().map(|r| r.join("framework")).ok_or_else(|| GovError::new("KERNEL_SOURCE_NOT_FOUND", "no kernel source given and canonical framework/ not found (set GOV_CANONICAL_ROOT or pass --source)"))?,
    };
    for cand in [src.clone(), src.join("kernel"), src.join("framework")] {
        if cand.join("KERNEL.yaml").exists() {
            return Ok(cand);
        }
    }
    Err(GovError::new("KERNEL_SOURCE_NOT_FOUND", format!("no kernel payload found at {}", src.display())))
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
    let s = |k: &str, d: &str| meta.get(k).map(|v| match v { Value::String(x) => x.clone(), other => other.to_string() }).unwrap_or(d.to_string());
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
    for d in meta.get("payload_dirs").and_then(|v| v.as_array()).cloned().unwrap_or_default() {
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
        return Err(GovError::new("KERNEL_MANIFEST_MISSING", format!("kernel manifest missing at {}", p.display())));
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
    let expected: BTreeMap<String, String> = manifest.get("files").and_then(|f| serde_json::from_value(f.clone()).ok()).unwrap_or_default();
    let modified: Vec<String> = expected.iter().filter(|(p, h)| actual.get(*p).map(|a| a != *h).unwrap_or(false)).map(|(p, _)| p.clone()).collect();
    let missing: Vec<String> = expected.keys().filter(|p| !actual.contains_key(*p)).cloned().collect();
    let added: Vec<String> = actual.keys().filter(|p| !expected.contains_key(*p)).cloned().collect();
    Ok(KernelVerification {
        ok: modified.is_empty() && missing.is_empty() && added.is_empty(),
        modified, missing, added,
        payload_hash: manifest.get("payload_hash").and_then(|v| v.as_str()).unwrap_or("").to_string(),
        version: manifest.get("version").and_then(|v| v.as_str()).unwrap_or("").to_string(),
    })
}
