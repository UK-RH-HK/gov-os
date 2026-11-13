"""The reranker's model call and GPU slot rule, shared with the one shared reranker service (W1-19, W2-112, W2-145;
ADR-0002 §2, DEC-397). Never imported except by ``rerank_service.py``, which loads it by its file and shares
``take_slot``, ``load``, ``scores`` and ``device_of``.

No private reranker runs (W2-145; DEC-1048 (5), DEC-1046 (1)): run as a program, this file ends at once, named
("no private reranker runs: the shared service reranks", exit 69), before torch or the model loads. A search the
shared service cannot answer stays unranked and named (``gov.retrieval.rerank``).

The GPU slot rule (DEC-1033, DEC-1036 T6): before torch or the model loads, the service holds one of
``GOV_RERANK_GPU_SLOTS`` (default 2) lock files ``gov-os-rerank-gpu-<n>.lock`` in ``GOV_RERANK_GPU_LOCK_DIR`` (default
/tmp) for its life, waiting for one up to ``GOV_RERANK_GPU_WAIT_S`` (default 20) seconds; without one it ends named
(exit 75). It never hides the GPU to run on the CPU: a GPU already hidden ends it named (exit 76). No setting opens a
CPU path (W2-145 S2).
"""

import os
import sys
import time

NO_SLOT, GPU_HIDDEN, NO_GPU = 75, 76, 78
NO_PRIVATE = 69  # run as a program: no private reranker runs (EX_UNAVAILABLE)
ENDED = "no private reranker runs: the shared service reranks"
_HELD = []  # the slot's lock file, open for the process's life


def take_slot(allow_cpu: bool = False):
    """None when this process may load its model, holding a GPU slot for its life; otherwise ``(exit code,
    reason)``. ``allow_cpu`` is kept for the callers' signature and opens nothing: no reranker runs on the CPU
    (DEC-1036, DEC-1048 (5))."""
    import fcntl

    del allow_cpu  # W2-145 S2: never the CPU, whatever the caller asks
    if os.environ.get("GOV_RERANK_GPU_SLOT"):
        return None  # the interim module holds one for this process
    if os.environ.get("CUDA_VISIBLE_DEVICES") in ("-1", ""):
        return GPU_HIDDEN, "the GPU is hidden from it (CUDA_VISIBLE_DEVICES), and no reranker runs on the CPU"
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


def main(*_args) -> None:
    """Run as a program (an older caller's private reranker): ends at once, named, before anything loads."""
    print(ENDED, file=sys.stderr, flush=True)
    sys.exit(NO_PRIVATE)


if __name__ == "__main__":
    main(*sys.argv[1:])
