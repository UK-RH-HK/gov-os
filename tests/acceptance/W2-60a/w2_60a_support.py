"""Support code for the W2-60a acceptance tests (standard library and PyYAML only).

W2-60a makes ``gov launch <role> <ticket> [-- <args>]`` start a worker session
as its role: the role file's text (and the skills it names) appended to the
CLI's system prompt, the role's default model and effort on the line, the
subagent model set, no compaction threshold, connectors, user-level agents and
skills and model-side memory kept out, and one launch record per launch,
written before the session starts. The tests drive one public interface,
``gov launch``, and read what it hands the CLI and what it leaves on disk.

**The code under test** is this worktree's ``src/`` (DEC-732): every ``gov``
child gets ``PYTHONPATH``, the runner's own value when it has one (DEC-732 sets
it per command), else the ``src`` folder of the worktree that holds this file.
``gov`` is run through ``pyproject.toml``'s console-script entry point, with no
install.

**The stand-in CLI.** ``gov launch`` starts the CLI by its absolute path
``~/.local/bin/claude`` (DEC-205). Every test gives ``gov launch`` a temporary
``HOME`` whose ``.local/bin/claude`` is a stand-in written here. It starts no
session and no model: it records, at the moment it is started, its arguments,
its environment, its ``--settings`` value, the bytes of every
``--append-system-prompt-file`` it is handed (the file lives in the session's
temp folder, which goes when the session ends, DEC-386), and the content of the
launch-record folder of the repository's main checkout (so a test sees whether
the record was there before the session started).

**The test home** is planted, for every test, with what a launched session must
not load (DEC-826 Q5): a connector in ``~/.claude.json``, a user-level agent,
a user-level skill, a model-side memory file, a user-level ``CLAUDE.md`` and
rule, and a user settings file that sets a model, an effort, a subagent model
and a compaction threshold. A project connector is planted in ``.mcp.json``.
The stand-in cannot load them; what it shows is the switches the launcher
passes (on the line and in the settings). What a real session's start shows is
the live file's (``test_w2_60a_live_sessions.py``).

**The fixture project** is a git repository built from scratch at
``<HOME>/work/repo``: fixture tickets, a settings file that registers a copy of
the kernel guard, fixture role files at ``template/governance/kernel/roles/``
(each with its version line, its default line and, for some, a skills line),
fixture generated agents at ``.claude/agents/`` (whose text is not the role
file's), fixture skills at ``.claude/skills/`` (the copies the session loads)
and kernel copies at ``template/governance/kernel/skills/`` with other versions
(which the record must not take), and the eight template copies at
``.claude/templates/<stem>.md`` (W2-153; any bytes). Nothing is copied from
this repository but the guard script and the research allowlist, as single
named files. Every ``gov`` child's environment names an open resource gate
planted in the test home (``plant_open_gate``, W2-20 S19).
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SUITE_DIR = Path(__file__).resolve().parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
GUARD_SOURCE = REPO_ROOT / "template/governance/kernel/hooks/pretooluse.py"
GUARD_REL = "governance/kernel/hooks/pretooluse.py"
GUARD_COMMAND = f'python3 "$CLAUDE_PROJECT_DIR"/{GUARD_REL}'
ALLOWLIST_REL = "template/governance/kernel/launch/research-allowlist.yaml"
ALLOWLIST_SOURCE = REPO_ROOT / ALLOWLIST_REL

SETTINGS_REL = ".claude/settings.json"
LOCAL_SETTINGS_REL = ".claude/settings.local.json"
HELD_OUT_REL = "governance/project/held-out.yaml"
ROLES_REL = "template/governance/kernel/roles"
AGENTS_REL = ".claude/agents"
SKILLS_REL = ".claude/skills"
KERNEL_SKILLS_REL = "template/governance/kernel/skills"
RECORDS_REL = ".gov-runtime/launches"
CLI_REL = ".local/bin/claude"

COMMAND_TIMEOUT_S = 60.0

ENGINEER = "engineer"
TEST_DESIGNER = "independent-test-designer"
AUDITOR = "independent-auditor"
RESEARCH = "research"
PRODUCT_SPEC = "product-spec"
ORCHESTRATOR = "orchestrator"
WORKER_ROLES = (ENGINEER, TEST_DESIGNER, AUDITOR, RESEARCH, PRODUCT_SPEC)

OPUS = "claude-opus-5-5"
SONNET = "claude-sonnet-5-5"
HAIKU = "claude-haiku-4-5-20251001"
EFFORTS = ("low", "medium", "high", "xhigh", "max")

# The fixture roles' default lines and versions. Research's model is not Opus, so a test can tell that the value
# is read from the role file and not written into the launcher.
DEFAULTS = {
    ENGINEER: (OPUS, "high"),
    TEST_DESIGNER: (OPUS, "high"),
    AUDITOR: (OPUS, "max"),
    RESEARCH: (SONNET, "medium"),
    PRODUCT_SPEC: (OPUS, "low"),
}
VERSIONS = {ENGINEER: "1.4.2", TEST_DESIGNER: "2.0.0", AUDITOR: "1.0.7", RESEARCH: "3.1.0", PRODUCT_SPEC: "0.9.1"}

# Words only these tests write, so that a text can be searched for them.
ROLE_WORD = "zq60a-role-text"          # in every fixture role file
AGENT_WORD = "zq60a-generated-agent"   # in every fixture generated agent, never in a role file
KERNEL_WORD = "zq60a-kernel-copy"      # in the kernel copies of the skills, never in the loaded copies
USER_WORD = "zq60a-user-level"         # in everything planted in the test home

KEPT_OUT = ["--strict-mcp-config", "--setting-sources project,local", "autoMemoryEnabled false"]
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
SHA256 = re.compile(r"[0-9a-f]{64}")
STARTED_AT = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")


# --------------------------------------------------------------------------
# The fixture tickets
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Ticket:
    tk: str
    role: str
    wbs: str
    allowed: tuple
    cls: str | None = "implementation"
    status: str = "in_progress"


T = Ticket("DAEO-zz6a", ENGINEER, "W2-60a-fixture", ("src/app/**",))
SPEC = Ticket("DAEO-zz6b", PRODUCT_SPEC, "W2-60a-spec", ("docs/spec/**",), cls="specification")
EXPERIMENT = Ticket("DAEO-zz6c", RESEARCH, "W2-60a-exp", ("experiments/spikes/exp-960/**",), cls="research")
NO_CLASS = Ticket("DAEO-zz6d", ENGINEER, "W2-60a-noclass", ("src/other/**",), cls=None)
CLOSED = Ticket("DAEO-zz6e", ENGINEER, "W2-60a-closed", ("src/closed/**",), status="closed")
TICKETS = (T, SPEC, EXPERIMENT, NO_CLASS, CLOSED)
TICKET_OF = {ENGINEER: T, TEST_DESIGNER: T, AUDITOR: T, PRODUCT_SPEC: SPEC, RESEARCH: EXPERIMENT}


def ticket_text(ticket):
    lines = [
        "---",
        f"id: {ticket.tk}",
        f"status: {ticket.status}",
        "deps: []",
        "links: []",
        "created: 2026-10-29T07:08:28Z",
        "type: task",
        "priority: 1",
        f"assignee: {ticket.role}",
        f"external-ref: {ticket.wbs}",
        "tags: [wave-2, implementation, full]",
        f"wbs_id: {ticket.wbs}",
        "title: W2-60a fixture ticket",
    ]
    if ticket.cls is not None:
        lines.append(f"class: {ticket.cls}")
    lines += [
        f"role: {ticket.role}",
        "depends_on: []",
        "allowed_paths:",
        *[f"- {path}" for path in ticket.allowed],
        "kpis:",
        "  success:",
        "  - The fixture component exists",
        "  failure:",
        "  - The fixture component is missing",
        "profile: FULL",
        "acceptance_tests:",
        f"  path: tests/acceptance/{ticket.wbs}/",
        "---",
        f"# {ticket.wbs} W2-60a fixture ticket",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# The fixture role files, generated agents and skills
# --------------------------------------------------------------------------

def default_line(model, effort):
    return f"- **Launch default:** model {model}, effort {effort}"


def version_line(version):
    return f"- **Version:** {version}"


def skills_line(names):
    return f"- **Skills:** {', '.join(names)}"


def role_text(role, version=None, default=None, skills=None, word=ROLE_WORD):
    """A fixture role file. ``version`` / ``default`` / ``skills``: a whole line to use, ``""`` for none, or None
    for the role's fixture value (no skills line by default)."""
    model, effort = DEFAULTS.get(role, (OPUS, "high"))
    version = version_line(VERSIONS.get(role, "1.0.0")) if version is None else version
    default = default_line(model, effort) if default is None else default
    lines = [
        f"# {role} role (W2-60a fixture)",
        "",
        f"This fixture role file carries the marker {word} for the role {role}. It states what the guard and the",
        "launcher decide; it grants nothing itself.",
        "",
        f"- **Purpose:** the W2-60a fixture {role}.",
    ]
    for line in (version, default, skills_line(skills) if skills else ""):
        if line:
            lines.append(line)
    lines += [
        "- **Tools:** Read, Grep, Glob, Edit, Write, Bash.",
        "- **Authority level:** worker, with no approval authority.",
        "",
    ]
    return "\n".join(lines)


def agent_text(role):
    return (f"---\nname: {role}\ndescription: >-\n  The W2-60a fixture {role} agent.\ntools:\n  - Read\n  - Write\n"
            f"  - Edit\n  - Bash\n  - Grep\n  - Glob\n---\n\nThis generated agent carries the marker {AGENT_WORD}; "
            "it is not the role file.\n")


@dataclass(frozen=True)
class Skill:
    folder: str
    name: str | None           # the front matter's name; None for none (the record then names the folder)
    version: str | None        # as written in the front matter; None for none (the record says "no version")
    version_yaml: str = ""     # how the version is written, when not ``"<version>"``
    extra: tuple = ()          # (relative path, text) of further files in the folder

    @property
    def recorded_name(self):
        return self.name or self.folder

    @property
    def recorded_version(self):
        return self.version if self.version is not None else "no version"

    @property
    def word(self):
        return f"zq60a-skill-{self.folder}"

    def text(self):
        head = ["---"]
        if self.name is not None:
            head.append(f"name: {self.name}")
        if self.version is not None:
            head.append(f"version: {self.version_yaml or json.dumps(self.version)}")
        head += [f"description: The W2-60a fixture skill {self.folder}.", "---", ""]
        body = [f"# {self.folder}", "", f"This skill's method text carries the marker {self.word}.", ""]
        return "\n".join(head + body)


BACKEND = Skill("w260a-backend", "w260a-backend", "2.0.1",
                extra=(("reference.md", "Backend reference.\n"), ("examples/one.md", "Example one.\n")))
SECURITY = Skill("w260a-security", "w260a-security", "1.1.0", version_yaml="1.1.0")
UNVERSIONED = Skill("w260a-unversioned", "w260a-unversioned", None)
FOLDER_NAMED = Skill("w260a-folder-named", None, "0.3.0")
SKILLS = (BACKEND, SECURITY, UNVERSIONED, FOLDER_NAMED)
SKILL_OF = {skill.folder: skill for skill in SKILLS}
# The kernel's copies carry other versions and another text: the record is taken from the loaded copy (D, F15).
KERNEL_VERSIONS = {BACKEND.folder: "9.9.9", SECURITY.folder: "8.8.8", UNVERSIONED.folder: "7.7.7"}


def kernel_skill_text(folder, version):
    return (f"---\nname: {folder}\nversion: \"{version}\"\ndescription: kernel copy\n---\n\n"
            f"The kernel copy of {folder}, marker {KERNEL_WORD}.\n")


COMMANDS_REL = ".claude/commands"


@dataclass(frozen=True)
class Command:
    """A project command file, which the CLI loads as a skill (review 1, F1): ``.claude/commands/<name>.md`` as
    ``<name>``, ``.claude/commands/<namespace>/<name>.md`` as ``<namespace>:<name>``."""
    rel: str                   # the file's path under .claude/commands/
    version: str | None        # as written in the front matter; None for none (the record says "no version")
    version_yaml: str = ""     # how the version is written, when not ``"<version>"``
    title: str | None = None   # a front matter ``name``, which is not the skill's name (``name: 'OPSX: Apply'``)
    front_matter: bool = True

    @property
    def recorded_name(self):
        return self.rel[:-len(".md")].replace("/", ":")

    @property
    def recorded_version(self):
        return self.version if self.version is not None else "no version"

    @property
    def word(self):
        return "zq60a-command-" + self.recorded_name.replace(":", "-")

    def text(self):
        body = [f"# {self.recorded_name}", "", f"This command's text carries the marker {self.word}.", ""]
        if not self.front_matter:
            return "\n".join(body)
        head = ["---", f"description: The W2-60a fixture command {self.recorded_name}."]
        if self.title is not None:
            head.append(f"name: '{self.title}'")
        if self.version is not None:
            head.append(f"version: {self.version_yaml or json.dumps(self.version)}")
        head += ["allowed-tools: Bash(true:*)", "---"]
        return "\n".join(head + body)


TOP_COMMAND = Command("w260a-top.md", "1.2.0", title="W260A: Top")
UNQUOTED_COMMAND = Command("w260a-ns/unquoted.md", "2.3.4", version_yaml="2.3.4")
UNVERSIONED_COMMAND = Command("w260a-ns/unversioned.md", None, title="W260A: Unversioned")
PLAIN_COMMAND = Command("w260a-ns/plain.md", None, front_matter=False)
COMMANDS = (TOP_COMMAND, UNQUOTED_COMMAND, UNVERSIONED_COMMAND, PLAIN_COMMAND)
NOT_A_COMMAND = "w260a-ns/notes.txt"  # not Markdown: the CLI does not load it


def add_commands(project, commands=COMMANDS):
    """The fixture command files under ``.claude/commands/``, and one file there that is not Markdown."""
    for command in commands:
        write(Path(project) / COMMANDS_REL / command.rel, command.text())
    write(Path(project) / COMMANDS_REL / NOT_A_COMMAND, "Not a command: zq60a-not-a-command.\n")
    return Path(project) / COMMANDS_REL


# --------------------------------------------------------------------------
# The sandbox: home, temp folder and elsewhere, disjoint
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    base: Path
    home: Path
    tmpdir: Path
    elsewhere: Path
    pycache: Path

    @property
    def project(self):
        return self.home / "work" / "repo"

    @property
    def records(self):
        """The launch-record folder of the fixture project, its own main checkout."""
        return self.project / RECORDS_REL


def make_sandbox(base):
    base = Path(base).resolve()
    box = Sandbox(base, base / "home", base / "systmp", base / "elsewhere", base / "pycache")
    for directory in (box.home, box.tmpdir, box.elsewhere, box.pycache):
        directory.mkdir(parents=True, exist_ok=True)
    plant_home(box)
    return box


USER_AGENT = "w260a-user-agent"
USER_SKILL = "w260a-user-skill"
USER_CONNECTOR = "w260a-user-connector"
PROJECT_CONNECTOR = "w260a-project-connector"
USER_SETTINGS_REL = ".claude/settings.json"  # under the home

# The user settings' permission rules a launched worker keeps (review 1, F2): every ``ask`` and ``deny`` string
# reaches the session's settings, and nothing else of the file does (no allow rule, mode, env, model, effort, hook).
USER_ASK = ("Bash(rm:*)", f"Bash({USER_WORD}-owner-ping:*)")
USER_DENY = (f"Bash({USER_WORD}-forbidden:*)", f"Read(//w260a/{USER_WORD}-denied/**)")
USER_ALLOW = (f"Bash({USER_WORD}-allowed:*)",)
USER_MODE = "acceptEdits"
USER_VARIABLE = "W260A_USER_VARIABLE"


def _sanitized(path):
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def user_settings():
    """The planted user settings file: what a session must not take from it, and the two lists it must."""
    return {
        "model": HAIKU, "effortLevel": "low", "autoCompactWindow": 300000,
        "env": {"CLAUDE_CODE_SUBAGENT_MODEL": HAIKU, "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "300000",
                USER_VARIABLE: USER_WORD},
        "permissions": {"allow": list(USER_ALLOW), "ask": list(USER_ASK), "deny": list(USER_DENY),
                        "defaultMode": USER_MODE},
        "hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": f"echo {USER_WORD}"}]}]},
    }


def plant_home(box):
    """What a launched session must not load, planted in the test home (DEC-826 Q5, lens E R6)."""
    claude = box.home / ".claude"
    write(box.home / ".claude.json", json.dumps({"mcpServers": {USER_CONNECTOR: {
        "type": "stdio", "command": "true", "args": [USER_WORD]}}}, indent=2) + "\n")
    write(box.home / USER_SETTINGS_REL, json.dumps(user_settings(), indent=2) + "\n")
    write(claude / "agents" / f"{USER_AGENT}.md",
          f"---\nname: {USER_AGENT}\ndescription: a user-level agent {USER_WORD}\n---\n\n{USER_WORD}\n")
    write(claude / "skills" / USER_SKILL / "SKILL.md",
          f"---\nname: {USER_SKILL}\nversion: \"1.0.0\"\ndescription: a user-level skill\n---\n\n{USER_WORD}\n")
    write(claude / "projects" / _sanitized(box.project) / "memory" / "MEMORY.md", f"- a memory {USER_WORD}\n")
    write(claude / "CLAUDE.md", f"User-level instructions {USER_WORD}.\n")
    write(claude / "rules" / "w260a-user-rule.md", f"A user-level rule {USER_WORD}.\n")


# --------------------------------------------------------------------------
# The fixture project, from scratch
# --------------------------------------------------------------------------

def git(directory, *args, check=True):
    proc = subprocess.run(["git", "-C", str(directory), "-c", "user.name=W2-60a acceptance",
                           "-c", "user.email=w2-60a@example.invalid", "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", "-c", "init.defaultBranch=main", *args],
                          capture_output=True, text=True, check=False, timeout=COMMAND_TIMEOUT_S,
                          env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull})
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {directory}: {proc.stderr.strip()}")
    return proc.stdout


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def settings_text(extra=None):
    data = {"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": GUARD_COMMAND}]}]}}
    data.update(extra or {})
    return json.dumps(data, indent=2) + "\n"


BASE_FILES = {
    "README.md": "# W2-60a fixture project\n",
    ".gitignore": ".gov-runtime/\n__pycache__/\n",
    "src/app/main.py": "VALUE = 1\n",
    "src/other/main.py": "VALUE = 1\n",
    "docs/spec/feature.md": "spec\n",
    "experiments/spikes/exp-960/README.md": "# Experiment 960\n",
    ".mcp.json": json.dumps({"mcpServers": {PROJECT_CONNECTOR: {"type": "stdio", "command": "true"}}}, indent=2)
    + "\n",
}
# W2-153 (DEC-1050): gov launch refuses a session without ``.claude/templates/<stem>.md`` for its role
# (LAUNCH_NO_TEMPLATE); the fixture project holds the eight copies (any bytes, W2-58's form), so the template check is
# never what refuses a launch here. Each carries the marker TEMPLATE_WORD, never in a role file.
TEMPLATE_WORD = "zq60a-template-copy"
TEMPLATE_STEMS = ("brief", "role-research", "role-product-spec", "role-test-designer", "role-engineer",
                  "role-reviewer", "role-lead", "role-cto")
TEMPLATE_FILES = {f".claude/templates/{stem}.md": f"---\nname: {stem}\n---\n# W2-60a fixture template copy {stem} "
                  f"{TEMPLATE_WORD}\n" for stem in TEMPLATE_STEMS}
BASE_FILES.update(TEMPLATE_FILES)


def make_project(sandbox, roles=WORKER_ROLES, skills=SKILLS, kernel_skills=True, agents=True, extra=None,
                 project=None, commit=True):
    """The fixture project: every worker role's fixture role file (``roles``), generated agents and skills."""
    project = Path(project or sandbox.project)
    files = dict(BASE_FILES)
    for ticket in TICKETS:
        files[f".tickets/{ticket.tk}.md"] = ticket_text(ticket)
    files[SETTINGS_REL] = settings_text()
    for role in roles:
        files[f"{ROLES_REL}/{role}.md"] = role_text(role)
    if agents:
        for role in (*WORKER_ROLES, ORCHESTRATOR):
            files[f"{AGENTS_REL}/{role}.md"] = agent_text(role)
    for skill in skills:
        files[f"{SKILLS_REL}/{skill.folder}/SKILL.md"] = skill.text()
        for rel, text in skill.extra:
            files[f"{SKILLS_REL}/{skill.folder}/{rel}"] = text
    if kernel_skills:
        for folder, version in KERNEL_VERSIONS.items():
            files[f"{KERNEL_SKILLS_REL}/{folder}/SKILL.md"] = kernel_skill_text(folder, version)
    files.update(extra or {})
    for rel, text in files.items():
        write(project / rel, text)
    for rel, source in ((GUARD_REL, GUARD_SOURCE), (ALLOWLIST_REL, ALLOWLIST_SOURCE)):
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, project / rel)
    if commit:
        git(project, "init", "-q", "-b", "main")
        git(project, "add", "-A")
        git(project, "commit", "-q", "-m", "W2-60a fixture project")
    return project


def role_path(project, role):
    return Path(project) / ROLES_REL / f"{role}.md"


def write_role(project, role, **kwargs):
    return write(role_path(project, role), role_text(role, **kwargs))


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def rewrite_settings(project, change, rel=SETTINGS_REL):
    path = Path(project) / rel
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    change(data)
    write(path, json.dumps(data, indent=2) + "\n")
    return path


# --------------------------------------------------------------------------
# The stand-in CLI
# --------------------------------------------------------------------------

_STUB = r'''#!@PYTHON@
"""Stand-in for the Claude Code CLI (W2-60a acceptance tests). Starts no session; records how it was started."""
import hashlib, json, os, sys

args = sys.argv[1:]


def values(name):
    found = []
    for index, arg in enumerate(args):
        if arg == name and index + 1 < len(args):
            found.append(args[index + 1])
        elif arg.startswith(name + "="):
            found.append(arg.split("=", 1)[1])
    return found


appended = []
for path in values("--append-system-prompt-file"):
    entry = {"path": path}
    try:
        with open(path, "rb") as handle:
            data = handle.read()
        entry.update(text=data.decode("utf-8", "replace"), sha256=hashlib.sha256(data).hexdigest())
    except OSError as error:
        entry["error"] = str(error)
    appended.append(entry)
folders = {}
for folder in @RECORDS@:
    if not os.path.isdir(folder):
        folders[folder] = None
        continue
    files = {}
    for name in sorted(os.listdir(folder)):
        try:
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                files[name] = handle.read()
        except OSError as error:
            files[name] = "unreadable: " + str(error)
    folders[folder] = files
record = {"argv0": sys.argv[0], "args": args, "cwd": os.getcwd(), "env": dict(os.environ),
          "settings": values("--settings"), "appended": appended, "records_at_start": folders}
with open(@LOG@, "a", encoding="utf-8") as handle:
    handle.write(json.dumps(record) + "\n")
if "--version" in args:
    print("2.1.292 (Claude Code)")
if os.path.isfile(@EXIT@):
    with open(@EXIT@, encoding="utf-8") as handle:
        sys.exit(int(handle.read().strip()))
'''


@dataclass(frozen=True)
class Cli:
    path: Path
    log: Path
    exit_file: Path


def install_stand_in_cli(sandbox, records=None, link_version=None):
    """The stand-in at ``<HOME>/.local/bin/claude``. ``link_version``: the stand-in is put at
    ``<HOME>/.local/share/claude/versions/<version>`` and the CLI's path is a link to it, as the CLI installs itself."""
    log = sandbox.elsewhere / "claude-calls.jsonl"
    exit_file = sandbox.elsewhere / "claude-exit-code"
    folders = [str(folder) for folder in (records or [sandbox.records])]
    text = (_STUB.replace("@PYTHON@", sys.executable).replace("@RECORDS@", repr(folders))
            .replace("@LOG@", repr(str(log))).replace("@EXIT@", repr(str(exit_file))))
    path = sandbox.home / CLI_REL
    target = path if link_version is None else sandbox.home / ".local/share/claude/versions" / link_version
    write(target, text)
    target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if link_version is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if os.path.lexists(path):
            path.unlink()
        path.symlink_to(target)
    return Cli(path, log, exit_file)


def calls(cli):
    if not cli.log.is_file():
        return []
    return [json.loads(line) for line in cli.log.read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------
# Running gov launch
# --------------------------------------------------------------------------

def python_path():
    """Every child's PYTHONPATH: the runner's own (DEC-732), else this worktree's src."""
    return os.environ.get("PYTHONPATH") or str(REPO_ROOT / "src")


GIB = 1024 ** 3


def plant_open_gate(sandbox):
    """An open resource gate in the sandbox's HOME; the variables that name its readings, for ``gov launch``'s
    environment.

    W2-20 S19 (DEC-1088 (5)(b)) runs the gate on every launch, and S8 shuts it when the configuration is missing. The
    form is W2-58's ``plant_open_gate``, from W2-136's ``_plant_open_gate`` and W2-20's README, "The configuration
    file": every value dated and sourced, in ``$HOME/.gov-os/machine/gate.json``; the readings are files under
    ``<elsewhere>/open-gate`` with room to spare, named through ``GOV_RESOURCES_*``. The gate is W2-20's, not under
    test here. Planted once per sandbox."""
    today = datetime.date.today().isoformat()

    def dated(value, source="planted for the W2-60a launcher cases (W2-20 README)"):
        return {"value": value, "date": today, "source": source}

    base = sandbox.elsewhere / "open-gate"
    readings = {
        "GOV_RESOURCES_MEMINFO": ("meminfo", f"MemTotal: {80 * GIB // 1024} kB\nMemAvailable: {64 * GIB // 1024} kB\n"),
        "GOV_RESOURCES_LOADAVG": ("loadavg", "0.00 0.00 0.00 1/321 54321\n"),
        "GOV_RESOURCES_BUSY_CORES": ("busy", "0\n"),
        "GOV_RESOURCES_EMBEDDING_CPU": ("embedding-cpu.json", json.dumps({"shared": 0, "query": 0})),
        "GOV_RESOURCES_DISK": ("disk.json", json.dumps({"free_bytes": 1024 * GIB, "free_inodes": 100_000_000})),
    }
    env = {"GOV_RESOURCES_NPROC": "64", **{variable: str(base / name) for variable, (name, _) in readings.items()}}
    if base.is_dir():
        return env
    base.mkdir(parents=True)
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
    machine = sandbox.home / ".gov-os" / "machine"
    machine.mkdir(parents=True, exist_ok=True)
    (machine / "gate.json").write_text(json.dumps(values, indent=1), encoding="utf-8")
    for name, text in readings.values():
        (base / name).write_text(text, encoding="utf-8")
    return env


def base_environment(sandbox, extra=None):
    """A minimal environment, built from scratch, with the open resource gate planted (``plant_open_gate``)."""
    env = {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONPATH": python_path(),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        **plant_open_gate(sandbox),
    }
    env.update(extra or {})
    return env


def _entry_point():
    scripts = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["scripts"]
    module, _, attribute = scripts["gov"].partition(":")
    return module.strip(), attribute.strip()


def gov_argv(*args):
    module, attribute = _entry_point()
    code = (f"import sys\nimport {module} as _m\n_t = _m\nfor _n in {attribute!r}.split('.'):\n"
            "    _t = getattr(_t, _n)\nsys.argv[0] = 'gov'\nsys.exit(_t())\n")
    return [sys.executable, "-c", code, *args]


@dataclass(frozen=True)
class Run:
    args: tuple
    returncode: int
    stdout: str
    stderr: str

    def describe(self):
        return (f"{' '.join(self.args)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-2000:]}\n"
                f"stderr:\n{self.stderr[-2000:]}")


def run_gov(sandbox, cwd, *args, extra_env=None, timeout=COMMAND_TIMEOUT_S):
    try:
        done = subprocess.run(gov_argv(*args), cwd=str(cwd), env=base_environment(sandbox, extra_env),
                              capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {timeout:.0f} s") from None
    return Run(("gov", *args), done.returncode, done.stdout, done.stderr)


def _listing(folder):
    folder = Path(folder)
    if not folder.is_dir():
        return {}
    found = {}
    for path in sorted(folder.iterdir()):
        try:
            found[path.name] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            found[path.name] = f"unreadable: {error}"
    return found


def occurrences(args, name):
    """How many arguments are ``name`` or ``name=<value>``."""
    return sum(1 for arg in args if arg == name or arg.startswith(name + "="))


def option_values(args, name):
    """The values of ``name`` in its spaced and its ``=`` spelling, in their order."""
    found = []
    for index, arg in enumerate(args):
        if arg == name:
            found.append(args[index + 1] if index + 1 < len(args) else None)
        elif arg.startswith(name + "="):
            found.append(arg.split("=", 1)[1])
    return found


@dataclass(frozen=True)
class Launch:
    """One run of ``gov launch`` and what the stand-in and the record folder show of it."""
    run: Run
    calls: tuple
    records_folder: Path
    before: dict
    after: dict
    started: float = 0.0
    ended: float = 0.0
    passed: tuple = field(default=())

    def describe(self):
        return (f"{self.run.describe()}\nCLI starts recorded: {len(self.calls)}\n"
                f"records before: {sorted(self.before)}\nrecords after: {sorted(self.after)}")

    @property
    def new_records(self):
        return {name: text for name, text in self.after.items() if name not in self.before}

    def session(self):
        """The one session the launcher started."""
        assert self.run.returncode == 0 and len(self.calls) == 1, (
            f"gov launch did not start exactly one session\n{self.describe()}")
        return self.calls[0]

    @property
    def args(self):
        return self.session()["args"]

    def settings(self):
        entries = self.session()["settings"]
        assert len(entries) == 1, f"the session was started with {len(entries)} --settings values\n{self.describe()}"
        data = json.loads(entries[0])
        assert isinstance(data, dict), "the --settings value is not a JSON object"
        return data

    def env_block(self):
        block = self.settings().get("env")
        assert isinstance(block, dict), f"the --settings value has no env block: {self.settings()}"
        return block

    def values(self, name):
        return option_values(self.args, name)

    def one(self, name):
        found = self.values(name)
        assert len(found) == 1, f"the session's line carries {name} {len(found)} times, not once: {self.args}"
        return found[0]

    def session_id(self):
        sid = self.one("--session-id")
        assert sid and UUID.fullmatch(sid), f"--session-id {sid!r} is not a UUID"
        return sid

    def appended(self):
        """What the session was handed with ``--append-system-prompt-file``, read when it started."""
        entries = self.session()["appended"]
        assert len(entries) == 1, (
            f"the session was started with {len(entries)} --append-system-prompt-file values, not one: {self.args}")
        assert "text" in entries[0], f"the appended file could not be read when the session started: {entries[0]}"
        return entries[0]

    def record(self):
        """The launch record of this launch: ``<session id>.json`` in the record folder."""
        sid = self.session_id()
        name = f"{sid}.json"
        assert name in self.after, (
            f"no launch record {name} in {self.records_folder}\n{self.describe()}")
        try:
            data = json.loads(self.after[name])
        except ValueError:
            raise AssertionError(f"the launch record {name} is not JSON: {self.after[name][:300]!r}") from None
        assert isinstance(data, dict), f"the launch record {name} is not a JSON object"
        return data

    def record_at_start(self):
        """The record as the session found it when it started, or None when it was not there."""
        sid = self.session_id()
        folder = self.session()["records_at_start"].get(str(self.records_folder))
        if folder is None:
            return None
        return folder.get(f"{sid}.json")


def launch(sandbox, cli, role, ticket, *cli_args, cwd=None, extra_env=None, records=None):
    """``gov launch <role> <ticket> [-- <cli_args>]`` in the project (or ``cwd``)."""
    records = Path(records or sandbox.records)
    tk = ticket.tk if isinstance(ticket, Ticket) else ticket
    before_calls = len(calls(cli))
    before = _listing(records)
    args = ("launch", role, tk) + (("--",) + tuple(cli_args) if cli_args else ())
    started = time.time()
    run = run_gov(sandbox, cwd or sandbox.project, *args, extra_env=extra_env)
    ended = time.time()
    return Launch(run, tuple(calls(cli)[before_calls:]), records, before, _listing(records), started, ended,
                  tuple(cli_args))


def said(result):
    return result.run.stderr + "\n" + result.run.stdout


def assert_refused(result, *words):
    """A refusal: a non-zero exit, no CLI start, no new launch record, and every word of ``words`` in what gov said
    (case-insensitive)."""
    assert result.run.returncode != 0, f"gov launch did not refuse (exit code 0)\n{result.describe()}"
    assert not result.calls, f"gov launch refused but started the CLI\n{result.describe()}"
    assert not result.new_records, (
        f"a refused launch left a launch record naming a session that never ran: {sorted(result.new_records)}\n"
        f"{result.describe()}")
    text = said(result).lower()
    missing = [word for word in words if word.lower() not in text]
    assert not missing, f"the refusal does not name {missing}\n{result.describe()}"


def assert_launched(result):
    assert result.run.returncode == 0 and len(result.calls) == 1, (
        f"gov launch did not start exactly one session\n{result.describe()}")
    return result


def deny_rules(settings):
    rules = (settings.get("permissions") or {}).get("deny") or []
    return [str(rule) for rule in rules]


def allow_write(settings):
    block = ((settings.get("sandbox") or {}).get("filesystem") or {})
    entries = block.get("allowWrite") or []
    return [str(entry) for entry in entries]
