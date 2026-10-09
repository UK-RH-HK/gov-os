"""The test runs of a close are parallel, and the declared cases run alone afterwards (DEC-527, DEC-518,
DEC-372).

"`gov close`'s regression step and the regression script run suites in parallel (`pytest -n auto`). The
latency, real-model and live-session cases run alone afterwards, serially (DEC-372)."

Which cases cannot hold under load is declared in the tests, in the list the project owns
(``support.SERIAL_ONLY_REL``; README, round 11, settlement 18): one entry on a line, the beginning of a node
id. A case no entry names runs in parallel, whatever it is called. A case an entry names runs exactly once,
after the parallel run of its suite, in no worker; its failure is a finding like any other.

How a case sees the form. Every project here has small tests of its own that tell how they ran
(``support.telling_test``): each adds a line, at every run, to a file outside the project, with the worker
of the parallel runner it ran in (the runner sets ``PYTEST_XDIST_WORKER`` in a worker and nowhere else) and
the time. No case reads the product's command line.

The projects are those of the suite: the ticket's acceptance folder, another ticket's acceptance folder and
a unit test as regression tests, each committed by the role that may write it.
"""

import pytest

import w1_30_support as support

TICKET = "PROJ-para"
WBS = "W1-para"
OTHER_WBS = "W1-other"
ACCEPTANCE = f"tests/acceptance/{WBS}"
OTHER = f"tests/acceptance/{OTHER_WBS}"
UNIT = "tests/unit"

# The telling tests of a project, by the folder each is in. One of them is named as a case that cannot hold
# under load would be: a name declares nothing.
ACCEPTANCE_TESTS = ("test_first_acceptance", "test_second_acceptance")
REGRESSION_TESTS = {OTHER: ("test_other_suite", "test_latency_p95_live_session_serial_only"),
                    UNIT: ("test_unit_one", "test_unit_two")}


def _told(tmp_path):
    told = tmp_path / "told"
    told.mkdir()
    return told


def _file_of(folder, name):
    return f"{folder}/{name}.py"


def _build(project, told, declared=(), bodies=None, extra=None):
    """The project: the regression tests (the orchestrator's commit), then the ticket with its acceptance
    tests, the list of ``declared`` entries when there are any, and the engineer's work. ``bodies`` gives a
    test another body than a pass; ``extra`` are further files (``{path: text}``) among the regression tests."""
    bodies = bodies or {}
    for folder, names in REGRESSION_TESTS.items():
        for name in names:
            project.write(_file_of(folder, name), support.telling_test(name, told, bodies.get(name, "assert True")))
    for rel, text in (extra or {}).items():
        project.write(rel, text)
    if declared:
        project.write(support.SERIAL_ONLY_REL, "# cases that cannot hold under load\n"
                      + "".join(f"{entry}  # latency: planted\n" for entry in declared))
    project.commit("regression tests", who=support.ORCHESTRATOR)
    project.add_ticket(TICKET, WBS)
    for name in ACCEPTANCE_TESTS:
        project.write(_file_of(ACCEPTANCE, name), support.telling_test(name, told, bodies.get(name, "assert True")))
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    support.checkpointed(project, TICKET)


def _all_tests():
    return list(ACCEPTANCE_TESTS) + [name for names in REGRESSION_TESTS.values() for name in names]


def _closed(project, sandbox, interface, *extra_args, env=None):
    support.load_store(project, sandbox)
    run = project.gov(sandbox, support.COMMAND, TICKET, "--json", *extra_args, env=env)
    result = support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed", run.describe()
    return run, result


def test_the_acceptance_run_and_the_regression_run_are_parallel(project, sandbox, interface, tmp_path):
    """Nothing is declared: every case of the ticket's folder, of another ticket's folder and of the unit tests
    runs exactly once, in a worker of the parallel runner, also the one whose name sounds serial-only."""
    told = _told(tmp_path)
    _build(project, told)

    run, _ = _closed(project, sandbox, interface)

    ran = support.told_by(told)
    assert sorted(ran) == sorted(_all_tests()), f"not every test of the project ran: {sorted(ran)}\n{run.describe()}"
    not_parallel = {name: runs for name, runs in ran.items() if not support.ran_in_a_worker(runs)}
    assert not not_parallel, \
        f"these cases did not run exactly once in a worker of the parallel runner: {not_parallel}\n{run.describe()}"


DECLARED = {
    "an acceptance case of the ticket": (_file_of(ACCEPTANCE, "test_second_acceptance") + "::test_second_acceptance",
                                         "test_second_acceptance", ACCEPTANCE_TESTS),
    "a case of another suite": (_file_of(OTHER, "test_other_suite") + "::test_other_suite",
                                "test_other_suite", REGRESSION_TESTS[OTHER] + REGRESSION_TESTS[UNIT]),
    "a unit test file": (_file_of(UNIT, "test_unit_two"), "test_unit_two",
                         REGRESSION_TESTS[OTHER] + REGRESSION_TESTS[UNIT]),
}


@pytest.mark.parametrize("which", sorted(DECLARED))
def test_a_declared_case_runs_alone_after_the_parallel_run_and_exactly_once(which, project, sandbox, interface,
                                                                            tmp_path):
    entry, declared, its_run = DECLARED[which]
    told = _told(tmp_path)
    _build(project, told, declared=[entry])

    run, _ = _closed(project, sandbox, interface)

    ran = support.told_by(told)
    assert sorted(ran) == sorted(_all_tests()), f"not every test of the project ran: {sorted(ran)}\n{run.describe()}"
    assert support.ran_alone(ran[declared]), \
        f"the declared case did not run exactly once and in no worker: {ran[declared]}\n{run.describe()}"
    others = {name: runs for name, runs in ran.items() if name != declared}
    not_parallel = {name: runs for name, runs in others.items() if not support.ran_in_a_worker(runs)}
    assert not not_parallel, \
        f"cases no entry names did not run exactly once in a worker: {not_parallel}\n{run.describe()}"
    before = max(ran[name][0][1] for name in its_run if name != declared)
    assert ran[declared][0][1] >= before, \
        f"the declared case ran before the parallel run of its tests had ended\n{ran}\n{run.describe()}"


def test_an_entry_names_a_whole_file_or_every_parameter_set_of_a_function(project, sandbox, interface, tmp_path):
    """Two entries: a file with two functions, and ``file::function`` of a function with two parameter sets.
    All four cases run alone and once; a function of the same file that the second entry does not name, and
    whose name begins like the named one, runs in a worker."""
    told = _told(tmp_path)
    whole = f"{UNIT}/test_whole_file.py"
    sets = f"{OTHER}/test_sets.py"
    extra = {
        whole: support.telling_test("test_whole_a", told)
        + support.telling_test("test_whole_b", told).split("import pytest\n\n\n", 1)[1],
        sets: support.telling_test("test_sets", told, decorator="@pytest.mark.parametrize('given', ['one', 'two'])\n",
                                   arguments="given")
        + support.telling_test("test_sets_too", told).split("import pytest\n\n\n", 1)[1],
    }
    _build(project, told, declared=[whole, f"{sets}::test_sets"], extra=extra)

    run, _ = _closed(project, sandbox, interface)

    ran = support.told_by(told)
    alone = ("test_whole_a", "test_whole_b", "test_sets[one]", "test_sets[two]")
    assert set(alone) <= set(ran), f"a declared case did not run at all: {sorted(ran)}\n{run.describe()}"
    wrong = {name: ran[name] for name in alone if not support.ran_alone(ran[name])}
    assert not wrong, f"declared cases did not run exactly once and in no worker: {wrong}\n{run.describe()}"
    assert support.ran_in_a_worker(ran.get("test_sets_too", [])), \
        f"a function no entry names did not run once in a worker: {ran.get('test_sets_too')}\n{run.describe()}"


@pytest.mark.parametrize("which", ["a case of another suite", "an acceptance case of the ticket"])
def test_a_failing_declared_case_is_a_finding_like_any_other(which, project, sandbox, interface, tmp_path):
    entry, declared, _ = DECLARED[which]
    told = _told(tmp_path)
    _build(project, told, declared=[entry], bodies={declared: "assert False, 'planted failure'"})

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert declared in support.error_text(error), \
        f"the refusal does not name the failing declared case\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the refusal is counted {support.iteration_count(project.root, TICKET)} times\n{run.describe()}"
    ran = support.told_by(told)
    assert support.ran_alone(ran.get(declared, [])), \
        f"the failing declared case did not run exactly once and in no worker: {ran.get(declared)}\n{run.describe()}"


def test_a_failing_case_of_the_parallel_run_is_named_as_before(project, sandbox, interface, tmp_path):
    """The findings of today, in the parallel form: the failing case is named, the declared case still runs
    (both runs go to their end), and the refusal is counted once."""
    entry, declared, _ = DECLARED["a unit test file"]
    told = _told(tmp_path)
    _build(project, told, declared=[entry], bodies={"test_unit_one": "assert False, 'planted failure'"})

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "test_unit_one" in support.error_text(error), \
        f"the refusal does not name the failing case of the parallel run\n{run.describe()}"
    assert declared not in support.error_text(error), \
        f"the refusal names the declared case, which passed\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    assert support.iteration_count(project.root, TICKET) == 1
    ran = support.told_by(told)
    assert support.ran_in_a_worker(ran["test_unit_one"]), f"the failing case ran as {ran['test_unit_one']}"
    assert support.ran_alone(ran.get(declared, [])), \
        f"after a failing parallel run the declared case did not run once, alone: {ran.get(declared)}\n{run.describe()}"


def test_a_declared_case_over_the_time_limit_is_a_finding(project, sandbox, interface, tmp_path):
    """The time limit holds for the run of the declared cases as for any test run (DEC-454)."""
    entry, declared, _ = DECLARED["a unit test file"]
    told = _told(tmp_path)
    _build(project, told, declared=[entry], bodies={declared: "time.sleep(999)"})

    run = support.run_close(project, sandbox, TICKET, "--timeout", "20")

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "time limit" in support.error_text(error).lower(), \
        f"the refusal is not for the time limit\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    ran = support.told_by(told)
    assert support.ran_alone(ran.get(declared, [])), f"the declared case ran as {ran.get(declared)}\n{run.describe()}"
    parallel = {name: runs for name, runs in ran.items() if name != declared}
    assert all(support.ran_in_a_worker(runs) for runs in parallel.values()), \
        f"the other cases did not each run once in a worker: {parallel}\n{run.describe()}"


def test_the_close_record_and_the_output_say_which_cases_ran_in_which_form_and_how_long(project, sandbox, interface,
                                                                                         tmp_path):
    """One declared regression case; one regression case sleeps a second, so that a time read from a clock is
    told from a zero. The record and the result state the same runs: the ticket's acceptance tests in
    parallel, the regression tests in parallel, the declared case afterwards, each with its counts and its
    seconds; the declared entry is named; and the totals count every case once."""
    entry, declared, _ = DECLARED["a case of another suite"]
    told = _told(tmp_path)
    _build(project, told, declared=[entry], bodies={"test_unit_one": "time.sleep(1.0)"})

    run, result = _closed(project, sandbox, interface)

    front = support.the_close_record(project, TICKET)
    stated = support.runs_stated_by(front, "the close record")
    assert support.runs_stated_by(result, "the result") == stated, \
        f"the result and the close record state different test runs\n{front.get(support.TEST_RUNS_KEY)}\n{run.describe()}"

    acceptance = support.the_run(stated, support.ACCEPTANCE_RUN, support.PARALLEL)
    regression = support.the_run(stated, support.REGRESSION_RUN, support.PARALLEL)
    afterwards = support.the_run(stated, support.REGRESSION_RUN, support.SERIAL_AFTERWARDS)
    assert acceptance and regression and afterwards, f"a run is not stated: {stated}"
    assert len(stated) == 3, f"a run is stated that the project did not have: {stated}"
    assert acceptance["passed"] == len(ACCEPTANCE_TESTS), f"the acceptance run's counts: {acceptance}"
    assert regression["passed"] == 3, f"the parallel regression run's counts: {regression}"
    assert afterwards["passed"] == 1, f"the counts of the run of the declared cases: {afterwards}"
    assert afterwards.get("cases") == [entry], \
        f"the run of the declared cases does not name the entries it ran: {afterwards}"
    assert regression["seconds"] >= 1.0, f"the regression run slept a second and is stated as {regression['seconds']} s"
    for entry_run in stated:
        assert entry_run["failed"] == entry_run["errors"] == entry_run["skipped"] == 0, f"{entry_run}"
        assert "note" not in entry_run, f"a run in the form asked for carries a note: {entry_run}"
    total = front.get("tests_run")
    assert isinstance(total, dict) and total.get("passed") == len(_all_tests()), \
        f"the record's totals do not count every case once ({len(_all_tests())} cases): {total}"


def test_without_declared_cases_no_run_afterwards_is_stated(project, sandbox, interface, tmp_path):
    told = _told(tmp_path)
    _build(project, told)

    run, result = _closed(project, sandbox, interface)

    stated = support.runs_stated_by(support.the_close_record(project, TICKET), "the close record")
    assert sorted((entry["run"], entry["form"]) for entry in stated) == \
        [(support.ACCEPTANCE_RUN, support.PARALLEL), (support.REGRESSION_RUN, support.PARALLEL)], \
        f"with nothing declared the runs are the two parallel ones: {stated}\n{run.describe()}"


def test_without_the_parallel_runner_the_ticket_closes_serially_and_says_so(project, sandbox, interface, tmp_path):
    """A project whose interpreter has the test runner and not the parallel runner closes as today, serially:
    no finding, exit code 0. Every case runs exactly once in no worker (no source says in which order). The record and the result say that the runs were serial, with a note that names the parallel
    runner as the reason."""
    env = support.environment_without_parallel_runner(tmp_path / "bare", sandbox)
    if env is None:
        pytest.skip("on this machine the parallel runner is not in the per-user folder of installed packages: "
                    "the fixture cannot take it away")
    assert support.can_import("pytest", sandbox, env=env) and support.can_import("yaml", sandbox, env=env), \
        "the fixture is wrong: the environment without the parallel runner lost another package too"
    entry, declared, its_run = DECLARED["a case of another suite"]
    told = _told(tmp_path)
    _build(project, told, declared=[entry])

    run, result = _closed(project, sandbox, interface, env=env)

    ran = support.told_by(told)
    assert sorted(ran) == sorted(_all_tests()), f"not every test of the project ran: {sorted(ran)}\n{run.describe()}"
    wrong = {name: runs for name, runs in ran.items() if not support.ran_alone(runs)}
    assert not wrong, f"without the parallel runner these cases did not run exactly once, serially: {wrong}"

    front = support.the_close_record(project, TICKET)
    stated = support.runs_stated_by(front, "the close record")
    assert support.runs_stated_by(result, "the result") == stated
    assert support.the_run(stated, support.ACCEPTANCE_RUN, support.PARALLEL) is None and \
        support.the_run(stated, support.REGRESSION_RUN, support.PARALLEL) is None, \
        f"a run is stated as parallel although the parallel runner is not installed: {stated}"
    for which in (support.ACCEPTANCE_RUN, support.REGRESSION_RUN):
        serial = support.the_run(stated, which, support.SERIAL)
        assert serial, f"the {which} run is not stated as serial: {stated}"
        note = serial.get("note")
        assert isinstance(note, str) and "parallel" in note.lower(), \
            f"the serial {which} run carries no note that says why it was not parallel: {serial}"
    assert front["tests_run"]["passed"] == len(_all_tests()), f"the totals: {front['tests_run']}"
