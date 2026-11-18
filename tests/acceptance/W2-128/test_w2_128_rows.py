"""W2-128 round 1: D5-ROWS rows 1 to 9 in the named templates (DEC-1109 (2)).

governance/project/orchestration/packages/LIFT-1/D5-ROWS.md: rows 1 and 7 in T-4, row 2 in T-5, rows 3, 4, 8 and 9
in T-7 and T-8, rows 5 and 6 in T-0 (row 6's pytest form also a facts command); each an imperative ending with its
decision id. One test per row: the line (a paragraph or list item, {CMD:name} read as its run form) holds the row's
substance and a bracketed decision id.
"""

from __future__ import annotations

import re

import pytest

import w2_128_support as s

LEAD_AND_CTO = ["role-lead", "role-cto"]


def _cited(hits: list[str], stem: str, row: int) -> None:
    assert hits, f"{stem}.md has no line carrying D5 row {row}"
    data = s.facts_or_empty()
    assert any(s.DEC_IN_BRACKETS.search(s.expanded(unit, data)) for unit in hits), \
        f"{stem}.md's line for D5 row {row} ends with no bracketed decision id: {hits}"


def test_row_1_t4_a_revised_case_carries_that_ticket_s_task_trailer():
    hits = s.units_with("role-test-designer", "task:", any_of=("revis", "rewrite"))
    _cited(hits, "role-test-designer", 1)


def test_row_2_t5_a_whole_branch_diff_uses_stat_or_excludes_the_acceptance_tests():
    hits = s.units_with("role-engineer", "git diff", any_of=("--stat", ":!tests/acceptance"))
    _cited(hits, "role-engineer", 2)


@pytest.mark.parametrize("stem", LEAD_AND_CTO)
def test_row_3_a_worker_brief_is_built_with_gov_brief_and_role(stem):
    # Emergency 2 (EMERGENCY-2.md 5.5, DEC-1209): gov context is switched off; a worker's brief is built by gov brief
    hits = s.units_with(stem, "gov brief", "role")
    _cited(hits, stem, 3)


@pytest.mark.parametrize("stem", LEAD_AND_CTO)
def test_row_4_a_pair_runs_under_its_ticket_s_own_id(stem):
    hits = s.units_with(stem, any_of=("pair", "coordination"), pattern=re.compile(r"\bown\b.{0,30}\bid\b"))
    _cited(hits, stem, 4)


def test_row_5_t0_no_merge_inside_the_sandbox():
    hits = [unit for unit in s.units_with("brief", "merge", "sandbox") if s.NEGATION.search(unit)]
    _cited(hits, "brief", 5)


def test_row_6_t0_and_facts_the_pytest_marker_form_empty_home_and_memory_first():
    """Row 6: T-0 and facts carry the pytest marker form with an empty HOME.

    Revised for W2-197 (EMERGENCY-2 5.4; DAEO-3d3o S3): the case required brief.md to say "no gov retrieve in the
    sandbox" (row 6's third part). W2-197 reverses it: T-0 says memory first for everyone, with no sandbox split for
    retrieve. The case now requires the opposite: no unit of brief.md denies or splits retrieve by the sandbox, and a
    unit holds "Ask memory first" with the retrieve command ({CMD:retrieve} read as its run form). The marker form and
    the empty HOME are required as before.
    """
    form = re.compile(r"""-m\s+["']not local_only["'].*-k\s+["']not real and not green_here and not time_limit["']""")
    entry = s.commands().get("pytest_folder")
    assert isinstance(entry, dict) and form.search(str(entry.get("run", ""))), \
        f"facts.yaml's pytest_folder does not carry the marker form: {entry!r}"
    data = s.facts()
    hits = [unit for unit in s.units(s.template("brief")) if form.search(s.expanded(unit, data))
            and "HOME" in s.expanded(unit, data)]
    _cited(hits, "brief", 6)
    retrieve_off = [unit for unit in s.units_with("brief", "retrieve", "sandbox") if s.NEGATION.search(unit)]
    assert not retrieve_off, f"brief.md still denies or splits gov retrieve by the sandbox (W2-197 S3): {retrieve_off}"
    first = s.units_with("brief", "ask memory first", "gov retrieve")
    assert first, "brief.md has no 'Ask memory first' unit naming the retrieve command (W2-197 S3)"


def test_row_7_t4_the_readme_map_names_every_case_by_its_full_node_id():
    hits = s.units_with("role-test-designer", "node id", any_of=("full", "::"))
    _cited(hits, "role-test-designer", 7)


@pytest.mark.parametrize("stem", LEAD_AND_CTO)
def test_row_8_no_unit_carries_the_gov_accept_outside_the_sandbox_until_w2_56_line(stem):
    """Row 8 records that the line "Run `gov accept` for a ticket whose suites need the code index outside the
    sandbox, until W2-56" is gone from both templates.

    Revised for DEC-1163 (1) (W2-182, DAEO-5y8d; a recorded rewrite by a fresh test designer, DEC-491; routed by
    DEC-1156 (7), widened by DEC-1157 (12)). Reason: the case required that line in ``role-lead.md`` and
    ``role-cto.md``; W2-56 is closed (1c02c490f), ``gov brief`` refused every lead brief ``UNTIL_CLOSED W2-56`` while
    the line stood, and the owner's DEC-1163 (1) had it deleted from both templates (and from the orchestrator
    source), commit b88a76172, so the case was red (and W2-152 S10, which runs ``gov accept W2-128``, with it).
    Decided behaviour: no unit of either template holds "gov accept", "outside", "sandbox" and "W2-56" together,
    found as the old case found it (``units_with``: each unit a paragraph or list item, ``{CMD:name}`` expanded,
    case and white space folded). What the case still catches: the line, or any rewording of it that keeps those four
    words in one unit, planted back into either template, which names the unit it found."""
    hits = s.units_with(stem, "gov accept", "outside", "sandbox", "W2-56")
    assert not hits, f"{stem}.md still carries the line telling a lead to run gov accept outside the sandbox until W2-56 (gone by DEC-1163 (1)): {hits}"


@pytest.mark.parametrize("stem", LEAD_AND_CTO)
def test_row_9_the_ticket_s_interface_is_stated_before_the_pair_starts(stem):
    hits = s.units_with(stem, "interface", "before", any_of=("pair", "start"))
    _cited(hits, stem, 9)
