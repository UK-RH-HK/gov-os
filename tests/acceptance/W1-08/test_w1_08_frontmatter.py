"""The shared frontmatter.

Success 6: it records `state_class` for every record type [CAP-07.b].
Success 3, second part: the artefact identity fields are in it [CAP-50.a]. Only `id`, `type` and `status` are
tested: the item names them in those words and the committed records already use those keys. The names of the
other identity fields are decision package DP-3 in the README.
"""

from __future__ import annotations

import pytest

import w1_08_support as support

RECORD_TYPES = sorted(support.RECORD_TYPES)
IDENTITY_FIELDS = ("id", "type", "status")


@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_the_template_records_a_state_class(record_type):
    path, good = support.template(record_type)
    value = good.get("state_class")
    assert isinstance(value, str) and value.strip(), f"{path.name}: `state_class` is {value!r}"


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_a_record_without_a_state_class_is_refused(record_type, check):
    schema = support.schema_path(record_type)
    _, good = support.template(record_type)
    assert "state_class" in good, f"the {record_type} template has no `state_class`"
    check.accepts(schema, good, f"the {record_type} template")
    check.refuses(schema, support.without(good, "state_class"), f"a {record_type} record without `state_class`")


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", RECORD_TYPES)
@pytest.mark.parametrize("value", (None, 42, ""))
def test_a_state_class_that_is_not_a_word_is_refused(record_type, value, check):
    schema = support.schema_path(record_type)
    _, good = support.template(record_type)
    check.accepts(schema, good, f"the {record_type} template")
    check.refuses(schema, support.replaced(good, "state_class", value),
                  f"a {record_type} record whose `state_class` is {value!r}")


@pytest.mark.parametrize("record_type", RECORD_TYPES)
@pytest.mark.parametrize("field", IDENTITY_FIELDS)
def test_the_template_carries_the_identity_field(record_type, field):
    path, good = support.template(record_type)
    assert field in good, f"{path.name} has no `{field}`"


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", RECORD_TYPES)
@pytest.mark.parametrize("field", IDENTITY_FIELDS)
def test_a_record_without_the_identity_field_is_refused(record_type, field, check):
    schema = support.schema_path(record_type)
    _, good = support.template(record_type)
    assert field in good, f"the {record_type} template has no `{field}`"
    check.accepts(schema, good, f"the {record_type} template")
    check.refuses(schema, support.without(good, field), f"a {record_type} record without `{field}`")
