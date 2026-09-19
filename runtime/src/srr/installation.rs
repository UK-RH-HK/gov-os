//! Signed Release Root v1 — **this machine's protected records of what it installed, and of what it verified**.
//!
//! Phase-2 repair iteration 1, WS-8: `BC-P2-35` (post-install integrity against the machine's own protected record),
//! `BC-P2-36` (an installation whose authenticity is not established is never presented as current), `BC-P2-38`
//! (the rollback ingress can restore a release this machine previously verified).
//!
//! ## The two records
//!
//! ```text
//! <state_root>/installed/<product>/projects/<key>.json    one per project: the exact payload (per-file digests)
//!                                                          this machine committed into that project, and what the
//!                                                          single verifier decided about it
//! <state_root>/installed/<product>/verified/<digest>.json  one per payload digest: a release this machine
//!                                                          AUTHENTICATED (signed metadata, or its own earlier
//!                                                          verification). Never written for authenticity UNKNOWN.
//! ```
//!
//! Both live in protected machine state, outside every project, beside the single `installed/<product>.json`
//! record the R1 verifier already keeps. A project, its `KERNEL_MANIFEST.json`, its `framework.lock` and any
//! mutually consistent files delivered with it can change none of them.
//!
//! ## How this connects the domains — by digest, and only by digest
//!
//! ARCH-0003 §2: "Release authenticity, local installation authority, post-install integrity, … are separate
//! domains. Evidence may connect domains by digest, but no domain silently substitutes for another." So:
//!
//! * **post-install integrity** (D-0007: `crate::kernel_trust` and `crate::kernel::verify_kernel`) asks this module
//!   only digest questions — "which per-file digests did this machine commit here?" ([`divergence`]) and "does a
//!   protected record bind these digests, and does this machine's posture require one?" ([`anchor_for`]). It never
//!   reads an authenticity verdict; D-0007 still establishes only that a copy is *intact*, now intact against a
//!   record the repository cannot rewrite (Contract v3:146) as well as against its own manifest and lock.
//! * **authenticity** questions — may this installation be presented as current ([`posture_of`]), may the rollback
//!   ingress admit these bytes offline ([`verified_release`]) — are answered here, in the SRR domain.
//!
//! D-0007's text is unchanged: rule 1 already provides that "when T1 cannot be authenticated, the embedded baseline
//! is substituted explicitly and mutating operations fail closed". What changes is that a consistent rewrite of the
//! payload, the manifest and the lock is now a T1 that cannot be authenticated.
//!
//! ## What a machine with no trust anchor gets (OD-P2-02 is with the owner)
//!
//! Admission is untouched. The per-project record is still written — it records what was *installed*, with
//! authenticity `UNKNOWN` — so a consistent post-install rewrite of a project this machine installed is detected on
//! every posture. Nothing on such a machine is ever presented as authentic, current or verified ([`posture_of`]).
use crate::srr::state::{resolve_state_root, write_durable, MachineState};
use crate::srr::verifier::{AuthenticatedRelease, Authenticity};
use crate::util::{hash_value, now_iso, read_json, sha256_text};
use crate::{Result, FRAMEWORK_NAME};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

/// Does an authenticity recorded in protected state record a **verification**?
///
/// `AUTHENTIC` (signed metadata chaining to the trusted root) and `PREVIOUSLY_VERIFIED_BY_THIS_MACHINE` do.
/// `UNKNOWN` (no trust anchor) records only that bytes were installed.
pub fn records_a_verification(authenticity: &str) -> bool {
    authenticity == Authenticity::Authentic.as_str()
        || authenticity == Authenticity::PreviouslyVerifiedByThisMachine.as_str()
}

// ---------------------------------------------------------------------------------------------- the records

/// One payload bound in protected state: its digests and what the single verifier decided about it.
#[derive(Debug, Clone, Default)]
pub struct BoundPayload {
    pub payload_hash: String,
    pub kernel_manifest_hash: String,
    /// Per-file SHA-256 of the committed payload, so a divergence names the files, not only the aggregate.
    pub files: BTreeMap<String, String>,
    pub release_version: String,
    pub sequence: u64,
    pub channel: String,
    pub authenticity: String,
    pub posture: String,
    pub release_metadata_sha256: String,
    /// Empty unless the **signed** release metadata binds a release commit (`evidence.provenance.release_commit`).
    pub release_commit: String,
    pub ingress: String,
    pub at: String,
}

impl BoundPayload {
    fn of(auth: &AuthenticatedRelease) -> BoundPayload {
        BoundPayload {
            payload_hash: auth.payload_hash.clone(),
            kernel_manifest_hash: auth.kernel_manifest_hash.clone(),
            files: auth.staged.files.clone(),
            release_version: auth.release_version.clone(),
            sequence: auth.sequence,
            channel: auth.channel.clone(),
            authenticity: auth.authenticity.as_str().to_string(),
            posture: match auth.posture {
                crate::srr::verifier::Posture::Provisioned => "PROVISIONED".into(),
                crate::srr::verifier::Posture::Unprovisioned => "UNPROVISIONED".into(),
            },
            release_metadata_sha256: auth.release_metadata_sha256.clone(),
            release_commit: signed_release_commit(&auth.evidence),
            ingress: auth.ingress.as_str().to_string(),
            at: now_iso(),
        }
    }

    pub fn to_value(&self) -> Value {
        json!({
            "payload_hash": self.payload_hash, "kernel_manifest_hash": self.kernel_manifest_hash,
            "files": self.files, "release_version": self.release_version, "sequence": self.sequence,
            "channel": self.channel, "authenticity": self.authenticity, "posture": self.posture,
            "release_metadata_sha256": self.release_metadata_sha256, "release_commit": self.release_commit,
            "ingress": self.ingress, "at": self.at,
        })
    }

    pub fn from_value(v: &Value) -> Option<BoundPayload> {
        let payload_hash = v.get("payload_hash")?.as_str()?.to_string();
        if payload_hash.is_empty() {
            return None;
        }
        let s = |k: &str| v.get(k).and_then(|x| x.as_str()).unwrap_or("").to_string();
        Some(BoundPayload {
            payload_hash,
            kernel_manifest_hash: s("kernel_manifest_hash"),
            files: v
                .get("files")
                .and_then(|f| serde_json::from_value(f.clone()).ok())
                .unwrap_or_default(),
            release_version: s("release_version"),
            sequence: v.get("sequence").and_then(|x| x.as_u64()).unwrap_or(0),
            channel: s("channel"),
            authenticity: s("authenticity"),
            posture: s("posture"),
            release_metadata_sha256: s("release_metadata_sha256"),
            release_commit: s("release_commit"),
            ingress: s("ingress"),
            at: s("at"),
        })
    }

    /// Digest match. The manifest digest is compared whenever both sides carry one.
    pub fn binds(&self, payload_hash: &str, kernel_manifest_hash: &str) -> bool {
        self.payload_hash == payload_hash
            && (self.kernel_manifest_hash.is_empty()
                || kernel_manifest_hash.is_empty()
                || self.kernel_manifest_hash == kernel_manifest_hash)
    }

    /// The identity this record states, without the per-file map (for reports).
    pub fn summary(&self) -> Value {
        json!({
            "release_version": self.release_version, "sequence": self.sequence, "channel": self.channel,
            "payload_hash": self.payload_hash, "kernel_manifest_hash": self.kernel_manifest_hash,
            "authenticity": self.authenticity, "posture_at_install": self.posture,
            "release_metadata_sha256": self.release_metadata_sha256, "ingress": self.ingress, "at": self.at,
        })
    }
}

/// A release commit is identity only when the signed release metadata binds it (ARCH-0003 §4: release metadata
/// carries "optional digest references to provenance … evidence"). An unsigned `manifest.json` never supplies it.
pub fn signed_release_commit(evidence: &Value) -> String {
    evidence
        .get("provenance")
        .and_then(|p| p.get("release_commit"))
        .or_else(|| evidence.get("release_commit"))
        .and_then(|c| c.as_str())
        .unwrap_or("")
        .to_string()
}

/// The per-project record: what this machine committed into one project.
///
/// `pending` is written immediately before the atomic swap and `current` immediately after its verification, so an
/// interrupted install that recovery completes (or reverts) always leaves an installed payload that one of the two
/// binds. Both are payloads the single verifier admitted for this project.
#[derive(Debug, Clone, Default)]
pub struct ProjectRecord {
    pub project_root: String,
    pub current: Option<BoundPayload>,
    pub pending: Option<BoundPayload>,
}

impl ProjectRecord {
    fn from_value(v: &Value) -> ProjectRecord {
        ProjectRecord {
            project_root: v
                .get("project_root")
                .and_then(|x| x.as_str())
                .unwrap_or("")
                .to_string(),
            current: v.get("current").and_then(BoundPayload::from_value),
            pending: v.get("pending").and_then(BoundPayload::from_value),
        }
    }

    fn to_value(&self, product: &str) -> Value {
        json!({
            "product": product,
            "project_root": self.project_root,
            "current": self.current.as_ref().map(|b| b.to_value()),
            "pending": self.pending.as_ref().map(|b| b.to_value()),
            "updated_at": now_iso(),
            "note": "BC-P2-35: this machine's own protected record of the kernel payload it committed into this project. Post-install integrity is checked against it; a project, its KERNEL_MANIFEST.json and its framework.lock cannot rewrite it.",
        })
    }

    /// The bound payload the given digests match, `current` first.
    pub fn binding(&self, payload_hash: &str, kernel_manifest_hash: &str) -> Option<&BoundPayload> {
        self.current
            .as_ref()
            .filter(|b| b.binds(payload_hash, kernel_manifest_hash))
            .or_else(|| {
                self.pending
                    .as_ref()
                    .filter(|b| b.binds(payload_hash, kernel_manifest_hash))
            })
    }

    fn records_anything(&self) -> bool {
        self.current.is_some() || self.pending.is_some()
    }
}

/// The canonical form of a project root, so one project reached by two spellings has one record.
pub fn canonical_project_root(root: &Path) -> PathBuf {
    std::fs::canonicalize(root).unwrap_or_else(|_| root.to_path_buf())
}

fn project_key(root: &Path) -> String {
    sha256_text(&canonical_project_root(root).display().to_string())[..32].to_string()
}

fn hex_only(s: &str) -> String {
    s.chars()
        .filter(|c| c.is_ascii_hexdigit())
        .take(64)
        .collect()
}

fn project_record_path(ms: &MachineState, product: &str, root: &Path) -> PathBuf {
    ms.installed_dir(product)
        .join("projects")
        .join(format!("{}.json", project_key(root)))
}

fn verified_record_path(ms: &MachineState, product: &str, payload_hash: &str) -> PathBuf {
    ms.installed_dir(product)
        .join("verified")
        .join(format!("{}.json", hex_only(payload_hash)))
}

/// The project root that owns an installed kernel directory (`<root>/governance/kernel`), if it has that shape.
pub fn project_root_of_kernel_dir(kernel_dir: &Path) -> Option<PathBuf> {
    let gov = kernel_dir.parent()?;
    if kernel_dir.file_name()? != "kernel" || gov.file_name()? != "governance" {
        return None;
    }
    gov.parent().map(|p| p.to_path_buf())
}

/// The project root that owns a governance directory (`<root>/governance`).
pub fn project_root_of_governance_dir(governance_dir: &Path) -> Option<PathBuf> {
    if governance_dir.file_name()? != "governance" {
        return None;
    }
    governance_dir.parent().map(|p| p.to_path_buf())
}

// ---------------------------------------------------------------------------------------------- read-only view

/// Protected state as a reader sees it. Resolution can fail only on the input the product already classifies as
/// hostile (`GOV_MACHINE_STATE_DIR` pointing elsewhere on a provisioned machine); that is reported, not guessed.
enum View {
    Resolved(MachineState),
    Undetermined(String),
}

fn view() -> View {
    match resolve_state_root() {
        Ok(root) => View::Resolved(MachineState::read_only(&root)),
        Err(e) => View::Undetermined(format!("{}: {}", e.code, e.message)),
    }
}

/// Identifies the protected state a verdict was computed against (cache keys must not outlive a change of machine).
pub fn state_key() -> String {
    match view() {
        View::Resolved(ms) => ms.root.display().to_string(),
        View::Undetermined(_) => "UNDETERMINED".into(),
    }
}

fn load_project_record(ms: &MachineState, product: &str, root: &Path) -> Option<ProjectRecord> {
    read_json(&project_record_path(ms, product, root))
        .ok()
        .map(|v| ProjectRecord::from_value(&v))
}

/// This machine's record for a project, read-only. `None` when there is none or protected state is undetermined.
pub fn project_record(project_root: &Path) -> Option<ProjectRecord> {
    match view() {
        View::Resolved(ms) => load_project_record(&ms, FRAMEWORK_NAME, project_root),
        View::Undetermined(_) => None,
    }
}

/// A release this machine authenticated, by payload digest. Never a record of an `UNKNOWN` install.
pub fn verified_release(
    ms: &MachineState,
    product: &str,
    payload_hash: &str,
    kernel_manifest_hash: &str,
) -> Option<BoundPayload> {
    read_json(&verified_record_path(ms, product, payload_hash))
        .ok()
        .and_then(|v| BoundPayload::from_value(&v))
        .filter(|b| records_a_verification(&b.authenticity))
        .filter(|b| b.binds(payload_hash, kernel_manifest_hash))
}

// ---------------------------------------------------------------------------------------------- writes

/// Before the atomic swap: record the payload about to be committed as `pending`, beside the current record.
pub fn bind_pending(auth: &AuthenticatedRelease, project_root: &Path) -> Result<()> {
    bind_pending_in(
        &auth.machine,
        &auth.product,
        project_root,
        BoundPayload::of(auth),
    )
}

/// After the swap and the verification of the committed bytes: the committed payload becomes `current`, and an
/// authenticated release enters this machine's verified-release ledger.
pub fn bind_committed(auth: &AuthenticatedRelease, project_root: &Path) -> Result<()> {
    bind_committed_in(
        &auth.machine,
        &auth.product,
        project_root,
        BoundPayload::of(auth),
    )?;
    record_verified(auth)
}

/// [`bind_pending`] against an explicit protected state.
pub fn bind_pending_in(
    ms: &MachineState,
    product: &str,
    project_root: &Path,
    payload: BoundPayload,
) -> Result<()> {
    let mut rec = load_project_record(ms, product, project_root).unwrap_or_default();
    rec.project_root = canonical_project_root(project_root).display().to_string();
    rec.pending = Some(payload);
    write_durable(
        &project_record_path(ms, product, project_root),
        &rec.to_value(product),
    )
}

/// [`bind_committed`] (without the ledger) against an explicit protected state.
pub fn bind_committed_in(
    ms: &MachineState,
    product: &str,
    project_root: &Path,
    payload: BoundPayload,
) -> Result<()> {
    let mut rec = load_project_record(ms, product, project_root).unwrap_or_default();
    rec.project_root = canonical_project_root(project_root).display().to_string();
    rec.current = Some(payload);
    rec.pending = None;
    write_durable(
        &project_record_path(ms, product, project_root),
        &rec.to_value(product),
    )
}

/// The swap did not happen (refused or reverted): drop `pending`, keep `current`.
pub fn clear_pending(auth: &AuthenticatedRelease, project_root: &Path) {
    let ms = &auth.machine;
    if let Some(mut rec) = load_project_record(ms, &auth.product, project_root) {
        if rec.pending.is_some() {
            rec.pending = None;
            let _ = write_durable(
                &project_record_path(ms, &auth.product, project_root),
                &rec.to_value(&auth.product),
            );
        }
    }
}

/// The raw per-project record, for a transaction that may have to put it back ([`restore_project_record`]).
pub fn read_project_record_raw(project_root: &Path) -> Option<Value> {
    match view() {
        View::Resolved(ms) => {
            read_json(&project_record_path(&ms, FRAMEWORK_NAME, project_root)).ok()
        }
        View::Undetermined(_) => None,
    }
}

/// Put back the per-project record read before a transaction that is now being aborted.
///
/// `update --apply` restores the pre-update kernel bytes from its own snapshot when the post-install suite fails
/// (the transaction abort of `SRR-R0-L5`); the record must describe the bytes that are installed afterwards, which
/// are exactly the bytes it described before. `None` removes a record that the aborted transaction created.
pub fn restore_project_record(project_root: &Path, prior: Option<Value>) -> Result<()> {
    let ms = MachineState::open()?;
    let path = project_record_path(&ms, FRAMEWORK_NAME, project_root);
    match prior {
        Some(v) => write_durable(&path, &v),
        None => {
            let _ = std::fs::remove_file(&path);
            Ok(())
        }
    }
}

/// Enter an authenticated release into this machine's verified-release ledger (idempotent).
///
/// Keyed by payload digest. When the release role has bound the same bytes under more than one sequence, the
/// highest is kept: it is the latest identity the signed metadata gave these exact bytes, and the floor check
/// applies to it like any other.
pub fn record_verified(auth: &AuthenticatedRelease) -> Result<()> {
    if !auth.authenticity.is_authenticated() {
        return Ok(());
    }
    record_verified_in(&auth.machine, &auth.product, BoundPayload::of(auth))
}

/// [`record_verified`] against an explicit protected state. A payload that does not record a verification is never
/// entered.
pub fn record_verified_in(ms: &MachineState, product: &str, payload: BoundPayload) -> Result<()> {
    if !records_a_verification(&payload.authenticity) {
        return Ok(());
    }
    let path = verified_record_path(ms, product, &payload.payload_hash);
    let mut entry = payload;
    let mut first = entry.at.clone();
    if let Some((prev, prev_first)) = read_json(&path).ok().and_then(|v| {
        let f = v
            .get("first_verified_at")
            .and_then(|x| x.as_str())
            .map(String::from);
        BoundPayload::from_value(&v).map(|b| (b, f))
    }) {
        if let Some(f) = prev_first {
            first = f;
        }
        if records_a_verification(&prev.authenticity) && prev.sequence > entry.sequence {
            entry = prev;
        }
    }
    let mut v = entry.to_value();
    v["files"] = Value::Null;
    v["first_verified_at"] = json!(first);
    v["last_verified_at"] = json!(now_iso());
    v["note"] = json!("BC-P2-38: a release this machine authenticated and installed, bound by payload digest. The rollback and recovery ingresses may derive offline authenticity from it (ARCH-0003 §7); the floor check still applies.");
    write_durable(&path, &v)
}

// ---------------------------------------------------------------------------------------------- D-0007 questions

/// How an installed payload stands against this machine's protected records. Digest-level only.
#[derive(Debug, Clone)]
pub enum Anchor {
    /// A protected record on this machine binds exactly these digests.
    Matched { basis: String },
    /// This machine recorded what it committed into this project, and the installed payload is not that: a
    /// post-install rewrite however consistent its manifest and lock are, or a change made without an ingress on
    /// this machine (another machine's update arriving through Git, a checkout of an older kernel).
    ///
    /// `enforced` — this machine holds a trust anchor, so the record it diverges from is part of the determined
    /// requirement (BC-P2-35) and the installed kernel is untrusted T1 until it matches. On a machine with no trust
    /// anchor the record is itself unauthenticated; that sub-case is OD-P2-02, with the owner, so the divergence is
    /// reported (kernel trust detail, presentation) and not enforced.
    Diverged {
        basis: String,
        recorded_payload_hash: String,
        enforced: bool,
    },
    /// No protected record binds this installation. `required` — this machine holds a trust anchor, so the
    /// installed kernel must be verified against the pinned release before privileged work (ARCH-0003 §8).
    Unrecorded { required: bool, basis: String },
    /// Protected state could not be resolved (the hostile override input); the §6 guards refuse it themselves.
    Undetermined { basis: String },
}

impl Anchor {
    pub fn state(&self) -> &'static str {
        match self {
            Anchor::Matched { .. } => "MATCHED",
            Anchor::Diverged { enforced: true, .. } => "DIVERGED",
            Anchor::Diverged {
                enforced: false, ..
            } => "DIVERGED_NOT_ENFORCED",
            Anchor::Unrecorded { required: true, .. } => "UNRECORDED_REQUIRED",
            Anchor::Unrecorded {
                required: false, ..
            } => "UNRECORDED",
            Anchor::Undetermined { .. } => "UNDETERMINED",
        }
    }
    pub fn basis(&self) -> &str {
        match self {
            Anchor::Matched { basis }
            | Anchor::Diverged { basis, .. }
            | Anchor::Unrecorded { basis, .. }
            | Anchor::Undetermined { basis } => basis,
        }
    }
    /// Does the installed kernel stand against the protected records as D-0007 needs it to?
    pub fn holds(&self) -> bool {
        !matches!(
            self,
            Anchor::Diverged { enforced: true, .. } | Anchor::Unrecorded { required: true, .. }
        )
    }
}

/// Measure an installed payload against this machine's protected records.
///
/// * a per-project record exists and binds the digests → `Matched` (on a machine with a trust anchor, only if the
///   record records a verification; otherwise the ledger is consulted, below);
/// * a per-project record exists and binds neither `current` nor `pending` → `Diverged` (enforced only on a machine
///   with a trust anchor; see [`Anchor::Diverged`]);
/// * no usable per-project record, machine holds a trust anchor → the verified-release ledger (a release this machine
///   authenticated, by digest); else `Unrecorded { required: true }`;
/// * no record, no trust anchor → `Unrecorded { required: false }` (OD-P2-02: posture decided by the owner).
pub fn anchor_for(project_root: &Path, payload_hash: &str, kernel_manifest_hash: &str) -> Anchor {
    match view() {
        View::Resolved(ms) => anchor_in(&ms, FRAMEWORK_NAME, project_root, payload_hash, kernel_manifest_hash),
        View::Undetermined(why) => Anchor::Undetermined {
            basis: format!("protected machine state could not be resolved ({why}); the protected installation record was not consulted"),
        },
    }
}

/// [`anchor_for`] against an explicit protected state.
pub fn anchor_in(
    ms: &MachineState,
    product: &str,
    project_root: &Path,
    payload_hash: &str,
    kernel_manifest_hash: &str,
) -> Anchor {
    anchor_posture(
        ms,
        ms.is_provisioned(),
        product,
        project_root,
        payload_hash,
        kernel_manifest_hash,
    )
}

/// [`anchor_in`] with the machine's posture given rather than read (the decision itself, testable without a latch).
pub fn anchor_posture(
    ms: &MachineState,
    provisioned: bool,
    product: &str,
    project_root: &Path,
    payload_hash: &str,
    kernel_manifest_hash: &str,
) -> Anchor {
    let record = load_project_record(ms, product, project_root);
    let mut unverified_install = false;
    if let Some(rec) = record.as_ref().filter(|r| r.records_anything()) {
        match rec.binding(payload_hash, kernel_manifest_hash) {
            Some(b) if !provisioned || records_a_verification(&b.authenticity) => {
                return Anchor::Matched {
                    basis: format!(
                        "matches this machine's protected installation record for this project ({} {} via {} at {})",
                        b.release_version, b.authenticity, b.ingress, b.at
                    ),
                };
            }
            Some(_) => unverified_install = true,
            None => {
                let recorded = rec
                    .current
                    .as_ref()
                    .or(rec.pending.as_ref())
                    .map(|b| b.payload_hash.clone())
                    .unwrap_or_default();
                return Anchor::Diverged {
                    basis: if provisioned {
                        format!(
                            "the installed payload {payload_hash} is not the payload {recorded} this machine committed into this project — a post-install rewrite, or a change made without an ingress on this machine; KERNEL_MANIFEST.json and framework.lock agreeing with it does not make it intact. Verify the release framework.lock pins: `gov kernel reinstall --source <signed release>`"
                        )
                    } else {
                        format!(
                            "the installed payload {payload_hash} is not the payload {recorded} this machine installed into this project. This machine holds no trust anchor, so its record is itself unauthenticated: the divergence is reported, not enforced (OD-P2-02 is with the owner)"
                        )
                    },
                    recorded_payload_hash: recorded,
                    enforced: provisioned,
                };
            }
        }
    }
    if provisioned {
        if let Some(v) = verified_release(ms, product, payload_hash, kernel_manifest_hash) {
            return Anchor::Matched {
                basis: format!(
                    "matches a release this machine verified ({} seq {}, {}) in its protected verified-release ledger",
                    v.release_version, v.sequence, v.authenticity
                ),
            };
        }
        return Anchor::Unrecorded {
            required: true,
            basis: if unverified_install {
                format!("this machine installed payload {payload_hash} here before it held a trust anchor and has never verified it; verify it against the pinned signed release before privileged work (`gov kernel reinstall --source <signed release>`)")
            } else {
                format!("this machine holds no protected record binding the installed payload {payload_hash} (installed elsewhere, or by another machine); verify it against the pinned signed release before privileged work (`gov kernel reinstall --source <signed release>`)")
            },
        };
    }
    Anchor::Unrecorded {
        required: false,
        basis: "this machine holds no trust anchor and no protected installation record for this project: the installed kernel is checked against KERNEL_MANIFEST.json and framework.lock only, and is not anchored to anything the repository cannot rewrite".into(),
    }
}

/// Where an installed kernel's files differ from what this machine committed into the project.
#[derive(Debug, Clone, Default)]
pub struct Divergence {
    pub modified: Vec<String>,
    pub missing: Vec<String>,
    pub added: Vec<String>,
    pub recorded_payload_hash: String,
    /// See [`Anchor::Diverged`]: enforced only on a machine with a trust anchor.
    pub enforced: bool,
}

/// Compare an installed kernel's measured files with this machine's per-project record. `None` when there is no
/// record (or protected state is undetermined), or when the files are exactly a payload the record binds.
pub fn divergence(kernel_dir: &Path, actual: &BTreeMap<String, String>) -> Option<Divergence> {
    match view() {
        View::Resolved(ms) => divergence_in(&ms, FRAMEWORK_NAME, kernel_dir, actual),
        View::Undetermined(_) => None,
    }
}

/// [`divergence`] against an explicit protected state.
pub fn divergence_in(
    ms: &MachineState,
    product: &str,
    kernel_dir: &Path,
    actual: &BTreeMap<String, String>,
) -> Option<Divergence> {
    divergence_posture(ms, ms.is_provisioned(), product, kernel_dir, actual)
}

/// [`divergence_in`] with the machine's posture given rather than read.
pub fn divergence_posture(
    ms: &MachineState,
    provisioned: bool,
    product: &str,
    kernel_dir: &Path,
    actual: &BTreeMap<String, String>,
) -> Option<Divergence> {
    let root = project_root_of_kernel_dir(kernel_dir)?;
    let rec = load_project_record(ms, product, &root)?;
    let measured = hash_value(&serde_json::to_value(actual).ok()?);
    let candidates: Vec<&BoundPayload> = rec.current.iter().chain(rec.pending.iter()).collect();
    if candidates.is_empty() || candidates.iter().any(|b| b.payload_hash == measured) {
        return None;
    }
    let reference = candidates[0];
    let expected = &reference.files;
    let mut d = Divergence {
        recorded_payload_hash: reference.payload_hash.clone(),
        enforced: provisioned,
        ..Default::default()
    };
    if expected.is_empty() {
        // a record without its per-file map still binds the aggregate digest
        d.modified.push("(aggregate payload digest)".into());
        return Some(d);
    }
    for (p, h) in expected {
        match actual.get(p) {
            Some(a) if a == h => {}
            Some(_) => d.modified.push(p.clone()),
            None => d.missing.push(p.clone()),
        }
    }
    for p in actual.keys() {
        if !expected.contains_key(p) {
            d.added.push(p.clone());
        }
    }
    Some(d)
}

// ---------------------------------------------------------------------------------------------- presentation

/// What this product may say about one installation's authenticity (`BC-P2-36`; Contract v3:150).
///
/// `authenticity_established` is true only when the machine holds a trust anchor, the installed kernel is intact,
/// and a protected record of a verification binds it. Anything else is disclosed and is never presented as
/// current, verified or certified.
pub fn posture_of(project_root: &Path) -> Value {
    let kt = crate::kernel_trust::trust(project_root);
    let root = canonical_project_root(project_root).display().to_string();
    if !kt.installed {
        return json!({"project_root": root, "installed": false, "authenticity_established": false});
    }
    let (machine_posture, record) = match view() {
        View::Resolved(ms) => (
            if ms.is_provisioned() {
                "PROVISIONED"
            } else {
                "UNPROVISIONED"
            },
            load_project_record(&ms, FRAMEWORK_NAME, project_root),
        ),
        View::Undetermined(_) => ("UNDETERMINED", None),
    };
    let anchor = anchor_for(project_root, &kt.measured_payload_hash, &kt.manifest_hash);
    let bound = record
        .as_ref()
        .and_then(|r| r.binding(&kt.measured_payload_hash, &kt.manifest_hash))
        .cloned();
    let established = machine_posture == "PROVISIONED"
        && kt.verified
        && matches!(anchor, Anchor::Matched { .. })
        && bound
            .as_ref()
            .map(|b| records_a_verification(&b.authenticity))
            .unwrap_or(true);
    let authenticity = if established {
        bound
            .as_ref()
            .map(|b| b.authenticity.clone())
            .unwrap_or_else(|| {
                Authenticity::PreviouslyVerifiedByThisMachine
                    .as_str()
                    .into()
            })
    } else if machine_posture == "UNPROVISIONED" {
        Authenticity::Unknown.as_str().into()
    } else {
        "NOT_ESTABLISHED".into()
    };
    let disclosure = if established {
        String::new()
    } else if machine_posture == "UNPROVISIONED" {
        "release authenticity of this installation is UNKNOWN: this machine holds no provisioned Signed Release Root trust anchor, so nothing installed on it can be authenticated. It is not current, not verified and not certified (Contract v3:150). Provision a trust anchor (`gov trust provision`) and reinstall from a signed release (`gov kernel reinstall --source <signed release>`).".to_string()
    } else if machine_posture == "UNDETERMINED" {
        "release authenticity of this installation cannot be determined: protected machine state could not be resolved. It is not presented as current.".to_string()
    } else {
        format!("release authenticity of this installation is NOT ESTABLISHED on this machine ({}). It is not current, not verified and not certified. {}", anchor.state(), anchor.basis())
    };
    json!({
        "project_root": root,
        "installed": true,
        "machine_posture": machine_posture,
        "authenticity": authenticity,
        "authenticity_established": established,
        "integrity": {"intact": kt.verified, "protected_record": anchor.state(), "basis": anchor.basis()},
        "bound_release": bound.as_ref().map(|b| b.summary()),
        "lock_version": kt.installed_version,
        "disclosure": disclosure,
    })
}

/// Every installation this process is presenting: the ones it evaluated (post-install integrity is consulted by
/// every governed command) and the one the working directory is in. Deduplicated by canonical root.
pub fn installations_in_context() -> Vec<Value> {
    let mut roots: BTreeMap<String, PathBuf> = BTreeMap::new();
    for r in crate::kernel_trust::evaluated_roots() {
        roots.insert(canonical_project_root(&r).display().to_string(), r);
    }
    if let Ok(cwd) = std::env::current_dir() {
        if let Some(r) = crate::project::find_root(&cwd) {
            roots.insert(canonical_project_root(&r).display().to_string(), r);
        }
    }
    roots
        .values()
        .filter(|r| {
            r.join("governance").join("framework.lock").exists()
                && r.join("governance")
                    .join("kernel")
                    .join(crate::kernel::KERNEL_MANIFEST)
                    .exists()
        })
        .map(|r| posture_of(r))
        .collect()
}

/// The disclosures the presentation block carries for the installations in context whose authenticity is not
/// established — one generic sentence per distinct posture, with no path, timestamp or machine identity in it, so the
/// block is reproducible across clones and machines in the same posture. Empty when every installation in context
/// is established (or there is none).
pub fn presentation_disclosures() -> Vec<String> {
    let mut out: Vec<String> = vec![];
    for p in installations_in_context() {
        if p["authenticity_established"].as_bool().unwrap_or(false) {
            continue;
        }
        let line = match p["machine_posture"].as_str().unwrap_or("") {
            "UNPROVISIONED" => "release authenticity UNKNOWN: this machine holds no provisioned Signed Release Root trust anchor, so no installation on it can be authenticated. It is not current, not verified and not certified (Contract v3:150). Provision a trust anchor (`gov trust provision --anchor <administrator root>`) and install a signed release (`gov kernel reinstall --source <signed release>`).".to_string(),
            "UNDETERMINED" => "release authenticity UNDETERMINED: protected machine state could not be resolved, so the installation is not presented as current. Resolve the protected state root and re-run.".to_string(),
            _ => format!(
                "release authenticity NOT ESTABLISHED on this machine (protected installation record: {}): no protected record of a verification binds the installed kernel. It is not current, not verified and not certified. `gov kernel trust` shows why; `gov kernel reinstall --source <the signed release framework.lock pins>` verifies it.",
                p["integrity"]["protected_record"].as_str().unwrap_or("")
            ),
        };
        if !out.contains(&line) {
            out.push(line);
        }
        if p["integrity"]["protected_record"] == "DIVERGED_NOT_ENFORCED" {
            let extra = "the installed kernel differs from the payload this machine installed into the project (a post-install rewrite, or a change that arrived without an ingress on this machine). On a machine with no trust anchor this is reported and not enforced (OD-P2-02 is with the owner); `gov kernel trust` shows the files.".to_string();
            if !out.contains(&extra) {
                out.push(extra);
            }
        }
    }
    out
}

/// **Integration point for `runtime/src/doctor.rs` (WS-2)** — a ready-made doctor check in doctor's own shape.
///
/// `add(crate::srr::installation::doctor_check(&p.root, "D0xx"));` — the id is doctor's to assign. The check fails
/// (severity `medium`, so the verdict cannot be HEALTHY) whenever the installation's authenticity is not
/// established, and its message is the disclosure. On a provisioned machine an unanchored kernel additionally fails
/// D029 (critical) through post-install integrity.
pub fn doctor_check(project_root: &Path, id: &str) -> Value {
    let p = posture_of(project_root);
    let ok = p["authenticity_established"].as_bool().unwrap_or(false);
    json!({
        "id": id,
        "name": "installation authenticity established (otherwise disclosed, never presented as current/verified/certified)",
        "ok": ok,
        "severity": if ok { "info" } else { "medium" },
        "message": if ok {
            format!("authenticity {} ({})", p["authenticity"].as_str().unwrap_or(""), p["integrity"]["basis"].as_str().unwrap_or(""))
        } else {
            p["disclosure"].as_str().unwrap_or("installation authenticity not established").to_string()
        },
        "remediation": if ok { Value::Null } else { json!("gov trust status; provision a trust anchor (gov trust provision --anchor <admin root>) and reinstall from a signed release (gov kernel reinstall --source <release>)") },
        "posture": p,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tmp(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("gov-ws08-{tag}-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    fn payload(files: &[(&str, &str)], authenticity: &str) -> BoundPayload {
        let map: BTreeMap<String, String> = files
            .iter()
            .map(|(p, h)| (p.to_string(), h.to_string()))
            .collect();
        BoundPayload {
            payload_hash: hash_value(&serde_json::to_value(&map).unwrap()),
            files: map,
            release_version: "4.1.5".into(),
            sequence: 10,
            authenticity: authenticity.into(),
            ingress: "init".into(),
            ..Default::default()
        }
    }

    /// A scratch protected state and project. The posture is passed to the decision functions directly
    /// (`anchor_posture`, `divergence_posture`), so no provisioning latch is ever written by a test.
    fn machine(tag: &str, provisioned: bool) -> (MachineState, PathBuf, bool) {
        let root = tmp(tag);
        let ms = MachineState::at(&root.join("state")).unwrap();
        let project = root.join("project");
        std::fs::create_dir_all(project.join("governance").join("kernel")).unwrap();
        (ms, project, provisioned)
    }

    const P: &str = crate::FRAMEWORK_NAME;

    /// BC-P2-35: a mutually consistent rewrite (payload + manifest + lock agree) is still not what this machine
    /// committed into the project, and the divergence names the file.
    #[test]
    fn a_consistent_rewrite_diverges_from_the_protected_record_and_names_the_file() {
        let (ms, project, prov) = machine("rewrite", true);
        let installed = payload(
            &[
                ("policies/SECURITY_POLICY.yaml", "aa"),
                ("KERNEL.yaml", "bb"),
            ],
            "AUTHENTIC",
        );
        bind_committed_in(&ms, P, &project, installed.clone()).unwrap();
        let mut rewritten = installed.files.clone();
        rewritten.insert("policies/SECURITY_POLICY.yaml".into(), "cc".into());
        let kd = project.join("governance").join("kernel");
        let d =
            divergence_posture(&ms, prov, P, &kd, &rewritten).expect("the rewrite must diverge");
        assert_eq!(
            d.modified,
            vec!["policies/SECURITY_POLICY.yaml".to_string()]
        );
        assert_eq!(d.recorded_payload_hash, installed.payload_hash);
        assert!(d.enforced);
        let measured = hash_value(&serde_json::to_value(&rewritten).unwrap());
        let a = anchor_posture(&ms, prov, P, &project, &measured, "");
        assert_eq!(a.state(), "DIVERGED");
        assert!(!a.holds());
        // the committed bytes themselves are intact
        assert!(divergence_posture(&ms, prov, P, &kd, &installed.files).is_none());
        assert!(matches!(
            anchor_posture(&ms, prov, P, &project, &installed.payload_hash, ""),
            Anchor::Matched { .. }
        ));
    }

    /// An interrupted install may recover to either tree; both are bound, and nothing else is.
    #[test]
    fn pending_and_current_are_both_bound_until_the_commit_completes() {
        let (ms, project, prov) = machine("pending", true);
        let old = payload(&[("a", "1")], "AUTHENTIC");
        let new = payload(&[("a", "2")], "AUTHENTIC");
        bind_committed_in(&ms, P, &project, old.clone()).unwrap();
        bind_pending_in(&ms, P, &project, new.clone()).unwrap();
        for b in [&old, &new] {
            assert!(anchor_posture(&ms, prov, P, &project, &b.payload_hash, "").holds());
        }
        let other = payload(&[("a", "3")], "AUTHENTIC");
        assert!(!anchor_posture(&ms, prov, P, &project, &other.payload_hash, "").holds());
    }

    /// OD-P2-02 is with the owner: with no trust anchor the record is unauthenticated, so a divergence from it is
    /// reported and not enforced.
    #[test]
    fn an_unprovisioned_divergence_is_reported_not_enforced() {
        let (ms, project, prov) = machine("rewrite-unprov", false);
        let installed = payload(&[("a", "1")], "UNKNOWN");
        bind_committed_in(&ms, P, &project, installed.clone()).unwrap();
        let other = payload(&[("a", "2")], "UNKNOWN");
        let a = anchor_posture(&ms, prov, P, &project, &other.payload_hash, "");
        assert_eq!(a.state(), "DIVERGED_NOT_ENFORCED");
        assert!(a.holds());
        let kd = project.join("governance").join("kernel");
        let d = divergence_posture(&ms, prov, P, &kd, &other.files).unwrap();
        assert!(!d.enforced);
    }

    /// ARCH-0003 §8 / BC-P2-35: on a machine with a trust anchor, an installation no protected record of a
    /// verification binds is not anchored — including one installed here before the machine was provisioned.
    #[test]
    fn a_provisioned_machine_requires_a_verification_record() {
        let (ms, project, prov) = machine("prov", true);
        let unknown = payload(&[("a", "1")], "UNKNOWN");
        match anchor_posture(&ms, prov, P, &project, &unknown.payload_hash, "") {
            Anchor::Unrecorded { required: true, .. } => {}
            a => panic!("expected UNRECORDED_REQUIRED, got {a:?}"),
        }
        bind_committed_in(&ms, P, &project, unknown.clone()).unwrap();
        assert_eq!(
            anchor_posture(&ms, prov, P, &project, &unknown.payload_hash, "").state(),
            "UNRECORDED_REQUIRED",
            "an install made before provisioning is not a verification"
        );
        // an UNKNOWN entry never enters the ledger
        record_verified_in(&ms, P, unknown.clone()).unwrap();
        assert!(verified_release(&ms, P, &unknown.payload_hash, "").is_none());
        // a release this machine authenticated anchors it, by digest
        let mut authentic = unknown.clone();
        authentic.authenticity = "AUTHENTIC".into();
        record_verified_in(&ms, P, authentic.clone()).unwrap();
        assert!(matches!(
            anchor_posture(&ms, prov, P, &project, &unknown.payload_hash, ""),
            Anchor::Matched { .. }
        ));
    }

    /// OD-P2-02 is with the owner: with no trust anchor and no record, nothing is required (and nothing is claimed).
    #[test]
    fn an_unprovisioned_machine_without_a_record_is_not_blocked() {
        let (ms, project, prov) = machine("unprov", false);
        let a = anchor_posture(&ms, prov, P, &project, "ff", "");
        assert_eq!(a.state(), "UNRECORDED");
        assert!(a.holds());
    }

    /// BC-P2-38: the ledger keeps the highest sequence the release role bound to the same bytes.
    #[test]
    fn the_ledger_keeps_the_highest_signed_sequence_for_the_same_bytes() {
        let (ms, _, _prov) = machine("ledger", true);
        let mut hi = payload(&[("a", "1")], "AUTHENTIC");
        hi.sequence = 100;
        let mut lo = hi.clone();
        lo.sequence = 60;
        record_verified_in(&ms, P, hi.clone()).unwrap();
        record_verified_in(&ms, P, lo).unwrap();
        assert_eq!(
            verified_release(&ms, P, &hi.payload_hash, "")
                .unwrap()
                .sequence,
            100
        );
    }

    /// BC-P2-38: the single installed record vouches only for a verification.
    #[test]
    fn an_unknown_installed_record_vouches_for_nothing() {
        let rec = crate::srr::state::InstalledRecord {
            payload_hash: "ab".into(),
            authenticity: "UNKNOWN".into(),
            ..Default::default()
        };
        assert!(!rec.vouches_for("ab", ""));
        let rec = crate::srr::state::InstalledRecord {
            authenticity: "AUTHENTIC".into(),
            ..rec
        };
        assert!(rec.vouches_for("ab", ""));
    }
}
