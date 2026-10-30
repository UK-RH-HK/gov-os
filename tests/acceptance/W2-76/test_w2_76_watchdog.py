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

The slowed rebuild is the first rebuild of its tree (DEC-956 item 1): the lexical index is incremental by blob, so a
second rebuild of a tree an earlier rebuild indexed hands the lexical stage's files to the secrets filter no more, and
the planted sleep would land in another stage. Its unslowed counterpart is the first rebuild of a twin: the same
files, committed in one commit with fixed dates (so the same commit hash: the digest holds the commits), in a second
box of its own (its own HOME, TMPDIR and tools), rebuilt after the slowed one. Two first rebuilds are compared, so
neither side's digest can come from the other's work; their stores are compared store by store on their status,
since a store's reason may name a folder made from the project's path (the code-graph tool's home). After the
records are judged, the slowed tree is rebuilt once more unslowed and must give the same digest and the same stores,
every field (the same tree at the same path, as before the revision; the record store, which the digest is taken
from, is loaded again in full from git on every rebuild).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import w2_76_support as support

pytestmark = support.needs_tools

THRESHOLD_S = 2
SLEEP_S = 9.0
FIXED_DATE = "2026-10-30T12:00:00+00:00"


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


def _names_slow_stage(record):
    """Whether the record's stage running names the lexical stage or the secrets filter (the planted slow stage)."""
    running = record.get(support.first_key(record, support.RUNNING_KEYS) or "")
    return running is not None and any(name in json.dumps(running) for name in ("lexical", "secrets"))


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


def _projects_alike(boxes, lock, monkeypatch):
    """One project per box, the same files in the same commit (fixed author and committer dates, so one hash)."""
    monkeypatch.setenv("GIT_AUTHOR_DATE", FIXED_DATE)
    monkeypatch.setenv("GIT_COMMITTER_DATE", FIXED_DATE)
    projects = [support.make_project(each, "project", lock, slow_after_s=THRESHOLD_S) for each in boxes]
    heads = {support.git(project, "rev-parse", "HEAD").strip() for project in projects}
    assert len(heads) == 1, f"the twin projects are not the same commit: {sorted(heads)}"
    return projects


def test_a_slow_rebuild_records_what_it_waits_on_and_goes_on(box, lock, monkeypatch):
    twin_box = support.make_box(box.base / "twin")
    project, twin = _projects_alike((box, twin_box), lock, monkeypatch)
    assert not (Path(project) / ".gov-runtime").exists(), "the slowed rebuild is not the first on its tree"
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
    assert not (Path(twin) / ".gov-runtime").exists(), "the twin was rebuilt before its own first rebuild"
    unslowed = support.rebuild(twin, support.environment(twin_box), "--no-embeddings")
    assert unslowed.returncode == 0, f"the unslowed rebuild of the same content failed\n{unslowed.describe()}"
    assert live, f"no record of this rebuild's processes while it ran ({unreadable} reads were not whole JSON)\n" \
                 f"{run.describe()}"
    assert len(writes) >= 2, f"the record was not rewritten while the rebuild ran (times of the writes: {writes})"
    # The planted sleep is in the lexical stage, not the last one: the record is rewritten in the stages after it,
    # so the read judged is the last one taken while the slow stage ran (DEC-956 item 1), and that stage alone must
    # have seen the record rewritten.
    during = [(record, text) for record, text in live if _names_slow_stage(record)]
    stages_seen = sorted({json.dumps(record.get(support.first_key(record, support.RUNNING_KEYS) or ""))
                          for record, _ in live})
    assert during, f"no record read while the planted slow secrets filter ran (stages running seen: {stages_seen})"
    writes_during = {json.dumps(record.get(support.first_key(record, support.WRITTEN_KEYS) or ""))
                     for record, _ in during}
    assert len(writes_during) >= 2, \
        f"the record was not rewritten while the slow stage ran (times of the writes: {writes_during})"
    problems = _check_live_record(*during[-1], background.pid)
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
        "the slow rebuild built a different digest from an unslowed first rebuild of the same content"
    statuses = [{name: (store or {}).get("status") for name, store in (each.get("stores") or {}).items()}
                for each in (result, unslowed.result)]
    assert statuses[0] == statuses[1] and statuses[0], \
        f"the slow rebuild built different stores from an unslowed first rebuild of the same content: {statuses}"

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

    again = support.rebuild(project, support.environment(box), "--no-embeddings")
    assert again.returncode == 0, f"the unslowed rebuild of the same tree failed\n{again.describe()}"
    assert again.result.get("digest") == result.get("digest") and \
        again.result.get("stores") == result.get("stores"), "the slow rebuild built a different digest or stores from an unslowed rebuild of the same tree"


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
