//! # The T2 binding primitive (BC-P2-09)
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
//! HMAC-SHA256 over the record's canonical content, the operation name and the time, keyed by a **machine binding
//! key** that lives in protected machine state outside every repository (`<state_root>/t2-binding/key.json`,
//! created on first use, mode 0600). The seal is stored in the record itself (field [`SEAL_FIELD`]) so it travels
//! with the record and needs no sidecar store. [`verify_record`] recomputes it:
//!
//! | [`Binding`] | meaning | honoured? |
//! |---|---|---|
//! | `Verified` | written by a `gov` operation on this machine and unmodified since | yes |
//! | `Unsealed` | no seal: hand-written, legacy, or written by code that has not adopted the primitive | **no** |
//! | `Broken` | sealed here, then modified (any field, including a single flag) | **no** |
//! | `Foreign` | sealed by another machine's key (a clone): not verifiable here | **no** |
//! | `KeyUnavailable` | this machine has no binding key / its state root cannot be resolved | **no** |
//!
//! Consumers never read a T2 field for a decision without first asking this module; everything that is not
//! `Verified` is reported, typed and refused ([`require_verified`], `T2_UNBOUND`).
//!
//! ## What it proves, and what it does not (stated, not overclaimed)
//!
//! * A process that can write the repository but cannot read the machine's protected state cannot produce a
//!   `Verified` record: hand-written gate answers, decisions and registry entries are detected (A0-E1-02's
//!   lower-role worker, A0-L3-02's record forgery). This is the attack in the findings.
//! * A process running with the **operator's full OS privileges** can read the machine key (same account) and could
//!   compute a seal. Against that attacker this primitive is detection-grade, not proof; the facts that must hold
//!   against it — human answers and human-approval assertions — are additionally bound to an **owner signature**
//!   the machine does not hold ([`crate::human_channel`]), which such a process cannot produce.
//! * A process can always *run `gov`* under a declared role; what it writes that way is an OS operation performed
//!   under that role's authority and is recorded as such (the agent-identity question is OD-P2-01, out of scope).
//! * Cross-machine: a record sealed on machine A is `Foreign` on machine B and is not honoured there. Owner-signed
//!   human evidence remains verifiable on any machine anchored to the same owner keys.
//!
//! ## API for other workstreams
//!
//! * writers of T2 state: [`seal_record`] / [`seal_value`] immediately before persisting (e.g. `records::save_record`
//!   callers for CIT state, the plugin registry writer);
//! * consumers: [`verify_record`] / [`verify_value`] / [`verify_file`] and [`require_verified`];
//! * task close (G2 mutation scope): [`classify_path`] — a changed path under an OS-managed prefix is an OS write only
//!   when it is `Verified`; otherwise it is a worker mutation to be refused, not exempted;
//! * suite / doctor: [`audit`] lists every open T2 record that no OS operation produced.
use crate::records::{Record, RecordFormat, RecordStore};
use crate::util::{canonical_json, now_iso, sha256_hex};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

/// The field that carries the seal inside a sealed record or JSON document.
pub const SEAL_FIELD: &str = "os_binding";
/// Seal algorithm identifier (bound into the MAC).
pub const SEAL_ALG: &str = "hmac-sha256/t2-v1";
const KEY_DIR: &str = "t2-binding";
const KEY_FILE: &str = "key.json";

/// Record types every instance of which is T2 state written only by OS operations (checked by [`audit`]).
pub const SEALED_RECORD_TYPES: &[&str] = &["human-gate"];

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
    KeyUnavailable {
        reason: String,
    },
}

impl Binding {
    pub fn is_verified(&self) -> bool {
        matches!(self, Binding::Verified { .. })
    }
    pub fn code(&self) -> &'static str {
        match self {
            Binding::Verified { .. } => "VERIFIED",
            Binding::Unsealed => "UNSEALED",
            Binding::Broken { .. } => "BROKEN",
            Binding::Foreign { .. } => "FOREIGN",
            Binding::KeyUnavailable { .. } => "KEY_UNAVAILABLE",
        }
    }
    pub fn to_value(&self) -> Value {
        match self {
            Binding::Verified {
                key_id,
                operation,
                at,
            } => json!({"binding": "VERIFIED", "key_id": key_id, "operation": operation, "at": at}),
            Binding::Unsealed => {
                json!({"binding": "UNSEALED", "reason": "no OS seal: the record was not written by a gov operation (hand-written, legacy, or written by a writer that has not adopted the T2 primitive)"})
            }
            Binding::Broken { reason } => json!({"binding": "BROKEN", "reason": reason}),
            Binding::Foreign { key_id } => {
                json!({"binding": "FOREIGN", "key_id": key_id, "reason": "sealed by another machine's binding key; not verifiable on this machine"})
            }
            Binding::KeyUnavailable { reason } => {
                json!({"binding": "KEY_UNAVAILABLE", "reason": reason})
            }
        }
    }
}

// ------------------------------------------------------------------------------------------------- the key

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

/// The id of this machine's binding key, if one exists (never creates one).
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

// ------------------------------------------------------------------------------------------------ seal / verify

/// Seal `data` (a record's data or a JSON document) as written by the OS operation `operation`. Call it
/// immediately before persisting; any later modification of any field breaks the seal.
pub fn seal_value(data: &mut Value, body: &str, operation: &str) -> Result<()> {
    let key = load_or_create_key()?;
    seal_with(&key, data, body, operation)
}

fn seal_with(key: &BindingKey, data: &mut Value, body: &str, operation: &str) -> Result<()> {
    if !data.is_object() {
        return Err(GovError::new(
            "USAGE",
            "only a JSON/YAML object can carry a T2 seal",
        ));
    }
    let at = now_iso();
    let content = canonical_content(data, body)?;
    let mac = hex::encode(hmac_sha256(
        &key.key,
        &mac_message(&key.id, operation, &at, &content),
    ));
    data[SEAL_FIELD] =
        json!({"alg": SEAL_ALG, "key_id": key.id, "operation": operation, "at": at, "mac": mac});
    Ok(())
}

/// Seal a record as written by `operation` (see [`seal_value`]).
pub fn seal_record(rec: &mut Record, operation: &str) -> Result<()> {
    let body = if rec.format == RecordFormat::Md {
        rec.body.clone()
    } else {
        String::new()
    };
    seal_value(&mut rec.data, &body, operation)
}

/// Verify the seal on `data` against this machine's binding key.
pub fn verify_value(data: &Value, body: &str) -> Binding {
    if data.get(SEAL_FIELD).filter(|v| !v.is_null()).is_none() {
        return Binding::Unsealed;
    }
    match load_key() {
        Ok(Some(k)) => verify_with(&k, data, body),
        Ok(None) => Binding::KeyUnavailable {
            reason: "this machine holds no T2 binding key, so no record sealed anywhere can be verified here"
                .into(),
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

/// Verify a record's seal.
pub fn verify_record(rec: &Record) -> Binding {
    let body = if rec.format == RecordFormat::Md {
        rec.body.as_str()
    } else {
        ""
    };
    verify_value(&rec.data, body)
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
            "{id} ({path}) cannot establish {what}: it is T2 state that no gov operation on this machine produced as it stands (binding {}). D-0007 rule 2: such a record is a request, recorded and ignored. Restore it from version control, or withdraw and re-raise it through gov.",
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

/// Every T2 record in the project that no OS operation produced as it stands: all records of
/// [`SEALED_RECORD_TYPES`], and every decision that asserts `human_approved: true` or derives from a gate.
/// For the governance suite and doctor (WS-2): each entry is a finding.
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
    out
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
        seal_with(&key, &mut rec.data, "", "gate answer").unwrap();
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
}
