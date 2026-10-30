"""Builder tests for the fingerprints a load records and the incremental record load (W2-68).

Regression evidence only (DEC-136): every load records one row out of the digest; the record load refuses another
code fingerprint and leaves the digest of a full load; the store-freshness check reads the row.
"""
from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import store  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.close.fingerprint import of_commit  # noqa: E402
from gov.close.repo import store_is_of_head  # noqa: E402

SCHEMA_REL = "template/governance/kernel/schemas/test-map.schema.json"
MAP_REL = "governance/project/test-map.yaml"
MAP = 'version: 1\nshared_core: ["src/core/**"]\nrecord_only:\n  - "docs/close/**.md"\n'
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}


def _git(root, *args):
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True,
                          env={**_ENV, "HOME": str(root)})
    return done.stdout.strip()


def _commit(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "work")
    return _git(root, "rev-parse", "HEAD")


def _row(root):
    connection = sqlite3.connect(root / store.STORE_REL)
    try:
        return store.fingerprints(connection)
    finally:
        connection.close()


@pytest.fixture()
def project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    (root / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    _commit(root, {SCHEMA_REL: (REPO / SCHEMA_REL).read_text(encoding="utf-8"), MAP_REL: MAP,
                   "src/a.py": "A = 1\n", "docs/close/T/CL-1.md": "---\nid: CL-1\ntype: close\nstatus: CLOSED\n---\n"})
    return root


def test_a_load_records_one_row_of_its_head_and_its_fingerprints_out_of_the_digest(project):
    digest = store.load(project)["digest"]
    head, prints = _git(project, "rev-parse", "HEAD"), of_commit(project)
    assert _row(project) == {"head": head, "code": prints["code"], "records": prints["records"], "kind": "rebuild"}
    connection = sqlite3.connect(project / store.STORE_REL)
    with connection:
        connection.execute("UPDATE fingerprints SET kind = 'records', head = 'other'")
    connection.close()
    assert store.digest(project) == digest
    assert store_is_of_head(project) is False


def test_the_record_load_after_a_record_only_commit_leaves_the_digest_of_a_full_load(project, tmp_path):
    store.load(project)
    head = _commit(project, {"docs/close/T/CL-2.md": "---\nid: CL-2\ntype: close\nstatus: CLOSED\n---\n"})
    assert store_is_of_head(project) is False
    loaded = store.load_records(project)
    assert loaded["kind"] == "records" and loaded["head"] == head
    assert _row(project)["kind"] == "records" and store_is_of_head(project) is True
    clean = tmp_path / "clean"
    clean.mkdir()
    os.symlink(project / ".git", clean / ".git")
    assert store.load(clean)["digest"] == loaded["digest"] == store.digest(project)


@pytest.mark.parametrize("change", [{"src/a.py": "A = 2\n"}, {MAP_REL: MAP + '  - "docs/**.md"\n'}],
                         ids=["code-commit", "test-map-change"])
def test_the_record_load_refuses_another_code_fingerprint_and_the_store_is_stale(project, change):
    store.load(project)
    _commit(project, change)
    with pytest.raises(GovError) as raised:
        store.load_records(project)
    assert raised.value.code == "STORE_CODE_CHANGED"
    assert store_is_of_head(project) is False


def test_the_record_load_refuses_without_a_store_or_a_fingerprint(project):
    with pytest.raises(GovError) as raised:
        store.load_records(project)
    assert raised.value.code == "STORE_CODE_CHANGED"
    _commit(project, {MAP_REL: "version: 2\n"})
    store.load(project)
    assert _row(project)["code"] is None
    with pytest.raises(GovError) as raised:
        store.load_records(project)
    assert raised.value.code == "STORE_CODE_CHANGED"


def test_without_fingerprints_only_a_rebuild_of_head_is_fresh(project):
    _commit(project, {MAP_REL: "version: 2\n"})
    store.load(project)
    assert store_is_of_head(project) is True
    connection = sqlite3.connect(project / store.STORE_REL)
    with connection:
        connection.execute("UPDATE fingerprints SET kind = 'records'")
    connection.close()
    assert store_is_of_head(project) is False


def test_a_store_without_the_row_is_judged_by_its_commits_alone(project):
    store.load(project)
    connection = sqlite3.connect(project / store.STORE_REL)
    with connection:
        connection.execute("DROP TABLE fingerprints")
    connection.close()
    assert store_is_of_head(project) is True
    _commit(project, {"docs/close/T/CL-2.md": "two\n"})
    assert store_is_of_head(project) is False


def test_a_fingerprints_table_without_its_one_row_is_stale(project):
    store.load(project)
    connection = sqlite3.connect(project / store.STORE_REL)
    with connection:
        connection.execute("DELETE FROM fingerprints")
    connection.close()
    assert store_is_of_head(project) is False
