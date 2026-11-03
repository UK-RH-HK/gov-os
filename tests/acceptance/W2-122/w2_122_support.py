"""Support code for the W2-122 acceptance tests: seeded rebuilds (DAEO-blwa, DEC-1014; KPI 5 moved to W2-124, DEC-1027 C).

The interface under test is public only (README, "The interface"):

- ``gov rebuild --json [--seed [<folder>]]``, run as ``sys.executable -m gov.cli.main rebuild ...``
  in a temporary repository built from scratch: its standard output (the API envelope), its exit code, its ``seed``
  object;
- the files it leaves under ``.gov-runtime/``: the shared store ``store.db`` (its lexical and semantic tables, read
  as data, never through private code) and the base's record ``.gov-runtime/rebuild/stores.json``;
- the project file ``governance/project/rebuild.yaml`` (W2-76's ``lock`` and ``slow_after_s``, and this ticket's
  ``integration_store``);
- the embedding endpoint at ``OLLAMA_HOST``: a stand-in on a loopback port that the case starts and stops, which
  records every text it is asked to embed.

**The code under test is whatever ``gov`` the pytest process imports (DEC-732).** Every child is started as
``sys.executable -m gov.cli.main`` with the pytest process's own ``PYTHONPATH`` (else the folder that holds the ``gov``
it imports); nothing of this worktree is written into a child's path. Merged into the ticket's worktree and run there
with that worktree's ``PYTHONPATH``, the cases exercise the ticket's code.

What the environment of every child holds: an empty ``HOME``; the real ``gitleaks`` linked into a tools folder first
on ``PATH``; no code-graph tool (left off ``PATH``, as W2-76 does: the code index reports itself not recreated and no
daemon starts); no ``ollama`` program (``GOV_OLLAMA_BIN`` names a path that does not exist); no secrets cache
(``GOV_SECRETS_CACHE`` empty); a ``rebuild.yaml`` whose lock is a temporary path (no case takes the machine's lock).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import site
import sqlite3
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
GITLEAKS_TEMPLATE = REPO_ROOT / "template/.gitleaks.toml"
PATH_MAP_TEMPLATE = REPO_ROOT / "template/governance/project/path-map.yaml"
EVIDENCE_REL = "docs/changes/W2-122-evidence.md"

REAL_GITLEAKS = shutil.which("gitleaks")
GIT = shutil.which("git")

SETTINGS_REL = "governance/project/rebuild.yaml"
STORE_REL = ".gov-runtime/store.db"
RECORD_REL = ".gov-runtime/rebuild/stores.json"
RUNTIME_REL = ".gov-runtime"

SEEDED, REFUSED, NONE = "seeded", "refused", "none"
EMBED_MODEL = "qwen3-embedding:0.6b"
EMBED_REVISION = "ac6da0dfba84"   # the pin of ADR-0002 §2: the stand-in's digest begins so by default
OTHER_REVISION = "0123456789ab"   # another revision of the same model: an endpoint that reports another digest

COMMAND_TIMEOUT_S = 300.0


def gov_src():
    """The folder that holds the ``gov`` package this pytest process imports: the code under test (DEC-732)."""
    spec = importlib.util.find_spec("gov")
    if spec is None or not spec.origin:
        raise AssertionError("no gov package can be imported: set PYTHONPATH to the worktree's src/ (README)")
    return Path(spec.origin).resolve().parents[1]


def python_path():
    """Every child's PYTHONPATH: the pytest process's own (DEC-732), else the folder of the ``gov`` it imports."""
    return os.environ.get("PYTHONPATH") or str(gov_src())


def lacking():
    """Why a rebuild that builds vectors cannot run on this machine, or None."""
    if REAL_GITLEAKS is None or GIT is None:
        return "gitleaks or git is not on PATH: the rebuild cannot run its stages"
    if importlib.util.find_spec("sqlite_vec") is None:
        return "sqlite_vec cannot be imported: the semantic store cannot hold a vector (ADR-0002)"
    return None


# --------------------------------------------------------------------------
# The stand-in embedder: Ollama's HTTP interface on a loopback port
# --------------------------------------------------------------------------

DIMENSIONS = 1024
_STOP = {"the", "and", "for", "with", "that", "this", "each", "does", "when", "who", "what", "into", "from"}


def stand_in_vector(text, salt=""):
    """A unit vector made of the words of ``text`` (and the endpoint's ``salt``: two endpoints with other salts give
    other vectors for the same text, so a store that mixes two embedders is seen in its vectors)."""
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"[a-z0-9]+", str(text).lower()):
        if len(word) < 3 or word in _STOP:
            continue
        digest = hashlib.sha256((salt + word).encode()).digest()
        vector[int.from_bytes(digest[:4], "big") % DIMENSIONS] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        vector[0], norm = 1.0, 1.0
    return [value / norm for value in vector]


class OllamaStandIn:
    """A healthy Ollama endpoint on a free loopback port. It reports ``model`` with a digest that begins with
    ``revision``, embeds with vectors made of words and ``salt``, and records every text it is asked to embed."""

    def __init__(self, revision=EMBED_REVISION, model=EMBED_MODEL, salt=""):
        self.revision, self.model, self.salt = revision, model, salt
        self.digest = revision + hashlib.sha256(f"w2-122 stand-in {revision}".encode()).hexdigest()[:52]
        self.embedded = []        # every text asked to be embedded, in order
        self.lock = threading.Lock()
        stand_in = self
        entry = {"name": model, "model": model, "digest": self.digest, "size": 639150000,
                 "details": {"family": "qwen3", "parameter_size": "595.78M", "quantization_level": "Q8_0"}}

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
                if route == "/api/version":
                    reply = {"version": "0.35.0"}
                elif route == "/api/tags":
                    reply = {"models": [entry]}
                elif route == "/api/ps":
                    # Rewrite-Reason: W2-32's S10 (DEC-1065): the model on the GPU
                    reply = {"models": [{**entry, "size_vram": entry["size"]}]}
                elif route == "/api/show":
                    reply = {"details": entry["details"],
                             "model_info": {"general.architecture": "qwen3", "qwen3.embedding_length": DIMENSIONS},
                             "capabilities": ["embedding"]}
                elif route in ("/api/embed", "/api/embeddings"):
                    given = asked.get("input", asked.get("prompt", ""))
                    texts = [given] if isinstance(given, str) else list(given)
                    with stand_in.lock:
                        stand_in.embedded.extend(str(text) for text in texts)
                    if route == "/api/embed":
                        reply = {"model": model, "embeddings": [stand_in_vector(t, stand_in.salt) for t in texts],
                                 "total_duration": 1, "load_duration": 1, "prompt_eval_count": len(texts)}
                    else:
                        reply = {"embedding": stand_in_vector(texts[0] if texts else "", stand_in.salt)}
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

    def forget(self):
        """Start a new count: the texts and requests recorded so far are dropped."""
        with self.lock:
            self.embedded.clear()

    def sent(self):
        """Every text sent to be embedded since the last ``forget``, as one text."""
        with self.lock:
            return "\n".join(self.embedded)

    def close(self):
        self.server.shutdown()
        self.server.server_close()


# --------------------------------------------------------------------------
# The environment of every child
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Box:
    base: Path
    home: Path
    tmpdir: Path
    tools: Path
    pycache: Path
    lock: Path


def make_box(base):
    base = Path(base).resolve()
    box = Box(base, base / "home", base / "systmp", base / "tools", base / "pycache", base / "locks" / "rebuild.lock")
    for folder in (box.home, box.tmpdir, box.tools, box.pycache, box.lock.parent):
        folder.mkdir(parents=True, exist_ok=True)
    if not (box.tools / "gitleaks").exists():
        (box.tools / "gitleaks").symlink_to(REAL_GITLEAKS)
    return box


def environment(box, host):
    """The rebuild's environment, from scratch, with the embedding endpoint at ``host``."""
    path = os.pathsep.join([str(box.tools), str(Path(sys.executable).parent), "/usr/bin", "/bin"])
    return {
        "PATH": path,
        "HOME": str(box.home),
        "TMPDIR": str(box.tmpdir),
        "XDG_CACHE_HOME": str(box.home / ".cache"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONPATH": python_path(),
        "PYTHONUSERBASE": site.getuserbase(),
        "PYTHONPYCACHEPREFIX": str(box.pycache),
        "PYTHONDONTWRITEBYTECODE": "1",
        "OLLAMA_HOST": host,
        "GOV_QUERY_OLLAMA_HOST": host,
        "GOV_OLLAMA_BIN": str(box.base / "no-ollama-here"),
        "GOV_SECRETS_CACHE": "",
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "W2-122 acceptance", "GIT_AUTHOR_EMAIL": "w2-122@example.invalid",
        "GIT_COMMITTER_NAME": "W2-122 acceptance", "GIT_COMMITTER_EMAIL": "w2-122@example.invalid",
    }


# --------------------------------------------------------------------------
# A planted repository: a base at one commit, a tree at a later one
# --------------------------------------------------------------------------

def git(directory, *args):
    proc = subprocess.run([GIT, "-C", str(directory), "-c", "user.name=W2-122 acceptance",
                           "-c", "user.email=w2-122@example.invalid", "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, check=False, timeout=60,
                          env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull})
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {directory}: {proc.stderr.strip()}")
    return proc.stdout


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def path_map_text():
    import yaml

    document = yaml.safe_load(PATH_MAP_TEMPLATE.read_text(encoding="utf-8"))
    document.setdefault("namespaces", {})["docs"] = {
        "paths": ["docs/**"],
        "memory_class": "governance",
        "sensitivity": "internal",
        "permitted_roles": ["engineer", "independent-test-designer", "independent-auditor", "orchestrator",
                            "product-spec", "research"],
        "retention": "kept in git history",
        "export_policy": "allowed",
        "embedding_policy": "embedded",
        "provenance": "written by the W2-122 tests",
        "deletion_rebuild": "authoritative; restored from git only",
    }
    return yaml.safe_dump(document, sort_keys=False)


def settings_text(lock, integration_store=None):
    text = f"slow_after_s: 600\nlock: {json.dumps(str(lock))}\n"
    if integration_store is not None:
        text += f"integration_store: {json.dumps(str(integration_store))}\n"
    return text


def note(word, extra=""):
    """A note whose words are its own: ``word`` appears in no other file, so a text sent to be embedded that holds it
    came from this file."""
    return (f"# The {word} note\n\nThe {word} ledger is kept in the {word} drawer beside the harbour.\n"
            f"Every {word} entry is copied twice by the {word} clerk.{extra}\n")


# The base's files (commit 1) and the tree's (commit 2): one kept, one changed, one removed, one added.
KEPT, KEPT_TOO, CHANGED, REMOVED, ADDED = "docs/kept.md", "docs/kept-too.md", "docs/changed.md", "docs/removed.md", \
    "docs/added.md"
WORDS = {KEPT: "quillwort", KEPT_TOO: "marjoram", CHANGED: "bergamot", REMOVED: "sorrel", ADDED: "fenugreek"}
CHANGED_WORD = "tamarind"   # the changed file's new word: in the tree only
BASE_FILES = {KEPT: note(WORDS[KEPT]), KEPT_TOO: note(WORDS[KEPT_TOO]), CHANGED: note(WORDS[CHANGED]),
              REMOVED: note(WORDS[REMOVED])}
TREE_FILES = {KEPT: note(WORDS[KEPT]), KEPT_TOO: note(WORDS[KEPT_TOO]),
              CHANGED: note(WORDS[CHANGED], f"\nThe {CHANGED_WORD} entry was added later by the {CHANGED_WORD} clerk."),
              ADDED: note(WORDS[ADDED])}


def make_base(box, name="base", settings=None):
    """The base repository at commit 1: the path map, the rules, ``rebuild.yaml`` and the base's files."""
    project = box.base / name
    project.mkdir(parents=True)
    write(project / ".gitignore", ".gov-runtime/\n__pycache__/\n")
    shutil.copy2(GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    write(project / "governance/project/path-map.yaml", path_map_text())
    write(project / SETTINGS_REL, settings if settings is not None else settings_text(box.lock))
    for rel, text in BASE_FILES.items():
        write(project / rel, text)
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "W2-122 base")
    return project


def make_tree(box, base, name="tree", integration_store=None):
    """A clone of the (temporary) base, moved on to commit 2: one file changed, one removed, one added; its
    ``rebuild.yaml`` names ``integration_store`` where one is given. No store: ``.gov-runtime/`` is not cloned."""
    tree = box.base / name
    git(box.base, "clone", "-q", str(base), str(tree))
    for rel in BASE_FILES:
        if rel not in TREE_FILES:
            (tree / rel).unlink()
    for rel, text in TREE_FILES.items():
        write(tree / rel, text)
    if integration_store is not None:
        write(tree / SETTINGS_REL, settings_text(box.lock, integration_store))
    git(tree, "add", "-A")
    git(tree, "commit", "-q", "-m", "W2-122 tree: one changed, one removed, one added")
    assert not (tree / RUNTIME_REL).exists()
    return tree


def set_settings(project, text):
    write(Path(project) / SETTINGS_REL, text)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "rebuild.yaml changed")


# --------------------------------------------------------------------------
# Running a rebuild
# --------------------------------------------------------------------------

@dataclass
class Run:
    args: tuple
    returncode: int | None
    stdout: str
    stderr: str
    seconds: float

    def envelope(self):
        try:
            return json.loads(self.stdout)
        except ValueError:
            return {}

    @property
    def ok(self):
        return self.returncode == 0 and self.envelope().get("ok") is True

    @property
    def result(self):
        return self.envelope().get("result") or {}

    def describe(self, tail=3000):
        return (f"{' '.join(self.args)}\nexit code: {self.returncode} after {self.seconds:.1f} s\n"
                f"stdout:\n{self.stdout[-tail:]}\nstderr:\n{self.stderr[-tail:]}")


def rebuild(project, env, *extra, timeout=COMMAND_TIMEOUT_S):
    """``gov rebuild --json <extra>`` in ``project``, run as ``sys.executable -m gov.cli.main`` (DEC-732)."""
    argv = (sys.executable, "-m", "gov.cli.main", "rebuild", "--json", *extra)
    began = time.monotonic()
    try:
        done = subprocess.run(argv, cwd=str(project), env=env, stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, timeout=timeout)
        code, out, err = done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired as exc:
        code = None
        out = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    return Run(argv[3:], code, out, err, time.monotonic() - began)


def built(project, env, *extra):
    """A rebuild that must succeed: its run."""
    run = rebuild(project, env, *extra)
    assert run.ok, f"the rebuild did not succeed\n{run.describe()}"
    return run


def seed_of(run):
    """The rebuild's ``seed`` object (an empty dict where it gives none)."""
    seed = run.result.get("seed")
    return seed if isinstance(seed, dict) else {}


def remove_store(project):
    """Remove the tree's derived state, so that the next rebuild of the same tree is cold."""
    shutil.rmtree(Path(project) / RUNTIME_REL, ignore_errors=False)


# --------------------------------------------------------------------------
# The base's record
# --------------------------------------------------------------------------

def read_record(project):
    path = Path(project) / RECORD_REL
    assert path.is_file(), f"the full rebuild wrote no record at {RECORD_REL} in {project}"
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise AssertionError(f"{RECORD_REL} is not JSON: {exc}") from None
    assert isinstance(record, dict), f"{RECORD_REL} is not a JSON object: {record!r}"
    return record


def change_record(project, change):
    """Change one value of the base's record: ``change(record)`` edits the parsed object, which is written back."""
    record = read_record(project)
    change(record)
    (Path(project) / RECORD_REL).write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")


# --------------------------------------------------------------------------
# The store, entry for entry
# --------------------------------------------------------------------------

def _connect(project):
    path = Path(project) / STORE_REL
    assert path.is_file(), f"no store at {path}"
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        import sqlite_vec

        connection.enable_load_extension(True)
        sqlite_vec.load(connection)
        connection.enable_load_extension(False)
    except Exception:   # a store without a virtual vector table reads without it
        pass
    return connection


def _value(value):
    if isinstance(value, (bytes, memoryview)):
        return "sha256:" + hashlib.sha256(bytes(value)).hexdigest()
    if isinstance(value, float):
        return repr(value)
    return value


def _table_rows(connection, table):
    """The table's columns and rows, but an INTEGER PRIMARY KEY column (a row number, ``lexical_chunk.id``): an
    incremental rebuild may number its rows otherwise than a cold one, and the number is no entry of the store."""
    info = list(connection.execute(f'PRAGMA table_info("{table}")'))
    columns = [row[1] for row in info if not (row[5] and str(row[2]).upper() == "INTEGER")]
    listed = ", ".join(f'"{column}"' for column in columns)
    rows = connection.execute(f'SELECT {listed} FROM "{table}"').fetchall()
    return columns, sorted(json.dumps([_value(value) for value in row], default=str) for row in rows)


# The tables of the shared store that are the lexical and semantic stores (W1-27's names), read as data.
STORE_TABLE_PREFIXES = ("lexical_", "semantic_")


def store_tables(project):
    """Every lexical and semantic table of the store (not the internal tables of a virtual table), by name:
    ``(columns, sorted rows)``; a blob is given by its sha256, so equal vectors give equal rows."""
    connection = _connect(project)
    try:
        names = [row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
        shadows = {name for name in names for other in names
                   if other != name and name.startswith(other + "_")
                   and connection.execute("SELECT sql FROM sqlite_master WHERE name = ?", (other,)).fetchone()[0]
                   .upper().startswith("CREATE VIRTUAL")}
        return {name: _table_rows(connection, name) for name in names
                if name.startswith(STORE_TABLE_PREFIXES) and name not in shadows}
    finally:
        connection.close()


def vector_count(project):
    connection = _connect(project)
    try:
        if connection.execute("SELECT 1 FROM sqlite_master WHERE name = 'semantic_vector'").fetchone() is None:
            return 0
        return connection.execute("SELECT COUNT(*) FROM semantic_vector").fetchone()[0]
    finally:
        connection.close()


def diff_tables(seeded, cold):
    """What differs between two ``store_tables`` answers, in words (empty where they are equal)."""
    lines = []
    for name in sorted(set(seeded) | set(cold)):
        if name not in seeded or name not in cold:
            lines.append(f"table {name}: only in the {'seeded' if name in seeded else 'cold'} store")
            continue
        (s_cols, s_rows), (c_cols, c_rows) = seeded[name], cold[name]
        if s_cols != c_cols:
            lines.append(f"table {name}: columns {s_cols} seeded, {c_cols} cold")
        only_s, only_c = sorted(set(s_rows) - set(c_rows)), sorted(set(c_rows) - set(s_rows))
        if only_s or only_c or len(s_rows) != len(c_rows):
            lines.append(f"table {name}: {len(s_rows)} rows seeded, {len(c_rows)} cold; "
                         f"{len(only_s)} only seeded (first: {only_s[:1]}), {len(only_c)} only cold "
                         f"(first: {only_c[:1]})")
    return lines


def snapshot(project, run):
    """What a rebuild built, to compare a seeded rebuild with a cold one: the digest, the stores' outcomes (but the
    seed's), and every lexical and semantic table, row for row."""
    stores = {name: value for name, value in (run.result.get("stores") or {}).items()}
    return {"digest": run.result.get("digest"), "stores": stores, "tables": store_tables(project)}


def assert_same_store(seeded, cold):
    """The seeded store is the cold store, entry for entry (K1, the failure line)."""
    assert seeded["digest"] == cold["digest"], \
        f"the seeded rebuild's digest {seeded['digest']!r} is not the cold rebuild's {cold['digest']!r}"
    assert seeded["stores"] == cold["stores"], \
        f"the stores' outcomes differ:\nseeded: {seeded['stores']}\ncold:   {cold['stores']}"
    differences = diff_tables(seeded["tables"], cold["tables"])
    assert not differences, "the seeded store is not the cold store, entry for entry:\n" + "\n".join(differences)
