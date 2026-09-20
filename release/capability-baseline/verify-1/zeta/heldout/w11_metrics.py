"""W11 — artifact-flow quantitative health (Contract v3:1173-1183). Held-out, P2-AR-0051.

Every metric must be computed with its numerator and denominator AND must move when the fault it
measures is injected. A metric that is only ever `null` is not tracked.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402

METRICS = ["required_input_delivery_accuracy", "current_version_selection_accuracy",
           "superseded_input_leakage_rate", "missing_required_input_detection",
           "staleness_propagation_accuracy", "requirement_to_code_traceability_coverage",
           "requirement_to_test_traceability_coverage", "orphan_detection",
           "fresh_agent_reconstruction_correctness"]


def flow(r, tier="G4"):
    h = r.run("health", "run", "--tier", tier)
    res = h.get("result") or (h.get("error") or {}).get("details") or {}
    fam = (res.get("families") or {}).get("artifact_flow_health") or {}
    findings = [f for f in (res.get("findings") or [])
                if f.get("family") == "artifact_flow_health"]
    return (fam.get("detail") or {}).get("w11_metrics") or {}, fam, findings


def closed_task(r, tid, src):
    lib.seed_task(r, tid, fields={"required_data": ["DATA-0002"]})
    r.ok("task", "status", tid, "READY")
    r.ok("task", "claim", tid, role="backend-engineer", session="impl1")
    r.put(src, "// implements REQ-0001\npub fn f%s() {}\n" % tid[-4:])
    r.ok("rebuild-memory", "--incremental")
    r.ok("verify", "product")
    rep = r.receipt(tid, [src], work="implemented the export")
    out = r.close(tid, rep, role="backend-engineer", session="impl1")
    assert out.get("ok"), json.dumps(out.get("error"))[:600]
    return out["result"]


def main():
    r = lib.Repo("w11")
    lib.seed_green(r)
    closed_task(r, "TASK-0001", "src/export.rs")
    r.commit("implemented")

    m0, fam0, _ = flow(r)

    # ---- all nine metrics exist, each with its contract line, numerator and denominator -----
    missing = [k for k in METRICS if k not in m0]
    shaped = {k: sorted(set(m0.get(k, {}).keys()) &
                        {"numerator", "denominator", "value", "contract", "applicable",
                         "orphans_detected", "orphan_detection_precision"})
              for k in METRICS if k in m0}
    lib.check("W11-01", "all nine W11 metrics are computed and reported, each citing its contract "
                        "line, with a numerator and a denominator (or, for orphan detection, its "
                        "counts)",
              not missing and all(m0[k].get("contract") for k in METRICS)
              and all(("numerator" in m0[k] and "denominator" in m0[k])
                      or "orphans_detected" in m0[k] for k in METRICS),
              json.dumps({"missing": missing, "shape": shaped})[:700])

    # a declared target per metric (and the leakage-rate maximum)
    d = fam0.get("detail") or {}
    targets = {t["metric"] for t in d.get("targets") or []}
    lib.check("W11-02", "each metric carries a declared target (and the leakage rate a maximum)",
              len(targets) >= 8 and d.get("max_superseded_input_leakage_rate") is not None,
              json.dumps({"targets": sorted(targets),
                          "max_leakage": d.get("max_superseded_input_leakage_rate")}))

    # ---- now inject a fault per metric and show the metric moves ----------------------------
    moved = {}

    # (a) requirement -> code / test traceability coverage: an unimplemented requirement
    base_code = m0["requirement_to_code_traceability_coverage"]
    r.put("spec/requirements/REQ-0700.yaml", """id: REQ-0700
type: requirement
title: Untraced requirement
status: ACTIVE
version: 1
kind: functional
acceptance_criteria: [it does something nothing implements]
summary: nothing implements or tests this
""")
    r.commit("untraced requirement")
    r.ok("rebuild-memory", "--incremental")
    m1, _, _ = flow(r)
    moved["requirement_to_code_traceability_coverage"] = (
        base_code.get("value"), m1["requirement_to_code_traceability_coverage"].get("value"),
        m1["requirement_to_code_traceability_coverage"]["detail"].get("uncovered"))
    moved["requirement_to_test_traceability_coverage"] = (
        m0["requirement_to_test_traceability_coverage"].get("value"),
        m1["requirement_to_test_traceability_coverage"].get("value"),
        m1["requirement_to_test_traceability_coverage"]["detail"].get("uncovered"))
    lib.check("W11-03", "requirement->code and requirement->test coverage fall and name the "
                        "uncovered requirement when an unimplemented requirement is added",
              m1["requirement_to_code_traceability_coverage"]["value"] < 1.0
              and "REQ-0700" in (m1["requirement_to_code_traceability_coverage"]["detail"]
                                 .get("uncovered") or [])
              and "REQ-0700" in (m1["requirement_to_test_traceability_coverage"]["detail"]
                                 .get("uncovered") or []),
              json.dumps(moved)[:500])

    # (b) missing_required_input_detection: a task STORED as READY whose manifest lacks a
    #     mandatory input (the exact fault the metric names: "stored or offered as runnable")
    r.put("spec/tasks/TASK-0700.yaml", """id: TASK-0700
type: task
title: live task with a missing mandatory input
status: ACTIVE
class: implementation
task_status: READY
objective: exercise the missing-required-input metric
feature: F-0001
required_inputs:
  - {id: REQ-9999, reason: a requirement that does not exist}
""")
    r.commit("missing input task")
    r.ok("rebuild-memory", "--incremental")
    m2, _, f2 = flow(r)
    mri = m2["missing_required_input_detection"]
    runnable = "TASK-0700" in json.dumps(r.ok("task", "dag").get("runnable"))
    lib.check("W11-04", "missing-required-input detection becomes applicable and names the task "
                        "stored as READY and the input it lacks; the DAG still refuses to offer "
                        "it as runnable",
              mri.get("applicable") is True and mri.get("denominator", 0) > 0
              and "TASK-0700" in json.dumps(mri) and "REQ-9999" in json.dumps(mri)
              and not runnable,
              json.dumps({"metric": mri, "offered_as_runnable": runnable})[:600])

    # (c) required-input delivery accuracy and current-version selection accuracy:
    #     deliver a packet for a live task, then change one of the inputs it delivered
    lib.seed_task(r, "TASK-0800", fields={"required_data": ["DATA-0002"]})
    r.ok("task", "status", "TASK-0800", "READY")
    r.ok("context", "compile", "TASK-0800")
    m3, _, _ = flow(r)
    delivered_applicable = m3["required_input_delivery_accuracy"].get("applicable")
    version_applicable = m3["current_version_selection_accuracy"].get("applicable")
    lib.check("W11-05", "required-input delivery accuracy and current-version selection accuracy "
                        "become applicable once a packet has been delivered",
              delivered_applicable is True and version_applicable is True,
              json.dumps({"delivery": m3["required_input_delivery_accuracy"],
                          "version": m3["current_version_selection_accuracy"]})[:600])

    r.put("spec/requirements/REQ-0001.yaml",
          r.read("spec/requirements/REQ-0001.yaml").replace(
              "CSV contains one row per ledger entry",
              "CSV contains one row per ledger entry, plus a header"))
    m4, _, f4 = flow(r)
    cvs = m4["current_version_selection_accuracy"]
    lib.check("W11-06", "current-version selection accuracy falls and names the input that has "
                        "changed since it was delivered",
              cvs.get("value") is not None and cvs["value"] < 1.0
              and "REQ-0001" in json.dumps(cvs.get("detail")),
              json.dumps(cvs)[:500])

    # (d) staleness propagation accuracy: the same direct edit, before propagation runs
    sp = m4["staleness_propagation_accuracy"]
    lib.check("W11-07", "staleness propagation accuracy becomes applicable and names the "
                        "(task, input) pair whose input changed since the work consumed it",
              sp.get("applicable") is True and "REQ-0001" in json.dumps(sp),
              json.dumps(sp)[:500])

    # (e) superseded input leakage: a DONE task whose governing input is now superseded
    r.put("spec/requirements/REQ-0800.yaml", """id: REQ-0800
type: requirement
title: Ledger CSV export v2
status: ACTIVE
version: 2
feature: F-0001
kind: functional
supersedes: [REQ-0001]
acceptance_criteria: [CSV contains one row per ledger entry, plus a header]
summary: supersedes REQ-0001
""")
    r.commit("supersede")
    r.ok("rebuild-memory", "--incremental")
    m5, _, f5 = flow(r)
    leak = m5["superseded_input_leakage_rate"]
    lib.check("W11-08", "superseded-input leakage rate is measured over the governing inputs of "
                        "live and DONE work, with its denominator",
              leak.get("applicable") is True and leak.get("denominator", 0) > 0
              and leak.get("value") is not None,
              json.dumps(leak)[:500])

    # (f) orphan detection and fresh-agent reconstruction
    m6, fam6, f6 = flow(r)
    orph = m6["orphan_detection"]
    fresh = m6["fresh_agent_reconstruction_correctness"]
    lib.check("W11-09", "orphan detection reports detected counts per W7 kind and the outcome of "
                        "its investigations (precision / false positives)",
              orph.get("orphans_detected", 0) > 0 and "by_kind" in orph
              and "investigations" in orph,
              json.dumps({k: orph[k] for k in ("orphans_detected", "by_kind", "investigations")})[:500])
    lib.check("W11-09b", "orphan-detection recall is explicitly stated as not measurable in the "
                         "governed repository, with the reason and the tier that measures it "
                         "(never silently null)",
              orph.get("orphan_detection_recall") is None and bool(orph.get("recall_source")),
              json.dumps(orph.get("recall_source")))
    lib.check("W11-10", "fresh-agent reconstruction correctness is measured by named probes",
              fresh.get("applicable") is True and bool(fresh.get("probes"))
              and fresh.get("denominator", 0) > 0,
              json.dumps(fresh)[:500])

    # ---- a metric below its target is disclosed as a finding --------------------------------
    below = [f for f in f6 if "below its target" in f.get("message", "")]
    lib.check("W11-11", "a metric below its declared target is disclosed as a finding naming the "
                        "metric, its value and its target",
              bool(below) and all("W11" in f["message"] for f in below),
              json.dumps([f["message"][:130] for f in below])[:600])

    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
