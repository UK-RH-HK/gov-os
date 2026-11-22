"""S12 to S15: G3 judges the update by regression, not by an absolute READY (the CTO's ruling on W2-209; DEC-1232,
DEC-1233).

``gov.release.proving.rehearse(root, commit, version, kept, run=, judge=)`` over a kept W2-81 run planted in a temporary
folder, with the stand-ins of ``w2_209_rg_standins``. The judge step passes when the verdict over the updated copy
equals the verdict over the kept repository (or improves on it); the close step passes when ``gov close`` of the queue
ticket exits as it did before the update (the label ``close_before``); each step's report entry holds both values;
``root`` may be relative. README, "The rehearsal judged by regression (S12 to S15)".
"""

import json
import os
import re
import subprocess
import sys

import pytest

import w2_209_support as support

NAMES = support.REPOSITORIES
READY, NOT_READY = "READY", "NOT_READY"


@pytest.fixture(scope="module")
def root(base, tmp_path_factory):
    return support.make_case(base, tmp_path_factory.mktemp("w2-209-regression") / "root", "clean")


def _call(home, args, kwargs, cwd):
    spec = json.dumps({"call": "gov.release.proving:rehearse", "args": args, "kwargs": kwargs})
    driver = support.HERE / "w2_209_rg_driver.py"
    proc = subprocess.run([sys.executable, str(driver)], cwd=str(cwd), env=support.environment(home), input=spec,
                          capture_output=True, text=True, timeout=support.TIMEOUT_S)
    done = support.Run(("gov.release.proving:rehearse",), proc.returncode, proc.stdout, proc.stderr)
    lines = [line for line in proc.stdout.splitlines() if line.startswith(support._MARK)]
    if not lines:
        return support.Outcome("crashed", run=done)
    data = json.loads(lines[-1][len(support._MARK):])
    return support.Outcome(data["kind"], data.get("result"), data.get("error") or {}, done)


def _rehearse(root, tmp_path, kept, runner=None, judge=None, root_arg=None, cwd=None):
    """Run the rehearsal in a child; returns ``(report, calls, judged)``. The kept folder and root are checked unchanged."""
    logs = tmp_path / "logs"
    logs.mkdir()
    home = tmp_path / "home"
    (home / "tmp").mkdir(parents=True)
    run_log, judge_log = logs / "run.jsonl", logs / "judge.jsonl"
    kept_before, root_before = support.folder_snapshot(kept), support.snapshot(root)
    kwargs = {"run": support.standin("rg_runner", log=str(run_log), **(runner or {})),
              "judge": support.standin("rg_judge", log=str(judge_log), kept=str(kept), **(judge or {}))}
    first = support.path_arg(root) if root_arg is None else root_arg
    out = _call(home, [first, support.rev(root), support.X, support.path_arg(kept)], kwargs, cwd or home)
    assert out.kind != "missing", support.missing_message(out, "gov.release.proving.rehearse")
    report = out.returned("rehearse")
    assert isinstance(report, dict) and report.get("verdict") in (READY, NOT_READY), f"no verdict: {report}"
    assert support.folder_snapshot(kept) == kept_before, "the rehearsal wrote in the kept folder"
    assert not support.difference(root_before, support.snapshot(root)), "the rehearsal changed root"
    return report, support.read_jsonl(run_log), support.read_jsonl(judge_log)


def _step(report, name, step):
    return ((report["repositories"].get(name) or {}).get("steps") or {}).get(step) or {}


def _failed(report, name):
    return (report["repositories"].get(name) or {}).get("failed")


def _reasons(report, name, step):
    return [r for r in report["reasons"] if name in r and step in r]


def _inside(path, folder):
    path, folder = os.path.realpath(path), os.path.realpath(folder)
    return path == folder or path.startswith(folder + os.sep)


def _only_failing(report, name, step):
    assert report["verdict"] == NOT_READY, f"{name}'s {step} regressed and the verdict is {report['verdict']}"
    assert _failed(report, name) == step, f"{name}: the failed step is {_failed(report, name)!r}, not {step!r}"
    assert _reasons(report, name, step), f"no reason names {name} and {step}: {report['reasons']}"
    others = [n for n in NAMES if n != name and _failed(report, n)]
    assert not others, f"repositories with no regression are named failed: {others}"


# ---- S12: the judge step -------------------------------------------------------------------------------------

def test_s12_a_not_ready_kept_run_and_an_equally_not_ready_copy_with_equal_doctor_and_close_is_ready(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root, tickets=True)
    report, _, judged = _rehearse(root, tmp_path, kept, runner={"close_before": 1, "close": 1},
                                  judge={"over_kept": NOT_READY, "over_copy": NOT_READY})
    assert report["verdict"] == READY, f"NOT_READY before and after, doctor and close equal: not READY: {report}"
    assert report["reasons"] == [], f"READY with reasons: {report['reasons']}"
    for name in NAMES:
        assert not _failed(report, name), f"{name} is named failed: {report['repositories'][name]}"
        judge = _step(report, name, "judge")
        assert judge.get("pass") is True and judge.get("verdicts") == [NOT_READY, NOT_READY], f"{name}: {judge}"
        close = _step(report, name, "close")
        assert close.get("pass") is True and close.get("before") == 1 and close.get("after") == 1, f"{name}: {close}"
        kinds = sorted((j["kept_root"], j["verdict"]) for j in judged if j["repository"] == name)
        assert kinds == [(False, NOT_READY), (True, NOT_READY)], f"{name}: the judge was asked {kinds}"


def test_s12_ready_before_and_not_ready_after_is_a_regression_naming_the_repository_the_step_and_both_values(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root, tickets=True)
    report, _, _ = _rehearse(root, tmp_path, kept, judge={"repo": "legacy-docs", "over_kept": READY, "over_copy": NOT_READY})
    _only_failing(report, "legacy-docs", "judge")
    assert _step(report, "legacy-docs", "judge").get("verdicts") == [READY, NOT_READY], \
        f"verdicts are not [over the kept repository, over the copy]: {_step(report, 'legacy-docs', 'judge')}"
    reason = _reasons(report, "legacy-docs", "judge")[0]
    assert NOT_READY in reason and re.search(r"(?<![A-Z_])READY", reason), f"the reason names not both values: {reason!r}"


def test_s12_not_ready_before_and_ready_after_is_not_worse_and_passes_the_judge_step(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root, tickets=True)
    report, _, _ = _rehearse(root, tmp_path, kept, judge={"repo": "rust-workspace", "over_kept": NOT_READY, "over_copy": READY})
    assert report["verdict"] == READY, f"an improvement (NOT_READY, then READY) is refused: {report['reasons']}"
    judge = _step(report, "rust-workspace", "judge")
    assert judge.get("pass") is True and judge.get("verdicts") == [NOT_READY, READY], f"{judge}"


@pytest.mark.parametrize("over_kept, over_copy", [("raise", READY), (READY, "raise"), ("none", "none"),
                                                  (READY, "none"), ("none", READY)])
def test_s12_a_judge_that_raises_or_returns_no_verdict_is_never_a_pass(root, tmp_path, over_kept, over_copy):
    kept = support.make_kept(tmp_path / "kept", root, tickets=True)
    report, _, _ = _rehearse(root, tmp_path, kept, judge={"repo": "rust-workspace", "over_kept": over_kept,
                                                          "over_copy": over_copy})
    _only_failing(report, "rust-workspace", "judge")


# ---- S13: the close step -------------------------------------------------------------------------------------

def test_s13_a_close_that_refuses_before_the_update_and_refuses_the_same_after_it_passes(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root, tickets=True)
    report, calls, _ = _rehearse(root, tmp_path, kept, runner={"repo": "secret-history", "close_before": 1, "close": 1})
    assert report["verdict"] == READY, f"close exits 1 before and after the update and the verdict is not READY: {report}"
    close = _step(report, "secret-history", "close")
    assert close.get("pass") is True and close.get("before") == 1 and close.get("after") == 1, f"{close}"
    assert close.get("ticket") == "K-4", f"the close entry does not name the ticket: {close}"


def test_s13_gov_close_runs_as_close_before_in_an_unupdated_throwaway_copy_before_the_update_and_as_close_after_it(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root, tickets=True)
    report, calls, _ = _rehearse(root, tmp_path, kept)
    assert report["verdict"] == READY, f"{report['reasons']}"
    for index, name in enumerate(NAMES):
        mine = [c for c in calls if c["repository"] == name]
        before = [c for c in mine if c["step"] == "close_before"]
        after = [c for c in mine if c["step"] == "close"]
        assert len(before) == 1 and len(after) == 1, f"{name}: close_before {len(before)} times and close {len(after)}"
        for call in (before[0], after[0]):
            assert "close" in call["argv"] and f"K-{index}" in call["argv"], f"{name}: not gov close K-{index}: {call}"
            assert not _inside(call["cwd"], kept) and not _inside(call["cwd"], root), f"{name}: ran in {call['cwd']}"
        steps = [c["step"] for c in mine]
        assert steps.index("close_before") < steps.index("update") < steps.index("close"), f"{name}: order {steps}"
        assert before[0]["updated"] is False, f"{name}: close_before ran in a folder already updated"
        assert after[0]["updated"] is True, f"{name}: close ran in a folder that was not updated"
        close = _step(report, name, "close")
        assert close.get("before") == 0 and close.get("after") == 0, f"{name}: {close}"


def test_s13_a_close_that_exits_0_before_the_update_and_not_after_it_fails_naming_close_and_both_exit_codes(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root, tickets=True)
    report, _, _ = _rehearse(root, tmp_path, kept, runner={"repo": "secret-history", "close_before": 0, "close": 7})
    _only_failing(report, "secret-history", "close")
    close = _step(report, "secret-history", "close")
    assert close.get("pass") is False and close.get("before") == 0 and close.get("after") == 7, f"{close}"
    reason = _reasons(report, "secret-history", "close")[0]
    assert re.search(r"\b0\b", reason) and re.search(r"\b7\b", reason), f"the reason names not both exit codes: {reason!r}"


def test_s13_a_close_that_refuses_before_the_update_and_exits_0_after_it_passes(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root, tickets=True)
    report, _, _ = _rehearse(root, tmp_path, kept, runner={"repo": "python-app", "close_before": 1, "close": 0})
    assert report["verdict"] == READY, f"nonzero before and 0 after is refused: {report['reasons']}"
    close = _step(report, "python-app", "close")
    assert close.get("pass") is True and close.get("before") == 1 and close.get("after") == 0, f"{close}"


def test_s13_with_no_queue_ticket_the_close_step_is_skipped_and_no_close_runs_at_all(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root)
    report, calls, _ = _rehearse(root, tmp_path, kept)
    assert report["verdict"] == READY, f"{report['reasons']}"
    assert not [c for c in calls if c["step"] in ("close", "close_before")], "a close ran with no queue ticket"
    for name in NAMES:
        assert _step(report, name, "close").get("skipped") is True, f"{name}: {_step(report, name, 'close')}"


# ---- S14: the report names both values -----------------------------------------------------------------------

def test_s14_each_judge_and_close_entry_holds_both_values(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root, tickets=True)
    report, _, _ = _rehearse(root, tmp_path, kept, runner={"repo": "python-app", "close_before": 0, "close": 5},
                             judge={"repo": "legacy-docs", "over_kept": READY, "over_copy": NOT_READY})
    judge = _step(report, "legacy-docs", "judge")
    assert judge.get("pass") is False and judge.get("verdicts") == [READY, NOT_READY], f"{judge}"
    close = _step(report, "python-app", "close")
    assert close.get("pass") is False and close.get("before") == 0 and close.get("after") == 5, f"{close}"
    steady = _step(report, "rust-workspace", "close")
    assert steady.get("pass") is True and steady.get("before") == 0 and steady.get("after") == 0, f"{steady}"
    assert _step(report, "rust-workspace", "judge").get("verdicts") == [READY, READY]
    assert _failed(report, "legacy-docs") == "judge" and _failed(report, "python-app") == "close"
    assert len(report["reasons"]) == 2, f"one reason per failed repository expected: {report['reasons']}"


# ---- S15: a relative root ------------------------------------------------------------------------------------

@pytest.mark.parametrize("form", ["dot", "dotdot"])
def test_s15_a_relative_root_behaves_as_the_absolute_one(root, tmp_path, form):
    kept = support.make_kept(tmp_path / "kept", root)
    if form == "dot":
        cwd, relative = root, "."
    else:
        cwd = tmp_path / "elsewhere" / "deeper"
        cwd.mkdir(parents=True)
        relative = os.path.relpath(root, cwd)
        assert ".." in relative.split(os.sep)
    report, calls, _ = _rehearse(root, tmp_path, kept, root_arg=support.path_arg(relative), cwd=cwd)
    assert not [r for r in report["reasons"] if "does not exist" in r], f"the relative root is not resolved: {report['reasons']}"
    assert report["verdict"] == READY, f"root {relative!r} from {cwd}: {report['reasons']}"
    for name in NAMES:
        steps = [c["step"] for c in calls if c["repository"] == name]
        assert "update" in steps and "doctor_after" in steps, f"{name}: steps run {steps}"
