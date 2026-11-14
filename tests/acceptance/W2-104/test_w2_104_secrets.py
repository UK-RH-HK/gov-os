"""KPI success 3 (second half) and failure F3: the harness reads no secret and prints none.

Success 3 [DEC-959 item 5, DEC-820 (a)]: "... the harness reads no secret and prints none".
F3: "A secret read or printed."

The contract: a fake key planted in the environment, or in a secrets-like file in the temporary project,
never appears in ``gov``'s standard output or error, nor in any record it writes, including when the stub
prints that key on its own standard error and fails. The values planted here are made-up strings
(``support.planted_values``); the environment passes through to the stub, as the contract states.
"""

from __future__ import annotations

import pytest

import w2_104_support as support

SKILL_REL = "skills/leaky"
SKILL_NAME = "leaky-skill"
SECRETS_FILE = ".env"


def _plant_values(project):
    env_value, file_value = support.planted_values()
    (project / SECRETS_FILE).write_text(f"ANTHROPIC_API_KEY={file_value}\n", encoding="utf-8")
    return env_value, file_value, {"ANTHROPIC_API_KEY": env_value}


def _assert_nowhere(values, run, project):
    for value in values:
        assert value not in run.stdout, f"a planted secret is on gov's standard output\n{run.describe()}"
        assert value not in run.stderr, f"a planted secret is on gov's standard error\n{run.describe()}"
    written = support.every_file_text(project, skip={SECRETS_FILE})
    for rel, text in written.items():
        for value in values:
            assert value not in text, f"a planted secret is written in {rel}"


@pytest.mark.parametrize("json_mode", [True, False], ids=["json", "text"])
def test_a_stub_that_prints_the_key_and_fails_leaks_nothing_through_gov(json_mode, project, sandbox, stub):
    """Scenario 1's stub prints the planted values on its stderr and exits 1; scenario 2's prints them as its
    non-JSON stdout; scenario 3's returns them in an ``is_error`` reply. All three are not run."""
    env_value, file_value, env = _plant_values(project)
    folder = support.plant_skill(project, SKILL_REL, SKILL_NAME, support.three(
        session=(support.SESSION_LEAK_STDERR, support.SESSION_LEAK_STDOUT, support.SESSION_LEAK_ERROR)))

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub, extra_env=env, json_mode=json_mode)

    assert run.returncode == support.EXIT_ANY_NOT_RUN, run.describe()
    assert len(stub.sessions()) == 3, "the stub was not run for each scenario, so nothing was put to the test"
    _assert_nowhere((env_value, file_value), run, project)
    verdicts = {entry["scenario"]: entry["verdict"] for entry in support.records(folder)[-3:]}
    assert verdicts == {1: "not-run", 2: "not-run", 3: "not-run"}, verdicts


def test_a_passing_run_prints_and_records_no_planted_secret(project, sandbox, stub):
    env_value, file_value, env = _plant_values(project)
    support.plant_skill(project, SKILL_REL, SKILL_NAME, support.three())

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub, extra_env=env)

    assert run.returncode == support.EXIT_ALL_PASSED, run.describe()
    _assert_nowhere((env_value, file_value), run, project)


def test_the_harness_does_not_read_a_secrets_file_in_the_project(project, sandbox, stub):
    """The secrets-like file is made unreadable: a harness that opens it fails, one that reads no secret
    evaluates the skill as usual."""
    _, file_value, _ = _plant_values(project)
    support.plant_skill(project, SKILL_REL, SKILL_NAME, support.three())
    secrets = project / SECRETS_FILE
    secrets.chmod(0)
    try:
        run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)
    finally:
        secrets.chmod(0o600)

    assert run.returncode == support.EXIT_ALL_PASSED, run.describe()
    assert run.verdicts() == {1: "pass", 2: "pass", 3: "pass"}, run.describe()
    assert file_value not in run.stdout + run.stderr, run.describe()
