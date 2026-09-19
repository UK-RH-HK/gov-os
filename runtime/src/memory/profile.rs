//! Retrieval-profile component identity and change governance (BC-P2-30).
//!
//! Framework §14.2: the framework must distinguish the **embedding model** (what creates the vectors), the
//! **inference runtime** that executes it, the vector store and the **reranker**. §14.3: "The chosen embedding and
//! reranker versions are pinned in the memory/index manifest and may be changed only through a measured migration
//! with re-indexing and regression testing." Contract v3 D1 ("Index manifest records compatible component
//! identity"), D4 (embedding model / embedding runtime / reranker "independently identifiable"), D5 ("selected
//! embedder/reranker revisions are pinned; changing them requires governed migration/reindex/regression").
//!
//! ## Component identity (A0-D4-01, A0-D5-01)
//!
//! For the embedder and the reranker the product actually executes, [`embedder_identity`] / [`reranker_identity`]
//! compute three separately identified, content-bound components:
//!
//! | component | built-in embedder | plugin |
//! |---|---|---|
//! | adapter | `hashed-ngram` implementation in this binary | plugin id, executed descriptor revision, descriptor bytes, SHA-256 of every local implementation file |
//! | model artefact | algorithm revision and parameters | SHA-256 of every file shipped beside the implementation (the plugin's own directory or module package: weights, tokenizer, configuration), other plugins' implementations excluded |
//! | inference runtime | in-process | the interpreter or executable the command runs (shebang or `PATH` resolution), content-hashed |
//!
//! Adapter and model are repository content, so their digest ([`ComponentIdentity::digest`]) is portable and is
//! part of the pinned `embedder` value in the index manifest's hashed core: a clone at another path reproduces the
//! manifest hash. The runtime's bytes are machine-specific: its digest ([`ComponentIdentity::runtime_digest`]) is
//! recorded in runtime meta and in the manifest outside the hashed core. Any difference between what the live index
//! recorded and what would execute now fails closed at query time (`EMBEDDER_MISMATCH` / `RERANKER_MISMATCH`, with
//! the changed components named), escalates an incremental build to a full re-embed, and makes `freshness` report a
//! pin mismatch (adapter/model) — a weight file changed behind an unchanged plugin id is never served silently.
//! A descriptor revision that differs from the pinned revision is refused before anything runs
//! (`EMBEDDER_REVISION_MISMATCH`, `RERANKER_REVISION_MISMATCH` — `embedder::Embedder::resolve`).
//!
//! ## Change governance (A0-D5-02)
//!
//! [`select`] is the only governed way to change the profile: it requires T2-bound benchmark evidence for the
//! chosen candidate, measured against the current held-out set and the candidate's current component identity;
//! the change-control gate for its radius (the pins live in `governance/project/**`, so
//! `CHANGE_POLICY.radius_rules.governance_paths_radius`, R5 by default; above
//! `HUMAN_GATE_POLICY.agent_resolvable_when.max_radius` only an owner-signed human answer bound to this exact change
//! authorises it, through `gates::human_approval_for`); a full re-index; and a held-out regression after the
//! re-index, recorded as an evidence audit record. A change whose regression fails (or is unmeasured) is rolled back.
//! The decision it writes asserts only the evidence that was supplied and derives `human_approved` only from the
//! verified human answer (WS-3 IP-8). [`governance`] detects a live profile that no decision pins (a direct overlay
//! edit): state `UNGOVERNED` / `UNGOVERNED_CHANGE`.
use crate::capabilities::governance::{plugin_set, PluginSet};
use crate::capabilities::protocol::PluginDescriptor;
use crate::memory::db::RuntimeDb;
use crate::memory::embedder::{EmbedSpec, Embedder, Reranker, BUILTIN_ID};
use crate::records::{new_record, save_record, Record, RecordStore};
use crate::util::{canonical_json, read_yaml, sha256_file, sha256_hex};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::{Path, PathBuf};

/// Tag carried by every retrieval-profile decision.
pub const PROFILE_TAG: &str = "retrieval-profile";
/// Audit scope of the post-reindex held-out regression a profile change records.
pub const REGRESSION_SCOPE: &str = "retrieval-profile-regression";
/// Subject kind the change-control gate of a profile change binds.
pub const SUBJECT_KIND: &str = "retrieval-profile-change";
/// Gate trigger of a profile change.
pub const TRIGGER: &str = "retrieval_profile_change";
/// Format of the benchmark block of a research record.
pub const BENCHMARK_FORMAT: &str = "retrieval-benchmark/1";

fn h(v: &Value) -> String {
    sha256_hex(canonical_json(v).as_bytes())
}

/// A file whose content an identity binds (with the stat data that lets a later check skip unchanged files).
#[derive(Debug, Clone)]
pub struct FileId {
    /// Portable key: repository-relative path, `external:<name>` or `runtime:<id>`.
    pub key: String,
    pub abs: PathBuf,
    pub size: u64,
    pub mtime_ns: i128,
    pub sha256: String,
}

impl FileId {
    fn to_value(&self) -> Value {
        json!({"key": self.key, "size": self.size, "mtime_ns": self.mtime_ns.to_string(), "sha256": self.sha256})
    }
}

type StatCache = HashMap<String, (u64, String, String)>;

fn stat_cache(recorded: Option<&Value>) -> StatCache {
    let mut m = HashMap::new();
    if let Some(files) = recorded.and_then(|r| r["files"].as_array()) {
        for f in files {
            if let (Some(k), Some(s), Some(t), Some(d)) = (
                f["key"].as_str(),
                f["size"].as_u64(),
                f["mtime_ns"].as_str(),
                f["sha256"].as_str(),
            ) {
                m.insert(k.to_string(), (s, t.to_string(), d.to_string()));
            }
        }
    }
    m
}

/// Hash `abs` under `key`, reusing the recorded digest when size and modification time are unchanged (query-time
/// checks stat the files; builds pass no cache and hash everything).
fn file_id(key: &str, abs: &Path, cache: &StatCache) -> Option<FileId> {
    let md = std::fs::metadata(abs).ok()?;
    if !md.is_file() {
        return None;
    }
    let mtime_ns = md
        .modified()
        .ok()
        .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
        .map(|d| d.as_nanos() as i128)
        .unwrap_or(0);
    let sha256 = match cache.get(key) {
        Some((s, t, d)) if *s == md.len() && *t == mtime_ns.to_string() => d.clone(),
        _ => sha256_file(abs).ok()?,
    };
    Some(FileId {
        key: key.to_string(),
        abs: abs.to_path_buf(),
        size: md.len(),
        mtime_ns,
        sha256,
    })
}

/// The identity of one executed retrieval component (embedder or reranker): adapter, model artefact and inference
/// runtime, each separately identified and content-bound.
#[derive(Debug, Clone)]
pub struct ComponentIdentity {
    pub role: String,
    pub adapter: Value,
    pub model: Value,
    /// Portable runtime identity (`id`, `kind`).
    pub runtime: Value,
    /// Machine-local runtime identity (content hash of the executable, its resolved location).
    pub runtime_observed: Value,
    /// Digest over adapter, model and the portable runtime identity (repository content only).
    pub digest: String,
    /// Digest over the runtime's bytes on this machine.
    pub runtime_digest: String,
    pub files: Vec<FileId>,
}

impl ComponentIdentity {
    fn finish(
        role: &str,
        adapter: Value,
        model: Value,
        runtime: Value,
        runtime_observed: Value,
        files: Vec<FileId>,
    ) -> Self {
        let digest =
            h(&json!({"role": role, "adapter": adapter, "model": model, "runtime": runtime}));
        let runtime_digest = h(&runtime_observed);
        ComponentIdentity {
            role: role.into(),
            adapter,
            model,
            runtime,
            runtime_observed,
            digest,
            runtime_digest,
            files,
        }
    }
    fn model_summary(&self) -> Value {
        let mut m = self.model.clone();
        if let Some(o) = m.as_object_mut() {
            let n = o
                .get("artefacts")
                .and_then(|a| a.as_array())
                .map(|a| a.len())
                .unwrap_or(0);
            o.insert("artefacts".into(), json!(n));
        }
        m
    }
    /// The portable identity carried inside the pinned `embedder`/`reranker` value (index manifest, runtime meta).
    pub fn pin_fields(&self) -> Value {
        json!({"identity": self.digest, "adapter": self.adapter, "model": self.model_summary(), "runtime": self.runtime})
    }
    /// What runtime meta records for the live index: everything, including the stat data of every bound file.
    pub fn to_record(&self) -> Value {
        json!({"role": self.role, "adapter": self.adapter, "model": self.model, "runtime": self.runtime,
               "runtime_observed": self.runtime_observed, "digest": self.digest, "runtime_digest": self.runtime_digest,
               "files": self.files.iter().map(|f| f.to_value()).collect::<Vec<_>>()})
    }
    /// The manifest's (unhashed) component block: no absolute paths, no stat data.
    pub fn manifest_value(&self) -> Value {
        let mut rt = self.runtime.clone();
        rt["sha256"] = self.runtime_observed["sha256"].clone();
        json!({"adapter": self.adapter, "model": self.model, "runtime": rt, "identity": self.digest, "runtime_digest": self.runtime_digest})
    }
    /// Which components differ from a recorded identity ([`Self::to_record`]); empty = identical.
    pub fn differences(&self, recorded: &Value) -> Vec<String> {
        let mut out = vec![];
        if recorded["digest"].as_str() == Some(self.digest.as_str())
            && recorded["runtime_digest"].as_str() == Some(self.runtime_digest.as_str())
        {
            return out;
        }
        if recorded["adapter"] != self.adapter {
            let fields: Vec<String> = [
                ("kind", "kind"),
                ("plugin_id", "plugin id"),
                ("version", "revision"),
                (
                    "descriptor_exec_sha256",
                    "descriptor (command, cwd, languages, permissions)",
                ),
                ("implementation_sha256", "implementation files"),
            ]
            .iter()
            .filter(|(k, _)| recorded["adapter"][*k] != self.adapter[*k])
            .map(|(_, label)| label.to_string())
            .collect();
            out.push(format!(
                "adapter {} ({} changed)",
                short(&self.adapter),
                if fields.is_empty() {
                    "identity".to_string()
                } else {
                    fields.join(", ")
                }
            ));
        }
        if recorded["model"]["sha256"] != self.model["sha256"]
            || recorded["model"]["id"] != self.model["id"]
        {
            let changed: Vec<String> = changed_artefacts(&recorded["model"], &self.model);
            out.push(format!(
                "model artefact {} (content {} -> {}{})",
                self.model["id"].as_str().unwrap_or("?"),
                recorded["model"]["sha256"]
                    .as_str()
                    .map(|s| &s[..s.len().min(12)])
                    .unwrap_or("none"),
                self.model["sha256"]
                    .as_str()
                    .map(|s| &s[..s.len().min(12)])
                    .unwrap_or("none"),
                if changed.is_empty() {
                    String::new()
                } else {
                    format!("; changed: {}", changed.join(", "))
                }
            ));
        }
        if recorded["runtime"] != self.runtime
            || recorded["runtime_digest"].as_str() != Some(self.runtime_digest.as_str())
        {
            out.push(format!(
                "inference runtime {} (content {} -> {})",
                self.runtime["id"].as_str().unwrap_or("?"),
                recorded["runtime_observed"]["sha256"]
                    .as_str()
                    .map(|s| &s[..s.len().min(12)])
                    .unwrap_or("none"),
                self.runtime_observed["sha256"]
                    .as_str()
                    .map(|s| &s[..s.len().min(12)])
                    .unwrap_or("none"),
            ));
        }
        if out.is_empty() {
            out.push("identity".into());
        }
        out
    }
}

fn short(v: &Value) -> String {
    let s = match v {
        Value::Object(o) => format!(
            "{}@{}",
            o.get("plugin_id")
                .or_else(|| o.get("id"))
                .and_then(|x| x.as_str())
                .unwrap_or("?"),
            o.get("version").and_then(|x| x.as_str()).unwrap_or("?")
        ),
        other => other.to_string(),
    };
    s.chars().take(80).collect()
}

fn changed_artefacts(recorded: &Value, now: &Value) -> Vec<String> {
    let index = |v: &Value| -> BTreeMap<String, String> {
        v["artefacts"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|x| {
                        Some((
                            x["path"].as_str()?.to_string(),
                            x["sha256"].as_str().unwrap_or("").to_string(),
                        ))
                    })
                    .collect()
            })
            .unwrap_or_default()
    };
    let (a, b) = (index(recorded), index(now));
    let keys: BTreeSet<&String> = a.keys().chain(b.keys()).collect();
    keys.into_iter()
        .filter(|k| a.get(*k) != b.get(*k))
        .take(5)
        .cloned()
        .collect()
}

// --------------------------------------------------------------------------------------------- identity sources

fn builtin_embedder(spec: &EmbedSpec) -> ComponentIdentity {
    let adapter = json!({"kind": "builtin", "id": BUILTIN_ID, "implementation": "gov-runtime memory::embeddings::HashedNgramEmbedder"});
    let mut model = json!({"id": BUILTIN_ID, "revision": spec.version, "parameters": {"dimensions": spec.dimensions}, "artefacts": [], "declared": true});
    model["sha256"] = json!(h(&model));
    let runtime = json!({"id": "gov-runtime", "kind": "in-process"});
    let observed = json!({"id": "gov-runtime", "kind": "in-process", "algorithm": format!("{BUILTIN_ID}/{}", spec.version), "sha256": null});
    ComponentIdentity::finish("embedder", adapter, model, runtime, observed, vec![])
}

fn no_reranker() -> ComponentIdentity {
    ComponentIdentity::finish(
        "reranker",
        json!({"kind": "none"}),
        json!({"id": "none", "sha256": null}),
        json!({"id": "none", "kind": "none"}),
        json!({"id": "none", "kind": "none", "sha256": null}),
        vec![],
    )
}

fn portable_key(root: &Path, abs: &Path) -> String {
    match abs.strip_prefix(root) {
        Ok(rel) => rel.to_string_lossy().replace('\\', "/"),
        Err(_) => format!(
            "external:{}",
            abs.file_name()
                .map(|n| n.to_string_lossy().to_string())
                .unwrap_or_default()
        ),
    }
}

fn placeholders(desc: &PluginDescriptor, root: &Path, s: &str) -> String {
    let plugin_dir = Path::new(&desc.source)
        .parent()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_default();
    s.replace("{project_root}", &root.to_string_lossy())
        .replace("{plugin_dir}", &plugin_dir)
}

/// Files the command vector names that exist on disk (interpreter scripts, local executables), after placeholder
/// substitution; options (`-x`) after the program are skipped. This is the retrieval-profile identity's view of a
/// plugin's local implementation files (the adapter component). Execution binding — which bytes a plugin may run —
/// is `capabilities::binding::resolve`'s, and is independent of this listing.
fn command_files(desc: &PluginDescriptor, root: &Path) -> Vec<(String, PathBuf)> {
    let mut out = vec![];
    for (i, c) in desc.command.iter().enumerate() {
        let c = placeholders(desc, root, c);
        if i > 0 && c.starts_with('-') {
            continue;
        }
        let cand = if Path::new(&c).is_absolute() {
            PathBuf::from(&c)
        } else {
            root.join(&c)
        };
        if cand.is_file() {
            out.push((c.clone(), cand));
        }
    }
    out
}

fn resolve_on_path(name: &str) -> Option<PathBuf> {
    if name.contains('/') {
        let p = PathBuf::from(name);
        return p.is_file().then_some(p);
    }
    let path = std::env::var("PATH").ok()?;
    std::env::split_paths(&path)
        .map(|d| d.join(name))
        .find(|c| c.is_file())
}

/// The interpreter a script names on its `#!` line (`#!/usr/bin/env python3` -> `python3`).
fn shebang(file: &Path) -> Option<String> {
    use std::io::Read;
    let mut head = [0u8; 256];
    let n = std::fs::File::open(file).ok()?.read(&mut head).ok()?;
    let first = head[..n].split(|b| *b == b'\n').next()?;
    let line = String::from_utf8_lossy(first);
    let rest = line.strip_prefix("#!")?.trim();
    let mut parts = rest.split_whitespace();
    let prog = parts.next()?;
    if Path::new(prog)
        .file_name()
        .map(|n| n == "env")
        .unwrap_or(false)
    {
        parts.find(|a| !a.starts_with('-')).map(|s| s.to_string())
    } else {
        Some(prog.to_string())
    }
}

/// The module a `python -m <module>` style command runs, and the directory it is resolved from.
fn module_of(desc: &PluginDescriptor, root: &Path) -> Option<(String, PathBuf)> {
    let i = desc.command.iter().position(|c| c == "-m")?;
    let module = desc.command.get(i + 1)?.clone();
    let base = match &desc.cwd {
        Some(c) => {
            let c = placeholders(desc, root, c);
            if Path::new(&c).is_absolute() {
                PathBuf::from(c)
            } else {
                root.join(c)
            }
        }
        None => root.to_path_buf(),
    };
    Some((module, base))
}

/// Files that make up a plugin's implementation (its command files and, for `-m`, the module's file or package).
fn implementation_files(desc: &PluginDescriptor, root: &Path) -> (Vec<PathBuf>, Vec<PathBuf>) {
    let mut files: Vec<PathBuf> = command_files(desc, root)
        .into_iter()
        .map(|(_, p)| p)
        .collect();
    let mut package_dirs = vec![];
    if let Some((module, base)) = module_of(desc, root) {
        let top = module.split('.').next().unwrap_or("").to_string();
        if !top.is_empty() {
            let dir = base.join(&top);
            let single = base.join(format!("{top}.py"));
            if dir.is_dir() {
                package_dirs.push(dir);
            } else if single.is_file() {
                files.push(single);
            }
        }
    }
    files.sort();
    files.dedup();
    (files, package_dirs)
}

fn walk_scope(dir: &Path, out: &mut Vec<PathBuf>) {
    let walker = walkdir::WalkDir::new(dir)
        .sort_by_file_name()
        .into_iter()
        .filter_entry(|e| {
            if e.depth() == 0 {
                return true;
            }
            let name = e.file_name().to_string_lossy();
            !(e.file_type().is_dir()
                && (name.starts_with('.')
                    || crate::paths::ALWAYS_EXCLUDED_DIRS.contains(&name.as_ref())))
        });
    for e in walker.filter_map(|e| e.ok()) {
        if e.file_type().is_file() && !e.path_is_symlink() {
            let n = e.file_name().to_string_lossy();
            if n.ends_with(".pyc") || n.ends_with(".pyo") {
                continue;
            }
            out.push(e.path().to_path_buf());
        }
    }
}

/// The runtime a plugin command executes on: the interpreter named by a local script's `#!` line, a local binary
/// itself, or the program resolved on `PATH`.
fn plugin_runtime(
    desc: &PluginDescriptor,
    root: &Path,
    cache: &StatCache,
    hashed: &[FileId],
) -> (Value, Value, Vec<FileId>) {
    let cmd0 = placeholders(
        desc,
        root,
        desc.command.first().map(|s| s.as_str()).unwrap_or(""),
    );
    let local = if Path::new(&cmd0).is_absolute() {
        PathBuf::from(&cmd0)
    } else {
        root.join(&cmd0)
    };
    let (id, kind, exe) = if local.is_file() {
        match shebang(&local) {
            Some(interp) => {
                let id = Path::new(&interp)
                    .file_name()
                    .map(|n| n.to_string_lossy().to_string())
                    .unwrap_or(interp.clone());
                (id, "interpreter", resolve_on_path(&interp))
            }
            None => (
                local
                    .file_name()
                    .map(|n| n.to_string_lossy().to_string())
                    .unwrap_or_default(),
                "executable",
                Some(local.clone()),
            ),
        }
    } else {
        let id = Path::new(&cmd0)
            .file_name()
            .map(|n| n.to_string_lossy().to_string())
            .unwrap_or(cmd0.clone());
        (id, "interpreter", resolve_on_path(&cmd0))
    };
    let resolved = exe.as_ref().map(|e| e.canonicalize().unwrap_or(e.clone()));
    // an executable that is also the adapter's implementation file is hashed once
    let fid = resolved.as_ref().and_then(|r| {
        hashed
            .iter()
            .find(|f| f.abs.canonicalize().ok().as_ref() == Some(r))
            .map(|f| FileId {
                key: format!("runtime:{}", r.display()),
                ..f.clone()
            })
            .or_else(|| file_id(&format!("runtime:{}", r.display()), r, cache))
    });
    let kind = if resolved.is_none() {
        "unresolved"
    } else {
        kind
    };
    let portable = json!({"id": id, "kind": kind});
    let observed = json!({"id": id, "kind": kind, "path": resolved.as_ref().map(|r| r.display().to_string()),
                          "sha256": fid.as_ref().map(|f| f.sha256.clone())});
    (portable, observed, fid.into_iter().collect())
}

fn plugin_identity(
    p: &Project,
    role: &str,
    desc: &PluginDescriptor,
    extra_model: Value,
    recorded: Option<&Value>,
) -> ComponentIdentity {
    let root = p.root.as_path();
    let cache = stat_cache(recorded);
    let (impl_files, package_dirs) = implementation_files(desc, root);
    let mut files: Vec<FileId> = vec![];
    let mut implementation = vec![];
    for f in &impl_files {
        let key = portable_key(root, f);
        if let Some(fid) = file_id(&key, f, &cache) {
            implementation.push(json!({"path": key, "sha256": fid.sha256}));
            files.push(fid);
        }
    }
    // the descriptor fields that decide what executes and how (not its provenance, registration or status notes)
    let exec: serde_json::Map<String, Value> = [
        "plugin_id",
        "capability",
        "command",
        "cwd",
        "version",
        "languages",
        "timeout_seconds",
        "permissions",
    ]
    .iter()
    .filter_map(|k| desc.raw.get(*k).map(|v| (k.to_string(), v.clone())))
    .collect();
    let adapter = json!({"kind": "plugin", "plugin_id": desc.plugin_id, "version": desc.version,
        "descriptor_exec_sha256": h(&Value::Object(exec)),
        "implementation": implementation, "implementation_sha256": h(&json!(implementation))});
    // --- model artefact: everything shipped beside the implementation (its own directory or module package),
    // other plugins' implementations and this plugin's own implementation files excluded
    let mut scopes: Vec<PathBuf> = package_dirs.clone();
    let mut notes = vec![];
    for f in &impl_files {
        let Ok(rel) = f.strip_prefix(root) else {
            notes.push(format!("implementation {} is outside the repository: its model artefacts are bound only through the adapter implementation", portable_key(root, f)));
            continue;
        };
        let parent = rel.parent().map(|x| x.to_path_buf()).unwrap_or_default();
        let prel = parent.to_string_lossy().replace('\\', "/");
        if prel.is_empty() || prel == "governance" || prel.starts_with("governance/") {
            notes.push(format!(
                "implementation {} sits in {}: only the file itself is bound",
                rel.display(),
                if prel.is_empty() {
                    "the repository root".to_string()
                } else {
                    prel
                }
            ));
            continue;
        }
        scopes.push(root.join(parent));
    }
    scopes.sort();
    scopes.dedup();
    let scopes: Vec<PathBuf> = scopes
        .iter()
        .filter(|s| !scopes.iter().any(|o| o != *s && s.starts_with(o)))
        .cloned()
        .collect();
    let mut others: BTreeSet<PathBuf> = BTreeSet::new();
    for d in crate::capabilities::host::discover_all(root).0 {
        if d.plugin_id == desc.plugin_id {
            continue;
        }
        for f in implementation_files(&d, root).0 {
            others.insert(f.canonicalize().unwrap_or(f));
        }
    }
    let own: BTreeSet<PathBuf> = impl_files
        .iter()
        .map(|f| f.canonicalize().unwrap_or(f.clone()))
        .collect();
    let mut candidates = vec![];
    for s in &scopes {
        walk_scope(s, &mut candidates);
    }
    let mut artefacts = vec![];
    for f in candidates {
        let c = f.canonicalize().unwrap_or(f.clone());
        if own.contains(&c) || others.contains(&c) {
            continue;
        }
        let key = portable_key(root, &f);
        if let Some(fid) = file_id(&key, &f, &cache) {
            artefacts.push(json!({"path": key, "sha256": fid.sha256}));
            files.push(fid);
        }
    }
    artefacts.sort_by(|a, b| a["path"].as_str().cmp(&b["path"].as_str()));
    let scope: Vec<String> = scopes.iter().map(|s| portable_key(root, s)).collect();
    let mut model = json!({"id": format!("{}@{}", desc.plugin_id, desc.version), "revision": desc.version,
        "declared": false, "scope": scope, "artefacts": artefacts, "notes": notes});
    if let (Some(m), Some(x)) = (model.as_object_mut(), extra_model.as_object()) {
        for (k, v) in x {
            m.insert(k.clone(), v.clone());
        }
    }
    model["sha256"] = json!(h(
        &json!({"id": model["id"], "artefacts": model["artefacts"], "parameters": model.get("parameters")})
    ));
    let (runtime, observed, rt_files) = plugin_runtime(desc, root, &cache, &files);
    files.extend(rt_files);
    ComponentIdentity::finish(role, adapter, model, runtime, observed, files)
}

/// The identity of the embedder that would execute (`recorded`: a prior [`ComponentIdentity::to_record`] whose stat
/// data lets unchanged files skip re-hashing).
pub fn embedder_identity(
    p: &Project,
    emb: &Embedder,
    recorded: Option<&Value>,
) -> ComponentIdentity {
    match emb {
        Embedder::Builtin(_) => builtin_embedder(&emb.spec()),
        Embedder::Plugin { desc, spec } => plugin_identity(
            p,
            "embedder",
            desc,
            json!({"parameters": {"dimensions": spec.dimensions}}),
            recorded,
        ),
    }
}

/// The identity of the reranker that would execute (`None`: no reranker is pinned).
pub fn reranker_identity(
    p: &Project,
    rr: Option<&Reranker>,
    recorded: Option<&Value>,
) -> ComponentIdentity {
    match rr {
        None => no_reranker(),
        Some(r) => plugin_identity(p, "reranker", &r.desc, json!({}), recorded),
    }
}

/// The pinned `embedder` value (index manifest core, runtime meta `embedder`): the policy pin plus the executed
/// component identity.
pub fn embedder_pin(spec: &EmbedSpec, id: &ComponentIdentity) -> Value {
    let mut v = spec.to_value();
    if let (Some(o), Some(x)) = (v.as_object_mut(), id.pin_fields().as_object()) {
        for (k, val) in x {
            o.insert(k.clone(), val.clone());
        }
    }
    v
}

/// The pinned `reranker` value: provider, the **executed** revision (not the policy's `0` placeholder), the pinned
/// revision, and the component identity.
pub fn reranker_pin(rr: Option<&Reranker>, id: &ComponentIdentity) -> Value {
    let mut v = match rr {
        None => json!({"provider": "none", "version": "0"}),
        Some(r) => {
            json!({"provider": r.spec.provider, "version": r.desc.version, "pinned_version": r.spec.version})
        }
    };
    if let (Some(o), Some(x)) = (v.as_object_mut(), id.pin_fields().as_object()) {
        for (k, val) in x {
            o.insert(k.clone(), val.clone());
        }
    }
    v
}

/// The expected embedder pin for the policy-pinned embedder as it would execute now; an embedder that cannot be
/// resolved yields a value that matches no live index (`identity: unresolved:<code>`).
pub fn expected_embedder_pin(p: &Project, spec: &EmbedSpec, plugins: &PluginSet) -> Value {
    match Embedder::resolve(spec, plugins) {
        Ok(e) => embedder_pin(spec, &embedder_identity(p, &e, None)),
        Err(e) => {
            let mut v = spec.to_value();
            v["identity"] = json!(format!("unresolved:{}", e.code));
            v
        }
    }
}

/// **Query-time binding (fail closed).** The embedder about to embed a query must be, component for component, the
/// one the live index was built with: `EMBEDDER_MISMATCH` names the changed component(s).
pub fn verify_live_embedder(p: &Project, db: &RuntimeDb, emb: &Embedder) -> Result<()> {
    let Some(rec) = db.get_meta("embedder_identity") else {
        return Err(GovError::new("EMBEDDER_MISMATCH", "the live index records no embedder component identity (built before component binding); run `gov rebuild-memory` (full) before querying")
            .with_details(json!({"remediation": "gov rebuild-memory"})));
    };
    let cur = embedder_identity(p, emb, Some(&rec));
    let diffs = cur.differences(&rec);
    if diffs.is_empty() {
        return Ok(());
    }
    Err(GovError::new("EMBEDDER_MISMATCH", format!("the live index was embedded by a different {}: {}; its vectors are not comparable with what would embed the query now. Run `gov rebuild-memory` (full re-embed), and govern the change (`gov memory benchmark` + `gov memory select`)", emb.spec().describe(), diffs.join("; ")))
        .with_details(json!({"changed": diffs, "recorded": {"identity": rec["digest"], "adapter": rec["adapter"], "model": {"id": rec["model"]["id"], "sha256": rec["model"]["sha256"]}, "runtime": rec["runtime_observed"]}, "current": cur.manifest_value(), "remediation": "gov rebuild-memory"})))
}

/// **Query-time binding of the reranker (fail closed):** `RERANKER_MISMATCH` when the reranker that would score the
/// candidates is not the one the live index recorded.
pub fn verify_live_reranker(p: &Project, db: &RuntimeDb, rr: &Reranker) -> Result<()> {
    let rec = db.get_meta("reranker_identity");
    let cur = reranker_identity(p, Some(rr), rec.as_ref());
    let diffs = match &rec {
        Some(r) => cur.differences(r),
        None => vec!["no reranker identity recorded by the live index".into()],
    };
    if diffs.is_empty() {
        return Ok(());
    }
    Err(GovError::new("RERANKER_MISMATCH", format!("the pinned reranker '{}' is not the one the live index recorded: {}; run `gov rebuild-memory` to record the reranker it will use, and govern the change (`gov memory select`)", rr.spec.provider, diffs.join("; ")))
        .with_details(json!({"changed": diffs, "current": cur.manifest_value(), "remediation": "gov rebuild-memory"})))
}

// --------------------------------------------------------------------------------------------- the profile

/// The retrieval profile: the pinned embedder and reranker with their component identities.
#[derive(Debug, Clone)]
pub struct Profile {
    pub embedder: Value,
    pub reranker: Value,
    pub digest: String,
}

impl Profile {
    pub fn of(embedder: Value, reranker: Value) -> Profile {
        let digest = h(
            &json!({"embedder": embedder, "reranker": {"provider": reranker["provider"], "version": reranker["version"], "identity": reranker["identity"]}}),
        );
        Profile {
            embedder,
            reranker,
            digest,
        }
    }
    pub fn to_value(&self) -> Value {
        json!({"digest": self.digest, "embedder": self.embedder, "reranker": self.reranker})
    }
    pub fn describe(&self) -> String {
        format!(
            "{}@{} ({}-d, {}){}",
            self.embedder["id"].as_str().unwrap_or("?"),
            self.embedder["version"].as_str().unwrap_or("?"),
            self.embedder["dimensions"],
            self.embedder["source"].as_str().unwrap_or("?"),
            match self.reranker["provider"].as_str() {
                Some("none") | None => String::new(),
                Some(r) => format!(
                    " + rerank {r}@{}",
                    self.reranker["version"].as_str().unwrap_or("?")
                ),
            }
        )
    }
}

/// The profile as the policy pins it and as it would execute now (errors when a pinned component cannot be
/// resolved).
pub fn current_profile(p: &Project) -> Result<Profile> {
    let plugins = plugin_set(p);
    let spec = EmbedSpec::from_policy(p);
    let emb = Embedder::resolve(&spec, &plugins)?;
    let rr = Reranker::resolve(p, &plugins)?;
    let eid = embedder_identity(p, &emb, None);
    let rid = reranker_identity(p, rr.as_ref(), None);
    Ok(Profile::of(
        embedder_pin(&spec, &eid),
        reranker_pin(rr.as_ref(), &rid),
    ))
}

/// Is the profile the kernel's own pin (no project override of the embedder or reranker)? The kernel release
/// governs that one; everything else needs a profile decision.
fn is_kernel_default(p: &Project, prof: &Profile) -> bool {
    let k = p
        .policies()
        .raw
        .get("MEMORY_POLICY")
        .cloned()
        .unwrap_or(Value::Null);
    let s = |path: &str, d: &str| {
        crate::util::deep_get(&k, path)
            .map(|v| match v {
                Value::String(s) => s.clone(),
                other => other.to_string(),
            })
            .unwrap_or_else(|| d.to_string())
    };
    let e = &prof.embedder;
    e["id"].as_str() == Some(s("embedding.provider", BUILTIN_ID).as_str())
        && e["version"].as_str() == Some(s("embedding.version", "1").as_str())
        && e["dimensions"].to_string() == s("embedding.dimensions", "512")
        && prof.reranker["provider"].as_str() == Some(s("reranker.provider", "none").as_str())
}

fn profile_decisions(store: &RecordStore) -> Vec<&Record> {
    let mut v: Vec<&Record> = store
        .of_type("decision")
        .into_iter()
        .filter(|d| d.status() == "ACTIVE" && d.data.get("retrieval_profile").is_some())
        .collect();
    v.sort_by_key(|d| d.id());
    v
}

/// **Ungoverned profile detection (A0-D5-02).** Whether the live profile is the kernel's own pin or is pinned by an
/// ACTIVE retrieval-profile decision; a profile no decision pins — a pin edited directly in the overlay, a plugin
/// revision swapped under the pin — is `UNGOVERNED` (no decision at all) or `UNGOVERNED_CHANGE` (differs from the
/// latest decision). A decision that pins it but is not T2-verifiable on this machine is `GOVERNED_UNVERIFIED`.
pub fn governance(p: &Project, prof: &Profile) -> Value {
    governance_in(p, &RecordStore::load(&p.root), prof)
}

/// [`governance`] over a record store the caller already loaded.
pub fn governance_in(p: &Project, store: &RecordStore, prof: &Profile) -> Value {
    if is_kernel_default(p, prof) {
        return json!({"state": "KERNEL_DEFAULT", "governed": true, "digest": prof.digest, "profile": prof.describe(),
                      "message": format!("the live retrieval profile {} is the kernel's own pin", prof.describe())});
    }
    let decisions = profile_decisions(store);
    if let Some(d) = decisions
        .iter()
        .rev()
        .find(|d| d.data["retrieval_profile"]["digest"].as_str() == Some(prof.digest.as_str()))
    {
        let b = crate::t2::verify_record(d);
        if b.is_verified() {
            return json!({"state": "GOVERNED", "governed": true, "decision": d.id(), "digest": prof.digest, "profile": prof.describe(),
                          "message": format!("the live retrieval profile {} is pinned by decision {}", prof.describe(), d.id())});
        }
        return json!({"state": "GOVERNED_UNVERIFIED", "governed": false, "decision": d.id(), "binding": b.to_value(), "digest": prof.digest,
                      "profile": prof.describe(), "severity": "medium",
                      "message": format!("decision {} pins the live retrieval profile {} but is not an OS-written record verifiable on this machine (T2): re-select the profile here (gov memory benchmark + gov memory select)", d.id(), prof.describe())});
    }
    match decisions.last() {
        Some(d) => {
            let pinned = &d.data["retrieval_profile"];
            let mut changed = vec![];
            for (k, label) in [("embedder", "embedder"), ("reranker", "reranker")] {
                for f in ["id", "provider", "version", "dimensions", "identity"] {
                    let (a, b) = (&pinned[k][f], &prof.to_value()[label][f]);
                    if !(a.is_null() && b.is_null()) && a != b {
                        changed.push(format!("{k}.{f}: decision {} pins {a}, live {b}", d.id()));
                    }
                }
            }
            json!({"state": "UNGOVERNED_CHANGE", "governed": false, "decision": d.id(), "digest": prof.digest, "decided_digest": pinned["digest"],
                   "profile": prof.describe(), "changed": changed, "severity": "high",
                   "message": format!("the live retrieval profile {} differs from the one decision {} pinned ({}): the embedder/reranker pin or its component identity changed outside `gov memory select` (framework §14.3: change only through a measured migration)", prof.describe(), d.id(), changed.join("; "))})
        }
        None => {
            json!({"state": "UNGOVERNED", "governed": false, "digest": prof.digest, "profile": prof.describe(), "severity": "high",
                       "message": format!("the live retrieval profile {} is not the kernel's pin and no decision pins it: the embedder/reranker pin was set outside `gov memory select` (no benchmark evidence, no regression, no change-control gate; framework §14.3)", prof.describe())})
        }
    }
}

/// Governance status of the profile as pinned now (`UNRESOLVED` when a pinned component cannot be resolved).
pub fn status(p: &Project) -> Value {
    match current_profile(p) {
        Ok(prof) => {
            let mut g = governance(p, &prof);
            g["retrieval_profile"] = prof.to_value();
            g
        }
        Err(e) => {
            json!({"state": "UNRESOLVED", "governed": false, "severity": "high", "code": e.code,
                         "message": format!("the pinned retrieval profile cannot be resolved: {}", e.message)})
        }
    }
}

// --------------------------------------------------------------------------------------------- governed change

fn radius_rank(r: &str) -> u8 {
    r.strip_prefix('R')
        .and_then(|n| n.parse().ok())
        .unwrap_or(5)
}

fn heldout_path(p: &Project) -> PathBuf {
    p.root.join(p.policies().get_str(
        "MEMORY_POLICY",
        "regression.heldout_file",
        "governance/tests/memory/heldout.yaml",
    ))
}

/// The benchmark row of `research` that measured `target` (by component identity, not by label).
fn evidence_row(rec: &Record, target: &Profile) -> Option<Value> {
    rec.data["measurements"]["rows"]
        .as_array()?
        .iter()
        .find(|r| {
            r["usable"] == true && r["profile"]["digest"].as_str() == Some(target.digest.as_str())
        })
        .cloned()
}

fn metric(v: &Value, k: &str) -> f64 {
    v[k].as_f64().unwrap_or(0.0)
}

/// Not worse than `baseline` on any held-out measure (recall@k, MRR, precision, stale/superseded hits, forbidden).
fn not_regressed(result: &Value, baseline: &Value) -> bool {
    let eps = 1e-9;
    metric(result, "recall_at_k") + eps >= metric(baseline, "recall_at_k")
        && metric(result, "mrr") + eps >= metric(baseline, "mrr")
        && metric(result, "stale_hit_rate") <= metric(baseline, "stale_hit_rate") + eps
        && metric(result, "superseded_hit_rate") <= metric(baseline, "superseded_hit_rate") + eps
        && result["forbidden_violations"].as_u64().unwrap_or(0)
            <= baseline["forbidden_violations"].as_u64().unwrap_or(0)
}

fn summary_of(r: &Value) -> Value {
    json!({"status": r["status"], "measured": r["measured"], "pass": r["pass"], "queries": r["queries"],
           "recall_at_k": r["recall_at_k"], "mrr": r["mrr"], "precision_at_k": r["precision_at_k"],
           "stale_hit_rate": r["stale_hit_rate"], "superseded_hit_rate": r["superseded_hit_rate"],
           "forbidden_violations": r["forbidden_violations"],
           "failed": r["results"].as_array().map(|a| a.iter().filter(|x| x["pass"] != true).map(|x| x["id"].clone()).collect::<Vec<_>>())})
}

/// The target profile of a candidate (`candidate` syntax of `gov memory benchmark`); the reranker is the
/// candidate's `+rerank:<id>` (`none` = no reranker) or, when absent, the one pinned now.
pub fn candidate_profile(
    p: &Project,
    cand: &crate::memory::benchmark::Candidate,
) -> Result<(Profile, Option<Reranker>)> {
    let plugins = plugin_set(p);
    let emb = Embedder::resolve(&cand.embed, &plugins)?;
    let eid = embedder_identity(p, &emb, None);
    let rr = match cand.reranker.as_deref() {
        Some("none") => None,
        Some(id) => Some(Reranker::resolve_id(p, &plugins, id)?),
        None => Reranker::resolve(p, &plugins)?,
    };
    let rid = reranker_identity(p, rr.as_ref(), None);
    Ok((
        Profile::of(
            embedder_pin(&cand.embed, &eid),
            reranker_pin(rr.as_ref(), &rid),
        ),
        rr,
    ))
}

/// **`gov memory select` — the governed retrieval-profile change (BC-P2-30).** See the module documentation.
/// Without an answered gate it raises (or re-reports) the change-control gate and applies nothing
/// (`applied: false`); with `gate` it verifies the answer against this exact change and applies it.
pub fn select(
    p: &Project,
    candidate: &str,
    research: Option<&str>,
    gate: Option<&str>,
    by: &str,
) -> Result<Value> {
    crate::authority::require(p, "memory_select")?;
    crate::orchestration::control::guard_write(p, "memory select")?;
    let cand = crate::memory::benchmark::parse_candidate(p, candidate)?;
    let (target, target_rr) = candidate_profile(p, &cand)?;
    let current = current_profile(p);
    let current_digest = current
        .as_ref()
        .map(|c| c.digest.clone())
        .unwrap_or_else(|e| format!("unresolved:{}", e.code));
    let current_desc = current
        .as_ref()
        .map(|c| c.describe())
        .unwrap_or_else(|e| format!("unresolved ({})", e.code));
    if let Ok(c) = &current {
        let g = governance(p, c);
        if c.digest == target.digest && g["governed"] == true {
            return Err(GovError::new("PROFILE_UNCHANGED", format!("{candidate} is the live retrieval profile and is already governed ({}); nothing to change", g["state"].as_str().unwrap_or(""))).with_details(g));
        }
    }
    // --- evidence: a T2-bound benchmark research record that measured exactly this target on the current held-out set
    let Some(res_id) = research else {
        return Err(GovError::new("PROFILE_EVIDENCE_REQUIRED", format!("a retrieval-profile change needs benchmark evidence for the chosen candidate (framework §14.3): run `gov memory benchmark --candidate current --candidate {candidate} --record` and pass its research record with --research")));
    };
    let store = RecordStore::load(&p.root);
    let rec = store
        .get(res_id)
        .filter(|r| r.rtype() == "research")
        .ok_or_else(|| {
            GovError::new(
                "PROFILE_EVIDENCE_REQUIRED",
                format!("{res_id} is not a research record"),
            )
        })?;
    if rec.data["benchmark"]["format"].as_str() != Some(BENCHMARK_FORMAT) {
        return Err(GovError::new("PROFILE_EVIDENCE_REQUIRED", format!("{res_id} is not a retrieval benchmark written by `gov memory benchmark --record` (no {BENCHMARK_FORMAT} block)")));
    }
    crate::t2::require_verified(rec, "retrieval-profile benchmark evidence").map_err(|e| {
        GovError::new("PROFILE_EVIDENCE_UNBOUND", format!("{res_id} is not benchmark evidence the OS wrote on this machine as it stands ({}); re-run `gov memory benchmark --record`", e.message)).with_details(e.details)
    })?;
    let hp = heldout_path(p);
    let held_sha = sha256_file(&hp).unwrap_or_default();
    if rec.data["benchmark"]["heldout_sha256"].as_str() != Some(held_sha.as_str()) {
        return Err(GovError::new("PROFILE_EVIDENCE_STALE", format!("{res_id} was measured on another held-out set than {} as it stands; re-run the benchmark", hp.strip_prefix(&p.root).unwrap_or(&hp).display())));
    }
    let row = evidence_row(rec, &target).ok_or_else(|| {
        GovError::new("PROFILE_EVIDENCE_STALE", format!("{res_id} has no usable measurement of {candidate} with its current component identity ({}): it was not benchmarked, or its plugin, model artefact or pins changed since; re-run the benchmark", &target.digest[..12]))
            .with_details(json!({"target": target.to_value(), "measured": rec.data["measurements"]["rows"].as_array().map(|a| a.iter().map(|r| json!({"candidate": r["candidate"], "profile": r["profile"]["digest"], "usable": r["usable"]})).collect::<Vec<_>>())}))
    })?;
    let baseline_row = rec.data["measurements"]["rows"].as_array().and_then(|a| {
        a.iter()
            .find(|r| r["profile"]["digest"].as_str() == Some(current_digest.as_str()))
            .cloned()
    });
    let research_hash = rec.data["content_hash"].as_str().unwrap_or("").to_string();
    let subject_body = json!({"kind": SUBJECT_KIND, "from": current_digest, "to": target.digest, "target": target.to_value(),
        "research": res_id, "research_content_hash": research_hash, "heldout_sha256": held_sha});
    let subject_sha = h(&subject_body);
    // --- the change-control gate for the change's radius (the pins live in governance/project/**)
    let pol = p.policies();
    let radius = pol.get_str(
        "CHANGE_POLICY",
        "radius_rules.governance_paths_radius",
        "R5",
    );
    let auto = pol.get_str("CHANGE_POLICY", "auto_approve_max_radius", "R1");
    let agent_max = pol.get_str(
        "HUMAN_GATE_POLICY",
        "agent_resolvable_when.max_radius",
        "R1",
    );
    let needs_gate = radius_rank(&radius) > radius_rank(&auto);
    let needs_human = radius_rank(&radius) > radius_rank(&agent_max);
    let mut approval = json!({"gate": null, "method": "auto_within_change_policy", "radius": radius, "human_approved": false});
    let mut approved_by = by.to_string();
    let mut approved_by_kind = "agent".to_string();
    if needs_gate {
        let Some(gid) = gate else {
            // re-report a pending gate raised for this exact change instead of raising another
            let existing = store.of_type("human-gate").into_iter().find(|g| {
                g.data["subject"]["sha256"].as_str() == Some(subject_sha.as_str())
                    && matches!(
                        g.get("gate_status").as_str(),
                        "PENDING" | "PRESENTED" | "ANSWERED"
                    )
            });
            let gid = match existing {
                Some(g) => {
                    let st = g.get("gate_status");
                    let declined = st == "ANSWERED"
                        && crate::orchestration::gates::verified_answer_in(p, &store, &g.id())
                            .map(|a| !a.authorises_blocked_work)
                            .unwrap_or(false);
                    let status = if declined {
                        "GATE_DECLINED"
                    } else if st == "ANSWERED" {
                        "GATE_ANSWERED"
                    } else {
                        "WAITING_HUMAN"
                    };
                    return Ok(
                        json!({"applied": false, "status": status, "human_gate": g.id(), "gate_status": st,
                        "subject_sha256": subject_sha, "impact_radius": radius, "human_answer_required": needs_human, "candidate": candidate,
                        "target": target.to_value(), "evidence": res_id,
                        "reason": if declined { format!("gate {} was raised for this exact change and the answer declined it; withdraw it (gov gate revoke {}) to ask again", g.id(), g.id()) } else { format!("gate {} was raised for this exact change; the change is applied only with --gate {} once an answer authorises it", g.id(), g.id()) },
                        "next_actions": if declined { vec![format!("gov gate revoke {}", g.id())] } else { vec![format!("gov gate present {}", g.id()), format!("gov memory select {candidate} --research {res_id} --gate {}", g.id())] }}),
                    );
                }
                None => {
                    let cur_row = baseline_row.as_ref();
                    let rec_confidence = rec.data["confidence"].as_f64().unwrap_or(0.5);
                    let better = cur_row.map(|b| not_regressed(&row, b)).unwrap_or(false);
                    let g = crate::orchestration::gates::create_system(
                        p,
                        json!({
                            "question": format!("Change this repository's retrieval profile from {current_desc} to {}?", target.describe()),
                            "why_now": format!("`gov memory select {candidate}` requested a retrieval-profile change; framework §14.3 allows it only as a measured migration with re-indexing and regression testing, and the pins live in governance/project/** (CHANGE_POLICY radius {radius})"),
                            "current_state": format!("live profile {current_desc} (identity {}); benchmark {res_id} measured the candidate: recall@k {} MRR {} precision {} (current: {})", &current_digest[..current_digest.len().min(12)], row["recall_at_k"], row["mrr"], row["precision_at_k"], cur_row.map(|b| format!("recall@k {} MRR {}", b["recall_at_k"], b["mrr"])).unwrap_or_else(|| "not measured in this benchmark".into())),
                            "options": [
                                {"id": "A", "description": format!("adopt {}: pin it, fully re-index, run the held-out regression and keep it only if the regression holds", target.describe())},
                                {"id": "B", "description": format!("keep the current profile {current_desc}")}
                            ],
                            "impact": format!("every semantic query and context packet is answered from vectors of the new profile after a full re-index ({} vectors measured in {res_id})", row["vectors"]),
                            "reversibility": "reversible: the previous profile is restored through the same governed path (re-pin and full re-index); a failed regression rolls back automatically",
                            "cost_rework": format!("one full re-index ({} ms measured) and a held-out regression run; reverting costs the same", row["index_ms"]),
                            "recommendation": if better { format!("A — the candidate is not worse than the current profile on every held-out measure in {res_id}") } else { format!("B unless the owner accepts the measured trade-off in {res_id} (the candidate is worse than, or not compared with, the current profile on some held-out measure)") },
                            "confidence": rec_confidence.clamp(0.0, 1.0),
                            "impact_radius": radius, "reversible": true, "trigger": TRIGGER,
                            "subject": {"kind": SUBJECT_KIND, "sha256": subject_sha, "candidate": candidate, "research": res_id, "from": current_digest, "to": target.digest},
                        }),
                    )?;
                    g["id"].as_str().unwrap_or("").to_string()
                }
            };
            return Ok(
                json!({"applied": false, "status": "WAITING_HUMAN", "human_gate": gid, "subject_sha256": subject_sha, "impact_radius": radius,
                "human_answer_required": needs_human, "candidate": candidate, "target": target.to_value(), "evidence": res_id,
                "reason": format!("a retrieval-profile change is radius {radius} (> CHANGE_POLICY.auto_approve_max_radius {auto}); it is applied only on an answer to {gid} that authorises this exact change"),
                "next_actions": [format!("gov gate present {gid}"), format!("the owner answers {gid} through the human channel (gov decide {gid} --option A --answer-file <signed>)"), format!("gov memory select {candidate} --research {res_id} --gate {gid}")]}),
            );
        };
        // an answer authorises one application of the change it approved, not a replay after a revert
        if let Some(d) = store.of_type("decision").into_iter().find(|d| {
            d.data.get("retrieval_profile").is_some()
                && d.data["approval"]["gate"].as_str() == Some(gid)
        }) {
            return Err(GovError::new("GATE_ALREADY_APPLIED", format!("gate {gid} already authorised the change recorded by decision {}; a new change needs a new gate (run select without --gate)", d.id())));
        }
        let a = if needs_human {
            // WS-3 IP-8: human approval only from a verified, owner-signed answer bound to this exact change
            crate::orchestration::gates::human_approval_for(p, gid, &subject_sha)?
        } else {
            let a = crate::orchestration::gates::verified_answer(p, gid)?;
            if !a.authorises_blocked_work {
                return Err(GovError::new(
                    "GATE_DECLINED",
                    format!(
                        "gate {gid} was answered '{}': the change is not authorised",
                        a.option
                    ),
                ));
            }
            if a.record.data["subject"]["sha256"].as_str() != Some(subject_sha.as_str()) {
                return Err(GovError::new(
                    "APPROVAL_STALE",
                    format!(
                        "gate {gid} did not approve this change (subject {})",
                        subject_sha
                    ),
                ));
            }
            a
        };
        if a.record.get("trigger") != TRIGGER {
            return Err(GovError::new(
                "GATE_MISMATCH",
                format!("{gid} is not a retrieval-profile change gate"),
            ));
        }
        let human = a.by_kind == "human"
            && crate::orchestration::gates::human_approval_for(p, gid, &subject_sha).is_ok();
        approved_by = if human {
            a.answered_by.clone()
        } else {
            by.to_string()
        };
        approved_by_kind = if human { "human" } else { "agent" }.into();
        approval = json!({"gate": gid, "method": if human { "human" } else { "agent_within_policy" }, "radius": radius,
                          "human_approved": human, "answer": a.to_value()});
    }
    // --- apply: pin, full re-index, held-out regression; roll back when the regression does not hold
    let held = read_yaml(&hp)?;
    let baseline = crate::memory::db::RuntimeDb::open(&p.db_path())
        .ok()
        .filter(|d| d.has_schema())
        .and_then(|d| crate::retrieval::run_heldout(p, &d, &held).ok());
    let pp_path = p.overlay_dir().join("PROJECT_POLICY.yaml");
    let before = std::fs::read(&pp_path).ok();
    let mut pp = read_yaml(&pp_path).unwrap_or(json!({}));
    let mut over = pp.get("policy_overrides").cloned().unwrap_or(json!({}));
    over["MEMORY_POLICY.embedding.provider"] = json!(cand.embed.id);
    over["MEMORY_POLICY.embedding.version"] = json!(cand.embed.version);
    over["MEMORY_POLICY.embedding.dimensions"] = json!(cand.embed.dimensions);
    match &target_rr {
        Some(r) => {
            over["MEMORY_POLICY.reranker.provider"] = json!(r.spec.provider);
            over["MEMORY_POLICY.reranker.version"] = json!(r.desc.version);
        }
        None => {
            over["MEMORY_POLICY.reranker.provider"] = json!("none");
            over["MEMORY_POLICY.reranker.version"] = json!("0");
        }
    }
    pp["policy_overrides"] = over;
    crate::util::write_yaml(&pp_path, &pp)?;
    let restore = |why: &str| -> Value {
        let restored = match &before {
            Some(b) => std::fs::write(&pp_path, b).is_ok(),
            None => std::fs::remove_file(&pp_path).is_ok(),
        };
        let rb = crate::memory::indexer::rebuild(
            p,
            crate::memory::indexer::IndexOptions {
                incremental: false,
                ..Default::default()
            },
        );
        json!({"rolled_back": restored, "reason": why, "reindex_of_previous_profile": match rb { Ok(r) => json!({"ok": true, "manifest_hash": r.manifest_hash}), Err(e) => json!({"ok": false, "code": e.code, "message": e.message}) }})
    };
    let rep = match crate::memory::indexer::rebuild(
        p,
        crate::memory::indexer::IndexOptions {
            incremental: false,
            ..Default::default()
        },
    ) {
        Ok(r) => r,
        Err(e) => {
            let rb = restore("the re-index under the new profile failed");
            return Err(GovError::new(
                "PROFILE_REINDEX_FAILED",
                format!(
                    "re-indexing under {} failed ({}: {}); the previous profile was restored",
                    target.describe(),
                    e.code,
                    e.message
                ),
            )
            .with_details(rb));
        }
    };
    let live = Profile::of(rep.embedder.clone(), rep.reranker.clone());
    if live.digest != target.digest {
        let rb = restore("the re-index did not build the approved profile");
        return Err(GovError::new("PROFILE_IDENTITY_CHANGED", format!("the re-index built {} (identity {}), not the approved {} (identity {}): a component changed between the evidence and the change; the previous profile was restored", live.describe(), &live.digest[..12], target.describe(), &target.digest[..12]))
            .with_details(json!({"approved": target.to_value(), "built": live.to_value(), "rollback": rb})));
    }
    // measured under the policy on disk now (the new pins), never a view cached before the overlay was written
    let pv = crate::memory::indexer::current_view(p);
    let regression = crate::memory::db::RuntimeDb::open(&p.db_path())
        .and_then(|db| crate::retrieval::run_heldout(&pv, &db, &held));
    let result = match regression {
        Ok(r) => r,
        Err(e) => {
            let rb = restore("the held-out regression could not run under the new profile");
            return Err(GovError::new("PROFILE_REGRESSION_FAILED", format!("the held-out regression could not run after re-indexing under {} ({}: {}); the previous profile was restored", target.describe(), e.code, e.message)).with_details(rb));
        }
    };
    let measured = result["measured"] == true;
    let held_by_policy = result["pass"] == true;
    let non_regression = baseline
        .as_ref()
        .filter(|b| b["measured"] == true)
        .map(|b| not_regressed(&result, b));
    let accepted = measured && (held_by_policy || non_regression == Some(true));
    let verdict = if accepted { "PASS" } else { "FAIL" };
    // --- the recorded held-out regression (evidence; an audit input, never a governance-suite record)
    let astore = RecordStore::load(&p.root);
    let aid = astore.next_id("audit");
    let mut findings = vec![];
    if !accepted {
        findings.push(json!({"id": "PR-0001", "severity": "high", "family": "memory_retrieval_regression",
            "message": if !measured { format!("held-out regression after re-indexing under {} is UNMEASURED ({} queries < MEMORY_POLICY.regression.min_queries)", target.describe(), result["queries"]) }
                       else { format!("held-out regression after re-indexing under {} failed the policy thresholds and regressed against the previous profile: recall@k {} MRR {} (before: {})", target.describe(), result["recall_at_k"], result["mrr"], baseline.as_ref().map(|b| format!("recall@k {} MRR {}", b["recall_at_k"], b["mrr"])).unwrap_or_else(|| "not measurable".into())) }}));
    }
    let mut audit = new_record(
        "audit",
        &aid,
        &format!(
            "Retrieval-profile regression {aid} ({verdict}): {}",
            target.describe()
        ),
        json!({
            "scope": REGRESSION_SCOPE, "auditor_role": p.role, "session": p.session_id, "state_class": "EVIDENCE",
            "families": {"memory_retrieval_regression": {"ok": accepted, "findings": findings.len(), "detail": summary_of(&result)}},
            "findings": findings, "verdict": verdict, "green": false, "run_at": crate::util::now_iso(),
            "profile_change": {"subject_sha256": subject_sha, "from": current_digest, "to": target.digest, "live_after_reindex": live.digest, "candidate": candidate},
            "baseline": baseline.as_ref().map(summary_of), "result": summary_of(&result), "non_regression": non_regression, "thresholds_met": held_by_policy,
            "inputs": {"heldout": hp.strip_prefix(&p.root).unwrap_or(&hp).to_string_lossy(), "heldout_sha256": held_sha, "index_manifest_hash": rep.manifest_hash},
            "derived_from": [res_id], "validated_by": [], "tags": ["memory", PROFILE_TAG, "regression"],
        }),
    );
    crate::t2::seal_record(&mut audit, "memory select (regression)")?;
    save_record(&p.root, &audit)?;
    if !accepted {
        let rb = restore("the held-out regression after re-indexing did not hold");
        let _ = crate::memory::failures::record(
            p,
            crate::memory::failures::FailureEvent {
                kind: "regression".into(),
                signature_basis: json!({"profile": target.digest, "heldout": held_sha}),
                title: format!("Retrieval-profile change to {} failed its held-out regression", target.describe()),
                summary: format!("After a full re-index under {} the held-out regression ({aid}) was {}; the change was rolled back to {current_desc}.", target.describe(), result["status"].as_str().unwrap_or("?")),
                subject: json!({"candidate": candidate, "research": res_id, "audit": aid, "result": summary_of(&result)}),
                root_cause_candidates: vec!["the candidate retrieves worse on this repository's held-out queries than the benchmark suggested".into(), "the held-out set is too small to measure the change".into()],
                required_actions: vec!["inspect the failed held-out queries in the audit record".into(), "re-benchmark or keep the current profile".into()],
                operation: "memory select".into(),
                detection: "automatic".into(),
            },
            false,
        );
        return Err(GovError::new(if measured { "PROFILE_REGRESSION_FAILED" } else { "PROFILE_REGRESSION_UNMEASURED" }, format!("the held-out regression after re-indexing under {} did not hold ({aid}); the change was rolled back to {current_desc}", target.describe()))
            .with_details(json!({"audit": aid, "result": summary_of(&result), "baseline": baseline.as_ref().map(summary_of), "rollback": rb})));
    }
    // --- the decision: asserts exactly the evidence supplied; human approval only from the verified human answer
    let dstore = RecordStore::load(&p.root);
    let did = dstore.next_id("decision");
    let alternatives: Vec<Value> = rec.data["measurements"]["rows"].as_array().cloned().unwrap_or_default().iter()
        .map(|r| json!({"candidate": r["candidate"], "usable": r["usable"], "profile": r["profile"]["digest"], "recall_at_k": r["recall_at_k"], "mrr": r["mrr"], "precision_at_k": r["precision_at_k"], "stale_hit_rate": r["stale_hit_rate"], "superseded_hit_rate": r["superseded_hit_rate"], "avg_query_latency_ms": r["avg_query_latency_ms"], "index_ms": r["index_ms"], "error": r.get("error")}))
        .collect();
    let mut derived = vec![json!(res_id), json!(aid)];
    if let Some(g) = approval["gate"].as_str() {
        derived.insert(0, json!(g));
    }
    let rationale = format!(
        "Benchmark {res_id} measured {candidate} on the held-out set: recall@k {} MRR {} precision {}{}. After the full re-index the held-out regression {aid} was {} (recall@k {} MRR {}{}). Change control: radius {radius}; {}.",
        row["recall_at_k"], row["mrr"], row["precision_at_k"],
        baseline_row.as_ref().map(|b| format!(" (current profile: recall@k {} MRR {})", b["recall_at_k"], b["mrr"])).unwrap_or_default(),
        result["status"].as_str().unwrap_or("?"), result["recall_at_k"], result["mrr"],
        if held_by_policy { ", policy thresholds met".to_string() } else { ", not worse than the previous profile".to_string() },
        match approval["gate"].as_str() { Some(g) => format!("authorised by gate {g} ({} answer)", approved_by_kind), None => format!("within CHANGE_POLICY.auto_approve_max_radius {auto}, no gate required") }
    );
    let mut dec = new_record(
        "decision",
        &did,
        &format!("Retrieval profile: {}", target.describe()),
        json!({
            "question": format!("Change this repository's retrieval profile from {current_desc} to {}?", target.describe()),
            "options": [{"id": "A", "description": format!("adopt {}", target.describe())}, {"id": "B", "description": format!("keep {current_desc}")}],
            "chosen_option": "A", "rationale": rationale, "alternatives": alternatives,
            "approved_by": approved_by, "approved_at": crate::util::now_iso(), "human_approved": approval["human_approved"],
            "approved_by_kind": approved_by_kind, "approved_by_role": p.role, "impact_radius": radius, "reversibility": "reversible: re-select the previous profile through gov memory select (re-pin and full re-index)",
            "confidence": rec.data["confidence"].as_f64().unwrap_or(0.5), "derived_from": derived, "evidence_refs": [res_id, aid],
            "retrieval_profile": {"digest": live.digest, "embedder": live.embedder, "reranker": live.reranker, "from": current_digest, "candidate": candidate},
            "subject_sha256": subject_sha, "approval": approval, "tags": ["memory", "embedder-selection", PROFILE_TAG], "state_class": "AUTHORITATIVE",
        }),
    );
    crate::t2::seal_record(&mut dec, "memory select")?;
    save_record(&p.root, &dec)?;
    // the new decision and audit records are governed content: keep the derived index fresh
    let fin = crate::memory::indexer::rebuild(
        p,
        crate::memory::indexer::IndexOptions {
            incremental: true,
            ..Default::default()
        },
    )?;
    Ok(
        json!({"applied": true, "decision": did, "audit": aid, "pinned": live.embedder, "reranker": live.reranker, "profile": live.digest,
              "rebuilt": fin.manifest_hash, "regression": summary_of(&result), "baseline": baseline.as_ref().map(summary_of),
              "human_approved": approval["human_approved"], "approval": approval}),
    )
}
