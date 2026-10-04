"""Support code for the W1-47 acceptance tests (standard library and PyYAML only).

W1-47 hardens the guard: the sandbox escape hatch, failed commands, the path of
the qualification oracle, the settings ask rules and four ``uv`` forms. The
tests drive the kernel hooks the way the harness does (one JSON object on
standard input, the decision on standard output) and read the committed settings
files. Nothing here imports ``src/gov/guard/``.

Two kinds of project are used, both in temporary directories:

- the **fixture project** of W1-03 (``w1_03_support.make_project``): a small
  committed repository with both kernel hooks installed at
  ``governance/kernel/hooks/``, the place Copier puts them, and the fixture
  tickets in progress. It is also the "project that has the kernel installed"
  in which the commands of the kernel template's settings file are run
  (DEC-217);
- the **wired copy** (``make_wired_copy``): the guard's own files of this
  repository (``src/gov``, the kernel hooks, ``.claude/settings.json``) copied
  into a new repository, so that the commands the committed settings register
  can be run as the harness runs them, with no ``PYTHONPATH`` from the test.

**The held-out path.** The paths are held in
``governance/project/held-out.yaml`` under the key ``held_out_paths``, a list of
absolute paths (DEC-218). No file of this suite carries a value of that list,
and no function here opens, lists or stats anything under one. The committed
file is read at run time by the static checks only (``load_configured``): the
committed ``Read`` deny rule is built from every path of the list, and no file
of the ticket repeats one. A value is never put in a failure message, a test id
or a file: every failure about it is raised with ``pytest.fail(...,
pytrace=False)`` and a fixed text, and the object that holds the values hides
them in its ``repr``.

The guard's behaviour is tested against a **stand-in**: a directory created in
the temporary area. ``configure_stand_in`` writes a ``held-out.yaml`` of its own
into the temporary project, with ``held_out_paths`` holding the stand-in's path.
The committed file plays no part in it, and the temporary project never names
the real path: the wired copy leaves the committed absolute ``Read`` rules out.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

_TESTS = Path(__file__).resolve().parent.parent
for _name in ("W1-03", "W1-05"):
    _directory = str(_TESTS / _name)
    if _directory not in sys.path:
        sys.path.insert(0, _directory)

import w1_03_support as check_support   # noqa: E402  the fixture project, a whole Bash call, findings
import w1_05_support as live_support    # noqa: E402  the registered commands of a settings file

REPO_ROOT = Path(__file__).resolve().parents[3]
SUITE_DIR = Path(__file__).resolve().parent
CONFIG_REL = "governance/project/held-out.yaml"
CONFIG_KEY = "held_out_paths"
SETTINGS_REL = ".claude/settings.json"
TEMPLATE_KERNEL_REL = "template/governance/kernel"
TEMPLATE_SETTINGS_REL = f"{TEMPLATE_KERNEL_REL}/settings.json"
CONTAINMENT_HOOK_STEM = "posttooluse"
GUARD_HOOK_STEM = "pretooluse"
PROJECT_DIR_VARIABLE = "CLAUDE_PROJECT_DIR"

ENGINEER = check_support.ENGINEER
ORCHESTRATOR = check_support.ORCHESTRATOR
PRODUCT_SPEC = check_support.PRODUCT_SPEC
TEST_DESIGNER = check_support.TEST_DESIGNER
AUDITOR = check_support.AUDITOR

# The ticket each role works on in the fixture project. The test designer works on the engineer's.
TICKET_OF = {
    ORCHESTRATOR: check_support.ORCHESTRATOR_TICKET_ID,
    ENGINEER: check_support.TICKET_ID,
    PRODUCT_SPEC: check_support.PRODUCT_SPEC_TICKET_ID,
    TEST_DESIGNER: check_support.TICKET_ID,
    AUDITOR: check_support.AUDITOR_TICKET_ID,
}

# Who makes a call: name -> (GOV_ROLE, GOV_TICKET, subagent type). "Every role" in the KPIs is the five
# known roles; a session that declares no role is started in the repository root as well.
EVERY_ROLE = {role: (role, ticket, None) for role, ticket in TICKET_OF.items()}
NO_ROLE = {"no-role": (None, None, None)}
SUBAGENTS = {
    "engineer-subagent-of-the-orchestrator": (ORCHESTRATOR, TICKET_OF[ORCHESTRATOR], ENGINEER),
    "untyped-subagent-of-the-orchestrator": (ORCHESTRATOR, TICKET_OF[ORCHESTRATOR], "general-purpose"),
}
EVERY_SESSION = {**EVERY_ROLE, **NO_ROLE}
EVERY_ACTOR = {**EVERY_ROLE, **NO_ROLE, **SUBAGENTS}

# Every permission mode of the harness, as in W1-04's tests.
PERMISSION_MODES = ("default", "acceptEdits", "auto", "dontAsk", "bypassPermissions", "plan")

HOOK_TIMEOUT_S = 30.0
SESSION_ID = "w1-47-acceptance-session"
SUBAGENT_ID = "agent-w1-47-acceptance"

# The eleven Bash ask rules DEC-172 withdraws, as the prefix each one matches.
WITHDRAWN_ASK_PREFIXES = (
    "pip", "pip3", "python -m pip", "python3 -m pip", "uv", "npm install", "cargo install",
    "apt", "apt-get", "curl", "wget",
)
# The deny rules the committed settings carried when the ticket was written; all of them stay.
KEPT_DENY_RULES = (
    "Read(./docs/source/**)",
    "Edit(./docs/source/**)",
    "Edit(**/.env*)",
    "Edit(**/*.pem)",
    "Edit(**/*.key)",
    "Edit(config/secrets*)",
    "Bash(sudo:*)",
)
# The ticket's ``allowed_paths``, without the two files that may carry a held-out path.
IMPLEMENTATION_GLOBS = (
    "src/gov/guard/**/*",
    "template/governance/kernel/hooks/pretooluse*",
    "template/governance/kernel/hooks/posttooluse*",
    "template/governance/kernel/settings*",
    "tests/unit/guard/**/*",
    "tests/unit/install/**/*",
)


# --------------------------------------------------------------------------
# The held-out configuration. A value of the committed file is never shown.
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Configured:
    """The paths of the committed configuration. ``repr`` hides them, so no report can print a value."""
    values: tuple = ()

    def __repr__(self):
        return "Configured(<hidden>)"


def load_configured(root=REPO_ROOT):
    """Read ``held_out_paths`` of ``governance/project/held-out.yaml``. Opens that one file and nothing else.

    For the static checks only. Every failure is a fixed text; no value, and
    nothing derived from one, is shown.
    """
    path = Path(root) / CONFIG_REL
    if not path.is_file():
        pytest.fail(f"{CONFIG_REL} does not exist", pytrace=False)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        pytest.fail(f"{CONFIG_REL} is not valid YAML", pytrace=False)
    paths = data.get(CONFIG_KEY) if isinstance(data, dict) else None
    if not isinstance(paths, list) or not paths:
        pytest.fail(f"{CONFIG_REL} does not hold a non-empty list under the key {CONFIG_KEY} (DEC-218)",
                    pytrace=False)
    for value in paths:
        if not isinstance(value, str) or not value.startswith("/") or value.rstrip("/") == "" or "\n" in value:
            pytest.fail(
                f"an entry of {CONFIG_KEY} in {CONFIG_REL} is not an absolute path on one line, or is the "
                "file-system root (the entry is not shown)",
                pytrace=False,
            )
    return Configured(tuple(value.rstrip("/") for value in paths))


def write_config(project, text):
    """Write ``text`` as the ``held-out.yaml`` of a temporary project."""
    target = Path(project) / CONFIG_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def stand_in_config_text(*stand_ins):
    """A ``held-out.yaml`` of the stated shape (DEC-218) whose list holds made-up paths."""
    return yaml.safe_dump({CONFIG_KEY: [str(path) for path in stand_ins]}, default_flow_style=False)


def configure_stand_in(project, *stand_ins):
    """Give the temporary ``project`` a ``held-out.yaml`` of its own that names the stand-in directories.

    The committed file of this repository is not read: the key is known
    (DEC-218), so the file is built here from made-up paths alone.
    """
    assert stand_ins, "a stand-in path is needed"
    return write_config(project, stand_in_config_text(*stand_ins))


def make_stand_in(directory):
    """A directory that plays the oracle: two files and a notebook, never the real thing."""
    directory = Path(directory)
    (directory / "cases").mkdir(parents=True, exist_ok=True)
    (directory / "answers.md").write_text("stand-in answers\n", encoding="utf-8")
    (directory / "cases" / "test_hidden.py").write_text("def test_hidden():\n    assert True\n", encoding="utf-8")
    (directory / "notes.ipynb").write_text('{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}\n',
                                           encoding="utf-8")
    return directory


# --------------------------------------------------------------------------
# Settings files
# --------------------------------------------------------------------------

def load_json_object(path, name):
    path = Path(path)
    assert path.is_file(), f"{name} does not exist"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise AssertionError(f"{name} is not valid JSON: {exc}") from None
    assert isinstance(data, dict), f"{name} does not hold a JSON object"
    return data


def load_settings(root=REPO_ROOT):
    """``.claude/settings.json`` of ``root``."""
    return load_json_object(Path(root) / SETTINGS_REL, SETTINGS_REL)


def permission_rules(settings, kind):
    """The rules of ``permissions.<kind>`` (``allow``, ``ask`` or ``deny``) that are strings."""
    permissions = settings.get("permissions")
    rules = permissions.get(kind) if isinstance(permissions, dict) else None
    return [rule for rule in rules if isinstance(rule, str)] if isinstance(rules, list) else []


def split_rule(rule):
    """``("Bash", "pip:*")`` for ``Bash(pip:*)``; ``("Bash", None)`` for ``Bash``; ``(None, None)`` otherwise."""
    match = re.fullmatch(r"\s*([A-Za-z_]+)\s*(?:\((.*)\))?\s*", rule)
    return (match.group(1), match.group(2)) if match else (None, None)


def bash_rule_prefix(rule):
    """The command prefix a Bash rule matches, without its wildcard; ``None`` for a rule of another tool."""
    tool, spec = split_rule(rule)
    if tool != "Bash":
        return None
    if spec is None:
        return ""
    spec = spec.strip()
    for wildcard in (":*", " *", "*"):
        if spec.endswith(wildcard):
            spec = spec[: -len(wildcard)]
            break
    return " ".join(spec.split())


def is_withdrawn_install_rule(rule):
    """A Bash rule on one of the eleven prefixes DEC-172 names, or on a longer command that begins with one."""
    prefix = bash_rule_prefix(rule)
    if prefix is None:
        return False
    return any(prefix == withdrawn or prefix.startswith(withdrawn + " ") for withdrawn in WITHDRAWN_ASK_PREFIXES)


def held_out_read_rules(settings, value):
    """The ``Read`` deny rules built from one configured path.

    The absolute form of a path in a permission rule is ``//<path>``: the rule
    is ``Read(/`` + the configured value + ``)``, where the value may be
    followed by ``/`` or ``/**`` to cover what is under the directory.
    """
    value = value.rstrip("/")
    wanted = {f"/{value}{suffix}" for suffix in ("", "/", "/**")}
    found = []
    for rule in permission_rules(settings, "deny"):
        tool, spec = split_rule(rule)
        if tool == "Read" and spec is not None and spec.strip() in wanted:
            found.append(rule)
    return found


def load_template_settings(root=REPO_ROOT):
    """``template/governance/kernel/settings.json``, parsed (DEC-217)."""
    path = Path(root) / TEMPLATE_SETTINGS_REL
    if not path.is_file():
        pytest.fail(f"{TEMPLATE_SETTINGS_REL} does not exist: the kernel template has no settings file",
                    pytrace=False)
    return load_json_object(path, TEMPLATE_SETTINGS_REL)


def containment_commands(settings, event):
    """The commands registered for ``event`` on Bash that run the containment hook."""
    return [command for command in live_support.hook_commands(settings, event, "Bash")
            if CONTAINMENT_HOOK_STEM in command]


def every_hook_command(settings):
    """Every command a settings file registers, whatever the event and the matcher."""
    hooks = settings.get("hooks")
    commands = []
    for entries in hooks.values() if isinstance(hooks, dict) else []:
        for entry in entries if isinstance(entries, list) else []:
            for hook in entry.get("hooks", []) if isinstance(entry, dict) else []:
                if isinstance(hook, dict) and isinstance(hook.get("command"), str):
                    commands.append(hook["command"])
    return commands


# --------------------------------------------------------------------------
# The commands of a settings file, run in a project that has the kernel installed
# --------------------------------------------------------------------------

def installed_environment(project, sandbox, role=None, ticket=None):
    """The environment of a hook command in a product repository.

    The kernel hooks are at ``governance/kernel/hooks/`` of the project and
    the ``gov`` package is installed. Nothing is installed by a test, so the
    package is put on Python's path instead; a command that sets its own
    ``PYTHONPATH`` (this repository's ``src``) finds no ``gov`` there.
    """
    env = live_support.command_environment(project, sandbox, role, ticket)
    env["PYTHONPATH"] = str(REPO_ROOT / check_support.GOV_PACKAGE_PARENT_REL)
    return env


def run_registered(project, settings, sandbox, event, tool_name, tool_input, role=None, ticket=None,
                   tool_use_id="toolu_w1_47_template", permission_mode="default"):
    """Run the commands ``settings`` registers for ``event`` and ``tool_name`` through the shell, one by one."""
    stdin = json.dumps(live_support.hook_input(project, sandbox, event, tool_name, tool_input,
                                               permission_mode=permission_mode, tool_use_id=tool_use_id))
    results = []
    for command in live_support.hook_commands(settings, event, tool_name):
        try:
            proc = subprocess.run(["sh", "-c", command], input=stdin, capture_output=True, text=True,
                                  cwd=str(project), env=installed_environment(project, sandbox, role, ticket),
                                  timeout=HOOK_TIMEOUT_S, check=False)
            results.append(GuardResult(_decision(proc.returncode, proc.stdout), proc.returncode, proc.stdout,
                                       proc.stderr))
        except subprocess.TimeoutExpired:
            results.append(GuardResult("timeout", None, "", "timed out"))
    return results


def combined_decision(results):
    """What the harness makes of several PreToolUse results: the strictest one; ``none`` when no command ran."""
    decisions = [result.decision for result in results]
    for outcome in ("deny", "timeout", "error", "ask"):
        if outcome in decisions:
            return outcome
    return "allow" if decisions else "none"


def describe_all(results):
    return "; ".join(result.describe() for result in results) or "no command is registered"


def report_text(results):
    """The text the post-command results put in front of the agent."""
    texts = [check_support.agent_text(result.returncode, result.stdout, result.stderr) for result in results]
    return "\n".join(text for text in texts if text)


# --------------------------------------------------------------------------
# One PreToolUse run of the hook installed in a fixture project
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class GuardResult:
    decision: str          # deny | ask | allow | error | timeout
    returncode: int | None
    stdout: str
    stderr: str

    def describe(self):
        return (f"decision={self.decision} exit={self.returncode} "
                f"stdout={self.stdout.strip()[:300]!r} stderr={self.stderr.strip()[:300]!r}")


def _decision(returncode, stdout):
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


def _argv(entry):
    if entry.suffix == ".py":
        return [sys.executable, str(entry)]
    if entry.suffix in (".sh", ".bash"):
        return ["bash", str(entry)]
    return [str(entry)]


_CALLS = iter(range(1, 1_000_000))


def guard_payload(project, sandbox, tool_name, tool_input, subagent=None, permission_mode="default"):
    """The PreToolUse stdin object of the harness."""
    data = {
        "session_id": SESSION_ID,
        "transcript_path": str(sandbox.home / ".claude" / "projects" / "fixture" / f"{SESSION_ID}.jsonl"),
        "cwd": str(project),
        "permission_mode": permission_mode,
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": f"toolu_w1_47_{next(_CALLS):05d}",
    }
    if subagent is not None:
        data["agent_id"] = SUBAGENT_ID
        data["agent_type"] = subagent
    return data


def run_guard(project, sandbox, tool_name, tool_input, role=None, ticket=None, subagent=None,
              permission_mode="default", environment=None):
    """Run the PreToolUse hook installed in the fixture project once and classify its decision."""
    project = Path(project)
    entry = project / check_support.PRODUCT_HOOK_DIR_REL / check_support.guard_entry().name
    env = check_support.hook_environment(project, sandbox, role, ticket)
    env.update(environment or {})
    stdin = json.dumps(guard_payload(project, sandbox, tool_name, tool_input, subagent, permission_mode))
    try:
        proc = subprocess.run(_argv(entry), input=stdin, capture_output=True, text=True, cwd=str(project),
                              env=env, timeout=HOOK_TIMEOUT_S, check=False)
    except subprocess.TimeoutExpired as exc:
        return GuardResult("timeout", None, str(exc.stdout or ""), str(exc.stderr or ""))
    return GuardResult(_decision(proc.returncode, proc.stdout), proc.returncode, proc.stdout, proc.stderr)


def bash_input(command, **extra):
    """The input of a Bash call. ``extra`` adds fields, ``dangerouslyDisableSandbox`` for one."""
    return {"command": command, "description": "W1-47 acceptance attempt", **extra}


def write_input(tool_name, path):
    return live_support.write_input(tool_name, path)


def assert_denied_by_rule(result, what):
    """The hook answered with a deny decision of its own: exit code 0 and ``permissionDecision: deny``.

    Exit code 2 also stops a call, but it is the hook's report of its own
    failure (DEC-110), not a rule. A rule this ticket adds must decide.
    """
    assert result.decision == "deny" and result.returncode == 0, f"{what} was not denied by a rule: {result.describe()}"


def assert_allowed(result, what):
    assert result.decision == "allow", f"{what} was not allowed: {result.describe()}"


def assert_stopped(result, what):
    """The call does not go through: a deny decision, or exit code 2, the hook's report of its own failure."""
    assert result.decision == "deny", f"{what} was let through: {result.describe()}"


# --------------------------------------------------------------------------
# The wired copy: this repository's guard files and committed settings
# --------------------------------------------------------------------------

WIRED_PATHSPECS = ("src/gov", "template/governance/kernel/hooks", SETTINGS_REL)
WIRED_FILES = {
    "README.md": "# Wired copy\n",
    ".gitignore": ".gov-runtime/\n__pycache__/\n",
    "tests/acceptance/W1-90/test_fixture.py": "VALUE = 1\n",
}


def make_wired_copy(directory, root=REPO_ROOT):
    """Copy the guard's own files and the committed settings into a new committed repository.

    Only ``src/gov``, the kernel hooks and ``.claude/settings.json`` are copied,
    file by file from git's listing of those three places. Nothing else of the
    working tree is read. The copy gets W1-05's fixture ticket, ``DAEO-zz90``.

    The copy of the settings file leaves out the ``Read`` deny rules with an
    absolute path (``Read(//...)``), so no temporary project carries a held-out
    path. Nothing else of the file changes; the hooks are run from the
    committed file itself.
    """
    import shutil

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    listing = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--",
         *WIRED_PATHSPECS],
        capture_output=True, text=True, check=True,
    ).stdout
    for rel in sorted(set(item for item in listing.split("\0") if item)):
        source = Path(root) / rel
        if source.is_file() and not source.is_symlink():
            target = directory / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for rel, text in WIRED_FILES.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    copied = load_settings(directory)
    permissions = copied.get("permissions")
    if isinstance(permissions, dict) and isinstance(permissions.get("deny"), list):
        permissions["deny"] = [rule for rule in permissions["deny"]
                               if not (isinstance(rule, str) and rule.replace(" ", "").startswith("Read(//"))]
        (directory / SETTINGS_REL).write_text(json.dumps(copied, indent=2) + "\n", encoding="utf-8")
    ticket = directory / ".tickets" / f"{live_support.FIXTURE_TICKET_ID}.md"
    ticket.parent.mkdir(parents=True, exist_ok=True)
    ticket.write_text(live_support.fixture_ticket_text(), encoding="utf-8")
    live_support.git(directory, "init", "-q", "-b", "main")
    live_support.git(directory, "add", "-A")
    live_support.git(directory, "commit", "-q", "-m", "wired copy")
    return directory


# --------------------------------------------------------------------------
# Files of the ticket, for the check that none repeats the oracle path
# --------------------------------------------------------------------------

def files_matching(globs, root=REPO_ROOT):
    """Regular files under ``root`` matching any of ``globs``; byte-code caches are left out."""
    found = set()
    for pattern in globs:
        for path in Path(root).glob(pattern):
            if path.is_file() and not path.is_symlink() and "__pycache__" not in path.parts:
                found.add(path)
    return sorted(found)


def files_naming(paths, needles):
    """The files among ``paths`` whose text holds one of ``needles``."""
    found = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(needle in text for needle in needles):
            found.append(path)
    return found
