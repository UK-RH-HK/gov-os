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
    'read -r a <<< "$v"', 'IFS=: read -r a b <<< "$line"', 'read -r a b <<< "$(git rev-parse HEAD HEAD)"',
    'while read -r f; do echo "$f"; done <<< "$(git status --porcelain)"', 'mapfile -t L <<< "$(ls)"',
    'readarray -t L <<< "$v"', "sed 's/a/b/' <<< \"$v\"", "awk '{print $1}' <<< \"$line\"", 'bc <<< "$x + 1"',
    'v=$(git log -1); read -r a <<< "$v"', 'grep x <<< "$v"', 'wc -l <<< "$(ls)"', 'cut -d: -f1 <<< "$v"',
    'tr a b <<< "$v"', 'sort <<< "$v"',
    'read -r a <<< "$v" > {w}', 'mapfile -t L <<< "$v"; touch {w}', 'while read -r f; do touch {w}; done <<< "$(ls)"',
    'while read -r f; do cp "$f" {w}; done <<< "$v"', "sed 's/a/b/' <<< \"$v\" > {w}", "awk '{print > \"{w}\"}' <<< \"$v\"",
    "awk '{system(\"touch {w}\")}' <<< \"$v\"", "sed 'w {w}' <<< \"$v\"", "sort -o {w} <<< \"$v\"",
    'bash <<< "$v"', 'sh <<< "$(cat x.py)"', 'xargs touch <<< "$v"', 'source /dev/stdin <<< "$v"', 'eval "$v"',
    'python3 <<< "$v"', 'perl <<< "$v"', "awk '{print}' <<< \"$(cat x)\" | sh",
    'while read -r f; do bash -c "$f"; done <<< "$v"', 'read -r a <<< "$(touch {w})"',
    'while read -r f; do echo "$f"; done <<< "$(touch {w})"', "sed 's/a/b/' <<< \"$(touch {w})\"",
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
