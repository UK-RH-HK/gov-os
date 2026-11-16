"""W2-190 S2: A3 and a DELETE_FROM_ACTIVE_TREE of a file the record graph or its front matter classes superseded.

Each target is named, by path, in no other tracked file (``w2_190_support.assert_planted`` checks it when planting), so
the refusal is for the class and for nothing else: a record whose front matter says ``status: SUPERSEDED``; one that
says ``status: superseded`` (any case); an ACTIVE record that a successor supersedes by id (``supersedes: [<id>]``,
the id, not the path); an ACTIVE record whose own front matter says ``superseded_by: [<id>]`` (the same edge).
"""

from __future__ import annotations

import pytest

import w2_190_support as support
from w2_190_support import base

TARGETS = {
    "status-upper-case": support.SUPERSEDED_STATUS,
    "status-lower-case": support.SUPERSEDED_LOWER,
    "target-of-a-supersedes-edge": support.EDGE_TARGET,
    "superseded-by-in-its-own-front-matter": support.EDGE_BY_TARGET,
}


@pytest.mark.parametrize("target", TARGETS.values(), ids=TARGETS.keys())
def test_s2_deleting_a_file_classed_superseded_is_refused_with_delete_superseded(adoption, target):
    before = base.head(adoption.root)
    done = support.propose(adoption, [base.entry(target, support.DELETE, batch=1)])
    problem = support.problem_for(done, target)
    assert support.SUPERSEDED_CODE in problem, f"the problem for {target} does not carry {support.SUPERSEDED_CODE}: {problem}"
    support.assert_no_a3_record(adoption.root, before, done)
