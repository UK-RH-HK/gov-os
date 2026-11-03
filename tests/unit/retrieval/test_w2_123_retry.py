"""Builder tests for W2-123 run 2: a rebuild's timed-out embedding request is retried, bounded (DEC-1026).

Regression evidence only (DEC-136). The shared runner is a stand-in HTTP endpoint on a free port of 127.0.0.1 that
accepts each request and, for the tries it is told to, holds it past ``TIMEOUT_S``; the real servers are never asked.
``TIMEOUT_S`` and ``RETRY_WAITS_S`` are lowered so the tests run fast. Each project is a temporary git repository.
"""
from __future__ import annotations

import json
import socket
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
REASON = (f"{semantic.NO_EMBEDDING}: the request timed out at all 3 tries (each under 0.3 s; waits 0.05 s, 0.1 s)")


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@pytest.fixture()
def endpoint(tmp_path, monkeypatch):
    """The stand-in runner: ``plan`` is what each successive ``/api/embed`` request gets ("ok", "hang" past the
    timeout, or an HTTP status such as "400"; "ok" once the plan is used up); ``seen`` counts the embed requests it
    accepted."""
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

    server = ThreadingHTTPServer(("127.0.0.1", _free_port()), Handler)
    server.daemon_threads, server.block_on_close = True, False
    threading.Thread(target=server.serve_forever, daemon=True).start()
    bin_ = tmp_path / "bin" / "ollama"
    bin_.parent.mkdir()
    bin_.write_text("#!/bin/sh\nexit 1\n")
    bin_.chmod(0o755)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("OLLAMA_HOST", f"127.0.0.1:{server.server_address[1]}")
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
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})
    yield root, state
    stop.set()
    server.shutdown()
    server.server_close()


def test_the_defaults_are_three_tries_with_a_growing_wait_each_under_the_timeout():
    assert semantic.TIMEOUT_S == 120.0 and semantic.RETRY_WAITS_S == (10.0, 30.0)


def test_a_request_that_answers_on_its_third_try_is_used_and_the_tries_are_reported(endpoint):
    root, state = endpoint
    state["plan"] = ["hang", "hang"]
    report = semantic.refresh(root)
    assert report["available"] is True and report["reason"] is None
    assert report["retries"] == [{"tries": 3, "waits_s": [0.05, 0.1], "embedded": True}]
    assert state["seen"] == 3
    assert semantic.search(root, "pear", refresh=False)["reason"] != "stale"


def test_after_the_last_timed_out_try_the_stage_stops_named_and_the_part_built_is_not_reported_built(endpoint,
                                                                                                    monkeypatch):
    root, state = endpoint
    monkeypatch.setattr(semantic, "BATCH", 1)
    state["plan"] = ["ok", "hang", "hang", "hang", "ok"]
    report = semantic.refresh(root)
    assert (report["available"], report["state"], report["reason"]) == (False, "FACET_UNAVAILABLE", REASON)
    assert report["retries"] == [{"tries": 3, "waits_s": [0.05, 0.1], "embedded": False}]
    assert state["seen"] == 4  # no later batch is sent
    answer = semantic.search(root, "pear", refresh=False)
    assert (answer["state"], answer["reason"], answer["hits"]) == ("FACET_UNAVAILABLE", "stale", [])


def test_a_4xx_ends_at_once_with_no_embedding(endpoint):
    """A client error is not transient: no retry (W2-126 KPI 7 retries a 5xx, P-W2-126-BT)."""
    root, state = endpoint
    state["plan"] = ["400"]
    report = semantic.refresh(root)
    assert (report["reason"], report["retries"], state["seen"]) == (semantic.NO_EMBEDDING, [], 1)


def test_a_refused_connection_is_retried_within_the_bound_then_named(endpoint, monkeypatch):
    """W2-126 KPI 7 (P-W2-126-BT): a refused connection is tried again, at most 3 tries, then the stage stops named."""
    root, state = endpoint
    monkeypatch.setenv("OLLAMA_HOST", f"127.0.0.1:{_free_port()}")
    monkeypatch.setattr(semantic, "_revision", lambda host=None: "d" * 64)
    report = semantic.refresh(root)
    named = ", ".join(["connection refused"] * 3)
    assert report["reason"] == (f"{semantic.NO_EMBEDDING}: the request failed at all 3 tries ({named}; "
                                "each under 0.3 s; waits 0.05 s, 0.1 s)")
    assert report["retries"] == [{"tries": 3, "waits_s": [0.05, 0.1], "embedded": False}]


def test_nothing_timed_out_gives_an_empty_list_and_the_question_s_embedding_is_not_retried(endpoint):
    root, state = endpoint
    assert semantic.refresh(root)["retries"] == []
    seen = state["seen"]
    state["plan"] = ["hang"]
    assert semantic._embed(["q"]) is None
    assert state["seen"] == seen + 1
