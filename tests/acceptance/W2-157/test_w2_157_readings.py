"""S2 (a spill into shared GPU memory) and F2 (each reading gives its stated outcome: the limit, the spill, an embedder
partly on the CPU, a partial offload).

Boundaries from L3 (used > limit trips: 15,872 does not at a limit of 15,872, 15,873 does; used >= total - 64 trips:
total - 63 and total - 64 trip, total - 65 does not) and L4 (``size_vram`` below ``size``; ``offloaded N/M layers to
GPU`` with N below M, appended after the watch started).
"""

from __future__ import annotations

import pytest

import w2_157_support as support
from w2_157_support import TOTAL_MIB

CARD = 8192  # a card total under the limit, so a reading near it is a spill and not an over-limit reading


def observe(machine, *, gpu=(1000, TOTAL_MIB), api=None, log_line=None, log_before=None, polls=5):
    """Run the watch over one planted condition and return (tripped, result, job). ``api``: ``(size_vram, size)`` of the
    one model a stand-in server answers; ``log_line``: a line appended to an embedder's log after the watch started;
    ``log_before``: a line already in the log at the start. The job is the named one; whether it is stopped must agree
    with ``tripped``."""
    machine.plant_smi([gpu])
    job = machine.start_job()
    embedder = None
    if api is not None or log_line is not None or log_before is not None:
        models = [support.model("planted-embedder", size=api[1], size_vram=api[0])] if api is not None else []
        embedder = machine.add_embedder(models=models, log_text=(log_before + "\n") if log_before else "")
    watch = machine.start_watch([job.pgid])
    if log_line is not None:
        machine.wait_calls(1, watch=watch)         # the watch is running: what is appended now is "since the watch started"
        embedder.append_log(log_line + "\n")
    reached = machine.wait_calls(polls, watch=watch, exit_ok=True)
    if reached:                                    # nothing tripped within the polls: end the job and the watch
        assert job.running(), f"the job was paused (state {job.state()})\n{watch.describe()}"
        job.end()
    outcome = machine.finish(watch)
    result = outcome.result()
    assert result["tripped"] is (not reached), f"the result and the polls disagree\n{outcome.text()}"
    if result["tripped"]:
        assert job.stopped(), f"tripped, but the job is not stopped (state {job.state()})"
    else:
        assert job.signals() == [] and machine.trips() == [], machine.log_lines()
    return result["tripped"], result, job


# --- S2 ---------------------------------------------------------------------------------------------------------------

def test_s2_a_reading_at_total_minus_63_trips_and_names_the_spill(machine):
    """Used = total - 63 MiB (8,129 of 8,192; far under the 15,872 limit): the job is stopped, the watch ends, and the
    reason names a spill (into shared GPU memory), not the limit."""
    machine.plant_smi([(CARD - 63, CARD)])
    job = machine.start_job()
    outcome = machine.run([job.pgid])
    result = outcome.result()
    assert result["tripped"] is True and result["reading"] == {"used_mib": CARD - 63, "total_mib": CARD}, outcome.text()
    assert "spill" in result["reason"].lower(), f"the reason does not name a spill: {result['reason']!r}"
    assert job.stopped(), f"the job is not stopped (state {job.state()})"
    trips = machine.trips()
    assert len(trips) == 1 and trips[0].group(2, 3) == (str(CARD - 63), str(CARD)), machine.log_lines()


def test_s2_a_reading_at_total_minus_65_does_not_trip(machine):
    """Used = total - 65 MiB (8,127 of 8,192): the watch goes on reading and the job is never paused, until it ends."""
    machine.plant_smi([(CARD - 65, CARD)])
    job = machine.start_job()
    watch = machine.start_watch([job.pgid])
    result = machine.watch_quietly(watch, job, polls=5).result()
    assert result["tripped"] is False and result["paused"] == [] and result["inbox_item"] is None, result
    assert machine.inbox_items() == [] and machine.trips() == []


# --- F2: each reading gives the stated outcome ---------------------------------------------------------------------------

GPU_CASES = [
    pytest.param((15800, TOTAL_MIB), False, id="used-15800-no-trip"),
    pytest.param((15872, TOTAL_MIB), False, id="used-at-the-limit-15872-no-trip"),
    pytest.param((15873, TOTAL_MIB), True, id="used-15873-trips"),
    pytest.param((15900, TOTAL_MIB), True, id="used-15900-trips"),
    pytest.param((CARD - 65, CARD), False, id="total-minus-65-no-trip"),
    pytest.param((CARD - 64, CARD), True, id="total-minus-64-trips"),
    pytest.param((CARD - 63, CARD), True, id="total-minus-63-trips"),
    pytest.param((0, CARD), False, id="empty-card-no-trip"),
]


@pytest.mark.parametrize("gpu,trips", GPU_CASES)
def test_f2_the_gpu_reading_gives_its_stated_outcome(machine, gpu, trips):
    tripped, result, _ = observe(machine, gpu=gpu)
    assert tripped is trips, f"reading {gpu}: tripped {tripped}, stated {trips}"
    if trips:
        assert result["reading"] == {"used_mib": gpu[0], "total_mib": gpu[1]}, result


API_CASES = [
    pytest.param((700, 700), False, id="size-vram-equals-size-no-trip"),
    pytest.param((699, 700), True, id="size-vram-one-below-size-trips"),
    pytest.param((350, 700), True, id="half-on-the-cpu-trips"),
    pytest.param((0, 700), True, id="wholly-on-the-cpu-trips"),
]


@pytest.mark.parametrize("api,trips", API_CASES)
def test_f2_an_embedders_model_gives_its_stated_outcome(machine, api, trips):
    tripped, result, _ = observe(machine, api=api)
    assert tripped is trips, f"/api/ps size_vram/size {api}: tripped {tripped}, stated {trips}"


LOG_CASES = [
    pytest.param("load_tensors: offloaded 33/33 layers to GPU", False, id="n-equals-m-no-trip"),
    pytest.param("load_tensors: offloaded 30/33 layers to GPU", True, id="n-below-m-trips"),
    pytest.param("load_tensors: offloaded 32/33 layers to GPU", True, id="one-layer-short-trips"),
    pytest.param("load_tensors: offloaded 0/29 layers to GPU", True, id="none-offloaded-trips"),
]


@pytest.mark.parametrize("line,trips", LOG_CASES)
def test_f2_a_log_line_gives_its_stated_outcome(machine, line, trips):
    tripped, result, _ = observe(machine, log_line=line)
    assert tripped is trips, f"log line {line!r}: tripped {tripped}, stated {trips}"


def test_f2_a_partial_offload_already_in_the_log_at_the_start_does_not_trip(machine):
    """Nothing before the start offset ever counts (L4): the same partial-offload line, written before the watch
    started, gives no trip."""
    tripped, _, _ = observe(machine, log_before="load_tensors: offloaded 30/33 layers to GPU")
    assert tripped is False
