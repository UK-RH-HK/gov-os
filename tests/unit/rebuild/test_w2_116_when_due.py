"""``gov rebuild --integration <branch> --when-due`` (W2-116 pass 2b, S2; P-W2-116-S2-INTERFACE Q1 (a), DEC-1157 (12)):
the settings, the clock, the due rules, the record, ``not_due``.

Regression evidence only (MR-3). The refresh itself is a stand-in (its own cases are ``test_w2_116_integration.py``'s):
here only whether, when and with what reason it is called, and what is written. The clock is ``GOV_NOW``; a verdict
file's time is planted with ``os.utime``.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta

import pytest

from gov.cli.errors import GovError
from gov.rebuild import integration
from gov.rebuild.command import add_arguments, run

HEAD = "a1b2c3d4e5f6" + "0" * 28
SETTINGS = integration.Refresh("integrate", "verdicts/*.txt", (10, 0), (18, 0))
DAY = "2026-11-13"


def _at(text: str) -> datetime:
    return datetime.fromisoformat(text).astimezone()


def _args(*given):
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    return parser.parse_args(list(given))


def _yaml(link, refresh: str | None) -> str:
    return f"integration_store: {link}\n" + ("" if refresh is None else refresh)


GOOD = ("integration_refresh:\n  branch: integrate\n  after_nightly:\n    verdict: verdicts/*.txt\n"
        "    latest: \"10:00\"\n  second: \"18:00\"\n")


_MP: list = []


def _now(value: str) -> None:
    _MP[-1].setenv("GOV_NOW", value)


@pytest.fixture(autouse=True)
def _patch(monkeypatch):
    _MP.append(monkeypatch)
    yield
    _MP.pop()


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A project folder with the configuration above and the refresh a stand-in that records its calls."""
    root = tmp_path / "project"
    (root / "governance" / "project").mkdir(parents=True)
    link = tmp_path / "stores" / "store"
    (root / "governance" / "project" / "rebuild.yaml").write_text(_yaml(link, GOOD), encoding="utf-8")
    monkeypatch.setenv("GOV_NOW", f"{DAY}T12:00:00+00:00")
    calls = []
    state = {"status": "switched", "fails": False}

    def refresh(where, branch):
        calls.append((where, branch))
        link.parent.mkdir(parents=True, exist_ok=True)  # the real refresh makes it for its lock
        if state["fails"]:
            raise GovError("REBUILD_FAILED", "the build failed", {"branch": branch})
        return {"integration": {"branch": branch, "head": HEAD, "link": str(link), "ready": "x", "status":
                                state["status"]}}

    monkeypatch.setattr(integration, "refresh", refresh)
    return root, link, calls, state


def _config(root, link, refresh: str | None):
    (root / "governance" / "project" / "rebuild.yaml").write_text(_yaml(link, refresh), encoding="utf-8")


def _verdict(root, name: str, text: str, when: str):
    path = root / "verdicts" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(text, encoding="utf-8")
    stamp = _at(when).timestamp()
    os.utime(path, (stamp, stamp))


def _record(link, **fields):
    link.parent.mkdir(parents=True, exist_ok=True)
    record = {"at": f"{DAY}T10:00:00+00:00", "reason": "after_nightly", "head": HEAD, "status": "switched",
              "branch": "integrate"} | fields
    integration.record_path(link).write_text(json.dumps(record), encoding="utf-8")
    return record


def _run(root, *extra):
    return run(root, _args("--integration", "integrate", "--when-due", *extra), {})


def _read(link):
    return json.loads(integration.record_path(link).read_text(encoding="utf-8"))


# the settings ----------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("refresh, key, value", [
    (None, "integration_refresh", None),
    ("integration_refresh:\n", "integration_refresh", None),
    ("integration_refresh: soon\n", "integration_refresh", "soon"),
    ("integration_refresh:\n  after_nightly: {latest: \"10:00\"}\n  second: \"18:00\"\n",
     "integration_refresh.branch", None),
    ("integration_refresh:\n  branch: ''\n  after_nightly: {latest: \"10:00\"}\n  second: \"18:00\"\n",
     "integration_refresh.branch", ""),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\"}\n",
     "integration_refresh.second", None),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\"}\n  second: ''\n",
     "integration_refresh.second", ""),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\"}\n  second: 1800\n",
     "integration_refresh.second", 1800),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\"}\n  second: 18:00\n",
     "integration_refresh.second", 1080),  # unquoted, YAML reads it as base 60: not a string
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\"}\n  second: \"25:00\"\n",
     "integration_refresh.second", "25:00"),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\"}\n  second: \"18:60\"\n",
     "integration_refresh.second", "18:60"),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\"}\n  second: \"9:5\"\n",
     "integration_refresh.second", "9:5"),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\"}\n  second: \"10am\"\n",
     "integration_refresh.second", "10am"),
    ("integration_refresh:\n  branch: integrate\n  second: \"18:00\"\n",
     "integration_refresh.after_nightly.latest", None),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {}\n  second: \"18:00\"\n",
     "integration_refresh.after_nightly.latest", None),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"24:00\"}\n  second: \"18:00\"\n",
     "integration_refresh.after_nightly.latest", "24:00"),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: [10, 0]}\n  second: \"18:00\"\n",
     "integration_refresh.after_nightly.latest", [10, 0]),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\", verdict: ''}\n"
     "  second: \"18:00\"\n", "integration_refresh.after_nightly.verdict", ""),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\", verdict: 7}\n"
     "  second: \"18:00\"\n", "integration_refresh.after_nightly.verdict", 7),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: late\n  second: \"18:00\"\n",
     "integration_refresh.after_nightly", "late"),
])
def test_a_missing_or_invalid_setting_refuses_by_its_key_and_builds_nothing(project, refresh, key, value):
    root, link, calls, _ = project
    _config(root, link, refresh)
    with pytest.raises(GovError) as raised:
        _run(root)
    error = raised.value
    assert error.code == "REBUILD_CONFIG_INVALID"
    assert error.details == {"key": key, "value": value}
    assert key in error.message
    assert calls == [] and not integration.record_path(link).exists()


def test_no_rebuild_yaml_at_all_refuses_for_the_missing_block(project):
    root, _, calls, _ = project
    (root / "governance" / "project" / "rebuild.yaml").unlink()
    with pytest.raises(GovError) as raised:
        _run(root)
    assert raised.value.code == "REBUILD_CONFIG_INVALID" and raised.value.details["key"] == "integration_refresh"
    assert calls == []


def test_a_file_that_is_not_yaml_refuses_for_the_block(project):
    root, _, calls, _ = project
    (root / "governance" / "project" / "rebuild.yaml").write_text("integration_refresh: [unclosed\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        _run(root)
    assert raised.value.code == "REBUILD_CONFIG_INVALID" and raised.value.details["key"] == "integration_refresh"
    assert calls == []


def test_the_verdict_glob_defaults_to_the_nightly_reports(project):
    root, link, _, _ = project
    _config(root, link, "integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\"}\n"
                        "  second: \"18:00\"\n")
    assert integration.refresh_settings(root).verdict == "docs/close/nightly/NR-*.json"


def test_this_repository_s_own_line_reads(tmp_path):
    from pathlib import Path

    own = integration.refresh_settings(Path(__file__).resolve().parents[3])
    assert own == integration.Refresh("w2/integrate", ".gov-runtime/scratch/orchestrator/log/nightly/*/run.txt",
                                      (10, 0), (18, 0))


# the clock -------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("given", ["", "noon", "2026-13-01T00:00:00", "12:00", "2026-11-13T25:00:00"])
def test_an_invalid_gov_now_refuses_by_name_and_builds_nothing(project, monkeypatch, given):
    root, link, calls, _ = project
    monkeypatch.setenv("GOV_NOW", given)
    with pytest.raises(GovError) as raised:
        _run(root)
    assert raised.value.code == "REBUILD_CONFIG_INVALID" and raised.value.details == {"key": "GOV_NOW", "value": given}
    assert calls == [] and not integration.record_path(link).exists()


def test_gov_now_with_an_offset_is_that_instant_and_that_wall_clock(monkeypatch):
    monkeypatch.setenv("GOV_NOW", "2026-11-13T23:30:00-05:00")
    now = integration.now()
    assert now == datetime.fromisoformat("2026-11-14T04:30:00+00:00")
    assert integration.at_time(now, (18, 0)).isoformat() == "2026-11-13T18:00:00-05:00"  # that offset's date


def test_gov_now_without_an_offset_is_local_time(monkeypatch):
    monkeypatch.setenv("GOV_NOW", "2026-11-13T09:30:00")
    now = integration.now()
    assert now == datetime(2026, 11, 13, 9, 30).astimezone() and now.utcoffset() is not None


def test_without_gov_now_it_is_the_real_clock(monkeypatch):
    monkeypatch.delenv("GOV_NOW", raising=False)
    before = datetime.now().astimezone() - timedelta(seconds=1)
    assert before <= integration.now() <= datetime.now().astimezone() + timedelta(seconds=1)


# the due rules ---------------------------------------------------------------------------------------------------------

def _due(now: str, record=None, verdicts=()):
    return integration.due_reason(SETTINGS, datetime.fromisoformat(now), record, [_at(when) for when in verdicts])


def _rec(at: str, reason: str = "after_nightly") -> dict:
    return {"at": at, "reason": reason}


@pytest.mark.parametrize("now, record, verdicts, expected", [
    # no record: the edge minutes of ``latest``, then ``second``
    (f"{DAY}T09:59:59+00:00", None, (), None),
    (f"{DAY}T10:00:00+00:00", None, (), "after_nightly"),
    (f"{DAY}T10:00:00+00:00", _rec(f"{DAY}T09:00:00+00:00"), (), None),  # an after_nightly today stands for ``latest``
    (f"{DAY}T17:59:59+00:00", _rec(f"{DAY}T10:00:00+00:00"), (), None),
    (f"{DAY}T18:00:00+00:00", _rec(f"{DAY}T10:00:00+00:00"), (), "second"),
    (f"{DAY}T18:00:00+00:00", None, (), "after_nightly"),  # both due: the nightly's reason
    (f"{DAY}T23:59:00+00:00", _rec(f"{DAY}T18:00:00+00:00", "second"), (), "after_nightly"),  # no after_nightly today
    (f"{DAY}T23:59:00+00:00", _rec(f"{DAY}T18:00:01+00:00"), (), None),
    # ``second``: the record at or after it is no refresh due, one before it is
    (f"{DAY}T18:00:00+00:00", _rec(f"{DAY}T17:59:59+00:00"), (), "second"),
    (f"{DAY}T18:30:00+00:00", _rec(f"{DAY}T18:00:00+00:00"), (), None),
    (f"{DAY}T18:30:00+00:00", _rec(f"{DAY}T10:05:00+00:00"), (), "second"),
    # yesterday's times and records are never today's
    (f"{DAY}T09:00:00+00:00", _rec("2026-11-12T10:00:00+00:00"), (), None),
    (f"{DAY}T09:00:00+00:00", _rec("2026-11-12T18:00:00+00:00", "second"), (), None),
    (f"{DAY}T10:00:00+00:00", _rec("2026-11-12T18:00:00+00:00", "second"), (), "after_nightly"),
    (f"{DAY}T10:00:00+00:00", _rec("2026-11-12T10:00:00+00:00"), (), "after_nightly"),
    (f"{DAY}T00:00:00+00:00", _rec("2026-11-12T23:00:00+00:00"), (), None),
    # a counting verdict file later than the record's ``at``, or any with no record
    (f"{DAY}T03:00:00+00:00", None, (f"{DAY}T02:00:00+00:00",), "after_nightly"),
    (f"{DAY}T03:00:00+00:00", _rec("2026-11-12T10:00:00+00:00"), (f"{DAY}T02:00:00+00:00",), "after_nightly"),
    (f"{DAY}T03:00:00+00:00", _rec("2026-11-12T10:00:00+00:00"), ("2026-11-12T09:59:59+00:00",), None),
    (f"{DAY}T03:00:00+00:00", _rec(f"{DAY}T02:00:00+00:00"), (f"{DAY}T02:00:00+00:00",), None),  # not later: equal
    (f"{DAY}T03:00:00+00:00", _rec(f"{DAY}T02:00:00+00:00"), (f"{DAY}T02:00:01+00:00",), "after_nightly"),
    (f"{DAY}T12:00:00+00:00", _rec(f"{DAY}T10:00:00+00:00"), (f"{DAY}T11:00:00+00:00",), "after_nightly"),
    (f"{DAY}T12:00:00+00:00", _rec(f"{DAY}T10:00:00+00:00"), (f"{DAY}T09:00:00+00:00",), None),
    # the dates are those of ``now``'s offset: 23:00 at -05:00 is 04:00 UTC on the 14th
    ("2026-11-13T23:30:00-05:00", _rec("2026-11-14T03:00:00+00:00"), (), None),  # 22:00 on the 13th at -05:00
    ("2026-11-13T23:30:00-05:00", _rec("2026-11-14T06:00:00+00:00"), (), "after_nightly"),  # 01:00 on the 14th: no
    ("2026-11-13T17:59:00-05:00", _rec("2026-11-13T10:00:00-05:00"), (), None),
    ("2026-11-13T18:00:00-05:00", _rec("2026-11-13T10:00:00-05:00"), (), "second"),
    # the record's ``after_nightly_at`` is the last scheduled after_nightly refresh, whatever the last refresh was
    (f"{DAY}T18:30:00+00:00", {"at": f"{DAY}T18:00:00+00:00", "reason": "second",
                               "after_nightly_at": f"{DAY}T10:00:00+00:00"}, (), None),
    (f"{DAY}T10:30:00+00:00", {"at": f"{DAY}T10:15:00+00:00", "reason": "second",
                               "after_nightly_at": "2026-11-12T10:00:00+00:00"}, (), "after_nightly"),
    # a verdict file stamped after ``now`` does not count yet
    (f"{DAY}T03:00:00+00:00", None, (f"{DAY}T03:00:01+00:00",), None),
    # a record that holds no readable ``at`` is no record
    (f"{DAY}T09:00:00+00:00", {"at": "tomorrow", "reason": "second"}, (), None),
    (f"{DAY}T12:00:00+00:00", {"at": 5}, (), "after_nightly"),
])
def test_the_due_rules(now, record, verdicts, expected):
    assert _due(now, record, verdicts) == expected


def test_a_verdict_file_without_a_verdict_does_not_count(project):
    root, link, calls, _ = project
    monkey_now = f"{DAY}T09:00:00+00:00"
    _now(monkey_now)
    _verdict(root, "running.txt", "nightly 2026-11-13\nstep 3 of 9\nverdict is not yet known\n", f"{DAY}T08:00:00+00:00")
    _record(link, at="2026-11-12T10:00:00+00:00")
    result = _run(root)
    assert result["integration"]["status"] == "not_due" and calls == []


@pytest.mark.parametrize("text", ["nightly\nverdict: PASS\n", "verdict: FAIL", '{"verdict": "pass", "n": 3}'])
def test_a_verdict_line_or_a_json_verdict_counts(project, text):
    root, link, calls, _ = project
    _now(f"{DAY}T09:00:00+00:00")
    _verdict(root, "run.txt", text, f"{DAY}T08:00:00+00:00")
    _record(link, at="2026-11-12T10:00:00+00:00")
    assert _run(root)["integration"]["reason"] == "after_nightly" and len(calls) == 1


@pytest.mark.parametrize("text", ["  verdict: PASS\n", "the verdict: PASS\n", '{"result": "pass"}', "[1]", ""])
def test_text_that_is_no_verdict_line_or_json_verdict_does_not_count(project, text):
    root, link, calls, _ = project
    _now(f"{DAY}T09:00:00+00:00")
    _verdict(root, "run.txt", text, f"{DAY}T08:00:00+00:00")
    _record(link, at="2026-11-12T10:00:00+00:00")
    assert _run(root)["integration"]["status"] == "not_due" and calls == []


def test_the_newest_counting_verdict_file_of_several_is_the_one_that_counts(project):
    root, link, calls, _ = project
    _now(f"{DAY}T09:00:00+00:00")
    _verdict(root, "old.txt", "verdict: PASS\n", "2026-11-12T03:00:00+00:00")
    _verdict(root, "new.txt", "verdict: PASS\n", f"{DAY}T05:00:00+00:00")
    _verdict(root, "other.log", "verdict: PASS\n", f"{DAY}T08:00:00+00:00")  # outside the glob
    _record(link, at=f"{DAY}T06:00:00+00:00")
    assert _run(root)["integration"]["status"] == "not_due" and calls == []
    _verdict(root, "newer.txt", "verdict: PASS\n", f"{DAY}T06:00:01+00:00")
    assert _run(root)["integration"]["reason"] == "after_nightly" and len(calls) == 1


# the command -----------------------------------------------------------------------------------------------------------

def test_not_due_builds_and_writes_nothing_and_succeeds_with_the_record_or_null(project):
    root, link, calls, _ = project
    _now(f"{DAY}T09:00:00+00:00")
    assert _run(root) == {"integration": {"status": "not_due", "branch": "integrate", "link": str(link),
                                          "last_refresh": None}}
    assert not integration.record_path(link).exists() and calls == []
    record = _record(link, at="2026-11-12T10:00:00+00:00")
    before = integration.record_path(link).read_bytes()
    assert _run(root)["integration"]["last_refresh"] == record
    assert integration.record_path(link).read_bytes() == before and calls == []


def test_due_runs_the_refresh_names_its_reason_and_writes_the_record_whole(project):
    root, link, calls, state = project
    _now(f"{DAY}T10:00:00+01:00")
    result = _run(root)
    assert calls == [(root, "integrate")]
    assert result["integration"]["reason"] == "after_nightly" and result["integration"]["status"] == "switched"
    assert _read(link) == {"at": f"{DAY}T10:00:00+01:00", "reason": "after_nightly", "head": HEAD,
                           "status": "switched", "branch": "integrate",
                           "after_nightly_at": f"{DAY}T10:00:00+01:00"}
    assert not list(link.parent.glob(".*tmp")), "the record is replaced, no temporary file is left"


def test_an_unchanged_head_is_a_refresh_that_is_recorded_too(project):
    root, link, calls, state = project
    state["status"] = "unchanged"
    _now(f"{DAY}T18:10:00+00:00")
    _record(link, at=f"{DAY}T10:00:00+00:00")
    result = _run(root)
    assert result["integration"]["reason"] == "second" and result["integration"]["status"] == "unchanged"
    assert _read(link)["reason"] == "second" and _read(link)["status"] == "unchanged"
    assert _read(link)["at"] == f"{DAY}T18:10:00+00:00"
    assert _read(link)["after_nightly_at"] == f"{DAY}T10:00:00+00:00"  # carried over by the second refresh
    assert _run_when(root, f"{DAY}T18:15:00+00:00")["integration"]["status"] == "not_due"  # the next tick


def test_the_record_carries_the_last_after_nightly_at_and_a_second_refresh_keeps_it(project):
    root, link, calls, _ = project
    _now(f"{DAY}T10:00:00+01:00")
    _run(root)
    assert _read(link)["after_nightly_at"] == f"{DAY}T10:00:00+01:00" == _read(link)["at"]
    _now(f"{DAY}T18:00:00+01:00")
    _run(root)
    assert _read(link)["reason"] == "second" and _read(link)["at"] == f"{DAY}T18:00:00+01:00"
    assert _read(link)["after_nightly_at"] == f"{DAY}T10:00:00+01:00"
    assert _run_when(root, f"{DAY}T18:05:00+01:00")["integration"]["status"] == "not_due"
    assert len(calls) == 2


def _run_when(root, now):
    _now(now)
    return _run(root)


def test_both_due_is_one_refresh_with_the_nightly_s_reason(project):
    root, link, calls, _ = project
    _now(f"{DAY}T19:00:00+00:00")
    assert _run(root)["integration"]["reason"] == "after_nightly" and len(calls) == 1


def test_a_failed_refresh_refuses_as_before_and_leaves_the_record_so_the_next_tick_is_due_again(project):
    root, link, calls, state = project
    record = _record(link, at="2026-11-12T10:00:00+00:00")
    state["fails"] = True
    _now(f"{DAY}T10:30:00+00:00")
    with pytest.raises(GovError) as raised:
        _run(root)
    assert raised.value.code == "REBUILD_FAILED" and _read(link) == record
    state["fails"] = False
    assert _run(root)["integration"]["reason"] == "after_nightly" and _read(link)["at"] == f"{DAY}T10:30:00+00:00"


def test_the_record_is_written_after_a_refresh_that_took_long_with_the_time_it_was_decided_at(project, monkeypatch):
    root, link, _, _ = project
    _now(f"{DAY}T10:00:00+00:00")
    inner = integration.refresh

    def slow(where, branch):
        _now(f"{DAY}T11:30:00+00:00")  # the clock moves on while it builds
        return inner(where, branch)

    monkeypatch.setattr(integration, "refresh", slow)
    _run(root)
    assert _read(link)["at"] == f"{DAY}T10:00:00+00:00"


def test_a_record_that_cannot_be_written_is_a_failure_that_names_it(project):
    root, link, _, _ = project
    link.parent.mkdir(parents=True)
    integration.record_path(link).mkdir()  # a folder where the record's file goes
    _now(f"{DAY}T10:00:00+00:00")
    with pytest.raises(GovError) as raised:
        _run(root)
    assert raised.value.code == "REBUILD_FAILED" and "refresh.json" in raised.value.message


def test_when_due_without_integration_is_the_usage_refusal(project):
    root, link, calls, _ = project
    with pytest.raises(GovError) as raised:
        run(root, _args("--when-due"), {})
    assert raised.value.code == "REBUILD_FAILED" and "--when-due" in raised.value.message and calls == []


def test_a_plain_refresh_never_reads_the_times_and_never_writes_the_record(project):
    root, link, calls, _ = project
    _config(root, link, "integration_refresh:\n  branch: integrate\n  second: \"25:00\"\n")  # invalid: never read
    _now("noon")  # invalid: never read
    result = run(root, _args("--integration", "integrate"), {})
    assert calls == [(root, "integrate")] and "reason" not in result["integration"]
    assert not integration.record_path(link).exists()


def test_the_flag_is_in_the_parser_and_takes_no_value():
    assert _args("--integration", "b", "--when-due").when_due is True
    assert _args("--integration", "b").when_due is False


# the last time a refresh fell due (``gov status``'s) ---------------------------------------------------------------------

def _last(now: str, verdicts=()):
    found = integration.last_due(SETTINGS, _at(now), [_at(when) for when in verdicts])
    return None if found is None else found[0].isoformat()


@pytest.mark.parametrize("now, verdicts, expected", [
    (f"{DAY}T09:00:00+00:00", (), "2026-11-12T18:00:00+00:00"),  # yesterday's second
    (f"{DAY}T10:00:00+00:00", (), f"{DAY}T10:00:00+00:00"),  # today's latest, no verdict before it
    (f"{DAY}T17:59:00+00:00", (), f"{DAY}T10:00:00+00:00"),
    (f"{DAY}T18:00:00+00:00", (), f"{DAY}T18:00:00+00:00"),
    (f"{DAY}T12:00:00+00:00", (f"{DAY}T09:00:00+00:00",), f"{DAY}T09:00:00+00:00"),  # a verdict, so no latest today
    (f"{DAY}T12:00:00+00:00", (f"{DAY}T10:30:00+00:00",), f"{DAY}T10:30:00+00:00"),
    (f"{DAY}T12:00:00+00:00", (f"{DAY}T09:00:00+00:00",) , f"{DAY}T09:00:00+00:00"),
    (f"{DAY}T19:00:00+00:00", (f"{DAY}T09:00:00+00:00",), f"{DAY}T18:00:00+00:00"),  # the second is the later
    (f"{DAY}T09:00:00+00:00", ("2026-11-12T08:00:00+00:00",), "2026-11-12T18:00:00+00:00"),
    (f"{DAY}T09:00:00+00:00", ("2026-11-12T19:00:00+00:00",), "2026-11-12T19:00:00+00:00"),  # newer than yesterday's
    (f"{DAY}T03:00:00+00:00", (f"{DAY}T04:00:00+00:00",), "2026-11-12T18:00:00+00:00"),  # a verdict after now: none yet
    (f"{DAY}T10:00:00+00:00", (f"{DAY}T10:00:00+00:00",), f"{DAY}T10:00:00+00:00"),
])
def test_the_last_time_a_refresh_fell_due(now, verdicts, expected):
    assert _last(now, verdicts) == expected


def test_a_verdict_on_a_date_before_its_latest_withdraws_that_dates_latest_only():
    now = [f"{DAY}T10:30:00+00:00"]
    # yesterday had a verdict at 09:00 (before its latest): its latest does not count; today has none
    verdicts = ("2026-11-12T09:00:00+00:00",)
    assert _last(now[0], verdicts) == f"{DAY}T10:00:00+00:00"
    assert _last(f"{DAY}T09:30:00+00:00", verdicts) == "2026-11-12T18:00:00+00:00"
