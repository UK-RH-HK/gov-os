"""W2-134, KPI S6 -- the output begins with the families in force (W2-61h S7's review, F3; DEC-1079).

S6: the measure's output begins with one line naming the families in force (each name and its member count, or
none), so a re-scored kept run says which families it used.

The line's form these cases assume (the designer's, the KPI names only its content):

    families: <name> (<n> members), <name> (<n> members)     # in the path map's order
    families: none

``1 member`` or ``1 members`` are both taken. It is the first line of the text run's standard output; with
``--json`` standard output stays one JSON document (``World.run`` parses it). In every plant here each member glob
matches exactly one file at the measured root, so a count of declared globs and a count of matched files agree: the
cases do not judge which the count is.

The kept case is the review's F3: the run was kept with no family declared anywhere; the sets root's path map then
declares the families while the measured root's committed path map still declares none (a pre-S7 clone), and the
re-score's first line names the families it scored with, which give the family hit.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_134_support as s  # noqa: E402

TWO = {"contract": [s.CONTRACT, "docs/contract/capabilities/*.md"], "notes": [s.OTHER]}
ENTRY = re.compile(r"(?P<name>[^\s,()]+) \((?P<n>\d+) members?\)")


def families_named(line: str) -> list[tuple[str, int]] | None:
    """The families a first line names, in order; ``[]`` for ``families: none``; None when it is no such line."""
    if line == "families: none":
        return []
    if not line.startswith("families: "):
        return None
    body = line[len("families: "):]
    entries = body.split(", ")
    found = [ENTRY.fullmatch(e) for e in entries]
    if not all(found):
        return None
    return [(m["name"], int(m["n"])) for m in found]


def _plant(world):
    """q01 a direct hit at rank 1; q02 the Contract's block held only by the capability page (a family hit when
    families are in force)."""
    w = world
    w.question("q01", [{"path": s.STEADY, "lines": list(s.STEADY_SPAN)}], [[w.item(s.STEADY, *s.STEADY_SPAN)]])
    w.question("q02", [{"path": s.CONTRACT, "lines": list(s.CONTRACT_OLD)}],
               [[w.item(s.OTHER, 1, 2), w.item(s.CAP7, 1, 3)]])


FAMILY_HIT = (True, 2, True, True, 1, 1)
NO_HIT = (False, None, False, False, 0, 1)

DECLARED = {
    "one-family": (s.FAMILIES, [("contract", 2)]),
    "two-families": (TWO, [("contract", 2), ("notes", 1)]),
}


@pytest.mark.parametrize("case", list(DECLARED))
def test_s6_the_first_line_names_the_families_in_force_with_their_member_counts(tmp_path, case):
    families, expected = DECLARED[case]
    w = s.World(tmp_path, second="steady", families=families)
    _plant(w)
    doc, text, _ = w.run()
    assert s.figures(s.by_id(doc)["q02"]) == FAMILY_HIT
    first = s.first_line(text)
    assert families_named(first) == expected, f"{case}: the output does not begin with the families: {first!r}"


def test_s6_with_no_family_declared_the_first_line_says_none(tmp_path):
    w = s.World(tmp_path, second="steady", families=None)
    _plant(w)
    doc, text, _ = w.run()
    assert s.figures(s.by_id(doc)["q02"]) == NO_HIT
    first = s.first_line(text)
    assert first == "families: none", f"the output does not begin with `families: none`: {first!r}"


@pytest.mark.parametrize("case", ["declared-in-the-sets-root", "none"])
def test_s6_a_kept_re_score_begins_with_the_families_it_used(tmp_path, case):
    w = s.World(tmp_path, second="steady", families=None)
    _plant(w)
    kept = tmp_path / "runs" / "point" / "name-run1"
    kept.mkdir(parents=True)
    (kept / ".n").write_text("")
    (kept / ".n.lock").write_text("")
    w.respond(keep=kept)
    done = w.measure()
    assert done.returncode == 0, f"the measure failed (exit {done.returncode}): {done.stderr[-2000:]}"
    if case == "declared-in-the-sets-root":
        w.set_sets_families(s.FAMILIES)
    w.respond(trip=True)
    before = len(w.calls())
    doc, text, _ = w.run("--kept", str(kept))
    assert not [c for c in w.calls()[before:] if c[:1] == ["retrieve"]], "the re-score ran the retriever"
    q02 = s.by_id(doc)["q02"]
    first = s.first_line(text)
    if case == "none":
        assert s.figures(q02) == NO_HIT
        assert first == "families: none", f"the re-score does not begin with `families: none`: {first!r}"
    else:
        assert s.figures(q02) == FAMILY_HIT
        assert s.names_family_hit(s.line_of(text, "q02"), s.CAP7), s.line_of(text, "q02")
        assert families_named(first) == [("contract", 2)], f"the re-score does not name its families: {first!r}"
