"""Builder tests for W2-201 fix X8 (DEC-1219 (5)): a worker's fix gets the run folder an in_progress worker gets.

Regression evidence only. HOME and the project are temporary; the real ``~/gov-os-runs`` is never named.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.util import runs  # noqa: E402

TICKET = "---\nid: TST-a001\nstatus: {status}\nexternal-ref: W2-90\nrole: engineer\n---\n"


@pytest.fixture
def project(tmp_path, monkeypatch):
    home, project = tmp_path / "home", tmp_path / "project"
    for folder in (home, project / ".tickets", project / ".git"):
        folder.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))

    def plant(status: str) -> str:
        (project / ".tickets" / "TST-a001.md").write_text(TICKET.format(status=status), encoding="utf-8")
        return str(project)

    plant.home = home
    return plant


@pytest.mark.parametrize("status", ("closed", "open", "in_progress"))
def test_a_fix_gets_the_folder_whatever_the_status(project, status):
    root = project(status)
    want = os.path.join(os.path.realpath(project.home), runs.ROOT_NAME, "W2-90")
    assert runs.folder(root, "TST-a001", "engineer", kind="fix") == want


@pytest.mark.parametrize("kind", (None, "feature"))
@pytest.mark.parametrize("status", ("closed", "open"))
def test_a_feature_on_a_ticket_not_in_progress_gets_none(project, status, kind):
    assert runs.folder(project(status), "TST-a001", "engineer", kind=kind) is None


def test_a_chore_gets_none(project):
    assert runs.folder(project("in_progress"), None, "engineer", kind="chore") is None


def test_a_fix_keeps_every_other_rule(project, tmp_path):
    root = project("closed")
    assert runs.folder(root, "TST-a001", "ticket-lead", kind="fix") is None  # a role with no folder
    assert runs.folder(root, "TST-zzzz", "engineer", kind="fix") is None  # an unknown ticket
    (tmp_path / "project" / ".tickets" / "TST-a002.md").write_text(
        TICKET.format(status="closed").replace("TST-a001", "TST-a002"), encoding="utf-8")
    assert runs.folder(root, "TST-a001", "engineer", kind="fix") is None  # the name given twice


def test_own_folder_of_a_fix_is_the_marked_folder(project):
    root = project("closed")
    name = runs.folder(root, "TST-a001", "engineer", kind="fix")
    assert runs.own_folder(root, "TST-a001", "engineer", kind="fix") is None  # not made yet
    runs.make(name, root)
    assert runs.own_folder(root, "TST-a001", "engineer", kind="fix") == name
    assert runs.own_folder(root, "TST-a001", "engineer") is None  # a feature on a closed ticket: none
