"""DEC-438: a family with no registered check is never GREEN.

Fail-open identified after the second reviewer round (DEC-438, under DEC-413
and DEC-136).  The runner initialises every family as GREEN and only downgrades
on findings, so any family without a registered check would be reported GREEN —
violating DEC-425 ("unmeasured is never green").

DEC-438 requires:
- A family with no registered check has status YELLOW (never GREEN).
- Its entry carries the reason "no registered check" and check_count 0.
- Every family's entry carries check_count (the number of registered checks).
- A family is GREEN only when it has >= 1 check and none is red/yellow/unmeasured.

No case in this file depends on which families other tickets have registered.
Each case that needs an uncovered family removes the ``core-claims`` declaration
so that ``concurrency/claims`` is guaranteed uncovered, then derives the full
set of uncovered families from the runner's own ``check_count`` field.
"""

from __future__ import annotations

import json

import pytest

import w1_26_support as support


# The family this module forces uncovered by removing its sole check
# declaration, and the check id to remove.  Picked so no other test in
# this file uses it as a covered exemplar.
_FORCED_UNCOVERED_FAMILY = "concurrency/claims"
_FORCED_CHECK_ID = "core-claims"


def _uncovered_from_result(result):
    """Families the runner reports as having no registered check (check_count 0)."""
    families = support.families_of(result)
    return {
        name for name in support.FAMILIES
        if isinstance(families.get(name), dict)
        and families[name].get("check_count") == 0
    }


def _setup_with_forced_uncovered(project):
    """Add core declarations then remove one check to guarantee an uncovered family."""
    project.add_core_declarations()
    project.remove_check_declaration(_FORCED_CHECK_ID)


# =====================================================================
# 1. Family with no registered check is not GREEN in --json
# =====================================================================

def test_no_check_family_not_green_json(project, sandbox, interface):
    """A family with zero registered checks must NOT be GREEN in ``gov check
    --json``.  DEC-425: unmeasured is never green.

    The set of uncovered families is derived from the runner's own
    ``check_count`` field, not from a fixed list.
    """
    _setup_with_forced_uncovered(project)
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    uncovered = _uncovered_from_result(result)
    assert _FORCED_UNCOVERED_FAMILY in uncovered, (
        f"{_FORCED_UNCOVERED_FAMILY!r} should be uncovered after removing "
        f"{_FORCED_CHECK_ID!r}, but check_count is "
        f"{families.get(_FORCED_UNCOVERED_FAMILY, {}).get('check_count')!r}"
    )

    for family_name in uncovered:
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

    Checked for every uncovered family, not a single hard-coded name.
    """
    _setup_with_forced_uncovered(project)
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    uncovered = _uncovered_from_result(result)
    assert _FORCED_UNCOVERED_FAMILY in uncovered, (
        f"{_FORCED_UNCOVERED_FAMILY!r} should be uncovered after removing "
        f"{_FORCED_CHECK_ID!r}, but check_count is "
        f"{families.get(_FORCED_UNCOVERED_FAMILY, {}).get('check_count')!r}"
    )

    for family_name in uncovered:
        entry = families.get(family_name, {})
        entry_text = json.dumps(entry).lower()

        assert "no registered check" in entry_text, (
            f"family {family_name!r} has zero checks but its entry does not say "
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

    Uses the deliberately forced-uncovered family rather than a fixed list.
    """
    _setup_with_forced_uncovered(project)
    project.commit()
    run = project.gov(sandbox, "check")
    combined = run.stdout + run.stderr

    assert _FORCED_UNCOVERED_FAMILY.lower() in combined.lower(), (
        f"family {_FORCED_UNCOVERED_FAMILY!r} has no registered check but "
        f"does not appear in the text output of 'gov check'.  "
        f"DEC-438: a family with no registered check must be visible to "
        f"the operator.\n"
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
    """Families with no registered check must have ``check_count: 0``.

    The forced-uncovered family provides the non-tautological anchor;
    the remaining uncovered families (derived from the result) are
    asserted for completeness.
    """
    _setup_with_forced_uncovered(project)
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    forced_entry = families.get(_FORCED_UNCOVERED_FAMILY, {})
    forced_count = forced_entry.get("check_count") if isinstance(forced_entry, dict) else None
    assert forced_count == 0, (
        f"family {_FORCED_UNCOVERED_FAMILY!r} has no registered check but "
        f"check_count is {forced_count!r}, expected 0.\n"
        f"entry: {json.dumps(forced_entry, indent=2) if isinstance(forced_entry, dict) else forced_entry!r}"
    )

    for family_name in _uncovered_from_result(result):
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
    for GREEN.  The set of uncovered families is derived, not hard-coded.
    """
    _setup_with_forced_uncovered(project)
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    uncovered = _uncovered_from_result(result)
    assert _FORCED_UNCOVERED_FAMILY in uncovered, (
        f"{_FORCED_UNCOVERED_FAMILY!r} should be uncovered after removing "
        f"{_FORCED_CHECK_ID!r}"
    )

    for family_name in uncovered:
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
