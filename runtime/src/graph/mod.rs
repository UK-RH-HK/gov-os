//! Relationship memory: typed edges stored in the runtime DB; deterministic traversal for impact and navigation.
//!
//! **Edge direction (Contract v3 W2 line 1090, W6 line 1133; BC-P2-21).** Every edge this module returns reads in
//! the direction of its meaning: `A CONSUMES B` means A consumes B, `A PRODUCES B` means A produces B, `A BLOCKS B`
//! means A blocks B. The indexer can only store an edge whose source is the record that declares it (it writes
//! `(record, type, target)`), so a relation field declared on the *other* end — `X.consumers: [T]` ("T consumes X"),
//! `X.producers: [P]`, `report.task: T` ("T produced this report"), `task.human_gate: G` ("G blocks this task") —
//! is stored under an explicitly inverse type name ([`INVERSE_EDGE_TYPES`]: `X CONSUMED_BY T`) and every query here
//! reads it back as the canonical edge (`T CONSUMES X`). Nothing outside this module needs to know the storage
//! form; `crate::records::Record::edges` gives the same canonical view of a single record.
pub mod identity;
pub mod lineage;

use crate::memory::db::RuntimeDb;
use crate::Result;
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet, VecDeque};

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

/// Storage-only inverse edge types: `(stored type, canonical type)`. A row `(X, CONSUMED_BY, T)` in the edges table
/// **is** the canonical edge `(T, CONSUMES, X)`; it is never returned in its stored form by any traversal.
pub const INVERSE_EDGE_TYPES: &[(&str, &str)] = &[
    ("CONSUMED_BY", "CONSUMES"),
    ("PRODUCED_BY", "PRODUCES"),
    ("BLOCKED_BY", "BLOCKS"),
    ("SUPERSEDED_BY", "SUPERSEDES"),
];

/// The canonical type a stored inverse type stands for (`CONSUMED_BY` -> `CONSUMES`), or `None` for a type that is
/// stored in its own direction.
pub fn canonical_of(stored: &str) -> Option<&'static str> {
    INVERSE_EDGE_TYPES
        .iter()
        .find(|(s, _)| *s == stored)
        .map(|(_, c)| *c)
}

/// The storage name used when the record declaring a `canonical` edge is its *destination* (`CONSUMES` ->
/// `CONSUMED_BY`), or `None` when the canonical type has no inverse storage form.
pub fn inverse_of(canonical: &str) -> Option<&'static str> {
    INVERSE_EDGE_TYPES
        .iter()
        .find(|(_, c)| *c == canonical)
        .map(|(s, _)| *s)
}

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

/// **Implicit consumers** — upstream inputs the context compiler delivers to consumers that never declared them.
/// `(input record type, consumer record type, why)`. Every compiled context packet carries every ACTIVE/PROVISIONAL
/// architecture record ([`crate::context::compile`] reads this table), so every task consumes every current
/// architecture record and impact traversal must reach them (Contract v3 W6 line 1133, W8 line 1148; A0-W2-01).
pub const IMPLICIT_CONSUMERS: &[(&str, &str, &str)] = &[(
    "architecture",
    "task",
    "every task context packet carries all ACTIVE/PROVISIONAL architecture records",
)];

/// Lifecycle statuses under which an implicit input is delivered (and therefore consumed).
pub const IMPLICIT_INPUT_STATUSES: &[&str] = &["ACTIVE", "PROVISIONAL"];

#[derive(Debug, Clone, serde::Serialize)]
pub struct Reach {
    pub node: String,
    pub hop: usize,
    pub via: String,
    pub from: String,
}

fn inverse_list_sql() -> String {
    INVERSE_EDGE_TYPES
        .iter()
        .map(|(s, _)| format!("'{s}'"))
        .collect::<Vec<_>>()
        .join(",")
}

fn rows(db: &RuntimeDb, sql: &str, node: &str, a: &str, b: &str) -> Result<Vec<(String, String)>> {
    Ok(db
        .query(sql, &[&node])?
        .into_iter()
        .map(|r| {
            (
                r[a].as_str().unwrap_or("").to_string(),
                r[b].as_str().unwrap_or("").to_string(),
            )
        })
        .collect())
}

/// Canonical out-edges of `node`: `(type, destination)` for every edge `node -type-> destination`, whichever end
/// declared it.
pub fn out_edges(db: &RuntimeDb, node: &str) -> Result<Vec<(String, String)>> {
    let inv = inverse_list_sql();
    let mut out = rows(
        db,
        &format!("SELECT type, dst FROM edges WHERE src=?1 AND type NOT IN ({inv})"),
        node,
        "type",
        "dst",
    )?;
    for (t, src) in rows(
        db,
        &format!("SELECT type, src FROM edges WHERE dst=?1 AND type IN ({inv})"),
        node,
        "type",
        "src",
    )? {
        if let Some(c) = canonical_of(&t) {
            out.push((c.to_string(), src));
        }
    }
    out.sort();
    out.dedup();
    Ok(out)
}

/// Canonical in-edges of `node`: `(type, source)` for every edge `source -type-> node`, whichever end declared it.
pub fn in_edges(db: &RuntimeDb, node: &str) -> Result<Vec<(String, String)>> {
    let inv = inverse_list_sql();
    let mut out = rows(
        db,
        &format!("SELECT type, src FROM edges WHERE dst=?1 AND type NOT IN ({inv})"),
        node,
        "type",
        "src",
    )?;
    for (t, dst) in rows(
        db,
        &format!("SELECT type, dst FROM edges WHERE src=?1 AND type IN ({inv})"),
        node,
        "type",
        "dst",
    )? {
        if let Some(c) = canonical_of(&t) {
            out.push((c.to_string(), dst));
        }
    }
    out.sort();
    out.dedup();
    Ok(out)
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

/// Consumers that receive `node` without declaring it ([`IMPLICIT_CONSUMERS`]): `(consumer, why)`.
pub fn implicit_consumers(db: &RuntimeDb, node: &str) -> Result<Vec<(String, String)>> {
    implicit_consumers_cached(db, node, &mut BTreeMap::new())
}

/// [`implicit_consumers`] with the consumer lists memoised per consumer type for one traversal.
fn implicit_consumers_cached(
    db: &RuntimeDb,
    node: &str,
    cache: &mut BTreeMap<&'static str, Vec<String>>,
) -> Result<Vec<(String, String)>> {
    // code and other file artefacts are never records of an implicit-input type
    if node.starts_with("file:") || node.contains(':') {
        return Ok(vec![]);
    }
    let Some(a) = db.artifact(node)? else {
        return Ok(vec![]);
    };
    let rtype = a["record_type"].as_str().unwrap_or("");
    let status = a["status"].as_str().unwrap_or("");
    let mut out = vec![];
    for (input_type, consumer_type, why) in IMPLICIT_CONSUMERS {
        if *input_type != rtype || !IMPLICIT_INPUT_STATUSES.contains(&status) {
            continue;
        }
        if !cache.contains_key(consumer_type) {
            let ids: Vec<String> = db
                .query(
                    "SELECT artifact_id FROM artifacts WHERE record_type=?1 ORDER BY artifact_id",
                    &[consumer_type],
                )?
                .into_iter()
                .filter_map(|r| r["artifact_id"].as_str().map(|s| s.to_string()))
                .collect();
            cache.insert(consumer_type, ids);
        }
        for id in &cache[consumer_type] {
            if id != node {
                out.push((id.clone(), why.to_string()));
            }
        }
    }
    Ok(out)
}

/// Deterministic impact traversal from seeds (framework §47.1 / §49).
pub fn impact_set(db: &RuntimeDb, seeds: &[String], depth: usize) -> Result<Vec<Reach>> {
    let mut seen: BTreeMap<String, Reach> = BTreeMap::new();
    let mut implicit_cache: BTreeMap<&'static str, Vec<String>> = BTreeMap::new();
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
        for (c, why) in implicit_consumers_cached(db, &n, &mut implicit_cache)? {
            if !seen.contains_key(&c) && !seeds.contains(&c) {
                seen.insert(
                    c.clone(),
                    Reach {
                        node: c.clone(),
                        hop: hop + 1,
                        via: format!("CONSUMES → {n} (implicit: {why})"),
                        from: n.clone(),
                    },
                );
                q.push_back((c, hop + 1));
            }
        }
    }
    Ok(seen.into_values().collect())
}

/// Reverse lineage: everything `seeds` depend on, up to `depth` (the mirror of [`impact_set`]: follows out-edges of
/// [`IMPACT_IN`] types and in-edges of [`IMPACT_OUT`] types). Answers "which authoritative inputs does this output
/// trace back to" (Contract v3 W8 lines 1148-1149).
pub fn upstream_set(db: &RuntimeDb, seeds: &[String], depth: usize) -> Result<Vec<Reach>> {
    let mut seen: BTreeMap<String, Reach> = BTreeMap::new();
    let mut q = VecDeque::new();
    for s in seeds {
        q.push_back((s.clone(), 0usize));
    }
    while let Some((n, hop)) = q.pop_front() {
        if hop >= depth {
            continue;
        }
        for (t, d) in out_edges(db, &n)? {
            if IMPACT_IN.contains(&t.as_str()) && !seen.contains_key(&d) && !seeds.contains(&d) {
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
        for (t, s) in in_edges(db, &n)? {
            if IMPACT_OUT.contains(&t.as_str()) && !seen.contains_key(&s) && !seeds.contains(&s) {
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
    }
    Ok(seen.into_values().collect())
}

/// Edges whose destination is not a known artifact (module:/external refs are not counted).
///
/// A `PRODUCES` edge to a `file:` destination records an output an execution produced (a closing report's or a
/// task's `outputs_produced`/`files_changed`); a deleted, binary, secret-class or otherwise unindexed output is a
/// lineage fact, not a dangling reference, and is reported by [`lineage::stale_links`] instead.
pub fn dangling_edges(db: &RuntimeDb) -> Result<Vec<Value>> {
    db.query("SELECT e.src, e.type, e.dst, e.source_artifact FROM edges e LEFT JOIN artifacts a ON a.artifact_id = e.dst WHERE a.artifact_id IS NULL AND e.dst NOT LIKE 'module:%' AND e.dst NOT LIKE 'external:%' AND e.dst NOT LIKE 'excluded:%' AND NOT (e.dst LIKE 'file:%' AND e.type = 'PRODUCES') ORDER BY e.src, e.type, e.dst", &[])
}

/// Governed records (non-file artifacts with graph_index) that have no edges at all.
pub fn orphan_nodes(db: &RuntimeDb) -> Result<Vec<String>> {
    Ok(db.query("SELECT a.artifact_id FROM artifacts a WHERE a.graph=1 AND a.record_type != 'file' AND NOT EXISTS (SELECT 1 FROM edges e WHERE e.src=a.artifact_id OR e.dst=a.artifact_id) ORDER BY a.artifact_id", &[])?
        .into_iter().filter_map(|r| r.get("artifact_id").and_then(|v| v.as_str()).map(|s| s.to_string())).collect())
}

/// Edge counts per **canonical** type (stored inverse forms are counted under the type they stand for).
pub fn edge_type_counts(db: &RuntimeDb) -> Result<Value> {
    let rows = db.query(
        "SELECT type, COUNT(*) AS c FROM edges GROUP BY type ORDER BY type",
        &[],
    )?;
    let mut m: BTreeMap<String, i64> = BTreeMap::new();
    for r in rows {
        let t = r["type"].as_str().unwrap_or("").to_string();
        let t = canonical_of(&t).map(|c| c.to_string()).unwrap_or(t);
        *m.entry(t).or_insert(0) += r["c"].as_i64().unwrap_or(0);
    }
    Ok(json!(m))
}

/// Every canonical edge touching `node` (both directions), for lineage reporting.
pub fn canonical_edges(db: &RuntimeDb, node: &str) -> Result<Vec<Value>> {
    let mut out: BTreeSet<(String, String, String)> = BTreeSet::new();
    for (t, d) in out_edges(db, node)? {
        out.insert((node.to_string(), t, d));
    }
    for (t, s) in in_edges(db, node)? {
        out.insert((s, t, node.to_string()));
    }
    Ok(out
        .into_iter()
        .map(|(s, t, d)| json!({"src": s, "type": t, "dst": d}))
        .collect())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn db_with(edges: &[(&str, &str, &str)], artifacts: &[(&str, &str, &str)]) -> RuntimeDb {
        let db = RuntimeDb::open_memory().unwrap();
        db.init_schema().unwrap();
        for (s, t, d) in edges {
            db.exec(
                "INSERT INTO edges(src, type, dst, source_artifact, provenance) VALUES (?1,?2,?3,?1,'test')",
                &[s, t, d],
            )
            .unwrap();
        }
        for (id, rt, st) in artifacts {
            db.exec(
                "INSERT INTO artifacts(artifact_id, path, record_type, status) VALUES (?1,?1,?2,?3)",
                &[id, rt, st],
            )
            .unwrap();
        }
        db
    }

    #[test]
    fn inverse_storage_is_read_back_in_the_direction_of_its_meaning() {
        // API-0001.consumers: [TASK-0001]  => stored API-0001 CONSUMED_BY TASK-0001 == TASK-0001 CONSUMES API-0001
        let db = db_with(&[("API-0001", "CONSUMED_BY", "TASK-0001")], &[]);
        assert_eq!(
            out_edges(&db, "TASK-0001").unwrap(),
            vec![("CONSUMES".to_string(), "API-0001".to_string())]
        );
        assert_eq!(
            in_edges(&db, "API-0001").unwrap(),
            vec![("CONSUMES".to_string(), "TASK-0001".to_string())]
        );
        assert!(out_edges(&db, "API-0001").unwrap().is_empty());
        // a change to the interface reaches its consumer; a change to the consumer does not reach the interface
        let imp = impact_set(&db, &["API-0001".into()], 2).unwrap();
        assert!(imp.iter().any(|r| r.node == "TASK-0001"));
        let imp = impact_set(&db, &["TASK-0001".into()], 2).unwrap();
        assert!(!imp.iter().any(|r| r.node == "API-0001"));
        // the neighbourhood names the canonical type
        let n = neighbours(&db, "TASK-0001", 1).unwrap();
        assert_eq!(n[0].via, "→CONSUMES");
        assert_eq!(edge_type_counts(&db).unwrap()["CONSUMES"], 1);
    }

    #[test]
    fn producer_and_report_edges_point_from_producer_to_product() {
        // report.task: TASK-0001 => TASK-0001 PRODUCES RPT-0001; report outputs => RPT-0001 PRODUCES file:src/lib.rs
        let db = db_with(
            &[
                ("RPT-0001", "PRODUCED_BY", "TASK-0001"),
                ("RPT-0001", "PRODUCES", "file:src/lib.rs"),
                ("TASK-0001", "GOVERNED_BY", "REQ-0001"),
                ("RPT-0001", "IMPLEMENTS", "REQ-0001"),
            ],
            &[],
        );
        let imp = impact_set(&db, &["REQ-0001".into()], 4).unwrap();
        let nodes: Vec<&str> = imp.iter().map(|r| r.node.as_str()).collect();
        assert!(nodes.contains(&"TASK-0001") && nodes.contains(&"RPT-0001"));
        assert!(nodes.contains(&"file:src/lib.rs"), "{nodes:?}");
        let up = upstream_set(&db, &["file:src/lib.rs".into()], 4).unwrap();
        let up: Vec<&str> = up.iter().map(|r| r.node.as_str()).collect();
        assert!(
            up.contains(&"RPT-0001") && up.contains(&"REQ-0001"),
            "{up:?}"
        );
        let n = neighbours(&db, "RPT-0001", 1).unwrap();
        assert!(n
            .iter()
            .any(|r| r.node == "TASK-0001" && r.via == "←PRODUCES"));
        // an output file that is not (or no longer) indexed is not a dangling reference
        assert!(dangling_edges(&db)
            .unwrap()
            .iter()
            .all(|d| d["dst"] != "file:src/lib.rs"));
    }

    #[test]
    fn implicit_architecture_consumers_are_reached_by_impact() {
        let db = db_with(
            &[],
            &[
                ("ARCH-0001", "architecture", "ACTIVE"),
                ("ARCH-0002", "architecture", "SUPERSEDED"),
                ("TASK-0001", "task", "ACTIVE"),
                ("TASK-0002", "task", "ACTIVE"),
            ],
        );
        let imp = impact_set(&db, &["ARCH-0001".into()], 1).unwrap();
        assert_eq!(
            imp.iter().map(|r| r.node.as_str()).collect::<Vec<_>>(),
            vec!["TASK-0001", "TASK-0002"]
        );
        // a superseded architecture record is not delivered, so nothing consumes it implicitly
        assert!(impact_set(&db, &["ARCH-0002".into()], 1)
            .unwrap()
            .is_empty());
    }
}
