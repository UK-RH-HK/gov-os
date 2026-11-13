"""S1's other half and failure lines 1-3: every other kind's wall is unchanged, no test opens the real sets root, and the
ticket's branch touches only its own paths.

- A writer's (round 2) and a checker's wall, built from the same planted set (its ``dropped/`` subtree included) with the
  same arguments and seed, equal byte for byte the wall the script at the base (``03393ee51``) builds in the same
  planted world. The two builds are made one after the other in one world, so every path is the same except the run id;
  the run id is the only field replaced (inside file contents, by ``<RUN>``): it is the one field that differs between
  two runs of one script with one seed. The sanity cases below run the BASE script twice and show that, after that one
  replacement, the two walls are equal in every entry and byte (a time, a temporary path or any other field that
  differed would show there). Modes are compared as well.
- Before this change a checker's wall carries ``input/set/dropped/...``; each case asserts it does in the base's wall
  and still does in the head's.
- F2: the files of ``tests/acceptance/W2-178/`` hold no line naming the real sets root (the case builds the name from two
  halves so that this file does not match itself).
- F3: ``git diff --name-only <base>...HEAD`` lists only paths the ticket's ``allowed_paths`` match, plus
  ``tests/acceptance/W2-178/**`` and the ticket's own process records (W1-01's reading, as in W2-173's F4 case: its
  ticket file ``.tickets/DAEO-7oxm.md``, ``docs/checkpoints/DAEO-7oxm/**``, ``docs/probes/DAEO-7oxm/**``). The base is
  the merge-base of HEAD with ``w2/integrate`` (``03393ee51``, the ticket's claim commit, when none is found).
"""

from __future__ import annotations

import fnmatch
import os

import pytest
import yaml

import w2_178_support as s
from w2_178_support import support

OWN_RECORDS = (f".tickets/{s.TICKET_ID}.md", f"docs/checkpoints/{s.TICKET_ID}/*", f"docs/probes/{s.TICKET_ID}/*")
KINDS = (pytest.param("writer", 2, id="writer-round-2"), pytest.param("checker", None, id="checker"))


# -- S1 / F1: the writer's and the checker's walls are what they were -------------------------------------------------

@pytest.mark.parametrize("kind,round_", KINDS)
def test_s1_the_wall_equals_the_base_build_byte_for_byte_with_the_dropped_files_in_it(world, base_script, kind, round_):
    """Green today (the head is the base): the wall holds ``input/set/dropped/...`` (all three files and the two
    folders on the way) in the base's build and in the head's, and the two walls are equal in every entry."""
    s.plant(world, s.DROPPED, s.LOOKALIKES, s.NESTED, s.RAW, xcheck=True)
    base_line = s.build(world, base_script, kind, round_)
    head_line = s.build(world, None, kind, round_)
    base_snap, head_snap = s.snapshot(world, base_line), s.snapshot(world, head_line)
    for name, snap in (("base", base_snap), ("head", head_snap)):
        for rel, data in s.DROPPED.items():
            assert snap.get("input/set/" + rel, (None, None))[1] == data, f"the {name}'s {kind} wall lacks input/set/{rel}"
    diff = s.differences(base_snap, head_snap)
    assert diff == {}, f"the head's {kind} wall differs from the base's: {diff}"


@pytest.mark.parametrize("kind,round_", KINDS)
def test_s1_the_wall_of_a_set_without_a_dropped_folder_equals_the_base_build(world, base_script, kind, round_):
    """Green today: W2-149's planted set as it is (no ``dropped/``) gives the same wall as the base's, entry for entry."""
    s.plant(world, xcheck=True)
    base_line = s.build(world, base_script, kind, round_)
    head_line = s.build(world, None, kind, round_)
    diff = s.differences(s.snapshot(world, base_line), s.snapshot(world, head_line))
    assert diff == {}, f"the head's {kind} wall differs from the base's: {diff}"


@pytest.mark.parametrize("kind,round_", KINDS)
def test_f1_the_dropped_files_stay_in_the_source_set_after_the_build(world, kind, round_):
    """Green today: building a writer's or a checker's wall moves or changes no file of the set on disk."""
    s.plant(world, s.DROPPED, s.LOOKALIKES, xcheck=True)
    before = s.sets_snapshot(world)
    s.build(world, None, kind, round_)
    assert s.sets_snapshot(world) == before


@pytest.mark.parametrize("kind,round_", (KINDS[0], KINDS[1], pytest.param("auditor", None, id="auditor")))
def test_s1_sanity_the_base_script_twice_gives_equal_walls_but_for_the_run_id(world, base_script, kind, round_):
    """Green: one script (the base's), one seed, one world, built twice. The run ids differ; after replacing the run id
    in file contents every entry and byte is equal. That shows the comparison's one replacement is enough."""
    s.plant(world, s.DROPPED, xcheck=True)
    one = s.build(world, base_script, kind, round_)
    two = s.build(world, base_script, kind, round_)
    assert one["run"] != two["run"], "both builds got one run id"
    diff = s.differences(s.snapshot(world, one), s.snapshot(world, two))
    assert diff == {}, f"two builds by the base script differ beyond the run id: {diff}"


# -- F2: no test opens the real sets root -----------------------------------------------------------------------------

def test_f2_no_line_of_this_folder_names_the_owner_s_sets_root():
    """Green: the real sets root's name (``gov-os-`` + ``eval``, bare, as ``~/...`` or as ``/home/<user>/...``) is in no
    file of ``tests/acceptance/W2-178/`` (this file builds the needle in two halves). A planted sets root is the only
    one these tests use; every launch in them passes W2-149's ``World.check_planted``."""
    needle = "gov-os-" + "".join(["ev", "al"])      # built at run time: not even a compiled file holds the name whole
    home = os.path.realpath(support.real_home())
    needles = (needle, "~/" + needle, "/home/usain/" + needle, home + "/" + needle)
    folder = support.TREE / "tests" / "acceptance" / s.W2
    hits = []
    for dp, _dn, fn in os.walk(folder):
        if "__pycache__" in dp:
            continue
        for n in fn:
            p = os.path.join(dp, n)
            with open(p, "rb") as f:
                text = f.read().decode("utf-8", "replace")
            for i, line in enumerate(text.splitlines(), 1):
                if any(x in line for x in needles):
                    hits.append(f"{os.path.relpath(p, support.TREE)}:{i}")
    assert hits == [], f"lines naming the real sets root: {hits}"


# -- F3: the branch's names -------------------------------------------------------------------------------------------

def branch_names():
    tree = support.TREE
    try:
        base = support.git(tree, "merge-base", "HEAD", "w2/integrate").strip()
    except RuntimeError:
        base = support.git(tree, "rev-parse", "--verify", s.BASE_FALLBACK + "^{commit}").strip()
    names = [x for x in support.git(tree, "diff", "--name-only", "--no-renames", f"{base}...HEAD").splitlines()
             if x.strip()]
    return base, names


def ticket_allowed_paths():
    text = (support.TREE / ".tickets" / f"{s.TICKET_ID}.md").read_text()
    front = yaml.safe_load(text.split("\n---", 1)[0].lstrip("-\n"))
    paths = front.get("allowed_paths")
    assert isinstance(paths, list) and paths, "the ticket names no allowed_paths"
    return paths


def matched(path, globs):
    return any(fnmatch.fnmatch(path, g) for g in globs)


def test_f3_the_branch_changes_only_the_ticket_s_paths():
    """Green on this branch (it changes only ``tests/acceptance/W2-178/``); judged on the engineer's branch."""
    base, names = branch_names()
    allowed = ticket_allowed_paths() + [f"tests/acceptance/{s.W2}/**"] + list(OWN_RECORDS)
    outside = [n for n in names if not matched(n, allowed)]
    assert outside == [], f"the branch (against {base[:12]}) changes paths outside the ticket's: {outside}"
