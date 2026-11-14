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
    "while read -r f; do touch \"$f\"; done <<< \"{w}\"", "read -r f <<< {w}; touch \"$f\"", "while read -r f; do $f; done <<< 'touch {w}'",
    "sed 's/a/b/w {w}' <<< \"$v\"", "sed 'W {w}' <<< \"$v\"", "sed 'e touch {w}' <<< \"$v\"", "sed 's/.*/touch {w}/e' <<< \"$v\"",
    "sed --in-place 's/a/b/' {w} <<< \"$v\"", "sed -e 'w {w}' <<< \"$v\"", "sed -n -e p -e 'w {w}' <<< \"$v\"",
    "sed -f x.sed <<< \"$v\"", "awk -f x.awk <<< \"$v\"", "awk '{system (\"touch {w}\")}' <<< \"$v\"",
    "awk '{print | \"sh\"}' <<< \"$v\"", "awk 'BEGIN{while((\"cat\"|getline l)>0) print l}' <<< \"$v\"",
    "sort --output={w} <<< \"$v\"", "sort -o{w} <<< \"$v\"",
    "mapfile -C 'touch {w}' -c 1 L <<< \"$v\"", "readarray -C 'touch {w}' -c1 L <<< \"$v\"",
    "read -r a <<< \"$v\"; eval \"$a\"", "while read -r f; do echo \"$f\"; done <<< \"$v\" | sh",
    "cut -d: -f1 <<< \"$v\" | bash", "sed 's/a/b/' <<< \"$v\" | sh", "while read -r f; do ssh h; done <<< \"$v\"",
    "while read -r f; do docker exec -i c sh; done <<< \"$v\"", "while read -r f; do sh; done <<< \"$v\"",
    "while read -r f; do cat > {w}; done <<< \"$v\"", "read -r a <<< \"$v\" && sh <<< \"$a\"",
    "bc <<< \"$x\" > {w}", "awk -v x=1 '{print}' <<< \"$v\"", "gawk '{print}' <<< \"$v\"",
    "read -r a <<< `touch {w}`", "IFS=: read -r a b <<< \"$(sh -c 'touch {w}')\"",
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
