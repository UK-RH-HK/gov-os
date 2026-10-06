"""Support code for the W1-05 acceptance tests (standard library only).

W1-05 switches this repository over to its own guard. The tests look at what
the switch-over leaves in the repository: the hook wiring in
``.claude/settings.json``, the record in ``governance/project/bootstrap.md`` and
the role subagent definitions under ``.claude/agents/``.

"Live" is tested by behaviour. A copy of the working tree is made in a temporary
directory, and the commands that ``.claude/settings.json`` registers are run
there the way the harness runs them: through the shell, in the project
directory, with ``CLAUDE_PROJECT_DIR`` set and the hook's JSON object on stdin.
The repository itself is never written, and no hook is ever run against it.

- The environment of a hook command is built from scratch: ``PATH``, an empty
  temporary ``HOME``, ``TMPDIR``, locale and ``CLAUDE_PROJECT_DIR``, plus
  ``GOV_ROLE`` and ``GOV_TICKET`` when the test declares them. There is no
  ``PYTHONPATH``: the wiring must find the ``gov`` package by itself.
- Several commands may be registered for one event. Their results combine as in
  the harness: one ``deny`` denies, otherwise one ``ask`` asks, otherwise the
  call is allowed. A command that ends with an exit code other than 0 or 2 is a
  hook error; the harness would let the call through, so the tests count it as
  neither allowed nor denied.
- A ``permissions.deny`` rule of the settings file denies before any hook is
  asked, so it is part of the decision.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SETTINGS_REL = ".claude/settings.json"
BOOTSTRAP_REL = "governance/project/bootstrap.md"
HELD_OUT_REL = "governance/project/held-out.yaml"   # DEC-385: no fixture copies it into a temporary project
AGENTS_REL = ".claude/agents"
ACCEPTANCE_REL = "tests/acceptance"
SCRATCH_REL = ".gov-runtime/scratch"

ENGINEER = "engineer"
ORCHESTRATOR = "orchestrator"
PRODUCT_SPEC = "product-spec"
TEST_DESIGNER = "independent-test-designer"
AUDITOR = "independent-auditor"
ROLES = (ORCHESTRATOR, ENGINEER, PRODUCT_SPEC, TEST_DESIGNER, AUDITOR)

WRITE_TOOLS = ("Edit", "Write", "NotebookEdit", "Bash")
FILE_TOOLS = ("Edit", "Write", "NotebookEdit")
READ_ONLY_TOOLS = ("Read", "Grep", "Glob")
# "Every tool" cannot be listed, so the tests ask for these names: the write and
# read-only tools, other tools of the harness, a tool of an MCP server, and a
# name that no list written today can hold.
OTHER_TOOLS = ("Agent", "Task", "TodoWrite", "WebFetch", "WebSearch", "mcp__github__create_issue",
               "ToolAddedAfterTheSwitchOver")
EVERY_TOOL = WRITE_TOOLS + READ_ONLY_TOOLS + OTHER_TOOLS
DEPENDENCIES = ("W1-02", "W1-03", "W1-04")

COMMAND_TIMEOUT_S = 30.0
SESSION_ID = "w1-05-acceptance-session"
TOOL_USE_ID = "toolu_w1_05_acceptance"
SUBAGENT_ID = "agent-w1-05-acceptance"

# A ticket added to the copy only, so that a role has something to work on.
FIXTURE_TICKET_ID = "DAEO-zz90"
FIXTURE_TICKET_PATHS = ("src/gov/guard/**", "tests/unit/guard/**")
FIXTURE_SOURCE = "src/gov/guard/decide.py"


# --------------------------------------------------------------------------
# The settings file
# --------------------------------------------------------------------------

def load_settings(root=REPO_ROOT):
    path = Path(root) / SETTINGS_REL
    assert path.is_file(), f"{SETTINGS_REL} does not exist"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise AssertionError(f"{SETTINGS_REL} is not valid JSON: {exc}") from None
    assert isinstance(data, dict), f"{SETTINGS_REL} does not hold a JSON object"
    return data


def matcher_matches(matcher, tool_name):
    """Whether a hook matcher covers ``tool_name``, on the strict reading.

    No matcher, an empty one and ``*`` cover every tool. Anything else must
    match the whole tool name, as an exact name or as a regular expression, so
    ``Edit|Write`` covers Edit and Write and ``Edit`` does not cover NotebookEdit.
    """
    if matcher is None or matcher in ("", "*"):
        return True
    if not isinstance(matcher, str):
        return False
    try:
        return re.fullmatch(matcher, tool_name) is not None
    except re.error:
        return matcher == tool_name


def hook_commands(settings, event, tool_name):
    """The shell commands registered for ``event`` that the harness runs for ``tool_name``."""
    hooks = settings.get("hooks")
    entries = hooks.get(event) if isinstance(hooks, dict) else None
    commands = []
    for entry in entries if isinstance(entries, list) else []:
        if not isinstance(entry, dict) or not matcher_matches(entry.get("matcher"), tool_name):
            continue
        for hook in entry.get("hooks") if isinstance(entry.get("hooks"), list) else []:
            if isinstance(hook, dict) and hook.get("type", "command") == "command" \
                    and isinstance(hook.get("command"), str) and hook["command"].strip():
                commands.append(hook["command"])
    return commands


def is_switched_over(settings):
    """The guard is wired before every write tool and the containment check after Bash."""
    return (all(hook_commands(settings, "PreToolUse", tool) for tool in WRITE_TOOLS)
            and bool(hook_commands(settings, "PostToolUse", "Bash")))


def is_wired_for_every_tool(settings):
    """Switched over, and a PreToolUse command runs for every tool, not for the write tools alone (DEC-142, DEC-144)."""
    return is_switched_over(settings) and all(hook_commands(settings, "PreToolUse", tool) for tool in EVERY_TOOL)


# --------------------------------------------------------------------------
# permissions.deny, as far as these tests need it
# --------------------------------------------------------------------------

def _glob_regex(pattern):
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return "".join(out)


def _split_rule(rule):
    match = re.fullmatch(r"\s*([A-Za-z]+)\s*(?:\((.*)\))?\s*", rule) if isinstance(rule, str) else None
    return (match.group(1), match.group(2)) if match else (None, None)


def _command_parts(command):
    return [part.strip() for part in re.split(r"&&|\|\||;|\||\n", command) if part.strip()]


def denied_by_settings(settings, tool_name, tool_input, project):
    """The ``permissions.deny`` rule that denies the call, or ``None``."""
    permissions = settings.get("permissions")
    rules = permissions.get("deny") if isinstance(permissions, dict) else None
    for rule in rules if isinstance(rules, list) else []:
        tool, spec = _split_rule(rule)
        if tool is None:
            continue
        if tool_name == "Bash":
            if tool != "Bash":
                continue
            if spec is None:
                return rule
            for part in _command_parts(tool_input.get("command", "")):
                if spec.endswith(":*"):
                    prefix = spec[:-2]
                    if part == prefix or part.startswith(prefix + " "):
                        return rule
                elif "*" in spec:
                    if re.fullmatch(".*".join(re.escape(piece) for piece in spec.split("*")), part):
                        return rule
                elif part == spec:
                    return rule
            continue
        covers = {"Edit": FILE_TOOLS, "Write": ("Write",), "NotebookEdit": ("NotebookEdit",)}.get(tool, ())
        if tool_name not in covers:
            continue
        if spec is None:
            return rule
        raw = tool_input.get("notebook_path" if tool_name == "NotebookEdit" else "file_path", "")
        try:
            rel = Path(raw).resolve().relative_to(Path(project).resolve()).as_posix()
        except ValueError:
            continue
        if spec.startswith("//") or spec.startswith("~"):
            continue
        pattern = spec[2:] if spec.startswith("./") else spec.lstrip("/")
        if re.fullmatch(_glob_regex(pattern), rel):
            return rule
    return None


# --------------------------------------------------------------------------
# A copy of the working tree
# --------------------------------------------------------------------------

def git(project, *args, check=True):
    proc = subprocess.run(
        ["git", "-C", str(project), "-c", "user.name=W1-05 acceptance",
         "-c", "user.email=w1-05@example.invalid", "-c", "commit.gpgsign=false",
         "-c", "core.hooksPath=/dev/null", *args],
        capture_output=True, text=True, check=False,
    )
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def fixture_ticket_text():
    paths = "".join(f"- {p}\n" for p in FIXTURE_TICKET_PATHS)
    return (
        "---\n"
        f"id: {FIXTURE_TICKET_ID}\n"
        "status: in_progress\n"
        "deps: []\n"
        "links: []\n"
        "created: 2026-09-30T22:49:58Z\n"
        "type: task\n"
        "priority: 1\n"
        "assignee: engineer\n"
        "external-ref: W1-90\n"
        "tags: [wave-1, implementation, full]\n"
        "wbs_id: W1-90\n"
        "title: Switch-over fixture ticket\n"
        "class: implementation\n"
        "role: engineer\n"
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
        "  path: tests/acceptance/W1-90/\n"
        "---\n"
        "# W1-90 Switch-over fixture ticket\n"
    )


def strip_held_out_rules(project):
    """Leave the ``Read`` deny rules with an absolute path out of the copied settings file (owner decision, DEC-399).

    As W1-46's and W1-47's fixtures do it: no temporary project carries a
    held-out path. Nothing else of the file changes, and no rule is shown.
    """
    path = Path(project) / SETTINGS_REL
    if not path.is_file() or path.is_symlink():
        return
    copied = json.loads(path.read_text(encoding="utf-8"))
    permissions = copied.get("permissions") if isinstance(copied, dict) else None
    if isinstance(permissions, dict) and isinstance(permissions.get("deny"), list):
        permissions["deny"] = [rule for rule in permissions["deny"]
                               if not (isinstance(rule, str) and rule.replace(" ", "").startswith("Read(//"))]
        path.write_text(json.dumps(copied, indent=2) + "\n", encoding="utf-8")


def copy_working_tree(destination, root=REPO_ROOT):
    """Copy the repository's working tree (tracked files and untracked, unignored ones) and commit it.

    The copy gets one extra ticket, ``DAEO-zz90``: an engineer ticket in progress.
    Its settings file is copied without the held-out deny rules (DEC-399).
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    listing = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True, check=True,
    ).stdout
    for rel in sorted(set(item for item in listing.split("\0") if item)):
        if rel == HELD_OUT_REL:   # DEC-385: left out by its path, never opened
            continue
        source = Path(root) / rel
        target = destination / rel
        if not (source.is_file() or source.is_symlink()):
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            target.symlink_to(os.readlink(source))
        else:
            shutil.copy2(source, target)
    strip_held_out_rules(destination)
    ticket = destination / ".tickets" / f"{FIXTURE_TICKET_ID}.md"
    ticket.parent.mkdir(parents=True, exist_ok=True)
    ticket.write_text(fixture_ticket_text(), encoding="utf-8")
    git(destination, "init", "-q", "-b", "main")
    git(destination, "add", "-A")
    git(destination, "commit", "-q", "-m", "copy of the working tree")
    return destination


# --------------------------------------------------------------------------
# Running the registered commands
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    home: Path
    tmpdir: Path


def make_sandbox(base):
    base = Path(base)
    box = Sandbox(base / "home", base / "systmp")
    for directory in (box.home, box.tmpdir):
        directory.mkdir(parents=True, exist_ok=True)
    return box


def command_environment(project, sandbox, role=None, ticket=None):
    env = {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "TMPDIR": str(sandbox.tmpdir),
        "CLAUDE_PROJECT_DIR": str(project),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if role is not None:
        env["GOV_ROLE"] = role
    if ticket is not None:
        env["GOV_TICKET"] = ticket
    return env


def hook_input(project, sandbox, event, tool_name, tool_input, subagent=None, permission_mode="default",
               agent_id=None, tool_use_id=TOOL_USE_ID):
    """The JSON object of one hook run.

    The actor is the session and, inside a subagent, its ``agent_id``. A call is
    its ``tool_use_id``: the PreToolUse and PostToolUse runs of one call share
    it, and two calls of one test that must be told apart get different ones.
    """
    data = {
        "session_id": SESSION_ID,
        "transcript_path": str(sandbox.home / ".claude" / "projects" / "gov-os" / f"{SESSION_ID}.jsonl"),
        "cwd": str(project),
        "permission_mode": permission_mode,
        "hook_event_name": event,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": tool_use_id,
    }
    if event == "PostToolUse":
        data["tool_response"] = {"stdout": "", "stderr": "", "interrupted": False, "isImage": False}
    if event == "PostToolUseFailure":
        data.update({"error": "Exit code 1", "error_type": "tool_error", "is_interrupt": False, "is_timeout": False})
    if subagent is not None:
        data["agent_id"] = agent_id or SUBAGENT_ID
        data["agent_type"] = subagent
    return data


@dataclass(frozen=True)
class CommandResult:
    command: str
    returncode: int | None
    stdout: str
    stderr: str

    def describe(self):
        return (f"`{self.command}` exit={self.returncode} stdout={self.stdout.strip()[:300]!r} "
                f"stderr={self.stderr.strip()[:300]!r}")


def run_commands(project, commands, stdin_object, sandbox, role=None, ticket=None):
    """Run each registered command once, through the shell, with the JSON object on stdin."""
    results = []
    for command in commands:
        try:
            proc = subprocess.run(["sh", "-c", command], input=json.dumps(stdin_object), capture_output=True,
                                  text=True, cwd=str(project),
                                  env=command_environment(project, sandbox, role, ticket),
                                  timeout=COMMAND_TIMEOUT_S, check=False)
            results.append(CommandResult(command, proc.returncode, proc.stdout, proc.stderr))
        except subprocess.TimeoutExpired:
            results.append(CommandResult(command, None, "", "timed out"))
    return results


def _permission_decision(result):
    if result.returncode == 2:
        return "deny"
    if result.returncode != 0:
        return "error"
    try:
        data = json.loads(result.stdout.strip() or "null")
    except ValueError:
        return "allow"
    specific = data.get("hookSpecificOutput") if isinstance(data, dict) else None
    decision = specific.get("permissionDecision") if isinstance(specific, dict) else None
    return decision if decision in ("deny", "ask") else "allow"


@dataclass(frozen=True)
class Decision:
    decision: str          # deny | ask | allow | error
    detail: str
    ran: int = 0           # how many registered PreToolUse commands the call reached

    def describe(self):
        return f"decision={self.decision} ({self.detail})"


def _combined(results):
    decisions = [_permission_decision(result) for result in results]
    detail = "; ".join(result.describe() for result in results) or "no PreToolUse hook is registered for the tool"
    for outcome in ("deny", "error", "ask"):
        if outcome in decisions:
            return Decision(outcome, detail, len(results))
    return Decision("allow", detail, len(results))


def pre_tool_use(project, settings, sandbox, tool_name, tool_input, role=None, ticket=None, subagent=None,
                 permission_mode="default", agent_id=None, tool_use_id=TOOL_USE_ID):
    """What the settings file and its PreToolUse hooks decide about one call."""
    rule = denied_by_settings(settings, tool_name, tool_input, project)
    if rule is not None:
        return Decision("deny", f"permissions.deny rule {rule}")
    commands = hook_commands(settings, "PreToolUse", tool_name)
    stdin_object = hook_input(project, sandbox, "PreToolUse", tool_name, tool_input, subagent, permission_mode,
                              agent_id, tool_use_id)
    return _combined(run_commands(project, commands, stdin_object, sandbox, role, ticket))


def timed_pre_tool_use(project, settings, sandbox, tool_name, tool_input, role=None, ticket=None, subagent=None):
    """One call's wait for its PreToolUse hooks, as the harness makes it. Returns ``(Decision, seconds)``.

    The harness starts every command registered for the tool at once and waits
    for all of them. The time is the wall-clock time from the first start to the
    last exit, with the shell that runs each command.
    """
    commands = hook_commands(settings, "PreToolUse", tool_name)
    payload = json.dumps(hook_input(project, sandbox, "PreToolUse", tool_name, tool_input, subagent))
    env = command_environment(project, sandbox, role, ticket)
    started = time.perf_counter()
    running = []
    for command in commands:
        proc = subprocess.Popen(["sh", "-c", command], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, cwd=str(project), env=env)
        try:
            proc.stdin.write(payload)
            proc.stdin.close()
        except OSError:
            pass   # the command ended without reading its input
        proc.stdin = None
        running.append(proc)
    results = []
    for command, proc in zip(commands, running):
        # communicate() returns when the command closes its output; wait(timeout=...) would poll, up to 50 ms late.
        try:
            stdout, stderr = proc.communicate(timeout=COMMAND_TIMEOUT_S)
            results.append(CommandResult(command, proc.returncode, stdout, stderr))
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            results.append(CommandResult(command, None, "", "timed out"))
    return _combined(results), time.perf_counter() - started


def p95(samples):
    """The 95th percentile by nearest rank, as in W1-02's tests."""
    ordered = sorted(samples)
    return ordered[max(0, -(-95 * len(ordered) // 100) - 1)]


def post_bash(project, settings, sandbox, command, role=None, ticket=None, subagent=None, event="PostToolUse",
              agent_id=None, tool_use_id=TOOL_USE_ID):
    """Run the commands registered after a Bash call. Returns the text that reaches the agent."""
    commands = hook_commands(settings, event, "Bash")
    stdin_object = hook_input(project, sandbox, event, "Bash",
                              {"command": command, "description": "W1-05 acceptance call"}, subagent,
                              agent_id=agent_id, tool_use_id=tool_use_id)
    results = run_commands(project, commands, stdin_object, sandbox, role, ticket)
    texts = []
    for result in results:
        if result.returncode == 2:
            texts.append(result.stderr.strip())
        elif result.returncode == 0:
            try:
                data = json.loads(result.stdout.strip() or "null")
            except ValueError:
                continue
            if isinstance(data, dict):
                if data.get("decision") == "block" and isinstance(data.get("reason"), str):
                    texts.append(data["reason"])
                specific = data.get("hookSpecificOutput")
                if isinstance(specific, dict) and isinstance(specific.get("additionalContext"), str):
                    texts.append(specific["additionalContext"])
    return "\n".join(text for text in texts if text), results


def run_bash(project, command, sandbox):
    """Run ``command`` for real in the copy, as an agent's Bash tool would."""
    env = command_environment(project, sandbox)
    env.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull})
    return subprocess.run(["bash", "-c", command], cwd=str(project), env=env, capture_output=True,
                          text=True, timeout=COMMAND_TIMEOUT_S, check=False)


def bash_call(project, settings, sandbox, command, role=None, ticket=None, subagent=None, event="PostToolUse",
              changed=(), agent_id=None, tool_use_id=TOOL_USE_ID):
    """One whole Bash call through the wiring: PreToolUse commands, the command for real, then ``event``.

    The containment check takes its before-snapshot in PreToolUse and acts only
    on what the call changed (DEC-124, DEC-126). With no PreToolUse run before
    it, the check cannot tell whose a change is, and it flags without restoring.

    ``command`` is saved as a script outside the copy and the call is
    ``bash <script>``: a call the guard has no way to judge, so it lets it
    through and the snapshot exists. ``changed`` names paths the command must
    have changed. Returns what ``post_bash`` returns.
    """
    directory = sandbox.home.parent / "calls"
    directory.mkdir(exist_ok=True)
    script = directory / f"call-{len(list(directory.iterdir())) + 1:04d}.sh"
    script.write_text(command + "\n", encoding="utf-8")
    call = f"bash {shlex.quote(str(script))}"
    before = pre_tool_use(project, settings, sandbox, "Bash", bash_input(call), role, ticket, subagent,
                          agent_id=agent_id, tool_use_id=tool_use_id)
    assert before.decision == "allow", (
        f"the registered PreToolUse commands did not let the fixture call `{call}` through, "
        f"so no Bash call would follow: {before.describe()}"
    )
    run_bash(project, call, sandbox)
    status = git(project, "status", "--porcelain", "--untracked-files=all")
    for relpath in changed:
        assert relpath in status, f"the fixture command `{command}` did not change {relpath}:\n{status}"
    return post_bash(project, settings, sandbox, call, role, ticket, subagent, event, agent_id, tool_use_id)


def write_input(tool_name, path):
    path = str(path)
    if tool_name == "Edit":
        return {"file_path": path, "old_string": "a", "new_string": "b"}
    if tool_name == "Write":
        return {"file_path": path, "content": "written by the acceptance test\n"}
    if tool_name == "NotebookEdit":
        return {"notebook_path": path, "new_source": "print('edited')", "cell_type": "code", "edit_mode": "insert"}
    raise ValueError(tool_name)


def bash_input(command):
    return {"command": command, "description": "W1-05 acceptance attempt"}


def read_input(tool_name, project):
    """The input of a read-only tool that looks at the copy."""
    if tool_name == "Read":
        return {"file_path": str(Path(project) / "README.md")}
    if tool_name == "Grep":
        return {"pattern": "guard", "path": str(project)}
    if tool_name == "Glob":
        return {"pattern": "**/*.py", "path": str(project)}
    raise ValueError(tool_name)


# --------------------------------------------------------------------------
# Role subagent definitions
# --------------------------------------------------------------------------

def frontmatter(text):
    """Top-level ``key: value`` pairs of a Markdown file's YAML frontmatter, or ``None``."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    pairs = {}
    for line in text[3:end].splitlines():
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if match:
            value = match.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            pairs[match.group(1)] = value
    return pairs


def agent_definitions(root=REPO_ROOT):
    """``{subagent type name: [files]}`` for every definition under ``.claude/agents/``."""
    found = {}
    directory = Path(root) / AGENTS_REL
    for path in sorted(directory.rglob("*.md")) if directory.is_dir() else []:
        pairs = frontmatter(path.read_text(encoding="utf-8"))
        if pairs and pairs.get("name"):
            found.setdefault(pairs["name"], []).append(path)
    return found
