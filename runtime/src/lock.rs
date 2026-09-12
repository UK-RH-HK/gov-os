//! framework.lock: exact installed release/version/hash.
use crate::kernel::manifest_hash;
use crate::util::{now_iso, read_yaml, write_yaml};
use crate::{GovError, Result, CLI_VERSION, FRAMEWORK_NAME};
use serde_json::{json, Value};
use std::path::Path;

pub const LOCK_SCHEMA_VERSION: &str = "1.0.0";

pub fn write_lock(path: &Path, manifest: &Value, source: &str, release_commit: Option<&str>) -> Result<Value> {
    let lock = json!({
        "framework": FRAMEWORK_NAME,
        "version": manifest["version"],
        "release_commit": release_commit.unwrap_or("unknown"),
        "release_hash": manifest["payload_hash"],
        "source": source,
        "installed_at": now_iso(),
        "kernel_manifest_hash": manifest_hash(manifest),
        "cli_version": CLI_VERSION,
        "schema_versions": manifest.get("schema_versions").cloned().unwrap_or(json!({})),
        "lock_schema_version": LOCK_SCHEMA_VERSION,
    });
    write_yaml(path, &lock)?;
    Ok(lock)
}

pub fn read_lock(path: &Path) -> Result<Value> {
    if !path.exists() {
        return Err(GovError::new("LOCK_MISSING", format!("framework.lock missing at {}", path.display())));
    }
    read_yaml(path)
}

pub fn parse_version(v: &str) -> (u64, u64, u64) {
    let core = v.split(['-', '+']).next().unwrap_or("0");
    let mut it = core.split('.').map(|p| p.parse::<u64>().unwrap_or(0));
    (it.next().unwrap_or(0), it.next().unwrap_or(0), it.next().unwrap_or(0))
}

pub fn compare_versions(a: &str, b: &str) -> std::cmp::Ordering {
    parse_version(a).cmp(&parse_version(b))
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct Compatibility {
    pub compatible: bool,
    pub warning: bool,
    pub reason: String,
}

pub fn compatibility(lock_version: &str, cli_version: &str) -> Compatibility {
    let (lv, cv) = (parse_version(lock_version), parse_version(cli_version));
    if lv.0 != cv.0 {
        Compatibility { compatible: false, warning: false, reason: "major version mismatch between installed kernel and gov CLI".into() }
    } else if (lv.1, lv.2) != (cv.1, cv.2) {
        Compatibility { compatible: true, warning: true, reason: format!("installed kernel {lock_version} differs from CLI {cli_version}; run gov update --check") }
    } else {
        Compatibility { compatible: true, warning: false, reason: "match".into() }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn versions_and_compat() {
        assert_eq!(parse_version("4.1.2-rc.1"), (4, 1, 2));
        assert!(compatibility("4.1.1", "4.1.2").warning);
        assert!(!compatibility("3.9.0", "4.1.2").compatible);
        assert!(!compatibility("4.1.2", "4.1.2").warning);
        assert_eq!(compare_versions("4.1.1", "4.1.2"), std::cmp::Ordering::Less);
    }
}
