"""Builder tests for ``gov discover``'s draft (W2-36): the change name, the required rows and the spec the draft is.
Regression evidence only (DEC-136); the acceptance cases are in tests/acceptance/W2-36."""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.discover import check, draft  # noqa: E402

MODULE = check.skill(REPO)


def test_change_name_drops_stop_words_and_keeps_six_words():
    assert draft.change_name("add CSV export to the report page") == "add-csv-export-report-page"
    assert draft.change_name("how could we add CSV export to the report page?") == "add-csv-export-report-page"
    assert draft.change_name("one two three four five six seven eight") == "one-two-three-four-five-six"
    assert draft.change_name("the of a") == ""


def test_required_rows_follow_the_checkers_rule():
    assert draft.required("LITE", []) == [1, 2, 4, 5, 6, 9, 16, 23, 24, 25]
    assert draft.required("STANDARD", ["performance-capacity"]) == [1, 2, 4, 5, 6, 9, 11, 16, 20, 23, 24, 25]
    assert draft.required("FULL", []) == list(range(1, 27))


def test_the_draft_has_the_form_and_the_check_refuses_its_parts_by_name():
    text = draft.spec("add CSV export", "LITE", [], True, ["- docs/a.md: CSV"], "Memory: not available: none")
    headings = re.findall(r"^## (.*)$", re.sub(r"<!--.*?-->", "", text, flags=re.S), re.M)
    assert headings == ["Problem", "Users and scenarios", "Goals", "Non-goals", "KPIs", "Test data", "Out of scope",
                        "Open questions", "Accepted by", "Verify", "Sources read"]
    assert "add CSV export" in text.split("## Users and scenarios")[0]
    lines = check.refusals(Path("/nonexistent"), text)
    named = {re.match(r"REFUSED ([^:]+):", line).group(1) for line in lines}
    assert {"Users and scenarios", "Goals", "Non-goals", "KPIs", "Test data", "Out of scope", "Accepted by"} <= named
    assert not named & {"Problem", "Open questions"}


GOOD = """## Problem
Rows cannot be exported.

## Users and scenarios
- An analyst exports the rows.

## Goals
- Rows are exported.
<!-- a comment -->

## Non-goals
- Pretty reports.
- Scheduling.

## KPIs
- K1: An analyst receives the rows as a file within a minute.
  Fails if: no file arrives within five minutes.
- K2: The file holds every row.
  Fails if: a row is missing.

## Test data
| source | kind | owner | licence or recipe | privacy | secrets | hidden half | secured |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fifty rows | synthetic | QA engineer | fixed seed | none | none | no | yes |

## Out of scope
- Imports: later.

## Open questions
- Question: Which format?
  - Options: one (cost: a); two (cost: b)
  - Recommendation: one.

## Accepted by
The owner.

## Verify
- K1: run the export and time it
- K2: count the rows
"""


def _check(text):
    return check.refusals(REPO, text)


def test_a_finished_spec_passes():
    assert _check(GOOD) == []


def test_verify_lines_are_matched_to_the_kpis():
    assert _check(GOOD.replace("- K2: count the rows\n", "")) == ["REFUSED Verify: K2 has no verify"]
    assert _check(GOOD + "- K3: nothing\n") == ["REFUSED Verify: K3 is not a KPI"]
    assert _check(GOOD.replace("count the rows", "<...>")) == ["REFUSED Verify: K2 has no verify"]
    assert _check(GOOD.replace("count the rows", "run `count_rows()`")) == []  # a verify may name code


def test_a_slot_and_a_comment_are_not_content():
    text = GOOD.replace("- Rows are exported.", "- <what the change makes true>")
    assert _check(text) == ["REFUSED Goals: missing"]


def test_the_kpi_lines_of_a_spec_are_read_with_their_failure_and_verify():
    kpis = check.kpis(GOOD, MODULE)
    assert [k[0] for k in kpis] == ["1", "2"]
    assert kpis[0][1] == "An analyst receives the rows as a file within a minute."
    assert kpis[1][2] == "a row is missing."
    assert check.verifies(GOOD, MODULE)["2"] == "count the rows"
    assert check.bullets(GOOD, "Non-goals", MODULE) == ["Pretty reports.", "Scheduling."]
