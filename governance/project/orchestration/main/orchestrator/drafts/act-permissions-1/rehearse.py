#!/usr/bin/env python3
"""ACT-PERMISSIONS-1's rehearsal (DEC-1057): the operator's steps exactly, on a copy of the real settings file in a
scratch folder (only the path substituted); the real file is hashed before and after and must not change.

    python3 rehearse.py <scratch folder>
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REAL = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.claude/settings.local.json")
APPLY = Path("/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-PERMISSIONS-1/apply.py")
scratch = Path(sys.argv[1])
scratch.mkdir(parents=True, exist_ok=True)
copy = scratch / "settings.local.json"
shutil.copy2(REAL, copy)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
real_before, copy_before = sha(REAL), sha(copy)
fails = 0


def step(name, args, want_rc):
    global fails
    r = subprocess.run([sys.executable, "-I", str(APPLY), str(copy), *args], capture_output=True, text=True)
    ok = r.returncode == want_rc
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}: rc {r.returncode} (want {want_rc}); {r.stdout.strip() or r.stderr.strip()}")
    return r


old = json.loads(copy.read_text())["permissions"]
step("1. check before (rules missing)", ["--check"], 1)
step("2. apply", [], 0)
step("3. check after (all present)", ["--check"], 0)
step("4. apply again (nothing added)", [], 0)
new = json.loads(copy.read_text())["permissions"]
checks = [
    ("deny unchanged", new.get("deny") == old.get("deny")),
    ("ask unchanged", new.get("ask", []) == old.get("ask", [])),
    ("every old allow rule kept, in order", new["allow"][: len(old["allow"])] == old["allow"]),
    ("only the ACT's rules added", len(new["allow"]) - len(old["allow"]) == 18),
    ("git push still denied", "Bash(git push *)" in new.get("deny", [])),
    ("no git -C rule at all (DEC-1081 (1))", not any(r.startswith("Bash(git -C") for r in new["allow"])),
    ("no new git rule of any kind", [r for r in new["allow"] if r.startswith("Bash(git")] == [r for r in old["allow"] if r.startswith("Bash(git")]),
    ("no rm, mv, cp, mkdir, curl, setsid or timeout allowed", not any(r.startswith(f"Bash({c}") for r in new["allow"] for c in ("rm", "mv", "cp", "mkdir", "curl", "setsid", "timeout"))),
    ("the other keys unchanged", {k: v for k, v in json.loads(copy.read_text()).items() if k != "permissions"} == {k: v for k, v in json.loads(REAL.read_text()).items() if k != "permissions"}),
]
for name, ok in checks:
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}")
step("5. undo", ["--undo"], 0)
ok = sha(copy) == copy_before
fails += not ok
print(f"{'ok  ' if ok else 'FAIL'} 6. after undo the copy equals the original byte for byte")
ok = sha(REAL) == real_before
fails += not ok
print(f"{'ok  ' if ok else 'FAIL'} 7. the real settings file unchanged throughout (sha256 {real_before[:12]})")
print("REHEARSAL PASS" if not fails else f"REHEARSAL FAILED {fails}")
sys.exit(1 if fails else 0)
