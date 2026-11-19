"""S5: a cited decision that no longer stands is recorded as such and never refuses the close.

``s5_world`` cites from ``sources`` one decision in each state: DEC-120 stands; DEC-121 is SUPERSEDED by its status
word, DEC-122 by a successor's ``**Supersedes:**`` line (its own status ACCEPTED), DEC-123 by "SUPERSEDED by DEC-128";
DEC-124 is RETIRED, DEC-125 REJECTED; DEC-126 is tagged done (it still stands).
"""

from __future__ import annotations

import w2_200_support as s


def _record(world):
    s.closed(world.run)
    return world.project.record()


def test_s5_the_close_passes_and_applies_the_standing_and_the_done_tagged(s5_world):
    record = _record(s5_world)
    assert record.get("decisions_applied") == s.S5_APPLIED, f"decisions_applied: {record.get('decisions_applied')!r}"


def test_s5_the_others_are_listed_not_standing_with_their_states_sorted_by_number(s5_world):
    record = _record(s5_world)
    assert record.get("decisions_not_standing") == s.S5_NOT_STANDING, \
        f"decisions_not_standing: {record.get('decisions_not_standing')!r}"


def test_s5_no_decision_is_both_applied_and_not_standing(s5_world):
    record = _record(s5_world)
    applied = set(record.get("decisions_applied") or [])
    not_standing = {item.get("id") for item in record.get("decisions_not_standing") or []}
    assert applied and not_standing and not applied & not_standing, f"in both lists: {sorted(applied & not_standing)}"
    assert record.get("decisions_unresolved") == [], f"decisions_unresolved: {record.get('decisions_unresolved')!r}"
