"""W2-42a, KPI line 9 (measured: the 61 logged commands, the planted writes, the unknown forms; the evidence file)
and failure line 1 (no write the base's parser catches is missed).

- **The 61 logged commands** are lines 1 to 61 of the CTO's ``log/guard-refusals.jsonl`` (ACT-GUARD-FIX-3's corpus):
  57 recovered in full from their transcripts (fixtures/refusals.json), and lines 51 to 54, summary rows with no
  tool-use id, counted as their twins, lines 55, 56, 59 and 60 (ACT-GUARD-FIX-3 §2). Each is read by the product's
  parser in its own folder with its session's TMPDIR, as the hook reads it.
- **The planted writes** are ACT-GUARD-FIX-3's (fixtures/planted.json). The parser's own ground is the shell: the
  cases with no Python, perl, node, ruby or uv code; the code cases are judged through the hook
  (test_w2_42a_replay.py).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w2_42a_support as s  # noqa: E402

TWINS = {51: 55, 52: 56, 53: 59, 54: 60}  # summary rows counted as the rows they summarise
MOST_UNRESOLVED = 2
PLANTED = s.planted()
SHELL = [r for r in PLANTED if s.shell_only(r)]
BASE_CAUGHT = [r for r in PLANTED if r["tool"] == "Bash" and r.get("base_caught")]


def _unresolved(row):
    with s.session_env(row["tmpdir"]):
        got = s.parse(row["input"]["command"], row["cwd"])
    return bool(got) and s.UNRESOLVABLE in got


def test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands():
    rows = {r["line"]: r for r in s.refusals() if r["line"] <= 61}
    assert len(rows) == 57 and all(rows[t]["tool"] == "Bash" for t in TWINS.values())
    lines = [TWINS.get(n, n) for n in range(1, 62)]
    unresolved = [n for n, src in zip(range(1, 62), lines) if _unresolved(rows[src])]
    assert len(unresolved) <= MOST_UNRESOLVED, f"{len(unresolved)} of 61 unresolvable: lines {unresolved}"


@pytest.mark.parametrize("row", SHELL, ids=[r["name"] for r in SHELL])
def test_kpi9_no_planted_shell_write_is_missed_by_the_parser(row):
    assert s.parser_caught(row, s.REPO), "the parser misses this planted write (no target there, no sentinel)"


@pytest.mark.parametrize("row", BASE_CAUGHT, ids=[r["name"] for r in BASE_CAUGHT])
def test_failure1_no_write_the_base_parser_catches_is_missed(row):
    assert s.parser_caught(row, s.REPO), "the base's parser catches this planted write and this one misses it"


def test_kpi9_the_measures_are_stated_in_the_evidence_file():
    assert os.path.isfile(s.EVIDENCE), "docs/changes/W2-42a-evidence.md is not in the tree"
    text = open(s.EVIDENCE, encoding="utf-8").read()
    assert "61" in text and "planted" in text.lower(), "the evidence names neither the 61 commands nor the planted cases"
