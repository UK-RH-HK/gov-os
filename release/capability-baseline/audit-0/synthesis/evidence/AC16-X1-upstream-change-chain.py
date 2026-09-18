#!/usr/bin/env python3
"""P2-AR-0007 AC-16, cross-family chain X1: ONE authoritative upstream change followed end-to-end through the
interactions the frozen contract lists, on a single project, so that no family boundary hides a hand-off:

  K2 <-> D1 <-> W6   CIT-E commits a requirement change: index refresh (D1), propagation to open AND completed work (W6)
  O4 / W6            does the prior green governance evidence go stale (O4 currency) once dependent work is stale (W6)?
  N  <-> W9          a checkpoint/handoff after the change: is the stale context packet flagged / handoff blocked?
  W12 (Gate W<->G0-G6) which tier observes each Gate-W duty after the change (G1/G2/G3/G4/G5)?
  U  <-> O5          is any health result produced by the scheduler (not by hand), and does health reflect the state?
  C9 / K1 lead       CIT-P semantic candidates: duplicate suppression.
Then the same kind of change is made directly (no CIT) to show the G1 path.

Run from the worktree root after `~/.cargo/bin/cargo build --release`:
  SYNTH_SCRATCH=<scratch> python3 release/capability-baseline/audit-0/synthesis/evidence/AC16-X1-upstream-change-chain.py
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa

root, g = new_project("x1")
spec_base(root)
commit(root, "spec")
# TASK-0001 will be completed against REQ-0001; TASK-0002 depends on TASK-0001 and is still open.
for tid, deps in (("TASK-0001", None), ("TASK-0002", "TASK-0001")):
    args = ["task", "create", "--id", tid, "--class", "implementation", "--objective", f"Implement totals ({tid})", "--feature", "F-0001",
            "--status", "READY", "--allowed", "src/**,tests/**",
            "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]})]
    if deps:
        args += ["--deps", deps]
    g.ok(*args, quiet=True)
commit(root, "tasks")
g.ok("rebuild-memory", quiet=True)

# --- complete TASK-0001 (G2 close) against the current REQ-0001
g.ok("context", "compile", "TASK-0001", quiet=True)
pk_done_before = json.load(open(os.path.join(root, ".governance-runtime/context/TASK-0001.json")))
g.ok("task", "claim", "TASK-0001", quiet=True)
write(root, "src/lib.rs", read(root, "src/lib.rs") + "\npub fn synth_total() -> i64 { 398 }\n")
g.ok("memory", "rebuild", "--incremental", quiet=True)
cl = g.ok("task", "close", "TASK-0001", "--report", report(root, "r1", "implemented exact totals per REQ-0001 (398)", ["src/lib.rs"]))
rpt = cl.get("report")
commit(root, "TASK-0001 done")
g.ok("memory", "rebuild", "--incremental", quiet=True)
# --- open downstream work: context packet + checkpoint for TASK-0002
pk2 = g.ok("context", "compile", "TASK-0002", quiet=True)
ck_before = g.ok("checkpoint", "create", "--task", "TASK-0002", "--next-action", "implement TASK-0002", quiet=True)
# --- green governance evidence (G5) recorded before the change
au = g.run("audit", quiet=True)
note(f"baseline audit verdict={ (au.get('result') or {}).get('verdict') } record={(au.get('result') or {}).get('id') or (au.get('result') or {}).get('record')}")
commit(root, "green audit")
g.ok("memory", "rebuild", "--incremental", quiet=True)
audits_before = sorted(glob.glob(os.path.join(root, "spec/audits/AUD-*.yaml")))
doc0 = g.ok("doctor", quiet=True)
d021_0 = [c for c in doc0.get("checks", []) if c.get("id") == "D021"]
note(f"D021 before the change: {[(c.get('ok'), c.get('message')) for c in d021_0]}")

# ======================================================================= K2 <-> D1 <-> W6 via CIT-E
manifest = [{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["2 x 199 = 400 (round to whole units)"]}]
mf = os.path.join(root, ".governance-runtime", "synth-x1-manifest.json")
json.dump(manifest, open(mf, "w"))
pr = g.ok("cit", "propose", "--proposal", "Totals must round to whole units (REQ-0001 acceptance criterion changes)",
          "--trigger", "acceptance_criteria_change", "--targets", "REQ-0001", "--manifest", mf, limit=2500)
cid = pr["id"]
sim = pr.get("simulation") or g.ok("cit", "simulate", cid, quiet=True)
imp = sim.get("impact") or {}
cands = [c.get("artifact_id") or c.get("id") or c.get("path") for c in (imp.get("semantic_candidates") or imp.get("candidates") or [])]
dups = sorted({c for c in cands if cands.count(c) > 1})
x("X1-C9-cit-p-candidates-deduplicated", not dups, "CIT-P supplementary candidates carry no duplicate artefacts (C9 duplicate suppression, lead from delta-r K1 OBSERVE)",
  {"radius": imp.get("radius"), "candidates": cands[:30], "duplicates": dups})
gid = sim.get("human_gate")
note(f"CIT {cid} radius={imp.get('radius')} human_gate={gid} affected_tasks={imp.get('affected_tasks')}")
if gid:
    g.ok("gate", "present", gid, quiet=True)
    g.as_(role="human").ok("decide", gid, "--option", "A", "--by", "owner", "--rationale", "x1 probe", quiet=True)
g.ok("cit", "approve", cid, "--by", "owner", "--method", "human" if gid else "auto", quiet=True)
ex = g.run("cit", "execute", cid, limit=2500)
x("X1-K2-cit-committed", ex.get("ok"), "the CIT-E transaction commits", (ex.get("result") or {}).get("status") or ex.get("error"))
commit(root, "after CIT")

fr = g.ok("memory", "freshness", quiet=True)
x("X1-K2xD1-index-fresh-after-cit", fr.get("fresh") is True, "K2->D1: CIT-E refreshed the index inside the transaction (index fresh afterwards)",
  {k: fr.get(k) for k in ("fresh", "stale", "added", "removed")})
tasks = {t["id"]: t for t in g.ok("task", "list", quiet=True)}
x("X1-K2xW6-open-task-retest", tasks["TASK-0002"].get("retest_required") is True, "K2->W6: the open dependent task is flagged for retest",
  {k: tasks["TASK-0002"].get(k) for k in ("task_status", "retest_required")})
x("X1-K2xW6-done-task-revalidated", tasks["TASK-0001"].get("retest_required") is True or tasks["TASK-0001"].get("task_status") != "DONE",
  "K2->W6: the COMPLETED task built on the old criterion is invalidated (W6 'COMPLETE does not imply permanently valid')",
  {k: tasks["TASK-0001"].get(k) for k in ("task_status", "retest_required")})
rdoc = yload(root, f"spec/reports/{rpt}.yaml") if rpt and os.path.exists(os.path.join(root, f"spec/reports/{rpt}.yaml")) else {}
x("X1-K2xW6-done-evidence-stale", bool(rdoc.get("staleness")) or rdoc.get("status") not in (None, "ACTIVE"),
  "K2->W6: the closing report (implementation evidence) of the completed task goes stale", {"report": rpt, "status": rdoc.get("status"), "staleness": rdoc.get("staleness")})
n_tasks = len(tasks)
x("X1-K2xW6-rework-generated", n_tasks > 2, "K2->W6/I3: a revalidation/rework task is generated for the invalidated completed work", {"task_count": n_tasks})
pk2_after = json.load(open(os.path.join(root, ".governance-runtime/context/TASK-0002.json")))
# only a TOP-LEVEL marker counts: the packet always carries authority_layers[2].staleness (a policy excerpt), which is not an invalidation
marker = any(k in pk2_after for k in ("stale", "invalidated", "staleness", "superseded_by"))
x("X1-K2xW6-packet-invalidated", marker or pk2_after.get("packet_hash") != pk2.get("packet_hash"),
  "K2->W6: the open task's stored context packet is invalidated or marked", {"packet_unchanged": pk2_after == pk2, "marker": marker,
                                                                            "still_carries_old_criterion": "2 x 199 = 398" in json.dumps(pk2_after)})

# ======================================================================= O4 <-> W6: green evidence currency
doc1 = g.ok("doctor", quiet=True)
d021_1 = [c for c in doc1.get("checks", []) if c.get("id") == "D021"]
note("D021 after the CIT: " + json.dumps([(c.get("ok"), c.get("message")) for c in d021_1]) + " -- CIT-E wrote CIT/HDG/decision records under spec/decisions/, which IS in the currency key (runtime/src/verification/mod.rs:54-71); the requirement change itself is not; see the isolated check X1-O4-* below")

# ======================================================================= W12 / O5: what ran automatically after the CIT?
audits_after = sorted(glob.glob(os.path.join(root, "spec/audits/AUD-*.yaml")))
x("X1-W12-G4-wider-check-recorded", len(audits_after) > len(audits_before),
  "W12 G4 / O5: a milestone (CIT-E on a spec) triggers a recorded wider health check without an operator running it", {"audit_records_before": len(audits_before), "after": len(audits_after)})

# ======================================================================= N <-> W9: checkpoint and handoff after the change
wd = g.run("checkpoint", "watchdog", quiet=True)
latest = g.ok("checkpoint", "latest", quiet=True)
x("X1-NxW9-checkpoint-stale-marked", "stale" in json.dumps(latest).lower() or "stale" in json.dumps(wd.get("result") or {}).lower(),
  "N3<->W9: the checkpoint that recorded the pre-change packet is marked stale", {"latest": {k: latest.get(k) for k in ("id", "context_packet_hash", "trigger")},
                                                                                 "watchdog": (wd.get("result") or wd.get("error"))})
ho = g.run("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-0002", "--fields", json.dumps({"objective": "implement TASK-0002"}), limit=1200)
latest2 = g.ok("checkpoint", "latest", quiet=True)
x("X1-NxW9-handoff-blocked-or-degraded", (not ho.get("ok")) or "degrad" in json.dumps(ho.get("result")).lower() or "stale" in json.dumps(ho.get("result")).lower(),
  "N<->W9: a handoff whose recorded packet predates an upstream change is blocked or explicitly degraded",
  {"handoff_ok": ho.get("ok"), "before_handoff_checkpoint_packet_hash": str(latest2.get("context_packet_hash"))[:16],
   "equals_pre_change_packet_hash": latest2.get("context_packet_hash") == pk2.get("packet_hash")})

# ======================================================================= U <-> O5: health state
# first let the operator re-establish a fresh green record: commit and re-index the handoff/checkpoint records written
# above so that index staleness does not mask what the audit sees about the invalid completed work
commit(root, "handoff records")
g.ok("memory", "rebuild", "--incremental", quiet=True)
au_fresh = g.run("audit", limit=2500)
res = au_fresh.get("result") or (au_fresh.get("error") or {}).get("details") or {}
note("fresh persisted audit after the CIT: verdict=" + str(res.get("verdict")) + " findings=" + json.dumps(res.get("findings"))[:1200])
commit(root, "fresh audit after CIT")
g.ok("memory", "rebuild", "--incremental", quiet=True)
doc2 = g.run("doctor", limit=2500)
dres = doc2.get("result") or (doc2.get("error") or {}).get("details") or {}
bad = [(c.get("id"), c.get("severity"), c.get("message")) for c in dres.get("checks", []) if not c.get("ok")]
x("X1-UxO5-health-reflects-invalid-completed-work", dres.get("verdict") != "HEALTHY" or res.get("verdict") != "HEALTHY",
  "U<->O5: with a DONE task built on a superseded acceptance criterion, its report ACTIVE, and a stale packet handed off, health is not HEALTHY",
  {"audit_after_cit": res.get("verdict"), "doctor_after_audit": dres.get("verdict"), "doctor_failing_checks": bad})

# ======================================================================= G1 path: the same kind of change made directly (no CIT)
d_pre = [c for c in g.ok("doctor", quiet=True).get("checks", []) if c.get("id") == "D021"]
note("D021 immediately before the direct edit: " + json.dumps([(c.get("ok"), c.get("message")) for c in d_pre]))
y = yload(root, "spec/requirements/REQ-0001.yaml")
y["acceptance_criteria"] = ["2 x 199 = 402 (direct edit, no CIT)"]
write_record(root, "spec/requirements/REQ-0001.yaml", y)
commit(root, "direct edit REQ-0001 (no CIT)")
fr2 = g.ok("memory", "freshness", quiet=True)
x("X1-G1-D1-detects-direct-change", fr2.get("fresh") is False, "G1/D1: index freshness detects the direct change", {k: fr2.get(k) for k in ("fresh", "stale")})
tasks2 = {t["id"]: t for t in g.ok("task", "list", quiet=True)}
g.run("task", "claim", "TASK-0002", quiet=True)
write(root, "src/lib.rs", read(root, "src/lib.rs") + "\npub fn synth_total2() -> i64 { 400 }\n")
c1 = g.run("task", "close", "TASK-0002", "--report", report(root, "r2", "implemented per the packet I was given", ["src/lib.rs"]), quiet=True)
note(f"close while index stale -> {(c1.get('error') or {}).get('code') if not c1.get('ok') else 'ok'}")
g.ok("memory", "rebuild", "--incremental", quiet=True)
c2 = g.run("task", "close", "TASK-0002", "--report", report(root, "r3", "implemented per the packet I was given", ["src/lib.rs"]), quiet=True)
x("X1-G1xW6-direct-change-cannot-be-licensed-by-rebuild", not c2.get("ok"),
  "G1<->W6<->D1: after a direct upstream change, an index rebuild alone must not license closing dependent work on the pre-change packet",
  {"close_after_rebuild_ok": c2.get("ok"), "retest_flag_before_close": tasks2.get("TASK-0002", {}).get("retest_required")})
doc3 = g.ok("doctor", quiet=True)
d021_3 = [c for c in doc3.get("checks", []) if c.get("id") == "D021"]
x("X1-O4-green-stale-after-direct-spec-change", (not d_pre or d_pre[0].get("ok") is True) and bool(d021_3) and d021_3[0].get("ok") is False,
  "O4: a green governance record that was current before a direct change to an authoritative requirement goes stale after it",
  {"before": [(c.get("ok"), c.get("message")) for c in d_pre], "after": [(c.get("ok"), c.get("message")) for c in d021_3]})
summary()
