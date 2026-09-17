//! HELD-OUT VERIFICATION MATERIAL — AR-0027 (verifier-a), independent R1 candidate verification.
//!
//! Authored by the fresh independent verifier. The builder has not seen this file. It deliberately does NOT reuse
//! `tests/certification/srr_material.rs`, so the attack material is constructed from an independent reading of the
//! wire format rather than inheriting the builder's assumptions about it.
//!
//! The one capability here that the product deliberately lacks is SIGNING: to attack a signature-verification
//! adapter you must be able to forge, so this crate carries `ed25519-dalek` with the signing feature. The product
//! binary does not (`SRR-R0-L4`).
#![allow(dead_code)]

use ed25519_dalek::{Signer, SigningKey};
use sha2::{Digest, Sha256};

pub const PRODUCT: &str = "agentic-engineering-os";
pub const SPEC: &str = "srr/1";

pub struct Key {
    pub sk: SigningKey,
    pub public_hex: String,
    pub keyid: String,
}

pub fn key(seed_byte: u8) -> Key {
    let sk = SigningKey::from_bytes(&[seed_byte; 32]);
    let public_hex = hex::encode(sk.verifying_key().to_bytes());
    let keyid = sha256_hex(&sk.verifying_key().to_bytes());
    Key { sk, public_hex, keyid }
}

pub fn sha256_hex(b: &[u8]) -> String {
    let mut h = Sha256::new();
    h.update(b);
    hex::encode(h.finalize())
}

/// Build an envelope with EXACT control over the bytes of the `signed` member.
///
/// `signed_text` is emitted verbatim, so the harness can present byte-strings a re-serialising producer could not,
/// which is the whole point of attacking a "we sign the raw bytes" design.
pub fn envelope_from_text(signed_text: &str, sigs: &[(String, String)]) -> String {
    let sig_items: Vec<String> = sigs
        .iter()
        .map(|(kid, s)| format!(r#"{{"keyid":"{kid}","sig":"{s}"}}"#))
        .collect();
    format!(
        r#"{{"signed":{signed_text},"signatures":[{}]}}"#,
        sig_items.join(",")
    )
}

/// Sign the exact bytes of `signed_text` with each key.
pub fn sign_text(signed_text: &str, keys: &[&Key]) -> Vec<(String, String)> {
    keys.iter()
        .map(|k| {
            let sig = k.sk.sign(signed_text.as_bytes());
            (k.keyid.clone(), hex::encode(sig.to_bytes()))
        })
        .collect()
}

pub fn signed_envelope(signed_text: &str, keys: &[&Key]) -> String {
    let sigs = sign_text(signed_text, keys);
    envelope_from_text(signed_text, &sigs)
}

/// A root document delegating root/release/snapshot/timestamp (+ optional recovery).
pub struct RootSpec<'a> {
    pub version: u64,
    pub expires: &'a str,
    pub product: &'a str,
    pub root_keys: Vec<&'a Key>,
    pub root_threshold: usize,
    pub release_keys: Vec<&'a Key>,
    pub release_threshold: usize,
    pub snapshot_keys: Vec<&'a Key>,
    pub timestamp_keys: Vec<&'a Key>,
    pub recovery_keys: Vec<&'a Key>,
}

impl<'a> RootSpec<'a> {
    pub fn simple(root: &'a Key, rel: &'a Key, snap: &'a Key, ts: &'a Key, rec: &'a Key) -> Self {
        RootSpec {
            version: 1,
            expires: "2099-01-01T00:00:00Z",
            product: PRODUCT,
            root_keys: vec![root],
            root_threshold: 1,
            release_keys: vec![rel],
            release_threshold: 1,
            snapshot_keys: vec![snap],
            timestamp_keys: vec![ts],
            recovery_keys: vec![rec],
        }
    }

    /// The `signed` text for this root. Key ids are derived from key material, as the implementation requires.
    pub fn signed_text(&self) -> String {
        let mut all: Vec<&Key> = vec![];
        for g in [
            &self.root_keys,
            &self.release_keys,
            &self.snapshot_keys,
            &self.timestamp_keys,
            &self.recovery_keys,
        ] {
            for k in g.iter() {
                if !all.iter().any(|x| x.keyid == k.keyid) {
                    all.push(k);
                }
            }
        }
        let keys: Vec<String> = all
            .iter()
            .map(|k| {
                format!(
                    r#""{}":{{"keytype":"ed25519","scheme":"ed25519","keyval":{{"public":"{}"}}}}"#,
                    k.keyid, k.public_hex
                )
            })
            .collect();
        let role = |name: &str, ks: &Vec<&Key>, th: usize| {
            let ids: Vec<String> = ks.iter().map(|k| format!(r#""{}""#, k.keyid)).collect();
            format!(
                r#""{name}":{{"keyids":[{}],"threshold":{th}}}"#,
                ids.join(",")
            )
        };
        let mut roles = vec![
            role("root", &self.root_keys, self.root_threshold),
            role("release", &self.release_keys, self.release_threshold),
            role("snapshot", &self.snapshot_keys, 1),
            role("timestamp", &self.timestamp_keys, 1),
        ];
        if !self.recovery_keys.is_empty() {
            roles.push(role("recovery", &self.recovery_keys, 1));
        }
        format!(
            r#"{{"_type":"root","spec_version":"{SPEC}","version":{},"expires":"{}","product":"{}","keys":{{{}}},"roles":{{{}}}}}"#,
            self.version,
            self.expires,
            self.product,
            keys.join(","),
            roles.join(",")
        )
    }

    pub fn file(&self) -> String {
        let text = self.signed_text();
        signed_envelope(&text, &self.root_keys)
    }
}

/// Parameters for a release document.
pub struct ReleaseSpec<'a> {
    pub version: u64,
    pub expires: &'a str,
    pub release_version: &'a str,
    pub sequence: u64,
    pub channel: &'a str,
    pub repository: &'a str,
    pub payload_hash: &'a str,
    pub kernel_manifest_hash: &'a str,
    pub files: &'a std::collections::BTreeMap<String, String>,
    pub minimum_secure_release: &'a str,
    pub minimum_secure_sequence: u64,
}

impl<'a> ReleaseSpec<'a> {
    pub fn signed_text(&self) -> String {
        let files: Vec<String> = self
            .files
            .iter()
            .map(|(p, h)| format!(r#"{}:{{"sha256":"{}"}}"#, json_str(p), h))
            .collect();
        format!(
            r#"{{"_type":"release","spec_version":"{SPEC}","version":{},"expires":"{}","product":"{PRODUCT}","repository":"{}","channel":"{}","release_version":"{}","sequence":{},"platforms":["any"],"minimum_secure_release":"{}","minimum_secure_sequence":{},"payload":{{"payload_hash":"{}","kernel_manifest_hash":"{}","files":{{{}}}}},"migrations":[],"delegations":[]}}"#,
            self.version,
            self.expires,
            self.repository,
            self.channel,
            self.release_version,
            self.sequence,
            self.minimum_secure_release,
            self.minimum_secure_sequence,
            self.payload_hash,
            self.kernel_manifest_hash,
            files.join(",")
        )
    }
}

pub fn json_str(s: &str) -> String {
    serde_json::to_string(s).unwrap()
}

/// A break-glass authorisation token.
#[allow(clippy::too_many_arguments)]
pub fn break_glass_text(
    machine_id: &str,
    nonce: &str,
    expires: &str,
    payload_hash: &str,
    kernel_manifest_hash: &str,
    release_version: &str,
) -> String {
    format!(
        r#"{{"_type":"break-glass","spec_version":"{SPEC}","version":1,"expires":"{expires}","product":"{PRODUCT}","machine_id":"{machine_id}","nonce":"{nonce}","reason":"held-out verification AR-0027","issued":"2026-09-17T00:00:00Z","recovery_release":{{"release_version":"{release_version}","payload_hash":"{payload_hash}","kernel_manifest_hash":"{kernel_manifest_hash}"}}}}"#
    )
}
