"""F1 (the start half): a session started for an entry not on the ready list, not ready, already running, or without room
for its peak; a return never put in the inbox; a lead count not from the processes. The landing half (a ticket landed
that was not approved, or twice) is part b's.

Each case is a pass over a planted list in which every entry is one of the named wrong starts: no session starts.
"""

from __future__ import annotations

import w2_121_support as support
from w2_121_support import GIB, explain, hist


def test_f1_no_session_starts_for_an_off_list_not_ready_or_running_entry(project):
    p = project
    off_list = p.add_ticket(901)
    unclean = p.add_ticket(902, dirty=True)
    no_claim = p.add_ticket(903, claim="worktree_only")
    no_brief = p.add_ticket(904, brief="Fill in {SOMETHING} first\n")
    running = p.add_ticket(905)
    unread = p.add_ticket(906)
    p.plant_lead(running.ticket)
    p.plant_item("0001.txt", "W2-906-A5-earlier.json", unread.w2)
    p.ready(unclean, no_claim, no_brief, running, unread)  # off_list is not on it
    for _ in range(2):
        r = p.tick()
        assert r.code == 0, r
    p.settle(1.0)
    assert p.launches() == [], f"a session started: {p.launched_logs()} (off-list entry {off_list.log})\n{explain(p, r)}"
    assert p.started() == []


def test_f1_no_session_starts_without_room_for_its_peak(project):
    p = project
    entries = [p.add_ticket(901), p.add_ticket(902)]
    p.history([hist("lead", 1.0, 9)])
    p.set_machine(mem_gib=6.0)
    p.ready(*entries)
    r = p.tick()
    assert r.code == 3, r
    p.settle()
    assert p.launches() == [] and p.started() == [], r


def test_f1_a_session_the_lead_count_ignores_in_the_logs_does_not_hold_a_start(project):
    """The lead count is the processes': planted worker and non-session processes are not counted against ``max_leads``."""
    p = project
    entry = p.add_ticket(901)
    p.cfg(max_leads=1)
    p.plant_lead("DAEO-r001", role="engineer")
    p.plant_process(["tail", "-f", "DAEO-r002.log"])
    p.plant_process(["python3", "-c", "print('GOV_ROLE orchestrator GOV_TICKET DAEO-r003')"])
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


def test_f1_the_lead_count_is_the_processes_and_nothing_else_holds_a_start(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(max_leads=1)
    pid = p.plant_lead("DAEO-r001")
    p.ready(entry)
    assert p.tick().code == 0
    p.settle()
    assert p.launches() == [], "a lead process was not counted"
    p.remove_process(pid)  # the process ends: the count follows it at once, with nothing else to clear
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


def test_f1_every_finished_session_is_in_the_inbox(project):
    p = project
    entries = [p.add_ticket(n) for n in (901, 902, 903)]
    p.ready(*entries)
    for count in (1, 2, 3):
        assert p.tick().code == 0
        p.wait_launches(count)
        p.wait_exit_file(entries[count - 1].log)
    assert p.tick().code == 0
    assert sorted(i.fields["log"] for i in p.all_items()) == sorted(e.log for e in entries)
