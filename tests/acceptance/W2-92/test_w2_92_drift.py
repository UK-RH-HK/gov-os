"""KPI success 10 (DEC-1072 (1)): the drift count before and after, by the census's definitions.

The count itself (``docs/research/W2-92-proto-drift.py`` on the rebuilt store: of the decisions current though stated
changed, how many a search reaching the decision also reaches a changer of) is a measure on this repository's store,
the CTO's, verified by the evidence file. This case checks only that the measure record holds it: a section of
``docs/research/W2-92-memory-measure.md`` whose heading names drift, giving a count before and a count after, and
naming the census whose definitions it uses (``D4B-link-census``).
"""

from __future__ import annotations

import re

import w2_92_support as support

RECORD = support.REPO_ROOT / "docs/research/W2-92-memory-measure.md"


def _sections(text):
    """``(heading, body)`` of each Markdown section, a section running to the next heading of its level or above."""
    lines, found = text.splitlines(), []
    heads = [(number, len(match.group(1))) for number, line in enumerate(lines)
             if (match := re.match(r"(#{1,6})\s", line))]
    for index, (number, level) in enumerate(heads):
        end = next((other for other, other_level in heads[index + 1:] if other_level <= level), len(lines))
        found.append((lines[number], "\n".join(lines[number + 1:end])))
    return found


def test_s10_the_measure_record_holds_the_drift_count_before_and_after():
    assert RECORD.is_file(), f"{RECORD.relative_to(support.REPO_ROOT)} is missing"
    drift = [(heading, body) for heading, body in _sections(RECORD.read_text(encoding="utf-8"))
             if "drift" in heading.lower()]
    assert drift, f"{RECORD.name} has no section whose heading names drift"
    heading, body = drift[0]
    for word in ("before", "after"):
        assert any(word in line.lower() and re.search(r"\d", line) for line in body.splitlines()), (
            f"{heading!r} gives no count {word} (no line naming {word!r} with a figure)")
    assert "census" in body.lower(), f"{heading!r} does not name the census whose definitions it uses"
