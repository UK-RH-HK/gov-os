#!/usr/bin/env python3
"""P2-AR-0038 (WS-7 round 3) — evidence for integration point IP-W7R3-1 (not a repair check).

A tooling task registers a plugin while it is claimed, declaring and allowing the plugin's own files (its script and
the descriptor `gov plugins register` writes) but not the registry file itself, and is then closed. On the base the
registry lives under `governance/generated/`, which task close treats as an OS-managed location (a sealed registry is
the OS's own write). After the BC-P2-31 move it lives at `governance/registry/plugin-registry.json`, which
`orchestration::tasks::OS_MANAGED_PREFIXES` (WS-5's file) does not list yet, so close sees it as an undeclared worker
mutation. Usage: GOV_BIN=<gov> WS07R3_SCRATCH=<dir> python3 ip_task_close_registration.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ws07_r3_named_checks as nc  # noqa: E402


def receipt(p, role, session, task, files, extra=None):
    pk = p.ok(role, "context", "compile", task, session=session)
    rc = pk.get("receipt_contract") or {}
    tr = rc.get("trace") or {}
    r = {"work_completed": "registered a plugin", "files_changed": files,
         "tests": {"status": "not_applicable_with_reason", "reason": "tooling"}, "outcome": "success", "evidence": [],
         "context_packet_hash": pk.get("packet_hash"),
         "inputs_consumed": [f"{e.get('id')}@{e.get('content_hash')}" for e in rc.get("acknowledge_inputs") or []],
         "outputs_produced": files, "requirements_implemented": tr.get("requirements"),
         "scenarios_implemented": tr.get("scenarios"), "features_implemented": tr.get("features"),
         "decisions_applied": tr.get("decisions"), "constraints_applied": tr.get("constraints"),
         "acceptance_evidence": [{"test": t, "result": "passed", "evidence": "n/a"} for t in rc.get("tests_requiring_evidence") or []],
         "deviations": [], "unresolved": []}
    r.update(extra or {})
    f = os.path.join(p.base, f"receipt-{task}.json")
    json.dump(r, open(f, "w"))
    return f


def main():
    print(f"# gov {nc.GOV}")
    p = nc.new_project("ip-close")
    p.ok("orchestrator", "rebuild-memory")
    te, s = "tooling-engineer", "S-tool"
    t = p.ok("orchestrator", "task", "create", "--class", "tooling", "--objective", "register the p1 plugin", "--status",
             "READY", "--allowed", "tools/**,governance/project/plugins/**")["id"]
    p.ok(te, "task", "claim", t, session=s)
    marker = os.path.join(p.base, "marker.txt")
    nc.marker_plugin(p, "tools/p.sh", marker)
    rel = nc.descriptor(p, "p1", "tools/p.sh")
    r = nc.register_approved(p, te, rel)
    print("registered:", (r.get("result") or {}).get("registered"), (r.get("result") or {}).get("registry"))
    changed = p.git("status", "--porcelain").stdout
    print("# working-tree changes during the task:\n" + changed)
    p.ok(te, "rebuild-memory", "--incremental", session=s)
    f = receipt(p, te, s, t, ["tools/p.sh", rel])
    v = p.run(te, "task", "close", t, "--report", f, session=s)
    err = v.get("error") or {}
    print("close ok:", v.get("ok"), "code:", err.get("code"))
    d = err.get("details") or {}
    print("undeclared:", json.dumps(d.get("undeclared")), "out_of_scope:", json.dumps(d.get("out_of_scope")),
          "t2_violations:", json.dumps(d.get("t2_violations"))[:300])
    if not v.get("ok"):
        print("message:", (err.get("message") or "")[:500])


if __name__ == "__main__":
    main()
