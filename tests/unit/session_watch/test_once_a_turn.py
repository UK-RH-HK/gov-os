"""S3 and S4: at most one block a turn, the IDLE-REASON line, and an error that is named, never silent or a trap."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from .conftest import HOUR, WAITER_CONFIG


@pytest.mark.parametrize("check", ["waiter", "idle"])
def test_a_check_blocks_once_a_turn_and_again_in_a_new_turn(hook, check):
    hook.config(WAITER_CONFIG)
    hook.plan(hook.ready_of("T-1"))
    assert hook.run(check)["decision"] == "block"
    assert hook.run(check, active=True) is None
    assert hook.run(check) is None  # a third call, the same turn
    hook.new_turn()
    assert hook.run(check)["decision"] == "block"


@pytest.mark.parametrize("check", ["waiter", "idle"])
def test_stop_hook_active_alone_never_blocks(hook, check):
    hook.config(WAITER_CONFIG)
    hook.plan(hook.ready_of("T-1"))
    assert hook.run(check, active=True) is None


def test_the_state_is_shared_and_keyed_by_check(hook):
    hook.config(WAITER_CONFIG)
    hook.plan(hook.ready_of("T-1"))
    assert hook.run("waiter")["decision"] == "block"
    assert hook.run("idle")["decision"] == "block"  # the idle check's own bound is not the waiter's
    state = json.loads((hook.folder / "state.json").read_text())
    assert set(state) == {"waiter", "idle"} and state["idle"]["session"] == hook.sid


def test_tool_results_and_meta_entries_do_not_start_a_turn_but_a_wakeup_does(hook):
    hook.plan(hook.ready_of("T-1"))
    assert hook.run("idle")["decision"] == "block"
    hook.entries.append({"type": "user", "uuid": "r1", "message": {"content": [{"type": "tool_result", "content": "x"}]}})
    hook.entries.append({"type": "user", "uuid": "m1", "isMeta": True, "message": {"content": "meta"}})
    hook.write_transcript()
    assert hook.run("idle") is None  # still the same turn
    hook.new_turn(wakeupSource="timer", isMeta=True)
    assert hook.run("idle")["decision"] == "block"


def test_an_idle_reason_ends_the_turn_and_is_logged_and_does_not_carry_over(hook):
    hook.plan(hook.ready_of("T-1"))
    hook.say("thinking\nIDLE-REASON: waiting for the owner's answer on T-1\nmore")
    out = hook.run("idle")
    assert "decision" not in out and "waiting for the owner's answer on T-1" in out["systemMessage"]
    assert "IDLE-REASON: waiting for the owner's answer on T-1" in hook.log()
    hook.new_turn()
    assert hook.run("idle")["decision"] == "block"  # the reason belonged to the turn before


def test_an_idle_reason_in_the_hooks_last_message_counts(hook):
    hook.plan(hook.ready_of("T-1"))
    out = hook.run("idle", extra={"last_assistant_message": "IDLE-REASON: nothing can move"})
    assert "decision" not in out and "nothing can move" in out["systemMessage"]


# -- S4 -----------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("check", ["waiter", "idle"])
@pytest.mark.parametrize("content", ["{not json", "[1, 2]", ""])
def test_an_unreadable_state_file_ends_the_turn_names_the_error_and_logs_it(hook, check, content):
    hook.config(WAITER_CONFIG)
    hook.plan(hook.ready_of("T-1"))
    (hook.folder / "state.json").write_text(content)
    out = hook.run(check)
    assert "decision" not in out and "state.json" in out["systemMessage"]
    line = hook.log().splitlines()[-1].split("\t")
    assert check in line and "error" in line and "state.json" in hook.log()


def test_a_standby_note_does_not_let_the_idle_check_end_idle(hook):
    hook.plan(hook.ready_of("T-1"))
    hook.standby(60)
    assert hook.run("idle")["decision"] == "block"


@pytest.mark.parametrize("check", ["waiter", "idle"])
def test_any_failure_is_a_system_message_never_a_traceback(hook, check):
    hook.config("session_watch: [not, a, mapping]\n")
    out = hook.run(check)
    assert "decision" not in out and "session-watch.yaml" in out["systemMessage"]
    assert "error" in hook.log()


def test_input_that_is_not_json_is_named(hook):
    out = hook.run("idle", stdin="not json")
    assert "decision" not in out and "systemMessage" in out


def test_a_log_that_cannot_be_written_is_named_too(hook):
    hook.plan(hook.ready_of("T-1"))
    (hook.folder / "stop-check.log").mkdir()
    out = hook.run("idle")
    assert "decision" not in out and "log" in out["systemMessage"]


# -- S5 / F3 ------------------------------------------------------------------------------------------------------

def test_the_package_names_nothing_of_this_repository():
    folder = Path(__file__).resolve().parents[3] / "src" / "gov" / "session_watch"
    bad = re.compile(r"cto-|DECIDED-NOT-DONE|inbox_wait|/home/|\bW2-\d|\bDAEO-|orchestrator/tools|stop_idle|stop_waiter")
    found = [f"{f.name}:{n}: {line.strip()}" for f in folder.glob("*.py")
             for n, line in enumerate(f.read_text().splitlines(), 1) if bad.search(line)]
    assert folder.is_dir() and found == []
