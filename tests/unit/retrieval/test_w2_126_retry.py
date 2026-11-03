"""Builder tests for W2-126 KPI 7: the bounded retry (W2-123, DEC-1026) also covers a transient server error (HTTP
5xx) and a reset or refused connection, within the same bound, and still fails closed after its last try (P-W2-123-4,
DEC-1042 item 4).

Regression evidence only (DEC-136). The shared runner is a stand-in HTTP endpoint on a free port of 127.0.0.1 that
answers each ``/api/embed`` request as its plan says; the real servers are never asked. ``TIMEOUT_S`` and
``RETRY_WAITS_S`` are lowered so the tests run fast. Each project is a temporary git repository; the conftest gives
each test a machine-wide vector cache of its own, so every chunk is a miss.
"""
from __future__ import annotations

import json
import socket
import struct
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import lexical, semantic  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
FILES = {".gitignore": ".gov-runtime/\n", "governance/project/path-map.yaml":
         "namespaces:\n  open: {paths: ['open/**'], embedding_policy: embedded}\n",
         "open/pear.md": "pear trees\n", "open/plum.md": "plum trees\n"}
TIMEOUT = 0.3
WAITS = (0.05, 0.1)
TAIL = "each under 0.3 s; waits 0.05 s, 0.1 s"


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@pytest.fixture()
def endpoint(tmp_path, monkeypatch):
    """The stand-in runner: ``plan`` is what each successive ``/api/embed`` request gets ("ok"; "hang" past the
    timeout; "500", "503" or "400", that status; "reset", the connection reset with no answer; "ok" once the plan is
    used up); ``seen`` counts the embed requests it accepted; ``host`` is its address."""
    state = {"plan": [], "seen": 0}
    stop = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            self._answer(200, {"models": [{"name": semantic.MODEL, "digest": "d" * 64}]})

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            state["seen"] += 1
            step = state["plan"].pop(0) if state["plan"] else "ok"
            if step == "hang":
                stop.wait(TIMEOUT * 4)
                return
            if step == "reset":  # SO_LINGER 0: the close sends a reset, not an orderly end
                self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
                self.connection.close()
                self.close_connection = True
                return
            if step.isdigit():
                return self._answer(int(step), {"error": "no"})
            self._answer(200, {"embeddings": [[float("pear" in text), 1.0] for text in body["input"]]})

        def _answer(self, code, payload):
            data = json.dumps(payload).encode()
            try:
                self.send_response(code)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except OSError:
                pass

        def finish(self):
            try:
                super().finish()
            except OSError:
                pass

    server = ThreadingHTTPServer(("127.0.0.1", _free_port()), Handler)
    server.daemon_threads, server.block_on_close = True, False
    threading.Thread(target=server.serve_forever, daemon=True).start()
    state["host"] = f"127.0.0.1:{server.server_address[1]}"
    bin_ = tmp_path / "bin" / "ollama"
    bin_.parent.mkdir()
    bin_.write_text("#!/bin/sh\nexit 1\n")
    bin_.chmod(0o755)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("OLLAMA_HOST", state["host"])
    monkeypatch.setenv("GOV_QUERY_OLLAMA_HOST", f"127.0.0.1:{_free_port()}")
    monkeypatch.setenv("GOV_OLLAMA_BIN", str(bin_))
    monkeypatch.setattr(semantic, "TIMEOUT_S", TIMEOUT)
    monkeypatch.setattr(semantic, "RETRY_WAITS_S", WAITS)
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None: None)
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    root = tmp_path / "project"
    root.mkdir()
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    for rel, text in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "files"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(root)})
    yield root, state
    stop.set()
    server.shutdown()
    server.server_close()


@pytest.mark.parametrize("plan", [["500"], ["503", "500"], ["reset"], ["reset", "502"], ["hang", "500"]])
def test_a_transient_failure_is_retried_and_the_answer_on_a_later_try_is_used(endpoint, plan):
    root, state = endpoint
    state["plan"] = list(plan)
    report = semantic.refresh(root)
    tries = len(plan) + 1
    assert (report["available"], report["reason"]) == (True, None)
    assert report["retries"] == [{"tries": tries, "waits_s": list(WAITS[:tries - 1]), "embedded": True}]
    assert state["seen"] == tries
    assert semantic.search(root, "pear", refresh=False)["reason"] != "stale"


@pytest.mark.parametrize("plan, named", [
    (["500", "500", "500", "ok"], "HTTP 500, HTTP 500, HTTP 500"),
    (["reset", "503", "hang", "ok"], "connection reset, HTTP 503, timed out"),
])
def test_after_the_last_transient_try_the_stage_stops_named_within_the_same_bound(endpoint, plan, named):
    root, state = endpoint
    state["plan"] = list(plan)
    report = semantic.refresh(root)
    assert (report["available"], report["state"]) == (False, "FACET_UNAVAILABLE")
    assert report["reason"] == f"{semantic.NO_EMBEDDING}: the request failed at all 3 tries ({named}; {TAIL})"
    assert report["retries"] == [{"tries": 3, "waits_s": list(WAITS), "embedded": False}]
    assert state["seen"] == 3  # the bound: never a fourth try
    answer = semantic.search(root, "pear", refresh=False)
    assert (answer["state"], answer["hits"]) == ("FACET_UNAVAILABLE", [])


def test_every_try_timed_out_keeps_w2_123_s_reason(endpoint):
    root, state = endpoint
    state["plan"] = ["hang", "hang", "hang"]
    report = semantic.refresh(root)
    assert report["reason"] == f"{semantic.NO_EMBEDDING}: the request timed out at all 3 tries ({TAIL})"


def test_a_refused_connection_is_retried_and_used_once_the_runner_listens(endpoint, monkeypatch):
    root, state = endpoint
    monkeypatch.setenv("OLLAMA_HOST", f"127.0.0.1:{_free_port()}")  # nothing listens there
    monkeypatch.setattr(semantic, "_revision", lambda host=None: "d" * 64)
    slept = []

    def sleep(seconds):  # the runner comes up during the first wait
        slept.append(seconds)
        monkeypatch.setenv("OLLAMA_HOST", state["host"])

    monkeypatch.setattr(semantic.time, "sleep", sleep)
    report = semantic.refresh(root)
    assert (report["available"], report["reason"]) == (True, None)
    assert report["retries"] == [{"tries": 2, "waits_s": [WAITS[0]], "embedded": True}]
    assert slept == [WAITS[0]] and state["seen"] == 1


def test_a_connection_refused_at_every_try_fails_closed_named(endpoint, monkeypatch):
    root, state = endpoint
    monkeypatch.setenv("OLLAMA_HOST", f"127.0.0.1:{_free_port()}")
    monkeypatch.setattr(semantic, "_revision", lambda host=None: "d" * 64)
    report = semantic.refresh(root)
    named = "connection refused, connection refused, connection refused"
    assert report["reason"] == f"{semantic.NO_EMBEDDING}: the request failed at all 3 tries ({named}; {TAIL})"
    assert report["retries"] == [{"tries": 3, "waits_s": list(WAITS), "embedded": False}]


@pytest.mark.parametrize("step", ["400", "404"])
def test_a_client_error_is_not_transient_and_ends_at_once(endpoint, step):
    root, state = endpoint
    state["plan"] = [step]
    report = semantic.refresh(root)
    assert (report["reason"], report["retries"], state["seen"]) == (semantic.NO_EMBEDDING, [], 1)


@pytest.mark.parametrize("step", ["500", "reset"])
def test_the_question_s_embedding_is_still_not_retried(endpoint, step):
    root, state = endpoint
    state["plan"] = [step]
    assert semantic._embed(["q"]) is None
    assert state["seen"] == 1
