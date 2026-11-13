"""W2-33 S1, S3, S6, S8: the files of the three layers and what the QA engineer's, the ticket lead's, the Senior
Engineer's and the CTO's files state. Tests read files only (``template/governance/kernel/roles/``).

Readings (also in README.md): the ticket gives no line heads for the reads, writes and handover of S1 and S8, so the
heads W1-33's files use today (``Allowed paths``, ``Handoff format``) and ROLES-SPEC-1's (``Reads``, ``Writes``,
``Handover``) are both accepted; a head must carry at least five words. A statement is judged by the KPI's own words,
case-insensitive and whitespace-normalised.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_33_support as W  # noqa: E402

FOLDER = W.roles_dir()


def _text(name):
    text = W.read(FOLDER, name)
    assert text is not None, f"{W.ROLES_REL}/{name}.md does not exist"
    return text


# ---------------------------------------------------------------------------------------------------- S1

def test_s1_ticket_lead_role_file_exists():
    assert (FOLDER / "ticket-lead.md").is_file(), f"{W.ROLES_REL}/ticket-lead.md does not exist (S1, ROLES-SPEC-1 §3.3)"


def test_s1_ticket_lead_names_its_reads_writes_and_handover():
    W.matcher_selfcheck("s1")
    faults = W.s1_ticket_lead(_text("ticket-lead"))
    assert not faults, "\n".join(faults)


def test_s1_orchestrator_no_longer_carries_the_ticket_lead_heading():
    text = _text("orchestrator")
    found = [(number, line) for number, line in enumerate(text.splitlines(), 1)
             if re.match(r"^\s*#{1,6}\s+The ticket lead\b", line, re.IGNORECASE)]
    assert not found, (f"{W.ROLES_REL}/orchestrator.md still has {len(found)} line(s) with the heading "
                       f"'## The ticket lead' (S1 wants 0): {found}")


# ---------------------------------------------------------------------------------------------------- S3

def test_s3_independent_reviewer_file_does_not_exist():
    """Green before the work, and guards it: the QA engineer replaces the independent reviewer (DEC-959 item 3)."""
    assert not (FOLDER / "independent-reviewer.md").exists(), (
        f"{W.ROLES_REL}/independent-reviewer.md exists: qa-engineer.md replaces it")


def test_s3_qa_engineer_role_file_exists():
    assert (FOLDER / "qa-engineer.md").is_file(), f"{W.ROLES_REL}/qa-engineer.md does not exist (S3)"


def test_s3_qa_engineer_reads_spec_kpis_tests_and_code_changes_none_writes_only_its_findings_report():
    W.matcher_selfcheck("s3-access")
    faults = W.s3_qa_access(_text("qa-engineer"))
    assert not faults, "\n".join(faults)


def test_s3_qa_engineer_states_the_per_stream_rule():
    W.matcher_selfcheck("s3-stream")
    faults = W.s3_per_stream(_text("qa-engineer"))
    assert not faults, "\n".join(faults)


def test_s3_independent_auditor_still_names_the_milestone_audits():
    """Green before the work, and guards it: the auditor keeps the milestone audits (its file names the milestone)."""
    text = W.normalise(_text("independent-auditor"))
    assert re.search(r"\bmilestone[\s-]+audit\w*", text, re.IGNORECASE), (
        "independent-auditor.md no longer names the milestone audits")


# ---------------------------------------------------------------------------------------------------- S6

@pytest.mark.parametrize("head", sorted(W.S6_HEADS))
def test_s6_qa_engineer_states(head):
    W.matcher_selfcheck("s6")
    faults = W.s6_heads(_text("qa-engineer"))[head]
    assert not faults, "\n".join(faults)


# ---------------------------------------------------------------------------------------------------- S8

def test_s8_senior_engineer_role_file_exists():
    assert (FOLDER / "senior-engineer.md").is_file(), f"{W.ROLES_REL}/senior-engineer.md does not exist (S8)"


def test_s8_senior_engineer_holds_reads_writes_skills_default_brief_and_handover():
    W.matcher_selfcheck("s8")
    faults = W.s8_senior_engineer(_text("senior-engineer"))
    assert not faults, "\n".join(faults)


def test_s8_orchestrator_file_is_the_ctos_and_keeps_its_id():
    text = W.normalise(_text("orchestrator"))
    assert re.search(r"\bCTO\b|master orchestrator", text, re.IGNORECASE), (
        "orchestrator.md names neither the CTO nor the master orchestrator: it must be the CTO's file")
    assert "GOV_ROLE=orchestrator" in text, "orchestrator.md no longer keeps its role id (GOV_ROLE=orchestrator)"
