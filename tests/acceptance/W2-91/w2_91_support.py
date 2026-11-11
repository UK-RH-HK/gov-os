"""Support code for the W2-91 acceptance tests (DAEO-a3u2; standard library and PyYAML only).

W2-91 (DEC-957, DEC-954 Q9c, DEC-388, DEC-694): the root files, every tracked file under ``governance/**`` and every
tracked file under ``schemas/**`` are embedded; the hidden half, the generated copies, the vendored code and ``cli/**``
stay out; the restricted overlay stays restricted; nothing else moves (DEC-381).

How the tests run (README, "How the tests pick up the code under test"):

- **The repository is the one this file sits in** (``Path(__file__).resolve().parents[3]``): its path map, its tracked
  files (``git ls-files``) and its history. Nothing in it is written.
- **The code under test is whatever ``PYTHONPATH`` gives the pytest process** (DEC-732). ``GOV_SRC`` is the folder that
  holds the imported ``gov`` package; every child process gets that folder on its ``PYTHONPATH``, and the suite refuses
  to run when it is not this repository's ``src/``.
- **Public interfaces only:** ``gov rebuild --json`` (run as ``python -m gov.cli.main``), the semantic store it writes
  (``semantic_vector`` joined to ``lexical_chunk``), and the pinned path-map check ``gov.check.pathmap.check``.
- **The path map's verdict** is read as DEC-381 and DEC-388 state it: a file is embedded when at least one namespace
  holds it and every namespace that holds it says exactly ``embedded``; any other value, or no namespace, is not
  embedded. The planted rebuilds show that the indexer gives vectors by that verdict.
- **Planted repositories** are built from scratch in pytest's ``tmp_path``: single named files of this repository only
  (its path map, the template's gitleaks rules), never a folder, never a clone. The embedder is a stand-in on the
  loopback interface (Ollama's HTTP interface, vectors computed from words); no network, no real embedder.
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

ROOT = Path(__file__).resolve().parents[3]
TICKET = "DAEO-a3u2"
# The ticket's base: the merge base of w2/W2-91 and w2/integrate when the tests were written (its path map and src/
# are those of the original base f46b96537d74). Used only where no commit of the ticket can be found (README).
BASE = "904bb3a0e7c6"
PATH_MAP_REL = "governance/project/path-map.yaml"
GITLEAKS_TEMPLATE_REL = "template/.gitleaks.toml"
STORE_REL = ".gov-runtime/store.db"

EMBEDDED, NOT_EMBEDDED = "embedded", "not embedded"
VALUES = {EMBEDDED, NOT_EMBEDDED}  # DEC-388 DP-8, DEC-694: the closed list

# W2-86's kernel-vendored parts (DEC-952 item 1, DEC-388): vendored code stays out.
VENDORED = ("template/governance/kernel/vendor/**", "template/governance/kernel/skills/superpowers/*/**",
            "template/governance/kernel/bin/**")
# DEC-957 / MEMORY-SPEC-MAP gap 1: what stays out by necessity. Since D-7 the path map names fixtures/ by its
# sub-folders (fixtures/evaluation/** in evaluation-fixtures, DEC-1066 (3)); every one of them still stays out.
HIDDEN = ("fixtures/**",)
GENERATED = (".claude/**", ".rulesync/**", "template/.rulesync/**")
CARRIED = ("cli/**",)


def gov_src():
    """The folder that holds the ``gov`` package this pytest process imports: the code under test (DEC-732)."""
    spec = importlib.util.find_spec("gov")
    if spec is None or not spec.origin:
        raise AssertionError("no gov package can be imported: set PYTHONPATH to the repository's src/ (README)")
    return Path(spec.origin).resolve().parents[1]


GOV_SRC = gov_src()


def assert_code_under_test():
    assert GOV_SRC == (ROOT / "src").resolve(), f"gov is not this repository's: {GOV_SRC} (set PYTHONPATH, README)"


# --------------------------------------------------------------------------
# The path map's language and verdict
# --------------------------------------------------------------------------

def matches(rel, pattern):
    """The path map's language (its header): ``**`` crosses folders, ``*`` stays inside one folder."""
    parts = [re.escape(part).replace(r"\*", "[^/]*") for part in pattern.split("**")]
    return re.fullmatch(".*".join(parts), rel) is not None


def matches_any(rel, patterns):
    return any(matches(rel, pattern) for pattern in patterns)


def homes(namespaces, rel):
    """The names of the namespaces whose patterns ``rel`` matches."""
    return [name for name, entry in namespaces.items()
            if isinstance(entry, dict) and matches_any(rel, entry.get("paths") or [])]


def embedded(namespaces, rel):
    """DEC-381, DEC-388: in at least one namespace, and every one that holds it says exactly ``embedded``."""
    policies = [namespaces[name].get("embedding_policy") for name in homes(namespaces, rel)]
    return bool(policies) and all(policy == EMBEDDED for policy in policies)


def embedded_set(namespaces, paths):
    return {rel for rel in paths if embedded(namespaces, rel)}


def newly_embedded_area(rel):
    """The sets DEC-957 embeds: the root files, ``governance/**`` and ``schemas/**``."""
    return "/" not in rel or rel.startswith(("governance/", "schemas/"))


# D-7 narrows DEC-957's sets (DEC-1052 M-4, DEC-1055 (2) and (3)): the overlay's close, nightly, session and review
# records stay in keyword search only. Written as the decision words them, not read from the path map.
OVERLAY_RECORDS = ("governance/project/orchestration/closes/**", "governance/project/orchestration/nightly/**",
                   "governance/project/orchestration/sessions/**", "governance/project/orchestration/reviews/**")


def embedded_after_d7(rel):
    """DEC-957's sets as D-7 leaves them: ``newly_embedded_area`` less the overlay's record folders. ``moved`` keeps
    ``newly_embedded_area``: this ticket's own steps are judged by the scope they were made under."""
    return newly_embedded_area(rel) and not matches_any(rel, OVERLAY_RECORDS)


# --------------------------------------------------------------------------
# This repository: tracked files, path maps, history
# --------------------------------------------------------------------------

def git(*args, cwd=ROOT, check=True):
    done = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    if check:
        assert done.returncode == 0, f"git {' '.join(args)} failed in {cwd}:\n{done.stderr}"
    return done


def tracked():
    return [rel for rel in git("ls-files", "-z").stdout.split("\0") if rel]


def path_map_text_at(revision):
    """The path map at ``revision`` (``None``: the working tree, as the run sees it)."""
    if revision is None:
        return (ROOT / PATH_MAP_REL).read_text(encoding="utf-8")
    return git("show", f"{revision}:{PATH_MAP_REL}").stdout


def namespaces_at(revision=None):
    return yaml.safe_load(path_map_text_at(revision))["namespaces"]


def ticket_commits(*paths):
    """The ticket's own commits (``Task: DAEO-a3u2``, merges left out), oldest first, that touch ``paths``."""
    log = git("log", "--no-merges", "--reverse", "--format=%H%x00%(trailers:key=Task,valueonly,separator=%x2C)",
              "HEAD", "--", *paths).stdout
    commits = []
    for line in log.splitlines():
        sha, _, tasks = line.partition("\0")
        if TICKET in {task.strip() for task in tasks.split(",")}:
            commits.append(sha)
    return commits


def ticket_steps(*paths):
    """This ticket's own changes to ``paths``, each as (before, after) revisions: each of its commits against its
    first parent, then the uncommitted change (HEAD against the working tree) when there is one. When the ticket has
    no commit there, the base against the working tree."""
    steps = [(f"{sha}^", sha) for sha in ticket_commits(*paths)]
    if git("diff", "--quiet", "HEAD", "--", *paths, check=False).returncode != 0:
        steps.append(("HEAD", None))
    if not steps:
        steps.append((BASE, None))
    return steps


# --------------------------------------------------------------------------
# Planted repositories and the stand-in embedder
# --------------------------------------------------------------------------

EMBED_MODEL = "qwen3-embedding:0.6b"
EMBED_REVISION = "ac6da0dfba84"  # the pin of ADR-0002 §2: the stand-in's model list reports a digest beginning so
DIMENSIONS = 1024
STAND_IN_DIGEST = EMBED_REVISION + hashlib.sha256(b"w2-91 stand-in").hexdigest()[:52]
REBUILD_TIMEOUT_S = 600


def stand_in_vector(text):
    """A unit vector made of the words of ``text``."""
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"[a-z0-9]+", str(text).lower()):
        digest = hashlib.sha256(word.encode()).digest()
        vector[int.from_bytes(digest[:4], "big") % DIMENSIONS] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        vector[0], norm = 1.0, 1.0
    return [value / norm for value in vector]


class OllamaStandIn:
    """A healthy Ollama endpoint on a free loopback port, reporting the model wholly on the CPU."""

    def __init__(self):
        self.embedded_texts = []
        texts_seen = self.embedded_texts
        model = {"name": EMBED_MODEL, "model": EMBED_MODEL, "digest": STAND_IN_DIGEST, "size": 639150000,
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
                    reply = {"models": [model]}
                elif route == "/api/ps":
                    # Rewrite-Reason: W2-32's S10 (DEC-1065): the model on the GPU
                    reply = {"models": [{**model, "size_vram": model["size"]}]}
                elif route == "/api/show":
                    reply = {"details": model["details"],
                             "model_info": {"general.architecture": "qwen3", "qwen3.embedding_length": DIMENSIONS},
                             "capabilities": ["embedding"]}
                elif route == "/api/embed":
                    given = asked.get("input", "")
                    texts = [given] if isinstance(given, str) else list(given)
                    texts_seen.extend(texts)
                    reply = {"model": EMBED_MODEL, "embeddings": [stand_in_vector(text) for text in texts]}
                elif route == "/api/embeddings":
                    texts_seen.append(asked.get("prompt", ""))
                    reply = {"embedding": stand_in_vector(asked.get("prompt", ""))}
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


def _free_port():
    with socket.socket() as handle:
        handle.bind(("127.0.0.1", 0))
        return handle.getsockname()[1]


def lacking():
    """What this machine lacks for a rebuild with vectors, or None."""
    if shutil.which("gitleaks") is None:
        return "no gitleaks executable on PATH: the lexical index cannot be built (DEC-287)"
    if importlib.util.find_spec("sqlite_vec") is None:
        return "sqlite_vec cannot be imported: no vector can be stored (ADR-0002)"
    return None


def _git_env(home):
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "W2-91 tests", "GIT_AUTHOR_EMAIL": "w2-91@example.invalid",
            "GIT_COMMITTER_NAME": "W2-91 tests", "GIT_COMMITTER_EMAIL": "w2-91@example.invalid",
            "GIT_AUTHOR_DATE": "2026-10-01T12:00:00+00:00", "GIT_COMMITTER_DATE": "2026-10-01T12:00:00+00:00"}


def planted_path_map(namespaces):
    """A full path map: this repository's own, with ``namespaces`` in place of its namespaces, no register file and
    no code index."""
    document = yaml.safe_load(path_map_text_at(None))
    document.pop("decision_register", None)  # the planted project holds no register file
    document["namespaces"] = namespaces
    document.setdefault("capabilities", {})["code_intelligence"] = {"enabled": False}
    return yaml.safe_dump(document, sort_keys=False)


def plant(project, namespaces, files):
    """A planted git repository: ``files`` (rel -> text), the path map and the gitleaks rules, committed."""
    project = Path(project)
    home = project.parent / f"{project.name}-home"
    home.mkdir(parents=True, exist_ok=True)
    project.mkdir(parents=True, exist_ok=True)
    env = _git_env(home)
    subprocess.run(["git", "init", "-q", "-b", "main", str(project)], check=True, env=env, capture_output=True)
    every = {**files, ".gitignore": ".gov-runtime/\n", PATH_MAP_REL: planted_path_map(namespaces)}
    for rel, text in every.items():
        path = project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    shutil.copy2(ROOT / GITLEAKS_TEMPLATE_REL, project / ".gitleaks.toml")
    for args in (["add", "-A"], ["commit", "-q", "-m", "the planted corpus"]):
        subprocess.run(["git", "-C", str(project), *args], check=True, env=env, capture_output=True)
    return project


def _site(workdir):
    """A folder that links the one ``sqlite_vec`` this machine's Python imports (the scratch HOME has no user site
    folder to find it in), as W1-19 and W2-108 do."""
    spec = importlib.util.find_spec("sqlite_vec")
    origin = Path(spec.origin)
    source = origin.parent if spec.submodule_search_locations else origin
    site = workdir / "site"
    site.mkdir(parents=True, exist_ok=True)
    link = site / source.name
    if not link.is_symlink():
        link.symlink_to(source, target_is_directory=source.is_dir())
    return site


def rebuild(project, host):
    """``gov rebuild --json`` in ``project``, with the embedder at ``host``; the envelope."""
    project = Path(project)
    workdir = project.parent / f"{project.name}-run"
    for name in ("home", "tmp", "pycache"):
        (workdir / name).mkdir(parents=True, exist_ok=True)
    # No real ollama reachable: every PATH folder holding one is dropped. The tools the rebuild needs are resolved on
    # the full PATH first and linked from a scratch folder, so a dropped folder (~/.local/bin, which holds the ollama
    # wrapper beside gitleaks) takes no tool away with it; the dropped folder itself is never put back.
    full = os.environ.get("PATH", "/usr/bin:/bin")
    tools = workdir / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    for name in ("gitleaks",):
        found = shutil.which(name, path=full)
        link = tools / name
        if found and not link.is_symlink():
            link.symlink_to(Path(found).resolve())
    path = os.pathsep.join([str(tools), *(folder for folder in full.split(os.pathsep)
                                          if folder and not (Path(folder) / "ollama").exists())])
    assert not (tools / "ollama").exists(), "the scratch tools folder must hold no ollama"
    env = {"PATH": path, "HOME": str(workdir / "home"), "TMPDIR": str(workdir / "tmp"), "LC_ALL": "C.UTF-8",
           "GIT_CONFIG_NOSYSTEM": "1", "PYTHONPATH": os.pathsep.join([str(GOV_SRC), str(_site(workdir))]),
           "PYTHONPYCACHEPREFIX": str(workdir / "pycache"), "OLLAMA_HOST": host, "GOV_QUERY_OLLAMA_HOST": host,
           "GOV_OLLAMA_BIN": str(workdir / "no-ollama"), "GOV_REBUILD_LOCK": str(workdir / "rebuild.lock"),
           "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "rebuild", "--json"], cwd=str(project), env=env,
                          capture_output=True, text=True, timeout=REBUILD_TIMEOUT_S)
    try:
        envelope = json.loads(done.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        raise AssertionError(f"gov rebuild gave no JSON (exit {done.returncode}):\n{done.stdout[-3000:]}\n"
                             f"{done.stderr[-3000:]}") from None
    semantic = (envelope.get("result") or {}).get("stores", {}).get("semantic", {})
    assert envelope.get("ok") is True and semantic.get("status") == "recreated", \
        f"the rebuild did not build the vectors: {json.dumps(envelope)[:3000]}\n{done.stderr[-3000:]}"
    return envelope


def store_paths(project):
    """From the store the rebuild wrote: the paths with a lexical chunk, and the paths with a vector."""
    connection = sqlite3.connect(Path(project) / STORE_REL)
    try:
        chunked = {rel for (rel,) in connection.execute("SELECT DISTINCT path FROM lexical_chunk")}
        vectors = {rel for (rel,) in connection.execute(
            "SELECT DISTINCT c.path FROM semantic_vector v JOIN lexical_chunk c ON c.chunk_id = v.chunk_id")}
    finally:
        connection.close()
    return chunked, vectors


def planted_text(rel):
    """An ordinary text for ``rel``, with words of its own so that each file is a chunk of its own."""
    words = " ".join(re.findall(r"[a-z]+", rel.lower())) or "root"
    return f"# Planted file\n\nThis planted note about {words} describes the harbour tide tables and the bakery.\n"


def namespace(paths, policy, sensitivity="internal", export_policy="allowed"):
    """A namespace with every field the schema asks for."""
    return {"paths": list(paths), "memory_class": "governance", "sensitivity": sensitivity,
            "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                                "independent-auditor", "research"],
            "retention": "kept in git history", "export_policy": export_policy, "embedding_policy": policy,
            "provenance": "written by the W2-91 tests", "deletion_rebuild": "authoritative; restored from git only"}
