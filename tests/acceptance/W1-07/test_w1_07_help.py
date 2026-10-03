"""KPI success 3, second half: ``gov --help`` answers in under 300 ms."""

from __future__ import annotations

import statistics

HELP_BUDGET_S = 0.300
RUNS = 9


def test_help_prints_usage_and_ends_with_exit_code_0(gov):
    run = gov("--help")
    assert run.returncode == 0, f"gov --help does not end with exit code 0\n{run.describe()}"
    assert "gov" in run.stdout and run.stdout.strip(), f"gov --help prints no usage\n{run.describe()}"


def test_help_answers_in_under_300_ms(gov):
    """The median of nine runs, after one run that fills the bytecode cache (an installed package has one)."""
    warm_up = gov("--help")
    assert warm_up.returncode == 0, f"gov --help does not end with exit code 0\n{warm_up.describe()}"
    times = []
    for _ in range(RUNS):
        run = gov("--help")
        assert run.returncode == 0, run.describe()
        times.append(run.seconds)
    median = statistics.median(times)
    assert median < HELP_BUDGET_S, \
        f"gov --help took {median * 1000:.0f} ms (median of {RUNS}: {[round(t * 1000) for t in times]} ms)"
