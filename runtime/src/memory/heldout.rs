//! Held-out retrieval regression sets (framework §17). A starter set is generated from the live index so that recall
//! is measured from day one; paraphrase placeholders stay `pending` until a human/agent fills them (never counted).
use crate::memory::db::RuntimeDb;
use crate::{Project, Result};
use serde_json::{json, Value};

pub fn generate_starter(p: &Project, db: &RuntimeDb, generated_by: &str) -> Result<Value> {
    let mut queries: Vec<Value> = vec![];
    let mut push = |cat: &str, query: String, expected: Vec<String>, forbidden: Vec<String>, route: Option<&str>| {
        if query.trim().is_empty() || expected.is_empty() { return; }
        let mut q = json!({"id": format!("HQ-{:03}", queries.len() + 1), "category": cat, "query": query, "expected_refs": expected, "forbidden": forbidden, "k": 8});
        if let Some(r) = route { q["route"] = json!(r); }
        queries.push(q);
    };
    // exact ids of governed records (non-file artefacts, not superseded)
    for r in db.query("SELECT artifact_id FROM artifacts WHERE record_type != 'file' AND (superseded_by IS NULL OR superseded_by='') AND status IN ('ACTIVE','PROVISIONAL') AND default_retrieval=1 ORDER BY artifact_id LIMIT 8", &[])? { let id = r["artifact_id"].as_str().unwrap_or("").to_string(); push("exact_id", id.clone(), vec![id], vec![], Some("structured")); }
    // exact paths of source/test files
    for r in db.query("SELECT artifact_id, path FROM artifacts WHERE record_type='file' AND path_class IN ('source','test','authoritative','evidence') ORDER BY path LIMIT 6", &[])? { push("exact_path", r["path"].as_str().unwrap_or("").to_string(), vec![r["artifact_id"].as_str().unwrap_or("").to_string()], vec![], Some("path")); }
    // symbols (functions/classes) → bare identifier queries
    for r in db.query("SELECT DISTINCT name, artifact_id FROM symbols WHERE kind IN ('function','class','struct','method','enum','trait') AND length(name) >= 4 ORDER BY name LIMIT 8", &[])? { push("symbol", r["name"].as_str().unwrap_or("").to_string(), vec![r["artifact_id"].as_str().unwrap_or("").to_string()], vec![], Some("symbol")); }
    // lexical literals: a distinctive line from record sections
    let mut lex = 0;
    for r in db.query("SELECT c.artifact_id, c.text FROM chunks c JOIN artifacts a ON a.artifact_id=c.artifact_id WHERE a.record_type != 'file' AND c.level='section' AND a.default_retrieval=1 ORDER BY c.chunk_id LIMIT 40", &[])? {
        if lex >= 4 { break; }
        let text = r["text"].as_str().unwrap_or("");
        if let Some(line) = text.lines().skip(1).find(|l| l.split_whitespace().filter(|w| w.len() >= 4).count() >= 5 && l.len() < 140 && !l.contains('"')) { push("lexical_literal", format!("\"{}\"", line.trim()), vec![r["artifact_id"].as_str().unwrap_or("").to_string()], vec![], Some("lexical_exact")); lex += 1; }
    }
    // lexical literals from source files when records are scarce
    for r in db.query("SELECT c.artifact_id, c.text FROM chunks c JOIN artifacts a ON a.artifact_id=c.artifact_id WHERE a.record_type = 'file' AND c.level='section' AND a.default_retrieval=1 ORDER BY c.chunk_id LIMIT 60", &[])? {
        if lex >= 6 { break; }
        let text = r["text"].as_str().unwrap_or("");
        if let Some(line) = text.lines().skip(1).find(|l| l.split_whitespace().filter(|w| w.len() >= 4 && w.chars().all(|c| c.is_alphanumeric() || c == '_')).count() >= 4 && l.len() < 100 && !l.contains('"') && !l.contains('\'')) { push("lexical_literal", format!("\"{}\"", line.trim()), vec![r["artifact_id"].as_str().unwrap_or("").to_string()], vec![], Some("lexical_exact")); lex += 1; }
    }
    // graph: records that something depends on / implements
    for r in db.query("SELECT DISTINCT e.dst FROM edges e JOIN artifacts a ON a.artifact_id=e.dst WHERE a.record_type != 'file' ORDER BY e.dst LIMIT 2", &[])? { let id = r["dst"].as_str().unwrap_or("").to_string(); push("graph_impact", format!("what depends on {id}"), vec![id], vec![], Some("graph")); }
    // superseded-vs-current pairs
    for r in db.query("SELECT a.artifact_id AS old, a.superseded_by AS new, b.title FROM artifacts a JOIN artifacts b ON b.artifact_id=a.superseded_by WHERE a.superseded_by IS NOT NULL AND a.superseded_by != '' LIMIT 2", &[])? { push("superseded_vs_current", r["title"].as_str().unwrap_or("").to_string(), vec![r["new"].as_str().unwrap_or("").to_string()], vec![r["old"].as_str().unwrap_or("").to_string()], None); }
    // paraphrase placeholders: pending until authored (not counted by run_heldout)
    let n = queries.len();
    queries.push(json!({"id": format!("HQ-{:03}", n + 1), "category": "semantic_paraphrase", "query": "TODO: paraphrase a decision rationale without reusing its words", "expected_refs": ["TODO"], "forbidden": [], "k": 8, "pending": true, "note": "author this query, then remove `pending`"}));
    queries.push(json!({"id": format!("HQ-{:03}", n + 2), "category": "semantic_paraphrase", "query": "TODO: describe a scenario outcome in different terms", "expected_refs": ["TODO"], "forbidden": [], "k": 8, "pending": true, "note": "author this query, then remove `pending`"}));
    Ok(json!({"version": "2", "generated_by": generated_by, "generated_at": crate::util::now_iso(), "note": "starter set: exact id/path/symbol/literal/graph/supersession queries generated from the index; paraphrase placeholders are pending", "queries": queries, "project": p.project_alias()}))
}
