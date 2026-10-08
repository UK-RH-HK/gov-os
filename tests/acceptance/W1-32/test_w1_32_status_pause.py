"""KPI success 3 (DEC-364): the pause state appears in ``gov status``.

The two status cases W1-28 handed over, and the edges of the flag. The pause
state is the freeze the guard enforces: the marked flag ``.gov-runtime/freeze``
(DEC-402, DEC-404) or its mirror outside the repository (DEC-429). Every case
builds its own project in a temporary folder, pauses it with ``gov pause`` as
the owner, and never touches this repository's flag: inside a launched session
that path is a placeholder device whether or not a flag exists (``bootstrap.md``,
"Observations from launched worker sessions").
"""

from __future__ import annotations

import os

import pytest

import w1_32_support as support

pause_support = support.pause_support


def _pause(project, sandbox, interface, *args, role=pause_support.OWNER):
    return pause_support.succeeded(pause_support.pause(project.root, sandbox, *args, role=role), interface)


def _flag(project):
    return project.root / support.FREEZE_FLAG_REL


# --------------------------------------------------------------------------
# The two cases moved from W1-28
# --------------------------------------------------------------------------

def test_a_project_that_is_not_paused_says_so(project, status, interface):
    assert not os.path.lexists(_flag(project))
    assert support.paused(support.answered(status(), interface)) is False


def test_a_paused_project_says_so(project, sandbox, status, interface):
    _pause(project, sandbox, interface)
    assert support.paused(support.parts(status(), interface)) is True


# --------------------------------------------------------------------------
# Who paused, and the rest of the answer
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role, name", [(pause_support.OWNER, pause_support.OWNER_NAME),
                                        (pause_support.ORCHESTRATOR, pause_support.ORCHESTRATOR)])
def test_a_paused_project_names_who_paused_it(project, sandbox, status, interface, role, name):
    """The flag's marker line is ``FROZEN <who> <when>`` (DEC-404): the status shows the caller it names."""
    _pause(project, sandbox, interface, role=role)
    answer = support.parts(status(), interface)
    assert support.paused(answer) is True
    assert name in support.text_of(answer[support.PAUSE]), \
        f"the pause part does not name {name}, who paused: {support.text_of(answer[support.PAUSE])}"


def test_a_paused_project_still_reports_its_other_parts(project, sandbox, status, interface):
    """A pause stops writes, not the owner's view: the tickets and the packages are there as before."""
    before = support.answered(status(), interface)
    _pause(project, sandbox, interface)
    after = support.parts(status(), interface)
    assert support.ids(after[support.TICKETS][support.READY]) == support.ids(before[support.TICKETS][support.READY])
    assert support.ids(after[support.PACKAGES]) == support.ids(before[support.PACKAGES])


def test_the_pause_state_is_the_projects_own(project, empty_project, sandbox, interface):
    """Two projects, one paused: each status answers for its own ``--root``, from another working directory."""
    _pause(project, sandbox, interface)
    for target, expected in ((project, True), (empty_project, False)):
        run = support.cli_support.run_gov_with_code(support.REPO_ROOT, target.root, sandbox, support.COMMAND,
                                                    "--json", "--root", str(target.root), cwd=sandbox.elsewhere)
        assert support.paused(support.parts(run, interface)) is expected, run.describe()


# --------------------------------------------------------------------------
# The edges of the flag
# --------------------------------------------------------------------------

def test_an_empty_file_at_the_flags_path_is_no_pause(project, status, interface):
    """DEC-402: an empty placeholder is no freeze, for the guard and so for the status."""
    _flag(project).parent.mkdir(parents=True, exist_ok=True)
    _flag(project).write_bytes(b"")
    assert support.paused(support.answered(status(), interface)) is False


def test_a_flag_removed_by_hand_with_its_mirror_left_is_not_reported_as_not_paused(project, sandbox, status, interface):
    """DEC-429: the mirror alone keeps the guard frozen, so "not paused" would be false."""
    _pause(project, sandbox, interface)
    _flag(project).unlink()
    answer = support.parts(status(), interface)
    assert support.paused(answer) is not False, \
        f"the flag is gone, its mirror still freezes the tree, and the status says not paused: " \
        f"{support.text_of(answer[support.PAUSE])}"
