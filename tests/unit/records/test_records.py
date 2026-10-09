"""Builder tests for the record queries (W1-10; the follow-up after W1-41).

Regression evidence only (DEC-136): a register entry carries its heading and title in the answer of the record
query, a record of a file carries neither key, and the filters still narrow both.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import records  # noqa: E402
from gov.store import STORE_REL  # noqa: E402

FILE = {"id": "ADR-0001", "type": "decision", "status": "ACTIVE", "path": "docs/adr/ADR-0001.md"}
ENTRY = {"id": "DEC-001", "type": "decision", "status": "ACCEPTED", "path": "decisions/REGISTER.md",
         "heading": "### DEC-001 — The first", "title": "The first"}


def test_a_register_entry_carries_its_heading_and_title_and_a_file_record_neither(tmp_path):
    (tmp_path / STORE_REL).parent.mkdir(parents=True)
    connection = sqlite3.connect(tmp_path / STORE_REL)
    connection.execute("CREATE TABLE records (path TEXT, id TEXT, type TEXT, status TEXT)")
    connection.execute("CREATE TABLE register_entries (id TEXT, heading TEXT, title TEXT)")
    for record in (FILE, ENTRY):
        connection.execute("INSERT INTO records VALUES (:path, :id, :type, :status)", record)
    connection.execute("INSERT INTO register_entries VALUES (:id, :heading, :title)", ENTRY)
    connection.commit()
    connection.close()

    assert records.records(tmp_path) == [FILE, ENTRY]
    assert records.records(tmp_path, type="decision", status="ACCEPTED") == [ENTRY]
    assert records.records(tmp_path, status="ACTIVE") == [FILE]
