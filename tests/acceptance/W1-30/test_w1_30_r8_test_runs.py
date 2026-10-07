"""The test runs of a close are the suite's own, and a close measures something (DEC-487).

"Options a caller's environment would add to the test runner are not passed on; a run of the ticket's
acceptance tests in which no test passed refuses, as a run that collects none does." And: "A time limit that
is not a positive number is refused as an invalid argument."

The caller's environment: the test runner reads options from a variable of its own
(``support.TEST_RUNNER_OPTIONS``). The cases set it in the environment of ``gov close`` only; the ticket's one
acceptance test fails, and the close is refused for that test as it is without the variable
(``test_close_refuses_when_acceptance_tests_fail``).

Nothing ran: the ticket's only acceptance test is marked to be skipped. It is refused as a ticket without
acceptance tests is (README, "Round 6"): a finding, exit code 3, counted.

The time limit: an argument that is no limit. DEC-490: "refused like any other invalid argument, before
anything runs." The other invalid argument of this command the suite holds is a disposition that is none of
the six names: an error in the envelope, exit code 1. The case runs it in the same project and holds the same
exit code for the time limit; the answer names the argument; the failing ticket is not counted and gets no
repair ticket, so nothing ran.
"""

import pytest

import w1_30_support as support

TICKET = "PROJ-runs"
WBS = "W1-runs"
FAILING_TEST = f"tests/acceptance/{WBS}/test_fail.py::test_fail"

CALLERS_OPTIONS = {
    "collect only": "--collect-only",
    "deselect the failing test": f"--deselect {FAILING_TEST}",
}


@pytest.mark.parametrize("options", sorted(CALLERS_OPTIONS))
def test_options_in_the_callers_environment_do_not_reach_the_test_runs(options, project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS, failing=True)
    support.load_store(project, sandbox)
    env = {**support.sandbox_env(sandbox), support.TEST_RUNNER_OPTIONS: CALLERS_OPTIONS[options]}

    run = project.gov(sandbox, support.COMMAND, TICKET, "--json", env=env)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "test_fail" in support.error_text(error), \
        f"the refusal does not name the failing acceptance test\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


def test_a_ticket_whose_only_acceptance_test_is_skipped_refuses(project, sandbox, interface):
    project.add_ticket(TICKET, WBS)
    project.write(f"tests/acceptance/{WBS}/test_skipped.py",
                  "import pytest\n\n\n@pytest.mark.skip(reason='not now')\ndef test_skipped():\n    assert False\n")
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    support.refused(run, interface, support.EXIT_CHECK_FAILED)
    support.assert_not_closed(project, TICKET)
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the close in which no acceptance test passed is not counted as one iteration\n{run.describe()}"


@pytest.mark.parametrize("limit", ["0", "-5"])
def test_a_time_limit_that_is_not_a_positive_number_is_refused_as_an_invalid_argument(
        limit, project, sandbox, interface):
    """The ticket's acceptance test fails, so a close that ran anything would count and open a repair ticket.
    The other invalid argument is the invented disposition of ``test_only_six_disposition_names_accepted``."""
    support.build_ticket(project, TICKET, WBS, failing=True)
    other = support.run_close(project, sandbox, TICKET, "--disposition", "invented_name")
    support.refused(other, interface, support.EXIT_GOV_ERROR)
    support.assert_nothing_counted(project, TICKET, other)

    run = support.run_close(project, sandbox, TICKET, f"--timeout={limit}")

    error = support.refused(run, interface, other.returncode)
    assert "timeout" in support.error_text(error).lower(), f"the answer does not name the argument\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    support.assert_nothing_counted(project, TICKET, run)
    support.assert_no_repair_ticket(project, run, TICKET)
