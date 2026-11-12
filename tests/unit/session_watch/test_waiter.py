"""S1: the waiter check, on planted process lists, session files and stand-by notes."""

from __future__ import annotations

from .conftest import HOUR, WAITER_CONFIG

WAITER = {"pid": 4001, "cmdline": "bash tools/inbox-wait --quiet", "start": 1_799_990_000, "state": "S", "fds": []}


def test_an_absent_waiter_blocks_naming_it_and_its_command(hook):
    hook.config("session_watch:\n  waiter_commands: ['inbox-wait', 'other-wait']\n  waiter_arm: 'bash run-the-waiter'\n")
    out = hook.run("waiter")
    assert out["decision"] == "block"
    assert "inbox waiter" in out["reason"] and "bash run-the-waiter" in out["reason"]


def test_the_arm_command_defaults_to_the_first_waiter_command(hook):
    hook.config(WAITER_CONFIG)
    assert "`inbox-wait`" in hook.run("waiter")["reason"]


def test_a_running_waiter_says_nothing(hook):
    hook.config(WAITER_CONFIG)
    hook.procs({**WAITER, "cmdline": "x other-wait y"})
    assert hook.run("waiter") is None


def test_a_dead_waiter_does_not_count(hook):
    hook.config(WAITER_CONFIG)
    hook.procs({**WAITER, "state": "Z"})
    assert hook.run("waiter")["decision"] == "block"


def test_a_younger_standby_note_says_nothing_and_an_older_one_does_not_hold(hook):
    hook.config(WAITER_CONFIG)
    hook.standby(HOUR)
    assert hook.run("waiter") is None
    hook.standby(3 * HOUR)
    assert hook.run("waiter", extra={}) is not None  # the same turn: blocked once, then the bound says nothing
    hook.new_turn()
    hook.config("session_watch:\n  waiter_commands: ['inbox-wait']\n  standby_max_age_h: 4\n")
    assert hook.run("waiter") is None  # 3 h is younger than a 4 h limit


def test_another_session_no_session_file_and_an_unreadable_one_say_nothing(hook):
    hook.config(WAITER_CONFIG)
    assert hook.run("waiter", session="someone-else") is None
    (hook.folder / "session.txt").unlink()
    assert hook.run("waiter") is None
    (hook.folder / "session.txt").mkdir()  # a directory cannot be read as the session file
    assert hook.run("waiter") is None
    assert hook.log() == ""


def test_no_configured_waiter_says_nothing(hook):
    assert hook.run("waiter") is None
    hook.config("session_watch:\n  waiter_commands: []\n")
    assert hook.run("waiter") is None


def test_the_waiter_is_recorded_in_the_log(hook):
    hook.config(WAITER_CONFIG)
    hook.run("waiter")
    line = hook.log().splitlines()[0].split("\t")
    assert "waiter" in line and "block" in line
