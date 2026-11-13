"""S4 (and F2): the helper watch reads names, timestamps and error codes only, matches no process by name, writes only the
inbox, its state file and its log, and looks only at transcripts and pid files inside the window."""

from __future__ import annotations

import pytest

import w2_160_support as support
from w2_160_support import CANARY, CONDITIONS, HOUR, NOW


def test_s4_a_planted_message_text_is_never_in_an_item_the_state_the_log_or_the_output(w, procs):
    support.plant_all(w, procs)
    for clock in (NOW, NOW + 120):  # the first pass writes the items; the second writes the state and the log again
        before = w.snapshot()
        result = w.run(now=clock)
        after = w.snapshot()
        assert CANARY not in result.out and CANARY not in result.err, f"standard output and error:\n{result}"
        for path, text in w.every_new_or_changed_text(before, after).items():
            assert CANARY not in text, f"a message's text was copied into {path}"
    assert len(w.items()) == len(CONDITIONS), "the canary run did report its conditions (else it shows nothing)"
    assert w.state_file.is_file() and w.log_file.is_file()


def test_s4_only_the_inbox_the_state_file_and_the_log_are_new_or_changed(w, procs):
    support.plant_all(w, procs)
    for clock in (NOW, NOW + 120):
        before = w.snapshot()
        w.run(now=clock)
        after = w.snapshot()
        outside = w.written_outside_the_allowed(before, after)
        assert outside == [], f"written outside the inbox, helper-watch-state.json and helper-watch.log: {outside}"
    assert len(w.items()) == len(CONDITIONS)


def test_s4_an_error_found_writes_nothing_else_either(w):
    w.config("session_watch:\n  pid_globs: 5\n")
    w.helper("apierr01", [support.user(900), support.api_error(300)], age=300)
    before = w.snapshot()
    w.run(expect=1)
    assert w.written_outside_the_allowed(before, w.snapshot()) == []


@pytest.mark.parametrize("hours, window, reported", [(25, 24, False), (23, 24, True), (25, 48, True)],
                         ids=["25h-old-window-24", "23h-old-window-24", "25h-old-window-48"])
def test_s4_only_a_transcript_whose_last_entry_is_inside_the_window_is_looked_at(w, hours, window, reported):
    age = hours * HOUR
    w.helper("apierr01", [support.user(age + 600), support.api_error(age)], age=age, finished=True)
    result = w.run("--window-h", window)
    assert bool(result.new_items) is reported, result
    if reported:
        assert len(result.new_items) == 1 and "apierr01" in next(iter(result.new_items.values())), result


def test_s4_a_stalled_helper_older_than_the_default_window_is_not_looked_at(w):
    w.helper("stall01", [support.user(26 * HOUR + 600), support.assistant(26 * HOUR)], age=26 * HOUR)
    assert w.run().new_items == {}


@pytest.mark.parametrize("hours, reported", [(25, False), (23, True)], ids=["pid-file-25h-old", "pid-file-23h-old"])
def test_s4_a_pid_file_older_than_the_window_is_skipped(w, procs, hours, reported):
    w.worker("wk-gone", procs.dead(), pid_age=hours * HOUR)
    result = w.run("--window-h", 24)
    assert bool(result.new_items) is reported, result
    if reported:
        assert len(result.new_items) == 1 and "wk-gone" in next(iter(result.new_items.values())), result


def test_s4_the_helper_watch_matches_no_process_by_name():
    assert support.HELPER_WATCH_SRC.is_file(), f"{support.HELPER_WATCH_SRC} does not exist: the helper watch is not built"
    hits = support.process_name_hits(support.HELPER_WATCH_SRC)
    assert hits == [], f"a process-name match in the helper watch: {hits}"


def test_s4_gov_wait_matches_no_process_by_name():
    assert support.WAIT_SRC.is_dir(), f"{support.WAIT_SRC} does not exist: gov wait is not built"
    sources = sorted(support.WAIT_SRC.rglob("*.py"))
    assert sources, f"{support.WAIT_SRC} holds no Python file"
    hits = [hit for path in sources for hit in support.process_name_hits(path)]
    assert hits == [], f"a process-name match in gov wait: {hits}"
