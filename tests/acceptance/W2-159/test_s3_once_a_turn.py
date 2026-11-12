"""S3: both checks block at most once per turn: never when ``stop_hook_active`` is set, never twice for the same turn (kept
in ``state.json``); a line ``IDLE-REASON: <why>`` in the orchestrator's messages of the turn lets the idle check end it and
is recorded in the log; neither a block nor a reason carries into the next turn.

A turn (the lead's reading, from the reference's definition): the transcript's JSON lines read back from the end to the last
``user`` entry that starts a turn (not a tool result, not ``isMeta``, or any user entry carrying ``turnOrigin`` or
``wakeupSource``); its ``uuid`` is the turn's key. The reason line is searched in the ``assistant`` entries' text after it and
in the hook input's ``last_assistant_message``. F1 (a turn blocked twice in a row) is these cases seen from the failure
side. Sources: DEC-1110 (1), DEC-1027.
"""

import pytest

import w2_159_support as support
from w2_159_support import assert_blocks, assert_no_block

CHECKS = ["waiter", "idle"]


@pytest.fixture
def b(w):
    """A project where both checks block."""
    w.blocking_project()
    return w


@pytest.mark.parametrize("check", CHECKS)
def test_s3_a_planted_turn_blocks_once_then_never_again_until_a_new_turn(b, check):
    first = b.run(check)
    assert_blocks(first, "(first call of the turn)")
    second = b.run(check, active=True)
    assert_no_block(second, "(second call, stop_hook_active set)")
    third = b.run(check)
    assert_no_block(third, "(third call, same turn, no stop_hook_active: already blocked this turn)")
    b.assistant("carrying on after the reminder")
    assert_no_block(b.run(check), "(the assistant's own message does not start a turn)")
    b.user("a new request from the owner")
    fourth = b.run(check)
    assert_blocks(fourth, "(a new turn: a new user entry in the transcript)")


@pytest.mark.parametrize("check", CHECKS)
def test_s3_stop_hook_active_never_blocks(b, check):
    result = b.run(check, active=True)
    assert_no_block(result, "(stop_hook_active set on the first call)")


@pytest.mark.parametrize("check", CHECKS)
def test_s3_the_bound_is_kept_in_the_state_file(b, check):
    assert_blocks(b.run(check))
    assert b.state_path().is_file(), "the once-a-turn state is .gov-runtime/session-watch/state.json"
    state = b.state()
    assert isinstance(state, dict) and check in state, f"state.json is keyed by check ({check}): {state}"


def test_s3_the_two_checks_share_one_state_file_and_each_keeps_its_own_bound(b):
    assert_blocks(b.run("waiter"), "(the waiter's first call of the turn)")
    assert_blocks(b.run("idle"), "(the idle check's first call: the waiter's block does not count for it)")
    assert_no_block(b.run("waiter"), "(the waiter, same turn)")
    assert_no_block(b.run("idle"), "(the idle check, same turn)")
    state = b.state()
    assert {"waiter", "idle"} <= set(state), f"one state file, keyed by check: {state}"


@pytest.mark.parametrize("check", CHECKS)
def test_s3_a_tool_result_does_not_start_a_new_turn(b, check):
    assert_blocks(b.run(check))
    b.tool_round()
    result = b.run(check)
    assert_no_block(result, "(a tool call and its result: the same turn)")


@pytest.mark.parametrize("check", CHECKS)
@pytest.mark.parametrize("keys", [{"isMeta": True, "wakeupSource": "scheduled"}, {"isMeta": True, "turnOrigin": "cron"}],
                         ids=["wakeupSource", "turnOrigin"])
def test_s3_a_scheduled_wakeup_entry_starts_a_new_turn(b, check, keys):
    assert_blocks(b.run(check))
    b.user("wake up and check the queue", **keys)
    result = b.run(check)
    assert_blocks(result, "(a user entry carrying wakeupSource or turnOrigin is a new turn)")


@pytest.mark.parametrize("check", CHECKS)
def test_s3_a_meta_user_entry_without_an_origin_does_not_start_a_new_turn(b, check):
    assert_blocks(b.run(check))
    b.user("system reminder text", isMeta=True)
    result = b.run(check)
    assert_no_block(result, "(an isMeta user entry with no turnOrigin or wakeupSource is not a turn)")


def test_s3_an_idle_reason_line_ends_the_turn_is_logged_and_does_not_carry_into_the_next_turn(b):
    why = "waiting for the nightly landing to finish before I start more"
    b.assistant(f"Nothing to start right now.\nIDLE-REASON: {why}")
    result = b.run("idle")
    assert_no_block(result, "(a line IDLE-REASON: <why> in the turn's messages)")
    assert why in result.message, f"the owner sees the stated reason in the systemMessage:\n{result}"
    assert why in result.log_text, f"the IDLE-REASON line's text is recorded in the log:\n{result}"
    assert any("\t" in line and "idle" in line.lower() for line in result.log_new), \
        f"one tab-separated log line with the check's name:\n{result}"
    again = b.run("idle")
    assert_no_block(again, "(the same turn, the reason still stands)")
    b.user("another request")
    b.assistant("Started the three open items.")
    nxt = b.run("idle")
    assert_blocks(nxt, "(a new turn without the line: the reason does not carry into it)")


def test_s3_an_idle_reason_in_an_earlier_turn_does_not_end_this_one(b):
    b.assistant("IDLE-REASON: earlier turn's reason")
    b.user("a new request")
    result = b.run("idle")
    assert_blocks(result, "(the reason line is before the turn's starting user entry)")


def test_s3_an_idle_reason_in_the_hook_inputs_last_assistant_message_ends_the_turn(b):
    why = "the owner has the floor on the scope question"
    result = b.run("idle", extra={"last_assistant_message": f"Done for now.\nIDLE-REASON: {why}"})
    assert_no_block(result, "(the line is in last_assistant_message)")
    assert why in result.log_text, f"the reason is recorded in the log:\n{result}"


def test_s3_an_idle_reason_line_is_found_among_the_turns_assistant_text_items(b):
    b.assistant("First message of the turn.")
    b.tool_round()
    b.assistant("Working.\nIDLE-REASON: the build farm is down")
    b.assistant("Closing words after the reason line.")
    result = b.run("idle")
    assert_no_block(result, "(the line is in an assistant text item of the turn, not the last one)")
    assert "the build farm is down" in result.log_text
