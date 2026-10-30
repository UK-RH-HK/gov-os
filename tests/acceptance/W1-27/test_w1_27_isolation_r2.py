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

import w1_27_support as support
import w2_67_doctor


def _is_constant_stub(isolation):
    return (
        isinstance(isolation, dict)
        and set(isolation.keys()) <= {"status", "isolated"}
        and isolation.get("status") == "pass"
    )


def test_doctor_isolation_is_measured_not_constant(sandbox, tmp_path):
    """The isolation section must reflect actual measurement, not a constant stub (DEC-425).

    A result that is exactly ``{"status": "pass", "isolated": True}`` with
    no additional evidence is never measured — it is the same regardless of
    input.  Per DEC-425: an unmeasured check must report "unmeasured",
    never "pass".

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion matches a key name
    that doctor always emits): it rejected one exact stub only, and the copy
    had no ``.gov-runtime``, so the measured branch never ran.  Two small
    committed projects now give both outcomes: a ``.gov-runtime`` at the
    repository's root is isolated, and one in a subfolder (its parent is not
    the git root) is not.
    """
    own = w2_67_doctor.small_project(tmp_path / "own")
    (own / ".gov-runtime").mkdir()
    own_run = w2_67_doctor.doctor(own, sandbox)
    isolation = w2_67_doctor.section(own_run, "isolation")
    assert not _is_constant_stub(isolation), (
        f"the isolation check is a constant stub: {isolation} — it reports "
        f"'pass' with no measurement evidence (DEC-425)\n{own_run.describe()}"
    )
    assert isolation.get("isolated") is True and isolation.get("status") == "pass", (
        f"a .gov-runtime at the repository's root is not reported isolated: {isolation}\n{own_run.describe()}"
    )

    outer = w2_67_doctor.small_project(tmp_path / "outer")
    inner = outer / "inner"
    (inner / ".gov-runtime").mkdir(parents=True)
    inner_run = support.run_gov_with_code(support.REPO_ROOT, inner, sandbox, "doctor", "--json")
    nested = w2_67_doctor.section(inner_run, "isolation")
    assert nested.get("isolated") is False and nested.get("status") == "fail", (
        f"a .gov-runtime whose parent ({inner}) is not the git root ({outer}) is not reported as not isolated: "
        f"{nested}\n{inner_run.describe()}"
    )
