"""S4: everything else the nightly does is unchanged: its selection, its runs, its record and its verdict [DEC-915,
DEC-890].

The same tiny project on a green night and on a red one (W2-66's interface, ``src/gov/close/nightly.py``'s module
text on the base): the selection is the full suite (``scope: full``, every test ran); the runs (the red test run
again alone, then bisected over the commits since the last green night to the culprit); the record's keys are
exactly today's (no ``cleanup`` key when the removal succeeds); the verdict, the exit code and the API-0002 envelope
are as today; and the clone is gone afterwards (its folder, its registration and its entry).

These cases are expected green before the implementation: they guard the behaviour W2-77 must not change.
"""

import pytest

import w2_77_support as support


class Nights:
    """A green night and a red night, run once for the module's cases."""

    def __init__(self, factory):
        self.green_project = support.Project(factory.mktemp("w2_77_green"))
        self.green_run = self.green_project.nightly()
        self.red_project = support.Project(factory.mktemp("w2_77_red"), red=True)
        self.red_run = self.red_project.nightly()


@pytest.fixture(scope="module")
def nights(tmp_path_factory):
    return Nights(tmp_path_factory)


def test_a_green_night_s_envelope_exit_code_and_verdict_are_as_today(nights):
    result = support.green(nights.green_run)
    data = nights.green_run.envelope()
    assert data.get("command") == support.COMMAND, f"the envelope's command is not {support.COMMAND!r}: {data}"
    assert set(result) == support.RECORD_KEYS | {"record"}, \
        f"the green envelope's result is not the record and its path: {sorted(result)}"
    record, rel = support.record_of(nights.green_project, nights.green_run)
    assert result["record"] == rel and record.get("verdict") == support.GREEN, f"not a green record: {record}"
    assert record.get("branch") == "main" and record.get("head") == nights.green_project.head("main"), \
        f"the record does not name the branch and its head: {record}"


def test_a_green_night_s_record_has_exactly_today_s_keys_and_no_cleanup_key(nights):
    support.green(nights.green_run)
    record, rel = support.record_of(nights.green_project, nights.green_run)
    assert support.CLEANUP_KEY not in record, f"a night whose clone was removed has a cleanup key in {rel}: {record}"
    assert set(record) == support.RECORD_KEYS, \
        (f"the record's keys changed: added {sorted(set(record) - support.RECORD_KEYS)}, "
         f"lost {sorted(support.RECORD_KEYS - set(record))}")


def test_a_green_night_selects_and_runs_the_full_suite(nights):
    support.green(nights.green_run)
    record, _ = support.record_of(nights.green_project, nights.green_run)
    assert record.get("scope") == support.FULL, f"the night is not stated full: {record.get('scope')!r}"
    told = nights.green_project.told_runs()
    assert len(told.get(support.PLAIN_CASE, [])) == 1, f"the suite's telling test did not run once: {told}"
    assert (nights.green_project.probe / "clone").is_file(), "the suite's probe did not run"
    assert not record.get("failures") and not record.get("packages") and not record.get("findings"), \
        f"a green night lists failures, packages or findings: {record}"
    assert (record.get("tests_run") or {}).get("passed") == 2, f"the green night did not pass 2 tests: {record}"


def test_a_red_night_s_envelope_exit_code_and_verdict_are_as_today(nights):
    error = support.red(nights.red_run)
    details = error.get("details") or {}
    assert set(details) == support.RECORD_KEYS | {"record"}, \
        f"the red envelope's details are not the record and its path: {sorted(details)}"
    record, rel = support.record_of(nights.red_project, nights.red_run)
    assert details["record"] == rel and record.get("verdict") == support.RED, f"not a red record: {record}"
    assert set(record) == support.RECORD_KEYS, \
        (f"the red record's keys changed: added {sorted(set(record) - support.RECORD_KEYS)}, "
         f"lost {sorted(support.RECORD_KEYS - set(record))}")


def test_a_red_night_runs_the_red_alone_and_bisects_it_to_the_culprit(nights):
    support.red(nights.red_run)
    record, _ = support.record_of(nights.red_project, nights.red_run)
    project = nights.red_project
    assert record.get("base") == project.initial, f"the base is not the last green night's head: {record}"
    failures = [f for f in record.get("failures") or [] if f.get("test") == support.RED_TEST]
    assert failures and failures[0].get("alone") == "failed" and failures[0].get("class") == support.RED, \
        f"the red is not named and run again alone: {record.get('failures')}"
    bisects = [p for p in record.get("packages") or [] if p.get("kind") == "bisect" and p.get("test") == support.RED_TEST]
    assert bisects and bisects[0].get("priority") == "P1", f"no P1 bisect package: {record.get('packages')}"
    assert bisects[0].get("first_bad") == project.culprit, \
        f"the bisect did not find the culprit {project.culprit}: {bisects[0]}"
    told = project.told_runs()
    assert len(told.get(support.RED_CASE, [])) >= 2, f"the red test did not run in the suite and again alone: {told}"


@pytest.mark.parametrize("which", ["green", "red"])
def test_the_clone_is_gone_after_the_night_its_folder_its_registration_and_its_entry(nights, which):
    project = nights.green_project if which == "green" else nights.red_project
    clone, entry = project.clone()
    assert not clone.exists(), f"the clone's folder {clone} is still there after the {which} night"
    assert not support.is_registered(project.root, clone), f"the clone {clone} is still registered"
    assert not entry.exists(), f"the clone's administrative entry {entry} is still there"
