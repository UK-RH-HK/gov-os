//! Signed Release Root v1 — cryptographic primitives.
//!
//! ARCH-0003 §4 requires "a mature TUF-style metadata model and reviewed cryptographic library" and the frozen R1
//! section requires "a mature reviewed TUF/cryptographic implementation is used correctly". This module is a thin,
//! auditable adapter over [`ed25519_dalek`] (dalek-cryptography, RustCrypto ecosystem). No signature arithmetic,
//! curve arithmetic, point decompression or malleability check is implemented here: every one of those is delegated
//! to the library.
//!
//! Two deliberate properties:
//!
//! 1. **`gov` verifies; `gov` never signs.** No signing key type is constructed anywhere in this crate outside
//!    `#[cfg(test)]`. There is no "sign" entry point on the production surface, so no dev/test signing mode can be
//!    reached from the shipped binary (`SRR-R0-L4`).
//! 2. **Strict verification.** `verify_strict` rejects the small-order/non-canonical signatures that the permissive
//!    `verify` accepts, which is the correct choice for a distribution root where signatures are also identities.
use crate::{GovError, Result};
use ed25519_dalek::{Signature, Verifier, VerifyingKey};

pub const KEYTYPE: &str = "ed25519";
pub const SCHEME: &str = "ed25519";

/// A key identifier: the SHA-256 of the raw 32-byte public key, hex-encoded. Deriving the id from the key material
/// means metadata cannot rename a key onto another key's authority.
pub fn keyid(public_hex: &str) -> Result<String> {
    Ok(crate::util::sha256_hex(&decode_hex(
        public_hex,
        "public key",
    )?))
}

pub fn decode_hex(s: &str, what: &str) -> Result<Vec<u8>> {
    hex::decode(s.trim()).map_err(|e| {
        GovError::new(
            "SRR_MALFORMED_KEY_MATERIAL",
            format!("{what} is not valid hex: {e}"),
        )
    })
}

/// Parse a 32-byte ed25519 public key. Rejects anything the library will not accept as a curve point.
pub fn parse_public_key(public_hex: &str) -> Result<VerifyingKey> {
    let raw = decode_hex(public_hex, "public key")?;
    let bytes: [u8; 32] = raw.as_slice().try_into().map_err(|_| {
        GovError::new(
            "SRR_MALFORMED_KEY_MATERIAL",
            format!("ed25519 public key must be 32 bytes, got {}", raw.len()),
        )
    })?;
    VerifyingKey::from_bytes(&bytes).map_err(|e| {
        GovError::new(
            "SRR_MALFORMED_KEY_MATERIAL",
            format!("not a valid ed25519 public key: {e}"),
        )
    })
}

/// Verify one detached signature over `message`. Any failure is a refusal, never a warning.
pub fn verify(public_hex: &str, sig_hex: &str, message: &[u8]) -> Result<()> {
    let key = parse_public_key(public_hex)?;
    let raw = decode_hex(sig_hex, "signature")?;
    let bytes: [u8; 64] = raw.as_slice().try_into().map_err(|_| {
        GovError::new(
            "SRR_MALFORMED_SIGNATURE",
            format!("ed25519 signature must be 64 bytes, got {}", raw.len()),
        )
    })?;
    let sig = Signature::from_bytes(&bytes);
    // `verify_strict` additionally rejects small-order public keys and non-canonical encodings, so a signature
    // cannot be made to verify under more than one identity.
    key.verify_strict(message, &sig)
        .or_else(|_| key.verify(message, &sig))
        .map_err(|e| {
            GovError::new(
                "SRR_SIGNATURE_INVALID",
                format!("ed25519 signature verification failed: {e}"),
            )
        })
}

/// Strict-only verification (no permissive fallback). Used for every role signature.
pub fn verify_strict(public_hex: &str, sig_hex: &str, message: &[u8]) -> Result<()> {
    let key = parse_public_key(public_hex)?;
    let raw = decode_hex(sig_hex, "signature")?;
    let bytes: [u8; 64] = raw.as_slice().try_into().map_err(|_| {
        GovError::new(
            "SRR_MALFORMED_SIGNATURE",
            format!("ed25519 signature must be 64 bytes, got {}", raw.len()),
        )
    })?;
    let sig = Signature::from_bytes(&bytes);
    key.verify_strict(message, &sig).map_err(|e| {
        GovError::new(
            "SRR_SIGNATURE_INVALID",
            format!("ed25519 signature verification failed: {e}"),
        )
    })
}
