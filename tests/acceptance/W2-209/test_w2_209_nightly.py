"""S11: the nightly runner's weekly tier as an option G2 reads.

A planted project (a git repository of its own, branch ``main``) holds one telling test: each run appends the
``GOV_TESTS_OPTIN`` it sees to a file outside the project. ``python3 -m gov.close.nightly main --root <project>
[--optin <name>] --json`` and ``gov.close.nightly.night(root, "main", rebuild=False, optin=...)`` run on it; the record
(``docs/close/nightly/NR-*.json``) must carry ``optin``, the sorted suites the run opted in to. README, "S11".
"""

import json
import sys

import w2_209_support as support


def _project(tmp_path):
    told = tmp_path / "told.jsonl"
    project = tmp_path / "project"
    project.mkdir()
    support.git(project, "init", "-q", "-b", "main")
    support.git(project, "config", "user.name", "W2-209 tests")
    support.git(project, "config", "user.email", "w2-209@example.invalid")
    support.commit(project, {
        ".gitignore": ".gov-runtime/\n__pycache__/\n",
        "tests/test_told.py": ("import json\nimport os\n\n\ndef test_told():\n"
                               f"    with open({str(told)!r}, 'a', encoding='utf-8') as handle:\n"
                               "        handle.write(json.dumps({'optin': os.environ.get('GOV_TESTS_OPTIN')}) + '\\n')\n"),
    }, "a planted project with one telling test")
    home = tmp_path / "home"
    (home / "tmp").mkdir(parents=True)
    return project, told, home


def _told(told):
    return support.read_jsonl(told)


def _records(project):
    return sorted((project / support.NIGHTLY_REL).glob("NR-*.json"))


def _cli(project, home, *args, extra=None):
    return support.run((sys.executable, "-m", "gov.close.nightly", "main", "--root", str(project), *args, "--json"),
                       project, support.environment(home, extra=extra))


def _cli_record(run, project):
    envelope = run.envelope()
    assert envelope.get("ok") is True, f"the planted night is not green\n{run.describe()}"
    return json.loads((project / envelope["result"]["record"]).read_text(encoding="utf-8"))


def _night(project, home, extra=None, **kwargs):
    out = support.call(home, "gov.close.nightly:night", [support.path_arg(project), "main"],
                       {"rebuild": False, **kwargs}, extra=extra)
    return out.returned("gov.close.nightly.night")


def _seen(told):
    lines = _told(told)
    assert lines, "the planted test did not run"
    value = lines[-1]["optin"]
    return None if value is None else sorted(part for part in value.split(",") if part)


def test_s11_the_optin_option_runs_the_weekly_tier_and_records_it(tmp_path):
    project, told, home = _project(tmp_path)
    record = _cli_record(_cli(project, home, "--optin", "weekly"), project)
    assert _seen(told) == ["weekly"], f"the tests saw GOV_TESTS_OPTIN={_told(told)[-1]}"
    assert record.get("optin") == ["weekly"], f"the record's optin is {record.get('optin')!r}"


def test_s11_the_option_adds_to_the_callers_variable_and_drops_none(tmp_path):
    project, told, home = _project(tmp_path)
    record = _cli_record(_cli(project, home, "--optin", "weekly", extra={"GOV_TESTS_OPTIN": "lifted"}), project)
    assert _seen(told) == ["lifted", "weekly"], f"the tests saw GOV_TESTS_OPTIN={_told(told)[-1]}"
    assert record.get("optin") == ["lifted", "weekly"], f"the record's optin is {record.get('optin')!r}"


def test_s11_a_run_started_by_hand_with_the_variable_alone_is_recorded(tmp_path):
    project, told, home = _project(tmp_path)
    result = _night(project, home, extra={"GOV_TESTS_OPTIN": "weekly"})
    assert _seen(told) == ["weekly"], f"the tests saw GOV_TESTS_OPTIN={_told(told)[-1]}"
    assert result.get("optin") == ["weekly"], f"the record's optin is {result.get('optin')!r}"


def test_s11_night_takes_the_option_as_a_list(tmp_path):
    project, told, home = _project(tmp_path)
    result = _night(project, home, optin=["weekly"])
    assert _seen(told) == ["weekly"], f"the tests saw GOV_TESTS_OPTIN={_told(told)[-1]}"
    assert result.get("optin") == ["weekly"], f"the record's optin is {result.get('optin')!r}"
    written = json.loads((project / result["record"]).read_text(encoding="utf-8"))
    assert written.get("optin") == ["weekly"], f"the written record's optin is {written.get('optin')!r}"


def test_s11_an_unknown_suite_name_is_refused_before_anything_runs(tmp_path):
    project, told, home = _project(tmp_path)
    run = _cli(project, home, "--optin", "nightly-extra")
    assert run.returncode != 0, f"an unknown suite name was not refused\n{run.describe()}"
    assert "nightly-extra" in run.stdout + run.stderr, f"the refusal does not name the suite\n{run.describe()}"
    assert "unrecognized arguments" not in run.stderr, f"--optin is not an option of the nightly\n{run.describe()}"
    assert not _told(told), "the tests ran for an unknown suite name"
    assert not _records(project), "a record was written for an unknown suite name"


def test_s11_without_option_or_variable_the_record_says_optin_empty(tmp_path):
    project, told, home = _project(tmp_path)
    result = _night(project, home)
    assert _seen(told) is None, f"the tests saw GOV_TESTS_OPTIN={_told(told)[-1]}"
    assert result.get("optin") == [], f"the record's optin is {result.get('optin')!r}, not []"
    assert result.get("scope") == "full" and result.get("verdict") == "green", result
