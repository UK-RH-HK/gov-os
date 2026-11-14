"""The command exists, and a skill that cannot be evaluated is refused before anything runs (exit 5).

KPI success 1 [DEC-959 item 5]: ``gov skilleval <skill>`` runs "each of the skill's three committed
scenarios". The contract: a skill folder holds ``SKILL.md`` (front matter with ``name`` and ``version``) and
``scenarios.md`` with exactly three scenarios in W2-11's form; otherwise exit 5, "nothing is run and nothing
is recorded".
"""

from __future__ import annotations

import pytest

import w2_104_support as support


def test_gov_help_offers_skilleval_and_its_help_names_it(project, sandbox):
    listed = support.run_gov(project, sandbox, "--help", root=False)
    assert listed.returncode == 0, listed.describe()
    assert support.COMMAND in listed.stdout, f"gov --help does not offer {support.COMMAND}\n{listed.describe()}"
    own = support.run_gov(project, sandbox, support.COMMAND, "--help", root=False)
    assert own.returncode == 0, f"gov skilleval --help does not end with exit code 0\n{own.describe()}"
    assert support.COMMAND in own.stdout, f"the help of gov skilleval does not name it\n{own.describe()}"


def _no_skill_md(folder):
    (folder / "SKILL.md").unlink()


def _no_version(folder):
    (folder / "SKILL.md").write_text(support.skill_md("broken-skill", version=None), encoding="utf-8")


def _no_scenarios_md(folder):
    (folder / "scenarios.md").unlink()


def _two_scenarios(folder):
    text = support.scenarios_md("broken-skill", support.three()[:2])
    (folder / "scenarios.md").write_text(text, encoding="utf-8")


def _four_scenarios(folder):
    text = support.scenarios_md("broken-skill", support.three() + [support.scenario(4)])
    (folder / "scenarios.md").write_text(text, encoding="utf-8")


def _a_scenario_without_its_pass_line(folder):
    text = support.scenarios_md("broken-skill", support.three(), drop_pass_line=2)
    (folder / "scenarios.md").write_text(text, encoding="utf-8")


BROKEN = {
    "no-SKILL.md": _no_skill_md,
    "no-version": _no_version,
    "no-scenarios.md": _no_scenarios_md,
    "two-scenarios": _two_scenarios,
    "four-scenarios": _four_scenarios,
    "a-scenario-without-its-pass-line": _a_scenario_without_its_pass_line,
}


@pytest.mark.parametrize("defect", sorted(BROKEN))
def test_a_skill_that_cannot_be_evaluated_ends_5_runs_nothing_and_records_nothing(defect, project, sandbox, stub):
    folder = support.plant_skill(project, "skills/broken", "broken-skill", support.three())
    BROKEN[defect](folder)

    run = support.skilleval(project, sandbox, "skills/broken", stub=stub)

    assert run.returncode == support.EXIT_NOT_EVALUABLE, f"expected exit code 5 ({defect})\n{run.describe()}"
    assert not stub.calls(), f"a model process was run for a skill that cannot be evaluated: {stub.calls()}"
    assert not (folder / support.RECORD_FILE).exists(), f"a record was written ({defect})\n{run.describe()}"


def test_adopt_on_a_skill_that_cannot_be_evaluated_ends_5_and_adopts_nothing(project, sandbox, stub):
    folder = support.plant_skill(project, "skills/broken", "broken-skill", support.three())
    _two_scenarios(folder)
    support.write_imports(project, [support.import_entry("broken-skill")])

    run = support.skilleval(project, sandbox, "skills/broken", "--adopt", stub=stub)

    assert run.returncode == support.EXIT_NOT_EVALUABLE, run.describe()
    assert not stub.calls(), stub.calls()
    assert support.read_imports(project)[0]["adopted"] is False, support.read_imports(project)
