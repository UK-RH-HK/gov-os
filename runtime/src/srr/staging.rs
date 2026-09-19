//! Signed Release Root v1 — private staging, verified-byte binding and the atomic, crash-safe install transaction.
//!
//! ARCH-0003 §6 / 00-ARCHITECTURE "Transaction invariant":
//!
//! 1. receive candidate bytes in a private staging area;
//! 2. verify signed metadata and **the exact staged bytes**;
//! 3. retain a typed authenticated-release handle;
//! 4. install only those measured bytes;
//! 5. atomically commit one complete version;
//! 6. verify the committed representation;
//! 7. durably update journal and high-water;
//! 8. recover after interruption to the old complete version or the new complete version.
//!
//! ## Verified-byte binding
//!
//! The candidate is copied into private staging **first**, and every digest is computed over the *staged* copy.
//! The signed metadata is compared against those staged digests, and the install reads from the same staged copy.
//! Nothing re-reads the original source after measurement, so there is no window in which the source could be
//! swapped between "the bytes that were verified" and "the bytes that were installed".
//!
//! ## `SRR-R0-L5` — durability ordering relative to atomic commit
//!
//! The ordering is fixed and deliberate:
//!
//! ```text
//!   (1) journal intent                       fsync'd BEFORE anything is moved
//!   (2) build <dest>.srr-new from staging
//!   (3) journal phase=swap                   fsync'd BEFORE the first rename
//!   (4) rename dest -> dest.srr-old          atomic
//!   (5) rename dest.srr-new -> dest          atomic; fsync(parent)
//!   (6) journal phase=committed              fsync'd
//!   (7) verify the committed bytes
//!   (8) remove dest.srr-old
//!   (9) ADVANCE THE FLOORS (high-water)      fsync'd, only now
//!  (10) journal phase=done
//! ```
//!
//! Step (9) is deliberately **after** (5)–(7), never before. If the high-water advanced first and the machine
//! crashed before the commit, it would come back on the *old* release while its own protected floor named the new
//! one — a machine below its own floor, i.e. self-inflicted bricking that only break-glass could clear. Advancing
//! afterwards has the opposite, safe failure: the machine is on the new release with a floor still naming the old
//! one, which admits nothing that was not already admissible and is corrected on the next successful ingress.
//!
//! Crash windows and their recovery ([`recover`]):
//! * between (1) and (4) — nothing moved; the intent is discarded and staging is swept.
//! * between (4) and (5) — `dest` is absent, `dest.srr-new` is complete: the swap is completed.
//! * between (5) and (8) — `dest` is the complete new version; `dest.srr-old` is removed.
//!
//! In every window the result is one complete valid installation, never a mixed tree.
use crate::srr::state::{fsync_dir, write_durable, MachineState};
use crate::util::{copy_dir, hash_tree, hash_value, now_iso, remove_dir_if_exists, short_uuid};
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

pub const NEW_SUFFIX: &str = ".srr-new";
pub const OLD_SUFFIX: &str = ".srr-old";

/// Candidate bytes copied into private staging and measured there.
#[derive(Debug, Clone)]
pub struct Staged {
    pub id: String,
    /// The private staging directory holding the complete, self-contained payload.
    pub payload_dir: PathBuf,
    /// Per-file SHA-256 over the staged bytes.
    pub files: BTreeMap<String, String>,
    /// Digest over the whole staged file map — identical in construction to `KERNEL_MANIFEST.payload_hash`.
    pub payload_hash: String,
    /// Digest of the manifest this payload would produce, i.e. what `framework.lock.kernel_manifest_hash` binds.
    pub kernel_manifest_hash: String,
    pub version: String,
    pub manifest: Value,
}

impl Staged {
    pub fn to_value(&self) -> Value {
        json!({"staging_id": self.id, "payload_hash": self.payload_hash,
               "kernel_manifest_hash": self.kernel_manifest_hash, "version": self.version,
               "file_count": self.files.len()})
    }
}

/// Copy a candidate kernel source into private staging and measure the staged bytes.
///
/// `candidate` is a kernel source directory (a built release's `kernel/`, a `framework/` checkout, or the payload
/// embedded in this binary after materialisation). `stage_payload` resolves the payload exactly as an install
/// would — including `migrations/` and `tools/` when they sit beside `framework/` — so the staged tree is
/// self-contained and no later step needs to consult the original location again.
pub fn stage(ms: &MachineState, candidate: &Path) -> Result<Staged> {
    let id = format!(
        "{}-{}",
        now_iso().replace([':', '-'], "").replace('T', "-"),
        short_uuid()
    );
    let dir = ms.staging_dir().join(&id);
    let payload_dir = dir.join("payload");
    remove_dir_if_exists(&dir)?;
    std::fs::create_dir_all(&dir).map_err(|e| GovError::io("mkdir staging", e))?;
    crate::kernel::stage_payload(candidate, &payload_dir)?;
    // Measure the STAGED bytes. Everything downstream compares against, and installs from, this measurement.
    let (_, files) = hash_tree(&payload_dir, &[crate::kernel::KERNEL_MANIFEST])?;
    let manifest = crate::kernel::build_manifest(&payload_dir)?;
    let payload_hash = hash_value(&serde_json::to_value(&files)?);
    if manifest["payload_hash"].as_str() != Some(payload_hash.as_str()) {
        return Err(GovError::new(
            "SRR_STAGING_MEASUREMENT_INCONSISTENT",
            "the staged payload digest does not agree with the manifest built from the same staged bytes",
        ));
    }
    let kernel_manifest_hash = crate::kernel::manifest_hash(&manifest);
    let version = manifest["version"].as_str().unwrap_or("").to_string();
    Ok(Staged {
        id,
        payload_dir,
        files,
        payload_hash,
        kernel_manifest_hash,
        version,
        manifest,
    })
}

/// Discard a staging area.
pub fn discard(staged: &Staged) {
    if let Some(parent) = staged.payload_dir.parent() {
        let _ = std::fs::remove_dir_all(parent);
    }
}

/// Re-measure the staged bytes and confirm they are unchanged since [`stage`]. Called immediately before the
/// commit so that the window between verification and install is closed on the staging side too.
pub fn confirm_unchanged(staged: &Staged) -> Result<()> {
    let (_, now) = hash_tree(&staged.payload_dir, &[crate::kernel::KERNEL_MANIFEST])?;
    if now != staged.files {
        return Err(GovError::new(
            "SRR_STAGED_BYTES_CHANGED",
            "the privately staged payload changed after it was verified; the install is refused (verified-byte binding)",
        ));
    }
    Ok(())
}

// ---------------------------------------------------------------------------------------------- transaction

fn journal_path(ms: &MachineState, id: &str) -> PathBuf {
    ms.journal_dir().join(format!("{id}.json"))
}

fn journal(ms: &MachineState, id: &str, phase: &str, extra: &Value) -> Result<()> {
    let mut v = crate::util::read_json(&journal_path(ms, id)).unwrap_or(json!({}));
    v["id"] = json!(id);
    v["phase"] = json!(phase);
    v["at"] = json!(now_iso());
    if let Some(o) = extra.as_object() {
        for (k, val) in o {
            v[k.clone()] = val.clone();
        }
    }
    write_durable(&journal_path(ms, id), &v)
}

/// Atomically install the staged payload at `dest`, verify the committed bytes, and leave the journal consistent.
///
/// On any failure after the swap has begun, the previous complete tree is restored before the error is returned.
pub fn commit_tree(ms: &MachineState, staged: &Staged, dest: &Path) -> Result<Value> {
    confirm_unchanged(staged)?;
    let parent = dest.parent().ok_or_else(|| {
        GovError::new(
            "IO_ERROR",
            format!("{} has no parent directory", dest.display()),
        )
    })?;
    std::fs::create_dir_all(parent).map_err(|e| GovError::io("mkdir install parent", e))?;
    let newp = with_suffix(dest, NEW_SUFFIX);
    let oldp = with_suffix(dest, OLD_SUFFIX);

    // (1) intent, durable before anything moves
    journal(
        ms,
        &staged.id,
        "prepare",
        &json!({"dest": dest.display().to_string(), "staging": staged.payload_dir.display().to_string(),
                "payload_hash": staged.payload_hash, "version": staged.version,
                "new_path": newp.display().to_string(), "old_path": oldp.display().to_string()}),
    )?;

    // (2) build the complete new tree beside the destination, on the same filesystem so the rename is atomic
    remove_dir_if_exists(&newp)?;
    copy_dir(&staged.payload_dir, &newp)?;
    // The manifest is written into the new tree before the swap, so the committed tree is complete on arrival. It is
    // a pure function of the verified payload: no install timestamp (`framework.lock.installed_at` records when), so
    // a second machine that verifies the release a clone pins (ARCH-0003 §8, `gov kernel reinstall`) re-commits
    // byte-identical files and leaves the repository unchanged.
    let manifest = staged.manifest.clone();
    crate::util::write_json(&newp.join(crate::kernel::KERNEL_MANIFEST), &manifest)?;
    fsync_dir(&newp);
    fsync_dir(parent);

    // (3) durable marker that the swap is about to start
    journal(ms, &staged.id, "swap", &json!({}))?;

    // (4)(5) the swap itself
    remove_dir_if_exists(&oldp)?;
    let had_previous = dest.exists();
    if had_previous {
        std::fs::rename(dest, &oldp)
            .map_err(|e| GovError::io("rename previous installation aside", e))?;
    }
    if let Err(e) = std::fs::rename(&newp, dest) {
        // put the previous tree back before reporting: never leave the machine with neither version
        if had_previous {
            let _ = std::fs::rename(&oldp, dest);
        }
        return Err(GovError::io("rename new installation into place", e));
    }
    fsync_dir(parent);

    // (6) committed
    journal(
        ms,
        &staged.id,
        "committed",
        &json!({"had_previous": had_previous}),
    )?;

    // (7) verify the committed representation against the measurement that was verified
    let (_, committed) = hash_tree(dest, &[crate::kernel::KERNEL_MANIFEST])?;
    if committed != staged.files {
        // restore and refuse: an installed tree that is not the verified tree must never be left in place
        let _ = std::fs::rename(dest, &newp);
        if had_previous {
            let _ = std::fs::rename(&oldp, dest);
        }
        journal(
            ms,
            &staged.id,
            "reverted",
            &json!({"reason": "committed bytes did not match the verified measurement"}),
        )?;
        return Err(GovError::new(
            "SRR_COMMITTED_BYTES_MISMATCH",
            "the committed installation does not match the verified staged bytes; the previous installation was restored",
        ));
    }

    // (8) drop the superseded tree
    let _ = std::fs::remove_dir_all(&oldp);
    journal(ms, &staged.id, "verified", &json!({}))?;
    Ok(
        json!({"dest": dest.display().to_string(), "payload_hash": staged.payload_hash,
              "version": staged.version, "files": staged.files.len(), "had_previous": had_previous}),
    )
}

/// Mark the transaction finished. Called by the ingress **after** the floors have been advanced durably, so the
/// journal records the true end of step (9).
pub fn finish(ms: &MachineState, staged: &Staged, floors_advanced: bool) -> Result<()> {
    journal(
        ms,
        &staged.id,
        "done",
        &json!({"floors_advanced": floors_advanced}),
    )?;
    let _ = std::fs::remove_file(journal_path(ms, &staged.id));
    discard(staged);
    Ok(())
}

/// Abandon a transaction that never committed.
pub fn abandon(ms: &MachineState, staged: &Staged, reason: &str) {
    let _ = journal(ms, &staged.id, "abandoned", &json!({"reason": reason}));
    let _ = std::fs::remove_file(journal_path(ms, &staged.id));
    discard(staged);
}

fn with_suffix(p: &Path, suffix: &str) -> PathBuf {
    let name = p
        .file_name()
        .map(|f| f.to_string_lossy().to_string())
        .unwrap_or("install".into());
    p.with_file_name(format!("{name}{suffix}"))
}

/// Replay incomplete install transactions. Idempotent; safe to call on every privileged ingress.
///
/// The outcome is always one complete valid installation: either the previous one or the new one, never a mixed
/// tree (ARCH-0003 §6).
pub fn recover(ms: &MachineState) -> Result<Vec<Value>> {
    let mut out = vec![];
    let Ok(rd) = std::fs::read_dir(ms.journal_dir()) else {
        return Ok(out);
    };
    let mut entries: Vec<PathBuf> = rd
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().map(|x| x == "json").unwrap_or(false))
        .collect();
    entries.sort();
    for jp in entries {
        let Ok(v) = crate::util::read_json(&jp) else {
            continue;
        };
        let phase = v.get("phase").and_then(|x| x.as_str()).unwrap_or("");
        let dest = PathBuf::from(v.get("dest").and_then(|x| x.as_str()).unwrap_or(""));
        let newp = PathBuf::from(v.get("new_path").and_then(|x| x.as_str()).unwrap_or(""));
        let oldp = PathBuf::from(v.get("old_path").and_then(|x| x.as_str()).unwrap_or(""));
        if dest.as_os_str().is_empty() {
            let _ = std::fs::remove_file(&jp);
            continue;
        }
        let action = match phase {
            // nothing was moved: discard the half-built tree
            "prepare" => {
                let _ = std::fs::remove_dir_all(&newp);
                "discarded_prepared_tree"
            }
            // the crash landed inside the two-rename window
            "swap" => {
                if !dest.exists() && newp.exists() {
                    let _ = std::fs::rename(&newp, &dest);
                    "completed_interrupted_swap"
                } else if !dest.exists() && oldp.exists() {
                    let _ = std::fs::rename(&oldp, &dest);
                    let _ = std::fs::remove_dir_all(&newp);
                    "restored_previous_installation"
                } else {
                    let _ = std::fs::remove_dir_all(&newp);
                    "no_action_destination_intact"
                }
            }
            // the new tree is in place; only the superseded copy remains
            "committed" | "verified" | "done" => {
                let _ = std::fs::remove_dir_all(&oldp);
                "removed_superseded_installation"
            }
            _ => "no_action",
        };
        // The floors are NOT advanced during replay. A crashed transaction never proved its post-commit
        // verification, so it must not move a protected floor (SRR-R0-L5).
        out.push(
            json!({"journal": jp.display().to_string(), "phase": phase, "action": action,
                        "dest": dest.display().to_string(), "floors_advanced": false}),
        );
        let _ = std::fs::remove_file(&jp);
    }
    // sweep abandoned staging areas
    if let Ok(rd) = std::fs::read_dir(ms.staging_dir()) {
        for e in rd.filter_map(|x| x.ok()) {
            if e.path().is_dir() {
                if let Ok(md) = e.metadata() {
                    if let Ok(modified) = md.modified() {
                        if modified
                            .elapsed()
                            .map(|d| d.as_secs() > 86_400)
                            .unwrap_or(false)
                        {
                            let _ = std::fs::remove_dir_all(e.path());
                        }
                    }
                }
            }
        }
    }
    Ok(out)
}
