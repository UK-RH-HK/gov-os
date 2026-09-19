//! framework.lock: exact installed release/version/hash.
use crate::kernel::manifest_hash;
use crate::util::{now_iso, read_yaml, write_yaml};
use crate::{GovError, Result, CLI_VERSION, FRAMEWORK_NAME};
use serde_json::{json, Value};
use std::path::Path;

pub const LOCK_SCHEMA_VERSION: &str = "1.1.0";

/// `release_commit` identifies the installed FRAMEWORK release (never the consumer repository); the consumer's own
/// HEAD at installation time is recorded separately as `installed_at_commit` (verifier M-N1).
///
/// **`BC-P2-37` — the lock records identity; it does not invent it** (Contract v3:149, :950; D-0007 rule 2;
/// OWNER-DIRECTIVE-0004 "A project repository may pin an authenticated release identity but cannot establish its
/// trust root"). Every identity field is taken from what verification established and states its basis:
///
/// * `release_hash`, `kernel_manifest_hash` — the measured digests of the installed bytes (`manifest` is the
///   manifest committed from the verified staging copy);
/// * `authenticity`, `sequence`, `channel`, `release_metadata_sha256` — from this machine's protected installation
///   record of the ingress that committed these exact digests into this project (`crate::srr::installation`);
/// * `release_commit` — bound by signed release metadata (`evidence.provenance.release_commit`), else the constant
///   of the running binary when the payload is byte-identical to its embedded payload, else `unverified`. An
///   unsigned `manifest.json` beside a source and a checkout's Git HEAD are never recorded as identity;
/// * `source` — `release:` only for a release this machine verified, `embedded:` for this binary's own payload
///   (decided by content, so it cannot vary with `XDG_CACHE_HOME` or any other path), otherwise `source:`.
///
/// `source` and `release_commit` from the caller are hints and are not trusted: identity is decided here, from the
/// installed digests, for every ingress that writes a lock (init, update, adopt).
pub fn write_lock(
    path: &Path,
    manifest: &Value,
    source: &str,
    release_commit: Option<&str>,
    installed_at_commit: Option<&str>,
) -> Result<Value> {
    let id = release_identity(path, manifest, source, release_commit);
    let lock = json!({
        "framework": FRAMEWORK_NAME,
        "version": manifest["version"],
        "release_commit": id.release_commit,
        "release_hash": manifest["payload_hash"],
        "source": id.source,
        "installed_at_commit": installed_at_commit.unwrap_or("unknown"),
        "installed_at": now_iso(),
        "kernel_manifest_hash": manifest_hash(manifest),
        "cli_version": CLI_VERSION,
        "schema_versions": manifest.get("schema_versions").cloned().unwrap_or(json!({})),
        "lock_schema_version": LOCK_SCHEMA_VERSION,
        "authenticity": id.authenticity,
        "sequence": id.sequence,
        "channel": id.channel,
        "release_metadata_sha256": id.release_metadata_sha256,
        "identity_basis": id.basis,
    });
    write_yaml(path, &lock)?;
    crate::kernel_trust::clear();
    Ok(lock)
}

/// The identity `framework.lock` may record for an installed manifest, and the basis for each field.
pub struct ReleaseIdentity {
    pub release_commit: String,
    pub source: String,
    pub authenticity: String,
    pub sequence: Value,
    pub channel: Value,
    pub release_metadata_sha256: Value,
    pub basis: Value,
}

/// Decide the lock identity of `manifest` (the manifest of the payload just committed under `lock_path`'s
/// `governance/`). See [`write_lock`].
pub fn release_identity(
    lock_path: &Path,
    manifest: &Value,
    _source_hint: &str,
    _release_commit_hint: Option<&str>,
) -> ReleaseIdentity {
    let version = manifest["version"]
        .as_str()
        .unwrap_or("unknown")
        .to_string();
    let payload_hash = manifest["payload_hash"].as_str().unwrap_or("").to_string();
    let kmh = manifest_hash(manifest);
    let bound = lock_path
        .parent()
        .and_then(crate::srr::installation::project_root_of_governance_dir)
        .and_then(|root| crate::srr::installation::project_record(&root))
        .and_then(|r| r.binding(&payload_hash, &kmh).cloned());
    let verified = bound
        .as_ref()
        .map(|b| crate::srr::installation::records_a_verification(&b.authenticity))
        .unwrap_or(false);
    let embedded =
        !payload_hash.is_empty() && payload_hash == crate::kernel::embedded_payload_hash();
    let signed_commit = bound
        .as_ref()
        .filter(|_| verified)
        .map(|b| b.release_commit.clone())
        .unwrap_or_default();
    let (release_commit, commit_basis) = if !signed_commit.is_empty() {
        (signed_commit, "bound by signed release metadata (evidence.provenance.release_commit) that this machine verified".to_string())
    } else if embedded {
        (crate::kernel::embedded::commit().to_string(), "constant of the running gov binary: the installed payload is byte-identical to the payload embedded in it".to_string())
    } else {
        (crate::kernel::RELEASE_COMMIT_UNVERIFIED.to_string(), "no verified source binds a release commit for this payload; unsigned claims (a manifest.json beside the source, a checkout's Git HEAD) are not recorded as identity".to_string())
    };
    let (kind, source_basis) = if verified {
        ("release", "a release this machine verified (signed release metadata, or its own protected record of an earlier verification)")
    } else if embedded {
        ("embedded", "byte-identical to the payload embedded in the running gov binary (decided by content, never by path)")
    } else {
        ("source", "an unauthenticated kernel source")
    };
    let authenticity = bound
        .as_ref()
        .map(|b| b.authenticity.clone())
        .filter(|a| !a.is_empty())
        .unwrap_or_else(|| "UNKNOWN".into());
    let established_by = if verified {
        "this machine's protected installation record of the verifier's decision for these exact digests"
    } else if bound.is_some() {
        "not established: installed on a machine with no Signed Release Root trust anchor (authenticity UNKNOWN)"
    } else {
        "not established: no protected installation record on this machine binds these digests"
    };
    ReleaseIdentity {
        release_commit,
        source: format!("{kind}:{FRAMEWORK_NAME}@{version}"),
        authenticity,
        sequence: bound
            .as_ref()
            .filter(|_| verified)
            .map(|b| json!(b.sequence))
            .unwrap_or(Value::Null),
        channel: bound
            .as_ref()
            .filter(|_| verified)
            .map(|b| json!(b.channel))
            .unwrap_or(Value::Null),
        release_metadata_sha256: bound
            .as_ref()
            .filter(|b| verified && !b.release_metadata_sha256.is_empty())
            .map(|b| json!(b.release_metadata_sha256))
            .unwrap_or(Value::Null),
        basis: json!({
            "established_by": established_by,
            "version": if verified { "bound by the verified release identity" } else { "declared by the installed payload's KERNEL.yaml (not authenticated)" },
            "release_hash": "measured digest of the installed payload (verified-byte binding at install)",
            "kernel_manifest_hash": "digest of the manifest committed from the measured staging copy",
            "release_commit": commit_basis,
            "source": source_basis,
            "note": "framework.lock records a release identity; it never establishes trust (OWNER-DIRECTIVE-0004). Post-install integrity is checked against this machine's protected installation record, which a repository cannot rewrite.",
        }),
    }
}

pub fn read_lock(path: &Path) -> Result<Value> {
    if !path.exists() {
        return Err(GovError::new(
            "LOCK_MISSING",
            format!("framework.lock missing at {}", path.display()),
        ));
    }
    read_yaml(path)
}

pub fn parse_version(v: &str) -> (u64, u64, u64) {
    let core = v.split(['-', '+']).next().unwrap_or("0");
    let mut it = core.split('.').map(|p| p.parse::<u64>().unwrap_or(0));
    (
        it.next().unwrap_or(0),
        it.next().unwrap_or(0),
        it.next().unwrap_or(0),
    )
}

pub fn compare_versions(a: &str, b: &str) -> std::cmp::Ordering {
    parse_version(a).cmp(&parse_version(b))
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct Compatibility {
    pub compatible: bool,
    pub warning: bool,
    pub reason: String,
}

pub fn compatibility(lock_version: &str, cli_version: &str) -> Compatibility {
    let (lv, cv) = (parse_version(lock_version), parse_version(cli_version));
    if lv.0 != cv.0 {
        Compatibility {
            compatible: false,
            warning: false,
            reason: "major version mismatch between installed kernel and gov CLI".into(),
        }
    } else if (lv.1, lv.2) != (cv.1, cv.2) {
        Compatibility { compatible: true, warning: true, reason: format!("installed kernel {lock_version} differs from CLI {cli_version}; run gov update --check") }
    } else {
        Compatibility {
            compatible: true,
            warning: false,
            reason: "match".into(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn versions_and_compat() {
        assert_eq!(parse_version("4.1.2-rc.1"), (4, 1, 2));
        assert!(compatibility("4.1.1", "4.1.2").warning);
        assert!(!compatibility("3.9.0", "4.1.2").compatible);
        assert!(!compatibility("4.1.2", "4.1.2").warning);
        assert_eq!(compare_versions("4.1.1", "4.1.2"), std::cmp::Ordering::Less);
    }
}
