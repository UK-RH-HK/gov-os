"""Builder tests for W2-42a R4 and R5, second batch: in ``<rev>:<path>`` the path starts at the top of the tree
``<rev>`` names, so only a commit (or the index) places it at the repository's top, and a subtree's id cannot be placed
(a ruled refusal for a session with a refused part, in git diff, git show and git cat-file alike); an object named by
its id alone that git prints as a file's text (``git cat-file blob <id>``, ``-p`` of a blob) is refused the same way;
git's own ``--output`` (git diff, show, log) is a write the write rules judge, and its file is no revision word.

Regression evidence only (DEC-136). Every project is a temporary git repository.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.bash_writes import _more_targets  # noqa: E402
from gov.guard.decide import decide  # noqa: E402
from gov.guard.reads import (HIDDEN_REFUSAL, PLACE_REFUSAL, REV_REFUSAL,  # noqa: E402
                             _Judge, parts)

TICKET = "DAEO-t42c"
SETS = ("evaluation_sets:\n  m:\n    visible: [docs/q.md]\n"
        "    hidden: [eval/hidden/**]\n    measures:\n      roles: [research]\n")


def _put(root: Path, rel: str, text: str = "x\n") -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture()
def project(tmp_path, monkeypatch):
    home = tmp_path / "home"
    root = home / "proj"
    monkeypatch.setenv("HOME", str(home))
    _put(root, f".tickets/{TICKET}.md", f"---\nid: {TICKET}\nwbs_id: W2-95\nstatus: in_progress\n"
                                        "role: engineer\nallowed_paths:\n- src/**\n---\n")
    for rel in ("docs/q.md", "docs/n.md", "src/a.py", "tests/acceptance/W2-95/test_f.py"):
        _put(root, rel)
    _put(root, "eval/hidden/a.yaml", "the hidden text\n")
    _put(root, "governance/project/held-out.yaml", "held_out_paths:\n  - /nowhere/held\n")
    _put(root, "governance/project/path-map.yaml", "namespaces: {}\n" + SETS)
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    _git(root, "branch", "w2/integrate")
    _put(root, "docs/n.md", "y\n")  # HEAD's own patch touches no refused part
    _git(root, "commit", "-qam", "second")
    return root


def judge(root: Path, role: str, command: str, cwd: Path | None = None) -> str:
    """The judge itself, so an exception it raises fails the case."""
    protected = parts(str(root), role, TICKET, {})
    return _Judge(str(root), protected).tool("Bash", {"command": command}, str(cwd or root))


def ids(root: Path) -> dict[str, str]:
    return {"eval": _git(root, "rev-parse", "HEAD:eval"),
            "hidden": _git(root, "rev-parse", "HEAD:eval/hidden"),
            "docs": _git(root, "rev-parse", "HEAD:docs"),
            "blob": _git(root, "rev-parse", "HEAD:eval/hidden/a.yaml"),
            "visible": _git(root, "rev-parse", "HEAD:docs/q.md")}


# -- a path under a tree that is not a commit's top cannot be placed -------------------------------------------------

@pytest.mark.parametrize("role", ["research", "engineer"])
@pytest.mark.parametrize("command", [
    "git diff {eval}:hidden/a.yaml HEAD:docs/q.md",
    "git diff HEAD:docs/q.md {eval}:hidden/a.yaml",
    "git diff {hidden}:a.yaml HEAD:docs/q.md",
    "git show {eval}:hidden/a.yaml",
    "git show {hidden}:a.yaml",
    "git cat-file -p {eval}:hidden/a.yaml",
    "git cat-file blob {hidden}:a.yaml",
    "git cat-file -t {hidden}:a.yaml",
    "git show {docs}:q.md",
])
def test_a_path_under_a_subtree_s_id_is_a_ruled_refusal(project, role, command):
    assert judge(project, role, command.format(**ids(project))) == PLACE_REFUSAL


@pytest.mark.parametrize("command", [
    "git show HEAD:docs/q.md", "git show HEAD^{{tree}}:docs/q.md", "git show :docs/q.md",
    "git show :0:docs/q.md", "git diff HEAD~0:docs/q.md HEAD:docs/n.md", "git cat-file -p HEAD:docs/q.md",
    "git show main:docs/q.md",
])
def test_a_path_under_a_commit_or_the_index_is_placed_at_the_top(project, command):
    assert judge(project, "research", command.format(**ids(project))) == ""


def test_a_hidden_path_under_a_commit_is_still_refused_by_its_rule(project):
    assert judge(project, "research", "git cat-file -p HEAD:eval/hidden/a.yaml") == HIDDEN_REFUSAL


def test_a_subtree_s_path_is_open_to_a_session_with_no_refused_part(project):
    assert parts(str(project), "orchestrator", TICKET, {}) == []
    assert judge(project, "orchestrator", "git show {docs}:q.md".format(**ids(project))) == ""


def test_an_unresolved_revision_keeps_its_ruled_refusal(project):
    assert judge(project, "research", "git show nosuch:docs/q.md") == REV_REFUSAL


# -- an object named by its blob id alone, shown as text --------------------------------------------------------------

@pytest.mark.parametrize("role", ["research", "engineer"])
@pytest.mark.parametrize("command", [
    "git cat-file blob {blob}", "git cat-file -p {blob}", "git cat-file blob {visible}",
    "git cat-file -p {visible}", "git -C {root} cat-file -p {blob}",
])
def test_a_blob_id_alone_shown_as_text_is_a_ruled_refusal(project, role, command):
    assert judge(project, role, command.format(root=project, **ids(project))) == PLACE_REFUSAL


@pytest.mark.parametrize("command", [
    "git cat-file -t {blob}", "git cat-file -s {blob}", "git cat-file -e {blob}", "git cat-file -p HEAD",
    "git cat-file commit HEAD", "git cat-file -p {docs}",
])
def test_a_blob_id_s_type_size_or_a_commit_object_stays_allowed(project, command):
    assert judge(project, "research", command.format(**ids(project))) == ""


def test_a_blob_id_is_open_to_a_session_with_no_refused_part(project):
    assert judge(project, "orchestrator", "git cat-file -p {blob}".format(**ids(project))) == ""


# -- git's own --output ------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("args, target", [
    (["diff", "--output=o.txt", "HEAD"], "o.txt"),
    (["diff", "HEAD", "--output", "o.txt"], "o.txt"),
    (["show", "--output=o.txt", "HEAD:docs/q.md"], "o.txt"),
    (["log", "-p", "--output", "o.txt", "HEAD~1..HEAD"], "o.txt"),
    (["whatchanged", "--output=o.txt"], "o.txt"),
])
def test_git_s_output_option_is_a_write_target(args, target):
    assert _more_targets("git", args, "/w") == [(target, "/w")]


def test_git_s_output_option_resolves_after_dash_c():
    assert _more_targets("git", ["-C", "sub", "diff", "--output=o.txt"], "/w") == [("o.txt", "/w/sub")]


@pytest.mark.parametrize("args", [
    ["diff", "--output-indicator-new=+"], ["status", "--output=o.txt"], ["diff", "--", "--output=x"],
])
def test_no_output_write_where_git_does_not_take_it(args):
    assert _more_targets("git", args, "/w") == []


@pytest.mark.parametrize("command", [
    "git diff --output tests/acceptance/X/z.txt HEAD:docs/q.md HEAD:docs/n.md",
    "git diff --output=tests/acceptance/X/z.txt HEAD:docs/q.md HEAD:docs/n.md",
    "cd tests && git show --output acceptance/X/z.txt HEAD:docs/q.md",
    "git -C {root} log -p --output=tests/acceptance/X/z.txt HEAD~1..HEAD -- docs",
])
def test_git_s_output_into_the_acceptance_folder_is_refused_by_the_write_rule(project, command):
    got = decide("Bash", {"command": command.format(root=project)}, str(project), "engineer", TICKET)
    assert got[0] == "deny" and "tests/acceptance/X/z.txt" in got[1], got


def test_git_s_output_into_the_ticket_s_paths_is_allowed(project):
    got = decide("Bash", {"command": "git diff --output src/o.txt HEAD:docs/q.md HEAD:docs/n.md"},
                 str(project), "engineer", TICKET)
    assert got == ("allow", "")


@pytest.mark.parametrize("command", ["git diff --output o.txt HEAD~0 HEAD", "git show --output o.txt HEAD",
                                     "git log -p --output o.txt HEAD~1..HEAD"])
def test_the_output_file_is_no_revision_word(project, command):
    assert judge(project, "research", command) == ""
