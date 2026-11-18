"""Support code for the W2-60b acceptance tests (standard library and PyYAML only).

W2-60b (DAEO-ecac) makes ``gov launch`` leave one record per launched session, ``.gov-runtime/sessions/<session
id>.json`` in the repository's main checkout, written whole at the session's start and replaced whole after it ends
(every exit path), its values read from the harness's own record of the session (its session log, through W1-31's
reader, and the result line of a ``--output-format json`` run); it reads the launchable roles from the kernel's role
files; it refuses a second writing session in a worktree that has one live; ``--tests-worktree`` makes a ticket's tests
worktree; and the guard knows ``qa-engineer``. The cases drive the public interfaces: ``gov launch`` through its
console-script entry point, the record file it leaves, ``gov.launch.session_record.read_record``, the product guard's
hook (W1-02's harness) and ``gov.guard.decide.KNOWN_ROLES``.

The launch machinery (sandbox HOME, open resource gate, fixture project, run of ``gov``) is W2-60a's support module,
with W2-184's RUBRIC-2 fixture project on top (role files with tables, ``criticality.yaml``, probe records), imported
as ``b`` and ``s``; nothing of them is changed here. This module adds:

- **The planted CLI** at ``<HOME>/.local/bin/claude``, which starts no model. It reads the ``--session-id``,
  ``--model`` and ``--effort`` it is given; writes the planted session log for that id at
  ``<config>/projects/<folder>/<session id>.jsonl`` (``config`` is ``CLAUDE_CONFIG_DIR`` when set, else
  ``<HOME>/.claude``), with its sub-agents' files under ``<session id>/subagents/``; prints the planted result line
  when it was given ``--output-format json``; and then exits with the planted code, or waits to be signalled. The log's
  ``@SID@``, ``@MODEL@`` and ``@EFFORT@`` are written as the id, model and effort the CLI was given, as a real session's
  log carries its own. What it does is set per case by a plan file.
- **The planted log** (``PlantedLog``), in the forms W1-31's specimens and the harness's real logs show (Claude Code
  2.1.31x-2.1.32x): assistant lines with ``usage`` and ``perTurnEffort``, a user prompt, ``compact_boundary`` lines,
  ``api_error`` lines (a rate-limit event is one with ``error.status`` 429), an optional totals (``cost-state``) line and
  sub-agent files with their ``.meta.json``. Each form was checked against W1-31's reader on the base
  (``gov.telemetry.sessionlog.read`` reads it without refusing and gives the sums ``PlantedLog.usage`` states).
- **Session records**: the reader of the file a launch leaves, the planted live record of the one-writer cases.
"""

from __future__ import annotations

import json
import os
import signal
import stat
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W2-184"))
import w2_184_support as s  # noqa: E402

b = s.b
REPO_ROOT = b.REPO_ROOT
ENGINEER, TEST_DESIGNER, AUDITOR = s.ENGINEER, s.TEST_DESIGNER, s.AUDITOR
RESEARCH, PRODUCT_SPEC = s.RESEARCH, s.PRODUCT_SPEC
QA = "qa-engineer"
SIXTH = "zq-checker"            # an invented worker role: a role file and nothing else
ABSENT = "zq-absent"            # a role named in a ticket with no role file
OPUS, SONNET, HAIKU5 = s.OPUS, s.SONNET, s.HAIKU5

SESSIONS_REL = ".gov-runtime/sessions"
LAUNCHES_REL = ".gov-runtime/launches"
CIT_E_REL = "docs/changes/W2-60b-CIT-E.md"
BASE_COMMIT = "4bc0399fb"        # w2/W2-60b at the claim: the code before the change
DECIDE_REL = "src/gov/guard/decide.py"
LAUNCHER_REL = "src/gov/launch/launcher.py"
KERNEL_ROLES = REPO_ROOT / "template/governance/kernel/roles"

INTERRUPT_EXIT = 130             # DEC-392: the launcher's exit after an ending signal
END_WAIT_S = 5

# The record's keys (the interface at claim, DEC-1157, as the lead settled their names).
HOUSEKEEPING = ("record", "format", "session_id", "worktree", "pid", "started_at", "ended_at", "exit_code")
FROM_LAUNCH_RECORD = ("role", "ticket", "task_class", "criticality", "promotion")
MEASURED = ("role", "ticket", "task_class", "model", "effort", "window", "tokens_input", "tokens_output",
            "tokens_cache_creation", "tokens_cache_read", "cost_usd", "minutes", "turns", "subagents",
            "rate_limit_events", "compactions", "claude_code_version", "tier", "criticality", "promotion")
TOKENS = ("tokens_input", "tokens_output", "tokens_cache_creation", "tokens_cache_read")
TIERS = ("opus", "sonnet", "haiku", "other")

# What only these tests write, so that a record can be searched for it (S3).
SENTENCE = "The zq60b marmoset counted seven lanterns beside the quiet harbour."
ERROR_WORD = "zq60b-error-text"
RESULT_WORD = "zq60b-result-text"
LOG_VERSION = "2.1.321"          # the Claude Code version the planted log's lines carry
LOG_FOLDER = "-w260b-planted-project"
ONE_MILLION = 1_000_000


# --------------------------------------------------------------------------
# The planted session log
# --------------------------------------------------------------------------

class _File:
    def __init__(self, owner, sidechain, agent=None):
        self.owner, self.sidechain, self.agent = owner, sidechain, agent
        self.lines, self.last = [], None


class PlantedLog:
    """One session's log: the session's own file and its sub-agents' files. Strings ``@SID@``, ``@MODEL@`` and
    ``@EFFORT@`` are filled in by the planted CLI with what it was given."""

    def __init__(self, version=LOG_VERSION, cwd="/w260b/planted/project"):
        self.version, self.cwd = version, cwd
        self.count = 0
        self.main = _File(self, False)
        self.subs: list[_File] = []
        self.messages = []            # (file, model, usage) per message
        self.rate_limit_stamps = []   # the timestamps of the lines that are rate-limit events

    def _stamp(self):
        return f"2026-11-16T06:{self.count // 60:02d}:{self.count % 60:02d}.000Z"

    def _full(self, file, head, **tail):
        self.count += 1
        line_id = f"6060b000-{self.count:04d}-4000-8000-{self.count:012d}"
        line = {"parentUuid": file.last, "isSidechain": file.sidechain,
                **({"agentId": file.agent} if file.agent else {}), **head, "uuid": line_id,
                "timestamp": self._stamp(), **tail, "userType": "external", "entrypoint": "sdk-cli", "cwd": self.cwd,
                "sessionId": "@SID@", "version": self.version, "gitBranch": "main"}
        file.lines.append(line)
        file.last = line_id
        return line

    def prompt(self, text="Work on the planted ticket.", file=None):
        self._full(file or self.main, {"promptId": "prompt-w260b", "type": "user",
                                       "message": {"role": "user", "content": text}}, permissionMode="default")
        return self

    def say(self, usage, text="Done with this step.", file=None, model="@MODEL@", effort="@EFFORT@"):
        """One message of the model: ``usage`` is ``(input, output, cache creation, cache read)``."""
        file = file or self.main
        fresh, out, created, read = usage
        number = len(self.messages) + 1
        message = {"model": model, "id": f"msg_w260b_{number:03d}", "type": "message", "role": "assistant",
                   "content": [{"type": "text", "text": text}], "stop_reason": "end_turn", "stop_sequence": None,
                   "usage": {"input_tokens": fresh, "cache_creation_input_tokens": created,
                             "cache_read_input_tokens": read, "output_tokens": out, "service_tier": "standard"}}
        tail = {"requestId": f"req_w260b_{number:03d}", "perTurnEffort": effort}
        if file.agent:
            tail["attributionAgent"] = "general-purpose"
        self._full(file, {"message": message, "type": "assistant"}, **tail)
        self.messages.append((file, model, usage))
        return self

    def compaction(self, pre_tokens=180_000):
        self._full(self.main, {"type": "system", "subtype": "compact_boundary", "content": "Conversation compacted",
                               "isMeta": False, "level": "info",
                               "compactMetadata": {"trigger": "auto", "preTokens": pre_tokens, "durationMs": 14000,
                                                   "postTokens": 4000}})
        return self

    def api_error(self, status, rate_limits=None, attempt=1):
        """An API error line; with status 429 it is a rate-limit event."""
        line = self._full(self.main, {"type": "system", "subtype": "api_error", "level": "error",
                                      "error": {"message": f"{ERROR_WORD} status {status}", "status": status,
                                                "rateLimits": rate_limits},
                                      "retryInMs": 2000, "retryAttempt": attempt, "maxRetries": 10})
        if status == 429:
            self.rate_limit_stamps.append(line["timestamp"])
        return self

    def subagent(self, agent, model, usage=(30, 40, 0, 0)):
        """A sub-agent's file ``<sid>/subagents/agent-<agent>.jsonl`` with one task and one message of ``model``."""
        file = _File(self, True, agent)
        self.subs.append(file)
        self.prompt("Run the one planted step.", file=file)
        self.say(usage, file=file, model=model, effort="high")
        return self

    def cost_line(self, cost=0.4321, duration=90_000):
        """A totals line (``cost-state``), as W1-31's specimens end with, holding a cost."""
        self.main.lines.append({"type": "cost-state", "sessionId": "@SID@", "totalCostUSD": cost,
                                "totalAPIDuration": duration, "totalAPIDurationWithoutRetries": duration - 31,
                                "totalToolDuration": 100, "totalLinesAdded": 0, "totalLinesRemoved": 0,
                                "totalDuration": duration + 2000, "startTime": 1791398922006,
                                "modelUsage": {}, "hasUnknownModelCost": False})
        return self

    def usage(self, subagents=False):
        """``(input, output, cache creation, cache read)`` summed over the messages (the session's own file only,
        unless ``subagents``)."""
        chosen = [u for f, _, u in self.messages if subagents or f is self.main]
        return tuple(sum(u[i] for u in chosen) for i in range(4))

    def subagent_models(self):
        return [m for f, m, _ in self.messages if f is not self.main]

    def spec(self):
        """What the planted CLI writes: the main file's text and each sub-agent file's text, by name."""
        def text(lines):
            return "".join(json.dumps(line, separators=(",", ":")) + "\n" for line in lines)
        main = [{"type": "queue-operation", "sessionId": "@SID@"}, *self.main.lines,
                {"type": "last-prompt", "sessionId": "@SID@"}]
        side = {}
        for file in self.subs:
            side[f"agent-{file.agent}.jsonl"] = text(file.lines)
            side[f"agent-{file.agent}.meta.json"] = json.dumps(
                {"agentType": "general-purpose", "description": "run the one planted step", "toolUseId": None,
                 "spawnDepth": 1}, separators=(",", ":"))
        return {"folder": LOG_FOLDER, "main": text(main), "side": side}


def rich_log(*, cost=False, compactions=3, subagents=()):
    """The planted log of the value cases: a prompt and an answer that hold ``SENTENCE``, four messages with usage
    and ``perTurnEffort``, three compactions, one 503 error and two rate-limit events (429, one with a
    ``rateLimits`` object), no totals line unless ``cost``. ``subagents``: ``(agent id, model)`` pairs."""
    log = PlantedLog().prompt(f"Please note: {SENTENCE}")
    log.say((1200, 300, 5000, 0), text=f"I read it. {SENTENCE}")
    log.say((80, 150, 0, 6000))
    log.api_error(503)
    log.api_error(429, rate_limits={"unifiedRateLimitStatus": "rejected", "resetsAt": 1791400000})
    for _ in range(compactions):
        log.compaction()
    log.say((60, 120, 200, 9000))
    log.api_error(429, attempt=2)
    log.say((40, 90, 0, 9500))
    for agent, model in subagents:
        log.subagent(agent, model)
    if cost:
        log.cost_line()
    return log


def result_line(cost=0.4321, window=ONE_MILLION, turns=4, duration_ms=125_000):
    """The result line of a ``--output-format json`` run, as the harness prints it (F-models-context F5, F8:
    ``modelUsage`` per model with ``contextWindow``)."""
    return json.dumps({
        "type": "result", "subtype": "success", "is_error": False, "duration_ms": duration_ms,
        "duration_api_ms": duration_ms - 30_000, "num_turns": turns, "result": RESULT_WORD,
        "session_id": "@SID@", "total_cost_usd": cost,
        "usage": {"input_tokens": 1380, "cache_creation_input_tokens": 5200, "cache_read_input_tokens": 24500,
                  "output_tokens": 660, "service_tier": "standard"},
        "modelUsage": {"@MODEL@": {"inputTokens": 1380, "outputTokens": 660, "cacheReadInputTokens": 24500,
                                   "cacheCreationInputTokens": 5200, "webSearchRequests": 0, "costUSD": cost,
                                   "contextWindow": window, "maxOutputTokens": 64000}},
        "permission_denials": [], "uuid": "6060b000-0000-4000-8000-000000000001"}, separators=(",", ":"))


# --------------------------------------------------------------------------
# The planted CLI
# --------------------------------------------------------------------------

_STUB = r'''#!@PYTHON@
"""Planted Claude Code CLI (W2-60b acceptance tests). Starts no model; writes the planted session log."""
import json, os, sys, time

args = sys.argv[1:]


def value(name):
    for index, arg in enumerate(args):
        if arg == name and index + 1 < len(args):
            return args[index + 1]
        if arg.startswith(name + "="):
            return arg.split("=", 1)[1]
    return None


sid = value("--session-id") or "no-session-id"
model = value("--model") or "no-model"
effort = value("--effort") or "no-effort"
with open(@PLAN@, encoding="utf-8") as handle:
    plan = json.load(handle)


def fill(text):
    return text.replace("@SID@", sid).replace("@MODEL@", model).replace("@EFFORT@", effort)


call = {"args": args, "cwd": os.getcwd(), "session_id": sid, "pid": os.getpid(), "ppid": os.getppid(),
        "settings": [value("--settings")] if value("--settings") is not None else [], "appended": [],
        "records_at_start": {}}
log = plan.get("log")
if log is not None:
    config = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.environ["HOME"], ".claude")
    folder = os.path.join(config, "projects", log["folder"])
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, sid + ".jsonl"), "w", encoding="utf-8") as handle:
        handle.write(fill(log["main"]))
    for name, text in log.get("side", {}).items():
        path = os.path.join(folder, sid, "subagents", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(fill(text))
watch = plan.get("watch")
if watch:
    path = os.path.join(watch["folder"], sid + ".json")
    seen, end = None, time.monotonic() + watch["seconds"]
    while time.monotonic() < end:
        try:
            with open(path, encoding="utf-8") as handle:
                seen = handle.read()
            break
        except OSError:
            time.sleep(0.05)
    call["record_seen"] = seen
with open(@CALLS@, "a", encoding="utf-8") as handle:
    handle.write(json.dumps(call) + "\n")
if plan.get("result") is not None and value("--output-format") == "json":
    sys.stdout.write(fill(plan["result"]) + "\n")
    sys.stdout.flush()
if plan.get("ready"):
    open(plan["ready"], "w").close()
if plan.get("sleep"):
    time.sleep(plan["sleep"])
sys.exit(int(plan.get("exit", 0)))
'''


@dataclass(frozen=True)
class Cli:
    path: Path
    calls_file: Path
    plan_file: Path


def install_cli(box):
    calls_file = box.elsewhere / "w260b-calls.jsonl"
    plan_file = box.elsewhere / "w260b-plan.json"
    text = (_STUB.replace("@PYTHON@", sys.executable).replace("@PLAN@", repr(str(plan_file)))
            .replace("@CALLS@", repr(str(calls_file))))
    path = box.home / b.CLI_REL
    b.write(path, text)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    cli = Cli(path, calls_file, plan_file)
    set_plan(cli)
    return cli


def set_plan(cli, *, log=None, result=None, exit_code=0, watch=None, ready=None, sleep=0):
    """What the planted CLI does at its next starts: ``log`` a ``PlantedLog`` (None: no log), ``result`` a result
    line printed for ``--output-format json``, ``watch`` ``(folder, seconds)`` to wait for ``<folder>/<sid>.json`` and
    note what it held, ``ready`` a file touched once the log is written, ``sleep`` seconds before the exit."""
    plan = {"log": None if log is None else log.spec(), "result": result, "exit": exit_code,
            "watch": None if watch is None else {"folder": str(watch[0]), "seconds": watch[1]},
            "ready": None if ready is None else str(ready), "sleep": sleep}
    cli.plan_file.write_text(json.dumps(plan), encoding="utf-8")


def calls(cli):
    if not cli.calls_file.is_file():
        return []
    return [json.loads(line) for line in cli.calls_file.read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------
# Launching
# --------------------------------------------------------------------------

def launch(box, cli, role, tk, *cli_args, options=(), cwd=None):
    """``gov launch <role> <ticket> <options> [-- <cli_args>]`` from ``cwd`` (else the main checkout). Returns
    W2-60a's ``Launch`` over this CLI's calls and the main checkout's launch records."""
    root = Path(cwd) if cwd is not None else Path(box.project)
    records = Path(box.records)
    before_calls, before = len(calls(cli)), b._listing(records)
    started = time.time()
    run = b.run_gov(box, root, "launch", role, tk, *options, *(("--", *cli_args) if cli_args else ()))
    return b.Launch(run, tuple(calls(cli)[before_calls:]), records, before, b._listing(records), started,
                    time.time(), tuple(cli_args))


def start_launch(box, role, tk, *cli_args, cwd=None):
    """``gov launch`` started in a session (and process group) of its own, as W2-56's ending cases start it, so that a
    signal sent to its pid reaches the launcher alone; SIGINT, SIGTERM and SIGHUP set to their default first."""
    def starting():
        for number in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            signal.signal(number, signal.SIG_DFL)
    argv = b.gov_argv("launch", role, tk, *(("--", *cli_args) if cli_args else ()))
    return subprocess.Popen(argv, cwd=str(cwd or box.project), env=b.base_environment(box), stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True,
                            preexec_fn=starting)


def finish(process, timeout=60.0):
    try:
        out, err = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except OSError:
            pass
        out, err = process.communicate()
        raise AssertionError(f"gov launch did not end within {timeout:.0f} s\nstderr:\n{err[-1500:]}") from None
    return process.returncode, out, err


def wait_for(predicate, timeout, step=0.05):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(step)
    return bool(predicate())


# --------------------------------------------------------------------------
# Session records
# --------------------------------------------------------------------------

def sessions(main):
    return Path(main) / SESSIONS_REL


def record_files(main):
    folder = sessions(main)
    return sorted(p.name for p in folder.iterdir()) if folder.is_dir() else []


def session_record(main, sid, what=""):
    """The session record ``<main>/.gov-runtime/sessions/<sid>.json``, read as JSON; fails naming what is there."""
    path = sessions(main) / f"{sid}.json"
    assert path.is_file(), (f"no session record {path.name} in {sessions(main)} {what}\n"
                            f"the folder holds: {record_files(main)}")
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except ValueError:
        raise AssertionError(f"the session record {path} is not JSON: {text[:300]!r}") from None
    assert isinstance(data, dict), f"the session record {path} is not a JSON object"
    return data


def launch_record(main, sid):
    path = Path(main) / LAUNCHES_REL / f"{sid}.json"
    assert path.is_file(), f"no launch record {path.name} in {path.parent}"
    return json.loads(path.read_text(encoding="utf-8"))


def entry(record, key):
    assert key in record, f"the session record has no key {key!r}; its keys: {sorted(record)}"
    value = record[key]
    assert isinstance(value, dict) and "value" in value, (
        f"the record's {key!r} is not an object {{'value': ..., 'source' or 'not_measured': ...}}: {value!r}")
    return value


def measured(record, key):
    """The value of a key the case knows is given: it is measured, with its source named."""
    item = entry(record, key)
    assert isinstance(item.get("source"), str) and item["source"].strip(), (
        f"the record's {key!r} names no source: {item!r}")
    assert "not_measured" not in item, f"the record's {key!r} is measured and not measured at once: {item!r}"
    assert item["value"] is not None, f"the record's {key!r} is given by the harness's record but is null: {item!r}"
    return item["value"]


def not_measured(record, key):
    """A key the case knows is not given: value null and a reason, never 0."""
    item = entry(record, key)
    assert item["value"] is None, (
        f"the record's {key!r} is not given by the session's log or result line, yet its value is "
        f"{item['value']!r} (never 0 or a guess for not measured): {item!r}")
    reason = item.get("not_measured")
    assert isinstance(reason, str) and reason.strip(), f"the record's {key!r} is not measured but gives no reason: {item!r}"
    return reason


def assert_form(record):
    """Every key present; each measured key an object with its value and a named source, or a null value and the
    reason it is not measured; never 0 for not measured. A key copied from the launch record may be null with its
    source (S11)."""
    missing = [key for key in (*HOUSEKEEPING, *MEASURED) if key not in record]
    assert not missing, f"the session record lacks the keys {missing}; it holds {sorted(record)}"
    assert record["record"] == "gov-session" and record["format"] == 1, (
        f"the record's 'record' and 'format' are not 'gov-session' and 1: {record['record']!r}, {record['format']!r}")
    for key in MEASURED:
        item = entry(record, key)
        source, reason = item.get("source"), item.get("not_measured")
        if isinstance(reason, str) and reason.strip():
            assert item["value"] is None, f"{key!r} says not measured but holds the value {item['value']!r}: {item!r}"
            assert source is None, f"{key!r} names a source and says not measured: {item!r}"
        else:
            assert isinstance(source, str) and source.strip(), (
                f"{key!r} neither names its source nor says why it is not measured: {item!r}")
            assert item["value"] is not None or key in FROM_LAUNCH_RECORD, (
                f"{key!r} is null with a source, but only a key copied from the launch record may be: {item!r}")


def assert_ended(record, sid, worktree, exit_code):
    assert record["session_id"] == sid, f"the record's session_id {record['session_id']!r} is not {sid!r}"
    assert record["worktree"] == os.path.realpath(worktree), (
        f"the record's worktree {record['worktree']!r} is not the launched tree {os.path.realpath(worktree)!r}")
    assert isinstance(record["pid"], int) and not isinstance(record["pid"], bool) and record["pid"] > 0, (
        f"the record's pid is not a process id: {record['pid']!r}")
    assert isinstance(record["started_at"], str) and record["started_at"], "the record has no started_at"
    assert isinstance(record["ended_at"], str) and record["ended_at"], (
        f"the session has ended, but the record's ended_at is {record['ended_at']!r}")
    assert record["exit_code"] == exit_code, (
        f"the record's exit_code is {record['exit_code']!r}, not the launcher's {exit_code}")


def copied(record, key, given):
    """A key copied from the launch record: its value is ``given`` (null when the launch record gives null, S11),
    with its source named, or, when null, a source or a reason."""
    item = entry(record, key)
    assert item["value"] == given, (
        f"the record's {key!r} is {item['value']!r}, not the launch record's {given!r}: {item!r}")
    named = isinstance(item.get("source"), str) and item["source"].strip()
    reason = isinstance(item.get("not_measured"), str) and item["not_measured"].strip()
    assert named or (given is None and reason), f"the record's {key!r} names no source: {item!r}"
    return item


def assert_from_launch_record(record, launched):
    """``role``, ``ticket`` and ``task_class`` are the launch record's ``role``, ``ticket`` and ``ticket_class``."""
    for key, source_key in (("role", "role"), ("ticket", "ticket"), ("task_class", "ticket_class")):
        copied(record, key, launched[source_key])


def text_of(main, sid):
    return (sessions(main) / f"{sid}.json").read_text(encoding="utf-8")


def plant_record(main, worktree, role, *, pid, ended=False, sid=None, ticket="DAEO-zzzz"):
    """A session record in the main checkout's folder, of the interface's form: ``worktree`` the tree's real path,
    ``ended_at`` null unless ``ended``, ``pid`` as given. Returns its session id."""
    sid = sid or str(uuid.uuid4())
    given = {"value": None, "not_measured": "planted: the session has not ended"}
    record = {"record": "gov-session", "format": 1, "session_id": sid, "worktree": os.path.realpath(worktree),
              "pid": pid, "started_at": "2026-11-16T05:00:00Z",
              "ended_at": "2026-11-16T05:30:00Z" if ended else None, "exit_code": 0 if ended else None}
    for key in MEASURED:
        record[key] = dict(given)
    record["role"] = {"value": role, "source": "launch record"}
    record["ticket"] = {"value": ticket, "source": "launch record"}
    record["task_class"] = {"value": "implementation", "source": "launch record"}
    folder = sessions(main)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{sid}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return sid


def dead_pid():
    """The id of a process that has ended (and been reaped)."""
    done = subprocess.Popen([sys.executable, "-c", "pass"])
    done.wait()
    return done.pid


# --------------------------------------------------------------------------
# Roles and tickets
# --------------------------------------------------------------------------

def worker_role_text(role, model=SONNET, effort="high"):
    """A worker role file in the form of the kernel's worker role files (version, default line, purpose, allowed
    paths, tools, the launcher's empty network profile, worker authority, handoff); no skills, no table."""
    return "\n".join([
        f"# {role} role (W2-60b fixture)",
        "",
        f"A planted worker role, {role}, that no code names. It states what the guard and the launcher decide; it "
        "grants nothing itself.",
        "",
        "- **Version:** 1.0.0",
        f"- **Launch default:** model {model}, effort {effort}",
        f"- **Purpose:** check planted work as a fresh session (the W2-60b fixture {role}).",
        "- **Allowed paths:** its ticket's `allowed_paths` (its findings report), while its ticket is `in_progress`.",
        "- **Tools:** Read, Grep, Glob, Edit, Write, Bash.",
        "- **Network:** the launcher's profile for this role, which is empty: a strict sandbox allowlist with no "
        "allowed domain. The guard grants no network.",
        "- **Authority level:** worker, with no approval authority.",
        "- **Handoff format:** its findings report.",
        "",
    ])


def template_files(role):
    """The role's template under every name a launcher could look for (``role-<role>.md`` and ``<role>.md``); any
    bytes (W2-153's form). The template is not under test here."""
    text = f"---\nname: role-{role}\n---\n# W2-60b fixture template for {role} {b.TEMPLATE_WORD}\n"
    return {f".claude/templates/role-{role}.md": text, f".claude/templates/{role}.md": text}


QA_SKILL = ".claude/skills/qa-review/SKILL.md"
QA_SKILL_TEXT = ("---\nname: qa-review\nversion: \"1.0.0\"\ndescription: The W2-60b fixture qa-review skill.\n---\n\n"
                 "# qa-review\n\nThe fixture method text.\n")


# The judging-work skill (W2-195, DEC-1204 (5)) a judging role's launch needs installed: the kernel file and the
# preloaded copy, the bytes this repository holds (the kernel's qa-engineer.md lists it among its skills).
JUDGING_SKILL_SRC = REPO_ROOT / "template/governance/kernel/skills/judging-work/SKILL.md"
JUDGING_SKILL_RELS = ("template/governance/kernel/skills/judging-work/SKILL.md",
                      ".claude/skills/judging-work/SKILL.md")


def plant_roles(project, roles=(SIXTH,)):
    """The sixth worker role's file (planted form) and the kernel's own ``qa-engineer.md`` (its bytes as they stand
    in this repository), with their templates and the skills the latter names (``qa-review`` as a fixture, and the
    installed ``judging-work``, which a judging role's launch is refused without)."""
    for role in roles:
        if role == QA:
            b.write(b.role_path(project, QA), (KERNEL_ROLES / "qa-engineer.md").read_text(encoding="utf-8"))
            b.write(Path(project) / QA_SKILL, QA_SKILL_TEXT)
            for rel in JUDGING_SKILL_RELS:
                b.write(Path(project) / rel, JUDGING_SKILL_SRC.read_text(encoding="utf-8"))
        else:
            b.write(b.role_path(project, role), worker_role_text(role))
        for rel, text in template_files(role).items():
            b.write(Path(project) / rel, text)


def plant_coordinators(project):
    """The kernel's own role files of the CTO, the Senior Engineer and the ticket lead, as they stand here."""
    for role in ("orchestrator", "senior-engineer", "ticket-lead"):
        b.write(b.role_path(project, role), (KERNEL_ROLES / f"{role}.md").read_text(encoding="utf-8"))


def ticket(project, tk, role, allowed=("docs/qa/findings.md",), profile="STANDARD", kind="implementation"):
    """An in_progress ticket whose ``role:`` is ``role`` (any name), not committed."""
    b.write(Path(project) / ".tickets" / f"{tk}.md", s.ticket_text(tk, role, list(allowed), profile, kind))
    return tk


def add_tree(box, name, branch=None):
    """A linked worktree ``<home>/work/<name>`` of the fixture project, on ``branch`` (default ``w2/<name>``), from the
    main checkout's HEAD."""
    return s.add_worktree(box.project, box.home / "work" / name, branch or f"w2/{name}")


def head(tree):
    return b.git(tree, "rev-parse", "HEAD").strip()


def branch(tree):
    return b.git(tree, "rev-parse", "--abbrev-ref", "HEAD").strip()
