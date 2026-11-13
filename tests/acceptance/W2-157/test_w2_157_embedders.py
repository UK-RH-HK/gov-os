"""S3: an embedder not wholly on the GPU trips the backstop, by its server's ``/api/ps`` or by its log.

The embedders are the gate file's ``gpu_backstop_embedders`` (a port and a log each): stand-in HTTP servers on free ports
answer ``GET /api/ps`` from a planted body, and planted log files stand for the servers' logs (L4). The watch is held at
its second reading (a gated stand-in ``nvidia-smi`` call) wherever a case needs "since the watch started": the first
poll is complete (so the start offsets were taken), the case changes the world, then releases the second reading.
"""

from __future__ import annotations

import pytest

import w2_157_support as support
from w2_157_support import TOTAL_MIB, model

PARTIAL_LINE = "llm_load_tensors: offloaded 30/33 layers to GPU"
FULL_LINE = "llm_load_tensors: offloaded 33/33 layers to GPU"


def held_at_second_reading(machine, job):
    """Start the watch with its second GPU reading held; return the watch once the first poll is complete."""
    machine.plant_smi([(1000, TOTAL_MIB), (1000, TOTAL_MIB)], gated=[1])
    watch = machine.start_watch([job.pgid])
    machine.wait_calls(2, watch=watch)
    assert job.running(), f"the job was paused by the first poll (state {job.state()})\n{watch.describe()}"
    assert machine.trips() == [], machine.log_lines()
    return watch


def test_s3_a_model_with_size_vram_below_size_trips_once_naming_port_model_and_ratio(machine):
    """The server answers a model wholly on the GPU at the first poll, then ``size_vram`` 500 of ``size`` 1000: the job
    is stopped, one TRIP line, one inbox item, and the reason names the port, the model and ``500/1000``."""
    embedder = machine.add_embedder(models=[model("mxbai-embed-large:latest", size=1000, size_vram=1000)], log_text="")
    job = machine.start_job()
    watch = held_at_second_reading(machine, job)
    assert ("GET", "/api/ps") in embedder.requests, "the first poll did not ask the server's /api/ps"
    embedder.answer([model("mxbai-embed-large:latest", size=1000, size_vram=500)])
    machine.release(1)
    support.wait_for(job.stopped, "the job to be stopped", watch=watch)
    outcome = machine.finish(watch)
    result = outcome.result()
    assert result["tripped"] is True and result["paused"] == [job.pgid], outcome.text()
    for part in (str(embedder.port), "mxbai-embed-large:latest", "500/1000"):
        assert part in result["reason"], f"the reason does not name {part!r}: {result['reason']!r}"
    assert len(machine.trips()) == 1 and len(machine.inbox_items()) == 1, machine.log_lines()
    assert job.signals() == []


def test_s3_a_partial_offload_line_written_since_the_start_trips_once_naming_the_log(machine):
    """A line ``offloaded 30/33 layers to GPU`` appended to the server's log after the watch started: the job is
    stopped, one TRIP line and one inbox item, and the reason names the log's path and the matched text."""
    embedder = machine.add_embedder(log_text="started\n")
    job = machine.start_job()
    watch = held_at_second_reading(machine, job)
    embedder.append_log(PARTIAL_LINE + "\n")
    machine.release(1)
    support.wait_for(job.stopped, "the job to be stopped", watch=watch)
    outcome = machine.finish(watch)
    result = outcome.result()
    assert result["tripped"] is True and result["paused"] == [job.pgid], outcome.text()
    assert str(embedder.log) in result["reason"], f"the reason does not name the log: {result['reason']!r}"
    assert "offloaded 30/33 layers to GPU" in result["reason"], f"nor the matched text: {result['reason']!r}"
    assert len(machine.trips()) == 1 and len(machine.inbox_items()) == 1, machine.log_lines()


def test_s3_a_line_with_n_equal_to_m_does_not_trip(machine):
    """``offloaded 33/33 layers to GPU`` appended after the start, and read by several polls: no trip."""
    embedder = machine.add_embedder(log_text="started\n")
    job = machine.start_job()
    watch = held_at_second_reading(machine, job)
    embedder.append_log(FULL_LINE + "\n")
    machine.release(1)
    result = machine.watch_quietly(watch, job, polls=6).result()
    assert result["tripped"] is False and machine.inbox_items() == [], result


def test_s3_only_what_was_appended_since_the_start_counts(machine):
    """The log holds a partial-offload line (30/33) when the watch starts: it does not trip. A line appended later
    (31/33) does, and the reason names the new line, not the old one."""
    embedder = machine.add_embedder(log_text=PARTIAL_LINE + "\n")
    job = machine.start_job()
    watch = held_at_second_reading(machine, job)
    embedder.append_log("llm_load_tensors: offloaded 31/33 layers to GPU\n")
    machine.release(1)
    support.wait_for(job.stopped, "the job to be stopped by the new line", watch=watch)
    result = machine.finish(watch).result()
    assert result["tripped"] is True and "31/33" in result["reason"] and "30/33" not in result["reason"], result


def test_s3_a_log_missing_at_the_start_counts_from_its_first_byte(machine):
    """The server's log does not exist when the watch starts (offset 0): once it appears with a partial-offload line,
    that line trips."""
    embedder = machine.add_embedder(log_text=None)
    assert not embedder.log.exists()
    job = machine.start_job()
    watch = held_at_second_reading(machine, job)
    embedder.plant_log(PARTIAL_LINE + "\n")
    machine.release(1)
    support.wait_for(job.stopped, "the job to be stopped", watch=watch)
    result = machine.finish(watch).result()
    assert result["tripped"] is True and str(embedder.log) in result["reason"], result


def test_s3_every_configured_embedder_is_watched_and_the_partial_one_is_named(machine):
    """Two configured servers (two free ports, not 11434 or 11435): the second goes partial; the reason names its port
    and not the first's, and both servers were asked ``GET /api/ps``."""
    first = machine.add_embedder(models=[model("first-model", size=1000)], log_text="")
    second = machine.add_embedder(models=[model("second-model", size=1000)], log_text="")
    job = machine.start_job()
    watch = held_at_second_reading(machine, job)
    assert ("GET", "/api/ps") in first.requests and ("GET", "/api/ps") in second.requests
    second.answer([model("second-model", size=1000, size_vram=400)])
    machine.release(1)
    support.wait_for(job.stopped, "the job to be stopped", watch=watch)
    result = machine.finish(watch).result()
    assert result["tripped"] is True, result
    assert str(second.port) in result["reason"] and "second-model" in result["reason"] and "400/1000" in result["reason"]
    assert str(first.port) not in result["reason"] and "first-model" not in result["reason"], result["reason"]


NO_ANSWER_CASES = [
    pytest.param(None, id="nothing-listening"),
    pytest.param("this is not json", id="not-json"),
    pytest.param("{}", id="no-models-key"),
    pytest.param('{"models": null}', id="models-null"),
    pytest.param('{"models": [{"name": "m"}]}', id="a-model-without-sizes"),
    pytest.param('{"models": [{"name": "m", "size": "big", "size_vram": "none"}]}', id="sizes-not-numbers"),
]


@pytest.mark.parametrize("body", NO_ANSWER_CASES)
def test_s3_no_answer_or_a_malformed_one_is_no_trip(machine, body):
    """A server that does not answer, or answers something that is not ``{"models": [{"name", "size", "size_vram"}]}``,
    never trips the backstop: the watch goes on until its job ends."""
    embedder = machine.add_embedder(listen=body is not None, log_text="")
    if body is not None:
        embedder.answer_raw(body)
    machine.plant_smi([(1000, TOTAL_MIB)])
    job = machine.start_job()
    watch = machine.start_watch([job.pgid])
    result = machine.watch_quietly(watch, job, polls=5).result()
    assert result["tripped"] is False and machine.trips() == [], result


def test_s3_an_embedder_trips_it_even_when_the_gpu_cannot_be_read(machine):
    """``nvidia-smi`` fails (exit 9) at every call: the readings are logged as ``no GPU reading``, the watch goes on, and
    a partial model still trips it, with ``reading none`` in the TRIP line and a null reading in the result (L3, L6)."""
    embedder = machine.add_embedder(models=[model("m", size=1000, size_vram=1000)], log_text="")
    machine.plant_smi([{"exit": 9}])
    job = machine.start_job()
    watch = machine.start_watch([job.pgid])
    machine.wait_calls(3, watch=watch)
    assert job.running(), f"an unreadable GPU paused the job (state {job.state()})"
    embedder.answer([model("m", size=1000, size_vram=1)])
    support.wait_for(job.stopped, "the job to be stopped", watch=watch)
    result = machine.finish(watch).result()
    assert result["tripped"] is True and result["reading"] is None, result
    lines = machine.log_lines()
    assert any(support.NO_READING_RE.match(line) for line in lines), f"no 'no GPU reading' line: {lines}"
    assert any(support.TRIP_NO_READING_RE.match(line) for line in lines), f"no TRIP line with 'reading none': {lines}"


@pytest.mark.parametrize("first,second", [("limit", "api"), ("spill", "api"), ("api", "log")])
def test_s3_the_checks_run_in_the_stated_order_and_the_first_reason_trips(machine, first, second):
    """L5's order is the limit, the spill, each embedder's ``/api/ps``, each embedder's log; when two conditions hold at
    once the first one found is the reason (the later one is not named)."""
    gpu = {"limit": (15900, TOTAL_MIB), "spill": (8150, 8192)}.get(first, (1000, TOTAL_MIB))
    embedder = machine.add_embedder(models=[model("order-model", size=1000, size_vram=300)], log_text="")
    machine.plant_smi([gpu], gated=[0])
    job = machine.start_job()
    watch = machine.start_watch([job.pgid])
    machine.wait_calls(1, watch=watch)
    if second == "log":
        embedder.append_log(PARTIAL_LINE + "\n")
    machine.release(0)
    support.wait_for(job.stopped, "the job to be stopped", watch=watch)
    result = machine.finish(watch).result()
    assert result["tripped"] is True, result
    reason = result["reason"]
    if first in ("limit", "spill"):
        assert str(embedder.port) not in reason and "order-model" not in reason, (
            f"the {first} was found first, but the reason names the embedder: {reason!r}")
    else:
        assert str(embedder.log) not in reason and "offloaded" not in reason, (
            f"the /api/ps answer was found first, but the reason names the log: {reason!r}")
        assert str(embedder.port) in reason and "order-model" in reason, reason
