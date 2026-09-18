#!/usr/bin/env python3
"""A2 bullet 7 (framework.lock records, not invents, the trusted release identity), bullet 8 (bootstrap/dev/test
modes cannot masquerade as certified production), S6 bullet 3 (machine-specific paths do not define release identity).

L1  provisioned machine, AUTHENTIC signed release; the UNSIGNED release manifest.json beside kernel/ is edited after
    signing (release_commit forged, certification.status -> CERTIFIED). What does framework.lock record?
L2  `gov update --check/--apply` to a signed 4.1.6 whose unsigned manifest.json claims CERTIFIED: is the Human
    Decision Gate still required? Control: the same release with the honest manifest.
L3  what the lock does NOT record (authenticity, sequence, channel, metadata digest) — authentic vs unprovisioned lock.
L4  embedded-payload install with XDG_CACHE_HOME placed (a) outside any git repo without '.cache' in the path and
    (b) inside the consumer repository: source label and release_commit.
Run: PROBE_TMP=<scratch> python3 A2-04-lock-identity-and-masquerade.py
"""
import os, sys, json, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

sb = Sandbox("a2-lock")
R = [K("root-a"), K("root-b"), K("root-c")]
REL1, SNAP, TS, REC = K("release-1"), K("snapshot-1"), K("timestamp-1"), K("recovery-1")
roles = {"root": (2, R), "release": (1, [REL1]), "snapshot": (1, [SNAP]), "timestamp": (1, [TS]), "recovery": (1, [REC])}
anchor = os.path.join(sb.admin, "root-1.json"); open(anchor, "w").write(envelope(root_doc(1, roles), R[:2]))
sb.gov("trust", "provision", "--anchor", anchor, cwd=sb.home, quiet=True)

def build(name, version, supported=None, migration=None, cert=None):
    canon = canonical_copy(sb.path(name + "-canon"), version=version, supported_from=supported, extra_migration=migration)
    args = ["release", "build", "--version", version, "--canonical", canon, "--out", sb.path(name)]
    if cert:
        args += ["--certification", cert]
    o = sb.gov(*args, quiet=True); assert o["ok"], o
    return sb.path(name, "releases", version)

rel15 = build("r15", "4.1.5")
publish(os.path.join(rel15, "metadata"), release_doc(os.path.join(rel15, "kernel"), sequence=10, version=1), [REL1], [SNAP], [TS])
mf = os.path.join(rel15, "manifest.json")
honest_commit = json.load(open(mf))["release_commit"]
m = json.load(open(mf)); m["release_commit"] = "f00dfacef00dfacef00dfacef00dfacef00dface"; m["certification"]["status"] = "CERTIFIED"
json.dump(m, open(mf, "w"), indent=2)
print("## [L1] signed release; unsigned manifest.json edited AFTER signing (release_commit forged, certification CERTIFIED)")
print("[L1] honest release_commit was", honest_commit)
p1 = sb.new_repo("p1")
o = sb.gov("init", "--source", os.path.join(rel15, "kernel"), "--name", "p1", "--alias", "p1a", "--skip-index", cwd=p1, quiet=True)
print("[L1] init ok =", o["ok"], "| authenticity =", o["result"]["release_authenticity"]["authenticity"])
lk = yaml.safe_load(open(os.path.join(p1, "governance/framework.lock")))
print("[L1] framework.lock.release_commit =", lk["release_commit"], "| source =", lk["source"])
print("[L1] lock keys:", sorted(lk.keys()))

print("\n## [L2] update to a SIGNED 4.1.6 whose UNSIGNED manifest.json claims certification CERTIFIED")
mig = ("M-4.1.5-4.1.6.yaml", {"id": "M-4.1.5-4.1.6", "from_version": "4.1.5", "to_version": "4.1.6", "description": "synthetic audit release",
       "breaking": False, "human_gate": "none", "affected_indexes": [], "operations": [{"op": "note", "text": "audit"}], "rollback": "gov update --rollback"})
rel16 = build("r16", "4.1.6", supported=["4.1.5"], migration=mig)
publish(os.path.join(rel16, "metadata"), release_doc(os.path.join(rel16, "kernel"), sequence=20, version=2), [REL1], [SNAP], [TS], snap_version=2, ts_version=2)
ck = sb.gov("update", "--check", "--source", os.path.join(rel16, "kernel"), cwd=p1, quiet=True)["result"]
print("[L2-control] honest manifest: certification =", ck["certification"], "| human_gate_required =", ck["human_gate_required"], "|", ck["recommendation"])
m16 = os.path.join(rel16, "manifest.json"); mm = json.load(open(m16)); mm["certification"]["status"] = "CERTIFIED"; json.dump(mm, open(m16, "w"), indent=2)
ck = sb.gov("update", "--check", "--source", os.path.join(rel16, "kernel"), cwd=p1, quiet=True)["result"]
print("[L2] edited manifest : certification =", ck["certification"], "| human_gate_required =", ck["human_gate_required"], "|", ck["recommendation"], "|", ck["impact"]["consequences"][-1])
o = sb.gov("update", "--apply", "--source", os.path.join(rel16, "kernel"), cwd=p1)   # NOTE: no --approve, no gate
if o.get("ok"):
    print("[L2] update applied without any Human Decision Gate: applied =", o["result"].get("applied"), "| to =", o["result"].get("to"))
gates = sb.gov("gate", "list", cwd=p1, quiet=True)
print("[L2] human gates in the project after the update:", json.dumps(gates.get("result")))
print("[L2] who may mint a CERTIFIED manifest: `gov release build --certification CERTIFIED` takes no project and no role")
x = sb.gov("release", "build", "--version", "4.1.5", "--canonical", canonical_copy(sb.path("any-canon")), "--out", sb.path("any"), "--certification", "CERTIFIED", role="research-agent", quiet=True)
print("[L2] release build as role research-agent (L1): ok =", x["ok"], "| certification.status =", (x.get("result") or {}).get("certification", {}).get("status"))

print("\n## [L3] what framework.lock does and does not record — authentic (provisioned) vs UNKNOWN (unprovisioned)")
sb2 = Sandbox("a2-lock-unprov")
p3 = sb2.new_repo("p3")
o3 = sb2.gov("init", "--source", os.path.join(sb.path("r15-canon"), "framework"), "--name", "p3", "--alias", "p3a", "--skip-index", cwd=p3, quiet=True)
lk3 = yaml.safe_load(open(os.path.join(p3, "governance/framework.lock")))
print("[L3] unprovisioned authenticity =", o3["result"]["release_authenticity"]["authenticity"])
for k in sorted(set(lk) | set(lk3)):
    if k in ("schema_versions",):
        continue
    print(f"[L3]   {k:22s} authentic-install={str(lk.get(k))[:50]:52s} unknown-install={str(lk3.get(k))[:50]}")
print("[L3] lock carries authenticity/sequence/channel/metadata digest:", any(k in lk for k in ("authenticity", "sequence", "channel", "release_metadata_sha256")))

print("\n## [L4] embedded payload + XDG_CACHE_HOME location (machine-specific path) -> recorded release identity")
sb3 = Sandbox("a2-lock-cache")
pA = sb3.new_repo("pA")
oA = sb3.gov("init", "--name", "pA", "--alias", "pAa", "--skip-index", cwd=pA, quiet=True)
lA = yaml.safe_load(open(os.path.join(pA, "governance/framework.lock")))
print("[L4a] default cache ($HOME/.cache): source =", lA["source"], "| release_commit =", lA["release_commit"])
sb4 = Sandbox("a2-lock-cache2")
pB = sb4.new_repo("pB")
oB = sb4.gov("init", "--name", "pB", "--alias", "pBa", "--skip-index", cwd=pB, env={"XDG_CACHE_HOME": sb4.path("xdgcache")}, quiet=True)
lB = yaml.safe_load(open(os.path.join(pB, "governance/framework.lock")))
print("[L4b] XDG_CACHE_HOME=<dir without '.cache'>: source =", lB["source"], "| release_commit =", lB["release_commit"])
sb5 = Sandbox("a2-lock-cache3")
pC = sb5.new_repo("pC")
head = sb5.git(pC, "rev-parse", "HEAD")[1]
oC = sb5.gov("init", "--name", "pC", "--alias", "pCa", "--skip-index", cwd=pC, env={"XDG_CACHE_HOME": os.path.join(pC, "tmpcache")}, quiet=True)
lC = yaml.safe_load(open(os.path.join(pC, "governance/framework.lock")))
print("[L4c] XDG_CACHE_HOME inside the consumer repo: source =", lC["source"], "| release_commit =", lC["release_commit"], "| consumer HEAD =", head,
      "| release_commit == consumer HEAD:", lC["release_commit"] == head, "| installed_at_commit =", lC["installed_at_commit"])
print("[L4] same binary, same embedded payload, same release_hash:", lA["release_hash"] == lB["release_hash"] == lC["release_hash"])
print("\nDONE")
