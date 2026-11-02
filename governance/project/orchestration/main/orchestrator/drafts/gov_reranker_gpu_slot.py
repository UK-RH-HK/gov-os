"""Gov OS: at most a few rerankers on the GPU at once, the rest on the CPU (DEC-1031 item 2; ACT-RERANK-GPU-SLOTS-1).

Loaded at start-up by `gov-reranker-gpu-slot.pth` in the reranker environment. Each process tries to hold one of
`GOV_RERANK_GPU_SLOTS` (default 2) lock files for its whole life; with one, it keeps the GPU; without one, it hides
the GPU (`CUDA_VISIBLE_DEVICES=-1`) and runs on the CPU. A lock is released when its process ends, whatever the end.
So the GPU never holds more than that many rerankers (about 3.5 GiB each) beside the pinned embedder (about 3.5 GiB):
the embedder is never pushed off. Any error here hides the GPU (fails safe for the embedder). Until W2-112's shared
reranker replaces it.
"""
import os

_HELD = None


def _claim():
    global _HELD
    if os.environ.get("CUDA_VISIBLE_DEVICES") == "-1":
        return
    try:
        import fcntl
        slots = int(os.environ.get("GOV_RERANK_GPU_SLOTS", "2"))
        folder = os.environ.get("GOV_RERANK_GPU_LOCK_DIR", "/tmp")
        for i in range(slots):
            fd = os.open(os.path.join(folder, f"gov-os-rerank-gpu-{i}.lock"), os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                os.close(fd)
                continue
            os.set_inheritable(fd, False)
            _HELD = fd  # kept open for the process's life
            os.environ["GOV_RERANK_GPU_SLOT"] = str(i)
            return
    except Exception:  # noqa: BLE001 - any error: the CPU, never a crowded GPU
        pass
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


_claim()
