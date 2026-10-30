"""Builder tests for the register as its entries (W2-87; DEC-952 item 1, DEC-423).

Regression evidence only (DEC-136). A chunk of the register is the entry whose span holds it, never the register's
last entry: its own entry joins the closure, and no register chunk is dropped for another entry's status. Every
store is built in a temporary git repository, with the secret filter replaced and no vectors.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import records, store  # noqa: E402
from gov.retrieval import authority, lexical, retrieve  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
REGISTER = "decisions/REGISTER.md"
TEXT = ("# Decision register\n\nThe register's preface.\n\n"
        "### DEC-001 — The pool\n- **Status:** ACCEPTED\n- **Decision:** the pool holds marigold workers.\n\n"
        "### DEC-002 — The queue\n- **Status:** DEPRECATED\n- **Decision:** the queue holds juniper tasks.\n\n"
        "### DEC-003 — The pool again\n- **Status:** SUPERSEDED\n- **Decision:** the pool held saffron workers.\n")


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A repository whose path map names a register of three entries, the last superseded, loaded and indexed."""
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    files = {".gitignore": ".gov-runtime/\n", "governance/project/path-map.yaml": f"decision_register: {REGISTER}\n",
             REGISTER: TEXT}
    for rel, text in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the register"]):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(tmp_path)})
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    return tmp_path


def _line(text):
    return TEXT.split("\n").index(text) + 1


def test_a_register_chunk_maps_to_the_entry_whose_span_holds_it(project):
    entry_of = authority.register_entries_of(records.records(project), [], project)
    assert entry_of(REGISTER, _line("The register's preface.")) is None
    assert entry_of(REGISTER, _line("### DEC-001 — The pool"))["id"] == "DEC-001"
    assert entry_of(REGISTER, _line("- **Decision:** the queue holds juniper tasks.")) == {
        "id": "DEC-002", "type": "decision", "status": "DEPRECATED", "current": False, "reason": "DEPRECATED",
        "start_line": 9, "end_line": 11}
    assert entry_of(REGISTER, _line("- **Decision:** the queue holds juniper tasks.") + 1) is None, "a blank line"
    assert entry_of(REGISTER, _line("### DEC-003 — The pool again"))["reason"] == "SUPERSEDED"
    assert entry_of("notes/other.md", 1) is None
    assert entry_of(REGISTER, _line("### DEC-001 — The pool"))["current"] is True


def test_the_target_of_a_supersedes_edge_is_not_current(project):
    edges = [{"type": "SUPERSEDES", "source": "DEC-003", "target": "DEC-001"},
             {"type": "CONSTRAINS", "source": "DEC-001", "target": "DEC-002"}]
    entry = authority.register_entries_of(records.records(project), edges, project)(REGISTER, 6)
    assert (entry["id"], entry["current"], entry["reason"]) == ("DEC-001", False, "SUPERSEDED")
    assert authority.register_path(records.records(project)) == REGISTER


def test_no_register_chunk_is_dropped_for_the_last_entry_s_status(project):
    bundle = retrieve.retrieve(project, "marigold")
    assert [item["path"] for item in bundle["evidence"]] == [REGISTER]
    assert bundle["merge"]["dropped"] == []


def test_a_register_chunk_joins_the_closure_by_its_own_entry(project):
    by_route = retrieve.retrieve(project, "nothing matches this", ids=["DEC-001"])["evidence"]
    assert [(item["start_line"], item["routes"]) for item in by_route] == [(5, ["closure"])]
