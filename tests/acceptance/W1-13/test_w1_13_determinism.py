"""W1-13 -- KPI success 3: "Output is identical on repeated runs."

Settled by the sources: the output is what the command line prints (API-0002: the envelope under ``--json``, the
plain form without it) and its exit code. Nothing in the envelope may vary between two runs on the same commit:
no time, no duration, no order that depends on a set or on the file system.
"""

from __future__ import annotations

import random

import pytest

import w1_13_support as support


def _open(project):
    rows = support.edit(support.fresh_rows(), [4, 7, 20], gap_ticket="TST-g001")
    project.specification(rows, profile="FULL")


def _complete(project):
    project.specification(support.complete_rows("STANDARD", capability_types=("backend",)), profile="STANDARD",
                          capability_types=("backend",))


def _invalid(project):
    rows = support.edit(support.complete_rows(), [3, 12, 22], state="N/A_WITH_REASON", evidence=[], reason="")
    project.specification(rows)


CASES = [pytest.param(_open, id="open"), pytest.param(_complete, id="complete"), pytest.param(_invalid, id="invalid")]


@pytest.mark.parametrize("build", CASES)
@pytest.mark.parametrize("flags", [("--json",), ()], ids=["json", "plain"])
def test_three_runs_print_the_same_bytes_and_end_with_the_same_code(project, gov, build, flags):
    build(project)
    runs = [gov(support.COMMAND, support.ARG_SPECIFICATION, support.SPEC, *flags) for _ in range(3)]
    first = runs[0]
    assert first.stdout or first.stderr, f"the command printed nothing\n{first.describe()}"
    for run in runs[1:]:
        assert (run.stdout, run.stderr, run.returncode) == (first.stdout, first.stderr, first.returncode), \
            f"two runs on the same commit differ\n{first.describe()}\n--- and ---\n{run.describe()}"


def test_the_bare_command_is_the_same_on_repeated_runs(project, gov):
    """Several specifications: the order of what is read from the file system does not reach the output."""
    _open(project)
    project.specification(support.complete_rows(), spec_id=support.OTHER_SPEC, change=support.OTHER_CHANGE)
    project.specification(support.fresh_rows(), spec_id="SPEC-zq12", change="zq12-first-feature", profile="LITE")
    runs = [gov(support.COMMAND, "--json") for _ in range(3)]
    assert len({(run.stdout, run.stderr, run.returncode) for run in runs}) == 1, \
        "\n--- and ---\n".join(run.describe() for run in runs)


def test_open_rows_are_listed_in_row_order_whatever_the_order_in_the_file(project, gov, interface):
    """The table's own order (rows 1 to 26) is the order of the report."""
    rows = support.edit(support.fresh_rows(), [2, 9, 25], gap_ticket="TST-g001")
    random.Random(13).shuffle(rows)
    project.specification(rows)
    report = support.held(gov(*support.select()), interface)
    assert support.open_numbers(report) == sorted(support.row_keys())


def test_the_plain_form_names_the_open_cells(project, gov):
    """MR-1: "``gov readiness`` names the open cells", also for a reader who did not ask for JSON."""
    rows = support.edit(support.complete_rows(), 7, state="MISSING", evidence=[], gap_ticket="TST-g001")
    support.edit(rows, 20, state="BLOCKED", evidence=[], reason="waits on TST-g001", gap_ticket=None)
    project.specification(rows)
    run = gov(support.COMMAND, support.ARG_SPECIFICATION, support.SPEC)
    assert run.returncode == support.EXIT_OPEN, run.describe()
    printed = run.stdout + run.stderr
    keys = support.row_keys()
    for expected in (keys[7], keys[20], "TST-g001", support.UNLINKED):
        assert expected in printed, f"the plain output does not name {expected!r}\n{run.describe()}"
