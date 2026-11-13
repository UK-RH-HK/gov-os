"""S1: gov plan --open reads every open and in-progress ticket and prints the batches and the waits; --json gives the
same in the shared envelope; exit 0 a plan, 1 a plan with findings, 2 cannot run (DEC-1088 (1), DEC-1087 (5))."""

from __future__ import annotations

import pytest

import w2_136_support as support
from w2_136_support import T

A = T("PLN-a001", "W2-201", status="in_progress", priority=1, writes=("src/lib/core.py",))
B = T("PLN-a002", "W2-202", writes=("src/app/**",), needs=("src/lib/core.py",))
C = T("PLN-a003", "W2-203", writes=("src/c/**",), depends_on=("PLN-a001",))
D = T("PLN-a004", "W2-204", writes=("src/d/**",))
Z = T("PLN-a009", "W2-209", status="closed", writes=("src/z/**",))
STORE = (A, B, C, D, Z)
FILES = ("src/lib/core.py", "src/app/main.py", "src/c/c.py", "src/d/d.py", "src/z/z.py")
BATCHES = [{"PLN-a001", "PLN-a004"}, {"PLN-a002", "PLN-a003"}]
TRIPLES = {("PLN-a002", "PLN-a001", "NEEDS_WHAT_WRITES"), ("PLN-a003", "PLN-a001", "DEPENDS_ON")}


def test_s1_the_text_plan_gives_the_first_line_the_batches_and_the_named_waits(planted):
    store = planted(STORE, FILES)
    run = support.run(store.root, "--open")
    assert run.code == 0, run
    plan = support.text_plan(run.out, store, run)
    assert (plan.n, plan.b, plan.w) == (4, 2, 2), run  # the closed PLN-a009 is not planned
    assert {"NEEDS_WHAT_WRITES", "DEPENDS_ON"} <= plan.codes, run
    assert plan.batches == BATCHES, run
    assert plan.triples == TRIPLES, run
    on = {waiter: on for waiter, _, _, on in plan.waits}
    assert "src/lib/core.py" in on["PLN-a002"], run      # the path it needs
    assert store.mentions(on["PLN-a003"], "PLN-a001"), run  # the ticket it depends on


def test_s1_json_gives_the_same_plan_in_the_shared_envelope(planted):
    store = planted(STORE, FILES)
    text = support.text_plan(support.run(store.root, "--open").out, store)
    run = support.run(store.root, "--open", "--json")
    assert run.code == 0, run
    data = support.envelope(run)
    assert data["ok"] is True and data["command"] == "plan", run
    plan = support.json_plan(data["result"], store)
    assert plan.batches == text.batches == BATCHES, run
    assert plan.triples == text.triples == TRIPLES, run
    assert plan.n in (None, 4), run
    needs = [w for w in data["result"]["waits"] if w.get("code") == "NEEDS_WHAT_WRITES"]
    assert needs and "src/lib/core.py" in support.strings(needs[0]), run


@pytest.mark.parametrize("form", ["text", "json"])
def test_s1_a_plan_with_findings_exits_1_and_still_gives_the_plan(planted, form):
    undeclared = T("PLN-a005", "W2-205", writes=("src/e/**",), needs=None)  # no needs: NEEDS_UNDECLARED (S5)
    store = planted((*STORE, undeclared), FILES)
    run = support.run(store.root, "--open", *(["--json"] if form == "json" else []))
    assert run.code == 1, run
    if form == "text":
        plan = support.text_plan(run.out, store, run)
    else:
        plan = support.json_plan(support.envelope(run)["result"], store)
    assert plan.batches == [BATCHES[0] | {"PLN-a005"}, BATCHES[1]], run


@pytest.mark.parametrize("form", ["text", "json"])
def test_s1_no_ticket_store_cannot_run_and_exits_2(planted, form):
    flags = ["--json"] if form == "json" else []
    good = planted(STORE, FILES)
    first = support.run(good.root, "--open", *flags)
    assert first.code == 0, first  # the command exists and plans a store: the 2 below is gov plan's own
    bare = planted((), ("src/x.py",), name="bare", with_tickets=False)
    run = support.run(bare.root, "--open", *flags)
    assert run.code == 2, run
