"""W2-11, KPI 11 (DEC-943 item 1, DEC-954; from the withdrawn W2-79): every gap the register of brief gaps marks
fixed in the common brief or the brief builder has a case, and the fix is still in the brief a lead is given.

A repository-state test (it reads the live register of gaps and the tracked common brief). The builder is an
untracked tool of the main tree: it puts the ticket's part before the common brief from its fourth paragraph on,
with the placeholders filled, so each fix is looked for in that part of the common brief. The case that runs the
builder itself runs only when GOV_BRIEF_BUILDER names it (see the README).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

import pytest

import w2_11_support as s

GAPS_REL = "governance/project/orchestration/brief-gaps.md"
COMMON_REL = "governance/project/briefs/LEAD-w2-common.md"

# Each fix, by a pattern of its "Fixed by" text or of the gap, with the ideas one statement of the brief carries.
FIXES = (
    (r"held past 90 minutes", [r"held past 90 minutes", r"checkpoint", r"PACKAGES"]),
    (r"P-R1", [r"P-R1", r"gov retrieve", r"drop unread"]),
    (r"name it in the return", [r"untracked scratch", r"name it"]),
    (r"rebuild before the first worker", [r"no store", r"rebuild", r"STORE_MISSING"]),
    (r"background waits", [r"never wait in the foreground", r"background"]),
    (r"probed_commit", [r"probed_commit", r"full commit id"]),
)


def _fixed_rows():
    rows = []
    for line in s.read(GAPS_REL).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 6 and re.match(r"\d{4}-\d{2}-\d{2}$", cells[0]) and re.search(
                r"common brief|builder", cells[5], re.I) and not re.match(r"open\b", cells[5], re.I):
            rows.append(cells)
    return rows


def _fix(row):
    return next((ideas for pattern, ideas in FIXES if re.search(pattern, f"{row[5]} {row[2]}", re.I)), None)


def _brief_body():
    return s.read(COMMON_REL).split("\n\n", 3)[3]


def test_the_register_has_fixed_gaps_to_keep():
    assert _fixed_rows(), f"{GAPS_REL} lists no gap fixed in the common brief or the builder"


@pytest.mark.parametrize("row", _fixed_rows(), ids=lambda r: f"{r[1]}:{r[2][:40]}")
def test_the_fixed_gap_is_still_in_the_brief(row):
    ideas = _fix(row)
    assert ideas is not None, f"a fixed gap has no case yet (the test designer adds one): {row[2]} / {row[5]}"
    assert s.stated(_brief_body(), ideas), f"the brief no longer carries the fix of '{row[2]}' ({row[5]})"


@pytest.mark.skipif(not os.environ.get("GOV_BRIEF_BUILDER"), reason="GOV_BRIEF_BUILDER names no builder")
def test_a_brief_built_today_carries_every_fix(tmp_path):
    part, out = tmp_path / "part.md", tmp_path / "brief.md"
    part.write_text("# Lead brief (planted part)\n", encoding="utf-8")
    values = ["ID=TEST-0000", "W2=T-01", "PROFILE=STANDARD", "PATHS=x", "ROWS=x", "SOURCES=x", "IMPL=DEC-943",
              "EST=1"]
    env = dict(os.environ, GOV_BRIEF_COMMON=str(s.REPO_ROOT / COMMON_REL))
    done = subprocess.run([sys.executable, os.environ["GOV_BRIEF_BUILDER"], str(part), str(out), *values],
                          env=env, capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr[-500:]
    built = out.read_text(encoding="utf-8")
    for row in _fixed_rows():
        assert _fix(row) and s.stated(built, _fix(row)), f"the built brief lacks the fix of '{row[2]}'"
