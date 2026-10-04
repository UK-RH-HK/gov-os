"""Success 1: "gov starts ollama serve on demand and relies on the 5-min idle unload; no always-on unit".

DEC-260 fixes the entry point and where the executable and the endpoint come from.
DEC-261 fixes the lifecycle: start on demand, never stop, no keep-alive override, no unit.
"""

from __future__ import annotations

import pytest

import w1_18_support as support


def test_a_healthy_endpoint_is_used_and_nothing_is_started(stage):
    stage.install_executable("healthy")
    stage.endpoint_up()

    call = stage.call(timeout_s=support.START_DEADLINE_S)

    assert call.result["available"] is True, call.result
    assert call.result["started"] is False, call.result
    assert stage.serve_runs() == [], "the endpoint was already healthy, but `ollama serve` was started"
    asked = [request for request in stage.requests() if request["path"] == support.HEALTH_PATH]
    assert asked, f"the endpoint of OLLAMA_HOST was never asked {support.HEALTH_PATH}"


@pytest.mark.parametrize("place", support.EXECUTABLE_PLACES)
def test_with_the_endpoint_down_ollama_serve_is_started_on_demand(stage, place):
    stage.install_executable("healthy", place=place)

    call = stage.call(timeout_s=support.START_DEADLINE_S)

    serves = stage.serve_runs()
    assert len(serves) == 1, f"`ollama serve` was started {len(serves)} times (executable found through {place})"
    assert call.result["available"] is True, call.result
    assert call.result["started"] is True, call.result


def test_starting_sets_up_no_unit_and_no_keep_alive_override(stage):
    stage.install_executable("healthy")
    before = stage.files(stage.home)

    call = stage.call(timeout_s=support.START_DEADLINE_S)

    assert call.result["started"] is True, call.result
    assert stage.unit_calls() == [], f"starting the daemon called a unit command: {stage.unit_calls()}"
    assert stage.files(stage.home) == before, "starting the daemon wrote a file under HOME (a user unit lives there)"
    for run in stage.runs():
        assert run["keep_alive_env"] == {}, f"a keep-alive override was set for the daemon: {run['keep_alive_env']}"
        assert not any("keep" in argument.lower() for argument in run["argv"]), run["argv"]
    overriding = [request for request in stage.requests() if "keep_alive" in request["body"]]
    assert not overriding, f"a request overrides the 5-minute idle unload: {overriding}"


def test_the_started_daemon_is_left_running_and_used_again(stage):
    stage.install_executable("healthy")

    first = stage.call(timeout_s=support.START_DEADLINE_S)
    assert first.result["started"] is True, first.result
    assert stage.endpoint_answers(), "the daemon gov started was gone once the call had returned (DEC-261)"

    second = stage.call(timeout_s=support.START_DEADLINE_S)

    assert second.result["available"] is True, second.result
    assert second.result["started"] is False, second.result
    assert len(stage.serve_runs()) == 1, "a second `ollama serve` was started while the first was healthy"
    assert stage.endpoint_answers(), "the daemon was stopped by the second call (DEC-261)"
    stops = [run["argv"] for run in stage.runs() if "stop" in run["argv"]]
    assert not stops, f"gov asked the executable to stop: {stops}"
