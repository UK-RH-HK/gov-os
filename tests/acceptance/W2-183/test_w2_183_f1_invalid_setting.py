"""F1: a setting that is not a positive whole number refuses by name (never a silent default, never a crash).

``budgets.close_context_tokens`` at ``0``, ``-5`` and ``"many"`` (and ``true`` and ``2.5``, edges: a bool is not a whole
number) each make the close's context step raise a ``_Finding`` ``CONTEXT_FAILED`` with ``context_error``
``CONTEXT_SETTING_INVALID``, its message naming the key. The stand-in's ticket fits the default ceiling, so a close that
fell back to 6,000 would build a packet: the refusal is the only right answer. A valid setting of ``1`` is a whole number:
it refuses as an ordinary ``CONTEXT_OVER_CEILING`` at a ceiling of 1.

Red today: the setting is not read, so the close builds a packet at the default.
"""

from __future__ import annotations

import pytest

import w2_183_support as s

INVALID = (0, -5, "many", True, 2.5)
IDS = ("zero", "negative", "string", "bool", "float")


@pytest.mark.parametrize("value", INVALID, ids=IDS)
def test_an_invalid_setting_refuses_the_closes_context_step_by_name(api, small, value):
    with small.setting(value):
        step = api.close_step(small.root, s.SMALL_TICKET)
    error = s.assert_close_refused(step, s.CONTEXT_FAILED, s.SETTING_INVALID)
    assert s.CLOSE_KEY in error["message"], f"the refusal does not name the key {s.CLOSE_KEY}: {error['message']!r}"
    assert s.SMALL_TICKET in error["message"], f"the refusal does not name the ticket: {error['message']!r}"


@pytest.mark.parametrize("value", INVALID, ids=IDS)
def test_close_budget_refuses_an_invalid_setting_naming_the_key_and_the_value(api, small, value):
    with small.setting(value):
        step = api.close_budget(small.root)
    error = step.error
    assert error is not None, f"close_budget gave {step.out.get('value')!r} for the setting {value!r}\n{step.describe()}"
    assert error["type"] == "GovError" and error["code"] == s.SETTING_INVALID, step.describe()
    assert s.CLOSE_KEY in error["message"], f"the refusal does not name the key: {error['message']!r}"
    assert str(value).lower() in error["message"].lower(), f"the refusal does not name the value {value!r}: {error['message']!r}"


def test_a_setting_of_1_is_valid_and_refuses_as_an_ordinary_ceiling(api, small):
    """The smallest whole number: a valid setting, a ceiling of 1, so the 131-token mandatory part is over it."""
    with small.setting(1):
        step = api.close_step(small.root, s.SMALL_TICKET)
    error = s.assert_close_refused(step, s.CONTEXT_FAILED, s.OVER_CEILING)
    assert error["details"].get("limit") == 1, error["details"]


def test_an_invalid_setting_is_refused_whatever_the_ticket(api, big):
    """Not only for a ticket that would fit the default: the big one is refused for its setting, not its size."""
    with big.setting("many"):
        step = api.close_step(big.root, s.BIG_TICKET)
    s.assert_close_refused(step, s.CONTEXT_FAILED, s.SETTING_INVALID)


def test_a_valid_setting_after_an_invalid_one_works(api, small):
    """The refusal leaves nothing behind: the same project with a valid setting builds its packet."""
    with small.setting(-5):
        s.assert_close_refused(api.close_step(small.root, s.SMALL_TICKET), s.CONTEXT_FAILED, s.SETTING_INVALID)
    with small.setting(s.CLOSE_VALUE):
        packet = api.close_step(small.root, s.SMALL_TICKET).packet
    assert packet["budget"]["limit"] == s.CLOSE_VALUE
