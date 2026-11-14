"""Probe the product guard on the R3 and fallback forms at the merge head (lead's own check of the baseline)."""
import os, sys, tempfile, pathlib
sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-42a/src")
from gov.guard.decide import decide  # noqa: E402

TICKET = """---
id: DAEO-03ub
status: in_progress
type: task
role: engineer
wbs_id: W2-42a
allowed_paths:
- src/**
---
# stand-in
"""
T, A = "tests/acceptance/X/zz.py", "src/ok.py"
forms = [
    "echo \"$v\" | sh", "echo 'touch {w}' | sh", "x=$(echo 'touch {w}'); $x", "L=(touch {w}); \"${L[@]}\"",
    "read -r a < x.py; $a", "cat x.py | while read -r f; do $f; done", "a=\"$v\"; $a", "f=$(cat x.py); $f",
    "read -r a < x.py; echo \"$a\" | sh", "mapfile -t L < x.py; \"${L[@]}\"", "printf '%s\\n' \"$v\" | bash",
    "x=$(read -r y <<< \"$v\"; echo $y); echo $x",
]
root = pathlib.Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR", "/tmp")))
(root / ".tickets").mkdir()
(root / ".tickets" / "DAEO-03ub.md").write_text(TICKET)
(root / "src").mkdir()
(root / "tests/acceptance/X").mkdir(parents=True)
(root / "x.py").write_text("x=1\n")
os.environ["HOME"] = str(root)
for k in [k for k in os.environ if k.startswith("GOV_")]: del os.environ[k]
os.chdir(root)
for f in forms:
    for w in (T, A):
        c = f.replace("{w}", w)
        try:
            r = decide("Bash", {"command": c}, os.path.realpath(str(root)), "engineer", "DAEO-03ub", cwd=os.path.realpath(str(root)), flag="open")
            d, why = r
        except Exception as e:  # noqa: BLE001
            d, why = "EXC", repr(e)
        print(f"{str(d):10} {c!r:70} {str(why)[:110]}")
        if "{w}" not in f:
            break
