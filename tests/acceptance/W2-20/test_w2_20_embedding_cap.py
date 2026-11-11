"""S12: the durable CPU cap of both embedding servers (a planted restart).

The gate's configuration file holds each server's logical CPUs and lower priority, inherited by their runner
processes, which their start (W2-123) reads; a planted restart of either server shows the cap applied, so a restart
never loses it [ACT-OLLAMA-CAP-1, ACT-OLLAMA-CAP-2, DEC-1010 item 7, DEC-1017]. (The p95 at admission:
``test_w2_20_cpu.py``.)

The restart is ``gov.retrieval.ollama.safe_restart(server, env=...)`` on a server that is down (a free local port,
never 11434 or 11435), with a stand-in ``ollama`` first on a PATH that has no wrapper; the stand-in records its CPU
affinity and niceness and ends.
"""

from __future__ import annotations

import importlib
import json
import os

import pytest

import w2_20_support as support


@pytest.mark.parametrize("server", ["shared", "query"])
def test_s12_a_planted_restart_of_either_server_applies_the_cap_from_the_gate_file(machine, server):
    ollama = importlib.import_module("gov.retrieval.ollama")
    cpus = support.allowed_cpus()
    cap = {"shared": cpus[:1], "query": cpus[1:2] or cpus[:1]}
    nice = min(19, max(os.getpriority(os.PRIO_PROCESS, 0) + 3, 7))
    machine.open_config(embedding_servers={
        name: {"cpus": support.cpu_list(cap[name]), "nice": nice, "date": support.today(), "source": "planted"}
        for name in ("shared", "query")})
    folder, record = machine.plant_ollama()
    env = {"PATH": f"{folder}:{support.SAFE_PATH}", "HOME": str(machine.home), "TMPDIR": str(machine.base),
           "OLLAMA_HOST": f"127.0.0.1:{support.free_port()}",
           "GOV_QUERY_OLLAMA_HOST": f"127.0.0.1:{support.free_port()}"}

    result = ollama.safe_restart(server, env=env)
    support.wait_for(record.exists, "the stand-in server's start")
    started = json.loads(record.read_text().splitlines()[-1])
    assert started["argv"][:1] == ["serve"], started["argv"]
    assert started["affinity"] == sorted(cap[server]), f"the {server} server lost its CPU cap: {started['affinity']}"
    assert started["nice"] == nice, f"the {server} server lost its lower priority: {started['nice']}"
    assert result.get("restarted") is True, f"the restart did not start the server: {result}"
