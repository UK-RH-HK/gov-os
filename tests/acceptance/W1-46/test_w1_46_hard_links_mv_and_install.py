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

Rewrite-Reason: DEC-953 item 2 (W2-90, DEC-957, DEC-906). The cases that asked this repository's live guard now
ask the kernel's: the ``kernel_*`` fixtures are W1-46's launch project built on a project generated from the
template, whose ``.claude/settings.json`` rulesync generates from the template's sources, and the PreToolUse
lines those settings register, run from ``governance/kernel/hooks/`` (``tests/acceptance/W2-90/README.md``).
Each moved case names its fixtures by their old names in its first line; its verdict is the same.

Emergency 2 (docs/emergency-2/EMERGENCY-2.md 2.1, 2.2, 6.1; release 0.1.2): this repository's settings no longer
register the guard, so the cases that asked its committed guard to refuse a write are retired. The controls that ask
the kernel's guard, generated from the template, stay.
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


def _ask(guard, project, command, role=ENGINEER):
    return guard("Bash", w47.bash_input(command), role, cwd=project)


# --------------------------------------------------------------------------
# 1. A hard link whose source is a file the role may not write
# --------------------------------------------------------------------------

@pytest.mark.parametrize("spelling", ("link", "cp -l"))
def test_the_guard_does_not_refuse_a_hard_link_between_two_names_inside_the_roles_paths(kernel_guard,
                                                                                        kernel_project, spelling):
    """The control for the two new spellings; ``ln`` has its control in ``test_w1_46_links_and_cp_targets.py``."""
    guard, project = kernel_guard, kernel_project
    command = f"{spelling} {OWN_FILE} {LINK}.py"
    w47.assert_allowed(_ask(guard, project, command), f"`{command}` by an engineer")


def test_the_test_designer_may_hard_link_one_acceptance_test_to_another_name_there(kernel_guard, kernel_project):
    """The control on the role: for the test designer the acceptance test is a file it may write."""
    guard, project = kernel_guard, kernel_project
    command = f"ln {TEST_FILE} {TESTS}/test_w1_46_other_name.py"
    w47.assert_allowed(_ask(guard, project, command, TEST_DESIGNER), f"`{command}` by the test designer")


# --------------------------------------------------------------------------
# 2. mv with the target directory given by the long option
# --------------------------------------------------------------------------

def test_the_guard_does_not_refuse_mv_with_a_target_directory_inside_the_roles_paths(kernel_guard, kernel_project):
    """The control: the directory exists, inside the engineer's paths."""
    guard, project = kernel_guard, kernel_project
    os.mkdir(project / OWN_DIRECTORY)
    command = f"mv --target-directory={OWN_DIRECTORY} {OWN_FILE}"
    w47.assert_allowed(_ask(guard, project, command), f"`{command}` by an engineer")


# --------------------------------------------------------------------------
# 3. install
# --------------------------------------------------------------------------

def test_the_guard_does_not_refuse_install_to_a_destination_inside_the_roles_paths(kernel_guard, kernel_project):
    """The control: the plain form, from the engineer's own file to a new name beside it."""
    guard, project = kernel_guard, kernel_project
    command = f"install {OWN_FILE} {OWN}/w1_46_installed.py"
    w47.assert_allowed(_ask(guard, project, command), f"`{command}` by an engineer")
