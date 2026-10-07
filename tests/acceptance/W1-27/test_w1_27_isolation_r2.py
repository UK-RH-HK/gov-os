"""Round 2, KPI success 1 (isolation): doctor's per-repository isolation check
must measure something, not return a constant.

The current ``_check_isolation`` in ``src/gov/doctor/command.py`` returns
``{"status": "pass", "isolated": True}`` unconditionally.  Per DEC-425,
a check that cannot measure must report "unmeasured", never "pass".

Predecessor analysis
--------------------
The first round's ``test_w1_27_doctor.py`` case
``test_doctor_report_mentions_isolation`` only asserts that the word
"isolat" appears somewhere in the doctor output.  A constant stub
satisfies that assertion.  The predecessor's case was **weak**: it
verified the keyword, not the measurement.
"""

from __future__ import annotations

import json

import pytest

import w1_27_support as support


def _doctor_sections(envelope):
    """Extract the doctor's full result dict from a healthy or unhealthy envelope."""
    if envelope["ok"]:
        return envelope.get("result", {})
    return envelope.get("error", {}).get("details", {})


def test_doctor_isolation_is_measured_not_constant(gov, project, interface):
    """The isolation section must reflect actual measurement, not a constant stub (DEC-425).

    A result that is exactly ``{"status": "pass", "isolated": True}`` with
    no additional evidence is never measured — it is the same regardless of
    input.  Per DEC-425: an unmeasured check must report "unmeasured",
    never "pass".
    """
    support.write_path_map(project, support.minimal_valid_path_map())
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")

    sections = _doctor_sections(envelope)
    isolation = sections.get("isolation", {})

    is_constant_stub = (
        isinstance(isolation, dict)
        and set(isolation.keys()) <= {"status", "isolated"}
        and isolation.get("status") == "pass"
    )
    assert not is_constant_stub, (
        f"the isolation check is a constant stub: {isolation} — it reports "
        f"'pass' with no measurement evidence (DEC-425)\n{run.describe()}"
    )
