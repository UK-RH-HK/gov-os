//! Kernel payload: build from the canonical repo, install into a consumer, verify immutability.
use crate::util::{copy_dir, hash_tree, hash_value, read_json, read_yaml, remove_dir_if_exists};
use crate::{GovError, Result, FRAMEWORK_NAME, VERSION};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

pub const KERNEL_MANIFEST: &str = "KERNEL_MANIFEST.json";

/// The kernel payload compiled into the binary (build.rs embeds framework/, migrations/ and tools/), so a single
/// `gov` executable can install a kernel on any machine without the source checkout (D-0002, verifier M6).
pub mod embedded {
    include!(concat!(env!("OUT_DIR"), "/embedded_kernel.rs"));
    pub fn version() -> &'static str {
        EMBEDDED_VERSION
    }
    /// The framework commit this payload was built from (release manifest commit when the build tree carries the
    /// release, else the git HEAD at build time; "unknown" outside a checkout).
    pub fn commit() -> &'static str {
        EMBEDDED_COMMIT
    }
    pub fn files() -> &'static [(&'static str, &'static [u8])] {
        EMBEDDED_FILES
    }
}

/// The payload digest the embedded kernel produces when staged, computed from the embedded bytes alone.
///
/// `BC-P2-37`: whether an installed payload *is* this binary's embedded payload is a property of its bytes, not of
/// the directory it was copied from. The recorded identity of an embedded install therefore cannot vary with
/// `XDG_CACHE_HOME`, `GOV_KERNEL_CACHE` or where a cache happens to sit (Contract v3:149, :950). The selection
/// mirrors [`stage_payload`] exactly: `KERNEL.yaml` plus every file under a `payload_dirs` entry.
pub fn embedded_payload_hash() -> String {
    static H: std::sync::OnceLock<String> = std::sync::OnceLock::new();
    H.get_or_init(|| {
        let files = embedded::files();
        let dirs: Vec<String> = files
            .iter()
            .find(|(p, _)| *p == "KERNEL.yaml")
            .and_then(|(_, b)| serde_yaml::from_slice::<Value>(b).ok())
            .and_then(|m| m.get("payload_dirs").and_then(|v| v.as_array()).cloned())
            .unwrap_or_default()
            .iter()
            .filter_map(|d| d.as_str().map(String::from))
            .collect();
        let mut map: BTreeMap<String, String> = BTreeMap::new();
        for (rel, bytes) in files {
            let first = rel.split('/').next().unwrap_or("");
            if *rel == "KERNEL.yaml"
                || (rel.contains('/') && dirs.iter().any(|d| d == first) && *rel != KERNEL_MANIFEST)
            {
                map.insert(rel.to_string(), crate::util::sha256_hex(bytes));
            }
        }
        hash_value(&serde_json::to_value(&map).unwrap_or(Value::Null))
    })
    .clone()
}

/// The identity of the running `gov` binary, as far as a bootstrap installation is tied to it (OWNER-DECISION-P2-0002
/// requirement 2: "the verifier binary's own embedded payload may be installed on an unprovisioned machine only as an
/// explicitly marked bootstrap mode tied to the binary's own identity").
///
/// The embedded payload digest is compiled into the binary, so "this payload is the binary's own" is decided by
/// content ([`embedded_payload_hash`]), never by a path. The executable digest records *which* binary did it; it is
/// best-effort (a binary that cannot read itself reports why) and identifies nothing a caller could choose.
pub fn binary_identity() -> Value {
    static EXE: std::sync::OnceLock<String> = std::sync::OnceLock::new();
    let exe = EXE
        .get_or_init(|| match std::env::current_exe().and_then(std::fs::read) {
            Ok(bytes) => crate::util::sha256_hex(&bytes),
            Err(e) => format!("unavailable: {e}"),
        })
        .clone();
    json!({
        "gov_version": VERSION,
        "cli_version": crate::CLI_VERSION,
        "embedded_kernel_version": embedded::version(),
        "embedded_commit": embedded::commit(),
        "embedded_payload_hash": embedded_payload_hash(),
        "executable_sha256": exe,
    })
}

/// The embedded payload's listing — `(relative path, sha256)` for every embedded file, sorted — and its digest, which
/// names the cache directory. Computed once per process from the embedded bytes alone.
fn embedded_listing() -> &'static (Vec<(String, String)>, String) {
    static L: std::sync::OnceLock<(Vec<(String, String)>, String)> = std::sync::OnceLock::new();
    L.get_or_init(|| {
        let mut listing: Vec<(String, String)> = embedded::files()
            .iter()
            .map(|(p, b)| (p.to_string(), crate::util::sha256_hex(b)))
            .collect();
        listing.sort();
        let id = crate::util::sha256_text(&serde_json::to_string(&listing).unwrap_or_default());
        (listing, id)
    })
}

/// The name of the marker [`embedded_kernel_dir`] writes last into a materialised cache directory.
const CACHE_COMPLETE_MARKER: &str = ".complete";

/// Is `dir` **exactly** the embedded payload? Every listed file present with its digest, no other file (the
/// completion marker aside), and the marker naming this listing.
///
/// IP-WS02-15 (root cause of the corrupt-cache defect WS-2 found, repair-1/ws02 §2): the old test was "`KERNEL.yaml`
/// and `.complete` exist", which a directory holding 61 of 127 files — the result of several threads materialising into
/// one shared `.staging-<pid>` — passed. A cache is now re-used only when its content is the listing.
fn cache_matches_listing(dir: &Path) -> bool {
    let (listing, id) = embedded_listing();
    match std::fs::read_to_string(dir.join(CACHE_COMPLETE_MARKER)) {
        Ok(m) if m.trim() == id.as_str() => {}
        _ => return false,
    }
    let Ok((_, on_disk)) = hash_tree(dir, &[CACHE_COMPLETE_MARKER]) else {
        return false;
    };
    on_disk.len() == listing.len()
        && listing
            .iter()
            .all(|(rel, sha)| on_disk.get(rel).map(|h| h == sha).unwrap_or(false))
}

/// Where [`embedded_kernel_dir`] materialises the embedded payload, computed without writing anything.
fn embedded_kernel_path() -> Result<PathBuf> {
    let id = &embedded_listing().1;
    let base = std::env::var("GOV_KERNEL_CACHE")
        .ok()
        .map(PathBuf::from)
        .or_else(|| {
            std::env::var("XDG_CACHE_HOME")
                .ok()
                .map(|c| PathBuf::from(c).join("gov"))
        })
        .or_else(|| {
            std::env::var("HOME")
                .ok()
                .map(|h| PathBuf::from(h).join(".cache").join("gov"))
        })
        .unwrap_or(std::env::temp_dir().join("gov-cache"));
    Ok(base
        .join("kernels")
        .join(format!("{}-{}", embedded::version(), &id[..12])))
}

/// Materialise the embedded payload into a per-user cache directory (content-addressed, verified before re-use).
///
/// **IP-WS02-15 — the root cause, fixed here rather than serialised around.** The old implementation staged into
/// `kernels/.staging-<pid>`, shared by every thread of one process, and re-used any directory holding `KERNEL.yaml`
/// and `.complete`. Two threads materialising at once interleaved their writes and removals and left a corrupt cache
/// marked complete, which later `gov init` runs installed (or, under OWNER-DECISION-P2-0002, would refuse as
/// not-the-embedded-payload). Now:
///
/// * an existing directory is re-used only when its content **is** the embedded listing ([`cache_matches_listing`]);
/// * every call stages into its own directory (`.staging-<pid>-<uuid>`), checks it against the listing, and publishes
///   it with one `rename`; a loser of that race keeps the winner's directory when it verifies;
/// * a directory that does not verify is moved aside (never deleted in place under a reader) and replaced.
///
/// A directory verified once is remembered for the rest of the process, so the per-file check is paid once.
pub fn embedded_kernel_dir() -> Result<PathBuf> {
    static VERIFIED: std::sync::Mutex<Option<PathBuf>> = std::sync::Mutex::new(None);
    let dir = embedded_kernel_path()?;
    if let Ok(v) = VERIFIED.lock() {
        if v.as_ref() == Some(&dir) && dir.join(CACHE_COMPLETE_MARKER).exists() {
            return Ok(dir);
        }
    }
    let remember = |d: &Path| {
        if let Ok(mut v) = VERIFIED.lock() {
            *v = Some(d.to_path_buf());
        }
    };
    if cache_matches_listing(&dir) {
        remember(&dir);
        return Ok(dir);
    }
    let kernels = dir
        .parent()
        .map(|p| p.to_path_buf())
        .unwrap_or_else(|| std::env::temp_dir().join("gov-cache").join("kernels"));
    std::fs::create_dir_all(&kernels)
        .map_err(|e| GovError::io(&format!("mkdir {}", kernels.display()), e))?;
    let unique = format!("{}-{}", std::process::id(), crate::util::short_uuid());
    let staging = kernels.join(format!(".staging-{unique}"));
    let write_all = || -> Result<()> {
        for (rel, bytes) in embedded::files() {
            let p = staging.join(rel);
            if let Some(d) = p.parent() {
                std::fs::create_dir_all(d)?;
            }
            std::fs::write(&p, bytes)?;
        }
        std::fs::write(
            staging.join(CACHE_COMPLETE_MARKER),
            embedded_listing().1.as_bytes(),
        )?;
        Ok(())
    };
    if let Err(e) = write_all() {
        let _ = std::fs::remove_dir_all(&staging);
        return Err(e);
    }
    if !cache_matches_listing(&staging) {
        let _ = std::fs::remove_dir_all(&staging);
        return Err(GovError::new(
            "KERNEL_CACHE_CORRUPT",
            format!("the embedded kernel payload could not be materialised intact under {}; the staged copy does not match the payload embedded in this binary", kernels.display()),
        ));
    }
    // Another process may have published a verified directory meanwhile; keep it. Otherwise move the unverified
    // directory aside (a reader holding paths under it sees the replacement, with identical content, at the same
    // path) and publish ours.
    if dir.exists() && !cache_matches_listing(&dir) {
        let aside = kernels.join(format!(".stale-{unique}"));
        let _ = std::fs::rename(&dir, &aside);
        let _ = std::fs::remove_dir_all(&aside);
    }
    if let Err(e) = std::fs::rename(&staging, &dir) {
        let _ = std::fs::remove_dir_all(&staging);
        if !cache_matches_listing(&dir) {
            return Err(GovError::io("materialise embedded kernel", e));
        }
    }
    if !cache_matches_listing(&dir) {
        return Err(GovError::new(
            "KERNEL_CACHE_CORRUPT",
            format!("the embedded kernel cache at {} does not match the payload embedded in this binary after materialisation", dir.display()),
        ));
    }
    remember(&dir);
    Ok(dir)
}

/// The canonical repository root, only when explicitly provided (GOV_CANONICAL_ROOT); no build path is baked in.
pub fn canonical_root() -> Option<PathBuf> {
    let c = std::env::var("GOV_CANONICAL_ROOT")
        .ok()
        .map(PathBuf::from)?;
    if c.join("framework").join("KERNEL.yaml").exists() {
        Some(c.canonicalize().unwrap_or(c))
    } else {
        None
    }
}

/// Kernel source precedence: explicit --source > GOV_CANONICAL_ROOT (developer checkout) > embedded payload.
pub fn resolve_kernel_source(source: Option<&Path>) -> Result<PathBuf> {
    let src = match source {
        Some(s) => s.to_path_buf(),
        None => match canonical_root() {
            Some(r) => r.join("framework"),
            None => embedded_kernel_dir()?,
        },
    };
    for cand in [src.clone(), src.join("kernel"), src.join("framework")] {
        if cand.join("KERNEL.yaml").exists() {
            return Ok(cand);
        }
    }
    Err(GovError::new(
        "KERNEL_SOURCE_NOT_FOUND",
        format!("no kernel payload found at {}", src.display()),
    ))
}

/// Whether `src` is the directory this binary materialises its embedded payload into.
///
/// `BC-P2-37`: decided by identity with [`embedded_kernel_dir`]'s own location, never by a path pattern. The old
/// test (`/kernels/` and `.cache` in the path) made the recorded identity depend on where `XDG_CACHE_HOME` pointed
/// (A0-A2-03). What is finally recorded in `framework.lock` is decided by content in [`crate::lock::write_lock`].
pub fn is_embedded_dir(src: &Path) -> bool {
    let canon = |p: &Path| std::fs::canonicalize(p).unwrap_or_else(|_| p.to_path_buf());
    match embedded_kernel_path() {
        Ok(e) => canon(src) == canon(&e),
        Err(_) => false,
    }
}

/// Marker recorded wherever a release commit is not established by anything verification can stand on.
pub const RELEASE_COMMIT_UNVERIFIED: &str = "unverified";

/// The framework release commit for a kernel source (verifier M-N1), **as far as verification can establish it**.
///
/// `BC-P2-37` (Contract v3:149 "recorded, not invented"; D-0007 rule 2): the commit baked into this binary is
/// returned for its own embedded payload; nothing else a source directory carries — an unsigned `manifest.json`
/// beside `kernel/`, the Git HEAD of a checkout — is authenticated, so neither is returned as identity. A release
/// commit bound by **signed** release metadata is recorded by [`crate::lock::write_lock`] from this machine's
/// protected installation record. Never the consumer repository's HEAD.
pub fn release_commit_for_source(src: &Path) -> String {
    if is_embedded_dir(src) {
        return embedded::commit().to_string();
    }
    RELEASE_COMMIT_UNVERIFIED.into()
}

/// Logical, machine-independent source label (a *kind*, not an authenticated identity).
///
/// `embedded:` for this binary's own payload directory, otherwise `source:`. `release:` is reserved for a release
/// authenticated by signed metadata and is assigned only by [`crate::lock::write_lock`] from the protected
/// installation record; a path segment such as `/release/releases/` no longer produces it (Contract v3:950).
pub fn source_label(src: &Path) -> String {
    let meta = kernel_meta(src).unwrap_or(serde_json::json!({}));
    let ver = meta
        .get("version")
        .map(|v| match v {
            Value::String(s) => s.clone(),
            o => o.to_string(),
        })
        .unwrap_or("unknown".into());
    if is_embedded_dir(src) {
        return format!("embedded:{}@{}", FRAMEWORK_NAME, ver);
    }
    format!("source:{}@{}", FRAMEWORK_NAME, ver)
}

pub fn kernel_meta(kernel_dir: &Path) -> Result<Value> {
    read_yaml(&kernel_dir.join("KERNEL.yaml"))
}

pub fn payload_files(kernel_dir: &Path) -> Result<BTreeMap<String, String>> {
    Ok(hash_tree(kernel_dir, &[KERNEL_MANIFEST])?.1)
}

pub fn build_manifest(kernel_dir: &Path) -> Result<Value> {
    let meta = kernel_meta(kernel_dir)?;
    let files = payload_files(kernel_dir)?;
    let files_v = serde_json::to_value(&files)?;
    let s = |k: &str, d: &str| {
        meta.get(k)
            .map(|v| match v {
                Value::String(x) => x.clone(),
                other => other.to_string(),
            })
            .unwrap_or(d.to_string())
    };
    Ok(json!({
        "framework": s("framework", FRAMEWORK_NAME),
        "version": s("version", VERSION),
        "files": files_v.clone(),
        "payload_hash": hash_value(&files_v),
        "schema_versions": meta.get("schema_versions").cloned().unwrap_or(json!({})),
        "cli_version": s("cli_version", VERSION),
        "runtime_version": s("runtime_version", VERSION),
        "adapter_versions": meta.get("adapter_versions").cloned().unwrap_or(json!({})),
        "supported_from_versions": meta.get("supported_from_versions").cloned().unwrap_or(json!([])),
    }))
}

/// Copy the payload dirs listed in KERNEL.yaml into `dest` (fresh). `migrations` may live next to framework/.
pub fn stage_payload(source_dir: &Path, dest: &Path) -> Result<()> {
    remove_dir_if_exists(dest)?;
    std::fs::create_dir_all(dest)?;
    let meta = kernel_meta(source_dir)?;
    for d in meta
        .get("payload_dirs")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default()
    {
        let d = d.as_str().unwrap_or("").to_string();
        let mut src = source_dir.join(&d);
        if !src.exists() && (d == "migrations" || d == "tools") {
            let cand = source_dir.parent().map(|p| p.join(&d)).unwrap_or_default();
            if cand.exists() {
                src = cand;
            }
        }
        if src.exists() {
            copy_dir(&src, &dest.join(&d))?;
        }
    }
    std::fs::copy(source_dir.join("KERNEL.yaml"), dest.join("KERNEL.yaml"))?;
    Ok(())
}

/// Install a kernel payload into `governance/` from a **typed authenticated-release value**.
///
/// ARCH-0003 §6: "Every privileged lifecycle adapter must call one verification policy and receive a typed
/// authenticated-release value, **never a raw source directory**." That rule is enforced here by the signature:
/// the only way to obtain an [`crate::srr::AuthenticatedRelease`] is [`crate::srr::admit`], so no ingress can
/// install bytes that the single verifier has not staged, measured and admitted. There is no path-taking variant.
///
/// The bytes installed are `auth.verified_payload()` — the private staging copy that was measured — and the commit
/// is the atomic, crash-safe transaction in [`crate::srr::staging`].
pub fn install_kernel(
    auth: &crate::srr::AuthenticatedRelease,
    governance_dir: &Path,
) -> Result<Value> {
    let r = install_kernel_inner(auth, governance_dir);
    crate::kernel_trust::clear();
    r
}

fn install_kernel_inner(
    auth: &crate::srr::AuthenticatedRelease,
    governance_dir: &Path,
) -> Result<Value> {
    let dest = governance_dir.join("kernel");
    // BC-P2-38 — the reinstall ingress restores the release the project pins; it is not a version change. The
    // refusal used to come from the caller only AFTER the swap, leaving the new payload under the old lock (a mixed
    // installation, A2-08 [V1]-[V3], A2-05 [K6a]). It is taken here, before a single byte moves, and the staging
    // area is abandoned, so a refused reinstall leaves the installation exactly as it found it. The caller's own
    // check stays as a second line; it can no longer be reached with a committed payload.
    pinned_release_check(auth, governance_dir).inspect_err(|e| {
        crate::srr::staging::abandon(&auth.machine, &auth.staged, &e.message);
    })?;
    // BC-P2-35 — this machine's protected record of what it commits into this project. `pending` is durable
    // before the swap and `current` after its verification, so whichever tree an interrupted install recovers to
    // is bound by one of them.
    let project_root = crate::srr::installation::project_root_of_governance_dir(governance_dir);
    if let Some(root) = project_root.as_ref() {
        crate::srr::installation::bind_pending(auth, root).inspect_err(|e| {
            crate::srr::staging::abandon(&auth.machine, &auth.staged, &e.message);
        })?;
    }
    if let Err(e) = crate::srr::staging::commit_tree(&auth.machine, &auth.staged, &dest) {
        if let Some(root) = project_root.as_ref() {
            crate::srr::installation::clear_pending(auth, root);
        }
        return Err(e);
    }
    let manifest = read_manifest(&dest)?;
    // The installed payload must be the verified payload, byte for byte.
    if manifest["payload_hash"].as_str() != Some(auth.payload_hash.as_str()) {
        return Err(GovError::new(
            "SRR_COMMITTED_BYTES_MISMATCH",
            "the installed kernel payload digest differs from the verified release payload digest",
        ));
    }
    if let Some(root) = project_root.as_ref() {
        crate::srr::installation::bind_committed(auth, root)?;
    }
    Ok(manifest)
}

/// `KERNEL_MISMATCH`, before the swap, when the reinstall ingress is handed a payload other than the pinned one.
///
/// Only the reinstall ingress is bound by the project's pin: init, adopt and update install a new pin, and rollback
/// and recovery restore an earlier one. A project with no lock yet has nothing pinned.
fn pinned_release_check(
    auth: &crate::srr::AuthenticatedRelease,
    governance_dir: &Path,
) -> Result<()> {
    if auth.ingress != crate::srr::Ingress::Reinstall {
        return Ok(());
    }
    let Ok(lock) = read_yaml(&governance_dir.join("framework.lock")) else {
        return Ok(());
    };
    let pinned = lock
        .get("release_hash")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    if pinned.is_empty() || pinned == auth.payload_hash {
        return Ok(());
    }
    // BC-P2-35: on a machine with a trust anchor, this machine's protected record of what it committed into the
    // project is the authority for what "the pinned release" was, not a framework.lock the repository can rewrite. A
    // candidate that IS the recorded payload while the lock pins something else means the pin itself was rewritten
    // (with the payload and manifest). That is refused precisely, with the values to restore, before anything moves.
    if auth.posture == crate::srr::verifier::Posture::Provisioned {
        let recorded = governance_dir
            .parent()
            .and_then(crate::srr::installation::project_record)
            .and_then(|r| r.current);
        if let Some(r) = recorded.filter(|r| r.payload_hash == auth.payload_hash) {
            return Err(GovError::new(
                "KERNEL_PIN_REWRITTEN",
                "framework.lock pins a payload this machine never committed into this project, while the candidate is exactly the payload it did commit: the pin was rewritten together with the kernel. Restore framework.lock's release_hash and kernel_manifest_hash to the recorded values (from version control, or as given in the details), then re-run `gov kernel reinstall`.",
            )
            .with_details(json!({
                "framework_lock_pins": {"release_hash": pinned, "kernel_manifest_hash": lock.get("kernel_manifest_hash")},
                "this_machine_committed": {"release_hash": r.payload_hash, "kernel_manifest_hash": r.kernel_manifest_hash, "release_version": r.release_version, "ingress": r.ingress, "at": r.at},
                "installation_changed": false,
            })));
        }
    }
    Err(GovError::new(
        "KERNEL_MISMATCH",
        "reinstalled payload hash differs from framework.lock release_hash; use gov update for a version change",
    )
    .with_details(json!({
        "pinned_release_hash": pinned,
        "candidate_payload_hash": auth.payload_hash,
        "candidate_release": auth.release_version,
        "installation_changed": false,
        "note": "refused before the atomic swap: the installed kernel, framework.lock and this machine's protected records are unchanged (BC-P2-38). `gov kernel reinstall` restores the pinned release; `gov update --apply` changes version and `gov update --rollback` returns to the previous one.",
    })))
}

pub fn read_manifest(kernel_dir: &Path) -> Result<Value> {
    let p = kernel_dir.join(KERNEL_MANIFEST);
    if !p.exists() {
        return Err(GovError::new(
            "KERNEL_MANIFEST_MISSING",
            format!("kernel manifest missing at {}", p.display()),
        ));
    }
    read_json(&p)
}

pub fn manifest_hash(manifest: &Value) -> String {
    let mut m = serde_json::Map::new();
    for k in ["framework", "version", "files", "payload_hash"] {
        if let Some(v) = manifest.get(k) {
            m.insert(k.to_string(), v.clone());
        }
    }
    hash_value(&Value::Object(m))
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct KernelVerification {
    pub ok: bool,
    pub modified: Vec<String>,
    pub missing: Vec<String>,
    pub added: Vec<String>,
    pub payload_hash: String,
    pub version: String,
    /// Digest of the payload files actually on disk, measured exactly as staging measures them. `payload_hash`
    /// above is what `KERNEL_MANIFEST.json` *claims*.
    pub measured_payload_hash: String,
    /// The files match `KERNEL_MANIFEST.json` (the original D-0007 comparison, on its own).
    pub matches_manifest: bool,
    /// `BC-P2-35`: the installed files differ from what this machine committed into this project (its protected
    /// installation record), whatever `KERNEL_MANIFEST.json` and `framework.lock` say. An enforced divergence puts the
    /// differing files in `modified` / `missing` / `added` and makes `ok` false; since OWNER-DECISION-P2-0002 every
    /// divergence is enforced, on a machine with no trust anchor as well (the payload embedded in the running binary
    /// never diverges there: it is the bootstrap baseline).
    pub diverges_from_protected_record: bool,
    pub protected_record_enforced: bool,
    pub protected_record_payload_hash: String,
    pub protected_record_divergence: Value,
}

/// D-0007 post-install integrity of an installed kernel directory.
///
/// Intact means: the payload matches `KERNEL_MANIFEST.json` file for file **and**, where this machine holds a
/// protected record of what it committed into the project (`<root>/governance/kernel`), the payload is exactly that
/// record. The second clause is `BC-P2-35` (Contract v3:146): the manifest and the lock live in the repository and a
/// mutually consistent rewrite of payload, manifest and lock satisfied the first clause alone.
pub fn verify_kernel(kernel_dir: &Path) -> Result<KernelVerification> {
    let manifest = read_manifest(kernel_dir)?;
    let actual = payload_files(kernel_dir)?;
    let expected: BTreeMap<String, String> = manifest
        .get("files")
        .and_then(|f| serde_json::from_value(f.clone()).ok())
        .unwrap_or_default();
    let mut modified: Vec<String> = expected
        .iter()
        .filter(|(p, h)| actual.get(*p).map(|a| a != *h).unwrap_or(false))
        .map(|(p, _)| p.clone())
        .collect();
    let mut missing: Vec<String> = expected
        .keys()
        .filter(|p| !actual.contains_key(*p))
        .cloned()
        .collect();
    let mut added: Vec<String> = actual
        .keys()
        .filter(|p| !expected.contains_key(*p))
        .cloned()
        .collect();
    let measured_payload_hash = hash_value(&serde_json::to_value(&actual)?);
    let matches_manifest = modified.is_empty() && missing.is_empty() && added.is_empty();
    let divergence = crate::srr::installation::divergence(kernel_dir, &actual);
    let enforced = divergence.as_ref().map(|d| d.enforced).unwrap_or(false);
    if let Some(d) = divergence.as_ref().filter(|d| d.enforced) {
        for (into, from) in [
            (&mut modified, &d.modified),
            (&mut missing, &d.missing),
            (&mut added, &d.added),
        ] {
            for p in from {
                if !into.contains(p) {
                    into.push(p.clone());
                }
            }
            into.sort();
        }
    }
    Ok(KernelVerification {
        ok: modified.is_empty() && missing.is_empty() && added.is_empty() && !enforced,
        modified,
        missing,
        added,
        payload_hash: manifest
            .get("payload_hash")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string(),
        version: manifest
            .get("version")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string(),
        measured_payload_hash,
        matches_manifest,
        diverges_from_protected_record: divergence.is_some(),
        protected_record_enforced: enforced,
        protected_record_payload_hash: divergence
            .as_ref()
            .map(|d| d.recorded_payload_hash.clone())
            .unwrap_or_default(),
        protected_record_divergence: divergence
            .map(|d| json!({"modified": d.modified, "missing": d.missing, "added": d.added, "enforced": d.enforced}))
            .unwrap_or(Value::Null),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    /// BC-P2-37: the embedded payload's identity is computed from its bytes and equals what staging would measure,
    /// so "is this the embedded payload?" is decided by content and never by a cache path.
    #[test]
    fn the_embedded_payload_digest_is_what_staging_measures() {
        let base = std::env::temp_dir().join(format!("gov-ws08-emb-{}", crate::util::short_uuid()));
        let src = base.join("src");
        for (rel, bytes) in embedded::files() {
            let p = src.join(rel);
            std::fs::create_dir_all(p.parent().unwrap()).unwrap();
            std::fs::write(&p, bytes).unwrap();
        }
        let dst = base.join("staged");
        stage_payload(&src, &dst).unwrap();
        let m = build_manifest(&dst).unwrap();
        assert_eq!(m["payload_hash"].as_str().unwrap(), embedded_payload_hash());
        let _ = std::fs::remove_dir_all(&base);
    }

    /// IP-WS02-15: a cache directory is re-used only when it is exactly the embedded listing — the old test
    /// (`KERNEL.yaml` and `.complete` present) accepted a directory missing files, and would have accepted one with
    /// extra files or a marker naming another listing.
    #[test]
    fn a_kernel_cache_is_reused_only_when_it_is_exactly_the_embedded_listing() {
        let base =
            std::env::temp_dir().join(format!("gov-ws08-cache-{}", crate::util::short_uuid()));
        let write_all = |d: &Path| {
            for (rel, bytes) in embedded::files() {
                let p = d.join(rel);
                std::fs::create_dir_all(p.parent().unwrap()).unwrap();
                std::fs::write(&p, bytes).unwrap();
            }
            std::fs::write(
                d.join(CACHE_COMPLETE_MARKER),
                embedded_listing().1.as_bytes(),
            )
            .unwrap();
        };
        let exact = base.join("exact");
        write_all(&exact);
        assert!(cache_matches_listing(&exact));
        let missing = base.join("missing");
        write_all(&missing);
        std::fs::remove_file(missing.join("policies").join("SECURITY_POLICY.yaml")).unwrap();
        assert!(missing.join("KERNEL.yaml").exists() && !cache_matches_listing(&missing));
        let extra = base.join("extra");
        write_all(&extra);
        std::fs::write(extra.join("policies").join("INJECTED.yaml"), "x: 1\n").unwrap();
        assert!(!cache_matches_listing(&extra));
        let altered = base.join("altered");
        write_all(&altered);
        std::fs::write(altered.join("KERNEL.yaml"), "framework: other\n").unwrap();
        assert!(!cache_matches_listing(&altered));
        let marker = base.join("marker");
        write_all(&marker);
        std::fs::write(marker.join(CACHE_COMPLETE_MARKER), "another-listing").unwrap();
        assert!(!cache_matches_listing(&marker));
        let _ = std::fs::remove_dir_all(&base);
    }
}
