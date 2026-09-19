#!/usr/bin/env python3
"""P2-AR-0040 (repair-1 round 3, WS-9/11) — BUILDER REGRESSION EVIDENCE ONLY (Contract v3 O3), not acceptance.

A tiny Python project adopted A0 → A10 on an UNPROVISIONED simulated machine that has only the gov binary's embedded
payload (OWNER-DECISION-P2-0002 bootstrap), driven through the `gov` JSON CLI:

  CMD.1  A5: an approval that would bind a reviewer `command` test running an arbitrary program is refused
         TEST_COMMAND_NOT_PERMITTED and nothing runs (Contract v3 A3).
  CMD.2  the same approval without that test goes through.
  BOOT   A6 batch 0 installs the embedded payload as a BOOTSTRAP installation (posture UNPROVISIONED, authenticity UNKNOWN).
  SNAP   no batch of this plan moves anything; the snapshot store is `.governance-state/migration` (BC-P2-31).
  A7     accepted by the designated verifier.
  A10    the memory verifier's own queries (real files) — reported as observed (see the report, observation O-1).
  DOC    doctor's failing checks on this machine, D032's posture (the A11 posture reason reads exactly this check).

Environment: GOV_BIN (gov binary), SCRATCH (a fresh directory; the project, machine state and embedded-kernel cache
live under it). Prints `X <id> PASS|FAIL|OBS <statement> -- <detail>`.
"""
import json
import os
import sqlite3
import subprocess
import sys

import yaml

GOV = os.environ["GOV_BIN"]
S = os.environ["SCRATCH"]
PROJ = os.path.join(S, "proj")
EV = "spec/audits/GOVERNANCE-ADOPTION"
results = []


def gov(session, role, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
    env.update({"XDG_STATE_HOME": os.path.join(S, "state"), "GOV_CANONICAL_ROOT": "/nonexistent",
                "GOV_KERNEL_CACHE": os.path.join(S, "cache")})
    o = subprocess.run([GOV, "--json", "--root", PROJ, "--session", session, "--role", role, *args],
                       capture_output=True, text=True, env=env)
    try:
        return json.loads(o.stdout)
    except Exception:
        return {"ok": False, "error": {"code": "NO_JSON", "message": o.stderr[-500:]}}


def x(i, ok, stmt, detail, obs=False):
    tag = "OBS" if obs else ("PASS" if ok else "FAIL")
    results.append((i, tag))
    print(f"X {i} {tag} {stmt} -- {json.dumps(detail)[:700]}")


def write(rel, text):
    p = os.path.join(PROJ, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)


os.makedirs(os.path.join(S, "state"), exist_ok=True)
os.makedirs(os.path.join(S, "cache"), exist_ok=True)
write("app/core.py", "def total(xs):\n    return sum(xs)\n")
write("app/main.py", "from app.core import total\n\nif __name__ == \"__main__\":\n    print(total([1, 2, 3]))\n")
write("tests/test_core.py", "from app.core import total\n\n\ndef test_total():\n    assert total([1, 2]) == 3\n")
write("README.md", "# tiny\n\nA tiny project. See app/main.py.\n")
subprocess.run(["git", "init", "-q"], cwd=PROJ, check=True)
subprocess.run(["git", "add", "-A"], cwd=PROJ, check=True)
subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init"], cwd=PROJ, check=True)

for s in ["baseline", "inventory", "classify", "map", "plan", "test-design"]:
    r = gov("S-planner", "orchestrator", "adopt", s)
    assert r.get("ok"), (s, r.get("error"))
tf = os.path.join(PROJ, EV, "06-migration-tests.yaml")
t = yaml.safe_load(open(tf))
t["tests"].append({"id": "RT-001", "kind": "path_present", "path": "app/core.py", "description": "reviewer: product source kept"})
approved = json.loads(json.dumps(t))
t["tests"].append({"id": "RT-002", "kind": "command", "path": ".", "command": ["sh", "-c", "touch PWNED"], "description": "reviewer: arbitrary command"})
yaml.safe_dump(t, open(tf, "w"), sort_keys=False)
r = gov("S-reviewer", "migration-reviewer", "adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED")
e = r.get("error") or {}
x("CMD.1", e.get("code") == "TEST_COMMAND_NOT_PERMITTED" and not os.path.exists(os.path.join(PROJ, "PWNED")),
  "an approval binding a command test that runs an arbitrary program is refused, typed, and nothing runs",
  {"code": e.get("code"), "refused": (e.get("details") or {}).get("refused"), "pwned_exists": os.path.exists(os.path.join(PROJ, "PWNED"))})
yaml.safe_dump(approved, open(tf, "w"), sort_keys=False)
r = gov("S-reviewer", "migration-reviewer", "adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED")
x("CMD.2", r.get("ok") is True, "without it the approval goes through", {"ok": r.get("ok"), "error": r.get("error")})
r = gov("S-executor", "migration-executor", "adopt", "migrate", "--name", "tiny", "--alias", "tiny")
ra = (((r.get("result") or {}).get("batches") or [{}])[0].get("installed") or {}).get("release_authenticity") or {}
x("BOOT", r.get("ok") is True and ra.get("posture") == "UNPROVISIONED" and ra.get("authenticity") == "UNKNOWN",
  "A6 batch 0 installs the embedded payload as a bootstrap installation", {"posture": ra.get("posture"), "authenticity": ra.get("authenticity"), "error": r.get("error")})
x("SNAP", not os.path.exists(os.path.join(PROJ, ".governance-runtime", "migration")),
  "no batch snapshot is kept in the derived runtime directory", {"state_dir": sorted(os.listdir(os.path.join(PROJ, ".governance-state"))) if os.path.isdir(os.path.join(PROJ, ".governance-state")) else None})
r = gov("S-verifier", "migration-verifier", "adopt", "verify-migration")
x("A7", (r.get("result") or {}).get("verdict") == "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD", "A7 accepts", (r.get("result") or r.get("error")))
assert gov("S-executor", "migration-executor", "adopt", "extract-legacy").get("ok")
assert gov("S-builder", "memory-engineer", "adopt", "build-memory").get("ok")
hf = os.path.join(PROJ, "governance/tests/memory/heldout.yaml")
h = yaml.safe_load(open(hf))
db = sqlite3.connect(os.path.join(PROJ, ".governance-runtime/state.db"))
n = 0
for path in ["app/core.py", "app/main.py", "tests/test_core.py", "README.md", "governance/project/REPOSITORY_CONTRACT.yaml"]:
    row = db.execute("SELECT artifact_id FROM artifacts WHERE path=? AND record_type='file'", (path,)).fetchone()
    if row:
        n += 1
        h["queries"].append({"id": f"VQ-{n:03}", "category": "exact_path", "query": path, "expected_refs": [row[0]], "forbidden": [], "k": 8, "route": "path", "author": "independent memory verifier"})
db.close()
yaml.safe_dump(h, open(hf, "w"), sort_keys=False)
r = gov("S-memverifier", "memory-verifier", "adopt", "verify-memory")
res = r.get("result") or {}
x("A10", True, "A10 on the verifier's own queries (observed, see report O-1)",
  {"verdict": res.get("verdict"), "independent": res.get("independent_heldout"), "failed": [(f.get("id"), f.get("query"), f.get("category")) for f in (res.get("heldout") or {}).get("failed", [])]}, obs=True)
r = gov("S-x", "orchestrator", "doctor")
d = r.get("result") or (r.get("error") or {}).get("details") or {}
failed = [(c["id"], c["severity"]) for c in d.get("checks", []) if not c.get("ok")]
d032 = next((c for c in d.get("checks", []) if c.get("id") == "D032"), {})
x("DOC", True, "doctor on this machine (D032 is the check A11's posture reason reads)",
  {"verdict": d.get("verdict"), "failed": failed, "D032_posture": {k: (d032.get("posture") or {}).get(k) for k in ["machine_posture", "authenticity", "admission"]}}, obs=True)
fails = [i for i, tag in results if tag == "FAIL"]
print(f"SUMMARY total={len(results)} pass={sum(1 for _, t in results if t == 'PASS')} obs={sum(1 for _, t in results if t == 'OBS')} fail={len(fails)} failed={fails}")
sys.exit(1 if fails else 0)
