# DERIVED COPY (P2-AR-0022, integration) of repair-1/ws08/evidence/WS08-P4-rollback-and-atomicity.py. Changes, and nothing else:
# none to this file; it imports ./ws08_common.py (changes (1)-(3)).
# Everything else, including every check and its statement, is P2-AR-0020's.
#!/usr/bin/env python3
"""P2-AR-0020 (WS-8) — BC-P2-38: on a provisioned machine the rollback ingress can restore a release this machine
previously verified, subject to the owner's floor/break-glass rule; a refused privileged lifecycle command leaves the
installation as it found it.

Builder evidence (regression, Contract v3 O3). Run against the repaired binary and, as the negative control, against
the base commit's binary:  PROBE_TMP=<scratch> GOV=<gov> python3 WS08-P4-rollback-and-atomicity.py

K1  provisioned: authentic 4.1.5 (seq 10) -> update through the Human Decision Gate to authentic 4.1.6 (seq 20) ->
    `update --rollback` (floor refuses, nothing changes) -> owner-signed break-glass -> `update --rollback
    --break-glass` restores 4.1.5 from this machine's verified-release ledger (alpha-r A2-05 [K6b] needed an unsigned
    CERTIFIED manifest to skip the gate, which BC-P2-37 removes; this is [K6b] with the gate walked).
K2  alpha-r A2-05 [K6a] shape: `kernel reinstall --source <older authentic release> --break-glass` is a version change
    and is refused before the swap: kernel, lock and protected records unchanged.
K3  alpha-r A2-08 [V1]-[V3] shape (no break-glass, above floor): refused before the swap; nothing to repair.
K4  a refused update leaves no snapshot behind, so `update --rollback` cannot "roll back" an update that never
    happened (A0-S5-01; S5-update [U8] built its source with an unsigned CERTIFIED claim, now refused).
K5  transaction abort (S5-update [U7] shape, gate walked): the post-install suite fails, the pre-update kernel, lock
    AND this machine's protected installation record are restored, and governed work continues.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ws08_common import *  # noqa


def tstatus(sb):
    return sb.gov("trust", "status", quiet=True).get("result") or {}


def snapshots(proj):
    d = os.path.join(proj, ".governance-runtime", "update")
    return sorted(os.listdir(d)) if os.path.isdir(d) else []


print("## K1 provisioned rollback after a gated update")
M = Sandbox("ws08-p4-M")
provision(M)
rel = Releases(M)
r15 = rel.build("r15")
k15 = rel.sign(r15, sequence=10)
r16 = rel.build("r16", version="4.1.6", supported=["4.1.5"], migration=mig("4.1.5", "4.1.6"))
k16 = rel.sign(r16, sequence=20)
p = M.new_repo("p")
M.gov("init", "--source", k15, "--name", "p", "--alias", "p-a", "--skip-index", cwd=p, quiet=True)
up, gid = apply_update_through_gate(M, p, k16)
w("K1a", up.get("ok") and (up.get("result") or {}).get("applied") is True and lock(p)["version"] == "4.1.6",
  "precondition: the update to authentic 4.1.6 is applied through its Human Decision Gate", {"gate": gid, "code": err(up), "lock": lock(p)["version"]})
floors_before = tstatus(M).get("floors")
lk_before = open(os.path.join(p, "governance/framework.lock")).read()
rb0 = M.gov("update", "--rollback", cwd=p, quiet=True)
kt0 = M.gov("kernel", "trust", cwd=p, quiet=True).get("result") or {}
w("K1b", err(rb0) == "SRR_BELOW_FLOOR", "without break-glass the floor refuses the rollback (OWNER-DECISION-0006 §9)", err(rb0) or "ok")
w("K1c", open(os.path.join(p, "governance/framework.lock")).read() == lk_before and kt0.get("verified") is True and snapshots(p),
  "the refused rollback leaves the installation as it found it (lock, trusted kernel, unconsumed snapshot)",
  {"verified": kt0.get("verified"), "snapshots": snapshots(p)})
mid = tstatus(M)["machine_id"]
tok = break_glass_doc(mid, stage_files(k15), nonce="ws08-k1", reason="probe: roll back a bad update")
inbox = os.path.join(M.home, ".local/state/governance-os/machine/breakglass/inbox")
open(os.path.join(inbox, "bg.json"), "w").write(envelope(tok, [REC]))
rb = M.gov("update", "--rollback", "--break-glass", "--reason", "probe", cwd=p, quiet=True)
res = rb.get("result") or {}
auth = (res.get("release_authenticity") or {}).get("authenticity")
kt = M.gov("kernel", "trust", cwd=p, quiet=True).get("result") or {}
ts = tstatus(M)
w("K1d", rb.get("ok") and lock(p)["version"] == "4.1.5" and auth == "PREVIOUSLY_VERIFIED_BY_THIS_MACHINE" and kt.get("verified") is True,
  "`update --rollback --break-glass` restores 4.1.5, authenticated from this machine's own record of verifying it",
  {"ok": rb.get("ok"), "code": err(rb), "lock": lock(p)["version"], "authenticity": auth, "kernel_verified": kt.get("verified")})
w("K1e", (ts.get("degraded") or {}).get("marking") == "DEGRADED — RECOVERY ONLY" and ts.get("floors", {}).get("release_high_water") == (floors_before or {}).get("release_high_water"),
  "the machine is marked DEGRADED — RECOVERY ONLY and no floor moved (OWNER-DECISION-0006 §4, §8)",
  {"degraded": (ts.get("degraded") or {}).get("marking"), "high_water": ts.get("floors", {}).get("release_high_water")})

print("\n## K2 [K6a] shape: break-glass reinstall of an older authentic release (a version change)")
G = Sandbox("ws08-p4-G")
provision(G)
relg = Releases(G)
rn = relg.build("rnew")
knew = relg.sign(rn, sequence=20)
ro = relg.build("rold", mutate=lambda d: open(os.path.join(d, "framework/policies/CONTEXT_POLICY.yaml"), "a").write("# older build\n"))
kold = relg.sign(ro, sequence=10)
pg = G.new_repo("pg")
G.gov("init", "--source", knew, "--name", "pg", "--alias", "pg-a", "--skip-index", cwd=pg, quiet=True)
midg = tstatus(G)["machine_id"]
open(os.path.join(G.home, ".local/state/governance-os/machine/breakglass/inbox", "bg.json"), "w").write(
    envelope(break_glass_doc(midg, stage_files(kold), nonce="ws08-k2", reason="probe"), [REC]))
lock_before = open(os.path.join(pg, "governance/framework.lock")).read()
man_before = json.load(open(os.path.join(pg, "governance/kernel/KERNEL_MANIFEST.json")))["payload_hash"]
rec_before = tstatus(G).get("installed_release")
ri = G.gov("kernel", "reinstall", "--source", kold, "--break-glass", cwd=pg, quiet=True)
man_after = json.load(open(os.path.join(pg, "governance/kernel/KERNEL_MANIFEST.json")))["payload_hash"]
ktg = G.gov("kernel", "trust", cwd=pg, quiet=True).get("result") or {}
tsg = tstatus(G)
w("K2a", err(ri) == "KERNEL_MISMATCH" and man_after == man_before and open(os.path.join(pg, "governance/framework.lock")).read() == lock_before
  and ktg.get("verified") is True and tsg.get("installed_release") == rec_before,
  "refused as a version change; kernel, lock, trusted state and the protected installed record are exactly as before",
  {"code": err(ri), "kernel_unchanged": man_after == man_before, "verified": ktg.get("verified")})
o("K2b", f"machine marking after the refused reinstall: {(tsg.get('degraded') or {}).get('marking')} — the verifier enters break-glass before the "
         "pin is known to it; with IP-3 (cli/src/main.rs passes `.with_pinned_payload(framework.lock release_hash)`) the refusal precedes "
         "break-glass entry and no owner authorisation is consumed")

print("\n## K3 [V1]-[V3] shape: reinstall of a newer authentic release, no break-glass")
V = Sandbox("ws08-p4-V")
provision(V)
relv = Releases(V)
v15 = relv.sign(relv.build("r15"), sequence=10)
v16 = relv.sign(relv.build("r16", version="4.1.6", supported=["4.1.5"], migration=mig("4.1.5", "4.1.6")), sequence=20)
pv = V.new_repo("pv")
V.gov("init", "--source", v15, "--name", "pv", "--alias", "pv-a", "--skip-index", cwd=pv, quiet=True)
r = V.gov("kernel", "reinstall", "--source", v16, cwd=pv, quiet=True)
man = json.load(open(os.path.join(pv, "governance/kernel/KERNEL_MANIFEST.json")))
t = V.gov("task", "create", "--objective", "after refused reinstall", cwd=pv, quiet=True)
w("K3a", err(r) == "KERNEL_MISMATCH" and man.get("version") == "4.1.5" and lock(pv)["version"] == "4.1.5" and t.get("ok"),
  "refused before the swap: the installed kernel is still 4.1.5 under a 4.1.5 lock and governed work continues",
  {"code": err(r), "kernel": man.get("version"), "lock": lock(pv)["version"], "task_create": t.get("ok") or err(t)})

print("\n## K4 a refused update leaves no snapshot behind")
r16u = relv.build("r16u", version="4.1.6", supported=["4.1.5"], migration=mig("4.1.5", "4.1.6"))   # UNSIGNED
up, gid = apply_update_through_gate(V, pv, os.path.join(r16u, "kernel"))
w("K4a", err(up) == "SRR_RELEASE_UNVERIFIED" and not snapshots(pv) and lock(pv)["version"] == "4.1.5",
  "the unsigned update is refused by the single verifier and leaves no snapshot", {"code": err(up), "snapshots": snapshots(pv)})
rbk = V.gov("update", "--rollback", cwd=pv, quiet=True)
lf = os.path.join(pv, "spec/reports/framework-updates.jsonl")
events = [json.loads(line).get("event") for line in open(lf)] if os.path.exists(lf) else []
w("K4b", err(rbk) == "SNAPSHOT_MISSING" and "rollback" not in events,
  "`gov update --rollback` finds nothing to roll back and writes no false ledger entry", {"code": err(rbk), "ledger_events": events})

print("\n## K5 transaction abort restores the protected record with the bytes")
U = Sandbox("ws08-p4-U")
R14 = os.path.join(REPO_ROOT, "release/releases/4.1.4/kernel")
pu = U.new_repo("pu", {"README.md": "# k5\n", "product/app.py": "def run():\n    return 1\n"})
U.gov("init", "--source", R14, "--name", "pu", "--alias", "pu-a", cwd=pu, quiet=True)
brk = mig("4.1.4", "4.1.7", ops=[{"op": "set_overlay_key", "file": "PROJECT_POLICY.yaml", "key": "schema_version", "value": 12345}])
brk[1]["overlay_template_changes"] = []
relu = Releases(U)
r17 = relu.build("r17", version="4.1.7", supported=["4.1.4"], migration=brk,
                 mutate=lambda dd: os.remove(os.path.join(dd, "migrations", "M-4.1.4-4.1.5.yaml")))
lock_before = open(os.path.join(pu, "governance/framework.lock")).read()
up, gid = apply_update_through_gate(U, pu, os.path.join(r17, "kernel"))
kt = U.gov("kernel", "trust", cwd=pu, quiet=True).get("result") or {}
t = U.gov("task", "create", "--objective", "after the aborted update", cwd=pu, quiet=True)
w("K5a", not up.get("ok") and "rolled back" in str((up.get("error") or {}).get("message")) and open(os.path.join(pu, "governance/framework.lock")).read() == lock_before,
  "precondition: the update aborts in its post-install suite and restores the pre-update lock", {"code": err(up)})
w("K5b", kt.get("verified") is True and "protected installation record" in str(kt.get("summary")) and t.get("ok"),
  "after the abort the restored kernel matches this machine's protected record and governed work continues",
  {"verified": kt.get("verified"), "summary": kt.get("summary"), "task_create": t.get("ok") or err(t)})
summary()
