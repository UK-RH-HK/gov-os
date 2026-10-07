"""The test runs of a close and what its close record holds."""
from __future__ import annotations

import os
from types import SimpleNamespace

import pytest
import yaml

from gov.cli.errors import GovError
from gov.close.command import NOT_MEASURED, _read_skill_versions, _run_tests, _write_close_record


def _tests(root, **files):
    for name, text in files.items():
        path = root / "tests" / "unit" / f"{name}.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root / "tests"


def test_a_passing_run_has_no_finding_and_its_counts(tmp_path):
    tests = _tests(tmp_path, test_a="def test_a():\n    assert True\n")
    assert _run_tests(tmp_path, tests, 60) == ([], {"passed": 1, "failed": 0, "errors": 0, "skipped": 0})


def test_every_failing_test_is_a_finding(tmp_path):
    tests = _tests(tmp_path, test_a="def test_a():\n    assert False\n\n\ndef test_b():\n    assert False\n",
                   test_c="def test_c():\n    assert True\n")
    findings, counts = _run_tests(tmp_path, tests, 60)
    assert len(findings) == 2 and "test_a" in findings[0] and "test_b" in findings[1]
    assert counts == {"passed": 1, "failed": 2, "errors": 0, "skipped": 0}


def test_a_collection_error_is_a_finding(tmp_path):
    findings, counts = _run_tests(tmp_path, _tests(tmp_path, test_a="def test_a(:\n"), 60)
    assert findings and counts["errors"] >= 1


def test_a_run_over_the_time_limit_is_a_finding_not_an_error(tmp_path):
    tests = _tests(tmp_path, test_slow="import time\n\n\ndef test_slow():\n    time.sleep(999)\n")
    findings, counts = _run_tests(tmp_path, tests, 1)
    assert findings == ["the test run of tests exceeded the time limit of 1s"]
    assert counts == {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}


def test_no_test_collected_is_a_finding_unless_the_run_may_be_empty(tmp_path):
    tests = _tests(tmp_path, helper="x = 1\n")
    assert _run_tests(tmp_path, tests, 60)[0] == ["no test was collected in tests"]
    assert _run_tests(tmp_path, tests, 60, none_collected_ok=True)[0] == []


def test_the_ignored_folder_is_not_run(tmp_path):
    tests = _tests(tmp_path, test_a="def test_a():\n    assert False\n")
    assert _run_tests(tmp_path, tests, 60, ignore=tests / "unit", none_collected_ok=True)[0] == []


def test_the_environment_of_the_run_is_the_callers_with_the_projects_src_alone_on_the_path(tmp_path, monkeypatch):
    """Nothing but ``PYTHONPATH`` is set for the test run, and it is the project's ``src/`` alone: the caller's
    is not passed on. Of the variables that speak to Python, the caller's are passed on only where they say
    where installed packages are and where compiled files go (DEC-500)."""
    seen = {}

    def fake_run(cmd, **keys):
        seen.update(keys["env"])
        return SimpleNamespace(returncode=0, stdout="1 passed in 0.01s\n", stderr="")

    for name in [name for name in os.environ if name.startswith("PYTHON")]:
        monkeypatch.delenv(name)
    places = {"PYTHONUSERBASE": "/base", "PYTHONPYCACHEPREFIX": "/compiled", "PYTHONDONTWRITEBYTECODE": "1"}
    switches = {"PYTHONPATH": "/elsewhere", "PYTHONOPTIMIZE": "1", "PYTHONWARNINGS": "ignore",
                "PYTHONHOME": "/another", "PYTHONSTARTUP": "/a/file.py", "PYTHONNOUSERSITE": "1"}
    for name, value in (places | switches).items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr("gov.close.command.subprocess.run", fake_run)
    before = {name: value for name, value in os.environ.items() if name not in switches}
    _run_tests(tmp_path, _tests(tmp_path, test_a=""), 60)
    assert seen == before | {"PYTHONPATH": str(tmp_path / "src")}
    assert places.items() <= seen.items() and os.environ["PYTHONOPTIMIZE"] == "1"


@pytest.mark.parametrize("level", ["1", "2"])
def test_the_switch_that_removes_assertions_does_not_reach_the_run(tmp_path, monkeypatch, level):
    """The ``assert`` of a module a test imports is compiled away under the switch; the run is made without it."""
    monkeypatch.setenv("PYTHONOPTIMIZE", level)
    tests = _tests(tmp_path, helper_of_a="def must_be_one(value):\n    assert value == 1\n",
                   test_a="from helper_of_a import must_be_one\n\n\ndef test_a():\n    must_be_one(2)\n")
    findings, counts = _run_tests(tmp_path, tests, 60)
    assert counts["failed"] == 1 and any("test_a" in finding for finding in findings)


def test_skipped_tests_are_counted_and_are_no_finding(tmp_path):
    skips = ("import pytest\n\n\n@pytest.mark.skip(reason='not here')\ndef test_one():\n    assert False\n\n\n"
             "def test_two():\n    pytest.skip('not here')\n")
    tests = _tests(tmp_path, test_a="def test_a():\n    assert True\n", test_skips=skips)
    assert _run_tests(tmp_path, tests, 60) == ([], {"passed": 1, "failed": 0, "errors": 0, "skipped": 2})
    failing = _tests(tmp_path / "other", test_a="def test_a():\n    assert False\n", test_skips=skips)
    findings, counts = _run_tests(tmp_path / "other", failing, 60)
    assert len(findings) == 1 and counts == {"passed": 0, "failed": 1, "errors": 0, "skipped": 2}


def test_a_test_runner_this_process_had_from_the_callers_path_alone_is_absent_not_a_finding(tmp_path, monkeypatch):
    monkeypatch.setattr("gov.close.command.subprocess.run", lambda cmd, **keys: SimpleNamespace(
        returncode=1, stdout="", stderr="/usr/bin/python3: No module named pytest\n"))
    with pytest.raises(GovError) as raised:
        _run_tests(tmp_path, _tests(tmp_path, test_a=""), 60)
    assert raised.value.code == "TEST_RUNNER_ABSENT" and "PYTHONPATH" in raised.value.message


def test_an_interpreter_without_pytest_is_an_error_and_no_test_is_run(tmp_path, monkeypatch):
    monkeypatch.setattr("importlib.util.find_spec", lambda name: None)
    monkeypatch.setattr("gov.close.command.subprocess.run", lambda *a, **k: pytest.fail("a test run was started"))
    with pytest.raises(GovError) as raised:
        _run_tests(tmp_path, _tests(tmp_path, test_a=""), 60)
    assert (raised.value.code, raised.value.exit_code) == ("TEST_RUNNER_ABSENT", 1)


RECORD = {"packet_hash": "ab" * 32, "commits": [{"commit": "c" * 40, "role": "engineer", "model": NOT_MEASURED}]}


def test_the_close_record_holds_what_it_is_given_and_its_outputs(tmp_path):
    rel = _write_close_record(tmp_path, "T-1", RECORD, ["src/a.py"], "docs/checkpoints/T-1/CP.md")
    assert rel == "docs/close/T-1/CL-T-1.md"
    front = yaml.safe_load((tmp_path / rel).read_text(encoding="utf-8").split("---")[1])
    assert front["type"] == "close" and front["task"] == "T-1"
    assert front["outputs"] == ["src/a.py", rel, "docs/checkpoints/T-1/CP.md"]
    assert RECORD.items() <= front.items()
    assert "governance_checks" not in front and "check_commit" not in front


def test_a_close_record_that_cannot_be_written_is_an_error(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "close").write_text("a file where the folder goes\n", encoding="utf-8")
    with pytest.raises(OSError):
        _write_close_record(tmp_path, "T-1", RECORD, [], "")


def test_skills_are_listed_with_the_version_read(tmp_path):
    kernel = tmp_path / "template" / "governance" / "kernel"
    for rel, text in (("skills/a/SKILL.md", '---\nname: alpha\nversion: "1.2"\n---\n'),
                      ("skills/b/SKILL.md", "---\nname: beta\n---\n"),
                      ("skills/c/SKILL.md", "no frontmatter\n"),
                      ("vendor/pack/skills/v/SKILL.md", '---\nname: vendored\nversion: "9"\n---\n')):
        (kernel / rel).parent.mkdir(parents=True)
        (kernel / rel).write_text(text, encoding="utf-8")
    assert _read_skill_versions(tmp_path) == [
        {"name": "alpha", "version": "1.2"}, {"name": "beta", "version": "no version"},
        {"name": "c", "version": NOT_MEASURED}, {"name": "vendored", "version": "no version"}]
    assert _read_skill_versions(tmp_path / "elsewhere") == []
