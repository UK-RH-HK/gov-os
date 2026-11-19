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
import importlib.util  # noqa: E402

# The store folder's builder file by its path, under a name of its own: the acceptance folder of W2-203 holds a file
# of the same base name, and in one collection of both (the full suite) a bare import finds that one.
_spec = importlib.util.spec_from_file_location("w2_203_unit_store_archive",
                                               REPO / "tests/unit/store/test_w2_203_archive.py")
_store_archive = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_store_archive)
plant = _store_archive.plant


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
