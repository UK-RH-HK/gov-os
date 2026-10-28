"""Helpers for the W2-57 acceptance tests: load out of the close (DAEO-cy5o, profile FULL).

Batch A holds the rulesync probe (KPI line 1, DEC-892 item 2) and the doctor probes (KPI line 2). Every case
builds what it needs under pytest's ``tmp_path``: an adopted project as W1-38's suite builds it (the template's
``.rulesync/`` sources, the kernel, the tool registry, the check's declaration), or a small git repository made
from scratch. Stand-in tools (a late or silent rulesync, a late tool for ``gov doctor``) are short shell scripts
in a folder of the case, reached the way a user's tools are: first on the ``PATH``, or named by ``RULESYNC_BIN``.
No product code is imported or patched.

The code under test is this worktree's ``src/``: the declared check runs with ``PYTHONPATH`` set to it (W1-38's
``run_portability_check``), and ``gov`` runs from it (W1-07's ``run_gov_with_code`` with this worktree as the code
root), whatever ``PYTHONPATH`` the caller has. ``code_under_test()`` shows it once per session.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import signal
import subprocess
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_W1_38 = str(_HERE.parent / "W1-38")
if _W1_38 not in sys.path:
    sys.path.insert(0, _W1_38)

import w1_38_support as adapters  # noqa: E402  (the adopted project, the declared check, gov check)

cli = adapters.cli_support          # W1-07's gov command line: the launcher, the sandbox, the envelope

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
REAL_RULESYNC = adapters.RULESYNC_BIN

# ---------------------------------------------------------------------------
# The figures the KPI gives. The new limits are the implementer's, measured under the close's parallel load;
# these tests hold only "well past the old limit" and "bounded" (DEC-892 item 2, I4 F2 and F5).
# ---------------------------------------------------------------------------

OLD_RULESYNC_LIMIT_S = 10   # each of the portability check's two rulesync calls, today
LATE_RULESYNC_S = 15        # well past it (I4 planted 11 s; the KPI asks at least 15 s)
SILENT_S = 600              # a stand-in that never answers within any wait of these cases

# gov doctor's probes with a time limit today (I4 F5): a tool's version, a venv's freeze hash, Claude Code's version.
DOCTOR_PROBES = {
    "tool-version": {"today_s": 5, "late_s": 15},
    "tool-own-version-command": {"today_s": 5, "late_s": 15},
    "venv-freeze-hash": {"today_s": 10, "late_s": 25},
    "claude-code-version": {"today_s": 3, "late_s": 15},
}

ABSENT_CODE = "RULESYNC_ABSENT"     # the check's finding for a rulesync that is not there, as today
NO_ANSWER_IN_TIME = adapters.NO_ANSWER_IN_TIME
READ_AS_ABSENT = adapters.READ_AS_ABSENT


# ---------------------------------------------------------------------------
# The code under test
# ---------------------------------------------------------------------------

def code_under_test() -> Path:
    """Where ``import gov`` resolves with the ``PYTHONPATH`` the helpers give: this worktree's ``src/``."""
    done = subprocess.run(
        [sys.executable, "-c", "import gov; print(gov.__file__)"], capture_output=True, text=True, timeout=60,
        env={**os.environ, "PYTHONPATH": str(SRC)}, stdin=subprocess.DEVNULL,
    )
    assert done.returncode == 0, f"the gov package cannot be imported from {SRC}: {done.stderr[-300:]}"
    found = Path(done.stdout.strip()).resolve()
    assert found.is_relative_to(SRC.resolve()), f"gov is imported from {found}, not from this worktree's {SRC}"
    return found


# ---------------------------------------------------------------------------
# Stand-in tools
# ---------------------------------------------------------------------------

class StandIns:
    """Stand-in tools in one folder of the case. Each records its process id, so a stand-in still waiting when
    the case ends (a silent one whose caller did not stop it) is stopped then and outlives no case."""

    def __init__(self, folder: Path):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self._pids = self.folder / ".pids"

    def write(self, name: str, body: str) -> Path:
        tool = self.folder / name
        tool.write_text(
            f"#!/bin/bash\necho $$ >> {shlex.quote(str(self._pids))}\n{body}\n", encoding="utf-8",
        )
        tool.chmod(0o755)
        return tool

    def path(self) -> str:
        """The ``PATH`` with this folder first."""
        return f"{self.folder}:{os.environ.get('PATH', '/usr/bin:/bin')}"

    def stop_leftovers(self) -> list[int]:
        """Stop every stand-in still running; returns their ids (a silent stand-in left by its caller)."""
        stopped = []
        if not self._pids.is_file():
            return stopped
        for line in self._pids.read_text(encoding="utf-8").split():
            pid = int(line)
            try:
                command = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
            except OSError:
                continue
            if command.startswith("sleep ") or str(self.folder) in command:
                try:
                    os.kill(pid, signal.SIGKILL)
                    stopped.append(pid)
                except OSError:
                    pass
        return stopped


def late_rulesync(stand_ins: StandIns, *, call: str, seconds: int = LATE_RULESYNC_S) -> Path:
    """A rulesync that answers ``call`` (``--version`` or ``generate``) only after ``seconds``, and is the
    installed rulesync in every other respect."""
    return stand_ins.write("rulesync", (
        f'if [[ "$1" == {shlex.quote(call)} ]]; then sleep {seconds}; fi\n'
        f"exec {shlex.quote(str(REAL_RULESYNC))} \"$@\""
    ))


def late_rulesync_both(stand_ins: StandIns, seconds: int = LATE_RULESYNC_S) -> Path:
    """A rulesync that answers both of the check's calls only after ``seconds`` each."""
    return stand_ins.write("rulesync", (
        f'if [[ "$1" == "--version" || "$1" == "generate" ]]; then sleep {seconds}; fi\n'
        f"exec {shlex.quote(str(REAL_RULESYNC))} \"$@\""
    ))


def silent_rulesync(stand_ins: StandIns, *, call: str) -> Path:
    """A rulesync that never answers ``call`` within any wait of these cases; the installed one otherwise."""
    return stand_ins.write("rulesync", (
        f'if [[ "$1" == {shlex.quote(call)} ]]; then exec sleep {SILENT_S}; fi\n'
        f"exec {shlex.quote(str(REAL_RULESYNC))} \"$@\""
    ))


def failing_rulesync(stand_ins: StandIns, reason: str) -> Path:
    """A rulesync that fails at once, with its own reason."""
    return stand_ins.write("rulesync", f"echo {shlex.quote(reason)} >&2\nexit 1")


def late_tool(stand_ins: StandIns, name: str, seconds: int, answer: str) -> Path:
    """A tool that prints ``answer`` to whatever it is asked, after ``seconds``."""
    return stand_ins.write(name, f"sleep {seconds}\nprintf '%s\\n' {shlex.quote(answer)}")


def silent_tool(stand_ins: StandIns, name: str) -> Path:
    return stand_ins.write(name, f"exec sleep {SILENT_S}")


# ---------------------------------------------------------------------------
# The portability check
# ---------------------------------------------------------------------------

def check_with(project: Path, rulesync: Path | None, stand_ins: StandIns | None = None, **env: str):
    """The declared check in ``project``, its rulesync named by ``RULESYNC_BIN`` and first on the ``PATH``
    (``rulesync=None``: the caller's environment decides)."""
    override = dict(env)
    if rulesync is not None:
        override["RULESYNC_BIN"] = str(rulesync)
        override.setdefault("PATH", stand_ins.path() if stand_ins else os.environ.get("PATH", "/usr/bin:/bin"))
    return adapters.run_portability_check(project, env_override=override)


def printed(result) -> dict:
    """The declared check's printed result: ``{"findings": [...], "compared": {...}}``."""
    adapters.printed_findings(result)   # fails, with what it printed, when there is no result
    return json.loads(result.stdout)


def gov_check_entry(project: Path, sandbox, monkeypatch, stand_ins: StandIns | None = None):
    """``(check entry, family entry, run)`` of the adapter/model-portability family after ``gov check --json``,
    with the stand-ins first on the ``PATH`` gov runs with (``gov`` builds its environment from scratch and
    passes ``RULESYNC_BIN`` on to no check, so the check finds rulesync on the ``PATH``)."""
    if stand_ins is not None:
        monkeypatch.setenv("PATH", stand_ins.path())
    run = adapters.run_gov(project, sandbox, "check", "--json")
    entry, family = adapters.portability_entries(adapters.check_result(run))
    return entry, family, run


def timeout_findings(findings: list) -> list[dict]:
    return adapters.timeout_findings(findings)


def absent_findings(findings: list) -> list[dict]:
    return [f for f in findings if isinstance(f, dict) and READ_AS_ABSENT.search(str(f.get("message", "")))]


# ---------------------------------------------------------------------------
# gov doctor in a small repository
# ---------------------------------------------------------------------------

def git(repo: Path, *args: str) -> str:
    return cli.git(repo, *args)


def doctor_repository(root: Path, tools: list[dict] | None = None) -> Path:
    """A committed git repository made from scratch, with ``governance/project/tool-registry.yaml`` holding
    ``tools`` (DEC-127: a project records the tools it expects) when given."""
    repo = Path(root)
    repo.mkdir(parents=True)
    (repo / "README.md").write_text("A repository for gov doctor's probes (W2-57).\n", encoding="utf-8")
    if tools is not None:
        registry = repo / "governance" / "project" / "tool-registry.yaml"
        registry.parent.mkdir(parents=True)
        registry.write_text(yaml.safe_dump({"tools": tools}, sort_keys=False), encoding="utf-8")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "gc.auto", "0")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "a repository for gov doctor")
    return repo


def run_doctor(repo: Path, sandbox, monkeypatch, stand_ins: StandIns | None = None):
    """``gov doctor --json`` in ``repo`` with this worktree's code, the stand-ins first on the ``PATH``."""
    if stand_ins is not None:
        monkeypatch.setenv("PATH", stand_ins.path())
    return cli.run_gov_with_code(REPO_ROOT, repo, sandbox, "doctor", "--json")


def doctor_result(run) -> dict:
    """The sections ``gov doctor --json`` reports: under ``result``, or under ``error.details`` when a part
    failed (``DOCTOR_UNHEALTHY``, API-0002)."""
    envelope = run.envelope()
    result = envelope.get("result") or (envelope.get("error") or {}).get("details") or {}
    assert isinstance(result, dict) and "tools" in result, f"gov doctor reported no sections\n{run.describe()}"
    return result


def tool_entry(result: dict, name: str) -> dict:
    tools = (result.get("tools") or {}).get("tools") or []
    found = [entry for entry in tools if isinstance(entry, dict) and entry.get("name") == name]
    assert len(found) == 1, f"gov doctor's tools part reports {len(found)} entries for {name}: {tools}"
    return found[0]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def section_names(result: dict) -> set[str]:
    """The parts of ``gov doctor``'s answer, as it names them, in the three spellings a message may use."""
    names = {key for key in result if key != "healthy"}
    return {spelling for name in names for spelling in (name, name.replace("_", " "), name.replace("_", "-"))}


def write_latin1_rename(repo: Path) -> None:
    """Ordinary means: ``core.quotePath`` off (git's setting for file names that are not ASCII), a file whose
    name is Latin-1, not UTF-8, committed and then renamed, so git's log of renames holds that name."""
    git(repo, "config", "core.quotePath", "false")
    name = b"caf\xe9-notes.txt"
    with open(os.path.join(os.fsencode(str(repo)), name), "wb") as handle:
        handle.write(b"notes written on a Latin-1 system\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "notes")
    git(repo, "mv", os.fsdecode(name), os.fsdecode(b"caf\xe9-notes-old.txt"))
    git(repo, "commit", "-q", "-m", "notes renamed")


def names_any(text: str, names: set[str]) -> bool:
    return any(re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", text) for name in names)
