"""Support code for the round 15 cases of the W1-30 suite (the fix round before adoption: DEC-612, DEC-613,
DEC-616, DEC-620).

A round 15 project is a temporary git repository that holds only what its case writes: no copy of ``src/``, no
copy of the kernel. The code that runs is this worktree's ``src/`` (``w1_30_support.run_gov`` puts it on
``PYTHONPATH``, and the runner of ``gov check`` hands that on to every check command). A kernel declaration or
schema a case needs is copied as the single named file it is.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

import w1_30_support as support

cli_support = support.cli_support
tasks_support = support.tasks_support

REPO_ROOT = support.REPO_ROOT
TEMPLATE_KERNEL = "template/governance/kernel"
INSTALLED_KERNEL = "governance/kernel"
LAYOUTS = {"template": TEMPLATE_KERNEL, "installed": INSTALLED_KERNEL}
CHECKS_REL = f"{TEMPLATE_KERNEL}/checks"
SCHEMAS_REL = f"{TEMPLATE_KERNEL}/schemas"
PATH_MAP_REL = support.PATH_MAP_REL

RED, YELLOW, GREEN = support.RED, support.YELLOW, support.GREEN
HARD_BLOCK, WARNING = support.HARD_BLOCK, support.WARNING
INFORMATIONAL = "informational"
INVALID = "CHECK_DECLARATION_INVALID"
CHECK_FAILED = "CHECK_FAILED"
NOT_COVERED = "POLICY_NOT_COVERED"
EXIT_OK, EXIT_REFUSED, EXIT_CHECK_FAILED = 0, 1, 3

ENFORCES = "enforces"            # the list field of a declaration (DEC-620)
TIMEOUT = "timeout-seconds"      # DEC-595
FIELDS = ("id", "family", "tier", "severity", "command")
A_FAMILY = "graph integrity"     # one of the seventeen: a declaration of an unknown family is never green (DEC-436)

# The thirteen policy keys and their kernel minimum (DEC-230, DEC-238), as W1-26's support holds them.
POLICIES = dict(support.check_support.POLICIES)


def kernel_declaration_path(check_id):
    return REPO_ROOT / CHECKS_REL / f"{check_id}.yaml"


def kernel_declaration(check_id):
    """The kernel template's declaration of one check, as the file states it."""
    path = kernel_declaration_path(check_id)
    assert path.is_file(), f"the kernel template declares no check {check_id!r} ({CHECKS_REL}/{check_id}.yaml)"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(document, dict), f"{CHECKS_REL}/{check_id}.yaml is not a map"
    return document


def kernel_declarations():
    """``check id -> declaration`` of every declaration file of the kernel template."""
    found = {}
    for path in sorted((REPO_ROOT / CHECKS_REL).glob("*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(document, dict) and isinstance(document.get("id"), str), f"{path.name} is no declaration"
        found[document["id"]] = document
    return found


def declaration_text(check_id, command="true", family=A_FAMILY, severity=HARD_BLOCK, tier="G1", **raw):
    """A declaration file's text. ``raw`` is ``key -> the value as YAML writes it``, beside the five fields."""
    fields = {"id": check_id, "family": family, "tier": tier, "severity": severity, "command": command}
    text = "".join(f"{key}: {json.dumps(value)}\n" for key, value in fields.items())
    return text + "".join(f"{key.replace('_', '-')}: {value}\n" for key, value in raw.items())


def policies_text(policies):
    """A path map that holds the ``policies`` block given and no namespace; without a key, no block."""
    if not policies:
        return "namespaces: {}\n"
    return "namespaces: {}\npolicies:\n" + "".join(f"  {key}: {strength}\n" for key, strength in policies.items())


def ticket_text(ticket_id, wbs, **keys):
    """A ticket file as the ticket tool and the orchestrator write it (``type: task``; W1-09's support), in
    progress, naming the one source every project of this module holds (``BASE_SOURCE``)."""
    keys.setdefault("status", "in_progress")
    return tasks_support.ticket_text(ticket_id, wbs, **keys)


def record_text(record_id, record_type, status="ACTIVE", state_class="AUTHORITATIVE", **more):
    """A record that holds the shared frontmatter (``id``, ``type``, ``status``, ``state_class``) and ``more``.
    ``state_class=None`` leaves that field out."""
    front = {"id": record_id, "type": record_type, "status": status}
    if state_class is not None:
        front["state_class"] = state_class
    front.update(more)
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# " + record_id + "\n\nA record.\n"


class Scratch:
    """A temporary git repository that holds what its case writes and nothing else."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True)
        support.git(self.root, "init", "-q", "-b", "main")
        self.write("README.md", "# A project\n")
        self.write(".gitignore", ".gov-runtime/\n")

    def write(self, rel, text):
        support.write(self.root, rel, text)
        return rel

    def remove(self, rel):
        (self.root / rel).unlink()

    def commit(self, message="fixture"):
        return support.commit_all(self.root, message)

    def declare(self, check_id, command="true", layout="template", **keys):
        return self.write(f"{LAYOUTS[layout]}/checks/{check_id}.yaml", declaration_text(check_id, command, **keys))

    def declare_as_the_kernel_does(self, check_id):
        """This project's copy of the one declaration file the kernel template holds for ``check_id``."""
        rel = f"{CHECKS_REL}/{check_id}.yaml"
        (self.root / CHECKS_REL).mkdir(parents=True, exist_ok=True)
        shutil.copy2(kernel_declaration_path(check_id), self.root / rel)
        return rel

    def kernel_schemas(self):
        """This project's copies of the kernel template's schema files, each copied as the file it is."""
        (self.root / SCHEMAS_REL).mkdir(parents=True, exist_ok=True)
        for path in sorted((REPO_ROOT / SCHEMAS_REL).glob("*.schema.json")):
            shutil.copy2(path, self.root / SCHEMAS_REL / path.name)

    def base_source(self):
        """The decision every fixture ticket names under ``sources``."""
        return self.write(f"docs/adr/{support.BASE_SOURCE}.md",
                          support.decision(support.BASE_SOURCE, "ACTIVE", title="The base decision"))

    def gov(self, sandbox, *args, env=None, commit=True):
        if commit:
            self.commit()
        return support.run_gov(self.root, sandbox, *args, env=env)

    def load_store(self, sandbox):
        """The record store loaded from the committed files, as ``gov.store.load(root)`` loads it."""
        self.commit()
        support.load_store(self, sandbox)


def check_body(run):
    """What ``gov check --json`` says of the checks: ``result`` when it passed, ``error.details`` when a
    hard-block check failed. A refusal of the command itself fails the case."""
    envelope = run.envelope()
    error = envelope.get("error") or {}
    assert envelope.get("ok") is True or error.get("code") == CHECK_FAILED, \
        f"gov check neither passed nor failed on a check: it was refused\n{run.describe()}"
    body = envelope["result"] if envelope.get("ok") else error.get("details") or {}
    assert isinstance(body.get("checks"), list), f"gov check named no check\n{run.describe()}"
    return body


def checked(project, sandbox, env=None, commit=True):
    """``gov check --json`` in the project: ``({check id: entry}, run)``."""
    run = project.gov(sandbox, "check", "--json", env=env, commit=commit)
    return {entry["id"]: entry for entry in check_body(run)["checks"] if isinstance(entry, dict)}, run


def status_of(project, sandbox, check_id, env=None, commit=True):
    """``(status, entry, run)`` of one declared check after ``gov check --json``."""
    entries, run = checked(project, sandbox, env=env, commit=commit)
    assert check_id in entries, f"gov check ran no check {check_id!r}: {sorted(entries)}\n{run.describe()}"
    return entries[check_id]["status"], entries[check_id], run


def listed(project, sandbox):
    """``{check id: entry}`` of ``gov check --list --json``; a refusal fails the case."""
    run = project.gov(sandbox, "check", "--list", "--json")
    envelope = run.envelope()
    assert envelope.get("ok") is True and run.returncode == EXIT_OK, \
        f"gov check --list did not list the declarations\n{run.describe()}"
    return {entry["id"]: entry for entry in envelope["result"]["checks"]}, run


def refused(project, sandbox, *args):
    """The error of a command that is refused as a command (exit code 1), and the run."""
    run = project.gov(sandbox, *args)
    envelope = run.envelope()
    assert envelope.get("ok") is False and run.returncode == EXIT_REFUSED, \
        f"gov {' '.join(args)} was not refused with exit code {EXIT_REFUSED}\n{run.describe()}"
    return envelope["error"], run


def policy_entries(entries):
    """``{policy key: entry}`` of the entries that report a policy key no check covers."""
    return {entry["findings"][0].get("policy"): entry for entry in entries.values()
            if any(isinstance(finding, dict) and finding.get("code") == NOT_COVERED
                   for finding in entry.get("findings") or [])}


def script(folder, name, body):
    """An executable shell script outside the project: what a declared command runs."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    path.chmod(0o755)
    return str(path)


def env_with_gov(sandbox):
    """The environment of a case whose declared command is a ``gov`` command: ``gov`` on ``PATH`` is this
    worktree's command line (W1-07's console-script stand-in), whatever is installed on the machine."""
    launcher = cli_support.write_launcher(REPO_ROOT, sandbox)
    folder = sandbox.bin / "on-path"
    folder.mkdir(parents=True, exist_ok=True)
    shim = folder / "gov"
    shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{launcher}" "$@"\n', encoding="utf-8")
    shim.chmod(0o755)
    env = support.sandbox_env(sandbox)
    env["PATH"] = f"{folder}:{env['PATH']}"
    return env


def run_declared_command(check_id, project, sandbox, env=None):
    """The kernel template's declared command of ``check_id``, run by ``sh -c`` in the project root as the
    runner runs it (DEC-285): the completed process."""
    command = kernel_declaration(check_id)["command"]
    return subprocess.run(["sh", "-c", command], cwd=str(project.root), env=env or support.sandbox_env(sandbox),
                          capture_output=True, text=True, timeout=cli_support.COMMAND_TIMEOUT_S,
                          stdin=subprocess.DEVNULL)
