"""DEC-1068, for re-pin window 4: the shared reranker releases the GPU memory a request used once it has answered.

The ticket's note (CTO, 2026-11-04): the service empties the PyTorch caching allocator's cache once it has answered a
request (after each request, or after each request whose padded size exceeds a named threshold), so its memory no
longer climbs to its highest peak and stays there; the client's padded request bound (W2-32, ``MAX_REQUEST_CHARS``)
stays; the service's memory after each request is reported in its log (``rerank.log``: the allocated and reserved
MiB). The CTO's brief adds: after a request that fails too; nothing else in the service's behaviour changes (the
socket, the answers, the idle end: the earlier cases of this suite hold those, and every answer here is checked).

How it is seen, with no GPU and no model: the stand-in ``torch.cuda`` (``standin/w2112_standin.py``) records each
``empty_cache`` with its process, when it began and ended, and the reserved MiB before and after; once the model is
on the stand-in GPU it reports ``memory_allocated`` as ``ALLOCATED_MIB`` and ``memory_reserved`` as ``RESERVED_MIB``,
plus ``REQUEST_MIB`` left in the cache by each scoring call until ``empty_cache`` gives it back. A release is an
``empty_cache`` in the service's process. The service is started by a search, as a session starts it; the requests
are then sent on its socket, one at a time, each a full request as the client sends one (16 texts, about 23,650 of
``MAX_REQUEST_CHARS``' 24,000 padded characters), so the cases hold whichever of the note's two rules is chosen: no
threshold that keeps a full request from being released serves the note's purpose.

Where the machine refuses ``socket(AF_UNIX)`` (the launch sandbox), these cases carry the box's Unix sockets over
loopback TCP (``standin/w2112_unix_over_tcp.py``), so they show red or green for the release itself; elsewhere the
product's own sockets are used, unchanged.
"""

from __future__ import annotations

import importlib.util
import re
import socket
import time
from pathlib import Path

import pytest

import w2_112_support as support
from w2_112_support import ask, query_of, score, scores_in


def _module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SHIM = _module(support.UNIX_OVER_TCP, "w2112_unix_over_tcp_here")
_STANDIN = _module(support.STANDIN, "w2112_standin_here")
ALLOCATED_MIB, RESERVED_MIB, REQUEST_MIB = _STANDIN.ALLOCATED_MIB, _STANDIN.RESERVED_MIB, _STANDIN.REQUEST_MIB

REQUESTS = 4             # N requests, one at a time
FULL_TEXTS = 16          # a full request: 16 pairs of about 1,478 characters (the client's bound is 24,000)
TEXT_CHARS = 1440
RELEASE_S = 10.0         # a request's release comes within this of its answer (it is due at once)
LOG_S = 5.0              # the log's lines are written within this of the last answer
HOLD_S = 3.0             # how long a release takes in the case that sees whether it holds the answer
LOG_REL = f"{support.CACHE_REL}/rerank.log"


# ---------------------------------------------------------------- helpers


def full_request(tag: str) -> tuple[str, list[str]]:
    """A query and 16 texts of its own (``tag`` in each), as large as a request the client sends."""
    query, texts = query_of(tag), []
    for number in range(FULL_TEXTS):
        head = f"[path: notes/{tag}-{number}.md]\nSession {tag}, passage {number}: the keeper's ledger. "
        filler = f"line {number} of the {tag} ledger holds the weight of the GPU's memory; "
        texts.append((head + filler * (TEXT_CHARS // len(filler) + 1))[:TEXT_CHARS])
    assert FULL_TEXTS * max(len(query) + len(text) for text in texts) <= 24_000, "the request is above the client's bound"
    return query, texts


def check_answer(answer, query: str, texts: list[str], who: str) -> None:
    """The service's answer is a private reranker's: one score per text, in the request's order, within rounding."""
    got = scores_in(answer, len(texts))
    assert got is not None, f"{who}: the service did not answer with one score per text: {answer!r}"[:800]
    for number, (value, text) in enumerate(zip(got, texts)):
        assert abs(value - score(query, text)) <= support.TOLERANCE, \
            (f"{who}: text {number} scored {value}, a private reranker scores it {score(query, text)}: the answers "
             "changed with the release")


def releases(box, pid: int) -> list[dict]:
    """The service's releases (``empty_cache`` in its process), in order."""
    return [record for record in box.events("empty-cache") if record["pid"] == pid]


def scoring(box, pid: int, query: str, kind: str) -> list[dict]:
    """The service's ``predict-begin`` or ``predict-end`` events for ``query``."""
    return [record for record in box.events(kind) if record["pid"] == pid and query in record.get("queries", [])]


def wait_for(condition, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return bool(condition())


def log_path(box) -> Path:
    return box.home / LOG_REL


def log_size(box) -> int:
    try:
        return log_path(box).stat().st_size
    except OSError:
        return 0


def settle_log(box, quiet: float = 0.5, longest: float = LOG_S) -> None:
    """Wait until ``rerank.log`` has not grown for ``quiet`` seconds (at most ``longest``)."""
    deadline, last, since = time.monotonic() + longest, log_size(box), time.monotonic()
    while time.monotonic() < deadline:
        time.sleep(0.05)
        now = log_size(box)
        if now != last:
            last, since = now, time.monotonic()
        elif time.monotonic() - since >= quiet:
            return


def log_lines_since(box, offset: int) -> list[str]:
    try:
        with open(log_path(box), "rb") as found:
            found.seek(offset)
            return found.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return []


def memory_lines(lines: list[str]) -> list[str]:
    """The lines that report the service's memory: they name its allocated and its reserved memory."""
    return [line for line in lines if re.search(r"alloc", line, re.I) and re.search(r"reserv", line, re.I)]


def carries(line: str, mib: int) -> bool:
    """Whether ``line`` gives ``mib`` (MiB, as a whole number or with decimals)."""
    return any(abs(float(number) - mib) <= 0.5 for number in re.findall(r"(?<![\d.])\d+(?:\.\d+)?", line))


def check_line(line: str, who: str) -> None:
    assert carries(line, ALLOCATED_MIB), \
        (f"{who}: the line does not give the allocated memory ({ALLOCATED_MIB} MiB, as the service's torch.cuda "
         f"reports it after the release): {line!r}")
    assert carries(line, RESERVED_MIB), \
        (f"{who}: the line does not give the reserved memory after the release ({RESERVED_MIB} MiB; "
         f"{RESERVED_MIB + REQUEST_MIB} MiB before it): {line!r}")


def released_after(box, pid: int, query: str, before: int, who: str) -> dict:
    """The first release after the ``before``-th, once ``query``'s scoring has ended: it must come within
    ``RELEASE_S`` and give the request's cache back."""
    came = wait_for(lambda: len(releases(box, pid)) > before, RELEASE_S)
    ended = scoring(box, pid, query, "predict-end")
    assert ended, f"{who}: the service's model never scored the request (no predict-end of {query!r})"
    assert came, \
        (f"{who}: no release of the GPU memory within {RELEASE_S:g} s of the answer: the service's process never "
         f"called torch.cuda.empty_cache, so the {REQUEST_MIB} MiB the request left in the allocator's cache stay "
         f"reserved ({RESERVED_MIB + REQUEST_MIB} MiB)")
    release = releases(box, pid)[before]
    assert release["began"] >= ended[-1]["time"] - 0.01, \
        f"{who}: the release began before the request's scoring ended, so it does not release what the request used"
    assert release["reserved_after_mib"] == RESERVED_MIB, \
        (f"{who}: after the release {release['reserved_after_mib']} MiB stay reserved, {RESERVED_MIB} MiB expected "
         "(the request's cache given back)")
    return release


@pytest.fixture()
def service(boxes, monkeypatch):
    """A box with room on the stand-in GPU and its service up (started by one search, which has settled)."""
    box = boxes(gpu=support.ROOM)
    if box.unix_over_tcp():  # the launch sandbox: this process reaches the service the same way
        monkeypatch.setattr(socket, "socket", _SHIM.OverTcp)
    pid = box.warm("mem-warm")
    wait_for(lambda: releases(box, pid), 2.0)  # the warm-up search's own release and log line, if any
    settle_log(box)
    return box, pid


# ---------------------------------------------------------------- the cases


def test_each_request_the_service_answers_is_followed_by_its_own_release_of_the_gpu_memory(service):
    """N requests give N releases, one after each answer and before the next request is scored; the answers are a
    private reranker's."""
    box, pid = service
    before, asked = len(releases(box, pid)), []
    for number in range(REQUESTS):
        query, texts = full_request(f"rel{number}")
        check_answer(ask(box.socket, query, texts, timeout=60), query, texts, f"request {number + 1}")
        released_after(box, pid, query, before + number, f"request {number + 1} of {REQUESTS}")
        asked.append(query)
    found = releases(box, pid)[before:]
    for number, query in enumerate(asked):
        ended = scoring(box, pid, query, "predict-end")[-1]["time"]
        following = scoring(box, pid, asked[number + 1], "predict-begin")[0]["time"] \
            if number + 1 < len(asked) else float("inf")
        own = [record for record in found if record["began"] >= ended - 0.01 and record["time"] <= following + 0.01]
        assert own, \
            (f"request {number + 1}: no release between the end of its scoring and the next request's: its memory "
             "was not given back before the next request")
    assert len(found) >= REQUESTS, f"{REQUESTS} requests gave {len(found)} releases"


def test_each_request_writes_one_line_to_rerank_log_with_the_allocated_and_reserved_mib(service):
    """N requests give N lines in ``~/.cache/gov-os/rerank.log``, each with the allocated and the reserved MiB as
    the service reads them after the request's release (they no longer climb)."""
    box, pid = service
    offset = log_size(box)
    for number in range(REQUESTS):
        query, texts = full_request(f"log{number}")
        check_answer(ask(box.socket, query, texts, timeout=60), query, texts, f"request {number + 1}")
    wait_for(lambda: len(memory_lines(log_lines_since(box, offset))) >= REQUESTS, LOG_S)
    settle_log(box)
    lines = memory_lines(log_lines_since(box, offset))
    assert len(lines) == REQUESTS, \
        (f"{REQUESTS} requests wrote {len(lines)} lines with the service's allocated and reserved memory to "
         f"{LOG_REL} (one per request expected); its new lines: {log_lines_since(box, offset)[-12:]}")
    for number, line in enumerate(lines):
        check_line(line, f"{LOG_REL}, request {number + 1}")


def test_a_request_that_fails_still_releases_its_gpu_memory_and_writes_its_line(service):
    """A request whose scoring fails is answered with an error and still released and logged; the next request is
    answered as before."""
    box, pid = service
    offset, before = log_size(box), len(releases(box, pid))
    box.for_pid(pid, predict_error=True)  # the service's model now fails while it scores
    query, texts = full_request("fail")
    answer = ask(box.socket, query, texts, timeout=60)
    assert scores_in(answer, len(texts)) is None, f"the planted failure did not fail the request: {answer!r}"[:600]
    assert any(record.get("error") for record in scoring(box, pid, query, "predict-end")), \
        "the service's model never failed on the request"
    released_after(box, pid, query, before, "the request that failed")
    box.for_pid(pid, predict_error=False)
    again, texts = full_request("after-fail")
    check_answer(ask(box.socket, again, texts, timeout=60), again, texts, "the request after the failed one")
    released_after(box, pid, again, before + 1, "the request after the failed one")
    wait_for(lambda: len(memory_lines(log_lines_since(box, offset))) >= 2, LOG_S)
    settle_log(box)
    lines = memory_lines(log_lines_since(box, offset))
    assert len(lines) == 2, \
        (f"the failed request and the next wrote {len(lines)} lines with the service's memory to {LOG_REL} (one "
         f"each expected); its new lines: {log_lines_since(box, offset)[-12:]}")
    for line, who in zip(lines, ("the request that failed", "the request after it")):
        check_line(line, f"{LOG_REL}, {who}")


def test_the_release_comes_after_the_answer_and_never_holds_it(service):
    """The answer is sent before the release: a release that takes 3 s does not delay the answer."""
    box, pid = service
    before = len(releases(box, pid))
    box.for_pid(pid, empty_cache_delay=HOLD_S)
    query, texts = full_request("hold")
    answer = ask(box.socket, query, texts, timeout=60)
    received = time.time()
    check_answer(answer, query, texts, "the request")
    wait_for(lambda: len(releases(box, pid)) > before, RELEASE_S + HOLD_S)
    release = released_after(box, pid, query, before, "the request")
    assert received < release["time"], \
        (f"the answer came {received - release['began']:.1f} s after the release began, only once the "
         f"{HOLD_S:g} s release had ended: the release held the answer (it is due once the service has answered)")
