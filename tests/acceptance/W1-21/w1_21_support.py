"""Support code for the W1-21 acceptance tests (standard library and PyYAML only).

W1-21 builds ``gov retrieve``: retrieval in batches with a continuation, merged, filtered by authority, reranked
once, and returned as a cited evidence bundle with one stopping reason. The tests use only public interfaces:

- ``gov.retrieval.retrieve.retrieve(root, query, ...)``, called in a child process (the README states the
  arguments and the bundle; every name the tests rely on is one constant below, so a decision changes one line);
- the command ``gov retrieve`` (``python -m gov.cli.main retrieve``), read through its ``--json`` envelope;
- ``gov.retrieval.lexical``, ``gov.retrieval.semantic`` and ``gov.store`` to build what a retrieval reads, and
  ``gov check --list`` for the family check.

How the tests call it:

- **Every call runs in a new Python process** with this worktree's ``src/`` on ``PYTHONPATH`` and a working
  directory that is never the project under test.
- **Nothing is built in this worktree** (DEC-322). Every project is a temporary git repository with its own
  path map, its own ``.gitleaks.toml`` and its own ``.gov-runtime/``.
- **The scratch environment** is built from nothing: an empty ``HOME`` (so the default reranker is absent,
  DEC-374), a ``PATH`` that holds ``git`` and ``gitleaks`` only (so the code tool is absent), and ``OLLAMA_HOST``
  pointing at a loopback port that is dead or served by the stand-in endpoint of this module. No model runs.
- **The real environment** is this machine's own, for the cases that need the models; they are marked
  ``local_only`` and ``needs(...)``, and skip where the machine lacks something. Nothing is installed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import tomllib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"

# ---- the public interface (package DP-1)
RETRIEVE = "gov.retrieval.retrieve"
FUNCTION = "retrieve"
COMMAND_REL = "src/gov/retrieve/command.py"  # DEC-317: the one file that builds `gov retrieve`
LEXICAL, SEMANTIC, STORE = "gov.retrieval.lexical", "gov.retrieval.semantic", "gov.store"
CHECKS_REL = "template/governance/kernel/checks"
CHECK_GLOB = "retrieval-regression*"
FAMILY = "retrieval-regression"
CHECK_FIELDS = ("id", "family", "tier", "severity", "command")
PYPROJECT_REL = "pyproject.toml"
RUNTIME_REL = ".gov-runtime"
PATH_MAP_REL = "governance/project/path-map.yaml"
CONFIG_REL = ".gitleaks.toml"
TEMPLATE_CONFIG_REL = "template/.gitleaks.toml"
CALL_TIMEOUT_S = 300.0
MEASURE_TIMEOUT_S = 3600.0
MISSING_EXIT = 3

# ---- the bundle (package DP-1): its keys
K_REASON, K_EVIDENCE, K_BATCHES, K_MERGE, K_EXPANSIONS = "stopping_reason", "evidence", "batches", "merge", "expansions"
K_GAPS, K_FACETS, K_BUDGET, K_CONTINUATION = "gaps", "facets", "budget", "continuation"
# an evidence item
E_ID, E_SHA, E_PATH, E_START, E_END, E_TEXT, E_CHUNK, E_ROUTES, E_BATCH = \
    "id", "sha256", "path", "start_line", "end_line", "text", "chunk_id", "routes", "batch"
# the merge
M_CANDIDATES, M_DUPLICATES, M_DROPPED, M_RERANKED = "candidates", "duplicates", "dropped", "reranked"
# the budget: ``budget.rounds`` is the retrieval spend, ``budget.bundle`` the bundle budget, each {limit, used}
B_ROUNDS, B_BUNDLE, B_LIMIT, B_USED = "rounds", "bundle", "limit", "used"
ROUTE_LEXICAL, ROUTE_SEMANTIC, ROUTE_CLOSURE = "lexical", "semantic", "closure"

# The fixed list of stopping reasons (ADR-0002 section 4, DEC-034; the sixth value by DEC-396).
REASONS = ("CLOSURE_COMPLETE", "SATURATED", "DEPTH_LIMIT_REACHED", "BUDGET_EXHAUSTED_WITH_GAPS", "FACET_UNAVAILABLE",
           "UNRESOLVED_IDS")
COMPLETE, SATURATED, DEPTH_LIMIT, BUDGET_EXHAUSTED, FACET_UNAVAILABLE, UNRESOLVED_IDS = REASONS
# The two reasons that say nothing is left to gather.
NOTHING_LEFT = (COMPLETE, SATURATED)
GAP_UNRESOLVED = "UNRESOLVED"  # a gap's reason, as `gov closure` gives it (DEC-391)
DROP_SUPERSEDED = "SUPERSEDED"

# Follow-up rounds by impact radius: DEC-035's table, as DEC-391 read it for depth, and the profile of each
# radius by DEC-005 (package DP-2: the numbers are placeholders in the decision).
ROUNDS_BY_RADIUS = {0: 1, 1: 1, 2: 3, 3: 8, 4: 8}
RADIUS_FULL = 3   # FULL, R3 and above: 8 follow-up rounds, and a closure depth of 8
RADIUS_LITE = 0   # LITE, R0 and R1: 1 follow-up round, and a closure depth of 1
# The bundle budget is counted in tokens, a token being four characters (S0b2's method; package DP-3). The two
# limits below hold whichever of the two units is taken: the child fits both, the parent fits only the large one.
BUDGET_SMALL, BUDGET_LARGE = 1500, 1_000_000
BATCH_LARGE = 200

EMBED_MODEL = "qwen3-embedding:0.6b"
RERANK_MODEL = "Qwen/Qwen3-Reranker-0.6B"
RERANK_REVISION = "e61197ed45024b0ed8a2d74b80b4d909f1255473"
RERANK_PYTHON_REL = ".local/share/gov-os/reranker-venv/bin/python"
HIT_AT_5_PASS_LINE = 80.0   # DEC-414: the pass line on the dev tiers; 85 is re-measured at the Wave 1 exit run
# S0b2's R1 cited a must-not-cite path 5 times in the first five (RESULTS.md). Three are a-dev decisions whose
# frontmatter says SUPERSEDED; two are b-dev files that no frontmatter marks (package DP-7).
FORBIDDEN_BASELINE = 2

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS") or "~/gov-os-workbench/synthetic").expanduser()
QUERY_SET = DEV_TIERS / "dev-queryset.yaml"
TIERS = {"A": "a-dev", "B": "b-dev"}


class Missing(AssertionError):
    """Something the ticket builds does not exist yet."""


# --------------------------------------------------------------------------
# The driver: one child process per batch of calls
# --------------------------------------------------------------------------

_DRIVER = r'''
import importlib, json, sys
from pathlib import Path

request = json.loads(sys.stdin.read())
LOG = {"loads": 0, "passes": []}


def loader():
    """The stand-in reranker's loader: counts each load; the scorer records each pass."""
    LOG["loads"] += 1
    favour = request["favour"]

    def score(query, texts):
        texts = [str(text) for text in texts]
        LOG["passes"].append({"query": query, "texts": texts})
        return [float(sum(text.count(word) for word in favour)) for text in texts]

    return score


def broken():
    """A reranker that loads and then dies: its scorer raises."""
    LOG["loads"] += 1

    def score(query, texts):
        LOG["passes"].append({"query": query, "texts": [str(text) for text in texts]})
        raise RuntimeError("the reranker process ended")

    return score


def decode(value):
    if isinstance(value, dict) and set(value) == {"$path"}:
        return Path(value["$path"])
    return {"$reranker": loader, "$broken": broken, "$absent": lambda: None}.get(value, value) \
        if isinstance(value, str) else value


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
    except Exception as exc:  # reported, so a test can say "never raises"
        record["error"] = {"type": type(exc).__name__, "message": str(exc), "code": getattr(exc, "code", None)}
    out["calls"].append(record)
out["reranker"] = LOG
print("\n" + json.dumps(out, default=repr))
'''

RERANKER, BROKEN_RERANKER, ABSENT_RERANKER = "$reranker", "$broken", "$absent"


def path_arg(path):
    return {"$path": str(path)}


class Outcome:
    """What one driver process reported."""

    def __init__(self, data, stderr):
        self.calls, self.stderr = data["calls"], stderr
        self.loads, self.passes = data["reranker"]["loads"], data["reranker"]["passes"]

    def error(self, index=0):
        return self.calls[index]["error"]

    def value(self, index=0):
        call = self.calls[index]
        assert call["error"] is None, \
            f"call {index} raised {call['error']['type']}: {call['error']['message']}\n{self.stderr[-2000:]}"
        return call["value"]


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class Api:
    """Calls this worktree's modules and its ``gov`` command line, each in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "site", "bin"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        # The scratch PATH: git, gitleaks and this interpreter (a declared check command names `python3`).
        for tool in ("git", "gitleaks", "python3"):
            found = sys.executable if tool == "python3" else shutil.which(tool)
            if found:
                wrapper = self.workdir / "bin" / tool
                wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
                wrapper.chmod(0o755)
        self.site = self._link_sqlite_vec()
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")
        self.dead_host = f"127.0.0.1:{free_port()}"

    def _link_sqlite_vec(self):
        """A folder that links the one package ``sqlite_vec`` this machine's Python imports (DEC-397): the empty
        HOME has no user site folder to find it in. None when the machine has none."""
        spec = importlib.util.find_spec("sqlite_vec")
        if spec is None or not spec.origin:
            return None
        origin = Path(spec.origin)
        source = origin.parent if spec.submodule_search_locations else origin
        link = self.workdir / "site" / source.name
        if not link.is_symlink():
            link.symlink_to(source, target_is_directory=source.is_dir())
        return self.workdir / "site"

    def scratch_env(self, ollama_host=None, **extra):
        """Built from nothing: no reranker environment, no code tool, and an endpoint that is dead unless given."""
        return {
            "PATH": str(self.workdir / "bin"),
            "HOME": str(self.workdir / "home"),
            "TMPDIR": str(self.workdir / "tmp"),
            "XDG_RUNTIME_DIR": str(self.workdir / "tmp"),
            "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": os.pathsep.join([str(SRC), *([str(self.site)] if self.site else [])]),
            "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
            "OLLAMA_HOST": ollama_host or self.dead_host,
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            **extra,
        }

    def real_env(self):
        """This machine's own environment, for the cases that need the models; nothing may be downloaded."""
        env = {key: value for key, value in os.environ.items() if key not in ("GOV_ROLE", "GOV_TICKET")}
        env.update({"PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
                    "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "GIT_CONFIG_NOSYSTEM": "1"})
        return env

    def run(self, calls, *, env=None, favour=(), timeout=CALL_TIMEOUT_S):
        """Run ``[(module, function, args, kwargs), ...]`` in one process and return its :class:`Outcome`."""
        request = {"favour": list(favour),
                   "calls": [{"module": module, "function": function, "args": list(args), "kwargs": dict(kwargs)}
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
            raise Missing(f"{RETRIEVE}.{FUNCTION} does not exist: {done.stderr.strip()}")
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr[-4000:]}"
        try:
            data = json.loads(done.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            raise AssertionError(f"{what} did not return JSON values:\n{done.stdout}\n{done.stderr}") from None
        return Outcome(data, done.stderr)

    def call(self, module, function, *args, env=None, **kwargs):
        return self.run([(module, function, args, kwargs)], env=env).value()

    def exists(self):
        """Raise Missing unless ``gov.retrieval.retrieve.retrieve`` can be imported."""
        done = subprocess.run([sys.executable, "-c", f"from {RETRIEVE} import {FUNCTION}"], capture_output=True,
                              text=True, cwd=str(self.workdir / "elsewhere"), env=self.scratch_env())
        if done.returncode != 0:
            last = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else "import failed"
            raise Missing(f"{RETRIEVE}.{FUNCTION} does not exist: {last}")

    # ---- what a retrieval reads

    def build(self, root, host=None, env=None):
        """Build the lexical index, the vectors (when the endpoint answers) and the record graph of ``root``."""
        env = env or self.scratch_env(host)
        outcome = self.run([(LEXICAL, "refresh", [path_arg(root)], {}), (SEMANTIC, "refresh", [path_arg(root)], {}),
                            (STORE, "load", [path_arg(root)], {})], env=env, timeout=MEASURE_TIMEOUT_S)
        return [outcome.value(index) for index in range(3)]

    # ---- the function

    def outcome(self, root, query, *, host=None, env=None, favour=(), **kwargs):
        """One call of ``retrieve`` and what its process reported."""
        return self.run([(RETRIEVE, FUNCTION, [path_arg(root), query], kwargs)],
                        env=env or self.scratch_env(host), favour=favour)

    def retrieve(self, root, query, **kwargs):
        """The bundle of one call of ``retrieve``."""
        return self.outcome(root, query, **kwargs).value()

    # ---- the command

    def gov(self, *args, host=None, env=None, cwd=None):
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args], capture_output=True, text=True,
                              cwd=str(cwd or self.workdir / "elsewhere"), env=env or self.scratch_env(host),
                              timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
        return Run(("gov", *args), done)

    def command(self, root, *args, **kwargs):
        """``gov retrieve --json --root <root> <args>``."""
        return self.gov("retrieve", "--json", "--root", str(root), *args, **kwargs)

    def command_exists(self):
        if not (REPO_ROOT / COMMAND_REL).is_file():
            raise Missing(f"gov retrieve is not built: there is no {COMMAND_REL} (DEC-317)")


class Run:
    def __init__(self, argv, done):
        self.argv, self.returncode, self.stdout, self.stderr = argv, done.returncode, done.stdout, done.stderr
        self.output = done.stdout + done.stderr

    def describe(self):
        return f"{' '.join(self.argv)}\nexit code: {self.returncode}\nstdout:\n{self.stdout}\nstderr:\n{self.stderr}"

    def envelope(self):
        try:
            envelope = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"standard output is not one JSON envelope\n{self.describe()}") from None
        assert envelope.get("command") == "retrieve", self.describe()
        return envelope

    def bundle(self):
        """The envelope's result of a call that succeeded."""
        assert self.returncode == 0, f"gov retrieve did not succeed\n{self.describe()}"
        envelope = self.envelope()
        assert envelope.get("ok") is True and isinstance(envelope.get("result"), dict), self.describe()
        return envelope["result"]


# --------------------------------------------------------------------------
# What a case needs from this machine
# --------------------------------------------------------------------------

def _needs():
    """``name -> reason to skip`` for everything this machine lacks. Nothing is run, started or installed."""
    lacking = {}
    if shutil.which("gitleaks") is None:
        lacking["gitleaks"] = "gitleaks is not on PATH on this machine; the secret filter cannot run (DEC-287)"
    if importlib.util.find_spec("sqlite_vec") is None:
        lacking["sqlite_vec"] = f"sqlite_vec cannot be imported by {sys.executable}; no vector can be stored"
    home = Path.home()
    ollama = os.environ.get("GOV_OLLAMA_BIN") or shutil.which("ollama") or home / ".local/ollama/bin/ollama"
    name, _, tag = EMBED_MODEL.partition(":")
    models = Path(os.environ.get("OLLAMA_MODELS") or home / ".ollama/models")
    if not Path(ollama).is_file():
        lacking["ollama"] = "no ollama executable (GOV_OLLAMA_BIN, PATH, ~/.local/ollama/bin/ollama)"
    elif not (models / "manifests/registry.ollama.ai/library" / name / tag).is_file():
        lacking["ollama"] = f"the model {EMBED_MODEL} is not in Ollama's model folder"
    cache = os.environ.get("HF_HUB_CACHE") or Path(os.environ.get("HF_HOME") or home / ".cache/huggingface") / "hub"
    snapshot = Path(cache) / ("models--" + RERANK_MODEL.replace("/", "--")) / "snapshots" / RERANK_REVISION
    if not (home / RERANK_PYTHON_REL).is_file():
        lacking["reranker"] = f"no interpreter at ~/{RERANK_PYTHON_REL}: the reranker environment is absent (DEC-397)"
    elif not snapshot.is_dir():
        lacking["reranker"] = f"{RERANK_MODEL}@{RERANK_REVISION[:12]} is not in the Hugging Face cache"
    return lacking


NEEDS = _needs()


def lacking(*names):
    return [NEEDS[name] for name in names if name in NEEDS]


# --------------------------------------------------------------------------
# The bundle
# --------------------------------------------------------------------------

def sha256(data):
    return hashlib.sha256(data).hexdigest()


def span_of(root, rel, start, end):
    """The bytes of lines ``start`` to ``end`` (1-based, inclusive) of the file as it stands."""
    lines = (Path(root) / rel).read_bytes().splitlines(keepends=True)
    return b"".join(lines[start - 1:end])


def check_citation(root, item):
    """An evidence item cites bytes that exist: its sha256 is that of the cited file or of the cited span, and
    its text is in the span it names (CAP-55.a; the validator of W1-22 checks the same)."""
    source = Path(root) / item[E_PATH]
    assert source.is_file(), f"an evidence item cites a file that does not exist: {item!r}"
    lines = source.read_bytes().splitlines(keepends=True)
    start, end = item[E_START], item[E_END]
    assert 1 <= start <= end <= len(lines), f"the cited lines are not in the file ({len(lines)} lines): {item!r}"
    span = b"".join(lines[start - 1:end])
    assert item[E_SHA] in (sha256(source.read_bytes()), sha256(span)), \
        f"the sha256 is neither that of {item[E_PATH]} nor that of its lines {start}-{end}: {item[E_SHA]}"
    # The index holds chunks of blank lines too (between two functions): the text may be blank, never foreign.
    assert item[E_TEXT].strip() in span.decode("utf-8", "replace"), \
        f"the cited text is not in lines {start}-{end} of {item[E_PATH]}: {item[E_TEXT][:200]!r}"


def check_item(item):
    assert isinstance(item, dict), f"an evidence item is not a map: {item!r}"
    for key in (E_ID, E_PATH, E_TEXT, E_CHUNK):
        assert isinstance(item.get(key), str) and item[key], f"an evidence item has no {key}: {item!r}"
    assert isinstance(item.get(E_SHA), str) and re.fullmatch(r"[0-9a-f]{64}", item[E_SHA]), \
        f"an evidence item has no sha256 (64 hexadecimal characters): {item!r}"
    for key in (E_START, E_END, E_BATCH):
        assert type(item.get(key)) is int, f"an evidence item's {key} is not a whole number: {item!r}"
    assert isinstance(item.get(E_ROUTES), list) and item[E_ROUTES], f"an evidence item names no route: {item!r}"
    return item


def check_bundle(bundle, root=None):
    """The form every bundle has, whatever was asked (KPI success 2). With ``root``, every citation is checked
    against the bytes of the project."""
    assert isinstance(bundle, dict), f"the bundle is not a map: {bundle!r}"
    reason = bundle.get(K_REASON)
    assert isinstance(reason, str), f"`{K_REASON}` is not one value: {reason!r}"
    assert reason in REASONS, f"the stopping reason {reason!r} is not in the fixed list {REASONS}"
    evidence = bundle.get(K_EVIDENCE)
    assert isinstance(evidence, list), f"`{K_EVIDENCE}` is not a list: {bundle!r}"
    for item in evidence:
        check_item(item)
        if root is not None:
            check_citation(root, item)
    ids = [item[E_CHUNK] for item in evidence]
    assert len(set(ids)) == len(ids), f"a chunk is cited twice: {sorted(i for i in ids if ids.count(i) > 1)}"
    batches = bundle.get(K_BATCHES)
    assert isinstance(batches, list) and batches and all(isinstance(batch, dict) for batch in batches), \
        f"`{K_BATCHES}` does not list the batches: {batches!r}"
    assert all(1 <= item[E_BATCH] <= len(batches) for item in evidence), \
        f"an evidence item names a batch the bundle does not list ({len(batches)} batches)"
    gaps = bundle.get(K_GAPS)
    assert isinstance(gaps, list) and all(isinstance(gap, dict) and isinstance(gap.get("reason"), str) and
                                          gap["reason"] for gap in gaps), f"`{K_GAPS}` is not a list of gaps: {gaps!r}"
    token = bundle.get(K_CONTINUATION, "")
    assert token is None or (isinstance(token, str) and token), \
        f"`{K_CONTINUATION}` is neither null nor a token: {token!r}"
    if reason == BUDGET_EXHAUSTED:
        assert gaps, "the budget was reached and no gap is listed: a silent truncation"
    if token is not None:
        assert reason not in NOTHING_LEFT, \
            f"the bundle can be continued and says {reason}: a batch-size limit reported as completeness"
    facets = bundle.get(K_FACETS)
    assert isinstance(facets, dict), f"`{K_FACETS}` is not a map: {bundle!r}"
    for facet in (ROUTE_LEXICAL, ROUTE_SEMANTIC):
        assert isinstance(facets.get(facet), dict) and isinstance(facets[facet].get("available"), bool), \
            f"`{K_FACETS}` does not report the state of the {facet} route: {facets!r}"
    assert isinstance(bundle.get(K_MERGE), dict), f"`{K_MERGE}` is not a map: {bundle!r}"
    assert isinstance(bundle.get(K_EXPANSIONS), list), f"`{K_EXPANSIONS}` is not a list: {bundle!r}"
    return bundle


def paths(bundle):
    """The cited paths, in the bundle's order, each once."""
    return list(dict.fromkeys(item[E_PATH] for item in bundle[K_EVIDENCE]))


def chunk_ids(bundle):
    return [item[E_CHUNK] for item in bundle[K_EVIDENCE]]


def rounds_limit(bundle):
    limit = bundle.get(K_BUDGET, {}).get(B_ROUNDS, {}).get(B_LIMIT)
    assert type(limit) is int and limit >= 0, f"`{K_BUDGET}.{B_ROUNDS}.{B_LIMIT}` is not a number of rounds: {bundle.get(K_BUDGET)!r}"
    return limit


def gap_names(bundle):
    """Everything a gap names: its id and its path."""
    return {gap.get(key) for gap in bundle[K_GAPS] for key in ("id", "path")} - {None}


def dropped(bundle):
    """``path -> reason`` of what the authority filter dropped."""
    entries = bundle[K_MERGE].get(M_DROPPED)
    assert isinstance(entries, list), f"`{K_MERGE}.{M_DROPPED}` is not a list: {bundle[K_MERGE]!r}"
    return {entry.get("path"): entry.get("reason") for entry in entries}


def follow(api, root, query, first, limit=40, **kwargs):
    """``first`` and every bundle its continuation leads to, asked with the same arguments."""
    bundles = [first]
    while bundles[-1][K_CONTINUATION] is not None:
        assert len(bundles) < limit, f"the continuation did not end after {limit} bundles"
        bundles.append(check_bundle(api.retrieve(root, query, continuation=bundles[-1][K_CONTINUATION], **kwargs)))
    return bundles


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------

BASE_DATE = "2026-09-01T12:00:00+00:00"
LATER = "2026-09-02T12:00:00+00:00"


def git(project, *args, date=BASE_DATE):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(project), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "W1-21 tests", "GIT_AUTHOR_EMAIL": "w1-21@example.invalid",
           "GIT_COMMITTER_NAME": "W1-21 tests", "GIT_COMMITTER_EMAIL": "w1-21@example.invalid",
           "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel


def commit(project, message="a change", date=LATER):
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message, date=date)


def clone(source, destination):
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(source), str(destination)], check=True,
                   capture_output=True)
    return Path(destination)


def tree(project):
    """``path -> sha256`` of every file under ``project``, git's own files left out."""
    project = Path(project)
    return {path.relative_to(project).as_posix(): sha256(path.read_bytes())
            for path in sorted(project.rglob("*")) if path.is_file() and ".git" not in path.relative_to(project).parts}


# --------------------------------------------------------------------------
# The fixture project
# --------------------------------------------------------------------------

EMBEDDED, NOT_EMBEDDED = "embedded", "not embedded"
_NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history", "export_policy": "allowed",
    "provenance": "written by the W1-21 tests", "deletion_rebuild": "authoritative; restored from git only",
}
# ``name -> (patterns, embedding_policy)``. Only ``docs/`` and ``app/`` reach the vectors, so the semantic route
# returns few chunks and a file elsewhere is found by the exact string alone.
NAMESPACES = {
    "top": (["*"], NOT_EMBEDDED),
    "overlay": (["governance/**"], NOT_EMBEDDED),
    "paging": (["paging/**"], NOT_EMBEDDED),
    "manual": (["manual/**"], NOT_EMBEDDED),
    "records": (["records/**"], NOT_EMBEDDED),
    "docs": (["docs/**"], EMBEDDED),
    "app": (["app/**"], EMBEDDED),
}


def adopt(project, namespaces):
    """Give ``project`` a path map and the kernel's gitleaks configuration (the two files the secret filter reads)."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document["namespaces"] = {name: {"paths": list(patterns), "memory_class": "governance", **_NAMESPACE_FIELDS,
                                     "embedding_policy": policy} for name, (patterns, policy) in namespaces.items()}
    write(project, PATH_MAP_REL, yaml.safe_dump(document, sort_keys=False))
    shutil.copy2(REPO_ROOT / TEMPLATE_CONFIG_REL, Path(project) / CONFIG_REL)


def record(record_id, kind, status, body, **more):
    """A record file: frontmatter with ``id``, ``type`` and ``status`` (DEC-239), then a body. ``kind=None``
    leaves ``type`` out, which the store's load reports as invalid (DEC-274)."""
    front = {"id": record_id, **({"type": kind} if kind else {}), "status": status, "state_class": "AUTHORITATIVE",
             **more}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {record_id}\n\n{body}\n"


# ---- paging: seven files hold one exact phrase, each in one chunk; no vector is made of them
PHRASE = "amber lantern protocol"
PAGING = [f"paging/p{number}.md" for number in range(1, 8)]
FAVOURED = "quartz"            # the stand-in reranker scores a text by how often it holds the favoured words
FAVOURED_PAGE = PAGING[4]      # the fifth file by path: no route returns it in its first batch of three

# ---- dedup: one chunk, found by both routes; the phrase stands on two of its lines
DEDUP_PHRASE = "sourdough proofing ledger"
BAKERY, TIDES = "docs/bakery.md", "docs/tides.md"

# ---- parent expansion (DEC-091, DEC-343): a long section and a long function, each of several chunks
EXPANSION_PHRASE = "obsidian valve interlock"
MANUAL = "manual/manual.md"
MANUAL_HEADING = "## Recovery"
CODE_PHRASE = "garnet sluice checkpoint"
POOL = "app/pool.py"
POOL_FUNCTION = "def drain(pool):"

# ---- the authority filter: every decision below holds the phrase, so the exact-string route returns them all
AUTHORITY_PHRASE = "cobalt ledger rule"
MUST_NOT_CITE_STATUS = "DEPRECATED"   # package DP-4: what marks a record must-not-cite
MUST_NOT_CITE_STATUSES = ("DEPRECATED", "REJECTED", "WITHDRAWN")  # DEC-423: the closed status list
DECISIONS = "records/decisions/"
CURRENT = [DECISIONS + "adr-0010.md", DECISIONS + "adr-0012.md"]
# ``path -> why it is not current``; the store reads each of these from the frontmatter (DEC-329, G-19).
SUPERSEDED = {
    DECISIONS + "adr-0003.md": "its own status says ACCEPTED and ADR-0010 lists it under `supersedes`",
    DECISIONS + "adr-0004.md": "its status is SUPERSEDED",
    DECISIONS + "adr-0005.md": "it names its successor under `superseded_by`, and no record has that id",
}
MUST_NOT_CITE = DECISIONS + "adr-0006.md"
MUST_NOT_CITE_REJECTED = DECISIONS + "adr-0008.md"   # DEC-423: status REJECTED
MUST_NOT_CITE_WITHDRAWN = DECISIONS + "adr-0009.md"  # DEC-423: status WITHDRAWN
UNTYPED_SUPERSEDED = DECISIONS + "adr-0007.md"   # status SUPERSEDED and no `type`: not a record of the store
# ---- the same by the semantic route: two decisions that reach the vectors
SEMANTIC_SUPERSEDED, SEMANTIC_CURRENT = "docs/decisions/adr-0020.md", "docs/decisions/adr-0021.md"
SEMANTIC_QUESTION = "which register lists every folded sail of the loft"

# ---- failure memory (CAP-14.a, CAP-41): records joined to a ticket by a typed edge (package DP-5)
TICKET_IN_SCOPE, TICKET_OUT_OF_SCOPE = "RT-0001", "RT-0002"
FAILURE = "records/failures/fail-0001.md"
LESSON = "records/lessons/l-0001.md"
SUPERSEDED_LESSON = "records/lessons/l-0002.md"
AHEAD_TYPES = ("failure", "lesson")
# ---- closure (DEC-033): a chain of decisions behind a ticket, and a ticket that names nothing
TICKET_CHAIN, TICKET_DANGLING, DANGLING_ID = "RT-0003", "RT-0004", "GONE-0404"
CHAIN = [DECISIONS + f"adr-003{number}.md" for number in range(3)]   # ADR-0030 <- ADR-0031 <- ADR-0032
NO_SUCH_TEXT = "zzyzx plover xyzzy"   # no line of the fixture holds it


def _manual():
    lines = ["# Manual", "", "## Starting", "", "Open the gate and start the scheduler.", "", MANUAL_HEADING, ""]
    for step in range(1, 91):
        note = f" The {EXPANSION_PHRASE} is tested here." if step == 45 else ""
        lines.append(f"Step {step:02d} of the recovery: read valve {step:02d} and log the reading in the plant book.{note}")
    lines += ["", "## Closing", "", "Close the gate."]
    return "\n".join(lines) + "\n"


def _pool():
    lines = ['"""Connection pool."""', "", "", "def refill(pool):", '    """Top the pool up."""', "    return pool",
             "", "", POOL_FUNCTION, '    """Empty the pool and close every connection."""']
    for slot in range(1, 41):
        if slot == 25:
            lines.append(f"    # {CODE_PHRASE}")
        lines.append(f"    pool.release(slot_{slot:02d})  # free slot {slot:02d} before the sweep goes on")
    lines += ["    return []", "", "", "LIMIT = 40"]
    return "\n".join(lines) + "\n"


def _long(text, lines=30):
    """A body long enough for several chunks, with ``text`` as its last line."""
    return "\n".join(f"Paragraph {number:02d} of the background, kept for the record of the decision." * 2
                     for number in range(1, lines + 1)) + "\n\n" + text


def corpus():
    rule = f"The {AUTHORITY_PHRASE} applies to every sealed crate."
    files = {
        "README.md": "# A project\n\nOrdinary text about the project.\n",
        ".gitignore": ".gov-runtime/\n",
        BAKERY: f"# Bakery\n\nThe {DEDUP_PHRASE} is kept by the night shift.\n"
                f"Every loaf is entered in the {DEDUP_PHRASE} before dawn.\n",
        TIDES: "# Tides\n\nThe harbour pilot reads the tide tables at dawn.\n",
        MANUAL: _manual(),
        POOL: _pool(),
        CURRENT[0]: record("ADR-0010", "decision", "ACCEPTED", rule, supersedes=["ADR-0003"]),
        CURRENT[1]: record("ADR-0012", "decision", "ACCEPTED", rule),
        DECISIONS + "adr-0003.md": record("ADR-0003", "decision", "ACCEPTED", rule),
        DECISIONS + "adr-0004.md": record("ADR-0004", "decision", "SUPERSEDED", _long(rule)),
        DECISIONS + "adr-0005.md": record("ADR-0005", "decision", "ACCEPTED", rule, superseded_by="ADR-0011"),
        MUST_NOT_CITE: record("ADR-0006", "decision", MUST_NOT_CITE_STATUS, rule),
        MUST_NOT_CITE_REJECTED: record("ADR-0008", "decision", "REJECTED", rule),
        MUST_NOT_CITE_WITHDRAWN: record("ADR-0009", "decision", "WITHDRAWN", rule),
        UNTYPED_SUPERSEDED: record("ADR-0007", None, "SUPERSEDED", rule),
        SEMANTIC_SUPERSEDED: record("ADR-0020", "decision", "SUPERSEDED",
                                    "The saffron register lists every folded sail of the loft."),
        SEMANTIC_CURRENT: record("ADR-0021", "decision", "ACCEPTED",
                                 "The indigo register lists every folded sail of the loft.", supersedes=["ADR-0020"]),
        "records/tickets/rt-0001.md": record(TICKET_IN_SCOPE, "ticket", "open", "Rework the pool sweep.",
                                             implements=["ADR-0010"]),
        "records/tickets/rt-0002.md": record(TICKET_OUT_OF_SCOPE, "ticket", "open", "Repaint the harbour office."),
        "records/tickets/rt-0003.md": record(TICKET_CHAIN, "ticket", "open", "Survey the breakwater.",
                                             depends_on=["ADR-0030"]),
        "records/tickets/rt-0004.md": record(TICKET_DANGLING, "ticket", "open", "Chart the outer shoal.",
                                             depends_on=[DANGLING_ID]),
        FAILURE: record("FAIL-0001", "failure", "ACTIVE", "Sweeping the slots in parallel lost two connections.",
                        constrains=[TICKET_IN_SCOPE]),
        LESSON: record("L-0001", "lesson", "ACTIVE", "Release one slot at a time and log each release.",
                       lifecycle="approved", scope="project", severity="high", constrains=[TICKET_IN_SCOPE]),
        SUPERSEDED_LESSON: record("L-0002", "lesson", "SUPERSEDED", "Release every slot at once.",
                                  lifecycle="approved", scope="project", severity="low",
                                  constrains=[TICKET_IN_SCOPE]),
        CHAIN[0]: record("ADR-0030", "decision", "ACCEPTED", "The breakwater is surveyed each spring.",
                         depends_on=["ADR-0031"]),
        CHAIN[1]: record("ADR-0031", "decision", "ACCEPTED", "Surveys use the tidal datum of the port.",
                         depends_on=["ADR-0032"]),
        CHAIN[2]: record("ADR-0032", "decision", "ACCEPTED", "The tidal datum is set by the harbour board."),
    }
    for number, rel in enumerate(PAGING, 1):
        extra = f" The {FAVOURED} seam, the {FAVOURED} vein." if rel == FAVOURED_PAGE else ""
        files[rel] = f"# Paging {number}\n\nThe {PHRASE} is logged at station {number}.{extra}\n"
    return files


def build_fixture(project):
    """The fixture repository: one commit holding the corpus, the path map and the rules. Not indexed."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    adopt(project, NAMESPACES)
    for rel, text in corpus().items():
        write(project, rel, text)
    commit(project, "the fixture", BASE_DATE)
    return project


def record_type(root, rel):
    """The ``type`` of the record file ``rel``, None when the file is no record."""
    text = (Path(root) / rel).read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return None
    front = yaml.safe_load(text[4:text.index("\n---\n", 4)])
    return front.get("type") if isinstance(front, dict) and "id" in front else None


# --------------------------------------------------------------------------
# The stand-in Ollama endpoint: the HTTP interface of the daemon, with vectors computed from words
# --------------------------------------------------------------------------

DIMENSIONS = 1024
_STOP = {"the", "and", "for", "with", "that", "this", "each", "does", "when", "who", "what", "into", "from", "its",
         "are", "was", "has", "have", "before", "after", "then", "any", "all", "given", "query", "instruct",
         "retrieve", "relevant", "passages", "search", "web", "answer", "which", "every"}


def stand_in_vector(text):
    """A unit vector made of the words of ``text``: texts that share words are near each other."""
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"[a-z0-9]+", str(text).lower()):
        if len(word) >= 3 and word not in _STOP:
            digest = hashlib.sha256(word.encode()).digest()
            vector[int.from_bytes(digest[:4], "big") % DIMENSIONS] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        vector[0], norm = 1.0, 1.0
    return [value / norm for value in vector]


class OllamaStandIn:
    """A healthy Ollama endpoint on a free loopback port: the version, the model list and the embeddings."""

    def __init__(self):
        model = {"name": EMBED_MODEL, "model": EMBED_MODEL, "digest": "ac6da0dfba84" + "0" * 52}

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                try:
                    asked = json.loads(self.rfile.read(length) or b"{}") if length else {}
                except ValueError:
                    asked = {}
                route, reply, status = self.path.split("?")[0].rstrip("/"), {}, 200
                if route == "/api/version":
                    reply = {"version": "0.35.0"}
                elif route == "/api/tags":
                    reply = {"models": [model]}
                elif route == "/api/embed":
                    given = asked.get("input", "")
                    texts = [given] if isinstance(given, str) else list(given)
                    reply = {"model": EMBED_MODEL, "embeddings": [stand_in_vector(text) for text in texts]}
                else:
                    status = 404
                payload = json.dumps(reply).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = do_HEAD = answer

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.host = f"127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


# --------------------------------------------------------------------------
# The family check
# --------------------------------------------------------------------------

def family_check(api):
    """The one check of the retrieval-regression family that ``gov check --list --json`` lists for this
    repository (DEC-186: a declaration under the kernel template registers a check)."""
    if not sorted((REPO_ROOT / CHECKS_REL).glob(CHECK_GLOB)):
        raise Missing(f"the retrieval-regression check is not registered: nothing matches {CHECKS_REL}/{CHECK_GLOB}")
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


def run_check(check, project, env):
    """Run the declared command as DEC-285 states: by ``sh -c``, in the project's root; exit 0 is green."""
    done = subprocess.run(check["command"], shell=True, cwd=str(project), env=env, capture_output=True, text=True,
                          timeout=MEASURE_TIMEOUT_S, stdin=subprocess.DEVNULL)
    return Run((check["command"],), done)


# --------------------------------------------------------------------------
# The dev tiers and the dev query set
# --------------------------------------------------------------------------

# RETR-A-04 (scenarios/a-dev.yaml of the dev tiers): the question, and the two files that must be found and cited.
RETR_A_04_QUESTION = "Which files implement the leapfrog integrator?"
RETR_A_04_EXPECTED = ("crates/orion-runtime/src/integrators.rs", "python/orion_ref/integrators.py")
# RETR-X-02 (scenarios/x-dev.yaml): a record that exists in neither programme, and a question whose answer
# spans three locations. The scenario names no question, so the cases take every dev query whose gold answer
# names three or more `must_cite` paths.
RETR_X_02_MISSING_ID = "DEC-9999"
RETR_X_02_LOCATIONS = 3


def clone_tier(name, destination):
    """A clone of a dev tier in a temporary directory, adopted with a map that classes all of it as embedded
    governance memory; None when this machine has no such tier."""
    tier = DEV_TIERS / name
    if not (tier / ".git").exists():
        return None
    root = clone(tier, destination)
    with open(root / ".git" / "info" / "exclude", "a", encoding="utf-8") as exclude:
        exclude.write("\n.gov-runtime/\n")
    adopt(root, {"everything": (["**"], EMBEDDED)})
    commit(root, "adopted by the W1-21 tests")
    return root


def dev_queries():
    if not QUERY_SET.is_file():
        return None
    return yaml.safe_load(QUERY_SET.read_text(encoding="utf-8"))["queries"]


def first_paths(bundle, depth=5):
    """The first ``depth`` distinct paths the bundle cites (S0b2: "top-5 distinct paths per query")."""
    return paths(bundle)[:depth]


def mean_hit_at_5(scored):
    """``class -> [bool, ...]``: the mean of the classes' percentages (S0b2: "Mean of ten classes", DEC-388)."""
    per_class = {name: 100.0 * sum(hits) / len(hits) for name, hits in scored.items()}
    return sum(per_class.values()) / len(per_class), {name: round(value, 1) for name, value in per_class.items()}


MEASURED = []  # what the dev-tier measurement found, shown in the terminal summary whether it passes or fails
