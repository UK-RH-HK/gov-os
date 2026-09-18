#!/usr/bin/env python3
"""S6 — cross-machine mechanics. Machine A and machine B are two sandboxes with different HOME / absolute paths; a bare
git repository stands in for the private remote.
[X1] tracked truth syncs through Git (clone on B sees A's governed records; B's change reaches A by pull)
[X2] derived runtime rebuilds locally on B; manifest hash equals A's (path independence)
[X3] machine-specific absolute paths do not define release identity (lock / tracked files carry no absolute path;
     lock identity with default caches vs a different XDG_CACHE_HOME — see also A2-04 [L4])
Run: PROBE_TMP=<scratch> python3 S6-cross-machine.py
"""
import os, sys, json, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

A = Sandbox("s6-machineA"); B = Sandbox("s6-machineB-other-path")
remote = A.path("remote.git"); subprocess.run(["git", "init", "-q", "--bare", "-b", "main", remote], check=True)
pa = A.new_repo("projA", {"README.md": "# shared\n", "src/app.py": "def run():\n    return 1\n"})
A.gov("init", "--name", "shared", "--alias", "sh-1", "--intent", "cross machine probe", cwd=pa, quiet=True)
A.gov("task", "create", "--objective", "created on machine A", cwd=pa, quiet=True)
os.makedirs(os.path.join(pa, "spec/decisions"), exist_ok=True)
open(os.path.join(pa, "spec/decisions/D-0001.yaml"), "w").write(yaml.safe_dump({"id": "D-0001", "type": "decision", "title": "decided on A", "status": "ACTIVE"}))
A.gov("rebuild-memory", cwd=pa, quiet=True)
A.git(pa, "add", "-A"); A.git(pa, "commit", "-q", "-m", "machine A state"); A.git(pa, "remote", "add", "origin", remote); A.git(pa, "push", "-q", "origin", "main")
mA = json.load(open(os.path.join(pa, "governance/generated/index-manifest.json")))["manifest_hash"]
lockA = yaml.safe_load(open(os.path.join(pa, "governance/framework.lock")))
print("## [X1] machine B clones the project (no runtime DB / index is copied)")
pb = B.path("clone-on-B")
subprocess.run(["git", "clone", "-q", remote, pb], check=True, env=B.env)
print("[X1] B has .governance-runtime after clone:", os.path.exists(os.path.join(pb, ".governance-runtime")))
st = B.gov("status", cwd=pb, quiet=True)["result"]
print("[X1] gov status on B: records =", st["records"], "| tasks =", st["tasks"]["counts"]["total"], "| framework =", st["framework"]["version"], "| memory =", st["memory"])
d = B.gov("doctor", cwd=pb, quiet=True); r_ = d.get("result") or (d.get("error") or {}).get("details") or {}
print("[X1] gov doctor on B:", r_.get("verdict"), [(c["id"], c["message"][:70]) for c in r_.get("checks", []) if not c["ok"]])
print("\n## [X2] derived runtime rebuilt locally on B")
rb = B.gov("rebuild-memory", cwd=pb, quiet=True)["result"]
mB = json.load(open(os.path.join(pb, "governance/generated/index-manifest.json")))["manifest_hash"]
print("[X2] manifest hash A =", mA[:16], "| B =", mB[:16], "| identical:", mA == mB)
q = B.gov("memory", "query", "decided on A", cwd=pb, quiet=True)["result"]["hits"]
print("[X2] retrieval on B finds A's decision:", [h["path"] for h in q][:3])
B.gov("task", "create", "--objective", "created on machine B", cwd=pb, quiet=True)
B.git(pb, "add", "-A"); B.git(pb, "commit", "-q", "-m", "machine B state"); B.git(pb, "push", "-q", "origin", "main")
A.git(pa, "pull", "-q", "origin", "main")
st = A.gov("status", cwd=pa, quiet=True)["result"]; print("[X1] after pull on A: tasks =", st["tasks"]["counts"]["total"], "(A sees B's task)")
fr = A.gov("memory", "freshness", cwd=pa, quiet=True)["result"]; print("[X2] A's derived index after the pull: fresh =", fr.get("fresh"), "| stale/added =", len(fr.get("stale", [])), len(fr.get("added", [])))
print("\n## [X3] no machine-specific absolute path defines release identity")
lockB = yaml.safe_load(open(os.path.join(pb, "governance/framework.lock")))
print("[X3] lock on B is A's tracked lock (identical):", lockA == lockB, "| lock identity:", {k: lockA[k] for k in ("version", "release_hash", "release_commit", "source")})
tracked = subprocess.run(["git", "ls-files"], cwd=pa, capture_output=True, text=True).stdout.split()
hits = [f for f in tracked if os.path.isfile(os.path.join(pa, f)) and (A.dir in open(os.path.join(pa, f), errors="ignore").read())]
print("[X3] tracked files containing machine A's absolute path:", hits)
pc = B.new_repo("fresh-on-B")
B.gov("init", "--name", "shared", "--alias", "sh-1", "--skip-index", cwd=pc, quiet=True)
lockC = yaml.safe_load(open(os.path.join(pc, "governance/framework.lock")))
print("[X3] same binary, fresh init on B (default cache): identity =", {k: lockC[k] for k in ("version", "release_hash", "release_commit", "source")}, "| equal to A:", all(lockC[k] == lockA[k] for k in ("version", "release_hash", "release_commit", "source")))
pd = B.new_repo("fresh-on-B-xdg")
B.gov("init", "--name", "shared", "--alias", "sh-1", "--skip-index", cwd=pd, env={"XDG_CACHE_HOME": B.path("var-cache")}, quiet=True)
lockD = yaml.safe_load(open(os.path.join(pd, "governance/framework.lock")))
print("[X3] same binary, init on B with XDG_CACHE_HOME=<path without '.cache'>: identity =", {k: lockD[k] for k in ("version", "release_hash", "release_commit", "source")}, "| equal to A:", all(lockD[k] == lockA[k] for k in ("version", "release_hash", "release_commit", "source")))
print("\nDONE")
