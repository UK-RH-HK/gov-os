"""W3 — mandatory task-input manifest (Contract v3:1092-1104). Held-out, P2-AR-0051."""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


def main():
    r = lib.Repo("w03")
    lib.seed_green(r)
    lib.seed_task(r, "TASK-0001", fields={"required_data": ["DATA-0002"]})
    r.ok("task", "status", "TASK-0001", "READY")
    r.commit("seed")

    # ---- W3.1 required input IDs -------------------------------------------------------------
    m = r.ok("context", "manifest", "TASK-0001")
    ids = {i["id"] for i in m["inputs"] if i["required"]}
    lib.check("W3-01", "the manifest names every required input id",
              {"F-0001", "REQ-0001", "D-0100", "SCN-0001", "TO-0001", "IFC-0001", "ARCH-0100",
               "DATA-0002"} <= ids, sorted(ids))

    # ---- W3.2 required authority/lifecycle state; W3.3 version/hash constraints ---------------
    r.put("spec/tasks/TASK-0002.yaml", """id: TASK-0002
type: task
title: constrained-input task
status: ACTIVE
class: implementation
task_status: DRAFT
objective: exercise declared constraints
feature: F-0001
required_inputs:
  - {id: REQ-0001, reason: the requirement this work realises, required_status: ACTIVE,
     required_state_class: AUTHORITATIVE, version: "1"}
""")
    m2 = r.ok("context", "manifest", "TASK-0002")
    e = [i for i in m2["inputs"] if i["id"] == "REQ-0001"][0]
    con = e.get("constraints") or {}
    lib.check("W3-02", "an entry can declare required lifecycle status and authority class",
              con.get("required_status") in ("ACTIVE", ["ACTIVE"])
              and con.get("required_state_class") in ("AUTHORITATIVE", ["AUTHORITATIVE"])
              and e["satisfied"], json.dumps(e)[:400])

    # a version constraint that the record violates must block
    r.put("spec/tasks/TASK-0003.yaml", """id: TASK-0003
type: task
title: wrong-version task
status: ACTIVE
class: implementation
task_status: DRAFT
objective: exercise a violated version constraint
feature: F-0001
required_inputs:
  - {id: REQ-0001, reason: needs v9, version: "9"}
""")
    m3 = r.ok("context", "manifest", "TASK-0003")
    v = [i for i in m3["input_violations"] if i["id"] == "REQ-0001"]
    lib.check("W3-03", "a declared version/hash constraint the input violates blocks the manifest",
              m3["delivery_state"] == "BLOCKED" and bool(v), json.dumps(m3["input_violations"])[:400])

    # a content_hash constraint
    h = [i for i in m["inputs"] if i["id"] == "REQ-0001"][0]["content_hash"]
    r.put("spec/tasks/TASK-0004.yaml", """id: TASK-0004
type: task
title: hash-pinned task
status: ACTIVE
class: implementation
task_status: DRAFT
objective: exercise a content-hash pin
feature: F-0001
required_inputs:
  - {id: REQ-0001, reason: pinned to reviewed content, content_hash: "%s"}
""" % h)
    m4 = r.ok("context", "manifest", "TASK-0004")
    ok_pin = m4["delivery_state"] == "COMPLETE"
    r.put("spec/requirements/REQ-0001.yaml",
          r.read("spec/requirements/REQ-0001.yaml") + "priority: high\n")
    m4b = r.ok("context", "manifest", "TASK-0004")
    lib.check("W3-03b", "a content-hash pin holds and then blocks when the content changes",
              ok_pin and m4b["delivery_state"] == "BLOCKED",
              "before=%s after=%s" % (m4["delivery_state"], json.dumps(m4b["input_violations"])[:300]))
    r.put("spec/requirements/REQ-0001.yaml",
          r.read("spec/requirements/REQ-0001.yaml").replace("priority: high\n", ""))

    # ---- W3.4 reason for each dependency ----------------------------------------------------
    # every entry in a fully declared manifest must carry a reason
    m = r.ok("context", "manifest", "TASK-0001")
    no_reason = [i["id"] for i in m["inputs"] if i["required"] and not i.get("reason")]
    lib.check("W3-04", "every required input records the reason for the dependency",
              not no_reason, "inputs with no reason: %s" % no_reason)

    # ---- W3.5 supplementary context separate from mandatory inputs --------------------------
    pkt = r.ok("context", "compile", "TASK-0002")
    det = json.dumps(pkt["deterministic_authority"])
    supp = pkt["retrieved_intelligence"]
    lib.check("W3-05", "supplementary/retrieved context is a separate block from mandatory inputs",
              "retrieved_intelligence" in pkt and "ranked_evidence" in supp
              and "ranked_evidence" not in det, json.dumps(list(supp.keys())))

    # ---- W3.6 a task cannot become READY / be claimed with an absent mandatory input ---------
    r.put("spec/tasks/TASK-0005.yaml", """id: TASK-0005
type: task
title: missing-input task
status: ACTIVE
class: implementation
task_status: DRAFT
objective: exercise a missing mandatory input
feature: F-0001
requirements: [REQ-0001, REQ-9999]
""")
    ready = r.run("task", "status", "TASK-0005", "READY")
    claim = r.run("task", "claim", "TASK-0005")
    dag = r.ok("task", "dag")
    blocked = [b for b in dag["blocked"] if b["task"] == "TASK-0005"]
    named = blocked and any("REQ-9999" in x for x in blocked[0]["reasons"])
    lib.check("W3-06", "READY and claim are refused, by name, when a mandatory input is absent",
              not ready.get("ok") and ready["error"]["code"] == "TASK_NOT_READY"
              and not claim.get("ok") and claim["error"]["code"] == "TASK_NOT_RUNNABLE"
              and "TASK-0005" not in dag["runnable"] and named,
              json.dumps({"ready": ready.get("error", {}).get("code"),
                          "claim": claim.get("error", {}).get("code"),
                          "blocked": blocked}))
    # the remedy stays available (availability rule): the task can still be inspected and repaired
    lib.check("W3-06b", "the block refuses only the work, not its remedy",
              r.run("context", "manifest", "TASK-0005").get("ok") is True
              and r.run("task", "show", "TASK-0005").get("ok") is True)

    # ---- W3.7 a superseded input cannot silently satisfy a current requirement ---------------
    r.put("spec/requirements/REQ-0010.yaml", """id: REQ-0010
type: requirement
title: Ledger CSV export v2
status: ACTIVE
version: 2
feature: F-0001
kind: functional
supersedes: [REQ-0001]
acceptance_criteria: [CSV contains one row per ledger entry and a header]
summary: the current export requirement
""")
    m = r.ok("context", "manifest", "TASK-0001")
    e = [i for i in m["inputs"] if i["id"] == "REQ-0001"][0]
    viol = [i["id"] for i in m["input_violations"]]
    pkt = r.ok("context", "compile", "TASK-0001")
    delivered_flagged = e["superseded_by"] == "REQ-0010"
    claim = r.run("task", "claim", "TASK-0001")
    lib.check("W3-07", "a superseded input does not satisfy the requirement: BLOCKED, flagged, "
                       "and the task is not claimable",
              m["delivery_state"] == "BLOCKED" and "REQ-0001" in viol and delivered_flagged
              and not claim.get("ok"),
              json.dumps({"state": m["delivery_state"], "violations": viol,
                          "superseded_by": e["superseded_by"],
                          "claim": claim.get("error", {}).get("code")}))
    os.remove(r.path("spec/requirements/REQ-0010.yaml"))

    # ---- W3.8 conflicting mandatory inputs trigger contradiction handling -------------------
    r.put("spec/decisions/D-0200.yaml", """id: D-0200
type: decision
title: Use TSV after all
status: ACTIVE
version: 1
question: Which CSV dialect?
options:
  - {id: TSV, description: tab separated}
chosen_option: TSV
rationale: a later team decided otherwise
conflicts_with: [D-0100]
affects: [TASK-0001]
summary: contradicts D-0100
""")
    m = r.ok("context", "manifest", "TASK-0001")
    con = m.get("contradictions") or []
    pkt = r.ok("context", "compile", "TASK-0001")
    active = [x["id"] for x in pkt["deterministic_authority"]["active_decisions"]]
    conflicting = [x["id"] for x in pkt["deterministic_authority"]["conflicting_decisions"]]
    routed = pkt.get("contradiction_routing") or []
    gates = [g for g in os.listdir(r.path("spec/decisions")) if g.startswith("HG-")]
    claim = r.run("task", "claim", "TASK-0001")
    lib.check("W3-08", "conflicting mandatory inputs are detected, neither is active authority, "
                       "and a human gate is raised",
              bool(con) and "D-0100" not in active and "D-0200" not in active
              and {"D-0100", "D-0200"} <= set(conflicting)
              and (bool(routed) or bool(gates)),
              json.dumps({"contradictions": con, "active": active, "conflicting": conflicting,
                          "routed": routed, "gates": gates})[:600])
    lib.check("W3-08b", "the task cannot be claimed while a mandatory contradiction is unresolved",
              not claim.get("ok"), json.dumps(claim.get("error", {}).get("code")))
    os.remove(r.path("spec/decisions/D-0200.yaml"))
    for g in gates:
        os.rename(r.path("spec/decisions/" + g), os.path.join(r.state, g))

    # ---- W3.9 required inputs resolved deterministically, not by retrieval ranking ----------
    m_with_index = r.ok("context", "manifest", "TASK-0001")
    moved = None
    for cand in (".governance-runtime/state.db", ".governance-runtime/index.db"):
        p = r.path(cand)
        if os.path.exists(p):
            moved = p
            shutil.move(p, p + ".moved-aside")
            break
    m_no_index = r.ok("context", "manifest", "TASK-0001")
    same = (json.dumps(m_with_index["inputs"], sort_keys=True)
            == json.dumps(m_no_index["inputs"], sort_keys=True))
    lib.check("W3-09", "the required-input resolution is byte-identical with the index removed",
              same and moved is not None,
              "index moved aside: %s; identical: %s" % (moved, same))
    if moved:
        shutil.move(moved + ".moved-aside", moved)

    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
