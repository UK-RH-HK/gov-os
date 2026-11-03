"""The shared reranker: one process per user serves every session's searches (W2-112; DEC-979 item 4, DEC-1032).

Started by ``gov.retrieval.rerank`` with the reranker environment's interpreter, never imported by it:
``python -I rerank_service.py MODEL REVISION SOCKET LOCK_FD``. ``LOCK_FD`` is the start lock (``rerank.lock`` beside
the socket), taken by the search that started it and held by this process for its life, so no second service starts
while it lives. The same pinned model and the same model call as ``rerank_worker.py`` (``load`` and ``scores``).

- **The GPU slots (DEC-1036 T6):** first it takes one of the private rerankers' GPU slots for its life, with their
  rule (``rerank_worker.take_slot``: the same locks and settings, a wait of ``GOV_RERANK_GPU_WAIT_S``), never
  allowing the CPU; so at most one private reranker runs beside it. Without a slot it ends named (exit 75; 76 when
  the GPU is hidden). The interim module ``gov_reranker_gpu_slot`` acts only on ``rerank_worker.py``, never here.
- **The GPU only (DEC-1036 T5, DEC-1032, DEC-1033):** holding a slot, it reads the GPU's free memory with the
  library that will hold it (``torch.cuda.mem_get_info``). Less than its share plus the headroom free, or no GPU to
  read: it does not start (exit 77). It never loads on the CPU. Every refusal is a REFUSED line in ``rerank.log``,
  and the search falls back.
- **Requests:** one connection per request, answered first come, first served, one request at a time (no batching
  across callers, so every answer is a private reranker's): ``[query, [text, …]]`` in, one JSON line out,
  ``{"scores": […], "device": …}`` or ``{"error": …, "device": …}``. More than ``MAX_TEXTS`` texts is refused.
- **Idle end:** with no request for ``GOV_RERANK_IDLE_S`` seconds (default 900) it removes its socket, answers what
  was already queued, and ends. Stopped with SIGTERM, it removes its socket and ends at once.
"""

import importlib.util
import json
import os
import signal
import socket
import sys
import time

# The worker's model call, by its file: this folder is never put on the path (its modules would shadow libraries).
_spec = importlib.util.spec_from_file_location("rerank_worker", os.path.join(os.path.dirname(__file__),
                                                                              "rerank_worker.py"))
_worker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_worker)
load, scores, device_of = _worker.load, _worker.scores, _worker.device_of

NO_GPU_SHARE = 77  # holding a slot, the GPU has too little free memory, or none can be read
GIB = 2 ** 30
SHARE, HEADROOM = 3.5 * GIB, 2.0 * GIB  # DEC-1032: the reranker's share (2.5 to 3.5 GB, the top taken), 2 GB spare
MAX_TEXTS = 512  # a search sends at most (rounds + 1) x batch size candidates: 90 at the defaults
READ_S = 10.0  # a caller sends its request as soon as it connects


def _free_gpu() -> int:
    import torch

    return torch.cuda.mem_get_info()[0]


def gpu_short(free=_free_gpu):
    """None when the GPU has the share and the headroom free; otherwise why the service does not start."""
    try:
        left = free()
    except Exception as error:  # no GPU, no CUDA, no torch: nothing to read
        return f"the GPU's free memory could not be read ({type(error).__name__}: {error})"
    if left < SHARE + HEADROOM:
        return f"the GPU has {left / GIB:.1f} GiB free, under the {(SHARE + HEADROOM) / GIB:.1f} GiB needed"
    return None


def note(log: str, kind: str, detail: str) -> None:
    with open(log, "a", encoding="utf-8") as out:
        out.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')}\t{kind}\t{detail}\n")


def answer(encoder, device: str, line: bytes) -> dict:
    try:
        query, texts = json.loads(line)
        if not isinstance(query, str) or not isinstance(texts, list) or len(texts) > MAX_TEXTS:
            raise ValueError(f"a request is a question and at most {MAX_TEXTS} texts")
        return {"scores": scores(encoder, query, texts), "device": device}
    except Exception as error:
        return {"error": f"{type(error).__name__}: {error}", "device": device}


def serve(listener, encoder, device: str) -> None:
    connection, _ = listener.accept()
    with connection:
        try:
            connection.settimeout(READ_S)
            line = connection.makefile("rb").readline(64 * 2 ** 20)
            connection.sendall((json.dumps(answer(encoder, device, line)) + "\n").encode())
        except OSError:
            pass  # the caller gave up: its search has gone on without this answer


def main(model: str, revision: str, path: str, lock_fd: str) -> None:
    os.set_inheritable(int(lock_fd), False)  # held until this process ends, and by no child of it
    sys.stdout = sys.stderr  # whatever the libraries print goes to the service's own log
    log, idle = os.path.join(os.path.dirname(path), "rerank.log"), float(os.environ.get("GOV_RERANK_IDLE_S", "900"))
    refused = _worker.take_slot(allow_cpu=False)  # before the free-memory reading and the load (DEC-1036 T6)
    if refused is None:
        short = gpu_short()
        refused = (NO_GPU_SHARE, short) if short else None
    if refused:
        note(log, "REFUSED", f"the shared reranker does not start: {refused[1]}")
        sys.exit(refused[0])
    encoder = load(model, revision)  # the worker's call: the library's device, the GPU it has just read
    device = device_of(encoder) or "cuda"
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    mask = os.umask(0o177)
    try:
        listener.bind(path)  # created 0600: the user's alone
    finally:
        os.umask(mask)

    def stop(signum, _frame):  # stopped (SIGTERM): no stale socket left; the slot and the lock go with the process
        if os.path.lexists(path):
            os.unlink(path)
        note(log, "END", f"pid {os.getpid()} signal {signum}")
        os._exit(0)

    signal.signal(signal.SIGTERM, stop)
    listener.listen(128)
    note(log, "READY", f"pid {os.getpid()} device {device}")
    listener.settimeout(idle)
    try:
        while True:
            serve(listener, encoder, device)
    except socket.timeout:
        os.unlink(path)  # no new caller reaches it; those already queued are answered
        listener.settimeout(0.2)
        try:
            while True:
                serve(listener, encoder, device)
        except OSError:
            pass
    note(log, "END", f"pid {os.getpid()} idle {idle:g} s")


if __name__ == "__main__":
    main(*sys.argv[1:5])
