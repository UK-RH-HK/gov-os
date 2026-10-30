"""W2-58, item 3 -- (c) for the engineer: T's acceptance tests are refused to it, and it can still run them.

KPI success 1 (restated by DEC-873): "A session of role engineer on ticket T is
refused reads of tests/acceptance/<T's W2 id>/** by the guard, on every tool
read and the read side of every Bash route an honest agent takes (no OS-level
Read rule for it, DEC-873), and can still run those tests with pytest and see
their names, results and failure messages [DEC-820 (c)]".
KPI failure: "(c) still refuses, by every read route an honest agent takes in
ordinary work (DEC-801)".

T is ``DAEO-zz58`` (``wbs_id: W2-95``); its acceptance folder is
``tests/acceptance/W2-95/``. Another ticket's folder (``W2-96``) stays readable.

**The launcher (DEC-873 item 2):** the ``--settings`` value ``gov launch
engineer <T>`` hands the CLI holds no ``Read`` deny rule and no sandbox read
denial that covers a file of T's acceptance folder. The CLI turns every Read
deny rule that matches existing files into a read denial of the session's own
commands, whatever its form (``<folder>/**``, ``<file>*``, ``W2-5[8]/**``,
measured in P-W2-58-1): a wildcard does not keep the sandbox out, so pytest would
collect nothing. The guard alone refuses (c). The held-out material keeps its
Read rules (b). What a launched session does with this is in
``test_w2_58_launched_sessions.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

import w2_58_support as s

ACC = s.T.acceptance
TEST_FILE = f"{ACC}/test_feature.py"
OTHER_TEST = f"{s.OTHER.acceptance}/test_other.py"


def _refused_calls(world):
    copy = world.sandbox.tmpdir / "copy-of-the-tests"
    return [
        # content reads of a file in the folder
        s.read(world.path(TEST_FILE)),
        s.read(world.path(f"{ACC}/README.md")),
        s.grep(path=world.path(TEST_FILE)),
        s.bash(f"cat {TEST_FILE}"),
        s.bash(f"head -n 3 {TEST_FILE}"),
        s.bash(f"sed -n 1,5p {TEST_FILE}"),
        s.bash(f"awk 1 {TEST_FILE}"),
        s.bash(f"grep -n assert {TEST_FILE}"),
        s.bash(f"git show HEAD:{TEST_FILE}"),
        s.bash(f"cp {TEST_FILE} {s.q(copy)}"),
        # listings and searches aimed inside the folder
        s.grep(path=world.path(ACC)),
        s.glob_call(f"{ACC}/*"),
        s.glob_call("*", path=world.path(ACC)),
        s.bash(f"ls {ACC}"),
        s.bash(f"ls -la {ACC}/"),
        s.bash(f"find {ACC} -name '*.py'"),
        # content searches from a folder above it, with nothing that keeps it out
        s.grep(),
        s.grep(path=world.path("tests")),
        s.grep(path=world.path("tests/acceptance")),
        s.bash(f"grep -rn {s.WORD} tests/"),
        s.bash(f"grep -r {s.WORD} ."),
        s.bash(f"rg {s.WORD}"),
        s.bash(f"git grep -n {s.WORD}"),
        # history with nothing that keeps the folder out
        s.bash("git log -p"),
        s.bash("git show HEAD"),
        s.bash("git diff HEAD~1"),
        s.bash(f"git diff {s.INTEGRATE}...HEAD"),
    ]


REFUSED_IDS = (
    "Read-test", "Read-readme", "Grep-file", "cat", "head", "sed-n", "awk", "grep-file", "git-show-rev-path", "cp",
    "Grep-folder", "Glob-pattern", "Glob-path", "ls", "ls-la", "find",
    "Grep-no-path", "Grep-tests", "Grep-tests-acceptance", "grep-r-tests", "grep-r-dot", "rg", "git-grep",
    "git-log-p", "git-show-rev", "git-diff-rev", "git-diff-base",
)


def _allowed_calls(world):
    return [
        # running the tests
        s.bash(f"python3 -m pytest {ACC}/ -q"),
        s.bash(f"pytest {ACC}/"),
        # another ticket's tests
        s.read(world.path(OTHER_TEST)),
        s.bash(f"cat {OTHER_TEST}"),
        s.bash(f"git show HEAD:{OTHER_TEST}"),
        # searches narrowed to src/, and history that keeps the folder out
        s.grep(path=world.path("src")),
        s.bash(f"grep -rn {s.WORD} src/"),
        s.bash(f"git grep -n {s.WORD} -- src/"),
        s.bash("git log -p -- src/"),
        s.bash("git show --stat HEAD"),
        s.bash("git diff --stat HEAD~1"),
        s.bash(f"git diff --name-only {s.INTEGRATE}...HEAD"),
        s.bash("git log --name-status"),
        # everything else Policy 2 opens
        s.read(world.path("src/app/main.py")),
        s.bash("ls tests/acceptance/"),
        s.read(world.path(s.HELD_OUT_LIST_REL)),
    ]


ALLOWED_IDS = (
    "python3-m-pytest", "pytest", "Read-other-ticket", "cat-other-ticket", "git-show-other-ticket",
    "Grep-src", "grep-r-src", "git-grep-src", "git-log-p-src", "git-show-stat", "git-diff-stat", "git-diff-name-only",
    "git-log-name-status", "Read-code", "ls-tests-acceptance", "Read-held-out-list",
)


@pytest.mark.parametrize("index", range(len(REFUSED_IDS)), ids=REFUSED_IDS)
def test_the_engineer_is_refused_its_tickets_acceptance_tests(branch_world, index):
    call = _refused_calls(branch_world)[index]
    s.assert_refused(branch_world.ask(call, s.ENGINEER), call, "engineer on T: ")


@pytest.mark.parametrize("index", range(len(ALLOWED_IDS)), ids=ALLOWED_IDS)
def test_the_engineer_still_runs_its_tests_and_reads_the_rest(branch_world, index):
    call = _allowed_calls(branch_world)[index]
    s.assert_allowed(branch_world.ask(call, s.ENGINEER), call, "engineer on T: ")


def test_the_engineer_on_another_ticket_reads_ts_tests(branch_world):
    """(c) is per ticket: the engineer of W2-96 reads W2-95's tests."""
    for call in (s.read(branch_world.path(TEST_FILE)), s.bash(f"cat {TEST_FILE}")):
        s.assert_allowed(branch_world.ask(call, s.ENGINEER, s.OTHER), call, "engineer on W2-96: ")


def test_the_pytest_run_shows_names_results_and_failure_messages(branch_world):
    """What the allowed run shows: the failing test's name, its message, and the counts."""
    run = s.run_in_project(branch_world.sandbox, branch_world.project,
                           [sys.executable, "-m", "pytest", f"{ACC}/", "-q", "-p", "no:cacheprovider"],
                           s.ENGINEER, s.T.tk, timeout=120, extra_path=(Path(pytest.__file__).resolve().parents[1],))
    assert "test_the_feature_fails_with_a_message" in run.stdout, run.describe()
    assert s.FAILURE_WORD in run.stdout, run.describe()
    assert "1 failed, 1 passed" in run.stdout, run.describe()


# --------------------------------------------------------------------------
# The launcher's --settings (DEC-873 item 2)
# --------------------------------------------------------------------------

def _launch_settings(sandbox, cli, role, ticket):
    result = s.launch(sandbox, cli, role, ticket)
    return result.settings()


def test_the_launch_adds_no_read_denial_for_ts_tests_and_keeps_the_held_out_rules(sandbox, cli):
    """Rewritten by DEC-873 (was ``test_the_launch_denies_the_read_tool_ts_tests_without_binding_the_sandbox``,
    which asked for a wildcard Read rule over T's tests on the belief that the Linux sandbox skips it).

    No Read deny rule and no sandbox read denial covers a file of T's acceptance
    folder: the CLI would turn it into a read denial of the session's commands,
    and the engineer's pytest would collect nothing (P-W2-58-1). The held-out
    material is still covered.
    """
    project = s.make_project(sandbox, base=True)
    settings = _launch_settings(sandbox, cli, s.ENGINEER, s.T)
    faults = s.read_denial_faults(settings, project, sandbox.home, (TEST_FILE, f"{ACC}/README.md"))
    assert not faults, (f"the launched engineer's settings deny reads of its own acceptance tests (DEC-873 item 2): "
                        f"{faults}")
    lost = s.held_out_faults(settings, sandbox, project)
    assert not lost, f"the held-out material lost its Read deny rule for {lost}: {s.read_deny_specs(settings)}"


def test_the_launch_leaves_other_files_to_the_read_tool_and_keeps_the_held_out_rules(sandbox, cli):
    project = s.make_project(sandbox, base=True)
    settings = _launch_settings(sandbox, cli, s.ENGINEER, s.T)
    specs = s.read_deny_specs(settings)
    for rel in (OTHER_TEST, "src/app/main.py", s.HELD_OUT_LIST_REL, s.SETTINGS_REL):
        covering = [spec for spec in specs if s.rule_covers(spec, project / rel, project, sandbox.home)]
        assert not covering, f"a Read deny rule of the launched engineer covers {rel}: {covering}"
    held = sandbox.held_out / "answers.md"
    assert any(s.rule_covers(spec, held, project, sandbox.home) for spec in specs), (
        f"the held-out material lost its Read deny rule: {specs}")
