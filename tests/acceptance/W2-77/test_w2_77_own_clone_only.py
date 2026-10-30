"""S1: after its run, ``gov.close.nightly`` removes only its own clone, by its exact path (``git worktree remove
--force <that path>``), and never runs a repo-wide ``git worktree prune`` [DEC-939 item 5, row W2-M406].

One green night on the tiny project, with the stand-in git logging every git call the night makes (its own and its
children's). A stale registration (a worktree added, its folder deleted) is planted before the night: a repo-wide
prune would drop it, so its survival shows, by behaviour, that none ran.

Red reason on the base (README): the night ends with ``git worktree prune`` (the log shows it), and that prune drops
the stale registration.
"""

import pytest

import w2_77_support as support


class Night:
    """One green night, run once for the module's cases."""

    def __init__(self, base):
        self.project = support.Project(base)
        self.stale = self.project.plant_stale(base / "stale")
        self.run = self.project.nightly()


@pytest.fixture(scope="module")
def night(tmp_path_factory):
    return Night(tmp_path_factory.mktemp("w2_77_own_clone"))


def test_the_night_runs_no_git_worktree_prune(night):
    support.green(night.run)
    prunes = support.worktree_calls(night.project.git_calls(), "prune")
    assert not prunes, (f"the night ran a repo-wide git worktree prune ({len(prunes)} calls: {prunes}); it removes "
                        "only its own clone, by its exact path (DEC-939 item 5, row W2-M406)")


def test_the_night_removes_its_clone_by_its_exact_path_with_git_worktree_remove_force(night):
    support.green(night.run)
    clone, _ = night.project.clone()
    assert support.same_path(night.project.added_clone(), clone), \
        f"the clone the suite ran in ({clone}) is not the worktree the night added ({night.project.added_clone()})"
    removals = support.worktree_calls(night.project.git_calls(), "remove")
    assert removals, "the night ran no git worktree remove: its clone is not removed by its path"
    others = [call for call in removals if not support.same_path(call[-1], clone)]
    assert not others, f"the night removed a worktree other than its clone ({clone}): {others}"
    forced = [call for call in removals if "--force" in call or "-f" in call]
    assert forced, f"the clone's removal is not git worktree remove --force <its path>: {removals}"


def test_the_clone_is_gone_afterwards_its_folder_its_registration_and_its_entry(night):
    support.green(night.run)
    clone, entry = night.project.clone()
    assert not clone.exists(), f"the clone's folder {clone} is still there after the night"
    assert not support.is_registered(night.project.root, clone), f"the clone {clone} is still registered"
    assert not entry.exists(), f"the clone's administrative entry {entry} is still there after the night"


def test_a_stale_registration_planted_before_the_night_is_still_registered_after_it(night):
    """No repo-wide prune, shown by behaviour: a registration whose folder is missing is not the night's to drop."""
    support.green(night.run)
    assert support.is_registered(night.project.root, night.stale.path), \
        (f"the stale registration of {night.stale.path} (its folder deleted before the night) was dropped by the "
         f"night: a repo-wide prune ran (registered now: {sorted(support.registered(night.project.root))})")
    assert night.stale.entry.is_dir(), f"the stale registration's administrative folder {night.stale.entry} is gone"
