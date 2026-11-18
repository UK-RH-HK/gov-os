"""S1 (discovery opens from an idea and reads what exists) and S7 (the same request in plain language)."""

from __future__ import annotations

import re

import yaml

import w2_36_support as support
from w2_36_support import opened, spec_text


def normalised(text, outcome, words):
    """A section with the run's own ticket id, root and words replaced, for comparing two runs."""
    text = text.replace(str(outcome.project), "<ROOT>").replace(words, "<WORDS>")
    for ticket_id in outcome.new_tickets:
        text = text.replace(ticket_id, "<TICKET>")
    return text


# --- S1 -------------------------------------------------------------------------------------------------------------

def test_discovery_writes_one_ticket_and_one_change_folder_and_nothing_else(discovered):
    ticket_id = opened(discovered)
    assert discovered.porcelain_before == []
    expected = sorted([f".tickets/{ticket_id}.md", *(f"{support.CHANGE_REL}/{name}" for name in support.CHANGE_FILES)])
    assert support.porcelain_paths(discovered.project) == expected, discovered.porcelain_after
    changes = sorted(p.name for p in (discovered.project / "openspec/changes").iterdir())
    assert changes == [support.CHANGE]


def test_json_result_names_the_change_the_spec_id_the_ticket_and_the_spec_path(discovered):
    ticket_id = opened(discovered)
    envelope = discovered.run.envelope()
    assert envelope is not None and envelope.get("ok") is True, discovered.run.describe()
    values = list(support.leaves(envelope.get("result")))
    assert support.CHANGE in values, values
    assert support.SPEC_ID in values, values
    assert ticket_id in values, values
    assert any(value.endswith(support.SPEC_REL) for value in values), values


def test_proposal_front_matter_is_a_lite_draft_specification_naming_its_ticket(discovered):
    ticket_id = opened(discovered)
    front = support.front_matter(discovered.project / support.CHANGE_REL / "proposal.md")
    assert front.get("type") == "specification"
    assert front.get("id") == support.SPEC_ID
    assert front.get("status") == "DRAFT"
    assert front.get("profile") == "LITE"
    assert front.get("spine") is False
    assert front.get("capability_types") == []
    assert front.get("discovery_ticket") == ticket_id


def test_readiness_holds_the_26_rows_all_missing_and_unlinked(discovered):
    opened(discovered)
    record = yaml.safe_load((discovered.project / support.CHANGE_REL / "readiness.yaml").read_text(encoding="utf-8"))
    rows = record.get("rows") if isinstance(record, dict) else None
    assert isinstance(rows, list) and len(rows) == 26, record
    assert [(row.get("n"), row.get("key")) for row in rows] == [(n, key) for n, (key, _) in support.ROWS.items()]
    assert all(row.get("state") == "MISSING" for row in rows), rows
    assert all("gap_ticket" in row and row["gap_ticket"] is None for row in rows), rows


def test_discovery_ticket_is_a_product_spec_ticket_whose_verify_is_the_check(discovered):
    ticket_id = opened(discovered)
    front = support.ticket(discovered.project, ticket_id)
    assert front.get("class") == "specification"
    assert front.get("role") == "product-spec"
    assert support.CHANGE in str(front.get("discovers") or ""), front.get("discovers")
    assert "specification" not in front
    assert front.get("allowed_paths") == [f"{support.CHANGE_REL}/**"]
    for name in ("reads", "needs", "waits_on"):
        assert isinstance(front.get(name), list), f"{name}: {front.get(name)!r}"
    verifies = [support.plain(verify) for _, verify in support.kpi_items(front, "success")]
    assert any(f"gov discover --check {support.CHANGE}" in verify for verify in verifies), verifies


def test_sources_read_lists_the_three_matching_files_and_says_memory_is_not_available(discovered):
    opened(discovered)
    part = support.sections(spec_text(discovered)).get("Sources read")
    assert part is not None, "spec.md has no ## Sources read"
    for rel in support.SOURCES:
        assert rel in part, f"{rel} is not listed:\n{part}"
    assert support.UNRELATED not in part, part
    assert re.search(r"Memory: not available\W+\w", part), part


# --- S7 -------------------------------------------------------------------------------------------------------------

def test_plain_request_makes_the_same_change_and_files_and_one_ticket(discovered_plain):
    ticket_id = opened(discovered_plain)
    expected = sorted([f".tickets/{ticket_id}.md", *(f"{support.CHANGE_REL}/{name}" for name in support.CHANGE_FILES)])
    assert support.porcelain_paths(discovered_plain.project) == expected, discovered_plain.porcelain_after


def test_plain_request_problem_holds_its_words_verbatim(discovered_plain):
    opened(discovered_plain)
    problem = support.sections(spec_text(discovered_plain)).get("Problem") or ""
    assert support.PLAIN_TEXT in problem, problem


def test_plain_request_reads_the_same_sources_and_asks_the_same_packages(discovered, discovered_plain):
    opened(discovered_plain)
    opened(discovered)
    first, plain = support.sections(spec_text(discovered)), support.sections(spec_text(discovered_plain))
    for name in ("Sources read", "Open questions"):
        assert normalised(plain.get(name) or "", discovered_plain, support.PLAIN_TEXT) == \
            normalised(first.get(name) or "", discovered, support.WORDS), f"## {name} differs from the first run"
