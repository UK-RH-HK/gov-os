"""W2-96 (DAEO-ouet): builder tests of ``gov accept``, the opaque acceptance runner (DEC-959 item 6).

Each test plants a tiny project in a temporary folder: a ticket, its acceptance folder with a README map
and a few tests. Nothing runs against this repository's own acceptance folders.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from gov.accept import runner
from gov.cli.errors import GovError
from gov.cli.main import main

MARK = "PLANTED-LEAK-7f3a"  # planted in assertions, output and names: must never reach the caller

ROW_README = f"""# Acceptance tests

| KPI | Test | Notes |
|-----|------|-------|
| S1 | `test_one.py` | {MARK} |
| Success 2 / F1 | `test_two.py::test_good`, `bad` | |
| failure 2 | `nothing_here` | |
"""

TEST_ONE = f"""
def test_alpha():
    print("{MARK}")
    assert 1

def test_beta():
    assert True
"""

TEST_TWO = f"""
import pytest

def test_good():
    assert 1

def test_bad():
    assert "{MARK}" == "x", "{MARK}"

@pytest.mark.parametrize("v", ["{MARK}"])
def test_{MARK.replace('-', '_').lower()}(v):
    raise RuntimeError(v)

def test_skipped():
    pytest.skip("{MARK}")
"""


def _plant(root: Path, readme: str | None, tests: dict[str, str], *, path: str | None = "tests/acceptance/T1/",
           ticket: str = "DAEO-t001", wbs: str = "W9-01") -> Path:
    (root / ".tickets").mkdir(parents=True, exist_ok=True)
    lines = ["---", f"id: {ticket}", f"wbs_id: {wbs}", "status: in_progress"]
    if path is not None:
        lines += ["acceptance_tests:", f"  path: {path}"]
    (root / ".tickets" / f"{ticket}.md").write_text("\n".join(lines + ["---", "# t", ""]), encoding="utf-8")
    folder = root / (path or "tests/acceptance/T1/")
    folder.mkdir(parents=True, exist_ok=True)
    if readme is not None:
        (folder / "README.md").write_text(readme, encoding="utf-8")
    for name, text in tests.items():
        (folder / name).write_text(text, encoding="utf-8")
    return folder


def _files(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*")}


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "proj"
    root.mkdir()
    temp = tmp_path / "tmpdir"
    temp.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(temp))
    monkeypatch.setenv("TMPDIR", str(temp))
    return root, temp


def _accept(root: Path, ticket: str, capsys, *extra: str) -> tuple[int, dict, str]:
    code = main(["accept", ticket, "--json", "--root", str(root), *extra])
    out, err = capsys.readouterr()
    return code, json.loads(out), out + err


# --- the README map ----------------------------------------------------------------------------------------------

def test_w2_96_names_in_every_form():
    assert runner.line_names("S1 / K2 and failure 3; F4, kpi 5") == [
        "success-1", "success-2", "failure-3", "failure-4", "success-5"]
    assert runner.line_names("Success 3 — the rest") == ["success-3"]
    assert runner.line_names("K2 — leaks") == ["success-2"]
    assert runner.line_names("Notes about S1") == []
    assert runner.line_names("Source 1") == []


def test_w2_96_row_form_maps_items_to_lines():
    mapping = runner.parse_map(ROW_README)
    assert set(mapping) == {"success-1", "success-2", "failure-1", "failure-2"}
    assert mapping["success-2"] == mapping["failure-1"]
    assert runner.ordered(mapping) == ["success-1", "success-2", "failure-1", "failure-2"]


def test_w2_96_heading_form_and_heading_without_names():
    readme = """
## KPI 1: runs
| Test | What |
|---|---|
| `test_one.py` | x |

### Other matters
| File | What |
|---|---|
| `test_two.py` | y |

### F2 and S3 — refusals
| Test |
|---|
| `test_good` |
"""
    mapping = runner.parse_map(readme)
    assert set(mapping) == {"success-1", "failure-2", "success-3"}


def test_w2_96_tables_in_code_fences_are_ignored():
    assert runner.parse_map("```\n| KPI | Test |\n|---|---|\n| S1 | `a.py` |\n```\n") == {}


def test_w2_96_item_matching():
    case = runner.Case("tests/acceptance/T1/sub/test_x.py", "test_run[a-b]", "passed")
    assert runner.matches("test_x.py", case)
    assert runner.matches("sub/test_x.py", case)
    assert runner.matches("tests/acceptance/T1/sub/test_x.py", case)
    assert not runner.matches("other/test_x.py", case)
    assert runner.matches("test_x.py::test_run", case)
    assert runner.matches("test_x.py::TestK::test_run", case)
    assert not runner.matches("test_x.py::test_other", case)
    assert runner.matches("run", case)
    assert runner.matches("test_run", case)
    assert not runner.matches("ru", case)
    assert not runner.matches("some words", case)


# --- end to end -----------------------------------------------------------------------------------------------------

def test_w2_96_fail_reports_counts_per_line_and_leaks_nothing(project, capsys):
    root, temp = project
    _plant(root, ROW_README, {"test_one.py": TEST_ONE, "test_two.py": TEST_TWO})
    before = _files(root)
    code, envelope, text = _accept(root, "DAEO-t001", capsys)
    assert code == 3
    assert envelope["ok"] is True and envelope["command"] == "accept"
    result = envelope["result"]
    assert result["ticket"] == "DAEO-t001" and result["outcome"] == "fail" and result["error_kind"] is None
    assert result["lines"] == [
        {"kpi": "success-1", "outcome": "pass", "passed": 2, "failed": 0, "skipped": 0},
        {"kpi": "success-2", "outcome": "fail", "passed": 1, "failed": 1, "skipped": 0},
        {"kpi": "failure-1", "outcome": "fail", "passed": 1, "failed": 1, "skipped": 0},
        {"kpi": "failure-2", "outcome": "fail", "passed": 0, "failed": 0, "skipped": 0},
    ]
    assert result["unmapped"] == {"passed": 0, "failed": 1, "skipped": 1}
    assert result["totals"] == {"passed": 3, "failed": 2, "skipped": 1}
    for leak in (MARK, MARK.replace("-", "_").lower(), "test_one", "test_two", "test_bad", "Traceback",
                 "assert", str(root)):
        assert leak not in text
    assert _files(root) == before
    assert list(temp.iterdir()) == []


def test_w2_96_pass_by_wbs_id_with_own_src_and_caller_settings_dropped(project, capsys, monkeypatch):
    root, temp = project
    (root / "src" / "w296pkg").mkdir(parents=True)
    (root / "src" / "w296pkg" / "__init__.py").write_text("VALUE = 7\n")
    test = "import w296pkg\n\ndef test_value():\n    assert w296pkg.VALUE == 7\n"
    _plant(root, "| KPI | File |\n|---|---|\n| K1 | `test_v.py` |\n", {"test_v.py": test})
    monkeypatch.setenv("PYTEST_ADDOPTS", "--no-such-option-w296")
    before = _files(root)
    code, envelope, _ = _accept(root, "W9-01", capsys)
    assert code == 0, envelope
    assert envelope["result"]["outcome"] == "pass"
    assert envelope["result"]["lines"] == [
        {"kpi": "success-1", "outcome": "pass", "passed": 1, "failed": 0, "skipped": 0}]
    assert _files(root) == before
    assert list(temp.iterdir()) == []


def test_w2_96_text_output_is_the_same_result(project, capsys):
    root, _ = project
    _plant(root, "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n", {"test_a.py": "def test_a():\n    pass\n"})
    assert main(["accept", "DAEO-t001", "--root", str(root)]) == 0
    assert json.loads(capsys.readouterr().out)["outcome"] == "pass"


@pytest.mark.parametrize("tests, kind", [
    ({"test_a.py": f"import no_such_module_w296  # {MARK}\n"}, "collection"),
    ({"test_a.py": "x = 1\n"}, "collection"),
    ({"test_a.py": "import os\n\ndef test_a():\n    os._exit(3)\n"}, "crash"),
    ({"test_a.py": "import os, signal\n\ndef test_a():\n    os.kill(os.getpid(), signal.SIGKILL)\n"}, "crash"),
])
def test_w2_96_run_errors_report_kind_only(project, capsys, tests, kind):
    root, temp = project
    _plant(root, "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n", tests)
    code, envelope, text = _accept(root, "DAEO-t001", capsys)
    assert code == 4
    assert envelope["ok"] is True
    assert envelope["result"] == {"ticket": "DAEO-t001", "outcome": "error", "error_kind": kind, "lines": [],
                                  "unmapped": {"passed": 0, "failed": 0, "skipped": 0},
                                  "totals": {"passed": 0, "failed": 0, "skipped": 0}}
    assert MARK not in text and "no_such_module" not in text
    assert list(temp.iterdir()) == []


def test_w2_96_timeout_kills_the_run(project, capsys):
    root, temp = project
    slow = "import subprocess, sys, time\n\ndef test_a():\n" \
           "    subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n    time.sleep(60)\n"
    _plant(root, "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n", {"test_a.py": slow})
    code, envelope, _ = _accept(root, "DAEO-t001", capsys, "--timeout", "3")
    assert code == 4 and envelope["result"]["error_kind"] == "timeout"
    assert list(temp.iterdir()) == []


def test_w2_96_runner_exception_is_a_crash_without_message(project, capsys, monkeypatch):
    root, temp = project
    _plant(root, "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n", {"test_a.py": "def test_a():\n    pass\n"})

    def broken(*_args, **_kwargs):
        raise OSError(2, "no such file", str(root / "tests" / MARK))

    monkeypatch.setattr(runner, "read_cases", broken)
    code, envelope, text = _accept(root, "DAEO-t001", capsys)
    assert code == 4 and envelope["result"]["error_kind"] == "crash"
    assert MARK not in text
    assert list(temp.iterdir()) == []


def test_w2_96_undecodable_readme_is_a_crash(project, capsys):
    root, _ = project
    folder = _plant(root, None, {"test_a.py": "def test_a():\n    pass\n"})
    (folder / "README.md").write_bytes(b"| KPI | Test |\n\xff\xfe\x80\n")
    code, envelope, _ = _accept(root, "DAEO-t001", capsys)
    assert code == 4 and envelope["result"]["error_kind"] == "crash"


# --- refusals -------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("readme", [None, f"# Tests\n\nAll of them. {MARK}\n",
                                    "| KPI | Test |\n|---|---|\n| — | no items |\n",
                                    "| KPI | Notes |\n|---|---|\n| S1 | `test_a.py` |\n"])
def test_w2_96_no_map_refuses(project, capsys, readme):
    root, _ = project
    _plant(root, readme, {"test_a.py": "def test_a():\n    pass\n"})
    code, envelope, text = _accept(root, "DAEO-t001", capsys)
    assert code == 1 and envelope["ok"] is False
    assert envelope["error"]["code"] == "ACCEPT_NO_MAP"
    assert MARK not in text and "test_a" not in text


@pytest.mark.parametrize("ticket, path, code_name", [
    ("DAEO-none", "tests/acceptance/T1/", "ACCEPT_UNKNOWN_TICKET"),
    ("../proj/.tickets/DAEO-t001", "tests/acceptance/T1/", "ACCEPT_UNKNOWN_TICKET"),
    ("DAEO-t001", None, "ACCEPT_NO_TESTS"),
    ("DAEO-t001", "../elsewhere/", "ACCEPT_NO_TESTS"),
    ("DAEO-t001", "tests/acceptance/missing/", "ACCEPT_NO_TESTS"),
])
def test_w2_96_refusals(project, capsys, ticket, path, code_name):
    root, _ = project
    _plant(root, "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n", {"test_a.py": "pass\n"},
           path=path if path != "tests/acceptance/missing/" else "tests/acceptance/T1/")
    if path == "tests/acceptance/missing/":
        _plant(root, None, {}, path=path, ticket="DAEO-t001")
        os.rmdir(root / path)
    code, envelope, _ = _accept(root, ticket, capsys)
    assert code == 1 and envelope["error"]["code"] == code_name


def test_w2_96_refusal_is_a_gov_error_naming_ticket_and_path(project):
    root, _ = project
    _plant(root, None, {})
    with pytest.raises(GovError) as raised:
        runner.accept(root, "DAEO-t001", 30)
    assert raised.value.code == "ACCEPT_NO_MAP"
    assert raised.value.details == {"ticket": "DAEO-t001", "path": "tests/acceptance/T1/"}


# --- review 1's addendum ----------------------------------------------------------------------------------------------

ONE_LINE = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n"


def test_w2_96_r1_a_conftest_refusing_a_basetemp_runs(project, capsys):
    root, temp = project
    (root / "tests").mkdir()
    (root / "tests" / "conftest.py").write_text(
        "import pytest\n\ndef pytest_configure(config):\n    if config.option.basetemp is not None:\n"
        "        raise pytest.UsageError('no basetemp')\n")
    test = "def test_a(tmp_path):\n    (tmp_path / 'f').write_text('x')\n"
    _plant(root, ONE_LINE, {"test_a.py": test})
    code, envelope, _ = _accept(root, "DAEO-t001", capsys)
    assert code == 0, envelope
    assert envelope["result"]["lines"][0]["passed"] == 1
    assert list(temp.iterdir()) == []


def _gone(pid: int) -> bool:
    try:
        return Path(f"/proc/{pid}/stat").read_text().split(")")[-1].split()[0] == "Z"
    except OSError:
        return True


@pytest.mark.parametrize("signum", [15, 1])  # SIGTERM, SIGHUP
def test_w2_96_r2_a_signal_stops_the_run_and_cleans_up(project, tmp_path, signum):
    import subprocess
    import sys
    import time

    root, temp = project
    flag = tmp_path / "started"
    test = ("import os, subprocess, sys, time\n\ndef test_a(tmp_path):\n"
            f"    (tmp_path / 'x').write_text('{MARK}')\n"
            "    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
            f"    open({str(flag)!r}, 'w').write(str(child.pid))\n    time.sleep(60)\n")
    _plant(root, ONE_LINE, {"test_a.py": test})
    env = dict(os.environ, PYTHONPATH=str(Path(runner.__file__).parents[2]), TMPDIR=str(temp))
    gov = subprocess.Popen([sys.executable, "-m", "gov.cli.main", "accept", "DAEO-t001", "--json", "--root",
                            str(root)], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    deadline = time.monotonic() + 60
    while not (flag.exists() and flag.read_text()) and time.monotonic() < deadline:
        time.sleep(0.1)
    grandchild = int(flag.read_text())
    gov.send_signal(signum)
    out, _ = gov.communicate(timeout=30)
    assert gov.returncode == 128 + signum
    assert MARK.encode() not in out
    assert list(temp.iterdir()) == []
    deadline = time.monotonic() + 10
    while not _gone(grandchild) and time.monotonic() < deadline:
        time.sleep(0.1)
    assert _gone(grandchild)


LOCKED = ("import os\n\ndef test_a(tmp_path):\n    (tmp_path / 'd' / 'e').mkdir(parents=True)\n"
          "    (tmp_path / 'd' / 'e' / 'f').write_text('x')\n    os.chmod(tmp_path / 'd' / 'e' / 'f', 0)\n"
          "    os.chmod(tmp_path / 'd' / 'e', 0)\n    os.chmod(tmp_path / 'd', 0)\n")


@pytest.mark.parametrize("tail, extra, code", [("    assert False\n", (), 3),
                                               ("    import time\n    time.sleep(60)\n", ("--timeout", "4"), 4)])
def test_w2_96_r3_folders_without_permissions_are_removed(project, capsys, tail, extra, code):
    root, temp = project
    _plant(root, ONE_LINE, {"test_a.py": LOCKED + tail})
    got, _, _ = _accept(root, "DAEO-t001", capsys, *extra)
    assert got == code
    assert list(temp.iterdir()) == []


@pytest.mark.parametrize("readme", [
    "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n| Failure: refusals | `test_b.py` |\n",
    "| KPI | Test |\n|---|---|\n| Success 3a | `test_a.py` |\n",
    "| KPI | Test |\n|---|---|\n| S8b | `test_a.py` |\n",
    "| KPI | Test |\n|---|---|\n| — | `test_a.py` |\n",
    "### KPI map\n| Test |\n|---|\n| `test_a.py` |\n",
    "## Success criteria\n| File | What |\n|---|---|\n| `test_a.py` | x |\n",
])
def test_w2_96_r4_an_unreadable_row_refuses_before_any_test(project, capsys, tmp_path, readme):
    root, _ = project
    flag = tmp_path / "ran"
    _plant(root, readme, {"test_a.py": f"def test_a():\n    open({str(flag)!r}, 'w').close()\n"})
    code, envelope, text = _accept(root, "DAEO-t001", capsys)
    assert code == 1 and envelope["ok"] is False
    assert envelope["error"]["code"] == "ACCEPT_MAP_UNREADABLE"
    assert envelope["error"]["details"] == {"ticket": "DAEO-t001", "path": "tests/acceptance/T1/"}
    assert "test_a" not in text and "refusals" not in text and "criteria" not in text
    assert not flag.exists()


def test_w2_96_r4_other_headings_still_map_nothing():
    readme = "### Successes and notes\n| Test |\n|---|\n| `test_a.py` |\n\n## K1\n| Test |\n|---|\n| `b` |\n"
    assert runner.parse_map(readme) == {"success-1": ["b"]}


def test_w2_96_r5_items_without_a_file_part():
    case = runner.Case("tests/acceptance/T1/test_x.py", "test_run[a]", "passed")
    assert runner.matches("::test_run", case)
    assert runner.matches("every_form::test_run", case)
    assert runner.matches("every_form::K::test_run", case)
    assert not runner.matches("every_form::test_other", case)
    assert not runner.matches("other.py::test_run", case)


def test_w2_96_r5_a_named_test_that_matches_nothing_fails_its_line(project, capsys):
    root, _ = project
    readme = ("| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_a`, `test_missing` |\n"
              "| S2 | `test_a.py`, `test_gone.py` |\n| S3 | `x::test_nope`, `test_a` |\n"
              "| S4 | `test_a`, `other_word`, `helpers.py` |\n")
    _plant(root, readme, {"test_a.py": "def test_a():\n    pass\n"})
    code, envelope, text = _accept(root, "DAEO-t001", capsys)
    assert code == 3
    assert envelope["result"]["lines"] == [
        {"kpi": "success-1", "outcome": "fail", "passed": 1, "failed": 1, "skipped": 0},
        {"kpi": "success-2", "outcome": "fail", "passed": 1, "failed": 1, "skipped": 0},
        {"kpi": "success-3", "outcome": "fail", "passed": 1, "failed": 1, "skipped": 0},
        {"kpi": "success-4", "outcome": "pass", "passed": 1, "failed": 0, "skipped": 0},
    ]
    assert envelope["result"]["totals"] == {"passed": 1, "failed": 0, "skipped": 0}
    for leak in ("test_missing", "test_gone", "test_nope", "other_word"):
        assert leak not in text


def test_w2_96_r6_no_log_file(project, capsys):
    root, temp = project
    (root / "pytest.ini").write_text("[pytest]\nlog_file = w296.log\nlog_file_level = INFO\n")
    test = f"import logging\n\ndef test_a():\n    logging.getLogger('x').warning('{MARK}')\n"
    _plant(root, ONE_LINE, {"test_a.py": test})
    before = _files(root)
    code, _, text = _accept(root, "DAEO-t001", capsys)
    assert code == 0
    assert _files(root) == before and MARK not in text
    assert list(temp.iterdir()) == []


def test_w2_96_r7_a_failed_exit_without_a_failed_case_is_a_crash(project, capsys):
    root, _ = project
    (root / "conftest.py").write_text("def pytest_sessionfinish(session, exitstatus):\n    session.exitstatus = 1\n")
    _plant(root, ONE_LINE, {"test_a.py": "def test_a():\n    pass\n"})
    code, envelope, _ = _accept(root, "DAEO-t001", capsys)
    assert code == 4 and envelope["result"]["error_kind"] == "crash"
