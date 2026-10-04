"""W1-46 -- a hard link to a file the role may not write, and ``mv --target-directory`` and ``install`` (batch 6).

Tests added after implementation, reason "delegated decision" (DEC-106).
DEC-334 (orchestrator, delegated; on DP-19 and DP-20; under DEC-311 and MR-3):

- "The guard refuses ``ln`` without ``-s`` (and ``link``, ``cp -l``) when the
  source is a file the role may not write: otherwise a later call writes
  through the hard link and changes an acceptance test."
- "The guard treats the destination of ``mv --target-directory=<dir>`` and of
  ``install`` as a write target, as it does for ``mv -t`` and ``cp -t``."

**1. A hard link, alone in its command.** The destination is a new name inside
the engineer's paths; the source is an acceptance test that exists, the
engineer's ticket file, or the freeze flag. Nothing is written after the link:
the link itself is what the guard refuses.

**2. ``mv --target-directory=<dir>``.** The directory is given by the option;
the one operand is the engineer's own file, a source.

**3. ``install``.** With the directory in ``-t``, with ``-D`` and a destination
path, and in the plain form ``install <file> <destination>``.

Only the guard's decision is asserted, never a reason or a mechanism: refusing
a form the guard cannot judge is a refusal too. The controls are therefore
forms that are plainly inside the role's paths: source and destination of the
link both the role's own, and a destination the role may write.

Not tested (README, "Batch 6"): the other spellings of the target-directory
option for ``mv`` and ``install``, ``ln -t`` and ``ln`` with several sources,
``cp --link`` and ``cp -al``, a hard link made by another program, the other
roles, the other names of ``.gov-runtime/``, and ``install`` with several
sources or with ``-d``.

The guard is asked through the PreToolUse commands the project's committed
settings register. No session is started.
"""

from __future__ import annotations

import os

import pytest

import w1_46_support as support

w47 = support.w47
ENGINEER, TEST_DESIGNER = support.ENGINEER, support.TEST_DESIGNER
OWN = "src/gov/guard"                      # the engineer's ticket: src/gov/guard/**
OWN_FILE = f"{OWN}/decide.py"              # a file of the engineer's own, which exists
OWN_DIRECTORY = f"{OWN}/w1_46_directory"   # a directory inside the engineer's paths, made by the test that needs it
LINK = f"{OWN}/w1_46_link"                 # a new name inside the engineer's paths
TESTS = "tests/acceptance/W1-90"           # the acceptance tests of the engineer's ticket
TEST_FILE = f"{TESTS}/test_fixture.py"     # one that exists
TICKETS = ".tickets"
TICKET_FILE = f"{TICKETS}/{support.TICKET_OF[ENGINEER]}.md"
FREEZE = ".gov-runtime/freeze"


def _ask(guard, project, command, role=ENGINEER):
    return guard("Bash", w47.bash_input(command), role, cwd=project)


# --------------------------------------------------------------------------
# 1. A hard link whose source is a file the role may not write
# --------------------------------------------------------------------------

HARD_LINKS = {
    "ln-from-an-acceptance-test": f"ln {TEST_FILE} {LINK}.py",
    "cp-l-from-an-acceptance-test": f"cp -l {TEST_FILE} {LINK}.py",
    "link-from-a-ticket": f"link {TICKET_FILE} {LINK}.md",
    "ln-from-the-freeze-flag": f"ln {FREEZE} {LINK}",
}


@pytest.mark.parametrize("name", sorted(HARD_LINKS))
def test_the_guard_refuses_a_hard_link_to_a_file_the_role_may_not_write(guard, project, name):
    """The link is alone in its command, and its destination is inside the engineer's paths."""
    command = HARD_LINKS[name]
    assert os.path.isfile(project / TEST_FILE) and os.path.isfile(project / TICKET_FILE), "the fixture lost a source"
    assert not os.path.lexists(project / FREEZE), "the fixture project is frozen"
    w47.assert_stopped(_ask(guard, project, command), f"`{command}` by an engineer")


@pytest.mark.parametrize("spelling", ("link", "cp -l"))
def test_the_guard_does_not_refuse_a_hard_link_between_two_names_inside_the_roles_paths(guard, project, spelling):
    """The control for the two new spellings; ``ln`` has its control in ``test_w1_46_links_and_cp_targets.py``."""
    command = f"{spelling} {OWN_FILE} {LINK}.py"
    w47.assert_allowed(_ask(guard, project, command), f"`{command}` by an engineer")


def test_the_test_designer_may_hard_link_one_acceptance_test_to_another_name_there(guard, project):
    """The control on the role: for the test designer the acceptance test is a file it may write."""
    command = f"ln {TEST_FILE} {TESTS}/test_w1_46_other_name.py"
    w47.assert_allowed(_ask(guard, project, command, TEST_DESIGNER), f"`{command}` by the test designer")


# --------------------------------------------------------------------------
# 2. mv with the target directory given by the long option
# --------------------------------------------------------------------------

@pytest.mark.parametrize("directory", (TESTS, TICKETS), ids=("the-acceptance-tests", "the-tickets"))
def test_the_guard_refuses_mv_with_a_protected_directory_as_the_target_directory_option(guard, project, directory):
    """The one operand is the engineer's own file, a source; the file lands in the directory the option names."""
    command = f"mv --target-directory={directory} {OWN_FILE}"
    w47.assert_stopped(_ask(guard, project, command), f"`{command}` by an engineer")


def test_the_guard_does_not_refuse_mv_with_a_target_directory_inside_the_roles_paths(guard, project):
    """The control: the directory exists, inside the engineer's paths."""
    os.mkdir(project / OWN_DIRECTORY)
    command = f"mv --target-directory={OWN_DIRECTORY} {OWN_FILE}"
    w47.assert_allowed(_ask(guard, project, command), f"`{command}` by an engineer")


# --------------------------------------------------------------------------
# 3. install
# --------------------------------------------------------------------------

INSTALLS = {
    "target-directory-option-into-the-acceptance-tests": f"install -t {TESTS} {OWN_FILE}",
    "two-operands-onto-an-acceptance-test": f"install {OWN_FILE} {TEST_FILE}",
    "created-path-under-the-tickets": f"install -D {OWN_FILE} {TICKETS}/w1-46/decide.py",
    "two-operands-onto-a-ticket": f"install {OWN_FILE} {TICKET_FILE}",
}


@pytest.mark.parametrize("name", sorted(INSTALLS))
def test_the_guard_refuses_install_into_the_acceptance_tests_and_the_tickets(guard, project, name):
    """The source is the engineer's own file in every form."""
    command = INSTALLS[name]
    w47.assert_stopped(_ask(guard, project, command), f"`{command}` by an engineer")


def test_the_guard_does_not_refuse_install_to_a_destination_inside_the_roles_paths(guard, project):
    """The control: the plain form, from the engineer's own file to a new name beside it."""
    command = f"install {OWN_FILE} {OWN}/w1_46_installed.py"
    w47.assert_allowed(_ask(guard, project, command), f"`{command}` by an engineer")
