"""Build the resolved W1-35 support file from the merge-tree's conflicted blob (read-only; writes only its output file)."""
import py_compile
import re
import subprocess
import sys

REPO = "/home/usain/gov-os-worktrees/W2-11"
TREE = sys.argv[1]
OUT = sys.argv[2]
REL = "tests/acceptance/W1-35/w1_35_orchestration_support.py"

blob = subprocess.run(["git", "-C", REPO, "show", f"{TREE}:{REL}"], capture_output=True, text=True, check=True).stdout
pattern = re.compile(r"<<<<<<< w2/W2-11\n(.*?)=======\n(.*?)>>>>>>> w2/integrate\n", re.S)
hunks = pattern.findall(blob)
assert len(hunks) == 1, len(hunks)
ours, theirs = hunks[0]
print("OURS:\n" + ours + "THEIRS:\n" + theirs)

resolved = '''            # Rewrite-Reason: DEC-1061 with DEC-1040 (1), inventory row R3: the clause "a stated ceiling of tickets
            # in flight" enforced DEC-737/776/786, replaced by DEC-847 and then DEC-942 (no fixed number of leads;
            # capacity is the resource gate's, whose clauses below stay). The stated-ceiling clause is removed; the
            # row keeps its positive form (W2-11, DEC-847, DEC-866): the skill says there is no fixed number.
            ("no fixed number of tickets in flight",
             [r"no fixed|not (a )?fixed|no set", r"number|ceiling|cap|count", r"ticket|lead"]),
'''
text = pattern.sub(lambda m: resolved, blob)
assert "<<<<<<<" not in text and ">>>>>>>" not in text and "=======\n" not in text
open(OUT, "w", encoding="utf-8").write(text)
py_compile.compile(OUT, cfile=OUT + ".pyc", doraise=True)
print("ok", len(text.splitlines()), "lines")
