"""W2-32 S7 (DEC-1067, P-W2-32-8): ``gov rebuild``'s result names the chunks the embedder's limit cut, copied from
``semantic.refresh``'s report, as ``stores.semantic.cut``. Regression evidence only (DEC-136): every store a rebuild
builds is a stand-in, as in ``tests/unit/rebuild/test_no_embeddings.py``; no model is started.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.rebuild.command import add_arguments, run  # noqa: E402

EMBEDDED = {"path-map.yaml": {"namespaces": {"all": {"paths": ["**"], "embedding_policy": "embedded"}}}}
CUT = {"limit": 10_000, "count": 2, "paths": ["docs/huge.md", "src/minified.js"]}


def _args(*given):
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    return parser.parse_args(list(given))


@pytest.fixture()
def semantic_answers(monkeypatch):
    answer = {}
    monkeypatch.setattr("gov.store.load", lambda root: {"digest": "d"})
    monkeypatch.setattr("gov.retrieval.lexical.refresh", lambda root: None)
    monkeypatch.setattr("gov.retrieval.semantic.refresh", lambda root: dict(answer))
    monkeypatch.setattr("gov.codeintel.index", lambda root: None)
    return answer


def test_the_rebuild_names_the_chunks_the_embedder_s_limit_cut(tmp_path, semantic_answers):
    semantic_answers.update(available=True, cut=CUT)
    assert run(tmp_path, _args(), EMBEDDED)["stores"]["semantic"] == {"status": "recreated", "cut": CUT}


def test_a_stage_not_built_still_names_the_cut(tmp_path, semantic_answers):
    semantic_answers.update(available=False, reason="EMBEDDER_ON_CPU: ...", cut=CUT)
    semantic = run(tmp_path, _args(), EMBEDDED)["stores"]["semantic"]
    assert semantic["status"] == "not_recreated" and semantic["cut"] == CUT


@pytest.mark.parametrize("cut", [None, {"limit": 10_000, "count": 0, "paths": []}])
def test_nothing_cut_leaves_the_result_as_before(tmp_path, semantic_answers, cut):
    semantic_answers.update(available=True, **({"cut": cut} if cut is not None else {}))
    assert run(tmp_path, _args(), EMBEDDED)["stores"]["semantic"] == {"status": "recreated"}
