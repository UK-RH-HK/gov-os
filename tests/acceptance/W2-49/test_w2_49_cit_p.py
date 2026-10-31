"""KPI success line 1: the CIT-P (``docs/changes/W2-49-CIT-P.md``).

"The CIT-P names each change, its source (DEC-722) and its impact (W2-02,
W2-16, W2-18, W2-27 to W2-30, exit criteria 6 and 7): CAP-44.h, lite: the
three verdicts and the conditions a lite verdict checks; the A7 and A10 gates
of CAP-44.f, lite, with what each lite gate checks and what stays for Wave 3;
CAP-43.b, lite: the manifest and file hashes."

Edge cases from the sources: what stays in Wave 3 (CAP-02.c, A9, A11, the
qualification certificate, the rest of CAP-43.b; DEC-722, the W2-49 card), and
DEC-105's three costed options for a change to a closed specification (CAP-33.e).
"""

from __future__ import annotations

import re

import pytest

from w2_49_support import CAP_43B_REST, CIT_P, VERDICTS, gate, has, read_doc, together, verdict

W3 = r"(?<![\w-])W3(?![\w-])|\bWave 3\b"


def test_cit_p_exists_and_names_its_source_dec_722():
    """DEC-722 is the owner decision behind every change the CIT-P proposes."""
    cit_p = read_doc(CIT_P)
    assert has(r"DEC-722", cit_p), "the CIT-P does not cite its source, DEC-722"


def test_cit_p_names_cap_44h_lite_with_the_three_verdicts():
    """CAP-44.h, lite: ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS, NOT_ADOPTED_HEALTHY (DEC-722)."""
    cit_p = read_doc(CIT_P)
    assert together(cit_p, r"CAP-44\.h", r"\blite\b"), "no place in the CIT-P names CAP-44.h as lite"
    assert together(cit_p, r"CAP-44\.h", *(verdict(v) for v in VERDICTS)), (
        "no place in the CIT-P names CAP-44.h with its three verdicts "
        "ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS and NOT_ADOPTED_HEALTHY"
    )


def test_cit_p_states_the_conditions_a_lite_verdict_checks():
    """CAP-44.h, lite: the conditions a lite verdict checks."""
    cit_p = read_doc(CIT_P)
    assert together(cit_p, r"CAP-44\.h|verdict", r"condition"), (
        "the CIT-P does not state the conditions a lite CAP-44.h verdict checks"
    )


@pytest.mark.parametrize("name", ["A7", "A10"])
def test_cit_p_names_each_lite_gate_of_cap_44f_with_what_it_checks(name):
    """CAP-44.f, lite: the A7 and A10 gates, with what each lite gate checks."""
    cit_p = read_doc(CIT_P)
    assert has(r"CAP-44\.f", cit_p), "the CIT-P does not name CAP-44.f, the item the A7 and A10 gates come from"
    assert together(cit_p, gate(name), r"\blite\b"), f"the CIT-P does not name the {name} gate as lite"
    assert together(cit_p, gate(name), r"check|verif"), (
        f"the CIT-P does not say what the lite {name} gate checks"
    )


@pytest.mark.parametrize("name", ["A9", "A11"])
def test_cit_p_says_what_of_cap_44f_stays_for_wave_3(name):
    """CAP-44.f: A9 and A11 stay in Wave 3 (the W2-49 card, DEC-722)."""
    cit_p = read_doc(CIT_P)
    assert together(cit_p, gate(name), W3), f"the CIT-P does not say that {name} stays in Wave 3"


def test_cit_p_names_cap_43b_lite_manifest_and_file_hashes():
    """CAP-43.b, lite: the manifest and file hashes (DEC-722)."""
    cit_p = read_doc(CIT_P)
    assert together(cit_p, r"CAP-43\.b", r"\blite\b", r"manifest", r"hash"), (
        "no place in the CIT-P names CAP-43.b, lite, with the manifest and file hashes"
    )


def test_cit_p_says_the_rest_of_cap_43b_stays_for_wave_3():
    """CAP-43.b: everything but the manifest and file hashes stays in Wave 3."""
    cit_p = read_doc(CIT_P)
    named_as_rest = together(cit_p, r"rest of\s+`?CAP-43\.b", W3)
    listed = all(together(cit_p, p, W3) for p in CAP_43B_REST.values())
    assert named_as_rest or listed, (
        "the CIT-P says neither that the rest of CAP-43.b stays in Wave 3 nor lists its other contents with Wave 3"
    )


def test_cit_p_keeps_cap_02c_signed_tags_in_wave_3():
    """CAP-02.c (signed release tags) stays in Wave 3 (DEC-722 item 2)."""
    cit_p = read_doc(CIT_P)
    assert together(cit_p, r"CAP-02\.c", W3), "the CIT-P does not say that CAP-02.c stays in Wave 3"


def test_cit_p_keeps_the_qualification_certificate_in_wave_3():
    """The qualification certificate stays in Wave 3 (the W2-49 card); in the Contract, CAP-43.c."""
    cit_p = read_doc(CIT_P)
    assert together(cit_p, r"qualification certificate|CAP-43\.c|certification by qualification", W3), (
        "the CIT-P does not say that the qualification certificate stays in Wave 3"
    )


@pytest.mark.parametrize("ticket", ["W2-02", "W2-16", "W2-18", "W2-27", "W2-28", "W2-29", "W2-30"])
def test_cit_p_names_each_impacted_ticket(ticket):
    """The impact: W2-02, W2-16, W2-18 and W2-27 to W2-30 (the W2-49 card)."""
    cit_p = read_doc(CIT_P)
    named = has(rf"(?<![\w-]){ticket}(?![\w])", cit_p)
    in_range = ticket in ("W2-27", "W2-28", "W2-29", "W2-30") and has(
        r"W2-27\s*(?:to|through|–|-|…|\.\.\.?)\s*W2-30", cit_p
    )
    assert named or in_range, f"the CIT-P does not name {ticket} in its impact"


def _exit_criteria(text: str) -> set[int]:
    numbers: set[int] = set()
    for m in re.finditer(
        r"exit criteri(?:on|a)\s+((?:\d+)(?:\s*(?:,|and|&|to|–|-)\s*\d+)*)", text, re.IGNORECASE
    ):
        numbers.update(int(n) for n in re.findall(r"\d+", m.group(1)))
    return numbers


@pytest.mark.parametrize("number", [6, 7])
def test_cit_p_names_exit_criteria_6_and_7_in_its_impact(number):
    """The impact: Wave 2 exit criteria 6 (the healthy verdict) and 7 (the lite items, both ways)."""
    cit_p = read_doc(CIT_P)
    assert number in _exit_criteria(cit_p), f"the CIT-P does not name exit criterion {number}"


@pytest.mark.parametrize("option", ["apply now", "defer", "re-?baseline"], ids=["apply-now", "defer", "re-baseline"])
def test_cit_p_presents_dec_105_three_options_with_their_cost(option):
    """A change to a closed specification gives three costed options (DEC-105, CAP-33.e)."""
    cit_p = read_doc(CIT_P)
    assert has(r"DEC-105", cit_p), "the CIT-P does not cite DEC-105"
    assert together(cit_p, rf"\b{option}", r"\bcost"), (
        f"the CIT-P does not present the option '{option}' with its cost"
    )


def test_cit_p_goes_the_cap_33_route_to_the_owner():
    """CAP-33: CIT-P, independent review, the owner's approval, versioned promotion."""
    cit_p = read_doc(CIT_P)
    assert has(r"CAP-33", cit_p), "the CIT-P does not cite CAP-33, its change route"
    assert together(cit_p, r"owner", r"approv"), "the CIT-P does not ask for the owner's approval"
    assert together(cit_p, r"independent", r"review|audit"), "the CIT-P does not name its independent review"
