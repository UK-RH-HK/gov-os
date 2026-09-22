#!/usr/bin/env python3
"""P2-AR-0077 / AR75-F2: can a project-editable path rule still manufacture an
exemption from governed observation by declaring a `class`?

Proof standard: a `gov task close` that SHOULD be refused (an undeclared,
out-of-scope write to a production path) and either is or is not. The state effect
is the close -- the task record reaching DONE with the write unobserved -- not a
status field.

Every case appends ONE rule to the project-editable
`governance/project/REPOSITORY_CONTRACT.yaml` and changes nothing else.
"""
import json, re, pathlib
from harness4 import fresh, save

CTRL = "product/undeclared.yaml"          # a production path the task never declares


def attempt(tag, appended_rule_yaml, *, target=CTRL, task_class=None,
            report_declares=(), note=""):
    """One project: append the rule (if any), then try the undeclared write + close."""
    p = fresh(f"f2-{tag}")
    row = {"case": tag, "rule": appended_rule_yaml, "target": target,
           "task_class": task_class, "note": note}
    row["append_index"] = None

    if appended_rule_yaml:
        c = p.root / "governance/project/REPOSITORY_CONTRACT.yaml"
        lines = c.read_text().split("\n")
        # append at the END of the `paths:` list -- i.e. immediately before the next
        # top-level key. (Appending at EOF lands after `capability_roots:` and
        # silently makes the document mean something else; verified the hard way.)
        start = next(i for i, l in enumerate(lines) if l.startswith("paths:"))
        end = next((i for i in range(start + 1, len(lines))
                    if lines[i] and not lines[i][0].isspace() and not lines[i].startswith("-")),
                   len(lines))
        out = lines[:end] + appended_rule_yaml.rstrip("\n").split("\n") + lines[end:]
        c.write_text("\n".join(out))
        row["append_index"] = end
        p.commit_all("append a path rule by hand")

    # does the OS report the hand edit at all? (OC-P2-04 clause 2/4: an increase
    # must be refused AND reported)
    pol = p.run(["policy", "overrides"])
    row["policy_overrides_ok"] = pol.get("ok")
    txt = json.dumps(pol.get("result") or pol.get("error"))
    row["refused_mentions_rule"] = ("refused" in txt and target.split("/")[0] in txt)
    row["policy_overrides_refused"] = [
        x for x in (((pol.get("result") or {}).get("refused")) or [])
    ][:6]

    # what does the path map actually DECIDE for the target now?
    eff = p.run(["policy", "effective"])
    er = eff.get("result") or {}
    paths = None
    for k in ("REPOSITORY_CONTRACT", "repository_contract"):
        if isinstance(er.get(k), dict):
            paths = er[k].get("paths")
    if paths is None:
        paths = json.dumps(er)[:0] or None
    row["effective_has_appended_rule"] = (
        any(isinstance(r, dict) and r.get("pattern") == "product/*.yaml" for r in paths)
        if isinstance(paths, list) else None
    )
    row["effective_raw_head"] = json.dumps(er)[:400]

    t = p.ok(["task", "create", "--class", task_class or "security",
              "--objective", f"P2-AR-0077 {tag}", "--status", "READY"])["id"]
    p.ok(["task", "claim", t], session="S-w", role="backend-engineer")
    p.ok(["rebuild-memory", "--incremental"], session="S-w", role="backend-engineer")
    pk = p.ok(["context", "compile", t], session="S-w", role="backend-engineer")
    rc = pk["receipt_contract"]

    # THE UNDECLARED, OUT-OF-SCOPE WRITE
    p.write(target, "manufactured: true\n")

    rec = {"work_completed": f"P2-AR-0077 {tag}", "files_changed": list(report_declares),
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
    det = (e.get("error") or {}).get("details") or {}
    row["observed"] = det.get("observed") if det else (e.get("result") or {}).get("observed_files_changed")
    row["out_of_scope"] = det.get("out_of_scope")
    row["undeclared"] = det.get("undeclared")

    # THE STATE EFFECT: did the task actually reach DONE with the write unobserved?
    st = p.run(["task", "show", t])
    res = st.get("result") or {}
    row["task_status"] = res.get("task_status") or (res.get("task") or {}).get("task_status")
    row["ESCAPED"] = bool(e.get("ok"))
    print(f"{tag:34s} close_ok={row['close_ok']} err={row['close_error']} "
          f"status={row['task_status']} ESCAPED={row['ESCAPED']}")
    return row


def rule(pattern, cls, extra=""):
    return f"- pattern: {pattern}\n  class: {cls}\n  owner_role: backend-engineer\n{extra}"


rows = []

# --- control: no appended rule at all. The close MUST be refused. -----------
rows.append(attempt("C0-no-rule", None,
                    note="control: an undeclared production write is refused"))

# --- AR75-F2's own witness, verbatim from P2-AR-0075's prose ---------------
rows.append(attempt("W-derived", rule("product/*.yaml", "derived"),
                    note="AR75-F2 witness: class derived over the kernel's product/** source"))
rows.append(attempt("W-generated", rule("product/*.yaml", "generated"),
                    note="the other value contract_generated matches"))

# --- other class values that confer OTHER exemptions ----------------------
#     tasks::is_production_path exempts evidence|narrative|historical|runtime-data
#     as well as generated|derived; the repair's check names only two of the six.
for cls in ["evidence", "narrative", "historical", "runtime-data", "operational",
            "authoritative", "test"]:
    rows.append(attempt(f"X-{cls}", rule("product/*.yaml", cls),
                        note=f"does class {cls} confer any exemption the check ignores?"))

save("f2", rows)
print("\n=== CLOSES THAT SUCCEEDED (an undeclared production write went unobserved) ===")
for r in rows:
    if r["ESCAPED"]:
        print(f"  {r['case']}: eff_has_rule={r.get('effective_has_appended_rule')}")
