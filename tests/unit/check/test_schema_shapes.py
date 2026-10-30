"""Builder tests for core-schema's shape check of a standalone type: a list's items, a map's properties and the keys
it requires, the one conditional, and every other keyword still a fault (regression evidence only; the acceptance
tests are tests/acceptance/W2-02/)."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check.schema import _validate_shapes, check  # noqa: E402

SCHEMAS_REL = "template/governance/kernel/schemas"
REL = "docs/x/R-0001.md"
COMMON = {"$defs": {"decision_id": {"type": "string", "pattern": "^(ADR|DEC)-[0-9]{3,}$"}}}
CONDITION = {
    "type": "object",
    "required": ["name", "state"],
    "properties": {"name": {"$ref": "#/$defs/text"}, "state": {"enum": ["met", "accepted"]},
                   "owner_entry": {"$ref": "common.schema.json#/$defs/decision_id"}},
    "if": {"properties": {"state": {"const": "accepted"}}},
    "then": {"required": ["owner_entry"]},
}
SCHEMA = {
    "properties": {"flag": {"type": "boolean"}, "word": {"$ref": "#/$defs/text"},
                   "conditions": {"type": "array", "items": {"$ref": "#/$defs/condition"}}},
    "$defs": {"text": {"type": "string", "minLength": 1}, "condition": CONDITION},
}


def _faults(front, schema=SCHEMA):
    return [(f["code"], f["field"], f["message"]) for f in _validate_shapes(front, schema, COMMON, REL)]


def _with(field_shape, **defs):
    """SCHEMA with ``conditions`` given ``field_shape`` and the definitions ``defs`` added."""
    return {"properties": {"conditions": field_shape}, "$defs": {**SCHEMA["$defs"], **defs}}


def test_a_list_of_well_formed_items_passes():
    met, accepted = {"name": "a", "state": "met"}, {"name": "b", "state": "accepted", "owner_entry": "DEC-741"}
    assert _faults({"conditions": [met, accepted]}) == []
    assert _faults({"conditions": []}) == []


def test_an_item_that_faults_is_the_top_level_fields_finding_and_says_where():
    found = _faults({"conditions": [{"name": "a", "state": "met"}, {"name": "b", "state": "waived"}]})
    assert found == [("SCHEMA_INVALID_FIELD", "conditions",
                      f"{REL}: field 'conditions': conditions[1].state is not one of ['met', 'accepted']")]


def test_a_map_missing_a_required_key_is_a_fault():
    assert _faults({"conditions": [{"state": "met"}]}) == [
        ("SCHEMA_INVALID_FIELD", "conditions", f"{REL}: field 'conditions': conditions[0] has no 'name'")]


def test_a_key_of_the_wrong_shape_is_a_fault():
    assert [m for _, _, m in _faults({"conditions": [{"name": "", "state": "met"}]})] == [
        f"{REL}: field 'conditions': conditions[0].name is empty"]
    assert [m for _, _, m in _faults({"conditions": [{"name": "a", "state": "accepted", "owner_entry": "the owner"}]})] \
        == [f"{REL}: field 'conditions': conditions[0].owner_entry does not match ^(ADR|DEC)-[0-9]{{3,}}$"]


def test_the_conditional_both_ways():
    # the `if` holds: the `then` is owed
    assert [m for _, _, m in _faults({"conditions": [{"name": "a", "state": "accepted"}]})] == [
        f"{REL}: field 'conditions': conditions[0] has no 'owner_entry'"]
    # the `if` does not hold: nothing more is owed
    assert _faults({"conditions": [{"name": "a", "state": "met"}]}) == []


def test_a_non_list_where_a_list_stands_and_a_non_map_where_a_map_stands():
    assert [m for _, _, m in _faults({"conditions": "all met"})] == [f"{REL}: field 'conditions' is not a array"]
    assert [m for _, _, m in _faults({"conditions": ["met"]})] == [
        f"{REL}: field 'conditions': conditions[0] is not a object"]


def test_an_unknown_keyword_inside_a_list_is_still_a_fault():
    schema = _with({"type": "array", "items": {"$ref": "#/$defs/condition"}},
                   condition={**CONDITION, "additionalProperties": False})
    assert [m for _, _, m in _faults({"conditions": [{"name": "a", "state": "met"}]}, schema)] == [
        f"{REL}: field 'conditions': conditions[0] has a shape the check cannot measure"]
    deeper = _with({"type": "array", "items": {"$ref": "#/$defs/condition"}},
                   condition={**CONDITION, "properties": {"name": {"type": "string", "format": "uri"}}})
    assert [m for _, _, m in _faults({"conditions": [{"name": "a", "state": "met"}]}, deeper)] == [
        f"{REL}: field 'conditions': conditions[0].name has a shape the check cannot measure"]


def test_a_keyword_of_another_type_an_unknown_type_or_an_unread_ref_is_a_fault():
    for shape in ({"type": "string", "items": {"type": "string"}}, {"type": "array", "properties": {}},
                  {"type": "integer"}, {"type": ["string", "array"]}, {"type": "array", "items": True},
                  {"type": "array", "items": {"$ref": "other.schema.json#/$defs/text"}},
                  {"type": "object", "required": "name"}, {"type": "object", "properties": []}):
        assert [m for _, _, m in _faults({"conditions": ["a"]}, _with(shape))] == [
            f"{REL}: field 'conditions' has a shape the check cannot measure"], shape


def test_an_if_that_is_no_constant_test_or_has_no_then_is_a_fault():
    for conditional in ({"if": {"properties": {"state": {"enum": ["accepted"]}}}, "then": {"required": ["name"]}},
                        {"if": {"properties": {"state": {"const": "accepted"}}, "required": ["state"]},
                         "then": {"required": ["name"]}},
                        {"if": {"properties": {}}, "then": {"required": ["name"]}},
                        {"if": {"properties": {"state": {"const": "accepted"}}}},
                        {"then": {"required": ["name"]}},
                        {"if": {"properties": {"state": {"const": "met"}}}, "then": {"items": {}}}):
        shape = {"type": "array", "items": {"type": "object", **conditional}}
        found = [m for _, _, m in _faults({"conditions": [{"name": "a", "state": "met"}]}, _with(shape))]
        assert found == [f"{REL}: field 'conditions': conditions[0] has a shape the check cannot measure"], conditional


def test_the_string_and_boolean_findings_are_as_before():
    assert _faults({"flag": "yes", "word": ""}) == [
        ("SCHEMA_INVALID_FIELD", "flag", f"{REL}: field 'flag' is not a boolean"),
        ("SCHEMA_INVALID_FIELD", "word", f"{REL}: field 'word' is empty")]
    assert _faults({"flag": True, "word": "a"}) == []


def _verdict_project(tmp_path, conditions):
    for path in (REPO / SCHEMAS_REL).glob("*.schema.json"):
        (tmp_path / SCHEMAS_REL).mkdir(parents=True, exist_ok=True)
        shutil.copy(path, tmp_path / SCHEMAS_REL / path.name)
    record = tmp_path / "docs/adoption/AV-0001.md"
    record.parent.mkdir(parents=True)
    record.write_text("---\nid: AV-0001\ntype: adoption-verdict\nstatus: ACCEPTED\nstate_class: EVIDENCE\n"
                      f"verdict: ADOPTED_WITH_ACCEPTED_EXCEPTIONS\n{conditions}---\n# A verdict\n", encoding="utf-8")
    return tmp_path


def test_the_kernel_verdict_with_its_named_conditions_passes(tmp_path):
    conditions = ("conditions:\n- {name: gov doctor is green, source: CAP-44.h, state: met}\n"
                  "- {name: a first gov close exits 0, source: CAP-44.h, state: accepted, owner_entry: DEC-741}\n")
    assert check(_verdict_project(tmp_path, conditions)) == []


def test_the_kernel_verdict_refuses_an_accepted_condition_without_its_owner_entry(tmp_path):
    conditions = "conditions:\n- {name: a first gov close exits 0, source: CAP-44.h, state: accepted}\n"
    assert [(f["code"], f["field"]) for f in check(_verdict_project(tmp_path, conditions))] == [
        ("SCHEMA_INVALID_FIELD", "conditions")]
