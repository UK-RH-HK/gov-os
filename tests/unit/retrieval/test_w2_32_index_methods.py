"""W2-32, DEC-1068's index-time methods of the keyword index, notes within S7: M2 (code chunks cut on definitions),
M5 (one span per register entry), M4 (identifier tokenisation). Each behind its own key in
``governance/project/rebuild.yaml``, absent = off = today's index byte for byte; the store records the methods it was
built with, so a switch makes the index stale and the next refresh rebuilds what it changes.

Regression evidence only (DEC-136): the secrets filter is replaced (every file indexable), no model is started.
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.config import loader  # noqa: E402
from gov.retrieval import chunking, lexical  # noqa: E402
from gov.store import STORE_REL  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
# Small classes with attributes alone share the module's run today (a function is a parent of its own already, and
# so is a method): M2 cuts that run at each class line.
CODE = ("import os\n\n\n"
        + "".join(f"class TideTable{n}:\n    \"\"\"Table {n} of the tide almanac.\"\"\"\n    hour = {n}\n"
                  f"    height = {n * 3}\n\n\n" for n in range(12))
        + "".join(f"def tide_step_{n}(day):\n    return day + {n}\n\n\n" for n in range(4))
        + "class HarbourLog:\n    \"\"\"The harbour's log.\"\"\"\n\n"
        + "".join(f"    def entry_{n}(self):\n        return {n}\n\n" for n in range(3)))
NOTE = "# Notes\n\n" + "".join(f"Line {n} of the harbour notes, about the tide almanac.\n" for n in range(40))


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


def _settings(root, **keys):
    path = root / "governance/project/rebuild.yaml"
    if keys:
        path.write_text("".join(f"{key}: {str(value).lower()}\n" for key, value in keys.items()), encoding="utf-8")
    elif path.exists():
        path.unlink()


@pytest.fixture()
def project(tmp_path, monkeypatch):
    root = tmp_path
    (root / "governance/project").mkdir(parents=True)
    (root / "governance/project/path-map.yaml").write_text(
        "namespaces:\n  all: {paths: ['**'], embedding_policy: embedded}\n", encoding="utf-8")
    (root / ".gitignore").write_text(".gov-runtime/\ngovernance/project/rebuild.yaml\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src/almanac.py").write_text(CODE, encoding="utf-8")
    (root / "notes.md").write_text(NOTE, encoding="utf-8")
    monkeypatch.setattr(lexical, "indexable", lambda root_, paths: list(paths))
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fixture")
    return root


def _spans(root, path):
    return [(c["start_line"], c["end_line"]) for c in lexical.chunks(root, path)]


def _tables(root):
    with sqlite3.connect(root / STORE_REL) as connection:
        return {name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


# --- the setting -------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("key", loader.INDEX_FLAGS)
@pytest.mark.parametrize("value", ["yes", "on", "True", "'true'", "1", ""])
def test_an_index_method_s_invalid_value_is_config_invalid_naming_it(tmp_path, key, value):
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / "governance/project/rebuild.yaml").write_text(f"{key}: {value}\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        loader.index_recipe(tmp_path)
    assert raised.value.code == "CONFIG_INVALID" and raised.value.details["key"] == key
    with pytest.raises(GovError):
        loader.load_config(tmp_path)  # every command that loads the configuration refuses it too


def test_no_file_no_key_or_comments_alone_is_every_method_off(tmp_path):
    off = dict.fromkeys(loader.INDEX_FLAGS, False)
    assert loader.index_recipe(tmp_path) == off
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / "governance/project/rebuild.yaml").write_text("# none yet\n", encoding="utf-8")
    assert loader.index_recipe(tmp_path) == off
    (tmp_path / "governance/project/rebuild.yaml").write_text("embed_headers: false\n", encoding="utf-8")
    assert loader.index_recipe(tmp_path) == off


# --- M2: code chunks cut on definitions --------------------------------------------------------------------------

def test_the_definitions_are_the_top_level_defs_and_classes_and_the_methods():
    lines = CODE.splitlines()
    starts = chunking.definitions(CODE)
    assert [lines[n - 1].split("(")[0].strip() for n in starts] == \
        [f"class TideTable{n}:" for n in range(12)] + [f"def tide_step_{n}" for n in range(4)] \
        + ["class HarbourLog:"] + [f"def entry_{n}" for n in range(3)]
    assert chunking.definitions("def broken(:\n") == []


def test_off_the_chunks_are_today_s_and_on_none_holds_the_start_of_two_definitions():
    today = chunking.chunk_file("src/almanac.py", "blob", CODE)
    assert chunking.chunk_file("src/almanac.py", "blob", CODE, {}) == today
    assert chunking.chunk_file("src/almanac.py", "blob", CODE, {"chunk_code_by_definition": False}) == today
    parents, chunks = chunking.chunk_file("src/almanac.py", "blob", CODE, {"chunk_code_by_definition": True})
    assert parents == today[0]  # the parents kept
    starts = chunking.definitions(CODE)
    for _, _, first, last, _, _ in chunks:
        assert len([s for s in starts if first <= s <= last]) <= 1
    assert any(len([s for s in starts if first <= s <= last]) > 1 for _, _, first, last, _, _ in today[1])
    assert chunking.chunk_file("notes.md", "b", NOTE, {"chunk_code_by_definition": True}) == \
        chunking.chunk_file("notes.md", "b", NOTE)  # not Python: unchanged


def test_switching_m2_marks_the_index_stale_rebuilds_the_python_files_and_off_restores_today_s(project):
    root = project
    lexical.refresh(root)
    today, note = lexical.digest(root), _spans(root, "notes.md")
    assert lexical.freshness(root)["status"] == "fresh" and "lexical_recipe" not in _tables(root)
    _settings(root, chunk_code_by_definition=True)
    assert lexical.freshness(root) == {"status": "stale", "stale": ["src/almanac.py"]}
    report = lexical.refresh(root)
    assert lexical.freshness(root)["status"] == "fresh" and lexical.digest(root) != today
    starts = chunking.definitions(CODE)
    assert all(len([s for s in starts if a <= s <= b]) <= 1 for a, b in _spans(root, "src/almanac.py"))
    assert _spans(root, "notes.md") == note  # what M2 does not change stands
    assert "lexical_recipe" in _tables(root) and report["indexed"] == ["src/almanac.py"]
    _settings(root)
    assert lexical.freshness(root)["status"] == "stale"
    lexical.refresh(root)
    assert lexical.digest(root) == today and "lexical_recipe" not in _tables(root)  # off: today's, byte for byte


def test_m2_on_a_question_naming_a_class_finds_the_chunk_that_begins_at_its_class_line(project):
    root = project
    _settings(root, chunk_code_by_definition=True)
    lexical.refresh(root)
    line = CODE.splitlines().index("class TideTable7:") + 1
    ranked = lexical.search(root, "TideTable7", refresh=False)["ranked"]
    assert ranked[0]["path"] == "src/almanac.py" and ranked[0]["start_line"] == line
