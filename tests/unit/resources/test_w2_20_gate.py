"""Unit tests for the gate's configuration, readings, registry and conditions (W2-20 S1-S8, S11, failure lines 2-6).

Planted machines only (the ``planted`` fixture): a temporary HOME, planted /proc files and process table."""
from __future__ import annotations

import datetime
import json
import os

import pytest

from gov.cli.errors import GovError
from gov.resources import config as configuration
from gov.resources import gate, registry

GIB = 1024 ** 3


def reasons(reading):
    return {reason["condition"]: reason for reason in reading["gate"]["reasons"]}


# --- S8: the one configuration file ---------------------------------------------------------------------------------

def test_no_configuration_file_shuts_the_gate_naming_it(planted):
    reading = gate.read("session")
    assert not reading["gate"]["open"]
    assert any("gate.json is missing" in r.get("why", "") for r in reading["gate"]["reasons"] if r["condition"] == "config")


@pytest.mark.parametrize("key", list(configuration.VALUES))
def test_each_missing_value_shuts_the_gate_naming_it(planted, key):
    planted.config(**{key: None})
    named = [r["why"] for r in gate.read("session")["gate"]["reasons"] if r["condition"] == "config"]
    assert any(why.startswith(key) for why in named), named


@pytest.mark.parametrize("key,bad", [("floor_bytes", -1), ("floor_bytes", "3G"), ("heavy_slots", 0),
                                     ("gpu_margin", 1.5), ("disk_path", "relative/path"), ("rebuild_peak_bytes", 0),
                                     ("gpu_shares", [{"kind": "embedder"}]), ("verification_lock", 3)])
def test_a_malformed_value_shuts_the_gate_naming_it(planted, key, bad):
    planted.config(**{key: bad})
    named = [r["why"] for r in gate.read("session")["gate"]["reasons"] if r["condition"] == "config"]
    assert any(why.startswith(key) for why in named), named


def test_a_value_without_date_or_source_shuts_the_gate(planted):
    data = planted.config()
    data["floor_bytes"].pop("date")
    data["inode_floor"]["source"] = " "
    (planted.dir / "gate.json").write_text(json.dumps(data))
    named = " ".join(r["why"] for r in gate.read("session")["gate"]["reasons"] if r["condition"] == "config")
    assert "floor_bytes: no date" in named and "inode_floor: no source" in named


def test_an_embedding_server_entry_malformed_shuts_the_gate(planted):
    data = planted.config()
    data["embedding_servers"]["query"]["device"] = "tpu"
    del data["embedding_servers"]["shared"]["source"]
    (planted.dir / "gate.json").write_text(json.dumps(data))
    named = " ".join(r["why"] for r in gate.read("session")["gate"]["reasons"] if r["condition"] == "config")
    assert "embedding_servers.query.device" in named and "embedding_servers.shared: no source" in named


def test_a_measured_figure_older_than_seven_days_is_due_for_remeasure_and_still_counts(planted):
    data = planted.config()
    old = (datetime.date.today() - datetime.timedelta(days=8)).isoformat()
    fresh = datetime.date.today().isoformat()
    for key in configuration.MEASURED:
        data[key]["date"] = fresh
    data["rebuild_peak_bytes"]["date"] = old
    (planted.dir / "gate.json").write_text(json.dumps(data))
    reading = gate.read("session")
    due = reading["config"]["due_for_remeasure"]
    assert len(due) == 1 and due[0].startswith("rebuild_peak_bytes") and "due for re-measure" in due[0]
    assert reading["gate"]["open"], reading["gate"]


def test_init_config_writes_a_dated_sourced_file_and_never_overwrites(planted):
    written = configuration.init()["config"]
    loaded = configuration.load()
    assert loaded["faults"] == [] and set(configuration.VALUES) <= set(loaded["values"])
    assert written["rebuild_peak_bytes"]["date"] and written["rebuild_peak_bytes"]["source"]
    before = configuration.path().read_text()
    with pytest.raises(GovError) as refused:
        configuration.init()
    assert refused.value.code == "RESOURCE_CONFIG_EXISTS" and configuration.path().read_text() == before


def test_the_template_derives_the_servers_cpus_on_a_smaller_machine():
    data = configuration.template(cpus=list(range(8)), home="/home/x")
    assert data["embedding_servers"]["shared"]["cpus"] == "0-7"
    assert "derived" in data["embedding_servers"]["shared"]["source"]


# --- S1, S3, failure 2: the registry --------------------------------------------------------------------------------

def test_every_live_session_is_read_whichever_repository_started_it(planted):
    planted.config()
    for pid, repo in ((501, "/repo/one"), (502, "/repo/two")):
        planted.process(pid, rss=GIB // 4)
        planted.session(pid, repository=repo)
    reading = gate.read(None)
    assert sorted(s["repository"] for s in reading["sessions"]) == ["/repo/one", "/repo/two"]
    assert reading["available_memory_bytes"] == 20 * GIB and reading["load_1m"] == 1.0


def test_a_stale_entry_is_cleared_by_the_read_that_finds_it(planted):
    planted.config()
    planted.process(601)
    planted.session(601)
    planted.session(602)  # no such process
    reading = gate.read(None)
    assert [s["pid"] for s in reading["sessions"]] == [601]
    assert [s["pid"] for s in reading["cleared"]] == [602]
    assert not (planted.dir / "sessions" / "602.json").exists()


def test_an_unreadable_entry_shuts_the_gate(planted):
    planted.config()
    (planted.dir / "sessions").mkdir(parents=True)
    (planted.dir / "sessions" / "77.json").write_text("{not json")
    assert "sessions" in reasons(gate.read("session"))


def test_register_writes_one_whole_entry(planted):
    entry = registry.register(4242, planted.root, "DAEO-r30l", "engineer")
    stored = json.loads((planted.dir / "sessions" / "4242.json").read_text())
    assert stored == entry and stored["repository"] == str(planted.root.resolve())
    with pytest.raises(GovError):
        registry.register(0, planted.root, "t", "r")


# --- S5: the load rule ----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("one,fifteen,open_", [(40.0, 5.0, True), (5.0, 40.0, True), (20.0, 20.0, False),
                                               (25.0, 30.0, False), (19.9, 30.0, True)])
def test_the_load_opens_while_the_lesser_of_one_and_fifteen_minutes_is_below_nproc(planted, one, fifteen, open_):
    planted.config()
    planted.loads(one, 10.0, fifteen)
    assert ("load" not in reasons(gate.read("session"))) is open_


def test_an_unreadable_load_shuts_the_gate(planted, monkeypatch):
    planted.config()
    monkeypatch.setenv("GOV_RESOURCES_LOADAVG", str(planted.root / "missing"))
    assert reasons(gate.read("session"))["load"]["reading"] is None


# --- S2, S11: busy cores and the servers ----------------------------------------------------------------------------

def test_busy_cores_over_the_last_minute_shut_the_gate_and_both_figures_are_shown(planted):
    planted.config()
    planted.busy(20.0)
    planted.loads(3.0, 3.0, 3.0)
    reading = gate.read("session")
    assert reading["busy_cores"] == 20.0 and reading["busy_window_s"] >= 60
    assert reading["load_1m"] == 3.0
    assert set(reasons(reading)) == {"cpu"}


def test_idle_cores_with_a_high_load_shut_on_load_alone(planted):
    planted.config()
    planted.busy(4.0)
    planted.loads(30.0, 30.0, 30.0)
    assert set(reasons(gate.read("session"))) == {"load"}


def test_cpu_counters_that_do_not_advance_shut_the_gate(planted):
    planted.config()
    (planted.dir / "cpu-stat.json").write_text("[]")
    (planted.root / "stat").write_text("cpu  5 0 0 5 0 0 0 0 0 0\n")
    reading = gate.read("session")
    assert reasons(reading)["cpu"]["reading"] is None


def test_the_servers_p95_is_counted_in_place_of_their_current_use(planted, monkeypatch):
    planted.config()
    planted.busy(10.0)
    states = {"shared": {"host": "h:1", "pid": 9, "cores_now": 1.0, "cores_p95": 11.0, "samples": 20},
              "query": {"host": "h:2", "pid": None, "cores_now": 0.0, "cores_p95": 0.0, "samples": 20}}
    monkeypatch.setattr(gate, "servers", lambda values, table: states)
    reading = gate.read("session")
    assert reading["cpu_demand_cores"] == 20.0 and "cpu" in reasons(reading)
    states["shared"]["cores_p95"] = 5.0
    assert gate.read("session")["cpu_demand_cores"] == 14.0


def test_a_server_p95_is_measured_from_its_process_tree(planted, monkeypatch):
    from gov.resources import machine
    data = planted.config()
    planted.process(900, ticks=0, cmdline="ollama serve")
    planted.process(901, ppid=900, ticks=0, cmdline="ollama runner")
    monkeypatch.setattr(machine, "listener", lambda port: 900 if port == 11434 else None)
    table = machine.processes()
    first = gate.servers(data and configuration.load()["values"], table)
    assert first["shared"]["pid"] == 900 and first["query"]["state"] == "not listening"
    history = json.loads((planted.dir / gate.SERVER_HISTORY).read_text())
    history["shared"]["last"][0] -= 10  # ten seconds ago, at 0 ticks
    (planted.dir / gate.SERVER_HISTORY).write_text(json.dumps(history))
    planted.process(901, ppid=900, ticks=machine.TICKS * 20, cmdline="ollama runner")  # 20 s of CPU in 10 s
    second = gate.servers(configuration.load()["values"], machine.processes())
    assert 1.9 <= second["shared"]["cores_now"] <= 2.1 and second["shared"]["cores_p95"] >= 1.9


# --- S6, failure 6: memory --------------------------------------------------------------------------------------------

def test_memory_opens_with_room_for_every_running_session_and_the_new_one(planted):
    planted.config(floor_bytes=3 * GIB, working_size_bytes=2 * GIB)
    for pid in (11, 12):
        planted.process(pid, rss=GIB)
        planted.session(pid)
    planted.memory(available=6 * GIB)  # have 6 + 2 = 8 < need 3 + 2*2 + 2 = 9
    assert "memory" in reasons(gate.read("session"))
    planted.memory(available=7 * GIB)  # have 9 = need 9
    assert "memory" not in reasons(gate.read("session"))


def test_nothing_is_reserved_for_a_run_that_has_not_started(planted):
    planted.config(floor_bytes=3 * GIB, working_size_bytes=2 * GIB, verification_peak_bytes=7 * GIB)
    planted.memory(available=5 * GIB)
    assert gate.read("session")["memory"]["need_bytes"] == 5 * GIB


def test_a_session_using_more_than_its_working_size_counts_at_what_it_uses(planted):
    planted.config(floor_bytes=GIB, working_size_bytes=GIB)
    planted.process(21, rss=4 * GIB)
    planted.session(21)
    planted.memory(available=2 * GIB)
    reading = gate.read("session")
    assert reading["memory"] == {"have_bytes": 6 * GIB, "need_bytes": 6 * GIB}


def test_a_worker_inside_its_leads_tree_is_charged_once(planted):
    planted.config(floor_bytes=GIB, working_size_bytes=GIB // 2)
    planted.process(30, rss=GIB)                 # the lead
    planted.process(31, ppid=30, rss=GIB)        # the lead's own helper
    planted.process(40, ppid=30, rss=2 * GIB)    # a worker the lead started, its own session
    planted.process(41, ppid=40, rss=GIB)        # the worker's test run
    planted.session(30, role="orchestrator")
    planted.session(40, role="engineer")
    held = {s["pid"]: s["memory_bytes"] for s in gate.read(None)["sessions"]}
    assert held == {30: 2 * GIB, 40: 3 * GIB}


@pytest.mark.parametrize("kind,peak_key", [("test", "verification_peak_bytes"), ("rebuild", "rebuild_peak_bytes")])
def test_a_heavy_job_asks_for_room_for_its_own_peak(planted, kind, peak_key):
    planted.config(floor_bytes=GIB, working_size_bytes=GIB, verification_peak_bytes=5 * GIB,
                   rebuild_peak_bytes=3 * GIB)
    reading = gate.read(kind)
    assert reading["memory"]["need_bytes"] == GIB + reading["config"]["values"][peak_key]


def test_unreadable_memory_shuts_the_gate(planted, monkeypatch):
    planted.config()
    monkeypatch.setenv("GOV_RESOURCES_MEMINFO", str(planted.root / "missing"))
    assert reasons(gate.read("session"))["memory"]["reading"] is None


# --- S4, failure 3: disk and inodes ---------------------------------------------------------------------------------

def test_the_disk_floor_and_the_inode_floor_each_shut_the_gate(planted):
    st = os.statvfs(planted.home)
    planted.config(disk_floor_bytes=st.f_bavail * st.f_frsize * 10 + GIB)
    assert set(reasons(gate.read("session"))) == {"disk"}
    planted.config(inode_floor=st.f_favail * 10 + 10)
    assert set(reasons(gate.read("session"))) == {"inodes"}


def test_check_disk_is_one_function_a_close_can_call(planted):
    planted.config()
    assert gate.check_disk()["open"]
    planted.config(inode_floor=10 ** 15)
    shut = gate.check_disk()
    assert not shut["open"] and [r["condition"] for r in shut["reasons"]] == ["inodes"]


def test_an_unreadable_disk_shuts_both(planted):
    planted.config(disk_path=str(planted.root / "no-such-disk"))
    assert {"disk", "inodes"} <= set(reasons(gate.read("session")))


# --- the reading names its reasons ----------------------------------------------------------------------------------

def test_describe_names_the_condition_the_reading_and_the_threshold():
    text = gate.describe({"condition": "load", "reading": 25.0, "threshold": 20})
    assert text == "load 25.0 against the threshold 20"
    assert "cannot be read" in gate.describe({"condition": "disk", "reading": None, "threshold": 5, "why": "x"})
