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
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"

# ---- the commits this suite reads with `git show` (never checked out)
BASE_COMMIT = "b644d28a"      # this ticket's claim commit: the tree before its implementation
W2_02_COMMIT = "2a35fd7b"     # W2-02's held branch: the audit-report type as W2-02 defines it (DEC-768 item 1)
# Rewrite-Reason: DEC-874. W2-02's branch with its types merged with w2/integrate: every W2-54 commit is among its
# ancestors, so "nothing of W2-02's other types" is judged on it as on HEAD (README, "Run 5 (DEC-874)").
W2_02_MERGED_COMMIT = "4ce16df2"

# ---- the files of this worktree the suite reads
CHECKS_REL = "template/governance/kernel/checks"
INSTALLED_CHECKS_REL = "governance/kernel/checks"
CONTEXT_DECLARATION_REL = f"{CHECKS_REL}/context-reproducibility.yaml"
SCHEMAS_REL = "template/governance/kernel/schemas"
AUDIT_SCHEMA_REL = f"{SCHEMAS_REL}/audit-report.schema.json"
COMMON_SCHEMA_REL = f"{SCHEMAS_REL}/common.schema.json"
W2_02_OTHER_SCHEMAS = ("close.schema.json", "adoption-verdict.schema.json")
W2_02_OTHER_TYPES = ("close", "adoption-verdict")
SCHEMA_FOLDERS = (SCHEMAS_REL, "governance/kernel/schemas")
SCHEMA_MODULE_REL = "src/gov/check/schema.py"
OWN_TASK = "DAEO-0rfi"         # the Task trailer of every commit of this ticket (W2-02's carry DAEO-zflj)
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
    """A scratch place: HOME, TMPDIR, a PATH of wrappers (python3, git, gitleaks, check-jsonschema), and the
    retrieval stand-in."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "bin", "hook", "log"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        # check-jsonschema: core-schema's validator (DEC-872 item 2, DEC-954), the one the suite's PATH finds
        for tool, found in (("python3", sys.executable), ("git", shutil.which("git")),
                            ("gitleaks", shutil.which("gitleaks")),
                            ("check-jsonschema", shutil.which("check-jsonschema"))):
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


def schema_findings(done):
    """Core-schema's findings from its output (DEC-954): a list of findings; the refusal form ``{"findings":
    [...], ...}``; or the success form ``{"ok": true, "result": {...}}``, which carries no finding."""
    try:
        output = json.loads(done.stdout) if done.stdout.strip() else []
    except ValueError:
        raise AssertionError(f"core-schema did not print its findings as JSON\n{done.describe()}") from None
    if isinstance(output, dict) and "findings" in output:
        findings = output["findings"]
    elif isinstance(output, dict) and output.get("ok") is True and isinstance(output.get("result"), dict):
        findings = output["result"].get("findings", [])
    else:
        findings = output
    assert isinstance(findings, list), done.describe()
    return findings


def core_schema(box, project):
    """Core-schema as its declaration says, in ``project``: its exit code and its findings."""
    declaration = yaml.safe_load((REPO_ROOT / CHECKS_REL / "core-schema.yaml").read_text(encoding="utf-8"))
    done = run(["sh", "-c", declaration["command"]], cwd=project, env=box.env(), timeout=CALL_TIMEOUT_S)
    return done, schema_findings(done)


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
# Run 5 (DEC-874): W2-54's own change, read through git (README, "Run 5 (DEC-874)")
# --------------------------------------------------------------------------
#
# Rewrite-Reason: DEC-874. "Nothing of W2-02's other types" is about W2-54's own change, not the tree: the commits of
# a history that are no merge and whose Task trailer is OWN_TASK, each read against its one parent. Nothing is
# checked out; ``repo`` is this repository, or a temporary one a case builds from scratch.

_MARK = "\x01"


def _git_out(repo, *args):
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {repo}:\n{done.stderr}"
    return done.stdout


def _own_log(history, *args, paths=(), repo=REPO_ROOT, task=OWN_TASK):
    """``git log --no-merges --no-renames --full-history <args> <history> -- <paths>``, split by commit:
    ``[(commit, its lines)]`` for the commits whose Task trailer is ``task``, newest first.

    Second batch (DEC-874): ``history`` stands before ``--``, so it is always read as a revision (one that does not
    exist is an error) and never as a path; ``--full-history`` keeps a path-limited walk from following only the side
    a merge kept of ``paths`` (W2-02's merge-back ``666f56d1`` kept its own ``src/gov/check/schema.py``), so every own
    commit that changes them is found whatever merges lie between."""
    text = _git_out(repo, "log", "--no-merges", "--no-renames", "--full-history",
                    f"--format={_MARK}%H%x09%(trailers:key=Task,valueonly,separator=%x2C)", *args, history,
                    "--", *paths)
    commits = []
    for block in text.split(_MARK)[1:]:
        head, _, rest = block.partition("\n")
        commit, _, tasks = head.partition("\t")
        if task in [value.strip() for value in tasks.split(",")]:
            commits.append((commit, rest.splitlines()))
    return commits


def own_commits(history, repo=REPO_ROOT, task=OWN_TASK):
    """The full hashes of ``history``'s own commits (no merge, Task trailer ``task``), newest first."""
    return [commit for commit, _ in _own_log(history, repo=repo, task=task)]


def own_files(history, repo=REPO_ROOT, task=OWN_TASK):
    """``(commit, status, path)`` for every file an own commit of ``history`` adds or changes (``--name-status``
    against its parent, renames as a deletion and an addition); deletions are left out."""
    found = []
    for commit, lines in _own_log(history, "--name-status", repo=repo, task=task):
        for line in lines:
            status, _, path = line.partition("\t")
            if path and not status.startswith("D"):
                found.append((commit, status, path))
    return found


def own_added_lines(history, rel, repo=REPO_ROOT, task=OWN_TASK):
    """``(commit, line)`` for every line an own commit of ``history`` adds to ``rel`` (``-p`` against its parent)."""
    found = []
    for commit, lines in _own_log(history, "-p", paths=(rel,), repo=repo, task=task):
        found.extend((commit, line[1:]) for line in lines if line.startswith("+") and not line.startswith("+++"))
    return found


def names_type(line, kind):
    """``line`` names the type ``kind``: as a quoted string (a type map key, a standalone type) or its schema file."""
    return bool(re.search(r"""(["'])""" + re.escape(kind) + r"\1", line)) or f"{kind}.schema.json" in line


def other_schema_files_brought_in(history, repo=REPO_ROOT, task=OWN_TASK):
    """Every ``(commit, status, path)`` by which an own commit adds or changes a schema file of W2-02's other types
    under either schema folder."""
    wanted = {f"{folder}/{name}" for folder in SCHEMA_FOLDERS for name in W2_02_OTHER_SCHEMAS}
    return [entry for entry in own_files(history, repo, task) if entry[2] in wanted]


def other_type_lines_brought_in(history, kind, repo=REPO_ROOT, task=OWN_TASK):
    """Every ``(commit, line)`` by which an own commit adds ``kind`` to core-schema's module."""
    return [(commit, line) for commit, line in own_added_lines(history, SCHEMA_MODULE_REL, repo, task)
            if names_type(line, kind)]


def last_own_commit_of(history, rel, repo=REPO_ROOT, task=OWN_TASK):
    """The newest own commit of ``history`` that touches ``rel``; None when there is none."""
    commits = [commit for commit, _ in _own_log(history, paths=(rel,), repo=repo, task=task)]
    return commits[0] if commits else None


# Runs ``python3 -m gov.check.schema`` with that one module read from the file named in argv[1] (a ``git show`` of one
# commit's module); every other module is this worktree's (PYTHONPATH). Relative imports resolve as under ``-m``.
_SCHEMA_AS = r'''
import importlib.abc, importlib.util, runpy, sys
_FILE = sys.argv[1]


class _One(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        return importlib.util.spec_from_file_location(name, _FILE) if name == "gov.check.schema" else None


sys.meta_path.insert(0, _One())
sys.argv = [_FILE, *sys.argv[2:]]
runpy.run_module("gov.check.schema", run_name="__main__", alter_sys=True)
'''


def core_schema_at(box, project, commit):
    """Core-schema as its declaration says, in ``project``, with its module as ``commit`` leaves it: the declared
    command with ``-m gov.check.schema`` read from ``git show <commit>:src/gov/check/schema.py`` (one named file,
    nothing checked out). Its run and its findings."""
    import shlex
    declaration = yaml.safe_load((REPO_ROOT / CHECKS_REL / "core-schema.yaml").read_text(encoding="utf-8"))
    argv = shlex.split(declaration["command"])
    at = next((i for i in range(len(argv) - 1) if argv[i:i + 2] == ["-m", "gov.check.schema"]), None)
    assert at is not None, f"core-schema's declared command runs no 'gov.check.schema': {declaration['command']}"
    module = box.workdir / "tmp" / f"schema-at-{commit[:12]}.py"
    module.write_bytes(show(commit, SCHEMA_MODULE_REL))
    done = run([*argv[:at], "-c", _SCHEMA_AS, module, *argv[at + 2:]], cwd=project, env=box.env(),
               timeout=CALL_TIMEOUT_S)
    return done, schema_findings(done)


def schema_project_at(project, files, commit):
    """As ``schema_project``, with the common and audit-report schema files as ``commit`` holds them."""
    project = new_repo(project)
    for rel in (COMMON_SCHEMA_REL, AUDIT_SCHEMA_REL):
        write(project, rel, show(commit, rel).decode("utf-8"))
    for rel, text in files.items():
        write(project, rel, text)
    commit_all(project)
    return project


def own_task_repo(project, task, adds):
    """A temporary repository built from scratch: a base commit (``Task: DAEO-base``) holding a stand-in core-schema
    module; an own commit (``Task: OWN_TASK``) that adds the ``audit-report`` type, as W2-54 does; then one commit
    carrying ``Task: <task>`` that writes ``adds`` (``{rel: text}``); then a merge of a side branch, the merge carrying
    ``Task: OWN_TASK``, whose one commit (``Task: DAEO-zflj``) adds W2-02's other schema files (a merge is never an
    own change)."""
    project = new_repo(project)
    write(project, SCHEMA_MODULE_REL, 'SCHEMA_MAP = {\n}\nSTANDALONE_TYPES = ("probe",)\n')
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base\n\nTask: DAEO-base")
    write(project, SCHEMA_MODULE_REL, 'SCHEMA_MAP = {\n    "audit-report": "audit-report.schema.json",\n}\n'
                                      'STANDALONE_TYPES = ("probe", "audit-report")\n')
    write(project, AUDIT_SCHEMA_REL, "{}\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", f"the audit-report type\n\nTask: {OWN_TASK}")
    git(project, "checkout", "-q", "-b", "side")
    for name in W2_02_OTHER_SCHEMAS:
        write(project, f"{SCHEMAS_REL}/{name}", "{}\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "side\n\nTask: DAEO-zflj")
    git(project, "checkout", "-q", "main")
    for rel, text in adds.items():
        write(project, rel, text)
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", f"the change\n\nTask: {task}")
    git(project, "merge", "-q", "--no-ff", "side", "-m", f"merge side\n\nTask: {task}")
    return project


def merge_back_repo(project):
    """Second batch (DEC-874): a temporary repository built from scratch in the shape of W2-02's merge-back
    ``666f56d1``. On ``main``, after a base commit (``Task: DAEO-base``), an own commit (``Task: OWN_TASK``) adds the
    ``audit-report`` type to core-schema's module; on ``w2-02``, from the base, a commit (``Task: DAEO-zflj``) writes
    the module with ``audit-report``, ``close`` and ``adoption-verdict`` and their schema files; then ``w2-02`` merges
    ``main`` (``Task: DAEO-zflj``) keeping its own side (``-s ours``). The checked-out branch is then ``elsewhere``, at
    the base: it holds no own commit, so only a reading of the named history finds one. Returns ``(project, the
    merge's hash, the own commit's hash)``."""
    project = new_repo(project)
    write(project, SCHEMA_MODULE_REL, 'SCHEMA_MAP = {\n}\nSTANDALONE_TYPES = ("probe",)\n')
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base\n\nTask: DAEO-base")
    base = git(project, "rev-parse", "HEAD").strip()
    write(project, SCHEMA_MODULE_REL, 'SCHEMA_MAP = {\n    "audit-report": "audit-report.schema.json",\n}\n'
                                      'STANDALONE_TYPES = ("probe", "audit-report")\n')
    write(project, AUDIT_SCHEMA_REL, "{}\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", f"the audit-report type\n\nTask: {OWN_TASK}")
    own = git(project, "rev-parse", "HEAD").strip()
    git(project, "checkout", "-q", "-b", "w2-02", base)
    write(project, SCHEMA_MODULE_REL, 'SCHEMA_MAP = {\n    "audit-report": "audit-report.schema.json",\n'
                                      '    "close": "close.schema.json",\n}\n'
                                      'STANDALONE_TYPES = ("probe", "audit-report", "adoption-verdict")\n')
    for name in ("audit-report.schema.json", *W2_02_OTHER_SCHEMAS):
        write(project, f"{SCHEMAS_REL}/{name}", "{}\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "W2-02's types\n\nTask: DAEO-zflj")
    git(project, "merge", "-q", "--no-ff", "-s", "ours", "main", "-m", "merge main, keeping W2-02's side\n\n"
                                                                       "Task: DAEO-zflj")
    merge = git(project, "rev-parse", "HEAD").strip()
    git(project, "checkout", "-q", "-b", "elsewhere", base)
    return project, merge, own


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


# --------------------------------------------------------------------------
# W2-75 (DEC-937): the green-here cases read the close's own check result (README, "W2-75")
# --------------------------------------------------------------------------
#
# Rewrite-Reason: W2-L429. Inside a close the pinned ``gov close`` sets GOV_CLOSE_CHECK_RESULT to its byte-for-byte
# copy of gate (b)'s ``gov check --json`` output (the same commit, after the rebuild; DEC-889 item 2, P-IS-2 (a)): the
# cases read that envelope and start no ``gov check``. Outside a close (the variable unset or empty) they run ``gov
# check --json`` here as before. A result that cannot be read, or is not gov check's envelope with its checks, fails
# the cases naming the file; it is never read as green, and no ``gov check`` is started in its place.

CHECK_RESULT_VARIABLE = "GOV_CLOSE_CHECK_RESULT"


class CheckResult:
    """Gate (b)'s ``gov check --json`` output as the close hands it: ``describe`` names the file, as ``Run`` does
    the process."""

    def __init__(self, path, text):
        self.path, self.stdout = Path(path), text

    def describe(self, tail=4000):
        return f"the close's check result {self.path} ({CHECK_RESULT_VARIABLE})\n{self.stdout[-tail:]}"


def read_check_result(path):
    """``(CheckResult, checks by id)`` from the ``gov check --json`` envelope at ``path``; an AssertionError naming
    the file and what is wrong with it when it is missing, unreadable, not JSON, or not gov check's envelope with
    its list of checks."""
    named = f"the close's check result {path} ({CHECK_RESULT_VARIABLE})"
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise AssertionError(f"{named} cannot be read: {e}") from None
    try:
        envelope = json.loads(text)
    except ValueError as e:
        raise AssertionError(f"{named} is not JSON ({e}): {text[:500]!r}") from None
    if not (isinstance(envelope, dict) and "ok" in envelope and envelope.get("command") == "check"):
        raise AssertionError(f"{named} is not gov check's JSON envelope: {text[:500]!r}")
    where = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
    checks = where.get("checks") if isinstance(where, dict) else None
    if not (isinstance(checks, list) and checks and all(isinstance(check, dict) for check in checks)):
        raise AssertionError(f"{named} lists no checks: {text[:1500]!r}")
    return CheckResult(path, text), checks_of(envelope)


def green_here_check(environ=None):
    """What the green-here cases judge: ``(the run or the result, checks by id)``. With GOV_CLOSE_CHECK_RESULT set
    (a close), the envelope it names, and no process is started; unset or empty, one ``gov check --json`` in this
    worktree with its ``src/``, as before (about six minutes)."""
    given = (os.environ if environ is None else environ).get(CHECK_RESULT_VARIABLE) or ""
    if given:
        return read_check_result(given)
    done = run([sys.executable, "-c", _GOV, "check", "--json"], cwd=REPO_ROOT, env=worktree_env(),
               timeout=GOV_CHECK_TIMEOUT_S)
    return done, checks_of(done.envelope())


# --------------------------------------------------------------------------
# Round 2: the query vector (owner, 2026-10-18, P-W2-30 (a))
# --------------------------------------------------------------------------
#
# The embedder is reached over HTTP at OLLAMA_HOST (Ollama's /api/tags and /api/embed). The stand-in below answers
# that interface on a loopback port and behaves as the real embedder was measured to: a text embedded right after a
# *different* text gets a slightly different vector; a text embedded right after itself gets its own vector again.
# Everything is observed through the semantic facet's public search, the retrieval's public entry, `gov context`
# and the context check; nothing names where or how a vector is kept.

SEMANTIC_MODULE = "gov.retrieval.semantic"
RETRIEVE_MODULE = "gov.retrieval.retrieve"
EMBED_MODEL = "qwen3-embedding:0.6b"             # the pinned embedder (ADR-0002 §2); no public interface selects another
EMBED_PIN = "ac6da0dfba84"                       # its pinned revision (DEC-374: the digest Ollama's model list reports)
DIGEST = EMBED_PIN + hashlib.sha256(b"w2-54 stand-in embedder").hexdigest()[:52]
OTHER_DIGEST = "5e" + hashlib.sha256(b"w2-54 another build of the embedder").hexdigest()[:62]
DIMENSIONS = 1024
CPU_SIZE = 2371270737            # what /api/ps reports as the loaded model's size (the change record, §5.5.2)
OTHER_MODEL = "nomic-embed-text:latest"
# Round 4 (DEC-798): the address of the CPU-only embedder that answers query embeddings (README, "Round 4", "The
# interfaces this KPI needs"): a setting in OLLAMA_HOST's form, and its default when it is not set.
QUERY_HOST_SETTING = "GOV_QUERY_OLLAMA_HOST"
QUERY_HOST_DEFAULT = "127.0.0.1:11435"
SHARED_HOST_DEFAULT = "127.0.0.1:11434"   # OLLAMA_HOST's default (DEC-260)
DRIFT = 0.35   # how far a text's vector moves toward the text embedded just before it (the stand-in's variation)
_STOP = {"the", "and", "for", "with", "that", "this", "each", "does", "when", "who", "what", "into", "from",
         "its", "are", "was", "has", "have", "before", "after", "then", "any", "all", "given", "query",
         "instruct", "retrieve", "relevant", "passages", "search", "web", "answer", "document"}


def word_vector(text):
    """A unit vector made of the words of ``text``: texts that share words are near each other."""
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"[a-z0-9]+", str(text).lower()):
        if len(word) < 3 or word in _STOP:
            continue
        digest = hashlib.sha256(word.encode()).digest()
        vector[int.from_bytes(digest[:4], "big") % DIMENSIONS] += 1.0 if digest[4] % 2 else -1.0
    norm = sum(value * value for value in vector) ** 0.5
    if norm == 0.0:
        vector[0], norm = 1.0, 1.0
    return [value / norm for value in vector]


def _unit(vector):
    norm = sum(value * value for value in vector) ** 0.5 or 1.0
    return [value / norm for value in vector]


class EmbedderStandIn:
    """A loopback Ollama endpoint whose vectors depend on what was embedded just before (the measured variation).

    - ``digest`` is what its model list (``GET /api/tags``) reports for the pinned model: the model's revision.
    - ``targets`` maps an exact text to another text whose words make its vector. A text sent to be embedded is
      matched by the longest key it *ends with*, compared character for character (no case folding, no Unicode
      normalisation, no stripping), so each spelling of a question can be sent to its own place in the corpus.
    - ``drift``: a text embedded right after a different text gets ``unit(own + drift * previous)``; right after
      itself (a repeat), or as the very first text, it gets ``own``. The order is the order of the texts within a
      request and across requests.
    - ``mode``: ``healthy``; ``fail`` (every embedding request answers HTTP 500); ``short`` (an embedding request
      answers with one vector fewer than it was asked for).
    - Round 4 (README, "The stand-ins of round 4"): ``device`` is where the model is loaded by a request that names
      no option (``cpu``, ``gpu``); a request whose ``options`` name ``num_gpu`` loads it on the CPU (0) or on the
      device (any other number), and a request without options is served by the runner already loaded, as Ollama
      does. ``GET /api/ps`` lists the model once it is loaded, with ``size_vram`` 0 on the CPU and equal to ``size``
      on the GPU. ``ps`` overrides what ``/api/ps`` reports, whatever is loaded: ``gpu``, ``partial`` (half of it
      in GPU memory), ``nothing``, ``other-model`` (another model, on the CPU). ``bind`` is the address to serve
      at (a free loopback port when None); ``log`` is a file every request is also appended to, as JSON lines.

    Every request is recorded: ``embedded()`` lists the texts sent to be embedded, in order.
    """

    def __init__(self, digest=DIGEST, targets=None, drift=DRIFT, device="cpu", bind=None, size=CPU_SIZE, log=None):
        self.digest, self.targets, self.drift, self.mode = digest, dict(targets or {}), drift, "healthy"
        self.requests, self.previous = [], None
        self.device, self.size, self.log, self.ps, self.loaded = device, size, log, None, None
        stand_in = self

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length).decode("utf-8") if length else ""
                try:
                    asked = json.loads(body) if body else {}
                except ValueError:
                    asked = {}
                status, reply = stand_in.reply(self.command, self.path.split("?")[0].rstrip("/"), asked)
                payload = json.dumps(reply).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = do_HEAD = do_DELETE = answer

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(bind or ("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.host = f"127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
        self._lock = threading.Lock()

    def _load(self, options):
        """Where a request with ``options`` is served: the runner it loads, or the one already loaded."""
        options = options if isinstance(options, dict) else {}
        if "num_gpu" in options:
            self.loaded = "cpu" if options["num_gpu"] == 0 or self.device == "cpu" else self.device
        elif self.loaded is None:
            self.loaded = self.device
        return self.loaded

    def ps_models(self):
        """What ``GET /api/ps`` reports now."""
        def entry(name, vram):
            return {"name": name, "model": name, "size": self.size, "digest": self.digest, "size_vram": vram,
                    "expires_at": "2026-10-19T12:05:00Z", "context_length": 8192,
                    "details": {"family": "qwen3", "parameter_size": "595.78M", "quantization_level": "Q8_0"}}
        if self.ps == "nothing":
            return []
        if self.ps == "other-model":
            return [entry(OTHER_MODEL, 0)]
        where = self.ps or self.loaded
        if where is None:
            return []
        return [entry(EMBED_MODEL, {"cpu": 0, "gpu": self.size, "partial": self.size // 2}[where])]

    def on_gpu(self):
        """True when ``/api/ps`` reports the pinned model wholly in GPU memory (``size_vram`` equal to ``size``)."""
        return any(model["name"] == EMBED_MODEL and model["size_vram"] == model["size"] > 0
                   for model in self.ps_models())

    def target(self, text):
        keys = [key for key in self.targets if text.endswith(key)]
        return self.targets[max(keys, key=len)] if keys else text

    def vector(self, text):
        own = word_vector(self.target(text))
        previous, self.previous = self.previous, text
        if previous is None or previous == text or not self.drift:
            return own
        before = word_vector(self.target(previous))
        return _unit([a + self.drift * b for a, b in zip(own, before)])

    def _record(self, entry):
        self.requests.append(entry)
        if self.log:
            with open(self.log, "a", encoding="utf-8") as handle:
                handle.write(json.dumps({"kind": "request", "pid": os.getpid(), **entry}) + "\n")

    def reply(self, method, route, asked):
        with self._lock:
            model = {"name": EMBED_MODEL, "model": EMBED_MODEL, "digest": self.digest, "size": 639150000,
                     "details": {"family": "qwen3", "parameter_size": "595.78M", "quantization_level": "Q8_0"}}
            if route in ("/api/embed", "/api/embeddings"):
                given = asked.get("input", asked.get("prompt", ""))
                texts = [given] if isinstance(given, str) else [str(text) for text in given]
                served = self._load(asked.get("options"))
                self._record({"route": route, "model": asked.get("model"), "texts": texts, "mode": self.mode,
                              "options": asked.get("options"), "served_on": served})
                if self.mode == "fail":
                    return 500, {"error": "the W2-54 stand-in embedder fails on purpose"}
                vectors = [self.vector(text) for text in texts]
                if self.mode == "short":
                    vectors = vectors[:-1]
                if route == "/api/embeddings":
                    return 200, ({"embedding": vectors[0]} if vectors else {})
                return 200, {"model": EMBED_MODEL, "embeddings": vectors, "total_duration": 1, "load_duration": 1,
                             "prompt_eval_count": len(texts)}
            self._record({"route": route, "method": method, "options": asked.get("options")})
            if route == "/api/version":
                return 200, {"version": "0.35.0"}
            if route == "/api/tags":
                return 200, {"models": [model]}
            if route == "/api/ps":
                return 200, {"models": self.ps_models()}
            if route == "/api/generate" and asked.get("model") == EMBED_MODEL:
                self._load(asked.get("options"))
                return 200, {"model": EMBED_MODEL, "response": "", "done": True}
            if route == "/api/show":
                return 200, {"details": model["details"], "capabilities": ["embedding"],
                             "model_info": {"general.architecture": "qwen3", "qwen3.embedding_length": DIMENSIONS}}
            return 404, {}

    def embedded(self):
        """Every text sent to be embedded, in the order it was sent."""
        return [text for request in self.requests if "texts" in request for text in request["texts"]]

    def asked_for(self, question):
        """How many texts sent to be embedded end with ``question`` exactly."""
        return sum(1 for text in self.embedded() if text.endswith(question))

    def embed_requests(self):
        """Every request to be embedded, in order."""
        return [request for request in self.requests if "texts" in request]

    def optioned(self):
        """Every request that named a runner option (a non-empty ``options``)."""
        return [request for request in self.requests if request.get("options")]

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def vector_site(box):
    """A folder holding one link, to the ``sqlite_vec`` package the Python that runs pytest imports (the scratch HOME
    has no user site folder to find it in); None when this machine has none."""
    spec = importlib.util.find_spec("sqlite_vec")
    if spec is None or not spec.origin:
        return None
    origin = Path(spec.origin)
    source = origin.parent if spec.submodule_search_locations else origin
    site = box.workdir / "site"
    site.mkdir(exist_ok=True)
    link = site / source.name
    if not link.is_symlink():
        link.symlink_to(source, target_is_directory=source.is_dir())
    return site


def embed_env(box, endpoint, cpu=None):
    """The scratch environment with the stand-in embedder at OLLAMA_HOST and ``sqlite_vec`` importable.

    Round 4 (DEC-798): the CPU embedder's address (``QUERY_HOST_SETTING``) is ``cpu`` (a stand-in or an address)
    when given, else the same stand-in as OLLAMA_HOST; with no endpoint, both are one dead address."""
    site = vector_site(box)
    shared = endpoint.host if endpoint else f"127.0.0.1:{_dead_port()}"
    query = cpu if isinstance(cpu, str) else cpu.host if cpu else shared
    return box.env(PYTHONPATH=os.pathsep.join([str(SRC), *([str(site)] if site else [])]),
                   OLLAMA_HOST=shared, **{QUERY_HOST_SETTING: query})


def _dead_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


# A driver: the calls of one process, through the public functions, each answer printed as JSON.
_DRIVER = r'''
import json, sys
from pathlib import Path
import gov.retrieval.semantic as semantic
import gov.retrieval.retrieve as entry

root = Path(sys.argv[1])
out = []
for call in json.loads(sys.argv[2]):
    if call[0] == "refresh":
        out.append(semantic.refresh(root))
    elif call[0] == "load":
        import gov.store
        gov.store.load(root)
        out.append(None)
    elif call[0] == "search":
        out.append(semantic.search(root, call[1], refresh=False))
    elif call[0] == "search-refresh":
        out.append(semantic.search(root, call[1], refresh=True))
    elif call[0] == "retrieve":
        out.append(entry.retrieve(root, call[1]))
    elif call[0] == "wait":
        import time
        while not Path(call[1]).exists():
            time.sleep(0.005)
        out.append(None)
print(json.dumps(out))
'''


def drive(box, project, endpoint, *calls):
    """``calls`` (``("refresh",)``, ``("load",)``, ``("search", question)``, ``("retrieve", question)``) in one
    new process, in that order; their answers."""
    return drive_env(box, project, embed_env(box, endpoint), *calls, timeout=CALL_TIMEOUT_S)


def ask(box, project, endpoint, question):
    """The semantic facet's answer to ``question`` (``search(root, question, refresh=False)``) in a new process."""
    return drive(box, project, endpoint, ("search", question))[0]


def hits_of(answer):
    """An answer as the hits it gives: chunk, path and distance, in order."""
    return [(hit.get("chunk_id"), hit.get("path"), hit.get("distance")) for hit in answer.get("hits") or []]


# The corpus of the query-vector cases: one file per subject, each with words no other file holds, so a vector
# made of one file's words has that file's chunk nearest.
SUBJECTS = {
    "notes/bakery.md": "# Bakery\n\nSourdough loaves proof overnight in the cold room; the baker scores each loaf.\n",
    "notes/tides.md": "# Tides\n\nThe harbour pilot reads the tide tables at dawn and logs the spring height.\n",
    "notes/orchard.md": "# Orchard\n\nThe orchard keeper prunes the pear trees in February with bronze shears.\n",
    "notes/kiln.md": "# Kiln\n\nThe potter fires the glazed bowls in the brick kiln on Thursdays.\n",
    "notes/forge.md": "# Forge\n\nThe smith quenches the iron horseshoes in the forge trough at noon.\n",
    "notes/apiary.md": "# Apiary\n\nThe beekeeper smokes the hives and lifts the honey frames in July.\n",
}
BAKERY, TIDES, ORCHARD, KILN, FORGE, APIARY = SUBJECTS


def semantic_project(box, project, endpoint, files=None, cpu=None):
    """A temporary project with its record store, its lexical index and its vectors, built through the stand-in
    ``endpoint``. The corpus is embedded without the variation, so two projects built alike hold the same vectors;
    the variation is on again for every question asked afterwards. ``cpu``: the CPU embedder's address during the
    build (round 4; ``embed_env``)."""
    project = new_repo(project)
    adopt_embedded(project)
    for rel, text in (files or SUBJECTS).items():
        write(project, rel, text)
    commit_all(project)
    drift, endpoint.drift = endpoint.drift, 0.0
    try:
        report = drive_env(box, project, embed_env(box, endpoint, cpu), ("refresh",), ("load",),
                           timeout=CALL_TIMEOUT_S)[0]
    finally:
        endpoint.drift = drift
    assert report.get("available") is True, f"the fixture's vectors were not built: {report}"
    return project


def home_files(box):
    """Every file under the scratch HOME of the suite's processes."""
    home = box.workdir / "home"
    return sorted(path.relative_to(home).as_posix() for path in home.rglob("*") if path.is_file())


# Tickets whose questions differ: each ticket's context asks the retrieval its own question.
QUESTION_TICKETS = {
    "TK-W254-BAKERY": "Sourdough loaf scoring by the baker",
    "TK-W254-TIDES": "Harbour tide tables read by the pilot",
    "TK-W254-ORCHARD": "Pear trees pruned by the keeper",
}
QUESTION_CHARTER = "CHARTER-W254-Q"


def ticket_files():
    """The corpus of the query-vector cases with a charter and three tickets, each with its own title."""
    files = dict(SUBJECTS)
    files["docs/charter/charter.md"] = record(QUESTION_CHARTER, "charter", "ACTIVE", "The charter of the project.")
    for ticket_id, title in QUESTION_TICKETS.items():
        files[f".tickets/{ticket_id}.md"] = ticket(ticket_id, title, [QUESTION_CHARTER])
    return files


# ---- the real embedder (this machine's Ollama), for the one case that uses it

def real_embedder_lacking():
    """Why this machine cannot run the real-embedder case; empty when it can. Nothing is started to decide it."""
    lacking = []
    if shutil.which("gitleaks") is None:
        lacking.append("gitleaks is not on PATH")
    if importlib.util.find_spec("sqlite_vec") is None:
        lacking.append(f"sqlite_vec cannot be imported by {sys.executable}")
    home = Path.home() / ".local/ollama/bin/ollama"
    if not (os.environ.get("GOV_OLLAMA_BIN") or shutil.which("ollama") or home.is_file()):
        lacking.append("no ollama executable (GOV_OLLAMA_BIN, PATH, ~/.local/ollama/bin/ollama)")
    models = Path(os.environ.get("OLLAMA_MODELS") or Path.home() / ".ollama/models")
    if not (models / "manifests/registry.ollama.ai/library/qwen3-embedding/0.6b").is_file():
        lacking.append(f"the model {EMBED_MODEL} is not in Ollama's model folder")
    return lacking


def real_env(box):
    """This machine's own environment (its Ollama), with this worktree's ``src/``; nothing may be downloaded."""
    env = {key: value for key, value in os.environ.items() if key not in ("GOV_ROLE", "GOV_TICKET")}
    env.update({"PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": str(box.workdir / "pycache"),
                "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "GIT_CONFIG_NOSYSTEM": "1"})
    return env


def drive_env(box, project, env, *calls, timeout=600.0):
    """As ``drive``, in the environment ``env``."""
    done = run([sys.executable, "-c", _DRIVER, project, json.dumps(calls)], cwd=box.workdir / "elsewhere",
               env=env, timeout=timeout)
    assert done.returncode == 0, f"the public calls failed\n{done.describe()}"
    return json.loads(done.stdout.strip().splitlines()[-1])


def adopt_embedded(project):
    """The project's path map, as ``adopt`` writes it, with the ``docs`` and ``notes`` namespaces embedded."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    keep = {key: document[key] for key in ("state_class", "capabilities", "policies", "systems") if key in document}
    spaces = {"top": (["*"], "not embedded"), "docs": (["docs/**"], "embedded"), "notes": (["notes/**"], "embedded"),
              "tickets": ([".tickets/**"], "not embedded")}
    keep["namespaces"] = {name: {"paths": patterns, "memory_class": "governance", **_NAMESPACE_FIELDS,
                                 "embedding_policy": policy} for name, (patterns, policy) in spaces.items()}
    write(project, PATH_MAP_REL, yaml.safe_dump(keep, sort_keys=False))
    shutil.copy2(REPO_ROOT / GITLEAKS_TEMPLATE_REL, Path(project) / ".gitleaks.toml")


def runtime_digest(project):
    """``relative path -> sha256`` of every file under the project's ``.gov-runtime/``."""
    base = Path(project) / ".gov-runtime"
    if not base.is_dir():
        return {}
    return {path.relative_to(base).as_posix(): sha256(path) for path in sorted(base.rglob("*")) if path.is_file()}


# --------------------------------------------------------------------------
# Round 3: the query-vector cache (owner, 2026-10-18, P-W2-32 (a))
# --------------------------------------------------------------------------
#
# What a read leaves on disk is seen as the project's file tree before and after; the store is the files named
# `store.db*` under `.gov-runtime/` (W1-19's suite: the one shared store). No case names the cache file: it is "the
# file under .gov-runtime/ a read wrote that is not the store".

RUNTIME_REL = ".gov-runtime"
STORE_PREFIX = "store.db"
# The public setting that lowers the cache's bound, in bytes (README, "The bound"): an interface this KPI needs.
CACHE_BOUND_SETTING = "GOV_QUERY_VECTOR_CACHE_MAX_BYTES"
LOW_BOUND = 262144             # 256 KiB: what the bound cases lower it to
VECTOR_BYTES = DIMENSIONS * 4  # the least one vector kept exactly takes (1024 float32 numbers)


def project_tree(project):
    """``relative path -> sha256`` of every file of ``project``, git's own folder left out."""
    project = Path(project)
    return {path.relative_to(project).as_posix(): sha256(path) for path in sorted(project.rglob("*"))
            if path.is_file() and ".git" not in path.relative_to(project).parts}


def tree_change(before, after):
    """The paths added, removed or changed between two ``project_tree`` results."""
    return sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))


def is_store(rel):
    """``rel`` (relative to the project) is a file of the shared store."""
    return rel.startswith(f"{RUNTIME_REL}/") and Path(rel).name.startswith(STORE_PREFIX)


def runtime_others(project):
    """Every file under ``.gov-runtime/`` that is not a file of the store, relative to the project."""
    base = Path(project) / RUNTIME_REL
    if not base.is_dir():
        return []
    return sorted(path.relative_to(project).as_posix() for path in base.rglob("*")
                  if path.is_file() and not path.name.startswith(STORE_PREFIX))


def others_size(project):
    """The bytes of every file under ``.gov-runtime/`` that is not a file of the store."""
    return sum((Path(project) / rel).stat().st_size for rel in runtime_others(project))


def delete_cache(project):
    """Delete every file under ``.gov-runtime/`` that is not a file of the store; what was deleted."""
    gone = runtime_others(project)
    for rel in gone:
        (Path(project) / rel).unlink()
    return gone


def tracked(project):
    """The files git tracks in ``project``."""
    return set(git(project, "ls-files", "-z").split("\0")) - {""}


def questions(count, start=0):
    """``count`` distinct questions, each with words of the corpus (so their hits differ) and a number of its own
    at its end (so no question ends with another)."""
    words = [word for text in SUBJECTS.values() for word in re.findall(r"[a-z]{4,}", text.lower())
             if word not in _STOP]
    return [f"how does the {words[(7 * n) % len(words)]} meet the {words[(11 * n + 3) % len(words)]} "
            f"item{n:04d}" for n in range(start, start + count)]


def drive_run(box, project, env, *calls, timeout=CALL_TIMEOUT_S):
    """As ``drive_env``, keeping the run: ``(answers, run)``. The answers are None when the process failed."""
    done = run([sys.executable, "-c", _DRIVER, project, json.dumps(calls)], cwd=box.workdir / "elsewhere",
               env=env, timeout=timeout)
    answers = json.loads(done.stdout.strip().splitlines()[-1]) if done.returncode == 0 and done.stdout.strip() \
        else None
    return answers, done


def clean(done):
    """Why a read's process was not clean (an exit code other than 0, a traceback); empty when it was."""
    faults = []
    if done.returncode != 0:
        faults.append(f"exit code {done.returncode}")
    if "Traceback" in done.stderr or "Traceback" in done.stdout:
        faults.append("a traceback")
    return faults


def at_once(box, project, env, call_lists, timeout=300.0):
    """One process per list of calls, all released together once every one has imported the code; their runs."""
    go = box.workdir / "tmp" / f"go-{time.monotonic_ns()}"
    started = time.monotonic()
    children = [subprocess.Popen([sys.executable, "-c", _DRIVER, str(project),
                                  json.dumps([("wait", str(go)), *calls])],
                                 cwd=str(box.workdir / "elsewhere"), env=env, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True, stdin=subprocess.DEVNULL)
                for calls in call_lists]
    time.sleep(1.5)   # every process imports the code and waits; then all are released at once
    go.touch()
    runs = []
    for child, calls in zip(children, call_lists):
        try:
            stdout, stderr = child.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            for other in children:
                other.kill()
            raise AssertionError(f"a concurrent read did not end within {timeout:.0f} s") from None
        done = subprocess.CompletedProcess(child.args, child.returncode, stdout, stderr)
        runs.append(Run(["driver", *[call[0] for call in calls]], done, time.monotonic() - started))
    return runs


class ReadOnly:
    """``with ReadOnly(paths):`` the paths (folders or files) lose every write bit; restored afterwards."""

    def __init__(self, *paths):
        self.paths = [Path(path) for path in paths]
        self.modes = {}

    def __enter__(self):
        for path in self.paths:
            self.modes[path] = path.stat().st_mode
            path.chmod(self.modes[path] & ~0o222)
        return self

    def __exit__(self, *exc):
        for path, mode in self.modes.items():
            path.chmod(mode)
        return False


def cannot_create_in(folder):
    """True when a new file cannot be made in ``folder`` (the premise of an unwritable cache folder)."""
    probe = Path(folder) / "w2-54-write-probe"
    try:
        probe.open("x").close()
    except OSError:
        return True
    probe.unlink()
    return False


# --------------------------------------------------------------------------
# Round 4: the CPU-only embedder on its own port (DEC-798, owner, 2026-10-19, P-W2-40 (b))
# --------------------------------------------------------------------------
#
# Two embedders: the shared one at OLLAMA_HOST (it builds the index) and the CPU-only one at the address the setting
# QUERY_HOST_SETTING names (it answers query embeddings, and only those). Which one a command asks is seen at the two
# stand-ins; what the CPU-only one is told when a read starts it is seen in what the stand-in executable records. No
# case names the code that does it.

def host_of(address):
    """``host:port`` of an address given in OLLAMA_HOST's forms (``host:port``, ``http://host:port/``)."""
    text = str(address or "").strip()
    text = text.split("://", 1)[-1].rstrip("/")
    return text if ":" in text else f"{text}:11434"


def gpu_hidden(env):
    """True when ``env`` tells an Ollama it starts to use no GPU, the way Ollama documents it: the CUDA devices set
    to an id that names no device (``CUDA_VISIBLE_DEVICES=-1``), or the CPU library forced (``OLLAMA_LLM_LIBRARY``
    ``cpu…``). README, "The stand-ins of round 4"."""
    if str(env.get("OLLAMA_LLM_LIBRARY", "")).lower().startswith("cpu"):
        return True
    value = env.get("CUDA_VISIBLE_DEVICES")
    if value is None or not value.strip():
        return False
    items = [item.strip() for item in value.split(",")]
    return not any(item.isdigit() or item.upper().startswith(("GPU-", "MIG-")) for item in items)


def answers(address, path="/api/version", timeout=2.0):
    """The status and JSON body of ``GET http://<address><path>``, asked by the test with no proxy; None when
    nothing answers."""
    import urllib.error
    import urllib.request
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(f"http://{host_of(address)}{path}", timeout=timeout) as reply:
            body = reply.read()
            status = reply.status
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except (urllib.error.URLError, OSError, ValueError):
        return None
    try:
        return status, json.loads(body or b"null")
    except ValueError:
        return status, None


DAEMON_LIFETIME_S = 120     # a started stand-in ends by itself after this long, whatever happens to the test
DAEMON_START_DELAY_S = 1.0  # how long a started stand-in takes before it listens (so two starts can race)

# The stand-in ``ollama`` executable. It records how it was run (its arguments, its OLLAMA_HOST and every variable
# that could tell it about the GPU). ``serve`` then waits a moment, as a daemon takes to start, and serves round 2's
# stand-in embedder at its own OLLAMA_HOST (Ollama's default when unset), with the model on the CPU when its
# environment hides the GPU and on the GPU otherwise; at an address already held it records that and ends with exit
# code 1, as Ollama does. It ends by itself after DAEMON_LIFETIME_S, records a SIGTERM or SIGINT before it ends, and
# writes nothing to its output streams.
_OLLAMA_EXE = r'''#!@PYTHON@
import json, os, signal, sys, time
sys.path.insert(0, @SUITE@)
LOG = @LOG@


def record(entry):
    with open(LOG, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


told = {key: value for key, value in os.environ.items()
        if key.startswith("OLLAMA_") or key in ("CUDA_VISIBLE_DEVICES", "HIP_VISIBLE_DEVICES",
                                                 "ROCR_VISIBLE_DEVICES", "GPU_DEVICE_ORDINAL")}
record({"kind": "exec", "argv": sys.argv[1:], "pid": os.getpid(), "env": told, "path": sys.argv[0]})
if sys.argv[1:2] != ["serve"]:
    sys.exit(0)
import w2_54_support as S

host = S.host_of(os.environ.get("OLLAMA_HOST") or S.SHARED_HOST_DEFAULT)
device = "cpu" if S.gpu_hidden(os.environ) else "gpu"
time.sleep(S.DAEMON_START_DELAY_S)
name, _, port = host.rpartition(":")
try:
    stand_in = S.EmbedderStandIn(device=device, bind=(name, int(port)), log=LOG)
except OSError as exc:
    record({"kind": "bind-failed", "pid": os.getpid(), "host": host, "error": str(exc)})
    sys.exit(1)


def stop(signum, frame):
    record({"kind": "signal", "pid": os.getpid(), "signal": signum})
    sys.exit(0)


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
record({"kind": "serving", "pid": os.getpid(), "host": host, "device": device})
end = time.monotonic() + S.DAEMON_LIFETIME_S
while time.monotonic() < end:
    time.sleep(0.1)
'''

EXECUTABLE_PLACES = ("GOV_OLLAMA_BIN", "PATH", "HOME")   # where DEC-260 finds the executable, in its order
HOME_EXECUTABLE_REL = ".local/ollama/bin/ollama"


class Daemons:
    """One case's stand-in executable and what every run of it recorded; ``close()`` ends every one it started.

    ``env(base, place)`` is ``base`` with the executable at ``place`` (``GOV_OLLAMA_BIN``, ``PATH`` or ``HOME``) or
    nowhere (None): a HOME of the case's own, and a PATH of folders that hold no ``ollama``."""

    def __init__(self, root):
        self.root = Path(root)
        self.home, self.bin, self.out = self.root / "home", self.root / "bin", self.root / "out"
        for folder in (self.home, self.bin, self.out):
            folder.mkdir(parents=True, exist_ok=True)
        self.log = self.root / "daemons.jsonl"
        self.text = (_OLLAMA_EXE.replace("@PYTHON@", sys.executable).replace("@SUITE@", repr(str(Path(__file__).parent)))
                     .replace("@LOG@", repr(str(self.log))))
        self._runs = 0

    def install(self, place):
        target = {"GOV_OLLAMA_BIN": self.root / "stand-in" / "ollama", "PATH": self.bin / "ollama",
                  "HOME": self.home / HOME_EXECUTABLE_REL}[place]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.text, encoding="utf-8")
        target.chmod(0o755)
        return target

    def env(self, base, place=None):
        env = dict(base)
        env.pop("GOV_OLLAMA_BIN", None)
        folders = [str(self.bin)] + [folder for folder in base.get("PATH", "/usr/bin:/bin").split(os.pathsep)
                                     if folder and not (Path(folder) / "ollama").exists()]
        env.update({"PATH": os.pathsep.join(folders), "HOME": str(self.home)})
        if place is not None:
            path = self.install(place)
            if place == "GOV_OLLAMA_BIN":
                env["GOV_OLLAMA_BIN"] = str(path)
        return env

    def records(self, kind=None):
        if not self.log.is_file():
            return []
        entries = [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines() if line.strip()]
        return [entry for entry in entries if kind is None or entry.get("kind") == kind]

    def serves(self):
        """Every run of the executable as ``serve``."""
        return [entry for entry in self.records("exec") if entry["argv"][:1] == ["serve"]]

    def serving(self):
        """Every started stand-in that took its address."""
        return self.records("serving")

    def alive(self, pid):
        try:
            return b"ollama" in Path(f"/proc/{pid}/cmdline").read_bytes() and \
                Path(f"/proc/{pid}/stat").read_text().split(")")[-1].split()[0] != "Z"
        except OSError:
            return False

    def asked(self, question):
        """How many texts the started stand-ins were sent to be embedded that end with ``question``."""
        return sum(1 for entry in self.records("request") for text in entry.get("texts") or []
                   if text.endswith(question))

    def run(self, argv, *, cwd, env, timeout=CALL_TIMEOUT_S):
        """``argv`` in a new process whose output streams are files (a daemon it starts may inherit them, and a
        pipe would stay open after the process ends); its Run."""
        return self.start(argv, cwd=cwd, env=env)(timeout)

    def start(self, argv, *, cwd, env):
        """``argv`` started now, its output in files; call the result with a timeout to wait for its Run."""
        self._runs += 1
        out, err = self.out / f"run-{self._runs}.out", self.out / f"run-{self._runs}.err"
        began = time.monotonic()
        with open(out, "wb") as stdout, open(err, "wb") as stderr:
            child = subprocess.Popen([str(part) for part in argv], cwd=str(cwd), env=env, stdin=subprocess.DEVNULL,
                                     stdout=stdout, stderr=stderr)

        def wait(timeout=CALL_TIMEOUT_S):
            try:
                child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
                raise AssertionError(f"{' '.join(map(str, argv[-4:]))} did not end within {timeout:.0f} s") from None
            done = subprocess.CompletedProcess(argv, child.returncode, out.read_text(encoding="utf-8", errors="replace"),
                                               err.read_text(encoding="utf-8", errors="replace"))
            return Run(argv, done, time.monotonic() - began)
        return wait

    def close(self):
        for entry in self.records("exec"):
            if self.alive(entry["pid"]):
                try:
                    os.kill(entry["pid"], 9)
                except (ProcessLookupError, PermissionError):
                    pass


def gov_argv(*args):
    """The argument list of ``gov <args>`` running this worktree's ``src/`` (as ``gov``)."""
    return [sys.executable, "-c", _GOV, *[str(arg) for arg in args]]


class NotAnEmbedder:
    """A loopback listener that is not an embedder: every request gets HTTP 404 with a page of text."""

    def __init__(self, port=0):
        self.requests = []
        requests = self.requests

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    self.rfile.read(length)
                requests.append(f"{self.command} {self.path}")
                payload = b"<html><body>Not an embedder.</body></html>"
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = do_HEAD = do_DELETE = answer

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.server.daemon_threads = True
        self.host = f"127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def facets_of(run):
    """The ``facets`` of a ``gov retrieve --json`` run that succeeded."""
    envelope = run.envelope()
    assert envelope.get("ok") is True and isinstance(envelope.get("result"), dict), run.describe()
    return envelope["result"].get("facets") or {}


def unavailable_with_reason(facet):
    """Why ``facet`` (a facet entry, or a semantic search's answer) is not "unavailable with a reason, no hit"."""
    faults = []
    if facet.get("available") is not False:
        faults.append(f"available is {facet.get('available')!r}")
    if not (isinstance(facet.get("reason"), str) and facet["reason"].strip()):
        faults.append(f"no reason ({facet.get('reason')!r})")
    if facet.get("hits"):
        faults.append(f"{len(facet['hits'])} hits")
    return faults


# ---- round 3's cache, as round 3 wrote it (the change record, §5.3; the file of this worktree's runtime folder)

ROUND_3_CACHE_REL = ".gov-runtime/query-vector-cache.db"
ROUND_3_CACHE_TABLE = ("CREATE TABLE query_vector (model TEXT NOT NULL, revision TEXT NOT NULL, text_sha256 TEXT "
                       "NOT NULL, embedding BLOB NOT NULL, PRIMARY KEY (model, revision, text_sha256))")
# What round 3's code sends to be embedded for a question, before the question (seen at the stand-in at 0914d8f8).
ROUND_3_PREFIX = "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: "


def plant_round_3_entry(project, texts, vector, revision=DIGEST):
    """Write ``vector`` into the project's cache file under round 3's key (model, revision, sha256 of the exact text
    sent) for each of ``texts``, in round 3's layout: 1024 float32 numbers, little-endian."""
    import sqlite3
    import struct
    path = Path(project) / ROUND_3_CACHE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        if connection.execute("SELECT 1 FROM sqlite_master WHERE name = 'query_vector'").fetchone() is None:
            connection.execute(ROUND_3_CACHE_TABLE)
        blob = struct.pack(f"<{len(vector)}f", *vector)
        for text in dict.fromkeys(texts):
            connection.execute("INSERT OR REPLACE INTO query_vector VALUES (?, ?, ?, ?)",
                               (EMBED_MODEL, revision, hashlib.sha256(text.encode("utf-8")).hexdigest(), blob))
        connection.commit()
    finally:
        connection.close()
    return path


def sent_for(stand_ins, question):
    """Every text the stand-ins were sent to be embedded that ends with ``question`` (the exact text sent for it)."""
    return [text for stand_in in stand_ins for text in stand_in.embedded() if text.endswith(question)]
