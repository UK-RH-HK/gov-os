"""W2-59 KPI success 4 and its failure line: ``retrieve_baseline.yaml`` is shipped as package data, proven from an
installed wheel (DEC-835 item 2).

Failure line: "A wheel without the data file fails the build or its test."

The wheel is the stand-in's, built once per session from this worktree; the installed check is the stand-in's.
"""

from __future__ import annotations

import zipfile

import pytest
import yaml

import w2_59_support as support


def test_the_wheel_ships_the_baseline_in_the_retrieval_package(stand_in):
    with zipfile.ZipFile(stand_in.wheel) as wheel:
        names = wheel.namelist()
        assert support.BASELINE_IN_PACKAGE in names, (
            f"the wheel {stand_in.wheel.name} built from this worktree has no {support.BASELINE_IN_PACKAGE}; its "
            f"data files: {[name for name in names if not name.endswith('.py')]}")
        shipped = wheel.read(support.BASELINE_IN_PACKAGE)
    assert shipped == (support.SRC / support.BASELINE_IN_PACKAGE).read_bytes(), (
        f"the wheel's {support.BASELINE_IN_PACKAGE} is not the source's")


def test_the_installed_package_holds_the_baseline(stand_in):
    installed = stand_in.site / support.BASELINE_IN_PACKAGE
    assert installed.is_file(), f"the installed package has no {installed}"
    assert yaml.safe_load(installed.read_text(encoding="utf-8")) == support.baseline_values()


def test_the_installed_check_does_not_fail_for_want_of_its_baseline(stand_in, tmp_path):
    """Dev tiers are configured (a temporary folder with a query set and no tier): the installed check reaches its
    own answer, "no dev tier could be indexed", and does not end on a missing baseline file."""
    tiers = tmp_path / "dev-tiers"
    tiers.mkdir()
    (tiers / "dev-queryset.yaml").write_text("queries: []\n", encoding="utf-8")
    project = support.make_repository(tmp_path / "project")
    box = support.make_box(tmp_path / "box", stand_in)
    env = support.base_env(box.home, f"{box.local_bin}:{support.SYSTEM_PATH}")
    env["GOV_DEV_TIERS"] = str(tiers)
    done = support.run([stand_in.python, "-m", "gov.retrieval.retrieve_check"], cwd=project, env=env)
    assert "retrieve_baseline" not in done.stderr and "Traceback" not in done.stderr, (
        f"the installed retrieval-regression check failed on its baseline\n{done.describe()}")
    assert "no dev tier could be indexed" in done.stdout, done.describe()


@pytest.mark.local_only
def test_the_installed_check_reads_its_thresholds_from_the_installed_package(stand_in, gitleaks, tmp_path):
    """The project holds baselines of its own, with other thresholds, where a lookup from the project would find
    them; the measured check prints the installed package's thresholds."""
    values = support.baseline_values()
    decoy = "# a baseline of the project's own\nhit_at_5: 7\nforbidden_citations: 99\n"
    files = {"src/gov/retrieval/retrieve_baseline.yaml": decoy, "retrieve_baseline.yaml": decoy}
    project = support.make_repository(tmp_path / "project", files, support.RETRIEVAL_PROJECTS["this-repository"])
    done = support.retrieval_check(stand_in, project, tmp_path, gitleaks)
    assert f"(baseline: {float(values['hit_at_5'])})" in done.stdout, (
        f"the measured check did not print the installed hit@5 baseline {float(values['hit_at_5'])}\n"
        f"{done.describe()}")
    assert f"(baseline: {int(values['forbidden_citations'])})" in done.stdout, (
        f"the measured check did not print the installed forbidden-citation baseline "
        f"{int(values['forbidden_citations'])}\n{done.describe()}")
