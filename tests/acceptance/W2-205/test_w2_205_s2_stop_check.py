"""W2-205, success line 2 (RT-2): the wake carrier at the end of a turn.

``gov msg stop-check`` reads the Stop hook's JSON on stdin and the address from ``$GOV_MSG_ADDRESS``: it prints the
hook decision ``{"decision": "block", "reason": <the unread wake messages' text>}`` and exits 0 to block, prints
nothing and exits 0 to pass. It blocks only for an unread ``wake`` message, once per message (the id recorded in
``~/.gov-os/inbox/<address>/stop-seen``). ``stop.py`` runs the check after writing its checkpoint, prints the check's
output and always exits 0.
"""

from __future__ import annotations

import w2_205_support as s

ME, TICKET = "lead:DAEO-s205", "DAEO-s205"
STOP = {"session_id": "0f1e2d3c-stop", "hook_event_name": "Stop", "stop_hook_active": False}


def test_s2_an_unread_wake_blocks_once_with_its_text_and_the_same_input_again_passes(box):
    sent = box.send(ME, "wake", "the zq205 build ended with exit code 3", "--from", "engineer:DAEO-s205")
    first = box.stop_check(ME)
    assert first is not None, "an unread wake message did not block the turn's end"
    assert "the zq205 build ended with exit code 3" in first["reason"], f"the reason is not the message text: {first}"
    assert sent["id"] in box.seen(ME), f"the blocked message's id is not in stop-seen: {box.seen(ME)!r}"
    assert box.stop_check(ME) is None, "the same message blocked a second time"
    assert box.stop_check(ME) is None, "the same message blocked a third time"


def test_s2_a_second_newer_wake_blocks_once_more(box):
    box.send(ME, "wake", "first: the worker ended")
    assert box.stop_check(ME) is not None, "an unread wake message did not block"
    assert box.stop_check(ME) is None
    box.send(ME, "wake", "second: the zq205 measure ended")
    again = box.stop_check(ME)
    assert again is not None, "a second, newer wake message did not block"
    assert "second: the zq205 measure ended" in again["reason"], f"the reason is not the new message's text: {again}"
    assert box.stop_check(ME) is None, "the second message blocked twice"


def test_s2_an_unread_notice_only_passes(box):
    for n in range(3):
        box.send(ME, "notice", f"structural notice {n}")
    assert box.stop_check(ME) is None, "a notice blocked the turn's end"
    assert len(box.ok("msg", "read", ME, "--peek")["messages"]) == 3, "the check consumed the unread notices"


def test_s2_nothing_unread_and_nothing_waited_on_passes_even_beside_a_launchable_ticket(box):
    root = s.project(box.base / "project", "DAEO-s2rd")  # a ticket that could be started: never a reason to block
    assert box.stop_check(ME, cwd=root) is None, "a session with an empty inbox and no wait armed was blocked"
    assert box.stop_check("lead:DAEO-none", cwd=root) is None, "a session whose inbox does not exist was blocked"


def test_s2_no_gov_msg_address_passes(box):
    for address in ("cto", "unknown", ME):
        box.send(address, "wake", "a wake message for someone")
    assert box.stop_check(None) is None, "a session with no GOV_MSG_ADDRESS was blocked"


def test_s2_a_wake_already_read_does_not_block(box):
    box.send(ME, "wake", "read before the turn ended")
    assert len(box.ok("msg", "read", ME)["messages"]) == 1
    assert box.stop_check(ME) is None, "a wake message already read (behind the mark) blocked"


def test_s2_the_stop_hook_prints_the_block_once_after_its_checkpoint_and_exits_0(box):
    root = s.project(box.base / "project", TICKET)

    def stop(address):
        done = s.run_hook(box, "stop.py", {**STOP, "cwd": str(root)}, root, ticket=TICKET, address=address)
        return s.decision(done.stdout)

    box.send(ME, "notice", "a notice only")
    assert stop(ME) is None, "stop.py blocked for a notice"
    box.send(ME, "wake", "the zq205 worker ended with exit code 0")
    assert stop(None) is None, "stop.py blocked a session with no GOV_MSG_ADDRESS"
    blocked = stop(ME)
    assert blocked is not None, "stop.py printed no block decision for an unread wake message"
    assert "the zq205 worker ended with exit code 0" in blocked["reason"], blocked
    assert s.checkpoint_files(root, TICKET), "stop.py wrote no checkpoint record"
    assert stop(ME) is None, "stop.py blocked twice for the same message"
