"""Support code for the W1-24 acceptance tests (standard library and PyYAML only).

W1-24 builds ``gov context``: compiled, budgeted, hashed context packets with
mandatory inputs resolved by id and sha256, an authority block ordered by
precedence, a ceiling, and a context-reproducibility family check. The tests
use only public interfaces:

- The function of ``gov.context`` (package DP-1), called in a child process;
- the command ``gov context`` (``python -m gov.cli.main context``), read
  through its ``--json`` envelope;
- ``gov.store`` to build what a context reads, and ``gov check --list`` for the
  family check.

How the tests call it:

- **Every call runs in a new Python process** with this worktree's ``src/`` on
  ``PYTHONPATH`` and a working directory that is never the project under test.
- **Nothing is built in this worktree** (DEC-322). Every project is a temporary
  git repository with its own store and its own ``.gov-runtime/``.
- **The scratch environment** is built from nothing: an empty ``HOME``, a
  ``PATH`` that holds ``git`` only, and locale. No model runs.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"

# ---- the public interface (package DP-1)
CONTEXT = "gov.context"
FUNCTION = "context"
COMMAND_REL = "src/gov/context/command.py"
STORE = "gov.store"
CHECKS_REL = "template/governance/kernel/checks"
CHECK_GLOB = "context-reproducibility*"
FAMILY = "context-reproducibility"
CHECK_FIELDS = ("id", "family", "tier", "severity", "command")
PYPROJECT_REL = "pyproject.toml"
RUNTIME_REL = ".gov-runtime"
SCRATCH_REL = ".gov-runtime/scratch"
PATH_MAP_REL = "governance/project/path-map.yaml"
CONFIG_REL = ".gitleaks.toml"
TEMPLATE_CONFIG_REL = "template/.gitleaks.toml"
CALL_TIMEOUT_S = 30.0

# ---- token counting (DEC-083: no tokenizer; the rule from gov.retrieval.retrieve._tokens)
TOKEN_CHARS = 4
DEFAULT_BUDGET = 6000
BRIEF_LIMIT = 2500

# ---- precedence tiers (CAP-01.a: Charter > Contract > ADRs > specifications > tasks > retrieval > inference)
PRECEDENCE = ("charter", "contract", "decision", "specification", "ticket")
PRECEDENCE_RANK = {kind: i for i, kind in enumerate(PRECEDENCE)}

# ---- packet keys (package DP-1: the tests hold these names only)
K_TICKET = "ticket"
K_AUTHORITY = "authority"
K_MANDATORY = "mandatory"
K_SUPPLEMENTARY = "supplementary"
K_DROPPED = "dropped"
K_HASH = "hash"
K_TOKENS = "tokens"
K_BUDGET = "budget"
M_ID = "id"
M_SHA = "sha256"
M_AUTHORITY = "authority"
M_LIFECYCLE = "lifecycle"
M_CONSTRAINT = "constraint"
M_REASON = "reason"
B_LIMIT = "limit"
B_USED = "used"

# ---- error codes
BLOCKED = "BLOCKED"
CONTRADICTION = "CONTRADICTION"


class Missing(AssertionError):
    """Something the ticket builds does not exist yet."""


def tokens(text):
    """Token count: ceil(len(text) / 4) (DEC-083, the same rule as gov.retrieval.retrieve._tokens)."""
    return -(-len(text) // TOKEN_CHARS)


# --------------------------------------------------------------------------
# The driver: one child process per batch of calls
# --------------------------------------------------------------------------

_DRIVER = r'''
import importlib, json, sys
from pathlib import Path

request = json.loads(sys.stdin.read())

def decode(value):
    if isinstance(value, dict) and set(value) == {"$path"}:
        return Path(value["$path"])
    return value

out = {"calls": []}
for call in request["calls"]:
    try:
        function = getattr(importlib.import_module(call["module"]), call["function"])
    except ModuleNotFoundError as exc:
        if exc.name is None or not (call["module"] == exc.name or call["module"].startswith(exc.name + ".")):
            raise
        print(f"No module named {exc.name!r}", file=sys.stderr)
        sys.exit(3)
    except AttributeError:
        print(f"{call['module']} has no function {call['function']}", file=sys.stderr)
        sys.exit(3)
    record = {"value": None, "error": None}
    try:
        record["value"] = function(*[decode(arg) for arg in call["args"]],
                                   **{key: decode(value) for key, value in call["kwargs"].items()})
    except Exception as exc:
        record["error"] = {"type": type(exc).__name__, "message": str(exc), "code": getattr(exc, "code", None)}
    out["calls"].append(record)
print("\n" + json.dumps(out, default=repr))
'''

MISSING_EXIT = 3


def path_arg(path):
    return {"$path": str(path)}


class Outcome:
    def __init__(self, data, stderr):
        self.calls, self.stderr = data["calls"], stderr

    def error(self, index=0):
        return self.calls[index]["error"]

    def value(self, index=0):
        call = self.calls[index]
        assert call["error"] is None, \
            f"call {index} raised {call['error']['type']}: {call['error']['message']}\n{self.stderr[-2000:]}"
        return call["value"]


class Api:
    """Calls this worktree's modules and its ``gov`` command line, each in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "bin"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        for tool in ("git", "python3"):
            found = sys.executable if tool == "python3" else shutil.which(tool)
            if found:
                wrapper = self.workdir / "bin" / tool
                wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
                wrapper.chmod(0o755)
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")

    def scratch_env(self, **extra):
        return {
            "PATH": str(self.workdir / "bin"),
            "HOME": str(self.workdir / "home"),
            "TMPDIR": str(self.workdir / "tmp"),
            "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": str(SRC),
            "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
            **extra,
        }

    def run(self, calls, *, env=None, timeout=CALL_TIMEOUT_S):
        request = {"calls": [{"module": module, "function": function, "args": list(args), "kwargs": dict(kwargs)}
                             for module, function, args, kwargs in calls]}
        what = ", ".join(dict.fromkeys(f"{module}.{function}" for module, function, *_ in calls))
        try:
            done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request),
                                  env=self.scratch_env() if env is None else env,
                                  cwd=str(self.workdir / "elsewhere"), capture_output=True, text=True,
                                  timeout=timeout)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {timeout:.0f} s") from None
        if done.returncode == MISSING_EXIT:
            raise Missing(f"{CONTEXT}.{FUNCTION} does not exist: {done.stderr.strip()}")
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr[-4000:]}"
        try:
            data = json.loads(done.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            raise AssertionError(f"{what} did not return JSON:\n{done.stdout}\n{done.stderr}") from None
        return Outcome(data, done.stderr)

    def call(self, module, function, *args, env=None, **kwargs):
        return self.run([(module, function, args, kwargs)], env=env).value()

    def exists(self):
        done = subprocess.run([sys.executable, "-c", f"from {CONTEXT} import {FUNCTION}"], capture_output=True,
                              text=True, cwd=str(self.workdir / "elsewhere"), env=self.scratch_env())
        if done.returncode != 0:
            last = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else "import failed"
            raise Missing(f"{CONTEXT}.{FUNCTION} does not exist: {last}")

    def build_store(self, root, env=None):
        env = env or self.scratch_env()
        return self.run([(STORE, "load", [path_arg(root)], {})], env=env).value()

    def context(self, root, ticket, **kwargs):
        return self.run([(CONTEXT, FUNCTION, [path_arg(root), ticket], kwargs)]).value()

    def context_outcome(self, root, ticket, **kwargs):
        return self.run([(CONTEXT, FUNCTION, [path_arg(root), ticket], kwargs)])

    def command_exists(self):
        if not (REPO_ROOT / COMMAND_REL).is_file():
            raise Missing(f"gov context is not built: there is no {COMMAND_REL} (DEC-317)")

    def gov(self, *args, env=None, cwd=None):
        scripts = tomllib.loads((REPO_ROOT / PYPROJECT_REL).read_text(encoding="utf-8"))["project"]["scripts"]
        module, _, attribute = scripts["gov"].partition(":")
        launcher = (f"import sys\nimport {module} as _m\nsys.argv[0] = 'gov'\n"
                    f"sys.exit(getattr(_m, {attribute!r})())\n")
        done = subprocess.run([sys.executable, "-c", launcher, *args], capture_output=True, text=True,
                              cwd=str(cwd or self.workdir / "elsewhere"), env=env or self.scratch_env(),
                              timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
        return Run(("gov", *args), done)

    def command(self, root, *args, **kwargs):
        return self.gov("context", "--json", "--root", str(root), *args, **kwargs)


class Run:
    def __init__(self, argv, done):
        self.argv, self.returncode, self.stdout, self.stderr = argv, done.returncode, done.stdout, done.stderr

    def describe(self):
        return f"{' '.join(self.argv)}\nexit code: {self.returncode}\nstdout:\n{self.stdout}\nstderr:\n{self.stderr}"

    def envelope(self):
        try:
            envelope = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"standard output is not one JSON envelope\n{self.describe()}") from None
        assert envelope.get("command") is not None, self.describe()
        return envelope

    def packet(self):
        assert self.returncode == 0, f"gov context did not succeed\n{self.describe()}"
        envelope = self.envelope()
        assert envelope.get("ok") is True and isinstance(envelope.get("result"), dict), self.describe()
        return envelope["result"]


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------

BASE_DATE = "2026-09-01T12:00:00+00:00"


def git(project, *args, date=BASE_DATE):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(project), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "W1-24 tests", "GIT_AUTHOR_EMAIL": "w1-24@example.invalid",
           "GIT_COMMITTER_NAME": "W1-24 tests", "GIT_COMMITTER_EMAIL": "w1-24@example.invalid",
           "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel


def commit(project, message="a change", date=BASE_DATE):
    git(project, "add", "-A", date=date)
    git(project, "commit", "-q", "--allow-empty", "-m", message, date=date)


def clone(source, destination):
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(source), str(destination)], check=True,
                   capture_output=True)
    return Path(destination)


def head_sha(project):
    return git(project, "rev-parse", "HEAD").strip()


# --------------------------------------------------------------------------
# Records
# --------------------------------------------------------------------------

def record(record_id, kind, status, body, **more):
    front = {"id": record_id, "type": kind, "status": status, "state_class": "AUTHORITATIVE", **more}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# " + record_id + "\n\n" + body + "\n"


def ticket_file(ticket_id, status="in_progress", sources=None, depends_on=None, **more):
    front = {"id": ticket_id, "type": "ticket", "status": status, "state_class": "AUTHORITATIVE",
             "role": "engineer", "allowed_paths": ["src/placeholder/**"],
             "kpis": {"success": ["placeholder"], "failure": ["placeholder"]}}
    if sources is not None:
        front["sources"] = list(sources)
    if depends_on is not None:
        front["depends_on"] = list(depends_on)
    front.update(more)
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# " + ticket_id + "\n"


# --------------------------------------------------------------------------
# The path map (adopted from the real repository)
# --------------------------------------------------------------------------

_NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history", "export_policy": "allowed",
    "provenance": "written by the W1-24 tests", "deletion_rebuild": "authoritative; restored from git only",
}

NAMESPACES = {
    "top": (["*"], "not embedded"),
    "docs": (["docs/**"], "not embedded"),
    "records": (["records/**"], "not embedded"),
    "tickets": ([".tickets/**"], "not embedded"),
    "overlay": (["governance/**"], "not embedded"),
}


def adopt(project, namespaces=NAMESPACES):
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document["namespaces"] = {name: {"paths": list(patterns), "memory_class": "governance", **_NAMESPACE_FIELDS,
                                     "embedding_policy": policy} for name, (patterns, policy) in namespaces.items()}
    write(project, PATH_MAP_REL, yaml.safe_dump(document, sort_keys=False))
    if (REPO_ROOT / TEMPLATE_CONFIG_REL).is_file():
        shutil.copy2(REPO_ROOT / TEMPLATE_CONFIG_REL, Path(project) / CONFIG_REL)


# --------------------------------------------------------------------------
# The fixture corpus
# --------------------------------------------------------------------------

# The records at each precedence level
CHARTER_ID = "CHARTER-W24"
CONTRACT_ID = "CONTRACT-W24"
ADR_A = "ADR-W24-A"
ADR_B = "ADR-W24-B"
ADR_SUPERSEDED = "ADR-W24-OLD"
ADR_CONFLICT_1 = "ADR-W24-C1"
ADR_CONFLICT_2 = "ADR-W24-C2"
SPEC_A = "SPEC-W24-A"

TK_NORMAL = "TK-W24-NORMAL"
TK_BRIEF = "TK-W24-BRIEF"
TK_PRESSURE = "TK-W24-PRESS"
TK_BLOCKED = "TK-W24-BLOCKED"
TK_SUPERSEDED = "TK-W24-STALE"
TK_CONFLICT = "TK-W24-CONFLICT"
TK_PRECEDENCE = "TK-W24-PREC"
GONE_ID = "GONE-W24-404"

CHARTER_TEXT = "Every agent sees a compiled context packet with mandatory inputs."
CONTRACT_TEXT = "The context packet stays under the configured ceiling of approximately six thousand tokens."
ADR_A_TEXT = "A token is four characters of the text, rounded up."
ADR_B_TEXT = "Authority precedence resolves conflicts between records at different levels."
SPEC_A_TEXT = "Authority precedence resolves conflicts between records at different levels."
ADR_SUPERSEDED_TEXT = "The old token counting rule, before the four-character method."
ADR_C1_TEXT = "The maximum token pressure threshold is five hundred tokens."
ADR_C2_TEXT = "The maximum token pressure threshold is one thousand tokens."

ALL_NORMAL_SOURCES = [CHARTER_ID, CONTRACT_ID, ADR_A]


def corpus():
    """The fixture's files: records at each precedence level and tickets that declare them."""
    return {
        "README.md": "# A project\n\nA fixture project for the W1-24 acceptance tests.\n",
        ".gitignore": ".gov-runtime/\n",

        "docs/charter/charter.md": record(CHARTER_ID, "charter", "ACTIVE", CHARTER_TEXT),
        "docs/contract/contract.md": record(CONTRACT_ID, "contract", "ACTIVE", CONTRACT_TEXT),
        "docs/adr/adr-a.md": record(ADR_A, "decision", "ACTIVE", ADR_A_TEXT),
        "docs/adr/adr-b.md": record(ADR_B, "decision", "ACTIVE", ADR_B_TEXT, supersedes=[SPEC_A]),
        "docs/specs/spec-a.md": record(SPEC_A, "specification", "CLOSED", SPEC_A_TEXT),
        "docs/adr/adr-old.md": record(ADR_SUPERSEDED, "decision", "SUPERSEDED", ADR_SUPERSEDED_TEXT,
                                       superseded_by=ADR_A),
        "docs/adr/adr-c1.md": record(ADR_CONFLICT_1, "decision", "ACTIVE", ADR_C1_TEXT),
        "docs/adr/adr-c2.md": record(ADR_CONFLICT_2, "decision", "ACTIVE", ADR_C2_TEXT,
                                      supersedes=[ADR_CONFLICT_1]),

        ".tickets/" + TK_NORMAL + ".md": ticket_file(TK_NORMAL, sources=ALL_NORMAL_SOURCES),
        ".tickets/" + TK_BRIEF + ".md": ticket_file(TK_BRIEF, sources=[ADR_A]),
        ".tickets/" + TK_PRESSURE + ".md": ticket_file(TK_PRESSURE, sources=ALL_NORMAL_SOURCES),
        ".tickets/" + TK_BLOCKED + ".md": ticket_file(TK_BLOCKED, sources=[CHARTER_ID, GONE_ID]),
        ".tickets/" + TK_SUPERSEDED + ".md": ticket_file(TK_SUPERSEDED, sources=[ADR_SUPERSEDED]),
        ".tickets/" + TK_CONFLICT + ".md": ticket_file(TK_CONFLICT, sources=[ADR_CONFLICT_1, ADR_CONFLICT_2]),
        ".tickets/" + TK_PRECEDENCE + ".md": ticket_file(TK_PRECEDENCE, sources=[ADR_B, SPEC_A]),
    }


def build_fixture(project):
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    adopt(project)
    for rel, text in corpus().items():
        write(project, rel, text)
    commit(project, "the fixture", BASE_DATE)
    return project


# --------------------------------------------------------------------------
# Packet checks
# --------------------------------------------------------------------------

def check_packet(packet):
    """The form every packet has: mandatory inputs by id and sha256, authority block, hash, budget."""
    assert isinstance(packet, dict), f"the packet is not a map: {type(packet).__name__}"
    assert isinstance(packet.get(K_HASH), str) and re.fullmatch(r"[0-9a-f]{64}", packet[K_HASH]), \
        f"the packet has no sha256 hash: {packet.get(K_HASH)!r}"
    mandatory = packet.get(K_MANDATORY)
    assert isinstance(mandatory, list), f"`{K_MANDATORY}` is not a list: {type(mandatory).__name__}"
    for item in mandatory:
        check_mandatory_input(item)
    authority = packet.get(K_AUTHORITY)
    assert isinstance(authority, list), f"`{K_AUTHORITY}` is not a list: {type(authority).__name__}"
    for item in authority:
        check_mandatory_input(item)
    return packet


def check_mandatory_input(item):
    assert isinstance(item, dict), f"a mandatory input is not a map: {item!r}"
    assert isinstance(item.get(M_ID), str) and item[M_ID], f"a mandatory input has no id: {item!r}"
    assert isinstance(item.get(M_SHA), str) and re.fullmatch(r"[0-9a-f]{64}", item[M_SHA]), \
        f"a mandatory input has no sha256: {item!r}"
    assert isinstance(item.get(M_AUTHORITY), str) and item[M_AUTHORITY], \
        f"a mandatory input has no authority tier: {item!r}"
    assert isinstance(item.get(M_LIFECYCLE), str) and item[M_LIFECYCLE], \
        f"a mandatory input has no lifecycle state: {item!r}"
    assert isinstance(item.get(M_REASON), str) and item[M_REASON], \
        f"a mandatory input has no reason: {item!r}"
    return item


# --------------------------------------------------------------------------
# The family check
# --------------------------------------------------------------------------

def family_check(api):
    matches = sorted((REPO_ROOT / CHECKS_REL).glob(CHECK_GLOB))
    if not matches:
        raise Missing(f"the context-reproducibility check is not registered: "
                      f"nothing matches {CHECKS_REL}/{CHECK_GLOB}")
    scripts = tomllib.loads((REPO_ROOT / PYPROJECT_REL).read_text(encoding="utf-8"))["project"]["scripts"]
    module, _, attribute = scripts["gov"].partition(":")
    launcher = f"import sys\nimport {module} as _m\nsys.argv[0] = 'gov'\nsys.exit(getattr(_m, {attribute!r})())\n"
    done = subprocess.run([sys.executable, "-c", launcher, "check", "--list", "--json", "--root", str(REPO_ROOT)],
                          cwd=str(api.workdir / "elsewhere"), env=api.scratch_env(), capture_output=True, text=True,
                          timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
    described = f"gov check --list --json\nexit code: {done.returncode}\nstdout:\n{done.stdout}\nstderr:\n{done.stderr}"
    assert done.returncode == 0, f"gov check --list does not succeed\n{described}"
    checks = json.loads(done.stdout)["result"]["checks"]
    found = [check for check in checks
             if str(check.get("family", "")).strip().lower().replace("_", "-").replace(" ", "-") == FAMILY]
    assert len(found) == 1, f"expected one listed check of the family {FAMILY!r}, found {len(found)}\n{described}"
    return found[0]
