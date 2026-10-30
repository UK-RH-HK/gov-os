"""KPI 5 (DEC-911 items 1 and 2): the rule's id and keywords are written only in parts in every tracked file this
ticket writes. Every file the ticket wrote under ``src/gov/secrets/``, ``tests/unit/secrets_check/`` and
``tests/acceptance/W2-71/`` holds neither of row W2-L423's rule's keywords whole, in any case, in its content or its
path.

The ticket's files come from its own commits: every commit reachable from HEAD whose message carries the trailer
``Task: DAEO-e8f0`` (a trailer line, as git parses trailers; a mention in prose is not one), and the paths those
commits changed under the three folders; plus the working tree's changed and untracked files there. Merge commits are
left out (``--no-merges``): the lead's merges carry the trailer too, but what they bring in is other tickets' work.
Nothing here depends on ``w2/integrate``, a merge base or the branch's name, so the list is the same on the ticket's
branch and in the main tree after the merge. If git cannot list the commits or the working tree, every file of the
three folders on disk is read instead (fail-closed: never an empty list that passes).

Rewrite-Reason: the close of 2026-10-30 02:12 was refused: the list was a diff from the merge base with
``w2/integrate``, which is empty once the ticket is merged, so the premise failed and its sister case read nothing.

A guard, green today: it must stay green, this suite's own files included.
"""

from __future__ import annotations

import subprocess

import w2_71_support as support

FOLDERS = ("src/gov/secrets", "tests/unit/secrets_check", "tests/acceptance/W2-71")
TICKET = "DAEO-e8f0"
OWN = "tests/acceptance/W2-71/test_w2_71_keywords_in_parts.py"


def _git(*args, stdin=None):
    try:
        done = subprocess.run(["git", "-C", str(support.REPO_ROOT), *args], input=stdin, capture_output=True,
                              text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return 1, ""
    return done.returncode, done.stdout


def the_tickets_commits():
    """Every commit reachable from HEAD, merges left out, whose ``Task:`` trailer names this ticket; None when git
    cannot list them."""
    code, out = _git("log", "--no-merges", "--format=%H%x1f%(trailers:key=Task,valueonly,separator=%x1f)%x1e", "HEAD")
    if code != 0:
        return None
    commits = []
    for record in out.split("\x1e"):
        fields = record.strip().split("\x1f")
        if fields[0] and TICKET in (value.strip() for value in fields[1:]):
            commits.append(fields[0])
    return commits


def every_file_of_the_folders():
    """The fallback without git: every file of the three folders on disk (``__pycache__`` left out)."""
    found = set()
    for folder in FOLDERS:
        found.update(f"{folder}/{rel}" for rel in support.files_under(support.REPO_ROOT / folder,
                                                                      skip=(".git", "__pycache__")))
    return sorted(found)


def written_by_the_branch():
    """The paths this ticket wrote under the three folders: its commits' (by the trailer, merges left out), and the
    working tree's changed and untracked files. Rewrite-Reason: the refused close of 2026-10-30 02:12 (the merge-base
    diff it replaces is empty once the ticket is merged)."""
    commits = the_tickets_commits()
    if commits is None:
        return every_file_of_the_folders()
    changed = ""
    if commits:
        code, changed = _git("diff-tree", "--stdin", "--root", "--no-commit-id", "--name-only", "-r", "--", *FOLDERS,
                             stdin="".join(f"{sha}\n" for sha in commits))
        if code != 0:
            return every_file_of_the_folders()
    code_wt, worktree = _git("diff", "--name-only", "HEAD", "--", *FOLDERS)
    code_un, untracked = _git("ls-files", "--others", "--exclude-standard", "--", *FOLDERS)
    if code_wt != 0 or code_un != 0:
        return every_file_of_the_folders()
    names = (changed + "\n" + worktree + "\n" + untracked).splitlines()
    return sorted({name for name in names if name and name.startswith(tuple(f"{f}/" for f in FOLDERS))})


def test_premise_the_list_holds_this_suites_own_files():
    """The list holds this suite's own file, and a file under ``src/gov/secrets/`` (the ticket's code): it is read
    from the ticket's own commits. Rewrite-Reason: the refused close of 2026-10-30 02:12 (the merge-base diff is
    empty once the ticket is merged)."""
    written = written_by_the_branch()
    assert OWN in written, "the files the ticket writes do not include this suite's own: the list is not read right"
    code = [rel for rel in written if rel.startswith("src/gov/secrets/")]
    assert code, "the files the ticket writes include none under src/gov/secrets/: the list is not read right"


def test_no_file_the_branch_writes_holds_a_keyword_of_row_w2_l423s_rule_whole():
    """Rewrite-Reason: the refused close of 2026-10-30 02:12 (the merge-base diff was empty once the ticket was
    merged, so this case read nothing); it now reads the files of the ticket's own commits."""
    offenders = []
    for rel in written_by_the_branch():
        path = support.REPO_ROOT / rel
        if path.is_symlink() or not path.is_file():
            continue
        text = path.read_bytes().decode("latin-1")
        if support.holds_keyword(text) or support.holds_keyword(rel):
            offenders.append(rel)
    clean = not offenders
    assert clean, support.say(f"files this ticket writes that hold a keyword whole: {offenders}")
