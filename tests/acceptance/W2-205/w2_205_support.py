"""Support code for the W2-205 acceptance tests: the run-time tool, slice 3 (standard library only).

Every case drives a public interface of ticket DAEO-rt3s as a child process (``python3 -m gov.cli.main`` on this
worktree's ``src``, or a kernel hook file run with a hook JSON on stdin) and reads what the ticket's Interface names:
the inbox files, ``~/.gov-os/runtime/log.jsonl``, ``~/.gov-os/runtime/relaunch/``, exit codes and what was printed.
Nothing of the implementation is imported.

``Home`` is slice 1's fixture machine (``w2_121c_support.Box``, imported unchanged) with slice 2's planted load and
slice 3's plantings: messages and log events written straight to their files, the relaunch key, ``gov`` with a stdin,
and a ``gov`` stand-in on ``PATH`` that runs this worktree's ``gov`` (for a hook that calls the command).

``Rig`` is a relaunch fixture: slice 1's ``LaunchKit`` (W2-184's and W2-60a's launch sandbox with the recording stand-in
CLI at ``~/.local/bin/claude``) and a ``Home`` on the same HOME, whose passes carry the open resource gate's readings,
so a ``gov launch`` the pass starts runs to the stand-in.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

SUITE = Path(__file__).resolve().parent
ACCEPTANCE = SUITE.parent
REPO_ROOT = SUITE.parents[2]
HOOKS = REPO_ROOT / "template" / "governance" / "kernel" / "hooks"
for _name in ("W2-121c", "W2-199"):
    sys.path.insert(0, str(ACCEPTANCE / _name))

import w2_199_support as slice2  # noqa: E402

base = slice2.base  # w2_121c_support
poll, said, envelope, write, mentions = base.poll, base.said, base.envelope, base.write, base.mentions
message_words, end_id, boot_id, start_ticks, epoch = (base.message_words, base.end_id, base.boot_id,
                                                      base.start_ticks, base.epoch)
iso = slice2.iso
RESUME_PART = "Resume at the recorded next step"
INBOX_LINE = "Read your inbox: gov msg read"


def clock(seconds: float) -> dict:
    """The planted clock of a pass or a report."""
    return {"GOV_RUNTIME_NOW": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(seconds))}


class Home(base.Box):
    """Slice 1's fixture machine with the load planted (3.0) and slice 3's plantings."""

    def __init__(self, folder, home=None, extra=None):
        self.extra, self.planted = dict(extra or {}), set()
        super().__init__(folder, home=home)
        self.loadavg = write(self.base / "readings" / "loadavg", "3.0 3.0 3.0 1/100 1\n")
        if home is None:
            self.profile(slice2.PROFILE_20)
            self.plant_gate(1 * base.GIB, 1 * base.GIB)
        write(self.bin / "gov", f'#!/bin/sh\nexec "{sys.executable}" -m gov.cli.main "$@"\n').chmod(0o755)

    def env(self, extra=None) -> dict:
        env = super().env()
        env.update(GOV_RESOURCES_LOADAVG=str(self.loadavg), GOV_ADMISSION_POLL_S="0.2", GOV_ADMISSION_SAMPLE_S="0.2")
        env.update(self.extra)
        env.update(extra or {})
        return {key: value for key, value in env.items() if value is not None}

    def gov_in(self, *args, stdin="", cwd=None, extra_env=None) -> subprocess.CompletedProcess:
        """``gov <args>`` with ``stdin`` as its standard input."""
        return subprocess.run(self.argv(*args), cwd=str(cwd or self.work), env=self.env(extra_env), input=stdin,
                              capture_output=True, text=True, timeout=base.COMMAND_TIMEOUT_S)

    # -- the Stop check -------------------------------------------------------------------------------------------------

    def stop_check(self, address, cwd=None) -> dict | None:
        """``gov msg stop-check`` with a Stop hook's input: the block decision it printed, or None when it passed."""
        payload = {"session_id": "0f1e2d3c-stop", "transcript_path": str(self.base / "transcript.jsonl"),
                   "cwd": str(cwd or self.work), "hook_event_name": "Stop", "stop_hook_active": False}
        done = self.gov_in("msg", "stop-check", stdin=json.dumps(payload), cwd=cwd,
                           extra_env={"GOV_MSG_ADDRESS": address})
        assert done.returncode == 0, f"gov msg stop-check: exit {done.returncode}, not 0\n{said(done)}"
        return decision(done.stdout)

    def seen(self, address) -> str:
        path = self.inbox_root / address / "stop-seen"
        return path.read_text(encoding="utf-8") if path.is_file() else ""

    # -- planted files --------------------------------------------------------------------------------------------------

    def plant_message(self, address, message_id, at, kind="wake", text="planted", sender="runtime", to=None) -> dict:
        """One message line appended to the address's inbox file, as ``gov msg send`` writes it."""
        message = {"id": message_id, "at": at, "from": sender, "to": to or address, "kind": kind, "text": text}
        path = self.inbox_file(address)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as out:
            out.write(json.dumps(message) + "\n")
        return message

    def plant_end(self, message_id, kind, to, ended_at: float, **more) -> dict:
        """One ``end`` event appended to the runtime log, in the Interface's form."""
        event = {"at": iso(ended_at), "event": "end", "id": message_id, "kind": kind, "to": to,
                 "ended_at": iso(ended_at), **more}
        self.runtime.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as out:
            out.write(json.dumps(event) + "\n")
        return event

    def events(self, name) -> list[dict]:
        return [item for item in self.log() if item.get("event") == name]

    def config(self, text) -> Path:
        """``~/.gov-os/runtime/config.json`` holding ``text`` (a dict is written as JSON)."""
        return write(self.runtime / "config.json", text if isinstance(text, str) else json.dumps(text))

    def claims(self) -> list[str]:
        place = self.runtime / "relaunch"
        return sorted(path.name for path in place.iterdir()) if place.is_dir() else []

    def died(self, ticket, repository, notify, session_id=None, role="engineer", **more) -> dict:
        """A registry entry, as the launcher writes it, of a session whose process is gone."""
        pid, ticks = self.dead_pid()
        entry = {"pid": pid, "repository": str(repository), "ticket": ticket, "role": role,
                 "started": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()), "notify": notify,
                 "address": f"{role}:{ticket}", "boot": boot_id(), "start_ticks": ticks, **more}
        if session_id is not None:
            entry["session_id"] = session_id
        self.put_entry(entry)
        return entry

    def put_entry(self, entry):
        self.planted.add(entry["pid"])
        self.sessions.mkdir(parents=True, exist_ok=True)
        temp = self.sessions / f".entry-{entry['pid']}.tmp"
        temp.write_text(json.dumps(entry), encoding="utf-8")
        os.replace(temp, self.sessions / f"{entry['pid']}.json")

    def drop_entry(self, entry):
        (self.sessions / f"{entry['pid']}.json").unlink(missing_ok=True)

    def named(self, address, words) -> list[dict]:
        """The wake messages of the inbox whose text or data holds ``words`` (case-insensitive)."""
        return [m for m in self.wakes(address) if words.lower() in message_words(m).lower()]


def decision(stdout: str) -> dict | None:
    """The Claude Code hook decision printed (``{"decision": "block", "reason": <text>}``), or None for nothing."""
    if not stdout.strip():
        return None
    try:
        data = json.loads(stdout)
    except ValueError:
        raise AssertionError(f"what was printed is not one JSON hook decision: {stdout[:500]!r}") from None
    assert isinstance(data, dict) and data.get("decision") == "block" and isinstance(data.get("reason"), str), (
        f"what was printed is not a block decision with a reason: {data}")
    return data


# --------------------------------------------------------------------------
# A fixture project, its checkpoints and the hooks
# --------------------------------------------------------------------------

def project(folder, *tickets) -> Path:
    """A git repository holding one in_progress ticket file per id, committed."""
    folder = Path(folder)
    for ticket in tickets:
        write(folder / ".tickets" / f"{ticket}.md", f"---\nid: {ticket}\nstatus: in_progress\ntype: task\n"
              f"title: a fixture ticket\nassignee: engineer\n---\n\n# {ticket}\n")
    git = ["git", "-C", str(folder), "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
    quiet = {"capture_output": True, "check": True, "env": {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull}}
    subprocess.run(git + ["init", "-q", "-b", "main"], **quiet)
    subprocess.run(git + ["add", "-A"], **quiet)
    subprocess.run(git + ["commit", "-q", "-m", "a fixture project"], **quiet)
    return folder


_CHECKPOINT = ("import sys\nfrom pathlib import Path\nfrom gov.checkpoint.record import write\n"
               "print(write(Path(sys.argv[1]), sys.argv[2], 'stop', sys.argv[3], [], dest='automatic')['path'])\n")


def checkpoint(home, root, ticket, next_action) -> str:
    """An automatic checkpoint record of the ticket holding ``next_action`` (``gov.checkpoint.record.write``, the
    record ``gov checkpoint`` and the hooks write); its path in the project."""
    done = subprocess.run([sys.executable, "-c", _CHECKPOINT, str(root), ticket, next_action], cwd=str(root),
                          env=home.env(), capture_output=True, text=True, timeout=base.COMMAND_TIMEOUT_S)
    assert done.returncode == 0, f"harness: the checkpoint record was not written\n{said(done)}"
    return done.stdout.strip()


def brief(home, root, ticket) -> dict:
    """``gov checkpoint --resume --ticket <ticket>``: the latest checkpoint's resume brief."""
    return home.ok("checkpoint", "--resume", "--ticket", ticket, cwd=root)


def checkpoint_files(root, ticket) -> dict:
    found = {}
    for rel in ("docs/checkpoints", ".gov-runtime/scratch/checkpoints"):
        for path in sorted((Path(root) / rel / ticket).glob("*")):
            found[f"{rel}/{ticket}/{path.name}"] = path.read_bytes()
    return found


def run_hook(home, name, payload, root, ticket=None, role="engineer", address=None) -> subprocess.CompletedProcess:
    """A kernel hook file run as Claude Code runs it: the hook JSON on stdin, the project as ``CLAUDE_PROJECT_DIR``."""
    env = home.env({"CLAUDE_PROJECT_DIR": str(root), "GOV_TICKET": ticket, "GOV_ROLE": role,
                    "GOV_MSG_ADDRESS": address})
    done = subprocess.run([sys.executable, str(HOOKS / name)], cwd=str(root), env=env, input=json.dumps(payload),
                          capture_output=True, text=True, timeout=base.COMMAND_TIMEOUT_S)
    assert done.returncode == 0, f"{name} exited {done.returncode}, not 0\n{said(done)}"
    return done


def injected(done) -> str:
    """The SessionStart hook's ``additionalContext`` ('' when it printed nothing)."""
    if not done.stdout.strip():
        return ""
    data = json.loads(done.stdout)
    return data["hookSpecificOutput"]["additionalContext"]


# --------------------------------------------------------------------------
# The relaunch fixture
# --------------------------------------------------------------------------

class Rig:
    def __init__(self, tmp_path, lead):
        self.kit = base.LaunchKit(tmp_path, rubric=True)
        self.s, self.b, self.lead = self.kit.s, self.kit.b, lead
        self.project = self.kit.project
        self.home = Home(Path(tmp_path) / "machine", home=self.kit.home,
                         extra=self.b.plant_open_gate(self.kit.sandbox))
        self.template = None

    def session(self, ticket) -> str:
        """An in_progress engineer ticket and a session of it that ``gov launch`` can resume: its session id. The
        first is a real launch (the stand-in ends at once with exit code 0); a later one is that launch's record
        planted under a new session id for its ticket."""
        self.s.ticket(self.project, self.s.ENGINEER, "C2", tk=ticket)
        if self.template is not None:
            return self.s.plant_launch_record(self.kit.sandbox, self.template, ticket=ticket)
        self.kit.ticket = ticket
        result = self.kit.launch({"GOV_MSG_ADDRESS": self.lead})
        assert result.run.returncode == 0 and len(self.launches()) == 1, (
            f"harness: the first launch did not run the stand-in once\n{result.describe()}")
        session_id = self.launches()[0]["args"][self.launches()[0]["args"].index("--session-id") + 1]
        self.template = json.loads((Path(self.kit.sandbox.records) / f"{session_id}.json").read_text("utf-8"))
        return session_id

    def checkpoint(self, ticket, next_action) -> str:
        return checkpoint(self.home, self.project, ticket, next_action)

    def died(self, ticket, session_id=None, **more) -> dict:
        return self.home.died(ticket, self.project, self.lead, session_id, **more)

    def launches(self) -> list[dict]:
        """The stand-in CLI's session starts (its ``--version`` calls left out)."""
        return [call for call in self.b.calls(self.kit.cli) if "--version" not in call["args"]]

    def resumed(self, wait_for=0, seconds=15.0, settle=0.0) -> list[dict]:
        """The stand-in's starts that carry ``--resume``: once there are ``wait_for`` of them (at most ``seconds``),
        and after ``settle`` more seconds in which a launch that should not happen would land."""
        def found():
            return [call for call in self.launches() if "--resume" in call["args"]]
        if wait_for:
            poll(lambda: len(found()) >= wait_for, seconds)
            self.quiet()
        time.sleep(settle)
        return found()

    def quiet(self, seconds=10.0):
        """Wait until the registry holds no entry but the planted ones (a detached ``gov launch`` has ended and taken
        its session's entry out)."""
        def launched():
            return [p for p in self.home.sessions.glob("*.json") if p.stem.isdigit() and int(p.stem) not in
                    self.home.planted]
        poll(lambda: not launched(), seconds)
        time.sleep(0.3)

    def cleanup(self):
        self.quiet(5.0)
        self.home.cleanup()
