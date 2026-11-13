"""KPI 5: the health probe embeds one fixed text and states healthy, slow, hung or down; it never starts, stops or
restarts anything (S3). Called in the pytest process."""

from __future__ import annotations

import time

import pytest

import w2_123_support as support


def _probe(ollama, stage, server):
    began = time.monotonic()
    result = ollama.probe(server, env=stage.environment())
    elapsed = time.monotonic() - began
    assert isinstance(result, dict), f"probe returned {result!r}, not an object"
    support.assert_keys(result, support.PROBE_KEYS, "the probe's result")
    return result, elapsed


@pytest.mark.parametrize(("behaviour", "state"), [
    pytest.param({}, "healthy", id="healthy"),
    pytest.param({"delay": support.SLOW_DELAY_S}, "slow", id="slow"),
    pytest.param({"never": True}, "hung", id="hung-no-answer"),
    pytest.param({"no_vector": True}, "hung", id="hung-no-vector"),
])
def test_the_probe_states_the_servers_health_from_one_embedding(ollama, stage, behaviour, state):
    """A vector within probe_slow_s is healthy; after it but within probe_hung_s slow; none in time, or an answer
    without a vector, hung. The probe sends the semantic store's model to /api/embed and returns within
    probe_hung_s (with slack)."""
    stage.configure({"shared": support.probe_section()})
    endpoint = stage.embedder(**behaviour)

    result, elapsed = _probe(ollama, stage, "shared")

    assert result["state"] == state, f"the probe stated {result['state']!r}, not {state!r}: {result}"
    assert result["server"] == "shared" and stage.host in str(result["host"]), result
    sent = endpoint.embed_requests()
    assert len(sent) == 1, f"the probe sent {len(sent)} embedding requests, not one"
    assert sent[0]["route"] == "/api/embed" and sent[0]["body"].get("model") == support.MODEL, sent[0]
    assert elapsed < support.PROBE_HUNG_S + 3.0, f"the probe took {elapsed:.1f} s"
    if state == "healthy":
        assert isinstance(result["seconds"], (int, float)) and result["seconds"] < support.PROBE_SLOW_S, result
    if state == "slow":
        assert isinstance(result["seconds"], (int, float)), result
        assert support.PROBE_SLOW_S <= result["seconds"] < support.PROBE_HUNG_S, result


def test_the_probe_states_down_and_starts_nothing(ollama, stage):
    """Nothing listens: down, and the planted executable never runs (a probe starts nothing)."""
    stage.configure({"shared": support.probe_section()})

    result, _ = _probe(ollama, stage, "shared")

    assert result["state"] == "down", result
    assert result["seconds"] is None, result
    time.sleep(0.5)
    assert stage.serves() == [], f"the probe started a server: {stage.serves()}"


def test_the_probe_of_the_query_server_asks_the_query_address(ollama, stage):
    """``probe("query")`` asks GOV_QUERY_OLLAMA_HOST, not OLLAMA_HOST (down here)."""
    stage.configure({"query": support.probe_section()})
    endpoint = stage.embedder(query=True)

    result, _ = _probe(ollama, stage, "query")

    assert result["state"] == "healthy" and result["server"] == "query", result
    assert stage.query_host in str(result["host"]), result
    assert len(endpoint.embed_requests()) == 1


def test_the_probe_with_an_unreadable_value_sends_nothing(ollama, stage):
    """An unreadable configuration value: CONFIG_INVALID naming it, and nothing is sent."""
    stage.configure({"shared": support.probe_section(probe_hung_s="soon")})
    endpoint = stage.embedder()

    result, _ = _probe(ollama, stage, "shared")

    assert result["state"] == support.CONFIG_INVALID, result
    assert f"{support.SECTION}.shared.probe_hung_s" in str(result), result
    assert endpoint.embed_requests() == [], "the probe sent a request with an unreadable configuration"
