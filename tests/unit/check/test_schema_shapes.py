"""Builder tests for core-schema's findings on a list of maps and its conditional, held through check-jsonschema
(W2-64; regression evidence only; the acceptance tests are tests/acceptance/W2-02/ and W2-64/). W2-64 replaced the
subset's own shape reader (``_validate_shapes``): its cases are taken here through ``check``, on the kernel's adoption
verdict, whose conditions hold a list of maps and the one conditional."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check.schema import check  # noqa: E402

SCHEMAS_REL = "template/governance/kernel/schemas"
REL = "docs/adoption/AV-0001.md"


def _verdict_project(tmp_path, conditions):
    for path in (REPO / SCHEMAS_REL).glob("*.schema.json"):
        (tmp_path / SCHEMAS_REL).mkdir(parents=True, exist_ok=True)
        shutil.copy(path, tmp_path / SCHEMAS_REL / path.name)
    record = tmp_path / REL
    record.parent.mkdir(parents=True)
    record.write_text("---\nid: AV-0001\ntype: adoption-verdict\nstatus: ACCEPTED\nstate_class: EVIDENCE\n"
                      f"verdict: ADOPTED_WITH_ACCEPTED_EXCEPTIONS\n{conditions}---\n# A verdict\n", encoding="utf-8")
    return tmp_path


def _faults(tmp_path, conditions):
    return [(f["code"], f["field"], f["at"]) for f in check(_verdict_project(tmp_path, conditions))]


def test_the_kernel_verdict_with_its_named_conditions_passes(tmp_path):
    conditions = ("conditions:\n- {name: gov doctor is green, source: CAP-44.h, state: met}\n"
                  "- {name: a first gov close exits 0, source: CAP-44.h, state: accepted, owner_entry: DEC-741}\n")
    assert check(_verdict_project(tmp_path, conditions)) == []


def test_the_kernel_verdict_refuses_an_accepted_condition_without_its_owner_entry(tmp_path):
    conditions = "conditions:\n- {name: a first gov close exits 0, source: CAP-44.h, state: accepted}\n"
    assert _faults(tmp_path, conditions) == [("SCHEMA_INVALID_FIELD", "conditions", "$.conditions[0]")]


def test_an_item_that_faults_is_the_top_level_fields_finding_and_says_where(tmp_path):
    conditions = ("conditions:\n- {name: a, source: CAP-44.h, state: met}\n"
                  "- {name: b, source: CAP-44.h, state: waived}\n")
    found = check(_verdict_project(tmp_path, conditions))
    assert [(f["code"], f["field"], f["at"], f["schema"]) for f in found] == [
        ("SCHEMA_INVALID_FIELD", "conditions", "$.conditions[1].state", "adoption-verdict.schema.json")]
    assert found[0]["message"].startswith(f"{REL}: field 'conditions' is refused by adoption-verdict.schema.json "
                                          "at $.conditions[1].state: 'waived' is not one of")


def test_a_map_missing_a_required_key_or_a_key_of_the_wrong_shape_is_a_fault(tmp_path):
    assert _faults(tmp_path, "conditions:\n- {source: CAP-44.h, state: met}\n") == [
        ("SCHEMA_INVALID_FIELD", "conditions", "$.conditions[0]")]


def test_a_key_of_the_wrong_shape_is_a_fault(tmp_path):
    assert _faults(tmp_path, "conditions:\n- {name: '', source: CAP-44.h, state: met}\n") == [
        ("SCHEMA_INVALID_FIELD", "conditions", "$.conditions[0].name")]


def test_a_non_list_where_a_list_stands_and_a_non_map_where_a_map_stands(tmp_path):
    assert _faults(tmp_path, "conditions: all met\n") == [("SCHEMA_INVALID_FIELD", "conditions", "$.conditions")]


def test_a_non_map_item(tmp_path):
    assert _faults(tmp_path, "conditions: [met]\n") == [("SCHEMA_INVALID_FIELD", "conditions", "$.conditions[0]")]


def test_a_missing_required_top_level_field_is_schema_missing_field(tmp_path):
    assert _faults(tmp_path, "") == [("SCHEMA_MISSING_FIELD", "conditions", "$")]
