"""Part 2, KPI 12: the lead's full verification is unchanged (DEC-880 item 2 (b)).

The lead verifies with a plain ``pytest tests`` in the close's form. What this ticket builds is read by
``gov close`` and the nightly command only: no file a plain run reads for its configuration or its collection
changes, and a project's test map changes nothing a plain run collects. README, "Part 2". Both cases are green on
the base by design: they turn red only if the implementation reaches into the plain run.
"""

import subprocess
import sys

import pytest

import w2_66_support as support

ROOT = support.REPO_ROOT
BASE_BRANCH = "w2/integrate"
OWN_FOLDER = "tests/acceptance/W2-66/"
# What a plain ``pytest tests`` reads before it collects: its configuration, the conftests, the serial-only list
# (which the leads' runs in the close's form read).
CONFIGURATION = ("pyproject.toml", "pytest.ini", "tox.ini", "setup.cfg", support.SERIAL_ONLY_REL)


def test_no_file_a_plain_run_reads_for_its_configuration_or_collection_changes():
    known = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", "--quiet", BASE_BRANCH],
                           capture_output=True, text=True)
    if known.returncode != 0:
        pytest.skip(f"no {BASE_BRANCH} in this clone to compare with")
    changed = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only", f"{BASE_BRANCH}...HEAD"],
                             capture_output=True, text=True, check=True).stdout.split()
    touched = [p for p in changed if p in CONFIGURATION or
               (p.endswith("conftest.py") and not p.startswith(OWN_FOLDER))]
    assert not touched, f"the ticket changes what a plain pytest run reads: {touched}"


def test_a_project_s_test_map_changes_nothing_a_plain_run_collects(tmp_path):
    with_map = support.Fixture(tmp_path / "with", tmp_path / "told-with")
    without = support.Fixture(tmp_path / "without", tmp_path / "told-without", test_map=None)

    def collected(fixture):
        done = subprocess.run([sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-p",
                               "no:cacheprovider"], cwd=str(fixture.root), capture_output=True, text=True,
                              env={**support.close_support.sandbox_env(support.cli_support.make_sandbox(
                                  tmp_path / f"sb-{fixture.root.name}")), "PYTHONPATH": str(fixture.root / "src")})
        assert done.returncode == 0, f"a plain run does not collect the fixture:\n{done.stdout}\n{done.stderr}"
        return sorted(line for line in done.stdout.splitlines() if "::" in line)

    assert collected(with_map) == collected(without), "a test map changes what a plain pytest run collects"
