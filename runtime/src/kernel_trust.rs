//! Verified kernel trust root (verifier V-H2).
//!
//! No authority, security, privacy, human-gate, export, policy-precedence or other constitutional enforcement
//! decision may consume installed kernel content unless that content has first been authenticated against the
//! installed release identity. This module is the single canonical loading boundary:
//!
//! 1. the installed release is identified from `governance/framework.lock`;
//! 2. the installed payload is verified against its own `KERNEL_MANIFEST.json` (per-file hashes) **and** the
//!    manifest is verified against `framework.lock.kernel_manifest_hash`, so neither the files nor the manifest
//!    can be rewritten independently;
//! 3. modified / missing / added kernel content makes the installed kernel untrusted;
//! 4. only then is the installed payload used as the policy root; otherwise the immutable payload embedded in this
//!    binary is substituted explicitly (never silently mixed) and the substitution is recorded;
//! 5. mutating operations fail closed with `KERNEL_TAMPERED` until `gov kernel reinstall`, or an L4+ role answers a
//!    presented Human Decision Gate bound to the exact observed kernel state.
//!
//! Security-critical consumers (`policy::PolicySet`, `policy_precedence`, `authority`, routing, handoffs, adapters,
//! migration verification) resolve their kernel content through `trusted_root`/`policy_root` rather than reading
//! `governance/kernel/**` directly.
use crate::kernel::{
    embedded_kernel_dir, manifest_hash, read_manifest, verify_kernel, KERNEL_MANIFEST,
};
use crate::util::{read_yaml, sha256_text};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::{Mutex, OnceLock};

/// Operations that must stay available while the kernel is untrusted: the remedies and the read-only diagnostics.
const EXEMPT_OPERATIONS: &[&str] = &[
    "kernel reinstall",
    "kernel verify",
    "recover",
    "update --rollback",
    "resume",
    "pause",
    "freeze writes",
    // the human-decision channel itself: presenting and answering gates is how the override (and any other
    // remediation decision) is recorded. Everything a gate might unblock stays refused until the kernel is trusted.
    "gate present",
    "gate answer",
];

#[derive(Debug, Clone)]
pub struct KernelTrust {
    /// A kernel payload and a lock are present (an installed, governed project).
    pub installed: bool,
    /// The installed payload matches its manifest and the manifest matches the lock.
    pub verified: bool,
    /// Where constitutional content must be read from (installed payload, or the embedded baseline).
    pub policy_root: PathBuf,
    pub source: String,
    /// The embedded baseline was substituted for an untrusted installed payload.
    pub substituted: bool,
    pub problems: Vec<String>,
    pub modified: Vec<String>,
    pub missing: Vec<String>,
    pub added: Vec<String>,
    pub manifest_matches_lock: bool,
    pub installed_version: String,
    pub trusted_version: String,
    /// Identifies the exact untrusted state, so an override gate cannot outlive the state it approved.
    pub fingerprint: String,
}

impl KernelTrust {
    fn uninstalled(kernel_dir: PathBuf) -> Self {
        KernelTrust {
            installed: false,
            verified: false,
            policy_root: kernel_dir,
            source: "no installed kernel".into(),
            substituted: false,
            problems: vec![],
            modified: vec![],
            missing: vec![],
            added: vec![],
            manifest_matches_lock: false,
            installed_version: String::new(),
            trusted_version: String::new(),
            fingerprint: String::new(),
        }
    }
    pub fn to_value(&self) -> Value {
        json!({
            "installed": self.installed, "verified": self.verified, "source": self.source,
            "substituted_embedded_baseline": self.substituted, "manifest_matches_lock": self.manifest_matches_lock,
            "modified": self.modified, "missing": self.missing, "added": self.added,
            "installed_version": self.installed_version, "trusted_version": self.trusted_version,
            "problems": self.problems, "fingerprint": self.fingerprint,
        })
    }
    /// One-line diagnostic for doctor / audit / context packets.
    pub fn summary(&self) -> String {
        if !self.installed {
            return "no installed kernel".into();
        }
        if self.verified {
            return format!(
                "installed kernel {} verified against KERNEL_MANIFEST.json and framework.lock",
                self.installed_version
            );
        }
        format!(
            "installed kernel FAILED verification ({}); constitutional policy is read from the embedded baseline {} and mutating operations are refused (KERNEL_TAMPERED)",
            self.problems.join("; "),
            self.trusted_version
        )
    }
}

fn cache() -> &'static Mutex<HashMap<PathBuf, KernelTrust>> {
    static C: OnceLock<Mutex<HashMap<PathBuf, KernelTrust>>> = OnceLock::new();
    C.get_or_init(|| Mutex::new(HashMap::new()))
}

/// Drop every cached verdict. Called whenever the installed kernel or the lock changes.
pub fn clear() {
    if let Ok(mut c) = cache().lock() {
        c.clear();
    }
}

fn compute(root: &Path) -> KernelTrust {
    let kernel_dir = root.join("governance").join("kernel");
    let lock_path = root.join("governance").join("framework.lock");
    if !kernel_dir.join(KERNEL_MANIFEST).exists() || !lock_path.exists() {
        return KernelTrust::uninstalled(kernel_dir);
    }
    let mut problems = vec![];
    let (mut modified, mut missing, mut added) = (vec![], vec![], vec![]);
    let mut payload_ok = false;
    match verify_kernel(&kernel_dir) {
        Ok(v) => {
            payload_ok = v.ok;
            modified = v.modified.clone();
            missing = v.missing.clone();
            added = v.added.clone();
            if !v.ok {
                problems.push(format!(
                    "kernel payload does not match KERNEL_MANIFEST.json: modified {:?} missing {:?} added {:?}",
                    v.modified, v.missing, v.added
                ));
            }
        }
        Err(e) => problems.push(format!("kernel payload unverifiable: {e}")),
    }
    let manifest = read_manifest(&kernel_dir).unwrap_or(json!({}));
    let installed_version = manifest
        .get("version")
        .and_then(|v| v.as_str())
        .unwrap_or("unknown")
        .to_string();
    let lock = read_yaml(&lock_path).unwrap_or(json!({}));
    let lock_hash = lock
        .get("kernel_manifest_hash")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let actual_hash = manifest_hash(&manifest);
    let manifest_matches_lock = !lock_hash.is_empty() && lock_hash == actual_hash;
    if !manifest_matches_lock {
        problems.push(format!(
            "KERNEL_MANIFEST.json hash {actual_hash} does not match framework.lock.kernel_manifest_hash {}",
            if lock_hash.is_empty() { "(absent)" } else { lock_hash.as_str() }
        ));
    }
    let verified = payload_ok && manifest_matches_lock;
    let fingerprint = sha256_text(&format!(
        "{installed_version}|{actual_hash}|{lock_hash}|{modified:?}|{missing:?}|{added:?}"
    ));
    if verified {
        return KernelTrust {
            installed: true,
            verified: true,
            policy_root: kernel_dir,
            source: "installed kernel (verified)".into(),
            substituted: false,
            problems,
            modified,
            missing,
            added,
            manifest_matches_lock,
            trusted_version: installed_version.clone(),
            installed_version,
            fingerprint,
        };
    }
    // fail closed to the immutable baseline embedded in this binary — explicitly, never mixed with the untrusted one
    match embedded_kernel_dir() {
        Ok(dir) => {
            let tv = read_yaml(&dir.join("KERNEL.yaml"))
                .ok()
                .and_then(|v| {
                    v.get("version")
                        .and_then(|x| x.as_str().map(|s| s.to_string()))
                })
                .unwrap_or_else(|| crate::VERSION.to_string());
            KernelTrust {
                installed: true,
                verified: false,
                policy_root: dir,
                source: format!(
                    "embedded baseline {tv} substituted for the untrusted installed kernel {installed_version}"
                ),
                substituted: true,
                problems,
                modified,
                missing,
                added,
                manifest_matches_lock,
                installed_version,
                trusted_version: tv,
                fingerprint,
            }
        }
        Err(e) => {
            problems.push(format!(
                "embedded kernel baseline unavailable ({e}): no trusted policy source exists"
            ));
            KernelTrust {
                installed: true,
                verified: false,
                policy_root: PathBuf::from("/nonexistent-untrusted-kernel"),
                source: "no trusted kernel source".into(),
                substituted: false,
                problems,
                modified,
                missing,
                added,
                manifest_matches_lock,
                installed_version,
                trusted_version: String::new(),
                fingerprint,
            }
        }
    }
}

/// Verified trust verdict for a repository (cached per process; `clear()` on any kernel/lock change).
pub fn trust(root: &Path) -> KernelTrust {
    let key = root.to_path_buf();
    if let Ok(c) = cache().lock() {
        if let Some(t) = c.get(&key) {
            return t.clone();
        }
    }
    let t = compute(root);
    if let Ok(mut c) = cache().lock() {
        c.insert(key, t.clone());
    }
    t
}

/// The kernel root that constitutional content must be read from (verified installed payload, else the embedded
/// baseline). Every security-critical consumer uses this instead of `Project::kernel_dir()`.
pub fn trusted_root(p: &Project) -> PathBuf {
    trust(&p.root).policy_root
}

/// Same, for code that only has the repository root.
pub fn trusted_root_of(root: &Path) -> PathBuf {
    trust(root).policy_root
}

/// An L4+ role may proceed on an untrusted kernel only through a presented, answered-A gate bound to this exact
/// kernel state (`kernel_fingerprint`), so the override cannot outlive the state it approved.
fn override_gate(p: &Project, fingerprint: &str) -> Option<String> {
    let store = crate::records::RecordStore::load(&p.root);
    store
        .of_type("human-gate")
        .into_iter()
        .find(|g| {
            g.get("trigger") == "kernel_integrity_override"
                && g.data
                    .get("kernel_fingerprint")
                    .and_then(|v| v.as_str())
                    .map(|f| f == fingerprint)
                    .unwrap_or(false)
                && crate::orchestration::gates::is_answered_yes(p, &g.id())
        })
        .map(|g| g.id())
}

/// Refuse a governed operation while the installed kernel is untrusted (verifier V-H2 / VV-14).
pub fn guard(p: &Project, operation: &str) -> Result<()> {
    let t = trust(&p.root);
    if !t.installed || t.verified {
        return Ok(());
    }
    if EXEMPT_OPERATIONS.iter().any(|e| operation.contains(e)) {
        return Ok(());
    }
    let level = crate::authority::level_of(p, &p.role).unwrap_or(0);
    if level >= 4 {
        if let Some(gate) = override_gate(p, &t.fingerprint) {
            let _ = crate::observability::emit(
                p,
                "kernel_integrity_override",
                json!({"operation": operation, "gate": gate, "fingerprint": t.fingerprint, "role": p.role}),
            );
            return Ok(());
        }
    }
    Err(GovError::new(
        "KERNEL_TAMPERED",
        format!(
            "'{operation}' refused: the installed kernel does not match the release it claims to be ({}). Constitutional policy is being read from the embedded baseline; restore the payload with `gov kernel reinstall`, or have an L4+ role answer a presented kernel-integrity gate (`gov kernel override --reason ...`) bound to this exact state.",
            t.problems.join("; ")
        ),
    )
    .with_details(json!({
        "operation": operation, "kernel_trust": t.to_value(),
        "remediation": ["gov kernel verify", "gov kernel reinstall", "gov kernel override --reason <why> (L4+, raises a gate)"],
    })))
}

/// Raise (or return) the kernel-integrity override gate for the current untrusted state. L4+ only.
pub fn request_override(p: &Project, reason: Option<&str>) -> Result<Value> {
    let t = trust(&p.root);
    if t.verified {
        return Ok(json!({"override_required": false, "kernel_trust": t.to_value()}));
    }
    crate::authority::require(p, "override_kernel_integrity")?;
    if let Some(g) = override_gate(p, &t.fingerprint) {
        return Ok(json!({"override_active": true, "human_gate": g, "kernel_trust": t.to_value()}));
    }
    let g = crate::orchestration::gates::create_system(
        p,
        json!({
            "question": format!("Proceed with an installed kernel that failed verification? ({})", t.problems.join("; ")),
            "why_now": "a governed operation was refused with KERNEL_TAMPERED",
            "current_state": t.summary(),
            "options": [{"id": "A", "description": "accept this exact kernel state and continue (records the fingerprint)"}, {"id": "B", "description": "refuse; restore the payload with gov kernel reinstall"}],
            "impact": "constitutional floors are currently read from the embedded baseline, not the installed payload",
            "reversibility": "gov kernel reinstall restores the released payload",
            "recommendation": "B unless the modification is a reviewed, deliberate local change",
            "confidence": 0.4, "trigger": "kernel_integrity_override", "impact_radius": "R5",
            "kernel_fingerprint": t.fingerprint, "rationale": reason,
        }),
    )?;
    Ok(
        json!({"override_active": false, "human_gate": g["id"], "kernel_trust": t.to_value(),
        "next": ["gov gate present <id>", "gov decide <id> --option A --by <human>"]}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn uninstalled_projects_keep_the_installed_kernel_path_and_never_block() {
        let dir = std::env::temp_dir().join(format!("gov-trust-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&dir).unwrap();
        let t = trust(&dir);
        assert!(!t.installed && !t.verified && !t.substituted);
        assert!(t.policy_root.ends_with("governance/kernel"));
        clear();
        let _ = std::fs::remove_dir_all(&dir);
    }
}
