#!/usr/bin/env python3
"""T1 — role separation for the nine adoption/audit roles of the Adoption protocol v3.0 §3, as the OS recognises and
enforces them. For each protocol role: the kernel role id (if any), its authority level as enforced by `gov`, and what
the adoption stage that role performs checks about the actor. Also: A11 (comprehensive independent auditor) run from
the executor's own session.
Run: PROBE_TMP=<scratch> python3 T1-roles.py
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

sb = Sandbox("t1")
p = sb.new_repo("t1", {"README.md": "# t1\n", "src/a.py": "def f():\n    return 1\n"})
sb.gov("init", "--name", "t1", "--alias", "t1a", "--skip-index", cwd=p, quiet=True)
proto = [("Conditional recovery agent", ["recovery-agent", "recovery"]), ("Role A adoption auditor/planner", ["adoption-planner", "adoption-auditor", "planner"]),
         ("Role B independent migration reviewer/test author", ["migration-reviewer"]), ("Role C migration executor", ["migration-executor"]),
         ("Role D independent migration verifier", ["migration-verifier"]), ("Role E memory engineer", ["memory-engineer"]),
         ("Role F independent memory verifier/test author", ["memory-verifier"]), ("Role G comprehensive independent auditor", ["independent-auditor"]), ("Role H operator/CTO", ["orchestrator"])]
print("## [T1a] protocol roles recognised by the OS (probe: `gov --role <id> task create`; UNKNOWN_ROLE = not a kernel role)")
for label, ids in proto:
    res = []
    for rid in ids:
        o = sb.gov("task", "create", "--objective", f"probe {rid}", role=rid, cwd=p, quiet=True)
        res.append((rid, "ok (>=L2)" if o["ok"] else err(o) + (" " + o["error"]["message"].split("(")[1].split(")")[0] if err(o) == "AUTHORITY_DENIED" else "")))
    print(f"[T1a] {label:52s} ->", res)
print("\n## [T1b] `gov recover` (the recovery role's operation): who may run it")
for rid in ["migration-executor", "change-controller", "backend-engineer", "independent-auditor"]:
    o = sb.gov("recover", "--dry-run", role=rid, cwd=p, quiet=True); o2 = sb.gov("recover", role=rid, cwd=p, quiet=True)
    print(f"[T1b] recover as {rid:22s} dry-run ->", "ok" if o["ok"] else err(o), "| real ->", "ok" if o2["ok"] else err(o2))
print("\n## [T1c] what each adoption stage checks about its actor (session / role), executed")
q = sb.new_repo("t1q", {"README.md": "# q\n", "src/a.py": "def f():\n    return 1\n"})
def A(label, *args, s=None, role=None):
    o = sb.gov("adopt", *args, cwd=q, session=s, role=role, quiet=True)
    print(f"[T1c] {label:64s} ->", "ok" if o["ok"] else f"REFUSED {err(o)}: {str(o['error']['message'])[:100]}")
    return o
for st in ["baseline", "inventory", "classify", "map", "plan", "test-design"]:
    A(f"planner stage {st} as role memory-verifier (L0), session S-exec", st, s="S-exec", role="memory-verifier")
A("A5 review by reviewer-session S-rev, reviewer-role orchestrator", "review", "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-session", "S-rev", "--reviewer-role", "orchestrator", s="S-rev")
A("A6 migrate as session S-exec", "migrate", s="S-exec")
A("A7 verify as session S-ver, verifier-role orchestrator", "verify-migration", "--verifier-role", "orchestrator", s="S-ver")
A("A8 extract-legacy as session S-exec (the executor)", "extract-legacy", s="S-exec")
A("A9 build-memory as session S-exec (the executor)", "build-memory", s="S-exec")
A("A10 verify-memory as session S-ver (the migration verifier), role orchestrator", "verify-memory", "--verifier-role", "orchestrator", s="S-ver")
A("A11 comprehensive audit as session S-exec (the executor itself)", "audit", "--accept-exceptions", s="S-exec")
b = yaml.safe_load(open(os.path.join(q, "spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml")))
print("[T1c] recorded: planner", b.get("planner_session"), "| executor", b.get("executor_session"), "| memory builder", b.get("memory_builder_session"),
      "| verdicts", {k: (v.get("verdict"), v.get("session"), v.get("role")) for k, v in b["verdicts"].items()})
print("[T1c] note: planner session == executor session == memory builder session == A11 auditor session = S-exec; accepted at every stage")
print("\nDONE")
