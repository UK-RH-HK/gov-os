"""Builder tests for W2-203: the archived register's ids and headings, kept by the store in a table of their own.

Regression evidence only (DEC-136). A planted repository whose path map names a register and an archive: the archive
is read from ``HEAD`` for ids and headings alone; an archive-only id is no record, no register entry and no edge end
of its own; the table is outside the digest.
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import store  # noqa: E402
from gov.store import layout, loader  # noqa: E402
from gov.util import archive  # noqa: E402

PATH_MAP = "governance/project/path-map.yaml"
KEPT = "### DEC-200 — The kept rule\n- **Status:** ACCEPTED · **Supersedes:** DEC-100, DEC-999\n- **Decision:** kept.\n"
ARCHIVE = ("> **ARCHIVED, READ-ONLY.**\n# Old register\n\n### DEC-100 — The old rule\n- **Status:** SUPERSEDED\n"
           "- **Decision:** the quay is closed.\n\n### DEC-027 — No status line\nA paragraph first.\n\n" + KEPT)
BOTH = "decision_register: reg.md\ndecision_register_archive: old/reg.md\n"


def plant(root: Path, path_map: str = BOTH, files: dict | None = None) -> Path:
    git = ["git", "-C", str(root), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid"]
    root.mkdir(exist_ok=True)
    subprocess.run([*git, "init", "-q"], check=True)
    given = {".gitignore": ".gov-runtime/\n", PATH_MAP: path_map, "reg.md": "# Register\n\n" + KEPT,
             "old/reg.md": ARCHIVE, **(files or {})}
    for rel, text in given.items():
        if text is not None:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture"], check=True)
    return root


def rows(root: Path, sql: str) -> list[tuple]:
    connection = sqlite3.connect(root / loader.STORE_REL)
    try:
        return sorted(connection.execute(sql))
    finally:
        connection.close()


def test_ids_in_gives_the_live_entries_headings_and_leaves_out_an_entry_the_loader_refuses():
    assert archive.ids_in(ARCHIVE) == {"DEC-100": "### DEC-100 — The old rule", "DEC-200": "### DEC-200 — The kept rule"}


def test_read_is_heads_archive_and_none_where_none_is_named_or_held(tmp_path):
    root = plant(tmp_path / "a")
    (root / "old/reg.md").write_text("### DEC-555 — Uncommitted\n- **Status:** ACCEPTED\n", encoding="utf-8")
    assert archive.read(root) == archive.ids_in(ARCHIVE)  # HEAD's, never the working tree's
    assert archive.read(plant(tmp_path / "b", "decision_register: reg.md\n")) is None
    assert archive.read(plant(tmp_path / "c", files={"old/reg.md": None})) is None


def test_the_load_keeps_the_archives_ids_in_their_own_table_and_makes_no_record_of_them(tmp_path):
    root = plant(tmp_path / "a")
    assert store.load(root)["invalid"] == []
    assert rows(root, f"SELECT id, heading FROM {loader.ARCHIVE_TABLE}") == sorted(archive.ids_in(ARCHIVE).items())
    assert rows(root, "SELECT id FROM records") == [("DEC-200",)]
    assert rows(root, "SELECT id FROM register_entries") == [("DEC-200",)]
    assert rows(root, "SELECT source FROM edges") == [("DEC-200",), ("DEC-200",)]


def test_the_table_is_outside_the_digest_and_in_the_layout(tmp_path):
    assert loader.ARCHIVE_TABLE in loader._TABLES and loader.ARCHIVE_TABLE not in loader._DIGESTED
    assert loader._DIGESTED[-1] == loader.REGISTER_TABLE
    assert layout.STORES["record"]["tables"][loader.ARCHIVE_TABLE] == ("id", "heading")
    with_archive = store.load(plant(tmp_path / "a"))["digest"]
    without = store.load(plant(tmp_path / "b", files={"old/reg.md": None}))["digest"]
    assert with_archive != without  # the path map and the file differ ...
    same = plant(tmp_path / "c", files={"old/reg.md": ARCHIVE + "\n### DEC-101 — One more\n- **Status:** ACCEPTED\n"})
    store.load(same)
    assert ("DEC-101",) in rows(same, f"SELECT id FROM {loader.ARCHIVE_TABLE}")
    assert ("DEC-101",) not in rows(same, "SELECT id FROM records")


@pytest.mark.parametrize("path_map, files", [("decision_register: reg.md\n", {}), (BOTH, {"old/reg.md": None})])
def test_no_archive_named_or_held_gives_an_empty_table_and_no_refusal(tmp_path, path_map, files):
    root = plant(tmp_path / "a", path_map, files)
    assert store.load(root)["invalid"] == []
    assert rows(root, f"SELECT id FROM {loader.ARCHIVE_TABLE}") == []
