"""W1-28 fix F10 (fixes-015a, release 0.1.5; CAP-05.a): a pause really stops.

While ``gov pause`` holds (its flag ``.gov-runtime/freeze``, first line ``FROZEN <who> <when>``):
- the dispatch pass (``gov dispatch tick``) starts nothing, and its output names ``PAUSED``;
- ``gov launch`` is refused with the error code ``PAUSED``, the message naming the pause;
- ``gov release <version> --patch`` is refused with ``PAUSED`` and builds nothing;
and ``gov pause`` sends one stop message (a ``wake``, text naming the pause) to the inbox of every running session
(the machine registry ``~/.gov-os/machine/sessions/<pid>.json``, its ``address``), none to a session whose process is gone.

Each case builds a planted project with W2-121's fixture (a git repository, the stub launch command, a planted process
table and machine); the pause is planted by writing the flag, except in the cases that run ``gov pause`` itself.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

_W2_121 = str(Path(__file__).resolve().parents[1] / "W2-121")
if _W2_121 not in sys.path:
    sys.path.insert(0, _W2_121)

import w2_121_support as support  # noqa: E402

FLAG_REL = ".gov-runtime/freeze"
SESSIONS = (("engineer", "DAEO-a901"), ("orchestrator", "DAEO-a902"))


@pytest.fixture
def project(tmp_path):
    planted = support.Project(tmp_path)
    try:
        yield planted
    finally:
        planted.cleanup()


def plant_pause(p) -> None:
    flag = p.root / FLAG_REL
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text("FROZEN owner 2026-11-22T00:00:00Z\n", encoding="utf-8")


def plant_session(p, role: str, ticket: str, *, running: bool = True) -> str:
    """A registered session (as ``gov launch`` writes it) whose process is in the planted table, or gone."""
    pid = p.plant_process(["claude", "--print"])
    if not running:
        p.remove_process(pid)
    address = f"{role}:{ticket}"
    folder = p.home / ".gov-os" / "machine" / "sessions"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{pid}.json").write_text(json.dumps({
        "pid": pid, "repository": str(p.root), "ticket": ticket, "role": role,
        "started": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()), "address": address}), encoding="utf-8")
    return address


def inbox(p, address: str) -> list[dict]:
    path = p.home / ".gov-os" / "inbox" / address / "messages.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def refusal(run) -> tuple[str | None, str]:
    """The error code and message of a refused command: from the ``--json`` envelope, else the stderr line."""
    try:
        error = json.loads(run.out).get("error") or {}
        if error:
            return error.get("code"), str(error.get("message", ""))
    except ValueError:
        pass
    for line in run.err.splitlines():
        parts = line.split(": ", 2)
        if len(parts) == 3 and parts[1].isupper():
            return parts[1], parts[2]
    return None, run.err


# --- gov pause: one stop message per running session ----------------------------------------------------------

def test_pause_sends_one_stop_message_to_each_running_session(project):
    p = project
    addresses = [plant_session(p, role, ticket) for role, ticket in SESSIONS]
    done = p.gov("pause", "--json")
    assert done.code == 0, done
    assert (p.root / FLAG_REL).is_file(), "gov pause set no flag"
    for address in addresses:
        found = inbox(p, address)
        assert len(found) == 1, f"{address}: {len(found)} messages after gov pause, one stop message is due\n{done}"
        assert found[0]["kind"] == "wake", f"a stop message that cannot wake its session: {found[0]}"
        assert "pause" in found[0]["text"].lower(), f"the stop message does not name the pause: {found[0]}"


def test_pause_sends_no_message_to_a_session_whose_process_is_gone(project):
    p = project
    live = plant_session(p, "engineer", "DAEO-a901")
    gone = plant_session(p, "engineer", "DAEO-a903", running=False)
    assert p.gov("pause", "--json").code == 0
    assert len(inbox(p, live)) == 1
    assert inbox(p, gone) == [], "a stop message went to a session that is not running"


# --- gov launch ------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("role", ["engineer", "lead"])
def test_launch_is_refused_with_paused_while_paused(project, role):
    p = project
    entry = p.add_ticket(901)
    plant_pause(p)
    done = p.gov("launch", role, entry.ticket, "--json")
    code, message = refusal(done)
    assert done.code != 0, done
    assert code == "PAUSED", f"gov launch {role} while paused: code {code!r}, not PAUSED\n{done}"
    assert "pause" in message.lower(), f"the message does not name the pause: {message}"


# --- the dispatch pass -----------------------------------------------------------------------------------------

def test_dispatch_tick_starts_nothing_while_paused(project):
    p = project
    p.ready(p.add_ticket(901))
    plant_pause(p)
    done = p.tick()
    p.settle()
    assert p.launches() == [], f"a dispatch pass started a session while paused\n{done}"
    started = p.state / "started.txt"
    assert not started.exists() or not started.read_text(encoding="utf-8").strip(), "a start was recorded while paused"
    shown = done.out + done.err
    if (p.state / "status.txt").is_file():
        shown += (p.state / "status.txt").read_text(encoding="utf-8")
    assert "PAUSED" in shown, f"the pass does not say PAUSED anywhere in its output or status\n{done}"


def test_dispatch_tick_still_starts_a_session_when_not_paused(project):
    """Guard: the same project with no pause starts its ready ticket, so the case above shows the pause and nothing else."""
    p = project
    p.ready(p.add_ticket(901))
    assert p.tick().code == 0
    p.wait_launches(1)


# --- gov release --patch ---------------------------------------------------------------------------------------

def test_patch_release_is_refused_with_paused_while_paused(project):
    p = project
    plant_pause(p)
    p.extra_env["GOV_ROLE"] = "orchestrator"
    head = support.git(p.root, "rev-parse", "HEAD").strip()
    done = p.gov("release", "0.1.1", "--patch", "--json")
    code, message = refusal(done)
    assert done.code != 0, done
    assert code == "PAUSED", f"gov release --patch while paused: code {code!r}, not PAUSED\n{done}"
    assert "pause" in message.lower(), f"the message does not name the pause: {message}"
    assert not (p.root / "docs" / "releases").exists(), "a release record was written while paused"
    assert support.git(p.root, "rev-parse", "HEAD").strip() == head, "a commit was made while paused"
