"""Helpers for the W1-06 acceptance tests: the registry, the schema and the decision register.

Nothing here installs, downloads, uninstalls or writes anything. The registry,
the schema, the register and the vendor folder are read from the working tree;
the looks at the machine (``installed_version``, ``file_sha256``) read a file
that is already there.
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

REQUIRED = ("name", "version", "sha256", "install", "uninstall", "date", "approved_by")

SHA256 = re.compile(r"[0-9a-fA-F]{64}")
EXACT_VERSION = re.compile(r"v?\d+(\.\d+)+([-+.][0-9A-Za-z.-]+)?")
DECISION_ID = re.compile(r"DEC-\d{3,}")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


class Missing(AssertionError):
    """A file the tests read is not there, or cannot be read."""


# --------------------------------------------------------------------------
# The registry and its schema
# --------------------------------------------------------------------------

def load_registry():
    """The data of ``governance/project/tool-registry.yaml``, as a plain YAML load gives it."""
    path = REPO_ROOT / REGISTRY_REL
    if not path.is_file():
        raise Missing(f"{REGISTRY_REL} does not exist: W1-06 has not created the tool registry")
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
    """The entries of the registry that are mappings (the schema test reports the rest)."""
    tools = registry.get("tools") if isinstance(registry, dict) else None
    return [entry for entry in tools if isinstance(entry, dict)] if isinstance(tools, list) else []


def norm_name(value):
    return str(value).strip().lower()


def norm_version(value):
    """``v0.3.2`` and ``0.3.2`` are the same pin."""
    text = str(value).strip()
    return text[1:] if text[:1] in "vV" else text


def find(registry, names):
    """Every entry whose name is one of ``names`` (compared without case)."""
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


def is_tracked(rel):
    """Whether git tracks ``rel`` in this repository."""
    result = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel], cwd=REPO_ROOT,
                            capture_output=True, text=True, check=False)
    return result.returncode == 0


def is_committed_unchanged(rel):
    """Whether the working-tree file equals the one in ``HEAD``."""
    result = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=REPO_ROOT,
                            capture_output=True, text=True, check=False)
    return result.returncode == 0 and result.stdout.strip() == ""


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


# --------------------------------------------------------------------------
# What is on this machine (local_only tests)
# --------------------------------------------------------------------------

def installed_version(command, package):
    """``(path, version)`` of ``command`` on ``PATH``; ``(None, None)`` when it is not there.

    The version is read from the ``package.json`` of the package the executable
    belongs to, so nothing is run and nothing can be fetched. When no such file
    is found, the executable is asked with ``--version`` (20 s limit) and its
    output is returned as the version text.
    """
    path = shutil.which(command)
    if path is None:
        return None, None
    real = Path(os.path.realpath(path))
    for parent in real.parents:
        manifest = parent / "package.json"
        if not manifest.is_file():
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if isinstance(data, dict) and data.get("name") == package and data.get("version"):
            return path, str(data["version"])
    result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=20, check=False)
    return path, (result.stdout + result.stderr).strip()


# --------------------------------------------------------------------------
# Second batch (DEC-192 … DEC-197)
# --------------------------------------------------------------------------

VENDOR_REL = "template/governance/kernel/vendor/superpowers"
SKILLS = ("test-driven-development", "systematic-debugging", "verification-before-completion")
SCRATCH_CLONE_REL = ".gov-runtime/scratch/orchestrator/vendor-src/superpowers"

# DEC-192: ccusage is installed with the npm of ADR-0002's Node 22, so it lands under that Node's prefix.
NODE_22_REL = ".nvm/versions/node/v22.23.3"
NODE_22_PREFIX = Path.home() / NODE_22_REL


def node_22_package(command, package):
    """``(path, version)`` of a global npm package of Node v22.23.3; ``(None, None)`` when it is not installed there.

    ``path`` is the command npm links into that Node's ``bin``; the version is
    read from the package's own ``package.json``. Nothing is run.
    """
    link = NODE_22_PREFIX / "bin" / command
    manifest = NODE_22_PREFIX / "lib" / "node_modules" / package / "package.json"
    if not (link.exists() and manifest.is_file()):
        return None, None
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except ValueError:
        return str(link), None
    return str(link), str(data.get("version")) if isinstance(data, dict) and data.get("version") else None


def file_sha256(path):
    """The sha256 of the file at ``path`` (symbolic links followed), read in pieces."""
    digest = hashlib.sha256()
    with open(os.path.realpath(path), "rb") as handle:
        for piece in iter(lambda: handle.read(1 << 20), b""):
            digest.update(piece)
    return digest.hexdigest()


def own_text(decision):
    """The heading and the entry's own lines: the text stops at the next section heading or change-log table.

    ``Decision.body`` runs to the next ``### DEC`` heading, so the last entry of a
    register section also holds that section's change-log row, which names every
    tool of the section. That row is not part of the decision.
    """
    body = re.split(r"^(?:## |\|)", decision.body, maxsplit=1, flags=re.MULTILINE)[0]
    return f"{decision.title}\n{body}"


def names_tool(text, name):
    """Whether ``text`` holds ``name`` as a word of its own (compared without case)."""
    return re.search(rf"(?<![0-9a-z-]){re.escape(norm_name(name))}(?![0-9a-z-])", text.lower()) is not None


def names_version(text, version):
    """Whether ``text`` holds exactly ``version`` (with or without a leading ``v``), not a longer one."""
    return re.search(rf"(?<![0-9.]){re.escape(norm_version(version))}(?![0-9]|\.[0-9])", text) is not None


def approved_by(entry):
    return str(entry.get("approved_by", "")).strip()


def tracked_files(rel=None):
    """The paths git tracks (under ``rel`` when given), relative to the repository root."""
    command = ["git", "ls-files", "-z"] + (["--", rel] if rel else [])
    result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    return sorted(path for path in result.stdout.split("\0") if path)


def load_vendor():
    """The files on disk under the Superpowers vendor folder, relative to that folder (posix paths)."""
    root = REPO_ROOT / VENDOR_REL
    if not root.is_dir():
        raise Missing(f"{VENDOR_REL}/ does not exist: W1-06 has not committed the Superpowers source")
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*")
                  if path.is_file() or path.is_symlink())


def skill_of(rel):
    """The one of the three skills whose folder holds ``rel``; None when it is in none of them."""
    for part in rel.split("/")[:-1]:
        if part in SKILLS:
            return part
    return None


def is_licence(rel):
    """A licence file outside the skill folders: ``LICENSE``, ``LICENCE`` or ``COPYING``, with any extension."""
    name = rel.split("/")[-1].upper()
    return skill_of(rel) is None and name.split(".")[0] in ("LICENSE", "LICENCE", "COPYING")


# --------------------------------------------------------------------------
# Third batch (DEC-199)
# --------------------------------------------------------------------------

def folder_digest(files):
    """DEC-199's digest of a folder, given as ``{relative posix path: the file's bytes}``.

    One line per file: the file's sha256 in lowercase hexadecimal, two spaces,
    the path, one line feed. The lines are encoded as UTF-8, sorted as bytes,
    concatenated, and hashed with sha256.
    """
    lines = sorted(f"{hashlib.sha256(content).hexdigest()}  {rel}\n".encode("utf-8")
                   for rel, content in files.items())
    return hashlib.sha256(b"".join(lines)).hexdigest()


def committed_files(rel):
    """``{path relative to rel: bytes}`` of every file ``HEAD`` holds under the folder ``rel``, as committed."""
    listed = subprocess.run(["git", "ls-tree", "-r", "-z", "HEAD", "--", f"{rel}/"], cwd=REPO_ROOT,
                            capture_output=True, check=False)
    if listed.returncode != 0:
        raise Missing(f"git cannot list {rel}/ in HEAD: {listed.stderr.decode('utf-8', 'replace').strip()}")
    found = {}
    for record in listed.stdout.split(b"\0"):
        if not record:
            continue
        meta, path = record.split(b"\t", 1)
        _, kind, blob = meta.decode("ascii").split()
        if kind != "blob":
            continue
        content = subprocess.run(["git", "cat-file", "blob", blob], cwd=REPO_ROOT, capture_output=True, check=False)
        if content.returncode != 0:
            raise Missing(f"git cannot read the committed {path.decode('utf-8', 'replace')}")
        found[path.decode("utf-8")[len(rel) + 1:]] = content.stdout
    if not found:
        raise Missing(f"HEAD holds no file under {rel}/: W1-06 has not committed the Superpowers source")
    return found
