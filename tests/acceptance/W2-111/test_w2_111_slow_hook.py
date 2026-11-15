"""W2-111 failure-5 (DEC-1184 (3), DEC-906): no new timing case passes a hook doing 150 ms of its own work.

Each of the six timing cases (success-5's three Bash calls, success-6's Read, Write and Bash with 150 worktrees) is
measured again, as its own case measures it, with the planted hook in place of the product hook: a hook that spends
150 ms of its own CPU time per call (a busy loop on ``time.process_time()``, not a sleep) and then gives the product
hook's own answer. The case must not pass: every round's judged figure is at or above the bound. The decision is
still the product hook's, so a wrong decision fails here as in the case itself, not as a pass.
"""

from __future__ import annotations

import pytest

import w2_111_support as support

CASES = [("bash", name) for name in support.BASH_CALLS] + [("trees", name) for name in support.TREES_CALLS]
IDS = [f"{world}-{name}" for world, name in CASES]


@pytest.mark.parametrize("world_name,name", CASES, ids=IDS)
def test_the_planted_150_ms_hook_fails_each_new_timing_case(request, world_name, name):
    if world_name == "bash":
        world = request.getfixturevalue("bash_world")
        call, trees = support.bash_call(world, name), 1
    else:
        world = request.getfixturevalue("trees_world")
        call, trees = support.trees_call(world, name), len(world.trees)
    with support.slow_hook(world.project):
        m = support.measure(f"planted 150 ms hook, {world_name} {name}", call, "allow", trees=trees)
    assert not m.passed, "the case passed a hook doing 150 ms of its own CPU work per call: " + m.describe()
    assert len(m.judged) == support.ROUNDS
