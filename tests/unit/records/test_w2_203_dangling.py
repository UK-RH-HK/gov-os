"""Builder tests for W2-203: an edge to an archived decision id is no dangling reference (DEC-136: regression only)."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests/unit/store"))

from gov import records, store  # noqa: E402
from gov.store import loader  # noqa: E402
from test_w2_203_archive import plant  # noqa: E402


def _targets(root):
    return [edge["target"] for edge in records.dangling(root)]


def test_an_archived_id_is_not_dangling_and_an_id_in_neither_file_is(tmp_path):
    root = plant(tmp_path / "a")
    store.load(root)
    assert _targets(root) == ["DEC-999"]


def test_a_store_without_the_table_is_still_read(tmp_path):
    root = plant(tmp_path / "a")
    store.load(root)
    connection = sqlite3.connect(root / loader.STORE_REL)
    connection.execute(f"DROP TABLE {loader.ARCHIVE_TABLE}")
    connection.commit()
    connection.close()
    assert _targets(root) == ["DEC-100", "DEC-999"]
