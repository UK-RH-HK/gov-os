"""Builder tests for the default reranker's processes (W1-19; DEC-397, DEC-374; W2-145, DEC-1048 (5)).

Regression evidence only (DEC-136). No model is loaded: a fake interpreter stands in a temporary ``HOME`` at the
path of the reranker environment's. It records every start (its arguments and ``HF_HUB_OFFLINE``) and would answer
as the old private worker did, scoring a text by its length. DEC-1048 (5): with the shared service not answering,
it is never started; the search keeps the order given, named.
"""
from __future__ import annotations

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


def _no_service(*_args):
    raise ConnectionError("the shared service is not under test here")


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("HF_HUB_OFFLINE", "0")
    # W2-112: every search asks the shared service first; here it does not answer (W2-145: no private fallback).
    monkeypatch.setattr(rerank, "_ask", _no_service)
    yield tmp_path


def _interpreter(home, loads):
    path = home / rerank.PYTHON_REL
    path.parent.mkdir(parents=True)
    path.write_text(FAKE.format(loads=loads), encoding="utf-8")
    path.chmod(0o755)
    return path


@pytest.mark.parametrize("loads", [True, False], ids=["a worker that would load", "a worker that would end"])
def test_without_the_service_no_private_process_is_ever_started(home, loads):
    # DEC-1048 (5): formerly "the process is started once offline and scores every text" and "a process that ends
    # without the model leaves the order given"; now no process is started, whatever it would do
    _interpreter(home, loads=loads)
    for question in ("a question", "another"):
        ranked = rerank.rerank(question, CANDIDATES)
        assert ranked == CANDIDATES and not any("rerank_score" in entry for entry in ranked)
        outcome = rerank.last_outcome()
        assert outcome["by"] == "unavailable" and "the shared service is not under test here" in outcome["reason"]
    assert not (home / "started").exists()  # never started
    assert not hasattr(rerank, "_started")


def test_with_no_environment_nothing_is_started(home):
    assert rerank.default_reranker() is None
    assert rerank.rerank("a question", CANDIDATES) == CANDIDATES
