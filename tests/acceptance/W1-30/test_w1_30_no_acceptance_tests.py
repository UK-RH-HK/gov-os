"""A ticket without acceptance tests: the refusal is a finding about the ticket's work.

KPI S1: ``gov close`` "runs tests/acceptance/<ticket>/". The ticket's acceptance tests are part of its work:
its file names their folder and their author (``acceptance_tests``; MR-3, DEC-069), and they are written
before the implementation. DEC-455: "A close refused for a finding about the ticket's work ... is one
iteration and opens a repair ticket"; the refusals it leaves uncounted are those of the call or of the count
itself (the ticket unknown, the arguments invalid, the ticket already closed, the escalation in force, the
count file corrupt). A ticket that has no acceptance test is none of those: work on the ticket repairs it. So
it is refused with exit code 3 (DEC-470: a finding about the ticket's work), counted, and a dependent repair
ticket is opened.

The projects are complete but for the tests: the orchestrator's ticket file and checkpoint, the engineer's
commit with its trailers inside the ticket's paths. Every case holds first that the answer is about the
acceptance tests.
"""

import shutil

import pytest

import w1_30_support as support

TICKET = "PROJ-noat"
WBS = "W1-noat"


def _without_tests(project, folder):
    """``folder`` False: the ticket has no acceptance folder. True: the folder holds its README and no test."""
    project.add_ticket(TICKET, WBS)
    if not folder:
        shutil.rmtree(project.root / "tests" / "acceptance" / WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    tests = list((project.root / "tests" / "acceptance").glob(f"{WBS}/**/test_*.py"))
    assert not tests and (project.root / "tests" / "acceptance" / WBS).is_dir() is folder, "the fixture is wrong"


def _refused_for_the_tests(project, sandbox, interface):
    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "acceptance" in support.error_text(error).lower(), \
        f"the close was refused for something other than the missing acceptance tests\n{run.describe()}"
    return run


FORMS = pytest.mark.parametrize("folder", [False, True], ids=["no-folder", "folder-without-a-test"])


@FORMS
def test_a_ticket_without_acceptance_tests_is_refused_and_nothing_is_closed(folder, project, sandbox, interface):
    _without_tests(project, folder)
    _refused_for_the_tests(project, sandbox, interface)
    support.assert_not_closed(project, TICKET)


@FORMS
def test_a_refusal_for_no_acceptance_tests_is_counted(folder, project, sandbox, interface):
    _without_tests(project, folder)
    run = _refused_for_the_tests(project, sandbox, interface)
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the close refused for no acceptance tests is not counted as one iteration\n{run.describe()}"


@FORMS
def test_a_refusal_for_no_acceptance_tests_opens_a_dependent_repair_ticket(folder, project, sandbox, interface):
    _without_tests(project, folder)
    run = _refused_for_the_tests(project, sandbox, interface)
    support.assert_dependent_repair_ticket(project, TICKET, run)
