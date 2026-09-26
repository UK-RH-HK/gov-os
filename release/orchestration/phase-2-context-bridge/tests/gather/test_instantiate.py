"""``govbridge.gather.instantiate`` (REPAIR_DAG.yaml node R1-GA1, repairing RC-2: "30 of 41 queries never
compiled"). Every fixture here is synthetic (REPAIR-1 rule 2: never the public demonstration query texts or run-1
answers) and generic (OC-BR-02: no class/subject id names a Review-8 item)."""
from __future__ import annotations

import pytest

from govbridge.gather import instantiate as instmod


def _doc():
    return {
        "schema": "test-query-set/1",
        "query_classes": {
            "CLASS_A": "what is the purpose of",
            "CLASS_B": "which requirement governs",
        },
        "subjects": {
            "SUBJ_1": "the fixture subsystem",
            "SUBJ_2": "the other fixture subsystem",
        },
        "queries": [
            {"id": "Q-TEXT", "kind": "query", "text": "an already-executable query"},
            {"id": "Q-CLASS-1", "kind": "query_class", "class": "CLASS_A", "subject": "SUBJ_1"},
            {"id": "Q-CLASS-2", "kind": "query_class", "class": "CLASS_B", "subject": "SUBJ_2"},
        ],
    }


def test_already_executable_entry_passes_through():
    out = instmod.instantiate_entry({"id": "Q1", "text": "hello world"})
    assert out["id"] == "Q1"
    assert out["text"] == "hello world"
    assert out["class"] is None and out["subject"] is None


def test_class_subject_entry_is_instantiated_from_the_query_sets_own_tables():
    doc = _doc()
    out = instmod.instantiate_entry(doc["queries"][1], query_classes=doc["query_classes"], subjects=doc["subjects"])
    assert out["id"] == "Q-CLASS-1"
    assert "what is the purpose of" in out["text"]
    assert "the fixture subsystem" in out["text"]
    assert out["class"] == "CLASS_A" and out["subject"] == "SUBJ_1"


def test_instantiate_all_yields_one_executable_query_per_entry():
    doc = _doc()
    out = instmod.instantiate_all(doc)
    assert [q["id"] for q in out] == ["Q-TEXT", "Q-CLASS-1", "Q-CLASS-2"]
    assert all(q["text"] for q in out)


@pytest.mark.parametrize("bad_entry,expected_substring", [
    ({"id": "BAD-1", "class": "CLASS_A"}, "BOTH keys"),                       # subject missing
    ({"id": "BAD-2", "subject": "SUBJ_1"}, "BOTH keys"),                      # class missing
    ({"id": "BAD-3", "class": "NOPE", "subject": "SUBJ_1"}, "not a row"),     # unknown class
    ({"id": "BAD-4", "class": "CLASS_A", "subject": "NOPE"}, "not a row"),    # unknown subject
    ({"id": "BAD-5"}, "no resolvable"),                                       # neither text nor class/subject
    ({"text": "no id here"}, "no string 'id'"),
])
def test_malformed_entry_raises_query_not_executable_never_skipped(bad_entry, expected_substring):
    doc = _doc()
    with pytest.raises(instmod.QueryNotExecutable) as exc_info:
        instmod.instantiate_entry(bad_entry, query_classes=doc["query_classes"], subjects=doc["subjects"])
    assert exc_info.value.CODE == "QUERY_NOT_EXECUTABLE"
    assert expected_substring in str(exc_info.value)


def test_instantiate_all_raises_on_the_first_malformed_entry_never_silently_skips():
    doc = _doc()
    doc["queries"].append({"id": "BAD"})  # no text, no class/subject
    with pytest.raises(instmod.QueryNotExecutable):
        instmod.instantiate_all(doc)


def test_empty_template_or_subject_text_is_not_executable():
    doc = _doc()
    doc["query_classes"]["CLASS_EMPTY"] = "   "
    entry = {"id": "Q-EMPTY", "class": "CLASS_EMPTY", "subject": "SUBJ_1"}
    with pytest.raises(instmod.QueryNotExecutable):
        instmod.instantiate_entry(entry, query_classes=doc["query_classes"], subjects=doc["subjects"])


def test_template_with_subject_placeholder_is_formatted():
    doc = _doc()
    doc["query_classes"]["CLASS_FMT"] = "explain {subject} in detail"
    entry = {"id": "Q-FMT", "class": "CLASS_FMT", "subject": "SUBJ_1"}
    out = instmod.instantiate_entry(entry, query_classes=doc["query_classes"], subjects=doc["subjects"])
    assert out["text"] == "explain the fixture subsystem in detail"


def test_subject_as_a_mapping_offers_its_own_fields_to_the_template():
    doc = _doc()
    doc["subjects"]["SUBJ_STRUCT"] = {"text": "the structured fixture", "owner": "team fixture"}
    doc["query_classes"]["CLASS_OWNER"] = "who owns {owner}?"
    entry = {"id": "Q-OWNER", "class": "CLASS_OWNER", "subject": "SUBJ_STRUCT"}
    out = instmod.instantiate_entry(entry, query_classes=doc["query_classes"], subjects=doc["subjects"])
    assert out["text"] == "who owns team fixture?"


def test_load_query_set_accepts_a_bare_list():
    doc = instmod.load_query_set([{"id": "Q1", "text": "hi"}])
    assert doc["queries"] == [{"id": "Q1", "text": "hi"}]


def test_load_query_set_accepts_none():
    assert instmod.load_query_set(None) == {"queries": []}


def test_resolve_query_by_id_instantiates_only_that_entry_even_if_another_entry_is_malformed():
    doc = _doc()
    doc["queries"].append({"id": "BAD-ELSEWHERE"})  # malformed, but irrelevant to the id we ask for
    out = instmod.resolve_query(doc, "Q-TEXT")
    assert out["id"] == "Q-TEXT"
    assert out["text"] == "an already-executable query"


def test_resolve_query_falls_back_to_literal_ad_hoc_text():
    doc = _doc()
    out = instmod.resolve_query(doc, "some literal query text not in the query set")
    assert out["text"] == "some literal query text not in the query set"
    assert out["id"].startswith("adhoc:")
    assert out["kind"] == "adhoc"
