"""W2-58, the narrow extra round (DEC-880 item 1, P-W2-58-4 (a)) -- two behaviours the second review found missing.

KPI success (DEC-880): "A path with a leading ~ is judged as its expanded form
in every path the guard judges, on Read, Grep, Glob, Edit, Write and Bash: each
of (a) to (d) refuses it exactly as it refuses the absolute path, and each write
rule judges it as the absolute path; one test per tool." And: "An engineer runs
its own ticket's tests with python3 -B -m pytest, python3 -m coverage run -m
pytest and coverage run -m pytest, as with plain python3 -m pytest, and still
cannot read their source." KPI failure: "Each of (a) to (d) still refuses, by
every read route an honest agent takes in ordinary work (DEC-801); no write rule
widens; a guard error still fails closed."

Words as in this suite's README: **T** is the session's ticket; **T's
acceptance folder** is ``tests/acceptance/<T's wbs_id>/``; a **protected part**
is (c)'s acceptance folder for an engineer on T, (c)'s changed files for a test
designer on T, and (d)'s hidden part for a session an evaluation set measures;
**(a)** is a secret (a file under ``~/.ssh``, a ``.env`` file in the project).

1. **A path with a leading ``~`` is judged as its expanded form, on every
   tool.** Each case asks the guard twice, once with the absolute spelling and
   once with the ``~`` spelling of the same file, and asserts both get the
   case's answer, so that the case shows they agree.
2. **An engineer's own test runs with interpreter flags or under coverage** are
   allowed exactly as plain ``python3 -m pytest`` is; the source stays refused,
   alone or joined to such a run.

**How ``~`` is set up.** The guard is run as a program (``w2_58_support.ask_guard``)
with ``HOME`` set to the test's temporary ``home/`` folder
(``w2_58_support.base_environment``). The fixture project lies inside it, at
``<tmp-home>/gov-os-worktrees/W2-95``, so ``~/gov-os-worktrees/W2-95/<path>`` and
``<tmp-home>/gov-os-worktrees/W2-95/<path>`` name the same file. The stand-in
secret is ``<tmp-home>/.ssh/id_ed25519``, made by the fixture. No real home
folder is named.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w2_58_support as s

ACC = s.T.acceptance
TEST_FILE = f"{ACC}/test_feature.py"
HIDDEN_DIR = "eval/memory/hidden"
HIDDEN_FILE = f"{HIDDEN_DIR}/answers.yaml"
VISIBLE_FILE = "eval/memory/visible/questions.yaml"
SSH_KEY = ".ssh/id_ed25519"   # under the temporary HOME: a stand-in, never a key
W = s.WORD

REFUSED, ALLOWED = "refused", "allowed"

# The sessions, by name: (role, ticket).
SESSIONS = {
    "engineer-on-T": (s.ENGINEER, s.T),
    "test-designer-on-T": (s.TEST_DESIGNER, s.T),
    "auditor-on-T": (s.AUDITOR, s.T),
    "measured-by-role": (s.RESEARCH, s.EXPERIMENT),
    "measured-by-ticket": (s.ENGINEER, s.MEASURED),
}


def _world(request, name):
    return request.getfixturevalue({"branch": "branch_world", "eval": "eval_world"}[name])


def _absolute(world, where, rel):
    """The absolute path: ``rel`` under the project (``where`` "project") or under the temporary HOME ("home")."""
    return (world.project if where == "project" else world.sandbox.home) / rel


def _tilde(world, path):
    """The ``~`` spelling of an absolute path under the temporary HOME."""
    return "~/" + Path(path).relative_to(world.sandbox.home).as_posix()


def _assert_both(world, session, absolute_call, tilde_call, expected):
    """Ask the guard for both spellings; each must get ``expected``, and the message shows the other's answer."""
    role, ticket = SESSIONS[session]
    answers = [(absolute_call, world.ask(absolute_call, role, ticket)), (tilde_call, world.ask(tilde_call, role, ticket))]
    for index, (call, result) in enumerate(answers):
        other, other_result = answers[1 - index]
        who = f"{session} (the other spelling, {other}, got {other_result.decision}): "
        if expected == REFUSED:
            s.assert_refused(result, call, who)
        else:
            s.assert_allowed(result, call, who)


# --------------------------------------------------------------------------
# 1. A leading ~ is judged as its expanded form
# --------------------------------------------------------------------------

# id -> (world, session, (where, rel), expected)
READ_CASES = {
    "c-engineer-T-acceptance-test": ("branch", "engineer-on-T", ("project", TEST_FILE), REFUSED),
    "c-test-designer-changed-file": ("branch", "test-designer-on-T", ("project", "src/app/main.py"), REFUSED),
    "c-test-designer-added-file": ("branch", "test-designer-on-T", ("project", "src/app/added.py"), REFUSED),
    "d-measured-by-role-hidden": ("eval", "measured-by-role", ("project", HIDDEN_FILE), REFUSED),
    "d-measured-by-ticket-hidden": ("eval", "measured-by-ticket", ("project", HIDDEN_FILE), REFUSED),
    "a-engineer-ssh-key": ("branch", "engineer-on-T", ("home", SSH_KEY), REFUSED),
    "a-auditor-ssh-key": ("branch", "auditor-on-T", ("home", SSH_KEY), REFUSED),
    "a-engineer-dot-env": ("branch", "engineer-on-T", ("project", ".env"), REFUSED),
    "a-auditor-dot-env": ("branch", "auditor-on-T", ("project", "services/api/.env"), REFUSED),
    "ok-engineer-own-code": ("branch", "engineer-on-T", ("project", "src/app/main.py"), ALLOWED),
    "ok-test-designer-unchanged-code": ("branch", "test-designer-on-T", ("project", "src/other/main.py"), ALLOWED),
    "ok-measured-visible-part": ("eval", "measured-by-ticket", ("project", VISIBLE_FILE), ALLOWED),
    "ok-auditor-T-acceptance-test": ("branch", "auditor-on-T", ("project", TEST_FILE), ALLOWED),
}


@pytest.mark.parametrize("case", sorted(READ_CASES))
def test_read_judges_a_tilde_path_as_its_absolute_path(request, case):
    name, session, (where, rel), expected = READ_CASES[case]
    world = _world(request, name)
    path = _absolute(world, where, rel)
    _assert_both(world, session, s.read(path), s.read(_tilde(world, path)), expected)


# id -> (world, session, (where, rel), pattern, expected)
GREP_CASES = {
    "c-engineer-T-acceptance-folder": ("branch", "engineer-on-T", ("project", ACC), W, REFUSED),
    "c-engineer-from-the-project-root": ("branch", "engineer-on-T", ("project", "."), W, REFUSED),
    "c-test-designer-changed-folder": ("branch", "test-designer-on-T", ("project", "src/app"), W, REFUSED),
    "d-measured-by-ticket-hidden-folder": ("eval", "measured-by-ticket", ("project", HIDDEN_DIR), "q1", REFUSED),
    "a-engineer-ssh-key": ("branch", "engineer-on-T", ("home", SSH_KEY), "STAND", REFUSED),
    "a-engineer-dot-env": ("branch", "engineer-on-T", ("project", ".env"), "STAND_IN", REFUSED),
    "ok-engineer-src": ("branch", "engineer-on-T", ("project", "src"), W, ALLOWED),
    "ok-test-designer-src-other": ("branch", "test-designer-on-T", ("project", "src/other"), W, ALLOWED),
    "ok-measured-visible-folder": ("eval", "measured-by-ticket", ("project", "eval/memory/visible"), "q1", ALLOWED),
}


@pytest.mark.parametrize("case", sorted(GREP_CASES))
def test_grep_judges_a_tilde_path_as_its_absolute_path(request, case):
    name, session, (where, rel), pattern, expected = GREP_CASES[case]
    world = _world(request, name)
    path = _absolute(world, where, rel)   # rel "." is the project folder itself (pathlib drops the ".")
    _assert_both(world, session, s.grep(path=path, pattern=pattern), s.grep(path=_tilde(world, path), pattern=pattern),
                 expected)


# id -> (world, session, (where, rel) of the folder, form, expected); form "path": Glob "*" in the folder,
# "pattern": the folder's path with "/*" as the pattern and no path.
GLOB_CASES = {
    "c-engineer-T-acceptance-folder-as-path": ("branch", "engineer-on-T", ("project", ACC), "path", REFUSED),
    "c-engineer-T-acceptance-folder-in-pattern": ("branch", "engineer-on-T", ("project", ACC), "pattern", REFUSED),
    "d-measured-by-role-hidden-folder": ("eval", "measured-by-role", ("project", HIDDEN_DIR), "path", REFUSED),
    "d-measured-by-ticket-hidden-folder": ("eval", "measured-by-ticket", ("project", HIDDEN_DIR), "path", REFUSED),
    "ok-engineer-src-app": ("branch", "engineer-on-T", ("project", "src/app"), "path", ALLOWED),
    "ok-measured-visible-folder": ("eval", "measured-by-ticket", ("project", "eval/memory/visible"), "path", ALLOWED),
}


def _glob(folder, form):
    return s.glob_call("*", path=folder) if form == "path" else s.glob_call(f"{folder}/*")


@pytest.mark.parametrize("case", sorted(GLOB_CASES))
def test_glob_judges_a_tilde_path_as_its_absolute_path(request, case):
    name, session, (where, rel), form, expected = GLOB_CASES[case]
    world = _world(request, name)
    folder = _absolute(world, where, rel)
    _assert_both(world, session, _glob(folder, form), _glob(_tilde(world, folder), form), expected)


# id -> (world, session, command with {path}, (where, rel), expected); {path} is the absolute path (quoted) or the
# ~ spelling (unquoted, so the shell would expand it).
BASH_CASES = {
    "c-engineer-cat-T-acceptance-test": ("branch", "engineer-on-T", "cat {path}", ("project", TEST_FILE), REFUSED),
    "c-test-designer-grep-changed-folder": ("branch", "test-designer-on-T", f"grep -rn {W} {{path}}",
                                            ("project", "src/app"), REFUSED),
    "d-measured-by-ticket-cat-hidden": ("eval", "measured-by-ticket", "cat {path}", ("project", HIDDEN_FILE), REFUSED),
    "a-engineer-cat-ssh-key": ("branch", "engineer-on-T", "cat {path}", ("home", SSH_KEY), REFUSED),
    "a-auditor-cat-ssh-key": ("branch", "auditor-on-T", "cat {path}", ("home", SSH_KEY), REFUSED),
    "a-engineer-cat-dot-env": ("branch", "engineer-on-T", "cat {path}", ("project", ".env"), REFUSED),
    "ok-engineer-cat-own-code": ("branch", "engineer-on-T", "cat {path}", ("project", "src/app/main.py"), ALLOWED),
    "ok-test-designer-cat-unchanged-code": ("branch", "test-designer-on-T", "cat {path}",
                                            ("project", "src/other/main.py"), ALLOWED),
}


@pytest.mark.parametrize("case", sorted(BASH_CASES))
def test_bash_judges_a_tilde_path_as_its_absolute_path(request, case):
    name, session, command, (where, rel), expected = BASH_CASES[case]
    world = _world(request, name)
    path = _absolute(world, where, rel)
    _assert_both(world, session, s.bash(command.format(path=s.q(path))),
                 s.bash(command.format(path=_tilde(world, path))), expected)


# The write rules, for the engineer on T (allowed paths: src/app/**). id -> (rel, expected)
WRITE_TARGETS = {
    "T-acceptance-test": (TEST_FILE, REFUSED),
    "held-out-list": (s.HELD_OUT_LIST_REL, REFUSED),
    "settings-file": (s.SETTINGS_REL, REFUSED),
    "outside-allowed-paths": ("docs/notes.md", REFUSED),
    "inside-allowed-paths": ("src/app/main.py", ALLOWED),
}


@pytest.mark.parametrize("target", sorted(WRITE_TARGETS))
def test_write_judges_a_tilde_path_as_its_absolute_path(branch_world, target):
    rel, expected = WRITE_TARGETS[target]
    path = branch_world.path(rel)
    _assert_both(branch_world, "engineer-on-T", s.write_call(path), s.write_call(_tilde(branch_world, path)), expected)


@pytest.mark.parametrize("target", sorted(WRITE_TARGETS))
def test_edit_judges_a_tilde_path_as_its_absolute_path(branch_world, target):
    rel, expected = WRITE_TARGETS[target]
    path = branch_world.path(rel)
    _assert_both(branch_world, "engineer-on-T", s.edit_call(path), s.edit_call(_tilde(branch_world, path)), expected)


# --------------------------------------------------------------------------
# 2. The engineer's own test runs with interpreter flags or under coverage
# --------------------------------------------------------------------------

PLAIN_RUN = f"python3 -m pytest {ACC}/ -q"
FLAGGED_RUNS = {
    "python3-B": f"python3 -B -m pytest {ACC}/ -q",
    "python3-m-coverage-run": f"python3 -m coverage run -m pytest {ACC}/",
    "coverage-run": f"coverage run -m pytest {ACC}/",
}
# Each run joined with a read of the tests' source: refused as the read alone is.
JOINED_WITH_A_READ = {
    "plain-then-cat": f"{PLAIN_RUN}; cat {TEST_FILE}",
    "python3-B-then-cat": f"{FLAGGED_RUNS['python3-B']}; cat {TEST_FILE}",
    "python3-m-coverage-run-and-cat": f"{FLAGGED_RUNS['python3-m-coverage-run']} && cat {TEST_FILE}",
    "coverage-run-then-head": f"{FLAGGED_RUNS['coverage-run']}; head -n 5 {TEST_FILE}",
}


@pytest.mark.parametrize("form", sorted(FLAGGED_RUNS))
def test_the_engineer_runs_its_tests_with_interpreter_flags_or_under_coverage(branch_world, form):
    """Allowed exactly as the plain run is: both asked, both allowed."""
    for command in (PLAIN_RUN, FLAGGED_RUNS[form]):
        call = s.bash(command)
        s.assert_allowed(branch_world.ask(call, s.ENGINEER, s.T), call, "engineer on T: ")


def test_the_engineer_still_cannot_read_its_tests_source(branch_world):
    for call in (s.read(branch_world.path(TEST_FILE)), s.bash(f"cat {TEST_FILE}")):
        s.assert_refused(branch_world.ask(call, s.ENGINEER, s.T), call, "engineer on T: ")


@pytest.mark.parametrize("form", sorted(JOINED_WITH_A_READ))
def test_a_test_run_joined_with_a_read_of_the_source_is_refused(branch_world, form):
    call = s.bash(JOINED_WITH_A_READ[form])
    s.assert_refused(branch_world.ask(call, s.ENGINEER, s.T), call, "engineer on T: ")
