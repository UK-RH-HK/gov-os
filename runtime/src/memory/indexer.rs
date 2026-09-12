//! Incremental index pipeline: repository files -> artifacts/chunks/FTS/vectors/edges/symbols -> manifests.
//! Secret-class paths are never read; secret-content hits block indexing of that file (fail closed, INV-009).
use crate::capabilities::ecosystems;
use crate::capabilities::host::{discover, find, invoke};
use crate::capabilities::protocol::PluginDescriptor;
use crate::code_intelligence;
use crate::memory::chunking::{chunk_code, chunk_plain, chunk_record, Chunk};
use crate::memory::db::RuntimeDb;
use crate::memory::embeddings::HashedNgramEmbedder;
use crate::memory::manifest::{build_index_manifest, read_index_manifest, write_manifests};
use crate::paths::iter_repo_files;
use crate::records::{parse_record_text, state_class_for};
use crate::util::{is_text_file, now_iso, read_text, sha256_hex};
use crate::{Project, Result, INDEX_VERSION};
use rusqlite::params;
use serde_json::{json, Value};
use std::collections::{BTreeMap, HashSet};
use std::path::Path;
use std::time::Duration;

#[derive(Debug, Clone, Default)]
pub struct IndexOptions { pub incremental: bool }

#[derive(Debug, Clone, serde::Serialize, Default)]
pub struct IndexReport {
    pub counts: Value, pub indexed: usize, pub unchanged: usize, pub removed: usize, pub excluded: Vec<Value>,
    pub secret_blocked: Vec<Value>, pub degradations: Vec<String>, pub problems: Vec<String>, pub manifest_hash: String,
    pub embedder: Value, pub duration_ms: u128, pub ecosystems: Value, pub supersession_conflicts: Vec<Value>,
}

enum Embed { Builtin(HashedNgramEmbedder), Plugin(PluginDescriptor, usize) }

impl Embed {
    fn describe(&self) -> Value {
        match self {
            Embed::Builtin(e) => json!({"id": e.id(), "version": e.version, "dimensions": e.dim, "source": "builtin"}),
            Embed::Plugin(p, dim) => json!({"id": p.plugin_id, "version": p.version, "dimensions": dim, "source": "plugin"}),
        }
    }
    fn embed_batch(&self, texts: &[String], root: &Path) -> std::result::Result<Vec<Vec<f64>>, String> {
        match self {
            Embed::Builtin(e) => Ok(texts.iter().map(|t| e.embed(t)).collect()),
            Embed::Plugin(p, dim) => {
                let out = invoke(p, root, json!({"texts": texts, "dimensions": dim}), Duration::from_secs(120)).map_err(|e| e.to_string())?;
                let vecs = out.outputs.get("vectors").and_then(|v| v.as_array()).ok_or("no vectors")?;
                Ok(vecs.iter().map(|v| v.as_array().map(|a| a.iter().filter_map(|x| x.as_f64()).collect()).unwrap_or_default()).collect())
            }
        }
    }
}

fn select_embedder(p: &Project, plugins: &[PluginDescriptor], degradations: &mut Vec<String>) -> Embed {
    let pol = p.policies();
    let provider = pol.get_str("MEMORY_POLICY", "embedding.provider", "hashed-ngram");
    let version = pol.get_str("MEMORY_POLICY", "embedding.version", "1");
    let dim = pol.get_i64("MEMORY_POLICY", "embedding.dimensions", 512).max(8) as usize;
    if provider == "hashed-ngram" { return Embed::Builtin(HashedNgramEmbedder::new(dim, &version)); }
    if let Some(desc) = find(plugins, "embed", None, Some(&provider)) { return Embed::Plugin(desc, dim); }
    degradations.push(format!("embedding provider '{provider}' not available as plugin; degraded to builtin hashed-ngram"));
    Embed::Builtin(HashedNgramEmbedder::new(dim, &version))
}

fn resolve_import(root: &Path, from_rel: &str, language: &str, name: &str, product_roots: &[String]) -> Option<String> {
    let exists = |rel: &str| root.join(rel).is_file();
    let dir = Path::new(from_rel).parent().map(|p| p.to_string_lossy().to_string()).unwrap_or_default();
    match language {
        "python" => {
            let rel_mod = name.trim_start_matches('.').replace('.', "/");
            let mut bases = vec![String::new(), dir.clone() + "/"];
            for pr in product_roots { bases.push(pr.clone()); }
            // also try each ancestor of the importing file as a package root
            let mut anc = Path::new(from_rel).parent();
            while let Some(a) = anc { bases.push(format!("{}/", a.to_string_lossy())); anc = a.parent(); }
            for b in bases {
                let b = b.trim_start_matches('/').to_string();
                for cand in [format!("{b}{rel_mod}.py"), format!("{b}{rel_mod}/__init__.py")] {
                    let c = cand.trim_start_matches('/').replace("//", "/");
                    if exists(&c) { return Some(c); }
                }
            }
            None
        }
        "javascript" | "typescript" => {
            if !name.starts_with('.') { return None; }
            let base = Path::new(&dir).join(name);
            let base_s = base.to_string_lossy().replace('\\', "/");
            let norm = normalize(&base_s);
            for ext in ["", ".ts", ".tsx", ".js", ".jsx", ".mjs", "/index.ts", "/index.js"] {
                let c = format!("{norm}{ext}");
                if exists(&c) { return Some(c); }
            }
            None
        }
        "rust" => {
            let path = name.trim_start_matches("crate::").replace("::", "/");
            let first = path.split('/').next().unwrap_or("");
            for base in [dir.clone(), "src".to_string(), format!("{dir}/..")] {
                for cand in [format!("{base}/{first}.rs"), format!("{base}/{first}/mod.rs"), format!("{base}/{path}.rs")] {
                    let c = normalize(&cand);
                    if exists(&c) { return Some(c); }
                }
            }
            None
        }
        "go" | "c" | "cpp" => {
            for cand in [format!("{dir}/{name}"), name.to_string()] { let c = normalize(&cand); if exists(&c) { return Some(c); } }
            None
        }
        _ => None,
    }
}

fn normalize(p: &str) -> String {
    let mut out: Vec<&str> = vec![];
    for seg in p.split('/') {
        match seg { "" | "." => {}, ".." => { out.pop(); }, s => out.push(s) }
    }
    out.join("/")
}

pub fn rebuild(p: &Project, opts: IndexOptions) -> Result<IndexReport> {
    let started = std::time::Instant::now();
    p.require_installed()?;
    std::fs::create_dir_all(p.runtime_dir())?;
    let db_path = p.db_path();
    if !opts.incremental {
        for suffix in ["", "-wal", "-shm"] { let f = p.runtime_dir().join(format!("state.db{suffix}")); if f.exists() { std::fs::remove_file(&f)?; } }
    }
    let db = RuntimeDb::open(&db_path)?;
    db.init_schema()?;
    let prev = if opts.incremental { read_index_manifest(p) } else { None };
    let prev_arts: BTreeMap<String, Value> = prev.as_ref().and_then(|m| m.get("artifacts")).and_then(|a| a.as_object()).map(|o| o.iter().map(|(k, v)| (k.clone(), v.clone())).collect()).unwrap_or_default();

    let pol = p.policies();
    let max_chars = pol.get_i64("MEMORY_POLICY", "chunking.max_chars", 1200).max(200) as usize;
    let overlap = pol.get_i64("MEMORY_POLICY", "chunking.overlap_chars", 120) as usize;
    let chunking = json!({"max_chars": max_chars, "overlap_chars": overlap, "levels": ["document", "section", "child"]});
    let authority = pol.effective.get("AUTHORITY_POLICY").cloned().unwrap_or(json!({}));
    let contract = p.contract();
    let scanner = p.secret_scanner();
    let plugins = discover(&p.root);
    let mut report = IndexReport::default();
    let mut embed = select_embedder(p, &plugins, &mut report.degradations);
    let product_roots: Vec<String> = contract.roots.iter().filter(|(k, _)| k == "product").map(|(_, v)| v.clone()).collect();
    let repo_commit = p.git_commit();
    let now = now_iso();

    let files = iter_repo_files(&p.root, false);
    let mut seen_paths: HashSet<String> = HashSet::new();
    let mut seen_ids: HashSet<String> = HashSet::new();
    let mut supersedes_map: Vec<(String, String)> = vec![]; // (superseder, superseded)
    let mut pending_vectors: Vec<(String, String, String)> = vec![]; // (chunk_id, artifact_id, text)
    let mut test_files: Vec<(String, String, Vec<String>)> = vec![]; // (artifact_id, language, resolved imports)
    let mut in_batch = 0usize;
    db.begin()?;
    for (abs, rel) in &files {
        let d = contract.decide(rel);
        if d.is_secret() || scanner.path_is_secret(rel) {
            report.excluded.push(json!({"path": rel, "reason": "secret_class"}));
            db.exec("INSERT OR REPLACE INTO excluded(path, reason, detail) VALUES (?1,?2,?3)", &[rel, &"secret_class", &d.rule_pattern.clone().unwrap_or_default()])?;
            continue;
        }
        let (lex, sem, gr, code) = (d.flag("lexical_index"), d.flag("semantic_index"), d.flag("graph_index"), d.flag("code_index"));
        if !(lex || sem || gr || code) { continue; }
        if !is_text_file(abs) { report.excluded.push(json!({"path": rel, "reason": "binary"})); continue; }
        let size = abs.metadata().map(|m| m.len()).unwrap_or(0);
        if size > 2_000_000 { report.excluded.push(json!({"path": rel, "reason": "too_large"})); continue; }
        let text = match read_text(abs) { Ok(t) => t, Err(_) => continue };
        let hits = scanner.scan_text(&text, rel);
        if !hits.is_empty() {
            let ids: Vec<String> = hits.iter().map(|h| h.pattern_id.clone()).collect::<HashSet<_>>().into_iter().collect();
            report.excluded.push(json!({"path": rel, "reason": "secret_content", "patterns": ids}));
            report.secret_blocked.push(json!({"path": rel, "patterns": ids, "lines": hits.iter().map(|h| h.line).collect::<Vec<_>>()}));
            db.exec("INSERT OR REPLACE INTO excluded(path, reason, detail) VALUES (?1,?2,?3)", &[rel, &"secret_content", &ids.join(",")])?;
            if let Some(a) = db.artifact_by_path(rel)? { db.delete_artifact(a["artifact_id"].as_str().unwrap_or(""))?; }
            continue;
        }
        let hash = sha256_hex(text.as_bytes());
        seen_paths.insert(rel.clone());
        if opts.incremental {
            if let Some(prev_e) = prev_arts.get(rel) {
                if prev_e.get("content_hash").and_then(|v| v.as_str()) == Some(hash.as_str()) {
                    report.unchanged += 1;
                    if let Some(id) = prev_e.get("artifact_id").and_then(|v| v.as_str()) { seen_ids.insert(id.to_string()); }
                    continue;
                }
            }
            if let Some(a) = db.artifact_by_path(rel)? { db.delete_artifact(a["artifact_id"].as_str().unwrap_or(""))?; }
        }
        // --- classify: record or file ---
        let record = if rel.ends_with(".yaml") || rel.ends_with(".yml") || rel.ends_with(".md") { parse_record_text(&text, rel) } else { None };
        let ext = Path::new(rel).extension().map(|e| e.to_string_lossy().to_lowercase()).unwrap_or_default();
        let language = ecosystems::language_for_ext(&ext);
        let (artifact_id, record_type, title, status, state_class, data_json, chunks, superseded_by): (String, String, String, String, String, String, Vec<Chunk>, Option<String>);
        let mut edges: Vec<(String, String, String)> = vec![]; // (src, type, dst)
        let mut symbols: Vec<code_intelligence::Symbol> = vec![];
        let mut sym_refs: Vec<(String, String, String)> = vec![]; // (name, kind, target)
        let mut provider = String::new();
        match record {
            Some(r) if !r.id().is_empty() && !r.rtype().is_empty() => {
                let id = r.id();
                if seen_ids.contains(&id) || (opts.incremental && db.artifact(&id)?.map(|a| a["path"].as_str() != Some(rel.as_str())).unwrap_or(false)) {
                    report.problems.push(format!("duplicate record id {id} at {rel} (first occurrence kept)"));
                    continue;
                }
                seen_ids.insert(id.clone());
                artifact_id = id.clone();
                record_type = r.rtype();
                title = r.title();
                status = if d.class() == "historical" && r.status() == "ACTIVE" { "HISTORICAL".into() } else { r.status() };
                state_class = if d.class() == "historical" { "HISTORICAL".into() } else { state_class_for(&r, &authority) };
                data_json = serde_json::to_string(&r.data)?;
                let fields = r.text_fields();
                let body = if r.body.is_empty() { r.get("body") } else { r.body.clone() };
                chunks = chunk_record(&title, &fields, &body, max_chars, overlap);
                for (t, target) in r.relations() {
                    edges.push((id.clone(), t.clone(), target.clone()));
                    if t == "SUPERSEDES" { supersedes_map.push((id.clone(), target)); }
                }
                let sb = r.get("superseded_by");
                superseded_by = if sb.is_empty() { None } else { Some(sb) };
            }
            _ => {
                artifact_id = format!("file:{rel}");
                record_type = "file".into();
                title = rel.clone();
                status = if d.class() == "historical" { "HISTORICAL".into() } else { "ACTIVE".into() };
                state_class = match d.class().as_str() { "source" | "test" | "devops" | "tooling" => "EVIDENCE", "historical" => "HISTORICAL", "generated" | "derived" => "DERIVED", "authoritative" => "AUTHORITATIVE", _ => "NARRATIVE" }.into();
                data_json = "{}".into();
                superseded_by = None;
                if code && language.is_some() {
                    let lang = language.unwrap();
                    let facts = code_intelligence::analyze(rel, lang, &text, &plugins, &p.root);
                    provider = facts.provider.clone();
                    if let Some(dg) = &facts.degraded { report.degradations.push(format!("{rel}: {dg}")); }
                    chunks = chunk_code(rel, &text, &facts.units, max_chars, overlap);
                    symbols = facts.symbols.clone();
                    let mut resolved = vec![];
                    for imp in &facts.imports {
                        match resolve_import(&p.root, rel, lang, imp, &product_roots) {
                            Some(target) => {
                                let td = contract.decide(&target);
                                if td.is_secret() || scanner.path_is_secret(&target) {
                                    // relationship to a secret-class file is recorded without ever indexing the target (INV-009)
                                    edges.push((artifact_id.clone(), "IMPORTS".into(), format!("excluded:{target}"))); sym_refs.push((imp.clone(), "import".into(), format!("excluded:{target}")));
                                } else {
                                    edges.push((artifact_id.clone(), "IMPORTS".into(), format!("file:{target}"))); sym_refs.push((imp.clone(), "import".into(), format!("file:{target}"))); resolved.push(format!("file:{target}"));
                                }
                            }
                            None => { sym_refs.push((imp.clone(), "import".into(), format!("module:{imp}"))); }
                        }
                    }
                    for (from, name) in &facts.calls { sym_refs.push((name.clone(), "call".into(), from.clone())); }
                    if d.class() == "test" { test_files.push((artifact_id.clone(), lang.to_string(), resolved)); }
                } else if ext == "md" || ext == "txt" || ext == "rst" {
                    chunks = crate::memory::chunking::chunk_markdown(rel, &text, max_chars, overlap);
                } else {
                    chunks = chunk_plain(rel, &text, max_chars, overlap);
                }
            }
        }
        db.exec("INSERT OR REPLACE INTO artifacts(artifact_id, path, record_type, title, status, state_class, namespace, sensitivity, path_class, content_hash, repo_commit, index_version, size, indexed_at, data_json, semantic, lexical, graph, code, default_retrieval, superseded_by) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,?16,?17,?18,?19,?20,?21)",
            &[&artifact_id, rel, &record_type, &title, &status, &state_class, &d.namespace(), &d.str("sensitivity"), &d.class(), &hash, &repo_commit, &INDEX_VERSION, &(size as i64), &now, &data_json, &(sem as i64), &(lex as i64), &(gr as i64), &(code as i64), &(d.default_retrieval() as i64), &superseded_by])?;
        for c in &chunks {
            let chunk_id = format!("{artifact_id}#{}", c.ordinal);
            let parent = c.parent_ordinal.map(|po| format!("{artifact_id}#{po}"));
            let chash = sha256_hex(c.text.as_bytes());
            db.exec("INSERT OR REPLACE INTO chunks(chunk_id, artifact_id, parent_chunk_id, level, section, ordinal, content_hash, text, chars, lexical, semantic) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11)",
                &[&chunk_id, &artifact_id, &parent, &c.level, &c.section, &(c.ordinal as i64), &chash, &c.text, &(c.text.chars().count() as i64), &(lex as i64), &(sem as i64)])?;
            if lex { db.exec("INSERT INTO chunks_fts(text, chunk_id, artifact_id) VALUES (?1,?2,?3)", &[&c.text, &chunk_id, &artifact_id])?; }
            if sem { pending_vectors.push((chunk_id, artifact_id.clone(), c.text.clone())); }
        }
        if gr {
            for (s, t, dst) in &edges { db.exec("INSERT OR IGNORE INTO edges(src, type, dst, source_artifact, provenance) VALUES (?1,?2,?3,?4,?5)", &[s, t, dst, &artifact_id, rel])?; }
        }
        for s in &symbols {
            let sid = format!("{rel}::{}", s.qualname);
            db.exec("INSERT OR REPLACE INTO symbols(symbol_id, artifact_id, path, name, qualname, kind, lineno, end_lineno, parent, signature, language, provider) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12)",
                &[&sid, &artifact_id, rel, &s.name, &s.qualname, &s.kind, &(s.lineno as i64), &(s.end_lineno as i64), &s.parent, &s.signature, &language.unwrap_or(""), &provider])?;
        }
        for (name, kind, target) in &sym_refs { db.exec("INSERT INTO symbol_refs(path, name, kind, lineno, target) VALUES (?1,?2,?3,0,?4)", &[rel, name, kind, target])?; }
        report.indexed += 1;
        in_batch += 1;
        if in_batch >= 500 { db.commit()?; db.begin()?; in_batch = 0; }
    }
    // TESTS edges: test files → imported product files
    for (aid, _lang, resolved) in &test_files {
        for target in resolved { db.exec("INSERT OR IGNORE INTO edges(src, type, dst, source_artifact, provenance) VALUES (?1,'TESTS',?2,?1,'code-intel')", &[aid, target])?; }
    }
    // supersession: mark superseded artifacts and detect conflicts (superseded record still ACTIVE)
    for (superseder, superseded) in &supersedes_map {
        db.exec("UPDATE artifacts SET superseded_by=?1 WHERE artifact_id=?2 AND (superseded_by IS NULL OR superseded_by='')", &[superseder, superseded])?;
        if let Some(a) = db.artifact(superseded)? {
            if a["status"].as_str() == Some("ACTIVE") { report.supersession_conflicts.push(json!({"superseded": superseded, "by": superseder, "status": "ACTIVE", "path": a["path"]})); }
        }
    }
    // removed artifacts (incremental)
    if opts.incremental {
        for a in db.query("SELECT artifact_id, path FROM artifacts", &[])? {
            let path = a["path"].as_str().unwrap_or("").to_string();
            if !seen_paths.contains(&path) && !p.root.join(&path).exists() { db.delete_artifact(a["artifact_id"].as_str().unwrap_or(""))?; report.removed += 1; }
        }
        db.exec("DELETE FROM excluded WHERE path NOT IN (SELECT path FROM excluded WHERE 1=0) AND 0", &[])?;
    }
    db.commit()?;
    // vectors in batches
    let dim = embed.describe()["dimensions"].as_i64().unwrap_or(512);
    db.begin()?;
    for batch in pending_vectors.chunks(256) {
        let texts: Vec<String> = batch.iter().map(|(_, _, t)| t.clone()).collect();
        let vecs = match embed.embed_batch(&texts, &p.root) {
            Ok(v) => v,
            Err(e) => {
                report.degradations.push(format!("embedding plugin failed ({e}); degraded to builtin hashed-ngram for this build"));
                embed = Embed::Builtin(HashedNgramEmbedder::new(dim.max(8) as usize, "1"));
                embed.embed_batch(&texts, &p.root).unwrap_or_default()
            }
        };
        let emb_id = embed.describe()["id"].as_str().unwrap_or("").to_string();
        for ((chunk_id, artifact_id, _), v) in batch.iter().zip(vecs) {
            let vs = serde_json::to_string(&v)?;
            db.conn.execute("INSERT OR REPLACE INTO vectors(chunk_id, artifact_id, embedder, dim, vec) VALUES (?1,?2,?3,?4,?5)", params![chunk_id, artifact_id, emb_id, v.len() as i64, vs])?;
        }
    }
    db.commit()?;
    let emb_desc = embed.describe();
    // capability memory: ecosystems + plugins
    let eco = ecosystems::detect(&p.root, &product_roots);
    db.set_meta("capability.ecosystems", &eco)?;
    db.set_meta("capability.plugins", &serde_json::to_value(&plugins)?)?;
    db.set_meta("capability.degradations", &json!(report.degradations))?;
    db.set_meta("index_version", &json!(INDEX_VERSION))?;
    db.set_meta("built_at", &json!(now))?;
    db.set_meta("supersession_conflicts", &json!(report.supersession_conflicts))?;
    // manifests
    let excluded_all = db.query("SELECT path, reason FROM excluded ORDER BY path", &[])?;
    let manifest = build_index_manifest(p, &db, &emb_desc, &chunking, &excluded_all)?;
    write_manifests(p, &db, &manifest)?;
    report.manifest_hash = manifest["manifest_hash"].as_str().unwrap_or("").to_string();
    report.embedder = emb_desc;
    report.counts = db.counts();
    report.ecosystems = eco;
    report.duration_ms = started.elapsed().as_millis();
    Ok(report)
}
