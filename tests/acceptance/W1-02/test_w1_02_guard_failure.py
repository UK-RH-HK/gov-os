"""W1-02 — a failing guard denies, and leaves a finding.

KPI failure 2: "Guard crash or timeout lets the call through without a recorded
finding".

Owner answer to KD-4: a failing guard denies, and appends one line to
``.gov-runtime/findings.jsonl``. Every internal error is caught and the guard
exits with code 2; an exit code 1 or a timeout would not block in the harness.
The finding is one JSON object with ``source`` = ``"guard"``, ``kind``,
``session_id``, ``tool_name`` and ``reason``.

The guard is made to fail through its public input only:

- a stdin it cannot use: not JSON, empty, not an object, no ``tool_name``, no
  ``tool_input``;
- a stdin that never ends: the guard answers within 5 s on its own;
- a ticket file it cannot use. Here the tests ask only for a denial, because a
  guard may treat such a file as "no ticket paths" without failing.

The session is the engineer on DAEO-zz90, so a guard that lets a failed call
through would be letting a write through.
"""

from __future__ import annotations

import json
import os

import pytest

import w1_02_support as support

ENGINEER = support.ENGINEER
TICKET = support.TICKET_ID

OWN_DEADLINE_S = 5.0


def _well_formed(project, sandbox, **changes):
    data = support.payload(
        project, "Write", support.edit_tool_input("Write", project / "src/gov/guard/decide.py"), sandbox
    )
    for key, value in changes.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = value
    return data


def _bad_stdin(kind, project, sandbox):
    if kind == "not-json":
        return "this is not JSON {"
    if kind == "empty":
        return ""
    if kind == "truncated-json":
        return json.dumps(_well_formed(project, sandbox))[:-25]
    if kind == "json-array":
        return "[]"
    if kind == "json-string":
        return '"Write"'
    if kind == "no-tool-name":
        return json.dumps(_well_formed(project, sandbox, tool_name=None))
    if kind == "no-tool-input":
        return json.dumps(_well_formed(project, sandbox, tool_input=None))
    if kind == "tool-input-not-an-object":
        return json.dumps(_well_formed(project, sandbox, tool_input="src/gov/guard/decide.py"))
    raise ValueError(kind)


BAD_STDIN = [
    "not-json", "empty", "truncated-json", "json-array", "json-string",
    "no-tool-name", "no-tool-input", "tool-input-not-an-object",
]
# Inputs from which the guard can still read the session and the tool.
READABLE = {"no-tool-input": "Write", "tool-input-not-an-object": "Write"}


def _new_findings(project, before):
    after = support.findings(project)
    assert after[:len(before)] == before, (
        f"{support.FINDINGS_REL} lost or changed earlier lines; findings are appended"
    )
    return after[len(before):]


def _assert_one_guard_finding(project, before, what):
    new = _new_findings(project, before)
    assert len(new) == 1, (
        f"{what}: expected one new line in {support.FINDINGS_REL}, found {len(new)}: {new!r}"
    )
    try:
        finding = json.loads(new[0])
    except ValueError:
        pytest.fail(f"{what}: the new line in {support.FINDINGS_REL} is not JSON: {new[0]!r}", pytrace=False)
    assert isinstance(finding, dict), f"{what}: the finding is not a JSON object: {new[0]!r}"
    assert finding.get("source") == "guard", f"{what}: the finding does not name its source as guard: {finding!r}"
    for key in ("kind", "reason"):
        value = finding.get(key)
        assert isinstance(value, str) and value.strip(), f"{what}: the finding has no {key}: {finding!r}"
    for key in ("session_id", "tool_name"):
        assert key in finding, f"{what}: the finding has no {key} field: {finding!r}"
    return finding


@pytest.mark.parametrize("kind", BAD_STDIN)
def test_unusable_input_is_denied_with_exit_code_2(project, sandbox, kind):
    result = support.run_hook_raw(project, _bad_stdin(kind, project, sandbox), sandbox, ENGINEER, TICKET)
    assert result.returncode == 2, (
        f"stdin {kind}: the guard must exit with code 2, the only exit that blocks the call: {result.describe()}"
    )


@pytest.mark.parametrize("kind", BAD_STDIN)
def test_unusable_input_leaves_one_finding(project, sandbox, kind):
    before = support.findings(project)
    support.run_hook_raw(project, _bad_stdin(kind, project, sandbox), sandbox, ENGINEER, TICKET)
    finding = _assert_one_guard_finding(project, before, f"stdin {kind}")
    if kind in READABLE:
        assert finding["session_id"] == support.SESSION_ID, f"stdin {kind}: wrong session_id in {finding!r}"
        assert finding["tool_name"] == READABLE[kind], f"stdin {kind}: wrong tool_name in {finding!r}"


def test_findings_are_appended_one_line_per_failure(project, sandbox):
    path = project / support.FINDINGS_REL
    path.parent.mkdir(parents=True)
    earlier = json.dumps({"source": "containment", "kind": "earlier", "reason": "written before the test"})
    path.write_text(earlier + "\n", encoding="utf-8")

    for count in (1, 2, 3):
        support.run_hook_raw(project, "this is not JSON {", sandbox, ENGINEER, TICKET)
        lines = support.findings(project)
        assert lines[0] == earlier, f"the earlier finding was lost or changed: {lines!r}"
        assert len(lines) == 1 + count, (
            f"after {count} failing calls {support.FINDINGS_REL} holds {len(lines) - 1} new lines"
        )
    assert path.read_text(encoding="utf-8").endswith("\n"), "the last finding does not end with a newline"


def test_a_failure_does_not_show_in_git_status(project, sandbox):
    support.run_hook_raw(project, "this is not JSON {", sandbox, ENGINEER, TICKET)
    assert support.porcelain(project) == "", (
        "git status --porcelain changed after a guard failure:\n" + support.porcelain(project)
    )


def test_input_that_never_ends_is_denied_by_the_guard_s_own_deadline(project, sandbox):
    """The harness lets a call through when a hook times out, so the guard must not wait for ever."""
    before = support.findings(project)
    result = support.run_hook_with_open_stdin(project, sandbox, OWN_DEADLINE_S, ENGINEER, TICKET)
    assert result.decision != "timeout", (
        f"the guard was still waiting for input after {OWN_DEADLINE_S:.0f} s; a hook timeout does not block the call"
    )
    assert result.returncode == 2, f"the guard gave up waiting but did not exit with code 2: {result.describe()}"
    _assert_one_guard_finding(project, before, "stdin that never ends")


def _break_ticket(project, how):
    path = project / ".tickets" / f"{TICKET}.md"
    if how == "frontmatter-never-closed":
        path.write_text("---\nid: " + TICKET + "\nrole: engineer\nallowed_paths:\n- src/gov/guard/**\n", "utf-8")
    elif how == "frontmatter-is-not-yaml":
        path.write_text("---\nallowed_paths: [src/gov/guard/**\n  role: {engineer\n\t- : :\n---\n# broken\n", "utf-8")
    elif how == "no-frontmatter":
        path.write_text("# A ticket file without frontmatter\n\nallowed_paths: src/gov/guard/**\n", "utf-8")
    elif how == "empty-file":
        path.write_text("", "utf-8")
    elif how == "not-utf-8":
        path.write_bytes(b"---\nid: " + TICKET.encode() + b"\nrole: engineer\nallowed_paths:\n- \xff\xfe\x00src\n---\n")
    elif how == "is-a-directory":
        path.unlink()
        path.mkdir()
    elif how == "unreadable":
        path.chmod(0)
    else:
        raise ValueError(how)
    return path


@pytest.mark.parametrize("how", [
    "frontmatter-never-closed", "frontmatter-is-not-yaml", "no-frontmatter", "empty-file",
    "not-utf-8", "is-a-directory", "unreadable",
])
def test_a_ticket_file_the_guard_cannot_use_never_lets_a_write_through(project, write, bash, how):
    if how == "unreadable" and os.geteuid() == 0:
        pytest.skip("root can read a file with mode 000")
    path = _break_ticket(project, how)
    try:
        attempts = [
            ("Write inside the former ticket paths", write(project, "src/gov/guard/decide.py", ENGINEER, TICKET)),
            ("Edit inside the former ticket paths",
             write(project, "src/gov/guard/decide.py", ENGINEER, TICKET, "Edit")),
            ("Write outside the ticket paths", write(project, "README.md", ENGINEER, TICKET)),
            ("Bash redirect", bash(project, "echo changed > src/gov/guard/decide.py", ENGINEER, TICKET)),
        ]
    finally:
        if how == "unreadable":
            path.chmod(0o644)
    for what, result in attempts:
        support.assert_denied(result, f"with a ticket file that is {how}, {what}")
