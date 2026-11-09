"""KPI success 1: ``gov resources`` reads free memory, load, and every live Gov OS session on the machine from a
machine-wide registry under ``~/.gov-os/machine/``, whichever repository started it."""

from __future__ import annotations

import os
import subprocess
import sys

import w2_20_support as support
from w2_20_support import GIB


def test_the_suite_runs_this_worktrees_code():
    """DEC-732: the ``gov`` the suite runs is the one in this working tree's ``src/``."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONPATH": str(support.SRC),
           "PYTHONDONTWRITEBYTECODE": "1"}
    out = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], env=env, capture_output=True,
                         text=True, check=True, timeout=support.COMMAND_TIMEOUT_S).stdout.strip()
    assert os.path.realpath(out).startswith(os.path.realpath(support.SRC) + os.sep), out


def test_the_reading_reports_memory_load_processors_and_the_registry_folder(machine, repo):
    machine.open_config()
    machine.set_readings(available_bytes=16 * GIB, load=0.5, nproc=4)

    reading = machine.read(repo)

    assert reading.get("available_memory_bytes") == 16 * GIB, reading
    assert reading.get("load_1m") == 0.5, reading
    assert reading.get("nproc") == 4, reading
    assert support.same_path(reading["registry"], machine.registry) or os.path.realpath(
        reading["registry"]).startswith(os.path.realpath(machine.registry) + os.sep), reading
    assert reading.get("sessions") == [], f"an empty registry lists sessions: {reading}"
    assert reading.get("weighted_sessions") == 0, reading
    gate = support.gate_of(reading)
    assert gate["open"] is True and gate["reasons"] == [], reading


def test_every_live_session_is_read_with_its_pid_repository_ticket_role_and_weight(machine, repo):
    machine.open_config()
    light = machine.live_process()
    heavy = machine.live_process()

    machine.register(repo, light.pid, ticket="DAEO-lite", role="engineer")
    machine.register(repo, heavy.pid, ticket="DAEO-hevy", role="independent-auditor", heavy=True)

    reading = machine.read(repo)
    assert support.session_pids(reading) == sorted([light.pid, heavy.pid]), reading
    by_pid = {int(s["pid"]): s for s in reading["sessions"]}
    for pid, ticket, role, is_heavy in ((light.pid, "DAEO-lite", "engineer", False),
                                        (heavy.pid, "DAEO-hevy", "independent-auditor", True)):
        entry = by_pid[pid]
        assert support.same_path(entry.get("repository"), repo), entry
        assert entry.get("ticket") == ticket, entry
        assert entry.get("role") == role, entry
        assert entry.get("heavy") is is_heavy, entry
    assert reading.get("weighted_sessions") == 3, f"one light and one heavy session weigh 1 + 2: {reading}"

    assert machine.registry.is_dir() and any(p.is_file() for p in machine.registry.rglob("*")), (
        f"nothing was written under $HOME/.gov-os/machine/ ({machine.registry})")


def test_the_registry_belongs_to_the_home_folder_not_to_the_repository(machine, repo):
    """The same repository read with another home folder sees none of the first home's sessions."""
    machine.open_config()
    proc = machine.live_process()
    machine.register(repo, proc.pid, ticket="DAEO-home")
    assert support.session_pids(machine.read(repo)) == [proc.pid]

    other_home = machine.base / "other-home"
    other_home.mkdir()
    code, envelope, out, err = machine.gov(repo, env_extra={"HOME": str(other_home)})
    reading = support.reading_of(code, envelope, out, err)
    assert reading.get("sessions") == [], f"another home folder sees this home's registry: {reading}"
    assert os.path.realpath(reading["registry"]).startswith(os.path.realpath(other_home) + os.sep), reading
