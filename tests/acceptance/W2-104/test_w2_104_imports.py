"""KPI success 2 and failure F2: an imported skill is adopted only with a licence record and three passes.

Success 2 [DEC-959 item 5]: "An imported skill (Anthropic's collection or another source) is adopted only when
governance/project/skill-imports.yaml records its source, version, licence and the licence's verdict for this
use, and its three scenarios pass; the harness refuses to mark an import adopted otherwise".

F2: "An import marked adopted with no licence record or a failing scenario."

The contract: ``--adopt`` marks the entry whose ``name`` is the skill's front-matter name ``adopted: true`` only
when the entry exists, ``source``, ``version`` and ``licence`` are non-empty, ``licence_verdict`` is exactly
``allowed``, and all three scenarios pass in that run (exit 0); otherwise exit 6, the entry, if there is one,
ends ``adopted: false``, and other entries are unchanged. Without ``--adopt`` nothing changes ``adopted``.
Whether the scenarios run before a refusal for the licence record is left open, so no case looks at it.

The skill's folder name differs from its front-matter name, so the entry is found by the name.
"""

from __future__ import annotations

import pytest

import w2_104_support as support

SKILL_REL = "skills/imported-pdf"
SKILL_NAME = "pdf-tools"
OTHER = support.import_entry("other-imported-skill", source="https://example.invalid/other", version="0.9.2",
                             licence="MIT", licence_verdict="allowed", adopted=True)


def _plant(project, session=("", "", ""), judge=("", "", "")):
    return support.plant_skill(project, SKILL_REL, SKILL_NAME, support.three(session=session, judge=judge))


def _entries(project):
    entries = support.read_imports(project)
    by_name = {entry.get("name"): entry for entry in entries}
    assert len(by_name) == len(entries), f"an import entry is duplicated: {entries}"
    return by_name


def _adopt(project, sandbox, stub):
    return support.skilleval(project, sandbox, SKILL_REL, "--adopt", stub=stub)


def test_a_recorded_allowed_import_whose_three_scenarios_pass_is_adopted(project, sandbox, stub):
    _plant(project)
    entry = support.import_entry(SKILL_NAME)
    support.write_imports(project, [OTHER, entry])

    run = _adopt(project, sandbox, stub)

    assert run.returncode == support.EXIT_ADOPTED, run.describe()
    assert run.verdicts() == {1: "pass", 2: "pass", 3: "pass"}, run.describe()
    assert run.result()["adopted"] is True, run.describe()
    after = _entries(project)
    assert after[SKILL_NAME]["adopted"] is True, after
    for key, value in entry.items():
        if key != "adopted":
            assert after[SKILL_NAME].get(key) == value, f"the entry's {key} changed: {after[SKILL_NAME]}"
    assert after["other-imported-skill"] == OTHER, "another import entry changed"


BAD_RECORDS = {
    "no-source": {"source": ""},
    "no-version": {"version": ""},
    "no-licence": {"licence": ""},
    "no-licence-key": {"licence": support.DROP},
    "verdict-denied": {"licence_verdict": "denied"},
    "verdict-unknown": {"licence_verdict": "unknown"},
    "no-verdict-key": {"licence_verdict": support.DROP},
}


@pytest.mark.parametrize("defect", sorted(BAD_RECORDS))
def test_an_import_without_a_full_allowing_licence_record_is_refused(defect, project, sandbox, stub):
    """The entry starts ``adopted: true``, so the case also holds that it ends ``false``."""
    _plant(project)
    support.write_imports(project, [OTHER, support.import_entry(SKILL_NAME, adopted=True, **BAD_RECORDS[defect])])

    run = _adopt(project, sandbox, stub)

    assert run.returncode == support.EXIT_ADOPTION_REFUSED, f"expected exit code 6 ({defect})\n{run.describe()}"
    assert run.result()["adopted"] is False, run.describe()
    after = _entries(project)
    assert after[SKILL_NAME]["adopted"] is False, f"the import is marked adopted ({defect}): {after[SKILL_NAME]}"
    assert after["other-imported-skill"] == OTHER, "another import entry changed"


def test_an_import_with_no_entry_is_refused(project, sandbox, stub):
    _plant(project)
    support.write_imports(project, [OTHER])

    run = _adopt(project, sandbox, stub)

    assert run.returncode == support.EXIT_ADOPTION_REFUSED, run.describe()
    assert run.result()["adopted"] is False, run.describe()
    after = _entries(project)
    assert after["other-imported-skill"] == OTHER, "another import entry changed"
    assert after.get(SKILL_NAME, {}).get("adopted") is not True, f"the import is marked adopted: {after}"


def test_an_import_with_no_import_record_file_is_refused(project, sandbox, stub):
    _plant(project)

    run = _adopt(project, sandbox, stub)

    assert run.returncode == support.EXIT_ADOPTION_REFUSED, run.describe()
    assert run.result()["adopted"] is False, run.describe()
    if (project / support.IMPORTS_REL).exists():
        assert _entries(project).get(SKILL_NAME, {}).get("adopted") is not True, _entries(project)


SCENARIO_DEFECTS = {
    "a-failing-scenario": {"judge": ("", support.JUDGE_FAIL, "")},
    "a-scenario-with-no-verdict": {"judge": ("", "", support.JUDGE_NO_VERDICT)},
    "a-scenario-not-run": {"session": (support.SESSION_EXIT_NONZERO, "", "")},
}


@pytest.mark.parametrize("defect", sorted(SCENARIO_DEFECTS))
def test_an_import_with_a_full_licence_record_but_not_three_passes_is_refused(defect, project, sandbox, stub):
    _plant(project, **SCENARIO_DEFECTS[defect])
    support.write_imports(project, [OTHER, support.import_entry(SKILL_NAME, adopted=True)])

    run = _adopt(project, sandbox, stub)

    assert run.returncode == support.EXIT_ADOPTION_REFUSED, f"expected exit code 6 ({defect})\n{run.describe()}"
    assert run.result()["adopted"] is False, run.describe()
    assert "pass" in run.verdicts().values() and set(run.verdicts().values()) != {"pass"}, run.describe()
    after = _entries(project)
    assert after[SKILL_NAME]["adopted"] is False, f"the import is marked adopted ({defect}): {after[SKILL_NAME]}"
    assert after["other-imported-skill"] == OTHER, "another import entry changed"


@pytest.mark.parametrize("adopted, judge, code", [
    (False, ("", "", ""), support.EXIT_ALL_PASSED),
    (True, ("", support.JUDGE_FAIL, ""), support.EXIT_ANY_FAILED),
], ids=["not-adopted-all-pass", "adopted-one-fails"])
def test_without_adopt_the_harness_never_changes_adopted(adopted, judge, code, project, sandbox, stub):
    _plant(project, judge=judge)
    entry = support.import_entry(SKILL_NAME, adopted=adopted)
    support.write_imports(project, [OTHER, entry])

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == code, run.describe()
    assert run.result()["adopted"] is None, run.describe()
    after = _entries(project)
    assert after[SKILL_NAME] == entry, f"the entry changed without --adopt: {after[SKILL_NAME]}"
    assert after["other-imported-skill"] == OTHER, "another import entry changed"
