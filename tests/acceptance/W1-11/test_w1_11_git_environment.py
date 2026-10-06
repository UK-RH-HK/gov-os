"""The interface, batch 4: `check(root)` checks `root`, whatever repository the environment names. Added after
implementation, from a behaviour a review described (DEC-136).

Git sets ``GIT_DIR`` when it runs a hook, and a git command that finds it reads that repository, not the one it
was sent to. The README's interface: the findings are those of ``root``; a ``root`` that is no git repository
raises ``GovError`` and is never an empty list. So with ``GIT_DIR`` naming another repository, a clean one, the
check of a ``root`` that holds an agent's ``ACTIVE`` decision gives that finding or raises ``GovError``; it never
passes on the other repository's account.

The suite's driver builds the checker's environment from scratch, so each case passes the variable on purpose.
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import AGENT, OWNER, adr_path, decision

ADR = "ADR-0010"
PATH = adr_path(ADR)


@pytest.fixture()
def elsewhere(api, tmp_path):
    """``GIT_DIR`` naming another repository: a clean register the owner committed, which passes the check."""
    other = support.Project(tmp_path / "elsewhere")
    other.put(support.CLEAN, who=OWNER)
    assert api.check_only(other.root) == [], "the fixture's other repository does not pass"
    return {"GIT_DIR": str(other.root / ".git")}


def with_an_agent_decision(project):
    project.put(support.CLEAN, who=OWNER)
    project.put({PATH: decision(ADR, "ACTIVE")}, who=AGENT)


def test_git_dir_naming_another_repository_does_not_hide_the_findings_of_the_root(api, project, elsewhere):
    with_an_agent_decision(project)
    kind, result = support.outcome(api, project.root, environment=elsewhere)
    if kind == "findings":
        support.assert_flagged(result, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def test_git_dir_does_not_make_a_folder_that_is_no_repository_pass(api, tmp_path, elsewhere):
    """Without the variable this is `test_a_folder_that_is_no_git_repository_is_an_error_not_a_pass`."""
    folder = tmp_path / "plain"
    (folder / "docs" / "adr").mkdir(parents=True)
    (folder / PATH).write_text(decision(ADR, "ACTIVE"), encoding="utf-8")
    kind, result = support.outcome(api, folder, environment=elsewhere)
    assert kind == "error", f"a folder that is no git repository gave findings:\n{support.show(result)}"


def test_git_dir_does_not_make_a_subfolder_of_a_repository_pass(api, project, elsewhere):
    """`root` is a folder inside the repository that holds the agent's decision. Whether such a `root` is an error
    or is checked as its repository, it does not pass."""
    with_an_agent_decision(project)
    kind, result = support.outcome(api, project.root / "docs", environment=elsewhere)
    if kind == "findings":
        support.assert_flagged(result, support.ACTIVE_UNAPPROVED, [ADR])
