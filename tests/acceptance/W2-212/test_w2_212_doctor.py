"""W2-212 SR-4: ``gov doctor`` names an unclassed stale namespace with the three lines, as a notice.

The part's key, the one the engineer reads from here: ``result["stale_class"]`` of ``gov doctor --json`` (always present),
a map with ``status``: ``report`` when a namespace needs the class (never ``fail``, never ``drift``), ``pass`` when none
does; its text (the section serialised as JSON) names each such namespace and the three lines to add."""
from __future__ import annotations

import json

import pytest
import yaml

from w2_212_support import PATH_MAP, commit, init

GOOD = {"lexical_policy": "not indexed", "embedding_policy": "not embedded"}


def plant(tmp_path, old_name, old_paths, **old):
    root = tmp_path / "project"
    init(root)
    spaces = {old_name: {"paths": old_paths, **old}, "rest": {"paths": ["*", "docs/*.md", "governance/**"]}}
    commit(root, {PATH_MAP: yaml.safe_dump({"namespaces": spaces}), "README.md": "x\n", "docs/legacy/a.md": "a\n",
                  "docs/archive/b.md": "b\n"})
    return root


def run(root):
    from w2_212_support import doctor
    return doctor(root)


@pytest.mark.parametrize("name, paths, word", [
    ("legacy-docs", ["docs/legacy/**"], "legacy"),
    ("old-notes", ["docs/archive/**"], "historical"),   # archive maps to historical
])
def test_sr4_an_unclassed_namespace_is_named_with_the_three_lines_and_the_run_still_exits_0(tmp_path, name, paths, word):
    code, result, text = run(plant(tmp_path, name, paths))
    assert code == 0, text
    section = result["stale_class"]
    assert section["status"] == "report"
    shown = json.dumps(section)
    assert name in shown
    for line in (f"stale_class: {word}", "lexical_policy: not indexed", "embedding_policy: not embedded"):
        assert line in shown


MIXED = ["docs/live/**", "docs/legacy/**", "docs/archive/**"]


def entries(section):
    return {entry["namespace"]: entry for entry in section["namespaces"]}


def test_sr4_a_mixed_namespace_is_named_with_its_stale_paths_and_no_lines_to_add(tmp_path):
    code, result, text = run(plant(tmp_path, "harbour", MIXED))
    assert code == 0, text
    section = result["stale_class"]
    assert section["status"] == "report"
    assert set(entries(section)) == {"harbour"}
    entry = entries(section)["harbour"]
    assert sorted(entry["paths"]) == ["docs/archive/**", "docs/legacy/**"]
    assert "add" not in entry, "adding the class to the whole namespace would drop its live documents"


def test_sr4_beside_a_mixed_namespace_only_the_wholly_stale_one_gets_the_three_lines(tmp_path):
    root = tmp_path / "project"
    init(root)
    spaces = {"harbour": {"paths": ["docs/live/**", "docs/legacy/**"]}, "attic": {"paths": ["docs/archive/**"]},
              "rest": {"paths": ["*", "docs/*.md", "governance/**"]}}
    commit(root, {PATH_MAP: yaml.safe_dump({"namespaces": spaces}), "README.md": "x\n", "docs/legacy/a.md": "a\n",
                  "docs/archive/b.md": "b\n", "docs/live/c.md": "c\n"})
    code, result, text = run(root)
    assert code == 0, text
    found = entries(result["stale_class"])
    assert set(found) == {"harbour", "attic"}
    assert found["attic"]["add"] == ["stale_class: historical", "lexical_policy: not indexed",
                                     "embedding_policy: not embedded"]
    assert "add" not in found["harbour"] and found["harbour"]["paths"] == ["docs/legacy/**"]


def test_sr4_all_namespaces_classed_gives_no_notice(tmp_path):
    root = plant(tmp_path, "legacy-docs", ["docs/legacy/**"], stale_class="legacy", **GOOD)
    code, result, text = run(root)
    assert code == 0, text
    section = result["stale_class"]
    assert section["status"] == "pass" and "legacy-docs" not in json.dumps(section)
