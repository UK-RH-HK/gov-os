"""S8: no watcher needs re-arming; every wake is an inbox item a pass writes.

The planted run across a restart: each ``tick`` is a fresh process (a restart of the host's job leaves only the state
folder behind); between the passes nothing of the dispatcher runs, so a finished session's return waits in its
``.exit`` file until the next pass writes the item. The host's cron entry and the real host restart are not tested
(part a's S1 and S8 leave them to the CTO's ACT).
"""

from __future__ import annotations

import time


def test_s8_every_wake_is_an_inbox_item_written_by_a_pass_and_nothing_else_wakes_the_caller(project):
    p = project
    first, second = p.add_ticket(901), p.add_ticket(902)
    p.set_output("task: planted\nstatus: DONE\n")
    p.ready(first, second)
    assert p.tick().code == 0
    p.wait_launches(1)
    p.wait_exit_file(first.log)
    time.sleep(1.5)
    assert p.all_items() == [], "an item appeared with no pass running: something watches"
    assert p.tick().code == 0  # a fresh process: the only thing that writes the wake
    (item,) = p.items()
    assert item.fields["log"] == first.log
    p.mark_read(item)  # the caller read the wake; nothing is re-armed for the next one
    p.wait_launches(2)
    p.wait_exit_file(second.log)
    time.sleep(1.5)
    assert [i.fields["log"] for i in p.all_items()] == [first.log], "the second return woke the caller with no pass"
    assert p.tick().code == 0
    assert sorted(i.fields["log"] for i in p.all_items()) == sorted([first.log, second.log])
    assert [i.fields["log"] for i in p.items()] == [second.log]


def test_s8_a_pass_leaves_no_process_of_its_own_running_after_it_exits(project):
    """After ``tick`` exits, the only process still running is the detached session the launch command made."""
    import os

    p = project
    entry = p.add_ticket(901)
    p.set_sleep(6)
    p.ready(entry)
    r = p.tick()
    assert r.code == 0, r
    (record,) = p.wait_launches(1)
    os.kill(record["pid"], 0)
    assert p.popens == [] or all(x.poll() is not None for x in p.popens)
    assert r.seconds < 20, "the pass stayed alive for the session it started"
    # a second pass over the same state, in a new process, sees the running session as the processes show it
    p.plant_lead(entry.ticket)
    assert p.tick().code == 0
    assert p.all_items() == []
