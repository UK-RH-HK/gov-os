"""KPI success 7 (corrected under DEC-1033): the fallback goes through the GPU slot rule, never the CPU.

"When the service is down the search falls back to a private reranker through the GPU slot rule (it waits for one
of the slots, else the search goes on unranked, named: `merge.reranked` false with its reason); it never runs a
reranker on the CPU (DEC-1033: on the CPU a query takes over 100 s)." The stopgap's retirement is an owner ACT the
lead prepares, written in the research record: ``test_w2_112_retirement_act.py``.

The rule as ACT-RERANK-WAIT-1 states it: a reranker holds one of ``GOV_RERANK_GPU_SLOTS`` lock files
(``gov-os-rerank-gpu-<i>.lock``, an exclusive ``flock``) in ``GOV_RERANK_GPU_LOCK_DIR`` for its life; without one it
waits up to ``GOV_RERANK_GPU_WAIT_S``, then the search goes on unranked; never the CPU unless
``GOV_RERANK_ALLOW_CPU=1`` (tests and measurements only; never set here). The KPI requires the rule after the owner
removes the stopgap module from the environment, so the box's reranker environment holds no such module: the rule
here can only be the product's. Each box has its own lock folder (never ``/tmp``); the case holds slots itself.

DEC-1036 T6 (b): "the service holds one of the two GPU slots (it waits for a slot like any reranker, or fails
named), so at most one private reranker beside it". The last three cases hold that.

In the first cases the service cannot start (a folder stands where its socket goes), so every answer is a
fallback's. "Named with its reason" is read in the bundle: ``test_w2_112_bundle.py``.
"""

from __future__ import annotations

import time

import pytest

import w2_112_support as support
from w2_112_support import candidates, check_scored, check_unranked, query_of, raised


def _scorer_loads(box, query):
    scorers = box.scorers_of(query)
    return [record for record in box.loads() if record["pid"] in scorers]


def test_with_a_gpu_slot_free_the_fallback_private_reranker_loads_on_the_gpu_holding_a_slot(box):
    box.block_service()
    query, given = query_of("slot-free"), candidates("slot-free", 5)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised: {raised(report)}"
    assert report["seconds"] <= support.FALLBACK_S, f"the search took {report['seconds']:.1f} s with a slot free"
    check_scored(report["result"], query, given, "the search whose service cannot start")
    loads = _scorer_loads(box, query)
    assert loads, "no private reranker that scored the search loaded the model"
    for record in loads:
        assert record["device"] == "cuda", \
            f"the fallback private reranker loaded its model on {record['device']}, not on the GPU (KPI 7)"
        assert record["slots_held"] and record["slots_held"] >= 1, \
            ("the fallback private reranker loaded its model while no GPU slot was held in "
             f"{support.LOCK_DIR_SETTING}: it did not go through the GPU slot rule")
    assert [record for record in box.loads() if record["device"] == "cpu"] == [], "a model was loaded on the CPU"


def test_with_both_gpu_slots_held_a_fallback_waits_then_goes_on_unranked_with_no_model_on_the_cpu(boxes):
    wait = 2.0
    box = boxes(settings={support.WAIT_SETTING: wait})
    box.block_service()
    box.hold_slots()
    query, given = query_of("slots-held"), candidates("slots-held", 5)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised with both GPU slots held: {raised(report)}"
    check_unranked(report["result"], given, "the search with both GPU slots held")
    assert report["seconds"] >= wait * 0.75, \
        f"the search went on after {report['seconds']:.1f} s: it did not wait {wait:g} s for a GPU slot"
    assert report["seconds"] <= wait + support.FALLBACK_S, \
        f"the search took {report['seconds']:.1f} s with both slots held (wait {wait:g} s)"
    assert box.scorers_of(query) == set(), f"the texts were scored by {box.scorers_of(query)} without a GPU slot"
    on_cpu = [record["pid"] for record in box.loads() if record["device"] == "cpu"]
    assert on_cpu == [], f"a reranker was loaded on the CPU when no GPU slot was free: {on_cpu}"


def test_a_fallback_waits_for_a_gpu_slot_and_takes_the_one_that_frees(boxes):
    box = boxes(settings={support.WAIT_SETTING: 8})
    box.block_service()
    box.hold_slots()
    query, given = query_of("slot-frees"), candidates("slot-frees", 5)
    session = box.start({"query": query, "candidates": given})
    time.sleep(1.5)
    freed = box.release_slots()
    report = session.wait()
    assert raised(report) is None, f"the search raised: {raised(report)}"
    check_scored(report["result"], query, given, "the search that waited for a GPU slot")
    loads = _scorer_loads(box, query)
    assert loads, "no private reranker that scored the search loaded the model"
    for record in loads:
        assert record["time"] >= freed - 0.05, \
            (f"the private reranker loaded its model {freed - record['time']:.2f} s before a GPU slot freed: it did "
             "not wait for a slot")
        assert record["device"] == "cuda", f"the private reranker loaded its model on {record['device']}, not the GPU"


@pytest.mark.parametrize("why", ["no-gpu", "gpu-hidden"])
def test_a_fallback_never_runs_a_reranker_on_the_cpu(boxes, why):
    box = boxes(gpu=support.NO_GPU if why == "no-gpu" else support.ROOM)
    box.block_service()
    env = box.env(CUDA_VISIBLE_DEVICES="-1") if why == "gpu-hidden" else None
    query, given = query_of(f"cpu-{why}"), candidates(f"cpu-{why}", 5)
    report = box.search(query, given, env=env)
    assert raised(report) is None, f"the search raised ({why}): {raised(report)}"
    assert report["seconds"] <= support.SLOT_WAIT_S + support.FALLBACK_S, \
        f"the search took {report['seconds']:.1f} s ({why})"
    on_cpu = [record["pid"] for record in box.loads() if record["device"] == "cpu"]
    assert on_cpu == [], f"the fallback ran a reranker on the CPU ({why}): KPI 7 forbids it"
    check_unranked(report["result"], given, f"the search whose fallback has no GPU ({why})")


# ---- DEC-1036 T6 (b): the service holds one of the two GPU slots


def test_the_service_holds_one_of_the_two_gpu_slots(box):
    service = box.warm()
    loaded = [record for record in box.loads() if record["pid"] == service][0]
    assert loaded["slots_held"] and loaded["slots_held"] >= 1, \
        f"the service loaded its model while no GPU slot was held in {support.LOCK_DIR_SETTING} (DEC-1036 T6 (b))"
    held = box.slots_held()
    assert held == 1, f"with the service up and nothing else running, {held} GPU slots are held, not the service's one"


def test_with_the_service_up_and_the_other_slot_held_a_fallback_waits_then_goes_on_unranked(boxes):
    wait = 2.0
    box = boxes(settings={support.WAIT_SETTING: wait})
    service = box.warm()
    taken = box.hold_free_slots()
    assert len(taken) == 1, \
        f"with the service up, the test could take {len(taken)} GPU slots ({taken}): the service is to hold one of two"
    box.for_pid(service, predict_error=True)  # the service now answers with an error: the search falls back
    query, given = query_of("beside"), candidates("beside", 5)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised: {raised(report)}"
    check_unranked(report["result"], given, "the search whose service failed while both slots were held")
    assert report["seconds"] >= wait * 0.75, \
        f"the fallback went on after {report['seconds']:.1f} s: it did not wait {wait:g} s for a GPU slot"
    assert report["seconds"] <= wait + support.FALLBACK_S, f"the search took {report['seconds']:.1f} s"
    beside = [(record["pid"], record["device"]) for record in box.loads() if record["pid"] != service]
    assert beside == [], \
        (f"a private reranker loaded the model beside the service with no GPU slot free ({beside}): at most one "
         "private reranker beside it, on a slot, never the CPU")


def test_with_both_slots_held_before_any_service_the_search_goes_on_unranked_with_no_model_loaded(boxes):
    wait = 2.0
    box = boxes(settings={support.WAIT_SETTING: wait})
    box.hold_slots()
    query, given = query_of("no-slot"), candidates("no-slot", 5)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised with both GPU slots held: {raised(report)}"
    check_unranked(report["result"], given, "the search with both GPU slots held before any service")
    # The service waits for a slot like any reranker, then the search's fallback does too: two waits at most.
    assert report["seconds"] <= 2 * wait + support.FALLBACK_S, f"the search took {report['seconds']:.1f} s"
    loads = [(record["pid"], record["device"]) for record in box.loads()]
    assert loads == [], \
        (f"a model was loaded although both GPU slots were held ({loads}): the service cannot start on the GPU "
         "without a slot, and no reranker runs on the CPU")
    assert box.live_loads() == [], "a service holds the model without a GPU slot"
