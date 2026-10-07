"""The git that ``gov close`` asks is not the caller's to bend (DEC-500, third behaviour; findings 6 and 8).

"An untracked file that is ignored only by a rule outside the commit (the repository's private exclude file,
an excludes file named by configuration or by the caller's environment) makes the tree not its commit.
Replacement refs are not followed, and configuration passed in the caller's environment does not reach the git
calls."

**A file ignored by a rule outside the commit.** The project is the one of
``test_an_untracked_file_at_the_root_that_makes_every_test_pass_refuses``: the committed acceptance test fails,
and an untracked ``conftest.py`` at the root makes the test runner pass every test. Here a rule that no commit
holds ignores that file:

- the repository's private exclude file (``.git/info/exclude``);
- an excludes file outside the project, named as git configuration in the environment of ``gov close`` only
  (``GIT_CONFIG_COUNT``, ``GIT_CONFIG_KEY_0=core.excludesFile``, ``GIT_CONFIG_VALUE_0``).

Each case first holds its fixture: git, asked with that rule, says the file is ignored and by which file; the
commit's own ignore file does not name it. The environment of every process the suite starts is built anew
(``support.sandbox_env``, ``support.git``), so git configuration in the environment of the suite's own run
reaches no case. The answer is round 8's for a tree that is not its commit: exit
code 1 ("could not measure", DEC-490), the path named, nothing closed, not counted, no repair ticket.

A file that the commit's own ignore file ignores refuses nothing, as before:
``test_a_file_git_ignores_refuses_nothing`` holds it and is unchanged (DEC-500 gives that shape to the owner).

**A replacement ref.** No commit of the ticket carries ``Implements:`` (the project of
``test_close_requires_implements_trailer``, with its checkpoint). For each of them the repository holds a
replacement (``refs/replace/<commit>``): the same commit with ``Implements: CAP-01`` added to its trailers.
The fixture holds that git shows the trailer where it follows replacements and none where it does not. The
trailers gate refuses as it does without the replacements: a finding, exit code 3, "Implements" named.
"""

import subprocess

import w1_30_support as support

TICKET = "PROJ-gitb"
WBS = "W1-gitb"
PLANTED = "conftest.py"
FEATURE = "src/example/feature.py"

# What pytest reads from the project's root before any test: every test function "passes" without being called.
EVERY_TEST_PASSES = (
    "import pytest\n\n\n"
    "@pytest.hookimpl(tryfirst=True)\n"
    "def pytest_pyfunc_call(pyfuncitem):\n"
    "    return True\n"
)


def _ignored_by(project, rel, env=None):
    """The file whose rule makes git ignore ``rel``, asked in ``env`` (without it: the suite's own git, which
    reads no configuration outside the project); ``None`` where git does not ignore it."""
    if env is None:
        out = support.git(project.root, "check-ignore", "-v", rel, check=False)
    else:
        out = subprocess.run(["git", "-C", str(project.root), "check-ignore", "-v", rel], env=env,
                             capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    return out.split(":", 1)[0] if out.strip() else None


def _a_failing_ticket_and_the_planted_file(project):
    support.build_ticket(project, TICKET, WBS, failing=True)
    project.write(PLANTED, EVERY_TEST_PASSES)
    assert PLANTED not in (project.root / ".gitignore").read_text(encoding="utf-8")
    assert support.git(project.root, "ls-files", "--", PLANTED) == "", "the fixture is wrong: the file is tracked"


def _refused_for_the_tree(project, interface, run):
    text = support.error_text(support.refused_without_a_finding(run, interface))
    assert PLANTED in text, f"the refusal does not name {PLANTED}\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    support.assert_nothing_counted(project, TICKET, run)
    support.assert_no_repair_ticket(project, run, TICKET)


def test_a_file_ignored_only_by_the_repositorys_private_exclude_file_refuses(project, sandbox, interface):
    _a_failing_ticket_and_the_planted_file(project)
    exclude = project.root / ".git" / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    exclude.write_text(f"{PLANTED}\n", encoding="utf-8")
    assert _ignored_by(project, PLANTED) == ".git/info/exclude", \
        f"the fixture is wrong: {PLANTED} is ignored by {_ignored_by(project, PLANTED)!r}"
    assert project.waiting_paths() == []

    run = support.run_close(project, sandbox, TICKET)

    _refused_for_the_tree(project, interface, run)


def test_a_file_ignored_only_by_an_excludes_file_named_in_the_callers_environment_refuses(
        project, sandbox, interface, tmp_path):
    _a_failing_ticket_and_the_planted_file(project)
    excludes = tmp_path / "the-callers-excludes"
    excludes.write_text(f"{PLANTED}\n", encoding="utf-8")
    env = {**support.sandbox_env(sandbox), "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.excludesFile",
           "GIT_CONFIG_VALUE_0": str(excludes)}
    assert _ignored_by(project, PLANTED, env=env) == str(excludes), \
        f"the fixture is wrong: in the caller's environment {PLANTED} is ignored by {_ignored_by(project, PLANTED, env=env)!r}"
    assert _ignored_by(project, PLANTED) is None and support.untracked_paths(project) == [PLANTED], \
        "the fixture is wrong: the file is ignored without the caller's environment too"
    support.load_store(project, sandbox)

    run = project.gov(sandbox, support.COMMAND, TICKET, "--json", env=env)

    _refused_for_the_tree(project, interface, run)


def _trailer(project, commit, key, *options):
    return support.git(project.root, *options, "log", "-1", f"--format=%(trailers:key={key},valueonly)",
                       commit).strip()


def test_a_replacement_ref_that_gives_a_commit_its_missing_trailer_does_not_pass_the_trailers_gate(
        project, sandbox, interface, tmp_path):
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write(FEATURE, "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=(f"Task: {TICKET}", support.ENGINEER_ROLE))
    commits = support.ticket_commits(project.root, TICKET)
    assert len(commits) == 2, f"the fixture is wrong: the ticket's commits are {commits}"
    for number, commit in enumerate(commits):
        body = support.git(project.root, "cat-file", "commit", commit)
        assert body.endswith("\n") and "Implements:" not in body
        replacement = tmp_path / f"replacement-{number}"
        replacement.write_text(body + "Implements: CAP-01\n", encoding="utf-8")
        new = support.git(project.root, "hash-object", "-t", "commit", "-w", str(replacement)).strip()
        support.git(project.root, "replace", commit, new)
        assert _trailer(project, commit, "Implements") == "CAP-01", \
            "the fixture is wrong: git does not show the replacement's trailer"
        assert _trailer(project, commit, "Implements", "--no-replace-objects") == "", \
            "the fixture is wrong: the commit itself carries the trailer"
    support.checkpointed(project, TICKET)
    assert project.waiting_paths() == []

    run = support.run_close(project, sandbox, TICKET)

    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    assert "implements" in text.lower(), f"the refusal does not name the missing trailer\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
