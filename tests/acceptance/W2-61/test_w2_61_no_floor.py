"""Fix F9 (audit N-14; DEC-1210, DEC-1233, EMERGENCY-2 5.2): the measure has no hit@5 floor and no target figure.

"hit@5 I DON'T CARE if it's even 10%": hit@k is a reported diagnostic, never a floor, a target or a verdict. For the
standing measure (``python3 -m gov.retrieval.measure``) that means:

- the text report's ``total:`` line gives both figures, hit@5 and full evidence, as counts and percentages and says
  nothing of ``floor 85`` or ``target 99 %``;
- the JSON total's ``hit_at_5`` and ``full_evidence`` objects hold ``count``, ``of`` and ``percent`` and no floor,
  target or below-floor field, the record written by ``--out`` the same;
- no exit code depends on a figure: a set with every question missed, one with every question hit and a mixed one all
  end 0;
- the source holds no ``FLOOR, TARGET = 85, 99`` and no other literal hit@k floor in ``src/``.

The planted worlds are W2-61's own (``w2_61_support``): a planted repository and a planted ``gov`` answering
canned evidence; no store, no model, no network.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61_support as s  # noqa: E402

SRC = s.SRC
BANNED_KEY = re.compile(r"floor|target|threshold", re.I)
FLOOR_WORDS = re.compile(r"floor|target|threshold|\b85\b|\b99\b", re.I)


def _hit(w, name="v01"):
    w.question(name, {"question": f"What is the packet ceiling {name}?", "gold_answer": "six thousand tokens",
                      "sources": [{"path": s.DECISIONS, "heading": "## DEC-1 The packet ceiling"}]},
               [[w.noise(1), w.section(s.DECISIONS, "## DEC-1 The packet ceiling"), w.noise(2)]])


def _miss(w, name="v04"):
    w.question(name, {"question": f"How does a session resume {name}?", "gold_answer": "from its last checkpoint",
                      "sources": [{"path": s.DECISIONS, "heading": "## DEC-4 The resume"}]},
               [[w.noise(4), w.noise(5)]])


def _world(tmp_path, plant):
    w = s.make_world(tmp_path, commit=False)
    plant(w)
    w.commit()
    return w


def _standard(w):
    s.standard_questions(w)


def _total_line(text):
    lines = [line for line in text.splitlines() if line.startswith("total:")]
    assert len(lines) == 1, f"the text report has {len(lines)} total lines, not one:\n{text[-1500:]}"
    return lines[0]


def _walk(value, path=()):
    """Every (path, key) of every object of a JSON document."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield path, key
            yield from _walk(item, (*path, key))
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item, path)


# ---- success: the figures are reported, with no floor or target ---------------------------------------------------


def test_the_total_line_gives_both_figures_and_names_no_floor_or_target(tmp_path):
    w = _world(tmp_path, _standard)
    run = w.measure(s.SET)
    assert run.returncode == 0, run.describe()
    line = _total_line(run.stdout)
    assert re.search(r"hit@5 2 of 4 \(50\.0 %", line), f"the total line does not report hit@5 2 of 4 (50.0 %): {line!r}"
    assert re.search(r"full evidence 3 of 4 \(75\.0 %", line), f"the total line does not report full evidence 3 of 4: {line!r}"
    assert not FLOOR_WORDS.search(line), f"the total line still names a floor, a target or a threshold: {line!r}"


def test_the_total_line_is_exactly_the_two_figures(tmp_path):
    """The line keeps today's form minus the two phrases (the three revised floor-85 cases assert the same text)."""
    w = _world(tmp_path, _standard)
    run = w.measure(s.SET)
    assert _total_line(run.stdout) == "total: hit@5 2 of 4 (50.0 %); full evidence 3 of 4 (75.0 %)", run.describe()


def test_the_json_total_holds_counts_and_no_floor_or_target_field(tmp_path):
    w = _world(tmp_path, _standard)
    document = w.measure(s.SET, "--json").json()
    total = document["total"]
    for name in ("hit_at_5", "full_evidence"):
        figure = total[name]
        assert set(figure) == {"count", "of", "percent"}, f"total.{name} holds {sorted(figure)}, not count, of, percent"
    assert (total["hit_at_5"]["count"], total["hit_at_5"]["of"], total["hit_at_5"]["percent"]) == (2, 4, 50.0)
    assert (total["full_evidence"]["count"], total["full_evidence"]["of"], total["full_evidence"]["percent"]) == (3, 4, 75.0)
    banned = [(path, key) for path, key in _walk(document) if BANNED_KEY.search(str(key))]
    assert not banned, f"the JSON document still carries a floor, target or threshold field: {banned}"


def test_the_record_written_by_out_holds_no_floor_or_target_field(tmp_path):
    w = _world(tmp_path, _standard)
    out = w.base / "out"
    run = w.measure(s.SET, "--json", "--out", out)
    run.json()
    records = s.records_in(out)
    assert len(records) == 1, f"--out wrote {len(records)} JSON files, not one"
    document = next(iter(records.values()))
    banned = [(path, key) for path, key in _walk(document) if BANNED_KEY.search(str(key))]
    assert not banned, f"the record still carries a floor, target or threshold field: {banned}"
    assert (document["total"]["hit_at_5"]["count"], document["total"]["hit_at_5"]["of"]) == (2, 4)


# ---- failure: a verdict or an exit code that follows a figure -------------------------------------------------------


@pytest.mark.parametrize("plant, hits", [(_miss, 0), (_hit, 1), (_standard, 2)], ids=["every-miss", "every-hit", "mixed"])
def test_the_exit_code_does_not_depend_on_the_hit_at_5_figure(tmp_path, plant, hits):
    """Guard (green on the base): a hit@5 of 0 %, of 100 % and of 50 % all end 0, report their count and say of none
    that it is below anything; the fix must not make the exit code follow a figure."""
    w = _world(tmp_path, plant)
    run = w.measure(s.SET)
    assert run.returncode == 0, f"a hit@5 of {hits} changes the measure's exit code\n{run.describe()}"
    line = _total_line(run.stdout)
    assert re.search(rf"hit@5 {hits} of \d+ \(\d+(\.\d)? %", line), f"the hit@5 count is not reported: {line!r}"
    assert "below" not in (run.stdout + run.stderr).lower(), f"the measure reports a figure as below something\n{run.describe()}"
    document = w.measure(s.SET, "--json").json()
    assert document["total"]["hit_at_5"]["count"] == hits


# ---- the source: no literal floor ------------------------------------------------------------------------------------


def test_the_measure_source_holds_no_floor_or_target_constant():
    text = (SRC / "gov" / "retrieval" / "measure.py").read_text(encoding="utf-8")
    assert not re.search(r"\bFLOOR\b|\bTARGET\b", text), "measure.py still names a FLOOR or a TARGET"
    assert not re.search(r"floor\s+(of\s+)?85|target\s+(of\s+)?99", text, re.I), "measure.py still states floor 85 or target 99"
    assert not re.search(r"""["']floor["']|["']target["']""", text), "measure.py still writes a floor or target key"


def test_no_source_file_holds_a_hit_at_k_floor_literal():
    """Narrow: the named literals of the old floors, and a hit@k name compared with a floor-like name; the
    ``_FLOOR`` of the secrets scan's gitleaks speed, the disk floors and the launcher's effort floor are no hit@k."""
    patterns = (
        re.compile(r"\bFLOOR\s*,\s*TARGET\b"),
        re.compile(r"hit_at_5_(threshold|floor|target)", re.I),
        re.compile(r"HIT_?(AT_?)?[0-9K]+_(FLOOR|TARGET|THRESHOLD)"),
        re.compile(r"hit@\d+[^\n]{0,60}\b(floor|target)\s+(of\s+)?\d", re.I),
        re.compile(r"\bhit\w*\s*(<|<=)\s*(FLOOR|TARGET|THRESHOLD)\b"),
        re.compile(r"\b(floor|target)\s+(of\s+)?(85|99)\b", re.I),
    )
    hits = []
    for path in sorted(list((SRC / "gov").rglob("*.py")) + list((SRC / "gov").rglob("*.yaml"))):
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            for found in pattern.finditer(text):
                hits.append(f"{path.relative_to(SRC)}: {found.group(0)!r}")
    assert not hits, "hit@k floors remain in src/: " + "; ".join(hits)
