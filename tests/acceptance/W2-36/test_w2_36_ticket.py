"""S6: a spec that passes becomes a feature ticket a test designer can test, accepted by gov brief."""

from __future__ import annotations

import re

import pytest

import w2_36_support as support

KS = {"K1": (support.K1, support.K1_FAILS, support.K1_VERIFY), "K2": (support.K2, support.K2_FAILS, support.K2_VERIFY)}


def text(value):
    return support.plain(value).rstrip(".")


def feature(outcome):
    assert outcome.run.returncode == 0, f"gov discover --ticket did not exit 0:\n{outcome.run.describe()}"
    assert len(outcome.new_tickets) == 1, f"expected exactly one new ticket, got {outcome.new_tickets}"
    return outcome.new_tickets[0], support.ticket(outcome.project, outcome.new_tickets[0])


def test_ticket_writes_exactly_one_new_ticket_and_nothing_else(ticketed):
    ticket_id, _ = feature(ticketed)
    assert ticketed.porcelain_before == []
    assert support.porcelain_paths(ticketed.project) == [f".tickets/{ticket_id}.md"], ticketed.porcelain_after


def test_feature_ticket_is_an_engineer_ticket_of_the_spec_with_its_paths_non_goals_and_test_path(ticketed):
    ticket_id, front = feature(ticketed)
    assert front.get("class") == "implementation"
    assert front.get("role") == "engineer"
    assert front.get("specification") == support.SPEC_ID
    assert front.get("allowed_paths") == ["src/report/**", "tests/unit/report/**"]
    assert [text(item) for item in front.get("non_goals") or []] == [text(item) for item in support.NON_GOALS]
    for name in ("reads", "needs", "waits_on"):
        assert isinstance(front.get(name), list), f"{name}: {front.get(name)!r}"
    assert front.get("profile") == "LITE"
    assert (front.get("acceptance_tests") or {}).get("path") == f"tests/acceptance/{ticket_id}/"


def test_feature_ticket_has_a_success_and_a_failure_line_per_k_each_with_the_ks_verify(ticketed):
    _, front = feature(ticketed)
    success, failure = support.kpi_items(front, "success"), support.kpi_items(front, "failure")
    assert len(success) == len(KS) and len(failure) == len(KS), front.get("kpis")
    for kpi, (behaviour, fails, verify) in KS.items():
        lines = [(line, check) for line, check in success
                 if re.search(rf"\b{kpi}\b", line) and text(behaviour) in support.plain(line)]
        assert len(lines) == 1, f"{kpi}: no single success line holding its behaviour and id: {success}"
        assert text(verify) in support.plain(lines[0][1]), f"{kpi}: success verify {lines[0][1]!r}"
        lines = [(line, check) for line, check in failure if text(fails) in support.plain(line)]
        assert len(lines) == 1, f"{kpi}: no single failure line holding its Fails if: text: {failure}"
        assert text(verify) in support.plain(lines[0][1]), f"{kpi}: failure verify {lines[0][1]!r}"


@pytest.mark.parametrize("role", ["independent-test-designer", "engineer"])
def test_gov_brief_accepts_the_feature_ticket_and_its_kpi_table_holds_every_k(ticketed, home, role):
    ticket_id, _ = feature(ticketed)
    brief = support.gov(ticketed.project, "brief", role, ticket_id, home=home)
    assert brief.returncode == 0, brief.describe()
    table = [re.match(r"^\|\s*([SF]\d+)\s*\|(.*)\|(.*)\|\s*$", line) for line in brief.stdout.splitlines()]
    table = [(m.group(1), support.plain(m.group(2)), support.plain(m.group(3))) for m in table if m]
    assert len(table) == 2 * len(KS), f"KPI table rows: {table}"
    assert all(verify and verify != "none" for _, _, verify in table), table
    for kpi, (behaviour, fails, verify) in KS.items():
        assert any(text(behaviour) in line and text(verify) in check for _, line, check in table), (kpi, table)
        assert any(text(fails) in line and text(verify) in check for _, line, check in table), (kpi, table)
