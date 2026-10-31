"""Builder tests for the authority order (W2-87; DEC-952 item 1, DEC-423, DEC-694).

Regression evidence only (DEC-136). The path map's ``retrieval_authority`` block is read and validated (fail
closed), a path pattern matches a path whole, a chunk in two tiers gets the lower one, a not-current record is
never lifted, and the lift is bounded. No store: the records are given as the store would give them.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.retrieval import authority  # noqa: E402

BLOCK = {"lift": {"fused": 0.004, "rerank": 1.0}, "default": "middle",
         "tiers": [{"name": "governing", "records": [{"type": "decision", "status": ["ACCEPTED"]}],
                    "paths": ["docs/spec/**"]},
                   {"name": "middle"},
                   {"name": "reports", "paths": ["tests/**", "docs/*.md"]}]}


def _write(root: Path, document) -> Path:
    path = root / authority.PATH_MAP_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document if isinstance(document, str) else yaml.safe_dump(document), encoding="utf-8")
    return root


def _block(**changes) -> dict:
    block = yaml.safe_load(yaml.safe_dump(BLOCK))
    block.update(changes)
    return block


def _order(root: Path, block=BLOCK, known=(), edges=()) -> authority.Order:
    read = authority.read_block(_write(root, {"retrieval_authority": block}))
    return authority.Order(read, list(known), list(edges), lambda path, line: None)


def test_no_path_map_or_no_block_reads_as_none(tmp_path):
    assert authority.read_block(tmp_path) is None
    assert authority.read_block(_write(tmp_path, {"namespaces": {}})) is None
    order = authority.Order(None, [], [], lambda path, line: None)
    hits = [{"chunk_id": "a", "path": "tests/x.py", "score": 0.1}, {"chunk_id": "b", "path": "docs/spec/y.md",
                                                                      "score": 0.1}]
    assert order.fused(hits, {}) is hits and order.reranked(hits) is hits


@pytest.mark.parametrize("block, key", [
    ([], "retrieval_authority"),
    (_block(extra=1), "retrieval_authority.extra"),
    ({k: v for k, v in BLOCK.items() if k != "default"}, "retrieval_authority.default"),
    (_block(lift={"fused": 0.1}), "retrieval_authority.lift.rerank"),
    (_block(lift={"fused": -0.1, "rerank": 1}), "retrieval_authority.lift.fused"),
    (_block(lift={"fused": True, "rerank": 1}), "retrieval_authority.lift.fused"),
    (_block(lift={"fused": "0.1", "rerank": 1}), "retrieval_authority.lift.fused"),
    (_block(tiers=[]), "retrieval_authority.tiers"),
    (_block(tiers=[{"name": "middle"}, {"name": "middle"}]), "retrieval_authority.tiers[1].name"),
    (_block(tiers=[{"name": "middle", "colour": "red"}]), "retrieval_authority.tiers[0].colour"),
    (_block(tiers=[{"paths": ["a"]}]), "retrieval_authority.tiers[0].name"),
    (_block(default="top"), "retrieval_authority.default"),
    (_block(tiers=[{"name": "middle", "paths": [""]}]), "retrieval_authority.tiers[0].paths"),
    (_block(tiers=[{"name": "middle", "records": [{"status": ["ACCEPTED"]}]}]),
     "retrieval_authority.tiers[0].records[0].type"),
    (_block(tiers=[{"name": "middle", "records": [{"type": "decision", "status": ["NOT ONE"]}]}]),
     "retrieval_authority.tiers[0].records[0].status"),
])
def test_an_invalid_block_refuses_with_config_invalid_naming_file_and_key(tmp_path, block, key):
    with pytest.raises(GovError) as raised:
        authority.read_block(_write(tmp_path, {"retrieval_authority": block}))
    assert raised.value.code == "CONFIG_INVALID"
    assert authority.PATH_MAP_REL in str(raised.value) and key in str(raised.value)


def test_a_path_map_that_cannot_be_parsed_refuses(tmp_path):
    with pytest.raises(GovError) as raised:
        authority.read_block(_write(tmp_path, "retrieval_authority: [unclosed\n"))
    assert raised.value.code == "CONFIG_INVALID"


@pytest.mark.parametrize("pattern, path, matches", [
    ("tests/**", "tests/a.py", True),
    ("tests/**", "tests/unit/deep/a.py", True),
    ("tests/**", "src/tests/a.py", False),
    ("docs/**/x.md", "docs/x.md", True),
    ("docs/**/x.md", "docs/a/b/x.md", True),
    ("docs/*.md", "docs/a.md", True),
    ("docs/*.md", "docs/a/b.md", False),
    ("docs/a.md", "docs/aXmd", False),
])
def test_a_pattern_matches_the_path_whole(pattern, path, matches):
    assert bool(authority._pattern(pattern).fullmatch(path)) is matches


def test_a_chunk_in_two_tiers_gets_the_lower_one(tmp_path):
    known = [{"id": "DEC-1", "type": "decision", "status": "ACCEPTED", "path": "tests/x.md", "span": None},
             {"id": "DEC-2", "type": "decision", "status": "ACCEPTED", "path": "notes/y.md", "span": None}]
    order = _order(tmp_path, known=known)
    assert order.steps("tests/x.md", 1) == -1  # governing by its record, reports by its path
    assert order.steps("notes/y.md", 1) == 1
    assert order.steps("docs/spec/z.md", 1) == 1
    assert order.steps("src/z.py", 1) == 0


@pytest.mark.parametrize("status, edges", [("SUPERSEDED", []), ("WITHDRAWN", []),
                                           ("ACCEPTED", [{"type": "SUPERSEDES", "source": "DEC-9",
                                                          "target": "DEC-1"}])])
def test_a_record_that_is_not_current_is_never_above_the_default(tmp_path, status, edges):
    known = [{"id": "DEC-1", "type": "decision", "status": status, "path": "docs/spec/a.md", "span": None}]
    block = _block(tiers=[{"name": "governing", "records": [{"type": "decision"}], "paths": ["docs/spec/**"]},
                          {"name": "middle"}])
    assert _order(tmp_path, block, known, edges).steps("docs/spec/a.md", 1) == 0


def test_the_lift_is_bounded_and_ties_keep_the_order(tmp_path):
    hits = [{"chunk_id": "t1", "path": "tests/a.py", "score": 0.020},
            {"chunk_id": "t2", "path": "tests/b.py", "score": 0.016},
            {"chunk_id": "g", "path": "docs/spec/c.md", "score": 0.010},
            {"chunk_id": "m", "path": "src/d.py", "score": 0.014}]
    # g gains 0.004 (0.014), the tests lose 0.004 (0.016, 0.012): t1 is better by more than the lift and stays first
    assert [hit["chunk_id"] for hit in _order(tmp_path).fused(hits, {})] == ["t1", "g", "m", "t2"]
    assert [hit["score"] for hit in hits] == [0.020, 0.016, 0.010, 0.014]


def test_the_rerank_lift_applies_only_when_every_candidate_has_a_score(tmp_path):
    ranked = [{"chunk_id": "t", "path": "tests/a.py", "start_line": 1, "rerank_score": 0.5},
              {"chunk_id": "g", "path": "docs/spec/c.md", "start_line": 1, "rerank_score": 0.2}]
    order = _order(tmp_path)
    assert [hit["chunk_id"] for hit in order.reranked(ranked)] == ["g", "t"]
    unscored = [{key: value for key, value in hit.items() if key != "rerank_score"} for hit in ranked]
    assert order.reranked(unscored) is unscored
