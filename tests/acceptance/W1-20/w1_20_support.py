"""Support code for the W1-20 acceptance tests (standard library only).

W1-20 builds ``gov closure``: the deterministic closure over referenced ids,
through the record graph (W1-10) and the code index (W1-16). The tests use only
public interfaces, stated in the README:

- the command ``gov closure`` (``python -m gov.cli.main closure``), read through
  its ``--json`` envelope and, for the byte comparison, its raw standard output;
- ``gov.closure.closure(root, ids, depth=...)``, called in a child process;
- ``gov.store.load(root)`` and ``gov.codeintel.index(root)``, to build the store
  and the code index a closure reads. A closure never builds either.

How the tests call it:

- **Every call runs in a new Python process**, with this worktree's ``src/`` on
  ``PYTHONPATH`` and a working directory that is never the repository under
  test. The environment is built from scratch: ``PATH``, an empty temporary
  ``HOME``, ``TMPDIR``, ``XDG_RUNTIME_DIR``, locale. ``GOV_ROLE`` and
  ``GOV_TICKET`` of the session that runs the tests are not passed on.
- **Every store and every code index is built in a temporary git repository**
  (DEC-322). No test reads or writes this repository's ``.gov-runtime/``, and no
  test indexes this repository or a worktree of it.
- **Two search paths.** ``bare`` holds ``git`` alone: the code tool is not on
  it, so the tests of the record graph run on any machine. ``full`` is the
  session's own ``PATH``, for the tests that run the real code tool.
- **Fixture commits have fixed dates and authors**, so the same fixture built
  twice has the same commit ids.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SRC = REPO_ROOT / "src"
COMMAND_REL = "src/gov/closure/command.py"
STORE_REL = ".gov-runtime/store.db"
INDEX_REL = ".gov-runtime/codeintel"
GITLEAKS_TEMPLATE_REL = "template/.gitleaks.toml"
TOOL = "codebase-memory-mcp"
TIMEOUT_S = 300.0

# The fixed list of stopping reasons (DEC-034, ADR-0002 section 4; the sixth value by the owner's DEC-396).
REASONS = ("CLOSURE_COMPLETE", "SATURATED", "DEPTH_LIMIT_REACHED", "BUDGET_EXHAUSTED_WITH_GAPS", "FACET_UNAVAILABLE",
           "UNRESOLVED_IDS")
COMPLETE, DEPTH_LIMIT, FACET_UNAVAILABLE = "CLOSURE_COMPLETE", "DEPTH_LIMIT_REACHED", "FACET_UNAVAILABLE"
# Everything within the depth was reached, the facets answered or were not asked, and some ids name nothing (DEC-396).
UNRESOLVED_IDS = "UNRESOLVED_IDS"
# The reasons of a gap (package DP-5): beyond the depth, no such record or symbol, or the facet could not be asked.
GAP_DEPTH, GAP_UNRESOLVED, GAP_FACET = "DEPTH_LIMIT_REACHED", "UNRESOLVED", "FACET_UNAVAILABLE"
KINDS = ("record", "symbol")
# The eight typed edges of CAP-09.a.
EDGE_TYPES = ("EVIDENCE_FOR", "CONSTRAINS", "IMPLEMENTS", "TESTS", "GENERATES", "VALIDATES", "SUPERSEDES",
              "DEPENDS_ON")


class Missing(AssertionError):
    """``gov closure`` does not exist yet."""


# Every root a test gave to ``gov closure`` or ``gov.codeintel.index``: the wrapper keeps a directory outside
# each, under ``/tmp`` (DEC-338). They are removed at the end of the session.
WRAPPED_ROOTS = set()


# --------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Box:
    """Places outside any repository: HOME, TMPDIR, a runtime directory, a working directory, a ``bare`` PATH."""
    base: Path
    home: Path
    tmp: Path
    runtime: Path
    elsewhere: Path
    bare: Path

    @property
    def full(self):
        """The session's own PATH: the code tool and gitleaks, when this machine has them."""
        return os.environ.get("PATH", "/usr/bin:/bin")


def script(path, text):
    path = Path(path)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)
    return path


def make_box(base):
    base = Path(base)
    places = [base / name for name in ("home", "tmp", "runtime", "elsewhere", "bare")]
    for place in places:
        place.mkdir(parents=True, exist_ok=True)
    script(base / "bare" / "git", f'#!/bin/sh\nexec "{shutil.which("git")}" "$@"\n')
    return Box(base, *places)


def stub(directory, name, marker, exit_code=1):
    """A program ``name`` in a new PATH directory that writes a line to ``marker`` whenever it is run."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    script(directory / name, f'#!/bin/sh\necho "{name} $*" >> "{marker}"\nexit {exit_code}\n')
    return directory


def child_env(box, path=None, **extra):
    return {
        "PATH": str(box.bare if path is None else path),
        "HOME": str(box.home),
        "TMPDIR": str(box.tmp),
        "XDG_RUNTIME_DIR": str(box.runtime),
        "LC_ALL": "C.UTF-8",
        "GIT_CONFIG_NOSYSTEM": "1",
        "PYTHONPATH": str(SRC),
        "PYTHONDONTWRITEBYTECODE": "1",
        **{key: str(value) for key, value in extra.items()},
    }


# --------------------------------------------------------------------------
# gov closure
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Run:
    argv: tuple
    returncode: int
    stdout: bytes
    stderr: str

    def describe(self):
        return (f"gov {' '.join(self.argv)}\nexit code: {self.returncode}\n"
                f"stdout:\n{self.stdout.decode('utf-8', 'replace')[-3000:]}\nstderr:\n{self.stderr[-3000:]}")


def closure(root, ids, box, depth=None, radius=None, form="json", path=None, cwd=None, **env):
    """Run ``gov closure [--json] --root <root> [--depth N] [--radius R] <id>...`` in a new process."""
    argv = ["closure", *(["--json"] if form == "json" else []), "--root", str(root)]
    if depth is not None:
        argv += ["--depth", str(depth)]
    if radius is not None:
        argv += ["--radius", str(radius)]
    argv += list(ids)
    WRAPPED_ROOTS.add(str(root))   # a closure that asks the code facet makes the wrapper's daemon directory
    try:
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", *argv], cwd=str(cwd or box.elsewhere),
                              env=child_env(box, path, **env), capture_output=True, timeout=TIMEOUT_S,
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(argv)} did not end within {TIMEOUT_S:.0f} s") from None
    return Run(tuple(argv), done.returncode, done.stdout, done.stderr.decode("utf-8", "replace"))


def envelope(run):
    """The API-0002 envelope of a ``--json`` run. A traceback is never an answer."""
    assert "Traceback" not in run.stderr, f"gov closure ended with a traceback\n{run.describe()}"
    try:
        document = json.loads(run.stdout)
    except ValueError:
        raise AssertionError(f"gov closure --json did not print one JSON document\n{run.describe()}") from None
    assert isinstance(document, dict) and document.get("command") == "closure" and "ok" in document, \
        f"gov closure --json did not print the envelope\n{run.describe()}"
    return document


def result(run):
    """The ``result`` of a run that succeeded, checked for the shape the README states."""
    document = envelope(run)
    assert run.returncode == 0 and document["ok"] is True, f"gov closure did not succeed\n{run.describe()}"
    found = document.get("result")
    assert isinstance(found, dict), f"the result is not a map\n{run.describe()}"
    assert found.get("stopping_reason") in REASONS, \
        f"`stopping_reason` is not one of the fixed list {REASONS}: {found.get('stopping_reason')!r}\n{run.describe()}"
    for key in ("closure", "gaps"):
        assert isinstance(found.get(key), list), f"`{key}` is not a list\n{run.describe()}"
    for entry in found["closure"]:
        assert isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry.get("kind") in KINDS, \
            f"a closure entry is not a map with an `id` and a `kind` of {KINDS}: {entry!r}\n{run.describe()}"
    for entry in found["gaps"]:
        assert isinstance(entry, dict) and isinstance(entry.get("id"), str) and isinstance(entry.get("reason"), str), \
            f"a gap is not a map with an `id` and a `reason`: {entry!r}\n{run.describe()}"
    return found


def ask(root, ids, box, **options):
    """The checked result of ``gov closure --json``."""
    return result(closure(root, ids, box, **options))


def ids(found, kind=None):
    """The ids of the closure, sorted; of one kind when ``kind`` is given."""
    return sorted(entry["id"] for entry in found["closure"] if kind is None or entry["kind"] == kind)


def gap_ids(found):
    return sorted(entry["id"] for entry in found["gaps"])


def gap_reasons(found, gap_id):
    """The reasons the gap list gives for ``gap_id``; empty when the id is not in the list."""
    return sorted(entry["reason"] for entry in found["gaps"] if entry["id"] == gap_id)


def code_facet(found):
    """What the result says about the code facet (package DP-4): ``facets.code``."""
    facets = found.get("facets")
    assert isinstance(facets, dict) and isinstance(facets.get("code"), str), \
        f"the result does not state the code facet in `facets.code`: {found.get('facets')!r}"
    return facets["code"]


def require_built(box):
    """Raise Missing unless ``gov closure`` is built: the reserved name answers NOT_IMPLEMENTED until then."""
    run = closure(box.elsewhere, ["W1-20-PROBE"], box, depth=0)
    code = None
    try:
        code = json.loads(run.stdout).get("error", {}).get("code")
    except (ValueError, AttributeError):
        pass
    if code == "NOT_IMPLEMENTED" or not (REPO_ROOT / COMMAND_REL).is_file():
        raise Missing(f"gov closure is not built: there is no {COMMAND_REL} "
                      f"(the command answers {code or 'nothing'}, exit code {run.returncode})")


# --------------------------------------------------------------------------
# Python calls in a child process: gov.closure, gov.store, gov.codeintel
# --------------------------------------------------------------------------

_CHILD = (
    "import importlib, json, sys\n"
    "from pathlib import Path\n"
    "module, function, root, args, kwargs = json.loads(sys.argv[1])\n"
    "value = getattr(importlib.import_module(module), function)(Path(root), *args, **kwargs)\n"
    "print('W1-20-RESULT ' + json.dumps(value, default=str))\n"
)


def call(module, function, root, box, *args, path=None, env=None, **kwargs):
    """``module.function(Path(root), *args, **kwargs)`` in a new process; the value, through JSON."""
    request = json.dumps([module, function, str(root), list(args), kwargs])
    done = subprocess.run([sys.executable, "-c", _CHILD, request], cwd=str(box.elsewhere),
                          env=child_env(box, path, **(env or {})), capture_output=True, text=True, timeout=TIMEOUT_S,
                          stdin=subprocess.DEVNULL)
    lines = [line for line in done.stdout.splitlines() if line.startswith("W1-20-RESULT ")]
    assert done.returncode == 0 and lines, \
        f"{module}.{function} failed (exit code {done.returncode}):\n{done.stdout[-2000:]}\n{done.stderr[-3000:]}"
    return json.loads(lines[-1][len("W1-20-RESULT "):])


_CHILD_SEVERAL = (
    "import importlib, json, sys\n"
    "from pathlib import Path\n"
    "module, root, requests = json.loads(sys.argv[1])\n"
    "module = importlib.import_module(module)\n"
    "values = [getattr(module, function)(Path(root), *args) for function, args in requests]\n"
    "print('W1-20-RESULT ' + json.dumps(values, default=str))\n"
)


def calls(module, root, box, requests, path=None):
    """``module.function(Path(root), *args)`` for every ``(function, args)`` of ``requests``, one after the other
    in one new process; the values in that order, through JSON. The code tool's start is paid per process that
    loads the code graph (DEC-561): questions of one repository state that need no process of their own go here."""
    request = json.dumps([module, str(root), [[function, list(args)] for function, args in requests]])
    done = subprocess.run([sys.executable, "-c", _CHILD_SEVERAL, request], cwd=str(box.elsewhere),
                          env=child_env(box, path), capture_output=True, text=True, timeout=TIMEOUT_S,
                          stdin=subprocess.DEVNULL)
    lines = [line for line in done.stdout.splitlines() if line.startswith("W1-20-RESULT ")]
    assert done.returncode == 0 and lines, \
        f"{module}: {requests} failed (exit code {done.returncode}):\n{done.stdout[-2000:]}\n{done.stderr[-3000:]}"
    values = json.loads(lines[-1][len("W1-20-RESULT "):])
    assert len(values) == len(requests), f"{module}: {len(requests)} calls gave {len(values)} values"
    return values


def load_store(root, box):
    """``gov.store.load(root)``: the store a closure reads, built in the temporary repository."""
    return call("gov.store", "load", root, box)


def build_index(root, box):
    """``gov.codeintel.index(root)``: the code index a closure reads, built in the temporary repository."""
    WRAPPED_ROOTS.add(str(root))
    return call("gov.codeintel", "index", root, box, path=box.full)


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------

BASE_DATE = "2026-09-01T12:00:00+00:00"


def git(project, *args, date=BASE_DATE):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(project), "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W1-20 tests", "GIT_AUTHOR_EMAIL": "w1-20@example.invalid",
        "GIT_COMMITTER_NAME": "W1-20 tests", "GIT_COMMITTER_EMAIL": "w1-20@example.invalid",
        "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
    }
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def commit(project, message="work", date=BASE_DATE):
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message, date=date)
    return head(project)


def head(project):
    return git(project, "rev-parse", "HEAD").strip()


def clone(source, destination):
    """A clone of a temporary fixture repository (never of this repository)."""
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(source), str(destination)], check=True,
                   capture_output=True)
    return Path(destination)


def porcelain(project):
    return git(project, "status", "--porcelain", "--untracked-files=all").splitlines()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# The fixture record set
# --------------------------------------------------------------------------

def record(record_id, record_type="decision", status="ACTIVE", **edges):
    """A record file: frontmatter (``id``, ``type``, ``status``, ``state_class``, the edge keys) and a body."""
    lines = [f"id: {record_id}", f"type: {record_type}", f"status: {status}", "state_class: AUTHORITATIVE"]
    lines += [f"{key}: {json.dumps(value)}" for key, value in edges.items()]  # a JSON list is a YAML flow value
    return "---\n" + "\n".join(lines) + f"\n---\n\n# {record_id}\n\nBody text.\n"


def record_path(record_id):
    return f"docs/records/{record_id}.md"


CHAIN = [f"CH-{number:04d}" for number in range(1, 11)]       # CH-0001 depends on CH-0002, ... up to CH-0010
CYCLE = ["CY-0001", "CY-0002"]                                # each depends on the other
HUB = "HUB-0001"                                              # one edge of each of the eight types
HUB_TARGETS = {edge_type: f"TGT-{position:04d}" for position, edge_type in enumerate(EDGE_TYPES, start=1)}
DANGLING_START, DANGLING_NEXT = "DG-0001", "DG-0002"
MISSING_NEAR, MISSING_FAR = "MISSING-0404", "MISSING-0405"    # ids of no record: one hop and two hops from DG-0001
REQUIREMENT, IMPLEMENTER, VALIDATOR = "REQ-0001", "DAEO-zzzz", "TR-0001"   # the two name the requirement
SOLO = "SOLO-0001"                                            # names nothing and is named by nothing
UNKNOWN = "NOPE-0001"                                       # no record and no symbol anywhere


def record_files():
    """``path -> text`` of the fixture's records. No component names a record of another component."""
    records = {}
    for position, record_id in enumerate(CHAIN):
        following = CHAIN[position + 1:position + 2]
        records[record_id] = record(record_id, depends_on=following) if following else record(record_id)
    records[CYCLE[0]] = record(CYCLE[0], depends_on=[CYCLE[1]])
    records[CYCLE[1]] = record(CYCLE[1], depends_on=[CYCLE[0]])
    records[HUB] = record(HUB, **{edge_type.lower(): [target] for edge_type, target in HUB_TARGETS.items()})
    for target in HUB_TARGETS.values():
        records[target] = record(target, record_type="requirement")
    records[DANGLING_START] = record(DANGLING_START, depends_on=[DANGLING_NEXT, MISSING_NEAR])
    records[DANGLING_NEXT] = record(DANGLING_NEXT, validates=[MISSING_FAR])
    records[SOLO] = record(SOLO)
    records[REQUIREMENT] = record(REQUIREMENT, record_type="requirement")
    records[IMPLEMENTER] = record(IMPLEMENTER, record_type="task", status="closed", implements=[REQUIREMENT])
    records[VALIDATOR] = record(VALIDATOR, record_type="evidence", status="FINAL", validates=[REQUIREMENT])
    return {record_path(record_id): text for record_id, text in records.items()}


# Four functions in one file: top calls mid, mid calls leaf, side calls leaf. Nothing calls top or side.
CODE_REL = "app/flow.py"
LEAF, MID, TOP, SIDE, DRAFT = "w20_leaf", "w20_mid", "w20_top", "w20_side", "w20_draft"
CODE = (
    f"def {LEAF}(value):\n    return value + 1\n\n\n"
    f"def {MID}(value):\n    return {LEAF}(value) * 2\n\n\n"
    f"def {TOP}(value):\n    return {MID}(value) - 3\n\n\n"
    f"def {SIDE}(value):\n    return {LEAF}(value) + 5\n"
)
DRAFT_CODE = f"\n\ndef {DRAFT}(value):\n    return {LEAF}(value) - 7\n"
CALLERS = {LEAF: [MID, SIDE], MID: [TOP], TOP: [], SIDE: []}   # what the source above says

# One namespace: everything in the repository is governance memory, so only a secret keeps a file out of the index.
PATH_MAP = (
    "state_class: AUTHORITATIVE\n\nnamespaces:\n  everything:\n    paths: [\"**\"]\n    memory_class: governance\n"
    "    sensitivity: internal\n    permitted_roles: [orchestrator, engineer, independent-test-designer]\n"
    "    retention: kept in git history\n    export_policy: allowed\n    embedding_policy: embedded\n"
    "    provenance: written by the W1-20 tests\n    deletion_rebuild: authoritative; restored from git only\n"
)


def build_fixture(project, code=False):
    """Build the fixture repository and commit it. ``code`` adds the adoption files and the four functions."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    write(project, ".gitignore", ".gov-runtime/\n")
    write(project, "README.md", "# A project\n\nNo frontmatter here.\n")
    for rel, text in sorted(record_files().items()):
        write(project, rel, text)
    if code:
        write(project, "governance/project/path-map.yaml", PATH_MAP)
        shutil.copyfile(REPO_ROOT / GITLEAKS_TEMPLATE_REL, project / ".gitleaks.toml")
        write(project, CODE_REL, CODE)
    commit(project, "fixture")
    return project


# --------------------------------------------------------------------------
# What must not happen: a model, the daemon directories left behind
# --------------------------------------------------------------------------

class Listener:
    """A loopback port that counts who connects: the endpoint a closure would reach if it asked Ollama."""

    def __enter__(self):
        self.socket = socket.socket()
        self.socket.bind(("127.0.0.1", 0))
        self.socket.listen()
        self.socket.setblocking(False)
        self.address = "127.0.0.1:%d" % self.socket.getsockname()[1]
        return self

    def connections(self):
        count = 0
        while True:
            try:
                self.socket.accept()[0].close()
            except BlockingIOError:
                return count
            count += 1

    def __exit__(self, *exc):
        self.socket.close()


def remove_daemon_dirs(box):
    """At the end of a session: remove the daemon directory of each of this suite's roots, and nothing else.

    Such a directory holds nothing but the tool's folder ``cbm-daemon-<uid>``, and that folder only plain files.
    The folder above it, shared by every repository of the user, is left alone.
    """
    folder = f"cbm-daemon-{os.getuid()}"
    for root in sorted(WRAPPED_ROOTS):
        try:
            path = Path(call("gov.codeintel", "daemon_dir", root, box))
            if path.is_symlink() or not path.is_dir() or os.listdir(path) not in ([], [folder]):
                continue
            inside = list(os.scandir(path / folder)) if (path / folder).is_dir() else []
            if (path / folder).is_symlink() or any(not entry.is_file(follow_symlinks=False) for entry in inside):
                continue
            for entry in inside:
                os.unlink(entry.path)
            if (path / folder).is_dir():
                (path / folder).rmdir()
            path.rmdir()
        except (AssertionError, OSError, subprocess.TimeoutExpired):
            continue
