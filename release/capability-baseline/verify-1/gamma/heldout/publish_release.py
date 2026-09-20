#!/usr/bin/env python3
"""Publish a signed Signed-Release-Root v1 release of an installed kernel payload.

TEST MATERIAL ONLY (published constant seeds; see ownersign.py). Written independently from the
on-disk metadata format so that a held-out probe can run on a PROVISIONED simulated machine, where
the human channel exists and gated branches can actually be exercised.

usage: publish_release.py <installed-kernel-dir> <out-dir> [sequence]
writes <out-dir>/kernel (the staged payload) and <out-dir>/metadata/{release,snapshot,timestamp}.json
"""
import hashlib, json, os, shutil, sys, yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ownersign import KEYS, envelope, FAR

def sha_file(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def canonical(v):  return json.dumps(v, sort_keys=True, separators=(",", ":"))

def stage(src, dest):
    if os.path.exists(dest): shutil.rmtree(dest)
    os.makedirs(dest)
    meta = yaml.safe_load(open(os.path.join(src, "KERNEL.yaml")))
    for d in meta.get("payload_dirs") or []:
        s = os.path.join(src, d)
        if os.path.isdir(s): shutil.copytree(s, os.path.join(dest, d))
    shutil.copy2(os.path.join(src, "KERNEL.yaml"), os.path.join(dest, "KERNEL.yaml"))

def measure(staged):
    files = {}
    for root, _, fs in os.walk(staged):
        for f in fs:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, staged).replace("\\", "/")
            if rel == "KERNEL_MANIFEST.json": continue
            files[rel] = sha_file(full)
    files = {k: files[k] for k in sorted(files)}
    return files, hashlib.sha256(canonical(files).encode()).hexdigest()

def migrations_of(staged):
    d = os.path.join(staged, "migrations")
    out = []
    if not os.path.isdir(d): return out
    for name in sorted(os.listdir(d)):
        if not name.endswith(".yaml"): continue
        m = yaml.safe_load(open(os.path.join(d, name)))
        if not isinstance(m, dict) or "id" not in m: continue
        out.append({"id": m["id"], "from_version": m.get("from_version"),
                    "to_version": m.get("to_version"),
                    "sha256": hashlib.sha256(canonical(m).encode()).hexdigest()})
    return out

def main():
    src, out = sys.argv[1], sys.argv[2]
    seq = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    staged = os.path.join(out, "kernel")
    os.makedirs(out, exist_ok=True)
    stage(src, staged)
    files, payload_hash = measure(staged)
    lock = None
    for cand in (os.path.join(os.path.dirname(src), "framework.lock"),):
        if os.path.exists(cand): lock = yaml.safe_load(open(cand))
    kmh = (lock or {}).get("kernel_manifest_hash") or ""
    version = yaml.safe_load(open(os.path.join(staged, "KERNEL.yaml"))).get("version") \
              or (lock or {}).get("framework_version")
    rel = {"_type": "release", "spec_version": "srr/1", "product": "agentic-engineering-os",
           "repository": "git+ssh://owner/private/agentic-engineering-os",
           "channel": "stable", "release_version": version, "sequence": seq,
           "version": seq, "expires": FAR, "platforms": ["any"],
           "minimum_secure_release": "", "minimum_secure_sequence": 0,
           "payload": {"payload_hash": payload_hash, "kernel_manifest_hash": kmh,
                       "files": {k: {"sha256": v} for k, v in files.items()}},
           "migrations": migrations_of(staged), "schema_identities": {}, "delegations": []}
    md = os.path.join(out, "metadata"); os.makedirs(md, exist_ok=True)
    open(os.path.join(md, "release.json"), "w").write(envelope(rel, ["release"]))
    rb = open(os.path.join(md, "release.json"), "rb").read()
    snap = {"_type": "snapshot", "spec_version": "srr/1", "product": "agentic-engineering-os",
            "version": seq, "expires": FAR,
            "meta": {"release.json": {"version": seq, "sha256": hashlib.sha256(rb).hexdigest()}}}
    open(os.path.join(md, "snapshot.json"), "w").write(envelope(snap, ["snapshot"]))
    sb = open(os.path.join(md, "snapshot.json"), "rb").read()
    ts = {"_type": "timestamp", "spec_version": "srr/1", "product": "agentic-engineering-os",
          "version": seq, "expires": FAR,
          "meta": {"snapshot.json": {"version": seq, "sha256": hashlib.sha256(sb).hexdigest()}}}
    open(os.path.join(md, "timestamp.json"), "w").write(envelope(ts, ["timestamp"]))
    print(json.dumps({"kernel": staged, "payload_hash": payload_hash,
                      "kernel_manifest_hash": kmh, "release_version": version}))

main()
