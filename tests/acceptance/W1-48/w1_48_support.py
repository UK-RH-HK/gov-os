"""Helpers for the W1-48 acceptance tests: the registry, its schema, the decision register and this machine.

The approach is the one of ``tests/acceptance/W1-06/w1_06_support.py``; the
helpers are repeated here so that this suite runs on its own and W1-06's files
stay untouched.

Nothing here installs, downloads, updates, uninstalls or writes anything, and
nothing starts a Claude Code session. The looks at the machine read a file that
is already there, or run a tool with its version flag.

DEC-205: the Claude Code CLI is always the file at ``~/.local/bin/claude``. No
helper resolves ``claude`` through ``PATH``.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

REGISTRY_REL = "governance/project/tool-registry.yaml"
SCHEMA_REL = "template/governance/kernel/schemas/tool-registry.schema.json"
REGISTER_REL = "docs/DECISION_REGISTER.md"
CONTRACT_REL = "docs/contract/contract.yaml"

SHA256 = re.compile(r"[0-9a-fA-F]{64}")
EXACT_VERSION = re.compile(r"v?\d+(\.\d+)+([-+.][0-9A-Za-z.-]+)?")
DECISION_ID = re.compile(r"DEC-\d{3,}")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
VERSION_TOKEN = re.compile(r"\d+(?:\.\d+)+")

# The names accepted for the three entries (compared without case).
CLAUDE_CODE = ("claude code", "claude-code", "claude")
BUBBLEWRAP = ("bubblewrap", "bwrap")
SOCAT = ("socat",)

# The KPI's floor: "pinned at 2.1.285 or later".
FLOOR = "2.1.285"


class Missing(AssertionError):
    """A file the tests read is not there, or cannot be read."""


# --------------------------------------------------------------------------
# The registry and its schema
# --------------------------------------------------------------------------

def load_registry():
    """The data of ``governance/project/tool-registry.yaml``, as a plain YAML load gives it."""
    path = REPO_ROOT / REGISTRY_REL
    if not path.is_file():
        raise Missing(f"{REGISTRY_REL} does not exist")
    import yaml  # PyYAML is the project's declared dependency (pyproject.toml)

    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise Missing(f"{REGISTRY_REL} is not YAML: {exc}") from exc


def load_schema():
    path = REPO_ROOT / SCHEMA_REL
    if not path.is_file():
        raise Missing(f"{SCHEMA_REL} does not exist: the tool-registry schema is missing")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise Missing(f"{SCHEMA_REL} is not JSON: {exc}") from exc


def entries(registry):
    """The entries of the registry that are mappings."""
    tools = registry.get("tools") if isinstance(registry, dict) else None
    return [entry for entry in tools if isinstance(entry, dict)] if isinstance(tools, list) else []


def norm_name(value):
    return str(value).strip().lower()


def norm_version(value):
    """``v0.3.2`` and ``0.3.2`` are the same pin."""
    text = str(value).strip()
    return text[1:] if text[:1] in "vV" else text


def version_key(value):
    """``2.1.285`` as ``(2, 1, 285)``, for comparing; None when the text is not digits and dots."""
    text = norm_version(value)
    if not re.fullmatch(r"\d+(\.\d+)*", text):
        return None
    return tuple(int(part) for part in text.split("."))


def find(registry, names):
    wanted = {norm_name(name) for name in names}
    return [entry for entry in entries(registry) if norm_name(entry.get("name", "")) in wanted]


def one(registry, names):
    """The single entry recorded under one of ``names``; fails when there is none or more than one."""
    found = find(registry, names)
    label = " / ".join(names)
    recorded = sorted(norm_name(entry.get("name", "")) for entry in entries(registry))
    assert found, f"{REGISTRY_REL} has no entry named {label} (recorded: {', '.join(recorded) or 'nothing'})"
    assert len(found) == 1, f"{REGISTRY_REL} records {label} {len(found)} times; a pin is one entry"
    return found[0]


def field(entry, key):
    return str(entry.get(key, "")).strip()


def approved_by(entry):
    return field(entry, "approved_by")


def statements(entry, skip=()):
    """``"<key>: <value>"`` for every fact of the entry whose key is not in ``skip``."""
    return [f"{key}: {value}" for key, value in entry.items() if key not in skip]


def clauses(text):
    """``text`` cut at sentence ends, semicolons and line ends. A full stop inside a version number does not cut."""
    return [piece for piece in re.split(r"(?:[.;:]\s+|\n)", text) if piece.strip()]


def is_committed_unchanged(rel):
    """Whether git tracks ``rel`` and the working-tree file equals the one in ``HEAD``."""
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel], cwd=REPO_ROOT,
                             capture_output=True, text=True, check=False)
    status = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=REPO_ROOT,
                            capture_output=True, text=True, check=False)
    return tracked.returncode == 0 and status.returncode == 0 and status.stdout.strip() == ""


# --------------------------------------------------------------------------
# The decision register
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Decision:
    id: str
    title: str
    status: str   # the text of the "- **Status:** …" line, or "" when the entry has none
    body: str

    @property
    def accepted_by_owner(self):
        return re.match(r"ACCEPTED \(owner\b", self.status) is not None

    @property
    def date(self):
        """The ISO date of the acceptance: from the status line, else from the heading; None when neither has one."""
        for text in (self.status.split("·")[0], self.title):
            found = ISO_DATE.search(text)
            if found:
                return found.group(0)
        return None


def load_decisions():
    """Every ``### DEC-nnn — title`` entry of the register, by id."""
    path = REPO_ROOT / REGISTER_REL
    if not path.is_file():
        raise Missing(f"{REGISTER_REL} does not exist")
    text = path.read_text(encoding="utf-8")
    heads = list(re.finditer(r"^### (DEC-\d+) — (.*)$", text, re.MULTILINE))
    found = {}
    for index, head in enumerate(heads):
        end = heads[index + 1].start() if index + 1 < len(heads) else len(text)
        body = text[head.end():end]
        status = re.search(r"^- \*\*Status:\*\* (.*)$", body, re.MULTILINE)
        found[head.group(1)] = Decision(id=head.group(1), title=head.group(2).strip(),
                                        status=status.group(1).strip() if status else "", body=body)
    if not found:
        raise Missing(f"{REGISTER_REL} holds no `### DEC-nnn — …` entry the tests can read")
    return found


def own_text(decision):
    """The heading and the entry's own lines: the text stops at the next section heading or change-log table."""
    body = re.split(r"^(?:## |\|)", decision.body, maxsplit=1, flags=re.MULTILINE)[0]
    return f"{decision.title}\n{body}"


def names_tool(text, name):
    """Whether ``text`` holds ``name`` as a word of its own (compared without case)."""
    return re.search(rf"(?<![0-9a-z-]){re.escape(norm_name(name))}(?![0-9a-z-])", text.lower()) is not None


def names_version(text, version):
    """Whether ``text`` holds exactly ``version`` (with or without a leading ``v``), not a longer one."""
    return re.search(rf"(?<![0-9.]){re.escape(norm_version(version))}(?![0-9]|\.[0-9])", text) is not None


def approval_problems(entry, registry, decisions, tool_names):
    """Why the entry's ``approved_by`` is not the recorded owner approval of this tool at this version (DEC-197).

    An empty list means: the cited id is an entry of the register, accepted by
    the owner, made under DEC-083, naming the tool and exactly the recorded
    version, and cited by no other entry of the registry.
    """
    cited = approved_by(entry)
    version = norm_version(entry.get("version", ""))
    if not DECISION_ID.fullmatch(cited):
        return [f"approved_by is {cited!r}, not a decision id"]
    decision = decisions.get(cited)
    if decision is None:
        return [f"{cited} is not an entry of {REGISTER_REL}"]
    problems = []
    text = own_text(decision)
    if not decision.accepted_by_owner:
        problems.append(f"{cited} is not accepted by the owner (status: {decision.status!r})")
    if not re.search(r"DEC-083(?!\d)", decision.status):
        problems.append(f"{cited} is not recorded under DEC-083 (status: {decision.status!r})")
    if not any(names_tool(text, name) for name in tool_names):
        problems.append(f"{cited} does not name the tool ({' / '.join(tool_names)})")
    if not (version and names_version(text, version)):
        problems.append(f"{cited} does not name the version {version!r}")
    shared = sorted(norm_name(other.get("name", "")) for other in entries(registry)
                    if other is not entry and approved_by(other) == cited)
    if shared:
        problems.append(f"{cited} is also cited as the approval of: {shared}")
    return problems


# --------------------------------------------------------------------------
# What is on this machine (local_only tests)
# --------------------------------------------------------------------------

# DEC-205: the pinned CLI is this file, never a bare `claude` found through PATH.
CLI_REL = ".local/bin/claude"
CLI = Path.home() / CLI_REL

EXTENSIONS = Path.home() / ".vscode-server" / "extensions"
EXTENSION_FOLDER = re.compile(r"anthropic\.claude-code-(\d+(?:\.\d+)+)(?:-.+)?")
BUNDLED_REL = "resources/native-binary/claude"

# The PATH given to a tool asked for its version: neither ~/.local/bin nor any Windows-side folder is on it.
BARE_PATH = "/usr/bin:/bin"


def file_sha256(path):
    """The sha256 of the file at ``path`` (symbolic links followed), read in pieces."""
    digest = hashlib.sha256()
    with open(os.path.realpath(path), "rb") as handle:
        for piece in iter(lambda: handle.read(1 << 20), b""):
            digest.update(piece)
    return digest.hexdigest()


def printed_version(argv):
    """``(text, version)``: what ``argv`` prints, and the first version number in it (None when there is none).

    ``argv`` is a tool with its version flag; it is run with a 30 s limit and a
    ``PATH`` of ``/usr/bin:/bin`` only.
    """
    env = dict(os.environ, PATH=BARE_PATH)
    result = subprocess.run([str(part) for part in argv], capture_output=True, text=True, timeout=30,
                            check=False, env=env)
    text = (result.stdout + result.stderr).strip()
    found = VERSION_TOKEN.search(text)
    return text, found.group(0) if found else None


def cli_version():
    """``(text, version)`` printed by ``~/.local/bin/claude --version``. No session is started."""
    return printed_version([CLI, "--version"])


def system_tool(command):
    """The path of a system tool (``bwrap``, ``socat``) on ``PATH``; None when it is not installed."""
    return shutil.which(command)


def extension_folders():
    """``{version: folder}`` of the Claude Code extension folders under ``~/.vscode-server/extensions/``.

    The version is the one in the folder's own ``package.json``; a folder
    without a readable one is left out.
    """
    found = {}
    if not EXTENSIONS.is_dir():
        return found
    for folder in sorted(EXTENSIONS.iterdir()):
        if not (folder.is_dir() and EXTENSION_FOLDER.fullmatch(folder.name)):
            continue
        try:
            data = json.loads((folder / "package.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and data.get("version"):
            found[norm_version(data["version"])] = folder
    return found


# --------------------------------------------------------------------------
# Node 22 commands (DEC-202, DEC-207)
# --------------------------------------------------------------------------

NODE_22_BIN = r"\.nvm/versions/node/v22\.23\.3/bin"
HOME_SPELLING = r"(?:~|\$HOME|\$\{HOME\})"

# `PATH=<home>/.nvm/versions/node/v22.23.3/bin:$PATH`, as a word of its own, optionally in double quotes.
NODE_22_PATH_PREFIX = re.compile(
    rf"(?<!\S)PATH=\"?{HOME_SPELLING}/{NODE_22_BIN}:(?:\$PATH|\$\{{PATH\}})\"?(?!\S)"
)
# A Node package manager as a command word, by its bare name or by any path.
NODE_PACKAGE_MANAGER = re.compile(r"(?<![\w.@-])(?:[^\s'\"]*/)?(?:npm|npx|pnpm|yarn|corepack)(?![\w.@/-])")


def is_node_22_command(command):
    """Whether the command runs a Node package manager, or anything from the ``bin`` of Node v22.23.3."""
    return (NODE_PACKAGE_MANAGER.search(command) is not None
            or re.search(rf"{NODE_22_BIN}/[\w.-]+", command) is not None)


def carries_node_22_prefix(command):
    """Whether the prefix stands before the first Node package manager or Node 22 ``bin`` program of the command.

    The text before the prefix must hold no such program, and the text after it
    must hold one.
    """
    prefix = NODE_22_PATH_PREFIX.search(command)
    if prefix is None:
        return False
    return not is_node_22_command(command[:prefix.start()]) and is_node_22_command(command[prefix.end():])
