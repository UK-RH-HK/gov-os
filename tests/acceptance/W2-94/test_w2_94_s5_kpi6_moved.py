"""W2-94, KPI success 5 (S5) -- W2-61's KPI 6 is met by this ticket; W2-61's close record names it as moved here.

S5: "W2-61's KPI 6 ("the same split for EXAMIN's set") is met by this ticket; W2-61's close record names it as moved
here Verify: a grep of W2-61's close record finds KPI 6 named as moved to W2-94; this ticket's visible and hidden folders
hold the split of S1". The first half is the grep below, on this repository's file. The second half is S1's cases on the
planted set and the CTO's run of ``check_gold.py`` on the real delivery (README: the CTO's record, not tested here).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_94_support as s  # noqa: E402


def names_kpi6_moved_to_w2_94(text):
    """The grep: a line that names KPI 6, says it moved, and names W2-94."""
    return [line for line in text.splitlines()
            if re.search(r"KPI 6\b", line) and re.search(r"\bmoved\b", line) and "W2-94" in line]


def test_s5_w2_61s_close_record_names_kpi_6_as_moved_to_w2_94():
    assert s.CLOSE_RECORD.is_file(), f"{s.CLOSE_RECORD.relative_to(s.REPO_ROOT)} does not exist"
    found = names_kpi6_moved_to_w2_94(s.CLOSE_RECORD.read_text(encoding="utf-8"))
    assert found, f"no line of {s.CLOSE_RECORD.name} names KPI 6 as moved to W2-94"


def test_s5_the_grep_finds_nothing_in_a_record_that_does_not_name_it():
    """The grep can fail: a record that names KPI 6 without the move, or the move of another line, is not a hit."""
    for text in ("# W2-61 close\n- KPI 6 met by W2-61 itself\n", "# W2-61 close\n- KPI 5 moved to W2-94\n",
                 "# W2-61 close\n- KPI 6 moved to W2-95\n", ""):
        assert names_kpi6_moved_to_w2_94(text) == [], text
    assert names_kpi6_moved_to_w2_94("- KPI 6 (\"the same split for EXAMIN's set\") moved to W2-94 (its S5)\n")
