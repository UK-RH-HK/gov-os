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
//! **`BC-P2-35` — intact against a record the repository cannot rewrite.** Steps 1-3 compare three files that all
//! live in the project, so a mutually consistent rewrite of payload, `KERNEL_MANIFEST.json` and `framework.lock`
//! passed them (A0-A2-01). The installed payload is now also measured against this machine's own protected
//! installation record ([`crate::srr::installation`]), by digest and only by digest (ARCH-0003 §2):
//!
//! * the record binds the measured payload → intact;
//! * the record names a different payload and this machine holds a trust anchor → the kernel is not intact
//!   (`KERNEL_TAMPERED`), whatever the manifest and the lock say, and the files that differ are named;
//! * no record binds it and this machine holds a trust anchor → the installed kernel has not been verified here
//!   (`KERNEL_UNANCHORED`, D-0007 rule 1: "when T1 cannot be authenticated"); `gov kernel reinstall --source
//!   <signed release>` verifies the pinned release and records it (ARCH-0003 §8);
//! * no trust anchor (OWNER-DECISION-P2-0002, Option A — the unprovisioned sub-case, now determined): such a machine
//!   admits no kernel material but a gov binary's embedded payload, in marked bootstrap mode. The installed kernel is
//!   anchored when it is a bootstrap installation this machine recorded, or byte-identical to the running binary's
//!   embedded payload (the baseline rule 1 would substitute anyway). A divergence from the recorded bootstrap
//!   installation is `DIVERGED` (`KERNEL_TAMPERED`), and any other kernel — a clone of another machine's kernel, a
//!   checkout, an external-source install made before the decision — is `UNADMITTED` (`KERNEL_UNANCHORED`, remedy:
//!   provision, then verify the pinned signed release).
//!
//! This module still establishes only *intact*. It reads digests from protected state and never a verdict of the
//! Signed Release Root about where the bytes came from; D-0007's text is unchanged.
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
    /// Digest of the payload files on disk (what staging would measure), not what the manifest claims.
    pub measured_payload_hash: String,
    /// Digest of the installed `KERNEL_MANIFEST.json` (what `framework.lock.kernel_manifest_hash` should bind).
    pub manifest_hash: String,
    /// `BC-P2-35`: how the installed payload stands against this machine's protected installation record —
    /// `MATCHED`, `DIVERGED`, `UNRECORDED`, `UNRECORDED_REQUIRED` or `UNDETERMINED`.
    pub protected_record: String,
    pub protected_record_basis: String,
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
            measured_payload_hash: String::new(),
            manifest_hash: String::new(),
            protected_record: String::new(),
            protected_record_basis: String::new(),
        }
    }
    /// The verdict as data. It is embedded in agent context packets, which a clone rebuilt on another machine must
    /// reproduce, so the machine-local protected-record state is included only when it bears on the verdict (the
    /// kernel is untrusted because of it) or is itself a disclosure (a divergence reported but not enforced). A
    /// record that simply holds — present on the installing machine, absent on a clean clone of an unprovisioned
    /// project — changes nothing and is described by [`KernelTrust::summary`] instead.
    pub fn to_value(&self) -> Value {
        let mut v = json!({
            "installed": self.installed, "verified": self.verified, "source": self.source,
            "substituted_embedded_baseline": self.substituted, "manifest_matches_lock": self.manifest_matches_lock,
            "modified": self.modified, "missing": self.missing, "added": self.added,
            "installed_version": self.installed_version, "trusted_version": self.trusted_version,
            "problems": self.problems, "fingerprint": self.fingerprint,
            "measured_payload_hash": self.measured_payload_hash, "manifest_hash": self.manifest_hash,
        });
        if self.protected_record_bears() {
            v["protected_record"] =
                json!({"state": self.protected_record, "basis": self.protected_record_basis});
        }
        v
    }

    /// Does the protected-record state bear on the verdict, or is it a disclosure in its own right?
    pub fn protected_record_bears(&self) -> bool {
        matches!(
            self.protected_record.as_str(),
            "DIVERGED"
                | "UNRECORDED_REQUIRED"
                | "DIVERGED_NOT_ENFORCED"
                | "UNADMITTED"
                | "UNDETERMINED"
        )
    }
    /// One-line diagnostic for doctor / audit / context packets.
    pub fn summary(&self) -> String {
        if !self.installed {
            return "no installed kernel".into();
        }
        if self.verified {
            return match self.protected_record.as_str() {
                "MATCHED" => format!(
                    "installed kernel {} intact: matches KERNEL_MANIFEST.json, framework.lock and this machine's protected installation record",
                    self.installed_version
                ),
                "UNDETERMINED" => format!(
                    "installed kernel {} matches KERNEL_MANIFEST.json and framework.lock; this machine's protected installation record could not be consulted ({})",
                    self.installed_version, self.protected_record_basis
                ),
                _ => format!(
                    "installed kernel {} matches KERNEL_MANIFEST.json and framework.lock only; nothing the repository cannot rewrite anchors it on this machine ({})",
                    self.installed_version, self.protected_record_basis
                ),
            };
        }
        format!(
            "installed kernel FAILED verification ({}); constitutional policy is read from the embedded baseline {} and mutating operations are refused (KERNEL_TAMPERED)",
            self.problems.join("; "),
            self.trusted_version
        )
    }
}

/// Cached verdicts, keyed by repository root **and** the protected state they were computed against, so a process
/// that changes machine (tests, CI runners) never reads a verdict computed for another machine's records.
fn cache() -> &'static Mutex<HashMap<(PathBuf, String), KernelTrust>> {
    static C: OnceLock<Mutex<HashMap<(PathBuf, String), KernelTrust>>> = OnceLock::new();
    C.get_or_init(|| Mutex::new(HashMap::new()))
}

/// Every repository root whose kernel this process has evaluated. Not cleared by [`clear`]: it names the
/// installations this process is acting on, which is what the presentation layer must speak about (`BC-P2-36`).
fn evaluated() -> &'static Mutex<std::collections::BTreeSet<PathBuf>> {
    static E: OnceLock<Mutex<std::collections::BTreeSet<PathBuf>>> = OnceLock::new();
    E.get_or_init(|| Mutex::new(std::collections::BTreeSet::new()))
}

/// The repository roots this process has evaluated (see [`evaluated`]).
pub fn evaluated_roots() -> Vec<PathBuf> {
    evaluated()
        .lock()
        .map(|s| s.iter().cloned().collect())
        .unwrap_or_default()
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
    let mut measured_payload_hash = String::new();
    match verify_kernel(&kernel_dir) {
        Ok(v) => {
            payload_ok = v.ok;
            modified = v.modified.clone();
            missing = v.missing.clone();
            added = v.added.clone();
            measured_payload_hash = v.measured_payload_hash.clone();
            if !v.matches_manifest {
                problems.push(format!(
                    "kernel payload does not match KERNEL_MANIFEST.json: modified {:?} missing {:?} added {:?}",
                    v.modified, v.missing, v.added
                ));
            }
            if v.protected_record_enforced {
                problems.push(format!(
                    "kernel payload is not the payload this machine committed into this project ({}), whatever KERNEL_MANIFEST.json and framework.lock say: modified {:?} missing {:?} added {:?}. A post-install rewrite, or a change made without an ingress on this machine: verify the release framework.lock pins with `gov kernel reinstall --source <signed release>`",
                    v.protected_record_payload_hash, v.modified, v.missing, v.added
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
    // BC-P2-35: the installed payload against this machine's protected installation record, by digest.
    let anchor = crate::srr::installation::anchor_for(root, &measured_payload_hash, &actual_hash);
    let anchor_holds = anchor.holds();
    if let crate::srr::installation::Anchor::Unrecorded {
        required: true,
        basis,
    }
    | crate::srr::installation::Anchor::Unadmitted { basis } = &anchor
    {
        problems.push(basis.clone());
    } else if let crate::srr::installation::Anchor::Diverged {
        basis,
        enforced: true,
        ..
    } = &anchor
    {
        if !problems
            .iter()
            .any(|p| p.contains("this machine committed"))
        {
            problems.push(basis.clone());
        }
    }
    let verified = payload_ok && manifest_matches_lock && anchor_holds;
    // The anchor state enters the fingerprint only when it is why the kernel is untrusted, so an override gate is
    // bound to it then, and a trusted kernel's fingerprint stays a function of its bytes alone.
    let fingerprint = sha256_text(&format!(
        "{installed_version}|{actual_hash}|{lock_hash}|{modified:?}|{missing:?}|{added:?}|{}",
        if anchor_holds {
            String::new()
        } else {
            format!("{measured_payload_hash}|{}", anchor.state())
        }
    ));
    let protected_record = anchor.state().to_string();
    let protected_record_basis = anchor.basis().to_string();
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
            measured_payload_hash,
            manifest_hash: actual_hash,
            protected_record,
            protected_record_basis,
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
                measured_payload_hash,
                manifest_hash: actual_hash,
                protected_record,
                protected_record_basis,
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
                measured_payload_hash,
                manifest_hash: actual_hash,
                protected_record,
                protected_record_basis,
            }
        }
    }
}

/// Verified trust verdict for a repository (cached per process; `clear()` on any kernel/lock change).
pub fn trust(root: &Path) -> KernelTrust {
    if let Ok(mut e) = evaluated().lock() {
        e.insert(root.to_path_buf());
    }
    let key = (root.to_path_buf(), crate::srr::installation::state_key());
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
    if t.protected_record == "UNADMITTED"
        && t.modified.is_empty()
        && t.missing.is_empty()
        && t.added.is_empty()
        && t.manifest_matches_lock
    {
        return Err(GovError::new(
            "KERNEL_UNANCHORED",
            format!(
                "'{operation}' refused: this machine holds no Signed Release Root trust anchor, and the installed kernel is neither a bootstrap installation this machine made nor the payload embedded in this gov binary ({}). A machine with no trust anchor admits no external-source kernel material (OWNER-DECISION-P2-0002); until the machine is provisioned and verifies the release the project pins, constitutional policy is read from the embedded baseline. Provision it (`gov trust provision --anchor <administrator root>`), then `gov kernel reinstall --source <the signed release framework.lock pins>`.",
                t.problems.join("; ")
            ),
        )
        .with_details(json!({
            "operation": operation, "kernel_trust": t.to_value(),
            "decision": "OWNER-DECISION-P2-0002",
            "remediation": ["gov kernel trust", "gov trust provision --anchor <root metadata from the administrator domain>", "gov kernel reinstall --source <signed release pinned by framework.lock>", "gov kernel override --reason <why> (L4+, raises a gate)"],
        })));
    }
    if t.protected_record == "UNRECORDED_REQUIRED"
        && t.modified.is_empty()
        && t.missing.is_empty()
        && t.added.is_empty()
        && t.manifest_matches_lock
    {
        return Err(GovError::new(
            "KERNEL_UNANCHORED",
            format!(
                "'{operation}' refused: this machine holds a Signed Release Root trust anchor and has no protected record of verifying the installed kernel ({}). A machine verifies the release a project pins before privileged work (ARCH-0003 §8); until then constitutional policy is read from the embedded baseline. Verify it: `gov kernel reinstall --source <the signed release framework.lock pins>`.",
                t.problems.join("; ")
            ),
        )
        .with_details(json!({
            "operation": operation, "kernel_trust": t.to_value(),
            "remediation": ["gov kernel trust", "gov kernel reinstall --source <signed release pinned by framework.lock>", "gov kernel override --reason <why> (L4+, raises a gate)"],
        })));
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
