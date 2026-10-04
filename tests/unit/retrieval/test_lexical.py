"""Builder tests for the lexical index (W1-17).

Regression evidence only (DEC-136). They cover what the acceptance tests leave to the builder: the chunking and
the FTS5 table are the carried ones, the filter is asked only about changed paths and before any read, and the
parts of a file a parent holds. Every index is built in a temporary git repository (DEC-322), with the secret
filter replaced by a recorder, so no test needs gitleaks.
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "cli"))

from gov.retrieval import chunking, lexical  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
NOTE = "# Title\n\nAn arrow -> here.\n"
CODE = "import os\n\n\nclass Pool:\n    size = 1\n\n    def full(self):\n        def inner():\n            return 1\n        return inner()\n"


def _commit(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "a change"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A repository with two files, and the list of what the filter was asked; ``secret.md`` is never let through."""
    asked = []

    def indexable(root, paths):
        asked.append(sorted(paths))
        return [rel for rel in paths if rel != "secret.md"]

    monkeypatch.setattr(lexical, "indexable", indexable)
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    _commit(tmp_path, {".gitignore": ".gov-runtime/\n", "notes/a.md": NOTE, "app/pool.py": CODE})
    return tmp_path, asked


def test_the_chunking_is_the_carried_one():
    """The same spans and text as ``cli/govbridge/core/chunking.py``, and every line is in a chunk."""
    carried = pytest.importorskip("govbridge.core.chunking")
    text = "".join(f"line {number} of the file, with some words on it\n" for number in range(1, 400)) + "no newline"
    ported = chunking.chunk_text(text)
    assert ported == [(chunk.start_line, chunk.end_line, chunk.text) for chunk in carried.chunk_text(text)]
    assert len(ported) > 1 and all(len(chunk) <= chunking.MAX_CHARS for _, _, chunk in ported)
    assert {line for start, end, _ in ported for line in range(start, end + 1)} == set(range(1, 401))
    assert chunking.chunk_text("") == []


def test_the_index_is_the_carried_fts5_table_in_the_shared_store(project):
    root, _ = project
    lexical.refresh(root)
    connection = sqlite3.connect(root / ".gov-runtime/store.db")
    (sql,) = connection.execute("SELECT sql FROM sqlite_master WHERE name = 'lexical_fts'").fetchone()
    connection.close()
    assert "fts5" in sql and "porter unicode61 tokenchars '_'" in sql


def test_the_filter_is_asked_about_changed_paths_only_and_before_any_read(project):
    root, asked = project
    assert sorted(lexical.refresh(root)["indexed"]) == [".gitignore", "app/pool.py", "notes/a.md"]
    assert lexical.refresh(root)["indexed"] == [] and len(asked) == 1, "an unchanged tree was judged again"
    _commit(root, {"secret.md": "never read\n", "notes/a.md": NOTE + "More.\n"})
    assert lexical.refresh(root)["indexed"] == ["notes/a.md"]
    assert asked[-1] == ["notes/a.md", "secret.md"]
    assert lexical.freshness(root) == {"status": "fresh", "stale": []}
    assert b"never read" not in (root / ".gov-runtime/store.db").read_bytes()
    _commit(root, {".gitleaks.toml": "title = 'rules'\n"})
    assert lexical.refresh(root)["indexed"] == [".gitleaks.toml"], "an unchanged file was chunked again"
    assert len(asked[-1]) == 5, "the rules changed and not every file was judged again"


def test_a_query_without_a_token_is_still_an_exact_string(project):
    root, _ = project
    assert [(hit["path"], hit["line"]) for hit in lexical.search(root, "->")["hits"]] == [("notes/a.md", 3)]


def test_the_parents_of_a_python_file_and_of_a_document():
    """A method is a function with its nested function inside it; a class body belongs to the module. The text
    before a document's first heading is a section of its own."""
    assert chunking.parents("app/pool.py", CODE) == [("module", 1, 10, [(1, 6)]), ("function", 7, 10, [(7, 10)])]
    assert chunking.parents("app/broken.py", "def (:\n") == [("module", 1, 1, [(1, 1)])]
    assert [span[:3] for span in chunking.parents("a.md", "intro\n# One\ntext\n## Two\n")] == [
        ("section", 1, 1), ("section", 2, 3), ("section", 4, 4)]
    assert chunking.parents("empty.txt", "") == []
