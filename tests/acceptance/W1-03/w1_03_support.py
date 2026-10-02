"""Support code for the W1-03 acceptance tests (standard library only).

The containment check is driven the way the harness drives it around one Bash
call (DEC-124):

1. the kernel's PreToolUse hook runs with the call on stdin; this is where the
   check takes its before-snapshot (DEC-126);
2. the command runs for real in a throw-away project;
3. the PostToolUse hook runs with the same call on stdin, and the test reads its
   exit code, stdout and stderr, the working tree, and
   ``.gov-runtime/findings.jsonl`` (DEC-122).

- The hooks are the files matching ``template/governance/kernel/hooks/pretooluse*``
  and ``posttooluse*``. They are copied into the project at
  ``governance/kernel/hooks/``, the place Copier puts them in a product
  repository (ADR-0002 section 5).
- ``src/`` of this repository is put on ``PYTHONPATH``; that stands in for the
  installed ``gov`` package.
- The project is named three ways, as the harness does: the working directory
  of the process, ``cwd`` in the stdin object, and ``CLAUDE_PROJECT_DIR``.
- The environment is built from scratch. ``HOME`` is an empty temporary
  directory and ``TMPDIR`` a directory next to the project. A role and an active
  ticket are declared through ``GOV_ROLE`` and ``GOV_TICKET`` (DEC-107); a call
  made inside a subagent carries ``agent_id`` and ``agent_type`` (DEC-117).
- Both hooks of one call get the same ``session_id`` and ``tool_use_id``; every
  call has a ``tool_use_id`` of its own.

**The call the hooks see.** A fixture command is saved as a script outside the
project, and the call is ``bash <script>``. The guard has no way to judge such a
call, so it lets it through and the before-snapshot exists, whatever the guard
parses today or later. The check judges a call by its effect inside the
repository (DEC-123), so it needs nothing more. ``literal_call`` passes a
command to the hooks word for word instead.

What reaches the agent from a PostToolUse or PostToolUseFailure hook (harness
2.1.284, hook reference):

- exit code 2: stderr is shown to the model;
- exit code 0 with a JSON object on stdout: ``decision: "block"`` shows
  ``reason`` to the model, and ``hookSpecificOutput.additionalContext`` is added
  to its context;
- exit code 0 with anything else: nothing reaches the model;
- any other exit code: a hook error, shown to the user only.
"""

from __future__ import annotations

import itertools
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_DIR_REL = "template/governance/kernel/hooks"
HOOK_GLOB = "posttooluse*"
GUARD_GLOB = "pretooluse*"
PRODUCT_HOOK_DIR_REL = "governance/kernel/hooks"
GOV_PACKAGE_PARENT_REL = "src"

ROLE_ENV = "GOV_ROLE"
TICKET_ENV = "GOV_TICKET"
SCRATCH_REL = ".gov-runtime/scratch"
FINDINGS_REL = ".gov-runtime/findings.jsonl"
ACCEPTANCE_REL = "tests/acceptance"

ENGINEER = "engineer"
ORCHESTRATOR = "orchestrator"
PRODUCT_SPEC = "product-spec"
TEST_DESIGNER = "independent-test-designer"
AUDITOR = "independent-auditor"
KNOWN_ROLES = (ORCHESTRATOR, PRODUCT_SPEC, TEST_DESIGNER, ENGINEER, AUDITOR)

HOOK_TIMEOUT_S = 30.0
BASH_TIMEOUT_S = 30.0
SESSION_ID = "w1-03-acceptance-session"

# The fields of a containment finding (DEC-122) and the two values of ``action``.
FINDING_FIELDS = ("time", "session_id", "agent_type", "role", "ticket", "tool", "command", "paths", "action",
                  "reason")
REVERTED = "reverted"
FLAGGED = "flagged"
ACTIONS = (REVERTED, FLAGGED)

# The engineer ticket most tests work on.
TICKET_ID = "DAEO-zz90"
TICKET_WBS_ID = "W1-90"
TICKET_ALLOWED_PATHS = (
    "src/gov/guard/**",
    "tests/unit/guard/**",
    "template/governance/kernel/hooks/pretooluse*",
    "pyproject.toml",
)
ORCHESTRATOR_TICKET_ID = "DAEO-zz91"
PRODUCT_SPEC_TICKET_ID = "DAEO-zz92"
ACCEPTANCE_NAMING_TICKET_ID = "DAEO-zz93"   # an engineer ticket that wrongly names tests/acceptance/**
AUDITOR_TICKET_ID = "DAEO-zz94"
DOCS_TICKET_ID = "DAEO-zz95"
NEW_DIRECTORY_TICKET_ID = "DAEO-zz96"       # an engineer ticket for a directory that does not exist yet

ACCEPTANCE_FILE = f"{ACCEPTANCE_REL}/{TICKET_WBS_ID}/test_fixture.py"
SOURCE_FILE = "src/gov/guard/decide.py"


class HookMissing(AssertionError):
    """A kernel hook is not in the repository, or its entry point is unclear."""


# --------------------------------------------------------------------------
# The hooks
# --------------------------------------------------------------------------

def _is_executable(path):
    return bool(path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


def hook_files(root=REPO_ROOT, pattern=HOOK_GLOB):
    """Every regular file matching ``template/governance/kernel/hooks/<pattern>``."""
    hook_dir = Path(root) / HOOK_DIR_REL
    if not hook_dir.is_dir():
        return []
    return sorted(p for p in hook_dir.glob(pattern) if p.is_file())


def _entry(root, pattern, name):
    files = hook_files(root, pattern)
    if not files:
        raise HookMissing(f"no file matches {HOOK_DIR_REL}/{pattern}: the {name} does not exist")
    if len(files) == 1:
        return files[0]
    executables = [p for p in files if _is_executable(p)]
    if len(executables) == 1:
        return executables[0]
    names = ", ".join(p.name for p in files)
    raise HookMissing(
        f"{HOOK_DIR_REL}/{pattern} matches {names}; exactly one of them must be executable "
        f"so the entry point is clear ({len(executables)} are)"
    )


def hook_entry(root=REPO_ROOT):
    """The PostToolUse file the harness is to run: the only match, or the only executable match."""
    return _entry(root, HOOK_GLOB, "post-command containment hook")


def guard_entry(root=REPO_ROOT):
    """The PreToolUse file the harness is to run (W1-02's guard; W1-03 adds the before-snapshot, DEC-126)."""
    return _entry(root, GUARD_GLOB, "PreToolUse hook")


def _argv(entry):
    if _is_executable(entry):
        return [str(entry)]
    if entry.suffix == ".py":
        return [sys.executable, str(entry)]
    if entry.suffix in (".sh", ".bash"):
        return ["bash", str(entry)]
    raise HookMissing(
        f"{entry.name} is not executable and is neither a .py nor a .sh file; cannot tell how to run it"
    )


# --------------------------------------------------------------------------
# A throw-away project
# --------------------------------------------------------------------------

_GIT_IDENTITY = (
    "-c", "user.name=W1-03 acceptance", "-c", "user.email=w1-03@example.invalid",
    "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
)


def git(project, *args):
    proc = subprocess.run(["git", "-C", str(project), *_GIT_IDENTITY, *args],
                          capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in the test project: {proc.stderr.strip()}")
    return proc.stdout


def ticket_text(ticket_id=TICKET_ID, wbs_id=TICKET_WBS_ID, status="in_progress", role=ENGINEER,
                allowed_paths=TICKET_ALLOWED_PATHS):
    """A ticket file with the frontmatter shape of the Wave 1 tickets."""
    paths = "".join(f"- {p}\n" for p in allowed_paths)
    return (
        "---\n"
        f"id: {ticket_id}\n"
        f"status: {status}\n"
        "deps: []\n"
        "links: []\n"
        "created: 2026-09-30T22:49:58Z\n"
        "type: task\n"
        "priority: 1\n"
        f"assignee: {role}\n"
        f"external-ref: {wbs_id}\n"
        "tags: [wave-1, implementation, full]\n"
        f"wbs_id: {wbs_id}\n"
        "title: Containment fixture ticket\n"
        "class: implementation\n"
        f"role: {role}\n"
        "depends_on: []\n"
        "allowed_paths:\n"
        f"{paths}"
        "kpis:\n"
        "  success:\n"
        "  - The fixture component exists\n"
        "  failure:\n"
        "  - The fixture component is missing\n"
        "profile: FULL\n"
        "acceptance_tests:\n"
        f"  path: tests/acceptance/{wbs_id}/\n"
        "---\n"
        f"# {wbs_id} Containment fixture ticket\n"
    )


def default_tickets():
    """The tickets of the fixture project, all in progress."""
    return {
        f"{TICKET_ID}.md": ticket_text(),
        f"{ORCHESTRATOR_TICKET_ID}.md": ticket_text(
            ticket_id=ORCHESTRATOR_TICKET_ID, wbs_id="W1-91", role=ORCHESTRATOR,
            allowed_paths=(".claude/settings.json", "governance/project/bootstrap.md"),
        ),
        f"{PRODUCT_SPEC_TICKET_ID}.md": ticket_text(
            ticket_id=PRODUCT_SPEC_TICKET_ID, wbs_id="W1-92", role=PRODUCT_SPEC,
            allowed_paths=("template/governance/kernel/roles/**", "docs/spec/**"),
        ),
        f"{ACCEPTANCE_NAMING_TICKET_ID}.md": ticket_text(
            ticket_id=ACCEPTANCE_NAMING_TICKET_ID, wbs_id="W1-93", role=ENGINEER,
            allowed_paths=("src/app/**", "tests/acceptance/**"),
        ),
        f"{AUDITOR_TICKET_ID}.md": ticket_text(
            ticket_id=AUDITOR_TICKET_ID, wbs_id="W1-94", role=AUDITOR,
            allowed_paths=("docs/audit/**",),
        ),
        f"{DOCS_TICKET_ID}.md": ticket_text(
            ticket_id=DOCS_TICKET_ID, wbs_id="W1-95", role=ENGINEER,
            allowed_paths=("docs/**",),
        ),
        f"{NEW_DIRECTORY_TICKET_ID}.md": ticket_text(
            ticket_id=NEW_DIRECTORY_TICKET_ID, wbs_id="W1-96", role=ENGINEER,
            allowed_paths=("tools/guard/**",),
        ),
    }


PROJECT_FILES = {
    "README.md": "# Fixture project\n",
    ".gitignore": ".gov-runtime/\n__pycache__/\n",
    "pyproject.toml": "[project]\nname = \"fixture\"\n",
    "docs/notes.md": "notes\n",
    "docs/spec/feature.md": "VALUE = 1\n",
    "src/gov/__init__.py": "VALUE = 1\n",
    "src/gov/guard/decide.py": "VALUE = 1\n",
    "src/gov/guardian/other.py": "VALUE = 1\n",
    "src/app/main.py": "VALUE = 1\n",
    "tests/unit/guard/test_decide.py": "VALUE = 1\n",
    "tests/unit/other/test_other.py": "VALUE = 1\n",
    ACCEPTANCE_FILE: "VALUE = 1\n",
    f"{ACCEPTANCE_REL}/{TICKET_WBS_ID}/README.md": "# Fixture acceptance tests\n",
    "template/governance/kernel/hooks/pretooluse.py": "VALUE = 1\n",
    "template/governance/kernel/roles/engineer.md": "VALUE = 1\n",
    "governance/project/bootstrap.md": "VALUE = 1\n",
    ".claude/settings.json": "{}\n",
}

# Committed symbolic links: (link, target relative to the link's directory).
PROJECT_SYMLINKS = (
    ("src/gov/guard/acceptance_link", "../../../tests/acceptance"),
)


def make_project(directory):
    """Create a committed git project with both kernel hooks installed."""
    project = Path(directory)
    project.mkdir(parents=True, exist_ok=True)
    files = dict(PROJECT_FILES)
    for name, text in default_tickets().items():
        files[f".tickets/{name}"] = text
    for rel, text in files.items():
        path = project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for link, target in PROJECT_SYMLINKS:
        (project / link).symlink_to(target, target_is_directory=True)
    hook_dir = project / PRODUCT_HOOK_DIR_REL
    hook_dir.mkdir(parents=True, exist_ok=True)
    for pattern in (GUARD_GLOB, HOOK_GLOB):
        for source in hook_files(pattern=pattern):
            shutil.copy2(source, hook_dir / source.name)
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "fixture project")
    return project


def commit_all(project, message):
    """Commit everything in the working tree: one more revision in the fixture's history."""
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", message)


def porcelain(project, *pathspec):
    """``git status --porcelain`` of the project, optionally for some paths."""
    args = ["status", "--porcelain"]
    if pathspec:
        args += ["--", *pathspec]
    return git(project, *args)


def porcelain_all(project, *pathspec):
    """``git status --porcelain`` with every untracked file listed by itself."""
    args = ["status", "--porcelain", "--untracked-files=all"]
    if pathspec:
        args += ["--", *pathspec]
    return git(project, *args)


def head_text(project, relpath):
    """Content of ``relpath`` at HEAD."""
    return git(project, "show", f"HEAD:{relpath}")


def read(project, relpath):
    """Text of a file in the working tree; ``None`` when it does not exist."""
    path = Path(project) / relpath
    return path.read_text(encoding="utf-8") if path.is_file() else None


# --------------------------------------------------------------------------
# One Bash call between its two hooks
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    """Directories outside the project that the processes see."""
    home: Path
    pycache: Path
    tmpdir: Path      # what tempfile.gettempdir() returns inside the hook
    elsewhere: Path   # outside the project, outside the scratch set


def make_sandbox(base):
    base = Path(base)
    box = Sandbox(base / "home", base / "pycache", base / "systmp", base / "elsewhere")
    for directory in (box.home, box.pycache, box.tmpdir, box.elsewhere):
        directory.mkdir(parents=True, exist_ok=True)
    return box


@dataclass(frozen=True)
class Call:
    """One Bash call of the agent, as both hooks are told about it."""
    command: str        # ``tool_input.command``, and what is run
    tool_use_id: str


_CALL_NUMBERS = itertools.count(1)


def script_call(sandbox, command):
    """Save ``command`` as a script outside the project; the call is ``bash <script>``."""
    number = next(_CALL_NUMBERS)
    directory = sandbox.elsewhere / "calls"
    directory.mkdir(exist_ok=True)
    script = directory / f"call-{number:04d}.sh"
    script.write_text(command + "\n", encoding="utf-8")
    return Call(f"bash {shlex.quote(str(script))}", f"toolu_w1_03_{number:04d}")


def literal_call(command):
    """A call whose command reaches the hooks word for word."""
    return Call(command, f"toolu_w1_03_{next(_CALL_NUMBERS):04d}")


def _base_environment(project, sandbox):
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "TMPDIR": str(sandbox.tmpdir),
        "CLAUDE_PROJECT_DIR": str(project),
    }


def run_bash(project, command, sandbox):
    """Run ``command`` for real in the project, as the agent's Bash tool would."""
    env = _base_environment(project, sandbox)
    env.update({
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "W1-03 acceptance", "GIT_AUTHOR_EMAIL": "w1-03@example.invalid",
        "GIT_COMMITTER_NAME": "W1-03 acceptance", "GIT_COMMITTER_EMAIL": "w1-03@example.invalid",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    return subprocess.run(["bash", "-c", command], cwd=str(project), env=env, capture_output=True,
                          text=True, timeout=BASH_TIMEOUT_S, check=False)


def hook_environment(project, sandbox, role=None, ticket=None):
    """A minimal environment: no variable of the calling session is inherited."""
    env = _base_environment(project, sandbox)
    env["PYTHONPATH"] = str(REPO_ROOT / GOV_PACKAGE_PARENT_REL)
    env["PYTHONPYCACHEPREFIX"] = str(sandbox.pycache)
    if role is not None:
        env[ROLE_ENV] = role
    if ticket is not None:
        env[TICKET_ENV] = ticket
    return env


def payload(project, call, sandbox, event, bash=None, subagent=None):
    """The stdin object of the harness for one of the three events around a Bash call.

    ``PreToolUse`` before the call; ``PostToolUse`` after it; ``PostToolUseFailure``
    instead, when the call failed, timed out or was interrupted.
    """
    data = {
        "session_id": SESSION_ID,
        "transcript_path": str(sandbox.home / ".claude" / "projects" / "fixture" / f"{SESSION_ID}.jsonl"),
        "cwd": str(project),
        "permission_mode": "default",
        "hook_event_name": event,
        "tool_name": "Bash",
        "tool_input": {"command": call.command, "description": "W1-03 acceptance call"},
        "tool_use_id": call.tool_use_id,
    }
    stdout = bash.stdout if bash is not None else ""
    stderr = bash.stderr if bash is not None else ""
    if event == "PostToolUseFailure":
        code = bash.returncode if bash is not None else 1
        data.update({"error": f"Exit code {code}\n{stderr}".strip(), "error_type": "tool_error",
                     "is_interrupt": False, "is_timeout": False})
    elif event == "PostToolUse":
        data["tool_response"] = {"stdout": stdout, "stderr": stderr, "interrupted": False, "isImage": False}
    if subagent is not None:
        data["agent_id"] = "agent-w1-03-acceptance"
        data["agent_type"] = subagent
    return data


def _run(entry, stdin, project, sandbox, role, ticket):
    started = time.perf_counter()
    try:
        proc = subprocess.run(_argv(entry), input=stdin, capture_output=True, text=True, cwd=str(project),
                              env=hook_environment(project, sandbox, role, ticket),
                              timeout=HOOK_TIMEOUT_S, check=False)
    except subprocess.TimeoutExpired as exc:
        return None, str(exc.stdout or ""), str(exc.stderr or ""), time.perf_counter() - started
    return proc.returncode, proc.stdout, proc.stderr, time.perf_counter() - started


@dataclass(frozen=True)
class GuardResult:
    decision: str          # allow | ask | deny | error | timeout
    returncode: int | None
    stdout: str
    stderr: str

    def describe(self):
        return (
            f"decision={self.decision} exit={self.returncode} "
            f"stdout={self.stdout.strip()[:300]!r} stderr={self.stderr.strip()[:300]!r}"
        )


def _guard_decision(returncode, stdout):
    if returncode is None:
        return "timeout"
    if returncode == 2:
        return "deny"
    if returncode != 0:
        return "error"
    try:
        data = json.loads(stdout.strip() or "null")
    except ValueError:
        return "allow"
    specific = data.get("hookSpecificOutput") if isinstance(data, dict) else None
    decision = specific.get("permissionDecision") if isinstance(specific, dict) else None
    return decision if decision in ("deny", "ask") else "allow"


def run_guard(project, call, sandbox, role=None, ticket=None, subagent=None):
    """Run the installed PreToolUse hook once, as the harness does before a Bash call."""
    project = Path(project)
    entry = project / PRODUCT_HOOK_DIR_REL / guard_entry().name
    stdin = json.dumps(payload(project, call, sandbox, "PreToolUse", subagent=subagent))
    returncode, stdout, stderr, _ = _run(entry, stdin, project, sandbox, role, ticket)
    return GuardResult(_guard_decision(returncode, stdout), returncode, stdout, stderr)


def finding_lines(project):
    """The non-empty lines of ``.gov-runtime/findings.jsonl``; empty when the file is absent."""
    path = Path(project) / FINDINGS_REL
    if not path.is_file():
        return []
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


@dataclass(frozen=True)
class HookResult:
    outcome: str           # report | silent | error | timeout
    report: str            # the text that reaches the agent; empty when nothing does
    returncode: int | None
    stdout: str
    stderr: str
    seconds: float
    project: Path
    command: str           # the command both hooks were told about
    new_lines: tuple       # the lines added to findings.jsonl since the call began

    def describe(self):
        return (
            f"outcome={self.outcome} exit={self.returncode} "
            f"stdout={self.stdout.strip()[:400]!r} stderr={self.stderr.strip()[:400]!r}"
        )


def agent_text(returncode, stdout, stderr):
    """The text a PostToolUse hook's result puts in front of the agent."""
    if returncode == 2:
        return stderr.strip()
    if returncode != 0:
        return ""
    try:
        data = json.loads(stdout.strip() or "null")
    except ValueError:
        return ""
    if not isinstance(data, dict):
        return ""
    parts = []
    if data.get("decision") == "block" and isinstance(data.get("reason"), str):
        parts.append(data["reason"])
    specific = data.get("hookSpecificOutput")
    if isinstance(specific, dict) and isinstance(specific.get("additionalContext"), str):
        parts.append(specific["additionalContext"])
    return "\n".join(part for part in parts if part.strip()).strip()


def classify(returncode, stdout, stderr):
    if returncode is None:
        return "timeout", ""
    if returncode not in (0, 2):
        return "error", ""
    text = agent_text(returncode, stdout, stderr)
    return ("report" if text else "silent"), text


def run_check(project, call, sandbox, role=None, ticket=None, subagent=None, bash=None, failed=False,
              seen=None):
    """Run the installed containment hook once, as the harness does after a Bash call.

    ``seen`` is the number of lines the findings file held when the call began;
    left out, the lines added by this run alone are returned.
    """
    project = Path(project)
    entry = project / PRODUCT_HOOK_DIR_REL / hook_entry().name
    event = "PostToolUseFailure" if failed else "PostToolUse"
    stdin = json.dumps(payload(project, call, sandbox, event, bash=bash, subagent=subagent))
    if seen is None:
        seen = len(finding_lines(project))
    returncode, stdout, stderr, seconds = _run(entry, stdin, project, sandbox, role, ticket)
    outcome, report = classify(returncode, stdout, stderr)
    return HookResult(outcome, report, returncode, stdout, stderr, seconds, project, call.command,
                      tuple(finding_lines(project)[seen:]))


# --------------------------------------------------------------------------
# Findings (DEC-122)
# --------------------------------------------------------------------------

def new_findings(result, what):
    """The findings this call added, each checked against the record DEC-122 defines."""
    findings = []
    for line in result.new_lines:
        try:
            data = json.loads(line)
        except ValueError:
            raise AssertionError(f"{what}: a line of {FINDINGS_REL} is not JSON: {line[:300]!r}") from None
        assert isinstance(data, dict), f"{what}: a line of {FINDINGS_REL} is not a JSON object: {line[:300]!r}"
        missing = [name for name in FINDING_FIELDS if name not in data]
        assert not missing, f"{what}: the finding lacks {', '.join(missing)}: {line[:400]!r}"
        paths = data["paths"]
        assert isinstance(paths, list) and paths and all(isinstance(p, str) and p.strip() for p in paths), (
            f"{what}: `paths` of the finding is not a list of path names: {paths!r}"
        )
        assert data["action"] in ACTIONS, (
            f"{what}: `action` of the finding is {data['action']!r}, not one of {ACTIONS}"
        )
        assert isinstance(data["reason"], str) and data["reason"].strip(), (
            f"{what}: `reason` of the finding is empty: {data['reason']!r}"
        )
        assert data["time"], f"{what}: `time` of the finding is empty: {data['time']!r}"
        assert data["tool"] == "Bash", f"{what}: `tool` of the finding is {data['tool']!r}, not 'Bash'"
        assert data["session_id"] == SESSION_ID, (
            f"{what}: `session_id` of the finding is {data['session_id']!r}, not the session's {SESSION_ID!r}"
        )
        assert data["command"] == result.command, (
            f"{what}: `command` of the finding is {data['command']!r}, not the call's {result.command!r}"
        )
        findings.append(data)
    return findings


def finding_paths(result, finding):
    """``paths`` of a finding, relative to the project, without a trailing slash."""
    root = str(result.project)
    names = []
    for entry in finding["paths"]:
        if entry.startswith(root + "/"):
            entry = entry[len(root) + 1:]
        names.append(entry.rstrip("/"))
    return names


def _covers(entry, path):
    """The recorded entry is ``path`` itself or a directory above it."""
    return entry == path or path.startswith(entry + "/")


def _related(entry, name):
    name = name.rstrip("/")
    return _covers(entry, name) or entry.startswith(name + "/")


# --------------------------------------------------------------------------
# Assertions
# --------------------------------------------------------------------------

def assert_let_through(guard, call):
    """The PreToolUse hook let the fixture call through, so the Bash call would follow."""
    assert guard.decision == "allow", (
        f"the PreToolUse hook did not let the fixture call `{call.command}` through, "
        f"so no Bash call would follow: {guard.describe()}"
    )


def assert_reported(result, *names, what):
    """The check told the agent, and the report names every one of ``names``."""
    assert result.outcome == "report", f"{what}: nothing was reported to the agent: {result.describe()}"
    for name in names:
        assert name in result.report, (
            f"{what}: the report to the agent does not name {name!r}: {result.report[:600]!r}"
        )


def assert_recorded(result, *names, what, action=None):
    """This call added a finding for every one of ``names``; with ``action``, each has that action.

    A name may be a file or a directory. A finding answers for it when one of
    its ``paths`` is that name, a directory above it, or a path below it.
    """
    findings = new_findings(result, what)
    assert findings, f"{what}: no containment finding was added to {FINDINGS_REL}"
    for name in names:
        matching = [f for f in findings if any(_related(e, name) for e in finding_paths(result, f))]
        assert matching, (
            f"{what}: no finding names {name!r}; recorded paths: {[f['paths'] for f in findings]}"
        )
        if action is not None:
            assert all(f["action"] == action for f in matching), (
                f"{what}: the finding for {name!r} has action {[f['action'] for f in matching]}, not {action!r}"
            )
    return findings


def assert_not_recorded(result, *paths, what):
    """No finding added by this call answers for any of ``paths``."""
    for finding in new_findings(result, what):
        for path in paths:
            assert not any(_related(e, path) for e in finding_paths(result, finding)), (
                f"{what}: a finding names {path!r}, which this call did not change out of scope: "
                f"{finding['paths']}"
            )


def assert_caught(result, *names, what, action=None):
    """Reported to the agent and recorded as a containment finding (KPI success 1, failure 1)."""
    assert_reported(result, *names, what=what)
    return assert_recorded(result, *names, what=what, action=action)


def assert_silent(result, what):
    """The check found nothing: exit code 0, no text for the agent, no finding."""
    assert result.outcome == "silent", f"{what}: the check did not stay silent: {result.describe()}"
    assert result.returncode == 0, f"{what}: the check did not exit with code 0: {result.describe()}"
    assert not result.new_lines, (
        f"{what}: the check found nothing and still added to {FINDINGS_REL}: {result.new_lines}"
    )


def assert_changed(project, *names, command):
    """Guard against an empty test: the Bash command really changed the named paths."""
    status = porcelain_all(project)
    for name in names:
        assert name in status, (
            f"the fixture command `{command}` did not change {name}; git status --porcelain is:\n{status}"
        )
