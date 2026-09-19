#!/usr/bin/env python3
"""P2-AR-0020 (WS-8) — BC-P2-37: no trust decision from an unauthenticated release field; framework.lock records the
identity verification established, and its basis, independent of machine paths.

Builder evidence (regression, Contract v3 O3). Run against the repaired binary and, as the negative control, against
the base commit's binary:  PROBE_TMP=<scratch> GOV=<gov> python3 WS08-P3-certification-and-lock-identity.py

C1  a SIGNED 4.1.6 whose UNSIGNED manifest.json is edited to CERTIFIED: the Human Decision Gate is still required.
C2  a 4.1.6 whose SIGNED release metadata binds evidence.certification.status CERTIFIED (the trust-root-authenticated
    carrier, ARCH-0003 §4): the certification is authenticated and is the only thing that can waive the gate.
C3  minting: `gov release build --certification CERTIFIED` is refused for every role, before anything is written.
C4  lock identity on an authentic install: the forged unsigned release_commit is not recorded; authenticity, sequence,
    channel and the metadata digest are; a release commit bound by SIGNED metadata is recorded with its basis.
C5  the embedded payload's recorded identity does not vary with XDG_CACHE_HOME (three placements).
C6  `gov release verify` reports an unsigned CERTIFIED claim as uncertified.
C7  R1 control: a self-identified source (consistent KERNEL_MANIFEST.json, no signed metadata) is still refused by the
    single verifier on a provisioned machine. (alpha-r A2-02 [P6]/[P8] build that source with `--certification
    CERTIFIED`, which BC-P2-37 now refuses, so their init/adopt fails earlier with KERNEL_SOURCE_NOT_FOUND; this is
    the same property with the source built without the certification claim.)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ws08_common import *  # noqa

print("## C1/C2 provisioned machine, update gating")
M = Sandbox("ws08-p3-M")
provision(M)
rel = Releases(M)
r15 = rel.build("r15")
k15 = rel.sign(r15, sequence=10)
p = M.new_repo("p")
M.gov("init", "--source", k15, "--name", "p", "--alias", "p-a", "--skip-index", cwd=p, quiet=True)
r16 = rel.build("r16", version="4.1.6", supported=["4.1.5"], migration=mig("4.1.5", "4.1.6"))
k16 = rel.sign(r16, sequence=20)
mf = os.path.join(r16, "manifest.json")
m = json.load(open(mf)); m["certification"]["status"] = "CERTIFIED"; json.dump(m, open(mf, "w"))
ck = M.gov("update", "--check", "--source", k16, cwd=p, quiet=True).get("result") or {}
w("C1a", ck.get("human_gate_required") is True and ck.get("certification") != "CERTIFIED",
  "an unsigned CERTIFIED claim does not waive the Human Decision Gate", {k: ck.get(k) for k in ("certification", "human_gate_required", "certification_basis")})
ap = M.gov("update", "--apply", "--source", k16, cwd=p, quiet=True)
w("C1b", err(ap) == "HUMAN_GATE_REQUIRED" and lock(p)["version"] == "4.1.5",
  "`gov update --apply` stops at the gate; nothing is installed", {"code": err(ap), "lock_version": lock(p)["version"]})
r16c = rel.build("r16c", version="4.1.6", supported=["4.1.5"], migration=mig("4.1.5", "4.1.6"))
k16c = rel.sign(r16c, sequence=21, evidence={"certification": {"status": "CERTIFIED", "record_sha256": "0" * 64}})
p2 = M.new_repo("p2")
M.gov("init", "--source", k15, "--name", "p2", "--alias", "p2-a", "--skip-index", cwd=p2, quiet=True)
ck2 = M.gov("update", "--check", "--source", k16c, cwd=p2, quiet=True).get("result") or {}
basis = ck2.get("certification_basis") or {}
w("C2a", ck2.get("certification") == "CERTIFIED" and basis.get("authenticated") is True and ck2.get("human_gate_required") is False,
  "a certification bound by signed release metadata is authenticated against this machine's trust root",
  {k: ck2.get(k) for k in ("certification", "human_gate_required", "certification_basis")})
ap2 = M.gov("update", "--apply", "--source", k16c, cwd=p2, quiet=True)
w("C2b", ap2.get("ok") and (ap2.get("result") or {}).get("applied") is True,
  "that authenticated certification — and only it — lets the update proceed without a gate",
  {"ok": ap2.get("ok"), "applied": (ap2.get("result") or {}).get("applied"), "code": err(ap2)})

print("\n## C3 minting a certification claim")
res = {}
for role in ("orchestrator", "research-agent"):
    out = M.path(f"mint-{role}")
    x = M.gov("release", "build", "--version", "4.1.5", "--canonical", canonical_copy(M.path(f"mint-canon-{role}")),
              "--out", out, "--certification", "CERTIFIED", role=role, quiet=True)
    res[role] = {"code": err(x), "written": os.path.exists(os.path.join(out, "releases"))}
w("C3a", all(v["code"] == "RELEASE_CERTIFICATION_REQUIRES_SIGNED_METADATA" and not v["written"] for v in res.values()),
  "no role can mint a CERTIFIED release; the refusal precedes any write", res)
y = M.gov("release", "build", "--version", "4.1.5", "--canonical", canonical_copy(M.path("mint-canon-ok")), "--out", M.path("mint-ok"),
          "--certification", "READY_FOR_INDEPENDENT_OS_VERIFICATION", quiet=True)
w("C3b", y.get("ok"), "a non-certifying status is still recorded (control)", err(y) or "ok")

print("\n## C4 framework.lock identity (a fresh provisioned machine: C2 raised the first machine's floor to 4.1.6)")
N = Sandbox("ws08-p3-N")
provision(N)
rel = Releases(N)
M = N
r15f = rel.build("r15f")
k15f = rel.sign(r15f, sequence=11)
mf = os.path.join(r15f, "manifest.json")
honest = json.load(open(mf))["release_commit"]
m = json.load(open(mf)); m["release_commit"] = "f00dface" * 5; json.dump(m, open(mf, "w"))
p3 = M.new_repo("p3")
M.gov("init", "--source", k15f, "--name", "p3", "--alias", "p3-a", "--skip-index", cwd=p3, quiet=True)
lk = lock(p3)
w("C4a", lk.get("release_commit") != "f00dface" * 5 and lk.get("authenticity") == "AUTHENTIC" and lk.get("sequence") == 11
  and lk.get("channel") and lk.get("release_metadata_sha256") and isinstance(lk.get("identity_basis"), dict),
  "the forged unsigned release_commit is not recorded; the verified identity and its basis are",
  {k: lk.get(k) for k in ("release_commit", "source", "authenticity", "sequence", "channel", "release_metadata_sha256")})
r15s = rel.build("r15s")
k15s = rel.sign(r15s, sequence=12, evidence={"provenance": {"release_commit": honest}})
p4 = M.new_repo("p4")
M.gov("init", "--source", k15s, "--name", "p4", "--alias", "p4-a", "--skip-index", cwd=p4, quiet=True)
lk4 = lock(p4)
w("C4b", lk4.get("release_commit") == honest and "signed release metadata" in str((lk4.get("identity_basis") or {}).get("release_commit")),
  "a release commit bound by SIGNED metadata is recorded, with that basis", {"release_commit": lk4.get("release_commit"), "basis": (lk4.get("identity_basis") or {}).get("release_commit")})

print("\n## C5 embedded identity vs XDG_CACHE_HOME")
ids = {}
for tag, env in (("default", None), ("no-dot-cache", "XDG"), ("inside-consumer", "INSIDE")):
    S = Sandbox(f"ws08-p3-e-{tag}")
    pe = S.new_repo("pe")
    e = None
    if env == "XDG":
        e = {"XDG_CACHE_HOME": S.path("xdgcache")}
    elif env == "INSIDE":
        e = {"XDG_CACHE_HOME": os.path.join(pe, "tmpcache")}
    S.gov("init", "--name", "pe", "--alias", "pe-a", "--skip-index", cwd=pe, env=e, quiet=True)
    le = lock(pe)
    ids[tag] = {k: le.get(k) for k in ("version", "release_hash", "release_commit", "source")}
    ids[tag]["consumer_head"] = S.git(pe, "rev-parse", "HEAD")[1]
vals = [{k: v[k] for k in ("version", "release_hash", "release_commit", "source")} for v in ids.values()]
w("C5a", all(v == vals[0] for v in vals) and all(v["release_commit"] != v["consumer_head"] for v in ids.values()),
  "the same binary's embedded payload records one identity wherever its cache sits, never the consumer's HEAD", ids)

print("\n## C6 release verify")
rv = N.gov("release", "verify", r16, quiet=True).get("result") or {}
c = rv.get("certification") or {}
w("C6a", c.get("effective_status") == "UNCERTIFIED" and c.get("authenticated") is False,
  "`gov release verify` treats an unsigned CERTIFIED claim as uncertified", c)
print("\n## C7 control: a self-identified unsigned source on a provisioned machine")
selfrel = rel.build("self", mutate=lambda dd: open(os.path.join(dd, "framework/policies/SECURITY_POLICY.yaml"), "a").write("# self-identified\n"))
p7 = N.new_repo("p7")
o7 = N.gov("init", "--source", os.path.join(selfrel, "kernel"), "--name", "p7", "--alias", "p7-a", "--skip-index", cwd=p7, quiet=True)
w("C7a", err(o7) == "SRR_RELEASE_UNVERIFIED" and not os.path.exists(os.path.join(p7, "governance", "framework.lock")),
  "the single verifier still refuses a source that regenerates its own identity; nothing is installed", err(o7) or "ok")
summary()
