"""Support code for the W2-108 acceptance tests (DAEO-zoex; standard library and PyYAML only).

W2-108 (DEC-969, DEC-966 item 4): within one process, the semantic store's status and the lexical index's
freshness are worked out once per store and tree and reused by every later retrieval call; every answer stays
the same; a change of the store, of a file or of the head is still seen.

How the tests run (README, "How the suite chooses the code under test"):

- **The code under test is whatever ``PYTHONPATH`` gives the pytest process.** ``GOV_SRC`` is the folder that
  holds the ``gov`` package the pytest process imports; every child process gets that folder (and nothing of
  this worktree hard-coded) on its ``PYTHONPATH``.
- **Through public interfaces only:** ``gov.retrieval.lexical.search``/``freshness``/``refresh``,
  ``gov.retrieval.semantic.search``/``refresh``, ``gov.retrieval.retrieve.retrieve`` and
  ``gov.context.context``. Each scenario runs in one child process, through a small driver written to a
  temporary folder, that makes the calls one after another (and, between them, edits files, commits, or starts
  another process that rebuilds the store).
- **The work is counted through its public effects:** the driver installs a Python audit hook
  (``sys.addaudithook``) and records, per call, every ``git`` command the process starts and every ``open`` of
  the path map. Nothing private is named or patched.
- **Every project is a temporary git repository built from scratch** in pytest's ``tmp_path``: single named
  files of this worktree only (the path map, the template's gitleaks rules), never a folder, never a clone.
- **No network:** the embedder is a stand-in on the loopback interface; ``PATH`` holds no ``ollama``; ``HOME``
  is empty. ``sqlite_vec`` is linked into a folder of its own when this machine has it (as W1-19 does).
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

# The worktree the tests run in: the single named files they read (the path map, the gitleaks rules), and its store.
REPO_ROOT = Path(__file__).resolve().parents[3]


def gov_src():
    """The folder that holds the ``gov`` package this pytest process imports: the code under test (DEC-732)."""
    spec = importlib.util.find_spec("gov")
    if spec is None or not spec.origin:
        raise AssertionError("no gov package can be imported: set PYTHONPATH to the worktree's src/ (README)")
    return Path(spec.origin).resolve().parents[1]


GOV_SRC = gov_src()

LEXICAL = "gov.retrieval.lexical"
SEMANTIC = "gov.retrieval.semantic"
RETRIEVE = "gov.retrieval.retrieve"
CONTEXT = "gov.context"
STORE = "gov.store"

STORE_REL = ".gov-runtime/store.db"
PATH_MAP_REL = "governance/project/path-map.yaml"
PATH_MAP_NAME = "path-map.yaml"
CONFIG_REL = ".gitleaks.toml"
TEMPLATE_CONFIG_REL = "template/.gitleaks.toml"

AVAILABLE, UNAVAILABLE = "AVAILABLE", "FACET_UNAVAILABLE"
FRESH, STALE = "fresh", "stale"
CALL_TIMEOUT_S = 600.0
EMBED_MODEL = "qwen3-embedding:0.6b"
EMBED_REVISION = "ac6da0dfba84"   # the pin of ADR-0002 §2: the stand-in's model list reports a digest beginning so
NO_RERANK = "none"                # the driver passes a reranker that does not rerank (the rerank is not under test)

# git commands that list or hash the tracked files: the work of a freshness or status check, seen from outside.
# A command that only asks git whether anything changed (``status``, ``diff-files``, ``rev-parse``, or
# ``ls-files`` with a filter that lists only changed files) is a probe, not that work, and is not counted.
LISTING = "ls-files"
HASHING = ("hash-object",)
PROBE_FILTERS = ("-m", "--modified", "-d", "--deleted", "-o", "--others", "-u", "--unmerged", "-k", "--killed")


# --------------------------------------------------------------------------
# What a case needs from this machine
# --------------------------------------------------------------------------

def lacking_gitleaks():
    """The lexical index judges every file with gitleaks (DEC-287): without it no index can be built."""
    return None if shutil.which("gitleaks") else "no gitleaks executable on PATH: the lexical index cannot be built"


def lacking_sqlite_vec():
    if importlib.util.find_spec("sqlite_vec") is None:
        return "sqlite_vec cannot be imported: the semantic facet cannot store or compare a vector (ADR-0002)"
    return None


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------

BASE_DATE = "2026-09-01T12:00:00+00:00"
LATER = "2026-09-02T12:00:00+00:00"


def git_env(project, date=BASE_DATE):
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(project),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W2-108 tests", "GIT_AUTHOR_EMAIL": "w2-108@example.invalid",
        "GIT_COMMITTER_NAME": "W2-108 tests", "GIT_COMMITTER_EMAIL": "w2-108@example.invalid",
        "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
    }


def git(project, *args, date=BASE_DATE):
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True,
                          env=git_env(project, date))
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


# --------------------------------------------------------------------------
# The planted repository
# --------------------------------------------------------------------------

EMBEDDED, NOT_EMBEDDED = "embedded", "not embedded"
_NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history",
    "export_policy": "allowed",
    "provenance": "written by the W2-108 tests",
    "deletion_rebuild": "authoritative; restored from git only",
}
# name -> (patterns, memory_class, embedding_policy)
NAMESPACES = {
    "top": (["*"], "governance", NOT_EMBEDDED),
    "overlay": (["governance/**"], "governance", NOT_EMBEDDED),
    "notes": (["notes/**"], "governance", EMBEDDED),
    "code": (["app/**"], "governance", EMBEDDED),
}

PHRASE = "amber lantern protocol"
LANTERN = "app/lantern.txt"
MARKER = "notes/marker.md"
ZETA = "notes/zeta.md"
BAKERY = "notes/bakery.md"
TIDES = "notes/tides.md"
POOL = "app/pool.py"
README = "README.md"
# A phrase no file holds until a test writes it: found only once the change is seen and the index rebuilt.
NEW_PHRASE = "cobalt heron signal"
NEW_FILE = "notes/heron.md"
NEW_TEXT = f"# Heron\n\nThe {NEW_PHRASE} is raised at noon over the cobalt heron pier.\n"

CORPUS = {
    README: "# A project\n\nOrdinary text about the project.\n",
    LANTERN: f"The {PHRASE} is posted beside the door.\n",
    MARKER: f"# Marker\n\nThe {PHRASE} begins at dusk.\nThe {PHRASE} ends at dawn.\n",
    ZETA: f"# Zeta\n\nA long note on stores, shelves and ropes, which mentions the {PHRASE} once, in passing.\n",
    BAKERY: ("# Bakery\n\nSourdough loaves proof overnight in the cold room.\n"
             "The baker scores each loaf before it goes into the oven.\n"),
    TIDES: ("# Tides\n\nThe harbour pilot reads the tide tables at dawn.\n"
            "The spring tide height is logged in the harbour book.\n"),
    POOL: ('"""Connection pool."""\n\n\ndef drain(pool):\n    """Empty the pool and close every connection."""\n'
           "    for connection in pool:\n        connection.close()\n    return []\n"),
}
GITIGNORE = ".gov-runtime/\n"

# Questions: an exact phrase (the lexical route finds it), two the vectors must find, one nothing holds.
QUESTIONS = (PHRASE, "when does the baker score each sourdough loaf", "who reads the tide tables at the harbour",
             "zebra quasar nothing")


def path_map_text(namespaces=NAMESPACES):
    """A full path map (DEC-225): this worktree's own, with ``namespaces`` in place of its namespaces."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("decision_register", None)   # the project holds no register file
    document["namespaces"] = {}
    for name, (patterns, memory_class, policy) in namespaces.items():
        document["namespaces"][name] = {"paths": list(patterns), "memory_class": memory_class,
                                        **_NAMESPACE_FIELDS, "embedding_policy": policy}
    return yaml.safe_dump(document, sort_keys=False)


def plant(project, *, with_commit=True):
    """The planted repository: the corpus, the path map and the rules, committed (or only staged)."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    write(project, PATH_MAP_REL, path_map_text())
    shutil.copy2(REPO_ROOT / TEMPLATE_CONFIG_REL, project / CONFIG_REL)
    write(project, ".gitignore", GITIGNORE)
    for rel, text in CORPUS.items():
        write(project, rel, text)
    if with_commit:
        commit(project, "the planted corpus", BASE_DATE)
    else:
        git(project, "add", "-A")
    return project


# --------------------------------------------------------------------------
# The stand-in embedder: Ollama's HTTP interface on a loopback port, vectors computed from words
# --------------------------------------------------------------------------

DIMENSIONS = 1024
STAND_IN_DIGEST = EMBED_REVISION + hashlib.sha256(b"w2-108 stand-in").hexdigest()[:52]
_STOP = {"the", "and", "for", "with", "that", "this", "each", "does", "when", "who", "what", "into", "from",
         "its", "are", "was", "has", "have", "before", "after", "then", "any", "all", "given", "query",
         "instruct", "retrieve", "relevant", "passages", "search", "web", "answer", "document"}


def stand_in_vector(text):
    """A unit vector made of the words of ``text``: texts that share words are near each other."""
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"[a-z0-9]+", str(text).lower()):
        if len(word) < 3 or word in _STOP:
            continue
        digest = hashlib.sha256(word.encode()).digest()
        vector[int.from_bytes(digest[:4], "big") % DIMENSIONS] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        vector[0], norm = 1.0, 1.0
    return [value / norm for value in vector]


class OllamaStandIn:
    """A healthy Ollama endpoint on a free loopback port, reporting the model wholly on the CPU (DEC-798)."""

    def __init__(self):
        self.requests = []
        requests = self.requests
        model = {"name": EMBED_MODEL, "model": EMBED_MODEL, "digest": STAND_IN_DIGEST, "size": 639150000,
                 "details": {"family": "qwen3", "parameter_size": "595.78M", "quantization_level": "Q8_0"}}

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
                requests.append({"method": self.command, "path": self.path})
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
                    reply = {"models": [{**model, "size_vram": 0}]}
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

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def free_port():
    with socket.socket() as handle:
        handle.bind(("127.0.0.1", 0))
        return handle.getsockname()[1]


# --------------------------------------------------------------------------
# The driver: one process, a list of steps, and what each call did
# --------------------------------------------------------------------------

_DRIVER = r'''
"""W2-108's driver (acceptance tests only): runs steps in one process and records, per call, the git commands it
started and the opens of the path map, through a Python audit hook."""
import importlib
import json
import os
import subprocess
import sys

_EFFECTS = []
_WATCHED = os.environ.get("W2108_WATCHED", "path-map.yaml")


def _text(value):
    try:
        return os.fsdecode(value)
    except TypeError:
        return str(value)


def _hook(event, args):
    try:
        if event == "subprocess.Popen":
            argv = args[1]
            argv = [argv] if isinstance(argv, (str, bytes, os.PathLike)) else list(argv or [])
            argv = [_text(part) for part in argv]
            program = _text(args[0]) if args[0] is not None else (argv[0] if argv else "")
            if os.path.basename(program) == "git" or (argv and os.path.basename(argv[0]) == "git"):
                _EFFECTS.append({"git": argv[1:]})
        elif event == "open":
            path = args[0]
            if isinstance(path, (str, bytes, os.PathLike)) and os.path.basename(_text(path)) == _WATCHED:
                _EFFECTS.append({"open": _text(path)})
    except Exception:
        pass


sys.addaudithook(_hook)


def _no_reranker():
    return None


def _call(step, root):
    module = importlib.import_module(step["module"])
    function = getattr(module, step["function"])
    args = [root if arg == "{root}" else arg for arg in step.get("args", [])]
    kwargs = dict(step.get("kwargs", {}))
    if kwargs.get("reranker") == "none":
        kwargs["reranker"] = _no_reranker
    return function(*args, **kwargs)


def main():
    request = json.loads(sys.stdin.read())
    root = request["root"]
    results = []
    for step in request["steps"]:
        op = step["op"]
        if op == "call":
            start = len(_EFFECTS)
            try:
                value, error = _call(step, root), None
            except Exception as exc:  # reported, never hidden: a test decides what an error means
                value, error = None, f"{type(exc).__name__}: {exc}"
            results.append({"op": op, "value": value, "error": error, "effects": _EFFECTS[start:]})
        elif op == "write":
            path = os.path.join(root, step["rel"])
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(step["text"])
            results.append({"op": op})
        elif op == "remove":
            os.remove(os.path.join(root, step["rel"]))
            results.append({"op": op})
        elif op in ("git", "external"):
            if op == "git":
                argv, env = ["git", "-C", root, *step["args"]], {**os.environ, **step.get("env", {})}
                done = subprocess.run(argv, capture_output=True, text=True, env=env)
            else:  # another process: a fresh driver with its own steps (a rebuild of the store, for example)
                done = subprocess.run([sys.executable, os.path.abspath(__file__)], capture_output=True, text=True,
                                      input=json.dumps({"root": root, "steps": step["steps"]}))
            if done.returncode != 0:
                raise SystemExit(f"{op} step failed: {step}\n{done.stdout}\n{done.stderr}")
            results.append({"op": op, "out": done.stdout[-20000:]})
    sys.stdout.write("\n" + json.dumps(results, default=repr, sort_keys=True) + "\n")


main()
'''


def call(module, function, *args, **kwargs):
    """A step: one call of a public function; ``"{root}"`` stands for the project root."""
    return {"op": "call", "module": module, "function": function, "args": list(args), "kwargs": kwargs}


def lexical_search(query):
    return call(LEXICAL, "search", "{root}", query, refresh=False)


def lexical_freshness():
    return call(LEXICAL, "freshness", "{root}")


def semantic_search(query):
    return call(SEMANTIC, "search", "{root}", query, refresh=False)


def retrieve(query, **kwargs):
    return call(RETRIEVE, "retrieve", "{root}", query, reranker=NO_RERANK, **kwargs)


def edit(rel, text):
    return {"op": "write", "rel": rel, "text": text}


def remove(rel):
    return {"op": "remove", "rel": rel}


def git_step(*args, date=LATER):
    return {"op": "git", "args": list(args), "env": {
        "GIT_AUTHOR_NAME": "W2-108 tests", "GIT_AUTHOR_EMAIL": "w2-108@example.invalid",
        "GIT_COMMITTER_NAME": "W2-108 tests", "GIT_COMMITTER_EMAIL": "w2-108@example.invalid",
        "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}}


def build_steps(semantic=True, records=True):
    """The calls that build the store: the record graph of ``HEAD`` (with its fingerprints row), the lexical index
    and, with ``semantic``, the vectors."""
    return ([call(STORE, "load", "{root}")] if records else []) + [call(LEXICAL, "refresh", "{root}")] \
        + ([call(SEMANTIC, "refresh", "{root}")] if semantic else [])


def rebuild(semantic=True, records=True):
    """A step: another process rebuilds the store (see ``build_steps``)."""
    return {"op": "external", "steps": build_steps(semantic, records)}


class Driver:
    """Runs a list of steps in one new process and returns the call results (``Calls``)."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "site"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        self.site = self._link_sqlite_vec()
        self.script = self.workdir / "w2_108_driver.py"
        self.script.write_text(_DRIVER, encoding="utf-8")
        self.dead_host = f"127.0.0.1:{free_port()}"

    def _link_sqlite_vec(self):
        """A folder that links the one ``sqlite_vec`` this machine's Python imports (the scratch HOME has no user
        site folder to find it in), as W1-19 does; None when it imports none."""
        spec = importlib.util.find_spec("sqlite_vec")
        if spec is None or not spec.origin:
            return None
        origin = Path(spec.origin)
        source = origin.parent if spec.submodule_search_locations else origin
        link = self.workdir / "site" / source.name
        if not link.is_symlink():
            link.symlink_to(source, target_is_directory=source.is_dir())
        return self.workdir / "site"

    def env(self, host=None, **extra):
        """Built from scratch: an empty HOME, no ``ollama`` on PATH, the embedder at ``host`` (else a dead port)."""
        path = os.pathsep.join(folder for folder in os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)
                               if folder and not (Path(folder) / "ollama").exists())
        return {
            "PATH": path,
            "HOME": str(self.workdir / "home"),
            "TMPDIR": str(self.workdir / "tmp"),
            "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": os.pathsep.join([str(GOV_SRC), *([str(self.site)] if self.site else [])]),
            "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
            "OLLAMA_HOST": host or self.dead_host,
            "GOV_QUERY_OLLAMA_HOST": host or self.dead_host,
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            **extra,
        }

    def run(self, root, steps, *, env=None, host=None, timeout=CALL_TIMEOUT_S):
        request = {"root": str(root), "steps": steps}
        try:
            done = subprocess.run([sys.executable, str(self.script)], input=json.dumps(request),
                                  env=env if env is not None else self.env(host),
                                  cwd=str(self.workdir / "elsewhere"), capture_output=True, text=True,
                                  timeout=timeout)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"the driver did not end within {timeout:.0f} s") from None
        assert done.returncode == 0, f"the driver failed (exit code {done.returncode}):\n{done.stderr[-6000:]}"
        try:
            results = json.loads(done.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            raise AssertionError(f"the driver returned no JSON:\n{done.stdout[-4000:]}\n{done.stderr[-4000:]}") \
                from None
        return Calls([result for result in results if result["op"] == "call"])


def build(driver, project, host, semantic=True, records=True):
    """Build the store of ``project`` in a process of its own and check that every part was built."""
    values = driver.run(project, build_steps(semantic, records), host=host).values()
    if semantic:
        assert values[-1]["available"], f"the vectors were not built: {values[-1]}"
    return values


class Calls(list):
    """The results of the call steps, in order."""

    def values(self):
        for result in self:
            assert result["error"] is None, f"a call raised: {result['error']}"
        return [result["value"] for result in self]


# --------------------------------------------------------------------------
# Reading the effects of a call
# --------------------------------------------------------------------------

def subcommand(argv):
    """The git subcommand of ``argv`` (the words after ``git``) and the words after it."""
    words = list(argv)
    index = 0
    while index < len(words):
        word = words[index]
        if word in ("-C", "-c", "--git-dir", "--work-tree", "--namespace"):
            index += 2
            continue
        if word.startswith("-"):
            index += 1
            continue
        return word, words[index + 1:]
    return "", []


def listing_work(effects):
    """The git commands among ``effects`` that list every tracked file or hash the tracked files' content."""
    work = []
    for effect in effects:
        if "git" not in effect:
            continue
        name, rest = subcommand(effect["git"])
        if name == LISTING and not any(word in PROBE_FILTERS for word in rest):
            work.append(effect["git"])
        elif name in HASHING:
            work.append(effect["git"])
    return work


def path_map_reads(effects):
    return [effect["open"] for effect in effects if "open" in effect]


def work_of(result):
    """What one call did of a freshness or status check: (listing and hashing commands, path-map reads)."""
    return len(listing_work(result["effects"])), len(path_map_reads(result["effects"]))


def describe_effects(calls):
    lines = []
    for number, result in enumerate(calls, 1):
        listing, reads = work_of(result)
        commands = [" ".join(effect["git"][:6]) for effect in result["effects"] if "git" in effect]
        lines.append(f"call {number}: {listing} listing/hashing git command(s), {reads} path-map read(s); "
                     f"git: {commands}")
    return "\n".join(lines)


def facet(answer):
    return answer["available"], answer["state"], answer["reason"]


# --------------------------------------------------------------------------
# This repository's store
# --------------------------------------------------------------------------

STORE_ROOT_SETTING = "W2108_STORE_ROOT"
# Exact strings this repository holds (the lexical route finds them) and questions for the vectors.
REPO_QUESTIONS = ("freshness", "DEC-969", "stopping_reason",
                  "how does retrieval decide that the lexical index is stale")
REPO_TICKET = "DAEO-0rfi"   # W2-54: closed, and present in every worktree of wave 2


def store_root():
    """The worktree whose store the repository cases read: this one, unless ``W2108_STORE_ROOT`` names another."""
    return Path(os.environ.get(STORE_ROOT_SETTING) or REPO_ROOT).resolve()


def repo_env(driver):
    """The scratch environment for this repository's store: the embedders where this environment names them (else
    the defaults), nothing on PATH that could start one, an empty HOME (so no reranker: the rerank is not under
    test)."""
    env = driver.env()
    for name in ("OLLAMA_HOST", "GOV_QUERY_OLLAMA_HOST"):
        if os.environ.get(name):
            env[name] = os.environ[name]
        else:
            del env[name]
    return env
