"""W2-20's DEC-1037 line: the query server's automatic start carries everything the interim wrapper adds.

A stand-in executable records its environment, CPU affinity and niceness; it is started through
``ensure_query_available(start=True)`` on a free loopback port with a temporary HOME and no wrapper on PATH. No real
Ollama, no GPU. Every process a test starts is stopped by it."""
from __future__ import annotations

import json
import os
import signal
import socket
import sys
import time

import pytest

from gov.retrieval import ollama

STANDIN = """#!{python}
import json, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
status = dict(line.split(":", 1) for line in open("/proc/self/status") if ":" in line)
with open(os.environ["STANDIN_LOG"], "a") as out:
    out.write(json.dumps({{"pid": os.getpid(), "argv": sys.argv[1:], "cpus": status["Cpus_allowed_list"].strip(),
                          "nice": os.getpriority(os.PRIO_PROCESS, 0), "env": dict(os.environ)}}) + "\\n")
print("stand-in serve output", flush=True)
host, port = os.environ["OLLAMA_HOST"].rsplit(":", 1)
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Length", "2"); self.end_headers(); self.wfile.write(b"{{}}")
    def log_message(self, *args):
        pass
HTTPServer((host, int(port)), Handler).serve_forever()
"""
BUDGET = {"OMP_NUM_THREADS": "2", "GOMAXPROCS": "2", "MKL_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2",
          "RAYON_NUM_THREADS": "2", "NUMEXPR_NUM_THREADS": "2", "NUMEXPR_MAX_THREADS": "2", "VECLIB_MAXIMUM_THREADS": "2",
          "GOV_HEAVY_THREAD_BUDGET": "2", "GOV_HEAVY_CPUS": "0-3", "GOV_HEAVY_SLOT": "1",
          "PYTEST_XDIST_AUTO_NUM_WORKERS": "2"}


def _free_host():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return f"127.0.0.1:{probe.getsockname()[1]}"


@pytest.fixture
def stage(tmp_path):
    home, bindir = tmp_path / "home", tmp_path / "bin"
    home.mkdir()
    bindir.mkdir()
    program = bindir / "ollama"  # found on PATH, as the real binary would be once the wrapper is gone
    program.write_text(STANDIN.format(python=sys.executable))
    program.chmod(0o755)
    log = tmp_path / "standin.jsonl"
    env = {"PATH": f"{bindir}:/usr/bin:/bin", "HOME": str(home), "OLLAMA_HOST": _free_host(),
           "GOV_QUERY_OLLAMA_HOST": _free_host(), "STANDIN_LOG": str(log), **BUDGET}
    lowest = ollama._cpu_list(sorted(os.sched_getaffinity(0))[:2])

    class Stage:
        pass
    s = Stage()
    s.home, s.env, s.log, s.cpus = home, env, log, lowest

    def gate(device=None, **extra):
        query = {"cpus": lowest, "nice": 7, **({"device": device} if device is not None else {}), **extra}
        (home / ".gov-os/machine").mkdir(parents=True, exist_ok=True)
        (home / ollama.GATE_REL).write_text(json.dumps({"embedding_servers": {"query": query}}))
    s.gate = gate

    def runs(count=1, seconds=10.0):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            found = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
            if len(found) >= count:
                return found
            time.sleep(0.05)
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    s.runs = runs
    yield s
    for run in runs(0, 0):
        try:
            os.kill(run["pid"], signal.SIGKILL)
        except OSError:
            pass


@pytest.mark.parametrize("device,caller,expected", [("gpu", None, None), ("gpu", "-1", None), ("gpu", "0", "0"),
                                                    (None, "-1", None), ("cpu", None, "-1"), ("cpu", "0", "-1")])
def test_the_query_start_takes_its_device_from_the_gate_file(stage, device, caller, expected):
    stage.gate(device)
    env = {**stage.env, **({"CUDA_VISIBLE_DEVICES": caller} if caller is not None else {})}
    result = ollama.ensure_query_available(start=True, timeout_s=15, env=env)
    assert result["available"] and result["started"], result
    [run] = stage.runs()
    assert run["env"].get("CUDA_VISIBLE_DEVICES") == expected
    assert run["cpus"] == stage.cpus and run["nice"] >= 7  # its CPUs and priority, as today


def test_no_thread_budget_variable_of_a_slot_reaches_the_server(stage):
    stage.gate("gpu")
    assert ollama.ensure_query_available(start=True, timeout_s=15, env=stage.env)["started"]
    [run] = stage.runs()
    assert not set(BUDGET) & set(run["env"]), sorted(set(BUDGET) & set(run["env"]))
    assert run["env"]["OLLAMA_HOST"] == stage.env["GOV_QUERY_OLLAMA_HOST"]


def test_the_server_output_goes_to_its_own_log_and_each_start_is_one_caller_line(stage):
    stage.gate("cpu")
    assert ollama.ensure_query_available(start=True, timeout_s=15, env=stage.env)["started"]
    stage.runs()
    output = stage.home / ollama.QUERY_LOG_REL
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and "stand-in serve output" not in output.read_text():
        time.sleep(0.05)
    assert "stand-in serve output" in output.read_text()
    [line] = (stage.home / ollama.QUERY_STARTS_REL).read_text().splitlines()
    assert "(cpu)" in line and f"caller pid {os.getpid()}" in line and f"cwd {os.getcwd()}" in line
    assert "pytest" in line or "python" in line  # the caller's command


def test_the_logs_may_be_named_in_the_gate_file(stage, tmp_path):
    stage.gate("gpu", log=str(tmp_path / "q.log"), start_log=str(tmp_path / "starts.log"))
    assert ollama.ensure_query_available(start=True, timeout_s=15, env=stage.env)["started"]
    stage.runs()
    assert "(gpu)" in (tmp_path / "starts.log").read_text()


@pytest.mark.parametrize("extra", [{"device": "tpu"}, {"device": 1}, {"log": "relative.log"}])
def test_an_unreadable_device_or_log_shuts_the_start_named(stage, extra):
    stage.gate(**extra)
    result = ollama.ensure_query_available(start=True, timeout_s=2, env=stage.env)
    assert not result["started"] and result["state"] == "CONFIG_INVALID"
    assert "embedding_servers.query." in result["warning"] and stage.runs(1, 0.3) == []


def test_the_shared_servers_start_drops_the_budget_too_and_keeps_its_streams_closed(stage):
    stage.env["OLLAMA_HOST"] = _free_host()
    (stage.home / ".gov-os/machine").mkdir(parents=True, exist_ok=True)
    result = ollama.ensure_available(start=True, timeout_s=15, env=stage.env)
    assert result["started"]
    [run] = stage.runs()
    assert not set(BUDGET) & set(run["env"])
    assert not (stage.home / ollama.QUERY_STARTS_REL).exists()  # the start log is the query server's alone
