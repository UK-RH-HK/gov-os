"""Builder tests for ``gov pause`` (W1-28).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: an empty ``GOV_ROLE`` is a role, not the owner, and a commit
of the ticket made after a rollback is the only one a second rollback reverts.
Every project is a temporary git repository made here.
"""
from __future__ import annotations

import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.pause import command  # noqa: E402

TICKET = "TST-a001"


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout


def _commit(root, rel, text):
    (root / rel).write_text(text, encoding="utf-8")
    _git(root, "add", "--", rel)
    _git(root, "commit", "-q", "-m", f"change {rel}", "--trailer", f"Task: {TICKET}")
    return _git(root, "rev-parse", "HEAD").strip()


@pytest.fixture
def project(tmp_path, monkeypatch):
    assert REPO not in (tmp_path, *tmp_path.parents)
    monkeypatch.delenv("GOV_ROLE", raising=False)
    _git(tmp_path, "init", "-q")
    for key, value in (("user.name", "builder test"), ("user.email", "builder@example.invalid"),
                       ("commit.gpgsign", "false")):
        _git(tmp_path, "config", key, value)
    (tmp_path / ".tickets").mkdir()
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    (tmp_path / ".tickets" / f"{TICKET}.md").write_text(f"---\nid: {TICKET}\nstatus: in_progress\n---\n# A ticket\n",
                                                        encoding="utf-8")
    _git(tmp_path, "add", "--", ".gitignore", ".tickets")
    _git(tmp_path, "commit", "-q", "-m", "a project")
    return tmp_path


def _pause(root, **options):
    return command.run(root, Namespace(**{"off": False, "cancel_agents": False, "rollback": None, **options}), {})


@pytest.mark.parametrize("options", ({}, {"off": True}, {"cancel_agents": True}, {"rollback": TICKET}))
def test_an_empty_gov_role_is_refused_and_sets_nothing(project, monkeypatch, options):
    monkeypatch.setenv("GOV_ROLE", "")
    with pytest.raises(GovError) as refusal:
        _pause(project, **options)
    assert refusal.value.code == "PAUSE_REFUSED" and not (project / ".gov-runtime").exists()


def test_a_second_rollback_reverts_only_what_was_committed_since_the_first(project):
    first = _commit(project, "a.txt", "a\n")
    assert _pause(project, rollback=TICKET)["reverted"] == [first]
    second = _commit(project, "b.txt", "b\n")
    assert _pause(project, rollback=TICKET)["reverted"] == [second]
    assert not (project / "a.txt").exists() and not (project / "b.txt").exists()
    assert _git(project, "status", "--porcelain") == "" and (project / ".gov-runtime" / "freeze").is_file()
