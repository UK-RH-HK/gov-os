"""W2-116 S2 (pass 2b): ``gov status --json`` names the integration store's head and age, and a stale store is named
(README, "Pass 2b"): ``result.integration_store`` is ``{link, half, head, branch, branch_head, built_at, age_seconds,
stale, stale_reason, last_refresh}``; stale when the store's head is not the branch's (``behind_branch``) or it was built
before the last time a refresh fell due (``built_before_due``).

``built_at`` is the build's real clock (the half's ``stores.json``, ``written_at``), so the cases plant ``GOV_NOW`` and the
configured times relative to it. ``GOV_NOW``'s offset is its wall clock: the cases pick the offset in which the real clock
reads about 12:00, so that no planted time (all within a few hours of the build) crosses a midnight.
"""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

import w2_116_s2_support as s2
import w2_116_support as support
from w2_116_s2_support import MISSING

MIN = dt.timedelta(minutes=1)


def build(box, env, project):
    """The store built by a plain refresh; returns the build's instant, the zone and the head."""
    support.built_integration(project, env)
    built = s2.built_at(box)
    return built, s2.midday_zone(built), support.head(project)


def clock(built, zone, minutes):
    return (built + minutes * MIN).astimezone(zone)


def future_times(built, zone):
    """Configured times that fall due only well after the build: ``latest`` three hours and ``second`` four hours on."""
    return {"latest": s2.hhmm(built + 180 * MIN, zone), "second": s2.hhmm(built + 240 * MIN, zone)}


def test_s2_success_status_names_the_integration_store_s_head_and_age_and_a_fresh_store_is_not_stale(box, env, project):
    s2.plant_config(box, project, latest="10:00", second="18:00")
    s2.first_refresh(box, env, project, s2.at(s2.DAY1, "10:05"))      # a record to name; the store is built here
    built = s2.built_at(box)
    zone = s2.midday_zone(built)
    head = support.head(project)
    s2.plant_config(box, project, commit=False, **future_times(built, zone))
    now = clock(built, zone, 90)
    part = s2.integration_store_part(s2.status(project, env, now))
    half = os.path.realpath(box.link)
    assert part.get("link") == str(box.link), f"link: {part.get('link')!r}"
    assert part.get("half") == half, f"half: {part.get('half')!r}, the link points at {half}"
    assert part.get("head") == head and s2.FULL_SHA.match(part["head"]), f"head: {part.get('head')!r}, not {head}"
    assert part.get("branch") == support.BRANCH, f"branch: {part.get('branch')!r}"
    assert part.get("branch_head") == head, f"branch_head: {part.get('branch_head')!r}, not {head}"
    assert s2.instant(part.get("built_at")) == built, f"built_at {part.get('built_at')!r} is not the build's {built}"
    assert part.get("age_seconds") == 90 * 60, f"age_seconds {part.get('age_seconds')!r}, expected {90 * 60} (GOV_NOW - built_at)"
    assert part.get("stale") is False and part.get("stale_reason") is None, (
        f"a fresh store is stale: {part.get('stale')!r}, {part.get('stale_reason')!r}")
    assert part.get("last_refresh") == s2.record(box), f"last_refresh {part.get('last_refresh')!r} is not the record's content"
    # the age follows GOV_NOW
    later = s2.integration_store_part(s2.status(project, env, clock(built, zone, 150)))
    assert later.get("age_seconds") == 150 * 60, f"age_seconds {later.get('age_seconds')!r}, expected {150 * 60}"
    assert later.get("stale") is False, f"the store is stale at +150 min, before any time fell due: {later.get('stale_reason')!r}"


def test_s2_success_a_store_behind_the_branch_is_stale_and_the_reason_names_both_heads(box, env, project):
    built, zone, h1 = build(box, env, project)
    h2 = support.land_h2(project)
    s2.plant_config(box, project, commit=False, **future_times(built, zone))
    part = s2.integration_store_part(s2.status(project, env, clock(built, zone, 30)))
    assert part.get("head") == h1 and part.get("branch_head") == h2, (
        f"head {part.get('head')!r} / branch_head {part.get('branch_head')!r}, expected {h1} / {h2}")
    assert part.get("stale") is True, f"a store behind the branch is not stale: {part}"
    reason = part.get("stale_reason") or ""
    assert "behind_branch" in reason, f"the stale reason does not say behind_branch: {reason!r}"
    assert s2.names_commit(reason, h1) and s2.names_commit(reason, h2), (
        f"the reason does not name both heads ({h1[:12]}, {h2[:12]}): {reason!r}")
    assert "built_before_due" not in reason, f"built_before_due holds for no time that fell due: {reason!r}"


def test_s2_success_a_store_built_before_latest_fell_due_is_stale_and_the_reason_names_the_time(box, env, project):
    built, zone, h1 = build(box, env, project)
    latest = built + 30 * MIN
    s2.plant_config(box, project, commit=False, latest=s2.hhmm(latest, zone), second=s2.hhmm(built + 240 * MIN, zone))
    part = s2.integration_store_part(s2.status(project, env, clock(built, zone, 60)))
    assert part.get("head") == part.get("branch_head") == h1
    assert part.get("stale") is True, f"a store built before latest passed is not stale: {part}"
    reason = part.get("stale_reason") or ""
    assert "built_before_due" in reason, f"the stale reason does not say built_before_due: {reason!r}"
    assert s2.names_instant(reason, latest, zone), f"the reason does not name the time ({s2.hhmm(latest, zone)}): {reason!r}"
    assert "behind_branch" not in reason, f"the store is at the branch's head: {reason!r}"
    # before that time passes, the same store is not stale
    before = s2.integration_store_part(s2.status(project, env, clock(built, zone, 20)))
    assert before.get("stale") is False, f"the store is stale before latest passed: {before.get('stale_reason')!r}"


def test_s2_success_a_store_built_before_a_verdict_file_is_stale(box, env, project):
    built, zone, h1 = build(box, env, project)
    verdict = built + 10 * MIN
    s2.plant_config(box, project, commit=False, **future_times(built, zone))
    s2.plant_verdict(project, "NR-1.txt", s2.LINE_VERDICT, verdict)
    part = s2.integration_store_part(s2.status(project, env, clock(built, zone, 20)))
    assert part.get("stale") is True, f"a store built before the nightly's verdict is not stale: {part}"
    reason = part.get("stale_reason") or ""
    assert "built_before_due" in reason, f"the stale reason does not say built_before_due: {reason!r}"
    assert s2.names_instant(reason, verdict, zone), f"the reason does not name the verdict's time ({s2.hhmm(verdict, zone)}): {reason!r}"
    # a verdict file that holds no verdict does not count
    os.remove(Path(project) / s2.VERDICT_DIR / "NR-1.txt")
    s2.plant_verdict(project, "NR-2.txt", s2.NO_VERDICT_TEXT, verdict)
    part = s2.integration_store_part(s2.status(project, env, clock(built, zone, 20)))
    assert part.get("stale") is False, f"a file with no verdict made the store stale: {part.get('stale_reason')!r}"


def test_s2_success_a_latest_that_a_verdict_already_answered_does_not_make_the_store_stale(box, env, project):
    built, zone, h1 = build(box, env, project)
    # latest falls after the build, but the nightly's verdict that day came before it (and before the build)
    s2.plant_config(box, project, commit=False, latest=s2.hhmm(built + 60 * MIN, zone), second=s2.hhmm(built + 240 * MIN, zone))
    now = clock(built, zone, 120)
    answered = s2.integration_store_part(s2.status(project, env, now))
    assert answered.get("stale") is True, f"premise: with no verdict file, latest passing after the build makes it stale: {answered}"
    s2.plant_verdict(project, "NR-1.txt", s2.LINE_VERDICT, built - 30 * MIN)
    part = s2.integration_store_part(s2.status(project, env, now))
    assert part.get("stale") is False, (
        f"latest was counted although a verdict fell on its date before it: {part.get('stale_reason')!r}")


def test_s2_failure_no_store_configured_or_no_link_gives_an_unread_part_and_status_still_exits_0(box, env, project):
    s2.plant_config(box, project, store=False)
    none = s2.status(project, env)
    assert none.returncode == 0, f"gov status refused for a project with no integration_store\n{none.describe()}"
    part = none.result.get("integration_store")
    assert s2.is_unread(part), f"no integration_store configured: the part is {part!r}, not {{read: false, reason}}"
    assert any(str(entry).startswith("integration_store") for entry in none.result.get("not_read") or []), (
        f"not_read does not name the integration store: {none.result.get('not_read')}")
    # configured, never built: no link
    s2.plant_config(box, project)
    unbuilt = s2.status(project, env)
    assert unbuilt.returncode == 0, f"gov status refused for a link that does not exist\n{unbuilt.describe()}"
    assert s2.is_unread(unbuilt.result.get("integration_store")), (
        f"no link: the part is {unbuilt.result.get('integration_store')!r}, not {{read: false, reason}}")


def test_s2_failure_without_a_refresh_configuration_the_store_is_named_and_the_stale_judgement_is_unread(box, env, project):
    built, zone, h1 = build(box, env, project)
    s2.plant_config(box, project, commit=False, refresh=False)
    part = s2.integration_store_part(s2.status(project, env, clock(built, zone, 30)))
    for key, expected in (("link", str(box.link)), ("half", os.path.realpath(box.link)), ("head", h1)):
        assert part.get(key) == expected, f"{key}: {part.get(key)!r}, expected {expected!r}"
    assert s2.instant(part.get("built_at")) == built and part.get("age_seconds") == 30 * 60, (
        f"built_at / age_seconds: {part.get('built_at')!r} / {part.get('age_seconds')!r}")
    assert "last_refresh" in part and part["last_refresh"] is None, f"last_refresh: {part.get('last_refresh')!r}"
    for key in ("branch", "branch_head", "stale", "stale_reason"):
        assert s2.is_unread(part.get(key)), f"{key} is {part.get(key)!r}, not {{read: false, reason}}"
        assert "integration_refresh" in part[key]["reason"], f"the reason of {key} does not name the key: {part[key]!r}"


def test_s2_failure_an_invalid_time_leaves_the_stale_judgement_unread_naming_the_key(box, env, project):
    built, zone, h1 = build(box, env, project)
    s2.plant_config(box, project, commit=False, second="25:00", latest=s2.hhmm(built + 180 * MIN, zone))
    part = s2.integration_store_part(s2.status(project, env, clock(built, zone, 30)))
    assert part.get("head") == h1 and part.get("age_seconds") == 30 * 60, f"head / age: {part.get('head')!r} / {part.get('age_seconds')!r}"
    for key in ("stale", "stale_reason"):
        assert s2.is_unread(part.get(key)), f"{key} is {part.get(key)!r}, not {{read: false, reason}}"
        assert "integration_refresh.second" in part[key]["reason"], f"the reason of {key} does not name the key: {part[key]!r}"
