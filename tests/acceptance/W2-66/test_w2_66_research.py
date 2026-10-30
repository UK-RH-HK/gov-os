"""Part 3, KPI 11: the measured report ``docs/research/W2-66-scoped-close.md``.

The report is the engineer's measurement; these cases hold that it states what the KPI line asks, in words a
reader finds: the time of a typical scoped close against the full close, the catch rate on lens H's planted
faults with the three widest modules among them, and the 15-minute target as reached by W2-66 with W2-68,
W2-57's serial rework and worksteal together. README, "Part 3".
"""

import re

import pytest

import w2_66_support as support

REPORT_REL = "docs/research/W2-66-scoped-close.md"
WIDEST = ("src/gov/config/loader.py", "src/gov/tasks/tickets.py", "src/gov/store/loader.py")
DURATION = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:s|sec|seconds?|min|minutes?|h|hours?)\b", re.IGNORECASE)
RATE = re.compile(r"\b\d+(?:[.,]\d+)?\s*%|\b\d+\s*(?:of|/)\s*\d+\b")


@pytest.fixture(scope="module")
def report():
    path = support.REPO_ROOT / REPORT_REL
    return path.read_text(encoding="utf-8") if path.is_file() else None


def _need(report):
    assert report is not None, f"{REPORT_REL} does not exist"
    return report


def _paragraphs(text):
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def test_the_report_states_a_typical_scoped_close_s_time_against_the_full_close(report):
    text = _need(report)
    found = [p for p in _paragraphs(text) if re.search(r"scoped", p, re.I) and re.search(r"\bfull\b", p, re.I)
             and len(DURATION.findall(p)) >= 2]
    assert found, "no passage states a scoped close's time beside the full close's, each with its unit"


def test_the_report_states_the_catch_rate_on_lens_h_s_planted_faults_with_the_three_widest_modules(report):
    text = _need(report)
    assert re.search(r"planted", text, re.I) and RATE.search(text), "no catch rate on the planted faults is stated"
    missing = [module for module in WIDEST if module not in text]
    assert not missing, f"the catch rate does not name the three widest modules: {missing}"


def test_the_report_states_the_15_minute_target_as_reached_by_the_four_together(report):
    text = _need(report)
    found = [p for p in _paragraphs(text) if re.search(r"\b15[\s-]*min", p, re.I)]
    assert found, "the 15-minute target is not stated"
    together = [p for p in found if all(re.search(word, p, re.I) for word in (r"W2-66", r"W2-68", r"W2-57",
                                                                              r"worksteal"))]
    assert together, "the 15-minute target is not stated as reached by W2-66, W2-68, W2-57's rework and worksteal"
