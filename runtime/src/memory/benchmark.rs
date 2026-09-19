//! Evidence-based embedder/reranker selection (framework §14.3): benchmark candidates on the held-out set, record a
//! research record with measurements, and (optionally) pin the selected implementation through a decision record.
use crate::memory::db::RuntimeDb;
use crate::memory::embedder::EmbedSpec;
use crate::memory::indexer::{rebuild, IndexOptions};
use crate::records::{new_record, save_record, RecordStore};
use crate::retrieval::run_heldout_with;
use crate::util::{read_yaml, write_yaml};
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
        "plugin" => { let id = parts.get(1).ok_or_else(|| GovError::new("USAGE", "plugin:<id>[:dim]"))?.to_string(); EmbedSpec { id, version: "1".into(), dimensions: parts.get(2).and_then(|d| d.parse().ok()).unwrap_or(policy.dimensions), source: "plugin".into() } }
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
    p.require_installed()?;
    crate::authority::require(p, "memory_benchmark")?;
    if candidates.len() < 2 {
        return Err(GovError::new(
            "USAGE",
            "a benchmark needs at least two candidates (e.g. current builtin:64 plugin:<id>)",
        ));
    }
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
        let t0 = std::time::Instant::now();
        let rep = match rebuild(
            p,
            IndexOptions {
                incremental: false,
                db_path: Some(db_path.clone()),
                embed_override: Some(cand.embed.clone()),
                record_failures: Some(false),
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
        rows.push(json!({"candidate": c, "usable": true, "embedder": cand.embed.to_value(), "reranker": cand.reranker, "recall_at_k": h["recall_at_k"], "mrr": h["mrr"], "precision_at_k": h["precision_at_k"], "stale_hit_rate": h["stale_hit_rate"], "superseded_hit_rate": h["superseded_hit_rate"], "forbidden_violations": h["forbidden_violations"], "symbol_recall": sym, "avg_query_latency_ms": h["avg_latency_ms"], "index_ms": index_ms, "vectors": rep.counts["vectors"], "dimensions": cand.embed.dimensions, "measured": h["measured"], "queries": h["queries"], "by_category": h["by_category"]}));
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
        let store = RecordStore::load(&p.root);
        let id = store.next_id("research");
        let rec = new_record(
            "research",
            &id,
            &format!(
                "Embedding/reranker benchmark ({} candidates)",
                candidates.len()
            ),
            json!({"question": "Which embedding/reranking implementation best serves this repository's held-out retrieval queries?", "reason": "framework §14.3: retrieval model selection is evidence-driven; pins are changed only through a measured migration", "method": format!("For each candidate: full re-index into an isolated database, then the held-out set ({} queries) with Recall@K, MRR, precision@K, stale/superseded hit rates, symbol recall, latency and index cost.", out["queries"]), "sources": [held_path.strip_prefix(&p.root).unwrap_or(&held_path).to_string_lossy()], "measurements": {"rows": out["rows"].clone()}, "uncertainty": "held-out set size and category coverage bound the confidence; paraphrase placeholders are pending", "conclusion": format!("recommended: {}", out["recommended"]), "confidence": if out["queries"].as_u64().unwrap_or(0) >= 10 { 0.7 } else { 0.4 }, "influences": [], "state_class": "EVIDENCE"}),
        );
        save_record(&p.root, &rec)?;
        out["research_record"] = json!(id);
    }
    Ok(out)
}

/// Pin a benchmarked candidate: decision record with alternatives + overlay override + full rebuild.
pub fn select(
    p: &Project,
    candidate: &str,
    research_record: Option<&str>,
    by: &str,
) -> Result<Value> {
    crate::authority::require(p, "memory_select")?;
    crate::orchestration::control::guard_write(p, "memory select")?;
    let cand = parse_candidate(p, candidate)?;
    let store = RecordStore::load(&p.root);
    let alternatives: Vec<Value> = research_record
        .and_then(|r| store.get(r))
        .and_then(|r| r.data["measurements"]["rows"].as_array().cloned())
        .unwrap_or_default();
    let did = store.next_id("decision");
    let dec = new_record(
        "decision",
        &did,
        &format!("Pin embedding implementation {}", cand.embed.describe()),
        json!({"question": "Which embedding/reranking implementation is pinned for this repository's semantic memory?", "options": alternatives.iter().map(|a| json!({"id": a["candidate"], "description": format!("recall@k {} mrr {} precision {} latency {} ms", a["recall_at_k"], a["mrr"], a["precision_at_k"], a["avg_query_latency_ms"])})).collect::<Vec<_>>(), "chosen_option": candidate, "rationale": format!("selected on held-out evidence{}", research_record.map(|r| format!(" ({r})")).unwrap_or_default()), "approved_by": by, "approved_at": crate::util::now_iso(), "human_approved": crate::authority::level_of(p, &p.role).map(|l| l >= 5).unwrap_or(false), "approved_by_kind": if crate::authority::level_of(p, &p.role).map(|l| l >= 5).unwrap_or(false) { "human" } else { "agent" }, "approved_by_role": p.role, "impact_radius": "R3", "reversibility": "re-pin and rebuild", "confidence": 0.7, "derived_from": research_record.map(|r| vec![r.to_string()]).unwrap_or_default(), "tags": ["memory", "embedder-selection"], "state_class": "AUTHORITATIVE"}),
    );
    save_record(&p.root, &dec)?;
    let pp_path = p.overlay_dir().join("PROJECT_POLICY.yaml");
    let mut pp = read_yaml(&pp_path)?;
    let mut over = pp.get("policy_overrides").cloned().unwrap_or(json!({}));
    over["MEMORY_POLICY.embedding.provider"] = json!(cand.embed.id);
    over["MEMORY_POLICY.embedding.version"] = json!(cand.embed.version);
    over["MEMORY_POLICY.embedding.dimensions"] = json!(cand.embed.dimensions);
    if let Some(r) = &cand.reranker {
        over["MEMORY_POLICY.reranker.provider"] = json!(r);
    }
    pp["policy_overrides"] = over;
    write_yaml(&pp_path, &pp)?;
    let mut p2 =
        Project::open(&p.root).with_session(Some(p.session_id.clone()), Some(p.role.clone()));
    p2.invalidate();
    let rep = rebuild(
        &p2,
        IndexOptions {
            incremental: false,
            ..Default::default()
        },
    )?;
    Ok(
        json!({"decision": did, "pinned": cand.embed.to_value(), "reranker": cand.reranker, "rebuilt": rep.manifest_hash}),
    )
}
