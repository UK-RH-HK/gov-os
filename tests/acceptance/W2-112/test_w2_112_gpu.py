"""KPI success 6, as decided by DEC-1036 T5 (b): the service's GPU budget, and no reranker on the CPU anywhere.

The service runs its one model on the GPU when there is one, within the GPU budget (DEC-1032: the embedder first,
about 3.5 GB; the shared reranker second, about 2.5 to 3.5 GB; at least 2 GB headroom), and never more than one
copy on the GPU. DEC-1036 T5 (b): "below its GPU share the service does not start; searches fall back through the
slot rule or go unranked, named (no reranker on the CPU anywhere, DEC-1033)".

The GPU is the stand-in's: ``torch.cuda`` and ``nvidia-smi`` in the box report its memory, and the stand-in model
records the device it was loaded on. The figures are far from the share's edges (14 GiB free, or 1 GiB), so no
exact share is assumed. Below its share (1 GiB free) a search may still be answered by a private reranker on a
free GPU slot, or go on unranked: whether a private reranker also weighs the GPU's free memory is not stated, so
either is taken; with no GPU at all the search goes on unranked. The reason reaches the fallback log under
``~/.cache/gov-os/`` (DEC-1034 item 3) and the bundle (``test_w2_112_bundle.py``); nothing more specific is held.
The service's GPU slot (DEC-1036 T6 (b)) and the fallback's slot rule (KPI 7) are in ``test_w2_112_slots.py``; the
real GPU's memory is the research document's.

"Never more than one copy on the GPU" is held as the service's: one service loads one copy, however many searches
start it (also in the 20-concurrent case). The slot rule bounds the rest: the service holds one of the two slots,
so at most one private reranker beside it.
"""

from __future__ import annotations

import re
import time

import pytest

import w2_112_support as support
from w2_112_support import candidates, check_scored, check_scored_or_unranked, check_unranked, query_of, raised

BELOW = [support.SHORT, support.NO_GPU]
BELOW_IDS = ["less-than-its-share-free", "no-gpu"]
FALLBACK = re.compile(r"rerank|fall|fell|unavailable|private", re.IGNORECASE)
REASON = re.compile(r"gpu|cuda|share|memory", re.IGNORECASE)


def _device_of(box, pid):
    devices = [record["device"] for record in box.events() if record["pid"] == pid and record["event"] in ("load",
                                                                                                           "move")]
    return devices[0] if devices else None


def test_with_room_on_the_gpu_the_service_runs_its_one_model_there(boxes):
    box = boxes(gpu=support.ROOM)
    service = box.warm()
    assert _device_of(box, service) == "cuda", \
        f"with 14 GiB of 16 free the service loaded its model on {_device_of(box, service)}, not on the GPU"
    assert box.on_gpu() == [service], f"the copies on the GPU are {box.on_gpu()}, not the service's one"


@pytest.mark.parametrize("gpu", BELOW, ids=BELOW_IDS)
def test_below_its_share_or_without_a_gpu_the_service_does_not_start_and_nothing_loads_on_the_cpu(boxes, gpu):
    box = boxes(gpu=gpu)
    for number in (1, 2):  # a second search does not start it either
        query, given = query_of(f"below-{number}"), candidates(f"below-{number}", 5)
        report = box.search(query, given)
        who = f"search {number} with {gpu}"
        assert raised(report) is None, f"{who} raised: {raised(report)}"
        assert report["seconds"] <= support.SLOT_WAIT_S + support.FALLBACK_S, f"{who} took {report['seconds']:.1f} s"
        on_cpu = [record["pid"] for record in box.loads() if record["device"] == "cpu"]
        assert on_cpu == [], \
            f"{who}: a model was loaded on the CPU ({on_cpu}): no reranker runs on the CPU anywhere (DEC-1036, DEC-1033)"
        live = [record["pid"] for record in box.live_loads()]
        assert live == [], f"{who}: a service holds the model ({live}) although its share of the GPU is not free"
        if gpu is support.NO_GPU:
            check_unranked(report["result"], given, who)
        elif check_scored_or_unranked(report["result"], query, given, who) == "scored":
            scorers = [record for record in box.loads() if record["pid"] in box.scorers_of(query)]
            assert scorers and all(record["device"] == "cuda" for record in scorers), \
                f"{who} was answered, but not by a private reranker on the GPU: {scorers}"


@pytest.mark.parametrize("gpu", BELOW, ids=BELOW_IDS)
def test_below_its_share_the_fallback_and_its_reason_are_logged_under_the_users_cache_folder(boxes, gpu):
    box = boxes(gpu=gpu)
    since = time.time()
    query, given = query_of("below-logged"), candidates("below-logged", 4)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised with {gpu}: {raised(report)}"
    found = box.cache_texts(since)
    assert any(FALLBACK.search(text) and REASON.search(text) for text in found), \
        (f"with {gpu} the service does not start, and no file under ~/{support.CACHE_REL}/ logs the fallback with "
         f"its reason (the GPU, its share or its memory; DEC-1034 item 3, DEC-1036): {found!r}")[:1500]


def test_searches_starting_together_put_one_copy_of_the_model_on_the_gpu(boxes):
    box = boxes(gpu=support.ROOM)
    box.config(load_delay=0.5)
    tags = [f"g{number}" for number in range(6)]
    reports = box.together([{"query": query_of(tag), "candidates": candidates(tag, 4)} for tag in tags])
    for tag, report in zip(tags, reports):
        assert raised(report) is None, f"search {tag} raised: {raised(report)}"
        check_scored(report["result"], query_of(tag), candidates(tag, 4), f"search {tag}")
    on_gpu = [record["pid"] for record in box.loads() if record["device"] == "cuda"]
    assert len(on_gpu) == 1, f"six searches starting together put {len(on_gpu)} copies of the model on the GPU"
