"""W2-106 KPI success 2 and its failure line: with no gov, or a broken one, each line refuses.

KPI success 2: "Fail closed: with no gov found, or a first line that names no interpreter that runs, the line
refuses (exit 2) with a message naming what is missing; it never falls back to a bare ``python3`` [DEC-966 item 2,
DEC-822]". Failure: "A missing or broken gov lets the hook pass, or falls back to another interpreter."

Each of the three guard lines of each template file is run through ``sh -c`` in a temporary project whose program
(a stand-in at ``governance/kernel/hooks/<program>``) would allow the call (exit 0) if it ran: a line that falls back
to anything lets the call through. A decoy ``python3`` and ``python`` first on ``PATH`` leave a marker if started.
Claude Code blocks a PreToolUse call only on exit 2 (or a deny decision with exit 0); any other non-zero exit lets
the call through, so the refusal asked for is exit 2.
"""

from __future__ import annotations

import pytest

import w2_106_support as support

LINES = pytest.mark.parametrize(("name", "event"), support.LINE_PARAMS, ids=support.LINE_IDS)
MISSING_INTERPRETER = "/nonexistent/w2106/bin/python3"


def _refused_and_nothing_started(done, box, program, where):
    assert done.returncode == 2, (
        f"{where}: the line ended with exit {done.returncode}, so the call is not refused (only exit 2 blocks)\n"
        f"{done.describe()}")
    assert box.record(program) is None, f"{where}: the hook program still ran\n{done.describe()}"
    started = box.marks("path-python")
    assert not started, f"{where}: the line fell back to the {started} first on PATH\n{done.describe()}"


@LINES
def test_with_no_gov_found_the_line_refuses_and_says_so(name, event, box):
    """No ``$HOME/.local/bin/gov`` and no ``gov`` on ``PATH``. Exit 2; standard error names what is missing: the
    gov, at ``$HOME/.local/bin/gov`` or on ``PATH``."""
    line = support.template_line(name, event)
    where = f"{support.FILES[name]}, {event}, with no gov"
    program = support.PROGRAM_OF[event]
    support.place_program(box, program)
    path = support.path_of(box.decoy_bin)
    support.assert_no_gov_on(path)
    done = support.run_line(line, box, path=path, event=event)
    _refused_and_nothing_started(done, box, program, where)
    assert ".local/bin/gov" in done.stderr and "PATH" in done.stderr, (
        f"{where}: the refusal does not name what is missing (no gov at {box.home_gov} or on PATH)\n"
        f"{done.describe()}")


@LINES
def test_a_home_gov_whose_first_line_names_no_interpreter_is_refused(name, event, box):
    """``$HOME/.local/bin/gov`` is there, but its first line is no ``#!`` line: it names no interpreter. Exit 2;
    standard error names that gov."""
    line = support.template_line(name, event)
    where = f"{support.FILES[name]}, {event}, a gov whose first line names no interpreter"
    program = support.PROGRAM_OF[event]
    support.script(box.home_gov, "import sys\nfrom gov.cli.main import main\nsys.exit(main())\n")
    support.place_program(box, program)
    path = support.path_of(box.decoy_bin)
    support.assert_no_gov_on(path)
    done = support.run_line(line, box, path=path, event=event)
    _refused_and_nothing_started(done, box, program, where)
    assert str(box.home_gov) in done.stderr, (
        f"{where}: the refusal does not name the gov whose first line names no interpreter ({box.home_gov})\n"
        f"{done.describe()}")


@LINES
def test_a_home_gov_whose_interpreter_is_missing_is_refused(name, event, box):
    """``$HOME/.local/bin/gov``'s first line names an interpreter that does not exist. Exit 2; standard error names
    that interpreter."""
    line = support.template_line(name, event)
    where = f"{support.FILES[name]}, {event}, a gov naming a missing interpreter"
    program = support.PROGRAM_OF[event]
    support.script(box.home_gov, f"#!{MISSING_INTERPRETER}\nimport sys\nfrom gov.cli.main import main\nsys.exit(main())\n")
    support.place_program(box, program)
    path = support.path_of(box.decoy_bin)
    support.assert_no_gov_on(path)
    done = support.run_line(line, box, path=path, event=event)
    _refused_and_nothing_started(done, box, program, where)
    assert MISSING_INTERPRETER in done.stderr, (
        f"{where}: the refusal does not name the missing interpreter {MISSING_INTERPRETER}\n{done.describe()}")


@LINES
def test_a_broken_home_gov_does_not_fall_back_to_the_gov_on_path(name, event, box, pin):
    """``$HOME/.local/bin/gov`` names a missing interpreter; a working gov (a link to the stand-in pin) is on
    ``PATH``. The line refuses: it does not fall back to another interpreter, that gov's included."""
    line = support.template_line(name, event)
    where = f"{support.FILES[name]}, {event}, a broken home gov and a working gov on PATH"
    program = support.PROGRAM_OF[event]
    support.script(box.home_gov, f"#!{MISSING_INTERPRETER}\nimport sys\nfrom gov.cli.main import main\nsys.exit(main())\n")
    support.link_gov(pin.gov, box.path_bin / "gov")
    support.place_program(box, program)
    done = support.run_line(line, box, path=support.path_of(box.path_bin, box.decoy_bin), event=event)
    _refused_and_nothing_started(done, box, program, where)
    assert not pin.marks("pin-python-"), (
        f"{where}: the line fell back to the interpreter of the gov on PATH\n{done.describe()}")
