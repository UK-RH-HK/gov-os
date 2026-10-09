"""The checks that read the command list hold the four recorded commands as they hold the twelve (DEC-542; DEC-569).

DEC-542: "``ci``, ``launch``, ``telemetry`` and ``lock`` are recorded in the command list".

Two checks read the command list today:

- ``core-commands`` (``python3 -m gov.check.commands``): a command of the list whose module file the project
  does not hold is a finding that names the command.
- The skill validator (``python3 -m gov.check.skill_validator``): a skill whose code names a ``gov`` command
  that is not in the list is a finding.

What the cases hold (README, section "The four recorded commands in the checks"):

- Each of the four is held by ``core-commands`` as the twelve are: where the project holds no module for it,
  a finding names it. For ``ci``, ``launch`` and ``telemetry`` the module is the command's module file, as for
  the twelve. ``lock`` is recorded as the module command ``python3 -m gov.lock`` (DEC-499): its module is the
  file that makes that command run.
- With every module present the check has no finding: recording ``lock`` does not make the check report it
  for having the form it has.
- A skill may name ``gov ci``, ``gov launch`` and ``gov telemetry``. ``gov lock`` stays an unknown command in
  a skill, because ``gov`` has no such command; ``python3 -m gov.lock`` is not flagged.

The module of a command is removed in the temporary project's own copy only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_26_support as support  # noqa: E402
import test_w1_26_skill_validator as skills  # noqa: E402

cli_support = support.cli_support

GOV_COMMANDS = cli_support.RECORDED_GOV_COMMANDS          # ci, launch, telemetry
MODULE_COMMANDS = cli_support.RECORDED_MODULE_COMMANDS    # lock
RECORDED = GOV_COMMANDS + MODULE_COMMANDS

FAMILY = "command-contract consistency"
CHECK_ID = "w1-26-recorded-commands"
UNKNOWN_COMMAND = "SKILL_UNKNOWN_COMMAND"


def _module_files(project, name):
    """The files in the project's own copy that make the recorded command run."""
    if name in MODULE_COMMANDS:
        path = project.root / "src" / "gov" / name / "__main__.py"
        return [path] if path.is_file() else []
    return project.reserved_command_module_files(name)


def _findings(project, sandbox, interface):
    project.add_check_declaration(CHECK_ID, FAMILY, severity="hard-block", command="python3 -m gov.check.commands")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    findings = []
    for entry in support.checks_of(result):
        if isinstance(entry, dict) and CHECK_ID in (entry.get("id"), entry.get("check_id")):
            findings.extend(entry.get("findings") or [])
    return findings, support.family_status(result, FAMILY), run


@pytest.mark.parametrize("name", RECORDED)
def test_a_recorded_command_without_its_module_is_a_finding_that_names_it(name, project, sandbox, interface):
    files = _module_files(project, name)
    assert files, f"the defect cannot be planted: the project holds no module of {name!r}"
    for path in files:
        assert support.REPO_ROOT not in path.resolve().parents, f"{path} is not in a temporary project"
        path.unlink()

    findings, status, run = _findings(project, sandbox, interface)

    named = [finding for finding in findings if isinstance(finding, dict) and finding.get("command") == name]
    assert named, f"no finding of the check on the command list names {name!r}: {findings}\n{run.describe()}"
    assert status == support.RED, f"{FAMILY} is {status!r} with the module of {name!r} gone\n{run.describe()}"
    others = [finding for finding in findings if finding not in named]
    assert not others, f"a finding names a command whose module is present: {others}"


def test_with_every_module_present_the_check_has_no_finding(project, sandbox, interface):
    """Green today, and it stays: the twelve and the four each have their module in this project."""
    for name in support.RESERVED_COMMANDS:
        assert project.reserved_command_module_files(name), f"the project holds no module of {name!r}"
    for name in RECORDED:
        assert _module_files(project, name), f"the project holds no module of {name!r}"

    findings, status, run = _findings(project, sandbox, interface)

    assert not findings, f"the check reports a finding with nothing planted: {findings}\n{run.describe()}"
    assert status == support.GREEN, f"{FAMILY} is {status!r} with nothing planted\n{run.describe()}"


# --------------------------------------------------------------------------
# The skill validator
# --------------------------------------------------------------------------

def _unknown_commands(tmp_path, body):
    path = skills.make_skill(tmp_path, name="names-a-command", body=body)
    done = skills.run_skill_validator(str(path))
    output = skills.parse_output(done)
    assert "findings" in output, f"the skill validator did not measure: {done.stdout}\n{done.stderr}"
    return [finding for finding in output["findings"] if finding.get("code") == UNKNOWN_COMMAND], done


@pytest.mark.parametrize("name", GOV_COMMANDS)
def test_a_skill_may_name_a_recorded_gov_command(name, tmp_path):
    unknown, done = _unknown_commands(tmp_path, f"Run `gov {name}` where the procedure asks for it.\n")
    assert not unknown, f"a skill that names `gov {name}` is flagged: {unknown}"
    assert done.returncode == 0, f"the skill validator does not pass the skill: {done.stdout}"


def test_gov_lock_in_a_skill_stays_an_unknown_command(tmp_path):
    """``lock`` is recorded as a module command: ``gov`` has no such command, and a skill that tells a reader
    to run it is flagged as before."""
    unknown, _ = _unknown_commands(tmp_path, "Run `gov lock` after the update.\n")
    assert unknown and "lock" in json.dumps(unknown), f"a skill that names `gov lock` is not flagged: {unknown}"


def test_the_module_command_of_lock_in_a_skill_is_not_flagged(tmp_path):
    unknown, done = _unknown_commands(tmp_path, "The template's task runs `python3 -m gov.lock`.\n")
    assert not unknown, f"a skill that names the module command is flagged: {unknown}"
    assert done.returncode == 0, done.stdout
