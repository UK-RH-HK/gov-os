"""Support code for the W1-28 acceptance tests (``gov pause``).

The tests use the command only through public interfaces:

- the ``gov pause`` command line with ``--json`` (W1-07's console-script
  stand-in, ``w1_07_support``), its API-0002 envelope and its exit code;
- the guard's PreToolUse hook, started as a process the way W1-02's suite
  starts it (``w1_02_support``);
- ``gov.tasks`` (W1-09), each call in a new process;
- ``git``, and the files a KPI names.

**No test pauses this repository.** Every project is a temporary git
repository: W1-02's fixture project (its tickets, its ``.gitignore`` with
``.gov-runtime/``, the guard hook installed). The code under test is this
worktree's ``src/``, and every command is run with the temporary project both
as ``--root`` and as the working directory (one test moves the working
directory to another temporary directory). ``conftest.py`` checks before and
after every test that this worktree has no freeze flag.

**The caller's role** (decision package DP-3 in ``README.md``, recommended
option). The role is given twice, with the same value: ``--role <role>`` and
``GOV_ROLE=<role>`` in the command's environment. The owner's invocation is
the role ``owner``. Another answer changes ``pause`` below and nothing else.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

for _suite in ("W1-07", "W1-02"):
    _path = str(Path(__file__).resolve().parents[1] / _suite)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import w1_02_support as guard_support  # noqa: E402  the guard hook as a process, and the fixture project
import w1_07_support as cli_support  # noqa: E402  the ``gov`` console script, without an install

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
NOT_IMPLEMENTED = cli_support.NOT_IMPLEMENTED
MODULE_INVALID = "COMMAND_MODULE_INVALID"

FREEZE_FLAG_REL = ".gov-runtime/freeze"   # DEC-109; ``FREEZE_FLAG`` of ``src/gov/guard/decide.py``
RUNTIME_REL = ".gov-runtime"
TICKETS_REL = ".tickets"
CLAIMS_REL = ".tickets/.claims"           # DEC-292

# DP-3 (recommended option): the owner's invocation names the role ``owner``.
OWNER = "owner"
ORCHESTRATOR = guard_support.ORCHESTRATOR
ENGINEER = guard_support.ENGINEER
WORKER_ROLES = (guard_support.ENGINEER, guard_support.PRODUCT_SPEC, guard_support.TEST_DESIGNER,
                guard_support.AUDITOR, "research")
GUARD_ROLES = guard_support.KNOWN_ROLES

# The tickets of W1-02's fixture project, all in progress.
TICKET = guard_support.TICKET_ID            # an engineer ticket
OTHER_TICKET = guard_support.DOCS_TICKET_ID  # a second engineer ticket
UNKNOWN_TICKET = "DAEO-zz00"                # no such ticket file, and no commit names it

# A write each role may make when nothing is frozen: (ticket, repository-relative path). As in W1-02's freeze tests.
NORMAL_WRITE = {
    guard_support.ENGINEER: (TICKET, "src/gov/guard/decide.py"),
    guard_support.ORCHESTRATOR: (guard_support.ORCHESTRATOR_TICKET_ID, ".claude/settings.json"),
    guard_support.PRODUCT_SPEC: (guard_support.PRODUCT_SPEC_TICKET_ID, "docs/spec/feature.md"),
    guard_support.TEST_DESIGNER: (TICKET, f"tests/acceptance/{guard_support.TICKET_WBS_ID}/test_fixture.py"),
    guard_support.AUDITOR: (TICKET, f"{guard_support.SCRATCH_REL}/audit-note.txt"),
}

HOLDER = "engineer:w1-28-session-a"                      # DEC-292: by convention ``<role>:<session>``
OTHER_HOLDER = "independent-test-designer:w1-28-session-b"

NEW_DATE = "2026-10-04T12:00:00+00:00"   # after DEC-182's rule date: trailers are in the final block
OLD_DATE = "2026-10-01T12:00:00+00:00"   # before it: a check falls back to the message body

COMMAND_TIMEOUT_S = 60.0


# --------------------------------------------------------------------------
# The temporary project
# --------------------------------------------------------------------------

def git(project, *args, date=NEW_DATE, check=True):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(project),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W1-28 tests", "GIT_AUTHOR_EMAIL": "w1-28@example.invalid",
        "GIT_COMMITTER_NAME": "W1-28 tests", "GIT_COMMITTER_EMAIL": "w1-28@example.invalid",
        "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
    }
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    if check and done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {project}:\n{done.stderr}")
    return done.stdout


def make_project(directory):
    """W1-02's fixture project, with an identity of its own so that a command can commit in it."""
    project = guard_support.make_project(directory)
    assert REPO_ROOT not in (project, *project.parents), f"{project} is inside this repository"
    git(project, "config", "user.name", "W1-28 fixture")
    git(project, "config", "user.email", "w1-28-fixture@example.invalid")
    git(project, "config", "commit.gpgsign", "false")
    return project


def flag(project):
    return Path(project) / FREEZE_FLAG_REL


def is_paused(project):
    return os.path.lexists(flag(project))


def ticket_path(project, ticket=TICKET):
    return Path(project) / TICKETS_REL / f"{ticket}.md"


def ticket_file(project, ticket=TICKET):
    return ticket_path(project, ticket).read_text(encoding="utf-8")


def head(project):
    return git(project, "rev-parse", "HEAD").strip()


def porcelain(project):
    return git(project, "status", "--porcelain")


def committed(project, rel, rev="HEAD"):
    """The content of ``rel`` in ``rev``; None when the commit has no such file."""
    done = subprocess.run(["git", "-C", str(project), "show", f"{rev}:{rel}"], capture_output=True, text=True)
    return done.stdout if done.returncode == 0 else None


def tree_outside_tickets(project, rev="HEAD"):
    """``git ls-tree -r`` of ``rev`` without ``.tickets/``, where a record may be written (DP-6)."""
    lines = git(project, "ls-tree", "-r", rev).splitlines()
    return [line for line in lines if not line.split("\t", 1)[1].startswith(TICKETS_REL + "/")]


def reflog(project):
    """The reflog subjects of HEAD, newest first."""
    return git(project, "reflog", "--format=%gs").splitlines()


def commit(project, files, subject, ticket, role=ENGINEER, date=NEW_DATE, in_body=False):
    """One commit that names ``ticket``; its hash.

    ``files`` maps a path to its new text. The ``Task:`` and ``Role:`` trailers
    are in the final trailer block (DEC-182). With ``in_body`` they are in the
    message body instead, followed by a closing paragraph, as some commits made
    before 2026-10-03 hold them.
    """
    for rel, text in files.items():
        path = Path(project) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        git(project, "add", "--", rel)
    if in_body:
        message = ["-m", subject, "-m", f"Task: {ticket}\nRole: {role}", "-m", "Closing words, not a trailer block."]
    else:
        message = ["-m", subject, "--trailer", f"Task: {ticket}", "--trailer", f"Role: {role}"]
    git(project, "commit", "-q", *message, date=date)
    return head(project)


FEATURE_REL, EXTRA_REL, CHANGED_REL, OTHER_REL = "src/app/feature.py", "src/app/extra.py", "src/app/main.py", \
    "docs/notes.md"
OTHER_TEXT = "notes\na line of the other ticket\n"


def ticket_history(project, date=NEW_DATE, in_body=False):
    """Two commits of ``TICKET`` around one of ``OTHER_TICKET``; ``(first, other, second)`` hashes.

    The ticket's second commit changes the line its first commit wrote, so the
    two revert cleanly only newest first.
    """
    first = commit(project, {FEATURE_REL: "STEP = 1\n", CHANGED_REL: "VALUE = 2\n"}, "feature, step 1", TICKET,
                   date=date, in_body=in_body)
    other = commit(project, {OTHER_REL: OTHER_TEXT}, "a note of the other ticket", OTHER_TICKET, date=date,
                   in_body=in_body)
    second = commit(project, {FEATURE_REL: "STEP = 2\n", EXTRA_REL: "EXTRA = 1\n"}, "feature, step 2", TICKET,
                    date=date, in_body=in_body)
    return first, other, second


def assert_rolled_back(project, what="after the rollback"):
    """HEAD holds none of ``TICKET``'s changes, and all of the other ticket's."""
    assert committed(project, FEATURE_REL) is None, f"{what}, HEAD still has {FEATURE_REL}"
    assert committed(project, EXTRA_REL) is None, f"{what}, HEAD still has {EXTRA_REL}"
    assert committed(project, CHANGED_REL) == "VALUE = 1\n", \
        f"{what}, {CHANGED_REL} is not back to its content before the ticket: {committed(project, CHANGED_REL)!r}"
    assert committed(project, OTHER_REL) == OTHER_TEXT, \
        f"{what}, the other ticket's commit did not survive: {committed(project, OTHER_REL)!r}"
    for rel in (FEATURE_REL, EXTRA_REL):
        assert not (Path(project) / rel).exists(), f"{what}, the working tree still has {rel}"


# --------------------------------------------------------------------------
# Running the command line
# --------------------------------------------------------------------------

def _environment(sandbox, role=None):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "GIT_CONFIG_NOSYSTEM": "1",
        "PYTHONPATH": str(SRC),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
    }
    if role is not None:
        env[guard_support.ROLE_ENV] = role
    return env


def gov(project, sandbox, *args, role=None, cwd=None):
    """Run ``gov <args> --root <project>`` with this worktree's code; the working directory is the project."""
    project = Path(project)
    assert REPO_ROOT not in (project, *project.parents), f"refusing to run gov in {project}: it is this repository"
    launcher = cli_support.write_launcher(REPO_ROOT, sandbox)
    argv = [*args, "--root", str(project)]
    started = time.perf_counter()
    try:
        done = subprocess.run([sys.executable, str(launcher), *argv], cwd=str(cwd or project),
                              env=_environment(sandbox, role), capture_output=True, text=True,
                              timeout=COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(argv)} did not end within {COMMAND_TIMEOUT_S:.0f} s") from None
    return cli_support.Run(tuple(argv), done.returncode, done.stdout, done.stderr, time.perf_counter() - started)


def pause(project, sandbox, *args, role=OWNER, cwd=None):
    """``gov pause <args> --json`` on the temporary project, as ``role`` (DP-3: ``--role`` and ``GOV_ROLE`` agree)."""
    named = ("--role", role) if role is not None else ()
    return gov(project, sandbox, "pause", *args, "--json", *named, role=role, cwd=cwd)


def succeeded(run, interface):
    """The run succeeded with the API-0002 envelope; returns its ``result``."""
    envelope = cli_support.assert_envelope(run, interface, command="pause")
    assert envelope["ok"] is True and run.returncode == 0, f"gov pause did not succeed\n{run.describe()}"
    return envelope["result"]


def refused(run, interface):
    """The run was refused by the command itself: a GovError envelope, not a usage error; returns the error."""
    envelope = cli_support.assert_envelope(run, interface, command="pause")
    assert envelope["ok"] is False, f"gov pause was expected to refuse\n{run.describe()}"
    code = envelope["error"]["code"]
    assert code not in (NOT_IMPLEMENTED, MODULE_INVALID), f"gov pause is not built: {code}\n{run.describe()}"
    assert run.returncode not in (0, 2), f"a refusal is a governance error, not exit code {run.returncode}\n" \
                                         f"{run.describe()}"
    return envelope["error"]


def text_of(value):
    """Everything a result says, as one string, to look for an id whatever the shape."""
    return json.dumps(value, sort_keys=True)


# --------------------------------------------------------------------------
# gov.tasks (W1-09), each call in a new process
# --------------------------------------------------------------------------

_TASKS = ("import json, pathlib, sys\n"
          "from gov import tasks\n"
          "print(json.dumps(getattr(tasks, sys.argv[1])(pathlib.Path(sys.argv[2]), *sys.argv[3:])))\n")


def tasks(project, sandbox, function, *args):
    """``gov.tasks.<function>(project, *args)``; its value. A GovError fails the test."""
    done = subprocess.run([sys.executable, "-c", _TASKS, function, str(project), *args], capture_output=True,
                          text=True, env=_environment(sandbox), cwd=str(sandbox.elsewhere), timeout=COMMAND_TIMEOUT_S)
    assert done.returncode == 0, f"gov.tasks.{function}{args!r} failed:\n{done.stderr}"
    return json.loads(done.stdout)


def locks(project):
    """The names of the claim locks in ``.tickets/.claims/``."""
    folder = Path(project) / CLAIMS_REL
    return sorted(path.name for path in folder.iterdir()) if folder.is_dir() else []


# --------------------------------------------------------------------------
# The guard (W1-02)
# --------------------------------------------------------------------------

def guard_write(project, sandbox, role, tool_name="Write"):
    """The guard's decision on the write ``role`` may make when nothing is frozen."""
    ticket, rel = NORMAL_WRITE[role]
    tool_input = guard_support.edit_tool_input(tool_name, Path(project) / rel)
    return guard_support.run_hook(project, tool_name, tool_input, sandbox, role=role, ticket=ticket)


def guard_bash(project, sandbox, role, command):
    ticket, _ = NORMAL_WRITE[role]
    return guard_support.run_hook(project, "Bash", guard_support.bash_tool_input(command), sandbox, role=role,
                                  ticket=ticket)


assert_allowed = guard_support.assert_allowed
assert_denied = guard_support.assert_denied
