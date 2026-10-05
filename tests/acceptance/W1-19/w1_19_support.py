"""Support code for the W1-19 acceptance tests (standard library and PyYAML only).

W1-19 builds the semantic route, the fusion (RRF) and the one rerank. No KPI names a ``gov`` command and
``src/gov/cli/**`` is outside the ticket's paths, so the tests use the Python interface of DEC-379, reached as
``gov.retrieval.semantic``, ``gov.retrieval.fusion`` and ``gov.retrieval.rerank``.

How the tests call it:

- **Every call runs in a new Python process**, through a small driver written to a temporary directory, with this
  worktree's ``src/`` on ``PYTHONPATH``. The driver also holds the stand-in reranker, counts its loads and passes,
  and can watch the peak memory of the processes the call starts.
- **No index is built in this worktree** (DEC-322). Every project is a temporary git repository with its own path
  map, its own ``.gitleaks.toml`` and its own ``.gov-runtime/store.db``.
- **Two environments.** The model-free cases get an environment built from scratch: an empty temporary ``HOME``,
  ``PATH`` without ``ollama``, and ``OLLAMA_HOST`` pointing at a loopback port that is either dead (Ollama absent) or
  served by the stand-in endpoint of this module. The cases that measure the real models get the machine's own
  ``HOME`` and ``PATH``, with the Hugging Face libraries held offline.
- **The scratch environment imports ``sqlite_vec`` exactly when this machine has it.** An empty ``HOME`` has no
  user site folder, which is where DEC-397 installed the package. So the one package the Python that runs pytest
  finds is linked into a folder of its own, and that folder is put on ``PYTHONPATH``: the ``needs`` marker and the
  process under test then agree, and nothing else of the real ``HOME`` is reachable.
- **The default reranker** starts from ``~/.local/share/gov-os/reranker-venv`` (DEC-397). In the scratch environment
  ``~`` is the empty ``HOME``, so the default is absent there; the cases that use the real one get the machine's
  own environment.
- **Nothing is installed and nothing is downloaded.** What a case needs and this machine lacks makes it skip, with
  the reason (``Needs``).
- **No secret is committed.** The planted string is built at run time from parts.
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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
SEMANTIC = "gov.retrieval.semantic"
FUSION = "gov.retrieval.fusion"
RERANK = "gov.retrieval.rerank"
LEXICAL = "gov.retrieval.lexical"
SECRETS = "gov.secrets"
# The public interface (DEC-379).
INTERFACE = (
    (SEMANTIC, ("refresh", "search", "manifest")),
    (FUSION, ("rrf", "search")),
    (RERANK, ("rerank",)),
)
STORE_REL = ".gov-runtime/store.db"
RUNTIME_REL = ".gov-runtime"
PATH_MAP_REL = "governance/project/path-map.yaml"
CONFIG_REL = ".gitleaks.toml"
TEMPLATE_CONFIG_REL = "template/.gitleaks.toml"

SEMANTIC_FACET = "semantic"
LEXICAL_FACET = "lexical"
UNAVAILABLE = "FACET_UNAVAILABLE"
CALL_TIMEOUT_S = 300.0
MEASURE_TIMEOUT_S = 3600.0
MISSING_EXIT = 3

# The pins of ADR-0002 §2 (DEC-074 R1).
EMBED_MODEL = "qwen3-embedding:0.6b"
EMBED_REVISION = "ac6da0dfba84"
RERANK_MODEL = "Qwen/Qwen3-Reranker-0.6B"
RERANK_REVISION = "e61197ed45024b0ed8a2d74b80b4d909f1255473"
# Where the default reranker's process starts from, under the home folder (DEC-397; the tool registry's row).
RERANK_ENV_REL = ".local/share/gov-os/reranker-venv"
RERANK_PYTHON_REL = RERANK_ENV_REL + "/bin/python"
# The Hugging Face cache under the home folder, when no variable names another.
HF_CACHE_REL = ".cache/huggingface"
# The S0b2 environment lives in the workbench; the default reranker never starts from there (DEC-397).
WORKBENCH_NAME = "gov-os-workbench"
# The libraries the reranker runs on (ADR-0002 §2): none may be loaded before the first rerank.
HEAVY_MODULES = ("torch", "transformers", "sentence_transformers")
# The standard constant of reciprocal rank fusion; the tests that compare scores pass it by name.
RRF_K = 60

# The KPI's figures.
HIT_AT_5_BASELINE = 85.0   # success 2: mean hit@5 >= 85 (the S0b2 R1 baseline)
HIT_AT_5_FAILURE = 80.0    # failure 1: mean hit@5 below 80
WARM_P95_LIMIT_S = 0.5     # success 2
RERANK_RSS_LIMIT_BYTES = 2_500_000_000  # failure 2: 2.5 GB, read as 2.5 x 10^9 bytes (the stricter reading)

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS") or "~/gov-os-workbench/synthetic").expanduser()
QUERY_SET = DEV_TIERS / "dev-queryset.yaml"
TIERS = {"A": "a-dev", "B": "b-dev"}
# Asked before the timed pass, so the models are loaded and no timed question has been asked before (DEC-373).
WARM_UP_QUERIES = ("What does this repository contain?", "Which decisions are recorded here?",
                   "Where are the tests kept?")


class Missing(AssertionError):
    """Something the ticket builds does not exist yet."""


# --------------------------------------------------------------------------
# The driver: one child process per batch of calls
# --------------------------------------------------------------------------

_DRIVER = r'''
import importlib, json, os, sys, threading, time
from pathlib import Path

request = json.loads(sys.stdin.read())
HEAVY = request["heavy"]
LOG = {"loads": 0, "passes": []}


def heavy():
    return [name for name in HEAVY if name in sys.modules]


def loader():
    """The stand-in reranker's loader: counts each load and returns the scorer, which records each pass."""
    LOG["loads"] += 1
    favour = request["reranker"]["favour"]

    def score(query, texts):
        texts = [str(text) for text in texts]
        LOG["passes"].append({"query": query, "texts": texts})
        return [float(sum(text.count(word) for word in favour)) for text in texts]

    return score


def decode(value):
    if isinstance(value, dict) and set(value) == {"$path"}:
        return Path(value["$path"])
    if value == "$reranker":
        return loader
    return value


# ---- the peak resident memory of this process and of every process it starts, the Ollama daemon left out

def _status(pid):
    try:
        with open(f"/proc/{pid}/status", encoding="utf-8", errors="replace") as handle:
            fields = dict(line.split(":", 1) for line in handle if ":" in line)
        with open(f"/proc/{pid}/stat", encoding="utf-8", errors="replace") as handle:
            parent = int(handle.read().rsplit(")", 1)[1].split()[1])
        with open(f"/proc/{pid}/cmdline", "rb") as handle:
            argv = [part.decode("utf-8", "replace") for part in handle.read().split(b"\0") if part]
    except (OSError, ValueError, IndexError):
        return None
    return {"name": fields.get("Name", "").strip(), "parent": parent, "argv": argv,
            "hwm_kb": int(fields.get("VmHWM", "0 kB").split()[0])}


def sample(peaks):
    table = {}
    for entry in os.listdir("/proc"):
        if entry.isdigit():
            status = _status(int(entry))
            if status is not None:
                table[int(entry)] = status
    wanted, frontier = {os.getpid()}, [os.getpid()]
    while frontier:
        parent = frontier.pop()
        for pid, status in table.items():
            if status["parent"] == parent and pid not in wanted and not status["name"].startswith("ollama"):
                wanted.add(pid)
                frontier.append(pid)
    for pid in wanted:
        status = table.get(pid)
        if status and status["hwm_kb"] > peaks.get(pid, {"hwm_kb": -1})["hwm_kb"]:
            peaks[pid] = {"hwm_kb": status["hwm_kb"], "argv": status["argv"][:4], "self": pid == os.getpid()}


peaks, stop = {}, threading.Event()


def watch():
    while not stop.is_set():
        sample(peaks)
        stop.wait(0.05)


modules = {}
for name in request["modules"]:
    try:
        modules[name] = importlib.import_module(name)
    except ModuleNotFoundError as exc:
        if exc.name is None or not (name == exc.name or name.startswith(exc.name + ".")):
            raise
        print(f"No module named {exc.name!r}", file=sys.stderr)
        sys.exit(3)
out = {"heavy_after_import": heavy(), "calls": []}
watcher = threading.Thread(target=watch, daemon=True) if request["watch"] else None
if watcher:
    watcher.start()
for call in request["calls"]:
    module = modules.get(call["module"]) or importlib.import_module(call["module"])
    try:
        function = getattr(module, call["function"])
    except AttributeError:
        print(f"{call['module']} has no function {call['function']}", file=sys.stderr)
        sys.exit(3)
    record = {"loads_before": LOG["loads"], "passes_before": len(LOG["passes"]), "heavy_before": heavy(),
              "value": None, "error": None}
    started = time.perf_counter()
    try:
        record["value"] = function(*[decode(arg) for arg in call["args"]],
                                   **{key: decode(value) for key, value in call["kwargs"].items()})
    except Exception as exc:  # reported, so a test can say "never raises"
        record["error"] = {"type": type(exc).__name__, "message": str(exc)}
    record["seconds"] = time.perf_counter() - started
    record["heavy_after"] = heavy()
    out["calls"].append(record)
if watcher:
    stop.set()
    watcher.join()
    sample(peaks)
out["reranker"] = LOG
out["peaks"] = sorted(peaks.values(), key=lambda peak: -peak["hwm_kb"])
print("\n" + json.dumps(out, default=repr))
'''


def path_arg(path):
    return {"$path": str(path)}


RERANKER = "$reranker"  # as a keyword value: the driver's stand-in loader


class Outcome:
    """What one driver process reported."""

    def __init__(self, data, stderr):
        self.calls = data["calls"]
        self.heavy_after_import = data["heavy_after_import"]
        self.loads = data["reranker"]["loads"]
        self.passes = data["reranker"]["passes"]
        self.peaks = data["peaks"]
        self.stderr = stderr

    def value(self, index=0):
        call = self.calls[index]
        assert call["error"] is None, \
            f"call {index} raised {call['error']['type']}: {call['error']['message']}\n{self.stderr[-2000:]}"
        return call["value"]

    def values(self):
        return [self.value(index) for index in range(len(self.calls))]


class Api:
    """Calls the three modules of this worktree, each batch in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "site"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        self.site = self._link_sqlite_vec()
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")
        self.dead_host = f"127.0.0.1:{free_port()}"

    # ---- environments

    def _link_sqlite_vec(self):
        """A folder that holds a link to the ``sqlite_vec`` this machine's Python imports, and nothing else; None
        when it imports none. The link is to the one installed package (DEC-397), found the way the ``needs`` marker
        finds it, so the scratch environment has the package exactly when the marker says the machine has it."""
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
        """Built from scratch: an empty HOME, no ``ollama`` on PATH, and an endpoint that is dead unless given.

        ``PYTHONPATH`` is this worktree's ``src`` and, when this machine has ``sqlite_vec``, the folder that links
        that one package: the empty HOME has no user site folder to find it in."""
        path = os.pathsep.join(folder for folder in os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)
                               if folder and not (Path(folder) / "ollama").exists())
        return {
            "PATH": path,
            "HOME": str(self.workdir / "home"),
            "TMPDIR": str(self.workdir / "tmp"),
            "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": os.pathsep.join([str(SRC), *([str(self.site)] if self.site else [])]),
            "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
            "OLLAMA_HOST": ollama_host or self.dead_host,
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            **extra,
        }

    def env_without_sqlite_vec(self, ollama_host=None):
        """The scratch environment, in which ``import sqlite_vec`` fails whatever this machine has installed: a
        module of that name that raises ``ImportError`` stands first on ``PYTHONPATH``."""
        blocked = self.workdir / "no-sqlite-vec"
        blocked.mkdir(exist_ok=True)
        (blocked / "sqlite_vec.py").write_text(
            'raise ImportError("sqlite_vec is held absent by the W1-19 tests")\n', encoding="utf-8")
        return self.scratch_env(ollama_host=ollama_host, PYTHONPATH=os.pathsep.join([str(blocked), str(SRC)]))

    def env_with_the_reranker_environment_and_no_snapshot(self, hub):
        """The scratch environment with one thing more under its HOME: a link to this machine's reranker
        environment, at the path DEC-397 gives. That HOME holds no Hugging Face cache, so the pinned snapshot is
        absent.

        ``hub`` is the address of a recording stand-in. It is the only Hugging Face endpoint this environment names,
        and every proxy variable points at a dead loopback port, so nothing can be downloaded through this
        environment whatever the process under test does. The two variables that hold the libraries offline are
        left out on purpose: the default reranker runs offline by itself (DEC-397), not because its caller did."""
        home = self.workdir / "home-with-reranker-environment"
        link = home / RERANK_ENV_REL
        if not link.is_symlink():
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(Path.home() / RERANK_ENV_REL, target_is_directory=True)
        dead = f"http://{self.dead_host}"
        env = self.scratch_env(HOME=str(home), HF_ENDPOINT=f"http://{hub}", HF_HUB_DISABLE_TELEMETRY="1",
                               NO_PROXY="127.0.0.1,localhost", no_proxy="127.0.0.1,localhost",
                               HTTP_PROXY=dead, HTTPS_PROXY=dead, ALL_PROXY=dead,
                               http_proxy=dead, https_proxy=dead, all_proxy=dead)
        for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE"):
            del env[name]
        return env

    def real_env(self):
        """This machine's own environment, for the cases that measure the real models; nothing may be downloaded."""
        env = {key: value for key, value in os.environ.items() if key not in ("GOV_ROLE", "GOV_TICKET")}
        env.update({"PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
                    "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "GIT_CONFIG_NOSYSTEM": "1"})
        return env

    # ---- running

    def run(self, calls, *, env=None, favour=(), watch=False, timeout=CALL_TIMEOUT_S):
        """Run ``[(module, function, args, kwargs), ...]`` in one process and return its :class:`Outcome`.

        The working directory is not the project: every function is given its root.
        """
        request = {
            "modules": [module for module, _ in INTERFACE], "heavy": list(HEAVY_MODULES), "watch": watch,
            "reranker": {"favour": list(favour)},
            "calls": [{"module": module, "function": function, "args": list(args), "kwargs": dict(kwargs)}
                      for module, function, args, kwargs in calls],
        }
        what = ", ".join(dict.fromkeys(f"{module}.{function}" for module, function, *_ in calls)) or "the import"
        try:
            done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request),
                                  env=self.scratch_env() if env is None else env,
                                  cwd=str(self.workdir / "elsewhere"), capture_output=True, text=True,
                                  timeout=timeout)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {timeout:.0f} s") from None
        if done.returncode == MISSING_EXIT:
            raise Missing(f"the semantic route, the fusion or the rerank does not exist: {done.stderr.strip()}")
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr[-4000:]}"
        try:
            data = json.loads(done.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            raise AssertionError(f"{what} did not return JSON values:\n{done.stdout}\n{done.stderr}") from None
        return Outcome(data, done.stderr)

    def call(self, module, function, *args, env=None, favour=(), **kwargs):
        return self.run([(module, function, args, kwargs)], env=env, favour=favour).value()

    def exists(self):
        """Raise Missing unless every function of the public interface can be imported."""
        source = "import importlib\n" + "".join(
            f"getattr(importlib.import_module({module!r}), {name!r})\n"
            for module, names in INTERFACE for name in names)
        done = subprocess.run([sys.executable, "-c", source], capture_output=True, text=True,
                              cwd=str(self.workdir / "elsewhere"), env=self.scratch_env())
        if done.returncode != 0:
            last = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else "import failed"
            raise Missing(f"the semantic route, the fusion or the rerank does not exist: {last}")


# --------------------------------------------------------------------------
# What a case needs from this machine
# --------------------------------------------------------------------------

def _ollama_executable():
    home = Path.home() / ".local/ollama/bin/ollama"
    return os.environ.get("GOV_OLLAMA_BIN") or shutil.which("ollama") or (str(home) if home.is_file() else None)


def _ollama_model():
    models = Path(os.environ.get("OLLAMA_MODELS") or Path.home() / ".ollama/models")
    name, _, tag = EMBED_MODEL.partition(":")
    return (models / "manifests/registry.ollama.ai/library" / name / tag).is_file()


def _reranker_snapshot():
    cache = os.environ.get("HF_HUB_CACHE") or (
        Path(os.environ.get("HF_HOME") or Path.home() / HF_CACHE_REL) / "hub")
    return (Path(cache) / ("models--" + RERANK_MODEL.replace("/", "--")) / "snapshots" / RERANK_REVISION).is_dir()


def reranker_python(home=None):
    """The interpreter the default reranker's process starts from (DEC-397), under ``home`` (default: this
    machine's home folder)."""
    return Path(home or Path.home()) / RERANK_PYTHON_REL


def _reranker_environment():
    interpreter = reranker_python()
    return interpreter.is_file() and os.access(interpreter, os.X_OK)


def _needs():
    """``name -> reason to skip`` for everything this machine lacks. Nothing is run, started or installed."""
    lacking = {}
    if shutil.which("gitleaks") is None:
        lacking["gitleaks"] = "gitleaks is not on PATH on this machine; the secret filter cannot run (DEC-287)"
    if importlib.util.find_spec("sqlite_vec") is None:
        lacking["sqlite_vec"] = ("sqlite_vec (sqlite-vec 0.1.9, ADR-0002) cannot be imported by "
                                 f"{sys.executable}; no vector can be stored (install package IP-1)")
    if _ollama_executable() is None:
        lacking["ollama"] = "no ollama executable (GOV_OLLAMA_BIN, PATH, ~/.local/ollama/bin/ollama): package IP-2"
    elif not _ollama_model():
        lacking["ollama"] = f"the model {EMBED_MODEL} is not in Ollama's model folder (install package IP-3)"
    # The reranker is two things (DEC-397): the environment its process starts from, seen by its interpreter at the
    # exact path, and the pinned snapshot. `reranker_env` is the first alone; `reranker` is both.
    if not _reranker_environment():
        lacking["reranker_env"] = (f"no interpreter at ~/{RERANK_PYTHON_REL}: the reranker environment is not "
                                   "installed (DEC-397)")
        lacking["reranker"] = lacking["reranker_env"]
    elif not _reranker_snapshot():
        lacking["reranker"] = (f"{RERANK_MODEL}@{RERANK_REVISION[:12]} is not in the Hugging Face cache "
                               "(install package IP-4)")
    return lacking


NEEDS = _needs()


def lacking(*names):
    """The reasons this machine cannot run a case that needs ``names``; empty when it can."""
    return [NEEDS[name] for name in names if name in NEEDS]


# --------------------------------------------------------------------------
# Shapes
# --------------------------------------------------------------------------

def check_facet(answer, facet):
    """The shape of a facet's report (DEC-260, DEC-257, DEC-342): unavailable says so, with a reason."""
    assert isinstance(answer, dict), f"not a map: {answer!r}"
    assert isinstance(answer.get("available"), bool), f"`available` is not true or false: {answer!r}"
    assert answer.get("facet") == facet, f"`facet` is not {facet!r}: {answer!r}"
    if not answer["available"]:
        assert answer.get("state") == UNAVAILABLE, f"an unavailable facet does not say {UNAVAILABLE}: {answer!r}"
        assert isinstance(answer.get("reason"), str) and answer["reason"], f"no reason is given: {answer!r}"
    else:
        assert answer.get("state") != UNAVAILABLE, f"an available facet says {UNAVAILABLE}: {answer!r}"
    return answer


def check_hit(hit):
    """A chunk-level hit: the chunk record of W1-17 (DEC-340), with its parent (DEC-091)."""
    assert isinstance(hit, dict), f"a hit is not a map: {hit!r}"
    for key in ("chunk_id", "path", "parent_id"):
        assert isinstance(hit.get(key), str) and hit[key], f"a hit has no {key}: {hit!r}"
    for key in ("start_line", "end_line"):
        assert isinstance(hit.get(key), int), f"a hit's {key} is not a line number: {hit!r}"
    return hit


def check_semantic(answer):
    """The shape of a ``semantic.search`` answer; an unavailable facet carries no hit."""
    check_facet(answer, SEMANTIC_FACET)
    hits = answer.get("hits")
    assert isinstance(hits, list), f"`hits` is not a list: {answer!r}"
    if not answer["available"]:
        assert hits == [], f"an unavailable facet returned hits: {answer!r}"
    for hit in hits:
        check_hit(hit)
    ids = [hit["chunk_id"] for hit in hits]
    assert len(set(ids)) == len(ids), f"a chunk is returned twice: {ids}"
    return answer


def check_fused(answer):
    """The shape of a ``fusion.search`` answer: one list, each chunk once, and the state of both routes."""
    assert isinstance(answer, dict), f"fusion.search did not return a map: {answer!r}"
    hits = answer.get("hits")
    assert isinstance(hits, list), f"`hits` is not a list: {answer!r}"
    for hit in hits:
        check_hit(hit)
        assert isinstance(hit.get("routes"), list) and hit["routes"], f"a hit names no route: {hit!r}"
    ids = [hit["chunk_id"] for hit in hits]
    assert len(set(ids)) == len(ids), f"a chunk is in the fused list twice: {ids}"
    facets = answer.get("facets")
    assert isinstance(facets, dict), f"`facets` is not a map: {answer!r}"
    for facet in (LEXICAL_FACET, SEMANTIC_FACET):
        assert facet in facets, f"`facets` does not report the {facet} route: {facets!r}"
        check_facet(facets[facet], facet)
    assert isinstance(answer.get("reranked"), bool), f"`reranked` is not true or false: {answer!r}"
    return answer


def paths(hits):
    return [hit["path"] for hit in hits]


def is_revision(value, pin):
    """Whether ``value`` records the pinned revision: the pin itself, or a longer digest that begins with it."""
    text = str(value or "").lower()
    return text.removeprefix("sha256:").startswith(pin)


def records_digest(value, digest):
    """Whether ``value`` is the digest the endpoint's model list reported (DEC-374): the digest itself or its first
    twelve or more characters, with ``sha256:`` allowed in front."""
    text = str(value or "").lower().removeprefix("sha256:")
    return len(text) >= 12 and digest.startswith(text)


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------

BASE_DATE = "2026-09-01T12:00:00+00:00"
LATER = "2026-09-02T12:00:00+00:00"


def git(project, *args, date=BASE_DATE):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(project),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W1-19 tests", "GIT_AUTHOR_EMAIL": "w1-19@example.invalid",
        "GIT_COMMITTER_NAME": "W1-19 tests", "GIT_COMMITTER_EMAIL": "w1-19@example.invalid",
        "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
    }
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel


def commit(project, message="a change", date=LATER):
    """Track and commit everything that is not ignored."""
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message, date=date)


def clone(source, destination):
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(source), str(destination)], check=True,
                   capture_output=True)
    return Path(destination)


def runtime_files(project):
    """Every file under ``.gov-runtime/`` of ``project``, as paths relative to that folder."""
    base = Path(project) / RUNTIME_REL
    return sorted(path.relative_to(base).as_posix() for path in base.rglob("*") if path.is_file())


# --------------------------------------------------------------------------
# The fixture project
# --------------------------------------------------------------------------

# The two values of ``embedding_policy`` whose meaning a source gives (DEC-381; the path maps in use). The schema of
# W1-08 allows any non-empty text, so every other value, and a namespace without the field, is read as not embedded.
EMBEDDED = "embedded"
NOT_EMBEDDED = "not embedded"
NO_FIELD = object()  # as a namespace's policy: the namespace has no ``embedding_policy`` at all

_NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history",
    "export_policy": "allowed",
    "embedding_policy": EMBEDDED,
    "provenance": "written by the W1-19 tests",
    "deletion_rebuild": "authoritative; restored from git only",
}

# ``name -> (patterns, memory_class)``. The product namespace has a name and a path this repository's own map does
# not use, so a rule written into the code for this repository cannot satisfy the tests.
NAMESPACES = {
    "top": (["*"], "governance"),
    "overlay": (["governance/**"], "governance"),
    "notes": (["notes/**"], "governance"),
    "code": (["app/**"], "governance"),
    "tenant-exports": (["tenant-exports/**"], "product"),
}


def path_map_text(namespaces):
    """A full path map (DEC-225): this repository's own, with ``namespaces`` in place of its namespaces.

    A namespace is ``(patterns, memory_class)`` or ``(patterns, memory_class, embedding_policy)``; the policy
    ``NO_FIELD`` leaves the field out.
    """
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document["namespaces"] = {}
    for name, (patterns, memory_class, *policy) in namespaces.items():
        entry = {"paths": list(patterns), "memory_class": memory_class, **_NAMESPACE_FIELDS}
        if policy and policy[0] is NO_FIELD:
            del entry["embedding_policy"]
        elif policy:
            entry["embedding_policy"] = policy[0]
        document["namespaces"][name] = entry
    return yaml.safe_dump(document, sort_keys=False)


def adopt(project, namespaces):
    """Give ``project`` a path map and the kernel's gitleaks configuration (the two files the secret filter reads)."""
    write(project, PATH_MAP_REL, path_map_text(namespaces))
    shutil.copy2(REPO_ROOT / TEMPLATE_CONFIG_REL, Path(project) / CONFIG_REL)


_WORD = "CAN" + "ARY"
# The canary as W1-15's first KPI line writes it, built from parts: found by the canary rule of the template.
CANARY = "_".join(["ARGUS", "TOKEN", _WORD, "4WM8"])

# An exact phrase three files hold. The lexical route (an exact-string search, DEC-340) returns them by path.
PHRASE = "amber lantern protocol"
LANTERN = "app/lantern.txt"
MARKER = "notes/marker.md"
ZETA = "notes/zeta.md"
PHRASE_FILES = [LANTERN, MARKER, ZETA]   # in the order of the lexical route: by path
# A word only the last of the three holds. The stand-in reranker scores a text by how often it holds this word.
FAVOURED = "quartz"

BAKERY = "notes/bakery.md"
TIDES = "notes/tides.md"
RUNBOOK = "notes/runbook.md"
POOL = "app/pool.py"
PRODUCT_FILE = "tenant-exports/2026/customers.csv"
LEAK = "notes/leak.md"
PRODUCT_WORDS = "heliotrope ledger of the Scarborough customers"
LEAK_WORDS = "vermilion gantry rota"

# Questions no line of the corpus holds as a string: the lexical route finds nothing, the vectors must.
BAKERY_QUESTION = "when does the baker score each sourdough loaf"
TIDES_QUESTION = "who reads the tide tables at the harbour"
PRODUCT_QUESTION = "heliotrope ledger Scarborough customers"
LEAK_QUESTION = "vermilion gantry rota"
# For the real embedding model: a paraphrase that shares no content word with the section it asks about.
PARAPHRASE = "What should operators do once the workers have stopped responding?"
PARAPHRASE_HEADING = "## Recovery"

CORPUS = {
    "README.md": "# A project\n\nOrdinary text about the project.\n",
    LANTERN: f"The {PHRASE} is posted beside the door.\n",
    MARKER: f"# Marker\n\nThe {PHRASE} begins at dusk.\nThe {PHRASE} ends at dawn.\n",
    ZETA: (f"# Zeta\n\nA long note on stores, shelves, ropes and the {FAVOURED} seam, which mentions the "
           f"{PHRASE} once, in passing, among many other matters of the yard.\n"),
    BAKERY: ("# Bakery\n\nSourdough loaves proof overnight in the cold room.\n"
             "The baker scores each loaf before it goes into the oven.\n"),
    TIDES: ("# Tides\n\nThe harbour pilot reads the tide tables at dawn.\n"
            "The spring tide height is logged in the harbour book.\n"),
    RUNBOOK: ("# Runbook\n\n## Starting\n\nStart the scheduler, then open the gate for incoming jobs.\n\n"
              "## Recovery\n\nWhen the pool hangs, drain it, restart the scheduler daemon and reopen the gate.\n"),
    POOL: ('"""Connection pool."""\n\n\ndef drain(pool):\n    """Empty the pool and close every connection."""\n'
           "    for connection in pool:\n        connection.close()\n    return []\n"),
}
GITIGNORE = ".gov-runtime/\n"
PRODUCT_TEXT = f"id,note\n1,{PRODUCT_WORDS}\n"
LEAK_TEXT = f"# Leak\n\nThe {LEAK_WORDS} is kept with {CANARY} in the same drawer.\n"


def build_fixture(project):
    """The fixture repository: one commit holding the corpus, a product-data file, a file with a planted secret,
    the path map and the rules."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    adopt(project, NAMESPACES)
    write(project, ".gitignore", GITIGNORE)
    write(project, PRODUCT_FILE, PRODUCT_TEXT)
    write(project, LEAK, LEAK_TEXT)
    for rel, text in CORPUS.items():
        write(project, rel, text)
    commit(project, "the fixture", BASE_DATE)
    return project


# --------------------------------------------------------------------------
# The policy fixture: one namespace for each reading of ``embedding_policy`` (DEC-381)
# --------------------------------------------------------------------------

# An unknown value. It begins with, and holds, the one value that embeds: a reading by prefix or by substring
# takes it for ``embedded``.
UNKNOWN_POLICY = "embedded on request"
# An exact phrase all four files hold, so the lexical route returns all four (W1-17's index is not changed).
POLICY_PHRASE = "pewter whistle signal"
ORCHARD = "open/orchard.md"
VAULT = "closed/vault.md"
ATTIC = "odd/attic.md"
CELLAR = "bare/cellar.md"
POLICY_NAMESPACES = {
    # The root files and the overlay are not embedded, as in this repository's own map.
    "top": (["*"], "governance", NOT_EMBEDDED),
    "overlay": (["governance/**"], "governance", NOT_EMBEDDED),
    "open": (["open/**"], "governance", EMBEDDED),
    "closed": (["closed/**"], "governance", NOT_EMBEDDED),
    "odd": (["odd/**"], "governance", UNKNOWN_POLICY),
    "bare": (["bare/**"], "governance", NO_FIELD),
}
POLICY_CORPUS = {
    ORCHARD: f"# Orchard\n\nThe orchard keeper prunes the pear trees in February.\nThe {POLICY_PHRASE} ends the day.\n",
    VAULT: f"# Vault\n\nThe cobalt ledger of the vault lists every sealed crate.\nThe {POLICY_PHRASE} opens it.\n",
    ATTIC: f"# Attic\n\nThe saffron register of the attic lists every folded sail.\nThe {POLICY_PHRASE} airs it.\n",
    CELLAR: f"# Cellar\n\nThe indigo roster of the cellar lists every corked barrel.\nThe {POLICY_PHRASE} locks it.\n",
}
ORCHARD_WORD = "February"
ORCHARD_QUESTION = "who prunes the pear trees in the orchard"
# ``file -> (why it is not embedded, a word only that file holds, a question near its text that lacks the word)``.
# No question holds its file's word, so the word reaches the endpoint only if the file's text is sent.
NEVER_EMBEDDED = {
    VAULT: (f"its namespace says `{NOT_EMBEDDED}`", "cobalt", "which ledger of the vault lists every sealed crate"),
    ATTIC: (f"its namespace says `{UNKNOWN_POLICY}`, an unknown value", "saffron",
            "which register of the attic lists every folded sail"),
    CELLAR: ("its namespace has no `embedding_policy`", "indigo",
             "which roster of the cellar lists every corked barrel"),
}


def build_policy_fixture(project):
    """A repository of four governance namespaces that differ only in ``embedding_policy``, one file in each."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    adopt(project, POLICY_NAMESPACES)
    write(project, ".gitignore", GITIGNORE)
    for rel, text in POLICY_CORPUS.items():
        write(project, rel, text)
    commit(project, "the policy fixture", BASE_DATE)
    return project


# --------------------------------------------------------------------------
# The stand-in Ollama endpoint: the HTTP interface of the daemon, with vectors computed from words
# --------------------------------------------------------------------------

DIMENSIONS = 1024  # what Qwen3-Embedding-0.6B returns
STAND_IN_DIGEST = EMBED_REVISION + hashlib.sha256(b"w1-19 stand-in").hexdigest()[:52]
# A digest that does not begin with the pin: what a model list reports when the tag holds another build.
OTHER_DIGEST = "5e" + hashlib.sha256(b"w1-19 another build of the embedder").hexdigest()[:62]
_STOP = {"the", "and", "for", "with", "that", "this", "each", "does", "when", "who", "what", "into", "from",
         "its", "are", "was", "has", "have", "before", "after", "then", "any", "all", "given", "query",
         "instruct", "retrieve", "relevant", "passages", "search", "web", "answer", "document"}


def _stem(word):
    return word[:-1] if word.endswith("s") and len(word) >= 5 else word


def stand_in_vector(text):
    """A unit vector made of the words of ``text``: texts that share words are near each other."""
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"[a-z0-9]+", str(text).lower()):
        if len(word) < 3 or word in _STOP:
            continue
        digest = hashlib.sha256(_stem(word).encode()).digest()
        vector[int.from_bytes(digest[:4], "big") % DIMENSIONS] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        vector[0], norm = 1.0, 1.0
    return [value / norm for value in vector]


class OllamaStandIn:
    """A healthy Ollama endpoint on a free loopback port. It answers the version, the model list, the model's
    description and both embedding requests, and records every request it receives.

    ``digest`` is the digest its model list (``GET /api/tags``) reports for the embedding model. No other answer
    carries a digest, as with the daemon, so the model list is the one place a revision can be observed (DEC-374).
    """

    def __init__(self, digest=STAND_IN_DIGEST):
        self.requests = []
        self.digest = digest
        requests = self.requests
        model = {"name": EMBED_MODEL, "model": EMBED_MODEL, "digest": digest, "size": 639150000,
                 "details": {"family": "qwen3", "parameter_size": "595.78M", "quantization_level": "Q8_0"}}

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
                requests.append({"method": self.command, "path": self.path, "body": body})
                try:
                    asked = json.loads(body) if body else {}
                except ValueError:
                    asked = {}
                route = self.path.split("?")[0].rstrip("/")
                reply, status = {}, 200
                if route == "/api/version":
                    reply = {"version": "0.35.0"}
                elif route == "/api/tags":
                    reply = {"models": [model]}
                elif route == "/api/ps":
                    reply = {"models": []}
                elif route == "/api/show":
                    reply = {"details": model["details"],
                             "model_info": {"general.architecture": "qwen3", "qwen3.embedding_length": DIMENSIONS},
                             "capabilities": ["embedding"]}
                elif route == "/api/embed":
                    given = asked.get("input", "")
                    texts = [given] if isinstance(given, str) else list(given)
                    reply = {"model": EMBED_MODEL, "embeddings": [stand_in_vector(text) for text in texts],
                             "total_duration": 1, "load_duration": 1, "prompt_eval_count": len(texts)}
                elif route == "/api/embeddings":
                    reply = {"embedding": stand_in_vector(asked.get("prompt", ""))}
                else:
                    status = 404
                payload = json.dumps(reply).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = do_HEAD = do_DELETE = answer

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.host = f"127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

    def embedded_text(self):
        """Everything that was sent to be embedded, as one string."""
        return "\n".join(request["body"] for request in self.requests if "/api/embed" in request["path"])

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class HubStandIn:
    """A loopback address that stands where the Hugging Face hub would be. It serves nothing (every answer is 404)
    and records every request it receives: a process that runs offline asks it nothing."""

    def __init__(self):
        self.requests = []
        requests = self.requests

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                requests.append(f"{self.command} {self.path}")
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()

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


def is_python(peak):
    """Whether the watched process ``peak`` was started as a Python interpreter, by the name of its first argument."""
    return bool(peak["argv"]) and Path(peak["argv"][0]).name.startswith("python")


def started_from(peak, interpreter):
    """Whether the watched process ``peak`` was started with an interpreter of the environment ``interpreter``
    belongs to: its first argument is a ``python`` in that environment's ``bin``. The path is compared as written,
    not resolved: the environment's interpreter is a link to the system's."""
    return is_python(peak) and Path(os.path.normpath(peak["argv"][0])).parent == Path(interpreter).parent


def free_port():
    """A loopback port nothing listens on."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


# --------------------------------------------------------------------------
# The dev tiers and the dev query set
# --------------------------------------------------------------------------

def clone_tier(name, destination):
    """A clone of a dev tier in a temporary directory, adopted with a map that classes all of it as governance
    memory; None when this machine has no such tier."""
    tier = DEV_TIERS / name
    if not (tier / ".git").exists():
        return None
    root = clone(tier, destination)
    with open(root / ".git" / "info" / "exclude", "a", encoding="utf-8") as exclude:
        exclude.write("\n.gov-runtime/\n")  # derived state is never tracked, whatever the tier's own .gitignore says
    adopt(root, {"everything": (["**"], "governance")})
    commit(root, "adopted by the W1-19 tests")
    return root


def dev_queries():
    """The public dev query set (S0b1; DEC-074 names its 52 queries), or None when it is not on this machine."""
    if not QUERY_SET.is_file():
        return None
    return yaml.safe_load(QUERY_SET.read_text(encoding="utf-8"))["queries"]


QUERY_CLASSES = 10  # S0b2 RESULTS.md: "52 queries, ten classes"


def distinct_paths(hits, depth=5):
    """The first ``depth`` distinct paths of a ranked list (S0b2: "each candidate's top-5 distinct paths per
    query")."""
    return list(dict.fromkeys(paths(hits)))[:depth]


def is_hit(gold_paths, hits, depth=5):
    """hit@5: one of the query's ``must_cite`` paths is among the first five distinct paths (DEC-380). A query
    that names no ``must_cite`` path cannot be a hit."""
    return bool(set(gold_paths) & set(distinct_paths(hits, depth)))


def mean_hit_at_5(scored):
    """``scored`` is ``class -> [bool, ...]``, one per query of the class, both tiers together. The mean of the
    classes' percentages of hits (S0b2: "Mean of ten classes"), and the percentage of each class."""
    per_class = {name: 100.0 * sum(hits) / len(hits) for name, hits in scored.items()}
    return sum(per_class.values()) / len(per_class), {name: round(value, 1) for name, value in per_class.items()}


def p95(seconds):
    """The 95th percentile by the nearest-rank rule."""
    ordered = sorted(seconds)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]
