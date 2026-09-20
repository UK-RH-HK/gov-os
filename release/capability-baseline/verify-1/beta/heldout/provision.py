#!/usr/bin/env python3
"""P2-AR-0047 held-out throw-away Signed Release Root publisher (VERIFIER TEST MATERIAL ONLY).

Why this exists: OWNER-DECISION-P2-0002 makes "provision, then install" the documented first-run path, and several
Contract v3 obligations this verifier must establish (C7 episodic close records, D5's governed profile change, the
reindex/regression route AC-7 §9.1 names) are only reachable on a provisioned machine with a green governance record.
`gov` contains no signing code (SRR-R0-L4), so the administrator-domain material is produced here, outside the product,
exactly as the product's own verifier reads it.

Every key here is derived from a seed drawn at run time and written only under the run's scratch directory. Nothing
here is a production key, and none of it enters the product tree.

Usage:
    provision.py publish  <canonical_worktree> <release_out_dir> <admin_dir> [sequence]
    provision.py answer   <admin_dir> <gate_package_json> <option> <out_file>
"""
import hashlib
import json
import os
import secrets
import subprocess
import sys

import yaml
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

FAR_FUTURE = "2099-01-01T00:00:00Z"
PRODUCT = "agentic-engineering-os"


# --------------------------------------------------------------------------------------------- canonical encoding
def sort_v(v):
    if isinstance(v, dict):
        return {k: sort_v(v[k]) for k in sorted(v)}
    if isinstance(v, list):
        return [sort_v(x) for x in v]
    return v


def canonical(v):
    """`gov_runtime::util::canonical_json`: serde_json compact encoding of the key-sorted value."""
    return json.dumps(sort_v(v), separators=(",", ":"), ensure_ascii=False)


def hash_value(v):
    return hashlib.sha256(canonical(v).encode()).hexdigest()


def compact(v):
    """`serde_json::to_string` of a value in its declared order (what a signature covers)."""
    return json.dumps(v, separators=(",", ":"), ensure_ascii=False)


# --------------------------------------------------------------------------------------------------------- keys
class Key:
    def __init__(self, seed=None):
        self.sk = Ed25519PrivateKey.from_private_bytes(seed or secrets.token_bytes(32))
        pub = self.sk.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.public_hex = pub.hex()
        self.keyid = hashlib.sha256(pub).hexdigest()

    def entry(self):
        return self.keyid, {"keytype": "ed25519", "scheme": "ed25519",
                            "keyval": {"public": self.public_hex}}

    def sign(self, data: bytes):
        return self.sk.sign(data).hex()


def envelope(signed, keys):
    body = compact(signed)
    sigs = [{"keyid": k.keyid, "sig": k.sign(body.encode())} for k in keys]
    return '{"signed":%s,"signatures":%s}' % (body, compact(sigs))


# ------------------------------------------------------------------------------------------------- measurement
def measure(kernel_dir):
    files = {}
    for root, _dirs, fs in os.walk(kernel_dir):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, kernel_dir).replace("\\", "/")
            if rel == "KERNEL_MANIFEST.json":
                continue
            files[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    km = json.load(open(os.path.join(kernel_dir, "KERNEL_MANIFEST.json")))
    sub = {k: km[k] for k in ["framework", "version", "files", "payload_hash"] if k in km}
    return files, hash_value(files), hash_value(sub), km["version"]


def migrations_of(kernel_dir):
    d = os.path.join(kernel_dir, "migrations")
    out = []
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        if not name.endswith(".yaml"):
            continue
        m = yaml.safe_load(open(os.path.join(d, name)))
        if not isinstance(m, dict) or "id" not in m:
            continue
        out.append({"id": m["id"], "from_version": m.get("from_version"),
                    "to_version": m.get("to_version"),
                    "sha256": hashlib.sha256(canonical(m).encode()).hexdigest()})
    return out


# ------------------------------------------------------------------------------------------------------ publish
def publish(canonical_wt, out_dir, admin_dir, sequence):
    os.makedirs(admin_dir, exist_ok=True)
    names = ["root_a", "root_b", "root_c", "release", "snapshot", "timestamp", "recovery", "owner", "t2"]
    keys = {n: Key() for n in names}
    # the release payload is built by the product itself, so what is signed is what `gov` would install
    gov = os.path.join(canonical_wt, "target", "release", "gov")
    subprocess.run([gov, "--json", "release", "build", "--version", "4.1.6", "--out", out_dir,
                    "--canonical", canonical_wt], check=True, capture_output=True)
    rel_dir = os.path.join(out_dir, "releases", "4.1.6")
    kernel = os.path.join(rel_dir, "kernel")
    files, payload_hash, kmh, version = measure(kernel)

    key_map = {}
    for n in names:
        kid, ent = keys[n].entry()
        key_map[kid] = ent
    root = {
        "_type": "root", "spec_version": "srr/1", "product": PRODUCT,
        "version": 1, "expires": FAR_FUTURE, "keys": key_map,
        "roles": {
            "root": {"keyids": [keys[n].keyid for n in ["root_a", "root_b", "root_c"]], "threshold": 2},
            "release": {"keyids": [keys["release"].keyid], "threshold": 1},
            "snapshot": {"keyids": [keys["snapshot"].keyid], "threshold": 1},
            "timestamp": {"keyids": [keys["timestamp"].keyid], "threshold": 1},
            "recovery": {"keyids": [keys["recovery"].keyid], "threshold": 1},
            "human-gate": {"keyids": [keys["owner"].keyid], "threshold": 1},
            # P2-ADJ-0002: the owner's T2 binding authority is delegated from the same root, so a fact one of the
            # owner's provisioned machines seals is honoured on the others.
            "t2-binding": {"keyids": [keys["t2"].keyid], "threshold": 1},
        },
    }
    root_path = os.path.join(admin_dir, "root-1.json")
    open(root_path, "w").write(envelope(root, [keys["root_a"], keys["root_b"]]))

    release = {
        "_type": "release", "spec_version": "srr/1", "product": PRODUCT,
        "repository": "git+ssh://verifier/p2-ar-0047-heldout",
        "channel": "verification", "release_version": version, "sequence": sequence,
        "version": 1, "expires": FAR_FUTURE, "platforms": ["any"],
        "minimum_secure_release": "4.1.0", "minimum_secure_sequence": 0,
        "payload": {"payload_hash": payload_hash, "kernel_manifest_hash": kmh,
                    "files": {p: {"sha256": h} for p, h in sorted(files.items())}},
        "migrations": migrations_of(kernel), "schema_identities": {}, "delegations": [],
    }
    md = os.path.join(rel_dir, "metadata")
    os.makedirs(md, exist_ok=True)
    open(os.path.join(md, "release.json"), "w").write(envelope(release, [keys["release"]]))
    rel_bytes = open(os.path.join(md, "release.json"), "rb").read()
    snapshot = {"_type": "snapshot", "spec_version": "srr/1", "product": PRODUCT,
                "version": 1, "expires": FAR_FUTURE,
                "meta": {"release.json": {"version": 1,
                                          "sha256": hashlib.sha256(rel_bytes).hexdigest()}}}
    open(os.path.join(md, "snapshot.json"), "w").write(envelope(snapshot, [keys["snapshot"]]))
    snap_bytes = open(os.path.join(md, "snapshot.json"), "rb").read()
    ts = {"_type": "timestamp", "spec_version": "srr/1", "product": PRODUCT,
          "version": 1, "expires": FAR_FUTURE,
          "meta": {"snapshot.json": {"version": 1,
                                     "sha256": hashlib.sha256(snap_bytes).hexdigest()}}}
    open(os.path.join(md, "timestamp.json"), "w").write(envelope(ts, [keys["timestamp"]]))

    # the owner's T2 binding authority and the binding key it authorises (administrator domain only)
    binding_key = secrets.token_bytes(32)
    key_id = hashlib.sha256(b"t2-binding-key-id:" + binding_key).hexdigest()[:16]
    commitment = hashlib.sha256(b"t2-binding-key-commitment:" + binding_key).hexdigest()
    authority = {
        "_type": "t2-binding-authority", "spec_version": "srr/1", "product": PRODUCT,
        "authority_id": "p2-ar-0047-heldout-binding", "owner": "product-owner",
        "version": 1, "expires": FAR_FUTURE,
        "keys": [{"key_id": key_id, "commitment": commitment, "status": "active"}],
        "machines": None,
    }
    open(os.path.join(admin_dir, "t2-binding-authority.json"), "w").write(
        envelope(authority, [keys["t2"]]))
    json.dump({"_type": "t2-binding-key", "key_id": key_id, "key_hex": binding_key.hex()},
              open(os.path.join(admin_dir, "t2-binding-key.json"), "w"))

    # the owner's private key stays in the administrator domain, outside every project
    open(os.path.join(admin_dir, "owner.key"), "w").write(
        keys["owner"].sk.private_bytes_raw().hex())
    print(json.dumps({"root": root_path, "release_dir": rel_dir, "metadata": md,
                      "payload_hash": payload_hash, "kernel_manifest_hash": kmh,
                      "owner_keyid": keys["owner"].keyid,
                      "t2_binding_authority": os.path.join(admin_dir, "t2-binding-authority.json"),
                      "t2_binding_key": os.path.join(admin_dir, "t2-binding-key.json")}))


# ------------------------------------------------------------------------------------------------- gate answers
def answer(admin_dir, package_file, option, out_file):
    """Produce an owner-signed `human-gate-answer` for the gate package the product rendered.

    `package_file` is the output of `gov gate present <gate>`: the gate id, its OS-issued instance and the SHA-256 of
    the exact package rendered are read from it, never invented."""
    pkg = json.load(open(package_file))
    pkg = pkg.get("result", pkg)
    pkg = pkg.get("gate", pkg)
    sk = Ed25519PrivateKey.from_private_bytes(
        bytes.fromhex(open(os.path.join(admin_dir, "owner.key")).read().strip()))
    key = Key.__new__(Key)
    key.sk = sk
    pub = sk.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    key.public_hex, key.keyid = pub.hex(), hashlib.sha256(pub).hexdigest()
    signed = {
        "_type": "human-gate-answer", "spec_version": "srr/1", "product": PRODUCT,
        "gate": pkg.get("id") or pkg["gate"], "gate_instance": pkg["gate_instance"],
        "package_sha256": pkg["package_sha256"], "option": option,
        "answered_by": "product-owner",
        "nonce": secrets.token_hex(16), "issued": "2026-01-01T00:00:00Z", "expires": FAR_FUTURE,
    }
    open(out_file, "w").write(envelope(signed, [key]))
    print(out_file)


if __name__ == "__main__":
    if sys.argv[1] == "publish":
        publish(sys.argv[2], sys.argv[3], sys.argv[4],
                int(sys.argv[5]) if len(sys.argv) > 5 else 100)
    elif sys.argv[1] == "answer":
        answer(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        raise SystemExit("usage: publish | answer")
