"""Verifier-authored Signed Release Root test material (P2-AR-0050).

TEST MATERIAL ONLY. Keys are derived from published constant seeds, so the private material is public by
construction and is unfit for any production anchor. `gov` itself contains no signing code (SRR-R0-L4); this file is
the verifier's own administrator-domain signer, written from the envelope/document shapes the runtime's verifier
accepts (`runtime/src/srr/`), so that epsilon's probes can reach the provisioned posture and the authenticated human
channel without depending on the product's certification harness.
"""
import hashlib
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

PRODUCT = "agentic-engineering-os"
FAR_FUTURE = "2099-01-01T00:00:00Z"


class Key:
    def __init__(self, seed_byte):
        self.sk = Ed25519PrivateKey.from_private_bytes(bytes([seed_byte]) * 32)
        from cryptography.hazmat.primitives import serialization
        self.pub = self.sk.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
        self.public_hex = self.pub.hex()
        self.keyid = hashlib.sha256(self.pub).hexdigest()

    def entry(self):
        return self.keyid, {"keytype": "ed25519", "scheme": "ed25519",
                            "keyval": {"public": self.public_hex}}

    def sign(self, data: bytes) -> str:
        return self.sk.sign(data).hex()


def canon(v) -> str:
    """serde_json's compact form with `preserve_order`: insertion order, no spaces."""
    return json.dumps(v, separators=(",", ":"), ensure_ascii=False)


def envelope(signed: dict, keys) -> str:
    b = canon(signed).encode()
    sigs = [{"keyid": k.keyid, "sig": k.sign(b)} for k in keys]
    return '{"signed":%s,"signatures":%s}' % (canon(signed), canon(sigs))


def root_doc(version, root_keys, root_threshold, release_keys, snapshot, timestamp,
             recovery=None, human_gate=None):
    keys = {}
    for k in list(root_keys) + list(release_keys) + [snapshot, timestamp]:
        kid, e = k.entry()
        keys[kid] = e
    roles = {
        "root": {"keyids": [k.keyid for k in root_keys], "threshold": root_threshold},
        "release": {"keyids": [k.keyid for k in release_keys], "threshold": 1},
        "snapshot": {"keyids": [snapshot.keyid], "threshold": 1},
        "timestamp": {"keyids": [timestamp.keyid], "threshold": 1},
    }
    if recovery is not None:
        kid, e = recovery.entry()
        keys[kid] = e
        roles["recovery"] = {"keyids": [recovery.keyid], "threshold": 1}
    if human_gate is not None:
        kid, e = human_gate.entry()
        keys[kid] = e
        roles["human-gate"] = {"keyids": [human_gate.keyid], "threshold": 1}
    return {"_type": "root", "spec_version": "srr/1", "product": PRODUCT,
            "version": version, "expires": FAR_FUTURE, "keys": keys, "roles": roles}


class Publisher:
    """A throw-away root: 2-of-3 root keys, one release/snapshot/timestamp/recovery key, `human-gate` → owner."""

    def __init__(self):
        self.root_a, self.root_b, self.root_c = Key(0x11), Key(0x12), Key(0x13)
        self.release, self.snapshot, self.timestamp = Key(0x21), Key(0x22), Key(0x23)
        self.recovery, self.owner = Key(0x24), Key(0x5A)

    def root_file(self, path, version=1):
        doc = root_doc(version, [self.root_a, self.root_b, self.root_c], 2, [self.release],
                       self.snapshot, self.timestamp, self.recovery, self.owner)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(envelope(doc, [self.root_a, self.root_b]))
        return path

    def gate_answer(self, gate, instance, package_sha256, option, nonce):
        s = {"_type": "human-gate-answer", "spec_version": "srr/1", "product": PRODUCT,
             "gate": gate, "gate_instance": instance, "package_sha256": package_sha256,
             "nonce": nonce, "issued": "2026-09-20T00:00:00Z", "expires": FAR_FUTURE,
             "option": option, "answered_by": "epsilon verifier owner (published test seed)",
             "rationale": "held-out probe (P2-AR-0050)"}
        return envelope(s, [self.owner])

    def gate_receipt(self, gate, instance, package_sha256, nonce):
        s = {"_type": "human-gate-receipt", "spec_version": "srr/1", "product": PRODUCT,
             "gate": gate, "gate_instance": instance, "package_sha256": package_sha256,
             "nonce": nonce, "issued": "2026-09-20T00:00:00Z", "expires": FAR_FUTURE,
             "acknowledged_by": "epsilon verifier owner (published test seed)"}
        return envelope(s, [self.owner])


# ---------------------------------------------------------------- release publication (administrator domain)
import os
import shutil


def _sorted(v):
    if isinstance(v, dict):
        return {k: _sorted(v[k]) for k in sorted(v)}
    if isinstance(v, list):
        return [_sorted(x) for x in v]
    return v


def hash_value(v) -> str:
    return hashlib.sha256(json.dumps(_sorted(v), separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def payload_files(kernel_dir) -> dict:
    """`kernel::payload_files`: {relpath: sha256}, KERNEL_MANIFEST.json excluded."""
    files = {}
    for dp, _dn, fn in os.walk(kernel_dir):
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, kernel_dir).replace("\\", "/")
            if rel == "KERNEL_MANIFEST.json":
                continue
            files[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return dict(sorted(files.items()))


def measure(kernel_dir):
    """(files, payload_hash, kernel_manifest_hash, release_version) as the verifier's staging measures it."""
    import yaml
    files = payload_files(kernel_dir)
    payload_hash = hash_value(files)
    meta = yaml.safe_load(open(os.path.join(kernel_dir, "KERNEL.yaml")))
    version = str(meta.get("version", ""))
    manifest_core = {"framework": str(meta.get("framework", "agentic-engineering-os")),
                     "version": version, "files": files, "payload_hash": payload_hash}
    return files, payload_hash, hash_value(manifest_core), version


def migrations_of(kernel_dir):
    import yaml
    d = os.path.join(kernel_dir, "migrations")
    out = []
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if not f.endswith(".yaml"):
            continue
        m = yaml.safe_load(open(os.path.join(d, f)))
        if not isinstance(m, dict) or "id" not in m:
            continue
        canon_m = json.dumps(_sorted(m), separators=(",", ":"), ensure_ascii=False)
        out.append({"id": m.get("id"), "from_version": m.get("from_version"),
                    "to_version": m.get("to_version"),
                    "sha256": hashlib.sha256(canon_m.encode()).hexdigest()})
    return out


def stage_payload(src_kernel, dest_kernel):
    """Copy an installed kernel payload (minus its manifest) into a release directory."""
    if os.path.exists(dest_kernel):
        shutil.rmtree(dest_kernel)
    shutil.copytree(src_kernel, dest_kernel)
    m = os.path.join(dest_kernel, "KERNEL_MANIFEST.json")
    if os.path.exists(m):
        os.remove(m)
    return dest_kernel


def publish(pub: "Publisher", release_dir, sequence=100, metadata_version=100, channel="stable",
            minimum_secure_release="", minimum_secure_sequence=0):
    """Write `<release_dir>/metadata/{release,snapshot,timestamp}.json` for `<release_dir>/kernel`."""
    kernel = os.path.join(release_dir, "kernel")
    files, payload_hash, kmh, version = measure(kernel)
    rel = {"_type": "release", "spec_version": "srr/1", "product": PRODUCT,
           "repository": "git+ssh://owner/private/agentic-engineering-os",
           "channel": channel, "release_version": version, "sequence": sequence,
           "version": metadata_version, "expires": FAR_FUTURE, "platforms": ["any"],
           "minimum_secure_release": minimum_secure_release,
           "minimum_secure_sequence": minimum_secure_sequence,
           "payload": {"payload_hash": payload_hash, "kernel_manifest_hash": kmh,
                       "files": {p: {"sha256": h} for p, h in files.items()}},
           "migrations": migrations_of(kernel), "schema_identities": {}, "delegations": []}
    md = os.path.join(release_dir, "metadata")
    os.makedirs(md, exist_ok=True)
    rb = envelope(rel, [pub.release]).encode()
    open(os.path.join(md, "release.json"), "wb").write(rb)
    snap = {"_type": "snapshot", "spec_version": "srr/1", "product": PRODUCT,
            "version": metadata_version, "expires": FAR_FUTURE,
            "meta": {"release.json": {"version": metadata_version,
                                      "sha256": hashlib.sha256(rb).hexdigest()}}}
    sb = envelope(snap, [pub.snapshot]).encode()
    open(os.path.join(md, "snapshot.json"), "wb").write(sb)
    ts = {"_type": "timestamp", "spec_version": "srr/1", "product": PRODUCT,
          "version": metadata_version, "expires": FAR_FUTURE,
          "meta": {"snapshot.json": {"version": metadata_version,
                                     "sha256": hashlib.sha256(sb).hexdigest()}}}
    open(os.path.join(md, "timestamp.json"), "wb").write(envelope(ts, [pub.timestamp]).encode())
    return kernel
