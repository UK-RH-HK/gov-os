"""Stage A6: controlled migration [CAP-44.d], and failure line 1 ("Any file content changes during a move batch").

Success line 2: "a failed batch rolls back to its recorded point; moves precede gov rebuild". Every batch ends in a
commit of the temporary project; its rollback point is a ref of that project which resolves to the commit the batch
started from. All of these cases move files, so they need the code graph (README, "Where the cases can run").
"""

from __future__ import annotations

import os

import pytest

import w1_41_support as support

MOVES = {item["path"]: item["target"] for item in support.moves_proposal()}
BATCH_OF = {item["path"]: item["batch"] for item in support.moves_proposal()}


def _evidence_folders(adoption):
    return {os.path.dirname(stage.record) for stage in adoption.stages.values()}


def _is_evidence(adoption, rel):
    return any(folder and rel.startswith(folder + "/") for folder in _evidence_folders(adoption))


def _batches(adoption):
    """Batch number -> its entry in the A6 record."""
    stage = adoption.stages["A6"]
    listed = stage.front.get("batches")
    assert isinstance(listed, list) and listed, f"{stage.record}: no list 'batches'"
    return {item.get("batch"): item for item in listed}


def test_every_moved_file_is_byte_for_byte_what_it_was(adoption, project):
    baseline = support.tree(project)
    adoption.through("A6", support.moves_proposal())
    now = support.tree(project)
    for origin, target in MOVES.items():
        assert origin not in now and not (project / origin).exists(), f"{origin} is still at its origin"
        assert now.get(target) == baseline[origin], \
            f"{target} does not hold byte for byte what {origin} held before the move"
        assert (project / target).is_file(), f"{target} is not in the working tree"


def test_no_other_tracked_file_changes_content_during_a_move_batch(adoption, project):
    """Failure line 1, batch by batch. Between a batch's rollback point and its commit: a path that is in both
    holds the same content; a path that appears is a planned target holding its origin's content, or one of the
    tool's own records; a path that disappears is a planned origin of that batch."""
    adoption.through("A6", support.moves_proposal())
    done = _batches(adoption)
    assert sorted(done) == [1, 2, 3], f"the A6 record does not list the three batches: {sorted(done)}"
    for number, item in sorted(done.items()):
        assert item.get("status") == "done", f"batch {number} is not recorded as done: {item.get('status')!r}"
        before_commit = support.resolve(project, item.get("rollback_point") or "")
        after_commit = support.resolve(project, item.get("commit") or "")
        assert before_commit, f"batch {number}: its rollback point {item.get('rollback_point')!r} does not resolve"
        assert after_commit and after_commit != before_commit, f"batch {number}: no commit of its own"
        before, after = support.tree(project, before_commit), support.tree(project, after_commit)
        planned = {origin: target for origin, target in MOVES.items() if BATCH_OF[origin] == number}
        changed = sorted(rel for rel in before.keys() & after.keys() if before[rel] != after[rel])
        assert not changed, f"batch {number} changed the content of {changed}"
        removed = set(before) - set(after)
        assert removed == set(planned), \
            f"batch {number} removed {sorted(removed)}; its planned origins are {sorted(planned)}"
        for rel in set(after) - set(before):
            if rel in planned.values():
                origin = next(origin for origin, target in planned.items() if target == rel)
                assert after[rel] == before[origin], f"batch {number}: {rel} is not byte for byte {origin}"
            else:
                assert _is_evidence(adoption, rel), f"batch {number} added {rel}, which is no planned target"


def test_the_rollback_points_are_the_ones_the_plan_recorded(adoption, project):
    adoption.through("A6", support.moves_proposal())
    planned = {item["batch"]: item["rollback_point"] for item in adoption.stages["A4"].front["batches"]}
    executed = {number: item.get("rollback_point") for number, item in _batches(adoption).items()}
    assert executed == planned, f"A6 used other rollback points ({executed}) than A4 recorded ({planned})"


def test_a_failed_batch_rolls_back_to_its_point_and_the_batches_before_it_stay(adoption, project, interface):
    """Batch 2 cannot be completed: the folder of one of its two targets exists and takes no new file. Batch 1
    stays; batch 2 is undone as a whole (its other move too); batch 3 does not run; the tree is what it was at
    batch 2's rollback point."""
    baseline = support.tree(project)
    adoption.through("A5", support.moves_proposal())
    locked = project / os.path.dirname(support.MOVED_RECORD_TARGET)   # spec/decisions: holds dec-301.md already
    mode = locked.stat().st_mode
    locked.chmod(0o555)
    try:
        if os.access(locked, os.W_OK):
            pytest.skip("this user is not held by folder permissions: the batch cannot be made to fail this way")
        assert support.porcelain(project) == "", "the fixture made the tree dirty"
        run = adoption.run("A6")
    finally:
        locked.chmod(mode)
    support.assert_refused(run, interface, any_of=(support.MOVED_RECORD, support.MOVED_RECORD_TARGET))
    point = {item["batch"]: item["rollback_point"] for item in adoption.stages["A4"].front["batches"]}[2]
    commit = support.resolve(project, point)
    assert commit, f"batch 2's rollback point {point} does not resolve after the failure"
    at_point, now = support.tree(project, commit), support.tree(project)
    # Batch 1 stays, and it is in the rollback point of batch 2.
    assert at_point.get(support.GUIDE_TARGET) == baseline[support.GUIDE] and support.GUIDE not in at_point, \
        "batch 2's rollback point does not hold batch 1's move"
    # The tree is what it was at that point (the tool's own records apart).
    differing = sorted(rel for rel in set(at_point) | set(now)
                       if at_point.get(rel) != now.get(rel) and not _is_evidence(adoption, rel))
    assert not differing, f"after the rollback the tree differs from batch 2's rollback point in {differing}"
    assert support.porcelain(project) == "", \
        f"after the rollback the working tree is not clean:\n{support.porcelain(project)}"
    # Batch 2 as a whole is undone, and batch 3 did not run.
    for origin in (support.NOTES, support.MOVED_RECORD, support.UTIL):
        assert now.get(origin) == baseline[origin] and (project / origin).is_file(), f"{origin} is not at its origin"
        assert not (project / MOVES[origin]).exists(), f"{MOVES[origin]} exists after the rollback"


def test_the_index_refresh_follows_the_moves(adoption, project, sandbox):
    """"Moves precede gov rebuild": no index of the old layout is built on the way, and after the moves the index
    is fresh at the new layout (measured by ``gov doctor`` in the temporary project)."""
    adoption.through("A5", support.moves_proposal())
    before = support.doctor_section(project, sandbox, "index_freshness")
    assert before.get("index_status") != "fresh", \
        f"an index was built before any move (index_status: {before.get('index_status')!r})"
    adoption.ok("A6")
    after = support.doctor_section(project, sandbox, "index_freshness")
    assert after.get("index_status") == "fresh", \
        f"after the moves the index is not fresh (index_status: {after.get('index_status')!r}, " \
        f"stale: {after.get('stale')})"


def test_a_backup_ref_that_no_longer_resolves_stops_the_migration(adoption, project, interface):
    """DEC-449: the safety baseline is measured, not assumed. Without the backup ref A0 recorded, nothing moves."""
    adoption.through("A5", support.moves_proposal())
    ref = adoption.stages["A0"].front["backup_ref"]
    support.git(project, "update-ref", "-d", ref)
    baseline = support.tree(project)
    run = adoption.run("A6")
    support.assert_refused(run, interface, ref)
    problems = support.moved_nothing(project, baseline, list(MOVES))
    assert not problems, f"files moved although the backup ref does not resolve: {problems}"


def test_a_tree_that_is_dirty_at_a6_is_not_migrated(adoption, project, interface):
    adoption.through("A5", support.moves_proposal())
    baseline = support.tree(project)
    support.write(project, "scratch.txt", "left behind\n")
    run = adoption.run("A6")
    support.assert_refused(run, interface, "scratch.txt")
    problems = support.moved_nothing(project, baseline, list(MOVES))
    assert not problems, f"files moved in a dirty tree: {problems}"
