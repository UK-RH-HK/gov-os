"""V2: the three verdicts and the owner's exceptions file [CAP-44.h; DEC-741 answer F].

The cases stand the live tools in (``compute``'s seam) to plant the conditions not met; the exceptions file is the
owner's when its last commit carries ``Role: owner`` and no other Role. The command line's exit codes and the re-run
that supersedes are in ``test_w2_210_command.py``; the refusals (a file not the owner's) in ``test_w2_210_owner.py``.
"""

from __future__ import annotations

import w2_210_support as d1

support = d1.support


def _a7_not_met(project):
    d1.set_result(project, "A7", "fail")


def _a7_and_doctor_not_met(project):
    d1.set_result(project, "A7", "fail")
    return d1.healthy_tools(doctor=d1.doctor(exit_code=3, failing_part="canaries"))


def test_a7_not_met_and_no_exceptions_file_gives_not_adopted_healthy(adopted):
    """V2: the repository of V1 with A7 not met and no exceptions file."""
    _a7_not_met(adopted.project)
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert result["verdict"] == "NOT_ADOPTED_HEALTHY"
    assert d1.states(result)[d1.LITE_A7] == "not met"


def test_the_owners_file_naming_that_condition_gives_adopted_with_accepted_exceptions(adopted):
    """V2: the same with the file naming A7's condition and a last commit with ``Role: owner``: the condition is
    ``accepted`` with its ``owner_entry``; every other is as it was."""
    _a7_not_met(adopted.project)
    d1.write_exceptions(adopted.project, d1.accept(d1.LITE_A7), "owner")
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert result["verdict"] == "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
    accepted = d1.condition(result, d1.LITE_A7)
    assert accepted["state"] == "accepted" and accepted["owner_entry"] == d1.OWNER_DECISION, accepted
    others = {n: s for n, s in d1.states(result).items() if n != d1.LITE_A7}
    assert set(others.values()) == {"met"}, others
    assert all("owner_entry" not in item for item in result["conditions"] if item["state"] != "accepted")


def test_each_entry_names_its_own_decision(adopted):
    """V2: ``{condition, decision}``: each accepted condition carries the decision its own entry names."""
    d1.set_result(adopted.project, "A7", "fail")
    d1.set_result(adopted.project, "A10", "fail")
    d1.write_exceptions(adopted.project, [{"condition": d1.LITE_A7, "decision": "DEC-9101"},
                                          {"condition": d1.LITE_A10, "decision": "DEC-9102"}], "owner")
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert result["verdict"] == "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
    assert d1.condition(result, d1.LITE_A7)["owner_entry"] == "DEC-9101"
    assert d1.condition(result, d1.LITE_A10)["owner_entry"] == "DEC-9102"


def test_with_two_conditions_not_met_and_the_file_naming_one_the_verdict_is_not_adopted_healthy(adopted):
    """V2: one accepted, one not: ``otherwise NOT_ADOPTED_HEALTHY``; the one named is ``accepted``, the other
    ``not met``."""
    tools = _a7_and_doctor_not_met(adopted.project)
    d1.write_exceptions(adopted.project, d1.accept(d1.LITE_A7), "owner")
    result = d1.compute(adopted.project, tools=tools)
    assert result["verdict"] == "NOT_ADOPTED_HEALTHY"
    assert d1.states(result)[d1.LITE_A7] == "accepted" and d1.states(result)[d1.DOCTOR] == "not met", \
        d1.states(result)


def test_with_two_conditions_not_met_and_the_file_naming_both_the_verdict_has_accepted_exceptions(adopted):
    tools = _a7_and_doctor_not_met(adopted.project)
    d1.write_exceptions(adopted.project, d1.accept(d1.LITE_A7, d1.DOCTOR), "owner")
    result = d1.compute(adopted.project, tools=tools)
    assert result["verdict"] == "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
    assert {n for n, s in d1.states(result).items() if s == "accepted"} == {d1.LITE_A7, d1.DOCTOR}


def test_with_every_condition_met_and_an_exceptions_file_the_verdict_is_adopted_healthy(adopted):
    """V2: an entry for a condition that is met, or for no condition, is recorded as unused and changes nothing:
    ADOPTED_HEALTHY, every state ``met``, both entries named under ``unused_exceptions``."""
    d1.write_exceptions(adopted.project, d1.accept("A0", "no such condition"), "owner")
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert result["verdict"] == "ADOPTED_HEALTHY"
    assert set(d1.states(result).values()) == {"met"}
    unused = result["unused_exceptions"]
    assert sorted(item["condition"] for item in unused) == ["A0", "no such condition"], unused
    assert all(item["decision"] == d1.OWNER_DECISION for item in unused), unused


def test_an_entry_for_a_met_condition_beside_a_used_one_is_recorded_as_unused(adopted):
    d1.set_result(adopted.project, "A7", "fail")
    d1.write_exceptions(adopted.project, d1.accept(d1.LITE_A7, "A0"), "owner")
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert result["verdict"] == "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
    assert d1.states(result)["A0"] == "met"
    assert [item["condition"] for item in result["unused_exceptions"]] == ["A0"]


def test_no_exceptions_file_leaves_no_unused_entry(adopted):
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert result.get("unused_exceptions", []) == []


def test_the_verdict_agrees_with_the_conditions_it_records_for_every_case_above(adopted):
    """V2: one reading of the conditions gives the verdict: healthy when all are met, with exceptions when each not
    met is accepted, otherwise not healthy."""
    from w2_81_judge import derived_verdict

    for plant, entries in ((None, ()), ("A7", ()), ("A7", d1.accept(d1.LITE_A7))):
        if plant:
            d1.set_result(adopted.project, plant, "fail")
        if entries:
            d1.write_exceptions(adopted.project, entries, "owner")
        result = d1.compute(adopted.project, tools=d1.healthy_tools())
        assert result["verdict"] == derived_verdict(list(d1.states(result).values())), d1.states(result)
