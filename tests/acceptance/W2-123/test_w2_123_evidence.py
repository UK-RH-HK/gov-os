"""KPI 3 and the failure line "a setting chosen without its measure": the evidence file holds the 16 measured cases
and the chosen setting (S6). No test runs the measurement."""

from __future__ import annotations

import re

import w2_123_support as support

PARALLEL = (1, 2, 4, 8)


def _tables(text):
    """Each markdown table in ``text`` as (its header cells, its data rows' cells)."""
    tables, block = [], []
    for line in text.splitlines() + [""]:
        if line.strip().startswith("|"):
            block.append([cell.strip() for cell in line.strip().strip("|").split("|")])
        elif block:
            if len(block) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in block[1] if cell):
                tables.append((block[0], block[2:]))
            block = []
    return tables


def _number(cell):
    match = re.search(r"-?\d+(?:[.,]\d+)?", cell.replace(",", ""))
    return float(match.group()) if match else None


def _column(header, word):
    found = [index for index, cell in enumerate(header) if word in cell.lower()]
    return found[0] if found else None


def test_the_evidence_file_holds_the_sixteen_measured_cases_and_the_chosen_setting():
    """One table: a parallel-requests column, a chunks-per-second column and a semantic-stage column; 16 rows, four
    for each of 1, 2, 4 and 8, each with numbers; and a line beginning ``Chosen setting:``."""
    path = support.REPO_ROOT / support.EVIDENCE_REL
    assert path.is_file(), f"there is no {support.EVIDENCE_REL}"
    text = path.read_text(encoding="utf-8")
    measured = None
    for header, rows in _tables(text):
        columns = [_column(header, word) for word in ("parallel", "chunks", "semantic")]
        if None not in columns:
            measured = (columns, rows)
            break
    assert measured, "no table names parallel requests, chunks per second and the semantic stage"
    (parallel_at, chunks_at, semantic_at), rows = measured
    rows = [row for row in rows if len(row) > max(parallel_at, chunks_at, semantic_at)]
    assert len(rows) >= 16, f"the table holds {len(rows)} measured cases, not the 16"
    counts = {value: 0 for value in PARALLEL}
    for row in rows:
        value = _number(row[parallel_at])
        assert value is not None and int(value) in counts, f"a row names no parallel setting of {PARALLEL}: {row}"
        counts[int(value)] += 1
        assert _number(row[chunks_at]) is not None, f"a row has no chunks per second: {row}"
        assert _number(row[semantic_at]) is not None, f"a row has no semantic stage in seconds: {row}"
    assert all(count >= 4 for count in counts.values()), \
        f"each parallel setting needs its four cases (capped or not, alone or with three rebuilds): {counts}"
    chosen = [line for line in text.splitlines() if line.startswith("Chosen setting:")]
    assert chosen and len(chosen[0]) > len("Chosen setting:") + 20, "no line begins 'Chosen setting:' with its choice"
