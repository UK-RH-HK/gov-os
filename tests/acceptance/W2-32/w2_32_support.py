"""Support code for the W2-32 acceptance tests (DAEO-0pyc; standard library and PyYAML only).

W2-32: retrieval components and bounded improvements. This round covers S1 to S5, S9 and F1 (DEC-1055); the README
maps each KPI line to its cases and names the interface the cases assume.

- **The repository** is the one this file sits in (``Path(__file__).resolve().parents[3]``); nothing in it is written.
- **The code under test** is the ``gov`` package the pytest process imports (DEC-732); every child process gets that
  package's folder first on its ``PYTHONPATH``, and each driver call reports the ``gov`` it imported.
- **Planted projects** are built from scratch in pytest's ``tmp_path``: a few small files, a path map (this
  repository's own, with planted namespaces), the secrets scan off (DEC-1045, so no ``gitleaks`` is needed).
- **No model runs, and no embedder is started** (the CTO's binding rule of 2026-11-03: no private embedder in the
  sandbox). The embedders are a stand-in for Ollama's HTTP interface on the loopback interface, serving two models
  (vectors made of words). Each child's ``GOV_OLLAMA_BIN`` is a trap script that only leaves a marker and exits; its
  ``PATH`` holds no folder with ``ollama`` or ``llama-server``. Every case fails if the trap was called.
- **The reranker** is a stand-in loader in the driver, or a fake reranker environment in the child's scratch ``HOME``
  whose worker prints its "loaded" line and exits (it dies after loading). No model is loaded.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import sqlite3
import struct
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DRIVER = HERE / "w2_32_driver.py"
TICKET = "DAEO-0pyc"
PATH_MAP_REL = "governance/project/path-map.yaml"
SECRETS_REL = "governance/project/secrets.yaml"
STORE_REL = ".gov-runtime/store.db"
# The configuration the embedder pin is read from in a project (the interface this suite assumes; README).
MODELS_REL = "governance/project/models.yaml"
CALL_TIMEOUT_S = 180
REBUILD_TIMEOUT_S = 300


def gov_src() -> Path:
    spec = importlib.util.find_spec("gov")
    if spec is None or not spec.origin:
        raise AssertionError("no gov package can be imported: set PYTHONPATH to the repository's src/ (README)")
    return Path(spec.origin).resolve().parents[1]


GOV_SRC = gov_src()
GOV_FILE = str(GOV_SRC / "gov" / "__init__.py")


def assert_code_under_test():
    assert GOV_SRC == (ROOT / "src").resolve(), f"gov is not this repository's: {GOV_SRC} (set PYTHONPATH, README)"


# --------------------------------------------------------------------------
# The models: the pin of ADR-0002 §2, another revision of it, and a second embedder to swap to
# --------------------------------------------------------------------------

PIN_MODEL = "qwen3-embedding:0.6b"
# The digest Ollama's model list reports for the pinned model: the manifest's sha256 in the tool registry (Ollama
# model id ac6da0dfba84; governance/project/tool-registry.yaml, qwen3-embedding; DEC-374, DEC-397).
PIN_DIGEST = "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"
PIN_ID = PIN_DIGEST[:12]
# The same model name at another revision (a re-pulled or replaced model).
OTHER_DIGEST = hashlib.sha256(b"w2-32 another revision of qwen3-embedding").hexdigest()
# A second embedder, the one the configuration swaps to (CAP-10.b, CAP-19.a).
SWAP_MODEL = "w2-32-stand-in-embed:1"
SWAP_DIGEST = hashlib.sha256(b"w2-32 swap embedder").hexdigest()
DIMENSIONS = {PIN_MODEL: 1024, SWAP_MODEL: 384}
EMBED_CHARS = 512  # the cut a chunk is embedded at (DEC-406); W2-L065 asks the manifest to record it


def stand_in_vector(model, text):
    """A unit vector made of the words of ``text``; each model hashes words its own way, at its own size."""
    size = DIMENSIONS.get(model, 256)
    vector = [0.0] * size
    for word in re.findall(r"[a-z0-9]+", str(text).lower()):
        digest = hashlib.sha256(f"{model}\0{word}".encode()).digest()
        vector[int.from_bytes(digest[:4], "big") % size] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        vector[0], norm = 1.0, 1.0
    return [value / norm for value in vector]


def blob(vector):
    return struct.pack(f"{len(vector)}f", *vector)


class OllamaStandIn:
    """A healthy Ollama endpoint on a free loopback port. ``offer`` sets the models its list reports (name -> digest);
    each is reported loaded on ``device``: the GPU by default (``size_vram`` equal to ``size``), the CPU when
    ``device`` is ``"cpu"`` (``size_vram`` 0; S10, DEC-1065: such a vector is refused). Every ``/api/embed`` request
    is kept as ``(model, texts)``, and every vector returned is kept per model as its float32 bytes."""

    def __init__(self, offered=None, device="gpu"):
        self.device = device
        self.offered = dict(offered or {PIN_MODEL: PIN_DIGEST})
        self.requests = []
        self.returned = {}
        self.lock = threading.Lock()
        stand_in = self

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
                try:
                    asked = json.loads(body) if body else {}
                except ValueError:
                    asked = {}
                route = self.path.split("?")[0].rstrip("/")
                reply, status = {}, 200
                with stand_in.lock:
                    offered = dict(stand_in.offered)
                models = [{"name": name, "model": name, "digest": digest, "size": 639150000,
                           "details": {"family": "stand-in", "parameter_size": "1M", "quantization_level": "F32"}}
                          for name, digest in offered.items()]
                if route == "/api/version":
                    reply = {"version": "0.35.0"}
                elif route == "/api/tags":
                    reply = {"models": models}
                elif route == "/api/ps":
                    on_gpu = stand_in.device != "cpu"
                    reply = {"models": [{**model, "size_vram": model["size"] if on_gpu else 0} for model in models]}
                elif route == "/api/show":
                    name = asked.get("model") or asked.get("name")
                    reply = {"details": {"family": "stand-in"}, "capabilities": ["embedding"],
                             "model_info": {"general.architecture": "stand-in",
                                            "stand-in.embedding_length": DIMENSIONS.get(name, 256)}}
                    status = 200 if name in offered else 404
                elif route == "/api/embed":
                    name = asked.get("model")
                    given = asked.get("input", "")
                    texts = [given] if isinstance(given, str) else list(given)
                    if name not in offered:
                        reply, status = {"error": f"model '{name}' not found"}, 404
                    else:
                        vectors = [stand_in_vector(name, text) for text in texts]
                        with stand_in.lock:
                            stand_in.requests.append((name, texts))
                            stand_in.returned.setdefault(name, set()).update(blob(v) for v in vectors)
                        reply = {"model": name, "embeddings": vectors}
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

    def offer(self, offered):
        with self.lock:
            self.offered = dict(offered)

    def clear(self):
        with self.lock:
            self.requests.clear()

    def texts_embedded(self, model=None):
        """The texts sent to be embedded since the last ``clear``, under ``model`` (any model when None)."""
        with self.lock:
            return [text for name, texts in self.requests if model in (None, name) for text in texts]

    def models_asked(self):
        with self.lock:
            return [name for name, _ in self.requests]

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def dead_host():
    """A loopback address nothing listens on: an embedder that cannot be reached (S10)."""
    import socket
    with socket.socket() as handle:
        handle.bind(("127.0.0.1", 0))
        return f"127.0.0.1:{handle.getsockname()[1]}"


def cache_rows(project):
    """The rows of every table of the two vector caches: the tree's query-vector cache (``.gov-runtime/``) and the
    machine-wide one (``GOV_VECTOR_CACHE_DIR``, the test's own). S10: a refused vector adds none."""
    files = [path for path in (Path(project) / ".gov-runtime").glob("*vector*.db")]
    folder = os.environ.get("GOV_VECTOR_CACHE_DIR")
    if folder and Path(folder).is_dir():
        files += list(Path(folder).glob("*.db"))
    total = 0
    for path in files:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall():
                total += connection.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
        finally:
            connection.close()
    return total


def lacking():
    """What this machine lacks for a store with vectors, or None."""
    if importlib.util.find_spec("sqlite_vec") is None:
        return "sqlite_vec cannot be imported: no vector can be stored (ADR-0002)"
    if shutil.which("git") is None:
        return "no git executable on PATH"
    return None


# --------------------------------------------------------------------------
# Planted projects
# --------------------------------------------------------------------------

def namespace(paths, policy):
    return {"paths": list(paths), "memory_class": "governance", "sensitivity": "internal",
            "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                                "independent-auditor", "research"],
            "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": policy,
            "provenance": "written by the W2-32 tests", "deletion_rebuild": "authoritative; restored from git only"}


# Only ``docs/**`` and the root README are embedded; everything else is lexical only (DEC-381).
NAMESPACES = {
    "notes": namespace(["docs/**", "README.md"], "embedded"),
    "project": namespace(["governance/**", "fixtures/**", "records/**", ".gitignore"], "not embedded"),
}


def planted_path_map():
    """This repository's path map with the planted namespaces, no register, no code index, no evaluation sets."""
    document = yaml.safe_load((ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("decision_register", None)
    document.pop("evaluation_sets", None)
    document["namespaces"] = NAMESPACES
    document.setdefault("capabilities", {})["code_intelligence"] = {"enabled": False}
    return yaml.safe_dump(document, sort_keys=False)


# Each planted note is about one thing, in words no other note uses; the questions ask about it in those words.
NOTES = {
    "docs/harbour.md": "# Harbour\n\nThe harbour master publishes the tide tables every Monday at dawn. "
                       "Ferries wait in the harbour for the high tide.\n",
    "docs/bakery.md": "# Bakery\n\nThe baker lights the wood oven at four and bakes rye loaves and sourdough "
                      "before the bakery opens.\n",
    "docs/orchard.md": "# Orchard\n\nThe apple orchard is pruned in February and the cider is pressed in "
                       "October, after the orchard harvest.\n",
    "docs/lighthouse.md": "# Lighthouse\n\nThe lighthouse keeper trims the lamp wick at dusk and sounds the "
                          "foghorn when the fog rolls in.\n",
    "docs/glacier.md": "# Glacier\n\nThe glacier survey measures the moraine and maps every crevasse each "
                       "summer as the glacier retreats.\n",
    "docs/violin.md": "# Violin\n\nThe luthier carves spruce tops and maple backs and varnishes each violin "
                      "seven times.\n",
    "README.md": "# Planted project\n\nNotes about a harbour town, written by the W2-32 tests.\n",
}

QUESTIONS = (
    ("When does the harbour master publish the tide tables?", "docs/harbour.md"),
    ("When does the baker light the wood oven for the rye loaves?", "docs/bakery.md"),
    ("When is the apple orchard pruned and the cider pressed?", "docs/orchard.md"),
    ("What does the lighthouse keeper do with the lamp wick and the foghorn?", "docs/lighthouse.md"),
)


def _git_env(home):
    return {"PATH": "/usr/bin:/bin", "HOME": str(home), "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "W2-32 tests", "GIT_AUTHOR_EMAIL": "w2-32@example.invalid",
            "GIT_COMMITTER_NAME": "W2-32 tests", "GIT_COMMITTER_EMAIL": "w2-32@example.invalid",
            "GIT_AUTHOR_DATE": "2026-11-03T12:00:00+00:00", "GIT_COMMITTER_DATE": "2026-11-03T12:00:00+00:00"}


def git(project, *args, check=True):
    project = Path(project)
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True,
                          env=_git_env(project.parent / f"{project.name}-git-home"))
    if check:
        assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done


def plant(project, files=None):
    """A planted git repository: ``files`` (rel -> text, default ``NOTES``), the path map and the secrets switch off,
    committed."""
    project = Path(project)
    (project.parent / f"{project.name}-git-home").mkdir(parents=True, exist_ok=True)
    project.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(project)], check=True, capture_output=True,
                   env=_git_env(project.parent / f"{project.name}-git-home"))
    every = {**(NOTES if files is None else files), ".gitignore": ".gov-runtime/\n",
             PATH_MAP_REL: planted_path_map(), SECRETS_REL: "scan: off\n"}
    for rel, text in every.items():
        write(project, rel, text)
    commit(project, "the planted corpus")
    return project


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def commit(project, message):
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message)


def pin(project, model, revision=..., commit_it=False):
    """Write the project's embedder pin (``MODELS_REL``): ``model`` and ``revision`` (left out when ``...``)."""
    embedder = {"model": model}
    if revision is not ...:
        embedder["revision"] = revision
    write(project, MODELS_REL, yaml.safe_dump({"embedder": embedder}, sort_keys=False))
    if commit_it:
        commit(project, "the embedder pin")


def unpin(project):
    path = Path(project) / MODELS_REL
    if path.exists():
        path.unlink()


def files_of(project):
    """Every file of ``project`` outside ``.git``, with its sha256: what a refused call must leave unchanged."""
    project = Path(project)
    return {str(path.relative_to(project)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(project.rglob("*")) if path.is_file() and ".git" not in path.relative_to(project).parts}


# --------------------------------------------------------------------------
# The children: a scratch environment built from nothing, the trap, the driver and gov rebuild
# --------------------------------------------------------------------------

TRAP = "#!/bin/sh\n# W2-32 tests: no embedder may be started (the CTO's rule). Leave a marker and fail.\n" \
       "echo \"$0 $*\" >> \"{marker}\"\nexit 1\n"


class Box:
    """The places and the environment of the child processes of one case."""

    def __init__(self, workdir, host):
        self.workdir = Path(workdir)
        self.host = host
        for name in ("home", "tmp", "pycache", "tools"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        self.home = self.workdir / "home"
        self.marker = self.workdir / "ollama-started.txt"
        self.trap = self.workdir / "tools-trap" / "ollama"
        self.trap.parent.mkdir(parents=True, exist_ok=True)
        self.trap.write_text(TRAP.format(marker=self.marker), encoding="utf-8")
        self.trap.chmod(0o755)
        tools = self.workdir / "tools"
        for name in ("git", "python3", "sh"):
            found = shutil.which(name)
            link = tools / name
            if found and not link.is_symlink():
                link.symlink_to(Path(found).resolve())
        folders = [str(tools)] + [folder for folder in ("/usr/bin", "/bin")
                                  if not any((Path(folder) / name).exists() for name in ("ollama", "llama-server"))]
        self.path = os.pathsep.join(folders)
        self.site = self._site()

    def _site(self):
        """A folder linking the one ``sqlite_vec`` this machine's Python imports (the scratch HOME has no user site)."""
        site = self.workdir / "site"
        site.mkdir(parents=True, exist_ok=True)
        spec = importlib.util.find_spec("sqlite_vec")
        if spec is not None and spec.origin:
            origin = Path(spec.origin)
            source = origin.parent if spec.submodule_search_locations else origin
            link = site / source.name
            if not link.is_symlink():
                link.symlink_to(source, target_is_directory=source.is_dir())
        return site

    def env(self, **extra):
        env = {"PATH": self.path, "HOME": str(self.home), "TMPDIR": str(self.workdir / "tmp"),
               "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
               "PYTHONPATH": os.pathsep.join([str(GOV_SRC), str(self.site)]),
               "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
               "OLLAMA_HOST": self.host, "GOV_QUERY_OLLAMA_HOST": self.host, "GOV_OLLAMA_BIN": str(self.trap),
               "GOV_REBUILD_LOCK": os.environ.get("GOV_REBUILD_LOCK") or str(self.workdir / "rebuild.lock"),
               "GOV_VECTOR_CACHE_DIR": os.environ.get("GOV_VECTOR_CACHE_DIR") or str(self.workdir / "vectors"),
               "GOV_RERANK_TIMEOUT_S": "5", "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
        env.update({key: str(value) for key, value in extra.items()})
        return env

    def assert_no_embedder_started(self):
        assert not self.marker.exists(), \
            f"a child tried to start an embedder ({self.marker.read_text()!r}): no case may (the CTO's rule)"

    # ---- gov rebuild ----

    def rebuild(self, project, *args):
        """``gov rebuild --json`` in ``project``: the envelope (not judged here)."""
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", "rebuild", "--json", *args],
                              cwd=str(project), env=self.env(), capture_output=True, text=True,
                              timeout=REBUILD_TIMEOUT_S)
        try:
            envelope = json.loads(done.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            raise AssertionError(f"gov rebuild gave no JSON (exit {done.returncode}):\n{done.stdout[-3000:]}\n"
                                 f"{done.stderr[-3000:]}") from None
        envelope["_stderr"] = done.stderr
        return envelope

    def built(self, project, *args):
        """``gov rebuild``, which must recreate the semantic store."""
        envelope = self.rebuild(project, *args)
        assert envelope.get("ok") is True and semantic_store(envelope).get("status") == "recreated", \
            f"the rebuild did not build the vectors: {json.dumps(envelope)[:3000]}\n{envelope['_stderr'][-2000:]}"
        return envelope

    # ---- the driver ----

    def call(self, op, **arguments):
        """One driver call in a child process: ``{"result": ...}`` or ``{"raised": {...}}``, with the stderr."""
        done = subprocess.run([sys.executable, str(DRIVER), json.dumps({"op": op, **arguments})],
                              env=self.env(), capture_output=True, text=True, timeout=CALL_TIMEOUT_S,
                              cwd=str(self.workdir))
        lines = done.stdout.strip().splitlines()
        try:
            data = json.loads(lines[-1])
        except (ValueError, IndexError):
            raise AssertionError(f"the driver gave no JSON for {op} (exit {done.returncode}):\n"
                                 f"{done.stdout[-3000:]}\n{done.stderr[-3000:]}") from None
        assert Path(data["gov"]).resolve() == Path(GOV_FILE).resolve(), \
            f"the child ran another gov ({data['gov']}) than the run's ({GOV_FILE}) (DEC-732)"
        data["stderr"] = done.stderr
        return data


def semantic_store(envelope):
    return ((envelope.get("result") or {}).get("stores") or {}).get("semantic") or {}


def result(data):
    """The driver call's result; fails naming the exception when the call raised."""
    raised = data.get("raised")
    assert raised is None, f"the call raised {raised['type']}: {raised['message']}\n{raised['traceback'][-2500:]}"
    return data["result"]


# --------------------------------------------------------------------------
# Reading a store and judging answers
# --------------------------------------------------------------------------

def vectors(project):
    """``chunk_id -> (path, embedding bytes)`` of every vector in the project's store."""
    connection = sqlite3.connect(f"file:{Path(project) / STORE_REL}?mode=ro", uri=True)
    try:
        return {chunk_id: (path, bytes(embedding)) for chunk_id, path, embedding in connection.execute(
            "SELECT v.chunk_id, c.path, v.embedding FROM semantic_vector v "
            "JOIN lexical_chunk c ON c.chunk_id = v.chunk_id")}
    finally:
        connection.close()


def vector_paths(project):
    try:
        return {path for path, _ in vectors(project).values()}
    except sqlite3.Error:
        return set()


def without_cut_record(project):
    """Make the project's store look as a store built before W2-32 does: the vectors kept, every other table named
    ``semantic_*`` dropped, and the manifest in its four-column form (the two models and their revisions), with the
    values it held. W2-L065: such a store records no embedding cut."""
    connection = sqlite3.connect(Path(project) / STORE_REL)
    try:
        row = connection.execute("SELECT embedder_model, embedder_revision, reranker_model, reranker_revision "
                                 "FROM semantic_manifest").fetchone()
        tables = [name for (name,) in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE 'semantic%'")]
        with connection:
            for name in tables:
                if name != "semantic_vector":
                    connection.execute(f'DROP TABLE "{name}"')
            connection.execute("CREATE TABLE semantic_manifest (embedder_model TEXT NOT NULL, embedder_revision TEXT "
                               "NOT NULL, reranker_model TEXT NOT NULL, reranker_revision TEXT NOT NULL)")
            connection.execute("INSERT INTO semantic_manifest VALUES (?, ?, ?, ?)", row)
    finally:
        connection.close()


def code_named(answer, word):
    """The error codes in ``answer`` (any of its text) that hold ``word``: upper-case tokens such as
    ``MODEL_MISMATCH`` (README, "Named errors")."""
    text = json.dumps(answer)
    return sorted(set(re.findall(rf"\b[A-Z0-9_]*{word}[A-Z0-9_]*\b", text)))


def any_code(answer):
    """Every upper-case code of two or more parts in ``answer`` (``MODEL_NOT_LISTED``, ``EMBEDDER_UNPINNED``)."""
    return sorted(set(re.findall(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b", json.dumps(answer))))


def first_paths(hits, n=5):
    seen = []
    for hit in hits:
        if hit["path"] not in seen:
            seen.append(hit["path"])
    return seen[:n]


def holds_value(document, value):
    """True when ``value`` is one of the leaf values of ``document`` (as a number or its text)."""
    if isinstance(document, dict):
        return any(holds_value(item, value) for item in document.values())
    if isinstance(document, (list, tuple)):
        return any(holds_value(item, value) for item in document)
    return document == value or (isinstance(document, str) and document.strip() == str(value))


def no_traceback(data):
    assert "Traceback (most recent call last)" not in data.get("stderr", ""), data["stderr"][-3000:]
