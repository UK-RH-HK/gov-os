"""A close whose test run exceeds its time limit is a failed close like any other (KPI S2: "tracks iterations
per ticket ... a failure opens a dependent repair ticket"; DEC-455: every failed close is one iteration).

The project is green and clean but for one regression test, the orchestrator's, that sleeps far beyond the
limit the case gives (``--timeout 1``, suite settlement). Each case measures one thing a failed close does:
it is counted; it opens one repair ticket that depends on the ticket; the third one writes the escalation;
after it the next attempt is blocked.
"""

import w1_30_support as support

TICKET = "PROJ-slow"
WBS = "W1-slow"
LIMIT = ("--timeout", "1")


def _slow_project(project):
    project.write("tests/unit/test_slow.py", "import time\n\n\ndef test_slow():\n    time.sleep(999)\n")
    project.commit("a regression test that does not end in time", who=support.ORCHESTRATOR)
    support.build_ticket(project, TICKET, WBS)


def _timed_out(project, sandbox, interface):
    run = support.run_close(project, sandbox, TICKET, *LIMIT)
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "time" in support.error_text(error).lower(), \
        f"the fixture is wrong: the close was refused for something other than the time limit\n{run.describe()}"
    return run


def test_a_close_over_its_time_limit_is_counted(project, sandbox, interface):
    _slow_project(project)
    run = _timed_out(project, sandbox, interface)
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the close over its time limit is not counted as one iteration\n{run.describe()}"


def test_a_close_over_its_time_limit_opens_a_dependent_repair_ticket(project, sandbox, interface):
    _slow_project(project)
    run = _timed_out(project, sandbox, interface)
    repairs = support.other_tickets(project.root, TICKET)
    assert len(repairs) == 1, f"one repair ticket is expected, found {[p.name for p in repairs]}\n{run.describe()}"
    tree = support.tk(project, "dep", "tree", repairs[0].stem).splitlines()
    assert any(TICKET in line for line in tree[1:]), \
        f"by the ticket tool the repair ticket does not depend on {TICKET}: {tree}"


def test_the_third_close_over_its_time_limit_writes_the_escalation(project, sandbox, interface):
    _slow_project(project)
    for _ in range(3):
        _timed_out(project, sandbox, interface)
    escalation = project.root / ".gov-runtime" / "escalations" / f"{TICKET}.json"
    assert escalation.is_file(), "three closes over their time limit wrote no escalation"


def test_after_three_closes_over_their_time_limit_the_next_is_blocked(project, sandbox, interface):
    _slow_project(project)
    for _ in range(3):
        _timed_out(project, sandbox, interface)
    run = support.run_close(project, sandbox, TICKET, *LIMIT)
    support.refused(run, interface, support.EXIT_BLOCKED)
