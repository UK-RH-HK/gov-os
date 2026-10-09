"""Round 13, piece 3: a refused close states each of its test runs (DEC-566).

DEC-566: "That a refused close prints the totals of its test runs and not each run is accepted as an item of
the follow-up after W1-41." DEC-555 has the orchestrator read "the ``test_runs`` of every close": a refused
close must give them too.

**Proposed (README, round 13, settlement 27).** The JSON of a refused close holds ``test_runs`` under
``error.details``: the same list of objects a passed close holds under ``result`` and in its close record
(settlement 19 and 22): for each run made, ``run``, ``form``, ``seconds``, the four counts, ``workers`` for a
parallel run and ``cases`` for the run afterwards of the declared cases. It is there whether or not a test
failed: a close refused only for a trailer or for the probe, with every test green, states its runs too.

Each project has one acceptance case that runs in parallel, one that the project declares serial-only, and one
unit test as the regression run. The twin of a project is the same project without the finding: it closes, and
what it states of its runs is what the refused one must state, the seconds apart.
"""

import pytest

import w1_30_support as support

TICKET = "PROJ-rfrn"
WBS = "W1-rfrn"
ACCEPTANCE = f"tests/acceptance/{WBS}"
DECLARED = f"{ACCEPTANCE}/test_apart.py::test_apart"
FINDINGS = ("a commit without Implements", "no probe record")


def _build(project, failing=False, finding=None):
    """The regression test (the orchestrator's), the ticket with its two acceptance cases, one of them
    declared serial-only, and the engineer's work. ``failing`` adds a failing acceptance case; ``finding`` is
    the one thing wrong beside the tests: the engineer's second commit lacks ``Implements:``, or the ticket is
    FULL and has no probe record. Without the finding the same second commit carries the trailer and the FULL
    ticket has its probe record."""
    project.write("tests/unit/test_unit_one.py", "def test_unit_one():\n    assert True\n")
    project.write(support.SERIAL_ONLY_REL, f"{DECLARED}  # latency: planted\n")
    project.commit("regression tests", who=support.ORCHESTRATOR)
    full = finding in (None, "no probe record")
    project.add_ticket(TICKET, WBS, profile="FULL" if full else "STANDARD")
    project.add_passing_test(WBS)
    project.add_passing_test(WBS, name="test_apart")
    if failing:
        project.add_failing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    project.write("src/example/more.py", "# more\n")
    lacking = finding == "a commit without Implements"
    project.commit("more", who=support.IMPLEMENTER,
                   trailers=(f"Task: {TICKET}", "Role: engineer") if lacking else support.trailers_of(TICKET))
    if full and finding is None:
        project.add_probe(TICKET)
        project.commit("the probe record", who=support.ORCHESTRATOR)
    support.checkpointed(project, TICKET)


def _runs_of_the_refusal(run, interface):
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    details = error.get("details") or {}
    return error, support.runs_stated_by(details, "the refusal's details")


def _without_seconds(runs):
    return [{key: value for key, value in run.items() if key != "seconds"} for run in runs]


def _assert_each_run(runs, failed):
    """The three runs of the project, each with its form, its workers or its cases, and its counts."""
    parallel = support.the_run(runs, support.ACCEPTANCE_RUN, support.PARALLEL)
    afterwards = support.the_run(runs, support.ACCEPTANCE_RUN, support.SERIAL_AFTERWARDS)
    regression = support.the_run(runs, support.REGRESSION_RUN, support.PARALLEL)
    assert parallel and afterwards and regression and len(runs) == 3, f"not the three runs of the project: {runs}"
    assert (parallel["passed"], parallel["failed"]) == (1, failed), f"the parallel acceptance run: {parallel}"
    assert parallel.get(support.WORKERS_FIELD) == support.SUITE_WORKERS, f"no number of workers: {parallel}"
    assert (afterwards["passed"], afterwards["failed"]) == (1, 0), f"the run afterwards: {afterwards}"
    assert afterwards.get("cases") == [DECLARED], f"the run afterwards does not name its cases: {afterwards}"
    assert (regression["passed"], regression["failed"]) == (1, 0), f"the regression run: {regression}"
    assert regression.get(support.WORKERS_FIELD) == support.SUITE_WORKERS, f"no number of workers: {regression}"


def test_a_close_refused_for_a_failing_test_states_each_run(project, sandbox, interface):
    _build(project, failing=True, finding="a commit without Implements")

    run = support.run_close(project, sandbox, TICKET)

    error, runs = _runs_of_the_refusal(run, interface)
    assert "test_fail" in support.error_text(error), f"the refusal does not name the failing case\n{run.describe()}"
    _assert_each_run(runs, failed=1)
    support.assert_not_closed(project, TICKET)


@pytest.mark.parametrize("finding", FINDINGS)
def test_a_close_refused_with_every_test_green_states_each_run_as_a_passed_close_does(finding, project, sandbox,
                                                                                      interface, tmp_path):
    """The only finding is a trailer's or the probe's. The twin without it closes; the refused close states
    the runs the twin states."""
    _build(project, finding=finding)
    twin = support.Project(tmp_path / "twin")
    _build(twin, finding=None if finding == "no probe record" else "none")

    run = support.run_close(project, sandbox, TICKET)
    twin_run = support.run_close(twin, sandbox, TICKET)

    passed = support.runs_stated_by(support.result_of(twin_run, interface), "the twin's result")
    _assert_each_run(passed, failed=0)
    error, runs = _runs_of_the_refusal(run, interface)
    assert "test_" not in " ".join(error["details"].get("findings", [])), \
        f"the fixture is wrong: a test is among the findings\n{run.describe()}"
    _assert_each_run(runs, failed=0)
    assert _without_seconds(runs) == _without_seconds(passed), \
        f"the refused close does not state its runs as the passed one does:\n{runs}\n{passed}"
    support.assert_not_closed(project, TICKET)
