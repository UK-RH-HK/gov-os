"""F1 (as the CTO amended it at the land): a close never records a decision it did not resolve as applied.

Reads the records of the worlds of S5 (decisions that no longer stand) and S6 (ids no register holds, in the sources,
the decisions list and a KPI line; no register named; an archived register beside the register).
"""

from __future__ import annotations

import w2_200_support as s


def _applied_and_hashed(world):
    s.closed(world.run)
    record = world.project.record()
    assert isinstance(record.get("decisions_applied"), list), f"no decisions_applied: {sorted(record)}"
    return set(record["decisions_applied"]), set(s.input_hashes(record))


def test_f1_a_decision_that_no_longer_stands_is_never_applied_nor_hashed(s5_world):
    applied, hashed = _applied_and_hashed(s5_world)
    for item in s.S5_NOT_STANDING:
        assert item["id"] not in applied, f"{item['id']} ({item['status']}) is in decisions_applied"
        assert item["id"] not in hashed, f"{item['id']} ({item['status']}) has a hash in inputs"


def test_f1_an_id_neither_register_holds_is_never_applied_nor_hashed(s6_unresolved, s6_kpi_only, s6_no_register,
                                                                     s6_archive):
    worlds = ((s6_unresolved, s.S6_MISSING), (s6_kpi_only, [s.S6_KPI_ONLY]), (s6_no_register, s.S6_UNNAMED),
              (s6_archive, [s.S6_IN_NEITHER]))
    for world, missing in worlds:
        applied, hashed = _applied_and_hashed(world)
        for rid in missing:
            assert rid not in applied, f"{rid}, which no register holds, is in decisions_applied"
            assert rid not in hashed, f"{rid}, which no register holds, has a hash in inputs"


def test_f1_an_archived_decision_is_never_applied_nor_hashed(s6_archive):
    applied, hashed = _applied_and_hashed(s6_archive)
    assert applied, "the archive world applied nothing: the register's own DEC-110 is cited"
    for item in s.S6_ARCHIVED:
        assert item["id"] not in applied, f"{item['id']} (archived) is in decisions_applied"
        assert item["id"] not in hashed, f"{item['id']} (archived) has a hash in inputs"
