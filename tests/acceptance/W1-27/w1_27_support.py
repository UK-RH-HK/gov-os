"""Support code for the W1-27 acceptance tests (standard library only, plus w1_07_support).

W1-27 builds ``gov doctor`` and ``gov rebuild``. The tests use them only through
their public interface: the ``gov`` command, its arguments, its output and its
exit code.

The same rules as W1-07 apply: nothing is installed; the repository itself is
never the project; the environment is built from scratch.

Claude Code drift is tested with fake binaries in temporary directories and
never by touching the installed CLI or extension.

One KPI line: doctor reports that the project's held-out file is missing. That
is an existence check and nothing else: the code never opens, reads, hashes,
copies or prints that file, and no worker, test or lead reads, prints, searches,
diffs or copies it in this repository or in any copy of it, or displays the
settings file's deny line for it. Tests show the line on a throwaway project in
a temporary directory (file absent: reported; an empty file present: not
reported). Put this paragraph word for word in every worker's brief.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import sys
from pathlib import Path

_W1_07_DIR = str(Path(__file__).resolve().parents[1] / "W1-07")
if _W1_07_DIR not in sys.path:
    sys.path.insert(0, _W1_07_DIR)

import w1_07_support as base  # noqa: E402

REPO_ROOT = base.REPO_ROOT
PATH_MAP_REL = base.PATH_MAP_REL
HELD_OUT_REL = base.HELD_OUT_REL
CHECKS_REL = base.CHECKS_REL

copy_working_tree = base.copy_working_tree
run_gov = base.run_gov
run_gov_with_code = base.run_gov_with_code
make_sandbox = base.make_sandbox
assert_envelope = base.assert_envelope
assert_error = base.assert_error
find_records = base.find_records
git = base.git
commit_all = base.commit_all
porcelain = base.porcelain
snapshot = base.snapshot
snapshot_difference = base.snapshot_difference
label = base.label
entry_point = base.entry_point

CONFIG_INVALID = base.CONFIG_INVALID
NOT_IMPLEMENTED = base.NOT_IMPLEMENTED

CLAUDE_CODE_PINNED_VERSION = "2.1.288"
CLAUDE_CODE_MINIMUM_VERSION = "2.1.285"

# The twenty-two constitutional systems (from the W1-08 path-map schema).
SYSTEMS = (
    "constitution-and-policies", "knowledge-fabric", "repository-contract",
    "agent-organisation", "skills", "tools-and-capabilities", "command-surface",
    "model-adapters", "orchestration-and-handoffs", "specification-and-planning",
    "research-and-experiments", "task-system", "product-delivery",
    "verification-and-governance-tests", "change-impact-control",
    "checkpoint-and-recovery", "observability-and-cost", "organisational-learning",
    "independent-audit", "security-and-permissions", "budget-governance",
    "emergency-stop-and-rollback",
)

# The thirteen required policy keys.
POLICIES = (
    "security", "authority", "test", "change", "human_gate", "tool",
    "memory", "context", "checkpoint", "model_routing", "budget",
    "learning", "archive",
)

# The nine required namespace fields.
NAMESPACE_FIELDS = (
    "paths", "memory_class", "sensitivity", "permitted_roles", "retention",
    "export_policy", "embedding_policy", "provenance", "deletion_rebuild",
)


def minimal_namespace_yaml(name="all", paths='["**"]', indent=2):
    """One namespace with all nine required fields, indented by ``indent`` spaces."""
    pad = " " * indent
    return (
        f"{pad}{name}:\n"
        f"{pad}  paths: {paths}\n"
        f"{pad}  memory_class: governance\n"
        f"{pad}  sensitivity: internal\n"
        f"{pad}  permitted_roles: [engineer]\n"
        f"{pad}  retention: kept\n"
        f"{pad}  export_policy: allowed\n"
        f"{pad}  embedding_policy: not embedded\n"
        f"{pad}  provenance: written\n"
        f"{pad}  deletion_rebuild: authoritative\n"
    )


def minimal_systems_yaml():
    """All twenty-two systems as absent with a reason (each line terminated)."""
    return "".join(f"  {name}:\n    status: absent\n    reason: minimal fixture\n" for name in SYSTEMS)


def minimal_policies_yaml():
    """All thirteen policies at their minimum allowed strength (each line terminated)."""
    hard = ("security", "authority", "test", "change", "human_gate", "tool")
    warning = ("memory", "context", "checkpoint")
    lines = []
    for name in POLICIES:
        if name in hard:
            lines.append(f"  {name}: hard-block\n")
        elif name in warning:
            lines.append(f"  {name}: warning\n")
        else:
            lines.append(f"  {name}: informational\n")
    return "".join(lines)


def minimal_valid_path_map():
    """A path-map.yaml valid under the W1-08 schema (all five top-level keys, code_intelligence disabled)."""
    return (
        "state_class: AUTHORITATIVE\n"
        "namespaces:\n"
        f"{minimal_namespace_yaml()}"
        "capabilities:\n"
        "  code_intelligence:\n    enabled: false\n"
        "  research_corpus:\n    enabled: false\n"
        f"policies:\n{minimal_policies_yaml()}"
        f"systems:\n{minimal_systems_yaml()}"
    )


def minimal_valid_path_map_with_code_intelligence():
    """A path-map.yaml valid under the W1-08 schema with code_intelligence enabled and languages present (DEC-265)."""
    return (
        "state_class: AUTHORITATIVE\n"
        "namespaces:\n"
        f"{minimal_namespace_yaml()}"
        "capabilities:\n"
        "  code_intelligence:\n    enabled: true\n    languages: [python]\n"
        "  research_corpus:\n    enabled: false\n"
        f"policies:\n{minimal_policies_yaml()}"
        f"systems:\n{minimal_systems_yaml()}"
    )


def write_path_map(project, text):
    """Write path-map.yaml into the project and commit it."""
    path = Path(project) / PATH_MAP_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    commit_all(project, "a path-map")
    return path


def write_held_out(project, content=""):
    """Write (or create empty) governance/project/held-out.yaml and commit it."""
    path = Path(project) / HELD_OUT_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    commit_all(project, "held-out.yaml")
    return path


def remove_held_out(project):
    """Remove governance/project/held-out.yaml if it exists and commit."""
    path = Path(project) / HELD_OUT_REL
    if path.exists():
        path.unlink()
        commit_all(project, "remove held-out.yaml")


def write_tool_registry(project, tools_yaml):
    """Write a tool-registry.yaml with the given tools section and commit."""
    path = Path(project) / "governance" / "project" / "tool-registry.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"tools:\n{tools_yaml}\n", encoding="utf-8")
    commit_all(project, "tool-registry")
    return path


def write_fake_claude_cli(directory, version, content_for_sha=None):
    """Write a fake ``claude`` shell script that responds to ``--version`` and return its path and sha256.

    The fake binary is a shell script in ``directory``. ``content_for_sha`` overrides the script body to produce a
    specific sha256; otherwise the sha256 is derived from the version string.
    """
    path = Path(directory) / "claude"
    body = content_for_sha or f"#!/bin/sh\necho '{version}'\n"
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, sha


def write_fake_extension(directory, version, binary_sha=None):
    """Write a fake VS Code extension directory structure and return (ext_dir, binary_sha256).

    Creates the minimum structure the doctor needs to find:
    - ``extensions.json`` listing the extension
    - ``anthropic.claude-code-<version>/package.json`` with the version
    - ``anthropic.claude-code-<version>/resources/native-binary/claude`` as a fake binary
    """
    ext_dir = Path(directory) / f"anthropic.claude-code-{version}"
    ext_dir.mkdir(parents=True, exist_ok=True)

    import json
    extensions_json = Path(directory) / "extensions.json"
    extensions_json.write_text(json.dumps([{
        "identifier": {"id": "anthropic.claude-code"},
        "version": version,
        "location": {"path": str(ext_dir)},
    }]), encoding="utf-8")

    (ext_dir / "package.json").write_text(json.dumps({
        "name": "claude-code",
        "version": version,
    }), encoding="utf-8")

    binary_dir = ext_dir / "resources" / "native-binary"
    binary_dir.mkdir(parents=True, exist_ok=True)
    binary_path = binary_dir / "claude"
    body = f"#!/bin/sh\necho 'extension {version}'\n"
    if binary_sha:
        body = f"#!/bin/sh\n# sha-override {binary_sha}\necho 'extension {version}'\n"
    binary_path.write_text(body, encoding="utf-8")
    binary_path.chmod(binary_path.stat().st_mode | stat.S_IEXEC)
    sha = hashlib.sha256(binary_path.read_bytes()).hexdigest()
    return ext_dir, sha


def tool_entry_yaml(name, version, sha256, **extra):
    """One tool entry as indented YAML, for use inside ``write_tool_registry``."""
    lines = [f"  - name: {name}", f"    version: \"{version}\"", f"    sha256: \"{sha256}\""]
    for key, value in extra.items():
        lines.append(f"    {key}: \"{value}\"")
    return "\n".join(lines)


def fake_tool(directory, name, version):
    """Write a fake tool shell script that prints ``version`` and return (path, sha256).

    Round-6 and round-7 cases use this pattern to test tool verification
    without depending on real tools installed on the machine.
    """
    path = Path(directory) / name
    body = f"#!/bin/sh\necho '{version}'\n"
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, sha


def tool_entry_with_location_yaml(name, version, sha256, location_prefix, **extra):
    """One tool entry with a PATH prefix, for use inside ``write_tool_registry``."""
    install = f'PATH={location_prefix}:$PATH {location_prefix}/{name} --version'
    lines = [
        f"  - name: {name}",
        f'    version: "{version}"',
        f'    sha256: "{sha256}"',
        f'    install: "{install}"',
        f'    uninstall: "rm -f {location_prefix}/{name}"',
        f'    date: "2026-01-01"',
        f'    approved_by: "test"',
    ]
    for key, value in extra.items():
        lines.append(f'    {key}: "{value}"')
    return "\n".join(lines)


def doctor_result(run):
    """Parse the doctor's JSON output and return the ``result`` object from the envelope."""
    envelope = run.envelope()
    return envelope.get("result", {})


def rebuild_result(run):
    """Parse the rebuild's JSON output and return the ``result`` object from the envelope."""
    envelope = run.envelope()
    return envelope.get("result", {})


def make_rebuild_project(cli, destination):
    """A tiny project for rebuild tests: ``.gitleaks.toml``, a path-map, and a test file.

    Rebuild goes through the lexical index's owner, which runs the secrets
    filter on every tracked file (DEC-440).  On the full tree (~955 files)
    this takes about 160 s; on a 3-file project it takes about 2–3 s.
    The code under test lives in ``cli`` (the session-scope copy) and is
    passed to ``run_gov_with_code`` as the code root.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    gitleaks = Path(cli) / ".gitleaks.toml"
    if gitleaks.is_file():
        shutil.copy2(gitleaks, destination / ".gitleaks.toml")
    git(destination, "init", "-q", "-b", "main")
    git(destination, "add", "-A")
    git(destination, "commit", "-q", "--allow-empty", "-m", "init")
    write_path_map(destination, minimal_valid_path_map())
    return destination


# Paths of the four kinds of historical records named in DEC-448.
HISTORICAL_RECORD_PATHS = [
    "docs/DECISION_REGISTER.md",
    "docs/changes/",
    "governance/project/bootstrap.md",
    "docs/source/",
]
