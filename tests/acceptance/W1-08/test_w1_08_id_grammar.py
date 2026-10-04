"""Failure 2: two schemas define the same id grammar differently.

DEC-227 makes that impossible by construction: one shared definitions file holds every id grammar under a fixed
name (`ticket_id`, `wbs_id`, `decision_id`, `lesson_id`, `record_id`), no other schema writes an id `pattern` of
its own, and the record schemas refer to the shared file. The patterns themselves are the engineer's; what is
tested is where they are written and that every record's `id` is governed by them.
"""

from __future__ import annotations

import json
import shutil

import pytest

import w1_08_support as support

# A property or a definition with one of these names holds an id, or a list of ids.
ID_NAMES = ("id", "supersedes", "superseded_by", "depends_on", "deps")
NOT_AN_ID = "w1-08 probe: not an id!"
# Ids this repository already uses: this ticket and its WBS number.
REAL_IDS = {"ticket_id": "DAEO-uudf", "wbs_id": "W1-08"}


def _holds_an_id(name):
    return name in ID_NAMES or name.endswith(("_id", "_ids")) or name in support.ID_GRAMMARS


def _has_pattern(value):
    if isinstance(value, dict):
        return isinstance(value.get("pattern"), str) or any(_has_pattern(item) for item in value.values())
    if isinstance(value, list):
        return any(_has_pattern(item) for item in value)
    return False


def _own_id_patterns(value, trail, found):
    """Collect the places where a schema writes a `pattern` under a property or a definition that holds an id."""
    if isinstance(value, dict):
        for keyword in ("properties",) + support.DEFINITION_KEYWORDS:
            block = value.get(keyword)
            if isinstance(block, dict):
                for name, subschema in block.items():
                    if isinstance(name, str) and _holds_an_id(name) and _has_pattern(subschema):
                        found.append("/".join(trail + (keyword, name)))
        for key, item in value.items():
            _own_id_patterns(item, trail + (str(key),), found)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _own_id_patterns(item, trail + (str(index),), found)
    return found


def test_the_five_id_grammars_are_defined_in_one_file_only():
    shared = support.shared_definitions_path()
    again = {}
    for path in support.kernel_json_files():
        if path != shared:
            names = [name for name in support.definitions(support.load_json(path)) if name in support.ID_GRAMMARS]
            if names:
                again[path.name] = names
    assert not again, f"an id grammar of {shared.name} is defined again in another schema: {again}"


@pytest.mark.local_only
@pytest.mark.parametrize("name", support.ID_GRAMMARS)
def test_the_shared_definition_is_a_grammar(name, check):
    """It refuses what no id is: the empty string, two lines, a number. The two grammars this repository already
    has ids for accept them."""
    schema = check.definition(support.shared_definitions_path(), name)
    for bad_id in ("", "two\nlines", 42, NOT_AN_ID):
        check.refuses(schema, bad_id, f"{bad_id!r} as a {name}")
    if name in REAL_IDS:
        check.accepts(schema, REAL_IDS[name], f"{REAL_IDS[name]} as a {name}")


def test_no_record_schema_writes_an_id_pattern_of_its_own():
    shared = support.shared_definitions_path()
    own = {}
    for record_type in sorted(support.SCHEMA_TYPES):
        path = support.schema_path(record_type)
        if path != shared:
            found = _own_id_patterns(support.load_json(path), (), [])
            if found:
                own[path.name] = found
    assert not own, f"a schema writes an id `pattern` of its own, outside {shared.name}: {own}"


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", sorted(support.RECORD_TYPES))
def test_the_id_of_the_record_is_governed_by_the_shared_grammar(record_type, check, tmp_path):
    """The record schema refuses an id that is no id. In a copy of the schemas folder whose five shared grammars
    are loosened to "any string", the same record is accepted: the grammar of the record's `id` is the shared one."""
    schema = support.schema_path(record_type)
    shared = support.shared_definitions_path()
    _, good = support.template(record_type)
    bad = support.replaced(good, "id", NOT_AN_ID)
    check.good(schema, good, f"the {record_type} template")
    check.refuses(schema, bad, f"a {record_type} record with id {NOT_AN_ID!r}")

    copy = tmp_path / "schemas"
    shutil.copytree(support.REPO_ROOT / support.SCHEMAS_REL, copy)
    loosened = support.load_json(shared)
    for name in support.ID_GRAMMARS:
        keyword, _ = support.definitions(loosened)[name]
        loosened[keyword][name] = {"type": "string"}
    (copy / shared.name).write_text(json.dumps(loosened, indent=2), encoding="utf-8")
    check.accepts(copy / schema.name, bad,
                  f"a {record_type} record with id {NOT_AN_ID!r}, although the shared id grammars accept any string "
                  f"(the schema has an id grammar of its own, or does not refer to {shared.name})")
