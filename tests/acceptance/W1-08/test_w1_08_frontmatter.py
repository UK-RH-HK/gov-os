"""The shared frontmatter.

Success 6: it records `state_class` for every record type [CAP-07.b]. The six values are held once, in the shared
definitions file, and every record schema accepts all six (DEC-229).
Success 3, second part: the artefact identity fields are in the shared frontmatter or derived by gov [CAP-50.a].
`id`, `type` and `status` are required; `lifecycle`, `version`, `provenance`, `supersedes`, `superseded_by` and
`consumers` are optional; the canonical path and `content_hash` are derived, not stored (DEC-239).
"""

from __future__ import annotations

import pytest

import w1_08_support as support

RECORD_TYPES = sorted(support.RECORD_TYPES)
REQUIRED_IDENTITY = ("id", "type", "status")
OPTIONAL_IDENTITY = ("lifecycle", "version", "provenance", "supersedes", "superseded_by", "consumers")
DERIVED_BY_GOV = ("content_hash", "canonical_path", "path")
# DEC-229: what the template of each record type carries. The schemas do not pin these.
DEFAULT_STATE_CLASS = {
    "decision": "AUTHORITATIVE",
    "ticket": "AUTHORITATIVE",
    "lesson": "AUTHORITATIVE",
    "gate": "AUTHORITATIVE",
    "failure": "EVIDENCE",
    "research": "EVIDENCE",
    "checkpoint": "NARRATIVE",
}


# --- state_class [CAP-07.b] -------------------------------------------------------------------------------------

@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_the_template_records_the_state_class_of_its_record_type(record_type):
    path, good = support.template(record_type)
    assert good.get("state_class") == DEFAULT_STATE_CLASS[record_type], (
        f"{path.name}: `state_class` is {good.get('state_class')!r}, not {DEFAULT_STATE_CLASS[record_type]}")


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_a_record_without_a_state_class_is_refused(record_type, check):
    schema = support.schema_path(record_type)
    _, good = support.template(record_type)
    assert "state_class" in good, f"the {record_type} template has no `state_class`"
    check.good(schema, good, f"the {record_type} template")
    check.refuses(schema, support.without(good, "state_class"), f"a {record_type} record without `state_class`")


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_the_six_state_classes_are_accepted_and_no_other(record_type, check):
    """Every record schema accepts all six: the template's value is a default, not a rule of the schema."""
    schema = support.schema_path(record_type)
    _, good = support.template(record_type)
    for value in support.STATE_CLASSES:
        check.accepts(schema, support.replaced(good, "state_class", value),
                      f"a {record_type} record whose `state_class` is {value}")
    for value in ("OFFICIAL", "authoritative", None):
        check.refuses(schema, support.replaced(good, "state_class", value),
                      f"a {record_type} record whose `state_class` is {value!r}")


@pytest.mark.local_only
def test_the_shared_definitions_file_holds_the_six_state_classes(check):
    schema = check.definition(support.shared_definitions_path(), "state_class")
    for value in support.STATE_CLASSES:
        check.accepts(schema, value, f"the state class {value}")
    for value in ("OFFICIAL", "", None):
        check.refuses(schema, value, f"{value!r} as a state class")


def test_the_state_classes_are_written_in_one_schema_file_only():
    """Held once (DEC-229): no schema of a record type lists the values again. One value alone (a `default`) is
    not a list."""
    shared = support.shared_definitions_path()
    again = []
    for record_type in sorted(support.SCHEMA_TYPES):
        path = support.schema_path(record_type)
        text = path.read_text(encoding="utf-8")
        if path != shared and sum(f'"{value}"' in text for value in support.STATE_CLASSES) > 1:
            again.append(path.name)
    assert not again, f"the `state_class` values are written again, outside {shared.name}, in {again}"


# --- identity fields [CAP-50.a] ---------------------------------------------------------------------------------

@pytest.mark.local_only
@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_a_record_without_id_type_or_status_is_refused(record_type, check):
    schema = support.schema_path(record_type)
    path, good = support.template(record_type)
    missing = [field for field in REQUIRED_IDENTITY if field not in good]
    assert not missing, f"{path.name} has no {missing}"
    check.good(schema, good, f"the {record_type} template")
    for field in REQUIRED_IDENTITY:
        check.refuses(schema, support.without(good, field), f"a {record_type} record without `{field}`")


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_the_optional_identity_fields_are_defined_and_optional(record_type, check):
    """The schema knows each of the six: a value of no plausible kind (a boolean) is refused. None of them is
    required: the template without them is still a valid record. A field the record type itself requires (the
    lesson's lifecycle state, CAP-41.a) stays in."""
    schema = support.schema_path(record_type)
    _, good = support.template(record_type)
    check.good(schema, good, f"the {record_type} template")
    for field in OPTIONAL_IDENTITY:
        check.refuses(schema, support.replaced(good, field, True), f"a {record_type} record whose `{field}` is true")
    bare = dict(good)
    for field in OPTIONAL_IDENTITY:
        if not (record_type == "lesson" and field == "lifecycle"):
            bare.pop(field, None)
    check.accepts(schema, bare, f"a {record_type} record without the optional identity fields")


@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_no_template_stores_what_gov_derives(record_type):
    """The canonical path and the content hash are derived by gov, not stored in the record (DEC-239)."""
    for path in support.template_paths(record_type):
        stored = [key for key in DERIVED_BY_GOV if key in support.load_record(path)]
        assert not stored, f"{path.name} stores {stored}, which gov derives"
