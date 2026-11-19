"""F1: a close never records a decision it did not resolve as applied, and a refusal leaves nothing.

Reads the worlds of S5 (decisions that no longer stand) and S6 (a missing id in a KPI line; a missing id in the
sources, refused; no register named).
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


def test_f1_an_id_the_register_does_not_hold_is_never_applied_nor_hashed(s6_kpi_only, s6_no_register):
    for world, missing in ((s6_kpi_only, [s.S6_KPI_ONLY]), (s6_no_register, s.S6_UNNAMED)):
        applied, hashed = _applied_and_hashed(world)
        for rid in missing:
            assert rid not in applied and rid not in hashed, f"{rid}, which the register does not hold, is applied"


def test_f1_a_refused_close_leaves_no_record_no_checkpoint_and_no_state_change(s6_refused):
    project, before = s6_refused.project, s6_refused.before
    assert s6_refused.run.envelope()["ok"] is False, s6_refused.run.describe()
    assert not project.record_path().exists(), "a refused close left a close record"
    assert project.checkpoints() == before.checkpoints, "a refused close left a checkpoint"
    assert project.status() == before.status and project.head() == before.head, "a refused close changed the tree"
    assert project.iteration_file().exists() == before.iteration, "a refused close changed the iteration count"
    status = s.front_of((project.root / f".tickets/{s.TICKET}.md").read_text(encoding="utf-8")).get("status")
    assert status == "in_progress", f"the ticket's status is {status!r} after a refused close"
