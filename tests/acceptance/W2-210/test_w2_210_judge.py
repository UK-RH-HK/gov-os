"""V5: W2-81's judge reads the verdict stage [DAEO-l78m; W2-81 analysis R7 and A5].

``w2_81_judge.built_today()`` counts ``VERDICT`` built when ``gov.adopt.command.STAGES`` lists it (as for A7 and A10);
a record at ``governance/adoption/VERDICT-lite.md`` is PRESENT when well formed (``verdict`` one of the three, ``lite``
true, ``conditions`` a list of mappings with ``name`` and ``state``, ``conditions_not_checked`` a list, the verdict
agreeing with the conditions as V2 states), ABSENT when missing and MALFORMED when not, each a reason of ``overall``.
The judge is test code: the cases hold it directly. They pass ``built`` explicitly, so that they stand on the judge
alone and not on the stage; the two that read the real stage list say so.
"""

from __future__ import annotations

import shutil

import pytest
import yaml

import w2_81_build as build
import w2_81_judge as judge
import w2_81_standin as standin
import w2_210_support as d1

ALL = set(judge.CAPABILITIES)
README = d1.REPO_ROOT / "tests/acceptance/W2-81/README.md"
FIGURES = {name: dict(standin.PERFECT_FIGURES) for name in (*build.SHAPES, build.CLEAN)}


def _record(verdict="ADOPTED_HEALTHY", conditions=None, **replace):
    """A well-formed lite verdict record's frontmatter; ``replace`` swaps a key (None removes it)."""
    front = {"id": "ADOPT-VERDICT", "type": "adoption-verdict", "status": "RECORDED", "state_class": "EVIDENCE",
             "verdict": verdict, "lite": True, "conditions": conditions or standin.verdict_conditions("met"),
             "conditions_not_checked": ["(2)", "(7)", "(8)", "(10)", "A9", "A11"]}
    for key, value in replace.items():
        if value is None:
            front.pop(key, None)
        else:
            front[key] = value
    return front


def _write(folder, front):
    path = folder / judge.record_name("VERDICT")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# the verdict\n", encoding="utf-8")


def _states(*states):
    return [{"name": f"C{n}", "source": "CAP-44.h", "state": state} for n, state in enumerate(states)]


def _accepted(*states):
    return [{**item, **({"owner_entry": "DEC-999"} if item["state"] == "accepted" else {})} for item in _states(*states)]


# --- built_today ------------------------------------------------------------------------------------------------

def test_built_today_counts_verdict_built_exactly_when_the_command_lists_it(monkeypatch):
    """V5: as for A7 and A10 (S-STAGES), from ``gov.adopt.command.STAGES``, never ``project.STAGES``."""
    from gov.adopt import command, project

    monkeypatch.setattr(command, "STAGES", (*(s for s in command.STAGES if s != "VERDICT"),))
    assert "VERDICT" not in judge.built_today()
    monkeypatch.setattr(project, "STAGES", (*project.STAGES, "VERDICT"))  # the project's list names it: no matter
    assert "VERDICT" not in judge.built_today()
    monkeypatch.setattr(command, "STAGES", (*command.STAGES, "VERDICT"))
    today = judge.built_today()
    assert "VERDICT" in today and {"A7", "A10"} <= today


def test_built_today_counts_the_verdict_stage_the_command_offers():
    """V5: today's code: the command's own stage list has VERDICT, so the judge counts it built."""
    from gov.adopt import command

    assert "VERDICT" in command.STAGES, "gov adopt --lite does not offer the VERDICT stage"
    assert "VERDICT" in judge.built_today()


def test_the_capability_table_and_the_readme_no_longer_say_the_verdict_is_not_built():
    """V5: ``CAPABILITIES['VERDICT']`` and the README's VERDICT row (T5)."""
    text = judge.CAPABILITIES["VERDICT"][2].lower()
    assert "not built" not in text and "not merged" not in text and "not read" not in text, text
    rows = [line for line in README.read_text(encoding="utf-8").splitlines() if line.startswith("| `VERDICT` |")]
    assert len(rows) == 1, rows
    assert "**no**" not in rows[0] and "not merged" not in rows[0] and "not built" not in rows[0].lower(), rows[0]


# --- the record's states ----------------------------------------------------------------------------------------

@pytest.mark.parametrize("front", [
    _record(),
    _record("ADOPTED_WITH_ACCEPTED_EXCEPTIONS", _accepted("met", "accepted", "met")),
    _record("NOT_ADOPTED_HEALTHY", _states("met", "not met", "met")),
    _record("NOT_ADOPTED_HEALTHY", _accepted("accepted", "not met")),
    _record(extra_field="a produced record has more keys than the judge reads"),
], ids=["healthy", "accepted-exceptions", "not-adopted", "not-adopted-beside-an-accepted", "extra-keys"])
def test_a_well_formed_record_is_present(tmp_path, front):
    _write(tmp_path, front)
    record = judge.read_record(tmp_path, judge.record_name("VERDICT"), "VERDICT")
    assert record.state == "PRESENT", (record.state, record.why)


def test_a_missing_record_is_absent(tmp_path):
    assert judge.read_record(tmp_path, judge.record_name("VERDICT"), "VERDICT").state == "ABSENT"


MALFORMED = {
    "verdict-outside-the-three": _record("FINE"),
    "healthy-over-a-condition-not-met": _record("ADOPTED_HEALTHY", _states("met", "not met")),
    "healthy-over-an-accepted-one": _record("ADOPTED_HEALTHY", _accepted("met", "accepted")),
    "exceptions-over-a-condition-not-met": _record("ADOPTED_WITH_ACCEPTED_EXCEPTIONS", _accepted("accepted", "not met")),
    "exceptions-with-none-accepted": _record("ADOPTED_WITH_ACCEPTED_EXCEPTIONS", _states("met", "met")),
    "not-adopted-over-conditions-all-met": _record("NOT_ADOPTED_HEALTHY", _states("met", "met")),
    "lite-false": _record(lite=False),
    "lite-missing": _record(lite=None),
    "lite-a-word": _record(lite="true"),
    "no-conditions": _record(),  # its `conditions` key is removed in the case
    "conditions-not-a-list": _record(conditions={"A0": "met"}),
    "a-condition-without-a-name": _record(conditions=[{"source": "CAP-44.h", "state": "met"}]),
    "a-condition-without-a-state": _record(conditions=[{"name": "A0", "source": "CAP-44.h"}]),
    "a-condition-that-is-not-a-mapping": _record(conditions=["A0"]),
    "no-conditions-not-checked": _record(conditions_not_checked=None),
    "conditions-not-checked-not-a-list": _record(conditions_not_checked="(2), (7), (8), (10)"),
}


@pytest.mark.parametrize("flaw", sorted(MALFORMED))
def test_a_record_not_well_formed_is_malformed(tmp_path, flaw):
    """V5: each flaw alone makes the record MALFORMED (a reason of ``overall``), never PRESENT."""
    if flaw == "no-conditions":
        front = _record()
        front.pop("conditions")
    else:
        front = MALFORMED[flaw]
    _write(tmp_path, front)
    record = judge.read_record(tmp_path, judge.record_name("VERDICT"), "VERDICT")
    assert record.state == "MALFORMED", (record.state, record.why)


# --- the judge over a stand-in adoption -------------------------------------------------------------------------

def _judged(ground, tmp_path, name, change):
    built_repo = ground[name]
    model = standin.perfect(built_repo)
    change(model)
    root, beside = standin.render(model, built_repo, tmp_path / "adopted", tmp_path / "beside")
    judgement = judge.judge_repository(built_repo.manifest, root, beside, built_repo.secrets, ALL)
    reasons = judge.overall([judgement], {name: FIGURES[name]}, [name])["reasons"]
    shutil.rmtree(tmp_path / "adopted", ignore_errors=True)
    return judgement, [r for r in reasons if "VERDICT" in r]


def test_a_stand_in_adoption_with_a_well_formed_verdict_record_has_no_verdict_reason(ground, tmp_path):
    judgement, reasons = _judged(ground, tmp_path, build.CLEAN, lambda model: None)
    assert judgement["stages"]["VERDICT"]["status"] == "PRESENT"
    assert reasons == []


def test_a_stand_in_adoption_without_the_record_has_one_verdict_reason(ground, tmp_path):
    judgement, reasons = _judged(ground, tmp_path, build.CLEAN, lambda model: model["records"].update(VERDICT=None))
    assert judgement["stages"]["VERDICT"]["status"] == "ABSENT"
    assert reasons == [f"{build.CLEAN}: stage VERDICT is ABSENT"]


def _healthy_over_not_met(model):
    model["records"]["VERDICT"].update(verdict="ADOPTED_HEALTHY", conditions=standin.verdict_conditions("not met"))


def _lite_false(model):
    model["records"]["VERDICT"]["lite"] = False


def _no_conditions_not_checked(model):
    del model["records"]["VERDICT"]["conditions_not_checked"]


@pytest.mark.parametrize("change", [_healthy_over_not_met, _lite_false, _no_conditions_not_checked],
                         ids=["healthy-over-a-condition-not-met", "lite-false", "no-conditions-not-checked"])
def test_a_stand_in_adoption_with_a_malformed_verdict_record_has_one_malformed_reason(ground, tmp_path, change):
    judgement, reasons = _judged(ground, tmp_path, build.CLEAN, change)
    assert judgement["stages"]["VERDICT"]["status"] == "MALFORMED"
    assert reasons == [f"{build.CLEAN}: stage VERDICT is MALFORMED"]


def test_a_malformed_record_is_never_read_as_the_verdict_for_the_secret(ground, tmp_path):
    """V5/F2: an ADOPTED_HEALTHY over a condition not met is MALFORMED, so the judge reads no verdict from it (its
    ``adoption_verdict`` is None)."""
    judgement, _ = _judged(ground, tmp_path, "secret-history", _healthy_over_not_met)
    assert judgement["adoption_verdict"] is None


def test_the_judge_without_a_built_set_follows_the_command_stage_list(ground, tmp_path):
    """V5: ``built=None`` is today's code: the verdict stage is measured, not NOT_BUILT, once the command lists it."""
    from gov.adopt import command

    built_repo = ground[build.CLEAN]
    root, beside = standin.render(standin.perfect(built_repo), built_repo, tmp_path / "adopted", tmp_path / "beside")
    judgement = judge.judge_repository(built_repo.manifest, root, beside, built_repo.secrets, None)
    want = "PRESENT" if "VERDICT" in command.STAGES else judge.NOT_BUILT
    assert judgement["stages"]["VERDICT"]["status"] == want
    assert "VERDICT" in command.STAGES, "gov adopt --lite does not offer the VERDICT stage"
