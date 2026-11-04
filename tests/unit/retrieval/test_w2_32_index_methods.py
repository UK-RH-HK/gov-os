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


# --- M5: one span per register entry -----------------------------------------------------------------------------

def _entry(number, lines):
    return f"### DEC-{number:03d} — Decision {number}\n" + "".join(
        f"- Line {n} of decision {number}, about the harbour's tide almanac and its keepers.\n" for n in range(lines))


REGISTER = ("# The register\n\n## Section one\n\nIntroductory text of the section.\n\n"
            + _entry(1, 5) + _entry(2, 40) + _entry(3, 160) + "## Section two\n\n"
            + "".join(f"Row {n} of a long table outside any entry, kept as before.\n" for n in range(60))
            + _entry(4, 2))


@pytest.fixture()
def register(project):
    root = project
    (root / "governance/project/path-map.yaml").write_text(
        "namespaces:\n  all: {paths: ['**'], embedding_policy: embedded}\ndecision_register: docs/REG.md\n",
        encoding="utf-8")
    (root / "docs").mkdir()
    (root / "docs/REG.md").write_text(REGISTER, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "register")
    return root


def _entry_spans(text):
    lines = text.splitlines()
    heads = [n for n, line in enumerate(lines, 1) if line.startswith("#")]
    return {lines[a - 1]: (a, b) for a, b in zip(heads, [h - 1 for h in heads[1:]] + [len(lines)])
            if lines[a - 1].startswith("### DEC-")}


def test_m5_off_is_today_s_and_on_each_entry_is_one_span_up_to_the_limit():
    today = chunking.chunk_file("docs/REG.md", "b", REGISTER)
    assert chunking.chunk_file("docs/REG.md", "b", REGISTER, {"chunk_register_by_entry": True}) == today  # no register
    parents, chunks = chunking.chunk_file("docs/REG.md", "b", REGISTER, {"chunk_register_by_entry": True},
                                          register="docs/REG.md")
    assert parents == today[0]  # the parents kept
    spans = [(first, last) for _, _, first, last, _, _ in chunks]
    entries = _entry_spans(REGISTER)
    sizes = {head: len("".join(REGISTER.splitlines(keepends=True)[a - 1:b])) for head, (a, b) in entries.items()}
    assert sizes["### DEC-002 — Decision 2"] > chunking.MAX_CHARS and sizes["### DEC-003 — Decision 3"] > 10_000
    for head, (a, b) in entries.items():
        inside = [(f, l) for f, l in spans if a <= f and l <= b]
        if sizes[head] <= chunking.REGISTER_ENTRY_CHARS:
            assert inside == [(a, b)], head  # one span: the whole entry
        else:
            assert len(inside) > 1 and all(len("".join(REGISTER.splitlines(keepends=True)[f - 1:l])) <= 10_000
                                           for f, l in inside)  # split within it, at the limit
    today_spans = [(first, last) for _, _, first, last, _, _ in today[1]]
    section = [(f, l) for f, l in today_spans if REGISTER.splitlines()[f - 1].startswith("Row")
               or REGISTER.splitlines()[f - 1].startswith("## Section two")]
    assert section and all(span in spans for span in section)  # outside the entries: as before
    from gov.retrieval import semantic
    assert chunking.REGISTER_ENTRY_CHARS == 10_000 == semantic.EMBED_LIMIT_CHARS  # an entry is embedded whole


def test_switching_m5_marks_only_the_register_stale_and_off_restores_today_s(register):
    root = register
    lexical.refresh(root)
    today, code = lexical.digest(root), _spans(root, "src/almanac.py")
    _settings(root, chunk_register_by_entry=True)
    assert lexical.freshness(root) == {"status": "stale", "stale": ["docs/REG.md"]}
    assert lexical.refresh(root)["indexed"] == ["docs/REG.md"]
    entries = _entry_spans(REGISTER)
    assert entries["### DEC-002 — Decision 2"] in _spans(root, "docs/REG.md")
    assert _spans(root, "src/almanac.py") == code
    _settings(root, chunk_register_by_entry=True, chunk_code_by_definition=True)  # both: only the code is added
    assert lexical.freshness(root) == {"status": "stale", "stale": ["src/almanac.py"]}
    _settings(root)
    lexical.refresh(root)
    assert lexical.digest(root) == today and "lexical_recipe" not in _tables(root)


def test_m5_on_a_question_about_an_entry_s_last_line_finds_the_whole_entry(register):
    root = register
    _settings(root, chunk_register_by_entry=True)
    lexical.refresh(root)
    ranked = lexical.search(root, "Line 39 of decision 2", refresh=False)["ranked"]
    assert (ranked[0]["start_line"], ranked[0]["end_line"]) == _entry_spans(REGISTER)["### DEC-002 — Decision 2"]


# --- M4: identifier tokenisation in the keyword index ------------------------------------------------------------

def test_m4_splits_the_identifiers_the_tokenizer_keeps_whole():
    text = "the rerank_service, rerankService, HTTPServer and MAX_REQUEST_TEXTS; gov.retrieval.semantic; plain W2-32"
    assert lexical.identifier_parts(text) == "rerank service http server max request texts"
    assert lexical.identifier_parts("plain words and gov/retrieval/semantic.py") == ""  # the tokenizer splits these


def _columns(root):
    with sqlite3.connect(root / STORE_REL) as connection:
        return tuple(row[1] for row in connection.execute("PRAGMA table_info(lexical_fts)"))


SPLIT_CODE = "def open_rerank_service(port):\n    return port\n\n\ndef startHarbourWatch():\n    return 1\n"


@pytest.fixture()
def identifiers(project):
    root = project
    (root / "src/ops.py").write_text(SPLIT_CODE, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "identifiers")
    return root


def test_switching_m4_rebuilds_the_whole_index_with_the_parts_and_off_restores_today_s(identifiers):
    root = identifiers
    lexical.refresh(root)
    today, chunks = lexical.digest(root), lexical.chunks(root)
    assert _columns(root) == lexical.COLUMNS
    _settings(root, lexical_split_identifiers=True)
    fresh = lexical.freshness(root)
    assert fresh["status"] == "stale" and set(fresh["stale"]) == {c["path"] for c in chunks}  # every file
    assert sorted(lexical.refresh(root)["indexed"]) == sorted({c["path"] for c in chunks})
    assert _columns(root) == lexical.SPLIT_COLUMNS and lexical.chunks(root) == chunks  # the chunks themselves stand
    _settings(root)
    assert lexical.freshness(root)["status"] == "stale"
    lexical.refresh(root)
    assert lexical.digest(root) == today and _columns(root) == lexical.COLUMNS and "lexical_recipe" not in _tables(root)


def test_m4_on_plain_words_find_a_snake_case_or_camel_case_identifier_and_the_exact_route_is_unchanged(identifiers):
    root = identifiers
    lexical.refresh(root)
    off_words = [c["path"] for c in lexical.search(root, "rerank service", refresh=False)["ranked"]]
    off_exact = lexical.search(root, "open_rerank_service", refresh=False)["hits"]
    assert "src/ops.py" not in off_words  # off: one token, not its words
    _settings(root, lexical_split_identifiers=True)
    lexical.refresh(root)
    assert lexical.search(root, "rerank service", refresh=False)["ranked"][0]["path"] == "src/ops.py"
    assert lexical.search(root, "harbour watch", refresh=False)["ranked"][0]["path"] == "src/ops.py"
    assert lexical.search(root, "open_rerank_service", refresh=False)["hits"] == off_exact  # the exact route as before
