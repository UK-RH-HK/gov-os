"""S3: overlap is decided by the guard's own pattern matcher (``gov.guard.decide._match_pattern``, decide.py:96-102:
``*`` within a folder, ``**`` across), on the tracked files and pattern to pattern for paths not yet created, erring
toward overlap; two patterns the guard would let two writers both touch are never planned in parallel
(DEC-1088 (1)).

Each case is a store of two tickets, PLN-c001 (priority 1) writing the first pattern and PLN-c002 (priority 2) the
second. Overlapping: two batches, PLN-c002 waiting for PLN-c001 (WRITES_OVERLAP). Not overlapping: one batch."""

from __future__ import annotations

import pytest

import w2_136_support as support
from w2_136_support import T

from gov.guard.decide import _match_pattern

TRACKED = ("src/p/mod.py", "src/p/deep/x/y.py", "src/a/x.py", "src/a/y.py", "src/b/z.py", "docs/a.md")

# (case id, first pattern, second pattern, a path both match under the guard's matcher, or None for none)
OVERLAP = [
    ("star-within-a-folder-on-a-tracked-file", "src/p/*.py", "src/p/mod.py", "src/p/mod.py"),
    ("double-star-across-folders-on-a-tracked-file", "src/p/**", "src/p/deep/x/y.py", "src/p/deep/x/y.py"),
    ("double-star-and-star-in-a-folder-not-yet-created", "src/new/**", "src/new/*.py", "src/new/a.py"),
    ("a-folder-and-a-file-not-yet-created", "docs/**", "docs/changes/W2-1-evidence.md",
     "docs/changes/W2-1-evidence.md"),
    ("the-same-literal-path-not-yet-created", "docs/new.md", "docs/new.md", "docs/new.md"),
    ("a-name-prefix-and-a-file-not-yet-created", "tests/unit/launch/test_w2_136*",
     "tests/unit/launch/test_w2_136_check.py", "tests/unit/launch/test_w2_136_check.py"),
    ("an-inner-double-star-and-a-file-in-folders-not-yet-created", "src/**/test_*.py", "src/q/r/test_a.py",
     "src/q/r/test_a.py"),
    ("a-wide-folder-and-a-star-in-a-folder-not-yet-created", "src/**", "src/r/*.py", "src/r/b.py"),
]
APART = [
    ("a-star-stays-in-its-folder", "src/p/*.py", "src/p/deep/x/y.py"),
    ("two-disjoint-folders", "src/a/**", "src/b/**"),
    ("two-tracked-files-in-one-folder", "src/a/x.py", "src/a/y.py"),
    ("two-files-not-yet-created-in-one-folder", "docs/c.md", "docs/d.md"),
]


def _store(planted, first, second):
    return planted((T("PLN-c001", "W2-301", priority=1, writes=(first,)),
                    T("PLN-c002", "W2-302", priority=2, writes=(second,))), TRACKED)


def test_s3_premise_the_cases_hold_under_the_guard_s_own_matcher():
    for case, first, second, witness in OVERLAP:
        assert _match_pattern(witness, first) and _match_pattern(witness, second), case
    candidates = set(TRACKED) | {p for _, first, second in APART for p in (first, second) if "*" not in p}
    candidates |= {"src/p/deep/x/y.py", "src/p/mod.py", "src/a/q/r.py", "src/b/q/r.py"}
    for case, first, second in APART:
        assert not any(_match_pattern(p, first) and _match_pattern(p, second) for p in candidates), case
    # the tracked files the "tracked" cases rest on are in every store
    assert {"src/p/mod.py", "src/p/deep/x/y.py", "src/a/x.py", "src/a/y.py"} <= set(TRACKED)


@pytest.mark.parametrize("first, second", [c[1:3] for c in OVERLAP], ids=[c[0] for c in OVERLAP])
def test_s3_patterns_the_guard_lets_two_writers_both_touch_run_in_series(planted, first, second):
    store = _store(planted, first, second)
    run = support.run(store.root, "--open")
    assert run.code == 0, run
    plan = support.text_plan(run.out, store, run)
    assert plan.batches == [{"PLN-c001"}, {"PLN-c002"}], run
    assert plan.triples == {("PLN-c002", "PLN-c001", "WRITES_OVERLAP")}, run


@pytest.mark.parametrize("first, second", [c[1:3] for c in APART], ids=[c[0] for c in APART])
def test_s3_patterns_no_path_matches_both_share_a_batch(planted, first, second):
    store = _store(planted, first, second)
    run = support.run(store.root, "--open")
    assert run.code == 0, run
    plan = support.text_plan(run.out, store, run)
    assert plan.batches == [{"PLN-c001", "PLN-c002"}] and plan.waits == [], run
