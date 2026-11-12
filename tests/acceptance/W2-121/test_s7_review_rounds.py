"""S7: the dispatcher never starts a third review round for a ticket; such a ticket goes to the inbox as an owner item.

Readings fixed by the brief (the lead's reading): a review launch is an entry whose brief holds a line ``run: review``;
its review rounds are counted from the probe records in ``<worktree>/<probes_dir>/<ticket id>/*.md`` (``probes_dir``
default ``docs/probes``); two or more records refuse the launch; the refusal is one item in the inbox, ``status:
owner``, written once. A brief without that line is not a review launch.
"""

from __future__ import annotations

import w2_121_support as support
from w2_121_support import explain, named_with

REVIEW = "# Review brief\n\nrun: review\n\nReview the ticket's work and return the twelve fields.\n"


def test_s7_a_ticket_with_two_probe_records_is_not_started_and_is_one_owner_item(project):
    p = project
    bad, good = p.add_ticket(901, brief=REVIEW), p.add_ticket(902)
    p.probes(bad, 2)
    p.ready(bad, good)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [good.log], "a third review round was started"
    owner = [i for i in p.all_items() if i.fields.get("status") == "owner"]
    assert len(owner) == 1, [i.text for i in p.all_items()]
    assert owner[0].fields.get("W2") == bad.w2 and owner[0].fields.get("log") == bad.log, owner[0].text
    assert owner[0].path.parent == p.state / "inbox", "the owner item is not unread in the inbox"


def test_s7_the_owner_item_is_written_once(project):
    p = project
    bad = p.add_ticket(901, brief=REVIEW)
    p.probes(bad, 3)
    p.ready(bad)
    for round_ in range(3):
        r = p.tick()
        assert r.code == 0, r
        if round_ == 0:
            (item,) = p.items()
            p.mark_read(item)  # the owner read it: the ticket still never starts, and no new item follows
    p.settle(0.5)
    assert p.launches() == []
    owner = [i for i in p.all_items() if i.fields.get("status") == "owner"]
    assert len(owner) == 1, [i.text for i in p.all_items()]


def test_s7_a_ticket_with_one_probe_record_is_started(project):
    p = project
    entry = p.add_ticket(901, brief=REVIEW)
    p.probes(entry, 1)
    p.ready(entry)
    assert p.tick().code == 0
    (record,) = p.wait_launches(1)
    assert record["stdin"] == REVIEW
    assert p.all_items() == []


def test_s7_a_ticket_with_no_probe_record_is_started(project):
    p = project
    entry = p.add_ticket(901, brief=REVIEW)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


def test_s7_a_brief_that_is_not_a_review_launch_is_started_whatever_the_records(project):
    p = project
    entry = p.add_ticket(901)
    p.probes(entry, 3)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]
    assert p.all_items() == []


def test_s7_only_the_markdown_records_of_the_tickets_own_folder_are_counted(project):
    p = project
    entry, other = p.add_ticket(901, brief=REVIEW), p.add_ticket(902, brief=REVIEW)
    p.probes(entry, 1)
    p.probes(entry, 1, suffix=".txt")  # a second file, but not a record
    p.commit(entry, f"docs/probes/{entry.ticket}/notes.json", "{}\n")
    p.probes(other, 3)  # another ticket's records
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]
    assert p.all_items() == []


def test_s7_the_probes_folder_is_the_configured_one(project):
    p = project
    p.cfg(probes_dir="records/probes")
    entry = p.add_ticket(901, brief=REVIEW)
    p.probes(entry, 2, folder="records/probes")
    p.ready(entry)
    r = p.tick()
    assert r.code == 0, r
    p.settle()
    assert p.launches() == []
    assert [i.fields.get("status") for i in p.items()] == ["owner"]


def test_s7_the_refusal_is_named_in_the_status(project):
    p = project
    bad = p.add_ticket(901, brief=REVIEW)
    p.probes(bad, 2)
    p.ready(bad)
    r = p.tick()
    assert r.code == 0, r
    assert named_with(p, bad.log, r"review|probe|round|owner"), explain(p, r)
