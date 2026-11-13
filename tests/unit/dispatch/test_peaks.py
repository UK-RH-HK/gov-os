"""Peaks, not the moment: the history, peaks.json, the room for a start (S3)."""
from __future__ import annotations

import datetime
import json

from conftest import GIB


def row(kind, cpu, mem_gib, at="2026-11-01T10:00:00+00:00"):
    return {"kind": kind, "at": at, "cpu": cpu, "mem_bytes": int(mem_gib * GIB)}


def plant(project, *rows, w2="W2-1"):
    project.ticket(w2)
    project.ready(project.entry(w2))
    if rows:
        project.history(*rows)


def reasons(project) -> dict:
    return {s["W2"]: s["reason"] for s in project.status()["skipped"]}


def test_peaks_are_the_maximum_of_each_kinds_history_with_a_date(project):
    plant(project, row("lead", 2, 4), row("lead", 3, 6, "2026-11-02T10:00:00+00:00"), row("rebuild", 8, 12),
          row("lead", 1, 2))
    project.tick()
    kinds = json.loads((project.state / "peaks.json").read_text())["kinds"]
    assert kinds["lead"]["cpu"] == 3 and kinds["lead"]["mem_bytes"] == 6 * GIB
    assert kinds["rebuild"]["cpu"] == 8 and kinds["rebuild"]["mem_bytes"] == 12 * GIB
    assert kinds["lead"]["date"] and kinds["rebuild"]["date"]
    shown = project.status()["peaks"]["kinds"]
    assert shown["lead"]["mem_bytes"] == 6 * GIB and shown["rebuild"]["cpu"] == 8
    assert "rebuild" in project.status_text() and "peaks" in project.status_text()


def test_peaks_older_than_a_day_are_refreshed_from_the_history(project):
    plant(project, row("lead", 3, 6))
    project.state.mkdir(parents=True, exist_ok=True)
    old = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)).isoformat()
    (project.state / "peaks.json").write_text(json.dumps(
        {"computed": old, "kinds": {"lead": {"cpu": 1, "mem_bytes": GIB, "date": old[:10]}}}))
    project.tick()
    data = json.loads((project.state / "peaks.json").read_text())
    assert data["kinds"]["lead"]["mem_bytes"] == 6 * GIB and data["computed"] > old


def test_a_fresh_peaks_file_is_kept_unless_the_history_is_newer(project):
    plant(project, row("lead", 3, 6))
    project.tick()
    first = json.loads((project.state / "peaks.json").read_text())["computed"]
    project.wait_exit("W2-1-log")
    project.read_all()
    project.ticket("W2-2")
    project.ready(project.entry("W2-2"))
    project.tick()
    assert json.loads((project.state / "peaks.json").read_text())["computed"] == first  # fresh, history unchanged
    project.history(row("lead", 3, 9))
    project.tick()
    assert json.loads((project.state / "peaks.json").read_text())["kinds"]["lead"]["mem_bytes"] == 9 * GIB


def test_no_history_counts_the_gates_working_size_as_the_memory_peak(project):
    plant(project)
    project.tick()
    lead = project.status()["peaks"]["kinds"]["lead"]
    assert lead["mem_bytes"] == 1 * GIB and lead["source"] == "gate working_size_bytes"
    assert project.started() == ["W2-1-log"]


def test_a_start_is_refused_under_the_new_peak_and_made_over_it(project):
    plant(project, row("lead", 2, 6))
    project.memory(8 * GIB)   # 8 - 3 (the floor) = 5 < 6
    code, _ = project.tick()
    assert code == 3 and project.started() == []
    why = reasons(project)["W2-1"]
    assert why.startswith("no room for its peak") and "memory" in why and str(6 * GIB) in why
    project.memory(10 * GIB)  # 10 - 3 = 7 >= 6; the gate's own memory condition still holds
    code, _ = project.tick()
    assert code == 0 and project.started() == ["W2-1-log"]


def test_the_peaks_ahead_of_running_work_are_kept_back(project):
    plant(project, row("lead", 2, 6))
    project.write_config(max_leads=5)
    project.lead_process(100, "T-a", rss=1 * GIB)   # 6 - 1 = 5 still to come
    project.lead_process(101, "T-b", rss=1 * GIB)   # another 5
    project.memory(18 * GIB)                        # 18 - 3 - 10 = 5 < 6
    code, _ = project.tick()
    assert code == 3 and project.started() == []
    assert project.status()["peaks_ahead"]["memory_bytes"] == 10 * GIB
    project.memory(20 * GIB)                        # 20 - 3 - 10 = 7 >= 6
    project.tick()
    assert project.started() == ["W2-1-log"]


def test_a_job_past_its_peak_leaves_nothing_ahead(project):
    plant(project, row("lead", 2, 6))
    project.lead_process(100, "T-a", rss=8 * GIB)   # holds more than the peak: never below 0
    project.tick()
    assert project.status()["peaks_ahead"]["memory_bytes"] == 0


def test_cpu_room_is_nproc_less_busy_band_and_the_peaks_ahead(project):
    plant(project, row("lead", 4, 1))
    project.mp.setenv("GOV_RESOURCES_NPROC", "6")      # 6 - 2 busy - 1 band = 3 < 4
    code, _ = project.tick()
    assert code == 3 and project.started() == []
    assert "cpu" in reasons(project)["W2-1"]
    project.mp.setenv("GOV_RESOURCES_NPROC", "8")      # 8 - 2 - 1 = 5 >= 4
    project.tick()
    assert project.started() == ["W2-1-log"]


def test_other_kinds_running_are_found_by_their_markers(project):
    plant(project, row("lead", 1, 1), row("rebuild", 6, 10))
    project.write_config(job_markers={"rebuild": "rebuild-job"})
    project.process(300, ["python", "rebuild-job", "--all"], rss=2 * GIB)
    project.process(301, ["python", "rebuild-job", "--child"], rss=1 * GIB, ppid=300)  # the same job
    project.memory(14 * GIB)   # 14 - 3 - (10 - 3 held by the whole tree) = 4 >= 1
    project.tick()
    ahead = project.status()["peaks_ahead"]
    assert ahead["memory_bytes"] == 7 * GIB and [j["kind"] for j in ahead["jobs"]] == ["rebuild"]
    assert project.started() == ["W2-1-log"]


def test_a_malformed_history_line_is_ignored_and_named(project):
    plant(project, row("lead", 1, 2))
    with open(project.state / "history.jsonl", "a") as file:
        file.write("not json\n" + json.dumps({"kind": "lead", "cpu": "x"}) + "\n")
    project.tick()
    assert project.status()["peaks"]["kinds"]["lead"]["mem_bytes"] == 2 * GIB
    assert project.status()["peaks"]["ignored_history_lines"] == 2
