"""W2-111 failure-5 for the live-hook case (DEC-1187 (1), DEC-906): its judgement fails a hook doing 150 ms of its own
work per call.

The planted hook (``w2_111_live_hook.plant_slow_hook``: 150 ms of its own CPU time per call, a busy loop, then the
after copy's own hook, so the decision is unchanged) is put in place of the after copy's ``pretooluse.py``, and
``test_w2_111_live_hook_diff_p95.py``'s judgement is applied to it, paired with the before copy as there. It must not
pass: every round's after figure is at or above 100 ms, all three rounds run. Five of the 20 cases, spread over the
kinds (a no-role Glob, an engineer's Write, a refused Write, the test designer's Read, a Bash pipeline), not all 20:
each takes all three rounds of a 0.2 s hook.
"""

from __future__ import annotations

import pytest

import w2_111_live_hook as live

SUBSET = ["W1-05 Glob-no-role", "W1-05 Write-engineer", "W1-02 engineer Write acceptance (deny r1)",
          "W2-57 test-designer Read ordinary", "Bash pipeline (engineer)"]


@pytest.fixture(scope="module")
def planted(tmp_path_factory):
    base = tmp_path_factory.mktemp("w2-111-live-planted")
    try:
        copies = live.make_copies(base / "copies")
        runner = live.make_runner(base / "run")
    except live.LiveHookUnavailable as exc:
        return {"error": str(exc)}
    return {"copies": copies, "runner": runner, "calls": live.calls(base / "targets"),
            "slow": live.plant_slow_hook(copies, base / "planted")}


@pytest.mark.parametrize("name", SUBSET, ids=[live.case_id(n) for n in SUBSET])
def test_the_planted_150_ms_hook_fails_the_live_hook_case(planted, name):
    if "error" in planted:
        pytest.fail(planted["error"], pytrace=False)
    status = live.porcelain()
    m = live.measure_paired(planted["runner"], planted["calls"][name], planted["copies"].before, planted["slow"],
                            mapped=live.NAMES.index(name) < live.MAPPED)
    assert live.porcelain() == status, "the case wrote in the repository (git status --porcelain changed)"
    assert not m.passed, "the live-hook case passed a hook doing 150 ms of its own CPU work per call: " + m.describe()
    assert len(m.rounds) == live.ROUNDS and all(r[1] >= live.BOUND_S for r in m.rounds), m.describe()
