"""The S0b2 glue G-24: "gov impact's radius needs the deletable-class join" (WAVE_2_TRIAGE.md).

Reading R8 (package P-3): the "deletable" class is the query class of S0b2's dev queries (W2-L322, DEC-388) that
asks whether something can be removed; the code index answers its code half ("dead code", W1-16). The join: an item
is deletable only when **neither** graph has anything that depends on it: no symbol calls it and no record names
it by an edge. What it depends on itself does not count. Each entry of ``result.change`` carries ``deletable``.
The radius of a change nothing depends on is lower than that of a change that reaches all five kinds.
"""

from __future__ import annotations

import pytest

import w2_37_support as support


def radius_number(found):
    return int(found["radius"].lstrip("R").rstrip("+"))


def deletable(found, wanted, symbol=False):
    entries = [entry for entry in found["change"]
               if (support.names_symbol(entry["id"], wanted) if symbol else entry["id"] == wanted)]
    assert len(entries) == 1, f"`change` does not name {wanted} once: {found['change']}"
    value = entries[0].get("deletable")
    assert isinstance(value, bool), f"the change {wanted} does not say whether it is deletable: {entries[0]}"
    return value


def test_a_decision_nothing_links_is_deletable_and_affects_nothing(asked):
    found = asked(support.SOLO)
    assert deletable(found, support.SOLO) is True, f"{support.SOLO}: nothing links it"
    assert support.ids_of(found) == [], f"{support.SOLO} affects {support.ids_of(found)}"


def test_a_decision_others_depend_on_is_not_deletable(asked):
    assert deletable(asked(support.CHANGED), support.CHANGED) is False, \
        f"{support.CHANGED}: DEC-002 depends on it and PROJ-ab01 implements it"


def test_the_radius_of_a_deletable_change_is_below_that_of_a_wide_one(asked):
    solo, wide = asked(support.SOLO), asked(support.CHANGED)
    assert radius_number(solo) < radius_number(wide), \
        f"{support.SOLO} (nothing affected) has radius {solo['radius']}; {support.CHANGED} (all five kinds) has " \
        f"{wide['radius']}"


@pytest.mark.local_only
def test_a_symbol_nothing_calls_and_no_record_names_is_deletable(asked_code):
    """w37_orphan calls w37_helper; nothing calls it; DEC-060 mentions it only in prose."""
    assert deletable(asked_code(support.ORPHAN), support.ORPHAN, symbol=True) is True


@pytest.mark.local_only
def test_a_symbol_nothing_calls_but_a_record_names_is_not_deletable(asked_code):
    """The join: the code graph alone would call w37_named_only dead code; DEC-051 names it."""
    found = asked_code(support.NAMED_ONLY)
    assert deletable(found, support.NAMED_ONLY, symbol=True) is False, \
        f"{support.NAMED_ONLY} is called deletable although {support.NAMING} names it"
    assert support.where(found, support.NAMING) == [("decisions", "record")], \
        f"{support.NAMING}, which names {support.NAMED_ONLY}, is not listed: {support.where(found, support.NAMING)}"


@pytest.mark.local_only
def test_a_called_symbol_is_not_deletable(asked_code):
    assert deletable(asked_code(support.HELPER), support.HELPER, symbol=True) is False
