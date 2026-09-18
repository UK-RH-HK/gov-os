#!/usr/bin/env python3
"""P2-AR-0010 probe helper (not product code).

treesnap.py snap <root> <out.json>      sha256 of every file under <root>, excluding .git/, .probe-machine/, .probe-*
                                        and (unless --runtime) .governance-runtime/
treesnap.py diff <a.json> <b.json>      print added / removed / modified paths (one per line, prefixed + - ~)
"""
import hashlib, json, os, sys

def snap(root, include_runtime):
    out = {}
    for d, dirs, files in os.walk(root):
        rel_d = os.path.relpath(d, root)
        parts = [] if rel_d == "." else rel_d.split(os.sep)
        if parts and (parts[0] in (".git", ".probe-machine") or (parts[0] == ".governance-runtime" and not include_runtime)):
            dirs[:] = []
            continue
        for f in files:
            rel = os.path.normpath(os.path.join(rel_d, f)) if parts else f
            if rel.startswith(".probe-"):
                continue
            with open(os.path.join(d, f), "rb") as fh:
                out[rel] = hashlib.sha256(fh.read()).hexdigest()
    return out

if __name__ == "__main__":
    if sys.argv[1] == "snap":
        inc = "--runtime" in sys.argv
        json.dump(snap(sys.argv[2], inc), open(sys.argv[3], "w"), sort_keys=True)
    elif sys.argv[1] == "diff":
        a, b = json.load(open(sys.argv[2])), json.load(open(sys.argv[3]))
        for k in sorted(set(a) | set(b)):
            if k not in a:
                print("+ " + k)
            elif k not in b:
                print("- " + k)
            elif a[k] != b[k]:
                print("~ " + k)
