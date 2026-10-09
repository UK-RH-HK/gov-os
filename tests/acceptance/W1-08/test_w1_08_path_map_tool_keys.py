"""The path-map schema names the optional keys the tools read (DEC-554, point 6; the follow-up after W1-41, DEC-569).

DEC-554, point 6: "The kernel's path-map schema names neither key, nor DEC-479's two: it goes to the follow-up
after W1-41 with DEC-521's items".

The five keys, each an optional top-level key of ``governance/project/path-map.yaml``, with the shape the tool
that reads it accepts:

- ``close_timeout`` (DEC-554): the time limit of a test run of ``gov close``, a positive number of seconds.
- ``close_workers`` (DEC-549, DEC-554): the number of workers of a parallel test run, a positive whole number,
  or the word ``auto``.
- ``decision_register`` (DEC-479): the project's register file, a path from the project's root, text that is
  not empty.
- ``decision_citations_base`` (DEC-479): the base commit of the decision-citations check, a commit id, full or
  abbreviated, as text.
- ``trailers_base`` (DEC-482; the name W1-30's suite proposed in its round 13, settlement 31): the base commit
  of the trailers check, a commit id, full or abbreviated, as text.

What the cases hold: a path map with each key in a valid shape validates; a key in a wrong shape is refused; a
path map without the keys validates as today; no key is required; a top-level key the schema does not know is
no finding, as today.

The path map of these cases is a fixture: the required systems are read from the schema, nothing is read from
this repository's own path map.
"""

from __future__ import annotations

import pytest

import w1_08_support as support

FULL_ID = "0123456789abcdef0123456789abcdef01234567"
SHORT_ID = "0123abcd"

# key -> (valid values, wrong values by what they are)
KEYS = {
    "close_timeout": (
        {"a whole number": 7200, "a fraction": 90.5},
        {"zero": 0, "a negative number": -5, "a word": "soon", "a number in quotes": "7200", "a truth value": True,
         "a list": [60], "no value": None},
    ),
    "close_workers": (
        {"a whole number": 4, "one": 1, "auto": "auto"},
        {"zero": 0, "a negative number": -2, "a fraction": 1.5, "a word": "many", "a number in quotes": "4",
         "another spelling of auto": "AUTO", "a truth value": True, "an empty text": "", "no value": None},
    ),
    "decision_register": (
        {"a path": "records/decision-log.md"},
        {"an empty text": "", "a list": ["records/decision-log.md"], "a number": 7, "a truth value": True,
         "no value": None},
    ),
    "decision_citations_base": (
        {"the full id": FULL_ID, "an abbreviated id": SHORT_ID},
        {"an empty text": "", "a number": 1234567, "a name that is no commit id": "main", "a list": [FULL_ID],
         "a truth value": True, "no value": None},
    ),
    "trailers_base": (
        {"the full id": FULL_ID, "an abbreviated id": SHORT_ID},
        {"an empty text": "", "a number": 1234567, "a name that is no commit id": "main", "a list": [FULL_ID],
         "a truth value": True, "no value": None},
    ),
}


def _schema():
    return support.schema_path("path-map")


def _plain():
    """A path map that is valid under the kernel's schema and holds none of the five keys."""
    schema = support.load_json(_schema())
    systems = schema["properties"]["systems"]["required"]
    policies = {"security": "hard-block", "authority": "hard-block", "test": "hard-block", "change": "hard-block",
                "human_gate": "hard-block", "tool": "hard-block", "memory": "warning", "context": "warning",
                "checkpoint": "warning", "model_routing": "informational", "budget": "informational",
                "learning": "informational", "archive": "informational"}
    return {
        "state_class": "AUTHORITATIVE",
        "namespaces": {"all": {
            "paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
            "permitted_roles": ["engineer"], "retention": "permanent", "export_policy": "allowed",
            "embedding_policy": "not embedded", "provenance": "fixture", "deletion_rebuild": "from git"}},
        "capabilities": {"code_intelligence": {"enabled": False}, "research_corpus": {"enabled": False}},
        "policies": policies,
        "systems": {name: {"status": "absent", "reason": "a fixture"} for name in systems},
    }


def _with(**entries):
    return {**_plain(), **entries}


# --- red until the schema names the keys ------------------------------------------------------------------------

@pytest.mark.parametrize("key", sorted(KEYS))
def test_the_path_map_schema_names_the_optional_key(key):
    """A reader of the schema finds the key among the top-level properties, with a description of what it is."""
    schema = support.load_json(_schema())
    named = schema.get("properties", {})
    assert key in named, f"{_schema().name} does not name the key `{key}` (top-level keys named: {sorted(named)})"
    assert isinstance(named[key], dict) and str(named[key].get("description", "")).strip(), \
        f"{_schema().name} names `{key}` without a description"


@pytest.mark.local_only
@pytest.mark.parametrize("key", sorted(KEYS))
def test_an_optional_key_in_a_wrong_shape_is_refused(key, check):
    schema = _schema()
    valid, wrong = KEYS[key]
    check.good(schema, _with(**{key: next(iter(valid.values()))}), f"a path map with `{key}` in a valid shape")
    check.refuses_each(schema, {what: _with(**{key: value}) for what, value in wrong.items()},
                       f"a path map whose `{key}` is")


# --- what stays (green today) -----------------------------------------------------------------------------------

@pytest.mark.local_only
def test_a_path_map_without_the_optional_keys_validates_as_before(check):
    check.accepts(_schema(), _plain(), "a path map with none of the five keys")


@pytest.mark.local_only
@pytest.mark.parametrize("key", sorted(KEYS))
def test_an_optional_key_in_a_valid_shape_validates(key, check):
    valid, _ = KEYS[key]
    check.accepts_all(_schema(), {f"value-{index}": _with(**{key: value})
                                  for index, value in enumerate(valid.values())},
                      f"a path map with `{key}` in a valid shape ({sorted(valid)})")


@pytest.mark.local_only
def test_a_path_map_with_all_five_keys_validates(check):
    entries = {key: next(iter(valid.values())) for key, (valid, _) in KEYS.items()}
    check.accepts(_schema(), _with(**entries), "a path map with the five keys")


def test_no_optional_key_is_required():
    required = support.load_json(_schema()).get("required", [])
    asked = sorted(key for key in KEYS if key in required)
    assert not asked, f"{_schema().name} requires {asked}: a project that writes none of them is refused"


@pytest.mark.local_only
def test_a_top_level_key_the_schema_does_not_know_is_no_finding_as_before(check):
    """As it is today: the schema does not close the top level, and this piece does not change that."""
    check.accepts(_schema(), _with(a_setting_of_a_later_ticket=1), "a path map with an unknown top-level key")
