#!/usr/bin/env python3
"""P2-AR-0077 / AR75-F2 continued, end to end.

`is_production_path` is consulted by THREE controls:
  * `EXPERIMENT_OUTPUT_IN_PRODUCTION` (lifecycle/experiment.rs:883) -- design time
  * `PRODUCTION_MERGE_NOT_ALLOWED`    (tasks.rs:2125)                -- close time
  * the governance-suite sweep        (tasks.rs:2662/2677)           -- after the fact
and it exempts SIX class values. The AR75-F2 repair compares only two of them, so
`class: evidence` (and narrative/historical/runtime-data) is accepted, unreported,
and takes all three controls off the path.

Proof standard: an experiment record that names a PRODUCTION path as its output
and exists on disk; and an experiment task that closes DONE with a production
write in its report.
"""
import json
from harness4 import fresh, save

TARGET = "product/experimental.yaml"
RULE = "- pattern: product/*.yaml\n  class: evidence\n  owner_role: backend-engineer\n"


def append_rule(p, rule_yaml):
    c = p.root / "governance/project/REPOSITORY_CONTRACT.yaml"
    lines = c.read_text().split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("paths:"))
    end = next((i for i in range(start + 1, len(lines))
                if lines[i] and not lines[i][0].isspace() and not lines[i].startswith("-")),
               len(lines))
    c.write_text("\n".join(lines[:end] + rule_yaml.rstrip("\n").split("\n") + lines[end:]))
    p.commit_all("append a path rule by hand")


def run(tag, with_rule):
    p = fresh(f"f2c-{tag}")
    row = {"case": tag, "with_rule": with_rule}
    if with_rule:
        append_rule(p, RULE)
        pol = p.run(["policy", "overrides"])
        ref = ((pol.get("result") or {}).get("refused")) or []
        row["rule_refused"] = bool([x for x in ref if "product/*.yaml" in json.dumps(x)])
        row["policy_overrides_refused_total"] = len(ref)
        # every reporting surface the orchestration names
        doc = p.run(["doctor"])
        row["doctor_ok"] = doc.get("ok")
        row["doctor_mentions_rule"] = "product/*.yaml" in json.dumps(doc.get("result") or doc.get("error"))

    p.write("fixtures/traffic.csv", "t,ms\n1,40\n2,18\n")
    p.commit_all("experiment input")
    p.ok(["rebuild-memory"])

    # --- control 1: EXPERIMENT_OUTPUT_IN_PRODUCTION ------------------------
    design = {"hypothesis": "P2-AR-0077", "method": "probe",
              "inputs": [{"path": "fixtures/traffic.csv"}],
              "outputs": [TARGET],
              "reproducibility": {"acceptance": {"mode": "tolerance", "relative": 0.05}}}
    e = p.run(["experiment", "design", "--fields", json.dumps(design)],
              session="S-x", role="research-agent")
    row["design_ok"] = e.get("ok")
    row["design_error"] = (e.get("error") or {}).get("code")
    eid = ((e.get("result") or {}).get("experiment") or {}).get("id")
    row["experiment_id"] = eid
    if eid:
        # THE STATE EFFECT: a governed experiment record naming a production path
        recs = list((p.root / "spec" / "experiments").glob("*")) if (p.root / "spec" / "experiments").exists() else []
        row["experiment_record_files"] = [x.name for x in recs]
        row["EXPERIMENT_RECORD_NAMES_PRODUCTION_OUTPUT"] = any(
            TARGET in x.read_text() for x in recs if x.is_file())

        # --- control 2: PRODUCTION_MERGE_NOT_ALLOWED at close -------------
        t = p.ok(["task", "create", "--class", "experiment",
                  "--objective", f"P2-AR-0077 {tag}", "--status", "READY"])["id"]
        p.ok(["task", "claim", t], session="S-w", role="backend-engineer")
        r = p.run(["experiment", "run", eid, "--results", json.dumps({"p95_ms": 18.0}),
                   "--task", t], session="S-w", role="backend-engineer")
        row["run_ok"] = r.get("ok")
        row["run_error"] = (r.get("error") or {}).get("code")
        p.ok(["rebuild-memory", "--incremental"], session="S-w", role="backend-engineer")
        pk = p.ok(["context", "compile", t], session="S-w", role="backend-engineer")
        rc = pk["receipt_contract"]
        p.write(TARGET, "experimental: true\n")
        rec = {"work_completed": f"P2-AR-0077 {tag}", "files_changed": [TARGET],
               "tests": {"status": "not_applicable_with_reason", "reason": "probe"},
               "outcome": "success", "evidence": [], "context_packet_hash": pk["packet_hash"],
               "inputs_consumed": [f"{x.get('id','')}@{x.get('content_hash','')}"
                                   for x in (rc.get("acknowledge_inputs") or [])],
               "outputs_produced": [],
               "requirements_implemented": rc["trace"]["requirements"],
               "scenarios_implemented": rc["trace"]["scenarios"],
               "features_implemented": rc["trace"]["features"],
               "decisions_applied": rc["trace"]["decisions"],
               "constraints_applied": rc["trace"]["constraints"],
               "acceptance_evidence": [{"test": x, "result": "passed", "evidence": "probe"}
                                       for x in (rc.get("tests_requiring_evidence") or [])],
               "deviations": [], "unresolved": []}
        rd = p.root / ".governance-runtime" / "reports"
        rd.mkdir(parents=True, exist_ok=True)
        f = rd / f"{tag}.json"
        f.write_text(json.dumps(rec))
        c = p.run(["task", "close", t, "--report", str(f)], session="S-w", role="backend-engineer")
        row["close_ok"] = c.get("ok")
        row["close_error"] = (c.get("error") or {}).get("code")
        st = p.run(["task", "show", t]).get("result") or {}
        row["task_status"] = st.get("task_status") or (st.get("task") or {}).get("task_status")

        # --- control 3: the after-the-fact sweep --------------------------
        chk = p.run(["experiment", "check"])
        row["experiment_check_ok"] = chk.get("ok")
        row["experiment_check_flags_production"] = (
            "production" in json.dumps(chk.get("result") or chk.get("error")).lower())
        doc = p.run(["doctor"])
        row["doctor_flags_production_merge"] = (
            "forbids production merge" in json.dumps(doc.get("result") or doc.get("error")))

    print(json.dumps(row, indent=1, default=str)[:1500])
    return row


rows = [run("C0-no-rule", False), run("X-evidence", True)]
save("f2c", rows)
