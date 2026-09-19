//! Persistence for the scheduler, all under `<project>/.governance-runtime/health/` (derived, machine-local state
//! that commands may write even under FREEZE_WRITES, like telemetry):
//!
//! * `cache/<check>.json` — the latest result of each check under the cache key it was computed for (Contract
//!   v3:805). A result is reused only when the current key is byte-identical.
//! * `results/<HR-id>.json` — every health result with its provenance (Contract v3:808): tier, trigger, checks,
//!   inputs, runtime identity, repository state, actor and time. The newest [`RETAIN`] are kept.
//! * `state.json` — the latest outcome of every check and the **active hard-blocks** derived from them; read by the
//!   G0 guard ([`super::guard`]).
//!
//! Governance-suite results that establish green currency are additionally persisted as governed `audit` records in
//! `spec/audits/` by `crate::verification::audit`; product-test results likewise (`crate::verification::product`).
use crate::util::{now_iso, read_json, write_json};
use crate::{Project, Result};
use serde_json::{json, Value};
use std::path::PathBuf;

pub const RETAIN: usize = 300;

pub fn dir(p: &Project) -> PathBuf {
    p.runtime_dir().join("health")
}
fn cache_path(p: &Project, check: &str) -> PathBuf {
    dir(p).join("cache").join(format!("{check}.json"))
}
fn results_dir(p: &Project) -> PathBuf {
    dir(p).join("results")
}
pub fn state_path(p: &Project) -> PathBuf {
    dir(p).join("state.json")
}

/// Atomic write (temp + rename) so a concurrent reader never sees a torn file.
fn write_atomic(path: &std::path::Path, v: &Value) -> Result<()> {
    if let Some(d) = path.parent() {
        std::fs::create_dir_all(d)?;
    }
    let tmp = path.with_extension(format!("tmp-{}", crate::util::short_uuid()));
    write_json(&tmp, v)?;
    std::fs::rename(&tmp, path)?;
    Ok(())
}

/// The cached entry for a check if, and only if, it was computed under exactly `key`.
pub fn cache_get(p: &Project, check: &str, key: &str) -> Option<Value> {
    let v = read_json(&cache_path(p, check)).ok()?;
    if v["key"].as_str() == Some(key) && v["check"].as_str() == Some(check) {
        // integrity of the entry itself: the stored result hash must match the stored result
        let rh = super::result_hash_of(&v["result"]);
        if v["result_hash"].as_str() == Some(rh.as_str()) {
            return Some(v);
        }
    }
    None
}

/// The cached entry for a check under any key (used for the reproducibility comparison and stale reporting).
pub fn cache_peek(p: &Project, check: &str) -> Option<Value> {
    read_json(&cache_path(p, check)).ok()
}

pub fn cache_put(
    p: &Project,
    check: &str,
    key: &str,
    key_parts: &Value,
    result: &Value,
    run_id: &str,
) -> Result<()> {
    let entry = json!({
        "check": check, "key": key, "key_parts": key_parts, "result": result,
        "result_hash": super::result_hash_of(result), "produced_by": run_id, "produced_at": now_iso(),
        "runtime_binary_sha256": crate::verification::currency::runtime_identity()["binary_sha256"],
    });
    write_atomic(&cache_path(p, check), &entry)
}

pub fn new_result_id() -> String {
    format!(
        "HR-{}-{}",
        chrono::Utc::now().format("%Y%m%dT%H%M%S%3fZ"),
        crate::util::short_uuid()
    )
}

/// Persist a health result and prune the oldest beyond [`RETAIN`].
pub fn save_result(p: &Project, result: &Value) -> Result<PathBuf> {
    let id = result["id"].as_str().unwrap_or("HR-unknown").to_string();
    let path = results_dir(p).join(format!("{id}.json"));
    write_atomic(&path, result)?;
    if let Ok(rd) = std::fs::read_dir(results_dir(p)) {
        let mut names: Vec<PathBuf> = rd
            .filter_map(|e| e.ok())
            .map(|e| e.path())
            .filter(|x| x.extension().map(|e| e == "json").unwrap_or(false))
            .collect();
        if names.len() > RETAIN {
            names.sort();
            for old in &names[..names.len() - RETAIN] {
                let _ = std::fs::remove_file(old);
            }
        }
    }
    Ok(path)
}

pub fn load_result(p: &Project, id: &str) -> Option<Value> {
    if id.contains('/') || id.contains("..") {
        return None;
    }
    read_json(&results_dir(p).join(format!("{id}.json"))).ok()
}

/// Newest first.
pub fn history(p: &Project, limit: usize) -> Vec<Value> {
    let Ok(rd) = std::fs::read_dir(results_dir(p)) else {
        return vec![];
    };
    let mut names: Vec<PathBuf> = rd
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|x| x.extension().map(|e| e == "json").unwrap_or(false))
        .collect();
    names.sort();
    names.reverse();
    names
        .into_iter()
        .take(limit)
        .filter_map(|n| read_json(&n).ok())
        .map(|r| {
            json!({"id": r["id"], "surface": r["surface"], "tier": r["tier"], "trigger": r["trigger"], "verdict": r["verdict"], "state": r["state"],
                   "executed": r["summary"]["executed"], "reused": r["summary"]["reused"], "started_at": r["started_at"], "duration_ms": r["duration_ms"], "record": r["record"]})
        })
        .collect()
}

pub fn load_state(p: &Project) -> Value {
    read_json(&state_path(p)).unwrap_or_else(|_| json!({"checks": {}, "blocks": []}))
}

pub fn save_state(p: &Project, state: &Value) -> Result<()> {
    write_atomic(&state_path(p), state)
}
