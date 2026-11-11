"""KPI success 3, as the owner re-baselined it (DEC-783, option (b) of P-W2-33): "`lefthook install` leaves
.claude/settings.json byte-identical to the committed file, and adapter-portability stays green; `uninstall` is an
owner act, followed by restoring the committed file (DEC-712)" [AR-2].

lefthook 2.1.15 rewrites a Claude Code settings file on every ``uninstall`` (its keys re-sorted), whatever the
project's files hold. What ``uninstall`` alone does to the file is lefthook's own behaviour and is not asserted
here. The cases assert the state once the owner's act is complete: ``lefthook uninstall``, then the committed file
restored with ``git restore`` in each tree whose file changed, as DEC-712 records the operator doing it. Every
``install`` keeps its byte-identical expectation.

Every case runs lefthook in a temporary repository built from scratch, with its working folder there and an
environment built from nothing (no ``GIT_*`` variable of the caller): lefthook can never act on this
repository, whose hooks stay uninstalled until W2-08. The hooks file is this repository's own (``lefthook.yml``,
and the template's hooks file ``template/lefthook.yml.jinja``, DEC-783), copied into the temporary repository as
one named file.

The settings file is a stand-in in the shape of a Claude Code settings file with hooks (``stand_in_settings``),
or, for the adapter-portability half, the one ``rulesync generate`` writes from the kernel template's sources
(W1-38's public support). This repository's own ``.claude/settings.json`` is never read.
"""

from __future__ import annotations

import pytest

import w2_05_support as support
from w2_05_support import skip_without

SETTINGS = ".claude/settings.json"
OWNER_ACT = "the owner's act (`lefthook uninstall`, then the committed file restored with `git restore`, DEC-712)"


def _hooks_file(which):
    # The template's hooks file is ``template/lefthook.yml.jinja`` (DEC-783, reading P-3 accepted).
    path = support.LEFTHOOK_YML if which == "project" else support.TEMPLATE_HOOKS
    assert path.is_file(), f"the {which} hooks file is absent ({path.relative_to(support.REPO_ROOT)})"
    return path


def _repo(root, hooks_file, settings=None):
    files = {"README.md": "# A project\n", "lefthook.yml": hooks_file.read_text(encoding="utf-8"),
             SETTINGS: settings if settings is not None else support.stand_in_settings()}
    return support.new_repo(root, files)


def _lefthook(box, where, verb):
    done = box.run(["lefthook", verb], cwd=where, env=box.env())
    assert done.returncode == 0, f"lefthook {verb} failed in {where}:\n{support.said(done)}"
    return done


def _install(box, where):
    """``lefthook install`` from ``where``; it must have installed the hooks file's pre-commit hook, so that a
    settings file left as it was is not the mark of an install that did nothing."""
    _lefthook(box, where, "install")
    hook = support.common_dir_of(where) / "hooks" / "pre-commit"
    assert hook.is_file(), f"`lefthook install` in {where} installed no pre-commit hook ({hook} is absent)"


def _owner_uninstall(box, where, trees, committed):
    """The owner's act: ``lefthook uninstall`` from ``where``, then the committed settings file restored with
    ``git restore`` in each of ``trees`` whose file changed (DEC-712)."""
    _lefthook(box, where, "uninstall")
    for tree in trees:
        if (tree / SETTINGS).read_bytes() != committed:
            support.git(tree, "restore", "--", SETTINGS)


def _committed(repo):
    return support.git(repo, "show", f"HEAD:{SETTINGS}").encode("utf-8")


def assert_byte_identical(tree, committed, after):
    now = (tree / SETTINGS).read_bytes()
    assert now == committed, (
        f"{SETTINGS} in {tree.name} is not byte-identical to the committed file after {after}:\n"
        + support.git(tree, "diff", "--", SETTINGS)[:3000])


def assert_no_change(tree, after):
    status = support.git(tree, "status", "--porcelain", "--untracked-files=all")
    assert status == "", f"the tree {tree.name} shows a change after {after}:\n{status[:3000]}"


@pytest.mark.parametrize("which", ("project", "template"), ids=("lefthook.yml", "the template's hooks file"))
def test_install_leaves_the_settings_byte_identical_before_and_after_the_owner_s_uninstall_and_restore(
        tmp_path, box, which):
    skip_without("lefthook")
    repo = _repo(tmp_path / "repo", _hooks_file(which))
    committed = _committed(repo)
    _install(box, repo)
    assert_byte_identical(repo, committed, "`lefthook install`")
    _install(box, repo)
    assert_byte_identical(repo, committed, "a second `lefthook install`")
    _owner_uninstall(box, repo, [repo], committed)
    assert_byte_identical(repo, committed, OWNER_ACT)
    assert_no_change(repo, OWNER_ACT)
    _install(box, repo)
    assert_byte_identical(repo, committed, f"`lefthook install` after {OWNER_ACT}")


def test_install_from_a_linked_worktree_leaves_both_settings_byte_identical_and_the_owner_s_act_both_clean(
        tmp_path, box):
    skip_without("lefthook")
    repo = _repo(tmp_path / "repo", _hooks_file("project"))
    tree = support.add_worktree(repo, tmp_path / "wt")
    committed = _committed(repo)
    _install(box, tree)
    assert_byte_identical(tree, committed, "`lefthook install` from the linked worktree")
    assert_byte_identical(repo, committed, "`lefthook install` from the linked worktree")
    _owner_uninstall(box, tree, [tree, repo], committed)
    for each in (tree, repo):
        assert_byte_identical(each, committed, f"{OWNER_ACT}, from the linked worktree")
        assert_no_change(each, f"{OWNER_ACT}, from the linked worktree")


def test_adapter_portability_stays_green_through_install_and_the_owner_s_uninstall_and_restore(tmp_path, box):
    """W1-38's adopted project, generated by the real rulesync and committed, with the project's hooks file."""
    skip_without("lefthook", "rulesync")
    import w1_38_support as w138
    if w138.rulesync_version() is None:
        pytest.skip(f"rulesync is not installed at {w138.RULESYNC_BIN}")
    project = tmp_path / "project"
    project.mkdir()
    w138.init_git(project)
    w138.build_project_from_template(project)
    generated = w138.run_rulesync_generate(project)
    assert generated.returncode == 0, f"rulesync generate failed: {generated.stderr}"
    support.write(project, "lefthook.yml", _hooks_file("project").read_text(encoding="utf-8"))
    w138.commit_all(project, "generated, with the hooks file")
    assert (project / SETTINGS).is_file(), f"rulesync generate wrote no {SETTINGS}; the case needs one"
    committed = _committed(project)
    first = w138.run_portability_check(project)
    assert first.returncode == 0, (f"adapter-portability is not green before lefthook runs; the case needs a green "
                                   f"start:\n{w138.output_of(first)[-3000:]}")
    _install(box, project)
    assert_byte_identical(project, committed, "`lefthook install`")
    checked = w138.run_portability_check(project)
    assert checked.returncode == 0, (f"adapter-portability went red after `lefthook install`:\n"
                                     f"{w138.output_of(checked)[-3000:]}")
    _owner_uninstall(box, project, [project], committed)
    assert_byte_identical(project, committed, OWNER_ACT)
    assert_no_change(project, OWNER_ACT)
    checked = w138.run_portability_check(project)
    assert checked.returncode == 0, (f"adapter-portability is red after {OWNER_ACT}:\n"
                                     f"{w138.output_of(checked)[-3000:]}")
