"""Unit tests for W2-205's two kernel hooks (the run-time tool, slice 3).

- ``stop.py`` runs the Stop check (``gov.msg.stopcheck.check``) after its checkpoint and prints the block decision
  (RT-2, the wake carrier): once per wake message, with or without a ticket, never when ``stop_hook_active`` is set.
- ``sessionstart.py`` puts the recorded next step first, ahead of every other part, with the inbox line (RT-5, RT-6).

Every hook is a child process with a ``HOME`` under ``tmp_path``: never the real ``~/.gov-os``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOKS = REPO_ROOT / "template" / "governance" / "kernel" / "hooks"
TICKET = "TEST-abcd"
ADDRESS = f"worker:{TICKET}:engineer"
ORCH = ".gov-runtime/scratch/orchestrator/CHECKPOINT.md"
FIRST = "Resume at the recorded next step"
INBOX_LINE = "Read your inbox: gov msg read"

_GIT_ENV = {
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid",
}


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / ".tickets").mkdir(parents=True)
    (root / ".tickets" / f"{TICKET}.md").write_text(
        f"---\nid: {TICKET}\nstatus: in_progress\ntitle: T\nsources: []\ndepends_on: []\n---\n# T\n")
    (root / "docs" / "checkpoints" / TICKET).mkdir(parents=True)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(tmp_path), **_GIT_ENV}
    for args in (("init", "-q", "-b", "main"), ("add", "-A"), ("commit", "-q", "-m", "init")):
        subprocess.run(["git", "-C", str(root), *args], env=env, capture_output=True, check=True)
    return root


def _checkpoint(root: Path, next_action: str, number: int = 1) -> str:
    rel = f"docs/checkpoints/{TICKET}/CP-{TICKET}-{number:04d}.md"
    (root / rel).write_text(
        f"---\nid: CP-{TICKET}-{number:04d}\ntype: checkpoint\nstatus: ACTIVE\n"
        f"state_class: NARRATIVE\ntitle: {TICKET} at compaction\n"
        f"task: {TICKET}\ntask_status: in_progress\ntrigger: compaction\n"
        f"next_action: {next_action}\ncreated: 2026-10-05T00:00:00Z\n"
        f"inputs:\n  - id: {TICKET}\n    version: abc1234\n"
        "    hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000'\n"
        f"---\n\n# CP-{TICKET}-{number:04d}\n")
    return rel


def _message(home: Path, address: str, ident: str, kind: str, text: str) -> None:
    place = home / ".gov-os" / "inbox" / address
    place.mkdir(parents=True, exist_ok=True)
    line = {"id": ident, "at": "2026-11-19T00:00:00Z", "from": "cto", "to": address, "kind": kind, "text": text}
    with open(place / "messages.jsonl", "a", encoding="utf-8") as handle:
        handle.write(json.dumps(line) + "\n")


def _run(name: str, root: Path, home: Path, stdin: dict, *, ticket: str | None = TICKET, role: str = "engineer",
         address: str | None = None, pythonpath: bool = True, path: str | None = None):
    env = {
        "PATH": path or os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "CLAUDE_PROJECT_DIR": str(root),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GOV_ROLE": role,
    }
    if pythonpath:
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
    if ticket is not None:
        env["GOV_TICKET"] = ticket
    if address is not None:
        env["GOV_MSG_ADDRESS"] = address
    return subprocess.run([sys.executable, str(HOOKS / name)], input=json.dumps(stdin), capture_output=True,
                          text=True, cwd=str(root), env=env, timeout=30, check=False)


def _records(root: Path) -> list[Path]:
    return sorted((root / ".gov-runtime" / "scratch" / "checkpoints" / TICKET).glob("CP-*.md"))


def _context(run) -> str:
    assert run.returncode == 0, run.stderr
    if not run.stdout.strip():
        return ""
    return json.loads(run.stdout)["hookSpecificOutput"]["additionalContext"]


# --------------------------------------------------------------------------
# stop.py: the Stop check after the checkpoint
# --------------------------------------------------------------------------

STOP = {"hook_event_name": "Stop", "session_id": "s1", "last_assistant_message": "Done."}


def test_stop_prints_the_block_for_an_unread_wake_after_its_checkpoint(tmp_path):
    root = _project(tmp_path)
    _message(tmp_path, ADDRESS, "end:1", "wake", "the worker ended with exit code 0")
    run = _run("stop.py", root, tmp_path, STOP, address=ADDRESS)
    assert run.returncode == 0
    decision = json.loads(run.stdout)
    assert decision["decision"] == "block"
    assert "the worker ended with exit code 0" in decision["reason"]
    assert len(_records(root)) == 1, "the checkpoint is still written"


def test_stop_blocks_once_per_wake_message(tmp_path):
    root = _project(tmp_path)
    _message(tmp_path, ADDRESS, "end:1", "wake", "first")
    assert _run("stop.py", root, tmp_path, STOP, address=ADDRESS).stdout.strip()
    again = _run("stop.py", root, tmp_path, STOP, address=ADDRESS)
    assert again.returncode == 0 and again.stdout == ""
    _message(tmp_path, ADDRESS, "end:2", "wake", "second")
    newer = _run("stop.py", root, tmp_path, STOP, address=ADDRESS)
    assert "second" in json.loads(newer.stdout)["reason"]


def test_stop_prints_nothing_for_a_notice_or_with_no_address(tmp_path):
    root = _project(tmp_path)
    _message(tmp_path, ADDRESS, "n:1", "notice", "idle")
    notice = _run("stop.py", root, tmp_path, STOP, address=ADDRESS)
    assert notice.returncode == 0 and notice.stdout == ""
    _message(tmp_path, ADDRESS, "end:1", "wake", "first")
    none = _run("stop.py", root, tmp_path, STOP, address=None)
    assert none.returncode == 0 and none.stdout == ""
    assert len(_records(root)) == 2, "each stop with a ticket writes its checkpoint"


def test_stop_checks_a_session_with_an_address_and_no_ticket(tmp_path):
    root = _project(tmp_path)
    _message(tmp_path, "operator", "end:1", "wake", "a job ended")
    run = _run("stop.py", root, tmp_path, STOP, ticket=None, address="operator")
    assert run.returncode == 0
    assert "a job ended" in json.loads(run.stdout)["reason"]
    assert not _records(root), "no ticket, no checkpoint"


def test_stop_hook_active_neither_blocks_nor_uses_up_the_message(tmp_path):
    root = _project(tmp_path)
    _message(tmp_path, ADDRESS, "end:1", "wake", "first")
    active = _run("stop.py", root, tmp_path, {**STOP, "stop_hook_active": True}, address=ADDRESS)
    assert active.returncode == 0 and active.stdout == ""
    assert not _records(root)
    later = _run("stop.py", root, tmp_path, STOP, address=ADDRESS)
    assert "first" in json.loads(later.stdout)["reason"], "the message still blocks the next real stop"


def test_stop_without_gov_exits_0_prints_no_decision_and_says_so(tmp_path):
    root = _project(tmp_path)  # a product: no copier.yml, so no src/ is put on the import path
    _message(tmp_path, ADDRESS, "end:1", "wake", "first")
    run = _run("stop.py", root, tmp_path, STOP, address=ADDRESS, pythonpath=False)
    if "no gov importable" not in run.stderr:  # this interpreter has a gov of its own installed
        return
    assert run.returncode == 0 and run.stdout == ""
    assert "the stop check was not run" in run.stderr


def test_stop_with_input_that_is_no_json_exits_0_silently(tmp_path):
    root = _project(tmp_path)
    run = subprocess.run([sys.executable, str(HOOKS / "stop.py")], input="not json", capture_output=True, text=True,
                         cwd=str(root), timeout=30, check=False,
                         env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(tmp_path),
                              "CLAUDE_PROJECT_DIR": str(root), "PYTHONPATH": str(REPO_ROOT / "src"),
                              "GOV_TICKET": TICKET, "GOV_MSG_ADDRESS": ADDRESS})
    assert run.returncode == 0 and run.stdout == ""


# --------------------------------------------------------------------------
# sessionstart.py: the recorded next step first
# --------------------------------------------------------------------------

def test_sessionstart_begins_with_the_recorded_next_step_and_the_inbox_line(tmp_path):
    root = _project(tmp_path)
    rel = _checkpoint(root, "Wire the parser into the CLI")
    for source in ("compact", "clear", "resume"):
        ctx = _context(_run("sessionstart.py", root, tmp_path, {"source": source}))
        lines = ctx.split("\n")
        assert lines[0] == f"{FIRST} ({TICKET}): Wire the parser into the CLI (checkpoint {rel})", source
        assert lines[1] == INBOX_LINE, source


def test_sessionstart_keeps_the_optional_checkpoint_resume_line(tmp_path):
    root = _project(tmp_path)
    _checkpoint(root, "Wire the parser into the CLI")
    ctx = _context(_run("sessionstart.py", root, tmp_path, {"source": "compact"}))
    assert "Checkpoint resume: ticket=TEST-abcd, next_action=Wire the parser into the CLI" in ctx


def test_sessionstart_names_the_latest_checkpoint(tmp_path):
    root = _project(tmp_path)
    _checkpoint(root, "The older step")
    newer = _checkpoint(root, "The newer step", number=2)
    text = (root / newer).read_text().replace("2026-10-05T00:00:00Z", "2026-10-06T00:00:00Z")
    (root / newer).write_text(text)
    ctx = _context(_run("sessionstart.py", root, tmp_path, {"source": "compact"}))
    assert ctx.startswith(f"{FIRST} ({TICKET}): The newer step (checkpoint {newer})")


def test_sessionstart_with_no_checkpoint_injects_no_such_part(tmp_path):
    root = _project(tmp_path)
    run = _run("sessionstart.py", root, tmp_path, {"source": "compact"})
    ctx = _context(run)
    assert FIRST not in ctx and INBOX_LINE not in ctx


def test_sessionstart_on_startup_or_with_no_ticket_injects_no_such_part(tmp_path):
    root = _project(tmp_path)
    _checkpoint(root, "Wire the parser into the CLI")
    startup = _context(_run("sessionstart.py", root, tmp_path, {"source": "startup"}))
    assert FIRST not in startup and INBOX_LINE not in startup
    no_ticket = _context(_run("sessionstart.py", root, tmp_path, {"source": "compact"}, ticket=None))
    assert FIRST not in no_ticket and INBOX_LINE not in no_ticket


def test_sessionstart_puts_the_next_step_ahead_of_the_orchestrators_parts(tmp_path):
    root = _project(tmp_path)
    rel = _checkpoint(root, "Land the ticket")
    orch = root / ORCH
    orch.parent.mkdir(parents=True)
    orch.write_text("# C\n\n## RESUME HERE\n\n- SECRET-71\n")
    stamp = time.time() - 60
    os.utime(orch, (stamp, stamp))
    ctx = _context(_run("sessionstart.py", root, tmp_path, {"source": "resume"}, role="orchestrator"))
    assert ctx.startswith(f"{FIRST} ({TICKET}): Land the ticket (checkpoint {rel})\n{INBOX_LINE}\n\n")
    assert ctx.index(FIRST) < ctx.index(ORCH) < ctx.index("SECRET-71")


def test_sessionstart_never_trims_the_next_step_away_and_stays_within_the_cap(tmp_path):
    root = _project(tmp_path)
    rel = _checkpoint(root, "Land the ticket")
    orch = root / ORCH
    orch.parent.mkdir(parents=True)
    orch.write_text("# C\n\n## RESUME HERE\n\n- SECRET-71\n")
    stamp = time.time() - 60
    os.utime(orch, (stamp, stamp))
    ready = tmp_path / "ready.txt"
    ready.write_text("".join(f"T-{i:04d} a ready ticket\n" for i in range(1000)))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "tk").write_text(f"#!/bin/sh\ncat '{ready}'\n")
    (bin_dir / "tk").chmod(0o755)
    path = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '/usr/bin:/bin')}"
    ctx = _context(_run("sessionstart.py", root, tmp_path, {"source": "compact"}, role="orchestrator", path=path))
    assert len(ctx) <= 10_000
    assert ctx.startswith(f"{FIRST} ({TICKET}): Land the ticket (checkpoint {rel})\n{INBOX_LINE}\n\n")
    assert "SECRET-71" in ctx, "the orchestrator's critical parts are kept"
    assert "T-0000 a ready ticket" in ctx and "T-0999" not in ctx, "the optional parts are the ones trimmed"


def test_sessionstart_counts_the_next_step_when_it_fits_the_resume_section(tmp_path):
    """A RESUME HERE section that fits alone but not beside the first part is named by its lines, never cut."""
    root = _project(tmp_path)
    _checkpoint(root, "Land the ticket " + "y" * 400)
    orch = root / ORCH
    orch.parent.mkdir(parents=True)
    orch.write_text("# C\n\n## RESUME HERE\n\n" + "x" * 9400 + "\n")
    stamp = time.time() - 60
    os.utime(orch, (stamp, stamp))
    ctx = _context(_run("sessionstart.py", root, tmp_path, {"source": "compact"}, role="orchestrator"))
    assert len(ctx) <= 10_000
    assert ctx.startswith(FIRST)
    assert "x" * 100 not in ctx and "none of it is shown here" in ctx
