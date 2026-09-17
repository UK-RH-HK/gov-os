//! Signed Release Root v1 — TUF-style signed metadata model (ARCH-0003 §4, 00-ARCHITECTURE "Metadata roles").
//!
//! Roles, and what each one may *not* do:
//!
//! | role        | authorises                                             | cannot do                                  |
//! |-------------|--------------------------------------------------------|--------------------------------------------|
//! | `root`      | keys, thresholds, delegations, rotation, revocation    | publish releases unattended                |
//! | `release`   | one exact release identity and its exact payload bytes | redefine root authority                    |
//! | `snapshot`  | one consistent set of metadata versions                | authorise target bytes                     |
//! | `timestamp` | bounded freshness for trust-changing operations        | authorise target bytes or rewrite history  |
//! | `recovery`  | one below-floor break-glass entry (OWNER-DECISION-0006)| authorise a release or lower a floor       |
//!
//! ## Why the signed payload is raw bytes, not re-serialised JSON
//!
//! TUF canonicalises the `signed` object before signing. Re-implementing a canonical-JSON encoder is exactly the
//! kind of hand-rolled metadata handling the frozen R1 section forbids, and encoder disagreements are a classic
//! source of signature-bypass bugs. Instead this implementation signs **the exact bytes of the `signed` member as
//! they appear in the file**, extracted with `serde_json::value::RawValue` — a first-class serde_json facility.
//! There is therefore no canonicalisation step that a producer and a consumer can disagree about, and no way to
//! present one byte-string to the signature check and a different parse to the policy: the policy is parsed from
//! the same `RawValue` that was verified.
use crate::util::{now_iso, sha256_hex};
use crate::{GovError, Result};
use serde::Deserialize;
use serde_json::value::RawValue;
use std::collections::BTreeMap;
use std::path::Path;

pub const SPEC_VERSION: &str = "srr/1";

pub const ROLE_ROOT: &str = "root";
pub const ROLE_RELEASE: &str = "release";
pub const ROLE_SNAPSHOT: &str = "snapshot";
pub const ROLE_TIMESTAMP: &str = "timestamp";
pub const ROLE_RECOVERY: &str = "recovery";

/// Canonical on-disk names inside a metadata directory.
pub const ROOT_JSON: &str = "root.json";
pub const RELEASE_JSON: &str = "release.json";
pub const SNAPSHOT_JSON: &str = "snapshot.json";
pub const TIMESTAMP_JSON: &str = "timestamp.json";

// ---------------------------------------------------------------------------------------------- envelope

#[derive(Debug, Clone, Deserialize)]
pub struct Signature {
    pub keyid: String,
    pub sig: String,
}

/// `{"signed": {...}, "signatures": [...]}`. `signed` is kept as raw bytes so the verified byte-string and the
/// parsed policy are provably the same document.
#[derive(Debug, Deserialize)]
struct RawEnvelope<'a> {
    #[serde(borrow)]
    signed: &'a RawValue,
    signatures: Vec<Signature>,
}

/// A parsed metadata document whose signed bytes are retained for verification.
#[derive(Debug, Clone)]
pub struct Envelope {
    pub signed_bytes: Vec<u8>,
    pub signed: serde_json::Value,
    pub signatures: Vec<Signature>,
    /// SHA-256 over the whole file, used by snapshot/timestamp binding.
    pub file_sha256: String,
    pub source: String,
}

impl Envelope {
    pub fn parse(bytes: &[u8], source: &str) -> Result<Envelope> {
        let raw: RawEnvelope = serde_json::from_slice(bytes).map_err(|e| {
            GovError::new(
                "SRR_METADATA_MALFORMED",
                format!("{source}: not a signed-metadata envelope: {e}"),
            )
        })?;
        let signed_bytes = raw.signed.get().as_bytes().to_vec();
        let signed: serde_json::Value = serde_json::from_slice(&signed_bytes).map_err(|e| {
            GovError::new(
                "SRR_METADATA_MALFORMED",
                format!("{source}: signed payload is not an object: {e}"),
            )
        })?;
        if raw.signatures.is_empty() {
            return Err(GovError::new(
                "SRR_METADATA_UNSIGNED",
                format!("{source}: metadata carries no signatures"),
            ));
        }
        Ok(Envelope {
            signed_bytes,
            signed,
            signatures: raw.signatures,
            file_sha256: sha256_hex(bytes),
            source: source.to_string(),
        })
    }

    pub fn read(path: &Path) -> Result<Envelope> {
        let bytes = std::fs::read(path)
            .map_err(|e| GovError::io(&format!("read {}", path.display()), e))?;
        Envelope::parse(&bytes, &path.display().to_string())
    }

    pub fn typ(&self) -> &str {
        self.signed
            .get("_type")
            .and_then(|v| v.as_str())
            .unwrap_or("")
    }
    pub fn version(&self) -> u64 {
        self.signed
            .get("version")
            .and_then(|v| v.as_u64())
            .unwrap_or(0)
    }
    pub fn expires(&self) -> &str {
        self.signed
            .get("expires")
            .and_then(|v| v.as_str())
            .unwrap_or("")
    }
    pub fn spec_version(&self) -> &str {
        self.signed
            .get("spec_version")
            .and_then(|v| v.as_str())
            .unwrap_or("")
    }
    pub fn product(&self) -> &str {
        self.signed
            .get("product")
            .and_then(|v| v.as_str())
            .unwrap_or("")
    }

    /// Expiry is evaluated against the **declared local clock** (ARCH-0003 §1: the local time source is inside the
    /// trusted local boundary; no attested or network time is assumed, required or provided).
    ///
    /// `AR27-N1` — the comparison is lexicographic, which is only sound when both sides are in the one canonical
    /// form this profile emits. That precondition is now **checked rather than assumed**, and every way of
    /// failing it is expired. See [`expiry_fault`].
    pub fn is_expired(&self, now: &str) -> bool {
        self.expiry_fault(now).is_some()
    }

    /// Why the expiry check refuses, or `None` when `expires` is canonical and still in the future.
    ///
    /// Callers use this instead of formatting `expires` themselves, so a refusal states which of the three
    /// failures occurred rather than printing an absent or non-canonical value as if it were a date.
    pub fn expiry_fault(&self, now: &str) -> Option<String> {
        expiry_fault(self.expires(), now)
    }
}

/// The one timestamp form this profile emits and compares: `YYYY-MM-DDTHH:MM:SSZ` — UTC, second precision,
/// uppercase `T` and `Z`. This is exactly what [`crate::util::now_iso`] produces.
///
/// RFC-3339 is far wider than this: it permits lowercase `t`/`z`, fractional seconds, and numeric offsets such as
/// `+14:00`. None of those order correctly against this form under a string comparison — `2026-09-17T13:00:00+14:00`
/// is thirteen hours in the *past* at `2026-09-17T12:00:00Z` yet sorts after it. So the form is gated rather than
/// the comparison being widened: a stricter producer contract, checked on the untrusted side.
pub fn is_canonical_utc_timestamp(s: &str) -> bool {
    let b = s.as_bytes();
    b.len() == 20
        && b[0..4].iter().all(u8::is_ascii_digit)
        && b[4] == b'-'
        && b[5..7].iter().all(u8::is_ascii_digit)
        && b[7] == b'-'
        && b[8..10].iter().all(u8::is_ascii_digit)
        && b[10] == b'T'
        && b[11..13].iter().all(u8::is_ascii_digit)
        && b[13] == b':'
        && b[14..16].iter().all(u8::is_ascii_digit)
        && b[16] == b':'
        && b[17..19].iter().all(u8::is_ascii_digit)
        && b[19] == b'Z'
}

/// `AR27-N1` — the whole expiry decision, fail-closed in every direction.
///
/// Three things make metadata expired, not one:
///
/// 1. **no `expires` at all** — an expiry that is not stated is not a promise of immortality. The previous
///    default (`!e.is_empty() && ...`) meant metadata carrying no `expires` never expired;
/// 2. **a non-canonical `expires`** — a valid RFC-3339 string that is not [`is_canonical_utc_timestamp`] cannot be
///    ordered against the local clock by string comparison, so it is refused rather than mis-ordered;
/// 3. **a canonical `expires` at or before the declared local clock** — the ordinary case.
///
/// A `now` that is not canonical is also fail-closed: if the clock string cannot be compared, nothing can be
/// asserted to be unexpired. Every product caller passes [`local_clock_now`], which is canonical by construction.
pub fn expiry_fault(expires: &str, now: &str) -> Option<String> {
    if expires.is_empty() {
        return Some("the metadata carries no `expires` member; an expiry that is not stated is treated as expired (fail closed)".to_string());
    }
    if !is_canonical_utc_timestamp(expires) {
        return Some(format!(
            "`expires` is '{expires}', which is not the canonical UTC form YYYY-MM-DDTHH:MM:SSZ that this profile emits and compares; a non-canonical expiry is treated as expired (fail closed)"
        ));
    }
    if !is_canonical_utc_timestamp(now) {
        return Some(format!(
            "the declared local clock '{now}' is not in canonical UTC form YYYY-MM-DDTHH:MM:SSZ, so no expiry comparison can be trusted (fail closed)"
        ));
    }
    if expires <= now {
        return Some(format!(
            "expired at {expires} against the declared local clock {now}"
        ));
    }
    None
}

// ---------------------------------------------------------------------------------------------- roles / keys

#[derive(Debug, Clone)]
pub struct KeyEntry {
    pub keyid: String,
    pub keytype: String,
    pub scheme: String,
    pub public: String,
}

#[derive(Debug, Clone)]
pub struct RoleEntry {
    pub keyids: Vec<String>,
    pub threshold: usize,
}

/// A verified root document: the trust anchor every other role is checked against.
#[derive(Debug, Clone)]
pub struct Root {
    pub envelope: Envelope,
    pub product: String,
    pub version: u64,
    pub expires: String,
    pub keys: BTreeMap<String, KeyEntry>,
    pub roles: BTreeMap<String, RoleEntry>,
}

impl Root {
    pub fn parse(env: Envelope) -> Result<Root> {
        require_type(&env, ROLE_ROOT)?;
        require_spec(&env)?;
        let mut keys = BTreeMap::new();
        let obj = env
            .signed
            .get("keys")
            .and_then(|v| v.as_object())
            .ok_or_else(|| {
                GovError::new(
                    "SRR_METADATA_MALFORMED",
                    format!("{}: root.keys missing", env.source),
                )
            })?;
        for (id, k) in obj {
            let public = k
                .get("keyval")
                .and_then(|v| v.get("public"))
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let keytype = k
                .get("keytype")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let scheme = k
                .get("scheme")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            if keytype != super::crypto::KEYTYPE || scheme != super::crypto::SCHEME {
                return Err(GovError::new(
                    "SRR_UNSUPPORTED_KEY_SCHEME",
                    format!("{}: key {id} uses unsupported keytype/scheme {keytype}/{scheme}; this profile supports {}/{} only", env.source, super::crypto::KEYTYPE, super::crypto::SCHEME),
                ));
            }
            // The key id is derived from the key material, never taken on trust from the document: a document
            // cannot point one key id at another key's bytes.
            let derived = super::crypto::keyid(&public)?;
            if derived != *id {
                return Err(GovError::new(
                    "SRR_KEYID_MISMATCH",
                    format!(
                        "{}: key id {id} does not match SHA-256 of its public key ({derived})",
                        env.source
                    ),
                ));
            }
            keys.insert(
                id.clone(),
                KeyEntry {
                    keyid: id.clone(),
                    keytype,
                    scheme,
                    public,
                },
            );
        }
        let mut roles = BTreeMap::new();
        let robj = env
            .signed
            .get("roles")
            .and_then(|v| v.as_object())
            .ok_or_else(|| {
                GovError::new(
                    "SRR_METADATA_MALFORMED",
                    format!("{}: root.roles missing", env.source),
                )
            })?;
        for (name, r) in robj {
            let keyids: Vec<String> = r
                .get("keyids")
                .and_then(|v| v.as_array())
                .map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(String::from))
                        .collect()
                })
                .unwrap_or_default();
            let threshold = r.get("threshold").and_then(|v| v.as_u64()).unwrap_or(0) as usize;
            if threshold == 0 {
                return Err(GovError::new(
                    "SRR_METADATA_MALFORMED",
                    format!("{}: role {name} has threshold 0", env.source),
                ));
            }
            if keyids.len() < threshold {
                return Err(GovError::new(
                    "SRR_UNSATISFIABLE_THRESHOLD",
                    format!(
                        "{}: role {name} needs {threshold} signatures but lists {} keys",
                        env.source,
                        keyids.len()
                    ),
                ));
            }
            for k in &keyids {
                if !keys.contains_key(k) {
                    return Err(GovError::new(
                        "SRR_METADATA_MALFORMED",
                        format!("{}: role {name} references unknown key {k}", env.source),
                    ));
                }
            }
            roles.insert(name.clone(), RoleEntry { keyids, threshold });
        }
        for required in [ROLE_ROOT, ROLE_RELEASE, ROLE_SNAPSHOT, ROLE_TIMESTAMP] {
            if !roles.contains_key(required) {
                return Err(GovError::new(
                    "SRR_METADATA_MALFORMED",
                    format!(
                        "{}: root does not delegate the required role '{required}'",
                        env.source
                    ),
                ));
            }
        }
        let product = env.product().to_string();
        if product.is_empty() {
            return Err(GovError::new(
                "SRR_METADATA_MALFORMED",
                format!("{}: root does not bind a product identity", env.source),
            ));
        }
        Ok(Root {
            product,
            version: env.version(),
            expires: env.expires().to_string(),
            keys,
            roles,
            envelope: env,
        })
    }

    pub fn role(&self, name: &str) -> Result<&RoleEntry> {
        self.roles.get(name).ok_or_else(|| {
            GovError::new(
                "SRR_ROLE_NOT_DELEGATED",
                format!("root does not delegate role '{name}'"),
            )
        })
    }

    pub fn has_role(&self, name: &str) -> bool {
        self.roles.contains_key(name)
    }

    /// Count distinct authorised key ids with a valid signature over `env.signed_bytes`, and require the threshold.
    ///
    /// A signature from a key that is not listed for the role contributes nothing; duplicate signatures from one
    /// key id count once, so a threshold cannot be reached by repeating a single key.
    pub fn verify_role(&self, name: &str, env: &Envelope) -> Result<Vec<String>> {
        let role = self.role(name)?;
        let mut accepted: Vec<String> = vec![];
        for sig in &env.signatures {
            if !role.keyids.contains(&sig.keyid) || accepted.contains(&sig.keyid) {
                continue;
            }
            let Some(key) = self.keys.get(&sig.keyid) else {
                continue;
            };
            if super::crypto::verify_strict(&key.public, &sig.sig, &env.signed_bytes).is_ok() {
                accepted.push(sig.keyid.clone());
            }
        }
        if accepted.len() < role.threshold {
            return Err(GovError::new(
                "SRR_THRESHOLD_NOT_MET",
                format!(
                    "{}: role '{name}' requires {} valid signature(s) from its authorised keys, found {}",
                    env.source,
                    role.threshold,
                    accepted.len()
                ),
            )
            .with_details(serde_json::json!({
                "role": name, "threshold": role.threshold, "accepted_keyids": accepted,
                "presented_keyids": env.signatures.iter().map(|s| s.keyid.clone()).collect::<Vec<_>>(),
            })));
        }
        Ok(accepted)
    }
}

fn require_type(env: &Envelope, want: &str) -> Result<()> {
    if env.typ() != want {
        return Err(GovError::new(
            "SRR_METADATA_WRONG_ROLE",
            format!(
                "{}: expected _type '{want}', found '{}'",
                env.source,
                env.typ()
            ),
        ));
    }
    Ok(())
}

fn require_spec(env: &Envelope) -> Result<()> {
    if env.spec_version() != SPEC_VERSION {
        return Err(GovError::new(
            "SRR_UNSUPPORTED_SPEC_VERSION",
            format!(
                "{}: spec_version '{}' is not supported (this verifier implements '{SPEC_VERSION}')",
                env.source,
                env.spec_version()
            ),
        ));
    }
    Ok(())
}

// ---------------------------------------------------------------------------------- root succession (SRR-R0-L1)

/// Accept a candidate root as the successor of `current`.
///
/// `SRR-R0-L1` — the R0 architecture imported client-side root succession "by reference from a mature TUF-style
/// metadata model". These are the concrete acceptance rules this implementation applies, stated rather than
/// referenced:
///
/// 1. the candidate must bind the **same product** as the trusted root;
/// 2. its version must be exactly `current.version + 1` — no gaps, so a chain cannot skip a root that revoked a
///    key, and no repeats, so an old root cannot be replayed;
/// 3. it must be signed by a threshold of the **outgoing** root's `root` role (succession authority), **and**
/// 4. by a threshold of its **own** `root` role (proof the incoming quorum holds the new keys);
/// 5. the candidate must not be expired against the declared local clock;
/// 6. keys and delegations absent from the candidate are revoked from the moment it is accepted — no grace period,
///    no carry-forward. Revocation is expressed by omission, which is why (2) forbids gaps.
///
/// Rotating more than one version at a time is performed by applying this function repeatedly over the ordered
/// chain, so every intermediate root's revocations take effect.
pub fn accept_root_succession(current: &Root, candidate_env: Envelope, now: &str) -> Result<Root> {
    let candidate = Root::parse(candidate_env)?;
    if candidate.product != current.product {
        return Err(GovError::new(
            "SRR_ROOT_WRONG_PRODUCT",
            format!(
                "candidate root binds product '{}', the trusted root binds '{}'",
                candidate.product, current.product
            ),
        ));
    }
    if candidate.version != current.version + 1 {
        return Err(GovError::new(
            "SRR_ROOT_VERSION_NOT_SUCCESSOR",
            format!(
                "candidate root version {} is not the immediate successor of the trusted root version {} (succession must be applied one version at a time so that every intermediate revocation takes effect)",
                candidate.version, current.version
            ),
        ));
    }
    // (3) outgoing quorum authorises the succession
    current
        .verify_role(ROLE_ROOT, &candidate.envelope)
        .map_err(|e| {
            GovError::new(
                "SRR_ROOT_SUCCESSION_UNAUTHORISED",
                format!(
                    "the trusted root's quorum did not authorise this successor: {}",
                    e.message
                ),
            )
            .with_details(e.details)
        })?;
    // (4) incoming quorum proves possession
    candidate
        .verify_role(ROLE_ROOT, &candidate.envelope)
        .map_err(|e| {
            GovError::new(
                "SRR_ROOT_SUCCESSION_UNAUTHORISED",
                format!(
                    "the candidate root is not self-signed by its own quorum: {}",
                    e.message
                ),
            )
            .with_details(e.details)
        })?;
    // (5) freshness
    if let Some(fault) = candidate.envelope.expiry_fault(now) {
        return Err(GovError::new(
            "SRR_METADATA_EXPIRED",
            format!("candidate root version {}: {fault}", candidate.version),
        ));
    }
    Ok(candidate)
}

/// Verify a self-contained root document against itself — used only when an administrator provisions the *first*
/// trust anchor, where bootstrap authenticity comes from the platform/admin installation boundary (ARCH-0003 §5),
/// not from the file. This is never used to accept a later root: succession always runs through
/// [`accept_root_succession`].
pub fn parse_self_signed_root(env: Envelope, now: &str) -> Result<Root> {
    let root = Root::parse(env)?;
    root.verify_role(ROLE_ROOT, &root.envelope)?;
    if let Some(fault) = root.envelope.expiry_fault(now) {
        return Err(GovError::new(
            "SRR_METADATA_EXPIRED",
            format!("root version {}: {fault}", root.version),
        ));
    }
    Ok(root)
}

// ---------------------------------------------------------------------------------------------- release metadata

/// One file of a release payload, bound by digest and length.
#[derive(Debug, Clone)]
pub struct PayloadFile {
    pub path: String,
    pub sha256: String,
    pub length: Option<u64>,
}

/// A migration identity bound by the release metadata (frozen R0 item 3 / R1 "modified ... migration ... fail closed").
#[derive(Debug, Clone)]
pub struct MigrationIdentity {
    pub id: String,
    pub from_version: String,
    pub to_version: String,
    pub sha256: String,
}

/// A delegated signed target: how a **remotely acquired** privileged plugin / tool / profile is authorised
/// (`SRR-R0-L6`). Built-in capabilities shipped inside the verified kernel payload are covered by the release
/// payload digests and need no delegation.
#[derive(Debug, Clone)]
pub struct Delegation {
    pub name: String,
    pub keyids: Vec<String>,
    pub threshold: usize,
    pub paths: Vec<String>,
    pub channel: Option<String>,
}

#[derive(Debug, Clone)]
pub struct Release {
    pub envelope: Envelope,
    pub product: String,
    /// Exact repository identity the release was published from/for.
    pub repository: String,
    /// `SRR-R0-L2` — the channel is a bound metadata field, not merely a scoping concept.
    pub channel: String,
    pub release_version: String,
    pub sequence: u64,
    pub version: u64,
    pub expires: String,
    pub platforms: Vec<String>,
    pub minimum_secure_release: String,
    pub minimum_secure_sequence: u64,
    pub payload_hash: String,
    pub kernel_manifest_hash: String,
    pub files: BTreeMap<String, PayloadFile>,
    pub migrations: Vec<MigrationIdentity>,
    pub schema_identities: serde_json::Value,
    pub delegations: Vec<Delegation>,
    pub evidence: serde_json::Value,
}

impl Release {
    pub fn parse(env: Envelope) -> Result<Release> {
        require_type(&env, ROLE_RELEASE)?;
        require_spec(&env)?;
        let s = &env.signed;
        let str_of = |k: &str| s.get(k).and_then(|v| v.as_str()).unwrap_or("").to_string();
        let product = str_of("product");
        let repository = str_of("repository");
        let channel = str_of("channel");
        let release_version = str_of("release_version");
        for (k, v) in [
            ("product", &product),
            ("repository", &repository),
            ("channel", &channel),
            ("release_version", &release_version),
        ] {
            if v.is_empty() {
                return Err(GovError::new(
                    "SRR_METADATA_MALFORMED",
                    format!("{}: release metadata does not bind '{k}'", env.source),
                ));
            }
        }
        let payload = s.get("payload").cloned().unwrap_or(serde_json::Value::Null);
        let payload_hash = payload
            .get("payload_hash")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        let kernel_manifest_hash = payload
            .get("kernel_manifest_hash")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        if payload_hash.is_empty() || kernel_manifest_hash.is_empty() {
            return Err(GovError::new(
                "SRR_METADATA_MALFORMED",
                format!(
                    "{}: release metadata does not bind payload_hash and kernel_manifest_hash",
                    env.source
                ),
            ));
        }
        let mut files = BTreeMap::new();
        for (path, f) in payload
            .get("files")
            .and_then(|v| v.as_object())
            .cloned()
            .unwrap_or_default()
        {
            let sha = f
                .get("sha256")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            if sha.is_empty() {
                return Err(GovError::new(
                    "SRR_METADATA_MALFORMED",
                    format!("{}: payload file '{path}' has no sha256", env.source),
                ));
            }
            files.insert(
                path.clone(),
                PayloadFile {
                    path,
                    sha256: sha,
                    length: f.get("length").and_then(|v| v.as_u64()),
                },
            );
        }
        if files.is_empty() {
            return Err(GovError::new(
                "SRR_METADATA_MALFORMED",
                format!("{}: release metadata binds no payload files", env.source),
            ));
        }
        let migrations = s
            .get("migrations")
            .and_then(|v| v.as_array())
            .map(|a| {
                a.iter()
                    .map(|m| MigrationIdentity {
                        id: m
                            .get("id")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                        from_version: m
                            .get("from_version")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                        to_version: m
                            .get("to_version")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                        sha256: m
                            .get("sha256")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                    })
                    .collect()
            })
            .unwrap_or_default();
        let delegations = s
            .get("delegations")
            .and_then(|v| v.as_array())
            .map(|a| {
                a.iter()
                    .map(|d| Delegation {
                        name: d
                            .get("name")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                        keyids: d
                            .get("keyids")
                            .and_then(|v| v.as_array())
                            .map(|x| {
                                x.iter()
                                    .filter_map(|k| k.as_str().map(String::from))
                                    .collect()
                            })
                            .unwrap_or_default(),
                        threshold: d.get("threshold").and_then(|v| v.as_u64()).unwrap_or(0)
                            as usize,
                        paths: d
                            .get("paths")
                            .and_then(|v| v.as_array())
                            .map(|x| {
                                x.iter()
                                    .filter_map(|k| k.as_str().map(String::from))
                                    .collect()
                            })
                            .unwrap_or_default(),
                        channel: d.get("channel").and_then(|v| v.as_str()).map(String::from),
                    })
                    .collect()
            })
            .unwrap_or_default();
        Ok(Release {
            product,
            repository,
            channel,
            release_version,
            sequence: s.get("sequence").and_then(|v| v.as_u64()).unwrap_or(0),
            version: env.version(),
            expires: env.expires().to_string(),
            platforms: s
                .get("platforms")
                .and_then(|v| v.as_array())
                .map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(String::from))
                        .collect()
                })
                .unwrap_or_default(),
            minimum_secure_release: str_of("minimum_secure_release"),
            minimum_secure_sequence: s
                .get("minimum_secure_sequence")
                .and_then(|v| v.as_u64())
                .unwrap_or(0),
            payload_hash,
            kernel_manifest_hash,
            files,
            migrations,
            schema_identities: s
                .get("schema_identities")
                .cloned()
                .unwrap_or(serde_json::Value::Null),
            delegations,
            evidence: s
                .get("evidence")
                .cloned()
                .unwrap_or(serde_json::Value::Null),
            envelope: env,
        })
    }
}

// ---------------------------------------------------------------------------------------- snapshot / timestamp

#[derive(Debug, Clone)]
pub struct MetaRef {
    pub version: u64,
    pub sha256: String,
}

#[derive(Debug, Clone)]
pub struct Snapshot {
    pub envelope: Envelope,
    pub version: u64,
    pub meta: BTreeMap<String, MetaRef>,
}

#[derive(Debug, Clone)]
pub struct Timestamp {
    pub envelope: Envelope,
    pub version: u64,
    pub meta: BTreeMap<String, MetaRef>,
}

fn parse_meta(env: &Envelope) -> Result<BTreeMap<String, MetaRef>> {
    let mut out = BTreeMap::new();
    let obj = env
        .signed
        .get("meta")
        .and_then(|v| v.as_object())
        .ok_or_else(|| {
            GovError::new(
                "SRR_METADATA_MALFORMED",
                format!("{}: meta map missing", env.source),
            )
        })?;
    for (name, m) in obj {
        out.insert(
            name.clone(),
            MetaRef {
                version: m.get("version").and_then(|v| v.as_u64()).unwrap_or(0),
                sha256: m
                    .get("sha256")
                    .and_then(|v| v.as_str())
                    .unwrap_or("")
                    .to_string(),
            },
        );
    }
    Ok(out)
}

impl Snapshot {
    pub fn parse(env: Envelope) -> Result<Snapshot> {
        require_type(&env, ROLE_SNAPSHOT)?;
        require_spec(&env)?;
        Ok(Snapshot {
            version: env.version(),
            meta: parse_meta(&env)?,
            envelope: env,
        })
    }
}

impl Timestamp {
    pub fn parse(env: Envelope) -> Result<Timestamp> {
        require_type(&env, ROLE_TIMESTAMP)?;
        require_spec(&env)?;
        Ok(Timestamp {
            version: env.version(),
            meta: parse_meta(&env)?,
            envelope: env,
        })
    }
}

// ---------------------------------------------------------------------------------- break-glass authorisation

/// A single-use, owner-signed below-floor recovery authorisation (OWNER-DECISION-0006 §2).
///
/// It is signed by the `recovery` role held **offline by the product owner**, so it cannot be manufactured by
/// repository content, environment variables, caller fields, plugins or model output, and a below-floor or revoked
/// binary cannot issue one to itself. Verification is entirely local: no network or code-hosting access is
/// consulted (OWNER-DECISION-0006 §10).
#[derive(Debug, Clone)]
pub struct BreakGlassToken {
    pub envelope: Envelope,
    pub product: String,
    pub machine_id: String,
    pub nonce: String,
    pub reason: String,
    pub issued: String,
    pub expires: String,
    /// `SRR2-R1-C2` — the authorisation binds the payload digests of the recovery release, not its version alone.
    pub recovery_payload_hash: String,
    pub recovery_kernel_manifest_hash: String,
    pub recovery_release_version: String,
}

impl BreakGlassToken {
    pub fn parse(env: Envelope) -> Result<BreakGlassToken> {
        require_type(&env, "break-glass")?;
        require_spec(&env)?;
        let s = &env.signed;
        let g = |k: &str| s.get(k).and_then(|v| v.as_str()).unwrap_or("").to_string();
        let rec = s
            .get("recovery_release")
            .cloned()
            .unwrap_or(serde_json::Value::Null);
        let gr = |k: &str| {
            rec.get(k)
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string()
        };
        let t = BreakGlassToken {
            product: g("product"),
            machine_id: g("machine_id"),
            nonce: g("nonce"),
            reason: g("reason"),
            issued: g("issued"),
            expires: env.expires().to_string(),
            recovery_payload_hash: gr("payload_hash"),
            recovery_kernel_manifest_hash: gr("kernel_manifest_hash"),
            recovery_release_version: gr("release_version"),
            envelope: env,
        };
        for (k, v) in [
            ("product", &t.product),
            ("machine_id", &t.machine_id),
            ("nonce", &t.nonce),
            ("reason", &t.reason),
        ] {
            if v.is_empty() {
                return Err(GovError::new(
                    "SRR_BREAK_GLASS_MALFORMED",
                    format!(
                        "{}: break-glass authorisation does not bind '{k}'",
                        t.envelope.source
                    ),
                ));
            }
        }
        // SRR2-R1-C2: a token that names only a version is refused.
        if t.recovery_payload_hash.is_empty() && t.recovery_kernel_manifest_hash.is_empty() {
            return Err(GovError::new(
                "SRR_BREAK_GLASS_MALFORMED",
                format!(
                    "{}: break-glass authorisation must bind recovery_release.payload_hash or .kernel_manifest_hash (SRR2-R1-C2: binding the release version alone is not sufficient)",
                    t.envelope.source
                ),
            ));
        }
        Ok(t)
    }
}

/// The local clock reading used for every freshness decision, in one place so the declared assumption
/// (ARCH-0003 §1) has exactly one implementation site.
pub fn local_clock_now() -> String {
    now_iso()
}

#[cfg(test)]
mod tests {
    use super::*;

    /// `AR27-N1` — the lexicographic comparison's precondition is checked, not assumed, and every way of failing
    /// it is expired.
    #[test]
    fn expiry_fails_closed_on_absent_and_non_canonical_forms() {
        let now = "2026-09-17T12:00:00Z";

        // The emitted form still behaves correctly in both directions.
        assert!(expiry_fault("2026-09-17T11:59:59Z", now).is_some(), "past UTC is expired");
        assert!(expiry_fault("2026-09-17T12:00:00Z", now).is_some(), "equal instant is expired");
        assert!(expiry_fault("2026-09-17T12:00:01Z", now).is_none(), "future UTC is not expired");

        // A +14:00 offset: 2026-09-16T23:00:00Z, thirteen hours in the PAST, yet it sorts after `now`.
        assert!(expiry_fault("2026-09-17T13:00:00+14:00", now).is_some());
        // A -12:00 offset that is genuinely in the future is refused too: the form, not the instant, is gated.
        assert!(expiry_fault("2026-09-18T00:00:00-12:00", now).is_some());
        // RFC-3339 permits lowercase `t`/`z`; this profile does not emit them.
        assert!(expiry_fault("2026-09-17t11:59:59z", now).is_some());
        assert!(expiry_fault("2099-01-01T00:00:00+00:00", now).is_some());
        // Fractional seconds, other precisions, and outright junk.
        assert!(expiry_fault("2026-09-17T12:00:00.500Z", now).is_some());
        assert!(expiry_fault("2099-01-01T00:00Z", now).is_some());
        assert!(expiry_fault("not a timestamp", now).is_some());
        // No `expires` member at all is expired, not immortal.
        assert!(expiry_fault("", now).is_some());
        // An uncomparable clock reading refuses rather than silently ordering against it.
        assert!(expiry_fault("2099-01-01T00:00:00Z", "17/09/2026").is_some());
    }

    #[test]
    fn canonical_utc_timestamp_accepts_exactly_what_now_iso_emits() {
        assert!(is_canonical_utc_timestamp(&crate::util::now_iso()));
        assert!(is_canonical_utc_timestamp(&local_clock_now()));
        assert!(is_canonical_utc_timestamp("2099-01-01T00:00:00Z"));
        for bad in [
            "",
            "2099-01-01T00:00:00z",
            "2099-01-01t00:00:00Z",
            "2099-01-01 00:00:00Z",
            "2099-01-01T00:00:00",
            "2099-01-01T00:00:00+00:00",
            "20990101T000000Z",
            "99-01-01T00:00:00Z",
            "2099-01-01T00:00:00Z ",
        ] {
            assert!(!is_canonical_utc_timestamp(bad), "'{bad}' must not be canonical");
        }
    }
}
