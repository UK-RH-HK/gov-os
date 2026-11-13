"""Builder tests for the declared id forms (W2-146; DEC-1071 (5), DEC-1099 (2)).

Regression evidence only (DEC-136). The path map may declare ``id_forms`` (a name and a regular expression each);
``lexical.id_forms(root)`` reads them, ``lexical.ids_in(text, forms)`` reads a token of any of them as an id, whole,
once and in order, beside the built-in shape. With no form declared the result is today's. Every id here is invented
and planted in a temporary folder.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.retrieval import lexical  # noqa: E402

SCHEMAS = REPO / "template/governance/kernel/schemas"

# five forms the built-in shape does not read: no hyphen, lowercase, underscore, dotted suffix, a space
FORMS = [
    {"name": "bare", "pattern": r"ZQ\d+"},
    {"name": "lower", "pattern": r"bug\d+"},
    {"name": "under", "pattern": r"[A-Z]{2}_\d+"},
    {"name": "dotted", "pattern": r"[A-Z]+-\d+(?:\.\d+)+"},
    {"name": "spaced", "pattern": r"PX \d+"},
]
TOKENS = {"bare": "ZQ41", "lower": "bug7", "under": "KV_12", "dotted": "SPEC-4.2", "spaced": "PX 41"}


def _plant(root: Path, forms=None, **more) -> Path:
    (root / "governance/project").mkdir(parents=True, exist_ok=True)
    document = {**more} if forms is None else {"id_forms": forms, **more}
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(document), encoding="utf-8")
    return root


# ---- the schema (S1) ------------------------------------------------------------------------------------------------

def _validator():
    import jsonschema

    documents = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in SCHEMAS.glob("*.json")}
    store = {**documents, **{each["$id"]: each for each in documents.values() if "$id" in each}}
    schema = documents["path-map.schema.json"]
    resolver = jsonschema.RefResolver(base_uri=schema.get("$id", ""), referrer=schema, store=store)
    return jsonschema.Draft202012Validator(schema, resolver=resolver, format_checker=jsonschema.FormatChecker())


def _repo_map(**more) -> dict:
    document = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    document.pop("id_forms", None)
    return {**document, **more}


def test_the_repository_map_is_valid_without_forms():
    assert list(_validator().iter_errors(_repo_map())) == []


@pytest.mark.parametrize("forms", [[], FORMS, FORMS[:2]], ids=["empty", "five", "two"])
def test_the_schema_accepts_declared_forms(forms):
    assert list(_validator().iter_errors(_repo_map(id_forms=forms))) == []


@pytest.mark.parametrize("entry", [
    {"pattern": r"ZQ\d+"},                       # no name
    {"name": "bare"},                            # no pattern
    {"name": "bare", "pattern": "ZQ(\\d+"},      # does not compile
    {"name": "bare", "pattern": ""},             # empty pattern
    {"name": "", "pattern": r"ZQ\d+"},           # empty name
    {"name": "bare", "pattern": r"ZQ\d+", "flags": "i"},  # a key the entry does not hold
    "ZQ\\d+",                                    # not a map
], ids=["nameless", "patternless", "non-compiling", "empty-pattern", "empty-name", "extra-key", "not-a-map"])
def test_the_schema_refuses_a_malformed_form(entry):
    assert list(_validator().iter_errors(_repo_map(id_forms=[FORMS[0], entry])))


def test_the_schema_refuses_forms_that_are_no_list():
    assert list(_validator().iter_errors(_repo_map(id_forms={"name": "bare", "pattern": r"ZQ\d+"})))


# ---- reading the forms ----------------------------------------------------------------------------------------------

def test_no_file_no_key_and_an_empty_list_declare_nothing(tmp_path):
    assert lexical.id_forms(tmp_path) == ()
    assert lexical.id_forms(_plant(tmp_path / "a", None, state_class="x")) == ()
    assert lexical.id_forms(_plant(tmp_path / "b", [])) == ()


def test_the_declared_forms_are_compiled_in_order_with_no_flags(tmp_path):
    forms = lexical.id_forms(_plant(tmp_path, FORMS))
    assert [form.pattern for form in forms] == [entry["pattern"] for entry in FORMS]
    assert all(isinstance(form, re.Pattern) and form.flags == re.compile("").flags for form in forms)
    assert forms[0].search("zq41") is None  # case-sensitive


@pytest.mark.parametrize("entry, reason", [
    ("ZQ\\d+", "not a map"),
    ({"pattern": r"ZQ\d+"}, "name"),
    ({"name": "", "pattern": r"ZQ\d+"}, "name"),
    ({"name": 3, "pattern": r"ZQ\d+"}, "name"),
    ({"name": "bare"}, "pattern"),
    ({"name": "bare", "pattern": ""}, "pattern"),
    ({"name": "bare", "pattern": 7}, "pattern"),
    ({"name": "bare", "pattern": "ZQ(\\d+"}, "compile"),
], ids=["not-a-map", "nameless", "empty-name", "name-number", "patternless", "empty-pattern", "pattern-number",
        "non-compiling"])
def test_a_malformed_form_is_config_invalid_naming_its_index(tmp_path, entry, reason):
    with pytest.raises(GovError) as raised:
        lexical.id_forms(_plant(tmp_path, [FORMS[0], entry]))
    assert raised.value.code == "CONFIG_INVALID"
    assert "id_forms[1]" in raised.value.message and reason in raised.value.message, raised.value.message


def test_forms_that_are_no_list_are_config_invalid(tmp_path):
    with pytest.raises(GovError) as raised:
        lexical.id_forms(_plant(tmp_path, {"name": "bare", "pattern": r"ZQ\d+"}))
    assert raised.value.code == "CONFIG_INVALID" and "id_forms" in raised.value.message


def test_a_path_map_that_is_no_yaml_is_config_invalid(tmp_path):
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / "governance/project/path-map.yaml").write_text("id_forms: [\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        lexical.id_forms(tmp_path)
    assert raised.value.code == "CONFIG_INVALID"


# ---- the reader (S2) ------------------------------------------------------------------------------------------------

TODAYS = "See DEC-12, W2-M071 and RETR-X-02; QX-4471 gauge, DEC-12 again, DEC-123-b, ABC-xyz, V1.2 and a-b-1."


@pytest.mark.parametrize("kind", sorted(TOKENS))
def test_a_declared_form_is_read_when_declared_and_not_when_not(tmp_path, kind):
    forms = lexical.id_forms(_plant(tmp_path, FORMS))
    token = TOKENS[kind]
    text = f"The pier {token} is open."
    assert lexical.ids_in(text, forms) == [token]
    if kind != "dotted":
        assert lexical.ids_in(text) == []
        assert lexical.ids_in(text, ()) == []
    else:  # the built-in shape reads only a fragment of it
        assert lexical.ids_in(text) == ["SPEC-4"]


def test_every_form_is_read_beside_the_built_in_shape_once_and_in_order(tmp_path):
    forms = lexical.id_forms(_plant(tmp_path, FORMS))
    text = (f"{TOKENS['spaced']} then DEC-12 then {TOKENS['bare']}, {TOKENS['lower']}; {TOKENS['under']} "
            f"and {TOKENS['dotted']}; {TOKENS['bare']} again, DEC-12 again, W2-M071.")
    assert lexical.ids_in(text, forms) == [TOKENS["spaced"], "DEC-12", TOKENS["bare"], TOKENS["lower"],
                                           TOKENS["under"], TOKENS["dotted"], "W2-M071"]


def test_with_no_form_the_result_is_today_s(tmp_path):
    forms = lexical.id_forms(_plant(tmp_path, FORMS))
    expected = ["DEC-12", "W2-M071", "RETR-X-02", "QX-4471", "DEC-123-b"]
    assert lexical.ids_in(TODAYS) == expected == lexical.ids_in(TODAYS, ()) == lexical.ids_in(TODAYS, [])
    assert lexical.ids_in(TODAYS, forms) == expected  # none of the forms reads a token of this text


@pytest.mark.parametrize("text", [
    "", "no id here", "DEC-12", "x DEC-12-b y", "a DEC-1.2 b", "ZQ41", "(RT-9)", "RT-9, RT-9; RT-10", "dec-12 Dec-12",
    "A-1 B-b C-2", "W2-M071.", "ZQ-5 ZQ", "line one\nDEC-1\nline DEC-2",
])
def test_ids_in_without_forms_is_the_built_in_expression(text):
    expect = list(dict.fromkeys(name for name in lexical.ID_SHAPE.findall(text) if any(c.isdigit() for c in name)))
    assert lexical.ids_in(text) == expect == lexical.ids_in(text, ())


@pytest.mark.parametrize("text, found", [
    ("xzq41", []),          # a word character before
    ("zq41x", []),          # a word character after
    ("zq411", ["zq411"]),   # the whole run of digits
    ("-zq41", []),          # a hyphen before
    ("zq41-b", []),         # a hyphen and a word character after
    ("zq41-", ["zq41"]),    # a hyphen with none after
    ("zq41.", ["zq41"]),
    ("(zq41)", ["zq41"]),
    ("a_zq41", []),         # an underscore is a word character
])
def test_a_form_s_match_must_be_a_whole_token(tmp_path, text, found):
    forms = lexical.id_forms(_plant(tmp_path, [{"name": "bare", "pattern": r"zq\d+"}]))
    assert lexical.ids_in(text, forms) == found


def test_a_dotted_form_is_read_whole_not_as_its_fragment(tmp_path):
    forms = lexical.id_forms(_plant(tmp_path, [{"name": "dotted", "pattern": r"[A-Z]+-\d+(?:\.\d+)+"}]))
    assert lexical.ids_in("per SPEC-4.2 and SPEC-4 and SPEC-4.2.1.", forms) == ["SPEC-4.2", "SPEC-4", "SPEC-4.2.1"]


def test_overlaps_keep_the_earlier_and_then_the_longer(tmp_path):
    forms = [re.compile(r"ZQ \d+"), re.compile(r"ZQ"), re.compile(r"zz\d+( zz\d+)?")]
    assert lexical.ids_in("ZQ 41", forms) == ["ZQ 41"]          # ZQ alone is a fragment of it
    assert lexical.ids_in("zz1 zz2", forms) == ["zz1 zz2"]
    assert lexical.ids_in("DEC-12", [re.compile(r"DEC-\d+")]) == ["DEC-12"]  # the same span from both: once


def test_a_form_that_matches_nothing_or_the_empty_string_adds_no_id():
    forms = [re.compile(r"nothing-here"), re.compile(r"(?:zz)?")]
    assert lexical.ids_in("DEC-12 and 7", forms) == ["DEC-12"]


def test_a_form_with_a_capture_group_is_read_by_its_whole_match():
    assert lexical.ids_in("see ticket#41 now", [re.compile(r"ticket#(\d+)")]) == ["ticket#41"]
