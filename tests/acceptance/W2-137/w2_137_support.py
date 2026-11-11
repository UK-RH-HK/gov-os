"""Shared stand-ins and the oracle for W2-137's acceptance tests (DAEO-5emz; DEC-1090 (2)).

No model, no GPU, no socket: the encoder is a deterministic stand-in, the service is driven in this process through
``rerank_service.answer`` and ``rerank_service.serve`` (W2-112's seam), and the expected request shapes are computed
here from the ticket's words alone (the padded size of a request is its count times its longest pair,
``len(query) + len(text)``), never from the code under test.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

# The question every case asks: its length enters every padded size.
QUERY = "which request cap does the shared reranker keep?"
# The bound the ticket keeps (S1: "the bound on padded characters per request (MAX_REQUEST_CHARS) stays").
TICKET_CHARS = 24_000
# The count cap on integrate before this ticket (DEC-1067 (f)), the reference S3 compares against.
OLD_CAP = 16
MEMORY_DETAIL = r"allocated \d+ MiB, reserved \d+ MiB"


def depth() -> int:
    """The pool's rerank_depth in this repository's retrieval.yaml (the ticket's 40)."""
    from gov.retrieval import pool

    return pool.settings(REPO)["rerank_depth"]


def padded(query: str, texts: list[str]) -> int:
    return len(texts) * max(len(query) + len(text) for text in texts) if texts else 0


def per_request(query: str, length: int, bound: int = TICKET_CHARS) -> int:
    """How many texts of ``length`` characters fit one request under the padded bound alone (no count cap)."""
    return max(1, bound // (len(query) + length))


def expected_requests(count: int, query: str, length: int, bound: int = TICKET_CHARS) -> int:
    return math.ceil(count / per_request(query, length, bound))


def texts_of(count: int, length: int, tag: str = "t") -> list[str]:
    """``count`` distinct texts of exactly ``length`` characters (distinct so each has its own score)."""
    out = []
    for number in range(count):
        head = f"{tag}{number:03d} "
        out.append((head + "abcdefghij" * (length // 10 + 2))[:length])
    return out


def check_requests(query: str, texts: list[str], out, cap: int, bound: int) -> None:
    """Fails unless ``out`` (``rerank.requests``' answer) sends every text once, each read up to the bound at most,
    and every request within ``cap`` texts and ``bound`` padded characters."""
    seen = sorted(index for indices, _ in out for index in indices)
    assert seen == list(range(len(texts))), f"every text in exactly one request: {seen}"
    room = max(0, bound - len(query))
    for number, (indices, sent) in enumerate(out):
        assert len(indices) == len(sent) and 0 < len(sent) <= cap, f"request {number}: {len(sent)} texts, cap {cap}"
        for index, text in zip(indices, sent):
            assert text == texts[index][:room], f"request {number}: text {index} is not its own text read up to {room}"
        assert padded(query, sent) <= bound, f"request {number}: padded {padded(query, sent)} over {bound}"


# --- the stand-in encoder: deterministic, with a padded model's small batch dependence -------------------------

def base_score(query: str, text: str) -> float:
    """A pair's score, from its digest alone: in [0, 1000), in steps of 0.001."""
    digest = hashlib.sha256(f"{query}\0{text}".encode()).hexdigest()
    return int(digest[:12], 16) % 1_000_000 / 1000


class Encoder:
    """A stand-in cross-encoder (``predict(pairs)``, as ``rerank_worker.scores`` calls it).

    Each pair's score is ``base_score`` plus under 1e-5 that depends on the batch it is padded into (the longest pair
    of the batch), as a real reranker's padded batch moves its scores slightly. So scores sent in one request and in
    requests of 16 differ, by less than the ticket's 1e-3."""

    def __init__(self, events: list | None = None):
        self.events = events if events is not None else []
        self.batches: list[int] = []

    def predict(self, pairs):
        self.events.append("predict")
        self.batches.append(len(pairs))
        longest = max((len(q) + len(t) for q, t in pairs), default=0)
        return [base_score(q, t) + 1e-5 * (longest - len(q) - len(t)) / TICKET_CHARS for q, t in pairs]


def via_service(encoder, calls: list):
    """A reranker loader whose every request goes through the service's own request handling
    (``rerank_service.answer``), as JSON both ways, the texts of each request recorded in ``calls``."""
    from gov.retrieval import rerank_service

    def score(query: str, texts: list[str]):
        calls.append(list(texts))
        line = (json.dumps([query, texts]) + "\n").encode()
        answer = json.loads(json.dumps(rerank_service.answer(encoder, "cuda:0", line)))
        assert "error" not in answer, answer
        return answer["scores"]

    return lambda: score


def recording(calls: list):
    """A reranker loader that records each request's texts and scores by ``base_score``."""
    def score(query: str, texts: list[str]):
        calls.append(list(texts))
        return [base_score(query, text) for text in texts]

    return lambda: score


# --- W2-112's in-process seam for ``rerank_service.serve`` ------------------------------------------------------

class Torch:
    """A stand-in torch, put in ``sys.modules``: each allocator call is an event."""

    def __init__(self, events: list):
        self.cuda, self.events = self, events

    def empty_cache(self):
        self.events.append("release")

    def memory_allocated(self):
        return 1200 * 2 ** 20

    def memory_reserved(self):
        return 1300 * 2 ** 20


class Connection:
    def __init__(self, events: list, line: bytes):
        self.events, self.line = events, line

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.events.append("closed")

    def settimeout(self, _):
        pass

    def makefile(self, _):
        return io.BytesIO(self.line)

    def sendall(self, data: bytes):
        self.events.append(("sent", json.loads(data)))


class Listener:
    def __init__(self, connection):
        self.connection = connection

    def accept(self):
        return self.connection, None
