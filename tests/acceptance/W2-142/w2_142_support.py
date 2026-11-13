"""Shared helpers of the W2-142 acceptance tests (README).

The two kernel skills as the tree holds them, and as the reference commit held them (``git show``), with the
reference's blob ids checked first, so a test never compares against a text it did not mean.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

RETRIEVAL = "template/governance/kernel/skills/retrieval/SKILL.md"
DISCOVERY = "template/governance/kernel/skills/discovery/SKILL.md"

# The reference: this branch's base, an ancestor of w2/integrate; integrate's head 1d49ca867188 holds the same two
# blobs (README, "The reference").
REFERENCE_COMMIT = "8bb10a68366c454c1eb93b505ed45690ceda0285"
REFERENCE_BLOBS = {
    RETRIEVAL: "1496eecd88db872de7707cc26d8f4955912fd418",
    DISCOVERY: "c2cf6cadaaa788e6e933f217172b5747149fc003",
}

# W2-138's step-5 line, word for word as the reference holds it (line 22 of the retrieval skill).
STEP_5_LINE = (
    "   Before relying on an evidence item, compare its `sha256` with the sha256 of the same lines (`start_line` to "
    "`end_line`) in your own tree; if they differ, your tree is behind or ahead of the store at `result.store.commit`: "
    "read the store's text with `git show <commit>:<path>`, and never cite the store's line numbers as your tree's "
    "(DEC-1090 (3))."
)

# The discovery skill's line 55, word for word as the reference holds it.
LINE_55 = (
    "Before formulating a decision package, the practitioner gathers context through `gov retrieve` (CAP-34.c). "
    "The retrieval bundle surfaces related specifications, decisions and evidence so that packages present questions "
    "the existing record does not already answer."
)

VERSION_LINE = re.compile(r'^version: "[^"\n]*"$', re.M)


def current(path: str) -> str:
    return (REPO / path).read_text(encoding="utf-8")


def _git(*args: str) -> str:
    done = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=False)
    assert done.returncode == 0, f"premise: git {' '.join(args)} failed: {done.stderr.strip()}"
    return done.stdout


def reference(path: str) -> str:
    """The skill as the reference commit held it, after checking that the commit holds the expected blob."""
    blob = _git("rev-parse", f"{REFERENCE_COMMIT}:{path}").strip()
    assert blob == REFERENCE_BLOBS[path], f"premise: {REFERENCE_COMMIT[:12]}:{path} is blob {blob}, not the reference"
    return _git("cat-file", "-p", blob)


def fold(text: str) -> str:
    return " ".join(text.split()).lower()


def version(text: str) -> str | None:
    from gov.util.frontmatter import with_body

    front, _body = with_body(text)
    return None if front is None else front.get("version")
