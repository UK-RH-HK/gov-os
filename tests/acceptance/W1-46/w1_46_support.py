"""Support code for the W1-46 acceptance tests (standard library and PyYAML only).

W1-46 builds ``gov launch``, the worker session launcher, and the research role.
The tests use public interfaces only: the ``gov launch`` command, the kernel
hooks as the harness calls them, and committed files. Nothing here imports
``src/gov``.

**How a test sees what the launcher builds.** The launcher starts the Claude
Code CLI by its absolute path ``~/.local/bin/claude`` (DEC-205). Each test gives
``gov launch`` a temporary ``HOME`` whose ``.local/bin/claude`` is a stand-in
program written by the test. The stand-in starts no session: it records its
arguments, its environment and the content of every ``--settings`` value in a
file, and ends. What the stand-in recorded is what a worker session would have
been started with. A second stand-in, first on ``PATH`` under the bare name
``claude``, records a launcher that did not use the absolute path.

**The project.** ``gov launch`` runs in a temporary project: this repository's
``src/gov``, kernel template, role files, committed settings and
``pyproject.toml``, copied file by file from git's listing, plus fixture tickets
and an experiment folder. The copy is both the project and the code under test.

**The held-out path.** ``governance/project/held-out.yaml`` is not copied, and
the copy of ``.claude/settings.json`` leaves out the ``Read`` deny rules with an
absolute path, as W1-47's wired copy does. Every temporary project gets a
``held-out.yaml`` of its own that names a stand-in directory made by the test
(DEC-218). No file of this suite carries a value of the committed list.

**The command line** is ``gov launch <role> <ticket> [-- <arguments for the
CLI>]`` (DEC-231): the role and the ticket are positional, and everything after
``--`` goes to the CLI unchanged.

**The research allowlist.** ``governance/project/research-allowlist.yaml`` is
copied from this repository when it exists (DEC-241). A test that changes it
changes the list it finds there, whatever key holds it.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

import yaml

_TESTS = Path(__file__).resolve().parent.parent
for _name in ("W1-07", "W1-47"):
    _directory = str(_TESTS / _name)
    if _directory not in sys.path:
        sys.path.insert(0, _directory)

import w1_07_support as cli_support   # noqa: E402  the ``gov`` console script, without an install
import w1_47_support as w47           # noqa: E402  the stand-in, settings rules, the fixture tickets

check_support = w47.check_support     # W1-03: ticket text, git
live_support = w47.live_support       # W1-05: the registered hook commands

REPO_ROOT = Path(__file__).resolve().parents[3]
SUITE_DIR = Path(__file__).resolve().parent
SETTINGS_REL = ".claude/settings.json"
LOCAL_SETTINGS_REL = ".claude/settings.local.json"
ROSTER_REL = "governance/project/roster.yaml"
AGENT_REL = ".claude/agents/research.md"
KERNEL_ROLE_GLOB = "template/governance/kernel/roles/research*"
REGISTRY_REL = "governance/project/tool-registry.yaml"
ALLOWLIST_REL = "governance/project/research-allowlist.yaml"   # DEC-241
CLI_REL = ".local/bin/claude"          # under HOME (DEC-205)

ENGINEER = "engineer"
TEST_DESIGNER = "independent-test-designer"
AUDITOR = "independent-auditor"
RESEARCH = "research"
WORKER_ROLES = (ENGINEER, TEST_DESIGNER, AUDITOR, RESEARCH)
EMPTY_ALLOWLIST_ROLES = (ENGINEER, TEST_DESIGNER, AUDITOR)
NOT_LAUNCHED = ("orchestrator", "product-spec", "no-such-role")

RESEARCH_TICKET = "DAEO-zz97"
EXPERIMENT_REL = "experiments/spikes/exp-901"
# The ticket each worker role is launched on. The test designer works on the engineer's ticket.
TICKET_OF = {
    ENGINEER: check_support.TICKET_ID,
    TEST_DESIGNER: check_support.TICKET_ID,
    AUDITOR: check_support.AUDITOR_TICKET_ID,
    RESEARCH: RESEARCH_TICKET,
}
# A path inside each role's write scope, as the guard decides it from the fixture tickets.
OWN_PATH = {
    ENGINEER: "src/gov/guard/new_module.py",
    TEST_DESIGNER: "tests/acceptance/W1-90/test_new.py",
    AUDITOR: "docs/audit/report.md",
    RESEARCH: f"{EXPERIMENT_REL}/notes.md",
}

# Copied from this repository, file by file, from git's listing. Never ``governance/project/held-out.yaml``.
PROJECT_PATHSPECS = ("src/gov", "template/governance/kernel", ".claude/agents", SETTINGS_REL, "pyproject.toml",
                     ROSTER_REL, REGISTRY_REL, ALLOWLIST_REL, ":(exclude)template/governance/kernel/vendor")
PROJECT_FILES = {
    "README.md": "# Launch fixture project\n",
    ".gitignore": ".gov-runtime/\n__pycache__/\n",
    "docs/notes.md": "notes\n",
    "docs/audit/earlier.md": "earlier audit\n",
    "tests/acceptance/W1-90/test_fixture.py": "VALUE = 1\n",
    "tests/unit/guard/test_decide.py": "VALUE = 1\n",
    f"{EXPERIMENT_REL}/README.md": "# Experiment 901\n",
    "experiments/spikes/exp-900/data.txt": "sibling experiment\n",
    "experiments/archive/old.txt": "archived\n",
    "experiments/notes.md": "experiment notes\n",
}
# What exists under ``.gov-runtime/`` at launch (ignored by git): the findings, the records, the snapshots, scratch.
RUNTIME_FILES = {
    ".gov-runtime/findings.jsonl": "",
    ".gov-runtime/records.jsonl": "",
    ".gov-runtime/snapshots/keep.json": "{}\n",
    ".gov-runtime/scratch/w1-46/seed.txt": "seed\n",
}
PROTECTED_RUNTIME = (".gov-runtime/freeze", ".gov-runtime/findings.jsonl", ".gov-runtime/records.jsonl",
                     ".gov-runtime/snapshots/keep.json", ".gov-runtime/snapshots/new.json",
                     ".gov-runtime/last_head.json", ".gov-runtime/a-link")
SCRATCH_PATHS = (".gov-runtime/scratch/w1-46/seed.txt", ".gov-runtime/scratch/new/file.txt")

# The starting hosts of the research allowlist, copied from DEC-241 in the register.
STARTING_HOSTS = (
    "github.com", "api.github.com", "raw.githubusercontent.com", "objects.githubusercontent.com",
    "codeload.github.com", "pypi.org", "files.pythonhosted.org", "registry.npmjs.org", "huggingface.co",
    "cdn-lfs.huggingface.co", "arxiv.org", "export.arxiv.org", "docs.python.org", "docs.rs", "crates.io",
    "static.crates.io", "developer.mozilla.org",
)
# "And the subdomains of readthedocs.io": the entry's form in the sandbox, and one host it must accept.
READTHEDOCS_ENTRY = "*.readthedocs.io"
READTHEDOCS_HOST = "docs.readthedocs.io"
NOT_A_RESEARCH_HOST = "w1-46-not-allowlisted.example"
ADDED_HOST = "w1-46-added-by-the-owner.example"

COMMAND_TIMEOUT_S = 60.0
HOOK_TIMEOUT_S = 30.0


# --------------------------------------------------------------------------
# The temporary project
# --------------------------------------------------------------------------

def make_project(directory, root=REPO_ROOT):
    """A committed project that holds this repository's launcher, guard, kernel template and settings."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    listing = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--",
         *PROJECT_PATHSPECS],
        capture_output=True, text=True, check=True,
    ).stdout
    for rel in sorted(set(item for item in listing.split("\0") if item)):
        source = Path(root) / rel
        if source.is_file() and not source.is_symlink():
            target = directory / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    files = dict(PROJECT_FILES)
    tickets = check_support.default_tickets()
    tickets[f"{RESEARCH_TICKET}.md"] = check_support.ticket_text(
        ticket_id=RESEARCH_TICKET, wbs_id="W1-97", role=RESEARCH, allowed_paths=(f"{EXPERIMENT_REL}/**",))
    for name, text in tickets.items():
        files[f".tickets/{name}"] = text
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    settings_path = directory / SETTINGS_REL
    if settings_path.is_file():   # no temporary project carries a held-out path (W1-47's wired copy does the same)
        copied = json.loads(settings_path.read_text(encoding="utf-8"))
        permissions = copied.get("permissions")
        if isinstance(permissions, dict) and isinstance(permissions.get("deny"), list):
            permissions["deny"] = [rule for rule in permissions["deny"]
                                   if not (isinstance(rule, str) and rule.replace(" ", "").startswith("Read(//"))]
        settings_path.write_text(json.dumps(copied, indent=2) + "\n", encoding="utf-8")
    check_support.git(directory, "init", "-q", "-b", "main")
    check_support.git(directory, "add", "-A")
    check_support.git(directory, "commit", "-q", "-m", "launch fixture project")
    for rel, text in RUNTIME_FILES.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return directory


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def project_settings(project):
    return w47.load_json_object(Path(project) / SETTINGS_REL, SETTINGS_REL)


# --------------------------------------------------------------------------
# The stand-in CLI
# --------------------------------------------------------------------------

_STUB = r'''#!@PYTHON@
"""Stand-in for the Claude Code CLI (W1-46 acceptance tests). Starts nothing; records how it was called."""
import json, os, sys

args = sys.argv[1:]
kind = @KIND@
if kind == "session" and ("--version" in args or "-v" in args):
    kind = "version"
    print(@VERSION@ + " (Claude Code)")
settings = []
i = 0
while i < len(args):
    value = None
    if args[i] == "--settings" and i + 1 < len(args):
        value = args[i + 1]
        i += 1
    elif args[i].startswith("--settings="):
        value = args[i].split("=", 1)[1]
    if value is not None:
        entry = {"value": value, "inline": value.lstrip().startswith("{")}
        if entry["inline"]:
            entry["text"] = value
        else:
            entry["realpath"] = os.path.realpath(value)
            entry["is_symlink"] = os.path.islink(value)
            try:
                with open(value, encoding="utf-8") as handle:
                    entry["text"] = handle.read()
            except OSError as exc:
                entry["text"] = None
                entry["error"] = str(exc)
        settings.append(entry)
    i += 1
named = dict(os.environ)
for entry in settings:
    try:
        block = json.loads(entry["text"]).get("env")
    except Exception:
        block = None
    if isinstance(block, dict):
        named.update({k: v for k, v in block.items() if isinstance(v, str)})
directories = {v: os.path.isdir(v) for k, v in named.items() if "TMP" in k.upper() and v.startswith("/")}
record = {"kind": kind, "argv0": sys.argv[0], "args": args, "cwd": os.getcwd(), "env": dict(os.environ),
          "settings": settings, "directories": directories}
with open(@LOG@, "a", encoding="utf-8") as handle:
    handle.write(json.dumps(record) + "\n")
'''


def pinned_cli_version(root=REPO_ROOT):
    """The Claude Code version the tool registry records (W1-48); what the stand-in answers to ``--version``."""
    try:
        data = yaml.safe_load((Path(root) / REGISTRY_REL).read_text(encoding="utf-8"))
        for entry in data.get("tools", []):
            if str(entry.get("name", "")).strip().lower() in ("claude code", "claude-code", "claude"):
                return str(entry.get("version", "")).strip() or "2.1.288"
    except (OSError, yaml.YAMLError, AttributeError):
        pass
    return "2.1.288"


def _write_stub(path, log, kind):
    text = (_STUB.replace("@PYTHON@", sys.executable).replace("@KIND@", repr(kind))
            .replace("@VERSION@", repr(pinned_cli_version())).replace("@LOG@", repr(str(log))))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


@dataclass(frozen=True)
class Cli:
    path: Path     # <HOME>/.local/bin/claude, the only place the launcher may start the CLI from (DEC-205)
    decoy: Path    # a directory, first on PATH, whose ``claude`` records a launcher that used the bare name
    log: Path


def install_stand_in_cli(sandbox):
    log = sandbox.elsewhere / "claude-calls.jsonl"
    decoy_dir = sandbox.elsewhere / "path-first"
    _write_stub(decoy_dir / "claude", log, "bare-name")
    return Cli(_write_stub(sandbox.home / CLI_REL, log, "session"), decoy_dir, log)


def calls(cli):
    if not cli.log.is_file():
        return []
    return [json.loads(line) for line in cli.log.read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------
# Running ``gov launch``
# --------------------------------------------------------------------------

def gov_environment(project, sandbox, cli=None, home=None):
    path = os.environ.get("PATH", "/usr/bin:/bin")
    return {
        "PATH": f"{cli.decoy}:{path}" if cli is not None else path,
        "HOME": str(home or sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(Path(project) / "src"),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
    }


def run_gov(project, sandbox, *args, cli=None, env=None, timeout=COMMAND_TIMEOUT_S):
    """Run ``gov <args>`` in ``project`` with the project's own ``gov`` package. Nothing is installed."""
    launcher = cli_support.write_launcher(project, sandbox)
    try:
        done = subprocess.run([sys.executable, str(launcher), *args], cwd=str(project),
                              env=env or gov_environment(project, sandbox, cli), capture_output=True, text=True,
                              timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {timeout:.0f} s") from None
    return cli_support.Run(tuple(args), done.returncode, done.stdout, done.stderr, 0.0)


@dataclass(frozen=True)
class Launch:
    """One run of ``gov launch`` and what the stand-in CLI recorded during it."""
    run: object
    calls: tuple

    @property
    def sessions(self):
        return [call for call in self.calls if call["kind"] == "session"]

    @property
    def bare(self):
        return [call for call in self.calls if call["kind"] == "bare-name"]

    def describe(self):
        return f"{self.run.describe()}\nCLI starts recorded: {[call['kind'] for call in self.calls]}"

    def session(self):
        """The one worker session the launcher started."""
        assert not self.bare, f"the launcher started a bare `claude` found on PATH (DEC-205)\n{self.describe()}"
        assert len(self.sessions) == 1, (
            f"gov launch did not start exactly one worker session ({len(self.sessions)} recorded)\n{self.describe()}"
        )
        return self.sessions[0]

    def settings(self):
        """The settings the session was started with: the one ``--settings`` value, parsed."""
        entries = self.session()["settings"]
        assert len(entries) == 1, f"the CLI was started with {len(entries)} --settings values, not one\n{self.describe()}"
        text = entries[0].get("text")
        assert text, f"the --settings file could not be read when the CLI started: {entries[0]}"
        try:
            data = json.loads(text)
        except ValueError:
            raise AssertionError(f"the --settings value is not JSON: {text[:300]!r}") from None
        assert isinstance(data, dict), "the --settings value is not a JSON object"
        return data

    def variable(self, name):
        """A variable of the session: the settings' ``env`` block wins over the process environment (DEC-183)."""
        block = self.settings().get("env")
        if isinstance(block, dict) and name in block:
            return block[name]
        return self.session()["env"].get(name)


def launch(project, sandbox, cli, role, ticket, *cli_args):
    before = len(calls(cli))
    args = ("launch", role, ticket) + (("--",) + tuple(cli_args) if cli_args else ())
    run = run_gov(project, sandbox, *args, cli=cli)
    return Launch(run, tuple(calls(cli)[before:]))


def assert_refused(result, *words):
    """Non-zero exit, a named reason, and no session started."""
    assert result.run.returncode != 0, f"gov launch did not refuse (exit code 0)\n{result.describe()}"
    assert not result.sessions and not result.bare, f"gov launch refused but started the CLI\n{result.describe()}"
    said = (result.run.stderr + "\n" + result.run.stdout).lower()
    assert any(word.lower() in said for word in words), (
        f"the refusal does not name its reason (one of {words})\n{result.describe()}"
    )


# --------------------------------------------------------------------------
# What the built settings say
# --------------------------------------------------------------------------

def sandbox_faults(settings):
    """Why the settings are not "on, strict and fail-closed" (CAP-61.a); empty when they are."""
    block = settings.get("sandbox")
    if not isinstance(block, dict):
        return ["the settings carry no sandbox block"]
    faults = []
    if block.get("enabled") is not True:
        faults.append("sandbox.enabled is not true")
    if block.get("failIfUnavailable") is not True:
        faults.append("sandbox.failIfUnavailable is not true")
    if block.get("allowUnsandboxedCommands") is not False:
        faults.append("sandbox.allowUnsandboxedCommands is not false")
    network = block.get("network")
    if not isinstance(network, dict) or network.get("strictAllowlist") is not True:
        faults.append("sandbox.network.strictAllowlist is not true")
    if block.get("excludedCommands"):
        faults.append("sandbox.excludedCommands has an entry (DEC-164)")
    return faults


def allowed_domains(settings):
    network = settings.get("sandbox", {}).get("network", {})
    domains = network.get("allowedDomains", []) if isinstance(network, dict) else []
    assert isinstance(domains, list), f"sandbox.network.allowedDomains is not a list: {domains!r}"
    return domains


def accepts(domains, host):
    """A domain allowlist accepts ``host`` as the sandbox does: the same name, or a subdomain of a ``*.`` entry."""
    for entry in domains:
        entry = str(entry).lower()
        if entry == host or (entry.startswith("*.") and host.endswith(entry[1:])):
            return True
    return False


def rewrite_allowlist(project, change):
    """Rewrite the project's research allowlist: ``change`` gets the list of entries and returns what replaces it.

    The file's key is not fixed by DEC-241. The list is the file's top level,
    or the one list a top-level mapping holds; the rest of the file is kept.
    """
    path = Path(project) / ALLOWLIST_REL
    assert path.is_file(), f"{ALLOWLIST_REL} does not exist in the project (DEC-241)"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        new = change(list(data))
    else:
        keys = [key for key, value in data.items() if isinstance(value, list)] if isinstance(data, dict) else []
        assert len(keys) == 1, (
            f"{ALLOWLIST_REL} is neither a list of hosts nor a mapping with one list of hosts: this test must be "
            "revised for its shape"
        )
        new = dict(data)
        new[keys[0]] = change(list(data[keys[0]]))
    path.write_text(yaml.safe_dump(new, default_flow_style=False), encoding="utf-8")
    return path


def allowlist_key(project):
    """The key that holds the list of hosts in the project's research allowlist, or None for a top-level list."""
    path = Path(project) / ALLOWLIST_REL
    assert path.is_file(), f"{ALLOWLIST_REL} does not exist in the project (DEC-241)"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    keys = [key for key, value in data.items() if isinstance(value, list)] if isinstance(data, dict) else []
    return keys[0] if len(keys) == 1 else None


GUARDED_TOOLS = ("Write", "Edit", "Bash")


def tools_without_a_guard_command(settings):
    """The write tools for which ``settings`` register no PreToolUse command."""
    return [tool for tool in GUARDED_TOOLS if not live_support.hook_commands(settings, "PreToolUse", tool)]


def assert_no_session_without_the_guard(result, hooks_switched_off=False):
    """What every answer to DP-11 shares: no worker session is started that no guard decides for.

    Either the launch is refused (non-zero exit, a named reason, nothing
    started), or the launcher wires the guard itself: the one ``--settings``
    value registers a PreToolUse command for every write tool, and switches the
    hooks back on where the repository's settings switched them off.
    """
    if result.run.returncode != 0:
        assert_refused(result, "hook", "guard", "settings")
        return
    built = result.settings()
    bare = tools_without_a_guard_command(built)
    assert bare == [], (
        "a worker session was started although the project's settings register no guard for it, and the built "
        f"settings register no PreToolUse command for {bare}\n{result.describe()}"
    )
    if hooks_switched_off:
        assert built.get("disableAllHooks") is False, (
            "a worker session was started although the repository's settings switch every hook off, and the built "
            f"settings do not switch them back on\n{result.describe()}"
        )


def write_ticket(project, ticket_id, role, status="in_progress", allowed_paths=("docs/**",), wbs_id="W1-98"):
    """Put one more committed ticket in the project."""
    write(project, f".tickets/{ticket_id}.md", check_support.ticket_text(
        ticket_id=ticket_id, wbs_id=wbs_id, status=status, role=role, allowed_paths=tuple(allowed_paths)))
    check_support.commit_all(project, f"ticket {ticket_id}")
    return ticket_id


def deny_rules(settings, tool):
    """The specifiers of the ``permissions.deny`` rules of one tool (``Edit`` or ``Read``)."""
    found = []
    for rule in w47.permission_rules(settings, "deny"):
        name, spec = w47.split_rule(rule)
        if name == tool and spec is not None:
            found.append(spec.strip())
    return found


def _absolute(spec, project, home):
    """The absolute pattern of a rule specifier: ``//abs``, ``~/home``, else relative to the project."""
    if spec.startswith("//"):
        return spec[1:]
    if spec.startswith("~/"):
        return f"{home}/{spec[2:]}"
    if spec.startswith("./"):
        spec = spec[2:]
    elif spec.startswith("/"):
        spec = spec[1:]
    return f"{project}/{spec}"


def _regex(pattern):
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
        elif pattern[i] == "[" and "]" in pattern[i + 1:]:
            close = pattern.index("]", i + 1)
            body = pattern[i + 1:close]
            out.append("[" + ("^" + body[1:] if body[:1] == "!" else body) + "]")
            i = close + 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def covers(specs, relpath, project, home):
    """True when a rule among ``specs`` matches ``relpath`` of the project or a directory above it.

    A rule on a directory holds for everything under it, in the permission
    rules and in the sandbox alike.
    """
    target = f"{project}/{relpath}"
    candidates = [target]
    while "/" in target.rstrip("/") and target != str(project):
        target = target.rsplit("/", 1)[0]
        candidates.append(target)
    for spec in specs:
        regex = _regex(_absolute(spec, str(project), str(home)).rstrip("/"))
        if any(regex.match(candidate) for candidate in candidates):
            return True
    return False


def edit_denied(result, relpath, project, sandbox):
    return covers(deny_rules(result.settings(), "Edit"), relpath, Path(project), sandbox.home)


def has_glob_character(name):
    return any(character in name for character in "*?[")


# --------------------------------------------------------------------------
# The guard, asked through the commands the committed settings register
# --------------------------------------------------------------------------

_CALLS = iter(range(1, 1_000_000))


def _decision(returncode, stdout):
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


def ask_guard(project, sandbox, tool_name, tool_input, role, ticket, cwd=None, mode="default"):
    """What the project's committed settings decide about one call: their deny rules, then their PreToolUse commands.

    The commands are run through the shell, as the harness runs them, with
    ``GOV_ROLE`` and ``GOV_TICKET`` in the environment and ``cwd`` as the
    session's working directory. No tool call is ever made.
    """
    settings = project_settings(project)
    rule = live_support.denied_by_settings(settings, tool_name, tool_input, project)
    if rule is not None:
        return w47.GuardResult("deny", 0, f"permissions.deny rule {rule}", "")
    data = live_support.hook_input(project, sandbox, "PreToolUse", tool_name, tool_input, permission_mode=mode,
                                   tool_use_id=f"toolu_w1_46_{next(_CALLS):05d}")
    data["cwd"] = str(cwd or project)
    results = []
    for command in live_support.hook_commands(settings, "PreToolUse", tool_name):
        proc = subprocess.run(["sh", "-c", command], input=json.dumps(data), capture_output=True, text=True,
                              cwd=str(project), env=live_support.command_environment(project, sandbox, role, ticket),
                              timeout=HOOK_TIMEOUT_S, check=False)
        results.append(w47.GuardResult(_decision(proc.returncode, proc.stdout), proc.returncode, proc.stdout,
                                       proc.stderr))
    assert results, "the committed settings register no PreToolUse command for " + tool_name
    for outcome in ("deny", "error", "ask"):
        for result in results:
            if result.decision == outcome:
                return result
    return results[0]


# --------------------------------------------------------------------------
# A wheel made by hand, for the install of the local_only research session (no network, no build tool)
# --------------------------------------------------------------------------

WHEEL_NAME = "w1_46_probe-0.1-py3-none-any.whl"
WHEEL_PACKAGE = "w1_46_probe"


def write_probe_wheel(directory):
    files = {
        f"{WHEEL_PACKAGE}/__init__.py": "VALUE = 1\n",
        f"{WHEEL_PACKAGE}-0.1.dist-info/METADATA": f"Metadata-Version: 2.1\nName: {WHEEL_PACKAGE}\nVersion: 0.1\n",
        f"{WHEEL_PACKAGE}-0.1.dist-info/WHEEL":
            "Wheel-Version: 1.0\nGenerator: w1-46-tests\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
    }
    record = []
    for name, text in files.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(text.encode()).digest()).rstrip(b"=").decode()
        record.append(f"{name},sha256={digest},{len(text.encode())}")
    record.append(f"{WHEEL_PACKAGE}-0.1.dist-info/RECORD,,")
    files[f"{WHEEL_PACKAGE}-0.1.dist-info/RECORD"] = "\n".join(record) + "\n"
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(directory / WHEEL_NAME, "w") as archive:
        for name, text in files.items():
            archive.writestr(name, text)
    return directory / WHEEL_NAME
