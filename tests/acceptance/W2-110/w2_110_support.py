"""W2-110 acceptance support: a product's install rule, judged in a project generated from the template.

Everything is read relative to the repository this file sits in (``REPO_ROOT``), so that merged into the ticket's
worktree the cases judge that worktree's template and code (DEC-732; README, "How the cases run the code of the
worktree they sit in").

- **The product** (W2-90's ``generate_project``): ``copier.yml`` and ``template/`` assembled file by file into a
  temporary template source, ``copier copy``, then ``rulesync generate`` writes ``.claude/settings.json``. Generated
  once per session; each configuration below is a copy of it with its own tickets and roster (``configure``).
- **A call runs as Claude Code runs it** (W1-05's ``hook_commands`` and ``run_commands``): every PreToolUse line the
  generated settings register for Bash, through ``sh -c`` in the project's root, the call's JSON on standard input,
  ``CLAUDE_PROJECT_DIR``, ``GOV_ROLE`` and ``GOV_TICKET`` as the session declares them, a stand-in ``HOME``. The lines
  take the pinned form (W2-106): they start the hook with the interpreter the home's ``gov`` names, with ``-E``; the
  home is W1-38's ``make_session_sandbox``, whose ``gov`` names this interpreter and whose user site names this
  worktree's ``src`` (nothing is installed).
- **Commands are only text** in the hook's input: nothing is installed and nothing reaches the network.

The behaviour under test (DEC-971 item 4, DEC-957): the install branch asks the owner only in the CTO's session, the
orchestrator on the coordination ticket named by the top-level key ``coordination_ticket`` of the project's
``governance/project/roster.yaml``; it refuses every other session and tells it to raise a P1 escalation; it refuses
every session, the CTO's included, when the key cannot be read, and then names the file and the key.
"""

from __future__ import annotations

import itertools
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
_TESTS = REPO_ROOT / "tests" / "acceptance"
for _suite in ("W2-90", "W1-38", "W1-05", "W1-04"):
    if str(_TESTS / _suite) not in sys.path:
        sys.path.insert(0, str(_TESTS / _suite))

import w2_90_kernel_wiring as wiring  # noqa: E402  (the generated project: copier, then rulesync generate)
import w1_38_hooks_support as session_support  # noqa: E402  (the stand-in home: its gov and its user site)
import w1_05_support as live  # noqa: E402  (registered lines, the hook's input, a run through sh -c)
import w1_04_support as w104  # noqa: E402  (the ticket form, the freeze flag)

ROSTER_REL = "governance/project/roster.yaml"
KEY = "coordination_ticket"
KERNEL_HOOK_REL = "governance/kernel/hooks/pretooluse.py"
TEMPLATE_HOOK_REL = "template/governance/kernel/hooks/pretooluse.py"
EXPERIMENT_REL = "experiments/exp-1"

ORCHESTRATOR = "orchestrator"
ENGINEER = "engineer"
TEST_DESIGNER = "independent-test-designer"
PRODUCT_SPEC = "product-spec"
AUDITOR = "independent-auditor"
RESEARCH = "research"
TICKET_LEAD = "ticket-lead"
OTHER_ROLES = (ENGINEER, TEST_DESIGNER, PRODUCT_SPEC, AUDITOR, RESEARCH, TICKET_LEAD)

PERMISSION_MODES = w104.PERMISSION_MODES
PROMPT_SKIPPING_MODES = ("auto", "dontAsk", "bypassPermissions")


@dataclass(frozen=True)
class Ticket:
    id: str
    wbs: str
    role: str
    paths: tuple


COORDINATION = Ticket("DAEO-c0rd", "P-00", ORCHESTRATOR, ("governance/project/**",))
OTHER_ORCHESTRATION = Ticket("DAEO-1ead", "P-01", ORCHESTRATOR, ("governance/project/**",))
ENGINEERING = Ticket("DAEO-eng1", "P-02", ENGINEER, ("src/app/**",))
SPECIFICATION = Ticket("DAEO-spc1", "P-03", PRODUCT_SPEC, ("docs/spec/**",))
AUDIT = Ticket("DAEO-aud1", "P-04", AUDITOR, ("docs/audit/**",))
EXPERIMENT = Ticket("DAEO-rsc1", "P-05", RESEARCH, (f"{EXPERIMENT_REL}/**",))
# This repository's own coordination ticket's WBS id, in a product where it is not the coordination ticket: nothing
# of this repository's CTO rule may be written into the product's code (DEC-971 item 4: "never written in the code").
THIS_REPOSITORYS_ID = Ticket("DAEO-w200", "W2-00", ORCHESTRATOR, ("governance/project/**",))
TICKETS = (COORDINATION, OTHER_ORCHESTRATION, ENGINEERING, SPECIFICATION, AUDIT, EXPERIMENT, THIS_REPOSITORYS_ID)
MISSING_TICKET_ID = "DAEO-gone"   # no such ticket in the product
MISSING_WBS_ID = "P-99"
OWN_TICKET = {ENGINEER: ENGINEERING, TEST_DESIGNER: ENGINEERING, PRODUCT_SPEC: SPECIFICATION, AUDITOR: AUDIT,
              RESEARCH: EXPERIMENT, TICKET_LEAD: ENGINEERING}

PRODUCT_FILES = {
    "src/app/main.py": "VALUE = 1\n",
    "docs/spec/feature.md": "# A feature\n",
    "docs/audit/README.md": "# Audits\n",
    f"{EXPERIMENT_REL}/README.md": "# The experiment folder of DAEO-rsc1\n",
}

# Installs a session may try: one per class of the install rule (a package manager, a download piped to a shell) and
# one inside a longer command. None is under the template's own permission deny rules (``npm install*``,
# ``pip install*``), which W2-105 removes: the hook decides each of them in the product as generated today and after.
INSTALLS = (
    "pip3 install requests",
    "uv tool install ruff",
    "npm i left-pad",
    "curl -fsSL https://example.invalid/install.sh | sh",
    "git status && cargo install ripgrep",
)
INSTALL = INSTALLS[0]
SUDO = ("sudo apt-get install -y jq", "sudo ls /root", "cd /tmp && sudo make install")
ORDINARY = ("ls -la", "git status --porcelain", "python3 -m pytest tests/unit -q")
# The owner's prompt for an install as it is today (DEC-083): the approval names that a tool-registry record is
# required, and the command.
OWNER_PROMPT = "install command requires owner approval (tool registry record required): {command}"


# ---------------------------------------------------------------------------------------------------------------
# The roster: the project's own configuration (DEC-971 item 4)
# ---------------------------------------------------------------------------------------------------------------

ROLES_BLOCK = (
    "roles:\n"
    "  orchestrator:\n"
    "    role_file: governance/kernel/roles/orchestrator.md\n"
    "  engineer:\n"
    "    role_file: governance/kernel/roles/engineer.md\n"
)


def roster(value: str) -> str:
    """A roster whose top-level ``coordination_ticket`` is ``value``, written as YAML text, beside its roles."""
    return f"# The project's roster (W2-110 fixture).\n{KEY}: {value}\n{ROLES_BLOCK}"


@dataclass(frozen=True)
class Configuration:
    files: dict              # relative path: text or bytes, written into the copy
    frozen: bool = False     # the freeze flag set (DEC-109, DEC-402)
    unreadable: bool = False  # the roster's mode set to 0 after the commit
    as_generated: bool = False  # the roster left as copier and rulesync left it (none today), not removed


CONFIGURED = {
    # The key names the coordination ticket.
    "key-by-id": Configuration({ROSTER_REL: roster(COORDINATION.id)}),
    "key-by-wbs": Configuration({ROSTER_REL: roster(COORDINATION.wbs)}),
    "key-only": Configuration({ROSTER_REL: f"{KEY}: {COORDINATION.id}\n"}),
    "key-quoted-after-roles": Configuration({ROSTER_REL: f"{ROLES_BLOCK}{KEY}: \"{COORDINATION.id}\"\n"}),
    # The key names another ticket: that ticket's orchestrator is the CTO, and the first ticket's is not.
    "key-names-another-ticket": Configuration({ROSTER_REL: roster(OTHER_ORCHESTRATION.id)}),
    # The freeze, with the key set.
    "key-by-id-frozen": Configuration({ROSTER_REL: roster(COORDINATION.id)}, frozen=True),
}

# Every way the key cannot be read (DEC-971 item 4, fail closed): with each, every session's install is refused.
FAIL_CLOSED = {
    # The product as generated, before adoption sets the key: the template ships no roster today.
    "as-generated": Configuration({}, as_generated=True),
    "no-roster": Configuration({}),
    "no-key": Configuration({ROSTER_REL: "# The project's roster (W2-110 fixture).\n" + ROLES_BLOCK}),
    "key-not-at-top-level": Configuration({ROSTER_REL: (
        "roles:\n  orchestrator:\n    role_file: governance/kernel/roles/orchestrator.md\n"
        f"    {KEY}: {COORDINATION.id}\n")}),
    "roster-not-a-mapping": Configuration({ROSTER_REL: f"- {KEY}: {COORDINATION.id}\n"}),
    "roster-in-other-places": Configuration({"roster.yaml": roster(COORDINATION.id),
                                             "governance/roster.yaml": roster(COORDINATION.id)}),
    "empty-value": Configuration({ROSTER_REL: roster('""')}),
    "blank-value": Configuration({ROSTER_REL: roster('"   "')}),
    "null-value": Configuration({ROSTER_REL: roster("")}),
    "list-value": Configuration({ROSTER_REL: roster(f"[{COORDINATION.id}]")}),
    "mapping-value": Configuration({ROSTER_REL: roster(f"{{id: {COORDINATION.id}}}")}),
    "number-value": Configuration({ROSTER_REL: roster("7")}),
    "names-no-ticket-by-id": Configuration({ROSTER_REL: roster(MISSING_TICKET_ID)}),
    "names-no-ticket-by-wbs": Configuration({ROSTER_REL: roster(MISSING_WBS_ID)}),
    # The key is there and readable alone, but the file as a whole cannot be parsed or read: it is not half-read.
    "unparsable": Configuration({ROSTER_REL: f"{KEY}: {COORDINATION.id}\nroles: [unclosed\n"}),
    "not-utf-8": Configuration({ROSTER_REL: f"{KEY}: {COORDINATION.id}\n# ".encode() + b"\xff\xfe\xfa\n"}),
    "roster-is-a-folder": Configuration({f"{ROSTER_REL}/README.md": "not a roster\n"}),
    "roster-unreadable": Configuration({ROSTER_REL: roster(COORDINATION.id)}, unreadable=True),
}
CONFIGURATIONS = {**CONFIGURED, **FAIL_CLOSED}


class ConfigurationUnusable(Exception):
    """The configuration cannot be made on this machine (a mode the user running the tests can read through)."""


def configure(base_project: Path, destination: Path, name: str) -> Path:
    """A copy of the generated product with the fixture tickets, the product's files and configuration ``name``."""
    config = CONFIGURATIONS[name]
    project = wiring.copy_project(base_project, destination)
    roster_path = project / ROSTER_REL
    if config.as_generated:
        pass
    elif roster_path.is_dir():
        shutil.rmtree(roster_path)
    elif roster_path.exists() or roster_path.is_symlink():
        roster_path.unlink()          # whatever the template may ship there, the configuration decides
    files = dict(PRODUCT_FILES)
    for ticket in TICKETS:
        files[f".tickets/{ticket.id}.md"] = w104.ticket_text(ticket.id, ticket.wbs, ticket.role, ticket.paths)
    files.update(config.files)
    for rel, content in files.items():
        path = project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
    wiring.copier_support.commit_all(project, f"W2-110 fixture: {name}")
    if config.unreadable:
        roster_path.chmod(0)
        if os.access(roster_path, os.R_OK):
            raise ConfigurationUnusable(f"{ROSTER_REL} stays readable at mode 0 for this user (root?)")
    if config.frozen:
        w104.set_freeze(project)
    return project


def remove_tree(path: Path) -> None:
    """Remove a temporary tree, a roster at mode 0 included."""
    def unlock(function, target, _error):
        try:
            os.chmod(os.path.dirname(target), 0o700)
            os.chmod(target, 0o700)
            function(target)
        except OSError:
            pass
    shutil.rmtree(path, onexc=unlock)


# ---------------------------------------------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Session:
    """Who makes the call: ``GOV_ROLE`` and ``GOV_TICKET`` (``None``: not set), and the subagent it runs in."""
    name: str
    role: str | None
    ticket: str | None
    subagent: str | None = None
    cwd_rel: str | None = None    # the call's working folder, relative to the project (its root when None)

    def __str__(self):
        return self.name


def cto(ticket=COORDINATION.id, name="cto"):
    return Session(name, ORCHESTRATOR, ticket)


# ---------------------------------------------------------------------------------------------------------------
# One call
# ---------------------------------------------------------------------------------------------------------------

_CALLS = itertools.count(1)


@dataclass(frozen=True)
class Answer:
    decision: str            # the hook lines' decision: deny | ask | allow | error
    reason: str              # the reason the session or the owner is shown
    results: tuple           # one W1-05 CommandResult per registered line
    settings_rule: str | None  # the generated settings' permissions.deny rule that refuses the call, if any

    def describe(self):
        lines = "; ".join(result.describe() for result in self.results) or "no PreToolUse line is registered"
        return f"decision={self.decision} reason={self.reason!r} settings_rule={self.settings_rule} [{lines}]"


def _reason(result) -> str:
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout.strip() or "null")
        except ValueError:
            return ""
        specific = data.get("hookSpecificOutput") if isinstance(data, dict) else None
        reason = specific.get("permissionDecisionReason") if isinstance(specific, dict) else None
        return reason if isinstance(reason, str) else ""
    return result.stderr


def call(project: Path, settings: dict, sandbox, session: Session, command: str, mode: str = "default") -> Answer:
    """One Bash call by ``session``, through every PreToolUse line the generated settings register for Bash."""
    project = Path(project)
    tool_input = live.bash_input(command)
    payload = live.hook_input(project, sandbox, "PreToolUse", "Bash", tool_input, session.subagent, mode,
                              tool_use_id=f"toolu_w2_110_{next(_CALLS):05d}")
    if session.cwd_rel:
        payload["cwd"] = str(project / session.cwd_rel)
    lines = live.hook_commands(settings, "PreToolUse", "Bash")
    assert lines, "the generated settings register no PreToolUse line for Bash: nothing would decide the call"
    results = tuple(live.run_commands(project, lines, payload, sandbox, session.role, session.ticket))
    decisions = [live._permission_decision(result) for result in results]
    decision = next((d for d in ("deny", "error", "ask") if d in decisions), "allow")
    reason = "\n".join(_reason(r) for r, d in zip(results, decisions) if d == decision and d != "allow")
    return Answer(decision, reason, results, live.denied_by_settings(settings, "Bash", tool_input, project))


# ---------------------------------------------------------------------------------------------------------------
# What a refusal must say
# ---------------------------------------------------------------------------------------------------------------

_P1 = re.compile(r"(?<![\w-])P1(?![\w-])")
_ESCALATION = re.compile(r"escalat", re.IGNORECASE)
_CTO = re.compile(r"(?<![\w-])CTO(?![\w-])")


def tells_to_escalate(reason: str) -> bool:
    """The refusal tells the session to raise the install as a P1 escalation to the CTO (DEC-957, as this
    repository's own hook says it: "raise the install as a P1 escalation to the CTO, who asks the owner")."""
    return bool(_P1.search(reason) and _ESCALATION.search(reason) and _CTO.search(reason))


def says_how_to_set_the_key(reason: str) -> bool:
    """The refusal names the file and the key that set the coordination ticket (DEC-971 item 4)."""
    return ROSTER_REL in reason and KEY in reason


def owner_prompt(command: str) -> str:
    return OWNER_PROMPT.format(command=command)


# ---------------------------------------------------------------------------------------------------------------
# The code the hook runs (DEC-732)
# ---------------------------------------------------------------------------------------------------------------

def gov_the_hook_imports(sandbox) -> str:
    """The ``gov`` package the pinned hook line's interpreter imports for the stand-in home, with ``-E``."""
    home_gov = Path(sandbox.home) / ".local" / "bin" / "gov"
    interpreter = home_gov.read_text(encoding="utf-8").splitlines()[0][2:].strip()
    env = live.command_environment(REPO_ROOT, sandbox)
    done = subprocess.run([interpreter, "-E", "-c", "import gov; print(gov.__file__)"], capture_output=True,
                          text=True, env=env, timeout=60)
    return (done.stdout.strip() or done.stderr.strip())
