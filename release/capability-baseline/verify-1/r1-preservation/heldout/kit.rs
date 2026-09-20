//! P2-AR-0044 held-out harness — my own minting and machine-provisioning kit.
//!
//! Written from the wire format as `runtime/src/srr/metadata.rs` and `runtime/src/srr/binding.rs` define it, so
//! that the material under test is the product's verifier rather than the product's own fixture builder. It shares
//! no line with `tests/certification/srr_material.rs`, nor with AR-0027's `forge.rs`, AR-0029's `mint.rs`,
//! AR-0031's `bench.rs` or AR-0033's `common.rs`.
//!
//! The one capability here that the product deliberately lacks is SIGNING (`SRR-R0-L4`).
#![allow(dead_code)]

use ed25519_dalek::{Signer, SigningKey};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::atomic::{AtomicU64, Ordering};

/// The candidate worktree this crate is compiled against.
pub fn product_root() -> PathBuf {
    let p = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("wt")
        .join("p2-verify1-r1-preservation");
    std::fs::canonicalize(&p).unwrap_or(p)
}

/// The `gov` binary built from the candidate, supplied by RUN-ALL.
pub fn gov_bin() -> PathBuf {
    PathBuf::from(std::env::var("AR0044_GOV_BIN").expect("AR0044_GOV_BIN must point at the candidate `gov`"))
}

static N: AtomicU64 = AtomicU64::new(0);

pub fn scratch(tag: &str) -> PathBuf {
    let n = N.fetch_add(1, Ordering::SeqCst);
    let d = std::env::temp_dir()
        .join("p2ar0044")
        .join(format!("{tag}-{}-{n}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    d
}

pub fn write(p: &Path, s: &str) {
    if let Some(parent) = p.parent() {
        std::fs::create_dir_all(parent).unwrap();
    }
    std::fs::write(p, s).unwrap();
}

pub fn read(p: &Path) -> String {
    std::fs::read_to_string(p).unwrap_or_default()
}

/// Read one product file, relative to the candidate root.
pub fn src(rel: &str) -> String {
    std::fs::read_to_string(product_root().join(rel))
        .unwrap_or_else(|e| panic!("cannot read {rel}: {e}"))
}

pub fn sha256_hex(b: &[u8]) -> String {
    let mut h = Sha256::new();
    h.update(b);
    hex::encode(h.finalize())
}

// ------------------------------------------------------------------------------------------- signing material

/// A deterministic signer. No randomness, so every run mints the same material.
pub fn signer(seed: u8) -> SigningKey {
    SigningKey::from_bytes(&[seed; 32])
}

pub fn pubhex(k: &SigningKey) -> String {
    hex::encode(k.verifying_key().to_bytes())
}

/// The key id this profile uses, derived exactly as `srr::crypto::keyid` does: SHA-256 over the decoded public
/// key bytes. The product refuses any document whose declared id does not derive from the key material it
/// publishes (`SRR_KEYID_MISMATCH`), so a chosen label is not available — which is itself the point.
pub fn kid(k: &SigningKey) -> String {
    sha256_hex(&k.verifying_key().to_bytes())
}

/// Wrap `signed` in the envelope shape `Envelope::parse` accepts, signed by each `(keyid, key)`.
///
/// The signature is over the exact bytes of the `signed` member as they appear in the file, which is why the
/// payload is serialised once and spliced in verbatim.
pub fn envelope(signed: &Value, signers: &[(&str, &SigningKey)]) -> String {
    let payload = serde_json::to_string(signed).unwrap();
    let sigs: Vec<Value> = signers
        .iter()
        .map(|(kid, k)| {
            json!({"keyid": kid, "sig": hex::encode(k.sign(payload.as_bytes()).to_bytes())})
        })
        .collect();
    format!(
        "{{\"signed\":{payload},\"signatures\":{}}}\n",
        serde_json::to_string(&sigs).unwrap()
    )
}

/// A detached signature over the exact serialised `signed` payload, hex-encoded — for forging a signature that
/// is presented under someone else's key id.
pub fn sign_hex(k: &SigningKey, signed: &Value) -> String {
    let payload = serde_json::to_string(signed).unwrap();
    hex::encode(k.sign(payload.as_bytes()).to_bytes())
}

/// An envelope whose signatures are attached verbatim (for forging: wrong sig, lifted sig, ...).
pub fn envelope_raw(signed: &Value, sigs: Vec<Value>) -> String {
    let payload = serde_json::to_string(signed).unwrap();
    format!(
        "{{\"signed\":{payload},\"signatures\":{}}}\n",
        serde_json::to_string(&sigs).unwrap()
    )
}

pub const PRODUCT: &str = gov_runtime::FRAMEWORK_NAME;
pub const SPEC: &str = "srr/1";

/// Far enough out that nothing in this suite expires mid-run.
pub const FAR: &str = "2039-01-01T00:00:00Z";

/// A self-signed root document. `extra_roles` adds delegations beyond `root` itself.
pub fn root_doc(version: u64, root_key: &str, extra_roles: &[(&str, Vec<&str>, usize)], keys: &[(&str, &SigningKey)]) -> Value {
    let mut keytable = serde_json::Map::new();
    for (kid, k) in keys {
        keytable.insert(
            kid.to_string(),
            // TUF-style: the material lives under `keyval.public`, and the map key must equal
            // SHA-256(decoded public), which the product derives rather than trusting.
            json!({"keytype": "ed25519", "scheme": "ed25519", "keyval": {"public": pubhex(k)}}),
        );
    }
    let mut roles = serde_json::Map::new();
    roles.insert(
        "root".into(),
        json!({"keyids": [root_key], "threshold": 1}),
    );
    // `Root::parse` requires root/release/snapshot/timestamp to be delegated, so every minted anchor carries all
    // four. Unless a caller overrides one, they are the root key itself — this suite attacks `t2-binding`.
    for required in ["release", "snapshot", "timestamp"] {
        roles.insert(
            required.into(),
            json!({"keyids": [root_key], "threshold": 1}),
        );
    }
    for (name, kids, threshold) in extra_roles {
        roles.insert(
            name.to_string(),
            json!({"keyids": kids, "threshold": threshold}),
        );
    }
    json!({
        "_type": "root",
        "spec_version": SPEC,
        "product": PRODUCT,
        "version": version,
        "expires": FAR,
        "keys": Value::Object(keytable),
        "roles": Value::Object(roles),
    })
}

/// An owner-signed `t2-binding-authority` document.
pub fn authority_doc(
    authority_id: &str,
    version: u64,
    keys: &[(&[u8], &str)],
    machines: Option<Vec<String>>,
) -> Value {
    let entries: Vec<Value> = keys
        .iter()
        .map(|(k, status)| {
            json!({
                "key_id": gov_runtime::srr::binding::key_id_of(k),
                "commitment": gov_runtime::srr::binding::commitment_of(k),
                "status": status,
            })
        })
        .collect();
    let mut d = json!({
        "_type": "t2-binding-authority",
        "spec_version": SPEC,
        "product": PRODUCT,
        "authority_id": authority_id,
        "version": version,
        "expires": FAR,
        "keys": entries,
    });
    if let Some(m) = machines {
        d["machines"] = json!(m);
    }
    d
}

/// A 32-byte binding key, deterministically.
pub fn binding_key(seed: u8) -> Vec<u8> {
    vec![seed; 32]
}

pub fn key_file_doc(key: &[u8]) -> Value {
    json!({"_type": "t2-binding-key", "key_hex": hex::encode(key)})
}

// --------------------------------------------------------------------------------------------- a whole machine

/// One simulated owner machine: its own protected state root, its own HOME, and a disposable project.
pub struct Machine {
    pub name: String,
    pub home: PathBuf,
    pub state: PathBuf,
    pub admin: PathBuf,
    pub project: PathBuf,
}

impl Machine {
    pub fn new(tag: &str) -> Machine {
        let base = scratch(tag);
        let m = Machine {
            name: tag.to_string(),
            home: base.join("home"),
            state: base.join("machine-state"),
            admin: base.join("admin-domain"),
            project: base.join("project"),
        };
        for d in [&m.home, &m.state, &m.admin, &m.project] {
            std::fs::create_dir_all(d).unwrap();
        }
        m
    }

    /// Run `gov` on this machine. `HOME`/`XDG_STATE_HOME` point at an empty per-machine home, so the *default*
    /// state root is unprovisioned and `GOV_MACHINE_STATE_DIR` is honoured — exactly the ARCH-0003 §8 route an
    /// administrator uses to provision a second machine or a CI runner.
    pub fn gov(&self, args: &[&str]) -> (bool, String, String) {
        let out = Command::new(gov_bin())
            .args(args)
            .current_dir(&self.project)
            .env_clear()
            .env("PATH", std::env::var("PATH").unwrap_or_default())
            .env("HOME", &self.home)
            .env("XDG_STATE_HOME", self.home.join(".local/state"))
            .env("GOV_MACHINE_STATE_DIR", &self.state)
            .output()
            .expect("gov did not run");
        (
            out.status.success(),
            String::from_utf8_lossy(&out.stdout).to_string(),
            String::from_utf8_lossy(&out.stderr).to_string(),
        )
    }

    pub fn gov_json(&self, args: &[&str]) -> (bool, Value) {
        let mut a = args.to_vec();
        a.push("--json");
        let (ok, so, se) = self.gov(&a);
        let v: Value = serde_json::from_str(so.trim())
            .unwrap_or_else(|_| json!({"_unparsed_stdout": so, "_stderr": se}));
        (ok, v)
    }

    /// Point this process's own library calls at this machine's protected state.
    ///
    /// Process-wide: every test that uses it runs under `--test-threads=1`.
    pub fn enter(&self) {
        std::env::set_var("HOME", &self.home);
        std::env::set_var("XDG_STATE_HOME", self.home.join(".local/state"));
        std::env::set_var("GOV_MACHINE_STATE_DIR", &self.state);
    }

    /// Provision this machine with `anchor_bytes` through the product's own provisioning command.
    pub fn provision(&self, anchor_bytes: &str) -> (bool, Value) {
        let a = self.admin.join("root.json");
        write(&a, anchor_bytes);
        self.gov_json(&["trust", "provision", "--anchor", a.to_str().unwrap()])
    }

    pub fn bind(&self, authority: &str, key: &[u8]) -> (bool, Value) {
        let af = self.admin.join("t2-binding-authority.json");
        let kf = self.admin.join("binding-key.json");
        write(&af, authority);
        write(&kf, &(serde_json::to_string_pretty(&key_file_doc(key)).unwrap() + "\n"));
        self.gov_json(&[
            "trust",
            "bind",
            "--authority",
            af.to_str().unwrap(),
            "--key",
            kf.to_str().unwrap(),
        ])
    }

    pub fn is_provisioned(&self) -> bool {
        self.state.join("trust").join("provisioned.json").exists()
    }
}

/// The typed error code a `--json` envelope carries, wherever the product puts it.
pub fn code(v: &Value) -> String {
    for p in [
        v.get("error").and_then(|e| e.get("code")),
        v.get("code"),
        v.get("result").and_then(|r| r.get("code")),
    ]
    .into_iter()
    .flatten()
    {
        if let Some(s) = p.as_str() {
            return s.to_string();
        }
    }
    String::new()
}

/// Everything the envelope says, flattened, for asserting that a refusal names its scope.
pub fn text(v: &Value) -> String {
    serde_json::to_string(v).unwrap_or_default()
}

/// Hex of a binding key, for leak-scanning a repository.
pub fn hex_of(k: &[u8]) -> String {
    hex::encode(k)
}
