"""S4 (and S7), review round 1 finding F-1: an inbox item, once written, is never written again.

Reading fixed by the fix round: an item (a finished session's return, a start that never ran, an S7 owner item), once
written, is never written again, as unread or at all, even after the operator deletes it from ``inbox/`` (a handled
item removed) or from ``inbox/read/`` (a tidy-up of the read folder). The record that it was written lives outside
``inbox/`` and outlives the item. An item already in ``inbox/`` or ``inbox/read/`` also counts as written (a state
folder from before the record), by the name the dispatcher gives it, ``<log name>.return.txt``. Deleting an item never
raises its escalation again either. The tests check behaviour only: what is in ``inbox/`` and ``inbox/read/`` and what
the notifier was run for, never the bookkeeping file's name.
"""

from __future__ import annotations

import time

import w2_121_support as support
from w2_121_support import explain, wait_for
from test_s7_review_rounds import REVIEW


def passes(p, count: int = 3) -> None:
    for _ in range(count):
        r = p.tick()
        assert r.code == 0, r


def test_s4_a_return_item_read_and_then_deleted_is_not_written_again(project):
    p = project
    entry = p.add_ticket(901)
    item = p.returned_item(entry)
    p.mark_read(item)
    (read,) = p.items(read=True)
    p.delete_item(read)
    passes(p)
    assert p.all_items() == [], f"the deleted item was written again: {[(str(i.path), i.text) for i in p.all_items()]}"


def test_s4_a_return_item_deleted_straight_from_the_inbox_is_not_written_again(project):
    p = project
    entry = p.add_ticket(901)
    item = p.returned_item(entry)
    p.delete_item(item)
    passes(p)
    assert p.all_items() == [], f"the deleted item was written again: {[(str(i.path), i.text) for i in p.all_items()]}"


def test_s4_a_deleted_return_item_no_longer_holds_its_entry_and_the_entry_is_not_started_again(project):
    p = project
    entry = p.add_ticket(901)
    item = p.returned_item(entry)
    p.delete_item(item)
    passes(p)
    p.settle()
    assert p.launched_logs() == [entry.log], f"the log was started again: {p.launched_logs()}"
    assert p.all_items() == []


def test_s4_an_item_already_in_the_read_folder_counts_as_written(project):
    p = project
    entry = p.add_ticket(901)
    p.finish_session(entry)
    p.plant_item(f"{entry.log}.return.txt", entry.log, entry.w2, status="DONE", read=True)  # a state from before the record
    passes(p)
    assert p.items() == [], f"an item was written again beside the one in inbox/read/: {[i.text for i in p.items()]}"
    assert len(p.items(read=True)) == 1


def test_s4_an_item_already_in_the_inbox_counts_as_written_even_after_it_is_deleted(project):
    p = project
    entry = p.add_ticket(901)
    p.finish_session(entry)
    planted = p.plant_item(f"{entry.log}.return.txt", entry.log, entry.w2, status="DONE")
    passes(p, 2)
    assert [i.path for i in p.items()] == [planted], [i.text for i in p.items()]
    planted.unlink()
    passes(p, 2)
    assert p.all_items() == []


def test_s4_a_never_ran_item_deleted_is_not_written_again(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(never_ran_after_s=1)
    p.set_sleep(40)  # no marker process ever shows in the planted /proc, and no .exit file for the next 40 s
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)

    def raised():
        assert p.tick().code == 0
        return p.items()

    (item,) = wait_for(raised, 15, 0.4, "an inbox item for the start that never ran")
    assert "never" in item.text.lower(), item.text
    p.delete_item(item)
    passes(p)
    assert p.all_items() == [], f"the deleted never-ran item was written again: {[i.text for i in p.all_items()]}"
    assert p.launched_logs() == [entry.log]


def test_s4_a_never_ran_item_read_and_deleted_is_not_written_again(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(never_ran_after_s=1)
    p.set_sleep(40)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)

    def raised():
        assert p.tick().code == 0
        return p.items()

    (item,) = wait_for(raised, 15, 0.4, "an inbox item for the start that never ran")
    p.mark_read(item)
    passes(p, 1)
    (read,) = p.items(read=True)
    p.delete_item(read)
    passes(p)
    assert p.all_items() == [], f"the deleted never-ran item was written again: {[i.text for i in p.all_items()]}"


def test_s7_an_owner_item_deleted_is_not_written_again(project):
    p = project
    bad = p.add_ticket(901, brief=REVIEW)
    p.probes(bad, 3)
    p.ready(bad)
    assert p.tick().code == 0
    (item,) = p.items()
    assert item.fields.get("status") == "owner", item.text
    p.delete_item(item)
    passes(p)
    p.settle(0.5)
    assert p.launches() == []
    assert p.all_items() == [], f"the deleted owner item was written again: {[i.text for i in p.all_items()]}"


def test_s7_an_owner_item_read_and_deleted_is_not_written_again(project):
    p = project
    bad = p.add_ticket(901, brief=REVIEW)
    p.probes(bad, 2)
    p.ready(bad)
    assert p.tick().code == 0
    (item,) = p.items()
    p.mark_read(item)
    (read,) = p.items(read=True)
    p.delete_item(read)
    passes(p)
    assert p.all_items() == [], f"the deleted owner item was written again: {[i.text for i in p.all_items()]}"


def test_s4_a_deleted_item_raises_no_escalation(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(unread_escalate_s=1)
    item = p.returned_item(entry)
    p.delete_item(item)  # handled and removed before it was escalated
    time.sleep(1.6)  # past the unread time of the item that was
    passes(p)
    assert p.all_items() == [], [i.text for i in p.all_items()]
    assert p.notifies() == [], f"the notifier ran for a deleted item: {p.notifies()}"


def test_s4_deleting_an_escalated_item_never_raises_its_escalation_again(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(unread_escalate_s=1)
    item = p.returned_item(entry)
    wait_for(lambda: p.tick().code == 0 and p.notifies(), 15, 0.4, "the notifier to run for the unread item")
    assert len(p.notifies()) == 1
    p.delete_item(item)
    time.sleep(1.6)
    passes(p)
    assert len(p.notifies()) == 1, f"the notifier ran again after the item was deleted: {p.notifies()}"
    assert p.all_items() == [], explain(p)
