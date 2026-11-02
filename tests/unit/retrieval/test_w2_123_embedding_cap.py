"""Builder tests for the capped embedding servers (W2-123; DEC-1014, DEC-1015 item 2, DEC-1017).

Regression evidence only (DEC-136). No real Ollama is reached: every test runs on free loopback ports with a temporary
``HOME``, a planted ``GOV_OLLAMA_BIN`` (a Python stand-in that records how it was started and starts a child that
records the same) or a stand-in endpoint in this process. Every process a test starts is stopped by that test.
"""
from __future__ import annotations

import json
import os
import signal
import socket
import struct
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import ollama  # noqa: E402

# The stand-in ``ollama``: ``serve`` records its CPUs, niceness and environment, starts a child that records the
# same, and answers /api/version and /api/embed (a vector, or none when STANDIN_MODE is "novector").
STANDIN = """#!{python}
import json, os, sys, subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
log = os.environ["STANDIN_LOG"]

def seen(who):
    status = dict(line.split(":", 1) for line in open("/proc/self/status") if ":" in line)
    with open(log, "a") as out:
        out.write(json.dumps({{"who": who, "pid": os.getpid(), "argv": sys.argv[1:],
            "cpus": status["Cpus_allowed_list"].strip(), "nice": os.getpriority(os.PRIO_PROCESS, 0),
            "parallel": os.environ.get("OLLAMA_NUM_PARALLEL"),
            "gpu": os.environ.get("CUDA_VISIBLE_DEVICES")}}) + "\\n")

if sys.argv[1:2] == ["child"]:
    seen("child")
    import time; time.sleep(600)
seen("serve")
subprocess.Popen([sys.executable, __file__, "child"])
mode = os.environ.get("STANDIN_MODE", "ok")
host, port = os.environ["OLLAMA_HOST"].rsplit("/", 1)[-1].rsplit(":", 1)

class Handler(BaseHTTPRequestHandler):
    def reply(self, body):
        data = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        self.reply({{"version": "stand-in"}})
    def do_POST(self):
        self.rfile.read(int(self.headers["Content-Length"]))
        self.reply({{"embeddings": [[0.5, 0.25]] if mode == "ok" else []}})
    def log_message(self, *args):
        pass

HTTPServer((host, int(port)), Handler).serve_forever()
"""


def _free_host():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return f"127.0.0.1:{probe.getsockname()[1]}"


@pytest.fixture
def stage(tmp_path):
    """A temporary HOME, two free ports, a planted executable and its log; every pid it logged is stopped after."""
    home = tmp_path / "home"
    home.mkdir()
    program = tmp_path / "bin/ollama"
    program.parent.mkdir()
    program.write_text(STANDIN.format(python=sys.executable), encoding="utf-8")
    program.chmod(0o755)
    log = tmp_path / "standin.jsonl"
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "OLLAMA_HOST": _free_host(),
           "GOV_QUERY_OLLAMA_HOST": _free_host(), "GOV_OLLAMA_BIN": str(program), "STANDIN_LOG": str(log)}

    class Stage:
        pass
    s = Stage()
    s.home, s.env, s.log, s.program = home, env, log, program
    s.runs = lambda: [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    def wait_runs(count, seconds=10.0):
        deadline = time.monotonic() + seconds
        while len(s.runs()) < count and time.monotonic() < deadline:
            time.sleep(0.05)
        return s.runs()
    s.wait_runs = wait_runs

    def gate(section):
        (home / ".gov-os/machine").mkdir(parents=True, exist_ok=True)
        (home / ollama.GATE_REL).write_text(json.dumps(section), encoding="utf-8")
    s.gate = gate
    yield s
    for run in s.runs():
        try:
            os.kill(run["pid"], signal.SIGKILL)
        except OSError:
            pass


def _highest(count):
    return ollama._cpu_list(sorted(os.sched_getaffinity(0))[-count:])


def test_the_shared_server_starts_under_the_default_cap_and_its_child_inherits_it(stage):
    result = ollama.ensure_available(timeout_s=15, env=stage.env)
    assert result["available"] and result["started"], result
    assert result["settings"] == {"parallel": 1, "cpus": _highest(8), "nice": 10, "source": "default"}
    runs = {run["who"]: run for run in stage.wait_runs(2)}
    assert runs["serve"]["argv"] == ["serve"]
    for run in runs.values():
        assert run["cpus"] == _highest(8) and run["nice"] >= 10 and run["parallel"] == "1", run


def test_the_query_server_starts_under_its_configured_cap_with_the_gpu_hidden(stage):
    stage.gate({"other": 1, "embedding_servers": {"query": {"parallel": 3, "cpus": "0-1", "nice": 15},
                                                  "shared": {"parallel": 2}}})
    result = ollama.ensure_query_available(timeout_s=15, env={**stage.env, "OLLAMA_NUM_PARALLEL": "9"})
    assert result["available"] and result["started"], result
    assert result["settings"] == {"parallel": 3, "cpus": "0-1", "nice": 15,
                                  "source": str(stage.home / ollama.GATE_REL)}
    for run in stage.wait_runs(2):
        assert (run["cpus"], run["nice"] >= 15, run["parallel"], run["gpu"]) == ("0-1", True, "3", "-1"), run


@pytest.mark.parametrize("section, key", [
    ("not json", "embedding_servers"),
    ([1, 2], "embedding_servers"),
    ({"embedding_servers": []}, "embedding_servers"),
    ({"embedding_servers": {"shared": "x"}}, "embedding_servers.shared"),
    ({"embedding_servers": {"shared": {"parallel": 0}}}, "embedding_servers.shared.parallel"),
    ({"embedding_servers": {"shared": {"parallel": True}}}, "embedding_servers.shared.parallel"),
    ({"embedding_servers": {"shared": {"nice": 20}}}, "embedding_servers.shared.nice"),
    ({"embedding_servers": {"shared": {"cpus": "5-2"}}}, "embedding_servers.shared.cpus"),
    ({"embedding_servers": {"shared": {"cpus": "100000"}}}, "embedding_servers.shared.cpus"),
    ({"embedding_servers": {"shared": {"probe_slow_s": 5, "probe_hung_s": 5}}},
     "embedding_servers.shared.probe_slow_s"),
])
def test_an_unreadable_value_refuses_the_start_and_names_the_key(stage, capsys, section, key):
    if section == "not json":
        stage.gate({})
        (stage.home / ollama.GATE_REL).write_text("{", encoding="utf-8")
    else:
        stage.gate(section)
    result = ollama.ensure_available(timeout_s=1, env=stage.env)
    assert (result["available"], result["started"], result["state"], result["settings"]) == \
        (False, False, "CONFIG_INVALID", None)
    assert key in result["warning"] and ollama.GATE_REL in result["warning"]
    assert capsys.readouterr().err.count(result["warning"]) == 1
    assert stage.runs() == []
    assert ollama.probe("shared", env=stage.env)["state"] == "CONFIG_INVALID"
    restart = ollama.safe_restart("shared", env=stage.env)
    assert restart["restarted"] is False and key in restart["reason"] and stage.runs() == []


@pytest.mark.parametrize("start", [ollama.ensure_available, ollama.ensure_query_available])
@pytest.mark.parametrize("missing", ["named", "nowhere"])
def test_no_executable_found_gives_the_result_of_w1_18_without_settings(stage, capsys, start, missing):
    env = {**stage.env, "PATH": str(stage.home)}
    if missing == "named":
        env["GOV_OLLAMA_BIN"] = str(stage.home / "missing")
    else:
        del env["GOV_OLLAMA_BIN"]
    result = start(timeout_s=1, env=env)
    assert result == {"available": False, "started": False, "facet": "semantic", "state": "FACET_UNAVAILABLE",
                      "warning": ollama.WARNING}
    assert capsys.readouterr().err.count(ollama.WARNING) == 1


def test_an_executable_that_cannot_start_still_states_its_settings(stage):
    stage.program.chmod(0o644)  # there, but not executable: a start attempted, not one without an executable
    result = ollama.ensure_available(timeout_s=1, env=stage.env)
    assert (result["available"], result["started"], result["state"]) == (False, False, "FACET_UNAVAILABLE")
    assert result["settings"] == {"parallel": 1, "cpus": _highest(8), "nice": 10, "source": "default"}


def test_an_unreadable_value_comes_before_a_missing_executable(stage):
    stage.gate({"embedding_servers": {"shared": {"nice": -1}}})
    result = ollama.ensure_available(timeout_s=1, env={**stage.env, "GOV_OLLAMA_BIN": str(stage.home / "missing")})
    assert (result["state"], result["settings"]) == ("CONFIG_INVALID", None)


class _Endpoint:
    """An in-process stand-in /api/embed: ``answer(text)`` gives the vector, or None for an answer without one."""

    def __init__(self, answer, delay=0.0):
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                time.sleep(delay)
                vector = answer(body["input"][0])
                data = json.dumps({"embeddings": [] if vector is None else [vector]}).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.host = f"127.0.0.1:{self.server.server_port}"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.mark.parametrize("delay, vector, state", [(0.0, [0.1], "healthy"), (0.6, [0.1], "slow"),
                                                  (0.0, None, "hung"), (2.0, [0.1], "hung")])
def test_the_probe_states_healthy_slow_hung(stage, delay, vector, state):
    stage.gate({"embedding_servers": {"shared": {"probe_slow_s": 0.3, "probe_hung_s": 1.0}}})
    endpoint = _Endpoint(lambda text: vector, delay)
    try:
        result = ollama.probe("shared", env={**stage.env, "OLLAMA_HOST": endpoint.host})
    finally:
        endpoint.close()
    assert (result["server"], result["host"], result["state"]) == ("shared", endpoint.host, state), result


def test_the_probe_states_down_and_starts_nothing(stage):
    result = ollama.probe("query", env=stage.env)
    assert (result["state"], result["seconds"], result["host"]) == ("down", None, stage.env["GOV_QUERY_OLLAMA_HOST"])
    assert stage.runs() == []


def test_a_safe_restart_leaves_an_answering_server_alone_and_records_nothing(stage):
    endpoint = _Endpoint(lambda text: [0.1])
    try:
        result = ollama.safe_restart("shared", env={**stage.env, "OLLAMA_HOST": endpoint.host})
    finally:
        endpoint.close()
    assert result["restarted"] is False and "answering" in result["reason"] and result["probe"]["state"] == "healthy"
    assert not (stage.home / ollama.RESTARTS_REL).exists()


def test_a_safe_restart_never_stops_a_port_held_by_another_process(stage):
    stage.gate({"embedding_servers": {"shared": {"probe_slow_s": 0.2, "probe_hung_s": 0.5}}})
    endpoint = _Endpoint(lambda text: None)  # held by this test's own process, which is not `ollama serve`
    try:
        result = ollama.safe_restart("shared", env={**stage.env, "OLLAMA_HOST": endpoint.host})
    finally:
        endpoint.close()
    assert result["restarted"] is False and str(os.getpid()) in result["reason"], result
    assert result["probe"]["state"] == "hung" and stage.runs() == []


def test_a_safe_restart_starts_a_down_server_under_its_cap_and_records_it(stage):
    stage.gate({"embedding_servers": {"query": {"cpus": "0", "nice": 12}}})
    result = ollama.safe_restart("query", env=stage.env)
    assert (result["restarted"], result["old_pid"], result["probe"]["state"]) == (True, None, "down"), result
    assert "down" in result["reason"] and result["new_pid"] == stage.wait_runs(1)[0]["pid"]
    assert all(run["cpus"] == "0" and run["nice"] >= 12 and run["gpu"] == "-1" for run in stage.wait_runs(2))
    record = [json.loads(line) for line in (stage.home / ollama.RESTARTS_REL).read_text().splitlines()]
    assert len(record) == 1 and record[0]["probe_state"] == "down" and record[0]["settings"]["cpus"] == "0"


def test_a_safe_restart_stops_a_hung_serve_with_its_child_and_starts_it_capped(stage):
    stage.gate({"embedding_servers": {"shared": {"probe_slow_s": 0.2, "probe_hung_s": 0.5, "parallel": 2}}})
    first = ollama.ensure_available(timeout_s=15, env={**stage.env, "STANDIN_MODE": "novector"})
    assert first["started"], first
    old = {run["who"]: run["pid"] for run in stage.wait_runs(2)}
    result = ollama.safe_restart("shared", env=stage.env)
    assert result["restarted"] is True and result["old_pid"] == old["serve"], result
    assert ollama._stat(old["serve"]) is None and ollama._stat(old["child"]) is None
    new = [run for run in stage.wait_runs(4) if run["pid"] not in old.values()]
    assert result["new_pid"] == next(run["pid"] for run in new if run["who"] == "serve")
    assert all(run["cpus"] == _highest(8) and run["nice"] >= 10 and run["parallel"] == "2" for run in new)
    assert ollama.probe("shared", env=stage.env)["state"] == "healthy"
    record = [json.loads(line) for line in (stage.home / ollama.RESTARTS_REL).read_text().splitlines()]
    assert [(line["old_pid"], line["new_pid"], line["probe_state"]) for line in record] == \
        [(old["serve"], result["new_pid"], "hung")]


def _blob(vector):
    return struct.pack(f"{len(vector)}f", *vector)


def test_the_determinism_check_accepts_equal_vectors_and_refuses_a_change_or_a_missing_answer():
    texts = [f"chunk {n}" for n in range(12)]
    vectors = {text: [n / 7, -n / 3, 0.1] for n, text in enumerate(texts)}
    references = [(text, _blob(vectors[text])) for text in texts]
    steady = _Endpoint(lambda text: vectors[text], 0.01)
    drifting = _Endpoint(lambda text: [v + 1e-6 for v in vectors[text]] if text == "chunk 3" else vectors[text])
    missing = _Endpoint(lambda text: None if text == "chunk 5" else vectors[text])
    try:
        assert ollama.check_determinism(steady.host, references, 4) == \
            {"parallel": 4, "checked": 12, "differing": [], "verdict": "accepted"}
        assert ollama.check_determinism(drifting.host, references, 2)["differing"] == [3]
        assert ollama.check_determinism(missing.host, references, 8) == \
            {"parallel": 8, "checked": 12, "differing": [5], "verdict": "refused"}
        assert ollama.check_determinism(steady.host, [], 1)["verdict"] == "refused"
    finally:
        for endpoint in (steady, drifting, missing):
            endpoint.close()


def test_the_defaults_are_the_measured_ones_and_the_evidence_states_their_choice():
    evidence = (REPO / "docs" / "changes" / "W2-123-evidence.md").read_text(encoding="utf-8")
    chosen = [line for line in evidence.splitlines() if line.startswith("Chosen setting:")]
    assert len(chosen) == 1
    assert "parallel requests 1 for both servers" in chosen[0] and "8 logical CPUs at nice 10" in chosen[0]
    assert ollama.DEFAULT_PARALLEL == {"shared": 1, "query": 1}
    assert (ollama.DEFAULT_CPU_COUNT, ollama.DEFAULT_NICE) == (8, 10)
    assert (ollama.DEFAULT_PROBE_SLOW_S, ollama.DEFAULT_PROBE_HUNG_S) == (10.0, 120.0)
