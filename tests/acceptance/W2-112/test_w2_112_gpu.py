"""KPI success 6 and 7: the GPU budget (DEC-1032, DEC-1031 item 2).

The service runs its one model on the GPU when there is one, within the GPU budget (the embedder first, about
3.5 GB; the shared reranker second, about 2.5 to 3.5 GB; at least 2 GB headroom): it never starts on the GPU when
less than its share is free (it starts on the CPU), and never more than one copy on the GPU. The fallback private
reranker runs on the CPU only when the service is down.

The GPU is the stand-in's: ``torch.cuda`` and ``nvidia-smi`` in the box report its memory, and the stand-in model
records the device it was loaded on (the one named, or the library's choice: the GPU when one is visible). The
figures are far from the share's edges (14 GiB free, or 1 GiB), so no exact share is assumed. That the CPU is
named and an alert raised are read in ``test_w2_112_surfaces.py``; the real GPU's memory is the research
document's measurement.
"""

from __future__ import annotations

import pytest

import w2_112_support as support
from w2_112_support import candidates, check_scored, query_of, raised

GIB = support.GIB
ROOM = {"present": True, "total": 16 * GIB, "free": 14 * GIB, "name": "Stand-in GPU"}
SHORT = {"present": True, "total": 16 * GIB, "free": 1 * GIB, "name": "Stand-in GPU"}
NONE = {"present": False}


def _device_of(box, pid):
    devices = [record["device"] for record in box.events() if record["pid"] == pid and record["event"] in ("load",
                                                                                                           "move")]
    return devices[0] if devices else None


def test_with_room_on_the_gpu_the_service_runs_its_one_model_there(boxes):
    box = boxes(gpu=ROOM)
    service = box.warm()
    assert _device_of(box, service) == "cuda", \
        f"with 14 GiB of 16 free the service loaded its model on {_device_of(box, service)}, not on the GPU"
    assert box.on_gpu() == [service], f"the copies on the GPU are {box.on_gpu()}, not the service's one"


@pytest.mark.parametrize("gpu", [SHORT, NONE], ids=["less-than-its-share-free", "no-gpu"])
def test_without_its_share_of_the_gpu_free_the_service_starts_on_the_cpu(boxes, gpu):
    box = boxes(gpu=gpu)
    service = box.warm()
    loaded = [record for record in box.events("load") if record["pid"] == service][0]
    assert loaded["device"] == "cpu", \
        f"the service loaded its model on {loaded['device']} with {gpu}: below its share it starts on the CPU"
    assert box.on_gpu() == [], f"a copy of the model is on the GPU although its share is not free: {box.on_gpu()}"


def _block_the_service(box):
    folder = box.socket.parent
    folder.parent.mkdir(parents=True, exist_ok=True)
    folder.write_text("not a folder: the W2-112 tests keep the service from starting\n", encoding="utf-8")


def test_the_fallback_private_reranker_runs_on_the_cpu_when_the_service_cannot_start(boxes):
    box = boxes(gpu=ROOM)
    _block_the_service(box)
    query, given = query_of("cpu-fallback"), candidates("cpu-fallback", 5)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised: {raised(report)}"
    check_scored(report["result"], query, given, "the search whose service cannot start")
    scorers = box.scorers_of(query)
    private = [record for record in box.events("load") if record["pid"] in scorers]
    assert private, "no private reranker that scored the search loaded the model"
    assert all(record["device"] == "cpu" for record in private), \
        (f"the fallback private reranker loaded its model on {[r['device'] for r in private]} with the GPU free: "
         "it runs on the CPU only")


def test_while_the_service_holds_the_gpu_a_fallback_never_puts_a_second_copy_there(boxes):
    box = boxes(gpu=ROOM)
    service = box.warm()
    box.for_pid(service, predict_error=True)
    query, given = query_of("second-copy"), candidates("second-copy", 5)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised: {raised(report)}"
    check_scored(report["result"], query, given, "the search whose service failed to score")
    others = [record for record in box.events("load") if record["pid"] != service]
    assert others, "no private reranker loaded the model although the service failed to score"
    assert all(record["device"] == "cpu" for record in others), \
        (f"a fallback loaded the model on {[r['device'] for r in others]} while the service held the GPU: never "
         "more than one copy on the GPU")
    assert len([record for record in box.events("load") if record["device"] == "cuda"]) == 1
