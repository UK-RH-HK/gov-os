"""W10 — deterministic mandatory inputs outrank retrieval (Contract v3:1162-1171).

The five "Verify" bullets, each by construction. Held-out, P2-AR-0051.
"""
import json
import os
import shutil
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402

INDEX = ".governance-runtime/state.db"


def index_rows(r, art):
    c = sqlite3.connect(r.path(INDEX))
    try:
        n = c.execute("select count(*) from chunks where artifact_id=?", (art,)).fetchone()[0]
        v = c.execute("select count(*) from vectors").fetchone()[0]
        return n, v
    finally:
        c.close()


def main():
    r = lib.Repo("w10")
    lib.seed_green(r)
    lib.seed_task(r, "TASK-0001", fields={"required_data": ["DATA-0002"]})
    r.ok("rebuild-memory", "--incremental")
    r.commit("seed")
    base = r.ok("context", "compile", "TASK-0001")
    base_ids = set(base["input_hashes"])

    # ---- W10.1 the current spec is delivered even when it is absent from the semantic index ---
    before_chunks, _ = index_rows(r, "REQ-0001")
    c = sqlite3.connect(r.path(INDEX))
    c.execute("delete from vectors where artifact_id=?", ("REQ-0001",))
    c.execute("delete from chunks where artifact_id=?", ("REQ-0001",))
    c.execute("delete from artifacts where artifact_id=?", ("REQ-0001",))
    c.commit()
    c.close()
    after_chunks, _ = index_rows(r, "REQ-0001")
    pkt = r.ok("context", "compile", "TASK-0001")
    req_ids = [x["id"] for x in pkt["deterministic_authority"]["governing_requirements"]]
    retrieved = json.dumps(pkt["retrieved_intelligence"])
    lib.check("W10-01", "a current spec deleted from the semantic index is still delivered as a "
                        "mandatory input, with its content",
              before_chunks > 0 and after_chunks == 0 and "REQ-0001" in req_ids
              and pkt["delivery_state"] == "COMPLETE"
              and pkt["input_hashes"].get("REQ-0001"),
              json.dumps({"chunks_before": before_chunks, "chunks_after": after_chunks,
                          "delivered": req_ids, "state": pkt["delivery_state"],
                          "in_retrieval": "REQ-0001" in retrieved}))
    r.ok("rebuild-memory")

    # ---- W10.2 a superseded but semantically similar spec cannot replace the current spec -----
    # F-0002/REQ-0020 is the current obligation the task declares. REQ-0030 is superseded and is
    # authored to match the task's own words, so retrieval ranks it high; it stays indexed.
    readiness = "\n".join("  %s: PRESENT" % c for c in lib.READINESS_CELLS)
    r.put("spec/features/F-0002.yaml", """id: F-0002
type: feature
title: Tabular extract
status: ACTIVE
readiness:
%s
requirements: [REQ-0020]
summary: tabular extract feature
""" % readiness)
    r.put("spec/requirements/REQ-0020.yaml", """id: REQ-0020
type: requirement
title: Tabular extract obligation
status: ACTIVE
version: 2
feature: F-0002
kind: functional
supersedes: [REQ-0030]
acceptance_criteria: [one record per ledger entry, plus a header row]
summary: the current, authoritative export obligation
""")
    r.put("spec/requirements/REQ-0030.yaml", """id: REQ-0030
type: requirement
title: stream the ledger to a flat file fast
status: SUPERSEDED
version: 1
kind: functional
superseded_by: REQ-0020
acceptance_criteria: [stream the ledger to a flat file fast, stream the ledger to a flat file fast]
summary: stream the ledger to a flat file fast - stream the ledger to a flat file fast
""")
    r.put("spec/tasks/TASK-0020.yaml", """id: TASK-0020
type: task
title: stream the ledger to a flat file fast
status: ACTIVE
class: implementation
task_status: DRAFT
objective: stream the ledger to a flat file fast
feature: F-0002
required_inputs:
  - {id: REQ-0020, reason: the current export obligation}
""")
    r.ok("rebuild-memory")
    p20 = r.ok("context", "compile", "TASK-0020")
    delivered = [x["id"] for x in p20["deterministic_authority"]["governing_requirements"]]
    ranked = [h["artifact_id"] for h in p20["retrieved_intelligence"]["ranked_evidence"]]
    superseded_ranked = "REQ-0030" in ranked
    lib.check("W10-02", "the current required spec is delivered and the superseded, more "
                        "semantically similar one is not (it reaches the worker only as "
                        "supplementary retrieval, if at all)",
              "REQ-0020" in delivered and "REQ-0030" not in delivered
              and p20["delivery_state"] == "COMPLETE",
              json.dumps({"mandatory": delivered, "state": p20["delivery_state"],
                          "retrieval_ranking": ranked[:8],
                          "superseded_in_retrieval": superseded_ranked}))
    # and the superseded record cannot satisfy the slot even if a task names it explicitly
    r.put("spec/tasks/TASK-0021.yaml", """id: TASK-0021
type: task
title: stream the ledger to a flat file fast
status: ACTIVE
class: implementation
task_status: DRAFT
objective: stream the ledger to a flat file fast
feature: F-0002
required_inputs:
  - {id: REQ-0030, reason: names the superseded spec}
""")
    m21 = r.ok("context", "manifest", "TASK-0021")
    lib.check("W10-02b", "naming the superseded spec explicitly blocks rather than silently passing",
              m21["delivery_state"] == "BLOCKED"
              and "REQ-0030" in [i["id"] for i in m21["input_violations"]],
              json.dumps(m21["input_violations"])[:350])

    # ---- W10.3 token pressure drops supplementary before mandatory --------------------------
    b = r.ok("context", "compile", "TASK-0020")
    pp = r.read("governance/project/PROJECT_POLICY.yaml").replace(
        "policy_overrides: {}", 'policy_overrides: {"CONTEXT_POLICY.max_packet_chars": 9000}')
    r.put("governance/project/PROJECT_POLICY.yaml", pp)
    s = r.ok("context", "compile", "TASK-0020")
    supp_before = len(b["retrieved_intelligence"]["ranked_evidence"])
    supp_after = len(s["retrieved_intelligence"]["ranked_evidence"])
    lib.check("W10-03", "token pressure drops supplementary slices and leaves every mandatory "
                        "input at its full content",
              s["input_hashes"] == b["input_hashes"] and supp_after < supp_before
              and s["deterministic_authority"]["governing_requirements"] ==
              b["deterministic_authority"]["governing_requirements"]
              and s["delivery_state"] == "COMPLETE",
              json.dumps({"supplementary_before": supp_before, "supplementary_after": supp_after,
                          "delivery_state": s["delivery_state"], "budget": s["budget"]}))
    pp = r.read("governance/project/PROJECT_POLICY.yaml").replace(
        'policy_overrides: {"CONTEXT_POLICY.max_packet_chars": 9000}', "policy_overrides: {}")
    r.put("governance/project/PROJECT_POLICY.yaml", pp)
    b = r.ok("context", "compile", "TASK-0020")

    # ---- W10.4 a retrieval / index outage does not erase deterministic dependencies ----------
    for kind, mutate in (("index removed", "remove"), ("index corrupt", "corrupt")):
        p = r.path(INDEX)
        shutil.move(p, p + ".aside")
        if mutate == "corrupt":
            with open(p, "wb") as f:
                f.write(b"this is not a sqlite database" * 100)
        out = r.run("context", "compile", "TASK-0020")
        ok = out.get("ok")
        res = out.get("result") or {}
        full = (ok and res.get("delivery_state") == "COMPLETE"
                and res.get("input_hashes") == b["input_hashes"]
                and res["deterministic_authority"]["governing_requirements"] ==
                b["deterministic_authority"]["governing_requirements"])
        degraded = res.get("supplementary_state") == "DEGRADED"
        reasons = json.dumps((res.get("retrieved_intelligence") or {}).get("degraded"))
        lib.check("W10-04-" + mutate,
                  "with the %s, the mandatory inputs are delivered whole and only the "
                  "supplementary block is marked DEGRADED, with its reason and remedy" % kind,
                  full and degraded and "remediation" in reasons,
                  json.dumps({"ok": ok, "delivery_state": res.get("delivery_state"),
                              "supplementary_state": res.get("supplementary_state"),
                              "inputs_identical": res.get("input_hashes") == b["input_hashes"],
                              "degraded": (res.get("retrieved_intelligence") or {}).get("degraded")})[:600])
        if os.path.exists(p):
            os.rename(p, p + ".broken")
        shutil.move(p + ".aside", p)

    # ---- W10.5 required-input delivery is independently testable ----------------------------
    r.ok("context", "compile", "TASK-0020")
    v = r.run("context", "verify", "TASK-0020")
    h = r.run("health", "run", "--tier", "G4")
    fams = (h.get("result") or {}).get("families") or {}
    cr = fams.get("context_reproducibility")
    vr = v.get("result") or {}
    lib.check("W10-05", "delivery is independently testable: a delivered packet verifies against "
                        "the declared manifest, and the context_reproducibility family re-checks "
                        "every dispatchable task",
              v.get("ok") and vr.get("ok") is True and cr is not None,
              json.dumps({"verify": vr, "context_reproducibility": cr})[:500])
    # ... and the verification actually fails when the delivered packet no longer matches
    r.put("spec/requirements/REQ-0020.yaml",
          r.read("spec/requirements/REQ-0020.yaml").replace("plus a header row",
                                                            "plus a header row and a checksum"))
    v2 = r.run("context", "verify", "TASK-0020")
    vr2 = v2.get("result") or {}
    failed = vr2.get("ok") is False and "REQ-0020" in json.dumps(vr2.get("stale_inputs") or [])
    lib.check("W10-05b", "that verification fails, by name, when a delivered input has changed since",
              failed, json.dumps(vr2)[:400])

    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
