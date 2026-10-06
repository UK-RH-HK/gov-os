"""Builder tests for how the default reranker's process is started and spoken to (W1-19; DEC-397, DEC-374).

Regression evidence only (DEC-136). No model is loaded: a fake interpreter stands in a temporary ``HOME`` at the
path of the reranker environment's. It records its arguments and ``HF_HUB_OFFLINE``, then answers as the worker
does, scoring a text by its length.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import rerank  # noqa: E402

FAKE = """#!/usr/bin/python3
import json, os, sys
with open(os.path.join(os.environ["HOME"], "started"), "a") as record:
    record.write(json.dumps([sys.argv[1:], os.environ.get("HF_HUB_OFFLINE")]) + "\\n")
if {loads}:
    print("true", flush=True)
    for line in sys.stdin:
        print(json.dumps([float(len(text)) for text in json.loads(line)[1]]), flush=True)
"""
CANDIDATES = [{"chunk_id": "short", "text": "ab"}, {"chunk_id": "long", "text": "abcdef"}]


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("HF_HUB_OFFLINE", "0")
    rerank._started.cache_clear()
    yield tmp_path
    rerank._started.cache_clear()


def _interpreter(home, loads):
    path = home / rerank.PYTHON_REL
    path.parent.mkdir(parents=True)
    path.write_text(FAKE.format(loads=loads), encoding="utf-8")
    path.chmod(0o755)
    return path


def test_the_process_is_started_once_offline_and_scores_every_text(home):
    _interpreter(home, loads=True)
    first = rerank.rerank("a question", CANDIDATES)
    second = rerank.rerank("another", CANDIDATES)
    assert [(entry["chunk_id"], entry["rerank_score"]) for entry in first] == [("long", 6.0), ("short", 2.0)]
    assert second == first
    started = [json.loads(line) for line in (home / "started").read_text().splitlines()]
    worker = str(Path(rerank.__file__).with_name("rerank_worker.py"))
    assert started == [[["-I", worker, rerank.MODEL, rerank.REVISION], "1"]]


def test_a_process_that_ends_without_the_model_leaves_the_order_given(home):
    _interpreter(home, loads=False)
    assert rerank.rerank("a question", CANDIDATES) == CANDIDATES
    assert rerank.rerank("another", CANDIDATES) == CANDIDATES
    assert len((home / "started").read_text().splitlines()) == 1  # it is not started again for each question


def test_with_no_environment_nothing_is_started(home):
    assert rerank.default_reranker() is None
    assert rerank.rerank("a question", CANDIDATES) == CANDIDATES
