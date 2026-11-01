"""DEC-745 item 2: the source map's eight rows follow Contract v4.2; no other row changes.

``docs/contract/SOURCE_MAP.csv`` maps each source item to the Contract item
that carries it (columns ``source_document,source_item,class,
carried_by_or_disposition``).  The CIT-P's §8 names eight rows that state the
moved parts as W3.  Under v4.2 each of them states its part in Wave 2, lite,
under its v4.2 item (A7 and A10: CAP-44.f; the verdict: CAP-44.h), and the rest
in Wave 3 under its v4.2 item (A7 and A10 beyond their lite form: CAP-44.k; the
verdict with the ten ADOPTED_HEALTHY conditions: CAP-44.l).  The rows of A11
("16. G") and A9 ("Stage A9") stay W3, unchanged.

Rows are found by their content (``source_document`` and the start of
``source_item``), never by line number.  "No other row changes" is read
against the file at a fixed commit from before this ticket, never a branch.

Reading of "states" (an assumption, not a source): the carrying cell is split
into parts at ``;`` and ``. `` outside brackets.  The Wave 2 statement is a part
that names the lite id, "lite" and W2/Wave 2; the Wave 3 statement is a part
that names the rest's id and W3/Wave 3.
"""

from __future__ import annotations

import pytest

from w2_49_support import (
    SOURCE_MAP,
    SOURCE_MAP_BASE,
    csv_rows,
    gate,
    has,
    names_id,
    read_at,
    read_doc,
    top_segments,
    wave_token,
)

ADOPTION = "Adoption Protocol v3.0"
DISTRIBUTION = "Distribution Protocol v1.2"

# (source_document, source_item's start, the part it maps)
EIGHT = [
    (ADOPTION, "Role D", "A7"),
    (ADOPTION, "Role F", "A10"),
    (ADOPTION, "12. D", "A7"),
    (ADOPTION, "15. F", "A10"),
    (ADOPTION, "20. Final adoption verdict", "verdict"),
    (DISTRIBUTION, "Stage A7", "A7"),
    (DISTRIBUTION, "Stage A10", "A10"),
    (DISTRIBUTION, "18. Adoption acceptance", "verdict"),
]
UNCHANGED = [(ADOPTION, "16. G"), (DISTRIBUTION, "Stage A9")]

# The part's own pattern, its v4.2 lite item (W2) and the item of its rest (W3).
PART = {
    "A7": (gate("A7"), "CAP-44.f", "CAP-44.k"),
    "A10": (gate("A10"), "CAP-44.f", "CAP-44.k"),
    "verdict": (r"verdict", "CAP-44.h", "CAP-44.l"),
}

COLUMNS = ["source_document", "source_item", "class", "carried_by_or_disposition"]


def is_row(row: list[str], doc: str, item: str) -> bool:
    return len(row) >= 2 and row[0] == doc and (row[1] == item or row[1].startswith(item + " "))


def find(rows: list[list[str]], doc: str, item: str) -> list[str]:
    found = [r for r in rows[1:] if is_row(r, doc, item)]
    assert len(found) == 1, f"{SOURCE_MAP}: {len(found)} rows of {doc} start with {item!r}; expected one"
    return found[0]


def is_one_of_the_eight(row: list[str]) -> bool:
    return any(is_row(row, doc, item) for doc, item, _ in EIGHT)


@pytest.fixture(scope="module")
def rows():
    return csv_rows(read_doc(SOURCE_MAP))


@pytest.fixture(scope="module")
def base_rows():
    return csv_rows(read_at(SOURCE_MAP_BASE, SOURCE_MAP))


@pytest.mark.parametrize("doc, item, part", EIGHT, ids=[f"{d.split()[0]}-{i}" for d, i, _ in EIGHT])
def test_source_map_row_states_its_part_lite_in_wave_2_and_the_rest_in_wave_3(rows, doc, item, part):
    """DEC-745 item 2: the row states its part in W2, lite, under its v4.2 item, and the rest in W3 under its item."""
    row = find(rows, doc, item)
    assert len(row) == 4, f"{doc} / {item}: {len(row)} columns, not 4: {row}"
    cell = row[3]
    pattern, lite_id, rest_id = PART[part]
    parts = top_segments(cell)
    w2, w3 = wave_token("W2"), wave_token("W3")
    assert has(pattern, cell), f"{doc} / {item} no longer names its part ({part}): {cell!r}"
    assert any(names_id(p, lite_id) and has(r"\blite\b", p) and w2.search(p) for p in parts), (
        f"{doc} / {item} does not state its part as Wave 2, lite, under {lite_id} (Contract v4.2): {cell!r}"
    )
    assert any(names_id(p, rest_id) and w3.search(p) for p in parts), (
        f"{doc} / {item} does not state the rest of its part as Wave 3 under {rest_id} (Contract v4.2): {cell!r}"
    )


@pytest.mark.parametrize("doc, item", UNCHANGED, ids=[f"{d.split()[0]}-{i}" for d, i in UNCHANGED])
def test_source_map_rows_of_a11_and_a9_still_say_wave_3_unchanged(rows, base_rows, doc, item):
    """DEC-745 item 2: A11 ("16. G") and A9 ("Stage A9") do not move; their rows say W3, as before this ticket."""
    row, before = find(rows, doc, item), find(base_rows, doc, item)
    assert row == before, f"{doc} / {item} changed: {before} -> {row}"
    assert wave_token("W3").search(row[3]), f"{doc} / {item} no longer says W3: {row[3]!r}"


def test_source_map_no_row_but_the_eight_differs_from_before_this_ticket(rows, base_rows):
    """DEC-745 item 2: four columns everywhere; the eight keep document, item and class; every other row as before."""
    assert rows and rows[0] == COLUMNS, f"{SOURCE_MAP}: header {rows[:1]}, not {COLUMNS}"
    bad_width = [r for r in rows if len(r) != 4]
    assert not bad_width, f"{SOURCE_MAP}: {len(bad_width)} rows without four columns, e.g. {bad_width[:3]}"
    assert len(rows) == len(base_rows), f"{SOURCE_MAP}: {len(rows) - 1} rows, {len(base_rows) - 1} at {SOURCE_MAP_BASE}"
    eight = [b for b in base_rows[1:] if is_one_of_the_eight(b)]
    assert len(eight) == len(EIGHT), f"{len(eight)} of the eight rows found at {SOURCE_MAP_BASE}"
    changed = []
    for now, before in zip(rows, base_rows):
        if is_one_of_the_eight(before):
            if now[:3] != before[:3]:
                changed.append(f"one of the eight lost its document, item or class: {before[:3]} -> {now[:3]}")
        elif now != before:
            changed.append(f"{before} -> {now}")
    assert not changed, (
        f"{SOURCE_MAP}: rows differ from {SOURCE_MAP_BASE} beyond the eight rows' carrying cells:\n" + "\n".join(changed[:10])
    )
