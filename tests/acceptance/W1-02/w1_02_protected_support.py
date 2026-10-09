"""Support code for the protected-reads cases of W1-02 (DEC-508, DEC-525).

Two files of a project are protected from every agent read: the Claude Code
settings file and the project's held-out file. Every case here works on
**stand-in files in a temporary project**: a settings file made up below (a
stand-in deny line, stand-in hooks) and a held-out file made up below (it lists
a stand-in directory). No file of this repository is opened.

**The held-out file's path is never spelled in this suite.** It is taken from
the guard, which already knows it: ``gov.guard.heldout.CONFIG_REL``, with the
key ``CONFIG_KEY``. That import is the one thing this suite takes from the
package directly; every decision is still asked of the hook, run as a process.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import w1_02_support as support

_SRC = str(support.REPO_ROOT / support.GOV_PACKAGE_PARENT_REL)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from gov.guard.heldout import CONFIG_KEY, CONFIG_REL  # noqa: E402  the path is imported, never typed

SETTINGS_REL = ".claude/settings.json"
HELD_REL = CONFIG_REL
PROTECTED = {"settings-file": SETTINGS_REL, "held-out-file": HELD_REL}

# The helper for hook listings: the interface the cases require (README, "The helper").
HELPER_MODULE = "gov.guard.hooks"
HELPER_COMMAND = f"python3 -m {HELPER_MODULE}"
REDACTED = "[redacted]"

# --------------------------------------------------------------------------
# The stand-in settings file
# --------------------------------------------------------------------------

STAND_IN_ENV_NAME = "W1_02_STAND_IN_ENV"
STAND_IN_ENV_VALUE = "w1-02-stand-in-env-value"
STAND_IN_ALLOW = "Bash(w1-02-stand-in-allowed:*)"
STAND_IN_ASK = "Bash(w1-02-stand-in-asked:*)"
STAND_IN_DENY_BASH = "Bash(w1-02-stand-in-denied:*)"
STAND_IN_SANDBOX_VALUE = "w1-02-stand-in-sandbox-path"
GUARD_COMMAND = 'python3 "$CLAUDE_PROJECT_DIR"/governance/kernel/hooks/pretooluse.py'
CHECK_COMMAND = 'python3 "$CLAUDE_PROJECT_DIR"/governance/kernel/hooks/posttooluse.py'
STOP_COMMAND = "echo w1-02-stand-in-stop"
LEAK_PREFIX = "echo w1-02-stand-in-before "
LEAK_SUFFIX = " w1-02-stand-in-after"


def deny_read_rule(listed):
    """A ``Read`` deny line in the form the committed rules have, for the stand-in directory."""
    return f"Read(/{listed}/**)"


def stand_in_settings(listed):
    """The stand-in settings: hooks, and around them everything a listing must leave out."""
    deny_read = deny_read_rule(listed)
    return {
        "env": {STAND_IN_ENV_NAME: STAND_IN_ENV_VALUE},
        "permissions": {
            "allow": [STAND_IN_ALLOW],
            "ask": [STAND_IN_ASK],
            "deny": [deny_read, STAND_IN_DENY_BASH],
            "defaultMode": "acceptEdits",
        },
        "hooks": {
            "PreToolUse": [
                {"hooks": [{"type": "command", "command": GUARD_COMMAND, "timeout": 10}]},
            ],
            "PostToolUse": [
                {"matcher": "Bash", "hooks": [
                    {"type": "command", "command": CHECK_COMMAND},
                    {"type": "command", "command": f"{LEAK_PREFIX}{deny_read}{LEAK_SUFFIX}"},
                ]},
            ],
            "Stop": [
                {"matcher": "", "hooks": [{"type": "command", "command": STOP_COMMAND}]},
            ],
        },
        "sandbox": {"filesystem": {"denyRead": [STAND_IN_SANDBOX_VALUE]}},
    }


def expected_listing():
    """What the helper prints for ``stand_in_settings``: event, matcher, command, in the file's order."""
    return [
        {"event": "PreToolUse", "matcher": "", "command": GUARD_COMMAND},
        {"event": "PostToolUse", "matcher": "Bash", "command": CHECK_COMMAND},
        {"event": "PostToolUse", "matcher": "Bash", "command": f"{LEAK_PREFIX}{REDACTED}{LEAK_SUFFIX}"},
        {"event": "Stop", "matcher": "", "command": STOP_COMMAND},
    ]


def settings_secrets(listed):
    """Every value of the stand-in settings file that is no hook: none may show in a refusal or a listing."""
    return (deny_read_rule(listed), str(listed), STAND_IN_DENY_BASH, STAND_IN_ALLOW, STAND_IN_ASK,
            STAND_IN_ENV_NAME, STAND_IN_ENV_VALUE, STAND_IN_SANDBOX_VALUE)


def write_settings(project, value):
    """Write the settings file of ``project``: a mapping as JSON, a string as it is."""
    path = Path(project) / SETTINGS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# The temporary project with both stand-in files
# --------------------------------------------------------------------------

SETTINGS_TICKET_ID = "DAEO-zz96"   # an engineer ticket whose allowed_paths name the settings file
NEIGHBOUR_OF_SETTINGS = ".claude/notes.md"
BELOW_SETTINGS_FOLDER = ".claude/agents/engineer.md"
RESEARCH = "research"
TICKET_LEAD = "ticket-lead"


@dataclass(frozen=True)
class Guarded:
    """A committed temporary project that holds both stand-in files."""
    project: Path
    sandbox: support.Sandbox
    listed: Path           # the stand-in directory the stand-in held-out file lists
    links: dict            # protected file name -> a symbolic link to it, outside the project

    def rel(self, name):
        return PROTECTED[name]

    def path(self, name):
        return self.project / PROTECTED[name]

    def folder_rel(self, name):
        return os.path.dirname(PROTECTED[name])

    def folder(self, name):
        return self.project / self.folder_rel(name)

    def neighbour_rel(self, name):
        """Another file in the folder that holds the protected file."""
        if name == "settings-file":
            return NEIGHBOUR_OF_SETTINGS
        return f"{self.folder_rel(name)}/bootstrap.md"

    def secrets(self, name):
        """What a refusal for the protected file must not carry."""
        if name == "settings-file":
            return settings_secrets(self.listed)
        return (HELD_REL, os.path.basename(HELD_REL), str(self.path(name)), str(self.listed))


def make_guarded(base):
    """Build the project, its sandbox directories and the two stand-in files; commit them."""
    base = Path(base)
    sandbox = support.make_sandbox(base / "sandbox")
    tickets = support.default_tickets()
    tickets[f"{SETTINGS_TICKET_ID}.md"] = support.ticket_text(
        ticket_id=SETTINGS_TICKET_ID, wbs_id="W1-96", role=support.ENGINEER, allowed_paths=(SETTINGS_REL,))
    project = support.make_project(base / "project", tickets=tickets)

    listed = sandbox.elsewhere / "w1-02-stand-in-held-out"
    listed.mkdir()
    (listed / "answers.md").write_text("stand-in answers\n", encoding="utf-8")

    write_settings(project, stand_in_settings(listed))
    held = project / HELD_REL
    held.parent.mkdir(parents=True, exist_ok=True)
    held.write_text(f"{CONFIG_KEY}:\n- {listed}\n", encoding="utf-8")
    for rel in (NEIGHBOUR_OF_SETTINGS, BELOW_SETTINGS_FOLDER):
        path = project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("VALUE = 1\n", encoding="utf-8")
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "stand-in settings file and stand-in held-out file")

    links = {}
    for name, rel in PROTECTED.items():
        link = sandbox.elsewhere / f"link-to-the-{name}"
        link.symlink_to(project / rel)
        links[name] = link
    return Guarded(project, sandbox, listed, links)


# --------------------------------------------------------------------------
# Who makes a call: name -> (GOV_ROLE, GOV_TICKET, subagent type)
# --------------------------------------------------------------------------

ACTORS = {
    "no-role": (None, None, None),
    "unknown-role": ("developer", support.TICKET_ID, None),
    "orchestrator": (support.ORCHESTRATOR, support.ORCHESTRATOR_TICKET_ID, None),
    "engineer": (support.ENGINEER, support.TICKET_ID, None),
    "product-spec": (support.PRODUCT_SPEC, support.PRODUCT_SPEC_TICKET_ID, None),
    "test-designer": (support.TEST_DESIGNER, support.TICKET_ID, None),
    "auditor": (support.AUDITOR, support.TICKET_ID, None),
    "research": (RESEARCH, support.TICKET_ID, None),
    "ticket-lead": (TICKET_LEAD, support.TICKET_ID, None),
    "engineer-subagent-of-the-orchestrator": (support.ORCHESTRATOR, support.ORCHESTRATOR_TICKET_ID,
                                              support.ENGINEER),
    "untyped-subagent-of-the-engineer": (support.ENGINEER, support.TICKET_ID, "general-purpose"),
}


def ask(guarded, tool_name, tool_input, who):
    """The guard's decision on one call by the actor named ``who``."""
    role, ticket, subagent = ACTORS[who] if isinstance(who, str) else who
    return support.run_hook(guarded.project, tool_name, tool_input, guarded.sandbox, role=role, ticket=ticket,
                            subagent=subagent)


def output_of(result):
    """Everything a refusal says: the reason, and whatever else the hook wrote."""
    return result.stdout + "\n" + result.stderr


def reason_of(result):
    try:
        return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    except (ValueError, KeyError, TypeError):
        return ""


def assert_refused_by_rule(result, what):
    """A deny decision of the guard's own: exit code 0 and ``permissionDecision: deny``.

    Exit code 2 also stops a call, but it is the hook's report of its own
    failure (DEC-110); a rule must decide here.
    """
    assert result.decision == "deny" and result.returncode == 0, (
        f"{what} was not refused by a rule: decision={result.decision} exit={result.returncode}"
    )


def assert_allowed(result, what):
    assert result.decision == "allow", f"{what} was not allowed: decision={result.decision} exit={result.returncode}"


# --------------------------------------------------------------------------
# The helper, run as a command
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class HelperRun:
    returncode: int
    stdout: str
    stderr: str


def run_helper(project, sandbox, cwd=None, project_dir=True):
    """Run the helper as an agent's shell would: no argument, the project found from the environment.

    ``project_dir`` False leaves ``CLAUDE_PROJECT_DIR`` out, so the working
    directory alone names the project.
    """
    env = support.hook_environment(project, sandbox)
    if not project_dir:
        del env["CLAUDE_PROJECT_DIR"]
    proc = subprocess.run([sys.executable, "-m", HELPER_MODULE], capture_output=True, text=True,
                          cwd=str(cwd or project), env=env, timeout=support.HOOK_TIMEOUT_S, check=False)
    return HelperRun(proc.returncode, proc.stdout, proc.stderr)
