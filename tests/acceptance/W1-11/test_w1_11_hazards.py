"""KPI success 1 and failure 1 [CAP-51.a], in a temporary register the test plants itself.

CAP-51's acceptance: "the checker flags an ACTIVE record that is superseded, a duplicate id or a cycle". The KPI
adds overlapping ids across directories. Every record here is a loadable MADR record, committed by the owner.
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import adr_path, decision


def checked(api, project, files):
    project.put({**support.CLEAN, **files})
    return api.check(project.root)


# ---- no hazard

def test_a_register_without_a_hazard_raises_no_hazard_finding(api, project):
    found = checked(api, project, {})
    raised = [finding for finding in found if finding["code"] in support.HAZARD_CODES]
    assert not raised, f"a register with no hazard was flagged:\n{support.show(raised)}"


def test_a_supersession_recorded_on_both_sides_is_not_flagged(api, project):
    found = checked(api, project, {})
    for record_id in ("ADR-0002", "ADR-0003", "ADR-0004"):
        support.assert_not_flagged(found, support.ACTIVE_SUPERSEDED, [record_id])
        support.assert_not_flagged(found, support.SUPERSESSION_CYCLE, [record_id])


# ---- ACTIVE while superseded

def test_an_active_decision_that_another_supersedes_is_flagged(api, project):
    found = checked(api, project, {
        adr_path("ADR-0010"): decision("ADR-0010", "ACTIVE"),
        adr_path("ADR-0011"): decision("ADR-0011", "ACTIVE", supersedes=["ADR-0010"]),
    })
    support.assert_flagged(found, support.ACTIVE_SUPERSEDED, ["ADR-0010"], [adr_path("ADR-0010")])
    support.assert_not_flagged(found, support.ACTIVE_SUPERSEDED, ["ADR-0011"])


def test_an_active_decision_that_names_its_own_successor_is_flagged(api, project):
    found = checked(api, project, {
        adr_path("ADR-0010"): decision("ADR-0010", "ACTIVE", superseded_by="ADR-0011"),
        adr_path("ADR-0011"): decision("ADR-0011", "ACTIVE"),
    })
    support.assert_flagged(found, support.ACTIVE_SUPERSEDED, ["ADR-0010"], [adr_path("ADR-0010")])


def test_every_active_superseded_decision_is_flagged_not_only_the_first(api, project):
    found = checked(api, project, {
        adr_path("ADR-0010"): decision("ADR-0010", "ACTIVE"),
        adr_path("ADR-0011"): decision("ADR-0011", "ACTIVE"),
        adr_path("ADR-0012"): decision("ADR-0012", "ACTIVE", supersedes=["ADR-0010", "ADR-0011"]),
    })
    for record_id in ("ADR-0010", "ADR-0011"):
        support.assert_flagged(found, support.ACTIVE_SUPERSEDED, [record_id], [adr_path(record_id)])


# ---- duplicate and overlapping ids

def test_one_id_in_two_files_of_one_directory_is_flagged(api, project):
    first, second = "docs/adr/ADR-0010-first.md", "docs/adr/ADR-0010-second.md"
    found = checked(api, project, {first: decision("ADR-0010", "PROPOSED"), second: decision("ADR-0010", "PROPOSED")})
    support.assert_flagged(found, support.DUPLICATE_ID, ["ADR-0010"], [first, second])


def test_one_id_in_two_directories_is_flagged(api, project):
    first, second = "docs/adr/ADR-0010.md", "decisions/ADR-0010.md"
    found = checked(api, project, {first: decision("ADR-0010", "PROPOSED"), second: decision("ADR-0010", "PROPOSED")})
    support.assert_flagged(found, support.DUPLICATE_ID, ["ADR-0010"], [first, second])


def test_ids_with_one_number_in_two_directories_are_flagged_as_overlapping(api, project):
    first, second = "docs/adr/ADR-0010.md", "decisions/DEC-0010.md"
    found = checked(api, project, {first: decision("ADR-0010", "PROPOSED"), second: decision("DEC-0010", "PROPOSED")})
    support.assert_flagged(found, support.OVERLAPPING_ID, ["ADR-0010", "DEC-0010"], [first, second])
    support.assert_not_flagged(found, support.DUPLICATE_ID, ["ADR-0010"])
    support.assert_not_flagged(found, support.DUPLICATE_ID, ["DEC-0010"])


# ---- supersession cycles

CYCLES = {
    "itself": {"ADR-0010": ["ADR-0010"]},
    "two": {"ADR-0010": ["ADR-0011"], "ADR-0011": ["ADR-0010"]},
    "three": {"ADR-0010": ["ADR-0011"], "ADR-0011": ["ADR-0012"], "ADR-0012": ["ADR-0010"]},
}


@pytest.mark.parametrize("name", sorted(CYCLES))
def test_a_supersession_cycle_is_flagged_with_its_members(api, project, name):
    cycle = CYCLES[name]
    found = checked(api, project, {
        adr_path(record_id): decision(record_id, "SUPERSEDED", supersedes=targets)
        for record_id, targets in cycle.items()})
    hits = support.matching(found, support.SUPERSESSION_CYCLE, sorted(cycle))
    assert hits, f"the cycle {sorted(cycle)} was not flagged:\n{support.show(found)}"
    assert any(set(hit["ids"]) == set(cycle) for hit in hits), (
        f"no cycle finding names exactly its members {sorted(cycle)}:\n{support.show(hits)}")


def test_a_cycle_closed_through_superseded_by_is_flagged(api, project):
    found = checked(api, project, {
        adr_path("ADR-0010"): decision("ADR-0010", "SUPERSEDED", supersedes=["ADR-0011"]),
        adr_path("ADR-0011"): decision("ADR-0011", "SUPERSEDED", superseded_by="ADR-0010", supersedes=["ADR-0010"]),
    })
    support.assert_flagged(found, support.SUPERSESSION_CYCLE, ["ADR-0010", "ADR-0011"])


# ---- failure 1: any planted hazard is missed

def test_every_hazard_planted_together_is_flagged(api, project):
    found = checked(api, project, {
        # ACTIVE while superseded
        adr_path("ADR-0010"): decision("ADR-0010", "ACTIVE"),
        adr_path("ADR-0011"): decision("ADR-0011", "ACTIVE", supersedes=["ADR-0010"]),
        # one id twice, across directories
        "docs/adr/ADR-0020.md": decision("ADR-0020", "PROPOSED"),
        "decisions/ADR-0020.md": decision("ADR-0020", "PROPOSED"),
        # one number under two prefixes, across directories
        "docs/adr/ADR-0030.md": decision("ADR-0030", "PROPOSED"),
        "decisions/DEC-0030.md": decision("DEC-0030", "PROPOSED"),
        # a cycle
        adr_path("ADR-0040"): decision("ADR-0040", "SUPERSEDED", supersedes=["ADR-0041"]),
        adr_path("ADR-0041"): decision("ADR-0041", "SUPERSEDED", supersedes=["ADR-0040"]),
    })
    support.assert_flagged(found, support.ACTIVE_SUPERSEDED, ["ADR-0010"])
    support.assert_flagged(found, support.DUPLICATE_ID, ["ADR-0020"], ["docs/adr/ADR-0020.md", "decisions/ADR-0020.md"])
    support.assert_flagged(found, support.OVERLAPPING_ID, ["ADR-0030", "DEC-0030"])
    support.assert_flagged(found, support.SUPERSESSION_CYCLE, ["ADR-0040", "ADR-0041"])


# ---- the interface

def test_the_same_tree_gives_the_same_findings_twice(api, project):
    project.put({**support.CLEAN,
                 adr_path("ADR-0010"): decision("ADR-0010", "ACTIVE"),
                 adr_path("ADR-0011"): decision("ADR-0011", "ACTIVE", supersedes=["ADR-0010"]),
                 "decisions/DEC-0010.md": decision("DEC-0010", "PROPOSED")})
    first = api.check(project.root)
    assert first, "nothing was flagged"
    assert api.check(project.root) == first


def test_a_folder_that_is_no_git_repository_is_an_error_not_a_pass(api, tmp_path):
    folder = tmp_path / "plain"
    (folder / "docs" / "adr").mkdir(parents=True)
    (folder / adr_path("ADR-0010")).write_text(decision("ADR-0010", "ACTIVE"), encoding="utf-8")
    with pytest.raises(support.Raised) as raised:
        api.check_only(folder)
    assert isinstance(raised.value.code, str) and raised.value.code, "the GovError has no code"
    assert isinstance(raised.value.details, dict), "the GovError's details are not a map"
