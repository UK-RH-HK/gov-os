//! Signed Release Root v1 — **the one verification policy**.
//!
//! ARCH-0003 §3.6 and §6: "One verifier evaluates the same policy for init, adopt, update, reinstall, rollback and
//! recovery" and "Every privileged lifecycle adapter must call one verification policy and receive a typed
//! authenticated-release value, never a raw source directory."
//!
//! [`admit`] is that verifier. It is the only constructor of [`AuthenticatedRelease`], and
//! [`crate::kernel::install_kernel`] takes an `&AuthenticatedRelease` rather than a path — so an ingress cannot
//! install from a source directory even by mistake. The compiler, not a convention, enforces "no bypass".
//!
//! The policy, in order:
//!
//! | step | what | fails closed with |
//! |---|---|---|
//! | 0 | environment may not carry authority | `SRR_ENV_CANNOT_CREATE_AUTHORITY` |
//! | 1 | replay any interrupted install transaction | — |
//! | 2 | copy the candidate into private staging and measure the staged bytes | `SRR_STAGING_*` |
//! | 3 | if provisioned: timestamp → snapshot → release chain against the trusted root | `SRR_THRESHOLD_NOT_MET`, `SRR_METADATA_*` |
//! | 4 | identity binding: product, repository, channel, platform | `SRR_WRONG_PRODUCT`, `SRR_WRONG_CHANNEL`, … |
//! | 5 | verified-byte binding: signed digests vs the measured staged bytes | `SRR_PAYLOAD_DIGEST_MISMATCH` |
//! | 6 | migration identity binding | `SRR_MIGRATION_NOT_AUTHORISED` |
//! | 7 | replay/rollback: metadata versions against the protected high-water | `SRR_METADATA_ROLLBACK` |
//! | 8 | expiry against the declared local clock | `SRR_METADATA_EXPIRED` |
//! | 9 | **the floor check — at every ingress, not only rollback** | `SRR_BELOW_FLOOR` |
//! | 10 | below floor: owner-signed break-glass or refusal | `SRR_BREAK_GLASS_NOT_AUTHORISED` |
//!
//! ## What a candidate can never do
//!
//! Nothing read from the candidate establishes its own authority. `KERNEL.yaml`, `KERNEL_MANIFEST.json`,
//! `framework.lock`, the Git repository, environment variables, caller fields, plugin descriptors and model output
//! are all *measured or ignored*, never believed: the identity comes from signed metadata verified against a root
//! anchor held in protected machine state, and the bytes come from the private staging copy.
//!
//! ## `SRR-R0-L3` — repository gate records
//!
//! "Repository gate records remain requests" is scoped to **trust-changing** operations (see
//! [`is_trust_changing`]). For ordinary governed work, D-0007 T2 and Contract v3 L2 are untouched: an answered
//! Human Gate record in the repository remains authoritative exactly as before.
use crate::srr::breakglass;
use crate::srr::metadata::{
    self, local_clock_now, Envelope, Release, Root, Snapshot, Timestamp, RELEASE_JSON,
    ROLE_RELEASE, ROLE_ROOT, ROLE_SNAPSHOT, ROLE_TIMESTAMP, SNAPSHOT_JSON, TIMESTAMP_JSON,
};
use crate::srr::staging::{self, Staged};
use crate::srr::state::{refuse_authority_env, Floors, InstalledRecord, MachineState};
use crate::util::now_iso;
use crate::{GovError, Result, FRAMEWORK_NAME};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

// ---------------------------------------------------------------------------------------------- ingress set

/// The privileged lifecycle ingresses of 00-ARCHITECTURE "Lifecycle ingress invariant". Every one of them calls
/// [`admit`]; the enum exists so the floor rule is scoped over the ingress **set** rather than named after one
/// operation (ARCH-0003 §7: "`rollback` is the name of one governed ingress, not the name of the rule").
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Ingress {
    Init,
    Adopt,
    Update,
    Reinstall,
    Rollback,
    Recovery,
}

impl Ingress {
    pub fn as_str(&self) -> &'static str {
        match self {
            Ingress::Init => "init",
            Ingress::Adopt => "adopt",
            Ingress::Update => "update",
            Ingress::Reinstall => "reinstall",
            Ingress::Rollback => "rollback",
            Ingress::Recovery => "recovery",
        }
    }
    /// Can this ingress move the machine *backwards* onto an older release? The floor rule binds every ingress, but
    /// these are the ones where a downgrade is the expected shape of the request.
    pub fn is_backward_capable(&self) -> bool {
        matches!(
            self,
            Ingress::Rollback
                | Ingress::Recovery
                | Ingress::Reinstall
                | Ingress::Init
                | Ingress::Adopt
                | Ingress::Update
        )
    }
    /// Recovery is the only ingress that may consult this machine's own protected installed record when no current
    /// metadata is reachable (ARCH-0003 §7).
    pub fn may_use_protected_installed_record(&self) -> bool {
        matches!(
            self,
            Ingress::Recovery | Ingress::Rollback | Ingress::Reinstall
        )
    }
}

/// `SRR-R0-L3` — the operations for which a repository record is only a *request*.
///
/// Outside this set, repository gate records keep the authority D-0007 T2 and Contract v3 L2 give them.
pub fn is_trust_changing(operation: &str) -> bool {
    const TRUST_CHANGING: &[&str] = &[
        "trust provision",
        "trust root-update",
        "trust revoke",
        "break-glass",
        "floor",
        "release certify",
        "plugin acquire",
        "plugin install",
    ];
    TRUST_CHANGING.iter().any(|t| operation.contains(t))
}

// ---------------------------------------------------------------------------------------------- posture / verdicts

/// Whether this machine holds an administrator-provisioned trust anchor.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Posture {
    /// A trusted root anchor exists. Full signed verification is required and unsigned input is refused.
    Provisioned,
    /// No anchor has ever been provisioned here. Release authenticity is **unknown** and is reported as unknown;
    /// it is never reported as authentic. See [`Authenticity::Unknown`].
    Unprovisioned,
}

/// What the verifier can honestly say about where the bytes came from.
///
/// These are three distinct predicates and they are kept distinct on purpose (frozen R0 item 11, and the R0
/// rejection that turned on conflating them):
/// * **authentic** — signed release metadata chains to the trusted root. This type.
/// * **intact** — the installed copy matches its own manifest and lock. That is D-0007, in
///   [`crate::kernel_trust`], and it is *not* consulted here.
/// * **admissible** — at or above the floors. That is [`AuthenticatedRelease::below_floor`].
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Authenticity {
    /// Verified against signed release metadata chaining to the machine's trusted root.
    Authentic,
    /// Verified against **this machine's own protected record** of a release it previously verified and installed,
    /// because no current metadata was reachable (ARCH-0003 §7). Never derived from the manifest, the lock, the
    /// repository or files delivered with the copy.
    PreviouslyVerifiedByThisMachine,
    /// No trust anchor exists on this machine, so authenticity is **not known**. This is an honest "unknown", not
    /// a permission: it asserts nothing and grants nothing, and every operation that needs authenticity refuses.
    Unknown,
}

impl Authenticity {
    pub fn as_str(&self) -> &'static str {
        match self {
            Authenticity::Authentic => "AUTHENTIC",
            Authenticity::PreviouslyVerifiedByThisMachine => "PREVIOUSLY_VERIFIED_BY_THIS_MACHINE",
            Authenticity::Unknown => "UNKNOWN",
        }
    }
    pub fn is_authenticated(&self) -> bool {
        matches!(
            self,
            Authenticity::Authentic | Authenticity::PreviouslyVerifiedByThisMachine
        )
    }
}

/// Honest currency reporting (frozen R0 item 10, 00-ARCHITECTURE "Freshness and revocation").
///
/// The client never claims knowledge of revocations it has not received, and never claims knowledge of revocations
/// that do not yet exist. `Unknown` and `Stale` are reported as such.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Currency {
    /// Fresh timestamp metadata was verified against the declared local clock.
    Current,
    /// Metadata was verified but is past its expiry against the declared local clock.
    Stale,
    /// No metadata was reachable, or no anchor exists. Nothing is known about current revocations.
    Unknown,
}

impl Currency {
    pub fn as_str(&self) -> &'static str {
        match self {
            Currency::Current => "CURRENT",
            Currency::Stale => "STALE",
            Currency::Unknown => "UNKNOWN",
        }
    }
}

/// The typed authenticated-release value. Only [`admit`] constructs it, and only it names bytes an installer may
/// read (`verified_payload`).
#[derive(Debug, Clone)]
pub struct AuthenticatedRelease {
    pub ingress: Ingress,
    pub product: String,
    pub release_version: String,
    pub sequence: u64,
    pub channel: String,
    pub repository: String,
    pub authenticity: Authenticity,
    pub currency: Currency,
    pub posture: Posture,
    pub payload_hash: String,
    pub kernel_manifest_hash: String,
    pub below_floor: bool,
    pub break_glass: Option<Value>,
    pub floors: Floors,
    pub staged: Staged,
    pub machine: MachineState,
    pub release_metadata_sha256: String,
    pub migrations: Vec<String>,
    pub delegations: Vec<metadata::Delegation>,
    pub notes: Vec<String>,
}

impl AuthenticatedRelease {
    /// The **only** bytes an installer may read. They are the bytes that were measured and verified.
    pub fn verified_payload(&self) -> &Path {
        &self.staged.payload_dir
    }
    pub fn to_value(&self) -> Value {
        json!({
            "ingress": self.ingress.as_str(), "product": self.product, "release_version": self.release_version,
            "sequence": self.sequence, "channel": self.channel, "repository": self.repository,
            "authenticity": self.authenticity.as_str(), "currency": self.currency.as_str(),
            "posture": match self.posture { Posture::Provisioned => "PROVISIONED", Posture::Unprovisioned => "UNPROVISIONED" },
            "payload_hash": self.payload_hash, "kernel_manifest_hash": self.kernel_manifest_hash,
            "below_floor": self.below_floor, "break_glass": self.break_glass,
            "machine_id": self.machine.machine_id, "release_metadata_sha256": self.release_metadata_sha256,
            "migrations_authorised": self.migrations, "notes": self.notes,
            "floors": self.floors.to_value(),
        })
    }
}

// ---------------------------------------------------------------------------------------------- request

pub struct AdmissionRequest<'a> {
    pub ingress: Ingress,
    /// Candidate kernel source. Unverified input.
    pub candidate: &'a Path,
    /// Explicit metadata directory. When absent, [`locate_metadata`] looks beside the candidate.
    pub metadata_dir: Option<PathBuf>,
    /// The channel the caller asks for. A *request*, matched against the bound `channel` field (`SRR-R0-L2`); it
    /// cannot create authority for a channel the metadata does not name.
    pub channel: Option<String>,
    /// The caller requests below-floor admission. This is a request only: the authority comes from an owner-signed
    /// token in protected machine state (`OWNER-DECISION-0006` §2).
    pub request_break_glass: bool,
    /// Human-readable reason recorded alongside the ingress.
    pub reason: Option<String>,
}

impl<'a> AdmissionRequest<'a> {
    pub fn new(ingress: Ingress, candidate: &'a Path) -> Self {
        AdmissionRequest {
            ingress,
            candidate,
            metadata_dir: None,
            channel: None,
            request_break_glass: false,
            reason: None,
        }
    }
    pub fn with_break_glass(mut self, yes: bool) -> Self {
        self.request_break_glass = yes;
        self
    }
    pub fn with_channel(mut self, c: Option<String>) -> Self {
        self.channel = c;
        self
    }
    pub fn with_reason(mut self, r: Option<String>) -> Self {
        self.reason = r;
        self
    }
    pub fn with_metadata_dir(mut self, d: Option<PathBuf>) -> Self {
        self.metadata_dir = d;
        self
    }
}

/// Signed metadata lives beside the payload it authorises: `<release>/metadata/*.json` for a built release, or
/// `<kernel>/.srr/*.json` for a payload carrying its own metadata.
pub fn locate_metadata(candidate: &Path) -> Option<PathBuf> {
    let mut cands = vec![candidate.join(".srr")];
    if let Some(p) = candidate.parent() {
        cands.push(p.join("metadata"));
        cands.push(p.join(".srr"));
    }
    cands.into_iter().find(|d| d.join(RELEASE_JSON).exists())
}

// ---------------------------------------------------------------------------------------------- the verifier

/// Load the machine's trusted root anchor, if one is provisioned.
pub fn trusted_root(ms: &MachineState, now: &str) -> Result<Option<Root>> {
    if !ms.is_provisioned() {
        return Ok(None);
    }
    let p = ms.root_metadata_path();
    if !p.exists() {
        return Err(GovError::new(
            "SRR_TRUST_ANCHOR_MISSING",
            format!("this machine is provisioned but its trusted root metadata is missing from {}. Re-provision it from the administrator's copy; it is never taken from a repository.", p.display()),
        ));
    }
    let env = Envelope::read(&p)?;
    let root = Root::parse(env)?;
    // The anchor is re-checked against itself on every load: a tampered protected file is refused rather than used.
    root.verify_role(ROLE_ROOT, &root.envelope)?;
    if root.envelope.is_expired(now) {
        // An expired root does not brick an installed system, but it cannot authorise a trust change.
        return Ok(Some(root));
    }
    Ok(Some(root))
}

/// **The single verification policy every privileged ingress calls.**
pub fn admit(req: AdmissionRequest) -> Result<AuthenticatedRelease> {
    // (0) the environment may not carry authority
    refuse_authority_env()?;
    let ms = MachineState::open()?;
    let now = local_clock_now();
    let product = FRAMEWORK_NAME.to_string();
    let mut notes: Vec<String> = vec![];

    // (1) replay any interrupted install transaction before starting a new one
    let replayed = staging::recover(&ms)?;
    for r in &replayed {
        notes.push(format!(
            "replayed interrupted install transaction ({}): {}",
            r["phase"].as_str().unwrap_or(""),
            r["action"].as_str().unwrap_or("")
        ));
    }

    // (2) private staging + measurement of the staged bytes
    let staged = staging::stage(&ms, req.candidate)?;
    let mut floors = Floors::load(&ms, &product);

    let outcome = admit_inner(&ms, &now, &product, &req, &staged, &mut floors, &mut notes);
    match outcome {
        Ok(a) => Ok(a),
        Err(e) => {
            staging::abandon(&ms, &staged, &format!("{}: {}", e.code, e.message));
            Err(e)
        }
    }
}

#[allow(clippy::too_many_arguments)]
fn admit_inner(
    ms: &MachineState,
    now: &str,
    product: &str,
    req: &AdmissionRequest,
    staged: &Staged,
    floors: &mut Floors,
    notes: &mut Vec<String>,
) -> Result<AuthenticatedRelease> {
    let root = trusted_root(ms, now)?;
    let posture = if root.is_some() {
        Posture::Provisioned
    } else {
        Posture::Unprovisioned
    };
    let metadata_dir = req
        .metadata_dir
        .clone()
        .or_else(|| locate_metadata(req.candidate));

    let mut authenticity = Authenticity::Unknown;
    let mut currency = Currency::Unknown;
    let mut release: Option<Release> = None;
    let mut release_metadata_sha256 = String::new();
    // Identity for the offline-recovery case: taken from this machine's own protected record, never from the
    // payload, its manifest, its lock or the repository (ARCH-0003 §7).
    let mut offline_identity: Option<(String, u64, String)> = None;

    if let Some(root) = root.as_ref() {
        match metadata_dir.as_ref() {
            Some(dir) => {
                let (rel, cur) = verify_metadata_chain(root, dir, now, floors, notes)?;
                release_metadata_sha256 = rel.envelope.file_sha256.clone();
                currency = cur;
                release = Some(rel);
                authenticity = Authenticity::Authentic;
            }
            None => {
                // No current metadata is reachable. ARCH-0003 §7: at the ingresses that may consult it, the
                // authenticity of an installed local recovery path derives from THIS MACHINE'S OWN protected
                // record of what it previously verified and installed — never from the manifest, the lock, the
                // repository or mutually consistent files delivered with the copy.
                if !req.ingress.may_use_protected_installed_record() {
                    return Err(GovError::new(
                        "SRR_RELEASE_UNVERIFIED",
                        format!("no signed release metadata was found for this candidate and ingress `{}` may not fall back to the machine's protected installed record. This machine holds a trust anchor, so unsigned releases are refused.", req.ingress.as_str()),
                    ).with_details(json!({"candidate": req.candidate.display().to_string(), "searched": [".srr/", "../metadata/"]})));
                }
                let rec = InstalledRecord::load(ms, product).ok_or_else(|| {
                    GovError::new(
                        "SRR_RELEASE_UNVERIFIED",
                        "no signed release metadata was found and this machine holds no protected record of a release it previously verified and installed; there is no non-circular basis for admitting these bytes (OWNER-DIRECTIVE-0004: the manifest and lock are not a first-install authenticity root)",
                    )
                })?;
                // SRR2-R1-C2: matched on payload digests, not on the release version.
                if !rec.vouches_for(&staged.payload_hash, &staged.kernel_manifest_hash) {
                    return Err(GovError::new(
                        "SRR_RELEASE_UNVERIFIED",
                        "the candidate payload does not match the digests this machine previously verified and installed; its authenticity cannot be established offline (SRR2-R1-C2)",
                    ).with_details(json!({
                        "measured": {"payload_hash": staged.payload_hash, "kernel_manifest_hash": staged.kernel_manifest_hash},
                        "previously_verified": {"payload_hash": rec.payload_hash, "kernel_manifest_hash": rec.kernel_manifest_hash, "release_version": rec.release_version},
                    })));
                }
                authenticity = Authenticity::PreviouslyVerifiedByThisMachine;
                currency = Currency::Unknown;
                offline_identity = Some((
                    rec.release_version.clone(),
                    rec.sequence,
                    rec.channel.clone(),
                ));
                notes.push(
                    "no current metadata was reachable; authenticity comes from this machine's own protected record of the release it previously verified and installed. Currency is UNKNOWN: this client makes no claim about revocations it has not received."
                        .into(),
                );
            }
        }
    } else {
        // Unprovisioned: no anchor exists, so nothing here can establish authenticity, and nothing pretends to.
        notes.push(
            "this machine holds no provisioned Signed Release Root trust anchor, so release authenticity is UNKNOWN and no authenticity claim is made. Provision one with `gov trust provision`. Verified-byte binding, atomic commit, the protected high-water and the D-0007 installed-integrity control all remain in force."
                .into(),
        );
        if metadata_dir.is_some() {
            notes.push("signed metadata accompanies this candidate but cannot be verified: no trust anchor is provisioned on this machine.".into());
        }
    }

    // (4)(5)(6) identity, verified-byte and migration binding
    let (
        release_version,
        sequence,
        channel,
        repository,
        migrations,
        delegations,
        min_secure,
        min_secure_seq,
    ) = match release.as_ref() {
        Some(rel) => {
            if rel.product != product {
                return Err(GovError::new(
                    "SRR_WRONG_PRODUCT",
                    format!(
                        "release metadata binds product '{}', this client is '{product}'",
                        rel.product
                    ),
                ));
            }
            if let Some(want) = req.channel.as_ref() {
                // SRR-R0-L2: the channel is a bound metadata field, so a wrong-channel release fails closed.
                if &rel.channel != want {
                    return Err(GovError::new(
                            "SRR_WRONG_CHANNEL",
                            format!("release metadata binds channel '{}', the requested channel is '{want}'", rel.channel),
                        ));
                }
            }
            if !rel.platforms.is_empty()
                && !rel
                    .platforms
                    .iter()
                    .any(|p| p == "any" || p == &current_platform())
            {
                return Err(GovError::new(
                    "SRR_UNSUPPORTED_PLATFORM",
                    format!(
                        "release {} supports {:?}, this machine is {}",
                        rel.release_version,
                        rel.platforms,
                        current_platform()
                    ),
                ));
            }
            // Verified-byte binding: the signed digests are compared against the measurement of the STAGED
            // bytes. Per-file checks run first so a refusal names the offending file rather than only the
            // aggregate; the aggregate then catches anything a per-file comparison could not.
            for (path, pf) in &rel.files {
                match staged.files.get(path) {
                        Some(actual) if actual == &pf.sha256 => {}
                        Some(actual) => {
                            return Err(GovError::new(
                                "SRR_PAYLOAD_DIGEST_MISMATCH",
                                format!("staged payload file '{path}' has digest {actual}, the signed metadata binds {}", pf.sha256),
                            ))
                        }
                        None => {
                            return Err(GovError::new(
                                "SRR_PAYLOAD_FILE_MISSING",
                                format!("the signed release metadata binds payload file '{path}', which is absent from the staged payload"),
                            ))
                        }
                    }
            }
            for path in staged.files.keys() {
                if !rel.files.contains_key(path) {
                    return Err(GovError::new(
                            "SRR_PAYLOAD_FILE_UNAUTHORISED",
                            format!("the staged payload contains '{path}', which the signed release metadata does not authorise"),
                        ));
                }
            }
            if rel.payload_hash != staged.payload_hash {
                return Err(GovError::new(
                        "SRR_PAYLOAD_DIGEST_MISMATCH",
                        format!("the staged payload digest {} does not match the digest bound by the signed release metadata {}", staged.payload_hash, rel.payload_hash),
                    ));
            }
            if rel.kernel_manifest_hash != staged.kernel_manifest_hash {
                return Err(GovError::new(
                        "SRR_PAYLOAD_DIGEST_MISMATCH",
                        format!("the staged kernel manifest digest {} does not match the digest bound by the signed release metadata {}", staged.kernel_manifest_hash, rel.kernel_manifest_hash),
                    ));
            }
            // Migration identity binding: migrations shipped in the payload must be the ones the metadata names.
            verify_migrations(rel, &staged.payload_dir)?;
            if rel.release_version != staged.version {
                return Err(GovError::new(
                    "SRR_RELEASE_VERSION_MISMATCH",
                    format!(
                        "signed release metadata names version {}, the staged payload declares {}",
                        rel.release_version, staged.version
                    ),
                ));
            }
            (
                rel.release_version.clone(),
                rel.sequence,
                rel.channel.clone(),
                rel.repository.clone(),
                rel.migrations
                    .iter()
                    .map(|m| m.id.clone())
                    .collect::<Vec<_>>(),
                rel.delegations.clone(),
                rel.minimum_secure_release.clone(),
                rel.minimum_secure_sequence,
            )
        }
        None => match offline_identity.clone() {
            // Offline recovery: the identity comes from the protected installed record that vouched for these
            // exact payload digests, so the floor check below runs on real, machine-verified values.
            Some((v, seq, ch)) => (v, seq, ch, String::new(), vec![], vec![], String::new(), 0),
            // No signed metadata and no protected record. The identity is what the payload declares, treated
            // as a claim and never as authority: `authenticity` stays UNKNOWN and no protected floor is
            // advanced from it.
            None => (
                staged.version.clone(),
                0,
                req.channel.clone().unwrap_or_else(|| "unspecified".into()),
                String::new(),
                vec![],
                vec![],
                String::new(),
                0,
            ),
        },
    };

    // The signed minimum secure release is monotonic and is raised before the floor check, so a newly learned
    // higher minimum applies to the operation that learned it.
    if !min_secure.is_empty() && authenticity == Authenticity::Authentic {
        floors.raise_minimum_secure(&min_secure, min_secure_seq, &release_metadata_sha256);
        floors.save(ms)?;
    }

    // (9) THE FLOOR CHECK — at every ingress in the set, not only at `rollback` (ARCH-0003 §7,
    //     OWNER-DECISION-0006 §9). The check is scoped over the ingress set; the ingress name does not change it.
    //
    // The floors enforced here are exactly the ones established from **verified** facts: a signed minimum secure
    // release, and the high-water of releases this machine verified and installed. A machine with no trust anchor
    // has established no such fact, so it has no floor to enforce — and it could not clear one either, since
    // break-glass authority is anchored in the trusted root's `recovery` role. `gov trust status` and `gov doctor`
    // report that plainly rather than implying a floor is protecting the machine when none is.
    let floor_seq = floors.effective_floor_sequence();
    let floor_ver = floors.effective_floor_version();
    let floors_established = floor_seq > 0 || !floor_ver.is_empty();
    let seq_below = floors_established && floor_seq > 0 && sequence < floor_seq;
    let ver_below = floors_established
        && !floor_ver.is_empty()
        && !release_version.is_empty()
        && crate::lock::compare_versions(&release_version, &floor_ver) == std::cmp::Ordering::Less;
    let below_floor = seq_below || ver_below;
    if !floors_established {
        notes.push(format!(
            "no protected release floor is in force for `{}` on this machine: none has been established from a verified release yet. Provision a trust anchor and install a signed release to establish one.",
            req.ingress.as_str()
        ));
    }

    let mut break_glass: Option<Value> = None;
    if below_floor {
        let detail = json!({
            "ingress": req.ingress.as_str(),
            "candidate_release": {"version": release_version, "sequence": sequence},
            "signed_minimum_secure_release": floors.minimum_secure_release,
            "signed_minimum_secure_sequence": floors.minimum_secure_sequence,
            "protected_release_high_water": floors.release_high_water_version,
            "protected_release_high_water_sequence": floors.release_high_water_sequence,
            "effective_floor_version": floor_ver, "effective_floor_sequence": floor_seq,
            "machine_id": ms.machine_id,
        });
        if !req.request_break_glass {
            return Err(GovError::new(
                "SRR_BELOW_FLOOR",
                format!(
                    "ingress `{}` would place this machine on release {release_version}, below its floor ({floor_ver}). The floors are a property of the machine and bind every privileged lifecycle ingress. Below-floor recovery is refused by default and is admissible only as an explicit owner-authorised emergency recovery mode (OWNER-DECISION-0006).",
                    req.ingress.as_str()
                ),
            )
            .with_details(detail));
        }
        // OWNER-DECISION-0006 §1: break-glass relaxes the floor check ONLY. Authenticity is still required.
        if !authenticity.is_authenticated() {
            return Err(GovError::new(
                "SRR_BREAK_GLASS_REQUIRES_AUTHENTIC_RELEASE",
                "below-floor break-glass recovery admits only an authentic Governance OS release (OWNER-DECISION-0006 §1). It never relaxes the authenticity check and never admits arbitrary or unsigned code.",
            )
            .with_details(detail));
        }
        let root = root.as_ref().ok_or_else(|| {
            GovError::new(
                "SRR_BREAK_GLASS_NO_AUTHORITY",
                "below-floor break-glass recovery requires a trusted root that delegates the owner's `recovery` role; this machine holds no trust anchor",
            )
        })?;
        let authorisation = breakglass::authorise(ms, root, product, now)?;
        let record = breakglass::enter(
            ms,
            &authorisation,
            floors,
            &release_version,
            sequence,
            &staged.payload_hash,
            &staged.kernel_manifest_hash,
            req.ingress.as_str(),
        )?;
        notes.push(format!(
            "entered below-floor break-glass recovery; this machine is marked `{}`",
            breakglass::DEGRADED_TOKEN
        ));
        break_glass = Some(record);
    }

    Ok(AuthenticatedRelease {
        ingress: req.ingress,
        product: product.to_string(),
        release_version,
        sequence,
        channel,
        repository,
        authenticity,
        currency,
        posture,
        payload_hash: staged.payload_hash.clone(),
        kernel_manifest_hash: staged.kernel_manifest_hash.clone(),
        below_floor,
        break_glass,
        floors: floors.clone(),
        staged: staged.clone(),
        machine: ms.clone(),
        release_metadata_sha256,
        migrations,
        delegations,
        notes: notes.clone(),
    })
}

/// timestamp → snapshot → release, each verified against the trusted root, with monotonic version enforcement.
fn verify_metadata_chain(
    root: &Root,
    dir: &Path,
    now: &str,
    floors: &mut Floors,
    notes: &mut Vec<String>,
) -> Result<(Release, Currency)> {
    let mut currency = Currency::Current;

    // timestamp: short-lived freshness for trust-changing operations
    let ts_path = dir.join(TIMESTAMP_JSON);
    let timestamp = if ts_path.exists() {
        let env = Envelope::read(&ts_path)?;
        root.verify_role(ROLE_TIMESTAMP, &env)?;
        let ts = Timestamp::parse(env)?;
        if ts.version < floors.metadata_floor(ROLE_TIMESTAMP) {
            return Err(rollback_err(
                ROLE_TIMESTAMP,
                ts.version,
                floors.metadata_floor(ROLE_TIMESTAMP),
            ));
        }
        if ts.envelope.is_expired(now) {
            currency = Currency::Stale;
            notes.push(format!("timestamp metadata expired at {} against the declared local clock {now}; currency is STALE", ts.envelope.expires()));
        }
        Some(ts)
    } else {
        currency = Currency::Unknown;
        notes.push("no timestamp metadata accompanies this candidate; currency is UNKNOWN and this client claims no knowledge of revocations it has not received".into());
        None
    };

    // snapshot: binds one consistent metadata set
    let snap_path = dir.join(SNAPSHOT_JSON);
    let snapshot = if snap_path.exists() {
        let env = Envelope::read(&snap_path)?;
        root.verify_role(ROLE_SNAPSHOT, &env)?;
        let snap = Snapshot::parse(env)?;
        if snap.version < floors.metadata_floor(ROLE_SNAPSHOT) {
            return Err(rollback_err(
                ROLE_SNAPSHOT,
                snap.version,
                floors.metadata_floor(ROLE_SNAPSHOT),
            ));
        }
        if let Some(ts) = timestamp.as_ref() {
            let bound = ts.meta.get(SNAPSHOT_JSON).ok_or_else(|| {
                GovError::new(
                    "SRR_SNAPSHOT_NOT_BOUND",
                    "timestamp metadata does not bind snapshot.json",
                )
            })?;
            if bound.sha256 != snap.envelope.file_sha256 || bound.version != snap.version {
                return Err(GovError::new(
                    "SRR_SNAPSHOT_MISMATCH",
                    format!(
                        "timestamp binds snapshot version {} digest {}, found version {} digest {}",
                        bound.version, bound.sha256, snap.version, snap.envelope.file_sha256
                    ),
                ));
            }
        }
        if snap.envelope.is_expired(now) && currency == Currency::Current {
            currency = Currency::Stale;
        }
        Some(snap)
    } else {
        if currency == Currency::Current {
            currency = Currency::Unknown;
        }
        None
    };

    // release/targets: the only role that authorises target bytes
    let rel_path = dir.join(RELEASE_JSON);
    let env = Envelope::read(&rel_path)?;
    root.verify_role(ROLE_RELEASE, &env)?;
    let release = Release::parse(env)?;
    if release.version < floors.metadata_floor(ROLE_RELEASE) {
        return Err(rollback_err(
            ROLE_RELEASE,
            release.version,
            floors.metadata_floor(ROLE_RELEASE),
        ));
    }
    if let Some(snap) = snapshot.as_ref() {
        let bound = snap.meta.get(RELEASE_JSON).ok_or_else(|| {
            GovError::new(
                "SRR_RELEASE_NOT_BOUND",
                "snapshot metadata does not bind release.json",
            )
        })?;
        if bound.sha256 != release.envelope.file_sha256 || bound.version != release.version {
            return Err(GovError::new(
                "SRR_RELEASE_NOT_IN_SNAPSHOT",
                format!(
                    "snapshot binds release version {} digest {}, found version {} digest {}",
                    bound.version, bound.sha256, release.version, release.envelope.file_sha256
                ),
            ));
        }
    }
    if release.envelope.is_expired(now) {
        return Err(GovError::new(
            "SRR_METADATA_EXPIRED",
            format!("release metadata for {} expired at {} against the declared local clock {now}; trust-changing lifecycle operations are refused (ARCH-0003 §7.2). An already authenticated installed system is not disabled by this.", release.release_version, release.expires),
        ));
    }
    // Advance the metadata high-water only after every check above has passed, and only upward.
    floors.raise_metadata(ROLE_RELEASE, release.version);
    if let Some(s) = snapshot.as_ref() {
        floors.raise_metadata(ROLE_SNAPSHOT, s.version);
    }
    if let Some(t) = timestamp.as_ref() {
        floors.raise_metadata(ROLE_TIMESTAMP, t.version);
    }
    floors.raise_metadata(ROLE_ROOT, root.version);
    Ok((release, currency))
}

fn rollback_err(role: &str, found: u64, floor: u64) -> GovError {
    GovError::new(
        "SRR_METADATA_ROLLBACK",
        format!("{role} metadata version {found} is below this machine's protected high-water {floor}; replaying older metadata is refused"),
    )
    .with_details(json!({"role": role, "presented_version": found, "protected_high_water": floor}))
}

/// Every migration file in the staged payload must be named by the signed release metadata, and match its digest.
fn verify_migrations(rel: &Release, payload_dir: &Path) -> Result<()> {
    let migs = crate::migrations::framework::load_migrations(payload_dir);
    if migs.is_empty() && rel.migrations.is_empty() {
        return Ok(());
    }
    for m in &migs {
        let id = m.get("id").and_then(|v| v.as_str()).unwrap_or("");
        let bound = rel.migrations.iter().find(|b| b.id == id);
        match bound {
            Some(b) => {
                let actual = crate::util::sha256_text(&crate::util::canonical_json(m));
                if !b.sha256.is_empty() && b.sha256 != actual {
                    return Err(GovError::new(
                        "SRR_MIGRATION_MODIFIED",
                        format!("migration '{id}' in the staged payload has digest {actual}, the signed release metadata binds {}", b.sha256),
                    ));
                }
            }
            None => {
                return Err(GovError::new(
                    "SRR_MIGRATION_NOT_AUTHORISED",
                    format!("the staged payload carries migration '{id}', which the signed release metadata does not authorise"),
                ))
            }
        }
    }
    Ok(())
}

pub fn current_platform() -> String {
    format!("{}-{}", std::env::consts::OS, std::env::consts::ARCH)
}

// ------------------------------------------------------------------------------- post-install floor advancement

/// Durably record the install and advance the floors — **step (9) of the transaction ordering**, called only after
/// the atomic commit and the post-commit verification have succeeded (`SRR-R0-L5`).
///
/// Also the single site that attempts break-glass exit, so the `SRR2-R1-C1` policy point has exactly one caller
/// path (`OWNER-DECISION-0006` §7).
pub fn record_installed(auth: &AuthenticatedRelease) -> Result<Value> {
    let ms = &auth.machine;
    let mut floors = Floors::load(ms, &auth.product);
    // Break-glass never lowers a floor; the raise_* helpers are monotonic, so a below-floor install moves nothing.
    floors.raise_release(
        &auth.release_version,
        auth.sequence,
        auth.authenticity == Authenticity::Authentic,
    );
    if !auth.floors.minimum_secure_release.is_empty() {
        floors.raise_minimum_secure(
            &auth.floors.minimum_secure_release,
            auth.floors.minimum_secure_sequence,
            &auth.floors.minimum_secure_source_sha256,
        );
    }
    for (role, v) in &auth.floors.metadata_high_water {
        floors.raise_metadata(role, *v);
    }
    floors.save(ms)?;
    InstalledRecord {
        product: auth.product.clone(),
        release_version: auth.release_version.clone(),
        sequence: auth.sequence,
        channel: auth.channel.clone(),
        payload_hash: auth.payload_hash.clone(),
        kernel_manifest_hash: auth.kernel_manifest_hash.clone(),
        authenticity: auth.authenticity.as_str().to_string(),
        verified_at: now_iso(),
        release_metadata_sha256: auth.release_metadata_sha256.clone(),
    }
    .save(ms)?;
    // OWNER-DECISION-0006 §7 — the only break-glass exit attempt in the implementation.
    let exit = breakglass::try_exit(
        ms,
        &auth.product,
        auth.sequence,
        &auth.release_version,
        auth.authenticity.is_authenticated(),
        &floors,
    )?;
    staging::finish(ms, &auth.staged, true)?;
    Ok(
        json!({"floors": floors.to_value(), "break_glass_exit": exit,
              "marked_degraded": breakglass::is_degraded(ms, &auth.product)}),
    )
}
