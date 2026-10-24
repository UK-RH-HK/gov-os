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

Revised for W2-07 (DEC-892 item 1, DEC-896 item 3): the close reads the folder a ticket's file declares in
``acceptance_tests.path``, not a folder derived from its WBS id. The ticket here is an implementation ticket
(judged on its acceptance tests, W2-07's KPI 1) that declares ``tests/acceptance/W1-noat-declared/``; that folder
holds no test, while ``tests/acceptance/W1-noat/`` holds a passing one, which is not the ticket's declared
acceptance test and does not stand in for it. The expectations are unchanged.
"""

import shutil

import pytest

import w1_30_support as support

TICKET = "PROJ-noat"
WBS = "W1-noat"
DECLARED = "tests/acceptance/W1-noat-declared/"


def _without_tests(project, folder):
    """``folder`` False: the ticket's declared acceptance folder does not exist. True: it holds its README and no
    test. In both, the folder named after the ticket's WBS id holds a passing test the ticket does not declare."""
    project.add_ticket(TICKET, WBS, acceptance=DECLARED)
    shutil.rmtree(project.root / "tests" / "acceptance" / WBS)
    project.write(f"tests/acceptance/{WBS}/test_noat_undeclared.py", "def test_noat_undeclared():\n    assert True\n")
    if folder:
        project.write(f"{DECLARED}README.md", "# The declared acceptance folder\n")
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    declared = project.root / DECLARED
    tests = list(declared.glob("**/test_*.py"))
    assert not tests and declared.is_dir() is folder, "the fixture is wrong"
    assert support.read_ticket_frontmatter(project.root, TICKET)["acceptance_tests"]["path"] == DECLARED, \
        "the fixture is wrong: the ticket does not declare its acceptance folder"


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
