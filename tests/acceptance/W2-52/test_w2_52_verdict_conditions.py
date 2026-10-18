"""The adoption verdict (W2-02's type) reads the A7 and A10 records as named conditions [CAP-44.h; DEC-741 I (ii)].

One adoption in the protocol's order: A0 to A6 (the session fixture), A7, A8, A10, each gate with its auditor's
passing record. W2-02's verdict gives a list of conditions, each with ``name``, ``source`` and ``state``
(``met``, ``not met``, ``accepted`` with an owner entry). CAP-44.h: condition (4)'s lite part is the lite A7
gate, condition (6)'s the lite A10 gate, condition (9)'s the derived state rebuilt from git that A10 checks;
ADOPTED_HEALTHY when every lite condition is met. The verdict itself is the auditor's (W2-28, W2-30): the cases
read what the two records give it.
"""

from __future__ import annotations

import pytest

import w2_52_support as gates

support = gates.support


@pytest.fixture(scope="module")
def protocol_order(after_a6, tmp_path_factory, interface, stand_in, vector_site):
    adoption = gates.copy_adoption(after_a6, tmp_path_factory.mktemp("protocol-order"), interface,
                                   endpoint=stand_in.host, site=vector_site)
    gates.write_gate_verdict(adoption, "A7")
    a7 = gates.run_gate(adoption, "A7")
    a8 = adoption.ok("A8")
    gates.write_gate_verdict(adoption, "A10")
    gates.remove_derived_state(adoption.project)
    a10 = gates.run_gate(adoption, "A10")
    return adoption, a7, a8, a10


def test_a8_runs_after_a7(protocol_order):
    """A8 runs after a passing A7 as it runs after A6 (the stages before it keep their behaviour)."""
    adoption, a7, a8, _ = protocol_order
    gates.assert_passed(a7)
    assert a8.front.get("stage") == "A8"


def test_the_a7_and_a10_records_each_give_a_condition_the_verdict_carries(protocol_order, needs_vectors):
    """Success 3 [CAP-44.h]: each record gives at least one condition in W2-02's form; one names A7, one A10;
    no condition of one record is a condition of the other."""
    _, a7, _, a10 = protocol_order
    rel7, front7, _ = gates.assert_passed(a7)
    rel10, front10, _ = gates.assert_passed(a10)
    seven, ten = gates.conditions(front7), gates.conditions(front10)
    assert any("A7" in item["name"] for item in seven), f"{rel7}: no condition names A7: {seven}"
    assert any("A10" in item["name"] for item in ten), f"{rel10}: no condition names A10: {ten}"
    shared = {item["name"] for item in seven} & {item["name"] for item in ten}
    assert not shared, f"the two records give conditions of the same name: {sorted(shared)}"


def test_a_verdict_reading_both_passing_records_can_be_healthy(protocol_order, needs_vectors):
    """Success 3 [CAP-44.h]: with both gates passed, the conditions the two records give are all met, so they
    keep no verdict from ADOPTED_HEALTHY."""
    _, a7, _, a10 = protocol_order
    found = gates.conditions(gates.assert_passed(a7)[1]) + gates.conditions(gates.assert_passed(a10)[1])
    assert gates.lite_verdict(found) == "ADOPTED_HEALTHY", found


def test_the_conditions_say_where_they_come_from(protocol_order, needs_vectors):
    """Success 3 [CAP-44.h; W2-02]: each condition's source is the item it comes from: CAP-44.f (the lite gate)
    or CAP-44.h (the verdict's condition)."""
    _, a7, _, a10 = protocol_order
    for outcome in (a7, a10):
        rel, front, _ = gates.assert_passed(outcome)
        for item in gates.conditions(front):
            assert any(source in item["source"] for source in gates.CONDITION_SOURCES), f"{rel}: {item}"


@pytest.mark.parametrize("states, verdict", [
    (("met", "met"), "ADOPTED_HEALTHY"),
    (("met", "not met"), "NOT_ADOPTED_HEALTHY"),
    (("not met", "met"), "NOT_ADOPTED_HEALTHY"),
    (("met", "accepted"), "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"),
])
def test_the_cases_read_conditions_as_cap_44_h_says(states, verdict):
    """The rule the cases use to say a failing record keeps a verdict from ADOPTED_HEALTHY (CAP-44.h: healthy when
    every lite condition is met; with accepted exceptions when each one not met is accepted by the owner)."""
    found = [{"name": f"lite {gate} gate", "source": "CAP-44.f", "state": state,
              **({"owner_entry": "DEC-999"} if state == "accepted" else {})}
             for gate, state in zip(gates.GATES, states)]
    for item in found:
        gates.assert_condition_form(item, "the case")
    assert gates.lite_verdict(found) == verdict
