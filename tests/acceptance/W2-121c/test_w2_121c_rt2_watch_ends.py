"""W2-121c, RT-2 the watch pass sees every end within one pass and messages it once (success line 6).

A session in ``~/.gov-os/machine/sessions/`` whose process is gone (or whose pid now belongs to another process),
whether seen alive in an earlier pass or first seen already gone, becomes one wake message to its entry's ``notify``
(else ``cto``) with the launcher's id; a watch registered by ``gov msg watch --to <address> --name <label> --pid <pid>``
or ``--exit-file <path>`` becomes one wake message to ``<address>`` when the process is gone or the exit file exists
(naming the exit code it holds). Real short-lived ``sleep`` processes; entries planted as the registry writes them.
"""

from __future__ import annotations

import re

import w2_121c_support as s

LEAD = "lead:DAEO-r2"


def _one_wake(box, address, wanted_id=None):
    wakes = box.wakes(address)
    assert len(wakes) == 1, f"{len(wakes)} wake messages in {address}'s inbox, not one: {wakes}"
    if wanted_id is not None:
        assert wakes[0].get("id") == wanted_id, f"the message's id is {wakes[0].get('id')!r}, not {wanted_id!r}"
    return wakes[0]


def test_rt2b_a_session_that_ends_between_two_passes_gives_one_message_after_the_second(box):
    proc = box.sleeper()
    entry = box.register(proc.pid, s.start_ticks(proc.pid), notify=LEAD, address="engineer:DAEO-r2")
    box.run_pass()
    assert box.wakes(LEAD) == [], "a live session gave a message"
    box.end(proc)
    box.run_pass()
    _one_wake(box, LEAD, s.end_id(entry))
    box.passes(5)
    _one_wake(box, LEAD, s.end_id(entry))


def test_rt2b_an_entry_dead_at_the_first_pass_gives_one_message_to_cto_without_notify(box):
    pid, ticks = box.dead_pid()
    entry = box.register(pid, ticks)
    box.run_pass()
    _one_wake(box, "cto", s.end_id(entry))
    box.passes(5)
    _one_wake(box, "cto", s.end_id(entry))


def test_rt2b_a_pid_that_now_belongs_to_another_process_is_an_end(box):
    proc = box.sleeper()
    entry = box.register(proc.pid, s.start_ticks(proc.pid) + 1000, notify=LEAD)  # the entry's process started earlier
    box.run_pass()
    _one_wake(box, LEAD, s.end_id(entry))


def test_rt2b_a_pid_watch_gives_one_message_when_the_process_is_gone(box):
    proc = box.sleeper()
    request = box.watch(LEAD, "the nightly build", "--pid", str(proc.pid))
    box.run_pass()
    assert box.wakes(LEAD) == [], "a pid watch on a live process gave a message"
    box.end(proc)
    box.run_pass()
    message = _one_wake(box, LEAD, f"watch:{request}")
    assert "the nightly build" in s.message_words(message), f"the message does not name the label: {message}"
    box.passes(5)
    _one_wake(box, LEAD)


def test_rt2b_an_exit_file_watch_gives_one_message_naming_the_exit_code(box):
    exit_file = box.base / "jobs" / "measure.exit"
    request = box.watch(LEAD, "the measure job", "--exit-file", str(exit_file))
    box.run_pass()
    assert box.wakes(LEAD) == [], "an exit-file watch gave a message before the file existed"
    s.write(exit_file, "3\n")
    box.run_pass()
    message = _one_wake(box, LEAD, f"watch:{request}")
    words = s.message_words(message)
    assert "the measure job" in words, f"the message does not name the label: {message}"
    assert re.search(r"\b3\b", words), f"the message does not name exit code 3: {message}"
    box.passes(5)
    _one_wake(box, LEAD)


def test_rt2b_an_end_the_launcher_already_messaged_adds_none(box):
    pid, ticks = box.dead_pid()
    entry = box.register(pid, ticks, notify=LEAD)
    box.send(LEAD, "wake", "engineer DAEO-x121 ended (exit 0)", "--id", s.end_id(entry), "--from", "launcher")
    box.passes(3)
    _one_wake(box, LEAD, s.end_id(entry))
