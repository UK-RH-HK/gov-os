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

The time limit: an argument that is no limit. Exit code 2 is API-0002's usage error, 1 its governance error;
the case accepts both and holds that the answer names the argument, nothing is closed and nothing counted.
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
    support.build_ticket(project, TICKET, WBS)

    run = support.run_close(project, sandbox, TICKET, f"--timeout={limit}")

    assert run.returncode in (support.EXIT_GOV_ERROR, 2), \
        f"a time limit of {limit} is an invalid argument (exit code 2, or 1 with an error)\n{run.describe()}"
    assert '"ok": true' not in run.stdout.replace('"ok":true', '"ok": true'), run.describe()
    assert "timeout" in (run.stdout + run.stderr).lower(), \
        f"the answer does not name the argument\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    support.assert_nothing_counted(project, TICKET, run)
    support.assert_no_repair_ticket(project, run, TICKET)
