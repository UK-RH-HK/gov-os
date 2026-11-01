"""W2-106 KPI success 1, run: each line finds the installed gov, starts the interpreter its first line names with
``-E``, and keeps its exit codes.

KPI success 1: "... it finds the installed gov (``$HOME/.local/bin/gov``, else ``gov`` on PATH), reads the
interpreter its first line names, and runs the hook with that interpreter and ``-E``; the line's exit codes are kept
(0 and 2 pass through; any other ends in a refusal) [DEC-966 item 2, DEC-822]". Failure: "A template hook line that
runs a bare ``python3``, or one without ``-E``."

Each of the three guard lines of each template file is run through ``sh -c`` (as Claude Code runs a hook's command)
in a temporary project that holds, at ``governance/kernel/hooks/<program>``, a stand-in program: it records the
interpreter that started it (``sys.prefix``: the stand-in pin's environment, or ``/usr`` for the system's), whether
``-E`` is in force (``sys.flags.ignore_environment``), and ends as the case asks. The installed gov is the stand-in
pin built from this repository's code (``conftest.stand_in``); a decoy ``python3`` and ``python`` first on ``PATH``
leave a marker if they are ever started.
"""

from __future__ import annotations

import json

import pytest

import w2_106_support as support

LINES = pytest.mark.parametrize(("name", "event"), support.LINE_PARAMS, ids=support.LINE_IDS)


def _started_by_the_pin(box, pin, program, where):
    record = box.record(program)
    assert record is not None, f"{where}: the hook program never ran"
    assert record["prefix"] == str(pin.venv), (
        f"{where}: the program was started by the interpreter of {record['prefix']} ({record['executable']}), not by "
        f"the one the installed gov's first line names ({pin.venv}/bin/python)")
    assert pin.marks("pin-python-"), f"{where}: the stand-in pin's interpreter never started"
    return record


def _no_decoy(box, where):
    started = box.marks("path-python")
    assert not started, f"{where}: the line started the decoy first on PATH ({started}): a bare python3 or python"


@LINES
def test_the_line_starts_its_program_with_the_interpreter_the_home_gov_names_and_minus_e(name, event, box, pin):
    """``$HOME/.local/bin/gov`` is a link to the stand-in pin's ``bin/gov``; ``PATH`` holds the decoy and the
    system's folders, and no gov. The line starts the program with the interpreter that ``bin/gov``'s first line
    names, with ``-E`` in force, and never the decoy ``python3``."""
    line = support.template_line(name, event)
    where = f"{support.FILES[name]}, {event}"
    program = support.PROGRAM_OF[event]
    support.link_gov(pin.gov, box.home_gov)
    support.place_program(box, program)
    path = support.path_of(box.decoy_bin)
    support.assert_no_gov_on(path)
    done = support.run_line(line, box, path=path, event=event)
    _no_decoy(box, f"{where}\n{done.describe()}")
    record = _started_by_the_pin(box, pin, program, f"{where}\n{done.describe()}")
    assert record["ignore_environment"] == 1, (
        f"{where}: the program's interpreter runs without -E (sys.flags.ignore_environment is "
        f"{record['ignore_environment']}), so the session's PYTHON* variables reach it")
    assert done.returncode == 0, f"{where}: the program allowed (exit 0) and the line did not\n{done.describe()}"


@LINES
def test_without_the_home_gov_the_line_uses_the_gov_on_path(name, event, box, pin):
    """No ``$HOME/.local/bin/gov``; a ``gov`` on ``PATH`` (a link to the stand-in's ``bin/gov``) ahead of the decoy.
    The line starts the program with the interpreter that gov's first line names."""
    line = support.template_line(name, event)
    where = f"{support.FILES[name]}, {event}"
    program = support.PROGRAM_OF[event]
    support.link_gov(pin.gov, box.path_bin / "gov")
    support.place_program(box, program)
    done = support.run_line(line, box, path=support.path_of(box.path_bin, box.decoy_bin), event=event)
    _no_decoy(box, f"{where}\n{done.describe()}")
    _started_by_the_pin(box, pin, program, f"{where}\n{done.describe()}")
    assert done.returncode == 0, f"{where}: the program allowed (exit 0) and the line did not\n{done.describe()}"


@LINES
def test_the_home_gov_comes_before_the_gov_on_path(name, event, box, pin):
    """``$HOME/.local/bin/gov`` links to the stand-in; another ``gov`` is first on ``PATH``, whose first line names an
    interpreter of its own. The line takes the home one ("``$HOME/.local/bin/gov``, else ``gov`` on PATH"): the other
    interpreter never starts."""
    line = support.template_line(name, event)
    where = f"{support.FILES[name]}, {event}"
    program = support.PROGRAM_OF[event]
    support.link_gov(pin.gov, box.home_gov)
    support.other_gov(box)
    support.place_program(box, program)
    done = support.run_line(line, box, path=support.path_of(box.path_bin, box.decoy_bin), event=event)
    other = box.marks("other-python-")
    assert not other, (f"{where}: the line started the interpreter of the gov on PATH ({other}), though "
                       f"$HOME/.local/bin/gov is there\n{done.describe()}")
    _no_decoy(box, f"{where}\n{done.describe()}")
    _started_by_the_pin(box, pin, program, f"{where}\n{done.describe()}")


# (ending of the stand-in program, the line's exit, what reaches standard output, what reaches standard error)
EXITS = [
    ("exit-0-with-output", 0, "the program's output", None),
    ("exit-2-with-refusal", 2, None, "the program's refusal"),
    ("exit-1", 2, None, "a message naming the program"),
    ("killed", 2, None, "a message naming the program"),
]


@LINES
@pytest.mark.parametrize(("ending", "expected", "out", "err"), EXITS, ids=[case[0] for case in EXITS])
def test_the_line_keeps_its_exit_codes(name, event, ending, expected, out, err, box, pin):
    """0 and 2 pass through (with the program's output, a deny decision on standard output included, and its
    refusal on standard error); any other exit (1, or a crash: the program killed by a signal) ends in a refusal,
    exit 2, with a message naming the program (DEC-880 item 3, DEC-913 item 1). Claude Code blocks a PreToolUse call
    only on exit 2 or a deny decision with exit 0; any other non-zero exit lets the call through."""
    line = support.template_line(name, event)
    where = f"{support.FILES[name]}, {event}, the program ending with {ending}"
    program = support.PROGRAM_OF[event]
    support.link_gov(pin.gov, box.home_gov)
    support.place_program(box, program, ending)
    done = support.run_line(line, box, path=support.path_of(box.decoy_bin), event=event)
    assert box.record(program) is not None, f"{where}: the program never ran, so the case measured nothing\n" \
                                            f"{done.describe()}"
    assert done.returncode == expected, f"{where}: the line ended with exit {done.returncode}, not {expected}\n" \
                                        f"{done.describe()}"
    if out:
        assert done.stdout.strip() == json.dumps(support.DENY), (
            f"{where}: {out} did not pass through unchanged\n{done.describe()}")
    if err == "the program's refusal":
        assert "w2106 refused toolu_w2106_0001" in done.stderr, f"{where}: {err} did not pass through\n" \
                                                                 f"{done.describe()}"
    if err == "a message naming the program":
        assert program in done.stderr, f"{where}: exit 2 without {err} ({program})\n{done.describe()}"
