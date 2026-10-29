"""KPI 4 and failure KPI 2 (its commit-gate part): the commit gates run first, before any test.

KPI 4: "The commit gates run first, before any test: the trailers, work without a task, accepted history, the
probe gate (a stale probe named before the run, W2-M403), and the ratchet's own reading of both lists' entries (an
entry the ratchet would not count is named); when one refuses, the close stops at once, names its cause and spends
no ratchet attempt [DEC-868 item 3, DEC-896 item 3, P-IS-4 (a), I2 F13, I4 F14, F17]."

Failure KPI 2: "... a stale probe, an unmeasured commit, a ratchet entry the ratchet would not count ... refused only
after the regression."

Every case's project holds two telling tests: the ticket's acceptance test and a regression test
(``tests/unit/``). Each case holds four things of the refusal: the close is refused; it names its cause (the gate's
finding code, as today's gates name them); no telling test ran; and the ticket's iteration count is still 0, with
no escalation written (no ratchet attempt spent). Today these findings are gathered after both runs and counted
(DEC-492, DEC-455); DEC-868 item 3, a later decision, changes that (DEC-866).
"""

import pytest

import w2_07_support as support

TICKET, WBS = "PROJ-gate", "W9-gate"


def _assert_stopped_before_any_test(project, sandbox, interface, cause):
    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface)
    assert cause in support.codes_of(error) or support.names(error, cause), \
        f"the refusal does not name its cause ({cause})\n{run.describe()}"
    support.assert_no_test_ran(project, run)
    support.assert_no_attempt_spent(project, TICKET, run)
    support.base.assert_not_closed(project, TICKET)
    return error


def test_a_commit_without_its_trailers_stops_the_close_before_any_test(project, sandbox, interface):
    support.with_regression_mark(project)
    support.create_ticket(project, TICKET, WBS)
    support.work(project, TICKET, {"src/example/feature.py": "# feature\n"},
                 trailers=(f"Task: {TICKET}", "Role: engineer"))
    support.checkpointed(project, TICKET)
    _assert_stopped_before_any_test(project, sandbox, interface, "TRAILER_MISSING")


def test_work_without_a_task_stops_the_close_before_any_test(project, sandbox, interface):
    support.with_regression_mark(project)
    support.ready_ticket(project, TICKET, WBS)
    project.write("src/example/other.py", "# work no ticket measured\n")
    project.commit("work without a task", who=support.AGENT, trailers=(), exact=True)
    support.checkpointed(project, TICKET)
    _assert_stopped_before_any_test(project, sandbox, interface, "WORK_WITHOUT_TASK")


def test_a_refused_accepted_history_entry_stops_the_close_before_any_test(project, sandbox, interface):
    """The entry names a decision the register does not hold (DEC-734: refused, ``ACCEPTED_HISTORY_REFUSED``)."""
    support.with_regression_mark(project)
    done = support.ready_ticket(project, TICKET, WBS)
    project.set_path_map(**{support.ACCEPTED_KEY: [{"commit": done, "decision": "DEC-777"}]})
    _assert_stopped_before_any_test(project, sandbox, interface, "ACCEPTED_HISTORY_REFUSED")


def test_a_stale_probe_is_named_before_any_test_runs(project, sandbox, interface):
    """W2-M403: the FULL ticket's probe judged its first commit; a later commit of the ticket changes its paths, so
    the probe is stale (``PROBE_INVALID``). The close names it before the regression, not after it."""
    support.with_regression_mark(project)
    support.create_ticket(project, TICKET, WBS, profile="FULL")
    first = support.work(project, TICKET, {"src/example/feature.py": "# feature\n"})
    support.probe_recorded(project, TICKET, first)
    support.work(project, TICKET, {"src/example/more.py": "# more, after the probe\n"})
    support.checkpointed(project, TICKET)
    error = _assert_stopped_before_any_test(project, sandbox, interface, "PROBE_INVALID")
    assert support.names(error, "probe"), "the refusal does not say that the probe is what is stale"


@pytest.mark.parametrize("key, code", [("accepted_reds", "ACCEPTED_RED_REFUSED"),
                                       ("load_sensitive", "LOAD_SENSITIVE_REFUSED")])
def test_a_ratchet_entry_the_ratchet_would_not_count_stops_the_close_before_any_test(key, code, project, sandbox,
                                                                                     interface):
    """The entry's decision is ACCEPTED by the owner, but its text names neither the test's file nor its name (I2
    F11: the ratchet refuses such an entry, "it covers nothing")."""
    support.with_regression_mark(project)
    project.record_decision("DEC-601", support.OWNER_ACCEPTED, "A case of the fixture is accepted for a while.")
    entry = (support.red_entry if key == "accepted_reds" else support.quarantine_entry)(support.REGRESSION_MARK_ID,
                                                                                        "DEC-601")
    project.set_path_map(**{key: [entry]})
    support.ready_ticket(project, TICKET, WBS)
    error = _assert_stopped_before_any_test(project, sandbox, interface, code)
    assert support.names(error, support.REGRESSION_MARK), "the refusal does not name the entry it would not count"
