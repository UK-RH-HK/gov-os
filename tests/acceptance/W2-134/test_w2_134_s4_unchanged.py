"""W2-134, KPI S4 -- nothing else changes.

S4: with every cited block unmoved, the per-question lines and totals equal today's output for the same run, and
source families (W2-61h S7) are scored as before.

The planted measured root's second commit is the *steady* one: it appends lines at the ends of files and adds a
file, so no cited block moves. Every source cites commit 1 (the question's ``commit`` or the source's own), save
q06, which names no commit. The expected lines and total are today's output for this run, recorded from the
integrated measure on this branch (``w2/W2-61h-s7`` with ``w2/integrate``, 2026-11-06): green today by design.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_134_support as s  # noqa: E402

TODAY_LINES = {
    "q01": "q01 (visible): hit@5 yes (first gold rank 2), in the bundle yes; full evidence yes (1 of 1 pieces); 1 calls",
    "q02": "q02 (visible): hit@5 yes (first gold rank 1), in the bundle yes; full evidence no (1 of 2 pieces); 1 calls",
    "q03": "q03 (visible): hit@5 no (first gold rank 6), in the bundle yes; full evidence yes (1 of 1 pieces); 1 calls",
    "q04": "q04 (visible): hit@5 yes (first gold rank 1), in the bundle yes; full evidence yes (1 of 1 pieces); 1 calls;"
           " family hit: docs/contract/capabilities/CAP-7.md",
    "q05": "q05 (visible): hit@5 no (first gold rank -), in the bundle no; full evidence no (0 of 1 pieces); 1 calls",
    "q06": "q06 (visible): hit@5 yes (first gold rank 1), in the bundle yes; full evidence yes (1 of 1 pieces); 1 calls",
}
TODAY_TOTAL = "total: hit@5 4 of 6 (66.7 %, floor 85); full evidence 4 of 6 (66.7 %, target 99 %)"
TODAY_FIGURES = {
    "q01": (True, 2, True, True, 1, 1),
    "q02": (True, 1, True, False, 1, 2),
    "q03": (False, 6, True, True, 1, 1),
    "q04": (True, 1, True, True, 1, 1),
    "q05": (False, None, False, False, 0, 1),
    "q06": (True, 1, True, True, 1, 1),
}


def _plant(world):
    """q01 a line-cited block at rank 2; q02 a heading and a whole file, one found; q03 a line-cited block (its
    source's own commit) at rank 6; q04 a family hit on the Contract's line-cited block; q05 a miss; q06 a
    line-cited block with no commit named."""
    w, c1 = world, world.c1
    w.question("q01", [{"path": s.MOVED, "lines": list(s.MOVED_OLD)}],
               [[w.item(s.OTHER, 1, 2), w.item(s.MOVED, *s.MOVED_OLD)]], commit=c1)
    w.question("q02", [{"path": s.STEADY, "heading": "## End"}, {"path": s.OTHER}], [[w.item(s.STEADY, 6, 7)]],
               commit=c1)
    w.question("q03", [{"path": s.GONE, "lines": list(s.GONE_SPAN), "commit": c1}],
               [[w.item(s.OTHER, n, n) for n in range(1, 6)] + [w.item(s.GONE, *s.GONE_SPAN)]])
    w.question("q04", [{"path": s.CONTRACT, "lines": list(s.CONTRACT_OLD)}], [[w.item(s.CAP7, 1, 3)]], commit=c1)
    w.question("q05", [{"path": s.STEADY, "lines": list(s.STEADY_SPAN)}], [[w.item(s.OTHER, 1, 2)]], commit=c1)
    w.question("q06", [{"path": s.MOVED, "lines": list(s.MOVED_OLD)}], [[w.item(s.MOVED, 6, 6)]])


@pytest.fixture
def world(tmp_path):
    w = s.World(tmp_path, second="steady")
    _plant(w)
    return w


def test_s4_with_every_cited_block_unmoved_the_lines_and_totals_are_today_s(world):
    doc, text, _ = world.run()
    q = s.by_id(doc)
    assert {qid: s.figures(one) for qid, one in q.items()} == TODAY_FIGURES
    assert q["q04"]["family_hits"] == [s.CAP7], q["q04"]
    assert (doc["total"]["questions"], doc["total"]["hit_at_5"]["count"], doc["total"]["full_evidence"]["count"]) == (
        6, 4, 4)
    for qid, line in TODAY_LINES.items():
        assert s.line_of(text, qid) == line
    assert s.total_line(text) == TODAY_TOTAL


def test_s4_kept_outputs_re_score_as_the_run_with_families(world, tmp_path):
    """The run's kept outputs, re-scored with ``--kept`` and a retriever that answers nothing (W2-61h S7), give the
    same lines and total as today's run, the family hit among them."""
    kept = tmp_path / "runs" / "point" / "name-run1"
    kept.mkdir(parents=True)
    (kept / ".n").write_text("")
    (kept / ".n.lock").write_text("")
    world.respond(keep=kept)
    done = world.measure()
    assert done.returncode == 0, f"the measure failed (exit {done.returncode}): {done.stderr[-2000:]}"
    world.respond(trip=True)
    doc, text, _ = world.run("--kept", str(kept))
    assert {qid: s.figures(one) for qid, one in s.by_id(doc).items()} == TODAY_FIGURES
    for qid, line in TODAY_LINES.items():
        assert s.line_of(text, qid) == line
    assert s.total_line(text) == TODAY_TOTAL
