"""Support code for the W1-22 acceptance tests (standard library and PyYAML only).

W1-22 builds the evidence validator and the zero-result canaries. The tests use only public interfaces:

- ``gov.retrieval.validate.validate(root, bundle)``, called in a child process;
- ``gov.retrieval.canary.run_canaries(root)``, called in a child process;
- the canary declarations under ``template/governance/kernel/canaries/``.

How the tests call it:

- **Every call runs in a new Python process** with this worktree's ``src/`` on ``PYTHONPATH`` and a working
  directory that is never the project under test.
- **Nothing is built in this worktree** (DEC-322). Every project is a temporary git repository with its own
  path map, its own ``.gitleaks.toml`` and its own ``.gov-runtime/``.
- **The scratch environment** is built from nothing: an empty ``HOME`` (so the default reranker is absent),
  a ``PATH`` that holds ``git``, ``gitleaks`` and ``python3`` only, and ``OLLAMA_HOST`` pointing at a loopback
  port that is dead or served by the stand-in endpoint. No model runs.
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

# ---- the public interface (package DP-1: validator, DP-2: canary runner) ---------
VALIDATE_MODULE = "gov.retrieval.validate"
VALIDATE_FUNCTION = "validate"
CANARY_MODULE = "gov.retrieval.canary"
CANARY_FUNCTION = "run_canaries"
LEXICAL = "gov.retrieval.lexical"
SEMANTIC = "gov.retrieval.semantic"
STORE = "gov.store"

CANARY_TEMPLATE_REL = "template/governance/kernel/canaries"
PATH_MAP_REL = "governance/project/path-map.yaml"
CONFIG_REL = ".gitleaks.toml"
TEMPLATE_CONFIG_REL = "template/.gitleaks.toml"
RUNTIME_REL = ".gov-runtime"
CALL_TIMEOUT_S = 300.0
MISSING_EXIT = 3

# ---- the bundle keys (shared with W1-21) -----------------------------------------
K_REASON = "stopping_reason"
K_EVIDENCE = "evidence"
K_BATCHES = "batches"
K_MERGE = "merge"
K_EXPANSIONS = "expansions"
K_GAPS = "gaps"
K_FACETS = "facets"
K_BUDGET = "budget"
K_CONTINUATION = "continuation"
E_ID, E_SHA, E_PATH, E_START, E_END, E_TEXT, E_CHUNK, E_ROUTES, E_BATCH = \
    "id", "sha256", "path", "start_line", "end_line", "text", "chunk_id", "routes", "batch"

# The fixed list of stopping reasons (ADR-0002 §4, DEC-034, DEC-396).
REASONS = ("CLOSURE_COMPLETE", "SATURATED", "DEPTH_LIMIT_REACHED", "BUDGET_EXHAUSTED_WITH_GAPS",
           "FACET_UNAVAILABLE", "UNRESOLVED_IDS")
FACET_UNAVAILABLE = "FACET_UNAVAILABLE"

# ---- the validator result keys (DP-1) --------------------------------------------
V_VALID = "valid"
V_ERRORS = "errors"

# ---- canary indexes (DP-2) -------------------------------------------------------
INDEXES = ("lexical", "semantic")


class Missing(AssertionError):
    """Something the ticket builds does not exist yet."""


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


def path_arg(path):
    return {"$path": str(path)}


class Outcome:
    """What one driver process reported."""

    def __init__(self, data, stderr):
        self.calls, self.stderr = data["calls"], stderr

    def error(self, index=0):
        return self.calls[index]["error"]

    def value(self, index=0):
        call = self.calls[index]
        assert call["error"] is None, \
            f"call {index} raised {call['error']['type']}: {call['error']['message']}\n{self.stderr[-2000:]}"
        return call["value"]


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class Api:
    """Calls this worktree's modules in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "site", "bin"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        for tool in ("git", "gitleaks", "python3"):
            found = sys.executable if tool == "python3" else shutil.which(tool)
            if found:
                wrapper = self.workdir / "bin" / tool
                wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
                wrapper.chmod(0o755)
        self.site = self._link_sqlite_vec()
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")
        self.dead_host = f"127.0.0.1:{_free_port()}"

    def _link_sqlite_vec(self):
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

    def run(self, calls, *, env=None, timeout=CALL_TIMEOUT_S):
        request = {"calls": [{"module": m, "function": f, "args": list(a), "kwargs": dict(k)}
                             for m, f, a, k in calls]}
        what = ", ".join(dict.fromkeys(f"{m}.{f}" for m, f, *_ in calls))
        try:
            done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request),
                                  env=self.scratch_env() if env is None else env,
                                  cwd=str(self.workdir / "elsewhere"), capture_output=True, text=True,
                                  timeout=timeout)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {timeout:.0f} s") from None
        if done.returncode == MISSING_EXIT:
            raise Missing(f"the module does not exist: {done.stderr.strip()}")
        assert done.returncode == 0, f"{what} failed (exit {done.returncode}):\n{done.stderr[-4000:]}"
        try:
            data = json.loads(done.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            raise AssertionError(f"{what} gave no JSON:\n{done.stdout}\n{done.stderr}") from None
        return Outcome(data, done.stderr)

    def call(self, module, function, *args, env=None, **kwargs):
        return self.run([(module, function, args, kwargs)], env=env).value()

    def exists(self, module, function):
        done = subprocess.run([sys.executable, "-c", f"from {module} import {function}"], capture_output=True,
                              text=True, cwd=str(self.workdir / "elsewhere"), env=self.scratch_env())
        if done.returncode != 0:
            last = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else "import failed"
            raise Missing(f"{module}.{function} does not exist: {last}")

    # ---- what a retrieval reads

    def build(self, root, host=None, env=None):
        env = env or self.scratch_env(host)
        outcome = self.run([(LEXICAL, "refresh", [path_arg(root)], {}),
                            (SEMANTIC, "refresh", [path_arg(root)], {}),
                            (STORE, "load", [path_arg(root)], {})], env=env, timeout=CALL_TIMEOUT_S)
        return [outcome.value(i) for i in range(3)]

    # ---- the validator (DP-1)

    def validate(self, root, bundle, env=None):
        return self.call(VALIDATE_MODULE, VALIDATE_FUNCTION, path_arg(root), bundle, env=env)

    # ---- the canary runner (DP-2)

    def run_canaries(self, root, env=None):
        return self.call(CANARY_MODULE, CANARY_FUNCTION, path_arg(root), env=env)


# --------------------------------------------------------------------------
# What a case needs from this machine
# --------------------------------------------------------------------------

def _needs():
    lacking = {}
    if shutil.which("gitleaks") is None:
        lacking["gitleaks"] = "gitleaks is not on PATH; the secret filter cannot run (DEC-287)"
    if importlib.util.find_spec("sqlite_vec") is None:
        lacking["sqlite_vec"] = f"sqlite_vec cannot be imported by {sys.executable}; no vector can be stored"
    return lacking


NEEDS = _needs()


def lacking(*names):
    return [NEEDS[name] for name in names if name in NEEDS]


# --------------------------------------------------------------------------
# The bundle
# --------------------------------------------------------------------------

def sha256(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def span_bytes(root, rel, start, end):
    lines = (Path(root) / rel).read_bytes().splitlines(keepends=True)
    return b"".join(lines[start - 1:end])


# --------------------------------------------------------------------------
# git and fixture helpers
# --------------------------------------------------------------------------

BASE_DATE = "2026-09-01T12:00:00+00:00"


def git(project, *args, date=BASE_DATE):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(project), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "W1-22 tests", "GIT_AUTHOR_EMAIL": "w1-22@example.invalid",
           "GIT_COMMITTER_NAME": "W1-22 tests", "GIT_COMMITTER_EMAIL": "w1-22@example.invalid",
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
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message, date=date)


# --------------------------------------------------------------------------
# The fixture project
# --------------------------------------------------------------------------

_NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history", "export_policy": "allowed",
    "provenance": "written by the W1-22 tests", "deletion_rebuild": "authoritative; restored from git only",
}
NAMESPACES = {
    "top": (["*"], "not embedded"),
    "overlay": (["governance/**"], "not embedded"),
    "docs": (["docs/**"], "embedded"),
}

CANARY_FILE = "docs/canary.md"
CANARY_TEXT = "juniper lantern protocol sentinel"
NOTES_FILE = "docs/notes.md"
NOTES_TEXT = "cedar almanac verification beacon"


def adopt(project):
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document["namespaces"] = {name: {"paths": list(patterns), "memory_class": "governance", **_NAMESPACE_FIELDS,
                                     "embedding_policy": policy} for name, (patterns, policy) in NAMESPACES.items()}
    write(project, PATH_MAP_REL, yaml.safe_dump(document, sort_keys=False))
    shutil.copy2(REPO_ROOT / TEMPLATE_CONFIG_REL, Path(project) / CONFIG_REL)


def build_fixture(project):
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    adopt(project)
    write(project, ".gitignore", ".gov-runtime/\n")
    write(project, "README.md", "# Test project\n\nA fixture for the W1-22 acceptance tests.\n")
    write(project, CANARY_FILE,
          f"# Canary\n\nThe {CANARY_TEXT} is checked by the canary runner.\n"
          f"Every adopted project contains at least one canary phrase.\n")
    write(project, NOTES_FILE,
          f"# Notes\n\nThe {NOTES_TEXT} marks this file.\n"
          f"Governance notes for the test project.\n")
    write(project, "records/dec-001.md",
          "---\nid: DEC-001\ntype: decision\nstatus: ACCEPTED\nstate_class: AUTHORITATIVE\n---\n\n"
          "# DEC-001\n\nA test decision for the fixture project.\n")
    commit(project, "the W1-22 fixture")
    return project


def valid_bundle(root, rel=None, start=1, end=None):
    """A bundle that should pass the validator: one evidence item citing a real file with a correct span hash."""
    root = Path(root)
    if rel is None:
        rel = CANARY_FILE
    lines = (root / rel).read_bytes().splitlines(keepends=True)
    if end is None:
        end = len(lines)
    body = b"".join(lines[start - 1:end])
    text = body.decode("utf-8", "replace")
    return {
        K_REASON: "SATURATED",
        K_EVIDENCE: [{
            E_ID: "test-chunk-001",
            E_SHA: sha256(body),
            E_PATH: rel,
            E_START: start,
            E_END: end,
            E_TEXT: text,
            E_CHUNK: "chunk-001",
            E_ROUTES: ["lexical"],
            E_BATCH: 1,
        }],
        K_BATCHES: [{"size": 1}],
        K_MERGE: {"candidates": 1, "duplicates": 0, "dropped": [], "reranked": False},
        K_EXPANSIONS: [],
        K_GAPS: [],
        K_FACETS: {"lexical": {"available": True, "reason": None},
                   "semantic": {"available": True, "reason": None}},
        K_BUDGET: {"rounds": {"limit": 1, "used": 0}, "bundle": {"limit": 6000, "used": len(text) // 4}},
        K_CONTINUATION: None,
    }


# --------------------------------------------------------------------------
# The stand-in Ollama endpoint
# --------------------------------------------------------------------------

EMBED_MODEL = "qwen3-embedding:0.6b"
DIMENSIONS = 1024
_STOP = {"the", "and", "for", "with", "that", "this", "each", "does", "when", "who", "what", "into", "from", "its",
         "are", "was", "has", "have", "before", "after", "then", "any", "all", "given", "query", "instruct",
         "retrieve", "relevant", "passages", "search", "web", "answer", "which", "every"}


def stand_in_vector(text):
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"[a-z0-9]+", str(text).lower()):
        if len(word) >= 3 and word not in _STOP:
            digest = hashlib.sha256(word.encode()).digest()
            vector[int.from_bytes(digest[:4], "big") % DIMENSIONS] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0.0:
        vector[0], norm = 1.0, 1.0
    return [v / norm for v in vector]


class OllamaStandIn:
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
                    reply = {"model": EMBED_MODEL, "embeddings": [stand_in_vector(t) for t in texts]}
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
