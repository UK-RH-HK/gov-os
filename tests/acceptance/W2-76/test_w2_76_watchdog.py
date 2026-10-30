"""KPI success 2 and failures "a slow rebuild with no record", "a rebuild stopped by the watchdog".

Past ``slow_after_s`` (here 2 s, set by ``rebuild.yaml``; the default is 1800), counted from the lock taken, the
rebuild writes ``.gov-runtime/rebuild/record.json`` at once and rewrites it while it runs (at least once per threshold
when the threshold is shorter than 30 s): the stages done with their times, the stage running and how long, each of
its processes (pid, parent, state, wait channel, command line), the load and the time of the write. It prints one
``rebuild: slow:`` line naming the record, says ``slow: true`` with ``slow_after_s``, keeps the record as
``slow-<UTC start>.json``, and goes on to the end with the same stores. A fault of the watchdog itself is reported
on standard error and in ``watchdog_faults`` and never changes the rebuild's success (DEC-939 item 2, row W2-L451).

The planted slow stage is a ``gitleaks`` first on ``PATH`` that sleeps on its first call, then hands on to the real
one: the secrets filter, inside the lexical stage, runs long.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import w2_76_support as support

pytestmark = support.needs_tools

THRESHOLD_S = 2
SLEEP_S = 9.0


def _numbers(value):
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, (list, tuple)):
        return bool(value) and all(_numbers(item) for item in value)
    if isinstance(value, dict):
        return bool(value) and all(_numbers(item) for item in value.values())
    return False


def _check_live_record(record, text, rebuild_pid):
    """One record read while the slow rebuild runs: every part the design names, in one of the accepted names."""
    problems = []
    procs_key = support.first_key(record, support.PROCESSES_KEYS)
    procs = record.get(procs_key) if procs_key else None
    if not isinstance(procs, list) or not procs or not all(isinstance(p, dict) for p in procs):
        return [f"no process list (one of {support.PROCESSES_KEYS})"]
    for proc in procs:
        for names, what in ((("pid",), "pid"), (support.PARENT_KEYS, "parent"), (("state",), "state"),
                            (support.WCHAN_KEYS, "wait channel"), (support.CMDLINE_KEYS, "command line")):
            if support.first_key(proc, names) is None:
                problems.append(f"a process without its {what} ({names}): {proc}")
        command = proc.get(support.first_key(proc, support.CMDLINE_KEYS) or "", "")
        if isinstance(command, str) and len(command) > 200:
            problems.append(f"a command line longer than 200 characters ({len(command)})")
    pids = {proc.get("pid") for proc in procs}
    if rebuild_pid not in pids:
        problems.append(f"the rebuild's own process {rebuild_pid} is not in the list: {sorted(map(str, pids))}")
    sleeping = [proc for proc in procs if "gitleaks" in str(proc.get(support.first_key(proc, support.CMDLINE_KEYS)
                                                                       or "", ""))]
    if not sleeping:
        problems.append("the descendant the rebuild waits on (the planted gitleaks) is not in the list")
    for proc in sleeping:
        state = proc.get("state")
        wchan = proc.get(support.first_key(proc, support.WCHAN_KEYS) or "")
        if not (isinstance(state, str) and state.strip()):
            problems.append(f"the waiting process has no state: {proc}")
        if not (isinstance(wchan, str) and wchan.strip()):
            problems.append(f"the waiting process has no wait channel: {proc}")
    load_key = support.first_key(record, support.LOAD_KEYS)
    if load_key is None or not _numbers(record[load_key]):
        problems.append(f"no load (one of {support.LOAD_KEYS}, numbers)")
    if support.first_key(record, support.WRITTEN_KEYS) is None:
        problems.append(f"no time of the write (one of {support.WRITTEN_KEYS})")
    running_key = support.first_key(record, support.RUNNING_KEYS)
    running = record.get(running_key) if running_key else None
    if running is None or not any(name in json.dumps(running) for name in ("lexical", "secrets")):
        problems.append(f"the stage running (one of {support.RUNNING_KEYS}) does not name the lexical stage or the "
                        f"secrets filter: {running!r}")
    running_for = (any(_numbers(v) for v in running.values()) if isinstance(running, dict)
                   else support.first_key(record, support.RUNNING_FOR_KEYS) is not None)
    if not running_for:
        problems.append(f"how long the stage has run is not given (a number in {running_key}, or one of "
                        f"{support.RUNNING_FOR_KEYS})")
    done_key = support.first_key(record, support.DONE_KEYS)
    if done_key is None or "record" not in json.dumps(record[done_key]):
        problems.append(f"the stages done with their times (one of {support.DONE_KEYS}) do not hold the record stage")
    if support.LONG_HEX.search(text):
        problems.append(f"an uncut run of 13 or more hex digits: {support.LONG_HEX.search(text).group(0)}")
    return problems


def test_a_slow_rebuild_records_what_it_waits_on_and_goes_on(box, lock):
    project = support.make_project(box, "project", lock, slow_after_s=THRESHOLD_S)
    unslowed = support.rebuild(project, support.environment(box), "--no-embeddings")
    assert unslowed.returncode == 0, f"the unslowed rebuild of the same tree failed\n{unslowed.describe()}"
    env = support.environment(box, support.slow_gitleaks(box, "slow-tools", SLEEP_S))

    background = support.Background(project, env, support.rebuild_argv("--no-embeddings"), box.base / "out")
    live, writes, unreadable = [], set(), 0
    try:
        while background.running():
            record, text = support.read_record(project)
            if record is not None and background.running():
                procs = record.get(support.first_key(record, support.PROCESSES_KEYS) or "") or []
                if any(isinstance(p, dict) and p.get("pid") == background.pid for p in procs):
                    written = record.get(support.first_key(record, support.WRITTEN_KEYS) or "")
                    live.append((record, text))
                    writes.add(json.dumps(written))
            elif text is not None:
                unreadable += 1
            time.sleep(0.25)
    finally:
        run = background.finish()

    assert run.returncode == 0 and run.envelope().get("ok") is True, \
        f"the slow rebuild did not go on to a successful end\n{run.describe()}"
    assert live, f"no record of this rebuild's processes while it ran ({unreadable} reads were not whole JSON)\n" \
                 f"{run.describe()}"
    assert len(writes) >= 2, f"the record was not rewritten while the rebuild ran (times of the writes: {writes})"
    problems = _check_live_record(*live[-1], background.pid)
    assert not problems, "the live record lacks what it must hold:\n- " + "\n- ".join(problems)

    flagged = [line for line in run.stderr.splitlines() if line.startswith("rebuild: slow:")]
    assert len(flagged) == 1 and support.RECORD_REL in flagged[0], \
        f"one `rebuild: slow:` line naming {support.RECORD_REL} was expected\nstderr:\n{run.stderr[-2000:]}"
    result = run.result
    assert result.get("slow") is True and result.get("slow_after_s") == THRESHOLD_S, \
        f"the result does not flag the rebuild slow\n{run.describe()}"
    timing = result.get("timing") or {}
    assert timing.get("secrets_s", 0) >= SLEEP_S - 1 and timing.get("lexical_s", 0) >= SLEEP_S - 1, \
        f"the planted slow secrets filter is not in its stage times: {timing}"
    assert result.get("digest") == unslowed.result.get("digest") and result.get("digest"), \
        "the slow rebuild built a different digest from an unslowed rebuild of the same tree"
    assert result.get("stores") == unslowed.result.get("stores"), "the slow rebuild built different stores"

    kept = sorted((Path(project) / support.RECORD_DIR_REL).glob("slow-*.json"))
    matching = [path for path in kept
                if (json.loads(path.read_text(encoding="utf-8")).get("lock") or {}).get("taken_at")
                == (result.get("lock") or {}).get("taken_at")]
    assert matching, f"the slow rebuild's record was not kept as slow-<UTC start>.json: {[p.name for p in kept]}"
    kept_record = json.loads(matching[0].read_text(encoding="utf-8"))
    assert kept_record.get("slow") is True, "the kept slow record does not say slow"
    final, final_text = support.read_record(project)
    assert final is not None and final.get("slow") is True and final.get("timing") == timing, \
        "the final record does not hold the slow rebuild's stage times"
    for text in [final_text, matching[0].read_text(encoding="utf-8")] + [t for _, t in live]:
        found = support.LONG_HEX.search(text)
        assert not found, f"a record holds an uncut run of 13 or more hex digits: {found.group(0)}"


def test_a_watchdog_fault_is_reported_and_the_rebuild_still_succeeds(box, lock, env):
    """``.gov-runtime/rebuild`` is a file, so no record can be written: the fault is reported on standard error and
    in ``watchdog_faults``, and the rebuild succeeds with the stores and digest of a fault-free rebuild."""
    project = support.make_project(box, "project", lock)
    blocker = Path(project) / support.RECORD_DIR_REL
    blocker.parent.mkdir(parents=True, exist_ok=True)
    blocker.write_text("not a folder\n", encoding="utf-8")

    run = support.rebuild(project, env, "--no-embeddings")

    assert run.returncode == 0 and run.envelope().get("ok") is True, \
        f"a watchdog fault changed the rebuild's success\n{run.describe()}"
    faults = run.result.get("watchdog_faults")
    assert isinstance(faults, list) and faults, f"the fault is not in watchdog_faults\n{run.describe()}"
    lines = [line for line in run.stderr.splitlines() if "watchdog" in line or support.RECORD_DIR_REL in line]
    assert lines, f"the fault is not reported on standard error\nstderr:\n{run.stderr[-2000:]}"

    blocker.unlink()
    clean = support.rebuild(project, env, "--no-embeddings")
    assert clean.returncode == 0, clean.describe()
    assert run.result.get("digest") == clean.result.get("digest") and run.result.get("stores") == \
        clean.result.get("stores"), "the rebuild with a watchdog fault built different stores"


def test_a_watchdog_fault_in_a_slow_rebuild_never_stops_it(box, lock):
    """The same fault while the rebuild runs past its threshold: it still goes on to a successful end, slow."""
    project = support.make_project(box, "project", lock, slow_after_s=THRESHOLD_S)
    blocker = Path(project) / support.RECORD_DIR_REL
    blocker.parent.mkdir(parents=True, exist_ok=True)
    blocker.write_text("not a folder\n", encoding="utf-8")
    env = support.environment(box, support.slow_gitleaks(box, "slow-tools", THRESHOLD_S * 2 + 1))

    run = support.rebuild(project, env, "--no-embeddings")

    assert run.returncode == 0 and run.envelope().get("ok") is True, \
        f"a watchdog fault stopped or failed a slow rebuild\n{run.describe()}"
    assert run.result.get("slow") is True, f"the slow rebuild was not flagged slow\n{run.describe()}"
    assert run.result.get("watchdog_faults"), f"the fault is not in watchdog_faults\n{run.describe()}"
    assert (run.result.get("stores") or {}).get("lexical", {}).get("status") == "recreated", run.describe()
