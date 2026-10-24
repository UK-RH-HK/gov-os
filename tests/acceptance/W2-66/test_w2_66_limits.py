"""Part 3, KPI 8 and 9 with failure line 4: the per-test time limit and the distribution mode.

Every test a close runs has a per-test limit (pytest-timeout, the ``signal`` method; the test map's
``per_test_timeout``, 900 s by default). A test that passes it fails, and the failure names the limit. Without
pytest-timeout the close does not pass: it is refused ``TIMEOUT_PLUGIN_ABSENT`` (README, "Interface").
pytest-timeout is an owner install not yet made: in this worktree every case of the suite that runs a close is
red for that reason until it is installed (README, "Red reasons"). The limit of the fixture is 2 s, so a case
runs in seconds; the hung test would sleep 30 s, and what it tells is counted, not timed.

The parallel run's distribution mode is one setting (the test map's ``distribution``), ``load`` by default.
"""

import pytest

import w2_66_support as support

LIMIT = 2
HANG = 30
HUNG = {
    "parallel": ("tests/acceptance/W1-bb/test_bb_hangs.py", "test_bb_hangs"),
    "serial-afterwards": (support.BB_APART.split("::")[0], "test_apart_W1_bb"),
}


def _hanging(told, name):
    return ("import os\nimport time\n\n\n"
            f"def {name}():\n"
            f"    open(os.path.join({str(told)!r}, {name!r} + '.started'), 'w').close()\n"
            f"    time.sleep({HANG})\n"
            f"    open(os.path.join({str(told)!r}, {name!r} + '.finished'), 'w').close()\n")


@pytest.mark.parametrize("form", sorted(HUNG))
def test_a_hung_test_fails_at_the_per_test_limit_and_the_failure_names_the_limit(make_fixture, sandbox, tmp_path,
                                                                                   form):
    told = tmp_path / "hung"
    told.mkdir()
    fixture = make_fixture(test_map={**support.DEFAULT_TEST_MAP, support.PER_TEST_TIMEOUT_KEY: LIMIT})
    rel, name = HUNG[form]
    fixture.merged({rel: _hanging(told, name)}, "a test that hangs")
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox, "--timeout", "600")
    support.refused(run)
    assert (told / f"{name}.started").exists(), f"the hung test did not start\n{run.describe()}"
    assert not (told / f"{name}.finished").exists(), \
        f"the hung test ran to its end: no per-test limit of {LIMIT} s held it ({form} run)"
    evidence = support.evidence_of(run)
    assert evidence.get(support.PER_TEST_TIMEOUT_KEY) == LIMIT, f"the evidence does not state the limit: {evidence}"
    failing = [f for f in evidence.get("failures") or [] if name in str(f.get("test"))]
    assert failing, f"the hung test is not among the failures: {evidence.get('failures')}"
    text = str(failing[0].get("text"))
    assert "timeout" in text.lower() and str(LIMIT) in text, f"the failure does not name the limit: {text!r}"


def test_without_pytest_timeout_the_close_does_not_pass_silently(fixture, sandbox, tmp_path):
    support.widget_change(fixture, sandbox)
    env = support.environment_without_module(tmp_path / "no-timeout", sandbox, ("pytest_timeout", "pytest-timeout"))
    assert not support.close_support.can_import("pytest_timeout", sandbox, env=env), \
        "the fixture cannot take pytest-timeout away from the interpreter here"
    run = fixture.close(sandbox, env=env)
    error = support.refused(run, exit_code=support.EXIT_GOV_ERROR)
    assert error.get("code") == support.TIMEOUT_PLUGIN_ABSENT, \
        f"a close without the per-test limit is not refused {support.TIMEOUT_PLUGIN_ABSENT}\n{run.describe()}"
    assert not support.close_support.close_records(fixture.root, support.TICKET), "a close record was written"


def test_the_distribution_mode_is_one_setting_and_the_runs_follow_it(make_fixture, sandbox):
    """``loadfile`` keeps the cases of a file in one worker: four cases of one file in one worker show it."""
    fixture = make_fixture(test_map={**support.DEFAULT_TEST_MAP, support.DISTRIBUTION_KEY: "loadfile"})
    names = [f"test_one_file_{n}" for n in range(4)]
    text = "".join(support.close_support.telling_test(name, fixture.told).split("\n\n\n", 1)[1] + "\n\n"
                   for name in names)
    fixture.merged({"tests/acceptance/W1-bb/test_bb_one_file.py": "import os\nimport time\n\nimport pytest\n\n\n"
                    + text})
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.evidence_of(run)
    assert evidence.get(support.DISTRIBUTION_KEY) == "loadfile", f"the mode is not stated: {evidence}"
    workers = support.close_support.workers_that_ran(fixture.told_runs(), names)
    assert len(workers) == 1, f"the four cases of one file ran in {workers}: the setting was not followed"
