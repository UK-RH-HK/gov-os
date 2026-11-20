"""S5 (fix, DEC-1223 (6)): `gov doctor` reports a pending update in a part `updates` (CAP-45.b).

The part reads the local source only (`_src_path` of the clone's answers, its tags and the records at them). It is a
notice: its status is always `report`, and `healthy` and every other part's status are those of the same clone with
the source untouched. The clone names its source through a link, so each run differs from the reference run only
by the source the link names.
"""

from __future__ import annotations

import pytest

import w2_17_support as support
from w2_17_support import NO_KIND, OTHER_KIND, PATCH, UNREADABLE_KIND


def _same_as_untouched(case, run, what):
    """doctor's exit code, `healthy` and every other part's status as with the source untouched."""
    assert run.returncode == case.reference.returncode, (
        f"{what}: gov doctor exits {run.returncode}, not {case.reference.returncode} as with the source untouched\n"
        f"{run.describe()}")
    expected, actual = support.other_statuses(case.reference), support.other_statuses(run)
    differing = sorted(name for name in set(expected) | set(actual) if expected.get(name) != actual.get(name))
    assert not differing, (
        f"{what}: `healthy` or other parts' statuses differ from the same clone with the source untouched: "
        + ", ".join(f"{name} {expected.get(name)!r} -> {actual.get(name)!r}" for name in differing))


def _part(run, what):
    part = support.updates_part(run)
    assert part.get("status") == "report", f"{what}: the updates part's status is not `report`: {part!r}"
    return part


def test_doctor_reports_a_pending_patch_with_its_fixes_and_the_quiet_point(doctor_at_a):
    run = doctor_at_a.runs[PATCH]
    part = _part(run, "a patch release B pending")
    missing = [key for key in support.UPDATES_KEYS if key not in part]
    assert not missing, f"the updates part lacks {missing}: {part!r}"
    found = {key: part.get(key) for key in ("held", "newest", "pending", "kind", "fixes")}
    expected = {"held": support.A, "newest": support.B, "pending": True, "kind": "patch", "fixes": support.FIXES}
    assert found == expected, (
        f"the updates part does not report held {support.A}, newest {support.B} (the tag {support.DECOY_TAG} has no "
        f"record), pending, kind patch and {support.FIXES} fixes: {found!r}")
    assert support.QUIET_STEP in str(part.get("next")), (
        f"the next step of a patch is not {support.QUIET_STEP!r}: {part.get('next')!r}")
    summary = part.get("summary")
    assert isinstance(summary, str) and summary.strip() and "\n" not in summary.strip(), (
        f"the summary is not one line: {summary!r}")
    _same_as_untouched(doctor_at_a, run, "a patch release B pending")


@pytest.mark.parametrize("variant", [NO_KIND, UNREADABLE_KIND, OTHER_KIND])
def test_doctor_reports_a_release_not_marked_patch_as_bigger_for_the_owner(variant, doctor_at_a):
    run = doctor_at_a.runs[variant]
    what = {NO_KIND: "B's record carries no kind.json", UNREADABLE_KIND: "B's kind.json does not read",
            OTHER_KIND: "B's kind.json says minor"}[variant]
    part = _part(run, what)
    found = {key: part.get(key) for key in ("held", "newest", "pending", "kind", "fixes")}
    assert found == {"held": support.A, "newest": support.B, "pending": True, "kind": "bigger",
                     "fixes": support.FIXES}, (
        f"{what}: the updates part does not report held {support.A}, newest {support.B}, pending, kind bigger and "
        f"{support.FIXES} fixes: {found!r}")
    step = str(part.get("next"))
    assert "owner decides" in step and support.OWNER_STEP in step and support.QUIET_STEP not in step, (
        f"{what}: the next step does not say the owner decides with `{support.OWNER_STEP}`: {step!r}")
    _same_as_untouched(doctor_at_a, run, what)


def test_doctor_says_up_to_date_for_a_clone_at_the_newest_release(project_at_b, tmp_path, sandbox):
    project = support.copy_project(project_at_b, tmp_path / "product")
    run = support.gov(project, sandbox, "doctor", "--json")
    part = _part(run, f"the clone at {support.B}")
    assert part.get("pending") is False, f"the clone at {support.B} is reported pending: {part!r}"
    assert part.get("held") == support.B, f"the updates part does not name the held release {support.B}: {part!r}"
    assert f"up to date ({support.B})" in str(part.get("summary")), (
        f"the summary does not say `up to date ({support.B})`: {part.get('summary')!r}")
    assert isinstance(part.get("reason"), str) and part["reason"].strip(), (
        f"no newer verified record, and the part gives no reason: {part!r}")


def test_doctor_with_an_unreadable_source_reports_nothing_pending_and_stays_as_healthy(doctor_at_a):
    run = doctor_at_a.runs["nowhere"]
    what = "_src_path pointing nowhere"
    part = _part(run, what)
    assert part.get("pending") is False and isinstance(part.get("reason"), str) and part["reason"].strip(), (
        f"{what}: the updates part does not report pending false with a reason: {part!r}")
    _same_as_untouched(doctor_at_a, run, what)


def test_doctor_holds_an_update_rolled_back_here(doctor_rolled_back_here):
    run = doctor_rolled_back_here.runs[PATCH]
    what = f"{support.ROLLED_BACK_REL} in the clone"
    part = _part(run, what)
    assert support.HELD_STEP in str(part.get("next")), (
        f"{what}: the next step is not {support.HELD_STEP!r}: {part!r}")
    assert part.get("pending") is False and part.get("rolled_back") is True, (
        f"{what}: the updates part does not report pending false and rolled_back true: {part!r}")
    _same_as_untouched(doctor_rolled_back_here, run, what)


def test_doctor_with_no_held_release_reports_nothing_pending(doctor_no_release):
    run = doctor_no_release.runs[PATCH]
    what = "a lock stating release: null"
    part = _part(run, what)
    assert part.get("pending") is False and isinstance(part.get("reason"), str) and part["reason"].strip(), (
        f"{what}: the updates part does not report pending false with a reason: {part!r}")
    _same_as_untouched(doctor_no_release, run, what)
