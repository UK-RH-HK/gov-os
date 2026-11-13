"""W2-136 S3 unit tests: the overlap of two path patterns, under the guard's own matcher."""

from __future__ import annotations

import itertools
import random

import pytest

from gov.guard.decide import _match_pattern
from gov.plan import overlap
from gov.plan.overlap import Tracked, patterns_overlap


@pytest.mark.parametrize("a, b, expected", [
    ("src/a.py", "src/a.py", True),
    ("src/a.py", "src/b.py", False),
    ("src/*.py", "src/a.py", True),
    ("src/*.py", "src/sub/a.py", False),          # * stays inside one folder
    ("src/**", "src/sub/deep/a.py", True),        # ** crosses folders
    ("src/a/**", "src/b/**", False),
    ("src/*/x.py", "src/a/*", True),
    ("src/*/x.py", "src/a/*/x.py", False),
    ("src/**/x.py", "src/a/*/x.py", True),
    ("tests/unit/launch/test_w2_136*", "tests/unit/launch/test_w2_*_x.py", True),
    ("tests/unit/launch/test_w2_136*", "tests/unit/launch/test_w2_20*", False),
    ("src/new/**", "src/new/sub/*.py", True),     # neither exists yet: pattern to pattern
    ("src/x", "src/x/**", True),                  # a literal path is also read as its folder (toward overlap)
    ("src/x", "src/xy.py", False),
    ("", "src/**", False),
])
def test_two_patterns_overlap_when_some_path_matches_both(a, b, expected):
    assert patterns_overlap(a, b) is expected
    assert patterns_overlap(b, a) is expected


def test_a_literal_path_is_judged_by_the_guards_own_matcher(monkeypatch):
    calls = []
    monkeypatch.setattr(overlap.decide, "_match_pattern", lambda path, pattern: calls.append((path, pattern)) or True)
    overlap.patterns_overlap.cache_clear()
    try:
        assert patterns_overlap("src/q.py", "src/*.txt") is True
    finally:
        overlap.patterns_overlap.cache_clear()
    assert ("src/q.py", "src/*.txt") in calls


def test_no_path_the_guard_lets_both_patterns_touch_is_missed():
    """Every pair of random patterns that the guard's matcher shows a common path for is an overlap."""
    rng = random.Random(136)
    parts = ["a", "b", "*", "**", "a*", "*b"]
    patterns = sorted({"/".join(rng.choice(parts) for _ in range(rng.randint(1, 3))) for _ in range(120)})
    paths = ["/".join(p) for n in (1, 2, 3, 4) for p in itertools.product(["a", "b", "ab", "ba", "c"], repeat=n)]
    for a, b in itertools.combinations(patterns, 2):
        common = any(_match_pattern(path, a) and _match_pattern(path, b) for path in paths)
        if common:
            assert patterns_overlap(a, b), (a, b)


def test_an_overlap_is_named_by_a_literal_path_then_by_a_tracked_file(tmp_path):
    tracked = Tracked(tmp_path)
    assert tracked.witness("src/**", "src/a.py") == "src/a.py"
    tracked._files = ["docs/x.md", "src/gov/plan/derive.py"]
    assert tracked.witness("src/**", "src/gov/*/derive.py") == "src/gov/plan/derive.py"
    assert tracked.witness("src/new/**", "src/new/*/x.py") == "src/new/**"
