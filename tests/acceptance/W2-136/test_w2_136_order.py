"""S2: what orders tickets. needs: on a path an unfinished ticket writes (NEEDS_WHAT_WRITES, naming the path);
overlapping writes in series (WRITES_OVERLAP); depends_on and an unfinished waits_on (DEPENDS_ON, WAITS_ON); reads:
orders nothing and is a READS_WIDE warning naming the waits it would have caused; the rest share one batch
(DEC-1088 (3), DEC-235). Every ticket here declares reads:, needs: and waits_on: (empty unless named), so no S5
finding is raised but where a case asks for one."""

from __future__ import annotations

import w2_136_support as support
from w2_136_support import T

DONE = T("PLN-b009", "W2-219", status="closed", writes=("src/done.py",))


def _plan(planted, tickets, files=()):
    store = planted(tickets, files)
    run = support.run(store.root, "--open")
    return store, run, support.text_plan(run.out, store, run)


def test_s2_needs_on_a_path_an_unfinished_ticket_writes_waits_for_it_naming_the_path(planted):
    a = T("PLN-b001", "W2-211", status="in_progress", priority=1, writes=("src/lib/core.py",))
    b = T("PLN-b002", "W2-212", writes=("src/app/**",), needs=("src/lib/core.py",))
    c = T("PLN-b003", "W2-213", writes=("src/c/**",), needs=("src/nobody.py",))  # a path nobody writes
    d = T("PLN-b004", "W2-214", writes=("src/d/**",), needs=("src/done.py",))    # a path only a closed ticket wrote
    store, run, plan = _plan(planted, (a, b, c, d, DONE), ("src/lib/core.py", "src/done.py"))
    assert run.code == 0, run
    assert plan.batches == [{"PLN-b001", "PLN-b003", "PLN-b004"}, {"PLN-b002"}], run
    assert [(w, x, c_) for w, x, c_, _ in plan.waits] == [("PLN-b002", "PLN-b001", "NEEDS_WHAT_WRITES")], run
    assert "src/lib/core.py" in plan.waits[0][3], run


def test_s2_tickets_whose_writes_overlap_run_in_series(planted):
    a = T("PLN-b001", "W2-211", priority=1, writes=("src/w/**",))
    b = T("PLN-b002", "W2-212", priority=2, writes=("src/w/x.py",))
    c = T("PLN-b003", "W2-213", priority=2, writes=("src/other/**",))
    store, run, plan = _plan(planted, (a, b, c), ("src/w/x.py",))
    assert run.code == 0, run
    assert plan.batches == [{"PLN-b001", "PLN-b003"}, {"PLN-b002"}], run
    assert plan.triples == {("PLN-b002", "PLN-b001", "WRITES_OVERLAP")}, run


def test_s2_depends_on_an_unfinished_ticket_waits_and_on_a_closed_one_does_not(planted):
    a = T("PLN-b001", "W2-211", status="in_progress", priority=1, writes=("src/a/**",))
    b = T("PLN-b002", "W2-212", writes=("src/b/**",), depends_on=("PLN-b001",))
    c = T("PLN-b003", "W2-213", writes=("src/c/**",), depends_on=("PLN-b009",))
    store, run, plan = _plan(planted, (a, b, c, DONE))
    assert run.code == 0, run
    assert plan.batches == [{"PLN-b001", "PLN-b003"}, {"PLN-b002"}], run
    assert plan.triples == {("PLN-b002", "PLN-b001", "DEPENDS_ON")}, run


def test_s2_an_unfinished_waits_on_waits_and_a_closed_one_does_not(planted):
    a = T("PLN-b001", "W2-211", priority=1, writes=("src/a/**",))
    b = T("PLN-b002", "W2-212", writes=("src/b/**",), waits_on=("PLN-b001",))
    c = T("PLN-b003", "W2-213", writes=("src/c/**",), waits_on=("PLN-b009",))
    store, run, plan = _plan(planted, (a, b, c, DONE))
    assert run.code == 0, run
    assert plan.batches == [{"PLN-b001", "PLN-b003"}, {"PLN-b002"}], run
    assert plan.triples == {("PLN-b002", "PLN-b001", "WAITS_ON")}, run


def test_s2_waits_compose_into_a_chain_of_batches(planted):
    a = T("PLN-b001", "W2-211", status="in_progress", writes=("src/a/**",))
    b = T("PLN-b002", "W2-212", writes=("src/b/**",), depends_on=("PLN-b001",))
    c = T("PLN-b003", "W2-213", writes=("src/c/**",), waits_on=("PLN-b002",))
    store, run, plan = _plan(planted, (a, b, c))
    assert run.code == 0, run
    assert plan.batches == [{"PLN-b001"}, {"PLN-b002"}, {"PLN-b003"}], run
    assert plan.triples == {("PLN-b002", "PLN-b001", "DEPENDS_ON"), ("PLN-b003", "PLN-b002", "WAITS_ON")}, run


def test_s2_a_wide_read_orders_nothing_and_warns_naming_the_wait_it_would_cause(planted):
    a = T("PLN-b001", "W2-211", status="in_progress", priority=1, writes=("src/r/x.py",))
    b = T("PLN-b002", "W2-212", writes=("docs/b.md",), reads=("src/**",))
    store, run, plan = _plan(planted, (a, b), ("src/r/x.py",))
    assert run.code in (0, 1), run  # whether a warning alone exits 1 is not stated (README, D-3)
    assert plan.batches == [{"PLN-b001", "PLN-b002"}], run
    assert plan.waits == [] and plan.w == 0, run
    warned = support.lines_with(plan, "READS_WIDE")
    assert any(store.mentions(line, "PLN-b002") and store.mentions(line, "PLN-b001") for line in warned), run
    data = support.envelope(support.run(store.root, "--open", "--json"))
    found = support.entries(data["result"], "READS_WIDE")
    assert any(support.json_mentions(store, e, "PLN-b002") and support.json_mentions(store, e, "PLN-b001")
               for e in found), data
    assert support.json_plan(data["result"], store).waits == [], data


def test_s2_the_rest_share_one_batch(planted):
    tickets = (T("PLN-b001", "W2-211", status="in_progress", writes=("src/a/**",)),
               T("PLN-b002", "W2-212", writes=("src/b/*.py",), needs=("src/shared/util.py",)),
               T("PLN-b003", "W2-213", status="in_progress", writes=("docs/c.md",), depends_on=("PLN-b009",)),
               T("PLN-b004", "W2-214", writes=("tests/unit/d/**",), waits_on=("PLN-b009",)), DONE)
    store, run, plan = _plan(planted, tickets, ("src/shared/util.py",))
    assert run.code == 0, run
    assert (plan.n, plan.b, plan.w) == (4, 1, 0), run
    assert plan.batches == [{"PLN-b001", "PLN-b002", "PLN-b003", "PLN-b004"}] and plan.waits == [], run
