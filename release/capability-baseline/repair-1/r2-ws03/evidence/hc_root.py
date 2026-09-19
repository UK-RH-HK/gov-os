#!/usr/bin/env python3
"""Throw-away Signed Release Root that delegates `human-gate` -- TEST MATERIAL ONLY (P2-AR-0024 evidence).

OWNER-DECISION-P2-0002 req. 3: dev/test machines provision a throw-away root. P2-ADJ-0001: governed human answers
derive from the provisioned root's `human-gate` delegation. This writes such a root for a test machine. Every key is
derived from a published seed (public by construction), exactly like tests/certification/srr_material.rs, so the
root is unfit for anything but tests. The human-gate key is the same seed hc_owner.py signs answers with.

Usage: hc_root.py <out.json> [--human-gate-seed N] [--no-human-gate]
"""
import hashlib
import json
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

PRODUCT = "agentic-engineering-os"


def key(seed: int):
    sk = Ed25519PrivateKey.from_private_bytes(bytes([seed]) * 32)
    pub = sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return sk, pub.hex(), hashlib.sha256(pub).hexdigest()


def entry(seed):
    _sk, pub, kid = key(seed)
    return kid, {"keytype": "ed25519", "scheme": "ed25519", "keyval": {"public": pub}}


def main(argv):
    out = argv[1]
    hg = int(argv[argv.index("--human-gate-seed") + 1]) if "--human-gate-seed" in argv else 7
    # the seeds of tests/certification/srr_material.rs Publisher (root 0x11-0x13 at 2-of-3, release 0x21,
    # snapshot 0x31, timestamp 0x41, recovery 0x51)
    seeds = {"root": [0x11, 0x12, 0x13], "release": [0x21], "snapshot": [0x31], "timestamp": [0x41], "recovery": [0x51]}
    if "--no-human-gate" not in argv:
        seeds["human-gate"] = [hg]
    keys, roles = {}, {}
    for role, ss in seeds.items():
        ids = []
        for s in ss:
            kid, e = entry(s)
            keys[kid] = e
            ids.append(kid)
        roles[role] = {"keyids": ids, "threshold": 2 if role == "root" else 1}
    signed = {"_type": "root", "spec_version": "srr/1", "product": PRODUCT, "version": 1,
              "expires": "2099-01-01T00:00:00Z", "keys": keys, "roles": roles}
    text = json.dumps(signed, separators=(",", ":"))
    sigs = []
    for s in (0x11, 0x12):
        sk, _pub, kid = key(s)
        sigs.append({"keyid": kid, "sig": sk.sign(text.encode()).hex()})
    with open(out, "w") as f:
        f.write('{"signed":' + text + ',"signatures":' + json.dumps(sigs, separators=(",", ":")) + "}")
    print(out)


if __name__ == "__main__":
    main(sys.argv)
