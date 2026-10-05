"""W1-50 — the repository's own git settings and replacement refs do not change what the check reads.

Added after implementation, from the review after the suite went green
(DEC-136, DEC-137). The behaviour, as it was passed to the test designer:

    Whoever makes a commit can also write the repository's local git
    configuration (`git config`, stored in `.git/config`) and replacement
    refs (`git replace`), in the same call or an earlier one. The check judges
    a move's commits as git reads the real objects with default settings,
    whatever the repository's local configuration and `refs/replace/` hold.

It is held by the KPIs and decisions the suite already tests. They speak of
the commit: its trailers and the paths it changes. Neither is a matter of how
the repository is set up to display them.

KPI success 5 [CAP-58.h]: "A commit carrying a Role: owner trailer that is made
during any agent session's call is a finding (DEC-360)".

KPI failure 2: "A commit that changes a path outside the allowed paths of its
own Role and Task trailers raises no finding, whoever the caller is".

KPI success 1 [CAP-58.h]: a forward HEAD move is judged commit by commit, "each
commit's paths against the allowed paths of its own Role and Task trailers".

DEC-319 (owner): "In a worker's call, a commit whose `Role` trailer differs
from the caller's role is a finding."

DEC-182: "Git reads trailers only from the last paragraph of a commit
message."

**The settings.** Each is written with ``git config --local`` in the
throw-away project, by the call's own command, after its commits:

- ``trailer.separators`` set to ``=``: git then reads ``Role=owner`` as a
  trailer and ``Role: owner`` as none;
- ``core.commentChar`` set to ``R``: git then takes a line that begins with
  ``R`` for a comment;
- ``trailer.role.key`` set to another word: git then shows a ``Role`` trailer
  under that word;
- ``log.showRoot`` set to ``false``: git's log then shows no change for a
  commit without a parent;
- ``diff.ignoreSubmodules`` set to ``all``: git's diff then shows no change of
  a submodule entry.

**The replacement refs.** ``git replace <object> <other object>`` makes git
read the other object wherever the first is named. The first object is still
the one the commit, the branch and every clone hold.

What each commit really is, is read by the tests from the object itself: the
last paragraph of the message as ``git cat-file`` prints it, and the tree as
``git --no-replace-objects ls-tree`` prints it.

No test writes a global or a system setting.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
NO_TRAILERS = support.NO_TRAILERS

ROLE_OWNER = f"Role: {support.OWNER}"
TASK = f"Task: {TICKET}"

# name: (key, value) in the repository's local git configuration
TRAILER_SETTINGS = {
    "trailer-separators": ("trailer.separators", "="),
    "core-commentchar": ("core.commentChar", "R"),
    "trailer-role-key": ("trailer.role.key", "Reviewed-by"),
}
SHOW_ROOT = ("log.showRoot", "false")
IGNORE_SUBMODULES = ("diff.ignoreSubmodules", "all")
DEFAULT = None


def _with(command, *settings):
    """Shell: ``command``, then each setting written into the repository's local configuration."""
    for setting in settings:
        if setting is not DEFAULT:
            command += " && " + support.set_locally(*setting)
    return command


def _assert_set(project, *settings):
    """Guard against an empty test: the local configuration holds each setting."""
    for setting in settings:
        if setting is not DEFAULT:
            key, value = setting
            assert support.local_setting(project, key) == value, (
                f"the fixture is wrong: {key} is {support.local_setting(project, key)!r} in the local configuration"
            )


def _assert_final_block(project, commit_id, *lines):
    """Guard against an empty test: the commit's last paragraph holds exactly ``lines``."""
    found = [line.decode("utf-8") for line in support.final_block(project, commit_id)]
    assert found == list(lines), f"the fixture is wrong: the commit's final block is {found!r}, not {list(lines)!r}"


# --------------------------------------------------------------------------
# Trailers: what the commit's final block holds, whatever the settings say about trailers and comments
# --------------------------------------------------------------------------

# name: (GOV_ROLE, a path that caller may write itself, the commit's trailer lines)
OWNER_CALLERS = {
    "orchestrator-session": (ORCHESTRATOR, support.README, (ROLE_OWNER,)),
    "engineer-session": (ENGINEER, support.SOURCE, (TASK, ROLE_OWNER)),
}


@pytest.mark.parametrize("setting", sorted(TRAILER_SETTINGS), ids=sorted(TRAILER_SETTINGS))
@pytest.mark.parametrize("caller", sorted(OWNER_CALLERS), ids=sorted(OWNER_CALLERS))
def test_a_role_owner_commit_is_a_finding_whatever_the_repository_s_settings_for_trailers(project, call, caller,
                                                                                         setting):
    """KPI success 5. The path is one the caller may write itself, so only the trailer makes the commit a finding.

    The same commits with default settings are
    ``test_a_role_owner_commit_made_in_an_agent_s_call_is_flagged``.
    """
    role, path, lines = OWNER_CALLERS[caller]
    command = _with(support.commit_with(path, *support.trailer_arguments(*lines)), TRAILER_SETTINGS[setting])
    result, left = call(project, command, role, TICKET)
    _assert_set(project, TRAILER_SETTINGS[setting])
    _assert_final_block(project, "HEAD", *lines)
    what = (f"a commit of {path} with the trailers {lines}, made in a call with GOV_ROLE={role!r} on {TICKET} "
            f"that also sets {' '.join(TRAILER_SETTINGS[setting])} in the local git configuration")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_another_role_s_trailer_in_a_worker_s_call_is_a_finding_whatever_the_comment_character(project, call):
    """DEC-319. An engineer's call commits its own source file with ``Role: orchestrator``.

    The same commit with default settings is
    ``test_in_a_worker_s_call_a_commit_with_another_role_s_trailer_is_a_finding[engineer-session-orchestrator-commit]``.
    """
    setting = TRAILER_SETTINGS["core-commentchar"]
    command = _with(support.commit(support.SOURCE, AS_ORCHESTRATOR), setting)
    result, left = call(project, command, ENGINEER, TICKET)
    _assert_set(project, setting)
    _assert_final_block(project, "HEAD", TASK, f"Role: {ORCHESTRATOR}")
    what = (f"a commit of {support.SOURCE} with trailers {AS_ORCHESTRATOR}, in a call of the engineer on {TICKET} "
            f"that also sets {' '.join(setting)}")
    check_support.assert_caught(result, support.SOURCE, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_commits_inside_their_own_paths_stay_silent_whatever_the_settings(project, call):
    """The other side (KPI success 1): the settings take nothing from a commit either.

    A test designer's commit of an acceptance test and an engineer's commit of
    its source file, in the orchestrator's own call, with all five settings
    written by the same call. Each commit is inside the paths of its own
    trailers.
    """
    settings = (*TRAILER_SETTINGS.values(), SHOW_ROOT, IGNORE_SUBMODULES)
    command = _with(support.commits((support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER)), *settings)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    _assert_set(project, *settings)
    _assert_final_block(project, "HEAD~1", TASK, f"Role: {support.DESIGNER}")
    _assert_final_block(project, "HEAD", TASK, f"Role: {ENGINEER}")
    what = f"`{command}` in a call of the orchestrator on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# Paths: what the commit's tree holds, whatever the settings say about showing changes
# --------------------------------------------------------------------------

ISLAND = "island"   # a branch whose only commit has no parent


def _island(project, sandbox, trailers):
    """A branch ``island`` with one root commit that adds ``NEW_TEST`` and nothing else. ``main`` is checked out."""
    directory = support.NEW_TEST.rsplit("/", 1)[0]
    command = (
        f"git checkout -q --orphan {ISLAND} && git rm -rfq . && mkdir -p {directory} "
        f"&& echo island > {support.NEW_TEST} && git add -- {support.NEW_TEST} && git commit -q -m 'a root commit'"
    )
    if trailers is not None:
        role, task = trailers
        command += f" --trailer 'Task: {task}' --trailer 'Role: {role}'"
    support.run(project, sandbox, command + " && git checkout -q main")
    parents = check_support.git(project, "rev-list", "--parents", "-n", "1", ISLAND).split()[1:]
    held = check_support.git(project, "ls-tree", "-r", "--name-only", ISLAND).split()
    assert parents == [] and held == [support.NEW_TEST], (
        f"the fixture is wrong: the commit on {ISLAND} has the parents {parents} and holds {held}"
    )


# name: (the local setting, the root commit's trailers)
ROOT_COMMITS = {
    "log-showroot-false-engineer-trailers": (SHOW_ROOT, AS_ENGINEER),
    # No trailers: the caller decides, and the orchestrator may not write an acceptance test.
    "log-showroot-false-no-trailers": (SHOW_ROOT, NO_TRAILERS),
    # Green when written: a commit without a parent adds every file it holds.
    "default-settings-engineer-trailers": (DEFAULT, AS_ENGINEER),
}


@pytest.mark.parametrize("case", sorted(ROOT_COMMITS), ids=sorted(ROOT_COMMITS))
def test_a_merged_root_commit_that_adds_an_acceptance_test_is_flagged(project, sandbox, call, case):
    """KPI failure 2. The orchestrator merges a history that has nothing in common with its own
    (``--allow-unrelated-histories``). Its one commit has no parent and adds an acceptance test."""
    setting, trailers = ROOT_COMMITS[case]
    _island(project, sandbox, trailers)
    command = _with(
        f"git merge -q --no-ff --no-commit --allow-unrelated-histories {ISLAND} && git commit -q -m 'Merge {ISLAND}'"
        f" --trailer '{TASK}' --trailer 'Role: {ORCHESTRATOR}'", setting)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    assert check_support.read(project, support.NEW_TEST), f"the merge did not bring in {support.NEW_TEST}"
    _assert_set(project, setting)
    what = (f"`{command}` by the orchestrator on {TICKET}, bringing a commit without a parent that adds "
            f"{support.NEW_TEST} with trailers {trailers}")
    check_support.assert_caught(result, support.NEW_TEST, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


SUBMODULE = f"{support.ACCEPTANCE}/{support.WBS}/vendored"   # a submodule entry (a gitlink) under tests/acceptance/**

# name: the local setting
SUBMODULE_ENTRIES = {
    "diff-ignoresubmodules-all": IGNORE_SUBMODULES,
    # Green when written: a submodule entry is a path like any other.
    "default-settings": DEFAULT,
}


@pytest.mark.parametrize("case", sorted(SUBMODULE_ENTRIES), ids=sorted(SUBMODULE_ENTRIES))
def test_a_commit_that_adds_a_submodule_entry_under_acceptance_tests_is_flagged(project, call, case):
    """KPI failure 2. An engineer's commit, in the orchestrator's own call, adds a repository inside
    ``tests/acceptance/**`` as a submodule entry: the tree holds a commit id at that path, with mode 160000."""
    setting = SUBMODULE_ENTRIES[case]
    command = _with(
        f"git init -q {SUBMODULE} && git -C {SUBMODULE} commit -q --allow-empty -m inner "
        f"&& git add -- {SUBMODULE} 2> /dev/null && git commit -q -m 'a submodule entry'"
        f" --trailer '{TASK}' --trailer 'Role: {ENGINEER}'", setting)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    _assert_set(project, setting)
    entry = support.real(project, "ls-tree", "HEAD", "--", SUBMODULE).split()
    before = support.real(project, "ls-tree", "HEAD~1", "--", SUBMODULE).split()
    assert entry[:2] == ["160000", "commit"] and before == [], (
        f"the fixture is wrong: HEAD holds {entry} at {SUBMODULE} and the commit before it {before}"
    )
    what = (f"a commit that adds the submodule entry {SUBMODULE} with trailers {AS_ENGINEER}, in the "
            f"orchestrator's own call on {TICKET}")
    check_support.assert_caught(result, SUBMODULE, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# Replacement refs
# --------------------------------------------------------------------------

# name: GOV_ROLE of the caller
REPLACING_CALLERS = {
    "orchestrator-session": ORCHESTRATOR,
    "engineer-session": ENGINEER,
}


@pytest.mark.parametrize("caller", sorted(REPLACING_CALLERS), ids=sorted(REPLACING_CALLERS))
def test_a_replacement_ref_does_not_hide_a_commit_s_change_of_an_acceptance_test(project, call, caller):
    """KPI failure 2. An engineer's commit changes an existing acceptance test. Then the same call maps the
    commit's ``tests/acceptance`` tree object to the tree the commit before it holds there.

    The same commit with no replacement ref is
    ``test_a_commit_outside_the_paths_of_its_own_trailers_is_flagged_whoever_the_caller_is``
    (``engineer-commit-of-an-acceptance-test``, callers ``orchestrator`` and ``engineer``).
    """
    role = REPLACING_CALLERS[caller]
    path = support.ACCEPTANCE_FILE
    command = (support.commit(path, AS_ENGINEER)
               + f" && git replace HEAD:{support.ACCEPTANCE} HEAD~1:{support.ACCEPTANCE}")
    result, left = call(project, command, role, TICKET)
    new_tree = support.real(project, "rev-parse", f"HEAD:{support.ACCEPTANCE}").strip()
    assert support.replacement_refs(project) == [new_tree], (
        f"the fixture is wrong: refs/replace/ holds {support.replacement_refs(project)}, not {new_tree}"
    )
    assert (support.real(project, "rev-parse", f"HEAD:{path}")
            != support.real(project, "rev-parse", f"HEAD~1:{path}")), (
        f"the fixture is wrong: the commit does not change {path}"
    )
    _assert_final_block(project, "HEAD", TASK, f"Role: {ENGINEER}")
    what = (f"a commit of {path} with trailers {AS_ENGINEER}, in a call with GOV_ROLE={role!r} on {TICKET} that "
            f"also replaces the commit's {support.ACCEPTANCE} tree with the one before it")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_replacement_ref_does_not_hide_a_role_owner_trailer(project, call):
    """KPI success 5. The orchestrator's own call makes a ``Role: owner`` commit of README.md. Then it maps the
    commit to a twin with the same tree and parent and a message without trailers."""
    path = support.README
    twin = support.commit_tree("HEAD^{tree}", ["HEAD~1"], NO_TRAILERS, subject="work")
    command = (support.commit_with(path, *support.trailer_arguments(ROLE_OWNER))
               + f" && git replace HEAD {twin}")
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    head = check_support.git(project, "rev-parse", "HEAD").strip()
    assert support.replacement_refs(project) == [head], (
        f"the fixture is wrong: refs/replace/ holds {support.replacement_refs(project)}, not HEAD {head}"
    )
    _assert_final_block(project, "HEAD", ROLE_OWNER)
    what = (f"a commit of {path} with the trailer {ROLE_OWNER!r}, in the orchestrator's own call on {TICKET} that "
            f"also replaces the commit with a twin without trailers")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)
