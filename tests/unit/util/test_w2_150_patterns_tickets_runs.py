"""Unit tests for the small helpers W2-150 moved into gov.util (DEC-136: regression evidence; S5).

``gov.util.patterns`` (``_match_pattern``, ``_has_glob``, from ``gov.guard.decide``), ``gov.util.tickets``
(``TICKETS_REL`` from ``gov.tasks.tickets``, ``_parse_frontmatter`` from ``gov.guard.decide``) and
``gov.util.runs_root`` (``root``, ``ROOT_NAME`` from ``gov.guard.runs``). The old names' cases stay where they are.
"""

from __future__ import annotations

import os

import pytest

from gov.util import patterns, runs_root, tickets


@pytest.mark.parametrize(("path", "pattern", "matched"), [
    ("src/gov/a.py", "src/gov/a.py", True),
    ("src/gov/a.py", "src/gov/*.py", True),
    ("src/gov/sub/a.py", "src/gov/*.py", False),  # one star stays in one folder
    ("src/gov/sub/a.py", "src/gov/**", True),  # a trailing ** crosses folders
    ("src/gov", "src/gov/**", False),
    ("src/gov/sub/deep/a.py", "src/**/a.py", True),
    ("src/gov/a.pyc", "src/gov/*.py", False),  # anchored at both ends
    ("src/gov/a+b.py", "src/gov/a+b.py", True),  # other characters are literal
    ("src/gov/axb.py", "src/gov/a?b.py", False),  # ? is no wildcard in this grammar
])
def test_match_pattern_is_the_allowed_paths_grammar(path, pattern, matched):
    assert patterns._match_pattern(path, pattern) is matched


@pytest.mark.parametrize(("word", "globbed"), [("a*", True), ("a?", True), ("[ab]", True), ("plain/path", False),
                                               ("{a,b}", False), ("", False)])
def test_has_glob_names_the_shell_glob_characters(word, globbed):
    assert patterns._has_glob(word) is globbed


def test_the_tickets_folder():
    assert tickets.TICKETS_REL == ".tickets"


def test_parse_frontmatter_reads_keys_and_the_allowed_paths_list():
    text = ("---\nid: DAEO-x\n# a comment\nstatus: in_progress\nallowed_paths:\n- src/a.py\n- 'tests/b/**'\n"
            "- \"*.md\"\n  # inside the list\nwbs_id: W2-9\n---\n# body\n")
    assert tickets._parse_frontmatter(text) == {
        "id": "DAEO-x", "status": "in_progress", "wbs_id": "W2-9",
        "allowed_paths": ["src/a.py", "tests/b/**", "*.md"]}


@pytest.mark.parametrize("text", ["no front matter\n", "---\nid: x\nno end\n", ""])
def test_parse_frontmatter_without_a_closed_block_is_none(text):
    assert tickets._parse_frontmatter(text) is None


def test_parse_frontmatter_ends_the_list_at_a_line_that_is_no_item():
    text = "---\nallowed_paths:\n- a\nplain words\n- b\n---\n"
    assert tickets._parse_frontmatter(text)["allowed_paths"] == ["a"]


def test_runs_root_is_in_the_home_its_links_resolved(tmp_path, monkeypatch):
    real = tmp_path / "real"
    real.mkdir()
    (tmp_path / "link").symlink_to(real, target_is_directory=True)
    monkeypatch.setenv("HOME", str(tmp_path / "link"))
    assert runs_root.ROOT_NAME == "gov-os-runs"
    assert runs_root.root() == os.path.join(os.path.realpath(real), "gov-os-runs")


def test_runs_root_without_an_absolute_home_is_none(monkeypatch):
    monkeypatch.setattr(runs_root.os.path, "expanduser", lambda _path: "relative")
    assert runs_root.root() is None


def test_the_old_modules_name_the_same_objects():
    from gov.guard import decide, runs
    from gov.tasks import tickets as task_tickets

    assert decide._match_pattern is patterns._match_pattern and decide._has_glob is patterns._has_glob
    assert decide._parse_frontmatter is tickets._parse_frontmatter
    assert task_tickets.TICKETS_REL is tickets.TICKETS_REL
    assert runs.root is runs_root.root and runs.ROOT_NAME == runs_root.ROOT_NAME
