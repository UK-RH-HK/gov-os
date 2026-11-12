"""Support code for the W2-124 acceptance tests: the semantic store fails named, adoption records it (DAEO-mb2t,
DEC-1027 C, DEC-1015 item 4; S5 moved from W2-88, DEC-1083).

The interface under test is public only (README, "The interface"):

- ``gov rebuild [--json] [--no-embeddings]`` and ``gov adopt --lite --stage <A> --json``, run as
  ``sys.executable -m gov.cli.main ...`` in a repository planted under pytest's ``tmp_path``: standard output (the API
  envelope), standard error, the exit code, the committed A6 record;
- the module the ticket's Interface names for the close, ``gov.close.rebuild_gate`` (``semantic_failure``, ``check``),
  where a line has no command form (S4);
- the embedding endpoint at ``OLLAMA_HOST``: a stand-in on a loopback port the case starts and stops (healthy, failing
  part way, hung), or a loopback port nothing listens on (unavailable). No case starts a real embedder or model.

**The code under test is whatever ``gov`` the pytest process imports (DEC-732)**: every child is started as
``sys.executable -m gov.cli.main`` with the pytest process's own ``PYTHONPATH``.

What the environment of every child holds: an empty ``HOME``; the real ``gitleaks`` linked into a tools folder first
on ``PATH``; no code-graph tool on ``PATH``; no ``ollama`` program (``GOV_OLLAMA_BIN`` names a path that does not
exist); no secrets cache; a rebuild lock of the case's own; a vector cache new and empty for each run.
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
import socket
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
GITLEAKS_TEMPLATE = REPO_ROOT / "template/.gitleaks.toml"
PATH_MAP_TEMPLATE = REPO_ROOT / "template/governance/project/path-map.yaml"

REAL_GITLEAKS = shutil.which("gitleaks")
GIT = shutil.which("git")

PATH_MAP_REL = "governance/project/path-map.yaml"
SETTINGS_REL = "governance/project/rebuild.yaml"
GITLEAKS_REL = ".gitleaks.toml"
COMMAND_TIMEOUT_S = 240.0
EMBED_MODEL = "qwen3-embedding:0.6b"
EMBED_REVISION = "ac6da0dfba84"
DIMENSIONS = 1024
BATCH = 32          # gov.retrieval.semantic.BATCH: more chunks than this need more than one embed request


def gov_src():
    spec = importlib.util.find_spec("gov")
    if spec is None or not spec.origin:
        raise AssertionError("no gov package can be imported: set PYTHONPATH to the worktree's src/")
    return Path(spec.origin).resolve().parents[1]


def python_path():
    return os.environ.get("PYTHONPATH") or str(gov_src())


def lacking():
    """Why a rebuild cannot run on this machine at all, or None."""
    if REAL_GITLEAKS is None or GIT is None:
        return "gitleaks or git is not on PATH: the rebuild cannot run its stages"
    if importlib.util.find_spec("sqlite_vec") is None:
        return "sqlite_vec cannot be imported: the semantic store cannot hold a vector"
    return None


# --------------------------------------------------------------------------------------------------------------------
# The stand-in embedders: Ollama's HTTP interface on a loopback port
# --------------------------------------------------------------------------------------------------------------------

def stand_in_vector(text):
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"[a-z0-9]+", str(text).lower()):
        if len(word) < 3:
            continue
        digest = hashlib.sha256(word.encode()).digest()
        vector[int.from_bytes(digest[:4], "big") % DIMENSIONS] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        vector[0], norm = 1.0, 1.0
    return [value / norm for value in vector]


class Embedder:
    """An Ollama endpoint on a free loopback port, in one of three ways (``mode``):

    - ``healthy``: lists the model, embeds every request;
    - ``part-way``: embeds the first ``good`` embed requests, then answers every later one with HTTP 400 and no vector
      (a failure that is not transient, so no wait of the rebuild's retries is spent);
    - ``part-way-500``: as ``part-way``, but the later requests get HTTP 500 (a transient failure the rebuild's own
      retries wait out, so a case that uses it patches those waits away);
    - ``hung``: lists the model, then accepts every embed request and never answers it.

    It counts the embed requests it was asked (``asked``) and the texts in them (``texts``).
    """

    def __init__(self, mode="healthy", good=1):
        self.mode, self.good = mode, good
        self.asked = 0
        self.texts = 0
        self.lock = threading.Lock()
        self.release = threading.Event()
        self.digest = EMBED_REVISION + hashlib.sha256(b"w2-124 stand-in").hexdigest()[:52]
        stand_in = self
        entry = {"name": EMBED_MODEL, "model": EMBED_MODEL, "digest": self.digest, "size": 639150000,
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
                    reply = {"models": [{**entry, "size_vram": entry["size"]}]}
                elif route == "/api/show":
                    reply = {"details": entry["details"],
                             "model_info": {"general.architecture": "qwen3", "qwen3.embedding_length": DIMENSIONS},
                             "capabilities": ["embedding"]}
                elif route in ("/api/embed", "/api/embeddings"):
                    given = asked.get("input", asked.get("prompt", ""))
                    texts = [given] if isinstance(given, str) else list(given)
                    with stand_in.lock:
                        stand_in.asked += 1
                        number = stand_in.asked
                        stand_in.texts += len(texts)
                    if stand_in.mode == "hung":
                        stand_in.release.wait(timeout=60)
                        return
                    if stand_in.mode in ("part-way", "part-way-500") and number > stand_in.good:
                        status = 400 if stand_in.mode == "part-way" else 500
                        reply = {"error": "the stand-in fails after its first requests"}
                    elif route == "/api/embed":
                        reply = {"model": EMBED_MODEL, "embeddings": [stand_in_vector(t) for t in texts]}
                    else:
                        reply = {"embedding": stand_in_vector(texts[0] if texts else "")}
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
        self.release.set()
        self.server.shutdown()
        self.server.server_close()


def dead_host():
    """``host:port`` of a loopback port that nothing listens on (bound, then released): an embedder that is unavailable."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"127.0.0.1:{port}"


# --------------------------------------------------------------------------------------------------------------------
# The environment of every child
# --------------------------------------------------------------------------------------------------------------------

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
    if REAL_GITLEAKS and not (box.tools / "gitleaks").exists():
        (box.tools / "gitleaks").symlink_to(REAL_GITLEAKS)
    return box


def environment(box, host, **extra):
    path = os.pathsep.join([str(box.tools), str(Path(sys.executable).parent), "/usr/bin", "/bin"])
    env = {
        "PATH": path, "HOME": str(box.home), "TMPDIR": str(box.tmpdir), "XDG_CACHE_HOME": str(box.home / ".cache"),
        "GOV_VECTOR_CACHE_DIR": str(box.base / "vector-cache"),
        "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC",
        "PYTHONPATH": python_path(), "PYTHONUSERBASE": site.getuserbase(),
        "PYTHONPYCACHEPREFIX": str(box.pycache), "PYTHONDONTWRITEBYTECODE": "1",
        "OLLAMA_HOST": host, "GOV_QUERY_OLLAMA_HOST": host,
        "GOV_OLLAMA_BIN": str(box.base / "no-ollama-here"),
        "GOV_SECRETS_CACHE": "", "GOV_REBUILD_LOCK": str(box.lock),
        "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
        "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "W2-124 acceptance", "GIT_AUTHOR_EMAIL": "w2-124@example.invalid",
        "GIT_COMMITTER_NAME": "W2-124 acceptance", "GIT_COMMITTER_EMAIL": "w2-124@example.invalid",
    }
    env.update(extra)
    root = Path(env["GOV_VECTOR_CACHE_DIR"])
    root.mkdir(parents=True, exist_ok=True)
    env["GOV_VECTOR_CACHE_DIR"] = tempfile.mkdtemp(prefix="run-", dir=root)
    return env


# --------------------------------------------------------------------------------------------------------------------
# A planted repository
# --------------------------------------------------------------------------------------------------------------------

def git(directory, *args):
    proc = subprocess.run([GIT, "-C", str(directory), "-c", "user.name=W2-124 acceptance",
                           "-c", "user.email=w2-124@example.invalid", "-c", "commit.gpgsign=false",
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


ALL_ROLES = ["engineer", "independent-test-designer", "independent-auditor", "orchestrator", "product-spec", "research"]


def path_map_document(policy="embedded", code_intelligence=False):
    """The kernel's path map (the template) with one more namespace, ``docs``, whose ``embedding_policy`` is
    ``policy`` (``embedded``, or ``not embedded``); ``policy=None`` leaves the template as it is (no embedded one)."""
    document = yaml.safe_load(PATH_MAP_TEMPLATE.read_text(encoding="utf-8"))
    if policy is not None:
        document.setdefault("namespaces", {})["docs"] = {
            "paths": ["docs/**"], "memory_class": "governance", "sensitivity": "internal",
            "permitted_roles": ALL_ROLES, "retention": "kept in git history", "export_policy": "allowed",
            "embedding_policy": policy, "provenance": "written by the W2-124 tests",
            "deletion_rebuild": "authoritative; restored from git only"}
    if code_intelligence:
        document.setdefault("capabilities", {})["code_intelligence"] = {"enabled": True, "languages": ["python"]}
    return document


def note(word):
    return (f"# The {word} note\n\nThe {word} ledger is kept in the {word} drawer beside the harbour.\n"
            f"Every {word} entry is copied twice by the {word} clerk.\n")


def plant(box, name="project", *, path_map="embedded", gitleaks=True, files=3, code_intelligence=False,
          commit=True):
    """A committed repository under ``box.base``. ``path_map``: ``embedded`` (a ``docs`` namespace that embeds),
    ``not embedded`` (one that does not), ``template`` (the kernel's namespaces only), ``absent`` (no path map).
    ``files`` notes under ``docs/`` (each a chunk or more; more than ``BATCH`` of them need two embed requests)."""
    project = box.base / name
    project.mkdir(parents=True)
    write(project / ".gitignore", ".gov-runtime/\n__pycache__/\n")
    if gitleaks:
        shutil.copy2(GITLEAKS_TEMPLATE, project / GITLEAKS_REL)
    if path_map != "absent":
        policy = {"embedded": "embedded", "not embedded": "not embedded", "template": None}[path_map]
        write(project / PATH_MAP_REL, yaml.safe_dump(path_map_document(policy, code_intelligence), sort_keys=False))
    write(project / SETTINGS_REL, f"slow_after_s: 600\nlock: {json.dumps(str(box.lock))}\n")
    for number in range(files):
        write(project / f"docs/note-{number:03d}.md", note(f"harbourword{number:03d}"))
    git(project, "init", "-q", "-b", "main")
    if commit:
        git(project, "add", "-A")
        git(project, "commit", "-q", "-m", "W2-124 planted project")
    return project


# --------------------------------------------------------------------------------------------------------------------
# Running the tool
# --------------------------------------------------------------------------------------------------------------------

@dataclass
class Run:
    args: tuple
    returncode: int | None
    stdout: str
    stderr: str
    seconds: float

    def envelope(self):
        for line in reversed(self.stdout.strip().splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    value = json.loads(line)
                except ValueError:
                    break
                return value if isinstance(value, dict) else {}
        try:
            value = json.loads(self.stdout)
            return value if isinstance(value, dict) else {}
        except ValueError:
            return {}

    @property
    def result(self):
        return self.envelope().get("result") or {}

    @property
    def error(self):
        return self.envelope().get("error") or {}

    @property
    def prints_ok(self):
        """Exit 0 and, with ``--json``, ``"ok": true``."""
        return self.returncode == 0 and self.envelope().get("ok") is True

    def describe(self, tail=2500):
        return (f"gov {' '.join(self.args)}\nexit code: {self.returncode} after {self.seconds:.1f} s\n"
                f"stdout:\n{self.stdout[-tail:]}\nstderr:\n{self.stderr[-tail:]}")


def gov(project, env, *args, timeout=COMMAND_TIMEOUT_S):
    argv = (sys.executable, "-m", "gov.cli.main", *args)
    began = time.monotonic()
    try:
        done = subprocess.run(argv, cwd=str(project), env=env, stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, timeout=timeout)
        code, out, err = done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired as exc:
        code = None
        out = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    return Run(tuple(args), code, out, err, time.monotonic() - began)


def rebuild(project, box, host, *extra, **env_extra):
    """``gov rebuild <extra>`` (add ``--json`` among ``extra`` for the envelope)."""
    return gov(project, environment(box, host, **env_extra), "rebuild", *extra)


def not_built_stores(result):
    """The store names listed in the result's ``not_built`` (a list of ``{store, reason}``)."""
    listed = result.get("not_built")
    if listed is None and result.get("complete") is True:   # a complete rebuild may leave the empty list out
        listed = []
    if not isinstance(listed, list):
        return None
    return [entry.get("store") if isinstance(entry, dict) else entry for entry in listed]


def semantic_status(result):
    return ((result.get("stores") or {}).get("semantic") or {})


# --------------------------------------------------------------------------------------------------------------------
# A planted adoption, stage by stage (as W2-23's tests drive it), with the embedder unavailable or healthy
# --------------------------------------------------------------------------------------------------------------------

ADOPTION = "governance/adoption"
A6_RECORD = f"{ADOPTION}/A6-controlled-migration.md"
A3_RECORD = f"{ADOPTION}/A3-target-path-map.md"
STAGES = ("A0", "A1", "A2", "A3", "A4", "A5", "A6")
VERDICT_REL = "audit/adoption/a5-verdict.md"
ADOPTER, AUDITOR = "adopter-w2-124", "auditor-w2-124"
DROP = "docs/drop-1.txt"
ADOPT_PATHS = (".gitignore", ".gitleaks.toml", "README.md", "governance/**", "docs/**", "lib/**", "audit/**")
SYSTEMS = ("constitution-and-policies", "knowledge-fabric", "repository-contract", "agent-organisation", "skills",
           "tools-and-capabilities", "command-surface", "model-adapters", "orchestration-and-handoffs",
           "specification-and-planning", "research-and-experiments", "task-system", "product-delivery",
           "verification-and-governance-tests", "change-impact-control", "checkpoint-and-recovery",
           "observability-and-cost", "organisational-learning", "independent-audit", "security-and-permissions",
           "budget-governance", "emergency-stop-and-rollback")


def adoption_path_map():
    """A path map in the kernel schema's shape (as W1-41's and W2-23's tests write it): one embedded namespace."""
    namespace = {"paths": list(ADOPT_PATHS), "memory_class": "governance", "sensitivity": "internal",
                 "permitted_roles": ["orchestrator", "engineer", "independent-auditor"],
                 "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": "embedded",
                 "provenance": "written by the W2-124 tests", "deletion_rebuild": "authoritative; restored from git only"}
    return {"state_class": "AUTHORITATIVE", "namespaces": {"harbour": namespace},
            "capabilities": {"code_intelligence": {"enabled": False}, "research_corpus": {"enabled": False}},
            "policies": {**{key: "hard-block" for key in ("security", "authority", "test", "change", "human_gate",
                                                           "tool")},
                         **{key: "warning" for key in ("memory", "context", "checkpoint", "model_routing", "budget",
                                                       "learning", "archive")}},
            "systems": {name: {"status": "absent", "reason": "a legacy project before adoption"} for name in SYSTEMS}}


def plant_legacy(box, name="harbour"):
    """A legacy repository, committed, to be adopted: notes to embed, one file the proposal removes."""
    project = box.base / name
    project.mkdir(parents=True)
    write(project / ".gitignore", ".gov-runtime/\n__pycache__/\n*.pyc\n")
    shutil.copy2(GITLEAKS_TEMPLATE, project / GITLEAKS_REL)
    write(project / PATH_MAP_REL, yaml.safe_dump(adoption_path_map(), sort_keys=False))
    write(project / "README.md", "# Harbour\n\nA programme's own repository, planted by the W2-124 tests.\n")
    write(project / "docs/guide.md", "# Guide\n\nHow the harbour is run.\n")
    write(project / "docs/notes.txt", "Tide tables are kept by the harbour master.\n")
    write(project / "lib/__init__.py", '"""Loose helpers."""\n')
    write(project / DROP, "Removed from the active tree by batch 1.\n")
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "the programme's repository")
    return project


def head_file(project, rel):
    proc = subprocess.run([GIT, "-C", str(project), "show", f"HEAD:{rel}"], capture_output=True, text=True,
                          env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull})
    return proc.stdout if proc.returncode == 0 else None


def frontmatter(text):
    lines = text.split("\n")
    assert lines and lines[0].strip() == "---", "the record has no frontmatter"
    end = [line.strip() for line in lines[1:]].index("---") + 1
    data = yaml.safe_load("\n".join(lines[1:end]))
    assert isinstance(data, dict), "the record's frontmatter is not a mapping"
    return data


class Adoption:
    """``gov adopt --lite --stage <A> --json`` one stage per call; the embedding endpoint is at ``host``."""

    def __init__(self, project, box, host):
        self.project, self.box, self.host = Path(project), box, host
        self.runs = {}

    def env(self):
        folders = [str(self.box.tools), str(Path(sys.executable).parent),
                   *os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep),
                   str(Path.home() / ".local" / "bin")]
        return environment(self.box, self.host, PATH=os.pathsep.join(dict.fromkeys(f for f in folders if f)))

    def run(self, stage, *extra):
        run = gov(self.project, self.env(), "adopt", "--lite", "--stage", stage, *extra, "--json",
                  "--session", ADOPTER)
        self.runs[stage] = run
        return run

    def write_verdict(self):
        data = head_file(self.project, A3_RECORD)
        assert data is not None, f"{A3_RECORD} is not committed"
        front = {"id": "AV-0001", "type": "adoption-verdict", "status": "ACTIVE", "state_class": "EVIDENCE",
                 "stage": "A5", "verdict": "pass", "path_map": A3_RECORD,
                 "path_map_hash": hashlib.sha256(data.encode()).hexdigest(), "auditor_session": AUDITOR}
        write(self.project / VERDICT_REL, "---\n" + yaml.safe_dump(front, sort_keys=False)
              + "---\n\n# AV-0001: review of the path map\n\nRead before any move.\n")
        git(self.project, "add", "--", VERDICT_REL)
        git(self.project, "commit", "-q", "-m", "A5: review of the path map", "--trailer", "Task: HARB-a5aa",
            "--trailer", "Role: independent-auditor")

    def through(self, last):
        """Run A0 to ``last``; return the first run that did not succeed, else the last run."""
        proposal = self.box.base / "proposal.yaml"
        proposal.write_text(yaml.safe_dump({"artefacts": [{"path": DROP, "action": "DELETE_FROM_ACTIVE_TREE",
                                                           "batch": 1}]}, sort_keys=False), encoding="utf-8")
        run = None
        for stage in STAGES[:STAGES.index(last) + 1]:
            if stage == "A3":
                run = self.run(stage, "--map", str(proposal))
            elif stage == "A5":
                self.write_verdict()
                run = self.run(stage, "--verdict", VERDICT_REL)
            else:
                run = self.run(stage)
            if run.returncode != 0:
                return run
        return run


# --------------------------------------------------------------------------------------------------------------------
# Shared assertions
# --------------------------------------------------------------------------------------------------------------------

RECORD_REL = ".gov-runtime/rebuild/stores.json"      # the warm base's record (W2-122): written by a full, ok rebuild


def assert_named_failure(run, label):
    """A rebuild that was asked for its semantic store and did not recreate it: exit 1, ``REBUILD_FAILED``,
    ``store: semantic`` with its reason and the stores built; never an ok answer."""
    assert run.returncode == 1, f"{label}: expected exit code 1, got {run.returncode}\n{run.describe()}"
    envelope = run.envelope()
    assert envelope.get("ok") is False, f"{label}: the envelope does not say ok: false\n{run.describe()}"
    assert run.error.get("code") == "REBUILD_FAILED", f"{label}: the error is not REBUILD_FAILED\n{run.describe()}"
    details = run.error.get("details") or {}
    assert details.get("store") == "semantic", f"{label}: details.store is not 'semantic'\n{run.describe()}"
    assert isinstance(details.get("reason"), str) and details["reason"].strip(), \
        f"{label}: details.reason is empty\n{run.describe()}"
    assert isinstance(details.get("stores"), dict) and "lexical" in details["stores"], \
        f"{label}: details.stores does not hold the stores built\n{run.describe()}"


def semantic_result(status="not_recreated", **more):
    return {"status": status, **more}


def planted_result(semantic="absent"):
    """A planted ``gov rebuild`` result (as today's shape): lexical recreated, the semantic store as given (the word
    ``absent``: no semantic entry at all)."""
    stores = {"lexical": {"status": "recreated"}, "codeintel": {"status": "not_recreated", "reason": "no tool"}}
    if semantic != "absent":
        stores["semantic"] = semantic
    return {"digest": "0" * 64, "store": {"digest": "0" * 64, "invalid": []}, "stores": stores}


def envelope_of(result):
    return {"ok": True, "command": "rebuild", "result": result, "session": ""}
