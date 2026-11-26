"""W2-212 (D3): the stale class's loader rule and the word matching that A3 and doctor share."""

from gov.config.loader import lexical_policy_fault
from gov.retrieval.stale import classifier, stale_words, unclassed

GOOD = {"stale_class": "legacy", "lexical_policy": "not indexed", "embedding_policy": "not embedded"}


def test_a_class_with_both_policies_is_no_fault():
    assert lexical_policy_fault(GOOD) is None


def test_a_class_without_a_policy_is_a_fault():
    assert "stale_class" in lexical_policy_fault({**GOOD, "lexical_policy": "indexed"})
    assert "stale_class" in lexical_policy_fault({**GOOD, "embedding_policy": "embedded"})
    assert "stale_class" in lexical_policy_fault({"stale_class": "legacy"})


def test_a_class_outside_the_three_is_a_fault():
    assert "stale_class" in lexical_policy_fault({**GOOD, "stale_class": "old"})


def test_words_are_whole_word_parts_and_archive_is_historical():
    assert stale_words("Legacy-Docs", "docs/old_archive/**") == ["legacy", "archive"]
    assert stale_words("legacyish") == []
    assert unclassed({"namespaces": {"a": {"paths": ["docs/archive/**"]},
                                     "b": {"paths": ["x/**"], **GOOD}}}) == [
        {"namespace": "a", "words": ["archive"], "stale_class": "historical"}]


def test_a_namespace_is_stale_as_a_whole_by_its_name_or_by_every_path():
    found = unclassed({"namespaces": {"legacy-docs": {"paths": ["docs/live/**"]},
                                      "b": {"paths": ["docs/legacy/**", "old/archive/**"]},
                                      "none": {"paths": []}}})
    assert [(item["namespace"], "paths" in item) for item in found] == [("legacy-docs", False), ("b", False)]


def test_a_namespace_only_some_of_whose_paths_say_it_gives_those_paths_to_move():
    [item] = unclassed({"namespaces": {"harbour": {"paths": ["docs/**", "docs/legacy/**", "a/archive/**"]}}})
    assert item["paths"] == ["docs/legacy/**", "a/archive/**"] and item["words"] == ["legacy", "archive"]
    assert "namespace of their own" in item["move"] and "stale_class" in item["move"]


def test_the_classifier_matches_only_classed_namespaces(tmp_path):
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / "governance/project/path-map.yaml").write_text(
        "namespaces:\n  old:\n    paths: [docs/old/**]\n    stale_class: legacy\n    lexical_policy: not indexed\n"
        "    embedding_policy: not embedded\n  cur:\n    paths: [docs/**]\n", encoding="utf-8")
    of = classifier(tmp_path)
    assert of("docs/old/a.md") == ("old", "legacy") and of("docs/b.md") is None
