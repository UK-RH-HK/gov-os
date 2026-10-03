"""Helpers for the W1-06 acceptance tests: the registry, the schema and the decision register.

Nothing here installs, downloads, uninstalls or writes anything. The registry,
the schema and the register are read from the working tree; the one look at the
machine (``installed_version``) reads a file next to an executable that is
already there.
"""

from __future__ import annotations

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
