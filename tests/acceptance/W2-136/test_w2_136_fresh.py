"""S8: the plan is recomputed from the current tickets on every run: an open ticket changed in flight changes the plan
at the next run, with nothing cached between runs (DEC-1088 (6)). Each edit is committed and keeps the file's mtime,
so a cache keyed on the file's time would go stale."""

from __future__ import annotations

import pytest

import w2_136_support as support
from w2_136_support import T

A = T("PLN-h001", "W2-801", status="in_progress", priority=1, writes=("src/a/**",))
B = T("PLN-h002", "W2-802", writes=("src/b/**",))
B_DEP = B.but(depends_on=("PLN-h001",))


def _plan(store):
    run = support.run(store.root, "--open")
    assert run.code == 0, run
    plan = support.text_plan(run.out, store, run)
    return (plan.n, plan.b, plan.w, sorted(map(sorted, plan.batches)), sorted(plan.triples)), plan, run


CASES = {
    "a-dependency-added": ((A, B), B_DEP, ([{"PLN-h001", "PLN-h002"}], set()),
                           ([{"PLN-h001"}, {"PLN-h002"}], {("PLN-h002", "PLN-h001", "DEPENDS_ON")})),
    "the-ticket-waited-for-closed": ((A, B_DEP), A.but(status="closed"),
                                     ([{"PLN-h001"}, {"PLN-h002"}], {("PLN-h002", "PLN-h001", "DEPENDS_ON")}),
                                     ([{"PLN-h002"}], set())),
}


@pytest.mark.parametrize("case", list(CASES))
def test_s8_a_ticket_edited_between_runs_changes_the_next_plan_and_back(planted, case):
    tickets, edited, (batches_1, waits_1), (batches_2, waits_2) = CASES[case]
    store = planted(tickets)
    original = store.tickets[edited.id]
    key_1, plan_1, run_1 = _plan(store)
    assert plan_1.batches == batches_1 and plan_1.triples == waits_1, run_1
    store.rewrite(edited)
    key_2, plan_2, run_2 = _plan(store)
    assert plan_2.batches == batches_2 and plan_2.triples == waits_2, run_2
    store.rewrite(original)
    key_3, plan_3, run_3 = _plan(store)
    assert key_3 == key_1, run_3
