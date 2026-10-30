"""W2-57, KPI line 5 (I1 F-10): the 100 ms p95 budget covers a test designer's read on a branch with changes.

DEC-149: the guard's decision is under 100 ms at p95, for every tool. Under Policy 2 (c) (DEC-820 (c), DEC-826
Q2) a test designer's every read runs git to find the files its ticket's branch changes against ``w2/integrate``;
no p95 case timed that path (W1-02's times five writes, W1-05's an engineer's and a role-less session's calls).

The world is W1-02's fixture project with the guard installed, its first commit on ``w2/integrate`` and the
ticket's own branch with 120 changed files (real ticket branches held 48 to 318, I1 F-10). That the read takes the
path is shown first: the designer is refused a file the branch changes, and allowed an ordinary one. The timing is
W1-02's: the hook process, start to exit, as the harness waits for it; p95 over 40 reads after 3 warm-up reads, a
round repeated up to three times so that a single stall does not fail it.

A latency case: it is kept serial in the close's list (``serial: latency``), alone after the parallel phase. About
2.5 s alone (on a quiet machine a read took a median of 50 ms, p95 55 ms; an engineer's, 45 and 47 ms).
"""

from __future__ import annotations

import re

import w2_57_list_support as support

guard = support.guard_support

LATENCY_BOUND_S = 0.100
SAMPLES = 40
WARM_UP = 3
ROUNDS = 3
ORDINARY = "README.md"
CHANGED = "src/gov/guard/change_000.py"


def test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95(tmp_path):
    project, sandbox = support.designer_world(tmp_path)
    refused = support.designer_read(project, sandbox, CHANGED)
    assert refused.decision == "deny" and re.search(r"DEC-820 \(c\)", refused.stdout), (
        f"the fixture is wrong: the test designer is not refused a file its ticket's branch changes, so the read "
        f"does not take Policy 2 (c)'s path: {refused.describe()}"
    )
    for _ in range(WARM_UP):
        support.designer_read(project, sandbox, ORDINARY)
    rounds = []
    for _ in range(ROUNDS):
        samples = []
        for _ in range(SAMPLES):
            result = support.designer_read(project, sandbox, ORDINARY)
            assert result.decision == "allow", f"the timed read was not allowed: {result.describe()}"
            samples.append(result.seconds)
        rounds.append(guard.p95(samples))
        if rounds[-1] < LATENCY_BOUND_S:
            break
    assert min(rounds) < LATENCY_BOUND_S, (
        "p95 of a test designer's read on a branch with changes, per round (ms): "
        + ", ".join(f"{value * 1000:.1f}" for value in rounds) + f"; the bound is {LATENCY_BOUND_S * 1000:.0f} ms"
    )
