//! Incremental index pipeline: repository files -> artifacts/chunks/FTS/vectors/edges/symbols -> manifests.
//! Never read: secret-class paths and any sensitivity class in SECURITY_POLICY.never_index_classes (fail closed).
//! The embedding implementation is the one pinned by policy; it is recorded in runtime meta and the manifest and a
//! pin change escalates an incremental build to a full rebuild (no mixed-embedder index, no silent fallback).
use crate::capabilities::ecosystems;
use crate::capabilities::governance::plugin_set;
use crate::capabilities::protocol::PluginDescriptor;
use crate::code_intelligence;
use crate::memory::chunking::{chunk_code, chunk_plain, chunk_record, Chunk};
use crate::memory::db::RuntimeDb;
use crate::memory::embedder::{EmbedSpec, Embedder, RerankSpec, Reranker};
use crate::memory::manifest::{build_index_manifest, read_index_manifest, write_manifests};
use crate::paths::iter_repo_files;
use crate::records::{parse_record_text, state_class_for};
use crate::util::{is_text_file, now_iso, read_text, sha256_hex};
use crate::{GovError, Project, Result, INDEX_VERSION};
use rusqlite::params;
use serde_json::{json, Value};
use std::collections::{BTreeMap, HashSet};
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Default)]
pub struct IndexOptions {
    pub incremental: bool,
    /// Build into this database instead of the project runtime (benchmarks); manifests are not written.
    pub db_path: Option<PathBuf>,
    /// Override the policy-pinned embedder (benchmarks only).
    pub embed_override: Option<EmbedSpec>,
}

#[derive(Debug, Clone, serde::Serialize, Default)]
pub struct IndexReport {
    pub counts: Value,
    pub indexed: usize,
    pub unchanged: usize,
    pub removed: usize,
    pub moved: Vec<Value>,
    pub excluded: Vec<Value>,
    pub secret_blocked: Vec<Value>,
    pub degradations: Vec<String>,
    pub problems: Vec<String>,
    pub manifest_hash: String,
    pub embedder: Value,
    pub reranker: Value,
    pub duration_ms: u128,
    pub ecosystems: Value,
    pub supersession_conflicts: Vec<Value>,
    pub mode: String,
    pub escalated_to_full: Option<String>,
}

pub fn lexical_config(p: &Project) -> Value {
    json!({"engine": "sqlite-fts5", "tokenizer": p.policies().get_str("MEMORY_POLICY", "lexical.tokenizer", "unicode61")})
}
pub fn chunking_config(p: &Project) -> Value {
    let pol = p.policies();
    json!({"max_chars": pol.get_i64("MEMORY_POLICY", "chunking.max_chars", 1200).max(200), "overlap_chars": pol.get_i64("MEMORY_POLICY", "chunking.overlap_chars", 120), "levels": ["document", "section", "child"]})
}

/// The pins the live index must satisfy: embedder, reranker, chunking, lexical engine, index format version.
pub fn expected_pins(p: &Project) -> Value {
    json!({"embedder": EmbedSpec::from_policy(p).to_value(), "reranker": RerankSpec::from_policy(p).to_value(), "chunking": chunking_config(p), "lexical": lexical_config(p), "index_version": INDEX_VERSION})
}
pub fn live_pins(db: &RuntimeDb) -> Value {
    json!({"embedder": db.get_meta("embedder").unwrap_or(Value::Null), "reranker": db.get_meta("reranker").unwrap_or(Value::Null), "chunking": db.get_meta("chunking").unwrap_or(Value::Null), "lexical": db.get_meta("lexical").unwrap_or(Value::Null), "index_version": db.get_meta("index_version").unwrap_or(Value::Null)})
}
/// Human-readable list of pin differences (empty = compatible).
pub fn pin_differences(expected: &Value, live: &Value) -> Vec<String> {
    let mut out = vec![];
    for k in ["embedder", "chunking", "lexical", "index_version"] {
        if expected.get(k) != live.get(k) {
            out.push(format!(
                "{k}: expected {} but live index has {}",
                expected
                    .get(k)
                    .map(|v| v.to_string())
                    .unwrap_or("null".into()),
                live.get(k).map(|v| v.to_string()).unwrap_or("null".into())
            ));
        }
    }
    out
}

fn resolve_import(
    root: &Path,
    from_rel: &str,
    language: &str,
    name: &str,
    product_roots: &[String],
    go_modules: &[(String, String)],
) -> Option<String> {
    let exists = |rel: &str| root.join(rel).is_file();
    let dir = Path::new(from_rel)
        .parent()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_default();
    match language {
        "python" => {
            let rel_mod = name.trim_start_matches('.').replace('.', "/");
            let mut bases = vec![String::new(), dir.clone() + "/"];
            for pr in product_roots {
                bases.push(pr.clone());
            }
            let mut anc = Path::new(from_rel).parent();
            while let Some(a) = anc {
                bases.push(format!("{}/", a.to_string_lossy()));
                anc = a.parent();
            }
            for b in bases {
                let b = b.trim_start_matches('/').to_string();
                for cand in [
                    format!("{b}{rel_mod}.py"),
                    format!("{b}{rel_mod}/__init__.py"),
                ] {
                    let c = cand.trim_start_matches('/').replace("//", "/");
                    if exists(&c) {
                        return Some(c);
                    }
                }
            }
            None
        }
        "javascript" | "typescript" => {
            if !name.starts_with('.') {
                return None;
            }
            let norm = normalize(
                &Path::new(&dir)
                    .join(name)
                    .to_string_lossy()
                    .replace('\\', "/"),
            );
            for ext in [
                "",
                ".ts",
                ".tsx",
                ".js",
                ".jsx",
                ".mjs",
                "/index.ts",
                "/index.js",
            ] {
                let c = format!("{norm}{ext}");
                if exists(&c) {
                    return Some(c);
                }
            }
            None
        }
        "rust" => {
            let path = name.trim_start_matches("crate::").replace("::", "/");
            let first = path.split('/').next().unwrap_or("");
            for base in [dir.clone(), "src".to_string(), format!("{dir}/..")] {
                for cand in [
                    format!("{base}/{first}.rs"),
                    format!("{base}/{first}/mod.rs"),
                    format!("{base}/{path}.rs"),
                ] {
                    let c = normalize(&cand);
                    if exists(&c) {
                        return Some(c);
                    }
                }
            }
            None
        }
        "go" => {
            // module-path imports (go.mod `module X`): X/a/b -> <dir of go.mod>/a/b/<first non-test .go>
            for (mod_path, mod_dir) in go_modules {
                if let Some(rest) = name.strip_prefix(mod_path.as_str()) {
                    let sub = rest.trim_start_matches('/');
                    let d = if mod_dir.is_empty() {
                        sub.to_string()
                    } else if sub.is_empty() {
                        mod_dir.clone()
                    } else {
                        format!("{mod_dir}/{sub}")
                    };
                    if let Ok(rd) = std::fs::read_dir(root.join(&d)) {
                        let mut files: Vec<String> = rd
                            .filter_map(|e| e.ok())
                            .map(|e| e.file_name().to_string_lossy().to_string())
                            .filter(|n| n.ends_with(".go") && !n.ends_with("_test.go"))
                            .collect();
                        files.sort();
                        if let Some(f) = files.first() {
                            return Some(normalize(&format!("{d}/{f}")));
                        }
                    }
                }
            }
            for cand in [format!("{dir}/{name}"), name.to_string()] {
                let c = normalize(&cand);
                if exists(&c) {
                    return Some(c);
                }
            }
            None
        }
        "c" | "cpp" => {
            for cand in [format!("{dir}/{name}"), name.to_string()] {
                let c = normalize(&cand);
                if exists(&c) {
                    return Some(c);
                }
            }
            None
        }
        _ => None,
    }
}

fn normalize(p: &str) -> String {
    let mut out: Vec<&str> = vec![];
    for seg in p.split('/') {
        match seg {
            "" | "." => {}
            ".." => {
                out.pop();
            }
            s => out.push(s),
        }
    }
    out.join("/")
}

fn go_modules(root: &Path, files: &[(PathBuf, String)]) -> Vec<(String, String)> {
    let mut out = vec![];
    for (abs, rel) in files {
        if rel == "go.mod" || rel.ends_with("/go.mod") {
            if let Ok(t) = read_text(abs) {
                if let Some(line) = t.lines().find(|l| l.trim_start().starts_with("module ")) {
                    let m = line.trim().trim_start_matches("module ").trim().to_string();
                    let dir = Path::new(rel)
                        .parent()
                        .map(|d| d.to_string_lossy().to_string())
                        .unwrap_or_default();
                    out.push((m, dir));
                }
            }
        }
    }
    let _ = root;
    out
}

/// Rebuild (full or incremental) the derived index. Full builds are staged in a temporary database and swapped in
/// only on success, so a failing embedder never leaves a partial index behind.
pub fn rebuild(p: &Project, opts: IndexOptions) -> Result<IndexReport> {
    let started = std::time::Instant::now();
    p.require_installed()?;
    std::fs::create_dir_all(p.runtime_dir())?;
    let pol = p.policies();
    let governed = plugin_set(p); // schema-valid, registered, healthy, pinned, authorised for the acting role
    let plugins = governed.usable.clone();
    let spec = opts
        .embed_override
        .clone()
        .unwrap_or_else(|| EmbedSpec::from_policy(p));
    let embed = Embedder::resolve(&spec, &governed)?; // no silent fallback
    let reranker = Reranker::resolve(p, &governed)?; // pinned reranker must exist too
    let expected = {
        let mut e = expected_pins(p);
        e["embedder"] = spec.to_value();
        e
    };
    let final_db = opts.db_path.clone().unwrap_or(p.db_path());
    let benchmark_mode = opts.db_path.is_some();
    let mut report = IndexReport::default();
    // --- decide mode: incremental only when the live pins match; otherwise escalate to a full rebuild
    let mut incremental = opts.incremental && !benchmark_mode;
    if incremental {
        if final_db.exists() {
            let live = RuntimeDb::open(&final_db)?;
            if !live.has_schema() {
                incremental = false;
                report.escalated_to_full = Some("runtime database has no schema".into());
            } else {
                let diffs = pin_differences(&expected, &live_pins(&live));
                if !diffs.is_empty() {
                    incremental = false;
                    report.escalated_to_full = Some(format!("pin change: {}", diffs.join("; ")));
                }
            }
        } else {
            incremental = false;
            report.escalated_to_full = Some("no runtime database".into());
        }
    }
    report.mode = if incremental {
        "incremental".into()
    } else {
        "full".into()
    };
    let build_path = if incremental || benchmark_mode {
        final_db.clone()
    } else {
        final_db.with_extension("db.building")
    };
    if !incremental {
        for suffix in ["", "-wal", "-shm"] {
            let f = PathBuf::from(format!("{}{suffix}", build_path.display()));
            if f.exists() {
                std::fs::remove_file(&f)?;
            }
        }
    }
    let tokenizer = lexical_config(p)["tokenizer"]
        .as_str()
        .unwrap_or("unicode61")
        .to_string();
    let db = RuntimeDb::open(&build_path)?;
    db.init_schema_with(&tokenizer)?;
    let prev = if incremental {
        read_index_manifest(p)
    } else {
        None
    };
    let prev_arts: BTreeMap<String, Value> = prev
        .as_ref()
        .and_then(|m| m.get("artifacts"))
        .and_then(|a| a.as_object())
        .map(|o| o.iter().map(|(k, v)| (k.clone(), v.clone())).collect())
        .unwrap_or_default();
    let chunking = chunking_config(p);
    let max_chars = chunking["max_chars"].as_i64().unwrap_or(1200) as usize;
    let overlap = chunking["overlap_chars"].as_i64().unwrap_or(120) as usize;
    let authority = pol
        .effective
        .get("AUTHORITY_POLICY")
        .cloned()
        .unwrap_or(json!({}));
    let contract = p.contract();
    let scanner = p.secret_scanner();
    let product_roots: Vec<String> = contract
        .roots
        .iter()
        .filter(|(k, _)| k == "product")
        .map(|(_, v)| v.clone())
        .collect();
    let repo_commit = p.git_commit();
    let now = now_iso();
    let files = iter_repo_files(&p.root, false);
    let gomods = go_modules(&p.root, &files);
    let mut seen_paths: HashSet<String> = HashSet::new();
    let mut seen_ids: HashSet<String> = HashSet::new();
    let mut supersedes_map: Vec<(String, String)> = vec![];
    let mut pending_vectors: Vec<(String, String, String)> = vec![];
    let mut test_files: Vec<(String, Vec<String>)> = vec![];
    let mut pending_calls: Vec<(String, String, String)> = vec![]; // (src artifact, path, callee name)
    let mut in_batch = 0usize;
    db.begin()?;
    for (abs, rel) in &files {
        let d = contract.decide(rel);
        if d.is_never_index() || scanner.path_is_secret(rel) {
            let reason = if d.is_secret() || scanner.path_is_secret(rel) {
                "secret_class".to_string()
            } else {
                format!("sensitivity:{}", d.sensitivity())
            };
            report.excluded.push(json!({"path": rel, "reason": reason}));
            db.exec(
                "INSERT OR REPLACE INTO excluded(path, reason, detail) VALUES (?1,?2,?3)",
                &[rel, &reason, &d.rule_pattern.clone().unwrap_or_default()],
            )?;
            if let Some(a) = db.artifact_by_path(rel)? {
                db.delete_artifact(a["artifact_id"].as_str().unwrap_or(""))?;
            }
            continue;
        }
        let (lex, sem, gr, code) = (
            d.flag("lexical_index"),
            d.flag("semantic_index"),
            d.flag("graph_index"),
            d.flag("code_index"),
        );
        if !(lex || sem || gr || code) {
            continue;
        }
        if !is_text_file(abs) {
            report
                .excluded
                .push(json!({"path": rel, "reason": "binary"}));
            continue;
        }
        let size = abs.metadata().map(|m| m.len()).unwrap_or(0);
        if size > 2_000_000 {
            report
                .excluded
                .push(json!({"path": rel, "reason": "too_large"}));
            continue;
        }
        let text = match read_text(abs) {
            Ok(t) => t,
            Err(_) => continue,
        };
        let hits = scanner.scan_text(&text, rel);
        if !hits.is_empty() {
            let ids: Vec<String> = hits
                .iter()
                .map(|h| h.pattern_id.clone())
                .collect::<HashSet<_>>()
                .into_iter()
                .collect();
            report
                .excluded
                .push(json!({"path": rel, "reason": "secret_content", "patterns": ids}));
            report.secret_blocked.push(json!({"path": rel, "patterns": ids, "lines": hits.iter().map(|h| h.line).collect::<Vec<_>>()}));
            db.exec(
                "INSERT OR REPLACE INTO excluded(path, reason, detail) VALUES (?1,?2,?3)",
                &[rel, &"secret_content", &ids.join(",")],
            )?;
            if let Some(a) = db.artifact_by_path(rel)? {
                db.delete_artifact(a["artifact_id"].as_str().unwrap_or(""))?;
            }
            continue;
        }
        let hash = sha256_hex(text.as_bytes());
        seen_paths.insert(rel.clone());
        if incremental {
            if let Some(prev_e) = prev_arts.get(rel) {
                if prev_e.get("content_hash").and_then(|v| v.as_str()) == Some(hash.as_str()) {
                    report.unchanged += 1;
                    if let Some(id) = prev_e.get("artifact_id").and_then(|v| v.as_str()) {
                        seen_ids.insert(id.to_string());
                    }
                    continue;
                }
            }
            if let Some(a) = db.artifact_by_path(rel)? {
                db.delete_artifact(a["artifact_id"].as_str().unwrap_or(""))?;
            }
        }
        let record = if rel.ends_with(".yaml") || rel.ends_with(".yml") || rel.ends_with(".md") {
            parse_record_text(&text, rel)
        } else {
            None
        };
        let ext = Path::new(rel)
            .extension()
            .map(|e| e.to_string_lossy().to_lowercase())
            .unwrap_or_default();
        let language = ecosystems::language_for_ext(&ext);
        let (
            artifact_id,
            record_type,
            title,
            status,
            state_class,
            data_json,
            chunks,
            superseded_by,
        ): (
            String,
            String,
            String,
            String,
            String,
            String,
            Vec<Chunk>,
            Option<String>,
        );
        let mut edges: Vec<(String, String, String)> = vec![];
        let mut symbols: Vec<code_intelligence::Symbol> = vec![];
        let mut sym_refs: Vec<(String, String, String)> = vec![];
        let mut provider = String::new();
        match record {
            Some(r) if !r.id().is_empty() && !r.rtype().is_empty() => {
                let id = r.id();
                if seen_ids.contains(&id) {
                    report.problems.push(format!(
                        "duplicate record id {id} at {rel} (first occurrence kept)"
                    ));
                    continue;
                }
                if incremental {
                    if let Some(a) = db.artifact(&id)? {
                        let old_path = a["path"].as_str().unwrap_or("").to_string();
                        if old_path != *rel {
                            if p.root.join(&old_path).exists()
                                && !seen_paths.contains(&old_path)
                                && iter_repo_files(&p.root, false)
                                    .iter()
                                    .any(|(_, r)| r == &old_path)
                            {
                                report.problems.push(format!("duplicate record id {id} at {rel} (first occurrence {old_path} kept)"));
                                continue;
                            }
                            // relocation (git mv / rename): the record keeps its identity and provenance at the new path
                            db.delete_artifact(&id)?;
                            report
                                .moved
                                .push(json!({"artifact_id": id, "from": old_path, "to": rel}));
                        }
                    }
                }
                seen_ids.insert(id.clone());
                artifact_id = id.clone();
                record_type = r.rtype();
                title = r.title();
                status = if d.class() == "historical" && r.status() == "ACTIVE" {
                    "HISTORICAL".into()
                } else {
                    r.status()
                };
                state_class = if d.class() == "historical" {
                    "HISTORICAL".into()
                } else {
                    state_class_for(&r, &authority)
                };
                data_json = serde_json::to_string(&r.data)?;
                let fields = r.text_fields();
                let body = if r.body.is_empty() {
                    r.get("body")
                } else {
                    r.body.clone()
                };
                chunks = chunk_record(&title, &fields, &body, max_chars, overlap);
                for (t, target) in r.relations() {
                    edges.push((id.clone(), t.clone(), target.clone()));
                    if t == "SUPERSEDES" {
                        supersedes_map.push((id.clone(), target));
                    }
                }
                let sb = r.get("superseded_by");
                superseded_by = if sb.is_empty() { None } else { Some(sb) };
            }
            _ => {
                artifact_id = format!("file:{rel}");
                record_type = "file".into();
                title = rel.clone();
                status = if d.class() == "historical" {
                    "HISTORICAL".into()
                } else {
                    "ACTIVE".into()
                };
                state_class = match d.class().as_str() {
                    "source" | "test" | "devops" | "tooling" => "EVIDENCE",
                    "historical" => "HISTORICAL",
                    "generated" | "derived" => "DERIVED",
                    "authoritative" => "AUTHORITATIVE",
                    _ => "NARRATIVE",
                }
                .into();
                data_json = "{}".into();
                superseded_by = None;
                if let (true, Some(lang)) = (code, language) {
                    let facts = code_intelligence::analyze(rel, lang, &text, &plugins, &p.root);
                    provider = facts.provider.clone();
                    if let Some(dg) = &facts.degraded {
                        report.degradations.push(format!("{rel}: {dg}"));
                    }
                    chunks = chunk_code(rel, &text, &facts.units, max_chars, overlap);
                    symbols = facts.symbols.clone();
                    let mut resolved = vec![];
                    for imp in &facts.imports {
                        match resolve_import(&p.root, rel, lang, imp, &product_roots, &gomods) {
                            Some(target) => {
                                let td = contract.decide(&target);
                                if td.is_never_index() || scanner.path_is_secret(&target) {
                                    edges.push((
                                        artifact_id.clone(),
                                        "IMPORTS".into(),
                                        format!("excluded:{target}"),
                                    ));
                                    sym_refs.push((
                                        imp.clone(),
                                        "import".into(),
                                        format!("excluded:{target}"),
                                    ));
                                } else {
                                    edges.push((
                                        artifact_id.clone(),
                                        "IMPORTS".into(),
                                        format!("file:{target}"),
                                    ));
                                    sym_refs.push((
                                        imp.clone(),
                                        "import".into(),
                                        format!("file:{target}"),
                                    ));
                                    resolved.push(format!("file:{target}"));
                                }
                            }
                            None => {
                                sym_refs.push((
                                    imp.clone(),
                                    "import".into(),
                                    format!("module:{imp}"),
                                ));
                            }
                        }
                    }
                    for (from, name) in &facts.calls {
                        sym_refs.push((name.clone(), "call".into(), from.clone()));
                        pending_calls.push((artifact_id.clone(), rel.clone(), name.clone()));
                    }
                    if d.class() == "test" {
                        test_files.push((artifact_id.clone(), resolved));
                    }
                } else if ext == "md" || ext == "txt" || ext == "rst" {
                    chunks =
                        crate::memory::chunking::chunk_markdown(rel, &text, max_chars, overlap);
                } else {
                    chunks = chunk_plain(rel, &text, max_chars, overlap);
                }
            }
        }
        db.exec("INSERT OR REPLACE INTO artifacts(artifact_id, path, record_type, title, status, state_class, namespace, sensitivity, path_class, content_hash, repo_commit, index_version, size, indexed_at, data_json, semantic, lexical, graph, code, default_retrieval, superseded_by) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,?16,?17,?18,?19,?20,?21)",
            &[&artifact_id, rel, &record_type, &title, &status, &state_class, &d.namespace(), &d.sensitivity(), &d.class(), &hash, &repo_commit, &INDEX_VERSION, &(size as i64), &now, &data_json, &(sem as i64), &(lex as i64), &(gr as i64), &(code as i64), &(d.default_retrieval() as i64), &superseded_by])?;
        for c in &chunks {
            let chunk_id = format!("{artifact_id}#{}", c.ordinal);
            let parent = c.parent_ordinal.map(|po| format!("{artifact_id}#{po}"));
            let chash = sha256_hex(c.text.as_bytes());
            db.exec("INSERT OR REPLACE INTO chunks(chunk_id, artifact_id, parent_chunk_id, level, section, ordinal, content_hash, text, chars, lexical, semantic) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11)", &[&chunk_id, &artifact_id, &parent, &c.level, &c.section, &(c.ordinal as i64), &chash, &c.text, &(c.text.chars().count() as i64), &(lex as i64), &(sem as i64)])?;
            if lex {
                db.exec(
                    "INSERT INTO chunks_fts(text, chunk_id, artifact_id) VALUES (?1,?2,?3)",
                    &[&c.text, &chunk_id, &artifact_id],
                )?;
            }
            if sem {
                pending_vectors.push((chunk_id, artifact_id.clone(), c.text.clone()));
            }
        }
        if gr {
            for (s, t, dst) in &edges {
                db.exec("INSERT OR IGNORE INTO edges(src, type, dst, source_artifact, provenance) VALUES (?1,?2,?3,?4,?5)", &[s, t, dst, &artifact_id, rel])?;
            }
        }
        for s in &symbols {
            let sid = format!("{rel}::{}", s.qualname);
            db.exec("INSERT OR REPLACE INTO symbols(symbol_id, artifact_id, path, name, qualname, kind, lineno, end_lineno, parent, signature, language, provider) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12)", &[&sid, &artifact_id, rel, &s.name, &s.qualname, &s.kind, &(s.lineno as i64), &(s.end_lineno as i64), &s.parent, &s.signature, &language.unwrap_or(""), &provider])?;
        }
        for (name, kind, target) in &sym_refs {
            db.exec(
                "INSERT INTO symbol_refs(path, name, kind, lineno, target) VALUES (?1,?2,?3,0,?4)",
                &[rel, name, kind, target],
            )?;
        }
        report.indexed += 1;
        in_batch += 1;
        if in_batch >= 500 {
            db.commit()?;
            db.begin()?;
            in_batch = 0;
        }
    }
    for (aid, resolved) in &test_files {
        for target in resolved {
            db.exec("INSERT OR IGNORE INTO edges(src, type, dst, source_artifact, provenance) VALUES (?1,'TESTS',?2,?1,'code-intel')", &[aid, target])?;
        }
    }
    // CALLS edges: callee name resolved to the file defining a symbol of that name (same file preferred)
    for (src, path, callee) in &pending_calls {
        let same = db.query_one("SELECT artifact_id FROM symbols WHERE name=?1 AND path=?2 AND kind != 'module' LIMIT 1", &[callee, path])?;
        let target = match same { Some(r) => Some(r["artifact_id"].as_str().unwrap_or("").to_string()), None => db.query_one("SELECT artifact_id FROM symbols WHERE name=?1 AND kind != 'module' ORDER BY path LIMIT 1", &[callee])?.map(|r| r["artifact_id"].as_str().unwrap_or("").to_string()) };
        if let Some(t) = target {
            if t != *src {
                db.exec("INSERT OR IGNORE INTO edges(src, type, dst, source_artifact, provenance) VALUES (?1,'CALLS',?2,?1,?3)", &[src, &t, &format!("call:{callee}")])?;
            }
        }
    }
    for (superseder, superseded) in &supersedes_map {
        db.exec("UPDATE artifacts SET superseded_by=?1 WHERE artifact_id=?2 AND (superseded_by IS NULL OR superseded_by='')", &[superseder, superseded])?;
        if let Some(a) = db.artifact(superseded)? {
            if a["status"].as_str() == Some("ACTIVE") {
                report.supersession_conflicts.push(json!({"superseded": superseded, "by": superseder, "status": "ACTIVE", "path": a["path"]}));
            }
        }
    }
    if incremental {
        for a in db.query("SELECT artifact_id, path FROM artifacts", &[])? {
            let path = a["path"].as_str().unwrap_or("").to_string();
            if !seen_paths.contains(&path) && !p.root.join(&path).exists() {
                db.delete_artifact(a["artifact_id"].as_str().unwrap_or(""))?;
                report.removed += 1;
            }
        }
    }
    db.commit()?;
    // --- vectors with the pinned embedder (errors abort the build; no fallback)
    let emb_spec = embed.spec();
    db.begin()?;
    for batch in pending_vectors.chunks(256) {
        let texts: Vec<String> = batch.iter().map(|(_, _, t)| t.clone()).collect();
        let vecs = embed.embed_batch(&texts, &p.root).inspect_err(|_e| {
            if !incremental {
                let _ = std::fs::remove_file(&build_path);
            }
        })?;
        for ((chunk_id, artifact_id, _), v) in batch.iter().zip(vecs) {
            db.conn.execute("INSERT OR REPLACE INTO vectors(chunk_id, artifact_id, embedder, dim, vec) VALUES (?1,?2,?3,?4,?5)", params![chunk_id, artifact_id, emb_spec.id, v.len() as i64, serde_json::to_string(&v)?])?;
        }
    }
    db.commit()?;
    // --- pins + capability memory
    db.set_meta("embedder", &emb_spec.to_value())?;
    db.set_meta(
        "reranker",
        &reranker
            .as_ref()
            .map(|r| r.spec.to_value())
            .unwrap_or(json!({"provider": "none", "version": "0"})),
    )?;
    db.set_meta("chunking", &chunking)?;
    db.set_meta("lexical", &lexical_config(p))?;
    db.set_meta("index_version", &json!(INDEX_VERSION))?;
    db.set_meta("built_at", &json!(now))?;
    let eco = ecosystems::detect(&p.root, &product_roots);
    db.set_meta("capability.ecosystems", &eco)?;
    db.set_meta("capability.plugins", &json!({"usable": plugins.iter().map(|d| json!({"plugin_id": d.plugin_id, "capability": d.capability, "version": d.version})).collect::<Vec<_>>(), "denied": governed.denied, "rejected": governed.rejected}))?;
    db.set_meta("capability.degradations", &json!(report.degradations))?;
    db.set_meta(
        "supersession_conflicts",
        &json!(report.supersession_conflicts),
    )?;
    let excluded_all = db.query("SELECT path, reason FROM excluded ORDER BY path", &[])?;
    let manifest = build_index_manifest(
        p,
        &db,
        &emb_spec.to_value(),
        &chunking,
        &excluded_all,
        &lexical_config(p),
        &reranker
            .as_ref()
            .map(|r| r.spec.to_value())
            .unwrap_or(json!({"provider": "none"})),
    )?;
    report.manifest_hash = manifest["manifest_hash"].as_str().unwrap_or("").to_string();
    report.counts = db.counts();
    db.set_meta("index_manifest_hash", &manifest["manifest_hash"])?;
    drop(db);
    if !incremental && !benchmark_mode {
        // swap the staged database in atomically
        for suffix in ["", "-wal", "-shm"] {
            let f = PathBuf::from(format!("{}{suffix}", final_db.display()));
            if f.exists() {
                std::fs::remove_file(&f)?;
            }
        }
        std::fs::rename(&build_path, &final_db)
            .map_err(|e| GovError::new("IO_ERROR", format!("swap index database: {e}")))?;
        for suffix in ["-wal", "-shm"] {
            let f = PathBuf::from(format!("{}{suffix}", build_path.display()));
            if f.exists() {
                let _ = std::fs::remove_file(&f);
            }
        }
    }
    if !benchmark_mode {
        let db2 = RuntimeDb::open(&final_db)?;
        write_manifests(p, &db2, &manifest)?;
    }
    report.embedder = emb_spec.to_value();
    report.reranker = reranker
        .as_ref()
        .map(|r| r.spec.to_value())
        .unwrap_or(json!({"provider": "none"}));
    report.ecosystems = eco;
    report.duration_ms = started.elapsed().as_millis();
    let _ = PluginDescriptor::from_value(&Value::Null, "");
    Ok(report)
}
