"""Standalone script (BR-DAG-AMEND-R1-22): runs ``gather_with_followup`` once, hermetically, and prints its
``merged_sha256`` to stdout. Invoked in a FRESH SUBPROCESS, with a caller-chosen ``PYTHONHASHSEED``, by
``tests/gather/test_followup.py::test_merged_sha256_is_identical_across_process_hash_seeds`` -- an in-process test
(even one that varies ``--threads``) can never observe Python's own per-process string-hash randomisation; only a
real subprocess boundary can. If any ordering in this node's own scope (``govbridge/gather/{followup,identifiers,
merge,versions}.py``) depended on iterating a bare ``set``/``frozenset`` of strings (whose iteration order Python
deliberately randomises per process via ``PYTHONHASHSEED``, unless a sort with a full tie-break re-orders it by
VALUE afterwards), two runs of this exact script with different seeds would print different hashes.

A hermetic fixture (no real store/git needed): the same 5-candidate, always-resolvable fake route this domain's own
``tests/gather/test_followup.py::_ResolvableExactRoutes`` uses, reused here rather than re-invented -- imported
directly from that test module (this script's own sys.path includes ``tests/gather``), never a second, silently
diverging copy of the same fake.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_DOMAIN = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
_FIXTURES_GATHER = os.path.join(_DOMAIN, "tests", "fixtures", "gather")
_TESTS_GATHER = os.path.join(_DOMAIN, "tests", "gather")
sys.path.insert(0, _DOMAIN)
sys.path.insert(0, _FIXTURES_GATHER)
sys.path.insert(0, _TESTS_GATHER)

from govbridge.core import taskctx as taskctxmod  # noqa: E402
from govbridge.gather import followup as followupmod  # noqa: E402
from test_followup import _ResolvableExactRoutes  # noqa: E402

TEST_FACETS_PATH = os.path.join(_FIXTURES_GATHER, "test-facets.yaml")


def main() -> int:
    routes = _ResolvableExactRoutes()
    ctx = taskctxmod.TaskContext(source="test")
    query = {"id": "Q1", "text": "nine ids", "class": None, "subject": None, "facets": ["purpose"]}
    result = followupmod.gather_with_followup(
        query, routes, task=ctx, batch_size=8, threads=1, max_followup_rounds=6,
        max_identifiers_per_round=2, max_total_identifiers=100, facets_path=TEST_FACETS_PATH,
    )
    print(result["merged_sha256"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
