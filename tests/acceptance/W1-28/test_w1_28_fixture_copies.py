"""KPI success 4 (DEC-385): no test fixture copies the held-out file.

"Every test fixture that copies the repository leaves
governance/project/held-out.yaml out, so it is never copied into a temporary
project."

The check is test code about test code: it is green as soon as the fixtures
are revised, before ``gov pause`` is built. It never opens, hashes or compares
the committed file. ``w1_28_copy_check`` holds the two routes:

- **By running.** Every fixture that takes the repository root as a parameter
  and copies files is called with a synthetic source repository as its root: a
  temporary git repository with a made-up ``governance/project/held-out.yaml``,
  once tracked and once untracked. No file of that path may be in what the
  fixture produced. A fixture a later suite adds in the same form is found and
  run without a change here.
- **By reading.** Every function under ``tests/acceptance/`` that copies the
  whole tree of the repository must be such a fixture, so that the first route
  runs it.

The last three cases show that the check is a real one: a planted fixture that
copies the synthetic held-out file is caught by running it, and two planted
whole-tree copies that take no root parameter are caught by reading.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w1_28_copy_check as check

COPIERS = check.copiers()
# The fixtures of the earlier suites that copy from the repository, as read on 2026-10-05 (README, part B).
KNOWN_COPIERS = {
    "W1-05/w1_05_support.py::copy_working_tree",
    "W1-07/w1_07_support.py::copy_working_tree",
    "W1-46/w1_46_support.py::make_project",
    "W1-47/w1_47_support.py::make_wired_copy",
    "W1-49/w1_49_support.py::make_project",
}


def test_the_check_finds_the_copying_fixtures_of_the_earlier_suites():
    """A fixture that was renamed or lost its root parameter is not silently dropped from the check."""
    missing = sorted(KNOWN_COPIERS - {function.label for function in COPIERS})
    assert not missing, (
        f"the check no longer finds these copying fixtures: {missing}. A fixture that copies from the repository "
        f"takes the root as a parameter with the default {check.ROOT_NAME}, so that the check can run it."
    )


@pytest.mark.parametrize("tracked", (True, False), ids=("tracked", "untracked"))
@pytest.mark.parametrize("function", COPIERS, ids=lambda function: function.label)
def test_a_fixture_that_copies_from_the_repository_leaves_the_held_out_file_out(function, tracked, tmp_path):
    source = check.make_source(tmp_path / "source", tracked=tracked)
    assert (source / check.HELD_OUT_REL).is_file(), "the synthetic source has no held-out file"
    produced = check.run_copier(function, source, tmp_path / "produced")
    assert check.arrived(produced), (
        f"{function.label} copied nothing from the synthetic root: the check did not exercise it"
    )
    copies = check.held_out_copies(tmp_path / "produced")
    assert not copies, (
        f"{function.label} copied {check.HELD_OUT_REL} into the project it built (DEC-385): {copies}"
    )


def test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs():
    """Read from the sources: a whole-tree copy that takes no root parameter cannot be run on a synthetic root."""
    unchecked = sorted(function.label for function in check.whole_tree_copiers() if not function.runnable)
    assert not unchecked, (
        f"these functions copy the whole tree of the repository and cannot be run by the check: {unchecked}. "
        f"Make each a module-level function with a parameter `root={check.ROOT_NAME}` that leaves "
        f"{check.HELD_OUT_REL} out by its path, or limit it to named paths (DEC-385)."
    )


# --------------------------------------------------------------------------
# The check is a real one
# --------------------------------------------------------------------------

_UNREVISED = '''
import os, shutil, subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def copy_working_tree(destination, root=REPO_ROOT):
    """W1-05's fixture as it was before DEC-385: every listed file is copied."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    listing = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True, check=True,
    ).stdout
    for rel in sorted(set(item for item in listing.split("\\0") if item)):
        source = Path(root) / rel
        target = destination / rel
        if not (source.is_file() or source.is_symlink()):
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return destination
'''

_NO_ROOT_PARAMETER = '''
import shutil, subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def copy_everything(destination):
    shutil.copytree(REPO_ROOT, destination, symlinks=True)


def clone_everything(destination):
    subprocess.run(["git", "clone", "-q", str(REPO_ROOT), str(destination)], check=True)


def copy_one_folder(destination):
    """Not a whole-tree copy: a named folder below the root."""
    shutil.copytree(REPO_ROOT / "template", destination)
'''


def _planted(tmp_path, text):
    suite = tmp_path / "tests" / "acceptance" / "W1-99"
    suite.mkdir(parents=True)
    (suite / "w1_99_support.py").write_text(text, encoding="utf-8")
    return tmp_path / "tests" / "acceptance"


@pytest.mark.parametrize("tracked", (True, False), ids=("tracked", "untracked"))
def test_an_unrevised_fixture_is_caught_by_running_it(tmp_path, tracked):
    """The fixture of before DEC-385, planted in a synthetic tests folder and run on the synthetic root."""
    found = check.copiers(_planted(tmp_path, _UNREVISED))
    assert [function.name for function in found] == ["copy_working_tree"], found
    source = check.make_source(tmp_path / "source", tracked=tracked)
    produced = check.run_copier(found[0], source, tmp_path / "produced")
    assert check.arrived(produced)
    assert check.held_out_copies(produced) == [str(produced / check.HELD_OUT_REL)], (
        "the check did not see the synthetic held-out file an unrevised fixture copied"
    )
    assert (produced / check.HELD_OUT_REL).read_text(encoding="utf-8") == check.SYNTHETIC_HELD_OUT


def test_a_whole_tree_copy_without_a_root_parameter_is_caught_by_reading(tmp_path):
    tests_root = _planted(tmp_path, _NO_ROOT_PARAMETER)
    unchecked = sorted(function.name for function in check.whole_tree_copiers(tests_root) if not function.runnable)
    assert unchecked == ["clone_everything", "copy_everything"], unchecked


def test_the_reading_route_does_not_flag_this_suite_or_a_named_folder(tmp_path):
    """No false alarm from this file's own planted texts, nor from a copy of one named folder."""
    here = Path(__file__).resolve()
    own = [function.label for function in check.whole_tree_copiers() if function.path == here]
    assert own == [], own
    named = [function.name for function in check.whole_tree_copiers(_planted(tmp_path, _NO_ROOT_PARAMETER))]
    assert "copy_one_folder" not in named
