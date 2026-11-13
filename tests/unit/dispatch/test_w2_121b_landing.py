"""Part b's logic the acceptance suite does not reach: the claim's parsing, the hold window across midnight, the finalise
after a half-done pass, the ancestor walk of the heavy steps, the record commit's retries and the new configuration keys.
No real model, no ``claude``, no ``gov close``: files, a temporary git repository and plain data."""
from __future__ import annotations

import datetime
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from gov.dispatch import config as configuration  # noqa: E402
from gov.dispatch import heavy, landing, status  # noqa: E402
from gov.dispatch import state as states  # noqa: E402

A, B = "W2-1=a1b2c3d4e5f6", "W2-2=b2c3d4e5f6a1"
IDENTITY = {"GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "T",
            "GIT_COMMITTER_EMAIL": "t@example.invalid", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}


def local(hour: int, minute: int = 0, day: int = 12) -> datetime.datetime:
    """A moment of local time, aware (the hold reads local time whatever the machine's zone)."""
    return datetime.datetime(2026, 11, day, hour, minute).astimezone()


# --- the approvals --------------------------------------------------------------------------------------------------

def test_split_lines_keeps_well_formed_approvals_once_and_names_the_rest():
    good, bad = landing.split_lines([A, "W2-9=xyz", B, A, "W2-3", "W2-4=A1B2C3D4E5F6", "W2-5=a1b2c3d4e5f6a"])
    assert good == [A, B]
    assert bad == ["W2-9=xyz", "W2-3", "W2-4=A1B2C3D4E5F6", "W2-5=a1b2c3d4e5f6a"]


def test_command_for_replaces_the_token_in_place_or_appends():
    assert landing.command_for(["x", "--a", "{approvals}", "--b"], [A, B]) == ["x", "--a", A, B, "--b"]
    assert landing.command_for(["x", "--a"], [A, B]) == ["x", "--a", A, B]


def test_done_set_leaves_out_the_lines_of_the_landing_being_finalised(tmp_path):
    state = states.State(tmp_path)
    state.make()
    state.append(landing.DONE, f"{A} 2026-11-12T10:00:00+00:00 0 land-1")
    state.append(landing.DONE, f"{B} 2026-11-12T11:00:00+00:00 0 land-2")
    assert landing.done_set(state) == {A, B}
    assert landing.done_set(state, "land-2") == {A}


def test_the_land_id_moves_on_when_its_second_was_used(tmp_path):
    state = states.State(tmp_path)
    state.make()
    moment = datetime.datetime(2026, 11, 12, 10, 0, 0, tzinfo=datetime.timezone.utc)
    first = landing.new_id(state, moment)
    assert first == "land-20261112T100000Z"
    state.write_item(first + landing.ITEM_SUFFIX, ["log: " + first])
    assert landing.new_id(state, moment) == "land-20261112T100001Z"


def test_finalise_finishes_a_pass_that_died_after_some_done_lines(tmp_path):
    state = states.State(tmp_path)
    state.make()
    land_id = "land-20261112T100000Z"
    state.file(f"land-claimed-{land_id}.txt").write_text(f"{A}\nW2-9=xyz\n{B}\n", encoding="utf-8")
    state.exit_file(land_id).write_text("3\n", encoding="utf-8")
    state.append(landing.DONE, f"{A} 2026-11-12T10:00:00+00:00 3 {land_id}")  # the first line was written, then a crash
    done = landing.finalise(state, datetime.datetime.now(datetime.timezone.utc))
    assert done == [{"land_id": land_id, "status": "failed (exit 3)", "W2": ["W2-1", "W2-2"]}]
    lines = state.lines(landing.DONE)
    assert [line.split()[0] for line in lines] == [A, B] and all(line.endswith(f"3 {land_id}") for line in lines)
    item = (state.inbox / f"{land_id}.land.txt").read_text(encoding="utf-8").splitlines()
    assert item == [f"log: {land_id}", "W2: W2-1 W2-2", "status: failed (exit 3)", "kind: land"]
    assert not state.file(f"land-claimed-{land_id}.txt").exists()
    assert landing.finalise(state, datetime.datetime.now(datetime.timezone.utc)) == []


def test_finalise_waits_for_the_exit_file(tmp_path):
    state = states.State(tmp_path)
    state.make()
    state.file("land-claimed-land-1.txt").write_text(A + "\n", encoding="utf-8")
    assert landing.finalise(state, datetime.datetime.now(datetime.timezone.utc)) == []
    assert state.file("land-claimed-land-1.txt").exists()


# --- the nightly hold -------------------------------------------------------------------------------------------------

def hold(**values):
    return {"from": "23:00", "until": "06:00", **values}


@pytest.mark.parametrize("hour,minute,held", [(22, 59, False), (23, 0, True), (23, 59, True), (0, 0, True), (3, 30, True),
                                              (5, 59, True), (6, 0, False), (12, 0, False)])
def test_a_window_crossing_midnight_holds_from_and_until(tmp_path, hour, minute, held):
    assert (landing.nightly(hold(), tmp_path, local(hour, minute)) is not None) is held


@pytest.mark.parametrize("hour,held", [(0, False), (1, True), (4, True), (5, False), (23, False)])
def test_a_window_within_a_day_holds_only_inside_it(tmp_path, hour, held):
    assert (landing.nightly({"from": "01:00", "until": "05:00"}, tmp_path, local(hour)) is not None) is held


def test_no_hold_configured_or_an_empty_window_never_holds(tmp_path):
    assert landing.nightly(None, tmp_path, local(3)) is None
    assert landing.nightly({"from": "03:00", "until": "03:00"}, tmp_path, local(3)) is None


def test_the_marker_ends_the_hold_when_newer_than_the_window_start(tmp_path):
    marker = tmp_path / "running.marker"
    text = "held for the nightly until it starts (from 23:00, at the latest 06:00)"
    assert landing.nightly(hold(marker="running.marker"), tmp_path, local(2)) == text  # no marker yet
    stamp = local(23, 30, day=11).timestamp()  # after yesterday's `from`: this window's start, 02:00 is in it
    marker.write_text("", encoding="utf-8")
    os.utime(marker, (stamp, stamp))
    assert landing.nightly(hold(marker="running.marker"), tmp_path, local(2)) is None
    old = local(22, 0, day=11).timestamp()  # before that `from`: last night's marker
    os.utime(marker, (old, old))
    assert landing.nightly(hold(marker="running.marker"), tmp_path, local(2)) == text
    assert landing.nightly(hold(marker=str(marker)), tmp_path, local(2)) == text  # an absolute path works too


# --- the closes ---------------------------------------------------------------------------------------------------

def test_ticket_ids_map_a_w2_id_through_external_ref_or_wbs_id(tmp_path):
    folder = tmp_path / ".tickets"
    folder.mkdir()
    (folder / "DAEO-aaaa.md").write_text("---\nid: DAEO-aaaa\nexternal-ref: W2-1\ntitle: x  # no\n---\nbody\n", encoding="utf-8")
    (folder / "DAEO-bbbb.md").write_text("---\nid: DAEO-bbbb\nwbs_id: W2-2\n---\n", encoding="utf-8")
    (folder / "DAEO-cccc.md").write_text("---\nid: DAEO-cccc\nexternal-ref: W2-3\n---\n", encoding="utf-8")
    (folder / "notes.md").write_text("no front matter: external-ref: W2-1\n", encoding="utf-8")
    assert landing.ticket_ids(tmp_path, {"W2-1", "W2-2"}) == {"DAEO-aaaa", "DAEO-bbbb"}
    assert landing.ticket_ids(tmp_path / "missing", {"W2-1"}) == set()


def _plant(root: Path, pid: int, *argv: str) -> None:
    (root / str(pid)).mkdir(parents=True)
    (root / str(pid) / "cmdline").write_bytes(b"\0".join(a.encode() for a in argv) + b"\0")


def test_a_close_under_a_shell_wrapper_is_read_from_its_child(tmp_path, monkeypatch):
    from types import SimpleNamespace
    proc = tmp_path / "proc"
    _plant(proc, 500, "bash", "-c", "cd /x && gov-close-stub W2-7 ; echo done")
    _plant(proc, 501, "python3", "/opt/gov/gov-close-stub", "W2-7")
    _plant(proc, 600, "sh", "-c", "gov-close-stub W2-8 ; echo done")
    _plant(proc, 601, "python3", "/opt/gov/gov-close-stub", "W2-8")
    monkeypatch.setenv("GOV_RESOURCES_PROC", str(proc))
    table = {500: {"ppid": 1, "cmdline": "bash -c cd /x && gov-close-stub W2-7 ; echo done"},
             501: {"ppid": 500, "cmdline": "python3 /opt/gov/gov-close-stub W2-7"},
             600: {"ppid": 1, "cmdline": "sh -c gov-close-stub W2-8 ; echo done"},
             601: {"ppid": 600, "cmdline": "python3 /opt/gov/gov-close-stub W2-8"},
             700: {"ppid": 1, "cmdline": "sleep 100"}}
    assert set(landing.close_arguments(table, "gov-close-stub")) == {500, 501, 600, 601}
    ctx = SimpleNamespace(root=tmp_path, runner=SimpleNamespace(git=lambda *a: SimpleNamespace(code=1, out="")),
                          conf=SimpleNamespace(job_markers={"close": "gov-close-stub"}, close_record_paths=[]))
    jobs = SimpleNamespace(jobs=[{"kind": "close", "pid": 500}, {"kind": "close", "pid": 600}])
    assert "W2-7" in landing.conflicting_close(ctx, jobs, {"W2-7"}, [], table)
    assert landing.conflicting_close(ctx, jobs, {"W2-9"}, [], table) is None


# --- the heavy steps ------------------------------------------------------------------------------------------------

TABLE = {10: {"ppid": 1}, 11: {"ppid": 10}, 12: {"ppid": 11}, 20: {"ppid": 1}, 30: {"ppid": 31}, 31: {"ppid": 30}}


def test_a_step_is_in_the_slot_of_itself_or_the_nearest_ancestor_runner():
    runners = {10: 1, 11: 2}
    assert heavy.slot_of(12, TABLE, runners) == 2  # the nearest one wins
    assert heavy.slot_of(10, TABLE, runners) == 1  # itself
    assert heavy.slot_of(20, TABLE, runners) is None
    assert heavy.slot_of(99, TABLE, runners) is None  # not in the table


def test_the_walk_ends_at_init_and_at_a_loop():
    assert heavy.slot_of(30, TABLE, {}) is None
    assert heavy.slot_of(12, TABLE, {1: 7}) is None  # pid 1 is never a runner's ancestor of interest


def test_steps_lists_only_the_heavy_kinds_and_names_those_outside_a_slot():
    jobs = [{"kind": "test", "pid": 12}, {"kind": "check", "pid": 20}, {"kind": "close", "pid": 30},
            {"kind": "measure", "pid": 11}]
    found, findings = heavy.steps(jobs, TABLE, {10: 1})
    assert found == [{"kind": "test", "pid": 12, "slot": 1}, {"kind": "check", "pid": 20, "slot": None},
                     {"kind": "measure", "pid": 11, "slot": 1}]
    assert findings == ["heavy step outside a slot: check pid 20"]


def test_the_status_text_shows_the_land_line_the_hold_the_steps_and_the_findings():
    data = {"ok": True, "time": "2026-11-12T10:00:00+00:00", "outcome": "idle", "exit_code": 0, "running": [],
            "load": {"load_1m": 0, "load_15m": 0, "busy_cores": 0, "nproc": 1},
            "memory": {"available_bytes": 1, "floor_bytes": 1, "working_size_bytes": 1},
            "gate": {"open": True, "reasons": [], "disk": {}}, "slots": {"held": [], "total": 1},
            "peaks": {"computed": "x", "kinds": {}}, "peaks_ahead": {"memory_bytes": 0, "cpu": 0, "jobs": []},
            "queue": [], "inbox": [], "nightly_hold": None, "started": None, "skipped": [], "problems": [],
            "land": "claimed land-1: " + A, "land_hold": "held for the nightly until it starts (from 23:00, at the latest 06:00)",
            "land_notes": ["not sent: W2-9=xyz (not of the form <W2>=<12-hex>)"],
            "heavy_steps": [{"kind": "test", "pid": 5, "slot": 1}, {"kind": "check", "pid": 6, "slot": None}],
            "findings": ["heavy step outside a slot: check pid 6"]}
    text = status.render(data)
    assert f"land: claimed land-1: {A}" in text
    assert "land: held for the nightly until it starts (from 23:00, at the latest 06:00)" in text
    assert "land: not sent: W2-9=xyz" in text
    assert "heavy steps (2): test pid 5 slot 1, check pid 6 no slot" in text
    assert "findings:\n  heavy step outside a slot: check pid 6" in text


# --- the record commit ------------------------------------------------------------------------------------------------

def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for key, value in IDENTITY.items():
        monkeypatch.setenv(key, value)
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "integ")
    (root / "keep.txt").write_text("k\n", encoding="utf-8")
    git(root, "add", "keep.txt")
    git(root, "commit", "-q", "-m", "first")
    return root


def test_commit_records_commits_only_the_paths_given_with_the_trailers(repo):
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    (repo / "other.txt").write_text("o\n", encoding="utf-8")
    git(repo, "add", "other.txt")  # staged by someone else: not ours
    head = landing.commit_records(repo, ["a.txt"], "record a", ["Task: DAEO-test"])
    assert head == git(repo, "rev-parse", "HEAD").strip()
    assert git(repo, "show", "--name-only", "--format=%B", "HEAD").split() == ["record", "a", "Task:", "DAEO-test",
                                                                               "a.txt"]
    assert "other.txt" in git(repo, "diff", "--cached", "--name-only")


def test_commit_records_takes_trailers_as_a_dict_too(repo):
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    landing.commit_records(repo, ["a.txt"], "record a", {"Task": "DAEO-test", "Role": "x"})
    body = git(repo, "log", "-1", "--format=%B")
    assert "Task: DAEO-test" in body and "Role: x" in body


def test_commit_records_retries_while_index_lock_is_held_then_lands(repo):
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    lock = repo / ".git" / "index.lock"
    lock.write_text("", encoding="utf-8")
    threading.Timer(0.4, lock.unlink).start()
    started = time.monotonic()
    landing.commit_records(repo, ["a.txt"], "record a", [], attempts=5, wait_s=0.3)
    assert time.monotonic() - started >= 0.3, "the first attempt found the lock and waited"
    assert git(repo, "log", "-1", "--format=%s").strip() == "record a"


def test_commit_records_gives_up_after_its_attempts_and_names_the_lock(repo):
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    (repo / ".git" / "index.lock").write_text("", encoding="utf-8")
    with pytest.raises(landing.CommitFailed, match="index.lock"):
        landing.commit_records(repo, ["a.txt"], "record a", [], attempts=2, wait_s=0)
    assert git(repo, "log", "-1", "--format=%s").strip() == "first"


def test_commit_records_does_not_retry_another_failure(repo):
    with pytest.raises(landing.CommitFailed, match="git add"):
        landing.commit_records(repo, ["missing.txt"], "record", [], attempts=3, wait_s=5)


# --- the configuration -----------------------------------------------------------------------------------------------

def load(tmp_path, extra: str):
    file = tmp_path / configuration.FILE
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text("dispatch:\n  max_leads: 1\n  stagger_s: 0\n  cpu_band: 1\n  integration_branch: integ\n"
                    "  worktrees_root: wt\n  notifier_command: [n]\n" + extra, encoding="utf-8")
    return configuration.load(tmp_path)


def test_the_hold_takes_an_optional_marker_and_the_record_paths_a_list(tmp_path):
    conf = load(tmp_path, "  nightly_hold: {from: '22:00', until: '06:00', marker: run/started}\n"
                          "  close_record_paths: [docs/, .tickets/]\n")
    assert conf.nightly_hold == {"from": "22:00", "until": "06:00", "marker": "run/started"}
    assert conf.close_record_paths == ["docs/", ".tickets/"]
    plain = load(tmp_path, "  nightly_hold: {from: '22:00', until: '06:00'}\n")
    assert plain.nightly_hold == {"from": "22:00", "until": "06:00"} and plain.close_record_paths == []


@pytest.mark.parametrize("extra,key", [("  nightly_hold: {from: '22:00', until: '06:00', marker: ''}\n", "nightly_hold"),
                                       ("  nightly_hold: {from: '22:00', until: '06:00', other: x}\n", "nightly_hold"),
                                       ("  nightly_hold: {from: '22:00'}\n", "nightly_hold"),
                                       ("  close_record_paths: docs/\n", "close_record_paths"),
                                       ("  close_record_paths: [1]\n", "close_record_paths")])
def test_a_malformed_hold_or_record_path_is_a_configuration_error_naming_its_key(tmp_path, extra, key):
    with pytest.raises(configuration.ConfigError, match=key):
        load(tmp_path, extra)
