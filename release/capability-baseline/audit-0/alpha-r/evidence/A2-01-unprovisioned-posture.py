#!/usr/bin/env python3
"""A2 bullets 1, 5, 6, 8 — the UNPROVISIONED posture (a machine with no Signed Release Root trust anchor).

This is the out-of-box state of every machine until an administrator runs `gov trust provision`
(README "Build and use" never provisions). Question: do init/adopt/update admit privileged kernel material whose
authenticity has not been established, and how is that presented?
Run: PROBE_TMP=<scratch> python3 A2-01-unprovisioned-posture.py
"""
import os, sys, json, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *

sb = Sandbox("a2-unprov")
print("## [U0] trust posture of a fresh machine")
sb.gov("trust", "status")

print("\n## [U1] a release is built, then one payload file is TAMPERED after the build (pre-install tampering)")
canon = canonical_copy(sb.path("canon"))
sb.gov("release", "build", "--version", "4.1.5", "--canonical", canon, "--out", sb.path("rel"), quiet=True)
kern = sb.path("rel", "releases", "4.1.5", "kernel")
sp = os.path.join(kern, "policies", "SECURITY_POLICY.yaml")
before = open(sp).read()
tampered = before.replace("never_index_classes: [secret, restricted]", "never_index_classes: []")
assert tampered != before
open(sp, "w").write(tampered)
print("tampered file:", sp, "-> never_index_classes: []")
v = sb.gov("release", "verify", sb.path("rel", "releases", "4.1.5"))

print("\n## [U2] gov init --source <tampered release> on the UNPROVISIONED machine")
proj = sb.new_repo("p-unprov")
o = sb.gov("init", "--source", kern, "--name", "pu", "--alias", "pu-a", "--skip-index", cwd=proj)
if o.get("ok"):
    ra = o["result"]["release_authenticity"]
    print("[U2] release_authenticity.authenticity =", ra["authenticity"], "| posture =", ra["posture"], "| currency =", ra["currency"])
    print("[U2] notes:", json.dumps(ra["notes"], ensure_ascii=False)[:700])
    inst = open(os.path.join(proj, "governance/kernel/policies/SECURITY_POLICY.yaml")).read()
    print("[U2] installed SECURITY_POLICY carries the tampered line:", "never_index_classes: []" in inst)
    pol = sb.gov("policy", "effective", "SECURITY_POLICY", cwd=proj, quiet=True)
    print("[U2] effective SECURITY_POLICY.never_index_classes =", pol["result"]["effective"]["never_index_classes"])
    kt = sb.gov("kernel", "trust", cwd=proj, quiet=True)
    print("[U2] gov kernel trust: verified =", kt["result"]["verified"], "|", kt["result"]["summary"])
    lock = open(os.path.join(proj, "governance/framework.lock")).read()
    print("[U2] framework.lock:\n" + lock)
    st = sb.gov("status", cwd=proj, quiet=True)
    print("[U2] gov status.release_trust =", json.dumps(st["result"]["release_trust"]))
    print("[U2] gov status.framework   =", json.dumps(st["result"]["framework"]))
    print("[U2] envelope release_trust.presented_as =", st.get("release_trust", {}).get("presented_as"))
    d = sb.gov("doctor", cwd=proj, quiet=True)
    res = d.get("result") or (d.get("error") or {}).get("details") or {}
    print("[U2] doctor verdict =", res.get("verdict"), "| release_trust =", json.dumps(res.get("release_trust"))[:300])
    fails = [c for c in res.get("checks", []) if not c.get("ok")]
    print("[U2] doctor failing checks:", [(c["id"], c["severity"], c["message"][:80]) for c in fails])
    print("[U2] doctor checks mentioning authenticity/posture:", [c["id"] for c in res.get("checks", []) if "authentic" in json.dumps(c).lower() or "provision" in json.dumps(c).lower()])
    ts = sb.gov("trust", "status", quiet=True)
    print("[U2] trust status: posture =", ts["result"]["posture"], "| installed_release =", json.dumps(ts["result"]["installed_release"]), "| floors =", json.dumps(ts["result"]["floors"]["release_high_water"]))

print("\n## [U3] gov init with the EMBEDDED payload (the README path) on the unprovisioned machine")
proj2 = sb.new_repo("p-emb")
o2 = sb.gov("init", "--name", "pe", "--alias", "pe-a", "--skip-index", cwd=proj2, quiet=True)
print("[U3] ok =", o2.get("ok"), "| authenticity =", o2["result"]["release_authenticity"]["authenticity"], "| source =", o2["result"]["source"])

print("\n## [U4] a source directory that regenerates its OWN identity (consistent manifest + manifest.json claiming CERTIFIED)")
canon2 = canonical_copy(sb.path("canon2"), mutate=lambda d: open(os.path.join(d, "framework/policies/SECURITY_POLICY.yaml"), "a").write("# attacker edit\n"))
b2 = sb.gov("release", "build", "--version", "4.1.5", "--canonical", canon2, "--out", sb.path("rel2"), "--certification", "CERTIFIED", quiet=True)
print("[U4] attacker built a release with certification.status =", b2["result"]["certification"]["status"])
proj3 = sb.new_repo("p-self")
o3 = sb.gov("init", "--source", sb.path("rel2", "releases", "4.1.5", "kernel"), "--name", "ps", "--alias", "ps-a", "--skip-index", cwd=proj3, quiet=True)
print("[U4] unprovisioned init of the self-identified source: ok =", o3.get("ok"), "| authenticity =", o3["result"]["release_authenticity"]["authenticity"] if o3.get("ok") else err(o3))
print("\nDONE")
