"""S4: every finished session's return becomes one inbox item, once; a start that never ran becomes one item; an item
unread past a configured time raises one escalation the notifier pushes.

Readings fixed by the brief: a session is finished when ``<state>/logs/<log name>.exit`` exists (the dispatcher's own
detached wrapper writes it); an item is a text file in ``<state>/inbox/`` whose first lines are ``log: <log name>``,
``W2: <W2>``, ``status: <status>``; ``status:`` is the return's own ``status:`` line where the log holds one, else
``exit <code>``; unread while in ``inbox/``, read once moved to ``inbox/read/``; a start that never ran is one in
``started.txt`` past ``never_ran_after_s`` with no marker process and no ``.exit`` file, listed in ``never-ran.txt``;
the notifier command (an argv list) gets the item's path appended as its last argument.

The sessions are the stub of ``w2_121_support`` (it exits at once, or sleeps); the returns are text the stub prints.
"""

from __future__ import annotations

import time

import w2_121_support as support
from w2_121_support import wait_for, explain


def finished(p, entry, output=None, exit_code=0):
    """Start the entry's session (a stub that prints ``output`` and exits) and wait until its ``.exit`` file exists."""
    if output is not None:
        p.set_output(output)
    p.set_exit(exit_code)
    before = len(p.launches())
    p.ready(entry)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(before + 1)
    return p.wait_exit_file(entry.log)


def test_s4_a_finished_session_becomes_one_inbox_item_and_no_more_on_the_next_pass(project):
    p = project
    entry = p.add_ticket(901)
    finished(p, entry, "task: planted\nstatus: DONE\n")
    assert p.items() == [], "an item before any pass saw the finished session"
    r = p.tick()
    assert r.code == 0, r
    (item,) = p.items()
    assert item.lines[0].startswith("log:") and item.fields["log"] == entry.log, item.text
    assert item.lines[1].startswith("W2:") and item.fields["W2"] == entry.w2, item.text
    assert item.lines[2].startswith("status:"), item.text
    for _ in range(2):
        assert p.tick().code == 0
    assert len(p.all_items()) == 1, [i.text for i in p.all_items()]


def test_s4_the_items_status_is_the_returns_own_status_line(project):
    p = project
    entry = p.add_ticket(901)
    finished(p, entry, "task: planted\nstatus: PACKAGES\nwork_completed: none\n")
    assert p.tick().code == 0
    (item,) = p.items()
    assert item.fields["status"] == "PACKAGES", item.text


def test_s4_without_a_status_line_the_items_status_is_the_exit_code(project):
    p = project
    entry = p.add_ticket(901)
    finished(p, entry, "the session printed no return at all", exit_code=7)
    assert p.tick().code == 0
    (item,) = p.items()
    assert item.fields["status"] == "exit 7", item.text


def test_s4_no_item_while_the_session_still_runs(project):
    p = project
    entry = p.add_ticket(901)
    p.set_sleep(8)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    for _ in range(2):
        assert p.tick().code == 0
    assert p.all_items() == []
    assert not (p.state / "never-ran.txt").exists() or entry.log not in (p.state / "never-ran.txt").read_text()


def test_s4_every_finished_session_is_its_own_item(project):
    p = project
    first, second = p.add_ticket(901), p.add_ticket(902)
    finished(p, first, "status: DONE\n")
    p.ready(first, second)
    assert p.tick().code == 0  # this pass writes the first item and starts the second entry (another W2: not held)
    (item,) = p.items()
    p.mark_read(item)
    p.wait_launches(2)
    p.wait_exit_file(second.log)
    assert p.tick().code == 0
    assert sorted(i.fields["log"] for i in p.all_items()) == sorted([first.log, second.log])


def test_s4_an_item_that_was_read_is_not_written_again(project):
    p = project
    entry = p.add_ticket(901)
    finished(p, entry, "status: DONE\n")
    assert p.tick().code == 0
    (item,) = p.items()
    p.mark_read(item)
    for _ in range(2):
        assert p.tick().code == 0
    assert p.items() == [] and len(p.items(read=True)) == 1


def test_s4_a_start_that_never_ran_is_one_inbox_item_once(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(never_ran_after_s=1)
    p.set_sleep(20)  # the session never shows as a marker process in the planted /proc, and never ends
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)

    def raised():
        assert p.tick().code == 0
        return p.items()

    items = wait_for(raised, 15, 0.4, "an inbox item for the start that never ran")
    (item,) = items
    assert item.fields["log"] == entry.log and item.fields["W2"] == entry.w2, item.text
    assert "never" in item.text.lower(), f"the item does not say the start never ran:\n{item.text}"
    assert entry.log in (p.state / "never-ran.txt").read_text(encoding="utf-8")
    for _ in range(2):
        assert p.tick().code == 0
    assert len(p.all_items()) == 1, [i.text for i in p.all_items()]


def test_s4_a_start_with_a_marker_process_has_run_and_raises_no_never_ran_item(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(never_ran_after_s=1)
    p.set_sleep(20)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    p.plant_lead(entry.ticket)  # the session is there: its marker is on a process
    time.sleep(1.6)
    for _ in range(2):
        assert p.tick().code == 0
    assert p.all_items() == []


def test_s4_an_item_unread_past_the_configured_time_runs_the_notifier_once(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(unread_escalate_s=1)
    finished(p, entry, "status: DONE\n")
    assert p.tick().code == 0
    (item,) = p.items()
    wait_for(lambda: p.tick().code == 0 and p.notifies(), 15, 0.4, "the notifier to run for the unread item")
    for _ in range(2):
        assert p.tick().code == 0
    calls = p.notifies()
    assert len(calls) == 1, f"the notifier ran {len(calls)} times for one item: {calls}"
    from pathlib import Path

    assert Path(calls[0]["argv"][-1]).resolve() == item.path.resolve(), calls[0]
    assert item.path.exists(), "the escalation moved or removed the item"


def test_s4_an_item_unread_for_less_than_the_configured_time_raises_no_escalation(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(unread_escalate_s=3600)
    finished(p, entry, "status: DONE\n")
    for _ in range(3):
        assert p.tick().code == 0
    time.sleep(1.2)
    assert p.tick().code == 0
    assert len(p.items()) == 1 and p.notifies() == []


def test_s4_an_item_that_was_read_raises_no_escalation(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(unread_escalate_s=1)
    finished(p, entry, "status: DONE\n")
    assert p.tick().code == 0
    (item,) = p.items()
    p.mark_read(item)
    time.sleep(1.6)
    for _ in range(2):
        assert p.tick().code == 0
    assert p.notifies() == []
