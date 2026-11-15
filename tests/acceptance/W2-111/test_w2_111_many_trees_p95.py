"""W2-111 success-6 (DEC-1184 (3)): a call is decided within the bound with 150 or more worktrees registered.

The planted repository has 150 worktrees registered besides its main tree, and a planted evaluation set whose hidden
part measures the engineer, so the guard must place the engineer's every call against the hidden part of every tree
(DEC-820 (d), W2-84). The engineer's session runs in the main tree and makes a Read, a Write and a Bash call there,
each allowed. The measure is W1-02's, unchanged (see ``w2_111_support.measure``): p95 of the hook's own CPU time,
less a reference hook's, within 100 ms. The call's PATH is the session's own.
"""

from __future__ import annotations

import pytest

import w2_111_support as support


@pytest.mark.parametrize("name", support.TREES_CALLS, ids=support.TREES_CALLS)
def test_a_call_with_150_worktrees_registered_is_decided_within_100_ms_at_p95(trees_world, name):
    assert len(trees_world.trees) - 1 >= 150, "the planted repository has fewer than 150 worktrees registered"
    m = support.measure(f"{name} with {len(trees_world.trees) - 1} worktrees (engineer)",
                        support.trees_call(trees_world, name), "allow", trees=len(trees_world.trees))
    assert m.passed, m.describe()
