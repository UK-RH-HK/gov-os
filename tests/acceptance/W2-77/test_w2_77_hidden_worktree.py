"""S2: a second worktree of the project whose folder is hidden or unreadable while the nightly runs keeps its
registration and its staged index afterwards; the fixture that reproduced W2-68's reviewer's F1 now keeps them
[DEC-939 item 5, P-W2-68-PRUNE].

W2-68's F1 (``docs/probes/DAEO-2gc7/PR-DAEO-2gc7.md``): a second worktree of the project's repository, holding a
staged change, has its folder out of the night's view for the whole run, then put back. Two ways to hide it: moved
aside (standing for an unmounted or moved folder) and made unreadable (permission denied), each restored in a
``finally``. Afterwards: its registration (``git worktree list --porcelain`` of the main repository), its
administrative folder and its staged index (the staged change, seen from inside it) are kept.

Red reason on the base (README): the night's repo-wide ``git worktree prune`` drops the hidden worktree's
registration and administrative folder, and with them its index; git answers "not a git repository" inside it.
"""

import pytest

import w2_77_support as support

STAGED = {"staged-change.txt": "a change staged in the second worktree, not committed\n"}


@pytest.mark.parametrize("hide", sorted(support.HIDDEN))
def test_a_worktree_hidden_while_the_night_runs_keeps_its_registration_its_admin_folder_and_its_staged_index(
        tmp_path, hide):
    project = support.Project(tmp_path)
    second = project.add_worktree(tmp_path / "second", staged=STAGED)
    support.assert_kept(project, second, "before the night (the fixture)")
    with support.HIDDEN[hide](second.path):
        run = project.nightly()
    support.green(run)
    support.assert_kept(project, second, f"the second worktree, {hide.replace('_', ' ')} while the night ran")
