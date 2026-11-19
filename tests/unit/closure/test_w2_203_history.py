"""Builder tests for W2-203: an archived decision id is a member of the closure, of kind history (DEC-136)."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests/unit/store"))

from gov import closure as closure_module, codeintel, store  # noqa: E402
from gov.closure import closure  # noqa: E402
from gov.store import loader  # noqa: E402
from test_w2_203_archive import plant  # noqa: E402


@pytest.fixture()
def root(tmp_path, monkeypatch):
    root = plant(tmp_path / "a")
    store.load(root)
    monkeypatch.setattr(codeintel, "definitions", lambda _root, name: [])
    return root


def test_an_archived_id_is_history_from_the_entry_that_names_it_and_by_itself(root):
    found = closure(root, ["DEC-200"], depth=1)
    assert found["closure"] == [{"id": "DEC-100", "kind": "history"}, {"id": "DEC-200", "kind": "record"}]
    assert found["gaps"] == [{"id": "DEC-999", "reason": closure_module.UNRESOLVED}]


def test_an_archived_id_is_where_the_walk_ends_as_the_missing_record_it_was(root):
    alone = closure(root, ["DEC-100"], depth=0)  # the entry that supersedes it is not named from it: no gap
    assert alone["closure"] == [{"id": "DEC-100", "kind": "history"}] and alone["gaps"] == []
    assert alone["stopping_reason"] == closure_module.COMPLETE


def test_a_store_without_the_table_leaves_the_id_unresolved(root):
    connection = sqlite3.connect(root / loader.STORE_REL)
    connection.execute(f"DROP TABLE {loader.ARCHIVE_TABLE}")
    connection.commit()
    connection.close()
    found = closure(root, ["DEC-200"], depth=1)
    assert {"id": "DEC-100", "reason": closure_module.UNRESOLVED} in found["gaps"]
