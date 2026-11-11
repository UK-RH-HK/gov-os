"""S1, the follow-up R3 (DEC-1112 (3), DEC-1114): a killed test run's folders are removed by the next run.

S1: a suite that builds the code graph uses one daemon folder per test session, cleaned when the session ends, so no
daemon folder is left behind [DEC-799 item 1, DEC-1052, P1-PLAN T-8]. The review's R3 (round 1): a run that is
killed (SIGKILL, a heavy-slot timeout) leaves its folder for daemon folders (``CODEINTEL_DAEMON_BASE``) and its
links folder (``gov-path-*``) behind, and no weekly sweep covers them (DEC-902's list).

What holds after the follow-up, point by point (the CTO's brief):

1. a run killed after it made its folders leaves them; the next run, when it starts, removes them (in the place
   where that run makes its own; the links folder in its temp root);
2. a live run's folder is never removed: run A held in its case, run B starts and ends, A's folders are still there,
   and A then ends normally and removes its own;
3. only this user's real folders with the run-folder names are touched: never a link (nor its target), never the
   shared ``/tmp/gov-cbm-<uid>`` or anything in it, never ``/tmp/gov-launch-*``, never a folder of another name;
4. a folder whose owner cannot be told is kept, unless it was last modified more than 24 hours ago (DEC-902);
5. a clean-up that cannot remove something never fails, stops or delays the run.

The places, the runs and the plants are ``w2_56_sweep_support``'s. Each case reads the place from its runs (never
assumes it). The ``real-tmp`` cases and the two pid-namespace cases carry ``real`` in their node ids, so the sandbox's
exclusion (``-k "not real ..."``) leaves them out; they also skip themselves where ``/tmp`` is read-only or ``bwrap``
cannot make a pid namespace.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import w2_56_sweep_support as sw

PLACES = pytest.mark.parametrize("where", sw.PLACES)


def _killed(p: sw.Place, label: str, prefix=()) -> tuple[dict, list[str]]:
    """A run held in its case and killed by SIGKILL once its record is written: its record and its folders, which
    are still there (a killed run cannot clean)."""
    run = p.runs.start(label, hold=p.base / f"{label}.never", prefix=prefix)
    note = p.runs.wait_note(run)
    folders = sw.own_folders(note)
    if p.session is not None:
        assert sw.place_of(note) == p.session or str(sw.place_of(note)).startswith(str(p.session) + "/"), (
            f"premise (S1): inside a launched session the run's folder is not in the session's temp folder "
            f"{p.session}: {note['daemon_base']}")
    p.runs.kill(run)
    assert sw.there(folders) == folders, f"premise: the killed run's folders are not there: {folders}"
    return note, folders


def _same_place(first: dict, second: dict) -> None:
    assert sw.place_of(first) == sw.place_of(second) and first["temp_root"] == second["temp_root"], (
        f"premise: two runs started alike do not share their place: {first['daemon_base']} and "
        f"{second['daemon_base']}")


# --------------------------------------------------------------------------
# Point 1: a killed run's folders go when the next run starts
# --------------------------------------------------------------------------

@PLACES
def test_r3_a_killed_runs_folders_are_removed_when_the_next_run_starts(where):
    with sw.place(where) as p:
        killed, left = _killed(p, "a")
        after = p.runs.finished(p.runs.start("b", watch=left))
        _same_place(killed, after)
        seen = [path for path, present in after["watched"].items() if present]
        assert not seen, (f"the killed run's folders were still there when the next run's case ran (its start did "
                          f"not remove them): {seen}")
        assert not sw.there(left), f"the killed run's folders are left after the next run: {sw.there(left)}"


# --------------------------------------------------------------------------
# Point 2: a live run's folders are never removed
# --------------------------------------------------------------------------

def _live_run_kept(p: sw.Place, prefix_a=(), prefix_b=()) -> tuple[dict, dict]:
    release = p.base / "a.release"
    a = p.runs.start("a", hold=release, prefix=prefix_a)
    live = p.runs.wait_note(a)
    mine = sw.own_folders(live)
    b = p.runs.start("b", watch=mine, prefix=prefix_b)
    other = p.runs.finished(b)
    _same_place(live, other)
    assert a.process.poll() is None, f"premise: run A ended while it was held:\n{a.text()}"
    gone = [path for path, present in other["watched"].items() if not present]
    assert not gone, f"run B removed live run A's folders while A ran: {gone}"
    assert sw.there(mine) == mine, f"live run A's folders are gone after run B ended: {sorted(set(mine) - set(sw.there(mine)))}"
    assert not sw.there(sw.own_folders(other)), f"run B left its own folders: {sw.there(sw.own_folders(other))}"
    release.write_text("go\n", encoding="utf-8")
    assert p.runs.finish(a) == 0, f"run A did not end normally once let go:\n{a.text()}"
    assert not sw.there(mine), f"run A did not remove its own folders when it ended: {sw.there(mine)}"
    return live, other


@PLACES
def test_r3_a_live_runs_folders_are_kept_while_another_run_starts_and_ends(where):
    with sw.place(where) as p:
        _live_run_kept(p)


def test_r3_real_namespaces_a_live_run_in_another_pid_namespace_keeps_its_folders():
    """Two commands of one sandboxed session each run in a pid namespace of their own (seen in the launch sandbox:
    a run's pid there is 4 or 5). Run A's pid, as A wrote it, is one run B's namespace does not hold."""
    why = sw.namespaces_refused()
    if why:
        pytest.skip(why)
    with sw.place("session") as p:
        live, other = _live_run_kept(p, prefix_a=sw.namespace_prefix(40), prefix_b=sw.namespace_prefix(0))
        assert live["pid_namespace"] != other["pid_namespace"], (
            f"premise: runs A and B ran in one pid namespace: {live['pid_namespace']}")


def test_r3_real_namespaces_a_killed_runs_folders_in_another_pid_namespace_are_removed():
    """Point 1 across pid namespaces (D-15 in the README: the CTO keeps or drops this case)."""
    why = sw.namespaces_refused()
    if why:
        pytest.skip(why)
    with sw.place("session") as p:
        killed, left = _killed(p, "a", prefix=sw.namespace_prefix(40))
        after = p.runs.finished(p.runs.start("b", watch=left, prefix=sw.namespace_prefix(0)))
        assert killed["pid_namespace"] != after["pid_namespace"], (
            f"premise: runs A and B ran in one pid namespace: {killed['pid_namespace']}")
        seen = [path for path, present in after["watched"].items() if present]
        assert not seen, (f"a killed run's folders, made in another pid namespace, were still there when the next "
                          f"run's case ran: {seen}")


# --------------------------------------------------------------------------
# Point 3: only this user's real folders with the run-folder names
# --------------------------------------------------------------------------

@PLACES
def test_r3_a_link_at_a_run_folders_name_is_never_removed_nor_followed(where):
    """A killed run's folders (the code's own names) replaced by links to folders outside, 25 hours old."""
    with sw.place(where) as p:
        _, left = _killed(p, "donor")
        links = [sw.link_to_outside(path, p.base) for path in left]
        p.runs.finished(p.runs.start("b"))
        for link, target in links:
            assert link.is_symlink() and os.readlink(link) == str(target), (
                f"a link with a run folder's name was removed or changed: {link} ({sw.kind(link)})")
            assert sw.kind(target) == "folder: kept.txt", f"the link's target was touched: {target} ({sw.kind(target)})"


@PLACES
def test_r3_folders_of_other_names_and_the_shared_places_are_never_removed(where):
    """In the place and the temp root, 25 hours old: folders of other names (the shared default daemon place's name,
    a launcher temp folder's form, the session's own ``cbm``, others), and regular files at the killed run's folder
    names. In the real /tmp the shared ``/tmp/gov-cbm-<uid>`` and the live ``/tmp/gov-launch-*`` are there already:
    the case plants a run folder's form inside the shared folder and a launcher folder's form beside them."""
    with sw.place(where) as p:
        killed, left = _killed(p, "donor")
        home, temp_root = sw.place_of(killed), Path(killed["temp_root"])
        planted = []
        if sw.in_real_tmp(home):
            planted.append(sw.plant_folder(home, prefix="gov-launch-w56"))
            planted.append(sw.plant_folder(home, prefix="w56-other-"))
            if sw.SHARED.is_dir() and not sw.SHARED.is_symlink() and sw.SHARED.stat().st_uid == sw.UID:
                planted.append(sw.plant_folder(sw.SHARED, prefix=f"gov-cbm-{sw.UID}-w56"))
            p.planted.extend(planted)
        else:
            for name in (f"gov-cbm-{sw.UID}", "cbm", "cc-socks"):
                if not os.path.lexists(home / name):
                    planted.append(sw.plant_folder(home, name=name))
            planted.append(sw.plant_folder(home, prefix="gov-launch-w56"))
            planted.append(sw.plant_folder(home, prefix="w56-other-"))
        for prefix in ("gov-pathology-", "w56-gov-path-"):
            made = sw.plant_folder(temp_root, prefix=prefix)
            planted.append(made)
            if sw.in_real_tmp(temp_root):
                p.planted.append(made)
        planted += [sw.plant_file(path) for path in left]
        before = {str(path): sw.kind(path) for path in planted}
        shared = sw.SHARED.is_dir()
        p.runs.finished(p.runs.start("b"))
        changed = {path: (was, sw.kind(path)) for path, was in before.items() if sw.kind(path) != was}
        assert not changed, f"the next run removed or changed what is not a run folder of this user's: {changed}"
        if sw.in_real_tmp(home):
            assert sw.SHARED.is_dir() == shared, f"the shared default daemon place {sw.SHARED} was removed"


# --------------------------------------------------------------------------
# Point 4: an owner that cannot be told
# --------------------------------------------------------------------------

@PLACES
def test_r3_a_folder_with_no_owner_record_younger_than_24_hours_is_kept(where):
    """Killed runs' folders emptied in place (as older code, or a run being made, leaves one): one fresh, one 23
    hours old."""
    with sw.place(where) as p:
        _, fresh = _killed(p, "donor-1")
        _, young = _killed(p, "donor-2")
        made = [sw.bare(path) for path in fresh] + [sw.bare(path, sw.YOUNG_S) for path in young]
        p.runs.finished(p.runs.start("b"))
        lost = [str(path) for path in made if sw.kind(path) != "folder: older-code.txt"]
        assert not lost, f"folders with no owner record, under 24 hours old, were removed: {lost}"


@PLACES
def test_r3_a_folder_with_no_owner_record_older_than_24_hours_is_removed(where):
    """A killed run's folders emptied in place and last modified 25 hours ago (DEC-902's line)."""
    with sw.place(where) as p:
        _, left = _killed(p, "donor")
        old = [str(sw.bare(path, sw.OLD_S)) for path in left]
        p.runs.finished(p.runs.start("b"))
        assert not sw.there(old), f"folders with no owner record, over 24 hours old, were kept: {sw.there(old)}"


# --------------------------------------------------------------------------
# Point 5: a clean-up that cannot remove something
# --------------------------------------------------------------------------

@pytest.mark.parametrize("where", ("session", "temp-root"))
def test_r3_a_folder_the_clean_up_cannot_simply_remove_never_fails_or_delays_the_run(where):
    """A killed run's folders emptied in place, 25 hours old, with their write bits taken (and a folder inside
    without its own): the next run starts and its case runs, in no more than an ordinary run's time and a margin.
    The clean-up may open them and remove them, or leave them; either is right."""
    with sw.place(where) as p:
        ordinary = p.runs.start("ordinary")
        p.runs.finished(ordinary)
        _, left = _killed(p, "donor")
        for path in left:
            sw.stuck(path)
        b = p.runs.start("b")
        note = p.runs.finished(b)
        assert note.get("daemon_base_exists"), f"the run did not make its own folder: {note}"
        assert b.seconds <= ordinary.seconds + sw.SLACK_S, (
            f"the run took {b.seconds:.1f} s beside a folder it cannot simply remove; an ordinary run took "
            f"{ordinary.seconds:.1f} s")
