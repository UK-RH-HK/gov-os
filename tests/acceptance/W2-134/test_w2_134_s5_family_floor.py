"""W2-134, KPI S5 -- a family hit needs a gold of at least 4 words and 24 characters, matched on word boundaries
(W2-61h S7's review, F1; DEC-1079, DEC-1078 (4)).

S5: a source-family hit needs the gold span's normalised text to be at least 4 words and 24 characters, matched on
word boundaries (no hit inside a longer token: CAP-1 never matches CAP-10, DEC-1078 never DEC-1079, 85 never 1985);
a gold below the floor counts only in its own path, as with no family. Failure line: a family hit on text that holds
the gold only inside a longer token, or on a gold below the floor.

The planted measured root is W2-134's steady world plus a third commit holding the review's probe files. Every gold
here is a line-cited source that names no commit, so it is scored on its stated lines at the measured root, as
today: these cases judge the family rule alone, apart from S1's re-anchoring. Each run carries a control question
whose gold (well above the floor) is held by a member: a family hit, so a case cannot pass by families not being
counted at all.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_134_support as s  # noqa: E402

YAML = "docs/contract/contract.yaml"
V4 = "docs/contract/CONTRACT_v4.md"
CAP1 = "docs/contract/capabilities/CAP-1.md"
CAP3 = "docs/contract/capabilities/CAP-3.md"
CAP10 = "docs/contract/capabilities/CAP-10.md"
CAP11 = "docs/contract/capabilities/CAP-11.md"
CAP12 = "docs/contract/capabilities/CAP-12.md"
REGISTER = "docs/decisions/register.md"
DIGEST = "docs/decisions/digest.md"
COPY = "docs/decisions/copy.md"

FAMILIES = {"contract": [s.CONTRACT, YAML, V4, "docs/contract/capabilities/*.md"],
            "decisions": ["docs/decisions/*.md"]}

PROBE_FILES = {
    YAML: [
        "capabilities:",
        "  - id: CAP-1",                                        # 2: the review's probe, `- id: CAP-1`
        "    statement: \"Scope of the kernel.\"",
        "  - id: CAP-10",
        "    statement: \"Retrieval of memory.\"",
        "review:",
        "    floor: 85",                                        # 7: the review's probe, `floor: 85`
    ],
    V4: [
        "# The Contract, version 4",
        "",
        "DEC-850 set the review at 1985 lines.",                # 3: holds 85 only inside 1985
        "",
        "Every packet stays bounded.",                          # 5: 4 words, 27 characters: just above the floor
        "",
        "85 lines per review at most.",                         # 7: above the floor
        "",
        "The scope is set by CAP-1",                            # 9: above the floor, ends on CAP-1
        "",
        "Unconditionally deterministic serialisation",          # 11: 3 words, 43 characters: below the floor
        "",
        "It is set to 85.",                                     # 13: 5 words, 16 characters: below the floor
    ],
    CAP1: ["# CAP-1 Scope", "", "The kernel's scope."],         # holds CAP-1 on word boundaries
    CAP3: ["# CAP-3 Bounds", "", "Every packet stays bounded."],
    CAP10: ["# CAP-10 Retrieval", "", "The scope is set by CAP-10 alone."],
    CAP11: ["# CAP-11 Reviews", "", "The cap is 1985 lines per review at most."],
    CAP12: ["# CAP-12 Forms", "", "Unconditionally deterministic serialisation", "", "It is set to 85."],
    REGISTER: ["# Register", "", "DEC-1078: the owner accepts option A."],
    DIGEST: ["# Digest", "", "DEC-1079: the owner accepts option A."],
    COPY: ["# Copy", "", "DEC-1078: the owner accepts option A."],
}

NO_HIT = (False, None, False, False, 0, 1)
HIT_1 = (True, 1, True, True, 1, 1)


@pytest.fixture
def world(tmp_path):
    w = s.World(tmp_path, second="steady", families=FAMILIES)
    w.commit(PROBE_FILES, "W2-134 fixture: the S5 probes")
    # the control: the Contract's two lines (well above the floor), held by the capability page: a family hit
    w.question("ctl", [{"path": s.CONTRACT, "lines": list(s.CONTRACT_OLD)}], [[w.item(s.CAP7, 1, 3, rev="HEAD")]])
    return w


def _src(rel: str, line: int) -> list[dict]:
    return [{"path": rel, "lines": [line, line]}]


def _check_control(q: dict, text: str) -> None:
    assert s.figures(q["ctl"]) == HIT_1, "the control: families are not counted at all"
    assert s.names_family_hit(s.line_of(text, "ctl"), s.CAP7), s.line_of(text, "ctl")


# --------------------------------------------------------------------------------------------------------------------
# The review's three probes: no family hit
# --------------------------------------------------------------------------------------------------------------------

PROBES = {
    # contract.yaml's `  - id: CAP-1` against CAP-10.md's heading, which holds only CAP-10
    "id-cap-1-against-cap-10": (YAML, 2, CAP10, 1, 1),
    # the register's `DEC-1078: X` against the digest's `DEC-1079: X` (X the same sentence)
    "dec-1078-against-dec-1079": (REGISTER, 3, DIGEST, 3, 3),
    # contract.yaml's `    floor: 85` against version 4's line holding 1985
    "floor-85-against-1985": (YAML, 7, V4, 3, 3),
}


@pytest.mark.parametrize("case", list(PROBES))
def test_s5_the_review_s_probes_are_no_family_hit(world, case):
    gold, line, member, first, last = PROBES[case]
    w = world
    w.question("p01", _src(gold, line), [[w.item(member, first, last, rev="HEAD")]])
    doc, text, _ = w.run()
    q = s.by_id(doc)
    _check_control(q, text)
    assert s.figures(q["p01"]) == NO_HIT, f"{case}: a family hit on text that does not hold the gold"
    assert member not in s.line_of(text, "p01"), s.line_of(text, "p01")


# --------------------------------------------------------------------------------------------------------------------
# Above the floor, held only inside a longer token: no family hit
# --------------------------------------------------------------------------------------------------------------------

INSIDE = {
    # `85 lines per review at most.` is held by `... 1985 lines per review at most.`: 85 inside 1985
    "starts-inside-a-token": (V4, 7, CAP11, 1, 3),
    # `The scope is set by CAP-1` is held by `The scope is set by CAP-10 alone.`: CAP-1 inside CAP-10
    "ends-inside-a-token": (V4, 9, CAP10, 1, 3),
}


@pytest.mark.parametrize("case", list(INSIDE))
def test_s5_a_gold_above_the_floor_held_only_inside_a_longer_token_is_no_hit(world, case):
    gold, line, member, first, last = INSIDE[case]
    w = world
    w.question("p01", _src(gold, line), [[w.item(member, first, last, rev="HEAD")]])
    doc, text, _ = w.run()
    q = s.by_id(doc)
    _check_control(q, text)
    assert s.figures(q["p01"]) == NO_HIT, f"{case}: a family hit inside a longer token"
    assert member not in s.line_of(text, "p01"), s.line_of(text, "p01")


# --------------------------------------------------------------------------------------------------------------------
# Below the floor: counts only in its own path, as with no family
# --------------------------------------------------------------------------------------------------------------------

BELOW = {
    # `- id: CAP-1` normalises to one or two words; CAP-1.md holds CAP-1 on word boundaries
    "id-cap-1": (YAML, 2, CAP1, 1, 1),
    # 3 words, 43 characters: CAP-12.md holds the line exactly
    "three-words": (V4, 11, CAP12, 3, 3),
    # 5 words, 16 characters: CAP-12.md holds the line exactly
    "sixteen-characters": (V4, 13, CAP12, 5, 5),
}


@pytest.mark.parametrize("case", list(BELOW))
def test_s5_a_gold_below_the_floor_counts_only_in_its_own_path(world, case):
    """b01: the member holding the gold exactly at rank 1, the gold's own path at rank 2: a hit at rank 2, no
    family named. b02: the member alone: no hit."""
    gold, line, member, first, last = BELOW[case]
    w = world
    w.question("b01", _src(gold, line), [[w.item(member, first, last, rev="HEAD"),
                                          w.item(gold, line, line, rev="HEAD")]])
    w.question("b02", _src(gold, line), [[w.item(member, first, last, rev="HEAD")]])
    doc, text, _ = w.run()
    q = s.by_id(doc)
    _check_control(q, text)
    assert s.figures(q["b01"]) == (True, 2, True, True, 1, 1), f"{case}: a gold below the floor hit in a member"
    assert s.figures(q["b02"]) == NO_HIT, f"{case}: a gold below the floor hit in a member"
    for qid in ("b01", "b02"):
        assert "famil" not in s.line_of(text, qid).lower(), s.line_of(text, qid)


# --------------------------------------------------------------------------------------------------------------------
# Just above the floor, in a member: still a hit
# --------------------------------------------------------------------------------------------------------------------

ABOVE = {
    # 4 words, 27 characters (26 without the full stop), held by CAP-3.md on word boundaries
    "four-words": (V4, 5, CAP3, 1, 3),
    # the register's `DEC-1078: X` held by another member's `DEC-1078: X`
    "dec-1078-held": (REGISTER, 3, COPY, 3, 3),
}


@pytest.mark.parametrize("case", list(ABOVE))
def test_s5_a_gold_just_above_the_floor_in_a_member_still_hits(world, case):
    gold, line, member, first, last = ABOVE[case]
    w = world
    w.question("a01", _src(gold, line), [[w.item(s.OTHER, 1, 2, rev="HEAD"), w.item(member, first, last, rev="HEAD")]])
    doc, text, _ = w.run()
    q = s.by_id(doc)
    _check_control(q, text)
    assert s.figures(q["a01"]) == (True, 2, True, True, 1, 1), f"{case}: no family hit just above the floor"
    assert s.names_family_hit(s.line_of(text, "a01"), member), s.line_of(text, "a01")
