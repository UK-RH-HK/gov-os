#!/usr/bin/env python3
"""Probe helper: tamper a kernel file and regenerate every self-describing manifest so the result is
internally self-consistent. Mirrors runtime/src/util.rs hash_tree/hash_value and kernel.rs manifest_hash."""
import hashlib, json, os, sys
import yaml


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def file_map(kdir):
    out = {}
    for dp, dns, fns in os.walk(kdir):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            rel = os.path.relpath(p, kdir).replace(os.sep, "/")
            if rel == "KERNEL_MANIFEST.json":
                continue
            out[rel] = sha(open(p, "rb").read())
    return dict(sorted(out.items()))


def manifest_hash(m):
    sub = {k: m[k] for k in ["framework", "version", "files", "payload_hash"] if k in m}
    return sha(canon(sub).encode())


def strip_restricted(path):
    data = yaml.safe_load(open(path))
    found = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "never_index_classes" and isinstance(v, list):
                    found.append(list(v))
                    o[k] = [x for x in v if x != "restricted"]
                else:
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(data)
    yaml.safe_dump(data, open(path, "w"), sort_keys=False)
    return found


def regen_kernel_manifest(kdir):
    mp = os.path.join(kdir, "KERNEL_MANIFEST.json")
    m = json.load(open(mp))
    files = file_map(kdir)
    m["files"] = files
    m["payload_hash"] = sha(canon(files).encode())
    json.dump(m, open(mp, "w"), indent=2, sort_keys=True)
    return m


def cmd_release(rdir, certify):
    m = regen_kernel_manifest(os.path.join(rdir, "kernel"))
    mj = os.path.join(rdir, "manifest.json")
    rel = json.load(open(mj))
    rel["file_hashes"] = m["files"]
    rel["release_hash"] = m["payload_hash"]
    if certify:
        rel["certification"] = {"status": "CERTIFIED", "implementer_evidence": "", "independent_verifier": "self-declared by the source", "certified_at": "2026-09-13"}
    json.dump(rel, open(mj, "w"), indent=2)
    print(json.dumps({"regenerated_release_hash": m["payload_hash"], "certification": rel["certification"]["status"]}))


def cmd_installed(root):
    kdir = os.path.join(root, "governance", "kernel")
    m = regen_kernel_manifest(kdir)
    lp = os.path.join(root, "governance", "framework.lock")
    lock = yaml.safe_load(open(lp))
    lock["kernel_manifest_hash"] = manifest_hash(m)
    lock["release_hash"] = m["payload_hash"]
    yaml.safe_dump(lock, open(lp, "w"), sort_keys=False)
    print(json.dumps({"lock_kernel_manifest_hash": lock["kernel_manifest_hash"], "lock_release_hash": lock["release_hash"]}))


def cmd_snapshot(sdir):
    kdir = os.path.join(sdir, "kernel")
    m = regen_kernel_manifest(kdir)
    lp = os.path.join(sdir, "framework.lock")
    lock = yaml.safe_load(open(lp))
    lock["kernel_manifest_hash"] = manifest_hash(m)
    lock["release_hash"] = m["payload_hash"]
    yaml.safe_dump(lock, open(lp, "w"), sort_keys=False)
    print(json.dumps({"snapshot_lock_release_hash": lock["release_hash"]}))


def cmd_classes(path):
    data = yaml.safe_load(open(path))
    res = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "never_index_classes":
                    res.append(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(data)
    print(json.dumps(res))


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "strip":
        print(json.dumps({"before": strip_restricted(sys.argv[2])}))
    elif c == "release":
        cmd_release(sys.argv[2], "--certify" in sys.argv)
    elif c == "installed":
        cmd_installed(sys.argv[2])
    elif c == "snapshot":
        cmd_snapshot(sys.argv[2])
    elif c == "classes":
        cmd_classes(sys.argv[2])
    elif c == "get":
        # get <json-file-or-'-'> <dotted.path>
        src = sys.stdin if sys.argv[2] == "-" else open(sys.argv[2])
        v = json.load(src)
        for part in sys.argv[3].split("."):
            v = v.get(part) if isinstance(v, dict) else None
        print(json.dumps(v))
