"""The shared reranker: one process per user serves every session's searches (W2-112; DEC-979 item 4, DEC-1032).

Started by ``gov.retrieval.rerank`` with the reranker environment's interpreter, never imported by it:
``python -I rerank_service.py MODEL REVISION SOCKET LOCK_FD``. ``LOCK_FD`` is the start lock (``rerank.lock`` beside
the socket), taken by the search that started it and held by this process for its life, so no second service starts
while it lives. The same pinned model and the same model call as ``rerank_worker.py`` (``load`` and ``scores``).

- **Device (DEC-1032):** before the model loads, the GPU's free memory is read with the library that will hold it
  (``torch.cuda.mem_get_info``). Less than its share plus the headroom free, or no GPU to read: it loads on the CPU,
  says so in its ready line and every answer, and writes an ALERT line to ``rerank.log``.
- **The GPU slots:** this is not ``rerank_worker.py``, so the interim module ``gov_reranker_gpu_slot`` leaves it
  untouched and it takes no slot; its own free-memory check and the single-service lock bound its GPU use.
- **Requests:** one connection per request, answered first come, first served, one request at a time (no batching
  across callers, so every answer is a private reranker's): ``[query, [text, …]]`` in, one JSON line out,
  ``{"scores": […], "device": …}`` or ``{"error": …, "device": …}``. More than ``MAX_TEXTS`` texts is refused.
- **Idle end:** with no request for ``GOV_RERANK_IDLE_S`` seconds (default 900) it removes its socket, answers what
  was already queued, and ends.
"""

import importlib.util
import json
import os
import socket
import sys
import time

# The worker's model call, by its file: this folder is never put on the path (its modules would shadow libraries).
_spec = importlib.util.spec_from_file_location("rerank_worker", os.path.join(os.path.dirname(__file__),
                                                                              "rerank_worker.py"))
_worker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_worker)
load, scores = _worker.load, _worker.scores

GIB = 2 ** 30
SHARE, HEADROOM = 3.5 * GIB, 2.0 * GIB  # DEC-1032: the reranker's share (2.5 to 3.5 GB, the top taken), 2 GB spare
MAX_TEXTS = 512  # a search sends at most (rounds + 1) x batch size candidates: 90 at the defaults
READ_S = 10.0  # a caller sends its request as soon as it connects


def _free_gpu() -> int:
    import torch

    return torch.cuda.mem_get_info()[0]


def choose_device(free=_free_gpu):
    """``("cuda", None)`` when the GPU has the share and the headroom free, else ``("cpu", why)``."""
    try:
        left = free()
    except Exception as error:  # no GPU, no CUDA, no torch: nothing to read
        return "cpu", f"the GPU's free memory could not be read ({type(error).__name__}: {error})"
    if left < SHARE + HEADROOM:
        return "cpu", f"the GPU has {left / GIB:.1f} GiB free, under the {(SHARE + HEADROOM) / GIB:.1f} GiB needed"
    return "cuda", None


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
    device, why = choose_device()
    if why:
        note(log, "ALERT", f"the shared reranker runs on the CPU: {why}")
    encoder = load(model, revision, device)
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    mask = os.umask(0o177)
    try:
        listener.bind(path)  # created 0600: the user's alone
    finally:
        os.umask(mask)
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
