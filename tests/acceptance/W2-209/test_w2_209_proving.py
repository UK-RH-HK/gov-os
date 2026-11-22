"""S5: G3, the update rehearsal on the kept proving repositories.

``gov.release.proving.rehearse(root, commit, version, kept, run=, judge=)`` over a kept W2-81 run planted in a
temporary folder (``<kept>/run.json``, ``<kept>/repos/<six names>``, ``<kept>/outputs/<name>``; ``report.json`` naming a
queue ticket per repository when the case says so), with the stand-in runner and judge of ``w2_209_standins``: all steps
passing is READY; one planted failure is NOT_READY naming that repository and step; five repositories, or no kept
folder, is NOT_READY; the kept folder and ``root`` are unchanged after every run. README, "S5".
"""

import os

import pytest

import w2_209_support as support

STEPS = ("check", "doctor_before", "update", "doctor_after")


@pytest.fixture(scope="module")
def root(base, tmp_path_factory):
    return support.make_case(base, tmp_path_factory.mktemp("w2-209-proving") / "root", "clean")


def _rehearse(root, tmp_path, kept, fail_repo=None, fail_step=None):
    logs = tmp_path / "logs"
    logs.mkdir()
    home = tmp_path / "home"
    (home / "tmp").mkdir(parents=True)
    kept_before = support.folder_snapshot(kept)
    root_before = support.snapshot(root)
    run_log, judge_log = logs / "run.jsonl", logs / "judge.jsonl"
    out = support.call(home, "gov.release.proving:rehearse",
                       [support.path_arg(root), support.rev(root), support.X, support.path_arg(kept)],
                       {"run": support.standin("runner", log=str(run_log), fail_repo=fail_repo, fail_step=fail_step),
                        "judge": support.standin("judge", log=str(judge_log), kept=str(kept),
                                                 fail_repo=fail_repo if fail_step == "judge" else None)})
    assert out.kind != "missing", support.missing_message(out, "gov.release.proving.rehearse")
    report = out.returned("rehearse")
    assert isinstance(report, dict) and report.get("verdict") in ("READY", "NOT_READY"), f"no verdict: {report}"
    assert isinstance(report.get("reasons"), list) and isinstance(report.get("repositories"), dict), \
        f"the report lacks reasons or repositories: {report}"
    assert support.folder_snapshot(kept) == kept_before, \
        f"the rehearsal wrote in the kept folder: {support.difference(kept_before, support.folder_snapshot(kept))[:10]}"
    assert not support.difference(root_before, support.snapshot(root)), "the rehearsal changed root"
    return report, support.read_jsonl(run_log), support.read_jsonl(judge_log)


def _inside(path, folder):
    path, folder = os.path.realpath(path), os.path.realpath(folder)
    return path == folder or path.startswith(folder + os.sep)


def test_s5_all_steps_passing_is_ready_in_throwaway_clones_of_the_kept_repositories(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root)
    report, calls, judged = _rehearse(root, tmp_path, kept)
    assert report["verdict"] == "READY", f"all steps passed and the verdict is not READY: {report}"
    for name in support.REPOSITORIES:
        steps = [c["step"] for c in calls if c["repository"] == name]
        assert all(step in steps for step in STEPS), f"{name}: the steps run were {steps}, not all of {STEPS}"
        assert "close" not in steps, f"{name}: gov close ran with no queue ticket in the kept run"
        close = ((report["repositories"].get(name) or {}).get("steps") or {}).get("close") or {}
        assert close.get("skipped") is True, f"{name}: the close step is not said skipped: {report['repositories'].get(name)}"
        cwds = {c["cwd"] for c in calls if c["repository"] == name}
        assert len(cwds) == 1, f"{name}: the steps ran in more than one folder: {cwds}"
        cwd = cwds.pop()
        assert not _inside(cwd, kept) and not _inside(cwd, root), f"{name}: a step ran in {cwd}, not a throwaway clone"
        update = [c for c in calls if c["repository"] == name and c["step"] == "update"][0]
        assert "update" in update["argv"] and support.X in update["argv"], f"{name}: not gov update 0.1.2: {update}"
        check = [c for c in calls if c["repository"] == name and c["step"] == "check"][0]
        assert "--check" in check["argv"], f"{name}: the check step is not gov update --check: {check}"
        source = update.get("source")
        assert source and not _inside(source, root) and not _inside(source, kept), \
            f"{name}: the update does not name a scratch source outside root and the kept folder: {update}"
        assert f"v{support.X}" in (update.get("source_tags") or []), \
            f"{name}: the scratch source holds no tag v{support.X} when the update runs: {update}"
        kinds = sorted((j["kept_root"], j["verdict"]) for j in judged if j["repository"] == name)
        assert kinds == [(False, "READY"), (True, "READY")], \
            f"{name}: the judge was not asked once over the kept repository and once over the clone: {kinds}"


def test_s5_the_close_step_lands_the_kept_run_queue_ticket(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root, tickets=True)
    report, calls, _ = _rehearse(root, tmp_path, kept)
    assert report["verdict"] == "READY", f"all steps passed and the verdict is not READY: {report}"
    for index, name in enumerate(support.REPOSITORIES):
        closes = [c for c in calls if c["repository"] == name and c["step"] == "close"]
        assert len(closes) == 1 and "close" in closes[0]["argv"] and f"K-{index}" in closes[0]["argv"], \
            f"{name}: gov close K-{index} was not run once in the clone: {closes}"


@pytest.mark.parametrize("step, repository", [
    ("check", "python-app"), ("update", "rust-workspace"), ("doctor", "typescript-monorepo"),
    ("judge", "legacy-docs"), ("close", "secret-history")])
def test_s5_one_failing_step_is_not_ready_naming_the_repository_and_the_step(root, tmp_path, step, repository):
    kept = support.make_kept(tmp_path / "kept", root, tickets=True)
    report, _, _ = _rehearse(root, tmp_path, kept, fail_repo=repository, fail_step=step)
    assert report["verdict"] == "NOT_READY", f"a failing {step} in {repository} is not NOT_READY: {report}"
    assert any(repository in r and step in r for r in report["reasons"]), \
        f"no reason names {repository} and {step}: {report['reasons']}"
    assert (report["repositories"].get(repository) or {}).get("failed") == step, \
        f"the report of {repository} does not name {step} as failed: {report['repositories'].get(repository)}"
    others = [n for n in support.REPOSITORIES if n != repository and (report["repositories"].get(n) or {}).get("failed")]
    assert not others, f"repositories with no planted failure are named failed: {others}"


def test_s5_a_kept_run_with_five_repositories_is_not_ready(root, tmp_path):
    kept = support.make_kept(tmp_path / "kept", root, leave_out="legacy-docs")
    report, _, _ = _rehearse(root, tmp_path, kept)
    assert report["verdict"] == "NOT_READY", f"five kept repositories gave {report['verdict']}"
    assert any("legacy-docs" in r for r in report["reasons"]), f"the missing repository is not named: {report['reasons']}"


def test_s5_a_missing_kept_folder_is_not_ready(root, tmp_path):
    report, calls, _ = _rehearse(root, tmp_path, tmp_path / "no-such-run")
    assert report["verdict"] == "NOT_READY", f"no kept folder gave {report['verdict']}"
    assert report["reasons"], "NOT_READY with no reason"
    assert not [c for c in calls if c["step"] == "update"], "an update ran with no kept folder"
