"""W2-84 -- matched by real path: links and ``..`` are refused as their targets are.

KPI success 2: "Matched by real path: a symbolic link, from inside or outside
any tree, to a hidden file, to a hidden folder, or to a tree itself, is refused
as its target is; a tree reached by a link or by a path spelled with .. is
refused as the tree is [DEC-950 item 1, DEC-820]".
KPI failure 1: "... or through a link into one."

The links (``w2_84_support.make_world``):

- ``peek``, in each session's own root: a link to W2-82's hidden folder (a link
  inside the session's own tree to another tree's hidden folder);
- ``home/outside/answers-link``: a link outside every tree to W2-82's hidden
  file;
- ``home/outside/tree-link``: a link to the worktree W2-82 itself;
- ``home/outside/clone-link``: a link to the run clone itself (a path under the
  runs root by its real path).

W2-82 is the target because no session runs in it: it is another tree for all
three. The paths spelled with ``..`` lead from the session's root to W2-82.
"""

from __future__ import annotations

import os

import pytest

import w2_84_support as s

LINK_IDS = ("inside-link-Read", "inside-link-cat", "inside-link-grep-r", "inside-link-Grep",
            "outside-file-link-Read", "outside-file-link-cat",
            "tree-link-Read", "tree-link-grep-r", "tree-link-Grep",
            "clone-link-Read", "clone-link-grep-r",
            "dot-dot-Read", "dot-dot-cat", "dot-dot-tree-grep-r", "dot-dot-tree-Glob")


def _routes(world, root):
    outside = world.sandbox.outside
    other = world.tree(s.WT_OTHER)
    up_file = os.path.relpath(other / s.HIDDEN_FILE, root)
    up_tree = os.path.relpath(other, root)
    assert up_file.startswith(".."), up_file
    return [
        s.read(root / "peek" / "answers.yaml"),
        s.bash("cat peek/answers.yaml"),
        s.bash(f"grep -rn {s.HIDDEN_WORD} peek/"),
        s.grep(root / "peek", pattern="q1"),
        s.read(outside / "answers-link"),
        s.bash(f"cat {s.q(outside / 'answers-link')}"),
        s.read(outside / "tree-link" / s.HIDDEN_FILE),
        s.bash(f"grep -rn {s.HIDDEN_WORD} {s.q(outside / 'tree-link')}/"),
        s.grep(outside / "tree-link", pattern="q1"),
        s.read(outside / "clone-link" / s.HIDDEN_FILE),
        s.bash(f"grep -rn {s.HIDDEN_WORD} {s.q(outside / 'clone-link')}/"),
        s.read(f"{root}/{up_file}"),
        s.bash(f"cat {s.q(up_file)}"),
        s.bash(f"grep -rn {s.HIDDEN_WORD} {s.q(up_tree)}"),
        s.glob_call(f"{s.HIDDEN_FOLDER}/*", f"{root}/{up_tree}"),
    ]


def test_the_links_lead_where_the_cases_say(world):
    """The fixture's own check: each link's real path is the hidden part or the tree it names."""
    other = world.tree(s.WT_OTHER)
    outside = world.sandbox.outside
    for name in s.SESSION_ROOTS:
        assert os.path.realpath(world.tree(name) / "peek") == os.path.realpath(other / s.HIDDEN_FOLDER)
    assert os.path.realpath(outside / "answers-link") == os.path.realpath(other / s.HIDDEN_FILE)
    assert os.path.realpath(outside / "tree-link") == os.path.realpath(other)
    assert os.path.realpath(outside / "clone-link") == os.path.realpath(world.tree(s.CLONE))
    assert os.path.realpath(world.tree(s.CLONE)).startswith(os.path.realpath(world.sandbox.runs) + "/")


@pytest.mark.parametrize("index", range(len(LINK_IDS)), ids=LINK_IDS)
@pytest.mark.parametrize("session", s.SESSION_ROOTS)
def test_a_link_or_a_dot_dot_path_is_refused_as_its_target_is(world, session, index):
    root = world.tree(session)
    call = _routes(world, root)[index]
    result = world.ask(call, s.ENGINEER, s.ENG, root)
    s.assert_refused(result, call, f"engineer rooted in the {session}: ")
