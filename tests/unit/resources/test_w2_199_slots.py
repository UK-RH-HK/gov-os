"""The slot set after the load admission (W2-199): the slot count's precedence, the held list, the priority registration,
a nested run and the runtime log's events. Planted machine of ``conftest``; the jobs are stand-in programs."""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from gov.cli.errors import GovError
from gov.resources import config as configuration
from gov.resources import slots

PLAIN = ["sh", "-c", "exit 7"]


def events(planted):
    path = planted.home / ".gov-os" / "runtime" / "log.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def test_the_slot_count_is_the_variable_then_the_file_then_the_derived_count(planted, monkeypatch):
    planted.config(heavy_slots=3)
    assert slots.slot_count(configuration.load(), lambda line: None) == 3
    monkeypatch.setenv("GOV_HEAVY_SLOTS", "1")
    assert slots.slot_count(configuration.load(), lambda line: None) == 1
    monkeypatch.delenv("GOV_HEAVY_SLOTS")
    planted.config(heavy_slots=None)
    assert slots.slot_count(configuration.load(), lambda line: None) == 2  # 20 CPUs: floor(0.1 x 20)


def test_the_held_list_keeps_the_slots_that_exist_once_each():
    assert slots._held_slots("1,2,2,9,x, 3", 3) == [1, 2, 3]
    assert slots._held_slots("", 3) == [] and slots._held_slots("0", 3) == []


def test_a_dead_priority_registration_is_ignored_and_removed(planted, monkeypatch):
    place = slots.folder()
    place.mkdir(parents=True)
    child = subprocess.Popen(["true"])
    child.wait()
    (place / f"prio-{child.pid}").write_text(str(child.pid))
    assert slots._priority_waiting() is False and not (place / f"prio-{child.pid}").exists()
    (place / "prio-1").write_text("1")  # pid 1 lives
    assert slots._priority_waiting() is True


def test_a_run_logs_ready_admitted_started_ended_with_one_job_id(planted):
    assert slots.run("test", PLAIN) == 7
    found = events(planted)
    assert [e["event"] for e in found] == ["ready", "admitted", "started", "ended"]
    assert len({e["job"] for e in found}) == 1 and found[-1]["code"] == 7 and found[-1]["workers"] == 4
    assert list((slots.folder()).glob("prio-*")) == []


def test_a_nested_run_takes_no_slot_and_logs_nested(planted, monkeypatch):
    monkeypatch.setenv("GOV_HEAVY_ADMITTED", "1")
    monkeypatch.setenv("GOV_HEAVY_SLOTS", "1")
    assert slots.run("test", PLAIN) == 7
    assert [e["event"] for e in events(planted)] == ["nested"]
    assert not list(slots.folder().glob("slot-*")) if slots.folder().exists() else True


def test_a_gpu_kind_without_its_need_is_invalid_and_with_no_gpu_refused_with_exit_3(planted):
    with pytest.raises(GovError) as invalid:
        slots.run("embedder", PLAIN)
    assert invalid.value.code == "RESOURCE_ARGUMENTS_INVALID"
    with pytest.raises(GovError) as refused:
        slots.run("embedder", PLAIN, gpu_need_mib=500)
    assert refused.value.exit_code == 3 and "memory is unavailable" in refused.value.message
    assert [e["event"] for e in events(planted)][-1] == "ended" and events(planted)[-1]["code"] == 3
