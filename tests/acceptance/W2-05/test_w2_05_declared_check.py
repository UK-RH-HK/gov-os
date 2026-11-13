"""KPI failure 1 and KPI success 2, for a check the project itself declares: F-A with reading P-1 (DEC-804 items 1
and 3, DEC-807 item 2).

git exports ``GIT_INDEX_FILE`` to a pre-commit hook: relative (``.git/index``) on a plain commit in the main tree,
absolute (``.git/index.lock``) on ``git commit -a`` in the main tree, and absolute (under
``.git/worktrees/<name>/``) in a linked worktree. A check the project declares, run by the pre-commit hook through
``gov ci checks``, may run git anywhere: here it makes a git repository of its own in a new folder outside the
project, then ``git add`` and ``git commit`` there. If it inherits the index, its git calls write the project's
index: the commit lands with a deletion nobody staged, or the project's index names an object that does not exist.

P-1, accepted by the owner (DEC-804 item 3): an inherited ``GIT_INDEX_FILE`` is honoured only for git calls in the
project root; a program that may start git elsewhere gets no index. So, in each of the three shapes:

- the declared check receives no ``GIT_INDEX_FILE`` at all, and no other location variable (``GIT_DIR``,
  ``GIT_WORK_TREE``, ``GIT_COMMON_DIR``): the check records the environment it was started with;
- the commit lands with exactly what was staged: its parent is the old head, its tree is the staged tree (no
  deletion and no addition nobody staged), no other ref moved and no other commit became reachable;
- the project's index afterwards matches that commit and names no object the repository does not hold;
- the repository the check made is its own and holds what the check put there (one commit, one file).

The hooks are the project's own ``lefthook.yml`` (``gov ci checks G1 G2`` and ``gov ci staged-secrets``), installed
by lefthook in a temporary repository built from scratch. The declared check is a Python script of the temporary
project, started by the interpreter's absolute path; it imports nothing of ``gov`` (since W2-59, DEC-822 item 3, a
declared check runs on the judge's own package, not the project's: this case does not depend on either). The G2
check is ``true``. What stays as it is (git's own index scanned by the staged-secrets gate, an index that is not
git's own refused naming it, a planted ``GIT_DIR`` or ``GIT_INDEX_FILE`` reaching no child git call) is held by
the cases of ``test_w2_05_planted.py``.
"""

from __future__ import annotations

import json
import shlex
import shutil
import sys
from pathlib import Path

import pytest

import w2_05_support as support
from w2_05_support import skip_without

MESSAGE = "the hooked change"
CHECK_ID = "w2-05-own-repository"
SCRIPT_REL = "tools/w2_05_own_repository_check.py"
OWN_FILE, OWN_TEXT, OWN_MESSAGE = "own.txt", "the check's own file\n", "the check's own commit"
LOCATION_VARIABLES = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")

_CHECK = '''"""A check the project declares (W2-05, F-A): it records the environment it was started with, then makes a git
repository of its own in a new folder outside the project and commits one file there."""
import json
import os
import subprocess
import sys
import tempfile

MARKS, BASE, GIT = {marks!r}, {base!r}, {git!r}

with open(os.path.join(MARKS, "check-env.json"), "w", encoding="utf-8") as out:
    json.dump(dict(os.environ), out)
own = tempfile.mkdtemp(prefix="own-", dir=BASE)
steps = []


def run(*args):
    done = subprocess.run([GIT, *args], cwd=own, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    steps.append({{"args": list(args), "exit": done.returncode, "stdout": done.stdout[-800:],
                  "stderr": done.stderr[-800:]}})
    return done.returncode == 0


with open(os.path.join(own, {own_file!r}), "w", encoding="utf-8") as out:
    out.write({own_text!r})
ok = (run("init", "-q", "-b", "own") and run("add", "-A")
      and run("-c", "user.name=The check", "-c", "user.email=check@example.invalid", "commit", "-q", "-m",
              {own_message!r}))
with open(os.path.join(MARKS, "check-steps.json"), "w", encoding="utf-8") as out:
    json.dump({{"own": own, "ok": ok, "steps": steps}}, out)
sys.exit(0 if ok else 1)
'''

SHAPES = {
    "the main tree, a plain commit": (False, ()),
    "the main tree, git commit -a": (False, ("-a",)),
    "a linked worktree, a plain commit": (True, ()),
}


def _project(tmp_path, box):
    """The project: the template's gitleaks rules, the project's ``lefthook.yml``, a G1 check of its own that runs
    git in a repository of its own (``_CHECK``) and a G2 check that passes; committed on ``main``."""
    assert support.LEFTHOOK_YML.is_file(), "lefthook.yml is absent from the repository root"
    base = tmp_path / "the-check-s-own"
    base.mkdir()
    root = support.gov_project(tmp_path / "repo", hooks_file=support.LEFTHOOK_YML, retrieval=False)
    support.write(root, SCRIPT_REL, _CHECK.format(marks=str(box.marks), base=str(base), git=support.GIT,
                                                  own_file=OWN_FILE, own_text=OWN_TEXT, own_message=OWN_MESSAGE))
    support.declare_check(root, CHECK_ID, "graph integrity", "G1", f"{shlex.quote(sys.executable)} {SCRIPT_REL}")
    support.git(root, "add", "-A")
    support.git(root, "commit", "-q", "-m", "a check of the project's own")
    return root


def _install(box, main):
    installed = box.run(["lefthook", "install"], cwd=main, env=box.env())
    assert installed.returncode == 0, f"lefthook install refused the project's lefthook.yml:\n{support.said(installed)}"
    assert (support.common_dir_of(main) / "hooks" / "pre-commit").is_file(), "lefthook installed no pre-commit hook"


def _what_commit_a_stages(tree, scratch):
    """The tree ``git commit -a`` records: the index with every tracked change added (``git add -u``), worked out on
    a copy of the index; the index itself is not touched."""
    copy = scratch / "index-for-commit-a"
    shutil.copyfile(support.git_dir_of(tree) / "index", copy)
    env = dict(support.clean_env(), GIT_INDEX_FILE=str(copy))
    support.git(tree, "add", "-u", env=env)
    return support.git(tree, "write-tree", env=env).strip()


def _stage(tree, commit_a, scratch):
    support.write(tree, "notes.md", "the first line\nthe hooked change\n")
    if commit_a:
        return _what_commit_a_stages(tree, scratch)
    support.git(tree, "add", "notes.md")
    return support.staged_tree(tree)


def _record(box, name):
    path = box.marks / name
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def _steps_said(steps):
    if steps is None:
        return "(the check left no record of its git calls)"
    return "\n".join(f"  git {' '.join(step['args'])}: exit {step['exit']} {step['stderr'].strip()[-300:]}"
                     for step in steps["steps"]) or "  (no git call)"


@pytest.mark.parametrize("shape", tuple(SHAPES))
def test_a_declared_check_that_runs_git_in_a_repository_of_its_own_gets_no_index_and_the_commit_lands_as_staged(
        tmp_path, box, shape):
    skip_without("lefthook", "gitleaks")
    linked, extra = SHAPES[shape]
    main = _project(tmp_path, box)
    tree = support.add_worktree(main, tmp_path / "wt") if linked else main
    trees = [main, tree] if linked else [main]
    _install(box, main)
    staged = _stage(tree, bool(extra), tmp_path)
    before = support.repo_state(main, trees)

    done = box.run([support.GIT, "commit", "-q", "-m", MESSAGE, *extra], cwd=tree, env=box.env(),
                   timeout=support.HOOKED_COMMIT_TIMEOUT_S)

    what = f"a hooked commit ({shape}) whose declared check runs git in a repository of its own"
    environment, steps = _record(box, "check-env.json"), _record(box, "check-steps.json")
    assert environment is not None, f"{what}: the declared check did not run:\n{support.said(done)}"
    assert "GIT_INDEX_FILE" not in environment, (
        f"{what}: the declared check received GIT_INDEX_FILE={environment['GIT_INDEX_FILE']!r} (P-1, DEC-804 item 3: "
        f"an inherited index is honoured only for git calls in the project root; a program that may start git "
        f"elsewhere gets no index). Its own git calls:\n{_steps_said(steps)}")
    located = {name: environment[name] for name in LOCATION_VARIABLES if name in environment}
    assert not located, f"{what}: the declared check received {located} (KPI failure 1)"

    after = support.repo_state(main, trees)
    branch = "refs/heads/" + support.git(tree, "symbolic-ref", "--short", "HEAD").strip()
    old, new = before.heads[str(tree)], after.heads[str(tree)]
    assert done.returncode == 0 and new != old, (
        f"{what}: the commit did not land:\n{support.said(done)}\nthe check's git calls:\n{_steps_said(steps)}")
    assert support.git(tree, "rev-parse", f"{new}^").strip() == old, f"{what}: the new head's parent is not the old head"
    assert support.git(tree, "log", "-1", "--format=%s", new).strip() == MESSAGE, (
        f"{what}: the branch points at a commit that is not the one made: "
        + support.git(tree, "log", "-3", "--format=%h %s", new))
    assert support.git(tree, "rev-parse", f"{new}^{{tree}}").strip() == staged, (
        f"{what}: the commit's tree is not the staged tree (a deletion or an addition nobody staged); from the staged "
        f"tree to the commit's:\n" + support.git(tree, "diff", "--name-status", staged, new))
    assert after.refs == dict(before.refs, **{branch: new}), (
        f"{what}: refs other than {branch} moved: "
        f"{ {k: v for k, v in after.refs.items() if dict(before.refs, **{branch: new}).get(k) != v} }")
    assert after.reachable - before.reachable == {new}, f"{what}: commits other than the one made became reachable"
    assert support.git(tree, "diff-index", "--cached", "--name-status", "HEAD").strip() == "", (
        f"{what}: the project's index does not match the commit:\n"
        + support.git(tree, "diff-index", "--cached", "--name-status", "HEAD"))
    missing = support.missing_from_the_index(tree)
    assert not missing, f"{what}: the project's index names objects the repository does not hold: {missing[:5]}"
    for other in trees:
        if other != tree:
            assert after.indexes[str(other)] == before.indexes[str(other)], f"{what}: the index of {other} changed"

    assert steps is not None and steps["ok"], (
        f"{what}: the declared check's own git calls failed:\n{_steps_said(steps)}")
    own = steps["own"]
    assert support.git(own, "rev-parse", "--absolute-git-dir").strip() == str(Path(own).resolve() / ".git"), (
        f"{what}: the check's repository {own} has no git directory of its own")
    assert support.git(own, "log", "--format=%s").splitlines() == [OWN_MESSAGE], (
        f"{what}: the check's own repository does not hold its one commit: "
        + support.git(own, "log", "--format=%h %s"))
    assert support.git(own, "ls-tree", "-r", "--name-only", "HEAD").splitlines() == [OWN_FILE], (
        f"{what}: the check's own commit does not hold its one file: "
        + support.git(own, "ls-tree", "-r", "--name-only", "HEAD"))
    assert support.git(own, "show", f"HEAD:{OWN_FILE}") == OWN_TEXT, f"{what}: the check's own file is not as written"
