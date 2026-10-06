"""DEC-438: a family with no registered check is never GREEN.

Fail-open identified after the second reviewer round (DEC-438, under DEC-413
and DEC-136).  Four of the seventeen canonical families currently have **no**
registered check at all: ``context reproducibility``, ``adapter/model
portability``, ``recovery/rebuild``, ``audit reproducibility``.  The runner
initialises every family as GREEN and only downgrades on findings, so these
four are reported GREEN — violating DEC-425 ("unmeasured is never green").

DEC-438 requires:
- A family with no registered check has status YELLOW (never GREEN).
- Its entry carries the reason "no registered check" and check_count 0.
- Every family's entry carries check_count (the number of registered checks).
- A family is GREEN only when it has >= 1 check and none is red/yellow/unmeasured.
"""

from __future__ import annotations

import json

import pytest

import w1_26_support as support


# The four families that have zero checks after add_core_declarations()
# plus the runner's built-in checks (openspec, skill-version, readiness).
ZERO_CHECK_FAMILIES = (
    "context reproducibility",
    "adapter/model portability",
    "recovery/rebuild",
    "audit reproducibility",
)


# =====================================================================
# 1. Family with no registered check is not GREEN in --json
# =====================================================================

def test_no_check_family_not_green_json(project, sandbox, interface):
    """A family with zero registered checks must NOT be GREEN in ``gov check
    --json``.  DEC-425: unmeasured is never green.

    After ``add_core_declarations()`` the runner has 7 core checks plus
    3 built-ins (openspec, skill-version, readiness).  The families
    ``context reproducibility``, ``adapter/model portability``,
    ``recovery/rebuild``, and ``audit reproducibility`` have no check at all.
    Each must be reported as non-GREEN (DEC-438 requires YELLOW).
    """
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    for family_name in ZERO_CHECK_FAMILIES:
        status = support.family_status(result, family_name)
        assert status != support.GREEN, (
            f"family {family_name!r} has zero registered checks but is GREEN; "
            f"DEC-425: unmeasured is never green.  "
            f"Expected YELLOW with reason 'no registered check'.\n"
            f"families: {json.dumps(families, indent=2)}"
        )


# =====================================================================
# 2. Family with no registered check says so by name
# =====================================================================

def test_no_check_family_reason(project, sandbox, interface):
    """The entry for a family with zero checks must contain a reason or
    message indicating "no registered check" — the absence is reported,
    not silently glossed over.
    """
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    target = "context reproducibility"
    entry = families.get(target, {})
    entry_text = json.dumps(entry).lower()

    assert "no registered check" in entry_text, (
        f"family {target!r} has zero checks but its entry does not say "
        f"'no registered check'.  DEC-438 requires the reason to be stated.\n"
        f"entry: {json.dumps(entry, indent=2)}"
    )


# =====================================================================
# 3. Family with no registered check is not GREEN in text output
# =====================================================================

def test_no_check_family_not_green_text(project, sandbox, interface):
    """When running ``gov check`` (without ``--json``), the text output must
    mention a family by name if it has no registered check — the operator
    should see that the family is uncovered.
    """
    project.add_core_declarations()
    project.commit()
    run = project.gov(sandbox, "check")
    combined = run.stdout + run.stderr

    mentioned = False
    for family_name in ZERO_CHECK_FAMILIES:
        if family_name.lower() in combined.lower():
            mentioned = True
            break

    assert mentioned, (
        f"none of the families with zero checks "
        f"({', '.join(ZERO_CHECK_FAMILIES)}) appear in the text output of "
        f"'gov check'.  DEC-438: a family with no registered check must be "
        f"visible to the operator.\n"
        f"stdout: {run.stdout[:500]}\nstderr: {run.stderr[:500]}"
    )


# =====================================================================
# 4. check_count per family in JSON
# =====================================================================

def test_check_count_present_for_every_family(project, sandbox, interface):
    """Every family's entry in ``--json`` must include ``check_count``: the
    number of registered checks for that family.  A family with zero checks
    has ``check_count: 0``; a family with one or more checks has the actual
    count.
    """
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    for family_name in support.FAMILIES:
        entry = families.get(family_name, {})
        assert isinstance(entry, dict), (
            f"family {family_name!r} is not a dict: {entry!r}"
        )
        assert "check_count" in entry, (
            f"family {family_name!r} has no 'check_count' key.  "
            f"DEC-438 requires every family to carry the count of its "
            f"registered checks.\nentry: {json.dumps(entry, indent=2)}"
        )


def test_check_count_zero_for_uncovered_families(project, sandbox, interface):
    """Families with no registered check must have ``check_count: 0``."""
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    for family_name in ZERO_CHECK_FAMILIES:
        entry = families.get(family_name, {})
        count = entry.get("check_count") if isinstance(entry, dict) else None
        assert count == 0, (
            f"family {family_name!r} has no registered check but "
            f"check_count is {count!r}, expected 0.\n"
            f"entry: {json.dumps(entry, indent=2) if isinstance(entry, dict) else entry!r}"
        )


def test_check_count_positive_for_covered_families(project, sandbox, interface):
    """Families that have at least one check must have ``check_count >= 1``."""
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    covered = "schema/invariants"
    entry = families.get(covered, {})
    count = entry.get("check_count") if isinstance(entry, dict) else None
    assert isinstance(count, int) and count >= 1, (
        f"family {covered!r} has core-schema registered but "
        f"check_count is {count!r}, expected >= 1.\n"
        f"entry: {json.dumps(entry, indent=2) if isinstance(entry, dict) else entry!r}"
    )


# =====================================================================
# 5. GREEN requires at least one check and none failing
# =====================================================================

def test_family_green_requires_at_least_one_check(project, sandbox, interface):
    """A family is GREEN only if it has >= 1 registered check and none of
    them is red, yellow, or unmeasured.  A family with zero checks is never
    GREEN — even though it has no failures either.

    This test verifies the logical conjunction: both conditions must hold
    for GREEN.
    """
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    for family_name in ZERO_CHECK_FAMILIES:
        entry = families.get(family_name, {})
        status = entry.get("status") if isinstance(entry, dict) else entry
        assert status != support.GREEN, (
            f"family {family_name!r} has zero checks but is GREEN.  "
            f"GREEN requires >= 1 passing check.  "
            f"DEC-425: unmeasured is never green."
        )

    covered = "schema/invariants"
    covered_entry = families.get(covered, {})
    covered_status = covered_entry.get("status") if isinstance(covered_entry, dict) else covered_entry
    assert covered_status in (support.RED, support.YELLOW, support.GREEN), (
        f"family {covered!r} has a registered check but status is "
        f"{covered_status!r}, expected one of RED/YELLOW/GREEN"
    )
