"""S6: plan_override: <DEC-id> on a ticket lets it share a batch despite an overlap or a wait, shown in the plan as
OVERRIDE with the decision id (DEC-899, DEC-1088 (5))."""

from __future__ import annotations

import pytest

import w2_136_support as support
from w2_136_support import T

A = T("PLN-f001", "W2-601", status="in_progress", priority=1, writes=("src/o/**",))
OVERLAP = T("PLN-f002", "W2-602", writes=("src/o/x.py",))
WAIT = T("PLN-f002", "W2-602", writes=("src/p/**",), depends_on=("PLN-f001",))


@pytest.mark.parametrize("ticket", [OVERLAP, WAIT], ids=["despite-an-overlap", "despite-a-wait"])
def test_s6_an_override_shares_the_batch_and_is_shown_with_its_decision_id(planted, ticket):
    store = planted((A, ticket.but(plan_override="DEC-899")), ("src/o/x.py",))
    run = support.run(store.root, "--open")
    assert run.code in (0, 1), run
    plan = support.text_plan(run.out, store, run)
    assert plan.batches == [{"PLN-f001", "PLN-f002"}], run
    shown = support.lines_with(plan, "OVERRIDE")
    assert any("DEC-899" in line and store.mentions(line, "PLN-f002") for line in shown), run
    data = support.envelope(support.run(store.root, "--open", "--json"))
    found = support.entries(data["result"], "OVERRIDE")
    assert any("DEC-899" in " ".join(support.strings(e)) and support.json_mentions(store, e, "PLN-f002")
               for e in found), data
    assert support.json_plan(data["result"], store).batches == [{"PLN-f001", "PLN-f002"}], data


@pytest.mark.parametrize("ticket", [OVERLAP, WAIT], ids=["an-overlap", "a-wait"])
def test_s6_without_the_override_the_same_tickets_wait(planted, ticket):
    store = planted((A, ticket), ("src/o/x.py",))
    run = support.run(store.root, "--open")
    assert run.code in (0, 1), run
    plan = support.text_plan(run.out, store, run)
    assert plan.batches == [{"PLN-f001"}, {"PLN-f002"}], run
    assert "OVERRIDE" not in run.out, run
