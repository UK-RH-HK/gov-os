"""W1-46 -- an option with a value of its own, written after the destination of ``install``, ``cp`` or ``ln`` (batch 7).

Tests added after implementation, reason "review finding (DEC-136)". A review
described one behaviour of the guard that batches 5 and 6 miss. It is decided
from the specification:

- MR-3: "the implementer's allowed paths exclude the acceptance tests".
- DEC-135: "fix every probe finding that could lose work or let an implementer
  change acceptance tests".
- DEC-334: "The guard treats the destination of ``mv --target-directory=<dir>``
  and of ``install`` as a write target".
- The guard holds a role's writes to its ticket's ``allowed_paths``:
  ``.tickets/`` is in no engineer's ticket here. ``cp`` onto an acceptance test
  or a ticket is refused already (batch 5, the control of its part 2).

- DEC-311: "The guard treats the destination of ``ln`` as a write target".
  ``ln`` has the same behaviour today; it was seen while the red result was
  taken, and this line decides it, so it has one case.

**The form.** ``install``, ``cp`` and ``ln`` accept an option after their
operands: ``install <file> <destination> -m 644`` (also ``--mode 644``),
``cp <file> <destination> -S bak`` (also ``--suffix bak``),
``ln -sf <target> <destination> -S bak``. The option's value is not an operand;
the file lands on ``<destination>``. The engineer's working directory is inside
its own paths, so that the value, read as a path, is a name the engineer may
write: the session's ``cwd`` is there, or the command starts with
``cd <that directory> &&``. The destination is an acceptance test that exists,
or the engineer's ticket file.

Only the guard's decision is asserted, never a reason or a mechanism: refusing
a form the guard cannot judge is a refusal too. The controls are therefore
forms that are plainly inside the role's paths: ``install`` with the option
before its operands, and ``cp`` with no option, from a working directory inside
the role's paths.

Not tested (README, "Batch 7"): the same form inside the role's paths, the
other options with a value (``-o``, ``-g``, ``--owner``, ``--group``),
``mv`` in that form (refused today), a hard link in that form,
``.gov-runtime/`` as the destination, and the other roles.

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

import w1_46_support as support

w47 = support.w47
ENGINEER = support.ENGINEER
OWN = "src/gov/guard"                      # the engineer's ticket: src/gov/guard/**
OWN_NAME = "decide.py"                     # a file of the engineer's own, which exists, named from that directory


def _ask(guard, project, directory, command):
    return guard("Bash", w47.bash_input(command), ENGINEER, cwd=project / directory)


def test_the_guard_does_not_refuse_install_with_its_option_before_the_operands(kernel_guard, kernel_project):
    """The control: the usual spelling, to a new name inside the engineer's paths, from the repository root."""
    guard, project = kernel_guard, kernel_project
    command = f"install -m 644 {OWN}/{OWN_NAME} {OWN}/w1_46_installed.py"
    w47.assert_allowed(_ask(guard, project, "", command), f"`{command}` by an engineer")


def test_the_guard_does_not_refuse_cp_between_two_names_of_the_working_directory_inside_the_roles_paths(
        kernel_guard, kernel_project):
    """The control on the working directory: the session's ``cwd`` is inside the engineer's paths, and so are both names."""
    guard, project = kernel_guard, kernel_project
    command = f"cp {OWN_NAME} w1_46_copy.py"
    w47.assert_allowed(_ask(guard, project, OWN, command), f"`{command}` by an engineer, working directory {OWN}")
