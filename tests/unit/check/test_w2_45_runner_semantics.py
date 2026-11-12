"""Builder tests for W2-45 (DAEO-neam): the runner's semantics at the level of ``run_checks`` on a planted project.

S2 (not green), S3 (absent tool), S4 (tier coverage) and S5 (the time limit, with the process group stopped).
Regression evidence only (DEC-136); the acceptance tests are the independent test designer's.
"""
from __future__ import annotations

import os
import shlex
import sys
import time
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check import runner  # noqa: E402

BUILT_INS = ("_check_openspec", "_check_skill_version", "_check_readiness")


def _plant(root, check_id, command, severity="hard-block", **extra):
    declaration = {"id": check_id, "family": "graph integrity", "tier": "G1", "severity": severity,
                   "command": command, **extra}
    path = root / "template/governance/kernel/checks" / f"{check_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(declaration), encoding="utf-8")


def _plant_policies(root, **policies):
    path = root / runner.PATH_MAP_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"namespaces": {}, "policies": policies}), encoding="utf-8")


@pytest.fixture
def project(tmp_path, monkeypatch):
    """An empty project whose three built-in checks are stubbed green: only the planted checks are measured."""
    for name in BUILT_INS:
        monkeypatch.setattr(runner, name, lambda root, commit, name=name: {
            "id": name, "family": "product traceability", "severity": runner.HARD_BLOCK, "status": runner.GREEN,
            "findings": [], "elapsed_s": 0.0, "time_limit_s": runner.TIMEOUT_S, "provenance": {}})
    return tmp_path / "project"


def _entry(report, check_id):
    return next(entry for entry in report["checks"] if entry["id"] == check_id)


def _print(text, code=0):
    return f"printf '%s' {shlex.quote(text)}; exit {code}"


def _alive(pid):
    try:
        os.kill(pid, 0)
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"
    except (ProcessLookupError, FileNotFoundError):
        return False


# --------------------------------------------------------------------------
# the time fields and the stated limit (S5, item 2)
# --------------------------------------------------------------------------

def test_the_result_states_the_limit_and_every_check_states_its_own_time(project):
    _plant(project, "plain", "exit 0")
    _plant(project, "limited", "exit 0", **{"timeout-seconds": 7})
    report, _ = runner.run_checks(project)
    assert report["time_limit_s"] == runner.TIMEOUT_S == 60
    assert _entry(report, "plain")["time_limit_s"] == 60
    assert _entry(report, "limited")["time_limit_s"] == 7
    for entry in report["checks"]:  # the built-ins (stubbed here) and the policy results carry both too
        assert isinstance(entry["elapsed_s"], float) and entry["elapsed_s"] >= 0
        assert isinstance(entry["time_limit_s"], int)


def test_the_built_in_checks_state_both_times(tmp_path, monkeypatch):
    monkeypatch.setattr(runner.shutil, "which", lambda name: None)
    for check in (runner._check_openspec, runner._check_skill_version, runner._check_readiness):
        entry = check(tmp_path, "abc123")
        assert isinstance(entry["elapsed_s"], float) and entry["time_limit_s"] == runner.TIMEOUT_S


def test_a_check_past_its_limit_is_stopped_and_reported_timed_out(project):
    _plant(project, "slow", "sleep 30", **{"timeout-seconds": 1})
    began = time.monotonic()
    report, red = runner.run_checks(project)
    assert time.monotonic() - began < 10
    slow = _entry(report, "slow")
    assert slow["status"] == "RED" and red
    assert [finding["code"] for finding in slow["findings"]] == ["CHECK_TIMED_OUT"]
    assert slow["findings"][0]["time_limit_s"] == 1 and slow["time_limit_s"] == 1
    assert 1 <= slow["elapsed_s"] < 10


def test_a_warning_past_its_limit_is_yellow(project):
    _plant(project, "slow-warning", "sleep 30", severity="warning", **{"timeout-seconds": 1})
    slow = _entry(runner.run_checks(project)[0], "slow-warning")
    assert slow["status"] == "YELLOW" and slow["findings"][0]["code"] == "CHECK_TIMED_OUT"


def test_a_grandchild_that_holds_the_pipe_does_not_keep_the_runner_waiting(project, tmp_path):
    pidfile = tmp_path / "grandchild.pid"
    _plant(project, "holds-pipe", f"sleep 30 & echo $! > {shlex.quote(str(pidfile))}; exit 0",
           **{"timeout-seconds": 1})
    began = time.monotonic()
    holds = _entry(runner.run_checks(project)[0], "holds-pipe")
    assert time.monotonic() - began < 10
    assert holds["findings"][0]["code"] == "CHECK_TIMED_OUT"
    grandchild = int(pidfile.read_text())
    for _ in range(30):  # the whole process group was stopped: the grandchild is gone
        if not _alive(grandchild):
            break
        time.sleep(0.1)
    assert not _alive(grandchild)


def _wait_gone(pid):
    for _ in range(50):
        if not _alive(pid):
            return True
        time.sleep(0.1)
    return False


def _break_the_wait(monkeypatch, error, started, pidfile=None):
    """Make the first wait of ``_run_command`` raise ``error``, once the check has started its grandchild (the
    pid file exists); the pid of the shell is recorded in ``started``. Later waits (the stop's own) are real."""
    real = runner.subprocess.Popen

    class Broken(real):
        def communicate(self, input=None, timeout=None):
            if not started:
                started.append(self.pid)
                for _ in range(100):
                    if pidfile is None or pidfile.exists() and pidfile.read_text().endswith("\n"):
                        break
                    time.sleep(0.05)
                raise error
            return super().communicate(input, timeout)

    monkeypatch.setattr(runner.subprocess, "Popen", Broken)


@pytest.mark.parametrize("error", [KeyboardInterrupt(), RuntimeError("boom"), OverflowError("timeout is too large")],
                         ids=lambda error: type(error).__name__)
def test_an_error_in_the_wait_leaves_no_process_of_the_check_running_and_reaches_the_caller(
        tmp_path, monkeypatch, error):
    pidfile, started, grandchild = tmp_path / "grandchild.pid", [], None
    try:
        _break_the_wait(monkeypatch, error, started, pidfile)
        with pytest.raises(type(error)):
            runner._run_command(f"sleep 30 & echo $! > {shlex.quote(str(pidfile))}; wait", tmp_path)
        grandchild = int(pidfile.read_text())
        assert _wait_gone(started[0]), "the shell of the check is still running"
        assert _wait_gone(grandchild), "a grandchild of the check is still running"
    finally:
        monkeypatch.undo()
        for pid in [*started, grandchild or 0]:
            if pid and _alive(pid):
                try:
                    os.killpg(pid, 9)
                except (ProcessLookupError, PermissionError):
                    os.kill(pid, 9)


def test_a_limit_too_large_for_the_wait_leaves_the_check_stopped(tmp_path, monkeypatch):
    """The wait itself fails on a huge stated limit (W2-L167): what was started is still stopped. The traceback
    stays that row's; here only that the check does not run on without a limit."""
    started = []
    real = runner.subprocess.Popen

    class Recording(real):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            started.append(self.pid)

    monkeypatch.setattr(runner.subprocess, "Popen", Recording)
    try:
        try:
            runner._run_command("sleep 30; wait", tmp_path, timeout=10 ** 12)
        except (OverflowError, ValueError):
            pass  # what the wait raises on this platform for a limit it cannot hold; a timer that holds it is fine
        else:
            pytest.skip("this platform's wait holds the huge limit and the check ended by itself")
        assert started and _wait_gone(started[0]), "the shell of the check is still running"
    finally:
        monkeypatch.undo()
        for pid in started:
            if _alive(pid):
                os.kill(pid, 9)


# --------------------------------------------------------------------------
# S2: a check is green only when it exits 0 with no finding (W2-M129, W2-M212)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("printed", [
    "[]", '{"ok": true, "result": {}}', '{"ok": true, "result": {"findings": []}}', "", "all measured",
])
def test_a_clean_check_that_exits_0_is_green(project, printed):
    _plant(project, "clean", _print(printed))
    clean = _entry(runner.run_checks(project)[0], "clean")
    assert clean["status"] == "GREEN" and clean["findings"] == []


@pytest.mark.parametrize("printed", [
    '[{"code": "SOMETHING_WRONG", "message": "m"}]',
    '{"ok": true, "result": {"findings": [{"code": "SOMETHING_WRONG", "message": "m"}]}}',
])
@pytest.mark.parametrize("severity, status", [("hard-block", "RED"), ("warning", "YELLOW")])
def test_a_check_that_exits_0_with_a_finding_is_not_green(project, printed, severity, status):
    _plant(project, "finds", _print(printed), severity=severity)
    finds = _entry(runner.run_checks(project)[0], "finds")
    assert finds["status"] == status
    assert [finding["code"] for finding in finds["findings"]] == ["SOMETHING_WRONG"]


@pytest.mark.parametrize("printed", [
    '{"unmeasured": true, "reason": "no index built"}',
    '{"ok": true, "result": {"unmeasured": true, "reason": "no index built"}}',
])
def test_a_json_answer_that_says_unmeasured_is_not_green(project, printed):
    _plant(project, "unsure", _print(printed))
    unsure = _entry(runner.run_checks(project)[0], "unsure")
    assert unsure["status"] == "RED"
    assert [(finding["code"], finding["reason"]) for finding in unsure["findings"]] == \
        [("CHECK_UNMEASURED", "no index built")]


def test_an_unmeasured_answer_without_a_reason_is_still_a_finding(project):
    _plant(project, "unsure", _print('{"unmeasured": true}'), severity="warning")
    unsure = _entry(runner.run_checks(project)[0], "unsure")
    assert unsure["status"] == "YELLOW" and unsure["findings"][0]["code"] == "CHECK_UNMEASURED"


def test_output_that_is_no_json_and_holds_the_word_unmeasured_is_not_green(project):
    _plant(project, "prose", _print("3 files, 2 unmeasured"))
    prose = _entry(runner.run_checks(project)[0], "prose")
    assert prose["status"] == "RED" and prose["findings"][0]["code"] == "CHECK_UNMEASURED"


def test_a_measured_answer_that_says_unmeasured_false_adds_no_unmeasured_finding(project):
    _plant(project, "measured", _print('{"ok": true, "result": {"unmeasured": false, "findings": []}}'))
    assert _entry(runner.run_checks(project)[0], "measured")["status"] == "GREEN"


def test_a_check_that_fails_keeps_its_own_findings_and_code(project):
    _plant(project, "fails", "exit 1")
    fails = _entry(runner.run_checks(project)[0], "fails")
    assert fails["status"] == "RED" and fails["findings"][0]["code"] == "CHECK_FAILED"


def test_the_not_applicable_answer_is_unchanged_and_carries_the_times(project):
    _plant(project, "not-here", _print('{"not_applicable": true, "reason": "no such thing here"}', 2))
    path = project / "template/governance/kernel/checks/not-here.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "allows-not-applicable: 'true'\n", encoding="utf-8")
    not_here = _entry(runner.run_checks(project)[0], "not-here")
    assert (not_here["status"], not_here["findings"], not_here["reason"]) == ("YELLOW", [], "no such thing here")
    assert isinstance(not_here["elapsed_s"], float) and not_here["time_limit_s"] == 60


# --------------------------------------------------------------------------
# S3: an absent tool of a hard-block check is red, never yellow (W2-M130, W2-M265)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("severity, status", [("hard-block", "RED"), ("warning", "YELLOW")])
def test_an_absent_tool_is_red_for_a_hard_block_check_and_yellow_for_a_warning(project, severity, status):
    _plant(project, "needs-tool", "w245-no-such-tool --flag --other", severity=severity)
    needs = _entry(runner.run_checks(project)[0], "needs-tool")
    assert needs["status"] == status
    assert [finding["code"] for finding in needs["findings"]] == ["CHECK_TOOL_ABSENT"]
    assert "w245-no-such-tool" in needs["findings"][0]["message"]
    assert "--flag" not in needs["findings"][0]["message"]  # the first word as written, and no more


def test_a_hard_block_check_that_exits_127_is_an_absent_tool(project):
    _plant(project, "says-127", "exit 127")
    says = _entry(runner.run_checks(project)[0], "says-127")
    assert says["status"] == "RED" and says["findings"][0]["code"] == "CHECK_TOOL_ABSENT"


def test_a_command_that_cannot_be_started_is_an_absent_tool(project, monkeypatch):
    def refuse(*args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory: '/bin/sh'")
    _plant(project, "cannot-start", "w245-some-tool run")
    monkeypatch.setattr(runner.subprocess, "Popen", refuse)
    cannot = _entry(runner.run_checks(project)[0], "cannot-start")
    assert cannot["status"] == "RED"
    assert cannot["findings"][0]["code"] == "CHECK_TOOL_ABSENT" and "w245-some-tool" in cannot["findings"][0]["message"]


def test_openspec_that_is_absent_is_red_not_yellow(tmp_path, monkeypatch):
    monkeypatch.setattr(runner.shutil, "which", lambda name: None)
    entry = runner._check_openspec(tmp_path, "abc123")
    assert entry["severity"] == "hard-block" and entry["status"] == "RED"
    assert [finding["code"] for finding in entry["findings"]] == ["OPENSPEC_ABSENT"]


# --------------------------------------------------------------------------
# S4: a hard-block key is covered only by a check of hard-block tier (W2-M211, W2-M259)
# --------------------------------------------------------------------------

def test_a_hard_block_key_covered_only_by_warnings_is_refused_naming_the_key(project):
    _plant_policies(project, security="hard-block")
    _plant(project, "weak-one", "exit 0", severity="warning", enforces=["security"])
    _plant(project, "weak-two", "exit 0", severity="warning", enforces=["security", "other"])
    report, red = runner.run_checks(project)
    refused = _entry(report, "policy-security")
    assert red and refused["severity"] == "hard-block" and refused["status"] == "RED"
    (finding,) = refused["findings"]
    assert finding["code"] == "POLICY_TIER_TOO_LOW" and finding["policy"] == "security"
    assert finding["checks"] == ["weak-one", "weak-two"] and "security" in finding["message"]
    assert isinstance(refused["elapsed_s"], float) and refused["time_limit_s"] == 60


def test_a_hard_block_key_covered_by_a_hard_block_check_is_accepted(project):
    _plant_policies(project, security="hard-block")
    _plant(project, "strong", "exit 0", severity="hard-block", enforces=["security"])
    report, red = runner.run_checks(project)
    assert not red and all(entry["id"] != "policy-security" for entry in report["checks"])


def test_one_hard_block_check_among_warnings_covers_the_key(project):
    _plant_policies(project, security="hard-block")
    _plant(project, "weak", "exit 0", severity="warning", enforces=["security"])
    _plant(project, "strong", "exit 0", severity="hard-block", enforces=["security"])
    report, red = runner.run_checks(project)
    assert not red and all(entry["id"] != "policy-security" for entry in report["checks"])


def test_tier_the_letter_is_not_read_only_severity_is(project):
    _plant_policies(project, security="hard-block")
    _plant(project, "g5-warning", "exit 0", severity="warning", enforces=["security"], tier="G5")
    assert _entry(runner.run_checks(project)[0], "policy-security")["findings"][0]["code"] == "POLICY_TIER_TOO_LOW"


def test_an_uncovered_key_keeps_its_own_finding(project):
    _plant_policies(project, security="hard-block", context="warning")
    report, _ = runner.run_checks(project)
    assert _entry(report, "policy-security")["findings"][0]["code"] == "POLICY_NOT_COVERED"
    assert _entry(report, "policy-context")["status"] == "YELLOW"


def test_a_warning_key_covered_by_a_warning_check_is_accepted(project):
    _plant_policies(project, context="warning")
    _plant(project, "weak", "exit 0", severity="warning", enforces=["context"])
    assert all(entry["id"] != "policy-context" for entry in runner.run_checks(project)[0]["checks"])
