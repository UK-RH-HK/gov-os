"""W2-51 KPI success line 4: "The list's and the triage's counts agree with their rows." """

from __future__ import annotations

import pytest

from w2_51_support import LIST_COUNTS, TRIAGE_COUNTS, assert_fails_naming, assert_passes, build_and_run, plan_v41


def test_the_list_and_the_triage_counts_agree_with_their_rows(tmp_path):
    """Closed rows (list §4) and the triage's table of outline items are not open rows and are not counted."""
    res = build_and_run(tmp_path, plan_v41())
    assert_passes(res, LIST_COUNTS, TRIAGE_COUNTS)


@pytest.mark.parametrize("severity, change", [("high", "row-added"), ("info", "heading-changed")])
def test_a_list_severity_heading_that_disagrees_with_its_rows_fails_naming_it(tmp_path, severity, change):
    plan = plan_v41()
    if change == "row-added":
        plan.list_stated[severity] = len(plan.list_rows[severity])
        plan.list_rows[severity].append(("W2-H003", "A row added without its count"))
    else:
        plan.list_stated[severity] = len(plan.list_rows[severity]) + 1
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, LIST_COUNTS, severity)


@pytest.mark.parametrize("key, needle", [(("medium", "Wave 3"), "medium"), (("all", "Total"), "all")],
                         ids=["severity-cell", "all-row"])
def test_a_triage_count_that_disagrees_with_its_rows_fails_naming_it(tmp_path, key, needle):
    plan = plan_v41()
    plan.triage_stated[key] = 99
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, TRIAGE_COUNTS, needle)
