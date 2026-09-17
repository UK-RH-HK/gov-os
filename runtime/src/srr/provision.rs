//! Signed Release Root v1 — administrator provisioning of the trust anchor, and root succession.
//!
//! ARCH-0003 §5: "Bootstrap authenticity comes from the pre-existing controlled platform/admin installation
//! boundary. It is **not** derived from the candidate source, its manifest, its lock, its Git repository or
//! mutually consistent files delivered with it."
//!
//! So [`provision`] deliberately refuses a root file that lives inside the governed project. The administrator
//! supplies it from the platform/admin domain — the same boundary that installed the verifier.
//!
//! `SRR-R0-L7` is **owner-closed and out of scope**: this is not an offline/air-gapped first-install ceremony, and
//! none is built here. Break-glass *recovery* remains fully offline (see [`super::breakglass`]).
use crate::srr::metadata::{self, Envelope, Root};
use crate::srr::state::MachineState;
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::path::Path;

/// Install the first trust anchor for this machine.
pub fn provision(root_file: &Path, project_root: Option<&Path>) -> Result<Value> {
    let ms = MachineState::open()?;
    let now = metadata::local_clock_now();
    refuse_repository_sourced_anchor(root_file, project_root)?;
    let bytes = std::fs::read(root_file)
        .map_err(|e| GovError::io(&format!("read {}", root_file.display()), e))?;
    let env = Envelope::parse(&bytes, &root_file.display().to_string())?;
    let root = metadata::parse_self_signed_root(env, &now)?;
    if ms.is_provisioned() {
        let existing = ms.provisioned_record();
        let current_version = existing
            .get("root_version")
            .and_then(|v| v.as_u64())
            .unwrap_or(0);
        return Err(GovError::new(
            "SRR_ALREADY_PROVISIONED",
            format!("this machine already holds a trust anchor for '{}' at root version {current_version}. Replacing it is root succession, not provisioning: use `gov trust root-update`, which requires the outgoing quorum's authorisation.", root.product),
        )
        .with_details(json!({"current_root_version": current_version, "candidate_root_version": root.version})));
    }
    ms.set_root_metadata(&bytes, root.version, &root.product)?;
    Ok(json!({
        "provisioned": true, "machine_id": ms.machine_id, "state_root": ms.root.display().to_string(),
        "product": root.product, "root_version": root.version, "root_expires": root.expires,
        "root_sha256": crate::util::sha256_hex(&bytes),
        "roles": root.roles.iter().map(|(k, v)| (k.clone(), json!({"threshold": v.threshold, "keys": v.keyids.len()}))).collect::<serde_json::Map<_, _>>(),
        "note": "Bootstrap authenticity comes from the platform/administrator installation boundary (ARCH-0003 §5), not from this file's contents and not from any repository.",
    }))
}

/// Accept a successor root (`SRR-R0-L1`). Applies one version at a time so every intermediate revocation takes
/// effect; see [`metadata::accept_root_succession`] for the concrete acceptance rules.
pub fn root_update(root_file: &Path, project_root: Option<&Path>) -> Result<Value> {
    let ms = MachineState::open()?;
    let now = metadata::local_clock_now();
    refuse_repository_sourced_anchor(root_file, project_root)?;
    let current = super::verifier::trusted_root(&ms, &now)?.ok_or_else(|| {
        GovError::new(
            "SRR_NOT_PROVISIONED",
            "this machine holds no trust anchor; use `gov trust provision` first",
        )
    })?;
    let bytes = std::fs::read(root_file)
        .map_err(|e| GovError::io(&format!("read {}", root_file.display()), e))?;
    let env = Envelope::parse(&bytes, &root_file.display().to_string())?;
    let next: Root = metadata::accept_root_succession(&current, env, &now)?;
    let revoked: Vec<String> = current
        .keys
        .keys()
        .filter(|k| !next.keys.contains_key(*k))
        .cloned()
        .collect();
    ms.set_root_metadata(&bytes, next.version, &next.product)?;
    let mut floors = crate::srr::state::Floors::load(&ms, &next.product);
    floors.raise_metadata(metadata::ROLE_ROOT, next.version);
    floors.save(&ms)?;
    Ok(json!({
        "root_updated": true, "from_version": current.version, "to_version": next.version,
        "product": next.product, "expires": next.expires,
        "revoked_keyids": revoked,
        "note": "Keys and delegations absent from the accepted successor are revoked from this moment. Succession is applied one version at a time so that no intermediate revocation is skipped (SRR-R0-L1).",
    }))
}

/// A trust anchor may not be taken from inside a governed repository.
fn refuse_repository_sourced_anchor(root_file: &Path, project_root: Option<&Path>) -> Result<()> {
    let abs = root_file
        .canonicalize()
        .unwrap_or_else(|_| root_file.to_path_buf());
    if let Some(pr) = project_root {
        let pabs = pr.canonicalize().unwrap_or_else(|_| pr.to_path_buf());
        if abs.starts_with(&pabs) {
            return Err(GovError::new(
                "SRR_ANCHOR_FROM_REPOSITORY_REFUSED",
                format!("{} is inside the governed project at {}. A trust anchor comes from the platform/administrator installation boundary, never from repository content (ARCH-0003 §5, OWNER-DIRECTIVE-0004).", abs.display(), pabs.display()),
            ));
        }
    }
    for part in abs.components() {
        let s = part.as_os_str().to_string_lossy();
        if s == ".git" || s == "governance" {
            return Err(GovError::new(
                "SRR_ANCHOR_FROM_REPOSITORY_REFUSED",
                format!("{} is repository-controlled content and cannot be a trust anchor (ARCH-0003 §5).", abs.display()),
            ));
        }
    }
    Ok(())
}

/// Report where an owner-signed break-glass authorisation must be placed, without ever printing key material.
pub fn break_glass_status() -> Result<Value> {
    let ms = MachineState::open()?;
    let inbox = ms.break_glass_inbox();
    let pending: Vec<String> = std::fs::read_dir(&inbox)
        .map(|rd| {
            rd.filter_map(|e| e.ok())
                .map(|e| e.file_name().to_string_lossy().to_string())
                .filter(|n| n.ends_with(".json"))
                .collect()
        })
        .unwrap_or_default();
    let consumed = std::fs::read_dir(ms.break_glass_consumed())
        .map(|rd| rd.filter_map(|e| e.ok()).count())
        .unwrap_or(0);
    Ok(json!({
        "machine_id": ms.machine_id,
        "inbox": inbox.display().to_string(),
        "pending_authorisations": pending,
        "consumed_authorisations": consumed,
        "marking": super::breakglass::DEGRADED_TOKEN,
        "currently_degraded": super::breakglass::is_degraded(&ms, crate::FRAMEWORK_NAME),
        "exit_policy": super::breakglass::EXIT_POLICY,
        "exit_condition": super::breakglass::exit_condition_description(),
        "requirements": {
            "signed_by": "the owner's offline `recovery` role declared in the trusted root metadata",
            "bound_to": ["product", "this machine_id", "a single-use nonce", "the recovery payload digests (SRR2-R1-C2)"],
            "cannot_come_from": ["repository content", "environment variables", "caller fields or CLI flags", "plugins", "model output", "the running binary itself"],
            "network_required": false,
        },
    }))
}
