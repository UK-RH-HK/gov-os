"""W2-60a, round 3 (review 2, DEC-951 item 4) -- a worktree's local settings; an adopted tree's role file.

(i) The CLI loads a linked worktree session's local settings from the **main
checkout's** ``.claude/settings.local.json``. A launch from a linked worktree
refuses on that file what it refuses on the tree's own copy (DEC-826 Q1,
DEC-838; a file that cannot be read), with the words the cases for
the tree's own file assert, and starts no session and leaves no record. A
worktree launch with no such file launches
(``test_w2_60a_launch_record.py::test_every_worktree_shares_the_main_checkout_s_record_folder``,
and the control launch in each case here).

(ii) A tree with no ``template/`` folder (an adopted repository) keeps its
kernel at ``governance/kernel/``: the role file is read from
``governance/kernel/roles/<role>.md``, and the record's ``role_text`` names it.
"""

from __future__ import annotations

import shutil

import pytest

import w2_60a_support as s

THRESHOLD_MESSAGE = "no launch sets a compaction threshold (DEC-838)"
VARIABLE = "CLAUDE_CODE_AUTO_COMPACT_WINDOW"
ADOPTED_ROLES_REL = "governance/kernel/roles"


KEYS = {
    # (change to the main checkout's local settings, words the tree's own file's case asserts)
    "auto-compact-window": (lambda data: data.update({"autoCompactWindow": 300000}), ("autoCompactWindow",)),
    "env-auto-compact-window": (lambda data: data.setdefault("env", {}).update({VARIABLE: "300000"}), (VARIABLE,)),
    "model-settings-auto-compact-window": (
        lambda data: data.setdefault("modelSettings", {}).setdefault(s.OPUS, {}).update({"autoCompactWindow": 300000}),
        (THRESHOLD_MESSAGE, "autoCompactWindow")),
    "agent": (lambda data: data.update({"agent": s.ENGINEER}), ("agent",)),
    # Emergency 2 (release 0.1.2): a sandbox key, the no-prompt mode, added directories and disableAllHooks are the
    # repository's own choice, no longer refused; their cases are retired.
}


@pytest.fixture()
def worktree(sandbox, project, cli):
    """A linked worktree of the committed fixture project, with no local settings file of its own; one control
    launch from it."""
    tree = sandbox.home / "work" / "worktree"
    s.git(project, "worktree", "add", "-q", "-b", "w2/W2-60a-fixture", str(tree))
    assert not (tree / s.LOCAL_SETTINGS_REL).exists()
    s.assert_launched(s.launch(sandbox, cli, s.ENGINEER, s.T, cwd=tree))
    return tree


@pytest.mark.parametrize("key", sorted(KEYS))
def test_the_main_checkout_s_local_settings_are_checked_for_a_worktree_launch(sandbox, project, cli, worktree, key):
    change, words = KEYS[key]
    s.rewrite_settings(project, change, s.LOCAL_SETTINGS_REL)
    s.assert_refused(s.launch(sandbox, cli, s.ENGINEER, s.T, cwd=worktree), "LAUNCH_REFUSED", *words)


def test_main_checkout_local_settings_that_are_not_json_refuse_a_worktree_launch(sandbox, project, cli, worktree):
    s.write(project / s.LOCAL_SETTINGS_REL, "{ not json\n")
    s.assert_refused(s.launch(sandbox, cli, s.ENGINEER, s.T, cwd=worktree), "LAUNCH_REFUSED", "settings.local.json")


def test_an_adopted_tree_s_role_file_is_read_from_its_kernel(sandbox, cli):
    project = s.make_project(sandbox, roles=(), kernel_skills=False, commit=False)
    shutil.move(project / "template/governance/kernel/launch", project / "governance/kernel/launch")
    shutil.rmtree(project / "template")
    role_file = s.write(project / ADOPTED_ROLES_REL / f"{s.ENGINEER}.md", s.role_text(s.ENGINEER))
    s.git(project, "init", "-q", "-b", "main")
    s.git(project, "add", "-A")
    s.git(project, "commit", "-q", "-m", "W2-60a adopted fixture project")
    result = s.launch(sandbox, cli, s.ENGINEER, s.T)
    s.assert_launched(result)
    expected = {"path": f"{ADOPTED_ROLES_REL}/{s.ENGINEER}.md", "version": s.VERSIONS[s.ENGINEER],
                "sha256": s.sha256_file(role_file)}
    assert result.record().get("role_text") == expected, (
        f"the record's role_text is not the adopted role file's\nrecord: {result.record().get('role_text')}\n"
        f"expected: {expected}")
