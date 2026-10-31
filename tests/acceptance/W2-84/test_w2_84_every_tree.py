"""W2-84 -- a measured session is refused the hidden part under every tree, wherever it runs, by every route.

KPI success 1: "A session that an evaluation set measures (by its role or by
its ticket) is refused the set's hidden part under every tree of the
repository: the main tree, every worktree that git worktree list names, and
every run clone under ~/gov-os-runs/; wherever the session itself runs (the
main tree or a worktree); by every read tool and every Bash route the guard
judges today in the session's own tree (Read, Grep, Glob, a reading command, a
search or listing from a folder above, git -C <tree>)".
KPI failure 1: "A measured session reads, lists or searches a hidden file of any
tree: the main tree, a worktree, a run clone, or through a link into one."

The world (``w2_84_support.make_world``): the planted repository's main tree
``home/repo``, its worktrees ``home/gov-os-worktrees/W2-81`` and ``W2-82``, a
run clone ``home/gov-os-runs/W2-83/clone`` in an own folder whose marker names
the repository, and a clone made by hand at
``home/gov-os-runs/W2-00/a/b/repo`` (deeper, no marker). Each holds the hidden
part ``eval/memory/hidden/**`` and ``eval/memory/answers-*.yaml``. The set
measures the role ``engineer`` and the ticket ``DAEO-zz86``.

The sessions: a measured engineer rooted in the main tree, in the worktree
W2-81, and in the run clone (the design note's item 3); a research session
measured by its ticket, rooted in W2-81.
"""

from __future__ import annotations

import os

import pytest

import w2_84_support as s

ROUTE_IDS = ("Read-hidden", "Read-one-folder-glob", "Grep-hidden-folder", "Glob-hidden", "cat", "ls-hidden-folder",
             "git-C-show-HEAD-path", "git-C-show-HEAD-dot-path", "git-C-grep")


def _routes(tree):
    """Every route the guard judges today in the session's own tree, aimed at ``tree``'s hidden part.

    ``git -C <tree> show HEAD:<path>`` names the path from the top of the
    tree; ``HEAD:./<path>`` names it from the folder ``-C`` moves to, which the
    guard judges today relative to that folder (the design note's item 5).
    """
    return [
        s.read(tree / s.HIDDEN_FILE),
        s.read(tree / s.HIDDEN_EXTRA),
        s.grep(tree / s.HIDDEN_FOLDER, pattern="q1"),
        s.glob_call(f"{s.HIDDEN_FOLDER}/*", tree),
        s.bash(f"cat {s.q(tree / s.HIDDEN_FILE)}"),
        s.bash(f"ls {s.q(tree / s.HIDDEN_FOLDER)}"),
        s.bash(f"git -C {s.q(tree)} show HEAD:{s.HIDDEN_FILE}"),
        s.bash(f"git -C {s.q(tree)} show HEAD:./{s.HIDDEN_FILE}"),
        s.bash(f"git -C {s.q(tree)} grep -n {s.HIDDEN_WORD}"),
    ]


@pytest.mark.parametrize("index", range(len(ROUTE_IDS)), ids=ROUTE_IDS)
@pytest.mark.parametrize("target", s.TREE_NAMES)
@pytest.mark.parametrize("session", s.SESSION_ROOTS)
def test_a_measured_engineer_is_refused_every_tree_s_hidden_part(world, session, target, index):
    call = _routes(world.tree(target))[index]
    result = world.ask(call, s.ENGINEER, s.ENG, world.tree(session))
    s.assert_refused(result, call, f"engineer rooted in the {session}, the {target}'s hidden part: ")


# --------------------------------------------------------------------------
# From a folder above: the worktrees' parent, the runs root, the temporary home
# --------------------------------------------------------------------------

START_IDS = ("worktrees-parent", "runs-root", "home")


def _start(world, name):
    return {"worktrees-parent": world.sandbox.worktrees_parent, "runs-root": world.sandbox.runs,
            "home": world.sandbox.home}[name]


def _below(world, name):
    """A hidden file below each start, of a tree no session runs in: W2-82, the clone made by hand, W2-82."""
    return {"worktrees-parent": world.tree(s.WT_OTHER), "runs-root": world.tree(s.DEEP),
            "home": world.tree(s.WT_OTHER)}[name] / s.HIDDEN_FILE


ABOVE_IDS = ("grep-r", "rg", "find-exec-cat", "find-xargs-cat", "cd-then-cat")


def _above(world, name):
    start = _start(world, name)
    rel = os.path.relpath(_below(world, name), start)
    return [
        s.bash(f"grep -rn {s.HIDDEN_WORD} {s.q(start)}"),
        s.bash(f"rg -n {s.HIDDEN_WORD} {s.q(start)}"),
        s.bash(f"find {s.q(start)} -type f -exec cat {{}} +"),
        s.bash(f"find {s.q(start)} -type f | xargs cat"),
        s.bash(f"cd {s.q(start)} && cat {s.q(rel)}"),
    ]


@pytest.mark.parametrize("index", range(len(ABOVE_IDS)), ids=ABOVE_IDS)
@pytest.mark.parametrize("start", START_IDS)
@pytest.mark.parametrize("session", (*s.SESSION_ROOTS, s.CLEAN))
def test_a_search_or_read_from_a_folder_above_the_trees_is_refused(world, session, start, index):
    """Also rooted in the clean worktree W2-85, which holds neither a hidden file nor the engineer's tests: from
    each start, what is refused is the other trees' hidden part alone."""
    call = _above(world, start)[index]
    result = world.ask(call, s.ENGINEER, s.ENG, world.tree(session))
    s.assert_refused(result, call, f"engineer rooted in the {session}, from the {start}: ")


# --------------------------------------------------------------------------
# A listing fed at run time, whose start the guard cannot place
# --------------------------------------------------------------------------

def test_a_listing_fed_at_run_time_is_refused_while_another_tree_holds_the_hidden_part(world):
    """Today such a listing (xargs reading its names from a file, a ``while read`` loop fed by a redirect) is
    refused only while the session's own tree holds a file of a part. Here the session runs in the clean worktree
    W2-85, which holds none, while the other trees and the clones hold the hidden part (the design note's item 4).
    The guard judges the command's text: ``names.txt`` need not exist."""
    root = world.tree(s.CLEAN)
    for call in (s.bash("xargs -a names.txt cat"), s.bash('while read -r f; do cat "$f"; done < names.txt')):
        result = world.ask(call, s.ENGINEER, s.ENG, root)
        s.assert_refused(result, call, "engineer rooted in the clean worktree W2-85: ")


# --------------------------------------------------------------------------
# A session measured by its ticket, not by its role
# --------------------------------------------------------------------------

@pytest.mark.parametrize("target", (s.MAIN, s.WT_OTHER, s.CLONE, s.DEEP))
def test_a_session_measured_by_its_ticket_is_refused_every_other_tree_s_hidden_part(world, target):
    tree = world.tree(target)
    root = world.tree(s.WT_OWN)
    for call in (s.read(tree / s.HIDDEN_FILE), s.bash(f"cat {s.q(tree / s.HIDDEN_EXTRA)}")):
        result = world.ask(call, s.RESEARCH, s.MEASURED_TK, root)
        s.assert_refused(result, call, f"research on {s.MEASURED_TK.tk} rooted in W2-81, the {target}: ")


def test_a_session_measured_by_its_ticket_is_refused_a_search_of_the_runs_root(world):
    call = s.bash(f"grep -rn {s.HIDDEN_WORD} {s.q(world.sandbox.runs)}")
    result = world.ask(call, s.RESEARCH, s.MEASURED_TK, world.tree(s.WT_OWN))
    s.assert_refused(result, call, f"research on {s.MEASURED_TK.tk} rooted in W2-81: ")
