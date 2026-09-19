//! Tracked reproducibility manifests (governance/generated/index-manifest.json, memory-manifest.json) and freshness.
use crate::memory::db::RuntimeDb;
use crate::paths::iter_repo_files;
use crate::util::{hash_value, is_text_file, read_json, sha256_file, sorted, write_json};
use crate::{Project, Result, INDEX_VERSION};
use serde_json::{json, Map, Value};

pub fn index_manifest_path(p: &Project) -> std::path::PathBuf {
    p.generated_dir().join("index-manifest.json")
}
pub fn memory_manifest_path(p: &Project) -> std::path::PathBuf {
    p.generated_dir().join("memory-manifest.json")
}

pub fn read_index_manifest(p: &Project) -> Option<Value> {
    read_json(&index_manifest_path(p)).ok()
}

pub fn manifest_hash(m: &Value) -> String {
    let core = json!({"index_version": m.get("index_version"), "embedder": m.get("embedder"), "chunking": m.get("chunking"), "lexical": m.get("lexical"), "artifacts": m.get("artifacts"), "excluded": m.get("excluded")});
    hash_value(&core)
}

pub fn build_index_manifest(
    p: &Project,
    db: &RuntimeDb,
    embedder: &Value,
    chunking: &Value,
    excluded: &[Value],
    lexical: &Value,
    reranker: &Value,
) -> Result<Value> {
    let rows = db.query("SELECT a.path, a.artifact_id, a.content_hash, a.status, a.state_class, a.record_type, a.namespace, a.path_class, a.superseded_by, d.key AS derivation FROM artifacts a LEFT JOIN derivation d ON d.path = a.path ORDER BY a.path", &[])?;
    let mut artifacts = Map::new();
    for r in rows {
        let path = r
            .get("path")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        let mut e = Map::new();
        for k in [
            "artifact_id",
            "content_hash",
            "status",
            "state_class",
            "record_type",
            "namespace",
            "path_class",
            "superseded_by",
            "derivation",
        ] {
            if let Some(v) = r.get(k) {
                if !v.is_null() {
                    e.insert(k.into(), v.clone());
                }
            }
        }
        artifacts.insert(path, Value::Object(e));
    }
    let mut ex: Vec<Value> = excluded
        .iter()
        .map(|e| json!({"path": e.get("path"), "reason": e.get("reason")}))
        .collect();
    ex.sort_by_key(|a| a.to_string());
    let mut m = json!({"index_version": INDEX_VERSION, "embedder": embedder, "reranker": reranker, "chunking": chunking, "lexical": lexical, "repo_commit": p.git_commit(),
        "artifacts": artifacts, "counts": db.counts(), "excluded": ex, "built_at": crate::util::now_iso()});
    let h = manifest_hash(&m);
    m["manifest_hash"] = Value::String(h);
    Ok(sorted(&m))
}

pub fn write_manifests(p: &Project, db: &RuntimeDb, index_manifest: &Value) -> Result<()> {
    write_json(&index_manifest_path(p), index_manifest)?;
    let pol = p.policies();
    let heldout = p.root.join(pol.get_str(
        "MEMORY_POLICY",
        "regression.heldout_file",
        "governance/tests/memory/heldout.yaml",
    ));
    let heldout_hash = if heldout.exists() {
        sha256_file(&heldout).unwrap_or_default()
    } else {
        String::new()
    };
    let mut mm = json!({
        "memory_policy_version": pol.get_str("MEMORY_POLICY", "version", "1.0.0"),
        "namespaces": pol.get("MEMORY_POLICY", "namespaces").unwrap_or(json!({})),
        "heldout_hash": heldout_hash,
        "runtime_dir": crate::RUNTIME_DIR,
        "stores": {"state_db": format!("{}/state.db", crate::RUNTIME_DIR), "tables": db.counts(), "index_manifest_hash": index_manifest.get("manifest_hash")},
    });
    let h = hash_value(
        &json!({"namespaces": mm["namespaces"], "heldout_hash": mm["heldout_hash"], "index_manifest_hash": index_manifest.get("manifest_hash")}),
    );
    mm["manifest_hash"] = Value::String(h);
    write_json(&memory_manifest_path(p), &mm)?;
    db.set_meta("index_manifest_hash", &index_manifest["manifest_hash"])?;
    Ok(())
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct Freshness {
    pub fresh: bool,
    pub stale: Vec<String>,
    pub added: Vec<String>,
    pub removed: Vec<String>,
    pub manifest_present: bool,
    pub checked: usize,
    /// Differences between the policy-pinned embedder/chunking/lexical/index format and the tracked manifest (empty = compatible).
    pub pin_mismatch: Vec<String>,
    pub age_hours: Option<f64>,
    pub age_exceeded: bool,
    /// Entries whose content is unchanged but whose derivation key differs from the current path map, adapter set
    /// or authority mapping (also listed in `stale`): the index still carries their old classification.
    pub reclassified: Vec<String>,
}

/// Compare the tracked index manifest with the working tree (indexable, non-secret, text files only), with the
/// policy pins (embedder, chunking, lexical engine, index format) and with each entry's derivation key (path-map
/// decision, code-intelligence adapter, authority mapping — BC-P2-29). A pin mismatch or a reclassified entry is
/// never "fresh". Evaluated against the policy set and path map on disk now (`indexer::current_view`), never a view
/// cached before a mutation.
pub fn freshness(p_in: &Project) -> Freshness {
    let view = crate::memory::indexer::current_view(p_in);
    let p = &view;
    let Some(m) = read_index_manifest(p) else {
        return Freshness {
            fresh: false,
            stale: vec![],
            added: vec![],
            removed: vec![],
            manifest_present: false,
            checked: 0,
            pin_mismatch: vec![],
            age_hours: None,
            age_exceeded: false,
            reclassified: vec![],
        };
    };
    let governed = crate::capabilities::governance::plugin_set(p);
    let expected = crate::memory::indexer::expected_pins_with(p, &governed);
    let live = json!({"embedder": m.get("embedder"), "chunking": m.get("chunking"), "lexical": m.get("lexical"), "index_version": m.get("index_version")});
    let pin_mismatch = crate::memory::indexer::pin_differences(&expected, &live);
    let age_hours = m
        .get("built_at")
        .and_then(|b| b.as_str())
        .and_then(|b| chrono::DateTime::parse_from_rfc3339(b).ok())
        .map(|t| {
            (chrono::Utc::now() - t.with_timezone(&chrono::Utc)).num_seconds() as f64 / 3600.0
        });
    let max_age = p
        .policies()
        .get_f64("MEMORY_POLICY", "freshness.max_index_age_hours", 168.0);
    let age_exceeded = age_hours.map(|h| h > max_age).unwrap_or(false);
    let arts = m
        .get("artifacts")
        .and_then(|a| a.as_object())
        .cloned()
        .unwrap_or_default();
    let excluded: std::collections::HashSet<String> = m
        .get("excluded")
        .and_then(|a| a.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|e| {
                    e.get("path")
                        .and_then(|p| p.as_str())
                        .map(|s| s.to_string())
                })
                .collect()
        })
        .unwrap_or_default();
    let contract = p.contract();
    let scanner = p.secret_scanner();
    let derive = crate::memory::indexer::DerivationContext::new(p, &governed.usable);
    let mut stale = vec![];
    let mut reclassified = vec![];
    let mut added = vec![];
    let mut seen = std::collections::HashSet::new();
    let mut checked = 0usize;
    for (abs, rel) in iter_repo_files(&p.root, false) {
        if crate::memory::failures::is_memory_quality_path(&rel) {
            continue; // never indexed (memory::failures::MEMORY_QUALITY_DIR)
        }
        let d = contract.decide(&rel);
        if d.is_never_index() || scanner.path_is_secret(&rel) {
            continue;
        }
        if !(d.flag("lexical_index")
            || d.flag("semantic_index")
            || d.flag("graph_index")
            || d.flag("code_index"))
        {
            continue;
        }
        if excluded.contains(&rel) || !is_text_file(&abs) {
            continue;
        }
        checked += 1;
        seen.insert(rel.clone());
        let h = sha256_file(&abs).unwrap_or_default();
        match arts.get(&rel) {
            Some(e) => {
                if e.get("content_hash").and_then(|v| v.as_str()) != Some(h.as_str()) {
                    stale.push(rel.clone());
                } else if e.get("derivation").and_then(|v| v.as_str())
                    != Some(derive.key(&d, &rel).as_str())
                {
                    stale.push(rel.clone());
                    reclassified.push(rel.clone());
                }
            }
            None => added.push(rel.clone()),
        }
    }
    // an entry is removed when its file is gone or no longer indexable under the current path map
    let removed: Vec<String> = arts
        .keys()
        .filter(|k| !seen.contains(*k))
        .cloned()
        .collect();
    let fresh =
        stale.is_empty() && added.is_empty() && removed.is_empty() && pin_mismatch.is_empty();
    Freshness {
        fresh,
        stale,
        added,
        removed,
        manifest_present: true,
        checked,
        pin_mismatch,
        age_hours,
        age_exceeded,
        reclassified,
    }
}
