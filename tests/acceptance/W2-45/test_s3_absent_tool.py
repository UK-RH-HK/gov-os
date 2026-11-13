"""S3: an absent tool of a hard-block check is red, not yellow [W2-M130, W2-M265].

Interface item 5: exit code 127, or an OSError on start, is the finding ``CHECK_TOOL_ABSENT`` naming the command's
first word; the status is RED when the check is hard-block (never YELLOW) and YELLOW when it is a warning. The
built-in ``openspec-validate`` (hard-block) follows the same rule: its ``OPENSPEC_ABSENT`` is RED.

The absent tool is a made-up name that is on no folder of ``PATH``. For openspec, the case builds a ``PATH`` of one
folder holding ``git``, ``python3`` and the shell only, so the result does not depend on whether openspec is
installed on the machine.
"""

from __future__ import annotations

import re

import w2_45_support as support
from w2_45_support import ABSENT_TOOL, GREEN, HARD_BLOCK, RED, WARNING, YELLOW


def test_s3_absent_tool_of_a_hard_block_check_is_red_never_yellow(project):
    project.declare("absent-hard", f"{ABSENT_TOOL} --verify", severity=HARD_BLOCK)
    project.commit_all("plant a hard-block check whose tool is absent")
    run = project.check()
    entry = run.entry("absent-hard")
    assert entry["status"] != YELLOW, run.describe()
    assert entry["status"] != GREEN, run.describe()
    assert entry["status"] == RED, run.describe()
    assert run.returncode == support.EXIT_CHECK_FAILED, run.describe()


def test_s3_the_finding_is_tool_absent_and_names_the_first_word_of_the_command(project):
    project.declare("absent-named", f"{ABSENT_TOOL} --verify --flag", severity=HARD_BLOCK)
    project.commit_all("plant a hard-block check whose tool is absent")
    run = project.check()
    entry = run.entry("absent-named")
    found = support.findings_with(entry, "CHECK_TOOL_ABSENT")
    assert found, f"no CHECK_TOOL_ABSENT finding\n{run.describe()}"
    assert ABSENT_TOOL in str(found), f"the finding does not name the tool\n{run.describe()}"
    assert "CHECK_FAILED" not in support.finding_codes(entry), run.describe()


def test_s3_exit_code_127_is_an_absent_tool_and_red_for_a_hard_block_check(project):
    project.declare("exit-127-hard", 'sh -c "exit 127"', severity=HARD_BLOCK)
    project.commit_all("plant a hard-block check that exits 127")
    run = project.check()
    entry = run.entry("exit-127-hard")
    assert entry["status"] == RED, run.describe()
    found = support.findings_with(entry, "CHECK_TOOL_ABSENT")
    assert found, f"no CHECK_TOOL_ABSENT finding\n{run.describe()}"
    assert re.search(r"\bsh\b", str(found)), f"the finding does not name the command's first word\n{run.describe()}"


def test_s3_absent_tool_of_a_warning_check_is_yellow(project):
    project.declare("absent-warning", f"{ABSENT_TOOL} --verify", severity=WARNING)
    project.commit_all("plant a warning check whose tool is absent")
    run = project.check()
    entry = run.entry("absent-warning")
    assert entry["status"] == YELLOW, run.describe()
    assert "CHECK_TOOL_ABSENT" in support.finding_codes(entry), run.describe()


def test_s3_a_tool_that_is_present_is_not_reported_absent(project):
    """The edge: a check that runs and exits non-zero for its own reason is not an absent tool."""
    project.declare("present-failing", project.script("present-failing", "import sys\nsys.exit(1)\n"))
    project.commit_all("plant a hard-block check that fails")
    run = project.check()
    entry = run.entry("present-failing")
    assert entry["status"] == RED, run.describe()
    assert "CHECK_TOOL_ABSENT" not in support.finding_codes(entry), run.describe()


def test_s3_openspec_absent_from_the_path_is_red(project, tmp_path):
    only_git_and_python = support.make_path(tmp_path / "bin-without-openspec")
    assert not any((tmp_path / "bin-without-openspec" / name).exists() for name in ("openspec", "gitleaks"))
    run = project.check(path=only_git_and_python)
    entry = run.entry("openspec-validate")
    assert entry["severity"] == HARD_BLOCK, run.describe()
    assert entry["status"] != YELLOW, run.describe()
    assert entry["status"] == RED, run.describe()
    assert "OPENSPEC_ABSENT" in support.finding_codes(entry), run.describe()
    assert run.returncode == support.EXIT_CHECK_FAILED, run.describe()
