"""Worker session launcher: ``gov launch <role> <ticket> [-- <CLI arguments>]`` (W1-46, DEC-231).

Starts the CLI at ``~/.local/bin/claude`` (DEC-205) in the repository root with
one ``--settings`` value built here: the strict sandbox block, the role's network
profile and ``Edit`` deny rules, the held-out ``Read`` deny rules, ``GOV_ROLE``,
``GOV_TICKET`` and a per-session temp directory. Nothing fails open: whatever
cannot be read or is not of the stated shape refuses the launch.

No message of this module carries a held-out path.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import yaml

from gov.cli.errors import GovError
from gov.guard.decide import FREEZE_FLAG, _load_ticket
from gov.guard.heldout import HeldOutError, load_held_out, load_yaml_unique
from gov.guard.install import experiment_folder

WORKER_ROLES = ("engineer", "independent-test-designer", "independent-auditor", "research")
# Open package DP-8: these roles need a ticket whose ``role`` is their own; the
# two independent roles may be launched on any ``in_progress`` ticket.
OWN_TICKET_ROLES = frozenset({"engineer", "research"})
CLI_REL = ".local/bin/claude"
REPO_SETTINGS = (".claude/settings.json", ".claude/settings.local.json")
RUNTIME, SCRATCH = ".gov-runtime", "scratch"
GUARD_HOOK = "hooks/pretooluse.py"  # the guard, as the repository's settings register it
GUARDED_TOOLS = frozenset({"Write", "Edit", "Bash"})
# Open package DP-9: both files hold a list of host names under this key; the
# project's file extends the kernel default, and may be absent (DEC-241).
ALLOWLIST_KEY = "hosts"
KERNEL_ALLOWLIST_REL = "template/governance/kernel/launch/research-allowlist.yaml"
PROJECT_ALLOWLIST_REL = "governance/project/research-allowlist.yaml"
_HOST = re.compile(r"(\*\.)?[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+")


def _refuse(reason: str) -> GovError:
    return GovError("LAUNCH_REFUSED", reason)


def _hosts(root: Path, rel: str) -> list[str]:
    """The host names of one allowlist file: a name, or ``*.<name>`` for its subdomains."""
    try:
        data = load_yaml_unique((root / rel).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        raise _refuse(f"the research allowlist {rel} cannot be read, or writes a key twice") from None
    hosts = data.get(ALLOWLIST_KEY) if isinstance(data, dict) else None
    if not isinstance(hosts, list) or not all(isinstance(h, str) and _HOST.fullmatch(h) for h in hosts):
        raise _refuse(f"the research allowlist {rel} must hold a list of host names under '{ALLOWLIST_KEY}'")
    return hosts


def _research_allowlist(root: Path) -> list[str]:
    hosts = _hosts(root, KERNEL_ALLOWLIST_REL)
    if os.path.lexists(root / PROJECT_ALLOWLIST_REL):
        hosts += _hosts(root, PROJECT_ALLOWLIST_REL)
    return sorted(set(hosts))


def _runtime_rules(root: Path) -> list[str]:
    """``Edit`` deny rules for ``.gov-runtime/**`` except ``.gov-runtime/scratch/**`` (DEC-180).

    The patterns match every name but ``scratch``; they bind the file tools. The
    Linux sandbox skips a pattern, so the entries that exist at launch and the
    freeze flag are also listed by name.
    """
    base = f"/{root}/{RUNTIME}"
    names = {f"{SCRATCH[:i]}[!{c}]*" for i, c in enumerate(SCRATCH)} | {SCRATCH[:i] for i in range(1, len(SCRATCH))}
    names |= {f"{SCRATCH}?*", os.path.basename(FREEZE_FLAG)}
    if (root / RUNTIME).is_dir():
        names |= {n for n in os.listdir(root / RUNTIME) if n != SCRATCH and not any(c in n for c in "*?[")}
    return [f"Edit({base}/{name})" for name in sorted(names)]


def _fence_rules(root: Path, folder: str) -> list[str]:
    """The research fence: an ``Edit`` deny rule for every entry that exists beside the path to the folder.

    Left out: ``.git`` (the session commits its evidence record), an entry whose
    name the sandbox would read as a pattern, and ``.gov-runtime`` (its own rules).
    """
    rules, here = [], root
    for depth, part in enumerate(Path(folder).relative_to(root).parts):
        for name in sorted(os.listdir(here)):
            if name == part or any(c in name for c in "*?[") or (depth == 0 and name in (".git", RUNTIME)):
                continue
            rules.append(f"Edit(/{here}/{name})")
        here = here / part
    return rules


def build_settings(root: Path, role: str, ticket_id: str) -> dict:
    """The ``--settings`` value of a worker session, less its temp directory. ``root`` is a real path."""
    deny = _runtime_rules(root)
    domains: list[str] = []
    if role == "research":
        folder = experiment_folder(str(root), ticket_id)
        if folder is None:
            raise _refuse("the research ticket's allowed_paths is not exactly one experiment folder (DEC-242)")
        deny += _fence_rules(root, folder)
        domains = _research_allowlist(root)
    try:
        deny += [f"Read(/{path}/**)" for path in load_held_out(str(root))]  # a missing file: no rule (DEC-242)
    except HeldOutError as error:
        raise _refuse(f"{error} (DEC-218)") from None
    return {
        "env": {"GOV_ROLE": role, "GOV_TICKET": ticket_id},
        "permissions": {"deny": deny},
        "sandbox": {
            "enabled": True,
            "failIfUnavailable": True,
            "allowUnsandboxedCommands": False,
            "network": {"strictAllowlist": True, "allowedDomains": domains},
        },
    }


def sandbox_faults(settings: dict) -> list[str]:
    """Why the settings are not on, strict and fail-closed (CAP-61.a); empty when they are."""
    block = settings.get("sandbox")
    block = block if isinstance(block, dict) else {}
    network = block.get("network")
    checks = {
        "sandbox.enabled is not true": block.get("enabled") is True,
        "sandbox.failIfUnavailable is not true": block.get("failIfUnavailable") is True,
        "sandbox.allowUnsandboxedCommands is not false": block.get("allowUnsandboxedCommands") is False,
        "sandbox.network.strictAllowlist is not true":
            isinstance(network, dict) and network.get("strictAllowlist") is True,
        "sandbox.excludedCommands is set (DEC-164)": "excludedCommands" not in block,
    }
    return [fault for fault, holds in checks.items() if not holds]


def _check_ticket(root: Path, role: str, ticket_id: str) -> None:
    ticket = _load_ticket(str(root), ticket_id)
    if ticket is None:
        raise _refuse(f"unknown ticket '{ticket_id}'")
    if ticket.get("status") != "in_progress":
        raise _refuse(f"ticket '{ticket_id}' is not in_progress (status: {ticket.get('status')})")
    if role in OWN_TICKET_ROLES and ticket.get("role") != role:
        raise _refuse(f"ticket '{ticket_id}' is a ticket of another role ('{ticket.get('role')}'), not of '{role}'")


def _guard_wired(settings: dict) -> bool:
    """True when the settings register the guard as a PreToolUse command for every guarded tool."""
    hooks = settings.get("hooks")
    entries = hooks.get("PreToolUse") if isinstance(hooks, dict) else None
    covered = set()
    for entry in entries if isinstance(entries, list) else []:
        commands = entry.get("hooks") if isinstance(entry, dict) else None
        if not any(isinstance(hook, dict) and hook.get("type") == "command" and GUARD_HOOK in str(hook.get("command"))
                   for hook in (commands if isinstance(commands, list) else [])):
            continue
        matcher = entry.get("matcher")
        if matcher in (None, "", "*"):
            return True
        covered |= set(matcher.split("|")) if isinstance(matcher, str) else set()
    return GUARDED_TOOLS <= covered


def _check_repository_settings(root: Path) -> None:
    """The repository's settings carry no sandbox key (DEC-233) and wire the guard, with the hooks on.

    The CLI may merge the repository's settings into the built ones, and a
    session whose settings register no guard has none.
    """
    wired = False
    for rel in REPO_SETTINGS:
        if not os.path.lexists(root / rel):
            continue
        try:
            data = json.loads((root / rel).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raise _refuse(f"{rel} cannot be read, so it cannot be shown to carry no sandbox key") from None
        if not isinstance(data, dict) or "sandbox" in data:
            raise _refuse(f"{rel} carries a sandbox key: the sandbox settings come from the launcher alone (DEC-233)")
        if data.get("disableAllHooks", False) is not False:
            raise _refuse(f"{rel} sets disableAllHooks: a worker session would have no guard")
        wired = wired or (rel == REPO_SETTINGS[0] and _guard_wired(data))
    if not wired:
        raise _refuse(f"{REPO_SETTINGS[0]} does not register the guard ({GUARD_HOOK}) as a PreToolUse hook for "
                      f"{', '.join(sorted(GUARDED_TOOLS))}: a worker session would have no guard")


def _check_cli_args(cli_args: list[str]) -> None:
    """Refuse the arguments that take the launcher's settings or the guard away from the session."""
    for arg in cli_args:
        if arg == "--settings" or arg.startswith("--settings="):
            raise _refuse("the CLI arguments carry --settings: the sandbox settings come from the launcher alone")
        if arg == "--bare":
            raise _refuse("the CLI arguments carry --bare, which skips every hook: the session would have no guard")
        if arg == "--setting-sources" or arg.startswith("--setting-sources="):
            raise _refuse("the CLI arguments carry --setting-sources: without the project's settings the session "
                          "would have no guard hook")


def launch(root: Path, role: str, ticket_id: str, cli_args: list[str]) -> int:
    """Start one worker session and return the CLI's exit code; raise ``GovError`` to refuse."""
    root = Path(os.path.realpath(root))
    if role not in WORKER_ROLES:
        raise _refuse(f"'{role}' is not a worker role ({', '.join(WORKER_ROLES)})")
    _check_cli_args(cli_args)
    _check_ticket(root, role, ticket_id)
    _check_repository_settings(root)
    cli = Path.home() / CLI_REL
    if not cli.is_file():
        raise _refuse(f"the CLI is not at ~/{CLI_REL} (DEC-205)")
    settings = build_settings(root, role, ticket_id)
    faults = sandbox_faults(settings)
    if faults:
        raise _refuse("the built settings are not strict: " + "; ".join(faults))
    # DEC-159: a temp directory of the session's own, for the CLI and for its sandboxed commands.
    tmpdir = tempfile.mkdtemp(prefix=f"gov-launch-{role}-")
    settings["env"].update({"TMPDIR": tmpdir, "CLAUDE_CODE_TMPDIR": tmpdir})
    settings["sandbox"]["filesystem"] = {"allowWrite": [f"/{tmpdir}"]}
    env = {**os.environ, **settings["env"]}
    return subprocess.run([str(cli), "--settings", json.dumps(settings), *cli_args], cwd=root, env=env).returncode
