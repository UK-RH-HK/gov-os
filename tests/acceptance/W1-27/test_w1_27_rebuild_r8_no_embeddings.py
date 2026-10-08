"""Round 8: ``gov rebuild`` has a mode without embeddings (DEC-530).

"`gov rebuild` gets a mode without embeddings, for closes and checks that need only fresh lexical and graph
indexes. A full rebuild with embeddings runs before W1-42's retrieval measurements."

The mode is an argument of ``gov rebuild`` (``--no-embeddings``); no command is added. What the cases hold:

- it builds everything a rebuild builds except the semantic vectors: the same record store digest, the
  lexical index recreated and answering, the code index with the outcome it has without the argument;
- it does not ask the embedding endpoint and does not start its program;
- its result says that the semantic store was not built because the mode was asked for, told apart from an
  endpoint that could not be used;
- without the argument nothing changes: the endpoint is asked, as today;
- a retrieval on a store without vectors says that the semantic route did not answer, and gives the lexical
  evidence as lexical.

The endpoint and its program are stand-ins of the cases' own: a loopback address that records every request
(it answers the version, and a model list without the embedding model, so nothing is ever embedded), and a
program that records that it was started. No model runs and nothing outside the loopback is asked.

Every project is a tiny temporary repository built from scratch (``support.make_rebuild_project``); the
code under test is this worktree's ``src``, given on ``PYTHONPATH``. Nothing of the repository is copied but
its ``.gitleaks.toml``.

Red reason of the cases that give the argument: ``gov rebuild`` takes no ``--no-embeddings`` (a usage
error, exit code 2). The cases without the argument hold today's behaviour and are green.
"""

from __future__ import annotations

import json
import os
import site
import sqlite3
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

import w1_27_support as support

base = support.base

MODE = "--no-embeddings"
SEMANTIC = "semantic"
LEXICAL = "lexical"
NOT_RECREATED = "not_recreated"
RECREATED = "recreated"
STORE_REL = ".gov-runtime/store.db"
FACET_UNAVAILABLE = "FACET_UNAVAILABLE"

PHRASE = "quillwort marmalade ledger"
NOTE_REL = "docs/note.md"
NOTE = f"# A note\n\nThe {PHRASE} is kept in the second drawer.\n"


class EndpointStandIn:
    """A loopback address where the embedding endpoint would be. It records every request. It answers the
    version (so it counts as reachable) and a model list that holds no model (so nothing is sent to be
    embedded); anything else is 404."""

    def __init__(self):
        self.requests = []
        requests = self.requests

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    self.rfile.read(length)
                requests.append(f"{self.command} {self.path}")
                route = self.path.split("?")[0].rstrip("/")
                reply = {"/api/version": {"version": "0.0.0"}, "/api/tags": {"models": []}}.get(route)
                payload = json.dumps(reply or {}).encode()
                self.send_response(200 if reply is not None else 404)
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


@pytest.fixture(scope="module")
def interface():
    """The envelope fields and exit codes of ``docs/interfaces/API-0002.yaml``, read from this worktree."""
    return base.load_interface(support.REPO_ROOT)


@pytest.fixture()
def endpoint():
    stand_in = EndpointStandIn()
    yield stand_in
    stand_in.close()


@pytest.fixture()
def program(tmp_path):
    """A program where the endpoint's would be: started, it writes ``started`` beside itself and ends."""
    folder = tmp_path / "program"
    folder.mkdir()
    script = folder / "ollama"
    script.write_text(f"#!/bin/sh\necho started >> '{folder / 'started'}'\n", encoding="utf-8")
    script.chmod(0o755)
    return script


def _was_started(program):
    return (program.parent / "started").exists()


@pytest.fixture()
def tiny(tmp_path):
    """A tiny project with a path map and one note that holds ``PHRASE``."""
    project = support.make_rebuild_project(support.REPO_ROOT, tmp_path / "repo")
    (project / "docs").mkdir()
    (project / NOTE_REL).write_text(NOTE, encoding="utf-8")
    support.commit_all(project, "a note")
    return project


@pytest.fixture()
def gov(tiny, sandbox, endpoint, program):
    """``gov(*args, project=None)`` runs this worktree's command line in the tiny project, in W1-07's stand-in
    environment with three things more: the per-user folder of installed packages of the interpreter running
    the suite (where ``sqlite_vec`` is, DEC-397), the stand-in endpoint and the stand-in program."""
    launcher = base.write_launcher(support.REPO_ROOT, sandbox)
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(support.REPO_ROOT / "src"),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "OLLAMA_HOST": endpoint.host,
        "GOV_OLLAMA_BIN": str(program),
        **({"PYTHONUSERBASE": site.getuserbase()} if site.ENABLE_USER_SITE else {}),
    }

    def _gov(*args, project=None):
        started = time.perf_counter()
        done = subprocess.run([sys.executable, str(launcher), *args], cwd=str(project or tiny), env=env,
                              capture_output=True, text=True, timeout=base.COMMAND_TIMEOUT_S,
                              stdin=subprocess.DEVNULL)
        return base.Run(tuple(args), done.returncode, done.stdout, done.stderr, time.perf_counter() - started)

    _gov.env = env
    return _gov


def _rebuilt(gov, interface, *args, project=None):
    """``gov rebuild <args> --json`` succeeded; its result."""
    run = gov("rebuild", *args, "--json", project=project)
    envelope = support.assert_envelope(run, interface, command="rebuild")
    assert envelope["ok"] is True and run.returncode == 0, f"gov rebuild {' '.join(args)} failed\n{run.describe()}"
    return envelope["result"]


def _vectors(project):
    """The number of vectors the project's store holds; 0 when it has no table of them."""
    connection = sqlite3.connect(Path(project) / STORE_REL)
    try:
        if connection.execute("SELECT 1 FROM sqlite_master WHERE name = 'semantic_vector'").fetchone() is None:
            return 0
        return connection.execute("SELECT COUNT(*) FROM semantic_vector").fetchone()[0]
    finally:
        connection.close()


def _the_interpreter_finds_sqlite_vec(gov):
    done = subprocess.run([sys.executable, "-c", "import sqlite_vec"], env=gov.env, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL)
    return done.returncode == 0


# =========================================================================== #
# Without the argument nothing changes
# =========================================================================== #

def test_a_rebuild_without_the_argument_asks_the_endpoint_as_today(gov, interface, endpoint, tiny):
    """The full rebuild stays the default. This is also the premise of the cases below: in this environment a
    rebuild that builds vectors does ask the stand-in, so "nothing was asked" measures something."""
    if not _the_interpreter_finds_sqlite_vec(gov):
        pytest.skip("this machine has no sqlite_vec: a rebuild gives up on the vectors before it asks the endpoint")

    result = _rebuilt(gov, interface)

    assert endpoint.requests, "a rebuild without the argument asked the embedding endpoint nothing"
    semantic = result["stores"][SEMANTIC]
    assert semantic["status"] == NOT_RECREATED, f"the stand-in holds no model, yet: {semantic}"
    assert MODE not in str(semantic.get("reason")), f"the reason names a mode nobody asked for: {semantic}"
    assert semantic.get("requested") is not False, f"the vectors are given as not asked for: {semantic}"


# =========================================================================== #
# The mode
# =========================================================================== #

def test_the_mode_asks_the_endpoint_nothing_and_starts_no_program(gov, interface, endpoint, program):
    _rebuilt(gov, interface, MODE)

    assert endpoint.requests == [], f"a rebuild without embeddings asked the embedding endpoint: {endpoint.requests}"
    assert not _was_started(program), "a rebuild without embeddings started the endpoint's program"


def test_the_mode_starts_no_program_when_the_endpoint_is_down(gov, interface, endpoint, program):
    """With the endpoint down a rebuild that wants vectors starts its program and waits for it (W1-18). The
    mode wants none: the program is not started."""
    endpoint.close()

    _rebuilt(gov, interface, MODE)

    assert not _was_started(program), "a rebuild without embeddings started the endpoint's program"


def test_the_mode_says_the_semantic_store_was_not_built_because_it_was_not_asked_for(gov, interface):
    result = _rebuilt(gov, interface, MODE)

    semantic = (result.get("stores") or {}).get(SEMANTIC) or {}
    assert semantic.get("status") == NOT_RECREATED, f"the semantic store's outcome: {semantic}"
    assert semantic.get("requested") is False, \
        f"the result does not say that the vectors were not asked for (`requested: false`): {semantic}"
    reason = str(semantic.get("reason") or "")
    assert MODE in reason, f"the reason does not name the argument that asked for it: {semantic}"
    assert "unavailable" not in reason.lower() and "ollama" not in reason.lower(), \
        f"the reason reads as an endpoint that could not be used: {semantic}"


def test_the_mode_builds_everything_else_a_rebuild_builds(gov, interface, tiny, tmp_path):
    """Two projects with the same commits: one rebuilt without the argument, one with it. The record store's
    digest is the same; the lexical index is recreated in both; the code index has the same outcome; and the
    store of the mode holds no vector."""
    twin = tmp_path / "twin"
    base.git(tmp_path, "clone", "-q", str(tiny), str(twin))

    full = _rebuilt(gov, interface, project=twin)
    lean = _rebuilt(gov, interface, MODE)

    assert lean["digest"] == full["digest"], "the mode gives another record store digest than a full rebuild"
    assert lean["stores"][LEXICAL] == full["stores"][LEXICAL] == {"status": RECREATED}, \
        f"the lexical index: {lean['stores'][LEXICAL]} with the mode, {full['stores'][LEXICAL]} without"
    assert lean["stores"]["codeintel"]["status"] == full["stores"]["codeintel"]["status"], \
        f"the code index: {lean['stores']['codeintel']} with the mode, {full['stores']['codeintel']} without"
    assert sorted(lean["stores"]) == sorted(full["stores"]), "the mode names other stores than a full rebuild"
    assert _vectors(tiny) == 0, "the store of a rebuild without embeddings holds vectors"


def test_two_rebuilds_in_the_mode_give_the_same_digest(gov, interface):
    assert _rebuilt(gov, interface, MODE)["digest"] == _rebuilt(gov, interface, MODE)["digest"]


def test_the_mode_writes_only_under_gov_runtime(gov, interface, tiny, sandbox):
    before = support.snapshot(tiny)
    before_elsewhere = support.snapshot(sandbox.elsewhere, skip=())

    _rebuilt(gov, interface, MODE)

    assert not support.snapshot_difference(before, support.snapshot(tiny)), "the mode wrote outside .gov-runtime/"
    assert not support.snapshot_difference(before_elsewhere, support.snapshot(sandbox.elsewhere, skip=()))


# =========================================================================== #
# What a retrieval answers on a store without vectors
# =========================================================================== #

def _honest_bundle(gov, interface):
    """``gov retrieve PHRASE``: the semantic route is given as not answering, with a reason; the stopping
    reason says a facet was unavailable; the note is cited, by the lexical route and not by the semantic."""
    run = gov("retrieve", PHRASE, "--json")
    envelope = support.assert_envelope(run, interface, command="retrieve")
    assert envelope["ok"] is True, f"gov retrieve failed on a store without vectors\n{run.describe()}"
    bundle = envelope["result"]
    semantic = bundle["facets"][SEMANTIC]
    assert semantic["available"] is False, f"the semantic route is given as answering without vectors: {semantic}"
    assert isinstance(semantic.get("reason"), str) and semantic["reason"].strip(), \
        f"the semantic route did not answer and no reason is given: {semantic}"
    assert bundle["facets"][LEXICAL]["available"] is True, f"the lexical route did not answer: {bundle['facets']}"
    assert bundle["stopping_reason"] == FACET_UNAVAILABLE, \
        f"the bundle's stopping reason does not say that a route did not answer: {bundle['stopping_reason']!r}"
    cited = [entry for entry in bundle["evidence"] if entry["path"] == NOTE_REL]
    assert cited, f"the lexical route did not find the note: {[entry['path'] for entry in bundle['evidence']]}"
    for entry in bundle["evidence"]:
        assert SEMANTIC not in entry["routes"], f"evidence is given as found by the semantic route: {entry}"
    return bundle


def test_a_retrieval_on_a_store_whose_vectors_could_not_be_built_says_so(gov, interface):
    """Today's behaviour, held: a rebuild without the argument at an endpoint that holds no model leaves no
    vectors, and the retrieval says that the semantic route did not answer."""
    _rebuilt(gov, interface)

    _honest_bundle(gov, interface)


def test_a_retrieval_on_a_store_rebuilt_without_embeddings_says_so(gov, interface, endpoint):
    _rebuilt(gov, interface, MODE)

    _honest_bundle(gov, interface)
