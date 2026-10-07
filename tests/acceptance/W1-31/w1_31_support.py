"""Support code for the W1-31 acceptance tests (the governance share counter, ``gov telemetry``).

How the cases run (README, "The interface the cases assume"):

- **Through the command line only**: ``gov telemetry <ticket> --json`` through W1-07's console-script stand-in,
  its API-0002 envelope and its exit code. Nothing of ``src/gov/telemetry/`` is imported.
- **Every project is a temporary git repository built from scratch** (a ticket file, a commit, checkpoint
  records). Nothing of this repository is copied; the code under test is this worktree's ``src/``.
- **No case reads the session logs of this machine.** Each case writes its own session logs in a temporary
  folder and gives that folder to the command, and to ccusage, as ``CLAUDE_CONFIG_DIR``; ``HOME`` is a temporary
  folder too, so that a counter which ignored the variable would still find no real log.
- **Deterministic, no network**: ccusage runs with its built-in prices (``--offline``).
"""

from __future__ import annotations

import json
import os
import pwd
import shutil
import site
import subprocess
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_W1_07 = str(_HERE.parent / "W1-07")
if _W1_07 not in sys.path:
    sys.path.insert(0, _W1_07)

import w1_07_support as cli_support  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
COMMAND = "telemetry"
NOT_MEASURED = "not measured"          # the word ``gov close`` already writes for a field it did not measure
EXIT_OK, EXIT_GOV_ERROR, EXIT_USAGE, EXIT_NOT_MEASURED = 0, 1, 2, 3

TICKET, OTHER_TICKET = "PROJ-aaaa", "PROJ-bbbb"
WBS = "T-01"
MODEL = "claude-opus-5-5"
SESSION_A = "11111111-1111-4111-8111-111111111111"
SESSION_B = "22222222-2222-4222-8222-222222222222"
SESSION_OTHER = "33333333-3333-4333-8333-333333333333"
SESSION_NOWHERE = "99999999-9999-4999-8999-999999999999"

# DEC-086: the seven sources of governance text, as the result names them.
SOURCES = ("instruction_files", "sessionstart_packet", "hook_output", "gov_output", "mcp_definitions",
           "checkpoint_records", "close_records")
# Ticket KPI, second success line: the Contract v3 P1 fields, as the result names them.
P1_FIELDS = ("sessions", "model", "role", "ticket", "skill_versions", "tool_versions", "packet_id",
             "retrieval_queries", "retrieval_hits", "tokens_in", "tokens_out", "cost", "files_written", "tests",
             "retries", "handoffs", "decisions", "owner_interventions")
# Third success line: taken from the harness session log.
LOG_FIELDS = ("agent", "provider", "latency", "files_read")
# A bare temporary project holds no trace of these: nothing may be invented for them.
NO_TRACE_FIELDS = ("retrieval_queries", "retrieval_hits", "retries", "handoffs", "owner_interventions")
LEARNING_METRICS = ("kpi_disputes", "acceptance_tests_rewritten", "governance_share")
SANDBOX_LINE = "sandbox_system_prompt_tokens"

# The registered place of ccusage (governance/project/tool-registry.yaml: Node v22.23.3).
CCUSAGE_REL = ".nvm/versions/node/v22.23.3/bin"
SYSTEM_PATH = "/usr/bin:/bin"

GIT_ENV = {
    "GIT_AUTHOR_NAME": "A Worker", "GIT_AUTHOR_EMAIL": "worker@example.invalid",
    "GIT_COMMITTER_NAME": "A Worker", "GIT_COMMITTER_EMAIL": "worker@example.invalid",
    "GIT_AUTHOR_DATE": "2026-10-07T09:00:00+00:00", "GIT_COMMITTER_DATE": "2026-10-07T09:00:00+00:00",
    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
}


# --------------------------------------------------------------------------
# ccusage
# --------------------------------------------------------------------------

def ccusage_dir():
    """The folder that holds the registered ccusage, or None where this machine has none."""
    home = Path(pwd.getpwuid(os.getuid()).pw_dir)  # the real home, whatever HOME says
    registered = home / CCUSAGE_REL
    if (registered / "ccusage").is_file():
        return registered
    found = shutil.which("ccusage")
    return Path(found).parent if found else None


def ccusage_sessions(logs, home):
    """What ccusage itself prints for the temporary log folder ``logs``: ``{session id: its row}``."""
    folder = ccusage_dir()
    assert folder is not None, "ccusage is not on this machine"
    done = subprocess.run(
        [str(folder / "ccusage"), "claude", "session", "--json", "--offline"],
        env={"PATH": f"{folder}:{SYSTEM_PATH}", "HOME": str(home), "CLAUDE_CONFIG_DIR": str(logs)},
        capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    assert done.returncode == 0, f"ccusage failed on the fixture's logs: {done.stderr}"
    return {row["sessionId"]: row for row in json.loads(done.stdout)["sessions"]}


# --------------------------------------------------------------------------
# Session logs, in the form ccusage 20.0.26 reads (README, "The session logs the cases write")
# --------------------------------------------------------------------------

def write_session(logs, session_id, turns, *, cwd="/work/project", model=MODEL):
    """Write the log of one session: ``<logs>/projects/<cwd with - for />/<session id>.jsonl``.

    ``turns`` is a list of ``(input, output, cache_creation, cache_read)``: one assistant line each, after one
    user line. Returns the file.
    """
    folder = Path(logs) / "projects" / cwd.replace("/", "-")
    folder.mkdir(parents=True, exist_ok=True)
    common = {"isSidechain": False, "userType": "external", "cwd": cwd, "sessionId": session_id,
              "version": "2.1.288", "gitBranch": "main"}
    lines = [{**common, "parentUuid": None, "type": "user", "message": {"role": "user", "content": "work"},
              "uuid": f"{session_id[:8]}-u0", "timestamp": "2026-10-07T10:00:00.000Z"}]
    for number, (fresh_in, out, created, read) in enumerate(turns, start=1):
        lines.append({
            **common, "parentUuid": lines[-1]["uuid"], "type": "assistant",
            "message": {"id": f"msg_{session_id[:8]}_{number}", "type": "message", "role": "assistant",
                        "model": model, "content": [{"type": "text", "text": "done"}], "stop_reason": "end_turn",
                        "usage": {"input_tokens": fresh_in, "output_tokens": out,
                                  "cache_creation_input_tokens": created, "cache_read_input_tokens": read,
                                  "service_tier": "standard"}},
            "requestId": f"req_{session_id[:8]}_{number}", "uuid": f"{session_id[:8]}-a{number}",
            "timestamp": f"2026-10-07T10:{number:02d}:00.000Z"})
    path = folder / f"{session_id}.jsonl"
    # Compact JSON, as the harness writes it: ccusage 20.0.26 passes over a line written with a space after
    # its colons and reports no session for it (exit code 0), as it does for a folder without logs.
    path.write_text("".join(json.dumps(line, separators=(",", ":")) + "\n" for line in lines), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# A temporary project, built from scratch
# --------------------------------------------------------------------------

def git(root, *args):
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          env={"PATH": os.environ.get("PATH", SYSTEM_PATH), "HOME": str(root), **GIT_ENV})
    assert done.returncode == 0, f"git {' '.join(args)} failed: {done.stderr}"
    return done.stdout


def ticket_text(ticket, profile="STANDARD"):
    lines = ["---", f"id: {ticket}", "status: in_progress", "deps: []", "links: []",
             "created: 2026-10-01T00:00:00Z", "type: task", "priority: 2", "assignee: engineer",
             f"external-ref: {WBS}", f"wbs_id: {WBS}", "title: A fixture ticket", "class: implementation",
             "state_class: AUTHORITATIVE", "role: engineer", "allowed_paths:", "- src/example/**",
             "kpis:", "  success:", "  - it works", "  failure:", "  - it does not"]
    if profile is not None:
        lines.append(f"profile: {profile}")
    return "\n".join(lines + ["---", "# A fixture ticket", ""])


def checkpoint_text(ticket, number, filler=""):
    """A checkpoint record of ``ticket`` in the kernel's form, padded to a whole number of 4-character tokens,
    so that the count is the same whether a counter rounds per record or over all of them."""
    ident = f"CP-{ticket}-{number:04d}"
    text = ("---\n"
            f"id: {ident}\ntype: checkpoint\nstatus: ACTIVE\nstate_class: NARRATIVE\n"
            f"title: {ticket} at stop\ntask: {ticket}\ntask_status: in_progress\ntrigger: stop\n"
            "next_action: resume\ncreated: '2026-10-07T09:30:00Z'\n"
            f"inputs:\n- id: {ticket}\n  version: untracked\n  hash: sha256:{'0' * 64}\n"
            "---\n\n"
            f"# {ident}\n\n## Next action\n\nresume {filler}\n")
    return text + "\n" * (-len(text) % 4)


def tokens(text):
    """W1-24's counter (``gov.context``), which W1-29's cap uses too: 4 characters a token, rounded up."""
    return -(-len(text) // 4)


class Project:
    """A temporary git repository with one in-progress ticket and one commit of that ticket."""

    def __init__(self, root, profile="STANDARD"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        git(self.root, "init", "-q", "-b", "main")
        self.write(".gitignore", ".gov-runtime/\n")
        self.write(f".tickets/{TICKET}.md", ticket_text(TICKET, profile))
        self.write(f".tickets/{OTHER_TICKET}.md", ticket_text(OTHER_TICKET))
        self.commit("tickets", "Role: orchestrator")
        self.write("src/example/a.py", "VALUE = 1\n")
        self.commit("the work", f"Task: {TICKET}", "Role: engineer", "Implements: CAP-00.a",
                    "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(text, bytes):
            path.write_bytes(text)
        else:
            path.write_text(text, encoding="utf-8")
        return path

    def commit(self, message, *trailers):
        git(self.root, "add", "-A")
        args = ["commit", "-q", "--no-gpg-sign", "--allow-empty", "-m", message]
        for trailer in trailers:
            args += ["--trailer", trailer]
        git(self.root, *args)

    def add_checkpoint(self, number, ticket=TICKET, filler="", automatic=False):
        """Write a checkpoint record of ``ticket`` and return its number of tokens."""
        base = ".gov-runtime/scratch/checkpoints" if automatic else "docs/checkpoints"
        text = checkpoint_text(ticket, number, filler)
        self.write(f"{base}/{ticket}/CP-{ticket}-{number:04d}.md", text)
        return tokens(text)


# --------------------------------------------------------------------------
# Running the command
# --------------------------------------------------------------------------

def run_env(sandbox, logs, path):
    env = {"PATH": path, "HOME": str(sandbox.home), "TMPDIR": str(sandbox.tmpdir), "LC_ALL": "C.UTF-8",
           "PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": str(sandbox.pycache), **GIT_ENV}
    if logs is not None:
        env["CLAUDE_CONFIG_DIR"] = str(logs)
    if site.ENABLE_USER_SITE:  # the installed packages of the interpreter running the suite (as W1-30 does)
        env["PYTHONUSERBASE"] = site.getuserbase()
    return env


def run_telemetry(project, sandbox, logs, *sessions, ticket=TICKET, path=None):
    """``gov telemetry <ticket> --json [--ticket-session <id>]...`` in the project, with ``logs`` as the
    session logs. ``path`` replaces ``PATH`` (the cases about an absent or failing ccusage give it)."""
    if path is None:
        folder = ccusage_dir()
        path = f"{folder}:{SYSTEM_PATH}" if folder else SYSTEM_PATH
    args = [COMMAND, ticket, "--json"]
    for session in sessions:
        args += ["--ticket-session", session]
    launcher = cli_support.write_launcher(REPO_ROOT, sandbox)
    started = time.perf_counter()
    done = subprocess.run([sys.executable, str(launcher), *args], cwd=str(getattr(project, "root", project)),
                          env=run_env(sandbox, logs, path), capture_output=True, text=True,
                          timeout=120, stdin=subprocess.DEVNULL)
    return cli_support.Run(tuple(args), done.returncode, done.stdout, done.stderr, time.perf_counter() - started)


# --------------------------------------------------------------------------
# Reading the answer
# --------------------------------------------------------------------------

def is_count(value):
    return type(value) is int and value >= 0


def is_number(value):
    return type(value) in (int, float) and value >= 0


def record(run):
    """The result of a run that answered with its record: exit code 0 (the share is a number) or 3 (it is
    "not measured"), ``ok: true``."""
    envelope = run.envelope()
    assert run.returncode in (EXIT_OK, EXIT_NOT_MEASURED) and envelope.get("ok") is True, \
        f"gov telemetry gave no record\n{run.describe()}"
    assert envelope.get("command") == COMMAND, run.describe()
    result = envelope["result"]
    assert isinstance(result, dict) and result, f"the record is empty\n{run.describe()}"
    return result


def assert_no_figure(run):
    """The run did not succeed and gave no share, token count or cost as a number."""
    assert run.returncode not in (EXIT_OK, EXIT_USAGE), \
        f"gov telemetry must not succeed here, and this is no usage error\n{run.describe()}"
    envelope = run.envelope()
    if envelope.get("ok") is False:
        assert envelope.get("error", {}).get("code"), f"a refusal names its code\n{run.describe()}"
        assert not envelope.get("result"), f"a refusal carries no record\n{run.describe()}"
        return envelope["error"]
    result = envelope["result"]
    assert run.returncode == EXIT_NOT_MEASURED, run.describe()
    for name in ("governance_share", "tokens_in", "tokens_out", "cache_read_tokens", "cost"):
        assert result.get(name) == NOT_MEASURED, \
            f"{name} is {result.get(name)!r}: it was not measured and must say so\n{run.describe()}"
    assert result["learning_metrics"]["governance_share"] == NOT_MEASURED, run.describe()
    return result
