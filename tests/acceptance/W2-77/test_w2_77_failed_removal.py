"""S3: if the removal of its own clone fails, the nightly removes only that clone's own administrative entry (by its
exact name under the common git directory), or reports the failure in its record; it never touches another
worktree's entry [DEC-939 item 5, DEC-866].

The removal is made to fail deterministically with real git: the night's own suite locks the worktree it runs in
(``git worktree lock``), and a single ``--force`` does not remove a locked worktree. Before the night:

- a registered worktree whose folder is also called ``tree``, holding a staged change: it holds the entry name
  ``tree``, so the clone (also a folder ``tree``) gets another entry name (``tree1``); an entry guessed from the
  clone's folder name would be this worktree's;
- a stale registration (a worktree added, its folder deleted).

The failure must be in the night's record (its ``cleanup`` key: ``ok: false``, the clone, its entry or null,
``entry_removed``, the error) and on standard error (one line naming the clone); the clone's own entry is gone, or
the record says it is not; the verdict is unchanged (green, exit 0).

A second night ends in an exception (no record): the stand-in git refuses ``git worktree remove`` and the branch's
head has no ``tests/`` folder. The failed removal is still on standard error.

Red reasons on the base (README): the record has no ``cleanup`` key and nothing goes to standard error; the locked
clone's entry is still there while no record says so; the repo-wide prune drops the stale registration.
"""

import pytest

import w2_77_support as support

STAGED = {"staged-in-tree.txt": "a change staged in the other worktree called tree\n"}


class LockedNight:
    """One night whose clone the suite locks, run once for the module's cases."""

    def __init__(self, base):
        self.project = support.Project(base, lock=True)
        self.other = self.project.add_worktree(base / "elsewhere" / "tree", staged=STAGED)
        self.stale = self.project.plant_stale(base / "stale")
        self.entries_before = support.admin_entries(self.project.root)
        self.run = self.project.nightly()


@pytest.fixture(scope="module")
def night(tmp_path_factory):
    return LockedNight(tmp_path_factory.mktemp("w2_77_failed_removal"))


def _cleanup(night):
    record, rel = support.record_of(night.project, night.run)
    cleanup = record.get(support.CLEANUP_KEY)
    assert isinstance(cleanup, dict), (
        f"the clone's removal failed (its worktree was locked) and the night's record {rel} does not say so: no "
        f"{support.CLEANUP_KEY!r} key (record keys: {sorted(record)}); a failed removal is never hidden")
    return cleanup


def test_the_fixture_the_other_worktree_holds_the_entry_name_tree_and_the_clone_another(night):
    support.green(night.run)
    clone, entry = night.project.clone()
    assert clone.name == "tree" and night.other.path.name == "tree", "the fixture's two folders are not both 'tree'"
    assert night.other.entry.name == "tree", f"the other worktree does not hold the entry name tree: {night.other.entry}"
    assert entry.name != "tree", f"the clone holds the entry name tree: the fixture does not test name-guessing"


def test_another_worktree_s_entry_is_never_touched_the_one_also_called_tree_keeps_its_registration_and_index(night):
    support.green(night.run)
    support.assert_kept(night.project, night.other, "the other worktree whose folder is also called tree")
    after = support.admin_entries(night.project.root)
    _, entry = night.project.clone()
    lost = sorted(name for name in night.entries_before if name not in after)
    assert not lost, f"the night removed other worktrees' administrative entries: {lost} (its clone's is {entry.name})"


def test_a_stale_registration_is_still_registered_after_a_failed_removal(night):
    support.green(night.run)
    assert support.is_registered(night.project.root, night.stale.path) and night.stale.entry.is_dir(), \
        (f"the stale registration of {night.stale.path} was dropped by the night (its entry {night.stale.entry}): "
         "a failed removal of the clone touches no other entry, and no prune runs")


def test_the_failed_removal_is_in_the_night_s_record_under_cleanup(night):
    support.green(night.run)
    cleanup = _cleanup(night)
    clone, entry = night.project.clone()
    missing = [field for field in support.CLEANUP_FIELDS if field not in cleanup]
    assert not missing, f"the record's cleanup lacks {missing}: {cleanup}"
    assert cleanup["ok"] is False, f"the record's cleanup does not say ok: false: {cleanup}"
    assert isinstance(cleanup["clone"], str) and support.same_path(cleanup["clone"], clone), \
        f"the record's cleanup does not name the clone {clone}: {cleanup}"
    assert cleanup["entry"] is None or support.same_path(cleanup["entry"], entry), \
        f"the record's cleanup names an entry that is not the clone's own ({entry}): {cleanup}"
    assert isinstance(cleanup["entry_removed"], bool), f"entry_removed is not true or false: {cleanup}"
    assert isinstance(cleanup["error"], str) and cleanup["error"].strip(), f"the cleanup gives no error: {cleanup}"


def test_the_clone_s_own_entry_is_gone_or_the_record_says_it_is_not(night):
    support.green(night.run)
    cleanup = _cleanup(night)
    clone, entry = night.project.clone()
    if cleanup.get("entry_removed") is True:
        assert not entry.exists(), f"the record says the clone's entry was removed, and {entry} is still there"
        assert not support.is_registered(night.project.root, clone), \
            f"the record says the clone's entry was removed, and the clone {clone} is still registered"
    else:
        assert entry.exists(), f"the record says the clone's entry was not removed, and {entry} is gone: {cleanup}"


def test_the_failed_removal_goes_to_standard_error_on_a_line_naming_the_clone(night):
    support.green(night.run)
    clone, _ = night.project.clone()
    lines = support.stderr_lines_naming(night.run, clone)
    assert lines, (f"no line of the night's standard error names the clone {clone} whose removal failed:\n"
                   f"{night.run.stderr[-3000:]}")


def test_a_failed_clean_up_does_not_change_the_verdict(night):
    result = support.green(night.run)
    record, _ = support.record_of(night.project, night.run)
    assert record.get("verdict") == support.GREEN and result.get("verdict") == support.GREEN, \
        f"a failed clean-up changed the night's verdict: {record.get('verdict')!r}"
    assert set(record) - {support.CLEANUP_KEY} == support.RECORD_KEYS, \
        f"a failed clean-up changed the record's other keys: {sorted(record)}"


def test_a_night_that_ends_in_an_exception_still_writes_the_failed_removal_to_standard_error(tmp_path):
    """No record is written (the branch's head has no ``tests/`` folder); the stand-in git refuses the removal."""
    project = support.Project(tmp_path, fail_remove=True)
    other = project.add_worktree(tmp_path / "elsewhere" / "tree", staged=STAGED)
    stale = project.plant_stale(tmp_path / "stale")
    run = project.nightly("bare")
    data = run.envelope()
    assert data.get("ok") is False and run.returncode != support.EXIT_OK, \
        f"the fixture: the night on a head without tests/ did not end in an error\n{run.describe()}"
    assert not project.records(), f"the fixture: the night wrote a record {project.records()}\n{run.describe()}"
    clone = project.added_clone()
    assert support.worktree_calls(project.git_calls(), "remove"), "the night did not try to remove its clone"
    assert support.stderr_lines_naming(run, clone), \
        (f"the night ended in an exception, its clone's removal failed, and no line of its standard error names "
         f"the clone {clone}:\n{run.stderr[-3000:]}")
    support.assert_kept(project, other, "the other worktree whose folder is also called tree")
    assert support.is_registered(project.root, stale.path), f"the stale registration of {stale.path} was dropped"
