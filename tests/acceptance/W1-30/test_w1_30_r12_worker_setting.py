"""The number of parallel workers of a close is a setting of the project (DEC-549, P-2), and the time limit a
project writes in the same place is the one a close without ``--timeout`` uses (DEC-549, P-3; DEC-487).

"The number of parallel workers of a `gov close` is a setting of the project, default `auto`; the temporary
projects of the suites set it small, so that a close under test does not start ten workers inside a parallel
run. The setting changes how many workers run, never which tests run."

Where a project writes it (README, round 12, settlement 21): two optional top-level keys of
``governance/project/path-map.yaml``, the one project file every command is handed (DEC-185) and where the
one other pair of settings read by a command is written (DEC-479):

    close_workers: 4        a positive whole number, or auto
    close_timeout: 7200     a positive number of seconds

How a case sees how many workers there were: every test of the case's project tells in which worker of the
parallel runner it ran (``support.telling_test``, as in round 11). Each run of a project here has twelve
tests in twelve files, so the runner gives tests to every worker it starts; the workers that ran are the
distinct names told. No case reads the product's command line.
"""

import pytest

import w1_30_support as support

TICKET = "PROJ-work"
WBS = "W1-work"
ACCEPTANCE = f"tests/acceptance/{WBS}"
UNIT = "tests/unit"

ACCEPTANCE_TESTS = tuple(f"test_a{number:02d}" for number in range(12))
UNIT_TESTS = tuple(f"test_u{number:02d}" for number in range(12))
ALL_TESTS = ACCEPTANCE_TESTS + UNIT_TESTS
DECLARED = "test_u11"
DECLARED_ENTRY = f"{UNIT}/{DECLARED}.py"
FAILING = "test_u03"
PLANTED = "assert False, 'planted failure'"


@pytest.fixture()
def project_with(built, tmp_path):
    """``project_with(settings, name)``: a temporary project whose path map holds ``settings`` as it would
    write them (``support.path_map_text``); ``None`` is a project without a path map."""
    def make(settings, name="project"):
        return support.Project(tmp_path / name, settings=settings)
    return make


def _told(tmp_path, name="told"):
    told = tmp_path / name
    told.mkdir()
    return told


def _build(project, told, declared=False, bodies=None):
    """Twelve unit tests as regression tests (the orchestrator's commit, with the list when ``declared``),
    then the ticket with twelve acceptance tests and the engineer's work. Every test tells how it ran."""
    bodies = bodies or {}
    for name in UNIT_TESTS:
        project.write(f"{UNIT}/{name}.py", support.telling_test(name, told, bodies.get(name, "assert True")))
    if declared:
        project.write(support.SERIAL_ONLY_REL, f"{DECLARED_ENTRY}  # latency: planted\n")
    project.commit("regression tests", who=support.ORCHESTRATOR)
    project.add_ticket(TICKET, WBS)
    for name in ACCEPTANCE_TESTS:
        project.write(f"{ACCEPTANCE}/{name}.py", support.telling_test(name, told, bodies.get(name, "assert True")))
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    support.checkpointed(project, TICKET)


def _closed(project, sandbox, interface, *extra_args, env=None):
    support.load_store(project, sandbox)
    run = project.gov(sandbox, support.COMMAND, TICKET, "--json", *extra_args, env=env)
    result = support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed", run.describe()
    return run, result


def _nothing_ran(project, told, run):
    """The refusal came before anything ran: no test of the project told anything, and the ticket, whose
    acceptance test fails, is neither counted nor given a repair ticket."""
    assert not support.told_by(told), f"tests ran although the close was refused: {sorted(support.told_by(told))}"
    support.assert_not_closed(project, TICKET)
    support.assert_nothing_counted(project, TICKET, run)
    support.assert_no_repair_ticket(project, run, TICKET)


# --------------------------------------------------------------------------
# The number a project writes is the number of workers
# --------------------------------------------------------------------------

@pytest.mark.parametrize("number", [1, 3])
def test_the_number_a_project_writes_is_the_number_of_workers_of_each_parallel_run(number, project_with, sandbox,
                                                                                   interface, tmp_path):
    """``close_workers: <number>`` in the project's path map: the acceptance run and the regression run each
    have that many workers, and every case still runs exactly once, in a worker."""
    project = project_with({support.WORKERS_KEY: number})
    told = _told(tmp_path)
    _build(project, told)

    run, _ = _closed(project, sandbox, interface)

    ran = support.told_by(told)
    assert sorted(ran) == sorted(ALL_TESTS), f"not every test of the project ran: {sorted(ran)}\n{run.describe()}"
    not_parallel = {name: runs for name, runs in ran.items() if not support.ran_in_a_worker(runs)}
    assert not not_parallel, f"these cases did not run exactly once in a worker: {not_parallel}\n{run.describe()}"
    for which, names in (("acceptance", ACCEPTANCE_TESTS), ("regression", UNIT_TESTS)):
        workers = support.workers_that_ran(ran, names)
        assert workers == support.workers_named(number), \
            f"the project sets {number} workers and the {which} run had {len(workers)}: {workers}\n{run.describe()}"


# --------------------------------------------------------------------------
# The setting changes how many workers run, never which tests run
# --------------------------------------------------------------------------

SETTINGS = {"one worker": {support.WORKERS_KEY: 1}, "three workers": {support.WORKERS_KEY: 3}, "no setting": None}


def _what_ran(ran):
    """What a close ran, without how: each test with the number of times it ran, and whether in a worker."""
    return {name: (len(runs), [worker != support.NO_WORKER for worker, _ in runs]) for name, runs in ran.items()}


def _without_how(runs):
    """The stated runs without their seconds and their number of workers."""
    return [{key: value for key, value in run.items() if key not in ("seconds", support.WORKERS_FIELD)}
            for run in runs]


def test_the_setting_never_changes_which_tests_run(project_with, sandbox, interface, tmp_path):
    """Three projects with the same tests and one declared case: one worker, three workers, no setting. In
    each, every case runs exactly once, the declared case alone and after the parallel run of its tests, and
    the close record states the same runs with the same counts."""
    seen = {}
    for which, settings in SETTINGS.items():
        name = which.replace(" ", "-")
        project = project_with(settings, name)
        told = _told(tmp_path, f"told-{name}")
        _build(project, told, declared=True)

        run, _ = _closed(project, sandbox, interface)

        ran = support.told_by(told)
        assert sorted(ran) == sorted(ALL_TESTS), f"{which}: not every test ran: {sorted(ran)}\n{run.describe()}"
        assert support.ran_alone(ran[DECLARED]), \
            f"{which}: the declared case did not run exactly once and in no worker: {ran[DECLARED]}\n{run.describe()}"
        others = {name: runs for name, runs in ran.items() if name != DECLARED}
        not_parallel = {name: runs for name, runs in others.items() if not support.ran_in_a_worker(runs)}
        assert not not_parallel, f"{which}: cases no entry names did not run once in a worker: {not_parallel}"
        last = max(ran[name][0][1] for name in UNIT_TESTS if name != DECLARED)
        assert ran[DECLARED][0][1] >= last, f"{which}: the declared case ran before the parallel run had ended\n{ran}"
        front = support.the_close_record(project, TICKET)
        seen[which] = (_what_ran(ran), front["tests_run"],
                       _without_how(support.runs_stated_by(front, f"the close record ({which})")))

    first = seen["no setting"]
    assert first[1]["passed"] == len(ALL_TESTS), f"the totals do not count every case once: {first[1]}"
    for which, stated in seen.items():
        assert stated == first, \
            f"with {which} the close ran or counted other than without a setting:\n{stated}\n{first}"


def test_the_setting_never_changes_the_findings(project_with, sandbox, interface, tmp_path):
    """The same three projects with one failing case in the parallel run: each close is refused for that case,
    with the same findings, counted once; the declared case still ran alone."""
    seen = {}
    for which, settings in SETTINGS.items():
        name = which.replace(" ", "-")
        project = project_with(settings, name)
        told = _told(tmp_path, f"told-{name}")
        _build(project, told, declared=True, bodies={FAILING: PLANTED})

        run = support.run_close(project, sandbox, TICKET)

        error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
        assert FAILING in support.error_text(error), f"{which}: the failing case is not named\n{run.describe()}"
        assert support.iteration_count(project.root, TICKET) == 1, f"{which}: counted other than once"
        ran = support.told_by(told)
        assert support.ran_alone(ran.get(DECLARED, [])), f"{which}: the declared case ran as {ran.get(DECLARED)}"
        seen[which] = (_what_ran(ran), error["details"]["findings"], error["details"].get("tests_run"))

    for which, found in seen.items():
        assert found == seen["no setting"], \
            f"with {which} the refusal differs from the one without a setting:\n{found}\n{seen['no setting']}"


# --------------------------------------------------------------------------
# The close record and the result state the number of workers
# --------------------------------------------------------------------------

STATED = {
    "a number": ({support.WORKERS_KEY: 3}, 3),
    "auto, written": ({support.WORKERS_KEY: support.AUTO}, support.AUTO),
    "a path map without the setting": ({}, support.AUTO),
    "no path map": (None, support.AUTO),
}


@pytest.mark.parametrize("which", sorted(STATED))
def test_each_parallel_run_states_its_number_of_workers(which, project_with, sandbox, interface, tmp_path):
    """Settlement 22: every run of the form ``parallel`` carries ``workers``, in the close record and in the
    result alike: the whole number the project wrote, or the word ``auto`` where it wrote that or nothing.
    The run of the declared cases afterwards had no worker and carries no ``workers``."""
    settings, expected = STATED[which]
    project = project_with(settings)
    told = _told(tmp_path)
    _build(project, told, declared=True)

    run, result = _closed(project, sandbox, interface)

    stated = support.runs_stated_by(support.the_close_record(project, TICKET), "the close record")
    assert support.runs_stated_by(result, "the result") == stated, \
        f"the result and the close record state different test runs\n{stated}\n{run.describe()}"
    for which_run in (support.ACCEPTANCE_RUN, support.REGRESSION_RUN):
        parallel = support.the_run(stated, which_run, support.PARALLEL)
        assert parallel, f"the {which_run} run is not stated as parallel: {stated}"
        assert support.WORKERS_FIELD in parallel, \
            f"the parallel {which_run} run does not state its number of workers under " \
            f"{support.WORKERS_FIELD!r}: {parallel}"
        workers = parallel[support.WORKERS_FIELD]
        assert workers == expected and type(workers) is type(expected), \
            f"the parallel {which_run} run states {workers!r} workers, the project's setting is {expected!r}"
    afterwards = support.the_run(stated, support.REGRESSION_RUN, support.SERIAL_AFTERWARDS)
    assert afterwards and support.WORKERS_FIELD not in afterwards, \
        f"the run of the declared cases, which had no worker, states a number of workers: {afterwards}"
    ran = support.told_by(told)
    assert sorted(ran) == sorted(ALL_TESTS), f"not every test of the project ran: {sorted(ran)}"


# --------------------------------------------------------------------------
# A value that is no number of workers refuses the close
# --------------------------------------------------------------------------

# What a project may write by mistake, and how the YAML reader gives it to the command.
NO_NUMBER_OF_WORKERS = {"zero": ("0", "0"), "a negative number": ("-2", "-2"), "a fraction": ("1.5", "1.5"),
                        "a word": ("many", "many"), "a truth value": ("true", "True")}


def _refused_for_the_setting(run, interface, code, key, read):
    """The refusal of a setting that is none, in the form of the time limit's (DEC-487): not a finding (exit
    code 1); the message names the setting's key; the details name it under ``argument`` and give what was
    read."""
    error = support.refused_without_a_finding(run, interface)
    assert error["code"] == code, f"the refusal's code is {error['code']!r}, not {code!r}\n{run.describe()}"
    assert key in error["message"], f"the message does not name the setting {key!r}\n{run.describe()}"
    details = error.get("details") or {}
    assert details.get(support.REFUSED_KEY) == key, \
        f"the details do not name the setting under {support.REFUSED_KEY!r}: {details}"
    assert read in [str(value) for value in details.values()], \
        f"the details do not give the value read ({read!r}): {details}"
    return error


@pytest.mark.parametrize("which", sorted(NO_NUMBER_OF_WORKERS))
def test_a_setting_that_is_no_number_of_workers_refuses_the_close_before_anything_runs(which, project_with, sandbox,
                                                                                       interface, tmp_path):
    """The ticket's acceptance tests fail, so a close that ran anything (in any number of workers, or serially)
    would count the refusal and open a repair ticket. Nothing falls back to ``auto`` or to a serial run."""
    written, read = NO_NUMBER_OF_WORKERS[which]
    project = project_with({support.WORKERS_KEY: written})
    told = _told(tmp_path)
    _build(project, told, bodies={name: PLANTED for name in ACCEPTANCE_TESTS})

    run = support.run_close(project, sandbox, TICKET)

    _refused_for_the_setting(run, interface, support.INVALID_WORKERS, support.WORKERS_KEY, read)
    _nothing_ran(project, told, run)


# --------------------------------------------------------------------------
# Without the parallel runner
# --------------------------------------------------------------------------

def _without_the_parallel_runner(tmp_path, sandbox):
    env = support.environment_without_parallel_runner(tmp_path / "bare", sandbox)
    if env is None:
        pytest.skip("on this machine the parallel runner is not in the per-user folder of installed packages: "
                    "the fixture cannot take it away")
    return env


def test_without_the_parallel_runner_a_number_of_workers_is_accepted_and_changes_nothing(project_with, sandbox,
                                                                                         interface, tmp_path):
    """Round 11 holds that such a project closes serially and says so. The setting is still read: a valid one
    closes the same way, every case once in no worker, each run ``serial`` with its note and no ``workers``."""
    env = _without_the_parallel_runner(tmp_path, sandbox)
    project = project_with({support.WORKERS_KEY: 3})
    told = _told(tmp_path)
    _build(project, told, declared=True)

    run, result = _closed(project, sandbox, interface, env=env)

    ran = support.told_by(told)
    assert sorted(ran) == sorted(ALL_TESTS), f"not every test of the project ran: {sorted(ran)}\n{run.describe()}"
    wrong = {name: runs for name, runs in ran.items() if not support.ran_alone(runs)}
    assert not wrong, f"without the parallel runner these cases did not run exactly once, serially: {wrong}"
    stated = support.runs_stated_by(support.the_close_record(project, TICKET), "the close record")
    assert support.runs_stated_by(result, "the result") == stated
    assert sorted((entry["run"], entry["form"]) for entry in stated) == \
        [(support.ACCEPTANCE_RUN, support.SERIAL), (support.REGRESSION_RUN, support.SERIAL)], \
        f"without the parallel runner the runs are the two serial ones: {stated}"
    for entry in stated:
        assert support.WORKERS_FIELD not in entry, f"a serial run states a number of workers: {entry}"
        assert "parallel" in str(entry.get("note", "")).lower(), f"a serial run carries no note that says why: {entry}"


def test_without_the_parallel_runner_a_setting_that_is_no_number_refuses_all_the_same(project_with, sandbox,
                                                                                     interface, tmp_path):
    """What a project wrote wrongly is refused wherever it is closed, not only where the runner is installed."""
    env = _without_the_parallel_runner(tmp_path, sandbox)
    project = project_with({support.WORKERS_KEY: 0})
    told = _told(tmp_path)
    _build(project, told, bodies={name: PLANTED for name in ACCEPTANCE_TESTS})
    support.load_store(project, sandbox)

    run = project.gov(sandbox, support.COMMAND, TICKET, "--json", env=env)

    _refused_for_the_setting(run, interface, support.INVALID_WORKERS, support.WORKERS_KEY, "0")
    _nothing_ran(project, told, run)


# --------------------------------------------------------------------------
# The time limit a project writes in the same place
# --------------------------------------------------------------------------

SLOW = "import time\n\n\ndef test_slow():\n    time.sleep({seconds})\n"


def _with_a_slow_regression_test(project, seconds):
    project.write(f"{UNIT}/test_slow.py", SLOW.format(seconds=seconds))
    project.commit("a regression test that takes its time", who=support.ORCHESTRATOR)
    support.build_ticket(project, TICKET, WBS)


def test_the_time_limit_a_project_writes_is_the_limit_of_a_close_without_the_argument(project_with, sandbox,
                                                                                      interface):
    """``close_timeout: 3`` in the project's path map and a regression test that sleeps far longer: the close
    without ``--timeout`` is refused for the time limit, a finding counted once, well inside the 30 s the suite
    waits for a command (the default limit is 120 s)."""
    project = project_with({support.WORKERS_KEY: support.SUITE_WORKERS, support.TIME_LIMIT_KEY: 3})
    _with_a_slow_regression_test(project, 999)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "time limit" in support.error_text(error).lower(), f"the refusal is not for the time limit\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the close over the project's time limit is not counted once\n{run.describe()}"


def test_the_argument_wins_over_the_time_limit_a_project_writes(project_with, sandbox, interface):
    """``close_timeout: 1`` in the project and a regression test that sleeps two seconds: with ``--timeout 60``
    the ticket closes."""
    project = project_with({support.WORKERS_KEY: support.SUITE_WORKERS, support.TIME_LIMIT_KEY: 1})
    _with_a_slow_regression_test(project, 2)

    run = support.run_close(project, sandbox, TICKET, "--timeout", "60")

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed", run.describe()


NO_TIME_LIMIT = {"zero": ("0", "0"), "a negative number": ("-5", "-5"), "a word": ("soon", "soon")}


@pytest.mark.parametrize("which", sorted(NO_TIME_LIMIT))
def test_a_time_limit_of_the_project_that_is_no_positive_number_is_refused_and_names_the_setting(
        which, project_with, sandbox, interface, tmp_path):
    """As ``--timeout`` is refused (``test_w1_30_r8_test_runs.py``), with the setting's key where that names
    the argument: ``INVALID_TIMEOUT``, exit code 1, nothing ran, nothing counted."""
    written, read = NO_TIME_LIMIT[which]
    project = project_with({support.WORKERS_KEY: support.SUITE_WORKERS, support.TIME_LIMIT_KEY: written})
    told = _told(tmp_path)
    _build(project, told, bodies={name: PLANTED for name in ACCEPTANCE_TESTS})

    run = support.run_close(project, sandbox, TICKET)

    _refused_for_the_setting(run, interface, support.INVALID_TIMEOUT, support.TIME_LIMIT_KEY, read)
    _nothing_ran(project, told, run)


# --------------------------------------------------------------------------
# A list entry that names no case (DEC-549, P-4: as built)
# --------------------------------------------------------------------------

NAMES_NO_CASE = {
    "a file that does not exist": f"{UNIT}/test_gone.py",
    "a function that does not exist": f"{UNIT}/test_u00.py::test_gone",
}


@pytest.mark.parametrize("which", sorted(NAMES_NO_CASE))
def test_a_list_entry_that_names_no_case_refuses_the_close_with_a_finding(which, project_with, sandbox, interface,
                                                                         tmp_path):
    """Every test of the project passes; the list names a case that is not there. The run afterwards of the
    declared cases fails, and the close is refused with a finding that names the entry's case: exit code 3,
    counted once, nothing closed. The parallel runs before it ran every case once."""
    entry = NAMES_NO_CASE[which]
    project = project_with(support.SUITE_SETTINGS)
    told = _told(tmp_path)
    for name in UNIT_TESTS:
        project.write(f"{UNIT}/{name}.py", support.telling_test(name, told))
    project.write(support.SERIAL_ONLY_REL, f"{entry}  # latency: planted\n")
    project.commit("regression tests", who=support.ORCHESTRATOR)
    project.add_ticket(TICKET, WBS)
    for name in ACCEPTANCE_TESTS:
        project.write(f"{ACCEPTANCE}/{name}.py", support.telling_test(name, told))
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "test_gone" in support.error_text(error), \
        f"the refusal does not name the case the entry names\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the refusal is counted {support.iteration_count(project.root, TICKET)} times\n{run.describe()}"
    ran = support.told_by(told)
    wrong = {name: runs for name, runs in ran.items() if not support.ran_in_a_worker(runs)}
    assert sorted(ran) == sorted(ALL_TESTS) and not wrong, \
        f"the cases that exist did not each run once in a worker: {sorted(ran)} {wrong}\n{run.describe()}"
