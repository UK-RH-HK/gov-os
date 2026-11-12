"""Unit tests for the gate's configuration, readings, registry and conditions (W2-20 S1-S8, S10, S12-S14, failure
lines 2-6; the interface of the designer's README).

Planted machines only (the ``planted`` fixture): a temporary HOME, planted readings and process table."""
from __future__ import annotations

import datetime
import json

import pytest

from gov.cli.errors import GovError
from gov.resources import config as configuration
from gov.resources import gate, machine, registry
import gov.resources

GIB = 1024 ** 3
CONDITIONS = {"memory", "load", "cpu", "disk", "inodes", "config", "gpu"}


def reasons(reading):
    found = reading["gate"]["reasons"]
    assert {r["condition"] for r in found} <= CONDITIONS, found
    return {reason["condition"]: reason for reason in found}


def config_keys(reading):
    return [r["key"] for r in reading["gate"]["reasons"] if r["condition"] == "config"]


# --- S8: the one configuration file ---------------------------------------------------------------------------------

def test_the_planted_template_opens_the_gate(planted):
    planted.config()
    reading = gate.read(True)
    assert reading["gate"] == {"open": True, "reasons": []}


def test_no_configuration_file_shuts_the_gate_naming_it(planted):
    reading = gate.read(True)
    assert not reading["gate"]["open"] and "gate.json" in config_keys(reading)


def test_a_file_that_is_not_json_shuts_the_gate_naming_it(planted):
    planted.dir.mkdir(parents=True)
    (planted.dir / "gate.json").write_text("{not json")
    assert "gate.json" in config_keys(gate.read(True))


@pytest.mark.parametrize("key", list(configuration.VALUES) + [configuration.SERVERS_KEY])
def test_each_missing_value_shuts_the_gate_naming_it(planted, key):
    planted.config(**{key: None})
    assert key in config_keys(gate.read(True))


@pytest.mark.parametrize("key,bad", [("memory_floor_bytes", -1), ("memory_floor_bytes", "three"), ("heavy_slots", 0),
                                     ("gpu_margin", -0.1), ("rebuild_peak_bytes", 1.5), ("oom_floor_bytes", True),
                                     ("gpu_shares", {"embedder_mib": 1}), ("verification_lock", 3),
                                     ("thread_budget", 0)])
def test_a_malformed_value_shuts_the_gate_naming_it_with_its_raw_value(planted, key, bad):
    planted.config(**{key: bad})
    [reason] = [r for r in gate.read(True)["gate"]["reasons"] if r["condition"] == "config"]
    assert reason["key"] == key and reason["reading"] == bad and reason["threshold"] is None


@pytest.mark.parametrize("change", [lambda e: e.pop("date"), lambda e: e.update(date="2026-13-01"),
                                    lambda e: e.update(date="yesterday"), lambda e: e.update(source=" "),
                                    lambda e: e.pop("source")])
def test_a_value_without_its_date_or_source_is_malformed(planted, change):
    data = planted.config()
    change(data["inode_floor"])
    (planted.dir / "gate.json").write_text(json.dumps(data))
    assert config_keys(gate.read(True)) == ["inode_floor"]


def test_a_bare_value_is_malformed(planted):
    data = planted.config()
    data["memory_floor_bytes"] = 3 * GIB
    (planted.dir / "gate.json").write_text(json.dumps(data))
    [reason] = [r for r in gate.read(True)["gate"]["reasons"] if r["condition"] == "config"]
    assert reason["key"] == "memory_floor_bytes" and reason["reading"] == 3 * GIB


def test_no_old_default_stands_in(planted):
    planted.config(working_size_bytes=None)
    reading = gate.read(True)
    assert reasons(reading)["memory"]["threshold"] is None


@pytest.mark.parametrize("where,bad", [("shared", {"cpus": "x-y", "nice": 10}), ("query", {"cpus": "8-11", "nice": 30}),
                                       ("query", {"cpus": "8-11", "nice": 0, "device": "tpu"})])
def test_a_malformed_servers_entry_shuts_the_gate_naming_it(planted, where, bad):
    data = planted.config()
    data["embedding_servers"][where] = bad
    (planted.dir / "gate.json").write_text(json.dumps(data))
    assert all(key.startswith(f"embedding_servers.{where}.") for key in config_keys(gate.read(True)))
    assert config_keys(gate.read(True))


@pytest.mark.parametrize("days,due", [(8, True), (7, False)])
def test_a_measured_figure_older_than_seven_days_is_due_and_still_counts(planted, days, due):
    data = planted.config()
    today = datetime.date.today()
    for key in configuration.MEASURED:
        data[key]["date"] = today.isoformat()
    data["working_size_bytes"]["date"] = (today - datetime.timedelta(days=days)).isoformat()
    (planted.dir / "gate.json").write_text(json.dumps(data))
    reading = gate.read(True)
    assert reading["due_for_remeasure"] == (["working_size_bytes"] if due else [])
    assert reading["gate"]["open"]


def test_init_config_writes_a_dated_sourced_file_with_the_decided_values_and_never_overwrites(planted):
    written = configuration.init()["config"]
    loaded = configuration.load()
    assert loaded["faults"] == [] and set(configuration.VALUES) <= set(loaded["values"])
    assert written["memory_floor_bytes"]["value"] == 3 * GIB and "DEC-942" in written["memory_floor_bytes"]["source"]
    assert written["disk_floor_bytes"]["value"] == 100 * GIB and written["inode_floor"]["value"] == 10_000_000
    assert written["gpu_margin"]["value"] == 0.10 and "DEC-950" in written["gpu_margin"]["source"]
    for key in configuration.VALUES:
        assert written[key]["date"] and written[key]["source"], key
    before = configuration.path().read_text()
    with pytest.raises(GovError) as refused:
        configuration.init()
    assert refused.value.code == "RESOURCE_CONFIG_EXISTS" and "gate.json" in refused.value.message
    assert configuration.path().read_text() == before


def test_the_template_derives_the_servers_cpus_on_a_smaller_machine():
    data = configuration.template(cpus=list(range(8)))
    assert data["embedding_servers"]["shared"]["cpus"] == "0-7"
    assert "derived" in data["embedding_servers"]["source"]


# --- S1, S3, failure 2: the registry --------------------------------------------------------------------------------

def test_every_live_session_is_read_whichever_repository_started_it(planted):
    planted.config()
    for pid, repo in ((501, "/repo/one"), (502, "/repo/two")):
        planted.process(pid, rss=GIB // 4)
        planted.session(pid, repository=repo, ticket=f"T-{pid}")
    reading = gate.read(False)
    assert sorted((s["repository"], s["ticket"], s["role"], s["live_memory_bytes"]) for s in reading["sessions"]) == [
        ("/repo/one", "T-501", "engineer", GIB // 4), ("/repo/two", "T-502", "engineer", GIB // 4)]
    assert reading["available_memory_bytes"] == 20 * GIB and reading["load_1m"] == 1.0
    assert reading["registry"] == str(planted.dir) and reading["sessions_live_memory_bytes"] == GIB // 2


def test_a_stale_entry_is_cleared_and_does_not_count(planted):
    planted.config()
    planted.process(601)
    planted.session(601)
    planted.session(602)  # no such process
    reading = gate.read(False)
    assert [s["pid"] for s in reading["sessions"]] == [601]
    assert [s["pid"] for s in reading["cleared"]] == [602]
    assert not (planted.dir / "sessions" / "602.json").exists()
    assert gate.read(False)["cleared"] == []


def test_an_unreadable_entry_shuts_the_gate_on_memory(planted):
    planted.config()
    (planted.dir / "sessions").mkdir(parents=True)
    (planted.dir / "sessions" / "77.json").write_text("{not json")
    reading = gate.read(True)
    assert reading["sessions_live_memory_bytes"] is None and reasons(reading)["memory"]["reading"] is None


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
    planted.loads(one, fifteen)
    found = reasons(gate.read(True))
    assert ("load" not in found) is open_
    if not open_:
        assert found["load"]["reading"] == min(one, fifteen) and found["load"]["threshold"] == 20


def test_an_unreadable_load_shuts_the_gate(planted, monkeypatch):
    planted.config()
    monkeypatch.setenv("GOV_RESOURCES_LOADAVG", str(planted.root / "missing"))
    reading = gate.read(True)
    assert reading["load_1m"] is None and reasons(reading)["load"]["reading"] is None


# --- S2, S12: busy cores and the servers' p95 ----------------------------------------------------------------------

def test_the_cpu_condition_is_busy_cores_plus_both_servers_p95_below_nproc(planted):
    planted.config()
    planted.busy(10.0)
    planted.servers(6.0, 3.0)
    reading = gate.read(True)
    assert reading["busy_cores_1m"] == 10.0 and reading["embedding_cpu_p95"] == {"shared": 6.0, "query": 3.0}
    assert "cpu" not in reasons(reading)
    planted.servers(6.0, 4.0)  # equal shuts
    found = reasons(gate.read(True))
    assert found["cpu"]["reading"] == 20.0 and found["cpu"]["threshold"] == 20


def test_busy_cores_and_load_are_judged_each_on_its_own(planted):
    planted.config()
    planted.busy(25.0)
    assert set(reasons(gate.read(True))) == {"cpu"}
    planted.busy(1.0)
    planted.loads(30.0, 30.0)
    assert set(reasons(gate.read(True))) == {"load"}


@pytest.mark.parametrize("variable,value", [("GOV_RESOURCES_BUSY_CORES", "lots"),
                                            ("GOV_RESOURCES_EMBEDDING_CPU", "{\"shared\": 1}"),
                                            ("GOV_RESOURCES_EMBEDDING_CPU", "not json")])
def test_an_unreadable_cpu_reading_shuts_the_gate(planted, monkeypatch, variable, value):
    planted.config()
    monkeypatch.setenv(variable, value)
    assert reasons(gate.read(True))["cpu"]["reading"] is None


def test_the_planted_readings_may_be_files_as_meminfo_is(planted, monkeypatch):
    planted.config()
    files = {"GOV_RESOURCES_BUSY_CORES": "1.25\n", "GOV_RESOURCES_EMBEDDING_CPU": '{"shared": 2.0, "query": 1.0}',
             "GOV_RESOURCES_DISK": '{"free_bytes": 200000000000, "free_inodes": 20000000}'}
    for name, text in files.items():
        path = planted.root / name.lower()
        path.write_text(text)
        monkeypatch.setenv(name, str(path))
    reading = gate.read(True)
    assert reading["busy_cores_1m"] == 1.25 and reading["embedding_cpu_p95"] == {"shared": 2.0, "query": 1.0}
    assert reading["disk"] == {"free_bytes": 200000000000, "free_inodes": 20000000} and reading["gate"]["open"]
    for name in files:
        monkeypatch.setenv(name, str(planted.root / "no-such-file"))
    shut = reasons(gate.read(True))
    assert shut["cpu"]["reading"] is None and shut["disk"]["reading"] is None and shut["inodes"]["reading"] is None


def test_the_own_busy_sampling_counts_the_last_minute(planted, monkeypatch):
    import time
    planted.config()
    monkeypatch.delenv("GOV_RESOURCES_BUSY_CORES")
    stat = planted.root / "stat"
    stat.write_text("cpu  7000 0 0 13000 0 0 0 0\n")  # 6000 busy of 12000 since the sample below
    monkeypatch.setenv("GOV_RESOURCES_STAT", str(stat))
    planted.dir.mkdir(parents=True, exist_ok=True)
    (planted.dir / machine.CPU_HISTORY).write_text(json.dumps([{"t": time.time() - 61, "busy": 1000,
                                                                 "total": 8000}]))
    assert gate.read(True)["busy_cores_1m"] == 10.0


def test_a_servers_p95_is_measured_from_its_process_tree(planted, monkeypatch):
    planted.config()
    monkeypatch.delenv("GOV_RESOURCES_EMBEDDING_CPU")
    planted.process(900, ticks=0, cmdline="ollama serve")
    planted.process(901, ppid=900, ticks=0, cmdline="ollama runner")
    monkeypatch.setattr(machine, "listener", lambda port, table=None: 900 if port == 11434 else None)
    values = configuration.load()["values"]
    first, why = machine.embedding_cpu(planted.dir, values)
    assert why is None and first == {"shared": 0.0, "query": 0.0}
    path = planted.dir / machine.SERVER_HISTORY
    lines = [json.loads(line) for line in path.read_text().splitlines()]
    assert lines and all(line["server"] == "shared" and line["pid"] == 900 for line in lines)
    # the kept samples moved ten seconds back, at 0 s of CPU
    path.write_text("".join(json.dumps({**line, "time": line["time"] - 10}) + "\n" for line in lines))
    planted.process(901, ppid=900, ticks=machine.TICKS * 20, cmdline="ollama runner")  # 20 s of CPU in 10 s
    second, _ = machine.embedding_cpu(planted.dir, values)
    assert 1.9 <= second["shared"] <= 2.1 and second["query"] == 0.0


# --- S6, failure 6: memory --------------------------------------------------------------------------------------------

def test_memory_needs_the_floor_and_a_working_size_for_each_running_session_and_the_new_one(planted):
    planted.config(memory_floor_bytes=3 * GIB, working_size_bytes=2 * GIB)
    for pid in (11, 12):
        planted.process(pid, rss=GIB)
        planted.session(pid)
    planted.memory(available=6 * GIB)  # have 6 + 2 = 8 < need 3 + 2 * 3 = 9
    found = reasons(gate.read(True))
    assert found["memory"]["reading"] == 8 * GIB and found["memory"]["threshold"] == 9 * GIB
    planted.memory(available=7 * GIB)  # equal opens
    assert "memory" not in reasons(gate.read(True))


def test_nothing_is_reserved_for_a_run_that_has_not_started(planted):
    planted.config(memory_floor_bytes=3 * GIB, working_size_bytes=2 * GIB, verification_peak_bytes=50 * GIB,
                   rebuild_peak_bytes=50 * GIB)
    planted.memory(available=5 * GIB)
    assert "memory" not in reasons(gate.read(True))


def test_a_worker_inside_its_leads_tree_is_charged_once(planted):
    planted.config()
    planted.process(30, rss=GIB)                 # the lead
    planted.process(31, ppid=30, rss=GIB)        # the lead's own helper
    planted.process(40, ppid=30, rss=2 * GIB)    # a worker the lead started, its own session
    planted.process(41, ppid=40, rss=GIB)        # the worker's test run
    planted.session(30, role="orchestrator")
    planted.session(40, role="engineer")
    reading = gate.read(False)
    assert {s["pid"]: s["live_memory_bytes"] for s in reading["sessions"]} == {30: 2 * GIB, 40: 3 * GIB}
    assert reading["sessions_live_memory_bytes"] == 5 * GIB


def test_unreadable_memory_shuts_the_gate(planted, monkeypatch):
    planted.config()
    monkeypatch.setenv("GOV_RESOURCES_MEMINFO", str(planted.root / "missing"))
    reading = gate.read(True)
    assert reading["available_memory_bytes"] is None and reasons(reading)["memory"]["reading"] is None


def test_no_ceiling_on_sessions(planted):
    planted.config(memory_floor_bytes=0, working_size_bytes=0)
    for pid in range(100, 140):
        planted.process(pid)
        planted.session(pid)
    assert gate.read(True)["gate"]["open"]


# --- S4, failure 3: disk and inodes ---------------------------------------------------------------------------------

@pytest.mark.parametrize("free,inodes,shut", [(100 * GIB, 10_000_000, set()), (100 * GIB - 1, 10_000_000, {"disk"}),
                                              (100 * GIB, 9_999_999, {"inodes"}),
                                              (GIB, 5, {"disk", "inodes"})])
def test_the_disk_floor_and_the_inode_floor_each_shut_the_gate(planted, free, inodes, shut):
    planted.config()
    planted.disk(free, inodes)
    assert set(reasons(gate.read(True))) == shut
    closing = gov.resources.check_disk()
    assert closing["open"] is (not shut) and {r["condition"] for r in closing["reasons"]} == shut
    assert (closing["free_bytes"], closing["free_inodes"]) == (free, inodes)


def test_check_disk_reads_the_env_it_is_given(planted, tmp_path):
    planted.config()
    other = tmp_path / "other-home"
    env = {"HOME": str(other), "GOV_RESOURCES_DISK": json.dumps({"free_bytes": 1, "free_inodes": 1})}
    shut = gov.resources.check_disk(env)
    assert not shut["open"] and {r["threshold"] for r in shut["reasons"]} == {None}  # that HOME has no file


@pytest.mark.parametrize("value", ["{}", "nope", "{\"free_bytes\": -1, \"free_inodes\": 3}"])
def test_an_unreadable_disk_shuts_both_for_a_start_and_a_close(planted, monkeypatch, value):
    planted.config()
    monkeypatch.setenv("GOV_RESOURCES_DISK", value)
    reading = gate.read(True)
    assert reading["disk"] is None and {"disk", "inodes"} <= set(reasons(reading))
    assert not gov.resources.check_disk()["open"]


def test_without_a_planted_disk_the_home_disk_is_read(planted, monkeypatch):
    planted.config()
    monkeypatch.delenv("GOV_RESOURCES_DISK")
    disk = gate.read(True)["disk"]
    assert disk["free_bytes"] > 0 and disk["free_inodes"] > 0


# --- S10, S13, S14: the GPU -----------------------------------------------------------------------------------------

def test_the_reading_measures_the_gpu_and_its_processes_once(planted):
    planted.config()
    calls = planted.smi(gpu="8192, 5000, 3192, 37", apps="5001, /usr/bin/ollama, 3000\n5002, python, 1500\n"
                                                         "5003, python, 500")
    planted.process(5001, cmdline="/usr/local/bin/ollama runner --model x")
    planted.process(5002, cmdline="python rerank_service.py")
    planted.process(5003, cmdline="python train.py")
    gpu = gate.read(False)["gpu"]
    assert gpu["available"] is True and gpu["memory_used_mib"] == 5000 and gpu["memory_total_mib"] == 8192
    assert gpu["utilisation_pct"] == 37.0
    assert gpu["processes"] == [{"pid": 5001, "kind": "embedder", "used_mib": 3000},
                                {"pid": 5002, "kind": "reranker", "used_mib": 1500},
                                {"pid": 5003, "kind": "other", "used_mib": 500}]
    asked = [call for call in calls() if any(a.startswith("--query-gpu") for a in call)]
    assert len(asked) == 1 and "--query-gpu=memory.total,memory.used,memory.free,utilization.gpu" in asked[0]


@pytest.mark.parametrize("setup", ["none", "no-gpu", "broken"])
def test_no_gpu_or_an_unreadable_one_is_named_never_an_error(planted, setup):
    planted.config()
    if setup == "no-gpu":
        planted.smi(exit_code=6, say="No devices were found")
    elif setup == "broken":
        planted.smi(exit_code=9, say="NVIDIA-SMI has failed")
    reading = gate.read(False)
    assert reading["gpu"]["available"] is False and reading["gpu"]["reason"] and reading["gate"]["open"]
    shut = gate.read(True, gpu_need_mib=100)
    found = reasons(shut)
    assert found["gpu"]["reading"] is None and set(found) == {"gpu"}


@pytest.mark.parametrize("free,open_", [(1101, True), (1099, False)])
def test_a_need_opens_only_with_the_need_plus_the_margin_on_one_gpu(planted, free, open_):
    planted.config(gpu_shares={"value": {"embedder_mib": 0, "reranker_mib": 0}, "date": "2026-11-09", "source": "t"})
    planted.smi(gpu=f"8000, {8000 - free}, {free}, 5")
    reading = gate.read(True, gpu_need_mib=1000)
    assert ("gpu" not in reasons(reading)) is open_ and reading["gpu_room_mib"] == free
    if not open_:
        assert reasons(reading)["gpu"]["reading"] == 1099 and reasons(reading)["gpu"]["threshold"] == 1100


def test_room_only_across_two_gpus_shuts(planted):
    planted.config(gpu_shares={"value": {"embedder_mib": 0, "reranker_mib": 0}, "date": "2026-11-09", "source": "t"})
    planted.smi(gpu="8000, 7400, 600, 5\n8000, 7400, 600, 5")
    assert "gpu" in reasons(gate.read(True, gpu_need_mib=1000))
    planted.smi(gpu="8000, 7400, 600, 5\n8000, 6000, 2000, 5")
    assert "gpu" not in reasons(gate.read(True, gpu_need_mib=1000))


def test_a_start_check_with_no_need_never_runs_nvidia_smi(planted):
    planted.config()
    calls = planted.smi()
    reading = gate.read(True)
    assert calls() == [] and "gpu" not in reading and reading["gate"]["open"]


@pytest.mark.parametrize("kind,apps,open_", [
    ("embedder", "", True),                         # an embedder keeps nothing back
    ("reranker", "", False),                        # the embedder's unused share is kept: 4000 - 3000 < 1100
    ("reranker", "5001, ollama, 3000", True),       # the embedder loaded: its share is used
    ("other", "5001, ollama, 3000", False),         # the reranker's 2000 still kept: 4000 - 2000 < 2200
    ("other", "5001, ollama, 3000\n5002, rerank, 2000", True),
])
def test_a_job_that_would_push_the_embedder_off_waits_and_the_room_is_stated(planted, kind, apps, open_):
    planted.config(gpu_shares={"value": {"embedder_mib": 3000, "reranker_mib": 2000}, "date": "2026-11-09",
                               "source": "t"})
    planted.process(5001, cmdline="/opt/ollama/bin/ollama runner")
    planted.process(5002, cmdline="python rerank.py")
    planted.smi(gpu="8000, 4000, 4000, 20", apps=apps)
    need = 2000 if kind == "other" else 1000
    reading = gate.read(True, gpu_need_mib=need, gpu_kind=kind)
    assert ("gpu" not in reasons(reading)) is open_
    assert isinstance(reading["gpu_room_mib"], int)


def test_per_process_memory_that_cannot_be_read_holds_its_share_and_only_free_memory_decides(planted):
    """WSL's nvidia-smi reports each process's memory as [N/A] (ACT-GATE-CONFIG-1's rehearsal)."""
    planted.config()  # the template: embedder 3584 MiB, reranker 3584 MiB, margin 10 %
    planted.process(5001, cmdline="/usr/local/bin/ollama runner")
    planted.process(5002, cmdline="python /srv/rerank_service.py")
    planted.smi(gpu="16303, 6800, 9503, 12", apps="5001, /ollama, [N/A]\n5002, /python3, [N/A]")
    reading = gate.read(True, gpu_need_mib=1024)
    assert reading["gate"]["open"] and reading["gpu_room_mib"] == 9503
    assert [p["used_mib"] for p in reading["gpu"]["processes"]] == [None, None]
    shut = gate.read(True, gpu_need_mib=9000)  # 9900 > 9503 free: the free memory says so
    assert reasons(shut)["gpu"]["reading"] == 9503


def test_the_gpu_kind_is_read_from_the_command_line():
    assert machine.gpu_kind("/home/u/.local/ollama/bin/ollama serve") == "embedder"
    assert machine.gpu_kind("ollama_llama_server --model x") == "embedder"
    assert machine.gpu_kind("python -m reranker.serve") == "reranker"
    assert machine.gpu_kind("python embed_things.py") == "other"


# --- the reasons in words -------------------------------------------------------------------------------------------

def test_describe_names_the_condition_its_reading_and_its_limit():
    assert gate.describe({"condition": "memory", "reading": 1073741824, "threshold": 4294967296}) == \
        "memory: reading 1073741824, limit 4294967296"
    assert gate.describe({"condition": "load", "reading": 25.0, "threshold": 20}) == "load: reading 25.0, limit 20"
    assert "heavy_slots" in gate.describe({"condition": "config", "reading": None, "threshold": None,
                                           "key": "heavy_slots", "why": "heavy_slots: missing"})
