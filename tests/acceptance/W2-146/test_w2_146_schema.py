"""KPI S1 and failure 3 (schema): the path map may declare ``id_forms``; the schema accepts the list and refuses an
entry with no name, no pattern, or a pattern that does not compile (DEC-1071 (5), DEC-1099 (2)).

Interface 1: an optional top-level ``id_forms``, an array (may be empty) of ``{name, pattern}`` objects with no other
key, ``name`` a non-empty string, ``pattern`` a non-empty string with the ``regex`` format; "does not compile" is judged
by ``Draft202012Validator(schema, format_checker=FormatChecker())``. Nothing else in the schema changes.

A planted path map (``w2_146_support.valid_path_map``) is validated; one case per malformed entry.
"""

from __future__ import annotations

import yaml

import pytest

import w2_146_support as support

GOOD = [{"name": "request", "pattern": "req[0-9]+"}, {"name": "ticket", "pattern": "TKT_[0-9]+"}]


def errors(document):
    return sorted(support.schema_validator().iter_errors(document), key=lambda error: list(error.path))


def refused(document):
    found = errors(document)
    assert found, f"the schema accepted a path map it must refuse: {document.get('id_forms')!r}"
    return found


def test_s1_premise_the_planted_path_map_without_id_forms_is_valid():
    assert errors(support.valid_path_map()) == []


def test_s1_the_repository_own_path_map_is_still_valid():
    """Nothing else in the schema changes (Interface 1): this repository's own map stays valid."""
    document = yaml.safe_load(support.OWN_PATH_MAP.read_text(encoding="utf-8"))
    assert errors(document) == []


def test_s1_a_map_with_two_well_formed_forms_is_accepted():
    assert errors(support.valid_path_map(id_forms=GOOD)) == []


def test_s1_the_five_planted_forms_are_accepted():
    assert errors(support.valid_path_map(id_forms=support.declared())) == []


def test_s1_an_empty_list_of_forms_is_accepted():
    assert errors(support.valid_path_map(id_forms=[])) == []


def test_s1_a_form_with_no_name_is_refused():
    found = refused(support.valid_path_map(id_forms=[GOOD[0], {"pattern": "TKT_[0-9]+"}]))
    assert any(list(error.path)[:1] == ["id_forms"] for error in found), [error.message for error in found]


def test_s1_a_form_with_no_pattern_is_refused():
    found = refused(support.valid_path_map(id_forms=[GOOD[0], {"name": "ticket"}]))
    assert any(list(error.path)[:1] == ["id_forms"] for error in found), [error.message for error in found]


def test_s1_a_form_whose_pattern_does_not_compile_is_refused():
    found = refused(support.valid_path_map(id_forms=[GOOD[0], {"name": "broken", "pattern": "("}]))
    assert any(list(error.path)[:1] == ["id_forms"] for error in found), [error.message for error in found]


def test_s1_a_form_whose_pattern_is_an_empty_string_is_refused():
    refused(support.valid_path_map(id_forms=[{"name": "empty", "pattern": ""}]))


def test_s1_a_form_whose_name_is_an_empty_string_is_refused():
    refused(support.valid_path_map(id_forms=[{"name": "", "pattern": "req[0-9]+"}]))


def test_s1_the_map_with_a_nameless_a_patternless_and_a_non_compiling_form_is_refused_each_time():
    """Failure 3's planted map, one malformed form at a time: each makes the whole map invalid."""
    for bad in ({"pattern": "TKT_[0-9]+"}, {"name": "ticket"}, {"name": "broken", "pattern": "("}):
        refused(support.valid_path_map(id_forms=[*GOOD, bad]))


def test_s1_a_form_with_a_pattern_that_is_not_text_is_refused():
    refused(support.valid_path_map(id_forms=[{"name": "number", "pattern": 5}]))


def test_s1_a_form_with_a_key_beside_name_and_pattern_is_refused():
    """Interface 1: the entry is closed (``additionalProperties: false``)."""
    refused(support.valid_path_map(id_forms=[{"name": "request", "pattern": "req[0-9]+", "flags": "i"}]))


def test_s1_id_forms_that_is_no_list_is_refused():
    refused(support.valid_path_map(id_forms={"request": "req[0-9]+"}))
