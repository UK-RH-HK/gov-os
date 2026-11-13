"""S4, review round 1 finding F-2: an escalation is recorded as raised only when it was sent.

Readings fixed by the fix round: an item unread past ``unread_escalate_s`` runs ``notifier_command`` (the item's path its
last argument). The escalation counts as raised (never run again for that item) only when the notifier exits 0. A
notifier that exits non-zero, times out (``command_timeout_s``) or cannot be started leaves the escalation due: it is
tried again on a later pass, no sooner than ``notify_retry_s`` seconds (a number >= 0; default 600; malformed: exit 2
naming the key) after its last attempt (0: every pass). While an escalation is due after a failed attempt, every pass's
status (``problems`` in ``status.json``, the ``problems:`` block of ``status.txt``) names the item and the last failure,
also on a pass that does not retry it; the line goes once the escalation is sent or the item is read, and a read item is
never retried. A notifier timeout in a pass ends that pass's escalations: the ones still due in that pass are not run,
not recorded as raised, and named in the status as not sent. A failed notifier never fails the pass: exit 0 and ``ok``
true. The stub notifier (``w2_121_support``) records each run when it starts, then sleeps and exits with a planted code.
A line of the status is taken as naming an item when it holds the item's log name (the item's file is named after it).
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import pytest

import w2_121_support as support
from w2_121_support import explain, wait_for

ESCALATION = r"(?i)notif|escalat|sent"
FAILURE = r"(?i)fail|exit|error|code|time[ds]?[- ]?out|timed out|cannot|could not|not sent"


def passes(p, count: int = 2) -> None:
    for _ in range(count):
        r = p.tick()
        assert r.code == 0, r


def first_run(p, timeout: float = 20.0) -> None:
    """Pass until the notifier has run once; every pass on the way is a good pass."""
    def ran():
        r = p.tick()
        assert r.code == 0, r
        assert p.status_json().get("ok") is True, explain(p, r)
        return p.notifies()

    wait_for(ran, timeout, 0.4, "the notifier to be run for the unread item")


def names_failure(p, entry) -> tuple[list[str], list[str]]:
    """The ``problems`` of ``status.json`` and of ``status.txt`` that name the entry's item and an escalation failure."""
    in_json = [s for s in p.problems_json(entry.log) if re.search(ESCALATION, s) and re.search(FAILURE, s)]
    in_text = [l for l in p.problem_lines(entry.log) if re.search(ESCALATION, l) and re.search(FAILURE, l)]
    return in_json, in_text


def planted(project, **config):
    p = project
    entry = p.add_ticket(901)
    p.cfg(unread_escalate_s=1, **config)
    item = p.returned_item(entry)
    return p, entry, item


def test_s4_a_failed_notifier_is_run_again_for_the_item_once_it_works_and_then_never(project):
    p, entry, item = planted(project, notify_retry_s=0)
    p.set_notify_exit(1)
    first_run(p)
    assert len(p.notifies()) == 1
    p.set_notify_exit(0)
    r = p.tick()
    assert r.code == 0, r
    calls = p.notifies()
    assert len(calls) == 2, f"the failed escalation was not tried again once the notifier worked: {calls}"
    assert all(Path(c["argv"][-1]).resolve() == item.path.resolve() for c in calls), calls
    passes(p, 3)
    assert len(p.notifies()) == 2, f"the notifier ran again after it had exited 0 for the item: {p.notifies()}"
    assert item.path.exists()


def test_s4_a_notifier_that_keeps_failing_is_tried_on_every_pass_with_retry_zero(project):
    p, entry, item = planted(project, notify_retry_s=0)
    p.set_notify_exit(1)
    first_run(p)
    passes(p, 2)
    assert len(p.notifies()) == 3, f"with notify_retry_s 0 every pass tries the due escalation: {p.notifies()}"


def test_s4_a_failed_escalation_is_not_retried_before_the_retry_time_and_every_status_names_it(project):
    p, entry, item = planted(project, notify_retry_s=3600)
    p.set_notify_exit(1)
    first_run(p)
    assert len(p.notifies()) == 1
    in_json, in_text = names_failure(p, entry)
    assert in_json, f"status.json's problems do not name the failed escalation on the pass that tried it:\n{explain(p)}"
    assert in_text, f"status.txt's problems do not name the failed escalation on the pass that tried it:\n{explain(p)}"
    for number in range(3):  # passes that do not retry it
        r = p.tick()
        assert r.code == 0, r
        assert len(p.notifies()) == 1, f"pass {number + 2} ran the notifier again inside notify_retry_s: {p.notifies()}"
        in_json, in_text = names_failure(p, entry)
        assert in_json, f"status.json's problems do not name the failed escalation on pass {number + 2}:\n{explain(p, r)}"
        assert in_text, f"status.txt's problems do not name the failed escalation on pass {number + 2}:\n{explain(p, r)}"


def test_s4_the_default_retry_time_is_not_every_pass(project):
    p, entry, item = planted(project)  # no notify_retry_s: the default (600 s)
    p.set_notify_exit(1)
    first_run(p)
    p.set_notify_exit(0)
    passes(p, 3)
    assert len(p.notifies()) == 1, f"the due escalation was tried again within the default retry time: {p.notifies()}"
    in_json, _ = names_failure(p, entry)
    assert in_json, explain(p)


def test_s4_a_notifier_that_times_out_does_not_record_the_escalation_as_raised(project):
    p, entry, item = planted(project, notify_retry_s=0, command_timeout_s=2)
    p.set_notify_sleep(8)
    first_run(p)
    assert len(p.notifies()) == 1
    p.set_notify_sleep(0)
    r = p.tick()
    assert r.code == 0, r
    calls = p.notifies()
    assert len(calls) == 2, f"a timed out notifier was recorded as sent: {calls}"
    assert Path(calls[-1]["argv"][-1]).resolve() == item.path.resolve(), calls[-1]
    passes(p, 2)
    assert len(p.notifies()) == 2, p.notifies()


def test_s4_a_notifier_that_cannot_be_started_leaves_the_escalation_due(project):
    p, entry, item = planted(project, notify_retry_s=0, notifier_command=["/nonexistent/planted-notifier"])

    def named():
        r = p.tick()
        assert r.code == 0, f"a notifier that cannot be started failed the pass\n{r}"
        assert p.status_json().get("ok") is True, explain(p, r)
        return p.problems_json(entry.log)

    wait_for(named, 20, 0.4, "the status to name the escalation that could not be sent")
    in_json, in_text = names_failure(p, entry)
    assert in_json and in_text, f"the notifier that could not be started is not named in the problems\n{explain(p)}"
    p.cfg(notifier_command=[sys.executable, str(p.stubs / "notify.py"), str(p.rec)])  # fixed
    r = p.tick()
    assert r.code == 0, r
    calls = p.notifies()
    assert len(calls) == 1 and Path(calls[0]["argv"][-1]).resolve() == item.path.resolve(), calls


def test_s4_a_failed_notifier_does_not_fail_the_pass(project):
    p, entry, item = planted(project, notify_retry_s=0)
    p.set_notify_exit(1)

    def ran():
        r = p.tick()
        assert r.code == 0, f"a pass failed on a failed notifier\n{r}"
        status = p.status_json()
        assert status.get("ok") is True, f"ok is not true after a failed notifier\n{explain(p, r)}"
        assert not p.status_text().startswith("PASS FAILED"), explain(p, r)
        return p.notifies()

    wait_for(ran, 20, 0.4, "the notifier to be run for the unread item")
    for _ in range(2):
        ran()


def test_s4_a_failed_notifier_does_not_hide_the_exit_3_of_a_refused_start(project):
    p, entry, item = planted(project, notify_retry_s=0)
    other = p.add_ticket(902)
    p.set_notify_exit(1)
    p.set_machine(mem_gib=1.5)  # the gate shuts for memory: this pass refuses every start
    p.ready(entry, other)
    deadline_runs = []

    def ran():
        r = p.tick()
        deadline_runs.append(r)
        assert r.code == 3, f"the exit code is the starts' (3), whatever the notifier did\n{r}"
        return p.notifies()

    wait_for(ran, 20, 0.4, "the notifier to be run for the unread item")
    assert p.status_json().get("ok") is True, explain(p, deadline_runs[-1])


def test_s4_an_item_read_while_its_escalation_is_failing_is_never_retried_and_its_problem_goes(project):
    p, entry, item = planted(project, notify_retry_s=0)
    p.set_notify_exit(1)
    first_run(p)
    assert len(p.notifies()) == 1
    in_json, in_text = names_failure(p, entry)
    assert in_json and in_text, explain(p)
    p.mark_read(item)
    p.set_notify_exit(0)
    for _ in range(3):
        r = p.tick()
        assert r.code == 0, r
        assert len(p.notifies()) == 1, f"a read item's escalation was tried again: {p.notifies()}"
        in_json, in_text = names_failure(p, entry)
        assert not in_json, f"status.json's problems still name the read item's escalation:\n{explain(p, r)}"
        assert not in_text, f"status.txt's problems still name the read item's escalation:\n{explain(p, r)}"


def test_s4_the_problem_line_goes_once_the_escalation_is_sent(project):
    p, entry, item = planted(project, notify_retry_s=0)
    p.set_notify_exit(1)
    first_run(p)
    in_json, in_text = names_failure(p, entry)
    assert in_json and in_text, explain(p)
    p.set_notify_exit(0)
    r = p.tick()
    assert r.code == 0, r
    assert len(p.notifies()) == 2
    in_json, in_text = names_failure(p, entry)
    assert not in_json and not in_text, f"the problem is still named after the escalation was sent\n{explain(p, r)}"


def test_s4_a_notifier_timeout_ends_the_passs_escalations_and_records_none_of_them(project):
    p = project
    first, second = p.add_ticket(901), p.add_ticket(902)
    p.cfg(unread_escalate_s=3600, notify_retry_s=0, command_timeout_s=2)
    one = p.returned_item(first)
    p.ready(first, second)
    assert p.tick().code == 0  # the second session starts (the first has its unread return)
    p.wait_launches(2)
    p.wait_exit_file(second.log)
    assert p.tick().code == 0
    (two,) = [i for i in p.items() if i.fields.get("log") == second.log]
    assert p.notifies() == []
    time.sleep(1.2)
    p.cfg(unread_escalate_s=1)  # both items are now past the unread time
    p.set_notify_sleep(8)
    r = p.tick(timeout=60)
    assert r.code == 0, r
    assert r.seconds < 40, f"the pass kept waiting after a notifier timeout ({r.seconds:.0f}s)\n{r}"
    calls = p.notifies()
    assert len(calls) == 1, f"a notifier timeout did not end the pass's escalations: {calls}"
    for entry in (first, second):
        said = [s for s in p.problems_json(entry.log) if re.search(ESCALATION, s)]
        assert said, f"the escalation of {entry.log} is not named in the status as failed or not sent\n{explain(p, r)}"
    p.set_notify_sleep(0)
    r = p.tick()
    assert r.code == 0, r
    calls = p.notifies()
    assert len(calls) == 3, f"both escalations should be due again, none recorded as raised: {calls}"
    sent = {Path(c["argv"][-1]).resolve() for c in calls[1:]}
    assert sent == {one.path.resolve(), two.path.resolve()}, sent
    passes(p, 2)
    assert len(p.notifies()) == 3, p.notifies()


@pytest.mark.parametrize("value", [-1, "soon"])
def test_s4_a_malformed_notify_retry_s_is_exit_2_and_names_the_key(project, value):
    p = project
    entry = p.add_ticket(901)
    p.cfg(notify_retry_s=value)
    p.ready(entry)
    r = p.tick()
    assert r.code == 2, r
    assert "notify_retry_s" in r.out + r.err, f"the configuration error does not name notify_retry_s\n{r}"
    p.settle(0.5)
    assert p.launches() == []


def test_s4_notify_retry_s_of_zero_is_a_good_value(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(notify_retry_s=0)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
