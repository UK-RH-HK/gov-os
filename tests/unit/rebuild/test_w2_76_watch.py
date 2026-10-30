"""Builder tests for the rebuild's settings, lock, stage times and watchdog (W2-76, DEC-939 item 2).

Regression evidence only (MR-3). They cover what the acceptance tests leave to the builder: the settings' checks, the
command-line cut, a hold on the lock through a descriptor of this process, a lock that cannot be opened, the secrets
filter's calls in several threads counted once, and a watchdog whose record cannot be written still never failing.
Every lock here is a temporary file, never the machine's.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import threading
import time

import pytest

from gov.cli.errors import GovError
from gov.rebuild import watch
from gov.rebuild.command import add_arguments, run


def _settings(root, text):
    path = root / watch.SETTINGS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_the_defaults_hold_without_a_settings_file(tmp_path):
    assert watch.settings(tmp_path) == (1800, "/tmp/gov-os-rebuild.lock")


@pytest.mark.parametrize("text, key", [("slow_after_s: true\n", "slow_after_s"), ("slow_after_s: -1\n", "slow_after_s"),
                                       ("lock: null\n", "lock"), ("lock: locks/x.lock\n", "lock"), ("[1, 2]\n", None)])
def test_a_wrong_setting_refuses_naming_the_file_and_the_key(tmp_path, text, key):
    _settings(tmp_path, text)
    with pytest.raises(GovError) as raised:
        watch.settings(tmp_path)
    assert raised.value.code == "REBUILD_FAILED" and raised.value.details == {"file": watch.SETTINGS_REL, "key": key}


def test_a_command_line_keeps_12_hex_digits_of_a_run_and_200_characters():
    assert watch.cut("git show " + "a" * 40 + " " + "b" * 12) == "git show " + "a" * 12 + " " + "b" * 12
    assert len(watch.cut("x" * 500)) == 200


def test_a_free_lock_is_taken_and_a_hold_of_this_process_is_used_without_waiting(tmp_path):
    path = str(tmp_path / "rebuild.lock")
    fd, part = watch.take(path)
    assert fd is not None and part["wait_s"] == 0.0 and part["held_by_caller"] is False and part["holder"] is None
    os.close(fd)
    held = os.open(path, os.O_RDONLY)  # as `flock <lock> gov rebuild` leaves a descriptor to its child
    try:
        fcntl.flock(held, fcntl.LOCK_EX)
        started = time.monotonic()
        fd, part = watch.take(path)
        assert fd is None and part["held_by_caller"] is True and time.monotonic() - started < 5
        assert part["holder"]["pid"] == os.getpid()
    finally:
        os.close(held)


def test_a_lock_that_cannot_be_opened_refuses_naming_it(tmp_path):
    path = str(tmp_path / "missing" / "rebuild.lock")
    with pytest.raises(GovError) as raised:
        watch.take(path)
    assert raised.value.code == "REBUILD_FAILED" and path in raised.value.message


def test_calls_in_several_threads_at_once_count_once():
    spans = watch._Spans()
    slow = spans.wrap(lambda: time.sleep(0.3))
    threads = [threading.Thread(target=slow) for _ in range(4)]
    started = time.monotonic()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert spans.total() <= time.monotonic() - started and spans.total() < 0.9


def test_an_unwritable_record_is_a_fault_and_the_slow_watch_goes_on(tmp_path, capsys):
    (tmp_path / ".gov-runtime").mkdir()
    (tmp_path / ".gov-runtime" / "rebuild").write_text("a file, not a folder")
    watched = watch.Watch(tmp_path, 0.2, {"path": "x", "wait_s": 0.0})
    with watched.stage("lexical"):
        time.sleep(0.6)
    ending = watched.end()
    assert ending["slow"] is True and ending["watchdog_faults"]
    assert len(ending["watchdog_faults"]) == len(set(ending["watchdog_faults"]))  # each fault said once
    err = capsys.readouterr().err
    assert err.count("rebuild: slow: past 0.2 s") == 1 and "rebuild: watchdog fault: " in err


def test_a_slow_watch_writes_its_record_and_keeps_it_apart(tmp_path):
    watched = watch.Watch(tmp_path, 0.2, {"path": "x", "wait_s": 0.0})
    with watched.stage("codeintel"):
        time.sleep(0.6)
    watched.end()
    record = json.loads((tmp_path / watch.RECORD_REL).read_text())
    assert record["slow"] is True and record["stages_done"] == {"codeintel": pytest.approx(0.6, abs=0.2)}
    assert record["processes"][0]["pid"] == os.getpid() and len(record["load"]) == 3
    assert len(list((tmp_path / ".gov-runtime" / "rebuild").glob("slow-*Z.json"))) == 1


def test_a_rebuild_s_result_times_every_stage_and_keeps_its_keys(tmp_path, monkeypatch):
    _settings(tmp_path, f"lock: {tmp_path / 'rebuild.lock'}\n")
    monkeypatch.setattr("gov.store.load", lambda root: {"digest": "d"})
    monkeypatch.setattr("gov.retrieval.lexical.refresh", lambda root: None)
    monkeypatch.setattr("gov.codeintel.index", lambda root: None)
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    result = run(tmp_path, parser.parse_args(["--no-embeddings"]), {"path-map.yaml": {}})
    assert list(result)[:4] == ["digest", "store", "stores", "compaction"]
    assert list(result["timing"]) == ["record_s", "lexical_s", "secrets_s", "semantic_s", "codeintel_s",
                                      "compaction_s", "total_s"]
    assert result["timing"]["semantic_s"] == 0.0 and result["slow"] is False and result["watchdog_faults"] == []
    assert result["lock"]["held_by_caller"] is False and result["lock"]["released_at"] >= result["lock"]["taken_at"]
    assert (tmp_path / result["record"]).is_file()
