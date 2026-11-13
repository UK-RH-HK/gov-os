"""S3 (and failure line 3): the shared service holds every reranker GPU slot for its life (DEC-1043 (2),
DEC-1046 (1), DEC-1048 (5), DEC-1036).

The service first waits for one slot as today (``take_slot``, ``GOV_RERANK_GPU_WAIT_S``, never the CPU), then takes
every other slot that is free and, for one held by another process, takes it within 2 s of its release (3 s is
held here, as the ticket's Verify says); all go with the process when it ends (idle, SIGTERM or a crash). So a
private reranker of any tree that keeps the slot rule, started beside a running service, waits and ends named (exit
75) and loads nothing.

The service is the code under test's own ``rerank_service.py``, started by a search from the planted reranker
environment (W2-112's stand-in encoder: no model, no GPU). The slots are lock files in the box's own folder
(``GOV_RERANK_GPU_LOCK_DIR``, never ``/tmp``), and their holders are read by pid from ``/proc/locks``. The private
reranker of an older tree is ``standin/w145_slot_rule_worker.py``, which keeps the rule as ACT-RERANK-WAIT-1 states
it and loads the stand-in model on a slot. The share check, the memory release, the cap and the idle end are held
unchanged by W2-112's own cases (its README names them).

Every case here needs the service to listen on its Unix socket: run outside the launch sandbox.
"""

from __future__ import annotations

import os
import signal
import subprocess
import time

import pytest

import w2_145_support as support
from w2_145_support import alive, base, candidates, check_scored, query_of, raised

STAND_IN_WAIT_S = 2.0


def _warm(box, tag: str) -> int:
    """One search that starts the service and is answered by it; the service's pid."""
    query, given = query_of(tag), candidates(tag, 4)
    report = box.search(query, given)
    assert raised(report) is None, f"the first search raised: {raised(report)}"
    check_scored(report["result"], query, given, "the first search")
    outcome = report.get("outcome") or {}
    assert outcome.get("by") == "service", \
        f"the first search was not answered by the shared service: last_outcome() {outcome}{base.note()}"
    holders = [record["pid"] for record in box.live_loads()]
    assert len(holders) == 1, \
        f"after the first search, {len(holders)} live processes hold the model ({holders}): one service{base.note()}"
    return holders[0]


def _all_held_by(box, pid: int) -> bool:
    return all(pids == {pid} for pids in box.holders().values())


def test_s3_the_running_service_holds_every_gpu_slot(boxes):
    box = boxes(slots=3)
    service = _warm(box, "s3-every")
    held = box.wait_for(lambda: _all_held_by(box, service), support.SERVICE_SLOTS_S)
    assert held, f"with nothing else holding a slot, the service {service} does not hold every one of the 3 slots " \
                 f"within {support.SERVICE_SLOTS_S:g} s: holders {box.holders()}"
    query, given = query_of("s3-every-again"), candidates("s3-every-again", 4)
    report = box.search(query, given)
    check_scored(report["result"], query, given, "a search while the service holds every slot")
    assert box.scorers_of(query) == {service}, "the search was not answered by the service holding the slots"


def test_s3_a_slot_another_process_held_is_held_by_the_service_within_3_s_of_its_release(boxes):
    box = boxes()
    other = box.hold_in_child(1)
    service = _warm(box, "s3-freed")
    box.wait_for(lambda: box.holders()[0] == {service}, support.SERVICE_SLOTS_S)
    holders = box.holders()
    assert holders[1] == {other.pid}, f"premise: slot 1 is to be held by the other process {other.pid}: {holders}"
    assert holders[0] == {service}, f"the service {service} does not hold the slot that was free: {holders}"
    time.sleep(1.0)
    released = other.release()
    taken = box.wait_for(lambda: box.holders()[1] == {service}, support.SERVICE_SLOTS_S + 3.0, step=0.02)
    after = time.monotonic() - released
    assert taken and after <= support.SERVICE_SLOTS_S, \
        (f"slot 1, released by the other process, is not held by the service {service} within "
         f"{support.SERVICE_SLOTS_S:g} s (holders {box.holders()} {after:.1f} s after the release)")


def test_s3_a_private_reranker_under_the_slot_rule_beside_the_running_service_ends_75_within_its_wait(boxes):
    box = boxes()
    service = _warm(box, "s3-beside")
    box.wait_for(lambda: _all_held_by(box, service), support.SERVICE_SLOTS_S)
    env = box.env(**{support.WAIT_SETTING: f"{STAND_IN_WAIT_S:g}"})
    began = time.monotonic()
    done = subprocess.run([str(box.venv / "bin" / "python"), "-I", str(support.SLOT_RULE_WORKER)], env=env,
                          capture_output=True, text=True, timeout=60, cwd=str(box.work))
    seconds = time.monotonic() - began
    beside = [(record["pid"], record["device"]) for record in box.loads() if record["pid"] != service]
    assert beside == [] and done.returncode == 75, \
        (f"a private reranker under the slot rule, started beside the running service, loaded the model "
         f"({beside}, exit {done.returncode}, stdout {done.stdout.strip()!r}): the service is to hold every slot "
         f"(holders {box.holders()})")
    assert seconds <= STAND_IN_WAIT_S + support.MARGIN_S + 1.0, \
        f"the private reranker took {seconds:.1f} s to end with its {STAND_IN_WAIT_S:g} s wait"


@pytest.mark.parametrize("how", ["sigterm", "crash", "idle"])
def test_s3_after_the_service_ends_every_slot_is_free(boxes, how):
    idle = 6.0
    box = boxes(settings={support.IDLE_SETTING: f"{idle:g}"} if how == "idle" else None)
    service = _warm(box, f"s3-end-{how}")
    held = box.wait_for(lambda: _all_held_by(box, service), support.SERVICE_SLOTS_S)
    assert held, f"premise: the running service {service} is to hold every slot: holders {box.holders()}"
    if how == "sigterm":
        os.kill(service, signal.SIGTERM)
    elif how == "crash":
        os.kill(service, signal.SIGKILL)
    ended = box.wait_for(lambda: not alive(service), idle + 15.0 if how == "idle" else 10.0)
    assert ended, f"the service {service} did not end ({how})"
    free = box.wait_for(lambda: box.free_slots() == list(range(box.slots)), 2.0)
    assert free, f"after the service ended ({how}) slots are still held: {box.holders()}"


def test_s3_the_service_first_waits_for_a_slot_on_the_gpu_then_holds_every_slot(boxes):
    box = boxes(settings={support.WAIT_SETTING: "8"})
    box.hold_slots(*range(box.slots))
    query, given = query_of("s3-waits"), candidates("s3-waits", 4)
    session = box.start({"query": query, "candidates": given})
    time.sleep(1.5)
    box.release_slots()
    report = session.wait()
    assert raised(report) is None, f"the search raised: {raised(report)}"
    check_scored(report["result"], query, given, "the search whose service waited for a slot")
    assert (report.get("outcome") or {}).get("by") == "service", f"not the service's answer: {report.get('outcome')}"
    loads = box.loads()
    assert len(loads) == 1 and loads[0]["device"] == "cuda" and (loads[0].get("slots_held") or 0) >= 1, \
        f"the service did not load its one model on the GPU holding a slot: {loads}"
    service = loads[0]["pid"]
    held = box.wait_for(lambda: _all_held_by(box, service), support.SERVICE_SLOTS_S)
    assert held, f"once started, the service {service} does not hold every slot: holders {box.holders()}"
