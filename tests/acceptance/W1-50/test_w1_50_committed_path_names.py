"""W1-50 — a path a commit changes is judged by its name in the commit.

Added after implementation, from the review after the suite went green
(DEC-136, DEC-137). The behaviour, as it was passed to the test designer:

    A path a commit changes is judged by its name in the commit, not by where
    the working tree leads today.

KPI failure 2: "A commit that changes a path outside the allowed paths of its
own Role and Task trailers raises no finding, whoever the caller is".

KPI success 1 [CAP-58.h]: "each commit's paths against the allowed paths of its
own Role and Task trailers".

A commit's paths are the names in its tree. They are the same in every clone
and every worktree, and they are what a merge brings to another branch. What a
name leads to in one working tree, at the moment the check runs, is not part
of the commit.

**The call.** It makes an engineer's commit that changes an existing
acceptance test. Then, in the working tree only:

1. every committed file under ``tests/acceptance`` is marked skip-worktree
   (``git update-index --skip-worktree``), so git does not compare it with the
   working tree;
2. the directory ``tests/acceptance`` is removed and a symbolic link of that
   name is made, pointing at ``src/gov/guard``, inside the engineer ticket's
   allowed paths;
3. ``/tests/acceptance`` is written to ``.git/info/exclude``, so the link is no
   untracked file for ``git status``.

``git status`` is empty after the call: the swap is hidden. The commit still
changes ``tests/acceptance/W1-90/test_fixture.py``.

The same commit without the swap is
``test_a_commit_outside_the_paths_of_its_own_trailers_is_flagged_whoever_the_caller_is``
(``engineer-commit-of-an-acceptance-test``, callers ``orchestrator`` and
``engineer``).
"""

from __future__ import annotations

import os

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
TICKET = support.TICKET
AS_ENGINEER = support.AS_ENGINEER

ACCEPTANCE = support.ACCEPTANCE
LINK_TARGET = "../src/gov/guard"   # from tests/: inside DAEO-zz90's allowed paths

HIDDEN_SWAP = (
    f"git ls-files -z -- {ACCEPTANCE} | xargs -0 git update-index --skip-worktree"
    f" && rm -rf {ACCEPTANCE} && ln -s {LINK_TARGET} {ACCEPTANCE}"
    f" && echo /{ACCEPTANCE} >> .git/info/exclude"
)

# name: GOV_ROLE of the caller
CALLERS = {
    "orchestrator-session": ORCHESTRATOR,
    "engineer-session": ENGINEER,
}


@pytest.mark.parametrize("caller", sorted(CALLERS), ids=sorted(CALLERS))
def test_a_committed_acceptance_test_is_flagged_although_its_directory_is_then_a_link_into_the_ticket_s_paths(
        project, call, caller):
    """In the orchestrator's own call the commit is judged by its trailers; in the engineer's call against the
    caller. Neither may write an acceptance test."""
    role = CALLERS[caller]
    path = support.ACCEPTANCE_FILE
    command = support.commit(path, AS_ENGINEER) + " && " + HIDDEN_SWAP
    result, left = call(project, command, role, TICKET)   # the fixture asserts that git status is empty
    link = project / ACCEPTANCE
    assert link.is_symlink() and os.readlink(link) == LINK_TARGET and (project / "src/gov/guard").is_dir(), (
        f"the fixture is wrong: {ACCEPTANCE} is no symbolic link to {LINK_TARGET} after the call"
    )
    assert support.changed_paths(project, "HEAD") == [path], (
        f"the fixture is wrong: the commit changes {support.changed_paths(project, 'HEAD')}, not {path}"
    )
    what = (f"a commit of {path} with trailers {AS_ENGINEER}, in a call with GOV_ROLE={role!r} on {TICKET} that "
            f"then replaces {ACCEPTANCE} in the working tree by a hidden symbolic link to {LINK_TARGET}")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)
    assert link.is_symlink(), f"{what}: the check changed the working tree: {ACCEPTANCE} is no longer the link"
