"""S1: the dry run, `gov update <B> --check`, shows the whole update first and changes nothing."""

from __future__ import annotations

import w2_17_support as support


def _result(checked):
    run = checked.run
    assert run.returncode == 0, f"`gov update {support.B} --check --json` did not exit 0\n{run.describe()}"
    return run.result()


def test_check_reports_versions_checks_and_the_whole_plan(checked, source):
    result = _result(checked)
    describe = checked.run.describe()
    assert result.get("check") is True, f"the dry run's report does not say check: true\n{describe}"
    assert (result.get("from"), result.get("to")) == (support.A, support.B), (
        f"the dry run does not report from {support.A} to {support.B}\n{describe}")
    checks = result.get("checks")
    assert isinstance(checks, dict) and all(checks.get(name) == "passed" for name in ("manifest", "files", "wheel")), (
        f"the three checks (manifest, shipped files, wheel) are not each reported passed: {checks!r}\n{describe}")
    support.assert_outcomes(result.get("files"), "the dry run's plan")
    pin = result.get("pin") or {}
    environment = str(pin.get("environment", ""))
    assert pin.get("version") == support.B and environment.rstrip("/").endswith(f"gov/envs/{support.B}"), (
        f"the dry run does not name the pinned gov it would install (version {support.B}, "
        f"<common>/gov/envs/{support.B}): {pin!r}\n{describe}")
    lock = result.get("lock") or {}
    assert lock.get("version") == support.B and lock.get("manifest_sha256") == source.manifest_b_sha256, (
        f"the dry run does not name the lock it would write (release {support.B}, manifest sha256 "
        f"{source.manifest_b_sha256}): {lock!r}\n{describe}")
    assert result.get("adapters") == "would regenerate" and result.get("store") == "would refresh", (
        f"the dry run does not say it would regenerate the adapters and refresh the memory store: adapters "
        f"{result.get('adapters')!r}, store {result.get('store')!r}\n{describe}")


def test_check_text_form_prints_the_same_plan(checked, source):
    run = checked.text
    assert run.returncode == 0, f"`gov update {support.B} --check` did not exit 0\n{run.describe()}"
    told = run.output
    missing = [word for word in (support.A, support.B, "passed", source.manifest_b_sha256, *support.EXPECTED)
               if word not in told]
    assert not missing, f"the dry run's text does not print {missing}\n{run.describe()}"


def test_check_changes_nothing(checked):
    _result(checked)
    assert checked.porcelain == [], f"`git status --porcelain` is not empty after the dry run: {checked.porcelain}"
    changed = support.tree_difference(checked.before, checked.after)
    assert not changed, f"the dry run changed HEAD or files outside .git: {changed[:20]}"
    assert checked.after_pin is None and checked.before_pin is None, (
        f"the dry run left a pin under the git common dir (<common>/gov/): {checked.after_pin!r}")
