"""S3 (a finished spec passes the check, open rows listed) and F1 (the check refuses an unfinished spec by name)."""

from __future__ import annotations

import re

import pytest

import w2_36_support as support


def open_rows(check):
    """{(key, gap ticket or UNLINKED)} of the check's ``OPEN <key> <ticket>`` lines."""
    found = set()
    for line in check.lines():
        row = re.match(r"^OPEN\s+(\S+)\s+(\S+)", line)
        if row:
            found.add((row.group(1), row.group(2)))
    return found


def test_check_passes_the_finished_spec_and_lists_every_open_required_row_unlinked(own_c, home):
    check = support.discover(own_c, "--check", support.CHANGE, home=home)
    assert check.returncode == 0, check.describe()
    assert "PASS" in check.lines(), check.describe()
    assert open_rows(check) == {(key, "UNLINKED") for key in support.MANDATORY}, check.describe()
    same = support.check_spec(own_c / support.SPEC_REL, home)
    assert same.returncode == 0 and "PASS" in same.lines(), same.describe()


def test_check_names_a_linked_rows_ticket_and_leaves_out_a_present_row(own_c, home):
    record = own_c / support.CHANGE_REL / "readiness.yaml"
    text = record.read_text(encoding="utf-8")
    text = text.replace("{n: 1, key: intent, state: MISSING, evidence: [],",
                        "{n: 1, key: intent, state: PRESENT, evidence: [\"docs/report.md#the-report\"],")
    text = text.replace("key: scenarios, state: MISSING, evidence: [], reason: null, gap_ticket: null",
                        f"key: scenarios, state: MISSING, evidence: [], reason: null, gap_ticket: {support.REPORT_TICKET}")
    assert "PRESENT" in text and support.REPORT_TICKET in text, support.FIXTURE_FAILED + ": the template's rows changed"
    record.write_text(text, encoding="utf-8")
    check = support.discover(own_c, "--check", support.CHANGE, home=home)
    assert check.returncode == 0, check.describe()
    assert "PASS" in check.lines(), check.describe()
    expected = {(key, "UNLINKED") for key in support.MANDATORY if key not in ("intent", "scenarios")}
    expected.add(("scenarios", support.REPORT_TICKET))
    assert open_rows(check) == expected, check.describe()


@pytest.mark.parametrize("variant", sorted(support.VARIANTS))
def test_check_refuses_an_unfinished_spec_by_name_and_never_prints_pass(variant, own_c, home):
    text, expected = support.VARIANTS[variant]
    spec = own_c / support.SPEC_REL
    spec.write_text(text, encoding="utf-8")
    if expected is None:  # the same line check_spec.py prints for it
        expected = support.code_line(support.check_spec(spec, home))
        assert expected, f"{support.FIXTURE_FAILED}: check_spec.py printed no K1 names code line"
    check = support.discover(own_c, "--check", support.CHANGE, home=home)
    assert check.returncode == 1, check.describe()
    assert any(expected in line for line in check.lines()), f"no line {expected!r}:\n{check.describe()}"
    assert "PASS" not in check.lines(), check.describe()
