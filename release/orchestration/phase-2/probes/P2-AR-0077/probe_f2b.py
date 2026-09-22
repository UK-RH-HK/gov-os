#!/usr/bin/env python3
"""P2-AR-0077 / AR75-F2 continued: `contract_generated` is not the only consumer
of `class`.

`orchestration::tasks::is_production_path` exempts SIX class values
(`evidence`, `narrative`, `historical`, `generated`, `derived`, `runtime-data`)
from the production tree; an `experiment`-class task (production_merge_allowed
false) is refused `PRODUCTION_MERGE_NOT_ALLOWED` when its mutations land there.
The repair's `confers_generated_exemption` names only `generated`/`derived`, so
the other four are still uncompared.

Proof standard: a `gov task close` on an experiment task whose declared write
lands in `product/` -- refused, or accepted.
"""
import json
from harness4 import fresh, save

TARGET = "product/experimental.yaml"


def attempt(tag, appended_rule_yaml, note=""):
    p = fresh(f"f2b-{tag}")
    row = {"case": tag, "rule": appended_rule_yaml, "note": note}
    if appended_rule_yaml:
        c = p.root / "governance/project/REPOSITORY_CONTRACT.yaml"
        lines = c.read_text().split("\n")
        start = next(i for i, l in enumerate(lines) if l.startswith("paths:"))
        end = next((i for i in range(start + 1, len(lines))
                    if lines[i] and not lines[i][0].isspace() and not lines[i].startswith("-")),
                   len(lines))
        c.write_text("\n".join(lines[:end] + appended_rule_yaml.rstrip("\n").split("\n") + lines[end:]))
        p.commit_all("append a path rule by hand")

    pol = p.run(["policy", "overrides"])
    ref = ((pol.get("result") or {}).get("refused")) or []
    row["rule_refused"] = [x for x in ref if "product/*.yaml" in json.dumps(x)]
    row["rule_was_refused"] = bool(row["rule_refused"])

    t = p.ok(["task", "create", "--class", "experiment",
              "--objective", f"P2-AR-0077 {tag}", "--status", "READY"])["id"]
    p.ok(["task", "claim", t], session="S-w", role="backend-engineer")
    p.ok(["rebuild-memory", "--incremental"], session="S-w", role="backend-engineer")
    pk = p.ok(["context", "compile", t], session="S-w", role="backend-engineer")
    rc = pk["receipt_contract"]

    # DECLARED (so no MUTATION_SCOPE_VIOLATION) but in the PRODUCTION tree
    p.write(TARGET, "experimental: true\n")

    rec = {"work_completed": f"P2-AR-0077 {tag}", "files_changed": [TARGET],
           "tests": {"status": "not_applicable_with_reason", "reason": "P2-AR-0077 probe"},
           "outcome": "success", "evidence": [], "context_packet_hash": pk["packet_hash"],
           "inputs_consumed": [f"{e.get('id','')}@{e.get('content_hash','')}"
                               for e in (rc.get("acknowledge_inputs") or [])],
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

    e = p.run(["task", "close", t, "--report", str(f)], session="S-w", role="backend-engineer")
    row["close_ok"] = e.get("ok")
    row["close_error"] = (e.get("error") or {}).get("code")
    st = p.run(["task", "show", t]).get("result") or {}
    row["task_status"] = st.get("task_status") or (st.get("task") or {}).get("task_status")
    # the STATE effect: the task record reached DONE with a production path in its close
    row["ESCAPED"] = bool(e.get("ok"))
    # and the governance suite's own after-the-fact sweep
    d = p.run(["doctor"])
    dj = json.dumps(d.get("result") or d.get("error"))
    row["doctor_mentions_production"] = "forbids production merge" in dj
    print(f"{tag:22s} rule_refused={row['rule_was_refused']} close_ok={row['close_ok']} "
          f"err={row['close_error']} status={row['task_status']} ESCAPED={row['ESCAPED']} "
          f"doctor_flags={row['doctor_mentions_production']}")
    return row


def rule(cls):
    return f"- pattern: product/*.yaml\n  class: {cls}\n  owner_role: backend-engineer\n"


rows = [attempt("C0-no-rule", None, note="control: experiment output in product/ is refused")]
for cls in ["evidence", "narrative", "historical", "runtime-data", "derived", "generated"]:
    rows.append(attempt(f"X-{cls}", rule(cls),
                        note=f"is_production_path exempts class {cls}"))
save("f2b", rows)
print("\n=== EXPERIMENT CLOSES THAT LANDED IN THE PRODUCTION TREE ===")
for r in rows:
    if r["ESCAPED"]:
        print(f"  {r['case']} (rule refused: {r['rule_was_refused']}, doctor flags: "
              f"{r['doctor_mentions_production']})")
