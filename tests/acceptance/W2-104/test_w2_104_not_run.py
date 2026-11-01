"""KPI success 3 (first half) and failure F1: a scenario that could not reach a model is not run, never a pass.

Success 3 [DEC-959 item 5, DEC-820 (a)]: "A scenario run that cannot reach a model (no network, no key) is
recorded as not run with its cause, never as a pass".

The contract names the ways a needed model process "could not be run or did not answer": no ``claude`` on the
``PATH``, a non-zero exit, output that is not the JSON object, ``is_error: true``, or a run past ``--timeout``.
A not-run scenario carries a one-line ``cause`` and no cost. Without ``--adopt``: exit 4 when none failed and
any was not run, exit 3 when any failed.

F1: "A scenario reported as passing that did not run". In every case below the stub's judgement would say
PASS if it were asked, so a harness that does not look at the session's answer reports a pass.
"""

from __future__ import annotations

import w2_104_support as support

SKILL_REL = "skills/flaky"
SKILL_NAME = "flaky-skill"
VERSION = "1.4.0"


def _assert_recorded_as_not_run(folder, run, numbers):
    by_number = support.last_entries(folder)
    for n, entry in by_number.items():
        support.assert_entry_shape(entry, run, SKILL_NAME, VERSION)
        if n in numbers:
            assert entry["verdict"] == "not-run", f"scenario {n} is not recorded as not run: {entry}"
    for n in numbers:
        support.assert_verdict_fields(run.scenario(n))


def test_a_session_that_fails_answers_badly_or_reports_an_error_is_not_run(project, sandbox, stub):
    folder = support.plant_skill(project, SKILL_REL, SKILL_NAME, support.three(
        session=(support.SESSION_EXIT_NONZERO, support.SESSION_BAD_JSON, support.SESSION_IS_ERROR)))

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == support.EXIT_ANY_NOT_RUN, run.describe()
    assert run.verdicts() == {1: "not-run", 2: "not-run", 3: "not-run"}, run.describe()
    _assert_recorded_as_not_run(folder, run, (1, 2, 3))


def test_a_judgement_that_fails_leaves_its_scenario_not_run(project, sandbox, stub):
    folder = support.plant_skill(project, SKILL_REL, SKILL_NAME,
                                 support.three(judge=("", "", support.JUDGE_EXIT_NONZERO)))

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == support.EXIT_ANY_NOT_RUN, run.describe()
    assert run.verdicts() == {1: "pass", 2: "pass", 3: "not-run"}, run.describe()
    _assert_recorded_as_not_run(folder, run, (3,))


def test_no_claude_on_the_path_leaves_every_scenario_not_run(project, sandbox):
    """No stub on the PATH, and none in the system folders: no model can be reached (no network, no key)."""
    folder = support.plant_skill(project, SKILL_REL, SKILL_NAME, support.three())

    run = support.skilleval(project, sandbox, SKILL_REL, stub=None)

    assert run.returncode == support.EXIT_ANY_NOT_RUN, run.describe()
    assert run.verdicts() == {1: "not-run", 2: "not-run", 3: "not-run"}, run.describe()
    _assert_recorded_as_not_run(folder, run, (1, 2, 3))


def test_a_session_past_the_timeout_is_not_run(project, sandbox, stub):
    folder = support.plant_skill(project, SKILL_REL, SKILL_NAME,
                                 support.three(session=(support.SESSION_SLEEP, "", "")))

    run = support.skilleval(project, sandbox, SKILL_REL, "--timeout", "2", stub=stub)

    assert run.returncode == support.EXIT_ANY_NOT_RUN, run.describe()
    assert run.verdicts() == {1: "not-run", 2: "pass", 3: "pass"}, run.describe()
    _assert_recorded_as_not_run(folder, run, (1,))
    assert support.last_entries(folder)[1]["seconds"] >= 1.9, "the wall time of a run past 2 s is under 2 s"


def test_a_failed_scenario_beside_a_not_run_one_ends_3(project, sandbox, stub):
    folder = support.plant_skill(project, SKILL_REL, SKILL_NAME, support.three(
        session=("", support.SESSION_EXIT_NONZERO, ""), judge=(support.JUDGE_FAIL, "", "")))

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == support.EXIT_ANY_FAILED, run.describe()
    assert run.verdicts() == {1: "fail", 2: "not-run", 3: "pass"}, run.describe()
    _assert_recorded_as_not_run(folder, run, (2,))
