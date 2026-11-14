"""Builder tests for W2-42a R4 and R5: a revision-colon-path (``<rev>:<path>``) in ``git show`` or on a side of
``git diff`` is judged as a read of its path; a revision git does not resolve, or one given at run time, gets a ruled
refusal, never an exception; a write tool's path that is no path is refused by a rule; a genuine fault (git missing)
still fails closed.

Regression evidence only (DEC-136). Every project is a temporary git repository.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.decide import NO_PATH_REFUSAL, decide  # noqa: E402
from gov.guard.reads import (HIDDEN_REFUSAL, REV_REFUSAL, SECRET_REFUSAL,  # noqa: E402
                             TESTS_REFUSAL, _Judge, parts, policy_refusal)

TICKET = "DAEO-t42b"
SETS = ("evaluation_sets:\n  m:\n    visible: [docs/q.md]\n"
        "    hidden: [eval/hidden/**]\n    measures:\n      roles: [research]\n")


def _put(root: Path, rel: str, text: str = "x\n") -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


@pytest.fixture()
def project(tmp_path, monkeypatch):
    home = tmp_path / "home"
    root = home / "proj"
    monkeypatch.setenv("HOME", str(home))
    _put(root, f".tickets/{TICKET}.md", f"---\nid: {TICKET}\nwbs_id: W2-95\nstatus: in_progress\n"
                                        "role: engineer\nallowed_paths:\n- src/**\n---\n")
    for rel in ("docs/q.md", "docs/n.md", ".env", "eval/hidden/a.yaml", "tests/acceptance/W2-95/test_f.py"):
        _put(root, rel)
    _put(root, "governance/project/held-out.yaml", "held_out_paths:\n  - /nowhere/held\n")
    _put(root, "governance/project/path-map.yaml", "namespaces: {}\n" + SETS)
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    _git(root, "branch", "w2/integrate")
    _put(root, "docs/q.md", "two\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "two")
    return root


def judge(root: Path, role: str, command: str, cwd: Path | None = None) -> str:
    """The judge itself, so an exception it raises fails the case."""
    protected = parts(str(root), role, TICKET, {})
    return _Judge(str(root), protected).tool("Bash", {"command": command}, str(cwd or root))


# -- R4: blob refs read as their paths -----------------------------------------------------------------------------

@pytest.mark.parametrize("command", [
    "git diff HEAD:docs/q.md HEAD:docs/n.md",
    "git diff HEAD~1:docs/q.md HEAD:docs/q.md",
    "git diff main~1:docs/q.md main:docs/n.md",
    "git show HEAD:docs/q.md",
    "git diff HEAD:docs/q.md docs/n.md",
    "git -C {root} diff HEAD:docs/q.md HEAD:docs/n.md",
])
def test_a_blob_ref_of_a_visible_path_is_allowed(project, command):
    assert judge(project, "research", command.format(root=project)) == ""


def test_blob_refs_relative_to_the_folder_are_allowed(project):
    assert judge(project, "research", "git diff HEAD:./q.md HEAD:./n.md", project / "docs") == ""


def test_an_engineer_s_diff_of_two_visible_blobs_is_not_a_whole_tree_diff(project):
    assert judge(project, "engineer", "git diff HEAD:docs/q.md HEAD:docs/n.md") == ""
    # A diff of revisions still shows the whole tree, the acceptance folder in it.
    assert judge(project, "engineer", "git diff HEAD~1 HEAD") == TESTS_REFUSAL


@pytest.mark.parametrize("command, rule", [
    ("git diff HEAD:eval/hidden/a.yaml HEAD:docs/q.md", HIDDEN_REFUSAL),
    ("git diff HEAD:docs/q.md HEAD:eval/hidden/a.yaml", HIDDEN_REFUSAL),
    ("git diff HEAD:eval/hidden/a.yaml docs/q.md", HIDDEN_REFUSAL),
    ("git diff HEAD:eval/hidden/a.yaml -- docs/q.md", HIDDEN_REFUSAL),
    ("git show :0:eval/hidden/a.yaml", HIDDEN_REFUSAL),
    ("git diff HEAD:.env HEAD:docs/q.md", SECRET_REFUSAL),
    ("git diff HEAD:.env docs/q.md", SECRET_REFUSAL),
    ("git diff HEAD:docs/q.md -- .env", SECRET_REFUSAL),
])
def test_a_blob_ref_of_a_refused_path_is_refused_by_its_rule(project, command, rule):
    assert judge(project, "research", command) == rule


def test_a_tree_on_a_side_of_a_diff_is_judged_by_the_files_it_shows(project):
    assert judge(project, "research", "git diff HEAD~1:docs HEAD:docs") == ""
    assert judge(project, "research", "git diff HEAD:eval HEAD:docs") == HIDDEN_REFUSAL
    # A hidden file in the revision's tree only, gone from the working tree, is still found.
    (project / "eval/hidden/a.yaml").unlink()
    assert judge(project, "research", "git diff HEAD:eval HEAD:docs") == HIDDEN_REFUSAL


def test_a_secret_blob_ref_in_a_diff_is_refused_to_every_role(project):
    assert judge(project, "orchestrator", "git diff HEAD:.env HEAD:docs/q.md") == SECRET_REFUSAL


def test_the_engineer_s_own_folder_by_blob_ref_is_refused(project):
    _put(project, "tests/acceptance/W2-95/test_f.py", "changed\n")
    _git(project, "commit", "-qam", "tests")
    assert judge(project, "engineer",
                 "git diff HEAD:tests/acceptance/W2-95/test_f.py HEAD:docs/q.md") == TESTS_REFUSAL


@pytest.mark.parametrize("command", [
    "git diff nosuch:docs/q.md HEAD:docs/n.md",
    "git diff HEAD:docs/q.md nosuch:docs/n.md",
    "git diff HEAD:docs/missing.md HEAD:docs/q.md",
    "git show nosuchref:docs/q.md",
    "git show HEAD:docs/missing.md",
])
def test_a_blob_ref_that_names_nothing_is_refused_by_a_rule(project, command):
    assert judge(project, "research", command) == REV_REFUSAL


# -- R5: what the judge cannot resolve gets a ruled refusal --------------------------------------------------------

@pytest.mark.parametrize("command", [
    "git diff HEAD:", "git diff :", "git diff ^", "git show :/", "git diff HEAD HEAD:",
    "git diff HEAD: HEAD:", 'git diff HEAD~1:"" HEAD:""', "git diff $W242A_UNSET",
    'git log -p "$(git rev-parse HEAD)"', "git log --stdin -p", "git log -p nosuchref",
    "git diff nosuch", "git diff HEAD..nosuch", "git show nosuch..HEAD", "git diff ls |",
    "git diff find -name", "cd docs && git diff HEAD:", "echo $(git diff :)", "git show diff",
])
def test_a_revision_the_judge_cannot_resolve_gets_a_ruled_refusal(project, command):
    assert judge(project, "research", command) == REV_REFUSAL


@pytest.mark.parametrize("command", ["git log -p HEAD~1..HEAD", "git show HEAD", "git diff HEAD~1 HEAD",
                                     "git show :/two"])
def test_a_revision_that_resolves_is_judged_as_before(project, command):
    assert judge(project, "research", command) == ""


def test_a_hidden_change_in_a_resolved_revision_is_still_refused(project):
    _put(project, "eval/hidden/a.yaml", "changed\n")
    _git(project, "commit", "-qam", "hidden")
    assert judge(project, "research", "git log -p HEAD") == HIDDEN_REFUSAL
    assert judge(project, "research", "git show HEAD") == HIDDEN_REFUSAL


def test_git_missing_still_fails_closed(project, monkeypatch, tmp_path):
    empty = tmp_path / "nobin"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    for command in ("git log -p HEAD", "git show HEAD:docs/q.md", "git diff HEAD:docs/q.md HEAD:docs/n.md"):
        why = policy_refusal("Bash", {"command": command}, str(project), str(project), "research", TICKET)
        assert "fail closed" in why, command


# -- R5: a write tool's path that is no path -----------------------------------------------------------------------

@pytest.mark.parametrize("tool, tool_input", [
    ("Write", {"file_path": "src/a\x00b.py", "content": ""}),
    ("Edit", {"file_path": "\x00", "old_string": "a", "new_string": "b"}),
    ("Write", {"file_path": 1, "content": ""}),
    ("Edit", {"file_path": ["src/ok.py"], "old_string": "a", "new_string": "b"}),
    ("NotebookEdit", {"notebook_path": {"a": 1}, "new_source": ""}),
    ("Read", {"file_path": "docs/\x00q.md"}),
])
def test_a_tool_path_that_is_no_path_is_refused_by_a_rule(project, tool, tool_input):
    assert decide(tool, tool_input, str(project), "engineer", TICKET) == ("deny", NO_PATH_REFUSAL)


def test_a_plain_write_path_is_judged_as_before(project):
    assert decide("Write", {"file_path": "src/ok.py", "content": ""}, str(project), "engineer",
                  TICKET) == ("allow", "")
