"""KPI success 7 (corrected under DEC-1033), as revised by W2-145 (DEC-1048 (5)): no private reranker takes a GPU
slot in the service's place, nothing runs on the CPU, and the service holds every slot.

KPI 7 said: "When the service is down the search falls back to a private reranker through the GPU slot rule (it
waits for one of the slots, else the search goes on unranked, named: `merge.reranked` false with its reason); it
never runs a reranker on the CPU (DEC-1033)". Under W2-145 (DEC-1048 (5), DEC-1046 (1)) the product starts no private
reranker at all: a search the service cannot answer goes on unranked, named, at once, without waiting for a GPU slot
(W2-145 S4: the 20 s slot wait is gone from the search's path), and the service, once it runs, holds every slot for
its life (W2-145 S3, the CTO's interim watcher's job moved into the product). The stopgap's place is
``test_w2_112_retirement_act.py`` (DEC-1048: it stays).

The rule as ACT-RERANK-WAIT-1 states it still binds the service: it holds lock files ``gov-os-rerank-gpu-<i>.lock``
(an exclusive ``flock``) in ``GOV_RERANK_GPU_LOCK_DIR``; it waits up to ``GOV_RERANK_GPU_WAIT_S`` for its first one;
never the CPU (``GOV_RERANK_ALLOW_CPU=1`` opens no CPU path, W2-145 S2). The box's reranker environment holds no
stopgap module, so the rule here can only be the product's. Each box has its own lock folder (never ``/tmp``).

Rewrite-Reason: DEC-1048 (5) (W2-145's test designer, DAEO-2tfd): each case below that asserted a private reranker on
a slot, or a search's wait for one, now asserts no private and no wait; the service's one slot is now every slot.
"Named with its reason" is read in the bundle: ``test_w2_112_bundle.py``.
"""

from __future__ import annotations

import time

import pytest

import w2_112_support as support
from w2_112_support import candidates, check_named_unavailable, check_unranked, query_of, raised

NO_WAIT_S = support.CONNECT_S + 1.0  # W2-145 S4: within CONNECT_S + 1 s when the start or the socket is refused


def _all_slots_held(box) -> bool:
    return box.slots_held() == support.SLOTS


def test_with_a_gpu_slot_free_and_the_service_unable_to_start_no_private_reranker_loads(box):
    box.block_service()
    query, given = query_of("slot-free"), candidates("slot-free", 5)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised: {raised(report)}"
    check_unranked(report["result"], given, "the search whose service cannot start, a GPU slot free")
    check_named_unavailable(report, "the search whose service cannot start, a GPU slot free")
    assert box.loads() == [], \
        f"a private reranker loaded the model on a free GPU slot although no private may run (W2-145): {box.loads()}"
    assert box.slots_held() == 0, f"{box.slots_held()} GPU slots are held after the search: no reranker runs"


def test_with_both_gpu_slots_held_and_the_service_unable_to_start_the_search_goes_on_unranked_without_waiting(boxes):
    wait = 5.0
    box = boxes(settings={support.WAIT_SETTING: wait})
    box.block_service()
    box.hold_slots()
    query, given = query_of("slots-held"), candidates("slots-held", 5)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised with both GPU slots held: {raised(report)}"
    check_unranked(report["result"], given, "the search with both GPU slots held")
    assert report["seconds"] <= NO_WAIT_S, \
        (f"the search went on after {report['seconds']:.1f} s: with the service unable to start it is to come back "
         f"within {NO_WAIT_S:g} s, never waiting {wait:g} s for a GPU slot")
    assert box.scorers_of(query) == set(), f"the texts were scored by {box.scorers_of(query)}"
    assert box.loads() == [], f"a model was loaded: {box.loads()}"


def test_a_slot_that_frees_while_the_search_runs_is_taken_by_no_private_reranker(boxes):
    box = boxes(settings={support.WAIT_SETTING: 8})
    box.block_service()
    box.hold_slots()
    query, given = query_of("slot-frees"), candidates("slot-frees", 5)
    session = box.start({"query": query, "candidates": given})
    time.sleep(0.3)
    box.release_slots()
    report = session.wait()
    assert raised(report) is None, f"the search raised: {raised(report)}"
    check_unranked(report["result"], given, "the search during which a GPU slot freed")
    assert box.loads() == [], f"a private reranker took the slot that freed and loaded the model: {box.loads()}"
    assert box.slots_held() == 0, "a GPU slot is held after the search: a private reranker took it"


@pytest.mark.parametrize("why", ["no-gpu", "gpu-hidden"])
def test_a_fallback_never_runs_a_reranker_on_the_cpu(boxes, why):
    box = boxes(gpu=support.NO_GPU if why == "no-gpu" else support.ROOM)
    box.block_service()
    env = box.env(CUDA_VISIBLE_DEVICES="-1") if why == "gpu-hidden" else None
    query, given = query_of(f"cpu-{why}"), candidates(f"cpu-{why}", 5)
    report = box.search(query, given, env=env)
    assert raised(report) is None, f"the search raised ({why}): {raised(report)}"
    assert report["seconds"] <= support.UNRANKED_S, f"the search took {report['seconds']:.1f} s ({why})"
    on_cpu = [record["pid"] for record in box.loads() if record["device"] == "cpu"]
    assert on_cpu == [], f"a reranker ran on the CPU ({why}): KPI 7 forbids it"
    assert box.loads() == [], f"a private reranker loaded the model ({why}): W2-145 forbids any: {box.loads()}"
    check_unranked(report["result"], given, f"the search whose service cannot start ({why})")


# ---- the service's GPU slots: every one, for its life (W2-145 S3; was DEC-1036 T6 (b), one of the two)


def test_the_service_holds_every_gpu_slot(box):
    service = box.warm()
    loaded = [record for record in box.loads() if record["pid"] == service][0]
    assert loaded["slots_held"] and loaded["slots_held"] >= 1, \
        f"the service loaded its model while no GPU slot was held in {support.LOCK_DIR_SETTING} (DEC-1036 T6)"
    deadline = time.monotonic() + 3.0
    while not _all_slots_held(box) and time.monotonic() < deadline:
        time.sleep(0.05)
    held = box.slots_held()
    assert held == support.SLOTS, \
        f"with the service up and nothing else running, {held} of {support.SLOTS} GPU slots are held: it is to hold all"


def test_with_the_service_up_no_slot_is_left_and_a_failing_service_leaves_the_search_unranked_at_once(boxes):
    box = boxes(settings={support.WAIT_SETTING: 2.0})
    service = box.warm()
    deadline = time.monotonic() + 3.0
    while not _all_slots_held(box) and time.monotonic() < deadline:
        time.sleep(0.05)
    taken = box.hold_free_slots()
    assert taken == [], f"with the service up, the test could take GPU slots {taken}: the service is to hold them all"
    box.for_pid(service, predict_error=True)  # the service now answers with an error: the search goes on unranked
    query, given = query_of("beside"), candidates("beside", 5)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised: {raised(report)}"
    check_unranked(report["result"], given, "the search whose service failed")
    check_named_unavailable(report, "the search whose service failed")
    assert report["seconds"] <= support.UNRANKED_S, f"the search took {report['seconds']:.1f} s"
    beside = [(record["pid"], record["device"]) for record in box.loads() if record["pid"] != service]
    assert beside == [], f"a private reranker loaded the model beside the service ({beside})"


def test_with_both_slots_held_before_any_service_the_search_goes_on_unranked_with_no_model_loaded(boxes):
    wait = 4.0
    box = boxes(settings={support.WAIT_SETTING: wait})
    box.hold_slots()
    query, given = query_of("no-slot"), candidates("no-slot", 5)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised with both GPU slots held: {raised(report)}"
    check_unranked(report["result"], given, "the search with both GPU slots held before any service")
    check_named_unavailable(report, "the search with both GPU slots held before any service", r"slot")
    # The service waits for a slot like any reranker and refuses; the search then comes back at once: one wait, the
    # service's, never a second one (a private's).
    assert report["seconds"] <= wait + NO_WAIT_S, \
        f"the search took {report['seconds']:.1f} s: one slot wait ({wait:g} s, the service's) and {NO_WAIT_S:g} s at most"
    loads = [(record["pid"], record["device"]) for record in box.loads()]
    assert loads == [], \
        (f"a model was loaded although both GPU slots were held ({loads}): the service cannot start on the GPU "
         "without a slot, and no reranker runs on the CPU")
    assert box.live_loads() == [], "a service holds the model without a GPU slot"
