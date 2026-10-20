"""W2-58, item 4 -- (c) for the test designer: the ticket's implementation is refused, the base's code is read.

KPI success 2: "A session of role independent-test-designer on T is refused
reads of the files T's branch changes against its base, other than its own
tests, and reads the base's version of existing code [DEC-820 (c), DEC-826 Q2]".
KPI failure: "(c) still refuses, by every read route an honest agent takes in
ordinary work (DEC-801)".

The base of T's branch is where it leaves ``w2/integrate`` (the merge base, as
``git diff w2/integrate...HEAD`` uses it). T's commit changes
``src/app/main.py``, adds ``src/app/added.py``, adds its acceptance tests under
``tests/acceptance/W2-95/`` and changes its ticket file: the first two are
refused, the tests (its own) and the ticket file (the specification) are not.
In a repository with no ``w2/integrate`` there is no base, and nothing is
refused under this item.

The launcher (DEC-873 item 2): the ``--settings`` of ``gov launch
independent-test-designer <T>`` hold no ``Read`` deny rule and no sandbox read
denial that covers a file T's branch changes: the CLI turns every Read deny rule
that matches existing files into a read denial of the session's own commands,
whatever its form (P-W2-58-1), and the test designer could not import the code
it tests. The guard alone refuses (c); the held-out material keeps its Read
rules (b).
"""

from __future__ import annotations

import pytest

import w2_58_support as s

TD = s.TEST_DESIGNER
OWN_TEST = f"{s.T.acceptance}/test_feature.py"
TICKET_FILE = f".tickets/{s.T.tk}.md"


def _refused_calls(world, rel):
    copy = world.sandbox.tmpdir / "copy-of-the-code"
    return [
        s.read(world.path(rel)),
        s.grep(path=world.path(rel)),
        s.bash(f"cat {rel}"),
        s.bash(f"head -n 2 {rel}"),
        s.bash(f"grep -n {s.WORD} {rel}"),
        s.bash(f"git show HEAD:{rel}"),
        s.bash(f"cp {rel} {s.q(copy)}"),
    ]


PER_FILE_IDS = ("Read", "Grep-file", "cat", "head", "grep-file", "git-show-HEAD-path", "cp")


def _refused_searches(world):
    return [
        s.grep(path=world.path("src/app")),
        s.glob_call("src/app/*"),
        s.bash("ls src/app"),
        s.bash("find src/app -name '*.py'"),
        s.grep(),
        s.grep(path=world.path("src")),
        s.bash(f"grep -rn {s.WORD} src/"),
        s.bash(f"grep -r {s.WORD} ."),
        s.bash(f"rg {s.WORD}"),
        s.bash(f"git grep -n {s.WORD}"),
        s.bash(f"git diff {s.INTEGRATE}...HEAD"),
        s.bash("git show HEAD"),
        s.bash("git log -p"),
    ]


SEARCH_IDS = ("Grep-folder", "Glob-folder", "ls-folder", "find-folder", "Grep-no-path", "Grep-src", "grep-r-src",
              "grep-r-dot", "rg", "git-grep", "git-diff-base-HEAD", "git-show-HEAD", "git-log-p")


def _allowed_calls(world):
    base_sha = s.git(world.project, "rev-parse", s.INTEGRATE).strip()
    return [
        s.bash(f"git show {s.INTEGRATE}:src/app/main.py"),
        s.bash(f"git show {base_sha}:src/app/main.py"),
        s.read(world.path("src/other/main.py")),
        s.bash("cat src/other/main.py"),
        s.read(world.path("docs/notes.md")),
        s.grep(path=world.path("src/other")),
        s.bash(f"grep -rn {s.WORD} src/other/"),
        s.bash(f"git grep -n {s.WORD} -- src/other/"),
        s.bash("git log -p -- src/other/"),
        s.read(world.path(OWN_TEST)),
        s.bash(f"cat {OWN_TEST}"),
        s.read(world.path(TICKET_FILE)),
        s.bash(f"cat {TICKET_FILE}"),
        s.bash(f"git diff --stat {s.INTEGRATE}...HEAD"),
        s.bash(f"git diff --name-only {s.INTEGRATE}...HEAD"),
        s.bash(f"git diff --name-status {s.INTEGRATE}...HEAD"),
        s.bash("git show --stat HEAD"),
        s.bash(f"python3 -m pytest {s.T.acceptance}/ -q"),
    ]


ALLOWED_IDS = ("git-show-base-branch-path", "git-show-base-sha-path", "Read-unchanged", "cat-unchanged",
               "Read-unchanged-doc", "Grep-unchanged-folder", "grep-r-unchanged-folder", "git-grep-unchanged-folder",
               "git-log-p-unchanged-folder", "Read-own-test", "cat-own-test", "Read-ticket", "cat-ticket",
               "git-diff-stat", "git-diff-name-only", "git-diff-name-status", "git-show-stat", "pytest-own-tests")


@pytest.mark.parametrize("index", range(len(PER_FILE_IDS)), ids=PER_FILE_IDS)
@pytest.mark.parametrize("rel", s.CHANGED)
def test_the_test_designer_is_refused_the_files_the_branch_changes(branch_world, rel, index):
    call = _refused_calls(branch_world, rel)[index]
    s.assert_refused(branch_world.ask(call, TD), call, "test designer on T: ")


@pytest.mark.parametrize("index", range(len(SEARCH_IDS)), ids=SEARCH_IDS)
def test_the_test_designer_is_refused_searches_and_history_that_take_in_the_changed_files(branch_world, index):
    call = _refused_searches(branch_world)[index]
    s.assert_refused(branch_world.ask(call, TD), call, "test designer on T: ")


@pytest.mark.parametrize("index", range(len(ALLOWED_IDS)), ids=ALLOWED_IDS)
def test_the_test_designer_reads_the_base_its_tests_its_ticket_and_unchanged_code(branch_world, index):
    call = _allowed_calls(branch_world)[index]
    s.assert_allowed(branch_world.ask(call, TD), call, "test designer on T: ")


def test_the_base_version_it_reads_is_the_base_s(branch_world):
    """What the allowed ``git show w2/integrate:<path>`` shows: the base's code, not the branch's."""
    run = s.run_in_project(branch_world.sandbox, branch_world.project,
                           ["git", "show", f"{s.INTEGRATE}:src/app/main.py"], TD, s.T.tk)
    assert s.BASE_WORD in run.stdout and s.CHANGED_WORD not in run.stdout, run.describe()


@pytest.mark.parametrize("call_name", ("Read", "cat", "git-show-HEAD", "grep-r-dot"))
def test_with_no_base_branch_nothing_is_refused_under_this_item(open_world, call_name):
    calls = {
        "Read": s.read(open_world.path("src/app/main.py")),
        "cat": s.bash("cat src/app/added.py"),
        "git-show-HEAD": s.bash("git show HEAD:src/app/main.py"),
        "grep-r-dot": s.bash(f"grep -r {s.WORD} ."),
    }
    call = calls[call_name]
    s.assert_allowed(open_world.ask(call, TD), call, "test designer, no w2/integrate: ")


def test_another_role_on_t_reads_the_changed_files(branch_world):
    """(c) for the test designer binds the test designer only: product-spec and the ticket lead read the code."""
    for role, ticket in ((s.PRODUCT_SPEC, s.SPEC), (s.ORCHESTRATOR, s.T)):
        for call in (s.read(branch_world.path("src/app/main.py")), s.bash("cat src/app/added.py")):
            s.assert_allowed(branch_world.ask(call, role, ticket), call, f"{role}: ")


# --------------------------------------------------------------------------
# The launcher's --settings (DEC-873 item 2)
# --------------------------------------------------------------------------

def test_the_launch_adds_no_read_denial_for_the_changed_files_and_keeps_the_held_out_rules(sandbox, cli):
    """Rewritten by DEC-873 (was ``test_the_launch_denies_the_read_tool_the_changed_files_without_binding_the_sandbox``,
    which asked for a wildcard Read rule over the changed files on the belief that the Linux sandbox skips it).

    No Read deny rule and no sandbox read denial covers a file T's branch
    changes, nor its own tests, its ticket or unchanged code; the held-out
    material is still covered.
    """
    project = s.make_project(sandbox, base=True)
    settings = s.launch(sandbox, cli, TD, s.T).settings()
    faults = s.read_denial_faults(settings, project, sandbox.home, (*s.CHANGED, OWN_TEST, TICKET_FILE,
                                                                    "src/other/main.py"))
    assert not faults, (f"the launched test designer's settings deny reads of the code it tests (DEC-873 item 2): "
                        f"{faults}")
    lost = s.held_out_faults(settings, sandbox, project)
    assert not lost, f"the held-out material lost its Read deny rule for {lost}: {s.read_deny_specs(settings)}"


def test_the_launch_with_no_base_denies_the_read_tool_no_code(sandbox, cli):
    project = s.make_project(sandbox, base=False)
    settings = s.launch(sandbox, cli, TD, s.T).settings()
    for rel in s.CHANGED:
        covering = s.covering_read_rules(settings, project, sandbox.home, project / rel)
        assert not covering, f"with no w2/integrate a Read deny rule covers {rel}: {covering}"
