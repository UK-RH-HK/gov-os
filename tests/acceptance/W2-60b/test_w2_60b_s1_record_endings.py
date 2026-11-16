"""W2-60b, KPI success-1 and failure-3 -- one record per launched session, whatever its exit.

success-1 [CAP-36.a lite, DEC-838 item 3, lens F R6]: "When a launched session ends, whatever its exit (DEC-392's
signals included), the launcher writes one record keyed by its session id: model (the main session's and each
subagent's), effort, window, tokens (input, output, cache creation, cache read), cost, minutes, turns, subagents (count
and model) and every rate-limit event; role, ticket and task class come from W2-60a's launch record." Verify: planted
launches that end by exit 0, by a non-zero exit and by DEC-392's signal: each leaves one record keyed by its session id
holding every listed key (a planted rate-limit event included), with role, ticket and task class taken from W2-60a's
launch record.

failure-3: "A changed exit code; a session that started with no record." Verify: after each planted launch (one ended
early included) a record exists for its session id.

Interface (at claim, DEC-1157; the lead's key names): ``.gov-runtime/sessions/<session id>.json`` in the main checkout;
written whole at the start (``ended_at`` null) and replaced whole after the end, with ``exit_code`` the launcher's;
``pid`` is the ``gov launch`` process's id; ``rate_limit_events`` is a list of ``{"at": <the line's timestamp>}``, one
per ``api_error`` line with ``error.status`` 429; ``subagents`` is ``{"count", "models"}``.
"""

from __future__ import annotations

import json
import os
import signal

import w2_60b_support as t

b = t.b
ENG, TD = t.ENGINEER, t.TEST_DESIGNER
T = b.T                        # W2-60a's engineer ticket, class implementation
SUBS = (("a1b2c3", t.HAIKU5), ("d4e5f6", t.SONNET))


def _sid(result):
    assert len(result.calls) == 1, f"gov launch did not start exactly one session\n{result.describe()}"
    return result.calls[0]["session_id"]


def _line(result, name):
    found = b.option_values(result.calls[0]["args"], name)
    assert len(found) == 1, f"the session's line carries {name} {len(found)} times: {result.calls[0]['args']}"
    return found[0]


def _one_record(project, sid):
    files = t.record_files(project)
    assert files == [f"{sid}.json"], (
        f"the session folder {t.sessions(project)} does not hold exactly the one record {sid}.json: {files}")
    return t.session_record(project, sid)


def _ended_by_exit(cli, launch, project, exit_code):
    log = t.rich_log(subagents=SUBS)
    t.set_plan(cli, log=log, exit_code=exit_code)
    result = launch(ENG, T.tk)
    assert result.run.returncode == exit_code, (
        f"gov launch did not end with the session's exit code {exit_code}\n{result.describe()}")
    sid = _sid(result)
    record = _one_record(project, sid)
    t.assert_form(record)
    t.assert_ended(record, sid, project, exit_code)
    t.assert_from_launch_record(record, t.launch_record(project, sid))
    events = t.measured(record, "rate_limit_events")
    assert sorted(events, key=str) == sorted(({"at": at} for at in log.rate_limit_stamps), key=str), (
        f"the record's rate-limit events are not the planted log's two 429 lines by their timestamps: {events!r}")
    return record


def test_s1_a_session_that_ends_by_exit_0_leaves_one_record_with_every_key(cli, launch, project):
    _ended_by_exit(cli, launch, project, 0)


def test_s1_a_session_that_ends_by_a_non_zero_exit_leaves_one_record_with_every_key(cli, launch, project):
    _ended_by_exit(cli, launch, project, 3)


def test_s1_a_session_ended_by_sigterm_to_the_launcher_leaves_one_record_with_every_key(box, cli, project):
    ready = box.elsewhere / "ready"
    log = t.rich_log(subagents=SUBS)
    t.set_plan(cli, log=log, ready=ready, sleep=60)
    process = t.start_launch(box, ENG, T.tk)
    try:
        assert t.wait_for(ready.exists, 30), "the planted session did not start"
        sid = t.calls(cli)[-1]["session_id"]
        process.send_signal(signal.SIGTERM)
        code, _, err = t.finish(process, timeout=t.END_WAIT_S + 30)
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
    assert code == t.INTERRUPT_EXIT, f"the launcher ended with {code}, not {t.INTERRUPT_EXIT}: {err[-800:]}"
    record = _one_record(project, sid)
    t.assert_form(record)
    t.assert_ended(record, sid, project, t.INTERRUPT_EXIT)
    t.assert_from_launch_record(record, t.launch_record(project, sid))
    assert len(t.measured(record, "rate_limit_events")) == 2, "the ended-early session's two rate-limit events"


def test_f3_a_session_ended_early_has_its_record_while_it_runs(box, cli, project):
    """The record is there from the session's start, with ``ended_at`` null and the launcher's pid, before the
    ending signal; afterwards it is replaced whole."""
    ready = box.elsewhere / "ready"
    t.set_plan(cli, log=t.rich_log(), ready=ready, sleep=60)
    process = t.start_launch(box, ENG, T.tk)
    try:
        assert t.wait_for(ready.exists, 30), "the planted session did not start"
        sid = t.calls(cli)[-1]["session_id"]
        path = t.sessions(project) / f"{sid}.json"
        assert t.wait_for(path.is_file, 10), (
            f"the session runs, but no record {path.name} is in {t.sessions(project)}: a session that started with "
            f"no record")
        running = t.session_record(project, sid, "while the session runs")
        assert running["ended_at"] is None and running["exit_code"] is None, (
            f"the running session's record does not have ended_at and exit_code null: {running}")
        assert running["pid"] == process.pid, (
            f"the running session's record names pid {running['pid']!r}, not the gov launch process {process.pid}")
        assert running["worktree"] == os.path.realpath(project) and running["session_id"] == sid
        t.copied(running, "role", ENG)
        process.send_signal(signal.SIGTERM)
        code, _, _ = t.finish(process, timeout=t.END_WAIT_S + 30)
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
    assert code == t.INTERRUPT_EXIT
    t.assert_ended(t.session_record(project, sid), sid, project, t.INTERRUPT_EXIT)


def test_f3_a_session_that_ends_by_exit_0_found_its_record_whole_at_its_start(cli, launch, project):
    """The planted CLI waits for ``<sid>.json`` and notes what it held: the start's record, whole."""
    t.set_plan(cli, log=t.rich_log(), watch=(t.sessions(project), 10))
    result = launch(ENG, T.tk)
    assert result.run.returncode == 0, result.describe()
    call, sid = result.calls[0], _sid(result)
    assert call.get("record_seen") is not None, (
        f"the session ran for 10 s and no record {sid}.json appeared in {t.sessions(project)}")
    seen = json.loads(call["record_seen"])
    assert seen["session_id"] == sid and seen["ended_at"] is None and seen["exit_code"] is None, (
        f"the record the running session found is not the start's (ended_at and exit_code null): {seen}")
    assert seen["pid"] == call["ppid"], (
        f"the start's record names pid {seen['pid']!r}, not the gov launch process {call['ppid']} that started the "
        f"session")
    t.assert_from_launch_record(seen, t.launch_record(project, sid))
    t.assert_ended(t.session_record(project, sid), sid, project, 0)


def test_s1_the_main_session_s_model_and_each_subagent_s_model_are_recorded(cli, launch, project):
    t.set_plan(cli, log=t.rich_log(subagents=SUBS))
    result = launch(ENG, T.tk)
    assert result.run.returncode == 0, result.describe()
    record = _one_record(project, _sid(result))
    assert t.measured(record, "model") == _line(result, "--model"), "the main session's model is not the log's"
    subagents = t.measured(record, "subagents")
    assert isinstance(subagents, dict) and subagents.get("count") == 2, (
        f"the record's subagents do not count the two planted sub-agents: {subagents!r}")
    assert sorted(subagents.get("models") or []) == sorted(m for _, m in SUBS), (
        f"the record's subagent models are not one per planted sub-agent ({[m for _, m in SUBS]}): {subagents!r}")


def test_s1_every_rate_limit_event_is_recorded_by_its_timestamp_and_nothing_else(cli, launch, project):
    log = t.rich_log()
    t.set_plan(cli, log=log)
    result = launch(ENG, T.tk)
    assert result.run.returncode == 0, result.describe()
    events = t.measured(_one_record(project, _sid(result)), "rate_limit_events")
    assert isinstance(events, list) and len(events) == 2, (
        f"the planted log holds two rate-limit events (status 429) and one other API error (503): {events!r}")
    assert sorted(events, key=str) == sorted(({"at": at} for at in log.rate_limit_stamps), key=str), (
        f"each event is not {{'at': <its line's timestamp>}} and nothing else: {events!r}")


def test_s1_role_ticket_and_task_class_are_the_launch_record_s(cli, launch, project):
    """A test designer on an engineer's ticket: the role is the launch's, not the ticket's; a ticket with no class
    gives a task class that is null."""
    t.set_plan(cli, log=t.rich_log())
    designer = launch(TD, T.tk)
    assert designer.run.returncode == 0, designer.describe()
    sid = _sid(designer)
    record = t.session_record(project, sid)
    t.assert_from_launch_record(record, t.launch_record(project, sid))
    t.copied(record, "role", TD)
    t.copied(record, "ticket", T.tk)
    t.copied(record, "task_class", "implementation")
    unclassed = launch(ENG, b.NO_CLASS.tk)
    assert unclassed.run.returncode == 0, unclassed.describe()
    t.copied(t.session_record(project, _sid(unclassed)), "task_class", None)


def test_s1_a_launch_from_a_linked_worktree_leaves_its_record_in_the_main_checkout(box, cli, launch, project):
    tree = t.add_tree(box, "W2-zz60")
    t.set_plan(cli, log=t.rich_log())
    result = launch(ENG, T.tk, cwd=tree)
    assert result.run.returncode == 0, result.describe()
    sid = _sid(result)
    record = _one_record(project, sid)
    t.assert_ended(record, sid, tree, 0)
    assert not (tree / t.SESSIONS_REL).exists() or not any((tree / t.SESSIONS_REL).iterdir()), (
        "the worktree's own .gov-runtime/sessions holds a record: the records lie in the main checkout")
