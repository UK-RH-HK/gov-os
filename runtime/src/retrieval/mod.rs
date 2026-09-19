//! Retrieval router (framework §14): classify the question, admit only what the acting role may see as current
//! authority, run routes, fuse, rerank (if pinned), de-duplicate, expand. The query is embedded with the
//! implementation the live index was built with.
//!
//! Order of the pipeline (framework §14 "query ↓ authority + namespace filter ↓ lexical + vector + graph/code
//! candidates ↓ rank fusion ↓ reranker ↓ deduplication ↓ active-state precedence ↓ expansion"; BC-P2-26):
//! * **Filters first.** The authority filter (excluded lifecycle statuses, superseded, not-default-retrievable) and
//!   the namespace/role filter decide *admission* before any route truncates its candidate pool, so excluded
//!   material can neither exhaust the pool nor cross the plugin boundary to a reranker (Contract v3:241).
//! * **Routing.** Known IDs → structured lookup; paths **and bare file names** → path lookup; symbols → code-symbol
//!   route; exact text → lexical; dependency/impact questions about records **or code entities** → graph
//!   traversal; concepts → semantic (Contract v3:246, :316-321).
//! * **Primary route.** When the question has one direct answer route (an exact ID, path or symbol lookup, or a
//!   dependency/impact question), that route's answers rank first and fused lexical/semantic candidates follow, so
//!   graph answers are never buried by fusion (Contract v3:319).
//! * **De-duplication.** At most two slices per artefact, and content-level duplicates across artefacts (a verbatim
//!   copy under another path, an identical slice) are suppressed and reported (Contract v3:291).
//! * **Failure memory.** For an agent's logged query, a result whose evidence does not cover the question becomes a
//!   durable retrieval-miss record (framework §18); a reranker or embedder failure becomes a tool-failure record.
use crate::authority::role_in;
use crate::graph;
use crate::memory::db::RuntimeDb;
use crate::memory::embedder::{for_query, Reranker};
use crate::memory::embeddings::{cosine, tokenize};
use crate::{GovError, Project, Result};
use regex::Regex;
use serde_json::{json, Value};
use std::collections::{BTreeSet, HashMap, HashSet};
use std::sync::OnceLock;

#[derive(Debug, Clone, Default)]
pub struct RetrieveOptions {
    pub k: usize,
    pub include_historical: bool,
    pub include_archive: bool,
    pub route: Option<String>,
    pub record_types: Vec<String>,
    /// An agent's ad-hoc query: logged in the retrieval log and, when its evidence does not cover the question,
    /// recorded in failure memory as a retrieval miss (framework §18).
    pub log: bool,
    /// Benchmark-only: query against an index built with this spec instead of the policy pin.
    pub embed_override: Option<crate::memory::embedder::EmbedSpec>,
    pub rerank_override: Option<String>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct Hit {
    pub artifact_id: String,
    pub path: String,
    pub chunk_id: String,
    pub section: String,
    pub level: String,
    pub score: f64,
    pub routes: Vec<String>,
    pub status: String,
    pub state_class: String,
    pub record_type: String,
    pub excerpt: String,
    pub parent_excerpt: Option<String>,
    pub neighbours: Vec<String>,
    pub flags: Vec<String>,
    pub rerank_score: Option<f64>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct RetrievalResult {
    pub query: String,
    pub routes: Vec<String>,
    pub strategy: String,
    pub hits: Vec<Hit>,
    pub index_version: String,
    pub index_manifest_hash: String,
    pub latency_ms: u128,
    pub excluded_by_authority: usize,
    pub excluded_by_namespace: usize,
    pub embedder: Value,
    pub reranker: Value,
    /// The route whose answers rank first (exact lookups, dependency/impact questions); none for pure fusion.
    pub primary_route: Option<String>,
    /// Slices withheld because the same content was already returned from another artefact.
    pub duplicates_suppressed: Vec<Value>,
    /// Share of the question's (IDF-weighted) terms held by the best returned artefact (logged queries only).
    pub evidence_coverage: Option<f64>,
    /// Failure-memory outcome when this query was recorded as a retrieval miss.
    pub failure_record: Option<Value>,
}

fn id_rx() -> &'static Regex {
    static R: OnceLock<Regex> = OnceLock::new();
    R.get_or_init(|| Regex::new(r"\b[A-Z]{1,6}-[0-9]{2,}[A-Za-z0-9.-]*\b").unwrap())
}
fn path_rx() -> &'static Regex {
    static R: OnceLock<Regex> = OnceLock::new();
    R.get_or_init(|| Regex::new(r"[\w./-]+/[\w.-]+\.[A-Za-z0-9]{1,6}").unwrap())
}
/// A bare file name: `runbook.md`, `ledger.rs`, `format.test.ts`, `.env.example` (an extension that starts with a
/// letter; `Order.total_cents` is a dotted symbol, not a file name).
fn filename_rx() -> &'static Regex {
    static R: OnceLock<Regex> = OnceLock::new();
    R.get_or_init(|| {
        Regex::new(
            r"(?:^|[\s(`'])([\w-]*[\w-]?(?:\.[\w-]+)*\.[A-Za-z][A-Za-z0-9]{0,7})(?:$|[\s)`',?.;:])",
        )
        .unwrap()
    })
}
fn symbol_rx() -> &'static Regex {
    static R: OnceLock<Regex> = OnceLock::new();
    R.get_or_init(|| Regex::new(r"\b(?:[A-Za-z_]\w*(?:::|\.))+[A-Za-z_]\w*\b|\b(?:def|fn|class|struct|function)\s+([A-Za-z_]\w*)|\bsymbol:([A-Za-z_][\w.]*)").unwrap())
}
fn ident_rx() -> &'static Regex {
    static R: OnceLock<Regex> = OnceLock::new();
    R.get_or_init(|| Regex::new(r"^[A-Za-z_][A-Za-z0-9_]{2,}$").unwrap())
}
fn quoted_rx() -> &'static Regex {
    static R: OnceLock<Regex> = OnceLock::new();
    R.get_or_init(|| Regex::new(r#""([^"]{2,})""#).unwrap())
}
const GRAPH_WORDS: &[&str] = &[
    "depend",
    "impact",
    "affect",
    "block",
    "downstream",
    "upstream",
    "uses",
    "consumer",
    "implements",
    "tests for",
    "what breaks",
    "related to",
    "callers",
    "calls ",
    "who calls",
    "extend",
    "subclass",
];
const CONCEPT_WORDS: &[&str] = &[
    "why",
    "rationale",
    "history",
    "reason",
    "how",
    "approach",
    "background",
    "explain",
    "decided",
    "lesson",
];
/// Words of a question that are never code entities or evidence terms.
const QUESTION_WORDS: &[&str] = &[
    "what",
    "which",
    "who",
    "whom",
    "whose",
    "where",
    "when",
    "why",
    "how",
    "the",
    "a",
    "an",
    "of",
    "to",
    "and",
    "or",
    "in",
    "on",
    "for",
    "is",
    "are",
    "be",
    "by",
    "with",
    "as",
    "at",
    "it",
    "this",
    "that",
    "from",
    "was",
    "we",
    "our",
    "not",
    "no",
    "yes",
    "if",
    "then",
    "than",
    "so",
    "do",
    "does",
    "did",
    "can",
    "could",
    "would",
    "should",
    "will",
    "there",
    "their",
    "they",
    "its",
    "into",
    "about",
    "any",
    "all",
    "some",
    "i",
    "me",
    "my",
    "you",
    "your",
    "changes",
    "change",
    "changing",
    "changed",
    "breaks",
    "break",
    "depends",
    "depend",
    "impact",
    "affects",
    "affect",
    "uses",
    "use",
    "used",
    "implements",
    "implement",
    "extends",
    "extend",
    "calls",
    "call",
    "callers",
    "related",
    "tests",
    "test",
    "upstream",
    "downstream",
    "consumers",
    "consumer",
    "subclasses",
    "subclass",
    "if",
];

pub fn is_bare_identifier(q: &str) -> bool {
    ident_rx().is_match(q.trim()) && !id_rx().is_match(q.trim())
}

/// Bare file names in the query (tokens shaped like `name.ext`).
pub fn filenames(query: &str) -> Vec<String> {
    filename_rx()
        .captures_iter(query)
        .map(|c| c[1].trim_matches('.').to_string())
        .filter(|f| !f.contains('/') && f.contains('.') && !id_rx().is_match(f))
        .collect()
}

pub fn classify(query: &str) -> Vec<String> {
    let mut routes = vec![];
    let q = query.trim();
    let ql = q.to_lowercase();
    if is_bare_identifier(q) {
        return vec!["symbol".into(), "lexical".into()];
    }
    // a single literal-like token (hyphens/underscores/digits/upper-case marker) is an exact lookup, not a concept:
    // exact routes only, never an OR-of-subtokens lexical match or a semantic nearest-neighbour over its n-grams
    let single = !q.contains(char::is_whitespace);
    let literal_like = q.contains('-')
        || q.contains('_')
        || q.chars().any(|c| c.is_ascii_digit())
        || q.chars().filter(|c| c.is_uppercase()).count() >= 3;
    let bare_files = filenames(q);
    if single
        && literal_like
        && !id_rx().is_match(q)
        && !path_rx().is_match(q)
        && !symbol_rx().is_match(q)
        && bare_files.is_empty()
    {
        return vec!["lexical_exact".into()];
    }
    if id_rx().is_match(q) {
        routes.push("structured".to_string());
    }
    if path_rx().is_match(q) || !bare_files.is_empty() {
        routes.push("path".to_string());
    }
    if symbol_rx().is_match(q) {
        routes.push("symbol".to_string());
    }
    if quoted_rx().is_match(q) {
        routes.push("lexical_exact".to_string());
    }
    if GRAPH_WORDS.iter().any(|w| ql.contains(w)) && id_rx().is_match(q) {
        routes.push("graph".to_string());
    }
    let conceptual = CONCEPT_WORDS.iter().any(|w| {
        ql.split_whitespace()
            .any(|t| t.trim_matches(|c: char| !c.is_alphanumeric()) == *w)
    });
    if routes.is_empty() || conceptual || q.split_whitespace().count() >= 4 {
        routes.push("lexical".to_string());
        routes.push("semantic".to_string());
    }
    if routes.iter().any(|r| r == "structured") && routes.len() == 1 {
        routes.push("lexical".to_string());
    }
    // a bare file name is also found by the lexical store (its path is part of the document chunk)
    if single && !bare_files.is_empty() && !routes.iter().any(|r| r == "lexical") {
        routes.push("lexical".to_string());
    }
    routes.dedup();
    routes
}

fn fts_query(q: &str) -> String {
    let mut parts: Vec<String> = vec![];
    for m in quoted_rx().captures_iter(q) {
        parts.push(format!("\"{}\"", m[1].replace('"', "")));
    }
    let stripped = quoted_rx().replace_all(q, " ");
    let mut toks: Vec<String> = tokenize(&stripped)
        .into_iter()
        .filter(|t| t.len() > 1)
        .collect::<HashSet<_>>()
        .into_iter()
        .collect();
    toks.sort();
    for t in toks {
        parts.push(format!("\"{}\"", t.replace('"', "")));
    }
    if parts.is_empty() {
        "\"\"".into()
    } else {
        parts.join(" OR ")
    }
}

fn chunk_for(db: &RuntimeDb, aid: &str, sections: &[&str]) -> Result<Option<String>> {
    for sec in sections {
        if sec.is_empty() {
            continue;
        }
        if let Some(ch) = db.query_one(
            "SELECT chunk_id FROM chunks WHERE artifact_id=?1 AND section=?2 ORDER BY ordinal LIMIT 1",
            &[&aid, sec],
        )? {
            return Ok(ch["chunk_id"].as_str().map(|s| s.to_string()));
        }
    }
    Ok(db
        .query_one(
            "SELECT chunk_id FROM chunks WHERE artifact_id=?1 ORDER BY ordinal LIMIT 1",
            &[&aid],
        )?
        .and_then(|c| c["chunk_id"].as_str().map(|s| s.to_string())))
}

fn like_escape(s: &str) -> String {
    s.replace('\\', "\\\\")
        .replace('%', "\\%")
        .replace('_', "\\_")
}

// ------------------------------------------------------------------------------------------------ admission

/// Why an artefact is not admitted to this query's candidates.
#[derive(Clone, Copy, PartialEq, Eq)]
enum Exclusion {
    Authority,
    Namespace,
    RecordType,
}

/// Admission decided once per query, before any route runs: the authority filter, the namespace/role filter and
/// the record-type filter, over every artefact of the index.
struct Admission {
    excluded: HashMap<String, Exclusion>,
    known: HashSet<String>,
}

impl Admission {
    fn new(p: &Project, db: &RuntimeDb, opts: &RetrieveOptions) -> Result<Self> {
        let pol = p.policies();
        let excl_status: Vec<String> =
            pol.get_list("AUTHORITY_POLICY", "retrieval_default_excludes_statuses");
        let namespaces = pol.get("MEMORY_POLICY", "namespaces").unwrap_or(json!({}));
        let mut ns_ok: HashMap<String, bool> = HashMap::new();
        let mut excluded = HashMap::new();
        let mut known = HashSet::new();
        for a in db.query(
            "SELECT artifact_id, status, superseded_by, default_retrieval, namespace, record_type FROM artifacts",
            &[],
        )? {
            let aid = a["artifact_id"].as_str().unwrap_or("").to_string();
            known.insert(aid.clone());
            let record_type = a["record_type"].as_str().unwrap_or("").to_string();
            if !opts.record_types.is_empty() && !opts.record_types.contains(&record_type) {
                excluded.insert(aid, Exclusion::RecordType);
                continue;
            }
            let ns = a["namespace"].as_str().unwrap_or("").to_string();
            let allowed = *ns_ok.entry(ns.clone()).or_insert_with(|| {
                let roles: Vec<String> = namespaces
                    .get(&ns)
                    .and_then(|n| n.get("roles"))
                    .and_then(|r| r.as_array())
                    .map(|a| {
                        a.iter()
                            .filter_map(|x| x.as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_else(|| vec!["all".into()]);
                role_in(p, &p.role, &roles)
            });
            if !allowed {
                excluded.insert(aid, Exclusion::Namespace);
                continue;
            }
            let status = a["status"].as_str().unwrap_or("");
            let superseded = !a["superseded_by"].as_str().unwrap_or("").is_empty();
            if !opts.include_historical && (excl_status.iter().any(|s| s == status) || superseded) {
                excluded.insert(aid, Exclusion::Authority);
                continue;
            }
            if !opts.include_archive && a["default_retrieval"].as_i64() == Some(0) {
                excluded.insert(aid, Exclusion::Authority);
            }
        }
        Ok(Admission { excluded, known })
    }
    fn admits(&self, aid: &str) -> bool {
        self.known.contains(aid) && !self.excluded.contains_key(aid)
    }
    fn reason(&self, aid: &str) -> Option<Exclusion> {
        self.excluded.get(aid).copied()
    }
}

/// Exclusions observed inside the candidate windows the routes would have used without filters.
#[derive(Default)]
struct ExclusionTally {
    authority: BTreeSet<String>,
    namespace: BTreeSet<String>,
}

impl ExclusionTally {
    fn note(&mut self, adm: &Admission, chunk: &str, aid: &str) {
        match adm.reason(aid) {
            Some(Exclusion::Authority) => {
                self.authority.insert(chunk.to_string());
            }
            Some(Exclusion::Namespace) => {
                self.namespace.insert(chunk.to_string());
            }
            _ => {}
        }
    }
}

/// Keep admitted candidates, in order, until `pool` are kept; exclusions ranked inside the unfiltered window of
/// `pool` are tallied.
fn admit_ranked(
    ranked: impl IntoIterator<Item = (String, String)>,
    adm: &Admission,
    pool: usize,
    tally: &mut ExclusionTally,
) -> Vec<(String, String)> {
    let mut out = vec![];
    let mut seen = HashSet::new();
    for (i, (chunk, aid)) in ranked.into_iter().enumerate() {
        if !seen.insert(chunk.clone()) {
            continue;
        }
        if adm.admits(&aid) {
            if out.len() < pool {
                out.push((chunk, aid));
            }
        } else if i < pool {
            tally.note(adm, &chunk, &aid);
        }
        if out.len() >= pool && i >= pool {
            break;
        }
    }
    out
}

// ------------------------------------------------------------------------------------------------ route plan

/// Code entities a dependency/impact question names: identifier-shaped words of the question that are symbols or
/// files of the index. Returns (name, defining artefacts).
fn code_entities(db: &RuntimeDb, query: &str) -> Result<Vec<(String, Vec<String>)>> {
    static TOK: OnceLock<Regex> = OnceLock::new();
    let tok = TOK.get_or_init(|| Regex::new(r"[A-Za-z_][\w.:/-]*[\w]").unwrap());
    let mut out: Vec<(String, Vec<String>)> = vec![];
    for m in tok.find_iter(query) {
        let t = m.as_str().trim_end_matches(['.', ':']);
        if t.len() < 3 || QUESTION_WORDS.contains(&t.to_lowercase().as_str()) || id_rx().is_match(t)
        {
            continue;
        }
        if out.iter().any(|(n, _)| n == t) {
            continue;
        }
        let last = t.rsplit(['.', ':']).next().unwrap_or(t).to_string();
        let mut defs: Vec<String> = db
            .query(
                "SELECT DISTINCT artifact_id FROM symbols WHERE (qualname=?1 OR name=?2) AND kind NOT IN ('module','route') ORDER BY artifact_id LIMIT 10",
                &[&t, &last],
            )?
            .into_iter()
            .filter_map(|r| r["artifact_id"].as_str().map(|s| s.to_string()))
            .collect();
        if defs.is_empty() && (t.contains('/') || t.contains('.')) {
            let pat = format!("%/{}", like_escape(t));
            defs = db
                .query(
                    "SELECT artifact_id FROM artifacts WHERE record_type='file' AND (path=?1 OR path LIKE ?2 ESCAPE '\\') ORDER BY length(path), path LIMIT 5",
                    &[&t, &pat],
                )?
                .into_iter()
                .filter_map(|r| r["artifact_id"].as_str().map(|s| s.to_string()))
                .collect();
        }
        if !defs.is_empty() {
            out.push((last, defs));
        }
    }
    Ok(out)
}

/// Graph answers for a dependency/impact question: for a code entity, its direct dependants first (callers at the
/// calling unit, subtypes/implementers at the subtype — in the same file too), then the impact set of its defining
/// artefacts; for records, the impact set of the named IDs. Returns `(answers, context)`: the answers are the
/// question's direct answer (the primary tier); the context is the rest of the neighbourhood. Ordered by distance,
/// deterministic.
#[allow(clippy::type_complexity)]
fn graph_candidates(
    db: &RuntimeDb,
    query: &str,
    entities: &[(String, Vec<String>)],
) -> Result<(Vec<(String, String)>, Vec<(String, String)>)> {
    let mut answers: Vec<(String, String)> = vec![];
    let mut context: Vec<(String, String)> = vec![];
    let mut seen_nodes: HashSet<String> = HashSet::new();
    let push = |v: &mut Vec<(String, String)>, ch: Option<String>, node: &str| {
        if let Some(c) = ch {
            if !v.iter().any(|(x, _)| x == &c) {
                v.push((c, node.to_string()));
            }
        }
    };
    let mut seeds: Vec<String> = id_rx()
        .find_iter(query)
        .map(|m| m.as_str().to_string())
        .collect();
    for (name, defs) in entities {
        for r in db.query(
            "SELECT DISTINCT a.artifact_id, sr.target FROM symbol_refs sr JOIN artifacts a ON a.path=sr.path WHERE sr.name=?1 AND sr.kind IN ('call','inherits','implements') ORDER BY a.artifact_id, sr.target",
            &[name],
        )? {
            let aid = r["artifact_id"].as_str().unwrap_or("").to_string();
            let unit = r["target"].as_str().unwrap_or("").trim_start_matches("symbol:").to_string();
            if unit == *name || unit.ends_with(&format!(".{name}")) {
                continue; // the entity's own definition (e.g. a recursive call)
            }
            let ch = chunk_for(db, &aid, &[&unit])?;
            push(&mut answers, ch, &aid);
            if !defs.contains(&aid) {
                seen_nodes.insert(aid);
            }
        }
        seeds.extend(defs.iter().cloned());
    }
    seeds.sort();
    seeds.dedup();
    let mut reach: Vec<graph::Reach> = graph::impact_set(db, &seeds, 2)?;
    reach.sort_by(|a, b| a.hop.cmp(&b.hop).then(a.node.cmp(&b.node)));
    let impact_nodes: HashSet<String> = reach.iter().map(|r| r.node.clone()).collect();
    for r in reach {
        if seeds.contains(&r.node) || !seen_nodes.insert(r.node.clone()) {
            continue;
        }
        let ch = chunk_for(db, &r.node, &[])?;
        push(&mut answers, ch, &r.node);
    }
    let mut near: Vec<graph::Reach> = vec![];
    for s in &seeds {
        for r in graph::neighbours(db, s, 2)? {
            if !impact_nodes.contains(&r.node) && !seeds.contains(&r.node) {
                near.push(r);
            }
        }
    }
    near.sort_by(|a, b| a.hop.cmp(&b.hop).then(a.node.cmp(&b.node)));
    for r in near {
        if !seen_nodes.insert(r.node.clone()) {
            continue;
        }
        let ch = chunk_for(db, &r.node, &[])?;
        push(&mut context, ch, &r.node);
    }
    Ok((answers, context))
}

/// Structural answers the code-structural store holds for a question: route registrations whose path the question
/// names (`/orders/<id>`) and database models whose table the question names (or whose class it names when it asks
/// about a model/table/entity). Candidates are the handler's or model's own chunk.
fn structural_candidates(db: &RuntimeDb, query: &str) -> Result<Vec<(String, String)>> {
    static URL: OnceLock<Regex> = OnceLock::new();
    static TOK: OnceLock<Regex> = OnceLock::new();
    let url = URL.get_or_init(|| Regex::new(r#"(?:^|[\s'"(`])(/[\w\-./<>:{}*]+)"#).unwrap());
    let tok = TOK.get_or_init(|| Regex::new(r"[A-Za-z_][\w]*").unwrap());
    let mut v: Vec<(String, String)> = vec![];
    for c in url.captures_iter(query) {
        let u = c[1].trim_end_matches(['.', ',', '?', ')']).to_string();
        if u.len() < 2 {
            continue;
        }
        let pat = format!("{}%", like_escape(&u));
        for r in db.query(
            "SELECT artifact_id, parent FROM symbols WHERE kind='route' AND (name=?1 OR name LIKE ?2 ESCAPE '\\') ORDER BY length(name), path LIMIT 10",
            &[&u, &pat],
        )? {
            let aid = r["artifact_id"].as_str().unwrap_or("").to_string();
            let parent = r["parent"].as_str().unwrap_or("").to_string();
            if let Some(ch) = chunk_for(db, &aid, &[&parent])? {
                v.push((ch, aid));
            }
        }
    }
    let ql = query.to_lowercase();
    let asks_model = ["model", "table", "entity", "schema", "orm"]
        .iter()
        .any(|w| ql.contains(w));
    for m in tok.find_iter(query) {
        let t = m.as_str();
        if t.len() < 3 || QUESTION_WORDS.contains(&t.to_lowercase().as_str()) {
            continue;
        }
        let table = format!("table={t} %");
        for r in db.query(
            "SELECT artifact_id, parent FROM symbols WHERE kind='db_model' AND (signature LIKE ?1 OR (?2 = 1 AND lower(name) = lower(?3))) ORDER BY path LIMIT 10",
            &[&table, &(asks_model as i64), &t],
        )? {
            let aid = r["artifact_id"].as_str().unwrap_or("").to_string();
            let parent = r["parent"].as_str().unwrap_or("").to_string();
            if let Some(ch) = chunk_for(db, &aid, &[&parent])? {
                v.push((ch, aid));
            }
        }
    }
    Ok(v)
}

// ------------------------------------------------------------------------------------------------ evidence coverage

/// IDF-weighted share of the question's terms held by the best returned artefact (framework §17 "retrieval-to-answer
/// evidence coverage"), the question's terms, and the terms the index holds nowhere.
fn evidence_coverage(db: &RuntimeDb, query: &str, hits: &[Hit]) -> (f64, Vec<String>, Vec<String>) {
    static TOK: OnceLock<Regex> = OnceLock::new();
    let tok = TOK.get_or_init(|| Regex::new(r"[A-Za-z0-9]+").unwrap());
    let mut terms: Vec<String> = vec![];
    for m in tok.find_iter(&query.to_lowercase()) {
        let t = m.as_str().to_string();
        if t.len() < 2 || QUESTION_WORDS.contains(&t.as_str()) || terms.contains(&t) {
            continue;
        }
        terms.push(t);
    }
    if terms.is_empty() {
        return (1.0, terms, vec![]);
    }
    let n: f64 = db.count("chunks_fts").max(1) as f64;
    let mut weights = vec![];
    let mut holders: Vec<HashSet<String>> = vec![];
    let mut absent = vec![];
    for t in &terms {
        let set: HashSet<String> = db
            .query(
                "SELECT chunk_id FROM chunks_fts WHERE chunks_fts MATCH ?1",
                &[&format!("\"{t}\"")],
            )
            .unwrap_or_default()
            .into_iter()
            .filter_map(|r| r["chunk_id"].as_str().map(|s| s.to_string()))
            .collect();
        if set.is_empty() {
            absent.push(t.clone());
        }
        weights.push((1.0 + n / (1.0 + set.len() as f64)).ln());
        holders.push(set);
    }
    let total: f64 = weights.iter().sum::<f64>().max(1e-9);
    // an answer is an artefact: a returned artefact covers a term when any of its chunks holds it
    let artefact_of = |chunk: &str| {
        chunk
            .rsplit_once('#')
            .map(|(a, _)| a.to_string())
            .unwrap_or_default()
    };
    let holders_by_artefact: Vec<HashSet<String>> = holders
        .iter()
        .map(|s| s.iter().map(|c| artefact_of(c)).collect())
        .collect();
    let best = hits
        .iter()
        .map(|h| {
            holders_by_artefact
                .iter()
                .zip(&weights)
                .filter(|(s, _)| s.contains(&h.artifact_id))
                .map(|(_, w)| *w)
                .sum::<f64>()
                / total
        })
        .fold(0.0f64, f64::max);
    (best, terms, absent)
}

fn is_tool_failure(e: &GovError) -> bool {
    !matches!(
        e.code.as_str(),
        "EMBEDDER_MISMATCH" | "RERANKER_MISMATCH" | "INDEX_MISSING" | "USAGE"
    )
}

fn note_tool_failure(p: &Project, kind: &str, id: &str, version: &str, e: &GovError) {
    let t = crate::memory::failures::ToolFailure {
        tool_kind: kind.into(),
        tool_id: id.into(),
        version: version.into(),
        code: e.code.clone(),
        message: e.message.clone(),
        operation: "memory query".into(),
        affected: vec![],
    };
    let _ = crate::memory::failures::record_tool_failure(p, &t, true);
}

pub fn retrieve(
    p: &Project,
    db: &RuntimeDb,
    query: &str,
    opts: RetrieveOptions,
) -> Result<RetrievalResult> {
    let started = std::time::Instant::now();
    let pol = p.policies();
    let k = if opts.k == 0 {
        pol.get_i64("MEMORY_POLICY", "retrieval.default_k", 8) as usize
    } else {
        opts.k
    };
    let rrf_k = pol.get_f64("MEMORY_POLICY", "retrieval.rrf_k", 60.0);
    let parent_top = pol.get_i64("MEMORY_POLICY", "retrieval.parent_expansion_top_n", 3) as usize;
    let graph_depth = pol
        .get_i64("MEMORY_POLICY", "retrieval.graph_neighbour_depth", 1)
        .max(1) as usize;
    let max_slice = pol.get_i64("MEMORY_POLICY", "retrieval.max_slice_chars", 1600) as usize;
    let mut routes = match &opts.route {
        Some(r) => vec![r.clone()],
        None => classify(query),
    };
    // --- route plan: dependency/impact questions about code entities reach the graph; the direct answer route
    let q = query.trim();
    let ql = q.to_lowercase();
    let graph_intent = GRAPH_WORDS.iter().any(|w| ql.contains(w));
    let entities = if opts.route.is_none() && graph_intent && q.split_whitespace().count() > 1 {
        code_entities(db, q)?
    } else if opts.route.as_deref() == Some("graph") {
        code_entities(db, q)?
    } else {
        vec![]
    };
    if opts.route.is_none()
        && graph_intent
        && !entities.is_empty()
        && !routes.iter().any(|r| r == "graph")
    {
        routes.push("graph".into());
    }
    // route registrations and database models the question names are answered from the code-structural store
    let structural = if opts.route.is_none() || opts.route.as_deref() == Some("symbol") {
        structural_candidates(db, q)?
    } else {
        vec![]
    };
    if opts.route.is_none() && !structural.is_empty() && !routes.iter().any(|r| r == "symbol") {
        routes.push("symbol".into());
    }
    let bare_files = filenames(q);
    let primary: Option<String> = if opts.route.is_some() {
        None
    } else if routes.iter().any(|r| r == "graph") && graph_intent {
        Some("graph".into())
    } else if id_rx().find(q).map(|m| m.as_str() == q).unwrap_or(false) {
        Some("structured".into())
    } else if path_rx().find(q).map(|m| m.as_str() == q).unwrap_or(false)
        || (bare_files.len() == 1 && bare_files[0] == q)
    {
        Some("path".into())
    } else if is_bare_identifier(q)
        || symbol_rx()
            .find(q)
            .map(|m| m.as_str() == q)
            .unwrap_or(false)
    {
        Some("symbol".into())
    } else {
        None
    };
    let adm = Admission::new(p, db, &opts)?;
    let mut tally = ExclusionTally::default();
    let pool = (k * 4).max(20);
    let mut embedder_used = json!({"provider": "none"});
    let mut route_hits: Vec<(String, Vec<(String, String)>)> = vec![];
    let mut graph_answers: HashSet<String> = HashSet::new();
    for route in &routes {
        let ranked: Vec<(String, String)> = match route.as_str() {
            "structured" => {
                let mut v = vec![];
                for m in id_rx().find_iter(query) {
                    for r in db.query("SELECT chunk_id, artifact_id FROM chunks WHERE artifact_id=?1 ORDER BY ordinal LIMIT 3", &[&m.as_str()])? { v.push((r["chunk_id"].as_str().unwrap_or("").into(), r["artifact_id"].as_str().unwrap_or("").into())); }
                }
                admit_ranked(v, &adm, pool, &mut tally)
            }
            "path" => {
                let mut v = vec![];
                for m in path_rx().find_iter(query) {
                    let pat = format!("%{}", like_escape(m.as_str().trim_start_matches("./")));
                    for r in db.query("SELECT c.chunk_id, c.artifact_id FROM chunks c JOIN artifacts a ON a.artifact_id=c.artifact_id WHERE a.path LIKE ?1 ESCAPE '\\' ORDER BY length(a.path), a.path, c.ordinal LIMIT 3", &[&pat])? { v.push((r["chunk_id"].as_str().unwrap_or("").into(), r["artifact_id"].as_str().unwrap_or("").into())); }
                }
                // bare file names: exact base-name matches anywhere in the tree (shortest path first)
                for f in &bare_files {
                    let pat = format!("%/{}", like_escape(f));
                    for a in db.query("SELECT artifact_id FROM artifacts WHERE path=?1 OR path LIKE ?2 ESCAPE '\\' ORDER BY length(path), path LIMIT 5", &[f, &pat])? {
                        let aid = a["artifact_id"].as_str().unwrap_or("").to_string();
                        for r in db.query("SELECT chunk_id FROM chunks WHERE artifact_id=?1 ORDER BY ordinal LIMIT 2", &[&aid])? { v.push((r["chunk_id"].as_str().unwrap_or("").into(), aid.clone())); }
                    }
                }
                admit_ranked(v, &adm, pool, &mut tally)
            }
            "symbol" => {
                let mut v = structural.clone();
                let mut names: Vec<(String, String)> = symbol_rx()
                    .captures_iter(query)
                    .map(|c| {
                        let name = c
                            .get(1)
                            .or(c.get(2))
                            .map(|m| m.as_str().to_string())
                            .unwrap_or_else(|| c[0].to_string());
                        let last = name.rsplit(['.', ':']).next().unwrap_or(&name).to_string();
                        (name, last)
                    })
                    .collect();
                if names.is_empty() && is_bare_identifier(query) {
                    names.push((query.trim().to_string(), query.trim().to_string()));
                }
                for (name, last) in names {
                    for r in db.query("SELECT s.path, s.qualname, s.parent, s.artifact_id FROM symbols s WHERE (s.name=?1 OR s.qualname=?2) AND s.kind NOT IN ('module','route') ORDER BY s.path, s.lineno LIMIT 10", &[&last, &name])? {
                        let aid = r["artifact_id"].as_str().unwrap_or("").to_string();
                        let q = r["qualname"].as_str().unwrap_or("").to_string();
                        let parent = r["parent"].as_str().unwrap_or("").to_string();
                        if let Some(ch) = chunk_for(db, &aid, &[&q, &parent])? { v.push((ch, aid)); }
                    }
                    // references (calls) to the symbol, at the calling unit
                    for r in db.query("SELECT DISTINCT a.artifact_id, sr.target FROM symbol_refs sr JOIN artifacts a ON a.path=sr.path WHERE sr.name=?1 AND sr.kind='call' ORDER BY a.artifact_id, sr.target LIMIT 10", &[&last])? {
                        let aid = r["artifact_id"].as_str().unwrap_or("").to_string();
                        let unit = r["target"].as_str().unwrap_or("").to_string();
                        if let Some(ch) = chunk_for(db, &aid, &[&unit])? { v.push((ch, aid)); }
                    }
                }
                admit_ranked(v, &adm, pool, &mut tally)
            }
            "lexical" | "lexical_exact" => {
                let fq = if route == "lexical_exact" {
                    let caps: Vec<String> = quoted_rx()
                        .captures_iter(query)
                        .map(|m| format!("\"{}\"", m[1].replace('"', "")))
                        .collect();
                    if caps.is_empty() {
                        format!("\"{}\"", query.trim().replace('"', ""))
                    } else {
                        caps.join(" AND ")
                    }
                } else {
                    fts_query(query)
                };
                // streamed in rank order: admission decides before the pool is cut
                let mut rows: Vec<(String, String)> = vec![];
                if let Ok(mut stmt) = db.conn.prepare(
                    "SELECT chunk_id, artifact_id FROM chunks_fts WHERE chunks_fts MATCH ?1 ORDER BY bm25(chunks_fts)",
                ) {
                    if let Ok(it) = stmt.query_map([&fq], |r| {
                        Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?))
                    }) {
                        let mut admitted = 0usize;
                        for (i, row) in it.enumerate() {
                            let Ok((c, a)) = row else { break };
                            if adm.admits(&a) {
                                admitted += 1;
                            }
                            rows.push((c, a));
                            if admitted >= pool && i >= pool {
                                break;
                            }
                        }
                    }
                }
                admit_ranked(rows, &adm, pool, &mut tally)
            }
            "semantic" => {
                // the query is embedded with the implementation pinned for the live index (errors propagate: no fallback)
                let embedder = match &opts.embed_override {
                    Some(spec) => {
                        let live = crate::memory::embedder::live_spec(db);
                        if live.as_ref() != Some(spec) {
                            return Err(GovError::new(
                                "EMBEDDER_MISMATCH",
                                "benchmark index does not match the candidate spec",
                            ));
                        }
                        crate::memory::embedder::Embedder::resolve(
                            spec,
                            &crate::capabilities::governance::plugin_set(p),
                        )?
                    }
                    None => match for_query(p, db) {
                        Ok(e) => e,
                        Err(e) => {
                            if is_tool_failure(&e) {
                                let s = crate::memory::embedder::EmbedSpec::from_policy(p);
                                note_tool_failure(p, "embed", &s.id, &s.version, &e);
                            }
                            return Err(e);
                        }
                    },
                };
                embedder_used = embedder.spec().to_value();
                let qv = match embedder.embed_one(query, &p.root) {
                    Ok(v) => v,
                    Err(e) => {
                        if opts.embed_override.is_none() {
                            let s = embedder.spec();
                            note_tool_failure(p, "embed", &s.id, &s.version, &e);
                        }
                        return Err(e);
                    }
                };
                let mut scored: Vec<(f64, String, String)> = vec![];
                for r in db.query("SELECT chunk_id, artifact_id, vec, dim FROM vectors", &[])? {
                    let v: Vec<f64> =
                        serde_json::from_str(r["vec"].as_str().unwrap_or("[]")).unwrap_or_default();
                    if v.len() != qv.len() {
                        return Err(GovError::new("EMBEDDER_MISMATCH", format!("stored vector for {} has {} dimensions but the query vector has {}; the index is heterogeneous: run gov rebuild-memory", r["chunk_id"], v.len(), qv.len())));
                    }
                    let s = cosine(&qv, &v);
                    if s > 0.0 {
                        scored.push((
                            s,
                            r["chunk_id"].as_str().unwrap_or("").into(),
                            r["artifact_id"].as_str().unwrap_or("").into(),
                        ));
                    }
                }
                scored.sort_by(|a, b| {
                    b.0.partial_cmp(&a.0)
                        .unwrap_or(std::cmp::Ordering::Equal)
                        .then(a.1.cmp(&b.1))
                });
                admit_ranked(
                    scored.into_iter().map(|(_, c, a)| (c, a)),
                    &adm,
                    pool,
                    &mut tally,
                )
            }
            "graph" => {
                let (answers, context) = graph_candidates(db, query, &entities)?;
                let answers = admit_ranked(answers, &adm, pool, &mut tally);
                graph_answers = answers.iter().map(|(c, _)| c.clone()).collect();
                let mut v = answers;
                for x in admit_ranked(context, &adm, pool, &mut tally) {
                    if v.len() < pool && !v.contains(&x) {
                        v.push(x);
                    }
                }
                v
            }
            _ => vec![],
        };
        route_hits.push((route.clone(), ranked));
    }
    // --- reciprocal-rank fusion
    let mut fused: HashMap<String, (f64, String, Vec<String>)> = HashMap::new();
    for (route, ranked) in &route_hits {
        for (rank, (chunk, art)) in ranked.iter().enumerate() {
            let e = fused
                .entry(chunk.clone())
                .or_insert((0.0, art.clone(), vec![]));
            e.0 += 1.0 / (rrf_k + rank as f64 + 1.0);
            if !e.2.contains(route) {
                e.2.push(route.clone());
            }
        }
    }
    let mut ordered: Vec<(String, f64, String, Vec<String>)> = fused
        .into_iter()
        .map(|(c, (s, a, r))| (c, s, a, r))
        .collect();
    ordered.sort_by(|a, b| {
        b.1.partial_cmp(&a.1)
            .unwrap_or(std::cmp::Ordering::Equal)
            .then(a.0.cmp(&b.0))
    });
    // --- primary route precedence: its answers first, in its own order
    // (for the graph route only its direct answers form the tier; its neighbourhood context is fused normally)
    let primary_rank: HashMap<String, usize> = primary
        .as_ref()
        .and_then(|pr| route_hits.iter().find(|(r, _)| r == pr))
        .map(|(r, ranked)| {
            ranked
                .iter()
                .filter(|(c, _)| r != "graph" || graph_answers.contains(c))
                .enumerate()
                .map(|(i, (c, _))| (c.clone(), i))
                .collect()
        })
        .unwrap_or_default();
    let apply_primary = |v: &mut Vec<(String, f64, String, Vec<String>)>| {
        if primary_rank.is_empty() {
            return;
        }
        let (mut first, rest): (Vec<_>, Vec<_>) = v
            .drain(..)
            .partition(|(c, _, _, _)| primary_rank.contains_key(c));
        first.sort_by_key(|(c, _, _, _)| primary_rank[c]);
        first.extend(rest);
        *v = first;
    };
    apply_primary(&mut ordered);
    // --- reranker hook (pinned plugin): only admitted candidates ever reach it
    let plugins = crate::capabilities::governance::plugin_set(p);
    let mut reranker_used = json!({"provider": "none"});
    let mut rerank_scores: HashMap<String, f64> = HashMap::new();
    let reranker = match &opts.rerank_override {
        Some(id) => {
            let desc = match plugins.find("rerank", None, Some(id)) {
                Some(d) => d,
                None => {
                    return Err(plugins.refusal(id).unwrap_or_else(|| {
                        GovError::new(
                            "RERANKER_UNAVAILABLE",
                            format!("rerank plugin '{id}' not declared"),
                        )
                    }))
                }
            };
            Some(Reranker {
                desc,
                spec: crate::memory::embedder::RerankSpec {
                    provider: id.clone(),
                    version: "1".into(),
                    candidates: pol
                        .get_i64("MEMORY_POLICY", "retrieval.rerank_candidates", 24)
                        .max(1) as usize,
                },
            })
        }
        None => match Reranker::resolve(p, &plugins) {
            Ok(r) => r,
            Err(e) => {
                let s = crate::memory::embedder::RerankSpec::from_policy(p);
                note_tool_failure(p, "rerank", &s.provider, &s.version, &e);
                return Err(e);
            }
        },
    };
    if let Some(rr) = reranker {
        let live_rr = db
            .get_meta("reranker")
            .unwrap_or(json!({"provider": "none"}));
        if opts.rerank_override.is_none()
            && live_rr.get("provider") != Some(&json!(rr.spec.provider))
        {
            return Err(GovError::new("RERANKER_MISMATCH", format!("MEMORY_POLICY pins reranker '{}' but the live index was built with {}; run gov rebuild-memory", rr.spec.provider, live_rr)));
        }
        let n = rr.spec.candidates.min(ordered.len());
        let cands: Vec<(String, String)> = ordered
            .iter()
            .take(n)
            .filter(|(_, _, a, _)| adm.admits(a))
            .filter_map(|(c, _, _, _)| {
                db.query_one("SELECT text FROM chunks WHERE chunk_id=?1", &[c])
                    .ok()
                    .flatten()
                    .map(|r| {
                        (
                            c.clone(),
                            r["text"]
                                .as_str()
                                .unwrap_or("")
                                .chars()
                                .take(max_slice)
                                .collect::<String>(),
                        )
                    })
            })
            .collect();
        match rr.rerank(query, &cands, &p.root) {
            Ok(scores) => {
                for (id, s) in scores {
                    rerank_scores.insert(id, s);
                }
            }
            Err(e) => {
                if opts.rerank_override.is_none() {
                    note_tool_failure(p, "rerank", &rr.spec.provider, &rr.spec.version, &e);
                }
                return Err(e);
            }
        }
        reranker_used = rr.spec.to_value();
        if !rerank_scores.is_empty() {
            let (mut scored, rest): (Vec<_>, Vec<_>) = ordered
                .into_iter()
                .partition(|(c, _, _, _)| rerank_scores.contains_key(c));
            scored.sort_by(|a, b| {
                rerank_scores[&b.0]
                    .partial_cmp(&rerank_scores[&a.0])
                    .unwrap_or(std::cmp::Ordering::Equal)
                    .then(a.0.cmp(&b.0))
            });
            scored.extend(rest);
            ordered = scored;
            apply_primary(&mut ordered);
        }
    }
    // --- active-state flags, per-artefact cap, content-level de-duplication
    let mut hits: Vec<Hit> = vec![];
    let mut per_artifact: HashMap<String, usize> = HashMap::new();
    let mut art_cache: HashMap<String, Option<Value>> = HashMap::new();
    let mut seen_file_content: HashMap<String, String> = HashMap::new();
    let mut seen_slice: HashMap<String, String> = HashMap::new();
    let mut duplicates_suppressed: Vec<Value> = vec![];
    for (chunk_id, score, artifact_id, rts) in ordered {
        if hits.len() >= k {
            break;
        }
        if !adm.admits(&artifact_id) {
            continue; // defence in depth: every route already admits
        }
        let art = art_cache
            .entry(artifact_id.clone())
            .or_insert_with(|| db.artifact(&artifact_id).ok().flatten())
            .clone();
        let Some(art) = art else { continue };
        let status = art["status"].as_str().unwrap_or("").to_string();
        let record_type = art["record_type"].as_str().unwrap_or("").to_string();
        let superseded_by = art["superseded_by"].as_str().unwrap_or("").to_string();
        let mut flags = vec![];
        if !superseded_by.is_empty() {
            flags.push(format!("superseded_by:{superseded_by}"));
        }
        let n = per_artifact.get(&artifact_id).copied().unwrap_or(0);
        if n >= 2 {
            continue;
        }
        let Some(ch) = db.query_one(
            "SELECT section, level, text, parent_chunk_id FROM chunks WHERE chunk_id=?1",
            &[&chunk_id],
        )?
        else {
            continue;
        };
        let text = ch["text"].as_str().unwrap_or("");
        // a verbatim copy of an artefact already answering (same file content under another path)
        let content_hash = art["content_hash"].as_str().unwrap_or("").to_string();
        if record_type == "file" && !content_hash.is_empty() {
            if let Some(first) = seen_file_content.get(&content_hash) {
                if first != &artifact_id {
                    duplicates_suppressed.push(json!({"artifact_id": artifact_id, "chunk_id": chunk_id, "duplicate_of": first, "kind": "artifact_content"}));
                    continue;
                }
            }
        }
        // an identical slice already returned from another artefact (title/path line aside)
        let path = art["path"].as_str().unwrap_or("").to_string();
        let title = art["title"].as_str().unwrap_or("").to_string();
        let body: String = {
            let mut ls = text.lines();
            let first = ls.clone().next().unwrap_or("").trim().to_string();
            let rest: Vec<&str> = if first == path || first == title || first == artifact_id {
                ls.next();
                ls.collect()
            } else {
                ls.collect()
            };
            rest.join(" ")
                .split_whitespace()
                .collect::<Vec<_>>()
                .join(" ")
        };
        if body.chars().count() >= 40 {
            let fp = crate::util::sha256_hex(body.as_bytes());
            match seen_slice.get(&fp) {
                Some(first) if first != &artifact_id => {
                    duplicates_suppressed.push(json!({"artifact_id": artifact_id, "chunk_id": chunk_id, "duplicate_of": first, "kind": "slice_content"}));
                    continue;
                }
                _ => {
                    seen_slice.insert(fp, artifact_id.clone());
                }
            }
        }
        if record_type == "file" && !content_hash.is_empty() {
            seen_file_content
                .entry(content_hash)
                .or_insert_with(|| artifact_id.clone());
        }
        per_artifact.insert(artifact_id.clone(), n + 1);
        let excerpt: String = text.chars().take(max_slice).collect();
        hits.push(Hit {
            artifact_id: artifact_id.clone(),
            path,
            chunk_id: chunk_id.clone(),
            section: ch["section"].as_str().unwrap_or("").into(),
            level: ch["level"].as_str().unwrap_or("").into(),
            score,
            routes: rts,
            status,
            state_class: art["state_class"].as_str().unwrap_or("").into(),
            record_type,
            excerpt,
            parent_excerpt: None,
            neighbours: vec![],
            flags,
            rerank_score: rerank_scores.get(&chunk_id).copied(),
        });
    }
    for h in hits.iter_mut().take(parent_top) {
        if h.level == "child" {
            if let Some(ch) = db.query_one("SELECT c2.text FROM chunks c1 JOIN chunks c2 ON c2.chunk_id=c1.parent_chunk_id WHERE c1.chunk_id=?1", &[&h.chunk_id])? { h.parent_excerpt = Some(ch["text"].as_str().unwrap_or("").chars().take(max_slice).collect()); }
        }
        h.neighbours = graph::neighbours(db, &h.artifact_id, graph_depth)?
            .into_iter()
            .map(|r| format!("{} {}", r.via, r.node))
            .take(12)
            .collect();
    }
    let idx_hash = db
        .get_meta("index_manifest_hash")
        .and_then(|v| v.as_str().map(|s| s.to_string()))
        .unwrap_or_default();
    let latency = started.elapsed().as_millis();
    if opts.log {
        let _ = db.exec("INSERT INTO retrieval_log(ts, query, routes, hits, latency_ms) VALUES (?1,?2,?3,?4,?5)", &[&crate::util::now_iso(), &query, &routes.join(","), &serde_json::to_string(&hits.iter().map(|h| h.artifact_id.clone()).collect::<Vec<_>>())?, &(latency as f64)]);
    }
    let excluded_by_authority = tally.authority.len();
    let excluded_by_namespace = tally.namespace.len();
    // --- failure memory: an agent's query whose evidence does not cover the question (framework §18)
    let mut evidence = None;
    let mut failure_record = None;
    if opts.log
        && pol.get_bool(
            "MEMORY_POLICY",
            "failure_memory.retrieval_miss.enabled",
            true,
        )
    {
        let answered_exactly = hits.iter().any(|h| {
            h.routes
                .iter()
                .any(|r| matches!(r.as_str(), "structured" | "path" | "symbol" | "graph"))
        });
        let (cov, terms, absent) = evidence_coverage(db, query, &hits);
        evidence = Some((cov * 1000.0).round() / 1000.0);
        let threshold = pol.get_f64(
            "MEMORY_POLICY",
            "failure_memory.retrieval_miss.min_evidence_coverage",
            0.5,
        );
        let real_hits = hits.len();
        if !answered_exactly && !terms.is_empty() && (real_hits == 0 || cov < threshold) {
            let mut causes = vec![];
            if !absent.is_empty() {
                causes.push(format!(
                    "knowledge gap or vocabulary mismatch: the index holds none of [{}]",
                    absent.join(", ")
                ));
            }
            if real_hits == 0 && (excluded_by_authority + excluded_by_namespace) > 0 {
                causes.push("authority or namespace filters excluded every candidate".into());
            }
            causes.push("routing / chunking / metadata / stale index (to be established)".into());
            let ev = crate::memory::failures::retrieval_miss_event(
                query,
                &[],
                json!({"routes": routes, "primary_route": primary, "k": k, "role": p.role,
                    "hits": hits.iter().take(5).map(|h| h.artifact_id.clone()).collect::<Vec<_>>(),
                    "evidence_coverage": evidence, "min_evidence_coverage": threshold,
                    "question_terms": terms, "terms_absent_from_index": absent,
                    "excluded_by_authority": excluded_by_authority, "excluded_by_namespace": excluded_by_namespace,
                    "index_manifest_hash": idx_hash}),
                causes,
                "memory query",
                "automatic",
            );
            failure_record = Some(crate::memory::failures::record(p, ev, true).to_value());
        }
    }
    Ok(RetrievalResult {
        query: query.into(),
        strategy: if routes.len() > 1 {
            "fusion".into()
        } else {
            routes.first().cloned().unwrap_or_default()
        },
        routes,
        hits,
        index_version: crate::INDEX_VERSION.into(),
        index_manifest_hash: idx_hash,
        latency_ms: latency,
        excluded_by_authority,
        excluded_by_namespace,
        embedder: embedder_used,
        reranker: reranker_used,
        primary_route: primary,
        duplicates_suppressed,
        evidence_coverage: evidence,
        failure_record,
    })
}

/// Held-out memory regression (framework §17): Recall@K, MRR, precision@K, stale/superseded hit rates; a set smaller
/// than MEMORY_POLICY.regression.min_queries is reported as UNMEASURED (never as green).
pub fn run_heldout(p: &Project, db: &RuntimeDb, heldout: &Value) -> Result<Value> {
    run_heldout_with(p, db, heldout, None, None)
}

pub fn run_heldout_with(
    p: &Project,
    db: &RuntimeDb,
    heldout: &Value,
    embed_override: Option<crate::memory::embedder::EmbedSpec>,
    rerank_override: Option<String>,
) -> Result<Value> {
    let all: Vec<Value> = heldout
        .get("queries")
        .and_then(|q| q.as_array())
        .cloned()
        .unwrap_or_default();
    let queries: Vec<Value> = all
        .iter()
        .filter(|q| !q.get("pending").and_then(|v| v.as_bool()).unwrap_or(false))
        .cloned()
        .collect();
    let pending = all.len() - queries.len();
    let pol = p.policies();
    let min_queries = pol
        .get_i64("MEMORY_POLICY", "regression.min_queries", 5)
        .max(0) as usize;
    let mut results = vec![];
    let (
        mut recall_sum,
        mut mrr_sum,
        mut prec_sum,
        mut stale_hits,
        mut superseded_hits,
        mut total_hits,
        mut forbidden_violations,
        mut latency_sum,
    ) = (0.0, 0.0, 0.0, 0usize, 0usize, 0usize, 0usize, 0u128);
    let fresh = crate::memory::manifest::freshness(p);
    let stale_paths: HashSet<String> = fresh.stale.iter().cloned().collect();
    let mut by_category: HashMap<String, (usize, f64)> = HashMap::new();
    for q in &queries {
        let text = q["query"].as_str().unwrap_or("");
        let k = q.get("k").and_then(|v| v.as_u64()).unwrap_or(8) as usize;
        let expected: Vec<String> = q
            .get("expected_refs")
            .and_then(|v| v.as_array())
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default();
        let forbidden: Vec<String> = q
            .get("forbidden")
            .and_then(|v| v.as_array())
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default();
        let route = q
            .get("route")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());
        let res = retrieve(
            p,
            db,
            text,
            RetrieveOptions {
                k,
                route,
                embed_override: embed_override.clone(),
                rerank_override: rerank_override.clone(),
                ..Default::default()
            },
        )?;
        let got: Vec<String> = res.hits.iter().map(|h| h.artifact_id.clone()).collect();
        let found = expected
            .iter()
            .filter(|e| got.contains(e) || res.hits.iter().any(|h| h.path == **e))
            .count();
        let recall = if expected.is_empty() {
            1.0
        } else {
            found as f64 / expected.len() as f64
        };
        let precision = if got.is_empty() {
            0.0
        } else {
            got.iter().filter(|g| expected.contains(g)).count() as f64 / got.len() as f64
        };
        let rr = expected
            .iter()
            .filter_map(|e| {
                got.iter()
                    .position(|g| g == e)
                    .map(|i| 1.0 / (i as f64 + 1.0))
            })
            .fold(0.0f64, f64::max);
        let viol: Vec<String> = forbidden
            .iter()
            .filter(|f| got.contains(f))
            .cloned()
            .collect();
        forbidden_violations += viol.len();
        for h in &res.hits {
            total_hits += 1;
            if stale_paths.contains(&h.path) {
                stale_hits += 1;
            }
            if h.flags.iter().any(|f| f.starts_with("superseded_by")) || h.status == "SUPERSEDED" {
                superseded_hits += 1;
            }
        }
        recall_sum += recall;
        mrr_sum += rr;
        prec_sum += precision;
        latency_sum += res.latency_ms;
        let cat = q
            .get("category")
            .and_then(|v| v.as_str())
            .unwrap_or("uncategorised")
            .to_string();
        let e = by_category.entry(cat).or_insert((0, 0.0));
        e.0 += 1;
        e.1 += recall;
        results.push(json!({"id": q["id"], "query": text, "category": q.get("category"), "routes": res.routes, "expected": expected, "got": got, "recall": recall, "precision": precision, "rr": rr, "forbidden_hits": viol, "latency_ms": res.latency_ms, "pass": recall >= 1.0 - 1e-9 && viol.is_empty()}));
    }
    let n = queries.len().max(1) as f64;
    let min_recall = pol.get_f64("MEMORY_POLICY", "regression.min_recall_at_k", 0.8);
    let min_mrr = pol.get_f64("MEMORY_POLICY", "regression.min_mrr", 0.5);
    let max_stale = pol.get_f64("MEMORY_POLICY", "regression.max_stale_hit_rate", 0.0);
    let max_sup = pol.get_f64("MEMORY_POLICY", "regression.max_superseded_hit_rate", 0.0);
    let (recall, mrr, precision) = (recall_sum / n, mrr_sum / n, prec_sum / n);
    let stale_rate = if total_hits == 0 {
        0.0
    } else {
        stale_hits as f64 / total_hits as f64
    };
    let sup_rate = if total_hits == 0 {
        0.0
    } else {
        superseded_hits as f64 / total_hits as f64
    };
    let measured = queries.len() >= min_queries && !queries.is_empty();
    let thresholds_met = recall >= min_recall
        && mrr >= min_mrr
        && stale_rate <= max_stale
        && sup_rate <= max_sup
        && forbidden_violations == 0;
    let pass = measured && thresholds_met;
    let status = if !measured {
        "UNMEASURED"
    } else if pass {
        "PASS"
    } else {
        "FAIL"
    };
    Ok(
        json!({"queries": queries.len(), "pending_queries": pending, "min_queries": min_queries, "measured": measured, "status": status, "recall_at_k": recall, "mrr": mrr, "precision_at_k": precision, "stale_hit_rate": stale_rate, "superseded_hit_rate": sup_rate, "forbidden_violations": forbidden_violations, "avg_latency_ms": if queries.is_empty() { 0.0 } else { latency_sum as f64 / n },
              "by_category": by_category.iter().map(|(c, (n, r))| json!({"category": c, "queries": n, "recall": r / *n as f64})).collect::<Vec<_>>(),
              "thresholds": {"min_recall_at_k": min_recall, "min_mrr": min_mrr, "max_stale_hit_rate": max_stale, "max_superseded_hit_rate": max_sup, "min_queries": min_queries}, "thresholds_met": thresholds_met, "pass": pass, "results": results, "index_fresh": fresh.fresh}),
    )
}

pub fn edge_types() -> std::collections::BTreeMap<String, usize> {
    graph::EDGE_TYPES
        .iter()
        .enumerate()
        .map(|(i, t)| (t.to_string(), i))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bare_file_names_reach_the_path_route() {
        for q in ["runbook.md", "ledger.rs", "format.test.ts", "settings.yaml"] {
            let r = classify(q);
            assert!(
                r.contains(&"path".to_string()) && r.contains(&"lexical".to_string()),
                "{q}: {r:?}"
            );
            assert_eq!(filenames(q), vec![q.to_string()]);
        }
        assert!(!classify("Order.total_cents").contains(&"path".to_string()));
        assert!(filenames("SettlementPipeline.reconcile_quarantine").is_empty());
        assert_eq!(
            filenames("where is ledger.rs used"),
            vec!["ledger.rs".to_string()]
        );
        assert!(classify("src/core/ledger.rs").contains(&"path".to_string()));
        assert_eq!(
            classify("ERR_LEDGER_DRIFT_4711"),
            vec!["symbol".to_string(), "lexical".to_string()]
        );
    }
}
