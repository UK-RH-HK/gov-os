//! Built-in deterministic baseline embedder (hashed n-gram vectors), bit-identical to the Python reference plugin.
//! Not a neural model: a reproducible lexical-semantic approximation so that semantic routing, fusion, manifests and
//! regression tests are testable offline. Stronger embedders are plugged in via API-0001 and pinned in the manifest.
use regex::Regex;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::sync::OnceLock;

const STOP: &[&str] = &[
    "the", "a", "an", "of", "to", "and", "or", "in", "on", "for", "is", "are", "be", "by", "with",
    "as", "at", "it", "this", "that", "from", "was", "we", "our", "not", "no", "yes", "if", "then",
    "than", "so", "do", "does",
];

fn token_rx() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"[A-Za-z_][A-Za-z0-9_]+|\d+").unwrap())
}
fn camel_rx() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"([a-z0-9])([A-Z])").unwrap())
}

fn split_camel(tok: &str) -> Vec<String> {
    let s = camel_rx()
        .replace_all(tok, "$1 $2")
        .replace('_', " ")
        .to_lowercase();
    let parts: Vec<String> = s.split_whitespace().map(|p| p.to_string()).collect();
    if parts.len() > 1 {
        parts
    } else {
        vec![]
    }
}

pub fn tokenize(text: &str) -> Vec<String> {
    let mut toks = vec![];
    for m in token_rx().find_iter(text) {
        let t = m.as_str();
        let low = t.to_lowercase();
        if STOP.contains(&low.as_str()) {
            continue;
        }
        toks.push(low);
        for p in split_camel(t) {
            if !STOP.contains(&p.as_str()) {
                toks.push(p);
            }
        }
    }
    toks
}

#[derive(Debug, Clone)]
pub struct HashedNgramEmbedder {
    pub dim: usize,
    pub version: String,
}

impl HashedNgramEmbedder {
    pub fn new(dim: usize, version: &str) -> Self {
        HashedNgramEmbedder {
            dim,
            version: version.to_string(),
        }
    }
    pub fn id(&self) -> &'static str {
        "hashed-ngram"
    }
    pub fn embed(&self, text: &str) -> Vec<f64> {
        let toks = tokenize(text);
        let mut counts: BTreeMap<String, u32> = BTreeMap::new();
        for t in &toks {
            *counts.entry(t.clone()).or_insert(0) += 1;
        }
        for w in toks.windows(2) {
            *counts.entry(format!("{}_{}", w[0], w[1])).or_insert(0) += 1;
        }
        let mut vec = vec![0.0f64; self.dim];
        for (f, c) in counts {
            let h = sha1_bytes(f.as_bytes());
            let idx = (u32::from_be_bytes([h[0], h[1], h[2], h[3]]) as usize) % self.dim;
            let sign = if h[4] & 1 == 1 { 1.0 } else { -1.0 };
            let mut w = 1.0 + (c as f64).ln();
            if f.len() > 12 || f.contains('_') {
                w *= 1.3;
            }
            vec[idx] += sign * w;
        }
        let norm = vec.iter().map(|v| v * v).sum::<f64>().sqrt();
        let norm = if norm == 0.0 { 1.0 } else { norm };
        vec.iter().map(|v| round6(v / norm)).collect()
    }
}

fn round6(x: f64) -> f64 {
    (x * 1_000_000.0).round() / 1_000_000.0
}

/// SHA-1 (used only for feature hashing, matching the reference plugin; not for security).
fn sha1_bytes(data: &[u8]) -> [u8; 20] {
    // Minimal SHA-1 implementation (RFC 3174) to stay dependency-light and bit-identical to hashlib.sha1.
    let mut h: [u32; 5] = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0];
    let mut msg = data.to_vec();
    let bit_len = (data.len() as u64) * 8;
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&bit_len.to_be_bytes());
    for chunk in msg.chunks(64) {
        let mut w = [0u32; 80];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                chunk[i * 4],
                chunk[i * 4 + 1],
                chunk[i * 4 + 2],
                chunk[i * 4 + 3],
            ]);
        }
        for i in 16..80 {
            w[i] = (w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]).rotate_left(1);
        }
        let (mut a, mut b, mut c, mut d, mut e) = (h[0], h[1], h[2], h[3], h[4]);
        for (i, wi) in w.iter().enumerate() {
            let (f, k) = match i {
                0..=19 => ((b & c) | ((!b) & d), 0x5A827999),
                20..=39 => (b ^ c ^ d, 0x6ED9EBA1),
                40..=59 => ((b & c) | (b & d) | (c & d), 0x8F1BBCDC),
                _ => (b ^ c ^ d, 0xCA62C1D6),
            };
            let temp = a
                .rotate_left(5)
                .wrapping_add(f)
                .wrapping_add(e)
                .wrapping_add(k)
                .wrapping_add(*wi);
            e = d;
            d = c;
            c = b.rotate_left(30);
            b = a;
            a = temp;
        }
        h[0] = h[0].wrapping_add(a);
        h[1] = h[1].wrapping_add(b);
        h[2] = h[2].wrapping_add(c);
        h[3] = h[3].wrapping_add(d);
        h[4] = h[4].wrapping_add(e);
    }
    let mut out = [0u8; 20];
    for (i, v) in h.iter().enumerate() {
        out[i * 4..i * 4 + 4].copy_from_slice(&v.to_be_bytes());
    }
    out
}

pub fn cosine(a: &[f64], b: &[f64]) -> f64 {
    a.iter().zip(b).map(|(x, y)| x * y).sum()
}

pub fn sha256_short(text: &str) -> String {
    format!("{:x}", Sha256::digest(text.as_bytes()))[..16].to_string()
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn deterministic_unit_vectors() {
        let e = HashedNgramEmbedder::new(64, "1");
        let a = e.embed("Governance OS rebuild memory");
        let b = e.embed("Governance OS rebuild memory");
        assert_eq!(a, b);
        let norm: f64 = a.iter().map(|x| x * x).sum::<f64>().sqrt();
        assert!((norm - 1.0).abs() < 1e-4);
        assert!(
            cosine(&a, &e.embed("rebuild the memory of the governance OS"))
                > cosine(&a, &e.embed("purple elephants dance"))
        );
        assert_eq!(
            tokenize("CamelCaseName the_snake"),
            vec![
                "camelcasename",
                "camel",
                "case",
                "name",
                "the_snake",
                "snake"
            ]
        );
    }
    #[test]
    fn sha1_matches_known_vector() {
        // sha1("abc") = a9993e364706816aba3e25717850c26c9cd0d89d
        let h = sha1_bytes(b"abc");
        assert_eq!(h[..4], [0xa9, 0x99, 0x3e, 0x36]);
    }
}
