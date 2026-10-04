"""Support code for the W1-47 acceptance tests (standard library and PyYAML only).

W1-47 hardens the guard: the sandbox escape hatch, failed commands, the path of
the qualification oracle, the settings ask rules and four ``uv`` forms. The
tests drive the kernel hooks the way the harness does (one JSON object on
standard input, the decision on standard output) and read the committed settings
files. Nothing here imports ``src/gov/guard/``.

Three kinds of project are used, all in temporary directories:

- the **fixture project** of W1-03 (``w1_03_support.make_project``): a small
  committed repository with both kernel hooks installed at
  ``governance/kernel/hooks/``, the place Copier puts them, and the fixture
  tickets in progress;
- the **wired copy** (``make_wired_copy``): the guard's own files of this
  repository (``src/gov``, the kernel hooks, ``.claude/settings.json``) copied
  into a new repository, so that the commands the committed settings register
  can be run as the harness runs them, with no ``PYTHONPATH`` from the test;
- a throw-away root for the static checks' own self-tests.

**The qualification oracle.** Its path is held in
``governance/project/held-out.yaml``. No file of this suite carries that path,
and no function here opens, lists or stats anything under it. The value is read
at run time for two purposes only: to check the committed ``Read`` deny rule
against it, and to check that no file of the ticket repeats it. It is never put
in a failure message, a test id or a file: every failure about it is raised with
``pytest.fail(..., pytrace=False)`` and a fixed text.

The guard's behaviour is tested against a **stand-in**: a directory created in
the temporary area, set through the same configuration. ``configure_stand_in``
takes the committed ``held-out.yaml``, replaces its one path value with the
stand-in's path and writes the result into the temporary project. So the test
needs to know nothing about the file's keys, and the temporary project never
names the oracle.
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
SETTINGS_REL = ".claude/settings.json"
TEMPLATE_KERNEL_REL = "template/governance/kernel"
TEMPLATE_SETTINGS_GLOB = "settings*"
CONTAINMENT_HOOK_STEM = "posttooluse"

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
# The ticket's ``allowed_paths``, without the two files that may carry the oracle path.
IMPLEMENTATION_GLOBS = (
    "src/gov/guard/**/*",
    "template/governance/kernel/hooks/pretooluse*",
    "template/governance/kernel/hooks/posttooluse*",
    "template/governance/kernel/settings*",
    "tests/unit/guard/**/*",
    "tests/unit/install/**/*",
)


# --------------------------------------------------------------------------
# The oracle configuration. The value is never shown.
# --------------------------------------------------------------------------

def _absolute_path_scalars(node):
    """Every string value of a parsed YAML document that is an absolute path. Keys are not values."""
    if isinstance(node, str):
        return [node] if node.startswith("/") else []
    if isinstance(node, dict):
        return [found for value in node.values() for found in _absolute_path_scalars(value)]
    if isinstance(node, (list, tuple)):
        return [found for value in node for found in _absolute_path_scalars(value)]
    return []


def paths_in_config_text(text):
    """The absolute paths a ``held-out.yaml`` text holds; ``None`` when the text is not YAML."""
    try:
        return _absolute_path_scalars(yaml.safe_load(text))
    except yaml.YAMLError:
        return None


@dataclass(frozen=True)
class Configured:
    """The committed configuration. ``repr`` hides both fields, so no report can print the value."""
    text: str = ""
    value: str = ""

    def __repr__(self):
        return "Configured(<hidden>)"


def load_configured(root=REPO_ROOT):
    """Read ``governance/project/held-out.yaml`` of ``root``. Opens that one file and nothing else."""
    path = Path(root) / CONFIG_REL
    if not path.is_file():
        pytest.fail(
            f"{CONFIG_REL} does not exist: the oracle path is not configured, so there is nothing the committed "
            "Read deny rule and the guard's rule could be built from",
            pytrace=False,
        )
    text = path.read_text(encoding="utf-8")
    found = paths_in_config_text(text)
    if found is None:
        pytest.fail(f"{CONFIG_REL} is not valid YAML", pytrace=False)
    if len(found) != 1:
        pytest.fail(
            f"{CONFIG_REL} holds {len(found)} values that are absolute paths; it must hold exactly one, "
            "the oracle path (the value itself is not shown)",
            pytrace=False,
        )
    value = found[0]
    if value.rstrip("/") == "" or "\n" in value:
        pytest.fail(f"the path value of {CONFIG_REL} is the file-system root or spans lines", pytrace=False)
    return Configured(text, value)


def configure_stand_in(project, stand_in, configured):
    """Write a ``held-out.yaml`` into ``project`` that names ``stand_in`` where the committed one names the oracle."""
    stand_in = str(stand_in)
    text = configured.text.replace(configured.value, stand_in)
    if paths_in_config_text(text) != [stand_in] or (configured.value in text and configured.value not in stand_in):
        pytest.fail(
            f"the path value of {CONFIG_REL} could not be replaced by a stand-in: the value must appear in the "
            "file as it is parsed, once, with no escaping",
            pytrace=False,
        )
    target = Path(project) / CONFIG_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


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


def oracle_read_rules(settings, configured):
    """The ``Read`` deny rules built from the configured path.

    The absolute form of a path in a permission rule is ``//<path>``: the rule
    is ``Read(/`` + the configured value + ``)``, where the value may be
    followed by ``/`` or ``/**`` to cover what is under the directory.
    """
    value = configured.value.rstrip("/")
    wanted = {f"/{value}{suffix}" for suffix in ("", "/", "/**")}
    found = []
    for rule in permission_rules(settings, "deny"):
        tool, spec = split_rule(rule)
        if tool == "Read" and spec is not None and spec.strip() in wanted:
            found.append(rule)
    return found


def template_settings_files(root=REPO_ROOT):
    """Every regular file matching ``template/governance/kernel/settings*``."""
    directory = Path(root) / TEMPLATE_KERNEL_REL
    if not directory.is_dir():
        return []
    return sorted(path for path in directory.glob(TEMPLATE_SETTINGS_GLOB) if path.is_file())


def load_template_settings(root=REPO_ROOT):
    """The kernel template's settings file, parsed. There must be exactly one."""
    files = template_settings_files(root)
    where = f"{TEMPLATE_KERNEL_REL}/{TEMPLATE_SETTINGS_GLOB}"
    if not files:
        pytest.fail(f"no file matches {where}: the kernel template has no settings file", pytrace=False)
    if len(files) != 1:
        pytest.fail(f"{where} matches {', '.join(p.name for p in files)}; one settings file is expected",
                    pytrace=False)
    return load_json_object(files[0], f"{TEMPLATE_KERNEL_REL}/{files[0].name}")


def containment_commands(settings, event):
    """The commands registered for ``event`` on Bash that run the containment hook."""
    return [command for command in live_support.hook_commands(settings, event, "Bash")
            if CONTAINMENT_HOOK_STEM in command]


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


def files_naming(paths, needle):
    """The files among ``paths`` whose text holds ``needle``."""
    return [path for path in paths if needle in path.read_text(encoding="utf-8", errors="replace")]
