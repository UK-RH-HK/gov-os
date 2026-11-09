"""S11: the out-of-memory trip-wire.

Below a second, lower memory floor (in the configuration file), the gate names the largest heavy job and stops it
before the kernel's out-of-memory killer would end a session, and the stop is a finding; nothing else is stopped
[DEC-947, DEC-983, DEC-982].

Interface (README, "The trip-wire"): ``gov resources --trip-wire`` takes one pass: below ``oom_floor_bytes`` it
stops the heavy job (a slot holder, with its command's processes) whose process tree holds the most memory, reports
it under ``stopped`` and appends one JSON line to ``$HOME/.gov-os/machine/findings.jsonl`` naming it; otherwise
``stopped`` is ``null`` and nothing is written.
"""

from __future__ import annotations

import json

import w2_20_support as support
from w2_20_support import GIB


def _jobs(machine, repo):
    machine.open_config(heavy_slots=3, oom_floor_bytes=2 * GIB)
    machine.slot_job(repo, "test", "small-job-A", memory_mib=0)
    machine.slot_job(repo, "test", "large-job-B", memory_mib=160)
    small, large = machine.wait_started("small-job-A"), machine.wait_started("large-job-B")
    session = machine.live_process(memory_mib=256)  # larger than either job, but a session, not a heavy job
    machine.register(repo, session.pid, ticket="DAEO-trip")
    return small, large, session


def test_s11_below_the_trip_floor_the_largest_heavy_job_is_stopped_and_nothing_else(machine, repo):
    small, large, session = _jobs(machine, repo)
    machine.set_readings(available_bytes=2 * GIB - 4096)

    code, envelope, out, err = machine.gov(repo, "--trip-wire")
    result = support.reading_of(code, envelope, out, err)
    stopped = result.get("stopped")
    assert stopped, f"nothing was stopped below the trip floor: {result}"
    assert "large-job-B" in json.dumps(stopped), f"the job named is not the largest heavy job: {stopped}"

    support.wait_for(lambda: not support.alive(large), "the largest heavy job's command to end", 30)
    assert support.alive(small), "the smaller heavy job was stopped too"
    assert support.alive(session.pid), "a session was stopped"

    assert machine.findings.exists(), "the stop is not recorded as a finding"
    lines = [json.loads(line) for line in machine.findings.read_text().splitlines() if line.strip()]
    assert len(lines) == 1 and "large-job-B" in json.dumps(lines[0]), lines
    assert "small-job-A" not in json.dumps(lines[0]), lines
    machine.release("small-job-A")


def test_s11_at_or_above_the_trip_floor_nothing_is_stopped(machine, repo):
    small, large, session = _jobs(machine, repo)
    machine.set_readings(available_bytes=2 * GIB)

    code, envelope, out, err = machine.gov(repo, "--trip-wire")
    result = support.reading_of(code, envelope, out, err)
    assert "stopped" in result and result["stopped"] is None, result
    assert support.alive(small) and support.alive(large) and support.alive(session.pid)
    assert not machine.findings.exists() or not machine.findings.read_text().strip()
    machine.release("small-job-A")
    machine.release("large-job-B")
