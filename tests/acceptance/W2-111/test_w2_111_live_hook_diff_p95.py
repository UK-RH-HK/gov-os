"""W2-111 success-9 (the 30 ms drop), success-10 (the 100 ms bound) and failure-4 (the decisions) on the live hook's
patched copy (DEC-1187 (1)).

The engineer's diff of ``.claude/hooks/`` (``docs/changes/W2-111-live-hook/live-hook.diff``) is applied by ``git
apply`` to a clean copy of the tree's ``.claude/hooks/`` (the applied ACT-GUARD-FIX-6 bytes, checked); the before copy
and the after copy are each run as ``.claude/settings.json``'s PreToolUse command runs the live hook, on the repository
the tests run in, and timed paired in the same run by W2-111's method (``w2_111_live_hook.measure_paired``), over
``measure.py``'s 20 cases. A case passes when, in one round, its after figure is under 100 ms and, for the 15 mapped
W1-05, W1-02 and W2-57 cases (``measure.py``'s first 15), at least 30 ms below its before figure; every call is decided
the same by both copies, and as ``measure.py`` recorded. The case writes nothing in the repository.
"""

from __future__ import annotations

import pytest

import w2_111_live_hook as live


@pytest.fixture(scope="module")
def setup(tmp_path_factory):
    """The copies, the runner and the calls; or the reason they cannot be had (each case fails with it)."""
    base = tmp_path_factory.mktemp("w2-111-live")
    try:
        copies = live.make_copies(base / "copies")
        runner = live.make_runner(base / "run")
    except live.LiveHookUnavailable as exc:
        return {"error": str(exc)}
    return {"copies": copies, "runner": runner, "calls": live.calls(base / "targets")}


@pytest.mark.parametrize("index", range(len(live.CASES)), ids=[live.case_id(n) for n in live.NAMES])
def test_the_live_hook_s_patched_copy_is_within_100_ms_and_30_ms_below_the_applied_hook(setup, index):
    if "error" in setup:
        pytest.fail(setup["error"], pytrace=False)
    name = live.NAMES[index]
    status = live.porcelain()
    copies = setup["copies"]
    m = live.measure_paired(setup["runner"], setup["calls"][name], copies.before, copies.after,
                            mapped=index < live.MAPPED)
    assert live.porcelain() == status, "the case wrote in the repository (git status --porcelain changed)"
    assert m.passed, m.describe()
