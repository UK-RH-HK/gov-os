//! Incremental index pipeline: repository files -> artifacts/chunks/FTS/vectors/edges/symbols -> manifests.
//! Never read: secret-class paths and any sensitivity class in SECURITY_POLICY.never_index_classes (fail closed).
//! The embedding implementation is the one pinned by policy; it is recorded in runtime meta and the manifest and a
//! pin change escalates an incremental build to a full rebuild (no mixed-embedder index, no silent fallback).
//!
//! **Incremental equals full (BC-P2-29, Contract v3:308-313).** Three rules make an incremental build derive the
//! same index as a full one:
//! 1. *Current policy.* Every build reads the policy set, overlay and path map from disk ([`current_view`]), never
//!    from a view a caller cached before a governed mutation (CIT-E applies a manifest and then refreshes: the
//!    refresh runs under the post-mutation path map and pins, and fails — so the transaction rolls back — when the
//!    new pins cannot be built).
//! 2. *Per-artefact derivation key.* Besides its content hash, each artefact carries a key over everything outside
//!    its content that shapes its derived rows: its path-map decision (class, namespace, sensitivity, index flags,
//!    default retrieval), the code-intelligence adapter that analyses it, and the authority state-class mapping for
//!    records ([`DerivationContext`]). An unchanged file whose key changed (a path-map reclassification, an adapter
//!    registered or replaced) is re-derived, and `manifest::freshness` reports it stale until it is.
//! 3. *Cross-artefact facts are derived globally.* Import resolution, `IMPORTS`/`CALLS`/`TESTS` edges,
//!    inheritance/implementation edges and supersession are recomputed over the whole index after every build
//!    ([`derive_cross_artifact_facts`]), so a fact owned by an unchanged file that depends on a changed one (a
//!    caller's `CALLS` edge to a renamed function, a superseder that was removed) never goes stale.
use crate::capabilities::ecosystems;
use crate::capabilities::governance::plugin_set;
use crate::capabilities::protocol::PluginDescriptor;
use crate::code_intelligence;
use crate::memory::chunking::{chunk_code, chunk_plain, chunk_record, uncovered_lines_with, Chunk};
use crate::memory::db::RuntimeDb;
use crate::memory::embedder::{EmbedSpec, Embedder, RerankSpec, Reranker};
use crate::memory::manifest::{build_index_manifest, read_index_manifest, write_manifests};
use crate::paths::{iter_repo_files, PathDecision};
use crate::records::{parse_record_text, state_class_for, Record};
use crate::util::{hash_value, is_text_file, now_iso, read_text, sha256_hex};
use crate::{GovError, Project, Result, INDEX_VERSION};
use rusqlite::params;
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Default)]
pub struct IndexOptions {
    pub incremental: bool,
    /// Build into this database instead of the project runtime (benchmarks); manifests are not written.
    pub db_path: Option<PathBuf>,
    /// Override the policy-pinned embedder (benchmarks only).
    pub embed_override: Option<EmbedSpec>,
    /// Record the tool failures this build observes in failure memory (`memory::failures`). Default: yes, except
    /// for benchmark builds (a failing candidate is a benchmark result, recorded in its research record).
    pub record_failures: Option<bool>,
    /// **Observe checkpoint boundaries (R2-11; WS-4 BC-P2-05, Contract v3 N2 "significant mutation").** When the
    /// build finds that at least `CHECKPOINT_POLICY.watchdog.max_operations_between_checkpoints` artefacts were
    /// added, changed or removed since the previous index build, every mandatory trigger not yet checkpointed is
    /// turned into a checkpoint (`checkpoints::observe_boundaries`) and, if none of them is the significant
    /// mutation itself, a `significant_mutation` checkpoint is written. For a build a host runs **as its own
    /// operation** (`gov rebuild-memory`, `gov memory rebuild`): the index refresh inside another governed operation
    /// (change-transaction execution, task close, update, adoption, a checkpoint's own refresh) stays off, because
    /// that operation records its own boundary (accepted CIT, task transition, migration batch) and a record written
    /// in the middle of it would become part of what it verifies. Default: off.
    pub observe_boundaries: bool,
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
    /// Unchanged-content artefacts re-derived because their derivation key changed (reclassification, adapter).
    pub rederived: Vec<String>,
    /// Coverage of the artefacts (re)indexed by this build: every non-empty code line and every record content
    /// line must be held by a chunk (`memory::coverage`).
    pub coverage: Value,
    /// Failure-memory outcomes for tool failures this build observed.
    pub failures: Vec<Value>,
    /// Graph integrity of the built index (BC-P2-28): orphan, dangling, stale, reversed and ill-typed relationships
    /// raised as findings (`memory::integrity`).
    pub graph_integrity: Value,
    /// Governance state of the retrieval profile the build used (BC-P2-30, `memory::profile::governance`).
    pub retrieval_profile: Value,
    /// Non-rebuildable OS state still kept inside the derived runtime or generated directory (BC-P2-31,
    /// `paths::misplaced_os_state`).
    pub os_state: Vec<Value>,
    /// With `IndexOptions::observe_boundaries`: the mutation this build observed and the checkpoints it wrote
    /// (`null` otherwise).
    pub boundaries: Value,
}

pub fn lexical_config(p: &Project) -> Value {
    json!({"engine": "sqlite-fts5", "tokenizer": p.policies().get_str("MEMORY_POLICY", "lexical.tokenizer", "unicode61")})
}
pub fn chunking_config(p: &Project) -> Value {
    let pol = p.policies();
    json!({"max_chars": pol.get_i64("MEMORY_POLICY", "chunking.max_chars", 1200).max(200), "overlap_chars": pol.get_i64("MEMORY_POLICY", "chunking.overlap_chars", 120), "levels": ["document", "section", "child"], "chunker": crate::memory::chunking::CHUNKER_VERSION})
}

/// The pins the live index must satisfy: embedder (with the component identity of the implementation that would
/// execute now: adapter, model artefact, runtime — BC-P2-30), reranker, chunking, lexical engine, index format
/// version.
pub fn expected_pins(p: &Project) -> Value {
    expected_pins_with(p, &plugin_set(p))
}

/// [`expected_pins`] against a plugin set the caller already classified for the acting role.
pub fn expected_pins_with(
    p: &Project,
    plugins: &crate::capabilities::governance::PluginSet,
) -> Value {
    let spec = EmbedSpec::from_policy(p);
    let embedder = crate::memory::profile::expected_embedder_pin(p, &spec, plugins);
    json!({"embedder": embedder, "reranker": RerankSpec::from_policy(p).to_value(), "chunking": chunking_config(p), "lexical": lexical_config(p), "index_version": INDEX_VERSION})
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

/// A view of the project whose policy set, overlay, path map and secret scanner are read from disk now — never a
/// cache taken before a mutation. Same root, session and role as `p`.
pub fn current_view(p: &Project) -> Project {
    Project::open(&p.root).with_session(Some(p.session_id.clone()), Some(p.role.clone()))
}

/// Everything outside an artefact's content that shapes its derived index rows.
pub struct DerivationContext {
    plugins: Vec<PluginDescriptor>,
    authority_sig: String,
    /// What the secret scanner excludes (`SecretScanner::signature`): a secret-scanning policy change re-derives,
    /// and so re-scans, every artefact (an excluded or indexed file is never judged under the previous rules).
    scanner_sig: String,
    provider_cache: std::cell::RefCell<HashMap<String, String>>,
}

impl DerivationContext {
    pub fn new(p: &Project, plugins: &[PluginDescriptor]) -> Self {
        let authority = p
            .policies()
            .effective
            .get("AUTHORITY_POLICY")
            .and_then(|a| a.get("default_state_class_by_type"))
            .cloned()
            .unwrap_or(Value::Null);
        DerivationContext {
            plugins: plugins.to_vec(),
            authority_sig: hash_value(&authority),
            scanner_sig: p.secret_scanner().signature(),
            provider_cache: std::cell::RefCell::new(HashMap::new()),
        }
    }
    fn provider(&self, language: &str) -> String {
        if let Some(v) = self.provider_cache.borrow().get(language) {
            return v.clone();
        }
        let v = code_intelligence::provider_identity(language, &self.plugins);
        self.provider_cache
            .borrow_mut()
            .insert(language.to_string(), v.clone());
        v
    }
    /// The derivation key of the artefact at `rel` under decision `d` (path-independent; no machine paths).
    pub fn key(&self, d: &PathDecision, rel: &str) -> String {
        let ext = Path::new(rel)
            .extension()
            .map(|e| e.to_string_lossy().to_lowercase())
            .unwrap_or_default();
        let provider = match (d.flag("code_index"), ecosystems::language_for_ext(&ext)) {
            (true, Some(lang)) => self.provider(lang),
            _ => String::new(),
        };
        let record_like = matches!(ext.as_str(), "yaml" | "yml" | "md");
        let v = json!({
            "class": d.class(), "namespace": d.namespace(), "sensitivity": d.sensitivity(),
            "default_retrieval": d.default_retrieval(), "never_index": d.is_never_index(),
            "flags": [d.flag("lexical_index"), d.flag("semantic_index"), d.flag("graph_index"), d.flag("code_index")],
            "provider": provider, "authority": if record_like { self.authority_sig.as_str() } else { "" },
            "secret_scanner": self.scanner_sig,
        });
        sha256_hex(v.to_string().as_bytes())[..32].to_string()
    }
}

// ---------------------------------------------------------------------------------------------- admission

/// Largest file the index holds, in bytes. A larger file is excluded (`too_large`); `manifest::freshness` applies
/// the same limit, so such a file is never reported as unindexed.
pub const MAX_INDEXED_FILE_BYTES: u64 = 2_000_000;

/// Reasons recorded in the index manifest's `excluded` list whose truth depends on the file's **content** (not on
/// its path or a property freshness can re-read cheaply). Each such entry carries the content hash and derivation
/// key it was decided under; it justifies the file's absence from the index only while both still match.
pub const CONTENT_EXCLUSIONS: &[&str] = &["secret_content", "duplicate_id"];

/// **How the index treats one repository file** — the single admission decision the indexer
/// ([`rebuild`]) and `memory::manifest::freshness` share (R2-10: a file the indexer skips must never read as
/// "unindexed" to freshness). Content-level exclusions (secret content, a duplicate record id) are decided after
/// admission, on the candidate's text.
#[derive(Debug)]
pub enum Admission {
    /// Not part of the index by its path: a memory-quality event (`Some` reason, reported) or a path-map decision
    /// with no index flag (`None`).
    Outside(Option<&'static str>),
    /// Excluded by the path map or the sensitivity rules (`secret_class`, `sensitivity:<class>`); recorded in the
    /// manifest's `excluded` list with the deciding rule.
    PathExcluded { reason: String, rule: String },
    /// Excluded by a property of the file itself: `binary` (report only), `too_large`, `not_utf8`, `unreadable`
    /// (recorded in `excluded`).
    FileExcluded { reason: &'static str, size: u64 },
    /// An indexable text file.
    Candidate { text: String, size: u64 },
}

/// The admission of the file at `abs` (`rel` from the project root) under path decision `d`.
pub fn admit(
    abs: &Path,
    rel: &str,
    d: &PathDecision,
    scanner: &crate::security::secrets::SecretScanner,
) -> Admission {
    if crate::memory::failures::is_memory_quality_path(rel) {
        // memory-quality events never feed back into retrieval (like the held-out set)
        return Admission::Outside(Some("memory_quality_event"));
    }
    if d.is_never_index() || scanner.path_is_secret(rel) {
        let reason = if d.is_secret() || scanner.path_is_secret(rel) {
            "secret_class".to_string()
        } else {
            format!("sensitivity:{}", d.sensitivity())
        };
        return Admission::PathExcluded {
            reason,
            rule: d.rule_pattern.clone().unwrap_or_default(),
        };
    }
    if !(d.flag("lexical_index")
        || d.flag("semantic_index")
        || d.flag("graph_index")
        || d.flag("code_index"))
    {
        return Admission::Outside(None);
    }
    let size = abs.metadata().map(|m| m.len()).unwrap_or(0);
    if !is_text_file(abs) {
        return Admission::FileExcluded {
            reason: "binary",
            size,
        };
    }
    if size > MAX_INDEXED_FILE_BYTES {
        return Admission::FileExcluded {
            reason: "too_large",
            size,
        };
    }
    match std::fs::read(abs) {
        Err(_) => Admission::FileExcluded {
            reason: "unreadable",
            size,
        },
        Ok(bytes) => match String::from_utf8(bytes) {
            Ok(text) => Admission::Candidate { text, size },
            Err(_) => Admission::FileExcluded {
                reason: "not_utf8",
                size,
            },
        },
    }
}

/// True for a file the indexer parses as a record.
pub fn record_like(rel: &str) -> bool {
    rel.ends_with(".yaml") || rel.ends_with(".yml") || rel.ends_with(".md")
}

/// Which of several files declaring the same record id the index holds — the one the record store resolves the id
/// to (`records::RecordStore::load`): a record outside `archive/` before an archived one, then `spec/` before
/// `governance/project/` before any other location, then walk order. A function of the tree alone, so a full and
/// an incremental build keep the same occurrence (BC-P2-29) and the index serves the record governance resolves.
fn record_rank(rel: &str, walk_index: usize) -> (u8, u8, usize) {
    let archived = rel.starts_with("archive/");
    let root = if rel.starts_with("spec/") {
        0
    } else if rel.starts_with("governance/project/") {
        1
    } else {
        2
    };
    (archived as u8, root, walk_index)
}

/// The research/experiment state class the index holds (IP-WS10-05): non-governed evidence is held reference-only
/// (`lifecycle::indexed_state_class`). `None` for other record types.
fn evidence_state_class(
    p: &Project,
    store: &std::cell::OnceCell<crate::records::RecordStore>,
    r: &Record,
) -> Option<String> {
    if !crate::lifecycle::EVIDENCE_TYPES.contains(&r.rtype().as_str()) {
        return None;
    }
    let store = store.get_or_init(|| crate::records::RecordStore::load(&p.root));
    let ctx = crate::lifecycle::Ctx::new(p, store);
    Some(crate::lifecycle::indexed_state_class(&ctx, r))
}

/// The state class the index derives for a record at a path of class `path_class`.
fn record_state_class(
    p: &Project,
    store: &std::cell::OnceCell<crate::records::RecordStore>,
    r: &Record,
    path_class: &str,
    authority: &Value,
) -> String {
    if path_class == "historical" {
        return "HISTORICAL".into();
    }
    evidence_state_class(p, store, r).unwrap_or_else(|| state_class_for(r, authority))
}

/// For an artefact whose content and derivation key are unchanged: does the state class the index recorded still
/// hold? Only research and experiment records derive it from other state (their standing, IP-WS10-05); for them the
/// standing is re-evaluated, so an incremental build and freshness see a standing change (incremental equals full).
pub fn recorded_state_class_holds(
    p: &Project,
    store: &std::cell::OnceCell<crate::records::RecordStore>,
    entry: &Value,
    rel: &str,
    text: &str,
    path_class: &str,
) -> bool {
    let rtype = entry
        .get("record_type")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    if !crate::lifecycle::EVIDENCE_TYPES.contains(&rtype) || path_class == "historical" {
        return true;
    }
    let Some(r) = parse_record_text(text, rel) else {
        return false;
    };
    let now = evidence_state_class(p, store, &r).unwrap_or_default();
    entry.get("state_class").and_then(|v| v.as_str()) == Some(now.as_str())
}

/// A declared `code_intel` adapter the acting role may not execute — denied (unregistered, pin drift, changed
/// implementation, not authorised) or rejected (schema-invalid). Files of its languages are analysed by the
/// built-in extractor: a degradation that is recorded, never silent (D-0005; WS-7 IP-W7-2).
#[derive(Debug, Clone)]
struct RefusedAdapter {
    plugin_id: String,
    version: String,
    code: String,
    message: String,
    /// Empty: every language.
    languages: Vec<String>,
}

impl RefusedAdapter {
    fn covers(&self, language: &str) -> bool {
        self.languages.is_empty() || self.languages.iter().any(|l| l == language)
    }
    fn failure_message(&self) -> String {
        format!(
            "code_intel plugin {} v{} is declared but refused ({}): {}; files of {} are analysed by the built-in extractor",
            self.plugin_id,
            self.version,
            self.code,
            self.message,
            if self.languages.is_empty() {
                "every language".to_string()
            } else {
                self.languages.join(", ")
            }
        )
    }
}

/// What the id-ranking pass learned about a record-like candidate it read (reused by the build loop when the
/// file's bytes are unchanged).
struct PreScan {
    hash: String,
    hits: Vec<crate::security::secrets::SecretHit>,
    record: Option<Record>,
}

fn refused_code_intel(
    governed: &crate::capabilities::governance::PluginSet,
) -> Vec<RefusedAdapter> {
    let mut out = vec![];
    for entry in governed.denied.iter().chain(governed.rejected.iter()) {
        let source = entry["source"].as_str().unwrap_or("");
        let desc = crate::util::read_yaml(Path::new(source)).unwrap_or(Value::Null);
        let capability = entry["capability"]
            .as_str()
            .or_else(|| desc["capability"].as_str())
            .unwrap_or("");
        if capability != "code_intel" {
            continue;
        }
        let plugin_id = entry["plugin_id"]
            .as_str()
            .or_else(|| desc["plugin_id"].as_str())
            .unwrap_or("?")
            .to_string();
        let version = entry["version"]
            .as_str()
            .or_else(|| desc["version"].as_str())
            .unwrap_or("")
            .to_string();
        let (code, message) = match governed.refusal(&plugin_id) {
            Some(e) => (e.code, e.message),
            None => (
                entry["code"]
                    .as_str()
                    .unwrap_or("PLUGIN_NOT_AUTHORIZED")
                    .to_string(),
                entry["reason"].as_str().unwrap_or("").to_string(),
            ),
        };
        out.push(RefusedAdapter {
            plugin_id,
            version,
            code,
            message,
            languages: crate::util::str_list(&desc, "languages"),
        });
    }
    out
}

// ---------------------------------------------------------------------------------------------- import resolution

/// Resolves import names to repository files from the file set of the current tree (no filesystem probing, so the
/// result depends only on the tree and is identical for incremental and full builds).
pub struct ImportResolver {
    files: HashSet<String>,
    by_dir: HashMap<String, Vec<String>>,
    by_basename: HashMap<String, Vec<String>>,
    product_roots: Vec<String>,
    go_modules: Vec<(String, String)>,
    rust_crates: Vec<(String, String)>,
}

fn parent_dir(rel: &str) -> String {
    Path::new(rel)
        .parent()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_default()
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

impl ImportResolver {
    pub fn new(root: &Path, files: &[(PathBuf, String)], product_roots: &[String]) -> Self {
        let mut set = HashSet::new();
        let mut by_dir: HashMap<String, Vec<String>> = HashMap::new();
        let mut by_basename: HashMap<String, Vec<String>> = HashMap::new();
        let mut go_modules = vec![];
        let mut rust_crates = vec![];
        for (abs, rel) in files {
            set.insert(rel.clone());
            let name = rel.rsplit('/').next().unwrap_or(rel).to_string();
            by_dir
                .entry(parent_dir(rel))
                .or_default()
                .push(name.clone());
            by_basename
                .entry(name.clone())
                .or_default()
                .push(rel.clone());
            if name == "go.mod" {
                if let Ok(t) = read_text(abs) {
                    if let Some(line) = t.lines().find(|l| l.trim_start().starts_with("module ")) {
                        let m = line.trim().trim_start_matches("module ").trim().to_string();
                        go_modules.push((m, parent_dir(rel)));
                    }
                }
            }
            if name == "Cargo.toml" {
                if let Ok(t) = read_text(abs) {
                    let mut in_pkg = false;
                    for l in t.lines() {
                        let l = l.trim();
                        if l.starts_with('[') {
                            in_pkg = l == "[package]";
                            continue;
                        }
                        if in_pkg && l.starts_with("name") {
                            if let Some(v) =
                                l.split_once('=').map(|(_, v)| v.trim().trim_matches('"'))
                            {
                                rust_crates.push((v.replace('-', "_"), parent_dir(rel)));
                            }
                        }
                    }
                }
            }
        }
        for v in by_dir.values_mut() {
            v.sort();
        }
        for v in by_basename.values_mut() {
            v.sort();
        }
        let _ = root;
        ImportResolver {
            files: set,
            by_dir,
            by_basename,
            product_roots: product_roots.to_vec(),
            go_modules,
            rust_crates,
        }
    }

    fn exists(&self, rel: &str) -> bool {
        self.files.contains(rel)
    }

    /// Files whose path ends with `/<key>` (or equals it), best match first: longest shared directory prefix with
    /// the importing file, then shortest path, then lexical order.
    fn by_suffix(&self, key: &str, from_rel: &str) -> Option<String> {
        let base = key.rsplit('/').next().unwrap_or(key);
        let cands: Vec<&String> = self
            .by_basename
            .get(base)?
            .iter()
            .filter(|f| f.as_str() == key || f.ends_with(&format!("/{key}")))
            .collect();
        let dir = parent_dir(from_rel);
        let shared = |f: &str| {
            dir.split('/')
                .zip(f.split('/'))
                .take_while(|(a, b)| a == b)
                .count()
        };
        cands
            .into_iter()
            .max_by(|a, b| {
                shared(a)
                    .cmp(&shared(b))
                    .then(b.len().cmp(&a.len()))
                    .then(b.cmp(a))
            })
            .cloned()
    }

    /// Nearest ancestor directory of `rel` holding a `Cargo.toml` (the crate root), if any.
    fn crate_root_of(&self, rel: &str) -> Option<String> {
        let mut d = parent_dir(rel);
        loop {
            let c = if d.is_empty() {
                "Cargo.toml".to_string()
            } else {
                format!("{d}/Cargo.toml")
            };
            if self.exists(&c) {
                return Some(d);
            }
            if d.is_empty() {
                return None;
            }
            d = parent_dir(&d);
        }
    }

    pub fn resolve(&self, from_rel: &str, language: &str, name: &str) -> Option<String> {
        let dir = parent_dir(from_rel);
        match language {
            "python" => {
                let dots = name.chars().take_while(|c| *c == '.').count();
                let rel_mod = name.trim_start_matches('.').replace('.', "/");
                if dots > 0 {
                    // relative import: the importing package, then its parents for each extra dot
                    let mut base = dir.clone();
                    for _ in 1..dots {
                        base = parent_dir(&base);
                    }
                    for cand in [
                        format!("{base}/{rel_mod}.py"),
                        format!("{base}/{rel_mod}/__init__.py"),
                    ] {
                        let c = normalize(&cand);
                        if !rel_mod.is_empty() && self.exists(&c) {
                            return Some(c);
                        }
                    }
                }
                let mut bases = vec![String::new(), dir.clone() + "/"];
                for pr in &self.product_roots {
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
                        if self.exists(&c) {
                            return Some(c);
                        }
                    }
                }
                // src-layout and other source roots: the package path anywhere in the tree
                if rel_mod.is_empty() {
                    return None;
                }
                self.by_suffix(&format!("{rel_mod}.py"), from_rel)
                    .or_else(|| self.by_suffix(&format!("{rel_mod}/__init__.py"), from_rel))
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
                    if self.exists(&c) {
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
                        if self.exists(&c) {
                            return Some(c);
                        }
                    }
                }
                // crate-qualified paths: `crate::`, `self::`, `super::`, or another crate of the tree by name
                let segs: Vec<&str> = name.split("::").filter(|s| !s.is_empty()).collect();
                let (src, rest): (Option<String>, &[&str]) = match segs.first().copied() {
                    Some("crate") => (
                        self.crate_root_of(from_rel)
                            .map(|r| normalize(&format!("{r}/src"))),
                        &segs[1..],
                    ),
                    Some("self") => (Some(dir.clone()), &segs[1..]),
                    Some("super") => (Some(parent_dir(&dir)), &segs[1..]),
                    Some(c) => (
                        self.rust_crates
                            .iter()
                            .find(|(n, _)| n == c)
                            .map(|(_, d)| normalize(&format!("{d}/src"))),
                        &segs[1..],
                    ),
                    None => (None, &segs[..]),
                };
                let src = src?;
                for n in (0..=rest.len()).rev() {
                    let sub = rest[..n].join("/");
                    let cands = if sub.is_empty() {
                        vec![format!("{src}/lib.rs"), format!("{src}/main.rs")]
                    } else {
                        vec![format!("{src}/{sub}.rs"), format!("{src}/{sub}/mod.rs")]
                    };
                    for c in cands {
                        let c = normalize(&c);
                        if self.exists(&c) {
                            return Some(c);
                        }
                    }
                }
                None
            }
            "go" => {
                // module-path imports (go.mod `module X`): X/a/b -> <dir of go.mod>/a/b/<first non-test .go>
                for (mod_path, mod_dir) in &self.go_modules {
                    if let Some(rest) = name.strip_prefix(mod_path.as_str()) {
                        let sub = rest.trim_start_matches('/');
                        let d = if mod_dir.is_empty() {
                            sub.to_string()
                        } else if sub.is_empty() {
                            mod_dir.clone()
                        } else {
                            format!("{mod_dir}/{sub}")
                        };
                        if let Some(names) = self.by_dir.get(&normalize(&d)) {
                            if let Some(f) = names
                                .iter()
                                .find(|n| n.ends_with(".go") && !n.ends_with("_test.go"))
                            {
                                return Some(normalize(&format!("{d}/{f}")));
                            }
                        }
                    }
                }
                for cand in [format!("{dir}/{name}"), name.to_string()] {
                    let c = normalize(&cand);
                    if self.exists(&c) {
                        return Some(c);
                    }
                }
                None
            }
            "c" | "cpp" => {
                for cand in [format!("{dir}/{name}"), name.to_string()] {
                    let c = normalize(&cand);
                    if self.exists(&c) {
                        return Some(c);
                    }
                }
                self.by_suffix(name, from_rel)
            }
            _ => None,
        }
    }

    /// The file a *relative* import names when it resolves to nothing in the tree (a broken reference: the target
    /// was renamed or deleted). Represented as an edge to that path, so graph integrity reports it as dangling in
    /// incremental and full builds alike. `None` for non-relative (package/module) imports.
    pub fn intended_path(&self, from_rel: &str, language: &str, name: &str) -> Option<String> {
        let dir = parent_dir(from_rel);
        let ext = Path::new(from_rel)
            .extension()
            .map(|e| e.to_string_lossy().to_string())
            .unwrap_or_default();
        match language {
            "javascript" | "typescript" if name.starts_with('.') => {
                let norm = normalize(&format!("{dir}/{name}"));
                if Path::new(&norm).extension().is_some() || ext.is_empty() {
                    Some(norm)
                } else {
                    Some(format!("{norm}.{ext}"))
                }
            }
            "python" if name.starts_with('.') => {
                let dots = name.chars().take_while(|c| *c == '.').count();
                let rel_mod = name.trim_start_matches('.').replace('.', "/");
                if rel_mod.is_empty() {
                    return None;
                }
                let mut base = dir;
                for _ in 1..dots {
                    base = parent_dir(&base);
                }
                Some(normalize(&format!("{base}/{rel_mod}.py")))
            }
            _ => None,
        }
    }

    /// Non-test Go files of the same package directory (a `_test.go` file tests its package without importing it).
    fn go_package_files(&self, test_rel: &str) -> Vec<String> {
        let dir = parent_dir(test_rel);
        self.by_dir
            .get(&dir)
            .map(|names| {
                names
                    .iter()
                    .filter(|n| n.ends_with(".go") && !n.ends_with("_test.go"))
                    .map(|n| {
                        if dir.is_empty() {
                            n.clone()
                        } else {
                            format!("{dir}/{n}")
                        }
                    })
                    .collect()
            })
            .unwrap_or_default()
    }
}

/// A test file by the conventions of the ecosystems in scope (test directories and test file names), in addition to
/// whatever the path map classifies `test`.
pub fn is_test_path(rel: &str) -> bool {
    let parts: Vec<&str> = rel.split('/').collect();
    let file = parts.last().copied().unwrap_or("");
    if parts[..parts.len().saturating_sub(1)]
        .iter()
        .any(|d| matches!(*d, "tests" | "test" | "__tests__" | "testing"))
    {
        return true;
    }
    let lower = file.to_lowercase();
    (lower.starts_with("test_") && lower.ends_with(".py"))
        || lower.ends_with("_test.py")
        || lower.ends_with("_test.go")
        || lower.ends_with("_test.rs")
        || lower.ends_with("_spec.rb")
        || lower.ends_with("_test.rb")
        || [".test.", ".spec."].iter().any(|m| lower.contains(m))
        || [
            "test.java",
            "tests.java",
            "test.kt",
            "tests.kt",
            "test.cs",
            "tests.cs",
            "test.scala",
            "spec.scala",
        ]
        .iter()
        .any(|s| lower.ends_with(s) && file.len() > s.len())
}

// ---------------------------------------------------------------------------------------------- cross-artefact facts

const TYPE_KINDS: &[&str] = &[
    "class",
    "struct",
    "interface",
    "trait",
    "type",
    "enum",
    "impl",
    "record",
];

/// Recompute every fact that depends on more than one artefact, over the whole index: import targets and `IMPORTS`
/// edges, `CALLS` edges, inheritance (`DEPENDS_ON`, provenance `inherits:`) and implementation (`IMPLEMENTS`)
/// edges, `TESTS` edges (test files by path class or convention → the files they import/call, Go same-package
/// tests → their package), and supersession (`superseded_by`, conflicts). Deterministic and independent of which
/// artefacts this build re-indexed, so an incremental build equals a full build.
pub fn derive_cross_artifact_facts(
    db: &RuntimeDb,
    p: &Project,
    resolver: &ImportResolver,
    report: &mut IndexReport,
) -> Result<()> {
    let contract = p.contract();
    let scanner = p.secret_scanner();
    let arts = db.query(
        "SELECT artifact_id, path, path_class, graph FROM artifacts WHERE record_type='file' ORDER BY path",
        &[],
    )?;
    let mut graph_on: HashSet<String> = HashSet::new();
    let mut tests: BTreeSet<String> = BTreeSet::new();
    let mut path_of: HashMap<String, String> = HashMap::new();
    for a in &arts {
        let aid = a["artifact_id"].as_str().unwrap_or("").to_string();
        let path = a["path"].as_str().unwrap_or("").to_string();
        if a["graph"].as_i64() == Some(1) {
            graph_on.insert(aid.clone());
        }
        if a["path_class"].as_str() == Some("test") || is_test_path(&path) {
            tests.insert(aid.clone());
        }
        path_of.insert(aid, path);
    }
    db.exec(
        "DELETE FROM edges WHERE src LIKE 'file:%' AND (type IN ('IMPORTS','CALLS','TESTS') OR provenance LIKE 'inherits:%' OR provenance LIKE 'implements:%')",
        &[],
    )?;
    // --- imports
    let mut imports_of: HashMap<String, Vec<String>> = HashMap::new();
    for r in db.query(
        "SELECT rowid AS rid, path, name, target FROM symbol_refs WHERE kind='import' ORDER BY path, name, rowid",
        &[],
    )? {
        let path = r["path"].as_str().unwrap_or("");
        let name = r["name"].as_str().unwrap_or("");
        let src = format!("file:{path}");
        let ext = Path::new(path)
            .extension()
            .map(|e| e.to_string_lossy().to_lowercase())
            .unwrap_or_default();
        let lang = ecosystems::language_for_ext(&ext).unwrap_or("");
        let target = match resolver.resolve(path, lang, name) {
            Some(t) => {
                let td = contract.decide(&t);
                if td.is_never_index() || scanner.path_is_secret(&t) {
                    format!("excluded:{t}")
                } else {
                    format!("file:{t}")
                }
            }
            // a relative import of a file that is not in the tree is a broken reference, not an external module
            None => match resolver.intended_path(path, lang, name) {
                Some(t) => format!("file:{t}"),
                None => format!("module:{name}"),
            },
        };
        if r["target"].as_str() != Some(target.as_str()) {
            db.exec(
                "UPDATE symbol_refs SET target=?1 WHERE rowid=?2",
                &[&target, &r["rid"].as_i64().unwrap_or(0)],
            )?;
        }
        if (target.starts_with("file:") || target.starts_with("excluded:")) && graph_on.contains(&src) {
            db.exec("INSERT OR IGNORE INTO edges(src, type, dst, source_artifact, provenance) VALUES (?1,'IMPORTS',?2,?1,?3)", &[&src, &target, &format!("import:{name}")])?;
        }
        if target.starts_with("file:") {
            imports_of.entry(src).or_default().push(target);
        }
    }
    // --- calls: callee name resolved to the file defining a symbol of that name (same file preferred)
    let mut calls_of: HashMap<String, BTreeSet<String>> = HashMap::new();
    let mut first_def: HashMap<String, Option<String>> = HashMap::new();
    for r in db.query(
        "SELECT DISTINCT path, name FROM symbol_refs WHERE kind='call' ORDER BY path, name",
        &[],
    )? {
        let path = r["path"].as_str().unwrap_or("").to_string();
        let callee = r["name"].as_str().unwrap_or("").to_string();
        let src = format!("file:{path}");
        let same = db.query_one("SELECT artifact_id FROM symbols WHERE name=?1 AND path=?2 AND kind NOT IN ('module','route','db_model') LIMIT 1", &[&callee, &path])?;
        let target = match same {
            Some(r) => Some(r["artifact_id"].as_str().unwrap_or("").to_string()),
            None => first_def
                .entry(callee.clone())
                .or_insert_with(|| {
                    db.query_one("SELECT artifact_id FROM symbols WHERE name=?1 AND kind NOT IN ('module','route','db_model') ORDER BY path LIMIT 1", &[&callee])
                        .ok()
                        .flatten()
                        .map(|r| r["artifact_id"].as_str().unwrap_or("").to_string())
                })
                .clone(),
        };
        if let Some(t) = target {
            if t != src && !t.is_empty() {
                db.exec("INSERT OR IGNORE INTO edges(src, type, dst, source_artifact, provenance) VALUES (?1,'CALLS',?2,?1,?3)", &[&src, &t, &format!("call:{callee}")])?;
                calls_of.entry(src).or_default().insert(t);
            }
        }
    }
    // --- inheritance / implementation
    for r in db.query(
        "SELECT DISTINCT path, name, kind FROM symbol_refs WHERE kind IN ('inherits','implements') ORDER BY path, name, kind",
        &[],
    )? {
        let path = r["path"].as_str().unwrap_or("").to_string();
        let base = r["name"].as_str().unwrap_or("").to_string();
        let kind = r["kind"].as_str().unwrap_or("").to_string();
        let src = format!("file:{path}");
        let defs: Vec<String> = db
            .query(
                &format!(
                    "SELECT DISTINCT artifact_id FROM symbols WHERE name=?1 AND kind IN ({}) ORDER BY path",
                    TYPE_KINDS
                        .iter()
                        .map(|k| format!("'{k}'"))
                        .collect::<Vec<_>>()
                        .join(",")
                ),
                &[&base],
            )?
            .into_iter()
            .filter_map(|x| x["artifact_id"].as_str().map(|s| s.to_string()))
            .collect();
        if defs.is_empty() || defs.contains(&src) {
            continue; // external supertype, or defined in the same file
        }
        let imported = imports_of.get(&src).cloned().unwrap_or_default();
        let dst = defs
            .iter()
            .find(|d| imported.contains(d))
            .cloned()
            .unwrap_or_else(|| defs[0].clone());
        let etype = if kind == "implements" {
            "IMPLEMENTS"
        } else {
            "DEPENDS_ON"
        };
        db.exec("INSERT OR IGNORE INTO edges(src, type, dst, source_artifact, provenance) VALUES (?1,?2,?3,?1,?4)", &[&src, &etype, &dst, &format!("{kind}:{base}")])?;
    }
    // --- test-coverage relationships
    for t in &tests {
        let mut targets: BTreeMap<String, &str> = BTreeMap::new();
        for d in imports_of.get(t).cloned().unwrap_or_default() {
            targets.entry(d).or_insert("import");
        }
        for d in calls_of.get(t).cloned().unwrap_or_default() {
            targets.entry(d).or_insert("call");
        }
        let tpath = path_of.get(t).cloned().unwrap_or_default();
        if tpath.ends_with("_test.go") {
            for f in resolver.go_package_files(&tpath) {
                targets.entry(format!("file:{f}")).or_insert("package");
            }
        }
        for (dst, basis) in targets {
            if tests.contains(&dst) || &dst == t || !path_of.contains_key(&dst) {
                continue;
            }
            db.exec("INSERT OR IGNORE INTO edges(src, type, dst, source_artifact, provenance) VALUES (?1,'TESTS',?2,?1,?3)", &[t, &dst, &format!("tests:{basis}")])?;
        }
    }
    // --- supersession: a record's own `superseded_by`, else the first superseder (path order) that names it
    let recs = db.query(
        "SELECT artifact_id, path, data_json, status, superseded_by FROM artifacts WHERE record_type != 'file' ORDER BY path",
        &[],
    )?;
    let mut sb: BTreeMap<String, Option<String>> = BTreeMap::new();
    let mut status_of: HashMap<String, (String, String)> = HashMap::new();
    let mut pairs: Vec<(String, String)> = vec![];
    for r in &recs {
        let aid = r["artifact_id"].as_str().unwrap_or("").to_string();
        let data: Value =
            serde_json::from_str(r["data_json"].as_str().unwrap_or("{}")).unwrap_or(json!({}));
        let own = data
            .get("superseded_by")
            .and_then(|v| v.as_str())
            .filter(|s| !s.is_empty())
            .map(|s| s.to_string());
        sb.insert(aid.clone(), own);
        status_of.insert(
            aid.clone(),
            (
                r["status"].as_str().unwrap_or("").to_string(),
                r["path"].as_str().unwrap_or("").to_string(),
            ),
        );
        let rec = Record {
            path: r["path"].as_str().unwrap_or("").to_string(),
            data,
            body: String::new(),
            format: crate::records::RecordFormat::Yaml,
            problems: vec![],
        };
        for (t, target) in rec.relations() {
            if t == "SUPERSEDES" {
                pairs.push((aid.clone(), target));
            }
        }
    }
    for (superseder, superseded) in &pairs {
        if let Some(slot) = sb.get_mut(superseded) {
            if slot.is_none() {
                *slot = Some(superseder.clone());
            }
        }
    }
    let current: HashMap<String, Option<String>> = recs
        .iter()
        .map(|r| {
            (
                r["artifact_id"].as_str().unwrap_or("").to_string(),
                r["superseded_by"]
                    .as_str()
                    .filter(|s| !s.is_empty())
                    .map(|s| s.to_string()),
            )
        })
        .collect();
    for (aid, v) in &sb {
        if current.get(aid) != Some(v) {
            db.exec(
                "UPDATE artifacts SET superseded_by=?1 WHERE artifact_id=?2",
                &[v, aid],
            )?;
        }
    }
    report.supersession_conflicts.clear();
    for (superseder, superseded) in &pairs {
        if let Some((status, path)) = status_of.get(superseded) {
            if status == "ACTIVE" {
                report.supersession_conflicts.push(json!({"superseded": superseded, "by": superseder, "status": "ACTIVE", "path": path}));
            }
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------------------------- per-artefact indexing

/// Structural units for the chunker: every symbol with a span (nested ones included) plus the adapter's own units.
fn chunk_units(facts: &code_intelligence::CodeFacts) -> Vec<(String, usize, usize)> {
    let mut u: Vec<(String, usize, usize)> = vec![];
    for s in &facts.symbols {
        if matches!(s.kind.as_str(), "module" | "route" | "db_model")
            || s.qualname.is_empty()
            || s.lineno == 0
            || s.end_lineno < s.lineno
        {
            continue;
        }
        let x = (s.qualname.clone(), s.lineno, s.end_lineno);
        if !u.contains(&x) {
            u.push(x);
        }
    }
    for x in &facts.units {
        if x.0 != crate::memory::chunking::MODULE_SECTION && !u.contains(x) {
            u.push(x.clone());
        }
    }
    u
}

use crate::memory::coverage::without_heading_markers;

#[derive(Default)]
struct CoverageTally {
    checked: usize,
    uncovered: usize,
    gaps: Vec<Value>,
}

impl CoverageTally {
    /// `markdown`: the content is a record's or a document's (headings compared by their text on both sides,
    /// `memory::coverage`).
    fn check(
        &mut self,
        rel: &str,
        expected: &str,
        chunks: &[Chunk],
        max_chars: usize,
        markdown: bool,
    ) {
        self.checked += 1;
        let miss = uncovered_lines_with(expected, chunks, max_chars, markdown);
        if !miss.is_empty() {
            self.uncovered += miss.len();
            if self.gaps.len() < 20 {
                self.gaps
                    .push(crate::memory::coverage::gap_row(None, rel, &miss));
            }
        }
    }
    fn to_value(&self) -> Value {
        json!({"checked_artifacts": self.checked, "uncovered_lines": self.uncovered, "complete": self.uncovered == 0, "gaps": self.gaps})
    }
}

/// Adapter failures observed during a build, grouped by adapter identity and error code.
#[derive(Default)]
struct AdapterFailures {
    by_key: BTreeMap<(String, String, String), (String, Vec<String>)>,
}

fn tool_failure_from(
    kind: &str,
    id: &str,
    version: &str,
    e: &GovError,
    operation: &str,
) -> crate::memory::failures::ToolFailure {
    crate::memory::failures::ToolFailure {
        tool_kind: kind.into(),
        tool_id: id.into(),
        version: version.into(),
        code: e.code.clone(),
        message: e.message.clone(),
        operation: operation.into(),
        affected: vec![],
    }
}

/// Rebuild (full or incremental) the derived index. Full builds are staged in a temporary database and swapped in
/// only on success, so a failing embedder never leaves a partial index behind.
pub fn rebuild(p_in: &Project, opts: IndexOptions) -> Result<IndexReport> {
    let started = std::time::Instant::now();
    p_in.require_installed()?;
    // the never-index / secret floors applied below come from kernel policy: refuse to index against an
    // unverified kernel rather than silently indexing under a tampered floor (verifier V-H2 / VV-14)
    crate::kernel_trust::guard(p_in, "rebuild-memory")?;
    // BC-P2-29: derive from the policy, overlay and path map on disk now, not from a view cached by the caller
    let view = current_view(p_in);
    let p = &view;
    std::fs::create_dir_all(p.runtime_dir())?;
    let final_db = opts.db_path.clone().unwrap_or(p.db_path());
    let benchmark_mode = opts.db_path.is_some();
    let record_failures = opts.record_failures.unwrap_or(!benchmark_mode) && !benchmark_mode;
    let mut report = IndexReport::default();
    let note_tool_failure = |report: &mut IndexReport, t: crate::memory::failures::ToolFailure| {
        if record_failures {
            let o = crate::memory::failures::record_tool_failure(p, &t, false);
            report.failures.push(o.to_value());
        }
    };
    let pol = p.policies();
    let governed = plugin_set(p); // schema-valid, registered, healthy, pinned, authorised for the acting role
    let plugins = governed.usable.clone();
    let spec = opts
        .embed_override
        .clone()
        .unwrap_or_else(|| EmbedSpec::from_policy(p));
    let embed = match Embedder::resolve(&spec, &governed) {
        Ok(e) => e,
        Err(e) => {
            note_tool_failure(
                &mut report,
                tool_failure_from("embed", &spec.id, &spec.version, &e, "rebuild-memory"),
            );
            return Err(e); // no silent fallback
        }
    };
    let reranker = match Reranker::resolve(p, &governed) {
        Ok(r) => r,
        Err(e) => {
            let rs = RerankSpec::from_policy(p);
            note_tool_failure(
                &mut report,
                tool_failure_from("rerank", &rs.provider, &rs.version, &e, "rebuild-memory"),
            );
            return Err(e); // pinned reranker must exist too
        }
    };
    // BC-P2-30: the executed components (adapter, model artefact, inference runtime) are identified and bound
    let emb_identity = crate::memory::profile::embedder_identity(p, &embed, None);
    let rr_identity = crate::memory::profile::reranker_identity(p, reranker.as_ref(), None);
    let emb_pin = crate::memory::profile::embedder_pin(&spec, &emb_identity);
    let rr_pin = crate::memory::profile::reranker_pin(reranker.as_ref(), &rr_identity);
    let expected = json!({"embedder": emb_pin, "reranker": RerankSpec::from_policy(p).to_value(), "chunking": chunking_config(p), "lexical": lexical_config(p), "index_version": INDEX_VERSION});
    // --- decide mode: incremental only when the live pins match; otherwise escalate to a full rebuild
    let mut incremental = opts.incremental && !benchmark_mode;
    if incremental {
        if final_db.exists() {
            let live = RuntimeDb::open(&final_db)?;
            if !live.has_schema() {
                incremental = false;
                report.escalated_to_full = Some("runtime database has no schema".into());
            } else {
                let mut diffs = pin_differences(&expected, &live_pins(&live));
                // the runtime's bytes are machine-local: bound through runtime meta, not the manifest core
                let live_rt = live
                    .get_meta("embedder_identity")
                    .and_then(|v| v["runtime_digest"].as_str().map(|s| s.to_string()));
                if live_rt.as_deref() != Some(emb_identity.runtime_digest.as_str()) {
                    diffs.push(format!(
                        "embedding runtime: {} changed or unrecorded",
                        emb_identity.runtime["id"].as_str().unwrap_or("?")
                    ));
                }
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
    // the index as it stood before this build: the basis of an incremental build, and of the mutation this build
    // observes (R2-11) in either mode
    let before = if benchmark_mode {
        None
    } else {
        read_index_manifest(p)
    };
    let prev = if incremental { before.clone() } else { None };
    let prev_arts: BTreeMap<String, Value> = prev
        .as_ref()
        .and_then(|m| m.get("artifacts"))
        .and_then(|a| a.as_object())
        .map(|o| o.iter().map(|(k, v)| (k.clone(), v.clone())).collect())
        .unwrap_or_default();
    // content-level exclusions of the previous build (secret content, duplicate id), valid while content and
    // derivation key are unchanged
    let prev_excluded: BTreeMap<String, Value> = prev
        .as_ref()
        .and_then(|m| m.get("excluded"))
        .and_then(|a| a.as_array())
        .map(|a| {
            a.iter()
                .filter(|e| CONTENT_EXCLUSIONS.contains(&e["reason"].as_str().unwrap_or("")))
                .filter_map(|e| e["path"].as_str().map(|s| (s.to_string(), e.clone())))
                .collect()
        })
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
    let derive = DerivationContext::new(p, &plugins);
    let repo_commit = p.git_commit();
    let now = now_iso();
    let files = iter_repo_files(&p.root, false);
    let file_set: HashSet<&str> = files.iter().map(|(_, r)| r.as_str()).collect();
    let resolver = ImportResolver::new(&p.root, &files, &product_roots);
    // the record store research/experiment standing is read against (IP-WS10-05), loaded only when needed
    let evidence_store: std::cell::OnceCell<crate::records::RecordStore> =
        std::cell::OnceCell::new();
    // declared code-intelligence adapters the acting role may not execute (WS-7 IP-W7-2)
    let refused_adapters = refused_code_intel(&governed);
    let mut languages_seen: BTreeSet<String> = BTreeSet::new();
    // --- which file the index holds for each record id: ranked over the whole tree before anything is written, so
    // the choice is a function of the tree (a full and an incremental build agree, BC-P2-29) and equals the record
    // store's. Content the previous build derived under the same derivation key is not re-read for its id (the
    // manifest records it); everything else is scanned and parsed once here and reused by the loop below.
    let mut claims: HashMap<String, Option<String>> = HashMap::new();
    let mut scanned: HashMap<String, PreScan> = HashMap::new();
    let mut holder: HashMap<String, ((u8, u8, usize), String)> = HashMap::new();
    for (walk_index, (abs, rel)) in files.iter().enumerate() {
        if !record_like(rel) {
            continue;
        }
        let d = contract.decide(rel);
        let Admission::Candidate { text, .. } = admit(abs, rel, &d, scanner) else {
            continue;
        };
        let hash = sha256_hex(text.as_bytes());
        let dkey = derive.key(&d, rel);
        let same = |e: &Value| {
            e.get("content_hash").and_then(|v| v.as_str()) == Some(hash.as_str())
                && e.get("derivation").and_then(|v| v.as_str()) == Some(dkey.as_str())
        };
        let reused: Option<Option<String>> = if let Some(e) = prev_arts.get(rel).filter(|e| same(e))
        {
            Some(
                e.get("record_type")
                    .and_then(|v| v.as_str())
                    .filter(|t| *t != "file")
                    .and_then(|_| e.get("artifact_id").and_then(|v| v.as_str()))
                    .map(String::from),
            )
        } else {
            prev_excluded.get(rel).filter(|x| same(x)).map(|x| {
                if x["reason"] == "duplicate_id" {
                    x["id"].as_str().map(String::from)
                } else {
                    None
                }
            })
        };
        let id = match reused {
            Some(id) => id,
            None => {
                let hits = scanner.scan_text(&text, rel);
                let record = if hits.is_empty() {
                    parse_record_text(&text, rel)
                        .filter(|r| !r.id().is_empty() && !r.rtype().is_empty())
                } else {
                    None
                };
                let id = record.as_ref().map(|r| r.id());
                scanned.insert(
                    rel.clone(),
                    PreScan {
                        hash: hash.clone(),
                        hits,
                        record,
                    },
                );
                id
            }
        };
        if let Some(id) = &id {
            let rank = record_rank(rel, walk_index);
            if holder.get(id).map(|(r, _)| rank < *r).unwrap_or(true) {
                holder.insert(id.clone(), (rank, rel.clone()));
            }
        }
        claims.insert(rel.clone(), id);
    }
    let mut seen_paths: HashSet<String> = HashSet::new();
    let mut excluded_now: HashSet<String> = HashSet::new();
    let mut pending_vectors: Vec<(String, String, String)> = vec![];
    let mut coverage = CoverageTally::default();
    let mut adapter_failures = AdapterFailures::default();
    let mut in_batch = 0usize;
    // record an exclusion (with what decided it) and drop whatever the index held for the path
    let exclude = |db: &RuntimeDb, rel: &str, reason: &str, detail: Value| -> Result<()> {
        db.exec(
            "INSERT OR REPLACE INTO excluded(path, reason, detail) VALUES (?1,?2,?3)",
            &[&rel, &reason, &detail.to_string()],
        )?;
        if let Some(a) = db.artifact_by_path(rel)? {
            db.delete_artifact(a["artifact_id"].as_str().unwrap_or(""))?;
        }
        Ok(())
    };
    db.begin()?;
    for (abs, rel) in &files {
        let d = contract.decide(rel);
        let text = match admit(abs, rel, &d, scanner) {
            Admission::Outside(reason) => {
                if let Some(r) = reason {
                    report.excluded.push(json!({"path": rel, "reason": r}));
                }
                continue;
            }
            Admission::PathExcluded { reason, rule } => {
                report.excluded.push(json!({"path": rel, "reason": reason}));
                excluded_now.insert(rel.clone());
                exclude(&db, rel, &reason, json!({"rule": rule}))?;
                continue;
            }
            Admission::FileExcluded { reason, size } => {
                // not read into the index; an artefact it had is removed with the unseen ones below
                report
                    .excluded
                    .push(json!({"path": rel, "reason": reason, "size": size}));
                if reason != "binary" {
                    excluded_now.insert(rel.clone());
                    db.exec(
                        "INSERT OR REPLACE INTO excluded(path, reason, detail) VALUES (?1,?2,?3)",
                        &[rel, &reason, &json!({"size": size}).to_string()],
                    )?;
                }
                continue;
            }
            Admission::Candidate { text, .. } => text,
        };
        let size = text.len();
        let hash = sha256_hex(text.as_bytes());
        let dkey = derive.key(&d, rel);
        let ext = Path::new(rel)
            .extension()
            .map(|e| e.to_string_lossy().to_lowercase())
            .unwrap_or_default();
        let language = ecosystems::language_for_ext(&ext);
        if let (true, Some(lang)) = (d.flag("code_index"), language) {
            languages_seen.insert(lang.to_string());
        }
        // --- a record id the index holds at another path: this occurrence is a duplicate (the held one is named)
        if let Some(Some(id)) = claims.get(rel) {
            if let Some((_, kept)) = holder.get(id).filter(|(_, k)| k != rel) {
                report.problems.push(format!(
                    "duplicate record id {id} at {rel} (the index holds {kept})"
                ));
                report
                    .excluded
                    .push(json!({"path": rel, "reason": "duplicate_id", "id": id, "kept": kept}));
                excluded_now.insert(rel.clone());
                exclude(
                    &db,
                    rel,
                    "duplicate_id",
                    json!({"content_hash": hash, "derivation": dkey, "id": id, "kept": kept}),
                )?;
                continue;
            }
        }
        // --- unchanged since the previous build: content, derivation key and, for research/experiment records, the
        // standing the index holds them under (the secret-scanning rules are part of the key)
        if incremental {
            if let Some(prev_e) = prev_arts.get(rel) {
                let same_content =
                    prev_e.get("content_hash").and_then(|v| v.as_str()) == Some(hash.as_str());
                let same_derivation =
                    prev_e.get("derivation").and_then(|v| v.as_str()) == Some(dkey.as_str());
                if same_content
                    && same_derivation
                    && recorded_state_class_holds(
                        p,
                        &evidence_store,
                        prev_e,
                        rel,
                        &text,
                        &d.class(),
                    )
                {
                    seen_paths.insert(rel.clone());
                    report.unchanged += 1;
                    continue;
                }
                if same_content {
                    report.rederived.push(rel.clone());
                }
            }
            if let Some(a) = db.artifact_by_path(rel)? {
                db.delete_artifact(a["artifact_id"].as_str().unwrap_or(""))?;
            }
        }
        // --- secret content is never indexed (fail closed); the exclusion holds while content and key are unchanged
        let pre = scanned.remove(rel).filter(|s| s.hash == hash);
        let hits = match &pre {
            Some(s) => s.hits.clone(),
            None => scanner.scan_text(&text, rel),
        };
        if !hits.is_empty() {
            let ids: Vec<String> = hits
                .iter()
                .map(|h| h.pattern_id.clone())
                .collect::<BTreeSet<_>>()
                .into_iter()
                .collect();
            report
                .excluded
                .push(json!({"path": rel, "reason": "secret_content", "patterns": ids}));
            report.secret_blocked.push(json!({"path": rel, "patterns": ids, "lines": hits.iter().map(|h| h.line).collect::<Vec<_>>()}));
            excluded_now.insert(rel.clone());
            exclude(
                &db,
                rel,
                "secret_content",
                json!({"content_hash": hash, "derivation": dkey, "patterns": ids}),
            )?;
            continue;
        }
        seen_paths.insert(rel.clone());
        let record = if record_like(rel) {
            match pre {
                Some(s) => s.record,
                None => parse_record_text(&text, rel),
            }
        } else {
            None
        };
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
        let mut sym_refs: Vec<(String, String, String, usize)> = vec![];
        let mut provider = String::new();
        let (lex, sem, gr, code) = (
            d.flag("lexical_index"),
            d.flag("semantic_index"),
            d.flag("graph_index"),
            d.flag("code_index"),
        );
        match record {
            Some(r) if !r.id().is_empty() && !r.rtype().is_empty() => {
                let id = r.id();
                // the file changed after the ranking and now claims an id another file holds
                if let Some((_, kept)) = holder.get(&id).filter(|(_, k)| k != rel) {
                    report.problems.push(format!(
                        "duplicate record id {id} at {rel} (the index holds {kept})"
                    ));
                    report.excluded.push(
                        json!({"path": rel, "reason": "duplicate_id", "id": id, "kept": kept}),
                    );
                    seen_paths.remove(rel);
                    excluded_now.insert(rel.clone());
                    exclude(
                        &db,
                        rel,
                        "duplicate_id",
                        json!({"content_hash": hash, "derivation": dkey, "id": id, "kept": kept}),
                    )?;
                    continue;
                }
                if incremental {
                    if let Some(a) = db.artifact(&id)? {
                        let old_path = a["path"].as_str().unwrap_or("").to_string();
                        if old_path != *rel {
                            // the id's artefact lives at another path: a relocation (git mv / rename) when that path
                            // is gone — the record keeps its identity and provenance at the new path — or an
                            // occurrence this one now outranks (excluded where it is walked)
                            db.delete_artifact(&id)?;
                            if !file_set.contains(old_path.as_str()) {
                                report
                                    .moved
                                    .push(json!({"artifact_id": id, "from": old_path, "to": rel}));
                            }
                        }
                    }
                }
                artifact_id = id.clone();
                record_type = r.rtype();
                title = r.title();
                status = if d.class() == "historical" && r.status() == "ACTIVE" {
                    "HISTORICAL".into()
                } else {
                    r.status()
                };
                state_class = record_state_class(p, &evidence_store, &r, &d.class(), &authority);
                data_json = serde_json::to_string(&r.data)?;
                // BC-P2-25: every content field — list-valued and nested ones included — is a named section
                let sections = r.text_sections();
                let body = if r.body.is_empty() {
                    r.get("body")
                } else {
                    r.body.clone()
                };
                chunks = chunk_record(&title, &sections, &body, max_chars, overlap);
                let body_lines = without_heading_markers(&body);
                let expected: String = sections
                    .iter()
                    .map(|(_, t)| t.as_str())
                    .chain(std::iter::once(body_lines.as_str()))
                    .collect::<Vec<_>>()
                    .join("\n");
                coverage.check(rel, &expected, &chunks, max_chars, true);
                for (t, target) in r.relations() {
                    edges.push((id.clone(), t.clone(), target.clone()));
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
                    "source" | "test" | "devops" | "tooling" | "evidence" => "EVIDENCE",
                    "historical" => "HISTORICAL",
                    "generated" | "derived" => "DERIVED",
                    "authoritative" => "AUTHORITATIVE",
                    _ => "NARRATIVE",
                }
                .into();
                data_json = "{}".into();
                superseded_by = None;
                if let (true, Some(lang)) = (code, language) {
                    // a declared adapter for this language that may not run: the built-in extractor analyses the
                    // file, and that is a recorded degradation (D-0005; WS-7 IP-W7-2), never a silent fallback
                    if !refused_adapters.is_empty()
                        && crate::capabilities::host::find(&plugins, "code_intel", Some(lang), None)
                            .is_none()
                    {
                        for a in refused_adapters.iter().filter(|a| a.covers(lang)) {
                            report.degradations.push(format!(
                                "{rel}: code_intel plugin {} refused ({}); built-in extractor used",
                                a.plugin_id, a.code
                            ));
                            let e = adapter_failures
                                .by_key
                                .entry((a.plugin_id.clone(), a.version.clone(), a.code.clone()))
                                .or_insert((a.failure_message(), vec![]));
                            e.1.push(rel.clone());
                        }
                    }
                    let facts = code_intelligence::analyze(rel, lang, &text, &plugins, &p.root);
                    provider = facts.provider.clone();
                    if let Some(dg) = &facts.degraded {
                        report.degradations.push(format!("{rel}: {dg}"));
                        if let Some(desc) = crate::capabilities::host::find(
                            &plugins,
                            "code_intel",
                            Some(lang),
                            None,
                        ) {
                            let code = dg
                                .split_once('(')
                                .and_then(|(_, r)| r.split_once(')'))
                                .map(|(c, _)| c.to_string())
                                .unwrap_or_else(|| "PLUGIN_UNUSABLE_OUTPUT".into());
                            let e = adapter_failures
                                .by_key
                                .entry((desc.plugin_id.clone(), desc.version.clone(), code))
                                .or_insert((dg.clone(), vec![]));
                            e.1.push(rel.clone());
                        }
                    }
                    chunks = chunk_code(rel, &text, &chunk_units(&facts), max_chars, overlap);
                    coverage.check(rel, &text, &chunks, max_chars, false);
                    symbols = facts.symbols.clone();
                    for rt in &facts.routes {
                        symbols.push(code_intelligence::Symbol {
                            name: rt.path.clone(),
                            qualname: format!("route:{} {}", rt.method, rt.path),
                            kind: "route".into(),
                            lineno: rt.lineno,
                            end_lineno: rt.lineno,
                            parent: rt.handler.clone(),
                            signature: format!(
                                "{} {} -> {}",
                                rt.method,
                                rt.path,
                                rt.handler.clone().unwrap_or_else(|| "<inline>".into())
                            ),
                        });
                        sym_refs.push((
                            rt.path.clone(),
                            "route".into(),
                            rt.handler.clone().unwrap_or_default(),
                            rt.lineno,
                        ));
                    }
                    for m in &facts.models {
                        symbols.push(code_intelligence::Symbol {
                            name: m.name.clone(),
                            qualname: format!("db_model:{}", m.qualname),
                            kind: "db_model".into(),
                            lineno: m.lineno,
                            end_lineno: m.lineno,
                            parent: Some(m.qualname.clone()),
                            signature: format!(
                                "table={} evidence={}",
                                m.table.clone().unwrap_or_default(),
                                m.evidence
                            ),
                        });
                    }
                    for rel_ in &facts.relations {
                        sym_refs.push((
                            rel_.name.clone(),
                            rel_.kind.clone(),
                            format!("symbol:{}", rel_.from),
                            rel_.lineno,
                        ));
                    }
                    for imp in &facts.imports {
                        // resolved over the whole tree by `derive_cross_artifact_facts`
                        sym_refs.push((imp.clone(), "import".into(), format!("module:{imp}"), 0));
                    }
                    for (from, name) in &facts.calls {
                        sym_refs.push((name.clone(), "call".into(), from.clone(), 0));
                    }
                } else if ext == "md" || ext == "txt" || ext == "rst" {
                    chunks =
                        crate::memory::chunking::chunk_markdown(rel, &text, max_chars, overlap);
                    coverage.check(
                        rel,
                        &without_heading_markers(&text),
                        &chunks,
                        max_chars,
                        true,
                    );
                } else {
                    chunks = chunk_plain(rel, &text, max_chars, overlap);
                }
            }
        }
        db.exec("INSERT OR REPLACE INTO artifacts(artifact_id, path, record_type, title, status, state_class, namespace, sensitivity, path_class, content_hash, repo_commit, index_version, size, indexed_at, data_json, semantic, lexical, graph, code, default_retrieval, superseded_by) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,?16,?17,?18,?19,?20,?21)",
            &[&artifact_id, rel, &record_type, &title, &status, &state_class, &d.namespace(), &d.sensitivity(), &d.class(), &hash, &repo_commit, &INDEX_VERSION, &(size as i64), &now, &data_json, &(sem as i64), &(lex as i64), &(gr as i64), &(code as i64), &(d.default_retrieval() as i64), &superseded_by])?;
        db.exec(
            "INSERT OR REPLACE INTO derivation(path, artifact_id, key) VALUES (?1,?2,?3)",
            &[rel, &artifact_id, &dkey],
        )?;
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
        for (name, kind, target, lineno) in &sym_refs {
            db.exec(
                "INSERT INTO symbol_refs(path, name, kind, lineno, target) VALUES (?1,?2,?3,?4,?5)",
                &[rel, name, kind, &(*lineno as i64), target],
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
    // a refused adapter is a standing degradation of every build while files of its languages exist, whether or
    // not this build re-analysed one of them (WS-7 IP-W7-2)
    for a in &refused_adapters {
        let langs: Vec<&String> = languages_seen
            .iter()
            .filter(|l| {
                a.covers(l)
                    && crate::capabilities::host::find(&plugins, "code_intel", Some(l), None)
                        .is_none()
            })
            .collect();
        if langs.is_empty() {
            continue;
        }
        report.degradations.push(format!(
            "code_intel plugin {} v{} refused ({}): {} files are analysed by the built-in extractor (D-0005)",
            a.plugin_id,
            a.version,
            a.code,
            langs
                .iter()
                .map(|l| l.as_str())
                .collect::<Vec<_>>()
                .join(", ")
        ));
        adapter_failures
            .by_key
            .entry((a.plugin_id.clone(), a.version.clone(), a.code.clone()))
            .or_insert((a.failure_message(), vec![]));
    }
    if incremental {
        // artefacts no longer part of the index (deleted, reclassified out of every index, now binary/too large)
        for a in db.query("SELECT artifact_id, path FROM artifacts", &[])? {
            let path = a["path"].as_str().unwrap_or("").to_string();
            if !seen_paths.contains(&path) {
                db.delete_artifact(a["artifact_id"].as_str().unwrap_or(""))?;
                report.removed += 1;
            }
        }
        // exclusions that no longer apply
        for e in db.query("SELECT path FROM excluded", &[])? {
            let path = e["path"].as_str().unwrap_or("").to_string();
            if !excluded_now.contains(&path) {
                db.exec("DELETE FROM excluded WHERE path=?1", &[&path])?;
            }
        }
        db.exec(
            "DELETE FROM derivation WHERE path NOT IN (SELECT path FROM artifacts)",
            &[],
        )?;
    }
    derive_cross_artifact_facts(&db, p, &resolver, &mut report)?;
    db.commit()?;
    report.coverage = coverage.to_value();
    if coverage.uncovered > 0 {
        report.problems.push(format!(
            "INDEX_COVERAGE_GAP: {} non-empty line(s) of {} artefact(s) are held by no chunk",
            coverage.uncovered,
            coverage.gaps.len()
        ));
    }
    // --- vectors with the pinned embedder (errors abort the build; no fallback)
    let emb_spec = embed.spec();
    db.begin()?;
    for batch in pending_vectors.chunks(256) {
        let texts: Vec<String> = batch.iter().map(|(_, _, t)| t.clone()).collect();
        let vecs = match embed.embed_batch(&texts, &p.root) {
            Ok(v) => v,
            Err(e) => {
                if !incremental {
                    let _ = std::fs::remove_file(&build_path);
                }
                note_tool_failure(
                    &mut report,
                    tool_failure_from(
                        "embed",
                        &emb_spec.id,
                        &emb_spec.version,
                        &e,
                        "rebuild-memory",
                    ),
                );
                return Err(e);
            }
        };
        for ((chunk_id, artifact_id, _), v) in batch.iter().zip(vecs) {
            db.conn.execute("INSERT OR REPLACE INTO vectors(chunk_id, artifact_id, embedder, dim, vec) VALUES (?1,?2,?3,?4,?5)", params![chunk_id, artifact_id, emb_spec.id, v.len() as i64, serde_json::to_string(&v)?])?;
        }
    }
    db.commit()?;
    // --- pins (with the executed component identity, BC-P2-30) + capability memory
    db.set_meta("embedder", &emb_pin)?;
    db.set_meta("embedder_identity", &emb_identity.to_record())?;
    db.set_meta("reranker", &rr_pin)?;
    db.set_meta("reranker_identity", &rr_identity.to_record())?;
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
    db.set_meta("index_coverage", &report.coverage)?;
    if !benchmark_mode {
        // BC-P2-28: graph integrity of what was just built, raised as findings (G1-equivalent)
        let store = crate::records::RecordStore::load(&p.root);
        let gi = crate::memory::integrity::check(p, &store, Some(&db))?;
        db.set_meta("graph_integrity", &gi.summary(200))?;
        report.graph_integrity = gi.summary(20);
        // BC-P2-30: is the profile this build used governed (kernel pin or a profile decision)?
        report.retrieval_profile = crate::memory::profile::governance_in(
            p,
            &store,
            &crate::memory::profile::Profile::of(emb_pin.clone(), rr_pin.clone()),
        );
        db.set_meta("retrieval_profile", &report.retrieval_profile)?;
        // BC-P2-31: non-rebuildable OS state still kept where the derived runtime directory is rebuilt
        report.os_state = crate::paths::misplaced_os_state(&p.root);
    }
    let excluded_all = db.query(
        "SELECT path, reason, detail FROM excluded ORDER BY path",
        &[],
    )?;
    let mut manifest = build_index_manifest(
        p,
        &db,
        &emb_pin,
        &chunking,
        &excluded_all,
        &lexical_config(p),
        &rr_pin,
    )?;
    // outside the hashed core: the machine-local runtime bytes and the governance state
    manifest["components"] = json!({"embedder": emb_identity.manifest_value(), "reranker": rr_identity.manifest_value()});
    manifest["retrieval_profile"] = json!({"digest": crate::memory::profile::Profile::of(emb_pin.clone(), rr_pin.clone()).digest,
        "state": report.retrieval_profile.get("state"), "decision": report.retrieval_profile.get("decision")});
    let manifest = crate::util::sorted(&manifest);
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
    report.embedder = emb_pin.clone();
    report.reranker = rr_pin.clone();
    report.ecosystems = eco;
    // --- failure memory: adapter failures observed by this build (BC-P2-32); a new record is indexed at once
    if record_failures {
        let mut recorded_new = false;
        for ((plugin_id, version, code), (message, paths)) in &adapter_failures.by_key {
            let mut t = crate::memory::failures::ToolFailure {
                tool_kind: "code_intel".into(),
                tool_id: plugin_id.clone(),
                version: version.clone(),
                code: code.clone(),
                message: message.clone(),
                operation: "rebuild-memory".into(),
                affected: paths.clone(),
            };
            t.affected.truncate(10);
            let o = crate::memory::failures::record_tool_failure(p, &t, false);
            recorded_new |= o.status == "recorded";
            report.failures.push(o.to_value());
        }
        if recorded_new {
            let again = rebuild(
                p_in,
                IndexOptions {
                    incremental: true,
                    record_failures: Some(false),
                    ..Default::default()
                },
            )?;
            report.indexed += again.indexed;
            report.manifest_hash = again.manifest_hash;
            report.counts = again.counts;
        }
    }
    // --- R2-11: a significant mutation this build observed is a checkpoint boundary (for the builds a host runs as
    // an operation of its own; see `IndexOptions::observe_boundaries`)
    if opts.observe_boundaries && !benchmark_mode {
        if let Some(before) = &before {
            let after = read_index_manifest(p).unwrap_or(Value::Null);
            report.boundaries = observe_significant_mutation(p, &final_db, before, &after);
            if let Some(h) = report.boundaries["manifest_hash_after"].as_str() {
                report.manifest_hash = h.to_string();
            }
            if let Some(e) = report.boundaries.get("error") {
                report.problems.push(format!(
                    "CHECKPOINT_NOT_WRITTEN: a significant mutation was observed but its checkpoint could not be written ({}: {})",
                    e["code"].as_str().unwrap_or("?"),
                    e["message"].as_str().unwrap_or("")
                ));
            }
        }
    }
    report.duration_ms = started.elapsed().as_millis();
    let _ = PluginDescriptor::from_value(&Value::Null, "");
    Ok(report)
}

/// The artefacts an index build added, changed (content hash) or removed relative to the index before it, by path.
/// A re-derivation of unchanged content is not a mutation of the repository and is not counted.
pub fn content_changes(before: &Value, after: &Value) -> Vec<String> {
    let empty = serde_json::Map::new();
    let b = before["artifacts"].as_object().unwrap_or(&empty);
    let a = after["artifacts"].as_object().unwrap_or(&empty);
    let hash = |e: &Value| e["content_hash"].as_str().unwrap_or("").to_string();
    let mut out: Vec<String> = a
        .iter()
        .filter(|(k, e)| b.get(*k).map(|x| hash(x) != hash(e)).unwrap_or(true))
        .map(|(k, _)| k.clone())
        .collect();
    out.extend(b.keys().filter(|k| !a.contains_key(*k)).cloned());
    out.sort();
    out
}

/// R2-11: turn a significant mutation the build observed into a checkpoint boundary (see
/// [`IndexOptions::observe_boundaries`]). The next action is carried forward from the latest checkpoint (the
/// product observed the boundary; it does not know a new plan). Never fails the build: a checkpoint that cannot be
/// written (authority, emergency control) is reported with its typed error.
fn observe_significant_mutation(
    p: &Project,
    db_path: &Path,
    before: &Value,
    after: &Value,
) -> Value {
    let changed = content_changes(before, after);
    let threshold = p
        .policies()
        .get_i64(
            "CHECKPOINT_POLICY",
            "watchdog.max_operations_between_checkpoints",
            25,
        )
        .max(1) as usize;
    let significant = changed.len() >= threshold;
    let mut out = json!({"significant_mutation": significant, "changed_artifacts": changed.len(),
        "threshold": threshold, "policy": "CHECKPOINT_POLICY.watchdog.max_operations_between_checkpoints", "checkpoints": []});
    if !significant {
        return out;
    }
    let err = |e: &GovError| json!({"code": e.code, "message": e.message});
    let db = match RuntimeDb::open(db_path) {
        Ok(d) => d,
        Err(e) => {
            out["error"] = err(&e);
            return out;
        }
    };
    let next_action = crate::checkpoints::latest(p)
        .and_then(|c| c["next_action"].as_str().map(String::from))
        .filter(|s| !s.trim().is_empty())
        .unwrap_or_else(|| {
            "review the significant mutation observed at the index rebuild and continue the current work".into()
        });
    let detail = json!({"changed_artifacts": changed.len(), "threshold": threshold, "observed_by": "index rebuild",
        "examples": changed.iter().take(10).collect::<Vec<_>>()});
    let mut written: Vec<Value> = vec![];
    match crate::checkpoints::observe_boundaries(p, &db, &next_action) {
        Ok(v) => written.extend(v),
        Err(e) => out["error"] = err(&e),
    }
    if out.get("error").is_none()
        && !written
            .iter()
            .any(|c| c["trigger"] == "significant_mutation")
    {
        let fields = json!({"trigger": "significant_mutation", "next_action": next_action,
            "last_completed_step": format!("observed boundary: significant_mutation ({} artefact(s) added, changed or removed since the previous index build; threshold {threshold})", changed.len()),
            "observed_boundary": {"trigger": "significant_mutation", "detail": detail}});
        match crate::checkpoints::create(p, &db, fields) {
            Ok(c) => written.push(
                json!({"checkpoint": c["id"], "trigger": "significant_mutation", "detail": detail}),
            ),
            Err(e) => out["error"] = err(&e),
        }
    }
    out["checkpoints"] = json!(written);
    // a checkpoint brings the index current again (`checkpoints::create`): report the index as it now stands
    out["manifest_hash_after"] = read_index_manifest(p)
        .and_then(|m| m.get("manifest_hash").cloned())
        .unwrap_or(Value::Null);
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    /// R2-10: the admission freshness and the indexer share — every skip reason is decided from the file itself, the
    /// same way for both; a candidate carries its text.
    #[test]
    fn admission_decides_every_skip_reason_from_the_file() {
        let dir = std::env::temp_dir().join(format!("gov-admit-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(dir.join("product")).unwrap();
        let c = crate::paths::RepositoryContract::new(json!({"paths": [
            {"pattern": "product/**", "class": "source"},
            {"pattern": "product/secrets/**", "class": "secret"},
            {"pattern": "product/quiet/**", "class": "derived"}]}));
        let scanner = crate::security::secrets::SecretScanner::default_scanner();
        let put = |rel: &str, bytes: &[u8]| {
            let p = dir.join(rel);
            std::fs::create_dir_all(p.parent().unwrap()).unwrap();
            std::fs::write(&p, bytes).unwrap();
            p
        };
        let cases: Vec<(&str, Vec<u8>, &str)> = vec![
            ("product/a.txt", b"plain text\n".to_vec(), "candidate"),
            ("product/latin1.txt", b"caf\xe9\n".to_vec(), "not_utf8"),
            ("product/img.bin", b"\x89PNG\x00\x01".to_vec(), "binary"),
            (
                "product/big.txt",
                "y".repeat(MAX_INDEXED_FILE_BYTES as usize + 1).into_bytes(),
                "too_large",
            ),
            ("product/secrets/k.txt", b"k\n".to_vec(), "secret_class"),
            ("product/quiet/x.txt", b"x\n".to_vec(), "outside"),
            (
                "spec/reports/memory-quality/FAIL-1.yaml",
                b"id: FAIL-1\n".to_vec(),
                "memory_quality_event",
            ),
        ];
        for (rel, bytes, want) in cases {
            let abs = put(rel, &bytes);
            let got = match admit(&abs, rel, &c.decide(rel), &scanner) {
                Admission::Candidate { text, .. } => {
                    assert_eq!(text.as_bytes(), &bytes[..]);
                    "candidate".to_string()
                }
                Admission::FileExcluded { reason, .. } => reason.to_string(),
                Admission::PathExcluded { reason, .. } => reason,
                Admission::Outside(Some(r)) => r.to_string(),
                Admission::Outside(None) => "outside".to_string(),
            };
            assert_eq!(got, want, "{rel}");
        }
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// The occurrence the index holds for a record id is the one the record store resolves it to, whatever the
    /// order files were met in; the mutation a build observes counts content changes only.
    #[test]
    fn record_rank_follows_the_record_store_and_changes_count_content_only() {
        let mut ranked = [
            ("archive/REQ-1.yaml", 0),
            ("governance/project/x/REQ-1.yaml", 1),
            ("docs/REQ-1.md", 2),
            ("spec/z/REQ-1.yaml", 4),
            ("spec/a/REQ-1.yaml", 3),
        ]
        .iter()
        .map(|(p, i)| (record_rank(p, *i), p.to_string()))
        .collect::<Vec<_>>();
        ranked.sort();
        let order: Vec<&str> = ranked.iter().map(|(_, p)| p.as_str()).collect();
        assert_eq!(
            order,
            vec![
                "spec/a/REQ-1.yaml",
                "spec/z/REQ-1.yaml",
                "governance/project/x/REQ-1.yaml",
                "docs/REQ-1.md",
                "archive/REQ-1.yaml"
            ]
        );
        let before = json!({"artifacts": {"a": {"content_hash": "1", "derivation": "k"}, "b": {"content_hash": "2"}, "c": {"content_hash": "3"}}});
        let after = json!({"artifacts": {"a": {"content_hash": "1", "derivation": "k2"}, "b": {"content_hash": "9"}, "d": {"content_hash": "4"}}});
        assert_eq!(content_changes(&before, &after), vec!["b", "c", "d"]);
    }

    #[test]
    fn test_paths_by_convention() {
        for t in [
            "tests/test_models.py",
            "src/app/test_colocated.py",
            "pkg/server_test.go",
            "web/format.test.ts",
            "web/__tests__/x.js",
            "src/OrderTest.java",
            "spec/models/order_spec.rb",
        ] {
            assert!(is_test_path(t), "{t}");
        }
        for f in [
            "src/app/models.py",
            "src/latest.py",
            "docs/testing-guide.md",
            "src/contest.go",
            "Test.java",
        ] {
            assert!(!is_test_path(f), "{f}");
        }
    }

    #[test]
    fn import_resolution_covers_src_layouts_and_crates() {
        let files: Vec<(PathBuf, String)> = [
            "src/app/__init__.py",
            "src/app/models.py",
            "tests/test_models.py",
            "lib/other/app/models.py",
            "crates/ledger/src/lib.rs",
            "crates/ledger/src/entries.rs",
            "crates/ledger/tests/it.rs",
            "srv/a.go",
            "srv/b.go",
            "srv/a_test.go",
        ]
        .iter()
        .map(|r| (PathBuf::from(format!("/nonexistent/{r}")), r.to_string()))
        .collect();
        let mut r = ImportResolver::new(Path::new("/nonexistent"), &files, &[]);
        r.rust_crates
            .push(("ledger".into(), "crates/ledger".into()));
        r.files.insert("crates/ledger/Cargo.toml".into());
        assert_eq!(
            r.resolve("tests/test_models.py", "python", "app.models")
                .as_deref(),
            Some("src/app/models.py")
        );
        assert_eq!(
            r.resolve("src/app/__init__.py", "python", ".models")
                .as_deref(),
            Some("src/app/models.py")
        );
        assert_eq!(
            r.resolve("crates/ledger/tests/it.rs", "rust", "ledger::entries::sum")
                .as_deref(),
            Some("crates/ledger/src/entries.rs")
        );
        assert_eq!(
            r.resolve("crates/ledger/src/lib.rs", "rust", "crate::entries")
                .as_deref(),
            Some("crates/ledger/src/entries.rs")
        );
        assert_eq!(
            r.go_package_files("srv/a_test.go"),
            vec!["srv/a.go".to_string(), "srv/b.go".to_string()]
        );
        assert!(r
            .resolve("tests/test_models.py", "python", "flask")
            .is_none());
    }
}
