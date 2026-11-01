"""Support code for the W2-13 acceptance tests (standard library and PyYAML only; not a test module).

W2-13 makes the lexical route a ranked one (BM25 over SQLite FTS5, with fields for id, title and body, the exact
string kept as a boost), hands its ranked list to the fusion, makes lexical search answer "unavailable" instead of
raising, and makes a question about an id that exists nowhere a stated gap (RETR-X-02, DEC-900). The tests reach it
only through public interfaces:

- the commands ``gov rebuild --json`` and ``gov retrieve "<question>" --json`` (the API-0002 envelope);
- ``gov.retrieval.lexical.search(root, query, refresh=...)`` and ``chunks`` and ``parent`` (W1-17's interface);
- ``gov.retrieval.fusion.search(root, query, limit, refresh=..., reranker=...)`` (W1-19's interface);
- the store file ``.gov-runtime/store.db``, read as an SQLite file only (which tables exist, what their rows hold).

How the tests reach the code under test (DEC-732):

- This module imports ``gov`` from whatever ``PYTHONPATH`` the run gives; nothing is hard-coded.
- Every child process gets, first on its ``PYTHONPATH``, the folder that this run's ``gov`` was imported from, then
  the run's own ``PYTHONPATH``; each driver call reports the ``gov`` it imported, and the cases check it.

Every project is a temporary git repository built from scratch, with its own path map, its own ``.gitleaks.toml``
and its own ``.gov-runtime/``. The scratch environment of a child is built from nothing: an empty ``HOME`` (so the
default reranker is absent, DEC-374), a ``PATH`` holding only ``git``, ``gitleaks`` and ``python3`` (so the code
tool is absent and the code graph is not built), ``OLLAMA_HOST`` and ``GOV_QUERY_OLLAMA_HOST`` at a stand-in
endpoint on a loopback port (or at a dead port), the run's own rebuild lock (DEC-956 item 2) and a secrets cache of
the case's own (W2-107's cache stays on, as ``gov rebuild`` uses it). No model runs outside the cases marked
``needs("ollama", "reranker")``.

The planted secret is joined at run time from parts: no file of this suite holds it whole (DEC-911).
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
import sqlite3
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

import gov

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
GOV_SRC = str(Path(gov.__file__).resolve().parents[1])  # the folder the run's ``gov`` comes from (DEC-732)
GOV_FILE = str(Path(gov.__file__).resolve())

LEXICAL, FUSION = "gov.retrieval.lexical", "gov.retrieval.fusion"
FACET = "lexical"
UNAVAILABLE = "FACET_UNAVAILABLE"
STORE_REL = ".gov-runtime/store.db"
RUNTIME_REL = ".gov-runtime"
PATH_MAP_REL = "governance/project/path-map.yaml"
CONFIG_REL = ".gitleaks.toml"
TEMPLATE_CONFIG_REL = "template/.gitleaks.toml"
CALL_TIMEOUT_S = 300.0
MEASURE_TIMEOUT_S = 3600.0

# ---- the bundle (W1-21's interface)
K_REASON, K_EVIDENCE, K_BATCHES, K_MERGE, K_EXPANSIONS = "stopping_reason", "evidence", "batches", "merge", "expansions"
K_GAPS, K_FACETS, K_BUDGET, K_CONTINUATION = "gaps", "facets", "budget", "continuation"
BUNDLE_KEYS = (K_REASON, K_EVIDENCE, K_BATCHES, K_MERGE, K_EXPANSIONS, K_GAPS, K_FACETS, K_BUDGET, K_CONTINUATION)
ITEM_KEYS = ("id", "sha256", "path", "start_line", "end_line", "text", "chunk_id", "routes", "batch")
EXPANSION_KEYS = ("chunk_id", "parent_id", "path", "start_line", "end_line")
REASONS = ("CLOSURE_COMPLETE", "SATURATED", "DEPTH_LIMIT_REACHED", "BUDGET_EXHAUSTED_WITH_GAPS", "FACET_UNAVAILABLE",
           "UNRESOLVED_IDS")
COMPLETE, SATURATED, DEPTH_LIMIT, BUDGET_EXHAUSTED, FACET_UNAVAILABLE, UNRESOLVED_IDS = REASONS
# A stated gap never says that nothing is left, nor that the budget ran out (W2-M296, DEC-900).
NOT_A_STATED_GAP = (COMPLETE, SATURATED, BUDGET_EXHAUSTED)
# The reasons that name a gap for an id no record and no file has (W1-21's case; W2-M098 is a package).
STATED_GAP = (UNRESOLVED_IDS, FACET_UNAVAILABLE)
ROUTE_LEXICAL, ROUTE_SEMANTIC = "lexical", "semantic"
BUDGET_LARGE = 1_000_000
BATCH_LARGE = 200

EMBED_MODEL = "qwen3-embedding:0.6b"
RERANK_MODEL = "Qwen/Qwen3-Reranker-0.6B"
RERANK_REVISION = "e61197ed45024b0ed8a2d74b80b4d909f1255473"
RERANK_PYTHON_REL = ".local/share/gov-os/reranker-venv/bin/python"
WARM_P95_LIMIT_S = 0.5  # W1-19's warm-query budget (success 2 of W1-19), the retrieve budget this ticket keeps

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS") or "~/gov-os-workbench/synthetic").expanduser()
QUERY_SET = DEV_TIERS / "dev-queryset.yaml"
TIERS = {"A": "a-dev", "B": "b-dev"}
WARM_UP_QUESTIONS = ("how is the configuration loaded", "where are errors logged", "which tests cover the parser")
# RETR-A-04 (scenarios/a-dev.yaml), as W1-21 and the Wave 1 exit run ask it (EXIT-REPORT.md, "Retrieval").
RETR_A_04_QUESTION = "Which files implement the leapfrog integrator?"
RETR_A_04_EXPECTED = ("crates/orion-runtime/src/integrators.rs", "python/orion_ref/integrators.py")
RETR_A_04_EXPANSIONS = 3
MISSING_ID = "DEC-9999"  # RETR-X-02's id: no record and no file of the fixture or of a dev tier holds it


class Missing(AssertionError):
    """Something the ticket builds does not exist."""


# --------------------------------------------------------------------------
# The driver: Python calls in a child process, each call's value or the type of what it raised
# --------------------------------------------------------------------------

_DRIVER = r'''
import importlib, json, sys, time
from pathlib import Path

request = json.loads(sys.stdin.read())
LOG = {"loads": 0, "passes": 0}


def loader():
    """A stand-in reranker's loader: it scores a text by how often it holds the favoured words."""
    LOG["loads"] += 1
    favour = [word.lower() for word in request["favour"]]

    def score(query, texts):
        LOG["passes"] += 1
        return [float(sum(str(text).lower().count(word) for word in favour)) for text in texts]

    return score


def decode(value):
    if isinstance(value, dict) and set(value) == {"$path"}:
        return Path(value["$path"])
    if value == "$reranker":
        return loader
    if value == "$absent":
        return lambda: None
    return value


import gov
out = {"gov": gov.__file__, "calls": []}
for call in request["calls"]:
    record = {"value": None, "error": None, "seconds": None}
    try:
        function = getattr(importlib.import_module(call["module"]), call["function"])
        started = time.perf_counter()
        record["value"] = function(*[decode(arg) for arg in call["args"]],
                                   **{key: decode(value) for key, value in call["kwargs"].items()})
        record["seconds"] = time.perf_counter() - started
    except Exception as exc:  # reported, so a case can say "never raises"
        record["error"] = {"type": type(exc).__name__, "message": str(exc)[:400], "code": getattr(exc, "code", None)}
    out["calls"].append(record)
out["reranker"] = LOG
print("\n" + json.dumps(out, default=repr))
'''


def path_arg(path):
    return {"$path": str(path)}


RERANKER, ABSENT_RERANKER = "$reranker", "$absent"


class Outcome:
    """What one driver process reported."""

    def __init__(self, data, stderr):
        self.calls, self.stderr, self.gov = data["calls"], stderr, data["gov"]
        self.loads, self.passes = data["reranker"]["loads"], data["reranker"]["passes"]

    def error(self, index=0):
        return self.calls[index]["error"]

    def value(self, index=0):
        call = self.calls[index]
        assert call["error"] is None, \
            f"call {index} raised {call['error']['type']}: {call['error']['message']}\n{self.stderr[-1500:]}"
        return call["value"]

    def seconds(self, index=0):
        return self.calls[index]["seconds"]


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class Run:
    """One ``gov`` command: its exit code and output."""

    def __init__(self, argv, done):
        self.argv, self.returncode, self.stdout, self.stderr = argv, done.returncode, done.stdout, done.stderr

    def describe(self):
        return f"{' '.join(self.argv)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-3000:]}\n" \
               f"stderr:\n{self.stderr[-3000:]}"

    def envelope(self):
        try:
            envelope = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"standard output is not one JSON envelope\n{self.describe()}") from None
        assert isinstance(envelope, dict), self.describe()
        return envelope

    def result(self):
        """The envelope's result of a call that succeeded."""
        assert self.returncode == 0, f"the command did not succeed\n{self.describe()}"
        envelope = self.envelope()
        assert envelope.get("ok") is True and isinstance(envelope.get("result"), dict), self.describe()
        return envelope["result"]


class Box:
    """The places and environments of the child processes; it needs nothing of the ticket."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "elsewhere", "site", "bin"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        # The scratch PATH: git, gitleaks and this interpreter, nothing else (so the code tool is absent).
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
        self.lock = os.environ.get("GOV_REBUILD_LOCK") or str(self.workdir / "rebuild.lock")
        self.cache = str(self.workdir / "secrets-cache" / "secrets-scan.sqlite")
        Path(self.cache).parent.mkdir(exist_ok=True)

    def _link_sqlite_vec(self):
        """A folder that links the one package ``sqlite_vec`` this machine's Python imports: the empty HOME has no
        user site folder to find it in. None when the machine has none."""
        spec = importlib.util.find_spec("sqlite_vec")
        if spec is None or not spec.origin:
            return None
        origin = Path(spec.origin)
        source = origin.parent if spec.submodule_search_locations else origin
        link = self.workdir / "site" / source.name
        if not link.is_symlink():
            link.symlink_to(source, target_is_directory=source.is_dir())
        return self.workdir / "site"

    def python_path(self, *extra):
        """The run's ``gov`` first, then the run's own ``PYTHONPATH``, then ``extra``."""
        return os.pathsep.join(filter(None, [GOV_SRC, os.environ.get("PYTHONPATH"), *map(str, extra)]))

    def scratch_env(self, ollama_host=None, **extra):
        """Built from nothing: no reranker environment, no code tool, an endpoint that is dead unless given."""
        host = ollama_host or self.dead_host
        return {
            "PATH": str(self.workdir / "bin"),
            "HOME": str(self.workdir / "home"),
            "TMPDIR": str(self.workdir / "tmp"),
            "XDG_RUNTIME_DIR": str(self.workdir / "tmp"),
            "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": self.python_path(*([self.site] if self.site else [])),
            "PYTHONDONTWRITEBYTECODE": "1",
            "OLLAMA_HOST": host,
            "GOV_QUERY_OLLAMA_HOST": host,
            "GOV_REBUILD_LOCK": self.lock,
            "GOV_SECRETS_CACHE": self.cache,
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            **extra,
        }

    def real_env(self):
        """This machine's own environment, for the cases that need the models; nothing may be downloaded."""
        env = {key: value for key, value in os.environ.items() if key not in ("GOV_ROLE", "GOV_TICKET")}
        env.update({"PYTHONPATH": self.python_path(), "PYTHONDONTWRITEBYTECODE": "1", "HF_HUB_OFFLINE": "1",
                    "TRANSFORMERS_OFFLINE": "1", "GIT_CONFIG_NOSYSTEM": "1", "GOV_REBUILD_LOCK": self.lock,
                    "GOV_SECRETS_CACHE": self.cache})
        return env

    # ---- Python calls

    def run(self, calls, *, env=None, favour=(), timeout=CALL_TIMEOUT_S):
        """Run ``[(module, function, args, kwargs), ...]`` in one process and return its :class:`Outcome`."""
        request = {"favour": list(favour),
                   "calls": [{"module": module, "function": function, "args": list(args), "kwargs": dict(kwargs)}
                             for module, function, args, kwargs in calls]}
        what = ", ".join(dict.fromkeys(f"{module}.{function}" for module, function, *_ in calls))
        try:
            done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request),
                                  env=self.scratch_env() if env is None else env,
                                  cwd=str(self.workdir / "elsewhere"), capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {timeout:.0f} s") from None
        assert done.returncode == 0, f"{what}: the child process failed (exit code {done.returncode}):\n" \
                                     f"{done.stderr[-3000:]}"
        try:
            data = json.loads(done.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            raise AssertionError(f"{what} did not return JSON values:\n{done.stdout[-2000:]}\n{done.stderr[-2000:]}") \
                from None
        assert Path(data["gov"]).resolve() == Path(GOV_FILE), \
            f"the child ran another gov ({data['gov']}) than the run's ({GOV_FILE}) (DEC-732)"
        return Outcome(data, done.stderr)

    def search(self, root, query, refresh=False, env=None):
        """``lexical.search(root, query, refresh=...)``: the answer, its form checked; it must not raise."""
        outcome = self.run([(LEXICAL, "search", [path_arg(root), query], {"refresh": refresh})], env=env)
        error = outcome.error()
        assert error is None, f"lexical search raised {error['type']} for {query!r}: {error['message']}"
        return check_answer(outcome.value(), query)

    def searches(self, root, queries, refresh=False, env=None):
        """``query -> answer`` or ``query -> {"raised": type}``, all in one process."""
        outcome = self.run([(LEXICAL, "search", [path_arg(root), query], {"refresh": refresh}) for query in queries],
                           env=env)
        found = {}
        for index, query in enumerate(queries):
            error = outcome.error(index)
            found[query] = {"raised": error["type"], "message": error["message"]} if error else outcome.value(index)
        return found

    # ---- the commands

    def gov(self, *args, host=None, env=None, timeout=CALL_TIMEOUT_S):
        try:
            done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args], capture_output=True, text=True,
                                  cwd=str(self.workdir / "elsewhere"), env=env or self.scratch_env(host),
                                  timeout=timeout, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"gov {' '.join(args)} did not end within {timeout:.0f} s") from None
        return Run(("gov", *args), done)

    def rebuild(self, root, host=None, env=None, timeout=MEASURE_TIMEOUT_S):
        """``gov rebuild --json --root <root>``: the result, which must say the lexical index was recreated."""
        result = self.gov("rebuild", "--json", "--root", str(root), host=host, env=env, timeout=timeout).result()
        lexical = result.get("stores", {}).get("lexical", {})
        assert lexical.get("status") == "recreated", f"gov rebuild did not recreate the lexical index: {result!r}"
        return result

    def retrieve(self, root, question, *args, host=None, env=None, timeout=CALL_TIMEOUT_S):
        """``gov retrieve --json --root <root> <args> <question>``: the command's run."""
        return self.gov("retrieve", "--json", "--root", str(root), *args, question, host=host, env=env,
                        timeout=timeout)


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
    if shutil.which("git") is None:
        lacking["git"] = "git is not on PATH on this machine"
    return lacking


NEEDS = _needs()


def lacking(*names):
    return [NEEDS[name] for name in names if name in NEEDS]


# --------------------------------------------------------------------------
# The lexical answer and the bundle
# --------------------------------------------------------------------------

def check_answer(answer, query):
    """The form of a ``search`` answer (W1-17's README): an unavailable facet says so, with a reason, and no hit."""
    assert isinstance(answer, dict), f"search did not return a map for {query!r}: {answer!r}"
    assert isinstance(answer.get("available"), bool), f"search's `available` is not true or false: {answer!r}"
    assert answer.get("facet") == FACET, f"search's `facet` is not {FACET!r}: {answer!r}"
    hits = answer.get("hits")
    assert isinstance(hits, list), f"search's `hits` is not a list: {answer!r}"
    if not answer["available"]:
        assert answer.get("state") == UNAVAILABLE, f"an unavailable facet does not say {UNAVAILABLE}: {answer!r}"
        assert isinstance(answer.get("reason"), str) and answer["reason"], f"no reason is given: {answer!r}"
        assert hits == [], f"an unavailable facet returned hits for {query!r}: {answer!r}"
        return answer
    assert answer.get("state") != UNAVAILABLE, f"an available facet says {UNAVAILABLE}: {answer!r}"
    for hit in hits:
        assert isinstance(hit, dict), f"a hit is not a map: {hit!r}"
        assert isinstance(hit.get("path"), str) and hit["path"], f"a hit has no file path: {hit!r}"
        assert isinstance(hit.get("line"), int) and hit["line"] >= 1, f"a hit has no line number: {hit!r}"
        assert isinstance(hit.get("text"), str), f"a hit has no text: {hit!r}"
        for key in ("chunk_id", "parent_id"):
            assert isinstance(hit.get(key), str) and hit[key], f"a hit has no {key}: {hit!r}"
    return answer


def ranked_paths(answer):
    """The paths of the hits, each once, in the order the route ranks them (its first hit in each file)."""
    assert answer["available"], f"the lexical facet is unavailable: {answer!r}"
    return list(dict.fromkeys(hit["path"] for hit in answer["hits"]))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_citation(root, item):
    """An evidence item cites bytes that exist: its sha256 is that of the cited file or of the cited lines, and its
    text is in those lines (CAP-55.a, as W1-21 checks it)."""
    source = Path(root) / item["path"]
    assert source.is_file(), f"an evidence item cites a file that does not exist: {item!r}"
    lines = source.read_bytes().splitlines(keepends=True)
    start, end = item["start_line"], item["end_line"]
    assert 1 <= start <= end <= len(lines), f"the cited lines are not in the file ({len(lines)} lines): {item!r}"
    span = b"".join(lines[start - 1:end])
    assert item["sha256"] in (sha256(source.read_bytes()), sha256(span)), \
        f"the sha256 is neither that of {item['path']} nor that of its lines {start}-{end}"
    assert item["text"].strip() in span.decode("utf-8", "replace"), \
        f"the cited text is not in lines {start}-{end} of {item['path']}: {item['text'][:200]!r}"


def check_bundle(bundle, root=None):
    """The bundle's form (W1-21's interface, unchanged by this ticket: failure 1)."""
    assert isinstance(bundle, dict), f"the bundle is not a map: {bundle!r}"
    missing = [key for key in BUNDLE_KEYS if key not in bundle]
    assert not missing, f"the bundle lacks {missing}: {sorted(bundle)}"
    assert bundle[K_REASON] in REASONS, f"the stopping reason {bundle[K_REASON]!r} is not in the fixed list"
    assert isinstance(bundle[K_EVIDENCE], list), f"`evidence` is not a list: {bundle!r}"
    for item in bundle[K_EVIDENCE]:
        assert isinstance(item, dict) and all(key in item for key in ITEM_KEYS), \
            f"an evidence item lacks one of {ITEM_KEYS}: {item!r}"
        assert re.fullmatch(r"[0-9a-f]{64}", str(item["sha256"])), f"an evidence item has no sha256: {item!r}"
        assert isinstance(item["routes"], list) and item["routes"], f"an evidence item names no route: {item!r}"
        if root is not None:
            check_citation(root, item)
    chunks = [item["chunk_id"] for item in bundle[K_EVIDENCE]]
    assert len(set(chunks)) == len(chunks), "a chunk is cited twice"
    assert isinstance(bundle[K_GAPS], list) and all(isinstance(gap, dict) and gap.get("reason")
                                                    for gap in bundle[K_GAPS]), f"`gaps` is not a list of gaps"
    assert isinstance(bundle[K_EXPANSIONS], list), "`expansions` is not a list"
    for entry in bundle[K_EXPANSIONS]:
        assert isinstance(entry, dict) and all(key in entry for key in EXPANSION_KEYS), \
            f"an expansion lacks one of {EXPANSION_KEYS}: {entry!r}"
    facets = bundle[K_FACETS]
    for facet in (ROUTE_LEXICAL, ROUTE_SEMANTIC):
        assert isinstance(facets.get(facet), dict) and isinstance(facets[facet].get("available"), bool), \
            f"`facets` does not report the state of the {facet} route: {facets!r}"
    if bundle[K_REASON] == FACET_UNAVAILABLE:
        assert any(isinstance(state, dict) and state.get("available") is False for state in facets.values()), \
            f"the bundle says {FACET_UNAVAILABLE} and every facet it reports is available: {facets!r}"
    return bundle


def cited_paths(bundle):
    return list(dict.fromkeys(item["path"] for item in bundle[K_EVIDENCE]))


def gap_names(bundle):
    """Everything a gap names: its id and its path."""
    return {gap.get(key) for gap in bundle[K_GAPS] for key in ("id", "path")} - {None}


def no_traceback(run):
    """A command answers an envelope (a bundle, or ``ok: false`` with a governance error), never a traceback."""
    assert "Traceback (most recent call last)" not in run.stderr + run.stdout, f"a traceback:\n{run.describe()}"
    assert run.returncode in (0, 1), f"the command did not answer a bundle or a governance error\n{run.describe()}"
    envelope = run.envelope()
    if run.returncode == 0:
        assert envelope.get("ok") is True, run.describe()
        return check_bundle(envelope["result"])
    assert envelope.get("ok") is False and isinstance(envelope.get("error"), dict) and envelope["error"].get("code"), \
        f"exit 1 without a governance error and its code\n{run.describe()}"
    return None


def p95(seconds):
    """The 95th percentile by the nearest-rank rule (as W1-19 takes it)."""
    ordered = sorted(seconds)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


# --------------------------------------------------------------------------
# git and files
# --------------------------------------------------------------------------

BASE_DATE = "2026-11-01T12:00:00+00:00"


def git(project, *args):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(project), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_AUTHOR_NAME": "W2-13 tests", "GIT_AUTHOR_EMAIL": "w2-13@example.invalid",
           "GIT_COMMITTER_NAME": "W2-13 tests", "GIT_COMMITTER_EMAIL": "w2-13@example.invalid",
           "GIT_AUTHOR_DATE": BASE_DATE, "GIT_COMMITTER_DATE": BASE_DATE}
    done = subprocess.run(["git", "-C", str(project), "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                           *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel


def commit(project, message):
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message)


def clone(source, destination):
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(source), str(destination)], check=True,
                   capture_output=True)
    return Path(destination)


def line_numbers(text, needle):
    return [number for number, line in enumerate(text.splitlines(), 1) if needle in line]


# --------------------------------------------------------------------------
# The planted secret (DEC-911): joined at run time, never whole in this file
# --------------------------------------------------------------------------

def joined(*parts):
    return "".join(parts)


def canary():
    """A string of the project's canary rule (``template/.gitleaks.toml``, ``gov-canary``)."""
    return joined("ARGUS", "_TOKEN", "_CAN", "ARY", "_4WM8")


CANARY_TAIL = joined("4W", "M8")  # the canary's own word, which no other file of the fixture holds


# --------------------------------------------------------------------------
# The fixture project
# --------------------------------------------------------------------------

_NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history", "export_policy": "allowed",
    "provenance": "written by the W2-13 tests", "deletion_rebuild": "authoritative; restored from git only",
}


def adopt(project, embedded=True):
    """A path map (this repository's own, its namespaces replaced by one that holds everything) and the kernel's
    gitleaks configuration: the two files the secret filter reads."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("decision_register", None)  # the project holds no register file, so its path map names none
    document["namespaces"] = {"everything": {"paths": ["**"], "memory_class": "governance", **_NAMESPACE_FIELDS,
                                             "embedding_policy": "embedded" if embedded else "not embedded"}}
    write(project, PATH_MAP_REL, yaml.safe_dump(document, sort_keys=False))
    shutil.copy2(REPO_ROOT / TEMPLATE_CONFIG_REL, Path(project) / CONFIG_REL)


def record(record_id, body, heading, kind="decision"):
    return (f"---\nid: {record_id}\ntype: {kind}\nstatus: ACCEPTED\nstate_class: AUTHORITATIVE\n---\n\n"
            f"# {heading}\n\n{body}\n")


# ---- success 1, BM25: a plain-word question no line holds verbatim. Same length; 3, 2 and 1 of its words.
PLAIN_QUESTION = "pilot tide harbour"
BEST, SECOND, THIRD = "rank/z-best.md", "rank/m-second.md", "rank/a-third.md"
RANKED = {
    BEST: "# Station log\n\nThe harbour pilot reads the tide table at dawn.\n",
    SECOND: "# Station log\n\nThe harbour pilot reads the wind table at dawn.\n",
    THIRD: "# Station log\n\nThe harbour clerk reads the wind table at dawn.\n",
}

# ---- success 1, fields: each pair holds the same words, the question's word in the title (or id) of one and in the
# body of the other, so only the field tells them apart. The pairs mirror their paths, so no tie-break by path,
# row or insertion order can pass both.
FIELD_PAIRS = {
    "title, the title first by path": ("Lighthouse", "fields/a-title.md", "fields/b-body.md"),
    "title, the body first by path": ("Beacon", "fields/d-title.md", "fields/c-body.md"),
    "id, the id first by path": ("ORCHARD", "fields/e-id.md", "fields/f-body.md"),
    "id, the body first by path": ("QUINCE", "fields/h-id.md", "fields/g-body.md"),
}
FIELDS = {
    "fields/a-title.md": "# Lighthouse ledger\n\nKeepers sign the ledger at dusk.\n",
    "fields/b-body.md": "# Keepers ledger\n\nLighthouse sign the ledger at dusk.\n",
    "fields/d-title.md": "# Beacon almanac\n\nKeepers sign the almanac at noon.\n",
    "fields/c-body.md": "# Keepers almanac\n\nBeacon sign the almanac at noon.\n",
    "fields/e-id.md": record("ORCHARD-12", "The note crates wait by the gate.", "Note twelve"),
    "fields/f-body.md": record("NOTE-12", "The ORCHARD crates wait by the gate.", "Note twelve"),
    "fields/h-id.md": record("QUINCE-14", "The note barrels wait by the wall.", "Note fourteen"),
    "fields/g-body.md": record("NOTE-14", "The QUINCE barrels wait by the wall.", "Note fourteen"),
}

# ---- success 1, the exact identifier: one file holds it; two others hold its parts far more often.
EXACT_ID = "QX-4471"
EXACT_HOLDER = "ids/z-holder.md"
EXACT_QUESTIONS = (EXACT_ID, f"{EXACT_ID} gauge reading")
IDS = {
    EXACT_HOLDER: f"# Valve register\n\nValve {EXACT_ID} is set to half open.\n",
    "ids/a-noise.md": "# QX gauge reading\n\nThe QX gauge reading is 4471; the QX gauge reading is 4471 again.\n"
                      "QX 4471, QX 4471, gauge reading QX 4471.\n",
    "ids/b-noise.md": "# Gauge 4471\n\nQX QX QX 4471 4471 4471: the QX gauge reading log.\n",
}

# ---- success 1, CAP-11: every line that holds an exact string, in two files.
EXACT_STRING = "KV-208"
EXACT_FILES = {
    "exact/one.md": f"# Keys\n\nThe key {EXACT_STRING} opens the shed.\nNothing here.\n\nAsk for {EXACT_STRING} at the desk.\n",
    "exact/two.py": f'"""Keys."""\nSHED_KEY = "{EXACT_STRING}"\n\n\ndef key():\n    return SHED_KEY\n',
}

# ---- W2-M100, whole tokens: ``tern`` is a word of one file and the middle of a longer word in another.
WHOLE_WORD = "tern"
WHOLE_FILE, INSIDE_FILE = "tokens/birds.md", "tokens/fish.md"
TOKENS = {
    WHOLE_FILE: "# Birds\n\nThe tern nests on the cliff.\n",
    INSIDE_FILE: "# Fish\n\nThe lanternfish glows in the deep.\n",
}

# ---- failure 2, the secrets filter: the canary in one tracked file, a clean file beside it.
LEAKY, CLEAN = "secret/leaky.md", "secret/clean.md"
LEAKY_WORDS, CLEAN_WORDS = "marigold ferryman", "juniper ferryman"
LEAKY_ONLY = "marigold"  # a word of the file that holds the canary and of no other file
CLEAN_TERM = "juniper"  # the clean file's own word; an index term holds it, its stem (porter) or a trigram of it

# ---- success 4, RETR-X-02: one record that exists; a line that holds a word of the question about the missing id.
RECORD_ID, RECORD_FILE = "DEC-0042", "records/dec-0042.md"
GAP_QUESTIONS = (MISSING_ID, f"What does {MISSING_ID} decide?")
OTHER = {
    RECORD_FILE: record(RECORD_ID, "The ferry runs every hour from the north quay.", RECORD_ID),
    "notes/board.md": "# Board\n\nThe board will decide on the dredging in spring.\nWhat does the board decide next?\n",
}

# ---- failure 1, a parent expansion: a long section whose one child chunk holds a phrase (W1-21's form).
EXPANSION_PHRASE = "obsidian valve interlock"
MANUAL, MANUAL_HEADING = "manual/manual.md", "## Recovery"


def _manual():
    lines = ["# Manual", "", "## Starting", "", "Open the gate and start the scheduler.", "", MANUAL_HEADING, ""]
    for step in range(1, 91):
        note = f" The {EXPANSION_PHRASE} is tested here." if step == 45 else ""
        lines.append(f"Step {step:02d} of the recovery: read valve {step:02d} and log the reading in the plant book.{note}")
    lines += ["", "## Closing", "", "Close the gate."]
    return "\n".join(lines) + "\n"


# ---- success 1, the parents and spans of today (W1-17, DEC-343): a document of sections and a Python file.
SPANS_DOC, SPANS_CODE = "spans/guide.md", "spans/tool.py"
SPANS = {
    SPANS_DOC: "# Guide\n\nIntro line.\n\n## First\n\nAlpha line one.\nAlpha line two.\n\n## Second\n\nBeta line.\n",
    SPANS_CODE: '"""Tool."""\n\n\ndef first():\n    return 1\n\n\ndef second():\n    value = 2\n    return value\n',
}
# What W1-17's interface gives for these two files on the base (``chunks`` and ``parent``), as
# ``(path, start_line, end_line, parent kind, parent start, parent end)``: the parents and spans of today, read by the
# designer from the base (w2/integrate at c38a5b49bc86) through ``chunks`` and ``parent`` (README, "Spans of today").
SPANS_TODAY = [
    (SPANS_DOC, 1, 4, "section", 1, 4),
    (SPANS_DOC, 5, 9, "section", 5, 9),
    (SPANS_DOC, 10, 12, "section", 10, 12),
    (SPANS_CODE, 1, 3, "module", 1, 10),
    (SPANS_CODE, 4, 5, "function", 4, 5),
    (SPANS_CODE, 6, 7, "module", 1, 10),
    (SPANS_CODE, 8, 10, "function", 8, 10),
]


def corpus():
    files = {"README.md": "# A project\n\nOrdinary text about the project.\n", ".gitignore": ".gov-runtime/\n"}
    for group in (RANKED, FIELDS, IDS, EXACT_FILES, TOKENS, OTHER, SPANS):
        files.update(group)
    files[MANUAL] = _manual()
    files[LEAKY] = f"# Leak\n\nThe {LEAKY_WORDS} keeps {canary()} in a drawer.\n"
    files[CLEAN] = f"# Clean\n\nThe {CLEAN_WORDS} keeps the ledger in a drawer.\n"
    return files


def build_fixture(project):
    """The fixture repository: one commit holding the corpus, the path map and the rules. Not indexed."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    adopt(project)
    for rel, text in corpus().items():
        write(project, rel, text)
    commit(project, "the W2-13 fixture")
    return project


# --------------------------------------------------------------------------
# The store, read as an SQLite file
# --------------------------------------------------------------------------

def store_files(root):
    store = Path(root) / STORE_REL
    return [path for path in (store, Path(f"{store}-wal"), Path(f"{store}-shm")) if path.exists()]


def fts5_tables(root):
    """The names of the FTS5 tables of the store."""
    with sqlite3.connect(f"file:{Path(root) / STORE_REL}?mode=ro", uri=True) as connection:
        rows = connection.execute("SELECT name, sql FROM sqlite_master WHERE type = 'table'").fetchall()
    return sorted(name for name, sql in rows if sql and re.search(r"USING\s+fts5", sql, re.I))


def rows_holding(root, needles):
    """``table -> count`` of the rows of every ordinary table of the store whose values hold one of ``needles``,
    compared without letter case (virtual tables are read through their shadow tables)."""
    wanted = [needle.lower() for needle in needles]
    found = {}
    with sqlite3.connect(f"file:{Path(root) / STORE_REL}?mode=ro", uri=True) as connection:
        tables = connection.execute("SELECT name, sql FROM sqlite_master WHERE type = 'table'").fetchall()
        for name, sql in tables:
            if not sql or sql.upper().startswith("CREATE VIRTUAL"):
                continue
            count = 0
            for row in connection.execute(f'SELECT * FROM "{name}"'):
                text = " ".join(value.decode("utf-8", "replace") if isinstance(value, bytes) else str(value)
                                for value in row).lower()
                count += any(needle in text for needle in wanted)
            if count:
                found[name] = count
    return found


def vocabulary(root, workdir):
    """``table -> set of terms`` of every FTS5 table of the store, read through ``fts5vocab`` on a copy of the store
    in ``workdir`` (the project's store is never written)."""
    copy = Path(workdir) / "store-copy.db"
    for path in store_files(root):
        shutil.copy2(path, Path(workdir) / path.name.replace("store.db", "store-copy.db"))
    terms = {}
    with sqlite3.connect(str(copy)) as connection:
        for table in fts5_tables(root):
            connection.execute(f'CREATE VIRTUAL TABLE temp."vocab_{table}" USING fts5vocab(main, "{table}", row)')
            terms[table] = {row[0] for row in connection.execute(f'SELECT term FROM temp."vocab_{table}"')}
    return terms


# --------------------------------------------------------------------------
# The stand-in Ollama endpoint (W1-21's): vectors computed from words, so no model runs
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
    """A healthy Ollama endpoint on a free loopback port: the version, the model lists and the embeddings."""

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
                elif route == "/api/ps":
                    reply = {"models": [{**model, "size": 639150000, "size_vram": 0}]}
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
# The dev tiers
# --------------------------------------------------------------------------

def clone_tier(name, destination):
    """A clone of a dev tier in a temporary folder, adopted with a map that classes all of it as embedded governance
    memory (as W1-21 adopts it); None when this machine has no such tier."""
    tier = DEV_TIERS / name
    if not (tier / ".git").exists():
        return None
    root = clone(tier, destination)
    with open(root / ".git" / "info" / "exclude", "a", encoding="utf-8") as exclude:
        exclude.write("\n.gov-runtime/\n")
    adopt(root)
    commit(root, "adopted by the W2-13 tests")
    return root


def dev_queries():
    if not QUERY_SET.is_file():
        return None
    return yaml.safe_load(QUERY_SET.read_text(encoding="utf-8"))["queries"]
