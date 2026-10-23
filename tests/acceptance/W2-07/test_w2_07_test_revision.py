"""KPI 2: a test-revision ticket is judged on the acceptance tests its ticket file names [DEC-892 item 1, DEC-896
item 3].

KPI 2: "A test-revision ticket is judged on the acceptance tests its ticket file names in acceptance_tests.path
(another ticket's folder), not on a folder of its own." DEC-892 item 1: "No tests are written into a W2-63 folder
just to satisfy the close ... W2-63 stays merged, not closed, until the close reads a ticket's declared
``acceptance_tests.path``." This repository's test-revision tickets (W2-63, W2-70) are written so:
``class: test-revision``, ``acceptance_tests.path: tests/acceptance/W1-49/``.

The project: an earlier ticket with its acceptance folder ``tests/acceptance/W9-old/``; the revision ticket's test
designer revises a test in that folder. The revision ticket has no folder of its own. The close's acceptance run
is the run of the declared folder: the answer states it as the ``acceptance`` run (W1-30's ``test_runs``).
"""

import w2_07_support as support

OLD, OLD_WBS = "PROJ-oldt", "W9-old"
REVISION, REVISION_WBS = "PROJ-revs", "W9-rev"
DECLARED = f"tests/acceptance/{OLD_WBS}/"
REVISED_NAME = "test_w207_revised"
REVISED_REL = f"{DECLARED}{REVISED_NAME}.py"


def _revision_ticket(project, revised_text):
    support.create_ticket(project, OLD, OLD_WBS)
    support.work(project, OLD, {"src/example/old.py": "# old\n"})
    support.create_ticket(project, REVISION, REVISION_WBS, cls="test-revision",
                          allowed_paths=(f"{DECLARED}**",), tests=False,
                          acceptance={"path": DECLARED, "author": "independent-test-designer (MR-3); the revision "
                                                                  "is the deliverable"})
    support.work(project, REVISION, {REVISED_REL: revised_text}, role="independent-test-designer",
                 who=support.TEST_DESIGNER, message="revise the earlier ticket's test")
    support.checkpointed(project, REVISION)
    assert not (project.root / "tests" / "acceptance" / REVISION_WBS).exists(), \
        "the fixture is wrong: the revision ticket has a folder of its own"


def _acceptance_runs(holder):
    return [run for run in holder.get("test_runs") or [] if isinstance(run, dict) and run.get("run") == "acceptance"]


def test_a_test_revision_ticket_closes_on_the_tests_its_ticket_file_names(project, sandbox, interface):
    _revision_ticket(project, support.base.telling_test(REVISED_NAME, project.told))

    run = support.run_close(project, sandbox, REVISION)

    result = support.closed(run, interface)
    assert support.ticket_status(project.root, REVISION) == "closed"
    runs = _acceptance_runs(result)
    assert runs and sum(r.get("passed", 0) for r in runs) >= 2, \
        f"the acceptance run is not the run of the declared folder (its two tests)\n{run.describe()}"
    assert REVISED_NAME in project.ran(), f"the revised test did not run\n{run.describe()}"


def test_a_test_revision_ticket_whose_named_tests_fail_is_refused_on_its_acceptance_run(project, sandbox, interface):
    """The failing revised test refuses the close as the ticket's own acceptance test, not only as a red of the
    regression."""
    _revision_ticket(project, f"def {REVISED_NAME}():\n    assert False, 'the revision is wrong'\n")

    run = support.run_close(project, sandbox, REVISION)

    error = support.refused(run, interface)
    assert run.returncode == support.EXIT_CHECK_FAILED, f"a failing acceptance test is a finding (exit 3)\n{run.describe()}"
    assert support.names(error, REVISED_NAME), f"the refusal does not name the failing test\n{run.describe()}"
    runs = _acceptance_runs(error.get("details") or {})
    assert runs and sum(r.get("failed", 0) + r.get("errors", 0) for r in runs) >= 1, \
        f"the refusal states no acceptance run of the declared folder that failed\n{run.describe()}"
    support.base.assert_not_closed(project, REVISION)
