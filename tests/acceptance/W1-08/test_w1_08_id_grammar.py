"""Failure 2: two schemas define the same id grammar differently.

What is tested is the part that needs no list of shared grammars: a definition that two schema files of the kernel
carry under the same name (`$defs` or `definitions`) is the same definition in both, and a schema file does not
define one property name with two different patterns. Which grammars the schemas share by meaning (a ticket id
used in another record, a decision id in a `supersedes` list) is decision package DP-6 in the README.
"""

from __future__ import annotations

import json

import pytest

import w1_08_support as support


def _schemas():
    """``file name -> schema`` for every schema file of the kernel, once the eight W1-08 schemas exist."""
    for record_type in sorted(support.SCHEMA_TYPES):
        support.schema_path(record_type)
    loaded = {}
    for path in support.schema_files():
        try:
            loaded[path.name] = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise AssertionError(f"{path.name} is not JSON: {exc}") from None
    return loaded


def _definitions(schema):
    found = {}
    for keyword in ("$defs", "definitions"):
        block = schema.get(keyword) if isinstance(schema, dict) else None
        if isinstance(block, dict):
            found.update(block)
    return found


def _strip_annotations(value):
    """A definition without its annotations, so that two differ only when they validate differently."""
    if isinstance(value, dict):
        return {key: _strip_annotations(item) for key, item in value.items()
                if key not in ("title", "description", "$comment", "examples")}
    if isinstance(value, list):
        return [_strip_annotations(item) for item in value]
    return value


def _patterns_by_property(value, found):
    """Collect ``property name -> set of patterns`` from every ``properties`` map inside ``value``."""
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            for name, subschema in properties.items():
                if isinstance(subschema, dict) and isinstance(subschema.get("pattern"), str):
                    found.setdefault(name, set()).add(subschema["pattern"])
        for item in value.values():
            _patterns_by_property(item, found)
    elif isinstance(value, list):
        for item in value:
            _patterns_by_property(item, found)
    return found


def test_a_definition_shared_by_name_is_the_same_in_every_schema():
    schemas = _schemas()
    by_name = {}
    for file_name, schema in schemas.items():
        for name, definition in _definitions(schema).items():
            by_name.setdefault(name, []).append((file_name, _strip_annotations(definition)))
    different = {}
    for name, entries in by_name.items():
        first = entries[0][1]
        if any(definition != first for _, definition in entries[1:]):
            different[name] = [file_name for file_name, _ in entries]
    assert not different, f"the same definition name is defined differently in two schemas: {different}"


def test_no_schema_gives_one_property_two_grammars():
    schemas = _schemas()
    different = {}
    for file_name, schema in schemas.items():
        for name, patterns in _patterns_by_property(schema, {}).items():
            if len(patterns) > 1:
                different[f"{file_name}: {name}"] = sorted(patterns)
    assert not different, f"one property has two different patterns inside one schema: {different}"


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", sorted(support.RECORD_TYPES))
@pytest.mark.parametrize("bad_id", ("", "two\nlines", 42, None))
def test_the_id_of_every_record_type_follows_a_grammar(record_type, bad_id, check):
    """An id has a grammar at all: no record schema accepts an id that is empty, holds a line break or is no string."""
    schema = support.schema_path(record_type)
    _, good = support.template(record_type)
    check.accepts(schema, good, f"the {record_type} template")
    check.refuses(schema, support.replaced(good, "id", bad_id), f"a {record_type} record with id {bad_id!r}")
