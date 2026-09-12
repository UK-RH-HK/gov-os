//! Project context: locates governance dirs and loads lock/kernel/overlay/policies/contract lazily.
use crate::kernel::{read_manifest, KERNEL_MANIFEST};
use crate::lock::read_lock;
use crate::paths::RepositoryContract;
use crate::policy::{load_overlay, Overlay, PolicySet};
use crate::schemas::SchemaRegistry;
use crate::security::secrets::SecretScanner;
use crate::util::{new_session_id, str_of};
use crate::{GovError, Result, RUNTIME_DIR};
use serde_json::Value;
use std::cell::OnceCell;
use std::path::{Path, PathBuf};
use std::process::Command;

pub fn find_root(start: &Path) -> Option<PathBuf> {
    let mut cur = Some(start.to_path_buf());
    while let Some(p) = cur {
        if p.join("governance").join("framework.lock").exists() {
            return Some(p);
        }
        cur = p.parent().map(|x| x.to_path_buf());
    }
    None
}

pub struct Project {
    pub root: PathBuf,
    pub session_id: String,
    pub role: String,
    lock: OnceCell<Value>,
    manifest: OnceCell<Value>,
    schemas: OnceCell<SchemaRegistry>,
    overlay: OnceCell<Overlay>,
    policies: OnceCell<PolicySet>,
    contract: OnceCell<RepositoryContract>,
    scanner: OnceCell<SecretScanner>,
}

impl Project {
    pub fn open(root: &Path) -> Self {
        let root = root.canonicalize().unwrap_or(root.to_path_buf());
        let session_id = std::env::var("GOV_SESSION").ok().filter(|s| !s.is_empty()).unwrap_or_else(new_session_id);
        let role = std::env::var("GOV_ROLE").ok().filter(|s| !s.is_empty()).unwrap_or_else(|| "orchestrator".into());
        Project { root, session_id, role, lock: OnceCell::new(), manifest: OnceCell::new(), schemas: OnceCell::new(), overlay: OnceCell::new(),
                  policies: OnceCell::new(), contract: OnceCell::new(), scanner: OnceCell::new() }
    }
    pub fn with_session(mut self, session: Option<String>, role: Option<String>) -> Self {
        if let Some(s) = session { self.session_id = s; }
        if let Some(r) = role { self.role = r; }
        self
    }
    pub fn governance_dir(&self) -> PathBuf { self.root.join("governance") }
    pub fn kernel_dir(&self) -> PathBuf { self.governance_dir().join("kernel") }
    pub fn overlay_dir(&self) -> PathBuf { self.governance_dir().join("project") }
    pub fn generated_dir(&self) -> PathBuf { self.governance_dir().join("generated") }
    pub fn lock_path(&self) -> PathBuf { self.governance_dir().join("framework.lock") }
    pub fn runtime_dir(&self) -> PathBuf { self.root.join(RUNTIME_DIR) }
    pub fn spec_dir(&self) -> PathBuf { self.root.join("spec") }
    pub fn db_path(&self) -> PathBuf { self.runtime_dir().join("state.db") }

    pub fn is_installed(&self) -> bool {
        self.lock_path().exists() && self.kernel_dir().join(KERNEL_MANIFEST).exists()
    }
    pub fn require_installed(&self) -> Result<()> {
        if self.is_installed() { Ok(()) } else { Err(GovError::new("NOT_INSTALLED", format!("no Governance OS installation at {} (run gov init or gov adopt)", self.root.display()))) }
    }
    pub fn lock(&self) -> Result<&Value> {
        if self.lock.get().is_none() { let v = read_lock(&self.lock_path())?; let _ = self.lock.set(v); }
        Ok(self.lock.get().unwrap())
    }
    pub fn kernel_manifest(&self) -> Result<&Value> {
        if self.manifest.get().is_none() { let v = read_manifest(&self.kernel_dir())?; let _ = self.manifest.set(v); }
        Ok(self.manifest.get().unwrap())
    }
    pub fn schemas(&self) -> &SchemaRegistry {
        self.schemas.get_or_init(|| {
            let sd = self.kernel_dir().join("schemas");
            if sd.exists() { SchemaRegistry::new(&sd) } else {
                let fallback = crate::kernel::canonical_root().map(|r| r.join("framework").join("schemas")).unwrap_or(sd);
                SchemaRegistry::new(&fallback)
            }
        })
    }
    pub fn overlay(&self) -> &Overlay {
        self.overlay.get_or_init(|| load_overlay(&self.overlay_dir(), Some(self.schemas())))
    }
    pub fn policies(&self) -> &PolicySet {
        self.policies.get_or_init(|| PolicySet::load(&self.kernel_dir(), self.overlay(), self.schemas()))
    }
    pub fn contract(&self) -> &RepositoryContract {
        self.contract.get_or_init(|| RepositoryContract::new(self.overlay().get("REPOSITORY_CONTRACT.yaml")))
    }
    pub fn project_policy(&self) -> Value { self.overlay().get("PROJECT_POLICY.yaml") }
    pub fn secret_scanner(&self) -> &SecretScanner {
        self.scanner.get_or_init(|| {
            let sec = self.policies().effective.get("SECURITY_POLICY").cloned().unwrap_or(Value::Null);
            SecretScanner::from_policies(&sec, &self.overlay().get("DATA_SENSITIVITY.yaml"))
        })
    }
    pub fn project_name(&self) -> String {
        let pp = self.project_policy();
        let n = pp.get("project").map(|p| str_of(p, "name")).unwrap_or_default();
        if n.is_empty() { self.root.file_name().map(|f| f.to_string_lossy().to_string()).unwrap_or("project".into()) } else { n }
    }
    pub fn project_alias(&self) -> String {
        let pp = self.project_policy();
        let a = pp.get("project").map(|p| str_of(p, "alias")).unwrap_or_default();
        if a.is_empty() { "project-alias".into() } else { a }
    }
    pub fn framework_version(&self) -> String { self.lock().map(|l| str_of(l, "version")).unwrap_or_default() }
    /// Drop cached state after mutations to governance/.
    pub fn invalidate(&mut self) {
        self.lock = OnceCell::new(); self.manifest = OnceCell::new(); self.overlay = OnceCell::new();
        self.policies = OnceCell::new(); self.contract = OnceCell::new(); self.scanner = OnceCell::new();
    }
    // --- git ---
    pub fn git(&self, args: &[&str]) -> (i32, String, String) {
        match Command::new("git").args(args).current_dir(&self.root).output() {
            Ok(o) => (o.status.code().unwrap_or(-1), String::from_utf8_lossy(&o.stdout).trim().to_string(), String::from_utf8_lossy(&o.stderr).trim().to_string()),
            Err(e) => (-1, String::new(), e.to_string()),
        }
    }
    pub fn git_available(&self) -> bool { self.git(&["rev-parse", "--is-inside-work-tree"]).0 == 0 }
    pub fn git_commit(&self) -> String { let (c, out, _) = self.git(&["rev-parse", "HEAD"]); if c == 0 && !out.is_empty() { out } else { "unknown".into() } }
    pub fn git_branch(&self) -> String { let (c, out, _) = self.git(&["rev-parse", "--abbrev-ref", "HEAD"]); if c == 0 { out } else { "unknown".into() } }
    pub fn git_dirty_files(&self) -> Vec<String> {
        let (c, out, _) = self.git(&["status", "--porcelain"]);
        if c != 0 { return vec![]; }
        out.lines().filter(|l| l.len() > 3).map(|l| l[3..].trim().to_string()).collect()
    }
}
