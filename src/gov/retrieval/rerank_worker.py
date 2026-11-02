"""The reranker's own process (W1-19; ADR-0002 §2, DEC-397). Started by ``gov.retrieval.rerank``, never imported
except by ``rerank_service.py``, which shares ``take_slot``, ``load`` and ``scores``.

It runs in the reranker environment, loads the pinned model once, and then answers one line with one line until
its caller closes the pipe: ``[query, [text, …]]`` in, ``[score, …]`` out, as JSON. The first line it writes says
the model is loaded and on which device (``{"device": ...}``); a process that ends without it has no model, and its
reason is on standard error.

The GPU slot rule (DEC-1033, W2-112): before torch or the model loads, the worker holds one of
``GOV_RERANK_GPU_SLOTS`` (default 2) lock files ``gov-os-rerank-gpu-<n>.lock`` in ``GOV_RERANK_GPU_LOCK_DIR`` (default
/tmp) for its life, waiting for one up to ``GOV_RERANK_GPU_WAIT_S`` (default 20) seconds; without one it ends named
(exit 75). It never hides the GPU to run on the CPU: a GPU already hidden ends it named (exit 76), unless
``GOV_RERANK_ALLOW_CPU=1`` (tests and measurements only). While the interim module ``gov_reranker_gpu_slot`` is
installed it has already taken a slot in this process (``GOV_RERANK_GPU_SLOT``), and the worker takes nothing more.
"""

import json
import os
import sys
import time

NO_SLOT, GPU_HIDDEN = 75, 76
_HELD = []  # the slot's lock file, open for the process's life


def take_slot(allow_cpu: bool):
    """None when this process may load its model, holding a GPU slot for its life (or, with ``allow_cpu``, on the
    CPU); otherwise ``(exit code, reason)``. The shared service calls it too, never allowing the CPU (DEC-1036)."""
    import fcntl

    if os.environ.get("GOV_RERANK_GPU_SLOT"):
        return None  # the interim module holds one for this process
    if os.environ.get("CUDA_VISIBLE_DEVICES") in ("-1", ""):
        return None if allow_cpu else (GPU_HIDDEN, "the GPU is hidden from it (CUDA_VISIBLE_DEVICES), and no "
                                                   "reranker runs on the CPU")
    slots, wait = int(os.environ.get("GOV_RERANK_GPU_SLOTS", "2")), float(os.environ.get("GOV_RERANK_GPU_WAIT_S", "20"))
    if not 0 <= wait < float("inf"):
        raise ValueError("GOV_RERANK_GPU_WAIT_S must be a finite number of seconds")
    folder, deadline = os.environ.get("GOV_RERANK_GPU_LOCK_DIR", "/tmp"), time.monotonic() + wait
    while True:
        for i in range(slots):
            fd = os.open(os.path.join(folder, f"gov-os-rerank-gpu-{i}.lock"), os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                os.close(fd)
                continue
            _HELD.append(fd)
            os.environ["GOV_RERANK_GPU_SLOT"] = str(i)
            return None
        if allow_cpu:  # the old fallback, for tests only
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
            return None
        if time.monotonic() >= deadline:
            return NO_SLOT, f"no GPU slot free within {wait:g} s"
        time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))


def load(model: str, revision: str, device: str | None = None):
    """The pinned cross-encoder; ``device`` None is the library's choice (the GPU when there is one), as before."""
    from sentence_transformers import CrossEncoder

    # The snapshot's own configuration carries the instruction and the yes/no scoring.
    return CrossEncoder(model, revision=revision, **({"device": device} if device else {}))


def scores(encoder, query: str, texts: list) -> list:
    return [float(score) for score in encoder.predict([(query, text) for text in texts])]


def device_of(encoder) -> str | None:
    return str(getattr(encoder, "device", "") or "") or None


def main(model: str, revision: str) -> None:
    answers, sys.stdout = sys.stdout, sys.stderr  # whatever the libraries print stays out of the answers
    refused = take_slot(os.environ.get("GOV_RERANK_ALLOW_CPU") == "1")
    if refused:
        print(f"gov reranker: {refused[1]}; this search goes without reranking", file=sys.stderr, flush=True)
        sys.exit(refused[0])
    encoder = load(model, revision)
    print(json.dumps({"device": device_of(encoder)}), file=answers, flush=True)
    for line in sys.stdin:
        query, texts = json.loads(line)
        print(json.dumps(scores(encoder, query, texts)), file=answers, flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:3])
