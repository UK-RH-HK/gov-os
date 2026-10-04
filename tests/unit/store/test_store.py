"""Builder tests for the store and record graph (W1-10).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: the graph is read from ``HEAD`` and not from the working tree,
a query before any load and a root that is not a git repository are GovErrors,
and a trailer that names no record is reported with the commit as its source.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import records, store  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402

ADR = "docs/adr/ADR-0001.md"
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}


def _git(root, *args):
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True,
                          env={**_ENV, "HOME": str(root)})
    return done.stdout.strip()


def _write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture()
def project(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _write(tmp_path, ADR, "---\nid: ADR-0001\ntype: decision\nstatus: ACTIVE\n---\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "a decision", "--trailer", "Task: T-404", "--trailer", "Implements: ADR-0001")
    return tmp_path


def test_the_graph_is_read_from_head_not_from_the_working_tree(project):
    before = store.load(project)["digest"]
    _write(project, ADR, "---\nid: ADR-0001\ntype: decision\nstatus: SUPERSEDED\n---\n")
    (project / "docs/adr/ADR-0002.md").write_text("---\nid: ADR-0002\ntype: decision\nstatus: ACTIVE\n---\n")
    assert store.load(project)["digest"] == before
    assert records.active(project) == ["ADR-0001"]


def test_a_query_before_any_load_is_a_gov_error_and_builds_no_store(project):
    with pytest.raises(GovError) as raised:
        records.records(project)
    assert raised.value.code == "STORE_MISSING"
    with pytest.raises(GovError):
        store.digest(project)
    assert not (project / store.STORE_REL).exists()


def test_a_root_that_is_not_a_git_repository_is_a_gov_error(tmp_path):
    with pytest.raises(GovError) as raised:
        store.load(tmp_path)
    assert raised.value.code == "STORE_GIT_FAILED"
    assert not (tmp_path / store.STORE_REL).exists()


def test_a_dangling_trailer_is_reported_with_its_commit_and_is_not_an_edge(project):
    store.load(project)
    head = _git(project, "rev-parse", "HEAD")
    assert records.dangling(project) == [{"type": "TASK", "source": head, "target": "T-404"}]
    assert records.edges(project) == []
    assert records.commits(project, path=ADR) == [{"commit": head, "task": ["T-404"], "implements": ["ADR-0001"]}]
