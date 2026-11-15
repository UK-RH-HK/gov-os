"""W2-111 success-5 (DEC-1184 (3)): a Bash call is decided within the 100 ms bound at p95 by the hook's own work.

The engineer's Bash calls in W1-02's fixture project, with a role set: a plain command, a pipe and a redirect, each
allowed (inside the ticket's ``src/gov/guard/**``, no install), so the hook does all of a Bash call's work: the
decision, the install check on the allowed command and the before-snapshot. The measure is W1-02's, unchanged (see
``w2_111_support.measure``): the CPU time of the hook's process and its children per call, less the median CPU time of
a reference hook timed beside it in the same round; nearest-rank p95 of 40 calls; the bound 100 ms at p95; a round
that misses repeats, up to three rounds. The call's PATH is the session's own.
"""

from __future__ import annotations

import pytest

import w2_111_support as support


@pytest.mark.parametrize("name", list(support.BASH_CALLS), ids=list(support.BASH_CALLS))
def test_a_bash_call_with_a_role_set_is_decided_within_100_ms_at_p95(bash_world, name):
    m = support.measure(f"Bash {name} `{support.BASH_CALLS[name]}` (engineer)",
                        support.bash_call(bash_world, name), "allow")
    assert m.passed, m.describe()
