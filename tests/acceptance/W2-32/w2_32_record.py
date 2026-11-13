"""S9 and F1 as rules over the measure records (W2-32; DEC-1055, DEC-954 Q9e, DEC-957). Standard library only.

S9 and F1 are judged on the record the CTO keeps (the standing measure's records under ``~/gov-os-runs/D4B/``) and
on the ticket's evidence file, not on W2-32's code (README). This module states the two rules as code, so the record
is judged the same way each time:

- **The noise band (F1)** of a figure is the range of its counts over the baseline's repeated runs (W2-15a's measure
  1: the same commit, set and part, run more than once). A round **lowers a figure beyond its noise band** when its
  count is below the band's lowest; that round's improvement is reverted.
- **S9** (DEC-1083 (2), re-worded by DEC-1097 (1)(d) and DEC-1129 (1)): K9's memory line is judged once, on the
  declared configuration, on the verdict set, by the figure **right end to end** and the **wrong claims**: right at
  least 85 % with wrong claims at most 5 % is met (target 95 %); below 85 %, or wrong claims above 5 %, is brought to
  the owner by the memory audit ("owner told"). hit@5 is reported beside the end-to-end figure and never judged. No
  "next round" and no "owner decides after two rounds" any more.

Run it on records: ``python3 w2_32_record.py <baseline records folder> [<round record.json> ...]`` prints each
figure's band and, per round in the order given, F1's verdict, hit@5 (reported) and S9's state, S9 being judged on the
record's ``total.end_to_end`` (``count`` right, ``wrong`` claims, ``of`` questions) when it carries one.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

FIGURES = ("hit_at_5", "full_evidence")
FLOOR, TARGET = 85, 95  # S9's bar and the owner's target for the end-to-end figure (DEC-1097 (1)(d), DEC-1129 (1))
WRONG_MAX = 5  # S9: wrong claims at most 5 %
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


def percent(count, of):
    return 100.0 * count / of


def s9_state(right_percent, wrong_percent=0.0):
    """S9's state, judged once on the end-to-end figure: ``right_percent`` of the questions right end to end and
    ``wrong_percent`` of them a wrong claim. hit@5 is never an input: it is reported beside, not judged."""
    if right_percent is None:
        return "no figure"
    if right_percent < FLOOR or wrong_percent > WRONG_MAX:
        return "owner told"
    if right_percent < TARGET:
        return "met, under target"
    return "met"


def s9_report(right, wrong, hit_at_5, of):
    """S9 on counts of ``of`` questions: the state, the end-to-end and wrong-claim percentages, and hit@5's
    percentage reported beside them."""
    right_percent, wrong_percent = percent(right, of), percent(wrong, of)
    return {"state": s9_state(right_percent, wrong_percent), "end_to_end": right_percent, "wrong_claims": wrong_percent,
            "hit_at_5": percent(hit_at_5, of)}


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
    for path in argv[1:]:
        record = load(path)
        verdicts = {figure: f1_verdict(bands[figure], record["total"][figure]["count"]) for figure in FIGURES}
        hit = percent(record["total"]["hit_at_5"]["count"], QUESTIONS)
        end = record["total"].get("end_to_end")
        if end:
            right, wrong = percent(end["count"], end["of"]), percent(end["wrong"], end["of"])
            print(f"{path}: F1 {verdicts}; hit@5 {hit:.1f} % (reported); end to end {right:.1f} %, wrong claims "
                  f"{wrong:.1f} %; S9 {s9_state(right, wrong)}")
        else:
            print(f"{path}: F1 {verdicts}; hit@5 {hit:.1f} % (reported); S9 {s9_state(None)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
