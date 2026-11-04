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
- **Memory after each request (DEC-1068, re-pin window 4):** once a request's answer is sent (or the caller has
  gone, or the request failed, a GPU out-of-memory among them), the service empties PyTorch's caching allocator
  (``torch.cuda.empty_cache()``), so its GPU memory falls back to the model's between requests instead of staying at
  the highest peak any request reached (7.7 -> 15.8 GB on 2026-11-04). After every request, not only after large
  ones: a threshold on the padded size would need a measured value this code cannot know (the padded bound,
  ``rerank.MAX_REQUEST_CHARS``, already sets the largest), and below it the cache would still climb to the bound's peak
  and hold it beside the embedder. The cost per request is the device sync and the frees of ``empty_cache`` and the
  next request's fresh allocations, estimated at a few milliseconds against a request's hundreds (to be measured on
  the GPU in window 4). Then one line in ``rerank.log``: ``MEMORY``, ``allocated <n> MiB, reserved <n> MiB``
  (``torch.cuda.memory_allocated`` and ``memory_reserved``, after the release); a release that fails is the line
  ``MEMORY``, ``not released (<error>)``, and the service goes on.
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
GIB, MIB = 2 ** 30, 2 ** 20
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


def release() -> str:
    """The GPU memory a request used given back (DEC-1068): the caching allocator's cache emptied; the detail of the
    ``MEMORY`` line, the allocated and reserved MiB after it."""
    import torch

    torch.cuda.empty_cache()
    return (f"allocated {torch.cuda.memory_allocated() / MIB:.0f} MiB, "
            f"reserved {torch.cuda.memory_reserved() / MIB:.0f} MiB")


def released(log: str) -> None:
    """``release`` and its ``MEMORY`` line; neither a failed release nor an unwritable log ends the service."""
    try:
        detail = release()
    except Exception as error:
        detail = f"not released ({type(error).__name__}: {error})"
    try:
        note(log, "MEMORY", detail)
    except OSError:
        pass


def serve(listener, encoder, device: str, log: str) -> None:
    connection, _ = listener.accept()
    asked = False
    try:
        with connection:
            try:
                connection.settimeout(READ_S)
                line = connection.makefile("rb").readline(64 * 2 ** 20)
                asked = True  # from here the request may reach the model, so its memory is released
                connection.sendall((json.dumps(answer(encoder, device, line)) + "\n").encode())
            except OSError:
                pass  # the caller gave up: its search has gone on without this answer
    finally:
        if asked:  # after the answer is sent, whatever became of the request
            released(log)


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
            serve(listener, encoder, device, log)
    except socket.timeout:
        os.unlink(path)  # no new caller reaches it; those already queued are answered
        listener.settimeout(0.2)
        try:
            while True:
                serve(listener, encoder, device, log)
        except OSError:
            pass
    note(log, "END", f"pid {os.getpid()} idle {idle:g} s")


if __name__ == "__main__":
    main(*sys.argv[1:5])
