"""One W2-145 search, in a process of its own (the tests run it; nothing imports it).

``python3 w2_145_session.py <request.json> <result.json>``. The request names the mode:

- ``"rerank"`` (default): ``gov.retrieval.rerank.rerank(query, candidates)`` with no reranker given, as a search
  calls it, then ``last_outcome()``;
- ``"retrieve"``: ``gov.retrieval.retrieve.retrieve(root, query)``, the bundle.

The result holds the answer, the outcome, the search's own start and end (``time.time()``, around the call alone;
and ``time.monotonic()`` as ``t0`` and ``t1``: this machine's wall clock steps by seconds, and a step is not the
search's time), the time this thread spent waiting for a CPU during the call (``queued``, seconds, from the kernel's
run-queue account ``/proc/thread-self/schedstat``; 0.0 where that file cannot be read), any exception, and which of
the model's libraries this process holds afterwards (``torch``, ``sentence_transformers``, ``transformers``: none may
be loaded in the calling process, S1). Nothing is read from a pipe, so a service it starts cannot hold it open.
"""

import json
import os
import sys
import time
import traceback
from pathlib import Path

HEAVY = ("torch", "sentence_transformers", "transformers")
request = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
destination = Path(sys.argv[2])
out = {"pid": os.getpid(), "error": None, "result": None, "outcome": None}


def queued_ns():
    """This thread's total run-queue wait in nanoseconds (the second field of schedstat), or None where unreadable.
    It is time the process was ready to run and had no CPU: the machine's queue, not the code's own time (W2-145:
    a search is judged by its own time, never by how long a loaded machine kept it waiting)."""
    for name in ("/proc/thread-self/schedstat", "/proc/self/schedstat"):
        try:
            return int(Path(name).read_text(encoding="ascii").split()[1])
        except (OSError, ValueError, IndexError):
            continue
    return None


def failure(error):
    return {"type": type(error).__name__, "message": str(error), "trace": traceback.format_exc()}


def finish():
    out["heavy"] = sorted(name for name in sys.modules if name.split(".")[0] in HEAVY)
    partial = destination.with_name(destination.name + ".part")
    partial.write_text(json.dumps(out, default=repr), encoding="utf-8")
    os.replace(partial, destination)


mode = request.get("mode", "rerank")
try:
    from gov.retrieval import rerank

    if mode == "retrieve":
        from gov.retrieval import retrieve
    out["module"] = rerank.__file__
except BaseException as error:  # noqa: BLE001 - reported, not raised
    out["error"] = failure(error)
    finish()
    sys.exit(0)

queued_before = queued_ns()
out["t0"] = time.monotonic()
out["started"] = time.time()
try:
    if mode == "retrieve":
        out["result"] = retrieve.retrieve(request["root"], request["query"])
    else:
        out["result"] = rerank.rerank(request["query"], request["candidates"])
except BaseException as error:  # noqa: BLE001 - a search that raises is what the tests look for
    out["error"] = failure(error)
out["ended"] = time.time()
out["t1"] = time.monotonic()
queued_after = queued_ns()
out["queued"] = (max(0.0, (queued_after - queued_before) / 1e9)
                 if queued_before is not None and queued_after is not None else 0.0)
try:
    out["outcome"] = rerank.last_outcome()
except BaseException as error:  # noqa: BLE001
    out["outcome_error"] = failure(error)
finish()
