"""W2-100: an imported skill or part is adopted only with its licence recorded and its three scenarios passing:
success-5 and failure-5.

Run through ``gov skilleval --adopt`` (W2-104's harness) with ``governance/project/skill-imports.yaml`` in a temporary
project and the stub ``claude`` of ``tmp_path``: an entry with a licence record (``licence_verdict: allowed``) and three
passing scenarios is adopted (exit 0, ``adopted: true``); no entry, no licence record, a forbidding verdict and a failing
scenario are each refused (exit 6), the output names the part (the skill's name) and the entry ends ``adopted: false``.
These cases need no skill folder of the ticket, so they are green on the base.
"""
from __future__ import annotations

import pytest

import w2_100_support as s

PART = "imported-notes"
REL = "skills/imported-notes"
OTHER = s.import_entry("other-imported-part", source="https://example.invalid/other", version="0.9.2", licence="MIT",
                       adopted=True)


def _plant(project, judge_fail_on=()):
    return s.plant_skill(project, REL, PART, s.planted_scenarios(PART, judge_fail_on=judge_fail_on))


def _adopt(project, base, stub):
    return s.run_skilleval(project, base, REL, "--adopt", stub=stub)


def test_a_part_with_a_licence_record_and_three_passing_scenarios_is_adopted(project, base, stub):
    _plant(project)
    entry = s.import_entry(PART)
    s.write_imports(project, [OTHER, entry])
    run = _adopt(project, base, stub)
    assert run.returncode == 0, run.describe()
    assert run.verdicts() == {1: "pass", 2: "pass", 3: "pass"}, run.describe()
    assert run.result()["adopted"] is True, run.describe()
    after = s.read_imports(project)
    assert after[PART]["adopted"] is True, after
    assert after["other-imported-part"] == OTHER, "another import entry changed"


DEFECTS = {
    "no-licence-record": {"licence": ""},
    "no-licence-key": {"licence": None},
    "no-source": {"source": ""},
    "forbidding-verdict": {"licence_verdict": "denied"},
    "forbidding-verdict-with-a-licence-named": {"licence": "GPL-3.0-only", "licence_verdict": "denied"},
}


@pytest.mark.parametrize("defect", sorted(DEFECTS))
def test_a_part_with_no_licence_record_or_a_forbidding_one_is_refused_naming_the_part(defect, project, base, stub):
    _plant(project)
    changes = {k: v for k, v in DEFECTS[defect].items()}
    entry = s.import_entry(PART, adopted=True, **changes)
    entry = {k: v for k, v in entry.items() if v is not None}
    s.write_imports(project, [OTHER, entry])
    run = _adopt(project, base, stub)
    assert run.returncode == 6, f"expected exit 6 ({defect})\n{run.describe()}"
    assert PART in run.stdout, f"the output does not name the part {PART}\n{run.describe()}"
    assert run.result()["adopted"] is False, run.describe()
    after = s.read_imports(project)
    assert after[PART]["adopted"] is False, f"the part is marked adopted ({defect}): {after[PART]}"
    assert after["other-imported-part"] == OTHER, "another import entry changed"


def test_a_part_with_no_entry_in_the_import_record_is_refused_naming_the_part(project, base, stub):
    _plant(project)
    s.write_imports(project, [OTHER])
    run = _adopt(project, base, stub)
    assert run.returncode == 6, run.describe()
    assert PART in run.stdout, f"the output does not name the part {PART}\n{run.describe()}"
    assert run.result()["adopted"] is False, run.describe()
    assert s.read_imports(project).get(PART, {}).get("adopted") is not True


def test_a_part_with_no_import_record_file_is_refused_naming_the_part(project, base, stub):
    _plant(project)
    run = _adopt(project, base, stub)
    assert run.returncode == 6, run.describe()
    assert PART in run.stdout, f"the output does not name the part {PART}\n{run.describe()}"
    assert run.result()["adopted"] is False, run.describe()


def test_a_part_with_a_full_licence_record_but_a_failing_scenario_is_refused_naming_the_part(project, base, stub):
    _plant(project, judge_fail_on=(3,))
    s.write_imports(project, [OTHER, s.import_entry(PART, adopted=True)])
    run = _adopt(project, base, stub)
    assert run.returncode == 6, run.describe()
    assert PART in run.stdout, f"the output does not name the part {PART}\n{run.describe()}"
    assert run.verdicts() == {1: "pass", 2: "pass", 3: "fail"}, run.describe()
    assert run.result()["adopted"] is False, run.describe()
    after = s.read_imports(project)
    assert after[PART]["adopted"] is False, f"the part is marked adopted: {after[PART]}"
    assert after["other-imported-part"] == OTHER, "another import entry changed"
