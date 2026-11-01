"""KPIs 5 and 6: the safe restart stops only a hung server the Gov OS would start, never one that answers and never
another program; it starts the server again under its cap and records it (S4). Called in a child process."""

from __future__ import annotations

import pytest

import w2_123_support as support
from w2_123_support import assert_capped, assert_settings


def _configure(stage, query=False):
    """Both entries configured, each with its own cap; returns (cpus, nice, parallel, the file) of the one asked."""
    lower, upper = support.lower_cpus(), support.upper_cpus()
    gate = stage.configure({
        "shared": support.probe_section(parallel=3, cpus=support.cpu_list(lower), nice=support.a_nice(5)),
        "query": support.probe_section(parallel=2, cpus=support.cpu_list(upper), nice=support.a_nice(3)),
    })
    return (upper, support.a_nice(3), 2, gate) if query else (lower, support.a_nice(5), 3, gate)


def _restart(stage, server):
    call = stage.call("safe_restart", server)
    support.assert_keys(call.result, support.RESTART_KEYS, "safe_restart's result")
    return call.result


@pytest.mark.parametrize("mode", ["healthy", "slow"])
def test_a_server_that_answers_is_never_restarted(stage, mode):
    """Answering (healthy or slow): nothing is stopped or started, the reason says it answers, nothing recorded."""
    _configure(stage)
    running = stage.start_server(mode)

    result = _restart(stage, "shared")

    assert result["restarted"] is False, result
    assert "answer" in str(result["reason"]).lower(), f"the reason does not say the server answers: {result}"
    assert isinstance(result["probe"], dict) and result["probe"].get("state") == mode, result
    assert running.poll() is None, "a server that answered was stopped"
    assert [entry["pid"] for entry in stage.serves()] == [running.pid], "a server was started beside one answering"
    assert stage.restarts() == [], f"a call that found the server answering recorded {stage.restarts()}"


def test_a_hung_server_of_the_gov_os_is_stopped_with_its_runner_and_started_again_under_its_cap(stage):
    """Hung, held by ``<executable> serve``: it and the process it started are stopped, the server is started again
    under its configured cap and parallel requests, the result names both pids, one line is recorded."""
    cpus, nice, parallel, gate = _configure(stage)
    hung = stage.start_server("hung")
    old_runner = stage.runner_of(hung.pid)

    result = _restart(stage, "shared")

    assert result["restarted"] is True, result
    assert result["probe"].get("state") == "hung", result
    assert result["old_pid"] == hung.pid, f"old_pid is {result['old_pid']}, the hung server was {hung.pid}"
    assert isinstance(result["new_pid"], int) and result["new_pid"] != hung.pid, result
    hung.wait(timeout=support.WAIT_S)
    stage.wait_for(lambda: support.gone(old_runner["pid"]),
                   f"the hung server's runner {old_runner['pid']} was left running")
    assert_settings(result["settings"], parallel=parallel, cpus=cpus, nice=nice, source=gate)
    daemon = stage.serve_of(result["new_pid"])
    assert daemon["mode"] == "healthy" and daemon["host"] == stage.host, daemon
    assert_capped(daemon, cpus=cpus, nice=nice, parallel=parallel, what="the restarted shared server")
    assert_capped(stage.runner_of(daemon["pid"]), cpus=cpus, nice=nice, parallel=parallel,
                  what="the process the restarted shared server started")
    lines = stage.restarts()
    assert len(lines) == 1, f"one restart line was expected in {stage.restarts_path}: {lines}"
    support.assert_keys(lines[0], support.RECORD_KEYS, "the restart record's line")
    assert lines[0]["server"] == "shared" and lines[0]["probe_state"] == "hung", lines[0]
    assert lines[0]["old_pid"] == hung.pid and lines[0]["new_pid"] == result["new_pid"], lines[0]
    assert lines[0]["restarted"] is True and lines[0]["settings"]["parallel"] == parallel, lines[0]


def test_a_port_held_by_another_program_is_never_stopped(stage):
    """Hung, but the port is held by a program that is not ``<executable> serve``: nothing is stopped or started,
    and the reason names the process that holds it."""
    _configure(stage)
    foreign = stage.start_foreign()

    result = _restart(stage, "shared")

    assert result["restarted"] is False, result
    assert foreign.poll() is None, "a process that is not the Gov OS's server was stopped"
    reason = str(result["reason"])
    assert str(foreign.pid) in reason or "python" in reason.lower(), \
        f"the reason does not name the process {foreign.pid} that holds the port: {reason!r}"
    assert stage.serves() == [], f"a server was started on a port another program holds: {stage.serves()}"


def test_a_down_server_is_started_under_its_cap_and_recorded(stage):
    """Down: started as S2 starts it; restarted, the reason names down, old_pid None, one line recorded."""
    cpus, nice, parallel, gate = _configure(stage)

    result = _restart(stage, "shared")

    assert result["restarted"] is True, result
    assert "down" in str(result["reason"]).lower(), result
    assert result["old_pid"] is None and isinstance(result["new_pid"], int), result
    assert_settings(result["settings"], parallel=parallel, cpus=cpus, nice=nice, source=gate)
    assert_capped(stage.serve_of(result["new_pid"]), cpus=cpus, nice=nice, parallel=parallel,
                  what="the shared server the safe restart started")
    lines = stage.restarts()
    assert len(lines) == 1 and lines[0]["probe_state"] == "down" and lines[0]["old_pid"] is None, lines


def test_the_query_server_restarts_under_its_own_cap_cpu_only(stage):
    """KPI 6: the safe restart of the query server keeps its cap and its hidden GPU."""
    cpus, nice, parallel, gate = _configure(stage, query=True)

    result = _restart(stage, "query")

    assert result["restarted"] is True and result["server"] == "query", result
    assert_settings(result["settings"], parallel=parallel, cpus=cpus, nice=nice, source=gate)
    daemon = stage.serve_of(result["new_pid"])
    assert daemon["host"] == stage.query_host, daemon
    assert daemon["env"]["CUDA_VISIBLE_DEVICES"] == "-1", f"the restarted query server sees a GPU: {daemon['env']}"
    assert_capped(daemon, cpus=cpus, nice=nice, parallel=parallel, what="the restarted query server")
    lines = stage.restarts()
    assert len(lines) == 1 and lines[0]["server"] == "query", lines


def test_an_unreadable_value_stops_and_starts_nothing(stage):
    """An unreadable value: a hung server is left as it is, nothing is started, the reason names the value."""
    stage.configure({"shared": support.probe_section(cpus="two-five")})
    hung = stage.start_server("hung")

    result = _restart(stage, "shared")

    assert result["restarted"] is False, result
    assert f"{support.SECTION}.shared.cpus" in str(result["reason"]), result
    assert hung.poll() is None, "the server was stopped with an unreadable configuration"
    assert [entry["pid"] for entry in stage.serves()] == [hung.pid], "a server was started"
