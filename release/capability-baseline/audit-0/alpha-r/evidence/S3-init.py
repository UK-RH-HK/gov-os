#!/usr/bin/env python3
"""S3 — gov init (six bullets). Greenfield init with the embedded payload; certification handling (install of a release
whose own manifest records certification REJECTED); overlay; contract; initial memory/state; health checks; retrieval
profile bootstrap; re-init / --force authority.
Run: PROBE_TMP=<scratch> python3 S3-init.py
"""
import os, sys, json, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

sb = Sandbox("s3")
p = sb.new_repo("green", {"README.md": "# greenfield\n"})
o = sb.gov("init", "--name", "green-shop", "--alias", "gs-01", "--intent", "sell plants online", cwd=p, quiet=True)
r = o["result"]
print("## [I1] kernel installation")
print("[I1] init ok =", o["ok"], "| version =", r["version"], "| source =", r["source"], "| kernel_files =", r["kernel_files"], "| authenticity =", r["release_authenticity"]["authenticity"])
kv = sb.gov("kernel", "verify", cwd=p, quiet=True)["result"]; print("[I1] kernel verify:", {k: kv[k] for k in ("ok", "version", "payload_hash")})
print("[I1] init result keys mentioning certification:", [k for k in r if "certif" in k.lower()], "| lock keys:", sorted(yaml.safe_load(open(os.path.join(p, "governance/framework.lock")))))
print("[I1b] install a release whose own manifest records certification REJECTED (release/releases/4.1.4)")
print("      manifest certification:", json.load(open(os.path.join(REPO, "release/releases/4.1.4/manifest.json")))["certification"])
p2 = sb.new_repo("rejected")
o2 = sb.gov("init", "--source", os.path.join(REPO, "release/releases/4.1.4/kernel"), "--name", "rj", "--alias", "rj-a", "--skip-index", cwd=p2, quiet=True)
print("[I1b] init ->", "ok" if o2["ok"] else f"REFUSED {err(o2)}", "| any warning/notes mentioning certification:", [n for n in json.dumps(o2.get("result")).split('"') if "certif" in n.lower()][:3])
st = sb.gov("status", cwd=p2, quiet=True)["result"]; d = sb.gov("doctor", cwd=p2, quiet=True); dres = d.get("result") or (d.get("error") or {}).get("details") or {}
print("[I1b] gov status / doctor mention of the installed release's certification:", "certif" in json.dumps(st).lower(), "certif" in json.dumps(dres).lower())

print("\n## [I2] project overlay creation")
od = os.path.join(p, "governance/project")
for f in sorted(os.listdir(od)):
    print(f"[I2] {f:32s} {os.path.getsize(os.path.join(od, f))} bytes")
pp = yaml.safe_load(open(os.path.join(od, "PROJECT_POLICY.yaml")))
print("[I2] PROJECT_POLICY.project =", pp["project"])
print("[I2] overlay separate from kernel: kernel files under governance/kernel, overlay under governance/project; overlay not in KERNEL_MANIFEST:", not any(k.startswith("project/") for k in json.load(open(os.path.join(p, "governance/kernel/KERNEL_MANIFEST.json")))["files"]))

print("\n## [I3] repository contract")
rc = yaml.safe_load(open(os.path.join(od, "REPOSITORY_CONTRACT.yaml")))
print("[I3] roots =", rc["roots"], "| rules =", len(rc["paths"]))
fj = os.path.join(p, "framework.json")
print("[I3] generated framework.json (machine-readable topology):", os.path.exists(fj), json.dumps(json.load(open(fj)) if os.path.exists(fj) else None)[:200])

print("\n## [I4] initial memory / state")
print("[I4] spec roots:", sorted(os.listdir(os.path.join(p, "spec"))))
print("[I4] project record:", yaml.safe_load(open(os.path.join(p, "spec/product/PRJ-0001.yaml"))) if os.path.exists(os.path.join(p, "spec/product/PRJ-0001.yaml")) else [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(p, "spec")) for f in fs if "PRJ" in f])
db = sqlite3.connect(os.path.join(p, ".governance-runtime/state.db"))
print("[I4] derived runtime: artifacts =", db.execute("SELECT count(*) FROM artifacts").fetchone()[0], "| chunks =", db.execute("SELECT count(*) FROM chunks").fetchone()[0], "| init index summary =", json.dumps(r["index"])[:200])
print("[I4] held-out starter queries generated at init:", r["heldout_generated"])
st = sb.gov("status", cwd=p, quiet=True)["result"]; print("[I4] gov status reconstructs: records =", st["records"], "| next_action =", st["next_action"], "| memory =", st["memory"])

print("\n## [I5] health checks at init")
print("[I5] init.doctor =", r["doctor"], "| init.conformance =", r["conformance"])
aud = os.path.join(p, "spec/audits", (r["conformance"]["audit"] or "") + ".yaml")
print("[I5] conformance audit record persisted:", os.path.exists(aud), yaml.safe_load(open(aud)).get("verdict") if os.path.exists(aud) else None)

print("\n## [I6] retrieval profile bootstrap")
im = json.load(open(os.path.join(p, "governance/generated/index-manifest.json")))
print("[I6] index manifest pins:", json.dumps({k: im.get(k) for k in ("index_version", "embedder", "reranker", "lexical", "chunking")})[:500])
mm = json.load(open(os.path.join(p, "governance/generated/memory-manifest.json")))
print("[I6] memory manifest keys:", sorted(mm.keys()))

print("\n## [I7] re-init and --force authority")
x = sb.gov("init", "--name", "green-shop", "--alias", "gs-01", "--skip-index", cwd=p, quiet=True); print("[I7] second init ->", "ok" if x["ok"] else f"REFUSED {err(x)}")
x = sb.gov("init", "--force", "--name", "green-shop", "--alias", "gs-01", "--skip-index", cwd=p, role="backend-engineer", quiet=True); print("[I7] init --force as backend-engineer (L1) ->", "ok" if x["ok"] else f"REFUSED {err(x)}")
print("\nDONE")
