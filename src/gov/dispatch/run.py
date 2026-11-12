"""One pass of the dispatcher: ``tick(root)`` (S1 to S10, F1).

Order of a pass: the OFF file (nothing runs); the lock (``tick.lock``; held by another pass: exit 4, nothing written);
the configuration; the readings (the gate, the processes); the returns (a finished session, a start that never ran);
the peaks; the ready list's entries in the list's order, each judged by its own checks (``readiness``) and then by the
machine's (gate, disk, ``max_leads``, the stagger, the room for the peak), at most one started; the escalations; the
status, written whole. The log name goes into ``started.txt`` before the launch command is spawned, so a crash after a
launch never starts that log again. Exit codes: 0 a pass done or nothing to do, 1 the pass failed, 2 a configuration
error, 3 the gate, the disk or the forecast refused a start, 4 the lock held.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from gov.dispatch import config as configuration
from gov.dispatch import peaks, procs, readiness, returns, status
from gov.dispatch import state as states
from gov.dispatch.shell import Runner

EXIT_OK, EXIT_FAILED, EXIT_CONFIG, EXIT_REFUSED, EXIT_LOCKED = 0, 1, 2, 3, 4
# The launch command runs in the ticket's worktree with the brief on its stdin and its output in the log; when it ends
# its exit code is written to <log>.exit. The wrapper is a shell of its own session: the pass does not wait for it.
WRAPPER = ('brief=$1; out=$2; done=$3; shift 3; "$@" < "$brief" > "$out" 2>&1; code=$?; '
           'echo "$code" > "$done.tmp" && mv "$done.tmp" "$done"')


def spawn(argv: list[str], cwd: Path, brief: Path, log: Path, exit_file: Path) -> None:
    subprocess.Popen(["/bin/sh", "-c", WRAPPER, "sh", str(brief), str(log), str(exit_file), *argv], cwd=cwd,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True, close_fds=True)


def fill(argument: str, values: dict) -> str:
    for name, value in values.items():
        argument = argument.replace("{" + name + "}", value)
    return argument


def tick(root: Path, now=None) -> tuple[int, dict | None]:
    """One pass: ``(exit code, the status data)``; the data is None when nothing was written (the lock was held)."""
    state = states.State(root)
    moment = now or states.now()
    if state.file("OFF").exists():
        data = {"ok": True, "time": states.stamp(moment), "outcome": "OFF", "exit_code": EXIT_OK}
        status.write(state, data)
        return EXIT_OK, data
    lock = state.lock()
    if lock is None:
        return EXIT_LOCKED, None
    try:
        state.make()
        try:
            code, data = _pass(Path(root), state, moment)
        except configuration.ConfigError as error:
            code, data = EXIT_CONFIG, status.failed(f"configuration: {error}", states.stamp(moment))
        except Exception as error:  # a pass that fails says so, whatever the failure (S5)
            code, data = EXIT_FAILED, status.failed(f"{type(error).__name__}: {error}", states.stamp(moment))
        data["exit_code"] = code
        status.write(state, data)
        return code, data
    finally:
        lock.close()


def _pass(root: Path, state: states.State, now) -> tuple[int, dict]:
    from gov.resources import config as gate_config
    from gov.resources import gate, machine

    conf = configuration.load(root)
    runner = Runner(conf.command_timeout_s)
    problems: list[str] = []
    reading = gate.read(True)
    values = gate_config.load()["values"]
    floor, working = values.get("memory_floor_bytes"), values.get("working_size_bytes")
    running = procs.find(machine.processes(), conf.job_markers)
    started = state.started()
    lately = {s.log for s in started if not state.exit_file(s.log).exists() and s.ticket not in running.tickets()
              and (now - s.at).total_seconds() <= conf.never_ran_after_s}
    pending = [s for s in started if s.log in lately]
    ctx = readiness.Context(root, conf, state, runner, {s.log for s in started}, running.tickets(),
                            {s.ticket for s in pending})
    state.record_seen()  # an item already in inbox/ or inbox/read/ counts as written (F-1)
    new_returns = returns.finished(ctx, problems)
    never = returns.never_ran(ctx, now)
    ctx.unread = {item.w2 for item in state.items() if item.w2}
    shown_peaks = peaks.refresh(state, root / conf.history, now)
    coming = peaks.ahead(shown_peaks, working, running, len(pending))

    disk = gate.check_disk()
    gate_reasons = [gate.describe(r) for r in reading["gate"]["reasons"]]
    shut = [gate.describe(r) for r in reading["gate"]["reasons"] if r["condition"] not in ("disk", "inodes")]
    full = [gate.describe(r) for r in disk["reasons"]]
    last = max((s.at for s in started), default=None)

    def machine_reason() -> tuple[str | None, bool]:
        """Why the machine cannot start another lead now, and whether the gate or the forecast refused it."""
        if shut:
            return "gate shut: " + "; ".join(shut), True
        if full:
            return "disk full: " + "; ".join(full), True
        if len(running.leads) + len(pending) >= conf.max_leads:
            return f"max_leads reached: {len(running.leads)} running and {len(pending)} just started of " \
                   f"{conf.max_leads}", False
        if last is not None and (now - last).total_seconds() < conf.stagger_s:
            return f"stagger: the last start was {(now - last).total_seconds():.0f} s ago, " \
                   f"{conf.stagger_s:g} s are kept between two", False
        no_room = peaks.room(shown_peaks, working, floor, reading["available_memory_bytes"], reading["nproc"],
                             reading["busy_cores_1m"], conf.cpu_band, coming)
        return no_room, no_room is not None

    skipped, began, refused = [], None, False
    for entry in states.read_ready(state):
        why = readiness.reason(entry, ctx)
        if why is None and began is not None:
            why = f"one start per pass: {began.log} was started in this pass"
        elif why is None:
            why, held = machine_reason()
            refused = refused or held
        if why is None:
            began = _start(entry, ctx, state, conf, now)
            ctx.started_logs.add(entry.log)
            continue
        skipped.append({"W2": entry.w2, "log": entry.log, "line": entry.line, "reason": why})
    raised = returns.escalate(ctx, conf, problems, now)

    code = EXIT_OK if began is not None or not refused else EXIT_REFUSED
    data = {
        "ok": True, "time": states.stamp(now),
        "outcome": "started" if began is not None else "refused" if refused else "idle", "exit_code": code,
        "running": [{"ticket": r["ticket"], "pid": r["pid"]} for r in running.leads],
        "running_jobs": [{"kind": j["kind"], "pid": j["pid"]} for j in running.jobs],
        "pending_starts": [{"log": s.log, "ticket": s.ticket} for s in pending],
        "load": {"load_1m": reading["load_1m"], "load_15m": reading["load_15m"],
                 "busy_cores": reading["busy_cores_1m"], "nproc": reading["nproc"]},
        "memory": {"available_bytes": reading["available_memory_bytes"], "floor_bytes": floor,
                   "working_size_bytes": working},
        "gate": {"open": reading["gate"]["open"], "reasons": gate_reasons,
                 "disk": {"open": disk["open"], "free_bytes": disk["free_bytes"], "free_inodes": disk["free_inodes"]}},
        "slots": reading["slots"],
        "peaks": peaks.shown(shown_peaks, working), "peaks_ahead": coming,
        "queue": _queue(state),
        "inbox": [{"name": i.path.name, "W2": i.w2, "log": i.log, "status": i.status, "age_s": round(i.age_s)}
                  for i in state.items()],
        "started": None if began is None else {"W2": began.w2, "log": began.log, "ticket": began.ticket},
        "skipped": skipped, "nightly_hold": conf.nightly_hold,
        "returns_written": new_returns, "never_ran_written": never, "escalations": raised, "problems": problems,
    }
    return code, data


def _queue(state: states.State) -> list[str]:
    """``land.txt``'s lines not yet in ``land-done.txt`` (the landing step is part b's; here the queue is only shown)."""
    done = state.lines("land-done.txt")
    return [line for line in state.lines("land.txt") if not any(d == line or d.startswith(line) for d in done)]


def _start(entry: states.Entry, ctx: readiness.Context, state: states.State, conf, now) -> states.Entry:
    """Record the start, then spawn the launch command detached; a spawn that fails leaves its exit file (127)."""
    state.record_start(entry.log, entry.w2, entry.ticket)  # before the launch: a crash after it never starts it twice
    values = {"ticket": entry.ticket, "w2": entry.w2, "brief": str(ctx.brief(entry.brief)), "log": entry.log}
    argv = [fill(argument, values) for argument in conf.launch_command]
    log, exit_file = state.logs / entry.log, state.exit_file(entry.log)
    try:
        spawn(argv, ctx.worktree(entry.w2), ctx.brief(entry.brief), log, exit_file)
    except OSError as error:
        log.write_text(f"the launch command could not be started: {error}\n", encoding="utf-8")
        exit_file.write_text("127\n", encoding="utf-8")
        raise RuntimeError(f"the launch of {entry.log} could not be started: {error}") from None
    return entry
