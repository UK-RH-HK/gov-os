//! Green-evidence currency (Contract v3:95-111, :788-789; frozen AC-10; BC-P2-03).
//!
//! A previously green result is **current** only while every evidence input relevant to it is unchanged. This module
//! is the one place that turns "the inputs" into digests:
//!
//! * every repository file (everything [`crate::paths::iter_repo_files`] sees — the same universe the suite reads) is
//!   assigned to exactly one **input class** by an ordered path partition ([`PATH_CLASSES`]); a file that matches no
//!   specific class is `source` ("relevant source files"). Nothing in the tree is silently outside the key;
//! * two non-file classes cover what the tree cannot show: the **runtime implementation identity** (the executing
//!   `gov` binary's SHA-256 plus the crate versions) and the **machine trust state** (the trust anchor, the
//!   provisioning latch and the break-glass marking of the protected machine state root);
//! * the only files excluded are the health system's **own outputs** (governance-suite and product-test result
//!   records): a result cannot be an input to itself. Their entries are also removed from the index manifest before it
//!   is digested, so indexing a new result does not make the result stale ([`normalized_index_manifest`]).
//!
//! The suite-level key ([`Snapshot::key`]) is what a green governance-suite record stores as `inputs_hash`; the
//! per-class digests ([`Snapshot::classes`]) are stored beside it as `inputs`, so staleness names the classes that
//! changed. The scheduler (`crate::scheduler`) derives each check's cache key from the subset of classes the check
//! declares it depends on ([`Snapshot::key_for`]).
use crate::records::RecordStore;
use crate::util::{glob_match, hash_value, read_bytes, sha256_hex};
use crate::{GovError, Project, Result};
use regex::Regex;
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;
use std::sync::OnceLock;

/// One input class: an id, the Contract v3:97-109 class it realises, and the path patterns that select its files.
#[derive(Debug, Clone, Copy)]
pub struct ClassDef {
    pub id: &'static str,
    pub contract_class: &'static str,
    pub patterns: &'static [&'static str],
}

/// Ordered path partition: the first class whose pattern matches a path owns it. Anything unmatched is `source`.
pub const PATH_CLASSES: &[ClassDef] = &[
    ClassDef {
        id: "kernel_policy",
        contract_class: "governing contract/policy",
        patterns: &[
            "governance/kernel/policies/**",
            "governance/kernel/constitution/**",
            "governance/kernel/contracts/**",
        ],
    },
    ClassDef {
        id: "kernel_schema",
        contract_class: "schema",
        patterns: &["governance/kernel/schemas/**"],
    },
    ClassDef {
        id: "kernel_migration",
        contract_class: "migration",
        patterns: &["governance/kernel/migrations/**"],
    },
    ClassDef {
        id: "kernel_skills",
        contract_class: "skill (versioned method)",
        patterns: &["governance/kernel/skills/**"],
    },
    ClassDef {
        id: "kernel_tools",
        contract_class: "tool/plugin",
        patterns: &["governance/kernel/tools/**"],
    },
    ClassDef {
        id: "kernel_other",
        contract_class: "runtime/kernel implementation",
        patterns: &["governance/kernel/**"],
    },
    ClassDef {
        id: "framework_lock",
        contract_class: "runtime/kernel implementation",
        patterns: &["governance/framework.lock"],
    },
    ClassDef {
        id: "project_policy",
        contract_class: "governing contract/policy",
        patterns: &[
            "governance/project/PROJECT_POLICY.yaml",
            "governance/project/PROJECT_EXCEPTIONS.yaml",
        ],
    },
    ClassDef {
        id: "path_map",
        contract_class: "project path map",
        patterns: &[
            "governance/project/REPOSITORY_CONTRACT.yaml",
            "framework.json",
        ],
    },
    ClassDef {
        id: "sensitivity",
        contract_class: "security/sensitivity policy",
        patterns: &["governance/project/DATA_SENSITIVITY.yaml"],
    },
    ClassDef {
        id: "model_profile",
        contract_class: "model/retrieval profile",
        patterns: &["governance/project/MODEL_ROUTING_OVERRIDES.yaml"],
    },
    ClassDef {
        id: "tools_plugins",
        contract_class: "tool/plugin",
        patterns: &[
            "governance/project/plugins/**",
            "governance/project/tools/**",
            "governance/project/TOOL_PERMISSIONS.yaml",
            "governance/project/CAPABILITY_PROFILE.yaml",
            "governance/generated/tool-registry.json",
            "governance/generated/plugin-registry.json",
            "governance/generated/mcp*",
        ],
    },
    ClassDef {
        id: "project_skills",
        contract_class: "skill (versioned method)",
        patterns: &[
            "governance/project/skills/**",
            "governance/generated/skill-bindings.json",
        ],
    },
    ClassDef {
        id: "overlay_other",
        contract_class: "governing contract/policy",
        patterns: &["governance/project/**"],
    },
    ClassDef {
        id: "governance_tests",
        contract_class: "governing contract/policy (governance test inputs)",
        patterns: &["governance/tests/**"],
    },
    ClassDef {
        id: "index_manifest",
        contract_class: "relevant index manifest",
        patterns: &[
            "governance/generated/index-manifest.json",
            "governance/generated/memory-manifest.json",
        ],
    },
    ClassDef {
        id: "generated_other",
        contract_class: "generated adapters/registries",
        patterns: &["governance/generated/**"],
    },
    ClassDef {
        id: "spec_decisions",
        contract_class: "authoritative spec/decision",
        patterns: &["spec/decisions/**"],
    },
    ClassDef {
        id: "spec_requirements",
        contract_class: "authoritative spec/decision",
        patterns: &[
            "spec/requirements/**",
            "spec/features/**",
            "spec/scenarios/**",
            "spec/product/**",
            "spec/workflows/**",
            "spec/data/**",
            "spec/now/**",
        ],
    },
    ClassDef {
        id: "spec_architecture",
        contract_class: "authoritative spec/decision",
        patterns: &[
            "spec/architecture/**",
            "spec/interfaces/**",
            "spec/security/**",
            "spec/performance/**",
        ],
    },
    ClassDef {
        id: "spec_tasks",
        contract_class: "authoritative spec/decision (task manifests, test obligations)",
        patterns: &["spec/tasks/**"],
    },
    ClassDef {
        id: "research_experiments",
        contract_class: "research/experiment records",
        patterns: &["spec/research/**", "spec/experiments/**"],
    },
    ClassDef {
        id: "continuity_records",
        contract_class: "checkpoint/handoff records",
        patterns: &["spec/reports/checkpoints/**", "spec/planning/**"],
    },
    ClassDef {
        id: "evidence_records",
        contract_class: "implementation/test evidence records",
        patterns: &["spec/reports/**", "spec/lessons/**"],
    },
    ClassDef {
        id: "adoption_evidence",
        contract_class: "adoption/audit evidence",
        patterns: &["spec/audits/**"],
    },
    ClassDef {
        id: "spec_other",
        contract_class: "authoritative spec/decision",
        patterns: &["spec/**"],
    },
    ClassDef {
        id: "archive",
        contract_class: "legacy/historical records",
        patterns: &["archive/**"],
    },
];

/// The default class: every file no specific class claims (product code, tests, docs, build files, README, ...).
pub const SOURCE: &str = "source";
/// Non-file class: the executing implementation (binary SHA-256 + crate versions).
pub const RUNTIME_IDENTITY: &str = "runtime_identity";
/// Non-file class: this machine's protected trust state (anchor, provisioning latch, break-glass marking).
pub const MACHINE_TRUST: &str = "machine_trust";

/// Record scopes the health system writes. A record of one of these scopes is an output, never an input.
pub const HEALTH_OUTPUT_SCOPES: &[&str] = &["governance-suite", "product-tests"];

/// Task classes whose work product is governance input (Contract v3:789 "governance-affecting work"). A task is
/// governance-affecting when its class is listed here **or** when it touches any governed (non-`source`) input.
pub const GOVERNANCE_AFFECTING_TASK_CLASSES: &[&str] = &[
    "governance",
    "specification",
    "decision-preparation",
    "architecture",
    "release",
    "memory",
    "migration",
];

/// Every class id, file classes in partition order, then `source`, then the non-file classes.
pub fn all_class_ids() -> Vec<&'static str> {
    let mut v: Vec<&'static str> = PATH_CLASSES.iter().map(|c| c.id).collect();
    v.push(SOURCE);
    v.push(RUNTIME_IDENTITY);
    v.push(MACHINE_TRUST);
    v
}

/// Contract v3 label for a class id (for reports).
pub fn contract_class_of(id: &str) -> &'static str {
    match id {
        SOURCE => "relevant source files",
        RUNTIME_IDENTITY => "runtime/kernel implementation",
        MACHINE_TRUST => "machine trust state",
        _ => PATH_CLASSES
            .iter()
            .find(|c| c.id == id)
            .map(|c| c.contract_class)
            .unwrap_or("unknown"),
    }
}

/// The input class that owns a repository-relative path.
pub fn classify_path(rel: &str) -> &'static str {
    for c in PATH_CLASSES {
        if c.patterns.iter().any(|pat| glob_match(pat, rel)) {
            return c.id;
        }
    }
    SOURCE
}

fn scope_regex() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| {
        Regex::new(r#"(?m)^scope:\s*['"]?([A-Za-z0-9_.-]+)['"]?\s*$"#).expect("scope regex")
    })
}
fn type_audit_regex() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r#"(?m)^type:\s*['"]?audit['"]?\s*$"#).expect("type regex"))
}

/// Is this record text a health-system output (a top-level `type: audit` record whose `scope` is a health scope)?
pub fn is_health_output_text(text: &str) -> bool {
    if !type_audit_regex().is_match(text) {
        return false;
    }
    scope_regex()
        .captures(text)
        .map(|c| HEALTH_OUTPUT_SCOPES.contains(&&c[1]))
        .unwrap_or(false)
}

/// Is the repository path a health-system output? Only top-level records under `spec/audits/` qualify (adoption
/// evidence lives in sub-directories and stays an input).
pub fn is_health_output(rel: &str, abs: &Path) -> bool {
    let Some(name) = rel.strip_prefix("spec/audits/") else {
        return false;
    };
    if name.contains('/') || !(name.ends_with(".yaml") || name.ends_with(".yml")) {
        return false;
    }
    std::fs::read_to_string(abs)
        .map(|t| is_health_output_text(&t))
        .unwrap_or(false)
}

/// The file identity of an executable that changes whenever its bytes can have changed: device, inode, size,
/// modification time and status-change time (`ctime` cannot be set by an unprivileged process).
#[cfg(unix)]
fn exe_stat_key(exe: &Path) -> Option<String> {
    use std::os::unix::fs::MetadataExt;
    let m = std::fs::metadata(exe).ok()?;
    Some(format!(
        "{}:{}:{}:{}.{}:{}.{}",
        m.dev(),
        m.ino(),
        m.size(),
        m.mtime(),
        m.mtime_nsec(),
        m.ctime(),
        m.ctime_nsec()
    ))
}
#[cfg(not(unix))]
fn exe_stat_key(_exe: &Path) -> Option<String> {
    None
}

fn digest_cache_path() -> Option<std::path::PathBuf> {
    std::env::var("XDG_CACHE_HOME")
        .ok()
        .filter(|v| !v.is_empty())
        .map(|c| std::path::PathBuf::from(c).join("gov"))
        .or_else(|| {
            std::env::var("HOME")
                .ok()
                .map(|h| std::path::PathBuf::from(h).join(".cache").join("gov"))
        })
        .map(|d| d.join("runtime-digests.json"))
}

/// SHA-256 of the running executable. The digest is re-used across processes only for the same file identity
/// ([`exe_stat_key`]); a replaced or rewritten binary always has a different identity and is hashed afresh.
fn exe_sha256(exe: &Path) -> Option<String> {
    let key = exe_stat_key(exe).map(|k| format!("{}|{k}", exe.display()));
    let cache = digest_cache_path();
    if let (Some(k), Some(c)) = (&key, &cache) {
        if let Some(v) = crate::util::read_json(c)
            .ok()
            .and_then(|d| d.get(k).and_then(|x| x.as_str()).map(|s| s.to_string()))
        {
            return Some(v);
        }
    }
    let sha = sha256_hex(&read_bytes(exe).ok()?);
    if let (Some(k), Some(c)) = (key, cache) {
        let mut d = crate::util::read_json(&c).unwrap_or(json!({}));
        if let Some(o) = d.as_object_mut() {
            if o.len() > 64 {
                o.clear();
            }
            o.insert(k, json!(sha));
        }
        if let Some(dir) = c.parent() {
            let _ = std::fs::create_dir_all(dir);
        }
        let tmp = c.with_extension(format!("tmp-{}", crate::util::short_uuid()));
        if crate::util::write_json(&tmp, &d).is_ok() {
            let _ = std::fs::rename(&tmp, &c);
        }
    }
    Some(sha)
}

/// The executing implementation: crate versions and the SHA-256 of the running executable (computed once per process).
pub fn runtime_identity() -> &'static Value {
    static ID: OnceLock<Value> = OnceLock::new();
    ID.get_or_init(|| {
        let exe = std::env::current_exe().ok();
        let sha = exe
            .as_ref()
            .and_then(|e| exe_sha256(e))
            .unwrap_or_else(|| "unavailable".into());
        json!({
            "cli_version": crate::CLI_VERSION,
            "runtime_version": crate::RUNTIME_VERSION,
            "index_version": crate::INDEX_VERSION,
            "binary_sha256": sha,
            "binary_name": exe.as_ref().and_then(|e| e.file_name()).map(|n| n.to_string_lossy().to_string()),
        })
    })
}

/// Digest-relevant subset of the runtime identity (the file name is informational only).
fn runtime_digest() -> String {
    let id = runtime_identity();
    hash_value(&json!({
        "cli_version": id["cli_version"], "runtime_version": id["runtime_version"],
        "index_version": id["index_version"], "binary_sha256": id["binary_sha256"],
    }))
}

fn sha_opt(p: &Path) -> Value {
    match read_bytes(p) {
        Ok(b) => json!(sha256_hex(&b)),
        Err(_) => Value::Null,
    }
}

/// This machine's trust state as the currency key sees it. Read-only: nothing is created.
///
/// Covered: the provisioned trust anchor, the provisioning latch and the break-glass marking. The anchor is read only
/// through the SRR verifier's reader (`srr::verifier::trusted_root`: the digest of the anchor file when it verifies,
/// the refusal code when it does not) — the R1 census basis is that nothing outside `srr/state.rs` and
/// `srr/verifier.rs` reaches the anchor path (AR-0031 `hx_a::a4`; integration P2-AR-0022).
/// Not covered: `floors/` and `installed/` — they are advanced by the lifecycle transaction itself *after* its
/// verification (init/update step 9) and the kernel content they bind is already keyed through `governance/kernel`
/// and `framework.lock`. If kernel trust starts consulting the installed record (BC-P2-35), that record must be added
/// here and the lifecycle conformance run moved after `srr::record_installed` (integration point, WS-8).
pub fn machine_trust_state() -> Value {
    match crate::srr::state::resolve_state_root() {
        Ok(root) => {
            let ms = crate::srr::state::MachineState::read_only(&root);
            let provisioned = ms.provisioned_path();
            let now = crate::srr::metadata::local_clock_now();
            let anchor = match crate::srr::verifier::trusted_root(&ms, &now) {
                Ok(Some(r)) => json!(r.envelope.file_sha256),
                Ok(None) => Value::Null,
                Err(e) => json!(format!("UNVERIFIABLE:{}", e.code)),
            };
            json!({
                "posture": if provisioned.exists() { "PROVISIONED" } else { "UNPROVISIONED" },
                "trust_anchor_sha256": anchor,
                "provisioning_latch_sha256": sha_opt(&provisioned),
                "break_glass_marking_sha256": sha_opt(&crate::srr::state::degraded_path_at(&root, crate::FRAMEWORK_NAME)),
            })
        }
        Err(e) => json!({"posture": "UNRESOLVED", "error": e.code}),
    }
}

/// The tracked index/memory manifests with the fields that describe *when* or *from which commit* they were built,
/// and every entry for a health-system output, removed. What remains is what the index was built from and with.
pub fn normalized_index_manifest(root: &Path, rel: &str, v: &Value) -> Value {
    let Some(obj) = v.as_object() else {
        return v.clone();
    };
    let mut m = obj.clone();
    if rel.ends_with("memory-manifest.json") {
        m.remove("stores");
        m.remove("manifest_hash");
        return Value::Object(m);
    }
    let self_consistent = obj
        .get("manifest_hash")
        .and_then(|h| h.as_str())
        .map(|h| h == crate::memory::manifest::manifest_hash(v))
        .unwrap_or(false);
    for k in ["built_at", "repo_commit", "counts", "manifest_hash"] {
        m.remove(k);
    }
    let drop = |path: &str, entry: Option<&Value>| -> bool {
        let abs = root.join(path);
        if abs.exists() {
            return is_health_output(path, &abs);
        }
        // a removed file whose manifest entry says it was an audit record under spec/audits/ was a health output
        path.starts_with("spec/audits/")
            && !path["spec/audits/".len()..].contains('/')
            && entry
                .and_then(|e| e.get("record_type"))
                .and_then(|t| t.as_str())
                == Some("audit")
    };
    if let Some(arts) = m.get("artifacts").and_then(|a| a.as_object()).cloned() {
        let kept: Map<String, Value> = arts
            .into_iter()
            .filter(|(path, e)| !drop(path, Some(e)))
            .collect();
        m.insert("artifacts".into(), Value::Object(kept));
    }
    if let Some(ex) = m.get("excluded").and_then(|a| a.as_array()).cloned() {
        let kept: Vec<Value> = ex
            .into_iter()
            .filter(|e| !drop(e["path"].as_str().unwrap_or(""), None))
            .collect();
        m.insert("excluded".into(), Value::Array(kept));
    }
    m.insert("self_consistent".into(), json!(self_consistent));
    Value::Object(m)
}

/// A point-in-time view of every evidence input: per-file digests, per-class digests and the non-file classes.
#[derive(Debug, Clone)]
pub struct Snapshot {
    /// class id → digest (every class in [`all_class_ids`], present even when empty)
    pub classes: BTreeMap<String, String>,
    /// repository-relative path → (class id, content digest)
    pub files: BTreeMap<String, (String, String)>,
    /// health-system outputs excluded from the key
    pub excluded: Vec<String>,
    pub runtime: Value,
    pub machine_trust: Value,
}

impl Snapshot {
    /// Digest every input. Cost is one read of every repository file (the same files the suite reads).
    pub fn take(p: &Project) -> Result<Snapshot> {
        let mut files: BTreeMap<String, (String, String)> = BTreeMap::new();
        let mut excluded = vec![];
        for (abs, rel) in crate::paths::iter_repo_files(&p.root, false) {
            if is_health_output(&rel, &abs) {
                excluded.push(rel);
                continue;
            }
            let class = classify_path(&rel);
            let digest = if class == "index_manifest" {
                match crate::util::read_json(&abs) {
                    Ok(v) => hash_value(&normalized_index_manifest(&p.root, &rel, &v)),
                    Err(_) => sha256_hex(&read_bytes(&abs).unwrap_or_default()),
                }
            } else {
                match read_bytes(&abs) {
                    Ok(b) => sha256_hex(&b),
                    Err(e) => format!("unreadable:{e}"),
                }
            };
            files.insert(rel, (class.to_string(), digest));
        }
        let mut per_class: BTreeMap<String, Vec<(String, String)>> = BTreeMap::new();
        for id in all_class_ids() {
            per_class.insert(id.to_string(), vec![]);
        }
        for (rel, (class, d)) in &files {
            per_class
                .entry(class.clone())
                .or_default()
                .push((rel.clone(), d.clone()));
        }
        let runtime = runtime_identity().clone();
        let machine_trust = machine_trust_state();
        let mut classes = BTreeMap::new();
        for (id, entries) in per_class {
            let d = match id.as_str() {
                RUNTIME_IDENTITY => runtime_digest(),
                MACHINE_TRUST => hash_value(&machine_trust),
                _ => hash_value(&json!(entries)),
            };
            classes.insert(id, d);
        }
        Ok(Snapshot {
            classes,
            files,
            excluded,
            runtime,
            machine_trust,
        })
    }

    /// The suite-level currency key: a digest over every class digest.
    pub fn key(&self) -> String {
        hash_value(&json!(self.classes))
    }

    /// The digest of a subset of classes (a check's declared dependencies). Unknown class ids are an error in the
    /// declaration, so they are keyed as themselves and can never collide with a real digest.
    pub fn key_for(&self, deps: &[&str]) -> String {
        let mut m = BTreeMap::new();
        for d in deps {
            m.insert(
                d.to_string(),
                self.classes
                    .get(*d)
                    .cloned()
                    .unwrap_or_else(|| format!("undeclared-class:{d}")),
            );
        }
        hash_value(&json!(m))
    }

    /// Per-class digests as JSON (stored beside `inputs_hash` in every health result).
    pub fn classes_value(&self) -> Value {
        json!(self.classes)
    }

    /// Classes whose digest differs from a previously recorded `inputs` map (a record without per-class digests
    /// predates this key; every class is then reported as unknown).
    pub fn changed_classes(&self, recorded: &Value) -> Vec<String> {
        let Some(rec) = recorded.as_object() else {
            return vec!["<record predates per-class input digests>".into()];
        };
        let mut out = vec![];
        for (id, d) in &self.classes {
            if rec.get(id).and_then(|v| v.as_str()) != Some(d.as_str()) {
                out.push(id.clone());
            }
        }
        for id in rec.keys() {
            if !self.classes.contains_key(id) {
                out.push(id.clone());
            }
        }
        out
    }

    /// Repository paths whose digest differs from a previous file map (added, changed or removed).
    pub fn changed_paths(&self, previous: &BTreeMap<String, (String, String)>) -> Vec<String> {
        let mut out = vec![];
        for (rel, (_, d)) in &self.files {
            match previous.get(rel) {
                Some((_, pd)) if pd == d => {}
                _ => out.push(rel.clone()),
            }
        }
        for rel in previous.keys() {
            if !self.files.contains_key(rel) {
                out.push(rel.clone());
            }
        }
        out.sort();
        out
    }

    /// A compact description for reports: counts per class, excluded outputs, runtime and machine trust.
    pub fn describe(&self) -> Value {
        let mut counts: BTreeMap<String, usize> = BTreeMap::new();
        for (class, _) in self.files.values() {
            *counts.entry(class.clone()).or_insert(0) += 1;
        }
        json!({
            "key": self.key(),
            "classes": self.classes.iter().map(|(id, d)| (id.clone(), json!({"digest": d, "files": counts.get(id).cloned().unwrap_or(0), "contract_class": contract_class_of(id)}))).collect::<Map<String, Value>>(),
            "excluded_health_outputs": self.excluded,
            "runtime": self.runtime,
            "machine_trust": self.machine_trust,
        })
    }
}

/// The suite-level currency key for the project as it is now.
pub fn inputs_hash(p: &Project) -> String {
    Snapshot::take(p)
        .map(|s| s.key())
        .unwrap_or_else(|e| format!("unavailable:{}", e.code))
}

/// The latest green governance-suite record (by id order), if any.
pub fn latest_green(p: &Project) -> Option<Value> {
    let store = RecordStore::load(&p.root);
    let mut audits: Vec<&crate::records::Record> = store
        .of_type("audit")
        .into_iter()
        .filter(|a| {
            a.data["green"].as_bool().unwrap_or(false) && a.get("scope") == "governance-suite"
        })
        .collect();
    audits.sort_by_key(|a| a.id());
    audits.last().map(|a| a.data.clone())
}

/// Currency of the latest green governance-suite record against the current inputs.
#[derive(Debug, Clone, serde::Serialize)]
pub struct Currency {
    pub green: Option<String>,
    pub current: bool,
    pub changed_classes: Vec<String>,
    pub key: String,
    pub recorded_key: Option<String>,
}

impl Currency {
    pub fn evaluate(p: &Project, snap: &Snapshot) -> Currency {
        let key = snap.key();
        match latest_green(p) {
            Some(g) => {
                let rk = g["inputs_hash"].as_str().map(|s| s.to_string());
                let current = rk.as_deref() == Some(key.as_str());
                let changed = if current {
                    vec![]
                } else {
                    snap.changed_classes(&g["inputs"])
                };
                Currency {
                    green: g["id"].as_str().map(|s| s.to_string()),
                    current,
                    changed_classes: changed,
                    key,
                    recorded_key: rk,
                }
            }
            None => Currency {
                green: None,
                current: false,
                changed_classes: vec![],
                key,
                recorded_key: None,
            },
        }
    }
    /// One-line description used by doctor D021 and the close gate.
    pub fn message(&self) -> String {
        match (&self.green, self.current) {
            (Some(g), true) => format!("green record \"{g}\" current"),
            (Some(g), false) => format!(
                "green record \"{g}\" is obsolete (inputs changed: {})",
                if self.changed_classes.is_empty() {
                    "unknown".to_string()
                } else {
                    self.changed_classes.join(", ")
                }
            ),
            (None, _) => "no green governance record".into(),
        }
    }
    pub fn to_value(&self) -> Value {
        json!({"green": self.green, "current": self.current, "changed_classes": self.changed_classes.iter().map(|c| json!({"class": c, "contract_class": contract_class_of(c)})).collect::<Vec<_>>(), "key": self.key, "recorded_key": self.recorded_key, "message": self.message()})
    }
}

/// Is a task governance-affecting? By class, and by the governed inputs it touches (Contract v3:789). The closing
/// task's own record is ignored: the OS writes its status transitions.
pub fn governance_affecting(task: &Value, touched: &[String]) -> (bool, Vec<String>) {
    let mut reasons = vec![];
    let class = task.get("class").and_then(|v| v.as_str()).unwrap_or("");
    if GOVERNANCE_AFFECTING_TASK_CLASSES.contains(&class) {
        reasons.push(format!("task class '{class}' is governance-affecting"));
    }
    let own = task
        .get("id")
        .and_then(|v| v.as_str())
        .map(|id| format!("spec/tasks/{id}.yaml"));
    let mut governed: BTreeSet<String> = BTreeSet::new();
    for f in touched {
        if Some(f) == own.as_ref() {
            continue;
        }
        let c = classify_path(f);
        if c != SOURCE {
            governed.insert(format!("{f} ({c})"));
        }
    }
    if !governed.is_empty() {
        reasons.push(format!(
            "touches governed inputs: {}",
            governed.into_iter().collect::<Vec<_>>().join(", ")
        ));
    }
    (!reasons.is_empty(), reasons)
}

/// The task-close currency verdict (evaluation only; [`enforce_close`] turns it into a refusal).
pub fn close_currency(p: &Project, task: &Value, touched: &[String]) -> Result<Value> {
    let (affecting, reasons) = governance_affecting(task, touched);
    let snap = Snapshot::take(p)?;
    let cur = Currency::evaluate(p, &snap);
    Ok(
        json!({"governance_affecting": affecting, "reasons": reasons, "currency": cur.to_value(), "allowed": !affecting || cur.current}),
    )
}

/// **Close gate (integration point for `orchestration::tasks::close`, WS-5).** Refuses the close of every
/// governance-affecting task (by class or by the governed inputs it touches) while the green governance evidence is
/// stale or absent. With `force` (an L3+ decision the caller has already authorised) the close proceeds and the
/// returned notes must be recorded as `degraded` on the report. The host is expected to have run
/// `crate::scheduler::tier_run(p, Tier::G2, ..)` first, so staleness that a re-check can clear is cleared before this
/// gate is asked.
pub fn enforce_close(
    p: &Project,
    task: &Value,
    touched: &[String],
    force: bool,
) -> Result<Vec<String>> {
    let (affecting, reasons) = governance_affecting(task, touched);
    if !affecting {
        return Ok(vec![]);
    }
    let snap = Snapshot::take(p)?;
    let cur = Currency::evaluate(p, &snap);
    if cur.current {
        return Ok(vec![]);
    }
    if force {
        return Ok(vec![format!("governance suite stale: {}", cur.message())]);
    }
    let (code, msg) = if cur.green.is_some() {
        ("GOVERNANCE_SUITE_STALE", format!("governance-affecting work cannot close on stale green evidence: {}; run `gov health run` (re-checks only the checks the changed inputs impact) or `gov audit`", cur.message()))
    } else {
        ("GOVERNANCE_SUITE_MISSING", "governance-affecting work cannot close: no green governance record exists; run `gov health run` or `gov audit`".to_string())
    };
    Err(GovError::new(code, msg).with_details(
        json!({"governance_affecting_because": reasons, "currency": cur.to_value(), "remediation": "gov health run"}),
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_contract_input_class_has_an_owner_class() {
        let cases = [
            (
                "governance/kernel/policies/BUDGET_POLICY.yaml",
                "kernel_policy",
            ),
            (
                "governance/kernel/schemas/task.schema.json",
                "kernel_schema",
            ),
            ("governance/kernel/migrations/M-1.yaml", "kernel_migration"),
            ("governance/kernel/skills/SKL-X.yaml", "kernel_skills"),
            ("governance/kernel/KERNEL.yaml", "kernel_other"),
            ("governance/framework.lock", "framework_lock"),
            ("governance/project/PROJECT_POLICY.yaml", "project_policy"),
            ("governance/project/REPOSITORY_CONTRACT.yaml", "path_map"),
            ("governance/project/DATA_SENSITIVITY.yaml", "sensitivity"),
            (
                "governance/project/MODEL_ROUTING_OVERRIDES.yaml",
                "model_profile",
            ),
            ("governance/project/plugins/x.yaml", "tools_plugins"),
            ("governance/generated/tool-registry.json", "tools_plugins"),
            ("governance/project/skills/SKL-P.yaml", "project_skills"),
            ("governance/tests/memory/heldout.yaml", "governance_tests"),
            ("governance/generated/index-manifest.json", "index_manifest"),
            (
                "governance/generated/adapters/ide/RULES.md",
                "generated_other",
            ),
            ("spec/decisions/D-0001.yaml", "spec_decisions"),
            ("spec/requirements/REQ-0001.yaml", "spec_requirements"),
            ("spec/architecture/ARCH-0001.yaml", "spec_architecture"),
            ("spec/interfaces/API-0001.yaml", "spec_architecture"),
            ("spec/tasks/TASK-0001.yaml", "spec_tasks"),
            ("spec/research/RES-1.yaml", "research_experiments"),
            ("spec/experiments/EXP-1.yaml", "research_experiments"),
            ("spec/reports/checkpoints/CKPT-1.yaml", "continuity_records"),
            ("spec/planning/HND-1.yaml", "continuity_records"),
            ("spec/reports/RPT-0001.yaml", "evidence_records"),
            (
                "spec/audits/GOVERNANCE-ADOPTION/06.yaml",
                "adoption_evidence",
            ),
            ("src/lib.rs", SOURCE),
            ("product/app.py", SOURCE),
            ("docs/x.md", SOURCE),
        ];
        for (path, want) in cases {
            assert_eq!(classify_path(path), want, "{path}");
        }
        let ids = all_class_ids();
        assert!(ids.contains(&RUNTIME_IDENTITY) && ids.contains(&MACHINE_TRUST));
    }

    #[test]
    fn health_outputs_are_recognised_by_content_not_by_name() {
        let suite =
            "id: AUD-0002\ntype: audit\ntitle: t\nstatus: ACTIVE\nscope: governance-suite\n";
        let product = "id: AUD-0003\ntype: audit\nscope: 'product-tests'\n";
        let independent = "id: AUD-0100\ntype: audit\nscope: independent-full-audit\n";
        let nested = "id: AUD-0101\ntype: audit\nnote:\n  scope: governance-suite\n";
        assert!(is_health_output_text(suite));
        assert!(is_health_output_text(product));
        assert!(!is_health_output_text(independent));
        assert!(!is_health_output_text(nested));
        assert!(!is_health_output_text(
            "id: X\ntype: decision\nscope: governance-suite\n"
        ));
    }

    #[test]
    fn governance_affecting_by_class_and_by_touched_inputs() {
        let t = json!({"id": "TASK-0001", "class": "governance"});
        assert!(governance_affecting(&t, &[]).0);
        let t = json!({"id": "TASK-0002", "class": "implementation"});
        assert!(!governance_affecting(&t, &["src/lib.rs".into()]).0);
        assert!(!governance_affecting(&t, &["spec/tasks/TASK-0002.yaml".into()]).0);
        let (a, why) = governance_affecting(&t, &["spec/architecture/ARCH-0001.yaml".into()]);
        assert!(a, "{why:?}");
    }

    #[test]
    fn snapshot_attributes_changes_to_classes_and_ignores_its_own_outputs() {
        let dir = std::env::temp_dir().join(format!("gov-snap-{}", crate::util::short_uuid()));
        let w = |rel: &str, text: &str| {
            let p = dir.join(rel);
            std::fs::create_dir_all(p.parent().unwrap()).unwrap();
            std::fs::write(p, text).unwrap();
        };
        w("src/lib.rs", "pub fn a() {}\n");
        w("spec/decisions/D-0001.yaml", "id: D-0001\ntype: decision\n");
        w(
            "spec/audits/AUD-0001.yaml",
            "id: AUD-0001\ntype: audit\nscope: governance-suite\n",
        );
        w("spec/audits/GOVERNANCE-ADOPTION/06.yaml", "tests: []\n");
        let p = Project::open(&dir);
        let s0 = Snapshot::take(&p).unwrap();
        assert!(s0
            .excluded
            .contains(&"spec/audits/AUD-0001.yaml".to_string()));
        // a new health output (another suite record) changes nothing
        w(
            "spec/audits/AUD-0002.yaml",
            "id: AUD-0002\ntype: audit\nscope: governance-suite\ngreen: true\n",
        );
        let s1 = Snapshot::take(&p).unwrap();
        assert_eq!(s0.key(), s1.key());
        // each input change is attributed to exactly its class
        for (rel, text, class) in [
            ("src/lib.rs", "pub fn b() {}\n", SOURCE),
            (
                "spec/decisions/D-0001.yaml",
                "id: D-0001\ntype: decision\ntitle: x\n",
                "spec_decisions",
            ),
            (
                "spec/audits/GOVERNANCE-ADOPTION/06.yaml",
                "tests: [x]\n",
                "adoption_evidence",
            ),
            (
                "spec/research/RES-1.yaml",
                "id: RES-1\n",
                "research_experiments",
            ),
        ] {
            let before = Snapshot::take(&p).unwrap();
            w(rel, text);
            let after = Snapshot::take(&p).unwrap();
            assert_ne!(before.key(), after.key(), "{rel}");
            assert_eq!(
                after.changed_classes(&before.classes_value()),
                vec![class.to_string()],
                "{rel}"
            );
            assert!(after
                .changed_paths(&before.files)
                .contains(&rel.to_string()));
        }
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn manifest_normalisation_drops_volatile_fields_only() {
        let dir = std::env::temp_dir().join(format!("gov-cur-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(dir.join("spec/audits")).unwrap();
        std::fs::write(
            dir.join("spec/audits/AUD-0001.yaml"),
            "id: AUD-0001\ntype: audit\nscope: governance-suite\n",
        )
        .unwrap();
        let a = json!({"index_version": "x", "embedder": {"id": "e"}, "built_at": "t1", "repo_commit": "c1", "counts": {"a": 1},
            "artifacts": {"spec/audits/AUD-0001.yaml": {"record_type": "audit"}, "src/lib.rs": {"content_hash": "h"}}, "excluded": []});
        let mut b = a.clone();
        b["built_at"] = json!("t2");
        b["repo_commit"] = json!("c2");
        b["counts"] = json!({"a": 2});
        b["artifacts"]["spec/audits/AUD-0001.yaml"]["content_hash"] = json!("changed");
        let rel = "governance/generated/index-manifest.json";
        assert_eq!(
            normalized_index_manifest(&dir, rel, &a),
            normalized_index_manifest(&dir, rel, &b)
        );
        let mut c = a.clone();
        c["embedder"]["id"] = json!("other");
        assert_ne!(
            normalized_index_manifest(&dir, rel, &a),
            normalized_index_manifest(&dir, rel, &c)
        );
        let mut d = a.clone();
        d["artifacts"]["src/lib.rs"]["content_hash"] = json!("h2");
        assert_ne!(
            normalized_index_manifest(&dir, rel, &a),
            normalized_index_manifest(&dir, rel, &d)
        );
        let _ = std::fs::remove_dir_all(&dir);
    }
}
