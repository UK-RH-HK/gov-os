"""Part 2, KPI 6 and failure line 2: every case a scoped close leaves out by deselection is named.

When a target finer than a file runs (a node id or its beginning), the other cases of that file are left out by
``--deselect``. Each case so left out is named in ``left_out`` by its node id, with why (README, "Interface",
item 6). The fixture's every-close target is one case of a file that holds two. From the FULL review of
9174e358. README, "Part 2".
"""

import w2_66_support as support

EC_RUN = f"{support.EC_CONTRACT}::test_ec_contract"
EC_DESELECTED = f"{support.EC_CONTRACT}::test_ec_contract_second"


def _map():
    return {**support.DEFAULT_TEST_MAP, "every_close": [EC_RUN]}


def test_a_case_left_out_by_deselection_is_named_with_why(make_fixture, sandbox):
    fixture = make_fixture(test_map=_map())
    fixture.based({support.EC_CONTRACT: support._telling("test_ec_contract", fixture.told)
                   + "\n\n" + support._telling("test_ec_contract_second", fixture.told)},
                  "W1-ec's contract file gains a second case, green at the base")
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.evidence_of(run)
    assert evidence.get("scope") == support.SCOPED, f"a one-module change is not a scoped run: {evidence}"
    assert fixture.ran("test_ec_contract"), f"the every-close case {EC_RUN} did not run"
    assert support.EVERY_CLOSE in {w["reason"] for w in support.selected_for(evidence, EC_RUN)}, \
        f"the every-close case is not named with {support.EVERY_CLOSE}: {evidence.get('selected')}"
    assert not fixture.ran("test_ec_contract_second"), f"{EC_DESELECTED} ran, though only {EC_RUN} is selected"
    # An entry that names the deselected case and not the case that ran: the case's node id (or a beginning of it).
    named = [entry for entry in evidence.get("left_out") or [] if isinstance(entry, dict)
             and support.covers(str(entry.get("target", "")), EC_DESELECTED)
             and not support.covers(str(entry.get("target", "")), EC_RUN)]
    assert named, \
        f"{EC_DESELECTED}, left out by deselection, is not named in left_out: {evidence.get('left_out')}"
    assert support.NOT_REACHED in {w["reason"] for entry in named for w in support.reasons(entry)}, \
        f"the deselected case is named without the reason {support.NOT_REACHED}: {named}"
    assert "test_ec_contract_second" not in support.junit_cases(fixture.root, evidence), \
        "the JUnit XML holds the deselected case"
