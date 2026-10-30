"""Support code for the W2-03 acceptance tests (DAEO-ym8a): decisions as records, each with its own hash.

How the tests run:

- **Through public interfaces only** (the README, "How the suite runs"):
  - the store as ``gov rebuild`` builds it: ``gov.store.load(root)``, then the record query
    ``gov.records.records(root)``;
  - the decision checker: ``gov.decisions.check(root)``, a list of findings, each with ``code``, ``ids``,
    ``paths`` and ``message`` (W1-11's interface);
  - the decision-citations check as ``gov check`` runs it: the command the kernel declares in
    ``template/governance/kernel/checks/core-decision-citations.yaml``, by ``sh -c`` in a project's root; its JSON
    object (findings ``{"code": "DECISION_UNRECORDED", "commit": ..., "decision": ...}``) and its exit code
    (W1-26's interface).
- **This worktree's code** (DEC-732): every process a case starts gets ``env()`` below, whose ``PYTHONPATH`` is this
  worktree's ``src/`` (``SRC``, found from this file's own place).
- **Nothing is written in this worktree.** Every project is a temporary git repository built from scratch under
  pytest's ``tmp_path``. One case reads this repository's ``docs/DECISION_REGISTER.md`` (read-only) and commits its
  text into a temporary project.
- **Deterministic, no network.** Fixed authors and dates; every call in a new process.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import site
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
OWN_REGISTER = REPO_ROOT / "docs" / "DECISION_REGISTER.md"
PATH_MAP_SCHEMA = REPO_ROOT / "template" / "governance" / "kernel" / "schemas" / "path-map.schema.json"
CITATIONS_DECLARATION = REPO_ROOT / "template" / "governance" / "kernel" / "checks" / "core-decision-citations.yaml"

PATH_MAP_REL = "governance/project/path-map.yaml"
REGISTER_KEY = "decision_register"            # DEC-479
REGISTER_REL = "records/decision-log.md"      # no file of this repository has this path

HASH_KEY = "content_hash"                     # reading R1 (README): DEC-012, W2-L031, common.schema.json
SPAN_KEY = "span"                             # reading R1: register-entry.schema.json

UNRECORDED = "DECISION_UNRECORDED"
CALL_TIMEOUT_S = 180.0
MISSING_EXIT = 3

# After DEC-463 (2026-10-07) and the trailer rule (2026-10-03), in every time zone.
DATE = "2026-10-09T{hour:02d}:{minute:02d}:00+00:00"
OWNER = {"name": "The Owner", "email": "owner@example.invalid", "trailers": ("Role: owner",)}
AGENT = {"name": "An Agent", "email": "agent@example.invalid", "trailers": ("Task: PROJ-aaaa", "Role: engineer")}

POLICIES = {
    "security": "hard-block", "authority": "hard-block", "test": "hard-block", "change": "hard-block",
    "human_gate": "hard-block", "tool": "hard-block", "memory": "warning", "context": "warning",
    "checkpoint": "warning", "model_routing": "informational", "budget": "informational",
    "learning": "informational", "archive": "informational",
}


# --------------------------------------------------------------------------
# The environment of every process a case starts (DEC-732)
# --------------------------------------------------------------------------

def env(home):
    """This worktree's ``src/`` on ``PYTHONPATH``, a throwaway ``HOME``, and the per-user packages of the
    interpreter running the suite (found through ``HOME`` otherwise)."""
    home = Path(home)
    found = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "TMPDIR": str(home),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }
    if site.ENABLE_USER_SITE:
        found["PYTHONUSERBASE"] = site.getuserbase()
    return found


# --------------------------------------------------------------------------
# The store, the record query and the decision checker, each batch in a new process
# --------------------------------------------------------------------------

_DRIVER = '''\
import importlib, json, sys
from pathlib import Path

out = []
for call in json.loads(sys.stdin.read()):
    try:
        function = getattr(importlib.import_module(call["module"]), call["function"])
    except (ModuleNotFoundError, AttributeError) as exc:
        print(f"{call['module']}.{call['function']} cannot be imported: {exc}", file=sys.stderr)
        sys.exit(3)
    try:
        out.append({"value": function(Path(call["root"]), **call["kwargs"])})
    except Exception as exc:
        if type(exc).__name__ != "GovError":
            raise
        out.append({"error": {"code": exc.code, "message": exc.message, "details": exc.details}})
print(json.dumps(out, default=str))
'''


class Api:
    """Calls ``gov.store``, ``gov.records`` and ``gov.decisions`` of this worktree."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")

    def batch(self, calls):
        """``[(module, function, root, kwargs), ...]`` in one process: ``[{"value": ...} | {"error": ...}]``."""
        request = [{"module": m, "function": f, "root": str(r), "kwargs": k} for m, f, r, k in calls]
        what = ", ".join(f"{m}.{f}" for m, f, _, _ in calls)
        try:
            done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request),
                                  env=env(self.workdir), cwd=str(self.workdir), capture_output=True, text=True,
                                  timeout=CALL_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {CALL_TIMEOUT_S:.0f} s") from None
        assert done.returncode != MISSING_EXIT, done.stderr.strip()
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr[-3000:]}"
        return json.loads(done.stdout)

    def load_and_records(self, root):
        """``gov.store.load(root)`` then ``gov.records.records(root)``: ``(summary, records)``."""
        loaded, listed = self.batch([("gov.store", "load", root, {}), ("gov.records", "records", root, {})])
        assert "value" in loaded, f"gov.store.load refused: {loaded.get('error')}"
        assert "value" in listed, f"gov.records.records refused: {listed.get('error')}"
        summary, records = loaded["value"], listed["value"]
        assert isinstance(summary, dict) and isinstance(summary.get("invalid"), list), \
            f"load did not return a summary with `invalid`: {summary!r}"
        assert isinstance(records, list) and all(isinstance(r, dict) for r in records), \
            f"records did not return a list of maps: {records!r}"
        return summary, records

    def check_decisions(self, root):
        """``gov.store.load(root)`` then ``gov.decisions.check(root)``: the findings."""
        loaded, checked = self.batch([("gov.store", "load", root, {}), ("gov.decisions", "check", root, {})])
        assert "value" in loaded, f"gov.store.load refused: {loaded.get('error')}"
        assert "value" in checked, f"gov.decisions.check refused instead of reporting: {checked.get('error')}"
        found = checked["value"]
        assert isinstance(found, list), f"check did not return a list of findings: {found!r}"
        for finding in found:
            assert isinstance(finding, dict) and isinstance(finding.get("code"), str), f"not a finding: {finding!r}"
            for key in ("ids", "paths"):
                assert isinstance(finding.get(key), list), f"a finding's `{key}` is not a list: {finding!r}"
        return found


def by_id(records):
    found = {}
    for record in records:
        found.setdefault(record.get("id"), []).append(record)
    return found


def register_records(records, register_rel=REGISTER_REL):
    """``id -> record`` of the records the store placed in the register file; each id once."""
    found = {}
    for record in records:
        if record.get("path") == register_rel:
            assert record.get("id") not in found, f"{record.get('id')} is recorded twice from the register"
            found[record["id"]] = record
    return found


def sha256_hex(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_sha256(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def show_findings(found):
    return "\n".join(f"  {f.get('code')} ids={f.get('ids')} paths={f.get('paths')}: {f.get('message')}"
                     for f in found) or "  (none)"


def invalid_naming(summary, word, path=None):
    """The ``invalid`` entries whose reason names ``word`` as a whole word (and whose path is ``path``)."""
    pattern = re.compile(rf"(?<![\w-]){re.escape(word)}(?![\w-])")
    return [entry for entry in summary["invalid"]
            if isinstance(entry, dict) and (path is None or entry.get("path") == path)
            and pattern.search(json.dumps(entry, ensure_ascii=False))]


def line_of(text, line):
    """The 1-based number of the one line of ``text`` that is exactly ``line``."""
    numbers = [n for n, found in enumerate(text.split("\n"), start=1) if found == line]
    assert len(numbers) == 1, f"the fixture is wrong: {line!r} is on lines {numbers}"
    return numbers[0]


def lines_of(text, line):
    return [n for n, found in enumerate(text.split("\n"), start=1) if found == line]


# --------------------------------------------------------------------------
# A temporary project with a history
# --------------------------------------------------------------------------

def path_map(**entries):
    """A path map valid under the kernel's schema (its required systems read from the schema), with ``entries``
    as further top-level keys."""
    schema = json.loads(PATH_MAP_SCHEMA.read_text(encoding="utf-8"))
    document = {
        "state_class": "AUTHORITATIVE",
        "namespaces": {"all": {
            "paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
            "permitted_roles": ["engineer"], "retention": "permanent", "export_policy": "allowed",
            "embedding_policy": "not embedded", "provenance": "fixture", "deletion_rebuild": "from git"}},
        "capabilities": {"code_intelligence": {"enabled": False}, "research_corpus": {"enabled": False}},
        "policies": dict(POLICIES),
        "systems": {name: {"status": "absent", "reason": "a fixture"}
                    for name in schema["properties"]["systems"]["required"]},
    }
    document.update(entries)
    return yaml.safe_dump(document, sort_keys=False)


class Project:
    """A temporary git repository whose commits a case makes one by one."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.minute = 0
        self.git("init", "-q", "-b", "main")

    def git(self, *args, who=AGENT):
        self.minute += 1
        hour, minute = divmod(self.minute, 60)
        date = DATE.format(hour=1 + hour, minute=minute)
        environment = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.root.parent), "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": who["name"], "GIT_AUTHOR_EMAIL": who["email"],
            "GIT_COMMITTER_NAME": who["name"], "GIT_COMMITTER_EMAIL": who["email"],
            "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
        }
        done = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, env=environment)
        assert done.returncode == 0, f"git {' '.join(args)} failed:\n{done.stderr}"
        return done.stdout

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def commit(self, subject, who=AGENT):
        self.git("add", "-A", who=who)
        arguments = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", subject]
        for trailer in who["trailers"]:
            arguments += ["--trailer", trailer]
        self.git(*arguments, who=who)
        return self.git("rev-parse", "HEAD").strip()


def project_with_register(root, register_text, files=None, named=True):
    """A project whose path map names ``REGISTER_REL`` (when ``named``) holding ``register_text``, with ``files``
    beside it, all in one first commit by the owner that cites nothing."""
    project = Project(root)
    project.write("README.md", "# A project\n\nNo frontmatter here.\n")
    project.write(PATH_MAP_REL, path_map(**({REGISTER_KEY: REGISTER_REL} if named else {})))
    if register_text is not None:
        project.write(REGISTER_REL, register_text)
    for rel, text in (files or {}).items():
        project.write(rel, text)
    project.commit("Start the project and its records", who=OWNER)
    return project


# --------------------------------------------------------------------------
# Record files
# --------------------------------------------------------------------------

def frontmatter_file(lines, body="Body text."):
    return "---\n" + "\n".join(lines) + f"\n---\n\n# A record\n\n{body}\n"


def decision_file(record_id, status="ACTIVE", **keys):
    """A schema-valid MADR decision file (madr.schema.json): id, type, status, state_class, title."""
    lines = [f"id: {record_id}", "type: decision", f"status: {status}", "state_class: AUTHORITATIVE",
             f"title: A decision {record_id}"]
    lines += [f"{key}: {json.dumps(value)}" for key, value in keys.items()]
    return frontmatter_file(lines)


# --------------------------------------------------------------------------
# The decision-citations check, as gov check runs it
# --------------------------------------------------------------------------

def citations_command():
    declaration = yaml.safe_load(CITATIONS_DECLARATION.read_text(encoding="utf-8"))
    assert isinstance(declaration, dict) and declaration.get("id") == "core-decision-citations", \
        f"the kernel's declaration of the decision-citations check is not where it was: {CITATIONS_DECLARATION}"
    return declaration["command"]


class Answer:
    def __init__(self, done):
        self.returncode, self.stdout, self.stderr = done.returncode, done.stdout, done.stderr

    def describe(self):
        return f"exit {self.returncode}\nstdout: {self.stdout[:3000]}\nstderr: {self.stderr[:3000]}"

    @property
    def data(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"the check's output is not one JSON object\n{self.describe()}") from None
        assert isinstance(data, dict), f"the check's output is not a JSON object\n{self.describe()}"
        return data

    @property
    def flagged(self):
        return sorted((f.get("commit"), f.get("decision")) for f in self.data.get("findings") or []
                      if isinstance(f, dict) and f.get("code") == UNRECORDED)


def run_citations(root):
    """The declared command, by ``sh -c``, in the project's root, with this worktree's code."""
    done = subprocess.run(citations_command(), shell=True, cwd=str(root), env=env(Path(root).parent),
                          capture_output=True, text=True, timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
    return Answer(done)


def assert_flagged(answer, expected):
    expected = sorted(expected)
    assert answer.flagged == expected, (
        f"the {UNRECORDED} findings are not the expected ones\n"
        f"expected (commit, decision): {expected}\nfound:                       {answer.flagged}\n"
        f"{answer.describe()}")
