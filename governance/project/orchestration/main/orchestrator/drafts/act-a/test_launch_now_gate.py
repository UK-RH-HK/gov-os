"""ACT-LOAD-BALANCER-A (DEC-1133 (3)): launch_now.sh checks the resource gate before each lead and registers it.

Run:  python3 -m pytest -q -p no:cacheprovider test_launch_now_gate.py
      LAUNCH_NOW=<another copy of the script> python3 -m pytest ...     (the old script: the tests are red)

The script under test names its paths absolutely, so each case runs a copy with the orchestrator folder, the worktrees
folder and the CLI paths pointed into tmp_path (the same method as tests/unit/launch/test_w2_153_template.py). No
real claude session and no real lead is ever started: `claude` is a stub that records what it saw at its start (its
pid and process start, the registry's entries at that moment, its argv) and may hold for a moment so a test can look
at the machine while it "runs". Two beds:
  stub gov   a stub `gov` that records its calls and answers with a chosen exit code (the order and the arguments);
  real gov   the pinned `gov` (its own binary, a planted HOME, the product's own test overrides for the readings): the
             registry entry written is the real one, and the gate's reading and lead_mem.py's sampler see the lead.
Nothing here matches a process by name; every wait is on a pid this test started (Popen), bounded.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SCRIPT = Path(os.environ.get("LAUNCH_NOW") or HERE / "launch_now.sh")
REAL_ORCH = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator"
REAL_TREES = "/home/usain/gov-os-worktrees"
REAL_CLAUDE = "/home/usain/.local/bin/claude"
REAL_GOV = "/home/usain/.local/bin/gov"
LEAD_MEM_PY = os.environ.get("LEAD_MEM_PY") or REAL_ORCH + "/tools/lead_mem.py"   # read only: a copy may be named
SAFE_PATH = "/usr/bin:/bin"
OPEN_GATE = {  # the product's own test overrides (resources/machine.py): an open gate whatever the machine is doing
    "GOV_RESOURCES_NPROC": "20", "GOV_RESOURCES_BUSY_CORES": "0",
    "GOV_RESOURCES_EMBEDDING_CPU": '{"shared": 0, "query": 0}',
    "GOV_RESOURCES_EMBEDDING_CPU_NOW": '{"shared": 0, "query": 0}',
    "GOV_RESOURCES_DISK": '{"free_bytes": 1000000000000000, "free_inodes": 1000000000}',
}

CLAUDE_STUB = r"""#!/bin/bash
# the stand-in for claude: records, may hold, never does anything else
{
  echo "pid=$$"
  echo "start=$(sed 's/.*) //' /proc/$$/stat | cut -d' ' -f20)"
  echo "sessions=$(ls "$HOME/.gov-os/machine/sessions" 2>/dev/null | tr '\n' ' ')"
  printf 'arg=%s\n' "$@"
} > "@RECORD@"
for _ in $(seq 1 300); do [ -f "@HOLD@" ] || break; sleep 0.1; done
exit 0
"""

GOV_STUB = r"""#!/bin/bash
# the stand-in for gov: records its call and answers with the exit code in rc-<subcommand>, 0 if there is none
echo "$*" >> "@CALLS@"
mode=check; case "$*" in *--register*) mode=register;; esac
rc=0; [ -f "@BED@/rc-$mode" ] && rc=$(cat "@BED@/rc-$mode")
echo "gov stub: $mode answers $rc"
exit "$rc"
"""


class Bed:
    def __init__(self, base: Path, real_gov: bool = False):
        self.base, self.real_gov = base, real_gov
        self.home, self.orch, self.trees = base / "home", base / "orch", base / "trees"
        self.bin = base / "bin"
        self.tree = self.trees / "W9-1"
        self.record, self.hold, self.calls = base / "claude-record.txt", base / "hold", base / "gov-calls.txt"
        self.ticket = "DAEO-act" + uuid.uuid4().hex[:8]
        for folder in (self.home, self.orch / "tools", self.orch / "briefs", self.orch / "log", self.bin,
                       self.tree / ".claude/templates"):
            folder.mkdir(parents=True, exist_ok=True)
        (self.orch / "tools/disk_gate.sh").write_text("exit 0\n", encoding="utf-8")
        (self.orch / "briefs/B.md").write_text("brief\n", encoding="utf-8")
        (self.tree / ".claude/templates/role-lead.md").write_text("# lead\n", encoding="utf-8")
        self.claude = self._write(self.bin / "claude", CLAUDE_STUB.replace("@RECORD@", str(self.record))
                                  .replace("@HOLD@", str(self.hold)))
        self.gov = REAL_GOV if real_gov else self._write(
            self.bin / "gov", GOV_STUB.replace("@CALLS@", str(self.calls)).replace("@BED@", str(base)))

    @staticmethod
    def _write(path: Path, text: str) -> str:
        path.write_text(text, encoding="utf-8")
        path.chmod(0o755)
        return str(path)

    def script(self) -> Path:
        text = SCRIPT.read_text(encoding="utf-8")
        for real, here in ((REAL_ORCH, self.orch), (REAL_TREES, self.trees), (REAL_CLAUDE, self.claude),
                           (REAL_GOV, self.gov)):
            text = text.replace(real, str(here))
        leftover = text.replace(REAL_GOV, "").replace(str(self.base), "")
        assert "/home/usain" not in leftover, "a real path is left in the script copy"
        out = self.base / "launch_now.sh"
        out.write_text(text, encoding="utf-8")
        return out

    def env(self, extra: dict | None = None) -> dict:
        env = {"PATH": SAFE_PATH, "HOME": str(self.home), "LC_ALL": "C", "TMPDIR": str(self.base)}
        if self.real_gov:
            env.update(OPEN_GATE)
            env["GOV_RESOURCES_MEMINFO"] = str(self.meminfo("MemAvailable: 67108864 kB\n"))
            env["GOV_RESOURCES_LOADAVG"] = str(self.loadavg())
        env.update(extra or {})
        return env

    def meminfo(self, text: str, name: str = "meminfo") -> Path:
        path = self.base / name
        path.write_text(text, encoding="utf-8")
        return path

    def loadavg(self) -> Path:
        path = self.base / "loadavg"
        path.write_text("0.1 0.1 0.1 1/1 1\n", encoding="utf-8")
        return path

    def argv(self) -> list[str]:
        return ["bash", str(self.script()), "W9-1", self.ticket, "B.md", "L.json"]

    def start(self, extra_env: dict | None = None) -> subprocess.Popen:
        """The launcher as the dispatcher starts it (no stdin, its own session), without waiting for it."""
        return subprocess.Popen(self.argv(), cwd=str(self.base), env=self.env(extra_env), stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)

    def run(self, extra_env: dict | None = None) -> subprocess.CompletedProcess:
        proc = self.start(extra_env)
        try:
            out, err = proc.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            proc.kill()  # by the pid this test started; never a name
            out, err = proc.communicate()
            raise AssertionError(f"the launcher did not end in 60 s\n{err}")
        return subprocess.CompletedProcess(proc.args, proc.returncode, out, err)

    def seen(self) -> dict:
        """What the claude stub recorded at its start; {} if it never started."""
        if not self.record.exists():
            return {}
        out: dict = {"arg": []}
        for line in self.record.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            if key == "arg":
                out["arg"].append(value)
            else:
                out[key] = value
        return out

    def gov_calls(self) -> list[str]:
        return self.calls.read_text(encoding="utf-8").splitlines() if self.calls.exists() else []


def wait_for(path: Path, seconds: float = 30.0) -> None:
    end = time.time() + seconds
    while not path.exists():
        assert time.time() < end, f"{path} did not appear in {seconds} s"
        time.sleep(0.05)


@pytest.fixture
def bed(tmp_path):
    return Bed(tmp_path / "bed")


@pytest.fixture
def real_bed(tmp_path):
    if not os.path.exists(REAL_GOV):
        pytest.skip("the pinned gov is not installed here")
    b = Bed(tmp_path / "bed", real_gov=True)
    done = subprocess.run([REAL_GOV, "resources", "--init-config"], cwd=str(b.tree), env=b.env(),
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    return b


# -- the order, with a stand-in gov -----------------------------------------------------------------------------------

def test_an_open_gate_checks_then_registers_the_launchers_own_pid_then_starts_the_lead(bed):
    done = bed.run()
    assert done.returncode == 0, done.stderr
    seen = bed.seen()
    assert seen, "the lead was not started"
    calls = bed.gov_calls()
    assert calls[0].split()[:2] == ["resources", "--check"], calls
    register = calls[1].split()
    assert register[:2] == ["resources", "--register"], calls
    # the registered pid is the process that then became the lead: exec keeps the pid
    assert register[2] == seen["pid"], f"registered {register[2]}, the lead's pid is {seen['pid']}"
    assert register[3:] == ["--ticket", bed.ticket, "--session-role", "orchestrator"]
    assert len(calls) == 2, calls


def test_a_shut_gate_starts_nothing_and_registers_nothing(bed):
    (bed.base / "rc-check").write_text("3\n")
    done = bed.run()
    assert done.returncode == 3, (done.returncode, done.stderr)
    assert bed.seen() == {}, "a lead was started with the gate shut"
    assert all("--register" not in c for c in bed.gov_calls()), bed.gov_calls()
    assert "LAUNCH_GATE_SHUT" in done.stderr


def test_a_gate_check_that_cannot_run_starts_nothing(bed):
    """Fail closed: gov missing (exit 127) is not an open gate."""
    os.unlink(bed.gov)
    done = bed.run()
    assert done.returncode == 3, (done.returncode, done.stderr)
    assert bed.seen() == {}


def test_a_check_that_fails_in_another_way_starts_nothing(bed):
    (bed.base / "rc-check").write_text("1\n")
    done = bed.run()
    assert done.returncode == 3 and bed.seen() == {}, done.stderr


def test_a_lead_that_cannot_be_registered_is_not_started(bed):
    (bed.base / "rc-register").write_text("5\n")
    done = bed.run()
    assert done.returncode == 4, (done.returncode, done.stderr)
    assert bed.seen() == {}
    assert "LAUNCH_NOT_REGISTERED" in done.stderr


def test_the_disk_gate_and_the_template_still_come_first_and_ask_nothing_of_gov(bed):
    (bed.tree / ".claude/templates/role-lead.md").unlink()
    done = bed.run()
    assert done.returncode == 2 and "LAUNCH_NO_TEMPLATE" in done.stderr
    assert bed.gov_calls() == [] and bed.seen() == {}
    (bed.tree / ".claude/templates/role-lead.md").write_text("# lead\n")
    (bed.orch / "tools/disk_gate.sh").write_text("exit 1\n")
    done = bed.run()
    assert done.returncode == 2 and bed.gov_calls() == [] and bed.seen() == {}


def test_the_lead_command_is_unchanged(bed):
    done = bed.run()
    assert done.returncode == 0, done.stderr
    argv = bed.seen()["arg"]
    assert argv[:8] == ["-p", "--model", "claude-opus-5-5", "--effort", "high", "--output-format", "json",
                        "--permission-mode"]
    assert argv[-2:] == ["--append-system-prompt-file", str(bed.tree / ".claude/templates/role-lead.md")]
    settings = json.loads(argv[argv.index("--settings") + 1])
    assert settings == {"env": {"GOV_ROLE": "orchestrator", "GOV_TICKET": bed.ticket,
                                "CLAUDE_CODE_SUBAGENT_MODEL": "claude-opus-5-5"}}


def test_the_script_is_in_order_and_matches_no_process_by_name():
    code = "\n".join(line for line in SCRIPT.read_text(encoding="utf-8").splitlines()
                     if not line.lstrip().startswith("#"))
    check, register, start = (code.index(s) for s in ("resources --check", "resources --register", "\nexec "))
    assert check < register < start
    for banned in ("pgrep", "pkill", "killall", "ps -", "pidof", "$(ps", "kill "):
        assert banned not in code, banned
    assert "&\n" not in code and not re.search(r"claude[^\n]*&\s*$", code, re.M), "the lead is started in the foreground"


# -- the real gov: the registry, the gate's reading and the sampler -----------------------------------------------------

def test_with_the_real_gov_the_lead_is_in_the_registry_before_it_runs_and_the_gate_and_the_sampler_see_it(real_bed):
    b = real_bed
    b.hold.write_text("hold\n")
    proc = b.start()
    try:
        wait_for(b.record)
        seen = b.seen()
        # 1. registered before the start: the stub, at its first line, already finds its own entry (same pid)
        assert f"{seen['pid']}.json" in seen["sessions"].split(), seen
        entry = json.loads((b.home / ".gov-os/machine/sessions" / f"{seen['pid']}.json").read_text())
        assert entry["pid"] == int(seen["pid"]) == proc.pid
        assert entry["ticket"] == b.ticket and entry["role"] == "orchestrator"
        assert Path(entry["repository"]) == b.tree.resolve()
        # 2. the entry is this process's own: its recorded start is the start the process has now
        assert str(entry["start_ticks"]) == seen["start"], (entry, seen)
        # 3. the gate's own reading lists the lead
        reading = subprocess.run([REAL_GOV, "resources"], cwd=str(b.tree), env=b.env(), capture_output=True, text=True,
                                 timeout=60)
        assert reading.returncode == 0, reading.stderr
        sessions = json.loads(reading.stdout)["sessions"]
        assert [s["ticket"] for s in sessions] == [b.ticket], sessions
        # 4. the sample the sample day takes holds the lead
        sample = subprocess.run([REAL_GOV, "resources", "--sample", "--json"], cwd=str(b.tree), env=b.env(),
                                capture_output=True, text=True, timeout=60)
        assert sample.returncode == 0, sample.stderr
        taken = json.loads(sample.stdout)
        text = json.dumps(taken)
        assert b.ticket in text and '"orchestrator"' in text, text[:400]
        # 5. the lead-memory sampler (tools/lead_mem.py, which reads the process table) lists it too
        spec = importlib.util.spec_from_file_location("lead_mem_under_test", LEAD_MEM_PY)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert b.ticket in mod.snapshot()["leads_kb"]
    finally:
        b.hold.unlink()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    assert proc.returncode == 0, proc.stderr.read()


def test_with_the_real_gov_a_shut_gate_starts_nothing_and_leaves_no_entry(real_bed):
    b = real_bed
    done = b.run({"GOV_RESOURCES_MEMINFO": str(b.meminfo("MemAvailable: 1000 kB\n", "meminfo-low"))})
    assert done.returncode == 3, (done.returncode, done.stderr)
    assert b.seen() == {}
    assert "RESOURCE_GATE_SHUT" in done.stderr and "LAUNCH_GATE_SHUT" in done.stderr
    assert not list((b.home / ".gov-os/machine/sessions").glob("*.json"))


def test_with_the_real_gov_a_registry_that_cannot_be_written_starts_nothing(real_bed):
    b = real_bed
    sessions = b.home / ".gov-os/machine/sessions"
    sessions.write_text("a file where the folder should be\n")
    done = b.run()
    assert done.returncode in (3, 4), (done.returncode, done.stderr)
    assert b.seen() == {}


def test_the_stale_entry_of_an_ended_lead_is_cleared_by_the_next_reading(real_bed):
    b = real_bed
    assert b.run().returncode == 0
    seen = b.seen()
    path = b.home / ".gov-os/machine/sessions" / f"{seen['pid']}.json"
    assert path.exists()                       # the stub ended; the entry stays until the next reading
    reading = subprocess.run([REAL_GOV, "resources"], cwd=str(b.tree), env=b.env(), capture_output=True, text=True,
                             timeout=60)
    assert reading.returncode == 0 and json.loads(reading.stdout)["sessions"] == []
    assert not path.exists()
