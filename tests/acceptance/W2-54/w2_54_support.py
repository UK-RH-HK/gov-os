"""Support code for the W2-54 acceptance tests (DAEO-0rfi; standard library and PyYAML only).

W2-54 (DEC-768): two computations of a ticket's context give one packet and one hash, whatever order the
retrieval returns its items in; the context-reproducibility check declares a time limit that fits its run; and
core-schema knows the ``audit-report`` type exactly as W2-02 defines it at ``2a35fd7b``.

How the tests run (README, "How the suite runs this worktree's code"):

- **Through public interfaces only:** ``gov context --json`` (and ``--budget``), the context-reproducibility
  check run as its declaration says (``python3 -m gov.context.context_check`` in the project root), ``gov check
  --json``, and core-schema (``python3 -m gov.check.schema`` in the project root).
- **Every process runs this worktree's ``src/``** (DEC-732): ``PYTHONPATH`` names it, per process, and the
  session first asserts that ``gov.__file__`` points into it.
- **The order the retrieval returns its items in** is set through the retrieval's public entry,
  ``gov.retrieval.retrieve.retrieve``: a ``sitecustomize`` in a temporary folder, first on ``PYTHONPATH``,
  wraps it in every process of a run; the wrapper calls the real entry and returns the same items in another
  order (or, for the failure line, other items). Each call is logged, so a test also proves the entry was reached.
- **Every project is a temporary git repository built from scratch:** single named files of this worktree only
  (the path map, the template's gitleaks rules, two schema files), never a folder, never a clone.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"

# ---- the commits this suite reads with `git show` (never checked out)
BASE_COMMIT = "b644d28a"      # this ticket's claim commit: the tree before its implementation
W2_02_COMMIT = "2a35fd7b"     # W2-02's held branch: the audit-report type as W2-02 defines it (DEC-768 item 1)

# ---- the files of this worktree the suite reads
CHECKS_REL = "template/governance/kernel/checks"
INSTALLED_CHECKS_REL = "governance/kernel/checks"
CONTEXT_DECLARATION_REL = f"{CHECKS_REL}/context-reproducibility.yaml"
SCHEMAS_REL = "template/governance/kernel/schemas"
AUDIT_SCHEMA_REL = f"{SCHEMAS_REL}/audit-report.schema.json"
COMMON_SCHEMA_REL = f"{SCHEMAS_REL}/common.schema.json"
W2_02_OTHER_SCHEMAS = ("close.schema.json", "adoption-verdict.schema.json")
CHANGE_RECORD_REL = "docs/changes/W2-54-CIT-E.md"
W1_43_REL = "docs/audit/wave-1/W1-43-wave-1-exit-audit.md"
W1_43_SHA256 = "b14e17d6e71b2727c3cea123dec112fdccbeb27afc1f50b67f5e27294ecdac1d"
PATH_MAP_REL = "governance/project/path-map.yaml"
GITLEAKS_TEMPLATE_REL = "template/.gitleaks.toml"

# ---- the declaration's time limit (README, "The bound on the time limit")
TIMEOUT_FIELD = "timeout-seconds"
RUNNER_DEFAULT_S = 60          # what a check without a declared limit gets (DEC-595)
LIMIT_BOUND_S = 600            # the highest limit this suite accepts: the sibling retrieval-regression check's
CONTEXT_CHECK_ID = "context-reproducibility"
CORE_SCHEMA_ID = "core-schema"
GREEN, RED = "GREEN", "RED"

# ---- the packet (W1-24's form) and core-schema's codes, as they are produced today
K_DROPPED, K_HASH, K_SUPPLEMENTARY = "dropped", "hash", "supplementary"
MISSING_FIELD = "SCHEMA_MISSING_FIELD"
INVALID_FIELD = "SCHEMA_INVALID_FIELD"
INVALID_TYPE = "SCHEMA_INVALID_TYPE"
AUDIT_FIELDS = ("milestone", "commit", "pack_sha256")

CALL_TIMEOUT_S = 120.0
CHECK_TIMEOUT_S = 900.0        # a pytest guard only: the check's own limit is what is under test
GOV_CHECK_TIMEOUT_S = 1800.0


# --------------------------------------------------------------------------
# The environment of every process: this worktree's src/, a scratch HOME, no network
# --------------------------------------------------------------------------

class Box:
    """A scratch place: HOME, TMPDIR, a PATH of wrappers (python3, git, gitleaks), and the retrieval stand-in."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "bin", "hook", "log"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        for tool, found in (("python3", sys.executable), ("git", shutil.which("git")),
                            ("gitleaks", shutil.which("gitleaks"))):
            if found:
                wrapper = self.workdir / "bin" / tool
                wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
                wrapper.chmod(0o755)
        (self.workdir / "hook" / "sitecustomize.py").write_text(_HOOK, encoding="utf-8")

    @property
    def log(self):
        return self.workdir / "log"

    def env(self, mode=None, **extra):
        """The environment of a child process; with ``mode``, the retrieval stand-in is on (README)."""
        paths = ([str(self.workdir / "hook")] if mode else []) + [str(SRC)]
        env = {
            "PATH": f"{self.workdir / 'bin'}:/usr/bin:/bin",
            "HOME": str(self.workdir / "home"),
            "TMPDIR": str(self.workdir / "tmp"),
            "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": os.pathsep.join(paths),
            "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            **extra,
        }
        if mode:
            env.update({"W254_MODE": mode, "W254_LOG": str(self.log)})
        return env

    def reset_log(self):
        shutil.rmtree(self.log, ignore_errors=True)
        self.log.mkdir()

    def calls(self):
        """The retrieval calls the stand-in saw since the last reset, in the order they were logged."""
        path = self.log / "calls.jsonl"
        if not path.is_file():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def has_gitleaks(self):
        return (self.workdir / "bin" / "gitleaks").exists()


# The retrieval stand-in. It wraps the public entry in every process started with W254_MODE set, calls the real
# entry, and returns the same bundle with its item lists in the order the mode names (or, for the failure line,
# with one item fewer on every second call of the same question). Every call is numbered per question, so two
# computations of one ticket see two different orders wherever they run, and each call is logged.
_HOOK = r'''
"""W2-54's stand-in for the order in which the retrieval returns its items (acceptance tests only)."""
import hashlib
import json
import os
import random

_MODE, _LOG = os.environ.get("W254_MODE"), os.environ.get("W254_LOG")

if _MODE and _LOG:
    import gov.retrieval.retrieve as _entry

    _real = _entry.retrieve

    def _number(key):
        index = 0
        while True:
            try:
                os.close(os.open(os.path.join(_LOG, f"{key}-{index}"), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                return index
            except FileExistsError:
                index += 1

    def _order(items, mode, number):
        items = list(items)
        if mode == "identity":
            return items
        if mode == "reverse":
            return items[::-1]
        if mode == "rotate":
            return items[1:] + items[:1]
        if mode == "shuffle":
            random.Random(54).shuffle(items)
            return items
        if mode == "alternate":
            return items if number % 2 == 0 else items[::-1]
        if mode == "drop-alternate":
            return items if number % 2 == 0 else items[:-1]
        if mode == "empty":
            return []
        raise RuntimeError(f"W254_MODE {mode!r} is no mode of the stand-in")

    def retrieve(*args, **kwargs):
        bundle = _real(*args, **kwargs)
        key = hashlib.sha256(repr((args[1:], sorted((k, repr(v)) for k, v in kwargs.items()))).encode()).hexdigest()
        number = _number(key[:20])
        # W254_TARGET: only the calls for that ticket get the mode; every other call is returned as it came
        target = os.environ.get("W254_TARGET")
        mode = _MODE if not target or kwargs.get("ticket") == target else "identity"
        evidence = list(bundle.get("evidence") or [])
        out = dict(bundle)
        out["evidence"] = _order(evidence, mode, number)
        # the item lists beside the evidence keep their items and change their order alike (never their content)
        reorder = "identity" if mode in ("drop-alternate", "empty") else mode
        if isinstance(bundle.get("gaps"), list):
            out["gaps"] = _order(bundle["gaps"], reorder, number)
        if isinstance(bundle.get("expansions"), list):
            out["expansions"] = _order(bundle["expansions"], reorder, number)
        if isinstance(bundle.get("merge"), dict) and isinstance(bundle["merge"].get("dropped"), list):
            out["merge"] = {**bundle["merge"], "dropped": _order(bundle["merge"]["dropped"], reorder, number)}
        line = {"pid": os.getpid(), "key": key[:20], "number": number, "mode": mode,
                "ticket": kwargs.get("ticket"),
                "in": [[item.get("id"), item.get("chunk_id")] for item in evidence],
                "out": [[item.get("id"), item.get("chunk_id")] for item in out["evidence"]]}
        with open(os.path.join(_LOG, "calls.jsonl"), "a", encoding="utf-8") as handle:
            handle.write(json.dumps(line) + "\n")
        return out

    _entry.retrieve = retrieve
'''


class Run:
    def __init__(self, argv, done, seconds):
        self.argv, self.returncode, self.stdout, self.stderr = argv, done.returncode, done.stdout, done.stderr
        self.seconds = seconds

    def describe(self, tail=4000):
        return (f"{' '.join(map(str, self.argv))}\nexit code: {self.returncode} ({self.seconds:.1f} s)\n"
                f"stdout:\n{self.stdout[-tail:]}\nstderr:\n{self.stderr[-tail:]}")

    def envelope(self):
        try:
            envelope = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"standard output is not one JSON envelope\n{self.describe()}") from None
        assert isinstance(envelope, dict) and "ok" in envelope, self.describe()
        return envelope


def run(argv, *, cwd, env, timeout):
    started = time.monotonic()
    try:
        done = subprocess.run([str(part) for part in argv], cwd=str(cwd), env=env, capture_output=True, text=True,
                              timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{' '.join(map(str, argv))} did not end within {timeout:.0f} s") from None
    return Run(argv, done, time.monotonic() - started)


_GOV = "import sys\nimport gov.cli.main as _m\nsys.argv[0] = 'gov'\nsys.exit(_m.main())\n"


def gov(box, *args, cwd=None, env=None, timeout=CALL_TIMEOUT_S):
    """``gov <args>`` in a new process, running this worktree's ``src/``."""
    return run([sys.executable, "-c", _GOV, *args], cwd=cwd or box.workdir / "elsewhere",
               env=env or box.env(), timeout=timeout)


def gov_file(env):
    """Where ``gov`` is imported from under ``env`` (DEC-732)."""
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], env=env, capture_output=True,
                          text=True, cwd="/", timeout=60)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


# --------------------------------------------------------------------------
# git and files
# --------------------------------------------------------------------------

BASE_DATE = "2026-10-18T12:00:00+00:00"


def git(project, *args):
    env = {"PATH": "/usr/bin:/bin", "HOME": str(project), "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "W2-54 tests", "GIT_AUTHOR_EMAIL": "w2-54@example.invalid",
           "GIT_COMMITTER_NAME": "W2-54 tests", "GIT_COMMITTER_EMAIL": "w2-54@example.invalid",
           "GIT_AUTHOR_DATE": BASE_DATE, "GIT_COMMITTER_DATE": BASE_DATE}
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def show(commit, rel):
    """The bytes of ``rel`` at ``commit`` of this repository (``git show``; nothing is checked out)."""
    done = subprocess.run(["git", "-C", str(REPO_ROOT), "show", f"{commit}:{rel}"], capture_output=True)
    assert done.returncode == 0, f"git show {commit}:{rel} failed:\n{done.stderr.decode(errors='replace')}"
    return done.stdout


def listed(commit, rel_dir):
    """The file names under ``rel_dir`` at ``commit`` (``git ls-tree``)."""
    done = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-tree", "--name-only", f"{commit}:{rel_dir}"],
                          capture_output=True, text=True)
    return sorted(done.stdout.split()) if done.returncode == 0 else []


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frontmatter(front, body="\n# A record\n"):
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n" + body


def new_repo(project):
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    write(project, ".gitignore", ".gov-runtime/\n")
    return project


def commit_all(project, message="the fixture"):
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message)


# --------------------------------------------------------------------------
# A project for the context packet
# --------------------------------------------------------------------------

_NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history", "export_policy": "allowed",
    "provenance": "written by the W2-54 tests", "deletion_rebuild": "authoritative; restored from git only",
}
NAMESPACES = {"top": ["*"], "docs": ["docs/**"], "tickets": [".tickets/**"]}


def adopt(project):
    """The project's path map: this worktree's, with the project's own namespaces and nothing it does not hold."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    keep = {key: document[key] for key in ("state_class", "capabilities", "policies", "systems") if key in document}
    keep["namespaces"] = {name: {"paths": patterns, "memory_class": "governance", **_NAMESPACE_FIELDS,
                                 "embedding_policy": "not embedded"} for name, patterns in NAMESPACES.items()}
    write(project, PATH_MAP_REL, yaml.safe_dump(keep, sort_keys=False))
    shutil.copy2(REPO_ROOT / GITLEAKS_TEMPLATE_REL, Path(project) / ".gitleaks.toml")


def record(record_id, kind, status, body, **more):
    front = {"id": record_id, "type": kind, "status": status, "state_class": "AUTHORITATIVE", **more}
    return frontmatter(front, f"\n# {record_id}\n\n{body}\n")


def ticket(ticket_id, title, sources):
    front = {"id": ticket_id, "type": "ticket", "status": "in_progress", "state_class": "AUTHORITATIVE",
             "title": title, "role": "engineer", "allowed_paths": ["src/placeholder/**"],
             "kpis": {"success": [title], "failure": [title]}, "sources": list(sources)}
    return frontmatter(front, f"\n# {ticket_id} {title}\n\n{title}.\n")


# The words every record shares with the tickets' titles, so the lexical route returns many items for each.
WORDS = ("context packet dropped order stable hash budget ceiling retrieval supplementary tie break "
         "reproducibility ticket computation")
TITLE = "context packet dropped order stable hash budget"

CHARTER_ID = "CHARTER-W254"
BIG_CHARTER_ID = "CHARTER-W254-BIG"
ADR_IDS = tuple(f"ADR-W254-{letter}" for letter in "ABCDEF")
SPLIT_ID = "ADR-W254-SPLIT"      # one record in many sections: several items with the same id
TK_SMALL = "TK-W254-SMALL"       # small mandatory inputs: its supplementary part fits unless the budget is small
TK_BIG = "TK-W254-BIG"           # a mandatory input past the default ceiling: every supplementary item is dropped


def _section(index):
    return (f"## Section {index}: the {WORDS.split()[index % len(WORDS.split())]} rule\n\n"
            f"Section {index} states how the {WORDS} are kept. " * 3 + "\n")


def corpus(tickets=(TK_SMALL, TK_BIG)):
    big = " ".join(f"Clause {n}: every agent sees one {WORDS}." for n in range(900))   # about 25,000 tokens
    files = {
        "README.md": f"# A project\n\nA fixture project for the W2-54 acceptance tests: {WORDS}.\n",
        "docs/charter/charter.md": record(CHARTER_ID, "charter", "ACTIVE", f"The {WORDS} of the project."),
        "docs/charter/big.md": record(BIG_CHARTER_ID, "charter", "ACTIVE", big),
        "docs/adr/split.md": record(SPLIT_ID, "decision", "ACTIVE", "\n".join(_section(i) for i in range(12))),
    }
    for index, adr in enumerate(ADR_IDS):
        files[f"docs/adr/{adr.lower()}.md"] = record(adr, "decision", "ACTIVE",
                                                      f"Decision {index}: the {WORDS}.\n\n{_section(index)}")
    for index in range(8):
        files[f"docs/notes/note-{index}.md"] = f"# Note {index}\n\n{_section(index)}\nThe {WORDS}.\n"
    sources = {TK_SMALL: [CHARTER_ID], TK_BIG: [BIG_CHARTER_ID]}
    for ticket_id in tickets:
        files[f".tickets/{ticket_id}.md"] = ticket(ticket_id, TITLE, sources[ticket_id])
    return files


def context_project(box, project, tickets=(TK_SMALL, TK_BIG), index=True):
    """A temporary project with its record store and (unless ``index`` is false) its lexical index."""
    project = new_repo(project)
    adopt(project)
    for rel, text in corpus(tickets).items():
        write(project, rel, text)
    commit_all(project)
    steps = ([("gov.retrieval.lexical", "refresh")] if index else []) + [("gov.store", "load")]
    script = "import importlib, sys\nfrom pathlib import Path\n" + "".join(
        f"importlib.import_module({module!r}).{function}(Path(sys.argv[1]))\n" for module, function in steps)
    done = run([sys.executable, "-c", script, project], cwd=box.workdir / "elsewhere", env=box.env(),
               timeout=CALL_TIMEOUT_S)
    assert done.returncode == 0, f"the fixture's store could not be built\n{done.describe()}"
    return project


def packet(box, project, ticket_id, mode, *extra):
    """``gov context --json`` for ``ticket_id`` with the retrieval stand-in in ``mode``; the packet."""
    done = gov(box, "context", "--json", "--root", project, *extra, ticket_id, env=box.env(mode))
    assert done.returncode == 0, f"gov context did not succeed\n{done.describe()}"
    envelope = done.envelope()
    assert envelope.get("ok") is True and isinstance(envelope.get("result"), dict), done.describe()
    return envelope["result"]


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def multiset(entries):
    return sorted(canonical(entry) for entry in entries)


def context_check(box, project, mode, target=None):
    """The context-reproducibility check, as its declaration says: its command, by ``sh -c``, in the project."""
    declaration = yaml.safe_load((REPO_ROOT / CONTEXT_DECLARATION_REL).read_text(encoding="utf-8"))
    env = box.env(mode, **({"W254_TARGET": target} if target else {}))
    return run(["sh", "-c", declaration["command"]], cwd=project, env=env, timeout=CHECK_TIMEOUT_S)


# --------------------------------------------------------------------------
# core-schema
# --------------------------------------------------------------------------

def schema_project(project, files, require_audit=True):
    """A temporary project with this worktree's common and audit-report schema files and ``files``. A case
    about another type runs without the audit-report file when this worktree has none (``require_audit``)."""
    project = new_repo(project)
    destination = Path(project) / SCHEMAS_REL
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / COMMON_SCHEMA_REL, destination / "common.schema.json")
    audit = REPO_ROOT / AUDIT_SCHEMA_REL
    assert audit.is_file() or not require_audit, f"there is no {AUDIT_SCHEMA_REL} in this worktree"
    if audit.is_file():
        shutil.copy2(audit, destination / "audit-report.schema.json")
    for rel, text in files.items():
        write(project, rel, text)
    commit_all(project)
    return project


def core_schema(box, project):
    """Core-schema as its declaration says, in ``project``: its exit code and its findings."""
    declaration = yaml.safe_load((REPO_ROOT / CHECKS_REL / "core-schema.yaml").read_text(encoding="utf-8"))
    done = run(["sh", "-c", declaration["command"]], cwd=project, env=box.env(), timeout=CALL_TIMEOUT_S)
    try:
        findings = json.loads(done.stdout) if done.stdout.strip() else []
    except ValueError:
        raise AssertionError(f"core-schema did not print its findings as JSON\n{done.describe()}") from None
    assert isinstance(findings, list), done.describe()
    return done, findings


def of_path(findings, rel):
    return [finding for finding in findings if finding.get("path") == rel]


def audit_front(**overrides):
    front = {"milestone": "wave-9-exit", "commit": "0123456789abcdef0123456789abcdef01234567",
             "pack_sha256": "2355ce5f42d2a8d087535fa0dd3bbcc012a0ec43ec0d08f1f712b6dde8e48c23"}
    front.update(overrides)
    return {key: value for key, value in front.items() if value is not None}


AUDIT_BODY = ("\n# An audit\n\n| item | class | evidence |\n|---|---|---|\n| CAP-01 | OK | README.md |\n")


def audit_record(**overrides):
    return frontmatter(audit_front(**overrides), AUDIT_BODY)


# --------------------------------------------------------------------------
# Declarations and gov check
# --------------------------------------------------------------------------

def limit_of(text):
    document = yaml.safe_load(text)
    return document.get(TIMEOUT_FIELD) if isinstance(document, dict) else None


def checks_of(envelope):
    """Each check's entry in a ``gov check --json`` envelope, by id (a passing run's result, a failing run's
    error details)."""
    where = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
    checks = (where or {}).get("checks") if isinstance(where, dict) else None
    assert isinstance(checks, list), f"the envelope lists no checks:\n{canonical(envelope)[:3000]}"
    return {check.get("id"): check for check in checks}


def worktree_env():
    """The environment of a process run in this worktree: the session's own, with this worktree's ``src/``."""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    return env
