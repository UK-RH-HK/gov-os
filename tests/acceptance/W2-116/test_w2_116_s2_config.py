"""W2-116 S2 (pass 2b), the failure line: a missing or invalid refresh time, a missing branch, no ``integration_refresh``
at all, or an invalid ``GOV_NOW`` refuses ``REBUILD_CONFIG_INVALID`` naming the key (``details.key`` and the message),
with nothing built and no record written; a failed refresh leaves the record so the next tick is due again; a plain
``gov rebuild --integration`` never reads the times nor writes the record; ``--when-due`` is only valid with
``--integration`` (README, "Pass 2b")."""

from __future__ import annotations

import pytest

import w2_116_s2_support as s2
import w2_116_support as support
from w2_116_s2_support import DAY1, MISSING, at

NOW = at(DAY1, "12:00")

# (case id, planted configuration, the key named, the value read: MISSING when the key is not there)
REFUSED = [
    ("second-missing", {"second": MISSING}, "integration_refresh.second", MISSING),
    ("second-empty", {"second": ""}, "integration_refresh.second", ""),
    ("second-not-a-string", {"second": 1800}, "integration_refresh.second", 1800),
    ("second-9-5", {"second": "9:5"}, "integration_refresh.second", "9:5"),
    ("second-10am", {"second": "10am"}, "integration_refresh.second", "10am"),
    ("second-25-00", {"second": "25:00"}, "integration_refresh.second", "25:00"),
    ("second-24-00", {"second": "24:00"}, "integration_refresh.second", "24:00"),
    ("second-12-60", {"second": "12:60"}, "integration_refresh.second", "12:60"),
    ("latest-missing", {"latest": MISSING}, "integration_refresh.after_nightly.latest", MISSING),
    ("latest-25-00", {"latest": "25:00"}, "integration_refresh.after_nightly.latest", "25:00"),
    ("latest-10am", {"latest": "10am"}, "integration_refresh.after_nightly.latest", "10am"),
    ("latest-not-a-string", {"latest": 1000}, "integration_refresh.after_nightly.latest", 1000),
    ("branch-missing", {"branch": MISSING}, "integration_refresh.branch", MISSING),
    ("no-integration-refresh", {"refresh": False}, "integration_refresh", MISSING),
]


@pytest.mark.parametrize("planted,key,value", [pytest.param(p, k, v, id=i) for i, p, k, v in REFUSED])
def test_s2_failure_a_missing_or_invalid_setting_refuses_by_name_and_builds_nothing(box, env, project, planted, key,
                                                                                    value):
    s2.plant_config(box, project, **planted)
    run = s2.when_due(project, env, NOW)
    error = run.envelope().get("error") or {}
    assert run.returncode != 0 and run.envelope().get("ok") is False and error.get("code") == "REBUILD_CONFIG_INVALID", (
        f"expected REBUILD_CONFIG_INVALID\n{run.describe()}")
    details = error.get("details") or {}
    assert details.get("key") == key, f"details.key is {details.get('key')!r}, not {key!r}: {error}"
    assert key in error.get("message", ""), f"the message does not name {key}: {error.get('message')!r}"
    if value is MISSING:
        assert details.get("value") is None, f"details.value of a missing key is {details.get('value')!r}, not null"
    else:
        assert details.get("value") == value, f"details.value is {details.get('value')!r}, not {value!r}"
    s2.assert_nothing_built(project, box, "a refused tick")


def test_s2_failure_an_invalid_now_refuses_by_name_and_builds_nothing(box, env, project):
    s2.plant_config(box, project)
    run = support.gov(project, {**env, "GOV_NOW": "yesterday-ish"}, "rebuild", "--json", support.INTEGRATION,
                      support.BRANCH, "--when-due")
    error = run.envelope().get("error") or {}
    assert error.get("code") == "REBUILD_CONFIG_INVALID" and run.returncode != 0, (
        f"an invalid GOV_NOW was not refused REBUILD_CONFIG_INVALID\n{run.describe()}")
    assert (error.get("details") or {}).get("key") == "GOV_NOW", f"details.key is not GOV_NOW: {error}"
    assert "GOV_NOW" in error.get("message", ""), f"the message does not name GOV_NOW: {error.get('message')!r}"
    s2.assert_nothing_built(project, box, "a tick with an invalid clock")


def test_s2_failure_the_times_are_not_read_without_when_due_and_no_record_is_written(box, env, project):
    # an invalid time stays unread by a plain refresh (the one a hook runs after a merge): it builds, and writes no record
    s2.plant_config(box, project, second="25:00")
    run = support.integration_build(project, env)
    assert run.ok, f"a plain refresh was refused for a time it never reads\n{run.describe()}"
    assert run.result["integration"]["status"] == "switched", run.describe()
    assert not s2.record_path(box).exists(), f"a plain refresh wrote {s2.record_path(box)}"


def test_s2_failure_a_plain_refresh_leaves_the_record_as_it_was(box, env, project):
    s2.plant_config(box, project)
    s2.first_refresh(box, env, project, at(DAY1, "10:05"))
    kept = s2.record_bytes(box)
    support.land_h2(project)
    run = support.integration_build(project, env)      # no --when-due: the refresh after a merge
    assert run.ok and run.result["integration"]["status"] == "switched", run.describe()
    assert s2.record_bytes(box) == kept, "a plain refresh after a merge rewrote the scheduled refresh's record"


def test_s2_failure_when_due_is_only_valid_with_integration(box, env, project):
    s2.plant_config(box, project)
    run = support.gov(project, env, "rebuild", "--json", "--when-due")
    assert run.returncode != 0, f"--when-due without --integration was accepted\n{run.describe()}"
    error = run.envelope().get("error") or {}
    assert error.get("code") == "REBUILD_FAILED", f"the refusal is not the REBUILD_FAILED usage refusal\n{run.describe()}"
    s2.assert_nothing_built(project, box, "--when-due without --integration")


def test_s2_failure_a_failed_refresh_refuses_and_leaves_the_record_so_the_next_tick_is_due_again(
        box, env, questions, project):
    s2.plant_config(box, project)
    s2.first_refresh(box, env, project, at(DAY1, "10:05"))
    kept = s2.record_bytes(box)
    ready = support.assert_link(box)
    h2 = support.land_h2(project)
    # second is due, but the build has no model: the refresh fails and the record is not written
    model_less = {**env, "OLLAMA_HOST": support.closed_host()}
    failed = s2.when_due(project, model_less, at(DAY1, "18:05"))
    error = failed.envelope().get("error") or {}
    assert failed.returncode != 0 and error.get("code") == "REBUILD_FAILED", (
        f"a failed scheduled refresh did not refuse REBUILD_FAILED\n{failed.describe()}")
    assert s2.record_bytes(box) == kept, "a failed refresh changed the record"
    assert support.target(box) == ready, "a failed refresh moved the link"
    # the next tick, the model back: due again with the same reason, and it succeeds
    again = s2.when_due(project, env, at(DAY1, "18:06"))
    s2.assert_due(again, "second", "the tick after a failed refresh")
    s2.assert_record(box, at(DAY1, "18:06"), "second", h2, "switched", "the refresh that followed the failed one")
