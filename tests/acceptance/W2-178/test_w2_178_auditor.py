"""S1 and failure line 1, the new part: the auditor's copy of a set leaves out everything under ``hidden/dropped/``.

Every case plants its own sets root under pytest's temporary folder (W2-149's world) and a set whose hidden folder holds
a ``dropped/`` subtree (three files, at one, two and three folders down) beside the files W2-149 plants (``q01.yaml``,
``q02.yaml``, ``sub/q03.yaml``). The wall is built by ``--kind auditor --set <set> --audit audit-1`` with a fixed seed
and ``--dry`` (the wall is left in place), and read through the file system only.

Readings (the lead's; none is a KPI line of its own):
- "under ``hidden/dropped/``" is the folder directly below ``hidden/`` named ``dropped``, its whole subtree. A file named
  ``dropped.yaml``, a folder ``dropped-items/`` or ``droppedq/`` beside it, and a folder named ``dropped`` further down
  (``hidden/sub/dropped/``) are not it and stay (the last is the lead's reading of "its ``hidden/dropped/`` folder").
- A set whose every file is under ``dropped/`` refuses as an empty set does today: not tested.
- Set-up A's overlap auditor (``--set tuning|held-out``) is a different path: not tested.
"""

from __future__ import annotations

import w2_178_support as s


def auditor_wall(world, *groups, script=None):
    s.plant(world, *groups)
    line = s.build(world, script, "auditor")
    return line, s.snapshot(world, line)


# -- S1 / F1: nothing under dropped/ reaches the auditor ---------------------------------------------------------------

def test_s1_the_auditor_s_wall_holds_nothing_under_dropped(world):
    """Red today: the wall's ``input/set/`` carries ``dropped/q07.yaml``, ``dropped/x/q08.yaml`` and
    ``dropped/x/y/q11.yaml``. No path (file or folder) under ``input/set/dropped`` may exist, and no file anywhere in the
    wall may hold a dropped question's bytes."""
    _line, snap = auditor_wall(world, s.DROPPED)
    leaked = sorted(k for k in snap if k == "input/set/dropped" or k.startswith("input/set/dropped/"))
    assert leaked == [], f"the auditor's wall holds dropped paths: {leaked}"
    holds = [k for k, v in snap.items() if v[0] != "dir" and any(d in v[1] for d in s.DROPPED.values())]
    assert holds == [], f"a dropped question's text is in: {holds}"


def test_s1_the_auditor_s_wall_holds_every_other_file_byte_identical(world):
    """Green today (an implementation that drops too much turns it red): each file of the set not under ``dropped/``
    (``q01.yaml``, ``q02.yaml``, ``sub/q03.yaml``) is in ``input/set/`` at the same relative path, byte for byte."""
    _line, snap = auditor_wall(world, s.DROPPED)
    got = s.input_set(snap)
    kept = {rel: data for rel, data in s.source_files(world).items() if not s.under_dropped(rel)}
    assert set(kept) == {"q01.yaml", "q02.yaml", "sub/q03.yaml"}, sorted(kept)
    for rel, data in kept.items():
        assert rel in got, f"input/set/{rel} is missing from the auditor's wall"
        assert got[rel][1] == data, f"input/set/{rel} differs from its source"


def test_s1_the_auditor_s_set_is_exactly_the_files_outside_dropped(world):
    """Red today (the dropped files are extra): the files of ``input/set/`` are the set's files outside ``dropped/``
    and nothing else."""
    _line, snap = auditor_wall(world, s.DROPPED)
    files = {rel for rel, v in s.input_set(snap).items() if v[0] != "dir"}
    want = {rel for rel in s.source_files(world) if not s.under_dropped(rel)}
    assert files == want, f"extra {sorted(files - want)}, missing {sorted(want - files)}"


def test_s1_names_that_only_look_like_dropped_stay_in_the_auditor_s_wall(world):
    """Green today: ``dropped.yaml``, ``dropped-items/q10.yaml`` and ``droppedq/q13.yaml`` are not under
    ``hidden/dropped/``; a prefix match would take them out. A non-text file also arrives byte for byte."""
    _line, snap = auditor_wall(world, s.DROPPED, s.LOOKALIKES, s.RAW)
    got = s.input_set(snap)
    for rel, data in {**s.LOOKALIKES, **s.RAW}.items():
        assert rel in got, f"input/set/{rel} was left out of the auditor's wall"
        assert got[rel][1] == data, f"input/set/{rel} differs from its source"


def test_s1_a_folder_named_dropped_below_another_folder_stays(world):
    """Green today. The lead's reading (named in ``unresolved``): only ``hidden/dropped/`` is left out; the file
    ``hidden/sub/dropped/q09.yaml`` is another folder's and stays, byte for byte."""
    _line, snap = auditor_wall(world, s.DROPPED, s.NESTED)
    got = s.input_set(snap)
    rel = "sub/dropped/q09.yaml"
    assert rel in got, "hidden/sub/dropped/q09.yaml was left out of the auditor's wall"
    assert got[rel][1] == s.NESTED[rel]


def test_s1_the_auditor_s_other_inputs_are_still_staged(world):
    """Green today: besides the set, the auditor's wall still holds ``input/misses.jsonl`` (the planted audit's, byte for
    byte) and ``input/selection.json``, and the set's files are read-only copies."""
    _line, snap = auditor_wall(world, s.DROPPED)
    misses = (world.sr / "runs/audit-1/misses.jsonl").read_bytes()
    assert snap["input/misses.jsonl"][1] == misses
    assert "input/selection.json" in snap
    for rel in ("q01.yaml", "q02.yaml", "sub/q03.yaml"):
        mode = snap["input/set/" + rel][0]
        assert mode & 0o222 == 0, f"input/set/{rel} is writable (mode {oct(mode)})"


def test_s1_the_auditor_s_wall_differs_from_the_base_build_only_by_the_dropped_subtree(world, base_script):
    """Red today: the same world, the same arguments and seed, built by the script at the base and by the head's. The
    head's wall equals the base's with every entry under ``input/set/dropped`` taken out: nothing else changes (the
    run id inside files is the one field replaced, see ``w2_178_support.snapshot``)."""
    s.plant(world, s.DROPPED)
    base_line = s.build(world, base_script, "auditor")
    head_line = s.build(world, None, "auditor")
    base_snap, head_snap = s.snapshot(world, base_line), s.snapshot(world, head_line)
    assert any(k.startswith("input/set/dropped/") for k in base_snap), "the base build carries no dropped files"
    diff = s.differences(s.without_dropped(base_snap), head_snap)
    assert diff == {}, f"the head's auditor wall differs from the base's beyond the dropped subtree: {diff}"


def test_s1_a_set_with_no_dropped_folder_builds_the_same_auditor_wall_as_before(world, base_script):
    """Green today: a set with no ``dropped/`` folder gives the auditor a wall equal to the base build's, entry for
    entry (a script that changed anything else for the auditor would differ)."""
    base_line = s.build(world, base_script, "auditor")
    head_line = s.build(world, None, "auditor")
    diff = s.differences(s.snapshot(world, base_line), s.snapshot(world, head_line))
    assert diff == {}, f"the head's auditor wall differs from the base's: {diff}"
    assert {"q01.yaml", "q02.yaml", "sub/q03.yaml"} <= set(s.input_set(s.snapshot(world, head_line)))


def test_s1_building_the_auditor_s_wall_leaves_the_set_on_disk_as_it_was(world):
    """Green today: the source set (the dropped files included) is read, never moved or changed; the sets root's
    ``fixtures`` tree is byte for byte what it was before the build."""
    s.plant(world, s.DROPPED, s.LOOKALIKES)
    before = s.sets_snapshot(world)
    s.build(world, None, "auditor")
    assert s.sets_snapshot(world) == before
    assert all((s.hidden_dir(world) / rel).is_file() for rel in s.DROPPED), "a dropped file left the set"


# -- S1: through a real (stubbed) run, not only a dry build ----------------------------------------------------------

def test_s1_a_delivered_auditor_run_packs_a_wall_without_the_dropped_files(world):
    """Red today: a real run (the stub plays the session and leaves a good ``classes.json``) delivers, exit 0, and the
    wall's tar holds ``input/set/q01.yaml`` but no member under ``input/set/dropped``."""
    s.plant(world, s.DROPPED)
    run = world.deliver("auditor", out=s.s173.auditor_out(), set_=s.SET)
    assert run.code == 0, run.why()
    assert run.line and run.line["status"] == "delivered", run.line
    names = world.tar_names(run.line)
    assert any(n.endswith("/input/set/q01.yaml") for n in names), "the tar holds no copy of the set"
    leaked = [n for n in names if "/input/set/dropped" in n]
    assert leaked == [], f"the packed wall holds dropped paths: {leaked}"
    assert all((s.hidden_dir(world) / rel).is_file() for rel in s.DROPPED), "a dropped file left the source set"
