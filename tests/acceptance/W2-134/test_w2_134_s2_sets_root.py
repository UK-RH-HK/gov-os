"""W2-134, KPI S2 -- the measure never writes the sets root or any label file; each commit is scored against its
own lines.

S2: the measure never writes the sets root or any label file. Two measures on different commits, run one after the
other, score each commit against its own lines, and every file under a planted sets root is byte for byte as it was
(hashed before and after). Failure lines 1 and 2: a measure that writes a label file or the sets root; a commit
scored against another commit's lines.

The planted sets root is a plain folder outside the measured root (as ``~/gov-os-eval``), named by ``--sets-root``;
the in-tree form puts the label files in the measured root itself (no ``--sets-root``). The measured root is checked
out at commit 2, then commit 1, then commit 2 again, with no change to any label between the runs.

Expected on today's code: the own-lines case is red (on commit 2 today's measure scores commit 1's lines); the
byte-for-byte case is green by design (today's measure writes no label; it guards that the re-anchoring is done in
memory, never by rewriting a label as ``repin_gold.py --write`` does).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_134_support as s  # noqa: E402


def _plant(world):
    """old: evidence on lines 5-7 (the block's lines on commit 1); new: evidence on 15-17 (its lines on commit 2).
    Both cite the block at commit 1's lines 5-7. A hidden question cites the moved Contract block and the deleted
    block, so the hidden label is re-anchored and left unresolved too."""
    sources = [{"path": s.MOVED, "lines": list(s.MOVED_OLD)}]
    world.question("old", sources, [[world.item(s.MOVED, *s.MOVED_OLD, rev=world.c1)]], commit=world.c1)
    world.question("new", sources, [[world.item(s.MOVED, *s.MOVED_NEW, rev=world.c2)]], commit=world.c1)
    world.question("h01", [{"path": s.CONTRACT, "lines": list(s.CONTRACT_OLD), "commit": world.c1},
                           {"path": s.GONE, "lines": list(s.GONE_SPAN), "commit": world.c1}],
                   [[world.item(s.CONTRACT, *s.CONTRACT_NEW, rev=world.c2)]], part="hidden",
                   text=f"{s.MARK} question?", answer=f"{s.MARK} answer")


def _hits(doc):
    return {qid: q["hit_at_5"] for qid, q in s.by_id(doc).items()}


def test_s2_two_measures_on_two_commits_score_each_against_its_own_lines(tmp_path):
    world = s.World(tmp_path)
    _plant(world)
    want = {world.c2: {"old": False, "new": True}, world.c1: {"old": True, "new": False}}
    for rev in (world.c2, world.c1, world.c2):
        world.checkout(rev)
        doc, text, _ = world.run()
        assert rev.startswith(str(doc["commit"])), f"the record names {doc['commit']}, not the measured {rev}"
        got = _hits(doc)
        assert got == want[rev], f"on {'commit 2' if rev == world.c2 else 'commit 1'}: {got}, want {want[rev]}"
        for qid, hit in want[rev].items():
            assert f"hit@5 {'yes' if hit else 'no'}" in s.line_of(text, qid), s.line_of(text, qid)


@pytest.mark.parametrize("layout", ["sets-root", "in-tree"])
def test_s2_every_file_under_the_sets_root_is_byte_for_byte_as_it_was(tmp_path, layout):
    world = s.World(tmp_path, in_tree=layout == "in-tree")
    _plant(world)
    before = world.label_state()
    assert len([p for p in before if p.endswith(".yaml")]) >= 4, sorted(before)   # three labels and the path map
    for rev in (world.c2, world.c1):
        world.checkout(rev)
        for extra in (("--json",), ()):
            done = world.measure(*extra, part="all")
            assert done.returncode == 0, f"the measure failed (exit {done.returncode}): {done.stderr[-2000:]}"
    after = world.label_state()
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(p for p in set(before) & set(after) if before[p] != after[p])
    assert not (added or removed or changed), (f"the measure wrote the sets root: added {added}, removed {removed}, "
                                               f"changed {changed}")
