"""KPI success 5 [CAP-28.a], second half: the command set stays at the Wave 1 list.

"... the command set stays at the Wave 1 list (no command without a contract
item)."

The Wave 1 list is the twelve governance operations the registry reserves
(CAP-28.b; W1-07's ``RESERVED_COMMANDS``, which its suite holds present and
this file reads from there). W1-07's suite does not hold the other direction:
nothing there fails when a thirteenth command appears. Three appeared before
this ticket: ``launch``, ``ci`` and ``telemetry`` (package P-3, README).

Rewritten in the follow-up after W1-41 (reason: DEC-542). The owner's answer
to P-3: "``ci``, ``launch``, ``telemetry`` and ``lock`` are recorded in the
command list". The three are no longer pinned "as found, not approved": they
are read from the recorded lines of W1-07's support, and the command set is
held exactly, the twelve and the three. ``lock`` is recorded as the module
command ``python3 -m gov.lock`` and is no ``gov`` command: recording it adds
none, and a ``gov lock`` fails this file.

The first half of the line, a status question asked in natural language, needs
a file outside this ticket's paths (package P-2, README) and has no case.
"""

from __future__ import annotations

import re

import w1_32_support as support

cli_support = support.cli_support

# The ``gov`` commands recorded beside the twelve (DEC-542), and the recorded command that is none of ``gov``'s.
RECORDED = cli_support.RECORDED_GOV_COMMANDS
NO_GOV_COMMAND = cli_support.RECORDED_MODULE_COMMANDS


def _commands(run):
    """The command names of ``gov --help``: the names in argparse's ``{a,b}`` list, or the indented first words."""
    found = re.search(r"\{([a-z,-]+)\}", run.stdout)
    if found:
        return sorted(found.group(1).split(","))
    listed = run.stdout.split("positional arguments:", 1)[-1].split("\noptions:", 1)[0]
    return sorted(set(re.findall(r"^    ([a-z][a-z-]*)(?:\s|$)", listed, re.MULTILINE)))


def test_status_is_one_of_the_wave_1_operations(empty_project, sandbox):
    run = support.gov(empty_project, sandbox, "--help")
    assert run.returncode == 0, run.describe()
    assert support.COMMAND in cli_support.RESERVED_COMMANDS
    assert support.COMMAND in _commands(run), f"gov --help does not name status\n{run.describe()}"


def test_the_command_set_is_the_twelve_and_the_three_recorded_ones(empty_project, sandbox):
    """Rewritten (DEC-542) from ``test_this_ticket_adds_no_command``, which pinned the three as found. Every
    command ``gov`` offers is in the command list, every ``gov`` command of the list is offered, and the
    recorded module command is not among them."""
    assert tuple(RECORDED) == ("ci", "launch", "telemetry") and tuple(NO_GOV_COMMAND) == ("lock",)
    run = support.gov(empty_project, sandbox, "--help")
    commands = _commands(run)
    assert set(cli_support.RESERVED_COMMANDS) <= set(commands), f"a Wave 1 operation is gone\n{run.describe()}"
    gone = sorted(set(RECORDED) - set(commands))
    assert not gone, f"a recorded command is gone from gov --help: {gone}\n{run.describe()}"
    extra = sorted(set(commands) - set(cli_support.RESERVED_COMMANDS) - set(RECORDED))
    assert not extra, f"gov has commands the command list does not record: {extra}"


def test_status_has_no_sub_command_and_no_argument_that_acts(empty_project, sandbox):
    """One read command, asked one way: its help offers the shared options and nothing that writes."""
    run = support.gov(empty_project, sandbox, support.COMMAND, "--help")
    assert run.returncode == 0, run.describe()
    options = set(re.findall(r"(?<![\w-])--[a-z][a-z-]*", run.stdout))
    acting = sorted(option for option in options if re.search(r"write|fix|repair|save|cache|load|rebuild", option))
    assert not acting, f"gov status offers options that act: {acting}\n{run.describe()}"
