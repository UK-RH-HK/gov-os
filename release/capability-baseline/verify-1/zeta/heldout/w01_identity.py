"""W1 — stable artefact identity (Contract v3:1068-1080). Held-out, P2-AR-0051.

Nine attributes, on every governed artefact type W1:1080 names, plus the properties that make the identity
*stable*: it survives a file move, and a producer that re-runs yields the same id for the same output.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402

ATTRS = ["id", "type", "canonical_dir", "authoritative_status", "lifecycle_state",
         "content_hash", "provenance", "superseded_by", "expected_consumers"]


def main():
    r = lib.Repo("w01")
    lib.seed_green(r)
    lib.seed_task(r, "TASK-0001", fields={"required_data": ["DATA-0002"]})
    r.commit("seed")

    # ---- W1.1-W1.9 on one artefact of every type the applies-to line names -------------------
    types = {"requirement (specification)": "REQ-0001", "feature (specification)": "F-0001",
             "scenario": "SCN-0001", "decision": "D-0100", "dataset": "DATA-0002",
             "architecture": "ARCH-0100", "interface": "IFC-0001", "test design": "TO-0001",
             "task": "TASK-0001"}
    missing = {}
    for label, rid in types.items():
        v = r.ok("artefact", "show", rid)
        gaps = [a for a in ATTRS if a not in v]
        if v.get("version") is None and v.get("content_hash") is None:
            gaps.append("version/content hash")
        if gaps:
            missing[label] = gaps
    lib.check("W1-01", "nine W1 attributes on every core artefact type", not missing, missing)

    # ---- experiments and research (W1:1080 "experiments") -----------------------------------
    r.ok("research", "record", "--fields", json.dumps(lib.RESEARCH), role="research-agent")
    ex = r.run("experiment", "design", "--fields", json.dumps({
        "id": "EXP-0001", "title": "throughput of the exporter",
        "hypothesis": "streaming is faster", "method": "benchmark both dialects",
        "data": ["DATA-0002"], "outputs": ["spec/experiments/EXP-0001-out.json"],
        "production_merge_allowed": False,
        "success_criteria": ["streaming wins"], "metrics": ["rows/s"]}), role="research-agent")
    ok_exp = ex.get("ok")
    ids = ["RES-0001"] + (["EXP-0001"] if ok_exp else [])
    gaps = {}
    for rid in ids:
        v = r.run("artefact", "show", rid)
        if not v.get("ok"):
            gaps[rid] = v.get("error", {}).get("code")
            continue
        g = [a for a in ATTRS if a not in v["result"]]
        if g:
            gaps[rid] = g
    lib.check("W1-02", "research/experiment records carry the W1 attributes",
              not gaps and ok_exp, gaps or ("experiment design refused: %s" % json.dumps(ex.get("error"))[:200] if not ok_exp else ""))

    # ---- W1.1 stable across a move; W1.3 a misplaced record is reported ---------------------
    before = r.ok("artefact", "show", "REQ-0001")
    os.makedirs(r.path("spec/moved"), exist_ok=True)
    os.rename(r.path("spec/requirements/REQ-0001.yaml"), r.path("spec/moved/REQ-0001.yaml"))
    after = r.run("artefact", "show", "REQ-0001")
    same_id = after.get("ok") and after["result"]["id"] == before["id"]
    same_hash = after.get("ok") and after["result"]["content_hash"] == before["content_hash"]
    chk = r.ok("artefact", "check")
    misplaced = json.dumps(chk.get("misplaced_records", chk)).find("REQ-0001") >= 0
    lib.check("W1-03", "stable id and content hash survive a file move", same_id and same_hash,
              json.dumps(after)[:200] if not (same_id and same_hash) else "")
    lib.check("W1-04", "a record outside its canonical path is reported by name", misplaced,
              json.dumps(chk)[:300])
    os.rename(r.path("spec/moved/REQ-0001.yaml"), r.path("spec/requirements/REQ-0001.yaml"))
    os.rmdir(r.path("spec/moved"))

    # ---- W1 audit findings: stable, content-derived ids across a re-run ---------------------
    def finding_ids():
        out = r.run("audit")
        res = out.get("result") or out.get("error", {}).get("details", {})
        aid = res.get("audit")
        import yaml
        d = yaml.safe_load(open(r.path("spec/audits/%s.yaml" % aid)))
        return {f["id"]: f["message"] for f in (d.get("findings") or [])}

    a1 = finding_ids()
    a2 = finding_ids()
    stable = set(a1) == set(a2) and all(a1[k] == a2[k] for k in a1)
    positional = any(not k.startswith("GF-") for k in a1)
    lib.check("W1-05", "audit finding ids are content-derived and stable across re-runs",
              bool(a1) and stable and not positional,
              "ids run1=%s run2=%s" % (sorted(a1)[:3], sorted(a2)[:3]))

    # ---- W1.7 provenance: declared on OS-written records, version control on authored ones --
    rpt = [f for f in os.listdir(r.path("spec/reports")) if f.startswith("RPT-")]
    prov_os = r.ok("artefact", "show", rpt[0].replace(".yaml", ""))["provenance"]
    has_declared = bool(prov_os.get("declared"))
    r.commit("commit records")
    prov_authored = r.ok("artefact", "show", "REQ-0001")["provenance"]
    vc = prov_authored.get("version_control") or {}
    has_vc = bool(vc.get("introduced_by")) and bool(vc.get("last_changed_by"))
    lib.check("W1-06", "producer/provenance: declared on OS-written records", has_declared,
              json.dumps(prov_os)[:200])
    lib.check("W1-07", "producer/provenance: version control on authored records", has_vc,
              json.dumps(prov_authored)[:250])

    # ---- W1.8 supersession lineage, both directions -----------------------------------------
    r.put("spec/requirements/REQ-0002.yaml", """id: REQ-0002
type: requirement
title: Ledger CSV export (revised)
status: ACTIVE
version: 2
feature: F-0001
kind: functional
supersedes: [REQ-0001]
acceptance_criteria: [CSV contains one row per ledger entry, with a header]
summary: revised export requirement
""")
    old = r.ok("artefact", "show", "REQ-0001")
    new = r.ok("artefact", "show", "REQ-0002")
    lib.check("W1-08", "supersedes / superseded-by lineage is derived in both directions",
              old.get("superseded_by") == "REQ-0002" and new.get("supersedes") == ["REQ-0001"],
              "old.superseded_by=%s new.supersedes=%s" % (old.get("superseded_by"),
                                                          new.get("supersedes")))

    # ---- W1.9 expected vs actual downstream consumers ---------------------------------------
    v = r.ok("artefact", "show", "REQ-0001")
    lib.check("W1-09", "expected consumers (declared) and actual consumers are both reported",
              v.get("expected_consumers") == ["TASK-0001"] and "TASK-0001" in (v.get("actual_consumers") or []),
              json.dumps({"expected": v.get("expected_consumers"),
                          "actual": v.get("actual_consumers")}))

    # a declared consumer that does not exist must be visible, not silently dropped
    r.put("spec/architecture/ARCH-0100.yaml",
          r.read("spec/architecture/ARCH-0100.yaml") + "consumers: [TASK-9999]\n")
    chk = r.ok("artefact", "check")
    un = chk.get("unconsumed_outputs") or []
    hit = [u for u in un if u["record"] == "ARCH-0100" and "TASK-9999" in u.get("missing_consumers", [])]
    lib.check("W1-10", "a declared downstream consumer that does not exist is reported by name",
              bool(hit), json.dumps(un)[:400])

    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
