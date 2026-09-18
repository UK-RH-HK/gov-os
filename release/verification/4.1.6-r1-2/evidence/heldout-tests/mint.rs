//! HELD-OUT VERIFICATION MATERIAL — AR-0029 (verifier-b), R1 verification iteration 2.
//!
//! An independent minting harness for Signed Release Root v1 metadata, written from my own reading of
//! `runtime/src/srr/metadata.rs`. It shares no line with AR-0027's `forge.rs` and does not reuse the builder's
//! `tests/certification/srr_material.rs`.
//!
//! The one capability here that the product deliberately lacks is SIGNING (`SRR-R0-L4`).
#![allow(dead_code)]

use ed25519_dalek::{Signer, SigningKey};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};

pub const PRODUCT: &str = "agentic-engineering-os";
pub const SPEC: &str = "srr/1";

pub fn digest(bytes: &[u8]) -> String {
    let mut h = Sha256::new();
    h.update(bytes);
    hex::encode(h.finalize())
}

/// A signing identity. `id` is the SHA-256 of the raw public key, which is how the product derives key ids.
pub struct Signer1 {
    sk: SigningKey,
    pub public: String,
    pub id: String,
}

impl Signer1 {
    pub fn seeded(seed: u8) -> Signer1 {
        let sk = SigningKey::from_bytes(&[seed; 32]);
        let raw = sk.verifying_key().to_bytes();
        Signer1 {
            sk,
            public: hex::encode(raw),
            id: digest(&raw),
        }
    }
    pub fn sign_hex(&self, msg: &[u8]) -> String {
        hex::encode(self.sk.sign(msg).to_bytes())
    }
}

/// Wrap an exact `signed` byte-string in an envelope signed by each of `signers`.
///
/// The `signed` text is emitted verbatim — the product verifies the raw bytes of the `signed` member, so the
/// harness must control them exactly.
pub fn envelope(signed_text: &str, signers: &[&Signer1]) -> String {
    let sigs: Vec<String> = signers
        .iter()
        .map(|s| {
            format!(
                r#"{{"keyid":"{}","sig":"{}"}}"#,
                s.id,
                s.sign_hex(signed_text.as_bytes())
            )
        })
        .collect();
    format!(
        r#"{{"signed":{signed_text},"signatures":[{}]}}"#,
        sigs.join(",")
    )
}

/// The `signed` text of a root document delegating every required role plus `recovery` to one key.
///
/// `version` and `expires` are the two fields the succession and expiry rules turn on.
pub fn root_signed_text(version: u64, expires: &str, holder: &Signer1) -> String {
    let roles = ["root", "release", "snapshot", "timestamp", "recovery"]
        .iter()
        .map(|r| format!(r#""{r}":{{"keyids":["{}"],"threshold":1}}"#, holder.id))
        .collect::<Vec<_>>()
        .join(",");
    format!(
        r#"{{"_type":"root","spec_version":"{SPEC}","product":"{PRODUCT}","version":{version},"expires":"{expires}","keys":{{"{kid}":{{"keytype":"ed25519","scheme":"ed25519","keyval":{{"public":"{pub}"}}}}}},"roles":{{{roles}}}}}"#,
        kid = holder.id,
        r#pub = holder.public,
    )
}

/// A complete root envelope self-signed by its own quorum.
pub fn root_document(version: u64, expires: &str, holder: &Signer1) -> String {
    let text = root_signed_text(version, expires, holder);
    envelope(&text, &[holder])
}

/// A successor root: signed by BOTH the outgoing quorum (succession authority) and its own incoming quorum.
pub fn successor_root(version: u64, expires: &str, outgoing: &Signer1, incoming: &Signer1) -> String {
    let text = root_signed_text(version, expires, incoming);
    envelope(&text, &[outgoing, incoming])
}

// ------------------------------------------------------------------------------- machine-state scaffolding

/// A throwaway protected-state root for one scenario.
pub struct Machine {
    pub home: PathBuf,
    pub state_root: PathBuf,
}

pub fn scenario(tag: &str) -> Machine {
    let base = std::env::temp_dir().join(format!(
        "ar0029-{tag}-{}-{}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    ));
    let state_root = base.join("state").join("governance-os").join("machine");
    std::fs::create_dir_all(&state_root).unwrap();
    Machine {
        home: base,
        state_root,
    }
}

impl Machine {
    pub fn open(&self) -> gov_runtime::srr::state::MachineState {
        gov_runtime::srr::state::MachineState::at(&self.state_root).unwrap()
    }
    /// Point the process-global protected-state resolution at this scenario. Callers must serialise
    /// (`--test-threads=1`); every test binary here does.
    pub fn activate(&self) {
        for k in [
            "GOV_BREAK_GLASS",
            "GOV_BREAKGLASS",
            "GOV_TRUST_OVERRIDE",
            "GOV_SKIP_VERIFY",
            "GOV_ALLOW_UNSIGNED",
            "GOV_RELEASE_AUTHORITY",
            "GOV_HUMAN_GATE_APPROVED",
            "GOV_FLOOR_OVERRIDE",
            "GOV_MINIMUM_SECURE_RELEASE",
            "GOV_MACHINE_STATE_DIR",
        ] {
            std::env::remove_var(k);
        }
        std::env::set_var("XDG_STATE_HOME", self.home.join("state"));
        std::env::set_var("HOME", &self.home);
    }
    /// Anchor this machine on `root_text`, exactly as `gov trust provision` would leave it.
    pub fn provision_with(&self, root_text: &str) {
        let ms = self.open();
        let env = gov_runtime::srr::metadata::Envelope::parse(root_text.as_bytes(), "mint").unwrap();
        let root = gov_runtime::srr::metadata::Root::parse(env).unwrap();
        ms.set_root_metadata(root_text.as_bytes(), root.version, &root.product)
            .unwrap();
    }
    /// Write the `DEGRADED — RECOVERY ONLY` marking record for `product`.
    ///
    /// These are the exact members `breakglass::read_marking` and `breakglass::Degraded::load` consult, in the
    /// shape `breakglass::enter` writes them. Minting the marking directly — rather than driving a signed
    /// break-glass entry — is deliberate: it isolates the §6 guard from the §2 authority path, which AR-0027
    /// already exercised end to end and which this suite re-confirms separately.
    pub fn mark_degraded(&self, product: &str) {
        let ms = self.open();
        let rec = serde_json::json!({
            "active": true,
            "marking": gov_runtime::srr::breakglass::DEGRADED_TOKEN,
            "entered_at": "2026-09-18T00:00:00Z",
            "product": product,
            "machine_id": ms.machine_id,
            "ingress": "rollback",
            "reason": "AR-0029 held-out scenario",
        });
        gov_runtime::srr::state::write_durable(&ms.degraded_path(product), &rec).unwrap();
    }
    /// Replace the marking record with bytes that are not a readable marking record.
    pub fn corrupt_marking(&self, product: &str, bytes: &[u8]) {
        let ms = self.open();
        let p = ms.degraded_path(product);
        std::fs::create_dir_all(p.parent().unwrap()).unwrap();
        std::fs::write(&p, bytes).unwrap();
    }
    pub fn marking_path(&self, product: &str) -> PathBuf {
        self.open().degraded_path(product)
    }
}

pub fn write(p: &Path, text: &str) {
    if let Some(d) = p.parent() {
        std::fs::create_dir_all(d).unwrap();
    }
    std::fs::write(p, text).unwrap();
}

/// A canonical UTC instant offset from the product's own clock reading, in the one form the profile emits.
pub fn canonical_year(year: i32) -> String {
    format!("{year:04}-01-01T00:00:00Z")
}
