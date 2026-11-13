"""KPI S2 and failure 3 (the reader): ``gov.retrieval.lexical.ids_in`` reads a token of any declared form as an id,
whole, once and in order, beside the built-in shape's ids; with no form its result is today's (DEC-1071 (5),
DEC-1099 (2)).

Interfaces 2 and 3: ``id_forms(root) -> tuple[re.Pattern, ...]`` reads only ``id_forms`` of
``<root>/governance/project/path-map.yaml`` (no file, no key or ``[]``: ``()``; a malformed entry: ``GovError``
``CONFIG_INVALID`` naming ``id_forms[<i>]``); ``ids_in(text, forms=())`` with forms keeps a form's match only when
non-empty and a whole token, drops a candidate that overlaps one already kept (by start, the longest first), and gives
each text once in order of position. Every case imports ``gov.retrieval.lexical`` inside the test, so the folder
collects before the reader exists.

Five planted forms the built-in shape does not read: no hyphen, lowercase, underscore, a dotted suffix, a space.
"""

from __future__ import annotations

import re

import pytest

import w2_146_support as support

FORMS = support.FORM_NAMES
BUILT_IN = ("DEC-12", "QX-4471")


def lexical():
    from gov.retrieval import lexical as module

    return module


def read_forms(tmp_path, *names):
    """``lexical.id_forms`` of a planted path map holding only the named planted forms (all when none is named)."""
    support.plant_id_forms_only(tmp_path, support.declared(*names))
    return lexical().id_forms(tmp_path)


def text_with(token):
    """The token twice, between the built-in shape's ids."""
    return f"First {BUILT_IN[0]} then {token} and again {token}, last {BUILT_IN[1]}."


# ---- S2: each form read when declared and not read when not -------------------------------------------------------

@pytest.mark.parametrize("name", FORMS)
def test_s2_a_declared_form_is_read_whole_once_in_order_beside_the_built_in_ids(tmp_path, name):
    token = support.FORMS[name]["missing"]
    forms = read_forms(tmp_path, name)
    assert lexical().ids_in(text_with(token), forms) == [BUILT_IN[0], token, BUILT_IN[1]]


@pytest.mark.parametrize("name", FORMS)
def test_s2_a_form_that_is_not_declared_is_not_read(name):
    token = support.FORMS[name]["missing"]
    text = text_with(token)
    assert token not in lexical().ids_in(text)
    assert token not in lexical().ids_in(text, ())


@pytest.mark.parametrize("name", FORMS)
def test_s2_a_declared_form_is_read_in_its_own_text_alone(tmp_path, name):
    token = support.FORMS[name]["missing"]
    assert lexical().ids_in(f"What does {token} decide?", read_forms(tmp_path, name)) == [token]


def test_s2_all_five_forms_declared_are_read_in_order_of_position(tmp_path):
    tokens = [support.FORMS[name]["missing"] for name in ("spaced", "lowercase", "dotted", "no-hyphen", "underscore")]
    text = f"{tokens[0]}, then {BUILT_IN[0]}; {tokens[1]} / {tokens[2]} and {tokens[3]} ({tokens[4]}) {BUILT_IN[1]}"
    assert lexical().ids_in(text, read_forms(tmp_path)) == [tokens[0], BUILT_IN[0], tokens[1], tokens[2], tokens[3],
                                                           tokens[4], BUILT_IN[1]]


def test_s2_a_token_read_by_two_forms_is_read_once(tmp_path):
    support.plant_id_forms_only(tmp_path, [{"name": "one", "pattern": "req[0-9]+"},
                                           {"name": "two", "pattern": "r[a-z]q[0-9]+"}])
    assert lexical().ids_in("Is req12 open? req12 is.", lexical().id_forms(tmp_path)) == ["req12"]


# ---- S2: the whole-token rule --------------------------------------------------------------------------------------

DECORATIONS = {"a word character before": "x{}", "a word character after": "{}x", "a hyphen before": "pre-{}",
               "a hyphen and a word character after": "{}-b", "an underscore before": "_{}"}


@pytest.mark.parametrize("decoration", list(DECORATIONS))
@pytest.mark.parametrize("name", FORMS)
def test_s2_a_token_of_a_declared_form_inside_a_longer_word_is_not_read(tmp_path, name, decoration):
    token = support.FORMS[name]["missing"]
    text = f"The note {DECORATIONS[decoration].format(token)} is nothing."
    assert token not in lexical().ids_in(text, read_forms(tmp_path, name))


@pytest.mark.parametrize("wrap", ["({})", "{}.", "{},", "[{}]", '"{}"', "{}:"], ids=["parens", "stop", "comma", "brackets",
                                                                                      "quotes", "colon"])
@pytest.mark.parametrize("name", FORMS)
def test_s2_a_declared_token_bounded_by_punctuation_is_read(tmp_path, name, wrap):
    token = support.FORMS[name]["missing"]
    assert token in lexical().ids_in(f"See {wrap.format(token)} now", read_forms(tmp_path, name))


# ---- S2: overlap (Interface 3) --------------------------------------------------------------------------------------

def test_s2_under_a_dotted_form_the_dotted_id_is_read_whole_not_its_fragment(tmp_path):
    forms = read_forms(tmp_path, "dotted")
    text = f"See {support.FRAGMENT_QUESTION_ID} for details."
    assert lexical().ids_in(text, forms) == [support.FRAGMENT_QUESTION_ID]
    assert lexical().ids_in(text) == [support.FRAGMENT_HELD]  # today's reader: the fragment alone


def test_s2_the_fragment_and_the_dotted_id_apart_in_one_text_are_both_read(tmp_path):
    forms = read_forms(tmp_path, "dotted")
    text = f"{support.FRAGMENT_HELD} is filed; {support.FRAGMENT_QUESTION_ID} is not."
    assert lexical().ids_in(text, forms) == [support.FRAGMENT_HELD, support.FRAGMENT_QUESTION_ID]


# ---- S2 / failure 3: byte-identical with no form declared -----------------------------------------------------------

TEXTS = {
    "empty": "",
    "no id": "What does the harbour decide about the tide?",
    "ids": "DEC-12 and RETR-X-02, W2-13 then W2-M071; DEC-12 again; QX-4471.",
    "no digit": "ABC-DEF, A-B and PLAIN-TEXT hold no digit",
    "a trailing hyphen": "DEC-12- and W2-13-b, and DEC-123.",
    "lower case": "dec-12 is no id, and neither is Dec-12; but ADR-0404 is.",
    "a heading": "## DEC-1099 (2): the reader\n\nSee DEC-1071 (5) and AR-9.",
    "a line of code": "assert ids_in('K-1 K-2') == ['K-1', 'K-2']  # K-1 twice",
}


@pytest.mark.parametrize("which", list(TEXTS))
def test_s2_with_no_form_the_result_is_todays_expression(which):
    text = TEXTS[which]
    assert lexical().ids_in(text) == support.today_ids(text)


@pytest.mark.parametrize("which", list(TEXTS))
def test_s2_the_same_list_with_forms_that_match_nothing_in_the_text(tmp_path, which):
    text = TEXTS[which]
    forms = read_forms(tmp_path)
    assert not any(form.search(text) for form in forms), "premise: a planted form matches the text"
    assert lexical().ids_in(text, forms) == lexical().ids_in(text) == support.today_ids(text)


@pytest.mark.parametrize("which", list(TEXTS))
def test_s2_the_same_list_with_an_empty_tuple_of_forms(which):
    text = TEXTS[which]
    assert lexical().ids_in(text, ()) == support.today_ids(text)


def test_s2_the_built_in_shape_is_always_read_beside_declared_forms(tmp_path):
    forms = read_forms(tmp_path)
    assert lexical().ids_in(TEXTS["ids"], forms) == ["DEC-12", "RETR-X-02", "W2-13", "W2-M071", "QX-4471"]
    assert lexical().ID_SHAPE.pattern == r"\b[A-Z][A-Z0-9]*(?:-[A-Za-z0-9]+)+\b"


# ---- Interface 2: reading the forms ---------------------------------------------------------------------------------

def test_s2_no_path_map_gives_no_forms(tmp_path):
    assert lexical().id_forms(tmp_path) == ()


def test_s2_a_path_map_with_no_id_forms_key_gives_no_forms(tmp_path):
    support.write(tmp_path, support.PATH_MAP_REL, "state_class: AUTHORITATIVE\n")
    assert lexical().id_forms(tmp_path) == ()


def test_s2_an_empty_id_forms_list_gives_no_forms(tmp_path):
    support.plant_id_forms_only(tmp_path, [])
    assert lexical().id_forms(tmp_path) == ()


def test_s2_the_forms_are_compiled_patterns_in_the_order_declared(tmp_path):
    forms = read_forms(tmp_path, "spaced", "lowercase")
    assert isinstance(forms, tuple) and all(isinstance(form, re.Pattern) for form in forms)
    assert [form.pattern for form in forms] == [support.FORMS["spaced"]["pattern"], support.FORMS["lowercase"]["pattern"]]


def test_s2_a_declared_pattern_is_case_sensitive(tmp_path):
    forms = read_forms(tmp_path, "lowercase")
    assert lexical().ids_in("Is REQ12 open? Is Req12?", forms) == []


def test_s2_inline_flags_at_the_start_of_a_pattern_are_the_repositorys(tmp_path):
    support.plant_id_forms_only(tmp_path, [{"name": "request", "pattern": "(?i)req[0-9]+"}])
    assert lexical().ids_in("Is REQ12 open? Is req13?", lexical().id_forms(tmp_path)) == ["REQ12", "req13"]


def test_s2_a_pattern_that_matches_nothing_in_a_text_reads_nothing(tmp_path):
    support.plant_id_forms_only(tmp_path, [{"name": "optional", "pattern": "x*"}])
    assert lexical().ids_in("A plain text.", lexical().id_forms(tmp_path)) == []


# ---- Interface 2: a malformed form is loud ---------------------------------------------------------------------------

MALFORMED = {
    "an entry that is not a map": "ABC[0-9]+",
    "an entry with no name": {"pattern": "ABC[0-9]+"},
    "an entry with no pattern": {"name": "request"},
    "an entry with an empty name": {"name": "", "pattern": "ABC[0-9]+"},
    "an entry with an empty pattern": {"name": "request", "pattern": ""},
    "an entry whose pattern is not text": {"name": "request", "pattern": 5},
    "an entry whose name is not text": {"name": 5, "pattern": "ABC[0-9]+"},
    "a pattern that does not compile": {"name": "broken", "pattern": "("},
}


@pytest.mark.parametrize("which", list(MALFORMED))
def test_s2_a_malformed_entry_is_a_config_invalid_error_naming_it(tmp_path, which):
    from gov.cli.errors import GovError

    support.plant_id_forms_only(tmp_path, [{"name": "good", "pattern": "ABC[0-9]+"}, MALFORMED[which]])
    with pytest.raises(GovError) as raised:
        lexical().id_forms(tmp_path)
    assert raised.value.code == "CONFIG_INVALID"
    assert "id_forms[1]" in raised.value.message, raised.value.message
    assert "id_forms[0]" not in raised.value.message, raised.value.message


def test_s2_a_malformed_first_entry_names_index_zero(tmp_path):
    from gov.cli.errors import GovError

    support.plant_id_forms_only(tmp_path, [{"name": "broken", "pattern": "("}, {"name": "good", "pattern": "ABC[0-9]+"}])
    with pytest.raises(GovError) as raised:
        lexical().id_forms(tmp_path)
    assert raised.value.code == "CONFIG_INVALID" and "id_forms[0]" in raised.value.message
