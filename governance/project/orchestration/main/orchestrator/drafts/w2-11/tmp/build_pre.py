"""Build the designer's pre-merge file: w2/W2-11's W1-35 support file with W2-11's one edit in the row "parallel tickets"
moved out of the lines integrate also changed, so git's own merge of it with w2/integrate has no conflict and gives both
sides' edits. Read-only (writes its output file only)."""
import py_compile
import subprocess
import sys

REPO = "/home/usain/gov-os-worktrees/W2-11"
OUT = sys.argv[1]
REL = "tests/acceptance/W1-35/w1_35_orchestration_support.py"
mine = subprocess.run(["git", "-C", REPO, "show", f"w2/W2-11:{REL}"], capture_output=True, text=True, check=True).stdout

new_hunk = '''            # DEC-847 replaced the stated ceiling (DEC-737, DEC-776, DEC-786) with no fixed number.
            ("no fixed number of tickets in flight",
             [r"no fixed|not (a )?fixed|no set", r"number|ceiling|cap|count", r"ticket|lead"]),
'''
base_hunk = '''            ("a stated ceiling of tickets in flight",
             [r"ceiling|at most|up to|no more than|maximum|limit", r"ticket",
              r"in flight|at a time|at once|parallel|concurrent|running"]),
'''
gate = '''            ("the resource gate before each start",
             [r"resource gate", r"before (each|every|any|a)\\b|(each|every) start"]),
'''
assert mine.count(new_hunk) == 1 and mine.count(gate) == 1 and base_hunk not in mine
text = mine.replace(new_hunk, base_hunk)
text = text.replace(gate, gate + '''            # W2-11 (DEC-847, DEC-866): DEC-847 replaced the stated ceiling (DEC-737, DEC-776, DEC-786) with no fixed
            # number; the skill says so, and this clause pins it.
            ("no fixed number of tickets in flight",
             [r"no fixed|not (a )?fixed|no set", r"number|ceiling|cap|count", r"ticket|lead"]),
''')
open(OUT, "w", encoding="utf-8").write(text)
py_compile.compile(OUT, cfile=OUT + ".pyc", doraise=True)
print("ok")
