//! # The authenticated human channel (BC-P2-10)
//!
//! Contract v3 L3: "Human approval cannot be fabricated by agent/CLI metadata"; "it must surface in active human
//! interface". ARCH-0003 §8 / OWNER-DIRECTIVE-0004: "Repository files, environment variables, caller fields, plugins
//! and models cannot manufacture trust or Human Gate approval." OWNER-DECISION-0006 req. 2 fixes the class of
//! authority: **owner-controlled local/out-of-band authority anchored in the administrator-provisioned boundary**.
//! The R1 break-glass authorisation (an owner-signed token verified against the provisioned root's `recovery` role,
//! placed in a machine-protected inbox) is the owner-accepted precedent. This module applies the same mechanism to
//! Human Decision Gates, reusing the Signed Release Root primitives through their public API
//! ([`crate::srr::metadata::Envelope`], [`crate::srr::metadata::Root::verify_role`],
//! [`crate::srr::crypto::verify_strict`], [`crate::srr::verifier::trusted_root`]).
//!
//! ## Mechanism (HC-1)
//!
//! * **Authority**: Ed25519 keys of the `human-gate` role, held by the product owner **outside the machine the
//!   agents run on** (the `gov` binary contains no signing code and no key). Threshold as delegated.
//! * **Anchor** ([`anchor`]): on a machine with a provisioned Signed Release Root, the trusted root's delegation of
//!   the `human-gate` role — the same administrator-provisioned anchor that governs releases and break-glass. A
//!   standalone human-channel anchor (`gov trust human-channel --provision`) exists only behind the kernel switch
//!   `HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned`, which is **off** (P2-ADJ-0001, following
//!   OWNER-DECISION-P2-0002 "provision, then work" and ARCH-0003 §2-§3: one trust chain, no parallel authority
//!   domain for Human Gate approval). With it off, a machine with no release root has no human channel: an answer is
//!   refused `HUMAN_CHANNEL_UNAVAILABLE` (cause `UNPROVISIONED`, remediation: provision a Signed Release Root that
//!   delegates `human-gate`), and provisioning a standalone anchor is refused `HUMAN_CHANNEL_STANDALONE_DISABLED`.
//!   Once a release root exists it alone governs, and a standalone anchor is ignored.
//! * **Answer**: an owner-signed `human-gate-answer` document binding the product, the gate id, the gate's OS-issued
//!   instance nonce, the SHA-256 of the exact decision package the OS rendered, the chosen option, a nonce and an
//!   expiry. It is placed out of band in the human-channel inbox (or passed by path — the path is not authority,
//!   the signature is). `gov decide` verifies it; a missing, unsigned, wrongly signed, expired, replayed, mis-bound
//!   (other gate / instance / package) or out-of-options document is refused with a typed error.
//! * **Presentation evidence**: a signed answer or a signed `human-gate-receipt` over the same package digest is the
//!   only thing that marks a gate `presented_in_chat`. Rendering the package to an agent's stdout does not.
//! * **Use-time re-verification**: the exact signed envelope is stored (hex) in the gate record, and every
//!   consumer that honours the answer re-verifies it against the current anchor ([`reverify`]).
//!
//! ## What cannot produce a human answer
//!
//! CLI arguments (`--by`, `--role human`, `--option`), environment variables (`GOV_ROLE=human`,
//! `GOV_HUMAN_GATE_APPROVED`), role claims (a declared L5 role carries no authority: `authority::level_of`),
//! defaults (no `--by` default), repository files (a gate/decision record is T2 state bound by
//! [`crate::t2`], and the answer's authority is a signature the repository cannot contain), plugins and model output
//! (neither holds the owner's private key).
//!
//! ## Premise (the support envelope, stated)
//!
//! ARCH-0003 §1 assumes an uncompromised local OS/administrator boundary. The owner's private key is never on the
//! agents' machine. The *verification anchor* lives in protected machine state; a process that can overwrite the
//! administrator's machine state (i.e. the administrator boundary itself) is outside the envelope, exactly as for
//! break-glass. [`status`] reports whether the anchor is writable by the invoking account so a deployment can see
//! whether that boundary actually separates the agent from the administrator.
use crate::srr::metadata::{Envelope, Root};
use crate::util::{now_iso, sha256_hex, sha256_text};
use crate::{GovError, Result, FRAMEWORK_NAME};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

/// The delegated role whose keys authorise human answers.
pub const ROLE: &str = "human-gate";
/// `_type` of an owner-signed answer.
pub const ANSWER_TYPE: &str = "human-gate-answer";
/// `_type` of an owner-signed presentation receipt (acknowledgement that the package reached the human).
pub const RECEIPT_TYPE: &str = "human-gate-receipt";
/// `_type` of a standalone human-channel anchor.
pub const ANCHOR_TYPE: &str = "human-channel-anchor";
const DIR: &str = "human-channel";
const ANCHOR_FILE: &str = "anchor.json";

/// Protected machine-state directory of the channel (outside every repository).
pub fn channel_dir() -> Result<PathBuf> {
    Ok(crate::srr::state::resolve_state_root()?.join(DIR))
}
/// Where the owner (or the owner's tooling) places signed answers and receipts.
pub fn inbox_dir() -> Result<PathBuf> {
    Ok(channel_dir()?.join("inbox"))
}
fn consumed_dir() -> Result<PathBuf> {
    Ok(channel_dir()?.join("consumed"))
}
/// Where the OS writes each rendered decision package (the exact bytes whose digest the owner signs over).
pub fn outbox_dir() -> Result<PathBuf> {
    Ok(channel_dir()?.join("outbox"))
}
fn standalone_anchor_path() -> Result<PathBuf> {
    Ok(channel_dir()?.join(ANCHOR_FILE))
}

// ------------------------------------------------------------------------------------------------ the anchor

/// The verification anchor for human answers on this machine.
#[derive(Debug, Clone)]
pub struct Anchor {
    /// `srr-root` or `standalone`.
    pub source: &'static str,
    pub version: u64,
    /// SHA-256 of the anchor document this machine holds.
    pub digest: String,
    pub threshold: usize,
    pub key_ids: Vec<String>,
    keys: BTreeMap<String, String>,
    root: Option<Root>,
}

impl Anchor {
    /// Verify `env` at the anchor's threshold; returns the accepted key ids.
    pub fn verify_signatures(&self, env: &Envelope) -> Result<Vec<String>> {
        if let Some(root) = &self.root {
            return root.verify_role(ROLE, env);
        }
        let mut accepted: Vec<String> = vec![];
        for sig in &env.signatures {
            if accepted.contains(&sig.keyid) {
                continue;
            }
            let Some(public) = self.keys.get(&sig.keyid) else {
                continue;
            };
            if crate::srr::crypto::verify_strict(public, &sig.sig, &env.signed_bytes).is_ok() {
                accepted.push(sig.keyid.clone());
            }
        }
        if accepted.len() < self.threshold {
            return Err(GovError::new(
                "SRR_THRESHOLD_NOT_MET",
                format!(
                    "{}: the human-gate anchor requires {} valid signature(s) from its keys, found {}",
                    env.source,
                    self.threshold,
                    accepted.len()
                ),
            ));
        }
        Ok(accepted)
    }
    pub fn describe(&self) -> Value {
        json!({"source": self.source, "role": ROLE, "version": self.version, "anchor_sha256": self.digest, "threshold": self.threshold, "key_ids": self.key_ids})
    }
}

/// The one command that provisions this machine's trust anchor (administrator domain).
pub const PROVISION_COMMAND: &str =
    "gov trust provision --anchor <root.json supplied from the administrator domain>";

fn unavailable(cause: &str, why: String, remediation: &str) -> GovError {
    GovError::new(
        "HUMAN_CHANNEL_UNAVAILABLE",
        format!("no authenticated human channel exists on this machine: {why}. A human answer can only come from an owner-signed document verified against an administrator-provisioned anchor (BC-P2-10; OWNER-DECISION-0006 req. 2). Remediation: {remediation}"),
    )
    .with_details(json!({"role": ROLE, "cause": cause, "remediation": remediation, "inbox": inbox_dir().ok().map(|p| p.display().to_string())}))
}

/// The kernel default of `HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned` as compiled into this
/// binary (used where no governed project is open, e.g. `gov trust human-channel` outside a project). Absent or
/// unreadable means off (P2-ADJ-0001).
pub fn standalone_allowed_by_embedded_kernel() -> bool {
    crate::kernel::embedded::files()
        .iter()
        .find(|(rel, _)| *rel == "policies/HUMAN_GATE_POLICY.yaml")
        .and_then(|(_, b)| serde_yaml::from_slice::<Value>(b).ok())
        .and_then(|d| d["human_channel"]["standalone_anchor_when_unprovisioned"].as_bool())
        .unwrap_or(false)
}

/// Resolve this machine's human-channel anchor. `standalone_allowed` is the kernel policy switch
/// `HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned`.
pub fn anchor(standalone_allowed: bool) -> Result<Anchor> {
    let ms = crate::srr::state::MachineState::open().map_err(|e| {
        unavailable(
            "MACHINE_STATE_UNRESOLVED",
            format!(
                "the protected machine state cannot be resolved ({}: {})",
                e.code, e.message
            ),
            "unset GOV_MACHINE_STATE_DIR on a provisioned machine",
        )
    })?;
    let now = crate::srr::metadata::local_clock_now();
    if let Some(root) = crate::srr::verifier::trusted_root(&ms, &now)? {
        let Some(role) = root.roles.get(ROLE).cloned() else {
            return Err(unavailable(
                "ROOT_DELEGATES_NO_HUMAN_GATE",
                format!("this machine's provisioned Signed Release Root (version {}) delegates no `{ROLE}` role", root.version),
                "have the owner's root quorum sign a successor root that delegates the `human-gate` role to the owner's human-gate key(s), and apply it with `gov trust root-update`",
            ));
        };
        let keys: BTreeMap<String, String> = role
            .keyids
            .iter()
            .filter_map(|k| root.keys.get(k).map(|e| (k.clone(), e.public.clone())))
            .collect();
        return Ok(Anchor {
            source: "srr-root",
            version: root.version,
            digest: root.envelope.file_sha256.clone(),
            threshold: role.threshold,
            key_ids: role.keyids.clone(),
            keys,
            root: Some(root),
        });
    }
    if !standalone_allowed {
        // P2-ADJ-0001: no release root means no human channel. Typed and observable, with the one remediation.
        let present = standalone_anchor_path()
            .map(|p| p.exists())
            .unwrap_or(false);
        let mut e = unavailable(
            "UNPROVISIONED",
            format!(
                "this machine holds no Signed Release Root, and human answers derive only from a provisioned root's `{ROLE}` delegation (HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned is false{})",
                if present { "; the standalone human-channel anchor present in machine state is not honoured" } else { "" }
            ),
            "provision this machine: the administrator installs a Signed Release Root whose `human-gate` role delegates the product owner's key(s) (`gov trust provision --anchor <root.json>`); a dev/test machine provisions a throw-away root (OWNER-DECISION-P2-0002)",
        );
        e.details["provision_command"] = json!(PROVISION_COMMAND);
        e.details["standalone_anchor_present"] = json!(present);
        e.details["policy"] =
            json!("HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned");
        return Err(e);
    }
    let path = standalone_anchor_path()?;
    if !path.exists() {
        return Err(unavailable(
            "NO_ANCHOR",
            format!("no human-channel anchor is provisioned ({} is absent)", path.display()),
            "the administrator installs the owner's public human-gate keys with `gov trust human-channel --provision <anchor.json>` (a self-signed `human-channel-anchor` document from the administrator domain), or provisions a Signed Release Root delegating `human-gate`",
        ));
    }
    let env = Envelope::read(&path)?;
    parse_standalone(env, None)
}

/// Parse and self-verify a standalone anchor. `now` = `Some(clock)` also checks expiry (provisioning).
fn parse_standalone(env: Envelope, now: Option<&str>) -> Result<Anchor> {
    let s = &env.signed;
    let bad = |m: String| {
        GovError::new(
            "HUMAN_CHANNEL_ANCHOR_INVALID",
            format!("{}: {m}", env.source),
        )
    };
    if env.typ() != ANCHOR_TYPE {
        return Err(bad(format!(
            "expected _type '{ANCHOR_TYPE}', found '{}'",
            env.typ()
        )));
    }
    if env.spec_version() != crate::srr::metadata::SPEC_VERSION {
        return Err(bad(format!(
            "unsupported spec_version '{}'",
            env.spec_version()
        )));
    }
    if env.product() != FRAMEWORK_NAME {
        return Err(bad(format!(
            "binds product '{}', not '{FRAMEWORK_NAME}'",
            env.product()
        )));
    }
    let mut keys = BTreeMap::new();
    for (id, k) in s
        .get("keys")
        .and_then(|v| v.as_object())
        .cloned()
        .unwrap_or_default()
    {
        let public = k["keyval"]["public"].as_str().unwrap_or("").to_string();
        if k["keytype"].as_str() != Some(crate::srr::crypto::KEYTYPE)
            || k["scheme"].as_str() != Some(crate::srr::crypto::SCHEME)
        {
            return Err(bad(format!(
                "key {id} is not {}/{}",
                crate::srr::crypto::KEYTYPE,
                crate::srr::crypto::SCHEME
            )));
        }
        if crate::srr::crypto::keyid(&public)? != id {
            return Err(bad(format!(
                "key id {id} does not match SHA-256 of its public key"
            )));
        }
        keys.insert(id, public);
    }
    let threshold = s.get("threshold").and_then(|v| v.as_u64()).unwrap_or(0) as usize;
    if keys.is_empty() || threshold == 0 || threshold > keys.len() {
        return Err(bad(format!(
            "needs at least one key and a threshold within 1..={} (found {threshold})",
            keys.len()
        )));
    }
    if let Some(now) = now {
        if let Some(f) = env.expiry_fault(now) {
            return Err(bad(f));
        }
    }
    let a = Anchor {
        source: "standalone",
        version: env.version(),
        digest: env.file_sha256.clone(),
        threshold,
        key_ids: keys.keys().cloned().collect(),
        keys,
        root: None,
    };
    // proof of possession: the anchor is signed, at threshold, by the keys it installs
    a.verify_signatures(&env)
        .map_err(|e| bad(format!("not self-signed at threshold: {}", e.message)))?;
    Ok(a)
}

/// **Administrator action**: install the standalone human-channel anchor (the owner's public `human-gate` keys).
///
/// Refused below floor (it is a trust-policy mutation: `OWNER-DECISION-0006` §6 bullet 4), for an anchor file that is
/// repository content (ARCH-0003 §5, the same rule `gov trust provision` applies to a Signed Release Root), on a
/// machine that holds a Signed Release Root (the root's delegation governs there), and when an anchor already exists
/// (the product never re-anchors; replacing it is an administrator-domain action outside the product).
///
/// `standalone_allowed` is `HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned`; while it is false
/// (the kernel default, P2-ADJ-0001) provisioning is refused `HUMAN_CHANNEL_STANDALONE_DISABLED`: an anchor that
/// would never be honoured is not installed, and the remediation is to provision a Signed Release Root.
pub fn provision_standalone(
    file: &Path,
    project_root: Option<&Path>,
    standalone_allowed: bool,
) -> Result<Value> {
    crate::srr::breakglass::guard_effect(
        crate::srr::breakglass::Effect::TrustPolicyMutation,
        "trust human-channel provision",
    )?;
    if !standalone_allowed {
        return Err(GovError::new(
            "HUMAN_CHANNEL_STANDALONE_DISABLED",
            format!("a standalone human-channel anchor is not a source of Human Gate authority: HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned is false (P2-ADJ-0001; OWNER-DECISION-P2-0002 \"provision, then work\"). Human answers derive from a provisioned Signed Release Root's `{ROLE}` delegation. Remediation: provision this machine ({PROVISION_COMMAND}) with a root whose `{ROLE}` role delegates the product owner's key(s); a dev/test machine provisions a throw-away root."),
        )
        .with_details(json!({"cause": "STANDALONE_ANCHOR_DISABLED", "policy": "HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned", "remediation": "provision a Signed Release Root that delegates the `human-gate` role", "provision_command": PROVISION_COMMAND})));
    }
    refuse_repository_sourced_anchor(file, project_root)?;
    let ms = crate::srr::state::MachineState::open()?;
    let now = crate::srr::metadata::local_clock_now();
    if let Some(root) = crate::srr::verifier::trusted_root(&ms, &now)? {
        return Err(GovError::new(
            "HUMAN_CHANNEL_SRR_GOVERNS",
            format!("this machine holds a Signed Release Root (version {}); human-gate keys are delegated by that root's `{ROLE}` role, and a standalone anchor would be ignored. Delegate the role through a root successor instead.", root.version),
        ));
    }
    let dest = standalone_anchor_path()?;
    if dest.exists() {
        return Err(GovError::new(
            "HUMAN_CHANNEL_ALREADY_PROVISIONED",
            format!("a human-channel anchor is already installed at {}; the product never replaces it (an agent must not be able to re-anchor the channel). Replacing it is an administrator-domain action.", dest.display()),
        ));
    }
    let bytes =
        std::fs::read(file).map_err(|e| GovError::io(&format!("read {}", file.display()), e))?;
    let env = Envelope::parse(&bytes, &file.display().to_string())?;
    let a = parse_standalone(env, Some(&now))?;
    let dir = dest.parent().expect("anchor has a parent").to_path_buf();
    std::fs::create_dir_all(&dir)
        .map_err(|e| GovError::io(&format!("mkdir {}", dir.display()), e))?;
    let tmp = dir.join(format!(".anchor.{}.tmp", std::process::id()));
    std::fs::write(&tmp, &bytes)
        .map_err(|e| GovError::io(&format!("write {}", tmp.display()), e))?;
    std::fs::rename(&tmp, &dest)
        .map_err(|e| GovError::io(&format!("install {}", dest.display()), e))?;
    crate::srr::state::fsync_dir(&dir);
    Ok(
        json!({"provisioned": true, "anchor": a.describe(), "path": dest.display().to_string(), "provisioned_at": now_iso()}),
    )
}

/// ARCH-0003 §5 / OWNER-DIRECTIVE-0004: a verification anchor comes from the administrator installation boundary,
/// never from repository content. Mirrors the rule `srr::provision` applies to a Signed Release Root (that helper is
/// private to `srr/**`, which this workstream does not edit): a file inside the governed project, or under any `.git`
/// or `governance` directory, is refused.
fn refuse_repository_sourced_anchor(file: &Path, project_root: Option<&Path>) -> Result<()> {
    let abs = file.canonicalize().unwrap_or_else(|_| file.to_path_buf());
    let refuse = |why: String| {
        GovError::new(
            "HUMAN_CHANNEL_ANCHOR_FROM_REPOSITORY_REFUSED",
            format!("{} {why}. The human-channel anchor comes from the platform/administrator installation boundary, never from repository content (ARCH-0003 §5, OWNER-DIRECTIVE-0004).", abs.display()),
        )
        .with_details(json!({"anchor_file": abs.display().to_string()}))
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

/// Whether `path` can be written by the invoking account (the premise check reported by [`status`]).
fn writable_by_invoker(path: &Path) -> Option<bool> {
    let meta = std::fs::metadata(path).ok()?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::MetadataExt;
        let uid = unsafe { libc::geteuid() };
        if uid == 0 {
            return Some(true);
        }
        let mode = meta.mode();
        return Some(
            (meta.uid() == uid && mode & 0o200 != 0) || mode & 0o002 != 0 || (mode & 0o020 != 0),
        );
    }
    #[allow(unreachable_code)]
    Some(!meta.permissions().readonly())
}

/// `gov trust human-channel`: the anchor, where answers go, what they must bind, and the premise check.
pub fn status(standalone_allowed: bool) -> Result<Value> {
    let a = anchor(standalone_allowed);
    let dir = channel_dir()?;
    let anchor_file = match &a {
        Ok(x) if x.source == "srr-root" => crate::srr::state::MachineState::open()
            .ok()
            .map(|m| m.trust_dir()),
        _ => standalone_anchor_path().ok(),
    };
    Ok(json!({
        "available": a.is_ok(),
        "anchor": a.as_ref().map(|x| x.describe()).unwrap_or(Value::Null),
        "unavailable_reason": a.as_ref().err().map(|e| json!({"code": e.code, "message": e.message})),
        "inbox": dir.join("inbox").display().to_string(),
        "outbox": dir.join("outbox").display().to_string(),
        "answer_document": {
            "_type": ANSWER_TYPE, "spec_version": crate::srr::metadata::SPEC_VERSION, "product": FRAMEWORK_NAME,
            "binds": ["gate", "gate_instance", "package_sha256", "option", "answered_by", "nonce", "issued", "expires"],
            "optional": ["rationale"],
            "signature": format!("ed25519 over the exact bytes of the `signed` member, by the `{ROLE}` role's keys at threshold"),
        },
        "receipt_document": {"_type": RECEIPT_TYPE, "binds": ["gate", "gate_instance", "package_sha256", "acknowledged_by", "nonce", "issued", "expires"]},
        "premise": {
            "statement": "ARCH-0003 §1: the administrator boundary is uncompromised; the owner's private key is never on this machine.",
            "anchor_path": anchor_file.as_ref().map(|p| p.display().to_string()),
            "anchor_writable_by_invoking_account": anchor_file.as_deref().and_then(writable_by_invoker),
            "note": "true means the invoking account (and any agent running as it) could replace the verification anchor: the administrator boundary is then not separating agents from the administrator on this machine.",
        },
        "standalone_anchor_permitted_by_policy": standalone_allowed,
        "cannot_produce_an_answer": ["CLI arguments (--by, --option, --role human)", "environment variables (GOV_ROLE, GOV_HUMAN_GATE_APPROVED)", "role claims (a declared L5 role carries no authority)", "defaults", "repository files", "plugins", "model output"],
    }))
}

// ------------------------------------------------------------------------------------------------ documents

/// What a signed document must bind to be an answer to (or receipt for) one rendered gate.
#[derive(Debug, Clone)]
pub struct Expected {
    pub gate: String,
    pub gate_instance: String,
    pub package_sha256: String,
    pub options: Vec<String>,
}

impl Expected {
    pub fn to_value(&self) -> Value {
        json!({"product": FRAMEWORK_NAME, "gate": self.gate, "gate_instance": self.gate_instance, "package_sha256": self.package_sha256, "options": self.options})
    }
}

/// A verified owner-signed document (answer or receipt).
#[derive(Debug, Clone)]
pub struct Signed {
    pub doc_type: String,
    pub option: Option<String>,
    pub by: String,
    pub rationale: Option<String>,
    pub nonce: String,
    pub issued: String,
    pub expires: String,
    pub key_ids: Vec<String>,
    pub envelope_hex: String,
    pub envelope_sha256: String,
    pub anchor: Value,
    pub source: Option<PathBuf>,
}

impl Signed {
    /// The evidence stored in the gate record (and re-verified at every use).
    pub fn evidence(&self) -> Value {
        json!({
            "channel": "HC-1 owner-signed",
            "document_type": self.doc_type,
            "signed_by_key_ids": self.key_ids,
            "anchor": self.anchor,
            "nonce": self.nonce,
            "issued": self.issued,
            "expires": self.expires,
            "envelope_sha256": self.envelope_sha256,
            "envelope_hex": self.envelope_hex,
            "verified_at": now_iso(),
        })
    }
}

fn str_of(v: &Value, k: &str) -> String {
    v.get(k).and_then(|x| x.as_str()).unwrap_or("").to_string()
}

/// Verify one signed document against `anchor` and `exp`. `now = Some(clock)` is the decide-time check (expiry
/// enforced); `None` is use-time re-verification of stored evidence (the answer was already applied while valid).
pub fn verify_document(
    anchor: &Anchor,
    bytes: &[u8],
    source: &str,
    doc_type: &str,
    exp: &Expected,
    now: Option<&str>,
) -> Result<Signed> {
    let env = Envelope::parse(bytes, source)?;
    let rej = |m: String| GovError::new("HUMAN_ANSWER_REJECTED", format!("{source}: {m}"));
    if env.typ() != doc_type {
        return Err(rej(format!(
            "expected _type '{doc_type}', found '{}'",
            env.typ()
        )));
    }
    if env.spec_version() != crate::srr::metadata::SPEC_VERSION {
        return Err(rej(format!(
            "unsupported spec_version '{}'",
            env.spec_version()
        )));
    }
    let key_ids = anchor.verify_signatures(&env).map_err(|e| {
        rej(format!(
            "not signed by the `{ROLE}` authority: {}",
            e.message
        ))
    })?;
    let s = &env.signed;
    if str_of(s, "product") != FRAMEWORK_NAME {
        return Err(rej(format!(
            "binds product '{}', not '{FRAMEWORK_NAME}'",
            str_of(s, "product")
        )));
    }
    for (k, want) in [
        ("gate", &exp.gate),
        ("gate_instance", &exp.gate_instance),
        ("package_sha256", &exp.package_sha256),
    ] {
        if &str_of(s, k) != want {
            return Err(rej(format!("binds {k} '{}', this gate's is '{want}' (a signed document authorises exactly the package it names)", str_of(s, k))));
        }
    }
    let by_field = if doc_type == ANSWER_TYPE {
        "answered_by"
    } else {
        "acknowledged_by"
    };
    let by = str_of(s, by_field);
    let nonce = str_of(s, "nonce");
    if by.trim().is_empty() || nonce.trim().is_empty() {
        return Err(rej(format!("must bind non-empty '{by_field}' and 'nonce'")));
    }
    let option = if doc_type == ANSWER_TYPE {
        let o = str_of(s, "option");
        if !exp.options.contains(&o) {
            return Err(rej(format!(
                "answers option '{o}', which the package does not offer (offered: {:?})",
                exp.options
            )));
        }
        Some(o)
    } else {
        None
    };
    if let Some(now) = now {
        if let Some(f) = env.expiry_fault(now) {
            return Err(rej(f));
        }
    }
    Ok(Signed {
        doc_type: doc_type.to_string(),
        option,
        by,
        rationale: s
            .get("rationale")
            .and_then(|v| v.as_str())
            .map(|x| x.to_string())
            .filter(|x| !x.is_empty()),
        nonce,
        issued: str_of(s, "issued"),
        expires: env.expires().to_string(),
        key_ids,
        envelope_hex: hex::encode(bytes),
        envelope_sha256: sha256_hex(bytes),
        anchor: anchor.describe(),
        source: None,
    })
}

fn consumed_marker(nonce: &str) -> Result<PathBuf> {
    Ok(consumed_dir()?.join(format!("{}.json", &sha256_text(nonce)[..32])))
}

/// Find and verify the owner-signed document of `doc_type` for `exp`: the explicit file if given, else the inbox.
/// Documents for other gates in the inbox are left alone; documents for this gate that fail are reported.
pub fn find(
    anchor: &Anchor,
    doc_type: &str,
    exp: &Expected,
    explicit: Option<&Path>,
) -> Result<Signed> {
    let now = crate::srr::metadata::local_clock_now();
    let inbox = inbox_dir()?;
    let candidates: Vec<PathBuf> = match explicit {
        Some(f) => vec![f.to_path_buf()],
        None => {
            let mut v: Vec<PathBuf> = std::fs::read_dir(&inbox)
                .map(|rd| {
                    rd.filter_map(|e| e.ok())
                        .map(|e| e.path())
                        .filter(|p| {
                            p.is_file() && p.extension().map(|x| x == "json").unwrap_or(false)
                        })
                        .collect()
                })
                .unwrap_or_default();
            v.sort();
            v
        }
    };
    let mut rejected: Vec<Value> = vec![];
    for path in candidates {
        let Ok(bytes) = std::fs::read(&path) else {
            rejected.push(json!({"path": path.display().to_string(), "reason": "unreadable"}));
            continue;
        };
        if explicit.is_none() {
            // only consider inbox documents that claim this gate; the rest belong to other gates
            let claims_this = Envelope::parse(&bytes, "inbox")
                .map(|e| str_of(&e.signed, "gate") == exp.gate && e.typ() == doc_type)
                .unwrap_or(false);
            if !claims_this {
                continue;
            }
        }
        match verify_document(
            anchor,
            &bytes,
            &path.display().to_string(),
            doc_type,
            exp,
            Some(&now),
        ) {
            Ok(mut s) => {
                if consumed_marker(&s.nonce)?.exists() {
                    rejected.push(json!({"path": path.display().to_string(), "reason": "nonce already consumed (a signed document is single-use)"}));
                    continue;
                }
                s.source = Some(path.clone());
                return Ok(s);
            }
            Err(e) => {
                rejected.push(json!({"path": path.display().to_string(), "reason": e.message}))
            }
        }
    }
    let what = if doc_type == ANSWER_TYPE {
        "answer"
    } else {
        "presentation receipt"
    };
    Err(GovError::new(
        if doc_type == ANSWER_TYPE { "HUMAN_ANSWER_UNAUTHENTICATED" } else { "HUMAN_RECEIPT_UNAUTHENTICATED" },
        format!(
            "no valid owner-signed {what} for {} was found ({} rejected). A human {what} is an `{doc_type}` document signed by the `{ROLE}` authority ({} anchor), binding gate {}, gate_instance {}, package_sha256 {}{}; place it in {} (or pass --answer-file). CLI flags, roles, environment and repository files cannot stand in for it.",
            exp.gate,
            rejected.len(),
            anchor.source,
            exp.gate,
            exp.gate_instance,
            exp.package_sha256,
            if doc_type == ANSWER_TYPE { format!(" and one of the options {:?}", exp.options) } else { String::new() },
            inbox.display()
        ),
    )
    .with_details(json!({"expected": exp.to_value(), "anchor": anchor.describe(), "inbox": inbox.display().to_string(), "rejected": rejected})))
}

/// Mark a verified document spent (single use) and remove it from the inbox. Called after the gate record that
/// carries its evidence has been written.
pub fn consume(s: &Signed, gate: &str) -> Result<()> {
    let marker = consumed_marker(&s.nonce)?;
    crate::srr::state::write_durable(
        &marker,
        &json!({"nonce_sha256": sha256_text(&s.nonce), "gate": gate, "document_type": s.doc_type, "envelope_sha256": s.envelope_sha256, "consumed_at": now_iso()}),
    )?;
    if let (Some(src), Ok(inbox)) = (&s.source, inbox_dir()) {
        if src.starts_with(&inbox) {
            let _ = std::fs::remove_file(src);
        }
    }
    Ok(())
}

/// **Use-time re-verification** of stored evidence: the signature against the *current* anchor and the binding to
/// `exp` (and `option`, for answers). Expiry and single use are decide-time properties and are not re-checked.
pub fn reverify(
    anchor: &Anchor,
    evidence: &Value,
    doc_type: &str,
    exp: &Expected,
    option: Option<&str>,
) -> Result<Signed> {
    let hexed = evidence
        .get("envelope_hex")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    let bytes = hex::decode(hexed).map_err(|_| {
        GovError::new(
            "HUMAN_ANSWER_UNVERIFIED",
            "the stored human evidence carries no decodable signed envelope",
        )
    })?;
    let s =
        verify_document(anchor, &bytes, "stored evidence", doc_type, exp, None).map_err(|e| {
            GovError::new(
                "HUMAN_ANSWER_UNVERIFIED",
                format!("stored human evidence no longer verifies: {}", e.message),
            )
            .with_details(e.details)
        })?;
    if let Some(o) = option {
        if s.option.as_deref() != Some(o) {
            return Err(GovError::new(
                "HUMAN_ANSWER_UNVERIFIED",
                format!(
                    "the recorded option '{o}' is not the option the owner signed ({:?})",
                    s.option
                ),
            ));
        }
    }
    Ok(s)
}

/// Write the rendered package into the outbox (the exact bytes whose SHA-256 the owner signs over).
pub fn write_outbox(gate: &str, instance: &str, package_bytes: &[u8]) -> Result<PathBuf> {
    let dir = outbox_dir()?;
    std::fs::create_dir_all(&dir)
        .map_err(|e| GovError::io(&format!("mkdir {}", dir.display()), e))?;
    let p = dir.join(format!(
        "{gate}-{}.json",
        &instance[..instance.len().min(12)]
    ));
    std::fs::write(&p, package_bytes)
        .map_err(|e| GovError::io(&format!("write {}", p.display()), e))?;
    Ok(p)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// P2-ADJ-0001: the kernel compiled into this binary keeps the standalone anchor off, and the strengthen-only
    /// precedence rule allows only `false` as an override.
    #[test]
    fn the_embedded_kernel_keeps_the_standalone_anchor_off() {
        assert!(!standalone_allowed_by_embedded_kernel());
        let prec = crate::policy_precedence::embedded().expect("embedded precedence rules");
        let key = "human_channel.standalone_anchor_when_unprovisioned";
        let kernel = json!(false);
        assert!(crate::policy_precedence::evaluate(
            &prec,
            "HUMAN_GATE_POLICY",
            key,
            Some(&kernel),
            &json!(true),
            false
        )
        .is_err());
        assert!(crate::policy_precedence::evaluate(
            &prec,
            "HUMAN_GATE_POLICY",
            key,
            Some(&kernel),
            &json!(false),
            false
        )
        .is_ok());
        // a kernel that predates the key (no kernel value) cannot be switched on by a project either
        assert!(crate::policy_precedence::evaluate(
            &prec,
            "HUMAN_GATE_POLICY",
            key,
            None,
            &json!(true),
            false
        )
        .is_err());
    }
}
