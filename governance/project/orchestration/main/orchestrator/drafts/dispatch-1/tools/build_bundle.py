"""Builds acts/ACT-DISPATCH-1 (the bundle) from the clone's changed files, in the operator's form (as
acts/ACT-IDLE-GUARD-1 has it).
   python3 build_bundle.py freeze [guard2]      after/ copies from the clone, list.txt, apply.sh (the frozen before/ copies were
                                       taken from the clone before the change)
   python3 build_bundle.py manifest    manifest.json with the checks and the rehearsal log's sha256 (run after rehearse.sh)
The checks are run as `bash -c` from the repository root: each a here-document of one tools/check_*.py, no pytest."""
import hashlib
import json
import os
import shutil
import sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WHICH = sys.argv[2] if len(sys.argv) > 2 else "dispatch"
ACT = {"dispatch": "ACT-DISPATCH-1", "guard2": "ACT-IDLE-GUARD-2"}[WHICH]
B = os.path.join(D, "acts", ACT)
CL = os.environ.get("DT_CLONE", "/home/usain/gov-os-runs/W2-00/dispatch-1/clone")
FILES = {"dispatch": [
    "governance/project/orchestration/tools/dispatch/dispatcher.py",
    "governance/project/orchestration/tools/dispatch/balancer.py",
    "tests/unit/orchestration/test_dispatcher.py",
    "tests/unit/orchestration/test_balancer.py",
], "guard2": [
    "governance/project/orchestration/tools/stop_idle_check.py",
    "tests/unit/orchestration/test_stop_idle_check.py",
]}[WHICH]
RLOG = "rehearsal.log" if WHICH == "dispatch" else "rehearsal-guard2.log"
APPLY_SRC = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/acts/ACT-IDLE-GUARD-1/apply.sh"


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


HEAD1 = '''#!/bin/bash
# ACT-DISPATCH-1's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256), relative
# to the repository it is run in (its cwd); the bundle is read from the script's own folder. Four files: the dispatcher
# (governance/project/orchestration/tools/dispatch/dispatcher.py), the Load Balancer's arithmetic (.../dispatch/balancer.py)
# and the two unit-test files that carry this ACT's cases (tests/unit/orchestration/test_dispatcher.py, test_balancer.py).
# The state of each file is decided by its sha256 alone:
#   before   hashes as list.txt's before          applied  hashes as its after
#   other    anything else (changed since the freeze, missing, a link): refused, NOTHING is touched (every file is
#            read first; no file is written unless every file is as the step expects)
#   check    read-only: every file is the before; exit 0, else exit 3 "moved: <path>"
#   apply    every file is the before (or the after: left as it is); the frozen after copy of each file that is still
#            the before is written to a temp file made by mktemp beside it, the mode kept, then moved into place whole
#   undo     every file is the after (or the before: left as it is); the frozen before copy put back the same way
#   verify   every file is the after; exit 0, else exit 3 "not applied: <path>"
# Each frozen copy is hashed against list.txt before it is used (exit 4 when it does not hash as listed). Nothing but the
# listed files is touched (a temp file is renamed over its file, so none is left). The running dispatcher tick reads its
# files whole at its start: no restart is needed.
'''
HEAD2 = HEAD1.replace('ACT-DISPATCH-1', 'ACT-IDLE-GUARD-2').replace(
    '''Four files: the dispatcher
# (governance/project/orchestration/tools/dispatch/dispatcher.py), the Load Balancer's arithmetic (.../dispatch/balancer.py)
# and the two unit-test files that carry this ACT's cases (tests/unit/orchestration/test_dispatcher.py, test_balancer.py).''',
    '''Two files: the CTO's Stop hook
# (governance/project/orchestration/tools/stop_idle_check.py) and the unit-test file that carries this ACT's cases and the
# ACT-IDLE-GUARD-1 companion cases (tests/unit/orchestration/test_stop_idle_check.py).''').replace(
    'The running dispatcher tick reads its\n# files whole at its start','Each running Stop hook reads its\n# file whole at its start')


def freeze():
    rows = []
    for rel in FILES:
        dst = os.path.join(B, "after/repo", rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(CL, rel), dst)
        shutil.copymode(os.path.join(CL, rel), dst)
        rows.append(f"repo|{rel}|{sha(os.path.join(B, 'before/repo', rel))}|{sha(dst)}")
    with open(os.path.join(B, "list.txt"), "w") as f:
        f.write("\n".join(rows) + "\n")
    text = open(APPLY_SRC).read()
    head, rest = text.split("set -u\n", 1)
    new_head = (HEAD1 if WHICH == "dispatch" else HEAD2)
    with open(os.path.join(B, "apply.sh"), "w") as f:
        f.write(new_head + "set -u\n" + rest)
    os.chmod(os.path.join(B, "apply.sh"), 0o755)
    print("frozen:", len(rows), "files; list.txt and apply.sh written")


def checks():
    rows = [r.split("|") for r in open(os.path.join(B, "list.txt")).read().split("\n") if r]

    def here(name):
        body = open(os.path.join(D, "tools", name)).read()
        assert "PYEOF" not in body
        return "python3 -I - <<'PYEOF'\n" + body + "PYEOF"
    parse = ("python3 -I -B -c 'import ast,sys; [ast.parse(open(p).read(), p) for p in sys.argv[1:]]' "
             + " ".join(r[1] for r in rows))
    tracked = {"cmd": "git ls-files --error-unmatch " + " ".join(r[1] for r in rows), "exit": 0, "count": None}
    if WHICH == "dispatch":
        cs = [{"cmd": parse, "exit": 0, "count": None}, {"cmd": here("check_cap.py"), "exit": 0, "count": 4},
              {"cmd": here("check_idle.py"), "exit": 0, "count": 5}, {"cmd": here("check_forecast.py"), "exit": 0, "count": 4},
              tracked]
        dec = "DEC-1140, DEC-1052, DEC-1118, DEC-1133, DEC-1110"
    else:
        cs = [{"cmd": parse, "exit": 0, "count": None}, {"cmd": here("check_hook.py"), "exit": 0, "count": 4}, tracked]
        dec = "DEC-1140, DEC-1110, DEC-1109, DEC-936"
    with open(os.path.join(D, "tools", f"checks-{WHICH}.json"), "w") as f:
        json.dump({"dec": dec, "checks": cs}, f, indent=1)
        f.write("\n")
    print(len(cs), "checks written")


def manifest():
    rows = [r.split("|") for r in open(os.path.join(B, "list.txt")).read().split("\n") if r]
    files = {}
    for _, rel, bef, aft in rows:
        assert sha(os.path.join(B, "before/repo", rel)) == bef and sha(os.path.join(B, "after/repo", rel)) == aft
        files[f"before/repo/{rel}"], files[f"after/repo/{rel}"] = bef, aft
    shutil.copyfile(os.path.join(D, RLOG), os.path.join(B, "rehearsal.log"))
    for n in ("apply.sh", "list.txt", "rehearsal.log"):
        files[n] = sha(os.path.join(B, n))

    checks = json.load(open(os.path.join(D, "tools", f"checks-{WHICH}.json")))["checks"]
    dec = json.load(open(os.path.join(D, "tools", f"checks-{WHICH}.json")))["dec"]
    m = {"act": ACT, "dec": dec, "author": "cto", "claimed_class": "O",
         "touched": [{"root": r[0], "path": r[1], "before": r[2], "after": r[3]} for r in rows],
         "files": files, "checks": checks, "commands": [],
         "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]}}
    with open(os.path.join(B, "manifest.json"), "w") as f:
        json.dump(m, f, indent=1)
        f.write("\n")
    print("manifest.json written;", len(files), "files hashed; sha256", sha(os.path.join(B, "manifest.json")))


{"freeze": freeze, "checks": checks, "manifest": manifest}[sys.argv[1]]()
