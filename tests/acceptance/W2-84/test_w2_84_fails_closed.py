"""W2-84 -- fail closed: nothing is taken as holding no hidden part because it could not be read.

KPI success 4: "Fail closed: when the trees cannot be listed (git worktree list
fails or times out, or the runs root cannot be read), the measured session's
calls are refused with the cause, as a malformed set refuses them today; a
search or listing from a folder above a hidden part that cannot be walked, or
that holds more than the guard reads in bounded time, is refused; nothing is
taken as holding no hidden part because it could not be read [DEC-950 item 1,
DEC-820, DEC-562]".
KPI failure 2: "A tree or a folder that cannot be listed or walked treated as
holding no hidden part."

"With the cause": refused as today's ``PolicyError`` refusals are rendered
(``<cause>: the call is refused (fail closed, DEC-820)``), which the design
note keeps for its new causes (item 7). The cases check the words ``fail
closed``, not the cause's wording.

Each case builds a world of its own (``fresh_world``) and changes it. A folder
made unreadable (mode 000) gets its mode back at teardown (``modes``).

- **git cannot list the worktrees**: a stand-in ``git`` first on ``PATH`` fails
  the ``worktree`` command and passes every other call to the real git by its
  absolute path; or it sleeps 12 seconds on ``worktree`` (past the guard's
  5-second git timeout) and then answers as the real git, so that only a guard
  that times out refuses. The calls are ones whose answer depends on the trees:
  another tree's hidden file, and a search from the worktrees' parent.
- **the runs root cannot be read** (mode 000): every call is refused (the design
  note's item 2), shown with calls that are allowed when it can be read.
- **a hidden folder below a search's start cannot be walked** (mode 000), in the
  session's own tree and in another, with no other hidden file below the start.
- **a hidden part larger than the bound** (10,001 files, one past today's bound
  of 10,000 files of a part, DEC-562) in another tree, below a search's start.
- **a session in a run clone whose own folder's marker is missing, a link, or
  names no git directory**: the repository's trees cannot be found from the
  clone (the design note's item 3), so every call is refused.
"""

from __future__ import annotations

import os
import subprocess
import time

import pytest

import w2_84_support as s


def _tree_calls(world):
    """Calls whose answer depends on the trees: another tree's hidden file, and a search from above the worktrees."""
    other = world.tree(s.WT_OTHER)
    return [
        s.read(other / s.HIDDEN_FILE),
        s.bash(f"cat {s.q(other / s.HIDDEN_EXTRA)}"),
        s.bash(f"grep -rn {s.HIDDEN_WORD} {s.q(world.sandbox.worktrees_parent)}"),
    ]


def _git_answers(world, stand_in, *args):
    env = s.base_environment(world.sandbox, path_first=stand_in.folder)
    return subprocess.run(["git", "-C", str(world.tree(s.MAIN)), *args], capture_output=True, text=True, env=env,
                          timeout=s.COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)


def test_git_that_cannot_list_the_worktrees_refuses_with_the_cause(fresh_world):
    world = fresh_world
    stand_in = s.install_git_stand_in(world.sandbox, "fail", "failing-git")
    listed = _git_answers(world, stand_in, "worktree", "list", "--porcelain")
    assert listed.returncode != 0, "the stand-in git listed the worktrees"
    assert _git_answers(world, stand_in, "rev-parse", "HEAD").returncode == 0, "the stand-in git fails other calls"
    for call in _tree_calls(world):
        result = world.ask(call, s.ENGINEER, s.ENG, world.tree(s.MAIN), path_first=stand_in.folder)
        s.assert_refused_closed(result, call, "engineer rooted in the main tree, git worktree list failing: ")


def test_git_that_times_out_listing_the_worktrees_refuses_with_the_cause(fresh_world):
    """The one slow case: the guard's git timeout is 5 seconds; the stand-in answers after 12."""
    world = fresh_world
    stand_in = s.install_git_stand_in(world.sandbox, "sleep", "slow-git")
    call = s.read(world.tree(s.WT_OTHER) / s.HIDDEN_FILE)
    started = time.monotonic()
    result = world.ask(call, s.ENGINEER, s.ENG, world.tree(s.MAIN), path_first=stand_in.folder)
    took = time.monotonic() - started
    s.assert_refused_closed(result, call, f"engineer rooted in the main tree, git worktree list slow ({took:.1f} s): ")


def test_an_unreadable_runs_root_refuses_every_call_with_the_cause(fresh_world, modes):
    world = fresh_world
    root = world.tree(s.MAIN)
    calls = [
        s.read(root / "README.md"),
        s.bash("cat docs/notes.md"),
        s.read(world.tree(s.WT_OTHER) / s.VISIBLE_FILE),
    ]
    for call in calls:  # allowed while the runs root can be read
        s.assert_allowed(world.ask(call, s.ENGINEER, s.ENG, root), call, "the runs root readable: ")
    modes.lock(world.sandbox.runs)
    assert s.unreadable(world.sandbox.runs), "mode 000 does not keep this user from listing the runs root"
    for call in calls:
        result = world.ask(call, s.ENGINEER, s.ENG, root)
        s.assert_refused_closed(result, call, "engineer rooted in the main tree, the runs root unreadable: ")


@pytest.mark.parametrize("where", (s.MAIN, s.WT_OTHER), ids=("own-tree", "another-tree"))
def test_a_hidden_folder_that_cannot_be_walked_below_a_search_s_start_refuses(fresh_world, modes, where):
    """Below the start ``<tree>/eval/memory`` the only hidden files lie in the unreadable folder; the one-folder
    glob's file is removed from that tree first, so that nothing else there is hidden."""
    world = fresh_world
    tree = world.tree(where)
    os.remove(tree / s.HIDDEN_EXTRA)
    modes.lock(tree / s.HIDDEN_FOLDER)
    assert s.unreadable(tree / s.HIDDEN_FOLDER), "mode 000 does not keep this user from listing the folder"
    start = tree / "eval" / "memory"
    for call in (s.bash(f"grep -rn {s.HIDDEN_WORD} {s.q(start)}"), s.grep(start, pattern="q1")):
        result = world.ask(call, s.ENGINEER, s.ENG, world.tree(s.MAIN))
        s.assert_refused(result, call, f"engineer rooted in the main tree, {where}'s hidden folder unreadable: ")


# Today's bound on a protected part's files (DEC-562), which the design note keeps per tree (item 4): one more.
MANY = 10001


def test_a_search_above_a_hidden_part_larger_than_the_bound_is_refused_in_bounded_time(fresh_world):
    """The other tree W2-82 holds more hidden files than the guard reads in bounded time; a search from above it
    is refused by the guard, not by the hook's own deadline (DEC-580)."""
    world = fresh_world
    many = world.tree(s.WT_OTHER) / s.HIDDEN_FOLDER / "many"
    many.mkdir()
    for n in range(MANY):
        (many / f"q{n:05d}.yaml").write_text("q\n", encoding="utf-8")
    call = s.bash(f"grep -rn {s.HIDDEN_WORD} {s.q(world.tree(s.WT_OTHER))}")
    result = world.ask(call, s.ENGINEER, s.ENG, world.tree(s.MAIN))
    s.assert_refused(result, call, "engineer rooted in the main tree, W2-82's hidden part over the bound: ")
    assert "deadline" not in result.reason, f"the hook's deadline answered, not the guard: {result.describe()}"


MARKER_FAULTS = ("missing", "a-link", "names-no-git-directory")


@pytest.mark.parametrize("fault", MARKER_FAULTS)
def test_a_session_in_a_run_clone_whose_marker_is_faulty_is_refused_every_call(fresh_world, fault):
    world = fresh_world
    clone = world.tree(s.CLONE)
    marker = clone.parent / s.OWN_MARKER
    content = marker.read_text(encoding="utf-8")
    marker.unlink()
    if fault == "a-link":
        target = s.write(world.sandbox.elsewhere / "marker-elsewhere", content)
        os.symlink(target, marker)
    elif fault == "names-no-git-directory":
        marker.write_text(str(world.sandbox.elsewhere) + "\n", encoding="utf-8")
    calls = [s.read(world.tree(s.MAIN) / s.HIDDEN_FILE), s.read(clone / "README.md")]
    for call in calls:
        result = world.ask(call, s.ENGINEER, s.ENG, clone)
        s.assert_refused_closed(result, call, f"engineer rooted in the run clone, its marker {fault}: ")


def test_a_session_in_a_clone_made_by_hand_with_no_marker_is_refused_every_call(fresh_world):
    world = fresh_world
    deep = world.tree(s.DEEP)
    assert not any((deep.parents[i] / s.OWN_MARKER).exists() for i in range(4)), "the deep clone has a marker"
    for call in (s.read(world.tree(s.WT_OTHER) / s.HIDDEN_FILE), s.read(deep / "README.md")):
        result = world.ask(call, s.ENGINEER, s.ENG, deep)
        s.assert_refused_closed(result, call, "engineer rooted in a clone made by hand: ")
