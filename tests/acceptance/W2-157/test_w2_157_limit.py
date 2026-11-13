"""S1 (the limit, the pause, the poll period, the configuration's refusals) and F3 (a limit from nowhere but the file).

Reached as its callers do: ``python3 -m gov.cli.main resources --backstop <pgid> ... --root <project> --json`` in a child
process, with a planted HOME whose ``gate.json`` holds the three W2-157 values, a stand-in ``nvidia-smi`` first on PATH
and a stand-in job in its own process group (``w2_157_support``). The interface read is the brief's L1-L9.
"""

from __future__ import annotations

import json
import re

import pytest

import w2_157_support as support
from w2_157_support import TOTAL_MIB, dated


def test_s1_the_job_runs_at_the_first_reading_and_is_stopped_at_the_second(machine):
    """Readings 15,800 then 15,900 MiB (total 24,576, no spill), the limit 15,872 in the planted file: while the second
    reading is held back (the first one was answered) the job is running; once it is answered the job is stopped
    (``T``), the watch ends (exit 0, ``tripped: true``), and the TRIP line holds the reading 15900."""
    machine.plant_smi([(15800, TOTAL_MIB), (15900, TOTAL_MIB)], gated=[1])
    job = machine.start_job()
    watch = machine.start_watch([job.pgid])
    machine.wait_calls(2, watch=watch)          # reading 1 answered and judged; reading 2 asked, held by the stand-in
    assert job.running(), f"the job is not running at the first reading (state {job.state()})\n{watch.describe()}"
    assert machine.trips() == [], f"a trip is logged at 15,800 MiB: {machine.log_lines()}"
    machine.release(1)
    support.wait_for(job.stopped, "the job to be stopped at the second reading", watch=watch)
    outcome = machine.finish(watch)
    result = outcome.result()

    assert result["tripped"] is True, outcome.text()
    assert result["paused"] == [job.pgid] and result["skipped"] == [], outcome.text()
    assert result["reading"] == {"used_mib": 15900, "total_mib": TOTAL_MIB}, outcome.text()
    assert isinstance(result["reason"], str) and result["reason"].strip(), outcome.text()
    assert job.stopped(), f"the job is not stopped (state {job.state()})"
    assert job.signals() == [], f"the job received signals {job.signals()}: it is paused, nothing else"

    start = [m for m in map(support.START_RE.match, machine.log_lines()) if m]
    assert len(start) == 1, f"the log has {len(start)} start lines: {machine.log_lines()}"
    assert start[0].groups()[0] == str(support.LIMIT_MIB) and start[0].group(3) == str(job.pgid), start[0].groups()
    assert start[0].group(4) == "none" and start[0].group(5) == "none", start[0].groups()
    trips = machine.trips()
    assert len(trips) == 1, f"the log has {len(trips)} TRIP lines: {machine.log_lines()}"
    assert trips[0].group(2, 3) == ("15900", str(TOTAL_MIB)) and trips[0].group(4) == str(job.pgid), trips[0].groups()
    assert machine.log_lines().index(start[0].string) < machine.log_lines().index(trips[0].string)
    assert machine.smi_argvs() == [support.SMI_ARGV, support.SMI_ARGV], (
        f"nvidia-smi was asked other than twice with L3's exact arguments: {machine.smi_argvs()}")


def test_s1_the_period_is_the_files_value(machine):
    """``gpu_backstop_every_s`` is read from the file: at 1 s the readings are one period apart (not 0.1 s, not the
    5 s of the script), and every other poll waits as long."""
    machine.set_every(1)
    machine.plant_smi([(1000, TOTAL_MIB)])
    job = machine.start_job()
    watch = machine.start_watch([job.pgid])
    machine.wait_calls(3, watch=watch)
    outcome = machine.watch_quietly(watch, job, polls=3)
    assert outcome.result()["tripped"] is False, outcome.text()
    times = [call["t"] for call in machine.smi_calls()]
    gaps = [b - a for a, b in zip(times, times[1:])]
    assert len(gaps) >= 2 and all(0.8 <= gap <= 3.0 for gap in gaps[:2]), f"the gaps between readings are {gaps}"


# --- a missing or malformed value refuses to start, naming it (S1, L2) ----------------------------------------------

LIMIT_FAULTS = {
    "missing": lambda g: g.pop("gpu_backstop_limit_mib"),
    "a-string": lambda g: g.update(gpu_backstop_limit_mib=dated("15872")),
    "zero": lambda g: g.update(gpu_backstop_limit_mib=dated(0)),
    "negative": lambda g: g.update(gpu_backstop_limit_mib=dated(-5)),
    "a-float": lambda g: g.update(gpu_backstop_limit_mib=dated(15872.5)),
    "a-boolean": lambda g: g.update(gpu_backstop_limit_mib=dated(True)),
    "null": lambda g: g.update(gpu_backstop_limit_mib=dated(None)),
    "a-bare-number": lambda g: g.update(gpu_backstop_limit_mib=15872),
    "no-date": lambda g: g.update(gpu_backstop_limit_mib={"value": 15872, "source": "planted"}),
    "a-bad-date": lambda g: g.update(gpu_backstop_limit_mib=dated(15872, date="15-11-2026")),
    "no-source": lambda g: g.update(gpu_backstop_limit_mib={"value": 15872, "date": support.today()}),
    "an-empty-source": lambda g: g.update(gpu_backstop_limit_mib=dated(15872, source="  ")),
}
EVERY_FAULTS = {
    "missing": lambda g: g.pop("gpu_backstop_every_s"),
    "zero": lambda g: g.update(gpu_backstop_every_s=dated(0)),
    "negative": lambda g: g.update(gpu_backstop_every_s=dated(-1)),
    "a-string": lambda g: g.update(gpu_backstop_every_s=dated("5")),
    "a-boolean": lambda g: g.update(gpu_backstop_every_s=dated(True)),
    "no-date": lambda g: g.update(gpu_backstop_every_s={"value": 5, "source": "planted"}),
    "no-source": lambda g: g.update(gpu_backstop_every_s={"value": 5, "date": support.today()}),
}
GOOD_ENTRY = {"port": 41234, "log": "/tmp/w2-157-planted-serve.log"}
EMBEDDER_FAULTS = {
    "missing": lambda g: g.pop("gpu_backstop_embedders"),
    "not-a-list": lambda g: g.update(gpu_backstop_embedders=dated("11434")),
    "an-object": lambda g: g.update(gpu_backstop_embedders=dated(GOOD_ENTRY)),
    "an-entry-that-is-a-number": lambda g: g.update(gpu_backstop_embedders=dated([11434])),
    "an-entry-without-port": lambda g: g.update(gpu_backstop_embedders=dated([{"log": GOOD_ENTRY["log"]}])),
    "an-entry-without-log": lambda g: g.update(gpu_backstop_embedders=dated([{"port": 41234}])),
    "port-zero": lambda g: g.update(gpu_backstop_embedders=dated([{**GOOD_ENTRY, "port": 0}])),
    "port-too-high": lambda g: g.update(gpu_backstop_embedders=dated([{**GOOD_ENTRY, "port": 65536}])),
    "port-a-string": lambda g: g.update(gpu_backstop_embedders=dated([{**GOOD_ENTRY, "port": "41234"}])),
    "port-a-boolean": lambda g: g.update(gpu_backstop_embedders=dated([{**GOOD_ENTRY, "port": True}])),
    "log-relative": lambda g: g.update(gpu_backstop_embedders=dated([{**GOOD_ENTRY, "log": "serve.log"}])),
    "log-empty": lambda g: g.update(gpu_backstop_embedders=dated([{**GOOD_ENTRY, "log": ""}])),
    "log-not-text": lambda g: g.update(gpu_backstop_embedders=dated([{**GOOD_ENTRY, "log": 5}])),
    "no-date": lambda g: g.update(gpu_backstop_embedders={"value": [], "source": "planted"}),
    "no-source": lambda g: g.update(gpu_backstop_embedders={"value": [], "date": support.today()}),
}


def _refused_naming(machine, names: list[str], env_extra: dict | None = None):
    """The command refuses to start: exit 1, ``RESOURCE_CONFIG_INVALID`` naming every key in ``names`` (in the message
    and in ``details.faults``), a named live job untouched and nothing written, asked or signalled."""
    machine.plant_smi([(15900, TOTAL_MIB)])          # a reading that would trip, were anything to start
    job = machine.start_job()
    outcome = machine.run([job.pgid], env_extra=env_extra)
    error = outcome.refusal(1)
    assert error.get("code") == "RESOURCE_CONFIG_INVALID", f"the error is {error.get('code')}\n{outcome.text()}"
    details = error.get("details")
    faults = details.get("faults") if isinstance(details, dict) else None
    assert isinstance(faults, list) and faults, f"the error's details.faults is {faults!r}\n{outcome.text()}"
    for name in names:
        assert name in error.get("message", ""), f"the message does not name {name}\n{outcome.text()}"
        assert name in json.dumps(faults), f"details.faults does not name {name}\n{outcome.text()}"
    machine.nothing_started("a refused start")
    support.assert_untouched(job)


@pytest.mark.parametrize("fault", sorted(LIMIT_FAULTS))
def test_s1_a_missing_or_malformed_limit_refuses_to_start_naming_it(machine, fault):
    LIMIT_FAULTS[fault](machine.gate)
    _refused_naming(machine, ["gpu_backstop_limit_mib"])


@pytest.mark.parametrize("fault", sorted(EVERY_FAULTS))
def test_s1_a_missing_or_malformed_period_refuses_to_start_naming_it(machine, fault):
    EVERY_FAULTS[fault](machine.gate)
    _refused_naming(machine, ["gpu_backstop_every_s"])


@pytest.mark.parametrize("fault", sorted(EMBEDDER_FAULTS))
def test_s1_a_missing_or_malformed_embedders_value_refuses_to_start_naming_it(machine, fault):
    EMBEDDER_FAULTS[fault](machine.gate)
    _refused_naming(machine, ["gpu_backstop_embedders"])


def test_s1_every_faulty_key_is_named(machine):
    """Two keys faulty at once: both are named (the message and ``details.faults`` name each faulty key)."""
    del machine.gate["gpu_backstop_limit_mib"]
    machine.gate["gpu_backstop_every_s"] = dated(0)
    machine.gate["gpu_backstop_embedders"] = dated("none")
    _refused_naming(machine, list(support.KEYS))


def test_s1_no_gate_file_refuses_to_start_naming_it(machine):
    machine.gate_missing = True
    _refused_naming(machine, ["gate.json"])


@pytest.mark.parametrize("text", ["this is not json", '["a", "list"]', ""], ids=["not-json", "not-an-object", "empty"])
def test_s1_a_gate_file_that_is_not_a_json_object_refuses_to_start_naming_it(machine, text):
    machine.gate_text = text
    _refused_naming(machine, ["gate.json"])


# --- F3: a limit from anywhere but the file ---------------------------------------------------------------------------

THIRD_VALUE = 20000
ENV_NAMES = ("LIMIT", "GPU_BACKSTOP_LIMIT_MIB", "GOV_GPU_BACKSTOP_LIMIT_MIB")


def test_f3_the_trip_happens_at_the_files_value_only(machine):
    """The file's limit is 12,000 (not the built-in 15,872) while ``LIMIT``, ``GPU_BACKSTOP_LIMIT_MIB`` and
    ``GOV_GPU_BACKSTOP_LIMIT_MIB`` hold 20,000: readings 11,990 then 12,010 trip at the second, and the log's start
    line states the file's limit."""
    machine.set_limit(12000)
    machine.plant_smi([(11990, TOTAL_MIB), (12010, TOTAL_MIB)], gated=[1])
    job = machine.start_job()
    watch = machine.start_watch([job.pgid], env_extra={name: str(THIRD_VALUE) for name in ENV_NAMES})
    machine.wait_calls(2, watch=watch)
    assert job.running(), f"the job was paused at 11,990 MiB (state {job.state()})"
    machine.release(1)
    support.wait_for(job.stopped, "the job to be stopped at 12,010 MiB", watch=watch)
    result = machine.finish(watch).result()
    assert result["tripped"] is True and result["reading"] == {"used_mib": 12010, "total_mib": TOTAL_MIB}, result
    start = [m for m in map(support.START_RE.match, machine.log_lines()) if m]
    assert start and start[0].group(1) == "12000", f"the start line does not state the file's limit: {start}"
    assert len(machine.smi_calls()) == 2


def test_f3_a_reading_between_the_files_limit_and_the_built_in_one_trips(machine):
    """12,000 in the file, 13,000 MiB read: above the file's limit and below the built-in 15,872 and the environment's
    20,000: it trips, so the limit in force is the file's."""
    machine.set_limit(12000)
    machine.plant_smi([(13000, TOTAL_MIB)])
    job = machine.start_job()
    outcome = machine.run([job.pgid], env_extra={name: str(THIRD_VALUE) for name in ENV_NAMES})
    result = outcome.result()
    assert result["tripped"] is True and result["reading"]["used_mib"] == 13000, outcome.text()
    assert job.stopped()


def test_f3_a_reading_between_the_built_in_limit_and_the_files_does_not_trip(machine):
    """18,000 in the file, 16,000 MiB read: above the built-in 15,872 (a limit taken from the code would trip) and below
    the file's: no trip."""
    machine.set_limit(18000)
    machine.plant_smi([(16000, TOTAL_MIB)])
    job = machine.start_job()
    watch = machine.start_watch([job.pgid], env_extra={name: "1" for name in ENV_NAMES})
    result = machine.watch_quietly(watch, job).result()
    assert result["tripped"] is False and result["paused"] == [], result


@pytest.mark.parametrize("name", ENV_NAMES)
def test_f3_an_environment_variable_is_never_a_fallback_for_a_missing_limit(machine, name):
    """The file lacks the limit and the environment holds a usable one: the start is still refused, naming the key."""
    del machine.gate["gpu_backstop_limit_mib"]
    _refused_naming(machine, ["gpu_backstop_limit_mib"], env_extra={name: str(THIRD_VALUE)})


def test_f3_the_period_is_not_taken_from_the_environment(machine):
    """The file's period is 0.1 s; ``EVERY``, ``GPU_BACKSTOP_EVERY_S`` and ``GOV_GPU_BACKSTOP_EVERY_S`` hold 30: six
    readings arrive within the wait's bound (at 30 s they could not)."""
    machine.plant_smi([(1000, TOTAL_MIB)])
    job = machine.start_job()
    env = {name: "30" for name in ("EVERY", "GPU_BACKSTOP_EVERY_S", "GOV_GPU_BACKSTOP_EVERY_S")}
    watch = machine.start_watch([job.pgid], env_extra=env)
    result = machine.watch_quietly(watch, job, polls=6).result()
    assert result["tripped"] is False, result


@pytest.mark.parametrize("option", [["--gpu-backstop-limit-mib", "20000"], ["--gpu-backstop-every-s", "1"],
                                    ["--limit", "20000"]])
def test_f3_no_option_sets_the_limit_or_the_period(machine, option):
    """The limit and the period have no command-line form: argparse's unrecognised-argument error (exit 2), the option
    named, nothing read, written or signalled (L1)."""
    machine.plant_smi([(15900, TOTAL_MIB)])
    job = machine.start_job()
    outcome = machine.run([job.pgid], *option)
    assert outcome.code == 2, f"expected exit 2\n{outcome.text()}"
    assert option[0] in outcome.err, f"the option is not named on standard error\n{outcome.text()}"
    assert "unrecognized arguments:" in outcome.err, f"not argparse's unrecognised-argument error\n{outcome.text()}"
    assert "--backstop" not in outcome.err.split("unrecognized arguments:")[-1], (
        f"--backstop itself is unknown, so the refusal does not come from the option\n{outcome.text()}")
    machine.nothing_started("an unrecognised option")
    support.assert_untouched(job)
