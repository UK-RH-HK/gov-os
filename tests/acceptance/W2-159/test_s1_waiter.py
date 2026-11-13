"""S1: ``gov session-watch stop-check waiter`` blocks when the registered orchestrator session's inbox waiter is not
running and no stand-by note younger than its limit is present; in every other case it says nothing.

Planted: ``waiter_commands`` (substrings of a process's command line) and ``waiter_arm`` in
``governance/project/session-watch.yaml``, the registered session in ``.gov-runtime/session-watch/session.txt``, a planted
process list, a stand-by note with a set mtime. Sources: DEC-1027, DEC-1028.
"""

import os

import pytest

import w2_159_support as support
from w2_159_support import assert_blocks, assert_no_block

ARM = "bash tools/arm-inbox-waiter.sh --background"


def _bystanders(w):
    w.proc(1201, "python3 -m http.server 8000")
    w.proc(1202, "bash /opt/other/tools/sync.sh --loop")


def test_s1_waiter_absent_blocks_naming_the_waiter_and_its_arm_command(w):
    w.waiter_configured(ARM)
    _bystanders(w)
    result = w.run("waiter")
    assert_blocks(result, "(waiter configured, not in the process list, registered session, no stand-by note)")
    assert "waiter" in result.reason.lower(), f"the reason names the inbox waiter:\n{result}"
    assert ARM in result.reason, f"the reason names the waiter_arm command as configured:\n{result}"
    assert any("\t" in line and "waiter" in line.lower() for line in result.log_new), \
        f"one tab-separated log line with the check's name:\n{result}"


def test_s1_waiter_arm_defaults_to_the_first_waiter_command(w):
    w.waiter_configured(arm=None)
    result = w.run("waiter")
    assert_blocks(result, "(no waiter_arm: default the first of waiter_commands)")
    assert "tools/inbox-wait.sh" in result.reason, f"the default arm command is the first waiter command:\n{result}"


@pytest.mark.parametrize("cmdline", ["bash /srv/proj/tools/inbox-wait.sh --quiet",
                                     "/bin/bash /srv/proj/tools/inbox-wait-quiet.sh"],
                         ids=["first-command", "second-command"])
def test_s1_a_running_waiter_says_nothing(w, cmdline):
    w.waiter_configured(ARM)
    _bystanders(w)
    w.proc(4300, cmdline)
    result = w.run("waiter")
    assert_no_block(result, "(a process of a configured waiter command is running)")


def test_s1_a_process_that_only_resembles_the_waiter_does_not_count(w):
    w.cfg(waiter_commands=["tools/inbox-wait-quiet.sh"], waiter_arm=ARM)
    w.proc(4301, "bash /srv/proj/tools/inbox-wait.sh --loop")  # not a substring match of the configured command
    result = w.run("waiter")
    assert_blocks(result, "(only a similar process runs)")


def test_s1_a_stand_by_note_younger_than_the_limit_says_nothing(w):
    w.waiter_configured(ARM)
    w.standby(1 * support.HOUR)
    result = w.run("waiter")
    assert_no_block(result, "(a stand-by note an hour old, the limit is 2 h)")


def test_s1_a_stand_by_note_older_than_the_limit_blocks_again(w):
    w.waiter_configured(ARM)
    w.standby(3 * support.HOUR)
    result = w.run("waiter")
    assert_blocks(result, "(a stand-by note 3 h old, the limit is 2 h)")
    assert ARM in result.reason


@pytest.mark.parametrize("limit_h,age_h,blocks", [(1, 1.5, True), (4, 3, False)],
                         ids=["note-past-a-1h-limit", "note-within-a-4h-limit"])
def test_s1_the_stand_by_limit_is_the_configured_one(w, limit_h, age_h, blocks):
    w.waiter_configured(ARM)
    w.cfg(standby_max_age_h=limit_h)
    w.standby(age_h * support.HOUR)
    result = w.run("waiter")
    if blocks:
        assert_blocks(result, f"(note {age_h} h old, limit {limit_h} h)")
    else:
        assert_no_block(result, f"(note {age_h} h old, limit {limit_h} h)")


def test_s1_another_sessions_id_says_nothing(w):
    w.waiter_configured(ARM)
    result = w.run("waiter", session=support.OTHER)
    assert result.silent, f"another session's id: the check says nothing:\n{result}"
    assert_blocks(w.run("waiter"), "(the same project, the registered session: the premise of the case above)")


def test_s1_no_session_file_says_nothing(w):
    w.waiter_configured(ARM)
    w.unregister()
    result = w.run("waiter")
    assert result.silent, f"no registered session: the check says nothing:\n{result}"


def test_s1_a_session_file_that_is_a_folder_says_nothing(w):
    w.waiter_configured(ARM)
    (w.rt / "session.txt").unlink()
    (w.rt / "session.txt").mkdir()
    result = w.run("waiter")
    assert result.silent, f"a session file that cannot be read: the check says nothing:\n{result}"


@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="mode 000 does not stop root")
def test_s1_a_session_file_with_mode_000_says_nothing(w):
    w.waiter_configured(ARM)
    path = w.rt / "session.txt"
    path.chmod(0o000)
    try:
        result = w.run("waiter")
    finally:
        path.chmod(0o644)
    assert result.silent, f"a session file that cannot be read: the check says nothing:\n{result}"


@pytest.mark.parametrize("config", [{}, {"waiter_commands": []}], ids=["unset", "empty"])
def test_s1_without_waiter_commands_the_check_says_nothing(w, config):
    w.cfg(standby_max_age_h=2, **config)  # a configuration file with the key unset or empty: nothing to arm
    result = w.run("waiter")
    assert result.silent, f"no waiter_commands: the waiter check says nothing:\n{result}"
