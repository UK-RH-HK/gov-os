"""S20: the query-wrapper removal (DEC-1037).

The product's automatic start of the query embedding server (``ensure_query_available`` with ``start``, in
``gov.retrieval.ollama``) carries everything the interim wrapper ``~/.local/bin/ollama`` adds: its CPUs and priority
from the gate's configuration file (as today); its device from that file (the GPU visible by default, or the CPU with
the GPU hidden), a malformed value shutting the start, named; none of a heavy slot's thread-budget variables
inherited by the server; its output appended to its own log; and one line per start in a start log naming the time,
the device and the caller (pid, working folder, command). Verify: unit tests with a stand-in executable that records
its environment, CPU affinity and niceness, started through ensure_query_available(start=True) with no wrapper on
PATH, one case per device and a planted thread budget [DEC-1037 (a), DEC-1037 (4), DEC-1038 (1)].

Interface (README, "The query server's start"): the device is ``embedding_servers.query.device`` in
``$HOME/.gov-os/machine/gate.json``, ``"gpu"`` (the default when absent) or ``"cpu"``; ``"cpu"`` starts the server
with ``CUDA_VISIBLE_DEVICES=-1``, ``"gpu"`` with no ``CUDA_VISIBLE_DEVICES`` of ``-1`` (a caller's ``-1`` removed). The
server's standard output and error are appended to ``$HOME/.gov-os/machine/embedding-query.log``; each start appends
one JSON line to ``$HOME/.gov-os/machine/embedding-starts.jsonl``: ``{"time", "server": "query", "device",
"caller": {"pid", "cwd", "command"}}``. The stand-in is the only ``ollama`` on PATH (no ``~/.local/bin``); the query
address is a free local port, never 11435.
"""

from __future__ import annotations

import datetime
import importlib
import json
import os
from pathlib import Path

import pytest

import w2_20_support as support

PLANTED_BUDGET = {var: "3" for var in support.THREAD_VARS} | {"NUMEXPR_MAX_THREADS": "3"}


def _start(machine, *, device="absent", caller_env=None):
    """Start the query server through ensure_query_available(start=True); return (result, the stand-in's record)."""
    ollama = importlib.import_module("gov.retrieval.ollama")
    cpus = support.allowed_cpus()
    query_cpus = cpus[-2:] if len(cpus) > 2 else cpus[-1:]
    nice = min(19, max(os.getpriority(os.PRIO_PROCESS, 0) + 2, 5))
    servers = machine.config_values()["embedding_servers"]
    servers["query"].update(cpus=support.cpu_list(query_cpus), nice=nice)
    if device != "absent":
        servers["query"]["device"] = device
    machine.open_config(embedding_servers=servers)
    folder, record = machine.plant_ollama()
    env = {"PATH": f"{folder}:{support.SAFE_PATH}", "HOME": str(machine.home), "TMPDIR": str(machine.base),
           "OLLAMA_HOST": f"127.0.0.1:{support.free_port()}",
           "GOV_QUERY_OLLAMA_HOST": f"127.0.0.1:{support.free_port()}", **PLANTED_BUDGET, **(caller_env or {})}
    result = ollama.ensure_query_available(start=True, env=env, timeout_s=0.5)
    return result, record, query_cpus, nice


def _record(record: Path) -> dict:
    support.wait_for(record.exists, "the stand-in server's start")
    return json.loads(record.read_text().splitlines()[-1])


def test_s20_the_start_takes_its_cpus_and_priority_from_the_gate_file(machine):
    _, record, cpus, nice = _start(machine)
    started = _record(record)
    assert started["argv"][:1] == ["serve"], started["argv"]
    assert started["affinity"] == sorted(cpus), started["affinity"]
    assert started["nice"] == nice, started["nice"]


@pytest.mark.parametrize("device, caller, hidden", [
    ("absent", {}, False),
    ("gpu", {"CUDA_VISIBLE_DEVICES": "-1"}, False),
    ("cpu", {}, True),
], ids=["no device: the GPU visible", "gpu: the GPU visible, a caller's -1 removed", "cpu: the GPU hidden"])
def test_s20_the_device_comes_from_the_gate_file(machine, device, caller, hidden):
    _, record, _, _ = _start(machine, device=device, caller_env=caller)
    seen = _record(record)["env"].get("CUDA_VISIBLE_DEVICES")
    if hidden:
        assert seen == "-1", f"device cpu, but the server sees CUDA_VISIBLE_DEVICES={seen!r}"
    else:
        assert seen != "-1", f"device {device}, but the server's GPU is hidden (CUDA_VISIBLE_DEVICES={seen!r})"


@pytest.mark.parametrize("device", ["tpu", "GPU please", 1], ids=["tpu", "a phrase", "a number"])
def test_s20_a_malformed_device_shuts_the_start_named(machine, device):
    result, record, _, _ = _start(machine, device=device)
    assert result.get("started") is False, f"a malformed device ({device!r}) started the server: {result}"
    assert not record.exists(), "the stand-in server was started"
    said = json.dumps(result)
    assert "device" in said, f"the answer does not name the device: {result}"


def test_s20_no_thread_budget_variable_is_inherited_by_the_server(machine):
    _, record, _, _ = _start(machine)
    env = _record(record)["env"]
    kept = {var: env[var] for var in support.THREAD_VARS if var in env}
    assert not kept, f"the server inherited a heavy slot's thread budget: {kept}"


def test_s20_the_output_is_appended_to_the_servers_own_log(machine):
    log = machine.registry / "embedding-query.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("an earlier start's line\n")
    _, record, _, _ = _start(machine)
    _record(record)
    support.wait_for(lambda: "W2-20 STAND-IN ERR" in log.read_text(), "the server's output in its log", 10)
    text = log.read_text()
    assert text.startswith("an earlier start's line\n"), f"the log was not appended to: {text!r}"
    assert "W2-20 STAND-IN OUT" in text and "W2-20 STAND-IN ERR" in text, text


@pytest.mark.parametrize("device, named", [("absent", "gpu"), ("cpu", "cpu")], ids=["gpu", "cpu"])
def test_s20_each_start_writes_one_line_naming_the_time_the_device_and_the_caller(machine, device, named):
    starts = machine.registry / "embedding-starts.jsonl"
    before = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=5)
    _, record, _, _ = _start(machine, device=device)
    _record(record)
    lines = [json.loads(line) for line in starts.read_text().splitlines() if line.strip()] if starts.exists() else []
    assert len(lines) == 1, f"one start, and the start log holds {len(lines)} lines: {lines}"
    line = lines[0]
    when = datetime.datetime.fromisoformat(str(line.get("time")))
    when = when if when.tzinfo else when.astimezone()
    assert before <= when <= datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=5), line
    assert line.get("device") == named, line
    caller = line.get("caller") or {}
    assert caller.get("pid") == os.getpid(), f"the caller's pid is not this process's: {line}"
    assert support.same_path(caller.get("cwd"), os.getcwd()), line
    own = Path("/proc/self/cmdline").read_bytes().split(b"\0")[0].decode()
    assert caller.get("command") and Path(own).name in json.dumps(caller["command"]), line

    _start(machine, device=device)
    support.wait_for(lambda: len(starts.read_text().splitlines()) == 2, "the second start's line", 10)
