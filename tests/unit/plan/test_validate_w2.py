"""Builder regression tests for docs/plan/tools/validate_w2.py (W2-51). The acceptance tests are in tests/acceptance/W2-51/."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "docs" / "plan" / "tools" / "validate_w2.py"


@pytest.fixture
def v(tmp_path):
    spec = importlib.util.spec_from_file_location("validate_w2", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.ROOT = tmp_path
    return mod


def _w(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_cit_p_lines_read_w2_49s_form(v, tmp_path):
    """A commented `- id:` with a folded item is a line; a `# unchanged` entry and a non-yaml fence are not."""
    _w(tmp_path, "docs/changes/W2-49-CIT-P.md", "\n".join([
        "```yaml", "  covers:", "  - id: CAP-44.h            # written with the recommended answers",
        "    item: 'Adoption verdict, lite: ADOPTED_HEALTHY from a fresh",
        "      Independent Auditor'", "    wave: W2", "  - id: CAP-43.c            # unchanged, W3", "```",
        "```text", "  - id: CAP-43.d", "    wave: W3", "```", ""]))
    assert v.cit_p_lines() == [("W2-49-CIT-P.md", "CAP-44.h", "W2")]


def test_wbs_id_wins_over_external_ref(v, tmp_path):
    """DEC-730: external-ref is read only when there is no wbs_id; a W1 wbs_id is not a Wave 2 ticket."""
    _w(tmp_path, ".tickets/a.md", "---\nwbs_id: W1-07\nexternal-ref: W2-07\n---\n# a\n")
    _w(tmp_path, ".tickets/b.md", "---\nexternal-ref: W2-15a\n---\n# b\n")
    assert [w2 for w2, _, _ in v.tickets()] == ["W2-15a"]


def test_a_ticket_with_no_frontmatter_is_a_named_failure(v, tmp_path):
    _w(tmp_path, ".tickets/c.md", "# no frontmatter\n")
    with pytest.raises(v.Unreadable, match=r"\.tickets/c\.md"):
        v.tickets()


def _plan(root, card_ids, ticket_ids):
    """A WBS whose §1 table holds W2-01 and whose §2 holds a card per id in `card_ids`; a ticket per id in `ticket_ids`."""
    cards = [f"#### {i} A later ticket (STANDARD, engineer)\n- **Why:** planted.\n" for i in card_ids]
    _w(root, "docs/plan/WAVE_2_WBS.md", "\n".join([
        "# Wave 2", "", "## 1. Tickets", "", "| W2 | Title |", "|---|---|", "| **W2-01** | First |", "",
        "- The later tickets (W2-59 onwards) are in §2's cards only.", "", "## 2. Ticket cards", "",
        "#### W2-01 First (FULL, engineer)", "", "### Track C", "", *cards,
        "#### W2-81's held-out half (proposed companion)", "", "## 3. Order", "", "#### W2-98 not a card here", ""]))
    for i in ticket_ids:
        _w(root, f".tickets/{i}.md", f"---\nwbs_id: {i}\n---\n# {i}\n")


def test_an_id_only_in_a_section_2_card_passes_wave2_tickets(v, tmp_path):
    """D-10 (DEC-1112 (3)): the later tickets are in §2's cards only, and the PASS line counts each source."""
    _plan(tmp_path, ["W2-59", "W2-60a"], ["W2-01", "W2-59", "W2-60a"])
    ok, reason = v.check_wave2_tickets()
    assert ok, reason
    assert "3 W2 ids" in reason and "1 in the §1 table" in reason and "2 in §2's cards only" in reason


def test_a_card_id_with_no_ticket_fails_wave2_tickets(v, tmp_path):
    """A card with no ticket still fails, named; a ticket with neither a row nor a card too; `W2-81's` and §3 are not cards."""
    _plan(tmp_path, ["W2-59", "W2-60"], ["W2-01", "W2-59", "W2-63"])
    ok, reason = v.check_wave2_tickets()
    assert not ok
    assert reason == "ids on one side only: W2-60 (WBS §2 card only), W2-63 (.tickets/ only)"


def test_a_contract_id_inside_a_longer_name_is_not_a_contract_id(v, tmp_path):
    """ACT-OLLAMA-CAP-1 is an ACT name, not CAP-1; a bare CAP-1 the Contract lacks is still reported."""
    _w(tmp_path, "docs/contract/contract.yaml",
       "capabilities:\n  - id: CAP-10\n    covers:\n      - id: CAP-10.a\n        wave: W2\n")
    _w(tmp_path, ".tickets/a.md", "---\nwbs_id: W2-20\n---\n# a\nCloses it [ACT-OLLAMA-CAP-1, ACT-OLLAMA-CAP-2, CAP-10.a]\n")
    ok, reason = v.check_ids_exist()
    assert ok, reason
    _w(tmp_path, ".tickets/b.md", "---\nwbs_id: W2-21\n---\n# b\nCites CAP-1 and S0a-CAP-13.\n")
    v.tickets.cache_clear()
    ok, reason = v.check_ids_exist()
    assert (ok, reason) == (False, "not in the Contract: CAP-1 (W2-21)")
