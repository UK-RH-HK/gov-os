//! # TEST MATERIAL ONLY — Signed Release Root v1 fixture signer
//!
//! **This file is test material. It is compiled only into the certification test binary, never into `gov`.**
//!
//! The `gov` binary contains no signing code and no key material: `gov_runtime::srr::crypto` exposes verification
//! entry points only. Metadata is produced here, by the test harness, so that the shipped product cannot reach a
//! signing path and no "dev/test trust mode" exists to be abused (`SRR-R0-L4`).
//!
//! ## These keys are NOT usable as a production root
//!
//! Every key below is derived from a hard-coded, published 32-byte seed pattern. The private material is therefore
//! public by construction and reproducible by anyone reading this file. It is unfit for any production trust
//! anchor, and `OWNER-DIRECTIVE-0004` / the frozen boundary place production key custody at R2 in any case. No
//! production private key exists in this repository.
#![allow(dead_code)]
use ed25519_dalek::{Signer, SigningKey};
use serde_json::{json, Value};
use std::path::Path;

/// A clearly-marked test key pair.
pub struct TestKey {
    signing: SigningKey,
    pub public_hex: String,
    pub keyid: String,
}

/// Deterministic test key from a published seed byte. NOT A PRODUCTION KEY.
pub fn key(seed: u8) -> TestKey {
    let bytes = [seed; 32];
    let signing = SigningKey::from_bytes(&bytes);
    let public_hex = hex::encode(signing.verifying_key().to_bytes());
    let keyid = gov_runtime::util::sha256_hex(&signing.verifying_key().to_bytes());
    TestKey {
        signing,
        public_hex,
        keyid,
    }
}

/// Build a signed envelope. The signature covers the **exact bytes** of the `signed` member as they are written,
/// which is what the verifier extracts with `serde_json::value::RawValue`.
pub fn envelope(signed: &Value, keys: &[&TestKey]) -> String {
    let signed_bytes = serde_json::to_string(signed).unwrap();
    let sigs: Vec<Value> = keys
        .iter()
        .map(|k| {
            json!({"keyid": k.keyid, "sig": hex::encode(k.signing.sign(signed_bytes.as_bytes()).to_bytes())})
        })
        .collect();
    format!(
        "{{\"signed\":{},\"signatures\":{}}}",
        signed_bytes,
        serde_json::to_string(&sigs).unwrap()
    )
}

/// An envelope whose signature is over different bytes than the `signed` member that will be parsed — the classic
/// "verify one document, act on another" attack. It must fail closed.
pub fn envelope_with_foreign_signature(
    signed: &Value,
    signed_over: &Value,
    keys: &[&TestKey],
) -> String {
    let signed_bytes = serde_json::to_string(signed).unwrap();
    let other = serde_json::to_string(signed_over).unwrap();
    let sigs: Vec<Value> = keys
        .iter()
        .map(|k| json!({"keyid": k.keyid, "sig": hex::encode(k.signing.sign(other.as_bytes()).to_bytes())}))
        .collect();
    format!(
        "{{\"signed\":{},\"signatures\":{}}}",
        signed_bytes,
        serde_json::to_string(&sigs).unwrap()
    )
}

pub fn key_entry(k: &TestKey) -> (String, Value) {
    (
        k.keyid.clone(),
        json!({"keytype": "ed25519", "scheme": "ed25519", "keyval": {"public": k.public_hex}}),
    )
}

pub fn far_future() -> String {
    "2099-01-01T00:00:00Z".into()
}
pub fn past() -> String {
    "2000-01-01T00:00:00Z".into()
}

/// Root metadata with the five roles this profile uses.
#[allow(clippy::too_many_arguments)]
pub fn root_doc(
    version: u64,
    expires: &str,
    root_keys: &[&TestKey],
    root_threshold: usize,
    release_keys: &[&TestKey],
    snapshot_key: &TestKey,
    timestamp_key: &TestKey,
    recovery_key: Option<&TestKey>,
) -> Value {
    let mut keys = serde_json::Map::new();
    for k in root_keys.iter().chain(release_keys.iter()) {
        let (id, v) = key_entry(k);
        keys.insert(id, v);
    }
    for k in [snapshot_key, timestamp_key] {
        let (id, v) = key_entry(k);
        keys.insert(id, v);
    }
    let mut roles = json!({
        "root": {"keyids": root_keys.iter().map(|k| k.keyid.clone()).collect::<Vec<_>>(), "threshold": root_threshold},
        "release": {"keyids": release_keys.iter().map(|k| k.keyid.clone()).collect::<Vec<_>>(), "threshold": 1},
        "snapshot": {"keyids": [snapshot_key.keyid.clone()], "threshold": 1},
        "timestamp": {"keyids": [timestamp_key.keyid.clone()], "threshold": 1},
    });
    if let Some(rk) = recovery_key {
        let (id, v) = key_entry(rk);
        keys.insert(id, v);
        roles["recovery"] = json!({"keyids": [rk.keyid.clone()], "threshold": 1});
    }
    json!({
        "_type": "root", "spec_version": "srr/1", "product": "agentic-engineering-os",
        "version": version, "expires": expires, "keys": Value::Object(keys), "roles": roles,
    })
}

/// Measure a kernel source directory exactly as the verifier's private staging does.
pub fn measure(
    candidate: &Path,
) -> (
    std::collections::BTreeMap<String, String>,
    String,
    String,
    String,
) {
    let tmpd = std::env::temp_dir().join(format!(
        "srr-measure-{}-{}",
        std::process::id(),
        gov_runtime::util::short_uuid()
    ));
    let _ = std::fs::remove_dir_all(&tmpd);
    gov_runtime::kernel::stage_payload(candidate, &tmpd).unwrap();
    let (_, files) = gov_runtime::util::hash_tree(&tmpd, &["KERNEL_MANIFEST.json"]).unwrap();
    let manifest = gov_runtime::kernel::build_manifest(&tmpd).unwrap();
    let payload_hash = gov_runtime::util::hash_value(&serde_json::to_value(&files).unwrap());
    let kmh = gov_runtime::kernel::manifest_hash(&manifest);
    let version = manifest["version"].as_str().unwrap_or("").to_string();
    let _ = std::fs::remove_dir_all(&tmpd);
    (files, payload_hash, kmh, version)
}

/// Release/targets metadata binding an exact payload.
#[allow(clippy::too_many_arguments)]
pub fn release_doc(
    candidate: &Path,
    metadata_version: u64,
    sequence: u64,
    channel: &str,
    expires: &str,
    minimum_secure_release: &str,
    minimum_secure_sequence: u64,
) -> Value {
    let (files, payload_hash, kmh, version) = measure(candidate);
    let migrations: Vec<Value> = gov_runtime::migrations::framework::load_migrations(candidate)
        .iter()
        .map(|m| {
            json!({"id": m["id"], "from_version": m["from_version"], "to_version": m["to_version"],
                   "sha256": gov_runtime::util::sha256_text(&gov_runtime::util::canonical_json(m))})
        })
        .collect();
    let fmap: serde_json::Map<String, Value> = files
        .iter()
        .map(|(p, h)| (p.clone(), json!({"sha256": h})))
        .collect();
    json!({
        "_type": "release", "spec_version": "srr/1", "product": "agentic-engineering-os",
        "repository": "git+ssh://owner/private/agentic-engineering-os",
        "channel": channel, "release_version": version, "sequence": sequence,
        "version": metadata_version, "expires": expires,
        "platforms": ["any"],
        "minimum_secure_release": minimum_secure_release, "minimum_secure_sequence": minimum_secure_sequence,
        "payload": {"payload_hash": payload_hash, "kernel_manifest_hash": kmh, "files": Value::Object(fmap)},
        "migrations": migrations,
        "schema_identities": {},
        "delegations": [],
    })
}

pub fn snapshot_doc(version: u64, expires: &str, release_file: &str) -> Value {
    let bytes = std::fs::read(release_file).unwrap();
    let rel: Value = serde_json::from_slice(&bytes).unwrap();
    json!({
        "_type": "snapshot", "spec_version": "srr/1", "product": "agentic-engineering-os",
        "version": version, "expires": expires,
        "meta": {"release.json": {"version": rel["signed"]["version"], "sha256": gov_runtime::util::sha256_hex(&bytes)}},
    })
}

pub fn timestamp_doc(version: u64, expires: &str, snapshot_file: &str) -> Value {
    let bytes = std::fs::read(snapshot_file).unwrap();
    let snap: Value = serde_json::from_slice(&bytes).unwrap();
    json!({
        "_type": "timestamp", "spec_version": "srr/1", "product": "agentic-engineering-os",
        "version": version, "expires": expires,
        "meta": {"snapshot.json": {"version": snap["signed"]["version"], "sha256": gov_runtime::util::sha256_hex(&bytes)}},
    })
}

#[allow(clippy::too_many_arguments)]
pub fn break_glass_doc(
    machine_id: &str,
    nonce: &str,
    reason: &str,
    expires: &str,
    release_version: &str,
    payload_hash: &str,
    kernel_manifest_hash: &str,
) -> Value {
    json!({
        "_type": "break-glass", "spec_version": "srr/1", "product": "agentic-engineering-os",
        "machine_id": machine_id, "nonce": nonce, "reason": reason,
        "issued": "2026-01-01T00:00:00Z", "expires": expires,
        "recovery_release": {"release_version": release_version, "payload_hash": payload_hash,
                             "kernel_manifest_hash": kernel_manifest_hash},
    })
}

/// Write a complete signed metadata set beside `<release_dir>/kernel`.
pub struct Publisher {
    pub root_a: TestKey,
    pub root_b: TestKey,
    pub root_c: TestKey,
    pub release: TestKey,
    pub snapshot: TestKey,
    pub timestamp: TestKey,
    pub recovery: TestKey,
}

impl Publisher {
    pub fn new() -> Publisher {
        Publisher {
            root_a: key(0x11),
            root_b: key(0x12),
            root_c: key(0x13),
            release: key(0x21),
            snapshot: key(0x31),
            timestamp: key(0x41),
            recovery: key(0x51),
        }
    }

    /// The target root policy of ARCH-0003 §4: three offline root keys at 2-of-3.
    pub fn root_json(&self, version: u64, expires: &str) -> String {
        let doc = root_doc(
            version,
            expires,
            &[&self.root_a, &self.root_b, &self.root_c],
            2,
            &[&self.release],
            &self.snapshot,
            &self.timestamp,
            Some(&self.recovery),
        );
        envelope(&doc, &[&self.root_a, &self.root_b])
    }

    pub fn write_root(&self, dir: &Path, version: u64, expires: &str) -> std::path::PathBuf {
        std::fs::create_dir_all(dir).unwrap();
        let p = dir.join(format!("root-{version}.json"));
        std::fs::write(&p, self.root_json(version, expires)).unwrap();
        p
    }

    /// Re-seal an arbitrary release document into an existing metadata directory, regenerating the snapshot and
    /// timestamp so the chain stays internally consistent.
    pub fn reseal(&self, md: &Path, release: &Value, metadata_version: u64, expires: &str) {
        std::fs::write(md.join("release.json"), envelope(release, &[&self.release])).unwrap();
        let snap = snapshot_doc(
            metadata_version,
            expires,
            md.join("release.json").to_str().unwrap(),
        );
        std::fs::write(md.join("snapshot.json"), envelope(&snap, &[&self.snapshot])).unwrap();
        let ts = timestamp_doc(
            metadata_version,
            expires,
            md.join("snapshot.json").to_str().unwrap(),
        );
        std::fs::write(md.join("timestamp.json"), envelope(&ts, &[&self.timestamp])).unwrap();
    }

    /// Publish release + snapshot + timestamp into `<release_dir>/metadata/`.
    #[allow(clippy::too_many_arguments)]
    pub fn publish(
        &self,
        release_dir: &Path,
        metadata_version: u64,
        sequence: u64,
        channel: &str,
        expires: &str,
        minimum_secure_release: &str,
        minimum_secure_sequence: u64,
    ) -> std::path::PathBuf {
        let md = release_dir.join("metadata");
        std::fs::create_dir_all(&md).unwrap();
        let rel = release_doc(
            &release_dir.join("kernel"),
            metadata_version,
            sequence,
            channel,
            expires,
            minimum_secure_release,
            minimum_secure_sequence,
        );
        std::fs::write(md.join("release.json"), envelope(&rel, &[&self.release])).unwrap();
        let snap = snapshot_doc(
            metadata_version,
            expires,
            md.join("release.json").to_str().unwrap(),
        );
        std::fs::write(md.join("snapshot.json"), envelope(&snap, &[&self.snapshot])).unwrap();
        let ts = timestamp_doc(
            metadata_version,
            expires,
            md.join("snapshot.json").to_str().unwrap(),
        );
        std::fs::write(md.join("timestamp.json"), envelope(&ts, &[&self.timestamp])).unwrap();
        md
    }
}
