#!/usr/bin/env python3
"""P2-AR-0049 held-out harness: the verifier's own administrator/owner domain.

TEST MATERIAL ONLY. Every key here is derived from a seed written in this file, so the private material is public by
construction and unusable as any production anchor. `gov` holds no signing key (SRR-R0-L4); this file is the
verifier's independent stand-in for the administrator and the product owner, written from the on-disk metadata
format that `runtime/src/srr/metadata.rs` and `runtime/src/human_channel.rs` parse — not copied from the product's
own test harness signer.

Subcommands
  root      <out.json>                                   throw-away Signed Release Root (all roles)
  bindauth  <out.json> [--machines m1,m2] [--version N] [--retire]  t2-binding authority document
  bindkey   <out.json>                                   the binding key file (administrator domain)
  release   <payload-dir> <out-dir> <sequence>           sign a kernel payload as a release
  answer    <out.json> --gate G --instance I --package-sha S --option O [--nonce N] [--expires E] [--signer owner|other]
  receipt   <out.json> --gate G --instance I --package-sha S [...]
  keyid     prints the human-gate key id
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

PRODUCT = "agentic-engineering-os"
SPEC = "srr/1"
FAR_FUTURE = "2099-01-01T00:00:00Z"


def sk(seed_byte):
    return Ed25519PrivateKey.from_private_bytes(bytes([seed_byte]) * 32)


def pub_raw(k):
    return k.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)


def pub_hex(k):
    return pub_raw(k).hex()


def keyid(k):
    return hashlib.sha256(pub_raw(k)).hexdigest()


def key_entry(k):
    return keyid(k), {
        "keytype": "ed25519",
        "scheme": "ed25519",
        "keyval": {"public": pub_hex(k)},
    }


# ---- the verifier's own key material (seeds chosen here, distinct from the product suite's 0x5a owner key)
ROOT_A, ROOT_B, ROOT_C = sk(0xD1), sk(0xD2), sk(0xD3)
RELEASE, SNAPSHOT, TIMESTAMP, RECOVERY = sk(0xD4), sk(0xD5), sk(0xD6), sk(0xD7)
OWNER = sk(0xDA)          # the product owner's `human-gate` key
BINDING_ROLE = sk(0xDB)   # the owner's `t2-binding` role key
OTHER = sk(0xEE)          # a key the root delegates nothing to (wrong-signer attacks)
BINDING_KEY = bytes([0xBC]) * 32  # the symmetric T2 binding key the machine holds


def envelope(signed, signers):
    """The signature covers the exact bytes of the `signed` member as written."""
    signed_bytes = json.dumps(signed, separators=(",", ":")).encode()
    sigs = [{"keyid": keyid(s), "sig": s.sign(signed_bytes).hex()} for s in signers]
    return (
        b'{"signed":' + signed_bytes + b',"signatures":' +
        json.dumps(sigs, separators=(",", ":")).encode() + b"}"
    )


def root_doc(version=1, expires=FAR_FUTURE):
    keys = {}
    for k in (ROOT_A, ROOT_B, ROOT_C, RELEASE, SNAPSHOT, TIMESTAMP, RECOVERY, OWNER, BINDING_ROLE):
        i, e = key_entry(k)
        keys[i] = e
    roles = {
        "root": {"keyids": [keyid(ROOT_A), keyid(ROOT_B), keyid(ROOT_C)], "threshold": 2},
        "release": {"keyids": [keyid(RELEASE)], "threshold": 1},
        "snapshot": {"keyids": [keyid(SNAPSHOT)], "threshold": 1},
        "timestamp": {"keyids": [keyid(TIMESTAMP)], "threshold": 1},
        "recovery": {"keyids": [keyid(RECOVERY)], "threshold": 1},
        "human-gate": {"keyids": [keyid(OWNER)], "threshold": 1},
        "t2-binding": {"keyids": [keyid(BINDING_ROLE)], "threshold": 1},
    }
    return {
        "_type": "root", "spec_version": SPEC, "product": PRODUCT,
        "version": version, "expires": expires, "keys": keys, "roles": roles,
    }


def binding_key_id(key=BINDING_KEY):
    return hashlib.sha256(b"t2-binding-key-id:" + key).hexdigest()[:16]


def binding_commitment(key=BINDING_KEY):
    return hashlib.sha256(b"t2-binding-key-commitment:" + key).hexdigest()


def binding_authority(version=1, machines=None, retired=False, expires=FAR_FUTURE):
    doc = {
        "_type": "t2-binding-authority", "spec_version": SPEC, "product": PRODUCT,
        "authority_id": "verify1-delta-owner", "owner": "P2-AR-0049 held-out owner (test material)",
        "version": version, "expires": expires,
        "keys": [{
            "key_id": binding_key_id(), "commitment": binding_commitment(),
            "status": "retired" if retired else "active",
        }],
    }
    if machines:
        doc["machines"] = machines
    return doc


# ---------------------------------------------------------------------------- release signing
def hash_tree(d, exclude=()):
    """SHA-256 per file, relative path -> hex, as gov_runtime::util::hash_tree records it."""
    out = {}
    for base, dirs, files in os.walk(d):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(base, f)
            rel = os.path.relpath(p, d).replace(os.sep, "/")
            if rel in exclude:
                continue
            out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def canonical(v):
    """serde_json canonical form the product hashes values with (sorted keys, compact)."""
    return json.dumps(v, sort_keys=True, separators=(",", ":"))


def hash_value(v):
    return hashlib.sha256(canonical(v).encode()).hexdigest()


def use_foreign():
    """Switch every key to a second, unrelated owner's material (the `foreign owner` attacks)."""
    global ROOT_A, ROOT_B, ROOT_C, RELEASE, SNAPSHOT, TIMESTAMP, RECOVERY, OWNER, BINDING_ROLE, BINDING_KEY
    ROOT_A, ROOT_B, ROOT_C = sk(0xF1), sk(0xF2), sk(0xF3)
    RELEASE, SNAPSHOT, TIMESTAMP, RECOVERY = sk(0xF4), sk(0xF5), sk(0xF6), sk(0xF7)
    OWNER, BINDING_ROLE = sk(0xFA), sk(0xFB)
    BINDING_KEY = bytes([0xFC]) * 32


def main():
    cmd = sys.argv[1]
    a = sys.argv[2:]
    if "--foreign" in a:
        use_foreign()

    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default

    if cmd == "root":
        open(a[0], "wb").write(envelope(root_doc(int(opt("--version", 1)), opt("--expires", FAR_FUTURE)),
                                        [ROOT_A, ROOT_B]))
    elif cmd == "bindauth":
        m = opt("--machines")
        open(a[0], "wb").write(envelope(
            binding_authority(int(opt("--version", 1)), m.split(",") if m else None, "--retire" in a),
            [BINDING_ROLE]))
    elif cmd == "bindkey":
        json.dump({"_type": "t2-binding-key", "key_hex": BINDING_KEY.hex()}, open(a[0], "w"))
    elif cmd == "keyid":
        print(json.dumps({"human_gate_keyid": keyid(OWNER), "binding_key_id": binding_key_id()}))
    elif cmd in ("answer", "receipt"):
        s = {
            "_type": "human-gate-answer" if cmd == "answer" else "human-gate-receipt",
            "spec_version": SPEC, "product": PRODUCT,
            "gate": opt("--gate"), "gate_instance": opt("--instance"),
            "package_sha256": opt("--package-sha"), "nonce": opt("--nonce", "n-" + os.urandom(6).hex()),
            "issued": "2026-09-20T00:00:00Z", "expires": opt("--expires", FAR_FUTURE),
        }
        if cmd == "answer":
            s["option"] = opt("--option")
            s["answered_by"] = "P2-AR-0049 held-out owner"
            s["rationale"] = opt("--rationale", "held-out verification decision")
        else:
            s["acknowledged_by"] = "P2-AR-0049 held-out owner"
        signer = {"owner": OWNER, "other": OTHER, "release": RELEASE}[opt("--signer", "owner")]
        open(a[0], "wb").write(envelope(s, [signer]))
    elif cmd == "release":
        # `release <staged-kernel-dir> <out-dir> <sequence>`: sign an already-staged kernel payload
        # (the payload_dirs of KERNEL.yaml plus KERNEL.yaml — e.g. a project's governance/kernel/).
        payload, outdir, seq = os.path.abspath(a[0]), os.path.abspath(a[1]), int(a[2])
        kernel = os.path.join(outdir, "kernel")
        if os.path.exists(kernel):
            shutil.rmtree(kernel)
        shutil.copytree(payload, kernel)
        files = hash_tree(kernel, exclude=("KERNEL_MANIFEST.json",))
        payload_hash = hash_value(files)
        meta = {}
        for line in open(os.path.join(kernel, "KERNEL.yaml")):
            if ":" in line and not line.startswith((" ", "#", "\t")):
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip().strip('"\'')
        manifest = {"framework": meta.get("framework", PRODUCT), "version": meta.get("version", ""),
                    "files": files, "payload_hash": payload_hash}
        kmh = hash_value(manifest)
        migs = []
        mdir = os.path.join(kernel, "migrations")
        if os.path.isdir(mdir):
            import yaml as _y
            for f in sorted(os.listdir(mdir)):
                if not f.endswith(".yaml"):
                    continue
                m = _y.safe_load(open(os.path.join(mdir, f)))
                if not isinstance(m, dict) or "id" not in m:
                    continue
                migs.append({"id": m["id"], "from_version": m.get("from_version"),
                             "to_version": m.get("to_version"), "sha256": hash_value(m)})
        rel = {
            "_type": "release", "spec_version": SPEC, "product": PRODUCT,
            "repository": "git+ssh://owner/private/agentic-engineering-os",
            "channel": opt("--channel", "stable"), "release_version": meta.get("version", ""),
            "sequence": seq, "version": seq, "expires": FAR_FUTURE, "platforms": ["any"],
            "minimum_secure_release": opt("--min-release", ""),
            "minimum_secure_sequence": int(opt("--min-sequence", 0)),
            "payload": {"payload_hash": payload_hash, "kernel_manifest_hash": kmh,
                        "files": {p: {"sha256": h} for p, h in files.items()}},
            "migrations": migs, "schema_identities": {}, "delegations": [],
        }
        md = os.path.join(outdir, "metadata")
        os.makedirs(md, exist_ok=True)
        open(os.path.join(md, "release.json"), "wb").write(envelope(rel, [RELEASE]))
        rb = open(os.path.join(md, "release.json"), "rb").read()
        snap = {"_type": "snapshot", "spec_version": SPEC, "product": PRODUCT, "version": seq,
                "expires": FAR_FUTURE,
                "meta": {"release.json": {"version": seq, "sha256": hashlib.sha256(rb).hexdigest()}}}
        open(os.path.join(md, "snapshot.json"), "wb").write(envelope(snap, [SNAPSHOT]))
        sb = open(os.path.join(md, "snapshot.json"), "rb").read()
        ts = {"_type": "timestamp", "spec_version": SPEC, "product": PRODUCT, "version": seq,
              "expires": FAR_FUTURE,
              "meta": {"snapshot.json": {"version": seq, "sha256": hashlib.sha256(sb).hexdigest()}}}
        open(os.path.join(md, "timestamp.json"), "wb").write(envelope(ts, [TIMESTAMP]))
        print(json.dumps({"kernel": kernel, "payload_hash": payload_hash,
                          "kernel_manifest_hash": kmh, "sequence": seq}))
    else:
        raise SystemExit("unknown command " + cmd)


if __name__ == "__main__":
    main()
