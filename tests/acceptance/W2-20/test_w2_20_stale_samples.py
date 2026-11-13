"""R2-F1 (DEC-1105): the servers' kept CPU samples all expired never shut the gate on cpu at the first reading.

The review (round 2, R2-F1): "The first reading after ten quiet minutes shuts the gate on cpu. ``known()`` counts any
kept window sample of the server's process, however old, so a server is not resampled; the window is then filtered to
``KEEP_S`` (600 s), leaving it empty; ``now`` is null, and the gate shuts on cpu. A launch reads the gate once, so that
launch is refused." DEC-1105: a server whose kept readings have all expired is resampled before the cpu rule reads
it, so the gate never refuses a launch for stale readings. Lines: S2 (the gate judges real CPU use), S12 (both
servers' CPU p95 counted at admission), S19 (a launch is refused only while a reading is shut).

How (README, "The servers' CPU samples"): nothing about the servers is planted through ``GOV_RESOURCES_EMBEDDING_CPU``
or ``GOV_RESOURCES_EMBEDDING_CPU_NOW`` (both removed from the environment), so the gate takes the servers' use itself.
Two stand-in servers, ``ollama serve`` (a stand-in script of that name), each listen on a free local port named by
``OLLAMA_HOST`` (the shared one) and ``GOV_QUERY_OLLAMA_HOST`` (the query one), as ``gov.retrieval.ollama`` reads them,
and sit idle (never 11434 or 11435). The samples file ``$HOME/.gov-os/machine/embedding-cpu.jsonl`` is planted with a
history of each server whose pid is the live stand-in's and whose samples are all hours older than the keep window
(600 s), at the CPU time the stand-in really has (an idle server's history). Every other reading is planted within
(the support's defaults: 0.5 busy cores of 4). The first reading on that history must open on cpu, show a fresh
``embedding_cpu_now`` for both servers (a number, not null), and leave a fresh sample of each server in the file.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

import pytest

import w2_20_support as support
from test_w2_20_launch import launch  # noqa: F401  (the launch fixture: the real launcher, the session a stub)

SAMPLES_REL = ".gov-os/machine/embedding-cpu.jsonl"  # README, "The servers' CPU samples"
KEEP_S = 600                 # the keep window the review names
STALE_S = 3 * 3600           # the planted history's newest sample: hours past the keep window
HISTORY = 10                 # samples per server, one a minute
IDLE_MAX_CORES = 0.5         # an idle stand-in never shows half a core of use

# A stand-in ``ollama``: run as ``ollama serve``, it listens on OLLAMA_HOST (as the real server does), writes its pid
# to the ready file, and sits idle.
SERVER = r'''#!%(python)s
import os, socket, time
address, port = os.environ["OLLAMA_HOST"].rsplit(":", 1)
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind((address, int(port)))
listener.listen(16)
with open(os.environ["W2_20_READY"], "w") as f:
    f.write(str(os.getpid()))
time.sleep(600)
'''


def _cpu_seconds(pid: int) -> float:
    """The process's user + system CPU time, from ``/proc/<pid>/stat``."""
    fields = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()
    return (int(fields[11]) + int(fields[12])) / os.sysconf("SC_CLK_TCK")


def _idle_servers(machine) -> dict[str, dict]:
    """Start the two stand-in servers; ``{name: {"pid", "host", "setting"}}``."""
    folder = machine.base / "servers"
    folder.mkdir()
    script = folder / "ollama"
    script.write_text(SERVER % {"python": sys.executable})
    script.chmod(0o755)
    servers = {}
    for name, setting in (("shared", "OLLAMA_HOST"), ("query", "GOV_QUERY_OLLAMA_HOST")):
        host = f"127.0.0.1:{support.free_port()}"
        ready = machine.base / f"server-{name}.ready"
        machine._spawn([str(script), "serve"], cwd=str(folder),
                       env={"PATH": support.SAFE_PATH, "HOME": str(machine.home), "OLLAMA_HOST": host,
                            "W2_20_READY": str(ready)},
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        support.wait_for(lambda r=ready: r.exists() and r.read_text().strip(), f"the stand-in {name} server")
        servers[name] = {"pid": int(ready.read_text()), "host": host, "setting": setting}
    time.sleep(1.0)  # past their start-up: from here on they use no CPU
    return servers


def _plant_expired_history(machine, servers) -> list[dict]:
    """Every sample of both servers hours older than the keep window, at each live server's own pid and CPU time."""
    now = time.time()
    lines = []
    for name, server in servers.items():
        cpu = _cpu_seconds(server["pid"])
        for i in range(HISTORY):
            lines.append({"time": now - STALE_S - (HISTORY - 1 - i) * 60, "server": name, "pid": server["pid"],
                          "cpu_seconds": cpu})
    path = machine.home / SAMPLES_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(line) + "\n" for line in lines))
    assert all(now - line["time"] > KEEP_S for line in lines)
    return lines


def _fresh_samples(machine, servers, since: float) -> dict[str, list[dict]]:
    path = machine.home / SAMPLES_REL
    assert path.exists(), f"the samples file {SAMPLES_REL} is gone after the reading"
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return {name: [r for r in rows if r.get("server") == name and r.get("pid") == server["pid"]
                   and isinstance(r.get("time"), (int, float)) and r["time"] >= since - 1.0]
            for name, server in servers.items()}


@pytest.mark.parametrize("path", ["gov resources --check", "a launch"])
def test_r2_f1_expired_server_samples_are_taken_afresh_so_the_first_reading_opens_on_cpu(
        machine, repo, monkeypatch, request, path):
    """Both servers present and idle, their kept samples all three hours old: the first reading opens on cpu (the
    start check opens; the launch starts its session), the reading shows both servers' current use as a number, and
    the samples file then holds a sample of each server taken by that reading."""
    launch = request.getfixturevalue("launch") if path == "a launch" else None  # noqa: F811
    machine.located(repo)  # the suite's location check first (a plain reading on planted figures), never after
    servers = _idle_servers(machine)
    hosts = {server["setting"]: server["host"] for server in servers.values()}
    unplanted = {"GOV_RESOURCES_EMBEDDING_CPU": None, "GOV_RESOURCES_EMBEDDING_CPU_NOW": None}
    _plant_expired_history(machine, servers)
    began = time.time()

    if path == "gov resources --check":
        code, envelope, out, err = machine.check(repo, env_extra={**unplanted, **hosts})
        if envelope is not None and envelope.get("ok") is False:
            reasons = support.reasons_by_condition(support.refusal_of(code, envelope, out, err))
            pytest.fail(f"the first reading on an expired history shut the gate: {reasons}")
        reading = support.opened_of(code, envelope, out, err)
        now = reading.get("embedding_cpu_now")
        assert isinstance(now, dict), f"the servers' current use is not shown after their samples expired: {reading}"
        for name in servers:
            value = now.get(name)
            assert isinstance(value, (int, float)) and 0.0 <= value <= IDLE_MAX_CORES, (
                f"the {name} server is idle, but its current use reads {value!r}: {now}")
        p95 = reading.get("embedding_cpu_p95")
        assert isinstance(p95, dict) and all(isinstance(p95.get(n), (int, float)) for n in servers), (
            f"the servers' p95 is not a reading after their samples expired: {p95}")
    else:
        from gov.cli.errors import GovError

        for key in unplanted:
            monkeypatch.delenv(key, raising=False)
        for key, value in hosts.items():
            monkeypatch.setenv(key, value)
        try:
            code = launch("engineer", "DAEO-wrk01")
        except GovError as refused:
            pytest.fail(f"the first launch on an expired history was refused: {refused.code}: {refused.message}")
        assert code == 0 and len(launch.started) == 1, "the launch did not start its session"

    fresh = _fresh_samples(machine, servers, began)
    for name, rows in fresh.items():
        assert rows, (f"the reading took no fresh sample of the {name} server (pid {servers[name]['pid']}) into "
                      f"{SAMPLES_REL}: its expired history was taken as known")
