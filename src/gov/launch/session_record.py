"""The session record: one JSON file per launched session (W2-60b; DEC-838 item 3, CAP-36.a lite, DEC-655, DEC-495).

``.gov-runtime/sessions/<session id>.json`` in the repository's main checkout (found as
``gov.launch.record.main_checkout`` finds the launch records), beside W2-60a's
``.gov-runtime/launches/``. It is written whole (a temporary file in the same folder,
then a rename) once the session's process has started, and replaced whole after the
session ends, whatever its ending. Its housekeeping keys hold plain values; each
measured key holds ``{"value": <v>, "source": "<named source>"}`` or
``{"value": null, "not_measured": "<reason>"}``, never 0 for not measured and never a
guess. ``role``, ``ticket``, ``task_class``, ``criticality`` and ``promotion`` come
from the session's launch record; every other value from the harness's own record of
the session: its session log, read through W1-31's reader
(``gov.telemetry.sessionlog``), and the ``--output-format json`` result line when one
is given. Counts only: no text of the log reaches a record, the Claude Code version
excepted. Pass or fail and the repair count are the close's (W2-07), not the record's.

One writer per worktree (S10, S12; DEC-847, DEC-963, DEC-1156 (3)): a record whose
``worktree`` is a launch's tree, whose ``ended_at`` is null and whose ``pid`` is alive
(and not a later process that took a dead launcher's pid) is a live writing session
unless its role is in ``REVIEWERS``. A record that cannot be read refuses the launch:
it could hide a live writer.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path

from gov.cli.errors import GovError
from gov.launch import record as launches
from gov.telemetry import sessionlog

RECORD, FORMAT = "gov-session", 1
RUNTIME, SESSIONS = ".gov-runtime", "sessions"
# DEC-959 item 3, DEC-953 item 2: the read-only sessions, which write only their reports: never counted as a writer,
# never refused as one.
REVIEWERS = frozenset({"independent-auditor", "qa-engineer"})
FROM_LAUNCH = {"role": "role", "ticket": "ticket", "task_class": "ticket_class", "criticality": "criticality",
               "promotion": "promotion"}
TOKENS = ("tokens_input", "tokens_output", "tokens_cache_creation", "tokens_cache_read")  # sessionlog.USAGE's order
TIERS = ("opus", "sonnet", "haiku")
STAMP = "%Y-%m-%dT%H:%M:%SZ"
CONFIG_ENV = "CLAUDE_CONFIG_DIR"
NO_WINDOW = ("the session log states no window in a form the specimens show, and no --output-format json result "
             "line (modelUsage.<model>.contextWindow) was read")
REUSED_SLACK_S = 2  # a process that started this long after the record's start is not the launcher that wrote it

LOG = "session log"
SOURCES = {
    "tokens": f"{LOG} (W1-31's sessionlog.read): the assistant lines' usage, each message once with its last line's "
              "figures, of the session's own file and its sub-agents' files",
    "model": f"{LOG}: the models of the session's own assistant lines",
    "effort": f"{LOG}: perTurnEffort of the session's own assistant lines",
    "turns": f"{LOG}: the session's own assistant messages (message ids), each once",
    "compactions": f"{LOG}: compact_boundary lines of the session's own file",
    "rate_limit_events": f"{LOG}: api_error lines with error.status 429 and assistant lines with isApiErrorMessage "
                         "and error rate_limit, of the session's and its sub-agents' files, each line once",
    "cost_usd": f"{LOG}: totalCostUSD of the last cost-state line of the session's own file",
    "minutes": f"{LOG}: from the first to the last line timestamp of the session's own file",
    "subagents": f"{LOG}: the sub-agents' files (<session id>/subagents/agent-*.jsonl), each one's first model",
    "claude_code_version": f"{LOG}: the version the lines carry",
}
RESULT = "result line (--output-format json)"


def _refuse(reason: str) -> GovError:
    return GovError("LAUNCH_REFUSED", reason)


def _now() -> str:
    return time.strftime(STAMP, time.gmtime())


def measured(value, source: str) -> dict:
    return {"value": value, "source": source}


def not_measured(reason: str) -> dict:
    return {"value": None, "not_measured": reason}


def folder(root: Path) -> Path:
    """The session records' folder of the repository ``root`` belongs to (not made here). ``root`` is a real path."""
    return launches.main_checkout(root, "the session record's folder") / RUNTIME / SESSIONS


def config_folder(environ=None, home: Path | None = None) -> Path:
    """The Claude config folder whose ``projects/`` holds the session's log: ``CLAUDE_CONFIG_DIR`` when the launcher's
    environment sets it, else ``<home>/.claude``."""
    environ = os.environ if environ is None else environ
    value = environ.get(CONFIG_ENV)
    return Path(value) if value else (Path.home() if home is None else home) / ".claude"


# -- the record --------------------------------------------------------------------------------------------------

def _from_launch(path: Path) -> dict:
    """The five keys the launch record gives, each with the record as its source; all not measured when it cannot be
    read as a launch record."""
    source = f"launch record {RUNTIME}/{launches.LAUNCHES}/{path.name}"
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = None
    if not isinstance(data, dict) or data.get("record") != "gov-launch":
        return {key: not_measured(f"the {source} cannot be read as a launch record") for key in FROM_LAUNCH}
    keys = {key: measured(data.get(name), source) for key, name in FROM_LAUNCH.items()}
    promotion = data.get("promotion")  # W2-184: {"reason", "record"} or null; the record keeps the reason
    keys["promotion"] = measured(promotion.get("reason") if isinstance(promotion, dict) else None, source)
    return keys


def begin(launch_path: Path, *, worktree: str, pid: int) -> dict:
    """The record at the session's start: the housekeeping keys, the launch record's keys, no end."""
    return {"record": RECORD, "format": FORMAT, "session_id": Path(launch_path).stem, "worktree": str(worktree),
            "pid": pid, "started_at": _now(), "ended_at": None, "exit_code": None, **_from_launch(launch_path)}


def _one_or_list(values: list, source: str, none: str) -> dict:
    if not values:
        return not_measured(none)
    return measured(values[0] if len(values) == 1 else list(values), source)


def _tier(model: dict) -> dict:
    """RUBRIC-2's tier from the model's name: opus, sonnet, haiku or other; not measured with the model."""
    if model["value"] is None:
        return not_measured(f"the model is not measured: {model['not_measured']}")
    names = model["value"] if isinstance(model["value"], list) else [model["value"]]
    tiers = {next((tier for tier in TIERS if tier in name.lower()), "other") for name in names}
    if len(tiers) != 1:
        return not_measured("the session ran on models of more than one tier")
    return measured(tiers.pop(), f"derived from the model's name ({model['source']})")


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def _count(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def measures(config: Path, session_id: str, result: dict | None = None) -> dict:
    """The measured keys the harness's own record gives: the session log through W1-31's reader, and ``result`` (the
    ``--output-format json`` result line) when given. A value neither gives is not measured, with the reason."""
    read = found = None
    why_read = why_found = None
    try:
        path = sessionlog.find(config, session_id)
    except GovError as error:
        why_read = why_found = error.message
    else:
        try:
            read = sessionlog.read(path, session_id)
        except GovError as error:
            why_read = error.message
        try:
            found = sessionlog.measure(path, session_id)
        except GovError as error:
            why_found = error.message
    result = result if isinstance(result, dict) and result.get("type") == "result" else None
    keys: dict = {}

    if read is not None:
        for key, value in zip(TOKENS, read["usage"]):
            keys[key] = measured(value, SOURCES["tokens"])
    else:
        for key in TOKENS:
            keys[key] = not_measured(why_read)

    def from_log(key, value, none):
        if found is None:
            return not_measured(why_found)
        return not_measured(none) if value is None else measured(value, SOURCES[key])

    if found is None:
        for key in ("model", "effort", "turns", "compactions", "rate_limit_events", "cost_usd", "minutes",
                    "subagents", "claude_code_version"):
            keys[key] = not_measured(why_found)
    else:
        keys["model"] = not_measured("a model name of the log is not of a model name's plain form") \
            if found["models"] is None else _one_or_list(found["models"], SOURCES["model"],
                                                        "the session log holds no assistant line of a model")
        keys["effort"] = _one_or_list(found["efforts"], SOURCES["effort"],
                                      "no assistant line of the session log states an effort (perTurnEffort)")
        keys["turns"] = measured(found["turns"], SOURCES["turns"])
        keys["compactions"] = measured(found["compactions"], SOURCES["compactions"])
        keys["rate_limit_events"] = from_log(
            "rate_limit_events", None if found["rate_limits"] is None else [{"at": at} for at in found["rate_limits"]],
            "a rate-limit line of the session log has no timestamp of the plain form")
        keys["cost_usd"] = from_log("cost_usd", found["cost"], "the session log holds no cost-state line with a "
                                    "totalCostUSD of 0 or more")
        keys["minutes"] = from_log("minutes", found["minutes"], "the session log's own file holds no line timestamp "
                                   "of the plain form, or one that is not")
        keys["subagents"] = measured({"count": len(found["subagents"]), "models": found["subagents"]},
                                     SOURCES["subagents"])
        keys["claude_code_version"] = _one_or_list(found["versions"], SOURCES["claude_code_version"],
                                                   "no line of the session log names a Claude Code version")

    keys["window"] = not_measured(NO_WINDOW)
    if result is not None:
        if _count(result.get("num_turns")):
            keys["turns"] = measured(result["num_turns"], f"{RESULT}: num_turns")
        if _number(result.get("total_cost_usd")):
            keys["cost_usd"] = measured(result["total_cost_usd"], f"{RESULT}: total_cost_usd")
        if _number(result.get("duration_ms")):
            keys["minutes"] = measured(round(result["duration_ms"] / 60000, 2), f"{RESULT}: duration_ms")
        usage = result.get("modelUsage")
        model = keys["model"]["value"]
        entry = usage.get(model) if isinstance(usage, dict) and isinstance(model, str) else None
        if isinstance(entry, dict) and _count(entry.get("contextWindow")) and entry["contextWindow"] > 0:
            keys["window"] = measured(entry["contextWindow"], f"{RESULT}: modelUsage.<model>.contextWindow")
    keys["tier"] = _tier(keys["model"])
    return keys


def finish(record: dict, exit_code, config: Path, result: dict | None = None) -> dict:
    """The record after the session has ended: the start record's keys, its end and exit code, and every measured
    key."""
    ended = {**record, "ended_at": _now(), "exit_code": exit_code}
    ended.update(measures(config, record["session_id"], result))
    return ended


def path_of(root: Path, session_id: str) -> Path:
    return folder(root) / f"{session_id}.json"


def write(root: Path, data: dict) -> Path:
    """Write the record whole: the bytes, flushed and fsynced, to a hidden ``.<session id>.<unique part>.tmp`` in the
    folder (a name no reader of ``*.json`` takes), then renamed over ``<session id>.json``. Raises ``OSError`` or
    ``GovError`` when it cannot; what it made is removed, so no part of a record is left."""
    base = folder(root)
    for here in (base.parent, base):
        if os.path.lexists(here) and (here.is_symlink() or not here.is_dir()):
            raise NotADirectoryError(f"{here} is a link or not a folder")
    os.makedirs(base, exist_ok=True)
    path = base / f"{data['session_id']}.json"
    body = (json.dumps(data, indent=2) + "\n").encode()
    temporary = base / f".{data['session_id']}.{secrets.token_hex(8)}.tmp"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    try:
        try:
            view = memoryview(body)
            while view:
                view = view[os.write(descriptor, view):]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    return path


def read_record(root: Path, ticket: str, session_id: str) -> dict:
    """The record of ``session_id``, which must be ``ticket``'s (W2-07's close joins it by both); refused when it is
    missing, cannot be read, is not a session record or is another ticket's."""
    if not sessionlog.SESSION_ID.fullmatch(session_id or ""):
        raise GovError("SESSION_RECORD_MISSING", f"'{session_id}' is not a session id")
    path = path_of(Path(os.path.realpath(root)), session_id)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise GovError("SESSION_RECORD_MISSING", f"no session record of {session_id} at {path}") from None
    except (OSError, ValueError):
        raise GovError("SESSION_RECORD_UNREADABLE", f"the session record {path} cannot be read") from None
    if not isinstance(data, dict) or data.get("record") != RECORD or data.get("session_id") != session_id:
        raise GovError("SESSION_RECORD_UNREADABLE", f"{path} is not the session record of {session_id}")
    held = data.get("ticket")
    if not isinstance(held, dict) or held.get("value") != ticket:
        raise GovError("SESSION_RECORD_MISSING", f"the session record of {session_id} is not of the ticket {ticket}")
    return data


class Keeper:
    """The launcher's two calls (S1, S5): ``begin`` once the session's process has started, ``end`` after it has
    ended, by every path. Neither raises nor changes the session's exit code; a record that cannot be written gives
    one line on stderr naming it, once for the whole session."""

    def __init__(self, root: Path, launch_path: Path, *, worktree: str, pid: int, say, config: Path | None = None,
                 result=None):
        self.root, self.launch_path, self.worktree, self.pid, self.say = root, Path(launch_path), worktree, pid, say
        self.config, self.result, self.started, self.said = config, result, None, False

    def _where(self) -> str:
        try:
            return str(path_of(self.root, self.launch_path.stem))
        except Exception:  # the main checkout cannot be found: the record's place in the tree, by its name
            return f"{RUNTIME}/{SESSIONS}/{self.launch_path.stem}.json"

    def _failed(self, error: BaseException) -> None:
        if not self.said:
            self.said = True
            message = getattr(error, "message", None)
            if not message and isinstance(error, OSError):
                message = error.strerror
            why = " ".join(str(message or error).split()) or type(error).__name__
            self.say(f"gov launch: the session record {self._where()} cannot be written ({why}); the session's exit "
                     f"code is kept (DEC-392)\n")

    def begin(self) -> None:
        try:
            self.started = begin(self.launch_path, worktree=self.worktree, pid=self.pid)
            write(self.root, self.started)
        except Exception as error:  # noqa: BLE001 - S5: nothing of the record's ends the launch
            self._failed(error)

    def end(self, exit_code) -> None:
        try:
            start = self.started or begin(self.launch_path, worktree=self.worktree, pid=self.pid)
            config = self.config if self.config is not None else config_folder()
            write(self.root, finish(start, exit_code, config, self.result))
        except Exception as error:  # noqa: BLE001
            self._failed(error)


# -- one writer per worktree -------------------------------------------------------------------------------------

def _started_epoch(pid: int) -> float | None:
    """When the process ``pid`` started, in seconds since the epoch, from ``/proc``; ``None`` when it cannot be read."""
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as handle:
            ticks = int(handle.read().rsplit(")", 1)[1].split()[19])
        with open("/proc/stat", encoding="utf-8") as handle:
            boot = next(int(line.split()[1]) for line in handle if line.startswith("btime "))
        return boot + ticks / os.sysconf("SC_CLK_TCK")
    except (OSError, ValueError, IndexError, StopIteration):
        return None


def alive(pid: int, started_at: str) -> bool:
    """True while ``pid`` is the process that wrote a record started at ``started_at``: it runs, and it did not start
    after the record's session did (a later process given a dead launcher's pid). What cannot be told counts as
    alive, so that a doubt never lets a second writer in."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    except OSError:
        return True
    began = _started_epoch(pid)
    if began is None:
        return True
    record_start = datetime.strptime(started_at, STAMP).replace(tzinfo=timezone.utc).timestamp()
    return began <= record_start + REUSED_SLACK_S


def _shape(data) -> bool:
    if not isinstance(data, dict) or data.get("record") != RECORD:
        return False
    pid, role = data.get("pid"), data.get("role")
    try:
        datetime.strptime(data.get("started_at"), STAMP)
    except (TypeError, ValueError):
        return False
    return (isinstance(data.get("worktree"), str) and isinstance(pid, int) and not isinstance(pid, bool) and pid > 0
            and (data.get("ended_at") is None or isinstance(data.get("ended_at"), str))
            and isinstance(data.get("session_id"), str) and isinstance(role, dict) and "value" in role)


def live_writers(root: Path, worktree: str) -> list[dict]:
    """The live writing sessions of ``worktree`` read from the session records. A record that cannot be read or is
    not of the record's form refuses (fail closed): it could be a live writer's. A place that is not a folder holds no
    record (``write`` writes into a folder only), so it hides none; a folder that cannot be listed refuses."""
    base = folder(root)
    if not base.is_dir():
        return []
    try:
        names = sorted(os.listdir(base))
    except OSError:
        raise _refuse(f"the session records' folder {base} cannot be listed, so it cannot be shown that no writing "
                      f"session is live in the worktree {worktree} (DEC-847)") from None
    tree = os.path.realpath(worktree)
    found = []
    for path in (base / name for name in names if name.endswith(".json") and not name.startswith(".")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = None
        if not _shape(data):
            raise _refuse(f"the session record {path} cannot be read or is not of the record's form, so it cannot be "
                          f"shown that no writing session is live in the worktree {worktree} (DEC-847)")
        if os.path.realpath(data["worktree"]) != tree or data["ended_at"] is not None:
            continue
        if data["role"]["value"] in REVIEWERS or not alive(data["pid"], data["started_at"]):
            continue
        found.append(data)
    return found


def check_one_writer(root: Path, worktree: str, role: str) -> None:
    """S10, S12: a writing role is refused while a writing session is live in its worktree, naming that session and
    the worktree; a reviewer is never refused for this."""
    if role in REVIEWERS:
        return
    live = live_writers(root, worktree)
    if live:
        first = live[0]
        raise _refuse(f"a writing session is live in the worktree {worktree}: session {first['session_id']} "
                      f"({first['role']['value']}, pid {first['pid']}); two sessions that write never share a "
                      f"worktree (DEC-847, DEC-963, DEC-1156 (3))")
