"""KPI failure 1: "A planted GIT_DIR or GIT_INDEX_FILE in a hook's environment reaches no child git call", and
the list rows of KPI success 1 [W2-M105, W2-M113, W2-M161, W2-L160].

"Planted" is a ``GIT_DIR`` and a ``GIT_INDEX_FILE`` that name a decoy repository (``make_decoy``: a commit, a
second branch, a staged change), as a hook's environment would carry them. "Reaches no child git call" is
observed from outside: the decoy's every byte (its ``.git`` included) is as it was, and the call does its work
on its own folder as it would with no plant (a check measures, a staged secret is found, a change is caught).

Which ``GIT_*`` value a call may keep (reading P-1, accepted by the owner, DEC-804 item 3): an inherited
``GIT_INDEX_FILE`` is honoured only for git calls in the project root, when it is git's own index there (``git
commit -a`` gives the hook an ``index.lock`` in the git directory); a program that may start git elsewhere gets no
index (``test_w2_05_declared_check.py``); any other value is cleared. The cases of ``_on_purpose`` hold that reading
from the other side: a hooked ``git commit -a`` and ``git commit -- <path>`` still have their secret found.

The staged-secrets gate is held to the stricter behaviour that stands under either answer to P-1 (independent
review F1, DEC-413 round 1): it never passes on an index other than the one being committed. An inherited
``GIT_INDEX_FILE`` that is not git's own index of the project (a decoy's, or any file outside the project's git
directory) is refused, and the refusal names it, whatever that index or the project's own index holds.

The list rows:

- W2-M105, ``gov.guard.containment_merge``: a merge is read with ``GIT_TRACE*`` cleared, and with
  ``GIT_NO_LAZY_FETCH`` set: in a partial clone a missing object is never fetched (the read fails instead).
- W2-M113, the containment check's git calls (W1-03's PostToolUse hook) run with a cleared environment and
  pinned configuration: a planted decoy, planted trace variables and a trace setting in the person's git
  configuration change nothing and write nothing.
- W2-M161, every subprocess of ``gov close`` (its test run included: the test helper) runs with a sanitised
  environment and pinned configuration. Red until W2-53 merges (``src/gov/close/**``).
- W2-L160, the guard hook resolves git by absolute path, and its freeze look-up has a limit of its own of 15 s
  (DEC-783 item 2), below the hook's 20 s deadline (DEC-580: the guard answers refuse). W2-50 has merged; this
  ticket's resume makes the change to ``src/gov/guard/decide.py``.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

import w2_05_support as support
from w2_05_support import skip_without

STAGED_SECRET_EXIT = "SECRET_STAGED"
# The freeze look-up's own limit (DEC-783 item 2; reading P-2 as decided), and the window its refusal is held to, on
# the test's clock from the start of the hook's process to its end: not before FREEZE_FROM_S (the look-up was waited
# for up to its limit; 0.5 s for the clocks), and by FREEZE_BY_S (3 s for the hook's start and its answer after the
# limit; 1 s before 19 s, the earliest the hook deadline's answer comes in W1-02's deadline cases, and 2 s before the
# hook's 20 s deadline, DEC-580).
FREEZE_LIMIT_S = 15.0
FREEZE_FROM_S = 14.5
FREEZE_BY_S = 18.0


def assert_untouched(decoy, what):
    repo, before = decoy
    after = support.folder_fingerprint(repo)
    changed = sorted(rel for rel in set(before) | set(after) if before.get(rel) != after.get(rel))
    assert not changed, (f"{what}: the planted GIT_DIR / GIT_INDEX_FILE reached a child git call; the decoy "
                         f"repository changed: {changed[:12]}\n" + support.git(repo, "log", "--all", "--oneline",
                                                                           "-5"))


def assert_no_trace(folder, what):
    written = support.written_traces(folder)
    assert not written, f"{what}: a child git call wrote the planted trace target(s) {written}"


# --------------------------------------------------------------------------
# a check and a command under a planted GIT_DIR / GIT_INDEX_FILE (KPI failure 1)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("how", ("the check's declared command", "gov ci checks G1"))
def test_the_retrieval_check_under_a_planted_git_dir_measures_and_leaves_the_decoy(tmp_path, box, retrieval_env,
                                                                                    decoy, how):
    project = support.gov_project(tmp_path / "project")
    env = dict(retrieval_env, **support.planted(decoy[0]))
    command = support.retrieval_check_command() if how.startswith("the check") else "gov ci checks G1"

    done = box.run(["sh", "-c", command], cwd=project, env=env)

    assert_untouched(decoy, f"`{command}` under a planted GIT_DIR")
    assert done.returncode == 0, f"`{command}` under a planted GIT_DIR is not green:\n{support.said(done)}"
    if how.startswith("the check"):
        assert support.measured(done.stdout + done.stderr), f"the check did not measure:\n{support.said(done)}"


def _secrets_repo(root, secret):
    repo = support.new_repo(root, {"README.md": "# A project\n",
                                   ".gitleaks.toml": support.GITLEAKS_RULES.read_text(encoding="utf-8")})
    support.write(repo, "config.txt", f"token = {support.SECRET}\n" if secret else "token = none\n")
    support.git(repo, "add", "config.txt")
    return repo


def _scan(box, repo, **plants):
    return box.run(["gov", "ci", "staged-secrets", "--json"], cwd=repo, env=box.env(**plants))


def assert_index_refused(done, index, what):
    """The staged-secrets gate refused the index it may not take as the commit's (independent review F1): a
    non-zero exit and a refusal that names that index, whatever either index holds. It never answers pass."""
    output = done.stdout + done.stderr
    assert done.returncode != 0, (
        f"{what}: gov ci staged-secrets passed on an index other than the one being committed ({index}); it "
        f"must refuse it:\n{support.said(done)}")
    assert support.names_path(output, index), (
        f"{what}: gov ci staged-secrets refused, but not the index it could not take as the commit's: the refusal "
        f"does not name {index}:\n{support.said(done)}")


# Rewritten (independent review F1, DEC-413 round 1; was ``test_a_staged_secret_is_found_under_a_planted_decoy_index``,
# which expected the staged-secret refusal): the planted index is not git's own index of the project, so the gate
# refuses it, naming it, instead of scanning another index.
@pytest.mark.parametrize("plants", ("GIT_INDEX_FILE", "GIT_DIR and GIT_INDEX_FILE"))
def test_a_staged_secret_under_a_planted_decoy_index_is_refused_naming_the_index(tmp_path, box, plants):
    skip_without("gitleaks")
    repo = _secrets_repo(tmp_path / "project", secret=True)
    decoy_repo = _secrets_repo(tmp_path / "elsewhere" / "decoy", secret=False)
    decoy = (decoy_repo, support.folder_fingerprint(decoy_repo))
    planted = support.planted(decoy_repo)
    if plants == "GIT_INDEX_FILE":
        planted.pop("GIT_DIR")

    done = _scan(box, repo, **planted)

    assert_index_refused(done, planted["GIT_INDEX_FILE"], f"a secret staged in the project under a planted {plants}")
    assert_untouched(decoy, f"gov ci staged-secrets under a planted {plants}")


# Rewritten (independent review F1, DEC-413 round 1; was ``test_a_clean_index_is_not_refused_for_a_decoy_s_staged_
# secret[GIT_DIR and GIT_INDEX_FILE]``, which expected a pass): a planted index is refused, never passed.
def test_a_clean_index_under_a_planted_decoy_index_is_refused_naming_the_index(tmp_path, box):
    skip_without("gitleaks")
    repo = _secrets_repo(tmp_path / "project", secret=False)
    decoy_repo = _secrets_repo(tmp_path / "elsewhere" / "decoy", secret=True)
    decoy = (decoy_repo, support.folder_fingerprint(decoy_repo))
    planted = support.planted(decoy_repo)

    done = _scan(box, repo, **planted)

    assert_index_refused(done, planted["GIT_INDEX_FILE"],
                         "the project's clean index under a planted GIT_DIR and GIT_INDEX_FILE")
    assert_untouched(decoy, "gov ci staged-secrets under a planted GIT_DIR and GIT_INDEX_FILE")


@pytest.mark.parametrize("plants", ("GIT_DIR",))
def test_a_clean_index_is_not_refused_for_a_decoy_s_staged_secret(tmp_path, box, plants):
    skip_without("gitleaks")
    repo = _secrets_repo(tmp_path / "project", secret=False)
    decoy_repo = _secrets_repo(tmp_path / "elsewhere" / "decoy", secret=True)
    decoy = (decoy_repo, support.folder_fingerprint(decoy_repo))
    planted = support.planted(decoy_repo)
    if plants == "GIT_DIR":
        planted.pop("GIT_INDEX_FILE")

    done = _scan(box, repo, **planted)

    assert done.returncode == 0, (f"the project's clean index was refused under a planted {plants} (it read the "
                                  f"decoy's staged secret):\n{support.said(done)}")
    assert_untouched(decoy, f"gov ci staged-secrets under a planted {plants}")


# --------------------------------------------------------------------------
# an index outside the project's git directory: the commit's index, never git's own (independent review F1)
# --------------------------------------------------------------------------

_CLEAN, _SECRET = "token = none\n", f"token = {support.SECRET}\n"

_OUTSIDE = {
    "a secret in that index, the project's index clean": (_SECRET, None),
    "nothing secret in that index, the project's index clean": ("token = rotated\n", None),
    "nothing secret in that index, a secret in the project's index": ("token = rotated\n", _SECRET),
}


@pytest.mark.parametrize("case", tuple(_OUTSIDE))
def test_staged_secrets_refuses_an_inherited_index_outside_the_git_directory_naming_it(tmp_path, box, case):
    """A person or a tool commits with ``GIT_INDEX_FILE=<a file outside the git directory>``: that file is the
    commit's index, and it is not git's own index of the project. The gate may not scan another index in its
    place: it refuses, naming the index, whatever either index holds."""
    skip_without("gitleaks")
    in_that_index, in_the_project = _OUTSIDE[case]
    repo = support.new_repo(tmp_path / "project", {
        "README.md": "# A project\n", "config.txt": _CLEAN,
        ".gitleaks.toml": support.GITLEAKS_RULES.read_text(encoding="utf-8")})
    index = support.index_outside_the_git_directory(repo, tmp_path / "elsewhere" / "commit-index",
                                                    {"config.txt": in_that_index})
    if in_the_project is not None:
        support.write(repo, "config.txt", in_the_project)
        support.git(repo, "add", "config.txt")

    done = _scan(box, repo, GIT_INDEX_FILE=index)

    assert_index_refused(done, index, f"an inherited GIT_INDEX_FILE outside the git directory ({case})")


def test_a_hooked_commit_with_its_index_outside_the_git_directory_and_a_secret_there_does_not_land(tmp_path, box):
    """The project's own ``lefthook.yml`` installed by lefthook in a temporary repository (G1 and G2 each a
    declared check that passes). A commit made with ``GIT_INDEX_FILE`` naming a file outside the git directory,
    a secret staged in that index only, does not land: the branch, the indexes and the reflogs stay as they were."""
    skip_without("lefthook", "gitleaks")
    assert support.LEFTHOOK_YML.is_file(), "lefthook.yml is absent from the repository root"
    repo = support.gov_project(tmp_path / "repo", hooks_file=support.LEFTHOOK_YML, retrieval=False)
    support.declare_check(repo, "w2-05-g1", "graph integrity", "G1", "true")
    support.git(repo, "add", "-A")
    support.git(repo, "commit", "-q", "-m", "a G1 check that passes")
    installed = box.run(["lefthook", "install"], cwd=repo, env=box.env())
    assert installed.returncode == 0, f"lefthook install refused the project's lefthook.yml:\n{support.said(installed)}"
    assert (support.common_dir_of(repo) / "hooks" / "pre-commit").is_file(), "lefthook installed no pre-commit hook"
    support.write(repo, "notes.md", "the first line\na plain change\n")
    support.git(repo, "add", "notes.md")
    plain = box.run([support.GIT, "commit", "-q", "-m", "a plain change"], cwd=repo, env=box.env(),
                    timeout=support.HOOKED_COMMIT_TIMEOUT_S)
    assert plain.returncode == 0, (f"a plain hooked commit with nothing secret was refused; the case needs hooks "
                                   f"that let it through:\n{support.said(plain)}")
    index = support.index_outside_the_git_directory(repo, tmp_path / "elsewhere" / "commit-index",
                                                    {"config.txt": _SECRET})
    before = support.repo_state(repo, [repo])
    staged = support.staged_in(repo, index)

    done = box.run([support.GIT, "commit", "-q", "-m", "a secret in another index"], cwd=repo,
                   env=box.env(GIT_INDEX_FILE=index), timeout=support.HOOKED_COMMIT_TIMEOUT_S)

    after = support.repo_state(repo, [repo])
    landed = after.heads[str(repo)] != before.heads[str(repo)]
    assert done.returncode != 0 and not landed, (
        "a commit whose index lies outside the git directory, with a secret staged there, landed: the "
        f"staged-secrets gate passed on another index\n{support.git(repo, 'log', '-2', '--format=%h %s')}"
        f"{support.said(done)}")
    assert after.refs == before.refs, (
        f"a refused commit moved refs: { {k: v for k, v in after.refs.items() if before.refs.get(k) != v} }")
    assert after.reflogs == before.reflogs, "a refused commit changed a reflog"
    assert after.reachable == before.reachable, "a refused commit left new commits reachable"
    assert after.indexes == before.indexes, "a refused commit changed the project's index"
    assert support.staged_in(repo, index) == staged, "a refused commit changed the index it was made with"


# --------------------------------------------------------------------------
# GIT_* set on purpose for the call's own folder (the edge case: git's own index of a commit)
# --------------------------------------------------------------------------

_ON_PURPOSE = {
    "git commit -a, a secret in a tracked file": (["-a"], True),
    "git commit -- <path>, a secret in that file": (["--", "config.txt"], True),
    "git commit -a, nothing secret": (["-a"], False),
}


@pytest.mark.parametrize("case", tuple(_ON_PURPOSE))
def test_a_hooked_commit_in_a_linked_worktree_scans_the_index_git_gives_it(tmp_path, box, case):
    """git gives the hook an index of its own (``index.lock``, or a ``next-index-*.lock`` for a commit of named
    paths) in the worktree's git directory: the secret is only there, never staged in the worktree's index."""
    skip_without("gitleaks")
    extra, secret = _ON_PURPOSE[case]
    main = support.new_repo(tmp_path / "repo", {
        "README.md": "# A project\n", "config.txt": "token = none\n",
        ".gitleaks.toml": support.GITLEAKS_RULES.read_text(encoding="utf-8")})
    tree = support.add_worktree(main, tmp_path / "wt")
    support.plain_hook(main, box.marks, "gov ci staged-secrets", result=True)
    support.write(tree, "config.txt", f"token = {support.SECRET}\n" if secret else "token = rotated\n")
    head = support.git(tree, "rev-parse", "HEAD").strip()

    done = box.run([support.GIT, "commit", "-q", "-m", "change the config", *extra], cwd=tree, env=box.env(),
                   timeout=support.HOOKED_COMMIT_TIMEOUT_S)

    code, output = support.hook_result(box.marks)
    assert code is not None, f"the pre-commit hook did not run:\n{support.said(done)}"
    moved = support.git(tree, "rev-parse", "HEAD").strip() != head
    if secret:
        assert not moved and done.returncode != 0, (
            f"`{case}`: the secret git gave the hook to commit was not found; the commit went through:\n"
            f"{output[-2000:]}")
        assert STAGED_SECRET_EXIT in output, f"`{case}`: the hook refused, but not for the secret:\n{output[-2000:]}"
    else:
        assert moved and done.returncode == 0, f"`{case}`: a commit with no secret was refused:\n{output[-2000:]}"


# --------------------------------------------------------------------------
# W2-M105: gov.guard.containment_merge reads a merge with trace variables cleared and no lazy fetch
# --------------------------------------------------------------------------

_READ_MERGE = (
    "import json, sys\n"
    "from gov.guard.containment_merge import read_merge\n"
    "try:\n"
    "    reading = read_merge(sys.argv[1], sys.argv[2])\n"
    "except Exception as error:\n"
    "    print(json.dumps({'raised': [type(error).__module__, type(error).__name__, str(error)]}))\n"
    "else:\n"
    "    print(json.dumps({'own': sorted(map(str, reading.own)), 'brought': sorted(map(str, reading.brought))}))\n"
)


def _merge_repo(root):
    """A merge of a side branch (``b.txt``) into ``main`` (``c.txt``) that adds a change of its own (``d.txt``)."""
    repo = support.new_repo(root, {"a.txt": "a\n"})
    support.git(repo, "checkout", "-q", "-b", "side")
    support.write(repo, "b.txt", "b\n")
    support.git(repo, "add", "-A")
    support.git(repo, "commit", "-q", "-m", "b")
    support.git(repo, "checkout", "-q", support.BRANCH)
    support.write(repo, "c.txt", "c\n")
    support.git(repo, "add", "-A")
    support.git(repo, "commit", "-q", "-m", "c")
    support.git(repo, "merge", "-q", "--no-ff", "-m", "merge", "side")
    support.write(repo, "d.txt", "own\n")
    support.git(repo, "add", "-A")
    support.git(repo, "commit", "-q", "--amend", "--no-edit")
    return repo, support.git(repo, "rev-parse", "HEAD").strip()


def _read_merge(box, repo, merge, **env):
    done = box.run([sys.executable, "-c", _READ_MERGE, repo, merge], cwd=box.tmp, env=box.env(**env))
    assert done.returncode == 0 and done.stdout.strip(), f"the read_merge driver did not answer:\n{support.said(done)}"
    return json.loads(done.stdout.strip().splitlines()[-1])


def test_read_merge_under_planted_trace_variables_writes_no_trace(tmp_path, box):
    repo, merge = _merge_repo(tmp_path / "repo")
    plain = _read_merge(box, repo, merge)
    assert "raised" not in plain, f"read_merge could not read a plain merge; the case needs one: {plain}"
    traces = tmp_path / "traces"

    reading = _read_merge(box, repo, merge, **support.trace_plants(traces))

    assert_no_trace(traces, "read_merge under planted GIT_TRACE variables (W2-M105)")
    assert reading == plain, f"read_merge read the merge otherwise under planted trace variables: {reading} != {plain}"


def test_read_merge_under_a_planted_git_dir_reads_its_own_repository(tmp_path, box, decoy):
    repo, merge = _merge_repo(tmp_path / "repo")
    plain = _read_merge(box, repo, merge)

    reading = _read_merge(box, repo, merge, **support.planted(decoy[0]))

    assert reading == plain, f"read_merge read the merge otherwise under a planted GIT_DIR: {reading} != {plain}"
    assert_untouched(decoy, "read_merge under a planted GIT_DIR")


def test_read_merge_in_a_partial_clone_fetches_nothing(tmp_path, box):
    """A clone made with ``--filter=tree:0`` lacks the trees of the merge; its ``origin`` serves them through a
    marking ``upload-pack``. With ``GIT_NO_LAZY_FETCH`` set by the code, nothing is fetched and the read fails
    (it cannot know the merge's files); without it git fetches the trees behind the reader's back."""
    no_fetch = dict(support.clean_env(), GIT_NO_LAZY_FETCH="1")
    repo, merge = _merge_repo(tmp_path / "repo")
    server = tmp_path / "server.git"
    support.git(tmp_path, "clone", "-q", "--bare", repo, server, env=no_fetch)
    support.git(server, "config", "uploadpack.allowFilter", "true", env=no_fetch)
    support.git(server, "config", "uploadpack.allowAnySHA1InWant", "true", env=no_fetch)
    clone = tmp_path / "clone"
    support.git(tmp_path, "clone", "-q", "--no-checkout", "--filter=tree:0", f"file://{server}", clone, env=no_fetch)
    mark = tmp_path / "fetch-mark"
    upload = tmp_path / "upload-pack"
    upload.write_text(f"#!/bin/sh\necho \"$*\" >> {support.sh_quote(mark)}\nexec git-upload-pack \"$@\"\n")
    upload.chmod(0o755)
    support.git(clone, "config", "remote.origin.uploadpack", upload, env=no_fetch)
    missing = support.git(clone, "rev-list", "--objects", "--missing=print", merge, env=no_fetch)
    assert any(line.startswith("?") for line in missing.splitlines()), "the partial clone lacks nothing; the case is wrong"

    reading = _read_merge(box, clone, merge)

    fetched = mark.read_text().splitlines() if mark.is_file() else []
    assert not fetched, (f"read_merge fetched {len(fetched)} time(s) from origin in a partial clone "
                         f"(GIT_NO_LAZY_FETCH was not set, W2-M105); it answered {reading}")
    assert "raised" in reading, f"read_merge answered without the merge's trees, instead of failing: {reading}"


# --------------------------------------------------------------------------
# W2-M113: the containment check (W1-03's PostToolUse hook) with a cleared environment and pinned configuration
# --------------------------------------------------------------------------

@pytest.mark.parametrize("plant", ("a decoy GIT_DIR and GIT_INDEX_FILE", "trace variables",
                                   "a trace setting in the person's git configuration"))
def test_the_containment_check_catches_the_change_whatever_its_environment_holds(tmp_path, decoy, plant):
    import w1_03_support as w103
    project = w103.make_project(tmp_path / "project")
    sandbox = w103.make_sandbox(tmp_path / "sandbox")
    traces = tmp_path / "traces"
    call = w103.script_call(sandbox, "echo changed >> README.md")
    guard = w103.run_guard(project, call, sandbox, role=w103.ENGINEER, ticket=w103.TICKET_ID)
    w103.assert_let_through(guard, call)
    bash = w103.run_bash(project, call.command, sandbox)
    if plant.startswith("a decoy"):
        environment = support.planted(decoy[0])
    elif plant == "trace variables":
        environment = support.trace_plants(traces)
    else:
        traces.mkdir()
        (sandbox.home / ".gitconfig").write_text(f"[trace2]\n\teventTarget = {traces / 'user-config-trace2'}\n")
        xdg = tmp_path / "xdg"
        support.write(xdg, "git/config", f"[trace2]\n\teventTarget = {traces / 'xdg-config-trace2'}\n")
        environment = {"XDG_CONFIG_HOME": str(xdg)}

    result = w103.run_check(project, call, sandbox, role=w103.ENGINEER, ticket=w103.TICKET_ID, bash=bash,
                            environment=environment)

    w103.assert_caught(result, "README.md", what=f"`echo changed >> README.md` with {plant} in the hook's environment")
    assert_no_trace(traces, f"the containment check with {plant}")
    assert_untouched(decoy, f"the containment check with {plant}")


# --------------------------------------------------------------------------
# W2-M161: every subprocess of gov close, its test run included (red until W2-53 merges)
# --------------------------------------------------------------------------

_ENV_TEST = '''"""Records the GIT_* variables and the git configuration this test run sees (W2-05, W2-M161)."""
import json
import os
import subprocess


def test_records_its_git_environment():
    seen = sorted(name for name in os.environ if name.startswith("GIT_"))
    with open({record!r}, "w", encoding="utf-8") as handle:
        json.dump(seen, handle)
    subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True)
'''


def test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment(tmp_path, decoy):
    """Red until W2-53 merges (``src/gov/close/**``)."""
    import w2_01_support as w201
    base = w201.base
    ticket, wbs = "PROJ-genv", "W1-genv"
    record = tmp_path / "seen-by-the-test.json"
    traces = tmp_path / "traces"
    project = w201.Project(tmp_path / "project")
    w201.create_ticket(project, ticket, wbs)
    project.write(f"tests/acceptance/{wbs}/test_records_its_environment.py", _ENV_TEST.format(record=str(record)))
    project.commit("acceptance tests: the environment", who=w201.TEST_DESIGNER,
                   trailers=w201.trailers_of(ticket, role="independent-test-designer"), exact=True)
    w201.engineer_commit(project, ticket, {"src/example/feature.py": "# feature\n"})
    w201.checkpointed(project, ticket)
    sandbox = w201.cli_support.make_sandbox(tmp_path / "sandbox")
    interface = w201.cli_support.load_interface(w201.REPO_ROOT)
    plants = dict(support.planted(decoy[0]), **support.trace_plants(traces))
    traces.mkdir(exist_ok=True)
    gitconfig = Path(sandbox.home) / ".gitconfig"
    gitconfig.write_text((gitconfig.read_text() if gitconfig.is_file() else "")
                         + f"[trace2]\n\teventTarget = {traces / 'user-config-trace2'}\n")
    env = dict(base.sandbox_env(sandbox), **plants)

    run = base.run_close(project, sandbox, ticket, env=env)

    assert record.is_file(), f"gov close did not run the ticket's acceptance test:\n{run.describe()}"
    reached = sorted(set(json.loads(record.read_text())) & set(plants))
    assert not reached, f"the planted {reached} reached the test run of gov close (W2-M161):\n{run.describe()}"
    assert_no_trace(traces, "gov close with planted trace variables and a trace setting (W2-M161)")
    assert_untouched(decoy, "gov close under a planted GIT_DIR")
    w201.closed(run, interface)


# --------------------------------------------------------------------------
# W2-L160: the guard hook's git by absolute path, and the freeze look-up's own limit (red until W2-50 merges)
# --------------------------------------------------------------------------

def _guard_project(tmp_path):
    import w1_02_support as w102
    project = w102.make_project(tmp_path / "project")
    return w102, project, w102.make_sandbox(tmp_path / "sandbox")


def test_the_guard_hook_does_not_run_the_git_first_on_path(tmp_path):
    """Red until W2-50 merges (``src/gov/guard/decide.py``)."""
    w102, project, sandbox = _guard_project(tmp_path)
    tool_input = w102.edit_tool_input("Write", project / "src/gov/guard/decide.py")
    plain = w102.run_hook(project, "Write", tool_input, sandbox, role=w102.ENGINEER, ticket=w102.TICKET_ID)
    assert plain.decision == "allow", f"the guard did not allow an in-scope write; the case needs it: {plain.describe()}"
    fake = tmp_path / "fake-bin"
    fake.mkdir()
    mark = tmp_path / "fake-git-ran"
    (fake / "git").write_text(f"#!/bin/sh\necho \"$*\" >> {support.sh_quote(mark)}\nexec {support.GIT} \"$@\"\n")
    (fake / "git").chmod(0o755)

    result = w102.run_hook(project, "Write", tool_input, sandbox, role=w102.ENGINEER, ticket=w102.TICKET_ID,
                           extra_env={"PATH": f"{fake}:{os.environ.get('PATH', support.SYSTEM_PATH)}"})

    ran = mark.read_text().splitlines() if mark.is_file() else []
    assert not ran, f"the guard hook ran the git first on PATH, not git by absolute path (W2-L160): {ran[:3]}"
    assert result.decision == plain.decision, f"the guard decided otherwise: {result.describe()}"


# Rewritten (DEC-783 item 2: the freeze look-up's own limit is 15 seconds; was held to "an answer within 18 s",
# reading P-2): the refusal is the look-up's own, at its 15 s limit, never the hook deadline's at 20 s.
def test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs(tmp_path, fifo_cleanup):
    """The worktree's ``HEAD`` in its git directory is a fifo: every git that opens it waits. The guard's freeze
    look-up gives up at its own limit of 15 s (DEC-783 item 2) and the guard refuses (DEC-580): the answer is
    ``deny``, not before 14.5 s and by 18 s, so it is the look-up's own and not the hook deadline's (20 s)."""
    w102, project, sandbox = _guard_project(tmp_path)
    tree = tmp_path / "wt"
    w102.git(project, "worktree", "add", "-q", str(tree), "-b", "w2-05/guard")
    head = support.git_dir_of(tree) / "HEAD"
    head.unlink()
    os.mkfifo(head)
    fifo_cleanup.append(head)

    result = w102.run_hook(tree, "Write", w102.edit_tool_input("Write", tree / "src/gov/guard/decide.py"), sandbox,
                           role=w102.ENGINEER, ticket=w102.TICKET_ID)

    assert result.decision != "timeout", (
        f"the guard hook did not answer within the hook's {w102.HOOK_TIMEOUT_S:.0f} s deadline while its freeze "
        f"look-up waited (W2-L160: the look-up has no limit of its own of {FREEZE_LIMIT_S:.0f} s, DEC-783 item 2): "
        f"{result.describe()}")
    assert result.decision == "deny", (
        f"the guard hook did not refuse when its freeze look-up hung (DEC-580): {result.describe()} "
        f"after {result.seconds:.1f} s")
    assert result.seconds >= FREEZE_FROM_S, (
        f"the guard hook refused after {result.seconds:.1f} s: before the freeze look-up's own limit of "
        f"{FREEZE_LIMIT_S:.0f} s (DEC-783 item 2; not before {FREEZE_FROM_S} s): {result.describe()}")
    assert result.seconds <= FREEZE_BY_S, (
        f"the guard hook refused after {result.seconds:.1f} s: not by the freeze look-up's own limit of "
        f"{FREEZE_LIMIT_S:.0f} s (by {FREEZE_BY_S:.0f} s); a refusal this late is the hook deadline's "
        f"({w102.HOOK_TIMEOUT_S:.0f} s, DEC-580), not the look-up's: {result.describe()}")
