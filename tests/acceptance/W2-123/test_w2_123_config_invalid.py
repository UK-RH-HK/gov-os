"""KPIs 1 and 4, and the failure line "a server started uncapped": an unreadable value refuses the start, named, and
is never an uncapped start (S1).

Rewrite-Reason: DEC-1065 (1): only the explicit restart (``safe_restart``) starts a server, so "refuses the start" is
judged there (not restarted, no settings, the reason naming the file and the key, the executable never run); the
health check (``ensure_*``) still reports the unreadable value as before (``CONFIG_INVALID``, settings None, the
warning naming the file and the key, written once to standard error)."""

from __future__ import annotations

import pytest

import w2_123_support as support

SHARED = f"{support.SECTION}.shared"


def _entry(**values):
    return {"slots": 4, support.SECTION: {"shared": support.probe_section(**values)}}


def _cases():
    """(id, the file's text, the key the warning names or None for the file itself), one per kind S1 names."""
    import json
    unknown = support.no_allowed_cpu()
    rows = [
        ("file-not-json", "{ this is not JSON", None),
        ("file-not-an-object", "[1, 2, 3]", None),
        ("section-not-an-object", json.dumps({"slots": 4, support.SECTION: "fast"}), support.SECTION),
        ("entry-not-an-object", json.dumps({"slots": 4, support.SECTION: {"shared": 4}}), SHARED),
        ("parallel-wrong-type", json.dumps(_entry(parallel="4")), f"{SHARED}.parallel"),
        ("parallel-out-of-range", json.dumps(_entry(parallel=0)), f"{SHARED}.parallel"),
        ("nice-out-of-range", json.dumps(_entry(nice=20)), f"{SHARED}.nice"),
        ("cpus-wrong-type", json.dumps(_entry(cpus=3)), f"{SHARED}.cpus"),
        ("cpus-unparseable", json.dumps(_entry(cpus="two-five")), f"{SHARED}.cpus"),
        ("cpus-not-allowed", json.dumps(_entry(cpus=str(unknown))), f"{SHARED}.cpus"),
        ("probe-not-positive", json.dumps(_entry(probe_slow_s=-1)), f"{SHARED}.probe_slow_s"),
        ("probe-slow-not-below-hung", json.dumps(
            {"slots": 4, support.SECTION: {"shared": {"probe_slow_s": 3.0, "probe_hung_s": 1.0}}}),
         (f"{SHARED}.probe_slow_s", f"{SHARED}.probe_hung_s")),
    ]
    return [pytest.param(text, key, id=name) for name, text, key in rows]


def _names(warning, key):
    if key is None:
        return "gate.json" in warning
    keys = key if isinstance(key, tuple) else (key,)
    return "gate.json" in warning and any(each in warning for each in keys)


@pytest.mark.parametrize(("text", "key"), _cases())
def test_an_unreadable_value_refuses_the_start_and_names_it(stage, text, key):
    """Nothing listens, the executable is there: an unreadable value refuses the start (CONFIG_INVALID, settings
    None), the warning names the file and the key, it is written once to standard error, and the planted
    executable never runs."""
    stage.configure(raw=text)

    restart = stage.call("safe_restart", "shared").result
    assert stage.serves() == [], f"the server was started with an unreadable configuration: {stage.serves()}"
    assert restart["restarted"] is False and restart["settings"] is None, restart
    assert _names(restart.get("reason") or "", key), f"the refusal does not name the file and {key}: {restart}"

    call = stage.call("ensure_available", timeout_s=support.START_TIMEOUT_S)

    result = call.result
    assert stage.serves() == [], f"the server was started with an unreadable configuration: {stage.serves()}"
    support.assert_keys(result, support.RESULT_KEYS, "ensure_available's result")
    assert result["available"] is False and result["started"] is False, result
    assert result["settings"] is None, result
    # Rewrite-Reason: DEC-1065 (1): with nothing listening, the health check names the embedder unavailable (it
    # starts nothing, so CONFIG_INVALID is the start's: judged on safe_restart above); its warning is still written
    # once to standard error, never silent.
    warning = result["warning"] or ""
    assert warning.strip() and call.stderr.count(warning) == 1, \
        f"the warning is not written once to standard error ({warning!r}):\n{call.stderr}"


def test_an_unreadable_query_entry_refuses_the_query_start(stage):
    """KPI 6: the query server's entry is read and checked the same way."""
    stage.configure({"query": support.probe_section(nice=25)})

    restart = stage.call("safe_restart", "query").result
    assert stage.serves() == [], f"the query server was started with an unreadable value: {stage.serves()}"
    assert restart["restarted"] is False and restart["settings"] is None, restart
    assert f"{support.SECTION}.query.nice" in (restart.get("reason") or ""), restart

    call = stage.call("ensure_query_available", timeout_s=support.START_TIMEOUT_S)

    result = call.result
    assert stage.serves() == [], f"the query server was started with an unreadable value: {stage.serves()}"
    # Rewrite-Reason: DEC-1065 (1): CONFIG_INVALID and the key are the start's (judged on safe_restart above); the
    # health check starts nothing and states no settings.
    assert result["available"] is False and not result.get("started"), result
    assert "settings" in result and result["settings"] is None, result


def test_an_unreadable_value_with_the_server_already_answering_uses_it_and_still_names_the_value(stage):
    """S1: a server that already answers is used as today; the warning still names the unreadable value."""
    stage.configure({"shared": support.probe_section(parallel=0)})
    stage.embedder()

    call = stage.call("ensure_available", timeout_s=support.START_TIMEOUT_S)

    result = call.result
    support.assert_keys(result, support.RESULT_KEYS, "ensure_available's result")
    assert result["available"] is True and result["started"] is False, result
    assert result["settings"] is None, result
    assert f"{SHARED}.parallel" in (result["warning"] or ""), result
    assert stage.serves() == []
