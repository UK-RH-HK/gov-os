"""W2-201 fix X8 (DEC-1219 (5)): a worker fix gets a run folder.

``gov launch engineer <ticket> --fix "<line>"`` on W2-184's fixture project and the stand-in CLI, with HOME the
sandbox's, so the runs root is ``<HOME>/gov-os-runs``. A worker launched with ``--fix`` on a closed (or open) ticket
gets the run folder an in_progress ticket's worker gets: ``<root>/<the ticket's external-ref>``, made with its marker
``.gov-os-repository`` naming the repository's git common directory when it is not there, reused (never removed or
rewritten) when it is, and handed to the session as an in_progress worker's. A feature launch on a closed ticket is
refused and gets none; a chore makes none.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

import w2_201_x_support as x

s, b = x.s, x.b
MARKER = ".gov-os-repository"
PLANTED = "notes.txt"


def _name(project, tk):
    """The run folder's name the ticket gives: its external-ref as written, else its id."""
    text = (Path(project) / ".tickets" / f"{tk}.md").read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1]) or {}
    return front.get("external-ref") or tk


def _folder(sandbox, project, tk):
    return Path(sandbox.home) / x.RUNS_NAME / _name(project, tk)


def _marker_text(project):
    return os.path.realpath(Path(project) / ".git") + "\n"


def _assert_made(sandbox, project, tk, where):
    folder = _folder(sandbox, project, tk)
    assert folder.is_dir() and not folder.is_symlink(), (
        f"{where}: no run folder {folder}; under the runs root: {x.runs_listing(sandbox)}")
    marker = folder / MARKER
    assert marker.is_file(), f"{where}: the run folder {folder} has no marker {MARKER}"
    assert marker.read_text(encoding="utf-8") == _marker_text(project), (
        f"{where}: the marker names {marker.read_text(encoding='utf-8')!r}, not the repository's "
        f"{_marker_text(project)!r}")
    return folder


def _in_progress_folder(sandbox, project, cli):
    """What holds on the base: an in_progress ticket's engineer gets its run folder, with its marker; the launch."""
    tk = s.ticket(project, x.ENGINEER, "C2", tk="DAEO-x8ip")
    result = x.launch(sandbox, cli, x.ENGINEER, tk)
    x.launched(result)
    _assert_made(sandbox, project, tk, "the in_progress launch (the plant's own check)")
    return tk, result


@pytest.mark.parametrize("status", ["closed", "open"])
def test_x8_a_fix_launch_gets_its_run_folder_with_the_marker(sandbox, project, cli, status):
    _in_progress_folder(sandbox, project, cli)
    tk = x.ticket(project, x.ENGINEER, "C2", status, tk=f"DAEO-x8f{status[0]}")
    result = x.launch(sandbox, cli, x.ENGINEER, tk, "--fix", x.FIX_LINE)
    x.launched(result)
    assert x.record_of(result, "kind")["kind"] == "fix", "fixture: the launch is not a fix's"
    _assert_made(sandbox, project, tk, f"the fix launch on the {status} ticket")


def test_x8_the_same_fix_launch_repeated_reuses_the_folder_and_leaves_what_it_holds(sandbox, project, cli):
    tk = x.ticket(project, x.ENGINEER, "C2", "closed", tk="DAEO-x8rp")
    x.launched(x.launch(sandbox, cli, x.ENGINEER, tk, "--fix", x.FIX_LINE))
    folder = _assert_made(sandbox, project, tk, "the first fix launch")
    (folder / PLANTED).write_text("the session's own notes\n", encoding="utf-8")
    listing, marker = x.runs_listing(sandbox), (folder / MARKER).read_bytes()
    x.launched(x.launch(sandbox, cli, x.ENGINEER, tk, "--fix", x.FIX_LINE))
    _assert_made(sandbox, project, tk, "the second fix launch")
    assert x.runs_listing(sandbox) == listing, f"the second launch made another folder: {x.runs_listing(sandbox)}"
    assert (folder / PLANTED).read_text(encoding="utf-8") == "the session's own notes\n", "what the folder held changed"
    assert (folder / MARKER).read_bytes() == marker, "the marker was rewritten"


def test_x8_a_fix_reuses_the_folder_an_earlier_in_progress_launch_of_the_ticket_made(sandbox, project, cli):
    """Guard on the base: the folder the ticket's in_progress worker had is there, untouched, after its fix."""
    tk = s.ticket(project, x.ENGINEER, "C2", tk="DAEO-x8er")
    x.launched(x.launch(sandbox, cli, x.ENGINEER, tk))
    folder = _assert_made(sandbox, project, tk, "the in_progress launch")
    (folder / PLANTED).write_text("work of the feature\n", encoding="utf-8")
    path = Path(project) / ".tickets" / f"{tk}.md"
    path.write_text(path.read_text(encoding="utf-8").replace("status: in_progress\n", "status: closed\n", 1),
                    encoding="utf-8")
    listing = x.runs_listing(sandbox)
    x.launched(x.launch(sandbox, cli, x.ENGINEER, tk, "--fix", x.FIX_LINE))
    _assert_made(sandbox, project, tk, "the fix launch")
    assert x.runs_listing(sandbox) == listing, f"the fix made another folder: {x.runs_listing(sandbox)}"
    assert (folder / PLANTED).read_text(encoding="utf-8") == "work of the feature\n", "what the folder held changed"


def _places(result, folder):
    """Where the session is told of ``folder``: ``(place, key)`` of the ``--settings`` env block, the CLI process's
    environment and the CLI's arguments whose value names it."""
    text = str(folder)
    block, env = x.env_pair(result)
    found = {("settings env", key) for key, value in block.items() if isinstance(value, str) and text in value}
    found |= {("process env", key) for key, value in env.items() if isinstance(value, str) and text in value}
    found |= {("argument", index) for index, arg in enumerate(result.args) if text in arg}
    settings = result.settings()
    for key, value in settings.items():
        if key != "env" and text in str(value):
            found.add(("settings", key))
    return found


def test_x8_the_fix_session_is_handed_its_folder_as_an_in_progress_worker_is(sandbox, project, cli):
    ip_tk, ip_result = _in_progress_folder(sandbox, project, cli)
    tk = x.ticket(project, x.ENGINEER, "C2", "closed", tk="DAEO-x8hd")
    result = x.launch(sandbox, cli, x.ENGINEER, tk, "--fix", x.FIX_LINE)
    x.launched(result)
    folder = _assert_made(sandbox, project, tk, "the fix launch")
    want = {(place, key) for place, key in _places(ip_result, _folder(sandbox, project, ip_tk))
            if place != "argument"}
    got = {(place, key) for place, key in _places(result, folder) if place != "argument"}
    assert got == want, (f"the fix session is told of its run folder in {sorted(got, key=str)}, an in_progress "
                         f"worker in {sorted(want, key=str)}")
    block, env = x.env_pair(result)
    assert block.get("GOV_TICKET") == tk and env.get("GOV_TICKET") == tk, "the fix session's GOV_TICKET"


def test_x8_a_feature_launch_on_a_closed_ticket_is_refused_and_gets_no_folder(sandbox, project, cli):
    """Guard on the base."""
    tk = x.ticket(project, x.ENGINEER, "C2", "closed", tk="DAEO-x8nf")
    s.refused(x.launch(sandbox, cli, x.ENGINEER, tk), "is not in_progress")
    assert not _folder(sandbox, project, tk).exists(), f"a refused launch made {_folder(sandbox, project, tk)}"


def test_x8_a_chore_makes_no_run_folder(sandbox, project, cli):
    """Guard on the base."""
    before = x.runs_listing(sandbox)
    x.launched(x.launch(sandbox, cli, x.ENGINEER, "--chore", x.CHORE_LINE))
    assert x.runs_listing(sandbox) == before, f"a chore made a run folder: {x.runs_listing(sandbox)}"
