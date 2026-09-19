#!/usr/bin/env python3
"""HC-1 owner-side reference signer — TEST MATERIAL ONLY (P2-AR-0016 evidence; never part of the product).

`gov` never signs anything and holds no key. In a real deployment the product owner signs human-gate answers with a
`human-gate` private key kept off the agents' machine. This script plays that owner for regression evidence: its
keys are derived from a published seed, so they are PUBLIC and unfit for anything but tests.

Usage:
  hc_owner.py anchor  <out.json> [seed]                         self-signed human-channel-anchor document
  hc_owner.py answer  <out.json> <gate> <instance> <sha256> <option> [--by NAME] [--seed N] [--expires TS] [--nonce N] [--product P] [--type T]
  hc_owner.py receipt <out.json> <gate> <instance> <sha256> [--by NAME] [--seed N]
  hc_owner.py keyid [seed]

The signature covers the exact bytes of the `signed` member as written (the verifier extracts it with RawValue).
"""
import hashlib
import json
import sys
import uuid

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

PRODUCT = "agentic-engineering-os"


def key(seed: int):
    sk = Ed25519PrivateKey.from_private_bytes(bytes([seed]) * 32)
    pub = sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return sk, pub.hex(), hashlib.sha256(pub).hexdigest()


def envelope(signed: dict, seeds):
    text = json.dumps(signed, separators=(",", ":"), sort_keys=False)
    sigs = []
    for s in seeds:
        sk, _pub, kid = key(s)
        sigs.append({"keyid": kid, "sig": sk.sign(text.encode()).hex()})
    return '{"signed":' + text + ',"signatures":' + json.dumps(sigs, separators=(",", ":")) + "}"


def opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        return args[i + 1]
    return default


def main(argv):
    cmd = argv[1]
    if cmd == "keyid":
        print(key(int(argv[2]) if len(argv) > 2 else 7)[2])
        return
    out = argv[2]
    if cmd == "anchor":
        seed = int(argv[3]) if len(argv) > 3 else 7
        _sk, pub, kid = key(seed)
        signed = {"_type": "human-channel-anchor", "spec_version": "srr/1", "product": PRODUCT, "version": 1,
                  "expires": "2099-01-01T00:00:00Z", "owner": "test owner (published seed)", "threshold": 1,
                  "keys": {kid: {"keytype": "ed25519", "scheme": "ed25519", "keyval": {"public": pub}}}}
        text = envelope(signed, [seed])
    else:
        gate, instance, sha = argv[3], argv[4], argv[5]
        seed = int(opt(argv, "--seed", "7"))
        signed = {"_type": opt(argv, "--type", "human-gate-answer" if cmd == "answer" else "human-gate-receipt"),
                  "spec_version": "srr/1", "product": opt(argv, "--product", PRODUCT), "gate": gate,
                  "gate_instance": instance, "package_sha256": sha,
                  "nonce": opt(argv, "--nonce", uuid.uuid4().hex), "issued": "2026-09-19T00:00:00Z",
                  "expires": opt(argv, "--expires", "2099-01-01T00:00:00Z")}
        if cmd == "answer":
            signed["option"] = argv[6]
            signed["answered_by"] = opt(argv, "--by", "product owner")
            signed["rationale"] = opt(argv, "--rationale", "owner decision")
        else:
            signed["acknowledged_by"] = opt(argv, "--by", "product owner")
        text = envelope(signed, [seed])
    with open(out, "w") as f:
        f.write(text)
    print(out)


if __name__ == "__main__":
    main(sys.argv)
