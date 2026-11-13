"""S9: measured, in ``docs/research/W2-115-smart-close.md``: the CTO's ``close_build.py`` and this close give the same
verdict on three of this repository's recorded batches (one clean, one with a caused red, one with an unowned red).

The document is read from the tree under test. The suite reads its comparison as a Markdown table: a header row
naming ``close_build`` in one column and this close (``gov close``, ``this close`` or ``smart close``) in another;
one row per batch, its kind (clean, caused, unowned) said in the row.

Red on today's code: the document does not exist.
"""

import re

import w2_115_support as support


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _tables(text):
    tables, current = [], []
    for line in text.splitlines():
        if line.strip().startswith("|"):
            current.append(line)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def _normal(verdict):
    return re.sub(r"[`*_\s]+", " ", verdict).strip().lower()


def test_the_research_record_compares_both_verdicts_on_three_recorded_batches():
    """S9: the document holds, for a clean batch, one with a caused red and one with an unowned red, the verdict of
    ``close_build.py`` and of this close side by side, and the two verdicts are equal on all three."""
    path = support.REPO_ROOT / support.RESEARCH_REL
    assert path.is_file(), f"{support.RESEARCH_REL} does not exist"
    text = path.read_text(encoding="utf-8")
    for table in _tables(text):
        header = [c.lower() for c in _cells(table[0])]
        theirs = [i for i, c in enumerate(header) if "close_build" in c]
        ours = [i for i, c in enumerate(header) if i not in theirs
                and any(w in c for w in ("gov close", "this close", "smart close"))]
        if not theirs or not ours:
            continue
        rows = [_cells(line) for line in table[2:]]
        found = {}
        for kind in ("unowned", "clean", "caused"):  # "caused" last: an unowned row may say "not caused"
            taken = [id(r) for r in found.values()]
            matching = [r for r in rows if id(r) not in taken
                        and any(re.search(rf"\b{kind}\b", c.lower()) for c in r)]
            assert matching, f"the comparison has no row for the {kind} batch: {table}"
            found[kind] = matching[0]
        for kind, row in found.items():
            a, b = _normal(row[theirs[0]]), _normal(row[ours[0]])
            assert a and a == b, f"the {kind} batch's verdicts differ or are empty: close_build {a!r}, this close {b!r}"
        return
    raise AssertionError("the document holds no table comparing close_build.py's verdict with this close's")
