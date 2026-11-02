"""One session's search, in a process of its own (the W2-112 acceptance tests run it; nothing imports it).

``python3 w2_112_session.py <request.json> <result.json>``. The request names what to do:

- ``"rerank"`` (default): ``gov.retrieval.rerank.rerank(query, candidates)`` with no reranker given, as a search
  does; with ``"private"``, also the same call with a private, in-process reranker of the stand-in model, as the
  reference a private reranker gives on the same inputs;
- ``"retrieve"``: ``gov.retrieval.retrieve.retrieve(root, query)``, the bundle.

With ``"barrier"`` it imports first, says it is ready, and waits for the go file, so that many sessions call at
once. The result (and every ``logging`` record of the process) is written to ``result.json``; the process's own
standard output stays out of it, and nothing is read from a pipe, so a service it starts cannot hold it open.
"""

import json
import logging
import os
import sys
import time
import traceback
from pathlib import Path

request = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
destination = Path(sys.argv[2])
records = []


class Keep(logging.Handler):
    def emit(self, record):
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001 - a record that cannot format is still a record
            message = str(record.msg)
        records.append({"logger": record.name, "level": record.levelname, "message": message})


logging.getLogger().addHandler(Keep())
logging.getLogger().setLevel(logging.DEBUG)
out = {"pid": os.getpid(), "error": None, "result": None, "private": None, "records": records}


def failure(error):
    return {"type": type(error).__name__, "message": str(error), "trace": traceback.format_exc()}


def finish():
    partial = destination.with_name(destination.name + ".part")
    partial.write_text(json.dumps(out, default=repr), encoding="utf-8")
    os.replace(partial, destination)


try:
    if request.get("mode", "rerank") == "retrieve":
        from gov.retrieval import retrieve as module
    else:
        from gov.retrieval import rerank as module
    out["module"] = module.__file__
except BaseException as error:  # noqa: BLE001 - reported, not raised
    out["error"] = failure(error)
    finish()
    sys.exit(0)

barrier = request.get("barrier")
if barrier:
    Path(f"{barrier}.ready-{os.getpid()}").touch()
    deadline = time.monotonic() + 120
    while not Path(f"{barrier}.go").exists() and time.monotonic() < deadline:
        time.sleep(0.005)

out["started"] = time.time()
try:
    if request.get("mode", "rerank") == "retrieve":
        out["result"] = module.retrieve(request["root"], request["query"])
    else:
        out["result"] = module.rerank(request["query"], request["candidates"])
except BaseException as error:  # noqa: BLE001 - a search that raises is what the tests look for
    out["error"] = failure(error)
out["ended"] = time.time()

if request.get("private"):
    sys.path.insert(0, request["private"])
    try:
        import w2112_standin

        out["private"] = module.rerank(request["query"], request["candidates"],
                                       reranker=lambda: w2112_standin.scores)
    except BaseException as error:  # noqa: BLE001
        out["private_error"] = failure(error)
finish()
