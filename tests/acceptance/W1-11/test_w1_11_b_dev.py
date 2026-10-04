"""KPI success 1 and failure 1 [CAP-51.a], on the b-dev fixtures HZ-B-03, HZ-B-04 and HZ-B-06.

The tier keeps decisions in two directories, ``docs/adr/`` (ADR-001 to ADR-008) and ``decisions/`` (DEC-001 to
DEC-006). Their frontmatter has ``id``, ``title``, ``status``, ``date`` and ``author``: no ``type``, so the store
of W1-10 does not load them as records, and no ``supersedes`` or ``superseded_by`` anywhere. The checker reads
them as decision files all the same: a Markdown file whose frontmatter ``id`` fits the ``decision_id`` grammar.

- As planted, the tier holds one of the KPI's three classes in its frontmatter: ids that overlap across the two
  directories (HZ-B-06, "two ADR directories with overlapping numbering"). The first test asserts it.
- HZ-B-03's supersession stands only in prose ("no formal link"), and the tier plants no cycle. The other tests
  write the link the hazard describes into a clone and check that (package DP-1).

Every test works in its own clone; the tier itself is never checked or written.
"""

from __future__ import annotations

import pytest

import w1_11_support as support

pytestmark = pytest.mark.local_only

OVERLAPPING_NUMBERS = ("001", "002", "003", "004", "005", "006")
ADR_003, DEC_003 = "docs/adr/adr-003.md", "decisions/dec-003.md"


def add_key(project, rel, line):
    """Add one frontmatter line to a decision file of the clone, before its ``status`` line."""
    path = project.root / rel
    text = path.read_text(encoding="utf-8")
    head, marker, rest = text.partition("\nstatus:")
    assert marker, f"{rel} has no status line"
    path.write_text(f"{head}\n{line}{marker}{rest}", encoding="utf-8")


def test_the_overlapping_ids_of_the_two_decision_directories_are_flagged(api, b_dev):
    """HZ-B-06, and the id overlap at the locations of HZ-B-03 (ADR-003, DEC-003) and HZ-B-04 (ADR-002, DEC-001)."""
    found = api.check(b_dev.root)
    for number in OVERLAPPING_NUMBERS:
        support.assert_flagged(found, support.OVERLAPPING_ID, [f"ADR-{number}", f"DEC-{number}"],
                               [f"docs/adr/adr-{number}.md", f"decisions/dec-{number}.md"])


def test_adr_003_is_flagged_as_active_while_superseded_once_dec_003_names_it(api, b_dev):
    """HZ-B-03: "ADR-003 status=ACTIVE (should be SUPERSEDED). DEC-003 has no supersedes field"."""
    add_key(b_dev, DEC_003, "supersedes: [ADR-003]")
    b_dev.commit("DEC-003 names what it supersedes")
    found = api.check(b_dev.root)
    support.assert_flagged(found, support.ACTIVE_SUPERSEDED, ["ADR-003"], [ADR_003])


def test_a_supersession_cycle_between_the_two_directories_is_flagged(api, b_dev):
    add_key(b_dev, DEC_003, "supersedes: [ADR-003]")
    add_key(b_dev, ADR_003, "supersedes: [DEC-003]")
    b_dev.commit("ADR-003 and DEC-003 supersede each other")
    found = api.check(b_dev.root)
    support.assert_flagged(found, support.SUPERSESSION_CYCLE, ["ADR-003", "DEC-003"])


def test_one_id_in_both_decision_directories_is_flagged(api, b_dev):
    path = b_dev.root / "decisions/dec-001.md"
    text = path.read_text(encoding="utf-8")
    assert "id: DEC-001\n" in text
    path.write_text(text.replace("id: DEC-001\n", "id: ADR-001\n", 1), encoding="utf-8")
    b_dev.commit("decisions/dec-001.md takes the id of docs/adr/adr-001.md")
    found = api.check(b_dev.root)
    support.assert_flagged(found, support.DUPLICATE_ID, ["ADR-001"], ["docs/adr/adr-001.md", "decisions/dec-001.md"])


def test_the_tier_is_byte_identical_after_the_check(api, b_dev):
    """KPI success 3 and failure 2, on the tier."""
    api.load(b_dev.root)
    before = support.snapshot(b_dev.root)
    found = api.check_only(b_dev.root)
    assert found, "nothing was flagged on b-dev"
    assert support.changed(before, support.snapshot(b_dev.root)) == []
