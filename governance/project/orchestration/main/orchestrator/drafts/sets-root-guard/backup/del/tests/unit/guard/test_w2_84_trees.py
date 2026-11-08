"""Builder tests for W2-84: the hidden part of an evaluation set refused under
every tree of the repository (the main tree, its worktrees, the run clones
under ~/gov-os-runs) and through the object store they share; fail closed
(DEC-950 item 1, DEC-820 (d)).

Regression evidence only (DEC-136).  Everything is planted under a temporary
HOME: the repository, its worktree, the runs root and the clones in it.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard import reads  # noqa: E402
from gov.guard.reads import HIDDEN_REFUSAL, policy_refusal  # noqa: E402

TICKET = "DAEO-t95"
SETS = ("evaluation_sets:\n  m:\n    visible: [docs/q.md]\n"
        "    hidden: [eval/hidden/**]\n    measures:\n      roles: [engineer]\n")


def _put(root: Path, rel: str, text: str = "x\n") -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t",
                           *args], check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture()
def world(tmp_path, monkeypatch):
    """main (holds the hidden part), wt (a worktree on a branch that never
    held it), a plain folder deep in the runs root that holds a copy."""
    home = tmp_path / "home"
    main, wt = home / "main", home / "wt"
    monkeypatch.setenv("HOME", str(home))
    _put(main, f".tickets/{TICKET}.md", f"---\nid: {TICKET}\nwbs_id: W2-95\nstatus: in_progress\n"
                                        "role: engineer\nallowed_paths:\n- src/**\n---\n")
    _put(main, "governance/project/path-map.yaml", "namespaces: {}\n" + SETS)
    _put(main, "src/app/main.py")
    _put(main, "docs/q.md")
    _git(main, "init", "-q", "-b", "main")
    _git(main, "add", "-A")
    _git(main, "commit", "-qm", "base")
    _git(main, "branch", "side")
    _put(main, "eval/hidden/a.yaml", "answer\n")
    _git(main, "add", "-A")
    _git(main, "commit", "-qm", "add the hidden answers")
    _git(main, "worktree", "add", "-q", str(wt), "side")
    _put(wt, "src/app/main.py", "changed\n")
    _git(wt, "commit", "-qam", "unrelated")
    _put(home, "gov-os-runs/W2-61/a/b/repo/eval/hidden/c.yaml")
    return {"home": home, "main": main, "wt": wt, "runs": home / "gov-os-runs"}


def _why(root, tool, tool_input, role="engineer", agent=None):
    return policy_refusal(tool, tool_input, str(root), str(root), role, TICKET, agent)


def _bash(command):
    return "Bash", {"command": command}


@pytest.mark.parametrize("where", ["main/eval/hidden/a.yaml",
                                   "gov-os-runs/W2-61/a/b/repo/eval/hidden/c.yaml"])
def test_every_tree_s_hidden_file_is_refused_from_a_worktree(world, where):
    path = str(world["home"] / where)
    assert _why(world["wt"], "Read", {"file_path": path}) == HIDDEN_REFUSAL
    assert _why(world["wt"], *_bash(f"cat {path}")) == HIDDEN_REFUSAL
    assert _why(world["wt"], *_bash(f"grep -rn answer {Path(path).parents[2]}")) == HIDDEN_REFUSAL


def test_a_search_from_above_every_tree_is_refused_and_the_visible_part_stays_open(world):
    assert _why(world["wt"], "Grep", {"pattern": "x", "path": str(world["home"])}) == HIDDEN_REFUSAL
    assert _why(world["wt"], "Read", {"file_path": str(world["main"] / "docs/q.md")}) == ""
    assert _why(world["wt"], *_bash("grep -rn x src")) == ""


def test_a_link_to_another_tree_is_refused_as_the_tree_is(world, tmp_path):
    (tmp_path / "link").symlink_to(world["main"])
    assert _why(world["wt"], "Read", {"file_path": str(tmp_path / "link/eval/hidden/a.yaml")}) \
        == HIDDEN_REFUSAL
    assert _why(world["wt"], "Grep", {"pattern": "x", "path": str(tmp_path / "link")}) \
        == HIDDEN_REFUSAL


def test_a_missing_worktree_folder_is_still_a_tree(world):
    gone = world["home"] / "gone"
    _git(world["main"], "worktree", "add", "-q", str(gone), "-b", "gone")
    os.rename(gone, world["home"] / "elsewhere")
    assert _why(world["wt"], "Read", {"file_path": str(gone / "eval/hidden/a.yaml")}) \
        == HIDDEN_REFUSAL
    assert _why(world["wt"], "Grep", {"pattern": "x", "path": str(world["wt"])}) == ""


@pytest.mark.parametrize("command", [
    "git show main:eval/hidden/a.yaml", "git cat-file -p main:eval/hidden/a.yaml",
    "git show main", "git log -p main", "git diff main", "git diff HEAD main -- eval",
    "git show ':/add the hidden'", "git grep answer main", "git grep -e answer main:eval",
    "git archive main", "git log -p --all -1", "git log -p HEAD --not main",
])
def test_a_revision_of_the_shared_store_that_holds_the_hidden_part_is_refused(world, command):
    assert _why(world["wt"], *_bash(command)) == HIDDEN_REFUSAL


def test_another_tree_is_judged_by_its_own_part_under_git_c(world):
    assert _why(world["wt"], *_bash(f"git -C {world['main']} grep answer")) == HIDDEN_REFUSAL
    assert _why(world["wt"], *_bash(f"git -C {world['main']} show HEAD")) == HIDDEN_REFUSAL
    assert _why(world["wt"], *_bash(f"git -C {world['main']} show HEAD~1")) == ""


@pytest.mark.parametrize("command", [
    "git show HEAD", "git log -p -1", "git diff HEAD~1 HEAD", "git log -p main -- src",
    "git grep x main -- src", "git diff", "git worktree list", "git show main --stat",
])
def test_a_patch_or_tree_that_shows_no_hidden_path_stays_allowed(world, command):
    assert _why(world["wt"], *_bash(command)) == ""


@pytest.mark.parametrize("command", ["git show {blob}", "git diff main:eval side:src",
                                     "git log -p nosuch"])
def test_a_revision_that_is_no_commit_refuses_with_the_cause(world, command):
    blob = _git(world["main"], "rev-parse", "main:src/app/main.py")
    assert _why(world["wt"], *_bash(command.format(blob=blob))).startswith(
        "git cannot say whether a revision holds the hidden part")


def test_trees_that_cannot_be_listed_refuse_every_call(world, monkeypatch):
    real = reads._git

    def failing(root, *args):
        if args[:2] == ("worktree", "list"):
            return subprocess.CompletedProcess(args, 128, "", "fatal")
        return real(root, *args)

    monkeypatch.setattr(reads, "_git", failing)
    why = _why(world["wt"], "Read", {"file_path": str(world["wt"] / "src/app/main.py")})
    assert why.startswith("the repository's worktrees cannot be listed")


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads every folder")
def test_a_runs_root_or_a_hidden_folder_that_cannot_be_read_refuses(world):
    runs, hidden = world["runs"], world["main"] / "eval/hidden"
    runs.chmod(0)
    try:
        assert _why(world["wt"], "Read", {"file_path": str(world["wt"] / "docs/q.md")}) \
            .startswith("the runs root cannot be read")
    finally:
        runs.chmod(0o755)
    hidden.chmod(0)
    try:
        assert _why(world["wt"], "Grep", {"pattern": "x", "path": str(world["main"])}) \
            .startswith("a hidden part's folder cannot be walked")
    finally:
        hidden.chmod(0o755)


def test_a_session_in_a_run_clone_sees_the_repository_s_trees_through_its_marker(world):
    own = world["runs"] / "W2-70"
    clone = own / "clone"
    _git(world["main"], "clone", "-q", "-b", "side", str(world["main"]), str(clone))
    common = os.path.realpath(world["main"] / ".git")
    (own / ".gov-os-repository").write_text(common + "\n", encoding="utf-8")
    hidden = str(world["main"] / "eval/hidden/a.yaml")
    assert _why(clone, "Read", {"file_path": hidden}) == HIDDEN_REFUSAL
    assert _why(clone, "Read", {"file_path": str(clone / "docs/q.md")}) == ""
    (own / ".gov-os-repository").unlink()
    assert _why(clone, "Read", {"file_path": str(clone / "docs/q.md")}).startswith(
        "the repository's trees cannot be found from this run clone")


def test_an_unmeasured_session_runs_no_new_git_call(world, monkeypatch):
    calls: list = []
    real = reads._git
    monkeypatch.setattr(reads, "_git", lambda root, *a: calls.append(a) or real(root, *a))
    assert _why(world["wt"], *_bash("git show main"), role="orchestrator") == ""
    assert _why(world["wt"], "Read", {"file_path": str(world["main"] / "eval/hidden/a.yaml")},
                role="orchestrator") == ""
    assert calls == []


def test_the_trees_are_listed_once_for_a_session_and_its_subagent(world, monkeypatch):
    calls: list = []
    real = reads._git
    monkeypatch.setattr(reads, "_git", lambda root, *a: calls.append(a) or real(root, *a))
    _why(world["wt"], "Read", {"file_path": str(world["wt"] / "docs/q.md")}, agent="engineer")
    assert [a for a in calls if a[:1] == ("worktree",)] == [("worktree", "list", "--porcelain",
                                                             "-z")]
