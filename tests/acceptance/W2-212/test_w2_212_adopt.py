"""W2-212 SR-3: A3 refuses an unclassed namespace that is stale as a whole (ADOPT_STALE_CLASS: its name, or every one of
its paths), notices one only some of whose paths say it, or only its description; the skill text."""
from __future__ import annotations

import pytest

from w2_212_support import REPO, a3, adopt_config, adopt_root, git  # noqa: F401  (adopt_root is a fixture)

from gov.adopt import project
from gov.cli.errors import GovError

GOOD = {"lexical_policy": "not indexed", "embedding_policy": "not embedded"}


def refused(root, conf):
    heads = []
    with pytest.raises(GovError) as caught:
        a3(root, conf, before_a3=lambda: heads.append(git(root, "rev-parse", "HEAD")))
    head = heads[0]
    assert git(root, "rev-parse", "HEAD") == head and not (root / project.record_path("A3")).exists()
    return caught.value


@pytest.mark.parametrize("name, paths", [
    ("legacy-docs", ["docs/legacy/**"]),            # a word in the name and in the path
    ("superseded_plans", ["docs/plans/**"]),         # a word in the name only, split on _
    ("plain", ["docs/archive/**"]),                  # a word in the path only (archive)
    ("plain", ["docs/Historical/**"]),               # case-insensitive
    ("plain", ["docs/legacy/**", "docs/archive/**"]),  # every one of several paths
    ("old_legacy", ["docs/plans/**", "docs/notes/**"]),  # a word in the name; no path says it
    ("legacy-docs", ["docs/plans/**", "docs/legacy/**"]),  # a word in the name; only some paths say it
])
def test_sr3_an_unclassed_namespace_saying_it_is_stale_is_refused_naming_it_and_records_nothing(
        adopt_root, name, paths):  # noqa: F811
    error = refused(adopt_root, adopt_config((name, {"paths": paths})))
    assert error.code == "ADOPT_STALE_CLASS" and name in error.message


def test_sr3_the_same_namespace_with_the_class_and_both_policies_is_recorded(adopt_root):  # noqa: F811
    conf = adopt_config(("legacy-docs", {"paths": ["docs/legacy/**"], "stale_class": "legacy", **GOOD}))
    assert a3(adopt_root, conf)["stage"] == "A3"
    assert (adopt_root / project.record_path("A3")).is_file()


def test_sr3_a_word_that_is_only_part_of_a_longer_word_is_no_match(adopt_root):  # noqa: F811
    result = a3(adopt_root, adopt_config(("legacyish", {"paths": ["docs/plans/**"]})))
    assert result["stage"] == "A3" and not result.get("notices")


def test_sr3_a_description_that_says_legacy_is_a_notice_not_a_refusal(adopt_root):  # noqa: F811
    conf = adopt_config(("notes", {"paths": ["docs/notes/**"], "provenance": "legacy material from the old team"}))
    result = a3(adopt_root, conf)
    assert result["stage"] == "A3"
    assert "notes" in __import__("json").dumps(result["notices"])


def the_notice(result, name):
    """The one ``notices`` entry of ``name`` in the A3 result."""
    found = [entry for entry in result.get("notices") or [] if entry["namespace"] == name]
    assert len(found) == 1, result.get("notices")
    return found[0]


@pytest.mark.parametrize("paths, stale, words", [
    (["docs/plans/**", "docs/legacy/**"], ["docs/legacy/**"], {"legacy"}),          # one of two
    (["docs/legacy/**", "docs/plans/**", "docs/Historical/**", "docs/notes/**", "docs/archive/**"],
     ["docs/legacy/**", "docs/Historical/**", "docs/archive/**"], {"legacy", "historical", "archive"}),
])
def test_sr3_a_namespace_only_some_of_whose_paths_say_it_is_recorded_with_a_notice_naming_those_paths(
        adopt_root, paths, stale, words):  # noqa: F811
    result = a3(adopt_root, adopt_config(("mixed", {"paths": paths})))
    assert result["stage"] == "A3" and (adopt_root / project.record_path("A3")).is_file()
    entry = the_notice(result, "mixed")
    assert sorted(entry["paths"]) == sorted(stale)
    assert {word.lower() for word in entry["words"]} == words
    text = entry["notice"].lower()
    assert "namespace" in text and "own" in text and ("stale_class" in text or "stale class" in text), entry["notice"]


def test_sr3_a_catch_all_harbour_map_with_legacy_and_archive_paths_and_no_class_passes_a3(adopt_root):  # noqa: F811
    """The end-to-end consequence: one namespace holds the live files and the old folders; obeying a refusal (classing it)
    would drop every live document from memory."""
    paths = ["lib/**", "README.md", ".gitignore", "docs/**", "legacy/**", "archive/**"]
    conf = {"path-map.yaml": {"namespaces": {"harbour": {"paths": paths, "embedding_policy": "embedded"}},
                              "capabilities": {"code_intelligence": {"enabled": False}}}}
    result = a3(adopt_root, conf)
    assert result["stage"] == "A3" and (adopt_root / project.record_path("A3")).is_file()
    assert sorted(the_notice(result, "harbour")["paths"]) == ["archive/**", "legacy/**"]


def test_sr3_beside_a_classed_namespace_only_the_mixed_one_gets_a_notice(adopt_root):  # noqa: F811
    result = a3(adopt_root, adopt_config(
        ("old-design", {"paths": ["docs/archive/**"], "stale_class": "historical", **GOOD}),
        ("mixed", {"paths": ["docs/plans/**", "docs/legacy/**"]})))
    assert result["stage"] == "A3"
    assert [entry["namespace"] for entry in result.get("notices") or []] == ["mixed"]


SKILLS = ("template/governance/kernel/skills/adopt/SKILL.md", "template/.rulesync/skills/adopt/SKILL.md")


def test_sr3_the_adopt_skill_has_a_section_on_the_class_and_its_two_copies_are_identical():
    texts = [(REPO / rel).read_bytes() for rel in SKILLS]
    assert texts[0] == texts[1]
    text = texts[0].decode("utf-8")
    sections = ["##" + part for part in text.split("\n##")[1:]]
    needed = ("stale_class", "lexical_policy: not indexed", "embedding_policy: not embedded", "superseded",
              "historical", "legacy")
    assert any(all(word in section for word in needed) for section in sections), "no section names the route"
