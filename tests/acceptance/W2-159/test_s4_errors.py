"""S4: a check never traps a session and never fails open silently: on any error the turn ends and the error is named to
the owner (``systemMessage``, no ``decision``) and in the check's log; a stand-by note does not let a turn end idle in S2
(unblocked work moves while the owner decides). F2 (a check that fails with no message, or traps a session it cannot
read) is the first two cases seen from the failure side.

The lead's reading: an error is a ``state.json`` that exists but cannot be read or parsed (here: not JSON; a folder in its
place), for the registered session, in both checks; for another session the check says nothing. The cases on an unusable
``gov`` program and a missing item file take S4's "on any error" as written: no block, a message, a log line.
Sources: DEC-1110 (1), DEC-1109 (3).
"""

import pytest

import w2_159_support as support
from w2_159_support import NAMES_ERROR, assert_blocks, assert_no_block

CHECKS = ["waiter", "idle"]


def _spoil_state(w, how):
    path = w.state_path()
    if how == "garbage":
        path.write_text("{this is not json", encoding="utf-8")
    else:
        path.mkdir()


@pytest.mark.parametrize("check", CHECKS)
@pytest.mark.parametrize("how", ["garbage", "folder"])
def test_s4_an_unreadable_state_file_ends_the_turn_names_the_error_and_logs_it(w, check, how):
    w.blocking_project()  # without the error, both checks would block
    _spoil_state(w, how)
    result = w.run(check)
    assert not result.blocked, f"an error never traps the session (no block):\n{result}"
    assert result.doc is not None and result.message.strip(), f"the error is named in a systemMessage:\n{result}"
    assert NAMES_ERROR.search(result.message), f"the systemMessage names the error:\n{result}"
    assert result.log_new, f"the error is named in the check's log:\n{result}"
    assert any("\t" in line and NAMES_ERROR.search(line) for line in result.log_new), \
        f"a tab-separated log line naming the error:\n{result}"


@pytest.mark.parametrize("check", CHECKS)
def test_s4_an_unreadable_state_file_is_not_an_error_for_another_session(w, check):
    w.blocking_project()
    _spoil_state(w, "garbage")
    result = w.run(check, session=support.OTHER)
    assert result.silent, f"another session's id: the check says nothing:\n{result}"


@pytest.mark.parametrize("check", CHECKS)
def test_s4_a_missing_state_file_is_an_empty_state_not_an_error(w, check):
    w.blocking_project()
    assert not w.state_path().exists()
    result = w.run(check)
    assert_blocks(result, "(no state file: nothing blocked yet this turn)")


def test_s4_a_stand_by_note_does_not_let_the_idle_check_end_the_turn(w):
    w.blocking_project()
    w.standby(10 * support.MINUTE)
    idle = w.run("idle")
    assert_blocks(idle, "(a fresh stand-by note beside unblocked items: unblocked work moves while the owner decides)")
    assert {"DAEO-u101", "DAEO-u102"} <= support.ids_named(idle.reason)
    waiter = w.run("waiter")
    assert_no_block(waiter, "(the same note does let the waiter check say nothing: S1)")


def test_s4_an_unusable_gov_program_is_named_and_does_not_block(w):
    w.waiter_configured()
    w.cfg(items={"source": "dispatcher"})
    w.status()
    # GOV_SESSION_WATCH_GOV names a program that does not exist: the plan cannot be read.
    result = w.run("idle")
    assert not result.blocked, f"no block on a plan that cannot be read:\n{result}"
    assert result.message.strip(), f"the owner is told (systemMessage):\n{result}"
    assert result.log_new, f"the log has a line for it:\n{result}"


def test_s4_a_missing_item_file_is_named_and_does_not_block(w):
    w.items_lines("DAEO-u101 READY\n", rel="items/open.txt")
    (w.root / "items" / "open.txt").unlink()
    w.status()
    result = w.run("idle")
    assert not result.blocked, f"no block on an item file that cannot be read:\n{result}"
    assert result.message.strip(), f"the owner is told (systemMessage):\n{result}"
    assert NAMES_ERROR.search(result.message + result.log_text), f"the error is named:\n{result}"
    assert result.log_new, f"the log has a line for it:\n{result}"
