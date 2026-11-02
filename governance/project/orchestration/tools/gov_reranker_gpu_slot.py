"""Gov OS: a reranker runs on a GPU slot or not at all; none grinds on the CPU (DEC-1033; before it DEC-1031 item 2).

Loaded at start-up by `gov-reranker-gpu-slot.pth` in the reranker environment, so it runs in every Python of that
environment; it acts only in the reranker worker (`rerank_worker.py`, by its path or as `-m ...rerank_worker`) and
leaves every other Python untouched. The worker tries to hold one of `GOV_RERANK_GPU_SLOTS` (default 2) lock files in
`GOV_RERANK_GPU_LOCK_DIR` (default /tmp) for its whole life; with one, it keeps the GPU. Without one, it polls the
locks once a second for up to `GOV_RERANK_GPU_WAIT_S` seconds (default 20); if none frees, it ends at once, before
the worker imports torch or loads a model, with a named line on standard error and exit code 75. `gov.retrieval.
rerank` then sees a worker that ended without the model and the search goes on unranked (`merge.reranked` false,
DEC-374). A lock is released when its process ends, whatever the end. So the GPU never holds more than that many
rerankers beside the pinned embedder, and no reranker runs on the CPU.

It never hides the GPU to run on the CPU, and a worker started with the GPU already hidden (`CUDA_VISIBLE_DEVICES`
-1 or empty) ends named too (exit 76), unless `GOV_RERANK_ALLOW_CPU=1`, the explicit opt-out for tests, which keeps
the old behaviour: no free slot at once means the CPU. Any error here ends the worker named (exit 70): no CPU grind,
no crowding the GPU. `sys.exit` is not used: raised from a `.pth` it is a fatal start-up error. Until W2-112's shared
reranker replaces it.
"""
import os
import sys

NO_SLOT = 75  # no slot freed within the wait (EX_TEMPFAIL)
GPU_HIDDEN = 76  # the caller hid the GPU and did not opt in to the CPU
FAILED = 70  # an error inside this module (EX_SOFTWARE)

_HELD = None


def _end(code, reason):
    """Ends this process at once: one named line on standard error, nothing on standard output, ``code``."""
    try:
        os.write(2, f"gov reranker: {reason}; this search goes without reranking\n".encode("utf-8", "replace"))
    finally:
        os._exit(code)


def _is_worker():
    """True in the reranker worker: ``python [-I] .../rerank_worker.py ...`` or ``python -m ...rerank_worker ...``.

    While a .pth runs, ``sys.argv`` is already the script's: its path first, or ``-m`` for a module, whose name is
    then only in ``sys.orig_argv``, just before the arguments that ``sys.argv`` repeats.
    """
    argv = list(getattr(sys, "argv", None) or [])
    if not argv:
        return False
    if argv[0] == "-m":
        orig = list(getattr(sys, "orig_argv", None) or [])
        at = len(orig) - len(argv)
        return 1 <= at < len(orig) and orig[at].rsplit(".", 1)[-1] == "rerank_worker"
    return os.path.basename(argv[0]) == "rerank_worker.py"


def _take(folder, slots):
    """The number of the slot now held for this process's life, or None when every slot is held."""
    global _HELD
    import fcntl

    for i in range(slots):
        fd = os.open(os.path.join(folder, f"gov-os-rerank-gpu-{i}.lock"), os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(fd)
            continue
        except BaseException:
            os.close(fd)
            raise
        os.set_inheritable(fd, False)
        _HELD = fd  # kept open for the process's life
        return i
    return None


def _main():
    if not _is_worker():
        return
    allow_cpu = os.environ.get("GOV_RERANK_ALLOW_CPU") == "1"
    hidden = os.environ.get("CUDA_VISIBLE_DEVICES")
    if hidden in ("-1", ""):
        if allow_cpu:
            return  # the CPU, asked for
        _end(GPU_HIDDEN, f"the GPU is hidden from it (CUDA_VISIBLE_DEVICES={hidden!r}) and GOV_RERANK_ALLOW_CPU is "
                         f"not 1")
    import time

    slots = int(os.environ.get("GOV_RERANK_GPU_SLOTS", "2"))
    wait = float(os.environ.get("GOV_RERANK_GPU_WAIT_S", "20"))
    if not 0 <= wait < float("inf"):  # nan or infinite: never an unbounded wait (review F2)
        raise ValueError("GOV_RERANK_GPU_WAIT_S must be a finite number of seconds")
    folder = os.environ.get("GOV_RERANK_GPU_LOCK_DIR", "/tmp")
    deadline = time.monotonic() + wait
    while True:
        slot = _take(folder, slots)
        if slot is not None:
            os.environ["GOV_RERANK_GPU_SLOT"] = str(slot)
            return
        if allow_cpu:  # the old fallback, for tests only
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
            return
        left = deadline - time.monotonic()
        if left <= 0:
            _end(NO_SLOT, f"no GPU slot free within {wait:g} s")
        time.sleep(min(1.0, left))


try:
    _main()
except BaseException as exc:  # noqa: BLE001 - any error, an interrupt too: end named, never the CPU or a crowded GPU
    _end(FAILED, f"the GPU slot check failed ({type(exc).__name__}: {exc})")
