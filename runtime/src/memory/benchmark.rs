//! Evidence-based embedder/reranker selection (framework §14.3): benchmark candidates on the held-out set, record a
//! research record with measurements, and pin the selected implementation through the governed change
//! (`memory::profile::select`: evidence, change-control gate, re-index, recorded regression — BC-P2-30).
//!
//! Every measured row carries the candidate's **retrieval profile** (the pinned embedder and reranker with their
//! component identities, `memory::profile`), so the evidence binds what was measured, not a label: a plugin, model
//! artefact or runtime changed after the benchmark no longer matches the evidence. The research record is T2-sealed
//! and carries the version and content hash of the benchmark result (WS-4 IP-13).
use crate::memory::db::RuntimeDb;
use crate::memory::embedder::EmbedSpec;
use crate::memory::indexer::{rebuild, IndexOptions};
use crate::records::{new_record, RecordStore};
use crate::retrieval::run_heldout_with;
use crate::util::read_yaml;
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::PathBuf;

#[derive(Debug, Clone)]
pub struct Candidate {
    pub label: String,
    pub embed: EmbedSpec,
    pub reranker: Option<String>,
}

/// Candidate syntax: `builtin[:dim]` | `plugin:<id>[:dim]` | either followed by `+rerank:<plugin id>`.
pub fn parse_candidate(p: &Project, s: &str) -> Result<Candidate> {
    let (base, rr) = match s.split_once("+rerank:") {
        Some((b, r)) => (b.to_string(), Some(r.to_string())),
        None => (s.to_string(), None),
    };
    let policy = EmbedSpec::from_policy(p);
    let parts: Vec<&str> = base.split(':').collect();
    let embed = match parts[0] {
        "builtin" => EmbedSpec { id: "hashed-ngram".into(), version: "1".into(), dimensions: parts.get(1).and_then(|d| d.parse().ok()).unwrap_or(policy.dimensions), source: "builtin".into() },
        "plugin" => {
            let id = parts.get(1).ok_or_else(|| GovError::new("USAGE", "plugin:<id>[:dim]"))?.to_string();
            // the revision is the one the declared plugin executes (A0-D5-01: never a hard-coded "1")
            let version = crate::capabilities::governance::plugin_set(p).find("embed", None, Some(&id)).map(|d| d.version).unwrap_or_default();
            EmbedSpec { id, version, dimensions: parts.get(2).and_then(|d| d.parse().ok()).unwrap_or(policy.dimensions), source: "plugin".into() }
        }
        "current" => policy,
        other => return Err(GovError::new("USAGE", format!("unknown candidate '{other}' (builtin[:dim] | plugin:<id>[:dim] | current, optionally +rerank:<id>)"))),
    };
    Ok(Candidate {
        label: s.to_string(),
        embed,
        reranker: rr,
    })
}

pub fn run(
    p: &Project,
    candidates: &[String],
    heldout: Option<PathBuf>,
    record: bool,
) -> Result<Value> {
    run_for(p, candidates, heldout, record, None)
}

/// [`run`] for the task that commissioned the benchmark (`gov memory benchmark --record --task <TASK>`): the research
/// record names it among the work it influenced (J1 "influenced decisions/tasks", WS-10 IP-WS10-04).
pub fn run_for(
    p: &Project,
    candidates: &[String],
    heldout: Option<PathBuf>,
    record: bool,
    task: Option<&str>,
) -> Result<Value> {
    p.require_installed()?;
    crate::authority::require(p, "memory_benchmark")?;
    if candidates.len() < 2 {
        return Err(GovError::new(
            "USAGE",
            "a benchmark needs at least two candidates (e.g. current builtin:64 plugin:<id>)",
        ));
    }
    if task.is_some() && !record {
        return Err(GovError::new(
            "USAGE",
            "--task names the task a recorded benchmark was commissioned for; add --record",
        ));
    }
    let commissioning = match task {
        Some(t) => {
            let store = RecordStore::load(&p.root);
            match store.get(t) {
                Some(r) if r.rtype() == "task" => Some(t.to_string()),
                _ => {
                    return Err(GovError::new(
                        "TASK_NOT_FOUND",
                        format!("--task {t} is not a task"),
                    ))
                }
            }
        }
        None => None,
    };
    let held_path = heldout.unwrap_or(p.root.join(p.policies().get_str(
        "MEMORY_POLICY",
        "regression.heldout_file",
        "governance/tests/memory/heldout.yaml",
    )));
    let held = read_yaml(&held_path)?;
    let bench_dir = p.runtime_dir().join("benchmarks");
    std::fs::create_dir_all(&bench_dir)?;
    let mut rows = vec![];
    for (i, c) in candidates.iter().enumerate() {
        let cand = parse_candidate(p, c)?;
        let db_path = bench_dir.join(format!("cand-{i}.db"));
        for suf in ["", "-wal", "-shm"] {
            let f = PathBuf::from(format!("{}{suf}", db_path.display()));
            if f.exists() {
                std::fs::remove_file(&f)?;
            }
        }
        // what this row measures: the candidate's retrieval profile with its component identities
        let profile = match crate::memory::profile::candidate_profile(p, &cand) {
            Ok((prof, _)) => prof,
            Err(e) => {
                rows.push(json!({"candidate": c, "error": e.to_string(), "code": e.code, "usable": false}));
                continue;
            }
        };
        let t0 = std::time::Instant::now();
        let rep = match rebuild(
            p,
            IndexOptions {
                incremental: false,
                db_path: Some(db_path.clone()),
                embed_override: Some(cand.embed.clone()),
                record_failures: Some(false),
                observe_boundaries: false,
                propagate_direct_changes: false,
            },
        ) {
            Ok(r) => r,
            Err(e) => {
                rows.push(json!({"candidate": c, "error": e.to_string(), "usable": false}));
                continue;
            }
        };
        let index_ms = t0.elapsed().as_millis();
        let db = RuntimeDb::open(&db_path)?;
        let h = run_heldout_with(
            p,
            &db,
            &held,
            Some(cand.embed.clone()),
            cand.reranker.clone(),
        )?;
        let sym = h["by_category"]
            .as_array()
            .and_then(|a| a.iter().find(|x| x["category"] == "symbol"))
            .map(|x| x["recall"].clone())
            .unwrap_or(Value::Null);
        rows.push(json!({"candidate": c, "usable": true, "profile": profile.to_value(), "embedder": cand.embed.to_value(), "reranker": cand.reranker, "recall_at_k": h["recall_at_k"], "mrr": h["mrr"], "precision_at_k": h["precision_at_k"], "stale_hit_rate": h["stale_hit_rate"], "superseded_hit_rate": h["superseded_hit_rate"], "forbidden_violations": h["forbidden_violations"], "symbol_recall": sym, "avg_query_latency_ms": h["avg_latency_ms"], "index_ms": index_ms, "vectors": rep.counts["vectors"], "dimensions": cand.embed.dimensions, "measured": h["measured"], "queries": h["queries"], "by_category": h["by_category"]}));
        drop(db);
        for suf in ["", "-wal", "-shm"] {
            let f = PathBuf::from(format!("{}{suf}", db_path.display()));
            if f.exists() {
                let _ = std::fs::remove_file(&f);
            }
        }
    }
    let mut ranked: Vec<&Value> = rows.iter().filter(|r| r["usable"] == true).collect();
    ranked.sort_by(|a, b| {
        b["recall_at_k"]
            .as_f64()
            .unwrap_or(0.0)
            .partial_cmp(&a["recall_at_k"].as_f64().unwrap_or(0.0))
            .unwrap_or(std::cmp::Ordering::Equal)
            .then(
                b["mrr"]
                    .as_f64()
                    .unwrap_or(0.0)
                    .partial_cmp(&a["mrr"].as_f64().unwrap_or(0.0))
                    .unwrap_or(std::cmp::Ordering::Equal),
            )
    });
    let best = ranked
        .first()
        .map(|r| r["candidate"].clone())
        .unwrap_or(Value::Null);
    let mut out = json!({"heldout": held_path.display().to_string(), "queries": held["queries"].as_array().map(|a| a.len()).unwrap_or(0), "rows": rows, "recommended": best, "note": "recall@k, MRR, precision@k, stale/superseded rates, symbol recall, latency and index cost per candidate on the held-out set; selection is a governed decision (gov memory benchmark --select <candidate>)"});
    if record {
        crate::orchestration::control::guard_write(p, "memory benchmark --record")?;
        let store = RecordStore::load(&p.root);
        let id = store.next_id("research");
        let heldout_sha = crate::util::sha256_file(&held_path).unwrap_or_default();
        let result = json!({"format": crate::memory::profile::BENCHMARK_FORMAT, "heldout_sha256": heldout_sha, "rows": out["rows"], "recommended": out["recommended"]});
        let content_hash = crate::util::sha256_hex(crate::util::canonical_json(&result).as_bytes());
        let mut rec = new_record(
            "research",
            &id,
            &format!(
                "Embedding/reranker benchmark ({} candidates)",
                candidates.len()
            ),
            json!({"question": "Which embedding/reranking implementation best serves this repository's held-out retrieval queries?", "reason": "framework §14.3: retrieval model selection is evidence-driven; pins are changed only through a measured migration", "method": format!("For each candidate: full re-index into an isolated database, then the held-out set ({} queries) with Recall@K, MRR, precision@K, stale/superseded hit rates, symbol recall, latency and index cost.", out["queries"]), "sources": [held_path.strip_prefix(&p.root).unwrap_or(&held_path).to_string_lossy()], "measurements": {"rows": out["rows"].clone()}, "uncertainty": "held-out set size and category coverage bound the confidence; paraphrase placeholders are pending", "conclusion": format!("recommended: {}", out["recommended"]), "confidence": if out["queries"].as_u64().unwrap_or(0) >= 10 { 0.7 } else { 0.4 }, "influences": commissioning.iter().collect::<Vec<_>>(), "state_class": "EVIDENCE",
                // IP-13: the version and content hash of the benchmark result this record carries
                "version": "1", "content_hash": content_hash,
                "benchmark": {"format": crate::memory::profile::BENCHMARK_FORMAT, "heldout_sha256": heldout_sha, "candidates": candidates, "recommended": out["recommended"], "result_sha256": content_hash},
                "tags": ["memory", "retrieval-benchmark"]}),
        );
        // a measured benchmark is concluded research (J1: every field above is recorded by the OS), written through
        // the research lifecycle's own stamps; schema-validated and T2-sealed: the evidence a profile change rests
        // on must be what the OS measured (memory::profile::select, WS-10 IP-WS10-04)
        rec.set("research_state", json!("CONCLUDED"));
        rec.set(
            "recorded_by",
            crate::lifecycle::stamp(p, "memory benchmark --record"),
        );
        rec.set(
            "concluded_by",
            crate::lifecycle::stamp(p, "memory benchmark --record"),
        );
        crate::lifecycle::push_history(&mut rec, p, "CONCLUDED", "memory benchmark --record");
        crate::lifecycle::validate_seal_save(p, &mut rec, "memory benchmark")?;
        out["research_record"] = json!(id);
        out["content_hash"] = json!(content_hash);
        out["influences"] = json!(commissioning.iter().collect::<Vec<_>>());
    }
    Ok(out)
}

/// Pin a benchmarked candidate through the governed retrieval-profile change (`memory::profile::select`).
pub fn select(
    p: &Project,
    candidate: &str,
    research_record: Option<&str>,
    gate: Option<&str>,
    by: &str,
) -> Result<Value> {
    crate::memory::profile::select(p, candidate, research_record, gate, by)
}
