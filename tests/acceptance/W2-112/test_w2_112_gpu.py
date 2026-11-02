"""KPI success 6: the service's GPU budget (DEC-1032, DEC-1031 item 2).

The service runs its one model on the GPU when there is one, within the GPU budget (the embedder first, about
3.5 GB; the shared reranker second, about 2.5 to 3.5 GB; at least 2 GB headroom): it never starts on the GPU when
less than its share is free (it starts on the CPU, named, and alerts), and never more than one copy on the GPU.

The GPU is the stand-in's: ``torch.cuda`` and ``nvidia-smi`` in the box report its memory, and the stand-in model
records the device it was loaded on (the one named, or the library's choice: the GPU when one is visible). The
figures are far from the share's edges (14 GiB free, or 1 GiB), so no exact share is assumed. The alert is read
in a file under ``~/.cache/gov-os/`` (DEC-1034 item 3); the CPU named in the bundle is in ``test_w2_112_bundle.py``;
the fallback's own GPU rule (KPI 7) in ``test_w2_112_slots.py``; the real GPU's memory is the research document's.

"Never more than one copy on the GPU" is held here as the service's: one service loads one copy, however many
searches start it (also in the 20-concurrent case). Fallback private rerankers are bounded by the GPU slot rule.
"""

from __future__ import annotations

import re
import time

import pytest

import w2_112_support as support
from w2_112_support import candidates, check_scored, query_of, raised


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


@pytest.mark.parametrize("gpu", [support.SHORT, support.NO_GPU], ids=["less-than-its-share-free", "no-gpu"])
def test_without_its_share_of_the_gpu_free_the_service_starts_on_the_cpu(boxes, gpu):
    box = boxes(gpu=gpu)
    service = box.warm()
    loaded = [record for record in box.events("load") if record["pid"] == service][0]
    assert loaded["device"] == "cpu", \
        f"the service loaded its model on {loaded['device']} with {gpu}: below its share it starts on the CPU"
    assert box.on_gpu() == [], f"a copy of the model is on the GPU although its share is not free: {box.on_gpu()}"


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


def test_the_service_alerts_when_it_starts_on_the_cpu_below_its_share(boxes):
    box = boxes(gpu=support.SHORT)
    since = time.time()
    box.warm()
    found = box.cache_texts(since)
    assert any(re.search(r"\bcpu\b", text, re.IGNORECASE) for text in found), \
        (f"the service started on the CPU below its share of the GPU, and no file under ~/{support.CACHE_REL}/ "
         f"names the CPU (DEC-1034 item 3): {found!r}")[:1500]
