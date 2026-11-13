"""S3, review round 2, B-1 (finding F-1, S3, Interface item 8): the VERDICT line's exact 95 % interval is computed from
the counts, never re-rounded from ``FIGURES.json``'s 4-place fractions.

Item 8: the interval is Clopper-Pearson, ``lo`` and ``hi`` in percent to one decimal, by bisection on the binomial tails;
the printed bounds are the exact bounds of (r, n) rounded once to one decimal. Item 10: ``FIGURES.json``'s
``verdict.interval_exact`` stays ``[lo, hi]`` as fractions to 4 places, for the same run. A double rounding (the 4-place
fraction, then one decimal of its percent) prints other digits at the planted counts below.

The planted counts (the exact bounds in percent in brackets; the double rounding's print after the arrow):

* 32 right of 40: ``64.4 to 90.9`` (64.352, 90.948; a double rounding prints 64.3 to 91.0);
* 31 right of 40: ``61.5 to 89.2`` (61.549, 89.160; a double rounding prints 61.6 to 89.2).

The brief's 78 of 79 (93.148 %, a double rounding prints 93.2) cannot be planted: ``measure`` goes through W2-170's
``declare`` and its ``preflight`` passes 36 to 40 questions (``PF-COUNT``), so no world here holds 79 questions. Two
counts at n = 40 where the two roundings differ were found by computing the interval for every r of 0 to 40 (r = 8, 31
and 32 differ at n = 40; 32 and 31 are used because 8 would need 32 misses). The expected bounds below come from this
file's own Clopper-Pearson (a bisection written here, not the scenario oracle's), and the literal strings are asserted
too, so the case is not the code's arithmetic mirrored.
"""

from __future__ import annotations

import math
import re

import pytest

import w2_171_scenario as S

FIVE = S.SCENARIOS["five"]
# (right of 40, the literal the VERDICT line must hold, the extra misses added to ``five``'s five)
PLANTED = [(32, "exact 95 % interval 64.4 to 90.9 %", ("q10", "q20", "q30")),
           (31, "exact 95 % interval 61.5 to 89.2 %", ("q10", "q20", "q30", "q36"))]


def _cdf_le(x: int, n: int, p: float) -> float:
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(x + 1))


def clopper_pearson(x: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """The exact two-sided interval of ``x`` of ``n`` by bisection on the binomial tails (this file's own)."""
    half = alpha / 2

    def bisect(too_small, hold_low_when):
        low, high = 0.0, 1.0
        for _ in range(200):
            mid = (low + high) / 2
            if too_small(mid) == hold_low_when:
                low = mid
            else:
                high = mid
        return (low + high) / 2
    lower = 0.0 if x == 0 else bisect(lambda p: (1 - _cdf_le(x - 1, n, p)) < half, True)
    upper = 1.0 if x == n else bisect(lambda p: _cdf_le(x, n, p) < half, False)
    return lower, upper


def scenario_with_extra_misses(name: str, extra) -> S.Scenario:
    """``five`` with the questions in ``extra`` answered at the first search with a citation that matches no gold place:
    right at A2 is false for each (an ``incomplete`` miss, no wrong claim), so ``right`` falls by ``len(extra)``."""
    behaviour = dict(FIVE.behaviour)
    behaviour.update({q: "A1_cite" for q in extra})
    return S.Scenario(name, behaviour=behaviour, ranks=dict(FIVE.ranks), routes=dict(FIVE.routes),
                      disagree=FIVE.disagree, retried=FIVE.retried, later_fail=FIVE.later_fail)


def judge_with(make_world, right: int, extra):
    world = make_world("measured:five")
    sc = scenario_with_extra_misses(f"right{right}", extra)
    sc.install(world)
    run = world.judge()
    assert run.code == 0, run
    assert S.Expected(sc, world).right_wrong() == (right, 2), "the planted scenario gives the planted r and w"
    return world, run


def verdict_line(run) -> str:
    lines = [x for x in run.lines if x.startswith("VERDICT")]
    assert len(lines) == 1, run
    return lines[0]


@pytest.mark.parametrize("right,literal,extra", PLANTED)
def test_s3_the_verdict_interval_is_the_exact_bounds_of_the_counts_rounded_once(make_world, right, literal, extra):
    """B-1 (F-1, Interface item 8): ``VERDICT`` prints the exact Clopper-Pearson bounds of (r, n), each rounded once to
    one decimal; the literal and this file's own bisection both say which digits."""
    world, run = judge_with(make_world, right, extra)
    lo, hi = clopper_pearson(right, 40)
    line = verdict_line(run)
    assert literal in line, (literal, line)
    printed = f"exact 95 % interval {100 * lo:.1f} to {100 * hi:.1f} %"
    assert printed == literal, "the planted literal is the single rounding of this file's own bounds"
    assert re.fullmatch(r"VERDICT right end to end %d of 40 \(%.1f %%; %s\); wrong claims 2 of 40 \(5\.0 %%\)"
                        % (right, 100 * right / 40, re.escape(printed)), line), line
    # it is not a re-rounding of the 4-place fractions (the digits the double rounding would print differ)
    double = f"exact 95 % interval {100 * round(lo, 4):.1f} to {100 * round(hi, 4):.1f} %"
    assert double != literal and double not in line, "the planted count is one where the two roundings differ"


@pytest.mark.parametrize("right,literal,extra", PLANTED)
def test_s3_figures_json_keeps_the_interval_as_fractions_to_4_places(make_world, right, literal, extra):
    """B-1 (Interface item 10): ``verdict.interval_exact`` is ``[lo, hi]`` as fractions to 4 places for the same run
    whose VERDICT line prints the one-decimal percents (that line is the other case's). This one guards item 10 against
    the fix for B-1: the fractions stay as they are."""
    world, run = judge_with(make_world, right, extra)
    lo, hi = clopper_pearson(right, 40)
    interval = world.json_of("FIGURES.json")["verdict"]["interval_exact"]
    assert interval == [round(lo, 4), round(hi, 4)], interval
    assert all(isinstance(x, float) and round(x, 4) == x and 0 <= x <= 1 for x in interval), interval
    assert verdict_line(run).startswith(f"VERDICT right end to end {right} of 40 ("), run
