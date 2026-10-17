"""Builder tests for the durable scratch root in the guard (W2-50, DEC-728, DEC-743).

Regression evidence only (DEC-136). Every case has a temporary HOME and a
temporary project; the real ``~/gov-os-runs`` is never named.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.guard import runs  # noqa: E402
from gov.guard.decide import decide  # noqa: E402


def _ticket(tk, status="in_progress", ref=None):
    lines = ["---", f"id: {tk}", f"status: {status}"] + ([f"external-ref: {ref}"] if ref else [])
    return "\n".join(lines + ["role: engineer", "allowed_paths:", "- src/**", "---", ""])


@pytest.fixture
def box(tmp_path, monkeypatch):
    home, project = tmp_path / "home", tmp_path / "project"
    (project / ".tickets").mkdir(parents=True)
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    for tk, status, ref in (("TST-a001", "in_progress", "W2-90"), ("TST-a002", "in_progress", None),
                            ("TST-a003", "closed", "W2-93")):
        (project / ".tickets" / f"{tk}.md").write_text(_ticket(tk, status, ref), encoding="utf-8")
    return home, project


def _decide(project, tool, value, role="engineer", ticket="TST-a001"):
    tool_input = {"command": value} if tool == "Bash" else {"file_path": str(value), "content": "x"}
    return decide(tool, tool_input, str(project), role, ticket, cwd=str(project), flag="absent")[0]


def test_the_folder_is_the_external_ref_or_the_tk_id(box):
    home, project = box
    root = os.path.join(os.path.realpath(home), runs.ROOT_NAME)
    assert runs.root() == root
    assert runs.own_folder(str(project), "TST-a001", "engineer") == os.path.join(root, "W2-90")
    assert runs.own_folder(str(project), "TST-a002", "research") == os.path.join(root, "TST-a002")


@pytest.mark.parametrize("ticket, role", (("TST-a003", "engineer"), ("TST-a001", "ticket-lead"), ("", "engineer"),
                                          (None, "engineer"), ("TST-zzzz", "engineer"), ("TST-a001", None)))
def test_no_folder_without_a_known_role_and_a_ticket_in_progress(box, ticket, role):
    assert runs.own_folder(str(box[1]), ticket, role) is None


def test_a_root_that_is_a_link_gives_no_folder(box, tmp_path):
    (tmp_path / "elsewhere").mkdir()
    (box[0] / runs.ROOT_NAME).symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    assert runs.own_folder(str(box[1]), "TST-a001", "engineer") is None


def test_the_guard_opens_the_own_folder_only(box):
    home, project = box
    root = home / runs.ROOT_NAME
    assert _decide(project, "Write", root / "W2-90" / "a" / "f.txt") == "allow"
    assert _decide(project, "Bash", f"mkdir -p {root / 'W2-90' / 'clone'}") == "allow"
    for target in (root / "W2-91" / "f.txt", root / "f.txt", root, root / "W2-90" / ".." / "f.txt"):
        assert _decide(project, "Write", target) == "deny", target
    assert _decide(project, "Write", root / "W2-90" / "f.txt", role="ticket-lead") == "deny"
    assert _decide(project, "Write", root / "W2-93" / "f.txt", ticket="TST-a003") == "deny"


def test_a_hard_link_in_the_own_folder_is_refused(box, tmp_path):
    own = box[0] / runs.ROOT_NAME / "W2-90"
    own.mkdir(parents=True)
    (tmp_path / "outside.txt").write_text("x", encoding="utf-8")
    os.link(tmp_path / "outside.txt", own / "hard.txt")
    assert _decide(box[1], "Write", own / "hard.txt") == "deny"
    assert _decide(box[1], "Bash", f"echo x > {own / 'hard.txt'}") == "deny"


def test_rmdir_is_judged_for_the_root_only(box):
    home, project = box
    root = home / runs.ROOT_NAME
    (root / "W2-90" / "empty").mkdir(parents=True)
    (project / "docs" / "empty").mkdir(parents=True)
    for spelling in (f"{root}", f"{root}/", f"{root}/.", f"{root}/W2-90/..", "~/gov-os-runs"):
        assert _decide(project, "Bash", f"rmdir {spelling}") == "deny", spelling
    assert _decide(project, "Bash", f"rmdir {root / 'W2-90' / 'empty'}") == "allow"
    assert _decide(project, "Bash", f"rmdir {project / 'docs' / 'empty'}") == "allow"
