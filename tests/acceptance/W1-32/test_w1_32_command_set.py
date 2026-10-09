"""KPI success 5 [CAP-28.a], second half: the command set stays at the Wave 1 list.

"... the command set stays at the Wave 1 list (no command without a contract
item)."

The Wave 1 list is the twelve governance operations the registry reserves
(CAP-28.b; W1-07's ``RESERVED_COMMANDS``, which its suite holds present and
this file reads from there). W1-07's suite does not hold the other direction:
nothing there fails when a thirteenth command appears. Three have appeared
before this ticket: ``launch`` (CAP-61 names it), ``ci`` and ``telemetry``
(no contract item names either as a command: package P-3, README). They are
named here as found, not approved; this file holds that ``gov status`` and its
ticket add nothing more.

The first half of the line, a status question asked in natural language, needs
a file outside this ticket's paths (package P-2, README) and has no case.
"""

from __future__ import annotations

import re

import w1_32_support as support

cli_support = support.cli_support

# Found in ``gov --help`` at this ticket's start, beside the twelve; see the module text and package P-3.
ADDED_BEFORE_W1_32 = ("ci", "launch", "telemetry")


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


def test_this_ticket_adds_no_command(empty_project, sandbox):
    run = support.gov(empty_project, sandbox, "--help")
    commands = _commands(run)
    assert set(cli_support.RESERVED_COMMANDS) <= set(commands), f"a Wave 1 operation is gone\n{run.describe()}"
    extra = sorted(set(commands) - set(cli_support.RESERVED_COMMANDS) - set(ADDED_BEFORE_W1_32))
    assert not extra, f"gov has commands outside the Wave 1 list and the three found at this ticket's start: {extra}"


def test_status_has_no_sub_command_and_no_argument_that_acts(empty_project, sandbox):
    """One read command, asked one way: its help offers the shared options and nothing that writes."""
    run = support.gov(empty_project, sandbox, support.COMMAND, "--help")
    assert run.returncode == 0, run.describe()
    options = set(re.findall(r"(?<![\w-])--[a-z][a-z-]*", run.stdout))
    acting = sorted(option for option in options if re.search(r"write|fix|repair|save|cache|load|rebuild", option))
    assert not acting, f"gov status offers options that act: {acting}\n{run.describe()}"
