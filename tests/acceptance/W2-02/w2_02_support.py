"""Support code for the W2-02 acceptance tests (DAEO-zflj): the record types of the kernel, core-schema green here,
unmeasured types and the ``wbs_id`` grammar.

How the tests run:

- **Through public interfaces only**: the command the kernel declares for ``core-schema``
  (``template/governance/kernel/checks/core-schema.yaml``), run by ``sh -c`` in a project's root as ``gov check``
  runs it; its output (a JSON list of findings, each with a ``code`` and a ``path``) and its exit code. The kernel
  schema folder ``template/governance/kernel/schemas/`` is read as files. One case runs ``gov close`` (its console
  entry, ``gov.cli.main:main``) to obtain the close record as this worktree's ``gov close`` writes it.
- **This worktree's code** (DEC-732): every process a case starts has ``PYTHONPATH`` set to this worktree's
  ``src/`` (``SRC`` below, found from this file's place), so the subprocess imports the same ``gov`` as the suite.
- **Nothing is written in this worktree.** Every project is a temporary git repository built from scratch under
  pytest's ``tmp_path``; the kernel's schema files are copied into it one named file at a time. Only the cases of
  KPI line 2 run the check in this worktree's root, and they only read.
- **Deterministic, no network.**
"""

from __future__ import annotations

import json
import os
import site
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
KERNEL_SCHEMAS_REL = "template/governance/kernel/schemas"
COMMON_SCHEMA = "common.schema.json"
CORE_SCHEMA_DECLARATION = REPO_ROOT / "template/governance/kernel/checks/core-schema.yaml"

# The three verdicts of CAP-44.h (docs/contract/contract.yaml; DEC-722).
VERDICTS = ("ADOPTED_HEALTHY", "ADOPTED_WITH_ACCEPTED_EXCEPTIONS", "NOT_ADOPTED_HEALTHY")

# DEC-441: the frontmatter of an audit report.
AUDIT_FIELDS = ("milestone", "commit", "pack_sha256")

INVALID_TYPE = "SCHEMA_INVALID_TYPE"
UNKNOWN_TYPE = "SCHEMA_UNKNOWN_TYPE"

TIMEOUT_S = 300

OWNER = ("The Owner", "owner@example.invalid")


# --------------------------------------------------------------------------
# The environment of every process a case starts
# --------------------------------------------------------------------------

def env(home):
    """This worktree's ``src/`` on ``PYTHONPATH`` (DEC-732), a throwaway ``HOME``, and the per-user packages of the
    interpreter running the suite (found through ``HOME`` otherwise)."""
    found = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "TMPDIR": str(home),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }
    if site.ENABLE_USER_SITE:
        found["PYTHONUSERBASE"] = site.getuserbase()
    return found


# --------------------------------------------------------------------------
# The core-schema check
# --------------------------------------------------------------------------

def core_schema_command():
    """The command the kernel declares for ``core-schema``."""
    declaration = yaml.safe_load(CORE_SCHEMA_DECLARATION.read_text(encoding="utf-8"))
    return declaration["command"]


def run_core_schema(root, home):
    """Run the declared command by ``sh -c`` in ``root``: ``(exit code, findings)``. Nothing printed is no finding."""
    done = subprocess.run(["sh", "-c", core_schema_command()], cwd=str(root), env=env(home), capture_output=True,
                          text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    assert "Traceback" not in done.stderr, f"core-schema ended with a traceback:\n{done.stderr}"
    findings = json.loads(done.stdout) if done.stdout.strip() else []
    if isinstance(findings, dict):
        findings = findings.get("findings", [])
    assert isinstance(findings, list), f"core-schema printed no list of findings:\n{done.stdout}"
    return done.returncode, findings


def about(findings, rel):
    """The findings whose ``path`` is ``rel``."""
    return [finding for finding in findings if finding.get("path") == rel]


def names_field(finding, field):
    """The finding names ``field``: in its ``field`` key, or as a word of its message."""
    return finding.get("field") == field or field in str(finding.get("message", ""))


def says_unmeasured(finding):
    """The finding says "unmeasured" (or "not measured"), in its code or its message; case, ``_`` and ``-`` aside."""
    text = " ".join(str(finding.get(key, "")) for key in ("code", "message", "status")).lower()
    text = text.replace("_", " ").replace("-", " ")
    return "unmeasured" in text or "not measured" in text


# --------------------------------------------------------------------------
# A temporary project
# --------------------------------------------------------------------------

def git(root, *args, home):
    run_env = dict(env(home), GIT_AUTHOR_NAME=OWNER[0], GIT_AUTHOR_EMAIL=OWNER[1], GIT_COMMITTER_NAME=OWNER[0],
                   GIT_COMMITTER_EMAIL=OWNER[1], GIT_AUTHOR_DATE="2026-10-16T12:00:00Z",
                   GIT_COMMITTER_DATE="2026-10-16T12:00:00Z")
    done = subprocess.run(["git", "-C", str(root), *args], env=run_env, capture_output=True, text=True)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {root}:\n{done.stderr}"
    return done.stdout


class Project:
    """A temporary git repository that holds what its case writes and nothing else."""

    def __init__(self, base):
        base = Path(base)
        self.root = base / "project"
        self.home = base / "home"
        self.root.mkdir(parents=True)
        self.home.mkdir(parents=True)
        git(self.root, "init", "-q", "-b", "main", home=self.home)

    def kernel_schemas(self, leave_out=()):
        """The kernel template's schema files, each copied by name, as the file it is; ``leave_out`` names files
        not copied."""
        for path in sorted((REPO_ROOT / KERNEL_SCHEMAS_REL).glob("*.schema.json")):
            if path.name not in leave_out:
                self.write(f"{KERNEL_SCHEMAS_REL}/{path.name}", path.read_text(encoding="utf-8"))

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return rel

    def commit(self, message="fixture"):
        git(self.root, "add", "-A", home=self.home)
        git(self.root, "commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message, home=self.home)
        return git(self.root, "rev-parse", "HEAD", home=self.home).strip()

    def core_schema(self):
        self.commit("records")
        return run_core_schema(self.root, self.home)


def markdown(front, body="# A record\n\nBody text.\n"):
    """A Markdown file with ``front`` as its YAML frontmatter."""
    return "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---\n\n" + body


def frontmatter_of(text):
    """``(frontmatter, body)`` of a Markdown file's text."""
    assert text.startswith("---\n"), "the text has no frontmatter"
    end = text.index("\n---", 3)
    return yaml.safe_load(text[4:end]) or {}, text[end + len("\n---"):].lstrip("\n")


def shared(record_id, record_type, status="ACTIVE", state_class="AUTHORITATIVE", **more):
    """The shared frontmatter of a record (DEC-239) and ``more``."""
    return {"id": record_id, "type": record_type, "status": status, "state_class": state_class, **more}


def audit_report(commit, leave_out=()):
    """An audit report in DEC-441's form: ``milestone``, ``commit``, ``pack_sha256``, and one table of ``item``,
    ``class``, ``evidence``. ``leave_out`` names frontmatter fields not written."""
    front = {"milestone": "wave-9-exit", "commit": commit, "pack_sha256": "a" * 64}
    for field in leave_out:
        del front[field]
    body = ("# Wave 9 exit audit\n\nProse around the table is free.\n\n"
            "| item | class | evidence |\n|---|---|---|\n| CAP-01.a | OK | README.md |\n| DEC-000 | GAP | - |\n")
    return markdown(front, body)


AUDIT_REPORT_REL = "docs/audit/wave-9/W9-99-wave-9-exit-audit.md"


# --------------------------------------------------------------------------
# The kernel's schema files, read as files
# --------------------------------------------------------------------------

def kernel_schema_files():
    """``{file name: schema}`` of every kernel schema file but the shared definitions."""
    found = {}
    for path in sorted((REPO_ROOT / KERNEL_SCHEMAS_REL).glob("*.schema.json")):
        if path.name != COMMON_SCHEMA:
            found[path.name] = json.loads(path.read_text(encoding="utf-8"))
    return found


def common_schema():
    return json.loads((REPO_ROOT / KERNEL_SCHEMAS_REL / COMMON_SCHEMA).read_text(encoding="utf-8"))


def _resolved(entry):
    """``entry``, or the shared definition its ``$ref`` names."""
    ref = entry.get("$ref") if isinstance(entry, dict) else None
    if isinstance(ref, str) and ref.startswith(COMMON_SCHEMA + "#/$defs/"):
        return common_schema()["$defs"].get(ref.rsplit("/", 1)[1], {})
    return entry if isinstance(entry, dict) else {}


def _parts(schema):
    """The schema and every ``allOf`` entry of it, references to the shared definitions resolved."""
    parts = [schema]
    for entry in schema.get("allOf", []) or []:
        parts.append(_resolved(entry))
    return parts


def required_of(schema):
    """Every field the schema requires, its own and those of the shared parts it takes in."""
    found = set()
    for part in _parts(schema):
        found.update(part.get("required", []) or [])
    return found


def properties_of(schema):
    """``{name: subschema}`` of every property the schema and its shared parts state; the schema's own win."""
    found = {}
    for part in reversed(_parts(schema)):
        found.update(part.get("properties", {}) or {})
    return found


def type_of(schema):
    """The record type a schema is of: its ``type`` property's constant (or single enum value)."""
    shape = (schema.get("properties") or {}).get("type") or {}
    if "const" in shape:
        return shape["const"]
    if isinstance(shape.get("enum"), list) and len(shape["enum"]) == 1:
        return shape["enum"][0]
    return None


def schemas_of_type(record_type):
    return {name: schema for name, schema in kernel_schema_files().items() if type_of(schema) == record_type}


def verdict_schemas():
    """``{file name: (schema, field)}`` of the kernel schema files with a property whose values are exactly the
    three verdicts of CAP-44.h."""
    found = {}
    for name, schema in kernel_schema_files().items():
        for field, shape in properties_of(schema).items():
            shape = _resolved(shape)
            if isinstance(shape.get("enum"), list) and set(shape["enum"]) == set(VERDICTS):
                found[name] = (schema, field)
    return found


def the_verdict_type():
    """``(record type, verdict field)`` of the one adoption-verdict schema; fails the case when there is none."""
    found = verdict_schemas()
    assert len(found) == 1, (f"{KERNEL_SCHEMAS_REL} holds {len(found)} schema files with a property whose values are "
                             f"exactly {list(VERDICTS)}; one is expected: {sorted(found)}")
    name, (schema, field) = next(iter(found.items()))
    record_type = type_of(schema)
    assert record_type, f"{name} says no record type (no constant `type` property)"
    return record_type, field


# --------------------------------------------------------------------------
# A real close (``gov close``), for the close record as this worktree writes it
# --------------------------------------------------------------------------

CLOSE_TICKET = "PROJ-aaaa"
CLOSE_WBS = "W9-01"

_TICKET = """---
id: {ticket}
status: in_progress
deps: []
links: []
created: 2026-09-01T12:00:00Z
type: task
priority: 2
assignee: engineer
external-ref: {wbs}
tags: [test]
wbs_id: {wbs}
title: Ticket {wbs}
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
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
  path: tests/acceptance/{wbs}/
  author: independent-test-designer; written before implementation
---
# {wbs} A ticket

Body text.
"""

_GOV = "import sys\nfrom gov.cli.main import main\nsys.argv = ['gov', *sys.argv[1:]]\nsys.exit(main())\n"


def gov(project, *args):
    """``gov <args>`` through its console entry, in the project's root, with this worktree's code."""
    return subprocess.run([sys.executable, "-c", _GOV, *args], cwd=str(project.root), env=env(project.home),
                          capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)


def _commit_as(project, message, trailers):
    git(project.root, "add", "-A", home=project.home)
    args = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message]
    for trailer in trailers:
        args += ["--trailer", trailer]
    git(project.root, *args, home=project.home)


def closed_ticket(base):
    """A project whose one ticket is closed by ``gov close``: ``(project, close record path, its text)``.

    The project holds what a close needs and nothing else: a path map with two workers, the kernel's schema files,
    one check declaration of its own (``true``), the kernel's ticket tool, the source the ticket names, the ticket
    in progress, a passing acceptance test, an engineer's commit with ``Task:``, ``Role:`` and ``Implements:``, a
    checkpoint and a loaded record store.
    """
    project = Project(base)
    ticket, wbs = CLOSE_TICKET, CLOSE_WBS
    project.write(".gitignore", ".gov-runtime/\n")
    project.write("governance/project/path-map.yaml", "namespaces: {}\nclose_workers: 2\n")
    project.kernel_schemas()
    project.write("template/governance/kernel/checks/trivial.yaml",
                  'id: "trivial"\nfamily: "schema/invariants"\ntier: "G1"\nseverity: "hard-block"\ncommand: "true"\n')
    tk = REPO_ROOT / "template/governance/kernel/bin/tk"
    project.write("governance/kernel/bin/tk", tk.read_text(encoding="utf-8"))
    (project.root / "governance/kernel/bin/tk").chmod(0o755)
    project.write("docs/adr/DEC-000.md", markdown(shared("DEC-000", "decision", title="The base decision")))
    _commit_as(project, "initial project", ())
    project.write(f".tickets/{ticket}.md", _TICKET.format(ticket=ticket, wbs=wbs))
    _commit_as(project, "ticket", ("Role: orchestrator",))
    project.write(f"tests/acceptance/{wbs}/README.md", f"# {wbs}\n")
    project.write(f"tests/acceptance/{wbs}/test_pass.py", "def test_pass():\n    assert True\n")
    _commit_as(project, "acceptance tests", (f"Task: {ticket}", "Role: independent-test-designer",
                                             "Implements: DEC-000"))
    project.write("src/example/feature.py", "# feature\n")
    _commit_as(project, "implement", (f"Task: {ticket}", "Role: engineer", "Implements: DEC-000"))
    done = gov(project, "checkpoint", "--ticket", ticket, "--trigger", "stop", "--next", "resume", "--json")
    assert done.returncode == 0, f"the fixture's gov checkpoint failed:\n{done.stdout}\n{done.stderr}"
    _commit_as(project, "checkpoint", ("Role: orchestrator",))
    done = subprocess.run([sys.executable, "-c", "import sys\nfrom gov.store import load\nload(sys.argv[1])\n",
                           str(project.root)], cwd=str(project.root), env=env(project.home), capture_output=True,
                          text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"the fixture's store load failed:\n{done.stdout}\n{done.stderr}"
    done = gov(project, "close", ticket, "--json")
    assert done.returncode == 0, f"the fixture's gov close did not close the ticket:\n{done.stdout}\n{done.stderr}"
    rel = json.loads(done.stdout)["result"]["close_record"]
    text = (project.root / rel).read_text(encoding="utf-8")
    return project, rel, text
