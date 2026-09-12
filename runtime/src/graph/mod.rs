//! Relationship memory: typed edges stored in the runtime DB; deterministic traversal for impact and navigation.
use crate::memory::db::RuntimeDb;
use crate::Result;
use serde_json::{json, Value};
use std::collections::{BTreeMap, VecDeque};

pub const EDGE_TYPES: &[&str] = &[
    "DEPENDS_ON",
    "BLOCKS",
    "IMPLEMENTS",
    "REALISES",
    "GOVERNED_BY",
    "CONSTRAINS",
    "DERIVED_FROM",
    "SUPERSEDES",
    "VALIDATED_BY",
    "TESTS",
    "USES",
    "PRODUCES",
    "CONSUMES",
    "AFFECTS",
    "GENERATED_FROM",
    "CALLS",
    "IMPORTS",
    "OWNS",
    "FAILED_BECAUSE",
    "LEARNED_FROM",
];
/// If X changes, nodes reaching X through these in-edge types are affected (they depend on / implement / test / use X).
pub const IMPACT_IN: &[&str] = &[
    "DEPENDS_ON",
    "IMPLEMENTS",
    "REALISES",
    "GOVERNED_BY",
    "TESTS",
    "USES",
    "CONSUMES",
    "GENERATED_FROM",
    "DERIVED_FROM",
    "IMPORTS",
    "CALLS",
];
/// If X changes, nodes X points to through these out-edge types are affected.
pub const IMPACT_OUT: &[&str] = &[
    "AFFECTS",
    "BLOCKS",
    "CONSTRAINS",
    "VALIDATED_BY",
    "PRODUCES",
    "SUPERSEDES",
];

#[derive(Debug, Clone, serde::Serialize)]
pub struct Reach {
    pub node: String,
    pub hop: usize,
    pub via: String,
    pub from: String,
}

pub fn out_edges(db: &RuntimeDb, node: &str) -> Result<Vec<(String, String)>> {
    Ok(db
        .query(
            "SELECT type, dst FROM edges WHERE src=?1 ORDER BY type, dst",
            &[&node],
        )?
        .into_iter()
        .map(|r| {
            (
                r["type"].as_str().unwrap_or("").to_string(),
                r["dst"].as_str().unwrap_or("").to_string(),
            )
        })
        .collect())
}
pub fn in_edges(db: &RuntimeDb, node: &str) -> Result<Vec<(String, String)>> {
    Ok(db
        .query(
            "SELECT type, src FROM edges WHERE dst=?1 ORDER BY type, src",
            &[&node],
        )?
        .into_iter()
        .map(|r| {
            (
                r["type"].as_str().unwrap_or("").to_string(),
                r["src"].as_str().unwrap_or("").to_string(),
            )
        })
        .collect())
}

/// Undirected neighbourhood up to `depth`.
pub fn neighbours(db: &RuntimeDb, seed: &str, depth: usize) -> Result<Vec<Reach>> {
    let mut seen: BTreeMap<String, Reach> = BTreeMap::new();
    let mut q = VecDeque::new();
    q.push_back((seed.to_string(), 0usize));
    while let Some((n, hop)) = q.pop_front() {
        if hop >= depth {
            continue;
        }
        for (t, d) in out_edges(db, &n)? {
            if !seen.contains_key(&d) && d != seed {
                seen.insert(
                    d.clone(),
                    Reach {
                        node: d.clone(),
                        hop: hop + 1,
                        via: format!("→{t}"),
                        from: n.clone(),
                    },
                );
                q.push_back((d, hop + 1));
            }
        }
        for (t, s) in in_edges(db, &n)? {
            if !seen.contains_key(&s) && s != seed {
                seen.insert(
                    s.clone(),
                    Reach {
                        node: s.clone(),
                        hop: hop + 1,
                        via: format!("←{t}"),
                        from: n.clone(),
                    },
                );
                q.push_back((s, hop + 1));
            }
        }
    }
    Ok(seen.into_values().collect())
}

/// Deterministic impact traversal from seeds (framework §47.1 / §49).
pub fn impact_set(db: &RuntimeDb, seeds: &[String], depth: usize) -> Result<Vec<Reach>> {
    let mut seen: BTreeMap<String, Reach> = BTreeMap::new();
    let mut q = VecDeque::new();
    for s in seeds {
        q.push_back((s.clone(), 0usize));
    }
    while let Some((n, hop)) = q.pop_front() {
        if hop >= depth {
            continue;
        }
        for (t, s) in in_edges(db, &n)? {
            if IMPACT_IN.contains(&t.as_str()) && !seen.contains_key(&s) && !seeds.contains(&s) {
                seen.insert(
                    s.clone(),
                    Reach {
                        node: s.clone(),
                        hop: hop + 1,
                        via: format!("{t} → {n}"),
                        from: n.clone(),
                    },
                );
                q.push_back((s, hop + 1));
            }
        }
        for (t, d) in out_edges(db, &n)? {
            if IMPACT_OUT.contains(&t.as_str()) && !seen.contains_key(&d) && !seeds.contains(&d) {
                seen.insert(
                    d.clone(),
                    Reach {
                        node: d.clone(),
                        hop: hop + 1,
                        via: format!("{n} {t} →"),
                        from: n.clone(),
                    },
                );
                q.push_back((d, hop + 1));
            }
        }
    }
    Ok(seen.into_values().collect())
}

/// Edges whose destination is not a known artifact (module:/external refs are not counted).
pub fn dangling_edges(db: &RuntimeDb) -> Result<Vec<Value>> {
    db.query("SELECT e.src, e.type, e.dst, e.source_artifact FROM edges e LEFT JOIN artifacts a ON a.artifact_id = e.dst WHERE a.artifact_id IS NULL AND e.dst NOT LIKE 'module:%' AND e.dst NOT LIKE 'external:%' AND e.dst NOT LIKE 'excluded:%' ORDER BY e.src, e.type, e.dst", &[])
}

/// Governed records (non-file artifacts with graph_index) that have no edges at all.
pub fn orphan_nodes(db: &RuntimeDb) -> Result<Vec<String>> {
    Ok(db.query("SELECT a.artifact_id FROM artifacts a WHERE a.graph=1 AND a.record_type != 'file' AND NOT EXISTS (SELECT 1 FROM edges e WHERE e.src=a.artifact_id OR e.dst=a.artifact_id) ORDER BY a.artifact_id", &[])?
        .into_iter().filter_map(|r| r.get("artifact_id").and_then(|v| v.as_str()).map(|s| s.to_string())).collect())
}

pub fn edge_type_counts(db: &RuntimeDb) -> Result<Value> {
    let rows = db.query(
        "SELECT type, COUNT(*) AS c FROM edges GROUP BY type ORDER BY type",
        &[],
    )?;
    let mut m = serde_json::Map::new();
    for r in rows {
        m.insert(r["type"].as_str().unwrap_or("").to_string(), r["c"].clone());
    }
    Ok(json!(m))
}
