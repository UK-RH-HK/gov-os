"""Unit tests of the GPU backstop (W2-157; Interface L1-L9, KPI S1-S5, F1-F4).

Everything is planted under ``tmp_path``: the job's own process groups (children started with
``start_new_session=True``), a stand-in ``nvidia-smi`` first on PATH, stand-in HTTP servers on free ports (never 11434 or
11435), planted logs, a planted HOME and project. Teardown sends SIGCONT then SIGKILL to the test's own groups. Nothing
is run against a real group, the real GPU, the real HOME or the real embedding servers.
"""
from __future__ import annotations

import inspect
import json
import os
import shlex
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.resources import backstop, config as configuration  # noqa: E402

REAL_SLEEP = time.sleep  # time.sleep is never replaced (the backstop's _pause is); waits on a process state use it
MARK = "w2157-planted"  # argv[1] of every planted process: a leftover is found by it after a run
SLEEPER = f"import time; time.sleep(120)  # {MARK}"

SMI = """#!{python}
import os, sys
seq = os.environ["SMI_SEQ"]
count = os.environ["SMI_COUNT"]
n = int(open(count).read() or 0) if os.path.exists(count) else 0
open(count, "w").write(str(n + 1))
open(os.environ["SMI_ARGS"], "a").write(" ".join(sys.argv[1:]) + "\\n")
lines = open(seq).read().splitlines()
line = lines[min(n, len(lines) - 1)]
if line.startswith("exit "):
    sys.stderr.write("boom")
    sys.exit(int(line.split()[1]))
print(line)
"""


class Rig:
    def __init__(self, tmp_path: Path, monkeypatch):
        self.tmp, self.mp = tmp_path, monkeypatch
        self.home = tmp_path / "home"
        self.root = tmp_path / "project"
        self.bin = tmp_path / "bin"
        for folder in (self.home, self.root, self.bin):
            folder.mkdir()
        self.groups: list[subprocess.Popen] = []
        self.servers: list[HTTPServer] = []
        self.env = {"HOME": str(self.home), "PATH": f"{self.bin}:/usr/bin:/bin"}
        monkeypatch.setenv("HOME", str(self.home))
        monkeypatch.setenv("PATH", self.env["PATH"])
        self.sleeps: list[float] = []  # only the backstop's own pause between polls is replaced, never time.sleep
        self.mp.setattr(backstop, "_pause", self.sleeps.append)
        self.log = self.home / ".gov-os" / "machine" / "gpu-backstop.log"
        self.inbox = self.root / ".gov-runtime" / "dispatch" / "inbox"

    # the stand-in nvidia-smi: one reading line per call, the last one repeating
    def smi(self, *lines: str):
        program = self.bin / "nvidia-smi"
        program.write_text(SMI.format(python=sys.executable))
        program.chmod(0o755)
        (self.tmp / "seq").write_text("\n".join(lines) + "\n")
        for name, file in (("SMI_SEQ", "seq"), ("SMI_COUNT", "count"), ("SMI_ARGS", "args")):
            self.mp.setenv(name, str(self.tmp / file))
            self.env[name] = str(self.tmp / file)
        (self.tmp / "count").unlink(missing_ok=True)

    def smi_calls(self) -> int:
        count = self.tmp / "count"
        return int(count.read_text()) if count.exists() else 0

    def smi_args(self) -> list[str]:
        return (self.tmp / "args").read_text().splitlines()

    # the configuration
    def config(self, limit=15872, every=5, embedders=(), **changes):
        entry = lambda value: {"value": value, "date": "2026-11-12", "source": "test"}  # noqa: E731
        data = {"gpu_backstop_limit_mib": entry(limit), "gpu_backstop_every_s": entry(every),
                "gpu_backstop_embedders": entry([{"port": p, "log": str(l)} for p, l in embedders])}
        for key, value in changes.items():
            if value is None:
                data.pop(key, None)
            else:
                data[key] = value
        folder = self.home / ".gov-os" / "machine"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "gate.json").write_text(json.dumps(data))
        return data

    # the job's groups: every one is registered here and reaped by close(), whatever the test did (DEC-1144 (2))
    def spawn(self, argv, **kwargs) -> subprocess.Popen:
        child = subprocess.Popen(argv, start_new_session=True, **kwargs)  # its group id is its pid
        self.groups.append(child)
        return child

    def job(self) -> int:
        return os.getpgid(self.spawn([sys.executable, "-c", SLEEPER, MARK]).pid)

    def short_job(self) -> int:
        child = self.spawn([sys.executable, "-c", "pass", MARK])
        pgid = os.getpgid(child.pid) if child.poll() is None else child.pid
        child.wait()
        return pgid

    def zombie(self) -> int:
        """A group whose only member has exited and is not reaped (a zombie): signal 0 still reaches it."""
        child = self.spawn([sys.executable, "-c", "pass", MARK])
        self.wait_state(child.pid, "Z")
        return child.pid

    def wait_state(self, pid: int, wanted: str, seconds: float = 20):
        deadline = time.monotonic() + seconds
        while self.state(pid) != wanted and time.monotonic() < deadline:
            REAL_SLEEP(0.01)
        assert self.state(pid) == wanted, f"process {pid} never reached state {wanted} (is {self.state(pid)})"

    @classmethod
    def stopped_state(cls, pid: int, seconds: float = 20) -> str:
        """The state of ``pid`` once a SIGSTOP sent to it has taken effect: the signal is acted on when the process next
        runs, so under load /proc still shows R for a while after killpg returned. Gives up (returns the state it
        has) after ``seconds``, so an assertion on 'T' still fails when the process was never stopped."""
        deadline = time.monotonic() + seconds
        while cls.state(pid) != "T" and time.monotonic() < deadline:
            REAL_SLEEP(0.01)
        return cls.state(pid)

    @staticmethod
    def members(group: int) -> dict[int, str]:
        """pid -> state of every process now in the process group ``group``."""
        found = {}
        for name in os.listdir("/proc"):
            if name.isdigit():
                try:
                    if os.getpgid(int(name)) == group:
                        found[int(name)] = Rig.state(int(name))
                except OSError:
                    pass
        return found

    @staticmethod
    def state(pid: int) -> str:
        try:
            lines = Path(f"/proc/{pid}/status").read_text().splitlines()
        except OSError:
            return "gone"
        for line in lines:
            if line.startswith("State:"):
                return line.split()[1]
        return "?"

    # a stand-in embedder: /api/ps answers the planted models
    def server(self, models) -> int:
        answer = json.dumps({"models": models}).encode() if models is not None else b"not json"

        class Handler(BaseHandler):
            body = answer

        server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.servers.append(server)
        return server.server_address[1]

    def close(self):
        """Every group the test planted gets SIGCONT then SIGKILL and every child is waited for (reaped), the servers
        stop after; one step failing never skips the others. A group id is its leader's pid (start_new_session), and
        the id cannot be reused while a member of the group lives, so a group left by a reaped leader is still ours."""
        try:
            for child in self.groups:
                for sig in (signal.SIGCONT, signal.SIGKILL):
                    try:
                        os.killpg(child.pid, sig)
                    except (ProcessLookupError, PermissionError):
                        pass
            for child in self.groups:
                try:
                    child.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    pass
        finally:
            for server in self.servers:
                try:
                    server.shutdown()
                    server.server_close()
                except OSError:
                    pass


class BaseHandler(BaseHTTPRequestHandler):
    body = b""

    def do_GET(self):
        if self.path != "/api/ps":
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, *args):
        pass


@pytest.fixture
def rig(tmp_path, monkeypatch):
    planted = Rig(tmp_path, monkeypatch)
    try:
        yield planted
    finally:
        planted.close()


# ---- S1: the limit ----------------------------------------------------------------------------------------------

def test_s1_below_then_above_the_limit_pauses_at_the_second_reading(rig):
    rig.smi("15800, 24000", "15900, 24000")
    rig.config()
    job = rig.job()
    result = backstop.watch([job], rig.root, rig.env, max_polls=5)
    assert result["tripped"] is True and result["paused"] == [job]
    assert rig.smi_calls() == 2  # the first reading did not trip, the second did
    assert rig.stopped_state(rig.groups[0].pid) == "T"
    assert result["reading"] == {"used_mib": 15900, "total_mib": 24000}
    assert "15900" in result["reason"] and "15872" in result["reason"]
    assert rig.sleeps == [5]
    text = rig.log.read_text()
    assert "TRIP:" in text and "reading 15900/24000 MiB" in text and f"paused groups {job}" in text


def test_s1_the_query_is_exactly_the_interface_line(rig):
    rig.smi("100, 24000")
    rig.config()
    result = backstop.watch([rig.short_job()], rig.root, rig.env, max_polls=4)
    assert result["tripped"] is False and rig.smi_calls() == 0  # an ended group: no reading is made for nothing
    rig.smi("15873, 24000")
    backstop.watch([rig.job()], rig.root, rig.env, max_polls=4)
    assert rig.smi_args() == ["--query-gpu=memory.used,memory.total --format=csv,noheader,nounits"]


def test_s1_the_limit_is_exclusive(rig):
    rig.smi("15872, 24000", "15873, 24000")
    rig.config()
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=5)
    assert rig.smi_calls() == 2 and result["reading"]["used_mib"] == 15873


def test_s1_the_limit_and_period_are_the_files(rig):
    rig.smi("1500, 24000", "1501, 24000")
    rig.config(limit=1500, every=7)
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=5)
    assert result["tripped"] and rig.sleeps == [7] and result["reading"]["used_mib"] == 1501
    assert "limit 1500 MiB; every 7 s" in rig.log.read_text()


@pytest.mark.parametrize("key", ["gpu_backstop_limit_mib", "gpu_backstop_every_s", "gpu_backstop_embedders"])
def test_s1_a_missing_key_refuses_to_start_naming_it(rig, key):
    rig.smi("1, 24000")
    rig.config(**{key: None})
    job = rig.job()
    with pytest.raises(GovError) as error:
        backstop.watch([job], rig.root, rig.env, max_polls=4)
    assert error.value.code == "RESOURCE_CONFIG_INVALID" and error.value.exit_code == 1
    assert key in error.value.message and [f["key"] for f in error.value.details["faults"]] == [key]
    assert not rig.log.exists() and not rig.inbox.exists() and rig.smi_calls() == 0
    assert rig.state(rig.groups[0].pid) != "T"


@pytest.mark.parametrize("entry", [
    {"value": 0, "date": "2026-11-12", "source": "x"},
    {"value": "15872", "date": "2026-11-12", "source": "x"},
    {"value": True, "date": "2026-11-12", "source": "x"},
    {"value": 15872, "source": "x"},
    {"value": 15872, "date": "yesterday", "source": "x"},
    {"value": 15872, "date": "2026-11-12", "source": " "},
    {"value": 15872, "date": "2026-11-12"},
    15872,
])
def test_s1_a_malformed_limit_refuses_to_start(rig, entry):
    rig.config(gpu_backstop_limit_mib=entry)
    with pytest.raises(GovError) as error:
        backstop.watch([rig.job()], rig.root, rig.env, max_polls=4)
    assert error.value.code == "RESOURCE_CONFIG_INVALID" and "gpu_backstop_limit_mib" in error.value.message


@pytest.mark.parametrize("value", [0, -1, "5", None, True])
def test_a_malformed_period_refuses_to_start(rig, value):
    rig.config(gpu_backstop_every_s={"value": value, "date": "2026-11-12", "source": "x"})
    with pytest.raises(GovError) as error:
        backstop.watch([rig.job()], rig.root, rig.env, max_polls=4)
    assert "gpu_backstop_every_s" in error.value.message


@pytest.mark.parametrize("value", [
    "x", [{"port": 0, "log": "/a"}], [{"port": 65536, "log": "/a"}], [{"port": "1", "log": "/a"}],
    [{"port": 5, "log": "relative"}], [{"port": 5}], [{"log": "/a"}], [5], [{"port": 5, "log": "/a", "x": 1}],
])
def test_a_malformed_embedder_list_refuses_to_start(rig, value):
    rig.config(gpu_backstop_embedders={"value": value, "date": "2026-11-12", "source": "x"})
    with pytest.raises(GovError) as error:
        backstop.watch([rig.job()], rig.root, rig.env, max_polls=4)
    assert "gpu_backstop_embedders" in error.value.message


def test_a_missing_file_and_a_file_not_json_refuse_to_start(rig):
    with pytest.raises(GovError) as error:
        backstop.watch([rig.job()], rig.root, rig.env, max_polls=4)
    assert error.value.code == "RESOURCE_CONFIG_INVALID" and "gate.json" in error.value.message
    folder = rig.home / ".gov-os" / "machine"
    folder.mkdir(parents=True)
    (folder / "gate.json").write_text("{not json")
    with pytest.raises(GovError) as error:
        backstop.watch([rig.groups[0].pid], rig.root, rig.env, max_polls=4)
    assert "gate.json" in error.value.message and not rig.log.exists()


def test_the_file_may_hold_every_other_key_or_none(rig):
    """Only --backstop reads the three keys: the other W2-20 keys neither help nor hinder."""
    rig.smi("1, 24000")
    rig.config(memory_floor_bytes={"value": "bad"})
    job = rig.short_job()
    assert backstop.watch([job], rig.root, rig.env, max_polls=4)["tripped"] is False


def test_the_environment_never_sets_the_limit_while_a_job_runs(rig, monkeypatch):
    rig.smi("15900, 24000", "20001, 24000")
    rig.config(limit=20000)
    monkeypatch.setenv("LIMIT", "100")
    rig.env["LIMIT"] = "100"
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=5)
    assert result["reading"]["used_mib"] == 20001 and rig.smi_calls() == 2


# ---- S2: the spill ----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("used,trips", [(24500 - 65, False), (24500 - 64, True), (24500 - 63, True)])
def test_s2_a_reading_within_64_mib_of_the_total_trips(rig, used, trips):
    rig.smi(f"{used}, 24500", "99999, 24500")
    rig.config(limit=30000)
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=4)
    assert result["tripped"] is True
    assert (rig.smi_calls() == 1) is trips
    assert ("spill" in result["reason"]) if trips else True


# ---- S3: the embedders ------------------------------------------------------------------------------------------

def test_s3_a_model_partly_off_the_gpu_trips_it(rig):
    port = rig.server([{"name": "nomic", "size": 1000, "size_vram": 1000},
                       {"name": "mxbai", "size": 1000, "size_vram": 400}])
    rig.smi("100, 24000")
    rig.config(embedders=[(port, rig.tmp / "none.log")])
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=4)
    assert result["tripped"] and f":{port}" in result["reason"] and "mxbai" in result["reason"]
    assert "400/1000" in result["reason"] and "nomic" not in result["reason"]


def test_s3_a_model_wholly_on_the_gpu_does_not_trip(rig):
    port = rig.server([{"name": "nomic", "size": 1000, "size_vram": 1000}])
    rig.smi("100, 24000", "100, 24000", "20000, 24000")
    rig.config(embedders=[(port, rig.tmp / "none.log")])
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=6)
    assert rig.smi_calls() == 3 and "embedder" not in result["reason"]


@pytest.mark.parametrize("models", [None, [], "x"])
def test_s3_no_answer_or_a_malformed_one_is_no_trip(rig, models):
    port = rig.server(models) if models != "x" else rig.server(None)
    rig.smi("100, 24000", "20000, 24000")
    rig.config(embedders=[(port, rig.tmp / "none.log")])
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=5)
    assert rig.smi_calls() == 2 and "limit" in result["reason"]


def test_s3_no_server_at_the_port_is_no_trip(rig):
    free = rig.server([])
    rig.servers[0].shutdown()
    rig.servers[0].server_close()
    rig.smi("100, 24000", "20000, 24000")
    rig.config(embedders=[(free, rig.tmp / "none.log")])
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=5)
    assert rig.smi_calls() == 2 and result["tripped"]


def test_s3_a_partial_offload_line_written_since_the_start_trips_it(rig):
    log = rig.tmp / "serve.log"
    log.write_text("offloaded 1/9 layers to GPU\n")  # before the start: never counts
    rig.smi("100, 24000", "100, 24000", "100, 24000")
    rig.config(embedders=[(9, log)])
    seen = []

    def append_after_first_reading(seconds):
        seen.append(seconds)
        if len(seen) == 1:
            with log.open("a") as handle:
                handle.write("llm: offloaded 33/33 layers to GPU\n")
        if len(seen) == 2:
            with log.open("a") as handle:
                handle.write("llm: offloaded 20/33 layers to GPU\n")

    rig.mp.setattr(backstop, "_pause",append_after_first_reading)
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=6)
    assert result["tripped"] and rig.smi_calls() == 3
    assert str(log) in result["reason"] and "offloaded 20/33 layers to GPU" in result["reason"]


def test_s3_an_equal_offload_never_trips_and_a_missing_log_starts_at_zero(rig):
    log = rig.tmp / "later.log"
    rig.smi("100, 24000", "100, 24000", "20000, 24000")
    rig.config(embedders=[(9, log)])
    calls = []

    def write(seconds):
        calls.append(seconds)
        if len(calls) == 1:
            log.write_text("offloaded 33/33 layers to GPU\n")

    rig.mp.setattr(backstop, "_pause",write)
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=6)
    assert rig.smi_calls() == 3 and "limit" in result["reason"]
    log.write_text("offloaded 33/33 layers to GPU\noffloaded 1/33 layers to GPU\n")


def test_s3_the_limit_comes_before_the_spill_before_the_embedder_before_the_log(rig):
    log = rig.tmp / "serve.log"
    log.write_text("")
    port = rig.server([{"name": "m", "size": 10, "size_vram": 1}])
    def append_a_line(seconds):  # a new line each time: the size grows whatever the earlier calls did
        with log.open("a") as handle:
            handle.write("offloaded 1/2 layers to GPU\n")

    rig.mp.setattr(backstop, "_pause",append_a_line)
    rig.smi("24400, 24500")
    rig.config(embedders=[(port, log)])
    def reason(result):
        assert result["tripped"], "no trip within the bound of 6 polls"
        return result["reason"]

    assert "limit" in reason(backstop.watch([rig.job()], rig.root, rig.env, max_polls=6))
    rig.smi("24450, 24500")
    rig.config(limit=30000, embedders=[(port, log)])
    assert "spill" in reason(backstop.watch([rig.job()], rig.root, rig.env, max_polls=6))
    rig.smi("100, 24500")
    assert f":{port}" in reason(backstop.watch([rig.job()], rig.root, rig.env, max_polls=6))
    rig.config(limit=30000, embedders=[(9, log)])
    assert "offloaded 1/2" in reason(backstop.watch([rig.job()], rig.root, rig.env, max_polls=6))


# ---- the reading that cannot be had -----------------------------------------------------------------------------

@pytest.mark.parametrize("line", ["exit 9", "garbage", "12", "a, b", "", "-5, 100"])
def test_a_reading_that_cannot_be_had_is_logged_and_is_no_trip(rig, line):
    rig.smi(line, line, "15900, 24000")
    rig.config()
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=6)
    assert rig.smi_calls() == 3 and result["tripped"]
    assert rig.log.read_text().count("no GPU reading:") == 2


def test_no_nvidia_smi_on_path_is_no_trip_and_the_watch_goes_on(rig):
    rig.config()
    job = rig.job()
    polls = []

    def kill_after_two(seconds):
        polls.append(seconds)
        if len(polls) == 2:
            rig.groups[0].kill()
            rig.groups[0].wait()

    rig.mp.setattr(backstop, "_pause",kill_after_two)
    result = backstop.watch([job], rig.root, rig.env, max_polls=6)
    assert result["tripped"] is False and "no GPU reading" in rig.log.read_text()
    assert result["reading"] is None


def test_a_trip_without_a_reading_logs_none(rig):
    log = rig.tmp / "serve.log"
    log.write_text("")
    rig.config(embedders=[(9, log)])

    def write(seconds):  # appended: a new line each time, never the same bytes again
        with log.open("a") as handle:
            handle.write("offloaded 1/2 layers to GPU\n")

    rig.mp.setattr(backstop, "_pause",write)
    result = backstop.watch([rig.job()], rig.root, rig.env, max_polls=5)
    assert result["tripped"] and result["reading"] is None and "reading none" in rig.log.read_text()


# ---- S4: only the named groups ----------------------------------------------------------------------------------

def test_s4_only_the_named_group_is_stopped_and_a_same_name_process_runs_on(rig):
    rig.smi("15900, 24000")
    rig.config()
    named = rig.job()
    other = rig.spawn([sys.executable, "-c", SLEEPER, MARK])
    backstop.watch([named], rig.root, rig.env, max_polls=4)
    assert rig.stopped_state(rig.groups[0].pid) == "T" and rig.state(other.pid) != "T"


def test_s4_a_group_that_has_ended_is_skipped_and_named(rig):
    rig.smi("15900, 24000")
    rig.config()
    ended = rig.short_job()
    live = rig.job()
    result = backstop.watch([ended, live], rig.root, rig.env, max_polls=4)
    assert result["paused"] == [live] and result["skipped"] == [ended]
    assert f"skipped (ended) {ended};" in rig.log.read_text()
    item = Path(result["inbox_item"]).read_text()
    assert f"skipped (already ended): {ended}" in item


@pytest.mark.parametrize("huge", [2**31, 2**63, 10**20])
def test_s4_a_number_no_group_can_have_is_skipped_and_named_not_a_crash(rig, huge):
    rig.smi("15900, 24000")
    rig.config()
    live = rig.job()
    result = backstop.watch([huge, live], rig.root, rig.env, max_polls=4)
    assert result["tripped"] and result["paused"] == [live] and result["skipped"] == [huge]
    assert f"skipped (ended) {huge};" in rig.log.read_text()
    assert f"skipped (already ended): {huge}" in Path(result["inbox_item"]).read_text()


def test_s4_only_numbers_no_group_can_have_end_the_watch_at_once(rig):
    rig.smi("15900, 24000")
    rig.config()
    result = backstop.watch([2**40], rig.root, rig.env, max_polls=4)
    assert result["tripped"] is False and result["skipped"] == [2**40] and rig.smi_calls() == 0
    assert "end: every watched group has ended" in rig.log.read_text()


def test_s4_a_job_that_ends_first_ends_the_watch_without_a_trip(rig):
    rig.smi("100, 24000", "100, 24000")
    rig.config()
    job = rig.job()
    polls = []

    def end(seconds):
        polls.append(seconds)
        rig.groups[0].kill()
        rig.groups[0].wait()

    rig.mp.setattr(backstop, "_pause",end)
    result = backstop.watch([job], rig.root, rig.env, max_polls=5)
    assert result == {"tripped": False, "reason": None, "reading": None, "paused": [], "skipped": [],
                      "log": str(rig.log), "inbox_item": None}
    assert f"end: every watched group has ended ({job})" in rig.log.read_text()
    assert not rig.inbox.exists() and rig.smi_calls() == 1


def test_s4_no_live_group_at_start_ends_at_once(rig):
    rig.smi("15900, 24000")
    rig.config()
    gone = rig.short_job()
    result = backstop.watch([gone], rig.root, rig.env, max_polls=4)
    assert result["tripped"] is False and result["skipped"] == [gone] and rig.smi_calls() == 0
    assert "end: every watched group has ended" in rig.log.read_text()


def test_s4_the_inbox_item_names_the_reason_the_groups_and_how_to_resume_or_stop(rig):
    rig.smi("15900, 24000")
    rig.config()
    a, b = rig.job(), rig.job()
    result = backstop.watch([a, b], rig.root, rig.env, max_polls=4)
    path = Path(result["inbox_item"])
    assert path.parent == rig.inbox and path.name.startswith("gpu-backstop-") and path.suffix == ".txt"
    lines = path.read_text().splitlines()
    assert lines[:3] == ["log: gpu-backstop.log", "W2: none", f"status: GPU backstop tripped: {result['reason']}"]
    assert lines[3:5] == [f"paused: {a} {b}", "skipped (already ended): none"]
    for g in (a, b):
        assert f"resume: kill -CONT -- -{g}" in lines
        assert f"stop: kill -TERM -- -{g} && kill -CONT -- -{g}" in lines
    assert [p.name for p in rig.inbox.iterdir()] == [path.name]  # no temporary left behind


def test_s4_the_log_lines_begin_with_a_timestamp_and_the_start_line_names_the_config(rig):
    rig.smi("15900, 24000")
    rig.config(embedders=[(11434, rig.tmp / "a.log"), (11435, rig.tmp / "b.log")])
    job = rig.job()
    backstop.watch([job], rig.root, rig.env, max_polls=4)
    lines = rig.log.read_text().splitlines()
    assert all(time.strptime(line[:19], "%Y-%m-%d %H:%M:%S") for line in lines)
    assert lines[0][20:] == (f"start: limit 15872 MiB; every 5 s; groups {job}; skipped (ended) none; "
                             "embedders 11434 11435")
    assert lines[1][20:].startswith("TRIP: ") and lines[1].endswith(f"paused groups {job}")


def test_s4_the_log_is_appended_never_replaced(rig):
    rig.smi("15900, 24000")
    rig.config()
    rig.log.parent.mkdir(parents=True, exist_ok=True)
    rig.log.write_text("older\n")
    backstop.watch([rig.job()], rig.root, rig.env, max_polls=4)
    assert rig.log.read_text().startswith("older\n")


# ---- S5: nothing else is written --------------------------------------------------------------------------------

def test_s5_a_run_with_no_trip_writes_only_its_log(rig):
    rig.smi("100, 24000")
    rig.config()
    log = rig.tmp / "serve.log"
    log.write_text("offloaded 5/5 layers to GPU\n")
    job = rig.job()
    rig.config(embedders=[(rig.server([{"name": "m", "size": 5, "size_vram": 5}]), log)])
    before = {p: (p.stat().st_mtime_ns, p.stat().st_size) for p in rig.tmp.rglob("*") if p.is_file()}
    calls = []

    def end(seconds):
        calls.append(seconds)
        rig.groups[0].kill()
        rig.groups[0].wait()

    rig.mp.setattr(backstop, "_pause",end)
    backstop.watch([job], rig.root, rig.env, max_polls=5)
    after = {p: (p.stat().st_mtime_ns, p.stat().st_size) for p in rig.tmp.rglob("*") if p.is_file()}
    changed = {p for p in after if before.get(p) != after[p]}
    assert changed - {rig.log, rig.tmp / "count", rig.tmp / "args"} == set()
    assert rig.log in changed and not rig.inbox.exists()
    assert json.loads((rig.home / ".gov-os" / "machine" / "gate.json").read_text())  # still whole


def test_s5_a_trip_writes_the_log_and_one_item_and_the_inbox_folder(rig):
    rig.smi("15900, 24000")
    rig.config()
    assert not rig.inbox.exists()
    backstop.watch([rig.job()], rig.root, rig.env, max_polls=4)
    assert len(list(rig.inbox.iterdir())) == 1 and rig.log.exists()
    assert not (rig.root / ".gov-runtime" / "dispatch" / "other").exists()


def test_the_signals_sent_are_killpg_stop_to_the_live_named_groups_and_nothing_else(rig):
    rig.smi("15900, 24000")
    rig.config()
    live, gone = rig.job(), rig.short_job()
    sent = []
    real = os.killpg
    rig.mp.setattr(backstop.os, "killpg", lambda g, s: (sent.append((g, s)), real(g, s))[1])
    rig.mp.setattr(backstop.os, "kill", lambda *a: pytest.fail("a pid was signalled"))
    backstop.watch([live, gone], rig.root, rig.env, max_polls=4)
    stops = [(g, s) for g, s in sent if s == signal.SIGSTOP]
    assert stops == [(live, signal.SIGSTOP)]
    assert {g for g, _ in sent} <= {live, gone}


# ---- the command (L1) -------------------------------------------------------------------------------------------

def gov(rig, *argv, expect=None):
    done = subprocess.run([sys.executable, "-c", "import sys; from gov.cli.main import main; sys.exit(main(sys.argv[1:]))",
                           "resources", *argv, "--root", str(rig.root)],
                          capture_output=True, text=True, env={**os.environ, **rig.env,
                                                               "PYTHONPATH": str(REPO / "src")}, timeout=60)
    return done


@pytest.mark.parametrize("value", ["abc", "1", "0", "-5", "2.5", ""])
def test_l1_a_value_that_is_not_a_group_id_above_1_is_a_usage_error(rig, value):
    rig.smi("15900, 24000")
    rig.config()
    done = gov(rig, "--backstop", value)
    assert done.returncode == 2 and (value in done.stderr or value == "")
    assert not rig.log.exists() and not rig.inbox.exists() and rig.smi_calls() == 0


@pytest.mark.parametrize("extra", [["--gpu-backstop-limit-mib", "99999"], ["--limit", "5"], ["--every", "1"]])
def test_l1_no_option_sets_the_limit_the_period_or_the_embedders(rig, extra):
    done = gov(rig, "--backstop", str(rig.job()), *extra)
    assert done.returncode == 2 and not rig.log.exists()
    assert rig.state(rig.groups[0].pid) != "T"


def test_l1_backstop_is_one_of_the_exclusive_modes(rig):
    done = gov(rig, "--backstop", "4242", "--check")
    assert done.returncode == 2


def test_l1_the_command_trips_and_prints_the_result(rig):
    rig.smi("15900, 24000")
    rig.config()
    job = rig.job()
    done = gov(rig, "--json", "--backstop", str(job))
    assert done.returncode == 0, done.stderr
    result = json.loads(done.stdout)["result"]
    assert result["tripped"] is True and result["paused"] == [job] and result["log"] == str(rig.log)
    assert set(result) == {"tripped", "reason", "reading", "paused", "skipped", "log", "inbox_item"}
    assert rig.stopped_state(rig.groups[0].pid) == "T"


def test_l1_a_missing_limit_is_exit_1_naming_it(rig):
    rig.smi("15900, 24000")
    rig.config(gpu_backstop_limit_mib=None)
    done = gov(rig, "--json", "--backstop", str(rig.job()))
    assert done.returncode == 1
    error = json.loads(done.stdout)["error"]
    assert error["code"] == "RESOURCE_CONFIG_INVALID" and "gpu_backstop_limit_mib" in error["message"]
    assert rig.state(rig.groups[0].pid) != "T"


def test_l1_several_groups_are_taken(rig):
    rig.smi("15900, 24000")
    rig.config()
    a, b = rig.job(), rig.job()
    result = json.loads(gov(rig, "--json", "--backstop", str(a), str(b)).stdout)["result"]
    assert result["paused"] == [a, b]


# ---- the configuration (L2) -------------------------------------------------------------------------------------

def test_l2_the_template_is_unchanged_and_the_three_keys_are_not_gate_values():
    assert not {"gpu_backstop_limit_mib", "gpu_backstop_every_s", "gpu_backstop_embedders"} & (
        set(configuration.template()) | set(configuration.VALUES) | set(configuration.OPTIONAL))


def test_l2_load_ignores_the_three_keys(rig):
    rig.config()
    loaded = configuration.load(rig.env)
    assert not any("gpu_backstop" in key for key in loaded["values"]) and loaded["faults"]  # W2-20's own keys absent
    rig.config(gpu_backstop_limit_mib={"value": "bad"})
    assert not any("gpu_backstop" in f["key"] for f in configuration.load(rig.env)["faults"])


def test_l2_this_machines_entries_are_the_constant_and_valid():
    entries = configuration.BACKSTOP_ENTRIES
    assert set(entries) == {"gpu_backstop_limit_mib", "gpu_backstop_every_s", "gpu_backstop_embedders"}
    assert entries["gpu_backstop_limit_mib"]["value"] == 15872 and entries["gpu_backstop_every_s"]["value"] == 5
    ports = {e["port"]: e["log"] for e in entries["gpu_backstop_embedders"]["value"]}
    assert ports == {11434: "$HOME/.ollama/serve-11434.log", 11435: "$HOME/.ollama/serve-11435.log"}
    assert all(e["source"] and e["date"] for e in entries.values())


def test_l2_the_values_function_returns_values_and_faults(rig):
    rig.config()
    values, faults = configuration.backstop_values(rig.env)
    assert faults == [] and values["limit_mib"] == 15872 and values["every_s"] == 5 and values["embedders"] == []
    rig.config(gpu_backstop_every_s=None, gpu_backstop_limit_mib=None)
    values, faults = configuration.backstop_values(rig.env)
    assert sorted(f["key"] for f in faults) == ["gpu_backstop_every_s", "gpu_backstop_limit_mib"]


def test_l2_a_planted_file_made_from_the_constant_is_accepted(rig):
    import copy
    entries = copy.deepcopy(configuration.BACKSTOP_ENTRIES)
    for entry in entries["gpu_backstop_embedders"]["value"]:
        entry["log"] = entry["log"].replace("$HOME", str(rig.home))
    rig.config(**entries)
    values, faults = configuration.backstop_values(rig.env)
    assert faults == [] and [e["port"] for e in values["embedders"]] == [11434, 11435]


# ---- L5b: the backstop's own group, when named, is paused last ----------------------------------------------------

def _own_group_rig(rig, position):
    """Three planted groups; one of them stands in for the backstop's own group (``os.getpgrp`` answers it)."""
    rig.smi("15900, 24000")
    rig.config()
    groups = [rig.job(), rig.job(), rig.job()]
    own = groups[position]
    rig.mp.setattr(backstop.os, "getpgrp", lambda: own)
    seen = {}
    real = os.killpg

    def killpg(group, sig):
        if sig == signal.SIGSTOP:
            seen.setdefault("order", []).append(group)
            if group == own:
                seen["log_at_own_stop"] = rig.log.read_text()
                seen["inbox_at_own_stop"] = sorted(p.name for p in rig.inbox.iterdir()) if rig.inbox.exists() else []
                # the groups already sent SIGSTOP (an unnamed group is never stopped: nothing to wait for there)
                seen["others_stopped"] = [rig.stopped_state(c.pid) for c in rig.groups if c.pid in seen["order"][:-1]]
        return real(group, sig)

    rig.mp.setattr(backstop.os, "killpg", killpg)
    return groups, own, seen


@pytest.mark.parametrize("position", [0, 1, 2], ids=["first", "middle", "last"])
def test_l5b_the_own_group_is_stopped_after_every_other_group_the_trip_line_and_the_item(rig, position):
    groups, own, seen = _own_group_rig(rig, position)
    result = backstop.watch(groups, rig.root, rig.env, max_polls=4)
    others = [g for g in groups if g != own]
    assert seen["order"] == others + [own]
    assert seen["others_stopped"] == ["T", "T"]
    assert sum(1 for line in seen["log_at_own_stop"].splitlines() if " TRIP: " in line) == 1
    assert len(seen["inbox_at_own_stop"]) == 1
    assert result["tripped"] is True and result["paused"] == others + [own]


@pytest.mark.parametrize("position", [0, 1, 2], ids=["first", "middle", "last"])
def test_l5b_the_start_line_ends_with_the_own_group_note_and_the_item_carries_the_note_line(rig, position):
    groups, own, seen = _own_group_rig(rig, position)
    result = backstop.watch(groups, rig.root, rig.env, max_polls=4)
    names = " ".join(str(g) for g in groups)
    start = rig.log.read_text().splitlines()[0]
    assert start[20:] == (f"start: limit 15872 MiB; every 5 s; groups {names}; skipped (ended) none; embedders none; "
                          f"own group {own} named: paused last")
    paused = [g for g in groups if g != own] + [own]
    lines = Path(result["inbox_item"]).read_text().splitlines()
    assert f"paused: {' '.join(str(g) for g in paused)}" in lines
    for g in paused:
        assert f"resume: kill -CONT -- -{g}" in lines
        assert f"stop: kill -TERM -- -{g} && kill -CONT -- -{g}" in lines
    assert lines[-1] == (f"note: the backstop's own group {own} is paused last; resuming it resumes the backstop, "
                         "which then ends")
    assert [line for line in lines if line.startswith("note:")] == [lines[-1]]
    assert f"paused groups {' '.join(str(g) for g in paused)}" in rig.log.read_text().splitlines()[1]


def test_l5b_the_own_group_named_alone_is_stopped_after_the_trip_line_and_the_item(rig):
    groups, own, seen = _own_group_rig(rig, 0)
    result = backstop.watch([own], rig.root, rig.env, max_polls=4)
    assert seen["order"] == [own] and result["paused"] == [own]
    assert " TRIP: " in seen["log_at_own_stop"] and len(seen["inbox_at_own_stop"]) == 1


def test_l5b_an_ended_group_is_skipped_beside_the_own_group_which_is_still_stopped_last(rig):
    rig.smi("15900, 24000")
    rig.config()
    ended, other, own = rig.short_job(), rig.job(), rig.job()
    rig.mp.setattr(backstop.os, "getpgrp", lambda: own)
    result = backstop.watch([own, ended, other], rig.root, rig.env, max_polls=4)
    assert result["skipped"] == [ended] and result["paused"] == [other, own]


def test_l5b_when_the_own_group_is_not_named_there_is_no_note_and_it_is_never_signalled(rig):
    rig.smi("15900, 24000")
    rig.config()
    a, b, unnamed = rig.job(), rig.job(), rig.job()
    rig.mp.setattr(backstop.os, "getpgrp", lambda: unnamed)
    sent = []
    real = os.killpg
    rig.mp.setattr(backstop.os, "killpg", lambda g, s: (sent.append((g, s)), real(g, s))[1])
    result = backstop.watch([a, b], rig.root, rig.env, max_polls=4)
    assert "own group" not in rig.log.read_text() and "note:" not in Path(result["inbox_item"]).read_text()
    assert result["paused"] == [a, b] and {g for g, _ in sent} == {a, b}


def test_l5b_a_job_sharing_the_backstops_own_group_and_a_second_group_are_both_paused_then_resumed(rig):
    rig.smi("15900, 24000")
    rig.config()
    second = rig.job()
    # gov runs in a session of its own; a job started with & shares its group, as the shell's $$ names it
    sleeper = f"{shlex.quote(sys.executable)} -c {shlex.quote(SLEEPER)} {MARK} >/dev/null 2>&1 &"
    shell = (sleeper + " exec " + sys.executable + " -c 'import sys; from gov.cli.main import main; "
             "sys.exit(main(sys.argv[1:]))' resources --json --backstop $$ " + str(second) + " --root " + str(rig.root))
    child = rig.spawn(["sh", "-c", shell], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                      env={**os.environ, **rig.env, "PYTHONPATH": str(REPO / "src")})
    own = child.pid
    deadline = time.monotonic() + 40
    while rig.state(child.pid) != "T" and time.monotonic() < deadline:
        REAL_SLEEP(0.05)
    assert rig.state(child.pid) == "T", "gov was never stopped"
    assert rig.stopped_state(rig.groups[0].pid) == "T"  # the second group was paused before the own group
    log = rig.log.read_text().splitlines()
    assert log[0].endswith(f"own group {own} named: paused last")
    assert sum(1 for line in log if " TRIP: " in line) == 1
    items = list(rig.inbox.iterdir())
    assert len(items) == 1 and f"paused: {second} {own}" in items[0].read_text().splitlines()
    os.killpg(own, signal.SIGCONT)
    out, err = child.communicate(timeout=40)
    assert child.returncode == 0, err
    result = json.loads(out)["result"]
    assert result["tripped"] is True and result["paused"] == [second, own]


# ---- the reopened fix (DEC-1144 (2)): a group of zombies has ended; the watch has a bound; the tests reap their groups --

def test_a_group_whose_only_member_is_an_unreaped_zombie_has_ended(rig):
    group = rig.zombie()
    assert rig.state(group) == "Z"
    os.killpg(group, 0)  # signal 0 still reaches a zombie's group: this is what kept a watch polling for ever
    assert backstop._live(group) is False


def test_a_job_that_ends_and_is_not_reaped_ends_the_watch_untripped_by_the_zombie_rule(rig):
    rig.smi("100, 24000")
    rig.config()
    job = rig.job()

    def die_unreaped(seconds):
        rig.groups[0].kill()  # never waited for: it stays a zombie, its group still answers signal 0
        rig.wait_state(rig.groups[0].pid, "Z")

    rig.mp.setattr(backstop, "_pause",die_unreaped)
    result = backstop.watch([job], rig.root, rig.env, max_polls=4)
    assert result["tripped"] is False and result["skipped"] == [] and rig.smi_calls() == 1
    text = rig.log.read_text()
    assert f"end: every watched group has ended ({job})" in text and "bound" not in text


def test_a_zombie_group_at_the_start_is_skipped_and_named_and_never_signalled(rig):
    rig.smi("15900, 24000")
    rig.config()
    zombie, live = rig.zombie(), rig.job()
    sent = []
    real = os.killpg
    rig.mp.setattr(backstop.os, "killpg", lambda g, s: (sent.append((g, s)), real(g, s))[1])
    result = backstop.watch([zombie, live], rig.root, rig.env, max_polls=3)
    assert result["paused"] == [live] and result["skipped"] == [zombie]
    assert (zombie, signal.SIGSTOP) not in sent
    alone = backstop.watch([zombie], rig.root, rig.env, max_polls=3)
    assert alone["tripped"] is False and alone["skipped"] == [zombie]
    assert "end: every watched group has ended" in rig.log.read_text()


def test_a_paused_group_is_still_live(rig):
    rig.smi("100, 24000")
    rig.config()
    job = rig.job()
    os.killpg(job, signal.SIGSTOP)
    rig.wait_state(rig.groups[0].pid, "T")
    assert backstop._live(job) is True
    result = backstop.watch([job], rig.root, rig.env, max_polls=3)
    assert result["tripped"] is False and result["skipped"] == [] and rig.smi_calls() == 3
    text = rig.log.read_text()
    assert "every watched group has ended" not in text and f"groups still live {job}" in text


def test_a_group_with_a_zombie_and_a_live_member_is_live_and_the_stop_reaches_the_live_one(rig):
    shell = f"{shlex.quote(sys.executable)} -c {shlex.quote(SLEEPER)} {MARK} & exit 0"
    leader = rig.spawn(["sh", "-c", shell])
    rig.wait_state(leader.pid, "Z")  # the leader is a zombie; the sleeper, in its group, runs on
    group = leader.pid
    assert sorted(rig.members(group).values()) in (["S", "Z"], ["R", "Z"])
    assert backstop._live(group) is True
    rig.smi("15900, 24000")
    rig.config()
    result = backstop.watch([group], rig.root, rig.env, max_polls=3)
    assert result["tripped"] is True and result["paused"] == [group] and result["skipped"] == []
    deadline = time.monotonic() + 20
    while "T" not in rig.members(group).values() and time.monotonic() < deadline:
        REAL_SLEEP(0.01)
    assert sorted(rig.members(group).values()) == ["T", "Z"]


@pytest.mark.parametrize("text,expected", [
    ("123 (python3) S 1 77 77 0 -1 4194304", ("S", 77)),
    ("123 (a b) c) Z 1 88 88 0", ("Z", 88)),
    ("123 (x)) T 1 5 5 0", ("T", 5)),
    ("123 () X 1 9 9", ("X", 9)),
    ("garbage", None), ("1 (x) Z 1", None), ("1 (x) Z 1 notanumber 3", None), ("", None),
])
def test_the_stat_line_is_read_after_its_last_parenthesis(text, expected):
    assert backstop._state_and_group(text) == expected


def _fake_proc(folder: Path, entries: dict) -> Path:
    """A planted /proc: pid -> stat text (None: a process that vanished, its folder holds no stat)."""
    for pid, text in entries.items():
        (folder / str(pid)).mkdir(parents=True)
        if text is not None:
            (folder / str(pid) / "stat").write_text(text)
    (folder / "self").mkdir()  # not a process number: never read
    return folder


@pytest.mark.parametrize("states,live", [
    (["Z"], False), (["Z", "Z"], False), (["X"], False), (["Z", "X"], False),
    (["Z", "S"], True), (["Z", "T"], True), (["T"], True), (["t", "Z"], True), (["Z", "D"], True), (["R"], True),
])
def test_only_a_group_whose_members_are_all_zombies_or_dead_has_ended(rig, states, live):
    job = rig.job()  # a real group, so that signal 0 succeeds; /proc is the planted one
    entries = {100 + n: f"{100 + n} (a b) {state} 1 {job} {job} 0" for n, state in enumerate(states)}
    entries[500] = f"500 (other) S 1 {job + 1} {job + 1} 0"  # another group: never counted
    entries[501] = None  # vanished while being read: skipped
    rig.mp.setattr(backstop, "PROC", str(_fake_proc(rig.tmp / "proc", entries)))
    assert backstop._live(job) is live


def test_a_zombie_leader_whose_thread_still_runs_is_live(rig):
    job = rig.job()
    proc = rig.tmp / "proc"
    _fake_proc(proc, {700: f"700 (j) Z 1 {job} {job} 0"})
    (proc / "700" / "task" / "700").mkdir(parents=True)
    (proc / "700" / "task" / "700" / "stat").write_text(f"700 (j) Z 1 {job} {job} 0")
    rig.mp.setattr(backstop, "PROC", str(proc))
    assert backstop._live(job) is False  # the leader alone: a zombie with no thread running
    (proc / "700" / "task" / "701").mkdir()
    (proc / "700" / "task" / "701" / "stat").write_text(f"701 (j) Z 1 {job} {job} 0")
    assert backstop._live(job) is False  # a thread that is itself a zombie runs nothing
    (proc / "700" / "task" / "701" / "stat").write_text(f"701 (j) S 1 {job} {job} 0")
    assert backstop._live(job) is True


def test_no_proc_or_no_member_found_keeps_the_answer_live(rig):
    job = rig.job()
    rig.mp.setattr(backstop, "PROC", str(rig.tmp / "no-such-proc"))
    assert backstop._live(job) is True
    rig.mp.setattr(backstop, "PROC", str(_fake_proc(rig.tmp / "proc", {500: f"500 (o) S 1 {job + 1} {job + 1} 0",
                                                                      501: None})))
    assert backstop._live(job) is True  # signal 0 succeeded and no member was found: today's answer


def test_a_group_that_no_longer_exists_or_cannot_be_named_is_still_ended_and_a_permission_error_is_live(rig):
    assert backstop._live(rig.short_job()) is False
    assert backstop._live(2**40) is False

    def refuse(group, sig):
        raise PermissionError

    rig.mp.setattr(backstop.os, "killpg", refuse)
    assert backstop._live(1) is True


@pytest.mark.parametrize("bound", [1, 2, 5])
def test_the_bound_ends_a_watch_that_never_trips_after_exactly_that_many_polls(rig, bound):
    rig.smi("100, 24000")
    rig.config()
    job = rig.job()
    result = backstop.watch([job], rig.root, rig.env, max_polls=bound)
    assert result == {"tripped": False, "reason": None, "reading": None, "paused": [], "skipped": [],
                      "log": str(rig.log), "inbox_item": None}  # the result has no new key
    assert rig.smi_calls() == bound and rig.sleeps == [5] * (bound - 1)  # no sleep after the last poll
    lines = rig.log.read_text().splitlines()
    assert lines[-1][20:] == f"end: the bound of {bound} polls reached; no trip; groups still live {job}"
    assert sum("bound" in line for line in lines) == 1
    assert rig.state(rig.groups[0].pid) not in ("T", "Z", "gone") and not rig.inbox.exists()


def test_a_trip_before_the_bound_is_a_trip_and_names_no_bound(rig):
    rig.smi("100, 24000", "15900, 24000")
    rig.config()
    job = rig.job()
    result = backstop.watch([job], rig.root, rig.env, max_polls=2)  # the second poll is the last one allowed
    assert result["tripped"] is True and result["paused"] == [job] and rig.smi_calls() == 2
    assert "bound" not in rig.log.read_text()


def test_the_bound_is_not_reached_by_a_group_that_ended_on_the_last_poll(rig):
    rig.smi("100, 24000")
    rig.config()
    job = rig.job()
    rig.mp.setattr(backstop, "_live", lambda g: rig.smi_calls() < 2)  # live at the loop top, ended after poll 2
    result = backstop.watch([job], rig.root, rig.env, max_polls=2)
    assert result["tripped"] is False and rig.smi_calls() == 2 and rig.sleeps == [5]  # no sleep after the last poll
    text = rig.log.read_text()
    assert f"end: every watched group has ended ({job})" in text and "bound" not in text


@pytest.mark.parametrize("bound", [0, -1, True, "3", 2.5])
def test_a_bound_that_is_not_a_positive_integer_refuses_to_start(rig, bound):
    rig.smi("100, 24000")
    rig.config()
    job = rig.job()
    with pytest.raises(GovError) as error:
        backstop.watch([job], rig.root, rig.env, max_polls=bound)
    assert error.value.code == "RESOURCE_ARGUMENTS_INVALID" and "max_polls" in error.value.message
    assert not rig.log.exists() and rig.smi_calls() == 0


def test_the_default_has_no_bound_and_polls_on_until_the_group_ends(rig):
    parameter = inspect.signature(backstop.watch).parameters["max_polls"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY and parameter.default is None
    rig.smi("100, 24000")
    rig.config()
    job = rig.job()
    polls = []

    def end_at_the_ninth(seconds):
        polls.append(seconds)
        if len(polls) > 50:
            raise AssertionError("runaway: the group was never ended")
        if len(polls) == 9:
            rig.groups[0].kill()
            rig.groups[0].wait()

    rig.mp.setattr(backstop, "_pause",end_at_the_ninth)
    result = backstop.watch([job], rig.root, rig.env)  # no bound: it ends only because the group ended
    assert result["tripped"] is False and rig.smi_calls() == 9 and len(polls) == 9
    text = rig.log.read_text()
    assert f"end: every watched group has ended ({job})" in text and "bound" not in text


def test_a_replaced_backstop_pause_is_not_called_by_subprocess_and_time_sleep_is_untouched(rig):
    rig.smi("100, 24000")
    rig.config()
    slow = rig.bin / "nvidia-smi"  # closes its output at once and exits 0.2 s later: subprocess waits on it with sleeps
    slow.write_text(f"#!{sys.executable}\nimport os, time\nprint('100, 24000', flush=True)\nos.close(1)\nos.close(2)\n"
                    "time.sleep(0.2)\n")
    job = rig.job()
    assert time.sleep is REAL_SLEEP
    result = backstop.watch([job], rig.root, rig.env, max_polls=3)
    assert result["tripped"] is False and result["reading"] is None
    assert rig.sleeps == [5, 5]  # the period only: none of subprocess's own waits (0.001, 0.002, ...) is in it
    assert "no GPU reading" not in rig.log.read_text()


def test_every_group_a_test_plants_is_reaped_by_the_rigs_teardown(tmp_path, monkeypatch):
    planted = Rig(tmp_path, monkeypatch)
    paused, killed, zombie = planted.job(), planted.job(), planted.zombie()
    outside = planted.spawn([sys.executable, "-c", SLEEPER, MARK])  # started in a test body, not by job()
    pids = [c.pid for c in planted.groups]
    os.killpg(paused, signal.SIGSTOP)
    planted.groups[1].kill()  # killed and never waited for
    planted.close()
    assert [c.returncode is not None for c in planted.groups] == [True] * len(pids)  # every child was waited for
    assert all(planted.members(pid) == {} for pid in pids)  # and no member of any of the groups is left
