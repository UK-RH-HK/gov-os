"""Row W2-L423's early warning (owner, DEC-911 (b)): the paths of the files under a tree's .gov-runtime/ that hold a
keyword of row W2-L423's rule, the gitleaks default rule that takes a bare 40-hex string for a token. A full commit hash
beside one of them turns the secrets-indexing check red, so I shorten the hashes or drop the keyword before gate (b).

Prints paths only, never content. Walks the folder as the check does (links followed, except into ~/gov-os-runs) and
reads every file in pieces, case-insensitively, as gitleaks matches keywords. The keywords are written in parts so that
this file never holds one. Usage: keyword_warn.py [<project root>]. Exit 0 with no hit, 1 with hits, 2 if a file cannot
be read (nothing is passed undecided).

Scope (owner, DEC-923, P-W2-L423-Q (a)): the files sessions write under .gov-runtime/ (scratch, logs, records and every
other file there), not the index stores that `gov rebuild` builds from tracked files (`codeintel/`, `store.db*`,
`query-vector-cache.db*` at the folder's top). The pinned secrets check (W2-69) reads those stores itself and is not
changed. Anything else under .gov-runtime/, a new or unknown file included, is still read.
"""
import os
import sys
from pathlib import Path

KEYWORDS = tuple(part[0] + part[1] for part in (("source", "graph"), ("sgp", "_")))
PIECE = 1 << 20
TAIL = max(len(word) for word in KEYWORDS) - 1

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/usain/Dynamic-Agentic-Engineering-OS")
runtime = root / ".gov-runtime"
runs = os.path.realpath(os.path.expanduser("~/gov-os-runs"))


def holds(path: Path) -> bool:
    carry = b""
    with open(path, "rb") as handle:
        while piece := handle.read(PIECE):
            text = (carry + piece).lower()
            if any(word.encode() in text for word in KEYWORDS):
                return True
            carry = text[-TAIL:]
    return False


STORE_FOLDERS = ("codeintel",)  # DEC-923: the index stores, at .gov-runtime/'s top only
# DEC-925 item 1, INTERIM until W2-74 merges: the close's own JUnit evidence (.gov-runtime/close/), which the judge
# writes and which holds a keyword only through W2-69's case name. Remove this line when W2-74 merges.
STORE_FOLDERS += ("close",)
STORE_FILES = ("store.db", "query-vector-cache.db")  # and their -wal / -shm / -journal companions

hits, unread, seen = [], [], set()
for folder, folders, names in os.walk(runtime, followlinks=True):
    real = os.path.realpath(folder)
    if real in seen or real == runs or real.startswith(runs + os.sep):
        folders[:] = []
        continue
    seen.add(real)
    if Path(folder) == runtime:
        folders[:] = [f for f in folders if f not in STORE_FOLDERS]
        names = [n for n in names if not any(n == s or n.startswith(s + "-") for s in STORE_FILES)]
    for name in names:
        path = Path(folder) / name
        target = os.path.realpath(path)
        if target == runs or target.startswith(runs + os.sep) or not os.path.isfile(path):
            continue
        try:
            if holds(path):
                hits.append(path.relative_to(root).as_posix())
        except OSError:
            unread.append(path.relative_to(root).as_posix())
for path in sorted(hits):
    print(f"keyword-warn: {path}")
for path in sorted(unread):
    print(f"keyword-warn: not read: {path}")
print(f"keyword-warn: {len(hits)} file(s) hold a keyword of row W2-L423's rule; {len(unread)} not read")
sys.exit(2 if unread else 1 if hits else 0)
