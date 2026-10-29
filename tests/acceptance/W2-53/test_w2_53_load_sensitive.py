"""KPI 7 and failure KPI 5: the named load-sensitive quarantine (DEC-757 item 2).

KPI 7 [DEC-757]: "A test the path map's ``load_sensitive`` lists, with an ACCEPTED owner decision naming it and a
reason, that fails in the close's run is run again alone; when it passes alone, the close does not refuse for it,
and reports the run and the re-run."

Failure KPI 5 [DEC-757]: "A listed test that fails alone too refuses the close. A test not on ``load_sensitive`` is
never re-run. An entry added without ``Role: owner`` is refused, naming it."

The forms (README): an entry's ``test`` is a node id, or ``file::function`` for every parameter set of that
function. "Alone" is its own process, one test id per process (its session holds that one test). The report is
``load_sensitive: [{test, decision, in_run, alone}]`` (``in_run`` and ``alone`` are ``passed`` or ``failed``), in
the result of a close and in the details of a refusal. A listed test that fails alone too has the finding
``LOAD_SENSITIVE_FAILED_ALONE``; an entry that does not count has ``LOAD_SENSITIVE_REFUSED``.

The stand-ins: the owner's first entries name W1-05's hook latency case and W1-02's decision latency case (DEC-757,
W1-05's own ticket). Each stand-in fails on its first run (the close's run, "under load") and passes on every later
one; it tells every run, its process and the size of its session, into a folder outside the project. A plain
passing test in ``tests/unit/`` sits beside them in the close's regression run. No timing, no load.
"""

import pytest

import w2_53_support as support

TICKET, WBS = "PROJ-load", "W1-load"
DECISION = "DEC-903"
HOOK_TEST, HOOK_FUNCTION = support.HOOK_TEST, support.HOOK_FUNCTION
DECISION_TEST, DECISION_FUNCTION = support.DECISION_TEST, support.DECISION_FUNCTION
PLAIN = "tests/unit/test_plain.py"


def _stand_ins(project, told, hook_body=support.FAILS_UNDER_LOAD, decision_params=None):
    project.write(support.W1_05_FILE, support.telling_file(told, {HOOK_FUNCTION: (hook_body, None)}))
    project.write(support.W1_02_FILE, support.telling_file(
        told, {DECISION_FUNCTION: ("pass" if decision_params is None else support.FAILS_UNDER_LOAD,
                                   decision_params)}))
    project.write(PLAIN, "def test_plain():\n    assert True\n")
    support.setup_commit(project, "the latency cases")


def _quarantined(project, *test_ids, role="owner"):
    project.record_decision(DECISION, support.OWNER_ACCEPTED, support.owner_text_naming(*test_ids))
    return support.add_entries(project, support.LOAD_SENSITIVE,
                               [support.quarantine_entry(test_id, DECISION) for test_id in test_ids], role=role)


def _ticket_done(project):
    support.create_ticket(project, TICKET, WBS)
    support.engineer_commit(project, TICKET, {"src/example/feature.py": "# feature\n"})
    support.checkpointed(project, TICKET)


def _reported(answer, test_id, alone):
    return [report for report in support.rerun_reports(answer)
            if report.get("test") == test_id and report.get("decision") == DECISION
            and report.get("in_run") == support.FAILED and report.get("alone") == alone]


def _ran_in_the_run_and_alone(told, node_name):
    runs = support.told_runs(told, node_name)
    assert runs and runs[0]["items"] > 1, f"the fixture is wrong: {node_name} did not run with others: {runs}"
    return support.re_run_alone(runs)


# --------------------------------------------------------------------------
# KPI 7: a listed test that fails in the run and passes alone does not refuse
# --------------------------------------------------------------------------

def test_a_listed_test_that_fails_in_the_run_and_passes_alone_does_not_refuse_and_is_reported(
        project, sandbox, interface, told):
    _stand_ins(project, told)
    _quarantined(project, HOOK_TEST, DECISION_TEST)
    _ticket_done(project)

    run = support.run_close(project, sandbox, TICKET)

    result = support.closed(run, interface)
    assert _ran_in_the_run_and_alone(told, HOOK_FUNCTION), \
        f"{HOOK_TEST} was not run again alone: {support.told_runs(told, HOOK_FUNCTION)}"
    assert _reported(result, HOOK_TEST, support.PASSED), \
        f"the close does not report the run and the re-run of {HOOK_TEST}\n{run.describe()}"
    assert len(support.told_runs(told, DECISION_FUNCTION)) == 1, \
        f"{DECISION_TEST}, listed and passing in the run, was run again"


def test_a_function_entry_covers_every_parameter_set_of_the_function(project, sandbox, interface, told):
    _stand_ins(project, told, hook_body="pass", decision_params=("hook", "decision"))
    _quarantined(project, DECISION_TEST)
    _ticket_done(project)

    run = support.run_close(project, sandbox, TICKET)

    result = support.closed(run, interface)
    for case in ("hook", "decision"):
        node = f"{DECISION_FUNCTION}[{case}]"
        assert _ran_in_the_run_and_alone(told, node), f"{node} was not run again alone: {support.told_runs(told, node)}"
        reports = [report for report in support.rerun_reports(result)
                   if report.get("test") == f"{DECISION_TEST}[{case}]" and report.get("alone") == support.PASSED]
        assert reports, f"the close does not report the re-run of {DECISION_TEST}[{case}]\n{run.describe()}"


# --------------------------------------------------------------------------
# Failure KPI 5
# --------------------------------------------------------------------------

def test_a_listed_test_that_fails_alone_too_refuses_the_close(project, sandbox, interface, told):
    _stand_ins(project, told, hook_body=support.FAILS_ALONE_TOO)
    _quarantined(project, HOOK_TEST)
    _ticket_done(project)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    assert _ran_in_the_run_and_alone(told, HOOK_FUNCTION), \
        f"{HOOK_TEST} was not run again alone: {support.told_runs(told, HOOK_FUNCTION)}"
    assert support.naming(support.findings_coded(error, support.LOAD_SENSITIVE_FAILED_ALONE), HOOK_FUNCTION), \
        f"no {support.LOAD_SENSITIVE_FAILED_ALONE} finding names {HOOK_TEST}\n{run.describe()}"
    assert _reported(error, HOOK_TEST, support.FAILED), f"the refusal does not report the re-run\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


LISTS = ("on neither list", "on accepted_reds only")


@pytest.mark.parametrize("listed", LISTS)
def test_a_test_not_on_load_sensitive_is_never_run_again(listed, project, sandbox, interface, told):
    """Its red is judged as any red: it refuses; on ``accepted_reds`` it is a covered red (KPI 5)."""
    _stand_ins(project, told)
    if listed == LISTS[1]:
        project.record_decision(DECISION, support.OWNER_ACCEPTED, support.owner_text_naming(HOOK_TEST))
        support.add_entries(project, support.ACCEPTED_REDS, [support.red_entry(HOOK_TEST, DECISION)])
    _ticket_done(project)

    run = support.run_close(project, sandbox, TICKET)

    if listed == LISTS[0]:
        error = support.refused(run, interface)
        assert HOOK_FUNCTION in support.text_of(error), f"the refusal does not name {HOOK_TEST}\n{run.describe()}"
        support.base.assert_not_closed(project, TICKET)
    else:
        result = support.closed(run, interface)
        assert [report for report in support.red_reports(result)
                if report.get("test") == HOOK_TEST and report.get("result") == support.RESULT_FAILED], \
            f"the close does not report {HOOK_TEST} as a listed red\n{run.describe()}"
    assert len(support.told_runs(told, HOOK_FUNCTION)) == 1, \
        f"{HOOK_TEST}, not on {support.LOAD_SENSITIVE}, was run again: {support.told_runs(told, HOOK_FUNCTION)}"


def test_an_entry_the_owner_did_not_add_is_refused_naming_it_and_its_test_is_not_run_again(
        project, sandbox, interface, told):
    """Revised for W2-07 (DEC-868 item 3): the ratchet's reading of ``load_sensitive`` is a commit gate. An
    entry that does not count refuses the close at once, naming it, before any test: its test is not run at
    all, let alone again, and the refusal spends no attempt."""
    _stand_ins(project, told)
    added = _quarantined(project, HOOK_TEST, role="orchestrator")
    _ticket_done(project)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    found = support.naming(support.findings_coded(error, support.LOAD_SENSITIVE_REFUSED), HOOK_FUNCTION, added[:7])
    assert found, f"no {support.LOAD_SENSITIVE_REFUSED} finding names the entry {HOOK_TEST} and its commit\n" \
                  f"{run.describe()}"
    assert len(support.told_runs(told, HOOK_FUNCTION)) == 0, \
        f"{HOOK_TEST} ran although a commit gate refused first: {support.told_runs(told, HOOK_FUNCTION)}"
    assert support.base.iteration_count(project.root, TICKET) == 0, \
        f"the refusal of a commit gate was counted\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)
