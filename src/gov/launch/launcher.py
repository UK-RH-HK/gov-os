"""Worker session launcher: ``gov launch <role> <ticket> [-- <CLI arguments>]`` (W1-46, DEC-231).

Starts the CLI at ``~/.local/bin/claude`` (DEC-205) in the repository root with
one ``--settings`` value built here: the strict sandbox block, the role's network
profile and ``Edit`` deny rules, the held-out ``Read`` deny rules, ``GOV_ROLE``,
``GOV_TICKET``, ``GOV_STORE`` where the project configures its integration store
(W2-116, ``gov.launch.store``) and a per-session temp directory, removed when the session ends
(DEC-386), also when the launcher is interrupted or sent SIGTERM or SIGHUP
(DEC-392). Nothing fails open: whatever cannot be read or is not of the stated
shape refuses the launch.

A lead (``gov launch orchestrator|lead <ticket>``, W2-136 S9) is started only when
the plan's check admits its ticket, with ``GOV_ROLE=orchestrator``, its
``GOV_TICKET`` and no sandbox block, as the dispatcher starts a lead
(``build_lead_settings``); a worker launch never consults the plan.

Every launch, lead or worker, passes the machine-wide resource gate (W2-20 S19,
DEC-1088 (5)(b)): while it is shut on any reading, the launch is refused naming
each limit and its reading, unless ``--gate-override DEC-NNN`` starts it anyway;
that override, and a lead's plan override, are written to
``~/.gov-os/machine/launch.log`` and to stderr (P-1, P-8). A started session is
in the machine-wide registry while it runs.

No message of this module carries a held-out path.
"""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from gov.cli.errors import GovError
from gov.guard.decide import ACCEPTANCE, _load_ticket
from gov.guard.heldout import HeldOutError, load_held_out, load_yaml_unique
from gov.guard.install import experiment_folder
from gov.guard.reads import PolicyError, check_sets
from gov.guard import runs
from gov.launch.store import ENV as STORE_ENV, StoreSettingError, configured as configured_store
from gov.launch.store import main_root as main_store_root

# DEC-386: product-spec is launched as the other workers are, with no host in its allowlist.
WORKER_ROLES = ("engineer", "independent-test-designer", "independent-auditor", "research", "product-spec")
# Open package DP-8: these roles need a ticket whose ``role`` is their own; the
# two independent roles may be launched on any ``in_progress`` ticket.
OWN_TICKET_ROLES = frozenset({"engineer", "research", "product-spec"})
# W2-136 S9: a lead is a session of GOV_ROLE orchestrator with a GOV_TICKET, launched as ``orchestrator`` or ``lead``
# (W2-121's name for it). Only the launched role and ticket are checked against the plan, never the caller's own
# environment: a worker launch never consults the plan (DEC-1088 (5)(a), settled by the CTO).
LEAD_ROLES = ("lead", "orchestrator")
LEAD_GOV_ROLE = "orchestrator"
CLI_REL = ".local/bin/claude"
REPO_SETTINGS = (".claude/settings.json", ".claude/settings.local.json")
RUNTIME, SCRATCH = ".gov-runtime", "scratch"
GUARD_HOOK = "hooks/pretooluse.py"  # the guard, as the repository's settings register it
GUARDED_TOOLS = frozenset({"Write", "Edit", "Bash"})
# DEC-315: no worker edits the tickets or .claude, and only the independent test
# designer the acceptance tests, whatever the ticket's allowed_paths name.
PROTECTED_TREES = (".tickets", ".claude")
# DEC-273: a research ticket's one folder lies under this root. How a project
# names another root is open (DP-18): there is no configuration key for it.
EXPERIMENTS_ROOT = "experiments"
# DEC-313: arguments that take the permission checks away or add a writable directory.
BYPASS_FLAGS = ("--dangerously-skip-permissions", "--allow-dangerously-skip-permissions")
BYPASS_MODE = "bypassPermissions"
# Open package DP-9: both files hold a list of host names under this key; the
# project's file extends the kernel default, and may be absent (DEC-241).
ALLOWLIST_KEY = "hosts"
KERNEL_ALLOWLIST_REL = "template/governance/kernel/launch/research-allowlist.yaml"
PROJECT_ALLOWLIST_REL = "governance/project/research-allowlist.yaml"
# DEC-392: these end the session and remove its folder, and the launcher then ends with INTERRUPT_EXIT.
END_SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
INTERRUPT_EXIT = 130
END_WAIT_S = 5  # whole seconds a session that was asked to end may still run before it is killed
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
    entries that exist at launch are also listed by name, so that the sandbox has
    a literal rule for each (what it makes of a pattern in an ``Edit`` rule is not
    measured; P-W2-58-1 measured ``Read`` rules): the freeze flag only when it is
    there, since the sandbox puts a placeholder at a denied name that does not
    exist (DEC-402).
    """
    base = f"/{root}/{RUNTIME}"
    names = {f"{SCRATCH[:i]}[!{c}]*" for i, c in enumerate(SCRATCH)} | {SCRATCH[:i] for i in range(1, len(SCRATCH))}
    names |= {f"{SCRATCH}?*"}
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


def _tree_rules(root: Path, role: str) -> list[str]:
    """``Edit`` deny rules for the acceptance tests, the tickets and ``.claude`` (DEC-315).

    The literal rule names the folder to the sandbox; the pattern says the same
    to the file tools (what the sandbox makes of a pattern in an ``Edit`` rule is
    not measured; P-W2-58-1 measured ``Read`` rules).
    """
    trees = PROTECTED_TREES if role == "independent-test-designer" else (ACCEPTANCE, *PROTECTED_TREES)
    return [f"Edit(/{root}/{tree}{tail})" for tree in trees for tail in ("", "/**")]


def build_settings(root: Path, role: str, ticket_id: str) -> dict:
    """The ``--settings`` value of a worker session, less its temp directory. ``root`` is a real path."""
    deny = _runtime_rules(root) + _tree_rules(root, role)
    domains: list[str] = []
    if role == "research":
        folder = experiment_folder(str(root), ticket_id)
        if folder is None:
            raise _refuse("the research ticket's allowed_paths is not exactly one experiment folder (DEC-242)")
        if Path(folder).relative_to(root).parts[0] != EXPERIMENTS_ROOT or Path(folder) == root / EXPERIMENTS_ROOT:
            raise _refuse(f"the research ticket's allowed_paths names a folder that is not under the experiments "
                          f"root, {EXPERIMENTS_ROOT}/ (DEC-273)")
        deny += _fence_rules(root, folder)
        domains = _research_allowlist(root)
    try:
        deny += [f"Read(/{path}/**)" for path in load_held_out(str(root))]  # a missing file: no rule (DEC-242)
    except HeldOutError as error:
        raise _refuse(f"{error} (DEC-218)") from None
    # DEC-873: no Read rule for (c) or (d), which the guard refuses: the CLI turns a Read rule that matches existing
    # files into a read denial for the session's commands too, and running a test means reading it. A malformed
    # evaluation_sets block still refuses the launch (fail closed, as DEC-218).
    try:
        check_sets(str(root))
    except PolicyError as error:
        raise _refuse(f"{error} (DEC-820)") from None
    env = {"GOV_ROLE": role, "GOV_TICKET": ticket_id}
    # W2-116 S3 (DEC-963, DEC-1087 (3)): every worker's plain `gov retrieve` answers from the integration store, the
    # configured link itself (followed at each search), never from the worktree the session runs in. The place is the
    # main repository's (review F4): a worktree branched before the line was added still gets it.
    try:
        store = configured_store(main_store_root(root))
    except StoreSettingError as error:
        raise _refuse(f"{error}: the session's retrieval would have no store to answer from (W2-116)") from None
    if store is not None:
        env[STORE_ENV] = store
    return {
        "env": env,
        "permissions": {"deny": deny},
        "sandbox": {
            "enabled": True,
            "failIfUnavailable": True,
            "allowUnsandboxedCommands": False,
            "network": {"strictAllowlist": True, "allowedDomains": domains},
        },
    }


def build_lead_settings(ticket_id: str) -> dict:
    """The ``--settings`` value of a lead session (W2-136 S9): ``GOV_ROLE=orchestrator`` and its ``GOV_TICKET``, no
    sandbox block, as the dispatcher starts a lead. Kept apart from ``build_settings`` so that a worker's settings
    never lose their sandbox block or deny rules on a lead's account."""
    return {"env": {"GOV_ROLE": LEAD_GOV_ROLE, "GOV_TICKET": ticket_id}}


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
        permissions = data.get("permissions", {})
        if not isinstance(permissions, dict):
            raise _refuse(f"{rel}: permissions is not a map, so it cannot be shown to carry no bypass mode")
        if permissions.get("defaultMode") == BYPASS_MODE:
            raise _refuse(f"{rel} sets permissions.defaultMode to {BYPASS_MODE}: a worker session would run "
                          f"without the permission checks (DEC-313)")
        if "additionalDirectories" in permissions:
            raise _refuse(f"{rel} carries permissions.additionalDirectories: a worker session gets no added "
                          f"directory (DEC-313)")
        wired = wired or (rel == REPO_SETTINGS[0] and _guard_wired(data))
    if not wired:
        raise _refuse(f"{REPO_SETTINGS[0]} does not register the guard ({GUARD_HOOK}) as a PreToolUse hook for "
                      f"{', '.join(sorted(GUARDED_TOOLS))}: a worker session would have no guard")


def _check_cli_args(cli_args: list[str]) -> None:
    """Refuse the arguments that take the launcher's settings or the guard away from the session."""
    for arg, value in zip(cli_args, [*cli_args[1:], None]):
        if arg in BYPASS_FLAGS:
            raise _refuse(f"the CLI arguments carry {arg}: a worker session keeps its permission checks (DEC-313)")
        if arg == f"--permission-mode={BYPASS_MODE}" or (arg == "--permission-mode" and value == BYPASS_MODE):
            raise _refuse(f"the CLI arguments carry --permission-mode {BYPASS_MODE}: a worker session keeps its "
                          f"permission checks (DEC-313)")
        if arg == "--add-dir" or arg.startswith("--add-dir="):
            raise _refuse("the CLI arguments carry --add-dir: a worker session gets no added directory (DEC-313)")
        if arg == "--settings" or arg.startswith("--settings="):
            raise _refuse("the CLI arguments carry --settings: the sandbox settings come from the launcher alone")
        if arg == "--bare":
            raise _refuse("the CLI arguments carry --bare, which skips every hook: the session would have no guard")
        if arg == "--setting-sources" or arg.startswith("--setting-sources="):
            raise _refuse("the CLI arguments carry --setting-sources: without the project's settings the session "
                          "would have no guard hook")


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


def _admit_lead(root: Path, ticket_id: str) -> None:
    """W2-136 S9 (DEC-1088 (5)(a)): a lead only for a planned ticket whose waits are met; an override is written to
    the machine-wide launch log and to standard error (W2-20 S21, review F4, P-8)."""
    from gov.launch.gate import record

    verdict = check_lead(root, ticket_id)
    if isinstance(verdict, tuple) and len(verdict) == 3:
        verdict = dict(zip(("admitted", "reason", "override"), verdict))
    field = verdict.get if isinstance(verdict, dict) else lambda name: getattr(verdict, name, None)
    if not field("admitted"):
        raise _refuse(f"no lead for ticket '{ticket_id}': {field('reason')} (DEC-1088 (5))")
    if field("override"):
        record(f"gov launch: OVERRIDE plan_override: {field('override')}: ticket {ticket_id}: {field('reason')} "
               f"(DEC-899)")
        _say(f"gov launch: OVERRIDE {field('override')}: {field('reason')} (DEC-899)\n")


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


def launch(root: Path, role: str, ticket_id: str, cli_args: list[str], gate_override: str | None = None,
           gpu_need_mib: int | None = None) -> int:
    """Start one worker or lead session and return the CLI's exit code; raise ``GovError`` to refuse.

    Only a lead (``role`` in ``LEAD_ROLES``) is checked against the plan; a worker launch never is, whoever calls.
    Every launch, lead or worker, passes the resource gate (W2-20 S19), unless ``gate_override`` (a decision id)
    starts it anyway; ``gpu_need_mib`` is the session's declared GPU need. The started session is entered in the
    machine-wide registry while it runs (W2-20 S1).
    """
    root = Path(os.path.realpath(root))
    if role in LEAD_ROLES:
        _admit_lead(root, ticket_id)
        _check_cli_args(cli_args)
        _check_repository_settings(root)  # a lead has no sandbox: the guard is its only fence
        cli = _cli()
        _admit_start(root, role, ticket_id, gate_override, gpu_need_mib)
        # DEC-743 7: a ticket lead has no own folder under ~/gov-os-runs; the dispatcher gives a lead no temp folder.
        return _run(root, cli, build_lead_settings(ticket_id), cli_args, entry=(ticket_id, LEAD_GOV_ROLE))
    if role not in WORKER_ROLES:
        raise _refuse(f"'{role}' is not a worker role ({', '.join(WORKER_ROLES)}) "
                      f"or a lead role ({', '.join(LEAD_ROLES)})")
    _check_cli_args(cli_args)
    _check_ticket(root, role, ticket_id)
    _check_repository_settings(root)
    cli = _cli()
    settings = build_settings(root, role, ticket_id)
    faults = sandbox_faults(settings)
    if faults:
        raise _refuse("the built settings are not strict: " + "; ".join(faults))
    _admit_start(root, role, ticket_id, gate_override, gpu_need_mib)
    # DEC-728, DEC-743 (R2): the session's own folder under ~/gov-os-runs, made before the session starts and
    # never removed by the launcher; what it holds is left alone, and no other folder is made. DEC-751 1: only a
    # folder made here is marked as this repository's; a folder that is there without this repository's marker,
    # or that cannot be named, made or marked, is not opened: the session then has none.
    name = runs.folder(str(root), ticket_id, role)
    if name is not None and not os.path.lexists(name):
        runs.make(name, str(root))
    own = runs.own_folder(str(root), ticket_id, role)
    return _run(root, cli, settings, cli_args, temp_prefix=f"gov-launch-{role}-", own=own, entry=(ticket_id, role))


def _run(root: Path, cli: Path, settings: dict, cli_args: list[str], *, temp_prefix: str | None = None,
         own: str | None = None, entry: tuple[str, str] | None = None) -> int:
    """Start the session and wait for it. With ``temp_prefix`` (a worker), the session gets a temp folder of its
    own, in its env and its sandbox's write list with ``own``, removed when it ends (DEC-159, DEC-386). With
    ``entry`` (its ticket and role), the session is in the machine-wide registry while it runs (W2-20 S1): one that
    cannot be entered is stopped, so the gate never runs blind to a session."""
    from gov.resources import registry

    state = {"session": None, "ended": False, "asked": False, "registered": None}

    def end(signum=None, frame=None):
        """DEC-392: an interrupt, SIGTERM or SIGHUP ends the session. It is asked first, and killed when a second
        signal arrives or it still runs END_WAIT_S later. Nothing is raised here, so no clean-up is cut short."""
        session, asked = state["session"], state["asked"]
        state["ended"] = True
        if session is not None and session.poll() is None:
            state["asked"] = True
            if asked:
                session.kill()
            else:
                session.terminate()
                signal.alarm(END_WAIT_S)

    previous = {number: signal.signal(number, end) for number in END_SIGNALS
                if signal.getsignal(number) is not signal.SIG_IGN}  # a signal the caller ignores stays ignored
    alarm, tmpdir, code = signal.signal(signal.SIGALRM, end), None, INTERRUPT_EXIT
    try:
        if temp_prefix is not None:  # DEC-159: a temp directory of the session's own, for the CLI and its commands
            tmpdir = tempfile.mkdtemp(prefix=temp_prefix)
            settings["env"].update({"TMPDIR": tmpdir, "CLAUDE_CODE_TMPDIR": tmpdir})
            settings["sandbox"]["filesystem"] = {"allowWrite": [f"/{tmpdir}", *([f"/{own}"] if own else [])]}
        env = {**os.environ, **settings["env"]}
        if not state["ended"]:  # a signal that came first: no session is started
            try:
                state["session"] = subprocess.Popen([str(cli), "--settings", json.dumps(settings), *cli_args],
                                                    cwd=root, env=env)
            except OSError:
                raise _refuse(f"the CLI at ~/{CLI_REL} cannot be started (DEC-205)") from None
            pid = getattr(state["session"], "pid", None)  # a started process always has one
            if entry is not None and isinstance(pid, int) and pid > 0:
                try:
                    registry.register(pid, root, *entry)
                    state["registered"] = pid
                except (OSError, GovError) as error:
                    raise _refuse(f"the session cannot be entered in the machine-wide registry "
                                  f"({getattr(error, 'message', error)}): it is stopped (W2-20)") from None
            if state["ended"]:  # a signal that came while the session was started
                end()
            code = state["session"].wait()
            if state["ended"]:
                code = INTERRUPT_EXIT
        return code
    finally:
        session = state["session"]
        if session is not None and session.poll() is None:  # only an error on the way here: no session is left
            session.kill()
            session.wait()
        if state["registered"] is not None:
            registry.unregister(state["registered"])
        # DEC-386: the folder goes when the session ends, whole; a link in it is removed as a link.
        try:
            if tmpdir is not None:
                shutil.rmtree(tmpdir)
        except OSError as error:  # DEC-392: the session's exit code is kept, and one line names what stayed
            _say(f"gov launch: the temp folder {tmpdir} could not be removed and stays: "
                 f"{' '.join(str(error).split())}\n")
        for number, handler in previous.items():
            signal.signal(number, handler or signal.SIG_DFL)
        signal.alarm(0)
        signal.signal(signal.SIGALRM, alarm or signal.SIG_DFL)
