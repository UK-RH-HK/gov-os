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
//! | **provisioned** (P2-ADJ-0002) | the active key of the owner's **T2 binding authority** (`crate::srr::binding`): an owner-signed, versioned `t2-binding-authority` document under the trusted root's `t2-binding` role authorises binding keys by id and commitment; the administrator installs the document and a key with `gov trust bind` | [`SEAL_ALG_PORTABLE`] | every machine that holds that key and whose trusted root authorises it under the current authority — i.e. every machine provisioned and bound for the owner/project, after a Git clone or pull |
//! | **machine** (round 1) | this machine's own binding key (`<state_root>/t2-binding/key.json`, created on first use, mode 0600) | [`SEAL_ALG`] | this machine only, and only while it is not bound to the owner's authority |
//!
//! A new seal uses the provisioned scope whenever this machine's binding authority verifies now
//! (`crate::srr::binding::keyring`: re-verified against the current trusted root, unexpired, this machine
//! authorised) and the machine holds the authority's active key; otherwise the machine scope, exactly as before (an
//! unprovisioned machine, or a provisioned one whose administrator has not bound it, keeps working locally and its
//! records are simply not portable). [`verify_record`] recomputes the seal:
//!
//! | [`Binding`] | meaning | honoured? |
//! |---|---|---|
//! | `Verified` | written by a `gov` operation and unmodified since: under a key the owner's current authority authorises (`ACTIVE` or `RETIRED`) that this machine holds, or — on a machine not bound to the owner's authority — with this machine's own key; `scope` says which | yes |
//! | `Unsealed` | no seal: hand-written, legacy, or written by code that has not adopted the primitive | **no** |
//! | `Broken` | sealed, then modified (any field, including a single flag), or a malformed seal | **no** |
//! | `Foreign` | sealed with a key this machine does not hold: another machine's own key (an unprovisioned or unauthorised machine, a clone of a machine-scope record) or a binding key this machine was not given (another owner's authority) | **no** |
//! | `Unauthorised` | sealed with a key this machine holds but does not honour now: a binding key the current authority no longer lists (revoked), any binding key while the authority does not verify (root succession dropped the `t2-binding` delegation, expired, altered), or this machine's own key once the machine is bound (its own machine-scope records are not owner facts) | **no** |
//! | `KeyUnavailable` | this machine has no binding key / its state root cannot be resolved | **no** |
//!
//! Consumers never read a T2 field for a decision without first asking this module; everything that is not
//! `Verified` is reported, typed and refused ([`require_verified`], `T2_UNBOUND`).
//!
//! ## The binding authority (P2-ADJ-0002: T2 facts portable across the owner's provisioned machines)
//!
//! ARCH-0003 §8: additional machines are provisioned outside the project repository with the verifier, public root
//! metadata and protected machine/workload policy. The authority for a portable seal is delegated through that same
//! provisioned root, and nothing about it is in any repository. **There is one mechanism** (round-3 integration,
//! P2-AR-0041): one delegated role, one authority document format, one provisioning command and one keyring, all in
//! `crate::srr::binding`; this module only seals and verifies through `crate::srr::binding::keyring`.
//!
//! 1. **Delegation.** The owner's root delegates the role [`AUTHORITY_ROLE`] (`t2-binding`) to the owner's key(s)
//!    (root metadata; public).
//! 2. **Authorisation.** The owner, off the agents' machines, generates 32-byte binding keys and signs a versioned
//!    `t2-binding-authority` document with the `t2-binding` key(s) at threshold: the authority id, a version (never
//!    lowered on a machine), an expiry, optionally the machine ids it authorises, and its keys — each by key id
//!    (`crate::srr::binding::key_id_of`) and commitment (`crate::srr::binding::commitment_of`), exactly one `active`,
//!    any number `retired`. `gov` verifies; it never signs (`SRR-R0-L4`).
//! 3. **Provisioning.** The administrator installs the document and a key it authorises on each of the owner's
//!    provisioned machines from the administrator domain: [`PROVISION_COMMAND`]. Refused below floor, from a
//!    repository, via the environment, on an unprovisioned machine, under a root that does not delegate the role,
//!    below threshold or by another signer, expired, older than (or conflicting with) the version this machine
//!    accepted, for an unlisted machine, and for a key the document does not authorise by id and commitment.
//! 4. **Use.** A portable seal binds the authority id, the key id, the sealing machine's id, the operation, the time
//!    and the content. A verifying machine honours it only when it holds that key (the MAC verifies) **and** its own
//!    binding authority verifies now and authorises the key (`ACTIVE` or `RETIRED`). Rotation keeps the retired
//!    key's seals honoured; a key the current version no longer lists is revoked; root succession that drops the
//!    delegation, and expiry, stop every seal of the authority being honoured until the administrator binds a valid
//!    one (and new seals fall back to the machine scope).
//! 5. **Continuity.** A bound machine honours only owner facts. Records it sealed with its own key while it was
//!    provisioned are re-sealed under the active key by [`reseal`] (`gov trust reseal`), keeping the recorded
//!    operation and time; nothing sealed while it was unprovisioned, and nothing whose seal does not verify, is ever
//!    re-sealed.
//!
//! ## What it proves, and what it does not (stated, not overclaimed)
//!
//! * A process that can write the repository but cannot read the machine's protected state cannot produce a
//!   `Verified` record — on any machine: hand-written gate answers, decisions and registry entries are detected
//!   (A0-E1-02's lower-role worker, A0-L3-02's record forgery). This is the attack in the findings.
//! * A record written by an unprovisioned machine, by a machine the owner's provisioning did not bind, or by a
//!   machine of another owner (another root, another authority) is `Foreign`/`Unauthorised` on the owner's machines:
//!   refused, typed and observable (P2-ADJ-0002).
//! * A process running with the **operator's full OS privileges** on a provisioned machine can read the binding key
//!   (same account) and could compute a seal. Against that attacker the primitive is detection-grade, not proof —
//!   and, because the requirement is that a record written on one provisioned machine is honoured on the others,
//!   what such a process forges on one of the owner's machines is honoured on the others holding the same key
//!   (any mechanism meeting the requirement has that property). The facts that must hold against it — human answers
//!   and human-approval assertions — are additionally bound to an **owner signature** the machines do not hold
//!   ([`crate::human_channel`]). The key is symmetric and shared by the machines that hold it (`gov` never signs, so
//!   no per-machine signature is available): revocation is per key (a new authority version), not per machine,
//!   unless the owner issues machine-listed authorities.
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
//!   [`binding_status`] is the one report of the sealing scope and the owner's binding authority.
use crate::records::{Record, RecordFormat, RecordStore};
use crate::srr::binding::{HeldKey, Keyring};
use crate::util::{canonical_json, now_iso, sha256_hex};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

/// The field that carries the seal inside a sealed record or JSON document.
pub const SEAL_FIELD: &str = "os_binding";
/// Seal algorithm identifier of a **machine-scope** seal (bound into the MAC).
pub const SEAL_ALG: &str = "hmac-sha256/t2-v1";
/// Seal algorithm identifier of a **provisioned-scope** (portable) seal under the owner's binding authority
/// (P2-ADJ-0002).
pub const SEAL_ALG_PORTABLE: &str = "hmac-sha256/t2-v2";
/// The root-delegated role whose keys authorise the owner's T2 binding authority (`crate::srr::binding::ROLE`).
pub const AUTHORITY_ROLE: &str = crate::srr::binding::ROLE;
/// The one administrator command that installs (or rotates) the owner's binding authority on a provisioned machine.
pub const PROVISION_COMMAND: &str =
    "gov trust bind --authority <owner-signed t2-binding-authority> --key <binding key>, both from the administrator domain";
/// The continuity command: re-seal what this machine sealed while provisioned under the owner's active key.
pub const RESEAL_COMMAND: &str = "gov trust reseal [--dry-run]";
const KEY_DIR: &str = "t2-binding";
const KEY_FILE: &str = "key.json";

/// Record types every instance of which is T2 state written only by OS operations (checked by [`audit`], and by
/// task close through `orchestration::tasks::sealed_kind`).
///
/// `cit` (round-3 integration, WS-5 r2 IP-R3-2 / IP-R3-WS03-2): every CIT writer whole-record-seals (WS-4 round 3,
/// `cit::binding::seal`), and the gate operations that rewrite a CIT record re-seal it when it verified before (WS-3
/// round 3, IP-R3-WS04-01) — so an unsealed CIT record is no OS write, and it covers nothing at close
/// (`orchestration::tasks::cit_record_honoured`).
///
/// `task` (round-3 integration, WS-5 r2 IP-R3-1, final step): every OS writer of a task record seals a record it
/// creates and re-seals one it rewrites when it verified before (`tasks::save_task`, `dag::replan`,
/// `readiness::plan`, `generation`, `verification::lineage::remediate`; `gates` and `cit::propagation` since round 3),
/// so a hand-written or seal-stripped task record is refused at a concurrent close. Records of these kinds that were
/// unsealed before the claim began (legacy) are reported, not refused (`tasks::LEGACY_SEALED_KINDS`).
pub const SEALED_RECORD_TYPES: &[&str] = &["human-gate", "cit", "task"];

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
///
/// `key_id` names the key a seal was made with: a machine key's id (16 hex) for a machine-scope seal, and
/// `<authority_id>/<key_id>` for a seal under the owner's binding authority ([`scope_of_key`]).
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
    /// Sealed with a key this machine holds but does not honour now (see the module table).
    Unauthorised {
        key_id: String,
        reason: String,
    },
    KeyUnavailable {
        reason: String,
    },
}

/// `provisioned` for a key named under the owner's binding authority (`<authority_id>/<key_id>`), `machine` for a
/// machine's own key (16 hex, never containing `/`).
pub fn scope_of_key(key_id: &str) -> &'static str {
    if key_id.contains('/') {
        "provisioned"
    } else {
        "machine"
    }
}

/// The name a [`Binding`] gives a key of the owner's binding authority.
pub fn owner_key_name(authority_id: &str, key_id: &str) -> String {
    format!("{authority_id}/{key_id}")
}

impl Binding {
    pub fn is_verified(&self) -> bool {
        matches!(self, Binding::Verified { .. })
    }
    /// A verified binding that other provisioned machines bound to the same authority also honour.
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
                json!({"binding": "FOREIGN", "key_id": key_id, "scope": "provisioned", "reason": format!("sealed under binding key {key_id}, which this machine does not hold (a machine of another owner or project, or a machine whose administrator has not bound it to that authority); not verifiable on this machine")})
            }
            Binding::Foreign { key_id } => {
                json!({"binding": "FOREIGN", "key_id": key_id, "scope": "machine", "reason": "sealed with another machine's own binding key (a machine-scope seal: an unprovisioned machine, a machine the owner's provisioning did not bind, or a record sealed before its machine was bound); not verifiable on this machine"})
            }
            Binding::Unauthorised { key_id, reason } if scope_of_key(key_id) == "provisioned" => {
                json!({"binding": "UNAUTHORISED", "key_id": key_id, "scope": "provisioned", "reason": format!("sealed under binding key {key_id}, which this machine holds but its owner's binding authority does not authorise now: {reason}")})
            }
            Binding::Unauthorised { key_id, reason } => {
                json!({"binding": "UNAUTHORISED", "key_id": key_id, "scope": "machine", "reason": reason})
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

/// The MAC input of a portable seal: the authority, the key, the sealing machine, the operation, the time and the
/// content.
fn mac_message_portable(
    authority: &str,
    key_id: &str,
    machine: &str,
    operation: &str,
    at: &str,
    content: &str,
) -> Vec<u8> {
    format!("{SEAL_ALG_PORTABLE}\n{authority}\n{key_id}\n{machine}\n{operation}\n{at}\n{content}")
        .into_bytes()
}

// ------------------------------------------------------------------ the owner's binding authority (P2-ADJ-0002)

/// This machine's standing under the owner's T2 binding authority, as `crate::srr::binding::keyring` establishes it
/// (the one keyring API), plus the key material installed by `gov trust bind`.
#[derive(Debug, Clone)]
struct MachineView {
    state_root: Option<PathBuf>,
    unresolved: Option<String>,
    machine_id: String,
    provisioned: bool,
    provisioned_at: Option<String>,
    /// `Ok(None)`: no authority installed; `Ok(Some)`: it verified against the current trusted root when loaded;
    /// `Err((code, message))`: installed but not honoured.
    keyring: std::result::Result<Option<Keyring>, (String, String)>,
    /// Every binding key installed here, whatever its standing (for the MAC check before the standing check).
    held: Vec<HeldKey>,
}

impl Default for MachineView {
    fn default() -> Self {
        MachineView {
            state_root: None,
            unresolved: None,
            machine_id: String::new(),
            provisioned: false,
            provisioned_at: None,
            keyring: Ok(None),
            held: vec![],
        }
    }
}

impl MachineView {
    /// The authority, when it verifies **now** (the load verified it; expiry is re-checked at `now` because the view
    /// is cached per process).
    fn valid(&self, now: &str) -> std::result::Result<Option<&Keyring>, String> {
        match &self.keyring {
            Ok(None) => Ok(None),
            Ok(Some(k)) => match crate::srr::metadata::expiry_fault(&k.authority.expires, now) {
                Some(f) => Err(format!(
                    "T2_BINDING_AUTHORITY_EXPIRED: binding authority '{}' version {} is not current: {f}",
                    k.authority.authority_id, k.authority.version
                )),
                None => Ok(Some(k)),
            },
            Err((code, msg)) => Err(format!("{code}: {msg}")),
        }
    }
    /// Owner mode: the authority verifies now and this machine holds its active key — new seals are portable and
    /// only owner facts are honoured.
    fn sealing(&self, now: &str) -> Option<(&Keyring, &HeldKey)> {
        let k = self.valid(now).ok().flatten()?;
        k.active().map(|a| (k, a))
    }
    fn held(&self, key_id: &str) -> Option<&HeldKey> {
        self.held.iter().find(|h| h.key_id == key_id)
    }
    /// Why new seals are machine-scope (for the status report).
    fn why_machine_scope(&self, now: &str) -> String {
        if let Some(u) = &self.unresolved {
            return format!("the protected machine state cannot be resolved ({u})");
        }
        if !self.provisioned {
            return "this machine is unprovisioned (no Signed Release Root): its seals are machine-scope and are not honoured on any other machine (P2-ADJ-0002; OWNER-DECISION-P2-0002)".into();
        }
        match self.valid(now) {
            Ok(None) => format!(
                "no T2 binding authority is installed here: administrator: {PROVISION_COMMAND}"
            ),
            Err(e) => format!("the installed T2 binding authority is not honoured now ({e})"),
            Ok(Some(k)) => format!(
                "this machine does not hold the active key {} of binding authority '{}' version {}: administrator: {PROVISION_COMMAND}",
                k.authority.active().map(|a| a.key_id.as_str()).unwrap_or("?"),
                k.authority.authority_id,
                k.authority.version
            ),
        }
    }
}

/// A digest of everything the view is derived from, so the per-process cache never serves a stale view.
///
/// The trust anchor itself is not read here (only `srr::state` composes its path and `srr::verifier` reads it — the R1
/// census holds that): the provisioning record, which `MachineState::set_root_metadata` rewrites with the anchor's
/// digest and version on every provisioning and root succession, stands for it.
fn fingerprint(state_root: &Path) -> String {
    let ms = crate::srr::state::MachineState::read_only(state_root);
    sha256_hex(
        [
            state_root.display().to_string(),
            canonical_json(&ms.provisioned_record()),
            ms.machine_id.clone(),
            crate::srr::binding::state_fingerprint(state_root),
        ]
        .join("\n")
        .as_bytes(),
    )
}

fn load_view(state_root: &Path) -> MachineView {
    let ms = crate::srr::state::MachineState::read_only(state_root);
    MachineView {
        state_root: Some(state_root.to_path_buf()),
        unresolved: None,
        machine_id: ms.machine_id.clone(),
        provisioned: ms.is_provisioned(),
        provisioned_at: ms
            .provisioned_record()
            .get("provisioned_at")
            .and_then(|v| v.as_str())
            .map(String::from),
        keyring: crate::srr::binding::keyring_at(state_root).map_err(|e| (e.code, e.message)),
        held: crate::srr::binding::held_keys(state_root),
    }
}

static VIEW_CACHE: Mutex<Option<(String, Arc<MachineView>)>> = Mutex::new(None);

/// This machine's view of the owner's binding authority, read-only (nothing is created by asking), cached per
/// process by a digest of every input.
fn machine_view() -> Arc<MachineView> {
    let root = match crate::srr::state::resolve_state_root() {
        Ok(r) => r,
        Err(e) => {
            return Arc::new(MachineView {
                unresolved: Some(format!("{}: {}", e.code, e.message)),
                ..Default::default()
            })
        }
    };
    let fp = fingerprint(&root);
    if let Ok(g) = VIEW_CACHE.lock() {
        if let Some((f, m)) = g.as_ref() {
            if *f == fp {
                return m.clone();
            }
        }
    }
    let m = Arc::new(load_view(&root));
    if let Ok(mut g) = VIEW_CACHE.lock() {
        *g = Some((fp, m.clone()));
    }
    m
}

// ------------------------------------------------------------------------------------------------ seal / verify

/// Seal `data` (a record's data or a JSON document) as written by the OS operation `operation`. Call it
/// immediately before persisting; any later modification of any field breaks the seal. The seal is portable
/// (provisioned scope) when this machine is bound to the owner's authority and holds its active key, machine-scope
/// otherwise.
pub fn seal_value(data: &mut Value, body: &str, operation: &str) -> Result<()> {
    let v = machine_view();
    let at = now_iso();
    if let Some((k, active)) = v.sealing(&at) {
        return seal_portable_at(
            &k.authority.authority_id,
            &active.key_id,
            &active.key,
            &v.machine_id,
            data,
            body,
            operation,
            &at,
        );
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

#[allow(clippy::too_many_arguments)]
fn seal_portable_at(
    authority: &str,
    key_id: &str,
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
        &mac_message_portable(authority, key_id, machine, operation, at, &content),
    ));
    data[SEAL_FIELD] = json!({"alg": SEAL_ALG_PORTABLE, "scope": "provisioned", "authority": authority,
        "key_id": key_id, "machine": machine, "operation": operation, "at": at, "mac": mac});
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
    let v = machine_view();
    if let Some(u) = &v.unresolved {
        return Binding::KeyUnavailable {
            reason: format!("the protected machine state cannot be resolved ({u})"),
        };
    }
    if seal.get("alg").and_then(|a| a.as_str()) == Some(SEAL_ALG_PORTABLE) {
        return verify_portable(&v, data, body);
    }
    verify_machine_scope(&v, data, body)
}

/// The standing of an authentic seal made with the held binding key `key_id`, under this machine's authority now.
fn owner_standing(
    v: &MachineView,
    key_id: &str,
    name: String,
    operation: String,
    at: String,
) -> Binding {
    let now = now_iso();
    match v.valid(&now) {
        Ok(Some(k)) => match k.standing(key_id) {
            Some(_) => Binding::Verified {
                key_id: name,
                operation,
                at,
            },
            None => Binding::Unauthorised {
                key_id: name,
                reason: format!(
                    "binding authority '{}' version {} does not list key {key_id} (revoked by the owner)",
                    k.authority.authority_id, k.authority.version
                ),
            },
        },
        Ok(None) => Binding::Unauthorised {
            key_id: name,
            reason: "no binding authority is installed on this machine to authorise the key".into(),
        },
        Err(reason) => Binding::Unauthorised {
            key_id: name,
            reason,
        },
    }
}

/// Verify a portable (provisioned-scope) seal against the binding keys this machine holds and its authority now.
fn verify_portable(v: &MachineView, data: &Value, body: &str) -> Binding {
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
        || key_id.is_empty()
        || key_id.contains('/')
        || mac.is_empty()
        || scope != "provisioned"
    {
        return Binding::Broken {
            reason: format!("malformed portable seal (authority '{authority}', key_id '{key_id}', scope '{scope}')"),
        };
    }
    let name = owner_key_name(&authority, &key_id);
    let Some(h) = v.held(&key_id) else {
        return Binding::Foreign { key_id: name };
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
        &h.key,
        &mac_message_portable(&authority, &key_id, &machine, &operation, &at, &content),
    );
    let got = hex::decode(&mac).unwrap_or_default();
    if !ct_eq(&want, &got) {
        return Binding::Broken {
            reason: format!(
                "the record was modified after the OS operation '{operation}' sealed it at {at} (machine {machine}, authority {authority}, key {key_id})"
            ),
        };
    }
    owner_standing(v, &key_id, name, operation, at)
}

/// Verify a machine-scope seal: under a binding key the owner's authority adopted, or this machine's own key.
fn verify_machine_scope(v: &MachineView, data: &Value, body: &str) -> Binding {
    let seal = &data[SEAL_FIELD];
    let field = |k: &str| {
        seal.get(k)
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string()
    };
    let (alg, key_id) = (field("alg"), field("key_id"));
    if alg != SEAL_ALG || key_id.is_empty() || field("mac").is_empty() {
        return Binding::Broken {
            reason: format!("malformed seal (alg '{alg}')"),
        };
    }
    // a machine key the owner's authority authorises (an administrator may authorise a machine's existing key): its
    // seals are owner facts under the authority's standing
    if let Some(h) = v.held(&key_id) {
        let k = BindingKey {
            key: h.key.clone(),
            id: h.key_id.clone(),
        };
        return match verify_with(&k, data, body) {
            Binding::Verified { operation, at, .. } => {
                let authority = match &v.keyring {
                    Ok(Some(k)) => k.authority.authority_id.clone(),
                    _ => crate::srr::binding::installed_authority_unverified(
                        v.state_root.as_deref().unwrap_or(Path::new("")),
                    )
                    .and_then(|a| a["authority_id"].as_str().map(String::from))
                    .unwrap_or_else(|| "t2-binding".into()),
                };
                owner_standing(
                    v,
                    &key_id,
                    owner_key_name(&authority, &key_id),
                    operation,
                    at,
                )
            }
            other => other,
        };
    }
    match load_key() {
        Ok(Some(local)) => match verify_with(&local, data, body) {
            Binding::Verified { key_id, operation, at } if v.sealing(&now_iso()).is_some() => {
                Binding::Unauthorised {
                    key_id,
                    reason: format!(
                        "sealed at {at} by '{operation}' with this machine's own key; this machine is bound to the owner's T2 binding authority and honours only facts sealed under it (P2-ADJ-0002). Records this machine sealed while it was provisioned are re-sealed with `{RESEAL_COMMAND}`"
                    ),
                }
            }
            other => other,
        },
        // this machine never sealed anything in the machine scope, so a machine-scope seal is another machine's
        Ok(None) => Binding::Foreign { key_id },
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

/// **The one T2 binding status** (`gov trust status` → `t2_binding`): whether this machine is bound to the owner's
/// T2 binding authority and whether that authority verifies now, which scope new seals take and why, the key new
/// seals use, and every key this machine holds with its standing. Read-only; never prints key material.
pub fn binding_status() -> Value {
    let v = machine_view();
    let now = now_iso();
    let sealing = v.sealing(&now);
    let machine_key = binding_key_id();
    let valid = v.valid(&now);
    let (bound, authority, authority_error) = match (&valid, &v.keyring) {
        (Ok(Some(k)), _) => {
            let mut a = k.authority.to_value();
            a["authorised_by_trusted_root"] = json!(true);
            (true, a, Value::Null)
        }
        (Ok(None), _) => (false, Value::Null, Value::Null),
        (Err(e), _) => {
            let mut a = v
                .state_root
                .as_deref()
                .and_then(crate::srr::binding::installed_authority_unverified)
                .unwrap_or(Value::Null);
            if a.is_object() {
                a["authorised_by_trusted_root"] = json!(false);
                a["unauthorised_reason"] = json!(e);
            }
            let (code, message) = e.split_once(": ").unwrap_or(("T2_BINDING_INVALID", e));
            (false, a, json!({"code": code, "message": message}))
        }
    };
    let standing_of = |id: &str| -> &'static str {
        match &valid {
            Ok(Some(k)) => k
                .standing(id)
                .map(|s| s.as_str())
                .unwrap_or("NOT_AUTHORISED"),
            _ => "NOT_AUTHORISED",
        }
    };
    let mut held: Vec<Value> = v
        .held
        .iter()
        .map(|h| json!({"key_id": h.key_id, "standing": standing_of(&h.key_id), "kind": "binding key"}))
        .collect();
    if let Some(m) = &machine_key {
        if !v.held.iter().any(|h| &h.key_id == m) {
            held.push(
                json!({"key_id": m, "standing": standing_of(m), "kind": "this machine's own key"}),
            );
        }
    }
    let (sealing_key_id, sealing_json) = match sealing {
        Some((k, a)) => (
            json!(a.key_id),
            json!({"scope": "provisioned", "authority_id": k.authority.authority_id, "key_id": a.key_id, "alg": SEAL_ALG_PORTABLE,
                "honoured_on": "every machine bound to this authority that holds this key and whose trusted root authorises it (the owner's provisioned machines), after a Git clone or pull"}),
        ),
        None => (
            json!(machine_key),
            json!({"scope": "machine", "machine_key_id": machine_key, "alg": SEAL_ALG,
                "honoured_on": "this machine only", "reason": v.why_machine_scope(&now)}),
        ),
    };
    let active = match &valid {
        Ok(Some(k)) => k.authority.active().map(|a| a.key_id.clone()),
        _ => None,
    };
    json!({
        "bound": bound,
        "state_root": v.state_root.as_ref().map(|p| p.display().to_string()),
        "machine_id": v.machine_id,
        "provisioned": v.provisioned,
        "role": AUTHORITY_ROLE,
        "root_delegates_role": match (&valid, &v.keyring) {
            (Ok(Some(_)), _) => json!(true),
            (Err(e), _) if e.starts_with("T2_BINDING_NOT_DELEGATED") => json!(false),
            _ => json!(crate::srr::binding::root_delegates_role()),
        },
        "authority": authority,
        "authority_error": authority_error,
        "portable": sealing.is_some(),
        "sealing": sealing_json,
        "sealing_key_id": sealing_key_id,
        "sealing_key_is_authority_active_key": sealing.is_some() && active.is_some() && sealing_key_id == json!(active),
        "machine_key_id": machine_key,
        "held_keys": held,
        "provision_command": PROVISION_COMMAND,
        "reseal_command": RESEAL_COMMAND,
        "meaning": if bound {
            "T2 facts sealed under an ACTIVE or RETIRED key of this authority were written by an owner machine; any other seal is not honoured here (FOREIGN, or UNAUTHORISED for a key this machine holds but the authority does not authorise now, including this machine's own key)"
        } else {
            "no owner binding authority is honoured here: T2 facts this machine writes are sealed with its own key and are FOREIGN (not honoured) on every other machine"
        },
        "cannot_provide_authority": ["repository content (an authority or key file inside a repository is refused)", "environment variables", "CLI flags", "a key the owner did not authorise under this machine's root", "another owner's root"],
        "premise": "ARCH-0003 §1/§8: the administrator boundary is uncompromised; the binding key is protected machine material installed from the administrator domain. A process with the operator's OS privileges can read it (detection-grade against that attacker; human answers stay owner-signed).",
    })
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

/// A seal's standing judged against exactly this machine's keys: a portable seal against the owner's authority, a
/// machine-scope seal against this machine's own key (whatever the machine's standing: reseal asks whether this
/// machine made it).
fn verify_in(m: &MachineView, local: &BindingKey, v: &Value, body: &str) -> Binding {
    if v[SEAL_FIELD].get("alg").and_then(|a| a.as_str()) == Some(SEAL_ALG_PORTABLE) {
        verify_portable(m, v, body)
    } else {
        verify_with(local, v, body)
    }
}

/// The owner's key new seals use: (authority id, key id, key).
type OwnerKey<'a> = (&'a str, &'a str, &'a [u8]);

/// Re-seal, inside `v` (bottom-up), every object whose machine-scope seal verifies under this machine's own key and
/// was made at or after `since`, under the owner's active key, keeping its recorded operation and time; an enclosing
/// sealed object whose content changed is re-sealed in the scope it already had. Returns the number of seals rewritten.
fn reseal_tree(
    v: &mut Value,
    body: &str,
    m: &MachineView,
    local: &BindingKey,
    owner: OwnerKey,
    machine: &str,
    since: &str,
) -> Result<usize> {
    let Some(obj) = v.as_object() else {
        if let Some(a) = v.as_array_mut() {
            let mut n = 0;
            for x in a.iter_mut() {
                n += reseal_tree(x, "", m, local, owner, machine, since)?;
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
                n += reseal_tree(x, "", m, local, owner, machine, since)?;
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
        seal_portable_at(owner.0, owner.1, owner.2, machine, v, body, &op, &at)?;
        return Ok(n + 1);
    }
    if n > 0 {
        // content inside changed: keep this object verifiable in the scope it already had
        if b.is_portable() {
            let original_machine = str_of(&v[SEAL_FIELD], "machine");
            seal_portable_at(
                owner.0,
                owner.1,
                owner.2,
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

fn str_of(v: &Value, k: &str) -> String {
    v.get(k).and_then(|x| x.as_str()).unwrap_or("").to_string()
}

/// `gov trust reseal [--dry-run]` — continuity for records sealed on this machine before it was bound to the owner's
/// binding authority (P2-ADJ-0002). Every tracked governed record or document under `spec/` and `governance/` (the
/// kernel excluded) whose **machine-scope** seal verifies under this machine's own key and was made **while this
/// machine was provisioned** is re-sealed under the owner's active key, keeping the operation and time the OS
/// recorded; a record sealed while the machine was unprovisioned, or one whose seal does not verify, is left as it is
/// (the OS never blesses content it did not write, and an unprovisioned machine's records stay machine-scope).
pub fn reseal(p: &Project, dry_run: bool) -> Result<Value> {
    if !dry_run {
        crate::orchestration::control::guard_write(p, "trust reseal")?;
        crate::authority::require(p, "reseal_t2_bindings")?;
    }
    let m = machine_view();
    let at = now_iso();
    let Some((k, active)) = m.sealing(&at) else {
        return Err(GovError::new(
            "T2_BINDING_UNAVAILABLE",
            format!(
                "this machine does not seal under the owner's T2 binding authority: {}",
                m.why_machine_scope(&at)
            ),
        )
        .with_details(json!({"provision_command": PROVISION_COMMAND})));
    };
    let since = m.provisioned_at.clone().ok_or_else(|| {
        GovError::new(
            "T2_BINDING_UNAVAILABLE",
            "this machine's provisioning time is not recorded, so records sealed while it was unprovisioned cannot be told apart; nothing was resealed",
        )
    })?;
    let Some(local) = load_key()? else {
        return Ok(
            json!({"resealed_files": [], "resealed_seals": 0, "note": "this machine holds no machine-scope key: nothing was sealed here before it was bound"}),
        );
    };
    let owner: OwnerKey = (
        k.authority.authority_id.as_str(),
        active.key_id.as_str(),
        active.key.as_slice(),
    );
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
        if rel.ends_with(".json") {
            let Ok(mut v) = serde_json::from_str::<Value>(&text) else {
                continue;
            };
            let n = reseal_tree(&mut v, "", &m, &local, owner, &m.machine_id, &since)?;
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
            let n = reseal_tree(&mut r.data, &body, &m, &local, owner, &m.machine_id, &since)?;
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
        let n = reseal_tree(&mut v, "", &m, &local, owner, &m.machine_id, &since)?;
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
        "authority_id": k.authority.authority_id,
        "key_id": active.key_id,
        "machine_id": m.machine_id,
        "provisioned_at": since,
        "resealed_seals": total,
        "resealed_files": files,
        "rule": "only machine-scope seals that verify under this machine's own key and were made while it was provisioned are resealed, keeping the operation and time the OS recorded; records sealed while unprovisioned, and records whose seal does not verify, are left as they are",
    }))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::srr::binding::{AuthorisedKey, Authority, KeyStatus};

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

    /// An owner authority (as `srr::binding::keyring` hands it back after verifying it) authorising `keys`.
    fn authority(id: &str, version: u64, expires: &str, keys: &[(&[u8], KeyStatus)]) -> Authority {
        Authority {
            authority_id: id.into(),
            owner: "test".into(),
            version,
            expires: expires.into(),
            keys: keys
                .iter()
                .map(|(k, st)| AuthorisedKey {
                    key_id: crate::srr::binding::key_id_of(k),
                    commitment: crate::srr::binding::commitment_of(k),
                    status: *st,
                })
                .collect(),
            machines: None,
            sha256: String::new(),
            signed_by: vec![],
        }
    }

    fn held(k: &[u8], status: Option<KeyStatus>) -> HeldKey {
        HeldKey {
            key_id: crate::srr::binding::key_id_of(k),
            status,
            key: k.to_vec(),
        }
    }

    /// A machine bound to `auth`, holding `keys`.
    fn bound(auth: Authority, keys: &[&[u8]]) -> MachineView {
        let held_keys: Vec<HeldKey> = keys
            .iter()
            .map(|k| held(k, auth.standing(&crate::srr::binding::key_id_of(k))))
            .collect();
        MachineView {
            provisioned: true,
            machine_id: "machine-B".into(),
            keyring: Ok(Some(Keyring {
                authority: auth,
                keys: held_keys.clone(),
            })),
            held: held_keys,
            ..Default::default()
        }
    }

    const FAR: &str = "2099-01-01T00:00:00Z";

    /// P2-ADJ-0002: a portable seal verifies on any machine bound to the owner's authority that holds the key and
    /// whose authority authorises it now; it binds the authority, the key, the sealing machine, the operation, the time
    /// and the content, and it is refused (typed) everywhere else.
    #[test]
    fn a_portable_seal_is_honoured_where_the_key_is_held_and_authorised_and_nowhere_else() {
        let k1 = [0x42u8; 32];
        let k1_id = crate::srr::binding::key_id_of(&k1);
        let mut data = json!({"id": "HDG-0001", "type": "human-gate", "gate_status": "ANSWERED", "question": "q?"});
        seal_portable_at(
            "owner",
            &k1_id,
            &k1,
            "machine-A",
            &mut data,
            "",
            "gate answer",
            "2026-09-19T01:02:03Z",
        )
        .unwrap();
        let machine_b = bound(
            authority("owner", 1, FAR, &[(&k1, KeyStatus::Active)]),
            &[&k1],
        );
        let b = verify_portable(&machine_b, &data, "");
        assert!(b.is_verified() && b.is_portable(), "{b:?}");
        assert_eq!(b.to_value()["scope"], "provisioned");
        assert_eq!(b.to_value()["key_id"], format!("owner/{k1_id}"));
        // a machine that does not hold the key (unprovisioned, not bound, another owner)
        let other = bound(
            authority("other", 1, FAR, &[(&[0x43u8; 32], KeyStatus::Active)]),
            &[&[0x43u8; 32]],
        );
        assert_eq!(verify_portable(&other, &data, "").code(), "FOREIGN");
        assert_eq!(
            verify_portable(&MachineView::default(), &data, "").code(),
            "FOREIGN"
        );
        // rotation: k2 active, k1 retired — k1's seals stay honoured
        let k2 = [0x44u8; 32];
        let rotated = bound(
            authority(
                "owner",
                2,
                FAR,
                &[(&k2, KeyStatus::Active), (&k1, KeyStatus::Retired)],
            ),
            &[&k1, &k2],
        );
        assert!(verify_portable(&rotated, &data, "").is_verified());
        // revocation: a version that no longer lists k1
        let revoked = bound(
            authority("owner", 3, FAR, &[(&k2, KeyStatus::Active)]),
            &[&k1, &k2],
        );
        let r = verify_portable(&revoked, &data, "");
        assert_eq!(r.code(), "UNAUTHORISED", "{r:?}");
        assert!(r.to_value()["reason"].as_str().unwrap().contains("revoked"));
        // an authority that does not verify now (root succession dropped the delegation) or has expired
        let mut dropped = bound(
            authority("owner", 1, FAR, &[(&k1, KeyStatus::Active)]),
            &[&k1],
        );
        dropped.keyring = Err((
            "T2_BINDING_NOT_DELEGATED".into(),
            "the root delegates no `t2-binding` role".into(),
        ));
        let u = verify_portable(&dropped, &data, "");
        assert_eq!(u.code(), "UNAUTHORISED", "{u:?}");
        assert!(u.to_value()["reason"]
            .as_str()
            .unwrap()
            .contains("t2-binding"));
        let expired = bound(
            authority(
                "owner",
                1,
                "2020-01-01T00:00:00Z",
                &[(&k1, KeyStatus::Active)],
            ),
            &[&k1],
        );
        assert_eq!(verify_portable(&expired, &data, "").code(), "UNAUTHORISED");
        // any edit — a field, the sealing machine, the operation, the time, the authority, the key — breaks it
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
            ("authority", "someone-else"),
        ] {
            let mut e = data.clone();
            e[SEAL_FIELD][k] = json!(val);
            assert_eq!(verify_portable(&machine_b, &e, "").code(), "BROKEN", "{k}");
        }
        let mut e = data.clone();
        e[SEAL_FIELD]["scope"] = json!("machine");
        assert_eq!(verify_portable(&machine_b, &e, "").code(), "BROKEN");
        let mut e = data.clone();
        e[SEAL_FIELD]["key_id"] = json!(crate::srr::binding::key_id_of(&k2));
        assert_ne!(verify_portable(&rotated, &e, "").code(), "VERIFIED");
    }

    #[test]
    fn new_seals_are_portable_only_under_an_authority_that_verifies_now_with_its_active_key_held() {
        let now = "2026-09-19T12:00:00Z";
        let k1 = [1u8; 32];
        let k2 = [2u8; 32];
        let a = bound(
            authority("owner", 1, FAR, &[(&k1, KeyStatus::Active)]),
            &[&k1],
        );
        assert_eq!(
            a.sealing(now).unwrap().1.key_id,
            crate::srr::binding::key_id_of(&k1)
        );
        // the active key is not held here (only a retired one was installed): machine scope, and why
        let b = bound(
            authority(
                "owner",
                2,
                FAR,
                &[(&k2, KeyStatus::Active), (&k1, KeyStatus::Retired)],
            ),
            &[&k1],
        );
        assert!(b.sealing(now).is_none());
        assert!(b.why_machine_scope(now).contains("active key"));
        // expired
        let c = bound(
            authority(
                "owner",
                1,
                "2026-09-19T11:00:00Z",
                &[(&k1, KeyStatus::Active)],
            ),
            &[&k1],
        );
        assert!(c.sealing(now).is_none());
        assert!(
            c.why_machine_scope(now).contains("EXPIRED"),
            "{}",
            c.why_machine_scope(now)
        );
        let unprov = MachineView::default();
        assert!(unprov.why_machine_scope(now).contains("unprovisioned"));
        let unbound = MachineView {
            provisioned: true,
            ..Default::default()
        };
        assert!(unbound
            .why_machine_scope(now)
            .contains("no T2 binding authority is installed"));
    }

    /// Reseal moves only seals this machine made with its own key while provisioned, keeps their operation and time,
    /// and keeps an enclosing seal valid when content inside it changed.
    #[test]
    fn reseal_moves_only_post_provisioning_local_seals_and_keeps_enclosing_seals_valid() {
        let local = test_key(5);
        let akey = [0x77u8; 32];
        let akey_id = crate::srr::binding::key_id_of(&akey);
        let m = bound(
            authority("owner", 1, FAR, &[(&akey, KeyStatus::Active)]),
            &[&akey],
        );
        let owner: OwnerKey = ("owner", akey_id.as_str(), &akey);
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
        let n = reseal_tree(
            &mut doc,
            "",
            &m,
            &local,
            owner,
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
        // sealed before provisioning: left machine-scope, still verifying under the machine's own key
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
                owner,
                "m1",
                "2026-09-10T00:00:00Z"
            )
            .unwrap(),
            0
        );
        assert_eq!(forged[SEAL_FIELD]["alg"], SEAL_ALG);
    }
}
