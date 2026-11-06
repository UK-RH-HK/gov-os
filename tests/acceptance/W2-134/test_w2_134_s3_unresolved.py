"""W2-134, KPI S3 -- a source whose block cannot be found at the measured root is named by id and entry number
only, and counts as not found.

S3: a source whose block cannot be found at the measured root is named by question id and entry number only (never
its text, path or lines), and counts as not found. Failure line 3: label text, path or lines printed for an
unresolved hidden source.

The planted source ``docs/zqxw134hidden/gone.md`` cites lines 73-77 at commit 1; commit 2 deletes those five lines,
so on commit 2 the stated lines 73-77 still lie in the file but hold other text. Every word of the label (its
question, its answer, the source's path and the block) holds ``zqxw134hidden``; the output is searched for that,
for ``gone.md`` and for the numbers 73 and 77 standing alone.

- ``x01``: entry 1 is the steady block (found, rank 1), entry 2 the deleted one; the evidence holds both stated
  spans. Hit at rank 1, full evidence 1 of 2; ``x01`` and ``entry 2`` named.
- ``x02``: its one source is the deleted block; the evidence holds its stated span. No hit, 0 of 1; ``entry 1``.

Red on today's code: today the stated lines are read at the measured root, so the evidence on 73-77 counts as found
(x01 full evidence 2 of 2, x02 a hit) and nothing names the unresolved sources.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_134_support as s  # noqa: E402

LONE_LINE_NUMBERS = re.compile(r"(?<![\w.])(73|77)(?![\w])")


@pytest.mark.parametrize("part", ["hidden", "visible"])
def test_s3_a_deleted_block_counts_as_not_found_and_is_named_by_id_and_entry_only(tmp_path, part):
    world = s.World(tmp_path)
    steady = {"path": s.STEADY, "lines": list(s.STEADY_SPAN)}
    gone = {"path": s.GONE, "lines": list(s.GONE_SPAN)}
    world.question("x01", [steady, gone], [[world.item(s.STEADY, *s.STEADY_SPAN), world.item(s.GONE, *s.GONE_SPAN)]],
                   part=part, commit=world.c1, text=f"{s.MARK} question one?", answer=f"{s.MARK} answer one")
    world.question("x02", [{**gone, "commit": world.c1}], [[world.item(s.GONE, *s.GONE_SPAN)]], part=part,
                   text=f"{s.MARK} question two?", answer=f"{s.MARK} answer two")
    doc, text, stderr = world.run(part=part)
    q = s.by_id(doc)
    assert s.figures(q["x01"]) == (True, 1, True, False, 1, 2), "the deleted block was counted as found"
    assert s.figures(q["x02"]) == (False, None, False, False, 0, 1), "the deleted block was counted as found"

    named = text + "\n" + stderr
    assert s.names_entry(named, "x01", 2), f"x01 entry 2 is not named:\n{named}"
    assert s.names_entry(named, "x02", 1), f"x02 entry 1 is not named:\n{named}"
    assert not s.names_entry(named, "x01", 1), f"x01's entry 1 (found) is named as unresolved:\n{named}"

    for name, output in (("the text", text), ("stderr", stderr), ("the record", json.dumps(doc))):
        for base in (str(tmp_path.resolve()), str(tmp_path)):   # the planted folders' own path (pytest numbers it)
            output = output.replace(base, "<tmp>")
        assert s.MARK not in output, f"{name} shows the label's text or path"
        assert "gone.md" not in output, f"{name} shows the source's path"
        assert not LONE_LINE_NUMBERS.search(output), f"{name} shows the source's lines"
