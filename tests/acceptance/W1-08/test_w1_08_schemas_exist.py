"""Success 1: a JSON Schema exists for each of the eight record types [CAP-31.a, CAP-53.a]."""

from __future__ import annotations

import json

import pytest

import w1_08_support as support

SCHEMA_TYPES = sorted(support.SCHEMA_TYPES)


@pytest.mark.parametrize("record_type", SCHEMA_TYPES)
def test_a_schema_file_exists_for_the_record_type(record_type):
    support.schema_path(record_type)


@pytest.mark.parametrize("record_type", SCHEMA_TYPES)
def test_the_schema_file_is_a_json_object(record_type):
    path = support.schema_path(record_type)
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise AssertionError(f"{path.name} is not JSON: {exc}") from None
    assert isinstance(schema, dict), f"{path.name}: the top level is not a JSON object"


@pytest.mark.parametrize("record_type", SCHEMA_TYPES)
def test_the_schema_file_is_tracked_by_git(record_type):
    path = support.schema_path(record_type)
    assert f"{support.SCHEMAS_REL}/{path.name}" in support.tracked_files(), f"{path.name} is not committed"


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", SCHEMA_TYPES)
def test_the_schema_is_a_valid_json_schema(record_type, check):
    check.metaschema(support.schema_path(record_type))


def test_each_record_type_has_its_own_schema_file():
    paths = {record_type: support.schema_path(record_type) for record_type in SCHEMA_TYPES}
    assert len(set(paths.values())) == len(paths), (
        f"one file serves more than one record type: { {k: v.name for k, v in paths.items()} }")
