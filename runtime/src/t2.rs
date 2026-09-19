//! # The T2 binding primitive (BC-P2-09) and its cross-machine continuity (P2-ADJ-0002)
//!
//! D-0007 classes "authoritative project state written by the OS" as **T2**: governed gate, decision and CIT
//! records, the plugin registry, ledgers. Rule 2: "registered", "approved", "human_approved", "authority" are facts
//! of T1/T2 only; a T4/T5/T6 field carrying such a name is a request, recorded and ignored. Those records are plain
//! repository files, so without a binding any process with repository write access could *write* the fact
//! (A0-E1-02, A0-L3-02, A0-F4-02). This module is the binding: a T2 fact is honoured only when the bytes of the
//! record are exactly what a `gov` operation wrote.
//!
//! ## Mechanism
//!
//! When an OS operation writes a T2 record it calls [`seal_record`] (or [`seal_value`]). The seal is an
//! HMAC-SHA256 over the record's canonical content, the operation name and the time, stored in the record itself
//! (field [`SEAL_FIELD`]) so it travels with the record and needs no sidecar store. The key comes from protected
//! machine state, outside every repository, in one of two scopes:
//!
//! | scope | key | alg | honoured on |
//! |---|---|---|---|
//! | **provisioned** (P2-ADJ-0002) | an owner-authorised **T2 binding authority**: a 32-byte HMAC key the administrator installs on each of the owner's provisioned machines, together with the owner's signed authorisation of that key under the trusted root's `t2-binding` role | [`SEAL_ALG_PORTABLE`] | every machine that holds the same authority **and** whose trusted Signed Release Root authorises it — i.e. every machine provisioned for the owner/project, after a Git clone or pull |
//! | **machine** (round 1) | this machine's own binding key (`<state_root>/t2-binding/key.json`, created on first use, mode 0600) | [`SEAL_ALG`] | this machine only |
//!
//! A new seal uses the provisioned scope whenever this machine holds a binding authority that its trusted root
//! currently authorises and that has not expired ([`binding_status`] says which, and why); otherwise the machine
//! scope, exactly as before (an unprovisioned machine, or a provisioned one whose administrator has not installed an
//! authority, keeps working locally and its records are simply not portable). [`verify_record`] recomputes the
//! seal:
//!
//! | [`Binding`] | meaning | honoured? |
//! |---|---|---|
//! | `Verified` | written by a `gov` operation (on this machine, or under a binding authority this machine holds and its root authorises) and unmodified since; `scope` says which | yes |
//! | `Unsealed` | no seal: hand-written, legacy, or written by code that has not adopted the primitive | **no** |
//! | `Broken` | sealed, then modified (any field, including a single flag), or a malformed seal | **no** |
//! | `Foreign` | sealed with a key this machine does not hold: another machine's own key (an unprovisioned or unauthorised machine, a clone of a machine-scope record) or a binding authority this machine was not provisioned with (a foreign owner's machine) | **no** |
//! | `Unauthorised` | sealed under a binding authority this machine holds, but this machine's trusted root does not authorise it now (unprovisioned, the `t2-binding` role not delegated, the signing key revoked by root succession) | **no** |
//! | `KeyUnavailable` | this machine has no binding key / its state root cannot be resolved | **no** |
//!
//! Consumers never read a T2 field for a decision without first asking this module; everything that is not
//! `Verified` is reported, typed and refused ([`require_verified`], `T2_UNBOUND`).
//!
//! ## The binding authority (P2-ADJ-0002: T2 facts portable across the owner's provisioned machines)
//!
//! ARCH-0003 §8: additional machines are provisioned outside the project repository with the verifier, public root
//! metadata and protected machine/workload policy. The authority for a portable seal is delegated through that same
//! provisioned root, and nothing about it is in any repository:
//!
//! 1. **Delegation.** The owner's root delegates the role [`AUTHORITY_ROLE`] (`t2-binding`) to the owner's key(s)
//!    (root metadata; public).
//! 2. **Authorisation.** The owner, off the agents' machines, generates a 32-byte binding key and signs a
//!    [`AUTHORITY_TYPE`] document with the `t2-binding` key(s) at threshold, binding the product, the authority id
//!    ([`authority_id_of`]) and a commitment to the key ([`key_commitment_of`]), with `issued`/`expires`. `gov`
//!    verifies; it never signs (`SRR-R0-L4`).
//! 3. **Provisioning.** The administrator installs the [`BUNDLE_TYPE`] bundle (the signed authorisation and the key)
//!    on each of the owner's provisioned machines from the administrator domain: `gov trust t2-binding --provision
//!    <bundle>` ([`provision_authority`]). Refused unless the machine is provisioned, the authorisation verifies
//!    against *its* trusted root's `t2-binding` role at threshold, is unexpired, and the key matches the commitment;
//!    refused for a file inside a repository; refused below floor (`OWNER-DECISION-0006` §6 bullet 4). The key is
//!    kept in protected machine state (mode 0600), never in a repository.
//! 4. **Use.** A portable seal binds the authority id, the sealing machine's id, the operation, the time and the
//!    content. A verifying machine honours it only when it holds that authority's key (the MAC verifies) **and** its
//!    own trusted root authorises the authority at use time (the signature is re-verified against the current root,
//!    so a root successor that drops the `t2-binding` key revokes it). Expiry bounds when an authority may *seal*;
//!    records sealed while it was valid stay honoured, as owner-signed human answers do.
//!
//! ## What it proves, and what it does not (stated, not overclaimed)
//!
//! * A process that can write the repository but cannot read the machine's protected state cannot produce a
//!   `Verified` record — on any machine: hand-written gate answers, decisions and registry entries are detected
//!   (A0-E1-02's lower-role worker, A0-L3-02's record forgery). This is the attack in the findings.
//! * A record written by an unprovisioned machine, by a machine the owner's provisioning did not give the authority,
//!   or by a machine of another owner (another root, another authority) is `Foreign`/`Unauthorised` on the owner's
//!   machines: refused, typed and observable (P2-ADJ-0002).
//! * A process running with the **operator's full OS privileges** on a provisioned machine can read the binding key
//!   (same account) and could compute a seal. Against that attacker the primitive is detection-grade, not proof —
//!   and, because the requirement is that a record written on one provisioned machine is honoured on the others,
//!   what such a process forges on one of the owner's machines is honoured on the others holding the same authority
//!   (any mechanism meeting the requirement has that property). The facts that must hold against it — human answers
//!   and human-approval assertions — are additionally bound to an **owner signature** the machines do not hold
//!   ([`crate::human_channel`]). The key is symmetric and shared by the machines that hold it (`gov` never signs, so
//!   no per-machine signature is available): revocation is per authority (root succession, or a new authority and
//!   [`reseal`]), not per machine, unless the owner issues one authority per machine.
//! * A process can always *run `gov`* under a declared role; what it writes that way is an OS operation performed
//!   under that role's authority and is recorded as such (the agent-identity question is OD-P2-01, out of scope).
//!
//! ## API for other workstreams
//!
//! * writers of T2 state: [`seal_record`] / [`seal_value`] immediately before persisting; a writer that rewrites a
//!   record the OS already sealed re-seals it only when its seal verified before the write ([`seal_if_verified`]) —
//!   the OS never blesses content it did not write;
//! * consumers: [`verify_record`] / [`verify_value`] / [`verify_file`] and [`require_verified`];
//! * task close (G2 mutation scope): [`classify_path`] — a changed path under an OS-managed prefix is an OS write only
//!   when it is `Verified`; otherwise it is a worker mutation to be refused, not exempted ([`OS_MANAGED_PREFIXES`]
//!   names the OS-written locations this module knows of);
//! * suite / doctor: [`audit`] lists every open T2 record (and plugin-registry entry) that no OS operation produced;
//!   [`binding_status`] reports the sealing scope and the installed authorities.
use crate::records::{Record, RecordFormat, RecordStore};
use crate::srr::metadata::{Envelope, Root};
use crate::util::{canonical_json, now_iso, sha256_hex};
use crate::{GovError, Project, Result, FRAMEWORK_NAME};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

/// The field that carries the seal inside a sealed record or JSON document.
pub const SEAL_FIELD: &str = "os_binding";
/// Seal algorithm identifier of a **machine-scope** seal (bound into the MAC).
pub const SEAL_ALG: &str = "hmac-sha256/t2-v1";
/// Seal algorithm identifier of a **provisioned-scope** (portable) seal under a binding authority (P2-ADJ-0002).
pub const SEAL_ALG_PORTABLE: &str = "hmac-sha256/t2-v2";
/// The root-delegated role whose keys authorise a T2 binding authority.
pub const AUTHORITY_ROLE: &str = "t2-binding";
/// `_type` of the owner-signed authorisation of one binding key.
pub const AUTHORITY_TYPE: &str = "t2-binding-authority";
/// `_type` of the provisioning bundle the administrator installs (the signed authorisation and the key).
pub const BUNDLE_TYPE: &str = "t2-binding-provisioning";
/// Every binding-authority id starts with this prefix (a machine key id never does).
pub const AUTHORITY_ID_PREFIX: &str = "t2a-";
/// The administrator command that installs a binding authority on a provisioned machine.
pub const PROVISION_COMMAND: &str =
    "gov trust t2-binding --provision <bundle.json supplied from the administrator domain>";
const KEY_DIR: &str = "t2-binding";
const KEY_FILE: &str = "key.json";
const AUTHORITIES_DIR: &str = "authorities";
const AUTHORITY_FILE: &str = "authority.json";
const AUTHORITY_KEY_FILE: &str = "key.json";

/// Record types every instance of which is T2 state written only by OS operations (checked by [`audit`]).
///
/// `cit` joins this list once every CIT writer whole-record-seals (WS-5 r2 IP-R3-2, WS-4 round 3): until then an
/// unsealed CIT record is legacy state, and adding it here would make every CIT written without a seal a T2
/// violation at task close (`orchestration::tasks::sealed_kind`, `cit_record_honoured`).
pub const SEALED_RECORD_TYPES: &[&str] = &["human-gate"];

/// Repository locations only the OS writes, as this module knows them (BC-P2-31 adds `governance/registry/`, where the
/// OS-written plugin registry belongs — `paths::PLUGIN_REGISTRY_PATH`). The task-close mutation scope classifies a
/// change under one of them by its seal ([`classify_path`]), never by its location.
pub const OS_MANAGED_PREFIXES: &[&str] = &[
    "governance/generated/",
    "governance/registry/",
    "spec/reports/",
    "spec/audits/",
    "spec/planning/",
    "spec/decisions/HDG-",
    "spec/decisions/CIT-",
    "spec/decisions/D-",
    "spec/lessons/",
];

/// Outcome of verifying a T2 binding.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Binding {
    Verified {
        key_id: String,
        operation: String,
        at: String,
    },
    Unsealed,
    Broken {
        reason: String,
    },
    Foreign {
        key_id: String,
    },
    /// Sealed under a binding authority this machine holds but its trusted root does not authorise now.
    Unauthorised {
        key_id: String,
        reason: String,
    },
    KeyUnavailable {
        reason: String,
    },
}

/// `provisioned` for a key id of a binding authority, `machine` for a machine's own key.
pub fn scope_of_key(key_id: &str) -> &'static str {
    if key_id.starts_with(AUTHORITY_ID_PREFIX) {
        "provisioned"
    } else {
        "machine"
    }
}

impl Binding {
    pub fn is_verified(&self) -> bool {
        matches!(self, Binding::Verified { .. })
    }
    /// A verified binding that other provisioned machines holding the same authority also honour.
    pub fn is_portable(&self) -> bool {
        matches!(self, Binding::Verified { key_id, .. } if scope_of_key(key_id) == "provisioned")
    }
    pub fn code(&self) -> &'static str {
        match self {
            Binding::Verified { .. } => "VERIFIED",
            Binding::Unsealed => "UNSEALED",
            Binding::Broken { .. } => "BROKEN",
            Binding::Foreign { .. } => "FOREIGN",
            Binding::Unauthorised { .. } => "UNAUTHORISED",
            Binding::KeyUnavailable { .. } => "KEY_UNAVAILABLE",
        }
    }
    pub fn to_value(&self) -> Value {
        match self {
            Binding::Verified {
                key_id,
                operation,
                at,
            } => {
                json!({"binding": "VERIFIED", "key_id": key_id, "scope": scope_of_key(key_id), "operation": operation, "at": at})
            }
            Binding::Unsealed => {
                json!({"binding": "UNSEALED", "reason": "no OS seal: the record was not written by a gov operation (hand-written, legacy, or written by a writer that has not adopted the T2 primitive)"})
            }
            Binding::Broken { reason } => json!({"binding": "BROKEN", "reason": reason}),
            Binding::Foreign { key_id } if scope_of_key(key_id) == "provisioned" => {
                json!({"binding": "FOREIGN", "key_id": key_id, "scope": "provisioned", "reason": format!("sealed under T2 binding authority {key_id}, which this machine was not provisioned with (a machine of another owner or project, or a machine whose administrator has not installed that authority here); not verifiable on this machine")})
            }
            Binding::Foreign { key_id } => {
                json!({"binding": "FOREIGN", "key_id": key_id, "scope": "machine", "reason": "sealed with another machine's own binding key (a machine-scope seal: an unprovisioned machine, a machine without the owner's T2 binding authority, or a record sealed before the authority existed); not verifiable on this machine"})
            }
            Binding::Unauthorised { key_id, reason } => {
                json!({"binding": "UNAUTHORISED", "key_id": key_id, "scope": "provisioned", "reason": format!("sealed under T2 binding authority {key_id}, which this machine holds but its trusted root does not authorise now: {reason}")})
            }
            Binding::KeyUnavailable { reason } => {
                json!({"binding": "KEY_UNAVAILABLE", "reason": reason})
            }
        }
    }
}

// ------------------------------------------------------------------------------------------------- the machine key

struct BindingKey {
    key: Vec<u8>,
    id: String,
}

fn key_path() -> Result<PathBuf> {
    Ok(crate::srr::state::resolve_state_root()?
        .join(KEY_DIR)
        .join(KEY_FILE))
}

fn parse_key(v: &Value) -> Option<BindingKey> {
    let key = hex::decode(v["key_hex"].as_str()?).ok()?;
    if key.len() != 32 {
        return None;
    }
    let id = key_id_of(&key);
    Some(BindingKey { key, id })
}

fn key_id_of(key: &[u8]) -> String {
    sha256_hex(&[b"t2-binding-key-id:".as_slice(), key].concat())[..16].to_string()
}

fn load_key() -> Result<Option<BindingKey>> {
    let path = key_path()?;
    if !path.exists() {
        return Ok(None);
    }
    let v = crate::util::read_json(&path)?;
    parse_key(&v).map(Some).ok_or_else(|| {
        GovError::new(
            "T2_KEY_INVALID",
            format!("the machine binding key at {} is unreadable; T2 facts cannot be verified (restore it from the machine's backup, or re-issue gates on a fresh key)", path.display()),
        )
    })
}

/// Load the machine binding key, creating it on first use. Creation is race-free: the key is written to a private
/// temporary file and hard-linked into place, so of two concurrent creators exactly one key wins and both use it.
fn load_or_create_key() -> Result<BindingKey> {
    if let Some(k) = load_key()? {
        return Ok(k);
    }
    let path = key_path()?;
    let dir = path.parent().expect("key path has a parent").to_path_buf();
    std::fs::create_dir_all(&dir)
        .map_err(|e| GovError::io(&format!("mkdir {}", dir.display()), e))?;
    let mut key = uuid::Uuid::new_v4().as_bytes().to_vec();
    key.extend_from_slice(uuid::Uuid::new_v4().as_bytes());
    let doc = json!({
        "key_hex": hex::encode(&key),
        "key_id": key_id_of(&key),
        "created": now_iso(),
        "purpose": "T2 binding key (BC-P2-09): seals records written by gov operations on this machine. Keep it out of every repository; anyone who can read it can seal records as this machine.",
    });
    let tmp = dir.join(format!(
        ".key.{}.{}.tmp",
        std::process::id(),
        crate::util::short_uuid()
    ));
    crate::util::write_json(&tmp, &doc)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let _ = std::fs::set_permissions(&tmp, std::fs::Permissions::from_mode(0o600));
    }
    let linked = std::fs::hard_link(&tmp, &path);
    let _ = std::fs::remove_file(&tmp);
    if let Err(e) = linked {
        if !path.exists() {
            return Err(GovError::io(&format!("install {}", path.display()), e));
        }
    }
    load_key()?.ok_or_else(|| {
        GovError::new(
            "T2_KEY_INVALID",
            "the machine binding key vanished while it was being created",
        )
    })
}

/// The id of this machine's own (machine-scope) binding key, if one exists (never creates one).
pub fn binding_key_id() -> Option<String> {
    load_key().ok().flatten().map(|k| k.id)
}

// ------------------------------------------------------------------------------------------------ HMAC-SHA256

fn hmac_sha256(key: &[u8], msg: &[u8]) -> [u8; 32] {
    use sha2::{Digest, Sha256};
    let mut k = [0u8; 64];
    if key.len() > 64 {
        k[..32].copy_from_slice(&Sha256::digest(key));
    } else {
        k[..key.len()].copy_from_slice(key);
    }
    let mut ipad = [0x36u8; 64];
    let mut opad = [0x5cu8; 64];
    for i in 0..64 {
        ipad[i] ^= k[i];
        opad[i] ^= k[i];
    }
    let inner = Sha256::new()
        .chain_update(ipad)
        .chain_update(msg)
        .finalize();
    let outer = Sha256::new()
        .chain_update(opad)
        .chain_update(inner)
        .finalize();
    outer.into()
}

fn ct_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    a.iter().zip(b).fold(0u8, |acc, (x, y)| acc | (x ^ y)) == 0
}

// ------------------------------------------------------------------------------------------------ canonical form

/// The canonical content a seal covers: the record data **without** the seal field, taken through exactly the
/// product's YAML writer and back (so the seal survives `save_record` → `RecordStore::load` byte-for-value), then
/// canonical JSON; plus the Markdown body for front-matter records.
fn canonical_content(data: &Value, body: &str) -> Result<String> {
    let mut d = data.clone();
    if let Some(m) = d.as_object_mut() {
        m.remove(SEAL_FIELD);
    }
    let text = crate::util::to_yaml(&d)?;
    let rt: Value = serde_yaml::from_str(&text)?;
    Ok(format!("{}\n{}", canonical_json(&rt), body))
}

fn mac_message(key_id: &str, operation: &str, at: &str, content: &str) -> Vec<u8> {
    format!("{SEAL_ALG}\n{key_id}\n{operation}\n{at}\n{content}").into_bytes()
}

/// The MAC input of a portable seal: the authority, the sealing machine, the operation, the time and the content.
fn mac_message_portable(
    authority: &str,
    machine: &str,
    operation: &str,
    at: &str,
    content: &str,
) -> Vec<u8> {
    format!("{SEAL_ALG_PORTABLE}\n{authority}\n{machine}\n{operation}\n{at}\n{content}")
        .into_bytes()
}

// ------------------------------------------------------------------------------- binding authorities (P2-ADJ-0002)

/// The id of the binding authority whose key is `key` (derived from the key, never taken from a document).
pub fn authority_id_of(key: &[u8]) -> String {
    format!(
        "{AUTHORITY_ID_PREFIX}{}",
        &sha256_hex(&[b"t2-binding-authority-id:".as_slice(), key].concat())[..16]
    )
}

/// The commitment to a binding key that the owner's authorisation binds (SHA-256 over a domain-separated key).
pub fn key_commitment_of(key: &[u8]) -> String {
    sha256_hex(&[b"t2-binding-key-commitment:".as_slice(), key].concat())
}

/// What an owner-signed authorisation established.
#[derive(Debug, Clone)]
struct AuthorityDoc {
    issued: String,
    expires: String,
    owner: String,
    signed_by: Vec<String>,
    envelope_sha256: String,
}

fn str_of(v: &Value, k: &str) -> String {
    v.get(k).and_then(|x| x.as_str()).unwrap_or("").to_string()
}

/// Verify an owner-signed authorisation of `key` against `root`'s `t2-binding` role. `now = Some(clock)` also
/// refuses an expired authorisation (provisioning and sealing); `None` is use-time verification of an authority
/// that sealed while it was valid.
fn authorise(
    root: &Root,
    env_bytes: &[u8],
    key: &[u8],
    source: &str,
    now: Option<&str>,
) -> Result<AuthorityDoc> {
    let bad = |code: &str, m: String| GovError::new(code, format!("{source}: {m}"));
    let env = Envelope::parse(env_bytes, source)
        .map_err(|e| bad("T2_AUTHORITY_INVALID", format!("{}: {}", e.code, e.message)))?;
    if env.typ() != AUTHORITY_TYPE {
        return Err(bad(
            "T2_AUTHORITY_INVALID",
            format!("expected _type '{AUTHORITY_TYPE}', found '{}'", env.typ()),
        ));
    }
    if env.spec_version() != crate::srr::metadata::SPEC_VERSION {
        return Err(bad(
            "T2_AUTHORITY_INVALID",
            format!("unsupported spec_version '{}'", env.spec_version()),
        ));
    }
    if env.product() != FRAMEWORK_NAME {
        return Err(bad(
            "T2_AUTHORITY_INVALID",
            format!("binds product '{}', not '{FRAMEWORK_NAME}'", env.product()),
        ));
    }
    if !root.has_role(AUTHORITY_ROLE) {
        return Err(bad(
            "T2_AUTHORITY_ROLE_NOT_DELEGATED",
            format!("this machine's trusted Signed Release Root (version {}) delegates no `{AUTHORITY_ROLE}` role, so no T2 binding authority is authorised here", root.version),
        ));
    }
    let signed_by = root.verify_role(AUTHORITY_ROLE, &env).map_err(|e| {
        bad(
            "T2_AUTHORITY_UNAUTHORISED",
            format!(
                "not authorised by the `{AUTHORITY_ROLE}` role of this machine's trusted root (version {}): {}",
                root.version, e.message
            ),
        )
    })?;
    let s = &env.signed;
    if str_of(s, "authority_id") != authority_id_of(key)
        || str_of(s, "key_commitment") != key_commitment_of(key)
    {
        return Err(bad(
            "T2_AUTHORITY_KEY_MISMATCH",
            format!("the binding key does not match the key the owner authorised (authority_id '{}', key_commitment '{}'; this key derives {})", str_of(s, "authority_id"), str_of(s, "key_commitment"), authority_id_of(key)),
        ));
    }
    if let Some(now) = now {
        if let Some(f) = env.expiry_fault(now) {
            return Err(bad("T2_AUTHORITY_EXPIRED", f));
        }
    }
    Ok(AuthorityDoc {
        issued: str_of(s, "issued"),
        expires: env.expires().to_string(),
        owner: str_of(s, "owner"),
        signed_by,
        envelope_sha256: env.file_sha256.clone(),
    })
}

/// One binding authority installed in this machine's protected state.
#[derive(Debug, Clone)]
struct HeldAuthority {
    id: String,
    /// `None` when the key file is missing, unreadable, or does not derive the authority id.
    key: Option<Vec<u8>>,
    /// The owner's authorisation, verified against this machine's trusted root now (expiry not applied).
    doc: std::result::Result<AuthorityDoc, String>,
}

/// This machine's T2 binding authorities and the trust state they are judged against.
#[derive(Debug, Clone, Default)]
struct MachineAuthorities {
    state_root: Option<PathBuf>,
    unresolved: Option<String>,
    machine_id: String,
    provisioned: bool,
    provisioned_at: Option<String>,
    root_version: Option<u64>,
    root_problem: Option<String>,
    role_delegated: bool,
    held: Vec<HeldAuthority>,
}

impl MachineAuthorities {
    fn find(&self, id: &str) -> Option<&HeldAuthority> {
        self.held.iter().find(|h| h.id == id)
    }
    /// The authority new seals use: installed, key usable, authorised by the trusted root now, unexpired; the most
    /// recently issued one (then the smallest id) when several qualify.
    fn sealing(&self, now: &str) -> Option<(&HeldAuthority, &Vec<u8>)> {
        self.held
            .iter()
            .filter_map(|h| match (&h.key, &h.doc) {
                (Some(k), Ok(d))
                    if crate::srr::metadata::expiry_fault(&d.expires, now).is_none() =>
                {
                    Some((h, k, d.issued.clone()))
                }
                _ => None,
            })
            .max_by(|a, b| (a.2.as_str(), b.0.id.as_str()).cmp(&(b.2.as_str(), a.0.id.as_str())))
            .map(|(h, k, _)| (h, k))
    }
    /// Why no authority seals (for the status report).
    fn why_machine_scope(&self, now: &str) -> String {
        if let Some(u) = &self.unresolved {
            return format!("the protected machine state cannot be resolved ({u})");
        }
        if !self.provisioned {
            return "this machine is unprovisioned (no Signed Release Root): its seals are machine-scope and are not honoured on any other machine (P2-ADJ-0002; OWNER-DECISION-P2-0002)".into();
        }
        if let Some(r) = &self.root_problem {
            return format!("this machine's trusted root cannot be loaded ({r})");
        }
        if !self.role_delegated {
            return format!("this machine's trusted root delegates no `{AUTHORITY_ROLE}` role");
        }
        if self.held.is_empty() {
            return format!("no T2 binding authority is installed here ({PROVISION_COMMAND})");
        }
        let reasons: Vec<String> = self
            .held
            .iter()
            .map(|h| match (&h.key, &h.doc) {
                (None, _) => format!("{}: its key is unusable", h.id),
                (_, Err(e)) => format!("{}: {e}", h.id),
                (_, Ok(d)) => match crate::srr::metadata::expiry_fault(&d.expires, now) {
                    Some(f) => format!("{}: expired ({f})", h.id),
                    None => format!("{}: usable", h.id),
                },
            })
            .collect();
        format!(
            "no installed T2 binding authority may seal now: {}",
            reasons.join("; ")
        )
    }
}

fn authorities_dir(state_root: &Path) -> PathBuf {
    state_root.join(KEY_DIR).join(AUTHORITIES_DIR)
}

fn file_digest(p: &Path) -> String {
    std::fs::read(p)
        .map(|b| sha256_hex(&b))
        .unwrap_or_else(|_| "-".into())
}

fn authority_dirs(state_root: &Path) -> Vec<PathBuf> {
    let mut v: Vec<PathBuf> = std::fs::read_dir(authorities_dir(state_root))
        .map(|rd| {
            rd.filter_map(|e| e.ok())
                .map(|e| e.path())
                .filter(|p| p.is_dir())
                .collect()
        })
        .unwrap_or_default();
    v.sort();
    v
}

/// A digest of everything the authority set is derived from, so the per-process cache never serves a stale view.
fn fingerprint(state_root: &Path) -> String {
    let trust = state_root.join("trust");
    let mut parts = vec![
        state_root.display().to_string(),
        file_digest(&trust.join("provisioned.json")),
        file_digest(&trust.join("root.json")),
        file_digest(&state_root.join("machine.json")),
    ];
    for d in authority_dirs(state_root) {
        parts.push(d.display().to_string());
        parts.push(file_digest(&d.join(AUTHORITY_FILE)));
        parts.push(file_digest(&d.join(AUTHORITY_KEY_FILE)));
    }
    sha256_hex(parts.join("\n").as_bytes())
}

fn load_machine_authorities(state_root: &Path) -> MachineAuthorities {
    let ms = crate::srr::state::MachineState::read_only(state_root);
    let mut m = MachineAuthorities {
        state_root: Some(state_root.to_path_buf()),
        machine_id: ms.machine_id.clone(),
        provisioned: ms.is_provisioned(),
        ..Default::default()
    };
    m.provisioned_at = ms
        .provisioned_record()
        .get("provisioned_at")
        .and_then(|v| v.as_str())
        .map(String::from);
    let now = crate::srr::metadata::local_clock_now();
    let trusted: Option<Root> = if m.provisioned {
        match crate::srr::verifier::trusted_root(&ms, &now) {
            Ok(r) => r,
            Err(e) => {
                m.root_problem = Some(format!("{}: {}", e.code, e.message));
                None
            }
        }
    } else {
        None
    };
    if let Some(r) = &trusted {
        m.root_version = Some(r.version);
        m.role_delegated = r.has_role(AUTHORITY_ROLE);
    }
    for d in authority_dirs(state_root) {
        let id = d
            .file_name()
            .map(|f| f.to_string_lossy().to_string())
            .unwrap_or_default();
        let key = crate::util::read_json(&d.join(AUTHORITY_KEY_FILE))
            .ok()
            .and_then(|v| {
                v["key_hex"]
                    .as_str()
                    .and_then(|h| hex::decode(h.trim()).ok())
            })
            .filter(|k| k.len() == 32 && authority_id_of(k) == id);
        let doc = match (&key, std::fs::read(d.join(AUTHORITY_FILE))) {
            (None, _) => Err("the binding key file of this authority is missing, unreadable or does not derive its id".to_string()),
            (_, Err(e)) => Err(format!("the authority document is unreadable: {e}")),
            (Some(k), Ok(bytes)) => match &trusted {
                None if !m.provisioned => Err("this machine holds no Signed Release Root (unprovisioned), so no T2 binding authority is authorised here".to_string()),
                None => Err(format!("this machine's trusted root cannot be loaded ({})", m.root_problem.clone().unwrap_or_default())),
                Some(r) => authorise(r, &bytes, k, &d.join(AUTHORITY_FILE).display().to_string(), None)
                    .map_err(|e| format!("{}: {}", e.code, e.message)),
            },
        };
        m.held.push(HeldAuthority { id, key, doc });
    }
    m
}

static AUTHORITY_CACHE: Mutex<Option<(String, Arc<MachineAuthorities>)>> = Mutex::new(None);

/// This machine's binding authorities, read-only (nothing is created by asking), cached per process by a digest of
/// every input.
fn machine_authorities() -> Arc<MachineAuthorities> {
    let root = match crate::srr::state::resolve_state_root() {
        Ok(r) => r,
        Err(e) => {
            return Arc::new(MachineAuthorities {
                unresolved: Some(format!("{}: {}", e.code, e.message)),
                ..Default::default()
            })
        }
    };
    let fp = fingerprint(&root);
    if let Ok(g) = AUTHORITY_CACHE.lock() {
        if let Some((f, m)) = g.as_ref() {
            if *f == fp {
                return m.clone();
            }
        }
    }
    let m = Arc::new(load_machine_authorities(&root));
    if let Ok(mut g) = AUTHORITY_CACHE.lock() {
        *g = Some((fp, m.clone()));
    }
    m
}

// ------------------------------------------------------------------------------------------------ seal / verify

/// Seal `data` (a record's data or a JSON document) as written by the OS operation `operation`. Call it
/// immediately before persisting; any later modification of any field breaks the seal. The seal is portable
/// (provisioned scope) when this machine holds a usable binding authority, machine-scope otherwise.
pub fn seal_value(data: &mut Value, body: &str, operation: &str) -> Result<()> {
    let m = machine_authorities();
    let at = now_iso();
    if let Some((h, key)) = m.sealing(&at) {
        return seal_portable_at(&h.id, key, &m.machine_id, data, body, operation, &at);
    }
    let key = load_or_create_key()?;
    seal_local_at(&key, data, body, operation, &at)
}

fn require_object(data: &Value) -> Result<()> {
    if !data.is_object() {
        return Err(GovError::new(
            "USAGE",
            "only a JSON/YAML object can carry a T2 seal",
        ));
    }
    Ok(())
}

fn seal_local_at(
    key: &BindingKey,
    data: &mut Value,
    body: &str,
    operation: &str,
    at: &str,
) -> Result<()> {
    require_object(data)?;
    let content = canonical_content(data, body)?;
    let mac = hex::encode(hmac_sha256(
        &key.key,
        &mac_message(&key.id, operation, at, &content),
    ));
    data[SEAL_FIELD] =
        json!({"alg": SEAL_ALG, "key_id": key.id, "operation": operation, "at": at, "mac": mac});
    Ok(())
}

fn seal_portable_at(
    authority: &str,
    key: &[u8],
    machine: &str,
    data: &mut Value,
    body: &str,
    operation: &str,
    at: &str,
) -> Result<()> {
    require_object(data)?;
    let content = canonical_content(data, body)?;
    let mac = hex::encode(hmac_sha256(
        key,
        &mac_message_portable(authority, machine, operation, at, &content),
    ));
    data[SEAL_FIELD] = json!({"alg": SEAL_ALG_PORTABLE, "scope": "provisioned", "key_id": authority,
        "authority": authority, "machine": machine, "operation": operation, "at": at, "mac": mac});
    Ok(())
}

/// Seal a record as written by `operation` (see [`seal_value`]).
pub fn seal_record(rec: &mut Record, operation: &str) -> Result<()> {
    let body = record_body(rec).to_string();
    seal_value(&mut rec.data, &body, operation)
}

fn record_body(rec: &Record) -> &str {
    if rec.format == RecordFormat::Md {
        rec.body.as_str()
    } else {
        ""
    }
}

/// For an OS writer that rewrites a record it did not create: re-seal `rec` as written by `operation` **only when**
/// `was_verified` — the binding the record had immediately before this write. A record whose seal did not verify
/// (unsealed, edited, foreign) is written and left unsealed: the OS never blesses content it did not write.
/// Returns whether it sealed.
pub fn seal_if_verified(rec: &mut Record, was_verified: bool, operation: &str) -> Result<bool> {
    if was_verified {
        seal_record(rec, operation)?;
    }
    Ok(was_verified)
}

/// Verify the seal on `data` (see the table in the module documentation).
pub fn verify_value(data: &Value, body: &str) -> Binding {
    let Some(seal) = data.get(SEAL_FIELD).filter(|v| !v.is_null()) else {
        return Binding::Unsealed;
    };
    if seal.get("alg").and_then(|v| v.as_str()) == Some(SEAL_ALG_PORTABLE) {
        return verify_portable(&machine_authorities(), data, body);
    }
    match load_key() {
        Ok(Some(k)) => verify_with(&k, data, body),
        // this machine never sealed anything in the machine scope, so a machine-scope seal is another machine's
        Ok(None) => match seal.get("key_id").and_then(|v| v.as_str()) {
            Some(k)
                if !k.is_empty() && seal.get("alg").and_then(|v| v.as_str()) == Some(SEAL_ALG) =>
            {
                Binding::Foreign {
                    key_id: k.to_string(),
                }
            }
            _ => Binding::Broken {
                reason: "malformed seal".into(),
            },
        },
        Err(e) => Binding::KeyUnavailable {
            reason: format!("{}: {}", e.code, e.message),
        },
    }
}

fn verify_with(key: &BindingKey, data: &Value, body: &str) -> Binding {
    let Some(seal) = data.get(SEAL_FIELD).filter(|v| !v.is_null()) else {
        return Binding::Unsealed;
    };
    let field = |k: &str| {
        seal.get(k)
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string()
    };
    let (alg, key_id, operation, at, mac) = (
        field("alg"),
        field("key_id"),
        field("operation"),
        field("at"),
        field("mac"),
    );
    if alg != SEAL_ALG || key_id.is_empty() || mac.is_empty() {
        return Binding::Broken {
            reason: format!("malformed seal (alg '{alg}')"),
        };
    }
    if key.id != key_id {
        return Binding::Foreign { key_id };
    }
    let content = match canonical_content(data, body) {
        Ok(c) => c,
        Err(e) => {
            return Binding::Broken {
                reason: format!("canonical form: {}", e.message),
            }
        }
    };
    let want = hmac_sha256(&key.key, &mac_message(&key_id, &operation, &at, &content));
    let got = hex::decode(&mac).unwrap_or_default();
    if ct_eq(&want, &got) {
        Binding::Verified {
            key_id,
            operation,
            at,
        }
    } else {
        Binding::Broken {
            reason: format!(
                "the record was modified after the OS operation '{operation}' sealed it at {at}"
            ),
        }
    }
}

/// Verify a portable (provisioned-scope) seal against the authorities this machine holds.
fn verify_portable(m: &MachineAuthorities, data: &Value, body: &str) -> Binding {
    let seal = &data[SEAL_FIELD];
    let field = |k: &str| {
        seal.get(k)
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string()
    };
    let (authority, key_id, scope, machine, operation, at, mac) = (
        field("authority"),
        field("key_id"),
        field("scope"),
        field("machine"),
        field("operation"),
        field("at"),
        field("mac"),
    );
    if authority.is_empty()
        || mac.is_empty()
        || key_id != authority
        || scope != "provisioned"
        || !authority.starts_with(AUTHORITY_ID_PREFIX)
    {
        return Binding::Broken {
            reason: format!("malformed portable seal (authority '{authority}', key_id '{key_id}', scope '{scope}')"),
        };
    }
    if let Some(u) = &m.unresolved {
        return Binding::KeyUnavailable {
            reason: format!("the protected machine state cannot be resolved ({u})"),
        };
    }
    let Some(h) = m.find(&authority) else {
        return Binding::Foreign { key_id: authority };
    };
    let Some(key) = &h.key else {
        return Binding::KeyUnavailable {
            reason: format!("T2 binding authority {authority} is installed on this machine but its key is unusable; re-provision it ({PROVISION_COMMAND})"),
        };
    };
    let content = match canonical_content(data, body) {
        Ok(c) => c,
        Err(e) => {
            return Binding::Broken {
                reason: format!("canonical form: {}", e.message),
            }
        }
    };
    let want = hmac_sha256(
        key,
        &mac_message_portable(&authority, &machine, &operation, &at, &content),
    );
    let got = hex::decode(&mac).unwrap_or_default();
    if !ct_eq(&want, &got) {
        return Binding::Broken {
            reason: format!(
                "the record was modified after the OS operation '{operation}' sealed it at {at} (machine {machine}, authority {authority})"
            ),
        };
    }
    match &h.doc {
        Ok(_) => Binding::Verified {
            key_id: authority,
            operation,
            at,
        },
        Err(reason) => Binding::Unauthorised {
            key_id: authority,
            reason: reason.clone(),
        },
    }
}

/// Verify a record's seal.
pub fn verify_record(rec: &Record) -> Binding {
    verify_value(&rec.data, record_body(rec))
}

/// Verify the seal of a repository file (`.yaml`/`.yml`/`.md` governed record, or a `.json` document carrying a
/// top-level [`SEAL_FIELD`]). A file that cannot be parsed is `Broken`.
pub fn verify_file(root: &Path, rel: &str) -> Binding {
    let abs = root.join(rel);
    let Ok(text) = std::fs::read_to_string(&abs) else {
        return Binding::Broken {
            reason: format!("{rel} is unreadable"),
        };
    };
    if rel.ends_with(".json") {
        return match serde_json::from_str::<Value>(&text) {
            Ok(v) => verify_value(&v, ""),
            Err(e) => Binding::Broken {
                reason: format!("{rel}: {e}"),
            },
        };
    }
    match crate::records::parse_record_text(&text, rel) {
        Some(r) if r.problems.is_empty() => verify_record(&r),
        Some(r) => Binding::Broken {
            reason: r.problems.join("; "),
        },
        None => Binding::Unsealed,
    }
}

/// Refuse to honour `rec` unless its binding is `Verified`. `what` names the fact the caller wanted to honour.
pub fn require_verified(rec: &Record, what: &str) -> Result<()> {
    let b = verify_record(rec);
    if b.is_verified() {
        return Ok(());
    }
    Err(unbound(&rec.id(), &rec.path, what, &b))
}

/// The typed `T2_UNBOUND` refusal.
pub fn unbound(id: &str, path: &str, what: &str, b: &Binding) -> GovError {
    GovError::new(
        "T2_UNBOUND",
        format!(
            "{id} ({path}) cannot establish {what}: it is T2 state that no gov operation honoured on this machine produced as it stands (binding {}) — honoured are records sealed on this machine, or under a T2 binding authority this machine's provisioning authorises (P2-ADJ-0002). D-0007 rule 2: such a record is a request, recorded and ignored. Restore it from version control, or withdraw and re-raise it through gov.",
            b.code()
        ),
    )
    .with_details(json!({"record": id, "path": path, "fact": what, "t2": b.to_value()}))
}

/// Whether a changed repository path is an OS write (`Verified`) or not — for the G2 task-close mutation scope.
/// Only paths that carry a seal can be proven OS-written; everything else is the worker's mutation.
pub fn classify_path(root: &Path, rel: &str) -> Binding {
    if !root.join(rel).exists() {
        // a deletion cannot carry a seal: it is never provably an OS write
        return Binding::Broken {
            reason: format!("{rel} was deleted"),
        };
    }
    verify_file(root, rel)
}

/// Is `rel` a location only the OS writes (see [`OS_MANAGED_PREFIXES`])?
pub fn os_managed_location(rel: &str) -> bool {
    OS_MANAGED_PREFIXES.iter().any(|pre| rel.starts_with(pre))
}

/// Every T2 record in the project that no OS operation produced as it stands: all records of
/// [`SEALED_RECORD_TYPES`], every decision that asserts `human_approved: true` or derives from a gate, and every
/// entry of the OS-written plugin registry (and the registry document itself) whose seal does not verify here
/// (WS-2 r2 R3-11). For the governance suite and doctor (WS-2): each entry is a finding.
pub fn audit(p: &Project) -> Vec<Value> {
    let store = RecordStore::load(&p.root);
    let mut out = vec![];
    for r in &store.records {
        let t = r.rtype();
        let t2 = SEALED_RECORD_TYPES.contains(&t.as_str())
            || (t == "decision"
                && (r
                    .data
                    .get("human_approved")
                    .and_then(|v| v.as_bool())
                    .unwrap_or(false)
                    || r.list("derived_from").iter().any(|d| d.starts_with("HDG-"))));
        if !t2 {
            continue;
        }
        let b = verify_record(r);
        if !b.is_verified() {
            out.push(json!({"id": r.id(), "type": t, "path": r.path, "t2": b.to_value()}));
        }
    }
    let reg = crate::capabilities::registry::path(p);
    if reg.exists() {
        let rel = reg
            .strip_prefix(&p.root)
            .map(|r| r.to_string_lossy().replace('\\', "/"))
            .unwrap_or_else(|_| reg.display().to_string());
        let doc = crate::capabilities::registry::document_binding(p);
        if !doc.is_verified() {
            out.push(
                json!({"id": "plugin-registry", "type": "plugin-registry", "path": rel, "t2": doc.to_value()}),
            );
        }
        for (pid, b) in crate::capabilities::registry::unbound_entries(p) {
            out.push(json!({"id": format!("plugin-registration:{pid}"), "type": "plugin-registration", "path": rel, "plugin_id": pid, "t2": b.to_value()}));
        }
    }
    out
}

// ------------------------------------------------------------------------------------------------ status

/// `gov trust t2-binding`: which scope new seals take on this machine and why, the installed binding authorities
/// and whether this machine's trusted root authorises each now, and what a bundle must contain.
pub fn binding_status() -> Value {
    let m = machine_authorities();
    let now = now_iso();
    let sealing = m.sealing(&now);
    let authorities: Vec<Value> = m
        .held
        .iter()
        .map(|h| {
            let (authorised, reason, doc) = match &h.doc {
                Ok(d) => (true, Value::Null, Some(d)),
                Err(e) => (false, json!(e), None),
            };
            let expiry = doc.and_then(|d| crate::srr::metadata::expiry_fault(&d.expires, &now));
            json!({
                "authority_id": h.id,
                "key_usable": h.key.is_some(),
                "authorised_by_trusted_root": authorised,
                "unauthorised_reason": reason,
                "issued": doc.map(|d| d.issued.clone()),
                "expires": doc.map(|d| d.expires.clone()),
                "expired": expiry.is_some(),
                "owner": doc.map(|d| d.owner.clone()),
                "signed_by_key_ids": doc.map(|d| d.signed_by.clone()),
                "authority_sha256": doc.map(|d| d.envelope_sha256.clone()),
                "seals_new_records": sealing.map(|(s, _)| s.id == h.id).unwrap_or(false),
            })
        })
        .collect();
    json!({
        "state_root": m.state_root.as_ref().map(|p| p.display().to_string()),
        "machine_id": m.machine_id,
        "provisioned": m.provisioned,
        "trusted_root_version": m.root_version,
        "role": AUTHORITY_ROLE,
        "root_delegates_role": m.role_delegated,
        "portable": sealing.is_some(),
        "sealing": match sealing {
            Some((h, _)) => json!({"scope": "provisioned", "authority_id": h.id, "alg": SEAL_ALG_PORTABLE,
                "honoured_on": "every machine that holds this authority and whose trusted root authorises it (the owner's provisioned machines), after a Git clone or pull"}),
            None => json!({"scope": "machine", "machine_key_id": binding_key_id(), "alg": SEAL_ALG,
                "honoured_on": "this machine only", "reason": m.why_machine_scope(&now)}),
        },
        "authorities": authorities,
        "machine_key_id": binding_key_id(),
        "provision_command": PROVISION_COMMAND,
        "bundle_document": {
            "_type": BUNDLE_TYPE,
            "members": {"key_hex": "the 32-byte binding key, hex (secret: kept only in protected machine state, never in a repository)",
                        "authority": format!("the owner-signed `{AUTHORITY_TYPE}` envelope, verbatim")},
            "authority_binds": ["_type", "spec_version", "product", "authority_id", "key_commitment", "issued", "expires", "owner"],
            "authority_id": "t2a- + the first 16 hex of SHA-256(\"t2-binding-authority-id:\" || key)",
            "key_commitment": "SHA-256(\"t2-binding-key-commitment:\" || key), hex",
            "signature": format!("ed25519 over the exact bytes of the `signed` member, by the trusted root's `{AUTHORITY_ROLE}` role at threshold"),
        },
        "cannot_provide_authority": ["repository content (a bundle file inside a repository is refused)", "environment variables", "CLI flags", "a key the owner did not authorise under this machine's root", "another owner's root"],
        "premise": "ARCH-0003 §1/§8: the administrator boundary is uncompromised; the binding key is protected machine material installed from the administrator domain. A process with the operator's OS privileges can read it (detection-grade against that attacker; human answers stay owner-signed).",
    })
}

// ------------------------------------------------------------------------------------------------ provisioning

/// ARCH-0003 §5 / OWNER-DIRECTIVE-0004: trust material comes from the administrator installation boundary, never from
/// repository content (the rule `gov trust provision` applies to a Signed Release Root).
fn refuse_repository_sourced(file: &Path, project_root: Option<&Path>) -> Result<()> {
    let abs = file.canonicalize().unwrap_or_else(|_| file.to_path_buf());
    let refuse = |why: String| {
        GovError::new(
            "T2_AUTHORITY_FROM_REPOSITORY_REFUSED",
            format!("{} {why}. A T2 binding authority is protected machine material installed from the administrator domain, never repository content (ARCH-0003 §5/§8, OWNER-DIRECTIVE-0004); it carries a secret key that must never be committed.", abs.display()),
        )
        .with_details(json!({"bundle_file": abs.display().to_string()}))
    };
    if let Some(pr) = project_root {
        let pabs = pr.canonicalize().unwrap_or_else(|_| pr.to_path_buf());
        if crate::project::find_root(&pabs).is_some_and(|r| abs.starts_with(&r))
            || abs.starts_with(&pabs)
        {
            return Err(refuse(format!(
                "is inside the governed project at {}",
                pabs.display()
            )));
        }
    }
    for part in abs.components() {
        let s = part.as_os_str().to_string_lossy();
        if s == ".git" || s == "governance" {
            return Err(refuse("is repository-controlled content".into()));
        }
    }
    Ok(())
}

/// Write `bytes` to `path` atomically (temporary file, fsync, rename), with `mode` on unix.
fn write_private(path: &Path, bytes: &[u8], mode: u32) -> Result<()> {
    let dir = path.parent().expect("a file path has a parent");
    let tmp = dir.join(format!(
        ".{}.{}.{}.tmp",
        path.file_name()
            .map(|f| f.to_string_lossy().to_string())
            .unwrap_or_default(),
        std::process::id(),
        crate::util::short_uuid()
    ));
    {
        use std::io::Write;
        let mut f = std::fs::File::create(&tmp)
            .map_err(|e| GovError::io(&format!("create {}", tmp.display()), e))?;
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let _ = std::fs::set_permissions(&tmp, std::fs::Permissions::from_mode(mode));
        }
        f.write_all(bytes)
            .map_err(|e| GovError::io(&format!("write {}", tmp.display()), e))?;
        f.sync_all()
            .map_err(|e| GovError::io(&format!("fsync {}", tmp.display()), e))?;
    }
    let _ = mode;
    std::fs::rename(&tmp, path)
        .map_err(|e| GovError::io(&format!("install {}", path.display()), e))?;
    crate::srr::state::fsync_dir(dir);
    Ok(())
}

/// **Administrator action (P2-ADJ-0002)**: install the owner's T2 binding authority on this provisioned machine from
/// a [`BUNDLE_TYPE`] bundle supplied from the administrator domain.
///
/// Refused below floor (a trust-policy mutation: `OWNER-DECISION-0006` §6 bullet 4), for a bundle that is repository
/// content, on an unprovisioned machine (`T2_AUTHORITY_UNPROVISIONED`: provision first), and unless the owner's
/// authorisation verifies against **this machine's** trusted root's `t2-binding` role at threshold, is unexpired,
/// binds this product, and commits to exactly the supplied key. Installing the same bundle again changes nothing; a
/// newly signed authorisation of the same key (e.g. after the owner rotated the role's keys) replaces the stored
/// authorisation. The key is written with mode 0600 and is never printed.
pub fn provision_authority(bundle: &Path, project_root: Option<&Path>) -> Result<Value> {
    crate::srr::breakglass::guard_effect(
        crate::srr::breakglass::Effect::TrustPolicyMutation,
        "trust t2-binding provision",
    )?;
    refuse_repository_sourced(bundle, project_root)?;
    let ms = crate::srr::state::MachineState::open()?;
    let now = crate::srr::metadata::local_clock_now();
    let root = crate::srr::verifier::trusted_root(&ms, &now)?.ok_or_else(|| {
        GovError::new(
            "T2_AUTHORITY_UNPROVISIONED",
            "this machine holds no Signed Release Root, so no T2 binding authority can be authorised here (P2-ADJ-0002: only machines provisioned for the owner/project honour and write portable T2 facts). Remediation: provision the machine first (`gov trust provision --anchor <root.json>` from the administrator domain), with a root whose `t2-binding` role delegates the owner's key(s).",
        )
        .with_details(json!({"cause": "UNPROVISIONED", "provision_command": crate::human_channel::PROVISION_COMMAND}))
    })?;
    let bytes = std::fs::read(bundle)
        .map_err(|e| GovError::io(&format!("read {}", bundle.display()), e))?;
    #[derive(serde::Deserialize)]
    struct Bundle<'a> {
        #[serde(rename = "_type")]
        typ: String,
        key_hex: String,
        #[serde(borrow)]
        authority: &'a serde_json::value::RawValue,
    }
    let b: Bundle = serde_json::from_slice(&bytes).map_err(|e| {
        GovError::new(
            "T2_AUTHORITY_INVALID",
            format!(
                "{}: not a `{BUNDLE_TYPE}` bundle ({{_type, key_hex, authority}}): {e}",
                bundle.display()
            ),
        )
    })?;
    if b.typ != BUNDLE_TYPE {
        return Err(GovError::new(
            "T2_AUTHORITY_INVALID",
            format!(
                "{}: expected _type '{BUNDLE_TYPE}', found '{}'",
                bundle.display(),
                b.typ
            ),
        ));
    }
    let key = hex::decode(b.key_hex.trim())
        .ok()
        .filter(|k| k.len() == 32)
        .ok_or_else(|| {
            GovError::new(
                "T2_AUTHORITY_INVALID",
                format!(
                    "{}: key_hex must be 32 bytes, hex-encoded",
                    bundle.display()
                ),
            )
        })?;
    let env_bytes = b.authority.get().as_bytes().to_vec();
    let doc = authorise(
        &root,
        &env_bytes,
        &key,
        &bundle.display().to_string(),
        Some(&now),
    )?;
    let id = authority_id_of(&key);
    let dir = authorities_dir(&ms.root).join(&id);
    let existing = std::fs::read(dir.join(AUTHORITY_FILE)).ok();
    let action = match &existing {
        Some(e) if *e == env_bytes => "unchanged",
        Some(_) => "authorisation replaced (the same key, newly authorised)",
        None => "installed",
    };
    std::fs::create_dir_all(&dir)
        .map_err(|e| GovError::io(&format!("mkdir {}", dir.display()), e))?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let _ = std::fs::set_permissions(&dir, std::fs::Permissions::from_mode(0o700));
    }
    let key_doc = json!({"authority_id": id, "key_hex": hex::encode(&key), "installed_at": now_iso(),
        "purpose": "T2 binding authority key (P2-ADJ-0002): seals records portable across the owner's provisioned machines. Protected machine material: keep it out of every repository."});
    let key_file = dir.join(AUTHORITY_KEY_FILE);
    let key_ok = crate::util::read_json(&key_file)
        .ok()
        .and_then(|v| v["key_hex"].as_str().map(|h| h.trim().to_lowercase()))
        == Some(hex::encode(&key));
    if !key_ok {
        write_private(
            &key_file,
            (serde_json::to_string_pretty(&key_doc)? + "\n").as_bytes(),
            0o600,
        )?;
    }
    if action != "unchanged" {
        write_private(&dir.join(AUTHORITY_FILE), &env_bytes, 0o644)?;
    }
    if let Ok(mut g) = AUTHORITY_CACHE.lock() {
        *g = None;
    }
    let status = binding_status();
    Ok(json!({
        "provisioned": true,
        "action": action,
        "authority_id": id,
        "issued": doc.issued,
        "expires": doc.expires,
        "owner": doc.owner,
        "signed_by_key_ids": doc.signed_by,
        "trusted_root_version": root.version,
        "role": AUTHORITY_ROLE,
        "machine_id": ms.machine_id,
        "sealing": status["sealing"],
        "note": "Records sealed under this authority are honoured on every machine provisioned with it and authorised by its trusted root (P2-ADJ-0002). The key never leaves protected machine state; nothing was written to any repository.",
    }))
}

// ------------------------------------------------------------------------------------------------ reseal

/// One seal-bearing object's standing before a reseal pass.
fn local_seal_at(data: &Value) -> Option<String> {
    let s = data.get(SEAL_FIELD)?;
    if s.get("alg").and_then(|v| v.as_str()) != Some(SEAL_ALG) {
        return None;
    }
    s.get("at").and_then(|v| v.as_str()).map(String::from)
}

/// Re-seal, inside `v` (bottom-up), every object whose machine-scope seal verifies here and was made at or after
/// `since` under the portable authority, keeping its recorded operation and time; an enclosing sealed object whose
/// content changed is re-sealed in the scope it already had. Returns the number of seals rewritten.
/// A seal's standing judged against exactly this machine's keys (the machine key and the held authorities).
fn verify_in(m: &MachineAuthorities, local: &BindingKey, v: &Value, body: &str) -> Binding {
    if v[SEAL_FIELD].get("alg").and_then(|a| a.as_str()) == Some(SEAL_ALG_PORTABLE) {
        verify_portable(m, v, body)
    } else {
        verify_with(local, v, body)
    }
}

#[allow(clippy::too_many_arguments)]
fn reseal_tree(
    v: &mut Value,
    body: &str,
    m: &MachineAuthorities,
    local: &BindingKey,
    authority: (&str, &[u8]),
    machine: &str,
    since: &str,
) -> Result<usize> {
    let Some(obj) = v.as_object() else {
        if let Some(a) = v.as_array_mut() {
            let mut n = 0;
            for x in a.iter_mut() {
                n += reseal_tree(x, "", m, local, authority, machine, since)?;
            }
            return Ok(n);
        }
        return Ok(0);
    };
    // this object's standing, judged before anything inside it changes
    let before = obj
        .get(SEAL_FIELD)
        .filter(|s| !s.is_null())
        .map(|_| verify_in(m, local, v, body));
    let local_at = local_seal_at(v);
    let mut n = 0;
    if let Some(o) = v.as_object_mut() {
        for (k, x) in o.iter_mut() {
            if k != SEAL_FIELD {
                n += reseal_tree(x, "", m, local, authority, machine, since)?;
            }
        }
    }
    let Some(b) = before else { return Ok(n) };
    if !b.is_verified() {
        return Ok(n);
    }
    let op = str_of(&v[SEAL_FIELD], "operation");
    let at = str_of(&v[SEAL_FIELD], "at");
    let eligible = local_at.as_deref().is_some_and(|a| a >= since);
    if eligible {
        seal_portable_at(authority.0, authority.1, machine, v, body, &op, &at)?;
        return Ok(n + 1);
    }
    if n > 0 {
        // content inside changed: keep this object verifiable in the scope it already had
        if b.is_portable() {
            let original_machine = str_of(&v[SEAL_FIELD], "machine");
            seal_portable_at(
                authority.0,
                authority.1,
                &original_machine,
                v,
                body,
                &op,
                &at,
            )?;
        } else {
            seal_local_at(local, v, body, &op, &at)?;
        }
        return Ok(n + 1);
    }
    Ok(n)
}

/// `gov trust t2-binding --reseal [--dry-run]` — continuity for records sealed on this machine before it held the
/// owner's binding authority (P2-ADJ-0002). Every tracked governed record or document under `spec/` and
/// `governance/` (the kernel excluded) whose **machine-scope** seal verifies here and was made **while this machine
/// was provisioned** is re-sealed under the portable authority, keeping the operation and time the OS recorded; a
/// record sealed while the machine was unprovisioned, or one whose seal does not verify, is left as it is (the OS
/// never blesses content it did not write, and an unprovisioned machine's records stay machine-scope).
pub fn reseal(p: &Project, dry_run: bool) -> Result<Value> {
    if !dry_run {
        crate::orchestration::control::guard_write(p, "trust t2-binding --reseal")?;
        crate::authority::require(p, "reseal_t2_bindings")?;
    }
    let m = machine_authorities();
    let at = now_iso();
    let Some((h, key)) = m.sealing(&at) else {
        return Err(GovError::new(
            "T2_AUTHORITY_UNAVAILABLE",
            format!(
                "no T2 binding authority may seal on this machine: {}",
                m.why_machine_scope(&at)
            ),
        )
        .with_details(json!({"provision_command": PROVISION_COMMAND})));
    };
    let since = m.provisioned_at.clone().ok_or_else(|| {
        GovError::new(
            "T2_AUTHORITY_UNAVAILABLE",
            "this machine's provisioning time is not recorded, so records sealed while it was unprovisioned cannot be told apart; nothing was resealed",
        )
    })?;
    let Some(local) = load_key()? else {
        return Ok(
            json!({"resealed_files": [], "resealed_seals": 0, "note": "this machine holds no machine-scope key: nothing was sealed here before the authority"}),
        );
    };
    let mut files: Vec<Value> = vec![];
    let mut total = 0usize;
    for (abs, rel) in crate::paths::iter_repo_files(&p.root, false) {
        let in_scope = (rel.starts_with("spec/") || rel.starts_with("governance/"))
            && !rel.starts_with("governance/kernel/")
            && (rel.ends_with(".yaml")
                || rel.ends_with(".yml")
                || rel.ends_with(".md")
                || rel.ends_with(".json"));
        if !in_scope {
            continue;
        }
        let Ok(text) = std::fs::read_to_string(&abs) else {
            continue;
        };
        if !text.contains(SEAL_FIELD) {
            continue;
        }
        let auth = (h.id.as_str(), key.as_slice());
        if rel.ends_with(".json") {
            let Ok(mut v) = serde_json::from_str::<Value>(&text) else {
                continue;
            };
            let n = reseal_tree(&mut v, "", &m, &local, auth, &m.machine_id, &since)?;
            if n > 0 {
                if !dry_run {
                    crate::util::write_json(&abs, &v)?;
                }
                total += n;
                files.push(json!({"path": rel, "seals": n}));
            }
            continue;
        }
        if let Some(mut r) = crate::records::parse_record_text(&text, &rel)
            .filter(|r| r.problems.is_empty() && !r.id().is_empty())
        {
            let body = record_body(&r).to_string();
            let n = reseal_tree(&mut r.data, &body, &m, &local, auth, &m.machine_id, &since)?;
            if n > 0 {
                if !dry_run {
                    crate::records::save_record(&p.root, &r)?;
                }
                total += n;
                files.push(json!({"path": rel, "seals": n}));
            }
            continue;
        }
        if rel.ends_with(".md") {
            continue;
        }
        let Ok(mut v) = serde_yaml::from_str::<Value>(&text) else {
            continue;
        };
        let n = reseal_tree(&mut v, "", &m, &local, auth, &m.machine_id, &since)?;
        if n > 0 {
            if !dry_run {
                crate::util::write_yaml(&abs, &v)?;
            }
            total += n;
            files.push(json!({"path": rel, "seals": n}));
        }
    }
    Ok(json!({
        "dry_run": dry_run,
        "authority_id": h.id,
        "machine_id": m.machine_id,
        "provisioned_at": since,
        "resealed_seals": total,
        "resealed_files": files,
        "rule": "only machine-scope seals that verify on this machine and were made while it was provisioned are resealed, keeping the operation and time the OS recorded; records sealed while unprovisioned, and records whose seal does not verify, are left as they are",
    }))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hmac_matches_rfc4231_test_cases() {
        // RFC 4231 test case 1
        let k = [0x0bu8; 20];
        assert_eq!(
            hex::encode(hmac_sha256(&k, b"Hi There")),
            "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"
        );
        // test case 2
        assert_eq!(
            hex::encode(hmac_sha256(b"Jefe", b"what do ya want for nothing?")),
            "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
        );
        // test case 6 (key longer than the block)
        let k = [0xaau8; 131];
        assert_eq!(
            hex::encode(hmac_sha256(
                &k,
                b"Test Using Larger Than Block-Size Key - Hash Key First"
            )),
            "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54"
        );
    }

    fn test_key(b: u8) -> BindingKey {
        let key = vec![b; 32];
        let id = key_id_of(&key);
        BindingKey { key, id }
    }

    #[test]
    fn a_seal_survives_the_product_writer_and_breaks_on_any_edit() {
        let key = test_key(7);
        let root = std::env::temp_dir().join(format!("gov-t2-proj-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(root.join("spec/decisions")).unwrap();
        let mut rec = crate::records::new_record(
            "decision",
            "D-0042",
            "t",
            json!({"question": "q?", "chosen_option": "A", "human_approved": false, "confidence": 0.7,
                   "approved_at": "2026-09-19T10:00:00Z", "created_day": "2026-09-19", "nested": {"x": [1, 2.5, "3"]},
                   "multi": "line one\nline two\n", "yes_word": "yes", "num_str": "1.0", "empty": ""}),
        );
        assert_eq!(verify_with(&key, &rec.data, ""), Binding::Unsealed);
        seal_local_at(&key, &mut rec.data, "", "gate answer", &now_iso()).unwrap();
        crate::records::save_record(&root, &rec).unwrap();
        let loaded = RecordStore::load(&root).get("D-0042").cloned().unwrap();
        assert!(
            verify_with(&key, &loaded.data, "").is_verified(),
            "{:?}",
            verify_with(&key, &loaded.data, "")
        );
        // flip one field by hand, as a worker with repository access would
        let text = std::fs::read_to_string(root.join(&loaded.path)).unwrap();
        std::fs::write(
            root.join(&loaded.path),
            text.replace("human_approved: false", "human_approved: true"),
        )
        .unwrap();
        let forged = RecordStore::load(&root).get("D-0042").cloned().unwrap();
        assert!(matches!(
            verify_with(&key, &forged.data, ""),
            Binding::Broken { .. }
        ));
        // a seal made with another machine's key is foreign, not verified
        assert!(matches!(
            verify_with(&test_key(9), &loaded.data, ""),
            Binding::Foreign { .. }
        ));
        // the recorded operation and time are bound: editing them breaks the seal
        let mut op_edit = loaded.clone();
        op_edit.data[SEAL_FIELD]["operation"] = json!("gate create");
        assert!(matches!(
            verify_with(&key, &op_edit.data, ""),
            Binding::Broken { .. }
        ));
        let _ = std::fs::remove_dir_all(&root);
    }

    fn held(id_key: &[u8], authorised: bool) -> HeldAuthority {
        HeldAuthority {
            id: authority_id_of(id_key),
            key: Some(id_key.to_vec()),
            doc: if authorised {
                Ok(AuthorityDoc {
                    issued: "2026-09-19T00:00:00Z".into(),
                    expires: "2099-01-01T00:00:00Z".into(),
                    owner: "test".into(),
                    signed_by: vec![],
                    envelope_sha256: String::new(),
                })
            } else {
                Err("T2_AUTHORITY_UNAUTHORISED: revoked (test)".into())
            },
        }
    }

    /// P2-ADJ-0002: a portable seal verifies on any machine holding the same authorised binding authority, binds the
    /// sealing machine, the operation, the time and the content, and is refused (typed) everywhere else.
    #[test]
    fn a_portable_seal_is_honoured_where_the_authority_is_held_and_authorised_and_nowhere_else() {
        let owner_key = [0x42u8; 32];
        let aid = authority_id_of(&owner_key);
        assert!(
            aid.starts_with(AUTHORITY_ID_PREFIX) && aid.len() == AUTHORITY_ID_PREFIX.len() + 16
        );
        assert_eq!(key_commitment_of(&owner_key).len(), 64);
        assert_ne!(authority_id_of(&[0x43u8; 32]), aid);
        let mut data = json!({"id": "HDG-0001", "type": "human-gate", "gate_status": "ANSWERED", "question": "q?"});
        seal_portable_at(
            &aid,
            &owner_key,
            "machine-A",
            &mut data,
            "",
            "gate answer",
            "2026-09-19T01:02:03Z",
        )
        .unwrap();
        let machine_b = MachineAuthorities {
            provisioned: true,
            held: vec![held(&owner_key, true)],
            ..Default::default()
        };
        let b = verify_portable(&machine_b, &data, "");
        assert!(b.is_verified() && b.is_portable(), "{b:?}");
        assert_eq!(b.to_value()["scope"], "provisioned");
        // a machine that was not given the authority (unprovisioned, unauthorised by the provisioning, another owner)
        let other = MachineAuthorities {
            provisioned: true,
            held: vec![held(&[0x43u8; 32], true)],
            ..Default::default()
        };
        assert!(matches!(
            verify_portable(&other, &data, ""),
            Binding::Foreign { .. }
        ));
        assert!(matches!(
            verify_portable(&MachineAuthorities::default(), &data, ""),
            Binding::Foreign { .. }
        ));
        // the authority is held but no longer authorised by this machine's trusted root (revoked by succession)
        let revoked = MachineAuthorities {
            provisioned: true,
            held: vec![held(&owner_key, false)],
            ..Default::default()
        };
        let u = verify_portable(&revoked, &data, "");
        assert_eq!(u.code(), "UNAUTHORISED", "{u:?}");
        assert!(!u.is_verified());
        // any edit — a field, the sealing machine, the operation, the time, the authority name — breaks it
        for (path, val) in [
            ("gate_status", json!("PENDING")),
            ("question", json!("q2?")),
        ] {
            let mut e = data.clone();
            e[path] = val;
            assert_eq!(verify_portable(&machine_b, &e, "").code(), "BROKEN");
        }
        for (k, val) in [
            ("machine", "machine-X"),
            ("operation", "gate create"),
            ("at", "2026-09-19T01:02:04Z"),
        ] {
            let mut e = data.clone();
            e[SEAL_FIELD][k] = json!(val);
            assert_eq!(verify_portable(&machine_b, &e, "").code(), "BROKEN", "{k}");
        }
        let mut e = data.clone();
        e[SEAL_FIELD]["key_id"] = json!("t2a-0000000000000000");
        assert_eq!(verify_portable(&machine_b, &e, "").code(), "BROKEN");
        let mut e = data.clone();
        e[SEAL_FIELD]["scope"] = json!("machine");
        assert_eq!(verify_portable(&machine_b, &e, "").code(), "BROKEN");
        // a key the authority id is not derived from is never used (the key file is refused at load)
        let mut forged_key = held(&owner_key, true);
        forged_key.key = None;
        let bad = MachineAuthorities {
            provisioned: true,
            held: vec![forged_key],
            ..Default::default()
        };
        assert_eq!(verify_portable(&bad, &data, "").code(), "KEY_UNAVAILABLE");
    }

    #[test]
    fn the_sealing_authority_is_authorised_unexpired_and_the_latest_issued() {
        let now = "2026-09-19T12:00:00Z";
        let mut a = held(&[1u8; 32], true);
        let mut b = held(&[2u8; 32], true);
        if let Ok(d) = &mut b.doc {
            d.issued = "2026-09-19T06:00:00Z".into();
        }
        let m = MachineAuthorities {
            provisioned: true,
            role_delegated: true,
            held: vec![a.clone(), b.clone()],
            ..Default::default()
        };
        assert_eq!(m.sealing(now).unwrap().0.id, b.id);
        if let Ok(d) = &mut b.doc {
            d.expires = "2026-09-19T11:00:00Z".into();
        }
        let m = MachineAuthorities {
            provisioned: true,
            role_delegated: true,
            held: vec![a.clone(), b.clone()],
            ..Default::default()
        };
        assert_eq!(m.sealing(now).unwrap().0.id, a.id);
        a.doc = Err("revoked".into());
        let m = MachineAuthorities {
            provisioned: true,
            role_delegated: true,
            held: vec![a, b],
            ..Default::default()
        };
        assert!(m.sealing(now).is_none());
        assert!(
            m.why_machine_scope(now).contains("expired"),
            "{}",
            m.why_machine_scope(now)
        );
        let unprov = MachineAuthorities::default();
        assert!(unprov.why_machine_scope(now).contains("unprovisioned"));
    }

    /// Reseal moves only seals this machine made while provisioned, keeps their operation and time, and keeps an
    /// enclosing seal valid when content inside it changed.
    #[test]
    fn reseal_moves_only_post_provisioning_local_seals_and_keeps_enclosing_seals_valid() {
        let local = test_key(5);
        let akey = [0x77u8; 32];
        let aid = authority_id_of(&akey);
        let mut early = json!({"id": "D-0001", "v": 1});
        seal_local_at(
            &local,
            &mut early,
            "",
            "gate answer",
            "2026-09-01T00:00:00Z",
        )
        .unwrap();
        let mut entry = json!({"plugin_id": "p", "v": 2});
        seal_local_at(
            &local,
            &mut entry,
            "",
            "plugins register",
            "2026-09-19T00:00:00Z",
        )
        .unwrap();
        let mut doc = json!({"plugins": {"p": entry}, "early": early});
        seal_local_at(
            &local,
            &mut doc,
            "",
            "plugins register",
            "2026-09-19T00:00:01Z",
        )
        .unwrap();
        let m = MachineAuthorities {
            provisioned: true,
            held: vec![held(&akey, true)],
            ..Default::default()
        };
        let n = reseal_tree(
            &mut doc,
            "",
            &m,
            &local,
            (&aid, &akey),
            "m1",
            "2026-09-10T00:00:00Z",
        )
        .unwrap();
        assert_eq!(n, 2, "{doc}");
        let inner = &doc["plugins"]["p"];
        let b = verify_portable(&m, inner, "");
        assert!(b.is_portable(), "{b:?}");
        assert_eq!(inner[SEAL_FIELD]["operation"], "plugins register");
        assert_eq!(inner[SEAL_FIELD]["at"], "2026-09-19T00:00:00Z");
        assert!(verify_portable(&m, &doc, "").is_portable());
        // sealed before provisioning: left machine-scope, still verifying locally
        assert_eq!(doc["early"][SEAL_FIELD]["alg"], SEAL_ALG);
        assert!(verify_with(&local, &doc["early"], "").is_verified());
        // an edited (unverified) object is never blessed
        let mut forged = json!({"id": "D-0002"});
        seal_local_at(
            &local,
            &mut forged,
            "",
            "gate answer",
            "2026-09-19T00:00:00Z",
        )
        .unwrap();
        forged["id"] = json!("D-0003");
        assert_eq!(
            reseal_tree(
                &mut forged,
                "",
                &m,
                &local,
                (&aid, &akey),
                "m1",
                "2026-09-10T00:00:00Z"
            )
            .unwrap(),
            0
        );
        assert_eq!(forged[SEAL_FIELD]["alg"], SEAL_ALG);
    }
}
