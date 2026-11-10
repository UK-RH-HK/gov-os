#!/usr/bin/env python3
"""ACT-W2-149-INSTALL-1's builder: APPROVED.before (ACT-INDEP-WALLS-1's list, rebuilt from its apply.sh's text and its
recorded sha256, never read from the sets root), APPROVED.after (the same bytes, then the new lines), and the hashes
written into apply.sh. Run from the main tree after the F11 merge:  python3 freeze.py <main tree> <F11 merge commit>
"""
import hashlib
import os
import re
import subprocess
import sys

TREE, MERGE = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = "governance/project/orchestration/tools/indep_launch.py"
BRIEFS = "governance/project/indep-briefs/sgx1"
TEMPLATE = {"README.md": "65298d3468484515ca18e2dd3db5e6eb867221f1d9d6318e5e07998a2a5aef49",
            "settings.json.tmpl": "9b85b9a604d00e5c5aadffedbbb3ff93e51cebe641c73c11dc248374278a609b",
            "wall_hook.py": "95638d7d9edb5eb67035248e928652a737e783f39b5860bac93b4958073343d3",
            "CLAUDE.md.tmpl": "aee245ce7a8034565d9c304820ece8091946b1d9898d34c20a3fb38f93bd9267",
            "kinds.yaml": "8b50a78f01b316d0bd5d41689cd3730da0e3142ac4c54705dc83bad0ace4d74f",
            "tree-exclude.txt": "21660e1ee5adf793e46d59e601cef662ef8a445399da185bd9397bc6067d47a6"}
ORDER = "README.md settings.json.tmpl wall_hook.py CLAUDE.md.tmpl kinds.yaml tree-exclude.txt".split()
LIST_BEFORE = "331e48fa336ef58ba5dc6fd4afcf9c1387ec4bd29e583eb955280a267626bbc9"   # ACT-INDEP-WALLS-1's backup record
BRIEF_LINES = [("labeller", "labeller.md"), ("labeller", "labeller-2.md"), ("writer", "writer-tuning.md"),
               ("writer", "writer-heldout.md"), ("auditor", "overlap-auditor.md")]
OPERATOR = [("governance/project/operator/brief.md", "51c459cfbcfec47652df455844480a56a5bc91b5fba3bcf57dc807c5dbf08cc2"),
            ("governance/project/operator/reviewer-brief.md",
             "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a")]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def show(path):
    return subprocess.run(["git", "-C", TREE, "show", f"{MERGE}:{path}"], capture_output=True, check=True).stdout


before = ("# ACT-INDEP-WALLS-1: the owner's approved list (DEC-1101 (2)). The launch script builds a wall only from files\n"
          "# whose sha256 is here. Written by the owner's operator only; the six refused roles neither read nor write it.\n")
for n in ORDER:
    assert sha(show(f"governance/project/indep-walls/{n}")) == TEMPLATE[n], n
    before += f"{TEMPLATE[n]}  template governance/project/indep-walls/{n}\n"
assert sha(before.encode()) == LIST_BEFORE, "APPROVED.before does not rebuild to ACT-INDEP-WALLS-1's recorded sha256"
launch = sha(show(SCRIPT))
merge12 = subprocess.run(["git", "-C", TREE, "rev-parse", "--short=12", MERGE], capture_output=True, text=True,
                         check=True).stdout.strip()
after = before + (
    "# ACT-W2-149-INSTALL-1 (DEC-1101 (2)-(3), DEC-1112, DEC-1113): the fixed briefs the owner approved once\n"
    "# (SANDBOX-GUARD-EXP-DECLARATION §12), for the launch script " + SCRIPT + "\n"
    "# " + launch + " (W2-149 with its F11 follow-up, " + merge12 + "). Written by the owner's operator only.\n")
for kind, name in BRIEF_LINES:
    data = open(os.path.join(HERE, "briefs", name), "rb").read()
    after += f"{sha(data)}  brief {kind} {BRIEFS}/{name}\n"
after += ("# The operator agent's two fixed briefs (DEC-1109 (1)), approved once, kept on the owner's one list; no launch\n"
          "# can use them (the launch script knows no kind \"operator\").\n")
for path, h in OPERATOR:
    assert sha(show(path)) == h, path
    after += f"{h}  brief operator {path}\n"
open(os.path.join(HERE, "APPROVED.before"), "w").write(before)
open(os.path.join(HERE, "APPROVED.after"), "w").write(after)
ap = os.path.join(HERE, "apply.sh")
text = open(ap).read()
text = re.sub(r"^LAUNCH_SHA=.*$", f"LAUNCH_SHA={launch}", text, flags=re.M)
text = re.sub(r"^LIST_AFTER=.*$", f"LIST_AFTER={sha(after.encode())}", text, flags=re.M)
open(ap, "w").write(text)
print(f"launch script {launch[:12]} at {merge12}; APPROVED.before {sha(before.encode())[:12]}; "
      f"APPROVED.after {sha(after.encode())[:12]} ({after.count(chr(10))} lines); apply.sh {sha(text.encode())[:12]}")
