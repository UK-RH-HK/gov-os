"""KPIs 1, 4 and 6: both servers start under their cap and parallel requests, from the gate's file or the defaults,
and state them in the result (S1, S2)."""

from __future__ import annotations

import w2_123_support as support
from w2_123_support import assert_capped, assert_settings


def test_shared_start_uses_the_configured_cap_and_parallel_requests_inherited_by_its_runner(stage):
    """KPIs 1, 4, 6: the shared server's start reads ``embedding_servers.shared``; the started process and the
    process it starts run on the configured CPUs at the configured niceness with the configured
    OLLAMA_NUM_PARALLEL, which wins over an inherited one; the result states the settings and their file."""
    cpus, nice = support.lower_cpus(), support.a_nice()
    gate = stage.configure({"shared": support.probe_section(parallel=3, cpus=support.cpu_list(cpus), nice=nice)})

    call = stage.call("ensure_available", timeout_s=support.START_TIMEOUT_S, env_extra={"OLLAMA_NUM_PARALLEL": "9"})

    result = call.result
    support.assert_keys(result, support.RESULT_KEYS, "ensure_available's result")
    assert result["available"] is True and result["started"] is True and result["state"] == "AVAILABLE", result
    assert_settings(result["settings"], parallel=3, cpus=cpus, nice=nice, source=gate)
    serves = stage.serves()
    assert len(serves) == 1, f"one start was expected, the planted executable ran as serve {len(serves)} times"
    daemon = serves[0]
    assert daemon["cmdline"][1:] == ["serve"], daemon["cmdline"]
    assert daemon["host"] == stage.host, daemon
    assert_capped(daemon, cpus=cpus, nice=nice, parallel=3, what="the started shared server")
    assert_capped(stage.runner_of(daemon["pid"]), cpus=cpus, nice=nice, parallel=3,
                  what="the process the shared server started")


def test_shared_start_without_configuration_uses_the_default_resolved_from_the_callers_cpus(stage):
    """KPIs 1, 4: no file: the measured defaults, the CPU count resolved to the highest-numbered CPUs the calling
    process may run on (here narrowed to the lower half of this machine's), never this machine's CPU numbers; the
    started process runs as the result states."""
    caller = support.lower_cpus()

    call = stage.call("ensure_available", timeout_s=support.START_TIMEOUT_S, affinity=caller)

    result = call.result
    support.assert_keys(result, support.RESULT_KEYS, "ensure_available's result")
    assert result["available"] is True and result["started"] is True, result
    settings = result["settings"]
    assert_settings(settings, source="default")
    applied = support.parse_cpus(settings["cpus"])
    assert applied <= caller, \
        f"the default cap {settings['cpus']} names CPUs the calling process may not run on ({support.cpu_list(caller)})"
    assert applied == set(sorted(caller)[-len(applied):]), \
        f"the default cap {settings['cpus']} is not the highest-numbered {len(applied)} of {support.cpu_list(caller)}"
    daemon = stage.serves()[0]
    assert_capped(daemon, cpus=applied, nice=settings["nice"], parallel=settings["parallel"],
                  what="the shared server started with the defaults")
    assert_capped(stage.runner_of(daemon["pid"]), cpus=applied, nice=settings["nice"],
                  parallel=settings["parallel"], what="the process the default-capped server started")


def test_query_start_uses_its_own_entry_and_keeps_the_gpu_hidden(stage):
    """KPI 6: the query server's start reads ``embedding_servers.query`` (not the shared entry), runs at
    GOV_QUERY_OLLAMA_HOST capped, its runner too, and stays CPU-only even when the environment names a GPU."""
    shared_cpus, query_cpus = support.lower_cpus(), support.upper_cpus()
    shared_nice, query_nice = support.a_nice(5), support.a_nice(3)
    gate = stage.configure({
        "shared": support.probe_section(parallel=3, cpus=support.cpu_list(shared_cpus), nice=shared_nice),
        "query": support.probe_section(parallel=2, cpus=support.cpu_list(query_cpus), nice=query_nice),
    })

    call = stage.call("ensure_query_available", timeout_s=support.START_TIMEOUT_S,
                      env_extra={"CUDA_VISIBLE_DEVICES": "0"})

    result = call.result
    support.assert_keys(result, support.RESULT_KEYS, "ensure_query_available's result")
    assert result["available"] is True and result["started"] is True, result
    assert_settings(result["settings"], parallel=2, cpus=query_cpus, nice=query_nice, source=gate)
    daemon = stage.serves()[0]
    assert daemon["host"] == stage.query_host, f"the query server was started at {daemon['host']}"
    assert daemon["env"]["CUDA_VISIBLE_DEVICES"] == "-1", f"the query server sees GPU {daemon['env']}"
    assert_capped(daemon, cpus=query_cpus, nice=query_nice, parallel=2, what="the started query server")
    runner = stage.runner_of(daemon["pid"])
    assert runner["env"]["CUDA_VISIBLE_DEVICES"] == "-1", f"the query server's runner sees a GPU {runner['env']}"
    assert_capped(runner, cpus=query_cpus, nice=query_nice, parallel=2,
                  what="the process the query server started")


def test_a_server_already_answering_is_used_and_the_settings_a_start_would_use_are_stated(stage):
    """KPI 1 (S2): when the server already answers nothing is started, and ``settings`` states the values a start
    would use."""
    cpus, nice = support.lower_cpus(), support.a_nice()
    gate = stage.configure({"shared": support.probe_section(parallel=4, cpus=support.cpu_list(cpus), nice=nice)})
    stage.embedder()

    call = stage.call("ensure_available", timeout_s=support.START_TIMEOUT_S)

    result = call.result
    support.assert_keys(result, support.RESULT_KEYS, "ensure_available's result")
    assert result["available"] is True and result["started"] is False, result
    assert_settings(result["settings"], parallel=4, cpus=cpus, nice=nice, source=gate)
    assert stage.serves() == [], "a server was started although one already answered"
