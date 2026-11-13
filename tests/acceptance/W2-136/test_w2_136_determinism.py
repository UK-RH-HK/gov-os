"""S4: deterministic. The same tickets give byte-identical output in any file order; ties and cycles are broken by
priority (the lower number first, as tk's priority 0 is the highest), then WBS order, then id, and named
CYCLE_TIEBREAK (DEC-1088 (1))."""

from __future__ import annotations

import os
import shutil

import pytest

import w2_136_support as support
from w2_136_support import T

MIXED = (
    T("PLN-d001", "W2-401", status="in_progress", priority=1, writes=("src/lib/core.py",)),
    T("PLN-d002", "W2-402", writes=("src/app/**",), needs=("src/lib/core.py",)),
    T("PLN-d003", "W2-403", writes=("src/w/**",)),
    T("PLN-d004", "W2-404", priority=3, writes=("src/w/x.py",)),
    T("PLN-d005", "W2-405", writes=("src/e/**",), depends_on=("PLN-d003",)),
    T("PLN-d006", "W2-406", writes=("docs/f.md",), reads=("src/**",)),
    T("PLN-d007", "W2-407", writes=("src/g/**",), needs=None),
    T("PLN-d008", "W2-408", writes=("src/w/y.py",), plan_override="DEC-899"),
    T("PLN-d009", "W2-409", status="closed", writes=("src/z/**",)),
)
FILES = ("src/lib/core.py", "src/w/x.py", "src/w/y.py")
ORDERS = [list(range(len(MIXED))), list(reversed(range(len(MIXED)))), [4, 0, 8, 2, 6, 1, 7, 3, 5]]


@pytest.mark.parametrize("form", ["text", "json"])
def test_s4_two_runs_on_the_same_tickets_are_byte_identical(planted, form):
    store = planted(MIXED, FILES)
    flags = ["--json"] if form == "json" else []
    first, second = support.run(store.root, "--open", *flags), support.run(store.root, "--open", *flags)
    assert first.code in (0, 1) and first.out.startswith(("gov plan:", "{")), first
    assert (first.code, first.out) == (second.code, second.out)


@pytest.mark.parametrize("form", ["text", "json"])
def test_s4_the_same_tickets_written_in_shuffled_file_orders_give_byte_identical_output(tmp_path, form):
    flags = ["--json"] if form == "json" else []
    root, outs = tmp_path / "repo", []
    for order in ORDERS:  # rebuilt at the same path, so neither the root nor the commit (fixed date) differs
        if root.exists():
            shutil.rmtree(root)
        store = support.build(root, MIXED, FILES, order)
        for i, tid in enumerate(store.tickets):  # mtimes in another order too
            os.utime(store.path(tid), (1_700_000_000 + 7 * ((i * 5 + len(outs)) % 9),) * 2)
        outs.append(support.run(root, "--open", *flags))
    assert outs[0].code in (0, 1) and outs[0].out.startswith(("gov plan:", "{")), outs[0]
    assert all((o.code, o.out) == (outs[0].code, outs[0].out) for o in outs), "\n=====\n".join(map(str, outs))


@pytest.mark.parametrize("form", ["text", "json"])
def test_s4_a_reversed_listing_of_the_ticket_folder_gives_byte_identical_output(planted, monkeypatch, capsys, form):
    """In process: every listing of the ``.tickets`` folder (os.listdir, os.scandir, and so Path.iterdir, Path.glob
    and glob) comes back reversed."""
    from gov.cli import main as cli

    store = planted(MIXED, FILES)
    for key in [k for k in os.environ if k.startswith(("GOV_", "GIT_"))]:
        monkeypatch.delenv(key)
    argv = ["plan", "--open", "--root", str(store.root), *(["--json"] if form == "json" else [])]

    def once():
        try:
            code = cli.main(list(argv))
        except SystemExit as stop:
            code = stop.code
        return code, capsys.readouterr().out

    plain = once()
    listdir, scandir = os.listdir, os.scandir

    def tickets_folder(path):
        return os.path.basename(os.path.normpath(os.fsdecode(path if path is not None else "."))) == ".tickets"

    def reversed_listdir(path="."):
        names = listdir(path)
        return list(reversed(names)) if tickets_folder(path) else names

    class Reversed:
        def __init__(self, items):
            self.items = items

        def __iter__(self):
            return iter(self.items)

        def __next__(self):
            raise StopIteration

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def close(self):
            pass

    def reversed_scandir(path="."):
        if not isinstance(path, int) and tickets_folder(path):
            with scandir(path) as found:
                return Reversed(list(reversed(list(found))))
        return scandir(path)

    monkeypatch.setattr(os, "listdir", reversed_listdir)
    monkeypatch.setattr(os, "scandir", reversed_scandir)
    shuffled = once()
    monkeypatch.undo()
    assert plain[0] in (0, 1) and plain[1].startswith(("gov plan:", "{")), plain
    assert shuffled == plain


def _first(planted, a, b, files=()):
    """The two tickets' writes overlap: which goes first, and the plan."""
    store = planted((a, b), files)
    run = support.run(store.root, "--open")
    assert run.code in (0, 1), run  # the exit code is S1's and S5's matter, not the order's
    plan = support.text_plan(run.out, store, run)
    assert len(plan.batches) == 2 and all(len(batch) == 1 for batch in plan.batches), run
    return next(iter(plan.batches[0])), plan, run


@pytest.mark.parametrize("high, low", [("PLN-d011", "PLN-d012"), ("PLN-d012", "PLN-d011")])
def test_s4_an_overlap_tie_goes_by_priority_first(planted, high, low):
    """The WBS order and the id order point the other way where PLN-d012 is the higher priority."""
    prio = {high: 0, low: 3}
    a = T("PLN-d011", "W2-411", priority=prio["PLN-d011"], writes=("src/t/**",))
    b = T("PLN-d012", "W2-412", priority=prio["PLN-d012"], writes=("src/t/x.py",))
    first, plan, run = _first(planted, a, b)
    assert first == high, run
    assert plan.triples == {(low, high, "WRITES_OVERLAP")}, run


def test_s4_an_overlap_tie_of_equal_priority_goes_by_wbs_order_before_the_id(planted):
    a = T("PLN-d029", "W2-421", priority=2, writes=("src/t/**",))   # the earlier WBS id, the later ticket id
    b = T("PLN-d021", "W2-422", priority=2, writes=("src/t/x.py",))
    first, plan, run = _first(planted, a, b)
    assert first == "PLN-d029", run


def test_s4_an_overlap_tie_of_equal_priority_and_no_wbs_id_goes_by_the_id(planted):
    a = T("PLN-d032", None, priority=2, writes=("src/t/**",))
    b = T("PLN-d031", None, priority=2, writes=("src/t/x.py",))
    first, plan, run = _first(planted, a, b)
    assert first == "PLN-d031", run


@pytest.mark.parametrize("winner, prio", [("PLN-d041", {"PLN-d041": 1, "PLN-d042": 2}),
                                          ("PLN-d042", {"PLN-d041": 2, "PLN-d042": 1}),
                                          ("PLN-d041", {"PLN-d041": 2, "PLN-d042": 2})],
                         ids=["by-priority", "by-priority-swapped", "equal-priority-by-wbs-order"])
def test_s4_a_needs_after_write_cycle_is_broken_by_the_key_and_named_cycle_tiebreak(planted, winner, prio):
    a = T("PLN-d041", "W2-431", priority=prio["PLN-d041"], writes=("src/ca.py",), needs=("src/cb.py",))
    b = T("PLN-d042", "W2-432", priority=prio["PLN-d042"], writes=("src/cb.py",), needs=("src/ca.py",))
    store = planted((a, b), ("src/ca.py", "src/cb.py"))
    run = support.run(store.root, "--open")
    assert run.code in (0, 1), run
    plan = support.text_plan(run.out, store, run)
    loser = ({"PLN-d041", "PLN-d042"} - {winner}).pop()
    assert plan.batches == [{winner}, {loser}], run
    assert any(w == (loser, winner) for w in [(x, y) for x, y, _, _ in plan.waits]), run
    assert "CYCLE_TIEBREAK" in run.out, run
    data = support.envelope(support.run(store.root, "--open", "--json"))
    named = support.entries(data["result"], "CYCLE_TIEBREAK")
    assert named and any(support.json_mentions(store, e, winner) or support.json_mentions(store, e, loser)
                         for e in named), data
