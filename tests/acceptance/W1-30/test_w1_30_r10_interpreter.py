"""The test runs take no interpreter switches from the caller's environment (DEC-500, fourth behaviour;
finding 7).

"A variable that changes how Python runs the tests (for one, the switch that removes assertions) does not
reach them."

The switch: ``PYTHONOPTIMIZE``. An interpreter started with it set compiles ``assert`` statements away. The
test runner rewrites the assertions of the test files themselves, so those still fail; an ``assert`` in a
module a test imports is gone.

The ticket's one acceptance test calls a helper module in the ticket's own test folder, and the helper's
``assert`` is the only thing that fails. Each case first holds its fixture by running the test runner on the
ticket's folder itself: the test fails in the suite's environment and passes with the variable set. Then
``gov close`` runs with the variable in its environment only, and the ticket is refused as it is without it
(``test_close_refuses_when_acceptance_tests_fail``): a finding, exit code 3, the failing test named, counted
once.
"""

import subprocess
import sys

import pytest

import w1_30_support as support

TICKET = "PROJ-intp"
WBS = "W1-intp"
SWITCH = "PYTHONOPTIMIZE"
FOLDER = f"tests/acceptance/{WBS}"
TEST_NAME = "test_the_helper_holds"

HELPER = (
    "def must_be_one(value):\n"
    "    assert value == 1, 'planted failure in the helper'\n"
)
TEST = (
    "from w1_intp_helper import must_be_one\n\n\n"
    f"def {TEST_NAME}():\n"
    "    must_be_one(2)\n"
)


def _test_runner(project, env):
    """The exit code of the test runner on the ticket's folder, started in ``env``; it leaves nothing in the
    project."""
    done = subprocess.run([sys.executable, "-m", "pytest", FOLDER, "-q", "-p", "no:cacheprovider"],
                          cwd=str(project.root), env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert project.waiting_paths() == [], f"the fixture's own test run left {project.waiting_paths()}"
    return done.returncode


@pytest.mark.parametrize("level", ["1", "2"])
def test_the_switch_that_removes_assertions_does_not_reach_the_test_runs(level, project, sandbox, interface):
    project.add_ticket(TICKET, WBS)
    project.write(f"{FOLDER}/w1_intp_helper.py", HELPER)
    project.write(f"{FOLDER}/test_helper.py", TEST)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    support.checkpointed(project, TICKET)
    env = {**support.sandbox_env(sandbox), SWITCH: level}
    assert _test_runner(project, support.sandbox_env(sandbox)) == 1, \
        "the fixture is wrong: the acceptance test does not fail in the suite's environment"
    assert _test_runner(project, env) == 0, \
        f"the fixture is wrong: with {SWITCH}={level} the acceptance test still does not pass"
    support.load_store(project, sandbox)

    run = project.gov(sandbox, support.COMMAND, TICKET, "--json", env=env)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert TEST_NAME in support.error_text(error), \
        f"the refusal does not name the failing acceptance test\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the refusal is counted {support.iteration_count(project.root, TICKET)} times\n{run.describe()}"
