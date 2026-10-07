"""The test runner the close needs (KPI S1; DEC-454: nothing is closed that was not measured).

``gov close`` runs the ticket's acceptance tests and the regression tests with pytest. Where the interpreter
that runs ``gov close`` finds no pytest, no test was run: the answer is ``TEST_RUNNER_ABSENT`` and nothing is
closed.

Every other case of the suite runs in a sandbox whose interpreter finds the installed packages of the
interpreter running the suite (``support.sandbox_env``; the session fixture ``built`` holds that it finds
pytest). This case takes pytest away and nothing else: ``support.interpreter_without_test_runner``.
"""

import w1_30_support as support

TICKET = "PROJ-norn"
WBS = "W1-norunner"


def test_without_a_test_runner_nothing_is_closed(project, sandbox, interface, tmp_path):
    support.build_ticket(project, TICKET, WBS)
    support.load_store(project, sandbox)
    python, env = support.interpreter_without_test_runner(tmp_path / "bare", sandbox)
    # The fixture: this interpreter finds what ``gov`` reads its files with, and no pytest.
    assert support.can_import("yaml", sandbox, python=python, env=env), \
        "the fixture is wrong: the interpreter without a test runner lost another package too"
    assert not support.can_import("pytest", sandbox, python=python, env=env), \
        "the fixture is wrong: the interpreter still finds pytest"

    run = project.gov(sandbox, support.COMMAND, TICKET, "--json", python=python, env=env)

    support.assert_error(run, interface, "TEST_RUNNER_ABSENT", exit_code=support.EXIT_GOV_ERROR)
    support.assert_not_closed(project, TICKET)
