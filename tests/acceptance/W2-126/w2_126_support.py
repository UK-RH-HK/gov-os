"""Support code for the W2-126 acceptance tests (DAEO-jpr0; standard library and PyYAML only).

W2-126 (DEC-1032, P1-LOAD-BALANCE-1 b.1 and b.6): one machine-wide vector cache keyed by the model, its revision
and the sha256 of the exact text sent, so each text is embedded once on the machine.

How the tests run (README, "How the suite finds the code under test"):

- **The code under test is the ``src/`` of the repository this file sits in** (``REPO_ROOT / "src"``), put first
  on ``PYTHONPATH`` of every child process; the session asserts that the ``gov`` package found from there is that
  one (DEC-732). Nothing of another worktree and no installed copy is used.
- **Through public interfaces only:** ``gov.retrieval.semantic.refresh``/``search``/``query_vector``, the store's
  ``semantic_vector`` and ``semantic_manifest`` tables, and the retrieval check (``python3 -m
  gov.retrieval.retrieve_check``). Each run is a child process (a small driver written to a temporary folder).
- **The embedder is a stand-in** on a free loopback port that answers Ollama's protocol (``/api/version``,
  ``/api/tags``, ``/api/ps``, ``/api/embed``), reports the model wholly on the CPU and a revision the test chooses,
  and records every text it is sent with the vector it returned. ``OLLAMA_HOST`` and ``GOV_QUERY_OLLAMA_HOST``
  both name it; it answers ``/api/version``, so nothing is ever started; ``PATH`` holds no ``ollama``.
- **The cache is never the user's real one:** ``GOV_VECTOR_CACHE_DIR`` names a temporary folder, and ``HOME`` and
  ``XDG_CACHE_HOME`` are temporary folders too.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import struct
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"

# The interface the cases need (README, "Interface the cases need").
CACHE_DIR_SETTING = "GOV_VECTOR_CACHE_DIR"
CACHE_BOUND_SETTING = "GOV_VECTOR_CACHE_MAX_BYTES"
RESULT_KEY = "vector_cache"  # in the result of semantic.refresh and semantic.search: {"hits", "misses", "skipped"}

MODEL = "qwen3-embedding:0.6b"  # the pinned embedder (ADR-0002 §2); no public interface selects another
REVISION_1 = "ac6da0dfba84" + hashlib.sha256(b"w2-126 revision 1").hexdigest()[:52]
REVISION_2 = "5e" + hashlib.sha256(b"w2-126 revision 2").hexdigest()[:62]
STORE_REL = ".gov-runtime/store.db"
PATH_MAP_REL = "governance/project/path-map.yaml"
GITLEAKS_TEMPLATE_REL = "template/.gitleaks.toml"
CALL_TIMEOUT_S = 300.0


def lacking():
    """Why a case cannot run on this machine, or None: the lexical index needs gitleaks, the vectors sqlite_vec."""
    if not shutil.which("gitleaks"):
        return "no gitleaks executable on PATH: the lexical index cannot be built"
    if importlib.util.find_spec("sqlite_vec") is None:
        return "sqlite_vec cannot be imported: no vector can be stored"
    return None


# --------------------------------------------------------------------------
# The stand-in embedder
# --------------------------------------------------------------------------

def vector_of(text, revision, dimensions, salt=0):
    """A float32-exact vector for ``text``: a function of the revision, the text and ``salt`` alone."""
    seed = f"{revision}\x00{salt}\x00{text}".encode("utf-8", "surrogatepass")
    raw = b"".join(hashlib.sha256(seed + n.to_bytes(4, "big")).digest() for n in range((dimensions * 4 + 31) // 32))
    numbers = [(value / 2147483648.0) - 1.0 for value in struct.unpack(f">{dimensions}I", raw[:dimensions * 4])]
    return list(struct.unpack(f"{dimensions}f", struct.pack(f"{dimensions}f", *numbers)))


def packed(vector):
    return struct.pack(f"{len(vector)}f", *vector)


class StandIn:
    """A healthy Ollama endpoint on a free loopback port that records every text it is sent.

    ``varying``: each request gives other vectors (a cached vector then shows it was not computed again).
    ``hold``: a request with a text that holds this mark is kept open until ``release()``.
    """

    def __init__(self, revision=REVISION_1, dimensions=64, varying=False, delay_s=0.0):
        self.revision, self.dimensions, self.varying, self.delay_s = revision, dimensions, varying, delay_s
        self.hold = None
        self.held, self.released = threading.Event(), threading.Event()
        self.lock = threading.Lock()
        self.records = []  # (text, vector bytes, revision), in the order received
        self.calls = 0
        stand_in = self

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                try:
                    asked = json.loads(body) if body else {}
                except ValueError:
                    asked = {}
                route = self.path.split("?")[0].rstrip("/")
                model = {"name": MODEL, "model": MODEL, "digest": stand_in.revision, "size": 639150000}
                status, reply = 200, {}
                if route == "/api/version":
                    reply = {"version": "0.35.0"}
                elif route == "/api/tags":
                    reply = {"models": [model]}
                elif route == "/api/ps":
                    # Rewrite-Reason: W2-32's S10 (DEC-1065): the model on the GPU
                    reply = {"models": [{**model, "size_vram": model["size"]}]}
                elif route == "/api/embed":
                    reply = stand_in.embed(asked.get("input", ""))
                else:
                    status = 404
                payload = json.dumps(reply).encode()
                try:
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                except OSError:
                    pass

            do_GET = do_POST = do_HEAD = answer

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.host = f"127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05},
                                       daemon=True)
        self.thread.start()

    def embed(self, given):
        texts = [given] if isinstance(given, str) else [str(text) for text in given]
        with self.lock:
            self.calls += 1
            salt, revision = (self.calls if self.varying else 0), self.revision
        vectors = [vector_of(text, revision, self.dimensions, salt) for text in texts]
        with self.lock:
            self.records.extend((text, packed(vector), revision) for text, vector in zip(texts, vectors))
        if self.delay_s:
            time.sleep(self.delay_s)
        if self.hold and any(self.hold in text for text in texts):
            self.held.set()
            self.released.wait(timeout=180)
        return {"model": MODEL, "embeddings": vectors}

    def texts(self):
        with self.lock:
            return [text for text, _, _ in self.records]

    def returned(self):
        """Every vector returned, as bytes."""
        with self.lock:
            return {vector for _, vector, _ in self.records}

    def sent_with(self, word):
        return [text for text in self.texts() if word in text]

    def reset(self):
        with self.lock:
            self.records.clear()

    def release(self):
        self.released.set()

    def close(self):
        self.released.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=10)


# --------------------------------------------------------------------------
# Planted projects
# --------------------------------------------------------------------------

DATE = "2026-11-01T12:00:00+00:00"
NAMESPACE_FIELDS = {
    "memory_class": "governance", "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history", "export_policy": "allowed", "provenance": "written by the W2-126 tests",
    "deletion_rebuild": "authoritative; restored from git only",
}
CORPUS = {
    "notes/bakery.md": "# Bakery\n\nSourdough loaves proof overnight in the cold room before the baker scores them.\n",
    "notes/tides.md": "# Tides\n\nThe harbour pilot reads the tide tables at dawn and logs the spring tide.\n",
    "notes/orchard.md": "# Orchard\n\nThe quince trees are pruned in February when the sap is still low.\n",
    "notes/foundry.md": "# Foundry\n\nBronze is poured at noon into sand moulds packed the evening before.\n",
    "notes/apiary.md": "# Apiary\n\nThe beekeeper smokes the hive gently before lifting the brood frames.\n",
    "app/pool.py": '"""Connection pool."""\n\n\ndef drain(pool):\n    """Close every connection."""\n'
                   "    for connection in pool:\n        connection.close()\n",
}


def git_env(home):
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "W2-126 tests",
            "GIT_AUTHOR_EMAIL": "w2-126@example.invalid", "GIT_COMMITTER_NAME": "W2-126 tests",
            "GIT_COMMITTER_EMAIL": "w2-126@example.invalid", "GIT_AUTHOR_DATE": DATE, "GIT_COMMITTER_DATE": DATE}


def git(project, *args, cwd=None):
    done = subprocess.run(["git", *(["-C", str(project)] if project else []), *args], capture_output=True,
                          text=True, cwd=cwd, env=git_env(Path(project or cwd).parent))
    assert done.returncode == 0, f"git {' '.join(args)} failed:\n{done.stderr}"
    return done.stdout


NAMESPACES = {   # name -> (patterns, embedding_policy): only the planted texts are embedded
    "top": (["*"], "not embedded"),
    "overlay": (["governance/**"], "not embedded"),
    "planted": (["notes/**", "app/**", "docs/**"], "embedded"),
}


def path_map_text():
    """This repository's own path map, with ``NAMESPACES`` in place of its namespaces."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("decision_register", None)
    document["namespaces"] = {name: {"paths": patterns, **NAMESPACE_FIELDS, "embedding_policy": policy}
                              for name, (patterns, policy) in NAMESPACES.items()}
    return yaml.safe_dump(document, sort_keys=False)


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def commit(project, message="a change"):
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message)


def plant(project, corpus=None, extra=None):
    """A committed project: the corpus (plus ``extra``), the path map and the gitleaks rules."""
    project = Path(project)
    project.mkdir(parents=True)
    git(project, "init", "-q", "-b", "main")
    write(project, PATH_MAP_REL, path_map_text())
    shutil.copy2(REPO_ROOT / GITLEAKS_TEMPLATE_REL, project / ".gitleaks.toml")
    write(project, ".gitignore", ".gov-runtime/\n")
    for rel, text in {**(CORPUS if corpus is None else corpus), **(extra or {})}.items():
        write(project, rel, text)
    commit(project, "the planted corpus")
    return project


def clone(source, dest):
    git(None, "clone", "-q", "--no-hardlinks", str(source), str(dest), cwd=str(Path(dest).parent))
    return Path(dest)


def store_vectors(project):
    """The store's vectors, chunk id -> bytes, read from its plain table."""
    connection = sqlite3.connect((Path(project) / STORE_REL).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        return dict(connection.execute("SELECT chunk_id, embedding FROM semantic_vector"))
    finally:
        connection.close()


def store_manifest(project):
    connection = sqlite3.connect((Path(project) / STORE_REL).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        return connection.execute("SELECT * FROM semantic_manifest").fetchall()
    finally:
        connection.close()


def files_under(folder):
    folder = Path(folder)
    return sorted(path for path in folder.rglob("*") if path.is_file()) if folder.exists() else []


# --------------------------------------------------------------------------
# The driver: one child process running the public calls one after another
# --------------------------------------------------------------------------

_DRIVER = r'''
import json, sys
from gov.retrieval import semantic

request = json.loads(sys.stdin.read())
root, out = request["root"], []
for step in request["steps"]:
    try:
        if step["op"] == "refresh":
            value = semantic.refresh(root)
        elif step["op"] == "search":
            value = semantic.search(root, step["q"], refresh=False)
        else:
            vector, reason = semantic.query_vector(root, step["q"])
            value = {"vector": vector.hex() if vector else None, "reason": reason}
        out.append({"value": value, "error": None})
    except Exception as exc:
        out.append({"value": None, "error": f"{type(exc).__name__}: {exc}"})
sys.stdout.write("\n" + json.dumps(out, default=repr) + "\n")
'''


def refresh():
    return {"op": "refresh"}


def search(question):
    return {"op": "search", "q": question}


def query(question):
    return {"op": "qv", "q": question}


class Box:
    """A test's own folders and environment: a temporary HOME, XDG cache, TMPDIR and cache folder."""

    def __init__(self, workdir, stand_in):
        self.workdir, self.stand_in = Path(workdir), stand_in
        for name in ("home", "xdg-cache", "tmp", "pycache", "elsewhere", "site"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        self.cache_dir = self.workdir / "vector-cache"   # not created: the code creates it
        self.script = self.workdir / "w2_126_driver.py"
        self.script.write_text(_DRIVER, encoding="utf-8")
        self.site = self._link_sqlite_vec()
        # gitleaks may share a folder with ``ollama``, which PATH must not hold: it gets a folder of its own
        (self.workdir / "bin").mkdir(exist_ok=True)
        (self.workdir / "bin" / "gitleaks").symlink_to(shutil.which("gitleaks"))

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

    def env(self, cache_dir=None, use_setting=True, **extra):
        path = os.pathsep.join([str(self.workdir / "bin"), *(
            folder for folder in os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)
            if folder and not (Path(folder) / "ollama").exists())])
        env = {
            "PATH": path, "HOME": str(self.workdir / "home"), "XDG_CACHE_HOME": str(self.workdir / "xdg-cache"),
            "TMPDIR": str(self.workdir / "tmp"), "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": os.pathsep.join([str(SRC), *([str(self.site)] if self.site else [])]),
            "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
            "OLLAMA_HOST": self.stand_in.host, "GOV_QUERY_OLLAMA_HOST": self.stand_in.host,
            "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
        }
        if use_setting:
            env[CACHE_DIR_SETTING] = str(cache_dir or self.cache_dir)
        env.update({key: str(value) for key, value in extra.items()})
        return env

    def start(self, root, steps, env=None):
        process = subprocess.Popen([sys.executable, str(self.script)], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   env=env or self.env(), cwd=str(self.workdir / "elsewhere"))
        process.stdin.write(json.dumps({"root": str(root), "steps": steps}))
        process.stdin.close()
        process.stdin = None   # written and closed: ``communicate`` only reads
        return process

    @staticmethod
    def finish(process, timeout=CALL_TIMEOUT_S):
        try:
            out, err = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise AssertionError(f"the driver did not end within {timeout:.0f} s") from None
        assert process.returncode == 0, f"the driver failed (exit {process.returncode}):\n{err[-6000:]}"
        results = json.loads(out.strip().splitlines()[-1])
        for result in results:
            assert result["error"] is None, f"a public call raised: {result['error']}"
        return [result["value"] for result in results]

    def run(self, root, steps, env=None, timeout=CALL_TIMEOUT_S):
        return self.finish(self.start(root, steps, env), timeout)

    def build(self, root, env=None):
        """``semantic.refresh`` of ``root``, asserted available; its result."""
        [result] = self.run(root, [refresh()], env)
        assert result["available"], f"the vectors of {root} were not built: {result.get('reason')}"
        return result


def cache_entry(box, cache_dir=None):
    """The one file of the cache folder (KPI 1)."""
    files = files_under(cache_dir or box.cache_dir)
    assert len(files) == 1, f"the cache folder must hold one file, not {[str(path) for path in files]}"
    return files[0]


def counts(result):
    """The result's naming of the cache (README, interface): {"hits", "misses", "skipped"}."""
    assert RESULT_KEY in result, f"the result does not name the vector cache ({RESULT_KEY!r}): {sorted(result)}"
    return result[RESULT_KEY]
