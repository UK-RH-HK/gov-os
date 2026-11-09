"""Support code for the W2-20 acceptance tests (standard library only).

W2-20 delivers ``gov resources``: a reading of the machine (available memory, 1-minute load, processor count) and of
every live Gov OS session in a machine-wide registry under ``~/.gov-os/machine/``, and the resource gate it reports,
with a start check a session start consults. The tests use it only through the public interface stated in
``README.md``:

- the command ``gov resources`` (``python3 -m gov.cli.main resources ...``) and its JSON envelope;
- the registry folder ``$HOME/.gov-os/machine/`` and its configuration file ``gate.json`` there;
- three environment variables that name where the readings come from (``GOV_RESOURCES_MEMINFO``,
  ``GOV_RESOURCES_LOADAVG``, ``GOV_RESOURCES_NPROC``).

How the code under test is chosen (DEC-732): every command runs with ``PYTHONPATH`` set to the ``src/`` folder of the
working tree this file is in, so in a ticket worktree it runs that worktree's own code.

What is never touched: the real ``~/.gov-os/``. Every command runs with ``HOME`` set to a temporary folder, with an
environment built from scratch (the session's ``GOV_ROLE`` and ``GOV_TICKET`` are not passed on), and every reading
comes from a file the test writes. No test depends on this machine's real memory, load or sessions. "Live" and "dead"
sessions are child processes the test starts and stops itself.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[3] / "src"

COMMAND_TIMEOUT_S = 120.0  # a wait under parallel load, not a time the ticket promises

GIB = 1024 ** 3
KIB = 1024

# The defaults: DEC-742's values (P-W2-9; first proposed in WAVE_2_WBS.md §0 rule 9).
DEFAULT_MIN_AVAILABLE_MEMORY_BYTES = 4 * GIB
DEFAULT_MAX_WEIGHTED_SESSIONS = 8
# The default load limit is the processor count (``nproc``).

GATE_SHUT_ERROR = "RESOURCE_GATE_SHUT"
CONDITIONS = ("memory", "load", "sessions")


class Machine:
    """One test's machine: a temporary home folder, readings it writes, repositories built from scratch."""

    def __init__(self, base: Path):
        self.base = base
        self.home = base / "home"
        self.home.mkdir()
        self.readings = base / "readings"
        self.readings.mkdir()
        self.meminfo = self.readings / "meminfo"
        self.loadavg = self.readings / "loadavg"
        self.nproc = 4
        self.children: list[subprocess.Popen] = []
        self._location_checked = False
        # Generous readings by default; each test sets what it needs.
        self.set_readings(available_bytes=64 * GIB, load=0.10, nproc=4)

    # ------------------------------------------------------------------ places

    @property
    def registry(self) -> Path:
        return self.home / ".gov-os" / "machine"

    @property
    def config_file(self) -> Path:
        return self.registry / "gate.json"

    def repo(self, name: str) -> Path:
        """A git repository built from scratch, with one commit."""
        path = self.base / name
        path.mkdir()
        self._git(path, "init", "-q")
        (path / "README.md").write_text(f"{name}: a W2-20 test repository\n")
        self._git(path, "add", "README.md")
        self._git(path, "commit", "-q", "-m", "initial")
        return path.resolve()

    def _git(self, path: Path, *args: str) -> None:
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.home),
            "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "W2-20 tests", "GIT_AUTHOR_EMAIL": "w2-20@example.invalid",
            "GIT_COMMITTER_NAME": "W2-20 tests", "GIT_COMMITTER_EMAIL": "w2-20@example.invalid",
        }
        subprocess.run(["git", "-C", str(path), *args], env=env, check=True, capture_output=True,
                       timeout=COMMAND_TIMEOUT_S)

    # ---------------------------------------------------------------- readings

    def set_readings(self, *, available_bytes=None, load=None, nproc=None) -> None:
        """Write the reading files. ``available_bytes`` must be a whole number of KiB (meminfo counts in kB)."""
        if available_bytes is not None:
            assert available_bytes % KIB == 0
            kib = available_bytes // KIB
            self.meminfo.write_text(
                f"MemTotal:       {kib + 8 * 1024 * 1024} kB\n"
                f"MemFree:        {max(kib // 2, 1)} kB\n"
                f"MemAvailable:   {kib} kB\n"
                f"Buffers:        1024 kB\n"
                f"Cached:         2048 kB\n"
            )
        if load is not None:
            self.loadavg.write_text(f"{load:.2f} {load:.2f} {load:.2f} 1/321 54321\n")
        if nproc is not None:
            self.nproc = nproc

    def set_config(self, **values) -> None:
        """Write ``gate.json`` with the given thresholds (keys as in README.md)."""
        self.registry.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps(values))

    def open_config(self, **overrides) -> None:
        """Thresholds the default readings pass with room to spare, unless overridden."""
        values = {"min_available_memory_bytes": 1 * GIB, "max_load_1m": 8.0, "max_weighted_sessions": 8}
        values.update(overrides)
        self.set_config(**values)

    # ---------------------------------------------------------------- processes

    def live_process(self) -> subprocess.Popen:
        """A child process that stays alive until the test ends."""
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"],
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.children.append(proc)
        return proc

    @staticmethod
    def stop(proc: subprocess.Popen) -> None:
        proc.kill()
        proc.wait(timeout=COMMAND_TIMEOUT_S)

    def cleanup(self) -> None:
        for proc in self.children:
            if proc.poll() is None:
                self.stop(proc)

    # ---------------------------------------------------------------- the command

    def env(self, **extra) -> dict:
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.home),
            "TMPDIR": str(self.base),
            "LC_ALL": "C",
            "PYTHONPATH": str(SRC),
            "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GOV_RESOURCES_MEMINFO": str(self.meminfo),
            "GOV_RESOURCES_LOADAVG": str(self.loadavg),
            "GOV_RESOURCES_NPROC": str(self.nproc),
        }
        env.update({k: v for k, v in extra.items() if v is not None})
        for key in [k for k, v in extra.items() if v is None]:
            env.pop(key, None)
        return env

    def gov(self, repo: Path, *args: str, json_output: bool = True, env_extra: dict | None = None):
        """Run ``gov resources <args>`` in ``repo``; return ``(exit code, envelope or None, stdout, stderr)``."""
        if not self._location_checked:
            self._location_checked = True
            self._check_location(repo)
        return self._run(repo, *args, json_output=json_output, env_extra=env_extra)

    def _run(self, repo: Path, *args: str, json_output: bool = True, env_extra: dict | None = None):
        argv = [sys.executable, "-m", "gov.cli.main", "resources", *args, "--root", str(repo)]
        if json_output:
            argv.append("--json")
        proc = subprocess.run(argv, cwd=str(repo), env=self.env(**(env_extra or {})), capture_output=True,
                              text=True, timeout=COMMAND_TIMEOUT_S)
        envelope = None
        if json_output:
            try:
                envelope = json.loads(proc.stdout)
            except ValueError:
                envelope = None
        return proc.returncode, envelope, proc.stdout, proc.stderr

    def _check_location(self, repo: Path) -> None:
        """Before a test enters anything, the reading must name a registry inside this test's temporary home."""
        code, envelope, out, err = self._run(repo)
        result = reading_of(code, envelope, out, err)
        assert "registry" in result, f"the reading names no registry folder: {result}"
        registry = os.path.realpath(result["registry"])
        expected = os.path.realpath(self.registry)
        assert registry == expected or registry.startswith(expected + os.sep), (
            f"the registry is {registry}, not under $HOME/.gov-os/machine/ ({expected})")

    def register(self, repo: Path, pid: int, *, ticket: str, role: str = "engineer", heavy: bool = False):
        args = ["--register", str(pid), "--ticket", ticket, "--session-role", role]
        if heavy:
            args.append("--heavy")
        code, envelope, out, err = self.gov(repo, *args)
        assert code == 0 and envelope is not None and envelope.get("ok") is True, (
            f"registering pid {pid} failed: exit {code}\nstdout: {out}\nstderr: {err}")
        return envelope

    def read(self, repo: Path, **kw) -> dict:
        code, envelope, out, err = self.gov(repo, **kw)
        return reading_of(code, envelope, out, err)

    def check(self, repo: Path, *, heavy: bool = False, **kw):
        """The start check; ``heavy`` asks it for a heavy session's start (``--check --heavy``, DEC-747)."""
        args = ["--check", "--heavy"] if heavy else ["--check"]
        return self.gov(repo, *args, **kw)


def reading_of(code, envelope, out, err) -> dict:
    """The ``result`` of a successful ``gov resources --json``."""
    assert envelope is not None, f"gov resources printed no JSON envelope (exit {code})\nstdout: {out}\nstderr: {err}"
    assert code == 0 and envelope.get("ok") is True, (
        f"gov resources did not succeed: exit {code}\nenvelope: {envelope}\nstderr: {err}")
    assert "resources" in str(envelope.get("command")), f"the envelope names another command: {envelope}"
    result = envelope.get("result")
    assert isinstance(result, dict), f"the envelope's result is not an object: {envelope}"
    return result


def refusal_of(code, envelope, out, err) -> dict:
    """The reading a refused start check carries: ``ok: false``, error ``RESOURCE_GATE_SHUT``, reading in details."""
    assert envelope is not None, f"gov resources --check printed no JSON envelope (exit {code})\nstdout: {out}\nstderr: {err}"
    assert code not in (0, 2), f"a start check with the gate shut ended with exit {code}, not a refusal\n{envelope}"
    assert envelope.get("ok") is False, f"a refused start check has ok: {envelope.get('ok')}\n{envelope}"
    error = envelope.get("error")
    assert isinstance(error, dict) and error.get("code") == GATE_SHUT_ERROR, (
        f"the refusal is not the named error {GATE_SHUT_ERROR}: {error}")
    details = error.get("details")
    assert isinstance(details, dict), f"the refusal carries no reading in error.details: {error}"
    return details


def gate_of(reading: dict) -> dict:
    gate = reading.get("gate")
    assert isinstance(gate, dict) and isinstance(gate.get("open"), bool) and isinstance(gate.get("reasons"), list), (
        f"the reading has no gate {{open, reasons}}: {reading}")
    return gate


def reasons_by_condition(reading: dict) -> dict:
    """``{condition: reason}`` of a reading's gate; each reason has ``condition``, ``reading`` and ``threshold``."""
    found = {}
    for reason in gate_of(reading)["reasons"]:
        assert isinstance(reason, dict) and {"condition", "reading", "threshold"} <= set(reason), (
            f"a reason without condition, reading and threshold: {reason}")
        assert reason["condition"] in CONDITIONS, f"a reason with an unknown condition: {reason}"
        found[reason["condition"]] = reason
    return found


def session_pids(reading: dict) -> list[int]:
    sessions = reading.get("sessions")
    assert isinstance(sessions, list), f"the reading has no sessions list: {reading}"
    return sorted(int(s["pid"]) for s in sessions)


def same_path(a, b) -> bool:
    return os.path.realpath(str(a)) == os.path.realpath(str(b))
