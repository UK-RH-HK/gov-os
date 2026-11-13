"""S3: peaks, not the moment (DEC-1008; the lead's reading of the forms, as the brief fixes them).

History lines (JSON, one a line, ``<state>/history.jsonl``): ``{"kind", "at", "cpu", "mem_bytes"}``. A kind's peak is
the maximum over its lines. A start of a lead is admitted only when

    MemAvailable - memory_floor - (for each running job: its kind's memory peak less what it holds now, never below 0)
        >= the lead kind's memory peak
    nproc - busy cores - cpu_band - the CPU peaks ahead >= the lead kind's CPU peak

A kind with no history counts the gate's ``working_size_bytes`` as its memory peak. A refusal names the entry ``no room
for its peak`` with the figures and exits 3.

The planted gate has the floor ``F`` and the working size ``W`` (GiB) given in each case; the gate's own memory
condition (``MemAvailable >= F + W`` with no registered session) is open in every case below (the premise is checked in
``test_premise.py``), so a refusal here is the dispatcher's own. A running job holds 0.5 GiB (its planted ``statm``);
thresholds are placed at least 0.5 GiB either side of the arithmetic so that a reading which counts the job's resident
memory as 0 or as 0.5 GiB gives the same verdict.
"""

from __future__ import annotations

import os
import re

import pytest

import w2_121_support as support
from w2_121_support import GIB, MEM_FORMS, hist, kind_entry, named_with, explain, has_figure, today_strings

ROOM = r"no room for its peak"
KINDS = ("lead", "rebuild", "close", "queue", "check")


def assert_refused(p, entry, r):
    assert r.code == 3, r
    p.settle()
    assert p.launches() == [], "a session started without room for its peak"
    candidates = support.candidates(p.status_json(), p.status_text(), entry.log)
    named = [c for c in candidates if re.search(ROOM, c, re.I)]
    assert named, f"{entry.log} is not named '{ROOM}'" + explain(p, r)
    assert any(re.search(r"\d", c) for c in named), f"'{ROOM}' carries no figures: {named}"


def assert_started(p, entry, r):
    assert r.code == 0, r
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


@pytest.mark.parametrize("mem_gib, starts", [(5.5, False), (6.5, True)])
def test_s3_a_start_is_refused_under_the_leads_memory_peak_and_made_over_it(project, mem_gib, starts):
    p = project
    entry = p.add_ticket(901)
    p.history([hist("lead", 1.0, 3), hist("lead", 2.0, 5), hist("lead", 1.5, 4)])  # the peak is the maximum: 5 GiB
    p.set_machine(mem_gib=mem_gib)  # the gate needs 2 GiB: open; the room above the floor is mem_gib - 1
    p.ready(entry)
    r = p.tick()
    assert_started(p, entry, r) if starts else assert_refused(p, entry, r)


@pytest.mark.parametrize("busy, starts", [(2.0, False), (0.5, True)])
def test_s3_a_start_is_refused_under_the_leads_cpu_peak_and_made_over_it(project, busy, starts):
    p = project
    entry = p.add_ticket(901)
    p.cfg(cpu_band=1)
    p.history([hist("lead", 4.0, 0.5), hist("lead", 6.0, 0.5)])  # the peak: 6 cores
    p.set_machine(nproc=8, busy=busy)  # 8 - 2 - 1 = 5 < 6 refused; 8 - 0.5 - 1 = 6.5 >= 6 admitted
    p.ready(entry)
    r = p.tick()
    assert_started(p, entry, r) if starts else assert_refused(p, entry, r)


def test_s3_the_peaks_still_ahead_of_a_running_job_are_kept_for_it(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(job_markers={"rebuild": "rebuild-job-marker"})
    p.history([hist("rebuild", 1.0, 2), hist("rebuild", 1.0, 6)])  # a rebuild peaks at 6 GiB; the lead has no history: W
    p.plant_process(["python3", "rebuild-job-marker", "--root", "x"], rss_bytes=GIB // 2)
    p.set_machine(mem_gib=6.5)  # ahead: ~5.5 GiB; 6.5 - 1 - 5.5 = 0 < the lead's 1 GiB
    p.ready(entry)
    r = p.tick()
    assert_refused(p, entry, r)
    assert support.values_under(p.status_json(), "ahead"), "the status holds no peaks ahead" + explain(p, r)


def test_s3_without_the_running_rebuild_the_same_machine_has_room(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(job_markers={"rebuild": "rebuild-job-marker"})
    p.history([hist("rebuild", 1.0, 2), hist("rebuild", 1.0, 6)])
    p.set_machine(mem_gib=6.5)
    p.ready(entry)
    assert_started(p, entry, p.tick())


def test_s3_a_rebuild_with_room_over_its_peak_ahead_admits_the_start(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(job_markers={"rebuild": "rebuild-job-marker"})
    p.history([hist("rebuild", 1.0, 2), hist("rebuild", 1.0, 6)])
    p.plant_process(["python3", "rebuild-job-marker"], rss_bytes=GIB // 2)
    p.set_machine(mem_gib=8.5)  # 8.5 - 1 - 5.5 = 2 >= 1
    p.ready(entry)
    assert_started(p, entry, p.tick())


@pytest.mark.parametrize("floor, work, mem_gib, starts", [
    (1, 2, 4.0, False), (1, 2, 5.5, True),     # a lead with no history peaks at W = 2: 4 - 1 - 1.5 = 1.5 < 2 ; 5.5 -> 3 >= 2
    (1, 4, 7.0, False), (1, 4, 9.5, True),     # W = 4 read from gate.json: 7 - 1 - 3.5 = 2.5 < 4 ; 9.5 -> 5 >= 4
    (4, 2, 7.0, False), (1, 2, 7.0, True),     # the floor F = 4 read from gate.json: 7 - 4 - 1.5 = 1.5 < 2 ; F = 1 -> 4.5 >= 2
])
def test_s3_the_floor_and_the_working_size_are_the_gates_own(project, floor, work, mem_gib, starts):
    p = project
    entry = p.add_ticket(901)
    p.set_gate(floor_gib=floor, work_gib=work)
    p.plant_lead("DAEO-r001", rss_bytes=GIB // 2)  # a running lead: a kind with no history peaks at the working size
    p.set_machine(mem_gib=mem_gib)
    assert p.gate_reading()["open"] is True
    p.ready(entry)
    r = p.tick()
    assert_started(p, entry, r) if starts else assert_refused(p, entry, r)


def test_s3_the_status_prints_each_kinds_peak_with_its_date(project):
    p = project
    p.history([hist("lead", 1.5, 3), hist("lead", 2.5, 5), hist("rebuild", 2.0, 2), hist("rebuild", 3.0, 1),
               hist("close", 4.0, 6), hist("queue", 5.0, 4), hist("queue", 1.0, 7), hist("check", 6.0, 3)])
    expected = {"lead": (2.5, 5), "rebuild": (3.0, 2), "close": (4.0, 6), "queue": (5.0, 7), "check": (6.0, 3)}
    r = p.tick()
    assert r.code == 0, r
    for document, name in ((p.status_json(), "status.json"), (p.read_json("peaks.json"), "peaks.json")):
        for kind, (cpu, mem_gib) in expected.items():
            entry = kind_entry(document, kind)
            assert entry is not None, f"{name} holds no entry for the kind {kind}\n{document}"
            assert has_figure(entry, cpu), f"{name}: the {kind} CPU peak {cpu} is not in {entry}"
            assert has_figure(entry, mem_gib * GIB, MEM_FORMS), f"{name}: the {kind} memory peak {mem_gib} GiB is not in {entry}"
            assert any(day in text for text in support.strings(entry) for day in today_strings()) or any(
                day in text for text in support.strings(document) for day in today_strings()), \
                f"{name}: no date of today with the peaks"
    text = p.status_text().lower()
    for kind in expected:
        assert kind in text, f"status.txt does not mention the kind {kind}" + explain(p, r)


def test_s3_a_kinds_peak_is_the_maximum_over_its_history(project):
    p = project
    p.history([hist("lead", 1.0, 9.0, hours_ago=30), hist("lead", 3.0, 2.0, hours_ago=2), hist("lead", 2.0, 4.0, hours_ago=1)])
    assert p.tick().code == 0
    entry = kind_entry(p.status_json(), "lead")
    assert entry is not None and has_figure(entry, 3.0) and has_figure(entry, 9.0 * GIB, MEM_FORMS), entry


def test_s3_peaks_are_refreshed_from_the_history_when_older_than_a_day(project):
    p = project
    p.history([hist("lead", 2.0, 5)])
    assert p.tick().code == 0
    first = kind_entry(p.read_json("peaks.json"), "lead")
    assert first is not None and has_figure(first, 5 * GIB, MEM_FORMS), first
    peaks = p.state / "peaks.json"
    peaks.write_text(support.shift_iso(peaks.read_text(encoding="utf-8"), 3 * 24 * 3600), encoding="utf-8")
    old = peaks.stat().st_mtime - 3 * 24 * 3600
    os.utime(peaks, (old, old))
    p.history([hist("lead", 2.0, 8)], append=True)  # the history now holds a larger peak
    assert p.tick().code == 0
    for document, name in ((p.read_json("peaks.json"), "peaks.json"), (p.status_json(), "status.json")):
        entry = kind_entry(document, "lead")
        assert entry is not None and has_figure(entry, 8 * GIB, MEM_FORMS), f"{name} was not refreshed: {entry}"
    assert any(day in text for text in support.strings(p.read_json("peaks.json")) for day in today_strings()), \
        "the refreshed peaks carry no date of today"


def test_s3_missing_peaks_are_computed_from_the_history(project):
    p = project
    p.history([hist("lead", 2.0, 5)])
    assert p.tick().code == 0
    (p.state / "peaks.json").unlink()
    p.history([hist("lead", 2.0, 8)], append=True)
    assert p.tick().code == 0
    entry = kind_entry(p.read_json("peaks.json"), "lead")
    assert entry is not None and has_figure(entry, 8 * GIB, MEM_FORMS), entry


def test_s3_the_job_history_file_is_the_configured_one(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(history="var/jobs.jsonl")
    p.history([hist("lead", 1.0, 5)], rel="var/jobs.jsonl")
    p.set_machine(mem_gib=5.5)  # refused only if the configured history is read: 5.5 - 1 < 5 (with no history: W = 1 fits)
    p.ready(entry)
    r = p.tick()
    assert_refused(p, entry, r)
