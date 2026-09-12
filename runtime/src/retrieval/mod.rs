//! Retrieval router (framework §14): classify the question, run routes, fuse, apply authority precedence, expand.
use crate::graph;
use crate::memory::db::RuntimeDb;
use crate::memory::embeddings::{cosine, tokenize, HashedNgramEmbedder};
use crate::{Project, Result};
use regex::Regex;
use serde_json::{json, Value};
use std::collections::{BTreeMap, HashMap, HashSet};
use std::sync::OnceLock;

#[derive(Debug, Clone, Default)]
pub struct RetrieveOptions { pub k: usize, pub include_historical: bool, pub include_archive: bool, pub route: Option<String>, pub record_types: Vec<String>, pub log: bool }

#[derive(Debug, Clone, serde::Serialize)]
pub struct Hit {
    pub artifact_id: String, pub path: String, pub chunk_id: String, pub section: String, pub level: String, pub score: f64,
    pub routes: Vec<String>, pub status: String, pub state_class: String, pub record_type: String, pub excerpt: String,
    pub parent_excerpt: Option<String>, pub neighbours: Vec<String>, pub flags: Vec<String>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct RetrievalResult { pub query: String, pub routes: Vec<String>, pub strategy: String, pub hits: Vec<Hit>, pub index_version: String, pub index_manifest_hash: String, pub latency_ms: u128, pub excluded_by_authority: usize }

fn id_rx() -> &'static Regex { static R: OnceLock<Regex> = OnceLock::new(); R.get_or_init(|| Regex::new(r"\b[A-Z]{1,6}-[0-9]{2,}[A-Za-z0-9.-]*\b").unwrap()) }
fn path_rx() -> &'static Regex { static R: OnceLock<Regex> = OnceLock::new(); R.get_or_init(|| Regex::new(r"[\w./-]+/[\w.-]+\.[A-Za-z0-9]{1,6}").unwrap()) }
fn symbol_rx() -> &'static Regex { static R: OnceLock<Regex> = OnceLock::new(); R.get_or_init(|| Regex::new(r"\b(?:[A-Za-z_]\w*(?:::|\.))+[A-Za-z_]\w*\b|\b(?:def|fn|class|struct|function)\s+([A-Za-z_]\w*)|\bsymbol:([A-Za-z_][\w.]*)").unwrap()) }
fn quoted_rx() -> &'static Regex { static R: OnceLock<Regex> = OnceLock::new(); R.get_or_init(|| Regex::new(r#""([^"]{2,})""#).unwrap()) }
const GRAPH_WORDS: &[&str] = &["depend", "impact", "affect", "block", "downstream", "upstream", "uses", "consumer", "implements", "tests for", "what breaks", "related to"];
const CONCEPT_WORDS: &[&str] = &["why", "rationale", "history", "reason", "how", "approach", "background", "explain", "decided", "lesson"];

pub fn classify(query: &str) -> Vec<String> {
    let mut routes = vec![];
    let q = query.trim();
    let ql = q.to_lowercase();
    if id_rx().is_match(q) { routes.push("structured".to_string()); }
    if path_rx().is_match(q) { routes.push("path".to_string()); }
    if symbol_rx().is_match(q) { routes.push("symbol".to_string()); }
    if quoted_rx().is_match(q) { routes.push("lexical_exact".to_string()); }
    if GRAPH_WORDS.iter().any(|w| ql.contains(w)) && id_rx().is_match(q) { routes.push("graph".to_string()); }
    let conceptual = CONCEPT_WORDS.iter().any(|w| ql.split_whitespace().any(|t| t.trim_matches(|c: char| !c.is_alphanumeric()) == *w));
    if routes.is_empty() || conceptual || q.split_whitespace().count() >= 4 { routes.push("lexical".to_string()); routes.push("semantic".to_string()); }
    if routes.iter().any(|r| r == "structured") && routes.len() == 1 { routes.push("lexical".to_string()); }
    routes.dedup();
    routes
}

fn fts_query(q: &str) -> String {
    let mut parts: Vec<String> = vec![];
    for m in quoted_rx().captures_iter(q) { parts.push(format!("\"{}\"", m[1].replace('"', ""))); }
    let stripped = quoted_rx().replace_all(q, " ");
    let toks: Vec<String> = tokenize(&stripped).into_iter().filter(|t| t.len() > 1).collect::<HashSet<_>>().into_iter().collect();
    let mut toks = toks; toks.sort();
    for t in toks { parts.push(format!("\"{}\"", t.replace('"', ""))); }
    if parts.is_empty() { "\"\"".into() } else { parts.join(" OR ") }
}

struct RouteHits { route: String, ranked: Vec<(String, String)> } // (chunk_id, artifact_id)

pub fn retrieve(p: &Project, db: &RuntimeDb, query: &str, opts: RetrieveOptions) -> Result<RetrievalResult> {
    let started = std::time::Instant::now();
    let pol = p.policies();
    let k = if opts.k == 0 { pol.get_i64("MEMORY_POLICY", "retrieval.default_k", 8) as usize } else { opts.k };
    let rrf_k = pol.get_f64("MEMORY_POLICY", "retrieval.rrf_k", 60.0);
    let parent_top = pol.get_i64("MEMORY_POLICY", "retrieval.parent_expansion_top_n", 3) as usize;
    let max_slice = pol.get_i64("MEMORY_POLICY", "retrieval.max_slice_chars", 1600) as usize;
    let excl_status: Vec<String> = pol.get_list("AUTHORITY_POLICY", "retrieval_default_excludes_statuses");
    let routes = match &opts.route { Some(r) => vec![r.clone()], None => classify(query) };
    let pool = (k * 4).max(20);
    let mut route_hits: Vec<RouteHits> = vec![];
    for route in &routes {
        let ranked: Vec<(String, String)> = match route.as_str() {
            "structured" => {
                let mut v = vec![];
                for m in id_rx().find_iter(query) {
                    for r in db.query("SELECT chunk_id, artifact_id FROM chunks WHERE artifact_id=?1 ORDER BY ordinal LIMIT 3", &[&m.as_str()])? { v.push((r["chunk_id"].as_str().unwrap().into(), r["artifact_id"].as_str().unwrap().into())); }
                }
                v
            }
            "path" => {
                let mut v = vec![];
                for m in path_rx().find_iter(query) {
                    let pat = format!("%{}", m.as_str().trim_start_matches("./"));
                    for r in db.query("SELECT c.chunk_id, c.artifact_id FROM chunks c JOIN artifacts a ON a.artifact_id=c.artifact_id WHERE a.path LIKE ?1 ORDER BY c.ordinal LIMIT 3", &[&pat])? { v.push((r["chunk_id"].as_str().unwrap().into(), r["artifact_id"].as_str().unwrap().into())); }
                }
                v
            }
            "symbol" => {
                let mut v = vec![];
                for c in symbol_rx().captures_iter(query) {
                    let name = c.get(1).or(c.get(2)).map(|m| m.as_str().to_string()).unwrap_or_else(|| c[0].to_string());
                    let last = name.rsplit(['.', ':']).next().unwrap_or(&name).to_string();
                    for r in db.query("SELECT s.path, s.qualname, s.artifact_id FROM symbols s WHERE s.name=?1 OR s.qualname=?2 ORDER BY s.path LIMIT 10", &[&last, &name])? {
                        let aid = r["artifact_id"].as_str().unwrap_or("").to_string();
                        let q = r["qualname"].as_str().unwrap_or("").to_string();
                        if let Some(ch) = db.query_one("SELECT chunk_id FROM chunks WHERE artifact_id=?1 AND section=?2 LIMIT 1", &[&aid, &q])? { v.push((ch["chunk_id"].as_str().unwrap().into(), aid)); }
                        else if let Some(ch) = db.query_one("SELECT chunk_id FROM chunks WHERE artifact_id=?1 ORDER BY ordinal LIMIT 1", &[&aid])? { v.push((ch["chunk_id"].as_str().unwrap().into(), aid)); }
                    }
                }
                v
            }
            "lexical" | "lexical_exact" => {
                let fq = if route == "lexical_exact" { quoted_rx().captures_iter(query).map(|m| format!("\"{}\"", m[1].replace('"', ""))).collect::<Vec<_>>().join(" AND ") } else { fts_query(query) };
                let rows = db.query("SELECT chunk_id, artifact_id, bm25(chunks_fts) AS rank FROM chunks_fts WHERE chunks_fts MATCH ?1 ORDER BY rank LIMIT ?2", &[&fq, &(pool as i64)]).unwrap_or_default();
                rows.into_iter().map(|r| (r["chunk_id"].as_str().unwrap_or("").into(), r["artifact_id"].as_str().unwrap_or("").into())).collect()
            }
            "semantic" => {
                let dim = db.query_one("SELECT dim FROM vectors LIMIT 1", &[])?.and_then(|r| r["dim"].as_i64()).unwrap_or(512) as usize;
                let qv = HashedNgramEmbedder::new(dim, "1").embed(query);
                let mut scored: Vec<(f64, String, String)> = vec![];
                for r in db.query("SELECT chunk_id, artifact_id, vec FROM vectors", &[])? {
                    let v: Vec<f64> = serde_json::from_str(r["vec"].as_str().unwrap_or("[]")).unwrap_or_default();
                    let s = cosine(&qv, &v);
                    if s > 0.0 { scored.push((s, r["chunk_id"].as_str().unwrap_or("").into(), r["artifact_id"].as_str().unwrap_or("").into())); }
                }
                scored.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap_or(std::cmp::Ordering::Equal).then(a.1.cmp(&b.1)));
                scored.into_iter().take(pool).map(|(_, c, a)| (c, a)).collect()
            }
            "graph" => {
                let mut v = vec![];
                let seeds: Vec<String> = id_rx().find_iter(query).map(|m| m.as_str().to_string()).collect();
                for r in graph::neighbours(db, &seeds.first().cloned().unwrap_or_default(), 2)? {
                    if let Some(ch) = db.query_one("SELECT chunk_id FROM chunks WHERE artifact_id=?1 ORDER BY ordinal LIMIT 1", &[&r.node])? { v.push((ch["chunk_id"].as_str().unwrap().into(), r.node.clone())); }
                }
                v
            }
            _ => vec![],
        };
        route_hits.push(RouteHits { route: route.clone(), ranked });
    }
    // Reciprocal-rank fusion
    let mut fused: HashMap<String, (f64, String, Vec<String>)> = HashMap::new();
    for rh in &route_hits {
        for (rank, (chunk, art)) in rh.ranked.iter().enumerate() {
            let e = fused.entry(chunk.clone()).or_insert((0.0, art.clone(), vec![]));
            e.0 += 1.0 / (rrf_k + rank as f64 + 1.0);
            if !e.2.contains(&rh.route) { e.2.push(rh.route.clone()); }
        }
    }
    let mut ordered: Vec<(String, f64, String, Vec<String>)> = fused.into_iter().map(|(c, (s, a, r))| (c, s, a, r)).collect();
    ordered.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal).then(a.0.cmp(&b.0)));
    // Authority + namespace filter, active-state precedence, dedup per artifact
    let mut hits: Vec<Hit> = vec![];
    let mut per_artifact: HashMap<String, usize> = HashMap::new();
    let mut excluded = 0usize;
    let mut art_cache: HashMap<String, Option<Value>> = HashMap::new();
    for (chunk_id, score, artifact_id, rts) in ordered {
        if hits.len() >= k { break; }
        let art = art_cache.entry(artifact_id.clone()).or_insert_with(|| db.artifact(&artifact_id).ok().flatten()).clone();
        let Some(art) = art else { continue };
        let status = art["status"].as_str().unwrap_or("").to_string();
        let record_type = art["record_type"].as_str().unwrap_or("").to_string();
        if !opts.record_types.is_empty() && !opts.record_types.contains(&record_type) { continue; }
        let superseded_by = art["superseded_by"].as_str().unwrap_or("").to_string();
        let mut flags = vec![];
        if !opts.include_historical && (excl_status.contains(&status) || !superseded_by.is_empty()) {
            if status == "ACTIVE" && !superseded_by.is_empty() { flags.push("UNKNOWN_OR_CONFLICTING".into()); }
            excluded += 1;
            continue;
        }
        if !opts.include_archive && art["default_retrieval"].as_i64() == Some(0) { excluded += 1; continue; }
        if !superseded_by.is_empty() { flags.push(format!("superseded_by:{superseded_by}")); }
        let n = per_artifact.entry(artifact_id.clone()).or_insert(0);
        if *n >= 2 { continue; }
        *n += 1;
        let Some(ch) = db.query_one("SELECT section, level, text, parent_chunk_id FROM chunks WHERE chunk_id=?1", &[&chunk_id])? else { continue };
        let excerpt: String = ch["text"].as_str().unwrap_or("").chars().take(max_slice).collect();
        hits.push(Hit { artifact_id: artifact_id.clone(), path: art["path"].as_str().unwrap_or("").into(), chunk_id: chunk_id.clone(), section: ch["section"].as_str().unwrap_or("").into(),
            level: ch["level"].as_str().unwrap_or("").into(), score, routes: rts, status, state_class: art["state_class"].as_str().unwrap_or("").into(), record_type, excerpt,
            parent_excerpt: None, neighbours: vec![], flags });
    }
    // Parent/section + graph-neighbour expansion for the top hits
    for h in hits.iter_mut().take(parent_top) {
        if h.level == "child" {
            if let Some(ch) = db.query_one("SELECT c2.text FROM chunks c1 JOIN chunks c2 ON c2.chunk_id=c1.parent_chunk_id WHERE c1.chunk_id=?1", &[&h.chunk_id])? {
                h.parent_excerpt = Some(ch["text"].as_str().unwrap_or("").chars().take(max_slice).collect());
            }
        }
        h.neighbours = graph::neighbours(db, &h.artifact_id, 1)?.into_iter().map(|r| format!("{} {}", r.via, r.node)).take(12).collect();
    }
    let idx_hash = db.get_meta("index_manifest_hash").and_then(|v| v.as_str().map(|s| s.to_string())).unwrap_or_default();
    let latency = started.elapsed().as_millis();
    if opts.log {
        let _ = db.exec("INSERT INTO retrieval_log(ts, query, routes, hits, latency_ms) VALUES (?1,?2,?3,?4,?5)", &[&crate::util::now_iso(), &query, &routes.join(","), &serde_json::to_string(&hits.iter().map(|h| h.artifact_id.clone()).collect::<Vec<_>>())?, &(latency as f64)]);
    }
    Ok(RetrievalResult { query: query.into(), strategy: if routes.len() > 1 { "fusion".into() } else { routes.first().cloned().unwrap_or_default() }, routes, hits, index_version: crate::INDEX_VERSION.into(), index_manifest_hash: idx_hash, latency_ms: latency, excluded_by_authority: excluded })
}

/// Held-out memory regression (framework §17): Recall@K, MRR, stale/superseded hit rates.
pub fn run_heldout(p: &Project, db: &RuntimeDb, heldout: &Value) -> Result<Value> {
    let queries = heldout.get("queries").and_then(|q| q.as_array()).cloned().unwrap_or_default();
    let mut results = vec![];
    let (mut recall_sum, mut mrr_sum, mut stale_hits, mut superseded_hits, mut total_hits, mut forbidden_violations) = (0.0, 0.0, 0usize, 0usize, 0usize, 0usize);
    let fresh = crate::memory::manifest::freshness(p);
    let stale_paths: HashSet<String> = fresh.stale.iter().cloned().collect();
    for q in &queries {
        let text = q["query"].as_str().unwrap_or("");
        let k = q.get("k").and_then(|v| v.as_u64()).unwrap_or(8) as usize;
        let expected: Vec<String> = q.get("expected_refs").and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
        let forbidden: Vec<String> = q.get("forbidden").and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
        let route = q.get("route").and_then(|v| v.as_str()).map(|s| s.to_string());
        let res = retrieve(p, db, text, RetrieveOptions { k, route, ..Default::default() })?;
        let got: Vec<String> = res.hits.iter().map(|h| h.artifact_id.clone()).collect();
        let found = expected.iter().filter(|e| got.contains(e) || res.hits.iter().any(|h| h.path == **e)).count();
        let recall = if expected.is_empty() { 1.0 } else { found as f64 / expected.len() as f64 };
        let rr = expected.iter().filter_map(|e| got.iter().position(|g| g == e).map(|i| 1.0 / (i as f64 + 1.0))).fold(0.0f64, f64::max);
        let viol: Vec<String> = forbidden.iter().filter(|f| got.contains(f)).cloned().collect();
        forbidden_violations += viol.len();
        for h in &res.hits {
            total_hits += 1;
            if stale_paths.contains(&h.path) { stale_hits += 1; }
            if h.flags.iter().any(|f| f.starts_with("superseded_by")) || h.status == "SUPERSEDED" { superseded_hits += 1; }
        }
        recall_sum += recall; mrr_sum += rr;
        results.push(json!({"id": q["id"], "query": text, "routes": res.routes, "expected": expected, "got": got, "recall": recall, "rr": rr, "forbidden_hits": viol, "pass": recall >= 1.0 - 1e-9 && viol.is_empty()}));
    }
    let n = queries.len().max(1) as f64;
    let pol = p.policies();
    let min_recall = pol.get_f64("MEMORY_POLICY", "regression.min_recall_at_k", 0.8);
    let min_mrr = pol.get_f64("MEMORY_POLICY", "regression.min_mrr", 0.5);
    let max_stale = pol.get_f64("MEMORY_POLICY", "regression.max_stale_hit_rate", 0.0);
    let max_sup = pol.get_f64("MEMORY_POLICY", "regression.max_superseded_hit_rate", 0.0);
    let recall = recall_sum / n; let mrr = mrr_sum / n;
    let stale_rate = if total_hits == 0 { 0.0 } else { stale_hits as f64 / total_hits as f64 };
    let sup_rate = if total_hits == 0 { 0.0 } else { superseded_hits as f64 / total_hits as f64 };
    let pass = queries.is_empty() || (recall >= min_recall && mrr >= min_mrr && stale_rate <= max_stale && sup_rate <= max_sup && forbidden_violations == 0);
    Ok(json!({"queries": queries.len(), "recall_at_k": recall, "mrr": mrr, "stale_hit_rate": stale_rate, "superseded_hit_rate": sup_rate, "forbidden_violations": forbidden_violations,
              "thresholds": {"min_recall_at_k": min_recall, "min_mrr": min_mrr, "max_stale_hit_rate": max_stale, "max_superseded_hit_rate": max_sup}, "pass": pass, "results": results, "index_fresh": fresh.fresh}))
}

pub fn edge_types() -> BTreeMap<String, usize> { graph::EDGE_TYPES.iter().enumerate().map(|(i, t)| (t.to_string(), i)).collect() }
