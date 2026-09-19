# DERIVED COPY (P2-AR-0022, integration) of repair-1/ws08/evidence/WS08-P1-post-install-integrity.py. Changes, and nothing else:
# (1)-(3) as in ./ws08_common.py (imported from this directory);
# (4) the three fixture gates carry a complete decision package (WS-3 BC-P2-49 refuses a partial one, which made
#     the unedited probe crash on gid=None); the probe's own options/radius/reversibility/confidence are kept.
# Everything else, including every check and its statement, is P2-AR-0020's.
#!/usr/bin/env python3
"""P2-AR-0020 (WS-8) — BC-P2-35: post-install integrity is checked against this machine's protected record.

Builder evidence (regression, Contract v3 O3). Run against the repaired binary and, as the negative control, against
the base commit's binary:  PROBE_TMP=<scratch> GOV=<gov> python3 WS08-P1-post-install-integrity.py

R1  provisioned machine, authentic install; a Human Decision Gate is raised and presented BEFORE a mutually consistent
    rewrite of the installed AUTHORITY_POLICY (answer_gate L3 -> L1) + KERNEL_MANIFEST.json + framework.lock.
    (AC16-X3 [X3d] cannot reach its own L1-answer step on a correct product: it creates its gate AFTER the rewrite,
    and gate creation is itself refused once the kernel is untrusted. This probe raises the gate first.)
R1  (remedy) `gov kernel reinstall --source <signed release>`: the lock was rewritten too, so the reinstall is refused
    KERNEL_PIN_REWRITTEN before anything moves and names the recorded pin; restoring the pin and re-running restores
    a trusted installation.
R2  the same consistent rewrite on the default UNPROVISIONED posture, of a project this machine installed: that
    sub-case is OD-P2-02 (with the owner) — it must be REPORTED (kernel trust detail + presentation), and is not
    enforced by this repair.
R3  a second PROVISIONED machine that did not install the project (a git clone): unanchored until it verifies the
    pinned signed release (ARCH-0003 §8), then anchored.
R4  the same machine, the project copied to a new path: the verified-release ledger anchors it.
R5  installed while unprovisioned, then the machine is provisioned: not anchored until verified.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ws08_common import *  # noqa
PKG = {"why_now": "the next task depends on this choice", "current_state": "two options analysed, none chosen", "impact": "the dependent tasks are re-planned", "cost_rework": "one task of rework if reversed", "recommendation": "B"}  # (4) BC-P2-49 package fields the fixture gates lacked
PKG_FULL = {"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "impact_radius": "R2",
            "reversibility": "reversible: the change can be rolled back", "confidence": 0.6, **PKG}

# ------------------------------------------------------------------------------------------------ R1
print("## R1 provisioned machine: consistent rewrite of the installed AUTHORITY_POLICY after an authentic install")
A = Sandbox("ws08-p1-A")
provision(A)
relA = Releases(A)
r15 = relA.build("r15")
k15 = relA.sign(r15, sequence=10)
pa = A.new_repo("pa")
oi = A.gov("init", "--source", k15, "--name", "pa", "--alias", "pa-a", "--skip-index", cwd=pa, quiet=True)
print("[R1] init ok =", oi.get("ok"), "| authenticity =", ((oi.get("result") or {}).get("release_authenticity") or {}).get("authenticity"))
g = A.gov("gate", "create", "--question", "may we drop the audit table?", "--fields",
          json.dumps({"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}],
                      "impact_radius": "R4", "reversibility": "irreversible", "confidence": 0.3, **PKG}),
          cwd=pa, role="orchestrator", quiet=True)
gid = (g.get("result") or {}).get("id")
A.gov("gate", "present", gid, cwd=pa, role="orchestrator", quiet=True)
print("[R1] gate raised and presented before the rewrite:", gid)
consistent_rewrite(pa, "policies/AUTHORITY_POLICY.yaml", "answer_gate: L3", "answer_gate: L1")
kv = A.gov("kernel", "verify", cwd=pa, quiet=True).get("result") or {}
w("R1a", kv.get("ok") is False and "policies/AUTHORITY_POLICY.yaml" in (kv.get("modified") or []),
  "`gov kernel verify` detects the consistent rewrite and names the file", {"ok": kv.get("ok"), "modified": kv.get("modified")})
kt = A.gov("kernel", "trust", cwd=pa, quiet=True).get("result") or {}
w("R1b", kt.get("verified") is False and (kt.get("trust") or {}).get("substituted_embedded_baseline") is True,
  "the installed kernel is untrusted T1: the embedded baseline is substituted (D-0007 rule 1)",
  {"verified": kt.get("verified"), "summary": kt.get("summary")})
d = A.gov("decide", gid, "--option", "A", "--by", "owner", cwd=pa, role="backend-engineer", session="S-l1", quiet=True)
w("R1c", not d.get("ok"), "an L1 worker still cannot record a human answer to a Human Decision Gate after the rewrite",
  {"ok": d.get("ok"), "code": err(d)})
gc = A.gov("gate", "create", "--question", "q after rewrite", "--fields", json.dumps(PKG_FULL), cwd=pa, role="orchestrator", quiet=True)
w("R1d", not gc.get("ok") and err(gc) == "KERNEL_TAMPERED", "mutating operations fail closed (KERNEL_TAMPERED)", err(gc))
dr = A.gov("doctor", cwd=pa, quiet=True)
dres = dr.get("result") or (dr.get("error") or {}).get("details") or {}
d003 = [c for c in dres.get("checks", []) if c.get("id") == "D003"]
w("R1e", dres.get("verdict") == "UNHEALTHY" and d003 and not d003[0]["ok"] and "AUTHORITY_POLICY" in d003[0]["message"],
  "doctor is UNHEALTHY and D003 names the rewritten file", {"verdict": dres.get("verdict"), "D003": d003[:1]})
st = A.gov("status", cwd=pa, quiet=True)
w("R1f", presented(st) not in (None, "CURRENT"), "the rewritten installation is not presented as current", presented(st))
lock_before = open(os.path.join(pa, "governance/framework.lock")).read()
kern_before = json.load(open(os.path.join(pa, "governance/kernel/KERNEL_MANIFEST.json")))["payload_hash"]
rr0 = A.gov("kernel", "reinstall", "--source", k15, cwd=pa, quiet=True)
unchanged = (open(os.path.join(pa, "governance/framework.lock")).read() == lock_before
             and json.load(open(os.path.join(pa, "governance/kernel/KERNEL_MANIFEST.json")))["payload_hash"] == kern_before)
rec = ((rr0.get("error") or {}).get("details") or {}).get("this_machine_committed") or {}
w("R1h", err(rr0) == "KERNEL_PIN_REWRITTEN" and unchanged and rec.get("release_hash"),
  "a reinstall against the rewritten pin is refused before anything moves, naming the pin this machine recorded",
  {"code": err(rr0), "installation_unchanged": unchanged, "recorded": rec})
if rec.get("release_hash"):
    lk = lock(pa)
    lk["release_hash"] = rec["release_hash"]
    lk["kernel_manifest_hash"] = rec["kernel_manifest_hash"]
    open(os.path.join(pa, "governance/framework.lock"), "w").write(yaml.safe_dump(lk, sort_keys=False))
rr = A.gov("kernel", "reinstall", "--source", k15, cwd=pa, quiet=True)
kt2 = A.gov("kernel", "trust", cwd=pa, quiet=True).get("result") or {}
gc2 = A.gov("gate", "create", "--question", "q after reinstall", "--fields", json.dumps(PKG_FULL), cwd=pa, role="orchestrator", quiet=True)
d2 = A.gov("decide", gid, "--option", "A", "--by", "owner", cwd=pa, role="backend-engineer", session="S-l1", quiet=True)
w("R1g", rr.get("ok") and kt2.get("verified") is True and gc2.get("ok") and not d2.get("ok"),
  "remedy: pin restored, `gov kernel reinstall --source <signed release>` restores a trusted kernel; the L3 floor is back",
  {"reinstall": rr.get("ok") or err(rr), "verified": kt2.get("verified"), "gate_create": gc2.get("ok"), "l1_decide": err(d2)})

# ------------------------------------------------------------------------------------------------ R2
print("\n## R2 unprovisioned machine: consistent rewrite of a project this machine installed")
U = Sandbox("ws08-p1-U")
pu = U.new_repo("pu")
U.gov("init", "--name", "pu", "--alias", "pu-a", "--skip-index", cwd=pu, quiet=True)
consistent_rewrite(pu, "policies/SECURITY_POLICY.yaml", "never_index_classes: [secret, restricted]", "never_index_classes: []")
kt = U.gov("kernel", "trust", cwd=pu, quiet=True).get("result") or {}
pr = (kt.get("trust") or {}).get("protected_record") or {}
st = U.gov("status", cwd=pu, quiet=True)
disc = " ".join((st.get("release_trust") or {}).get("disclosure") or [])
w("R2a", pr.get("state") == "DIVERGED_NOT_ENFORCED" and presented(st) == "UNAUTHENTICATED" and "differs from the payload this machine installed" in disc,
  "on the default posture the rewrite is REPORTED: kernel trust names the divergence and the presentation discloses it",
  {"protected_record": pr, "presented_as": presented(st), "disclosure": disc[:300]})
t = U.gov("task", "create", "--objective", "after rewrite", cwd=pu, quiet=True)
o("R2b", f"not enforced on the unprovisioned posture (OD-P2-02 is with the owner): kernel trust verified={kt.get('verified')}, task create -> {err(t) or t.get('ok')}")

# ------------------------------------------------------------------------------------------------ R3
print("\n## R3 a second provisioned machine that did not install the project (git clone)")
A.git(pa, "add", "-A")
A.git(pa, "commit", "-q", "-m", "state on A")
B = Sandbox("ws08-p1-B")
shutil.copy(os.path.join(A.admin, "root-1.json"), os.path.join(B.admin, "root-1.json"))
provision(B)
pb = B.path("clone")
subprocess.run(["git", "clone", "-q", pa, pb], check=True, env=B.env)
t = B.gov("task", "create", "--objective", "on B before verifying", cwd=pb, quiet=True)
w("R3a", err(t) == "KERNEL_UNANCHORED", "machine B refuses privileged work on a kernel it never verified (ARCH-0003 §8)", err(t) or t.get("ok"))
st = B.gov("status", cwd=pb, quiet=True)
w("R3b", presented(st) == "UNAUTHENTICATED", "machine B does not present the unverified installation as current", presented(st))
k15b = B.path("r15-copy")
copytree(r15, k15b)
rb = B.gov("kernel", "reinstall", "--source", os.path.join(k15b, "kernel"), cwd=pb, quiet=True)
t2 = B.gov("task", "create", "--objective", "on B after verifying", cwd=pb, quiet=True)
st2 = B.gov("status", cwd=pb, quiet=True)
w("R3c", rb.get("ok") and t2.get("ok") and presented(st2) == "CURRENT",
  "after `gov kernel reinstall --source <the pinned signed release>` machine B works on it and presents it as current",
  {"reinstall": rb.get("ok") or err(rb), "task_create": t2.get("ok") or err(t2), "presented_as": presented(st2)})

# ------------------------------------------------------------------------------------------------ R4
print("\n## R4 the same provisioned machine, the project copied to a new path")
pa2 = A.path("pa-moved")
copytree(pa, pa2)
t = A.gov("task", "create", "--objective", "in the moved copy", cwd=pa2, quiet=True)
kt = A.gov("kernel", "trust", cwd=pa2, quiet=True).get("result") or {}
w("R4a", t.get("ok") and kt.get("verified") is True,
  "the machine's verified-release ledger anchors a payload it verified, wherever the project now sits",
  {"task_create": t.get("ok") or err(t), "protected_record": (kt.get("trust") or {}).get("protected_record")})

# ------------------------------------------------------------------------------------------------ R5
print("\n## R5 installed while unprovisioned, then the machine is provisioned")
C = Sandbox("ws08-p1-C")
pc = C.new_repo("pc")
rc15 = C.path("r15-copy")
copytree(r15, rc15)
C.gov("init", "--source", os.path.join(rc15, "kernel"), "--name", "pc", "--alias", "pc-a", "--skip-index", cwd=pc, quiet=True)
shutil.copy(os.path.join(A.admin, "root-1.json"), os.path.join(C.admin, "root-1.json"))
provision(C)
t = C.gov("task", "create", "--objective", "after provisioning", cwd=pc, quiet=True)
w("R5a", err(t) == "KERNEL_UNANCHORED", "an install made before provisioning is not a verification: privileged work waits for one", err(t) or t.get("ok"))
rc = C.gov("kernel", "reinstall", "--source", os.path.join(rc15, "kernel"), cwd=pc, quiet=True)
t2 = C.gov("task", "create", "--objective", "after verifying", cwd=pc, quiet=True)
w("R5b", rc.get("ok") and t2.get("ok"), "verifying the pinned signed release anchors it", {"reinstall": rc.get("ok") or err(rc), "task_create": t2.get("ok") or err(t2)})
summary()
