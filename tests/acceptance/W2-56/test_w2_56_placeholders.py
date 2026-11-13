"""S4 and F3 (first half): no placeholder file the sandbox makes can reach a commit.

S4: no placeholder file that the sandbox makes (.bashrc, .gitconfig, .mcp.json and the others, in the worktree or at a
denied name) can reach a commit: a test plants each name the sandbox makes and shows it neither staged nor committed
by an ordinary git add and git commit [DEC-799 item 1, DEC-402, row W2-I012]. F3: a placeholder file in a commit.

The placeholders are planted as the empty files a sandboxed session leaves at those names (``w2_56_support.
PLACEHOLDERS``): the CLI sandbox's fixed names at the worktree's root, and the names the launcher's own deny rules
write literally that need not exist. Two ordinary commits are made while they are there:

- **inside the session**, by the worker: the stand-in CLI, started by ``gov launch`` in the worktree with the
  environment the launcher gives it, plants them and runs ``git add`` (``-A`` or ``.``) and ``git commit``;
- **beside the session**, by its caller in the same worktree (a lead committing while the worker runs), with the
  caller's own environment.

Each commit also carries an ordinary new file (and one whose name only resembles a placeholder's), so the commit is
not empty and a fix that ignores too much fails too.
"""

from __future__ import annotations

import pytest

import w2_56_support as s

WORK = ("src/app/work.py", "docs/gitconfig-notes.md")


@pytest.fixture
def box(tmp_path):
    box = s.make_box(tmp_path)
    s.make_project(box)
    s.install_stand_in_cli(box)
    return box


def _placeholders_in(names) -> list[str]:
    names = [n.strip() for n in names if n.strip()]
    return sorted({p for p in s.PLACEHOLDERS for n in names if n == p or n.startswith(p + "/")})


@pytest.mark.parametrize("add", (["add", "-A"], ["add", "."]), ids=("git-add-A", "git-add-dot"))
def test_s4_no_placeholder_is_staged_or_committed_inside_the_session(box, add):
    s.set_plan(box, [
        {"do": "plant", "names": list(s.PLACEHOLDERS)},
        *[{"do": "write", "path": rel, "text": "work\n"} for rel in WORK],
        {"do": "git", "argv": add, "label": "add"},
        {"do": "git", "argv": ["diff", "--cached", "--name-only"], "label": "staged"},
        {"do": "git", "argv": ["commit", "-q", "-m", "the worker's commit"], "label": "commit"},
        {"do": "git", "argv": ["ls-tree", "-r", "--name-only", "HEAD"], "label": "tree"},
        {"do": "exit", "code": 0},
    ])
    launch = s.run_launch(box, s.ENGINEER, s.T.tk)
    assert launch.returncode == 0 and launch.started, f"the session did not run\n{launch.describe()}"
    name = launch.call["name"]
    added = s.result(box, name, "add")
    assert added["code"] == 0, f"an ordinary git {' '.join(add)} failed in the session: {added['stderr']}"
    staged = s.result(box, name, "staged")["stdout"].splitlines()
    assert not _placeholders_in(staged), f"placeholders staged by git {' '.join(add)}: {_placeholders_in(staged)}"
    assert set(WORK) <= set(staged), f"the ordinary files were not staged: {staged}"
    committed = s.result(box, name, "commit")
    assert committed["code"] == 0, f"the worker's commit failed: {committed['stderr']}"
    tree = s.result(box, name, "tree")["stdout"].splitlines()
    assert not _placeholders_in(tree), f"placeholders in the worker's commit: {_placeholders_in(tree)}"
    assert set(WORK) <= set(tree), f"the ordinary files are not in the worker's commit"


def test_s4_no_placeholder_is_committed_beside_a_running_session(box):
    planted, release = box.elsewhere / "planted", box.elsewhere / "release"
    s.set_plan(box, [
        {"do": "plant", "names": list(s.PLACEHOLDERS)},
        {"do": "touch", "path": str(planted)},
        {"do": "wait_for", "paths": [str(release)], "timeout": 45, "fail_code": 7},
        {"do": "exit", "code": 0},
    ])
    process = s.start_launch(box, s.ENGINEER, s.T.tk)
    try:
        assert s.wait_for(planted.exists, 30), "the session did not plant the placeholders"
        env = s.base_environment(box)
        for rel in WORK:
            s.write(box.project / rel, "the lead's work\n")
        added = s.git(box.project, "add", "-A", check=False, env=env)
        assert added.returncode == 0, f"an ordinary git add -A beside the session failed: {added.stderr}"
        staged = s.git(box.project, "diff", "--cached", "--name-only", env=env).stdout.splitlines()
        assert not _placeholders_in(staged), f"placeholders staged beside the session: {_placeholders_in(staged)}"
        s.git(box.project, "commit", "-q", "-m", "the lead's commit", env=env)
        tree = s.git(box.project, "ls-tree", "-r", "--name-only", "HEAD", env=env).stdout.splitlines()
        assert not _placeholders_in(tree), f"placeholders in the lead's commit: {_placeholders_in(tree)}"
        assert set(WORK) <= set(tree), "the ordinary files are not in the lead's commit"
    finally:
        release.touch()
        code, _, err = s.finish(process)
    assert code == 0, f"the session ended with {code}: {err[-1000:]}"
