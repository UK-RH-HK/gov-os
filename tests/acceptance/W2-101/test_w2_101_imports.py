"""W2-101: an imported part is adopted only with its licence recorded and its three scenarios passing: success-5,
failure-3 (the failing-scenario half) and failure-4. No new adoption gate exists: the cases run ``gov skilleval <part>
--adopt`` of this repository's ``src/`` on a planted part and a planted ``governance/project/skill-imports.yaml``,
with a stub model (a ``claude`` of the test's own on a ``PATH`` of its folder and the system folders).

Adopted: the entry (found by the part's front-matter ``name``) with source, version, licence and ``licence_verdict:
allowed`` and three passes: exit 0, ``adopted: true``. Refused: no entry, no record file, a missing source, version or
licence, a ``licence_verdict`` other than ``allowed`` (``denied``, ``unknown``, ``forbidden``), or a failing scenario:
exit 6, the part named in the result, the entry ends ``adopted: false`` and the other entries are unchanged.
These cases judge shipped code (``gov skilleval``) on planted input: green on the base by design.
"""
from __future__ import annotations

import pytest

import w2_101_support as s

OTHER = s.import_entry("other-imported-part", source="https://example.invalid/other", version="0.9.2",
                       licence="MIT", licence_verdict="allowed", adopted=True)
PARTS = pytest.mark.parametrize("part", s.SKILLS)


def _rel(part):
    return f"imported/{part}"


def _adopt(project, tmp_path, stub, part):
    return s.skilleval(project, tmp_path / "sandbox", stub, _rel(part), "--adopt")


def _refused(run, part, project):
    """The refusals' common ground: exit 6, the part named, ``adopted`` false in the result and in the record."""
    assert run.returncode == 6, f"expected exit 6\n{run.describe()}"
    result = run.result()
    assert result.get("skill") == part and part in run.stdout, f"the part {part} is not named\n{run.describe()}"
    assert result.get("adopted") is False, run.describe()
    entries = s.read_imports(project) if (project / s.IMPORTS_REL).exists() else {}
    assert entries.get(part, {}).get("adopted") is not True, f"the part is marked adopted: {entries.get(part)}"
    if entries:
        assert entries.get("other-imported-part") == OTHER, "another import entry changed"


# success-5: adopted with a licence record and three passing scenarios -------------------------------------------------------

@PARTS
def test_a_part_with_a_licence_record_and_three_passing_scenarios_is_adopted(part, project, stub, tmp_path):
    s.plant_part(project, _rel(part), part)
    entry = s.import_entry(part)
    s.write_imports(project, [OTHER, entry])
    run = _adopt(project, tmp_path, stub, part)
    assert run.returncode == 0, run.describe()
    assert run.verdicts() == {1: "pass", 2: "pass", 3: "pass"}, run.describe()
    assert run.result().get("adopted") is True, run.describe()
    after = s.read_imports(project)
    assert after[part]["adopted"] is True, after[part]
    for key, value in entry.items():
        if key != "adopted":
            assert after[part].get(key) == value, f"the entry's {key} changed: {after[part]}"
    assert after["other-imported-part"] == OTHER, "another import entry changed"


# success-5 and failure-4: no record, an incomplete record, a forbidding licence ---------------------------------------------

@PARTS
def test_a_part_with_no_licence_record_is_refused_naming_the_part(part, project, stub, tmp_path):
    s.plant_part(project, _rel(part), part)
    s.write_imports(project, [OTHER])
    _refused(_adopt(project, tmp_path, stub, part), part, project)


@PARTS
def test_a_part_with_no_record_file_at_all_is_refused_naming_the_part(part, project, stub, tmp_path):
    s.plant_part(project, _rel(part), part)
    _refused(_adopt(project, tmp_path, stub, part), part, project)


DEFECTS = {
    "no-licence": {"licence": ""},
    "no-licence-key": {"licence": s.DROP},
    "no-source": {"source": ""},
    "no-version": {"version": ""},
    "verdict-denied": {"licence_verdict": "denied"},
    "verdict-forbidden": {"licence_verdict": "forbidden"},
    "verdict-unknown": {"licence_verdict": "unknown"},
    "no-verdict-key": {"licence_verdict": s.DROP},
}


@pytest.mark.parametrize("defect", sorted(DEFECTS))
def test_a_part_with_no_licence_or_a_forbidding_licence_is_refused_naming_the_part(defect, project, stub, tmp_path):
    """The entry starts ``adopted: true``, so the case also holds that the refusal ends it ``false``."""
    part = "frontend"
    s.plant_part(project, _rel(part), part)
    s.write_imports(project, [OTHER, s.import_entry(part, adopted=True, **DEFECTS[defect])])
    _refused(_adopt(project, tmp_path, stub, part), part, project)


# success-5 and failure-3: a failing scenario ---------------------------------------------------------------------------------

@PARTS
@pytest.mark.parametrize("failing", [(1,), (3,), (1, 2, 3)], ids=["first", "last", "all"])
def test_a_part_with_a_failing_scenario_is_refused_naming_the_part_and_is_not_adopted(part, failing, project, stub,
                                                                                      tmp_path):
    s.plant_part(project, _rel(part), part, fail=failing)
    s.write_imports(project, [OTHER, s.import_entry(part, adopted=True)])
    run = _adopt(project, tmp_path, stub, part)
    _refused(run, part, project)
    verdicts = run.verdicts()
    assert [n for n, v in verdicts.items() if v == "fail"] == list(failing), f"verdicts {verdicts}"


@PARTS
def test_gov_skilleval_without_adopt_exits_3_on_a_failing_scenario_and_never_changes_adopted(part, project, stub,
                                                                                            tmp_path):
    """failure-3's failing-scenario half: exit 3 on the planted skill whose judgement fails one scenario; the
    adoption flag is untouched without ``--adopt`` and a later ``--adopt`` is refused."""
    s.plant_part(project, _rel(part), part, fail=(2,))
    entry = s.import_entry(part)
    s.write_imports(project, [OTHER, entry])
    run = s.skilleval(project, tmp_path / "sandbox", stub, _rel(part))
    assert run.returncode == 3, run.describe()
    assert run.result().get("skill") == part, run.describe()
    assert run.verdicts() == {1: "pass", 2: "fail", 3: "pass"}, run.describe()
    assert s.read_imports(project)[part] == entry, "the entry changed without --adopt"
    _refused(_adopt(project, tmp_path, stub, part), part, project)
    assert s.read_imports(project)[part]["adopted"] is False


@PARTS
def test_a_failing_scenario_leaves_a_record_naming_the_part_with_a_fail_entry(part, project, stub, tmp_path):
    """The planted scenario record with one failing result: ``scenario-records.yaml`` beside the planted part holds
    three entries for the part, the second ``fail``."""
    folder = s.plant_part(project, _rel(part), part, fail=(2,))
    s.skilleval(project, tmp_path / "sandbox", stub, _rel(part))
    records = s.load_yaml(folder / s.RECORD_FILE)["records"]
    assert [(r["skill"], r["scenario"], r["verdict"]) for r in records[-3:]] == \
        [(part, 1, "pass"), (part, 2, "fail"), (part, 3, "pass")], records
