"""Builder tests for the Ollama lifecycle module (W1-18).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: the ``env`` argument, the order of the three executable
locations, and a ``GOV_OLLAMA_BIN`` that names a missing file. Loopback only;
no process is started.
"""
from __future__ import annotations

import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import ollama  # noqa: E402


def _free_host():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return f"127.0.0.1:{probe.getsockname()[1]}"


def _write_executable(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n", encoding="utf-8")
    path.chmod(0o755)
    return str(path)


def test_the_executable_is_looked_up_in_the_order_of_dec_260(tmp_path):
    env = {"PATH": str(tmp_path / "bin"), "HOME": str(tmp_path / "home")}
    assert ollama._executable(env) is None
    in_home = _write_executable(tmp_path / "home/.local/ollama/bin/ollama")
    assert ollama._executable(env) == in_home
    on_path = _write_executable(tmp_path / "bin/ollama")
    assert ollama._executable(env) == on_path
    assert ollama._executable({**env, "GOV_OLLAMA_BIN": "/named/by/the/variable"}) == "/named/by/the/variable"


def test_a_missing_executable_degrades_with_one_warning_and_does_not_raise(tmp_path, capsys):
    env = {"PATH": str(tmp_path), "HOME": str(tmp_path), "OLLAMA_HOST": _free_host(),
           "GOV_OLLAMA_BIN": str(tmp_path / "missing")}
    result = ollama.ensure_available(timeout_s=1, env=env)
    assert result == {"available": False, "started": False, "facet": "semantic", "state": "FACET_UNAVAILABLE",
                      "warning": ollama.WARNING}
    assert capsys.readouterr().err.count(ollama.WARNING) == 1


def test_a_healthy_endpoint_given_through_env_is_available_without_a_warning(tmp_path, capsys):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200 if self.path == ollama.HEALTH_PATH else 404)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
    try:
        env = {"PATH": str(tmp_path), "HOME": str(tmp_path), "OLLAMA_HOST": f"127.0.0.1:{server.server_port}"}
        result = ollama.ensure_available(timeout_s=2, env=env)
    finally:
        server.shutdown()
        server.server_close()
    assert result["available"] is True and result["started"] is False and result["warning"] is None
    assert capsys.readouterr().err == ""
