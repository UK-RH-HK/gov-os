"""Failure 1: "A query hangs > 30 s waiting for Ollama".

One total deadline covers the probe, the start and the wait for health (DEC-260). Its default is 20 s; the
tests pass a short one. Every call in this suite is also killed, and fails, after 30 s.
"""

from __future__ import annotations

import w1_18_support as support

BOUND_S = support.SHORT_DEADLINE_S + support.DEADLINE_SLACK_S


def test_a_daemon_that_never_becomes_healthy_is_given_up_at_the_deadline(stage):
    stage.install_executable("never")

    call = stage.call(timeout_s=support.SHORT_DEADLINE_S)

    assert call.result["available"] is False, call.result
    assert call.elapsed_s <= BOUND_S, (
        f"the call took {call.elapsed_s:.1f} s with a deadline of {support.SHORT_DEADLINE_S:.0f} s")
    assert call.wall_s < support.HANG_LIMIT_S


def test_an_endpoint_that_accepts_and_never_answers_does_not_hang_the_call(stage):
    stage.endpoint_silent()

    call = stage.call(timeout_s=support.SHORT_DEADLINE_S)

    assert call.result["available"] is False, call.result
    assert call.result["state"] == support.FACET_UNAVAILABLE, call.result
    assert call.warning, "the degraded result carries no warning"
    assert call.elapsed_s <= BOUND_S, (
        f"the call took {call.elapsed_s:.1f} s with a deadline of {support.SHORT_DEADLINE_S:.0f} s")


def test_the_default_deadline_is_20_seconds(stage):
    default = stage.default_deadline()

    assert default == support.DEFAULT_DEADLINE_S, f"the default of timeout_s is {default!r}, not 20 s (DEC-260)"
    assert default < support.HANG_LIMIT_S
