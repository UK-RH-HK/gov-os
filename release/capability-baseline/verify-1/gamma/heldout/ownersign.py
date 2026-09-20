#!/usr/bin/env python3
"""Independent owner-side signer for Governance OS Signed Release Root v1 documents.

TEST MATERIAL ONLY. Keys are derived from published constant seeds, exactly as the product's own
certification material documents them, so nothing secret exists here. Written from the on-disk
format (`signed` member's exact bytes + ed25519 signatures), not copied from the product's harness.
"""
import hashlib, json, sys, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def key(seed):
    sk = Ed25519PrivateKey.from_private_bytes(bytes([seed])*32)
    from cryptography.hazmat.primitives import serialization as S
    pub = sk.public_key().public_bytes(S.Encoding.Raw, S.PublicFormat.Raw)
    return {"sk": sk, "pub": pub.hex(), "keyid": hashlib.sha256(pub).hexdigest()}

KEYS = {n: key(s) for n, s in
        {"root_a":0x11,"root_b":0x12,"root_c":0x13,"release":0x21,
         "snapshot":0x31,"timestamp":0x41,"recovery":0x51,"owner":0x5a,"binding":0x6a}.items()}

def entry(k): return {"keytype":"ed25519","scheme":"ed25519","keyval":{"public":k["pub"]}}

def envelope(signed, signers):
    b = json.dumps(signed, separators=(",",":")).encode()
    sigs = [{"keyid": KEYS[s]["keyid"], "sig": KEYS[s]["sk"].sign(b).hex()} for s in signers]
    return "{\"signed\":%s,\"signatures\":%s}" % (b.decode(), json.dumps(sigs, separators=(",",":")))

FAR = "2099-01-01T00:00:00Z"

def root_doc(version=1):
    keys = {}
    for n in ("root_a","root_b","root_c","release","snapshot","timestamp","recovery","owner"):
        keys[KEYS[n]["keyid"]] = entry(KEYS[n])
    roles = {
      "root": {"keyids":[KEYS[n]["keyid"] for n in ("root_a","root_b","root_c")], "threshold":2},
      "release": {"keyids":[KEYS["release"]["keyid"]], "threshold":1},
      "snapshot": {"keyids":[KEYS["snapshot"]["keyid"]], "threshold":1},
      "timestamp": {"keyids":[KEYS["timestamp"]["keyid"]], "threshold":1},
      "recovery": {"keyids":[KEYS["recovery"]["keyid"]], "threshold":1},
      "human-gate": {"keyids":[KEYS["owner"]["keyid"]], "threshold":1},
    }
    return {"_type":"root","spec_version":"srr/1","product":"agentic-engineering-os",
            "version":version,"expires":FAR,"keys":keys,"roles":roles}

def answer(gate, instance, pkg_sha, option, nonce):
    return {"_type":"human-gate-answer","spec_version":"srr/1","product":"agentic-engineering-os",
            "gate":gate,"gate_instance":instance,"package_sha256":pkg_sha,"nonce":nonce,
            "issued":"2026-09-20T00:00:00Z","expires":FAR,"option":option,
            "answered_by":"gamma verification owner (test seed)","rationale":"held-out verification"}

def receipt(gate, instance, pkg_sha, nonce):
    return {"_type":"human-gate-receipt","spec_version":"srr/1","product":"agentic-engineering-os",
            "gate":gate,"gate_instance":instance,"package_sha256":pkg_sha,"nonce":nonce,
            "issued":"2026-09-20T00:00:00Z","expires":FAR,"acknowledged_by":"gamma verification owner (test seed)"}

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "root":
        open(sys.argv[2],"w").write(envelope(root_doc(), ["root_a","root_b"]))
    elif cmd == "answer":
        _, _, out, gate, inst, sha, option, nonce = sys.argv
        open(out,"w").write(envelope(answer(gate,inst,sha,option,nonce), ["owner"]))
    elif cmd == "receipt":
        _, _, out, gate, inst, sha, nonce = sys.argv
        open(out,"w").write(envelope(receipt(gate,inst,sha,nonce), ["owner"]))
    else:
        raise SystemExit("usage: ownersign.py root|answer|receipt ...")
