"""Part 1, KPI 2 and failure line 1, KPI 7: what widens a close to the full regression, and ``--full``.

A change under the shared core, a change no mapping places, a missing or unreadable test map, and a base that
cannot be known each run the full regression: every suite runs, the evidence says ``full`` and why, and nothing
is left out. Anything less is a failure (README, "Part 1").
"""

import pytest

import w2_66_support as support


# --------------------------------------------------------------------------
# The shared core (the fixture's list: src/gov/close/**, the path map, the test map)
# --------------------------------------------------------------------------

def test_a_change_under_the_shared_core_runs_the_full_regression(fixture, sandbox):
    fixture.merged({support.CORE: "# the shared core, changed\n"})
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    support.assert_full(run, fixture, support.SHARED_CORE, path=support.CORE)


def test_a_change_to_the_path_map_runs_the_full_regression(fixture, sandbox):
    text = (fixture.root / support.PATH_MAP_REL).read_text(encoding="utf-8")
    fixture.merged({support.PATH_MAP_REL: text + "# a comment\n"})
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    support.assert_full(run, fixture, support.SHARED_CORE, path=support.PATH_MAP_REL)


def test_a_change_to_the_test_map_runs_the_full_regression(fixture, sandbox):
    text = (fixture.root / support.TEST_MAP_REL).read_text(encoding="utf-8")
    fixture.merged({support.TEST_MAP_REL: text + "# a comment\n"})
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    support.assert_full(run, fixture, support.SHARED_CORE, path=support.TEST_MAP_REL)


def test_a_shared_core_change_in_the_ticket_s_own_commit_runs_the_full_regression(make_fixture, sandbox):
    """The ticket's own paths may hold shared core: its own commit widens the run the same way."""
    fixture = make_fixture()
    text = (fixture.root / support.close_support.ticket_path(support.TICKET)).read_text(encoding="utf-8")
    fixture.record_commit({support.close_support.ticket_path(support.TICKET):
                           text.replace("- src/gov/widget/**", "- src/gov/widget/**\n- src/gov/close/**")})
    fixture.work({support.WIDGET: "# changed\n", support.CORE: "# changed too\n"})
    fixture.ready(sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    support.assert_full(run, fixture, support.SHARED_CORE, path=support.CORE)


# --------------------------------------------------------------------------
# What cannot be placed or read fails safe
# --------------------------------------------------------------------------

def test_a_changed_file_no_mapping_places_runs_the_full_regression(fixture, sandbox):
    fixture.merged({support.UNPLACED_FILE: "# changed, and nobody's\n"})
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    support.assert_full(run, fixture, support.UNPLACED, path=support.UNPLACED_FILE)


def test_a_missing_test_map_runs_the_full_regression(make_fixture, sandbox):
    fixture = make_fixture(test_map=None)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    support.assert_full(run, fixture, support.TEST_MAP_MISSING)


@pytest.mark.parametrize("text", [
    "shared_core: [src/gov/close/**\nrecord_only: {\n",           # not YAML
    "version: 1\nshared_core: 7\n",                                 # YAML, not valid against the schema
    "- just\n- a list\n",                                           # not a mapping
], ids=["not-yaml", "not-the-schema", "not-a-mapping"])
def test_a_test_map_that_cannot_be_read_runs_the_full_regression(make_fixture, sandbox, text):
    fixture = make_fixture(test_map=text)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    support.assert_full(run, fixture, support.TEST_MAP_UNREADABLE)


def test_without_a_record_of_a_green_commit_the_base_is_unknown_and_the_run_is_full(make_fixture, sandbox):
    fixture = make_fixture(green=False)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.assert_full(run, fixture, support.BASE_UNKNOWN)
    assert evidence.get("base") is None, f"an unknown base is stated as a commit: {evidence.get('base')!r}"


@pytest.mark.parametrize("named", ["0" * 40, "not-a-commit"], ids=["no-such-commit", "not-a-commit-id"])
def test_a_green_record_naming_no_commit_of_the_history_leaves_the_base_unknown(make_fixture, sandbox, named):
    fixture = make_fixture(green=False)
    fixture.plant_green_night(named)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    support.assert_full(run, fixture, support.BASE_UNKNOWN)


def test_a_red_night_is_no_base(make_fixture, sandbox):
    fixture = make_fixture(green=False)
    fixture.plant_green_night(fixture.initial, verdict=support.RED)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    support.assert_full(run, fixture, support.BASE_UNKNOWN)


# --------------------------------------------------------------------------
# KPI 7: gov close --full
# --------------------------------------------------------------------------

def test_full_runs_the_full_regression_and_the_record_says_so(fixture, sandbox):
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox, support.FULL_OPTION)
    support.passed(run)
    evidence = support.assert_full(run, fixture, support.FULL_ASKED)
    assert support.record_evidence(fixture).get("scope") == support.FULL, "the close record does not say full"
    assert evidence.get("base") == fixture.initial, f"a full run still states its base: {evidence.get('base')!r}"


def test_a_passed_full_close_is_the_base_of_the_next_scoped_close(make_fixture, sandbox):
    """No nightly record: the first ticket's ``--full`` close is the last fully green commit for the next."""
    fixture = make_fixture(green=False)
    first, wbs = "PROJ-ffff", "W2-ff"
    fixture.record_commit({
        support.close_support.ticket_path(first): support.close_support.ticket_text(
            first, wbs, allowed_paths=["src/gov/fine/**"], status="in_progress"),
        f"{support.suite_of(wbs)}/test_ff.py": "def test_ff():\n    assert True\n",
    }, "the first ticket")
    fixture.work({"src/gov/fine/f.py": "# fine\n"}, ticket=first)
    fixture.ready(sandbox, ticket=first)
    full_head = fixture.head()
    support.passed(fixture.close(sandbox, support.FULL_OPTION, ticket=first))
    fixture.commit_what_the_close_left()
    for path in fixture.told.iterdir():
        path.unlink()
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.evidence_of(run)
    assert evidence.get("scope") == support.SCOPED, f"the second close is not scoped: {evidence}"
    assert evidence.get("base") == full_head, \
        f"the base is not the head of the passed full close ({full_head}): {evidence.get('base')!r}"
    assert f"docs/close/{first}/CL-{first}.md" in (evidence.get("changed") or []), \
        "the full close's own record commit is not inside the change"
