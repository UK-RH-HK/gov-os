"""S3 (and F3): ``gov session-watch helper-watch`` writes one inbox item per condition, once, for a helper of the registered
session or a launched worker; none for a healthy one."""

from __future__ import annotations

import json
import re

import pytest

import w2_160_support as support
from w2_160_support import CONDITIONS, HEALTHY, HOUR, MINUTE, NOW


def _subjects():
    return tuple(CONDITIONS) + HEALTHY


def test_s3_one_item_per_condition_each_naming_its_subject_and_none_for_the_healthy(w, procs):
    support.plant_all(w, procs)
    result = w.run()
    items = result.new_items
    assert len(items) == len(CONDITIONS), f"one item per planted condition ({len(CONDITIONS)}):\n{result}\n{sorted(items)}"
    assert w.inbox == w.items()[0].parent, "the items are in <root>/.gov-runtime/dispatch/inbox/"
    for subject in CONDITIONS:
        naming = [name for name, text in items.items() if subject in text]
        assert len(naming) == 1, f"exactly one item names {subject!r} ({CONDITIONS[subject]}); {naming}\n{result}"
    for name, text in items.items():
        named = support.item_subjects(text, _subjects())
        assert len(named) == 1 and named[0] in CONDITIONS, f"{name} names one planted condition's subject, got {named}:\n{text}"
    for subject in HEALTHY:
        assert not any(subject in text for text in items.values()), f"the healthy {subject!r} has no item"
        assert subject not in result.out, f"nor a line on stdout: {result}"


def test_s3_a_second_pass_writes_no_new_item_at_the_same_clock_or_a_little_later(w, procs):
    support.plant_all(w, procs)
    first = w.run()
    count = len(w.items())
    assert count == len(CONDITIONS), first
    for offset in (0, 120):
        again = w.run(now=NOW + offset)
        assert again.new_items == {}, f"nothing changed: no new item at clock +{offset}s:\n{again}"
        assert "HELPER_WATCH item" not in again.out, again
        assert len(w.items()) == count, "the inbox count is unchanged"


def test_s3_the_state_file_and_the_log_record_each_pass(w, procs):
    support.plant_all(w, procs)
    first = w.run()
    state_after_first = json.loads(w.state_file.read_text(encoding="utf-8"))
    assert state_after_first, "the state file holds the reported conditions"
    w.run()
    state_after_second = json.loads(w.state_file.read_text(encoding="utf-8"))
    assert state_after_second == state_after_first, "a second pass with nothing changed leaves the state as it was"
    lines = [line for line in w.log_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 2, f"one JSON line per pass:\n{lines}"
    docs = [json.loads(line) for line in lines]
    assert all(isinstance(doc, dict) for doc in docs), lines
    assert all(name in lines[0] for name in first.new_items), "the first line names the items it wrote"
    assert not any(name in lines[1] for name in first.new_items), "the second line names none of them"


def test_s3_a_condition_that_drops_out_of_one_pass_and_comes_back_is_not_reported_twice(w, procs):
    trail = w.helper("apierr01", [support.user(900), support.assistant(600), support.api_error(300)], age=300)
    w.worker("wk-gone", procs.dead(), pid_age=600)
    assert len(w.run().new_items) == 2
    saved = trail.read_text(encoding="utf-8")
    trail.unlink()
    (w.subagents / "agent-apierr01.meta.json").unlink()
    pid_file = w.root / ".gov-runtime/jobs/launch/wk-gone.pid"
    pid_text = pid_file.read_text(encoding="utf-8")
    pid_file.unlink()
    assert w.run().new_items == {}, "the conditions are gone from this pass"
    trail.write_text(saved, encoding="utf-8")
    support.touch(trail, 300)
    pid_file.write_text(pid_text, encoding="utf-8")
    support.touch(pid_file, 600)
    back = w.run()
    assert back.new_items == {}, f"a reported condition is never forgotten (the state only grows):\n{back}"
    assert len(w.items()) == 2


def test_s3_no_registered_session_means_no_helper_is_looked_at(w):
    w.helper("apierr01", [support.user(900), support.api_error(300)], age=300)
    w.unregister()
    result = w.run()
    assert result.new_items == {}, f"no session file: no helper item:\n{result}"
    assert result.code == 0


def test_s3_a_helper_that_recovered_after_an_api_error_is_not_reported(w):
    w.helper("recov01", [support.user(900), support.api_error(500), support.assistant(100, "recovered")], age=100)
    result = w.run()
    assert result.new_items == {}, f"the last entry is a normal reply:\n{result}"


def test_s3_entries_that_are_not_messages_after_the_error_do_not_hide_it(w):
    w.helper("apierr01", [support.user(900), support.assistant(600), support.api_error(300), support.bookkeeping(250)],
             age=250)
    result = w.run()
    assert len(result.new_items) == 1 and "apierr01" in next(iter(result.new_items.values())), result


def test_s3_the_clients_synthetic_error_form_is_found(w):
    w.helper("synth01", [support.user(900), support.api_error(300, synthetic=True)], age=300)
    result = w.run()
    assert len(result.new_items) == 1 and "synth01" in next(iter(result.new_items.values())), result


@pytest.mark.parametrize("minutes, finished, stale_arg, reported", [
    (29, False, None, False),
    (31, False, None, True),
    (31, True, None, False),
    (15, False, 10, True),
    (15, False, 20, False),
], ids=["29-min-under-the-default", "31-min-over-the-default", "31-min-but-finished", "15-min-over-stale-min-10",
        "15-min-under-stale-min-20"])
def test_s3_a_helper_not_finished_is_stalled_after_stale_min_minutes(w, minutes, finished, stale_arg, reported):
    age = minutes * MINUTE
    w.helper("stall01", [support.user(age + 600), support.assistant(age)], age=age, finished=finished)
    result = w.run(*(["--stale-min", stale_arg] if stale_arg else []))
    assert bool(result.new_items) is reported, result
    if reported:
        assert len(result.new_items) == 1 and "stall01" in next(iter(result.new_items.values())), result


@pytest.mark.parametrize("age, every, reported", [(600, None, False), (100, None, True), (600, 1000, True)],
                         ids=["exit-file-600s-old-every-300", "exit-file-100s-old-every-300", "exit-file-600s-old-every-1000"])
def test_s3_an_exit_file_counts_only_if_not_older_than_the_start_less_every(w, procs, age, every, reported):
    w.worker("wk-exit3", procs.dead(), code=3, exit_age=age, pid_age=age + 300)
    result = w.run(*(["--every", every] if every else []))
    assert bool(result.new_items) is reported, result
    if reported:
        assert len(result.new_items) == 1 and "wk-exit3" in next(iter(result.new_items.values())), result


def test_s3_each_helper_item_carries_its_last_entrys_type_or_time(w):
    entry = support.api_error(300)
    w.helper("apierr01", [support.user(900), entry], age=300)
    result = w.run()
    text = next(iter(result.new_items.values()))
    assert "apierr01" in text
    assert entry["type"] in text or entry["timestamp"] in text, f"the item gives the last line (type or time):\n{text}"


def test_s3_pid_files_are_found_by_the_default_glob_at_any_depth_under_gov_runtime(w, procs):
    w.worker("wk-deep", procs.dead(), folder=".gov-runtime/a/b/c")
    result = w.run()
    assert len(result.new_items) == 1 and "wk-deep" in next(iter(result.new_items.values())), result


def test_s3_the_configured_pid_globs_replace_the_default(w, procs):
    w.config("session_watch:\n  pid_globs:\n    - 'custom/**/*.pid'\n")
    w.worker("wk-default", procs.dead(), folder=".gov-runtime/jobs/launch")
    w.worker("wk-custom", procs.dead(), folder="custom/run")
    result = w.run()
    texts = list(result.new_items.values())
    assert len(texts) == 1 and "wk-custom" in texts[0], f"only the configured glob is searched:\n{result}"
    assert "wk-default" not in texts[0]


def test_s3_a_pid_globs_of_the_wrong_kind_is_a_configuration_error_exit_1_naming_the_key(w):
    w.config("session_watch:\n  pid_globs: 5\n")
    result = w.run(expect=1)
    assert "pid_globs" in result.out + result.err, f"the error names the key:\n{result}"
    assert w.items() == []


def test_s3_a_zombie_worker_is_gone(w, procs):
    pid = procs.zombie()
    if pid is None:
        pytest.skip("a zombie cannot be arranged here")
    w.worker("wk-zombie", pid)
    result = w.run()
    assert len(result.new_items) == 1 and "wk-zombie" in next(iter(result.new_items.values())), result


def test_s3_a_live_worker_with_no_exit_file_is_not_reported(w, procs):
    w.worker("wk-run", procs.sleeper().pid, pid_age=300)
    assert w.run().new_items == {}


def test_s3_a_clean_exit_with_a_clean_result_is_not_reported(w, procs):
    w.worker("wk-clean", procs.dead(), code=0, result={"is_error": False, "api_error_status": None}, pid_age=900)
    assert w.run().new_items == {}


def test_s3_helpers_default_to_the_claude_projects_folder_of_the_root(w):
    folder = w.home / ".claude" / "projects" / support.mangled(w.root) / support.SESSION / "subagents"
    w.helper("apierr01", [support.user(900), support.api_error(300)], age=300, folder=folder)
    result = w.run(subagents=False)
    assert len(result.new_items) == 1 and "apierr01" in next(iter(result.new_items.values())), result


def test_s3_the_loop_ends_after_max_with_one_ended_line_and_writes_each_item_once(w):
    w.helper("apierr01", [support.user(900), support.api_error(300)], age=300)
    result = w.run("--every", 1, "--max", 1, once=False, timeout=30)
    lines = [line for line in result.out.splitlines() if line.strip()]
    assert re.fullmatch(r"HELPER_WATCH ended after \d+(\.\d+)? s; 1 item\(s\) written; re-arm it", lines[-1]), result
    assert sum(1 for line in lines if line.startswith("HELPER_WATCH ended")) == 1, result
    assert len(w.items()) == 1, "two passes of the loop, one item"
    assert result.elapsed < 15, result
