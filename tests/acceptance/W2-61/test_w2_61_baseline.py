"""W2-61, KPI success 7 -- the baseline record.

"The baseline: the first measure runs today on the pinned stores, both halves, and is recorded in
docs/research/W2-61-baseline.md with the pinned gov's version and commit and the stores' fingerprint; the same
measure is repeated after each ticket of the memory chain, beside the baseline [DEC-941, DEC-833 item 3]".

Structural checks only, never the values of the figures beyond their presence. The record holds:

- the date of the run;
- the measured clone's commit; the pinned gov's version and its commit (commits as at least 12 hex digits);
- the stores' fingerprint (as the rebuild records it, or the sha256 of each store file, so named);
- both figures together, hit@5 against 85 and full evidence against 99 %;
- a per-question table of the visible half: hit@5, in the bundle, full evidence, the repeat run, the run after the
  rebuild; one row per visible question;
- lens B's figures (13 of 20, 17 of 20) beside;
- a labelled place (a heading) for the hidden half's scores, which W2-61h's run fills.

Red now: the record does not exist.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61_support as s  # noqa: E402

HEX = re.compile(r"\b[0-9a-f]{12,64}\b")


MISSING = f"{s.BASELINE.relative_to(s.REPO_ROOT)} does not exist"


@pytest.fixture(scope="module")
def text():
    """The record's text, or None: each case then fails (rather than errs) on its absence."""
    return s.BASELINE.read_text(encoding="utf-8") if s.BASELINE.is_file() else None


def _lines(text, *words):
    return [line for line in text.splitlines() if all(word.lower() in line.lower() for word in words)]


def test_the_date(text):
    assert text is not None, MISSING
    assert re.search(r"\b20\d\d-[01]\d-[0-3]\d\b", text), "the record gives no date (YYYY-MM-DD)"


def test_the_measured_clone_s_commit(text):
    assert text is not None, MISSING
    assert any(HEX.search(line) for line in _lines(text, "clone")), (
        "no line names the measured clone with its commit (at least 12 hex digits)")


def test_the_pinned_gov_s_version_and_commit(text):
    assert text is not None, MISSING
    assert any(re.search(r"\d+\.\d+", line) for line in _lines(text, "gov", "version")), (
        "no line gives the pinned gov's version")
    assert any(HEX.search(line) for line in _lines(text, "gov", "commit")), (
        "no line gives the pinned gov's commit (at least 12 hex digits)")


def test_the_stores_fingerprint(text):
    assert text is not None, MISSING
    lines = _lines(text, "fingerprint") + _lines(text, "sha256")
    assert any(HEX.search(line) for line in lines), "no line gives the stores' fingerprint or their sha256"


def test_both_figures_together_against_85_and_99(text):
    assert text is not None, MISSING
    both = [line for line in text.splitlines() if s.HIT_LABEL.search(line) and s.FULL_LABEL.search(line)]
    assert both, "no line gives hit@5 and full evidence together"
    assert re.search(r"\b85\b", text) and re.search(r"\b99\b", text), "the floor 85 and the target 99 are not given"
    assert any(re.search(r"\b85\b", line) for line in text.splitlines() if s.HIT_LABEL.search(line)), (
        "hit@5 is not set against 85")
    assert any(re.search(r"\b99\b", line) for line in text.splitlines() if s.FULL_LABEL.search(line)), (
        "full evidence is not set against 99")


def _visible_ids():
    files = sorted(s.REAL_VISIBLE.glob("*.yaml")) if s.REAL_VISIBLE.is_dir() else []
    assert files, "the visible half does not exist"
    ids = []
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        ids.append(str(data.get("id") or path.stem))
    return ids


def test_a_per_question_table_of_the_visible_half(text):
    assert text is not None, MISSING
    rows = [line for line in text.splitlines() if line.lstrip().startswith("|")]
    headers = [line for line in rows if s.HIT_LABEL.search(line) and s.FULL_LABEL.search(line)
               and "bundle" in line.lower() and "repeat" in line.lower() and "rebuild" in line.lower()]
    assert headers, ("no table header gives hit@5, in the bundle, full evidence, the repeat run and the run after "
                     "the rebuild")
    missing = [qid for qid in _visible_ids() if not any(re.search(rf"\b{re.escape(qid)}\b", row) for row in rows)]
    assert not missing, f"the table has no row for: {missing}"


def test_lens_b_s_figures_beside(text):
    assert text is not None, MISSING
    assert re.search(r"lens\s*B", text, re.I), "lens B is not named"
    assert re.search(r"\b13\s*(of|/)\s*20\b", text), "lens B's 13 of 20 is not given"
    assert re.search(r"\b17\s*(of|/)\s*20\b", text), "lens B's 17 of 20 is not given"


def test_a_labelled_place_for_the_hidden_half(text):
    assert text is not None, MISSING
    headings = [line for line in text.splitlines() if line.startswith("#") and "hidden" in line.lower()]
    assert headings, "no heading labels the place of the hidden half's scores"
