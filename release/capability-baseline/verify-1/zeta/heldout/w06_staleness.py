"""W6 — upstream-change staleness propagation (Contract v3:1128-1136). Held-out, P2-AR-0051.

Covers the iteration-1 duty: staleness after an upstream change **both** when a rebuild observes it
and at claim, for a change made outside change control and for one made through CIT-E.
"""
import json
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


def rec(r, rid, folder):
    return yaml.safe_load(open(r.path("spec/%s/%s.yaml" % (folder, rid))))


def closed_impl_task(r, tid, src, extra=None):
    """Create, claim, implement and close an implementation task honestly."""
    lib.seed_task(r, tid, fields=dict({"required_data": ["DATA-0002"]}, **(extra or {})))
    r.ok("task", "status", tid, "READY")
    r.ok("task", "claim", tid, role="backend-engineer", session="impl1")
    r.put(src, "// implements REQ-0001\npub fn f%s() {}\n" % tid[-4:])
    r.ok("rebuild-memory", "--incremental")
    r.ok("verify", "product")
    rp = r.receipt(tid, [src], work="implemented the export")
    out = r.close(tid, rp, role="backend-engineer", session="impl1")
    assert out.get("ok"), json.dumps(out.get("error"))[:600]
    return out["result"], rp["context_packet_hash"]


def main():
    r = lib.Repo("w06")
    lib.seed_green(r)
    res, pkt_hash = closed_impl_task(r, "TASK-0001", "src/export.rs")
    rpt = res.get("report")
    r.commit("implemented")
    audit_before = r.run("audit")
    cur_before = r.ok("health", "currency")

    # ---------------------------------------------------------------- the upstream change
    # an ordinary edit to the authoritative requirement, made OUTSIDE change control
    r.put("spec/requirements/REQ-0001.yaml",
          r.read("spec/requirements/REQ-0001.yaml").replace(
              "CSV contains one row per ledger entry",
              "CSV contains one row per ledger entry, and a header row"))

    # ---- W6 (a) the change is observed when the index is rebuilt ---------------------------
    reb = r.ok("rebuild-memory", "--incremental")
    t = rec(r, "TASK-0001", "tasks")
    rp = rec(r, rpt, "reports")
    lib.check("W6-01", "a DONE task whose authoritative input changed outside change control is "
                       "marked stale / retest_required when the index rebuild observes the change",
              t.get("retest_required") is True
              and "REQ-0001" in json.dumps(t.get("staleness") or {}),
              json.dumps({"retest_required": t.get("retest_required"),
                          "staleness": t.get("staleness"),
                          "rebuild_propagation": reb.get("propagation")})[:500])
    lib.check("W6-02", "the closing report (the implementation evidence) is marked stale",
              bool(rp.get("staleness")) and "REQ-0001" in json.dumps(rp.get("staleness")),
              json.dumps(rp.get("staleness"))[:350])

    # ---- W6.3 the affected context packet is invalidated ------------------------------------
    stored = r.ok("context", "show", "TASK-0001", "--hash", pkt_hash)
    inv = stored.get("invalidated")
    lib.check("W6-03", "the delivered context packet is invalidated, naming the input, its "
                       "delivered hash and its current one",
              inv is not None and "REQ-0001" in json.dumps(inv),
              json.dumps(inv)[:400])

    # ---- W6.4 the impacted downstream nodes are computed ------------------------------------
    st = r.ok("context", "staleness", "TASK-0001")
    lib.check("W6-04", "the derived staleness of the task names the input that changed, with the "
                       "hash it consumed and the hash now",
              "REQ-0001" in json.dumps(st), json.dumps(st)[:500])

    # ---- W6.5 revalidation / rework work is generated ---------------------------------------
    tasks = [yaml.safe_load(open(r.path("spec/tasks/" + f)))
             for f in os.listdir(r.path("spec/tasks")) if f.startswith("TASK-")]
    reval = [x for x in tasks if x.get("revalidates") == "TASK-0001"
             or "TASK-0001" in (x.get("revalidates") or [])]
    lib.check("W6-05", "a linked revalidation task is generated for the completed work",
              bool(reval), json.dumps([{"id": x["id"], "class": x.get("class"),
                                        "revalidates": x.get("revalidates")} for x in tasks])[:400])
    # idempotent: a second observation does not multiply the work
    before_files = sorted(f for f in os.listdir(r.path("spec/tasks")) if f.startswith("TASK-"))
    r.ok("rebuild-memory", "--incremental")
    r.ok("rebuild-memory", "--incremental")
    after_files = sorted(f for f in os.listdir(r.path("spec/tasks")) if f.startswith("TASK-"))
    lib.check("W6-05b", "re-observing the same change generates no duplicate revalidation work",
              before_files == after_files,
              "before=%s after=%s" % (before_files, after_files))

    # ---- W6.6 COMPLETE does not imply permanently valid --------------------------------------
    t = rec(r, "TASK-0001", "tasks")
    lib.check("W6-06", "the task is still DONE but is no longer valid evidence (retest required)",
              t.get("task_status") == "DONE" and t.get("retest_required") is True
              and (t.get("revalidation") or {}).get("required") is True,
              json.dumps({"task_status": t.get("task_status"),
                          "retest_required": t.get("retest_required"),
                          "revalidation": t.get("revalidation")})[:300])

    # ---- W6.7 stale evidence cannot remain green ---------------------------------------------
    cur_after = r.ok("health", "currency")
    changed_classes = [c["class"] for c in (cur_after.get("currency") or {}).get("changed_classes", [])]
    lib.check("W6-07", "the recorded green/health evidence is no longer current after the change, "
                       "naming the input class that changed",
              cur_after["currency"]["current"] is False and "spec_requirements" in changed_classes,
              json.dumps({"current": cur_after["currency"]["current"],
                          "changed": changed_classes,
                          "message": cur_after["currency"].get("message")})[:400])

    # the health family that owns W6 reports it
    h = r.ok("health", "run", "--tier", "G4")
    ucp = (h.get("families") or {}).get("upstream_change_propagation")
    lib.check("W6-07b", "the upstream_change_propagation family observes the state at G4",
              ucp is not None, json.dumps(ucp)[:400])

    # ---- the "at claim" half: a fresh claim propagates and refuses the stale close -----------
    # a NEW task on the same requirement: claiming it propagates what was not yet propagated
    r2 = lib.Repo("w06b")
    lib.seed_green(r2)
    res2, pkt2 = closed_impl_task(r2, "TASK-0001", "src/export.rs")
    r2.commit("implemented")
    r2.put("spec/requirements/REQ-0001.yaml",
           r2.read("spec/requirements/REQ-0001.yaml").replace(
               "CSV contains one row per ledger entry",
               "CSV contains one row per ledger entry, and a header row"))
    lib.seed_task(r2, "TASK-0002", fields={"required_data": ["DATA-0002"]})
    r2.ok("task", "status", "TASK-0002", "READY")
    before = rec(r2, "TASK-0001", "tasks").get("retest_required")
    cl = r2.run("task", "claim", "TASK-0002", role="backend-engineer", session="impl2")
    after = rec(r2, "TASK-0001", "tasks").get("retest_required")
    lib.check("W6-08", "claiming work propagates an upstream change made outside change control, "
                       "so the completed work's staleness is recorded at claim time",
              before is not True and after is True,
              json.dumps({"before_claim": before, "after_claim": after,
                          "claim_ok": cl.get("ok"),
                          "propagation": (cl.get("result") or {}).get("propagation")})[:400])

    # ---- closing stale work is refused until the changed inputs are re-tested ---------------
    # The change is committed and propagated BEFORE the close, so this is not a mutation-scope
    # question: the receipt itself consumed an input that is no longer the governed content.
    r3 = lib.Repo("w06c")
    lib.seed_green(r3)
    lib.seed_task(r3, "TASK-0001", fields={"required_data": ["DATA-0002"]})
    r3.ok("task", "status", "TASK-0001", "READY")
    r3.ok("task", "claim", "TASK-0001", role="backend-engineer", session="impl1")
    r3.put("src/export.rs", "// implements REQ-0001\npub fn export() {}\n")
    r3.ok("rebuild-memory", "--incremental")
    r3.ok("verify", "product")
    stale_receipt = r3.receipt("TASK-0001", ["src/export.rs"], work="implemented the export")
    r3.ok("task", "release", "TASK-0001", role="backend-engineer", session="impl1")
    r3.put("spec/requirements/REQ-0001.yaml",
           r3.read("spec/requirements/REQ-0001.yaml").replace(
               "CSV contains one row per ledger entry",
               "CSV contains one row per ledger entry, and a header row"))
    r3.ok("rebuild-memory", "--incremental")
    r3.commit("requirement changed and propagated")
    reclaim = r3.run("task", "claim", "TASK-0001", role="backend-engineer", session="impl2")
    why = json.dumps(reclaim.get("error"))
    lib.check("W6-09", "after the change is propagated the work cannot simply be re-claimed and "
                       "closed on the stale evidence: the refusal names the retest requirement "
                       "and its remedy",
              not reclaim.get("ok") and "retest required" in why
              and ("re-test evidence" in why or "re-delivers its context" in why),
              why[:450])
    # the blocked work's own remedy stays available (availability rule)
    lib.check("W6-09b", "the remedy of that block is available: the context recompiles and the "
                        "staleness is inspectable",
              r3.run("context", "compile", "TASK-0001").get("ok") is True
              and r3.run("context", "staleness", "TASK-0001").get("ok") is True)
    # and a close forced through with the stale receipt is still refused
    forced = r3.close("TASK-0001", stale_receipt, role="backend-engineer", session="impl2")
    lib.check("W6-09c", "a close carrying the stale receipt is refused",
              not forced.get("ok"), json.dumps(forced.get("error"))[:400])

    # ---- the CIT-E route: the transaction computes the impacted downstream nodes -------------
    r4 = lib.Repo("w06d")
    lib.seed_green(r4)
    res4, pkt4 = closed_impl_task(r4, "TASK-0001", "src/export.rs")
    r4.commit("implemented")
    newtext = r4.read("spec/requirements/REQ-0001.yaml").replace(
        "CSV contains one row per ledger entry",
        "CSV contains one row per ledger entry, and a header row")
    man = os.path.join(r4.state, "cit-manifest.json")
    with open(man, "w") as f:
        json.dump([{"op": "write_file", "path": "spec/requirements/REQ-0001.yaml",
                    "content": newtext, "reason": "add the header row"}], f)
    cit = r4.run("cit", "propose", "--proposal", "add a header row to the export requirement",
                 "--targets", "REQ-0001", "--manifest", man, role="change-controller")
    cid = (cit.get("result") or {}).get("id")
    sim = r4.run("cit", "simulate", cid, role="change-controller") if cid else {}
    sr = sim.get("result") or {}
    impact = sr.get("impact") or {}
    nodes = {a["node"] for a in impact.get("affected") or []}
    cons = json.dumps(impact.get("consequences") or [])
    reval = impact.get("completed_tasks_to_revalidate") or []
    lib.check("W6-10", "CIT-P computes the impacted downstream nodes by name — the completed task, "
                       "its close report, its scenario and its test obligation — and states the "
                       "revalidation consequence",
              bool(cid) and sim.get("ok")
              and {"TASK-0001", "SCN-0001", "TO-0001"} <= nodes
              and any(n.startswith("RPT-") for n in nodes)
              and "revalidation tasks generated" in cons and "TASK-0001" in json.dumps(reval),
              json.dumps({"cit": cid, "radius": impact.get("radius"),
                          "affected": sorted(nodes),
                          "completed_tasks_to_revalidate": reval,
                          "consequences": impact.get("consequences")})[:800])
    # execution at this radius is gated behind a Human Decision Gate (correct, not a W6 gap): the
    # propagation itself is the same `cit::propagation` engine the direct route exercised above.
    app = r4.run("cit", "approve", cid, role="change-controller") if cid else {}
    lib.check("W6-10b", "executing that CIT is gated behind an unanswered Human Decision Gate, so "
                        "the CIT-E execution half is not agent-drivable at this radius (recorded)",
              not app.get("ok") and "gate" in json.dumps(app.get("error")).lower(),
              json.dumps(app.get("error"))[:300])

    _ = (audit_before, cur_before, res2, pkt2, res4, pkt4)
    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
