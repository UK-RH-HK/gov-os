#!/usr/bin/env python3
"""ACT-MEMORY-AUDIT-INSTALL-1's builder (DEC-1129 (2)).

APPROVED.before: the list as the last applied ACT (ACT-W2-149-INSTALL-1, applied by the owner's operator 2026-11-10
15:41, the list's recorded sha256 6b923cb4d552...) left it. It is rebuilt from the records, never read from the sets
root: ACT-W2-149-INSTALL-1's reviewed draft APPROVED.after (its sha256 must equal the recorded one), and every
template, brief and operator line of it is checked against the repository at the given commit.
APPROVED.after: APPROVED.before plus one comment block and three `brief` lines for the memory audit's three briefs
(sha256 as the owner approved them in DEC-1129 (2); the bytes checked at 8c18fa300 and at the given commit).
The hashes are then written into apply.sh.

    python3 freeze.py <main tree> <commit>
"""
import hashlib
import os
import re
import subprocess
import sys

TREE, COMMIT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
W149 = os.path.join(HERE, "..", "w2-149-install", "APPROVED.after")
W149_SHA = "6b923cb4d552077f99924fd5df38f1a448b21f863c4755c9ff4e0dcfb28ed959"     # DECIDED-NOT-DONE row 75
APPROVED_AT = "8c18fa300"                                                          # DEC-1129 (2)
SRC = "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs"
DEST = "governance/project/indep-briefs/memory-audit"
# the owner's hashes, DEC-1129 (2), verbatim
OWNER = {"writer": "bc0894230e3181e5be27726d60e9fb781f9355da1c4f8e76f69b400af97d379b",
         "checker": "cea517b8da7d4834bb2a698b9c7023670da36f0ceca6b3350656c6db77c45248",
         "auditor": "37be41c3fb2fea1654d68f71f1ecfc5ad4b41faaed9356a27ce1f01d8ef94245"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def show(rev, path):
    return subprocess.run(["git", "-C", TREE, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout


before = open(W149, "rb").read()
assert sha(before) == W149_SHA, "ACT-W2-149-INSTALL-1's draft list is not the recorded 6b923cb4d552"
n = 0
for line in before.decode().splitlines():
    m = re.fullmatch(r"([0-9a-f]{64})  (template|brief) (\S+)(?: (\S+))?", line)
    if not m:
        assert line.startswith("#"), line
        continue
    path = m.group(4) or m.group(3)
    assert sha(show(COMMIT, path)) == m.group(1), f"{path} at {COMMIT} is not as the recorded list has it"
    n += 1
assert n == 6 + 7, n

after = before.decode()
assert after.endswith("\n")
after += ("# ACT-MEMORY-AUDIT-INSTALL-1 (DEC-1129 (2), DEC-1101 (1)-(2), DEC-1125 (2)): the memory audit's three fixed\n"
          "# briefs, approved once by the owner on 2026-11-11 as written at " + APPROVED_AT + " (packages/MEMORY-AUDIT-1/briefs/);\n"
          "# the bytes below are those, placed under governance/project/indep-briefs/memory-audit/ so every wall's tree\n"
          "# leaves them out. No template line changes. Written by the owner's operator only.\n")
lines = []
for kind in ("writer", "checker", "auditor"):
    data = open(os.path.join(HERE, "briefs", kind + ".md"), "rb").read()
    assert sha(data) == OWNER[kind], f"briefs/{kind}.md is not the brief the owner approved"
    assert sha(show(APPROVED_AT, f"{SRC}/{kind}.md")) == OWNER[kind], f"{kind}.md at {APPROVED_AT}"
    assert sha(show(COMMIT, f"{SRC}/{kind}.md")) == OWNER[kind], f"{kind}.md at {COMMIT}"
    lines.append(f"{OWNER[kind]}  brief {kind} {DEST}/{kind}.md\n")
after += "".join(lines)
open(os.path.join(HERE, "APPROVED.before"), "wb").write(before)
open(os.path.join(HERE, "APPROVED.after"), "w").write(after)
ap = os.path.join(HERE, "apply.sh")
text = open(ap).read()
text = re.sub(r"^LIST_BEFORE=.*$", f"LIST_BEFORE={sha(before)}", text, flags=re.M)
text = re.sub(r"^LIST_AFTER=.*$", f"LIST_AFTER={sha(after.encode())}", text, flags=re.M)
open(ap, "w").write(text)
print(f"APPROVED.before {sha(before)[:12]} ({before.count(chr(10).encode())} lines); "
      f"APPROVED.after {sha(after.encode())[:12]} ({after.count(chr(10))} lines); apply.sh {sha(text.encode())[:12]}")
