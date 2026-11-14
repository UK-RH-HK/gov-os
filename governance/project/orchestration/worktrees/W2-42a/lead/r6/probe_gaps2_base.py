"""Probe the product guard on the R3 and fallback forms at the merge head (lead's own check of the baseline)."""
import os, sys, tempfile, pathlib
sys.path.insert(0, "/tmp/w242a-lead/base/src")
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
    "while read -r f; do $f; done <<< 'touch {w}'", "while read -r a b; do $a $b; done <<< 'touch {w}'",
    "read -r a b <<< 'touch {w}'; $a $b", "read -r a b <<< \"$v\"; $a $b", "while read -r l; do ${l}; done <<< \"$v\"",
    "while read -r f; do env $f; done <<< \"$v\"", "while read -r f; do . \"$f\"; done <<< \"$v\"",
    "while read -r f; do xargs touch; done <<< \"$v\"", "mapfile -tC 'touch {w}' -c1 L <<< \"$v\"",
    "mapfile -C cb L <<< \"$v\"", "mapfile -t -C \"$cb\" L <<< \"$v\"", "mapfile -C 'touch {w}' L < x.py",
    "read -r a <<< \"$v\"; $a", "while read -r f; do \"$f\" x; done <<< \"$v\"",
    "while read -r f; do time $f; done <<< \"$v\"", "while read -r f; do command $f; done <<< \"$v\"",
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
