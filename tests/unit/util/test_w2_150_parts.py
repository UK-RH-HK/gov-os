"""Unit tests for gov.util.parts, the guard's parts, ticket names and evaluation sets moved by W2-150 (DEC-136; S5).

Planted trees and path maps only; no evaluation set of this repository is read. The old names
(``gov.guard.reads.evaluation_sets`` and the rest) keep their cases in tests/unit/guard.
"""

from __future__ import annotations

import os

import pytest

from gov.util import parts

SET = ("evaluation_sets:\n  memory:\n    visible: [fixtures/v/**]\n    hidden: [fixtures/h/**]\n"
       "    measures:\n      roles: [engineer]\n")


def _map(root, text):
    (root / "governance/project").mkdir(parents=True, exist_ok=True)
    (root / parts.PATH_MAP_REL).write_text(text, encoding="utf-8")


def test_no_path_map_or_no_block_is_no_set(tmp_path):
    assert parts.evaluation_sets(str(tmp_path)) == {}
    _map(tmp_path, "version: 1\n")
    assert parts.evaluation_sets(str(tmp_path)) == {}


def test_the_block_is_read_alone_so_an_error_elsewhere_does_not_stop_it(tmp_path):
    _map(tmp_path, "version: 1\nother: [unclosed\n" + SET + "after: 1\n")
    sets = parts.evaluation_sets(str(tmp_path))
    assert sets == {"memory": {"visible": ["fixtures/v/**"], "hidden": ["fixtures/h/**"],
                               "measures": {"roles": ["engineer"]}}}
    assert parts.set_fault(sets["memory"]) is None


@pytest.mark.parametrize("text", [
    SET + "    hidden: [again]\n",  # a key written twice
    "evaluation_sets: [a, b]\n",  # not a map of sets
])
def test_a_block_that_cannot_be_read_as_sets_fails_closed(tmp_path, text):
    _map(tmp_path, text)
    with pytest.raises(parts.PolicyError):
        parts.evaluation_sets(str(tmp_path))


@pytest.mark.parametrize(("entry", "fault"), [
    ("not a map", "a set is not a map"),
    ({"visible": ["/abs"], "hidden": ["h"], "measures": {"roles": ["r"]}}, "visible part"),
    ({"hidden": [], "measures": {"roles": ["r"]}}, "hidden part"),
    ({"hidden": ["a/../b"], "measures": {"roles": ["r"]}}, "hidden part"),
    ({"hidden": ["h"], "measures": {"roles": []}}, "measures name no role"),
    ({"hidden": ["h"], "measures": {"tickets": ["T-1"]}}, None),
])
def test_set_fault_names_what_is_not_of_the_stated_shape(entry, fault):
    found = parts.set_fault(entry)
    assert found is None if fault is None else fault in found


def test_load_yaml_unique_refuses_a_key_written_twice():
    assert parts.load_yaml_unique("a: 1\nb: 2\n") == {"a": 1, "b": 2}
    with pytest.raises(Exception):
        parts.load_yaml_unique("a: 1\na: 2\n")


@pytest.mark.parametrize(("glob", "path", "matched"), [
    ("a/**/z", "a/b/c/z", True), ("a/*/z", "a/b/c/z", False), ("a/?.py", "a/x.py", True),
    ("a/{x,y}.py", "a/y.py", True), ("a/[xy].py", "a/x.py", True), ("a/*.py", "a/b/x.py", False),
])
def test_the_glob_matches_whole_paths(glob, path, matched):
    assert parts._Glob(glob).match(path) is matched


def test_a_part_holds_a_path_at_or_under_its_globs(tmp_path):
    root = str(tmp_path)
    part = parts._Part(root, ["fixtures/h/**", "docs/*.md"], "")
    assert part.inside(os.path.join(root, "fixtures/h/q1.json"))
    assert part.inside(os.path.join(root, "fixtures/h"))  # the folder itself
    assert part.inside(os.path.join(root, "docs/a.md"))
    assert not part.inside(os.path.join(root, "docs/sub/a.md"))
    assert not part.inside(os.path.join(root, "fixtures/v/q1.json"))
    assert not part.inside("/elsewhere/fixtures/h/q1.json")
    assert part.under(root) and not part.strict
    assert parts._Part(root, ["x/**"], parts.HIDDEN_REFUSAL).strict


def test_a_part_s_files_are_the_existing_ones_and_bounded(tmp_path, monkeypatch):
    (tmp_path / "fixtures/h/sub").mkdir(parents=True)
    for name in ("fixtures/h/a.json", "fixtures/h/sub/b.json", "fixtures/v.json"):
        (tmp_path / name).write_text("{}", encoding="utf-8")
    part = parts._Part(str(tmp_path), ["fixtures/h/**"], "")
    assert part.files == sorted(str(tmp_path / n) for n in ("fixtures/h/a.json", "fixtures/h/sub/b.json"))
    assert part.held() and part.below(str(tmp_path / "fixtures/h/sub")) == [str(tmp_path / "fixtures/h/sub/b.json")]
    monkeypatch.setattr(parts, "_MOST_FILES", 1)
    with pytest.raises(parts.PolicyError):
        _ = parts._Part(str(tmp_path), ["fixtures/h/**"], "").files


def test_related_and_walk(tmp_path):
    assert parts._related("/a", "/a/b") and parts._related("/a/b", "/a") and parts._related("/", "/x")
    assert not parts._related("/a", "/ab")
    assert parts._walk(str(tmp_path / "missing"), True) == []
    (tmp_path / "f").write_text("x", encoding="utf-8")
    assert parts._walk(str(tmp_path / "f"), False) == [(str(tmp_path), [], ["f"])]


def _ticket_file(root, name, text):
    (root / ".tickets").mkdir(exist_ok=True)
    (root / ".tickets" / name).write_text(text, encoding="utf-8")


def test_the_ticket_s_names_by_its_file_or_its_wbs_id(tmp_path):
    _ticket_file(tmp_path, "DAEO-ab12.md", "---\nid: DAEO-ab12\nwbs_id: W2-77\n---\n# x\n")
    assert parts._ticket(str(tmp_path), "DAEO-ab12") == ({"DAEO-ab12", "W2-77"}, "W2-77")
    assert parts._ticket(str(tmp_path), "W2-77") == ({"W2-77", "DAEO-ab12"}, "W2-77")
    assert parts._ticket(str(tmp_path), "W2-78") == ({"W2-78"}, None)
    assert parts._ticket(str(tmp_path), None) == (set(), None)
    assert parts._ticket(str(tmp_path), "a/b") == (set(), None)


def test_a_ticket_file_that_cannot_be_read_for_its_wbs_id_fails_closed(tmp_path):
    _ticket_file(tmp_path, "DAEO-bad.md", "---\nid: DAEO-bad\nwbs_id: 'not a wbs id'\n---\n")
    with pytest.raises(parts.PolicyError):
        parts._ticket(str(tmp_path), "DAEO-bad")
    _ticket_file(tmp_path, "DAEO-none.md", "no front matter at all\n")
    with pytest.raises(parts.PolicyError):
        parts._ticket(str(tmp_path), "DAEO-none")


def test_the_old_module_names_the_same_objects():
    from gov.guard import reads

    for name in ("evaluation_sets", "set_fault", "PolicyError", "PATH_MAP_REL", "SETS_KEY", "_Part", "_ticket",
                 "_read_text", "_related", "_walk", "HIDDEN_REFUSAL"):
        assert getattr(reads, name) is getattr(parts, name), name
    assert issubclass(reads._Runs, parts._Part)
