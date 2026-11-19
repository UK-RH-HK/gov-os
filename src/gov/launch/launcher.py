"""Worker session launcher: ``gov launch <role> <ticket> [-- <CLI arguments>]`` (W1-46, DEC-231).

Starts the CLI at ``~/.local/bin/claude`` (DEC-205) in the repository root with
one ``--settings`` value built here: ``GOV_ROLE``, ``GOV_TICKET``, ``GOV_STORE`` where the project configures its integration store
(W2-116, ``gov.launch.store``) and a per-session temp directory, removed when the session ends
(DEC-386), also when the launcher is interrupted or sent SIGTERM or SIGHUP
(DEC-392). A worker session starts as its role: the role file's text and its named
skills appended, its default model and effort, no compaction threshold, the user
settings' ask and deny rules kept, and one launch record written before it starts
(W2-60a).

Emergency 2 (docs/emergency-2/EMERGENCY-2.md 2.1-2.4, 6.1, release 0.1.2): no guard, no sandbox, no permission
limits. A launch no longer requires the guard in the repository's settings, writes no sandbox block and no deny rule
of its own, and accepts the no-prompt mode (``permissions.defaultMode: bypassPermissions`` in the repository's
settings, or ``--permission-mode bypassPermissions`` / ``--dangerously-skip-permissions`` after ``--``). The only deny
rules a worker carries are the user's (``git push`` and ``sudo``, 2.4). Sessions stay apart by their worktree, their
folders and their brief.

A lead (``gov launch orchestrator|lead <ticket>``, W2-136 S9) is started only when
the plan's check admits its ticket, with ``GOV_ROLE=orchestrator``, its
``GOV_TICKET`` and the launcher's own ``GOV_STORE`` as a worker's (W2-56 R5), as the dispatcher starts a lead (``build_lead_settings``); a worker
launch never consults the plan.

Every launch, lead or worker, passes the machine-wide resource gate (W2-20 S19,
DEC-1088 (5)(b)): while it is shut on any reading, the launch is refused naming
each limit and its reading, unless ``--gate-override DEC-NNN`` starts it anyway;
that override, and a lead's plan override, are written to
``~/.gov-os/machine/launch.log`` and to stderr (P-1, P-8). A started session is
in the machine-wide registry while it runs.

Every session, lead or worker, gets its role's template ``<root>/.claude/templates/<stem>.md`` in its appended
system prompt, by the one ``--append-system-prompt-file`` after the caller's arguments; a launch whose template is
missing is refused before anything is written (W2-153, DEC-1050). A lead's flag names the template itself. A worker's
names one file in the session's temp folder, ``role-<role>.md``, composed of the role file's bytes as W2-60a appends
them (the role file, then each named skill's ``SKILL.md``), then one blank line, then the template's bytes; the
launch record's ``appended_sha256`` is that file's, and its ``template`` names the template's path and sha256.

W2-60b: a worker role is launchable when its kernel role file says it is a worker (``_role_kind``); there is no fixed
list of roles. A writing session is refused while another is live in its worktree, read from the session records
(``gov.launch.session_record``). Each worker session gets one session record, written whole once its process has
started and replaced whole after it ends, whatever its ending; a record that cannot be written leaves the exit code as
it is, with one line on stderr. ``tests_worktree`` makes a ticket's tests worktree, ``<tree>-tests`` on
``<branch>-tests`` at the tree's HEAD.

No message of this module carries a held-out path.
"""

from __future__ import annotations

import io
import json
import os
import re
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from subprocess import SubprocessError

import yaml

from gov.cli.errors import GovError
from gov.launch import criticality as crit, environ, model_exceptions, record, role as roles, session_record
from gov.launch.store import ENV as STORE_ENV, StoreSettingError, configured as configured_store
from gov.launch.store import main_root as main_store_root
from gov.spend import brake as spend_brake
from gov.util import runs
from gov.util.freeze import freeze_state
from gov.util.gitenv import git_binary, git_env
from gov.util.parts import load_yaml_unique
from gov.util.tickets import _load_ticket

# W2-60b S7, S8 (DEC-946 (W3-P09), DEC-826 Q1): the launchable roles and their own-ticket rule are read from the
# kernel's role files (``_role_kind``), so a new role is a file, not a code change. A role file is a worker's unless it
# says otherwise: its ``Authority level`` line names another level (the CTO's, the Senior Engineer's and the ticket
# lead's say ``coordinator``) or its ``Network`` line says the launcher gives it no profile. A worker keeps to a ticket
# whose ``role`` is its own (open package DP-8) unless it is independent: its ``Authority level`` line says
# "independent of", or its name begins ``independent-`` (the kernel's naming of its independent roles); an independent
# role may be launched on any ``in_progress`` ticket. A role with no role file, or one that cannot be read, refuses.
ROLE_NAME = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
AUTHORITY_HEAD, NETWORK_HEAD = "- **Authority level:**", "- **Network:**"
WORKER_LEVEL, NO_PROFILE = "worker", "no profile from the launcher"
INDEPENDENT, INDEPENDENT_PREFIX = "independent of", "independent-"
TESTS_SUFFIX = "-tests"  # W2-60b S10: the tests worktree and its branch are the ticket tree's and branch's names + this
# W2-136 S9: a lead is a session of GOV_ROLE orchestrator with a GOV_TICKET, launched as ``orchestrator`` or ``lead``
# (W2-121's name for it). Only the launched role and ticket are checked against the plan, never the caller's own
# environment: a worker launch never consults the plan (DEC-1088 (5)(a), settled by the CTO).
LEAD_ROLES = ("lead", "orchestrator")
LEAD_GOV_ROLE = "orchestrator"
# W2-153 (DEC-1050, W2-128 TPL-4): the role -> template map. The template is the session's appended system prompt;
# gov.adapters.portability reuses the map for the subagent sources and the template copies.
ROLE_TEMPLATES = {
    "engineer": "role-engineer",
    "independent-test-designer": "role-test-designer",
    "independent-auditor": "role-reviewer",
    "product-spec": "role-product-spec",
    "research": "role-research",
    "lead": "role-lead",
    "orchestrator": "role-lead",
}
# A role the map does not name has the template ``role-<role>.md`` (W2-60b): a new role is its role file and its
# template, with no code change.
TEMPLATE_STEM = "role-{role}"
TEMPLATES_REL = ".claude/templates"  # the generated copies, written only by an ACT (DEC-315)
TEMPLATE_FLAG = "--append-system-prompt-file"
CLI_REL = ".local/bin/claude"
REPO_SETTINGS = (".claude/settings.json", ".claude/settings.local.json")
RUNTIME, SCRATCH = ".gov-runtime", "scratch"
# The no-prompt mode, accepted since Emergency 2 (0.1.2; DEC-313 superseded by EMERGENCY-2 2.2, 2.9).
BYPASS_MODE = "bypassPermissions"
WORKER_CACHE_TTL = "5m"  # a launched worker's prompt-cache lifetime (audit 09; the CTO's own session keeps 1 h)
# W2-201 S8 (audit 09 item 3, DEC-1212 (4)): no inbox waiter and no idle-check wake-up; a hook of these events whose
# command names one of these refuses a worker launch.
WAKE_EVENTS = ("Stop", "SubagentStop", "UserPromptSubmit")
WAKE_COMMANDS = ("stop_waiter_check", "stop_idle_check", "gov session-watch", "gov msg wait")
# Names kept for the readers that import them (suites, fixtures); since Emergency 2 no launch decides by them.
EXPERIMENTS_ROOT = "experiments"
KERNEL_ALLOWLIST_REL = "template/governance/kernel/launch/research-allowlist.yaml"
PROJECT_ALLOWLIST_REL = "governance/project/research-allowlist.yaml"
BYPASS_FLAGS = ("--dangerously-skip-permissions", "--allow-dangerously-skip-permissions")
# W2-56 S6 (DEC-826 Q5): arguments that add context or replace the role's prompt; refused alone, with a spaced value
# and in the ``=`` form, wherever they stand after ``--``. Emergency 2: the guard's own (--restricted, --safe-mode) go.
CONTEXT_FLAGS = ("--agents", "--plugin-dir", "--plugin-url", "--mcp-config", "--system-prompt")
GUARD_FLAGS = CONTEXT_FLAGS  # the former name, for its readers
# W2-56 D-12: a worker's temp folder, short enough that its code-graph daemon folders fit the tool's socket (107
# bytes, DEC-338); the prefix is what the weekly sweep (DEC-902) and the code index (``gov.codeintel``) look for.
TEMP_PREFIX = "gov-launch-"
# DEC-392: these end the session and remove its folder, and the launcher then ends with INTERRUPT_EXIT.
END_SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
INTERRUPT_EXIT = 130
END_WAIT_S = 5  # whole seconds a session that was asked to end may still run before it is killed
REAP_WAIT_S = 3.0  # seconds the launcher waits, after the kill, for the session's group to be gone (W2-56 S12)
# W2-60a (DEC-826 Q5): what the launcher's own line keeps out: connectors, user-level agents and skills.
OWN_SWITCHES = ("--setting-sources", "project,local", "--strict-mcp-config")
KEPT_OUT = ["--strict-mcp-config", "--setting-sources project,local", "autoMemoryEnabled false"]
# W2-60a: the arguments the launcher sets itself, refused after "--", and why.
SET_ITSELF = {
    "--agent": "the launcher starts the session as its role, with the role file's text appended (DEC-826 Q1)",
    "--append-system-prompt": "the launcher appends the role's text itself (DEC-826 Q1)",
    "--append-system-prompt-file": "the launcher appends the role's text itself (DEC-826 Q1)",
    "--session-id": "the launcher gives the session its id and keys the launch record by it",
    "--autocompact": "no launch sets a compaction threshold (DEC-838)",
    "--fallback-model": "the session runs on the role's model alone, never on another (DEC-839 item 1)",
    "--chrome": "a launched session loads no connector (DEC-826 Q5)",
    "--ide": "a launched session loads no connector (DEC-826 Q5)",
    "--system-prompt-snapshot": "the session's prompt is the CLI's default with the role's text appended (DEC-826 Q1)",
}
RESUME_RULE = "a launch resumes a session by its id (--resume <session id>), so that the record can name it"
COMPACT_ENV, COMPACT_KEY = "CLAUDE_CODE_AUTO_COMPACT_WINDOW", "autoCompactWindow"
# W2-60a: the other names under env by which the CLI takes a compaction threshold.
COMPACT_ENVS = (COMPACT_ENV, "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE", "CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS")
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
# W2-184 (RUBRIC-2 at launch, DEC-1120): the options' forms, the trial and probe records' places, the effort floor.
_TRIAL_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_DECISION = re.compile(r"DEC-\d+")
_PROBE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_VERDICT = re.compile(r"^```verdict[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
TRIALS_REL = "governance/project/trials"
PROBES_REL = "docs/probes"
TRIAL_KEYS = frozenset({"role", "criticality", "model", "effort", "tickets", "reviewer"})
FLOOR = "high"  # DEC-1120 (3): when the table's effort is high or above, the launch's own choice is not below it
BELOW_FLOOR = ("low", "medium")
AUDITOR = "independent-auditor"


def __getattr__(name: str):
    """W2-60b F1 (DEC-946 (W3-P09)): no list of launchable roles is held in this module. ``WORKER_ROLES`` is served by
    name (PEP 562) for W2-153's and W1-50's readers only: the template map's worker entries (its five, the lead names
    left out), worked out when read. No launch reads it to decide anything; what a launch admits is whatever role file
    ``_role_kind`` admits (W2-60b S7)."""
    if name == "WORKER_ROLES":
        return tuple(role for role in ROLE_TEMPLATES if role not in LEAD_ROLES)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _refuse(reason: str) -> GovError:
    return GovError("LAUNCH_REFUSED", reason)


def build_settings(root: Path, role: str, ticket_id: str) -> dict:
    """The ``--settings`` value of a worker session: its env (``GOV_ROLE``, ``GOV_TICKET``, ``GOV_STORE``) and an empty
    deny list, to which ``_worker_plan`` adds the user's deny rules. Emergency 2 (2.2, 2.4): no sandbox block and no
    deny rule of the launcher's own. ``root`` is a real path."""
    # the owner's audit 09 item (2026-11-18): workers write the 5-minute prompt cache (their calls come fast; checked:
    # CLAUDE_CODE_PROMPT_CACHE_TTL=5m sends the writes to the 5-minute tier); measured in the spend log
    env = {"GOV_ROLE": role, "GOV_TICKET": ticket_id, "CLAUDE_CODE_PROMPT_CACHE_TTL": WORKER_CACHE_TTL, **_store_env(root)}
    return {"env": env, "permissions": {"deny": []}}


def _store_env(root: Path) -> dict:
    """``GOV_STORE`` for a launched session, or nothing where the project configures no integration store. W2-116 S3
    (DEC-963, DEC-1087 (3)): a session's plain `gov retrieve` answers from the integration store, the configured link
    itself as written (followed at each search), never from the worktree the session runs in. The place is the main
    repository's (review F4): a worktree branched before the line was added still gets it. A setting that cannot be
    used refuses the launch before anything starts; the parent's ``GOV_STORE`` never counts (W2-56 S5)."""
    try:
        store = configured_store(main_store_root(root))
    except StoreSettingError as error:
        raise _refuse(f"{error}: the session's retrieval would have no store to answer from (W2-116)") from None
    return {} if store is None else {STORE_ENV: store}


def build_lead_settings(root: Path, ticket_id: str) -> dict:
    """The ``--settings`` value of a lead session (W2-136 S9): ``GOV_ROLE=orchestrator``, its ``GOV_TICKET`` and the
    launcher's own ``GOV_STORE`` as a worker's (W2-56 R5, ``_store_env``), as the dispatcher starts a lead. ``root``
    is a real path."""
    return {"env": {"GOV_ROLE": LEAD_GOV_ROLE, "GOV_TICKET": ticket_id, **_store_env(root)}}


def _check_ticket(root: Path, role: str, ticket_id: str) -> None:
    ticket = _load_ticket(str(root), ticket_id)
    if ticket is None:
        raise _refuse(f"unknown ticket '{ticket_id}'")
    if ticket.get("status") != "in_progress":
        raise _refuse(f"ticket '{ticket_id}' is not in_progress (status: {ticket.get('status')})")
    # W2-60b: whether the role keeps to its own ticket is read from its role file, only when the ticket is another's
    if ticket.get("role") != role and _role_kind(root, role)["own_ticket"]:
        raise _refuse(f"ticket '{ticket_id}' is a ticket of another role ('{ticket.get('role')}'), not of '{role}'")


def _role_kind(root: Path, role: str) -> dict:
    """W2-60b S7, S8: the role file's path and whether the role keeps to its own ticket, read from the kernel role file
    ``gov.launch.role`` reads; refused, naming the role, when the name is not a plain role name, the file is missing or
    cannot be read, holds its ``Authority level`` or ``Network`` line more than once, or says it is no worker."""
    _check_worker_role(role)
    try:
        rel, _, lines = roles._role_file(root, role)
    except GovError as error:
        raise _refuse(f"'{role}' is not a worker role: {error.message} (DEC-946 (W3-P09))") from None
    stated = {}
    for head in (AUTHORITY_HEAD, NETWORK_HEAD):
        found = [line.strip()[len(head):].strip() for line in lines if line.lstrip().startswith(head)]
        if len(found) > 1:
            raise _refuse(f"'{role}': the role file {rel} holds its line '{head}' more than once, so it cannot be told "
                          f"whether gov launch starts it (DEC-946 (W3-P09))")
        stated[head] = found[0] if found else None
    level, network = stated[AUTHORITY_HEAD], stated[NETWORK_HEAD]
    word = re.split(r"[\s,.;:]", level, maxsplit=1)[0] if level is not None else None
    if word is not None and word != WORKER_LEVEL:
        raise _refuse(f"'{role}' is not a worker role: its role file {rel} gives the authority level '{word}', and "
                      f"gov launch starts workers only (a lead is launched as {' or '.join(LEAD_ROLES)})")
    if network is not None and network.startswith(NO_PROFILE):
        raise _refuse(f"'{role}' is not a worker role: its role file {rel} says it has {NO_PROFILE}")
    independent = (level is not None and INDEPENDENT in level) or role.startswith(INDEPENDENT_PREFIX)
    return {"rel": rel, "own_ticket": not independent}


def _check_repository_settings(root: Path, worker: bool = True) -> None:
    """The repository's settings can be read, and for a worker (W2-60a) carry no agent key and no compaction threshold;
    for a linked worktree the CLI loads the local settings from the main checkout's file, which is judged as the tree's
    own copy is; a main checkout that cannot be found refuses. Emergency 2 (2.2, 2.3; 0.1.2): the guard is not required,
    and a sandbox key, ``disableAllHooks``, the no-prompt mode and added directories are the repository's own choice."""
    files = [(root / rel, rel) for rel in REPO_SETTINGS]
    if worker:
        main = record.main_checkout(root, "the local settings file the CLI loads for a worktree session")
        if main != root:
            files.append((main / REPO_SETTINGS[1], str(main / REPO_SETTINGS[1])))
    for path, rel in files:
        if not os.path.lexists(path):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raise _refuse(f"{rel} cannot be read as JSON") from None
        if not isinstance(data, dict):
            raise _refuse(f"{rel} is not a JSON object")
        if worker:
            _check_role_settings(data, rel)
            _check_wake_hooks(data, rel)


def _check_wake_hooks(data: dict, rel: str) -> None:
    """W2-201 S8: a settings file with a hook, in a ``Stop``, ``SubagentStop`` or ``UserPromptSubmit`` entry, whose
    command names an inbox waiter or an idle check refuses a worker launch, naming the file and the command."""
    hooks = data.get("hooks")
    for event in WAKE_EVENTS:
        entries = hooks.get(event) if isinstance(hooks, dict) else None
        for entry in entries if isinstance(entries, list) else []:
            inner = entry.get("hooks") if isinstance(entry, dict) else None
            for hook in inner if isinstance(inner, list) else []:
                command = hook.get("command") if isinstance(hook, dict) else None
                for name in WAKE_COMMANDS:
                    if isinstance(command, str) and name in command:
                        raise _refuse(f"{rel} holds a {event} hook whose command names '{name}': no inbox waiter "
                                      f"and no idle-check wake-up hook wakes a worker session (DEC-1212 (4))")


def _mode_args(cli_args: list[str]) -> list[str]:
    """Emergency 2 (2.3): a session starts in the no-prompt mode unless the caller names a permission mode itself
    (``--permission-mode``, ``--dangerously-skip-permissions``). The CLI does not take ``defaultMode: bypassPermissions``
    from a project's settings for a launched session (seen in EXAMIN's smoke launch, 2026-11-17), so the launcher
    passes it."""
    named = any(a == "--permission-mode" or a.startswith("--permission-mode=") or a in BYPASS_FLAGS for a in cli_args)
    return [] if named else ["--permission-mode", BYPASS_MODE]


def _check_not_paused(root: Path) -> None:
    """Emergency 2 (CAP-05; audit 7 C-1): with the guard gone, ``gov pause``'s freeze flag is honoured here: while the
    main checkout's ``.gov-runtime/freeze`` is frozen, no lead or worker starts. A worktree's own flag counts too."""
    roots = {root}
    try:
        roots.add(record.main_checkout(root, "the freeze flag gov pause sets"))
    except GovError:
        pass
    for each in sorted(roots, key=str):
        if freeze_state(str(each)) == "frozen":
            raise _refuse(f"the project is paused (gov pause set {each}/.gov-runtime/freeze): no session starts "
                          f"until the owner lifts it with gov pause --off (CAP-05)")


def _check_role_settings(data: dict, rel: str) -> None:
    """W2-60a: a settings file that would change a worker session's prompt or its compaction threshold refuses."""
    if "agent" in data:
        raise _refuse(f"{rel} carries an agent key: the launcher starts the session as its role, with the role "
                      f"file's text appended (DEC-826 Q1)")
    env = data.get("env", {})
    if not isinstance(env, dict) or COMPACT_ENV in env or COMPACT_KEY in data:
        raise _refuse(f"{rel} sets {COMPACT_KEY} or env.{COMPACT_ENV}, or carries an env that is not a map: no "
                      f"launch sets a compaction threshold (DEC-838)")
    models = data.get("modelSettings", {})
    if not isinstance(models, dict) or not all(isinstance(each, dict) for each in models.values()):
        raise _refuse(f"{rel} carries a modelSettings that is not a map of maps, so it cannot be shown to set no "
                      f"compaction threshold (DEC-838)")
    thresholds = [f"env.{key}" for key in COMPACT_ENVS if key in env] + \
        [f"modelSettings.{model}.{COMPACT_KEY}" for model, each in models.items() if COMPACT_KEY in each]
    if thresholds:
        raise _refuse(f"{rel} sets {thresholds[0]}: no launch sets a compaction threshold (DEC-838)")


def _check_cli_args(cli_args: list[str]) -> None:
    """Refuse the arguments that replace the launcher's own settings, or add context or replace the role's prompt
    (DEC-826 Q5). Emergency 2 (0.1.2): the no-prompt mode, ``--add-dir`` and ``--bare`` are accepted."""
    for arg in cli_args:
        if arg == "--settings" or arg.startswith("--settings="):
            raise _refuse("the CLI arguments carry --settings: the session's settings come from the launcher")
        if arg == "--setting-sources" or arg.startswith("--setting-sources="):
            raise _refuse("the CLI arguments carry --setting-sources: the launcher sets the session's sources itself")
        name = arg.split("=", 1)[0]
        if name in CONTEXT_FLAGS:
            raise _refuse(f"the CLI arguments carry {name}: it adds context to a worker session or replaces its "
                          f"role's prompt (DEC-826 Q5)")


def template_args(root: Path, role: str) -> list[str]:
    """The flag that gives the session its role template, by absolute path; refused when the file is missing, so no
    session starts without its template (W2-153 S1, F1)."""
    path = root / TEMPLATES_REL / f"{ROLE_TEMPLATES.get(role) or TEMPLATE_STEM.format(role=role)}.md"
    if not path.is_file():
        raise GovError("LAUNCH_NO_TEMPLATE", f"the role template {path} is missing: no '{role}' session starts "
                                             f"without it (DEC-1050)")
    return [TEMPLATE_FLAG, str(path)]


def _given_value(name: str, arg: str, value: str | None, given: dict) -> str | None:
    """The value of ``--model`` or ``--effort`` in ``arg`` (spaced or ``=``); ``None`` when ``arg`` is neither."""
    if arg == name:
        found = value if value is not None and not value.startswith("-") else ""
    elif arg.startswith(name + "="):
        found = arg[len(name) + 1:]
    else:
        return None
    if not found:
        raise _refuse(f"the CLI arguments carry {name} without a value")
    if name in given:
        raise _refuse(f"the CLI arguments carry {name} twice: the session has one")
    return found


def _check_own_args(cli_args: list[str]) -> dict:
    """Refuse the arguments the launcher sets itself (W2-60a) and return the ``model``, ``effort`` and ``resume`` given.

    Judged word by word, as ``_check_cli_args``: a prompt that only names one as a word passes."""
    given: dict = {}
    for arg, value in zip(cli_args, [*cli_args[1:], None]):
        for name, why in SET_ITSELF.items():
            if arg == name or arg.startswith(name + "="):
                raise _refuse(f"the CLI arguments carry {name}: {why}")
        if arg == "--fork-session":
            raise _refuse("the CLI arguments carry --fork-session: the launcher forks a resumed session itself, so "
                          "that it has an id of its own")
        if arg in ("--continue", "-c") or (re.fullmatch(r"-[A-Za-z]{2,}", arg) and "c" in arg) \
                or (arg.startswith("-c") and len(arg) > 2):
            raise _refuse(f"the CLI arguments carry {arg} (--continue, -c): {RESUME_RULE}")
        if arg in ("--resume", "-r") or arg.startswith("--resume="):
            found = value if arg in ("--resume", "-r") else arg[len("--resume="):]
            if found is None or not _UUID.fullmatch(found) or "resume" in given:
                raise _refuse(f"the CLI arguments carry {arg} without one session id (a UUID): {RESUME_RULE}")
            given["resume"] = found
        elif (re.fullmatch(r"-[A-Za-z]{2,}", arg) and "r" in arg) or (arg.startswith("-r") and len(arg) > 2):
            raise _refuse(f"the CLI arguments carry {arg}, a resume (--resume, -r) spelled otherwise: {RESUME_RULE}")
        for name, key in (("--model", "model"), ("--effort", "effort")):
            found = _given_value(name, arg, value, given)
            if found is not None:
                if key == "effort" and found not in roles.EFFORTS:
                    raise _refuse(f"the CLI arguments carry --effort {found}: the effort is one of "
                                  f"{', '.join(roles.EFFORTS)}")
                given[name] = found
    return {"model": given.get("--model"), "effort": given.get("--effort"), "resume": given.get("resume")}


def _composed(appended: bytes, template: bytes) -> bytes:
    """A worker's appended prompt: the role file's bytes as W2-60a appends them, one blank line, the template's bytes.
    The blank line is one empty line after the role text's last line (a missing final newline is supplied first)."""
    return (appended if appended.endswith(b"\n") else appended + b"\n") + b"\n" + template


def _worker_deny(deny: list[str], user_deny: list[str]) -> list[str]:
    """A worker's deny list: ``build_settings``' rules (none since Emergency 2), then the user's; each once, in that
    order. Emergency 2 (2.4): the user's ``git push`` and ``sudo`` lines are the only denies."""
    return list(dict.fromkeys([*deny, *user_deny]))


def _check_options(reason: str | None, trial: str | None, owner_named: str | None) -> None:
    """W2-184: the forms of ``--reason``, ``--trial`` and ``--owner-named``, before anything is read or made."""
    if reason is not None and (not isinstance(reason, str) or not reason.strip()):
        raise _refuse("--reason takes a reason, not an empty text")
    if trial is not None and (not isinstance(trial, str) or not _TRIAL_ID.fullmatch(trial)):
        raise _refuse(f"--trial takes a trial id of letters, digits, '.', '_' and '-', not {trial!r}")
    if owner_named is not None and (not isinstance(owner_named, str) or not _DECISION.fullmatch(owner_named)):
        raise _refuse(f"--owner-named takes a decision id (DEC-<number>), not {owner_named!r}")


def _check_projection(projection_usd) -> None:
    """W2-156: ``--projection-usd`` is a number above 0 (the runaway brake's projection), before anything is read."""
    if projection_usd is not None and (isinstance(projection_usd, bool) or not isinstance(projection_usd, (int, float))
                                       or not 0 < projection_usd < float("inf")):
        raise _refuse(f"--projection-usd takes a number above 0, not {projection_usd!r}")


def _ticket_names(ticket_id: str, ticket: dict) -> list[str]:
    """The names one ticket goes by: the id the launch was given, and the ticket's own ``id`` and ``wbs_id``."""
    names = [ticket_id] + [ticket.get(key) for key in ("id", "wbs_id")]
    return list(dict.fromkeys(name for name in names if isinstance(name, str) and name))


def _launch_records(root: Path) -> list[tuple[str, dict]]:
    """The shared record folder's launch records (``record: gov-launch``), read once for the probe records' roots
    (W2-184 5.1a) and the review count (6.1). A file there that cannot be read as JSON refuses: a skipped record could
    hide a promotion or a review (P-td5-1, fail closed). Each is returned as ``(file stem, record)``."""
    found = []
    for path in sorted(record.folder(root).glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raise _refuse(f"the launch record {path.name} cannot be read as JSON, so the roots of the ticket's probe "
                          f"records cannot be found and its reviews cannot be counted") from None
        if isinstance(data, dict) and data.get("record") == "gov-launch":
            found.append((path.stem, data))
    return found


def _probe_roots(root: Path, names: list[str], launches: list[tuple[str, dict]]) -> list[Path]:
    """W2-184 5.1a (P-W2-184-1 (a), DEC-1010): the launch root, then, in sorted order, every other folder that a
    launch record of this ticket (under any of its names, any role) gives as its ``root``. A named root that is not
    there, or is not a folder, is skipped."""
    others = set()
    for _, data in launches:
        named = data.get("root")
        if not isinstance(data.get("ticket"), str) or data["ticket"] not in names or not isinstance(named, str) \
                or not os.path.isabs(named) or not os.path.isdir(named):
            continue
        real = Path(os.path.realpath(named))
        if real != root:
            others.add(real)
    return [root, *sorted(others, key=str)]


def _probe_files(roots: list[Path], names: list[str]) -> list[tuple[str, list[tuple[Path, Path]]]]:
    """The ticket's probe records (W2-184 5.1, 5.1a): the ``.md`` files under ``docs/probes/<ticket id>/`` of each root,
    at any depth, as ``(root-relative path, [(file, root), ...])`` in sorted path order. Every root's copy of a path is
    kept (R3, interface 10.3, revising P-td5-2), the launch root's first, then the others in sorted order."""
    copies: dict[str, list[tuple[Path, Path]]] = {}
    for base in roots:
        for name in names:
            folder = base / PROBES_REL / name
            if not _PROBE_NAME.fullmatch(name) or not folder.is_dir():
                continue
            for path in sorted(folder.rglob("*.md")):
                if path.is_file():
                    found = copies.setdefault(path.relative_to(base).as_posix(), [])
                    if all(path != seen for seen, _ in found):
                        found.append((path, base))
    return sorted(copies.items())


def _read_probe(rel: str, path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError:
        raise _refuse(f"the probe record {rel} cannot be read, so the ticket's promotion cannot be judged") from None


def _probe_record(rel: str, data: bytes) -> tuple[dict, str] | None:
    """One probe record's front matter and the text after it, from the file's bytes; ``None`` when it has none, or it
    is not a map with ``type: probe`` (skipped). A front matter that is not YAML, or bytes that are not UTF-8, refuse,
    naming the file as ``rel`` (its root-relative path, with the file's own path when it lies under another root)."""
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        raise _refuse(f"the probe record {rel} cannot be read, so the ticket's promotion cannot be judged") from None
    if not lines or lines[0].strip() != "---":
        return None
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None
    try:
        front = load_yaml_unique("\n".join(lines[1:end]))
    except yaml.YAMLError:
        raise _refuse(f"the probe record {rel} has a front matter that is not YAML") from None
    if not isinstance(front, dict) or front.get("type") != "probe":
        return None
    return front, "\n".join(lines[end + 1:])


def _fails_open(rel: str, body: str) -> bool:
    """True when a ``verdict`` block of the record holds a finding whose consequence is ``fails open``; a block that
    is not JSON of JUDGEMENT.md's shape refuses."""
    found = False
    for block in _VERDICT.finditer(body):
        try:
            data = json.loads(block.group(1))
            kpis = data["kpis"]
            findings = [finding for kpi in kpis for finding in kpi["findings"]]
            if not isinstance(kpis, list) or not all(isinstance(finding, dict) for finding in findings) \
                    or not all(isinstance(kpi["findings"], list) for kpi in kpis):
                raise TypeError
        except (ValueError, KeyError, TypeError):
            raise _refuse(f"the probe record {rel} has a verdict block that is not JSON of the form "
                          f'{{"kpis": [{{"kpi": ..., "verdict": ..., "findings": [{{"id": ..., "consequence": ...}}]}}]}}'
                          ) from None
        found = found or any(finding.get("consequence") == "fails open" for finding in findings)
    return found


def _promotion(root: Path, names: list[str], launches: list[tuple[str, dict]]) -> dict | None:
    """W2-184 5.2: ``{"reason", "record"}`` when the ticket's probe records, under the launch root and every root the
    ticket's launch records name (5.1a), hold a fail-open finding (checked first), or two or more of them have
    ``judgement`` fail or failed; ``None`` when neither. The record is named by its root-relative path.

    R3 (interface 10.3): every root's copy of a path is read (identical bytes are one copy), and each copy that
    refuses refuses the launch; the path is one review: it holds a fail-open finding, or has failed, when any of its
    copies does, and counts as one failed record at most."""
    failed, fail_open = [], None
    for rel, copies in _probe_files(_probe_roots(root, names, launches), names):
        read: list[bytes] = []
        path_fails_open = path_failed = False
        for path, base in copies:
            shown = rel if base == root else f"{rel} ({path})"
            data = _read_probe(shown, path)
            if data in read:
                continue
            read.append(data)
            loaded = _probe_record(shown, data)
            if loaded is None:
                continue
            front, body = loaded
            path_fails_open = _fails_open(shown, body) or path_fails_open
            path_failed = path_failed or front.get("judgement") in ("fail", "failed")
        if path_fails_open and fail_open is None:
            fail_open = rel
        if path_failed:
            failed.append(rel)
    if fail_open is not None:
        return {"reason": "a fail-open finding", "record": fail_open}
    if len(failed) >= 2:
        return {"reason": "two failed reviews", "record": failed[1]}
    return None


def _counted_reviews(launches: list[tuple[str, dict]], names: list[str], resume: str | None) -> list[dict]:
    """W2-184 6.1: of the shared record folder's launch records (``_launch_records``), this ticket's auditor launches
    that resume nothing, leaving out the record of the session being resumed."""
    counted = []
    for stem, data in launches:
        if data.get("role") == AUDITOR and isinstance(data.get("ticket"), str) and data["ticket"] in names \
                and data.get("resumes") is None and data.get("session_id") != resume:
            counted.append({"session_id": data.get("session_id") or stem, "model": data.get("model"),
                            "effort": data.get("effort")})
    return counted


def _trial(root: Path, trial_id: str, role: str, ticket_class: str, names: list[str]) -> dict:
    """W2-184 4.3: the recorded trial, read from ``governance/project/trials/<id>.yaml`` and judged against this
    launch; a trial that is missing, malformed or does not fit refuses, naming the file and the field."""
    rel = f"{TRIALS_REL}/{trial_id}.yaml"
    try:
        data = load_yaml_unique((root / rel).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        raise _refuse(f"the trial {rel} cannot be read, is not YAML, or writes a key twice") from None

    def bad(field: str, why: str) -> GovError:
        return _refuse(f"the trial {rel} does not fit this launch: its {field} {why}")

    if not isinstance(data, dict):
        raise _refuse(f"the trial {rel} is not a map")
    for key in sorted(TRIAL_KEYS - set(data)):
        raise bad(key, "is missing")
    for key in sorted(map(str, set(data) - TRIAL_KEYS)):
        raise bad(key, f"is not a field of a trial ({', '.join(sorted(TRIAL_KEYS))})")
    if data["role"] != role:
        raise bad("role", f"is {data['role']!r}, not the launch's {role!r}")
    if data["criticality"] not in crit.CLASSES:
        raise bad("criticality", f"is not one of {', '.join(crit.CLASSES)}")
    if data["criticality"] != ticket_class:
        raise bad("criticality", f"is {data['criticality']}, not the ticket's {ticket_class}")
    if not isinstance(data["model"], str) or not re.fullmatch(roles.MODEL, data["model"]):
        raise bad("model", "is not a model id (claude-...)")
    if data["effort"] not in roles.EFFORTS:
        raise bad("effort", f"is not one of {', '.join(roles.EFFORTS)}")
    tickets = data["tickets"]
    if not isinstance(tickets, list) or len(tickets) < 2 or not all(isinstance(t, str) and t for t in tickets) \
            or len(set(tickets)) != len(tickets):
        raise bad("tickets", "is not a list of two or more distinct ticket ids")
    if not set(tickets) & set(names):
        raise bad("tickets", f"does not include this launch's ticket {names[0]}")
    reviewer = data["reviewer"]
    if not isinstance(reviewer, dict) or set(reviewer) != {"model"} or not isinstance(reviewer["model"], str) \
            or not crit.OPUS.fullmatch(reviewer["model"]):
        raise bad("reviewer", "is not a map holding one Opus model (claude-opus-...)")
    return {"model": data["model"], "effort": data["effort"]}


def _rubric(root: Path, role: str, ticket_id: str, ticket: dict, loaded: dict, given: dict, reason: str | None,
            trial_id: str | None, owner_named: str | None) -> dict:
    """W2-184, RUBRIC-2 at launch (DEC-1120): the session's model and effort and where each came from, the ticket's
    criticality, the promotion, the review round and the other record keys. Every refusal comes here, before the gate
    and before any record or session is made."""
    table, profile = loaded["by_criticality"], ticket.get("profile")
    names = _ticket_names(ticket_id, ticket)
    if not crit.exists(root):
        # 1.4 (amended 2026-11-14): no criticality.yaml, the launch as before W2-184 (DEC-1167 (2)): the role's default
        # line for every class; no promotion, no review count, no probe, no same-setting refusal; a trial needs the file
        if trial_id is not None:
            raise _refuse(f"--trial {trial_id} is refused: a trial needs the ticket's criticality, and {crit.REL} is "
                          f"not there")
        counted, review_round, probe, promotion, opus, ticket_class = [], None, False, None, None, None
        table_model, table_effort, table_source = loaded["model"], loaded["effort"], "role default"
    else:  # the file is read on every worker launch; one that cannot be read or is malformed refuses (1.3)
        ticket_class = crit.ticket_criticality(root, ticket)
        launches = _launch_records(root)  # every launch reads the folder, for 5.1a's roots and 6.1's count (P-td5-1)
        promotion = _promotion(root, names, launches)
        if promotion is not None and trial_id is not None:
            raise _refuse(f"--trial {trial_id} is refused: a promotion applies to {ticket_id} ({promotion['reason']}, "
                          f"{promotion['record']}), and a lower model is refused (DEC-1120 (3))")
        counted, review_round = [], None
        if role == AUDITOR and profile == "FULL":
            counted = _counted_reviews(launches, names, given["resume"])
            review_round = len(counted) + 1
        probe = review_round is not None and review_round >= 2
        opus = crit.opus_model(root) if promotion is not None or probe else None
        if table is not None:
            table_model, table_effort = table[ticket_class]["full" if profile == "FULL" else "other"]
            table_source = "by criticality"
        else:
            table_model, table_effort, table_source = loaded["model"], loaded["effort"], "role default"
    trial = _trial(root, trial_id, role, ticket_class, names) if trial_id is not None else None

    # the model: promotion, trial, probe (only where it changes the model), then the table's
    if promotion is not None:
        model, model_source, why = opus, "promotion", f"a promotion applies ({promotion['reason']})"
    elif trial is not None:
        model, model_source, why = trial["model"], "trial", f"the trial {trial_id}'s"
    elif probe and opus != table_model:
        model, model_source, why = opus, "probe", f"the second review is the probe ({opus})"
    else:
        model, model_source, why = table_model, table_source, f"the {role}'s for criticality {ticket_class}"
    exception = None
    if given["model"] is not None:
        if given["model"] != model:
            # W2-201 S4 (DEC-1212 (2), DEC-1214 K1): another model only by an entry of the exceptions file, and only
            # where the table decides: a promotion, a trial and the probe stay as they are
            shown = ticket_class if ticket_class is not None else f"none (no {crit.REL})"
            refusal = (f"the CLI arguments carry --model {given['model']}, which is not the session's model {model} "
                       f"({why}; the ticket's class is {shown}) (DEC-839 item 1, DEC-1120 (3)); another model comes "
                       f"only from an exception in {model_exceptions.REL} (DEC-1212 (2))")
            substituted = roles.substitution_active(root)
            if substituted and model_exceptions.names_opus(given["model"]):
                # W2-201 S9 (DEC-1215): as the helper hook refuses an Opus spawn, whatever the exceptions file holds
                raise _refuse(f"the CLI arguments carry --model {given['model']}: while the owner's temporary "
                              f"substitution is active (DEC-1215, {roles.SUBSTITUTION_REL}) every Opus role runs "
                              f"Claude Fable 5.2 instead; name no model, or 'fable' (claude-fable-5-2) where an "
                              f"exception in {model_exceptions.REL} covers it")
            if model_source != table_source:
                raise _refuse(refusal)
            try:
                entry = model_exceptions.find(root, role, given["model"], ticket_class, substituted)
            except GovError as error:
                raise _refuse(f"{refusal}: {error.message}") from None
            if entry is None:
                raise _refuse(f"{refusal}: it holds none for '{role}' with that model"
                              f"{' and class' if ticket_class is not None else ''}")
            model, model_source, exception = given["model"], "exception", str(entry.get("decided"))
        elif model_source == table_source:
            model_source = "after --"

    # the effort: trial, after --, probe, then the table's
    own = True
    if trial is not None:
        if given["effort"] is not None and given["effort"] != trial["effort"]:
            raise _refuse(f"the CLI arguments carry --effort {given['effort']}, which is not the trial "
                          f"{trial_id}'s effort {trial['effort']}")
        effort, effort_source = trial["effort"], "trial"
    else:
        if given["effort"] in BELOW_FLOOR and table_effort not in BELOW_FLOOR:
            raise _refuse(f"the CLI arguments carry --effort {given['effort']}, below the floor '{FLOOR}' of "
                          f"{role}'s {table_effort} (DEC-1120 (3))")
        resolved = "max" if probe else table_effort  # interface 3.2a: the effort already resolved for this launch
        if given["effort"] is not None:
            effort, effort_source = given["effort"], "after --"
            if effort == resolved:  # not the launch's own choice: needs no --reason; the probe's max stays `probe`
                own = False
                if probe:
                    effort_source = "probe"
        elif probe:
            effort, effort_source, own = "max", "probe", False
        else:
            effort, effort_source, own = table_effort, table_source, False
    if effort == "max" and own and reason is None:
        raise _refuse(f"an effort of max that the launch chooses ({effort_source}) needs --reason \"<text>\" "
                      f"(DEC-1120 (3))")
    repeated = next((e for e in counted if (e["model"], e["effort"]) == (model, effort)), None)
    if review_round is not None and review_round >= 3 and owner_named is None:
        # 6.3 as amended: at most two review rounds, whatever the setting (DEC-1010); a repeated setting is named too
        also = (f"; its setting, model {model}, effort {effort}, repeats the review of session "
                f"{repeated['session_id']}") if repeated is not None else ""
        raise _refuse(f"review round {review_round} of {ticket_id} is refused: at most two review rounds "
                      f"(DEC-1010){also}; a third or later needs --owner-named <DEC-id>")
    if repeated is not None and owner_named is None:  # DEC-1010: the same setting twice only when the owner named it
        raise _refuse(f"the review of session {repeated['session_id']} ran on model {model}, effort {effort}, "
                      f"the setting this launch would repeat: it needs --owner-named <DEC-id> (DEC-1010)")
    return {"model": model, "effort": effort, "model_source": model_source, "effort_source": effort_source,
            "tier": (model.split("-") + [model])[1], "criticality": ticket_class, "exception": exception,
            "rubric": crit.REL if crit.exists(root) else None,  # W2-121c RT-8: the file the choice came from
            "trial": trial_id, "promotion": promotion, "effort_reason": reason, "owner_named": owner_named,
            "review_round": review_round}


def _worker_plan(root: Path, role: str, ticket_id: str, given: dict, template: list[str], settings: dict,
                 options: tuple = (None, None, None), projection_usd: float | None = None) -> dict:
    """W2-60a, before the gate: the role read once, its model and effort, the resumed session's record, and the
    settings a worker session gets on top of ``build_settings`` (the record folder's deny rules, the user's ask and
    deny rules, no model-side memory, the subagent model in its env). What ``_launch_line`` needs once the session's
    temp folder exists is returned; any refusal comes here, before anything but the record folder is made."""
    loaded = roles.read_role(root, role)
    ticket = _load_ticket(str(root), ticket_id) or {}
    chosen = _rubric(root, role, ticket_id, ticket, loaded, given, *options)  # W2-184: every launch-setting refusal
    model, effort = chosen["model"], chosen["effort"]
    template_path = Path(template[1])
    try:
        template_bytes = template_path.read_bytes()
    except OSError:
        raise GovError("LAUNCH_NO_TEMPLATE", f"the role template {template_path} cannot be read: no '{role}' "
                                             f"session starts without it (DEC-1050)") from None
    user_rules = roles.user_rules(Path.home())  # the ask and deny rules --setting-sources project,local would drop
    ticket_class = ticket.get("class")
    records = record.folder(root)
    # Corrections to Behaviour 8: a resumed, forked session keeps its original's prompt, so its record holds that.
    resumed = record.original(records, given["resume"], role, ticket_id) if given["resume"] else None
    deny = settings["permissions"]["deny"]
    # The user's ask and deny rules only: never an allow rule or a mode, which would take a protection away.
    settings["permissions"]["deny"] = _worker_deny(deny, user_rules["deny"])
    if user_rules["ask"]:
        settings["permissions"]["ask"] = list(dict.fromkeys(user_rules["ask"]))
    settings["autoMemoryEnabled"] = False  # DEC-826 Q5: no model-side memory
    # DEC-839 item 3: in the env the launcher owns, so gov.launch.environ passes it to --settings and the CLI process
    settings["env"]["CLAUDE_CODE_SUBAGENT_MODEL"] = model
    composed = _composed(loaded["appended"], template_bytes)
    template_entry = {"path": str(template_path), "sha256": roles.sha256(template_bytes)}
    origin = resumed or {"role_text": loaded["role_text"], "skills": loaded["skills"],
                         "appended_sha256": roles.sha256(composed), "template": template_entry}
    return {"role": role, "ticket": ticket_id, "root": root, "given": given, "model": model, "effort": effort,
            "ticket_class": ticket_class, "chosen": chosen, "records": records, "resumed": resumed is not None, "origin": origin,
            "composed": composed, "projection_usd": projection_usd}


def _launch_line(plan: dict, tmpdir: str, cli: Path) -> tuple[list[str], list[str], Path]:
    """W2-60a, once the temp folder exists: the appended file written, the launch record written before the session
    starts and keyed by its id, and the launcher's own arguments: those before the caller's, and the one appended
    file after them (W2-153's place). The record's path is returned, for its removal when the session cannot start."""
    given, model, effort, chosen = plan["given"], plan["model"], plan["effort"], plan["chosen"]
    appended = Path(tmpdir) / f"role-{plan['role']}.md"
    appended.write_bytes(plan["composed"])
    session_id = str(uuid.uuid4())
    origin = plan["origin"]
    data = {
        "record": "gov-launch", "format": record.FORMAT, "session_id": session_id,
        "resumes": given["resume"], "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root": str(plan["root"]), "role": plan["role"], "ticket": plan["ticket"], "ticket_class": plan["ticket_class"],
        "model": model, "model_source": chosen["model_source"], "tier": chosen["tier"],
        "effort": effort, "effort_source": chosen["effort_source"], "criticality": chosen["criticality"],
        "trial": chosen["trial"], "promotion": chosen["promotion"], "effort_reason": chosen["effort_reason"],
        "owner_named": chosen["owner_named"], "review_round": chosen["review_round"],
        "rubric": chosen.get("rubric"),  # W2-121c RT-8: the rubric file the choice came from, or null
        "exception": chosen.get("exception"),  # W2-201 S4: the exceptions entry's decided text, or null
        "cache_ttl": WORKER_CACHE_TTL,  # W2-201 S7: the worker's cache setting (CLAUDE_CODE_PROMPT_CACHE_TTL)
        "subagent_model": model, "compaction_threshold": "none",
        "role_text": origin["role_text"], "appended_sha256": origin["appended_sha256"],
        "template": origin.get("template"), "skills": origin["skills"], "kept_out": KEPT_OUT,
        "cli": {"path": f"~/{CLI_REL}", "version": record.cli_version(cli)}}
    if plan.get("projection_usd") is not None:  # W2-156: the runaway brake's projection; absent, the key is absent
        data["projection_usd"] = plan["projection_usd"]
    written = record.write(plan["records"], data)
    head = [*OWN_SWITCHES, *plan.get("mode", []), *([] if given["model"] else ["--model", model]),
            *([] if given["effort"] else ["--effort", effort]), "--session-id", session_id,
            *(["--fork-session"] if plan["resumed"] else [])]
    return head, [TEMPLATE_FLAG, str(appended)], written


def _end_message(entry: dict | None, code) -> None:
    """W2-121c RT-2: the session's end as one wake message to whoever launched it, with the id the watch pass gives
    the same end. Best effort: a failed send is said on stderr and never changes the exit code or the launch."""
    if entry is None:
        return
    try:
        from gov.dispatch import inbox, runtime
        role, ticket = entry.get("role"), entry.get("ticket")
        inbox.send(entry["notify"], "wake", f"session {role} {ticket} ended with exit code {code}",
                   sender=entry["address"], message_id=runtime.end_id(entry),
                   data={"role": role, "ticket": ticket, "pid": entry.get("pid"), "exit_code": code,
                         "repository": entry.get("repository")})
    except Exception as error:  # noqa: BLE001 - nothing here may end the launch
        _say(f"gov launch: the end message to {entry.get('notify')} could not be sent: "
             f"{' '.join(str(getattr(error, 'message', error)).split())}\n")


def _notify_address() -> str:
    """Whoever launched: the launching process's ``$GOV_MSG_ADDRESS`` when it is an address, else ``cto``."""
    from gov.dispatch import inbox
    given = os.environ.get("GOV_MSG_ADDRESS")
    try:
        return inbox.check(given) if given else "cto"
    except inbox.InboxError:
        return "cto"


def check_lead(root: Path, ticket_id: str):
    """The plan's check of a lead (W2-136 S9): ``gov.launch.plan_check.check_lead``, looked up when called."""
    from gov.launch import plan_check
    return plan_check.check_lead(root, ticket_id)


def _say(line: str) -> None:
    """One line to stderr. A stderr that is closed or that nobody reads loses the line and nothing else (DEC-392):
    the line goes past the stream's buffer, since what stays in it changes the exit code when the interpreter ends."""
    stream = sys.stderr
    if stream is None:  # the launcher was started without a stderr
        return
    try:
        try:
            descriptor = stream.fileno()
        except io.UnsupportedOperation:  # a stream of the caller's that has no descriptor
            stream.write(line)
            return
        stream.flush()
        os.write(descriptor, line.encode(errors="replace"))
    except (OSError, ValueError):
        pass


def _admit_lead(root: Path, ticket_id: str) -> tuple[str, str] | None:
    """W2-136 S9 (DEC-1088 (5)(a)): a lead only for a planned ticket whose waits are met. A plan override's
    ``(decision, reason)`` is returned, for ``_record_plan_override`` once the gate admits the launch too (review F8):
    a lead the gate refuses leaves no override line."""
    verdict = check_lead(root, ticket_id)
    if isinstance(verdict, tuple) and len(verdict) == 3:
        verdict = dict(zip(("admitted", "reason", "override"), verdict))
    field = verdict.get if isinstance(verdict, dict) else lambda name: getattr(verdict, name, None)
    if not field("admitted"):
        raise _refuse(f"no lead for ticket '{ticket_id}': {field('reason')} (DEC-1088 (5))")
    return (field("override"), field("reason")) if field("override") else None


def _record_plan_override(ticket_id: str, override: tuple[str, str] | None) -> None:
    """A plan override that admitted a lead: one line in the machine-wide launch log and one on standard error
    (W2-20 S21, W2-136 review F4, P-8)."""
    from gov.launch.gate import record

    if override is None:
        return
    decision, reason = override
    record(f"gov launch: OVERRIDE plan_override: {decision}: ticket {ticket_id}: {reason} (DEC-899)")
    _say(f"gov launch: OVERRIDE {decision}: {reason} (DEC-899)\n")


def _admit_start(root: Path, role: str, ticket_id: str, gate_override: str | None, gpu_need_mib: int | None) -> None:
    """W2-20 S19 (DEC-1088 (5)(b)): no session, lead or worker, while the resource gate is shut on any reading; one
    recorded override (``--gate-override DEC-NNN``) starts it anyway, written to the launch log and standard error."""
    from gov.launch.gate import GATE_SHUT, check_start, override_decision, record, shut_text

    decision = override_decision(gate_override)
    if gpu_need_mib is not None and (isinstance(gpu_need_mib, bool) or not isinstance(gpu_need_mib, int)
                                     or gpu_need_mib < 1):
        raise _refuse(f"--gpu-need-mib takes a positive number of MiB, not {gpu_need_mib!r}")
    try:
        check_start(gpu_need_mib=gpu_need_mib)
    except GovError as shut:
        if shut.code != GATE_SHUT:
            raise _refuse(f"the resource gate cannot be read: {shut.message} (DEC-1088 (5))") from None
        text = shut_text(shut.details)
        if decision is None:
            raise GovError("LAUNCH_REFUSED", f"the resource gate is shut: {text} (DEC-1088 (5))",
                           shut.details) from None
        line = (f"gov launch: OVERRIDE gate_override: {decision}: {role} {ticket_id} started with the resource gate "
                f"shut: {text} (DEC-899)")
        record(line)
        _say(line + "\n")


def _cli() -> Path:
    cli = Path.home() / CLI_REL
    if not cli.is_file():
        raise _refuse(f"the CLI is not at ~/{CLI_REL} (DEC-205)")
    return cli


def _check_worker_role(role: str) -> None:
    """The role's name only, before anything is read (W2-60b): a plain role name, the stem of a role file. Whether it
    is a worker is its role file's to say (``_role_kind``)."""
    if not isinstance(role, str) or not ROLE_NAME.fullmatch(role):
        raise _refuse(f"'{role}' is not a worker role: a role is the name of its role file (lower-case letters, digits "
                      f"and '-'), and a lead role is {' or '.join(LEAD_ROLES)}")


def tests_worktree(root: Path, role: str, ticket_id: str) -> int:
    """W2-60b S10 (DEC-847, DEC-963, DEC-982): ``gov launch independent-test-designer <ticket> --tests-worktree``, run
    in the ticket's worktree, makes the tests worktree ``<tree>-tests`` on a new branch ``<tree's branch>-tests`` at the
    tree's ``HEAD``, prints its path and returns 0. No session starts, nothing is recorded or gated. An existing path or
    branch, a tree on no branch, or a ticket that is unknown or not ``in_progress`` refuses."""
    root = Path(os.path.realpath(root))
    if role != "independent-test-designer":
        raise _refuse(f"--tests-worktree makes the independent test designer's own tree, not one for '{role}' "
                      f"(DEC-963)")
    ticket = _load_ticket(str(root), ticket_id)
    if ticket is None:
        raise _refuse(f"unknown ticket '{ticket_id}'")
    if ticket.get("status") != "in_progress":
        raise _refuse(f"ticket '{ticket_id}' is not in_progress (status: {ticket.get('status')})")
    git, env = git_binary() or "git", git_env(root)

    def run(*argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([git, "-C", str(root), *argv], capture_output=True, text=True, env=env, check=False)

    head = run("symbolic-ref", "--quiet", "--short", "HEAD")
    if head.returncode != 0 or not head.stdout.strip():
        raise _refuse(f"the tree {root} is on no branch, so its tests branch cannot be named")
    branch, path = head.stdout.strip() + TESTS_SUFFIX, Path(f"{root}{TESTS_SUFFIX}")
    if os.path.lexists(path):
        raise _refuse(f"the tests worktree's path {path} is already there")
    if run("show-ref", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0:
        raise _refuse(f"the tests worktree's branch {branch} is already there")
    made = run("worktree", "add", "-b", branch, str(path), "HEAD")
    if made.returncode != 0:
        why = (made.stderr.strip().splitlines() or ["no message"])[-1]
        raise _refuse(f"git could not make the tests worktree {path} on the branch {branch}: {why}")
    print(path)
    return 0


def plan(root: Path, role: str, ticket_id: str) -> int:
    """``gov launch --plan <role> <ticket>`` (W2-60a, routed from W2-33 S2; DEC-1167 (2)): print the one line
    ``model <id>, effort <e>`` of the role file's default line and return 0. A worker's role and ticket are checked as a
    launch checks them; nothing is started, made or gated. A lead reads no role file, so it has no plan here."""
    root = Path(os.path.realpath(root))
    if role in LEAD_ROLES:
        raise _refuse(f"a '{role}' session is started without a role file's default line, so it has no plan")
    _role_kind(root, role)
    _check_ticket(root, role, ticket_id)
    model, effort = roles.launch_default(root, role)
    print(f"model {model}, effort {effort}")
    return 0


def launch(root: Path, role: str, ticket_id: str, cli_args: list[str], gate_override: str | None = None,
           gpu_need_mib: int | None = None, *, reason: str | None = None, trial: str | None = None,
           owner_named: str | None = None, projection_usd: float | None = None) -> int:
    """Start one worker or lead session and return the CLI's exit code; raise ``GovError`` to refuse.

    A worker's ``projection_usd`` (``--projection-usd``, W2-156) is recorded on its launch record: the runaway brake's
    projection. A braked ticket's launch is refused (``SPEND_BRAKED``) after the gate's check; a lead takes no projection.

    Only a lead (``role`` in ``LEAD_ROLES``) is checked against the plan; a worker launch never is, whoever calls.
    Every launch, lead or worker, passes the resource gate (W2-20 S19), unless ``gate_override`` (a decision id)
    starts it anyway; ``gpu_need_mib`` is the session's declared GPU need. The started session is entered in the
    machine-wide registry while it runs (W2-20 S1). A worker's ``reason`` (``--reason``), ``trial`` (``--trial``) and
    ``owner_named`` (``--owner-named``) are RUBRIC-2's options (W2-184, DEC-1120); a lead takes none of them.

    The machine-wide start lock is held from the gate's check until the session is registered (review F1): launches
    that start together are judged one after another, each with the sessions started before it counted, and one that
    ends before registering leaves no entry.
    """
    from gov.launch.gate import StartLock

    root = Path(os.path.realpath(root))
    if role in LEAD_ROLES:
        # W2-184 R1 (interface 10.1): the second fence behind the CLI's exit 2, before anything is read or started
        given = [flag for flag, value in (("--reason", reason), ("--trial", trial), ("--owner-named", owner_named))
                 if value is not None]
        if given:
            raise _refuse(f"a lead launch ({role}) takes none of --reason, --trial and --owner-named; given: "
                          f"{', '.join(given)}")
        if projection_usd is not None:  # W2-156: a lead writes no launch record, so it has nowhere to keep one
            raise _refuse(f"a lead launch ({role}) takes no --projection-usd: it writes no launch record to hold one")
        _check_not_paused(root)
        plan_override = _admit_lead(root, ticket_id)
        _check_cli_args(cli_args)
        _check_repository_settings(root, False)
        template = template_args(root, role)
        cli = _cli()
        settings = build_lead_settings(root, ticket_id)  # an unusable store setting refuses here, before the gate
        lock = StartLock()
        try:
            _admit_start(root, role, ticket_id, gate_override, gpu_need_mib)
            _record_plan_override(ticket_id, plan_override)  # only once the gate admits it too (review F8)
            # DEC-743 7: a ticket lead has no own folder under ~/gov-os-runs; the dispatcher gives a lead no temp folder.
            return _run(root, cli, settings, [*_mode_args(cli_args), *cli_args, *template],
                        entry=(ticket_id, LEAD_GOV_ROLE), lock=lock)
        finally:
            lock.release()
    _check_worker_role(role)
    _check_cli_args(cli_args)
    given = _check_own_args(cli_args)
    _check_options(reason, trial, owner_named)
    _check_projection(projection_usd)
    _check_ticket(root, role, ticket_id)
    _check_not_paused(root)
    _check_repository_settings(root)
    if role not in ROLE_TEMPLATES:  # W2-60b S8: a new role's file before its template is looked for
        _role_kind(root, role)
    template = template_args(root, role)
    cli = _cli()
    # W2-60b S7: the role file says the role is a worker; today's refusals above come first (W2-60a Behaviour 10)
    _role_kind(root, role)
    # W2-60b S10, S12 (DEC-847, DEC-963, DEC-1156 (3)): no second writer in a worktree. Here, a planted or long-live
    # writer refuses before anything is written; the check that decides is made again under the start lock below.
    session_record.check_one_writer(root, str(root), role)
    session_record.make_folder(root)  # before the settings, so every launch's runtime rules are the same (W2-56 S3)
    settings = build_settings(root, role, ticket_id)
    # W2-60a: the role read once; W2-184: the session's model and effort are RUBRIC-2's for its role and criticality.
    plan = _worker_plan(root, role, ticket_id, given, template, settings, (reason, trial, owner_named), projection_usd)
    plan["mode"] = _mode_args(cli_args)
    lock = StartLock()
    try:
        # W2-60b review round 1, F1: the one-writer check under the start lock. A writing launch writes its start
        # record (Keeper.begin, in _run) before it gives the lock back, so a launch that takes the lock after it sees
        # it live; two launches that start together, or wait together on a lock a third party holds, are judged one
        # after the other. A refusal here starts no CLI and writes no record of its own.
        session_record.check_one_writer(root, str(root), role)
        _admit_start(root, role, ticket_id, gate_override, gpu_need_mib)
        braked = spend_brake.refusal(root, ticket_id)  # W2-156 (DEC-1091 (2)): after the gate, before anything starts
        if braked is not None:
            raise GovError("SPEND_BRAKED", braked)
        # DEC-728, DEC-743 (R2): the session's own folder under ~/gov-os-runs, made before the session starts and
        # never removed by the launcher; what it holds is left alone, and no other folder is made. DEC-751 1: only a
        # folder made here is marked as this repository's; a folder that is there without this repository's marker,
        # or that cannot be named, made or marked, is not opened: the session then has none.
        name = runs.folder(str(root), ticket_id, role)
        if name is not None and not os.path.lexists(name):
            runs.make(name, str(root))
        own = runs.own_folder(str(root), ticket_id, role)
        # W2-60a: the appended file (the role's text, then the template) and the record are made in _run
        return _run(root, cli, settings, cli_args, temp_prefix=TEMP_PREFIX, own=own, entry=(ticket_id, role),
                    lock=lock, worker=plan)
    finally:
        lock.release()


def _run(root: Path, cli: Path, settings: dict, cli_args: list[str], *, temp_prefix: str | None = None,
         own: str | None = None, entry: tuple[str, str] | None = None, lock=None, worker: dict | None = None) -> int:
    """Start the session and wait for it. With ``temp_prefix`` (a worker), the session gets a temp folder of its
    own, in its env, removed when it ends (DEC-159, DEC-386). With
    ``entry`` (its ticket and role), the session is in the machine-wide registry while it runs (W2-20 S1): one that
    cannot be entered is stopped, so the gate never runs blind to a session. ``lock`` (the machine-wide start lock,
    review F1) is given back once the session is registered, or when the launch ends without one. With ``worker``
    (``_worker_plan``'s, W2-60a), the appended file and the launch record are written in the temp folder's time,
    just before the session starts, and the record is removed when it cannot be started."""
    from gov.resources import registry

    state = {"session": None, "ended": False, "asked": False, "registered": None, "deadline": None, "code": None,
             "entry": None}
    keeper = None  # W2-60b: the session record's two calls, for a worker session with its launch record
    relay = None  # W2-60b S2: the session's stdout relayed, for its result line, when it runs --output-format json

    def end(signum=None, frame=None):
        """DEC-392: an interrupt, SIGTERM or SIGHUP ends the session's whole process group (W2-56 S12). It is asked
        first, and killed when a second signal arrives or it still runs END_WAIT_S later. Nothing is raised here, so
        no clean-up is cut short."""
        session, asked = state["session"], state["asked"]
        state["ended"] = True
        if session is not None and (session.poll() is None or _group_alive(session)):
            state["asked"] = True
            if asked:
                _signal_session(session, signal.SIGKILL)
            else:
                _signal_session(session, signal.SIGTERM)
                state["deadline"] = time.monotonic() + END_WAIT_S
                signal.alarm(END_WAIT_S)

    previous = {number: signal.signal(number, end) for number in END_SIGNALS
                if signal.getsignal(number) is not signal.SIG_IGN}  # a signal the caller ignores stays ignored
    alarm, tmpdir, code, terminal = signal.signal(signal.SIGALRM, end), None, INTERRUPT_EXIT, None
    try:
        own_env = dict(settings["env"])
        if temp_prefix is not None:  # DEC-159: a temp directory of the session's own, for the CLI and its commands
            tmpdir = tempfile.mkdtemp(prefix=temp_prefix)
            own_env.update({"TMPDIR": tmpdir, "CLAUDE_CODE_TMPDIR": tmpdir})
        # W2-56 S5: the cleaned environment for the CLI process (gov.launch.environ), and in a worker's --settings (a
        # lead's keeps its role, ticket and store alone, W2-136 S9, W2-56 R5)
        settings["env"] = environ.settings_env(os.environ, own_env) if temp_prefix is not None else own_env
        env = environ.session_env(os.environ, own_env)
        address = f"{entry[1]}:{entry[0]}" if entry is not None else None
        if address is not None:  # W2-121c RT-2: the session's own inbox address, in its process's environment
            env["GOV_MSG_ADDRESS"] = address
        if not state["ended"]:  # a signal that came first: no session is started
            head, tail, written = [], [], None
            if worker is not None:  # W2-60a: the record before the session starts; the appended file last (W2-153)
                head, tail, written = _launch_line(worker, tmpdir, cli)
            terminal = _terminal()
            piped = _relays(worker, cli_args)
            try:  # W2-56 S12: the session leads a process group of its own, which the ending signals reach
                state["session"] = _start([str(cli), "--settings", json.dumps(settings), *head, *cli_args, *tail],
                                          root, env, terminal, piped)
            except (OSError, SubprocessError):
                if written is not None:
                    record.remove(written)
                raise _refuse(f"the CLI at ~/{CLI_REL} cannot be started (DEC-205)") from None
            if written is not None:  # W2-60b S1: the session record, whole, once the session's process has started,
                # and first, before the start lock can be given back by any path (review round 1, F1)
                keeper = session_record.Keeper(root, written, worktree=str(root), pid=os.getpid(), say=_say,
                                               config=session_record.config_folder())
                keeper.begin()
            source = getattr(state["session"], "stdout", None) if piped else None
            if source is not None:  # a stand-in that starts no process has no pipe: nothing to relay
                relay = _Relay(source.fileno())
            pid = getattr(state["session"], "pid", None)  # a started process always has one
            if entry is not None and isinstance(pid, int) and pid > 0:
                try:
                    state["entry"] = registry.register(pid, root, *entry, notify=_notify_address(), address=address)
                    state["registered"] = pid
                except (OSError, GovError) as error:
                    raise _refuse(f"the session cannot be entered in the machine-wide registry "
                                  f"({getattr(error, 'message', error)}): it is stopped (W2-20)") from None
            if lock is not None:  # registered: the next launch's check counts this session (review F1)
                lock.release()
            if state["ended"]:  # a signal that came while the session was started
                end()
            if relay is not None:  # relayed through DEC-392's endings too: the handler never stops it
                relay.pump(lambda: state["session"].poll() is None)
            code = state["session"].wait()
            _end_group(state)  # W2-56 S12: what the session left in its group ends with it
            if relay is not None:  # what the session wrote before it ended, to the pipe's end
                relay.drain(END_WAIT_S)
            if state["ended"]:
                code = INTERRUPT_EXIT
            state["code"] = code
        return code
    finally:
        session = state["session"]
        if session is not None and session.poll() is None:  # only an error on the way here: no session is left
            _signal_session(session, signal.SIGKILL)
            session.wait()
        if session is not None and _group_alive(session):
            _signal_session(session, signal.SIGKILL)
        if relay is not None:  # W2-60b S2: the last line, and the pipe given back; the result line for the record
            try:
                relay.close()
                session.stdout.close()
            except (OSError, ValueError, AttributeError):
                pass
            if keeper is not None:
                keeper.result = relay.result
        if keeper is not None:  # W2-60b S1, S5: replaced whole by every ending; it never changes the exit code
            keeper.end(state["code"] if state["code"] is not None else getattr(session, "returncode", None))
        _end_message(state["entry"], state["code"] if state["code"] is not None else getattr(session, "returncode",
                                                                                            None))
        if terminal is not None:
            _take_terminal(terminal)
        if state["registered"] is not None:
            registry.unregister(state["registered"])
        if lock is not None:
            lock.release()
        # DEC-386, W2-56 S15: the folder goes when the session ends, whole; a link in it is removed as a link.
        try:
            if tmpdir is not None:
                _remove(tmpdir)
        except OSError as error:  # DEC-392: the session's exit code is kept, and one line names what stayed
            _say(f"gov launch: the temp folder {tmpdir} could not be removed and stays: "
                 f"{' '.join(str(error).split())}\n")
        for number, handler in previous.items():
            signal.signal(number, handler or signal.SIG_DFL)
        signal.alarm(0)
        signal.signal(signal.SIGALRM, alarm or signal.SIG_DFL)


OUTPUT_FORMAT = "--output-format"
RELAY_CHUNK = 65536
RESULT_LINE_MAX = 64 * 1024 * 1024  # a longer line is relayed whole but not parsed: its result is not measured


def _json_output(cli_args: list[str]) -> bool:
    """W2-60b S2: the session runs with ``--output-format json`` (spaced or ``=`` form; the last one given counts, as
    the CLI takes it)."""
    value = None
    for index, arg in enumerate(cli_args):
        if arg == OUTPUT_FORMAT:
            value = cli_args[index + 1] if index + 1 < len(cli_args) else None
        elif arg.startswith(OUTPUT_FORMAT + "="):
            value = arg.split("=", 1)[1]
    return value == "json"


def _relays(worker: dict | None, cli_args: list[str]) -> bool:
    """A worker session (which has a session record to read the result line into) run with ``--output-format json``.
    A lead's stdout, and every other run's, stays inherited as before (S7)."""
    return worker is not None and _json_output(cli_args)


class _Relay:
    """W2-60b S2 (the result line when the session ran with ``--output-format json``): every byte the session writes
    to its stdout pipe goes, unchanged and in order, to the launcher's own stdout (``out``) as it arrives; the last
    complete line that parses as a JSON object of ``"type": "result"`` is kept in ``result`` (a last line with no
    newline counts when it parses whole). Nothing is added, dropped or reordered. When ``out`` cannot be written, one
    line is said and the pipe is still read to its end, so the session is never blocked and its exit code is its own;
    when the pipe cannot be read, one line is said and the relay stops. The result line's text never leaves here but
    as ``result``, which the session record reads counts from (S3)."""

    def __init__(self, source: int, out: int = 1, say=None):
        self.source, self.out, self.say = source, out, say or _say
        self.partial, self.overlong, self.result = bytearray(), False, None
        self.writable, self.done, self.said = True, False, False
        try:
            sys.stdout.flush()  # what the launcher printed itself goes first
        except (OSError, ValueError, AttributeError):
            pass

    def _fail(self, what: str, error: BaseException) -> None:
        if not self.said:
            self.said = True
            why = " ".join(str(getattr(error, "strerror", None) or error).split()) or type(error).__name__
            self.say(f"gov launch: the session's stdout {what} ({why}); the session's exit code is kept (DEC-392)\n")

    def _write(self, data: bytes) -> None:
        view = memoryview(data)
        while view and self.writable:
            try:
                view = view[os.write(self.out, view):]
            except BlockingIOError:  # a non-blocking stdout: wait until it takes more
                select.select([], [self.out], [], 1.0)
            except (OSError, ValueError) as error:
                self.writable = False
                self._fail("cannot be relayed to the launcher's stdout, and the rest of it is lost", error)

    def _consider(self, line: bytes) -> None:
        line = line.strip()
        if not line.startswith(b"{") or b'"result"' not in line:
            return
        try:
            value = json.loads(line)
        except (ValueError, RecursionError):  # deep nesting raises RecursionError: no result, the relay goes on
            return
        if isinstance(value, dict) and value.get("type") == "result":
            self.result = value

    def _feed(self, data: bytes) -> None:
        self._write(data)
        start = 0
        while (end := data.find(b"\n", start)) != -1:
            if not self.overlong:
                self._consider(bytes(self.partial) + data[start:end])
            self.partial.clear()
            self.overlong, start = False, end + 1
        rest = data[start:]
        if not self.overlong:
            if len(self.partial) + len(rest) > RESULT_LINE_MAX:
                self.partial.clear()
                self.overlong = True
            else:
                self.partial += rest

    def _step(self, timeout: float) -> bool:
        """Read what is ready within ``timeout``; False once the pipe has ended or cannot be read."""
        try:
            ready, _, _ = select.select([self.source], [], [], timeout)
            if not ready:
                return True
            data = os.read(self.source, RELAY_CHUNK)
        except (OSError, ValueError) as error:
            self._fail("cannot be read to relay it", error)
            self.done = True
            return False
        if not data:
            self.done = True
            return False
        self._feed(data)
        return True

    def pump(self, running) -> None:
        """Relay while the session's leader runs (``running()``); what is left is ``drain``'s, after its group ends."""
        while not self.done and running():
            self._step(0.1)

    def drain(self, seconds: float) -> None:
        """Relay what is left until the pipe ends; at most ``seconds`` more, for a process that left the session's
        group and still holds the pipe."""
        deadline = time.monotonic() + seconds
        while not self.done and (left := deadline - time.monotonic()) > 0:
            self._step(min(left, 0.1))

    def close(self) -> None:
        if self.partial and not self.overlong:
            self._consider(bytes(self.partial))
        self.partial.clear()
        self.done = True


def _terminal() -> int | None:
    """Standard input's descriptor when it is a terminal whose foreground group is the launcher's, else None."""
    try:
        if os.isatty(0) and os.tcgetpgrp(0) == os.getpgrp():
            return 0
    except OSError:
        pass
    return None


def _group_options(terminal: int | None) -> dict:
    """``Popen`` options that make the session the leader of a process group of its own (W2-56 S12). On a terminal
    the session's group is also made the terminal's foreground group, so that an interactive session can read it."""
    if terminal is None:
        return {"process_group": 0}

    def foreground() -> None:  # in the child, before the CLI is started
        os.setpgid(0, 0)
        signal.signal(signal.SIGTTOU, signal.SIG_IGN)
        os.tcsetpgrp(terminal, os.getpgrp())
        signal.signal(signal.SIGTTOU, signal.SIG_DFL)

    return {"preexec_fn": foreground}


def _start(argv: list[str], root: Path, env: dict, terminal: int | None, relay: bool = False):
    """The session, started as the leader of its own process group; with ``relay`` (W2-60b S2), its stdout on a pipe
    the launcher relays, else inherited. A ``Popen`` put in the real one's place that takes no process options (the
    suites' in-process stand-ins) is called without them: it starts no process."""
    piped = {"stdout": subprocess.PIPE} if relay else {}
    try:
        return subprocess.Popen(argv, cwd=root, env=env, **_group_options(terminal), **piped)
    except TypeError as error:
        if "unexpected keyword argument" not in str(error):
            raise
        return subprocess.Popen(argv, cwd=root, env=env)


def _take_terminal(terminal: int) -> None:
    """The terminal back to the launcher's group once the session has ended."""
    former = signal.signal(signal.SIGTTOU, signal.SIG_IGN)
    try:
        os.tcsetpgrp(terminal, os.getpgrp())
    except OSError:
        pass
    finally:
        signal.signal(signal.SIGTTOU, former)


def _pgid(session) -> int | None:
    pid = getattr(session, "pid", None)
    return pid if isinstance(pid, int) and not isinstance(pid, bool) and pid > 0 else None


def _group_alive(session) -> bool:
    """True while a process of the session's group runs (its leader, or one it left behind)."""
    pgid = _pgid(session)
    if pgid is None:
        return False
    try:
        os.killpg(pgid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def _signal_session(session, number: int) -> None:
    """``number`` to the session's whole process group; to the session alone when it leads no group."""
    pgid = _pgid(session)
    if pgid is not None:
        try:
            os.killpg(pgid, number)
            return
        except (ProcessLookupError, PermissionError):
            pass
    if session.poll() is None:
        session.kill() if number == signal.SIGKILL else session.terminate()


def _end_group(state: dict) -> None:
    """After the session's leader has ended: the rest of its group is asked to end, and killed when it still runs
    END_WAIT_S after the first ask (D-5: the kill reaches the group, not only a leader that has ended)."""
    session = state["session"]
    if not _group_alive(session):
        return
    if not state["asked"]:
        state["asked"] = True
        _signal_session(session, signal.SIGTERM)
        state["deadline"] = time.monotonic() + END_WAIT_S
    deadline = state["deadline"] if state["deadline"] is not None else time.monotonic()
    while _group_alive(session) and time.monotonic() < deadline:
        time.sleep(0.05)
    if _group_alive(session):
        _signal_session(session, signal.SIGKILL)
        reaped = time.monotonic() + REAP_WAIT_S  # a killed orphan stays in the group until its new parent reaps it
        while _group_alive(session) and time.monotonic() < reaped:
            time.sleep(0.05)


def _remove(folder: str) -> None:
    """The session's temp folder, whole (W2-56 S15): also when it holds folders its owner may not write or list (mode
    0500 or 0000, as a module cache leaves them), a fifo, or a link (removed as a link; its target is untouched)."""
    try:
        if not os.path.islink(folder):
            os.chmod(folder, 0o700)
    except OSError:
        pass
    for here, folders, _files in os.walk(folder):  # links are not followed
        for name in folders:
            path = os.path.join(here, name)
            if not os.path.islink(path):
                try:
                    os.chmod(path, 0o700)
                except OSError:
                    pass
    shutil.rmtree(folder)
