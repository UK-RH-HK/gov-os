"""The watch pass: one machine-wide pass, one state file, every end and stall messaged once (the run-time tool,
slice 1: RT-2, RT-3, RT-7; F1, F2; audit 3 D1, D4).

``gov dispatch watch`` runs one pass; no project and no ``dispatch.yaml`` is read. The pass holds an exclusive,
non-blocking ``flock`` on the folder ``~/.gov-os/runtime/`` itself (held: exit 4, nothing written), so the folder holds
``state.json`` and ``log.jsonl`` only. Each pass:

1. detects the machine and derives the limits (``gov.dispatch.limits``);
2. takes the ``runtime`` inbox's new watch requests (the mark moves only once the state holding them is written);
3. reads every ``~/.gov-os/machine/sessions/*.json`` directly (never ``registry.sessions()``, which removes entries):
   a session whose process is gone, or whose pid is another process's now, becomes one wake message to its entry's
   ``notify`` (else ``cto``), and so does a session tracked by an earlier pass whose entry went with its process;
4. checks each watch: a pid gone or an exit file written is one wake message to the watch's ``to``; a transcript
   silent past its limit is one wake message (and, with ``push``, one detached run of that command) per incident;
5. writes ``state.json`` whole (a temporary file and a rename) and appends its events to ``log.jsonl``.

Message ids make every send idempotent (F1): a session's end ``end:<boot>:<pid>:<start_ticks>`` (``end:<pid>:<started>``
without the identity, as the launcher's), a watch's end ``watch:<request id>``, a stall
``stall:<request id>:<the transcript's mtime, whole seconds>``. A push runs only for a stall message actually appended.
What cannot be read is named in ``problems`` and the log, and the rest of the pass still runs (F2).
"""

from __future__ import annotations

import datetime
import fcntl
import json
import os
import shlex
import subprocess
import tempfile
import time
from pathlib import Path

from gov.dispatch import inbox, limits
from gov.resources import machine
from gov.resources.config import machine_dir

FORMAT = 1
STATE, LOG = "state.json", "log.jsonl"
TEMP_PREFIX = ".state-"
EXIT_OK, EXIT_LOCKED = 0, 4
FALLBACK = "cto"
STALL_AFTER_S, NIGHT_STALL_AFTER_S, NIGHT = 3600, 7200, "02:00-07:30"
FORMS = ("pid", "exit-file", "transcript")
SENDER = "runtime"


def folder() -> Path:
    return Path(os.environ.get("HOME") or Path.home()) / ".gov-os" / "runtime"


def iso(epoch: float) -> str:
    return datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def end_id(entry: dict) -> str:
    """The end message's id of a registry entry: the launcher and the pass give the same one."""
    boot, ticks = entry.get("boot"), entry.get("start_ticks")
    if boot and isinstance(ticks, int) and not isinstance(ticks, bool):
        return f"end:{boot}:{entry['pid']}:{ticks}"
    return f"end:{entry['pid']}:{entry.get('started')}"


def clock() -> tuple[float, str | None]:
    """Now, from ``GOV_RUNTIME_NOW`` (ISO-8601; with no offset, local time) when set."""
    given = os.environ.get("GOV_RUNTIME_NOW")
    if not given:
        return time.time(), None
    try:
        return datetime.datetime.fromisoformat(given.strip().replace("Z", "+00:00")).timestamp(), None
    except ValueError:
        return time.time(), f"GOV_RUNTIME_NOW={given!r} is not an ISO-8601 time: the clock is read instead"


def in_night(epoch: float, night: str) -> bool:
    start, _, end = night.partition("-")
    minutes = [int(part[:2]) * 60 + int(part[3:5]) for part in (start, end)]
    local = datetime.datetime.fromtimestamp(epoch)
    now = local.hour * 60 + local.minute
    if minutes[0] <= minutes[1]:
        return minutes[0] <= now < minutes[1]
    return now >= minutes[0] or now < minutes[1]


def last_change(path: str) -> float:
    """The file's mtime, or the newest file's in the folder; ``OSError`` when there is none."""
    target = Path(path)
    if target.is_dir():
        times = [p.stat().st_mtime for p in target.iterdir() if p.is_file()]
        if not times:
            raise FileNotFoundError(f"the folder {path} holds no file")
        return max(times)
    return target.stat().st_mtime


def push(command: str, text: str) -> None:
    """The stall's push: the command run once, detached (its own session, no pipe), the text its last argument."""
    subprocess.Popen([*shlex.split(command), text], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True)


class Pass:
    def __init__(self, place: Path):
        self.place, self.events, self.problems = place, [], []
        self.now, why = clock()
        if why:
            self.problem(why)

    def event(self, name: str, **fields) -> None:
        self.events.append({"at": iso(time.time()), "event": name, **fields})

    def problem(self, what: str) -> None:
        self.problems.append(what)
        self.event("problem", what=what)

    def send(self, to: str, text: str, message_id: str, data: dict) -> bool | None:
        """True when appended, False for a duplicate, None when the send failed (a problem)."""
        try:
            sent = inbox.send(to, "wake", text, sender=SENDER, message_id=message_id, data=data)
        except (OSError, inbox.InboxError) as error:
            self.problem(f"the message {message_id} to {to} cannot be sent: {getattr(error, 'message', error)}")
            return None
        if sent["sent"]:
            self.event("sent", id=message_id, to=to, kind="wake")
        return sent["sent"]

    # --- the pass -------------------------------------------------------------------------------------------------

    def previous(self) -> dict:
        try:
            data = json.loads((self.place / STATE).read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("not a JSON object")
            return data
        except FileNotFoundError:
            return {}
        except (OSError, ValueError, UnicodeDecodeError) as error:
            self.problem(f"{STATE}: the previous state cannot be read ({error}): this pass starts afresh")
            return {}

    def requests(self, watches: dict) -> int | None:
        try:
            found, _mark, end = inbox.pending(inbox.RUNTIME)
        except (OSError, inbox.InboxError) as error:
            self.problem(f"the runtime inbox cannot be read: {error}")
            return None
        for message in found:
            data, wid = message.get("data"), message.get("id")
            if message.get("kind") != "watch" or not isinstance(wid, str) or wid in watches:
                continue
            why = self.bad_watch(data)
            if why:
                self.problem(f"the watch request {wid} is refused: {why}")
                continue
            watches[wid] = {**data, "requested_at": message.get("at")}
        return end

    @staticmethod
    def bad_watch(data) -> str | None:
        if not isinstance(data, dict) or data.get("form") not in FORMS:
            return "no form among " + ", ".join(FORMS)
        try:
            inbox.check(data.get("to"))
        except inbox.InboxError as error:
            return error.message
        if data["form"] == "pid" and not (isinstance(data.get("pid"), int) and data["pid"] > 0):
            return "no pid"
        if data["form"] != "pid" and not (isinstance(data.get("path"), str) and os.path.isabs(data["path"])):
            return "no absolute path"
        return None

    def end_session(self, entry: dict, sid: str) -> None:
        notify = entry.get("notify")
        try:
            to = inbox.check(notify) if notify else FALLBACK
        except inbox.InboxError:
            to = FALLBACK
        role, ticket, pid = entry.get("role"), entry.get("ticket"), entry.get("pid")
        text = f"session {role} {ticket} ended (pid {pid}); the watch pass does not know its exit code"
        if self.send(to, text, sid, {"role": role, "ticket": ticket, "pid": pid, "exit_code": None,
                                     "repository": entry.get("repository")}):
            self.event("ended", id=sid, role=role, ticket=ticket, pid=pid)

    def sessions(self, tracked: dict) -> dict:
        live, ended = {}, set()
        place = machine_dir() / "sessions"
        try:
            paths = sorted(place.glob("*.json")) if place.exists() else []
        except OSError as error:
            self.problem(f"the registry {place} cannot be listed: {error}")
            paths = []
        for path in paths:
            try:
                entry = json.loads(path.read_text(encoding="utf-8"))
                pid = entry.get("pid") if isinstance(entry, dict) else None
                if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
                    raise ValueError("no positive integer pid")
            except FileNotFoundError:
                continue
            except (OSError, ValueError, UnicodeDecodeError) as error:
                self.problem(f"the registry entry {path} cannot be read: {error}")
                continue
            sid = end_id(entry)
            if machine.alive(pid) and machine.same_process(pid, entry):
                live[sid] = {key: entry.get(key) for key in ("pid", "role", "ticket", "repository", "started", "boot",
                                                             "start_ticks", "notify", "address")}
            else:
                ended.add(sid)
                self.end_session(entry, sid)
        for sid, entry in tracked.items():  # an entry removed by another reader: its process judged here
            if sid in live or sid in ended or not isinstance(entry, dict) or not isinstance(entry.get("pid"), int):
                continue
            if machine.alive(entry["pid"]) and machine.same_process(entry["pid"], entry):
                live[sid] = entry
            else:
                self.end_session(entry, sid)
        return live

    def check_watch(self, wid: str, data: dict, incidents: dict) -> bool:
        """True when the watch is done (its end messaged)."""
        to, name = data["to"], data.get("name") or wid
        if data["form"] == "pid":
            pid = data["pid"]
            if machine.alive(pid) and (not isinstance(data.get("start_ticks"), int) or machine.same_process(pid, data)):
                return False
            return self.send(to, f"watch {name}: process {pid} ended", f"watch:{wid}",
                             {"watch": wid, "name": name, "pid": pid}) is not None
        if data["form"] == "exit-file":
            path = Path(data["path"])
            try:
                if not path.is_file() or path.stat().st_size == 0:
                    return False
                first = path.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0].strip()
            except OSError as error:
                self.problem(f"watch {name}: the exit file {path} cannot be read: {error}")
                return False
            code = int(first) if first.isascii() and first.isdigit() else None
            said = f"exit code {code}" if code is not None else f"no exit code ({first[:40]!r})"
            return self.send(to, f"watch {name}: the exit file {path} holds {said}", f"watch:{wid}",
                             {"watch": wid, "name": name, "exit_file": str(path), "exit_code": code}) is not None
        self.check_stall(wid, data, incidents)
        return False

    def check_stall(self, wid: str, data: dict, incidents: dict) -> None:
        to, name, path = data["to"], data.get("name") or wid, data["path"]
        try:
            changed = last_change(path)
        except OSError as error:
            self.problem(f"watch {name}: the transcript {path} cannot be read: {error}")
            return
        night = data.get("night") or NIGHT
        try:
            at_night = in_night(self.now, night)
        except (ValueError, IndexError):
            self.problem(f"watch {name}: --night {night!r} is not HH:MM-HH:MM: the default {NIGHT} is used")
            at_night = in_night(self.now, NIGHT)
        limit = (data.get("night_stall_after") or NIGHT_STALL_AFTER_S) if at_night else \
            (data.get("stall_after") or STALL_AFTER_S)
        age = self.now - changed
        if age < limit:
            incidents.pop(wid, None)  # a later change ends the incident
            return
        key = f"stall:{wid}:{int(changed)}"
        if (incidents.get(wid) or {}).get("key") == key:
            return  # once per incident: never a reminder
        minutes = int(age // 60)
        text = f"stall: {name} silent {minutes} min (no change to {path} since {iso(changed)}; limit {limit // 60} min)"
        sent = self.send(to, text, key, {"watch": wid, "name": name, "silent_min": minutes, "transcript": path})
        if sent is None:
            return
        pushed = False
        if sent and data.get("push"):
            try:
                push(data["push"], text)
                pushed = True
            except (OSError, ValueError) as error:
                self.problem(f"watch {name}: the push command cannot be started: {error}")
        incidents[wid] = {"key": key, "since": iso(changed), "silent_min": minutes, "pushed": pushed}
        self.event("stall", id=key, watch=wid, name=name, silent_min=minutes, pushed=pushed)

    def run(self) -> dict:
        for stray in self.place.glob(TEMP_PREFIX + "*"):  # a pass killed while writing left its temporary file
            try:
                stray.unlink()
            except OSError:
                pass
        previous = self.previous()
        detected = limits.detect()
        for problem in detected["problems"]:
            self.problem(problem)
        watches = {k: v for k, v in (previous.get("watches") or {}).items() if isinstance(v, dict)}
        incidents = dict(previous.get("incidents") or {})
        end = self.requests(watches)
        sessions = self.sessions(previous.get("sessions") or {})
        for wid, data in list(watches.items()):
            try:
                if self.check_watch(wid, data, incidents):
                    del watches[wid]
                    incidents.pop(wid, None)
            except Exception as error:  # one watch never stops the pass (F2)
                self.problem(f"watch {wid}: {type(error).__name__}: {error}")
        state = {"format": FORMAT, "pass": {"at": iso(self.now), "ok": not self.problems},
                 "machine": detected["machine"], "limits": detected["limits"], "sessions": sessions,
                 "watches": watches, "incidents": {k: v for k, v in incidents.items() if k in watches},
                 "problems": list(self.problems)}
        with tempfile.NamedTemporaryFile("w", dir=self.place, prefix=TEMP_PREFIX, delete=False) as handle:
            json.dump(state, handle, indent=1)
        os.replace(handle.name, self.place / STATE)
        if end is not None:  # the requests are in the state: the mark may move past them
            try:
                inbox.advance(inbox.RUNTIME, end)
            except OSError as error:
                self.problem(f"the runtime inbox's mark cannot be moved: {error}")
        self.event("pass", ok=not self.problems, sent=sum(e["event"] == "sent" for e in self.events),
                   problems=len(self.problems))
        with open(self.place / LOG, "a", encoding="utf-8") as log:
            log.write("".join(json.dumps(e) + "\n" for e in self.events))
        return state


def watch_pass() -> tuple[int, dict | None]:
    """One pass: ``(0, state)``, or ``(4, None)`` when another pass holds the folder's lock (nothing written)."""
    place = folder()
    place.mkdir(parents=True, exist_ok=True)
    fd = os.open(place, os.O_RDONLY | os.O_DIRECTORY)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return EXIT_LOCKED, None
        return EXIT_OK, Pass(place).run()
    finally:
        os.close(fd)
