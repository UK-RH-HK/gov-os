#!/usr/bin/env python3
"""A2 bullet 9 — signing keys / trust anchors support rotation, revocation and recovery.

K1 root succession rules (skip, unauthorised, not self-signed, expired, valid) with release-key rotation
K2 revocation by omission: the rotated-out release key no longer authorises a release; the new key does
K3 replay of an old root
K4 recovery from the loss of one root key (2-of-3 quorum)
K5 revocation of old releases via a signed minimum secure release (and the sequence-less variant)
K6 break-glass recovery below floor with an owner-signed recovery-role token: via `kernel reinstall` and via
   `update --rollback`; state after each; exit from DEGRADED
Run: PROBE_TMP=<scratch> python3 A2-05-rotation-revocation-recovery.py
"""
import os, sys, json, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

sb = Sandbox("a2-rot")
A, B, C, D, E = K("root-a"), K("root-b"), K("root-c"), K("root-d"), K("root-e")
REL1, REL2, SNAP, TS, REC = K("release-1"), K("release-2"), K("snapshot-1"), K("timestamp-1"), K("recovery-1")
def roles(rootkeys, relkey):
    return {"root": (2, rootkeys), "release": (1, [relkey]), "snapshot": (1, [SNAP]), "timestamp": (1, [TS]), "recovery": (1, [REC])}
def write(name, doc, signers):
    p = os.path.join(sb.admin, name); open(p, "w").write(envelope(doc, signers)); return p
root1 = write("root-1.json", root_doc(1, roles([A, B, C], REL1)), [A, B])
sb.gov("trust", "provision", "--anchor", root1, cwd=sb.home, quiet=True)
MV = [0]
def nv():
    MV[0] += 1; return MV[0]
canon = canonical_copy(sb.path("canon"))
sb.gov("release", "build", "--version", "4.1.5", "--canonical", canon, "--out", sb.path("rel"), quiet=True)
base = sb.path("rel", "releases", "4.1.5")
def signed(name, seq, relkey, **kw):
    d = sb.path(name); shutil.copytree(base, d)
    v = nv(); publish(os.path.join(d, "metadata"), release_doc(os.path.join(d, "kernel"), sequence=seq, version=v, **kw), [relkey], [SNAP], [TS], snap_version=v, ts_version=v)
    return os.path.join(d, "kernel")
def init(src, name, **kw):
    p = sb.new_repo(name)
    return p, sb.gov("init", "--source", src, "--name", name, "--alias", name + "-a", "--skip-index", cwd=p, **kw)

print("## [K0] baseline: release signed by release-1 under root v1")
p0, o = init(signed("s0", 10, REL1), "p0", quiet=True); print("[K0] ok =", o["ok"], "| authenticity =", o["result"]["release_authenticity"]["authenticity"])

print("\n## [K1] root succession v1 -> v2 (rotate root-c -> root-d, rotate release-1 -> release-2)")
new_roles = roles([A, B, D], REL2)
bad_skip = write("root-3-skip.json", root_doc(3, new_roles), [A, B, D])
sb.gov("trust", "root-update", "--anchor", bad_skip, cwd=sb.home)
bad_unauth = write("root-2-unauth.json", root_doc(2, roles([D, E, C], REL2)), [D, E])
sb.gov("trust", "root-update", "--anchor", bad_unauth, cwd=sb.home)
bad_notself = write("root-2-notself.json", root_doc(2, roles([C, D, E], REL2)), [A, B])
sb.gov("trust", "root-update", "--anchor", bad_notself, cwd=sb.home)
bad_exp = write("root-2-expired.json", root_doc(2, new_roles, expires=PAST), [A, B, D])
sb.gov("trust", "root-update", "--anchor", bad_exp, cwd=sb.home)
good2 = write("root-2.json", root_doc(2, new_roles), [A, B])   # A,B are in both the outgoing and incoming quorums
o = sb.gov("trust", "root-update", "--anchor", good2, cwd=sb.home)
if o.get("ok"):
    print("[K1] accepted v2; revoked_keyids =", o["result"]["revoked_keyids"], "| release-1 keyid =", REL1.keyid[:12], "… root-c keyid =", C.keyid[:12], "…")

print("\n## [K2] revocation by omission: release-1 no longer authorises releases; release-2 does")
p2, o = init(signed("s2-old", 11, REL1), "p2")
p2b, o = init(signed("s2-new", 11, REL2), "p2b", quiet=True); print("[K2] release-2 signed release: ok =", o["ok"], "| authenticity =", (o.get("result") or {}).get("release_authenticity", {}).get("authenticity"))

print("\n## [K3] replay of the old root v1 through root-update")
sb.gov("trust", "root-update", "--anchor", root1, cwd=sb.home)

print("\n## [K4] recovery from loss of one root key: root-b is lost; v3 is authorised by root-a + root-d (2-of-3 of v2)")
r3_roles = roles([A, D, E], REL2)
good3 = write("root-3.json", root_doc(3, r3_roles), [A, D])
o = sb.gov("trust", "root-update", "--anchor", good3, cwd=sb.home)
print("[K4] a v4 attempted with the LOST key root-b + root-c (no longer trusted) is refused:")
bad4 = write("root-4-lost.json", root_doc(4, roles([B, C, E], REL2)), [B, C])
sb.gov("trust", "root-update", "--anchor", bad4, cwd=sb.home)
ts = sb.gov("trust", "status", quiet=True)["result"]
print("[K4] trust anchor now: version =", ts["trust_anchor"]["version"], "| roles =", json.dumps(ts["trust_anchor"]["roles"]), "| metadata_high_water.root =", ts["floors"]["metadata_high_water"].get("root"))

print("\n## [K5] revocation of old releases by a signed minimum secure release")
p5, o = init(signed("s5-min", 30, REL2, minimum_secure_release="4.1.5", minimum_secure_sequence=30), "p5", quiet=True)
print("[K5] authentic release seq 30 carrying minimum_secure_sequence 30: ok =", o["ok"], "| floors.minimum_secure =", json.dumps(o["result"]["protected_state"]["floors"]["minimum_secure"])[:160])
p5b, o = init(signed("s5-old", 25, REL2), "p5b")
print("[K5b] a minimum_secure_release published WITHOUT minimum_secure_sequence (AR27-N5):")
sbx = Sandbox("a2-rot-min")
rx1 = write("x-root-1.json", root_doc(1, roles([A, B, C], REL1)), [A, B]); shutil.copy(rx1, os.path.join(sbx.admin, "root-1.json"))
sbx.gov("trust", "provision", "--anchor", os.path.join(sbx.admin, "root-1.json"), cwd=sbx.home, quiet=True)
def xsigned(name, seq, v, **kw):
    d = sbx.path(name); shutil.copytree(base, d)
    publish(os.path.join(d, "metadata"), release_doc(os.path.join(d, "kernel"), sequence=seq, version=v, **kw), [REL1], [SNAP], [TS], snap_version=v, ts_version=v)
    return os.path.join(d, "kernel")
px = sbx.new_repo("px"); o = sbx.gov("init", "--source", xsigned("m1", 30, 1, minimum_secure_release="9.9.9"), "--name", "px", "--alias", "pxa", "--skip-index", cwd=px, quiet=True)
print("[K5b] floors after a release declaring minimum_secure_release 9.9.9 with no sequence:", json.dumps(o["result"]["protected_state"]["floors"]["minimum_secure"]))

print("\n## [K6] break-glass recovery below floor (owner-signed recovery-role token)")
sbg = Sandbox("a2-bg")
rg1 = os.path.join(sbg.admin, "root-1.json"); open(rg1, "w").write(envelope(root_doc(1, roles([A, B, C], REL1)), [A, B]))
sbg.gov("trust", "provision", "--anchor", rg1, cwd=sbg.home, quiet=True)
mid = sbg.gov("trust", "status", quiet=True)["result"]["machine_id"]
inbox = os.path.join(sbg.home, ".local/state/governance-os/machine/breakglass/inbox")
def gsigned(name, seq, v, reldir=base, edit_comment=None, **kw):
    d = sbg.path(name); shutil.copytree(reldir, d)
    if edit_comment:
        f = os.path.join(d, "kernel", "policies", "CONTEXT_POLICY.yaml"); open(f, "a").write(f"# {edit_comment}\n")
    publish(os.path.join(d, "metadata"), release_doc(os.path.join(d, "kernel"), sequence=seq, version=v, **kw), [REL1], [SNAP], [TS], snap_version=v, ts_version=v)
    return os.path.join(d, "kernel")
k_new = gsigned("new", 20, 1)                                        # authentic current release (metadata v1)
k_old = gsigned("old", 10, 2, edit_comment="older build")           # authentic OLDER release (seq 10) re-published by the owner at metadata v2
pg = sbg.new_repo("pg"); o = sbg.gov("init", "--source", k_new, "--name", "pg", "--alias", "pga", "--skip-index", cwd=pg, quiet=True)
print("[K6] installed authentic seq 20: ok =", o["ok"], "| floor =", json.dumps(o["result"]["protected_state"]["floors"]["release_high_water"]))
st_old = stage_files(k_old)
tok = break_glass_doc(mid, st_old, nonce="nonce-0001", reason="audit: restore older build")
open(os.path.join(inbox, "bg-1.json"), "w").write(envelope(tok, [REC]))
print("[K6a] kernel reinstall --source <authentic older release, seq 10> --break-glass (token present)")
o = sbg.gov("kernel", "reinstall", "--source", k_old, "--break-glass", cwd=pg)
kv = sbg.gov("kernel", "verify", cwd=pg, quiet=True)
print("[K6a] after: kernel verify ok =", kv["result"]["ok"], "| trust.verified =", kv["result"]["trust"]["verified"], "| problems =", kv["result"]["trust"]["problems"][:1])
lk = yaml.safe_load(open(os.path.join(pg, "governance/framework.lock")))
print("[K6a] installed KERNEL_MANIFEST payload_hash =", json.load(open(os.path.join(pg, "governance/kernel/KERNEL_MANIFEST.json")))["payload_hash"][:16], "… | lock.release_hash =", lk["release_hash"][:16], "… | older payload =", st_old["payload_hash"][:16], "…")
ts = sbg.gov("trust", "status", quiet=True)["result"]
print("[K6a] trust status: degraded =", json.dumps(ts["degraded"])[:200], "| installed_release.payload_hash =", ts["installed_release"]["payload_hash"][:16], "…")
t = sbg.gov("task", "create", "--objective", "work below floor", cwd=pg, quiet=True)
print("[K6a] normal privileged operation (task create) while below floor:", "ok" if t["ok"] else "REFUSED " + str(err(t)))
print("[K6a] exit: reinstall the authentic at-floor release (seq 20)")
o = sbg.gov("kernel", "reinstall", "--source", k_new, cwd=pg)
ts = sbg.gov("trust", "status", quiet=True)["result"]
kv = sbg.gov("kernel", "verify", cwd=pg, quiet=True)
print("[K6a] after exit attempt: degraded =", json.dumps(ts["degraded"]), "| kernel verify ok =", kv["result"]["ok"], "| trust.verified =", kv["result"]["trust"]["verified"])

print("\n[K6c] alternative restoration path: gov init --force --break-glass --source <authentic older release> (fresh token)")
tok2 = break_glass_doc(mid, st_old, nonce="nonce-0002", reason="audit: restore older build via init --force")
open(os.path.join(inbox, "bg-2.json"), "w").write(envelope(tok2, [REC]))
o = sbg.gov("init", "--force", "--break-glass", "--source", k_old, "--name", "pg", "--alias", "pga", "--skip-index", cwd=pg)
kv = sbg.gov("kernel", "verify", cwd=pg, quiet=True)
lk = yaml.safe_load(open(os.path.join(pg, "governance/framework.lock")))
ts = sbg.gov("trust", "status", quiet=True)["result"]
print("[K6c] after: kernel verify ok =", kv["result"]["ok"], "| trust.verified =", kv["result"]["trust"]["verified"], "| lock.release_hash =", lk["release_hash"][:16], "… | degraded marking =", (ts["degraded"] or {}).get("marking"), "| floors.release_high_water =", json.dumps(ts["floors"]["release_high_water"]))
t = sbg.gov("task", "create", "--objective", "work below floor", cwd=pg, quiet=True)
print("[K6c] normal privileged operation (task create) while marked:", "ok" if t["ok"] else "REFUSED " + str(err(t)))
st = sbg.gov("status", cwd=pg, quiet=True)
print("[K6c] gov status envelope release_trust.presented_as =", st.get("release_trust", {}).get("presented_as"), "| marking =", st.get("release_trust", {}).get("marking"))

print("\n[K6b] update --rollback --break-glass after an authenticated update (the rollback ingress)")
sbr = Sandbox("a2-bg-rb")
rr1 = os.path.join(sbr.admin, "root-1.json"); open(rr1, "w").write(envelope(root_doc(1, roles([A, B, C], REL1)), [A, B]))
sbr.gov("trust", "provision", "--anchor", rr1, cwd=sbr.home, quiet=True)
midr = sbr.gov("trust", "status", quiet=True)["result"]["machine_id"]
def rsigned(name, reldir, seq, v):
    d = sbr.path(name); shutil.copytree(reldir, d)
    publish(os.path.join(d, "metadata"), release_doc(os.path.join(d, "kernel"), sequence=seq, version=v), [REL1], [SNAP], [TS], snap_version=v, ts_version=v)
    return os.path.join(d, "kernel")
k15 = rsigned("r15", base, 10, 1)
mig = ("M-4.1.5-4.1.6.yaml", {"id": "M-4.1.5-4.1.6", "from_version": "4.1.5", "to_version": "4.1.6", "description": "synthetic audit release",
       "breaking": False, "human_gate": "none", "affected_indexes": [], "operations": [{"op": "note", "text": "audit"}], "rollback": "gov update --rollback"})
c16 = canonical_copy(sbr.path("c16"), version="4.1.6", supported_from=["4.1.5"], extra_migration=mig)
sbr.gov("release", "build", "--version", "4.1.6", "--canonical", c16, "--out", sbr.path("rel16"), quiet=True)
k16 = rsigned("r16", sbr.path("rel16", "releases", "4.1.6"), 20, 2)
m16 = os.path.join(os.path.dirname(k16), "manifest.json"); mm = json.load(open(m16)); mm["certification"]["status"] = "CERTIFIED"; json.dump(mm, open(m16, "w"))
pr = sbr.new_repo("pr"); sbr.gov("init", "--source", k15, "--name", "pr", "--alias", "pra", "--skip-index", cwd=pr, quiet=True)
o = sbr.gov("update", "--apply", "--source", k16, cwd=pr, quiet=True); print("[K6b] update 4.1.5 -> 4.1.6 applied =", (o.get("result") or {}).get("applied"))
tok = break_glass_doc(midr, stage_files(k15), nonce="nonce-rb-1", reason="audit: roll back")
open(os.path.join(sbr.home, ".local/state/governance-os/machine/breakglass/inbox/bg-rb.json"), "w").write(envelope(tok, [REC]))
o = sbr.gov("update", "--rollback", "--break-glass", cwd=pr)
lk = yaml.safe_load(open(os.path.join(pr, "governance/framework.lock")))
print("[K6b] after rollback attempt: lock.version =", lk["version"])
print("\nDONE")
