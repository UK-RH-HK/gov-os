"""S10: the ready list the dispatcher reads may come from ``gov plan --ready`` (W2-136), reviewed and committed by the
orchestrator; the dispatcher starts only what is on it, and its own order is never its choice.

The list is made by the real ``gov plan --open --ready <file>`` on the planted project (tickets with their ``priority``,
``needs:``, ``waits_on:`` declared), and put in the state folder as ``ready.txt``; its briefs are written under the names
the list gives (``<W2>-A5-<run>.md``), as the orchestrator builds them. The planted priorities make the plan's order
differ from the order of the ids, so only a dispatcher that keeps the list's order passes.
"""

from __future__ import annotations

import w2_121_support as support
from w2_121_support import explain


def listed(text: str):
    return [line.split() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def planted_list(p):
    """Tickets W2-901 (priority 1), W2-902 (priority 2), W2-903 (priority 0), planned into ``ready.txt``."""
    for n, priority in ((901, 1), (902, 2), (903, 0)):
        p.add_ticket(n, brief=None, priority=priority)
    target = p.tmp / "ready-from-plan.txt"
    r = p.plan_ready(target)
    assert r.code in (0, 1), r
    text = target.read_text(encoding="utf-8")
    fields = listed(text)
    assert len(fields) == 3 and all(len(f) == 4 for f in fields), f"gov plan --ready wrote:\n{text}"
    p.state.mkdir(parents=True, exist_ok=True)
    (p.state / "ready.txt").write_text(text, encoding="utf-8")
    for w2, ticket, brief, log in fields:
        p.write_brief(brief, f"Brief of {ticket}, as the plan listed it.\n")
    return text, fields


def test_s10_the_dispatcher_starts_the_entries_of_a_plan_list_in_the_lists_own_order(project):
    p = project
    text, fields = planted_list(p)
    order = [f[3] for f in fields]
    assert order != sorted(order), f"premise: the plan's order is that of the ids: {order}"
    for count in (1, 2, 3):
        r = p.tick()
        assert r.code == 0, r
        p.wait_launches(count)
        p.settle(0.3)
        assert p.launched_logs() == order[:count], (p.launched_logs(), order)
    p.settle()
    assert p.tick().code == 0
    p.settle(0.5)
    assert len(p.launches()) == 3


def test_s10_an_entry_that_is_not_on_the_plan_list_is_not_started(project):
    p = project
    text, fields = planted_list(p)
    stranger = p.add_ticket(909)  # claimed, a worktree, a complete brief: but the plan was made without it
    for _ in range(4):
        assert p.tick().code == 0
        p.settle(0.3)
    p.wait_launches(3)
    p.settle()
    assert stranger.log not in p.launched_logs() and len(p.launches()) == 3, p.launched_logs()
    assert (p.state / "ready.txt").read_text(encoding="utf-8") == text, "the dispatcher changed the orchestrator's list"


def test_s10_the_plan_lists_comment_lines_are_not_malformed_entries(project):
    p = project
    text, fields = planted_list(p)
    assert any(line.lstrip().startswith("#") for line in text.splitlines()), "premise: the plan's list has comment lines"
    r = p.tick()
    assert r.code == 0, r
    assert "malformed" not in (p.status_text() + str(p.status_json())).lower(), explain(p, r)
