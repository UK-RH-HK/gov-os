"""The one rerank over the merged candidate set (W1-19; DEC-379, DEC-374; ADR-0002 §2).

A reranker is given as its loader: a function without arguments that returns ``score(query, texts)``, one number
per text, higher is better (or None for "not scored"). The loader is called at the first rerank and not before, so
nothing of a model is loaded by importing this module or by a retrieval that has nothing to rerank. A loader that
returns None says the reranker cannot be loaded: the order given is kept and no candidate carries a score.

The default reranker (W2-112; DEC-979 item 4, DEC-1032, DEC-1033) asks the user's one shared reranker service
(``rerank_service.py``, on ``~/.cache/gov-os/rerank.sock``), starting it under ``rerank.lock`` when none listens.
No private reranker runs beside it (W2-145; DEC-1048 (5), DEC-1046 (1)): a client cannot tell a service that is down
from one it cannot reach, so when the service cannot be reached, started, or does not answer, in any way, the search
keeps the order given, unranked and named, at once (no second wait, no other process, no model in this process, on
the GPU or the CPU). Each such search is one FALLBACK line in ``~/.cache/gov-os/rerank.log`` (the service's failure,
then ``unranked``); ``last_outcome`` names who answered.
"""

from __future__ import annotations

import fcntl
import json
import os
import socket
import subprocess
import threading
import time
from pathlib import Path

# The pins of ADR-0002 §2; the index manifest records them.
MODEL = "Qwen/Qwen3-Reranker-0.6B"
REVISION = "e61197ed45024b0ed8a2d74b80b4d909f1255473"
# The interpreter of the reranker environment, under the home folder (DEC-397).
PYTHON_REL = ".local/share/gov-os/reranker-venv/bin/python"
_SERVICE = Path(__file__).with_name("rerank_service.py")
CACHE_REL = ".cache/gov-os"  # the socket, its start lock and the logs, in the user's own folder (0700)
SOCKET, LOCK, LOG, SERVICE_LOG = "rerank.sock", "rerank.lock", "rerank.log", "rerank-service.log"
CONNECT_S = 2.0  # to connect and be accepted (DEC-1034 T3); the answer is bounded by GOV_RERANK_TIMEOUT_S
START_S = 60.0  # the bound on a search's wait while the service starts and loads its model
# The most texts one request to a reranker carries (DEC-1067 (f), raised by DEC-1090 (2), W2-137). It was 16 when
# requests of 100 whole chunks held the shared reranker at 15.75 GB (PyTorch kept its peak). Since W2-112's release
# (DEC-1068) the service empties its GPU cache after every request, and a request's memory is set by its padded size,
# which ``MAX_REQUEST_CHARS`` bounds whatever the count. So the count only has to let a search's candidates go in one
# request when they are short: 64 holds the pool's ``rerank_depth`` (40) and a pool as deep as the routes (60), and
# stays far under the service's own bound (``rerank_service.MAX_TEXTS``, 512).
MAX_REQUEST_TEXTS = 64
# And the most characters one request carries, padded (the CTO's bound after the GPU backstop of 2026-11-04 03:53 and
# 05:37: the reranker pads every pair of a batch to the longest, so one 23,000-character chunk with 15 short ones is a
# batch of 16 x 23,000). Counted as the service scores, by pair (each text with the question): a request's size is its
# count times its longest pair, ``count * max(len(query) + len(text))``; the model's own fixed instruction (about 80
# characters a pair) is not counted and sits in the margin.
MAX_REQUEST_CHARS = 24_000
_ENDED = {75: "no GPU slot freed within its wait", 76: "the GPU is hidden from it", 70: "its GPU slot check failed",
          77: "the GPU has too little free memory for its share", 78: "no GPU is available to it"}
_last = threading.local()


def _cache() -> Path:
    return Path(os.environ.get("HOME") or Path.home()) / CACHE_REL


def _note(by: str, device, reason) -> None:
    _last.outcome = {"by": by, "device": device, "reason": reason}


def last_outcome() -> dict:
    """This thread's last rerank: ``by`` is ``service``, ``given`` or ``unavailable`` (the order kept), never
    ``private`` (W2-145), with the device that scored and the reason the order was kept."""
    return dict(getattr(_last, "outcome", {"by": "unavailable", "device": None, "reason": "no rerank was asked"}))


def _log(kind: str, detail: str) -> None:
    try:
        with open(_cache() / LOG, "a", encoding="utf-8") as out:
            out.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')}\t{kind}\t{detail}\n")
    except OSError:
        pass  # a session that cannot write there still searches


def status() -> dict:
    """What ``gov status`` shows: the searches that fell back and the service's refusals to start, from the log."""
    path = _cache() / LOG
    try:
        kinds = [line.split("\t")[1] for line in path.read_text(encoding="utf-8").splitlines() if "\t" in line]
    except FileNotFoundError:
        kinds = []
    return {"fallbacks": kinds.count("FALLBACK"), "service_refusals": kinds.count("REFUSED"), "log": str(path)}


def fallback_count() -> int:
    return status()["fallbacks"]


def _refusal(folder: Path) -> str:
    """The detail of the last REFUSED line the service wrote in ``rerank.log``, or the log's name."""
    try:
        lines = (folder / LOG).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        lines = []
    refused = [line.split("\t", 2)[2] for line in lines if line.count("\t") >= 2 and line.split("\t")[1] == "REFUSED"]
    return refused[-1] if refused else LOG


def _start(folder: Path, interpreter: str, path: str, waited: bool):
    """The service just started, or None when the start lock is held (another search starting it, or it runs).
    A search that ``waited`` for a service which then ended without listening does not start another: it goes on
    unranked (that service's refusal, a missing slot or GPU memory, holds for this search too)."""
    fd = os.open(folder / LOCK, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return None
        if waited:
            raise ConnectionError(f"the service this search waited for ended before it listened ({_refusal(folder)})")
        if os.path.lexists(path):
            os.unlink(path)  # a dead service's socket: a live service holds the lock
        env = {key: value for key, value in os.environ.items() if key != "GOV_RERANK_GPU_SLOT"}
        with open(folder / SERVICE_LOG, "ab") as log:  # the lock passes to the service, which holds it for its life
            return subprocess.Popen([interpreter, "-I", str(_SERVICE), MODEL, REVISION, path, str(fd)],
                                    env={**env, "HF_HUB_OFFLINE": "1"}, stdin=subprocess.DEVNULL, stdout=log,
                                    stderr=log, pass_fds=(fd,), start_new_session=True)
    finally:
        os.close(fd)


def _connect(interpreter: str) -> socket.socket:
    """A connection to the service, starting it when none listens; raises when it cannot be had within the bounds."""
    folder = _cache()
    folder.mkdir(parents=True, exist_ok=True)
    folder.chmod(0o700)
    path, deadline, started, waited = str(folder / SOCKET), time.monotonic() + START_S, None, False
    while True:
        connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)  # a sandbox refuses this at once (EPERM)
        connection.settimeout(CONNECT_S)
        try:
            connection.connect(path)
            return connection
        except (FileNotFoundError, ConnectionRefusedError):
            connection.close()
        except BaseException:
            connection.close()
            raise
        if started is not None and started.poll() is not None:
            code = started.returncode
            raise ConnectionError(f"the service ended before it listened ({_ENDED.get(code, f'exit {code}')})")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"the service did not listen within {START_S:g} s")
        if started is None:
            started = _start(folder, interpreter, path, waited)
            waited = started is None
        time.sleep(0.05)


def _ask(interpreter: str, query: str, texts: list[str]):
    """The service's scores for ``texts`` and its device; raises naming why there are none."""
    with _connect(interpreter) as connection:
        connection.settimeout(float(os.environ.get("GOV_RERANK_TIMEOUT_S", "30")))
        connection.sendall((json.dumps([query, texts]) + "\n").encode())
        line = connection.makefile("rb").readline()
    if not line:
        raise ConnectionError("the service closed the connection without an answer")
    answer = json.loads(line)
    if "error" in answer:
        raise RuntimeError(f"the service refused the request: {answer['error']}")
    if len(answer["scores"]) != len(texts):
        raise ValueError("the service's answer does not match the request")
    return answer["scores"], answer["device"]


def default_reranker():
    """The loader of the pinned reranker, which runs in its own pinned process (ADR-0002 §2): the shared service
    alone, started from ``~/.local/share/gov-os/reranker-venv`` (DEC-397), ``~`` being the folder ``HOME`` names.
    None when the environment is absent (DEC-374).

    The scorer returns None when the service does not answer, in any way (DEC-1048 (5)): the search keeps the order
    given, ``last_outcome`` is ``unavailable`` with the service's failure, and one FALLBACK line is logged. Nothing
    else is started and nothing is waited for (W2-145 S1, S4)."""
    interpreter = Path(os.environ.get("HOME") or Path.home()) / PYTHON_REL
    if not interpreter.is_file():
        _note("unavailable", None, f"no reranker environment at {interpreter}")
        return None

    def score(query: str, texts: list[str]):
        try:
            values, device = _ask(str(interpreter), query, texts)
        except Exception as error:  # the service unreachable, in any way: this search goes on unranked, never fails
            why = f"the shared reranker did not answer ({type(error).__name__}: {error})"
            _log("FALLBACK", f"{why}\tunranked")
            _note("unavailable", None, why)
            return None
        _note("service", device, None)
        return values

    return score


def requests(query: str, texts: list[str]) -> list[tuple[list[int], list[str]]]:
    """The fewest requests, each of at most ``MAX_REQUEST_TEXTS`` texts and of at most ``MAX_REQUEST_CHARS`` padded
    characters (its count times its longest pair, ``len(query) + len(text)``): ``(indices, texts)``, the indices into
    ``texts``. The texts are grouped longest first: each request takes the longest left and as many of the next
    longest as fit, which is the fewest (a request's size is set by its longest text). A text whose pair alone is
    above the budget is read up to it, as a chunk is read up to ``fusion.RERANK_LIMIT_CHARS``."""
    room = max(0, MAX_REQUEST_CHARS - len(query))
    sent = [text[:room] for text in texts]
    order = sorted(range(len(sent)), key=lambda index: -len(sent[index]))  # longest first, ties in the order given
    out, at = [], 0
    while at < len(order):
        longest = len(query) + len(sent[order[at]])
        fits = max(1, min(MAX_REQUEST_TEXTS, MAX_REQUEST_CHARS // max(1, longest)))
        group = sorted(order[at:at + fits])
        out.append((group, [sent[index] for index in group]))
        at += fits
    return out


def rerank(query: str, candidates: list[dict], reranker=None) -> list[dict]:
    """``candidates`` in the order of the reranker's scores, each with ``rerank_score``; equal scores keep the order
    given. ``score`` is called with the ``text`` of the candidates in requests of at most ``MAX_REQUEST_TEXTS`` (64,
    DEC-1090 (2)) and at most ``MAX_REQUEST_CHARS`` padded characters (``requests``): no request to any reranker,
    the shared service or one given, carries more. Each score goes back to its candidate, so the order is the
    unbatched one;
    one request that scores nothing or fails leaves every candidate unscored. Without a reranker the candidates are
    returned as given.

    A reranker that fails once loaded (W2-32 S4, W2-M104: it died, closed its pipe, answered garbage or the wrong
    number of scores) is reported, not raised: the candidates come back in the order given, with no score, and
    ``last_outcome`` says ``unavailable`` with the failure named. So does a loader that raises."""
    candidates = [dict(candidate) for candidate in candidates]
    _note("unavailable", None, "nothing to rerank" if not candidates else "the reranker given could not be loaded")
    try:
        score = (reranker or default_reranker)() if candidates else None
    except Exception as error:
        _note("unavailable", None, f"the reranker could not be loaded ({type(error).__name__}: {error})")
        return candidates
    if score is None:
        return candidates
    if reranker is not None:
        _note("given", None, None)
    try:
        scores: list = [None] * len(candidates)
        for indices, batch in requests(query, [candidate["text"] for candidate in candidates]):
            values = score(query, batch)
            if values is None:
                if reranker is not None:
                    _note("unavailable", None, "the reranker given scored nothing: the order given is kept")
                return candidates
            values = [float(value) for value in values]
            if len(values) != len(batch):
                raise ValueError(f"{len(values)} scores for {len(batch)} texts")
            for index, value in zip(indices, values):  # each score back in its place: the unbatched order
                scores[index] = value
        ranked = sorted(zip(scores, candidates, strict=True), key=lambda pair: -pair[0])
    except Exception as error:
        _note("unavailable", None, f"the reranker failed after loading ({type(error).__name__}: {error}): "
                                   f"the order given is kept")
        return candidates
    return [{**candidate, "rerank_score": value} for value, candidate in ranked]
