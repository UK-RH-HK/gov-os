"""W2-116 S2 (pass 2b): ``gov rebuild --integration <branch> --when-due`` reads the project's two refresh times and runs
the refresh after the nightly's verdict and at the second time; a refresh that ran is recorded beside the link
(``<link>.refresh.json``); a tick that is not due builds and writes nothing (README, "Pass 2b").

The clock is planted with ``GOV_NOW`` and the verdict files' times with ``os.utime``. Each case builds the store once
(the first due tick) and then ticks again: at an unchanged head a refresh is ``unchanged`` (cheap), and the record is
what tells a tick apart.
"""

from __future__ import annotations

import w2_116_s2_support as s2
import w2_116_support as support
from w2_116_s2_support import DAY1, DAY2, at


def test_s2_success_the_two_times_are_read_from_the_planted_configuration(box, env, project):
    s2.plant_config(box, project, latest="05:15", second="21:40", verdict=None)
    # before ``latest``, no verdict file, no record: not due, and nothing is built or written
    early = s2.when_due(project, env, at(DAY1, "04:00"))
    s2.assert_not_due(early, box, support.BRANCH, "04:00, before latest 05:15")
    assert s2.integration_of(early).get("last_refresh") is None
    s2.assert_nothing_built(project, box, "a tick that is not due")
    # past ``latest``: due, after_nightly (the planted 05:15, not any default)
    first = s2.first_refresh(box, env, project, at(DAY1, "05:20"))
    h1 = support.head(project)
    s2.assert_record(box, at(DAY1, "05:20"), "after_nightly", h1, "switched", "the 05:20 refresh")
    # between the two times: not due
    middle = s2.when_due(project, env, at(DAY1, "21:00"))
    s2.assert_not_due(middle, box, support.BRANCH, "21:00, before second 21:40")
    # past ``second``: due, with reason second (the after_nightly slot of the day is used)
    late = s2.when_due(project, env, at(DAY1, "21:45"))
    s2.assert_due(late, "second", "21:45, past second 21:40")
    s2.assert_record(box, at(DAY1, "21:45"), "second", h1, "unchanged", "the 21:45 refresh")
    assert first.ok


def test_s2_success_a_refresh_runs_after_a_newer_verdict_file_and_writes_the_record(box, env, project):
    s2.plant_config(box, project)    # latest 10:00, second 18:00
    s2.plant_verdict(project, "NR-1.txt", s2.LINE_VERDICT, at(DAY1, "08:30"))
    run = s2.when_due(project, env, at(DAY1, "09:00"))
    s2.assert_due(run, "after_nightly", "a verdict file with a `verdict:` line, before latest")
    assert run.result["integration"]["status"] == "switched", f"the refresh built no store\n{run.describe()}"
    h1 = support.head(project)
    assert support.worktrees(project).get(support.assert_link(box), {}).get("head") == h1
    s2.assert_record(box, at(DAY1, "09:00"), "after_nightly", h1, "switched", "the refresh after the verdict")
    assert s2.FULL_SHA.match(s2.record(box)["head"]), f"the record's head is no full sha: {s2.record(box)}"


def test_s2_success_a_json_verdict_file_newer_than_the_last_refresh_is_due(box, env, project):
    s2.plant_config(box, project)
    s2.plant_verdict(project, "NR-1.txt", s2.LINE_VERDICT, at(DAY1, "08:30"))
    s2.first_refresh(box, env, project, at(DAY1, "09:00"))
    h1 = support.head(project)
    s2.plant_verdict(project, "NR-2.json", s2.JSON_VERDICT, at(DAY1, "09:50"))
    run = s2.when_due(project, env, at(DAY1, "09:55"))
    s2.assert_due(run, "after_nightly", "a JSON verdict file with a `verdict` key, newer than the record")
    s2.assert_record(box, at(DAY1, "09:55"), "after_nightly", h1, "unchanged", "the refresh after the JSON verdict")


def test_s2_failure_a_file_without_a_verdict_or_an_older_verdict_does_not_make_a_refresh_due(box, env, project):
    s2.plant_config(box, project)
    s2.plant_verdict(project, "NR-1.txt", s2.LINE_VERDICT, at(DAY1, "08:30"))
    s2.first_refresh(box, env, project, at(DAY1, "09:00"))
    kept = s2.record_bytes(box)
    # a matching file that holds no verdict (a nightly still running), newer than the record
    s2.plant_verdict(project, "NR-2.txt", s2.NO_VERDICT_TEXT, at(DAY1, "09:30"))
    s2.plant_verdict(project, "NR-3.json", s2.NO_VERDICT_JSON, at(DAY1, "09:31"))
    run = s2.when_due(project, env, at(DAY1, "09:45"))
    s2.assert_not_due(run, box, support.BRANCH, "files that match but hold no verdict")
    # a verdict file older than the record's at
    s2.plant_verdict(project, "NR-4.txt", s2.LINE_VERDICT, at(DAY1, "08:45"))
    run = s2.when_due(project, env, at(DAY1, "09:46"))
    s2.assert_not_due(run, box, support.BRANCH, "a verdict file older than the record's at")
    assert s2.record_bytes(box) == kept, "a tick that was not due rewrote the record"


def test_s2_success_latest_passes_without_a_verdict_and_the_same_day_is_not_due_again(box, env, project):
    s2.plant_config(box, project)
    first = s2.when_due(project, env, at(DAY1, "10:05"))     # no verdict file at all, no record
    s2.assert_due(first, "after_nightly", "latest 10:00 passed with no verdict")
    h1 = support.head(project)
    s2.assert_record(box, at(DAY1, "10:05"), "after_nightly", h1, "switched", "the refresh at latest")
    kept = s2.record_bytes(box)
    again = s2.when_due(project, env, at(DAY1, "10:30"))
    s2.assert_not_due(again, box, support.BRANCH, "the same day, after the after_nightly refresh")
    assert s2.record_bytes(box) == kept, "a tick that was not due rewrote the record"
    # the next day: yesterday's after_nightly refresh does not stand in for today's
    early = s2.when_due(project, env, at(DAY2, "09:00"))
    s2.assert_not_due(early, box, support.BRANCH, "the next day, before latest")
    next_day = s2.when_due(project, env, at(DAY2, "10:05"))
    s2.assert_due(next_day, "after_nightly", "the next day, latest passed again")
    s2.assert_record(box, at(DAY2, "10:05"), "after_nightly", h1, "unchanged", "the next day's refresh")


def test_s2_success_second_is_due_once_after_its_time_and_brings_the_store_to_the_branch_head(box, env, project):
    s2.plant_config(box, project)
    s2.first_refresh(box, env, project, at(DAY1, "10:05"))
    ready = support.assert_link(box)
    h2 = support.land_h2(project)
    # a merge landed, but no refresh is due at noon: the scheduled tick does not follow the merge
    noon = s2.when_due(project, env, at(DAY1, "12:00"))
    s2.assert_not_due(noon, box, support.BRANCH, "noon, after a merge, between the two times")
    assert support.target(box) == ready, "a tick that was not due moved the link"
    run = s2.when_due(project, env, at(DAY1, "18:05"))
    s2.assert_due(run, "second", "past second 18:00")
    assert run.result["integration"]["status"] == "switched", f"the second refresh did not switch\n{run.describe()}"
    s2.assert_record(box, at(DAY1, "18:05"), "second", h2, "switched", "the refresh at second")
    assert support.worktrees(project).get(support.assert_link(box), {}).get("head") == h2
    once = s2.when_due(project, env, at(DAY1, "18:10"))
    s2.assert_not_due(once, box, support.BRANCH, "the next tick, after the second refresh")


def test_s2_success_a_second_refresh_does_not_stand_in_for_the_after_nightly_one(box, env, project):
    # a project whose second time falls before ``latest``: the refresh at second has reason second, and latest still
    # falls due afterwards (no scheduled refresh with reason after_nightly is on today's date)
    s2.plant_config(box, project, latest="10:00", second="06:00")
    early = s2.when_due(project, env, at(DAY1, "07:00"))
    s2.assert_due(early, "second", "second 06:00 passed, latest 10:00 not yet")
    h1 = support.head(project)
    s2.assert_record(box, at(DAY1, "07:00"), "second", h1, "switched", "the refresh at second")
    still = s2.when_due(project, env, at(DAY1, "09:00"))
    s2.assert_not_due(still, box, support.BRANCH, "09:00, after the second refresh, before latest")
    later = s2.when_due(project, env, at(DAY1, "10:05"))
    s2.assert_due(later, "after_nightly", "latest passed; only a second refresh was made today")
    s2.assert_record(box, at(DAY1, "10:05"), "after_nightly", h1, "unchanged", "the refresh at latest")


def test_s2_success_when_both_are_due_one_refresh_runs_with_reason_after_nightly(box, env, project):
    s2.plant_config(box, project)
    run = s2.when_due(project, env, at(DAY1, "19:00"))       # past latest 10:00 and second 18:00, no record
    s2.assert_due(run, "after_nightly", "both times passed with no record")
    s2.assert_record(box, at(DAY1, "19:00"), "after_nightly", support.head(project), "switched", "the one refresh")
    again = s2.when_due(project, env, at(DAY1, "19:05"))
    s2.assert_not_due(again, box, support.BRANCH, "after the one refresh that answered both")


def test_s2_success_the_verdict_glob_defaults_to_docs_close_nightly_nr_json(box, env, project):
    s2.plant_config(box, project, verdict=None, latest="10:00", second="18:00")
    s2.plant_verdict(project, "NR-1.json", s2.JSON_VERDICT, at(DAY1, "08:30"), folder="docs/close/nightly")
    run = s2.when_due(project, env, at(DAY1, "09:00"))
    s2.assert_due(run, "after_nightly", "a verdict file in docs/close/nightly with no verdict key configured")
