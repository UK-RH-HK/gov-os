"""KPI success 2: "A hooked commit in a linked worktree leaves its branch, index and reflog as the commit made
them (the DEC-710 case)" [AR-2].

The DEC-710 case, rebuilt from scratch: a repository with a linked worktree, and a pre-commit hook that runs
the retrieval-regression check as its declaration names it (``python3 -m gov.retrieval.retrieve_check``, by
``sh -c`` in the working tree's root, DEC-285) against a stand-in dev tier (W1-21's fixture, named by
``GOV_DEV_TIERS``; the embeddings come from W1-21's stand-in endpoint). git gives the hook ``GIT_DIR`` (the
worktree's own git directory) and an absolute ``GIT_INDEX_FILE``; the check clones the tier into a temporary
folder and commits there. On the code before this ticket that commit lands on the worktree's branch.

"As the commit made them" is read in full (README): after the hooked commit, the branch points at one new
commit whose parent is the old head and whose tree is what the index held; the branch's reflog and the
worktree's HEAD reflog have that one entry more; the index equals the new head; nothing else of the
repository moved (other refs, their reflogs, the main tree's index), and the only new commit reachable from a
ref or a reflog is that one. A refusing hook leaves the branch, its reflog and the staged change as they were.

The hook here is a plain script that runs the check's command, so that the case stands without lefthook; the
case through lefthook and the project's own ``lefthook.yml`` (``gov ci checks G1 G2``) is the last one.
"""

from __future__ import annotations

import pytest

import w2_05_support as support
from w2_05_support import skip_without

MESSAGE = "the hooked change"


def _setup(tmp_path, linked=True, hooks_file=None):
    main = support.gov_project(tmp_path / "repo", hooks_file=hooks_file)
    tree = support.add_worktree(main, tmp_path / "wt") if linked else main
    trees = [main, tree] if linked else [main]
    return main, tree, trees


def _stage_a_change(tree):
    support.write(tree, "notes.md", "the first line\nthe hooked change\n")
    support.git(tree, "add", "notes.md")
    return support.staged_tree(tree)


def _commit(box, tree, env, *extra):
    return box.run([support.GIT, "commit", "-q", "-m", MESSAGE, *extra], cwd=tree, env=env,
                   timeout=support.HOOKED_COMMIT_TIMEOUT_S)


def assert_not_nested(box):
    nested = support.nested_runs(box.marks)
    assert not nested, (
        f"the check's own git calls reached this repository and ran its pre-commit hook again, {len(nested)} "
        f"time(s) (the GIT_* variables the hook inherited reached a child git call): {nested[:3]}")


def _branch_of(tree):
    return "refs/heads/" + support.git(tree, "symbolic-ref", "--short", "HEAD").strip()


def assert_as_the_commit_made_them(main, tree, trees, before, staged, done):
    """Every half of KPI success 2 for a commit that went through."""
    what = f"a hooked commit in {'a linked worktree' if tree != main else 'the main tree'}"
    after = support.repo_state(main, trees)
    branch = _branch_of(tree)
    old, new = before.heads[str(tree)], after.heads[str(tree)]
    assert done.returncode == 0, f"{what} was refused:\n{support.said(done)}"
    assert new != old, f"{what}: the branch did not move"
    assert support.git(tree, "rev-parse", f"{new}^").strip() == old, (
        f"{what}: the new head's parent is not the old head; the history of {branch}:\n"
        + support.git(tree, "log", "--format=%h %p %s", "-5", new))
    assert support.git(tree, "rev-parse", f"{new}^{{tree}}").strip() == staged, (
        f"{what}: the new head does not hold the tree the index held; it holds:\n"
        + support.git(tree, "diff", "--stat", staged, new))
    assert support.git(tree, "log", "-1", "--format=%s", new).strip() == MESSAGE, (
        f"{what}: the branch points at a commit that is not the one made: "
        + support.git(tree, "log", "-3", "--format=%h %s", new))
    expected_refs = dict(before.refs, **{branch: new})
    assert after.refs == expected_refs, (
        f"{what}: refs other than {branch} moved: "
        f"{ {k: (before.refs.get(k), v) for k, v in after.refs.items() if expected_refs.get(k) != v} }")
    assert after.reflogs[branch] == [new] + before.reflogs[branch], (
        f"{what}: the reflog of {branch} is not the old one plus the commit made: "
        f"{support.git(tree, 'reflog', 'show', '--format=%h %gs', branch)}")
    head_log = f"HEAD of {tree.name}"
    assert after.reflogs[head_log] == [new] + before.reflogs[head_log], (
        f"{what}: the HEAD reflog of the worktree is not the old one plus the commit made: "
        f"{support.git(tree, 'reflog', 'show', '--format=%h %gs', 'HEAD')}")
    others = {k: v for k, v in after.reflogs.items() if k not in (branch, head_log)}
    assert others == {k: before.reflogs[k] for k in others}, f"{what}: another reflog changed: {others}"
    assert support.git(tree, "diff-index", "--cached", "--name-status", "HEAD").strip() == "", (
        f"{what}: the index does not equal the new head:\n"
        + support.git(tree, "diff-index", "--cached", "--name-status", "HEAD"))
    assert support.git(tree, "status", "--porcelain").strip() == "", (
        f"{what}: the working tree is not clean after the commit:\n" + support.git(tree, "status", "--porcelain"))
    for other in trees:
        if other != tree:
            assert after.indexes[str(other)] == before.indexes[str(other)], f"{what}: the index of {other} changed"
    assert after.reachable - before.reachable == {new}, (
        f"{what}: commits other than the one made became reachable: "
        + ", ".join(support.git(main, "log", "-1", "--format=%h %s", c).strip()
                    for c in sorted(after.reachable - before.reachable - {new})))


@pytest.mark.parametrize("linked", (True, False), ids=("a linked worktree", "the main tree"))
def test_a_hooked_commit_that_runs_the_retrieval_check_leaves_the_branch_as_the_commit_made_it(
        tmp_path, box, retrieval_env, linked):
    main, tree, trees = _setup(tmp_path, linked)
    support.plain_hook(main, box.marks, support.retrieval_check_command())
    before = support.repo_state(main, trees)
    staged = _stage_a_change(tree)

    done = _commit(box, tree, retrieval_env)

    code, output = support.hook_result(box.marks)
    assert code is not None, f"the pre-commit hook did not run:\n{support.said(done)}"
    assert_not_nested(box)
    assert code == 0 and support.measured(output), (
        f"the retrieval-regression check did not measure green inside the hook (exit {code}); the case needs a "
        f"check that ran to the end:\n{output[-3000:]}")
    assert_as_the_commit_made_them(main, tree, trees, before, staged, done)


def test_a_refusing_hook_in_a_linked_worktree_leaves_the_branch_the_reflog_and_the_staged_change(
        tmp_path, box, retrieval_env):
    main, tree, trees = _setup(tmp_path)
    support.plain_hook(main, box.marks, support.retrieval_check_command(), refuse=True)
    before = support.repo_state(main, trees)
    _stage_a_change(tree)
    staged_index = support.git(tree, "ls-files", "--stage")

    done = _commit(box, tree, retrieval_env)

    code, output = support.hook_result(box.marks)
    assert code is not None, f"the pre-commit hook did not run:\n{support.said(done)}"
    assert_not_nested(box)
    assert done.returncode != 0, f"the hook refused, yet the commit went through:\n{support.said(done)}"
    after = support.repo_state(main, trees)
    assert after.refs == before.refs, (
        f"a refused commit moved refs: { {k: v for k, v in after.refs.items() if before.refs.get(k) != v} }")
    assert after.reflogs == before.reflogs, "a refused commit changed a reflog"
    assert after.reachable == before.reachable, (
        "a refused commit left new commits reachable: "
        + ", ".join(support.git(main, "log", "-1", "--format=%h %s", c).strip()
                    for c in sorted(after.reachable - before.reachable)))
    assert support.git(tree, "ls-files", "--stage") == staged_index, (
        "a refused commit changed the worktree's index:\n" + support.git(tree, "status", "--porcelain"))
    assert support.git(tree, "status", "--porcelain").strip() == "M  notes.md", (
        "the staged change is not left as it was staged:\n" + support.git(tree, "status", "--porcelain"))


def test_a_commit_in_a_linked_worktree_through_lefthook_and_the_project_hooks_file(tmp_path, box, retrieval_env):
    """The project's own ``lefthook.yml`` (pre-commit: ``gov ci checks G1 G2`` and ``gov ci staged-secrets``),
    installed in a temporary repository whose G1 check is the retrieval-regression declaration."""
    skip_without("lefthook", "gitleaks")
    assert support.LEFTHOOK_YML.is_file(), "lefthook.yml is absent from the repository root"
    main, tree, trees = _setup(tmp_path, hooks_file=support.LEFTHOOK_YML)
    installed = box.run(["lefthook", "install"], cwd=main, env=box.env())
    assert installed.returncode == 0, f"lefthook install refused the project's lefthook.yml:\n{support.said(installed)}"
    assert (support.common_dir_of(main) / "hooks" / "pre-commit").is_file(), "lefthook installed no pre-commit hook"
    before = support.repo_state(main, trees)
    staged = _stage_a_change(tree)

    done = _commit(box, tree, retrieval_env)

    assert_as_the_commit_made_them(main, tree, trees, before, staged, done)
