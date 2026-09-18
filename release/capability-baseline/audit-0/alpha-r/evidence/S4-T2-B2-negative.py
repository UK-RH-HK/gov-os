#!/usr/bin/env python3
"""Negative / adversarial checks for S4 (adopt), T1/T2 (role separation, fresh-session independence) and B2 (path map)
on small synthetic brownfield repositories.

[N1] one agent, one role, NO --session flags: do the independence gates (A5/A7/A10) still hold?
[N2] after the A5 approval, the executor edits the reviewed tests (deletes them) and the reviewed catalogue (adds an
     un-gated DELETE of live product source): what does A6 execute and what does A7 conclude?
[N3] verifier claims ACCEPTED while reality diverges from the map -> VERDICT_CONFLICT? (B2 bullet 5)
[N4] unknown material artefact blocks destructive batches (B2 bullet 3); SPLIT/MERGE actions (B2 bullet 2)
[N5] references / imports represented and rewritten on MOVE (B2 bullet 4); batch rollback (A6)
[N6] A0 detects interrupted prior governance work
[N7] verifier role strings are not validated (T1)
Run: PROBE_TMP=<scratch> python3 S4-T2-B2-negative.py
"""
import os, sys, json, shutil, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

MINI = {
    "README.md": "# mini\nSee the [login spec](docs/spec-login.md).\n",
    "src/pkg/__init__.py": "",
    "src/pkg/core.py": "from pkg.util import helper\n\ndef run():\n    return helper()\n",
    "src/pkg/util.py": "def helper():\n    return 7\n",
    "src/pkg/dead.py": "def unused():\n    return 0\n",
    "tests/test_core.py": "from pkg.core import run\n\ndef test_run():\n    assert run() == 7\n",
    "docs/spec-login.md": "# Login feature\nRequirement: users log in with email.\n",
    ".cursorrules": "Always use tabs. These rules are authoritative.\n",
}
def repo(sb, name, extra=None):
    files = dict(MINI); files.update(extra or {})
    return sb.new_repo(name, files)
def EV(p, f=""):
    return os.path.join(p, "spec/audits/GOVERNANCE-ADOPTION", f)
def show_(label, o, keys=None):
    if o["ok"]:
        r = o["result"]; print(f"[{label}] ok", json.dumps({k: r.get(k) for k in keys} if keys else r, ensure_ascii=False)[:600])
    else:
        print(f"[{label}] REFUSED {err(o)}: {str(o['error']['message'])[:200]}")

print("## [N1] single agent, single role, no --session flags anywhere")
sb = Sandbox("s4n")
p = repo(sb, "n1")
for st in [["baseline"], ["inventory"], ["classify"], ["map"], ["plan"], ["test-design"], ["review", "--verdict", "MIGRATION_PLAN_APPROVED"], ["migrate"],
           ["verify-migration"], ["extract-legacy"], ["build-memory"], ["verify-memory"], ["audit", "--accept-exceptions"]]:
    o = sb.gov("adopt", *st, cwd=p, quiet=True)
    print(f"[N1] adopt {' '.join(st):45s} ->", "ok" if o["ok"] else f"REFUSED {err(o)}: {str(o['error']['message'])[:120]}")
b = yaml.safe_load(open(EV(p, "00-BASELINE.yaml")))
print("[N1] recorded sessions: planner", b.get("planner_session"), "| reviewer", b["verdicts"].get("A5", {}).get("session"), "| executor", b.get("executor_session"),
      "| migration verifier", b["verdicts"].get("A7", {}).get("session"), "| memory builder", b.get("memory_builder_session"), "| memory verifier", b["verdicts"].get("A10", {}).get("session"))
print("[N1] stage status:", b["stage_status"], "| final verdict:", b.get("final_verdict"))

print("\n## [N2] post-approval edits to the reviewed tests and catalogue")
sb2 = Sandbox("s4n2")
p = repo(sb2, "n2")
for st in [["baseline"], ["inventory"], ["classify"], ["map"], ["plan"], ["test-design"]]:
    sb2.gov("adopt", *st, cwd=p, session="S-plan", quiet=True)
tf = EV(p, "06-migration-tests.yaml"); t0 = yaml.safe_load(open(tf))
print("[N2] reviewer approves a plan with", len(t0["tests"]), "tests")
show_("N2-review", sb2.gov("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-session", "S-review", cwd=p, session="S-review", quiet=True))
t0["tests"] = []; open(tf, "w").write(yaml.safe_dump(t0))
cat = [json.loads(l) for l in open(EV(p, "04-TARGET-PATH-MAP.jsonl"))]
for e in cat:
    if e["current_path"] == "src/pkg/util.py":
        e.update({"action": "DELETE_FROM_ACTIVE_TREE", "batch": 2, "requires_human_gate": False, "reason": "executor decided"})
open(EV(p, "04-TARGET-PATH-MAP.jsonl"), "w").write("".join(json.dumps(e) + "\n" for e in cat))
print("[N2] executor (after approval) emptied 06-migration-tests.yaml and changed src/pkg/util.py to DELETE_FROM_ACTIVE_TREE, batch 2, no gate")
o = sb2.gov("adopt", "migrate", cwd=p, session="S-exec", quiet=True); show_("N2-A6", o, ["complete"])
print("[N2] src/pkg/util.py still exists:", os.path.exists(os.path.join(p, "src/pkg/util.py")), "| core.py imports it:", "pkg.util" in open(os.path.join(p, "src/pkg/core.py")).read())
o = sb2.gov("adopt", "verify-migration", cwd=p, session="S-verify", quiet=True); show_("N2-A7", o, ["verdict", "catalogue_problems", "broken_links", "tests"])

print("\n## [N3] reality diverges from the map; the verifier claims ACCEPTED")
sb3 = Sandbox("s4n3")
p = repo(sb3, "n3")
for st in [["baseline"], ["inventory"], ["classify"], ["map"], ["plan"], ["test-design"]]:
    sb3.gov("adopt", *st, cwd=p, session="S-plan", quiet=True)
sb3.gov("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-session", "S-review", cwd=p, session="S-review", quiet=True)
o = sb3.gov("adopt", "migrate", cwd=p, session="S-exec", quiet=True); show_("N3-A6", o, ["complete"])
cat = [json.loads(l) for l in open(EV(p, "04-TARGET-PATH-MAP.jsonl"))]
moved = [(e["current_path"], e["target_path"]) for e in cat if e["action"] in ("MOVE", "RENAME")]
print("[N3] moves in the map:", moved)
if moved:
    src, dst = moved[0]
    os.makedirs(os.path.dirname(os.path.join(p, src)) or p, exist_ok=True); shutil.move(os.path.join(p, dst), os.path.join(p, src))
    print(f"[N3] reality tampered: {dst} moved back to {src}")
show_("N3-claim", sb3.gov("adopt", "verify-migration", "--verdict", "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD", cwd=p, session="S-verify", quiet=True))
o = sb3.gov("adopt", "verify-migration", cwd=p, session="S-verify", quiet=True); show_("N3-computed", o, ["verdict", "catalogue_problems", "tests"])
show_("N3-next-stage", sb3.gov("adopt", "extract-legacy", cwd=p, session="S-mem", quiet=True))
au = sb3.gov("audit", "--no-persist", "--family", "path_map_compliance", cwd=p, quiet=True)
r_ = au.get("result") or (au.get("error") or {}).get("details") or {}
print("[N3] audit family path_map_compliance:", r_.get("verdict"), json.dumps(r_.get("families", {}).get("path_map_compliance", r_.get("findings")))[:300])

print("\n## [N4] unknown material artefacts block destructive batches; SPLIT / MERGE")
sb4 = Sandbox("s4n4")
p = repo(sb4, "n4", {"legacy-index/vectors.json": '{"vectors": [[0.1, 0.2]], "paths": ["gone.md"]}\n'})
os.makedirs(os.path.join(p, "misc"), exist_ok=True)
open(os.path.join(p, "misc/blob.xq9"), "wb").write(bytes([0, 1, 2, 3, 255, 254]) + b" opaque vendor blob\n")
open(os.path.join(p, "misc/opaque.zzz"), "w").write("k7 q2 v9\nzz aa\n")   # text artefact of no recognisable kind
sb4.git(p, "add", "-A"); sb4.git(p, "commit", "-q", "-m", "blob")
for st in [["baseline"], ["inventory"], ["classify"], ["map"], ["plan"], ["test-design"]]:
    o = sb4.gov("adopt", *st, cwd=p, session="S-plan", quiet=True)
    if st[0] in ("classify", "map"):
        show_("N4-" + st[0], o, ["unknown", "by_class", "actions", "unknown_blocking_destructive"])
cat = [json.loads(l) for l in open(EV(p, "04-TARGET-PATH-MAP.jsonl"))]
print("[N4] UNKNOWN entries:", [(e["current_path"], e["finding_state"], e["action"]) for e in cat if e.get("finding_state") == "UNKNOWN" or e.get("current_class") == "UNKNOWN"])
print("[N4] destructive entries:", [(e["current_path"], e["action"], e["batch"]) for e in cat if e["action"] in ("DELETE_FROM_ACTIVE_TREE", "RETIRE")])
sb4.gov("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-session", "S-review", cwd=p, session="S-review", quiet=True)
for bn in range(0, 8):
    o = sb4.gov("adopt", "migrate", "--batch", str(bn), cwd=p, session="S-exec", quiet=True)
    print(f"[N4] migrate batch {bn} ->", "ok" if o["ok"] else f"REFUSED {err(o)}: {str(o['error']['message'])[:120]}")
for act in ("SPLIT", "MERGE"):
    cat = [json.loads(l) for l in open(EV(p, "04-TARGET-PATH-MAP.jsonl"))]
    for e in cat:
        if e["current_path"] == "README.md":
            e.update({"action": act, "batch": 5, "target_path": "docs/README-part.md", "requires_human_gate": False})
    open(EV(p, "04-TARGET-PATH-MAP.jsonl"), "w").write("".join(json.dumps(e) + "\n" for e in cat))
    o = sb4.gov("adopt", "migrate", "--batch", "5", cwd=p, session="S-exec", quiet=True)
    print(f"[N4] catalogue entry README.md -> {act}: migrate batch 5 ->", "ok " + json.dumps(o["result"])[:200] if o["ok"] else f"REFUSED {err(o)}: {str(o['error']['message'])[:140]}")

print("\n## [N5] references / imports are represented and rewritten on MOVE; batch rollback")
sb5 = Sandbox("s4n5")
p = repo(sb5, "n5")
for st in [["baseline"], ["inventory"], ["classify"], ["map"], ["plan"], ["test-design"]]:
    sb5.gov("adopt", *st, cwd=p, session="S-plan", quiet=True)
cat = [json.loads(l) for l in open(EV(p, "04-TARGET-PATH-MAP.jsonl"))]
for e in cat:
    if e["current_path"] in ("docs/spec-login.md", "src/pkg/util.py", "src/pkg/core.py", "README.md"):
        print(f"[N5] map {e['current_path']:22s} action={e['action']:14s} target={e['target_path']} references={e['references']} imports={e['imports']} consumers={e['consumers']}")
sb5.gov("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-session", "S-review", cwd=p, session="S-review", quiet=True)
readme0 = open(os.path.join(p, "README.md")).read()
o = sb5.gov("adopt", "migrate", "--batch", "0", cwd=p, session="S-exec", quiet=True)
o = sb5.gov("adopt", "migrate", "--batch", "1", cwd=p, session="S-exec", quiet=True); show_("N5-batch1", o, ["complete"])
o = sb5.gov("adopt", "migrate", "--batch", "2", cwd=p, session="S-exec", quiet=True); show_("N5-batch2", o)
led = [json.loads(l) for l in open(EV(p, "migration-ledger.jsonl"))]
print("[N5] ledger entries for batch 2:", [(l.get("artifact_id"), l.get("status"), l.get("references_updated") or l.get("refs")) for l in led if l.get("batch") == 2])
print("[N5] README link before:", readme0.strip().splitlines()[-1], "| after:", open(os.path.join(p, "README.md")).read().strip().splitlines()[-1])
o = sb5.gov("adopt", "rollback", "--batch", "2", cwd=p, session="S-exec", quiet=True); show_("N5-rollback", o)
print("[N5] after rollback: docs/spec-login.md exists =", os.path.exists(os.path.join(p, "docs/spec-login.md")), "| README restored =", open(os.path.join(p, "README.md")).read() == readme0)

print("\n## [N6] A0 detects interrupted prior governance work")
sb6 = Sandbox("s4n6")
p = repo(sb6, "n6")
os.makedirs(os.path.join(p, "governance/kernel"), exist_ok=True); open(os.path.join(p, "governance/kernel/partial.yaml"), "w").write("x: 1\n")
o = sb6.gov("adopt", "baseline", cwd=p, session="S-plan", quiet=True); show_("N6-A0", o, ["interrupted", "freeze_advice"])
b = yaml.safe_load(open(EV(p, "00-BASELINE.yaml"))); print("[N6] interrupted_work =", json.dumps(b["interrupted_work"]))
b["stage_status"]["A2"] = "in_progress"; open(EV(p, "00-BASELINE.yaml"), "w").write(yaml.safe_dump(b))
o = sb6.gov("adopt", "baseline", cwd=p, session="S-plan", quiet=True); show_("N6-A0-rerun", o, ["interrupted", "freeze_advice"])
print("[N6] does A0 refuse / freeze on interrupted work, or only advise?", "only advises" if o["ok"] else "refuses")

print("\n## [N7] verifier role strings")
sb7 = Sandbox("s4n7")
p = repo(sb7, "n7")
for st in [["baseline"], ["inventory"], ["classify"], ["map"], ["plan"], ["test-design"]]:
    sb7.gov("adopt", *st, cwd=p, session="S-plan", quiet=True)
sb7.gov("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-session", "S-r", "--reviewer-role", "migration-executor", cwd=p, quiet=True)
sb7.gov("adopt", "migrate", cwd=p, session="S-exec", quiet=True)
o = sb7.gov("adopt", "verify-migration", "--verifier-role", "migration-executor", cwd=p, session="S-v", quiet=True); show_("N7-A7-role-migration-executor", o, ["verdict"])
o = sb7.gov("adopt", "verify-migration", "--verifier-role", "backend-engineer", cwd=p, session="S-v2", role="backend-engineer", quiet=True); show_("N7-A7-acting-role-L1", o, ["verdict"])
b = yaml.safe_load(open(EV(p, "00-BASELINE.yaml"))); print("[N7] recorded verdicts:", {k: (v.get("verdict"), v.get("role"), v.get("session")) for k, v in b["verdicts"].items()})
print("\nDONE")
