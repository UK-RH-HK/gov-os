"""W2-147 unit tests: gov plan breaks a cycle only inside it (DEC-1102), on planted ticket stores (S1-S4)."""

from __future__ import annotations

import re

from gov.plan.derive import Context, _order, hard_waits
from gov.plan.tickets import load

from .w2_136_store import plant, run, run_json, ticket


def batches(out: str) -> list[list[str]]:
    return [line.split(": ", 1)[1].split(", ") for line in out.splitlines() if re.match(r"batch \d+: ", line)]


def tiebreaks(out: str) -> list[str]:
    return [line for line in out.splitlines() if "(CYCLE_TIEBREAK " in line]


def same_in_two_orders(tmp_path, capsys, tickets, shuffled) -> tuple[str, dict]:
    """The text and --json of ``tickets`` planted in their own order and in ``shuffled``; both must be equal."""
    one = plant(tmp_path / "one", *tickets)
    two = plant(tmp_path / "two", *tickets, order=shuffled)
    texts = [run(root, capsys)[1] for root in (one, two)]
    jsons = [run(root, capsys, "--json")[1] for root in (one, two)]
    assert texts[0] == texts[1]
    assert jsons[0] == jsons[1]
    return texts[0], run_json(one, capsys)[1]["result"]


# -- S1: the break falls inside the cycle --------------------------------------------------------------------------

def outside_waiter():
    return [ticket("T-1", waits_on=["T-2"]), ticket("T-2", waits_on=["T-1"]),
            ticket("T-3", priority=0, waits_on=["T-1"])]  # T-3 sorts first by the key but is in no cycle


def test_a_cycle_with_an_outside_waiter_is_broken_inside_the_cycle(tmp_path, capsys):
    out, data = same_in_two_orders(tmp_path, capsys, outside_waiter(), [2, 1, 0])
    assert tiebreaks(out) == ["T-2 waits for T-1 (CYCLE_TIEBREAK WAITS_ON T-2)"]
    assert "T-3 waits for T-1 (WAITS_ON T-1)" in out
    broken = [w for w in data["waits"] if w["code"] == "CYCLE_TIEBREAK"]
    assert broken == [{"ticket": "T-2", "waits_for": "T-1", "code": "CYCLE_TIEBREAK", "what": "WAITS_ON T-2"}]


def test_an_outside_ticket_the_cycle_waits_on_is_never_broken(tmp_path, capsys):
    out, _ = same_in_two_orders(tmp_path, capsys, [
        ticket("T-1", waits_on=["T-2", "T-9"]), ticket("T-2", waits_on=["T-1"]),
        ticket("T-9", priority=5)], [1, 2, 0])
    assert tiebreaks(out) == ["T-2 waits for T-1 (CYCLE_TIEBREAK WAITS_ON T-2)"]
    assert "T-1 waits for T-9 (WAITS_ON T-9)" in out
    assert batches(out) == [["T-9"], ["T-1"], ["T-2"]]


# -- S2: a ticket outside every cycle keeps all its waits -----------------------------------------------------------

def test_the_outside_waiter_is_batched_after_what_it_waits_on(tmp_path, capsys):
    out, _ = same_in_two_orders(tmp_path, capsys, outside_waiter(), [1, 2, 0])
    assert batches(out) == [["T-1"], ["T-3", "T-2"]]


def test_the_case_seen_on_2026_11_09_keeps_w2_27_s_wait_on_w2_88(tmp_path, capsys):
    seen = [ticket("T-27", wbs="W2-27", waits_on=["W2-88"]), ticket("T-88", wbs="W2-88", waits_on=["W2-145"]),
            ticket("T-137", wbs="W2-137", waits_on=["W2-145"]), ticket("T-145", wbs="W2-145", waits_on=["W2-137"])]
    out, data = same_in_two_orders(tmp_path, capsys, seen, [3, 1, 0, 2])
    assert "T-27 waits for T-88 (WAITS_ON W2-88)" in out
    assert "T-88 waits for T-145 (WAITS_ON W2-145)" in out
    assert tiebreaks(out) == ["T-145 waits for T-137 (CYCLE_TIEBREAK WAITS_ON W2-145)"]
    assert batches(out) == [["T-137"], ["T-145"], ["T-88"], ["T-27"]]
    assert data["batch_wbs"] == [["W2-137"], ["W2-145"], ["W2-88"], ["W2-27"]]


# -- S3: deterministic and named ------------------------------------------------------------------------------------

def test_the_break_is_counted_in_the_codes_and_the_waits(tmp_path, capsys):
    out, data = same_in_two_orders(tmp_path, capsys, outside_waiter(), [0, 2, 1])
    assert out.splitlines()[0] == "gov plan: 3 tickets, 2 batches, 3 waits (CYCLE_TIEBREAK, WAITS_ON)"
    assert "CYCLE_TIEBREAK" in data["codes"]


def test_a_needs_cycle_breaks_at_its_first_ticket_by_the_key_as_before(tmp_path, capsys):
    out, _ = same_in_two_orders(tmp_path, capsys, [
        ticket("T-1", priority=2, writes=["src/a.py"], needs=["src/b.py"]),
        ticket("T-2", priority=1, writes=["src/b.py"], needs=["src/a.py"])], [1, 0])
    assert batches(out) == [["T-2"], ["T-1"]]
    assert tiebreaks(out) == ["T-1 waits for T-2 (CYCLE_TIEBREAK NEEDS_WHAT_WRITES src/a.py)"]


# -- S4: two cycles, a self-loop, no cycle ---------------------------------------------------------------------------

def test_two_separate_cycles_are_each_broken_once_inside_themselves(tmp_path, capsys):
    out, _ = same_in_two_orders(tmp_path, capsys, [
        ticket("T-1", waits_on=["T-2"]), ticket("T-2", waits_on=["T-1"]),
        ticket("T-3", waits_on=["T-4", "T-1"]), ticket("T-4", waits_on=["T-3"]),
        ticket("T-5", priority=0, waits_on=["T-4"])], [4, 3, 2, 1, 0])
    assert tiebreaks(out) == ["T-2 waits for T-1 (CYCLE_TIEBREAK WAITS_ON T-2)",
                              "T-4 waits for T-3 (CYCLE_TIEBREAK WAITS_ON T-4)"]
    assert "T-3 waits for T-1 (WAITS_ON T-1)" in out   # the wait between the cycles is kept
    assert "T-5 waits for T-4 (WAITS_ON T-4)" in out   # the outside waiter's too
    assert batches(out) == [["T-1"], ["T-2", "T-3"], ["T-4"], ["T-5"]]


def test_two_unlinked_cycles_are_broken_once_each(tmp_path, capsys):
    out, _ = same_in_two_orders(tmp_path, capsys, [
        ticket("T-1", waits_on=["T-2"]), ticket("T-2", waits_on=["T-1"]),
        ticket("T-3", waits_on=["T-4"]), ticket("T-4", waits_on=["T-3"])], [3, 1, 2, 0])
    assert tiebreaks(out) == ["T-2 waits for T-1 (CYCLE_TIEBREAK WAITS_ON T-2)",
                              "T-4 waits for T-3 (CYCLE_TIEBREAK WAITS_ON T-4)"]
    assert batches(out) == [["T-1", "T-3"], ["T-2", "T-4"]]


def test_a_self_loop_is_broken_at_that_ticket_and_named(tmp_path, capsys):
    out, data = same_in_two_orders(tmp_path, capsys, [
        ticket("T-1", waits_on=["T-1"]), ticket("T-2", priority=0, waits_on=["T-1"])], [1, 0])
    assert tiebreaks(out) == ["T-1 waits for T-1 (CYCLE_TIEBREAK WAITS_ON T-1)"]
    assert "T-2 waits for T-1 (WAITS_ON T-1)" in out
    assert batches(out) == [["T-1"], ["T-2"]]
    assert "CYCLE_TIEBREAK" in data["codes"]


def test_the_launch_check_s_waits_still_leave_a_self_wait_out(tmp_path):
    plant(tmp_path, ticket("T-1", waits_on=["T-1"]))
    ctx = Context(tmp_path, load(tmp_path))
    assert hard_waits(ctx.tickets["T-1"], ctx) == []
    assert [w.on for w in hard_waits(ctx.tickets["T-1"], ctx, self_loop=True)] == ["T-1"]


def test_a_three_ticket_cycle_breaks_only_its_first_ticket_s_waits_from_inside(tmp_path, capsys):
    out, _ = same_in_two_orders(tmp_path, capsys, [
        ticket("T-1", waits_on=["T-3"]), ticket("T-2", waits_on=["T-1"]), ticket("T-3", waits_on=["T-2"]),
        ticket("T-0", priority=0, waits_on=["T-2"])], [2, 3, 0, 1])
    assert tiebreaks(out) == ["T-3 waits for T-1 (CYCLE_TIEBREAK WAITS_ON T-3)"]
    assert batches(out) == [["T-1"], ["T-2"], ["T-0", "T-3"]]


def test_order_breaks_a_downstream_cycle_only_after_its_upstream_one():
    rank = {n: i for i, n in enumerate(["x", "y", "a", "b"])}
    edges = {("a", "b"): ["a"], ("b", "a"): ["b"], ("y", "x"): ["y"], ("x", "y"): ["x"], ("a", "x"): ["ax"]}
    order, broken = _order(list(rank), edges, rank)
    assert order == ["a", "b", "x", "y"]
    assert sorted(broken) == [("b", "a"), ("y", "x")]


NO_CYCLE = [
    ticket("T-1", writes=["src/a.py"]),
    ticket("T-2", writes=["src/a.py", "src/b.py"], needs=["src/c.py"], reads=["src/d.py"]),
    ticket("T-3", priority=2, writes=["src/c.py"], depends_on=["T-1"]),
    ticket("T-4", wbs="W9-10", writes=["src/d.py"], waits_on=["T-3", "rec.md"]),
    ticket("T-5", writes=["src/a.py"], plan_override="DEC-899 the owner's exception"),
    ticket("T-6", status="in_progress", writes=["src/e.py"], waits_on=["T-2"]),
    ticket("T-7", writes=["src/f.py"], needs=None, depends_on=["T-4"], deps=[]),
    ticket("T-8", writes=["src/g.py"], waits_on=["open.md"]),
    ticket("T-9", writes=["src/h.py"], depends_on=["T-8"]),
]
NO_CYCLE_TEXT = (  # pinned from integrate's derive.py (003f0bc23d47) for NO_CYCLE
    "gov plan: 9 tickets, 4 batches, 8 waits (DEPENDS_ON, DEPS_DISAGREE, NEEDS_UNDECLARED, NEEDS_WHAT_WRITES, "
    "OVERRIDE, READS_WIDE, WAITS_ON, WRITES_OVERLAP)\n"
    "batch 1: T-1, T-5\n"
    "batch 2: T-3\n"
    "batch 3: T-2, T-4\n"
    "batch 4: T-6, T-7\n"
    "T-3 waits for T-1 (DEPENDS_ON T-1)\n"
    "T-2 waits for T-1 (WRITES_OVERLAP src/a.py)\n"
    "T-2 waits for T-3 (NEEDS_WHAT_WRITES src/c.py)\n"
    "T-4 waits for T-3 (WAITS_ON T-3)\n"
    "T-6 waits for T-2 (WAITS_ON T-2)\n"
    "T-7 waits for T-4 (DEPENDS_ON T-4)\n"
    "T-8 waits for open.md (WAITS_ON open.md)\n"
    "T-9 waits for T-8 (DEPENDS_ON T-8)\n"
    "held: T-8, T-9 (a wait outside the plan is not met)\n"
    "T-5 overrides its wait for T-1 (OVERRIDE DEC-899 WRITES_OVERLAP src/a.py)\n"
    "T-5 overrides its wait for T-2 (OVERRIDE DEC-899 WRITES_OVERLAP src/a.py)\n"
    "T-2 warning READS_WIDE (reads: would have made it wait for T-4; it orders nothing)\n"
    "T-7 finding NEEDS_UNDECLARED (no needs: declared; planned as needing only its own writes)\n"
    "T-7 finding DEPS_DISAGREE (deps [] but depends_on [T-4])\n"
)


def test_with_no_cycle_the_output_is_byte_identical_to_integrate_s(tmp_path, capsys):
    plant(tmp_path, *NO_CYCLE)
    (tmp_path / "rec.md").write_text("---\nstatus: closed\n---\n", encoding="utf-8")
    (tmp_path / "open.md").write_text("---\nstatus: open\n---\n", encoding="utf-8")
    out = run(tmp_path, capsys)[1]
    assert out == NO_CYCLE_TEXT
