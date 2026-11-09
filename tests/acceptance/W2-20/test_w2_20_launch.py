"""S19: enforcement at launch (DEC-1088 (5)(b)).

gov launch refuses any session, lead or worker, while the gate is shut on any of its readings (load, CPU, memory,
disk, inodes, a heavy-job slot, the GPU for a start that declares a need) or when the new session's working size
would pass a limit, naming the limit and its reading; one recorded override (gate_override: <DEC-id> on the launch)
starts it anyway, and the override is written in the launch log and the plan's output. Verify: unit tests with each
reading planted shut, and with the override [DEC-1088 (5), DEC-899].

How: the real launcher (``gov.launch.launcher.launch``) and the real gate, in this process, with the readings planted
through the environment and a temporary HOME; everything of the launch that is not the gate is replaced (the
repository's settings check, the ticket check, the worker's settings, the runs folder, W2-136's plan check, which
admits), and ``subprocess.Popen`` of the CLI is a stub: no session ever starts. Interface (README, "The launch"):
``launch(root, role, ticket, cli_args, gate_override=None, gpu_need_mib=None)``; ``gov launch ... --gate-override
DEC-NNN [--gpu-need-mib N]``. A refusal is ``GovError("LAUNCH_REFUSED", ...)`` whose message names each broken
condition and its reading. An override writes one line to ``$HOME/.gov-os/machine/launch.log`` and one line to
standard error, each holding ``gate_override: <DEC-id>``, the role, the ticket and the conditions it passed over.
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess

import pytest

import w2_20_support as support
from w2_20_support import GIB

ROLES = [("orchestrator", "DAEO-lead1"), ("engineer", "DAEO-wrk01")]
ROLE_IDS = ["a lead", "a worker"]


@pytest.fixture
def launch(machine, repo, monkeypatch):
    """``launch(role, ticket, **kw)`` -> exit code; ``launch.started`` lists the sessions the stub would start."""
    from gov.launch import launcher

    for key, value in machine.env().items():
        monkeypatch.setenv(key, value)
    for key in ("GOV_PLAN_READY", "GOV_ROLE", "GOV_TICKET"):
        monkeypatch.delenv(key, raising=False)
    (machine.home / ".local" / "bin").mkdir(parents=True, exist_ok=True)
    cli = machine.home / launcher.CLI_REL
    cli.write_text("")
    monkeypatch.setattr(launcher.tempfile, "tempdir", str(machine.base))
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)
    monkeypatch.setattr(launcher, "_check_ticket", lambda *args: None)
    monkeypatch.setattr(launcher, "build_settings", lambda root, role, ticket: {
        "env": {"GOV_ROLE": role, "GOV_TICKET": ticket}, "permissions": {"deny": []},
        "sandbox": {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
                    "network": {"strictAllowlist": True, "allowedDomains": []}}})
    monkeypatch.setattr(launcher.runs, "folder", lambda *args: None)
    monkeypatch.setattr(launcher.runs, "own_folder", lambda *args: None)
    monkeypatch.setattr(launcher, "check_lead", lambda *args, **kwargs: {
        "admitted": True, "reason": "STUB-W2-20: the plan admits", "override": None})

    started = []
    real_popen = subprocess.Popen

    class Session:  # the CLI's stand-in: nothing starts
        returncode = 0

        def wait(self):
            return 0

        def poll(self):
            return 0

        def kill(self):
            pass

    def popen(argv, *args, **kwargs):
        if str(argv[0]) == str(cli):
            started.append(kwargs.get("env"))
            return Session()
        return real_popen(argv, *args, **kwargs)  # anything else (a stand-in nvidia-smi) runs for real

    monkeypatch.setattr(launcher.subprocess, "Popen", popen)

    def _launch(role, ticket, **kwargs):
        return launcher.launch(repo, role, ticket, [], **kwargs)
    _launch.started = started
    return _launch


def _spellings(value) -> set[str]:
    out = {str(value)}
    if isinstance(value, float):
        out |= {repr(value), f"{value:g}", f"{value:.1f}", f"{value:.2f}"}
    return out


SHUT = {
    "memory": (lambda m: m.set_readings(available_bytes=1 * GIB), "memory", 1 * GIB),
    "working size": (lambda m: m.set_readings(available_bytes=4 * GIB - 1024), "memory", 4 * GIB - 1024),
    "load": (lambda m: m.set_readings(load=9.0, load_15=9.0), "load", 9.0),
    "cpu": (lambda m: m.set_readings(busy_cores=3.5, embedding_p95=(0.25, 0.25)), "cpu", 4.0),
    "disk": (lambda m: m.set_readings(free_bytes=50 * GIB), "disk", 50 * GIB),
    "inodes": (lambda m: m.set_readings(free_inodes=5_000_000), "inodes", 5_000_000),
    "config": (lambda m: m.open_config(memory_floor_bytes=None), "memory_floor_bytes", None),
}


@pytest.mark.parametrize("role, ticket", ROLES, ids=ROLE_IDS)
@pytest.mark.parametrize("planted", list(SHUT))
def test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading(
        machine, launch, role, ticket, planted):
    """Floor 3 GiB + the new session's 1 GiB: "memory" is far below, "working size" 1 KiB short of the need."""
    from gov.cli.errors import GovError

    plant, name, value = SHUT[planted]
    plant(machine)
    with pytest.raises(GovError) as refused:
        launch(role, ticket)
    assert refused.value.code == "LAUNCH_REFUSED", refused.value
    message = refused.value.message
    assert name in message, f"the refusal does not name {name}: {message}"
    if value is not None:
        assert any(s in message for s in _spellings(value)), f"the refusal does not give the reading {value}: {message}"
    assert launch.started == [], "a session was started although the gate is shut"


@pytest.mark.parametrize("role, ticket", ROLES, ids=ROLE_IDS)
def test_s19_a_launch_that_declares_a_gpu_need_is_refused_without_the_room(machine, launch, role, ticket):
    from gov.cli.errors import GovError

    machine.plant_gpu(gpus=[{"memory.total": 8192, "memory.used": 7692, "utilization.gpu": 50}])
    with pytest.raises(GovError) as refused:
        launch(role, ticket, gpu_need_mib=1000)
    assert refused.value.code == "LAUNCH_REFUSED" and "gpu" in refused.value.message.lower(), refused.value
    assert "500" in refused.value.message, f"the refusal does not give the free GPU memory: {refused.value.message}"
    assert launch.started == []


@pytest.mark.parametrize("role, ticket", ROLES, ids=ROLE_IDS)
def test_s19_guard_a_launch_starts_while_the_gate_is_open(machine, launch, role, ticket):
    assert launch(role, ticket) == 0
    assert len(launch.started) == 1


@pytest.mark.parametrize("role, ticket", ROLES, ids=ROLE_IDS)
def test_s19_the_override_starts_it_and_is_written_in_the_launch_log_and_the_output(
        machine, launch, capfd, role, ticket):
    machine.set_readings(available_bytes=1 * GIB)

    assert launch(role, ticket, gate_override="DEC-1234") == 0
    assert len(launch.started) == 1, "the override did not start the session"

    assert machine.launch_log.exists(), f"no launch log at {machine.launch_log}"
    lines = [line for line in machine.launch_log.read_text().splitlines() if "DEC-1234" in line]
    assert len(lines) == 1, machine.launch_log.read_text()
    for needed in ("gate_override", role, ticket, "memory"):
        assert needed in lines[0], f"the launch log's line does not hold {needed!r}: {lines[0]}"
    err = capfd.readouterr().err
    said = [line for line in err.splitlines() if "OVERRIDE" in line and "gate_override: DEC-1234" in line]
    assert said and "memory" in said[0], f"the launch's output does not show the override: {err}"


def test_s19_an_override_that_names_no_decision_is_refused(machine, launch):
    from gov.cli.errors import GovError

    machine.set_readings(available_bytes=1 * GIB)
    with pytest.raises(GovError) as refused:
        launch("engineer", "DAEO-wrk01", gate_override="because I say so")
    assert refused.value.code == "LAUNCH_REFUSED", refused.value
    assert launch.started == []


def test_s19_gov_launch_takes_the_override_and_the_gpu_need_on_its_command_line(repo, monkeypatch):
    command = importlib.import_module("gov.launch.command")
    from gov.launch import launcher

    calls = []
    monkeypatch.setattr(launcher, "launch", lambda *args, **kwargs: calls.append((args, kwargs)) or 0)
    parser = argparse.ArgumentParser()
    command.add_arguments(parser)
    args = parser.parse_args(["engineer", "DAEO-wrk01", "--gate-override", "DEC-1234", "--gpu-need-mib", "1000"])
    args.passthrough = []
    assert command.run(repo, args, {}) == 0
    assert calls, "gov launch did not call the launcher"
    (positional, keywords), = calls
    assert keywords.get("gate_override") == "DEC-1234", calls
    assert keywords.get("gpu_need_mib") == 1000, calls
    assert json.dumps([str(a) for a in positional]).count("DAEO-wrk01") == 1, calls
