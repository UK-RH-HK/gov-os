"""S2: at most one session a pass, staggered, only an entry of the ready list, in the list's order; the launch itself.

Readings fixed by the brief (the lead's reading where the ticket is silent): the launch command is an argv list with the
placeholders ``{ticket}``, ``{w2}``, ``{brief}``, ``{log}``; the brief goes to its stdin, its output to
``<state>/logs/<log name>``, and ``<state>/logs/<log name>.exit`` holds its exit code once it ends; the log name is
appended to ``started.txt`` BEFORE the launch command is spawned; the launch is detached (its own session) and the pass
exits without waiting. A pass that skips entries for a reason that is not the gate's or the forecast's (the stagger,
``max_leads``) exits 0: exit 3 is the gate's and the forecast's (the ticket's Interface).
"""

from __future__ import annotations

import os
import re

import pytest

import w2_121_support as support
from w2_121_support import named_with, explain


def test_s2_one_session_starts_a_pass_the_first_eligible_in_the_lists_order(project):
    p = project
    entries = [p.add_ticket(n) for n in (903, 901, 902)]  # a list order that is no order of ids
    p.cfg(stagger_s=3600)
    p.ready(*entries)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    p.settle()
    assert p.launched_logs() == [entries[0].log], p.launched_logs()
    assert p.started() == [entries[0].log]


def test_s2_the_next_start_is_staggered(project):
    p = project
    first, second = p.add_ticket(901), p.add_ticket(902)
    p.cfg(stagger_s=3600)
    p.ready(first, second)
    assert p.tick().code == 0
    p.wait_launches(1)
    r = p.tick()
    assert r.code == 0, r
    p.settle()
    assert p.launched_logs() == [first.log], "a second session started inside the stagger"
    assert re.search(r"(?i)stagger", p.status_text() + str(p.status_json())), explain(p, r)


def test_s2_with_no_stagger_each_pass_starts_the_next_entry_in_order(project):
    p = project
    entries = [p.add_ticket(n) for n in (903, 901, 902)]
    p.ready(*entries)
    for count in (1, 2, 3):
        assert p.tick().code == 0
        p.wait_launches(count)
        p.settle(0.3)
        assert p.launched_logs() == [e.log for e in entries[:count]], p.launched_logs()
    assert p.tick().code == 0
    p.settle()
    assert len(p.launches()) == 3


def test_s2_the_launch_gets_the_brief_on_stdin_and_the_entrys_names_and_logs_its_output(project):
    p = project
    entry = p.add_ticket(901, brief="# Brief 901\nThe planted brief text.\n")
    p.set_output("hello from the stub session")
    p.ready(entry)
    assert p.tick().code == 0
    (record,) = p.wait_launches(1)
    assert record["stdin"] == "# Brief 901\nThe planted brief text.\n", record
    argv = record["argv"]
    assert argv[0] == entry.ticket and argv[1] == entry.w2 and argv[3] == entry.log, argv
    assert argv[2].endswith(entry.brief), argv
    assert p.wait_exit_file(entry.log) == "0"
    assert "hello from the stub session" in (p.state / "logs" / entry.log).read_text(encoding="utf-8")


def test_s2_the_exit_code_of_a_session_is_kept_beside_its_log(project):
    p = project
    entry = p.add_ticket(901)
    p.set_exit(7)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.wait_exit_file(entry.log) == "7"


def test_s2_the_log_name_is_in_started_txt_before_the_launch_command_runs(project):
    p = project
    entry = p.add_ticket(901)
    p.ready(entry)
    assert p.tick().code == 0
    (record,) = p.wait_launches(1)
    assert entry.log in record["started_txt"], f"started.txt when the launch command ran: {record['started_txt']!r}"


def test_s2_the_launch_is_detached_and_the_pass_does_not_wait_for_it(project):
    p = project
    entry = p.add_ticket(901)
    p.set_sleep(25)
    p.ready(entry)
    r = p.tick()
    assert r.code == 0, r
    (record,) = p.wait_launches(1)
    assert r.seconds < 20, f"the pass waited for the session ({r.seconds:.1f}s)\n{r}"
    os.kill(record["pid"], 0)  # still running: the pass did not stop it
    assert os.getsid(record["pid"]) != os.getsid(0), "the launch is not in a session of its own"


def test_s2_a_log_name_is_never_started_twice(project):
    p = project
    first, second = p.add_ticket(901), p.add_ticket(902)
    dup = f"{second.w2} {second.ticket} {second.brief} {first.log}"  # one log name on two lines
    p.ready(first, dup)
    for _ in range(3):
        assert p.tick().code == 0
        p.settle(0.3)
    assert p.launched_logs() == [first.log], p.launched_logs()
    assert p.started().count(first.log) == 1


def test_s2_an_entry_not_on_the_list_is_never_started(project):
    p = project
    listed, other, third = p.add_ticket(901), p.add_ticket(902), p.add_ticket(903)
    p.ready(listed)
    for _ in range(3):
        assert p.tick().code == 0
        p.settle(0.3)
    assert p.launched_logs() == [listed.log]
    assert other.log not in p.started() and third.log not in p.started()


def test_s2_comments_and_blank_lines_are_ignored_and_are_not_malformed(project):
    p = project
    entry = p.add_ticket(901)
    p.ready("# a comment line", "", "   ", "  # an indented comment W2-999 DAEO-zzzz b.md L.json", entry)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]
    assert "malformed" not in (p.status_text() + str(p.status_json())).lower(), explain(p, r)


def test_s2_no_ready_list_starts_nothing_and_is_not_an_error(project):
    p = project
    p.add_ticket(901)
    r = p.tick()
    assert r.code == 0, r
    assert (p.state / "status.json").is_file()
    p.settle(0.3)
    assert p.launches() == []


def test_s2_a_malformed_line_is_named_and_the_other_lines_are_still_read(project):
    p = project
    good = p.add_ticket(901)
    p.ready("W2-903 DAEO-bad3 briefX.md", "justoneword", good)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [good.log]
    for ident in ("DAEO-bad3", "justoneword"):
        assert named_with(p, ident, r"malformed"), f"{ident} is not named malformed" + explain(p, r)


def test_s2_the_claim_must_be_committed_on_the_integration_branch(project):
    p = project
    bad, good = p.add_ticket(901, claim="worktree_only"), p.add_ticket(902)
    p.ready(bad, good)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [good.log]
    assert named_with(p, bad.log, r"claim"), explain(p, r)


def test_s2_the_claim_must_be_committed_at_the_worktrees_head(project):
    p = project
    bad, good = p.add_ticket(901, claim="integration_only"), p.add_ticket(902)
    p.ready(bad, good)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [good.log]
    assert named_with(p, bad.log, r"claim"), explain(p, r)


def test_s2_a_ticket_not_claimed_anywhere_is_skipped_with_its_reason(project):
    p = project
    bad, good = p.add_ticket(901, claim="none"), p.add_ticket(902)
    p.ready(bad, good)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [good.log]
    assert named_with(p, bad.log, r"claim"), explain(p, r)


def test_s2_a_worktree_with_a_tracked_change_is_not_clean(project):
    p = project
    bad, good = p.add_ticket(901, dirty=True), p.add_ticket(902)
    p.ready(bad, good)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [good.log]
    assert named_with(p, bad.log, r"clean|dirty|modif|tracked|uncommitted|change"), explain(p, r)


def test_s2_an_untracked_file_does_not_make_the_worktree_unclean(project):
    p = project
    entry = p.add_ticket(901, untracked=True)
    p.ready(entry)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


BRIEFS = {"missing": None, "empty": "", "blank": "  \n\n", "at-at": "Do the work\n@@ fill in later\n",
          "slot": "Brief for {TICKET_ID} here\n", "slot-digits": "Run {STEP_2} now\n"}


@pytest.mark.parametrize("kind", sorted(BRIEFS))
def test_s2_an_incomplete_brief_is_skipped_and_named(project, kind):
    p = project
    bad, good = p.add_ticket(901, brief=BRIEFS[kind]), p.add_ticket(902)
    p.ready(bad, good)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [good.log], f"a {kind} brief was started"
    assert named_with(p, bad.log, r"brief|slot|@@|empty|missing"), explain(p, r)


def test_s2_braces_that_are_not_an_unfilled_slot_do_not_make_a_brief_incomplete(project):
    p = project
    text = 'Use {lower_case} and {Mixed} and {"a": 1} and { } and {1X}.\nDone.\n'
    entry = p.add_ticket(901, brief=text)
    p.ready(entry)
    assert p.tick().code == 0
    (record,) = p.wait_launches(1)
    assert record["stdin"] == text


def test_s2_a_relative_brief_resolves_against_briefs_dir(project):
    p = project
    folder = p.tmp / "my-briefs"
    p.cfg(briefs_dir=str(folder))
    entry = p.add_ticket(901, brief=None)
    p.write_brief(entry.brief, "From the configured briefs folder.\n", folder)
    p.ready(entry)
    assert p.tick().code == 0
    (record,) = p.wait_launches(1)
    assert record["stdin"] == "From the configured briefs folder.\n"


def test_s2_an_absolute_brief_path_is_used_as_is(project):
    p = project
    entry = p.add_ticket(901, brief=None)
    path = p.write_brief("elsewhere.md", "An absolute brief.\n", p.tmp / "elsewhere")
    p.ready(f"{entry.w2} {entry.ticket} {path} {entry.log}")
    assert p.tick().code == 0
    (record,) = p.wait_launches(1)
    assert record["stdin"] == "An absolute brief.\n"


def test_s2_the_worktree_is_found_under_a_worktrees_root_relative_to_the_project(project):
    p = project
    p.wt_root = p.tmp / "wts"
    p.wt_root.mkdir()
    p.cfg(worktrees_root="../wts")
    entry = p.add_ticket(901)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


def test_s2_a_running_ticket_is_skipped_and_named(project):
    p = project
    bad, good = p.add_ticket(901), p.add_ticket(902)
    p.plant_lead(bad.ticket)
    p.ready(bad, good)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [good.log]
    assert named_with(p, bad.log, r"running|already|live|process"), explain(p, r)


def test_s2_a_process_that_only_mentions_the_ticket_is_not_a_running_ticket(project):
    p = project
    entry = p.add_ticket(901)
    p.plant_process(["tail", "-f", f"{entry.ticket}.log"])
    p.plant_lead(entry.ticket, role="engineer")  # a worker's settings: GOV_ROLE is not orchestrator
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


def test_s2_an_unread_return_holds_its_entry_and_is_named(project):
    p = project
    bad, good = p.add_ticket(901), p.add_ticket(902)
    p.plant_item("0001-return.txt", "W2-901-A5-earlier.json", bad.w2)
    p.ready(bad, good)
    r = p.tick()
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [good.log]
    assert named_with(p, bad.log, r"unread|return|inbox"), explain(p, r)


def test_s2_a_return_that_was_read_no_longer_holds_its_entry(project):
    p = project
    entry = p.add_ticket(901)
    p.plant_item("0001-return.txt", "W2-901-A5-earlier.json", entry.w2, read=True)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


def test_s2_another_tickets_unread_return_does_not_hold_the_entry(project):
    p = project
    entry = p.add_ticket(901)
    p.plant_item("0001-return.txt", "W2-950-A5-other.json", "W2-950")
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


def test_s2_a_shut_gate_starts_nothing_names_every_entry_and_exits_3(project):
    p = project
    entries = [p.add_ticket(901), p.add_ticket(902)]
    p.set_machine(mem_gib=1.5)  # the floor 1 GiB + one working size 1 GiB are not available: W2-20's memory condition
    assert p.gate_reading()["open"] is False
    p.ready(*entries)
    r = p.tick()
    assert r.code == 3, r
    p.settle()
    assert p.launches() == []
    for entry in entries:
        assert named_with(p, entry.log, r"gate|shut"), f"{entry.log} not named with the gate" + explain(p, r)  # review F-5: the gate, not a memory figure
    assert any(k == "open" and v is False for k, v in support.walk(p.status_json())), "the status does not show a shut gate"


def test_s2_a_full_disk_starts_nothing_names_every_entry_and_exits_3(project):
    p = project
    entries = [p.add_ticket(901), p.add_ticket(902)]
    p.set_machine(disk_free_gib=1)
    assert p.gate_reading()["open"] is False
    p.ready(*entries)
    r = p.tick()
    assert r.code == 3, r
    p.settle()
    assert p.launches() == []
    for entry in entries:
        assert named_with(p, entry.log, r"disk"), f"{entry.log} not named with the disk" + explain(p, r)


def test_s2_max_leads_counts_the_running_sessions_from_the_processes(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(max_leads=2)
    p.plant_lead("DAEO-r001")
    p.plant_lead("DAEO-r002")
    p.ready(entry)
    r = p.tick()
    assert r.code == 0, r
    p.settle()
    assert p.launches() == [], "a session started with max_leads running"
    assert re.search(r"(?i)max[_ ]?leads|leads", p.status_text() + str(p.status_json())), explain(p, r)


def test_s2_below_max_leads_the_entry_starts(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(max_leads=3)
    p.plant_lead("DAEO-r001")
    p.plant_lead("DAEO-r002")
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


def test_s2_a_start_with_no_process_yet_counts_toward_max_leads(project):
    p = project
    first, second = p.add_ticket(901), p.add_ticket(902)
    p.cfg(max_leads=1)
    p.set_sleep(10)  # the first session is still launching: no marker process, no .exit file
    p.ready(first, second)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.tick().code == 0
    p.settle()
    assert p.launched_logs() == [first.log], "a second session started beside a start that has no process yet"
