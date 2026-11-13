"""W2-88 S4, F3: the store layout stated once, its stamp, and the open path that refuses another version."""

import os
import sqlite3
import subprocess

import pytest

from gov.cli.errors import GovError
from gov.store import STORE_REL, connect, layout, load

ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t"}


def repo_with_record(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    for args in (("init", "-q"), ("add", "-A")):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=ENV)
    (root / "a.md").write_text("---\nid: R-1\ntype: note\nstatus: ACTIVE\n---\n\nbody\n")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True, env=ENV)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "one"], check=True, capture_output=True, env=ENV)
    return root


def test_the_layout_states_its_version_each_store_file_and_its_tables():
    assert layout.LAYOUT_VERSION == 2 and layout.STAMP_TABLE == "store_layout"
    assert set(layout.STORES) == {"record", "lexical", "vectors", "codegraph"}
    for name in ("record", "lexical", "vectors"):
        assert layout.STORES[name]["file"] == ".gov-runtime/store.db"
    assert layout.STORES["codegraph"] == {"file": ".gov-runtime/codeintel/", "tables": ()}
    assert "span" in layout.STORES["record"]["tables"]["register_entries"]
    assert all(table.startswith("lexical_") for table in layout.STORES["lexical"]["tables"])
    assert all(table.startswith("semantic_") for table in layout.STORES["vectors"]["tables"])


def test_a_load_stamps_the_store_and_a_current_store_opens(tmp_path):
    root = repo_with_record(tmp_path)
    load(root)
    conn = connect(root)
    try:
        assert layout.version_of(conn) == layout.LAYOUT_VERSION
    finally:
        conn.close()


@pytest.mark.parametrize("version", [1, 3], ids=["older", "newer"])
def test_an_older_or_newer_stamp_is_refused_naming_both_versions(tmp_path, version):
    root = repo_with_record(tmp_path)
    load(root)
    db = sqlite3.connect(root / STORE_REL)
    db.execute("UPDATE store_layout SET version = ?", (version,))
    db.commit()
    db.close()
    with pytest.raises(GovError) as raised:
        connect(root)
    assert raised.value.code == "STORE_LAYOUT_STALE"
    assert raised.value.details == {"found": version, "expected": layout.LAYOUT_VERSION}
    assert f"store layout {version}, this gov reads {layout.LAYOUT_VERSION}" in raised.value.message


def test_a_store_from_before_the_span_column_is_stale_and_never_missing(tmp_path):
    root = tmp_path / "old"
    (root / ".gov-runtime").mkdir(parents=True)
    db = sqlite3.connect(root / STORE_REL)
    db.execute("CREATE TABLE register_entries (id TEXT PRIMARY KEY, heading TEXT, title TEXT, content_hash TEXT)")
    db.commit()
    db.close()
    with pytest.raises(GovError) as raised:
        connect(root)
    assert raised.value.code == "STORE_LAYOUT_STALE" and raised.value.details["found"] == 0


def test_an_unstamped_whole_store_is_read_as_current_and_an_absent_one_is_missing(tmp_path):
    root = tmp_path / "hand"
    (root / ".gov-runtime").mkdir(parents=True)
    db = sqlite3.connect(root / STORE_REL)
    db.execute("CREATE TABLE records (path TEXT, id TEXT, type TEXT, status TEXT)")
    db.commit()
    db.close()
    connect(root).close()
    with pytest.raises(GovError) as raised:
        connect(tmp_path / "nothing")
    assert raised.value.code == "STORE_MISSING"
