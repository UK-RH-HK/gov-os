"""W1-50 — what a commit's author puts in a trailer value or a file name never changes what the check sees.

Added after implementation, from the review after the suite went green
(DEC-136, DEC-137). The behaviour, as it was passed to the test designer:

    The check judges each commit of a forward move by that commit's own id,
    parents, `Role` and `Task` trailer values and changed paths. What a
    commit's author puts in a trailer value or in a file name can never make
    the check see another commit, another role, another ticket or other paths
    than the commit really has. A commit whose trailer values or paths the
    check cannot read unambiguously is a finding, never silence.

It is held by the KPIs the suite already tests:

KPI success 1 [CAP-58.h]: a forward HEAD move is judged commit by commit, "each
commit's paths against the allowed paths of its own Role and Task trailers".

KPI failure 2: "A commit that changes a path outside the allowed paths of its
own Role and Task trailers raises no finding, whoever the caller is".

KPI success 5 [CAP-58.h]: "A commit carrying a Role: owner trailer that is made
during any agent session's call is a finding (DEC-360)".

DEC-268: trailers that name an unknown role or an unknown ticket allow
nothing, "and every path it changes is a finding".

**The commits.** Git accepts control characters in a trailer value and in a
file name (not 0x00, and no newline inside a trailer's line). A commit here
carries, after an ordinary beginning, two such characters and between them
text shaped like the record of a commit that does not exist: a
40-character hexadecimal id, a role and a ticket id. One character stands
where a reader that separates fields by it would end a field, the other where
such a reader would end the commit. Read that way, the real commit ends early
and the acceptance test it changes belongs to a commit of a role that may
write it.

What the commit really is does not depend on those bytes:

- with the bytes in the ``Role`` or the ``Task`` value, the commit names no
  known role or no known ticket (DEC-268), and every path it changes is a
  finding;
- with the bytes in a file name, the commit is an engineer's commit that
  changes an acceptance test, and that path is a finding.

Four pairs of characters are used, so that no test rests on one way of
separating: 0x02 with 0x01, 0x01 with 0x03, 0x03 with 0x02, and 0x1f with 0x1e
(the ASCII unit and record separators). The behaviour holds for every byte git
lets a commit's author put in a trailer value or a file name; the suite tests
these.

Every call is an orchestrator session's own call: only there is a commit
judged by its own trailers (DEC-319).

The last two tests hold the other side: a file name with a space, a
non-ASCII letter or a tab, in a commit with ordinary trailers, is a path like
any other.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
DESIGNER = support.DESIGNER
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER

NO_SUCH_COMMIT = "0123456789abcdef0123456789abcdef01234567"   # shaped like a commit id; names no commit

# name: (the character between two values, the character between two commits), as a separating reader would take them
PAIRS = {
    "0x02-0x01": ("\x02", "\x01"),
    "0x01-0x03": ("\x01", "\x03"),
    "0x03-0x02": ("\x03", "\x02"),
    "0x1f-0x1e": ("\x1f", "\x1e"),
}

GUARD_DIRECTORY = "src/gov/guard"   # inside DAEO-zz90's allowed paths


def _role_value(start, between, end, other_role):
    """A ``Role`` value: ``start``, then a ticket id, then the beginning of another commit's record."""
    return start + between + TICKET + between + end + NO_SUCH_COMMIT + between + between + other_role


def _task_value(between, end, other_role):
    """A ``Task`` value: the ticket's id, then another commit's record with a role and a ticket id."""
    return TICKET + between + end + NO_SUCH_COMMIT + between + between + other_role + between + TICKET


def _file_name(between, end, other_role):
    """A file name: an ordinary beginning, then another commit's record with a role and a ticket id."""
    return "x" + end + NO_SUCH_COMMIT + between + between + other_role + between + TICKET + between


def _commit(where, pair):
    """-> (shell command, the bytes, the paths the commit changes). The commit changes an existing acceptance test."""
    between, end = PAIRS[pair]
    role, task, paths = ENGINEER, TICKET, [support.ACCEPTANCE_FILE]
    if where == "role-value":
        role = text = _role_value(ENGINEER, between, end, DESIGNER)
    elif where == "task-value":
        task = text = _task_value(between, end, DESIGNER)
    else:
        text = f"{GUARD_DIRECTORY}/{_file_name(between, end, DESIGNER)}"
        paths = [text, support.ACCEPTANCE_FILE]
    command = support.commit_changes(paths, (f"Task: {task}", f"Role: {role}"), subject="work with chosen bytes")
    return command, text, paths


def _assert_the_commit_holds(project, commit_id, where, text, paths):
    """Guard against an empty test: git itself reads the bytes where the test put them, and the real paths."""
    assert sorted(support.changed_paths(project, commit_id)) == sorted(paths), (
        f"the fixture is wrong: the commit changes {support.changed_paths(project, commit_id)!r}, not {paths!r}"
    )
    roles = support.trailer_values(project, commit_id, "Role")
    tasks = support.trailer_values(project, commit_id, "Task")
    assert len(roles) == 1 and len(tasks) == 1, f"the fixture is wrong: git reads Role {roles!r} and Task {tasks!r}"
    if where == "role-value":
        assert roles == [text], f"the fixture is wrong: git reads the Role value {roles!r}, not {text!r}"
    if where == "task-value":
        assert tasks == [text], f"the fixture is wrong: git reads the Task value {tasks!r}, not {text!r}"


# name: (where the bytes are, the pair of characters, how the commit reaches HEAD in the orchestrator's call)
BROUGHT = {
    "role-value-0x02-0x01-integration-merge": ("role-value", "0x02-0x01", "merge"),
    "role-value-0x01-0x03-integration-merge": ("role-value", "0x01-0x03", "merge"),
    "role-value-0x03-0x02-integration-merge": ("role-value", "0x03-0x02", "merge"),
    "role-value-0x1f-0x1e-integration-merge": ("role-value", "0x1f-0x1e", "merge"),
    "role-value-0x02-0x01-fast-forward": ("role-value", "0x02-0x01", "fast-forward"),
    "task-value-0x02-0x01-integration-merge": ("task-value", "0x02-0x01", "merge"),
    "task-value-0x01-0x03-integration-merge": ("task-value", "0x01-0x03", "merge"),
    "file-name-0x02-0x01-integration-merge": ("file-name", "0x02-0x01", "merge"),
    "file-name-0x01-0x03-integration-merge": ("file-name", "0x01-0x03", "merge"),
    "file-name-0x03-0x02-integration-merge": ("file-name", "0x03-0x02", "merge"),
    "file-name-0x1f-0x1e-integration-merge": ("file-name", "0x1f-0x1e", "merge"),
    "file-name-0x02-0x01-fast-forward": ("file-name", "0x02-0x01", "fast-forward"),
}


@pytest.mark.parametrize("case", sorted(BROUGHT), ids=sorted(BROUGHT))
def test_a_commit_of_an_acceptance_test_is_flagged_whatever_bytes_its_trailers_or_file_names_hold(project, sandbox,
                                                                                                 call, case):
    """KPI failure 2. The ticket branch holds a test designer's commit inside its paths and, after it, a commit
    that changes an existing acceptance test and is not the test designer's. The orchestrator merges the branch,
    or fast-forwards to it. The finding names the acceptance test."""
    where, pair, move = BROUGHT[case]
    command_of_the_commit, text, paths = _commit(where, pair)
    support.ticket_branch_of(project, sandbox, support.commit(support.NEW_TEST, AS_DESIGNER), command_of_the_commit,
                             main_moves_on=(move == "merge"))
    command = support.merge() if move == "merge" else f"git merge -q --ff-only {support.TICKET_BRANCH}"
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project) == (move == "merge"), f"the fixture command `{command}` is no {move}"
    commit_id = support.commit_of(project, support.ACCEPTANCE_FILE)
    _assert_the_commit_holds(project, commit_id, where, text, paths)
    what = (f"`{command}` by the orchestrator on {TICKET}, bringing commit {commit_id[:12]} of "
            f"{support.ACCEPTANCE_FILE} with the bytes {text!r} in its {where}")
    check_support.assert_caught(result, support.ACCEPTANCE_FILE, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# name: the pair of characters
OWNER_PAIRS = ("0x02-0x01", "0x03-0x02")


@pytest.mark.parametrize("pair", OWNER_PAIRS, ids=OWNER_PAIRS)
def test_a_role_value_that_begins_with_owner_is_a_finding_whatever_bytes_follow(project, call, pair):
    """KPI success 5. The commit is made in the orchestrator's own call and changes README.md, which the
    orchestrator may write itself. The record-shaped text names the orchestrator's role, which may write it too.

    The commit's ``Role`` value is ``owner`` followed by other bytes. Whether the check reads that as the owner's
    trailer or as a role nobody has (DEC-268), the commit is a finding.
    """
    between, end = PAIRS[pair]
    role = _role_value(support.OWNER, between, end, ORCHESTRATOR)
    command = support.commit_changes([support.README], (f"Task: {TICKET}", f"Role: {role}"))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    commit_id = support.commit_of(project, support.README)
    _assert_the_commit_holds(project, commit_id, "role-value", role, [support.README])
    what = (f"a commit of {support.README} with the Role value {role!r}, made in the orchestrator's own call "
            f"on {TICKET}")
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# The other side: an unusual file name in a commit with ordinary trailers is a path like any other
# --------------------------------------------------------------------------

# name: the file's name
UNUSUAL_NAMES = {
    "a-space": "two words.py",
    "a-non-ascii-letter": "grün.py",
    "a-tab": "tab\there.py",
}


@pytest.mark.parametrize("case", sorted(UNUSUAL_NAMES), ids=sorted(UNUSUAL_NAMES))
def test_a_file_with_an_unusual_name_inside_the_commit_s_own_paths_is_silent(project, call, case):
    """An engineer's commit that adds the file inside its ticket's paths, in the orchestrator's own call."""
    path = f"{GUARD_DIRECTORY}/{UNUSUAL_NAMES[case]}"
    command = support.commit_changes([path], (f"Task: {TICKET}", f"Role: {ENGINEER}"))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.changed_paths(project, "HEAD") == [path], "the fixture is wrong: the commit does not add the file"
    what = f"a commit that adds {path!r} with trailers {AS_ENGINEER}, in the orchestrator's own call on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(UNUSUAL_NAMES), ids=sorted(UNUSUAL_NAMES))
def test_a_file_with_an_unusual_name_outside_the_commit_s_own_paths_is_flagged_by_its_name(project, call, case):
    """The same commit with the file under ``docs/``: outside the engineer ticket's paths, and a path the
    orchestrator may write itself. The finding's ``paths`` hold the file's name as it is.

    The report to the agent names the file too. For the tab, the report may
    write it as it is or as ``\\t``.
    """
    name = UNUSUAL_NAMES[case]
    path = f"docs/{name}"
    command = support.commit_changes([path], (f"Task: {TICKET}", f"Role: {ENGINEER}"))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.changed_paths(project, "HEAD") == [path], "the fixture is wrong: the commit does not add the file"
    what = f"a commit that adds {path!r} with trailers {AS_ENGINEER}, in the orchestrator's own call on {TICKET}"
    findings = support.findings_naming(result, path, what)
    assert all(finding["action"] == check_support.FLAGGED for finding in findings), (
        f"{what}: the finding has action {[finding['action'] for finding in findings]}"
    )
    assert result.outcome == "report", f"{what}: nothing was reported to the agent: {result.describe()}"
    assert path in result.report or path.replace("\t", "\\t") in result.report, (
        f"{what}: the report to the agent does not name {path!r}: {result.report[:600]!r}"
    )
    check_support.assert_left_as_the_call_left_it(project, left, what)
