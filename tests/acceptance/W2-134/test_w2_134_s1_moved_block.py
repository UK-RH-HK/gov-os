"""W2-134, KPI S1 -- the measure re-anchors a line-cited gold source in memory for the commit it measures.

S1: before it scores, the measure finds each line-cited gold source's block again in the commit it measures: the
block is read at the source's own commit, found once at the measured root (as repin_gold.py finds it), and the
question is scored against those lines. A source whose block is unchanged keeps its lines.

The planted measured root (``w2_134_support``): ``docs/moved.md``'s cited block is lines 5-7 at commit 1 and lines
15-17 at commit 2 (10 lines inserted above it); the measure runs on commit 2. Red on today's code, save the unmoved
case (a guard, green by design): today the measure reads the stated lines at the measured root and re-anchors
nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_134_support as s  # noqa: E402

HIT_AT_2 = (True, 2, True, True, 1, 1)
HIT_AT_1 = (True, 1, True, True, 1, 1)
MISS = (False, None, False, False, 0, 1)


@pytest.fixture
def world(tmp_path):
    return s.World(tmp_path)


def _cite(world, form):
    """The moved block cited at commit 1's lines, by the question's own ``commit`` or by the source's."""
    if form == "question-commit":
        return [{"path": s.MOVED, "lines": list(s.MOVED_OLD)}], world.c1
    return [{"path": s.MOVED, "lines": list(s.MOVED_OLD), "commit": world.c1}], None


@pytest.mark.parametrize("form", ["question-commit", "source-commit"])
def test_s1_a_moved_block_is_scored_on_its_new_lines(world, form):
    """The evidence holds the moved lines (15-17) at rank 2: a hit at rank 2, full evidence 1 of 1."""
    sources, commit = _cite(world, form)
    world.question("m01", sources, [[world.item(s.OTHER, 1, 2), world.item(s.MOVED, *s.MOVED_NEW)]], commit=commit)
    doc, text, _ = world.run()
    assert s.figures(s.by_id(doc)["m01"]) == HIT_AT_2, f"{form}: the moved lines were not scored as the gold block"
    assert s.line_of(text, "m01").startswith("m01 (visible): hit@5 yes (first gold rank 2)"), s.line_of(text, "m01")
    assert doc["total"]["hit_at_5"]["count"] == 1


def test_s1_the_old_lines_of_a_moved_block_no_longer_count(world):
    """On commit 2 the old lines 5-7 hold inserted notes, not the block: evidence there is no hit (a commit is
    never scored against another commit's lines, failure line 2)."""
    sources, commit = _cite(world, "question-commit")
    world.question("m02", sources, [[world.item(s.MOVED, *s.MOVED_OLD)]], commit=commit)
    doc, text, _ = world.run()
    assert s.figures(s.by_id(doc)["m02"]) == MISS, "commit 1's lines were scored on commit 2"
    assert "hit@5 no" in s.line_of(text, "m02")


def test_s1_an_unmoved_block_keeps_its_lines(world):
    """``docs/steady.md`` changed below its cited block (3-4), which stays: evidence on 3-4 is a hit, evidence on
    the lines just below (5-6) is not. Green today by design: it guards that an unchanged block keeps its lines."""
    world.question("u01", [{"path": s.STEADY, "lines": list(s.STEADY_SPAN)}], [[world.item(s.STEADY, 3, 4)]],
                   commit=world.c1)
    world.question("u02", [{"path": s.STEADY, "lines": list(s.STEADY_SPAN), "commit": world.c1}],
                   [[world.item(s.STEADY, 5, 6)]])
    doc, _, _ = world.run()
    q = s.by_id(doc)
    assert s.figures(q["u01"]) == HIT_AT_1
    assert s.figures(q["u02"]) == MISS


def test_s1_a_family_member_holding_a_moved_block_s_text_is_a_hit(world):
    """The Contract's cited block (5-6 at commit 1) is at 11-12 on commit 2; the capability page CAP-7.md, a member
    of its family (W2-61h S7), holds that text. The family hit is judged against the re-anchored lines' text, so it
    is a hit at rank 1, named in the line."""
    world.question("f01", [{"path": s.CONTRACT, "lines": list(s.CONTRACT_OLD)}], [[world.item(s.CAP7, 1, 3)]],
                   commit=world.c1)
    doc, text, _ = world.run()
    assert s.figures(s.by_id(doc)["f01"]) == HIT_AT_1, "the family member was judged against commit 1's lines"
    assert s.names_family_hit(s.line_of(text, "f01"), s.CAP7), s.line_of(text, "f01")


def test_s1_kept_outputs_are_re_scored_on_the_moved_lines(world, tmp_path):
    """A run on commit 2 keeps its outputs (``00001.json`` ... beside ``.n``); re-scored with ``--kept`` and a
    retriever that answers nothing, the moved block is re-anchored too: a hit at rank 2, no retrieval asked."""
    sources, commit = _cite(world, "question-commit")
    world.question("k01", sources, [[world.item(s.OTHER, 1, 2), world.item(s.MOVED, *s.MOVED_NEW)]], commit=commit)
    kept = tmp_path / "runs" / "point" / "name-run1"
    kept.mkdir(parents=True)
    (kept / ".n").write_text("")
    (kept / ".n.lock").write_text("")
    world.respond(keep=kept)
    done = world.measure()
    assert done.returncode == 0, f"the measure failed (exit {done.returncode}): {done.stderr[-2000:]}"
    assert sorted(p.name for p in kept.glob("*.json")) == ["00001.json"]
    world.respond(trip=True)
    before = len(world.calls())
    doc, _, _ = world.run("--kept", str(kept))
    assert not [c for c in world.calls()[before:] if c[:1] == ["retrieve"]], "the re-score ran the retriever"
    assert s.figures(s.by_id(doc)["k01"]) == HIT_AT_2, "the kept outputs were scored on commit 1's lines"
