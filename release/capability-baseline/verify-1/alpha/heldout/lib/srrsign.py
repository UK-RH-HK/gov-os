"""P2-AR-0046 (verify-1 alpha) — INDEPENDENT Signed-Release-Root metadata producer.

Written by the verifier from the on-disk metadata format (`runtime/src/srr/metadata.rs`,
`runtime/src/srr/binding.rs`, `runtime/src/human_channel.rs`) and NOT from the product's own
`tests/certification/srr_material.rs` test material.  It uses `cryptography`'s ed25519, not
`ed25519-dalek`, so the signature side of every probe is produced by a different implementation
from the one `gov` verifies with.

`gov` verifies and never signs (SRR-R0-L4); this file is the adversary/administrator side.
Nothing here is ever placed in the product tree, and every key is drawn per run into a
throw-away administrator-domain directory outside every repository.
"""
import hashlib
import json
import os
import pathlib
import secrets

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    PrivateFormat,
    NoEncryption,
)

SPEC = "srr/1"
FAR_FUTURE = "2099-01-01T00:00:00Z"
LONG_PAST = "2000-01-01T00:00:00Z"


# ---------------------------------------------------------------- canonicalisation (util.rs)
def canonical_json(v):
    """serde_json::to_string(&sorted(v)) — compact, recursively key-sorted."""
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()


def sha256_text(s):
    return sha256_hex(s.encode("utf-8"))


def hash_value(v):
    return sha256_text(canonical_json(v))


# ---------------------------------------------------------------- keys
class Key:
    def __init__(self, seed=None):
        self.seed = seed if seed is not None else secrets.token_bytes(32)
        self.sk = Ed25519PrivateKey.from_private_bytes(self.seed)
        self.pub = self.sk.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.public_hex = self.pub.hex()
        self.keyid = sha256_hex(self.pub)

    def sign(self, msg: bytes) -> str:
        return self.sk.sign(msg).hex()

    def entry(self):
        return {
            "keytype": "ed25519",
            "scheme": "ed25519",
            "keyval": {"public": self.public_hex},
        }


def envelope(signed_obj, signers):
    """{"signed": <exact bytes>, "signatures": [...]} — signatures cover the exact `signed` bytes."""
    signed_bytes = canonical_json(signed_obj).encode("utf-8")
    sigs = [{"keyid": k.keyid, "sig": k.sign(signed_bytes)} for k in signers]
    body = b'{"signed":' + signed_bytes + b',"signatures":' + json.dumps(sigs).encode() + b"}"
    return body


# ---------------------------------------------------------------- documents
def root_doc(
    version,
    keys_roles,
    product="governance-os",
    expires=FAR_FUTURE,
):
    """keys_roles: {role_name: ([Key,...], threshold)}"""
    keys = {}
    roles = {}
    for role, (ks, threshold) in keys_roles.items():
        for k in ks:
            keys[k.keyid] = k.entry()
        roles[role] = {"keyids": [k.keyid for k in ks], "threshold": threshold}
    return {
        "_type": "root",
        "spec_version": SPEC,
        "product": product,
        "version": version,
        "expires": expires,
        "keys": keys,
        "roles": roles,
    }


def measure_payload(kernel_dir):
    """Reproduce staging's measurement: files map, payload_hash, kernel_manifest_hash, version."""
    kernel_dir = pathlib.Path(kernel_dir)
    manifest = json.loads((kernel_dir / "KERNEL_MANIFEST.json").read_text())
    files = {}
    for p in sorted(kernel_dir.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(kernel_dir)).replace("\\", "/")
        if rel == "KERNEL_MANIFEST.json":
            continue
        files[rel] = sha256_hex(p.read_bytes())
    payload_hash = hash_value(files)
    km = {k: manifest[k] for k in ("framework", "version", "files", "payload_hash") if k in manifest}
    return files, payload_hash, hash_value(km), manifest["version"]


def _yaml_migrations(kernel_dir):
    """Migration identities as the product hashes them: sha256_text(canonical_json(parsed yaml))."""
    import subprocess

    d = pathlib.Path(kernel_dir) / "migrations"
    out = []
    if not d.is_dir():
        return out
    for p in sorted(d.glob("*.yaml")):
        # parse with PyYAML if present; else ask python3 -c via ruamel is unavailable -> use yaml
        import yaml  # type: ignore

        m = yaml.safe_load(p.read_text())
        if not isinstance(m, dict) or "id" not in m:
            continue
        out.append(
            {
                "id": m["id"],
                "from_version": str(m.get("from_version", "")),
                "to_version": str(m.get("to_version", "")),
                "sha256": sha256_text(canonical_json(m)),
            }
        )
    return out


def release_doc(
    kernel_dir,
    sequence,
    version=None,
    product="governance-os",
    repository="governance-os",
    channel="stable",
    expires=FAR_FUTURE,
    minimum_secure_release="",
    minimum_secure_sequence=0,
    certification=None,
    files=None,
    payload_hash=None,
    kernel_manifest_hash=None,
    release_version=None,
    migrations=None,
):
    f, ph, kmh, ver = measure_payload(kernel_dir)
    files = files if files is not None else {k: {"sha256": v} for k, v in f.items()}
    doc = {
        "_type": "release",
        "spec_version": SPEC,
        "product": product,
        "repository": repository,
        "channel": channel,
        "release_version": release_version or ver,
        "sequence": sequence,
        "version": version if version is not None else sequence,
        "expires": expires,
        "platforms": ["any"],
        "minimum_secure_release": minimum_secure_release,
        "minimum_secure_sequence": minimum_secure_sequence,
        "payload": {
            "payload_hash": payload_hash or ph,
            "kernel_manifest_hash": kernel_manifest_hash or kmh,
            "files": files,
        },
        "migrations": migrations if migrations is not None else _yaml_migrations(kernel_dir),
    }
    if certification is not None:
        doc["evidence"] = {"certification": {"status": certification}}
    return doc


def meta_ref(path):
    b = pathlib.Path(path).read_bytes()
    v = json.loads(b)["signed"]["version"]
    return {"version": v, "sha256": sha256_hex(b)}


def snapshot_doc(version, release_path, expires=FAR_FUTURE, product="governance-os"):
    return {
        "_type": "snapshot",
        "spec_version": SPEC,
        "product": product,
        "version": version,
        "expires": expires,
        "meta": {"release.json": meta_ref(release_path)},
    }


def timestamp_doc(version, snapshot_path, expires=FAR_FUTURE, product="governance-os"):
    return {
        "_type": "timestamp",
        "spec_version": SPEC,
        "product": product,
        "version": version,
        "expires": expires,
        "meta": {"snapshot.json": meta_ref(snapshot_path)},
    }


def publish(kernel_dir, meta_dir, pub, sequence, **kw):
    """Write release.json/snapshot.json/timestamp.json for `kernel_dir` into `meta_dir`."""
    meta_dir = pathlib.Path(meta_dir)
    meta_dir.mkdir(parents=True, exist_ok=True)
    rel = release_doc(kernel_dir, sequence, **kw)
    (meta_dir / "release.json").write_bytes(envelope(rel, [pub["release"]]))
    snap = snapshot_doc(sequence, meta_dir / "release.json", product=rel["product"])
    (meta_dir / "snapshot.json").write_bytes(envelope(snap, [pub["snapshot"]]))
    ts = timestamp_doc(sequence, meta_dir / "snapshot.json", product=rel["product"])
    (meta_dir / "timestamp.json").write_bytes(envelope(ts, [pub["timestamp"]]))
    return rel


# ---------------------------------------------------------------- T2 binding authority
def t2_key_id(key: bytes):
    return sha256_hex(b"t2-binding-key-id:" + key)[:16]


def t2_commitment(key: bytes):
    return sha256_hex(b"t2-binding-key-commitment:" + key)


def binding_authority_doc(
    authority_id,
    version,
    keys,
    machines=None,
    expires=FAR_FUTURE,
    product="governance-os",
    owner="verify-1-alpha owner",
):
    """keys: [(raw 32 bytes, 'active'|'retired')]"""
    return {
        "_type": "t2-binding-authority",
        "spec_version": SPEC,
        "product": product,
        "owner": owner,
        "authority_id": authority_id,
        "version": version,
        "expires": expires,
        "machines": machines,
        "keys": [
            {"key_id": t2_key_id(k), "commitment": t2_commitment(k), "status": s}
            for k, s in keys
        ],
    }


def write_binding_key(path, key: bytes):
    pathlib.Path(path).write_text(
        json.dumps({"_type": "t2-binding-key", "key_hex": key.hex()}) + "\n"
    )


# ---------------------------------------------------------------- break-glass
def break_glass_doc(
    machine_id,
    nonce,
    reason,
    release_version,
    payload_hash,
    kernel_manifest_hash,
    expires=FAR_FUTURE,
    product="governance-os",
    issued="2026-09-20T00:00:00Z",
):
    return {
        "_type": "break-glass",
        "spec_version": SPEC,
        "product": product,
        "machine_id": machine_id,
        "nonce": nonce,
        "reason": reason,
        "issued": issued,
        "expires": expires,
        "recovery_release": {
            "release_version": release_version,
            "payload_hash": payload_hash,
            "kernel_manifest_hash": kernel_manifest_hash,
        },
    }


def new_publisher(root_keys=3, threshold=2, extra_roles=None):
    """A throw-away publisher: root quorum + release/snapshot/timestamp/recovery/human-gate/t2-binding."""
    pub = {
        "root": [Key() for _ in range(root_keys)],
        "release": Key(),
        "snapshot": Key(),
        "timestamp": Key(),
        "recovery": Key(),
        "human-gate": Key(),
        "t2-binding": Key(),
    }
    pub["_threshold"] = threshold
    if extra_roles:
        for r in extra_roles:
            pub[r] = Key()
    return pub


def publisher_root(pub, version=1, product="governance-os", expires=FAR_FUTURE, omit_roles=()):
    roles = {
        "root": (pub["root"], pub["_threshold"]),
        "release": ([pub["release"]], 1),
        "snapshot": ([pub["snapshot"]], 1),
        "timestamp": ([pub["timestamp"]], 1),
        "recovery": ([pub["recovery"]], 1),
        "human-gate": ([pub["human-gate"]], 1),
        "t2-binding": ([pub["t2-binding"]], 1),
    }
    for r in omit_roles:
        roles.pop(r, None)
    return root_doc(version, roles, product=product, expires=expires)


def write_root(pub, path, version=1, signers=None, **kw):
    doc = publisher_root(pub, version=version, **kw)
    signers = signers if signers is not None else pub["root"][: pub["_threshold"]]
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_bytes(envelope(doc, signers))
    return doc


# ---------------------------------------------------------------- owner-signed human answers
def human_answer_doc(gate, gate_instance, package_sha256, option, answered_by, nonce,
                     product="agentic-engineering-os", expires=FAR_FUTURE,
                     issued="2026-09-20T00:00:00Z", rationale=None, doc_type="human-gate-answer"):
    d = {
        "_type": doc_type,
        "spec_version": SPEC,
        "product": product,
        "gate": gate,
        "gate_instance": gate_instance,
        "package_sha256": package_sha256,
        "nonce": nonce,
        "issued": issued,
        "expires": expires,
    }
    if doc_type == "human-gate-answer":
        d["option"] = option
        d["answered_by"] = answered_by
        if rationale:
            d["rationale"] = rationale
    else:
        d["acknowledged_by"] = answered_by
    return d
