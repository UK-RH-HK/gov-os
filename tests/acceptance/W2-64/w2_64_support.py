"""Support code for the W2-64 acceptance tests (DAEO-0uhh): core-schema through check-jsonschema, the close
schema's evidence block, and ``docs/imported/`` left out of the schema check.

How the tests run:

- **Through public interfaces only**: the command the kernel declares for ``core-schema``
  (``template/governance/kernel/checks/core-schema.yaml``, ``python3 -m gov.check.schema``), run by ``sh -c`` in a
  project's root as ``gov check`` runs it, with its exit code and its output; ``gov check --json`` and its
  ``core-schema`` entry; the kernel's schema files, copied one named file at a time; check-jsonschema itself.
- **This worktree's code** (DEC-732): every process a case starts has ``PYTHONPATH`` set to this worktree's ``src/``
  (``SRC``, found from this file's place). ``python3`` on the case's ``PATH`` is a wrapper that runs the interpreter
  running the suite.
- **The validator on PATH is the case's choice.** A case's ``PATH`` is ``<case>/bin`` (the ``python3`` wrapper and
  ``git``), then one folder of the case's (nothing; a link to the installed check-jsonschema; or a stand-in), then
  ``/usr/bin:/bin``. No other folder of the machine is on it.
- **Nothing is written in this worktree.** Every project is a temporary git repository built from scratch under
  pytest's ``tmp_path``. Only the live cases run in this worktree's root, and they only read.
"""

from __future__ import annotations

import json
import os
import shutil
import site
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
KERNEL_SCHEMAS_REL = "template/governance/kernel/schemas"
INSTALLED_SCHEMAS_REL = "governance/kernel/schemas"
CHECKS_REL = "template/governance/kernel/checks"
CORE_SCHEMA_DECLARATION = REPO_ROOT / CHECKS_REL / "core-schema.yaml"
REGISTRY_REL = "governance/project/tool-registry.yaml"
TOOL = "check-jsonschema"
IMPORTED = "docs/imported/"
CHECK_ID = "core-schema"

MISSING_FIELD = "SCHEMA_MISSING_FIELD"
INVALID_FIELD = "SCHEMA_INVALID_FIELD"
INVALID_TYPE = "SCHEMA_INVALID_TYPE"
UNKNOWN_TYPE = "SCHEMA_UNKNOWN_TYPE"
UNREADABLE = "SCHEMA_UNREADABLE"
REFUSALS = (MISSING_FIELD, INVALID_FIELD)

TIMEOUT_S = 300
OWNER = ("The Owner", "owner@example.invalid")


# --------------------------------------------------------------------------
# The validator: the installed one, and its pin in this repository's registry
# --------------------------------------------------------------------------

def installed_tool():
    """The installed check-jsonschema: on the suite's PATH, or at ``~/.local/bin``. A case that needs it fails
    without it; it is never skipped (KPI failure line 2)."""
    found = shutil.which(TOOL) or str(Path.home() / ".local/bin" / TOOL)
    if not os.access(found, os.X_OK):
        pytest.fail(f"{TOOL} is not installed ({found}): the case needs the real validator")
    return Path(found)


def pinned_entry():
    """The ``check-jsonschema`` entry of this repository's tool registry (DEC-074), read by name."""
    registry = yaml.safe_load((REPO_ROOT / REGISTRY_REL).read_text(encoding="utf-8"))
    entries = [tool for tool in registry["tools"] if tool.get("name") == TOOL]
    assert len(entries) == 1, f"{REGISTRY_REL} holds {len(entries)} entries named {TOOL}"
    return entries[0]


def pinned_version():
    return str(pinned_entry()["version"])


OTHER_VERSION = "0.37.0"


# --------------------------------------------------------------------------
# A case's place: its bin, its HOME, and the validator folder it puts on PATH
# --------------------------------------------------------------------------

STAND_INS = {
    # prints text that is not the JSON answer and exits 1
    "prints-text": "print('Traceback (most recent call last):\\n  something broke')\nsys.exit(1)\n",
    # exits 0 and prints nothing
    "silent-exit-0": "sys.exit(0)\n",
    # answers `ok` naming none of the instances it was given
    "names-no-instance": "print(json.dumps({'status': 'ok', 'checked_paths': []}))\nsys.exit(0)\n",
    # is killed
    "killed": "os.kill(os.getpid(), signal.SIGKILL)\n",
    # an error exit with no output, for every call (its --version included)
    "fails-every-call": None,
}


class Place:
    """A temporary folder for one case: ``bin`` (python3, git), ``home``, and a validator folder."""

    def __init__(self, base):
        self.base = Path(base)
        self.bin = self.base / "bin"
        self.home = self.base / "home"
        self.validator = self.base / "validator"
        for folder in (self.bin, self.home, self.validator):
            folder.mkdir(parents=True, exist_ok=True)
        for tool, found in (("python3", sys.executable), ("git", shutil.which("git"))):
            wrapper = self.bin / tool
            wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
            wrapper.chmod(0o755)

    # the validator the case gives

    def real_tool(self):
        """A link to the installed check-jsonschema, alone in the validator folder."""
        (self.validator / TOOL).symlink_to(installed_tool())
        return self

    def no_tool(self):
        """No check-jsonschema anywhere on PATH."""
        assert shutil.which(TOOL, path=self.path()) is None, f"{TOOL} is on {self.path()}"
        return self

    def stand_in(self, kind):
        """A check-jsonschema stand-in: answers ``--version`` with the pinned version, and behaves as ``kind``."""
        body = STAND_INS[kind]
        if body is None:
            script = "#!/bin/sh\nexit 2\n"
        else:
            script = (f"#!{sys.executable}\nimport json, os, signal, sys\n"
                      f"if '--version' in sys.argv[1:]:\n"
                      f"    print('{TOOL}, version {pinned_version()}')\n    sys.exit(0)\n{body}")
        self._write_tool(script)
        return self

    def other_version(self):
        """A stand-in that answers ``--version`` with another version than the pin and runs the real tool for
        everything else."""
        real = installed_tool()
        self._write_tool(f"#!/bin/sh\nfor a in \"$@\"; do\n  if [ \"$a\" = --version ]; then\n"
                         f"    echo '{TOOL}, version {OTHER_VERSION}'\n    exit 0\n  fi\ndone\n"
                         f"exec \"{real}\" \"$@\"\n")
        return self

    def answers_exit_0(self):
        """A stand-in that runs the real tool, prints its answer, and exits 0 whatever the answer."""
        real = installed_tool()
        self._write_tool(f"#!/bin/sh\n\"{real}\" \"$@\"\nexit 0\n")
        return self

    def not_executable(self):
        """A check-jsonschema on PATH that cannot be executed."""
        path = self.validator / TOOL
        path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        path.chmod(0o644)
        return self

    def _write_tool(self, script):
        path = self.validator / TOOL
        path.write_text(script, encoding="utf-8")
        path.chmod(0o755)

    # the environment

    def path(self):
        return f"{self.bin}:{self.validator}:/usr/bin:/bin"

    def env(self):
        found = {
            "PATH": self.path(),
            "HOME": str(self.home),
            "LC_ALL": "C.UTF-8",
            "PYTHONPATH": str(SRC),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
        }
        if os.environ.get("TMPDIR"):
            found["TMPDIR"] = os.environ["TMPDIR"]
        if site.ENABLE_USER_SITE:
            found["PYTHONUSERBASE"] = site.getuserbase()
        return found


# --------------------------------------------------------------------------
# core-schema, as declared, and what it printed
# --------------------------------------------------------------------------

class Run:
    def __init__(self, done, root):
        self.code, self.stdout, self.stderr, self.root = done.returncode, done.stdout, done.stderr, root
        self.output = None
        if done.stdout.strip():
            try:
                self.output = json.loads(done.stdout)
            except ValueError:
                self.output = None

    @property
    def findings(self):
        """The findings: a printed list, or the ``findings`` of a printed object; the success form
        (``{"ok": true, "result": ...}``) and nothing printed are no finding."""
        if isinstance(self.output, list):
            return self.output
        if isinstance(self.output, dict):
            if self.output.get("ok") is True and "result" in self.output:
                return []
            found = self.output.get("findings", [])
            return found if isinstance(found, list) else [found]
        return []

    def describe(self):
        return f"exit {self.code}\n--- stdout ---\n{self.stdout[:4000]}\n--- stderr ---\n{self.stderr[:2000]}"

    def is_red(self):
        """RED as ``gov check`` reads it: a non-zero exit, and at least one finding or no readable answer."""
        return self.code != 0

    def text(self):
        return self.stdout


def core_schema_command():
    return yaml.safe_load(CORE_SCHEMA_DECLARATION.read_text(encoding="utf-8"))["command"]


def run_core_schema(root, place):
    done = subprocess.run(["sh", "-c", core_schema_command()], cwd=str(root), env=place.env(), capture_output=True,
                          text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    run = Run(done, root)
    assert "Traceback" not in done.stderr, f"core-schema ended with a traceback\n{run.describe()}"
    return run


def run_gov_check(root, place):
    """``gov check --json`` in ``root``: ``(run, the core-schema entry)``."""
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "check", "--json"], cwd=str(root), env=place.env(),
                          capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    run = Run(done, root)
    assert isinstance(run.output, dict), f"gov check --json printed no JSON object\n{run.describe()}"
    result = run.output.get("result") or (run.output.get("error") or {}).get("details") or {}
    checks = result.get("checks") or result.get("results") or []
    entries = [entry for entry in checks if isinstance(entry, dict) and CHECK_ID in (entry.get("id"),
                                                                                       entry.get("check_id"))]
    assert len(entries) == 1, f"gov check --json holds {len(entries)} {CHECK_ID} entries\n{run.describe()}"
    return run, entries[0]


def about(findings, rel):
    return [finding for finding in findings if finding.get("path") == rel]


def text_of(finding):
    return json.dumps(finding, sort_keys=True, default=str)


def names_rule(finding, schema_file, place, words=()):
    """The finding names the rule: the schema file, the place in the record, and the validator's message (here,
    ``words`` that the validator's message holds)."""
    text = text_of(finding)
    return schema_file in text and place in text and all(word in text for word in words)


def strings_in(value):
    """Every string inside ``value``, at any depth."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from strings_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings_in(item)


def integers_in(value):
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from integers_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from integers_in(item)


def says_imported_left_out(output):
    """The output names ``docs/imported/`` and says why it is left out: as history, or by DEC-844."""
    text = " ".join(strings_in(output)).lower()
    return "docs/imported" in text and ("history" in text or "dec-844" in text)


# --------------------------------------------------------------------------
# A temporary project
# --------------------------------------------------------------------------

def git(root, *args, place):
    env = dict(place.env(), GIT_AUTHOR_NAME=OWNER[0], GIT_AUTHOR_EMAIL=OWNER[1], GIT_COMMITTER_NAME=OWNER[0],
               GIT_COMMITTER_EMAIL=OWNER[1], GIT_AUTHOR_DATE="2026-10-30T12:00:00Z",
               GIT_COMMITTER_DATE="2026-10-30T12:00:00Z")
    done = subprocess.run(["git", "-C", str(root), *args], env=env, capture_output=True, text=True)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {root}:\n{done.stderr}"
    return done.stdout


class Project:
    """A temporary git repository holding what its case writes, and nothing else."""

    def __init__(self, place):
        self.place = place
        self.root = place.base / "project"
        self.root.mkdir(parents=True)
        git(self.root, "init", "-q", "-b", "main", place=place)

    def kernel_schemas(self, leave_out=(), layout=KERNEL_SCHEMAS_REL):
        """The kernel template's schema files, each copied by name; ``leave_out`` names files not copied."""
        for path in sorted((REPO_ROOT / KERNEL_SCHEMAS_REL).glob("*.schema.json")):
            if path.name not in leave_out:
                self.write(f"{layout}/{path.name}", path.read_text(encoding="utf-8"))
        return self

    def registry(self, version=None):
        """A tool registry with this repository's check-jsonschema entry (``version`` replacing its pin)."""
        entry = dict(pinned_entry())
        if version is not None:
            entry["version"] = version
        self.write(REGISTRY_REL, yaml.safe_dump({"tools": [entry]}, sort_keys=False))
        return self

    def declaration(self):
        """The kernel's core-schema declaration, copied by name."""
        self.write(f"{CHECKS_REL}/core-schema.yaml", CORE_SCHEMA_DECLARATION.read_text(encoding="utf-8"))
        return self

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return rel

    def core_schema(self):
        git(self.root, "add", "-A", place=self.place)
        git(self.root, "commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", "records", place=self.place)
        return run_core_schema(self.root, self.place)

    def gov_check(self):
        git(self.root, "add", "-A", place=self.place)
        git(self.root, "commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", "records", place=self.place)
        return run_gov_check(self.root, self.place)


def markdown(front, body="# A record\n\nBody text.\n"):
    return "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---\n\n" + body


def frontmatter_of(text):
    lines = text.split("\n")
    assert lines[0].strip() == "---", "the text has no frontmatter"
    end = lines.index("---", 1)
    return yaml.safe_load("\n".join(lines[1:end])), "\n".join(lines[end + 1:])


def shared(record_id, record_type, status="ACTIVE", state_class="AUTHORITATIVE", **more):
    return {"id": record_id, "type": record_type, "status": status, "state_class": state_class, **more}


# A ticket that every kernel schema takes: the shape of this repository's tickets. `created` is left unquoted, a
# YAML timestamp, as tk writes it.
VALID_TICKET = """---
id: PROJ-aaaa
status: in_progress
deps: [PROJ-bbbb]
links: []
created: 2026-09-01T12:00:00Z
type: task
priority: 2
assignee: engineer
external-ref: W9-01
tags: [test]
wbs_id: W9-01
title: Ticket W9-01
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [W9-00]
allowed_paths:
- src/example/**
kpis:
  success:
  - It works
  failure:
  - It does not work
profile: STANDARD
sources:
- DEC-000
est_loc: 10
acceptance_tests:
  path: tests/acceptance/W9-01/
  author: independent-test-designer
---
# W9-01 A ticket

Body text.
"""


def ticket(**changes):
    """The valid ticket with ``changes`` to its frontmatter (a value of None removes the key)."""
    front, body = frontmatter_of(VALID_TICKET)
    for key, value in changes.items():
        if value is None:
            front.pop(key, None)
        else:
            front[key] = value
    return markdown(front, body)


# Run G-4's planted ticket (lens G, F2): six faults.
PLANTED = {"status": "banana", "state_class": "NOT-A-CLASS", "profile": "HUGE", "est_loc": -5,
           "deps": ["not an id"], "allowed_paths": [], "kpis": {}}

# The close records of this repository the cases copy, each a single named file.
CLOSE_WITH_EVIDENCE = "docs/close/DAEO-c1uz/CL-DAEO-c1uz.md"
CLOSE_BASE_UNKNOWN = "docs/close/DAEO-uzme/CL-DAEO-uzme.md"
CLOSE_BEFORE_W2_66 = "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md"

# The evidence block's fields W2-66's close writes, each required (the lead's design note, item 5; DEC-890 item 1).
EVIDENCE_REQUIRED = ("scope", "why_full", "base", "head", "tree", "changed", "selected", "left_out", "skips",
                     "skip_count", "failures", "junit_xml")


def close_record(rel=CLOSE_WITH_EVIDENCE):
    """``(frontmatter, body)`` of one of this repository's close records."""
    return frontmatter_of((REPO_ROOT / rel).read_text(encoding="utf-8"))
