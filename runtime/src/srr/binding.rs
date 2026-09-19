//! # The owner's T2 binding authority — the provisioning side of P2-ADJ-0002
//!
//! **The requirement** (P2-ADJ-0002, orchestrator adjudication, routed to WS-3 with WS-8 provisioning): a T2 fact
//! written by an OS operation on any machine provisioned for the owner/project is honoured on every other such
//! machine after a Git clone/pull; a record written by anything else (a hand edit, an unprovisioned machine, a
//! machine not authorised by the provisioning, a forged or modified seal) is still refused, typed and observable. No
//! private key or shared secret is stored in any repository, and no new external dependency class is introduced.
//! ARCH-0003 §8 fixes where the authority for an additional machine comes from: "Headless CI and additional machines
//! are provisioned outside the project repository with the verifier, public root metadata and protected
//! machine/workload policy."
//!
//! ## Why the authority is a delegated *binding key*, not per-machine signatures
//!
//! A T2 seal ([`crate::t2`]) is an HMAC keyed by a key held in protected machine state. For a seal written on
//! machine A to verify on machine B, B must hold the key A sealed with. The alternative the adjudication names —
//! per-machine keys that other machines verify — needs each machine to *sign* its seals, and `gov` verifies and
//! never signs (`SRR-R0-L4`; the R1 held-out suites measure that no signing capability exists in the product). So
//! the conforming design inside the accepted boundary is the other one it names: **a per-owner binding authority
//! delegated through the provisioned root**.
//!
//! * The owner's root metadata (administrator domain, already provisioned on every owner machine) delegates a role,
//!   [`ROLE`] (`t2-binding`), to key(s) the owner holds offline.
//! * Those keys sign a **binding-authority document** ([`AUTHORITY_TYPE`]): the owner's authority id, a version, an
//!   expiry, and the binding keys it authorises — each named only by its key id and a SHA-256 *commitment*, never by
//!   its bytes — with exactly one `active` key (the one owner machines seal with) and any number of `retired` keys
//!   (still valid for verifying seals made before a rotation). A key absent from the current document is revoked.
//!   It may also list the machine ids it authorises; without such a list it authorises every machine provisioned
//!   from the root.
//! * The binding key itself (32 random bytes) travels from the administrator domain to each owner machine the same
//!   way the root metadata does — outside every repository — and `gov trust bind --authority <doc> --key <file>`
//!   installs it into protected machine state **only if** the document verifies against this machine's provisioned
//!   root at the role's threshold, is unexpired, is not older than an authority this machine already accepted, lists
//!   this machine (when it lists machines), and authorises exactly this key (id and commitment).
//!
//! Every owner machine then seals with the same key, so what one of them writes verifies on the others. A machine
//! that is unprovisioned, provisioned from another root, or provisioned from the owner's root but never given the
//! authority keeps a machine-local key: its seals are `FOREIGN` everywhere else and are refused. A hand edit breaks
//! the seal (`BROKEN`) exactly as before. Nothing secret is ever written to a repository: the document carries only
//! commitments, and the key file and the installed key live in protected machine state.
//!
//! ## Where the key goes, and the API for `crate::t2` (WS-3)
//!
//! `crate::t2` keeps its sealing key at `<state_root>/t2-binding/key.json` (`key_hex`). Binding installs the
//! authority's active key **there**, so every T2 writer and consumer uses it without any change to `t2.rs`; a key
//! that was already there (a machine that sealed records before it was bound) is kept in the keyring, never
//! destroyed. [`keyring`] is the richer interface for WS-3's round-3 work: the authority re-verified against the
//! current trusted root at the moment of use, with every key this machine holds and its standing (`ACTIVE`,
//! `RETIRED`, or not authorised), so a consumer can honour seals made under a retired key and refuse a revoked one.
//!
//! ## What this does not do (stated, not overclaimed)
//!
//! * Within one machine the binding key is exactly as protected as the machine-local key it replaces: a process
//!   with the operator's full OS privileges can read it (see `crate::t2`, "What it proves"). Across machines, a key
//!   exfiltrated from an owner machine lets its holder seal as the owner's machines — the administrator boundary
//!   (ARCH-0003 §1) is assumed, as it is for the root metadata and the break-glass inbox.
//! * Revoking one machine means rotating the authority's active key on every other owner machine; a machine the
//!   administrator never re-binds keeps sealing with the old key, which re-bound machines then refuse (fail closed).
//! * `crate::t2` still verifies against the single installed key; honouring retired keys and refusing a key whose
//!   authority no longer verifies is the consumer side (WS-3), through [`keyring`].
use crate::srr::breakglass::{self, Effect};
use crate::srr::metadata::{self, Envelope, Root};
use crate::srr::state::{fsync_dir, write_durable, MachineState};
use crate::util::{now_iso, sha256_hex};
use crate::{GovError, Result, FRAMEWORK_NAME};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

/// The root-delegated role whose keys authorise the owner's T2 binding authority.
pub const ROLE: &str = "t2-binding";
/// `_type` of the binding-authority document the `t2-binding` role signs.
pub const AUTHORITY_TYPE: &str = "t2-binding-authority";
/// `_type` of a binding-key file handed over from the administrator domain (optional in the file; a `crate::t2`
/// `key.json` carrying only `key_hex` is accepted as well, so an existing machine key can become the authority's).
pub const KEY_FILE_TYPE: &str = "t2-binding-key";
/// The directory of protected machine state `crate::t2` keeps its sealing key in.
const DIR: &str = "t2-binding";
/// The file `crate::t2` seals with and verifies against.
const CURRENT_KEY_FILE: &str = "key.json";
/// The exact bytes of the accepted binding-authority document.
const AUTHORITY_FILE: &str = "authority.json";
/// What this machine accepted, and the highest authority version it has seen (never lowered).
const BINDING_FILE: &str = "binding.json";
/// Every binding key this machine holds, by key id (verification material for rotated keys).
const KEYRING_DIR: &str = "keyring";

/// The key id `crate::t2` derives for a sealing key (the id a seal names). Kept identical to `t2::key_id_of`.
pub fn key_id_of(key: &[u8]) -> String {
    sha256_hex(&[b"t2-binding-key-id:".as_slice(), key].concat())[..16].to_string()
}

/// The commitment the authority document publishes for a key: SHA-256 over a domain-separated encoding of the key.
/// It identifies the key without disclosing it.
pub fn commitment_of(key: &[u8]) -> String {
    sha256_hex(&[b"t2-binding-key-commitment:".as_slice(), key].concat())
}

/// Standing of a binding key under the owner's current authority.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum KeyStatus {
    /// The key owner machines seal with now.
    Active,
    /// Superseded for sealing; seals made under it remain valid.
    Retired,
}

impl KeyStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            KeyStatus::Active => "ACTIVE",
            KeyStatus::Retired => "RETIRED",
        }
    }
    fn parse(s: &str) -> Option<KeyStatus> {
        match s {
            "active" | "ACTIVE" => Some(KeyStatus::Active),
            "retired" | "RETIRED" => Some(KeyStatus::Retired),
            _ => None,
        }
    }
}

/// One key an authority document authorises.
#[derive(Debug, Clone)]
pub struct AuthorisedKey {
    pub key_id: String,
    pub commitment: String,
    pub status: KeyStatus,
}

/// A binding-authority document that verified against a trusted root.
#[derive(Debug, Clone)]
pub struct Authority {
    pub authority_id: String,
    pub owner: String,
    pub version: u64,
    pub expires: String,
    pub keys: Vec<AuthorisedKey>,
    /// `None`: every machine provisioned from the root; `Some`: exactly these machine ids.
    pub machines: Option<Vec<String>>,
    /// SHA-256 of the whole document file.
    pub sha256: String,
    /// Key ids of the `t2-binding` role that signed it (at least the threshold).
    pub signed_by: Vec<String>,
}

impl Authority {
    pub fn active(&self) -> Option<&AuthorisedKey> {
        self.keys.iter().find(|k| k.status == KeyStatus::Active)
    }
    pub fn standing(&self, key_id: &str) -> Option<KeyStatus> {
        self.keys
            .iter()
            .find(|k| k.key_id == key_id)
            .map(|k| k.status)
    }
    pub fn authorises_machine(&self, machine_id: &str) -> bool {
        match &self.machines {
            None => true,
            Some(list) => list.iter().any(|m| m == machine_id),
        }
    }
    pub fn to_value(&self) -> Value {
        json!({
            "authority_id": self.authority_id, "owner": self.owner, "version": self.version, "expires": self.expires,
            "keys": self.keys.iter().map(|k| json!({"key_id": k.key_id, "commitment": k.commitment, "status": k.status.as_str()})).collect::<Vec<_>>(),
            "machines": self.machines.clone().map(Value::from).unwrap_or(json!("every machine provisioned from the root")),
            "sha256": self.sha256, "signed_by": self.signed_by,
        })
    }
}

fn refusal(code: &str, message: String, details: Value) -> GovError {
    GovError::new(code, message).with_details(details)
}

/// Parse and verify a binding-authority document against `root`: type, spec version, product, the `t2-binding`
/// role's signatures at its threshold, expiry against the declared local clock, and the shape of the key list
/// (exactly one active key; ids and commitments well formed; no key listed twice).
pub fn verify_authority(root: &Root, env: &Envelope, now: &str) -> Result<Authority> {
    if env.typ() != AUTHORITY_TYPE {
        return Err(refusal(
            "T2_BINDING_AUTHORITY_INVALID",
            format!(
                "{}: expected a `{AUTHORITY_TYPE}` document, found _type '{}'",
                env.source,
                env.typ()
            ),
            json!({"source": env.source}),
        ));
    }
    if env.spec_version() != metadata::SPEC_VERSION {
        return Err(refusal(
            "T2_BINDING_AUTHORITY_INVALID",
            format!(
                "{}: spec_version '{}' is not '{}'",
                env.source,
                env.spec_version(),
                metadata::SPEC_VERSION
            ),
            json!({"source": env.source}),
        ));
    }
    if env.product() != root.product {
        return Err(refusal(
            "T2_BINDING_AUTHORITY_INVALID",
            format!(
                "{}: the authority is for product '{}', this machine's root is for '{}'",
                env.source,
                env.product(),
                root.product
            ),
            json!({"source": env.source}),
        ));
    }
    if !root.has_role(ROLE) {
        return Err(refusal(
            "T2_BINDING_NOT_DELEGATED",
            format!("this machine's trusted root (version {}) delegates no `{ROLE}` role, so no binding authority can verify against it. The owner adds the delegation by root succession (`gov trust root-update`).", root.version),
            json!({"root_version": root.version, "roles": root.roles.keys().cloned().collect::<Vec<_>>()}),
        ));
    }
    // The signatures, at the role's threshold, over the exact signed bytes (the same verifier every role uses).
    let signed_by = root.verify_role(ROLE, env)?;
    if let Some(fault) = env.expiry_fault(now) {
        return Err(refusal(
            "T2_BINDING_AUTHORITY_EXPIRED",
            format!(
                "{}: the binding authority is not current: {fault}",
                env.source
            ),
            json!({"expires": env.expires(), "local_clock": now}),
        ));
    }
    let s = &env.signed;
    let authority_id = s["authority_id"].as_str().unwrap_or("").to_string();
    let version = env.version();
    if authority_id.is_empty() || version == 0 {
        return Err(refusal(
            "T2_BINDING_AUTHORITY_INVALID",
            format!(
                "{}: an authority must name itself (`authority_id`) and carry a version >= 1",
                env.source
            ),
            json!({"source": env.source}),
        ));
    }
    let hex_of = |v: &str, n: usize| v.len() == n && v.chars().all(|c| c.is_ascii_hexdigit());
    let mut keys: Vec<AuthorisedKey> = vec![];
    for k in s["keys"].as_array().cloned().unwrap_or_default() {
        let key_id = k["key_id"].as_str().unwrap_or("").to_ascii_lowercase();
        let commitment = k["commitment"].as_str().unwrap_or("").to_ascii_lowercase();
        let status = k["status"].as_str().and_then(KeyStatus::parse);
        match status {
            Some(status) if hex_of(&key_id, 16) && hex_of(&commitment, 64) => {
                if keys.iter().any(|x| x.key_id == key_id) {
                    return Err(refusal(
                        "T2_BINDING_AUTHORITY_INVALID",
                        format!("{}: key {key_id} is listed twice", env.source),
                        json!({"source": env.source}),
                    ));
                }
                keys.push(AuthorisedKey {
                    key_id,
                    commitment,
                    status,
                });
            }
            _ => {
                return Err(refusal(
                    "T2_BINDING_AUTHORITY_INVALID",
                    format!("{}: every key entry needs `key_id` (16 hex), `commitment` (64 hex) and `status` (active | retired): {k}", env.source),
                    json!({"source": env.source}),
                ))
            }
        }
    }
    if keys
        .iter()
        .filter(|k| k.status == KeyStatus::Active)
        .count()
        != 1
    {
        return Err(refusal(
            "T2_BINDING_AUTHORITY_INVALID",
            format!("{}: an authority authorises exactly one active binding key (the one owner machines seal with); found {}", env.source, keys.iter().filter(|k| k.status == KeyStatus::Active).count()),
            json!({"source": env.source}),
        ));
    }
    let machines = match &s["machines"] {
        Value::Null => None,
        Value::Array(a) => Some(
            a.iter()
                .filter_map(|m| m.as_str().map(String::from))
                .collect(),
        ),
        other => {
            return Err(refusal(
                "T2_BINDING_AUTHORITY_INVALID",
                format!(
                    "{}: `machines` must be a list of machine ids, found {other}",
                    env.source
                ),
                json!({"source": env.source}),
            ))
        }
    };
    Ok(Authority {
        authority_id,
        owner: s["owner"].as_str().unwrap_or("").to_string(),
        version,
        expires: env.expires().to_string(),
        keys,
        machines,
        sha256: env.file_sha256.clone(),
        signed_by,
    })
}

/// Where this machine keeps the binding state (the directory `crate::t2` keeps its key in).
fn dir_of(ms: &MachineState) -> PathBuf {
    ms.root.join(DIR)
}

/// Refuse material taken from inside a governed repository: the authority and the key come from the administrator
/// domain (ARCH-0003 §5, §8), never from repository content.
fn refuse_repository_sourced(file: &Path, what: &str, project_root: Option<&Path>) -> Result<()> {
    let abs = file.canonicalize().unwrap_or_else(|_| file.to_path_buf());
    let inside_project = project_root
        .map(|pr| pr.canonicalize().unwrap_or_else(|_| pr.to_path_buf()))
        .map(|pabs| abs.starts_with(&pabs))
        .unwrap_or(false);
    let repository_component = abs.components().any(|c| {
        let s = c.as_os_str().to_string_lossy();
        s == ".git" || s == "governance"
    });
    if inside_project || repository_component {
        return Err(refusal(
            "T2_BINDING_FROM_REPOSITORY_REFUSED",
            format!("{} ({what}) is repository content. The owner's T2 binding authority and its key come from the administrator domain, outside every repository (ARCH-0003 §8, P2-ADJ-0002: no key or shared secret in any repository).", abs.display()),
            json!({"file": abs.display().to_string(), "what": what}),
        ));
    }
    Ok(())
}

fn read_key_file(key_file: &Path) -> Result<Vec<u8>> {
    let v = crate::util::read_json(key_file).map_err(|e| {
        refusal(
            "T2_BINDING_KEY_INVALID",
            format!(
                "{}: not a binding-key file: {}",
                key_file.display(),
                e.message
            ),
            json!({"file": key_file.display().to_string()}),
        )
    })?;
    if let Some(t) = v.get("_type").and_then(|t| t.as_str()) {
        if t != KEY_FILE_TYPE {
            return Err(refusal(
                "T2_BINDING_KEY_INVALID",
                format!(
                    "{}: expected _type '{KEY_FILE_TYPE}', found '{t}'",
                    key_file.display()
                ),
                json!({"file": key_file.display().to_string()}),
            ));
        }
    }
    let key = v["key_hex"]
        .as_str()
        .and_then(|h| hex::decode(h).ok())
        .filter(|k| k.len() == 32)
        .ok_or_else(|| {
            refusal(
                "T2_BINDING_KEY_INVALID",
                format!("{}: `key_hex` must be 32 bytes of hex", key_file.display()),
                json!({"file": key_file.display().to_string()}),
            )
        })?;
    Ok(key)
}

/// Write bytes durably (temp → fsync → rename → fsync(dir)), readable by the owning account only.
fn write_private(path: &Path, bytes: &[u8]) -> Result<()> {
    let parent = path.parent().ok_or_else(|| {
        GovError::new(
            "IO_ERROR",
            format!("{} has no parent directory", path.display()),
        )
    })?;
    std::fs::create_dir_all(parent)
        .map_err(|e| GovError::io(&format!("mkdir {}", parent.display()), e))?;
    let tmp = parent.join(format!(
        ".{}.tmp-{}-{}",
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
            let _ = f.set_permissions(std::fs::Permissions::from_mode(0o600));
        }
        f.write_all(bytes)
            .map_err(|e| GovError::io(&format!("write {}", tmp.display()), e))?;
        f.sync_all()
            .map_err(|e| GovError::io(&format!("fsync {}", tmp.display()), e))?;
    }
    std::fs::rename(&tmp, path)
        .map_err(|e| GovError::io(&format!("rename into {}", path.display()), e))?;
    fsync_dir(parent);
    Ok(())
}

fn key_doc(key: &[u8], status: &str, authority: Option<&Authority>, note: &str) -> Value {
    json!({
        "key_hex": hex::encode(key),
        "key_id": key_id_of(key),
        "commitment": commitment_of(key),
        "status": status,
        "authority": authority.map(|a| json!({"authority_id": a.authority_id, "version": a.version, "sha256": a.sha256})),
        "installed_at": now_iso(),
        "created": now_iso(),
        "purpose": note,
    })
}

/// **`gov trust bind`** — install the owner's T2 binding authority on this provisioned machine.
///
/// `authority_file` is the owner-signed binding-authority document and `key_file` one binding key it authorises,
/// both from the administrator domain. Re-binding the same authority and key is a no-op; binding a newer authority
/// (a rotation) retires nothing on its own — the document says which key is active.
pub fn bind(authority_file: &Path, key_file: &Path, project_root: Option<&Path>) -> Result<Value> {
    crate::srr::state::refuse_authority_env()?;
    let ms = MachineState::open()?;
    // OWNER-DECISION-0006 §6 bullet 4: installing a binding authority changes which T2 facts this machine honours —
    // a trust-policy mutation, refused below floor. The effect is refused again inside the write
    // (`install_binding`), so the operation-level refusal here only gives the accurate diagnosis first.
    breakglass::guard(&ms, FRAMEWORK_NAME, "trust bind")?;
    refuse_repository_sourced(authority_file, "binding authority", project_root)?;
    refuse_repository_sourced(key_file, "binding key", project_root)?;
    let now = metadata::local_clock_now();
    let root = super::verifier::trusted_root(&ms, &now)?.ok_or_else(|| {
        refusal(
            "T2_BINDING_UNPROVISIONED",
            "this machine holds no trust anchor. A binding authority is delegated through the owner's provisioned root, so an unprovisioned machine cannot be authorised to write T2 facts other owner machines honour (OWNER-DECISION-P2-0002, P2-ADJ-0002).".to_string(),
            json!({"remediation": ["gov trust provision --anchor <root metadata from the administrator domain>", "gov trust bind --authority <owner-signed t2-binding-authority> --key <binding key from the administrator domain>"]}),
        )
    })?;
    let bytes = std::fs::read(authority_file)
        .map_err(|e| GovError::io(&format!("read {}", authority_file.display()), e))?;
    let env = Envelope::parse(&bytes, &authority_file.display().to_string())?;
    let authority = verify_authority(&root, &env, &now)?;
    if !authority.authorises_machine(&ms.machine_id) {
        return Err(refusal(
            "T2_BINDING_MACHINE_NOT_AUTHORISED",
            format!("the binding authority '{}' (version {}) lists the machines it authorises, and this machine ({}) is not one of them", authority.authority_id, authority.version, ms.machine_id),
            json!({"machine_id": ms.machine_id, "authority": authority.to_value()}),
        ));
    }
    let key = read_key_file(key_file)?;
    let key_id = key_id_of(&key);
    let entry = authority
        .keys
        .iter()
        .find(|k| k.key_id == key_id)
        .ok_or_else(|| {
            refusal(
                "T2_BINDING_KEY_NOT_AUTHORISED",
                format!("the key in {} (id {key_id}) is not authorised by binding authority '{}' version {}", key_file.display(), authority.authority_id, authority.version),
                json!({"key_id": key_id, "authorised": authority.keys.iter().map(|k| k.key_id.clone()).collect::<Vec<_>>()}),
            )
        })?;
    if entry.commitment != commitment_of(&key) {
        return Err(refusal(
            "T2_BINDING_KEY_MISMATCH",
            format!("the key in {} has id {key_id}, but its commitment does not match the one binding authority '{}' publishes for that id", key_file.display(), authority.authority_id),
            json!({"key_id": key_id}),
        ));
    }
    let prior = read_binding(&ms);
    let highest = prior["highest_version"].as_u64().unwrap_or(0);
    if authority.version < highest {
        return Err(refusal(
            "T2_BINDING_AUTHORITY_ROLLBACK",
            format!("binding authority version {} is older than version {highest} this machine already accepted; an older authority can re-enable a key the owner revoked", authority.version),
            json!({"presented_version": authority.version, "highest_accepted_version": highest}),
        ));
    }
    if authority.version == highest
        && prior["authority_sha256"]
            .as_str()
            .map(|s| s != authority.sha256)
            .unwrap_or(false)
    {
        return Err(refusal(
            "T2_BINDING_AUTHORITY_CONFLICT",
            format!("a different binding-authority document with the same version {highest} was already accepted here; the owner issues a new version instead"),
            json!({"version": highest, "accepted_sha256": prior["authority_sha256"], "presented_sha256": authority.sha256}),
        ));
    }
    install_binding(&ms, &root, &authority, &bytes, &key, entry.status)
}

/// The one writer of the binding state. Refuses the effect below floor at the instant of the write.
fn install_binding(
    ms: &MachineState,
    root: &Root,
    authority: &Authority,
    authority_bytes: &[u8],
    key: &[u8],
    status: KeyStatus,
) -> Result<Value> {
    breakglass::guard_effect_on(
        ms,
        FRAMEWORK_NAME,
        Effect::TrustPolicyMutation,
        "t2 binding authority write",
    )?;
    let dir = dir_of(ms);
    let key_id = key_id_of(key);
    // 1. the key joins the keyring (verification material, whatever its status)
    write_private(
        &dir.join(KEYRING_DIR).join(format!("{key_id}.json")),
        (serde_json::to_string_pretty(&key_doc(
            key,
            status.as_str(),
            Some(authority),
            "binding key authorised by the owner's t2-binding authority (P2-ADJ-0002)",
        ))? + "\n")
            .as_bytes(),
    )?;
    // 2. the accepted authority, as its exact bytes
    write_private(&dir.join(AUTHORITY_FILE), authority_bytes)?;
    // 3. an active key becomes the key `crate::t2` seals with; a machine-local key it replaces is kept
    let current_path = dir.join(CURRENT_KEY_FILE);
    let previous = crate::util::read_json(&current_path).ok();
    let previous_id = previous
        .as_ref()
        .and_then(|v| v["key_hex"].as_str())
        .and_then(|h| hex::decode(h).ok())
        .map(|k| key_id_of(&k));
    let mut retired_local: Option<String> = None;
    if status == KeyStatus::Active && previous_id.as_deref() != Some(key_id.as_str()) {
        if let (Some(prev), Some(pid)) = (previous.as_ref(), previous_id.as_ref()) {
            let kept = dir.join(KEYRING_DIR).join(format!("{pid}.json"));
            if !kept.exists() {
                let mut doc = prev.clone();
                doc["status"] = json!("MACHINE_LOCAL");
                doc["kept_at"] = json!(now_iso());
                doc["note"] = json!("the machine-local key this machine sealed with before it was bound; kept so records sealed under it stay verifiable (by the T2 consumer, through srr::binding::keyring)");
                write_private(
                    &kept,
                    (serde_json::to_string_pretty(&doc)? + "\n").as_bytes(),
                )?;
            }
            if authority.standing(pid).is_none() {
                retired_local = Some(pid.clone());
            }
        }
        write_private(
            &current_path,
            (serde_json::to_string_pretty(&key_doc(key, "ACTIVE", Some(authority), "T2 binding key (BC-P2-09) delegated by the owner's t2-binding authority (P2-ADJ-0002): every owner machine seals with it. Keep it out of every repository; anyone who can read it can seal records as the owner's machines."))? + "\n").as_bytes(),
        )?;
    }
    let sealing_key = crate::util::read_json(&current_path)
        .ok()
        .and_then(|v| v["key_hex"].as_str().and_then(|h| hex::decode(h).ok()))
        .map(|k| key_id_of(&k));
    // 4. what was accepted (the version floor never goes down)
    let record = json!({
        "authority_id": authority.authority_id, "authority_version": authority.version,
        "highest_version": authority.version, "authority_sha256": authority.sha256,
        "authority_expires": authority.expires, "root_version": root.version, "product": root.product,
        "machine_id": ms.machine_id, "bound_at": now_iso(), "active_key_id": authority.active().map(|k| k.key_id.clone()),
        "sealing_key_id": sealing_key, "machine_local_key_kept": retired_local,
    });
    write_durable(&dir.join(BINDING_FILE), &record)?;
    Ok(json!({
        "bound": true, "machine_id": ms.machine_id, "authority": authority.to_value(), "root_version": root.version,
        "installed_key": {"key_id": key_id, "status": status.as_str()},
        "sealing_key_id": sealing_key,
        "sealing_key_is_authority_active_key": sealing_key.is_some() && sealing_key == authority.active().map(|k| k.key_id.clone()),
        "machine_local_key_kept": retired_local,
        "state": dir.display().to_string(),
        "note": "T2 facts this machine's gov operations write from now on are sealed with the owner's binding key, and verify on every other machine bound to the same authority (P2-ADJ-0002). Records sealed by an unbound, unprovisioned or foreign machine stay FOREIGN here and are refused.",
    }))
}

fn read_binding(ms: &MachineState) -> Value {
    crate::util::read_json(&dir_of(ms).join(BINDING_FILE)).unwrap_or(Value::Null)
}

/// One key this machine holds, with its standing under the current authority.
#[derive(Debug, Clone)]
pub struct HeldKey {
    pub key_id: String,
    /// `Some` when the current authority lists the key; `None` for a machine-local key the authority does not name.
    pub status: Option<KeyStatus>,
    pub key: Vec<u8>,
}

/// The owner's binding authority as this machine holds it, **re-verified against the current trusted root at the
/// moment of the call** (a root succession that drops the `t2-binding` delegation or its keys, or an expired or
/// tampered document, yields an error, never a stale keyring).
#[derive(Debug, Clone)]
pub struct Keyring {
    pub authority: Authority,
    pub keys: Vec<HeldKey>,
}

impl Keyring {
    /// The key owner machines seal with now, if this machine holds it.
    pub fn active(&self) -> Option<&HeldKey> {
        self.keys
            .iter()
            .find(|k| k.status == Some(KeyStatus::Active))
    }
    /// The standing of `key_id` (a seal's key id) under the current authority: `Some(Active | Retired)` when the
    /// authority authorises it, `None` when it does not (a revoked, foreign or machine-local key).
    pub fn standing(&self, key_id: &str) -> Option<KeyStatus> {
        self.authority.standing(key_id)
    }
    /// Key material for `key_id`, when this machine holds it and the authority authorises it.
    pub fn verification_key(&self, key_id: &str) -> Option<&[u8]> {
        self.keys
            .iter()
            .find(|k| k.key_id == key_id && k.status.is_some())
            .map(|k| k.key.as_slice())
    }
}

/// **The API for the T2 consumer (WS-3).** `Ok(None)` on a machine that holds no binding authority (unprovisioned,
/// or provisioned but never bound): its seals are machine-local. `Err` when an authority is installed but does not
/// verify now (root succession dropped the delegation, the document expired or was altered): the consumer refuses
/// rather than trusting a stale authority. Read-only: nothing is created or written.
pub fn keyring() -> Result<Option<Keyring>> {
    let root_dir = crate::srr::state::resolve_state_root()?;
    let ms = MachineState::read_only(&root_dir);
    let dir = dir_of(&ms);
    let path = dir.join(AUTHORITY_FILE);
    if !path.exists() {
        return Ok(None);
    }
    let now = metadata::local_clock_now();
    let root = super::verifier::trusted_root(&ms, &now)?.ok_or_else(|| {
        refusal("T2_BINDING_UNPROVISIONED", "a binding authority is installed on a machine that holds no trust anchor; it cannot be verified and is not honoured".into(), json!({"authority": path.display().to_string()}))
    })?;
    let env = Envelope::read(&path)?;
    let authority = verify_authority(&root, &env, &now)?;
    let recorded = read_binding(&ms);
    if recorded["authority_sha256"].as_str() != Some(authority.sha256.as_str()) {
        return Err(refusal(
            "T2_BINDING_STATE_INCONSISTENT",
            "the installed binding-authority document is not the one this machine recorded accepting".into(),
            json!({"recorded": recorded["authority_sha256"], "installed": authority.sha256}),
        ));
    }
    let mut keys: Vec<HeldKey> = vec![];
    if let Ok(rd) = std::fs::read_dir(dir.join(KEYRING_DIR)) {
        let mut paths: Vec<PathBuf> = rd.filter_map(|e| e.ok()).map(|e| e.path()).collect();
        paths.sort();
        for p in paths {
            let Some(k) = crate::util::read_json(&p)
                .ok()
                .and_then(|v| v["key_hex"].as_str().and_then(|h| hex::decode(h).ok()))
                .filter(|k| k.len() == 32)
            else {
                continue;
            };
            let key_id = key_id_of(&k);
            let status = authority
                .keys
                .iter()
                .find(|a| a.key_id == key_id && a.commitment == commitment_of(&k))
                .map(|a| a.status);
            keys.push(HeldKey {
                key_id,
                status,
                key: k,
            });
        }
    }
    Ok(Some(Keyring { authority, keys }))
}

/// `gov trust status` → `t2_binding`: whether this machine is bound, to which authority, and whether the key
/// `crate::t2` seals with is the authority's active key. Read-only; never prints key material.
pub fn status() -> Value {
    let sealing = crate::t2::binding_key_id();
    match keyring() {
        Ok(None) => json!({
            "bound": false,
            "sealing_key_id": sealing,
            "meaning": "no owner binding authority is installed: T2 facts this machine writes are sealed with a machine-local key and are FOREIGN (not honoured) on every other machine",
            "remediation": "administrator: gov trust bind --authority <owner-signed t2-binding-authority> --key <binding key>, both from the administrator domain (P2-ADJ-0002)",
        }),
        Ok(Some(k)) => {
            let active = k.authority.active().map(|a| a.key_id.clone());
            json!({
                "bound": true,
                "authority": k.authority.to_value(),
                "sealing_key_id": sealing,
                "sealing_key_is_authority_active_key": sealing.is_some() && sealing == active,
                "held_keys": k.keys.iter().map(|h| json!({"key_id": h.key_id, "standing": h.status.map(|s| s.as_str()).unwrap_or("NOT_AUTHORISED")})).collect::<Vec<_>>(),
                "meaning": "T2 facts sealed with an ACTIVE or RETIRED key of this authority were written by an owner machine; any other seal is FOREIGN here",
            })
        }
        Err(e) => json!({
            "bound": false,
            "sealing_key_id": sealing,
            "authority_error": {"code": e.code, "message": e.message},
            "meaning": "a binding authority is installed but does not verify against this machine's trusted root now; it must not be honoured",
        }),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn key_ids_match_the_t2_primitive_and_commitments_are_domain_separated() {
        let k = [7u8; 32];
        // `crate::t2` derives the id a seal names with this exact encoding (t2::key_id_of is private)
        assert_eq!(
            key_id_of(&k),
            sha256_hex(&[b"t2-binding-key-id:".as_slice(), &k].concat())[..16]
        );
        assert_ne!(commitment_of(&k)[..16], key_id_of(&k));
        assert_eq!(commitment_of(&k).len(), 64);
        assert_ne!(commitment_of(&k), commitment_of(&[8u8; 32]));
    }
}
