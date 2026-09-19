//! Repository contract and path map: what belongs where, what may be indexed, who may write it, what must never leave.
//!
//! **The OS's own state is classified by the kernel, not by the overlay (BC-P2-31; Contract v3 B1:188 "Generated/
//! runtime state is distinguished from authoritative tracked state", B3:202 "Deleting derived state cannot delete
//! project truth", D6:352; D-0007 T2).** The project overlay (`REPOSITORY_CONTRACT.yaml`) maps the project's layout.
//! The stores the OS itself keeps and cannot rebuild — session claims, the emergency-control state, claim-time tree
//! snapshots, rollback snapshots and the OS-written plugin registry — are declared once, in [`OS_STORES`], with the
//! location each belongs in and the location its writer used before this repair. [`RepositoryContract::decide`]
//! applies those declarations after the overlay's rules, so no overlay rule (a blanket `.governance-runtime/**:
//! derived`, `governance/generated/**: generated`) can make the product call non-rebuildable state derived or
//! generated. The declarations only ever *strengthen* (never index, never retrieve, never export, OS-only
//! mutation), and a `secret` classification still wins.
//!
//! Where the stores belong: machine-local operational state in [`STATE_DIR`] (untracked, self-ignored by Git,
//! never walked, never indexed, never deleted by a rebuild); the plugin registry at [`PLUGIN_REGISTRY_PATH`]
//! (tracked, OS-written T2). The writers are other workstreams' code: they call [`store_path`] for the location and
//! [`relocate_legacy`] once to move an existing store; [`misplaced_os_state`] reports every store still found where
//! the product (framework §81/§19) treats the directory as derived or generated.
use crate::util::{glob_match, read_yaml};
use crate::{GovError, Result};
use serde_json::{json, Map, Value};
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

pub const SECRET_CLASS: &str = "secret";
/// Non-rebuildable OS operational state: authoritative for what it records, never derived, never indexed.
pub const OPERATIONAL_CLASS: &str = "operational";
/// Directory (repository root) of the OS's non-rebuildable, machine-local operational state (BC-P2-31). It is not
/// the derived runtime directory (`crate::RUNTIME_DIR`, framework §81), which may be deleted and rebuilt.
pub const STATE_DIR: &str = ".governance-state";
/// Where the OS-written plugin registry (D-0007 T2: "authoritative project state written by the OS") belongs:
/// tracked, and outside `governance/generated/` (T3, regenerable views).
pub const PLUGIN_REGISTRY_PATH: &str = "governance/registry/plugin-registry.json";
pub const ALWAYS_EXCLUDED_DIRS: &[&str] = &[
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".governance-runtime",
    ".governance-state",
    ".venv",
    "venv",
    "target",
];

/// One store the OS keeps that cannot be rebuilt from Git and the governed records.
#[derive(Debug, Clone, Copy)]
pub struct OsStore {
    pub id: &'static str,
    pub what: &'static str,
    /// [`OPERATIONAL_CLASS`] (machine-local) or `authoritative` (tracked OS-written T2 state).
    pub class: &'static str,
    pub tracked: bool,
    /// Repository-relative globs covering the store where it belongs.
    pub patterns: &'static [&'static str],
    /// Repository-relative globs covering where its writer kept it before BC-P2-31 (inside the derived runtime
    /// directory or the generated-views directory). Classified exactly like `patterns`, so the product never calls
    /// the store derived wherever it currently is.
    pub legacy_patterns: &'static [&'static str],
    /// `(legacy path, path where it belongs)` pairs — files or directories — that [`relocate_legacy`] moves.
    pub moves: &'static [(&'static str, &'static str)],
    /// The writer that owns the store's location (it must resolve it through [`store_path`]).
    pub writer: &'static str,
}

/// The OS's non-rebuildable stores (BC-P2-31). Everything else the OS keeps under `crate::RUNTIME_DIR` is derived
/// (index, caches, packets, observations) and may be deleted and rebuilt (framework §19).
pub const OS_STORES: &[OsStore] = &[
    OsStore {
        id: "claims",
        what: "session claims (Contract v3 C1 'claims' current truth; E4)",
        class: OPERATIONAL_CLASS,
        tracked: false,
        patterns: &[".governance-state/claims.db*"],
        legacy_patterns: &[".governance-runtime/claims.db*"],
        moves: &[
            (".governance-runtime/claims.db", ".governance-state/claims.db"),
            (".governance-runtime/claims.db-wal", ".governance-state/claims.db-wal"),
            (".governance-runtime/claims.db-shm", ".governance-state/claims.db-shm"),
        ],
        writer: "memory::claims::ClaimsStore::path_for / open (WS-5)",
    },
    OsStore {
        id: "emergency-control",
        what: "emergency-control state: FREEZE_WRITES / PAUSE / CANCEL_AGENTS (framework §74)",
        class: OPERATIONAL_CLASS,
        tracked: false,
        patterns: &[".governance-state/control.json"],
        legacy_patterns: &[".governance-runtime/control.json"],
        moves: &[(
            ".governance-runtime/control.json",
            ".governance-state/control.json",
        )],
        writer: "orchestration::control::path (WS-3)",
    },
    OsStore {
        id: "claim-trees",
        what: "claim-time working-tree snapshots and carried mutations a task close attributes against",
        class: OPERATIONAL_CLASS,
        tracked: false,
        patterns: &[".governance-state/tasks", ".governance-state/tasks/**"],
        legacy_patterns: &[".governance-runtime/tasks", ".governance-runtime/tasks/**"],
        moves: &[(".governance-runtime/tasks", ".governance-state/tasks")],
        writer: "orchestration::tasks::task_runtime_dir (WS-5)",
    },
    OsStore {
        id: "cit-snapshots",
        what: "change-transaction rollback snapshots (CHANGE_POLICY.rollback)",
        class: OPERATIONAL_CLASS,
        tracked: false,
        patterns: &[".governance-state/cit", ".governance-state/cit/**"],
        legacy_patterns: &[".governance-runtime/cit", ".governance-runtime/cit/**"],
        moves: &[(".governance-runtime/cit", ".governance-state/cit")],
        writer: "cit::snapshot_dir / prune_snapshots (WS-4)",
    },
    OsStore {
        id: "update-snapshots",
        what: "framework-update rollback snapshots (gov update --rollback)",
        class: OPERATIONAL_CLASS,
        tracked: false,
        patterns: &[".governance-state/update", ".governance-state/update/**"],
        legacy_patterns: &[".governance-runtime/update", ".governance-runtime/update/**"],
        moves: &[(".governance-runtime/update", ".governance-state/update")],
        writer: "update::snapshot_dir (WS-8)",
    },
    OsStore {
        id: "migration-snapshots",
        what: "migration batch snapshots and rollback material",
        class: OPERATIONAL_CLASS,
        tracked: false,
        patterns: &[".governance-state/migration", ".governance-state/migration/**"],
        legacy_patterns: &[".governance-runtime/migration", ".governance-runtime/migration/**"],
        moves: &[(".governance-runtime/migration", ".governance-state/migration")],
        writer: "migrations::executor::snapshot_dir (WS-9)",
    },
    OsStore {
        id: "plugin-registry",
        what: "the OS-written plugin registry, the only proof of registration (D-0007 T2)",
        class: "authoritative",
        tracked: true,
        patterns: &[PLUGIN_REGISTRY_PATH],
        legacy_patterns: &["governance/generated/plugin-registry.json"],
        moves: &[(
            "governance/generated/plugin-registry.json",
            PLUGIN_REGISTRY_PATH,
        )],
        writer: "capabilities::registry::REGISTRY_PATH / path (WS-7)",
    },
];

/// The store declared under `id`.
pub fn os_store(id: &str) -> Option<&'static OsStore> {
    OS_STORES.iter().find(|s| s.id == id)
}

/// The kernel rules [`RepositoryContract::decide`] applies after the overlay's (see the module documentation).
fn os_rules() -> &'static [Value] {
    static RULES: OnceLock<Vec<Value>> = OnceLock::new();
    RULES.get_or_init(|| {
        let rule = |pattern: &str, s: Option<&OsStore>, legacy: bool| {
            let (class, id, tracked, what) = match s {
                Some(s) => (s.class, s.id, s.tracked, s.what),
                None => (
                    OPERATIONAL_CLASS,
                    "state-dir",
                    false,
                    "non-rebuildable machine-local OS operational state",
                ),
            };
            json!({"pattern": pattern, "class": class, "namespace": if tracked { "governance" } else { "runtime" },
                   "semantic_index": false, "lexical_index": false, "graph_index": false, "code_index": false,
                   "default_retrieval": false, "mutation": "os-only", "export": "denied", "rebuildable": false,
                   "os_store": id, "tracked": tracked, "legacy_location": legacy, "store": what,
                   "source": "kernel: paths::OS_STORES (BC-P2-31)"})
        };
        let mut v = vec![
            rule(STATE_DIR, None, false),
            rule(&format!("{STATE_DIR}/**"), None, false),
        ];
        for s in OS_STORES {
            for pat in s.legacy_patterns {
                v.push(rule(pat, Some(s), true));
            }
            for pat in s.patterns {
                v.push(rule(pat, Some(s), false));
            }
        }
        v
    })
}

/// The absolute location a store belongs at (its first declared move target), e.g. `store_path(root, "claims")`
/// is `<root>/.governance-state/claims.db`. Writers resolve their location here (BC-P2-31).
pub fn store_path(root: &Path, id: &str) -> Option<PathBuf> {
    os_store(id)
        .and_then(|s| s.moves.first())
        .map(|(_, to)| root.join(to))
}

/// The state directory of `root`, created on first use with a `.gitignore` that ignores its whole content, so the
/// directory never shows in `git status`, never reaches a commit and never counts as a worker mutation, whatever the
/// project's own `.gitignore` says.
pub fn ensure_state_dir(root: &Path) -> Result<PathBuf> {
    let d = root.join(STATE_DIR);
    std::fs::create_dir_all(&d)?;
    let gi = d.join(".gitignore");
    if !gi.exists() {
        std::fs::write(
            &gi,
            "# Governance OS non-rebuildable operational state (claims, emergency control, rollback snapshots).\n# Machine-local and never derived: `gov rebuild-memory` never touches it; do not delete it (BC-P2-31).\n*\n",
        )?;
    }
    Ok(d)
}

fn move_path(from: &Path, to: &Path) -> Result<()> {
    if let Some(parent) = to.parent() {
        std::fs::create_dir_all(parent)?;
    }
    if std::fs::rename(from, to).is_ok() {
        return Ok(());
    }
    // a different filesystem: copy, then remove the original
    if from.is_dir() {
        crate::util::copy_dir(from, to)?;
        std::fs::remove_dir_all(from)?;
    } else {
        std::fs::copy(from, to)?;
        std::fs::remove_file(from)?;
    }
    Ok(())
}

/// Move a store from where its writer kept it before BC-P2-31 to where it belongs. Idempotent: nothing to move is
/// `Ok(vec![])`. A legacy file whose destination already exists with identical bytes is removed; different bytes at
/// both places is `STATE_LOCATION_CONFLICT` (nothing is overwritten). The writer calls this under its own store
/// lock, before opening the store (a relocated SQLite store moves with its `-wal`/`-shm` files).
pub fn relocate_legacy(root: &Path, id: &str) -> Result<Vec<Value>> {
    let s =
        os_store(id).ok_or_else(|| GovError::new("USAGE", format!("unknown OS store '{id}'")))?;
    let mut moved = vec![];
    for (from, to) in s.moves {
        let (f, t) = (root.join(from), root.join(to));
        if !f.exists() {
            continue;
        }
        if to.starts_with(STATE_DIR) {
            ensure_state_dir(root)?;
        }
        if t.exists() {
            let same =
                f.is_file() && t.is_file() && std::fs::read(&f).ok() == std::fs::read(&t).ok();
            if !same {
                return Err(GovError::new("STATE_LOCATION_CONFLICT", format!("{} exists both at its legacy location {from} and where it belongs {to} with different content; nothing was moved or overwritten", s.what))
                    .with_details(json!({"store": s.id, "legacy": from, "location": to, "remediation": format!("keep the current copy at {to} and remove {from}, or move {from} over it after checking which one the OS last wrote")})));
            }
            std::fs::remove_file(&f)?;
            moved.push(json!({"store": s.id, "from": from, "to": to, "action": "removed identical legacy copy"}));
            continue;
        }
        move_path(&f, &t)?;
        moved.push(json!({"store": s.id, "from": from, "to": to, "action": "moved"}));
    }
    Ok(moved)
}

/// Every OS store still found where its writer kept it before BC-P2-31: inside the derived runtime directory
/// (framework §81/§19: deleted and rebuilt) or the generated-views directory. Deleting those directories would lose
/// it (A0-D6-01, A0-D6-02). Empty once every writer resolves its location through [`store_path`].
pub fn misplaced_os_state(root: &Path) -> Vec<Value> {
    let mut out = vec![];
    for s in OS_STORES {
        for (from, to) in s.moves {
            if root.join(from).exists() {
                let dir = if from.starts_with(crate::RUNTIME_DIR) {
                    "the derived runtime directory (framework §81; deleted and rebuilt under §19)"
                } else {
                    "the generated-views directory (governance/generated/, regenerable T3 views)"
                };
                out.push(json!({"store": s.id, "what": s.what, "found_at": from, "belongs_at": to, "class": s.class,
                    "writer": s.writer, "severity": "medium",
                    "message": format!("{} ({}) is kept at {from}, inside {dir}; it is non-rebuildable {} state and belongs at {to} (BC-P2-31)", s.id, s.what, s.class)}));
            }
        }
    }
    out
}

/// Every existing file under the derived runtime directory and `governance/generated/` that `contract` classifies
/// derived or generated — what framework §19's disaster-recovery procedure may delete. By construction it never
/// contains an [`OS_STORES`] file, wherever its writer keeps it.
pub fn derived_deletion_set(root: &Path, contract: &RepositoryContract) -> Vec<String> {
    let mut out = vec![];
    for base in [crate::RUNTIME_DIR, "governance/generated"] {
        let dir = root.join(base);
        if !dir.is_dir() {
            continue;
        }
        for e in walkdir::WalkDir::new(&dir)
            .sort_by_file_name()
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_type().is_file())
        {
            let rel = e
                .path()
                .strip_prefix(root)
                .unwrap_or(e.path())
                .to_string_lossy()
                .replace('\\', "/");
            if matches!(
                contract.decide(&rel).class().as_str(),
                "derived" | "generated"
            ) {
                out.push(rel);
            }
        }
    }
    out
}

#[derive(Debug, Clone)]
pub struct PathDecision {
    pub path: String,
    pub rule_pattern: Option<String>,
    pub attrs: Map<String, Value>,
}

impl PathDecision {
    pub fn class(&self) -> String {
        self.attrs
            .get("class")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown")
            .to_string()
    }
    pub fn is_secret(&self) -> bool {
        self.class() == SECRET_CLASS
            || self.attrs.get("sensitivity").and_then(|v| v.as_str()) == Some("secret")
    }
    /// Never read/indexed: secret-class or a sensitivity class in SECURITY_POLICY.never_index_classes.
    pub fn is_never_index(&self) -> bool {
        self.is_secret()
            || self
                .attrs
                .get("never_index")
                .and_then(|v| v.as_bool())
                .unwrap_or(false)
    }
    pub fn sensitivity(&self) -> String {
        self.str("sensitivity")
    }
    pub fn export_allowed(&self) -> bool {
        self.attrs.get("export").and_then(|v| v.as_str()) == Some("allowed")
    }
    pub fn flag(&self, key: &str) -> bool {
        if self.is_secret() && key.ends_with("_index") {
            return false;
        }
        self.attrs
            .get(key)
            .and_then(|v| v.as_bool())
            .unwrap_or(false)
    }
    pub fn str(&self, key: &str) -> String {
        self.attrs
            .get(key)
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string()
    }
    pub fn namespace(&self) -> String {
        self.str("namespace")
    }
    pub fn default_retrieval(&self) -> bool {
        self.attrs
            .get("default_retrieval")
            .and_then(|v| v.as_bool())
            .unwrap_or(true)
            && !self.is_secret()
    }
}

fn class_defaults(cls: &str) -> Value {
    match cls {
        "source" => {
            json!({"semantic_index": true, "lexical_index": true, "graph_index": true, "code_index": true})
        }
        "test" => {
            json!({"semantic_index": true, "lexical_index": true, "graph_index": true, "code_index": true})
        }
        "authoritative" => {
            json!({"semantic_index": true, "lexical_index": true, "graph_index": true})
        }
        "evidence" => json!({"semantic_index": true, "lexical_index": true, "graph_index": true}),
        "narrative" => json!({"semantic_index": true, "lexical_index": true}),
        "derived" => json!({"semantic_index": false, "lexical_index": false, "graph_index": false}),
        "generated" => {
            json!({"semantic_index": false, "lexical_index": false, "graph_index": false, "mutation": "generated"})
        }
        "historical" => {
            json!({"semantic_index": false, "lexical_index": true, "default_retrieval": false, "mutation": "restricted"})
        }
        "secret" => {
            json!({"semantic_index": false, "lexical_index": false, "graph_index": false, "code_index": false, "default_retrieval": false,
                           "agent_read": "prohibited", "export": "denied", "sensitivity": "secret", "namespace": "secret"})
        }
        "runtime-data" => {
            json!({"semantic_index": false, "lexical_index": false, "graph_index": false})
        }
        OPERATIONAL_CLASS => {
            json!({"semantic_index": false, "lexical_index": false, "graph_index": false, "code_index": false,
                   "default_retrieval": false, "mutation": "os-only", "export": "denied"})
        }
        "devops" => json!({"semantic_index": true, "lexical_index": true}),
        "tooling" => json!({"semantic_index": true, "lexical_index": true, "code_index": true}),
        _ => json!({}),
    }
}

fn base_defaults() -> Map<String, Value> {
    json!({"class": "unknown", "semantic_index": false, "lexical_index": false, "graph_index": false, "code_index": false,
           "default_retrieval": true, "mutation": "allowed", "agent_read": "allowed", "export": "denied",
           "sensitivity": "internal", "namespace": "unknown"}).as_object().unwrap().clone()
}

/// Sensitivity enforcement inputs (SECURITY_POLICY + DATA_SENSITIVITY + ARCHIVE_POLICY).
#[derive(Debug, Clone, Default)]
pub struct SensitivityRules {
    pub classifications: Vec<(String, String)>, // (pattern, class)
    pub never_index: Vec<String>,
    pub never_export: Vec<String>,
    pub archive_default_retrieval: Option<bool>,
    pub secret_agent_read: Option<String>,
}

pub fn sensitivity_rank(class: &str) -> u8 {
    match class {
        "secret" => 4,
        "restricted" => 3,
        "confidential" => 2,
        "internal" => 1,
        _ => 0,
    }
}

#[derive(Debug, Clone)]
pub struct RepositoryContract {
    pub data: Value,
    pub roots: Vec<(String, String)>,
    pub rules: Vec<Value>,
    pub sensitivity: SensitivityRules,
}

impl RepositoryContract {
    pub fn new(data: Value) -> Self {
        let mut roots = vec![];
        if let Some(m) = data.get("roots").and_then(|r| r.as_object()) {
            for (k, v) in m {
                let s = v.as_str().unwrap_or("").trim_end_matches('/').to_string() + "/";
                roots.push((k.clone(), s));
            }
        }
        let rules = data
            .get("paths")
            .and_then(|p| p.as_array())
            .cloned()
            .unwrap_or_default();
        RepositoryContract {
            data,
            roots,
            rules,
            sensitivity: SensitivityRules::default(),
        }
    }
    pub fn with_sensitivity(mut self, rules: SensitivityRules) -> Self {
        self.sensitivity = rules;
        self
    }
    pub fn load(p: &Path) -> Result<Self> {
        Ok(Self::new(read_yaml(p)?))
    }
    pub fn root(&self, name: &str) -> String {
        self.roots
            .iter()
            .find(|(k, _)| k == name)
            .map(|(_, v)| v.clone())
            .unwrap_or(format!("{name}/"))
    }
    pub fn namespace_for(&self, path: &str) -> String {
        for (name, root) in &self.roots {
            if path.starts_with(root.as_str()) {
                return name.clone();
            }
        }
        "root".to_string()
    }
    /// Ordered rules; later rules override earlier ones. A `secret` classification can never be downgraded. The
    /// kernel's classification of the OS's own non-rebuildable stores ([`OS_STORES`]) is applied after the
    /// overlay's rules, so the overlay cannot classify them derived or generated (BC-P2-31).
    pub fn decide(&self, path: &str) -> PathDecision {
        let path = path.replace('\\', "/");
        let path = path.trim_start_matches("./").to_string();
        let mut attrs = base_defaults();
        let mut matched: Option<String> = None;
        let mut secret_locked = false;
        for rule in self.rules.iter().chain(os_rules().iter()) {
            let pat = rule.get("pattern").and_then(|v| v.as_str()).unwrap_or("");
            if pat.is_empty() || !glob_match(pat, &path) {
                continue;
            }
            let cls = rule
                .get("class")
                .and_then(|v| v.as_str())
                .unwrap_or("unknown");
            if secret_locked && cls != SECRET_CLASS {
                continue;
            }
            let mut merged = base_defaults();
            if let Some(cd) = class_defaults(cls).as_object() {
                for (k, v) in cd {
                    merged.insert(k.clone(), v.clone());
                }
            }
            if let Some(r) = rule.as_object() {
                for (k, v) in r {
                    if k != "pattern" {
                        merged.insert(k.clone(), v.clone());
                    }
                }
            }
            attrs = merged;
            matched = Some(pat.to_string());
            if cls == SECRET_CLASS {
                secret_locked = true;
            }
        }
        let ns = attrs
            .get("namespace")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown")
            .to_string();
        if ns == "unknown" || ns.is_empty() {
            attrs.insert("namespace".into(), Value::String(self.namespace_for(&path)));
        }
        // --- sensitivity: DATA_SENSITIVITY classifications (highest class wins) + SECURITY_POLICY never_index / never_export
        let mut sensitivity = attrs
            .get("sensitivity")
            .and_then(|v| v.as_str())
            .unwrap_or("internal")
            .to_string();
        for (pat, cls) in &self.sensitivity.classifications {
            if glob_match(pat, &path) && sensitivity_rank(cls) > sensitivity_rank(&sensitivity) {
                sensitivity = cls.clone();
            }
        }
        if attrs.get("class").and_then(|v| v.as_str()) == Some(SECRET_CLASS) {
            sensitivity = "secret".into();
        }
        attrs.insert("sensitivity".into(), Value::String(sensitivity.clone()));
        if self
            .sensitivity
            .never_index
            .iter()
            .any(|c| c == &sensitivity)
        {
            for k in [
                "semantic_index",
                "lexical_index",
                "graph_index",
                "code_index",
            ] {
                attrs.insert(k.into(), Value::Bool(false));
            }
            attrs.insert("default_retrieval".into(), Value::Bool(false));
            attrs.insert("export".into(), Value::String("denied".into()));
            let ar = if sensitivity == "secret" {
                self.sensitivity
                    .secret_agent_read
                    .clone()
                    .unwrap_or("prohibited".into())
            } else {
                "restricted".into()
            };
            attrs.insert("agent_read".into(), Value::String(ar));
            attrs.insert("never_index".into(), Value::Bool(true));
        }
        if self
            .sensitivity
            .never_export
            .iter()
            .any(|c| c == &sensitivity)
        {
            attrs.insert("export".into(), Value::String("denied".into()));
        }
        if attrs.get("class").and_then(|v| v.as_str()) == Some("historical") {
            if let Some(dr) = self.sensitivity.archive_default_retrieval {
                if attrs.get("default_retrieval").is_none() || matched.is_none() {
                    attrs.insert("default_retrieval".into(), Value::Bool(dr));
                }
            }
        }
        PathDecision {
            path,
            rule_pattern: matched,
            attrs,
        }
    }
    /// **Rules that never decide anything** (the class of WS-6 r2 O-1): under last-match semantics a rule is dead
    /// when a LATER rule matches every path it matches and says something else — `spec/reports/**: evidence` listed
    /// before `spec/**: authoritative` makes every report authoritative, and the path map states a classification
    /// the product never applies. Judged for the area form rule lists use (`prefix/**`, and `**`); a `secret` rule is
    /// never shadowed (a secret classification always wins). Each finding names the dead rule, the rule that
    /// overrides it and what the product applies instead — the input for a doctor/audit finding (WS-2) and for a
    /// migration that reorders an installed contract (WS-9).
    pub fn shadowed_rules(&self) -> Vec<Value> {
        let literal = |p: &str| -> String {
            p.chars()
                .take_while(|c| !matches!(c, '*' | '?' | '['))
                .collect()
        };
        let covers = |general: &str, specific: &str| -> bool {
            if general == "**" {
                return true;
            }
            match general.strip_suffix("/**") {
                Some(gp) if !gp.contains(['*', '?', '[']) => {
                    literal(specific).starts_with(&format!("{gp}/"))
                }
                _ => false,
            }
        };
        let attrs = |r: &Value| -> Value {
            let mut o = r.as_object().cloned().unwrap_or_default();
            o.shift_remove("pattern");
            o.shift_remove("owner_role");
            Value::Object(o)
        };
        let mut out = vec![];
        for (i, a) in self.rules.iter().enumerate() {
            let pa = a.get("pattern").and_then(|v| v.as_str()).unwrap_or("");
            if pa.is_empty() || a.get("class").and_then(|v| v.as_str()) == Some(SECRET_CLASS) {
                continue;
            }
            if let Some(b) = self.rules[i + 1..].iter().rev().find(|b| {
                let pb = b.get("pattern").and_then(|v| v.as_str()).unwrap_or("");
                covers(pb, pa) && attrs(b) != attrs(a)
            }) {
                let pb = b.get("pattern").and_then(|v| v.as_str()).unwrap_or("");
                out.push(json!({"rule": pa, "class": a.get("class"), "overridden_by": pb, "applied_class": b.get("class"),
                    "message": format!("repository-contract rule `{pa}` ({}) never decides a path: the later rule `{pb}` matches every path it matches and applies {} (rules are last-match: list a specific rule after the general rule it refines)",
                        a.get("class").and_then(|v| v.as_str()).unwrap_or("?"), b.get("class").and_then(|v| v.as_str()).unwrap_or("?"))}));
            }
        }
        out
    }
    pub fn to_framework_json(&self, framework: &str, version: &str) -> Value {
        let mut paths = Map::new();
        for r in &self.rules {
            if let (Some(pat), Some(obj)) =
                (r.get("pattern").and_then(|v| v.as_str()), r.as_object())
            {
                let mut o = obj.clone();
                o.shift_remove("pattern");
                paths.insert(pat.to_string(), Value::Object(o));
            }
        }
        let mut roots = Map::new();
        for (k, v) in &self.roots {
            roots.insert(k.clone(), Value::String(v.clone()));
        }
        // BC-P2-31 (WS-6 IP-R2-11): the projection states the classification the product applies, including the
        // kernel's classification of its own non-rebuildable stores, which no overlay rule can override
        let mut kernel_paths = Map::new();
        for r in os_rules() {
            if let (Some(pat), Some(obj)) =
                (r.get("pattern").and_then(|v| v.as_str()), r.as_object())
            {
                let mut o = obj.clone();
                o.shift_remove("pattern");
                kernel_paths.insert(pat.to_string(), Value::Object(o));
            }
        }
        json!({"framework": framework, "version": version, "generated": true, "source": "governance/project/REPOSITORY_CONTRACT.yaml",
               "governance_dir": "governance", "roots": roots, "paths": paths, "kernel_paths": kernel_paths,
               "precedence": "for each path the last matching rule of `paths` decides; the rules of `kernel_paths` (paths::OS_STORES, the OS's own non-rebuildable stores) apply after them; a `secret` classification always wins"})
    }
}

/// Deterministically list repository files (sorted), skipping VCS/runtime/cache directories.
pub fn iter_repo_files(root: &Path, include_runtime: bool) -> Vec<(PathBuf, String)> {
    let mut out = vec![];
    let walker = walkdir::WalkDir::new(root)
        .sort_by_file_name()
        .into_iter()
        .filter_entry(|e| {
            if e.depth() == 0 {
                return true;
            }
            let name = e.file_name().to_string_lossy();
            if e.file_type().is_dir() {
                if name == ".governance-runtime" {
                    return include_runtime;
                }
                return !ALWAYS_EXCLUDED_DIRS.contains(&name.as_ref());
            }
            true
        });
    for entry in walker.filter_map(|e| e.ok()) {
        if entry.file_type().is_file() && !entry.path_is_symlink() {
            let rel = entry
                .path()
                .strip_prefix(root)
                .unwrap()
                .to_string_lossy()
                .replace('\\', "/");
            out.push((entry.path().to_path_buf(), rel));
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    fn contract() -> RepositoryContract {
        RepositoryContract::new(
            json!({"roots": {"governance": "governance/", "spec": "spec/", "product": "product/", "archive": "archive/"},
            "paths": [{"pattern": "spec/**", "class": "authoritative"}, {"pattern": "product/**", "class": "source"}, {"pattern": "**/.env*", "class": "secret"}, {"pattern": "product/secrets/**", "class": "secret"}, {"pattern": "product/**", "class": "source", "semantic_index": true}, {"pattern": "archive/**", "class": "historical"}]}),
        )
    }
    #[test]
    fn secret_classification_can_never_be_downgraded() {
        let c = contract();
        let d = c.decide("product/secrets/key.pem");
        assert!(
            d.is_secret()
                && !d.flag("semantic_index")
                && !d.flag("lexical_index")
                && d.str("agent_read") == "prohibited"
        );
        assert!(c.decide("product/.env.prod").is_secret());
        let s = c.decide("product/app.py");
        assert_eq!(s.class(), "source");
        assert!(s.flag("code_index") && s.flag("semantic_index"));
        let a = c.decide("archive/old.md");
        assert!(!a.default_retrieval() && a.class() == "historical" && a.flag("lexical_index"));
        assert_eq!(c.decide("spec/x.yaml").namespace(), "spec");
        assert_eq!(c.decide("README.md").class(), "unknown");
    }

    fn tmp(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!(
            "gov-paths-{tag}-{}-{}",
            std::process::id(),
            crate::util::short_uuid()
        ));
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    /// BC-P2-31: wherever a non-rebuildable OS store is (where its writer kept it before the repair, or where it
    /// belongs), the product never classifies it derived or generated — not under the shipped template (whose
    /// blanket rules call `.governance-runtime/**` derived and `governance/generated/**` generated) and not under an
    /// overlay that tries to; while everything else in those directories stays derived/generated.
    #[test]
    fn os_stores_are_never_classified_derived_or_generated() {
        let shipped: Value = serde_yaml::from_str(include_str!(
            "../../framework/overlay-templates/REPOSITORY_CONTRACT.yaml"
        ))
        .unwrap();
        let hostile = json!({"paths": [{"pattern": "**", "class": "derived"}, {"pattern": ".governance-state/**", "class": "derived"},
            {"pattern": "governance/**", "class": "generated"}, {"pattern": ".governance-runtime/**", "class": "derived"}]});
        for data in [shipped, hostile] {
            let c = RepositoryContract::new(data);
            for s in OS_STORES {
                let mut paths: Vec<String> = s
                    .moves
                    .iter()
                    .flat_map(|(a, b)| [a.to_string(), b.to_string()])
                    .collect();
                paths.extend(
                    [
                        "claims.db",
                        "tasks/TASK-0001/claim-tree.json",
                        "cit/CIT-0001/snapshot/x.yaml",
                    ]
                    .iter()
                    .map(|f| format!("{STATE_DIR}/{f}")),
                );
                for path in paths {
                    let probe = if path.ends_with("/tasks")
                        || path.ends_with("/cit")
                        || path.ends_with("/update")
                        || path.ends_with("/migration")
                    {
                        format!("{path}/x/y.json")
                    } else {
                        path.clone()
                    };
                    let d = c.decide(&probe);
                    assert!(
                        !matches!(d.class().as_str(), "derived" | "generated"),
                        "{} at {probe} classified {}",
                        s.id,
                        d.class()
                    );
                    assert!(
                        !d.flag("semantic_index")
                            && !d.flag("lexical_index")
                            && !d.default_retrieval()
                            && d.str("mutation") == "os-only",
                        "{probe}: {:?}",
                        d.attrs
                    );
                }
            }
            assert_eq!(
                c.decide(&format!("{STATE_DIR}/anything.bin")).class(),
                OPERATIONAL_CLASS
            );
        }
        // the rest of the runtime and generated directories keep the overlay's classification
        let c = RepositoryContract::new(
            serde_yaml::from_str(include_str!(
                "../../framework/overlay-templates/REPOSITORY_CONTRACT.yaml"
            ))
            .unwrap(),
        );
        assert_eq!(c.decide(".governance-runtime/state.db").class(), "derived");
        assert_eq!(
            c.decide(".governance-runtime/context/TASK-1.json").class(),
            "derived"
        );
        assert_eq!(
            c.decide("governance/generated/index-manifest.json").class(),
            "generated"
        );
        assert_eq!(
            c.decide("governance/generated/plugin-registry.json")
                .class(),
            "authoritative"
        );
        // a secret classification still wins over the kernel store rules
        let s = RepositoryContract::new(
            json!({"paths": [{"pattern": ".governance-state/**", "class": "secret"}]}),
        );
        assert!(s.decide(".governance-state/control.json").is_secret());
    }

    /// BC-P2-31 (repair-1 round 3, WS-6 IP-R2-11 / WS-9 IP-R2-2): the shipped repository-contract template states the
    /// classification the product applies — under ANY reading of its rules (every matching rule, not only the last)
    /// no location of an OS store is derived or generated; the specific rules that refine a general one come after it
    /// and so take effect (the evidence areas of spec/, product tests); retrieval-miss records are never indexed; the
    /// template is valid against the repository-contract schema; framework.json projects the kernel store rules.
    #[test]
    fn the_shipped_template_states_the_store_classification_under_any_reading() {
        let tpl: Value = serde_yaml::from_str(include_str!(
            "../../framework/overlay-templates/REPOSITORY_CONTRACT.yaml"
        ))
        .unwrap();
        let rules = tpl["paths"].as_array().unwrap();
        for s in OS_STORES {
            for (legacy, target) in s.moves {
                for rel in [legacy, target] {
                    let probe = if rel.rsplit('/').next().unwrap_or("").contains('.') {
                        rel.to_string()
                    } else {
                        format!("{rel}/x.json")
                    };
                    let classes: Vec<&str> = rules
                        .iter()
                        .filter(|r| glob_match(r["pattern"].as_str().unwrap_or(""), &probe))
                        .map(|r| r["class"].as_str().unwrap_or(""))
                        .collect();
                    assert!(
                        !classes.is_empty()
                            && classes
                                .iter()
                                .all(|c| !matches!(*c, "derived" | "generated")),
                        "{} at {probe}: {classes:?}",
                        s.id
                    );
                }
            }
        }
        let c = RepositoryContract::new(tpl.clone());
        for (path, class) in [
            ("spec/reports/checkpoints/CKPT-00001.yaml", "evidence"),
            ("spec/lessons/L-0001.yaml", "evidence"),
            ("spec/research/RES-0001.yaml", "evidence"),
            ("spec/experiments/EXP-0001.yaml", "evidence"),
            ("spec/audits/AUD-0001.yaml", "evidence"),
            ("spec/requirements/REQ-0001.yaml", "authoritative"),
            ("product/tests/test_a.py", "test"),
            ("product/a.py", "source"),
            (".governance-runtime/state.db-wal", "derived"),
            (".governance-runtime/telemetry/events.jsonl", "runtime-data"),
            ("governance/generated/adapter-manifest.json", "generated"),
            ("governance/generated/adapters/ide/RULES.md", "generated"),
        ] {
            assert_eq!(c.decide(path).class(), class, "{path}");
        }
        let mq = c.decide("spec/reports/memory-quality/FAIL-0001.yaml");
        assert_eq!(mq.class(), "evidence");
        for f in [
            "semantic_index",
            "lexical_index",
            "graph_index",
            "code_index",
        ] {
            assert!(!mq.flag(f), "{f}");
        }
        let reg = crate::schemas::SchemaRegistry::new(
            &Path::new(env!("CARGO_MANIFEST_DIR")).join("../framework/schemas"),
        );
        let errs = reg.errors("repository-contract", &tpl).unwrap();
        assert!(errs.is_empty(), "{errs:?}");
        let fj = c.to_framework_json("fw", "1");
        assert_eq!(
            fj["kernel_paths"][".governance-runtime/control.json"]["class"],
            OPERATIONAL_CLASS
        );
        assert_eq!(
            fj["kernel_paths"][PLUGIN_REGISTRY_PATH]["class"],
            "authoritative"
        );
        assert!(fj["paths"].get("spec/**").is_some());
        // no rule of the shipped template is dead; the template before this repair had shadowed rules (O-1)
        assert!(c.shadowed_rules().is_empty(), "{:?}", c.shadowed_rules());
        let old = RepositoryContract::new(json!({"paths": [
            {"pattern": "spec/reports/**", "class": "evidence"}, {"pattern": "spec/research/**", "class": "evidence"},
            {"pattern": "spec/**", "class": "authoritative"}, {"pattern": "product/tests/**", "class": "test"},
            {"pattern": "product/**", "class": "source"}, {"pattern": "**/.env*", "class": "secret"}]}));
        let dead: Vec<String> = old
            .shadowed_rules()
            .iter()
            .map(|f| {
                format!(
                    "{}<{}",
                    f["rule"].as_str().unwrap(),
                    f["overridden_by"].as_str().unwrap()
                )
            })
            .collect();
        assert_eq!(
            dead,
            vec![
                "spec/reports/**<spec/**",
                "spec/research/**<spec/**",
                "product/tests/**<product/**"
            ]
        );
    }

    /// BC-P2-31 tripwire (repair-1 round 3): wherever the writers that expose their location keep a store — today's
    /// location, or [`store_path`] once they move (WS-3/WS-5/WS-7/WS-9, round 3) — the product classifies it as the
    /// store it is, never derived or generated, under the shipped template and a hostile overlay. A writer that moved a
    /// store somewhere [`OS_STORES`] does not declare fails here.
    #[test]
    fn every_writer_location_is_classified_as_its_store() {
        let root = tmp("writers");
        let p = crate::Project::open(&root);
        let rel = |abs: PathBuf| -> String {
            abs.strip_prefix(&root)
                .unwrap_or(&abs)
                .to_string_lossy()
                .replace('\\', "/")
        };
        let mut located: Vec<(&str, String)> = vec![
            (
                "claims",
                rel(crate::memory::claims::ClaimsStore::path_for(&p)),
            ),
            (
                "emergency-control",
                rel(crate::orchestration::control::path(&p)),
            ),
            (
                "plugin-registry",
                rel(crate::capabilities::registry::path(&p)),
            ),
            (
                "migration-snapshots",
                rel(crate::migrations::executor::snapshot_dir(&root, 3).join("x.json")),
            ),
        ];
        for s in OS_STORES {
            let to = store_path(&root, s.id).unwrap();
            let probe = if to.extension().is_some() {
                to
            } else {
                to.join("X-0001/snapshot.json")
            };
            located.push((s.id, rel(probe)));
        }
        let shipped: Value = serde_yaml::from_str(include_str!(
            "../../framework/overlay-templates/REPOSITORY_CONTRACT.yaml"
        ))
        .unwrap();
        let hostile = json!({"paths": [{"pattern": "**", "class": "derived"}, {"pattern": "governance/**", "class": "generated"}]});
        for data in [shipped, hostile] {
            let c = RepositoryContract::new(data);
            for (id, path) in &located {
                let d = c.decide(path);
                let want = os_store(id).unwrap().class;
                assert_eq!(d.class(), want, "{id} at {path}");
                assert_eq!(d.str("os_store"), *id, "{id} at {path}");
            }
        }
        let _ = std::fs::remove_dir_all(&root);
    }

    #[test]
    fn legacy_stores_relocate_and_are_reported_until_moved() {
        let root = tmp("reloc");
        let rt = root.join(crate::RUNTIME_DIR);
        std::fs::create_dir_all(rt.join("cit/CIT-0001/snapshot")).unwrap();
        std::fs::write(rt.join("claims.db"), b"claims").unwrap();
        std::fs::write(rt.join("control.json"), b"{\"mode\":\"FROZEN\"}").unwrap();
        std::fs::write(rt.join("cit/CIT-0001/snapshot/a.yaml"), b"a").unwrap();
        std::fs::write(rt.join("state.db"), b"index").unwrap();
        let found: Vec<String> = misplaced_os_state(&root)
            .iter()
            .map(|f| f["store"].as_str().unwrap().to_string())
            .collect();
        assert_eq!(found, vec!["claims", "emergency-control", "cit-snapshots"]);
        let c = RepositoryContract::new(
            json!({"paths": [{"pattern": ".governance-runtime/**", "class": "derived"}]}),
        );
        assert_eq!(
            derived_deletion_set(&root, &c),
            vec![".governance-runtime/state.db".to_string()]
        );
        for id in ["claims", "emergency-control", "cit-snapshots"] {
            assert!(!relocate_legacy(&root, id).unwrap().is_empty());
        }
        assert!(misplaced_os_state(&root).is_empty());
        assert_eq!(
            std::fs::read(store_path(&root, "claims").unwrap()).unwrap(),
            b"claims"
        );
        assert!(root
            .join(".governance-state/cit/CIT-0001/snapshot/a.yaml")
            .is_file());
        assert!(
            std::fs::read_to_string(root.join(".governance-state/.gitignore"))
                .unwrap()
                .lines()
                .any(|l| l.trim() == "*")
        );
        // idempotent; a second, different copy at the old place is a typed conflict and nothing is overwritten
        assert!(relocate_legacy(&root, "claims").unwrap().is_empty());
        std::fs::write(rt.join("claims.db"), b"other").unwrap();
        let e = relocate_legacy(&root, "claims").unwrap_err();
        assert_eq!(e.code, "STATE_LOCATION_CONFLICT");
        assert_eq!(
            std::fs::read(root.join(".governance-state/claims.db")).unwrap(),
            b"claims"
        );
        // an identical legacy copy is simply removed
        std::fs::write(rt.join("claims.db"), b"claims").unwrap();
        relocate_legacy(&root, "claims").unwrap();
        assert!(!rt.join("claims.db").exists());
        let _ = std::fs::remove_dir_all(&root);
    }
}
