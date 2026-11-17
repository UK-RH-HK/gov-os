"""W1-46 -- a write through a link made in the same command, and ``cp`` with its directory in an option (batch 5).

Tests added after implementation, reason "review finding (DEC-136)". A review
described two behaviours the suite missed. Each is decided from the
specification:

- MR-3: "the implementer's allowed paths exclude the acceptance tests".
- DEC-135: "fix every probe finding that could lose work or let an implementer
  change acceptance tests".
- DEC-311: "The guard treats the destination of ``ln`` as a write target", and
  "``.gov-runtime/`` outside ``scratch/`` is denied by the guard to every role".
- KPI success 10: "a write to the freeze flag, the snapshots, the findings or
  the records fails, through a file tool, through an opaque Bash form and
  through ln".
- The guard holds a role's writes to its ticket's ``allowed_paths`` (success 5
  says so for the research role; W1-03 for the others): ``.tickets/`` is in no
  engineer's ticket here.

**1. A link and a write through it, in one command.** The command first links
a name inside the engineer's paths to a tree the engineer may not write, and
then writes through that name. The file that changes is in the protected tree,
so the command is a write there, whatever name it used.

**2. ``cp`` with the target directory in an option.** ``cp -t <directory>`` and
``cp --target-directory=<directory>`` write into that directory; the last
operand is a source.

Only the guard's decision is asserted, never a reason or a mechanism: refusing
a form the guard cannot judge is a refusal too. The controls are therefore
forms that are plainly inside the role's paths: a link alone, and ``cp`` with
its destination as the last operand.

Not tested (README, "Batch 5"): other separators than ``&&`` and ``;``, a link
made by another program than ``ln``, a write through the link by an opaque
form, a hard link to an acceptance test with no write after it or with the
write in a later call (DP-19), and ``mv`` and ``install`` (DP-20).

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

import pytest

import w1_46_support as support

w47 = support.w47
ENGINEER = support.ENGINEER
OWN = "src/gov/guard"                      # the engineer's ticket: src/gov/guard/**
OWN_FILE = f"{OWN}/decide.py"              # a file of the engineer's own, which exists
LINK = f"{OWN}/w1_46_link"                 # a new name inside the engineer's paths
TESTS = "tests/acceptance/W1-90"           # the acceptance tests of the engineer's ticket
TEST_FILE = f"{TESTS}/test_fixture.py"     # one that exists
TICKETS = ".tickets"
TICKET_FILE = f"{TICKETS}/{support.TICKET_OF[ENGINEER]}.md"


def _ask(guard, project, command):
    return guard("Bash", w47.bash_input(command), ENGINEER, cwd=project)


# --------------------------------------------------------------------------
# 1. A link and a write through it, in one command
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kind", ("symbolic", "hard"))
def test_the_guard_does_not_refuse_a_link_whose_source_and_destination_are_inside_the_roles_paths(
        kernel_guard, kernel_project, kind):
    """The control: the link alone, from a file of the engineer's own to a new name beside it."""
    guard, project = kernel_guard, kernel_project
    command = {"symbolic": f"ln -s {project}/{OWN_FILE} {LINK}.py", "hard": f"ln {OWN_FILE} {LINK}.py"}[kind]
    w47.assert_allowed(_ask(guard, project, command), f"`{command}` by an engineer")


# --------------------------------------------------------------------------
# 2. cp with the target directory given by an option
# --------------------------------------------------------------------------

def test_cp_with_the_destination_as_the_last_operand_is_judged_as_before(kernel_guard, kernel_project):
    """The control: allowed inside the engineer's paths, refused in the acceptance tests and the tickets."""
    guard, project = kernel_guard, kernel_project
    inside = f"cp {OWN_FILE} {OWN}/w1_46_copy.py"
    w47.assert_allowed(_ask(guard, project, inside), f"`{inside}` by an engineer")
    for destination in (TEST_FILE, f"{TESTS}/", TICKET_FILE):
        outside = f"cp {OWN_FILE} {destination}"
        w47.assert_stopped(_ask(guard, project, outside), f"`{outside}` by an engineer")
