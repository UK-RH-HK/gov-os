"""S7 with DEC-1067 (f)'s size bound (the review's S7-F4; the CTO's bound after the GPU trip of 2026-11-04 03:53):
every reranker request carries at most 16 texts **and at most 24,000 characters in total**; a pool of long chunks is
split into the fewest requests meeting both; a single chunk above the budget is read up to it; the order is the
unbatched one.

- **Ten long chunks:** ten notes, each one line of about 6,000 characters (so one chunk each), all answering the
  question: no request above 16 texts or 24,000 characters, in total and padded (its texts times its longest, as
  the engineer's bound counts it; every text the reranker is given counted whole, its path line too); the requests
  are the fewest that meet both, grouped longest first; the order is the unbatched one.
- **One chunk of 40,000 characters:** the reranker is given its first part, at most 24,000 characters, and no request
  goes above the budget.

The stand-in reranker keeps each request (one per call) and scores each text by a hash of it (no ties).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w2_32_driver as driver
import w2_32_support as s

CAP_TEXTS, CAP_CHARS = 16, 24_000
QUESTION = "Which ledger entries record the harbour quorum?"


def _long_line(index, chars):
    unit = f"the harbour quorum ledger entry {index:02d} records the tide and the quay; "
    return (unit * (chars // len(unit) + 1))[:chars] + "\n"


@pytest.fixture
def long_pool(tmp_path, needs_vectors, box):
    notes = {f"docs/ledger-{i:02d}.md": f"# Ledger {i:02d}\n\n" + _long_line(i, 6_000) for i in range(10)}
    project = s.plant(tmp_path / "pool", {**s.NOTES, **notes})
    box.built(project)
    return project


@pytest.fixture
def one_long(tmp_path, needs_vectors, box):
    project = s.plant(tmp_path / "one", {**s.NOTES, "docs/ledger-long.md": "# Ledger long\n\n" + _long_line(99, 40_000)})
    box.built(project)
    return project


def _requests(box):
    path = Path(box.workdir) / "rerank-calls.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


def _path_of(text):
    first = text.split("\n", 1)[0]
    return first[len("[path: "):-1] if first.startswith("[path: ") and first.endswith("]") else None


def _fewest(pool):
    """How many requests the pool takes under the padded bound (a request's texts times its longest text at most
    ``CAP_CHARS``, at most ``CAP_TEXTS`` texts), grouped longest first: each group opens with its longest text and
    takes the next while the bound holds; no grouping meets the bound with fewer.

    Rewrite-Reason: the padded bound groups requests by length (ties in the pool's order): the engineer's bound
    (b7085897) is the padded size, the requests grouped longest first; this counted the summed size in the order sent."""
    count, texts, longest = 0, 0, 0
    for size in sorted((len(text) for text in pool), reverse=True):
        if texts and (texts + 1 > CAP_TEXTS or (texts + 1) * longest > CAP_CHARS):
            count, texts, longest = count + 1, 0, 0
        texts, longest = texts + 1, max(longest, size)
    return count + (1 if texts else 0)


def _ask(box, project, op):
    spec = f"calls:{Path(box.workdir) / 'rerank-calls.jsonl'}"
    extra = {"limit": 30} if op == "fusion_search" else {"radius": 0}
    answer = s.result(box.call(op, root=str(project), query=QUESTION, reranker=spec, **extra))
    return answer, _requests(box)


def _within_both_bounds(requests):
    for number, request in enumerate(requests, 1):
        chars = sum(len(text) for text in request)
        padded = len(request) * max((len(text) for text in request), default=0)
        assert len(request) <= CAP_TEXTS, f"request {number} carries {len(request)} texts (DEC-1067 (f): at most 16)"
        assert chars <= CAP_CHARS, f"request {number} carries {chars} characters (S7-F4: at most {CAP_CHARS})"
        # Rewrite-Reason: the padded bound groups requests by length: the bound is the padded size (b7085897).
        assert padded <= CAP_CHARS, \
            f"request {number}'s padded size is {padded} characters ({len(request)} texts of up to " \
            f"{padded // max(len(request), 1)}): above {CAP_CHARS}"


@pytest.mark.parametrize("op", ["fusion_search", "retrieve"])
def test_a_pool_of_long_chunks_goes_in_the_fewest_requests_within_16_texts_and_24000_characters(
        long_pool, box, standin, op):
    answer, requests = _ask(box, long_pool, op)
    pool = [text for request in requests for text in request]
    assert sum(len(text) for text in pool) > CAP_CHARS, f"premise: the pool holds more than {CAP_CHARS} characters"
    assert sum(1 for text in pool if len(text) > 5_000) >= 4, "premise: the pool holds the long chunks"
    _within_both_bounds(requests)
    assert len(requests) == _fewest(pool), \
        f"{len(requests)} requests where {_fewest(pool)} meet both bounds: {[len(r) for r in requests]} texts, " \
        f"{[sum(map(len, r)) for r in requests]} characters"
    unbatched = []  # each path at its first place, as ``first_paths`` reads the hits (a long note is two chunks)
    for text in sorted(pool, key=driver.hashed_score, reverse=True):
        if _path_of(text) not in unbatched:
            unbatched.append(_path_of(text))
    hits = answer["hits"] if op == "fusion_search" else answer["evidence"]
    order = s.first_paths(hits, len(hits))
    assert order == unbatched[:len(order)], f"the order is not the unbatched one ({op}): {order[:6]} {unbatched[:6]}"


@pytest.mark.parametrize("op", ["fusion_search", "retrieve"])
def test_a_chunk_above_the_budget_is_read_up_to_it(one_long, box, standin, op):
    _, requests = _ask(box, one_long, op)
    _within_both_bounds(requests)
    given = [text for request in requests for text in request if _path_of(text) == "docs/ledger-long.md"
             and "entry 99" in text]
    assert given, "premise: the reranker was given the long chunk"
    for text in given:
        body = text.split("\n", 1)[1] if "\n" in text else ""
        assert len(text) <= CAP_CHARS, f"the long chunk was given whole ({len(text)} characters)"
        assert len(text) >= CAP_CHARS // 2, f"the long chunk was cut far below the budget ({len(text)} characters)"
        assert _long_line(99, 40_000).startswith(body.rstrip("\n")), "the reranker was not given the chunk's first part"
