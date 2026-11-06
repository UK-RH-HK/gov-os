"""Support code for the W2-116 acceptance tests: the integration branch's store, double-buffered (DAEO-f58b).

Public interfaces only (README, "The interface the cases assume"):

- ``gov rebuild --json --integration <branch>``, run in the project, and the link at the path ``integration_store``
  names in ``governance/project/rebuild.yaml`` (W2-122's key): where it points, what is checked out there, and the
  store under it;
- ``gov rebuild --json [--seed]`` in a ticket worktree, and its ``seed`` object;
- ``gov retrieve --json [--root <dir>] <question>``: its envelope, its evidence's paths and its ``facets``;
- ``gov launch <role> <ticket>``, with a stand-in CLI at ``<HOME>/.local/bin/claude`` that does what a session does
  when it searches: it applies the settings' ``env`` block to its environment and runs a plain ``gov retrieve``
  (no ``--root``) in the folder it was started in;
- the embedding endpoint at ``OLLAMA_HOST`` (the build's) and at ``GOV_QUERY_OLLAMA_HOST`` (the questions'): two
  stand-ins on loopback ports that each case starts and stops. The build's records every text it is asked to
  embed, and can hold its answers (a build half-way) or be closed (no model).

**The code under test is whatever ``gov`` the pytest process imports (DEC-732).** Every child is started as
``sys.executable -m gov.cli.main`` with the pytest process's own ``PYTHONPATH`` (else the folder of the ``gov`` it
imports). No model, no GPU, no real store: everything is under the case's ``tmp_path``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import signal
import site
import sqlite3
import stat
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
GITLEAKS_TEMPLATE = REPO_ROOT / "template/.gitleaks.toml"
PATH_MAP_TEMPLATE = REPO_ROOT / "template/governance/project/path-map.yaml"

REAL_GITLEAKS = shutil.which("gitleaks")
GIT = shutil.which("git")

BRANCH = "integrate"
SETTINGS_REL = "governance/project/rebuild.yaml"
STORE_REL = ".gov-runtime/store.db"
RUNTIME_REL = ".gov-runtime"
INTEGRATION = "--integration"          # the option this suite assumes (README)
BEHIND = "behind"                      # the word a seed from a store behind the head says (README)

EMBED_MODEL = "qwen3-embedding:0.6b"
EMBED_REVISION = "ac6da0dfba84"        # ADR-0002 §2's pin: the default when no models.yaml is planted
COMMAND_TIMEOUT_S = 300.0
WAIT_S = 120.0


def gov_src():
    spec = importlib.util.find_spec("gov")
    if spec is None or not spec.origin:
        raise AssertionError("no gov package can be imported: set PYTHONPATH to the worktree's src/ (README)")
    return Path(spec.origin).resolve().parents[1]


def python_path():
    return os.environ.get("PYTHONPATH") or str(gov_src())


def lacking():
    if REAL_GITLEAKS is None or GIT is None:
        return "gitleaks or git is not on PATH: a rebuild cannot run its stages"
    if importlib.util.find_spec("sqlite_vec") is None:
        return "sqlite_vec cannot be imported: the semantic store cannot hold a vector"
    return None


# --------------------------------------------------------------------------
# The stand-in embedder
# --------------------------------------------------------------------------

DIMENSIONS = 1024
_STOP = {"the", "and", "for", "with", "that", "this", "each", "does", "when", "who", "what", "into", "from"}


def stand_in_vector(text):
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


class Embedder:
    """Ollama's HTTP interface on a free loopback port, reporting the pinned model on the GPU. It records every text
    it is asked to embed; ``hold()`` makes every embedding request wait until ``release()`` (a build half-way), and
    ``asked`` is set at the first request that arrives while held."""

    def __init__(self):
        self.embedded = []
        self.requests = 0
        self.lock = threading.Lock()
        self.gate = threading.Event()
        self.gate.set()
        self.asked = threading.Event()
        digest = EMBED_REVISION + hashlib.sha256(b"w2-116 stand-in").hexdigest()[:52]
        entry = {"name": EMBED_MODEL, "model": EMBED_MODEL, "digest": digest, "size": 639150000,
                 "details": {"family": "qwen3", "parameter_size": "595.78M", "quantization_level": "Q8_0"}}
        me = self

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
                    reply = {"models": [{**entry, "size_vram": entry["size"]}]}
                elif route == "/api/show":
                    reply = {"details": entry["details"],
                             "model_info": {"general.architecture": "qwen3", "qwen3.embedding_length": DIMENSIONS},
                             "capabilities": ["embedding"]}
                elif route in ("/api/embed", "/api/embeddings"):
                    given = asked.get("input", asked.get("prompt", ""))
                    texts = [given] if isinstance(given, str) else list(given)
                    if not me.gate.is_set():
                        me.asked.set()
                        me.gate.wait(timeout=COMMAND_TIMEOUT_S)
                    with me.lock:
                        me.requests += 1
                        me.embedded.extend(str(text) for text in texts)
                    if route == "/api/embed":
                        reply = {"model": EMBED_MODEL, "embeddings": [stand_in_vector(t) for t in texts],
                                 "total_duration": 1, "load_duration": 1, "prompt_eval_count": len(texts)}
                    else:
                        reply = {"embedding": stand_in_vector(texts[0] if texts else "")}
                else:
                    status = 404
                payload = json.dumps(reply).encode()
                try:
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                except OSError:  # the asker was killed while it waited
                    pass

            do_GET = do_POST = do_HEAD = do_DELETE = answer

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.host = f"127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

    def forget(self):
        with self.lock:
            self.embedded.clear()
            self.requests = 0

    def texts(self):
        with self.lock:
            return list(self.embedded)

    def hold(self):
        self.asked.clear()
        self.gate.clear()

    def release(self):
        self.gate.set()

    def close(self):
        self.gate.set()
        self.server.shutdown()
        self.server.server_close()


def closed_host():
    """A loopback address where nothing listens: an endpoint with no model."""
    import socket

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return f"127.0.0.1:{probe.getsockname()[1]}"


# --------------------------------------------------------------------------
# The box: every folder of a case, and the environment of every child
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Box:
    base: Path
    home: Path
    tmpdir: Path
    tools: Path
    pycache: Path
    lock: Path
    link: Path       # integration_store: outside the project


def make_box(base):
    base = Path(base).resolve()
    box = Box(base, base / "home", base / "systmp", base / "tools", base / "pycache",
              base / "locks" / "rebuild.lock", base / "stores" / "integration")
    for folder in (box.home, box.tmpdir, box.tools, box.pycache, box.lock.parent, box.link.parent):
        folder.mkdir(parents=True, exist_ok=True)
    if not (box.tools / "gitleaks").exists():
        (box.tools / "gitleaks").symlink_to(REAL_GITLEAKS)
    return box


def environment(box, build_host, query_host):
    path = os.pathsep.join([str(box.tools), str(Path(sys.executable).parent), "/usr/bin", "/bin"])
    return {
        "PATH": path,
        "HOME": str(box.home),
        "TMPDIR": str(box.tmpdir),
        "XDG_CACHE_HOME": str(box.home / ".cache"),
        "GOV_VECTOR_CACHE_DIR": str(box.base / "vector-cache"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONPATH": python_path(),
        "PYTHONUSERBASE": site.getuserbase(),
        "PYTHONPYCACHEPREFIX": str(box.pycache),
        "PYTHONDONTWRITEBYTECODE": "1",
        "OLLAMA_HOST": build_host,
        "GOV_QUERY_OLLAMA_HOST": query_host,
        "GOV_OLLAMA_BIN": str(box.base / "no-ollama-here"),
        "GOV_SECRETS_CACHE": "",
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "W2-116 acceptance", "GIT_AUTHOR_EMAIL": "w2-116@example.invalid",
        "GIT_COMMITTER_NAME": "W2-116 acceptance", "GIT_COMMITTER_EMAIL": "w2-116@example.invalid",
    }


def run_environment(env):
    """A machine-wide vector cache of its own for each child (W2-126): a cold build is cold in the cache too."""
    root = Path(env["GOV_VECTOR_CACHE_DIR"])
    root.mkdir(parents=True, exist_ok=True)
    return {**env, "GOV_VECTOR_CACHE_DIR": tempfile.mkdtemp(prefix="run-", dir=root)}


# --------------------------------------------------------------------------
# The planted project: an integration branch, notes with words of their own, tickets, the guard's settings
# --------------------------------------------------------------------------

def git(directory, *args):
    proc = subprocess.run([GIT, "-C", str(directory), "-c", "user.name=W2-116 acceptance",
                           "-c", "user.email=w2-116@example.invalid", "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, check=False, timeout=60,
                          env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull})
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {directory}: {proc.stderr.strip()}")
    return proc.stdout


def head(directory, ref="HEAD"):
    return git(directory, "rev-parse", ref).strip()


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
        "provenance": "written by the W2-116 tests",
        "deletion_rebuild": "authoritative; restored from git only",
    }
    return yaml.safe_dump(document, sort_keys=False)


def settings_text(box):
    return (f"slow_after_s: 600\nlock: {json.dumps(str(box.lock))}\n"
            f"integration_store: {json.dumps(str(box.link))}\n")


def note(word, extra=""):
    """A note whose words are its own: ``word`` is in no other file."""
    return (f"# The {word} note\n\nThe {word} ledger is kept in the {word} drawer beside the harbour.\n"
            f"Every {word} entry is copied twice by the {word} clerk.{extra}\n")


ENGINEER_TICKET, PRODUCT_SPEC_TICKET = "DAEO-w901", "DAEO-w902"
GUARD_SETTINGS = {"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [
    {"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse.py\""}]}]}}


def ticket_text(ticket_id, wbs, role, allowed):
    return (f"---\nid: {ticket_id}\nstatus: in_progress\ndeps: []\nlinks: []\ncreated: 2026-11-06T00:00:00Z\n"
            f"type: task\npriority: 2\nassignee: {role}\nexternal-ref: {wbs}\ntags: [wave-2]\nwbs_id: {wbs}\n"
            f"title: 'A planted ticket of the W2-116 tests'\nclass: implementation\nstate_class: AUTHORITATIVE\n"
            f"role: {role}\ndepends_on: []\nallowed_paths:\n- {allowed}\nkpis:\n  success:\n  - 'A planted line'\n"
            f"  failure:\n  - 'A planted failure'\nprofile: STANDARD\nsources: []\nest_loc: 10\n"
            f"acceptance_tests:\n  path: tests/acceptance/{wbs}/\ntrack: B\nlist_rows: []\n---\n# {wbs}\n")


# The integration branch at H1; the words are the cases' questions.
KEPT, CHANGED, MERGED, ENGINEERS = "docs/kept.md", "docs/changed.md", "docs/merged.md", "docs/engineer-new.md"
KEPT_WORD, CHANGED_WORD, NEW_WORD, MERGED_WORD = "quillwort", "bergamot", "tamarind", "fenugreek"
ENGINEERS_WORD = "zanzibar"     # only in a ticket worktree's own commit, never on the integration branch
H1_FILES = {KEPT: note(KEPT_WORD), CHANGED: note(CHANGED_WORD), "docs/other.md": note("marjoram")}


def make_project(box, name="project"):
    """The project at H1, on the branch ``integrate``: the path map (docs embedded), the gitleaks rules,
    ``rebuild.yaml`` (a temporary lock; ``integration_store`` the link outside the project), three notes, two
    in-progress tickets and the guard's settings (so ``gov launch`` accepts the project). No store."""
    project = box.base / name
    project.mkdir(parents=True)
    write(project / ".gitignore", ".gov-runtime/\n__pycache__/\n")
    shutil.copy2(GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    write(project / "governance/project/path-map.yaml", path_map_text())
    write(project / SETTINGS_REL, settings_text(box))
    write(project / ".claude/settings.json", json.dumps(GUARD_SETTINGS, indent=2) + "\n")
    write(project / f".tickets/{ENGINEER_TICKET}.md", ticket_text(ENGINEER_TICKET, "W2-901", "engineer", "docs/**"))
    write(project / f".tickets/{PRODUCT_SPEC_TICKET}.md",
          ticket_text(PRODUCT_SPEC_TICKET, "W2-902", "product-spec", "docs/**"))
    for rel, text in H1_FILES.items():
        write(project / rel, text)
    git(project, "init", "-q", "-b", BRANCH)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "W2-116 H1")
    return project


def land(project, files, removed=(), message="a landing"):
    """A merge into the integration branch, as a ticket's landing: a side branch with ``files`` (and ``removed``)
    merged with --no-ff. Returns the new head."""
    side = f"w2/side-{time.monotonic_ns()}"
    git(project, "checkout", "-q", "-b", side)
    for rel, text in files.items():
        write(Path(project) / rel, text)
    for rel in removed:
        (Path(project) / rel).unlink()
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", f"{message} (side)")
    git(project, "checkout", "-q", BRANCH)
    git(project, "merge", "-q", "--no-ff", "-m", message, side)
    return head(project)


def land_h2(project):
    """H2: the changed note gains NEW_WORD and the merged note (MERGED_WORD) is added."""
    return land(project, {CHANGED: note(CHANGED_WORD, f"\nThe {NEW_WORD} entry was added later."),
                          MERGED: note(MERGED_WORD)}, message="W2-116 H2: a merge into integrate")


def worktree(project, path, branch=None, ref=BRANCH):
    """A worktree of the project: on a new branch ``branch``, or detached at ``ref``. No store."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if branch:
        git(project, "worktree", "add", "-q", "-b", branch, str(path), ref)
    else:
        git(project, "worktree", "add", "-q", "--detach", str(path), ref)
    return path


def worktrees(project):
    """``{path: {"head": sha, "detached": bool}}`` from ``git worktree list --porcelain``, the project's own left out."""
    found, current = {}, None
    for line in git(project, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            current = os.path.realpath(line.split(" ", 1)[1])
            found[current] = {"head": None, "detached": False}
        elif line.startswith("HEAD ") and current:
            found[current]["head"] = line.split(" ", 1)[1]
        elif line == "detached" and current:
            found[current]["detached"] = True
    found.pop(os.path.realpath(project), None)
    return found


# --------------------------------------------------------------------------
# Running gov
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
            value = json.loads(self.stdout)
        except ValueError:
            return {}
        return value if isinstance(value, dict) else {}

    @property
    def ok(self):
        return self.returncode == 0 and self.envelope().get("ok") is True

    @property
    def result(self):
        result = self.envelope().get("result")
        return result if isinstance(result, dict) else {}

    @property
    def error_code(self):
        error = self.envelope().get("error")
        return error.get("code") if isinstance(error, dict) else None

    def describe(self, tail=2500):
        return (f"gov {' '.join(self.args)}\nexit code: {self.returncode} after {self.seconds:.1f} s\n"
                f"stdout:\n{self.stdout[-tail:]}\nstderr:\n{self.stderr[-tail:]}")


def gov(cwd, env, *args, timeout=COMMAND_TIMEOUT_S):
    argv = (sys.executable, "-m", "gov.cli.main", *args)
    began = time.monotonic()
    try:
        done = subprocess.run(argv, cwd=str(cwd), env=run_environment(env), stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=timeout)
        code, out, err = done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired as exc:
        code = None
        out = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    return Run(tuple(args), code, out, err, time.monotonic() - began)


def integration_build(project, env, branch=BRANCH):
    """``gov rebuild --json --integration <branch>`` in the project."""
    return gov(project, env, "rebuild", "--json", INTEGRATION, branch)


def built_integration(project, env, branch=BRANCH):
    run = integration_build(project, env, branch)
    assert run.ok, f"`gov rebuild {INTEGRATION} {branch}` did not succeed\n{run.describe()}"
    return run


def rebuild(cwd, env, *extra):
    return gov(cwd, env, "rebuild", "--json", *extra)


def start_integration_build(project, env, branch=BRANCH):
    """The same command in the background, in a session of its own (so a kill takes its whole group)."""
    argv = (sys.executable, "-m", "gov.cli.main", "rebuild", "--json", INTEGRATION, branch)
    return subprocess.Popen(argv, cwd=str(project), env=run_environment(env), stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)


def finish(process, timeout=COMMAND_TIMEOUT_S):
    began = time.monotonic()
    out, err = process.communicate(timeout=timeout)
    return Run(tuple(process.args[3:]), process.returncode, out, err, time.monotonic() - began)


def descendants(pid):
    """Every process under ``pid``, from the kernel's children lists."""
    found, todo = [], [pid]
    while todo:
        current = todo.pop()
        try:
            for task in os.listdir(f"/proc/{current}/task"):
                with open(f"/proc/{current}/task/{task}/children") as handle:
                    for child in handle.read().split():
                        found.append(int(child))
                        todo.append(int(child))
        except (OSError, ValueError):
            pass
    return found


def kill_build(process):
    """SIGKILL the build, its group and every process under it, at once: a build killed half-way."""
    for pid in [*descendants(process.pid), process.pid]:
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        process.communicate(timeout=WAIT_S)
    except subprocess.TimeoutExpired:
        pass


def wait_until_held(embedder, process, what):
    """Wait until the build asks the held endpoint for a vector: it is then half-way (past the record and lexical
    stages, in the semantic one)."""
    deadline = time.monotonic() + WAIT_S
    while not embedder.asked.wait(timeout=0.1):
        if process.poll() is not None:
            out, err = process.communicate()
            raise AssertionError(f"{what}: the build ended (exit {process.returncode}) before it asked for any "
                                 f"vector, so it was never half-way\nstdout:\n{out[-2000:]}\nstderr:\n{err[-2000:]}")
        if time.monotonic() > deadline:
            raise AssertionError(f"{what}: the build asked for no vector within {WAIT_S:.0f} s")


# --------------------------------------------------------------------------
# The link and the store under it
# --------------------------------------------------------------------------

def target(box):
    """Where the link points (resolved), or None when there is no link."""
    if not os.path.islink(box.link):
        return None
    return os.path.realpath(box.link)


def assert_link(box):
    assert os.path.islink(box.link), (
        f"no link at integration_store ({box.link}); there: "
        f"{'a folder' if box.link.is_dir() else 'a file' if box.link.exists() else 'nothing'}")
    return os.path.realpath(box.link)


def outside(path, project):
    path, project = os.path.realpath(path), os.path.realpath(project)
    return not (path == project or path.startswith(project + os.sep))


def file_digest(path):
    path = Path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def vector_count(root):
    path = Path(root) / STORE_REL
    if not path.is_file():
        return None
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        try:
            import sqlite_vec

            connection.enable_load_extension(True)
            sqlite_vec.load(connection)
            connection.enable_load_extension(False)
        except Exception:
            pass
        if connection.execute("SELECT 1 FROM sqlite_master WHERE name = 'semantic_vector'").fetchone() is None:
            return 0
        return connection.execute("SELECT COUNT(*) FROM semantic_vector").fetchone()[0]
    finally:
        connection.close()


def hand_built_store(box, project, env, name="hand-a"):
    """The integration store as the CTO's script makes it today, without the product: a detached worktree of the
    branch's head outside the project, a full ``gov rebuild`` in it, and the link at ``integration_store`` to it.
    The S3 and S4 cases that are not about the build itself read this one, so their red is their own line's."""
    half = worktree(project, box.base / "hand" / name)
    run = rebuild(half, env)
    assert run.ok, f"the hand-built store's rebuild did not succeed\n{run.describe()}"
    assert (run.result.get("stores") or {}).get("semantic", {}).get("status") == "recreated", run.describe()
    temporary = box.link.with_name(box.link.name + ".tmp")
    if os.path.lexists(temporary):
        temporary.unlink()
    temporary.symlink_to(half)
    os.replace(temporary, box.link)
    return half


# --------------------------------------------------------------------------
# Searching
# --------------------------------------------------------------------------

def search(cwd, env, question, root=None):
    args = ("retrieve", "--json") + (("--root", str(root)) if root is not None else ()) + (question,)
    return gov(cwd, env, *args, timeout=WAIT_S)


def evidence_paths(run):
    return [item.get("path") for item in run.result.get("evidence") or [] if isinstance(item, dict)]


def facets(run):
    value = run.result.get("facets")
    return value if isinstance(value, dict) else {}


def assert_answers(run, question, path, what):
    """The search succeeded, its evidence holds ``path``, and its lexical and semantic facets are available."""
    assert run.ok, f"{what}: the search for {question!r} did not answer\n{run.describe()}"
    assert path in evidence_paths(run), (
        f"{what}: the search for {question!r} gave no evidence from {path}: {evidence_paths(run)}\n{run.describe()}")
    assert_facets_available(run, what)


def assert_facets_available(run, what):
    found = facets(run)
    for name in ("lexical", "semantic"):
        facet = found.get(name)
        assert isinstance(facet, dict) and facet.get("available") is True, (
            f"{what}: the {name} facet is not available ({facet!r}); every facet: {found}")
        assert facet.get("reason") in (None, ""), f"{what}: the {name} facet gives a reason: {facet!r}"


def assert_not_answered_with(run, path, what):
    assert path not in evidence_paths(run), (
        f"{what}: the search gave evidence from {path}, which only the store being built (or a ticket's store) "
        f"holds: {evidence_paths(run)}")


# --------------------------------------------------------------------------
# gov launch with a stand-in CLI that searches as a session would
# --------------------------------------------------------------------------

CLI_REL = ".local/bin/claude"
SESSION_LOG = "W2_116_SESSION_LOG"
SESSION_QUESTION = "W2_116_QUESTION"

_STUB = r'''#!@PYTHON@
"""Stand-in for the Claude Code CLI (W2-116 acceptance tests): it applies the settings' env block to its environment,
as the CLI does for the session and its commands, runs a plain `gov retrieve --json <question>` (no --root) in the
folder it was started in, and records what it saw."""
import json, os, subprocess, sys

args = sys.argv[1:]
block = {}
for i, arg in enumerate(args):
    value = args[i + 1] if arg == "--settings" and i + 1 < len(args) else (
        arg.split("=", 1)[1] if arg.startswith("--settings=") else None)
    if value is not None:
        try:
            text = value if value.lstrip().startswith("{") else open(value, encoding="utf-8").read()
            found = json.loads(text).get("env") or {}
            block.update({k: v for k, v in found.items() if isinstance(v, str)})
        except Exception:
            pass
env = {**os.environ, **block}
question = os.environ.get(@QUESTION@, "")
done = subprocess.run([sys.executable, "-m", "gov.cli.main", "retrieve", "--json", question], cwd=os.getcwd(),
                      env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120)
with open(os.environ[@LOG@], "a", encoding="utf-8") as handle:
    handle.write(json.dumps({"cwd": os.getcwd(), "env_block": block, "returncode": done.returncode,
                             "stdout": done.stdout, "stderr": done.stderr[-3000:]}) + "\n")
'''


def install_cli(box):
    path = box.home / CLI_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_STUB.replace("@PYTHON@", sys.executable).replace("@QUESTION@", repr(SESSION_QUESTION))
                    .replace("@LOG@", repr(SESSION_LOG)), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


@dataclass
class Session:
    launch: Run
    record: dict | None

    @property
    def search(self):
        """The session's search, as a Run (its envelope is the plain `gov retrieve`'s)."""
        assert self.record is not None, f"gov launch started no session\n{self.launch.describe()}"
        return Run(("retrieve", "--json", "(in the session)"), self.record["returncode"], self.record["stdout"],
                   self.record["stderr"], 0.0)

    def describe(self):
        return f"{self.launch.describe()}\nthe session saw: {json.dumps(self.record)[:3000]}"


def launch_and_search(box, env, cwd, role, ticket, question):
    """``gov launch <role> <ticket>`` in ``cwd``; the stand-in session searches ``question`` with a plain
    ``gov retrieve``."""
    install_cli(box)
    log = box.base / f"session-{role}-{time.monotonic_ns()}.jsonl"
    launched = gov(cwd, {**env, SESSION_LOG: str(log), SESSION_QUESTION: question}, "launch", role, ticket)
    records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.is_file() else []
    assert len(records) <= 1, f"gov launch started {len(records)} sessions"
    return Session(launched, records[0] if records else None)
