//! Signed Release Root v1 — protected local machine state.
//!
//! ARCH-0003 §7: "Clients persist the highest valid root/metadata versions and minimum secure release they have
//! observed. Those floors are a property of **the machine**, not of one operation." This module is that state.
//!
//! ## Why it lives outside every repository
//!
//! Nothing here is stored under a governed project. `governance/`, `framework.lock`, `KERNEL_MANIFEST.json` and the
//! Git working tree are all *candidate content* — the very inputs the frozen R1 section says must not be able to
//! create trusted identity. Protected state therefore lives in the machine/administrator domain:
//!
//! ```text
//! <state_root>/
//!   machine.json                 machine identity and the path this state was provisioned at
//!   trust/root.json              the trusted root metadata (administrator-provisioned bootstrap anchor)
//!   trust/provisioned.json       durable "this machine has a trust anchor" latch — never cleared
//!   floors/<product>.json        metadata high-water, release high-water, signed minimum secure release
//!   installed/<product>.json     what this machine itself verified and installed, bound by payload digest
//!   degraded/<product>.json      `DEGRADED — RECOVERY ONLY` marking and the break-glass entry record
//!   breakglass/inbox/            owner-signed authorisations are dropped here, out of band
//!   breakglass/consumed/         spent nonces (single use)
//!   journal/                     transaction intents for crash recovery
//!   staging/                     private verified-byte staging areas
//! ```
//!
//! `SRR2-R1-C3`: because none of this is inside a project, uninstalling the Governance OS from a project, deleting
//! `governance/`, or deleting the whole project directory leaves the floors intact. [`Floors::load`] reads them back
//! from a machine path that the project never had write access to.
//!
//! `SRR-R0-L5` — **durability ordering**. Every write here is temp-write → `fsync(file)` → `rename` → `fsync(dir)`,
//! so a record is either the old value or the complete new value. The ordering *between* records is fixed by
//! [`super::staging`] and is stated there.
use crate::util::{now_iso, sha256_text};
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

/// Environment variable that selects the protected state root.
///
/// It is honoured **only while the default root holds no trust anchor**. Once a machine has been provisioned, the
/// override is refused: an environment variable must never be able to move an already-provisioned machine onto a
/// different, attacker-chosen set of floors. See [`resolve_state_root`].
pub const ENV_STATE_DIR: &str = "GOV_MACHINE_STATE_DIR";

/// Environment variables that are explicitly refused as *authority*. Reading them at all would be a bug; this list
/// exists so that an operator who sets one gets a typed refusal instead of silence (frozen R1: "project, CLI,
/// environment, model and plugin inputs cannot create trust or approval").
pub const REFUSED_AUTHORITY_ENV: &[&str] = &[
    "GOV_BREAK_GLASS",
    "GOV_BREAKGLASS",
    "GOV_TRUST_OVERRIDE",
    "GOV_SKIP_VERIFY",
    "GOV_ALLOW_UNSIGNED",
    "GOV_RELEASE_AUTHORITY",
    "GOV_HUMAN_GATE_APPROVED",
    "GOV_FLOOR_OVERRIDE",
    "GOV_MINIMUM_SECURE_RELEASE",
];

/// Refuse any attempt to supply authority through the environment. Called at the top of the single verifier.
pub fn refuse_authority_env() -> Result<()> {
    for k in REFUSED_AUTHORITY_ENV {
        if std::env::var_os(k).is_some() {
            return Err(GovError::new(
                "SRR_ENV_CANNOT_CREATE_AUTHORITY",
                format!("{k} is set. Environment variables cannot create release authority, break-glass authority or Human Gate approval (ARCH-0003 §8). Unset it and use the owner-controlled local mechanism."),
            ).with_details(json!({"variable": k})));
        }
    }
    Ok(())
}

fn default_state_root() -> PathBuf {
    if let Some(x) = std::env::var_os("XDG_STATE_HOME").filter(|v| !v.is_empty()) {
        return PathBuf::from(x).join("governance-os").join("machine");
    }
    if let Some(h) = std::env::var_os("HOME").filter(|v| !v.is_empty()) {
        return PathBuf::from(h)
            .join(".local")
            .join("state")
            .join("governance-os")
            .join("machine");
    }
    std::env::temp_dir().join("governance-os").join("machine")
}

/// Resolve the protected state root.
///
/// Precedence, and why:
/// 1. If the **default** root already holds a trust anchor, that is the machine's state and `GOV_MACHINE_STATE_DIR`
///    is refused. An env var cannot relocate a provisioned machine onto different floors.
/// 2. Otherwise `GOV_MACHINE_STATE_DIR`, if set — this is how an administrator provisions a CI runner or a second
///    machine "outside the project repository" (ARCH-0003 §8).
/// 3. Otherwise the default.
pub fn resolve_state_root() -> Result<PathBuf> {
    let default = default_state_root();
    let default_provisioned = default.join("trust").join("provisioned.json").exists();
    match std::env::var_os(ENV_STATE_DIR).filter(|v| !v.is_empty()) {
        Some(v) if default_provisioned => {
            let candidate = PathBuf::from(&v);
            if candidate == default {
                Ok(default)
            } else {
                Err(GovError::new(
                    "SRR_PROTECTED_STATE_OVERRIDE_REFUSED",
                    format!("{ENV_STATE_DIR} is set, but this machine is already provisioned at {}. An environment variable may not relocate a provisioned machine's protected floors.", default.display()),
                ))
            }
        }
        Some(v) => Ok(PathBuf::from(v)),
        None => Ok(default),
    }
}

/// Durable write: temp file → fsync → rename → fsync(dir). Either the old bytes or all the new bytes survive a crash.
pub fn write_durable(path: &Path, v: &Value) -> Result<()> {
    let parent = path.parent().ok_or_else(|| {
        GovError::new(
            "IO_ERROR",
            format!("{} has no parent directory", path.display()),
        )
    })?;
    std::fs::create_dir_all(parent)
        .map_err(|e| GovError::io(&format!("mkdir {}", parent.display()), e))?;
    let tmp = parent.join(format!(
        ".{}.tmp-{}",
        path.file_name()
            .map(|f| f.to_string_lossy().to_string())
            .unwrap_or("state".into()),
        std::process::id()
    ));
    let body = serde_json::to_string_pretty(&crate::util::sorted(v))? + "\n";
    {
        use std::io::Write;
        let mut f = std::fs::File::create(&tmp)
            .map_err(|e| GovError::io(&format!("create {}", tmp.display()), e))?;
        f.write_all(body.as_bytes())
            .map_err(|e| GovError::io(&format!("write {}", tmp.display()), e))?;
        f.sync_all()
            .map_err(|e| GovError::io(&format!("fsync {}", tmp.display()), e))?;
    }
    std::fs::rename(&tmp, path)
        .map_err(|e| GovError::io(&format!("rename into {}", path.display()), e))?;
    fsync_dir(parent);
    Ok(())
}

/// fsync a directory so a rename into it is durable. Best-effort: not every platform/filesystem supports it, and a
/// failure here degrades crash-window tightness, never correctness of the committed bytes.
pub fn fsync_dir(dir: &Path) {
    if let Ok(f) = std::fs::File::open(dir) {
        let _ = f.sync_all();
    }
}

fn read_opt(path: &Path) -> Option<Value> {
    crate::util::read_json(path).ok()
}

// ---------------------------------------------------------------------------------------------- machine state

#[derive(Debug, Clone)]
pub struct MachineState {
    pub root: PathBuf,
    pub machine_id: String,
}

impl MachineState {
    /// Open (creating the layout if absent) the protected state for this machine.
    pub fn open() -> Result<MachineState> {
        MachineState::at(&resolve_state_root()?)
    }

    pub fn at(root: &Path) -> Result<MachineState> {
        for d in [
            "trust",
            "floors",
            "installed",
            "degraded",
            "journal",
            "staging",
            "breakglass/inbox",
            "breakglass/consumed",
        ] {
            std::fs::create_dir_all(root.join(d))
                .map_err(|e| GovError::io(&format!("mkdir {}", root.join(d).display()), e))?;
        }
        let mpath = root.join("machine.json");
        let machine_id = match read_opt(&mpath) {
            Some(v) if v.get("machine_id").and_then(|x| x.as_str()).is_some() => {
                v["machine_id"].as_str().unwrap().to_string()
            }
            _ => {
                // Stable-per-state-root identity. It names the machine in durable break-glass records
                // (OWNER-DECISION-0006 §3); it is not a secret and grants nothing.
                let id = sha256_text(&format!(
                    "{}|{}|{}",
                    root.display(),
                    std::env::var("HOSTNAME").unwrap_or_default(),
                    crate::util::short_uuid()
                ))[..32]
                    .to_string();
                write_durable(
                    &mpath,
                    &json!({"machine_id": id, "created": now_iso(), "state_root": root.display().to_string(),
                            "note": "Protected Governance OS machine state (Signed Release Root v1). Not part of any project repository."}),
                )?;
                id
            }
        };
        Ok(MachineState {
            root: root.to_path_buf(),
            machine_id,
        })
    }

    pub fn trust_dir(&self) -> PathBuf {
        self.root.join("trust")
    }
    pub fn root_metadata_path(&self) -> PathBuf {
        self.trust_dir().join("root.json")
    }
    pub fn provisioned_path(&self) -> PathBuf {
        self.trust_dir().join("provisioned.json")
    }
    pub fn floors_path(&self, product: &str) -> PathBuf {
        self.root
            .join("floors")
            .join(format!("{}.json", safe(product)))
    }
    pub fn installed_path(&self, product: &str) -> PathBuf {
        self.root
            .join("installed")
            .join(format!("{}.json", safe(product)))
    }
    pub fn degraded_path(&self, product: &str) -> PathBuf {
        degraded_path_at(&self.root, product)
    }
    pub fn journal_dir(&self) -> PathBuf {
        self.root.join("journal")
    }
    pub fn staging_dir(&self) -> PathBuf {
        self.root.join("staging")
    }
    pub fn break_glass_inbox(&self) -> PathBuf {
        self.root.join("breakglass").join("inbox")
    }
    pub fn break_glass_consumed(&self) -> PathBuf {
        self.root.join("breakglass").join("consumed")
    }

    /// Has an administrator ever provisioned a trust anchor here? This latch is set at provisioning and never
    /// cleared, so a machine cannot be pushed back to the unprovisioned posture by deleting `root.json`.
    pub fn is_provisioned(&self) -> bool {
        self.provisioned_path().exists()
    }

    pub fn provisioned_record(&self) -> Value {
        read_opt(&self.provisioned_path()).unwrap_or(Value::Null)
    }

    /// Record the trust anchor. `root_bytes` are the exact provisioned bytes.
    ///
    /// **This is the `OWNER-DECISION-0006` §6 bullet 4 sink.** It is the only function in the product that writes
    /// `trust/root.json` and the provisioning latch, so re-anchoring the machine, revoking a key by omission from
    /// a successor, and moving the protected `root` metadata high-water all pass through here and nowhere else.
    /// The §6 check therefore lives *inside* it rather than beside its callers: `provision::root_update` reached
    /// no enforcement point at all (`AR29-B1`), and a guard bolted onto that one function would have left the
    /// class open for whatever trust-changing path is written next.
    ///
    /// The check is taken at the instant of the effect, against this machine's own protected state, and it is not
    /// parameterised on a [`crate::srr::breakglass::Clearance`] the caller supplies: a token minted earlier is a
    /// decision taken earlier, and the question §6 asks is whether the machine is marked *now*.
    pub fn set_root_metadata(&self, root_bytes: &[u8], version: u64, product: &str) -> Result<()> {
        // Checked under this machine's own marking key (`FRAMEWORK_NAME`, which is what `enter` writes and every
        // other consumer reads) and, when the anchor being written names a different product, under that too — so
        // a successor root declaring a different product cannot step around the marking.
        for key in [crate::FRAMEWORK_NAME, product] {
            crate::srr::breakglass::guard_effect_on(
                self,
                key,
                crate::srr::breakglass::Effect::TrustPolicyMutation,
                "trust anchor write",
            )?;
        }
        let p = self.root_metadata_path();
        std::fs::create_dir_all(self.trust_dir()).map_err(|e| GovError::io("mkdir trust", e))?;
        let tmp = self.trust_dir().join(".root.json.tmp");
        {
            use std::io::Write;
            let mut f =
                std::fs::File::create(&tmp).map_err(|e| GovError::io("create root.json.tmp", e))?;
            f.write_all(root_bytes)
                .map_err(|e| GovError::io("write root.json.tmp", e))?;
            f.sync_all()
                .map_err(|e| GovError::io("fsync root.json.tmp", e))?;
        }
        std::fs::rename(&tmp, &p).map_err(|e| GovError::io("rename root.json", e))?;
        fsync_dir(&self.trust_dir());
        // The latch is written after the anchor, so a crash never claims provisioning without an anchor.
        let mut rec = self.provisioned_record();
        if rec.is_null() {
            rec =
                json!({"provisioned_at": now_iso(), "state_root": self.root.display().to_string()});
        }
        rec["product"] = json!(product);
        rec["root_version"] = json!(version);
        rec["root_sha256"] = json!(crate::util::sha256_hex(root_bytes));
        rec["updated_at"] = json!(now_iso());
        write_durable(&self.provisioned_path(), &rec)
    }
}

/// Where the `DEGRADED — RECOVERY ONLY` marking record for `product` lives under a protected state root.
///
/// `AR29-N3`: the hot-path guard used to build this path with its own, weaker sanitiser while
/// [`MachineState::degraded_path`] used [`safe`]. The two agreed for the current `FRAMEWORK_NAME` and would have
/// disagreed for any product string containing a character only one of them rewrote — the guard would then have
/// read a different file from the one `enter` wrote, which is a silent, total bypass of `OWNER-DECISION-0006` §6
/// at the main chokepoint. There is now one function and one spelling.
///
/// This resolves a path *within* an already-resolved state root. It is not, and must not become, machine-state
/// root resolution: [`resolve_state_root`] and `default_state_root` are owner-closed by `OWNER-DECISION-0007` §1
/// and are untouched.
pub fn degraded_path_at(root: &Path, product: &str) -> PathBuf {
    root.join("degraded").join(format!("{}.json", safe(product)))
}

fn safe(s: &str) -> String {
    s.chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || c == '-' || c == '_' || c == '.' {
                c
            } else {
                '_'
            }
        })
        .collect()
}

// ---------------------------------------------------------------------------------------------- floors

/// The protected floors for one product on this machine.
///
/// Three distinct, separately durable things:
/// * `metadata_high_water` — highest accepted version per metadata role. Pure replay protection.
/// * `release_high_water`  — the highest release this machine has itself verified **and installed**.
/// * `minimum_secure`      — the signed minimum secure release, taken from release metadata; monotonic, never
///   lowered, and explicitly never lowered by break-glass (OWNER-DECISION-0006 §8).
#[derive(Debug, Clone, Default)]
pub struct Floors {
    pub product: String,
    pub metadata_high_water: std::collections::BTreeMap<String, u64>,
    pub release_high_water_version: String,
    pub release_high_water_sequence: u64,
    pub minimum_secure_release: String,
    pub minimum_secure_sequence: u64,
    pub minimum_secure_source_sha256: String,
    pub updated_at: String,
}

impl Floors {
    pub fn load(ms: &MachineState, product: &str) -> Floors {
        let v = read_opt(&ms.floors_path(product)).unwrap_or(Value::Null);
        let mut f = Floors {
            product: product.to_string(),
            ..Default::default()
        };
        if let Some(m) = v.get("metadata_high_water").and_then(|x| x.as_object()) {
            for (k, x) in m {
                f.metadata_high_water
                    .insert(k.clone(), x.as_u64().unwrap_or(0));
            }
        }
        f.release_high_water_version = v
            .get("release_high_water")
            .and_then(|x| x.get("version"))
            .and_then(|x| x.as_str())
            .unwrap_or("")
            .to_string();
        f.release_high_water_sequence = v
            .get("release_high_water")
            .and_then(|x| x.get("sequence"))
            .and_then(|x| x.as_u64())
            .unwrap_or(0);
        f.minimum_secure_release = v
            .get("minimum_secure")
            .and_then(|x| x.get("release"))
            .and_then(|x| x.as_str())
            .unwrap_or("")
            .to_string();
        f.minimum_secure_sequence = v
            .get("minimum_secure")
            .and_then(|x| x.get("sequence"))
            .and_then(|x| x.as_u64())
            .unwrap_or(0);
        f.minimum_secure_source_sha256 = v
            .get("minimum_secure")
            .and_then(|x| x.get("source_metadata_sha256"))
            .and_then(|x| x.as_str())
            .unwrap_or("")
            .to_string();
        f.updated_at = v
            .get("updated_at")
            .and_then(|x| x.as_str())
            .unwrap_or("")
            .to_string();
        f
    }

    pub fn to_value(&self) -> Value {
        json!({
            "product": self.product,
            "metadata_high_water": self.metadata_high_water,
            "release_high_water": {"version": self.release_high_water_version, "sequence": self.release_high_water_sequence},
            "minimum_secure": {"release": self.minimum_secure_release, "sequence": self.minimum_secure_sequence, "source_metadata_sha256": self.minimum_secure_source_sha256},
            "updated_at": self.updated_at,
            "note": "Protected Governance OS floors (Signed Release Root v1). Monotonic: values here are never lowered, reset or forgotten, including by break-glass recovery (OWNER-DECISION-0006 §8).",
        })
    }

    /// Persist the floors.
    ///
    /// **The `OWNER-DECISION-0006` §6 bullet 6 (and §8) sink.** This is the only function in the product that
    /// writes `floors/<product>.json`, so every path that could lower or reset a floor passes through it — and it
    /// refuses to lower one. The persisted value is re-applied through the same monotonic `raise_*` functions
    /// before the write, so a floor can only ever move up, whatever the in-memory value says and whoever set it.
    ///
    /// Repair 2's census recorded bullet 6 as `no primitive exists: Floors::raise_* are monotonic and never write
    /// a lower value`. The derived census (`SECTION_6_SIGNATURES`) contradicts that by construction: every field
    /// of [`Floors`] is `pub` and `save` is `pub`, so `f.release_high_water_sequence = 0; f.save(&ms)` is a
    /// floor-lowering primitive that the mutator census could not see, exactly the shape of `AR31-N1` one bullet
    /// over. No code in the product does it today and the certification suite measures that; the property is now
    /// a property of the sink rather than of the callers, so it also holds for code that has not been written.
    ///
    /// Monotonicity is enforced here **at all times**, not only below floor: §8 says break-glass does not lower,
    /// reset or forget the floors, and ARCH-0003 §7 says the floors are the highest values the machine has
    /// observed. Neither is conditional on the marking, and a check that binds always cannot be skipped by a
    /// caller that reaches it at the wrong moment. Every current caller loads, raises and saves, so the merge is
    /// a no-op for all of them.
    pub fn save(&mut self, ms: &MachineState) -> Result<()> {
        let persisted = Floors::load(ms, &self.product);
        let roles: Vec<(String, u64)> = persisted
            .metadata_high_water
            .iter()
            .map(|(k, v)| (k.clone(), *v))
            .collect();
        for (role, version) in roles {
            self.raise_metadata(&role, version);
        }
        self.raise_release(
            &persisted.release_high_water_version,
            persisted.release_high_water_sequence,
            true,
        );
        self.raise_minimum_secure(
            &persisted.minimum_secure_release,
            persisted.minimum_secure_sequence,
            &persisted.minimum_secure_source_sha256,
        );
        self.updated_at = now_iso();
        write_durable(&ms.floors_path(&self.product), &self.to_value())
    }

    pub fn metadata_floor(&self, role: &str) -> u64 {
        *self.metadata_high_water.get(role).unwrap_or(&0)
    }

    /// Raise a metadata high-water. Monotonic by construction: a lower value is ignored, never written.
    pub fn raise_metadata(&mut self, role: &str, version: u64) {
        let cur = self.metadata_floor(role);
        if version > cur {
            self.metadata_high_water.insert(role.to_string(), version);
        }
    }

    /// Raise the release high-water. Monotonic in **two independent bases**, so a machine that starts
    /// unprovisioned and is later given a trust anchor never loses a floor and never mixes the bases:
    ///
    /// * `release_high_water_version` — semantic version ordering, for the human-readable floor and for releases
    ///   whose metadata omits an explicit sequence.
    /// * `release_high_water_sequence` — the signed monotonic sequence.
    ///
    /// **Both are advanced only from a verified signed release** (`signed == true`). ARCH-0003 §7 says clients
    /// persist "the **highest valid** root/metadata versions and minimum secure release they have observed", and
    /// on a machine with no trust anchor nothing has been validated. Recording an unauthenticated version as a
    /// protected floor would manufacture a security claim out of an unverified observation — the exact move the
    /// frozen R1 section forbids — and would also brick rollback on a machine that has no break-glass authority to
    /// unbrick it, because break-glass is itself anchored in the trusted root's `recovery` role.
    pub fn raise_release(&mut self, version: &str, sequence: u64, signed: bool) {
        if !signed {
            return;
        }
        if !version.is_empty()
            && (self.release_high_water_version.is_empty()
                || crate::lock::compare_versions(version, &self.release_high_water_version)
                    == std::cmp::Ordering::Greater)
        {
            self.release_high_water_version = version.to_string();
        }
        if sequence > self.release_high_water_sequence {
            self.release_high_water_sequence = sequence;
        }
    }

    /// The last release this machine observed, whatever its posture. Reported, never enforced as a floor; it
    /// exists so `gov trust status` can be honest about what has been installed here.
    pub fn observed_only(&self) -> bool {
        self.release_high_water_version.is_empty() && self.release_high_water_sequence == 0
    }

    /// Raise the signed minimum secure release. Monotonic; a lower signed minimum is ignored, so a replayed or
    /// downgraded metadata set cannot relax the floor.
    pub fn raise_minimum_secure(&mut self, release: &str, sequence: u64, source_sha256: &str) {
        if sequence > self.minimum_secure_sequence {
            self.minimum_secure_sequence = sequence;
            self.minimum_secure_release = release.to_string();
            self.minimum_secure_source_sha256 = source_sha256.to_string();
        }
    }

    /// The effective release floor in the signed basis: the higher of the protected local high-water and the
    /// signed minimum secure release. Used by the one floor check and by the `SRR2-R1-C1` exit policy point.
    pub fn effective_floor_sequence(&self) -> u64 {
        self.release_high_water_sequence
            .max(self.minimum_secure_sequence)
    }

    /// The effective release floor in the semantic-version basis.
    pub fn effective_floor_version(&self) -> String {
        if self.minimum_secure_release.is_empty() {
            return self.release_high_water_version.clone();
        }
        if self.release_high_water_version.is_empty() {
            return self.minimum_secure_release.clone();
        }
        if crate::lock::compare_versions(
            &self.minimum_secure_release,
            &self.release_high_water_version,
        ) == std::cmp::Ordering::Greater
        {
            self.minimum_secure_release.clone()
        } else {
            self.release_high_water_version.clone()
        }
    }
}

// ---------------------------------------------------------------------------------------------- installed record

/// This machine's own protected record of what it verified and installed.
///
/// ARCH-0003 §7: "Where no current metadata is reachable, the authenticity of an installed local recovery path
/// derives from this machine's own protected record of the release identity it previously verified and installed,
/// never from the manifest, the lock, the repository or mutually consistent files delivered with the copy."
///
/// `SRR2-R1-C2` — the record binds the **payload digests** actually verified (`payload_hash` and
/// `kernel_manifest_hash`), not the release version alone, so a different payload claiming the same version does
/// not match it.
#[derive(Debug, Clone, Default)]
pub struct InstalledRecord {
    pub product: String,
    pub release_version: String,
    pub sequence: u64,
    pub channel: String,
    pub payload_hash: String,
    pub kernel_manifest_hash: String,
    pub authenticity: String,
    pub verified_at: String,
    pub release_metadata_sha256: String,
}

impl InstalledRecord {
    pub fn load(ms: &MachineState, product: &str) -> Option<InstalledRecord> {
        let v = read_opt(&ms.installed_path(product))?;
        let g = |k: &str| v.get(k).and_then(|x| x.as_str()).unwrap_or("").to_string();
        Some(InstalledRecord {
            product: product.to_string(),
            release_version: g("release_version"),
            sequence: v.get("sequence").and_then(|x| x.as_u64()).unwrap_or(0),
            channel: g("channel"),
            payload_hash: g("payload_hash"),
            kernel_manifest_hash: g("kernel_manifest_hash"),
            authenticity: g("authenticity"),
            verified_at: g("verified_at"),
            release_metadata_sha256: g("release_metadata_sha256"),
        })
    }

    pub fn save(&self, ms: &MachineState) -> Result<()> {
        write_durable(
            &ms.installed_path(&self.product),
            &json!({
                "product": self.product, "release_version": self.release_version, "sequence": self.sequence,
                "channel": self.channel, "payload_hash": self.payload_hash,
                "kernel_manifest_hash": self.kernel_manifest_hash, "authenticity": self.authenticity,
                "verified_at": self.verified_at, "release_metadata_sha256": self.release_metadata_sha256,
                "note": "SRR2-R1-C2: the offline-recovery authenticity basis is bound to the payload digests this machine verified, not to the release version alone.",
            }),
        )
    }

    /// Does this record vouch for the given measured payload? Digest-bound, per `SRR2-R1-C2`.
    pub fn vouches_for(&self, payload_hash: &str, kernel_manifest_hash: &str) -> bool {
        !self.payload_hash.is_empty()
            && self.payload_hash == payload_hash
            && (self.kernel_manifest_hash.is_empty()
                || self.kernel_manifest_hash == kernel_manifest_hash)
    }
}
