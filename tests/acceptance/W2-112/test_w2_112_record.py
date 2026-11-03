"""KPI success 5 and the measured half of KPI 6: the measurements are recorded (DEC-979 item 4, CAPACITY-1, DEC-1032).

"Measured, in docs/research/W2-112-shared-reranker.md: memory with 10 concurrent searches before and after (today up
to 9 rerankers, 9.4 GiB at peak), and the searches' times"; and "measured: the GPU's memory with the embedder and
the service under 20 concurrent searches". The figures are measured with the real model by the engineer; a test
cannot remake them. These cases hold only that the record exists in the worktree under test and carries figures of
each kind; whether the figures are right is the reviewer's and the auditor's.
"""

from __future__ import annotations

import re

import w2_112_support as support

RECORD_REL = "docs/research/W2-112-shared-reranker.md"
MEMORY = re.compile(r"\d+(?:[.,]\d+)?\s*(?:GiB|GB|MiB|MB)\b")
TIME = re.compile(r"\d+(?:[.,]\d+)?\s*(?:ms|s|seconds?)\b")


def _record() -> str:
    path = support.REPO_ROOT / RECORD_REL
    assert path.is_file(), f"there is no {RECORD_REL}: the KPI's measurements are recorded there"
    return path.read_text(encoding="utf-8")


def test_the_record_gives_memory_before_and_after_with_10_concurrent_searches_and_their_times():
    text = _record()
    assert re.search(r"\b10\b[^\n]{0,80}concurren|concurren[^\n]{0,80}\b10\b", text, re.IGNORECASE), \
        "the record does not name the measurement with 10 concurrent searches"
    assert re.search(r"\bbefore\b", text, re.IGNORECASE) and re.search(r"\bafter\b", text, re.IGNORECASE), \
        "the record does not give the memory before and after"
    assert len(MEMORY.findall(text)) >= 2, "the record gives fewer than two memory figures (before and after)"
    assert TIME.search(text), "the record gives no time for the searches"


def test_the_record_gives_the_gpus_memory_with_the_embedder_and_the_service_under_20_concurrent_searches():
    text = _record()
    assert re.search(r"\bGPU\b", text), "the record does not mention the GPU"
    assert re.search(r"\b20\b[^\n]{0,80}concurren|concurren[^\n]{0,80}\b20\b", text, re.IGNORECASE), \
        "the record does not name the measurement under 20 concurrent searches"
    assert re.search(r"embedd", text, re.IGNORECASE), "the record does not give the GPU's memory with the embedder"
