"""S5: the gate opens on load only while min(1-minute load, 15-minute load) < nproc: a short peak does not shut it;
both at or above nproc does [DEC-942 item 2, DEC-942 item 3, DEC-950 item 2].

The load reason's ``reading`` is min(1-minute, 15-minute), its ``threshold`` nproc (README, "The gate").
"""

from __future__ import annotations

import pytest

import w2_20_support as support


@pytest.mark.parametrize("one, fifteen, opens", [
    (30.0, 2.0, True),
    (2.0, 30.0, True),
    (3.99, 50.0, True),
    (4.0, 4.0, False),
    (6.0, 5.0, False),
], ids=["a short peak opens", "a falling load opens", "just below nproc opens", "both at nproc shuts",
        "both above nproc shuts"])
def test_s5_the_load_rule_is_the_lower_of_the_1_and_15_minute_loads_below_nproc(machine, repo, one, fifteen, opens):
    machine.set_readings(nproc=4, load=one, load_15=fifteen)

    reading = machine.read(repo)
    assert reading.get("load_1m") == one and reading.get("load_15m") == fifteen, reading
    reasons = support.reasons_by_condition(reading)
    code, envelope, out, err = machine.check(repo)
    if opens:
        assert support.gate_of(reading)["open"] is True and reasons == {}, reading
        support.opened_of(code, envelope, out, err)
    else:
        assert support.gate_of(reading)["open"] is False, reading
        assert set(reasons) == {"load"}, reasons
        assert (reasons["load"]["reading"], reasons["load"]["threshold"]) == (min(one, fifteen), 4), reasons["load"]
        assert "load" in support.reasons_by_condition(support.refusal_of(code, envelope, out, err))
