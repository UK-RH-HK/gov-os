//! Retrieval router (framework §14): classify the question, run routes, fuse, rerank (if pinned), apply authority and
//! namespace/role precedence, expand. The query is embedded with the implementation the live index was built with.
use crate::authority::role_in;
use crate::graph;
use crate::memory::db::RuntimeDb;
use crate::memory::embedder::{for_query, Reranker};
use crate::memory::embeddings::{cosine, tokenize};
use crate::{GovError, Project, Result};
use regex::Regex;
use serde_json::{json, Value};
use std::collections::{HashMap, HashSet};
use std::sync::OnceLock;

#[derive(Debug, Clone, Default)]
pub struct RetrieveOptions { pub k: usize, pub include_historical: bool, pub include_archive: bool, pub route: Option<String>, pub record_types: Vec<String>, pub log: bool,
    /// Benchmark-only: query against an index built with this spec instead of the policy pin.
    pub embed_override: Option<crate::memory::embedder::EmbedSpec>, pub rerank_override: Option<String> }

#[derive(Debug, Clone, serde::Serialize)]
pub struct Hit {
    pub artifact_id: String, pub path: String, pub chunk_id: String, pub section: String, pub level: String, pub score: f64,
    pub routes: Vec<String>, pub status: String, pub state_class: String, pub record_type: String, pub excerpt: String,
    pub parent_excerpt: Option<String>, pub neighbours: Vec<String>, pub flags: Vec<String>, pub rerank_score: Option<f64>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct RetrievalResult { pub query: String, pub routes: Vec<String>, pub strategy: String, pub hits: Vec<Hit>, pub index_version: String, pub index_manifest_hash: String, pub latency_ms: u128, pub excluded_by_authority: usize, pub excluded_by_namespace: usize, pub embedder: Value, pub reranker: Value }

fn id_rx() -> &'static Regex { static R: OnceLock<Regex> = OnceLock::new(); R.get_or_init(|| Regex::new(r"\b[A-Z]{1,6}-[0-9]{2,}[A-Za-z0-9.-]*\b").unwrap()) }
fn path_rx() -> &'static Regex { static R: OnceLock<Regex> = OnceLock::new(); R.get_or_init(|| Regex::new(r"[\w./-]+/[\w.-]+\.[A-Za-z0-9]{1,6}").unwrap()) }
fn symbol_rx() -> &'static Regex { static R: OnceLock<Regex> = OnceLock::new(); R.get_or_init(|| Regex::new(r"\b(?:[A-Za-z_]\w*(?:::|\.))+[A-Za-z_]\w*\b|\b(?:def|fn|class|struct|function)\s+([A-Za-z_]\w*)|\bsymbol:([A-Za-z_][\w.]*)").unwrap()) }
fn ident_rx() -> &'static Regex { static R: OnceLock<Regex> = OnceLock::new(); R.get_or_init(|| Regex::new(r"^[A-Za-z_][A-Za-z0-9_]{2,}$").unwrap()) }
fn quoted_rx() -> &'static Regex { static R: OnceLock<Regex> = OnceLock::new(); R.get_or_init(|| Regex::new(r#""([^"]{2,})""#).unwrap()) }
const GRAPH_WORDS: &[&str] = &["depend", "impact", "affect", "block", "downstream", "upstream", "uses", "consumer", "implements", "tests for", "what breaks", "related to"];
const CONCEPT_WORDS: &[&str] = &["why", "rationale", "history", "reason", "how", "approach", "background", "explain", "decided", "lesson"];

pub fn is_bare_identifier(q: &str) -> bool { ident_rx().is_match(q.trim()) && !id_rx().is_match(q.trim()) }

pub fn classify(query: &str) -> Vec<String> {
    let mut routes = vec![];
    let q = query.trim();
    let ql = q.to_lowercase();
    if is_bare_identifier(q) { return vec!["symbol".into(), "lexical".into()]; }
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
    let mut toks: Vec<String> = tokenize(&stripped).into_iter().filter(|t| t.len() > 1).collect::<HashSet<_>>().into_iter().collect();
    toks.sort();
    for t in toks { parts.push(format!("\"{}\"", t.replace('"', ""))); }
    if parts.is_empty() { "\"\"".into() } else { parts.join(" OR ") }
}

struct RouteHits { route: String, ranked: Vec<(String, String)> }

fn chunk_for(db: &RuntimeDb, aid: &str, section: Option<&str>) -> Result<Option<String>> {
    if let Some(sec) = section { if let Some(ch) = db.query_one("SELECT chunk_id FROM chunks WHERE artifact_id=?1 AND section=?2 LIMIT 1", &[&aid, &sec])? { return Ok(ch["chunk_id"].as_str().map(|s| s.to_string())); } }
    Ok(db.query_one("SELECT chunk_id FROM chunks WHERE artifact_id=?1 ORDER BY ordinal LIMIT 1", &[&aid])?.and_then(|c| c["chunk_id"].as_str().map(|s| s.to_string())))
}

pub fn retrieve(p: &Project, db: &RuntimeDb, query: &str, opts: RetrieveOptions) -> Result<RetrievalResult> {
    let started = std::time::Instant::now();
    let pol = p.policies();
    let k = if opts.k == 0 { pol.get_i64("MEMORY_POLICY", "retrieval.default_k", 8) as usize } else { opts.k };
    let rrf_k = pol.get_f64("MEMORY_POLICY", "retrieval.rrf_k", 60.0);
    let parent_top = pol.get_i64("MEMORY_POLICY", "retrieval.parent_expansion_top_n", 3) as usize;
    let graph_depth = pol.get_i64("MEMORY_POLICY", "retrieval.graph_neighbour_depth", 1).max(1) as usize;
    let max_slice = pol.get_i64("MEMORY_POLICY", "retrieval.max_slice_chars", 1600) as usize;
    let excl_status: Vec<String> = pol.get_list("AUTHORITY_POLICY", "retrieval_default_excludes_statuses");
    let namespaces = pol.get("MEMORY_POLICY", "namespaces").unwrap_or(json!({}));
    let routes = match &opts.route { Some(r) => vec![r.clone()], None => classify(query) };
    let pool = (k * 4).max(20);
    let mut embedder_used = json!({"provider": "none"});
    let mut route_hits: Vec<RouteHits> = vec![];
    for route in &routes {
        let ranked: Vec<(String, String)> = match route.as_str() {
            "structured" => { let mut v = vec![]; for m in id_rx().find_iter(query) { for r in db.query("SELECT chunk_id, artifact_id FROM chunks WHERE artifact_id=?1 ORDER BY ordinal LIMIT 3", &[&m.as_str()])? { v.push((r["chunk_id"].as_str().unwrap().into(), r["artifact_id"].as_str().unwrap().into())); } } v }
            "path" => { let mut v = vec![]; for m in path_rx().find_iter(query) { let pat = format!("%{}", m.as_str().trim_start_matches("./")); for r in db.query("SELECT c.chunk_id, c.artifact_id FROM chunks c JOIN artifacts a ON a.artifact_id=c.artifact_id WHERE a.path LIKE ?1 ORDER BY c.ordinal LIMIT 3", &[&pat])? { v.push((r["chunk_id"].as_str().unwrap().into(), r["artifact_id"].as_str().unwrap().into())); } } v }
            "symbol" => {
                let mut v = vec![];
                let mut names: Vec<(String, String)> = symbol_rx().captures_iter(query).map(|c| { let name = c.get(1).or(c.get(2)).map(|m| m.as_str().to_string()).unwrap_or_else(|| c[0].to_string()); let last = name.rsplit(['.', ':']).next().unwrap_or(&name).to_string(); (name, last) }).collect();
                if names.is_empty() && is_bare_identifier(query) { names.push((query.trim().to_string(), query.trim().to_string())); }
                for (name, last) in names {
                    for r in db.query("SELECT s.path, s.qualname, s.artifact_id FROM symbols s WHERE (s.name=?1 OR s.qualname=?2) AND s.kind != 'module' ORDER BY s.path LIMIT 10", &[&last, &name])? {
                        let aid = r["artifact_id"].as_str().unwrap_or("").to_string(); let q = r["qualname"].as_str().unwrap_or("").to_string();
                        if let Some(ch) = chunk_for(db, &aid, Some(&q))? { v.push((ch, aid)); }
                    }
                    // references (imports/calls) to the symbol
                    for r in db.query("SELECT DISTINCT a.artifact_id FROM symbol_refs sr JOIN artifacts a ON a.path=sr.path WHERE sr.name=?1 AND sr.kind='call' ORDER BY a.artifact_id LIMIT 10", &[&last])? { let aid = r["artifact_id"].as_str().unwrap_or("").to_string(); if let Some(ch) = chunk_for(db, &aid, None)? { v.push((ch, aid)); } }
                }
                v
            }
            "lexical" | "lexical_exact" => {
                let fq = if route == "lexical_exact" { quoted_rx().captures_iter(query).map(|m| format!("\"{}\"", m[1].replace('"', ""))).collect::<Vec<_>>().join(" AND ") } else { fts_query(query) };
                db.query("SELECT chunk_id, artifact_id, bm25(chunks_fts) AS rank FROM chunks_fts WHERE chunks_fts MATCH ?1 ORDER BY rank LIMIT ?2", &[&fq, &(pool as i64)]).unwrap_or_default().into_iter().map(|r| (r["chunk_id"].as_str().unwrap_or("").into(), r["artifact_id"].as_str().unwrap_or("").into())).collect()
            }
            "semantic" => {
                // the query is embedded with the implementation pinned for the live index (errors propagate: no fallback)
                let embedder = match &opts.embed_override { Some(spec) => { let live = crate::memory::embedder::live_spec(db); if live.as_ref() != Some(spec) { return Err(GovError::new("EMBEDDER_MISMATCH", "benchmark index does not match the candidate spec")); } crate::memory::embedder::Embedder::resolve(spec, &crate::capabilities::host::discover(&p.root))? } None => for_query(p, db)? };
                embedder_used = embedder.spec().to_value();
                let qv = embedder.embed_one(query, &p.root)?;
                let mut scored: Vec<(f64, String, String)> = vec![];
                for r in db.query("SELECT chunk_id, artifact_id, vec, dim FROM vectors", &[])? {
                    let v: Vec<f64> = serde_json::from_str(r["vec"].as_str().unwrap_or("[]")).unwrap_or_default();
                    if v.len() != qv.len() { return Err(GovError::new("EMBEDDER_MISMATCH", format!("stored vector for {} has {} dimensions but the query vector has {}; the index is heterogeneous: run gov rebuild-memory", r["chunk_id"], v.len(), qv.len()))); }
                    let s = cosine(&qv, &v);
                    if s > 0.0 { scored.push((s, r["chunk_id"].as_str().unwrap_or("").into(), r["artifact_id"].as_str().unwrap_or("").into())); }
                }
                scored.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap_or(std::cmp::Ordering::Equal).then(a.1.cmp(&b.1)));
                scored.into_iter().take(pool).map(|(_, c, a)| (c, a)).collect()
            }
            "graph" => { let mut v = vec![]; let seeds: Vec<String> = id_rx().find_iter(query).map(|m| m.as_str().to_string()).collect(); for r in graph::neighbours(db, &seeds.first().cloned().unwrap_or_default(), 2)? { if let Some(ch) = chunk_for(db, &r.node, None)? { v.push((ch, r.node.clone())); } } v }
            _ => vec![],
        };
        route_hits.push(RouteHits { route: route.clone(), ranked });
    }
    // --- reciprocal-rank fusion
    let mut fused: HashMap<String, (f64, String, Vec<String>)> = HashMap::new();
    for rh in &route_hits { for (rank, (chunk, art)) in rh.ranked.iter().enumerate() { let e = fused.entry(chunk.clone()).or_insert((0.0, art.clone(), vec![])); e.0 += 1.0 / (rrf_k + rank as f64 + 1.0); if !e.2.contains(&rh.route) { e.2.push(rh.route.clone()); } } }
    let mut ordered: Vec<(String, f64, String, Vec<String>)> = fused.into_iter().map(|(c, (s, a, r))| (c, s, a, r)).collect();
    ordered.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal).then(a.0.cmp(&b.0)));
    // --- reranker hook (pinned plugin; between fusion and authority filtering)
    let plugins = crate::capabilities::host::discover(&p.root);
    let mut reranker_used = json!({"provider": "none"});
    let mut rerank_scores: HashMap<String, f64> = HashMap::new();
    let reranker = match &opts.rerank_override { Some(id) => { let desc = crate::capabilities::host::find(&plugins, "rerank", None, Some(id)).ok_or_else(|| GovError::new("RERANKER_UNAVAILABLE", format!("rerank plugin '{id}' not declared")))?; Some(Reranker { desc, spec: crate::memory::embedder::RerankSpec { provider: id.clone(), version: "1".into(), candidates: pol.get_i64("MEMORY_POLICY", "retrieval.rerank_candidates", 24).max(1) as usize } }) } None => Reranker::resolve(p, &plugins)? };
    if let Some(rr) = reranker {
        let live_rr = db.get_meta("reranker").unwrap_or(json!({"provider": "none"}));
        if opts.rerank_override.is_none() && live_rr.get("provider") != Some(&json!(rr.spec.provider)) { return Err(GovError::new("RERANKER_MISMATCH", format!("MEMORY_POLICY pins reranker '{}' but the live index was built with {}; run gov rebuild-memory", rr.spec.provider, live_rr))); }
        let n = rr.spec.candidates.min(ordered.len());
        let cands: Vec<(String, String)> = ordered.iter().take(n).filter_map(|(c, _, _, _)| db.query_one("SELECT text FROM chunks WHERE chunk_id=?1", &[c]).ok().flatten().map(|r| (c.clone(), r["text"].as_str().unwrap_or("").chars().take(max_slice).collect::<String>()))).collect();
        for (id, s) in rr.rerank(query, &cands, &p.root)? { rerank_scores.insert(id, s); }
        reranker_used = rr.spec.to_value();
        if !rerank_scores.is_empty() {
            let (mut scored, rest): (Vec<_>, Vec<_>) = ordered.into_iter().partition(|(c, _, _, _)| rerank_scores.contains_key(c));
            scored.sort_by(|a, b| rerank_scores[&b.0].partial_cmp(&rerank_scores[&a.0]).unwrap_or(std::cmp::Ordering::Equal).then(a.0.cmp(&b.0)));
            scored.extend(rest); ordered = scored;
        }
    }
    // --- authority + namespace/role filter, active-state precedence, dedup per artefact
    let mut hits: Vec<Hit> = vec![];
    let mut per_artifact: HashMap<String, usize> = HashMap::new();
    let (mut excluded, mut excluded_ns) = (0usize, 0usize);
    let mut art_cache: HashMap<String, Option<Value>> = HashMap::new();
    for (chunk_id, score, artifact_id, rts) in ordered {
        if hits.len() >= k { break; }
        let art = art_cache.entry(artifact_id.clone()).or_insert_with(|| db.artifact(&artifact_id).ok().flatten()).clone();
        let Some(art) = art else { continue };
        let status = art["status"].as_str().unwrap_or("").to_string();
        let record_type = art["record_type"].as_str().unwrap_or("").to_string();
        if !opts.record_types.is_empty() && !opts.record_types.contains(&record_type) { continue; }
        let ns = art["namespace"].as_str().unwrap_or("").to_string();
        let allowed_roles: Vec<String> = namespaces.get(&ns).and_then(|n| n.get("roles")).and_then(|r| r.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_else(|| vec!["all".into()]);
        if !role_in(p, &p.role, &allowed_roles) { excluded_ns += 1; continue; }
        let superseded_by = art["superseded_by"].as_str().unwrap_or("").to_string();
        let mut flags = vec![];
        if !opts.include_historical && (excl_status.contains(&status) || !superseded_by.is_empty()) { excluded += 1; continue; }
        if !opts.include_archive && art["default_retrieval"].as_i64() == Some(0) { excluded += 1; continue; }
        if !superseded_by.is_empty() { flags.push(format!("superseded_by:{superseded_by}")); }
        let n = per_artifact.entry(artifact_id.clone()).or_insert(0);
        if *n >= 2 { continue; }
        *n += 1;
        let Some(ch) = db.query_one("SELECT section, level, text, parent_chunk_id FROM chunks WHERE chunk_id=?1", &[&chunk_id])? else { continue };
        let excerpt: String = ch["text"].as_str().unwrap_or("").chars().take(max_slice).collect();
        hits.push(Hit { artifact_id: artifact_id.clone(), path: art["path"].as_str().unwrap_or("").into(), chunk_id: chunk_id.clone(), section: ch["section"].as_str().unwrap_or("").into(), level: ch["level"].as_str().unwrap_or("").into(), score, routes: rts, status, state_class: art["state_class"].as_str().unwrap_or("").into(), record_type, excerpt, parent_excerpt: None, neighbours: vec![], flags, rerank_score: rerank_scores.get(&chunk_id).copied() });
    }
    for h in hits.iter_mut().take(parent_top) {
        if h.level == "child" { if let Some(ch) = db.query_one("SELECT c2.text FROM chunks c1 JOIN chunks c2 ON c2.chunk_id=c1.parent_chunk_id WHERE c1.chunk_id=?1", &[&h.chunk_id])? { h.parent_excerpt = Some(ch["text"].as_str().unwrap_or("").chars().take(max_slice).collect()); } }
        h.neighbours = graph::neighbours(db, &h.artifact_id, graph_depth)?.into_iter().map(|r| format!("{} {}", r.via, r.node)).take(12).collect();
    }
    let idx_hash = db.get_meta("index_manifest_hash").and_then(|v| v.as_str().map(|s| s.to_string())).unwrap_or_default();
    let latency = started.elapsed().as_millis();
    if opts.log { let _ = db.exec("INSERT INTO retrieval_log(ts, query, routes, hits, latency_ms) VALUES (?1,?2,?3,?4,?5)", &[&crate::util::now_iso(), &query, &routes.join(","), &serde_json::to_string(&hits.iter().map(|h| h.artifact_id.clone()).collect::<Vec<_>>())?, &(latency as f64)]); }
    Ok(RetrievalResult { query: query.into(), strategy: if routes.len() > 1 { "fusion".into() } else { routes.first().cloned().unwrap_or_default() }, routes, hits, index_version: crate::INDEX_VERSION.into(), index_manifest_hash: idx_hash, latency_ms: latency, excluded_by_authority: excluded, excluded_by_namespace: excluded_ns, embedder: embedder_used, reranker: reranker_used })
}

/// Held-out memory regression (framework §17): Recall@K, MRR, precision@K, stale/superseded hit rates; a set smaller
/// than MEMORY_POLICY.regression.min_queries is reported as UNMEASURED (never as green).
pub fn run_heldout(p: &Project, db: &RuntimeDb, heldout: &Value) -> Result<Value> { run_heldout_with(p, db, heldout, None, None) }

pub fn run_heldout_with(p: &Project, db: &RuntimeDb, heldout: &Value, embed_override: Option<crate::memory::embedder::EmbedSpec>, rerank_override: Option<String>) -> Result<Value> {
    let all: Vec<Value> = heldout.get("queries").and_then(|q| q.as_array()).cloned().unwrap_or_default();
    let queries: Vec<Value> = all.iter().filter(|q| !q.get("pending").and_then(|v| v.as_bool()).unwrap_or(false)).cloned().collect();
    let pending = all.len() - queries.len();
    let pol = p.policies();
    let min_queries = pol.get_i64("MEMORY_POLICY", "regression.min_queries", 5).max(0) as usize;
    let mut results = vec![];
    let (mut recall_sum, mut mrr_sum, mut prec_sum, mut stale_hits, mut superseded_hits, mut total_hits, mut forbidden_violations, mut latency_sum) = (0.0, 0.0, 0.0, 0usize, 0usize, 0usize, 0usize, 0u128);
    let fresh = crate::memory::manifest::freshness(p);
    let stale_paths: HashSet<String> = fresh.stale.iter().cloned().collect();
    let mut by_category: HashMap<String, (usize, f64)> = HashMap::new();
    for q in &queries {
        let text = q["query"].as_str().unwrap_or("");
        let k = q.get("k").and_then(|v| v.as_u64()).unwrap_or(8) as usize;
        let expected: Vec<String> = q.get("expected_refs").and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
        let forbidden: Vec<String> = q.get("forbidden").and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
        let route = q.get("route").and_then(|v| v.as_str()).map(|s| s.to_string());
        let res = retrieve(p, db, text, RetrieveOptions { k, route, embed_override: embed_override.clone(), rerank_override: rerank_override.clone(), ..Default::default() })?;
        let got: Vec<String> = res.hits.iter().map(|h| h.artifact_id.clone()).collect();
        let found = expected.iter().filter(|e| got.contains(e) || res.hits.iter().any(|h| h.path == **e)).count();
        let recall = if expected.is_empty() { 1.0 } else { found as f64 / expected.len() as f64 };
        let precision = if got.is_empty() { 0.0 } else { got.iter().filter(|g| expected.contains(g)).count() as f64 / got.len() as f64 };
        let rr = expected.iter().filter_map(|e| got.iter().position(|g| g == e).map(|i| 1.0 / (i as f64 + 1.0))).fold(0.0f64, f64::max);
        let viol: Vec<String> = forbidden.iter().filter(|f| got.contains(f)).cloned().collect();
        forbidden_violations += viol.len();
        for h in &res.hits { total_hits += 1; if stale_paths.contains(&h.path) { stale_hits += 1; }
            if h.flags.iter().any(|f| f.starts_with("superseded_by")) || h.status == "SUPERSEDED" { superseded_hits += 1; } }
        recall_sum += recall; mrr_sum += rr; prec_sum += precision; latency_sum += res.latency_ms;
        let cat = q.get("category").and_then(|v| v.as_str()).unwrap_or("uncategorised").to_string();
        let e = by_category.entry(cat).or_insert((0, 0.0)); e.0 += 1; e.1 += recall;
        results.push(json!({"id": q["id"], "query": text, "category": q.get("category"), "routes": res.routes, "expected": expected, "got": got, "recall": recall, "precision": precision, "rr": rr, "forbidden_hits": viol, "latency_ms": res.latency_ms, "pass": recall >= 1.0 - 1e-9 && viol.is_empty()}));
    }
    let n = queries.len().max(1) as f64;
    let min_recall = pol.get_f64("MEMORY_POLICY", "regression.min_recall_at_k", 0.8);
    let min_mrr = pol.get_f64("MEMORY_POLICY", "regression.min_mrr", 0.5);
    let max_stale = pol.get_f64("MEMORY_POLICY", "regression.max_stale_hit_rate", 0.0);
    let max_sup = pol.get_f64("MEMORY_POLICY", "regression.max_superseded_hit_rate", 0.0);
    let (recall, mrr, precision) = (recall_sum / n, mrr_sum / n, prec_sum / n);
    let stale_rate = if total_hits == 0 { 0.0 } else { stale_hits as f64 / total_hits as f64 };
    let sup_rate = if total_hits == 0 { 0.0 } else { superseded_hits as f64 / total_hits as f64 };
    let measured = queries.len() >= min_queries && !queries.is_empty();
    let thresholds_met = recall >= min_recall && mrr >= min_mrr && stale_rate <= max_stale && sup_rate <= max_sup && forbidden_violations == 0;
    let pass = measured && thresholds_met;
    let status = if !measured { "UNMEASURED" } else if pass { "PASS" } else { "FAIL" };
    Ok(json!({"queries": queries.len(), "pending_queries": pending, "min_queries": min_queries, "measured": measured, "status": status, "recall_at_k": recall, "mrr": mrr, "precision_at_k": precision, "stale_hit_rate": stale_rate, "superseded_hit_rate": sup_rate, "forbidden_violations": forbidden_violations, "avg_latency_ms": if queries.is_empty() { 0.0 } else { latency_sum as f64 / n },
              "by_category": by_category.iter().map(|(c, (n, r))| json!({"category": c, "queries": n, "recall": r / *n as f64})).collect::<Vec<_>>(),
              "thresholds": {"min_recall_at_k": min_recall, "min_mrr": min_mrr, "max_stale_hit_rate": max_stale, "max_superseded_hit_rate": max_sup, "min_queries": min_queries}, "thresholds_met": thresholds_met, "pass": pass, "results": results, "index_fresh": fresh.fresh}))
}

pub fn edge_types() -> std::collections::BTreeMap<String, usize> { graph::EDGE_TYPES.iter().enumerate().map(|(i, t)| (t.to_string(), i)).collect() }
