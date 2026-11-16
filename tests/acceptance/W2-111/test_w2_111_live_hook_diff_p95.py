"""W2-111 success-9 and success-10 (DEC-1187 (1)'s target: within 100 ms, paired, the drop recorded) and failure-4 (the
decisions) on the live hook's patched copy (DEC-1187 (1); S9 amended by P-W2-111-S9-DROP (a), DEC-1157 (12)).

The engineer's diff of ``.claude/hooks/`` (``docs/changes/W2-111-live-hook/live-hook.diff``) is applied by ``git
apply`` to a clean copy of the tree's ``.claude/hooks/`` (the applied ACT-GUARD-FIX-6 bytes, checked); the before copy
and the after copy are each run as ``.claude/settings.json``'s PreToolUse command runs the live hook, on the repository
the tests run in, and timed paired in the same run by W2-111's method (``w2_111_live_hook.measure_paired``), over
``measure.py``'s 20 cases (the 15 mapped W1-05, W1-02 and W2-57 cases and the 5 Bash cases). A case passes when, in one
round, its after figure is under 100 ms; every call is decided the same by both copies, and as ``measure.py`` recorded.
The drop (before less after, per round) is recorded, not judged: it is in the failure message and printed on a pass
(``-s``). The 30 ms clause was removed by P-W2-111-S9-DROP (a): it came from a measure at load 14-28, and quiet the
applied hook is already under the bound. The case writes nothing in the repository. (The function, whose name read "and 30 ms
below", was renamed to what it checks, by the lead's decision on P-W2-111-TD5-NAME (a); its 20 ids are unchanged.)
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
def test_the_live_hook_s_patched_copy_is_within_100_ms_of_the_applied_hook_the_drop_recorded(setup, index):
    if "error" in setup:
        pytest.fail(setup["error"], pytrace=False)
    name = live.NAMES[index]
    status = live.porcelain()
    copies = setup["copies"]
    m = live.measure_paired(setup["runner"], setup["calls"][name], copies.before, copies.after,
                            mapped=index < live.MAPPED)
    assert live.porcelain() == status, "the case wrote in the repository (git status --porcelain changed)"
    assert m.passed, m.describe()
