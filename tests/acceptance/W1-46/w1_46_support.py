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
copied from this repository when it exists (DEC-241). Its list is under the key
``hosts`` (DEC-272).

**The session's exit code.** The stand-in ends with exit code 0, or with the
code a test wrote for it (``set_session_exit_code``), as a worker session that
ended with that code would.
"""

from __future__ import annotations

import base64
import datetime
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
NOT_LAUNCHED = ("orchestrator", "no-such-role")   # owner decision, DEC-386: product-spec is launched (W1-28)

RESEARCH_TICKET = "DAEO-zz97"
EXPERIMENT_REL = "experiments/spikes/exp-901"
# The ticket each worker role is launched on. The test designer works on the engineer's ticket.
TICKET_OF = {
    ENGINEER: check_support.TICKET_ID,
    TEST_DESIGNER: check_support.TICKET_ID,
    AUDITOR: check_support.AUDITOR_TICKET_ID,
    RESEARCH: RESEARCH_TICKET,
}

# Copied from this repository, file by file, from git's listing. Never ``governance/project/held-out.yaml``.
# ``.claude/hooks`` since ACT-GUARD-FIX-4: the settings' PreToolUse line runs
# ``$CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse.py``, so a project that copies the settings without it refuses every
# call (D-4's red fix R-2, DEC-1061). In the project, ``role_reads`` finds no ``role_paths:`` and checks nothing.
# ``.claude/skills`` since W2-60a (DAEO-cv58; P-8 (a), DEC-1156 (7)): gov launch refuses a role file whose
# ``- **Skills:**`` line names a skill that is not at ``.claude/skills/<name>/SKILL.md`` with a version; the kernel's
# role files are copied, so the skills they name are too (the three vendored Superpowers skills take their version from
# ``template/governance/kernel/skills/superpowers/vendored.yaml``, copied with the kernel template).
PROJECT_PATHSPECS = ("src/gov", "template/governance/kernel", ".claude/agents", ".claude/hooks", ".claude/skills",
                     SETTINGS_REL, "pyproject.toml", ROSTER_REL, REGISTRY_REL, ALLOWLIST_REL,
                     ":(exclude)template/governance/kernel/vendor")
# W2-60a (DAEO-cv58; P-8 (a)): gov launch refuses a model after ``--`` that is not the role file's (DEC-839 item 1).
# The launch cases here hand a worker ``--model claude-opus-5-5`` after ``--``; the project's copies of the worker role
# files say that model at effort high (the rest of each file, its version and skills lines included, is this
# repository's). A live case still sets Haiku at effort low on its own copy (``set_live_launch_default``).
FIXTURE_MODEL = "claude-opus-5-5"
FIXTURE_LAUNCH_DEFAULT = f"- **Launch default:** model {FIXTURE_MODEL}, effort high"
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
# W2-153 (DEC-1050, DEC-866): gov launch refuses a session without ``.claude/templates/<stem>.md`` for its role; the
# project holds the eight copies (any bytes), so the template check is never what refuses a launch here. W1-28's,
# W1-32's, W1-50's and W2-54's launch projects are this one, and W2-90's generated one takes these files too.
TEMPLATE_STEMS = ("brief", "role-research", "role-product-spec", "role-test-designer", "role-engineer",
                  "role-reviewer", "role-lead", "role-cto")
PROJECT_FILES.update({f".claude/templates/{stem}.md": f"---\nname: {stem}\n---\n# W1-46 fixture template copy {stem}\n"
                      for stem in TEMPLATE_STEMS})
# What exists under ``.gov-runtime/`` at launch (ignored by git): the findings, the records, the snapshots, scratch.
RUNTIME_FILES = {
    ".gov-runtime/findings.jsonl": "",
    ".gov-runtime/records.jsonl": "",
    ".gov-runtime/snapshots/keep.json": "{}\n",
    ".gov-runtime/scratch/w1-46/seed.txt": "seed\n",
}


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
    for role in WORKER_ROLES:
        if (directory / ROLES_REL / f"{role}.md").is_file():
            set_live_launch_default(directory, role, FIXTURE_LAUNCH_DEFAULT)
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
if kind == "session" and os.path.isfile(@EXIT@):
    with open(@EXIT@, encoding="utf-8") as handle:
        sys.exit(int(handle.read().strip()))
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


def _exit_file(log):
    return Path(str(log) + ".exit-code")


def set_session_exit_code(cli, code):
    """From now on the stand-in session ends with ``code``, as a worker session that ended with it would."""
    _exit_file(cli.log).write_text(f"{int(code)}\n", encoding="utf-8")


def _write_stub(path, log, kind):
    text = (_STUB.replace("@PYTHON@", sys.executable).replace("@KIND@", repr(kind))
            .replace("@VERSION@", repr(pinned_cli_version())).replace("@LOG@", repr(str(log)))
            .replace("@EXIT@", repr(str(_exit_file(log)))))
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

GIB = 1024 ** 3
OPEN_GATE_DIR = "open-gate"   # under ``sandbox.elsewhere``: the planted readings


def _open_gate_readings(base):
    return {
        "GOV_RESOURCES_MEMINFO": ("meminfo", f"MemTotal: {80 * GIB // 1024} kB\nMemAvailable: {64 * GIB // 1024} kB\n"),
        "GOV_RESOURCES_LOADAVG": ("loadavg", "0.00 0.00 0.00 1/321 54321\n"),
        "GOV_RESOURCES_BUSY_CORES": ("busy", "0\n"),
        "GOV_RESOURCES_EMBEDDING_CPU": ("embedding-cpu.json", json.dumps({"shared": 0, "query": 0})),
        "GOV_RESOURCES_DISK": ("disk.json", json.dumps({"free_bytes": 1024 * GIB, "free_inodes": 100_000_000})),
    }


def open_gate_environment(sandbox):
    """The variables that name the planted readings, once ``plant_open_gate`` has run for ``sandbox``; else none."""
    base = Path(sandbox.elsewhere) / OPEN_GATE_DIR
    if not base.is_dir():
        return {}
    env = {variable: str(base / name) for variable, (name, _) in _open_gate_readings(base).items()}
    env["GOV_RESOURCES_NPROC"] = "64"
    return env


def plant_open_gate(sandbox, home=None):
    """Plant an open resource gate for a case that starts ``gov launch``; return the variables of its readings.

    W2-20 S19 (DEC-1088 (5)(b)) runs the gate on every launch, and S8 shuts it when the configuration is missing.
    The form is W2-136's ``_plant_open_gate`` (``tests/acceptance/W2-136/test_w2_136_launch_check.py``), from W2-20's
    README, "The configuration file": every value dated and sourced, in ``<home>/.gov-os/machine/gate.json``; the
    readings are files under ``<sandbox.elsewhere>/open-gate`` with room to spare, named through ``GOV_RESOURCES_*``.
    ``gov_environment`` carries them once planted. So these cases test what they were written for, whatever the
    machine is doing. A second call plants nothing more (it adds the configuration to another ``home`` if missing).
    A case whose point is the gate itself never calls it."""
    today = datetime.date.today().isoformat()

    def dated(value, source="planted for the W1-46 launcher cases (W2-20 README)"):
        return {"value": value, "date": today, "source": source}

    base = Path(sandbox.elsewhere) / OPEN_GATE_DIR
    if not base.is_dir():
        base.mkdir(parents=True)
        for name, text in _open_gate_readings(base).values():
            (base / name).write_text(text, encoding="utf-8")
    config = Path(home or sandbox.home) / ".gov-os" / "machine" / "gate.json"
    if not config.is_file():
        cpu = str(max(os.sched_getaffinity(0)))
        values = {
            "memory_floor_bytes": dated(3 * GIB, "DEC-942 item 2 (planted)"),
            "verification_peak_bytes": dated(4 * GIB),
            "working_size_bytes": dated(1 * GIB),
            "rebuild_peak_bytes": dated(2 * GIB),
            "disk_floor_bytes": dated(100 * GIB, "DEC-898 item 1 (planted)"),
            "inode_floor": dated(10_000_000, "DEC-898 item 1 (planted)"),
            "verification_lock": dated(str(base / "verification.lock")),
            "gpu_margin": dated(0.10, "DEC-950 item 2 (planted)"),
            "oom_floor_bytes": dated(1 * GIB),
            "heavy_slots": dated(2),
            "gpu_shares": dated({"embedder_mib": 0, "reranker_mib": 0}),
            "embedding_servers": {
                "shared": {"cpus": cpu, "nice": 10, "date": today, "source": "planted"},
                "query": {"cpus": cpu, "nice": 10, "date": today, "source": "planted"},
            },
        }
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(json.dumps(values, indent=1), encoding="utf-8")
    return open_gate_environment(sandbox)


def gov_environment(project, sandbox, cli=None, home=None):
    """The environment of a ``gov`` run, built from scratch; with an open gate's readings once planted."""
    path = os.environ.get("PATH", "/usr/bin:/bin")
    return {
        "PATH": f"{cli.decoy}:{path}" if cli is not None else path,
        "HOME": str(home or sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(Path(project) / "src"),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        **open_gate_environment(sandbox),
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
    """``gov launch <role> <ticket> [-- cli_args]`` with an open resource gate planted (``plant_open_gate``)."""
    plant_open_gate(sandbox)
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


ROLE_PROMPT_FLAG = "--append-system-prompt-file"


def caller_args_then_template_pair(argv, args, role=None):
    """True when ``args`` are one contiguous, ordered run at the end of ``argv``, followed by nothing or by exactly one
    ``--append-system-prompt-file <path>`` pair whose file name is ``role-<role>.md`` (any one role when ``role`` is
    None): since P-4 (A) (DEC-1167) a worker launch hands its role text, a blank line and the template's bytes as one
    file in its TMPDIR, placed last (W2-153's S1, DEC-1050; DEC-866; DEC-1156 (7)). The rule is W2-56's revised S6.
    An extra, dropped or reordered caller argument, a second pair, a pair before or inside the caller's run, and
    anything after the pair still fail."""
    argv, args = list(argv), list(args)
    n = len(args)

    def pairs(items):
        return sum(1 for item in items if item == ROLE_PROMPT_FLAG or item.startswith(ROLE_PROMPT_FLAG + "="))

    if not args:
        return False
    if argv[-n:] == args:
        return pairs(argv) == 0
    if len(argv) < n + 2 or argv[-n - 2:-2] != args or argv[-2] != ROLE_PROMPT_FLAG:
        return False
    if pairs(argv[:-2]):
        return False
    head, sep, name = argv[-1].replace("\\", "/").rpartition("/")
    if not (sep and head) or (head + "/").endswith("/.claude/templates/"):
        return False  # the bare template is the old pair: a worker now gets the composed file in its TMPDIR
    if role is not None:
        return name == f"role-{role}.md"
    stem = name[len("role-"):-len(".md")] if name.startswith("role-") and name.endswith(".md") else ""
    return bool(stem) and not stem.startswith("-")


# --------------------------------------------------------------------------
# What the built settings say
# --------------------------------------------------------------------------


def hook_keys(settings):
    """The keys of ``settings`` that register a hook or switch the hooks on or off."""
    return sorted(key for key in ("hooks", "disableAllHooks") if key in settings)


def rewrite_settings(project, change, rel=SETTINGS_REL):
    """Change the repository's settings file ``rel`` in place: ``change`` gets the parsed object ({} if missing)."""
    path = Path(project) / rel
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    change(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


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

    Rewrite-Reason: DEC-866, W2-106. The committed lines take the pinned form (``$HOME/.local/bin/gov``, else
    ``gov`` on ``PATH``); the sandbox's HOME is given a pinned ``gov`` of this tree first (W1-47's
    ``plant_pinned_gov``), here, where every case of this support and of W1-33's runs a hook line, so no case
    depends on the runner's ``PATH``: not refused where none is on it, not judging the owner's pin where it is.
    """
    w47.plant_pinned_gov(sandbox.home)
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


# --------------------------------------------------------------------------
# W2-60a: a live session's model and effort come from the role file's default line
# --------------------------------------------------------------------------

ROLES_REL = "template/governance/kernel/roles"
LAUNCH_DEFAULT = "- **Launch default:**"
# DEC-839 item 2: live harness tests run on Haiku 4.5 at effort low where the case only checks that a hook fired.
LIVE_LAUNCH_DEFAULT = f"{LAUNCH_DEFAULT} model claude-haiku-4-5-20251001, effort low"


def set_live_launch_default(project, role, line=LIVE_LAUNCH_DEFAULT):
    """Write ``line`` as the role's default line in the project's own copy of its role file.

    Since W2-60a the launcher takes the session's model and effort from the role
    file's default line and refuses a model after ``--`` that is not the role's
    (DEC-839 items 1 and 5), so a live case no longer passes ``--model haiku``:
    its copy of the role file says Haiku at effort low instead, in place of the
    line W2-11 writes, or after the file's last line when it has none. The rest
    of the file, its version line included, is this repository's.
    """
    path = Path(project) / ROLES_REL / f"{role}.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    at = next((index for index, text in enumerate(lines) if text.startswith(LAUNCH_DEFAULT)), len(lines))
    kept = [text for text in lines if not text.startswith(LAUNCH_DEFAULT)]
    kept.insert(min(at, len(kept)), line)
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return path
