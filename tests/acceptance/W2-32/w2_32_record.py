"""S9 and F1 as rules over the measure records (W2-32; DEC-1055, DEC-954 Q9e, DEC-957). Standard library only.

S9 and F1 are judged on the record the CTO keeps (the standing measure's records under ``~/gov-os-runs/D4B/``) and
on the ticket's evidence file, not on W2-32's code (README). This module states the two rules as code, so the record
is judged the same way each time:

- **The noise band (F1)** of a figure is the range of its counts over the baseline's repeated runs (W2-15a's measure
  1: the same commit, set and part, run more than once). A round **lowers a figure beyond its noise band** when its
  count is below the band's lowest; that round's improvement is reverted.
- **S9:** after a round, hit@5 below 85 % is the next round while fewer than two rounds have run, and the owner's
  decision after two (DEC-954 Q9e); at 85 % or above but under 95 %, with room for improvement found, memory is not
  closed and goes to the owner; at 95 % or above, nothing.

Run it on records: ``python3 w2_32_record.py <baseline records folder> [<round record.json> ...]`` prints each
figure's band and, per round in the order given, F1's verdict and S9's state.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

FIGURES = ("hit_at_5", "full_evidence")
FLOOR, TARGET = 85, 95  # CAP-10's floor; the owner's target for hit@5 (DEC-957)
QUESTIONS = 48


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def baseline_records(folder):
    return [load(path) for path in sorted(Path(folder).glob("measure-*.json"))]


def form_problems(record):
    """What a measure record lacks for S9 and F1 to be judged on it (an empty list when nothing)."""
    problems = []
    total = record.get("total") or {}
    if total.get("questions") != QUESTIONS:
        problems.append(f"total.questions is {total.get('questions')!r}, not {QUESTIONS}")
    for figure, bar, value in (("hit_at_5", "floor", 85), ("full_evidence", "target", 99)):
        entry = total.get(figure) or {}
        if not isinstance(entry.get("count"), int) or entry.get("of") != QUESTIONS:
            problems.append(f"total.{figure} has no count of {QUESTIONS}: {entry}")
        if entry.get(bar) != value:
            problems.append(f"total.{figure}.{bar} is {entry.get(bar)!r}, not {value}")
    for key in ("set", "part", "commit"):
        if not record.get(key):
            problems.append(f"no {key}")
    return problems


def noise_band(records, figure):
    """``(lowest, highest)`` count of ``figure`` over the baseline's runs."""
    counts = [record["total"][figure]["count"] for record in records]
    return min(counts), max(counts)


def f1_verdict(band, count):
    """``revert`` when ``count`` is below the band's lowest, else ``keep``."""
    return "revert" if count < band[0] else "keep"


def s9_state(percents, room=True):
    """S9's state after the rounds whose hit@5 percentages are ``percents`` (in order)."""
    if not percents:
        return "no round"
    last = percents[-1]
    if last < FLOOR:
        return "owner decides" if len(percents) >= 2 else "next round"
    if last < TARGET and room:
        return "owner told: not closed"
    return "none"


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    baseline = baseline_records(argv[0])
    for record in baseline:
        for problem in form_problems(record):
            print(f"baseline form: {problem}")
    bands = {figure: noise_band(baseline, figure) for figure in FIGURES}
    for figure, band in bands.items():
        print(f"{figure}: baseline {band[0]}..{band[1]} of {QUESTIONS} over {len(baseline)} runs")
    percents = []
    for path in argv[1:]:
        record = load(path)
        verdicts = {figure: f1_verdict(bands[figure], record["total"][figure]["count"]) for figure in FIGURES}
        percents.append(100.0 * record["total"]["hit_at_5"]["count"] / QUESTIONS)
        print(f"{path}: F1 {verdicts}; hit@5 {percents[-1]:.1f} %; S9 {s9_state(percents)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
