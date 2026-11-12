"""Builder tests for the decision checker's speed path (W2-45, Interface item 3).

Regression evidence only (DEC-136). The checker learns once, in one pass of git, which Markdown paths each commit
changes, and passes over a single-parent commit that leaves a decision's file as its parent has it, without reading
it. These cases pin that the pass gives the same answers as reading every commit (the pass switched off), for the
changes the walk meets between the commit that set a decision and ``HEAD``: commits that leave the file alone, a
revision, a move, a demotion and a merge; and that the reads no longer grow with the commits that leave it alone.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import decisions  # noqa: E402
from gov.decisions import checker  # noqa: E402

ADR = "docs/adr/ADR-0001.md"
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid",
        "GIT_AUTHOR_DATE": "2026-10-04T12:00:00+00:00", "GIT_COMMITTER_DATE": "2026-10-04T12:00:00+00:00"}


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True,
                          env={**_ENV, "HOME": str(root)}).stdout.strip()


def _record(status, title="t", record_id="ADR-0001"):
    return f"---\nid: {record_id}\ntype: decision\nstatus: {status}\ntitle: {title}\n---\n"


def _commit(root, files, role, *removed):
    for rel in removed:
        _git(root, "rm", "-q", rel)
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "--allow-empty", "-m", "c", "--trailer", f"Role: {role}")


def _others(root, count):
    for number in range(count):
        _commit(root, {f"src/m{number}.py": f"x = {number}\n"}, "engineer")


@pytest.fixture()
def project(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    return tmp_path


def _both(root, monkeypatch):
    """The findings with the speed path, and the findings with every commit read as before."""
    fast = [dict(finding) for finding in decisions.check(root)]
    monkeypatch.setattr(checker, "_changes", lambda _root: {})
    return fast, decisions.check(root)


def _owner_sets_then_others(root):
    _commit(root, {ADR: _record("ACTIVE")}, "owner")
    _others(root, 6)


def _agent_sets_then_owner_elsewhere(root):
    _commit(root, {ADR: _record("ACTIVE")}, "engineer")
    _commit(root, {"README.md": "# p\n"}, "owner")
    _others(root, 4)


def _owner_sets_agent_revises_then_others(root):
    _commit(root, {ADR: _record("ACTIVE")}, "owner")
    _others(root, 3)
    _commit(root, {ADR: _record("ACTIVE", title="revised")}, "engineer")
    _others(root, 3)


def _demoted_then_set_again_by_an_agent(root):
    _commit(root, {ADR: _record("ACTIVE")}, "owner")
    _commit(root, {ADR: _record("PROPOSED")}, "owner")
    _others(root, 2)
    _commit(root, {ADR: _record("ACTIVE")}, "engineer")
    _others(root, 2)


def _moved_by_an_agent_then_others(root):
    _commit(root, {ADR: _record("ACTIVE")}, "owner")
    _others(root, 3)
    _git(root, "mv", ADR, "docs/adr/moved.md")
    _commit(root, {}, "engineer")
    _others(root, 3)


def _removed_and_added_again(root):
    _commit(root, {ADR: _record("ACTIVE")}, "owner")
    _others(root, 2)
    _commit(root, {}, "owner", ADR)
    _commit(root, {ADR: _record("ACTIVE")}, "engineer")
    _others(root, 2)


def _merged_branch_of_the_owner(root):
    _commit(root, {"README.md": "# p\n"}, "engineer")
    _git(root, "checkout", "-q", "-b", "owner")
    _commit(root, {ADR: _record("ACTIVE")}, "owner")
    _others(root, 2)
    _git(root, "checkout", "-q", "main")
    _commit(root, {"docs/other.md": "# o\n"}, "engineer")
    _git(root, "merge", "-q", "--no-ff", "owner", "-m", "m\n\nRole: engineer")
    _others(root, 3)


SCENARIOS = [_owner_sets_then_others, _agent_sets_then_owner_elsewhere, _owner_sets_agent_revises_then_others,
             _demoted_then_set_again_by_an_agent, _moved_by_an_agent_then_others, _removed_and_added_again,
             _merged_branch_of_the_owner]


@pytest.mark.parametrize("build", SCENARIOS, ids=lambda build: build.__name__.strip("_"))
def test_the_speed_path_gives_the_findings_of_reading_every_commit(project, monkeypatch, build):
    build(project)
    fast, slow = _both(project, monkeypatch)
    assert fast == slow


@pytest.mark.parametrize("build, codes", [
    (_owner_sets_then_others, []),
    (_agent_sets_then_owner_elsewhere, [("ACTIVE_UNAPPROVED", ["ADR-0001"])]),
    (_owner_sets_agent_revises_then_others, []),
    (_demoted_then_set_again_by_an_agent, [("ACTIVE_UNAPPROVED", ["ADR-0001"])]),
    (_moved_by_an_agent_then_others, []),
    (_removed_and_added_again, [("ACTIVE_UNAPPROVED", ["ADR-0001"])]),
    (_merged_branch_of_the_owner, []),
], ids=lambda value: value.__name__.strip("_") if callable(value) else "answer")
def test_the_answers_the_speed_path_keeps(project, build, codes):
    """The answers themselves, so that the parity above is not two wrong answers that agree."""
    build(project)
    assert [(finding["code"], finding["ids"]) for finding in decisions.check(project)] == codes


def test_the_pass_lists_single_parent_commits_with_their_markdown_paths_only(project):
    _commit(project, {ADR: _record("ACTIVE"), "src/a.py": "a\n"}, "owner")
    first = _git(project, "rev-parse", "HEAD")
    _git(project, "checkout", "-q", "-b", "side")
    _commit(project, {"docs/side.md": "# s\n"}, "engineer")
    side = _git(project, "rev-parse", "HEAD")
    _git(project, "checkout", "-q", "main")
    _commit(project, {"src/b.py": "b\n"}, "engineer")
    plain = _git(project, "rev-parse", "HEAD")
    _git(project, "merge", "-q", "--no-ff", "side", "-m", "m\n\nRole: engineer")
    merge =_git(project, "rev-parse", "HEAD")
    changes = checker._changes(project)
    assert first not in changes  # a commit with no parent is read
    assert merge not in changes  # so is a merge
    assert changes[side] == (first, frozenset({"docs/side.md"}))
    assert changes[plain] == (first, frozenset())


def test_the_reads_do_not_grow_with_the_commits_that_leave_the_decision_alone(project, monkeypatch):
    reads = []
    original = checker._Objects.read
    monkeypatch.setattr(checker._Objects, "read", lambda self, name: reads.append(name) or original(self, name))
    _commit(project, {ADR: _record("ACTIVE")}, "owner")
    _others(project, 3)
    assert decisions.check(project) == []
    few = len(reads)
    reads.clear()
    _others(project, 40)
    assert decisions.check(project) == []
    assert len(reads) == few


def test_where_git_cannot_give_the_pass_every_commit_is_read_as_before(project, monkeypatch):
    _owner_sets_then_others(project)
    real = checker._git

    def refuse(root, *args):
        if args[0] == "log":
            raise checker.GovError("DECISIONS_GIT_FAILED", "no", {})
        return real(root, *args)

    monkeypatch.setattr(checker, "_git", refuse)
    assert checker._changes(project) == {}
    assert decisions.check(project) == []
