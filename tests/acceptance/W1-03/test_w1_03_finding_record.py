"""W1-03 — a containment finding is one JSON line in ``.gov-runtime/findings.jsonl``.

KPI success 1: "… recorded as a containment finding" [CAP-58.a].
KPI success 2: "… and the breach is recorded".
KPI failure 1: "Any out-of-scope change survives without a finding".

DEC-122: a containment finding is one JSON line in ``.gov-runtime/findings.jsonl``,
the same file as guard failures (DEC-110), with ``time``, ``session_id``,
``agent_type``, ``role``, ``ticket``, ``tool``, ``command``, ``paths``,
``action`` (``reverted`` or ``flagged``) and ``reason``.

Each test makes one whole Bash call in a project with a clean tree and reads the
lines the call added to the file.
"""

from __future__ import annotations

import json

import pytest

import w1_03_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
DESIGNER = support.TEST_DESIGNER
TICKET = support.TICKET_ID
SOURCE = support.SOURCE_FILE
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
FINDINGS = support.FINDINGS_REL


def _only_finding(result, what):
    findings = support.new_findings(result, what)
    assert len(findings) == 1, (
        f"{what}: one out-of-scope path is one finding, one line; the call added {len(findings)}: "
        f"{list(result.new_lines)}"
    )
    return findings[0]


def test_an_out_of_scope_change_is_recorded_as_one_finding(project, after_bash):
    command = "echo changed >> README.md"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md"])
    what = f"`{command}` by the engineer on {TICKET}"
    finding = _only_finding(result, what)   # checks the ten fields, session_id, tool and command
    assert support.finding_paths(result, finding) == ["README.md"], (
        f"{what}: `paths` is {finding['paths']!r}, not the one path changed out of scope"
    )
    assert finding["role"] == ENGINEER, f"{what}: `role` is {finding['role']!r}, not the session's role"
    assert finding["ticket"] == TICKET, f"{what}: `ticket` is {finding['ticket']!r}, not the session's ticket"
    assert not finding["agent_type"], (
        f"{what}: `agent_type` is {finding['agent_type']!r} for a call made outside any subagent"
    )


def test_the_findings_file_is_one_json_object_per_line(project, after_bash):
    for command in ("echo changed >> README.md", "echo new > docs/new.md"):
        after_bash(project, command, ENGINEER, TICKET)
    text = (project / FINDINGS).read_text(encoding="utf-8")
    assert text.endswith("\n"), f"{FINDINGS} does not end with a newline, so the next line would be joined to it"
    lines = text.splitlines()
    assert len(lines) == 2, f"two calls with one out-of-scope path each gave {len(lines)} lines in {FINDINGS}"
    for line in lines:
        assert isinstance(json.loads(line), dict), f"a line of {FINDINGS} is not a JSON object: {line[:300]!r}"


def test_the_finding_names_every_out_of_scope_path_and_no_other(project, after_bash):
    command = ("echo changed >> README.md && echo new > docs/new.md && echo new > 'docs/my notes.md' "
               f"&& rm docs/notes.md && echo changed >> {SOURCE} && echo new > src/gov/guard/new_module.py")
    result = after_bash(project, command, ENGINEER, TICKET,
                        changed=["README.md", "docs/new.md", "docs/my notes.md", "docs/notes.md", SOURCE])
    what = f"`{command}` by the engineer on {TICKET}"
    recorded = [path for finding in support.new_findings(result, what)
                for path in support.finding_paths(result, finding)]
    assert sorted(recorded) == ["README.md", "docs/my notes.md", "docs/new.md", "docs/notes.md"], (
        f"{what}: the recorded paths are {sorted(recorded)}; expected the four out-of-scope paths, each once, "
        "and neither of the two in-scope ones"
    )


def test_a_breach_of_the_acceptance_tests_is_recorded_as_reverted(project, after_bash):
    """KPI success 2: "restored from HEAD and the breach is recorded"."""
    command = f"echo changed >> {ACCEPTANCE_FILE}"
    result = after_bash(project, command, ENGINEER, TICKET, changed=[ACCEPTANCE_FILE])
    what = f"`{command}` by the engineer on {TICKET}"
    finding = _only_finding(result, what)
    assert support.finding_paths(result, finding) == [ACCEPTANCE_FILE], (
        f"{what}: `paths` is {finding['paths']!r}, not the acceptance test that was changed"
    )
    assert finding["action"] == support.REVERTED, (
        f"{what}: `action` is {finding['action']!r}; the file was to be restored from HEAD"
    )
    assert support.read(project, ACCEPTANCE_FILE) == support.head_text(project, ACCEPTANCE_FILE), (
        f"{what}: the finding says reverted, and {ACCEPTANCE_FILE} does not hold its HEAD content"
    )


def test_the_recorded_action_tells_what_happened_to_the_change(project, after_bash):
    """Outside ``tests/acceptance/**`` the check may undo the change or leave it. The record says which."""
    command = "echo changed >> README.md"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md"])
    what = f"`{command}` by the engineer on {TICKET}"
    finding = _only_finding(result, what)
    status = support.porcelain(project, "README.md")
    if finding["action"] == support.REVERTED:
        assert status == "" and support.read(project, "README.md") == support.head_text(project, "README.md"), (
            f"{what}: the finding says reverted, and README.md still differs from HEAD:\n{status}"
        )
    else:
        assert "README.md" in status and support.read(project, "README.md").endswith("changed\n"), (
            f"{what}: the finding says flagged, and the change to README.md is gone:\n{status}"
        )


def test_one_call_with_both_kinds_records_what_was_done_with_each(project, after_bash):
    command = f"echo changed >> README.md && echo changed >> {ACCEPTANCE_FILE} && echo changed >> {SOURCE}"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md", ACCEPTANCE_FILE, SOURCE])
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_recorded(result, ACCEPTANCE_FILE, what=what, action=support.REVERTED)
    support.assert_recorded(result, "README.md", what=what)
    support.assert_not_recorded(result, SOURCE, what=what)


# name: (command, GOV_ROLE, GOV_TICKET)
NOTHING_FOUND = {
    "clean-tree": ("ls -la", ENGINEER, TICKET),
    "in-scope-change": (f"echo changed >> {SOURCE}", ENGINEER, TICKET),
    "in-scope-new-file": ("echo new > src/gov/guard/new_module.py", ENGINEER, TICKET),
    "test-designer-s-own-change": (f"echo changed >> {ACCEPTANCE_FILE}", DESIGNER, TICKET),
    "scratch-write": (
        f"mkdir -p {support.SCRATCH_REL} && echo note > {support.SCRATCH_REL}/note.txt", ENGINEER, TICKET),
}


@pytest.mark.parametrize("case", sorted(NOTHING_FOUND), ids=sorted(NOTHING_FOUND))
def test_a_run_that_finds_nothing_records_nothing(project, after_bash, case):
    command, role, ticket = NOTHING_FOUND[case]
    result = after_bash(project, command, role, ticket)
    what = f"`{command}` by {role} on {ticket}"
    support.assert_silent(result, what)
    assert support.finding_lines(project) == [], (
        f"{what}: nothing was out of scope, and {FINDINGS} holds: {support.finding_lines(project)}"
    )


def test_earlier_lines_of_the_findings_file_stay(project, after_bash):
    """The file is shared with the guard's failure findings (DEC-110). A new finding is appended."""
    earlier = (
        '{"source":"guard","kind":"invalid_json","reason":"stdin is not valid JSON","session_id":"s-1",'
        '"tool_name":""}\n'
        '{"time":"2026-10-01T10:00:00Z","session_id":"s-0","agent_type":null,"role":"engineer",'
        '"ticket":"DAEO-zz90","tool":"Bash","command":"true","paths":["docs/old.md"],"action":"flagged",'
        '"reason":"earlier finding"}\n'
    )
    path = project / FINDINGS
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(earlier, encoding="utf-8")
    command = "echo changed >> README.md"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md"])
    what = f"`{command}` by the engineer on {TICKET}, with two earlier lines in {FINDINGS}"
    _only_finding(result, what)
    text = path.read_text(encoding="utf-8")
    assert text.startswith(earlier), f"{what}: the earlier lines were changed or removed:\n{text[:600]}"
    assert len(text.splitlines()) == 3, f"{what}: the file holds {len(text.splitlines())} lines, not 3"


# name: (GOV_ROLE, agent_type)
SUBAGENTS = {
    "engineer-in-orchestrator-session": (ORCHESTRATOR, ENGINEER),
    "general-purpose-in-engineer-session": (ENGINEER, "general-purpose"),
}


@pytest.mark.parametrize("case", sorted(SUBAGENTS), ids=sorted(SUBAGENTS))
def test_a_finding_inside_a_subagent_names_the_subagent_type(project, after_bash, case):
    session_role, agent_type = SUBAGENTS[case]
    command = "echo changed >> README.md"
    result = after_bash(project, command, session_role, TICKET, changed=["README.md"], subagent=agent_type)
    what = f"`{command}` by subagent {agent_type} in a session with GOV_ROLE={session_role!r}"
    finding = _only_finding(result, what)
    assert finding["agent_type"] == agent_type, (
        f"{what}: `agent_type` is {finding['agent_type']!r}, not the subagent's type"
    )
    assert finding["ticket"] == TICKET, f"{what}: `ticket` is {finding['ticket']!r}, not the session's ticket"


def test_a_session_without_role_and_ticket_is_recorded_without_them(project, after_bash):
    command = "echo changed >> README.md"
    result = after_bash(project, command, None, None, changed=["README.md"])
    what = f"`{command}` in a session with no GOV_ROLE and no GOV_TICKET"
    finding = _only_finding(result, what)
    assert not finding["role"], f"{what}: `role` is {finding['role']!r}; the session declared none"
    assert not finding["ticket"], f"{what}: `ticket` is {finding['ticket']!r}; the session declared none"


def test_a_failed_call_is_recorded_too(project, after_bash):
    """The harness sends PostToolUseFailure when the call failed. Its changes are recorded all the same."""
    command = f"echo changed >> README.md; echo changed >> {ACCEPTANCE_FILE}; exit 3"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md", ACCEPTANCE_FILE], failed=True)
    what = f"`{command}` (failed call) by the engineer on {TICKET}"
    support.assert_caught(result, "README.md", what=what)
    support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.REVERTED)


def test_the_findings_file_does_not_show_in_git_status(project, after_bash):
    command = "echo changed >> README.md"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md"])
    support.assert_recorded(result, "README.md", what=f"`{command}` by the engineer on {TICKET}")
    lines = set(support.porcelain_all(project).splitlines())
    assert lines <= {" M README.md"}, (
        "recording the finding left changes of its own in git status: " + ", ".join(sorted(lines - {" M README.md"}))
    )
