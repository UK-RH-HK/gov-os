"""W2-69 (K4): the design question is answered with evidence in docs/research/W2-69-secrets-scan.md before the code.

Success: "The design question is answered with evidence in
docs/research/W2-69-secrets-scan.md before the code ... [DEC-897 item 1]."

Judged from git history only, in this repository: the note exists at HEAD and is
not empty, and the commit that first added it is an ancestor of (and not the same
as) every commit of this ticket (trailer ``Task: DAEO-rmbe``) that changes code
under ``src/``. The note's words are never read here: what it says is the
reviewer's to judge.
"""

from __future__ import annotations

import subprocess

import w2_69_support as support

NOTE = "docs/research/W2-69-secrets-scan.md"
TASK = "DAEO-rmbe"


def _git(*args):
    done = subprocess.run(["git", "-C", str(support.REPO_ROOT), *args], capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, f"git {' '.join(args)}: {done.stderr.strip()}"
    return done.stdout


def _ticket_commits():
    out = _git("log", "--format=%H%x1f%(trailers:key=Task,valueonly,separator=%x2c)%x1e", "HEAD")
    commits = []
    for entry in out.split("\x1e"):
        if "\x1f" not in entry:
            continue
        sha, tasks = entry.lstrip("\n").split("\x1f", 1)   # str.strip() would take \x1f for white space
        if TASK in [task.strip() for task in tasks.split(",")]:
            commits.append(sha)
    return commits


def test_the_design_note_was_committed_before_any_code_of_this_ticket():
    assert _git("cat-file", "-t", f"HEAD:{NOTE}").strip() == "blob", f"{NOTE} is not in HEAD"
    assert int(_git("cat-file", "-s", f"HEAD:{NOTE}").strip()) > 0, f"{NOTE} is empty"
    added = _git("log", "--diff-filter=A", "--format=%H", "HEAD", "--", NOTE).split()
    assert added, f"no commit of HEAD's history adds {NOTE}"
    first = added[-1]
    code = [sha for sha in _ticket_commits()
            if any(path.startswith("src/") for path in _git("show", "--format=", "--name-only", sha).split())]
    late = []
    for sha in code:
        ancestor = subprocess.run(["git", "-C", str(support.REPO_ROOT), "merge-base", "--is-ancestor", first, sha],
                                  capture_output=True, timeout=120).returncode == 0
        if sha == first or not ancestor:
            late.append(sha[:12])
    assert not late, (
        f"commits of {TASK} change code under src/ before (or with) the commit that first added {NOTE} "
        f"({first[:12]}): {late}")
