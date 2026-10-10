"""Round 15, piece 2 (DEC-612, DEC-620): a check command that succeeds is not a finding.

Measured before the round: the fresh-agent-reconstruction check's declared command is
``gov checkpoint --resume --json``. With ``gov`` installed it runs, exits 0 and prints the success form of every
``gov`` command (API-0002: a JSON object with ``"ok": true`` and a ``result``). The runner reads any JSON object
on standard output as one finding, so the check is red on its own success.

DEC-620: "only the success form of a ``gov`` command with exit 0 stops being a finding. Every other output is
judged as today." What "today" is was measured with this suite's stand-in commands before the cases were written
(README, round 15, piece 2) and is pinned here for the shapes no other suite holds:

- the success form with another exit code: RED;
- the refusal form (``"ok": false``), exit code 0 or not: RED, the object its one finding;
- another JSON object with exit code 0 (``unmeasured``, a finding written as an object, ``"ok": true`` without a
  ``result``): RED, the object its one finding.

A ``findings`` list, a list of findings and the forms ``not_applicable`` and ``unmeasured`` (exit code 1) have
their cases in W1-26's and W1-15's suites and are not repeated.
"""

from __future__ import annotations

import json

import pytest

import w1_30_r15_support as r15

SUCCESS = {"ok": True, "command": "checkpoint", "result": {"briefs": []}, "session": ""}
REFUSAL = {"ok": False, "command": "checkpoint", "result": {}, "session": "",
           "error": {"code": "CHECKPOINT_INVALID", "message": "no resume brief"}}
FRESH_AGENT = "fresh-agent-reconstruction"
TICKET = "PROJ-aaaa"


def _prints(tmp_path, name, document, exit_code):
    return r15.script(tmp_path / "commands", name, f"printf '%s\\n' '{json.dumps(document)}'\nexit {exit_code}")


def _entry(scratch, sandbox, tmp_path, document, exit_code):
    project = scratch()
    project.declare("answers", _prints(tmp_path, "answers.sh", document, exit_code))
    _status, entry, run = r15.status_of(project, sandbox, "answers")
    return entry, run


def test_the_success_form_of_a_gov_command_with_exit_code_0_is_green(scratch, sandbox, tmp_path):
    """Red before the round: RED, the success envelope itself read as the one finding."""
    entry, run = _entry(scratch, sandbox, tmp_path, SUCCESS, 0)
    assert entry["status"] == r15.GREEN, \
        f"a check whose command succeeded is {entry['status']}: {entry['findings']}\n{run.describe()}"
    assert entry["findings"] == [], f"the success form was read as a finding: {entry['findings']}\n{run.describe()}"


def test_the_success_form_with_another_exit_code_is_red(scratch, sandbox, tmp_path):
    """Pins what holds today (passes before the round): the exit code decides, not the words."""
    entry, run = _entry(scratch, sandbox, tmp_path, SUCCESS, 1)
    assert entry["status"] == r15.RED and entry["findings"], \
        f"a command that failed is {entry['status']} because it printed a success form\n{run.describe()}"


@pytest.mark.parametrize("exit_code", (0, 1))
def test_the_refusal_form_is_judged_as_today(exit_code, scratch, sandbox, tmp_path):
    """Pins what holds today (passes before the round): RED with the refusal as its one finding, whatever the
    exit code. Nothing red today turns green."""
    entry, run = _entry(scratch, sandbox, tmp_path, REFUSAL, exit_code)
    assert entry["status"] == r15.RED and entry["findings"] == [REFUSAL], \
        f"a refusal form with exit code {exit_code} is not judged as before the round\n{run.describe()}"


NOT_THE_SUCCESS_FORM = {
    "unmeasured, exit code 0": {"unmeasured": True, "reason": "nothing was measured"},
    "a finding written as an object": {"code": "PLANTED", "message": "a finding"},
    "ok true without a result": {"ok": True},
}


@pytest.mark.parametrize("what", sorted(NOT_THE_SUCCESS_FORM))
def test_another_object_with_exit_code_0_is_still_a_finding(what, scratch, sandbox, tmp_path):
    """Pins what holds today (passes before the round): only the success form of a ``gov`` command (``"ok": true``
    and a ``result``) stops being a finding."""
    document = NOT_THE_SUCCESS_FORM[what]
    entry, run = _entry(scratch, sandbox, tmp_path, document, 0)
    assert entry["status"] == r15.RED and entry["findings"] == [document], \
        f"{what}: not judged as before the round ({entry['status']}, {entry['findings']})\n{run.describe()}"


def test_the_fresh_agent_reconstruction_check_is_green_where_the_resume_brief_can_be_built(scratch, sandbox):
    """The check as the kernel template declares it, in a project with a ticket and its checkpoint, ``gov`` on
    PATH being this worktree's command line. Red before the round: RED, its finding the success envelope of
    ``gov checkpoint --resume --json``."""
    project = scratch()
    project.write(r15.PATH_MAP_REL, "namespaces: {}\n")
    project.base_source()
    project.write(f".tickets/{TICKET}.md", r15.ticket_text(TICKET, "W9-01"))
    project.declare_as_the_kernel_does(FRESH_AGENT)
    env = r15.env_with_gov(sandbox)
    made = project.gov(sandbox, "checkpoint", "--ticket", TICKET, "--trigger", "stop", "--next", "the next step",
                       "--json", env=env)
    assert made.returncode == 0, f"the fixture's checkpoint was not written\n{made.describe()}"
    resumed = project.gov(sandbox, "checkpoint", "--resume", "--json", env=env)
    briefs = resumed.envelope().get("result", {}).get("briefs")
    assert resumed.returncode == 0 and briefs and briefs[0].get("ticket") == TICKET, \
        f"the fixture's resume brief cannot be built, so the case measures nothing\n{resumed.describe()}"
    status, entry, run = r15.status_of(project, sandbox, FRESH_AGENT, env=env)
    assert status == r15.GREEN and entry["findings"] == [], \
        f"the resume brief can be built and the check is {status}: {entry['findings']}\n{run.describe()}"
